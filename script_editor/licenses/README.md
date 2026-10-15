# 来源与后续许可证清单

容器模块`core/archives/{fls0slf,flsdata,readers}.py`及`core/errors.py`
整理自本仓库`resource_editor/src/resource_editor/core`（设计检查点2f5f7e4时版本）。
这些文件随独立工具一同保存，不在运行时导入兄弟目录；保留原格式注释。
仓库未提供总LICENSE；工具沿用既有编辑器Proprietary标识，不假定拥有游戏资源再分发权。

二进制不入Git；0.6.0.dev3独立源码ZIP附双Windows标准CPython编译器，
runtimes/manifest.json记录版本/来源/逐文件SHA与许可证；交付还附官方对应源码归档。
第二引擎pycdc附GPL完整源码与BUILD-NOTICES.txt（静态运行时许可、完整构建配方）。
主引擎固定源码及四项Python依赖源码也随包；这些不是GUI的Proprietary许可。
Qt/PyInstaller等首次联网安装，不是本源码ZIP中预构建的编辑器EXE；
用户构建EXE时仍须保留实际依赖的许可/对应源码。本包不含游戏二进制。

M2 opcode数值表从同仓库`tools/decompiler/batch_decompile.py`抽取，来源SHA见
`core/vm/tables.py`；不导入旧修复器/打包器。VM2.7实际DLL分发表另作只读小样证据，
历史注释误标的操作名和未知opcode66不直接沿用；未新增游戏DLL或其他二进制。
