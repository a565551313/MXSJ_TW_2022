# 注册第二期测试说明（现行风格 + 注册五个账号）

> **2026-10-22 换版式（当前）**：用户重新设计了两个布局，进包路径改为
> **`login_new/agreement.dlg`** 与 **`login_new/register2027.dlg`**，控件名也随之全换
> （`edt_account`/`edt_Pwd`/`edt_Pwd_1`/`edt_email`、`txt_Wrong`、`btn_fiveaccount`、
> `btn_isee`、`btn_Back`、`btn_register`）。勾选框改成版式自带三态按钮，走原生
> `.dlg` 接口 `IsSelected()/SetSelect()`，**引擎自己翻转、脚本只读**。
> 下文凡是 `login/regterms.dlg`、`login/regform.dlg`、`account/pwd/pwd2/email/txt/chk_five`
> 的写法都是 2026-10-22 之前的版式，仅作历史保留；实机测试请按
> [2027 版式测试说明](TESTING_2027.md)。

> **状态更新**：原第二期包已被报告申请会员导致窗口无响应。若你已导入两张布局，
> 不要再按下面步骤重导；当前 phase2-diag1 只换脚本，按
> [入口卡屏诊断步骤](DIAGNOSTIC_TESTING.md) 取得最小阶段日志。
> **后续更正**：diag1 用户确认不再冻窗，但 terms layout 构造异常，无法跳转。
> 已发现明文新布局与原生路径 XOR 不兼容；当前按
> [布局存储修复](NATIVE_STORAGE_REPAIR.md) 保留你已修改的布局出新包。
> 下文明文导入流程只是历史记录，不要继续当成原生兼容的安装步骤。

这包只验证游戏界面和资料生成。目前没有注册服务端，不会创建真实账号。
不要看到账号清单就当成已经注册成功；提示会明确写「尚未註冊」。

## 你要做的

只在游戏的「测试副本」操作。先关闭游戏，备份测试副本里的
`data/script.fls`、`data/interface.fls`，不要碰原来的安装目录。

### 1. 把两张新布局装进 interface.fls

1. 用资源编辑器 0.4.2（打开速度修复版）打开测试副本的 `data/interface.fls`。
2. 点顶部「导入」（按路径导入），选择包里的
   `interface_import/login/regterms.dlg`。
   弹窗里的游戏资源路径要填完整：`login/regterms.dlg`。
3. 再导入 `interface_import/login/regform.dlg`，路径填：`login/regform.dlg`。
   不要只填 regform.dlg/regterms.dlg，也不要写成实际硬盘路径。
   如果提示该游戏路径已经存在，才选择替换该路径条目。
4. 保存成新包 `interface_patched.fls`，不要覆盖打开的原包。
   确认资源编辑器报告写后逐条校验通过；原来其它条目必须保持不变。
5. 将这个新包复制到测试副本，命名为 `data/interface.fls`。
   测试副本的旧 interface.fls 要先留好备份；不要重开旧包误以为没导入。

### 2. 换测试副本的脚本

把包里的 `data/script.fls` 复制到测试副本的 `data/script.fls`。
它仅修改首页注册入口和注册模块，不要用它覆盖仓库的锁定原始样本。

### 3. 进游戏检查

1. 首页点「申請會員」，协议页应使用游戏现成服务条款的版式。
   拒绝回首页；同意进新表单。**条款正文应显示正式条款全文**（包内 `script/data/servicedata.pyo`
   存在，2026-10-15 已核实；若这里仍是那三段明示占位文本，说明模块没被取到，属于缺陷）。
   点「我同意」后的二次确认框：本版归档没有 `servicedata.CONFIRM_MSG`，预期显示
   `CONFIRM_FALLBACK` 的明示兜底文案（「確認註冊 / 確定要註冊這個帳號嗎？/ …」）——
   这是有意的兜底而不是坏数据；旧客户端在这里会直接构造失败。
2. 表单应有四个框：账号、密码、确认密码、邮箱。
   三个按钮：上一步、確認註冊、返回首頁。
3. 邮箱下面应有「註冊五個帳號」，默认不勾选。
   点方框或这几个字应都能勾选/取消，一次点只能切换一次。
4. Tab 应按账号→密码→确认密码→邮箱轮转，密码要遮挡显示。

只用下面这组假资料，不要发真实密码给任何人：

- 账号：account
- 密码/确认密码：Preview42
- 邮箱：preview@example.invalid

不勾选，点確認註冊：只弹「伺服器尚未開放註冊，請稍後再試」。
勾选后再点：同一提示里列出五个待注册名称，并明确写「尚未註冊」：

- account
- account_1
- account_2
- account_3
- account_4

五个账号共用密码和邮箱，第一项不加编号，没有 account_0。

长度检查：不勾时账号 6～16 位；勾选时基础账号 6～14 位；密码始终 6～16 位。
可以先取消勾选，输入 16 位假账号 abcdefghijklmnop，再勾选：原输入应保留，
提交应提醒缩短基础账号，不能偷偷截掉末尾两位。

再检查上一步、返回首页，回到表单时勾选默认关闭。

## 什么还没完成

- 真实创建五个账号：还没有服务端注册接口。
- 真正五个全部成功后，弹窗列出五个账号：回调已预留，离线模拟测试通过；
  本测试包不调用成功回调，不能假报完成。
- 真实客户端加载这两条新布局、原生勾选框皮肤及交互：本轮正要由你实机验证，
  Linux 测试通过不等于 Windows 已可用。

后续业务规则已经确定：一条批量请求，由服务器跳过重名并顺延，最多尝试到
_99 且每个最终账号不超过 16 位；凑足五个才整批创建，同一批重试不能多建一组。
这套接口/查重/顺延/事务规则仍待服务端实现，本测试包不实现也不验收这些能力。
包里列出的 account～account_4 只是未查重的候选，未来成功弹窗要用服务端实际名单。

如果打不开或点了没反应：本版**不会再静默**——会弹一个「不詳的錯誤」框、自动退回首页，
并把最后走到的那一步写进测试副本 `photo/register_diag.txt`。把那个文件发我就能定位，
不用你描述现象。常见几行对照：

- `form edit account anchor missing` → `login/regform.dlg` 没导入进 `interface.fls`，
  或导入时游戏路径填成了 `regform.dlg`（必须是完整的 `login/regform.dlg`）。
- `terms anchor missing` → 同上，缺 `login/regterms.dlg`。
- `font fallback FontLT14_3` → 本版客户端没有 `interface.FONT_EDIT`，已自动改用
  旧版实机用过的字体名；这条只是记账，不是失败。
- `step=1 failed type=...` → 建表单页时抛的异常类型（只有类型名，不含你输入的内容）。

诊断不记录账号、密码或邮箱。
不要发送整个游戏目录、真实密码或账号数据库。

还原：退出游戏，将之前备份的 script.fls 和 interface.fls 恢复到测试副本。
