"""Synthetic guide data; never derive unit expectations from production topics."""

from mxsj_manual.core.io import digest


def install_guide(case):
    record = case.record
    reference = {
        "archive_sha256": record["archive_sha256"],
        "entry_index": record["entry_index"],
        "annotation_sha256": digest(case.annotation.read_bytes()),
        "function": record["functions"][0]["name"],
        "evidence_ids": [record["evidence"][0]["id"]],
    }
    guide = {
        "schema_version": 1,
        "id": "fixture-guide",
        "title": "合成公告任务",
        "domain": "login",
        "author": "synthetic guide author",
        "editorial_status": "draft_unreviewed",
        "summary": "合成入口，不执行源码",
        "keywords": ["合成", "公告"],
        "prerequisites": ["synthetic only"],
        "steps": [
            {
                "title": "检查入口",
                "explanation": "合成流程",
                "change": "仅建议",
                "check": "未执行的检查方案",
                "references": [reference],
            }
        ],
        "limitations": ["并非实机结果"],
    }
    path = case.root / "guides/fixture.json"
    path.parent.mkdir(exist_ok=True)
    case.put(path, guide)
    return path, guide
