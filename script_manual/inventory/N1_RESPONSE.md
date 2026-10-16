# N1 回应：脚本手册全量目录签名与提取回执修复

> 新 N1 会话交付，不是原 B 会话；逻辑包仍为 B（`script_manual/inventory/`）。
> 本文只陈述实际运行过的命令与结果。结构验证通过 ≠ 语义正确；B 未获语义验收，
> 本会话不自我验收。128382 是结构函数记录数，不是解释数。

## 0. 实际基线与会话

| 项 | 实际值 |
|---|---|
| 任务卡 | `script_manual/coordination/new_agents_20261016/N1.md`，修订 `20261016-new-cohort-v1` |
| 会话分支 | `arena/8c171896-mxsj-tw-2022`（Arena 固定分支；未切换、未复用旧代理分支） |
| 起点 | `9b0dea799768aaacbb967ffc59f45753970752be`（= 集成分支 `arena/61deb9e5-mxsj-tw-2022` 当时的头）。按 AGENTS.md 先推送本分支，再 `git fetch` + `git merge --no-edit 9b0dea7` → `Already up to date`，无合并提交 |
| 原包指纹（运行前后都核对，未变） | `data/script.fls` 8b6e9266…0d72（24,454,082 B）；`data/data.fls` 5f96bdb2…0a12c（354,143 B）；`tools/decompiler/script_fls_keys.json` 43bb090d…ceb；旧 catalog `server/docs/catalog/script_entries.jsonl` d42694bf…2da |
| 真实 20 种子 | `git show cc5c1bad7a806078794eca1ab7482230a18ef9d5:script_manual/inventory/modules.jsonl`：20 行、4027 B、SHA `de75ec619cf61e8a71098bd74f746081547b1423c6d28bd8595039f6a8e3483b`；20 个身份与 `coordination/tasks.json` 完全一致，全部 `historical` |
| 环境 | Linux；Python 3.11.2（与 B 回执相同）；仓库外临时 venv 安装 `script_manual/requirements.txt`（PySide6 6.10.3、jsonschema 4.25.1）与 ruff 0.17.1；未装 PyInstaller，未打包 |

## 1. 逐项回应（任务卡“必做”1–6）

### 1. 仅 `**kwargs` 时错插裸 `*`（A 收据 70 例）

- **先复现**：用修复前提取器（SHA 662c6fbf…）对合成码对象调用 `signature_of`：
  `(a, b, **kwargs)` 被渲染成 `(a, b, *, **kwargs)`，`(**kwargs)` 被渲染成 `(*, **kwargs)`；
  普通、仅 `*args`、两者都有的渲染正确。
- **根因**：`signature_of` 里的 `elif flags & 0x08: params.append("*")` 把 Python 3 的仅关键字分隔符
  套到了 Python 2。依据 CPython v2.5.6 `Lib/inspect.py` 672–728 行（getargs：`co_varnames[nargs]`
  依次为 `*`/`**` 名）与 769–793 行（formatargspec：只在存在时追加 `*名`/`**名`，从不输出裸 `*`），
  `Include/code.h` 31–36 行（CO_VARARGS=0x04、CO_VARKEYWORDS=0x08）。
- **修复**：新 `signature_parts()` 按 co_varnames 布局读取（位置形参 → 可选 `*名` → 可选 `**名`）。
- **结果**：70 条（script 53 + data 17）全部变为“原签名删去裸 `*`”，例如 entry 30
  `CAccountMgr.GetUrl (self, path, *, **dct)` → `(self, path, **dct)`。与 A 收据
  `B.affected_signatures` 按 (archive_sha256, entry_index, name, 签名) 多重集合逐条相等（测试
  `test_against_bdf_machine_receipt`）。新目录裸 `*` 签名为 0。
- **没有回归**：其余 128078 条函数记录的签名值（含 class 与元数据不足的 null）与 B 版逐字相同。
  旧版 2091 条含 `*名` 的签名中，2087 条逐字不变；另外 4 条（其中 1 条同时含 `**名`）因带内部槽或
  乱码形参转为 null，属于 §1.2 / §1.2b 的分类，不是渲染回归。有/无位置形参两种情况都有合成测试覆盖。

### 2. 48 条 `.0/.1/.3…` 编译器内部槽签名

- **依据**：CPython v2.5.6 `Python/symtable.c` 1216–1218 行 `symtable_implicit_arg` 生成 `".%d"`；
  1243–1246 行：第 i 个 tuple 形参记为 `.i`；1412–1413 行：生成器表达式的外层迭代器记为 `.0`；
  `Lib/inspect.py` 689 行把以 `''`/`'.'` 开头的名字视为匿名 tuple 形参（需要读字节码才能还原）。
- **处理**：只要有一个形参名命中 `\.[0-9]+`（fullmatch），签名就记 `null`。函数记录、限定名、kind 都保留。
  原渲染与槽名只作为审阅线索，写入回执 `signature_audit.rejected[]`（reason=`compiler_internal_slot`），
  例如 `BlockFinder.tokeneater` 原渲染 `(self, type, token, .3, .4, line)`，槽名 `[".3", ".4"]`。
  不猜 tuple 形状，也不从旧 catalog 补签名。
- **结果**：48 条（script 33 + data 15）全部为 null，与 A 收据 `B.internal_argument_signatures`
  逐条相等（同一测试）。新目录内部槽签名为 0。

### 2b. 范围判断，请 A 确认：另有 186 条形参名不是标识符

- 同一检查还发现 186 条签名的形参名不是 Python 2 标识符。它们分布在 script.fls 的 91 个条目中，
  data.fls 为 0。例如 entry 178 `CDecorateMainDlg.__init__ (\x89elf, oParent, iPage, iSubPage)`、
  entry 13 `(self, pSkillM24:cDlg)`、entry 3514 `(iModuleID, \x06\r\x1c\x07\nj)`。
  它们的形态与 B 回执中 `suspect_names` 的函数名相同（B 原文写的是 possible marshal seam garbling）；
  这里只是推断，没有逐条证实成因。
- 这些名字同样不能冒充公开调用参数，所以一并记 `null`（reason=`non_identifier_parameter`）。
  回执保留原渲染和原字节 hex，名字本身不修复。这是把任务卡第 2 条原则（不可靠就 null）延伸到 A 所列
  48 条之外，属于可逆的范围判断：如果 A 认为应保留带乱码的签名，删掉 `check_signature` 中的
  非标识符分支后重放即可。
- 局限：乱码后恰好仍是合法标识符的名字，无法靠标识符规则识别。

### 3. 拒绝 fallback 的实际原值（880/2310/3078/3122）

- **原问题**：B 版代码注释写的是“原样保留”，实际却把 fallback 清成 `""`。
- **修复**：`rejected_fallback()` 保持原优先级（`index_filename` → `historical_filename`）。
  遇到控制字符时，`fallback` 仍为 `""`，只表示“未采用任何回退”，不是原值。原值另记在
  `script_failures[].fallback_rejected`，字段包括：`source`、`source_sha256`（d42694bf…）、`field`、
  `original_value`（由 JSON 序列化转义控制字符）、`original_value_utf8_hex`、
  `control_characters`（偏移与码位）、`disposition`。

| entry | 字段 | 原值（JSON 转义） | 控制字符 |
|---|---|---|---|
| 880 | index_filename | `script/dialog/newwarui/newus\u0000item/newwaruseitemdefine.py` | 偏移 28，U+0000 |
| 2310 | index_filename | `script/mxgame/activity/heartychocolate/heartych\u0000colatedefine.py` | 偏移 47，U+0000 |
| 3078 | index_filename | `script/reddotsys/redpoint\rool/redpointfoldersystemdefine.py` | 偏移 25，U+000D |
| 3122 | index_filename | `script/pyb2/pubbigdata/pubbigdax\u0000value.py` | 偏移 32，U+0000 |

- 4 条原值与 A 收据 `rejected_fallback_originals_missing_from_B_receipt[].original_historical_path`
  逐条相等（测试断言）。这 4 条在 modules.jsonl 中仍是 `unreadable`、`path=null`，未改变。

### 4. 独立纯元数据回归

- 新文件 `script_manual/inventory/test_signature_metadata.py`，共 32 项。
  不打开原包，不执行任何游戏代码，不改 A 的测试。
  - 五类（`FiveClassSignatureTest`）：普通、仅 `*args`、仅 `**kwargs`（有位置形参 / 无位置形参）、
    两者都有（有 / 无位置形参）、内部槽（生成器表达式 `.0`、tuple 形参 `.3/.4`、带 `**kw` 的 `.1`）。
  - 被拒名字：接缝字节、控制字符、结尾换行（`re.match` 的 `$` 会放过它）、非 ASCII、空名，
    以及“槽名优先于乱码”的判定。
  - 元数据不一致的情况（argcount 越界、标志位缺名、负 argcount）→ unavailable。
  - 独立口径（`IndependentOracleTest`）：CPython 自己编译 7 个无仅关键字形参的函数，以
    `inspect.signature` 的输出作为期望值，被测代码只拿到 (co_argcount, co_varnames, co_flags)；
    再用真实生成器表达式提供 `.0`。这一层不复用被测实现的任何逻辑。
  - `extract_functions` 合成树：被拒签名只把 `signature` 置 null，记录数、限定名、kind 不变，审计清单完整。
  - `rejected_fallback` 单元测试；`AuditedArchive` 对排除条目“先登记、再拒绝”。
  - 交付数据：5135 身份、128382 记录、状态分布、1288 元记录、全部签名形状合规、回执/回归报告摘要
    与文件一致、签名审计与目录一致、4 条原值，以及与 A 的 BDF 机器收据逐条对照（文件存在时执行，
    本次已执行，未跳过）。
- **反证**：在 B 旧目录（未修复）上运行同一测试文件，交付数据类 6 项失败，检出 304 个不合规签名
  （70+48+186），并发现回执缺字段；合成类 25 项通过。说明这套测试能抓住原缺陷。

### 5. 真实 20 种子，在仓库外隔离树依次 `--sample` → `--full`

- 隔离树只复制固定输入与复用工具。`inventory/` 中只放 cc5c1ba 的 20 行种子，不放旧
  `sample_regression.json`。分别在两棵全新的树中独立运行，运行时间与结果见 §4。
- 种子来源有记录：`seed_source.is_frozen_seed_file=true`；20 条全部取自种子文件的 historical 行；
  从旧回归报告补入 0 条。
- 两棵树产出的三份文件逐字节一致，原样拷回仓库。之后又用仓库内脚本 `n1_replay_audit.py` 从头重放
  两棵树，结果仍逐字节一致，并且等于已交付文件（`delivered_equal_replay=true`）。
- 20 条样板回归：除新增字段 `signatures_rejected_null`（20 条均为 0，样板中没有受影响签名）外，
  所有字段与 B 版报告相同，`all_paths_match_seed=true`。

### 6. 没有静默丢失（对比基线 9b0dea7 的 modules.jsonl，逐条比较）

| 检查 | 基线（B） | 本次（N1） |
|---|---|---|
| 行数 / 身份（含顺序） | 5135 | 5135，顺序相同 |
| path / vm / path_status 变化 | — | 0 / 0 / 0 |
| 函数记录 | 128382 | 128382（每条的 name、kind 相同；按条目计数变化 0） |
| 状态分布 | script 4950 结构读 / 37 historical / 14 unreadable / 1 excluded；data 121 结构读 / 12 directory | 相同 |
| 20 种子路径 | 一致 | 一致 |
| 非空路径重复 | 0（`duplicate_paths_kept: []`） | 0（不变） |
| 重复限定名 | 193 | 193（清单相同） |
| 1288 | 仅政策元记录 | 逐字段相同（`excluded_1288_exact=true`） |
| 可确认签名 | 118363 | 118129（−48 内部槽 −186 非标识符；70 条改写后仍可确认） |
| 非 class 的 null 签名 | 71（元数据不足） | 305 = 71 + 48 + 186 |
| 签名变化分类 | — | 删去裸 `*` 70 / 内部槽→null 48 / 非标识符→null 186 / 其他 0；未变 128078 |

- **1288 读取审计**：所有运行中 `read_stored(1288)` 都是 0。B 版已靠 `continue` 跳过 1288；
  本次另加 `AuditedArchive`，对排除条目在任何定点读取前拒绝，并把读取统计写进回执 `read_audit`。
  外部 harness 还在 `FileReader.read_at` 层统计：每次运行与 1288 目录区间（偏移 3460344、长 5661）
  重叠的底层读取都只有 1 次，来自整包 SHA-256 指纹（script 按 24 个 1 MiB 块顺序读完整包）。
  也就是说，1288 的字节确实作为整包哈希输入被读过，这里不声称“完全未读”；但它从未被定点请求、
  解压、解密或解析。另外，读取目录索引时会解析到 1288 的目录元数据（偏移/长度），那不是负载。
- 每次运行：script 共 10002 次 `read_stored`，涉及 5001 个条目。代码路径是提取时
  `doc.read_stored` 1 次、`KeyProfile.validate` 再读 1 次；总数正好等于 2×5001，所以每条恰好 2 次。
  data 121 次（只在 `--full` 时读）。与 A 之前重放的口径一致（两次运行合计 20004 次、
  5001 个不同条目、从未请求 1288）。

## 2. 改动清单

| 文件 | 改动 |
|---|---|
| `extract_inventory.py` | 662c6fbf… → e12addfb…。新增 `signature_parts` / `render_signature` / `SignatureCheck` / `check_signature` / `count_signature` / `signature_is_wellformed`；`signature_of` 改为薄封装；`extract_functions` 增加可选 `audit_sink`（参数向后兼容）；新增 `AuditedArchive`（定点读审计 + 排除条目拒读）、`rejected_fallback`、`note_signatures`、`new_audit`、`signature_counts`、`loaded_script_editor_modules`；`load_old_catalog` 和 `sample_report` 改为一次读取字节、同时用于哈希与解析（只按 `\n` 分行）；`sample_report` 记录种子来源；回执新增 `logical_owner` / `session` / `revision_note` / `inputs.frozen_seed` / `tools.loaded_script_editor_modules_sha256`（实际加载的 21 个模块，B 原清单只列 13 个）/ `isolation` / `rejected_fallback_entries` / `seed_source` / `read_audit` / `signature_audit` 和新增自检项；`agent` 字段由 `B` 改为 `N1`（逻辑包仍是 B）。路径、kind 判定、`walk_standard` / `classify_children` 未改 |
| `modules.jsonl` | 35203710… → 266a7834…（11,995,883 → 11,990,715 B），只有签名变化，见 §1.6 |
| `sample_regression.json` | 7a538b1d… → d179e158…；新增 `seed_source` / `extractor_sha256` / `read_audit` 和逐条 `signatures_rejected_null` |
| `B_extraction_receipt.json` | 52c606e9… → 2ce69d3a…（21 KB → 177 KB，增量主要是逐条的签名审计清单）；51 条失败记录中，除 4 条新增 `fallback_rejected` 外不变；`data_failures`、重名清单、可疑名样例、13 个复用模块 SHA 都不变 |
| `test_signature_metadata.py` | 新增，0a0c0718… |
| `n1_replay_audit.py` | 新增，81bf9f47…：建隔离树、核对种子、子进程重放、外部读审计、跨树比较、与基线逐条对比 |
| `N1_replay_audit.json.template` | 新增，9ac56ad5…：上述脚本产出的辅助机器报告（不是注释，手册不加载；不含本机绝对路径） |
| `N1_RESPONSE.md` | 本文 |

未改动：A 所属的 src / schema / coordination / tasks / tests / docs（包括 `docs/STATUS.md`）、原包、
密钥 JSON、编辑器、启动器。AGENTS.md 要求每轮结束更新 STATUS，但任务卡把 STATUS 划归 A，
因此本轮不更新，交由 A 汇总。

## 3. 摘要

| 对象 | SHA-256 |
|---|---|
| 提取器（运行版 = 仓库版） | `e12addfbed390638d850e0bba2e8116e518528f875f5a7d26091e19e35ec8c11` |
| 重放 / 审计脚本 | `81bf9f470b80cf430df0a8c075a3ce90e699337c698e95d3f12e8e4be09c6d5e` |
| modules.jsonl | `266a7834765bb6b106d7c9e25261c2751277808d0b4d4be12bfbd142638ebf5c` |
| sample_regression.json | `d179e1586151e1ffadd0a3016a4822bceb67a842da83aaf9bc16c48639b96051` |
| B_extraction_receipt.json | `2ce69d3afeefcf37cef488e99d7f9b44274047cfceab677b512b22a7243504aa` |
| N1_replay_audit.json.template | `9ac56ad577d9be5c1a69caef3040300a1db7010440d74e839133e559a372a336` |
| test_signature_metadata.py | `0a0c071879890c03c909002000f3d671c12ce5f9062ffafea56ee7732dcaceba` |
| 13 个复用模块 | 与 B 回执相同（`tools.reused_modules_sha256`）；实际加载的 21 个模块见 `tools.loaded_script_editor_modules_sha256` |
| CPython v2.5.6 依据文件（经 api.github.com 只读获取，git blob 与 API 一致） | `Lib/inspect.py` blob 000725ac…；`Python/symtable.c` blob 3e58b503…；`Python/compile.c` blob d40357c4…；`Include/code.h` blob 334ebab4… |

## 4. 实际命令与结果（Linux）

```
# 修复前复现（合成码对象，修复前提取器 662c6fbf…）
kwargs_only          expected '(a, b, **kwargs)'  actual '(a, b, *, **kwargs)'  MISMATCH
kwargs_no_positional expected '(**kwargs)'        actual '(*, **kwargs)'        MISMATCH
internal_slot_tuple  expected None  actual '(self, type, token, .3, .4, line)'  MISMATCH
internal_slot_genexpr expected None actual '(.0)'                               MISMATCH
ordinary / varargs_only / both                                                  OK

# 隔离树（两棵，各自先 --sample 后 --full；外部审计 harness 包住提取器）
--sample  exit 0  13.3–14.9 s  script: structurally_read 4950, historical 37, unreadable 14,
          excluded_by_policy 1, functions_total 125973, signatures 115953, signature_kwargs_only 53,
          signature_rejected_compiler_internal_slot 33, signature_rejected_non_identifier_parameter 186,
          signature_unavailable 71, fallback_rejected_control_chars 4
          all_paths=True; seed_source: is_frozen_seed_file True, from historical rows 20, from prior 0
--full    exit 0  14.7–16.2 s  data: structurally_read 121, directory 12, functions_total 2409,
          signatures 2176, signature_kwargs_only 17, signature_rejected_compiler_internal_slot 15
          inventory written rows=5135
审计（最终提取器 e12addfb… 共 8 次运行结果一致：手工建的两棵树 4 次 + n1_replay_audit.py 两棵树 4 次）：
          script read_stored 10002 / 5001 个条目 / 1288=0；data 121（仅 --full）；
          与 1288 区间重叠的读取 = {"fingerprint": 1}；原包摘要运行前后相同
两棵树三份产物逐字节一致；N1_replay_audit.json.template: all_runs_passed / outputs_identical_across_trees /
          delivered_equal_replay 均为 true

# 标准验证
PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --require-full-inventory --repository .
  → exit 0  {"expected_entries": 5135, "indexed": 5135, "annotated": 20, "accepted": 3, "excluded": 1}
PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest discover -s script_manual/tests -v
  → exit 0  Ran 82 tests, OK (skipped=11)：71 通过 + 11 个 GUI 测试跳过
    （ImportError: libGL.so.1；GUI 未执行，不计为通过）
ruff check script_manual script_manual/script_manual.spec            → All checks passed!
python tools/devkit/check_windows_compat.py script_manual --strict  → 文件名 125 项、源码扫描 29 个，ERROR 0 / WARNING 0 / INFO 0

# N1 回归
python -m unittest discover -s script_manual/inventory -p 'test_*.py' -v → Ran 32 tests, OK（无跳过）
```

复现方式（仓库根目录，`--work` 必须位于仓库外且是新目录）：
`python3 script_manual/inventory/n1_replay_audit.py --work <仓库外新目录> --report <路径>.json.template`

## 5. 未运行项 / 风险 / 待 A 决定

- **Linux 已做**：上面全部命令。**Windows 待测**：没有在 Windows 上运行提取器或测试，没有构建或运行 EXE，
  没有运行游戏；`check_windows_compat` 只是静态检查。11 个 GUI 测试因缺 `libGL.so.1` 被跳过，
  不代表 GUI 可用。
- **已知差异**：签名口径变化（70 条改写，234 条转为 null）；回执 `agent` 由 `B` 改为 `N1`
  （另有 `logical_owner: B`），文件名保持 `B_extraction_receipt.json` 不变，方便兼容；回执体积增大到 177 KB。
- **范围判断**：186 条非标识符形参签名置 null（§1.2b）超出 A 所列 48 条，请 A 确认或否决。
- **残余风险**：
  1. 乱码后仍是合法标识符的形参名无法识别。
  2. 自定义 VM 的码对象标志位按标准 CPython 2 解读，没有独立证明。旁证：落在 `**` 位置上的名字以
     惯用名为主（22 种，`**kwargs` 130、`**kw` 34、`**argvs` 15、`**kwds` 10、`**dct` 9 …），
     落在 `*` 位置上的以 `args` 为主（37 种，`*args` 1916、`*arg` 48 …），与标准解读一致；
     如果标志位含义不同，这两个位置上应出现普通局部变量名。
  3. 默认值不渲染；签名为 null 表示“未知”，不表示“无参数”。
  4. `AuditedArchive` 依赖 `ArchiveDocument` 的私有属性 `_fingerprint`；编辑器改实现时需要同步。
  5. 旧的函数名可疑性检查仍用 `re.match` 加 `$`（会放过结尾换行）；当前 0 个函数名受影响，未改动该口径。
- **不声称**：B 已获语义验收；128382 是解释数；结构验证通过即语义正确；Windows / EXE / 游戏已验证。
