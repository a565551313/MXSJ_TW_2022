from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .guides import load_guides, search_guides
from .io import MAX_INVENTORY, ManualError, digest, module_id, parse_json, read_bytes
from .store import ContentStore


@dataclass
class Catalog:
    baseline: dict
    modules: list[dict]
    warnings: list[str]
    file_hashes: dict[str, str]
    guides: list[dict] = field(default_factory=list)

    def search_guides(self, query=""):
        return search_guides(self.guides, query)

    def search(self, query="", domain="", status=""):
        tokens = query.replace("\\", "/").casefold().split()
        return [
            row
            for row in self.modules
            if (not domain or row["domain"] == domain)
            and (not status or row["review_status"] == status)
            and all(token in row["search_text"] for token in tokens)
        ]

    def payload(self):
        return {
            "guides": self.guides,
            "baseline": self.baseline,
            "modules": self.modules,
            "warnings": self.warnings,
            "coverage": self.coverage(),
        }

    def coverage(self):
        return {
            "expected_entries": sum(a["entries"] for a in self.baseline["archives"]),
            "indexed": len(self.modules),
            "annotated": sum(r["annotation"] is not None for r in self.modules),
            "accepted": sum(r["review_status"] == "accepted" for r in self.modules),
            "excluded": sum(
                r["path_status"] == "excluded_by_policy" for r in self.modules
            ),
        }


def _read_inventory(store):
    raw = read_bytes(store.root / "inventory/modules.jsonl", MAX_INVENTORY)
    store.file_hashes["inventory/modules.jsonl"] = digest(raw)
    inventory = {}
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = store.contract.check("inventory", parse_json(line))
            archive, key = store.identity(row)
            if key in inventory or row["vm"] != archive["vm"]:
                raise ManualError("重复模块身份或VM不匹配")
            excluded = row["entry_index"] in archive["excluded_indices"]
            if excluded != (row["path_status"] == "excluded_by_policy"):
                raise ManualError("排除条目必须只保留政策元数据")
            if excluded and (row["path"] is not None or row["functions"]):
                raise ManualError("排除条目不得包含路径/函数内容")
            if row["path_status"] in {"structurally_read", "historical", "directory"}:
                if not row["path"]:
                    raise ManualError("可读路径状态缺少路径")
            inventory[key] = row
        except ManualError as exc:
            raise ManualError(f"inventory第{number}行：{exc}") from exc
    return inventory


def _compose(store, inventory, tasks, annotations, reviews, repository):
    modules, warnings = [], []
    for key in reviews:
        if key not in annotations:
            raise ManualError("审核引用尚不存在的说明")
    for key, row in inventory.items():
        annotation, annotation_hash = annotations.get(key, (None, None))
        task = tasks.get(key)
        review = reviews.get(key)
        status = "unannotated" if annotation is None else "pending"
        if review:
            decision = review[0]
            if decision["annotation_sha256"] != annotation_hash:
                status = "stale_review"
                warnings.append("说明已变化，审核过期：" + key)
            else:
                status = decision["decision"]
        if annotation:
            links = list(annotation["related_modules"])
            links.extend(
                r["module"] for r in annotation["relationships"] if r["module"]
            )
            for related in links:
                store.identity(related)
                if module_id(related) not in inventory:
                    warnings.append("关联模块尚未编入目录：" + module_id(related))
        data = {
            **row,
            "id": key,
            "owner": task["owner"] if task else "B",
            "domain": task["domain"] if task else "unassigned",
            "task_state": task["state"] if task else "unassigned",
            "annotation": annotation,
            "annotation_sha256": annotation_hash,
            "review_status": status,
            "review": review[0] if review else None,
            "evidence_status": "verified_bytes_and_lines"
            if repository is not None and annotation
            else "not_checked_in_this_load",
        }
        data["search_text"] = (
            (
                str(row["path"] or "")
                + f" #{row['entry_index']} "
                + json.dumps(annotation or {}, ensure_ascii=False)
                + " "
                + json.dumps(row["functions"], ensure_ascii=False)
            )
            .replace("\\", "/")
            .casefold()
        )
        modules.append(data)
    modules.sort(key=lambda item: (item["path"] or "~", item["id"]))
    return modules, warnings


def load_catalog(root: Path, *, repository=None, require_full=False) -> Catalog:
    store = ContentStore(root)
    inventory = _read_inventory(store)
    expected = sum(a["entries"] for a in store.archives.values())
    if require_full and len(inventory) != expected:
        raise ManualError("全量目录未完成：不能把样板目录当成全量")
    tasks = store.tasks(inventory)
    annotations = store.records(
        "annotations", "annotation", inventory, tasks, repository
    )
    reviews = store.records("reviews", "review", inventory, tasks, repository)
    modules, warnings = _compose(
        store, inventory, tasks, annotations, reviews, repository
    )
    guides = load_guides(store, modules, repository, warnings)
    return Catalog(store.baseline, modules, warnings, store.file_hashes, guides)
