# 2027 版式测试说明（2026-10-22，第二轮 2026-10-22 晚 / build=2027-10-22b）

用户重做布局后，注册脚本按新版式重写接线。本页只讲这一版怎么装、怎么看日志、
以及哪些结论已验／未验。

> **第二轮（build=2027-10-22b）修三件事，全部只改脚本、不动布局**：
> 1. 四框与 `txt_Wrong` 改**白字**（`16777215`，照登录页 `edt_Name`/`edt_Pwd`）；
>    原来传的是 `0`＝黑。详见下节「为什么布局里改颜色不管用」。
> 2. 协议页新增**用户自加的 `btn_back`**：消息号从版式现读（`m_MsgID`），
>    点击回登录首頁；若被填成 1（与「我同意」同号）会在日志里留警告。
> 3. `iTeam`：用户实机确认**两个勾选必须不同值**才能点动（原稿都是 1）。

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

### iTeam 必须不同（用户 2026-10-22 实机定论）

原稿里 `btn_fiveaccount` 与 `btn_isee` 的 `iTeam` **都是 1**，点不动；用户改成
不同值后正常。**iTeam 相同的按钮会被当成同一组**，所以每个勾选给各自的值
（例如 `btn_fiveaccount=1`、`btn_isee=2`；0 也是一个组号，不是「不分组」）。

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

## 装法

1. 备份测试副本的 `data/script.fls`，用构建产物覆盖。
2. **不要再导入任何布局**：`btn_back`、`iTeam`、颜色都在用户本地布局里，本包只发脚本。
3. 旧路径的两个布局留着不冲突。

## 日志看什么

日志在 `photo\register_diag.txt`，关键行：

- `terms layout begin build=2027-10-22b`：**第一行**，有它才说明本包的脚本已在跑
  （尾碼 `b` = 白字 + `btn_back` 这一轮）。
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
- 真实注册服务（仍是桩，提交只弹「伺服器尚未開放註冊，請稍後再試」）。

## 怎么重跑

```sh
# 编译（需 CPython 2.5.6）
python tools/registration/compile_with_py25.py tools/registration/register.py /tmp/register.pyc
# 桩件回归（13 组；另两种模式：MXSJ_HARNESS_MODE=missing_layout / no_font_edit）
python tools/registration/harness.py2 /tmp/register.pyc
# 布局回归
python3 -m unittest discover -s tools/registration/tests
# 全量构建（改 337/4007）
python3 tools/registration/build_native_registration.py --python25 <py2.5.6> \
    --output /tmp/build/script.fls --report /tmp/build/build_report.json
```
