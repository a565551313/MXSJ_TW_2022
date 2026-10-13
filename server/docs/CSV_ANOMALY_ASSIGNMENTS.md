# 客户端CSV提取异常：可分派给其他Agent的检查任务

## 复制给所有Agent的共同说明

请对分配给你的客户端静态配置异常做独立核查，为后续CSV导出提供依据。这里只检查静态目录和配置，不实现玩家实例存储或服务端业务。

仓库：`a565551313/MXSJ_TW_2022`。
已推送的初始检查基线：`arena/b53b33e6-mxsj-tw-2022`，提交 `2d403c2`。注意：本次扩展扫描、清单和新工具是在此基线上新增的工作区材料，生成本文件时尚未提交推送。仅拉取该提交不会得到新材料，需要协调者提供附件或后续提交。

输入主体是 `data/script.fls`。下面的“条目”是FLS的零基索引，不是道具/宠物ID；“记录”才是表中的键。序列下标也是零基。

当前保存的XOR边界和字节码修复带有启发式。请区分：提取错误、读取器尚不支持的合法表达式、原始源值、正常业务差异、未解决问题。不要预设所有异常都由同一原因引起。

禁止事项：

- 不修改原始FLS和客户端，不启动会修改客户端的 `mock_server.py`。
- 不执行恢复的游戏脚本，不使用 `exec/eval` 或导入其代码来生成表。
- 不猜名称/技能ID，不剪掉坏字节，不静默丢弃记录，不把表间名称差异直接统一。
- 不把未确认候选写入正式 `server/game_data/`，本轮不做繁简转换。
- 不用“编码合法”“文字通顺”“相邻编号连续”“测试通过”代替原生加载结果或独立证据。

## 共同材料与复现

初始基线中已有：

```text
docs/archive/2026-10-11-CLIENT_DATA_AGENT_HANDOFF.md（原 server/docs/CLIENT_DATA_AGENT_HANDOFF.md，已归档）
server/docs/CLIENT_DATA_REVIEW.md
server/docs/catalog/client_data_boundary_review.json
server/tools/review_client_data_boundaries.py
```

本轮扩展材料（需取得附件或后续提交）：

```text
server/docs/CSV_READINESS.md
server/docs/catalog/csv_readiness_survey.json
server/tools/survey_csv_readiness.py
server/tests/architecture/test_csv_readiness.py
```

在取得对应材料的仓库根目录运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_client_data_boundaries.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/survey_csv_readiness.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -v
```

扩展扫描覆盖33个脚本、48个指定表目标，其中38个能重建字面量赋值、10个未可靠重建。不是全客户端检查。机器报告包含来源SHA-256、字段路径、原始异常字节、类型/关联问题和错误原因。原始字节在JSON中，不要用本任务书的中文摘要反向猜值。

## Agent A：底层解码和四个边界候选（公共工具唯一负责人）

**目标：**核对真实的分段/XOR规则、自定义Python字节码和marshal格式，定位现有启发式工具为什么可以产生“结构合法但值错误”的输出。

重点文件：

```text
tools/decompiler/batch_decompile.py
tools/decompiler/script_fls_keys.json
tools/fls_batch_decoder.py
```

请验证这四个候选，偏移都是**zlib解压载荷中的零基偏移**：

| 条目 / 记录 | 边界索引 | 旧边界 → 候选边界 | 当前候选结果 |
|---|---:|---|---|
| 1945 / 道具10424 | 0 | 259624 → 259583 | “同心靈果·陰”描述恢复连贯文字 |
| 1945 / 道具71700 | 3 | 1038363 → 1038307 | “時空之輪”使用说明恢复连贯文字 |
| 1115 / 宠物2910 | 0 | 825 → 828 | 整数2280变为“混沌騎士” |
| 2242 / SKILLIDLST[16] | 1 | 262 → 264 | 64605变为416 |

限制：前两项有其他可合法解码的边界候选；1115探测时关闭了字节码边界自动求解；416未与技能主表/原生结果独立核实。均未批准为正式修复。

优先追踪原生加载逻辑，旧工具关于 `PkgImport` 地址等注释只能作为线索，必须核对具体二进制与地址映射。保留全量字节变化、受影响范围和回归结果。其他Agent向你提交字节/边界证据，不各自修改公共解码器。

## Agent B：道具、装备、工艺、宝石、商城和相关物品表

| 条目 / 脚本 | 表 / 记录 / 字段 | 本轮发现 |
|---|---|---|
| 1945 / itemdata.py | DATA[10424][1] | “同心靈果·陰”描述不能严格按CP950解码；与Agent A的候选交叉验证 |
| 1945 | DATA[71700][1] | “時空之輪”描述编码异常；与Agent A交叉验证 |
| 1945 | DATA[72548][0] | 可读前缀“雙人坐騎體驗”，末尾字节84；坏字节载荷偏移1100465，不邻近已保存的四个边界，禁止直接删除 |
| 17 / equipitemdata.py | DATA[55010][2] | “飛蝗石”的属性文本可以解码，但包含控制字符和乱码；不是名称或描述字段 |
| 1698 / itemextdata.py | DATA[10004] | 编码失败 |
| 1698 | DATA[10020]、DATA[10026] | 能解码但含控制字符；不能只修10004 |
| 2455 / craftdata.py | DATA[25241]['name'] | 名称含控制字符；道具表同ID为“白芒角樽”，只能用于交叉佐证，不能直接覆盖 |
| 246 / gem2equipposdata.py | GEM2EQUIP[72838]['Name'] | “寶石附魔”与道具表“寶石附魔符”不一致，可能是合法简称 |
| 3791 / petitemdata.py | DATA[10191]、DATA[25670] | 两个名称编码失败 |
| 3791 | CHILD_DATA[72222] | “神武項圈”与道具表“武神項圈”不一致 |
| 2409 / shopdata.py | DATA[8]['itemid'] | 商品ID变成文字“雙技能英靈護符”，该行name却为“隨機終級獸訣” |
| 2409 | DATA[7]['itemid']=72050、DATA[9]['itemid']=9027 | 引用未在当前道具主表找到，不能直接判非法商品或补造道具 |
| 1381 / cookdata.py | DATA目标 | 受限读取器拒绝 opcode 21 @4938；需区分有效表达式和解码错误 |
| 2338 / drugs2typedata.py | DATA目标 | 保存的分段边界未通过排序校验：invalid boundary ordering |
| 293 / equipicondata.py | DATA目标 | 异常EXTENDED_ARG；当前提取的文件名本身也出现 `scripeMdata` 异常前缀 |
| 4924 / mxitemdata.py | DATA目标 | 受限读取器拒绝 opcode 75 @39396 |

交付重点：哪些问题来自解码，哪些名称差异是正常业务用途，哪些字段可以原样保留在待审CSV。商品表中的价格和类型不能未经核实就成为服务端商城规则。

## Agent C：宠物详情、资质、图鉴和怪物说明

| 条目 / 脚本 | 表 / 记录 / 字段 | 本轮发现 |
|---|---|---|
| 2027 / petdata.py | DATA[2600]['address'] | 出现地点文本编码失败 |
| 2027 | DATA[4011]['maySkillLst'][3] | 第4个候选技能名称编码失败，可能影响名称关联 |
| 1115 / mxpetdata.py | DATA[2910] | 基线值为整数2280；另一表同ID为“混沌騎士”；修复候选交Agent A验证 |
| 2954 / petaptitudedata.py | DATA[2800] | “機甲少女”的“法力資質”为2130，“法力資質最大值”为1989；需核查字段用途及原始值，不自动交换 |
| 1761 / petgraphdata.py | DATA[2190]['desc'][0]、DATA[2600]['desc'][0]、DATA[4015]['desc'][0] | 图鉴描述编码失败 |
| 3526 / monsterdata.py | DATA[2490]['lock1']、DATA[2650]['lock2']、DATA[2740]['lock3'] | 怪物/图鉴说明编码失败；lock3包含技能说明 |

另外必须核查、不能直接修正的关系差异：

- 宠物详细表135条、mxpetdata137条，后者多5106和5107。
- 4024在详细表叫“仙獸雷吉斯”，mxpetdata叫“神獸雷吉斯”。
- 132条资质记录都能关联详细表，但详细表3010、4021、4022没有对应资质记录。不能补零。
- 用现有解码结果搜索 `mxpetdata` 字面串只找到其自身，不能据此判断该表无用。

技能主表由Agent D负责；你负责提供技能名、形态ID及交叉引用证据。不要把monsterdata中的图鉴说明当作完整战斗属性。

## Agent D：技能、技能书、主动技能与Buff

| 条目 / 脚本 | 目标 | 当前症状 |
|---|---|---|
| 3205 / petskill.py | DATA | 曾遇常量索引越界；严格扫描先遇EXTENDED_ARG后接无参指令 |
| 454 / skilldata.py | DATA | 受限读取器拒绝 opcode 83 @3086 |
| 3075 / skillbookdata.py | DATA | 受限读取器拒绝 opcode 70 @5626 |
| 2242 / petactiveskilldata.py | SKILLIDLST[16] | 64605位于415、417之间；候选416未被确认，与Agent A协作 |
| 333 / buffdata.py | DATA[277]['desc']、['effect'] | 两字段编码失败 |
| 333 | DATA[702]['desc']、['effect'] | 两字段编码失败 |

交付重点：区分损坏转译与当前字面量读取器不支持的真实表达式；恢复后检查技能ID和名称关系，给Agent C提供可验证映射。不能按邻号补技能ID，也不能把客户端说明当成服务端完整技能算法。

## Agent E：地图、场景、NPC名称和坐标

| 条目 / 脚本 | 目标 | 当前症状 |
|---|---|---|
| 1301 / mapdata.py | DATA的异常键 | 一条键为文字“兔坦卡門陵墓”，值中name却为“加洛法師師道殿”，w=1588、h=1220；其他记录主要用整数键 |
| 400 / sceneid2name.py | DATA[1071] | 在当前mapdata表中没有同键记录；可能是用途差异，也可能有关联数据未正确提取 |
| 1799 / npcname2realnamedata.py | DATA['個人心法教師'] | 对应名称值编码失败 |
| 1799 | DATA中的另一条键 | 键本身编码失败；原字节hex为 `a4d1bfefa8197c1a`，不能靠显示出来的“天選...”猜名称 |
| 2601 / npcposdata.py | DATA目标 | 受限读取器拒绝 opcode 101 @124，可能依赖其他运行时值 |
| 2804 / minimapnpcpos.py | DATA目标 | 未找到支持的字面量赋值；请先核实实际变量名、初始化/版本分支，不能直接判文件损坏 |

交付重点：确认两张地图/场景表是否同一语义；确认NPC数据是否依赖版本条件或初始化函数。不要直接把不同表的尺寸和ID体系合并，不通过执行游戏脚本获取结果。

## Agent F：称谓、坐骑提示和家具数据

| 条目 / 脚本 | 目标 | 当前症状 |
|---|---|---|
| 2566 / titledata.py | DATA[336][0]、DATA[877][0] | 称谓说明文本编码失败 |
| 1919 / ridedata.py | CHANGESHAPE_PREVIEWDATA[24]、[34] | 坐骑造型切换提示编码失败 |
| 244 / newfurnituredata.py | DATA目标 | 读取期间遇异常EXTENDED_ARG；此前TYPE2NAME和ORDER等字面量可部分恢复，不代表家具主表已恢复 |

交付重点：保留富文本标记，核实家具主数据实际存放位置和赋值方式。不能因为几个辅助表有数据，就宣称完整家具配置已恢复。

## 协作边界与统一交付格式

- Agent A负责公共解码器变更。B～F在各自工具/报告中做独立探测，不并行改写历史密钥库、公共转译器或同一份总报告。
- 建议各组分别交付 `server/docs/csv_checks/AGENT_A.md` 等报告和自有小型复现脚本/JSON。此路径是建议，不代表这些文件已存在。
- 每项至少记录：条目索引、实际文件名、表、记录键或原字节、字段路径、输入SHA-256、原始载荷偏移（能定位时）、当前值/字节、候选、依据、状态、未排除解释。
- 状态建议：`confirmed_extraction_bug`、`confirmed_source_value`、`legitimate_table_difference`、`reader_limitation`、`candidate`、`unresolved`。
- 确认源数据本身异常前，要说明如何排除了提取器和编码解释错误。
- 测试必须同时包含“可以解码但值错误”的反例；记录实际执行命令和失败项。
- 最后说明可否进入待审CSV、需隔离哪些记录，以及是否取得原生算法或独立读取结果的证据。不要笼统写“全部修复”。

## 汇总提醒

这份清单收集的是已发现问题，不是完整异常总数。特别是数字和合法中文中的潜在错误仍可能漏检。当前31项检查通过是研究回归结果，不是游戏数据完整正确的证明。
