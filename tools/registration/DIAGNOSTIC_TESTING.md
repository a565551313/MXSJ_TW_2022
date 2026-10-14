# 第二期入口卡屏诊断包 phase2-diag1

## 目的与边界

2026-10-14 用户确认：网盘 `registration_phase2.zip` 的脚本；两个新布局
在同一个实际 interface.fls 都能找到；申请会员导致整个窗口冻住、无响应。
这排除了此前“只导入了表单”的排查前提，但不证明原生加载成功。

本包是**阶段诊断 + 会返回的脚本异常尽力回退**，不是已定位/修好的原生卡屏。
没有真实注册接口，不发注册请求，不创建账号。继续使用现有两张新布局，
不要求再导入、覆盖 interface.fls 或上传整个 600 MB 包。

## 测试副本中只换脚本

1. 退出游戏。只操作测试副本，另行备份当前 `data/script.fls`。
2. 把本包 `data/script.fls` 放到测试副本的同名位置。
   **保留已经有 regterms/regform 的 interface.fls 不变。**
3. 若已有 `photo/register_diag.txt`，先改名备份，避免混淆旧日志。
   若有工作目录根下 `register_diag.txt` 也一并改名备份，不删其它游戏日志。
4. 启动测试副本，点一次「申請會員」，不要连点或输入真实账号资料。
5. 若仍冻住，可用任务管理器结束这个测试副本。该版本每条阶段日志写完
   立即关文件，不需要等游戏正常退出才保存；但不能保证断电情况下持久化。
6. 只回传该次 `photo/register_diag.txt` **最后 30 行**。
   若 photo 路径无法写入，日志会尝试写到游戏工作目录 `register_diag.txt`，
   请检查这个备用位置；两个位置都没有时如实说没有，不能据此断定入口没执行。
   不要发整个游戏包、账号数据库或真实密码；截图如含登录资料请遮挡。

若协议页已出现：先拒绝回首页，再重新打开并同意，检查表单/返回按钮即可。
这次先定位入口，不需要重复提交资料测试，更不需要操作任何真实账号。

## 怎么解释最后阶段（维护者）

每次打开的识别标记是 `phase2-diag1 show open begin`。
首次导入还有 `phase2-diag1 module begin` 和 `phase2-diag1 module ready`。
前后标记用于圈定调用范围，不是证明内部某一行必定有错。

| 最后阶段例子 | 本次停留的调用范围 |
|---|---|
| `module import ... begin`，无对应 ready | 对应依赖模块导入；尚未完成注册模块初始化 |
| `input secrecy on begin`，无 ready | 原生 `C_sys.InputSecrecy(1)` |
| `terms layout begin`，无 ready | 原生 CCombPanel 构造；包含布局读取、控件/资源创建、AfterInit 和 MessageProcess，不只是“找文件” |
| `terms source begin`，无 ready | servicedata 导入/条款处理；缺失仍回退占位条款 |
| `terms anchor begin`，无 ready | loc_msg 查找及 GetSize/GetPos |
| `terms output create begin`，无 ready | COutput 构造，内部也有 MessageProcess |
| `terms output reset begin`，无 ready | 条款文本排版/滚动初始化 |
| `step=0 ready` 后仍卡 | 构造已返回，应继续查后续绘制/消息；不能据此说游戏通过 |
| `step=... EXC type=...` | 捕获到会返回的 Python 异常；只记类型，不记可能含隐私的异常文本 |

表单阶段同样记录 layout、导入、四编辑框、Tab、提示、勾选框、默认值和焦点。
`entry recovery home ready` 仅表示尝试恢复首页的函数已返回，显示效果待实机。
没有线程/看门狗/强制中断；原生同步调用不返回时 **except 无法恢复或超时取消**。

## 离线证据与未验

- 自写源码使用真 CPython **2.5.6** 编译、marshal/opcode 转换后从新包读回验证。
- 相对锁定原包仅 337/4007 改变；337 仍是原 9 字节条件补丁，没有扩大窗口。
- 相对已发第二期脚本（SHA-256
  `17a94c77e4cda673023f0e17221edb73f789183a0af0d4fcd5c6a1d3b651e0b2`）
  **仅 4007 改变，另外 5001 条压缩负载相等**。
- 14 项离线测试通过，含原版本先失败、本版通过的入口异常恢复探针；桩中
  模拟布局/文本异常、无效尺寸、旧页面引用保留、日志隐私/写失败/备用路径。
  原 code object 只读反汇编确认 COutput 使用 `w-20` 的行宽，故拒绝非正有效
  行宽/高度；这只是防御条件，没有证据表明用户的 loc_msg 尺寸有问题。
- 日志仅 ASCII 阶段/尺寸/异常类型；不输出账号、密码、邮箱或完整 traceback。
- 尚无 Windows/原生引擎运行证据；离线桩**没有复现或证明修复用户的整窗无响应**。
  不改引擎、布局、目录 f1/XOR 策略，也不启动服务端。

还原：退出测试副本，恢复本次单独备份的 script.fls；interface.fls 不需要改动。
