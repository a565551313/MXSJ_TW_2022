# N2 返修回执（新会话；任务卡 20261016-new-cohort-v1）

## 身份、基线与边界

- 实际作者 N2，新 Arena 会话固定分支 `arena/a1839872-mxsj-tw-2022`；不是旧 C。
- 开工/固定交接 HEAD：`9b0dea799768aaacbb967ffc59f45753970752be`。起始工作区干净，无待提交用户工作；先推送自己的分支，再 fetch A、merge 固定号，结果 Already up to date。克隆初始 shallow，首次祖先检查因对象未加载失败；随后 `git fetch --unshallow origin arena/61deb9e5-mxsj-tw-2022`，重查 `7d32e5340b0ab4168f725d238d767ad6232f715d` 为祖先成功。没有追浮动 HEAD 合并。
- 只改 `script_manual/annotations/login/`。根 STATUS、协调表、reviews 均由 A/N7维护，本回执供 A 摘入状态；没有自行接纳或刷新旧审核。
- 原包 script/data 与 keys 三个完整 SHA 均符合任务卡；完整摘要与工具 SHA 在 `N2_provenance.json.template`。未改游戏、注册补丁、启动器、编辑器、原包或参数；未恢复1288，未执行/导入恢复游戏模块，未请求业务 URL。
- 本轮实际恢复时间为 2026-10-15 UTC 23:54 起；任务卡中的20261016为交接轮标识，不冒充时钟日期。

## 原预审五组阻塞逐项回应

### 1. LoginOk / OnLogin全文一致性

`loginin`函数摘要、消息2分支、问答及`main`登录问答统一：

- 旧候选原行575–585：仅 `not misc.IsTWServer()` 内检查协议框；存在且未勾选才return，TW没有该门禁。
- 原行246–267：先读取并设g_User；非空、密码长度至少6、账号非纯数字校验后，设g_LoginEmail，C2SLoginIn，再设置错误回调。
- 原行657–661：OnLogin在LoginIn存在时SaveAccount；这不是LoginOk内保存，也不能证明提交就成功。
- RandomConnect只作为OneoffLogin/OneoffLogin2（原行513–559）的另一路记录，不串进普通按钮链。

E协审关于516先OnLogin再Show(False)仅只读参考；本卡没有恢复516，不据此新增确定的上游成功链或隐藏后目的地。

### 2. 实际条件而非地区猜测

ShowLogin摘要及新增两分支只按 `main.g_LangVersion == 0`：构造SERVICE_MSG2框并绑定ShowService，否则ShowService(True)；不再附会TW/HK映射。协议检查的作用域已同步到摘要相关说明、分支及问答。首页注册入口则确实有IsTWServer条件，独立保留：TW开外部URL，非TW才register.Show。

### 3. Claim来源覆盖与六题

没有用扩大无关范围方式凑证据：

| 题/结论 | 实际证据（旧三候选原行号；main为新候选原行号） |
|---|---|
| 公告失败出处 | mainpage 260–283：succeed假/缺头分隔符；不是refreshService提示 |
| 公告正文/URL/布局 | mainpage 50–86、226–256、260–283、305–329；News与Service分节读取在OnMessage(30) |
| 登录点击 | loginin 575–585、246–267、657–661；RandomConnect另列513–559 |
| 注册逻辑/布局/入口 | mainpage 111–139；register 136–166(confirm)、167–213、307–543、561–930、1208–1254、1255–1305 |
| 主循环/战斗切换 | 新main 425–544、547–582；模块回调493–516；非loginin显示段 |
| 主循环退出/快捷键 | 新main 73–130、718–798、801–837、981–1061、1118–1342 |

`main`、`mainpage`、`loginin`的注册问答均补实际首页入口和布局证据；`register`自身问答亦补入口来源。confirm是CConfirm独立确认入口，不硬串进Step序列。普通OnRegisterGame成功Step(2)，2980的OnRegister成功Register2980(1)，不再混成同链。OnRegCode的非零错误与OnRegisterGame的120要求验证码分开说明。

loginin内main问答收缩成entry4293导航，confidence=inferred且无行为断言，不再拿自身Show段证明main循环。

额外核查发现并纠正：CloseGame延迟回调才置Quit；Restart暂置AfterRestart而非立即恢复MainLoop；ExitGame的`not IsShowMainPage()`不能反转；ClearHotKey没有调用RegisterDefaultHotKey。首页Show的try/else位置、消息11先查缺项映射再到history.txt读取、服务框异常推导式照实标未知。没有改游戏来消除候选异常。

### 4. 关系方向 / kind

- register→mainpage.Show为downstream calls，引用实际拒绝/完成页调用。
- loginin读取并删除register.g_AccountInfo.ResultEmail为upstream data_flow（register提供数据），不是calls。
- loginin→mainpage.Show为downstream calls，但实际在自动登录入口；普通返回按钮去selectserver，删除“返回首页”误述。
- mainpage的register上游边补register调用者证据，不能拿首页消息处理证明外部caller。
- 新main完整候选未找到mainpage.Show/loginin.Show/register.Show调用；删除三条由职责推出来的直接显示边。Loop赋值归data_flow，不称message。

### 5. 来源保真、旧main有损稿

旧main证据全文SHA `f048f22c053bed8c6b85cf088f91f4098a6f1b9e70fe2ca10bd70c5ffa2244f5` 的dev0恢复环境/字符后处理无法复现；sNz/hXCN形态不可靠。它的具名netserver状态槽位也不能沿用于新稿。**不是改扩展名宣称解决**：本轮重建pyc与候选、验证编码处理，原位将该文件替换为新候选17段有限摘录，所有main证据行号和SHA重绑。

- 新main完整候选1579行，仅放仓库外；精确去六头正文SHA `bf5051dc501a38128b4cf33dcdd17d5e2e99f2f274838af6e672e14d9edb05dc`，与E协审记录一致。此一致只是来源交叉核对，不借用E的语义验收。
- 三份旧登录候选分别332/1305/1436行，与本轮输出精确去六头后的**全部原字节**一致（不是删任意头/去空白/归一化后相似）。继续引用原文件，无需改共用证据，其他域sources SHA不受影响。
- 四条两轮恢复全部baseline、无key修复、decompile_ok/source；两轮各精确去六头正文4/4逐字节相等。完整输出形状不等于原始源码正确；source_status仍recovered_complete_not_original，不升级native/runtime。
- `N2_provenance.json.template`逐条钉完整stored SHA（原恢复报告仅16位前缀）、entry ID/offset/长度、keys/bounds、转译pyc SHA/长度、raw u6 SHA、含时间候选SHA及去六头正文SHA；并列main摘录原行→证据行映射。

编码链：原包→read_entry→zlib→固定五段XOR/转译pyc→u6原始输出（decode_big5=False）→`decode_big5_literals`→UTF-8候选。该函数使用ast.literal_eval解析字面量（仅工具的受限字面量处理，不执行游戏模块）、严格cp950解码，异常保留转义，再转义引号/反斜线等；不使用ignore、不手猜中文字串、不统一简繁替换。本轮验证raw经该函数后与候选去六头正文4/4相等。严格解码成功仍不证明字节本来使用cp950；混合编码资源路径及受污染字串仍不可靠，不能据显示字样修原包。

恢复工具有一个需交A的发现：`decompile_isolated`把decode_big5参数先repr再用!r格式化，False会成为字符串'False'（真值），所以本轮raw审阅改为**直接**调用`bd.decompile_pyc_bytes(pyc, engine='uncompyle6', decode_big5=False)`。首次尝试在4007多出编码头的断言失败，未采纳错误回执；改用真实布尔False后4/4严格相等。没有越域修改工具，也没有掩盖失败。这个问题不改变本轮默认True恢复结果。

## 可复核命令与产物边界

外置环境 `/home/user/n2-venv`：Python3.11.2，u6=3.9.3、xdis=6.1.8、spark-parser=1.9.0、click=8.5.0；另装手册jsonschema4.25.1/PySide6 6.10.3及ruff。工具代码SHA见回执。

```sh
/home/user/n2-venv/bin/python tools/decompiler/recover_entries.py \
  --out /home/user/n2-recovery --entries 337,4293,4007,4806 \
  --decompile-timeout 30 --report /home/user/n2-recovery-report.json
# 第二轮改用新的外置目录 n2-recovery-round2 与独立 report。
```

pyc核验使用只读工具API（不import恢复游戏文件）：

```python
# 在仓库根，用同版环境；输出pyc/raw只写仓库外新目录
import sys, json, zlib, hashlib
from pathlib import Path
sys.path.insert(0, 'tools/decompiler')
import recover_entries as r
archive = Path('data/script.fls').read_bytes()
db = json.loads(Path('tools/decompiler/script_fls_keys.json').read_text())
for idx in [337, 4293, 4007, 4806]:
    eid, clen, offset, stored = r.read_entry(archive, idx)
    info = db[str(idx)]
    got = r.transpile(zlib.decompress(stored), info['keys'], info['bounds'],
                      'uncompyle6', True)
    ok, engine, raw = r.bd.decompile_pyc_bytes(
        got['pyc'], engine='uncompyle6', decode_big5=False)
    assert ok
    # sha256(stored), sha256(got['pyc']), sha256(raw.encode('utf-8'))
    # 与N2_provenance逐项核对；完整候选去头只允许splitlines(keepends=True)[6:]
    # raw经r.bd.decode_big5_literals后UTF-8字节须与该正文相等。
```

完整候选、raw、pyc、恢复报告、安装/测试日志、外置核查脚本都留仓库外；入库仅四正文、有限main摘录及三个小回执。main摘录每段保留候选字节，首行标原行号；映射不是把摘录冒充完整源码。

## 实际测试与覆盖变化

本轮实跑（含最终正文更改后的来源复核）：

1. `PYTHONPATH=script_manual/src .../python -m mxsj_manual validate --verify-evidence --require-full-inventory --repository .`：通过，5135登记/20说明/3审核通过/1排除。只是结构/full/SHA/行号闸门，不是N2语义认可。
2. `PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen .../python -m unittest discover -s script_manual/tests -v`：82项，**71通过、11 GUI跳过、0失败**。实际ImportError为缺`libGL.so.1`，安装PySide6也不能视为GUI已验。
3. `ruff check script_manual script_manual/script_manual.spec`：通过。
4. `python tools/devkit/check_windows_compat.py script_manual --strict`：124文件名/27脚本，ERROR/WARNING/INFO均0。
5. 外置机械回归：消息守卫/提交/保存、版本条件、独立RandomConnect、News节、失败回调、注册入口/confirm、main网络驱动/热键、关系kind共12项锚点检查，加17段摘录逐行原字节校验全部通过；结果在`N2_validation.json.template`。机械锚点不替代逐Claim语义审查。
6. 原包/keys完成前再核同SHA；`git diff --check`通过。

四模块函数记录数未增：mainpage10/register58/loginin61/main26，合计155。分支由30增至37：ShowLogin新增2；MainLoop/WarLoop/SwitchHotKey新增5。总量是已记录说明，不是全函数完成率；现存未覆盖辅助函数/分支继续保留。

## 剩余问题 / 接收提醒

- N7须按新JSON原字节独立审核，作者未自批；A负责状态、工具问题登记和集成，禁止把结构通过写成已接纳。
- 新main DGW分支serverid未赋值、netserver槽位不透明；网络协审所指DoDgwQuickLogin缺失/StartQuickTimer门禁与成功回调绑定问题仍待network owner/原生复核，不补写成功链。
- mainpage Show的else、消息11缺映射、loginin服务文本推导式及空账号索引是静态候选风险，不能直接断定原游戏bug。
- 没有运行游戏/恢复模块、没有业务请求、抓包、真实Qt/浏览器、Windows EXE、原生客户端或服务端联调；不宣称可用。
