# 2027 版式测试说明（布局 2026-10-22，脚本 build=2027-10-22d）

用户重做布局后，注册脚本按新版式重写接线。本页只讲这一版怎么装、怎么看日志、
以及哪些结论已验／未验。

> **第二轮（b）**：四框与 `txt_Wrong` 改**白字**（`16777215`，照登录页）；
> 协议页认用户自加的 `btn_back`（消息号从版式现读，撞号 1 会警告）；
> 两个勾选的 `iTeam` 必须不同（用户实测，属布局侧）。
> **第三轮（c）**：修条款每行少一个字、没有换行的问题——反编译里的
> `_[1]` 是 py2 列表推导的隐藏累加器，被误抄成了切片；原版是 `[s + '#r' ...]`。
> **第四轮（d，最新）**：PR #75 审查修复——读不到勾选状态时脚本自己翻（不再死锁）、
> 缺 `btn_isee` 时提交一律挡下（fail-closed）、harness 补回 `GetColor` 让颜色优先级真被测到。
> **2026-10-23 补记**：用户在 `.dlg` 里把两个勾选定为 50/iTeam1 与 51/iTeam2（见下
> 「定稿版式」）。脚本本来就按这两个消息号分派，**代码不变、build 仍是 d**，
> 出货包不用重打。

## 版式对照

| 项 | 旧（≤ 0.15） | 新（本版） |
| --- | --- | --- |
| 协议页 | `login/regterms.dlg` | `login_new/agreement.dlg` |
| 表单页 | `login/regform.dlg` | `login_new/register2027.dlg` |
| 帐号 / 密码 / 确认 / 邮箱 | `account` / `pwd` / `pwd2` / `email` | `edt_account` / `edt_Pwd` / `edt_Pwd_1` / `edt_email` |
| 提示 | `txt`（322×64） | `txt_Wrong`（90×20，只放短句） |
| 注册五个账号 | `chk_five`（脚本自建勾选框） | `btn_fiveaccount`（版式自带三态按钮） |
| 同意协议 | 无 | `btn_isee`（版式自带三态按钮，注册前置条件） |
| 上一步 / 提交 | msg 1 / msg 2 | msg 1 / msg 2（新版式没有「返回首頁」） |

布局原字节在 `templates/2027/`（`agreement.dlg`、`register2027.dlg`），坐标一律不动。

## 勾选框接法（这里改过一次结论）

先前据「控件类型表里没有勾选框」判 `CButton` 无勾选态——**错的**。真实脚本里
`loginin.py`（entry 4806）的 `OnMessage` 只读

```
GetObject('chk_agree').IsSelected()
GetObject('btn_Protect').IsSelected()
```

`SetSelect` 只出现在 `__init__` / `OneoffLogin` / `OneoffLogin2` 这类程序性设置里。
结论：**引擎自己翻转，脚本只读**。所以：

- 点击消息只用来刷新五账号模式的位数上限与提示，**脚本不翻**；
- 状态一律在提交时重读，客户端「消息先到」或「翻完再发」都不影响校验；
- 两个勾选在原稿里同为 msgid 50 也不影响（不需要知道点的是哪个）。

### 协议页按钮的消息号（用户 2026-10-23 实机确认）

| 控件 | iMsgID | 结果 |
| --- | --- | --- |
| `btn_dft_000`（同意） | 1 | 进注册表单 |
| `btn_dft_002`（拒絕） | 2 | 回登录首頁 |
| `btn_back`（返回） | **3** | 回登录首頁（用户实测可用） |

脚本不写死这些号：`btn_back` 的消息号从版式 `m_MsgID` 现读，且协议页的
「其余消息号」本来就回登录首頁，所以 3、4… 都能用。**唯一要避开的是 1**
（与「同意」同号会让返回键变成同意），撞号时日誌会写
`terms WARN btn_back msgid=1 conflicts with agree`。

### iTeam 必须不同（用户 2026-10-22 实机定论）

原稿里 `btn_fiveaccount` 与 `btn_isee` 的 `iTeam` **都是 1**，点不动；用户改成
不同值后正常。**iTeam 相同的按钮会被当成同一组**，所以每个勾选给各自的值
（例如 `btn_fiveaccount=1`、`btn_isee=2`；0 也是一个组号，不是「不分组」）。

### 定稿版式（用户 2026-10-23 在 `register2027.dlg` 里改的）

| 控件 | iMsgID | iTeam |
| --- | --- | --- |
| `btn_fiveaccount`（五個賬號） | **50** | **1** |
| `btn_isee`（同意） | **51** | **2** |

脚本**不读 `iTeam`**，只按 `m_MsgID` 分派（`ID_FIVE_CHECK=50` /
`ID_CONSENT_CHECK=51`）；50/50 的旧版式也认（靠 `OnButtonEnter/OnButtonLeave`
认按钮）。这组数字由 `test_check_msgids_match_delivered_layout` 钉住，
harness 第 15 节按「原生客户端 + 50/51」整条跑通：点 50 只动五个账号、
点 51 只动同意，提交走通，日志里**不应**出现 `fallback toggle` 或
`target unknown`。

对应日志（进表单页时）应为：

```
check btn_fiveaccount ready=0 via=IsSelected
check btn_isee ready=0 via=IsSelected
form checks shared_msgid=0
```

这一条是布局侧的事，脚本不碰。`templates/2027/register2027_msg.dlg` 是上一轮
的历史交付件（`iTeam` 仍 1/1，只把「同意」的消息号改成 51），**不要导入**，
留作「除消息号外与原稿逐字节一致」的证据。布局以用户本地版为准。

## 为什么布局里改颜色不管用

`edt_account` / `edt_Pwd` / `edt_Pwd_1` / `edt_email` / `txt_Wrong` 在 `.dlg` 里只是
**占位锚点**（`CBox`）。真正显示的是脚本用 `combmacro.CEDIT` / `CRICHTEXT` 在锚点上
另建的控件，字色只认**构造参数**：

```python
combmacro.CEDIT(edit_class, name, parent, color, font, linecolor=0)   # color=文字色
combmacro.CRICHTEXT(..., text, font, color)
```

所以往 `.dlg` 里加 `ICOLOR` 不会自动生效。旧脚本把 color 写成 `0`（黑）——这是
「登录页拷过来为什么变黑」的真正原因，不是控件属性丢了。

现在脚本：先读锚点的 `GetColor()`（原版 `dlgitembill1.CreateBookAmountEdit` 就这么读），
**非 0 就用版式值**；读不到或为 0 退回白字 `16777215`。也就是说今后在布局里给
锚点设颜色是能生效的，但**前提是这版客户端支持 `GetColor()`**；不支持就固定白字。

## 协议页的正文在哪里

**不在布局里，也不在本脚本里。** `agreement.dlg` 的 `loc_msg` 只是个显示区，
里面没有文字；正文来自 `script.fls` 的 **entry 1931**（自报路径
`script\data\servicedata.py`）里的 **`SERVICE_MSG`**（11,602 B，Big5，
开头是 `#cd95927夢想世界遊戲服務條款#n`；`SERVICE_MSG2` 是另一套
「線上遊戲定型化契約範本」）。`loginin.py` 登录时的服务条款弹窗也读同一个常量。

`register.py` 里的 `TERMS_FALLBACK` 只在这个模块 import 不到时才用（真机有，
所以看不到它）。

### 第三轮改掉一个真 bug：条款每行少一个字、还没有换行

原版写法（`CRegPanel1` / `CConfirm` / `CServiceMessageDialog` 三处一致）是

```python
result = [s + '#r' for s in servicedata.SERVICE_MSG.split('\n')]
```

反编译输出把它印成了 `result = [_[1] for s in ...]`——那个 `_[1]` 是 **Python 2
列表推导的隐藏累加器变量**，不是下标。2026-10-22 那版照抄成了
`[line[1:] for line in ...]`，后果是**每行第一个字符被吃掉、也没有 `#r` 换行标记**。
（0.15 之前的老版也是这么写的，你之前看到的条款就是被啃过的。）

2026-10-23 直接反汇编 entry 4007 与 4806 的 `__init__` 确认：
`LOAD_CONST '#r'` + `BINARY_ADD` + `LIST_APPEND`，就是 `s + '#r'`。
现在 `_RichLines()` 统一补 `#r`，条款页和确认框都走它（兜底文本也同样处理）。
日志第一行相应升到 **`build=2027-10-22d`**。

所以**改写正文时不用管行首**，每行原样写中文即可；`#cRRGGBB` 这类行内颜色码
仍然有效（原包首行就是 `#cd95927` 开头）。

想换正文有两条路（都还没做，需要时再说）：
1. 给构建器加 `--terms <文本文件>`，构建时替换 entry 1931 的 `SERVICE_MSG`
   （Big5 编码由工具处理）。
2. 让脚本优先读客户端目录下的一个纯文本（例如 `agreement.txt`），有就用它、
   没有才用 `servicedata`——你之后改条款只要改那个 txt，不用重打包。

## 注册页的颜色在哪里

### 先回答「改哪个属性」

真 `.dlg` 里**字色属性的名字不是 `ICOLOR`**。手头 11 个 `.dlg` 全量统计只有两种：

| 控件类型 | 颜色属性 | 值的样子 |
| --- | --- | --- |
| `CTextFrame` / `CTextFrameEx`（文字） | **`lColor`** | `[255,255,255]` / `[255,255,255,0,0,0]`（1~3 组 RGB） |
| `CButton`（按钮） | **`lNormalColor`** | `[255,255,255]` |

`ICOLOR` 不在任何一份 `.dlg` 里；引擎按属性名逐项解析，没有这个名字就等于没写。

**更关键的是**：本页的 `edt_account` / `edt_Pwd` / `edt_Pwd_1` / `edt_email` /
`txt_Wrong` 在布局里都是 **`CBox`**——这 11 个 `.dlg` 里**没有任何 CBox 带颜色属性**。
而脚本拿颜色用的是原生 `GetColor()`（证据：`dlgitembill1.CreateBookAmountEdit`
先 `GetObject('txt_num').GetColor()` 再传给 `CEDIT`；`dlgloginqueue.CheckServer`
先 `oText.GetColor()` 再当文字颜色参数）。它读的是控件自己的字色属性，CBox 上没有，
所以给 CBox 加 `ICOLOR` 读不出来——你实测无效是符合证据的，不是哪里写错了。

### 所以「只改某一个框」怎么改

`tools/registration/register.py` 的 `COLOR_TEXT_BY_ANCHOR`（第 398 行附近）：

```python
COLOR_TEXT_BY_ANCHOR = {}          # 默认全白
# 例：只把密码框变红
# COLOR_TEXT_BY_ANCHOR = {"edt_Pwd": 16711680}
# 想一起改：{"edt_Pwd": 16711680, "txt_Wrong": 16776960}
```

优先级：**这个表 > 版式 `GetColor()` > 白字 `16777215`**。
`txt_Wrong` 是富文本，也可以只在提示文字前加内联色码 `#cRRGGBB`（渲染时生效，
不用改构造参数）。

### 全部改

```python
COLOR_TEXT_WHITE = 16777215     # 0=黑，16711680=红，16776960=黄，65280=绿
```

`linecolor=0` 是输入框线色，与登录页一致；要改也在 `_CreateFormEdit` 同一行。

### 如果非要在布局里改

把那个锚点的控件类型从 `CBox` 换成 `CTextFrame` 并设 `lColor`，理论上
`GetColor()` 就会吐出版式值——**但这条路我们没有验过**（换类型会不会影响
`CCombPanel` 的锚点查找、`CEDIT` 还能不能在它上面建，都未知），不建议在正式
测试副本上试。代码里的覆盖表是可靠路径。

## 装法

1. 备份测试副本的 `data/script.fls`，用构建产物覆盖。
2. **不要再导入任何布局**：`btn_back`、`iTeam`、颜色都在用户本地布局里，本包只发脚本。
3. 旧路径的两个布局留着不冲突。

## 日志看什么

日志在 `photo\register_diag.txt`，关键行：

- `terms layout begin build=2027-10-22d`：**第一行**，有它才说明本包的脚本已在跑
  （尾碼 `d` = 审查修复轮，`c` = 条款换行，`b` = 白字 + `btn_back`）。
- `check btn_isee ready=0 via=IsSelected`：勾选框读到了（`via=` 是实际用的方法名）。
  变成 `read api missing` 时：脚本自己记状态，点一下翻一下（日誌 `fallback toggle`）。
- `consent anchor missing: submit blocked`：版式里没有 `btn_isee`，提交被挡（这是故意的）。
- `terms layout ready` / `form layout ready`：两个布局都取到了。
- `check btn_fiveaccount ready=0` / `check btn_isee ready=0`：勾选框读到原生状态
  （`ready` 后是初始值）。若变成 `check ... read api missing`，说明这版客户端没有
  `IsSelected()`，脚本退回自记状态——界面不会变，但流程能走完，会把退化写进日志。
- `check anchor missing btn_xxxx`：`GetObject` 取不到该控件，布局没导入或名字不对。
- `terms msgid=N`：协议页点了哪个消息号；`terms btn_back -> home` 是返回键生效。
- `msgid btn_back=N`：开局从版式读到的返回键消息号（没这按钮就没有这行）。
- `form msgid=50` / `form msgid=51`：勾选被点。`check five=.. consent=..` 是刷新时读到的状态。
- `color edt_account fallback white`：这版取不到版式颜色，用了白字；
  若显示的是 `color edt_account layout=16777215`，说明颜色是从布局里读到的。
- `step=1 EXC type=...`：构造表单失败，会把异常类型与静态位置写进日志后回首頁。

## 已验 / 未验

已验（离线，CPython 2.5.6 真编译 + 桩件）：

- 13 组：条款兜底、表单锚点/掩码/tab、`AddChar` 过滤、单账号边界、
  未勾同意被拦（提示进 `txt_Wrong`）、两种点击顺序下的引擎翻转与 6~14 校验、
  共用 msg50 旧版式、五账号、完成回调守卫、异常兜底且日志无私密、缺布局回首頁、
  缺 `FONT_EDIT` 回退。
- `tools/registration` 43 项、`ruff` 0、`check_windows_compat` 0/0/0。
- 构建器：只改 337/4007，337 差 9 字节，完整 marshal 往返一致，无网络调用名残留。

第二轮新增的离线验证：白字（四框 + 提示行都由构造参数给出）、版式给色时优先采用、
缺 `GetColor()` 时退回白字、`btn_back` 回主頁 + 撞号警告，三套模式（默认 /
`missing_layout` / `no_font_edit`）全过；`tools/registration` 45 项、ruff 0。

未验：

- Windows 实机、真实客户端里的排版与点击手感；
- 这版客户端到底有没有 `GetColor()`（没有就固定白字，页照样开）；
- `iTeam` 的语义只按用户实测记「必须不同」，没有逆向出分组规则；
- 退化客户端（没有 `IsSelected`）到底会不会由引擎翻转：不知道，所以那条路上脚本
  自己翻并写 `fallback toggle`；真机没遇到过这种客户端（登录页本身就在读
  `chk_agree.IsSelected()`，读不到登录也走不通）；
- 两个勾选共用消息号 50 时靠 `OnButtonEnter/OnButtonLeave` 认按钮——这依赖引擎
  在鼠标移到按钮上时回调（`loginin.py`/`mainpage.py` 有同名方法，但「按下时一定
  先经过 enter」没实测）；认不出时默认当成「五個賬號」，宁可不翻同意；
- 真实注册服务（仍是桩，提交只弹「伺服器尚未開放註冊，請稍後再試」）。

## 怎么重跑

```sh
# 编译（需 CPython 2.5.6）
python tools/registration/compile_with_py25.py tools/registration/register.py /tmp/register.pyc
# 桩件回归（15 组；另两种模式：MXSJ_HARNESS_MODE=missing_layout / no_font_edit）
python tools/registration/harness.py2 /tmp/register.pyc
# 布局/路径回归
python3 -m unittest discover -s tools/registration/tests
# 全量构建（改 337/4007）
python3 tools/registration/build_native_registration.py --python25 <py2.5.6> \
    --output /tmp/build/script.fls --report /tmp/build/build_report.json
```

> **别在仓库目录里跑 harness 等它留下日志。** `register.py` 的 `_Diag()` 写的是
> Windows 路径 `photo\register_diag.txt`；POSIX 上反斜杠是普通字符，就地跑会生成一个
> **文件名带反斜杠**的文件。harness 现在会先 `chdir` 到 `out/harness/`
> （可用 `MXSJ_HARNESS_WORKDIR` 改），所以日志落在
> `tools/registration/out/harness/photo\register_diag.txt`，`out/` 已在 `.gitignore` 里。
> 2026-10-23 就是这件事漏了一次：那个文件被提交进仓库，Windows 上 `git pull` 直接
> 中止——`error: invalid_path 'tools/registration/photo\register_diag.txt'`。
> `tests/test_repo_paths.py` 现在会拦住任何 Windows 非法路径。
> **`register.py` 里那行路径不能改**：客户端是 Windows 程序，改了会让 `co_lnotab`
> 变、出货包哈希变；治的是「怎么跑测试」，不是「代码里怎么写」。
