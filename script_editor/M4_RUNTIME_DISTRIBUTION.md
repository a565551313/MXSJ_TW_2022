# M4 · Windows双运行时整套审计与发行检查（0.3.2.dev1）

**已补齐真实Windows x86双编译器并入库；2026-10-23 用户真实Windows上通过
`检查内置编译器.bat`双编译/marshal验收、GUI显示`2/2可用`；EXE打包与游戏客户端
加载验收仍未做。**
官方CPython源码经Zig0.13.0交叉构建，2.5.6为156个core编译单元、2.7.13为178个，均0失败。
4个EXE/DLL均为真实PE32/i386，不是合成测试PE；完整标准库、许可和SHA已齐。
仅MinGW平台适配，compiler/opcode/marshal实现未改，不使用游戏DLL。
编译器生成物已入库（用户2026-10-23决定，见`../docs/STATUS.md` §3.79），克隆即得，
不再只随完整源码ZIP交付；普通用户不需要重建它们。重建时二进制与`manifest.json`
必须成对提交，每轮构建永久占用约6.7MB Git历史。

## 1. 为什么补这一层

原逻辑仅在注册时比较EXE的SHA，无法发现python25.dll/python27.dll、标准库ZIP或其它依赖变化。
现在`core/compiler/bundles.py`独立做有界清单读取、完整文件集合与哈希、PE32/x86、来源/许可记录检查。
`Compiler`携带不可变BundlePin：清单SHA、VM、根目录与每个文件SHA；
版本探测、实际编译、标准marshal审计前重新核验，子进程后再次核验，变化则不发布输出。
编译输出保护扩展到整套运行时文件及清单。显式开发编译器保持原有API，但GUI标明没有随包整套审计。

- 拒绝额外/缺失文件、非法/绝对/越界/反斜杠/Windows保留路径名、大小写冲突。
- 拒绝符号链接/Windows重解析点；EXE/DLL/PYD检查x86 PE32及EXE/DLL类型。
- JSON重复字段/VM、错误精确版本/魔数/32bit、来源或许可缺失均失败；清单读取限制4MiB。
- 要求python.exe、对应标准DLL、标准库ZIP；所有其它依赖及许可文件同样列入SHA清单。
- 许可中必须有CPython；随包MSVCR/MSVCP/VCRUNTIME时必须有Microsoft CRT许可记录。
- schema1空清单仍作为不可用状态识别；**schema1非空的EXE-only清单拒绝，不静默降级**。

## 2. schema2（当前随包清单）

顶层：`schema: 2`与`compilers: [...]`。发行必须恰有py25/py27两套；
GUI单独检查某VM时可只检查该VM，不能据此声称完整双VM发行。
每项字段：

| 字段 | 要求 |
|---|---|
| vm/platform | py25或py27 / win32 |
| version/bits/magic | 2.5.6 / 32 / b3f20d0a，或2.7.13 / 32 / 03f30d0a |
| root/executable | `py25/win-x86`与`py25/win-x86/python.exe`（py27同理） |
| files | 相对本项root的POSIX路径→64位小写SHA256，**完整文件集合** |
| source | url（官方CPython HTTPS来源）、revision（精确40位源码commit）、archive_sha256 |
| licenses | `[{component, path}, ...]`，path相对本项root，须列入files且文件非空 |

source是构建者对来源的声明，哈希只能证明与本地可信清单一致；
不能证明binary确由该源码编译、不能替代签名/可重现构建或人工许可证审核。
不会从不可信manifest下载或运行新文件。需从真实构建和实际许可文件生成记录，不能填示例哈希。

## 3. 审计和精确复制

在工具源码目录设置`PYTHONPATH=src`后：

```text
python -m script_editor.runtime_cli audit --root . --static
python -m script_editor.runtime_cli audit --root .
python -m script_editor.runtime_cli stage --root . --destination dist/MXSJScriptEditor
```

- `--static`可在Linux运行：只有文件/PE/声明检查，JSON状态明确`static-only`，不执行任何PE。
- 不带`--static`必须在Windows：精确探测两VM、真实编译包含嵌套函数/繁体Unicode/非UTF8逻辑文件名的
  自写源码、完整marshal读取，并确认带写文件/raise的目标源码未执行。不能当作客户端游戏验收。
- stage要求已有发行根目录，但其runtimes子目录必须**不存在**；不覆盖任何已有目录。
  只复制清单列出的文件和manifest，复查复制后的字节、检查源清单竞态，再做对应审计。
  失败仅清理本次创建的runtimes，不删除已有EXE或输入文件。
- JSON可重定向保存为发行根的`runtime-audit.json`；它是运行时编译/marshal记录，
  不是GUI双击、DPI、游戏加载或注册业务已验收的证据。

## 4. Windows发行检查

`build_exe.bat`改为失败关闭：

1. 在安装依赖前执行双运行时完整Windows编译/marshal检查；空清单立即拒绝。
2. 创建venv/安装依赖。
3. `release_checks`从随包位置设置**仅测试进程的**MXSJ_PY25/MXSJ_PY27，运行全套测试。
   必须发现指定GUI/真实双编译器/双VM原生端到端测试，防止空目录/漏测试假绿；
   GUI及真实双编译器skip一律导致失败；仅6个确切的独立游戏/DLL材料opt-in测试允许缺失。
   测试后再审计运行时，捕获标准库写缓存/变化；环境变量用完恢复，不改系统PATH。
4. PyInstaller onedir，保留EXE + _internal布局；两套legacy运行时不塞入onefile临时目录。
5. 精确复制runtime并在新目录再次实际验收，写runtime-audit.json；任何一步失败不打印成功。

这是发行构建，不能再用空manifest构建一个看似免安装的目录。
开发查看GUI仍可直接运行bootstrap/run.py；缺编译器就禁编译，不替换成系统Python。

## 5. 本次来源与构建

2026-10-15实际下载并校验的官方归档：

| 版本 | 官方tag的commit | codeload源码SHA256 |
|---|---|---|
| 2.5.6 | 11a859d70dffc8da51d346dabd1fe6a635825ae5 | c68b9e84e9a302d120e5ec3ada6ef9fceb84d7768cea63dedb3074c6ed47bcfa |
| 2.7.13 | 9c1426de7521299f70eb5483e7e25d1c2a73dbbd | ae1dc735e2990bf8de8e73c3f77b35d4f69502570957c743a7e8618a652fe08a |

来源URL为`https://codeload.github.com/python/cpython/tar.gz/refs/tags/v2.5.6`及`v2.7.13`。
纠正旧文档的2.7.13归档SHA；二进制/ZIP各自的实际SHA另列manifest，不混用源码归档SHA。

维护者重建（需要联网及磁盘空间；普通用户无需运行）：

```text
python -m pip install ziglang==0.13.0
python build_runtimes.py --work NEW_WORK_DIRECTORY --destination NEW_RUNTIME_DIRECTORY --jobs 4
```

两个目录都必须尚不存在，避免覆盖；脚本校验归档、拒绝目录穿越/链接、
按官方VC工程源列表编译、链接真实EXE/DLL，再生成标准库、5份原许可、BUILD.json与整套SHA清单。
可审查代码和固定来源重建，但不宣称不同宿主/时间生成的PE逐位一致。

平台适配：posixmodule.c的Windows分支允许MinGW；dynload_win.c私有strcasecmp重命名避免SDK冲突；
2.7 signalmodule.c的Windows.h改成windows.h适配大小写敏感文件系统。
每处被修改源文件的前后SHA都记在BUILD.json。没有改编译器语法、opcode表或marshal。

每VM根目录9个文件（EXE、DLL、ZIP、BUILD及5许可），18个文件均做整套校验。
标准库ZIP为ZIP_STORED纯.py，排除test/tests/idlelib/lib-tk；不承诺通用Python2外部扩展。
目标为**Windows10/11系统UCRT**，实际PE导入为系统KERNEL32/ADVAPI32/SHELL32/USER32及
api-ms-win-crt-*。不随包复制微软CRT，不支持XP/Win7；许可原文包括CPython/Zig/MinGW/LLVM/zlib。

## 6. 启动检查与验收边界

GUI开窗后自动后台检查两VM，显示版本/魔数/32bit/整套SHA结果，无需先打开源码。
缺件或损坏只禁该VM编译，仍可阅读/编辑源码；错误显示在诊断区，不伪造“已通过”。
`检查内置编译器.bat`和`bootstrap.py --check-only`做完整编译/marshal检查；后一项也检查Qt加载。

静态审计已通过，但不把交叉构建、模拟PE测试、Linux编译回归或Wine兼容层测试当真实Windows验收。
曾尝试push触发Windows CI，run 38662087057在分配任何job前startup_failure，
没有Windows执行结果；未保留无法启动的试验工作流，不以CI配置代替通过证据。

仍须验证：真正Windows启动和双编译/marshal；中文/空格/跨盘路径与旧ANSI argv；
没有开发环境的干净Win10/11上的系统依赖；PyInstaller父进程DLL路径、NTFS文件锁、
DPI/快捷键/退出、EXE自构建/双击、客户端加载与注册业务。
0.5已获用户授权附带固定原包匹配的解码参数（详decoding/README.md），不含原游戏包、
注册补丁或离线探针，不改变account/CBox或用户布局。

测试标准和mock审计护栏保持：合成PE/mock仅证明拒绝规则，不是运行时来源证明。
只有真实Windows执行与桌面验收补齐后，才能把M4和免安装发行标为完成。
