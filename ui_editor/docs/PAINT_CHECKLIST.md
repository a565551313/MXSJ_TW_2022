# 控件绘制对照清单（编辑器 vs 真机）

> 由 `ui_editor/src/ui_editor/ui/paint_samples.py` 生成（`python3 ui_editor/tools/render_paint_samples.py --checklist-md ui_editor/docs/PAINT_CHECKLIST.md`）。
> 类型集合与 `defaults_data.DEFAULT_PROPS` 一致，由 `ui_editor/tests/test_paint_samples.py` 机检。

## 这份清单解决什么问题

`painters.py` 是全项目最像游戏、却验证最少的一层：它只能近似，而「编辑器里好看 ≠ 游戏里一样」。单测能证明「不崩、尺寸对」，**证明不了外观一致**——所以这里把判断交给人，但把材料准备好：

1. 生成样例：`python3 ui_editor/tools/render_paint_samples.py --out <仓库外目录>`（可加 `--pack data/xxx.fls` 用真实资源再渲一套）；
2. 在 Windows 真机上打开对应界面截图（同尺寸裁剪，别缩放）；
3. 用 `python3 ui_editor/tools/paint_compare.py --editor <样例.png> --game <真机截图.png> --out <目录>` 得到并排图与像素差异统计；
4. 把结论填回本表：**没做过真机核对的格子必须留空**，不要预填「一致」；发现差异先记录，再决定改绘制还是改用法。

## 规矩

* 只对「看得出差异会误导用户」的项目较真；纯抗锯齿/字体渲染差异（系统字体不同）可以记「环境差异」而不改代码。
* 结论一旦从「有差异」变成「已修」，要在`docs/STATUS.md` 写明版本与证据（截图路径）。
* 本表不替代进游戏验收：`AGENTS.md` §0「能运行 ≠ 正确」同样适用。

| # | 类型 | 绘制函数 | 编辑器画什么 | 依赖 | 游戏侧期望外观 | 真机截图 | 差异 | 结论 |
|---|---|---|---|---|---|---|---|---|
| 1 | `CAutoDlgBase` | `_paint_main_frame` | 整窗底板：底图/边框 + 子控件由场景分别绘制 | 无（纯几何） |  |  |  |  |
| 2 | `CBitmapFrame` | `_paint_image` | 图片控件：画首帧，按 iWidth/iHeight 拉伸；位图控件：拉伸整图（与九宫格不同） | 图片资源 |  |  |  |  |
| 3 | `CBitmapHFrame` | `_paint_image` | 图片控件：画首帧，按 iWidth/iHeight 拉伸 | 图片资源 |  |  |  |  |
| 4 | `CBitmapVFrame` | `_paint_image` | 图片控件：画首帧，按 iWidth/iHeight 拉伸 | 图片资源 |  |  |  |  |
| 5 | `CBorder` | `_paint_frame` | 矩形底板（有图用图，缺图按占位框 + 文件名标注） | 图片资源 |  |  |  |  |
| 6 | `CBox` | `_paint_frame` | 矩形底板（有图用图，缺图按占位框 + 文件名标注）；容器：画边框与栅格间距，不画子控件本身 | 行列参数 |  |  |  |  |
| 7 | `CBoxWithTips` | `_paint_text` | 文字：按 iFont 取字体表字号/字色，居中或多行 | 无（纯几何） |  |  |  |  |
| 8 | `CButton` | `_paint_button` | 按钮：底图/样式底色 + 居中 sText；多状态按预览开关近似 | 图片资源 |  |  |  |  |
| 9 | `CCombCheckButton` | `_paint_grid` | 网格类：表头/行列线与单元格文字（按行列推算尺寸）；组合勾选按钮：按栅格近似，勾选态未比对 | 图片资源、行列参数 |  |  |  |  |
| 10 | `CDataWidget` | `_paint_fallback` | 未登记的控件类型：画占位框 + 类型名（说明该类型没有专用绘制） | 无（纯几何） |  |  |  |  |
| 11 | `CEdit` | `_paint_edit` | 输入框：边框 + sText 或提示字；输入框：编辑态外观，游戏焦点态未比对 | 字体表 iFont |  |  |  |  |
| 12 | `CFrame` | `_paint_frame` | 矩形底板（有图用图，缺图按占位框 + 文件名标注） | 图片资源 |  |  |  |  |
| 13 | `CHFrame` | `_paint_frame` | 矩形底板（有图用图，缺图按占位框 + 文件名标注） | 图片资源 |  |  |  |  |
| 14 | `CHPageButton` | `_paint_button` | 按钮：底图/样式底色 + 居中 sText；多状态按预览开关近似；翻页按钮：按样式底色 + 文字近似 | 图片资源、ui.lst 样式 |  |  |  |  |
| 15 | `CHPagePngButton` | `_paint_button` | 按钮：底图/样式底色 + 居中 sText；多状态按预览开关近似；翻页按钮（图片皮肤）：与九宫格切法相关，未比对 | 图片资源、ui.lst 样式 |  |  |  |  |
| 16 | `CHPngFrame` | `_paint_image` | 图片控件：画首帧，按 iWidth/iHeight 拉伸 | 图片资源 |  |  |  |  |
| 17 | `CHotBox` | `_paint_hotbox` | 热区：半透明提示框（编辑用，游戏里不可见）；热区在游戏里不可见；这里画半透明框仅为编辑 | 无（纯几何） |  |  |  |  |
| 18 | `CImagesFrame` | `_paint_grid` | 网格类：表头/行列线与单元格文字（按行列推算尺寸）；按 iRow/iCol 平铺首帧，间距 iHSpace/iVSpace | 图片资源、行列参数 |  |  |  |  |
| 19 | `CList` | `_paint_list` | 列表：行分隔线 + 行文字 | 行列参数 |  |  |  |  |
| 20 | `CMainFrame` | `_paint_main_frame` | 整窗底板：底图/边框 + 子控件由场景分别绘制 | 无（纯几何） |  |  |  |  |
| 21 | `CPngList` | `_paint_grid` | 网格类：表头/行列线与单元格文字（按行列推算尺寸）；按行网格近似；游戏列表项样式未比对 | 行列参数 |  |  |  |  |
| 22 | `CPngNineFrame` | `_paint_nine` | 九宫格：源图**固定三分**近似（边角不拉伸，切割线不可配）；固定三分近似；游戏切法未比对 | 图片资源 |  |  |  |  |
| 23 | `CPngTable` | `_paint_table` | 表格：表头 + 网格 + 单元格文字；表格近似；真机列宽/表头样式未比对 | 行列参数 |  |  |  |  |
| 24 | `CProgress` | `_paint_progress` | 进度条：轨道 + 按 iValue 比例填充；轨道用图或底色，填充比例按 iValue（0–100 假设） | 图片资源 |  |  |  |  |
| 25 | `CRichTextFrame` | `_paint_text` | 文字：按 iFont 取字体表字号/字色，居中或多行；富文本按纯文本近似（不解析标签） | 字体表 iFont |  |  |  |  |
| 26 | `CSpriteFrame` | `_paint_image` | 图片控件：画首帧，按 iWidth/iHeight 拉伸；精灵首帧（多帧动画只画第 0 帧） | 图片资源 |  |  |  |  |
| 27 | `CTable` | `_paint_table` | 表格：表头 + 网格 + 单元格文字 | 行列参数 |  |  |  |  |
| 28 | `CTableView` | `_paint_table` | 表格：表头 + 网格 + 单元格文字；可滚动表格的近似；滚动与裁剪未比对 | ui.lst 样式、行列参数 |  |  |  |  |
| 29 | `CTextButton` | `_paint_text_button` | 文字按钮：按 ui.lst TBStyle 着色 + sText | 图片资源、ui.lst 样式、字体表 iFont |  |  |  |  |
| 30 | `CTextFrame` | `_paint_text` | 文字：按 iFont 取字体表字号/字色，居中或多行 | 字体表 iFont |  |  |  |  |
| 31 | `CTextFrameEx` | `_paint_text` | 文字：按 iFont 取字体表字号/字色，居中或多行；扩展文本：多行与对齐按纯文本近似 | 字体表 iFont |  |  |  |  |
| 32 | `CTitleTableView` | `_paint_table` | 表格：表头 + 网格 + 单元格文字；带标题栏表格的近似 | 行列参数 |  |  |  |  |
| 33 | `CVFrame` | `_paint_frame` | 矩形底板（有图用图，缺图按占位框 + 文件名标注） | 图片资源 |  |  |  |  |
| 34 | `CVPageButton` | `_paint_button` | 按钮：底图/样式底色 + 居中 sText；多状态按预览开关近似；翻页按钮：按样式底色 + 文字近似 | 图片资源、ui.lst 样式 |  |  |  |  |
| 35 | `CVPagePngButton` | `_paint_button` | 按钮：底图/样式底色 + 居中 sText；多状态按预览开关近似；翻页按钮（图片皮肤）：与九宫格切法相关，未比对 | 图片资源、ui.lst 样式 |  |  |  |  |
| 36 | `CVPngFrame` | `_paint_image` | 图片控件：画首帧，按 iWidth/iHeight 拉伸 | 图片资源 |  |  |  |  |
| 37 | `CVPngScrollBar` | `_paint_scrollbar` | 滚动条：轨道 + 滑块（按 iValue 位置）；图片皮肤滚动条：拉伸方式未比对 | 无（纯几何） |  |  |  |  |
| 38 | `CVScrollBar` | `_paint_scrollbar` | 滚动条：轨道 + 滑块（按 iValue 位置）；滑块位置按 iValue 线性映射，游戏手感未比对 | 无（纯几何） |  |  |  |  |

共 **38** 类控件；样例图与 SHA256 见渲染命令输出的 `manifest.json`。
