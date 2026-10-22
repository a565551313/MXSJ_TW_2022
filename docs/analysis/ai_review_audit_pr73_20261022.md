# PR #73 AI 审查复核（2026-10-22）

## 范围与方法

PR #73 https://github.com/a565551313/MXSJ_TW_2022/pull/73 上的 AI 审查共
**13 条行内评论 + 1 条范围外评论**：

- gitar-bot 5 条（`4347348436`、`4347348635`、`4347635514`、`4347635659`、`4347635765`）
- coderabbitai 8 条（`4347457539`、`4347707194`、`4347707205`、`4347707217`、
  `4347707248`、`4347707265`、`4347707274`、`4347707289`）
- coderabbitai review 正文 1 条范围外（`5613054191`，`source_actions.py:51-54`、
  `149-153`）

复核方式：逐条读当前代码（HEAD `d93ac64`）→ 写最小复现脚本跑一遍 →
**只把能复现或代码路径成立的算「属实」**。Windows 专有行为在 Linux 沙箱里
无法实测的，单独标明。所有复现脚本都在 `/tmp` 下一次性运行，不提交。

结论：**14 条全部属实**（其中 1 条只能用代码/平台语义判定，见 #2；
1 条需要病态包才触发，见 #5）。已全部修复并补回归。

---

## 逐条判定

### 1. gitar `4347348436` — `core/publish.py:104`：同文件二次保存自比自

**判定：属实。**

复现：源包写一次 → 第二次 `src == out` 且新增一个布局：

```
patch ok: ['new/added.dlg'] added
verify error: 条目数变化，写回结果不可信
```

`same_file` 当时只用于 `report["changed_entries"] = None`，条目数检查与
「声明新增 vs 实际新增」检查仍按 `before + 新增` 计算，而 `before` 已经是
写后的文件。`_verify_copy` 在 `os.replace` 之前已对照源包校验过临时文件，
这些检查在同文件场景下只会误报。

### 2. gitar `4347348635` — `ui/save_workflows.py:337`：Windows 覆盖打开中的包

**判定：属实（代码路径成立；Windows 实机未验）。**

`FlsPack` 打开后一直持有 `open(path, "rb")` 句柄（`core/pack.py:43`）。
第一次保存后 `_adopt_written_pack` 把输出包挂进 resolver；第二次保存
`patch_pack_copy` 末尾 `os.replace(tmp, out)` 时该文件仍被打开。POSIX 允许
替换打开中的文件，Windows 的 `MoveFileEx` 会拒绝（共享冲突/拒绝访问）。
沙箱是 Linux，无法复现系统错误码；按平台语义与代码路径判定属实。

### 3. coderabbit `4347457539` — `ui/save_workflows.py:510`：散装另存可覆盖输出包

**判定：属实。**

`_pack_sources()` 无条件把「自己的输出包」排除出保护列表。`_write_to`
（另存为散装 `.dlg`）用它做 `guard_output`，用户选中上次的输出包时会把
`.fls` 整包写成 `.dlg` 明文：

```
precious is pack: 1
write_to own output ok: True
覆盖后还是 0SLF 包吗: False 开头: b'# -*- coding: gbk -*-'
```

### 4. gitar `4347635514` — `ui/save_workflows.py:398`：当前标签是已有布局时整批失败

**判定：属实。**

复现：先排队一个新布局，再打开源包里已有的 `dialog/base.dlg`，Ctrl+S：

```
warns [('写回失败', '包中找不到条目：new/new.dlg')]
out exists False
```

`allow_create` 只取当前文档的 `pending_pack_import`，队列里的新路径被拿去做
`_plan_patch`，直接抛错，整次保存中止。

### 5. gitar `4347635659` — `core/pack_build.py:598`：重组回退重复计数

**判定：属实（需要 `_RebuildNeeded` 落在补图途中，属病态包/罕见路径）。**

模拟第 3 次补图时抛 `_RebuildNeeded`：

```
mode rebuild images_added ['img/a.png', 'img/b.png', 'img/a.png', 'img/b.png', 'img/c.png']
实际新增应为 3，计数 5
```

重组前没有清空 `added/replaced`，同一张图被算两次，`verify_structure` 的
条目数检查随之误报。

### 6. gitar `4347635765` — `core/pack_build.py:611`：要重组的包仍先整包复制

**判定：属实。**

构造目录逆序的包（`need_rebuild=True`）并监视 `_copy_with_progress`：

```
mode rebuild 先整包复制了吗 True ['out.fls']
```

### 7. coderabbit `4347707194` — `docs/STATUS.md:45`：测试计数不一致

**判定：属实。** 概览行仍写「708 项：705 通过、1 跳过、2 项既有错误」，
与同页 0.15.0 的 744 项冲突。已改为 744（本轮修复后为 756）。

### 8. coderabbit `4347707205` — `core/publish.py:115`：同文件校验拒绝合法再保存

**判定：属实（与 #1 同源，含具体测试反证）。**

用真实 GUI 链路跑「第二批导入 → 再次 Ctrl+S」：

```
save2 (None, [('写回校验未通过',
  '条目数变化，写回结果不可信\n新包文件已生成但不可信，请勿替换进客户端。')])
pending {'...interface_edited.fls': ['p/s1.dlg']}
```

包文件已经被替换，文档却保持待入状态。评论指出
`test_second_batch_joins_queue_and_same_output` 因 mock 掉 `QMessageBox.warning`
而仍然通过——属实（见 #13）。

### 9. coderabbit `4347707217` — `ui/batch_import.py:290`：entries 返回未规范化路径

**判定：属实。**

`path_bytes()` 会 `strip()` 并把反斜杠转成 `/`，`path_hash()` 不会。表格里
`"custom/a.dlg "` 或 `custom\a.dlg` 状态判「新增」，写包按规范化路径，
写后集合校验却按原始字符串算哈希：

```
path_hash("custom/a.dlg ") != path_hash("custom/a.dlg")
```

触发「新包条目集合与预期不符」，同样发生在 `os.replace` 之后。

### 10. coderabbit `4347707248` — `ui/import_queue.py:191`：adopt 不设 output_pack

**判定：属实。**

保存后打开队列里已开过的文档，`output_pack` 仍为空；下一次 Ctrl+S 走
另存为，默认名 `_edited2.fls`。复现中还能看到同类后果：往**自己上次的
输出包**里再导入布局，保存被 `guard_output` 拒绝：

```
warns [('保存前检查失败', '拒绝覆盖源资源或其别名：.../interface_edited.fls')]
```

### 11. coderabbit `4347707265` — `ui/save_workflows.py:390`：allow_create 只看当前文档

**判定：属实（与 #4 同源）。** 修复按路径精确开创建，不整批放开。

### 12. coderabbit `4347707274` — `ui/source_actions.py:103`：恢复待入叶子时机不对

**判定：属实。**

`refresh_sources` 先 `_restore_pending_items()`，随后 `_set_document(...)`
内部 `clear_pending()` 把刚挂上的叶子全部清掉。已用真实刷新流程验证修复：

```
test refresh_keeps_pending_leaves_after_tab_switch ... ok
```

### 13. coderabbit `4347707289` — `tests/test_gui_batch_import.py:158`：测试吞掉警告

**判定：属实。** `_save()` mock 了 `QMessageBox.warning`，第二次保存实际
失败（见 #8）测试仍绿。已改为记录警告并断言为空，另加队列/文档状态断言。

### 14. coderabbit review 正文 `5613054191` — `ui/source_actions.py:51-54`、`149-153`

**判定：属实。**

切换文本编码与 F5 重新读取都会 `LayoutDocument.from_dicts(...)` 重建文档，
只复制 `source_bytes/source_path/source_pack`，丢 `output_pack/origin_pack`。
后果：下次 Ctrl+S 重新问路径、标题丢来源包名。已补两处复制。

---

## 修复内容

| 文件 | 修复 |
| --- | --- |
| `core/publish.py` | `verify_structure` 同文件（`src == out`）走快速路径：只查目录升序与寻址，不再拿文件自比自；计数/声明检查留给写前 `_verify_copy` |
| `core/pack_build.py` | `allow_create` 支持「只允许这些路径新建」；重组分支先清空 `added/replaced`；`need_rebuild` 为真时不再先整包复制 |
| `core/assets.py` | 新增 `release_pack()`：写回同一个包前放掉句柄 |
| `ui/save_workflows.py` | 按路径计算 `create_paths`；`_pack_sources(for_pack_write=)`——散装另存仍保护输出包；写法一：写回自己输出包前 `release_pack`，失败/取消后重新挂载 |
| `ui/import_queue.py` | adopt 时设置 `output_pack`；往自己的输出包导入时也记住它 |
| `ui/source_actions.py` | 待入叶子恢复挪到 `_set_document` 之后；编码切换/F5 重建保留 `output_pack`/`origin_pack` |
| `ui/batch_import.py` | 表格路径先规范化（去空格、`\`→`/`），`entries()` 再校验一次 |
| `docs/STATUS.md` | 测试总数 708 → 744（本轮后 756） |

## 回归

新增 12 项：

- `test_pack_copy_many.py`（+4）：同文件二次保存校验、重组不重复计图、
  重组不先复制、选择性允许新建路径；
- `test_gui_batch_import.py`（+7）：已有布局标签上批量保存、队列文档记
  输出包、往自己的输出包再导入、写前释放句柄、刷新保留待入叶子、散装
  另存拒绝输出包、编码切换保留 output_pack；
- `test_gui_import.py`（+1）：批量对话框路径规范化。

全套 **756 项：755 通过、1 跳过、0 错误**；`ruff check` 0；
`check_windows_compat` 0/0/0。

边界：Windows 句柄问题按平台语义修复，沙箱（Linux）无法复现系统错误码，
仍需 Windows 实机跑「第二次 Ctrl+S」确认。
