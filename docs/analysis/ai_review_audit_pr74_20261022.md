# PR #74 AI 审查复核（2026-10-22）

## 范围与方法

PR #74 https://github.com/a565551313/MXSJ_TW_2022/pull/74 上的 AI 审查共 **5 条行内评论**：

- gitar-bot 1 条（`4348486534`，`ui/save_mode.py:129`）
- coderabbitai 4 条（`4348575599` `docs/STATUS.md:149`、`4348575621` `ui/save_mode.py:88`、
  `4348575653` `ui/save_mode.py:137`、`4348575674` `ui/save_workflows.py:357`）

复核方式：逐条读当前代码（HEAD `a4f26dc`）→ 写最小复现脚本（offscreen Qt，`/tmp` 下一次性运行，
不提交）→ **只把能复现或代码路径成立的算「属实」**。Windows 专有行为在 Linux 沙箱无法实测的
单独标明。

结论：**首轮 5 条 + 追加 2 条全部属实，无一驳回**。已全部修复并补 11 项回归，
全套 779 项测试完成（778 通过、1 跳过、0 错误）；追加修复后再跑一次为
782 项完成（781 通过、1 跳过、0 错误）。

---

## 逐条判定

### 1. gitar `4348486534` — `ui/save_mode.py:129`：切回严格误清新包 + 队列漏清

**判定：属实（两个独立 bug）。**

复现一：严格模式存过新包 `interface_edited.fls` → 切宽松 → 立刻切回严格（中间没存过）。
`_forget_in_place_outputs` 拿 `output_pack` 和 `source_pack[0]` 比，而 `_adopt_written_pack`
在严格保存成功后已把 `source_pack[0]` 也指向新包，于是两者相等，**合法的新包被当成
「就地写回」清掉**。下次 Ctrl+S 重新问路径，`_default_output_pack()` 见新包已存在，建议
`interface_edited2.fls`——凭空多出第二个输出包。

复现二：宽松模式下批量导入若干布局（只排队、没打开）→ 切回严格 → 打开其中一个 →
Ctrl+S。探针实测 `patch ok` 直接写进**原包**，没有提示、没有守卫——比审查描述的
「被 `guard_output` 拒绝」更严重。原因是 `_documents_for_mode()` 只走已打开标签和当前
文档，`self._pending_imports` 里的文档没被遍历。

修法：`_forget_in_place_outputs` 改为与 `origin_pack` 比；`_documents_for_mode` 追加
`_pending_imports` 中的文档。

### 2. coderabbit `4348575621` — `ui/save_mode.py:88`：确认框写错包

**判定：属实。**

确认框显示 `source_pack[0]`，而宽松模式实际写的是 `origin_pack`。严格模式存过新包后
两者不同：框里说会改 `interface_edited.fls`，实际会改 `interface.fls`——差的正是
「哪个包会被覆盖」这件事。改为 `origin_pack or source_pack[0]`。

### 3. coderabbit `4348575653` — `ui/save_mode.py:137`：`_documents_for_mode` 漏队列

**判定：属实。** 与 #1 的第二个 bug 同一根因，同一处修复（见上）。

### 4. coderabbit `4348575674` — `ui/save_workflows.py:357`：校验落在 `os.replace` 之后（Major）

**判定：属实，且是最严重的一条。**

`check_staging` 原来先 `patch_pack_copy_many()` 再 `verify_written_pack(path)`。原地写回
（宽松模式写原包、或严格模式续写自己的输出包）时，`patch_pack_copy_many` 内部的
`os.replace` 已经把目标换掉，此时校验失败**原包已毁且没有备份**——与「不备份」的产品
口径叠加后不可恢复。

探针 `probe74_5.py`：构造「写回后读回的布局和预期不符」，直接跑旧链路，原包被替换成
坏包；改后同一探针下原包字节 SHA-256 不变、临时文件清掉、`resolver` 句柄重新挂上。

修法：`patch_pack_copy_many(..., verify=callable)` 在 `guard_output` 与 `os.replace`
**之间**调用钩子；`check_staging` 传闭包，内部调 `verify_written_pack(trusted_copy=True)`
——未改动条目已由 `_verify_copy` 逐字节比过，这里只数允许改动的条目，`changed_entries`
仍能算出真实条数。失败抛 `PackError`，UI 按「写回原包 / 写回目标包」区分文案，原地
写回明说「原包没有改动，可以继续编辑后重试」。

### 5. coderabbit `4348575599` — `docs/STATUS.md:149`：证据行过时

**判定：属实。**

§1「本轮证据」仍写上一轮的真包数据（2,708 篇布局 / 729 个基路径 / 780 个候选名），
「本轮授权」还是选族那一轮，起点写 `32f1c24` 而本轮是从 `0e502aa` 起的。§2 UI 编辑器行
也重复了真包结论。

修法：起点改 `0e502aa`、授权改为「0.16.0 保存模式 + 复核 PR #74」，真包数据标注为
0.12.5–0.13.x 的历史结果并写「本轮未执行」，测试计数改 779。

---

## 回归

`tests/test_gui_save_mode.py` +6（审查首轮）：

- 严格存过新包后切宽松再切回严格，新包仍在、Ctrl+S 不再问路径；
- 宽松确认框显示原包路径、不显示输出包路径；
- 切回严格会清掉队列里布局的 `output_pack`；
- 队列布局切回严格后打开保存要问路径、原包字节不变；
- 宽松校验失败：原包字节不变、提示「原包没有改动」、句柄能挂回；
- 严格续写自己的输出包时校验失败：目标包保持原样。

`tests/test_pack_copy_many.py` +2：

- `verify` 钩子在替换前调用，失败时目标文件保持原样、临时文件清掉（原地写回）；
- 目标是新包时同样先校验再替换。

首轮修复合计 8 项回归，全套 **779 项**（778 通过、1 跳过、0 错误）；追加 3 项后为
**782 项**（781 通过、1 跳过、0 错误），ruff 0、wincompat 0/0/0。

## 未验

Windows 实机；`os.replace` 在 Windows 上目标被占用时的行为沿用上一轮结论，本轮未重测。

---

## 追加复核（同日，修复提交 `316b605` 之后的 2 条）

### 6. gitar `4348840630` — `ui/save_workflows.py:403`：所有 `PackError` 都被说成校验失败

**判定：属实。**

`check_staging` 为了让「替换前校验失败」有个专门的提示，抛的是通用 `PackError`；而
`_save_to_pack` 新加的 `except PackError` 把它一起接住了。`patch_pack_copy_many` 会把
所有 `OSError`/`ValueError` 包成 `PackError("写入新包失败：…")`，`_plan_patch` 的
「包中找不到条目」也是 `PackError`。探针实测：目标目录不存在（路径写错）时弹出

```
写回校验未通过
写入新包失败：[Errno 2] No such file or directory: '…/.interface_edited.fls.xxx.tmp'
已有文件没有改动，可以继续编辑后重试。
```

三处都不对：标题说是校验失败、正文建议「继续编辑后重试」（编辑救不了路径）、目标根本
不存在却说「已有文件没有改动」。

修法：新增 `_StagingVerifyFailed(PackError)`，只有 `check_staging` 抛它；`except
_StagingVerifyFailed` 走「写回校验未通过」，`except PackError` 回到原来的「写回失败」。
校验失败的结尾文案按目标分四种：原包 / 目标包 / 已有的别人的文件 / **没有写出新包**
（目标原本不存在时不再说「已有文件」）。

回归 3 条：路径写错 → 标题「写回失败」且不提校验；新路径校验失败 → 「没有写出新包」且
文件确实没生成；目标是他人的已有包 → 说「已有文件没有改动」且字节不变。

### 7. coderabbit `4348933020` — `docs/analysis/ai_review_audit_pr74_20261022.md:15`：把跳过算成通过

**判定：属实（措辞）。**

第 15 行写「全套 779 项通过」，而第 98 行是「778 通过、1 跳过、0 错误」。跳过的 1 项
不能算通过。改为「779 项测试完成（778 通过、1 跳过、0 错误）」。

## 追加回归与计数

`tests/test_gui_save_mode.py` 再 +3（共 24 项），全套 **782 项**（781 通过、1 跳过、
0 错误），ruff 0、wincompat 0/0/0。
