# 梦想世界逆向工程 — 快速开始指南

**欢迎加入！** 请先阅读本文，了解项目背景和你的任务。

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

### 2. 阅读核心文档（必读）
```bash
# 总览（10分钟）
cat work/dream-world-connect-login-map/report/final-summary-20261010.md

# 你的任务相关文档（见任务书）
```

### 3. 创建你的工作区
```bash
# 创建个人工作区（把 <任务名> 替换为你的任务，<你的名字> 替换为你的标识）
mkdir -p work/dream-world-connect-login-map/notes/<任务名>-<你的名字>
mkdir -p work/dream-world-connect-login-map/notes/<任务名>-<你的名字>/artifacts
```

### 4. 开始分析
```bash
# 使用已有工具
python3 tools/mock_server.py --help
python3 tools/packet_analyzer.py --help

# 参考已有分析
cat notes/crypto-analysis-complete.md
```

---

## 📚 核心知识速查

### 加密算法（已破解）
```python
# 使用已有的加密模块
import sys
sys.path.append('work/dream-world-connect-login-map/notes/protocol-artifacts')
from im_crypto import CryptContext, encrypt, decrypt, derive_key

# 示例
ctx = CryptContext()
ctx.init(b'\xaa\xbb\xcc\xdd\xee\xff\x00\x11')  # 8字节密钥
encrypted = encrypt(ctx, b'hello world')
decrypted = decrypt(ctx, encrypted)
```

### FLS脚本解码（已破解）
```python
# 使用解码器
import sys
sys.path.append('work/dream-world-connect-login-map/notes/decoder-artifacts')
from decode_entry516 import extract_entry, xor_decode, MarshalReader

# 解码任意entry（修改 ENTRY_INDEX）
with open('data/script.fls', 'rb') as f:
    archive = f.read()
entry = extract_entry(archive, 516)  # entry 516 = netserver.py
decoded = xor_decode(entry['expanded'])
reader = MarshalReader(decoded)
root = reader.read()
```

### 字节码解码（部分破解）
```python
# 加载映射表
import json
with open('work/dream-world-connect-login-map/notes/co_code_analysis/mapping_table_a_v2.json') as f:
    mapping = json.load(f)['mapping']
# mapping: {"0x55": "0x3C", "0x85": "0x4E", ...}

# 解码字节码
def decode(bytecode):
    return bytes(int(mapping.get(f'0x{b:02X}', f'0x{b:02X}'), 16) for b in bytecode)
```

### 网络工具
```bash
# 模拟服务器
python3 tools/mock_server.py --port 3134 --response-type auto

# 捕获工具
python3 tools/enhanced_capture_server.py --port 3134 --auto-crack

# 数据包分析
python3 tools/packet_analyzer.py capture.bin --report report.md
```

---

## ⚠️ 重要提醒

1. **只读分析**: 不要修改 `mx.exe`, `mxmain.dll`, `IMProtocol.dll`, `data/script.fls` 等原始文件
2. **不连接外部服务器**: 所有分析离线进行，模拟服务器只绑定本地
3. **详细记录**: 每一步都要记录，包括失败的尝试
4. **代码脚本化**: 所有分析写成可重复运行的Python脚本
5. **及时保存**: 分析成果放在自己的工作区，重要发现共享到公共目录

---

## 📞 遇到问题？

1. 先查看 `TASK_DISPATCH.md` 中的"关键参考文件"
2. 查看已有报告：`notes/` 目录下的各种 `*-complete.md`
3. 参考工具文档：`tools/README.md`
4. 查看任务A的详细分析：`notes/co_code_analysis/任务A详细报告.md`

---

**祝分析顺利！** 🎯
