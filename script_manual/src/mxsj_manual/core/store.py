from __future__ import annotations

from .io import ManualError, digest, module_id, parse_json, read_bytes
from .validation import OWNER_DOMAINS, Contract, annotation_semantics

MAX_ANNOTATIONS = 32 * 1024 * 1024
# AGENTS.md: this exact archive's sensitive entry must never be restored.
PROTECTED_ARCHIVE = "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"


class ContentStore:
    def __init__(self, root):
        self.root = root.resolve(strict=True)
        for name in ("schema", "coordination", "inventory", "annotations", "reviews"):
            folder = self.root / name
            if folder.is_symlink() or not folder.is_dir():
                raise ManualError("缺少内容目录或目录是符号链接：" + name)
        self.contract = Contract(self.root)
        self.file_hashes = {
            "schema/contract.schema.json": digest(
                read_bytes(self.root / "schema/contract.schema.json")
            )
        }
        self.baseline = self.load(self.root / "coordination/baseline.json", "baseline")
        self.archives = {a["sha256"]: a for a in self.baseline["archives"]}
        if len(self.archives) != len(self.baseline["archives"]):
            raise ManualError("重复包指纹")
        for archive in self.archives.values():
            exclusions = archive["excluded_indices"]
            if len(set(exclusions)) != len(exclusions) or any(
                i >= archive["entries"] for i in exclusions
            ):
                raise ManualError("非法排除范围")
            if archive["sha256"] == PROTECTED_ARCHIVE and 1288 not in exclusions:
                raise ManualError("禁止解除固定原包1288排除政策")
        corpus = self.baseline["corpus_reference"]
        if corpus["status"] == "pinned_manifest_available" and not corpus.get(
            "manifest_sha256"
        ):
            raise ManualError("未提供实际语料manifest摘要，不可宣称已钉死")
        self.consumed = 0

    def load(self, path, kind):
        raw = read_bytes(path)
        self.file_hashes[path.relative_to(self.root).as_posix()] = digest(raw)
        return self.contract.check(kind, parse_json(raw))

    def identity(self, row):
        archive = self.archives.get(row["archive_sha256"])
        if archive is None or row["entry_index"] >= archive["entries"]:
            raise ManualError("记录不属于冻结包/条目范围")
        return archive, module_id(row)

    def tasks(self, inventory):
        tasks = {}
        path = self.root / "coordination/tasks.json"
        for task in self.load(path, "tasks")["tasks"]:
            archive, key = self.identity(task)
            if key in tasks or OWNER_DOMAINS[task["owner"]] != task["domain"]:
                raise ManualError("任务重复或负责人/领域不匹配")
            if key not in inventory:
                raise ManualError("任务引用未登记模块")
            if task["entry_index"] in archive["excluded_indices"]:
                raise ManualError("排除条目不能分配正文任务")
            if task["owner"] in task["collaborators"]:
                raise ManualError("主负责人不能同时列为协审")
            tasks[key] = task
        return tasks

    def records(self, folder_name, kind, inventory, tasks, repository):
        target = {}
        folder = self.root / folder_name
        if any(p.is_symlink() for p in folder.rglob("*")):
            raise ManualError("内容目录不允许符号链接")
        paths = sorted(folder.rglob("*.json"))
        if len(paths) > 10000:
            raise ManualError("内容文件过多，请分批集成")
        for path in paths:
            self.consumed += path.stat().st_size
            if self.consumed > MAX_ANNOTATIONS:
                raise ManualError("说明总量超过32MiB，需分批集成")
            row = self.load(path, kind)
            archive, key = self.identity(row)
            if key in target:
                raise ManualError("模块重复提交，不按文件名静默覆盖：" + key)
            if key not in inventory:
                raise ManualError("提交引用未登记模块")
            if row["entry_index"] in archive["excluded_indices"]:
                raise ManualError("排除模块不得提交说明或审核正文")
            if inventory[key]["path_status"] == "directory":
                raise ManualError("目录记录不是可分析脚本")
            if kind == "annotation":
                self.check_annotation(
                    row, folder, path, key, inventory, tasks, repository
                )
            target[key] = (
                row,
                self.file_hashes[path.relative_to(self.root).as_posix()],
            )
        return target

    @staticmethod
    def check_annotation(row, folder, path, key, inventory, tasks, repository):
        task = tasks.get(key)
        if task is None or (row["owner"], row["domain"]) != (
            task["owner"],
            task["domain"],
        ):
            raise ManualError("未分配任务或跨域抢占")
        if row["path"] != inventory[key]["path"]:
            raise ManualError("说明路径与冻结目录不一致")
        if path.parent != folder / row["domain"]:
            raise ManualError("说明必须放在负责人所属领域目录")
        annotation_semantics(row, repository=repository)
