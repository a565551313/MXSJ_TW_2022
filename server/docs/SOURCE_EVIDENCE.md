# 材料证据与边界（2026-10-11）

## 原始资料

- `data/data.fls`：现有 `tools/decompiler/output/data_fls/` 有121个 .py；其中lib62、pub2 29，以客户端基础框架为主。
- `data/script.fls`：5002个条目；现有源码输出目录只有52个 .py，不能称为全量源码已还原。
- 历史全量目录：`work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl`。
- 历史状态：ok4484、suspect246、fail272；这是旧解码器结果，**不是本次全量重验**。
- 当前 script.fls SHA-256：`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`。

## 本次建立清单时的检查

对模块参考中的96个唯一条目，从当前归档读取、解压、按密钥转译marshal并提取根文件名；96个完成该检查。
结果保存在 `source_map.json`。这不是96个文件都已反编译成功，更不是完整玩法代码审核。
主参考之外的前缀匹配数来自历史目录，不能据此宣称全量准确覆盖。

## 已做过的函数级行为抽查

| 条目 | 模块 | 发现 |
|---|---|---|
| 1406 | script/netwar.py | C2SWarAttack/Perform发请求；S2CWarWState读取hp_chg与生命状态；HP百分比也从服务器读取 |
| 697 | script/core/war.py | State使用收到的血量变化/生命状态驱动表现；NextServerCmd/ServerCmd执行服务端指令 |
| 3745 | script/mxgame/item/netitem.py | 使用物品发请求；S2CItemAdd/Quantity读取服务器物品及数量 |
| 4913 | script/mxgame/task/nettask.py | S2CTaskAdd从服务器读取任务名字、描述、NPC等信息 |
| 1721 | script/mxgame/fakewar/fakewar.py | CFakeWar继承界面对象，读取FWR并管理表现指令，不能直接视为权威战斗模拟器 |

上一轮抽查时整体反编译 netwar、skilldata 遇到错误；netwar关键函数单独还原成功。
临时输出不是本次工程的权威源码，也未拷入 server 作为可执行业务代码。

## 新设计，不是逆向事实

数据库选型、模块分组、DTO字段、方法名、幂等/事务规范、战斗阶段和协作组均为我们提出的架构。
原版伤害公式、掉落率、成长公式、任务完整分支、经济约束、实际协议字段有效范围仍需各组核实。
客户端原始代码也可能依赖 C_sys/C_net/C_marshal 等原生模块，Python文件不等于可独立运行。

## 待继续盘点

source_map只选取起步参考，不是穷尽5002条目的分类；每组应交付自己的完整材料清单。
未映射内容、支付/跨服等未单独立项能力应进入后续评审，不应被默认为“已完成”。
不要将 tools/data-export 的所有字段作为权威游戏规则：之前已发现硬编码装备和按索引生成的技能字段。

## 重复验证当前归档引用

在仓库根目录执行 `PYTHONDONTWRITEBYTECODE=1 python3 server/tools/verify_source_map.py`。
该工具只读归档并验证记录中的文件名，不执行游戏脚本，也不写出反编译产物。


## 后续全量文件名检查（本轮新增，不替代函数审核）

已覆盖5002个条目：4979个获得当前转译文件名；9个完成转译但没有提取到文件名；14个转译失败。
其中23个使用历史文件名回退，60个索引路径有结构异常；351个当前文件名与历史记录不同，需要核实，不能自动称作纠错成功。
本轮没有执行游戏脚本，也没有全量反编译成Python源码；函数名列表仍来自历史解码记录。
细节见 `catalog/summary.json`、`catalog/script_entries.jsonl`、`catalog/DIRECTORIES.md`。

重复生成（从仓库根目录运行）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/build_material_inventory.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/build_feature_catalog.py
```

其他归档仍不能漏掉：skill.fls 342、skill2.fls 454、passive.fls 41、effect.fls 65个条目（本轮仅检查头部数量，未判断具体载荷语义）。
