# 外部材料：Google Drive 上的现成包（interface.fls 分卷 / 全量反编译语料）

> **本文只管一件事**：真 `.dlg` 语料和反编译语料**去哪儿拿、怎么解开、怎么校验、哪些边界**。
> 「要不要自己建反编译语料、怎么建」看 [`DECOMPILE_CORPUS.md`](DECOMPILE_CORPUS.md)——能直接取现成的就别重跑几小时。

## 0. 取用规则（先看这条）

1. **只用用户指定的两个目录**：`interface1019` 与 `MXSJ_CORPUS`（都在 My Drive 根下）。
   根目录里散落的同名整包/清单**不是**取用来源，别拿它替代目录内容。
2. **目录是活的**：里面的文件会随开发进度更新（换包、增删卷、重打包）。
   所以——
   - **每次取用先列目录**，按当时实际看到的文件取，别照着本文表格硬编码文件名；
   - 本文 `§1` 的 id / 大小 / SHA 只是 **2026-10-20 的快照**，只用于「当时是什么样」；
   - 目录内容与本文不一致时，**以目录为准**，并回写本文 `§5` 的变更记录（见 §5）。
3. **字节级校验以同批清单为准**：语料带官方 `..._ARCHIVES.sha256`；清单被换代时同样以新的为准，
   不要把旧 SHA 当成「文件被篡改」的证据——先看是不是换了基线。
4. 下载/解压产物**一律在仓库外**，不入库（红线 §4-8）。

`§1` 以下凡是写死的数字都受这条约束：**快照，不是契约**。

## 1. 两个目录（2026-10-20 快照）

| 目录 | Drive folder id | 当时改时间 | 当时内容 |
|---|---|---|---|
| `interface1019` | `1Xz6eXwbyIm8HrXOXL_sJALYYZovAr8Zs` | 2026-10-19T03:37Z | `interface.fls` 的**分卷**，4 个文件 |
| `MXSJ_CORPUS` | `1zT36d47NsosEjfns4jxJIPlsi4B6AGZN` | 2026-10-16T10:47Z | 全量**反编译语料**，10 个独立 ZIP |

### 1.1 `interface1019`（界面布局与图片的真包）

分卷是**一个 zip 被切开**：`interface.zip` 是最后一段，`interface.z01/z02/z03` 是前三段。

| 文件（当时） | id | 大小（B） |
|---|---|---:|
| `interface.z01` | `1H2qLiOMhwgp58pl9aDFv9A9m-IEn77K7` | 94,371,840 |
| `interface.z02` | `1Dy48zoe09ffP_JiyTFsimYQqz-Ym0PTD` | 94,371,840 |
| `interface.z03` | `1Om_nYzEiJM0o8T9Fu_DmYDUXmzzbzkyS` | 94,371,840 |
| `interface.zip` | `1rL0IV46QiL4ysc4bz4ZCDLMmLfkXb7C7` | 77,782,093 |
| 合计 | — | 360,897,613 |

`interface.fls` 里是布局 `.dlg` 与界面图片——仓库里**没有**这个包（`data/` 只有
script/data/effect/skill/skill2/magicres5/passive），所以「真布局往返」「真切片/真按钮皮肤」
「真图渲染」这些结论只能用它验。

> 分卷是「按当时的打包结果」切的。若目录里换成整包或重新分卷，**卷号/文件名会变**，
> 解压前先 `7z l` 看是哪一种。

### 1.2 `MXSJ_CORPUS`（`data/script.fls` 的反编译语料）

当时基线 **`8212b26` / 2026-10-15**，10 卷**全部是独立 ZIP**（索引明确写「不做二进制拼接」），
合计 **152,769,019 B**（与 `DELIVERY_INDEX.md` 记的总压缩大小、与目录里 10 个文件大小求和三者一致）。

| 卷（当时） | id | 大小（B） | SHA-256（同批清单） |
|---|---|---:|---|
| part01 | `1XctBMWekB2yfDGnfy2KUQgrIxjCIEfYm` | 23,312,078 | `95ccc52384b8a196d7fa75cf0e0dc4047d3670fd3f13aa939324e004101e7e08` |
| part02 | `1iSlzbF5rdyxhVK2lMUX92TvhFBnznYZi` | 18,641,599 | `ec4991d1742627607e2e4b83b73592bd787a48a86968ebd091acfa29bcebd670` |
| part03 | `1BU1GifCl9zqM0-2AdwB0b1HFBwA6CliY` | 19,508,725 | `75a0f40c15b1b3e9591211221a6b30324b5adb3b7a652ade0582251e1d6de352` |
| part04 | `1xlKpxNkYrsRzEHmQ1L_mcnp9dZOR5z2n` | 22,436,061 | `0bb5a268eb2bb621e9cc924f3661ed5253615e1a6520e23d5ec874aabaeadd7b` |
| part05 | `1qslRsfVHqRWfxC1wo_VRyX8jc3lLOMoa` | 22,209,061 | `1a6c4726f3ce704ae0147e1dcdf42e0c07d6ec577a65f6b8656de8902be43617` |
| part06 | `1fzikabz9SDW8CqXrblfo0h6uBuDweDnB` | 19,740,225 | `478c0fad40468cc4872cb6e5a044de65b5702a51cfac8115e98340d1e0a69e06` |
| part07 | `1huI7SFc0PYRy2CrK1xFcDmgGbaBBR3iD` | 14,072,561 | `6143ca10215d054cfd3fe70fa924be46ad025a3daa81ae0ff7ff69531b3837b1` |
| part08 | `1M7NTe-jcbUd5zo1lxTX0abxEDZ_JdFiD` | 4,708,874 | `054c866cc1eade2634d6ad9ffe9cc2c7bd8b35431f0fcb0f5bdab4b2bd5c24ca` |
| part09 | `19vafs3m5Pr1P3ekOo4PUDKl7aNcPFV3H` | 5,140,639 | `7fb13b824f987fe6ccf2d6bef9f4f748543005d36c3b0eca4fc0cdd12b2256ab` |
| part10 | `1-9B4ww1GPpzyu9d2sBNzSrF-shVJ58n5` | 2,999,196 | `fdea0dbc34b2bb2985749a245273c4030db0600f3c830ac4b9aa4f9560a512c7` |

同批签发的说明文件（正文出处，随换代一起换）：`..._DELIVERY_INDEX.md`（统计口径、卷表、
编辑器对接口）、`..._ARCHIVES.sha256`（上表 SHA 的出处）、`..._upload_receipts.json`、
`..._archive-verification.json`；另有小体积先行样例包与失败 entry 82 补充包。**按需取，不是每次都全下。**

**语料是什么/不是什么**（照 `DELIVERY_INDEX.md`，别外推）：是 5,002 条 entry 的**反编译候选**；
`entry 1288` 只保留 `excluded_by_policy`；「完整输出标记」是启发式，不是语义正确率；
≠ 可回编译源码（要回编必须走 CPython 2.5 真编译那条路）。**不含**原始 `script.fls`/`interface.fls`、
不含参数表。

## 2. 该用哪个

| 要回答的问题 | 用 |
|---|---|
| 真 `.dlg` 全量往返、真实切片/按钮状态、真图渲染、游戏内布局 | `interface1019` |
| 谁加载哪个布局、按钮皮肤/消息号 | 仓库内 `tools/script_link/build_script_index.py` 产物（已入库，别下载语料） |
| 「符号 X 在全档有没有定义者」、语义级全档检索 | `MXSJ_CORPUS` |
| 只查某一条 entry 的代码 | `tools/decompiler/recover_entries.py --entries N`（秒级，见 `DECOMPILE_CORPUS.md` §2） |

## 3. 取用（先列目录，再动手；产物在仓库外）

```sh
OUT=/home/user/ext && mkdir -p "$OUT"      # 仓库外，别放进仓库
```

**第 0 步（每次都做）**：先看目录现在有什么——文件名、数量、总大小按当时的实际值，
和 §1 不同就以目录为准（并在 §5 记一笔）：

```sh
# 有 Drive 连接器时直接列目录；否则用 rclone/gcloud 等本地工具列同一目录
# 关心的只有：文件数、文件名、字节数、修改时间
```

**interface.fls（分卷）**

```sh
# 4 个文件下载到同一目录后，解最后一个 .zip；7z/unzip 会按 .z01→.z02→.z03 自动续卷
7z x -o"$OUT/mxsj" interface.zip            # 或： unzip interface.zip -d "$OUT/mxsj"
find "$OUT/mxsj" -maxdepth 3 -iname 'interface.fls'
```

- `.z01/.z02/.z03` **不能**单独解压，也**不要** `cat` 拼接（它们本来就是同一个 zip 的卷）；
- **2026-10-20 实测**：`interface.zip` 带 **8 字节前缀**（非标准 zip 头），且各卷内的
  偏移是**卷内相对偏移**——所以 `zipfile` / `unzip` / `cat` 后喂 `zipfile` 三种都失败，
  报「找不到中央目录」。当时跑通的办法是：按 EOCD 找中央目录 → 对目标条目读 local
  header（绝对偏移 4 起）→ `4+30+nlen+elen` 处取 `csize` 字节，用
  `zlib.decompressobj(-15)` 流式 inflate，边写边验 CRC32。**换卷/换整包前先看有没有这
  8 字节前缀**，别默认是标准 zip；
- 先看内容：`7z l interface.zip`（同样需要各卷在同目录）；
- 若目录换成了整包（单个 `.zip`），直接解它，不要去找 `.z0x`。

**反编译语料（10 个独立 ZIP，不是拼接包）**

```sh
cd "$OUT"
sha256sum -c MXSJ_CORPUS_*_ARCHIVES.sha256     # 用同批清单；换了基线就换清单
mkdir -p corpus
for z in MXSJ_CORPUS_*_part*.zip; do
  unzip -q -o "$z" -d corpus                    # 所有卷解到同一个空目录
done
```

- 解压后再跑产物自校验：`corpus/SHA256SUMS`（索引记录归档后 185,048 个文件逐字节校验通过）；
- 入口：`full/manifest.audited.jsonl`（主键 `(archive_sha256, entry_index)`，不是文件名），
  报告在 `reports/`，版本/工具指纹在 `versions.json`、`external-tools.sha256`。

**把语料指给编辑器/回归用例**

```sh
export MXSJ_DLG_CORPUS="$OUT/mxsj/interface"   # 支持 ':' 分隔多目录；数量按实际上报
(cd ui_editor && PYTHONPATH=src python3 -m unittest tests.test_codec)
```

## 4. 边界（违反就先停下来问）

1. **不入库**：分卷、解压出的 `.dlg`、反编译语料都不进 git（红线 §4-8）；仓库只留本文与命令。
2. **不覆盖原始包**：`data/script.fls`、`interface.fls`、密钥表一个字节都不动；编辑器一律「原包不动、另存新包」。
3. **不擅自动 Drive**：不加分享、不改权限、不删卷、不覆盖上传；目录归用户维护，我们只用**目录里当前存在**的文件。
4. **不拿根目录杂物替代目录**：整包副本、旧清单等只作参考，取用位置就是用户指定的两个目录。
5. **只读解析**：语料不执行、不 `eval`；`.dlg` 只当数据解析。
6. **未验不宣称**：真包已在 2026-10-20 全量跑过一次（见 §5.1 的实测数字与
   `docs/STATUS.md`）。**「切片与客户端像素级一致」仍未验**——那要进游戏比对，
   沙箱里只能证明「族形状/文件尺寸/解码结果」，不能证明渲染语义。

## 5. 目录变更记录（每次发现内容变了就加一行）

| 日期 | 目录 | 观察到什么 | 处理 |
|---|---|---|---|
| 2026-10-20 | `interface1019` | 4 文件：`interface.z01/z02/z03` 各 94,371,840 B + `interface.zip` 77,782,093 B | 记为快照；未下载 |
| 2026-10-20 | `MXSJ_CORPUS` | 10 卷独立 ZIP，合计 152,769,019 B，基线 `8212b26`/2026-10-15 | 记为快照；SHA 抄自同批清单；未下载 |
| 2026-10-20 | `interface1019` | 4 卷已下载并按 §3 的办法解开：`interface.fls` **614,482,967 B**，SHA-256 `3fb516a9…1fb124`，CRC `0x4fa12d0b` 与包内记录一致 | 用作真语料基线（§5.1） |

### 5.1 真包实测（2026-10-20，`interface1019` 当批内容）

| 项 | 实测值 |
|---|---|
| 分卷 | `interface.z01/z02/z03` 各 94,371,840 B + `interface.zip` 77,782,093 B（合计 360,897,613 B） |
| 解出 `interface.fls` | **614,482,967 B**、CRC32 `0x4fa12d0b`、SHA-256 `3fb516a961bfb32556af7a7d2761c703b70d194a16956535b18e7ab1571fb124`（3.7 s） |
| 包内条目 | **53,556** |
| 仓库 catalog 已知布局路径 | 2,903 条，包内命中 **2,708** |
| 解出 `.dlg` 明文 | **2,708** 篇（= 包内命中的全部；解析失败 **0**，往返失败 **0**） |
| `tests.test_codec`（`MXSJ_DLG_CORPUS` 指向这 2,708 篇） | **Ran 10 → OK**（全量往返 0 失败） |
| 目录型基路径 | **729 个唯一值 / 736 处引用**，全部探过子图名 |
| 拼名族实测分布（`dir_base.plan` 判决，729 个基路径全有归属） | 序号帧 423 / 九片 130 / 横三片 109 / 三态横片 `{n}l`+`{n}c`+`{n}r` 36 / 竖三片 22 / 单图 9 |
| 渲染解析 | 用真 `AssetResolver` 逐个取图：**729/729 解出**（切片 297、整图 432），0 失败、0 资源问题 |
| 图片格式 | 除了 PNG，还有 `I0`（4×4 角块等）与 **`I4`**（行内 2 字节 RGB565 真彩）；`I4` 已并入共享 `sprite_format` |

**另一个实测缺陷**：有 5 篇 `.dlg` 的**密文首字节正好是 `[`**（实为 4 字节循环
XOR，密钥如 `78 c7 ae 39`），旧实现「首字节是 `[` 就当明文」把它们原样返回，
于是解析报「找不到 UI_INFO」。现在改为「以 `[` 开头**且**头段几乎全可打印」
才算明文，这 5 篇按密钥还原后正文正常——这也是 2,697 → 2,708 的来源。

**拼名族的两个反直觉实测**（旧实现按反编译字面量写，真包上 0 命中）：

1. 九片的中列叫 `top/middle`、`middle/middle`、`bottom/middle`，**没有**平铺的
   `top.png`/`middle.png`/`bottom.png`；130 个九片基路径全部 9 块齐装。
2. 按钮的态是**文件名前缀**：整图族 `0/1/2/3.png`、切片族 `0l/0c/0r … `；
   态数实测 2～5。哪个序号是悬停/按下仍无实据（族里没有字段说明）。

下次真正取用时补：`interface.fls` 当时的 SHA/条目数、`MXSJ_DLG_CORPUS` 指向后
`test_codec` 实际篇数——**按当时的目录内容测，不套用本文旧表**。
