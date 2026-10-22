# 2027 版式测试说明（2026-10-22）

用户重做布局后，注册脚本按新版式重写接线。本页只讲这一版怎么装、怎么看日志、
以及哪些结论已验／未验。

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

## 装法

1. 备份测试副本的 `data/script.fls`，用构建产物覆盖。
2. 可选（推荐）：把 `templates/2027/register2027_msg.dlg` 导入 `interface.fls` 的
   `login_new/register2027.dlg`。它只把「同意」的消息号 50 改成 51，其余逐字节不变；
   不导入也能跑。
3. 不用再导入旧的两个布局；旧路径的布局留着不冲突。

## 日志看什么

日志在 `photo\register_diag.txt`，关键行：

- `terms layout begin build=2027-10-22`：**第一行**，有它才说明本包的脚本已在跑。
- `terms layout ready` / `form layout ready`：两个布局都取到了。
- `check btn_fiveaccount ready=0` / `check btn_isee ready=0`：勾选框读到原生状态
  （`ready` 后是初始值）。若变成 `check ... read api missing`，说明这版客户端没有
  `IsSelected()`，脚本退回自记状态——界面不会变，但流程能走完，会把退化写进日志。
- `check anchor missing btn_xxxx`：`GetObject` 取不到该控件，布局没导入或名字不对。
- `form msgid=50` / `form msgid=51`：勾选被点。`check five=.. consent=..` 是刷新时读到的状态。
- `step=1 EXC type=...`：构造表单失败，会把异常类型与静态位置写进日志后回首頁。

## 已验 / 未验

已验（离线，CPython 2.5.6 真编译 + 桩件）：

- 13 组：条款兜底、表单锚点/掩码/tab、`AddChar` 过滤、单账号边界、
  未勾同意被拦（提示进 `txt_Wrong`）、两种点击顺序下的引擎翻转与 6~14 校验、
  共用 msg50 旧版式、五账号、完成回调守卫、异常兜底且日志无私密、缺布局回首頁、
  缺 `FONT_EDIT` 回退。
- `tools/registration` 43 项、`ruff` 0、`check_windows_compat` 0/0/0。
- 构建器：只改 337/4007，337 差 9 字节，完整 marshal 往返一致，无网络调用名残留。

未验：

- Windows 实机、真实客户端里的排版与点击手感；
- 两个勾选框是否互斥（两处 `iTeam` 都是 1；若点一个另一个被取消，把 `btn_isee`
  的 `iTeam` 改成 0）；
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
