from __future__ import annotations

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing.exceptions import Unresolvable

from .io import ManualError, digest, read_bytes, read_json, source_path

OWNER_DOMAINS = {
    "C": "login",
    "D": "ui_chat",
    "E": "network",
    "F": "battle",
    "G": "gameplay",
}


def _local_references_only(schema):
    pending = [schema]
    while pending:
        node = pending.pop()
        if isinstance(node, list):
            pending.extend(node)
        elif isinstance(node, dict):
            for name, value in node.items():
                if name in {"$id", "$dynamicRef", "$recursiveRef"}:
                    raise ManualError("离线契约不允许动态或远程schema解析")
                if name == "$ref" and (
                    not isinstance(value, str) or not value.startswith("#/$defs/")
                ):
                    raise ManualError("离线契约只允许本地$defs引用")
                pending.append(value)


class Contract:
    def __init__(self, root):
        schema = read_json(root / "schema/contract.schema.json")
        _local_references_only(schema)
        try:
            self.definitions = schema["$defs"]
            Draft202012Validator.check_schema({"$defs": self.definitions})
        except (KeyError, SchemaError, RecursionError) as exc:
            raise ManualError("手册契约schema无效") from exc

    def check(self, kind, record):
        schema = {"$defs": self.definitions, "$ref": f"#/$defs/{kind}"}
        try:
            errors = sorted(
                Draft202012Validator(schema).iter_errors(record),
                key=lambda error: str(list(error.path)),
            )
        except (Unresolvable, RecursionError) as exc:
            raise ManualError("契约引用不存在或递归过深") from exc
        if errors:
            error = errors[0]
            location = ".".join(map(str, error.path)) or kind
            raise ManualError(f"{location}: {error.message}")
        return record


def claims(record):
    yield record["purpose"]
    for function in record["functions"]:
        yield function["summary"]
        for branch in function["branches"]:
            yield branch["effect"]
    for relation in record["relationships"]:
        yield relation["summary"]
    for resource in record["resources"]:
        yield resource["summary"]
    for guide in record["modification_guides"]:
        yield guide["answer"]


def annotation_semantics(record, *, repository=None):
    if OWNER_DOMAINS[record["owner"]] != record["domain"]:
        raise ManualError("owner与domain不匹配")
    sources, evidence = {}, {}
    for source in record["sources"]:
        if source["id"] in sources:
            raise ManualError("重复证据来源ID")
        # Validate path syntax even when the external repository is unavailable.
        name = source["path"]
        if (
            name.startswith(("/", "\\"))
            or "\\" in name
            or ":" in name
            or any(p in {"..", ".", ""} for p in name.split("/"))
            or any(ord(c) < 32 for c in name)
        ):
            raise ManualError("非法证据相对路径")
        sources[source["id"]] = source
    line_counts = {}
    if repository is not None:
        for key, source in sources.items():
            raw = read_bytes(source_path(repository, source["path"]), 16 * 1024 * 1024)
            if digest(raw) != source["sha256"]:
                raise ManualError("证据来源摘要变化：" + source["path"])
            try:
                line_counts[key] = len(raw.decode("utf-8-sig").splitlines())
            except UnicodeError as exc:
                raise ManualError("证据须为可读UTF8文本，不执行或猜码页") from exc
    for item in record["evidence"]:
        if item["id"] in evidence or item["source_id"] not in sources:
            raise ManualError("重复证据ID或未知来源")
        if item["end_line"] < item["start_line"]:
            raise ManualError("证据行范围倒置")
        if repository is not None and item["end_line"] > line_counts[item["source_id"]]:
            raise ManualError("证据行范围超过来源文件")
        evidence[item["id"]] = item
    names = [f["name"] for f in record["functions"]]
    if len(names) != len(set(names)):
        raise ManualError("函数限定名重复，请用类名/嵌套限定名区分")
    for claim in claims(record):
        refs = claim["evidence"]
        if any(ref not in evidence for ref in refs):
            raise ManualError("说明引用未知证据")
        if claim["confidence"] != "inferred" and not refs:
            raise ManualError("事实/已核对/实机结论必须引用证据")
        if claim["confidence"] == "runtime_verified" and not any(
            sources[evidence[ref]["source_id"]]["kind"] == "runtime_report"
            for ref in refs
        ):
            raise ManualError("静态源码不能证明实机验收")
