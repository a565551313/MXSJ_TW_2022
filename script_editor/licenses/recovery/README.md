# 独立恢复工具与许可

主编辑器通过标准pyc文件/JSON结果调用独立命令行程序，不在GUI进程中导入恢复引擎。
`src/script_editor/data/recovery_worker.py`是独立GPL-3.0-or-later程序；可单独运行：

```
python recovery_worker.py --input standard.pyc --vm py25 --output result.json
```

不执行输入模块。工作进程依赖：
- uncompyle6 3.9.3：GPL-3.0-or-later，https://github.com/rocky/python-uncompyle6
- xdis 6.1.8：GPL-2.0-or-later，可按GPL3使用，https://github.com/rocky/python-xdis
- spark-parser 1.9.0：MIT，https://github.com/rocky/python-spark
- six 1.17.0：MIT，https://github.com/benjaminp/six
- click 8.5.0：BSD-3-Clause，https://github.com/pallets/click

完整许可证随本目录提供。现有主编辑器代码的权利声明不因此改变；本目录不宣称拥有游戏源码。
源码模式使用当前Python3环境的这些依赖（bootstrap安装固定版本）。Windows构建时用独立spec
生成`recovery-worker/MXSJRecoveryWorker.exe`，不把GPL引擎混入主GUI EXE；同时保存独立工具
源码、许可和所用上游完整源码归档。若再分发这个独立程序，须履行其GPL等许可义务，
不能只提供二进制或仅提供不可控的下载链接。
