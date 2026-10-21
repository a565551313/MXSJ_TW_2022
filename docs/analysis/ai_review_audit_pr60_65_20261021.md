# PR #60–#65 AI 代码审查复核

- 复核日期：2026-10-21（Asia/Shanghai）
- 复核基线：`master` `69994778de5792ed684c3efb91405376e0771d18`（PR #67 合并后，ui_editor 0.12.6）
- 复核对象：PR #60–#65 里 `gitar-bot[bot]` 与 `coderabbitai[bot]` 的**全部**行内审查意见（review 摘要只是重复行内意见，已去重）
- 复核方法：读当前代码 + 纯逻辑动态复现；GUI 像素路径用几何/纯数据复现（沙箱未安装 PySide6，未跑 GUI 像素测试）。非 GUI 的 94 项相关测试（`test_asset_export`、`test_pack_build`、`test_slicing`、`test_fidelity`、`test_dir_base`、`test_image_export_safety`、`test_interface_probe_stats`）全部通过。

> 先说结论：**六个 PR 都是已合并（MERGED），不是关闭未合并。** 去重后共 **23 条** AI 审查意见：**3 条已修复、2 条部分修复、18 条仍属实且未修复、0 条完全失实**。但其中若干条只是措辞或时间口径不准，问题本体仍成立（见 §7）。
>
> **2026-10-21 修复结果（ui_editor 0.12.7）**：按用户「只修属实意见」的授权，18 条「属实未修」全部落地，#60-1 的剩余半边（磁盘既有同名文件）也补上，#65-1 的「快照/§1/§2 未更新」子项随 `docs/STATUS.md` 更新；**#65-1 的「未来日期」不成立、不改**，**#62-2 的「回归」措辞不改**（问题本体已修）。逐条结果见 §10。

## 0. 总览

> 各表「判定」列保留复核当时的结论，**`→` 之后是 2026-10-21 的修复状态**；
> 「当前状态与证据」列仍是复核时的证据，修复后的实现见 §10。

| PR | 去重后意见 | 已修复 | 部分修复 | 属实未修 |
|---|---:|---:|---:|---:|
| #60 导出素材 | 3 | 2 | 1 | 0 |
| #61 对齐夹父 / 保存 | 2 | 0 | 0 | 2 |
| #62 原生还原度 | 6 | 0 | 0 | 6 |
| #63 角标/标签/替换布局 | 7 | 1 | 0 | 6 |
| #64 拼名族实测 | 2 | 0 | 0 | 2 |
| #65 批量导出 | 3 | 0 | 1 | 2 |
| **合计** | **23** | **3** | **2** | **18** |

**复核当时最值得先修的 6 条**（会造成可见错误或数据损失；均已于 2026-10-21 修复）：

1. [#62-1] 单图九宫格只画四个象限，放大时中间出现十字空洞（**0.12.0 引入的回归，复核时仍存在**）。
2. [#60-1 剩余部分] 「转成图片」批量导出会覆盖目标文件夹**已存在**的同名文件（README 宣称不覆盖）。
3. [#61-1] 对齐/分布夹父用的是原始 `iWidth/iHeight`，图片尺寸控件（宽高为 0）夹不住。
4. [#65-2] `.spr` 连带帧图被拒时，状态栏点名的是 `.spr`（其实 `.spr` 已写出），真正的被拒文件没说。
5. [#63-6] 替换散装布局后切换文本编码，会丢掉「原地替换」的脏状态，关标签时不提示就丢弃替换内容。
6. [#64-1] `_looks_plain_text` 把 GBK 的 `ui.lst` 判成密文，可能解包成乱码（仓库自带 fixture 已复现）。

## 1. PR #60（0.10.6 导出素材）

| # | 来源 | 位置 | 意见 | 判定 | 当前状态与证据 |
|---|---|---|---|---|---|
| 60-1 | gitar ⚠️ / CodeRabbit 🟠 | `ui_editor/src/ui_editor/ui/commands.py:479-501`；`ui_editor/src/ui_editor/ui/image_export.py:45-55` | 「转成图片」批量导出同名静默覆盖，目录里已有同名文件也被覆盖 | **部分修复** → ✅ **已补（2026-10-21，0.12.7：磁盘既有文件也加序号）** | 批次内同名已修：`export_widget_assets` 传入共享 `used_names`，`_reserve_names` 会加 `-2` 后缀（`test_convert_same_basename_does_not_overwrite` 覆盖）。但 `_reserve_names` **只查本批 `used` 集合，不查磁盘**。实测：目标目录预存 `btn.png`，`export_image_files("a\\btn.png", PNG, None, dest, used_names=set())` 仍写回 `btn.png` 并覆盖旧内容。README 0.10.6 节「不覆盖目标文件夹里的既有文件」对这条入口仍不成立（0.12.6 节只承诺批次内不覆盖，单张导出才允许覆盖）。 |
| 60-2 | gitar 💡 / CodeRabbit 🟡 | `commands.py:477,482-484,507`；`core/asset_export.py:184-189,238-259` | 多选共享素材重复导出成 `btn-2.png` | **已修复** | 新增 `source_key`/`seen`，跨控件与 `.spr` 连带帧图都去重；`test_convert_shared_asset_exported_once`、`test_raw_shared_asset_exported_once`、`test_spr_frame_source_not_duplicated` 覆盖。 |
| 60-3 | gitar 💡 | `core/asset_export.py:191-202`；`commands.py:494-524` | `guard_output` 中途拒绝时已写文件不汇报、整批中止 | **已修复** | `rejected` 收集器逐目标继续，`written` 保留；状态栏同时报「已导出」与「被拒绝」。`test_rejected_target_does_not_abort_remaining`、`test_all_rejected_reports_reason` 覆盖。 |

## 2. PR #61（0.11.1–0.11.2）

| # | 来源 | 位置 | 意见 | 判定 | 当前状态与证据 |
|---|---|---|---|---|---|
| 61-1 | gitar ⚠️ | `ui_editor/src/ui_editor/ui/main_window.py:486-493`；对照 `core/snap.py:129-148`、`ui/canvas.py:117,166`、`ui/commands.py:110` | 对齐/分布夹父用原始宽高，未用 `effective_size` | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `_clamp_in_parent` 仍传 `(parent.width, parent.height)` 与 `widget.width, widget.height`。`snap.clamp_in_parent` 的文档明确要求「父的**有效**像素尺寸」。实测：父 `iWidth=0`（图片宽 400）、子 x=1000 时返回 `(1000, 0, False)`，不夹；按有效尺寸 `(400,300)` 才返回 `(300, 0, True)`。图片尺寸控件很常见，右/下对齐仍会越界且不报「被夹」。 |
| 61-2 | gitar 💡 | `ui_editor/src/ui_editor/ui/save_workflows.py:273-288` | 「目标文件夹不存在」检查在保存前复核弹窗之后，用户白点一次 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `_write_to` 顺序仍是：`guard_output`(279) → `_confirm_save_review`(280，模态) → `_require_save_encoding`(282) → dump(283) → `target.parent.is_dir()`(285)。属于体验问题，不是写坏文件。 |

## 3. PR #62（0.12.0 画布原生还原度）

| # | 来源 | 位置 | 意见 | 判定 | 当前状态与证据 |
|---|---|---|---|---|---|
| 62-1 | gitar ⚠️ / CodeRabbit 🟠 | `ui_editor/src/ui_editor/core/painters.py:331-370` | 单图九宫格只画 4 个角象限，放大时中间十字不画；角是 1/2 不是 1/3 | **属实未修（回归）** → ✅ **已修（2026-10-21，0.12.7）** | 当前 `_paint_nine` 仍用 `Piece(W,H)` 建九块，`slicing.layout(..., W, H)` 会把左右/上下都压成 `W/2`、中列/中行变 0 并被丢弃。实测 `slicing.layout(nine_slice((Piece(30,30),)*9), 30, 30)` 只有 4 个 cell（index 0/2/6/8），每块 15×15。目标大于原图时 `_map_axis` 把四块按原尺寸钉在四角，中间留下 `target-W` 的十字空洞。对照 PR #61 合并点 `52b3dd4` 的旧实现：`sw, sh = pixmap.width()/3.0, ...`，九块完整、边/中心拉伸——所以这是 0.12.0 引入的**可见回归**。 |
| 62-2 | gitar ⚠️ | `painters.py:550-565`；`core/fidelity.py:143-148,178-188` | 目录切片按钮丢失 pressed/hover/disabled 预览，角标仍报「原生」 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）**（「回归」措辞不完全准确） | `_paint_button` 在 `_draw_slice` 成功后直接 `return`，`_simulate_state_overlay` 只存在于非切片分支；`_draw_slice` 完全不读 `ctx.button_state`。实测 `fidelity.markers`：`normal` 与 `pressed` 都只返回 `native_h_slice`，没有 `state_overlay`/`state_by_frame_order`。补充：PR #61 合并点的旧代码对目录型按钮也是走「样式底色」分支、同样没有状态预览，所以更准确的说法是**旧限制在新画法下变得自相矛盾**；0.12.5 起 `h_state` 真有 `0l/0c/0r…` 态切片，但 `fetch_slice` 固定取 0 号态，状态预览依旧无效。 |
| 62-3 | gitar 💡 | `ui_editor/tools/interface_probe.py:303-305` | `print("切片族实例：" + join(...) or "（无）")` 的 `or` 永远不生效 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `+` 优先级高于 `or`；实算空 `families` 时输出就是裸的 `'      切片族实例：'`，`（无）` 永不显示。下一行 `按钮状态字段出现次数` 已正确加了括号，这一行没加。 |
| 62-4 | gitar 💡 / CodeRabbit nit | `painters.py:230-244` | 每个切片 cell 每次重绘都 `QPixmap.fromImage` | **属实未修（性能）** → ✅ **已修（2026-10-21，0.12.7）** | `_draw_slice` 仍逐 cell 转换，没有用 `PaintContext._pixmaps` 缓存；拖动/缩放时每个切片控件每帧最多 9 次 QImage→QPixmap 上传。 |
| 62-5 | CodeRabbit 🟡 | `ui_editor/src/ui_editor/ui/main_window.py:458-472`；`ui/window_setup.py:306-319` | 切换按钮状态后不刷新状态栏保真度标签 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `set_button_state` 只刷新画布与状态栏提示，没有调用 `_update_fidelity_label(self._selected)`；后者唯一调用点是 `main_window.py:323` 的 `_select_widget`。标签会一直显示切换前的分类，直到重新选中控件。 |
| 62-6 | CodeRabbit 🟡 | `ui_editor/tools/interface_probe.py:121-141` | JPEG 扫描不跳过 `0xFF` 填充字节，带填充的 SOF 读不到尺寸 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | 当前循环在 `data[index] == 0xFF` 后直接读 `index+1` 当 marker、`index+2..4` 当长度。实测：同一张最小 JPEG，SOF 前多一个 `0xFF` 时 `image_size` 返回 `None`；去掉填充后返回 `(80, 100)`。`test_interface_probe_stats` 只测普通 JPEG，未覆盖填充字节。 |

## 4. PR #63（0.12.1–0.12.4）

| # | 来源 | 位置 | 意见 | 判定 | 当前状态与证据 |
|---|---|---|---|---|---|
| 63-1 | gitar ⚠️ / CodeRabbit 🟡 | `ui_editor/src/ui_editor/core/diagnostics.py:294-321` | `RENDER_STYLE_SKIN` 对目录型按钮误报，和画布切片画法矛盾 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | 仍用 `not name.endswith(("\\", "/"))` 判「不可解析」，没有 `dir_base.plan`、没有代码皮肤、也没校验 `ButtonNormalColor` 能否解析。实测：`CTextButton`、`sFileName="btn\\"`、`iStyle=3`（有 `ButtonNormalColor`）时同一份诊断同时输出 `RESOURCE_DIR_BASE`（拼名族提示）和 `RENDER_STYLE_SKIN`（说图片不可用）。 |
| 63-2 | gitar 💡 / CodeRabbit 🟡 | `painters.py:504-528` 对照 `578-607` | `resolve_source` 漏掉 `lNormalColor`，角标文案标错来源 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `_paint_text_button` 先取 `lNormalColor`，再取 iStyle；`resolve_source` 只看 `style_button_color()`（只读 `ButtonNormalColor`）。两种情形都会标错：iStyle 无颜色 → 标「模拟/编辑器默认色」（实际是 `.dlg` 颜色）；iStyle 有颜色 → 标「ui.lst 配色」（实际是 `lNormalColor`）。 |
| 63-3 | CodeRabbit 🟡 | `painters.py:29,33-43` | `PaintContext` 在 `button_state` 前插入 `show_badges`，破坏位置参数兼容 | **属实未修（影响有限）** → ✅ **已修（2026-10-21，0.12.7）** | 对照 `52b3dd4`：旧顺序是 `assets, styles, show_names, button_state, animation_frame, code_skins, _pixmaps`；当前 `show_badges` 插在第 4 位，后续全部后移。仓库内 5 处构造全部用关键字参数，故当前无实际故障；但 `PaintContext` 在 `__all__` 里是公开类，外部按位置构造会静默错位。 |
| 63-4 | CodeRabbit 🟡 | `ui_editor/src/ui_editor/ui/tab_menu.py:161-175` | 「关闭其他标签」第二段结果覆盖第一段状态栏 | **已修复** | 现为 `_close_range` 两段各自返回计数，`total = tuple(sum(...))` 后只 `_report_batch_close` 一次；CodeRabbit 标注的「Addressed in 93efaef」属实。 |
| 63-5 | gitar 💡 | `ui_editor/src/ui_editor/ui/replace_layout.py:60-101` | 替换已打开的包内布局时资源树不显示「待入包」标记 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `replace_layout_with` 在已开标签分支只 `_activate_session(index)` + `_set_document(doc)`，然后 `reveal_selection(key)`。`_set_document` 只 `clear_pending()`（`main_window.py:169`）不 `show_pending`；`show_pending` 只在 `_activate_session`（`window_setup.py:493-495`）里对**旧**文档做。`prepare_layout_import` 确实会给新文档 `begin_pack_import`（`layout_import.py:78`），所以标记被清掉后要切走再切回才出现。 |
| 63-6 | CodeRabbit 🟡 | `ui_editor/src/ui_editor/ui/source_actions.py:33-68`；`replace_layout.py:131-136` | 切换编码时丢掉「原地替换」基线/脏状态 | **属实未修（可静默丢改动）** → ✅ **已修（2026-10-21，0.12.7）** | `change_text_encoding` 重建 `LayoutDocument.from_dicts` 后只补了 `pending_pack_import` 分支，没有对 `begin_inplace_replace` 的文档重放基线。`begin_inplace_replace` 只设 `dirty=True`、不设 `pending_pack_import`（`model.py:148-155`），于是新文档 `dirty=False`、`pending_pack_import=False`；`_confirm_discard` 不会拦，关标签直接丢弃刚替换进来的内容。 |
| 63-7 | CodeRabbit 🟡 | `ui_editor/src/ui_editor/ui/window_setup.py:333-355` | 帧滑块范围变小时只夹滑块值，不同步 `ctx.animation_frame` | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `blockSignals(True)` → `setRange` → `setValue(min(...))` → `blockSignals(False)` → 只 `_refresh_frame_readout`；没有在夹值后调用 `_set_animation_frame`。读数显示被夹后的帧，画布仍按旧 `ctx.animation_frame` 取帧。 |

## 5. PR #64（0.12.5 拼名族实测）

| # | 来源 | 位置 | 意见 | 判定 | 当前状态与证据 |
|---|---|---|---|---|---|
| 64-1 | gitar 💡 | `ui_editor/src/ui_editor/core/pack_build.py:197-208` | 95% 可打印阈值把 GBK 的 `ui.lst` 判成密文 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | 仍只把 ASCII 32–126 + Tab/LF/CR 算可打印。实测仓库自带 fixture `b"[Font]\n\xa7\xba\xc5\xe9 12 400 0\n"`：`_looks_plain_text` 为 `False`，`_recover_key_by_frequency` 返回 `b'\x00o\x00\x00'`（非零），`unpack_packed_text` 输出 `b'[)ont2\\n\xa7\xba\xaa\xe9 1] 40_ 0\\n'` —— 已被打乱。真实 69,300 B 的 `ui.lst` 若头部 GBK 占比足够高也会走同一条路；是否打乱取决于频率启发式是否恰好返回零密钥。影响：`fetch_styles` 静默拿不到样式；`replace_dlg_entry`/`_plan_patch` 的「不是 .dlg 条目」保护（`pack_build.py:251,349`）会失效。 |
| 64-2 | gitar 💡 | `core/dir_base.py:1-30`；`docs/EXTERNAL_CORPUS.md:164,167,179`；`ui_editor/README.md:74,78`；`docs/STATUS.md:1392-1393` | 实测数字在不同文件互相矛盾 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | `dir_base.py`：2,697 篇 `.dlg` / 九片 124 / 横三片 105 / 单图 10；`EXTERNAL_CORPUS.md` §5.1：2,708 篇 / 九片 130 / 横三片 109 / 三态 36 / 单图 9，但同文件第 179 行又写九片 124；README 0.12.5：九片 130 / 横三片 145 / 测试 575；STATUS 0.12.5 行：测试 578；0.12.6 行：测试 592。至少 `.dlg` 数、九片数、横三片口径、测试数四处不一致。 |

## 6. PR #65（0.12.6 批量导出）

| # | 来源 | 位置 | 意见 | 判定 | 当前状态与证据 |
|---|---|---|---|---|---|
| 65-1 | CodeRabbit 🟡 | `docs/STATUS.md:16,20-27,30-40,1392` | 行日期未来化、快照/§1–§2 未更新、未记 0.12.6 结果 | **部分属实 / 未修复** → ◐ **日期不改（不实）；快照/§1/§2 已随 0.12.7 更新** | 子claim「2026-10-21 在未来」**不成立**：项目口径是 Asia/Shanghai，PR #65 合并于 2026-10-20 21:49 UTC = 2026-10-21 05:49 CST，0.12.6 行写 10-21 正确。**但**快照仍写 `2026-10-19`，§1 仍写会话分支 `arena/e0fb7c91` / 起点 PR #54 / 集成边界 0.11.0，§2 的 UI 编辑器仍写 0.11.0 —— 按 STATUS 自己的规则确实没更新；§2 也没有 0.12.6 的 592+1 skip 结果。§6 行已存在。 |
| 65-2 | CodeRabbit 🟡 | `core/asset_export.py:191-199` | 被拒时记录 `name`（主资源）而不是该 target 的真实来源 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | 仍是 `for filename, data, _source in targets:` + `rejected.append((name, str(exc)))`。实测：`anim\x.spr` 连带 `real.igs`，目标目录预存悬空链接 `real.png`；结果 `written=['x.spr']`，`rejected=[('anim\\x.spr', '拒绝写入符号链接…real.png')]` —— `.spr` 明明写成功了，状态栏却把它列为被拒。CodeRabbit 给出的 diff（用 `source`）正确。 |
| 65-3 | CodeRabbit 🟡 | `ui_editor/tests/test_asset_export.py:261-279`；`ui_editor/tests/test_gui_asset_export.py:161-186` | Windows 无符号链接权限时测试报错而非跳过 | **属实未修** → ✅ **已修（2026-10-21，0.12.7）** | 4 处 `(self.dest / ...).symlink_to(...)` 都没有 `try/except OSError` + `skipTest`。同仓库其它测试用 `os.link`（`test_image_export_safety.py:20,33`、`test_write_safety.py:38`），正是为了避开 Windows 符号链接权限。 |

## 7. 审查意见本身不准确 / 需要修正口径的地方

1. **#65-1 的「未来日期」**：按项目 `Asia/Shanghai` 口径，0.12.6 行写 `2026-10-21` 是对的；错的是快照与 §1/§2 没更新。CodeRabbit 用 UTC 日期判断，结论方向对、理由错。
2. **#62-2 的「回归」**：目录型按钮在 0.12.0 之前也**没有**状态预览（走样式底色分支），不是「原来有、现在丢了」。现在的问题是：切片成功即返回 + 角标只报原生，状态切换静默无效，且 0.12.5 已有真实 `h_state` 切片却仍固定画 0 号态。
3. **#60-1 的「状态栏报两个 btn.png」**：批次内同名已由 0.12.6 修掉，这部分现在不再成立；仍成立的是「目标目录已有同名文件会被覆盖」。
4. **#62-1、#62-3、#62-6、#64-1、#65-2** 的描述与当前代码/实测完全对得上，可直接按建议修。
5. **#63-4** 的「已修复」标记属实。

## 8. 建议修复顺序

| 优先级 | 条目 | 理由 / 建议改法 |
|---|---|---|
| P0 | 62-1 | 恢复 `sw, sh = W/3.0, H/3.0` 的源网格，按 index 映射 src/dst；补大于原图、非 3 倍数、宽高 <3 的像素测试。 |
| P0 | 60-1 剩余 | `_reserve_names` 同时检查磁盘已存在文件（或批量转换改走 `unique_target`）；同步 README 口径。 |
| P1 | 61-1 | `_clamp_in_parent` 改用 `painters.effective_size(parent/widget, self.ctx)`；补宽高为 0 的夹父测试。 |
| P1 | 65-2 | `rejected.append((source, str(exc)))`；状态栏用真实来源名。 |
| P1 | 63-6 | 文档保存 `inplace_replace` 标记/基线，重建后重放 `begin_inplace_replace`；补「替换→切编码→关标签」用例。 |
| P1 | 64-1 | `_looks_plain_text` 改为只统计 C0 控制字节（Tab/LF/CR 除外），GBK 高位字节算文本；补 GBK `ui.lst` 往返用例。 |
| P2 | 62-2 / 63-2 / 63-1 / 63-5 | 统一切片按钮的「状态预览 + 角标 + 诊断」来源判定；用 `resolve_source`/`fetch_slice` 做唯一 oracle。 |
| P2 | 63-7 / 62-5 / 61-2 | 都是小改动，顺手修。 |
| P3 | 62-3 / 62-4 / 62-6 / 63-3 / 64-2 / 65-3 | 工具输出、缓存、JPEG 头解析、dataclass 字段顺序、文档数字、测试跳过。 |

## 9. 复核限制

- ~~沙箱没有 PySide6，没有跑 GUI 像素测试~~（**2026-10-21 补记**：之后在沙箱用
  PySide6 6.7 + 手写桩库以 `QT_QPA_PLATFORM=offscreen` 跑起了 GUI 测试；
  0.12.7 的新用例含真实 `QPainter` 像素断言。它仍不能替代 Windows 客户端
  像素级比对）。复核当时：#62-1/#62-2 的绘制结论来自 `slicing.layout` 纯几何复现与 `fidelity.markers` 纯逻辑复现，以及 PR #61 合并点 `52b3dd4` 旧源码对照（通过 GitHub API 取回）。
- 仓库是浅克隆（只有 1 个 commit），PR 内更早的历史用 GitHub API 的 `contents?ref=<sha>` 取回核对。
- 复核当时未修改任何产品代码；修复在 2026-10-21 的 0.12.7 单独落地（见 §10）。

## 10. 修复结果（2026-10-21，ui_editor 0.12.7）

用户授权「只修属实的意见，不实的项不改」。23 条里 21 条的**问题本体**已落地，
另 2 条只改文档或不改措辞。全部改动未提交、未开 PR；版本号 `0.12.6 → 0.12.7`。

| # | 复核判定 | 修复动作 | 用例 |
|---|---|---|---|
| 60-1 | 部分修复 → **已补** | `_reserve_names(names, used, dest)` 额外查 `dest/name` 是否存在，整组加序号；单张导出（`used is None`）仍覆盖 | `test_batch_does_not_overwrite_existing_files_on_disk`、`test_batch_keeps_all_frames_clear_of_existing_files` |
| 60-2 / 60-3 | 已修复 | 不动 | — |
| 61-1 | 属实未修 → **已修** | `_clamp_in_parent` 改用 `painters.effective_size` | `test_image_sized_child_is_clamped_with_effective_size`、`test_image_sized_parent_is_clamped_with_effective_size` |
| 61-2 | 属实未修 → **已修** | `_write_to` 的目标目录检查前移到 `_confirm_save_review` 之前 | 现有保存用例 |
| 62-1 | 属实未修（回归）→ **已修** | 新增 `slicing.nine_thirds_cells`（W/3、H/3，宽高 <3 与不整除夹边界）；`painters._paint_nine` 改用它 | `TestSingleImageThirds` 5 项（放大中心/边中段有像素） |
| 62-2 | 属实未修 → **已修**（措辞不改） | `assets.fetch_slice_state` 取 `{n}l/{n}c/{n}r`；`_paint_button` 有真态按态号画、无真态回退模拟蒙版；`fidelity` 新增 `state_slice_by_index/state_overlay` | 真态切片/无真态回退/缓存 3 项 |
| 62-3 | 属实未修 → **已修** | 「切片族实例」一行抽出 `format_families()`（空表→`（无）`），`or` 不再被 `+` 吃掉 | `TestFormatFamilies` 2 项 |
| 62-4 | 属实未修（性能）→ **已修** | `_draw_slice` 走 `ctx._pixmaps`（key 带 `#slice`） | `test_slice_cells_are_cached_between_paints` |
| 62-5 | 属实未修 → **已修** | `set_button_state` 调 `_update_fidelity_label` | `test_button_state_switch_refreshes_fidelity_label` |
| 62-6 | 属实未修 → **已修** | `image_size` 跳过 marker 前连续 `0xFF` | 实测带填充/普通/PNG 三种 |
| 63-1 | 属实未修 → **已修** | `diagnostics` 皮肤豁免改与画布同判（`_parses_rgb` / `_code_skin_available` / `dir_base.plan`） | `test_diagnostics` 现有族用例 |
| 63-2 | 属实未修 → **已修** | `resolve_source` 先认 `lNormalColor` → `SOURCE_DLG_COLOR` | `test_lnormal_color_badge_matches_painter` |
| 63-3 | 属实未修（影响有限）→ **已修** | `PaintContext.show_badges` 移到字段末尾 | 构造处全用关键字，结构性修复 |
| 63-4 | 已修复 | 不动 | — |
| 63-5 | 属实未修 → **已修** | `replace_layout_with` 重挂 `show_pending` 并定位 | `test_second_replace_keeps_pending_marker`、`test_second_replace_reveals_pending_leaf` |
| 63-6 | 属实未修（可静默丢改动）→ **已修** | `change_text_encoding` 重建后按 `inplace_replace` 基线重放 `begin_inplace_replace` | `test_switch_keeps_inplace_replace_dirty_state`、`test_switch_after_save_does_not_revive_replace_state` |
| 63-7 | 属实未修 → **已修** | 夹值后帧号变化即 `_set_animation_frame`，未变化只刷读数 | `test_shrinking_range_moves_canvas_to_clamped_frame`、`test_unchanged_frame_is_kept_on_refresh` |
| 64-1 | 属实未修 → **已修** | `_looks_plain_text` 改看 C0 控制字节（Tab/LF/CR 除外）+ DEL 占比 ≤2% | `test_pack_build` 增 GBK 明文用例 |
| 64-2 | 属实未修 → **已修** | `dir_base.py` 2,697/124 → 2,708/130；`EXTERNAL_CORPUS.md` 124 → 130；README 0.12.5 575 → 578 | 文档 |
| 65-1 | 部分属实 → **日期不改** | 「10-21 在未来」不成立（CST）；快照/§1/§2 已随 0.12.7 更新 | 文档 |
| 65-2 | 属实未修 → **已修** | `rejected.append((source, str(exc)))` | `test_rejected_target_does_not_abort_remaining` |
| 65-3 | 属实未修 → **已修** | 两处测试改用 `dangling_link()`，无权限 `skipTest` | 同上（Linux 正常建链） |

**验证**：`ui_editor` 全套 **615 项**（新增 23 项）——613 项无失败（含 1 跳过）、
2 项 `QMenu already deleted` 错误；这 2 项在改动前基线 `6999477`（592 项）上同样
失败，不是本轮引入。纯逻辑 `tests.test_slicing` 19 项全 OK。沙箱用
PySide6 6.7.0 + 手写 `libGL/libEGL/libxkbcommon/libdbus` 桩库、`offscreen` 平台
运行，只能证明绘制路径不崩与合成夹具上的像素断言；`ruff check` 0、
`check_windows_compat` 0/0/0。**真实客户端像素级一致仍未验**。

**边界**：没改 `mock_server` 相关代码；Windows 实机结论（mock_server_v2 全链路）
来自用户口述，记在 `docs/MOCK_SERVER.md` 与 `MOCK_SERVER_V2_README.md`，本文件
不据此宣称认证／事务安全。
