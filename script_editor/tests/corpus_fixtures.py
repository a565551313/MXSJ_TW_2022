"""Small real containers + external-style artifacts, no corpus/product scripts run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from native_fixtures import minimal_pyc, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.project.storage import CatalogRef


def fixture(root: Path, *, repair=False, mismatched=False):
    data, keys = script_fixture()
    package = root / "original.fls"
    package.write_bytes(data)
    actual = json.loads(json.dumps(keys))
    if repair:
        keys["0"]["bounds"][0] += 1
    path = root / "keys.json"
    path.write_text(json.dumps(keys), encoding="utf8")
    archive = ArchiveDocument(package)
    catalog = CatalogRef(
        package.resolve(),
        archive.fingerprint(),
        path.resolve(),
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )
    corpus = root / "corpus"
    rows = []
    for entry in range(3):
        row = {
            "schema_version": 1,
            "index_base": 0,
            "archive_sha256": archive.fingerprint(),
            "entry_index": entry,
            "status": "failed",
            "engines": {},
            "artifacts": [],
            "transpile": {
                "entry_id": archive.index.metas[entry].entry_id,
                "stage": "baseline",
            },
        }
        rows.append(row)
    row = rows[0]
    row["transpile"].update(actual["0"])
    row["transpile"].update(
        stage="seam_refine" if repair else "baseline", original_parameters=keys["0"]
    )

    def artifact(name, raw):
        path = corpus / f"full/entries/0000/{name}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return {
            "path": path.relative_to(corpus).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }

    row["artifacts"].append(
        artifact("standard.pyc", minimal_pyc("py25", value=2 if mismatched else 1))
    )
    for engine in ("uncompyle6", "pycdc"):
        raw = b"# engine\nx=1\n" if engine == "uncompyle6" else b"x='\xff'\n"
        stdout = artifact(f"raw/{engine}/engine.stdout", raw)
        stderr = artifact(f"raw/{engine}/engine.stderr", b"line1\nline2\n")
        candidate = artifact(
            f"candidates/{engine}/escaped_utf8.py",
            raw.decode("utf8", "backslashreplace").encode("utf8"),
        )
        candidate.update(
            candidate_kind="source_heuristic",
            transform="UTF8-backslashreplace",
            syntax_checks={"2.5.6": {"result": {"status": "pass"}}},
        )
        row["engines"][engine] = {
            "stdout": stdout,
            "stderr": stderr,
            "candidates": [candidate],
            "engine_version": "test",
            "has_source_body": True,
            "raw_invalid_utf8": engine == "pycdc",
            "status": "complete",
            "raw_syntax_checks": {},
        }
    row["status"] = "complete"
    manifest = corpus / "full/manifest.audited.jsonl"
    write_manifest(manifest, rows)
    return archive, catalog, manifest, rows


def write_manifest(path, rows):
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf8")
