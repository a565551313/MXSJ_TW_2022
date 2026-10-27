# Windows x86双编译器（0.3.2.dev1源码交付ZIP内含）

`manifest.json`为schema2非空实测文件清单，分别固定标准CPython 2.5.6和2.7.13。
两套EXE/DLL/标准库**已入库**（用户2026-10-23决定，见`../../docs/archive/STATUS_HISTORY.md` §3.79）：
克隆或拉取即得到完整编译器，无需另装Python2，也无需解压交付ZIP。
重建（`../build_runtimes.py`）后必须把新二进制与`manifest.json`成对提交；Git历史会
永久保留每一份旧构建（每轮约6.7MB），没有理由时不要反复重建。
这些文件在仓库`.gitattributes`里声明为`-text`（binary）：Windows版Git的`core.autocrlf`
只改文本文件的换行，被改过的`BUILD.json`/许可会让自检报「runtime文件SHA256不匹配」。
真遇到了就双击`../修复编译器文件.bat`（等价于
`git -c core.autocrlf=false checkout -- script_editor/runtimes`），再跑一次自检。

```text
runtimes/
  manifest.json
  py25/win-x86/python.exe + python25.dll + python25.zip + BUILD.json + 5 licenses
  py27/win-x86/python.exe + python27.dll + python27.zip + BUILD.json + 5 licenses
```

每个root均为9个文件，全部实际SHA256列在manifest中。标准库ZIP使用ZIP_STORED，
不向Lib写.pyc、不依赖外部zlib扩展。只含纯Python标准库及编译所需内置模块，非通用Python2环境。
官方源码compiler/opcode/marshal未改，MinGW平台适配文件前后SHA记入BUILD.json。
许可：CPython、Zig、MinGW-w64 CRT、LLVM runtime、zlib，均附原文。

目标Windows10/11；使用OS的UCRT和KERNEL32/ADVAPI32/SHELL32/USER32等系统组件，
不再分发微软CRT，不支持XP/Win7。若OS组件缺失须修复系统，不得用游戏DLL/PATH编译器充数。

启动GUI自动做两VM版本/魔数/位数/整套SHA探测，可从菜单重新检查，无需先打开源码。
双击`../检查内置编译器.bat`做真正的双编译/marshal验收，不执行目标源码。
`build_exe.bat`须全部审计及严格GUI/原生包回归通过才生成EXE；不能把skip当通过。

**2026-10-23 已在用户真实 Windows 上通过 `检查内置编译器.bat` 的双编译/marshal
验收，GUI 状态栏显示 `2/2可用`**（见`../../docs/archive/STATUS_HISTORY.md` §3.81）。该验收只编译并
回读 marshal，不执行目标源码，也不等于游戏客户端加载验收。
哈希证明与清单一致，非签名、法律审核或逐位可重现构建证明。
来源、重建命令及剩余实机检查见[运行时记录](../M4_RUNTIME_DISTRIBUTION.md)。

若自检报`runtime文件SHA256不匹配`，是Git把文本文件的换行改成了CRLF：
双击`../修复编译器文件.bat`即可（不需要git、不联网，只按清单校字节）。
