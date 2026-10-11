# 原版客户端协议适配

接入负责人负责。当前只有目录，没有编解码实现。

## 材料起点

- script.fls entry 3970：`script/protocol.py`，命令常量。
- entry 4082：`script/login/netlogin.py`，登录与角色选择。
- entry 1406：`script/netwar.py`，战斗请求和回包；与战斗组共同核验。
- entry 3745：`script/mxgame/item/netitem.py`，物品操作与同步。
- entry 4913：`script/mxgame/task/nettask.py`，任务同步。
- 根目录 `mock_server.py`：实验报文参考，不作为协议真值，不导入其自动补丁启动流程。

正式协议表必须记录：方向、opcode/subcode、字段宽度与符号、编码、版本、允许会话阶段、长度上限、证据、测试样本。
源代码读出的格式与真实客户端验证过的格式分开标注。S2C 接收函数不能当作服务端 C2S Handler。
新内部 DTO 不直接映射旧报文字段布局；战斗单位ID与角色ID等不能混用。
