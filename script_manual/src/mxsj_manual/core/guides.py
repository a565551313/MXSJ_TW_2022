"""Task-oriented editorial guides bound to exact, independently tracked inputs.

Navigation readiness is NOT acceptance. Source changes disable old anchors;
optional excerpts are read as text only, after the source digest is checked.
"""

from __future__ import annotations

from .io import ManualError, digest, module_id, read_bytes, source_path


def load_guides(store, modules, repository, warnings):
    folder = store.root / "guides"
    if not folder.exists():
        return []  # Older content/isolated fixtures remain supported.
    if folder.is_symlink() or not folder.is_dir():
        raise ManualError("专题目录不得为符号链接")
    paths = sorted(folder.iterdir())
    if len(paths) > 200 or any(p.is_symlink() or p.is_dir() for p in paths):
        raise ManualError("专题须为有限数量的平面文件，不允许符号链接或子目录")
    by_id = {row["id"]: row for row in modules}
    result, ids, cache = [], set(), {}
    size = 0
    for path in paths:
        if path.suffix != ".json":
            continue
        size += path.stat().st_size
        if size > 4 * 1024 * 1024:
            raise ManualError("专题总量超过4MiB")
        guide = store.load(path, "guide")
        if guide["id"] in ids:
            raise ManualError("重复专题身份：" + guide["id"])
        ids.add(guide["id"])
        stale = []
        for step in guide["steps"]:
            for ref in step["references"]:
                key = module_id(ref)
                row = by_id.get(key)
                if row is None or not row["annotation"]:
                    raise ManualError("专题引用未编写模块：" + key)
                if row["path_status"] == "excluded_by_policy":
                    raise ManualError("专题不得引用政策排除模块")
                ref.update(
                    module_id=key,
                    path=row["path"],
                    review_status=row["review_status"],
                    reviewer=row["review"]["reviewer"] if row["review"] else None,
                    binding_current=row["annotation_sha256"]
                    == ref["annotation_sha256"],
                    evidence=[],
                )
                if not ref["binding_current"]:
                    stale.append(row["path"])
                    continue  # Never bind old prose to changed function/evidence IDs.
                annotation = row["annotation"]
                functions = {
                    f["name"]: i for i, f in enumerate(annotation["functions"])
                }
                if ref["function"] not in functions:
                    raise ManualError("专题函数未在对应正文登记：" + ref["function"])
                ref["function_index"] = functions[ref["function"]]
                evidence = {e["id"]: e for e in annotation["evidence"]}
                sources = {s["id"]: s for s in annotation["sources"]}
                for identity in ref["evidence_ids"]:
                    if identity not in evidence:
                        raise ManualError("专题引用未知证据：" + identity)
                    item = evidence[identity]
                    source = sources[item["source_id"]]
                    excerpt = {
                        **item,
                        "path": source["path"],
                        "sha256": source["sha256"],
                        "lines": [],
                        "verified": repository is not None,
                    }
                    if repository is not None:
                        name = source["path"]
                        if name not in cache:
                            raw = read_bytes(
                                source_path(repository, name), 16 * 1024 * 1024
                            )
                            if digest(raw) != source["sha256"]:
                                raise ManualError("专题证据字节已变化：" + name)
                            try:
                                cache[name] = (
                                    source["sha256"],
                                    raw.decode("utf-8").splitlines(),
                                )
                            except UnicodeDecodeError as exc:
                                raise ManualError("专题来源非UTF8：" + name) from exc
                        expected_sha, lines = cache[name]
                        if expected_sha != source["sha256"]:
                            raise ManualError(
                                "专题对同一路径的来源SHA绑定冲突：" + name
                            )
                        start, end = item["start_line"], item["end_line"]
                        if end > len(lines):
                            raise ManualError("专题证据行越界：" + identity)
                        stop = min(end, start + 59)
                        excerpt["lines"] = [
                            {"number": n, "text": lines[n - 1]}
                            for n in range(start, stop + 1)
                        ]
                        excerpt["truncated"] = stop < end
                    ref["evidence"].append(excerpt)
        guide["stale_dependencies"] = sorted(set(stale))
        guide["navigation_status"] = "stale" if stale else "current"
        if stale:
            warnings.append("专题引用正文已变化（禁用旧锚点）：" + guide["title"])
        searchable = [
            guide["title"],
            guide["summary"],
            *guide["keywords"],
            *guide["prerequisites"],
            *guide["limitations"],
        ]
        for step in guide["steps"]:
            searchable.extend(
                step[k] for k in ("title", "explanation", "change", "check")
            )
            for ref in step["references"]:
                searchable.extend([ref["path"], ref["function"], *ref["evidence_ids"]])
        guide["search_text"] = " ".join(searchable).replace("\\", "/").casefold()
        result.append(guide)
    return result


def search_guides(guides, query=""):
    tokens = query.replace("\\", "/").casefold().split()
    return [g for g in guides if all(t in g["search_text"] for t in tokens)]
