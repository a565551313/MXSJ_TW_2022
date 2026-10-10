# dis_v43 — v4.3 映射驱动的自定义字节码对齐反汇编器

**来源**：并行任务 P3（连接流程与 Connect() 复核），2026-10-10。
结果报告：`work/dream-world-connect-login-map/notes/parallel-20261010/P3-result.md`。

## 用途

对游戏客户端脚本（FLS 条目解出的 Python 2.7 marshal 对象树）里的**自定义 S 盒字节码**
做可靠反汇编。与 `tools/pymarshal_dis.py`（固定 S 盒通用反汇编）互补：本工具以
`notes/co_code_analysis/mapping_table_v4.json`（版本 **4.3-taskB**）为映射来源，并额外处理
v4.3 已证明的**多变体 S 盒**问题（同字节在不同 code object 中大小/含义不同）。

## 文件

| 文件 | 说明 |
|---|---|
| `parse_marshal.py` | 只读 Python 2.7 marshal 解析器；恢复**完整常量池**（含整数）。`notes/co_code_analysis/code_objects.json` 只留字符串常量，解 `chr(port % 256)` 这类表达式必须用它。 |
| `dis_v43.py` | 反汇编器 CLI。 |

## 用法

```bash
# 列出 marshal 树里的全部 code object
python3 tools/dis_v43/dis_v43.py \
    work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin --list

# 反汇编（路径过滤词，子串匹配；可多个）
python3 tools/dis_v43/dis_v43.py \
    work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin \
    '/CRandomConnectMgr/Connect' '/CReselectConnectMgr/Connect'
```

无第三方依赖（纯标准库；不需要 capstone）。

## 方法（与 P3-result.md §1 一致）

1. 指令大小/名称取自 v4.3 表 A/B；跳转基数：`A2`=绝对，`B7/E3/AF/D3/E5`=`pos+3+arg`。
2. 双变体字节（`0x37/0x6C/0x90`）与未知字节按 **1 字节和 3 字节两种大小回溯**，
   解必须**端点精确**（end-exact，恰好落在 co_code 末尾）。
3. 候选解按**跳转目标对齐**排序（目标全部落在指令起点或 EOF 者最优），其次未知 3 字节少者优先。
4. 已知 3 字节指令做参数合理性过滤（names/consts/varnames 索引范围；`CALL_FUNCTION`
   低位=位置参数数、高位=关键字参数数）。

## 已知限制 / 注意

- **多变体 S 盒**（v4.3 已对 `0x6C/0x37` 证明）：同一字节在不同 code object 里可能不同。
  输出中带 `(ctx)` 的语义（`DUP_TOP`、`ROT_TWO`、`BINARY_MODULO?`、`SLICE+2?` 等）是
  P3 期间在 netserver.py **函数代码对象**内用栈一致性分析得出的**上下文结论**，
  **不覆盖** v4.3 表——例如 0x30 在模块层是 POP_TOP 类（(05,30) 高频 idiom），
  而在 netserver.py 函数代码里必须读作 DUP_TOP（`self.m_Time += 1` 的栈必需）。
- `0x00` **不**当作指令处理（参数区高频字节，语义未定）。若允许它作指令，双变体/未知字节的
  错误 3 字节读法会借 `00` 填充走通并挤掉正确解（P3 期间在 `CRandomConnectMgr.Connect` 上验证过）。
- 本工具**只读**：不写任何游戏文件；对 marshal blob 仅读。
