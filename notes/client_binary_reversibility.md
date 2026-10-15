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
  **所以别拿 `strings` 的 0 命中当证据**——它既不能证明"`interface` 没有 `FONT_EDIT`"，
  也不能证明有；这类"符号在不在"的问题只能靠运行期探针（见 §4 第一条）。

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

## 6. 启动器资源：已经整份抽出来了（2026-10-15）

工務已落成工具，**不要手工再解一次**：`tools/data-parser/pe_resource_dump.py`
（只用标准库；输入档全程唯讀；解不动的就留原字节 + 在 manifest 记 `note`，不猜）。
回归测试 `tools/data-parser/test_pe_resource_dump.py`（12 项：自建最小 PE + 真档核对）。

`mxLauncher.exe`（1,659,992 B，SHA-256 `3eeba17e7be96fcc…`）→ **86 条资源**：

| 资源型别 | 条数 | 抽出来是什么 |
|---|---|---|
| BITMAP | 30 | 32bpp DIB（补上 BMP 头即成 `.bmp`）：按钮/进度条切片，151×48、151×42 这类尺寸 |
| 具名型別 `PNG` | 1 | **545,162 B / 982×553 的整套启动器皮肤**：`新夢想世界 Online` logo、四个页签（新手指引/官方網站/官方論壇/遊戲資料）、新闻区、`進入遊戲`/`檢查更新`、下载与更新两条进度条。PNG 里带 Photoshop CC 2015 的 XMP 元数据 ⇒ **皮肤是 2015 年重画的**，而版式里的版权字串还停在 `Copyright (C) 2008` |
| CURSOR + GROUP_CURSOR | 16 + 15 | 组装成 15 个 `.cur`（MFC 自订光标，每项 1~2 张图） |
| ICON + GROUP_ICON | 1 + 1 | 1 个 `.ico`（程序图标，主图 67,624 B） |
| STRING | 14 块 | 82 条字串：id 117 = `关于 mxstartup(&A)...`，其余多为 MFC 内建（61456+） |
| DIALOG | 5 | **全部解出**：`100`「梦想世界更新程序」235×55（4 控件，`确定`按钮）；`102` 415×307、18 控件，**id 1000 是 WebBrowser ActiveX**（CLSID `{8856F961-…}`）⇒ 新闻/广告是 IE 控件承载，不是自绘；`179` 空模板；`30721`/`30734` 是 MFC 内建（AFX）模板 |
| VERSION | 1 | `file_version = 128.0.1.0` —— **别拿它当版本号**：`update.ini` 写的是 `2.27.2`，串里另有 `1.5.4`，三者互不相干 |
| MANIFEST | 1 | 空 `assembly`（既没有 UAC 声明也没有 comctl32 版本依赖） |
| 型別 240 | 1 | 170 B 自定义块，未解出，按原样落地 |

自检规则：版式必须**刚好吃掉整个 buffer**，否则退回 `.bin` 并记原因；所以「解出来了」这件事本身是可证的。

## 7. 但「资源包」的主体不在 exe 里

启动器内嵌的只是**它自己的皮肤与版式**。真正的游戏资源与更新链路在客户端目录：

- 游戏资源：`data/*.fls` 共 7 个（`script.fls` 24,454,082、`magicres5.fls` 21,544,668、
  `skill2.fls`、`effect.fls`、`skill.fls`、`passive.fls`、`data.fls`）——这条线已有
  `tools/decompiler/`（反解）与 `tools/data-parser/repack_fls.py`（回填），**跟 PE 资源无关**。
- 皮肤外掛：串里有 `bk%d.png` 与 `resource\updaterbk.res`；本仓库 `resource/` 只剩一个空的
  `history.his` ⇒ 实机找不到就退回内嵌那张 PNG，**所以上表抽出来的图就是玩家看到的图**。
- 更新/下载：`update.ini`（UTF-8）`[Setting] Version=2.27.2`、`UpdateURL=http://mxupdate.lager.com.tw/httpupdate.txt`、
  `FileInfoURL=https://mxconfig.duoyi.com/filemd5.txt`（**服务器侧的 MD5 清单**）、
  `[Download] DLServerUrl=http://dtminiclient.lager.com.tw/mini/mx/`；另有 `[HK]` 段（港版另一组 URL）。
- 下载器也不在 exe 里：`ResLib.dll`（399,216 B，内嵌 libcurl，**没有导出表**，只导入 6 个 DLL；
  日志格式串 `rid:%d fid:%u uid:%u url:%s httpcode:%d`、`Range: bytes=%I64u-`）；
  `exe/ResLib.dll` 是**另一颗**（MD5 不同），别当同一份。
- 自我更新：`patch/mx.bin` 与 `mxLauncher.exe` **MD5 相同**（`b1ce8c9f11ff6596c680f0b3d8bd9dd9`）
  ⇒ `mx.bin` 就是「新版启动器自己」，配 `patch/mxupd.exe` + `%s.tmp` + `mxpatch_shadow`/`mxpatch_run` 完成替换。
- 字体：串里 `AddFontResourceA` + `%s\Fonts\FZLanTingYuan-DB-GBK.ttf` ⇒ 仓库 `Fonts/` 那 4 个 ttf
  是启动器注册给 UI 用的（**注意是 GBK 版 latin‑ting‑yuan**，与繁中显示那条线直接相关）。

### 复现

```sh
python3 tools/data-parser/pe_resource_dump.py mxLauncher.exe --summary
python3 tools/data-parser/pe_resource_dump.py mxLauncher.exe --dump /tmp/launch_rsrc \
    --json /tmp/launch_rsrc/summary.json
md5sum mxLauncher.exe patch/mx.bin          # 相同 ⇒ mx.bin 就是启动器本体
python3 -c "print(open('update.ini',encoding='utf-8').read())"
strings -a -n 5 mxLauncher.exe | grep -Ei 'ResLib|update\.ini|bk%d|Fonts|MX_SPLASH'
```
