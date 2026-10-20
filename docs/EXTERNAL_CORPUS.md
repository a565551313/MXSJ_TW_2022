# 外部材料：Google Drive 上的现成包（interface.fls 分卷 / 全量反编译语料）

> **本文只管一件事**：真 `.dlg` 语料和反编译语料**去哪儿拿、怎么解开、怎么校验、哪些边界**。
> 「要不要自己建反编译语料、怎么建」看 [`DECOMPILE_CORPUS.md`](DECOMPILE_CORPUS.md)——能直接取现成的就别重跑几小时。
>
> **本轮取证口径**：2026-10-20 只读了 Drive 的元数据（目录/文件名/大小/修改时间/官方校验清单），
> **没有下载任何分卷、没有解压、没有跑语料用例**。本文出现的字节数与 SHA 都有来源；
> 没有来源的（例如 interface 分卷自身的 SHA-256）明确标「待实测」，不要拿别的数字冒充。

## 1. 两个目录（事实，2026-10-20 读自 Drive）

| 目录 | Drive folder id | 改时间 | 内容 |
|---|---|---|---|
| `interface1019`（My Drive 根下） | `1Xz6eXwbyIm8HrXOXL_sJALYYZovAr8Zs` | 2026-10-19T03:37Z | `interface.fls` 的**分卷 ZIP**，共 4 个文件 |
| `MXSJ_CORPUS`（My Drive 根下） | `1zT36d47NsosEjfns4jxJIPlsi4B6AGZN` | 2026-10-16T10:47Z | 全量**反编译语料**，10 个独立 ZIP |

### 1.1 `interface.fls`（界面布局与图片的真包）

分卷是**一个 zip 被切开**，`interface.zip` 是最后一段，`interface.z01/z02/z03` 是前三段：

| 文件 | id | 大小（B） |
|---|---|---:|
| `interface.z01` | `1H2qLiOMhwgp58pl9aDFv9A9m-IEn77K7` | 94,371,840 |
| `interface.z02` | `1Dy48zoe09ffP_JiyTFsimYQqz-Ym0PTD` | 94,371,840 |
| `interface.z03` | `1Om_nYzEiJM0o8T9Fu_DmYDUXmzzbzkyS` | 94,371,840 |
| `interface.zip` | `1rL0IV46QiL4ysc4bz4ZCDLMmLfkXb7C7` | 77,782,093 |
| 合计 | — | **360,897,613** |

My Drive 根还有一份整包 `interface1019.zip`（id `1hDLskWjCueEoJvoDDby87rRhuZynCTAs`，360,897,609 B，
2026-10-19T02:54Z）。它比分卷合计**小 4 字节**；两者是否同一份内容**未下载核对**，按用户说明以**分卷**为准。

`interface.fls` 里是 2,706+ 个 `.dlg` 布局与界面图片——仓库里**没有**这个包（`data/` 只有 script/data/effect/skill/skill2/magicres5/passive），
所以「真布局往返」「真切片/真按钮皮肤」「真图渲染」这些结论都只能用它验。

### 1.2 `MXSJ_CORPUS`（`data/script.fls` 的反编译语料）

固定基线 **`8212b26` / 2026-10-15**，10 卷**全部是独立 ZIP**（索引明确写「不做二进制拼接」），
合计 **152,769,019 B**（与 `DELIVERY_INDEX.md` 记的总压缩大小、与目录里 10 个文件大小求和三者一致）。

| 卷 | id | 大小（B） | SHA-256（官方清单） |
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

同目录/根目录的配套小文件（都在 My Drive 根，`0AM2SnEVIISYdUk9PVA` 下）：

- `MXSJ_CORPUS_8212b26_20261015_ARCHIVES.sha256`（`1FLksxEL5ZbXzH0LTz2U63wfjk0Keuve6`，1,060 B）——上表 SHA 的出处；
- `MXSJ_CORPUS_8212b26_20261015_DELIVERY_INDEX.md`（`1nIUskEGc1pkECGZIi3ZqUB8exmv8Zgrm`）——统计口径、十卷下载表、编辑器对接口；
- `..._upload_receipts.json`、`..._archive-verification.json`——上传回执与归档校验回执；
- 先行样例 `MXSJ_CORPUS_SAMPLE_8212b26_20261015.zip`（446,379 B）与双引擎失败 entry 82 补充包（58,020 B）。

**语料是什么/不是什么**（照 `DELIVERY_INDEX.md`，别外推）：是 5,002 条 entry 的**反编译候选**；
`entry 1288` 只保留 `excluded_by_policy`；「完整输出标记」是启发式，不是语义正确率；
≠ 可回编译源码（要回编必须走 CPython 2.5 真编译那条路）。**不含**原始 `script.fls`/`interface.fls`、不含参数表。

## 2. 该用哪个

| 要回答的问题 | 用 |
|---|---|
| 真 `.dlg` 全量往返、真实切片/按钮状态、真图渲染、游戏内布局 | `interface1019`（`interface.fls`） |
| 谁加载哪个布局、按钮皮肤/消息号 | 仓库内 `tools/script_link/build_script_index.py` 产物（已入库，别下载语料） |
| 「符号 X 在全档有没有定义者」、语义级全档检索 | `MXSJ_CORPUS` |
| 只查某一条 entry 的代码 | `tools/decompiler/recover_entries.py --entries N`（秒级，见 `DECOMPILE_CORPUS.md` §2） |

## 3. 取用（产物一律在仓库外）

```sh
OUT=/home/user/ext && mkdir -p "$OUT"          # 仓库外，别放进仓库
```

**interface.fls（分卷）**

```sh
# 4 个文件下载到同一目录后，解最后一个 .zip；7z/unzip 会按 .z01→.z02→.z03 自动续卷
7z x -o"$OUT/mxsj" interface.zip               # 或： unzip interface.zip -d "$OUT/mxsj"
# 解出的目录结构以实际为准；找到 interface.fls 后记下真实路径
find "$OUT/mxsj" -maxdepth 3 -iname 'interface.fls'
```

- `.z01/.z02/.z03` **不能**单独解压，也**不要** `cat` 拼接（它们本来就是同一个 zip 的卷）；
- 想先看里面有什么：`7z l interface.zip`（同样需要三卷在同目录）。

**反编译语料（10 个独立 ZIP）**

```sh
cd "$OUT" && sha256sum -c MXSJ_CORPUS_8212b26_20261015_ARCHIVES.sha256   # 先对官方清单
mkdir -p corpus
for z in MXSJ_CORPUS_8212b26_20261015_part*.zip; do
  unzip -q -o "$z" -d corpus        # 10 个卷解到同一个空目录，不是拼包
done
```

- 解压后再跑一次产物自校验：`corpus/SHA256SUMS`（索引 §6 记录归档后 185,048 个文件逐字节校验通过）；
- 入口：`full/manifest.audited.jsonl`（主键 `(archive_sha256, entry_index)`，不是文件名），
  报告在 `reports/`，版本/工具指纹在 `versions.json`、`external-tools.sha256`。

**把语料指给编辑器/回归用例**

```sh
export MXSJ_DLG_CORPUS="$OUT/mxsj/interface"     # 支持 ':' 分隔多目录；数量按实际上报
(cd ui_editor && PYTHONPATH=src python3 -m unittest tests.test_codec)
```

## 4. 边界（违反就先停下来问）

1. **不入库**：分卷、解压后的 `.dlg`、反编译语料都不进 git（红线 §4-8）；仓库里只留本文件和命令。
2. **不覆盖原始包**：`data/script.fls`、`interface.fls`、密钥表一个字节都不动；编辑器一律「原包不动、另存新包」。
3. **不擅自上传/改权限**：这份 Drive 是用户提供的取用位置，不是我们的备份盘；不加分享、不改权限、不删卷。
4. **只读解析**：语料不执行、不 `eval`；`.dlg` 只当数据解析。
5. **校验先行**：语料用官方 `ARCHIVES.sha256` 对；`interface` 分卷**没有公开校验和**，
   下载后自己 `sha256sum` 一遍并记进本节（表待填，别拿别的数字冒充）。
6. **未验不宣称**：截至 2026-10-20 只核了元数据；「真 `.dlg` 全量往返通过」「真切片与游戏一致」
   这些结论要等真跑完再写进 `STATUS`，并按实际数量上报。

## 5. 待补（下次真正取用时填）

| 项 | 值 |
|---|---|
| `interface.fls` 实际路径 / 解压后条目数 | 待实测 |
| `interface.z01` SHA-256 | 待实测 |
| `interface.z02` SHA-256 | 待实测 |
| `interface.z03` SHA-256 | 待实测 |
| `interface.zip` SHA-256 | 待实测 |
| `MXSJ_DLG_CORPUS` 指向后 `test_codec` 实际解的篇数 | 待实测 |
