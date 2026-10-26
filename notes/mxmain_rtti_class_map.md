# mxmain.dll 的 RTTI 类图、虚表与虚析构清单（2026-10-26）

> 结论先行：
> 1. **明文 RTTI 是一份完整的类清单**：`mxmain.dll` 里 352 个 TypeDescriptor、305 个
>    CompleteObjectLocator、305 张虚表、**1,769 个虚函数槽**、305 条继承链，全部可用
>    `tools/data-parser/mxmain_rtti.py` 一次性解出；`_dyprot0/1` 那 54% 高熵段不参与，
>    所以这份清单是**只靠明文就能站住**的。
> 2. **它给的是"类 → 基类链 → 虚函数地址"，不是"方法名"**。要问"某个原生类有没有某个
>    方法"，还是要另找锚点；但本文 §6 记了一个此前被判定"只能靠运行期探针"的例外：
>    **原生→脚本回调名表就在明文 `.rdata` 里**。
> 3. 边界没变：仍然**反不出源码**。本清单是"锚点集"，用来让后续反汇编从"猜"变成"查表"。

配套工具：`tools/data-parser/mxmain_rtti.py`（只读解析，标准库）+ 回归
`tools/data-parser/test_mxmain_rtti.py`（14 项）。锁定输入：
`mxmain.dll` = `mx.exe`，9,698,712 B，SHA-256
`637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`。

## 1. 这份清单能回答什么、不能回答什么

| 问题 | 现在能不能答 | 依据 |
|---|---|---|
| 客户端有哪些原生类？分布在哪些子系统？ | **能**，305 个有虚表的 + 47 个无虚表的全部列出 | 本文 §4、§3 |
| `CMainWnd` 继承谁？`CMapHeroObject` 呢？ | **能**，深度优先链完整 | §4 的"继承自上"列 |
| 某个类的虚函数在哪个地址？ | **能**，按槽序号给全 | 生成 `--json` / `--md` |
| 某个类有哪些虚函数？ | **只能给地址**，名字要靠脚本绑定表或反汇编 | §2 第 5 条 |
| 某个坐标（如 `0x4c5e40`）属于谁？ | **能**，只要它正好是虚函数入口 | §5 的对照表 |
| `interface` 有没有某个方法？ | **部分能**（回调名表在明文里），但需要逐名 xref | §6，未结案 |
| 某个类的成员变量偏移/名字 | **不能**（只有虚析构里露出的少量偏移片段） | §8 |
| 源码 / 重新编译 | **不能**，与 `notes/client_binary_reversibility.md` 的结论一致 | §8 |

## 2. 怎么解出来的（结构、实测坑与一次自证）

解析链是教科书式的 MSVC RTTI 四件套，但每一条都踩过坑，写下来免得下一个人重踩：

```text
.data    TypeDescriptor      [vfptr][spare][.?AV...]           → 类名 + TD 地址
.rdata   CompleteObjectLocator [0][0][0][pTD][pCHD]            → COL 地址
.rdata   ClassHierarchyDescriptor [0][attr][numBase][pBCA]     → 基类数组
.rdata   BaseClassDescriptor   [pTD][numContained][mdisp][pdisp][vdisp][attr][pCHD]  (28 B)
.rdata   虚表                  [COL 指针][槽0][槽1]…            → 虚函数地址
.text    `C7 /0 imm32`         movl $虚表,(%reg)                → 写 vfptr 的位置
```

1. **指针是绝对 VA（`0x400000 + RVA`），不是 RVA。** 照 SDK 注释当 RVA 用会一个都对不上
   （本文第一版就是这么得出"0 个 COL"的）。
2. **TypeDescriptor 是 `[vfptr][spare][name]`**，352 条的 `vfptr` 全是同一个值
   `0x77cb64`。这个值本身也在清单里：它是 `type_info@@` 的虚表，两个槽
   （`0x5c1b90` 析构 + 一个比对函数），于是"名字前面的 8 字节"就是结构起点，
   不需要另外找表头。
3. **BaseClassDescriptor 实测步长 28 字节（7 个 dword），不是 SDK 写的 24。** 判定依据是
   同一条 BaseClassArray 里两个目标相差 28；解出来的字段顺序
   `[pTD][numContained][mdisp][pdisp][vdisp][attr][pCHD]` 能把 std 的
   `ios_base::failure` → `system_error` → `_System_error` → `runtime_error` → `exception`
   五层链**完全解对**（MSVC 的真实继承就是这样），这条链现在是回归测试项的固定期望。
4. **BaseClassArray[0] 是类自己**，之后才是祖先，深度优先；把 [0] 当基底会多算一层。
5. **虚表只有 `[COL][槽0]…` 这一种形态，槽 0 是 scalar deleting destructor**；
   同一个类可以有多个"写 vfptr"的位置（构造、工厂、异常对象创建等），
   本次共 292 个类找到写入点、合计 919 处。**不能把写入点数量当方法数**，
   例如 `ZXQRCodeECB` 有 106 处——那是一张静态 QR 码版本表的逐项构造，不是 106 个虚函数。
6. **扫槽位时有两个必须挡掉的假阳性**：① `CMapHeroObject` 虚表后面紧跟一段方法名
   字串（`GetHeight` / `GetSize` / `ClickID` / `SetText` …）字串 `"ii"` 会被读成指针 `0x00696969`，
   它恰好落在 `.text` 里，看起来完全合法；② `std` 系列的 deleting destructor 入口是
   **奇数地址** `0x5c6085`，任何"4 字节对齐"假设都会把 52 个类的虚表整个砍掉。
   工具用"目标必须落在 `.text` 且不以 `0x00`/`0x0F` 开头"来收尾，两条都有回归测试。

**自证**：`type_info@@` 的虚表地址 `0x77cb64` 与 352 条 TypeDescriptor 里的 `vfptr` 字段
完全一致；`CMapHeroObject` 的虚表里第 2 槽 `0x4c5e40` 正好等于
`notes/native_tcp_channel.md` 里用另一条路（原生指令模拟）定出的 LZW 解压函数；
`0x4c5d50`（同一笔记里的"LZW 初始化"）正好落在 `CLZWDecompress` 写 vfptr 的位置上。
三条独立路径对上同一批地址，说明这张表可以当锚点用。

## 3. 统计（本版实测）

| 指标 | 值 |
|---|---|
| RTTI 名字（`.data` 内） | 352 个 TypeDescriptor / 355 条不同名字串 |
| 有 COL（即有多态） | 305 |
| 有虚表 | 305，**合计 1,769 个槽** |
| 无虚表（纯数据/接口/λ） | 47，例如 `CGameWnd`、`CPaletteOp`、`_cef_*_t`、全部 `<lambda_*>` |
| 继承链解析失败 | 0 |
| 找到写 vfptr 的位置 | 292 个类 / 919 处 |
| 槽数分布 | 1 槽 63、2 槽 65、3 槽 26、4 槽 33、5 槽 9、6 槽 12、7 槽 37、8–19 槽 32、21–24 槽 28 |

命名空间分布（`@ns@@` 里的 ns）：全局 115、`Concurrency::details` 42、`Graphics` 34、
`Concurrency` 29、`std` 24、`Switch` 9、`Common` 6、`duoyi_gif` 6、`Network` 3、`fmt` 3、
`TimeLog`/`GlobalCore`/`GlobalNode`/`Sound`/`Dmp`/`Debug` 各 1，其余为模板/λ 的残片。

**两个可以直接拿去做设计判断的结构事实**：

- **窗口类几乎不写虚函数。** `CCommonWnd`/`CMainWnd`/`CChatWnd` 的虚表都只有 1 槽
  （虚析构），也就是说窗口层面的分发不走虚表；`CMainWnd : CCommonWnd : CGameWnd`
  这条链上真正的"方法"是普通成员函数，要靠调用点或脚本来找。
- **渲染对象是另一套。** `CBaseObject` 与它的 20 多个子类（`CSpriteObject` 23 槽、
  `CMapHeroObject` 23 槽、`CTextObject` 22 槽…）是货真价实的多态体系，
  它们的虚表槽位可以直接对照渲染循环的调用点，这是后续做"对象生命周期/渲染顺序"
  研究最省力的一条线。

## 4. 引擎类清单

下面按子系统分组，字段含义：虚表 = 虚表起始地址（`[COL]` 之后第一格）；
槽 = 虚函数个数；虚析构 = 槽 0 的地址（scalar deleting destructor）；
"继承自上"不含自身，深度优先；vfptr 写入点 = `movl $虚表,(%reg)` 的出现次数。
**全部地址都在首选基址 `0x400000` 下，实际加载若发生重定位不能直接当进程地址**
（与 `notes/native_tcp_channel.md` 的口径一致）。

表里是 172 个引擎/第三方类；另外 180 个是静态链接运行库与模板残片（`std` 24、`Concurrency` 29、`Concurrency::details` 42，其余是 `?$_Func_impl`/`<lambda_*>`/`_cef_*_t` 一类），不逐条列；完整 352 行表格用

```bash
python3 tools/data-parser/mxmain_rtti.py mxmain.dll --md /tmp/rtti.md
```

即可重出（`--json` 另给 `mdisp`/`pdisp`/`attributes` 等原始字段）。

### 4.1 窗口 / UI / 内嵌浏览器（35）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `?$CefStringBase@UCefStringTraitsUTF16@@@@` | `0x6b5e80` | 1 | `0x46c9c0` | — | 43 |
| `?$CefStructBase@UCefBrowserSettingsTraits@@@@` | `0x6bb938` | 1 | `0x4b19c0` | _cef_browser_settings_t@@ | 3 |
| `?$CefStructBase@UCefMainArgsTraits@@@@` | `0x6b5e70` | 1 | `0x46cab0` | _cef_main_args_t@@ | 2 |
| `?$CefStructBase@UCefSettingsTraits@@@@` | `0x6b5efc` | 1 | `0x46ca10` | _cef_settings_t@@ | 1 |
| `?$CefStructBase@UCefWindowInfoTraits@@@@` | `0x6bb658` | 1 | `0x4b1a60` | _cef_window_info_t@@ | 2 |
| `CAtom@@` | `0x6ba610` | 7 | `0x4a2f90` | — | 7 |
| `CBoxAtom@@` | `0x6ba670` | 7 | `0x4a2fc0` | CAtom@@ | 2 |
| `CCefObject@@` | `0x6bb488` | 1 | `0x4af4f0` | — | 2 |
| `CChatWnd@@` | `0x6b112c` | 1 | `0x44b2a0` | CCommonWnd@@ → CGameWnd@@ | 1 |
| `CCommonWnd@@` | `0x6b111c` | 1 | `0x44b2a0` | CGameWnd@@ | 7 |
| `CFont@Graphics@@` | `0x7978b0` | 3 | `0x619e70` | — | 11 |
| `CFtFont@Graphics@@` | `0x7978c0` | 3 | `0x619ec0` | CFont@Graphics@@ | 3 |
| `CGameCefApp@@` | `0x6b5ec8` | 5 | `0x46cbe0` | CefApp@@ → CefBase@@ | 1 |
| `CGameCefHandler@@` | `0x6bb7f0` | 15 | `0x4b1b80` | CefClient@@ → CefBase@@ → CefContextMenuHandler@@ → CefBase@@ → CefLifeSpanHandler@@ → CefBase@@ → CefLoadHandler@@ → CefBase@@ → CefDragHandler@@ → CefBase@@ → CefRenderProcessHandler@@ → CefBase@@ → CefRequestHandler@@ → CefBase@@ | 1 |
| `CGameWnd@@` | `—` | 0 | `—` | — | 0 |
| `CIconAtom@@` | `0x6ba630` | 7 | `0x4a3030` | CAtom@@ | 4 |
| `CMainWnd@@` | `0x6b1124` | 1 | `0x44b2e0` | CCommonWnd@@ → CGameWnd@@ | 3 |
| `CRichTextObject@@` | `0x6ba690` | 22 | `0x4a30b0` | CBaseObject@@ | 2 |
| `CStretchFont@Graphics@@` | `0x7978d0` | 3 | `0x619f30` | CFont@Graphics@@ | 3 |
| `CText@Graphics@@` | `0x799330` | 7 | `0x633730` | CGrapObject@Graphics@@ | 4 |
| `CTextAtom@@` | `0x6ba650` | 7 | `0x4a30e0` | CAtom@@ | 2 |
| `CTextObject@@` | `0x6b9a98` | 22 | `0x496ec0` | CBaseObject@@ | 3 |
| `CViewportObject@@` | `0x6bafa0` | 22 | `0x4a9ee0` | CBaseObject@@ | 1 |
| `CWinFont@Graphics@@` | `0x799538` | 3 | `0x638f80` | CFont@Graphics@@ | 3 |
| `CefApp@@` | `0x6b5e9c` | 5 | `0x46cbe0` | CefBase@@ | 1 |
| `CefBase@@` | `0x6b5e88` | 4 | `0x5c08f8` | — | 6 |
| `CefClient@@` | `0x6bb79c` | 15 | `0x46cbc0` | CefBase@@ | 1 |
| `CefContextMenuHandler@@` | `0x6bb6d4` | 4 | `0x4b1f00` | CefBase@@ | 0 |
| `CefDragHandler@@` | `0x6bb6fc` | 2 | `0x4b2310` | CefBase@@ | 0 |
| `CefLifeSpanHandler@@` | `0x6bb71c` | 5 | `0x4b2040` | CefBase@@ | 0 |
| `CefLoadHandler@@` | `0x6bb668` | 4 | `0x4b24e0` | CefBase@@ | 0 |
| `CefMainArgs@@` | `0x6b5e78` | 1 | `0x46cab0` | ?$CefStructBase@UCefMainArgsTraits@@@@ → _cef_main_args_t@@ | 0 |
| `CefRenderProcessHandler@@` | `0x6bb690` | 11 | `0x4b1ee0` | CefBase@@ | 0 |
| `CefRequestHandler@@` | `0x6bb748` | 15 | `0x4b1e50` | CefBase@@ | 0 |
| `CefWindowInfo@@` | `0x6bb660` | 1 | `0x4b1a60` | ?$CefStructBase@UCefWindowInfoTraits@@@@ → _cef_window_info_t@@ | 1 |

### 4.2 渲染对象（B 类，21–23 槽，13）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CBaseObject@@` | `0x6b8908` | 21 | `0x48e130` | — | 3 |
| `CBitmapObject@@` | `0x6b9994` | 21 | `0x496600` | CBaseObject@@ | 3 |
| `CBoxObject@@` | `0x6b9160` | 21 | `0x494030` | CBaseObject@@ | 3 |
| `CCanvasObject@@` | `0x6ba940` | 21 | `0x4a5700` | CBaseObject@@ | 2 |
| `CContainerObject@@` | `0x6b90c8` | 21 | `0x48e130` | CBaseObject@@ | 2 |
| `CEffectObject@@` | `0x6baeb8` | 21 | `0x4a9910` | CBaseObject@@ | 2 |
| `CGifObject@@` | `0x6b99f4` | 21 | `0x4968d0` | CBaseObject@@ | 4 |
| `CImagesObject@@` | `0x6b94d4` | 21 | `0x4953d0` | CBaseObject@@ | 3 |
| `CQRCodeObject@@` | `0x6bb004` | 21 | `0x4aa130` | CBitmapObject@@ → CBaseObject@@ | 4 |
| `CSpineObject@@` | `0x6baad0` | 23 | `0x4a79a0` | CBaseObject@@ | 3 |
| `CSpriteObject@@` | `0x6b7f70` | 23 | `0x484110` | CBaseObject@@ | 3 |
| `CStretchImagesObject@@` | `0x6b952c` | 21 | `0x4953d0` | CImagesObject@@ → CBaseObject@@ | 1 |
| `CStretchSpriteObject@@` | `0x6b7fd0` | 23 | `0x484110` | CSpriteObject@@ → CBaseObject@@ | 1 |

### 4.3 地图、行走与精灵资源（18）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CCoverSort@@` | `0x6ba358` | 4 | `0x49fcc0` | CRes@Common@@ | 2 |
| `CCustomMapObject@@` | `0x6b9b30` | 21 | `0x497320` | CBaseObject@@ | 4 |
| `CMapAddonBitmapObject@@` | `0x6bb0a4` | 21 | `0x4aad80` | CBitmapObject@@ → CBaseObject@@ | 2 |
| `CMapAddonObject@@` | `0x6ba7dc` | 21 | `0x4a4c60` | CImagesObject@@ → CBaseObject@@ | 2 |
| `CMapFileHeader@@` | `0x6b85f4` | 1 | `0x48a920` | — | 2 |
| `CMapHeroObject@@` | `0x6ba538` | 23 | `0x4a1380` | CMapWalkerObject@@ → CWalkerObject@@ → CBaseObject@@ | 3 |
| `CMapImagesObject@@` | `0x6b9584` | 21 | `0x4953d0` | CImagesObject@@ → CBaseObject@@ | 1 |
| `CMapMask@@` | `0x6bbfbc` | 10 | `0x4b98f0` | CGrapObject@Graphics@@ | 2 |
| `CMapMaskRes@@` | `0x6bbfa8` | 4 | `0x4c3310` | CRes@Common@@ | 4 |
| `CMapObject@@` | `0x6b85fc` | 21 | `0x48a950` | CBaseObject@@ | 2 |
| `CMapOccupyRes@@` | `0x6ba7c8` | 4 | `0x4a4c90` | CRes@Common@@ | 4 |
| `CMapSpaceObject@@` | `0x6ba834` | 21 | `0x4a4d10` | CBaseObject@@ | 4 |
| `CMapSpriteObject@@` | `0x6b8030` | 23 | `0x484110` | CSpriteObject@@ → CBaseObject@@ | 1 |
| `CMapWalkerMaskObject@@` | `0x6ba440` | 21 | `0x49fcf0` | CBaseObject@@ | 4 |
| `CMapWalkerObject@@` | `0x6ba3e0` | 23 | `0x49fd70` | CWalkerObject@@ → CBaseObject@@ | 2 |
| `CPathFind@@` | `0x6bbf24` | 9 | `0x4bab70` | — | 2 |
| `CSpriteRes@@` | `0x6b7f5c` | 4 | `0x4840e0` | CRes@Common@@ | 2 |
| `CWalkerObject@@` | `0x6ba380` | 23 | `0x49fda0` | CBaseObject@@ | 2 |
| `CWalkerRes@@` | `0x6ba36c` | 4 | `0x49fdd0` | CSpriteRes@@ → CRes@Common@@ | 4 |

### 4.4 图形资源（Graphics，31）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `?$_Ref_count@VCPngRes@Graphics@@@std@@` | `0x799408` | 4 | `0x6361b0` | _Ref_count_base@std@@ | 1 |
| `?$_Ref_count_obj@VCPngRes@Graphics@@@std@@` | `0x6baf38` | 4 | `0x4a9ac0` | _Ref_count_base@std@@ | 1 |
| `CBitmap@Graphics@@` | `0x797914` | 7 | `0x61cce0` | CBitmapBase@Graphics@@ → CGrapObject@Graphics@@ | 5 |
| `CBitmapBase@Graphics@@` | `0x7978f4` | 7 | `0x61cd80` | CGrapObject@Graphics@@ | 1 |
| `CBitmapForRestore@Graphics@@` | `0x797934` | 7 | `0x61cce0` | CBitmap@Graphics@@ → CBitmapBase@Graphics@@ → CGrapObject@Graphics@@ | 1 |
| `CBitmapRes@Graphics@@` | `0x799154` | 4 | `0x62b5b0` | CRes@Common@@ | 6 |
| `CBitmaps@Graphics@@` | `0x7992f0` | 7 | `0x633200` | CBitmapBase@Graphics@@ → CGrapObject@Graphics@@ | 3 |
| `CBitmapsRes@Graphics@@` | `0x79db04` | 4 | `0x63c180` | CRes@Common@@ | 4 |
| `CBox@Graphics@@` | `0x79925c` | 7 | `0x62f560` | CGrapObject@Graphics@@ | 4 |
| `CGrapObject@Graphics@@` | `0x79923c` | 7 | `0x62f230` | — | 3 |
| `CHsvPalettePro@Graphics@@` | `0x799184` | 1 | `0x62b730` | CPaletteOp@Graphics@@ | 1 |
| `CImages@Graphics@@` | `0x799194` | 13 | `0x62e6c0` | CGrapObject@Graphics@@ | 5 |
| `CImagesRes@Graphics@@` | `0x7990b8` | 4 | `0x62a890` | CRes@Common@@ | 3 |
| `CMaskBitmap@Graphics@@` | `0x6b8678` | 7 | `0x48c610` | CBitmap@Graphics@@ → CBitmapBase@Graphics@@ → CGrapObject@Graphics@@ | 7 |
| `CPaletteGrey@Graphics@@` | `0x79917c` | 1 | `0x62b710` | CPaletteOp@Graphics@@ | 1 |
| `CPaletteLight@Graphics@@` | `0x79916c` | 1 | `0x62b6a0` | CPaletteOp@Graphics@@ | 1 |
| `CPaletteOp@Graphics@@` | `—` | 0 | `—` | — | 0 |
| `CPalettePro@Graphics@@` | `0x79918c` | 1 | `0x62b760` | CPaletteOp@Graphics@@ | 2 |
| `CPaletteSet@Graphics@@` | `0x799174` | 1 | `0x62b6d0` | CPaletteOp@Graphics@@ | 1 |
| `CPreloadBitmapRes@Graphics@@` | `0x7993f0` | 2 | `0x635fc0` | CPreloadRes@Graphics@@ | 2 |
| `CPreloadPngRes@Graphics@@` | `0x7993fc` | 2 | `0x635ff0` | CPreloadRes@Graphics@@ | 2 |
| `CPreloadRes@Graphics@@` | `0x7993e4` | 2 | `0x636020` | — | 5 |
| `CScreen@Graphics@@` | `0x797250` | 11 | `0x613660` | — | 3 |
| `CScreenDDraw@Graphics@@` | `0x7975d4` | 11 | `0x614880` | CScreen@Graphics@@ | 2 |
| `CScreenGDI@Graphics@@` | `0x6b2744` | 11 | `0x459320` | CScreen@Graphics@@ | 3 |
| `CSpine@Graphics@@` | `0x79938c` | 1 | `0x635080` | — | 2 |
| `CStretchBitmap@Graphics@@` | `0x7990e0` | 7 | `0x62a830` | CMaskBitmap@Graphics@@ → CBitmap@Graphics@@ → CBitmapBase@Graphics@@ → CGrapObject@Graphics@@ | 1 |
| `CStretchImages@Graphics@@` | `0x7991cc` | 13 | `0x62e760` | CImages@Graphics@@ → CGrapObject@Graphics@@ | 3 |
| `CStretchImagesRes@Graphics@@` | `0x7990cc` | 4 | `0x62a8c0` | CRes@Common@@ | 3 |
| `Configuration@Graphics@@` | `0x798390` | 1 | `0x6234e0` | — | 3 |
| `GLView@Graphics@@` | `0x798544` | 1 | `0x623c10` | — | 3 |

### 4.5 公共资源 / 计时 / 日志（Common，7）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CCache@Common@@` | `0x797144` | 1 | `0x60cf30` | — | 2 |
| `CFrameNode@TimeLog@Common@@` | `0x6b14f8` | 1 | `0x44cb30` | — | 3 |
| `CLogFile@Common@@` | `0x6b14f0` | 1 | `0x44cb90` | — | 2 |
| `CPalProjectRes@@` | `0x6bc07c` | 4 | `0x4c4ed0` | CRes@Common@@ | 4 |
| `CRes@Common@@` | `0x7971dc` | 4 | `0x612470` | — | 5 |
| `CResWithThreadLoad@Common@@` | `0x7971f0` | 7 | `0x6124a0` | CRes@Common@@ | 3 |
| `CShadeObject@@` | `0x6bbf74` | 7 | `0x4c2450` | CBitmap@Graphics@@ → CBitmapBase@Graphics@@ → CGrapObject@Graphics@@ | 3 |
| `CShare@Common@@` | `0x7971d4` | 1 | `0x612520` | — | 3 |
| `CTimer@Common@@` | `0x6b2170` | 3 | `0x454550` | — | 1 |

### 4.6 网络 / 命令 / 密码器（18）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CClientCommand@@` | `0x6bb114` | 1 | `0x4ab000` | — | 3 |
| `CDecryptor@@` | `0x6bbff4` | 1 | `0x4c3a50` | — | 3 |
| `CDownloadObject@Network@@` | `0x6b5460` | 2 | `0x46a150` | CHttpObject@Network@@ → CRefBase@Network@@ | 2 |
| `CEncryptor@@` | `0x6bbfec` | 1 | `0x4c3aa0` | — | 2 |
| `CFFMClient@@` | `0x6b89b4` | 1 | `0x48ec90` | — | 4 |
| `CFFMServer@@` | `0x6b89ac` | 1 | `0x48ecc0` | — | 4 |
| `CHttpObject@Network@@` | `0x6bb348` | 2 | `0x4ad6b0` | CRefBase@Network@@ | 2 |
| `CLZWDecompress@@` | `0x6bb184` | 3 | `0x4c5e00` | — | 2 |
| `CNet@@` | `0x6bb330` | 1 | `0x4ac710` | — | 4 |
| `CObjectCCommand@@` | `0x6bbea8` | 3 | `0x4b7dc0` | CObjectCommand@@ | 1 |
| `CObjectCommand@@` | `0x6bbe98` | 3 | `0x4b7e40` | — | 6 |
| `CObjectPyCommand@@` | `0x6bbeb8` | 3 | `0x4b7e40` | CObjectCommand@@ | 1 |
| `CPreloadObject@@` | `0x6bbe4c` | 2 | `0x4b54e0` | — | 4 |
| `CRefBase@@` | `0x6bbae4` | 1 | `0x4b4310` | — | 3 |
| `CRefBase@Network@@` | `0x6bb340` | 1 | `0x4ad6e0` | — | 3 |
| `CServerCommand@@` | `0x6bb11c` | 1 | `0x4ab050` | — | 3 |
| `CShareAgentListener@@` | `0x6bbad0` | 4 | `0x4b4340` | — | 2 |
| `ClientRenderAgent@@` | `0x6bbaec` | 1 | `0x4b4370` | CRefBase@@ → CShareAgentListener@@ | 2 |

### 4.7 场景切换特效（Switch，9）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CSwitch4Block@Switch@@` | `0x6b86b0` | 2 | `0x48c640` | CSwitch@Switch@@ | 2 |
| `CSwitch@Switch@@` | `0x6b8698` | 2 | `0x48c670` | — | 14 |
| `CSwitchBlind@Switch@@` | `0x6b86f8` | 2 | `0x48c670` | CSwitch@Switch@@ | 1 |
| `CSwitchCircle@Switch@@` | `0x6b86d4` | 2 | `0x48c670` | CSwitch@Switch@@ | 1 |
| `CSwitchFade@Switch@@` | `0x6b86a4` | 2 | `0x48c670` | CSwitch@Switch@@ | 1 |
| `CSwitchSector@Switch@@` | `0x6b86c8` | 2 | `0x48c670` | CSwitch@Switch@@ | 1 |
| `CSwitchSnow@Switch@@` | `0x6b86bc` | 2 | `0x48c670` | CSwitch@Switch@@ | 1 |
| `CSwitchString@Switch@@` | `0x6b86e0` | 2 | `0x48c6a0` | CSwitch@Switch@@ | 2 |
| `CSwitchTransString@Switch@@` | `0x6b86ec` | 2 | `0x48c6d0` | CSwitch@Switch@@ | 2 |

### 4.8 音频 / 诊断（4）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CExceptionReport@Debug@Common@@` | `0x797210` | 3 | `0x6125f0` | — | 3 |
| `CMxBugTaceShell@Dmp@@` | `0x6b7c9c` | 3 | `0x47ff20` | CExceptionReport@Debug@Common@@ | 0 |
| `CWaveRes@Sound@@` | `0x7bce2c` | 4 | `0x406230` | CRes@Common@@ | 2 |
| `CWaves@@` | `0x7bce60` | 1 | `0x408570` | — | 2 |

### 4.9 二维码（zxing，17）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `ZXBitArray@@` | `0x7bdaac` | 1 | `0x413e20` | ZXObject@@ | 8 |
| `ZXBitMatrix@@` | `0x7bda7c` | 1 | `0x411380` | ZXObject@@ | 2 |
| `ZXByteArray@@` | `0x7bdabc` | 1 | `0x4145e0` | ZXObject@@ | 3 |
| `ZXByteMatrix@@` | `0x7bda8c` | 1 | `0x411550` | ZXObject@@ | 2 |
| `ZXEncodeHints@@` | `0x7bda60` | 1 | `0x40c600` | ZXObject@@ | 1 |
| `ZXGenericGF@@` | `0x7bdaa4` | 1 | `0x4139c0` | ZXObject@@ | 2 |
| `ZXGenericGFPoly@@` | `0x7bdacc` | 1 | `0x40c600` | ZXObject@@ | 9 |
| `ZXIntArray@@` | `0x7bda94` | 1 | `0x4132d0` | ZXObject@@ | 53 |
| `ZXObject@@` | `0x7bda84` | 1 | `0x40c600` | — | 12 |
| `ZXQRCode@@` | `0x7bdab4` | 1 | `0x40c600` | ZXObject@@ | 1 |
| `ZXQRCodeECB@@` | `0x7bda48` | 1 | `0x40c600` | ZXObject@@ | 106 |
| `ZXQRCodeECBlocks@@` | `0x7bda50` | 1 | `0x4109d0` | ZXObject@@ | 3 |
| `ZXQRCodeErrorCorrectionLevel@@` | `0x7bda40` | 1 | `0x40c600` | ZXObject@@ | 2 |
| `ZXQRCodeMode@@` | `0x7bda9c` | 1 | `0x413400` | ZXObject@@ | 5 |
| `ZXQRCodeVersion@@` | `0x7bda58` | 1 | `0x40c940` | ZXObject@@ | 2 |
| `ZXQRCodeWriter@@` | `0x7bda38` | 1 | `0x40c600` | ZXObject@@ | 1 |
| `ZXReedSolomonEncoder@@` | `0x7bdac4` | 1 | `0x415050` | ZXObject@@ | 2 |

### 4.10 GIF（duoyi_gif，6）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `CGifInput@duoyi_gif@@` | `0x79dfb0` | 2 | `0x640c50` | GifStreamInput@duoyi_gif@@ | 2 |
| `CGifMemBitmap256@duoyi_gif@@` | `0x79dfbc` | 19 | `0x6428a0` | CGifMemBitmap@duoyi_gif@@ | 2 |
| `CGifMemBitmap@duoyi_gif@@` | `—` | 0 | `—` | — | 0 |
| `CGifOutput@duoyi_gif@@` | `0x79dfa8` | 1 | `0x640b00` | GifStreamOutput@duoyi_gif@@ | 2 |
| `GifStreamInput@duoyi_gif@@` | `—` | 0 | `—` | — | 0 |
| `GifStreamOutput@duoyi_gif@@` | `—` | 0 | `—` | — | 0 |

### 4.11 fmt / 运行时（11）

| 类 | 虚表 | 槽 | 虚析构 | 继承自上 | vfptr 写入点 |
|---|---|---:|---|---|---:|
| `?$BasicMemoryWriter@DV?$allocator@D@std@@@fmt@@` | `0x6b1f84` | 1 | `0x450ef0` | ?$BasicWriter@D@fmt@@ | 0 |
| `?$BasicWriter@D@fmt@@` | `0x6b1f7c` | 1 | `0x450f40` | — | 3 |
| `?$Buffer@D@fmt@@` | `0x6b1f40` | 2 | `0x5c08f8` | — | 3 |
| `?$Buffer@_W@fmt@@` | `0x6b1f28` | 2 | `0x5c08f8` | — | 3 |
| `?$MemoryBuffer@D$0BPE@V?$allocator@D@std@@@internal@fmt@@` | `0x6b1f4c` | 2 | `0x452670` | ?$allocator@D@std@@ → ?$_Allocator_base@D@std@@ → ?$Buffer@D@fmt@@ | 3 |
| `?$MemoryBuffer@_W$0BPE@V?$allocator@_W@std@@@internal@fmt@@` | `0x6b1f34` | 2 | `0x4526f0` | ?$allocator@_W@std@@ → ?$_Allocator_base@_W@std@@ → ?$Buffer@_W@fmt@@ | 3 |
| `FormatError@fmt@@` | `0x6b1f1c` | 2 | `0x451050` | runtime_error@std@@ → exception@std@@ | 1 |
| `RuntimeError@internal@fmt@@` | `0x6b1f58` | 2 | `0x451050` | runtime_error@std@@ → exception@std@@ | 1 |
| `SystemError@fmt@@` | `0x6b1f64` | 2 | `0x451050` | RuntimeError@internal@fmt@@ → runtime_error@std@@ → exception@std@@ | 2 |
| `WindowsError@fmt@@` | `0x6b1f70` | 2 | `0x451050` | SystemError@fmt@@ → RuntimeError@internal@fmt@@ → runtime_error@std@@ → exception@std@@ | 2 |
| `type_info@@` | `0x77cb64` | 2 | `0x5c1b90` | — | 1 |

## 5. 与现有 notes 的坐标对照

把 `notes/` 里已经记录过的原生地址拿去查这张表，能落在"虚表槽位"或"写 vfptr 位置"上的
只有下面三条；其余的要么是自由函数、要么在 `_dyprot` 段里，本表覆盖不到——**查不到不代表
旧地址有错**，只说明它不是虚函数入口。

| 现有笔记里的地址 | 本表给出的归属 | 关系 |
|---|---|---|
| `0x4c5e40`（`native_tcp_channel.md`：LZW 解压） | `CLZWDecompress` 槽 1 | 互证：两条独立路径（原生指令模拟 / RTTI）指向同一函数 |
| `0x4c5d50`（同一笔记：LZW 初始化） | `CLZWDecompress` 写 vfptr 的位置（`0x4c5d57` 处 `c7 06`） | 说明它就是构造函数邻域 |
| `0x4aadb0`（同一笔记：上行构造/终结） | `CClientCommand` 写 vfptr 的位置 | 同上 |

`CNet`（虚表 `0x6bb330`，1 槽）、`CEncryptor`（`0x6bbfec`，1 槽）、`CDecryptor`
（`0x6bbff4`，1 槽）都只有虚析构，所以笔记里那些密码器地址不会出现在虚表里；反过来说，
**这三个类的位置现在有了确切的类名归属**，后续再看到 `0x4ac7xx`/`0x4c3axx` 一带的代码，
可以直接按"`CNet` 的成员函数"来读，而不是"某个网络函数"。

## 6. 延伸发现：原生→脚本的回调名表就在明文 `.rdata` 里（未结案）

`notes/client_binary_reversibility.md` §2 有一条关键负面结论：
"`CCombPanel`、`FONT_EDIT`、`PyArg_ParseTuple` 明文命中都是 0，所以别拿 strings 的 0 命中
当证据"。这条**仍然成立**，但它说的只是"那些名字不在明文里"；本轮发现了反例方向——

在 `0x6bb120` 起的一段 `.rdata`（紧邻 `CClientCommand` / `CServerCommand` 的虚表之后），
明文躺着这样一串东西（原字节，`\0` 分隔）：

```text
"decompress error"  ""  "(i)"  "OnServerCmd"  "(i)"  "i"  ""  ""
"OnSpecialServerCmd"  ""  "()"  ""  "OnError"  ""  "()"  ""  "OnConnectFail"  …
```

即**「签名串 + 方法名」成对出现**的回调表。配套的调用点是可以指认的：

- `0x4ab7b2` 处 `call 0x4576b0`，压栈顺序（从右到左）是
  `对象 → "OnServerCmd"(0x6bb138) → ""(0x6bb131) → 0 → "(i)"(0x6bb134) → 参数`；
- `0x4576b0` 本身是变参函数（函数体里有 `lea 0xc(%ebp),%eax` 取可变参数区）；取不到方法时
  走 `0x4576fd` 那条分支，把可变参数区与 **`0x6b2448 = "Can't get method:{}"`** 一起交给
  `0x457f40` 报错。

⇒ 这一段是**"原生按名字调用脚本方法"的桥**，方法名、签名都在明文里。
已知可 xref 的名字（名字串地址 → `.text` 引用点）：

| 名字 | 名字串地址 | 签名串 | 代码引用点 |
|---|---|---|---|
| `OnServerCmd` | `0x6bb138` / `0x6bb1c8` | `(i)` / `(s)` | `0x4ab7ac`、`0x4ab8e3`、`0x4ab943` / `0x4ac052` |
| `OnSpecialServerCmd` | `0x6bb14c` | `(i)` | `0x4ab7f6` |
| `OnConnectFail` | `0x6bb170` | `()` | `0x4abad4` |
| `OnConnected` | `0x6bb1dc` | `(i)` | `0x4ac5bc` |
| `OnError` | `0x6bb1f8` | `()` | `0x4ac5e1` |
| `KeepAlive` | `0x6bba00` | `(sI)` | `0x40f185`、`0x40f4a2`、`0x40f995` |
| `ProcessMessage` | `0x6b7cb8` | `()` | `0x480515` |
| `ShowWindow` / `MainStart` | `0x6b1264` / `0x6b12b4` | `(s)` / `(i)` | `0x44b5ea` / `0x44b65e` |

这和 2026-10-09 的旧交接（`docs/archive/work-20261010/HANDOVER-20261010.md`
「`0x2714` → `OnServerCmd(int)` 桥接」）方向一致，但现在多了两样东西：
**桥的实现地址（`0x4576b0`）**和**名字/签名串的物理位置**。

想扩成一张完整的"原生→脚本回调清单"还差一步：把全 `.rdata` 里"名字 + 相邻签名串"
的候选（本次粗筛 260 条）逐条和代码引用点核对。粗筛会混进嵌入式 CPython 自己的
方法名表（`iteritems`、`__getstate__`、`struct_time` 之类），
**候选 ≠ 结论**，所以本文只把已核过 xref 的 8 条列出来，其余留给下一轮。
顺带一提：`0x6b4b88`/`0x6b4b90`/`0x6b4b9c` 处明文有 `C_net` / `CNetClient` /
`CServerCommand` 三个名字，与 `notes/` 里 `C_sys`/`C_net` 原生模块的说法对得上，
同样值得下一轮一起核。

## 7. 复现与回归

```bash
# 摘要（默认行为）；完整 JSON / Markdown 需要显式给路径
python3 tools/data-parser/mxmain_rtti.py mxmain.dll --limit 20
python3 tools/data-parser/mxmain_rtti.py mxmain.dll --json /tmp/rtti.json --md /tmp/rtti.md

# 回归（14 项：7 项自建 PE + 7 项真档断言）
python3 -m unittest tools/data-parser/test_mxmain_rtti.py
```

回归里钉住的真档期望值：SHA-256 与锁定摘要一致、352/305/305、继承链 0 失败、
`failure@ios_base` 五层链、`CMainWnd` 三层链、`CCommonWnd` 单槽 `0x44b2a0`、
`CLZWDecompress` 含 `0x4c5e40`、`invalid_argument@std` 的槽 0 是奇数地址 `0x5c6085`。
自建 PE 那 7 项锁的是结构假设：TD/COL/虚表定位、槽尾字串 0x696969 必须被挡、
BCA[0] 是自身、`movl $虚表,(%esi)` 的写入点、以及"输入文件全程不被改"。

## 8. 明确边界（别把这张表当成立项）

- **没有方法名**。虚表给的是地址序列；要名字，只能走 §6 的回调名表（原生→脚本方向）、
  脚本侧绑定（`interface` / `C_sys` 的 Python 对象）或人工反汇编。
- **没有成员变量**。虚析构函数里能读到少量偏移与释放的指针（例如 `CCommonWnd` 的析构
  会释放 `+0x18`、`+0x1a4`），但那只是"这里有个对象/指针"，不是字段名也不是完整布局。
- **54% 的镜像没进这张表**。`_dyprot0/1`（5.2 MB，熵 7.85/7.72）里如果还有类，明文根本
  看不到；本文的 352 个是**明文可见的全部**，不是客户端的全部。
- **`mdisp` 只作参考**。`CMainWnd → CCommonWnd → CGameWnd` 链上 `CGameWnd` 的
  `mdisp=8`（其余多为 0），说明它作为子对象落在 +8；这与"单继承基类在 0"的直觉不符，
  本文只如实记录，不解释成因，也不据此推断成员布局。
- **地址是首选基址下的**。`mxmain.dll` 以 DLL 形态加载时若被重定位，这些 VA 不能直接用；
  做运行期钩子必须先取模块基址。
- **Windows 未验**。本轮所有结论都来自 Linux 沙箱里的静态解析（纯标准库、不执行镜像），
  没有在 Windows 实机上做任何运行期对照。

## 9. 下一步（按性价比）

1. 把 §6 的候选名表逐条核 xref，产出"原生→脚本回调清单"（半天到一天，纯静态）；
   这份清单能直接回答"脚本能不能收到某个回调"。
2. 用 `CBaseObject` 家族的 21–23 槽虚表反查渲染循环调用点，把"对象生命周期 / draw 顺序"
   变成可读流程（对应地图编辑器里 `CMapHeroObject` 等行为）。
3. 需要真机时再上 Windows：用 `mxmain_rtti.py --json` 的地址做断点表，
   把 §5 里那三条互证升级成"运行期一致"。
