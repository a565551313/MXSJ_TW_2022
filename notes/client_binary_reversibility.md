# 客户端二进制（mx.exe / mxmain.dll / mxLauncher.exe）能做到什么程度

> 结论先说：**这三个东西反编译不出源码**。脚本层（`data/script.fls` 里的定制 Python 2.5
> 字节码）能出可读 `.py`，那是另一回事，见 `notes/opcode_mapping_and_decompilation.md`
> 与 `docs/DECOMPILE_CORPUS.md`。二进制层只能出**汇编 + 伪 C + 一份结构清单**。
> 本文把"能不能"用实测数据钉住，免得下一个人再去试一遍。
> 全部数字于 2026-10-15 在本仓库根目录（游戏安装目录）实测得出。

## 1. 三个对象其实只有两颗

| 文件 | 大小 | MD5 | 说明 |
|---|---|---|---|
| `mx.exe` | 9,698,712 B | `2609423fe7fadd5446eb2425ab894ac8` | 与 `mxmain.dll` **逐字节相同** |
| `mxmain.dll` | 9,698,712 B | 同上 | 同一颗镜像换名加载 |
| `mxLauncher.exe` | 1,659,992 B | `b1ce8c9f11ff6596c680f0b3d8bd9dd9` | 启动器，独立一颗 |

`mxmain.dll` 的导出表里 DLL 自报名是 **`ClientLoader.exe`**，只导出两个具名函数：

```
?JSON_DecodeObject@@YAPAXPAU__JSONObjectDecoder@@PBDI@Z
?JSON_EncodeObject@@YAPADPAXPAU__JSONObjectEncoder@@PADI@Z
```

即 `void* __cdecl JSON_DecodeObject(__JSONObjectDecoder*, const char*, unsigned)` 与
`char* __cdecl JSON_EncodeObject(void*, __JSONObjectEncoder*, unsigned)`
（按 MSVC 修饰规则手工还原；实测 binutils 2.40 的 `c++filt` **不改写** `?…@@` 名，
要自动还原得用 `llvm-cxxfilt`）。这是二进制层唯一能白拿的"源码级信息"。

## 2. mx.exe / mxmain.dll：静态只能到伪 C，且有一半镜像读不进去

`objdump -h` + 逐节香农熵（>7.4 判为加密/压缩）：

| 节 | 大小 | 熵 | 判读 |
|---|---|---|---|
| `.text` | 2,811,918 | 6.64 | 正常 x86 码，**没被壳盖住**，可反汇编 |
| `.rdata` | 1,224,536 | 5.99 | 明文数据 + RTTI 名 |
| `.data` | 322,560 | 5.10 | — |
| `_dyprot0` | 3,237,612 | **7.85** | 多益保护壳（配套 `DuoyiProtect.dll`），静态读不进去 |
| `_dyprot1` | 1,981,616 | **7.72** | 同上 |
| `.rsrc` | 105,821 | 5.15 | 图标/manifest |

⇒ `.dyprot` 两段共 **5.2 MB ≈ 全镜像 54%**，是加密/压缩载荷。静态分析只能覆盖剩下的部分。

其它实测特征：

- **无符号表、无 PDB 路径**（`objdump --syms` = no symbols）。
- 依赖 37 个 DLL，**其中没有任何 `python2x.dll`** ⇒ 解释器是自己内嵌的定制 Python（与
  `AGENTS.md`「双 VM：`mxmain.dll` 内定制 2.5、`exe/python27*.dll` 内定制 2.7」一致）。
- 明文可得的"结构清单"只有 RTTI：**331 个 `.?AV` 类名**，例如
  `CCommonWnd` / `CGameWnd` / `CMainWnd` / `CChatWnd` / `Common::CLogFile` / `fmt::FormatError`。
  这些能当锚点用（vftable 交叉引用 → 反推成员偏移），但不会变成源码。
- **关键负面结果**：全仓所有 `.dll`/`.exe` 明文里 `CCombPanel`、`FONT_EDIT`、
  `PyArg_ParseTuple` 命中数**都是 0**。也就是说 `interface` / `combdialog` 这些原生
  包装类的注册名与常量名不在明文库里（大概率就在那 5.2 MB 高熵段内）。

## 3. mxLauncher.exe：这颗是"可读"的，但仍不是源码

- 无壳（`.text` 熵 6.70、`.rdata` 5.90），MFC/ATL **VS2003** 静态链接
  （串里有 `C:\Program Files (x86)\Microsoft Visual Studio 8\VC\atlmfc\include\afxwin1.inl`
  与 `f:\sp\vctools\vc7libs\ship\...`）；PE 头带 `HAS_LINENO|HAS_DEBUG|HAS_LOCALS`，
  但 COFF 符号表已被剥掉（`objdump --syms` = no symbols）。
- `.rsrc` 1,134,072 B：对话框、控件表、图标、版本信息、manifest —— **这部分能近乎原样导出**
  （`rc /fo` + Resource Hacker 一类工具，或 Ghidra 的 resource 视图）。
- RTTI 115 个类名，含自己的控件类：`CBackWin`、`CMxBitmapButton`、`CMxLink`、
  `CMxProgressCtrl`；串里还能看到 `DY_GAME_UPDATER`、`DestroyResDownloader`、
  `Software\...\protocol\StdFileEditing\server` 之类更新器/OLE 自动化痕迹。
- 结论：**能出伪 C + 完整资源 + 类名清单**，变量名/注释/函数边界靠人重建；
  工程量以周计，产出是"看得懂流程"，不是"能重新编译"。

## 4. 真要推进的话，三条路的成本

| 目标 | 手段 | 成本/收益 |
|---|---|---|
| 回答"本版 `interface` 有没有某个常量/方法" | **别看二进制**，跑运行期探针（出货包里让脚本 `dir(interface)` 写日志），或看新包自动打的 `font FONT_EDIT` / `font fallback FontLT14_3` 日志行 | 分钟级 ⇒ 直接决定脚本怎么写，**优先** |
| 搞清启动器流程/更新协议/资源 ID | 解析 `mxLauncher.exe` 的 `.rsrc` + 串 + RTTI，出一张清单 | 半天～一天；只服务"启动/更新线"，不解决脚本层问题 |
| 要动引擎本体（如让窗口标题走 Unicode、加原生接口） | Ghidra/IDA 全量反编译 + 打补丁；5.2 MB 高熵段还得先绕壳 | 人年级 + 需要 Windows 实机；**当前没有任何待办需要它** |

> 沙箱侧现实：无 `java`（Ghidra 跑不起来）、无 IDA；`capstone`/`pefile` 可从 pypi 装上，
> 够做定点反汇编（本文的入口反汇编就是这么出的），不够做全量反编译。

## 5. 复现命令

```sh
md5sum mx.exe mxmain.dll mxLauncher.exe
objdump -f mx.exe | head -6                 # 架构/入口
objdump -h mx.exe                           # 节表（配合逐节熵计算）
objdump -p mx.exe | sed -n '/The Export Tables/,/The Import Tables/p'
objdump -p mx.exe | grep -A600 "The Import Tables" | grep "DLL Name" | sort -u
strings -a mx.exe | grep -c '^\.?AV'        # RTTI 类名数
strings -a mx.exe | grep -c CCombPanel      # 关键负面结果：0
```
