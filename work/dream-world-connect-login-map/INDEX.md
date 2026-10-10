# 梦想世界(MXSJ)台湾版 2022 客户端逆向 — 文档索引

**最后更新**: 2026-10-10（同日完成核对，见 `report/verification-20261010.md`）
**原工作分支**: `arena/6fbb3403-mxsj-tw-2022`（已合入 master）
**当前会话分支**: `arena/febc1561-mxsj-tw-2022`（与 master 同一 commit `ffec3d9`；`711e6a7` 为其祖先）

---

## ⭐ 新接手必读

| 文档 | 说明 |
|------|------|
| [**HANDOVER-20261010.md**](HANDOVER-20261010.md) | ⭐ **项目交接文档** — 完整进度、文件路径、工具手册、FAQ |
| [**QUICK_START.md**](QUICK_START.md) | 5 分钟快速上手 |
| [**report/verification-20261010.md**](report/verification-20261010.md) | ⭐ **2026-10-10 核对报告**：哪些说法已核实、哪些不成立（先读） |

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
└── handoff-20261009.md                # 旧交接文档（2026-10-09）

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
│       └── script-catalog.csv         # 脚本目录（5007行）
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
| 项目整体进度 | `HANDOVER-20261010.md` 第 2 节 |
| 某个任务的详细报告 | 见上表"报告"列 |
| 工具怎么用 | `HANDOVER-20261010.md` 第 6 节 |
| 文件路径 | `HANDOVER-20261010.md` 第 5 节 |
| 映射表 v4.3 纠正 | `HANDOVER-20261010.md` 第 7.1 节 |
| 协议命令字 | `notes/protocol-commands-values.md` |
| 协议命令目录（28个家族） | `notes/task-b-脚本分析/artifacts/protocol-commands-catalog.md` |
| 商城协议 | `notes/task-b-脚本分析/artifacts/mall-protocol-analysis.md` |
| 战斗逻辑 | `notes/task-b-脚本分析/artifacts/battle-logic-analysis.md` |
| 地图格式 | `notes/task-c-地图分析/map-format-analysis.md` |
| 加密算法 | `notes/crypto-analysis-complete.md` + `notes/protocol-artifacts/im_crypto.py` |
| 命令字数值 | `notes/protocol-commands-values.md` |
| 混淆key候选 | `HANDOVER-20261010.md` 附录 |
| 常见问题 FAQ | `HANDOVER-20261010.md` 第 9 节 |

---

## 📝 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-10-10 | 创建 INDEX.md 和 HANDOVER-20261010.md；更新 QUICK_START.md |
| 2026-10-10 | 全面核对：新增 `report/verification-20261010.md`、`evidence/E-VERIFY-001.md`；修正 HANDOVER、workitems（WI-009 改回 in_progress，WI-012 改为 partial，新增 WI-013–017）、QUICK_START、INDEX；补全浅克隆历史；未删除任何文件 |
| 2026-10-10 | 合并任务C（PR #3）和任务B收尾（cherry-pick PR #4） |
| 2026-10-10 | 任务B终版统计：89.6% ok（4484/5002） |
| 2026-10-09 | 任务A完成、任务D完成、命令字数值确定 |
