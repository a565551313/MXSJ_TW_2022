# PR #68 AI 审查复核

- 复核日期：**2026-10-22**（Asia/Shanghai）；被复核的评论提交于 2026-10-21 23:43–23:54 CST
- 复核对象：PR #68（`arena/7d7d4382-mxsj-tw-2022` → `master`，head `b3fdf74`，ui_editor 0.12.7）
- 审查来源：`gitar-bot[bot]`（1 条行内 + 1 条总结，状态 Changes requested）、
  `coderabbitai[bot]`（6 条行内 + 1 条总结）
- 行内评论共 **7 条**，去重后 **6 个问题**（缓存键一条被两个机器人各报一次）
- 复核方法：读当前代码 + **动态复现**。沙箱已重建 PySide6 6.7.0 + 手写
  `libGL/libEGL/libxkbcommon/libdbus` 桩库、`QT_QPA_PLATFORM=offscreen`；
  纯逻辑（`pack_build`、`diagnostics`）直接跑真函数，绘制路径跑真 `QPainter` 与真
  `MainWindow` 场景

## 0. 结论

| # | 意见摘要 | 判定 | 严重度 |
|---|---|---|---|
| 68-1 | 切片 QPixmap 缓存键漏按钮态，常态/按下共用同一批图 | **属实**（两个机器人重复报告） | **高：新功能在真实界面里失效** |
| 68-2 | `docs/STATUS.md` §2 组件行仍写「本轮」，与本轮只重跑 ui_editor 的说明矛盾 | **属实** | 低（文档） |
| 68-3 | 诊断的代码皮肤判定用 `any(所有 refs)`，画布只用 `refs[0]` | **属实** | 低 |
| 68-4 | 诊断不考虑 `lNormalColor`，文案说「按 ui.lst 配色」，画布实际用 `.dlg` 颜色 | **属实** | 低 |
| 68-5 | `_looks_plain_text` 先于已知文件头解密，可能把密文当明文返回 | **属实（机制成立，现实语料未见影响）** | 低（防御性） |
| 68-6 | 未知尺寸父用兜底 80×24 当硬边界夹子控件 | **部分属实** | 低 |
| 68-7 | Docstring 覆盖率 47.71% < 80%（预合并检查告警） | **不属代码缺陷**（仓库无此门槛） | — |

**合并前必须修 68-1**：0.12.7 的主打功能「按钮态画真切片」在真实界面里不生效——
常态先画过一次后，切到按下/悬停仍显示常态图，但角标报 `state_slice_by_index`，
画出来的和标出来的不一致。其余 5 条建议同批修，成本都很低。

复核后已按用户授权**只修属实项**（2026-10-22）：68-1～68-5 与 68-2 全部落地，
68-7 不改；逐条结果与验证见 §9。

## 1. 68-1 切片缓存键漏按钮态（属实，严重）

- 评论：gitar `painters.py:69-76` + CodeRabbit `painters.py:76`（同一条，两个机器人）
- 代码：`PaintContext.slice_pixmap(name, index, image)` 的键是
  `(name + "#slice", index)`（`painters.py:69-76`）；`_draw_slice` 现在按
  `fetch_slice_state(name, state)` 取图，但调 `ctx.slice_pixmap(name, cell.index, image)`
  时**没把 state 传进去**（`painters.py:260`）。三态横片的 0/1/2 态 cell 下标都是
  0..2，于是共用同一批缓存。

复现（同一 `PaintContext`，先正常再按下）：

```
fresh ctx: normal  -> (35, 207, 255, 255)
fresh ctx: pressed -> (35, 207, 255, 255)   # 应为橙色态图
cache keys: ['…一级按钮\\#slice', '…一级按钮\\#slice', '…一级按钮\\#slice']
```

在**真实主窗口**里走 `set_button_state("pressed")` 也一样（场景截图采样同为
`(35,207,255)`），因为画布加载时先画的就是常态；`set_button_state` 只改
`ctx.button_state` 并 `refresh_all()`，不清 `_pixmaps`。反向同样成立（先画过按下，
再切回常态仍是按下图）。评论里「角标报 `state_slice_by_index` 与画面不一致」也属实。

测试缺口属实：`test_text_button_draws_real_state_slices` 用**新 context** 只渲染
按下态，缓存是冷的，因此通过。修复前全套 615 项在带这个 bug 的情况下仍全绿（只有 2 项
与本事无关的 `QMenu already deleted` 既有错误），证明现有用例抓不到。

**建议修复成立**：把 state 放进键。原型验证后同一 context 连续渲染：

```
normal (35, 207, 255, 255) → pressed (254, 172, 36, 255) → normal (35, 207, 255, 255)
```

补一条「同 context 先常态后按下」的用例即可锁住；修完全套仍 615 项（2 项既有错误）。

## 2. 68-2 STATUS 组件行仍写「本轮」（属实，文档）

- 评论：CodeRabbit `docs/STATUS.md:40`
- 现状：§2 顶部说明写「本轮只重跑 **ui_editor** 全套……local_server 68 项、资源编辑器
  126 项等为历史结果」（第 40 行），但同一张表里：

| 行 | 现文 |
|---|---|
| 第 45 行 独立客户端 Web 服务 | 「**本轮** 60 项通过、3 项 GUI 跳过」 |
| 第 46 行 本地服诊断日志 | 「已包含在**本轮** 68 项回归中」 |

两处都不是本 PR 改的行，但本 PR 新增的说明使它们自相矛盾。属实（只改措辞：去掉
「本轮」或标注日期）。

## 3. 68-3 代码皮肤判定 any() 与画布不一致（属实，轻）

- 评论：CodeRabbit `diagnostics.py:110`
- 画布：`ScriptIndex.skin_bindings()` 只取 `refs[0]`，`_code_skin_pixmap` 用它取图；
  诊断的 `_code_skin_available` 却是 `any(resource_exists(ref.skin) for ref in refs)`。

复现：同一控件绑两条皮肤引用，`refs[0]="missing.png"`、`refs[1]="ok.png"`，
`resource_exists` 只认 `ok.png`：

```
现实现诊断：['STATIC_ONLY']            # RENDER_STYLE_SKIN 被 any() 误抑制
画布绑定：refs[0] = missing.png        # 画布不会走代码皮肤
改成 refs[0]-only：['RENDER_STYLE_SKIN']  # 与画布一致
```

同一场景改成只认 `refs[0]` 后诊断恢复报出，单引用缺图场景不受影响。属实。

## 4. 68-4 诊断漏 `lNormalColor`（属实，轻）

- 评论：CodeRabbit `diagnostics.py:328`
- 画布：`_paint_text_button` 先取 `lNormalColor`，`resolve_source` 也先判它。

复现：`CTextButton`、无图、`iStyle=0` 有效色、`lNormalColor=[10,120,200]`：

```
画布 resolve_source = dlg_color
诊断 = [('RENDER_STYLE_SKIN', '图片不可用，画布按 ui.lst 的 iStyle=0 样式表配色绘…')]
```

文案与画布实际用色不符，属实。修复时注意：`painters._color_from_value` 支持
「单个打包整数 / `[r,g,b]` / `[打包整数]`」，诊断里要写一个**无 Qt 的等价判定**
（真包与 fixtures 里 `lNormalColor` 都是 `[r,g,b,a]` 列表），否则打包整数会被漏掉。
建议顺带把文案改成「按 .dlg 的 lNormalColor 画底色」，而不是简单不报。

## 5. 68-5 `unpack_packed_text` 判定顺序（属实但现实语料未见影响）

- 评论：CodeRabbit `pack_build.py:213`
- 现状：`if data.startswith(_KNOWN_HEADER[:5]) or _looks_plain_text(data): return data`
  ——**先**认 INI 明文、**后**按已知文件头解密（`pack_build.py:183`）。
- 机制：加密 `.dlg` 的密文首字节必然是 `[`（密钥首字节恒为 `0x78`），所以每篇密文
  都会进 `_looks_plain_text`；新口径（控制字节 ≤2%）在内容 GBK 占比高、对齐刚好时
  会放行密文，随后被当明文返回。

复现 CodeRabbit 的合成载荷（`UI_INFO = [{"X": "測×180"}]`）：

| 密钥 | 前 256B 控制字节 | 现实现 | 改序后 |
|---|---|---|---|
| `78 00 00 00` | 2（0.8%） | 返回密文（还原失败） | 正确还原 |
| `78 ff ff ff` | 2（0.8%） | 返回密文 | 正确还原 |
| `78 c7 ae 39` | 7（2.7%） | 正确还原 | 正确还原 |

**但真实语料没受影响**：仓库 8 篇真实 `.dlg` 在 3 种密钥下控制字节都是 17–46/256
（6.6%–18%），全部被正确拒绝；用 `dlg_codec.dump_bytes` 生成 1–199 个汉字标题 ×
3 种密钥共 597 组，**0 例误判**。原因是本仓库 dump 出来的头是
`# -*- coding: gbk -*-\n# MD5: <32 hex>\n\nUI_INFO = …`，前 256 字节以 ASCII 为主。

判定：机制属实，属**防御性**问题；评论说「会弄乱真包」目前没有证据。建议采纳其改法
（先解已知文件头，解不开再认 INI 明文），实测：ui.lst 明文、8 篇明文、3 种密钥密文、
上述合成载荷全部正确；修复前后全套测试均为「2 项既有 `QMenu already deleted` 错误」，
没有新增失败。

## 6. 68-6 未知尺寸父用兜底尺寸硬夹（部分属实）

- 评论：CodeRabbit `main_window.py:491`
- 现象：`_clamp_in_parent` 用 `effective_size(parent)`，而 `effective_size` 在
  「无显式尺寸 + 取不到图」时会兜底 `80×24`（`CMainFrame` 为 `120×90`）。

复现：父 `CFrame` 无图、`iWidth/iHeight=0`，子 50×20 拖到 (999,999)：

```
现实现：(30, 4, True)      # 被夹进 80×24 兜底框
基线（原始宽高 0,0）：(999, 999, False)
父有真实图片 200×100：(150, 80, True)   # 这条是 61-1 要修的场景，保持不变
```

`snap.clamp_in_parent` 的文档明确写「父某一维 <=0 表示尺寸未知，该维只保证非负」，
所以在「未知」情况下把兜底尺寸当硬边界确实偏离契约，会**静默搬动**控件——这部分属实。

但它不像评论说得那么「假」：画布本身也用同一套 `effective_size` 把父画成 80×24，
夹进这个框与画面一致；问题在于兜底值是编辑器占位、不应作为几何约束。判**部分属实**。
建议的 `effective_size(..., fallback=False)` 原型验证可行：未知父 → `(999,999,False)`，
图片父 → `(150,80,True)`，现有两条夹父用例仍成立。

## 7. 68-7 Docstring 覆盖率（不是代码缺陷）

CodeRabbit 的预合并检查报「Docstring coverage 47.71% < 80%」，这是它的通用策略阈值；
仓库 `AGENTS.md`、`docs/PYTHON_TOOL_CONVENTIONS.md` 没有这条门槛（检索无结果）。不必按它
补全量 docstring；本轮新增函数均已带说明。

## 8. 建议处理顺序

| 顺序 | 条目 | 动作 |
|---|---|---|
| P0 | 68-1 | 缓存键加 `state`；补「同一 context 先常态再按下、再切回常态」像素用例 |
| P1 | 68-3 / 68-4 | 诊断改成与画布同源判定（`refs[0]`；`lNormalColor` 可用时改口径/不报） |
| P2 | 68-5 | 调换判定顺序（先解已知文件头，再认 INI 明文），补合成用例 |
| P2 | 68-6 | `effective_size` 加 `fallback` 开关，只在子控件用兜底 |
| P3 | 68-2 | STATUS 两行去掉「本轮」，标为历史 |

边界：以上结论来自沙箱 offscreen 与合成夹具，**不等于**与真实客户端像素级一致；
68-5 的「真包是否会出现 GBK 占比高的头部」没有语料可证，只能按防御处理。

## 9. 修复结果（2026-10-22，ui_editor 0.12.7 同版补修）

| # | 判定 | 修复动作 | 用例 |
|---|---|---|---|
| 68-1 | 属实（严重） | `slice_pixmap(..., state=0)` 把态号并入缓存键；`_draw_slice` 传 `state`。注释写明为什么必须带 | `test_state_switch_on_warm_cache_shows_each_state`（同一 context 常态→按下→常态；旧代码上失败） |
| 68-2 | 属实 | STATUS §2：Web 服务 60 项标「历史结果（2026-10-19）」、本地服诊断日志 68 项标 2026-10-19 | 文档 |
| 68-3 | 属实 | `_code_skin_available` 只看 `refs[0]`，与画布 `skin_bindings` 一致 | `test_code_skin_uses_first_reference_like_the_canvas` |
| 68-4 | 属实 | 新增无 Qt 的 `_usable_color`（列表/打包整数，同 `_color_from_value` 口径）；`CTextButton` 有可用 `lNormalColor` 时跳过 `RENDER_STYLE_SKIN` | `test_dlg_color_is_not_reported_as_style_skin`（两种写法） |
| 68-5 | 属实（防御性） | `unpack_packed_text`：明文直返 → 已知头试解 → `_looks_plain_text` → 频率还原 | `test_gbk_heavy_ciphertext_is_decoded_not_kept_as_text` |
| 68-6 | 部分属实 | `effective_size(..., fallback=False)`；`_clamp_in_parent` 只对父关兜底，子仍用兜底 | `test_unknown_parent_size_does_not_clamp`（含负坐标抬回 0） |
| 68-7 | 不属缺陷 | 不改 | — |

**验证**：`ui_editor` 全套 **620 项**（新增 5 项）：618 无失败（含 1 跳过）、2 项
`QMenu already deleted` 为基线既有；`ruff check src tools tests` 0；
`check_windows_compat` 0/0/0。新增用例逐条在**未修**代码上验证过会失败（缓存键、
诊断两例、未知父夹取、密文顺序），避免“写了但抓不到”的假测试。
`main_window.py` 仍守住 600 行上限（结构测试通过）。

**边界**：仍是沙箱 offscreen 与合成夹具；`main_window._clamp_in_parent` 的改动只影响
「父无显式尺寸且取不到图」的未知维度，图片尺寸父（61-1 的场景）行为不变。
