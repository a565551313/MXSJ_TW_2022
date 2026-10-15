# 固定上游恢复引擎源码（不是动态跟随master）

0.5.0错误地将仅允许Python<3.13的xdis6.1.8用于声明支持Python3.14的启动器；
且uncompyle6 3.9.3依赖xdis<6.2，所以不能只升级xdis或忽略Requires-Python强装。

0.5.1使用上游自身已适配xdis>=6.3、列出Python3.14支持的固定提交：

- 项目：https://github.com/rocky/python-uncompyle6
- 提交：`91298ba80e322cfb8736ab8a697509527297a7a9`（2026-10-05）
- 版本元数据：`3.9.4.dev0`。这是固定上游开发快照，不冒称已发布的PyPI正式版。
- 下载：https://codeload.github.com/rocky/python-uncompyle6/tar.gz/91298ba80e322cfb8736ab8a697509527297a7a9
- 文件：`uncompyle6-91298ba80e322cfb8736ab8a697509527297a7a9.tar.gz`
- SHA256：`9e60958d4b0386e3976331ba6236ef2a1a986b2a162f3ddb9a8db424ae2e4d87`
- GPL-3.0-or-later；原样完整源码，包括原许可证与构建元数据，没有修改上游依赖声明。

源码启动从此本地归档安装，不要求联网GitHub下载新提交；安装前核对SHA，安装后检查
PEP610来源摘要及版本，不能把相同dev版本的其他提交误当已测版本。
其余依赖固定xdis6.3.0/spark-parser1.9.0/six1.17.0/click8.5.0，由pip正常解析，不使用
--ignore-requires-python或--no-deps绕过兼容声明。pip/Qt等依赖首次安装仍需要联网。

GUI进程不导入GPL引擎；独立worker进程中适配xdis6.3的implementation枚举接口，并保留
非UTF8字节常量（不使用其errors=ignore丢字节）；旧Unicode显示适配仍在。没有修改已安装上游文件、
目标常量值或VM/opcode/加密边界。Windows独立EXE构建的对应源码归档也使用本文件，非失配的PyPI3.9.3。

## 第二引擎 pycdc（独立 GPL-3.0 可执行程序）

官方仓库 https://github.com/zrax/pycdc ，固定提交
`b4289760970dbc399684f1e155ec6d1ea1cc787e`。
完整源码归档 `pycdc-b4289760970dbc399684f1e155ec6d1ea1cc787e.tar.gz`，373,111 B，
SHA256 `d7d8c53d37a1a586097145b532fca02535db2f2f0999b3b1e910133c9941bf31`。
归档包含上游 GPL-3.0 许可证；由 `build_recovery_engine.py` 校验后独立构建、复制许可证和生成二进制清单。
此引擎不替换 uncompyle6/xdis 固定依赖，不导入主 GUI，不执行目标模块。
