# 任务A进展: Co_code 编码破解 - 映射表构建

**时间**: 2026-10-10
**状态**: 进行中 - 已发现关键模式，部分映射已破解

---

## 重大发现

### 1. 编码方式确认

**co_code 使用字节替换编码（S盒）**，**只有 opcode 字节被编码，参数（2字节小端序）是明文**！

证据:
- `GetPlayerID`: `85 00 00 55` = `LOAD_NAME 0; RETURN_VALUE`
- `SetPlayerID`: `C1 00 00 C4 00 00 8F 00 00 55` = `LOAD_FAST 0; STORE_NAME 0; LOAD_CONST 0; RETURN_VALUE`
- 参数 `00 00`, `01 00` 等是明文小端序整数

### 2. 已破解的映射（5个）

| 编码字节 | 标准字节 | Opcode 名称 | 证据函数 |
|---------|---------|------------|---------|
| 0x55 | 0x3C | RETURN_VALUE | GetPlayerID/SetPlayerID (函数返回) |
| 0x85 | 0x4E | LOAD_NAME | GetPlayerID (return g_iPlayerId) |
| 0x8F | 0x4D | LOAD_CONST | SetPlayerID/Connect (加载None) |
| 0xC1 | 0x62 | LOAD_FAST | SetPlayerID (加载参数) |
| 0xC4 | 0x43 | STORE_NAME | SetPlayerID (存储全局变量) |

### 3. 待破解的未知 Opcode

共 88 种未知 opcode，出现 1328 次

| 编码字节 | 出现次数 | 推测 |
|---------|---------|------|
| 0x00 | 529 |  |
| 0x41 | 70 | 可能是 LOAD_ATTR (0x53)? |
| 0xD9 | 61 | 可能是 CALL_FUNCTION (0x66)? |
| 0x71 | 59 | 可能是 STORE_ATTR (0x48)? |
| 0xDA | 59 | 可能是 LOAD_ATTR (0x53)? |
| 0x01 | 45 | 可能是参数的一部分，或 CALL_FUNCTION (0x66)? |
| 0x05 | 30 |  |
| 0x98 | 30 | 可能是 CALL_FUNCTION (0x66)? |
| 0xE0 | 28 | 可能是 POP_JUMP_IF_FALSE (0x5B)? |
| 0xFB | 23 | 可能是 COMPARE_OP (0x54)? |
| 0xB7 | 22 | 可能是 CALL_FUNCTION (0x66)? |
| 0x02 | 22 |  |
| 0x06 | 16 |  |
| 0x74 | 16 |  |
| 0x0E | 16 |  |
| 0x04 | 14 |  |
| 0xA2 | 14 | 可能是 LOAD_CONST? 但 0x8F 已经是 LOAD_CONST |
| 0x0B | 14 |  |
| 0x08 | 12 |  |
| 0x03 | 11 |  |

## 下一步行动

### 立即行动
1. **在 mx.exe/mxmain.dll 中搜索 S盒映射表**
   - 搜索包含 `sbox[0x85]=0x4E, sbox[0x55]=0x3C, sbox[0xC1]=0x62, sbox[0xC4]=0x43, sbox[0x8F]=0x4D` 的 256 字节表
   - 或搜索逆表

2. **分析更多函数，扩展已知映射**
   - 分析 `getMsg`, `S2CServerRoleInfo`, `C2STransferServer` 等关键函数
   - 利用 names/varnames/consts 上下文推测

3. **尝试部分解码**
   - 用已知5个映射解码，看能理解多少代码

### 搜索 S盒的方法
```python
# 在 mx.exe 中搜索
pattern = bytes([0x4E, ?, ?, ...])  # sbox[0x85] = 0x4E
# 或者搜索逆序
```