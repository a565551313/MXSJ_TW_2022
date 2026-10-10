# 梦想世界逆向工程 — 快速开始指南

**欢迎加入！** 请先阅读本文，了解项目背景和你的任务。

> ⭐ **新接手的 agent 请先阅读交接文档**: [`HANDOVER-20261010.md`](HANDOVER-20261010.md)（项目交接文档，含完整进度、文件路径、工具手册）

---

## 🚀 5分钟快速上手

### 1. 了解项目
```bash
# 进入项目目录
cd /home/user/MXSJ_TW_2022

# 查看项目结构
ls -la

# 查看工作区（已有成果）
ls work/dream-world-connect-login-map/
```

### 2. 阅读核心文档（必读，按顺序）

| 序号 | 文档 | 内容 | 时间 |
|-----|------|------|------|
| 1 | **`HANDOVER-20261010.md`** | ⭐ 项目交接文档（必读！） | 20分钟 |
| 2 | `report/final-summary-20261010.md` | 项目最终总结 | 15分钟 |
| 3 | `TASK_DISPATCH.md` | 任务分派总纲 | 10分钟 |
| 4 | `task-briefs/TASK-X-xxx.md` | 你的具体任务书 | 10分钟 |

### 3. 创建你的工作区
```bash
# 创建个人工作区（把 <任务名> 替换为你的任务）
mkdir -p work/dream-world-connect-login-map/notes/<任务名>-<你的标识>/artifacts
```

### 4. 开始分析
```bash
# 使用已有工具（详见 HANDOVER-20261010.md 第 6 节 工具使用手册）
python3 tools/fls_batch_decoder.py --help      # FLS 批量解码器 v7
python3 tools/pymarshal_dis.py --help           # Python 2 marshal 反汇编
python3 tools/mock_server.py --help             # 模拟服务器
python3 tools/packet_analyzer.py --help         # 数据包分析
python3 tools/map_parser.py --help              # 地图解析器
python3 tools/data_browser/app.py --help        # 数据浏览器
```

---

## 📚 核心知识速查

### 加密算法（已破解 ✅）
```python
import sys
sys.path.append('work/dream-world-connect-login-map/notes/protocol-artifacts')
from im_crypto import CryptContext, encrypt, decrypt, derive_key

ctx = CryptContext()
ctx.init(b'\xaa\xbb\xcc\xdd\xee\xff\x00\x11')  # 8字节密钥
encrypted = encrypt(ctx, b'hello world')
decrypted = decrypt(ctx, encrypted)
```

### FLS脚本解码（已破解 ✅）
```bash
# 批量解码（v7，推荐）
python3 tools/fls_batch_decoder.py --entry 516 --input data/script.fls

# 全量解码结果已在:
# work/.../task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl
```

### 字节码映射表（v4.3 ✅）
```python
import json
# 最新映射表（v4.3，含重大纠正）
with open('work/dream-world-connect-login-map/notes/co_code_analysis/mapping_table_v4.json') as f:
    data = json.load(f)
# table_a: 43个映射, table_b: 5个（含多变体）, v3_corrections: 6个纠正
```

> ⚠️ **重要**: v4.3 纠正了 4 处误判（0x98→STORE_NAME, 0xE0→IMPORT_NAME, 0xFB→MAKE_FUNCTION, 0x42→BUILD_CLASS）

### 协议帧格式（已确认 ✅）
```
[加密( uint16_be(总长度,含长度字段本身2字节) + uint16_be(命令字) + payload )]
```

### 命令字（C→S 已确认 ✅）
| 命令字 | 名称 |
|--------|------|
| 0x0001 | loginhello (LOGIN_HELLO) |
| 0x0002 | TEST_HELLO |
| 0x0003 | RESELECT_HELLO |
| 0x0010 | C2GS_SELECT_SERVER |
| 0x00FF | HEARTBEAT |

详见: `notes/protocol-commands-values.md`

---

## 🛠️ 工具速查

| 工具 | 路径 | 用途 |
|------|------|------|
| FLS 批量解码器 v7 | `tools/fls_batch_decoder.py` | 解码 script.fls 全部 5002 条目 |
| Python 2 marshal 反汇编 | `tools/pymarshal_dis.py` | 反汇编 marshal 数据 |
| 加密/解密 | `notes/protocol-artifacts/im_crypto.py` | IMProtocol 加密算法 |
| 模拟服务器 | `tools/mock_server.py` | 本地模拟服务器框架 |
| 数据包分析 | `tools/packet_analyzer.py` | 分析捕获的数据包 |
| 地图解析器 | `tools/map_parser.py` | 解析 .map 文件 |
| 地图查看器 | `tools/map_viewer.py` / `map_gui.py` | 查看地图 |
| 通用 FLS 工具 | `tools/data-parser/universal_fls_tool.py` | 6 种 FLS 归档解包/重打包 |
| 数据浏览器 | `tools/data_browser/app.py` | Web 数据浏览器（端口 8080） |

**详见**: `HANDOVER-20261010.md` 第 6 节 工具使用手册

---

## ⚠️ 重要提醒

1. **只读分析**: 不要修改 `mx.exe`, `mxmain.dll`, `IMProtocol.dll`, `data/script.fls` 等原始文件
2. **不连接外部服务器**: 所有分析离线进行，模拟服务器只绑定本地 `127.0.0.1`
3. **工作分支**: `arena/6fbb3403-mxsj-tw-2022`（不要切换分支）
4. **详细记录**: 每一步都要记录，包括失败的尝试
5. **代码脚本化**: 所有分析写成可重复运行的 Python 脚本
6. **及时保存**: 分析成果放在自己的工作区，重要发现共享到公共目录
7. **中文文件名**: `git config core.quotepath false`（如遇乱码）

---

## 📞 遇到问题？

1. **先查交接文档**: `HANDOVER-20261010.md`（含常见问题 FAQ）
2. **查任务进度**: `HANDOVER-20261010.md` 第 2 节
3. **查关键文件路径**: `HANDOVER-20261010.md` 第 5 节
4. **查工具使用**: `HANDOVER-20261010.md` 第 6 节
5. **查已有报告**: `notes/` 目录下的各任务报告

---

**祝分析顺利！** 🎯
