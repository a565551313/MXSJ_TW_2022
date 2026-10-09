# Co_code 编码深入分析报告

**分析时间**: 2026-10-10
**目标**: 破解 `script\login\netserver.py` 的 co_code 自定义编码

---

## 1. 关键发现

### 1.1 编码类型推测

基于字节码模式分析，**co_code 使用了字节替换编码（S盒）**，而不是简单的 XOR/ADD。**

证据:
1. **参数部分未被编码**: 观察到 `00 00`, `01 00`, `03 00`, `04 00` 等小端序整数作为参数，这些是明文
2. **只有 opcode 字节被编码**: 位置为 3n 的字节（假设3字节一条指令）呈现非标准值
3. **重复模式**: `BB`, `C4`, `8F` 等字节高频出现，对应常见的 Python opcode
4. **简单转换无效**: XOR、ADD 等简单转换无法达到 100% 标准 opcode 比例

### 1.2 字节码结构

```
每条指令 3 字节: [编码的opcode] [参数低字节] [参数高字节]
```

### 1.3 推测的 Opcode 映射

| 编码字节 | 出现次数 | 推测含义 | 可能的标准 Opcode |
|---------|---------|---------|------------------|
| 0xC4 | 22 | STORE_NAME or STORE_GLOBAL (高频，存储操作) | |
| 0xBB | 2 | LOAD_GLOBAL or LOAD_NAME (高频，加载操作) | |
| 0x8F | 110 | POP_TOP or CALL_FUNCTION (高频，常用操作) | |
| 0x85 | 35 | LOAD_FAST or LOAD_CONST (中频) | |
| 0xC1 | 95 | STORE_FAST (中频) | |
| 0x95 | 9 | LOAD_GLOBAL (中频) | |
| 0x98 | 5 | CALL_FUNCTION (中频) | |

## 2. 下一步行动

### 2.1 短期（立即）
1. **在 mx.exe/mxmain.dll 中搜索 S盒/映射表**
   - 搜索 256 字节的连续数据，可能是 opcode 替换表
   - 寻找 `Py_Uncompress` 或类似的解码函数

2. **频率分析破解**
   - 对比标准 Python 2.7 字节码的 opcode 频率分布
   - 利用已知函数（如 `GetPlayerID` 应该只有 `LOAD_FAST` + `RETURN_VALUE`）

3. **已知明文攻击**
   - `GetPlayerID` 字节码只有 4 字节: `85 00 00 55`
   - 推测: `LOAD_FAST 0` + `RETURN_VALUE`
   - 即: 0x85 = LOAD_FAST (0x62), 0x55 = RETURN_VALUE (0x3C) ?

### 2.2 中期
4. **完整破解映射表后，反编译所有函数**
5. **理解 ProcessServerCmd 的完整逻辑**

### 2.3 寻找原生解码函数
6. **在 mx.exe 中定位 co_code 解码函数**
   - 可能在 `Py_Uncompress` 或类似函数中
   - 可能在加载 FLS 脚本时进行转换