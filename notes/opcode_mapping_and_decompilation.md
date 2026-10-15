# 《夢想世界》(MXSJ TW 2022) Python 字節碼定製混淆還原與批量反編譯技術報告

## 1. 核心架構發現：雙定製 Python 虛擬機體系

通過對客戶端主程序 `mx.exe` / `mxmain.dll` 與 `exe/python27.dll` / `exe/python27_dy.dll` 的白盒反匯編分析，我們徹底釐清了《夢想世界》（台灣版 v2.27.2）的腳本執行架構：**客戶端同時包含兩套不同版本、不同字節碼結構、不同 Opcode 置換表的定製 Python 虛擬機**：

| 特性維度 | VM #1：主遊戲邏輯腳本虛擬機 (`data/script.fls`) | VM #2：啟動器與基礎庫虛擬機 (`data/data.fls`) |
| :--- | :--- | :--- |
| **宿主二進制文件** | `mx.exe` / `mxmain.dll` (SHA256: `637331b5...`) | `exe/python27.dll` / `exe/python27_dy.dll` |
| **基礎 Python 版本** | **Python 2.5** (標準 `.pyc` Magic: `b3 f2 0d 0a`) | **Python 2.7.13** (標準 `.pyc` Magic: `03 f3 0d 0a`) |
| **解釋器核心函數** | `PyEval_EvalFrameEx` @ VA `0x004E7460` | `PyEval_EvalFrame` @ VA `0x1E12A380` |
| **Switch 跳轉表地址** | Jump Table @ `0x004EA308` (98 項)<br>Index Table @ `0x004EA490` (252 字節) | Jump Table @ `0x1E12CA48` (105 項)<br>Index Table @ `0x1E12CBF8` (248 字節) |
| **`HAVE_ARGUMENT` 閾值** | **`0x5F` (95)** (`0x004E74D1: cmp edx, 0x5f`) | **`0x5A` (90)** (`0x1E12A48E: cmp eax, 0x5a`) |
| **`PyCodeObject` Header** | 標準 16 字節 (`argcount, nlocals, stacksize, flags`) | **20 字節**：新增 4 字節 `co_extra` (`op_stream_len`) |
| **`co_code` 存儲結構** | 標準交錯流（無參數 1B，帶參數 3B `<op> <lo> <hi>`） | **指令/參數雙流分離結構 (Split-Stream)** |
| **`co_lnotab` 編碼** | 標準字節偏移增量 (`byte_delta, line_delta`) | **指令索引增量 (`op_idx_delta, line_delta`)** |
| **外層容器與加密** | `0SLF` 歸檔 + `zlib` 壓縮 + **5 段式動態 XOR** (`0x00457C20`) | 定製 ZIP 歸檔 (`data.fls`)，內含 121 個明文 `.pyo` |

---

## 2. VM #1 (`data/script.fls` / `mxmain.dll`) 逆向推導與完整 Opcode 映射表

### 2.1 `PyEval_EvalFrameEx` (`0x004E7460`) 取指與分發機制

在 `mxmain.dll` (與 `mx.exe` 完全一致) 中，通過交叉引用字符串 `"unknown opcode"` (`0x0085DD54`) 定位到 `PyEval_EvalFrameEx` (`0x004E7460`)。其取指核心匯編如下：

```x86asm
0x004e74bd: movzx  edx, byte ptr [esi]       ; 讀取 1 字節 opcode -> edx
0x004e74c0: add    esi, 1                    ; next_instr += 1
0x004e74c3: cmp    edx, 0x5f                 ; HAVE_ARGUMENT = 0x5F (95)!
0x004e74d6: mov    dword ptr [esp+0x14], edx ; 保存當前 opcode
0x004e74da: jl     0x4e74ea                  ; 若 op < 0x5F，無參數
0x004e74dc: movzx  eax, byte ptr [esi+1]     ; 讀取參數高字節
0x004e74e0: movzx  ecx, byte ptr [esi]       ; 讀取參數低字節
0x004e74e3: shl    eax, 8
0x004e74e6: add    edi, eax                  ; oparg = (hi << 8) | lo (小端 uint16)
0x004e74e8: add    esi, 2                    ; next_instr += 2
0x004e74ea: cmp    edx, 0xfb                 ; 最大有效 opcode = 0xFB (251)
0x004e74f0: ja     0x4e96f7                  ; default -> "unknown opcode"
0x004e74f6: movzx  eax, byte ptr [edx+0x4ea490] ; 查 252 字節索引表
0x004e74fd: jmp    dword ptr [eax*4+0x4ea308]   ; 跳轉至 98 個 case 處理塊
```

這一發現直接推翻了此前文檔中的「多變體 S-Box / 參數二次混淆」假設：
1. **為何此前反匯編器會在 `0x5A..0x5E` 處失步**：多益將 `HAVE_ARGUMENT` 從標準的 `0x5A` (90) 上調至 `0x5F` (95)，因此 `0x5A` (`ROT_THREE = 2`)、`0x5B` (`DELETE_GLOBAL = 79`)、`0x5E` (`YIELD_VALUE = 86`) 均為 **1 字節無參數指令**。若按 `>= 0x5A` 吞掉後續 2 字節，指令流必然失步。
2. **為何 `0xB7` / `0xE3` 後總是緊跟 `0x41` (`POP_TOP`)**：`mx.exe` 基於 **Python 2.5** 而非 Python 2.7。在 Python 2.5 中，條件跳轉是相對跳轉 `JUMP_IF_FALSE` (111) 和 `JUMP_IF_TRUE` (112)，不彈出棧頂元素，編譯器會在每個分支開頭顯式生成 `POP_TOP` (`0x41`)。
3. **`SETUP_LOOP` / `SETUP_EXCEPT` / `SETUP_FINALLY` 的精確區分**：`0xD3`、`0xCF`、`0xD6` 在 Jump Table 中共用入口 `0x004E8E15` (`PyFrame_BlockSetup(f, opcode, target, level)`)，但在異常展開與 `BREAK_LOOP` 的 `fast_block_end` 塊 (`0x004E9825`, `0x004E9912`) 中：
   - `cmp eax, 0xd3` (`0x004E9825`) 專門匹配循環塊 (`SETUP_LOOP = 120`)；
   - `cmp eax, 0xcf` (`0x004E9912`) 專門匹配異常捕獲塊 (`SETUP_EXCEPT = 121`)；
   - `cmp eax, 0xd6` (`0x004E9850`) 專門匹配 finally 塊 (`SETUP_FINALLY = 122`)。

### 2.2 `data/script.fls` (Python 2.5) 完整 Opcode 映射表 (`PY25_MAP`，共 106 個指令)

| 多益 Opcode | 10進制 | `mxmain.dll` Handler VA | 標準 Py2.5 Opcode | 標準值 | 參數說明 / 逆向驗證依據 |
| :---: | :---: | :---: | :--- | :---: | :--- |
| `0x00` | 0 | `0x004E7504` | `NOP` | 9 | 無操作，直接跳回取指循環 |
| `0x01` | 1 | `0x004E79E8` | `INPLACE_LSHIFT` | 75 | 調用 `PyNumber_InPlaceLshift` |
| `0x03` | 3 | `0x004E7840` | `BINARY_FLOOR_DIVIDE` | 26 | 調用 `PyNumber_FloorDivide` |
| `0x05` | 5 | `0x004E7C14` | `STORE_SUBSCR` | 60 | 調用 `PyObject_SetItem` |
| `0x06` | 6 | `0x004E7559` | `ROT_FOUR` | 3 | 交換棧頂 4 個元素 |
| `0x07` | 7 | `0x004E794E` | `INPLACE_FLOOR_DIVIDE` | 28 | 調用 `PyNumber_InPlaceFloorDivide` |
| `0x08` | 8 | `0x004E8202` | `IMPORT_STAR` | 84 | 調用 `import_all_from` |
| `0x09` | 9 | `0x004E768F` | `BINARY_MULTIPLY` | 20 | 調用 `PyNumber_Multiply` |
| `0x0A` | 10 | `0x004E81BE` | `PRINT_ITEM_TO` | 73 | 帶流對象的 `print >>` |
| `0x0B` | 11 | `0x004E815B` | `PRINT_ITEM` | 71 | 標準 `print item` |
| `0x0C` | 12 | `0x004E7D31` | `SLICE+0` | 30 | `apply_slice(v, NULL, NULL)` (`edx - 0x0c`) |
| `0x0D` | 13 | `0x004E7D31` | `SLICE+1` | 31 | `apply_slice(v, w, NULL)` |
| `0x0E` | 14 | `0x004E7D31` | `SLICE+2` | 32 | `apply_slice(v, NULL, w)` |
| `0x0F` | 15 | `0x004E7D31` | `SLICE+3` | 33 | `apply_slice(v, v2, w)` |
| `0x10` | 16 | `0x004E9314` | `END_FINALLY` | 88 | 結束 `finally` 塊並重拋異常或跳轉 |
| `0x11` | 17 | `0x004E7642` | `BINARY_POWER` | 19 | 調用 `PyNumber_Power` |
| `0x12` | 18 | `0x004E7581` | `UNARY_POSITIVE` | 10 | 調用 `PyNumber_Positive` |
| `0x15` | 21 | `0x004E75CE` | `UNARY_NOT` | 12 | `PyObject_IsTrue` 取反 |
| `0x18` | 24 | `0x004E7C44` | `DELETE_SUBSCR` | 61 | `PyObject_DelItem` |
| `0x19` | 25 | `0x004E7A82` | `INPLACE_AND` | 77 | `PyNumber_InPlaceAnd` |
| `0x1A` | 26 | `0x004E8E49` | `WITH_CLEANUP` | 81 | 查找 `__exit__` (`0x0085DBA4`) |
| `0x1B` | 27 | `0x004E81FC` | `PRINT_NEWLINE_TO` | 74 | 帶流對象的 `print >>` 換行 |
| `0x1D` | 29 | `0x004E7541` | `ROT_TWO` | 5 | 實際為 `DUP_TOPX` 前置 / 棧複製 |
| `0x1F` | 31 | `0x004E8189` | `PRINT_NEWLINE` | 72 | 輸出 `\n` |
| `0x20` | 32 | `0x004E7B6A` | `BINARY_OR` | 66 | `PyNumber_Or` |
| `0x21` | 33 | `0x004E82AD` | `EXEC_STMT` | 85 | 調用 `exec_statement` |
| `0x23` | 35 | `0x004E77DE` | `BINARY_SUBTRACT` | 24 | 整數快速路徑 `sub` + `PyNumber_Subtract` |
| `0x24` | 36 | `0x004E7A35` | `INPLACE_RSHIFT` | 76 | `PyNumber_InPlaceRshift` |
| `0x27` | 39 | `0x004E7B1D` | `BINARY_XOR` | 65 | `PyNumber_Xor` |
| `0x28` | 40 | `0x004E7EB9` | `DELETE_SLICE+0` | 50 | `assign_slice(..., NULL)` (`edx - 0x28`) |
| `0x29` | 41 | `0x004E7EB9` | `DELETE_SLICE+1` | 51 | `DELETE_SLICE+1` |
| `0x2A` | 42 | `0x004E7EB9` | `DELETE_SLICE+2` | 52 | `DELETE_SLICE+2` |
| `0x2B` | 43 | `0x004E7EB9` | `DELETE_SLICE+3` | 53 | `DELETE_SLICE+3` |
| `0x2C` | 44 | `0x004E761B` | `UNARY_CONVERT` | 13 | `PyObject_Repr` (反引號 `` `x` ``) |
| `0x30` | 48 | `0x004E7531` | `DUP_TOP` | 4 | 複製棧頂元素並 `Py_INCREF` |
| `0x32` | 50 | `0x004E78B5` | `INPLACE_POWER` | 67 | `PyNumber_InPlacePower` |
| `0x33` | 51 | `0x004E7C95` | `INPLACE_MODULO` | 58 | `PyNumber_InPlaceRemainder` |
| `0x36` | 54 | `0x004E921E` | `GET_ITER` | 68 | `PyObject_GetIter` |
| `0x37` | 55 | `0x004E7727` | `BINARY_MODULO` | 22 | `PyNumber_Remainder` / `PyString_Format` |
| `0x38` | 56 | `0x004E8285` | `LOAD_LOCALS` | 82 | 加載 `f->f_locals` |
| `0x3A` | 58 | `0x004E7CE2` | `INPLACE_DIVIDE` | 59 | `PyNumber_InPlaceDivide` |
| `0x3B` | 59 | `0x004E799B` | `INPLACE_TRUE_DIVIDE` | 29 | `PyNumber_InPlaceTrueDivide` |
| `0x3D` | 61 | `0x004E76DC` | `BINARY_DIVIDE` | 21 | `PyNumber_Divide` |
| `0x3E` | 62 | `0x004E7AD0` | `BINARY_AND` | 64 | `PyNumber_And` |
| `0x3F` | 63 | `0x004E776B` | `BINARY_ADD` | 23 | 整數快速路徑 `add` + 字符串拼接 + `PyNumber_Add` |
| `0x40` | 64 | `0x004E8DFC` | `POP_BLOCK` | 87 | `PyFrame_BlockPop` |
| `0x41` | 65 | `0x004E7509` | `POP_TOP` | 1 | 彈出棧頂並 `Py_DECREF` |
| `0x42` | 66 | `0x004E93AB` | `BUILD_CLASS` | 89 | 調用 `build_class` |
| `0x43` | 67 | `0x004E7CBA` | `INPLACE_ADD` | 55 | 整數快速路徑 + 字符串就地拼接 + `PyNumber_InPlaceAdd` |
| `0x44` | 68 | `0x004E7ACF` | `INPLACE_XOR` | 78 | `PyNumber_InPlaceXor` |
| `0x45` | 69 | `0x004E75A7` | `UNARY_NEGATIVE` | 11 | `PyNumber_Negative` |
| `0x46` | 70 | `0x004E7DD0` | `BINARY_RSHIFT` | 63 | `PyNumber_Rshift` |
| `0x47` | 71 | `0x004E8321` | `BREAK_LOOP` | 80 | `why = WHY_BREAK` (16) |
| `0x48` | 72 | `0x004E7E1D` | `STORE_SLICE+0` | 40 | `assign_slice` (`edx - 0x48`) |
| `0x49` | 73 | `0x004E7E1D` | `STORE_SLICE+1` | 41 | `STORE_SLICE+1` |
| `0x4A` | 74 | `0x004E7E1D` | `STORE_SLICE+2` | 42 | `STORE_SLICE+2` |
| `0x4B` | 75 | `0x004E7E1D` | `STORE_SLICE+3` | 43 | `STORE_SLICE+3` |
| `0x4C` | 76 | `0x004E7C70` | `INPLACE_MULTIPLY` | 57 | `PyNumber_InPlaceMultiply` |
| `0x4D` | 77 | `0x004E7FE9` | `LIST_APPEND` | 18 | `PyList_Append` (列表推導式專用) |
| `0x4E` | 78 | `0x004E788D` | `BINARY_TRUE_DIVIDE` | 27 | `PyNumber_TrueDivide` |
| `0x53` | 83 | `0x004E80FE` | `PRINT_EXPR` | 70 | 交互式表達式打印 |
| `0x54` | 84 | `0x004E77B6` | `UNARY_INVERT` | 15 | `PyNumber_Invert` (`~x`) |
| `0x55` | 85 | `0x004E829E` | `RETURN_VALUE` | 83 | `why = WHY_RETURN` (8) |
| `0x56` | 86 | `0x004E7DA9` | `BINARY_LSHIFT` | 62 | `PyNumber_Lshift` |
| `0x57` | 87 | `0x004E7D48` | `INPLACE_SUBTRACT` | 56 | `PyNumber_InPlaceSubtract` |
| `0x58` | 88 | `0x004E78FA` | `BINARY_SUBSCR` | 25 | 列表快速索引 + `PyObject_GetItem` |
| `0x5A` | 90 | `0x004E7521` | `ROT_THREE` | 2 | `ROT_TWO` 交換棧頂兩元素（注：`0x1d` 為 `ROT_THREE`） |
| `0x5B` | 91 | `0x004E7BBA` | `INPLACE_OR` | 79 | `PyNumber_InPlaceOr` |
| `0x5E` | 94 | `0x004E82EF` | `YIELD_VALUE` | 86 | 生成器 `yield` (`why = WHY_YIELD = 64`) |
| `0x61` | 97 | `0x004E80D5` | `DELETE_GLOBAL` | 98 | `PyDict_DelItem(f_globals, name)` |
| `0x6C` | 108 | `0x004E855F` | `UNPACK_SEQUENCE` | 92 | 元組/列表解包 `unpack_iterable` |
| `0x71` | 113 | `0x004E7FB4` | `STORE_FAST` | 125 | 寫入局部變量槽 `f_localsplus[oparg]` |
| `0x72` | 114 | `0x004E89B4` | `LOAD_DEREF` | 136 | `PyCell_Get(freevars[oparg])` |
| `0x7E` | 126 | `0x004E9520` | `BUILD_SLICE` | 133 | `PySlice_New` |
| `0x83` | 131 | `0x004E7FF6` | `DELETE_FAST` | 126 | 刪除局部變量槽 |
| `0x85` | 133 | `0x004E88B8` | `LOAD_GLOBAL` | 116 | 查 `f_globals` 與 `f_builtins` |
| `0x8B` | 139 | `0x004E96CF` | `EXTENDED_ARG` | 143 | `oparg = (oparg << 16) | next_arg` |
| `0x8F` | 143 | `0x004E8022` | `LOAD_CONST` | 100 | 讀取 `co_consts[oparg]` |
| `0x90` | 144 | `0x004E836D` | `RAISE_VARARGS` | 130 | `do_raise(argc)` |
| `0x91` | 145 | `0x004E8980` | `LOAD_CLOSURE` | 135 | 壓入閉包 Cell 對象 |
| `0x95` | 149 | `0x004E8B63` | `COMPARE_OP` | 106 | `cmp_outcome` (`<, <=, ==, !=, >, >=, in, not in, is, is not, exc`) |
| `0x98` | 152 | `0x004E83C6` | `STORE_NAME` | 90 | 存入 `f_locals[name]` |
| `0xA2` | 162 | `0x004E8DA4` | `JUMP_ABSOLUTE` | 113 | `esi = co_code + oparg` |
| `0xAA` | 170 | `0x004E87CB` | `LOAD_NAME` | 101 | 依次查找 `f_locals`, `f_globals`, `f_builtins` |
| `0xAD` | 173 | `0x004E9187` | `IMPORT_FROM` | 108 | `import_from(v, name)` |
| `0xAF` | 175 | `0x004E9267` | `FOR_ITER` | 93 | 調用 `tp_iternext`，結束時跳轉 `+oparg` |
| `0xB7` | 183 | `0x004E8C7D` | `JUMP_IF_FALSE` | 111 | Py2.5 相對條件跳轉（不彈棧） |
| `0xBB` | 187 | `0x004E879E` | `BUILD_MAP` | 104 | `PyDict_New()` |
| `0xBC` | 188 | `0x004E7F74` | `DUP_TOPX` | 99 | 複製棧頂 `oparg` 個元素 (`oparg == 2 or 3`) |
| `0xBF` | 191 | `0x004E8A19` | `STORE_DEREF` | 137 | `PyCell_Set(freevars[oparg], w)` |
| `0xC1` | 193 | `0x004E7F43` | `LOAD_FAST` | 124 | 讀取局部變量槽 `f_localsplus[oparg]` |
| `0xC4` | 196 | `0x004E8082` | `STORE_GLOBAL` | 97 | `PyDict_SetItem(f_globals, name, w)` |
| `0xC5` | 197 | `0x004E85FF` | `STORE_ATTR` | 95 | `PyObject_SetAttr(v, name, w)` |
| `0xCA` | 202 | `0x004E873F` | `BUILD_LIST` | 103 | `PyList_New(oparg)` |
| `0xCD` | 205 | `0x004E8330` | `CONTINUE_LOOP` | 119 | `retval = oparg; why = WHY_CONTINUE (32)` |
| `0xCF` | 207 | `0x004E8E15` | `SETUP_EXCEPT` | 121 | `PyFrame_BlockSetup` (在 `0x4e9912` 處匹配 `0xcf`) |
| `0xD3` | 211 | `0x004E8E15` | `SETUP_LOOP` | 120 | `PyFrame_BlockSetup` (在 `0x4e9825` 處匹配 `0xd3`) |
| `0xD6` | 214 | `0x004E8E15` | `SETUP_FINALLY` | 122 | `PyFrame_BlockSetup` (在 `0x4e9850` 處匹配 `0xd6`) |
| `0xD9` | 217 | `0x004E8AA7` | `LOAD_ATTR` | 105 | `PyObject_GetAttr(v, name)` |
| `0xDA` | 218 | `0x004E957E` | `CALL_FUNCTION` | 131 | `call_function(&sp, oparg)` |
| `0xDB` | 219 | `0x004E95E6` | `CALL_FUNCTION_VAR` | 140 | `flags = (edx - 0xdb) + 1` -> `1` (`*args`) |
| `0xDC` | 220 | `0x004E95E6` | `CALL_FUNCTION_KW` | 141 | `flags = 2` (`**kwargs`) |
| `0xDD` | 221 | `0x004E95E6` | `CALL_FUNCTION_VAR_KW` | 142 | `flags = 3` (`*args, **kwargs`) |
| `0xDE` | 222 | `0x004E86DF` | `BUILD_TUPLE` | 102 | `PyTuple_New(oparg)` |
| `0xE0` | 224 | `0x004E9042` | `IMPORT_NAME` | 107 | 查找 `__import__` 並調用 |
| `0xE3` | 227 | `0x004E8D13` | `JUMP_IF_TRUE` | 112 | Py2.5 相對條件跳轉（不彈棧） |
| `0xE4` | 228 | `0x004E84B4` | `DELETE_NAME` | 91 | `PyObject_DelItem(f_locals, name)` |
| `0xE5` | 229 | `0x004E8D9E` | `JUMP_FORWARD` | 110 | `esi += oparg` |
| `0xF1` | 241 | `0x004E867B` | `DELETE_ATTR` | 96 | `PyObject_SetAttr(v, name, NULL)` |
| `0xF2` | 242 | `0x004E9472` | `MAKE_CLOSURE` | 134 | `PyFunction_New` + `PyFunction_SetClosure` |
| `0xFB` | 251 | `0x004E93FC` | `MAKE_FUNCTION` | 132 | `PyFunction_New(v, f_globals)` |

---

## 3. VM #2 (`data/data.fls` / `exe/python27.dll`) 逆向推導與完整 Opcode 映射表

### 3.1 `r_object` (`0x1E14A470`) 與雙流分離 `co_code` 結構

在 `exe/python27.dll` 中，`PyCodeObject` 的反序列化代碼位於 `0x1E14AA42` (`case 'c'`)：
1. 依次讀取 5 個 32 位整數：`co_argcount`、`co_nlocals`、`co_stacksize`、`co_flags` 以及多益新增的 **`co_extra`**（存入結構體偏移 `+0x40`）。
2. 在 `PyEval_EvalFrame` (`0x1E12A380`) 初始化時：
   ```x86asm
   0x1e12a460: mov  ecx, dword ptr [eax+0x40] ; ecx = co->co_extra (指令流長度)
   0x1e12a475: add  eax, 0x14                 ; eax = PyString_AS_STRING(co->co_code) (指令流起點)
   0x1e12a47d: lea  esi, [ecx+eax]            ; esi = co_code + co_extra (16位參數流起點!)
   ```
3. **取指與參數消費規則**：
   - 每次從指令流指針 `ebx` 讀取 1 字節 `opcode` (`ebx += 1`)。
   - 若 `opcode < 0x5A`：無參數，`esi` 不變。
   - 若 `opcode >= 0x5A` 且為**非跳轉指令**：從參數流 `esi` 讀取 1 個 `uint16_le` (`oparg`)，`esi += 2`。
   - 若 `opcode` 為**跳轉或循環塊指令** (`ABS_JUMP_OPS = {0xE2, 0xE7, 0x9A, 0xA6, 0xA2, 0xC1}`, `REL_JUMP_OPS = {0x75, 0x93, 0x88, 0xDF, 0xC2, 0x5F}`)：編譯器在參數流 `esi` 中連續存放了 **2 個 `uint16_le`（共 4 字節）**：
     - 第 1 個 `uint16_le` (`[esi]`)：**目標指令在指令流中的偏移量**（絕對跳轉為目標指令索引 `target_op_idx`；相對跳轉為指令條數增量 `delta_op_count`）。
     - 第 2 個 `uint16_le` (`[esi+2]`)：**目標指令對應的參數流 `uint16` 索引** (`target_arg_idx`)，以便跳轉時同時同步指令指針 `ebx` 與參數指針 `esi` (`0x1E12AD4E: movzx ecx, word ptr [esi+2]; lea esi, [eax+ecx*2]`)！
   - 因此在將雙流結構轉換回標準 Python 2.7 交錯字節碼時，非跳轉帶參指令消費 `args` 流 2 字節，跳轉指令消費 `args` 流 **4 字節**（取第 1 個 `uint16_le` 通過指令偏移映射表 `std_offsets` 換算為標準字節偏移量）。
4. **`co_lnotab` 行號表轉換**：
   - `PyCode_Addr2Line` (`0x1E0DD970`) 直接將 `addrq`（指令索引差）與 `co_lnotab` 的偶數字節累加比較。因此轉換為標準 `.pyc` 時，需將 `co_lnotab` 中的指令索引增量通過 `std_offsets[cur_op_idx]` 轉換為標準字節偏移增量。

### 3.2 `data/data.fls` (Python 2.7.13) 完整 Opcode 映射表 (`PY27_MAP`，共 119 個指令)

以下映射表由 `exe/python27.dll` 的 `PyEval_EvalFrame` (`0x1E12A380`) Jump Table (`0x1E12CA48`) 靜態提取，並與 `data/data.fls` 中全部 121 個模塊（含標準庫 `lib/UserDict.pyo`、`lib/opcode.pyo`、`lib/hashlib.pyo`、`core/gamecode.pyo` 等）進行 100% 字節級交叉驗證：

| 多益 Opcode | 10進制 | `python27.dll` Handler VA | 標準 Py2.7 Opcode | 標準值 | 類別 / 雙流參數消費 |
| :---: | :---: | :---: | :--- | :---: | :--- |
| `0x00`..`0x03` | 0..3 | `0x1E12AC6F` | `DELETE_SLICE+0..+3` | 50..53 | 無參數 (1B) |
| `0x04` | 4 | `0x1E12A7BD` | `INPLACE_DIVIDE` | 59 | 無參數 (1B) |
| `0x05` | 5 | `0x1E12BD97` | `GET_ITER` | 68 | 無參數 (1B) |
| `0x06` | 6 | `0x1E12AF41` | `YIELD_VALUE` | 86 | 無參數 (1B) |
| `0x07` | 7 | `0x1E12A4AF` | `POP_TOP` | 1 | 無參數 (1B) |
| `0x08` | 8 | `0x1E12A8CF` | `INPLACE_LSHIFT` | 75 | 無參數 (1B) |
| `0x09` | 9 | `0x1E12B1AC` | `BREAK_LOOP` | 80 | 無參數 (1B) |
| `0x0B` | 11 | `0x1E12A5B7` | `UNARY_INVERT` | 15 | 無參數 (1B) |
| `0x0C` | 12 | `0x1E12B14D` | `EXEC_STMT` | 85 | 無參數 (1B) |
| `0x10` | 16 | `0x1E12A526` | `UNARY_POSITIVE` | 10 | 無參數 (1B) |
| `0x11` | 17 | `0x1E12A959` | `BINARY_RSHIFT` | 63 | 無參數 (1B) |
| `0x14` | 20 | `0x1E12AA28` | `BINARY_OR` | 66 | 無參數 (1B) |
| `0x15` | 21 | `0x1E12B9BB` | `POP_BLOCK` | 87 | 無參數 (1B) |
| `0x16` | 22 | `0x1E12AB1E` | `DELETE_SUBSCR` | 61 | 無參數 (1B) |
| `0x17` | 23 | `0x1E12A4AA` | `NOP` | 9 | 無參數 (1B，亦用於奇數指令對齊填充) |
| `0x18`..`0x1B` | 24..27 | `0x1E12ABC8` | `SLICE+0..+3` | 30..33 | 無參數 (1B) |
| `0x1C` | 28 | `0x1E12A914` | `BINARY_LSHIFT` | 62 | 無參數 (1B) |
| `0x1D` | 29 | `0x1E12BDAE` | `END_FINALLY` | 88 | 無參數 (1B) |
| `0x1E` | 30 | `0x1E12A733` | `BINARY_TRUE_DIVIDE` | 27 | 無參數 (1B) |
| `0x1F` | 31 | `0x1E12B06F` | `PRINT_ITEM_TO` | 73 | 無參數 (1B) |
| `0x20` | 32 | `0x1E12A4BE` | `ROT_TWO` | 2 | 無參數 (1B) |
| `0x21` | 33 | `0x1E12A9E3` | `INPLACE_OR` | 79 | 無參數 (1B) |
| `0x22` | 34 | `0x1E12A607` | `BINARY_POWER` | 19 | 無參數 (1B) |
| `0x23` | 35 | `0x1E12A88A` | `INPLACE_RSHIFT` | 76 | 無參數 (1B) |
| `0x24` | 36 | `0x1E12A4DE` | `DUP_TOP` | 4 | 無參數 (1B) |
| `0x25` | 37 | `0x1E12A4EB` | `ROT_FOUR` | 5 | 無參數 (1B) |
| `0x27` | 39 | `0x1E12AC8A` | `INPLACE_MODULO` | 58 | 無參數 (1B) |
| `0x28`..`0x2B` | 40..43 | `0x1E12AC55` | `STORE_SLICE+0..+3` | 40..43 | 無參數 (1B) |
| `0x2C` | 44 | `0x1E12AAFD` | `INPLACE_MULTIPLY` | 57 | 無參數 (1B) |
| `0x2E` | 46 | `0x1E12B0AD` | `IMPORT_STAR` | 84 | 無參數 (1B) |
| `0x30` | 48 | `0x1E12A778` | `INPLACE_FLOOR_DIVIDE` | 28 | 無參數 (1B) |
| `0x31` | 49 | `0x1E12A802` | `INPLACE_TRUE_DIVIDE` | 29 | 無參數 (1B) |
| `0x32` | 50 | `0x1E12ACCF` | `INPLACE_POWER` | 67 | 無參數 (1B) |
| `0x33` | 51 | `0x1E12AC07` | `BINARY_ADD` | 23 | 無參數 (1B) |
| `0x35` | 53 | `0x1E12AD17` | `BINARY_SUBTRACT` | 24 | 無參數 (1B) |
| `0x37` | 55 | `0x1E12A549` | `UNARY_NEGATIVE` | 11 | 無參數 (1B) |
| `0x38` | 56 | `0x1E12B03E` | `PRINT_NEWLINE` | 72 | 無參數 (1B) |
| `0x39` | 57 | `0x1E12A64F` | `BINARY_MULTIPLY` | 20 | 無參數 (1B) |
| `0x3A` | 58 | `0x1E12B9EF` | `WITH_CLEANUP` | 81 | 無參數 (1B) |
| `0x3C` | 60 | `0x1E12A99E` | `INPLACE_XOR` | 78 | 無參數 (1B) |
| `0x3D` | 61 | `0x1E12BE40` | `BUILD_CLASS` | 89 | 無參數 (1B) |
| `0x3E` | 62 | `0x1E12AE61` | `BINARY_SUBSCR` | 25 | 無參數 (1B) |
| `0x3F` | 63 | `0x1E12AA6D` | `INPLACE_AND` | 77 | 無參數 (1B) |
| `0x41` | 65 | `0x1E12AEB2` | `BINARY_XOR` | 65 | 無參數 (1B) |
| `0x42` | 66 | `0x1E12AC55` | `STORE_SLICE+2` | 42 | 無參數 (1B) |
| `0x43` | 67 | `0x1E12A694` | `BINARY_DIVIDE` | 21 | 無參數 (1B) |
| `0x45` | 69 | `0x1E12A6D9` | `STORE_MAP` | 54 | 無參數 (1B) |
| `0x46` | 70 | `0x1E12AB48` | `INPLACE_ADD` | 55 | 無參數 (1B) |
| `0x47` | 71 | `0x1E12A4CC` | `ROT_THREE` | 3 | 無參數 (1B) |
| `0x48` | 72 | `0x1E12B125` | `LOAD_LOCALS` | 82 | 無參數 (1B) |
| `0x49` | 73 | `0x1E12A5DF` | `UNARY_CONVERT` | 13 | 無參數 (1B) |
| `0x4A` | 74 | `0x1E12A571` | `UNARY_NOT` | 12 | 無參數 (1B) |
| `0x4C` | 76 | `0x1E12AE1B` | `STORE_SUBSCR` | 60 | 無參數 (1B) |
| `0x50` | 80 | `0x1E12ABA7` | `INPLACE_SUBTRACT` | 56 | 無參數 (1B) |
| `0x51` | 81 | `0x1E12A845` | `BINARY_FLOOR_DIVIDE` | 26 | 無參數 (1B) |
| `0x52` | 82 | `0x1E12B010` | `PRINT_ITEM` | 71 | 無參數 (1B) |
| `0x53` | 83 | `0x1E12B0A7` | `PRINT_NEWLINE_TO` | 74 | 無參數 (1B) |
| `0x54` | 84 | `0x1E12B13E` | `RETURN_VALUE` | 83 | 無參數 (1B) |
| `0x55` | 85 | `0x1E12AFBF` | `PRINT_EXPR` | 70 | 無參數 (1B) |
| `0x56` | 86 | `0x1E12ACDF` | `BINARY_MODULO` | 22 | 無參數 (1B) |
| `0x59` | 89 | `0x1E12AAB2` | `BINARY_AND` | 64 | 無參數 (1B) |
| `0x5A` | 90 | `0x1E12AEF7` | `STORE_FAST` | 125 | 帶參數 (消費 2B `uint16`) |
| `0x5B` | 91 | `0x1E12AF90` | `LOAD_CONST` | 100 | 帶參數 (消費 2B `uint16`) |
| `0x5C` | 92 | `0x1E12B5B7` | `BUILD_LIST` | 103 | 帶參數 (消費 2B `uint16`) |
| `0x5D` | 93 | `0x1E12BFAF` | `BUILD_SLICE` | 133 | 帶參數 (消費 2B `uint16`) |
| `0x5F` | 95 | `0x1E12C15B` | `SETUP_WITH` | 143 | **相對跳轉塊** (消費 **4B**: 2×`uint16`) |
| `0x64` | 100 | `0x1E12AFE5` | `MAP_ADD` | 147 | 帶參數 (消費 2B `uint16`) |
| `0x70` | 112 | `0x1E12B251` | `STORE_NAME` | 90 | 帶參數 (消費 2B `uint16`) |
| `0x75` | 117 | `0x1E12BDDD` | `FOR_ITER` | 93 | **相對跳轉** (消費 **4B**: 2×`uint16`) |
| `0x79` | 121 | `0x1E12BEF7` | `MAKE_CLOSURE` | 134 | 帶參數 (消費 2B `uint16`) |
| `0x7C` | 124 | `0x1E12BAFF` | `IMPORT_NAME` | 107 | 帶參數 (消費 2B `uint16`) |
| `0x82` | 130 | `0x1E12B4AF` | `STORE_ATTR` | 95 | 帶參數 (消費 2B `uint16`) |
| `0x87` | 135 | `0x1E12BC74` | `IMPORT_FROM` | 108 | 帶參數 (消費 2B `uint16`) |
| `0x88` | 136 | `0x1E12B9D4` | `SETUP_LOOP` | 120 | **相對跳轉塊** (消費 **4B**: 2×`uint16`) |
| `0x89` | 137 | `0x1E12B961` | `LOAD_ATTR` | 105 | 帶參數 (消費 2B `uint16`) |
| `0x8A` | 138 | `0x1E12B503` | `DELETE_ATTR` | 96 | 帶參數 (消費 2B `uint16`) |
| `0x8B` | 139 | `0x1E12AF61` | `DELETE_FAST` | 126 | 帶參數 (消費 2B `uint16`) |
| `0x93` | 147 | `0x1E12AE97` | `JUMP_FORWARD` | 110 | **相對跳轉** (消費 **4B**: 2×`uint16`) |
| `0x9A` | 154 | `0x1E12B721` | `POP_JUMP_IF_FALSE` | 114 | **絕對跳轉** (消費 **4B**: 2×`uint16`) |
| `0x9B` | 155 | `0x1E12B9AD` | ` COMPARE_OP` | 107 | 帶參數 (消費 2B `uint16`) |
| `0x9C` | 156 | `0x1E12B8F8` | `STORE_DEREF` | 137 | 帶參數 (消費 2B `uint16`) |
| `0x9E` | 158 | `0x1E12B532` | `STORE_GLOBAL` | 97 | 帶參數 (消費 2B `uint16`) |
| `0xA2` | 162 | `0x1E12ADBE` | `JUMP_IF_FALSE_OR_POP` | 111 | **絕對跳轉** (消費 **4B**: 2×`uint16`) |
| `0xA3` | 163 | `0x1E12B56C` | `BUILD_TUPLE` | 102 | 帶參數 (消費 2B `uint16`) |
| `0xA4` | 164 | `0x1E12B65F` | `LOAD_NAME` | 101 | 帶參數 (消費 2B `uint16`) |
| `0xA6` | 166 | `0x1E12B7B6` | `POP_JUMP_IF_TRUE` | 115 | **絕對跳轉** (消費 **4B**: 2×`uint16`) |
| `0xAC` | 172 | `0x1E12AF18` | `LIST_APPEND` | 94 | 帶參數 (消費 2B `uint16`) |
| `0xAF` | 175 | `0x1E12BFFC` | `CALL_FUNCTION` | 131 | 帶參數 (消費 2B `uint16`) |
| `0xB0`..`0xB2` | 176..178 | `0x1E12C066` | `CALL_FUNCTION_VAR..VAR_KW` | 140..142 | 帶參數 (消費 2B `uint16`) |
| `0xB3` | 179 | `0x1E12C120` | `SET_ADD` | 146 | 帶參數 (消費 2B `uint16`) |
| `0xB7` | 183 | `0x1E12B643` | `BUILD_MAP` | 104 | 帶參數 (消費 2B `uint16`) |
| `0xBA` | 186 | `0x1E12B3EA` | `UNPACK_SEQUENCE` | 92 | 帶參數 (消費 2B `uint16`) |
| `0xC1` | 193 | `0x1E12B84F` | `JUMP_IF_TRUE_OR_POP` | 112 | **絕對跳轉** (消費 **4B**: 2×`uint16`) |
| `0xC2` | 194 | `0x1E12B9D4` | `SETUP_FINALLY` | 122 | **相對跳轉塊** (消費 **4B**: 2×`uint16`) |
| `0xC3` | 195 | `0x1E12B1F8` | `RAISE_VARARGS` | 130 | 帶參數 (消費 2B `uint16`) |
| `0xC8` | 200 | `0x1E12B893` | `LOAD_DEREF` | 136 | 帶參數 (消費 2B `uint16`) |
| `0xDA` | 218 | `0x1E12AD27` | `LOAD_FAST` | 124 | 帶參數 (消費 2B `uint16`) |
| `0xDB` | 219 | `0x1E12B555` | `DELETE_GLOBAL` | 98 | 帶參數 (消費 2B `uint16`) |
| `0xDF` | 223 | `0x1E12B9D4` | `SETUP_EXCEPT` | 121 | **相對跳轉塊** (消費 **4B**: 2×`uint16`) |
| `0xE2` | 226 | `0x1E12AD39` | `JUMP_ABSOLUTE` | 113 | **絕對跳轉** (消費 **4B**: 2×`uint16`) |
| `0xE5` | 229 | `0x1E12BE86` | `MAKE_FUNCTION` | 132 | 帶參數 (消費 2B `uint16`) |
| `0xE6` | 230 | `0x1E12B9AD` | `COMPARE_OP` | 106 | 帶參數 (消費 2B `uint16`) |
| `0xE7` | 231 | `0x1E12B1BB` | `CONTINUE_LOOP` | 119 | **絕對跳轉** (消費 **4B**: 2×`uint16`) |
| `0xE9` | 233 | `0x1E12AD8E` | `DUP_TOPX` | 99 | 帶參數 (消費 2B `uint16`) |
| `0xEB` | 235 | `0x1E12B85F` | `LOAD_CLOSURE` | 135 | 帶參數 (消費 2B `uint16`) |
| `0xF2` | 242 | `0x1E12C1CA` | `EXTENDED_ARG` | 145 | 帶參數 (消費 2B `uint16`) |
| `0xF6` | 246 | `0x1E12AD61` | `LOAD_GLOBAL` | 116 | 帶參數 (消費 2B `uint16`) |
| `0xF7` | 247 | `0x1E12B33F` | `DELETE_NAME` | 91 | 帶參數 (消費 2B `uint16`) |

---

## 4. 自動化轉譯與批量反編譯工具 (`tools/decompiler/batch_decompile.py`)

我們在 `tools/decompiler/` 下構建了完整的字節碼轉譯與並行反編譯工具鏈：
- `tools/decompiler/batch_decompile.py`：支持一鍵處理 `data/data.fls`、解包後的 `.pyo` 目錄、以及 `data/script.fls`。
- `tools/decompiler/script_fls_keys.json`：預計算並持久化的 `data/script.fls` 全部 5,002 個條目的 5 段式 XOR 密鑰與分段邊界數據庫。

### 4.1 關鍵工程技術亮點

1. **`data.fls` (Python 2.7) 雙流合並與 `TYPE_STRINGREF` 保序**：
   - 自動剝離 `PyCodeObject` 中 4 字節 `co_extra` 字段，將 `co_code[:co_extra]` 指令流與 `co_code[co_extra:]` 參數流重組為標準 Python 2.7 3 字節交錯指令流，並將 `co_lnotab` 從指令索引增量重映射為字節偏移增量。
   - 嚴格保留 `co_code` 與 `co_lnotab` 的原始 `'t'` (interned string) 標記，確保後續 `'R'` (`TYPE_STRINGREF`) 索引表 100% 對齊。
2. **`script.fls` (Python 2.5) 跨段邊界精確求解器 (`solve_py25_co_span`)**：
   - 當 5 段式 XOR 的分段邊界落在某個函數的 `co_code` 內部或 16 字節 `PyCodeObject` 頭部時，利用該函數自身的元組長度約束 `(len(co_consts), len(co_names), len(co_varnames), len(co_freevars) + len(co_cellvars), len(co_code))` 進行精確邊界搜索，消除跨段偽指令干擾。
3. **Big5 (`cp950`) 繁體中文字面量無損解碼 (`decode_big5_literals`)**：
   - 將反編譯源碼中形如 `'\xa6b\xb3o\xbb\xda'` 的 Big5 轉義字節序列自動還原為可讀的 UTF-8 繁體中文字符串，同時保留語法合法性與混合轉義字符。

### 4.2 命令行使用方式

```bash
# 1. 一鍵解包、轉譯並反編譯整個 data/data.fls (121 個 Python 2.7 .pyo 模塊)
python3 tools/decompiler/batch_decompile.py data/data.fls tools/decompiler/output/data_fls --workers 8

# 2. 按路徑關鍵字或條目編號反編譯 data/script.fls 中的指定模塊或子目錄
python3 tools/decompiler/batch_decompile.py data/script.fls tools/decompiler/output/script_fls --entry "login" --workers 8
python3 tools/decompiler/batch_decompile.py data/script.fls tools/decompiler/output/script_fls --entry 516
python3 tools/decompiler/batch_decompile.py data/script.fls tools/decompiler/output/script_fls --entry 17

# 3. 批量反編譯整個 data/script.fls (5,002 個 Python 2.5 模塊) 並同時導出標準 .pyc
python3 tools/decompiler/batch_decompile.py data/script.fls /tmp/full_script_py --emit-pyc /tmp/full_script_pyc --workers 8
```

### 4.3 驗證結果匯總

| 驗證目標 | 所屬歸檔與 VM | 反編譯輸出路徑 | 狀態與行數 |
| :--- | :--- | :--- | :--- |
| **全部 121 個 `.pyo` 模塊** | `data/data.fls` (Py2.7) | `tools/decompiler/output/data_fls/` | **121 / 121 (100%)** 零報錯通過 |
| **`script.fls` 全量復跑（2026-10-13）** | `data/script.fls` (Py2.5) | `/tmp/full_script`、`/tmp/missing_out`（暫存驗證產物） | **4,442 / 5,002 (88.8%)** 成功；546 個轉譯成功但 uncompyle6 失敗；12 個轉譯失敗；2 個 uncompyle6 病理案以超時隔離 |
| `core/gamecode.pyo` | `data/data.fls` (Py2.7) | `tools/decompiler/output/data_fls/core/gamecode.py` | **113 行**，語法與邏輯 100% 完整 |
| Entry 516 (`netserver.py`) | `data/script.fls` (Py2.5) | `tools/decompiler/output/script_fls/script/login/netserver.py` | **580 行**，完整還原登錄與選服協議 |
| Entry 17 (`equipitemdata.py`) | `data/script.fls` (Py2.5) | `tools/decompiler/output/script_fls/script/data/equipitemdata.py` | **104 行**，完整還原裝備表結構與中文 |
| 登錄與認證全套 51 個模塊 | `data/script.fls` (Py2.5) | `tools/decompiler/output/script_fls/script/login/` | **51 / 51 (100%)** 零報錯通過 |

### 4.4 `script.fls` 殘餘條目的分段參數修復（2026-10-13）

`script_fls_keys.json` 對絕大多數條目給出的 5 段 XOR 參數可以直接工作，但驗證中曾有 14 條目在 `Py25MarshalTranspiler` 階段失敗。本次在 `batch_decompile.py` 內加入**僅於記憶體中執行**的修復管線，不修改金鑰資料庫，也不回寫原始歸檔；所有修復結果仍須通過「完整轉譯 + 成功反編譯」的原有驗收。

#### 根因分類

1. **`catalog` 條目的邊界偏差**：金鑰正確，但分段邊界可偏移若干字節。縫口附近字節會被鄰段金鑰解密，一旦落在字串長度、容器計數或物件標籤等結構欄位上，Marshal 步進即脫軌。此類共救回 5 條：entries `63`、`64`、`1013`、`1528`、`1854`。
2. **`catalog_fallback` 條目的整套參數失真**：此類條目的金鑰與邊界原本只是原求解器的兜底近似，不但數值可大幅偏差，真實分段還可能包含僅約 10 字節的微分段，或把縫藏在長字串、`co_code` 等對結構步進不透明的區域內。此類共救回 4 條：entries `1931`、`2643`、`2984`、`4133`。

#### 修復策略

1. **嚴格 Marshal 步進裁判**：新增 `_strict_walk` / `_strict_progress`，逐步檢查標籤、長度與容器計數是否落在剩餘緩衝區內，並以第一個結構不可能物件的位置作為進度。不能直接使用轉譯器的 `pos` 作進度，因為壞長度欄位會令它飛出界外而失去比較意義。
2. **第一層：邊界移位**：保留目錄金鑰，對四個分段邊界逐縫在 ±1600 內按距離由近及遠試移，以嚴格步進完成度排序；多縫同時偏移時逐輪推進。
3. **第二層：整套分段重解**：若目錄參數不可信，則利用模組流必以程式碼物件標籤 `c` 開頭取得第一把金鑰 `exp[0] ^ 0x63`，之後每逢步進脫軌便在該點試遍 256 把金鑰，採納能使結構續跑最遠者。若直接換鑰不足，還會在有限窗口內聯合調整分段點與金鑰，並以光束搜尋作中小條目的兜底。不足 5 段時以同金鑰虛分段補齊，以符合轉譯器介面；超過 5 段則放棄。
4. **縫口精修**：嚴格步進只能指出第一個壞物件，真縫可能位於其前數十字節（例如躲在定長小物件或字串尾部）。精修在每縫 `-64..+8` 範圍內同時要求嚴格步進完整、所有 `'R'` 引用小於此前 `'t'` 駐留字串數量，並以縫口前後 48 字節的 GBK/ASCII 文本連貫性作決勝。
5. **成本護欄**：修復僅在基線轉譯失敗時觸發。移縫轉譯嘗試次數按條目大小、且逐縫獨立封頂；光束搜尋評估預算隨條目變大而收緊；大條目跳過窗口搜尋，避免在無望的大條目上長時間空耗。

#### 全量驗證結果

2026-10-13 以 8 個 worker 復跑 `data/script.fls` 全部 5,002 條目。由於 entries `2371`、`2679` 會使 uncompyle6 在掃描/文法建樹階段長時間空轉，主跑先完成其餘部分，再將缺失的 318 條以每條 120 秒超時逐一補跑並分類。最終帳目為：

| 結果 | 數量 | 說明 |
| :--- | ---: | :--- |
| 反編譯成功 | **4,442** | 佔 **88.8%**，包括本次救回的 9 條 |
| 轉譯成功、uncompyle6 反編譯失敗（stub） | 546 | 非本次分段修復範圍 |
| 轉譯階段失敗 | 12 | `880`、`1954`、`2310`、`3066`、`3122`、`3505`、`3794`、`4166`、`4305`、`4691`、`4741`、`4928` |
| uncompyle6 病理案（超時隔離） | 2 | `2371`、`2679`；py-spy 堆疊位於 uncompyle6 的 scanner/parser，非歸檔解密或本次修復程式碼 |

同一輪對照中，`data/data.fls` 的 **121 / 121** 個 `.pyo` 模塊仍全部反編譯成功，證明另一條 Python 2.7 管線未受影響。健康 `script.fls` 抽查 entries `0`、`579`、`4538` 亦維持成功。

#### 已知邊界

- 尚未救回的 6 個重點條目為 `1954`、`3066`、`4166`、`4305`、`4691`、`4928`。其共同困難是分段點可藏在對 Marshal 步進不透明的長字串或 `co_code` 內，或需要比目前窗口更精確的內容層定位；`4928` 已能完成結構重解與轉譯，但仍被 uncompyle6 深層檢查拒絕。**（2026-10-15 勘誤：`4305`、`4928` 已由 §4.5 的定點恢復救回，未救回者現為 `1954`、`3066`、`4166`、`4691` 四條。）**
- 若要繼續攻克，應另行研究以 GBK 文本統計、字串內容連續性與 `co_code` 操作碼合理性聯合評分的「內容驅動金鑰恢復」，不要把目前以結構為主的裁判硬擴成無界搜尋。
- entries `2371`、`2679` 應在後續工程化時加入**單條反編譯超時隔離**，或在具備 pycdc 的環境作第二引擎對照；不要因這兩個 uncompyle6 病理案而誤判 `script.fls` 解密失敗。
- CLI 的成功摘要會以「其中 N 條靠邊界修復救回」標示經修復條目數量；`script_fls_keys.json` 保持原封不動。

### 4.5 定點恢復 `tools/decompiler/recover_entries.py`（2026-10-15）

用戶要求「把沒反編譯的反編譯出來」後，重點處理 §4.4 帳目裡那 12 條 `轉譯階段失敗` 與清點中顯示「無產物」的 26 條。工具**以 import 方式複用** `batch_decompile`（其 SHA-256 被 `agent_e_reproduction.json` 鎖定，不得改動），與主批量的差別只有三點：

1. **不用 `_decompile_ok` 否決整條**：轉譯拿到的 pyc 一律保留，反編譯成敗另記一欄，避免「金鑰已解對卻整條丟棄」。
2. **逐路徑分量清洗 `co_filename`**：歸檔內的自報檔名本身也帶位元汙染（含 `\x00`、`?`、`*` 等），主批量會因此在寫檔時拋 `OSError` 而**靜默零產物**。清洗後仍不像正常包內路徑的，收進 `script/mangled/entry_XXXX_ID.py` 並保留原名。
3. **反編譯放子進程並帶 `--decompile-timeout`**（預設 120 秒）：一個病理案不再拖住整批；反編譯失敗時改寫 marshal 結構摘要，並在旁邊留 `.pyc` 供後續換引擎重試。

四級梯子為 `baseline → 縫口精修 → 邊界移位 → solve/beam`，其中「縫口精修對 catalog 金鑰先試一次」是本輪新增：`4305` 的嚴格步進其實已 100% 走通，只是縫位未細化導致 marshal 校驗失敗，精修後直接得到可用源碼。

#### 26 條的真實根因（推翻「解不開」）

| 類別 | 條目 | 處理 |
| :--- | :--- | :--- |
| 清点誤差：產物一直存在 | `508`、`955`、`1438`、`2005`、`2187`、`2330`、`3143`、`3341`、`3614`（落 `script/unknown/`）＋ `1931`、`2643`、`2984`、`4133`（落真實模組路徑） | 只需重算。前 9 條因索引 `current_filename` 為 `null`、後 4 條因檔名取自包內自報路徑，按目錄名比對時都被漏掉 |
| `co_filename` 含非法字元 → 寫檔異常 | `880`、`2310`、`3122`、`3794`、`4305`、`4741` | 清洗路徑後落盤，得 6 份完整源碼 |
| 已解出但被反編譯閘門丟棄 | `3505`、`4928`（部分源碼＋結構摘要）、`2371`（僅結構摘要＋`.pyc`） | 保留 pyc 與摘要，不再假裝成功 |
| 目前真的解不開 | `1954`（進度 322/340）、`3066`（414/916）、`4166`（1523/1599，僅差 76 位元組）、`4691`（17025/82936） | 老實標 `untranspilable`；`4166` 是最有希望的下個目標 |

全語料最終帳目：**5,000 個 `.py` ＋ 1 個 `.pyc`（66 MB）= 4,444 完整反編譯 ＋ 9 本輪恢復產物 ＋ 547 個 52 位元組失敗佔位**；`data/script.fls` 與 `script_fls_keys.json` 全程唯讀（SHA-256 `8b6e9266…` / `43bb090d…` 複核未變）。回歸：`python -m unittest discover -s tools/decompiler -p "test_*.py"` 25 項通過，`ruff`（倉庫 `ruff.toml`）對兩個新檔 0 錯。

```sh
/home/user/dec-venv/bin/python tools/decompiler/recover_entries.py \
    --out <倉庫外语料目錄> --entries 880,2310,4305 \
    --report <恢復報告.json> [--dry-run] [--decompile-timeout 150]
```

#### 順帶解決的註冊線疑案：`servicedata` 其實在包內

本輪最有意外的收獲。`tools/registration/README.md` 與 `docs/STATUS.md` 先前記「原 `servicedata` 模組不在本版 `script.fls` 內」，故條款走佔位文字；實際該模組**一直存在**，條目 `1931` 解出的自報路徑即 `script\data\servicedata.py`（86,579 位元組，已完整反編譯）：`if main.g_LangVersion == 0:` 分支給出 `SERVICE_MSG`（11,602 位元組，首行 `#cd95927夢想世界遊戲服務條款#n`，末段含「因服務條款所生之爭議，以台灣台北地方法院為第一審管轄法院」）與 `SERVICE_MSG2`（9,055 位元組「線上遊戲定型化契約範本」），`else` 分支另有一份 7,264 位元組的 AMS 版條款。誤判原因是 `catalog` 裡這條沒有名字，按名字索引查不到；而 `script/login/register.py:171`、`script/login/loginin.py:696` 本來就寫 `import servicedata`（與 14 個模組 `import defines` 同構，說明 `script/data` 在 import 路徑上），可見真客戶端能取到它。**後續（未做）**：把註冊測試包的條款從佔位改成直接取包內 `servicedata`，需重建 `out/script.fls` 並跑 `tools/registration` 的 13 項回歸，另輪授權。

---

### 4.6 第二反編譯引擎 `pycdc` 的交叉覆核（2026-10-15）

`tools/decompiler/crosscheck_pycdc.py` 把 pycdc 接成第二引擎，用來複核「轉譯成功、uncompyle6 失敗」的 547 個 52 字節佔位與 §4.5 的殘餘。前提與 §4.5 相同：不改 `batch_decompile.py`（SHA 被釘），複用 `recover_entries` 的路徑清洗與轉譯梯；pycdc 一律放子進程帶超時；`--write` 只寫 `<out>/pycdc/` 這棵獨立樹，已存在就跳過，**絕不覆蓋 uncompyle6 的產物**。

構建配方（沙箱實測約 2 分鐘，只需要被放行的 github）：pycdc 是純 C++，**不需要 flex/bison**；Debian 缺的 cmake 可用 `pip install cmake` 取（輪子自帶真二進制）。

```sh
/home/user/dec-venv/bin/pip install cmake          # 或任何自帶 cmake 的環境
git clone -q --depth 1 https://github.com/zrax/pycdc
cmake -S pycdc -B pycdc/build && cmake --build pycdc/build -j4

python3 tools/decompiler/crosscheck_pycdc.py --out <語料目錄> \
    --accounting accounting.json --class failed --jobs 4 --timeout 25 \
    --write --keep-pyc <pyc 目錄> [--ladder]
```

#### 5,002 條的雙引擎矩陣

| 行=uncompyle6 現有產物 | pycdc ok | 只拿到部分 | pycdc 崩 | 無 pyc | 合計 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `full`（完整源碼） | 4,312 | 0 | 75 | 0 | 4,387 |
| `recovered`（§4.5 產物） | 2 | 0 | 0 | 0 | 2 |
| `stub`（52 字節佔位） | **465** | 23 | 56 | 0 | 544 |
| `absent`（無產物） | 53 | 0 | 1 | 0 | 54 |
| 未拿到 pyc（未開 `--ladder`） | 0 | 0 | 0 | 15 | 15 |
| **合計** | **4,832** | 23 | 132 | 15 | 5,002 |

* pycdc **淨補 546 條**讀得懂的源碼（541 條直接命中 + 5 條要開 `--ladder`；那 5 條正是 §4.4 記的 `63`、`64`、`1013`、`1528`、`1854`），全語料 10.4 秒跑完 547 條。
* 反向也有：75 條 uncompyle6 出得了、pycdc 直接崩（`vector::_M_range_check: __n … >= this->size()`、`std::bad_cast`）⇒ **單一引擎的成敗不構成結論**，兩邊要各留一份。
* 定論殘餘：把 pycdc、uncompyle6、§4.5 修復梯全開之後仍**零產物的是 61 條**（56 條佔位 + 1 條無產物 + 4 條連轉譯都過不了：`1954`、`3066`、`4166`、`4691`）；清單寫在語料目錄 `residual_no_source.json`。覆蓋率 **4,941 / 5,002 = 98.78%**。

#### 入庫與分發（2026-10-15，用戶明確授權）

- 倉庫內：`tools/decompiler/output/script_fls_pycdc/`（**499** 個 pycdc 產物 + `manifest.json` +
  `README.md`；uncompyle6 側已有完整源碼的 18 個重複項刻意不重複入庫）、`output/script_fls/`
  併入 §4.5 救回的 **9** 個產物。`manifest.json` 逐檔記 `entry` / `status` / `lines` /
  `escaped_bytes` / `py25`（`raw`、`top_return_only`、`no`）與 `uncompyle6` 成色，並釘住三個鎖定輸入的 SHA-256。
- 倉庫外：全量語料與全部報告打包為 `MXSJ_script_fls_pycdc_recovered_20261015.zip`
  （2,364,954 B，MD5 `c566766dc3a2ea96415711ac19851bd0`，Drive `1B588Ib1AlxycyzEXU9W4jZxiVe5xNFbd`）。
  61 條「兩引擎 + 修復梯全開仍零源碼」的清單在包內 `reports/residual_no_source.json`。

#### 「反編譯成功」不等於「可回編譯」

用 `tools/registration/build_python25.sh` 自建的真 CPython 2.5.6（照跑即通，`Python 2.5.6`）對全部產物做 `compile()`，這是本輪最該記下來的一筆：

| 產物集 | 原樣可編譯 | 剝掉模組頂層 `return` 後 | 仍失敗 |
| :--- | ---: | ---: | ---: |
| uncompyle6 全語料 4,998 檔 | 550（11.0%） | **3,770（75.4%）** | 1,228 |
| pycdc 交叉覆核 512 檔 | 248（48.4%） | 248（沒有這個偽影） | 264 |

1. **系統性偽影**：這些 `.pyo` 的模組碼物件以 `RETURN_VALUE` 收尾，uncompyle6 如實還原成模組頂層一句 `return`，而模組級 `return` 不是合法 Python——3,220 個檔案**只因為這一行**編譯不過。走「編輯後回編譯」管線（STATUS §5.2 ④）時必須先剝掉它，否則第一步就 `SyntaxError: 'return' outside function`。
2. 仍失敗的 1,228 檔分類：真語法錯 1,159、含 NUL 位元組 35（§4.5 那類 `\x00` 汙染已經滲進源碼常量）、編碼宣告與實際位元組不符 27、縮進 6。
3. pycdc 那 264 檔失敗**不是**本工具把非 UTF-8 位元組轉義成 `\xNN` 造成的：拿未轉義原文重測，0 檔被修好，仍是 pycdc 自己寫錯（例：`script/usermacro.py:147` invalid syntax）。

所以 pycdc 產物的定位是**「能讀、能互證，不能直接回編譯」**；要進回編譯管線的候選必須兩邊都過 `compile()` 再挑。工具側另有一處必須記住的事：pycdc 會把 GBK 字節原樣吐出來，用 `text=True` 收管道會在 `UnicodeDecodeError` 上崩掉整批——本工具改成二進制捕獲 + `backslashreplace` 轉義，並在報告與產物頭註記「已轉義」，這條也有回歸測試兜著。

---

## 5. 正向字節碼混淆、5段式 XOR 加密與 `.fls` 重打包管線 (`tools/decompiler/pack_and_encrypt.py`)

除了解密與反編譯外，我們還實現了完整的**逆向回寫（正向混淆 + 加密 + 歸檔打包）工具** `tools/decompiler/pack_and_encrypt.py`：

1. **VM #2 (`data/data.fls` — Python 2.7 Split-Stream 正向混淆與全量重打包)**：
   - **`obfuscate_py27_pyc_bytes`**：將標準 Python 2.7 `.pyc` 轉換回多益定製 `.pyo`：
     - 透過 `INV_PY27_MAP` 將標準 Opcode 映射回多益混淆 Opcode，並在末尾追加 `0x17` (`NOP`) 哨兵，寫入 4 字節 `co_extra = len(ops)`。
     - 將跳轉指令（`PY27_ABS_JUMP_OPS | PY27_REL_JUMP_OPS`）精確編碼為 4 字節雙 `uint16_le` 參數：
       - 絕對跳轉：`struct.pack("<HH", target_op_idx, target_arg_byte_offset)`
       - 相對跳轉：`struct.pack("<HH", target_op_idx - (cur_op_idx + 1), target_arg_byte_offset - (cur_arg_byte_offset + 4))`
     - 將標準字節偏移 `co_lnotab` 還原為多益指令索引增量 `co_lnotab`。
   - **逐比特往返驗證（Bit-Identical Round-Trip）**：`data/data.fls` 內全部 **121 / 121 個 `.pyo` 文件（共 2,530 / 2,530 個 `PyCodeObject`）** 經 `transpile -> obfuscate` 往返後與原始 `.pyo` **100.0% 逐字節完全一致**。
   - **`repack_data_fls`**：支持將修改後的 `.pyc` 或 `.pyo` 重新以 raw deflate 壓縮並完整重構 `data.fls`（自動更新 `0xA0975237` 本地頭、`0x87F2017C` 中央目錄偏移/CRC32/大小、以及末尾 8 字節 `<II(cd_offset, 0xA1985237)` 尾標，無文件大小限制）。

2. **VM #1 (`data/script.fls` — Python 2.5 正向 Opcode 混淆、5段式 XOR 加密與 `0SLF` 打包)**：
   - **`obfuscate_py25_pyc_bytes`**：透過 `INV_PY25_MAP` (`HAVE_ARGUMENT = 0x5F`) 將標準 Python 2.5 `.pyc` 還原為無頭多益 Marshal 流。
   - **`encrypt_5seg_xor`**：讀取 `tools/decompiler/script_fls_keys.json` 中的 5 段 XOR 密鑰與分段邊界進行加密（若修改後長度小於原始長度，自動在根 `PyCodeObject` 末尾填充至原始長度以保持 `_dyprot` 的 5 段邊界 100% 不變；等長時與原始載荷 **100% 逐比特一致**）。
   - **`repack_script_fls`**：以 `zlib.compress(..., 9)` 壓縮並透過 `0x0048F170` 逆向推導的三階多項式加密重構 `0SLF` 索引表，生成完整合法的 `script.fls`。

```bash
# 運行往返一致性與打包自檢測試 (121/121 .pyo & script.fls 100% 逐字節一致)
python3 tools/decompiler/pack_and_encrypt.py verify

# 將標準 Python 2.7 .pyc 混淆為多益 Split-Stream .pyo
python3 tools/decompiler/pack_and_encrypt.py pyc2pyo input.pyc output.pyo

# 將修改後的 .pyc/.pyo 打包回 data/data.fls
python3 tools/decompiler/pack_and_encrypt.py pack-data --input modified_dir_or_file --output data/data_repacked.fls

# 將修改後的標準 Python 2.5 .pyc 混淆、5段XOR加密並打包回 data/script.fls
python3 tools/decompiler/pack_and_encrypt.py pack-script --index 516 --pyc netserver.pyc --output data/script_repacked.fls
```

