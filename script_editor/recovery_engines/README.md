# 可选的第二恢复引擎（开发接入阶段）

这里不是标准 Python 2 编译器目录；后者仍在 `runtimes/`。
pycdc 是独立 GPL-3.0 命令行解析器，不 import/执行目标模块，不由 GUI 链接。
引擎只从 `recovery_engines/pycdc/manifest.json` 及固定文件名加载；不用 PATH、
环境变量或游戏 DLL。缺失/校验失败保留主引擎能力并显示诊断，不伪称双引擎就绪。

固定源 commit `b4289760970dbc399684f1e155ec6d1ea1cc787e`，完整官方源码附在
`third_party/pycdc-*.tar.gz`，SHA256
`d7d8c53d37a1a586097145b532fca02535db2f2f0999b3b1e910133c9941bf31`。

维护者在目标平台准备 CMake 和本机 C++ 编译器后执行：

```sh
python build_recovery_engine.py --output recovery_engines/pycdc
```

输出新目录（拒绝覆盖），包含 pycdc[.exe]、GPL-3.0 许可证、完整对应源码归档及来源/二进制 SHA 清单。
生成的二进制不入 Git。清单提供交付完整性核对，不是数字签名/沙箱；不要加载来历不明的引擎。
当前尚未验证 Windows 构建、运行及 EXE 分发；不能把只含源码的 Git 克隆当成双引擎完整发行包。
