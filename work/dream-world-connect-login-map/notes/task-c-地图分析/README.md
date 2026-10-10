# 任务 C 工作区

- `map-format-analysis.md`：证据、结构、阴性结果、重跑步骤和未解决事项。
- `artifacts/recon.py` + `recon.json`：离线侦察脚本及五个样本的哈希/文件头/压缩探测结果。
- `artifacts/analyze_records.py` + `2303-records-validation.json`：32 条矩形记录和 61 次分块引用的匹配验证。
- `artifacts/probe_image.py`：可复现 GEPJ→JPEG 的失败尝试，不保留伪图。
- `artifacts/native_gepj_trace.py` + `native-gepj-disasm.txt`：原生 GEPJ 分段表的只读静态证据。
- `artifacts/analyze_llec_pixels.py` + `llec-pixel-correlation.json`：五张底图与 LLEC 的逐值亮度相关性、值 2 的边界内坐标。
- `artifacts/native_walkable_trace.py` + `native-walkable-disasm.txt`：寻路接口与 LLEC 读取片段的只读静态证据；两者未建立直接映射。
- `artifacts/test_maps.py`：11 项测试（五份样本、GEPJ 分段/解码、网格相关性及损坏输入拒绝）。
- `artifacts/test_map_gui.py`：7 项 GUI 数据逻辑、外部目录和离线 HTML 生成的无头测试；有 Node 时检查内嵌 JavaScript 语法。
- `artifacts/*-llec*.svg`：**原始网格字节**视图；`2303-image-llec-records.svg` 在底图上叠加原始字节和未识别空间对象边框。
- 公共 `tools/gepj_decoder.py` + `tools/map-textures/*.png`：已恢复五张 2000×1500 场景底图。

共享交付物位于 `work/dream-world-connect-login-map/tools/`（`map_parser.py`、`map_viewer.py`、`map_gui.py`、`map_gui_html.py`、`map-viewer.html`、`MAP_GUI_README.md`、`map-data/`、`map-textures/`）及 `work/dream-world-connect-login-map/evidence/E-MAP-001.md`、`E-MAP-002.md`、`E-MAP-003.md`。GUI 的开发/测试步骤、未验证项和重做命令已补入 `map-format-analysis.md`。

所有脚本仅读取原始地图，输出在工作区或显式指定的工具输出目录；无网络请求。
