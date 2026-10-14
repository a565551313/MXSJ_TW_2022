# 梦想世界(MXSJ)台湾版 2022 客户端逆向 — 文档索引

> ⛔ **2026-10-12 客户端侧现状以 [`report/client-status-20261012.md`](report/client-status-20261012.md) 为准。**
> 项目级入口在根目录 [`AGENTS.md`](../../AGENTS.md) 与 [`docs/STATUS.md`](../../docs/STATUS.md)。
> 2026-10-14 整理：本目录 10-09/10-10 的交接与分派文档（`HANDOVER-20261010.md`、`HANDOFF-agent-20261010.md`、`QUICK_START.md`、`TASK_DISPATCH.md`、`DISPATCH_OVERVIEW.md`、`发给其他会话的指令.md`、`report/handoff-20261009.md`）已移至 [`docs/archive/work-20261010/`](../../docs/archive/work-20261010/)，下文对它们的引用均指归档位置。
> 本索引中与该文冲突的内容已过期，至少包括：`tools/mock_server.py` 已被**仓库根目录**的
> `mock_server.py` 取代；命令字 0x0001/0x0002/0x0003/0x0010/0x00FF 不成立（命令字是单字节 1..242，
> 权威表见 `artifacts/protocol_table/protocol_opcodes.csv`）；帧格式不是 `uint16_be 总长 + 命令字`，
> 而是 `[1 字节长度 L][L 字节包体]`，`L==0xFF` 时续读 **2** 字节小端长度；
> `packet_analyzer.py` / `enhanced_capture_server.py` / `im_crypto.py` 的帧模型已过期。

**最后更新**: 2026-10-10（同日完成核对，见 `report/verification-20261010.md`）
**原工作分支**: `arena/6fbb3403-mxsj-tw-2022`（已合入 master）
**当前会话分支**: `arena/febc1561-mxsj-tw-2022`（与 master 同一 commit `ffec3d9`；`711e6a7` 为其祖先）

---

## ⭐ 新接手必读

| 文档 | 说明 |
|------|------|
| [**report/client-status-20261012.md**](report/client-status-20261012.md) | ⭐ **客户端侧权威现状**：协议号表来源、帧格式判定、过期工具清单（先读） |
| [**report/verification-20261010.md**](report/verification-20261010.md) | 2026-10-10 核对报告：哪些说法已核实、哪些不成立 |
| [HANDOVER-20261010.md](../../docs/archive/work-20261010/HANDOVER-20261010.md)（已归档） | 10-10 交接文档：当时的进度、文件路径、工具手册、FAQ；工具手册部分仍有参考价值 |
| [QUICK_START.md](../../docs/archive/work-20261010/QUICK_START.md)（已归档） | 10-10 快速上手；其命令字/帧格式结论已被 client-status 推翻 |

---

## 📊 任务进度

| 任务 | 状态 | 报告 |
|------|------|------|
| A - 登录脚本反编译 | ✅ 完成 | `notes/co_code_analysis/netserver_py_decompiled.md` |
| B - 脚本全量分析 | ✅ 基本完成 (95%) | `notes/task-b-脚本分析/artifacts/终版统计.md` |
| C - 地图格式分析 | 🔄 第二轮 (~70%) | `notes/task-c-地图分析/map-format-analysis.md` |
| D - 游戏数据分析 | ✅ 完成 | `notes/task-d-游戏数据/game-data-analysis.md` |
| ④ - 命令字数值 | ⚠️ 数值未证实 | `notes/protocol-commands-values.md` |
| E - 模拟服务器 | 🔄 框架已建，未与客户端联调 | `task-briefs/TASK-E-mock-server.md` |
| G - 协议文档 | ⏳ 可开始 | `task-briefs/TASK-G-protocol-doc.md` |
| ① - 混淆字典 key | ⏳ 待破解 | — |
| ② - 参数字节编码 | ⏳ 待破解 | — |
| ③ - S2CServerRoleInfo | ⏳ 待抓包 | — |

---

## 📁 目录导航

### 报告（按任务）
```
report/
├── verification-20261010.md           # ⭐ 2026-10-10 核对报告
├── final-summary-20261010.md          # 项目最终总结（任务A）（含修正提示）
├── analysis.md                        # 综合分析报告
└── client-status-20261012.md          # ⭐ 客户端侧权威现状（2026-10-12）
    （handoff-20261009.md 已归档至 docs/archive/work-20261010/）

notes/
├── co_code_analysis/                  # 任务A：字节码破解
│   ├── mapping_table_v4.json          # ⭐ 映射表 v4.3（最新版）
│   ├── netserver_py_decompiled.md     # 登录脚本反编译
│   ├── 任务A深入-Connect函数破解报告.md
│   └── 任务A深入-表B破解报告.md
├── task-b-脚本分析/                   # 任务B：脚本全量分析
│   └── artifacts/
│       ├── 终版统计.md                # ⭐ 终版统计（89.6% ok）
│       ├── protocol-commands-catalog.md  # ⭐ 协议命令目录（63KB）
│       ├── mall-protocol-analysis.md  # 商城协议专题
│       ├── battle-logic-analysis.md   # 战斗逻辑分析
│       ├── quest-item-analysis.md     # 任务/物品分析
│       ├── suspicious-names-review.md # 可疑名复核
│       ├── unknown-opcode-round4-status.md  # 第四轮未知opcode
│       ├── fullrun/                   # 全量解码结果
│       └── script-catalog.csv         # 脚本目录（5002 条数据 + 表头）
├── task-c-地图分析/                   # 任务C：地图格式分析
│   ├── map-format-analysis.md         # ⭐ 地图格式完整报告
│   ├── README.md
│   └── artifacts/                     # 分析脚本和可视化
├── task-d-游戏数据/                   # 任务D：游戏数据分析
│   ├── game-data-analysis.md          # ⭐ 完整报告
│   ├── task-d-summary.md              # 摘要
│   └── E-DATA-001.md                  # 证据文件
├── protocol-commands-values.md        # ⭐ 命令字数值
├── crypto-analysis-complete.md        # 加密算法完整报告
├── protocol-artifacts/                # 加密相关
│   ├── im_crypto.py                   # ⭐ 加密/解密模块
│   └── *_sbox.bin                     # S盒文件
└── decoder-artifacts/                 # FLS解码
    └── all_scripts_catalog.json       # 全部5002条目catalog
```

### 工具
```
tools/                                 # 根目录工具（任务B/D）
├── fls_batch_decoder.py               # ⭐ FLS批量解码器 v7
├── pymarshal_dis.py                   # ⭐ Python 2 marshal反汇编
├── extract_co_signatures.py           # 签名提取
├── data_browser/                      # 数据浏览器（任务D）
├── data-parser/                       # 数据解析/重打包（任务D）
└── data-export/                       # 导出数据（任务D）

work/.../tools/                        # 工作区工具
├── map_parser.py                      # 地图解析器（任务C）
├── map_viewer.py                      # 地图查看器（任务C）
├── map_gui.py / map_gui_html.py       # 地图GUI（任务C）
├── gepj_decoder.py                    # GEPJ图像解码（任务C）
├── mock_server.py                     # 模拟服务器框架
├── packet_analyzer.py                 # 数据包分析
├── enhanced_capture_server.py         # 增强捕获（自动破解密钥）
└── test-data/                         # ❌ 目录不存在（2026-10-10 核对）；原 loginhello 明文包样本缺失
```

### 证据文件
```
evidence/                              # 根目录证据（任务D）
└── E-DATA-001.md

work/.../evidence/                     # 工作区证据
├── E-CRYPTO-001.md                    # 加密破解证据
├── E-SCRIPT-001.md / E-SCRIPT-002.md  # 脚本分析证据
├── E-MAP-001.md / E-MAP-002.md / E-MAP-003.md  # 地图分析证据（任务C）
├── E-REA-*.md                         # 静态分析证据
├── E-IDA-*.md                         # IDA分析证据
├── E-LOOPBACK-*.md                    # 回环测试证据
├── E-VERIFY-001.md                    # 2026-10-10 核对证据
└── ...
```

### 任务书
```
task-briefs/
├── TASK-B-script-analysis.md          # 任务B：脚本全量分析
├── TASK-C-map-format.md               # 任务C：地图格式分析
├── TASK-D-game-data.md                # 任务D：游戏数据分析
├── TASK-E-mock-server.md              # 任务E：模拟服务器
└── TASK-G-protocol-doc.md             # 任务G：协议文档
```

---

## 🔍 快速查找

| 你想找... | 去这里 |
|----------|--------|
| 当前项目状态 | 根目录 `docs/STATUS.md` |
| 2026-10-10 时的整体进度 | 归档 `docs/archive/work-20261010/HANDOVER-20261010.md` 第 2 节 |
| 某个任务的详细报告 | 见上表"报告"列 |
| 工具怎么用 | 归档 `HANDOVER-20261010.md` 第 6 节；过期工具清单见 `report/client-status-20261012.md` §5 |
| 文件路径 | 归档 `HANDOVER-20261010.md` 第 5 节 |
| 映射表 v4.3 纠正 | 归档 `HANDOVER-20261010.md` 第 7.1 节；完整 opcode 表见根目录 `notes/opcode_mapping_and_decompilation.md` |
| 协议命令字 | `notes/protocol-commands-values.md` |
| 协议命令目录（28个家族） | `notes/task-b-脚本分析/artifacts/protocol-commands-catalog.md` |
| 商城协议 | `notes/task-b-脚本分析/artifacts/mall-protocol-analysis.md` |
| 战斗逻辑 | `notes/task-b-脚本分析/artifacts/battle-logic-analysis.md` |
| 地图格式 | `notes/task-c-地图分析/map-format-analysis.md` |
| 加密算法 | `notes/crypto-analysis-complete.md` + `notes/protocol-artifacts/im_crypto.py` |
| 命令字数值 | `notes/protocol-commands-values.md` |
| 混淆key候选 | 归档 `HANDOVER-20261010.md` 附录 |
| 常见问题 FAQ | 归档 `HANDOVER-20261010.md` 第 9 节 |
| 协议号权威表（412 条） | `artifacts/protocol_table/protocol_opcodes.csv`（来源 `script.fls` entry 3970） |

---

## 📝 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-10-14 | 文档整理：交接/分派类文档归档至 `docs/archive/work-20261010/`，本索引改为指向归档位置与 client-status |
| 2026-10-12 | 新增 `report/client-status-20261012.md`，取代本索引中与之冲突的内容 |
| 2026-10-10 | 创建 INDEX.md 和 HANDOVER-20261010.md；更新 QUICK_START.md |
| 2026-10-10 | 全面核对：新增 `report/verification-20261010.md`、`evidence/E-VERIFY-001.md`；修正 HANDOVER、workitems（WI-009 改回 in_progress，WI-012 改为 partial，新增 WI-013–017）、QUICK_START、INDEX；补全浅克隆历史；未删除任何文件 |
| 2026-10-10 | 合并任务C（PR #3）和任务B收尾（cherry-pick PR #4） |
| 2026-10-10 | 任务B终版统计：89.6% ok（4484/5002） |
| 2026-10-09 | 任务A完成、任务D完成、命令字数值确定 |
