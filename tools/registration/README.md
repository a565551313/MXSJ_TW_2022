# 注册界面原生重做（第一期：管道验证）

## 这是什么

把旧运营商时代的注册脚本换成我们自己写的、合乎游戏原生规范的实现，
作为 UI 编辑器 x script.fls 联动的第一个实战。本期只求**管道跑通**：
首页点「申請會員」-> 条款页 -> 表单页 -> 点确认只弹桩提示
「伺服器尚未開放註冊，請稍後再試」，不发任何网络请求。

## 做法（全部原生）

| 环节 | 做法 |
|---|---|
| 入口 | 首页 mainpage（条目 337）「申請會員」分支本就有走 register 的原生代码，只是被服谓词挡住；打一个 9 字节定宽补丁把该谓词换成 False（与旧 v1 已实机验证的补丁逐字节相同） |
| 脚本 | `login/register`（条目 4007）整模块换成本目录 `register.py`：条款页 `CRegTermsPanel`（reg1.dlg）+ 表单页 `CRegFormPanel`（reg2.dlg），`CCombPanel` 按名取件、`OnMessage` 分发、`Show/Step` 开关，与改密表单 `chgpwd` 同一套路 |
| 对外接口 | `Show`/`ShowConfirmDlg`/`CConfirm`/`g_AccountInfo`/`g_ConfirmDlg` 等 loginin、netlogin、selectrole、mainpage 在用的接口全部保留，帐号确认框行为原样 |
| 布局 | 本期不动 interface.fls：复用旧 `login/reg1.dlg`/`login/reg2.dlg`；2980 链接与图形验证码的占位控件在脚本里隐藏，步骤图沿用旧图 |
| 打包 | 先 `build_python25.sh` 自建 CPython 2.5.6，再 `build_native_registration.py`：编译 -> 混淆 -> 5 段 XOR 加密 -> 重打包；原包只读、产物另存、只改 337/4007 两条、其余 5000 条负载逐字节不变，构建后自动逐项校验 |

## 与旧版的已知差异（记账）

1. 旧 reg2.dlg 没有独立帐号框，**邮箱即帐号**（原版式如此）；用户定的
   「帐号+密码+确认+邮箱」四字段要等第二期改版 layout 后实现。
2. 条款文本原由外部模块 `servicedata.SERVICE_MSG` 提供，该模块不在本
   版本 script.fls 里；缺失时用源码内的**占位条款**（正式条款待补）。
   `CConfirm` 仍按原样引用 `servicedata.CONFIRM_MSG`（既有流程，不动）。
3. 条款页所有非「同意」按钮统一返回首页（旧版 msgid 2 是关闭游戏，
   那是把注册当入口页时代的语义；现在从首页进入，返回首页才对）。
4. 旧版的输入框子类（限字母数字、焦点提示气泡）第一期未复刻：改在
   提交时校验密码为字母数字；提示气泡第二期随 layout 一起补。
5. 删除的旧流程：HTTP 注册、2980 邮箱/手机验证、图形验证码、
   `gameurl`/`net.CHttpObject`/`OpenUrl`——构建校验会断言这些名字
   不出现在新模块里。

## 第二期（待用户导出模板后）

请用资源编辑器打开真实 interface.fls 按真名导出并回传：
`login/chgpwd.dlg`、`login/reg1.dlg`、`login/reg2.dlg`、`login/confirm.dlg`。
拿到后：给表单加上独立帐号框（改 reg2.dlg 或仿 chgpwd 新建布局）、
补焦点提示气泡、条款定版，再出第二期测试包。

## 用法

```sh
sh tools/registration/build_python25.sh            # 一次性，产物在 /tmp/py25build
python3 tools/registration/build_native_registration.py \
    --python25 /tmp/py25build/cpython-2.5.6/python
# 产物：tools/registration/out/script.fls（git 忽略，不入库）
```

测试方法（用户在已还原原包的测试副本上）：把产物改名 script.fls 放回
data 目录启动游戏，首页点「申請會員」应出现条款页；同意进表单；
乱填应报格式错；填对点确认应弹「伺服器尚未開放註冊，請稍後再試」。
