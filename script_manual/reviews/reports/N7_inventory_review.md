# N7_inventory_review · 全量目录语义验收（PR#43 / N1）

> 审核会话：**N7 新会话**（Arena 2026-10-16 分配的第 7 个新 agent，逻辑任务包 H / review）。
> 不是旧 H、不是 A、不是旧 B；未代写任何作者正文，只写本审核记录。
> 本文件是**报告**，`inventory/` 目录本身不符合 `$defs.annotation` review schema，
> 因此按任务卡要求**不造 entry、不塞 JSON**，只以 Markdown 记录语义验收结论。

## 0. 基线与输入

| 项 | 值 |
|---|---|
| 集成分支固定 head | `9b0dea799768aaacbb967ffc59f45753970752be` |
| 合并内容检查点 | `7d32e5340b0ab4168f725d238d767ad6232f715d` 已确认在祖先中 |
| 本机锁定输入 | `data/script.fls` `8b6e9266…0d72`、`data/data.fls` `5f96bdb2…0a12c`、`tools/decompiler/script_fls_keys.json` `43bb090d…ceb` —— `sha256sum` 逐条核对一致，未改动 |
| 旧 catalog | `server/docs/catalog/script_entries.jsonl` `d42694bf…2da` 一致 |
| PR#43 head | `f953eb992bf3c5d072ae478a0ac67e4d651e5064` |
| 分析环境 | 仓库外 venv，Python **3.11.2** + `jsonschema==4.25.1` + `ruff==0.17.1`；复现树另需仓库 `script_editor/`（提取器 `extract_inventory.py` 依赖 `script_editor.core.archives.flsdata`） |

## 1. 真实 20 种子 → 5135 复现：**本会话独立重跑，三份产物逐字节一致**

冻结种子取 `git show cc5c1bad7a806078794eca1ab7482230a18ef9d5:script_manual/inventory/modules.jsonl`：

| 核对项 | N1 自报 | 本会话实测 | 结论 |
|---|---|---|---|
| 种子文件行数 / 字节 | 20 / 4027 | 20 / 4027 | 一致 |
| 种子文件 SHA256 | `de75ec619cf61e8a71098bd74f746081547b1423c6d28bd8595039f6a8e3483b` | 同 | **逐字一致** |
| 种子身份 | 20 条全部 `historical`，与 `coordination/tasks.json` 一致 | 同（提取器回执 `historical_seed_rows_in_modules_jsonl=20`） | 一致 |

在**全新的仓库外隔离树**（`script_manual/`、`script_editor/`、`server/docs/catalog/`、`data/`、参数表；`inventory/` 只放 20 行种子，不放旧 `sample_regression.json`）依次执行：

```bash
python script_manual/inventory/extract_inventory.py --sample   # 20 行种子，14.7s
python script_manual/inventory/extract_inventory.py --full     # 13.6s，rows=5135
```

`--sample` 回执要点，与 N1 自报一致：`all_paths=True`；
`seed_source.is_frozen_seed_file=true`、`frozen_seed_sha256=de75ec61…`、`seed_paths_from_prior_sample_regression=0`（**未从旧回归报告补种子**）。

三份产物与 PR#43 交付文件逐字节比对：

| 文件 | 本会话重跑 SHA256 | PR#43 交付 SHA256 | `cmp` |
|---|---|---|---|
| `inventory/modules.jsonl` | `266a7834765bb6b106d7c9e25261c2751277808d0b4d4be12bfbd142638ebf5c` | 同 | **IDENTICAL** |
| `inventory/B_extraction_receipt.json` | `2ce69d3afeefcf37cef488e99d7f9b44274047cfceab677b512b22a7243504aa` | 同 | **IDENTICAL** |
| `inventory/sample_regression.json` | `d179e1586151e1ffadd0a3016a4822bceb67a842da83aaf9bc16c48639b96051` | 同 | **IDENTICAL** |

**结论：真实 20 种子 → 5135 的复现成立，且本会话独立重跑得到逐字节相同的三份产物。**

## 2. 签名修复：独立复算，与 N1 自报逐项吻合

| 指标 | 基线（B，`35203710…`） | PR#43（N1，`266a7834…`） | 判定 |
|---|---:|---:|---|
| 身份数 / 顺序 | 5135 | 5135，顺序相同 | 无静默丢失 |
| 函数记录总数 | 128382 | 128382 | 无静默丢失 |
| 含内部槽（`.0/.1/.3`）的签名 | 48 | **0** | 已按策略置 null |
| `null` 签名 | 10019 | 10253（+234） | +234 = 48 内部槽 + 186 非标识符形参，**与 N1 自报完全吻合** |
| 状态分布 | script 4950 结构读 / 37 historical / 14 unreadable / 1 excluded；data 121 结构读 / 12 directory | 完全相同 | 未因修签名而变 |
| `path` / `vm` / `path_status` 变化 | — | 0 / 0 / 0 | 未漂移 |

**裸 `*`（A 收据记 70 例）**：本会话用较宽正则 `\*(?!\*|\w)` 统计基线上命中 **72** 条；逐条核对后其中 **70 条确实形如 `(self, path, *, **dct)`**（含 `**kwargs`），另 2 条是 `entry 4621` 的**乱码形参名**（`CCustomWalkerBase.GetShowInSpecial` `(self, \r\x17*\x14c, walkShow, nameShow)`、`NpcLimit` `(self, \r\x17*\x14c)`），并非“错插裸 `*`”。
→ **A 的 70 计数正确**；那 2 条乱码在 PR#43 中已由“非标识符形参”规则一并置 null，PR#43 的裸 `*` 计数为 **0**。

**拒绝 fallback 原值（880/2310/3078/3122）**：从 PR#43 回执 `script_failures[].fallback_rejected` 读出，与 N1 表格**逐条逐字段一致**：

| entry | 原值（JSON 转义） | 控制字符 |
|---|---|---|
| 880 | `script/dialog/newwarui/newus\x00item/newwaruseitemdefine.py` | 偏移 28，U+0000 |
| 2310 | `script/mxgame/activity/heartych\x00colatedefine.py` | 偏移 47，U+0000 |
| 3078 | `script/reddotsys/redpoint\rool/redpointfoldersystemdefine.py` | 偏移 25，U+000D |
| 3122 | `script/pyb2/pubbigdata/pubbigdax\x00value.py` | 偏移 32，U+0000 |

四条在 `modules.jsonl` 中仍为 `unreadable`、`path=null`，**未借修复改状态**。

**签名审计**：`B_extraction_receipt.json` 的 `signature_audit.rejected` 共 **234** 条 = `non_identifier_parameter` 186 + `compiler_internal_slot` 48，与 N1 自报一致。

## 3. 五类纯元数据回归测试：本会话实跑通过，并做了反证

```bash
PYTHONPATH=.:script_manual/src python -m unittest discover -s script_manual/inventory \
  -p 'test_signature_metadata.py'
```

- 对 **PR#43**：`Ran 32 tests … OK`（32 项全通过，0 失败/0 错误）。
- **反证**（本会话自建：把 `inventory/` 换回基线 9b0dea7 的旧提取器 + 旧目录 + 旧回执，只保留新的测试文件）：
  `Ran 32 tests … FAILED (failures=13, errors=16)`，仅 3 项 ok、1 项 skipped（跳过原因：机器收据不在该树）。
  失败项覆盖 `FiveClassSignatureTest` 全部五类（普通 / 仅 `*args` / 仅 `**kwargs` 有·无位置形参 / 两者都有 / 内部槽）、
  `test_every_signature_is_wellformed`、`test_signature_audit_matches_inventory`、`test_rejected_fallbacks_keep_originals` 等。
  → **这套测试确实能抓住原缺陷，不是为通过而写的空测试。**

> 与 N1 自报的口径差异（需 A 知悉，非缺陷）：N1 在响应中写的是“交付数据类 6 项失败、合成类 25 项通过”。
> 本会话的反证树**连提取器也换回旧版**，故合成类同样失败（29 项未通过）。两者反证树构成不同，结论一致。
> 建议 A 要求 N1 在响应里写明反证树的具体构成（旧代码+旧数据 还是 新代码+旧数据），以免后续复算对不上。

## 4. 1288 政策边界：实测守住

`modules.jsonl` 中 `path_status == excluded_by_policy` 的记录**恰好 1 条**，即 `entry_index=1288`，其 `path=null`、`functions=[]`，两个基线/PR#43 版本一致。

本会话未对 1288 做定点恢复、未读其 payload。需要如实指出的边界：

- 提取器为计算整包指纹会**读取整个 `data/script.fls` 的字节**，这与“不对 1288 定点恢复/不解其 payload”并不矛盾，但**不能反过来声称“其字节完全未被读过”**。这一点与 A 的 BDF 报告口径一致，N1 响应中未见越界表述。

## 5. 语义验收结论

**（1）结构与可复现性：通过（有限范围）。** 20 种子 → 5135 可逐字节复现；128382 条函数记录在修签名前后不变；状态分布不变；路径未漂移；1288 政策边界守住；拒绝 fallback 原值已如实留痕。

**（2）目录语义：仍不接受“语义已验收”。** 本轮修的是**签名渲染正确性**与**回执保真**，目录本身仍是**自动元数据**：

- 128382 是**结构函数记录数**，不是手册解释完成数；
- 10019→10253 条 `signature=null` 表示**不可靠/未重建**，不是“无参数”；
- `suspect_names=231`、`kind_fallback=1668`、`parent_bytecode_undecodable=1986`、`failures=51`（script）等既有风险**原样保留**，未因本轮修复减少；
- 186 条“非标识符形参置 null”是 N1 **超出 A 所列 48 条之外的范围判断**（已在响应 §2b 明说并给出可逆方式），属合理延伸，但**应由 A 显式确认**，不应由审核代批。

**（3）需要 A 处理的三件事**

1. **目录回归测试未接入标准套件**：`script_manual/inventory/test_signature_metadata.py` 不在 `unittest discover -s script_manual/tests` 的发现范围内（后者实测 82 项）。且它需要 `PYTHONPATH=.`（仓库根）才能 import `script_editor.core.archives.flsdata`——**不带仓库根会直接 `ModuleNotFoundError`**。建议 A 明确其入口命令并考虑接入标准套件，否则这 32 项在常规验证里不会被执行。
2. **186 条范围判断请 A 显式确认**（保留原渲染 vs 置 null 的可逆开关）。
3. **反证树构成请在响应中写明**（见 §3）。
