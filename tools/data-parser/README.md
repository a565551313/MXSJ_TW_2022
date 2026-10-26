# 资源与 PE 专项工具：逐文件选择

状态：**研究专用和历史实现混合**。常规资源操作优先 [资源编辑器](../../resource_editor/README.md)，布局优先 [UI 编辑器](../../ui_editor/README.md)，脚本优先 [脚本编辑器](../../script_editor/README.md)。
这些替代入口不意味着全部专项能力等价，也不允许直接删本目录。见 [依赖清单](../DEPENDENCIES.md)。

| 文件 | 状态／适用输入 | 输出／风险及替代关系 |
|---|---|---|
| `universal_fls_tool.py` | 历史实现，仍是旧 batch 的 data 包解包子进程 | 解包文件／manifest 或重包；“ALL formats”不是当前全部变体验收，输出保护需独立审查 |
| `repack_fls.py` | 历史重包／补丁研究 | 生成 FLS／补丁；新开发优先编辑器，不借其 docstring 宣称绝不损坏 |
| `extract_game_data.py` | 历史启发式数据提取 | CSV／JSON／SQLite 输出；缺失或乱码不能补成真实规则，不直接发布到 game_data |
| `extract_dlg.py` | 研究专用；给定 0SLF 与布局路径 | 写解密布局；含头部／频率探测，读取兼容不等于正确的原生写入策略 |
| `mx_path_hash.py` | 研究参考；原生路径哈希 | 哈希分析；编辑器共享实现真源现为 `mx_common/`，extract_dlg 仍直接 import 本文件 |
| `i0_sprite.py` | 研究专用；对应 I0 等样本 | 信息、帧图／条带导出；日常预览用资源编辑器，格式对照仍有价值 |
| `I0_SPRITE_FORMAT.md` | 格式研究参考 | 不是所有精灵类型的最终兼容声明 |
| `pe_resource_dump.py` | 研究专用；PE 的 `.rsrc` | 导出资源及报告；不是 FLS 资源编辑器的等价功能 |
| `skin_label_patch.py` | 研究专用；皮肤 PNG＋标签矩形／字体 | 写改字 PNG，可填充到指定长度；不是任意 UI 控件的原生替代方案 |
| `skin_labels.launcher.json` | 固定启动器皮肤标签配置 | 不能跨任意皮肤尺寸／版本直接套用 |
| `pe_resource_patch.py` | 研究专用；指定 PE 资源及替换负载 | 写 PE 和报告；原位是资源布局概念，不代表允许覆盖原始输入，先核查源／目标和备份 |
| `test_pe_resource_dump.py`、`test_skin_and_resource_patch.py` | 专项回归 | 测试范围不能外推 EXE 启动、签名／保护系统或 Windows 验收 |
| `mxmain_rtti.py` | 研究专用；`mxmain.dll` 的明文 MSVC RTTI | 输出类名／基类链／虚表／虚析构／写 vfptr 位置的 JSON 与 Markdown；只读、不反编译、不执行镜像，见 [类图清单](../../notes/mxmain_rtti_class_map.md) |
| `test_mxmain_rtti.py` | 专项回归（自建 PE + 真档断言） | 钉住 TD/COL 定位、BCD 28 位元组步长、槽尾字串假阳性；不代表 Windows 运行期一致 |

## 写入规则

工具有无源路径／别名保护应逐函数审查，不因为输出参数叫“新文件”就认为安全。
所有分析产物放仓库外新目录，原包／PE 输入只读，不自动部署；文本编码、资源长度及未知数据保持真实。
本轮只补文档，没有执行解包、改图、重包或 PE 写入，也没有为旧工具补安全校验。
