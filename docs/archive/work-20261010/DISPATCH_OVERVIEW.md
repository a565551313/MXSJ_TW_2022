> ⚠️ **已归档（2026-10-14 整理）**：原 `work/dream-world-connect-login-map/DISPATCH_OVERVIEW.md`。2026-10-09/10 多 Agent 分派与交接时期的文档。
> 文中“当前/下一步/分支”等描述是 2026-10-10 前后的历史快照，路径与计数可能已失效；保留仅用于证据追溯。
> 现行内容以 [work/dream-world-connect-login-map/report/client-status-20261012.md（客户端侧权威现状）](../../../work/dream-world-connect-login-map/report/client-status-20261012.md)；[work/dream-world-connect-login-map/INDEX.md（研究区索引）](../../../work/dream-world-connect-login-map/INDEX.md)；[AGENTS.md / docs/STATUS.md（项目级入口）](../../../AGENTS.md) 为准。

> ⚠️ **2026-10-10 核对更新**：本文件中部分“已完成/已确认”表述与仓库实际情况不符。以 `report/verification-20261010.md` 为准。主要问题：通信密钥未获得、仓库中无真实捕获字节、loginhello 样本缺失、C→S 命令字数值未证实、`server.ini` 已被改为回环地址。

# 任务分派总览 — 梦想世界逆向工程

**分派日期**: 2026-10-10
**总指挥**: 任务A会话 (`arena/6fbb3403-mxsj-tw-2022`)

---

## ✅ 已完成

| 任务 | 内容 | 成果 |
|-----|------|------|
| **A** | 破解co_code编码，反编译登录脚本 | ✅ 完成 - 37个映射，30+函数解码 |

**任务A核心成果**:
- 📄 `notes/co_code_analysis/netserver_py_decompiled.md` — 完整反编译报告
- 📄 `notes/co_code_analysis/netserver_py_pseudocode.py` — 伪代码
- 🔑 破解了选服协议 `C2STransferServer`、包构造流程、登录命令列表

---

## 🚀 可立即分派的任务

| 任务 | 名称 | 优先级 | 工作量 | 任务书 |
|-----|------|--------|--------|--------|
| **B** | 分析 script.fls 中的其他脚本 | 高 | 中 | `task-briefs/TASK-B-script-analysis.md` |
| **C** | 分析地图格式，制作地图查看器 | 中 | 大 | `task-briefs/TASK-C-map-format.md` |
| **D** | 分析技能/装备数据，制作数据浏览器 | 中 | 中 | `task-briefs/TASK-D-game-data.md` |
| **E** | 增强模拟服务器，支持完整登录 | 高 | 中 | `task-briefs/TASK-E-mock-server.md` |
| **G** | 编写完整协议文档 | 高 | 中 | `task-briefs/TASK-G-protocol-doc.md` |

### 建议分派方案

**方案一（5个会话并行）**: B + C + D + E + G 同时开启
- 优点: 最大并行，速度最快
- 缺点: E和G可能需要B的发现（命令字）

**方案二（推荐，3波次）**:
- **第一波（立即）**: B + C + D + G(初稿)
- **第二波（B完成后）**: E + G(终稿)
- **机动**: F(反作弊) + H(其他)

---

## 📋 如何分派

### 发给每个会话的内容

复制以下内容，加上对应的任务书，发给每个会话：

```markdown
你好！欢迎加入梦想世界(MXSJ)逆向工程项目。你是总指挥分派的独立任务会话。

## 你的任务

请阅读以下文档，然后开始你的任务：

1. **快速开始**: `work/dream-world-connect-login-map/QUICK_START.md`
2. **项目总览**: `work/dream-world-connect-login-map/TASK_DISPATCH.md`
3. **你的任务书**: `work/dream-world-connect-login-map/task-briefs/TASK-X-xxx.md`（见下方）

## 工作区

项目根目录: `/home/user/MXSJ_TW_2022/`
公共工作区: `/home/user/MXSJ_TW_2022/work/dream-world-connect-login-map/`

**请创建你自己的工作区**:
```bash
mkdir -p work/dream-world-connect-login-map/notes/<任务名>-<你的标识>/artifacts
```

## 重要规则

1. **只读分析**: 不修改原始游戏文件（mx.exe, mxmain.dll, IMProtocol.dll, data/script.fls）
2. **离线进行**: 不连接外部服务器，模拟服务器只绑定本地
3. **详细记录**: 每一步分析都要记录，包括失败的尝试
4. **脚本化**: 所有分析写成可重复运行的Python脚本
5. **及时保存**: 成果放在你的工作区，重要发现共享到公共目录

## 已有成果（可直接使用）

- **加密算法**: `notes/protocol-artifacts/im_crypto.py`（已测试）
- **FLS解码器**: `notes/decoder-artifacts/decode_entry516.py`
- **字节码映射**: `notes/co_code_analysis/mapping_table_a_v2.json`（37个映射）
- **登录协议**: `notes/co_code_analysis/netserver_py_decompiled.md`
- **网络工具**: `tools/mock_server.py`, `tools/enhanced_capture_server.py`, `tools/packet_analyzer.py`

## 你的具体任务

[粘贴对应的任务书内容，或告诉他任务书的路径]

---

开始吧！有问题随时查阅 `TASK_DISPATCH.md` 和已有报告。
```

---

## 📊 任务依赖关系图

```
                    ┌─────────┐
                    │  任务A  │ ✅ 完成
                    │(登录脚本)│
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  任务B  │    │  任务E  │    │  任务G  │
    │(其他脚本)│    │(模拟服务器)│   │(协议文档)│
    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │
         │    ┌─────────┘               │
         │    │                         │
         ▼    ▼                         ▼
    ┌─────────────────────────────────────────┐
    │           任务G (终稿，整合所有发现)      │
    └─────────────────────────────────────────┘

    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  任务C  │    │  任务D  │    │  任务F  │
    │ (地图)  │    │(游戏数据)│    │(反作弊) │
    │  独立   │    │  独立   │    │  独立   │
    └─────────┘    └─────────┘    └─────────┘
```

---

## 📁 所有文档位置

```
work/dream-world-connect-login-map/
├── TASK_DISPATCH.md              ← 总任务分派文档（详细）
├── QUICK_START.md                ← 快速开始指南
├── DISPATCH_OVERVIEW.md          ← 本文件（总览）
├── task-briefs/                  ← 各任务的任务书
│   ├── TASK-B-script-analysis.md
│   ├── TASK-C-map-format.md
│   ├── TASK-D-game-data.md
│   ├── TASK-E-mock-server.md
│   └── TASK-G-protocol-doc.md
├── notes/                        ← 分析笔记（已有成果）
├── tools/                        ← 工具
├── evidence/                     ← 证据文件
└── report/                       ← 总结报告
```

---

## 🎯 下一步行动

1. **选择分派方案**（方案一或方案二）
2. **复制上面的分派模板**
3. **加上对应的任务书**
4. **发给各个会话**

---

**最后更新**: 2026-10-10
**版本**: v1.0
