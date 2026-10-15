# Windows双运行时：尚未随包提供

`manifest.json`是schema2**空清单**，当前内置编译器不可用，发行构建会明确失败。
这不是已经交付的免安装Windows工具。不得拿游戏DLL、PATH的Python或Python3填充清单。
Linux开发仍可显式选择自己编译的标准2.5.6/2.7.13（不代表Windows运行时）。

M4准备代码现已校验**每个文件**，不再只查EXE：DLL、标准库ZIP、许可及所有其它运行时文件
均须SHA256匹配；拒绝漏件/额外文件、链接/重解析点、路径越界和大小写冲突；
检查PE32/x86和精确版本/魔数/32bit。注册后每次编译/审计重新检查，子进程后也检查。

预定布局（各VM的源码/许可来源独立记录）：

```text
runtimes/
  manifest.json
  py25/win-x86/python.exe + python25.dll + python25.zip + licenses + needed CRT
  py27/win-x86/python.exe + python27.dll + python27.zip + licenses + needed CRT
```

旧版Python可能在可写Lib目录生成.pyc，从而改变审计文件集合；使用标准库ZIP，
不在运行时生成/忽略未列入清单的缓存。所需CRT必须随包并依法携带许可，不能假设用户电脑装过。

`build_exe.bat`现在要求：两套完整运行时→Windows真实编译/marshal检查→严格测试（GUI与编译器
不可skip）→PyInstaller→精确复制到发行目录并复验；空清单不能再被复制成“完成”的发行版。
整套校验只提供本地文件一致性，不是数字签名、许可法律审核或可重现构建证明。

完整schema、命令、来源事实与Windows待办见[`../M4_RUNTIME_DISTRIBUTION.md`](../M4_RUNTIME_DISTRIBUTION.md)。
