# PR #72 AI 审查复核

- 复核日期：**2026-10-22**（Asia/Shanghai）
- 复核对象：PR #72（`arena/b7f9eeb4-mxsj-tw-2022` → `master`，ui_editor 0.13.6，
  head `aaf976d`）
- 审查来源：`gitar-bot[bot]`（5 条行内）、`coderabbitai[bot]`（15 条行内 +
  3 条「范围外」+ 1 条 nitpick），共 **24 条评论**
- 复核方法：逐条读**当前**代码（不是评论所附的旧 diff），能在沙箱复现的就跑；
  真包 `interface.fls`（614,482,967 B / 53,556 条）只读，不写回
- 用户要求：「检查 #72 的 pr 有 ai 审查，复核一下是否属实」——**只改属实的**，
  不照抄机器人的改法，也不为措辞改日期或伪造回归历史

## 0. 结论

24 条评论去重后 **18 个问题**：

- **16 个属实（其中 1 个部分属实），本轮修掉**（11 处代码 + 5 处文档/证据）；
- **2 个在先前提交已经修好**：族标签/子图缓存（gitar 4344440189，`aaf976d`）、
  README 测试分类（coderabbit 4344719964，`1e607d0`）；
- 其中 README 的族类型优先级（coderabbit 4344481640）在 `4f9f7ec` 只改了
  后半段，旧段仍写「控件只在认不出来时兜底」，本轮补全；
- **没有需要驳回的失实条目**，也没有「评论说的现象不存在」的情况。
  少数评论引用的是旧行号/旧数字（评论时文件还没到 `aaf976d`），但同类问题
  在当前代码里仍然存在，按「属实」处理并修掉。

| # | 评论 | 位置（评论时） | 判定 | 处理 |
|---|---|---|---|---|
| 1 | gitar 4344440111 | `ui/property_panel.py:516` | 属实 | 保留族内相对路径 |
| 2 | gitar 4344440189 | `ui/image_picker.py:942` | 已修（`aaf976d`），实测 0 次重复查询 | 不改 |
| 3 | coderabbit 4344481634 | `docs/STATUS.md:68` | 属实（旧行号；685+2≠686 的分类问题） | 统一分类写法 |
| 4 | coderabbit 4344481637 | `ui_editor/README.md:47` | 属实 | 说明候选名范围 |
| 5 | coderabbit 4344481640 | `ui_editor/README.md:55` | 部分属实（旧段仍矛盾） | 补全优先级说明 |
| 6 | coderabbit 4344481643 | `ui_editor/README.md:171` | 属实 | 统一分类写法 |
| 7 | coderabbit 4344481645 | `core/dir_base.py:351` | 属实 | 删重复候选 |
| 8 | coderabbit 4344481658 | `ui/image_picker.py:330` | 属实（Major） | 预览同时限宽 |
| 9 | coderabbit 4344481661 | `ui/image_picker.py:396` | 属实 | 缺图不拼半张 |
| 10 | coderabbit 4344481666 | `ui/image_picker.py:427` | 属实 | 预览按键缓存 |
| 11 | coderabbit 4344676155 | `interface_names_20261022.json:26` | 属实 | 736 → 9,310 |
| 12 | coderabbit 4344719951 | 同上 | 属实（重复） | 同上 |
| 13 | coderabbit 4344719958 | `docs/STATUS.md:70` | 属实 | 统一分类写法 |
| 14 | coderabbit 4344719964 | `ui_editor/README.md:108` | 已修（`1e607d0`） | 不改 |
| 15 | gitar 4344983785 | `core/fidelity.py:218` | 属实 | 逐轴比较 |
| 16 | coderabbit 4345060152 | `fidelity_autosize_20261022.json:9` | 属实 | 补全 SHA-256 |
| 17 | coderabbit 4345060156 | `docs/STATUS.md:2291` | 属实 | 统一分类写法 |
| 18 | coderabbit 4345060158 | `core/fidelity.py:205` | 属实（与 15 同一问题） | 逐轴比较 |
| 19 | coderabbit 4345060165 | `tests/test_fidelity.py:149` | 属实 | 改成「用途与顺序未核实」 |
| 20 | gitar 4345179726 | `ui/image_picker.py:696` | 属实 | 刷新行作废缩略图 |
| 21 | coderabbit（范围外） | `ui/image_picker.py:763` | 属实（Major） | 旧族遮挡时拦住 |
| 22 | coderabbit（范围外） | `ui/save_workflows.py:242-246` | 属实（Major） | 取消不再删目标 |
| 23 | coderabbit（范围外） | `ui/image_picker.py:383-385` | 属实 | 空 `pairs` 单独提示 |
| 24 | coderabbit（nitpick） | `ui/save_workflows.py:150-154` | 属实 | 改成显式参数 |

## 1. 代码问题（11 处）

### 1.1 九片子图提示只剩文件名（#1，属实）

`asset.family_pieces()` 返回的是**完整路径**（`…\top\left.png`）；旧实现
`piece.replace("\\", "/").split("/")[-1]` 只留最后一段，九片每行的
`top/left`、`middle/left`、`bottom/left` 全变成 `left.png`。实测真包有
**130 个九片基路径**，提示里三行同名，用户分不清哪张是哪块。

改法：按基路径前缀裁（兼容 `/`、`\` 两种写法），返回 `top/left.png` 这样的
族内相对路径；前缀对不上时才退回文件名。位置：`ui/property_panel.py:508`。
回归：`test_property_panel_pieces_keep_the_row_folder`。

### 1.2 重挂同名图后缩略图不换（#20，属实）

`add_staged_path` 为了不重建整表，改成 `_refresh_row` 就地改文字/提示；但
`_thumb_done` 里还留着这个路径，`_fill_thumbs` 会跳过，列表一直显示旧图，
直到下一次过滤。触发场景：`_stage_one` 替换包里已有同名图（确认
「这个名字已在包里」后）、`_stage_family` 重挂同一族。

改法：`_refresh_row` 里 `_thumb_done.discard(path)`、置空白图标并重新排缩略图。
位置：`ui/image_picker.py:811`。回归：`test_refresh_row_drops_stale_thumbnail`
（同一路径先红后蓝，刷新后必须变蓝）。

### 1.3 `middle/middle` 被数两遍（#7，属实）

`_PROBE_STEMS` 先由九片生成式产出 `middle/middle`，候选表末尾又手写了一次。
复现（修复前）：

```
dir_base.probe_pieces('a/', lambda p: p == 'a/middle/middle.png')
# ('middle/middle.png', 'middle/middle.png')
```

只有一张图的目录会在选图窗里显示「里面有 2 张」。改法：删掉手写的那一个
（九片生成式保留），位置 `core/dir_base.py:377`。回归：
`test_probe_does_not_double_count_middle_middle`。

### 1.4 拼接预览只限高、不限宽（#8，Major，属实）

旧 `_montage` 的缩放因子只有 `max_height / tallest`。三张 1000×40 的横片
`tallest=40` → `scale=1.0` → 画布宽 3000 px；`QLabel.setPixmap` 的
sizeHint 会把对话框撑到屏幕外。改法：同时按整行最大宽度算
`max_width / widest`，上限 480 px；位置 `ui/image_picker.py:339`。
回归：`test_family_preview_width_is_capped`（三张 1000×40 → ≤480 px）。

### 1.5 缺一张图仍拼半张（#9、#23，属实）

旧 `_update_picture` 把读不出的 `QImage` 直接过滤掉：`0l` 读不出、`0c/0r`
正常时，按钮横片预览只显示两格，caption 却写「三片拼成一条」；九片缺一块
会让后面每格错位。另外 `pairs` 为空（张数与族类型对不上）时也落到
「`.igs` 精灵没法预览」，原因说错了，旧 caption 还留在界面上。

改法：`pairs` 为空单独提示；任一张读不出就清图并说明（全读不出才说
`.igs`）；清掉旧 caption。位置 `ui/image_picker.py:383`。回归：
`test_family_preview_refuses_partial_montage`。

### 1.6 改目录路径每个按键重解预览（#10，属实）

`_base.textChanged → _refresh → _update_picture`，每次都 `QImage(path)` 解码
全部选中图片。多张大图时输入目录会明显卡。改法：按
`(族类型, 文件清单)` 缓存结果，图没变直接返回；换族类型或换图才重拼。
位置 `ui/image_picker.py:383`。回归：
`test_family_preview_not_redecoded_for_base_edits`（改三次目录 0 次解码，
换族类型后 >0 次）。

### 1.7 只写一个轴时误报「原生 1:1」（#15、#18，属实）

`painters.effective_size` 是**逐轴**兜底的：`iWidth=300, iHeight=0` +
120×44 的图，画布画 300×44（横向拉伸）；旧 `fidelity.markers` 只看
`width > 0 and height > 0`，两轴不齐就当成「没写尺寸」→ `native_1to1`。
状态栏与画布不一致，正是 0.13.5 要修的那类问题。

改法：先用图片尺寸补齐非正轴，再与图片尺寸逐轴比较；缺的轴补上后相等仍
报 1:1，不等报拉伸。位置 `core/fidelity.py:208`。回归：
`test_one_missing_axis_is_compared_per_axis`（300×0 → 拉伸；0×30 → 拉伸；
120×0 → 1:1）。

### 1.8 多帧整图把「其余帧是悬停/按下」写成事实（#19，属实）

旧文案「其余帧留给悬停/按下（序号语义未核实）」把**帧的用途**写成了事实，
只把序号标为未核实。真包只能证明「有几帧」，不能证明第几帧是什么态。

改法：改成「其余帧用途与顺序未核实」，整句仍 ≤60 字（状态栏截断）。
位置 `core/fidelity.py:225`。回归：`test_multi_frame_normal_state_mentions_state_mapping`
增加 `assertIn("用途与顺序未核实")` 与 `assertNotIn("悬停")`。

### 1.9 新族被同目录旧族盖住却没提示（#21，Major，属实）

`dir_base.plan` 的优先级固定：按钮横片 → 九片 → 横三片 → 竖三片 → 序号帧 →
单图。目录里已有 `0l/0c/0r`（h_state）时，再导入 `0/1/2.png`（frames）：

- `_existing_pieces` 只按**同名**子图判冲突，`0.png` 与 `0l.png` 不同名 →
  不警告；
- 保存后 `plan` 仍先命中 h_state，新写的三张永远不被画布/游戏使用。

改法：`FamilyImportDialog._shadowing_plan()` 把「这次要写的路径」并进存在性
判断，模拟保存后的 `plan`；若命中的不是这一族，红字说明并禁用 OK，同时
显示「换个新目录」。`accept()` 也再查一次，防止回车绕过。新族优先级更高
（会顶掉旧族）时不拦，但提示「原有的【单图】保存后不会再被用到」。
位置 `ui/image_picker.py:460`。回归：`test_family_dialog_blocks_a_shadowed_family`、
`test_family_dialog_notes_old_family_is_replaced`。

### 1.10 写包取消会删掉用户选来覆盖的旧文件（#22，Major，属实）

`patch_pack_copy` 只在 `os.replace(tmp, out)` **之前**轮询取消；取消时它删
自己的临时文件，目标路径上原来的包根本没动过。旧取消处理却无条件
`Path(path).unlink(missing_ok=True)`——用户选了一个旧 `_patched.fls` 覆盖、
中途取消，旧文件就没了。

改法：取消处理不再删 `path`，状态改成「没有写出新包，原包与目标文件都没动」。
位置 `ui/save_workflows.py:261`。回归：
`test_pack_dialog_cancel_keeps_an_existing_target`（预置 `older pack, keep me`，
取消后字节不变）。

### 1.11 写包事实挂在 `self` 上（#24，nitpick，属实）

旧注释说 `pending_import`/`encoding`「在界面线程先抓好」，实际是在
`_write_pack_copy_file` 里读 `self.doc` 并写 `self._writing_*`——而这个函数
正是交给 `run_busy` 在后台线程跑的。后果：注释与事实不符、单独调用
`_write_pack_file` 会 `AttributeError`、两次写包会互相覆盖。

改法：两个值在 `save_to_pack_dialog` 的界面线程先取好，作为显式参数传给
`_write_pack_copy_file` / `_write_pack_file`；删掉 `_writing_*` 属性。
`_write_pack_copy_file` 不传时按当前文档取一次，保持测试/脚本入口可用。
位置 `ui/save_workflows.py:136`。

## 2. 文档/证据问题（5 处）

### 2.1 测试分类合计对不上（#3、#6、#13、#17）

凡是写「N 项无失败（含 1 跳过）、2 项基线」而总数是 `N + 3` 的，N 其实是
**通过数**，再加跳过就重复了。逐条改为「N 通过、1 跳过、2 项基线」：

- 0.13.7：708 项 = 705 通过 + 1 跳过 + 2 基线；
- 0.13.6 记录：698 = 695 + 1 + 2；
- 0.13.5：690 = 687 + 1 + 2；
- 0.13.4：688 = 685 + 1 + 2；
- 0.13.3：686 = 683 + 1 + 2；
- `docs/STATUS.md` §1/§2 总表与 `ui_editor/README.md` 的对应段落同步。

`N 项无失败（含 1 跳过）` 在 `N + 2 = 总数` 的旧条目里是另一种口径
（N = 通过 + 跳过），本轮不动那些条目，避免把历史数字改错。

### 2.2 目录探测范围写得比实现大（#4）

README 原句「工具认不出的命名也会列出来」不成立：`probe_pieces` 只查
`_PROBE_STEMS` 里的候选名，`weird.png` 不会出现（`test_probe_lists_every_known_spelling`
明确排除）。改为「候选名能探到、拼不成整族也会列；候选名以外的文件不会列」。

### 2.3 族类型优先级前后矛盾（#5）

0.13.3 段旧文说「控件只在认不出来时兜底」，0.13.4 段又说「位置词由控件
决定」「多数派兜底」。实际是**三段**：结构（`0/1/2`、`0l/0c/0r`、`top/left`）
> 位置词按控件（`left/middle/right`）> 名字认不出时按 `WIDGET_DEFAULT_KINDS`
多数派。已按这个口径重写，删除「没有逐控件类型证据」的过期说法。

### 2.4 引用计数 736 vs 9,310（#11、#12）

证据 JSON 的 `method` 写「736 处引用」，同一文件的 `totals.dir_base_refs`
和 `kinds_by_refs` 合计都是 **9,310**；`EXTERNAL_CORPUS.md` 也跟着写 736。
2026-10-22 用同一份真包重算（2,708 篇布局全解）：

```
dir-base refs: 9,310
unique bases:  729
refs by key:   sFileName 9,133 + sBgFileName 105 + sBarFileName 72
```

9,310 才是「处引用」，736 是过期数字。证据 JSON 的 `method` 改为 9,310，
新增 `totals.dir_base_refs_by_key` 记录分项，`EXTERNAL_CORPUS.md` 同步。

### 2.5 截断的 SHA-256（#16）

`fidelity_autosize_20261022.json` 的 `pack.sha256` 写成
`3fb516a9...1fb124`。已补全为
`3fb516a961bfb32556af7a7d2761c703b70d194a16956535b18e7ab1571fb124`
（`sha256sum /tmp/iface/interface.fls` 实测一致，614,482,967 B）。

## 3. 已修、不改的条目

| 评论 | 为什么不改 |
|---|---|
| gitar 4344440189 | `aaf976d` 已把 `family_plan`/`family_pieces` 按路径缓存；实测首次整理后连续 4 次 `_refilter`（含搜索）触发 `resource_exists` **0 次**（构造时已由 `media_candidates` 填好缓存） |
| coderabbit 4344719964 | `1e607d0` 已把 README 的 685/1/2 分类改对；当前文本已是「685 通过、1 跳过、2 项错误」 |

## 4. 验证

- 新增 10 项回归（见各节）；全套 **708 项**：**705 通过、1 跳过、2 项
  `QMenu already deleted` 基线**（改动前同样失败）。
- `ruff check ui_editor/src ui_editor/tests`：0。
- `check_windows_compat.py ui_editor/src ui_editor/tests`：0/0/0。
- 真包复核：9,310 处引用 / 729 个唯一值；完整 SHA-256 见上；选图窗缓存
  0 次重复查询。
- 版本：`ui_editor/__init__.py`、`pyproject.toml` 升到 **0.13.7**。

## 5. 边界

- 真包只读，没有写回；写包取消的回归用合成包，未在真包上跑到中途取消。
- 「预览限宽」用纯 Qt 对象复现（1000×40 ×3），没有在用户机器上截图。
- Windows 实机、游戏内效果、像素级一致性仍未验。
- 评论里少数旧行号（如 `STATUS.md:68`）在当前文件已对不上，复核以**当前代码**
  为准；同类问题仍存在的按属实处理。
