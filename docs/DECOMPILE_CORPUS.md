# 全量反编译语料（79 MB）：要不要建、怎么建

> **本文只管一件事**：`data/script.fls` 的**可读副本**（5,517 个 `.py`、2,338,388 行、约 79 MB）
> 默认**不存在于任何环境**——按红线 §4-1 / §4-8 它不入库、只写在仓库外，所以沙箱一重置就没。
> 要用它之前先看 §0；决定要建就照 §3 整段执行；想让用户点头，把 §6 那段模板发出去。
>
> 下面每条命令都在 2026-10-15 的沙箱里实测过（Python 3.11.2 / 2 核），含 §4 那几个坑的复现结果。
> 研究结论与双引擎矩阵的权威文本是
> [`notes/opcode_mapping_and_decompilation.md`](../notes/opcode_mapping_and_decompilation.md) §4.5–§4.6；
> 本文不重复结论，只给可执行配方与判断依据。

> **先看有没有现成的**：全量语料已按基线打成 ZIP 放在 Google Drive 的 `MXSJ_CORPUS` 目录（随附 SHA-256 清单），
> 位置与取用命令见 [`EXTERNAL_CORPUS.md`](EXTERNAL_CORPUS.md)。目录**会随开发更新**（换基线就换卷与清单），
> 取用前先列目录、以目录为准。要的是「现成可验」就用那份，别重跑几小时；
> 本文剩下的是「要自己新建一份 / 换工具版本重建」的配方。

## 0. 先花 30 秒决定（给 AI 的决策表）

| 你要回答的问题 | 该用什么 | 别做什么 |
| :--- | :--- | :--- |
| 「entry N 的代码长什么样」 | §2 法 A：`recover_entries.py --entries N`，**秒级**（实测 1 条 2.3 s） | 别建全量 |
| 「符号 / 字符串 X 在全档**有没有定义者**」这类**否定命题** | §2 法 A 之后 `grep -c` 数标识符；要字节码级就 §3.2 建好 pycdc 后 `--keep-pyc` | 别只 grep 仓库里那 681 份就宣布「不存在」 |
| 「谁加载哪个 `.dlg`、谁取哪个控件、按钮皮肤/消息号」 | `tools/script_link/build_script_index.py`（只做 marshal 解析，不反编译，几分钟）；产物已随 `ui_editor` 入库 | 别为布局问题跑反编译 |
| 「那 499 个 pycdc 交叉复核产物」 | **已在 git**：`tools/decompiler/output/`（681 份 `.py`，15 MB），直接 grep | 别重跑 |
| 「把某模块改回去 / 回编译成新包」 | 语料**不合格**：必须逐档过真 CPython 2.5 `compile()`（§5 第 3 条） | 别把 `script_fls_pycdc/` 当回编输入 |
| 语义级全档检索（引用者 + 定义者 + 上下文一起看） | 才建全量：§3，**小时级** | 别在 `bash` 里前台等（单轮 30 分钟会切断你）→ `start_process` 后台跑 |

**每次都不变的红线**：不覆盖 `data/script.fls` 与 `tools/decompiler/script_fls_keys.json`；
不执行反编译出来的模块、不 `eval` 任何数据（这三个工具只转译/解析，请保持这个性质，别加 `import`）；
产物一律写到仓库外新目录。

### 0.1 数据模块失败的判读（2026-10-22 补充）

反编译失败、marshal 可读、字面量结构通过和原生语义正确是不同结果。
同一工具的自动边界修复也可能引入错误。此次伤害研究核对到：

- entry **3458**：关闭 `solve_py25_co_span`，按保存参数从 DATA 构建起点 258 解析，
  914 条结构通过；此前的 LOAD_NAME/乘法拒绝不能归结为原始游戏代码错误。
- entry **4329**：保存 keys/bounds 下的 EXTENDED_ARG 异常仍可复现；使用独立候选参数后，
  18 组中 6 组通过，六组各 927 条，925 条原始记录值一致，4791/2429 仍有歧义。
- entry **3773**：第一边界 6306→6307 是支持 103 条字面量结构恢复的候选，未作原生验收。

这更正了会话第二轮“这三个表尚不可解析”的状态；不是全量源码成功率的重新统计。
固定参数、失败偏移、当前原生地址限制及可运行复核片段见
[客户端伤害公式研究](../notes/client_damage_formula.md#6-更正解析失败密钥与自动修复)。
不修改锁定 key DB，也不把候选表当成正式服务端配置。

## 1. 它是什么 / 不是什么

**是什么**：`data/script.fls`（5,002 条自定义 `.pyo` 型条目）经「5 段 XOR 解密 → Py2.5 marshal
转译 → 反编译」得到的 `.py` 副本，两条独立引擎互为交叉证据。

```
data/script.fls ──转译──▶ .pyc ──uncompyle6（主）──▶ 5,000 个 .py + 1 个 .pyc
                     同批 .pyc ──pycdc（第二引擎）──▶ 另 517 个 .py
```

**成色**（全语料定案）：4,444 份完整 + 9 份手工救回 + 547 份只有 52 字节失败占位；pycdc 净补
546 条（541 直接命中 + 5 条须开 `--ladder`：`63`/`64`/`1013`/`1528`/`1854`）；两引擎加修复梯全开
后仍**零产物 = 61 条**，其中 `1954`/`3066`/`4166`/`4691` 连转译都过不去。

**不是什么**：不是孤本（本文 §3 就能再生）；不是真相源（真相只有 `data/script.fls`、`data/data.fls`，
语料是**线索**）；不是可回编译源码（uncompyle6 侧原样仅 550/4,998 = 11.0%，删掉模块顶层 `return`
后 3,770 = 75.4%；已入库的 pycdc 499 份是 236 可编 / 263 不可）。

## 2. 不建全量的三条捷径（先试这个）

```sh
cd /home/user/MXSJ_TW_2022
export PY=/home/user/dec-venv/bin/python        # 没有它会直接拒绝开跑（坑 P1 已工程化）
OUT=/home/user/mxsj-dec/probe && mkdir -p "$OUT"
```

**法 A · 单条源码（最快、无外部依赖，实测 2.3 s/条）**

```sh
$PY tools/decompiler/recover_entries.py --out /home/user/mxsj-dec/rec --entries 1931 \
    --report /home/user/mxsj-dec/rec_report.json
#   处理 1 条，用时 0.6s → {'recovered': 1}
#   entry  1931  recovered  source  script/data/servicedata.py        （实测 86,917 B）
```

它带**完整修复梯**（`transpile()` 逐级 baseline → shift → `_resolve_segments` → `_beam_resolve` →
`_refine_seams`），所以能救 `batch_decompile` 救不动的条目。**否定命题就数这一份**：

```sh
grep -c "CONFIRM_MSG" /home/user/mxsj-dec/rec/script/data/servicedata.py   # → 0
grep -c "SERVICE_MSG" /home/user/mxsj-dec/rec/script/data/servicedata.py   # → 3
```

这就是 2026-10-15 判定「`servicedata.CONFIRM_MSG` 在本版归档里不存在、旧客户端 `CConfirm`
一构造即报错」所用的证据形状：**同一个模块里引用者有、定义者无**。

**法 B · 布局 ⇄ 脚本关联**（不反编译，几分钟；`ui_editor` 用的就是它）

```sh
$PY tools/script_link/build_script_index.py --workers 2 --out /home/user/mxsj-dec/script_index.json
```

**法 C · 已在 git 的 681 份**：`tools/decompiler/output/{script_fls,script_fls_pycdc,data_fls}/`，
直接 `grep -rn`。注意它只覆盖「已复核入库」的那批，**不能**当全量用（见 §0 第 2 行警告）。

## 3. 建全量：完整配方

### 3.0 先核对锁定输入（不符就停，别放宽）

```sh
sha256sum data/script.fls tools/decompiler/script_fls_keys.json tools/decompiler/batch_decompile.py
# 8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72  data/script.fls
# 43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb  tools/decompiler/script_fls_keys.json
# 242543f8264e72524fea18a19887b8a46ff655511df5ff0f842a4af91965bf25  tools/decompiler/batch_decompile.py
```

同一组值也钉在 `tools/decompiler/output/script_fls_pycdc/manifest.json` 的 `inputs` 里；
`batch_decompile.py` 的 SHA 另被 `server/docs/csv_checks/agent_e_reproduction.json` 钉住——
**改它会连带让架构套件变红**，所以本配方全程不改这个文件。

### 3.1 装主引擎（⚠ 必须用这个 venv 跑，见坑 P1）

```sh
python3 -m venv /home/user/dec-venv
/home/user/dec-venv/bin/pip install -q uncompyle6==3.9.3 ruff
export PY=/home/user/dec-venv/bin/python
$PY -c "import uncompyle6" && echo "引擎就位"
```

### 3.2 建 pycdc（并让 `--engine auto` 真的用得上它）

```sh
git clone -q https://github.com/zrax/pycdc /home/user/pycdc
# 要逐字节复现已入库那 499 份，就检出钉住的 commit（manifest.engine.source_commit）：
git -C /home/user/pycdc fetch -q --depth 1 origin b4289760970dbc399684f1e155ec6d1ea1cc787e \
  && git -C /home/user/pycdc checkout -q FETCH_HEAD     # 取不到就直接用 master，并在结论里注明 commit
$PY -m pip install -q cmake                             # 缺 cmake 时才需要
cmake -S /home/user/pycdc -B /home/user/pycdc/build -DCMAKE_BUILD_TYPE=Release
cmake --build /home/user/pycdc/build -j2

# 之后有两种接法（2026-10-15 起两条都可用）：
$PY tools/decompiler/batch_decompile.py … --pycdc /home/user/pycdc/build/pycdc
#   或 export MXSJ_PYCDC=/home/user/pycdc/build/pycdc   （子进程也会继承）
# /usr/local/bin/pycdc 仍是兜底默认值，老环境照旧工作；不接也没关系，
# 工具现在会打印 [engines] uncompyle6=… pycdc=缺失 并拒绝在“选了 pycdc 却没有它”时开跑。
```

### 3.3 跑主引擎（后台 + 先看小批）

```sh
OUT=/home/user/mxsj-dec/full && mkdir -p "$OUT"
ACC=/home/user/mxsj-dec/accounting.json            # §3.4 两个下游工具都要它，这里一次生成
$PY tools/decompiler/batch_decompile.py data/script.fls "$OUT" --limit 40 --workers 2 \
    --report "$ACC"                                # 验路：应 40/40
nohup $PY tools/decompiler/batch_decompile.py data/script.fls "$OUT" --workers 2 \
    --report "$ACC" > /home/user/mxsj-dec/full.log 2>&1 &
```

- 验路那步**必须看两行**：`40/40`，以及 `[engines] uncompyle6=ok pycdc=…`。
  `pycdc=缺失` 时 `--engine auto` 只会有主引擎的结果（这是历史账面的口径）。
- 没跑完的部分用 `recover_entries.py` 补（它带梯），别指望 `batch_decompile` 兜住全部——
  它对 baseline 转译失败的条目**静默不写文件**（坑 P3）。

### 3.4 救回 + 第二引擎复核

```sh
# ① 修复梯救回：batch 没产出的那些（--entries 直接给号，或用清点 JSON 的 "missing" 键）
$PY tools/decompiler/recover_entries.py --out /home/user/mxsj-dec/recovered \
    --missing-report /home/user/mxsj-dec/accounting.json --report /home/user/mxsj-dec/recover_report.json

# ② 第二引擎复核：只往 <out>/pycdc/ 独立树写，已存在一律跳过（不会覆盖 uncompyle6 产物）
$PY tools/decompiler/crosscheck_pycdc.py --out "$OUT" \
    --accounting /home/user/mxsj-dec/accounting.json --class failed \
    --jobs 2 --timeout 25 --ladder --write --keep-pyc /home/user/mxsj-dec/pyc \
    --report /home/user/mxsj-dec/cross_failed.json
```

> **清点表现在由 §3.3 的 `--report` 直接产出**（2026-10-15）。键名就是这两个工具吃的名字：
> `crosscheck_pycdc.py --class failed` 读 `"failed"`、`recover_entries.py --missing-report` 读
> `"missing"`，另附 `inputs.sha256`（钉住跑的是哪个归档）与 `engines`（钉住当时到底有哪些引擎）。
> 临时只查几条时不必跑全量：`--entries 1954,3066,4166,4691` 优先于 `--accounting`。
> 历史账面上的 `accounting.json` 是一次性脚本产物，字段名与新版一致，可以混用。

### 3.5 验收：数字必须对上

| 检查 | 期望 |
| :--- | :--- |
| `find "$OUT" -name '*.py' 2>/dev/null \| wc -l` | 历史账面 **5,000**；2026-10-15 起每次跑完是 **5,002**（见 §4 P3：转译失败条目现在会留 `script/failed/` 标记） |
| 占位数 `grep -rl "Decompilation failed" "$OUT" --include='*.py' \| wc -l` | **547**（救回/复核后应下降） |
| 双引擎矩阵（notes §4.6） | `full 4,387` / `recovered 2` / `stub 544` / `absent 54` / 未拿到 pyc `15`，合计 5,002 |
| 仍零产物 | 历史账面 **61 条**；`1954`/`3066`/`4166`/`4691` 连转译都过不去（现在会在 `script/failed/` 留下明示标记，正文首行是 `TRANSMAP FAILED`，`uncompyle6_state()` 判为 `unknown` —— 既不算占位也不算可用源码） |
| 规模 | 约 79 MB / 2,338,388 行 |

对不上就是**跑的过程出问题**（环境缺引擎、被超时切断、目录被覆盖），不是归档变了——归档有 SHA 钉着。

## 4. 坑的现况：3 条已工程化关闭，1 条仍开放

2026-10-15 之前这三条只能靠人记住；现在 `batch_decompile.py` 会自己拦下来（`test_batch_decompile.py`
共 21 项覆盖）。下面左列是原来的现象，右列是现在的行为。

| 坑 | 原来的现象 | 现在 |
| :--- | :--- | :--- |
| **P1 解释器选错** | 用系统 `python3`（没装 uncompyle6）跑全量，5,002 条**全部**写成 52 字节占位，退出码仍是 0 | `preflight()` 探针发现引擎不可用就直接 `SystemExit`，并把该跑哪条命令写在错误信息里；确有其事要照旧行为时加 `--allow-missing-engine`（此时仍会打 `[warn]` 列出条目号） |
| **P2 pycdc 路径** | 回退只认硬编码 `/usr/local/bin/pycdc`，自建在别处 = 静默不用第二引擎 | `resolve_pycdc_bin()`：`--pycdc <路径>` → `$MXSJ_PYCDC` → `/usr/local/bin/pycdc`（兼容保留）→ `PATH`；`--engine pycdc` 而引擎不在时**拒绝开跑**；每次跑完打一行 `[engines] uncompyle6=… pycdc=…（解释器 …）` |
| **P3 静默零产出** | 转译失败只返回记录、不落文件，事后分不清「没跑到」和「解不动」；且 `--entry <文本>` 走 catalog 的 filename 列，12+ 条无名条目（含 1931）必漏 | 现在在 `script/failed/entry_XXXX_<id>.py` 留一份 `TRANSMAP FAILED` 明示标记（不与任何真实模块路径同名 ⇒ 不会覆盖已有产物），摘要打条目号；`--report` 同时给出 `missing` 列表 |
| **P4 单条超时隔离** | 个别超大字节码条目（实测 `2371 preload_mov`、`2679 wingtypeposdata`）让 uncompyle6 指数级爆炸，把 worker 堵死 | **仍开放**（notes §4.5 记着）。对策：`--workers` 大于 1、跳过这两条，或给 `decompile_pyc_bytes()` 的 uncompyle6 分支也加超时（pycdc 分支已有 30 s）。别据此判定 `script.fls` 解密失败 |

**跑之前 5 秒自检**（能同时排掉 P1/P2）：

```sh
$PY -c "import uncompyle6; print('主引擎 ok')"
$PY tools/decompiler/batch_decompile.py data/script.fls /tmp/probe --limit 2 --workers 1 | tail -2
#   期望 2/2 + 一行 [engines]；0/2 或那行写着「缺失」就别往下跑
```

## 5. 使用约定（三条，别绕过）

1. **只读与互证**：同一模块在 `script_fls/`（uncompyle6）与 `script_fls_pycdc/`（pycdc）各一份，
   两边不一致处就是引擎错解点；任一引擎的成功或失败都**不构成结论**。
2. **文件名可能已清洗**：包内自报 `co_filename` 带 `\x00`/`?`/`*` 时按分量替换成 `_`，深烂的收进
   `script/mangled/`；原始值在文件头与 `manifest.json`。**不要按路径反推原文**，也不要按
   `script_entries.jsonl` 的 `current_filename` 匹配（AGENTS §6：清点必须扫目录）。
3. **`\xNN` 转义不可逐字节还原**：141 份含被转义的非 UTF-8 字节，只作阅读参考；哪几档被转义，
   `manifest.json` 的逐档 `escaped_bytes` 标了。要回编译（STATUS §5.2 ④）必须：剥掉模块顶层那个
   `return` + **两引擎都过 `compile()`** + 输入不得取自 `script_fls_pycdc/`。

## 6. 产物放哪、能活多久，以及怎么跟用户要授权

| 位置 | 会不会随沙箱重置消失 |
| :--- | :--- |
| `tools/decompiler/output/**`（681 份 `.py`） | **不会**（已入库；2026-10-15 用户明确授权的例外） |
| 全量语料、`accounting.json`、`cross_*.json`、`/home/user/py25`、`dec-venv` | **会**（都在仓库外，快照不含） |
| 网盘包 | 不会（沙箱外的异地副本） |

2026-10-15 实证：重置后 `/home/user` 下这些全消失、本地 `.git` 还退回旧 commit；恢复顺序是
先 `git fetch` 比对（当时只有 515 份缺失、**零内容差异**）再 `git reset --hard FETCH_HEAD`，
然后重编 CPython 2.5.6 重跑构建器——出货包 SHA-256 与重置前**逐字节一致**。
**结论：值得留的东西要么进 git，要么传网盘，不要只留在仓库外目录或 `out/`。**
现存网盘副本：`MXSJ_script_fls_pycdc_recovered_20261015.zip`（id `1B588Ib1AlxycyzEXU9W4jZxiVe5xNFbd`，
内含 `pycdc/` 517 + `recovered/` 9 + `reports/` 10 份 JSON，包括那 61 条的 `residual_no_source.json`）。

**要用户授权时，把这段发出去**（成本、位置、可否走捷径，一次讲完）：

> 这个问题需要**全量**反编译语料才能答（仓库里只有已入库的 681 份）。我会照
> `docs/DECOMPILE_CORPUS.md` §3 跑：装 uncompyle6 + 编译 pycdc + 全量转译，产物写仓库外
> `/home/user/mxsj-dec/full`（约 79 MB，**不进 git**），本沙箱 2 核预计**小时级**，我后台跑分段回报。
> 也可以先试 §2 的秒级捷径（单条 + 数标识符）。要我直接开跑，还是先走捷径？

需要用户动手的只有两件：**授权跑**（占时间与磁盘），以及要长期留档时的**网盘上传授权**
（红线 §4-7：不拿未改完的候选让用户盲试；要日志/截图只索取最小且脱敏的证据）。

## 7. 本文的维护规则

- 改动 `batch_decompile.py` / `crosscheck_pycdc.py` / `recover_entries.py` 的 CLI 或默认路径后，
  **本文与 `tools/decompiler/output/script_fls_pycdc/README.md` 同轮更新**（参数名、硬编码路径、
  验收数字都可能变）。
- §4 的 P1/P2/P3 已于 2026-10-15 关闭（`preflight()` / `resolve_pycdc_bin()` / `script/failed/` 标记 +
  `--report`），对应回归在 `tools/decompiler/test_batch_decompile.py`。以后若把这些护栏放宽或删掉，
  必须同时把 §4 改回「坑」并说明为什么可以静默。**P4 仍是待办**。
- 改这三个工具的 CLI 或默认路径属于**行为变更**：`batch_decompile.py` 的 SHA 被
  `server/docs/csv_checks/agent_e_reproduction.json` 与 `batch_001/manifest.json` 双重钉住，
  必须按 `docs/STATUS.md` §3.1 的两步刷新（重生成证据 → 干跑对比只拷 `manifest.json`），
  并逐字段确认只有哈希在动。
