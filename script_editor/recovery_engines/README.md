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
0.6.0.dev3完整源码交付ZIP附真实交叉构建的Windows x86 pycdc.exe（不进Git），
仅依赖Windows 10/11系统UCRT/kernel32；未在Windows执行，不代表EXE构建或游戏验收。
维护者也可用固定Zig0.13.0从Linux重建（普通用户不需要Zig）：

```sh
python -m pip install ziglang==0.13.0
python build_windows_recovery_engine.py --work NEW_WORK --output NEW_OUTPUT
```

BUILD-NOTICES.txt包含Zig/MinGW/libc++/libc++abi/libunwind许可证与完整构建配方；
其SHA进入manifest，加载及EXE暂存均校验并保留，不能只拷贝二进制丢掉运行时声明。
Windows编译出现13条Zig libunwind别名属性警告，构建退出0；没有以此冒充零警告运行验收。
Git纯克隆仍不含二进制，不能等同于完整源码交付ZIP。
