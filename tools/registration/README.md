# 注册原生重做：第二期（现行风格 + 注册五个账号）

> **2026-10-15 合并取舍（最新用户确认）**：PR #32 的 `mxLauncher.exe` 相关方案与注册 `script.fls` 修改以对方版本为准；用户已确认注册脚本测试没有问题。独立 `script_editor/` 以本分支 0.5.1.dev1 为准，不以旧历史记录回退。下文旧测试状态和交付说明保留为历史，不覆盖本次确认。此前启动器生成工具的路径/写入边界审查问题仍单独记录，不能当作已修复。

## 当前做到哪里

第一期 1.1 的入口、条款、表单校验、桩提示、返回流程已由用户实机确认。
第二期改用现行风格并加五账号勾选：**用户已报告申请会员时整窗无响应，未通过原生验收**。
用户确认脚本来自原第二期 ZIP、两张新布局可在同一个包找到。
已补 phase2-diag1 入口分段日志与 Python 异常尽力回退，见
[诊断测试步骤](DIAGNOSTIC_TESTING.md)。只换测试副本 script，不重新导入布局；
用户现反馈 diag1 不再冻窗，但 terms layout 构造抛 Exception 并恢复首页。
已发现明文入包不符合真实 LoadFile 路径 XOR。用户指出一次性助手不解决
后续新增/持续改布局，现转为资源0.4.3/UI0.8.3原生写入永久修正。
按 [编辑器正常流程](EDITORS_NATIVE_LAYOUT_WORKFLOW.md) 操作，不用助手/模板覆盖。
原生跳转仍待实际游戏验证；23项注册回归只作历史证据，不是编辑器新版本验收。
这不是已接通的注册服务；服务端仍无注册接口，不会创建真实账号。

## 最新修复：phase2-font1（2026-10-15）

diag2实机精确报缺失`FONT_EDIT`，锚点/工厂已ready。此为脚本引用旧别名错误，
不是用户控件名/协议接线。已按原entry4007的CEDIT调用核对FontLT14_3，四框和
提示区明确使用该原生字体；提示区黑色0，不再依赖旧COLOR_EDIT别名，不注入假属性。
默认测试桩删除FONT_EDIT/COLOR_EDIT，旧源同探针先失败，新源通过（32项真2.5.6）。
细节与只换script、不重导布局的步骤见 [字体修复测试](FONT_FIX_TESTING.md)。

打包新代码时仍硬性验证原生marshal逐字匹配混淆输入及全零padding，再严格反变换
co_code后完整marshal逐字匹配编译结果。新增authored_marshal只用于已知自写新代码，
原条目的修复转译器/五段XOR/key DB不改；不得让旧边界猜测误改新co_code。
此次不声称Windows全部交互已过；原生表单显示/控件仍需实测。

## 2026-10-15 当前实机断点：账号输入框 AttributeError

用户已用新版编辑器保存，确认协议页可进入、同意消息为1；日志已走到
`form layout ready` / `form account begin` 后 `step=1 EXC type=AttributeError`。
用户进一步确认实际表单占位 `sName=account`、`sWidgetType=CBox`，不再要求
改正确名字、重导布局或怀疑同意接线。

phase2-diag2 是**定位版，不是声称修好版**：保持原生CEDIT接口和全部用户布局，
拆分运行时anchor、工厂解析、FONT_EDIT解析、工厂调用、SetLimit标记。
异常只补静态代码位置/PC及受co_names白名单约束的缺失属性名，不记录对象repr、
完整异常文字、帐号/密码/邮箱或局部变量。构造失败仍保留协议页。
详见 [诊断步骤](DIAGNOSTIC_TESTING.md) 顶部最新章节。
原CEDIT→CreateEdit别名、七形参/九参数子类构造、原CEdit.SetLimit已逐code object
只读核对；不执行恢复游戏模块。离线桩也改用九参数构造，不再假装cls(name)即原生。
本轮26项通过（真CPython2.5.6），仍不能凭AttributeError类型确定实际缺失属性。

## 用户定的行为

- 协议页：`login/service.dlg` 逐字拷贝为 `login/regterms.dlg`，
  脚本按 `loginin.CServiceMessageDialog` 的 `loc_msg`/COutput 写法显示条款。
- 表单：照原生改密页 `chgpwd.dlg` 派生 `login/regform.dlg`。
  四框为帐号、密码、确认密码、邮箱；三个按钮为上一步、確認註冊、返回首頁。
- 邮箱下方加原生勾选框「註冊五個帳號」，默认**不勾选**，方框和文字都可点。
- 不勾选：一个帐号，帐号和密码均为 6～16 位 ASCII 字母/数字。
- 勾选：基础帐号为 **6～14 位**（用户已选定），生成恰好五个：
  `account`、`account_1`、`account_2`、`account_3`、`account_4`。
  第一项不加后缀、没有 `_0`；后四项加后缀后最长仍为 16 位。
- 五份注册资料共用同一密码和邮箱，密码仍为 6～16 位字母/数字。
  下划线只用于自动后缀，基础帐号输入框仍不接受下划线。
- 邮箱沿原校验口径：5～50 位，`^[_.\-a-z0-9A-Z]+@[_.\-a-z0-9A-Z]+$`；
  输入框限制同步为 50。不是完整 RFC 邮件地址校验。
- 切换勾选后，长度限制和提示同步改变。已经填了 15～16 位再勾选，
  原输入不截断；提交会要求缩短基础帐号，不会偷偷改名。

### 当前测试包的提交提示（不是成功提示）

单帐号仍弹「伺服器尚未開放註冊，請稍後再試」。五帐号在这句之后列出
五个**待注册**名称，并明确标「尚未註冊」。不发网络请求、不报注册成功，
提示和日志都不显示密码。

### 完成弹窗已预留，真实注册仍待服务端

`CRegFormPanel.OnRegistrationComplete(registered_accounts)` 是预留回调。
只有真实请求送出后由传输层设置 `m_PendingAccounts`、服务端确认完整成功集合，
才显示「註冊完成！以下5個帳號已建立」并逐行列出五个帐号。

当前桩路径不设置 pending、不调用此回调，因此本包绝不假报成功。
部分成功、重复名称、错误名单、未提交/过期回覆、旧表单回覆均不能报全成功。
离线回归对成功回调使用的是**模拟回覆**，不是服务端联调证据。
将来接通时仍需实现：真实注册接口、批次/事务、同邮箱五帐号规则、下划线
后缀支持、重名及部分失败处理；不能覆盖已有帐号或擅自改变编号。

## 批量发送与重名：已定后续规则（接口仍未实现）

2026-10-14 用户选定「一条发送＋重名顺延」。当前实际代码仍只在内存
准备固定候选；没有网络请求、数据库查重或真实顺延实现。

服务端接通时按以下规则做：

1. 客户端提交一条批量业务请求：基础帐号、注册数量 1/5、共用密码/邮箱、
   本批编号。不是连续五次单帐号请求，也不是仅靠一个勾选标记猜名单。
2. 五帐号模式由服务器按原帐号、`_1`、`_2`……递增，跳过已经注册的名称，
   不覆盖旧帐号。比如原帐号和 `_1` 已被占用，实际可返回 `_2`～`_6`。
3. 最多尝试到 `_99`，且每个最终帐号仍不得超过 16 位；14 位基础帐号
   只能尝试原名及 `_1`～`_9`，`_10` 已超长；13 位及更短才可到 `_99`。
4. 找齐五个可用名称才整批创建；找不齐则整批不创建、提示换基础帐号。
   查重和创建必须遵守服务器唯一性/事务约束，不能客户端先查再发五次。
5. 服务器成功回覆实际创建的五个帐号；弹窗和登录预填均用实际结果，
   不继续使用客户端示意候选。所有五个共用同一密码和邮箱。
6. 同一批编号重试返回该批原结果，不能因为断网/双击额外再创建五个。
   服务端需要校验批次与请求资料的一致性；本规则没有实现成运行代码。
7. 不勾选时仍只注册一个；单帐号重名不擅自顺延改名。

还要做：当前 `OnRegistrationComplete` 校验固定 pending 名单，接通顺延接口前
必须调整为核验批次、实际成功数量及合法的服务端分配名单，并覆盖重名、范围
耗尽、并发冲突和重试测试。现有离线成功模拟不是这些服务端行为的验收证据。
这定义的是业务规则，不是已经确定的原生封包格式；协议号、编码与传输接线
仍要在真实注册接口阶段核实，不在本轮偷偷实现或连网。

## 原生依据与编码纪律

- 游戏模块 `register.py` 是自写源码，不执行反编译稿；用 CPython **2.5.6** 编译。
  `Show`/`Step`/`ShowConfirmDlg`/`CConfirm`/`g_AccountInfo` 等对外接口保留。
- 编辑框使用原生 `combmacro.CEDIT` + `SetLimit`/`m_IsPassword`/`SetNextEdit`，
  提示区使用 `CRICHTEXT`；输入子类的 `AddChar` 过滤非法字符。
- 勾选用原生工厂（签名已按原 code object 反汇编核对）：
  `CIMGCHECKBOX(box_class, objname, parent, filename, manual, msgid)`，
  绑定布局的 `chk_five`，`box_class=interface.CImageCheckBox`，消息号 4。
- `CImageCheckBox.LeftUp` **先发消息，再自动翻转**；所以设 `manual=True`，
  注册页收到 4 时只翻转一次，防止一次点击刚勾上又取消。
- 皮肤使用原生资源 `combdialog/登录注册/按钮/勾选框.igs`（GBK 路径，
  原 `data/ui_res_style1.py` 含此字节常量）；没有自造图片、包外图或烤字按钮。
  真实包是否有该皮肤以及显示/点击效果仍需 Windows 实机验。
- 已核对原 `CEdit.SetLimit` 只写 `m_Limit`，`GetText` 不按限长截取已有资料。
- 所有 UI 出口文案为 **Big5 字节串**。1.0 曾传 unicode 导致原生弹框
  静默失败，1.1 已实机证实修复；不可现代化成 Unicode/f-string。
- `.dlg` 的显示文字为 Big5、资源路径为 GBK，不能整份重编码。
  生成器只转义控制字节/引号/反斜杠，原字节往返与编辑器解码文案均有测试。
- `photo\register_diag.txt` 只记流程、数量、控件尺寸、异常类型，不记录帐号、密码或邮箱。
  phase2-diag1 从模块导入、InputSecrecy 开始到布局/条款/表单逐段前后关文件写日志；
  photo 路径不可写时尝试工作目录 `register_diag.txt`。同步原生阻塞不能靠 except 取消。

## 源码与模板

`templates/` 的五个文件来自用户导出，回归钉住 SHA-256 防止损坏/乱码母版：

| 文件 | 来源 | SHA-256 |
|---|---|---|
| chgpwd.dlg | reg.zip | b20859a172a51cfecc3059f86618d8a28a40d84fbf99c343c11ac1a3d7408c7e |
| confirm.dlg | reg.zip | b53ac5347d413d76cdb7e4b0a58b5cc413826fda956425ba490ef965d3c2130c |
| reg1.dlg | reg.zip，仅历史参考 | 244a6507decb4e300b0e02fe5d46f1beb6bd1450a3c2da55239f90009fe1c1da |
| reg2.dlg | reg.zip，旧风格作废 | 64be77d148f853a99ba5f47c9e6d722012a4e77462c66263df1ee93b08ef043a |
| service.dlg | Drive `1KaFXbFxU-VOJ5OJ0UIS7rINmn9uhJagS` | 820f09a8cd4e8ff80494cffdfc6de042550f897f7747c6345de793fa68b46d26 |

条款文本取 `servicedata.SERVICE_MSG`；该模块在本版 `script.fls` 内（见下方勘误），
所以**真机走的是正式条款全文**，只有离线桩件环境（harness 不装该模块时）才退回
`TERMS_FALLBACK` 明示占位。`CConfirm` 需要的 `servicedata.CONFIRM_MSG` 经实测
**归档里不存在**，因此本包不再照抄旧客户端那句裸取属性，改走 `_LoadConfirmLines()`：
包内一旦补上该常量就自动改用原文，否则用 `CONFIRM_FALLBACK` 明示兜底文案。

> **[勘误 2026-10-15]** 本 README 曾记「`servicedata` 不在本版 script.fls 中」，现已推翻：
> 该模块在包内，条目 `1931` 的自报路径为 `script\data\servicedata.py`，且已完整反编译
> （`SERVICE_MSG` 11,602 B 正式条款全文、`SERVICE_MSG2` 9,055 B「線上遊戲定型化契約範本」，
> 另有 `main.g_LangVersion != 0` 分支的 AMS 版）。真客户端 `script/login/register.py`、
> `loginin.py` 本来就以裸名 `import servicedata` 取用，故**运行期并非缺失**；
> 之前的误判来自 catalog 索引对无名字条目检索不到。
> 2026-10-15 已据此重建 `out/script.fls`（`sha256=ed0f4126c0b5d3533b157cd1b8002b9d570f3c1e152c61f7c60dcd48de5a5a5f`，
> 24,262,648 B）并跑完本目录 13 项回归（11 布局 + 2 运行时，全通过）。
>
> **[同轮新增] `CONFIRM_MSG` 是旧包自带的死路**：`servicedata` 的 pyc 名字表只有
> `SERVICE_MSG`/`SERVICE_MSG2`，两归档共 4,941 个可读模块里**没有任何一个定义**
> `CONFIRM_MSG`，唯一引用者就是 `script/login/register.py:142` 且没有 try。
> 原 harness 的 `servicedata` 桩件恰好提供了这个常量，所以历次「CConfirm 流程走通」
> 覆盖的是桩件世界、不是真归档。现 harness 增加 9a 段（忠实本版：有 `SERVICE_MSG`、
> 无 `CONFIRM_MSG` → 条款取真文本、确认框落兜底、构造不抛，并按字节核对）与 9b 对照组
> （补上常量后必须自动改用原文），`test_runtime.py` 断言 9a 的输出行。

## 构建与回归（仓库侧，不要求用户安装解释器）

```sh
# 参数可换成仓库外的持久目录；/tmp 会随沙箱重建而丢失。
sh tools/registration/build_python25.sh /home/user/py25build
python3 tools/registration/build_regform_dlg.py
python3 tools/registration/build_native_registration.py \
    --python25 /home/user/py25build/cpython-2.5.6/python
# 打成出货包（生成 SHA256SUMS + 回显 zip 的 SHA-256/MD5，并自检一遍）
python3 tools/registration/make_release.py --stage <备好的目录> --zip <输出.zip>
python3 tools/registration/make_release.py --check <输出.zip>
MXSJ_PYTHON25=/home/user/py25build/cpython-2.5.6/python \
    python3 -m unittest discover -s tools/registration/tests -v
ruff check tools/registration
python3 tools/devkit/check_windows_compat.py tools/registration
```

构建器只读原包，拒绝输入/输出同名或硬链接别名；新包默认在 `out/`（Git 忽略）。
只改条目 337（首页入口 9 字节窗口）及 4007（整个注册模块），其余 5000 条
**压缩负载逐字节不变**；条目数、身份与顺序保持原样。
新注册模块解密/转译后完整 marshal 与编译前逐字节相等，再直接对从新包
读回的模块运行真 2.5.6 离线冒烟，任何失败都不得交付。

本目录含嵌入式游戏源码和仓库侧离线构建器，不是新增的桌面编辑器/EXE 产品。
Python 3 构建器/测试按仓库 ruff 规则检查；两份必须在 2.5.6 运行的 `.py`
只豁免 `UP` 现代化规则（`.format`、f-string 和删除 coding 声明会破坏原解释器）。
`harness.py2` 由真 2.5.6 执行，不能以 Python 3 能否解析它判断游戏兼容性。

### 换基线重做（客户机现行的 script.fls ≠ 仓库 `data/script.fls`）

默认基线钉死在 `data/script.fls`（`BASE_SHA256 = 8b6e9266…`）。要拿用户在跑的
那份归档重做，必须显式给两条参数，缺一不可：

```sh
python3 tools/registration/build_native_registration.py \
    --archive google_drive/script1015.fls \
    --base-sha256 77b3eac611f52cf8ac750fe1adf57d672e3f3e85f51fa5f9c81980e1d6564466 \
    --python25 /home/user/py25build/cpython-2.5.6/python \
    --report out/build_report.json
```

- SHA 不符就退出，同时把**实测 SHA 和可直接复制的 `--base-sha256` 参数**打出来；
  不做「差不多就放行」。
- 337 是幂等敏感的：补丁窗口已是 patched 形态（基线本身就是上一版工具产物）→
  打 `[note] … 原樣保留`，实际改动变成 `[4007]`；窗口既非未补形态也非已补形态 →
  `ValueError: TW predicate fingerprint mismatch`，拒绝盲目重打包。三态判定与
  两条分支各有单测（`tests/test_build_base.py`，7 项，0.2 秒内跑完）。
- 4007 是整模块替换，天然覆盖旧内容，与基线新旧无关。
- `--report` 只在验证全通过后落盘：记基线/密钥表/源码/产物四者 SHA、条目数、
  337 处理方式与实际改动条目，可直接粘进出货登记。

2026-10-15 实测：网盘 `script1015.fls`（24,264,943 B，SHA-256 `77b3eac6…`，
MD5 `f85917c2…`）与仓库基线逐条比对——**5,002 条里只有 337、4007 两条不同**，
其余 5,000 条压缩负载逐字节相同。337 与我们的 9 字节补丁逐字节一致；4007 是
A 案**之前**的旧 register（`CConfirm` 仍裸取 `servicedata.CONFIRM_MSG`，即那条
AttributeError 死路，并多带 `_DiagFailure`/`_ImportRuntime`/`_RecoverEntry`/
`_CreateFormEdit` 调试脚手架）。以它为基线重建，产物 SHA-256 仍是 `ed0f4126…`
（与已出货那颗逐字节相同）——即这份网盘归档不含任何我们无法复现的内容。

## 原第二期测试包（2026-10-14 已授权上传，现为卡屏排查基线）

- 源码提交：`22a3fab`，已推送当前会话分支，未合入 master。
- [下载 registration_phase2.zip](https://drive.google.com/file/d/1FQjI8tiFSYAihlHUzwJN2GNNZWy5CBy7/view)（Google Drive，未改分享权限）。
- 大小：24,189,000 字节；ZIP MD5：`56c583afa4fa58b7fa8f47efb5a802c3`。
- ZIP SHA-256：`0541062f45a74bfbda99b62022d30c3929feb0e0979069d36b06d513d3cec97b`。
- 此链接是已报告卡屏的原包，**不是 phase2-diag1**，勿重下它当修复版。
- 包内有新 script.fls、两张新布局、测试说明、SHA256SUMS。
  本包只测界面/校验/候选资料，不发送真实注册请求；顺延规则还只是已定方案。

### 第二期 b 测试包（2026-10-15 已授权上传）

- 源码提交：`421ab91`（会话分支 `arena/19a59906-mxsj-tw-2022`，未合入 `master`）。
- [下载 registration_phase2b_terms_confirm.zip](https://drive.google.com/file/d/1k5dE9pt9NQL-ywhh27U_lM6JfcAEQD7b/view)（Google Drive，未改分享权限）。
- 大小 24,190,980 字节；ZIP MD5 `e5177426ce0982e85fee6feae0f02655`；
  ZIP SHA-256 `c30a638719497d4850057c3717f303e9ef48e1c502f6b5f871579d179773d3f0`。
- 内容：`data/script.fls`（`ed0f4126c0b5d353…`，24,262,648 B）、
  `interface_import/login/regterms.dlg` 与 `regform.dlg`（与 phase2 **逐字节相同**，
  已导入过且没动过的话可跳过 TESTING 第 1 节）、`测试说明-TESTING.md`、`README.txt`、
  `SHA256SUMS.txt`。
- 与 phase2 的唯一差异是 `data/script.fls`：条款页改读包内真文本（勘误「模块缺失」误判）、
  `CConfirm` 改走 `_LoadConfirmLines()` 明示兜底（本版归档无 `CONFIRM_MSG` 定义）。
- **可复现性**：沙箱在 2026-10-15 重置，`out/` 属 Git 忽略项随之外消失；按上文「构建与回归」
  命令重建后 `script.fls` 的 SHA-256 与重置前逐字节一致 ⇒ 构建是确定性的。
  结论：**要留档的出货包必须传网盘或入库，不能只靠 `out/`**。

### 第二期 b · 以 `script1015.fls`（用户网盘）为基线重做（2026-10-15 已授权上传）

- 源码提交：`744c5e2`（会话分支 `arena/19a59906-mxsj-tw-2022`，未合入 `master`）。
- [下载 registration_phase2b_on_script1015base.zip](https://drive.google.com/file/d/1KDEq1eiF_RJMM4l7pDvorScuMAIo_Ojo/view)
  （Google Drive，未改分享权限）。
- 大小 24,190,255 字节；ZIP MD5 `f3bdaf9a6c678385618298b2e8e7833d`；
  ZIP SHA-256 `437fd798540553f293dfef773c168a7900325b5fe80487656225edc7f19bfbc2`
  （上传后已核对 Drive 侧 MD5 与本地一致）。
- 基线换成 `script1015.fls`（24,264,943 B，SHA-256 `77b3eac6…`）：实测只改 4007，
  337 因基线已含同一补丁而「原样保留」；产物 `data/script.fls` 仍是
  `ed0f4126c0b5d353…`，**与上一包逐字节相同** ⇒ 已经在测 phase2b 的人不用换包。
- 比 phase2b 多一个 `build_report.json`（基线/密钥表/源码/产物四者 SHA、`mainpage.state`、
  `changed_entries`），换基线出货时拿它对账；成员其余同 phase2b。
- 那份归档里的旧 `register`（4007）比我们的版本多 `_DiagFailure`/`_ImportRuntime`/
  `_RecoverEntry`/`_CreateFormEdit` 与分步 diag，但 `CConfirm` 仍是会 `AttributeError`
  的死路。用户已选定：不保留这套脚手架，直接以当前 A 案版本覆盖。

> **打包坑（已由 `make_release.py` 堵上）**：`find | xargs sha256sum > SHA256SUMS.txt`
> 会先把目标文件建成**空文件**再被 `find` 收进去，于是清单里多一行「空文件的哈希」
> 自称是 `SHA256SUMS.txt` 本身——这行永远校验不过。本轮之前手工打的包（含
> `registration_phase2b_on_script1015base.zip`）就带这一行；除它以外全部有效，
> 拿不准就只核 `data/script.fls` 那一行。`make_release.py` 生成时排除自身，
> `--check` 会拒绝含自指行的清单。

### 2026-10-15 实机回归：协议页点「我同意」进不去表单页（已修）

现象：装 `ed0f4126…` 那颗包后，条款页能开，点「我同意」毫无反应。

排查（不猜，逐条比字节）：把用户网盘那份 `script1015.fls` 里能进到表单页的 4007
模块解出来反汇编，与我们出货的 4007 逐函数对比。结论是**两条**：

1. 表单单框的字体常量不同。旧版（实机走通过）用 `interface.FontLT14_3`；
   我这版照 `chgpwd.py` 用了 `interface.FONT_EDIT`，提示框颜色同理用 `COLOR_EDIT`。
   这两个名字的存在性只有「归档里别的模块用了」这一条间接证据——**离线桩件
   恰好定义了它们**（`harness.py2` 里 `FONT_EDIT=1`），所以桩件世界永远测不出来。
2. 旧版在 `Show`/`Step` 外面套了 try/except + `_DiagFailure` + `_RecoverEntry`，
   每个环节写 `_Diag` 标记；我做「清理调试脚手架」时把这套一起删了 ⇒
   客户端吞异常后就变成「点了没反应」，日志里也什么都没有。

修法（不是简单回退）：

- `_EditFont()` / `_HintColor()`：仍优先照原版 `chgpwd.py` 的 `interface.FONT_EDIT`
  /`COLOR_EDIT`，取不到就退回实机验证过的 `FontLT14_3` / `0`，并把选了哪个写进日志
  ⇒ 常量存在与否都不会再把界面打死，同时还能告诉我们本版客户端到底有没有。
- `_CreateFormEdit()`：按 chgpwd 的 `CEDIT` 调用建框，但先 `parent.GetObject(名字)`，
  查不到就写 `anchor missing` 再抛 ⇒ 「.dlg 没导入/路径填错」这种最常见的现场错误
  从此有明确名字（`regform.dlg` 里确有 account/pwd/pwd2/email/txt/chk_five 六个锚点，
  已核对，加这个检查不会误伤正常路径）。
- `Step()`/`Show()`：异常一律接住 ⇒ 记 `_DiagFailure`（只记类型名，绝不记异常值）
  + `_RecoverEntry()`（解除输入遮蔽、回首页）+ 弹 `MSG_UNKNOWN_ERR`。
  规则写死在这里：**绝不允许出现「点了什么都没发生」**。
- 构建器加守卫：`_CreateFormEdit`/`_DiagFailure`/`_RecoverEntry` 三个函数名一旦从
  模块里消失，`build_native_registration.py` 直接拒绝出货（防的就是这次这种「清理」）。
- `harness.py2` 新增两个残酷世界（`MXSJ_HARNESS_MODE=no_font_edit|missing_layout`），
  `test_runtime.py` 各跑一次断言：缺常量必须照常开页、缺版式必须「有弹框 + 回首项 +
  日志点名」，两种情况都不许把异常漏给客户端。

产物：`script.fls` 24,264,817 B，SHA-256 `f0253c9536d95e0a…`（4007 负载仍是 44,362 B
定长，编译后 pyc 20,748 B，无需缩 `co_lnotab`）。

## 原第二期 Windows 验收步骤（下列明文导入方式已被存储修复说明取代）

只在**游戏测试副本**操作，备份旧 `script.fls` 和 `interface.fls`，勿改原安装包。
测试包包含 `data/script.fls`、`interface_import/login/` 下两份新布局及测试说明。

1. 资源编辑器打开测试副本的 `interface.fls`，分别按路径导入：
   `regterms.dlg` 填完整路径 **`login/regterms.dlg`**；
   `regform.dlg` 填完整路径 **`login/regform.dlg`**，不能只填文件名。
2. 保存成新的 `interface_patched.fls`，确认写后逐条校验通过。
   将这个新包复制到测试副本并命名 `data/interface.fls`（旧包先备份）。
3. 将测试包的 `data/script.fls` 复制到测试副本对应位置，启动游戏点「申請會員」。
4. 验协议页/四框/三按钮/Tab/密码遮挡；勾选方框和文字应都可切换且只切换一次。
5. 用假资料 `account` / `Preview42` / `preview@example.invalid`：
   不勾只提示尚未开放；勾上列出 account、account_1～account_4 并注明尚未注册。
   先填 15～16 位再勾，提交应提醒缩短而不是截断原输入。
6. 若打不开/点了没反应，只回传失败步骤及脱敏的诊断/截图，不要发送真实密码。

**更正**：明文 `.dlg` 新增不符合真实原生路径 XOR，不能继续按原导入流程验收。
已导入用户应按存储修复说明操作测试副本；首次新导入也必须使用对应路径密文，
不能拿编辑器能显示当作引擎解密通过。详 `notes/native_dlg_path_cipher.md`。
真实五帐号创建与真实成功回覆不在本阶段 Windows 验收范围内。
提交推送、Drive 上传仍需用户逐轮明确授权；没有授权不得发布。
