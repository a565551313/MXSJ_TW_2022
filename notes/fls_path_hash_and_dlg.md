# 0SLF 路径哈希寻址与 interface.fls 对话框布局（.dlg）逆向记录

> **2026-10-16 更正（第二处）：§2 的「运行时线性扫描」不适用于 `.dlg`。**
> `0x48ECF0` 的线性扫描属 **ReadFls** 那条取目录路径；`.dlg` 真正走的是
> `0x45D580 LoadFile → 0x609760 → 0x6097F0 → 0x60DD00`，而 `0x60DD00` 先调
> `0x60E080` 求路径哈希，再把目录交给 **`0x60E690` = `std::lower_bound`（二分）**
> 定位，返回后 `0x60DD3D` 判「到 end」、`0x60DD41` 判「entry_id 不等」
> （`sub %esi,%ecx` → `sar $0x4` 求条数、`sar %edx` 取中点、
> `cmp %edi,(%esi,%eax,8)` 逐次半区）。**因此目录必须按 entry_id 升序**，
> 新增条目若只追加到目录尾会查不到——这正是资源/UI 编辑器 0.3.3/0.5.2
> 「有序插入 + 重算下标」修复方向正确的依据（详见
> [native_dlg_path_cipher.md](native_dlg_path_cipher.md) §2）。
> §2 的解目录公式（`0x48F170`）本身**仍然有效**（本轮已逐条比对反汇编，
> 三个闭式常量在 `.text` 中各只出现 1 次）；失效的只是「运行时线性扫描」
> 这一句及其推论。实测反例：把同一份新条目改成追加到目录尾，用精确复刻的
> lower_bound 查询 → **查不到**（插值点落在无关 entry_id 上），与 0.5.2 记录的
> 「新图不显示、重开条目变少、进游戏卡屏」症状一致。

> **2026-10-14 更正**：真实 C_sys.LoadFile 绑定为 0x45D580，而非这里旧记录的
> 0x461340（后者实际名为 ReadFls）。原生包内 .dlg 的 XOR 密钥来自路径哈希：
> `((hash + 0x9234AB) & 0xffffffff) ^ 0x937F4912`，不是随机/从文件头自解。
> 新的绑定与调用链证据见 [native_dlg_path_cipher.md](native_dlg_path_cipher.md)。
> 下文旧加载器地址归属与“密钥派生未定位”已被该证据取代；既有明文头反推是
> 编辑器解码技巧，不等于原生能读任意密钥/明文新增。原目录字段不凭猜测重写。


> 2026-10-13 结案。结论：台服客户端的 UI 布局文件 `.dlg` 全部存放于
> `interface.fls`，包内以「路径哈希 → entry_id」寻址，负载为 4 字节
> XOR 加密的 Python 源码。脚本引用的 2,901 条 `.dlg` 路径中 2,706 条
> 已定位并解码（成品在本机 `interface_dlg_decoded/` 与同名 zip，
> 未入库）。工具：`tools/data-parser/mx_path_hash.py`（哈希复刻）、
> `tools/data-parser/extract_dlg.py`（按路径提取）。

## 1. 证据链概览

| 环节 | 结论 | 证据 |
|---|---|---|
| 脚本加载链 | 台服走「包内文本 exec」分支 | 反编译 `script/combdialog.py`（idx 579）、`uetovr/debug/innerversionfun.py`（idx 4538）、`script/interface.py`（idx 3854：`UIPath='interface'`、`TAIWAN=1`）、`script/misc.py`（idx 1693：`IsTWServer()==True`） |
| 引用面 | 2,901 条不同 `.dlg` 路径、1,400 个引用模块 | 对 script.fls 全部 5,002 条目做 marshal 常量收割（py2.5/2.7 常量遍历） |
| 包内定位 | `entry_id == mx_hash(规范化路径)` | mxmain.dll 反汇编复刻哈希后：interface IG 记录 390/483 命中、misc.fls 11/11、`.dlg` 2,706/2,901、`ui.lst` 命中 idx 29720 |
| 负载解密 | 4 字节周期 XOR，头部反推密钥 | 2,706/2,706 解出合法 `# -*- coding: gbk -*-` + `UI_INFO` 源码 |

## 2. 0SLF 目录与运行时查找（mxmain.dll）

客户端本体位于仓库根目录 `mx.exe` / `mxmain.dll`（同一镜像）。

- **目录读取 VA `0x48F170`**：读取一条 16 字节记录
  `<IIII (entry_id, r1, r2, r3)>`，解出四个值：

  ```
  f1   = ((index * 0x0E7C83D2 + entry_id) ^ r1)        # 见 §5
  len  = ((r1 * entry_id + 0x0DF25E) ^ r2)
  off  = ((r2 * index * 0x00F718FE + 0x0D59D16C) ^ r3)
  ```

- **包查找 VA `0x48ECF0`**：以 `"rb"` 打开包文件，校验 `0SLF` 魔数，
  读 12 字节头（count、目录偏移），seek 到目录后逐条调用
  `0x48F170` **线性扫描**（`0x48EDE6`–`0x48EE16`：`inc %esi` 逐条比对），
  拿解出的 `entry_id` 与 `0x48EF80(路径)` 的结果比对；命中后把 16 字节解码结构
  `{entry_id, f1, len, off}` 拷回调用方。未命中返回错误码 3。
  其上层封装 `0x461340` 对应脚本侧 **`ReadFls`**（不是 LoadFile；见文首两处更正）。

> 注：目录内 entry_id 虽然全局升序（打包时按哈希排序），运行时用
> 的是线性扫描，并非二分。
> **⚠ 2026-10-16 更正：这句只对 `0x48ECF0`（ReadFls）成立，对 `.dlg` 不成立。**
> `.dlg` 走的 LoadFile 链在 `0x60DD00` 用 `0x60E690`（`lower_bound`）**二分**定位，
> 所以目录必须升序（见文首更正与 `native_dlg_path_cipher.md` §2）。
> 此前按「文件名 → 标准哈希
> (CRC32/FNV/DJB2/BKDR/Murmur…)」的大量尝试全部失败，正是因为
> 哈希为引擎自研（§3），与文件名约定无关。

## 3. 路径哈希 VA `0x48EF80`（复刻见 mx_path_hash.py）

1. **规范化**：逐字节扫描路径，`\`（0x5C）替换为 `/`，
   小写字母减 0x20 转大写；写入以 0 填充的 u32 字数组
   （第 i 字节进入第 i/4 字的第 i%4 字节道，用加法组装）。
   最长 256 字节（64 字）。
2. 在最后用到的字之后依次写入终止字 `0x9BE74448`、`0x66F42C48`。
3. 状态初值 `A=0xF4FA8928, X=0x37A8470E, Y=0x7758B42B`，逐字迭代：

   ```
   A  = (2A + (A >> 31)) mod 2^32
   U  = A ^ 0x267B0B11
   Y ^= w;  Xn = X ^ w
   m1 = ((Y + U) & 0xBDEB77DE) | 0x02040801
   V  = fold1(Xn * m1)          # 64 位积的 1 的补数折叠
   m2 = ((U + Xn) & 0x7D7EBBDE) | 0x00804021
   Y  = fold2(Y * m2)           # 高半字 *2 后带进位折叠
   X  = V
   ```

4. 返回 `Y ^ X`。

测试向量：`dialog/recommendfriend.dlg -> 0x04964CA7`、
`dialog/report_command.dlg -> 0x38A57E9D`、`ui.lst -> 0x8DA5E6EC`
（与 interface.fls 目录逐条核对无误；分隔符/大小写差异经规范化
后等价）。

**适用面**：全部 0SLF 包共用（IG 清单即按此互引：记录文本
`IG\r\n<域名>\r\n<路径>` 给出的路径哈希应落在域名包内；
interface 390/483 命中、未命中者多为跨包引用或已移除资源，
misc.fls 本地验证 11/11）。**例外**：script.fls 的脚本模块不走
本查找（试过 20 余种输入形式均不命中），其导入解析机制另行处理，
见 §6。

## 4. .dlg 负载的 XOR 加密

- 存储字节 = 源码明文与一把 **每条目 4 字节密钥**的周期 XOR，
  无压缩（解码后长度与存储长度相同，尾部以 `},\n]\n` 收尾）。
- 明文首行恒为 `# -*- coding: gbk -*-`（次行为源文件 MD5 戳，
  系 UI 编辑器保存时写入，与解码正确性无关，戳值与整文件 MD5
  的对应关系未验证），故密钥可直接由前 4 字节反推：
  `key = ct[0:4] ^ '# -*'`。2,706 条全部一次解码成功，
  `UI_INFO` 布局定义完整（控件树、`.igs` 关联文件等俱在）。
- **密钥的派生公式未定位**：已排除与路径哈希结果（含中间状态
  X/Y）、目录各字段（r1/r2/r3/f1）及偏移/长度的算术组合、
  明文/密文 CRC32/MD5 前缀、归一化路径的标准哈希等。因文件头
  固定，不影响解码；推测为打包工具侧参数（保存 MD5 戳的同一
  工具链），如后续需「任意路径 → 直达解密」再行深挖。

## 5. 目录第四字段 f1 的观察

打包器并非随机填 r1：对 2,706 条布局记录回算，
`f1 = ((index*0x0E7C83D2 + entry_id) ^ r1)` 有 2,659 条恰为 0，
其余为小整数（1、2、3…个别达 173）。即打包器把一个小标记编入
r1。布局条目中 f1 非 0 者同样正常解码，故 f1 与加密方式无关；
其确切语义（疑为资源子类型/版本标记）未明，不影响读写——
`resource_editor` 重打包时本就原样保留 `(entry_id, r1)`。

## 6. 未决与排除项（避免重复劳动）

- **195 条未命中 `.dlg`**（dialog/ 130、根目录 30、dialog4/ 6 等）：
  包内无对应哈希条目，前缀拼接（`interface/`）亦不命中；应为
  已删除的死引用（脚本收割覆盖全部模块含不可达代码），或运行时
  经 `buildstyle` 样式重映射后才命中的路径变体。
- **script.fls 模块导入**不使用 §3 哈希：候选输入（完整路径、
  去扩展、点分名、`.pyo/.pyc`、域名/资源根前缀、UTF-16LE、
  反转串等）与 30 余种哈希函数（含 mx 复刻）两两组合均不命中
  4,979 组「文件名 ↔ entry_id」真值。疑为按 marshal 内
  `co_filename` 建表或私有索引，待单独课题。
- `.dlg` 明文 MD5 戳的计算口径未验证（整文/去戳行/CRLF 变体
  均不符，疑为编辑器内部序列化摘要）。

## 7. 复现

```bash
# 哈希自检（3 个真值向量）
python tools/data-parser/mx_path_hash.py

# 从客户端 interface.fls 按路径提取布局
python tools/data-parser/extract_dlg.py <interface.fls> <输出目录> \
    dialog/worldmap.dlg ui.lst

# 批量：--paths-file 指向路径清单（每行一条）
```

`interface.fls`（614 MB，云盘保存，未入库）因体积走「本机探针
dump 指定条目」流程：探针 `interface_probe4.py`（仓库根目录，
未入库）内嵌由脚本收割路径算出的 2,706 个条目下标，批量导出
负载与目录原字段，再由本机解码校验。

## 8. 附记：ui.lst

`ui.lst` 同样以哈希条目存于 interface.fls（idx 29720，
`entry_id = 0x8DA5E6EC`，f1=0），但其负载为 **明文**（无 XOR）：
69,300 字节、2,418 行的 INI 风格 UI 样式注册表，含 `[Font]`、
`[NewFont]`、`[List]`、`[Table]`、`[Button]`、`[Frame]`、
`[TBStyle_000]`…`[TBStyle_105]` 等节（字体表、控件颜色/边距等
样式参数），GB18030 编码。说明 XOR 加密只施加于 UI 编辑器产出的
`.dlg`，并非包级统一处理。用 `extract_dlg.py` 按路径 `ui.lst`
即可直接取出（频率恢复得到全零密钥时按明文写出）。成品与
2,706 个 `.dlg` 同置于 `interface_dlg_decoded/`。

## 9. 附记：控件图片（sFileName）引用分布

全包目录扫描（探针 v7）结论：2,706 个已解密 `.dlg` 共引用
2,738 个不同的 `sFileName`。其中 706 个是以 `\` 结尾的**目录型
伪引用**（边框类控件拼图用的基路径，如
`combdialog2\公用内框\`，运行时再拼 left/right/top/bottom 等
子图），并非文件、永不命中。其余 2,032 个文件引用中 **2,028
个命中，仅 4 个未命中**：

* interface.fls 2,008 条（PNG 与 I0/T0/I1 精灵为主）；
* item.fls 20 条（`item120/`、`item44/` 前缀，与运行时
  `combdialog.py::GetIgsPath` 的“interface 不存在则回退 item”
  逻辑吻合）；
* 未命中 4 条：`combdialog4\回归活动\huawen1.png`、
  `huawen2.png`、`combdialog4\活动界面\氛围图.png`、
  `combdialog\杂图\人物大筐140x200.igs`，疑为热更新资源，
  不在本批客户端文件中。

注意抓取口径：`sFileName` 必须经 Python 字面量求值得到单反斜
杠原值再做 GBK 编码哈希；直接正则抓取 `.dlg` 源码会得到双反
斜杠转义形，哈希后变成双斜杠而全部落空（探针 v6 的教训）。
UI 编辑器挂载 interface.fls（+ item.fls）即可解析约 99.8% 的
文件引用图片。
