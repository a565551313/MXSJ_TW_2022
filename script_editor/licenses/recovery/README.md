# 独立恢复工具与许可

主编辑器通过标准pyc文件/JSON结果调用独立命令行程序，不在GUI进程中导入恢复引擎。
`src/script_editor/data/recovery_worker.py`是独立GPL-3.0-or-later程序；可单独运行：

```
python recovery_worker.py --input standard.pyc --vm py25 --output result.json
```

不执行输入模块。工作进程依赖：
- uncompyle6 3.9.4.dev0（固定上游提交91298ba80e322cfb8736ab8a697509527297a7a9）：GPL-3.0-or-later，https://github.com/rocky/python-uncompyle6
- xdis 6.3.0：GPL-2.0-or-later，可按GPL3使用，https://github.com/rocky/python-xdis
- spark-parser 1.9.0：MIT，https://github.com/rocky/python-spark
- six 1.17.0：MIT，https://github.com/benjaminp/six
- click 8.5.0：BSD-3-Clause，https://github.com/pallets/click

完整许可证随本目录提供。现有主编辑器代码的权利声明不因此改变；本目录不宣称拥有游戏源码。
源码模式使用当前Python3环境的这些依赖（bootstrap安装固定版本）。Windows构建时用独立spec
生成`recovery-worker/MXSJRecoveryWorker.exe`，不把GPL引擎混入主GUI EXE；同时保存独立工具
源码、许可和所用上游完整源码归档。若再分发这个独立程序，须履行其GPL等许可义务，
不能只提供二进制或仅提供不可控的下载链接。

上游完整固定源码、SHA及Python3.14兼容修复范围见../../third_party/README.md；不从PyPI安装失配的3.9.3。

## 0.6 开发分支新增的第二独立程序 pycdc

经固定上游归档 LICENSE / README 核实，pycdc 为 **GNU GPL version 3**，不是 MIT。
源提交 `b4289760970dbc399684f1e155ec6d1ea1cc787e`，完整源码随工具保存在
`third_party/pycdc-*.tar.gz`。本工具不导入/链接 pycdc，通过新进程与标准 pyc 数据交互，
不执行反编译目标。构建产物、上游 GPL 许可证及完整对应源码一起进入独立
`recovery_engines/pycdc/`；加载时核对源码归档、许可证及二进制摘要。
若分发第二程序必须保留这些文件及 GPL 权利；完整归档已含上游构建脚本和作者声明。
这一分离方式不是法律审核意见，不改变编辑器其它部分的许可声明。
