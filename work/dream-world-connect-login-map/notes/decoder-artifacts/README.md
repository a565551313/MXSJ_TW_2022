# decoder-artifacts 目录说明（2026-10-10 核对更新）

| 文件 | 状态 | 说明 |
|---|---|---|
| `entry516-result.json` | ✅ | 对 `data/script.fls` 的 entry 516 解码结果；`archive.entry_count` = 5002，`all_entries_zlib_verified` = true |
| `entry516-five-xor-marshal.bin` | ✅ | 17,234 B；已用 `tools/fls_batch_decoder.py --archive … --index 516` 在仓库外重跑，结果一致（59 个 code object） |
| `decode_entry516.py` | 历史脚本 | 旧版入口，建议改用 `tools/fls_batch_decoder.py` |
| `all_scripts_catalog.json` | ❌ **只有 11 条记录**，不是全部 5002 条 | 旧文档称其为“全部 5002 条目 catalog”，不成立。完整目录请使用 `notes/task-b-脚本分析/artifacts/script-catalog.csv`（5002 条数据行 + 表头）和 `notes/task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl`（5002 行） |
| `run-output.json` | 历史 | 其中一段为二进制内容，直接 `json.load` 会失败，属于历史产物 |

本目录内任何文件都未被删除；上述说明仅作注释。
