# M4准备 · Windows双运行时整套审计与发行检查（0.3.1.dev1）

**已实现检查代码；未交付Windows运行时或EXE，M4没有完成。**
当前manifest仍空，不能执行内置编译。M3的14项真实GUI测试也仍缺系统库未执行。
本轮没有上传、自动下载二进制、使用游戏DLL、修改PATH或提交编译器/FLS。

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

## 2. schema2（格式说明，不是可用清单）

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

## 5. 已核对来源事实与未解决条件

本地已从官方CPython源码编译出的**Linux**2.5.6/2.7.13继续只用于Linux回归。
2026-10-15只读GitHub refs确认（不是Windows二进制验证）：

| 版本 | 官方tag的commit | 本地已下载codeload源码SHA256 |
|---|---|---|
| 2.5.6 | 11a859d70dffc8da51d346dabd1fe6a635825ae5 | c68b9e84e9a302d120e5ec3ada6ef9fceb84d7768cea63dedb3074c6ed47bcfa |
| 2.7.13 | 9c1426de7521299f70eb5483e7e25d1c2a73dbbd | 0e3cfac947d2a6c7ac6938d2457861bf4590ae4a30b00ab74647f40c542d7b84 |

来源URL为`https://codeload.github.com/python/cpython/tar.gz/refs/tags/v2.5.6`及`v2.7.13`。
这些是现有源码包的hash，**不能填作Windows EXE/DLL/ZIP的hash**。
2.5.6源码PCbuild是旧vcproj，2.7.13为vcxproj；不能假设当前Windows runner拿到源码就能构建。

尚未解决：Windows构建机/匹配旧工具链、真正标准x86双运行时及CRT再发行许可、逐文件实际哈希，
PyInstaller父进程DLL搜索路径对legacy子进程的影响、中文/空格/跨盘路径与旧ANSI argv，
NTFS文件锁/硬链接、DPI/快捷键/退出、EXE双击、客户端加载与注册业务。
另未解析所有PE动态导入/LoadLibrary依赖闭包；Windows构建机预装依赖可能掩盖漏件，
仍须在没有开发环境的干净Windows上验证，不能仅靠清单数量宣称依赖闭包完整。
沙箱没有Windows/Wine执行环境，四个Qt依赖仍缺libGL/libEGL/libxkbcommon/libdbus。
没有用伪造库或合成PE冒充真实运行时验收。

## 6. 本轮测试范围

24项新增运行时测试使用**明确的合成PE头/测试标准库内容及mock probe**，
只验证拒绝规则、整套文件pin重核验、精确复制/失败清理/竞态、CLI退出码和发行skip规则。
不是标准Windows运行时、没有启动这些合成EXE。
标准库ZIP宜用ZIP_STORED；若用压缩ZIP，必须把相应标准zlib依赖及其许可完整纳入运行时，不能依赖系统模块。
既有真实Linux双编译器和双包两轮M3工作流仍全量回归；实际计数见STATUS。
只有补齐真实Windows执行与桌面验收后，才能把M4和免安装发行标为完成。
