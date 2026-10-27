# 项目当前状态（STATUS）

> **2026-10-28（本地 UTC+8；同日 UTC 仍是 10-27）：脚本编辑器 0.6.0.dev15（分支 `arena/39bf6796-mxsj-tw-2022`，起点 `65092a0`）**：
> 对 dev14 的 PR #96 自动审查做**逐条验证**（13 条行级评论、去重后 10 个独立问题）：**9 条判定成立并已改**（8 处代码 + 1 处文档限定），1 条（STATUS 日期）复核后说明不改：
> ① **换包重建目录树**（gitar 4394946826）：`repoint_archive()` 假定条目表不变——只按 `min(子项数, 条目数)` 重指、只更新第 1 列。
> 同一路径换成**条目更少**的包会留下指向已 `close()` 文档的子项（点开报"资源包读取句柄已关闭"），换成**条目更多**的包则新条目不出现。
> 新增 `replace_archive()`：先比 `[e.identity for e in entries]`，一致才走 `repoint_archive`，不一致就删掉旧根项、`close()` 旧文档，再 `add_archive(new)` 整棵重建。
> ② **`module_paths` 不再无条件承接**（kody 4394961254 / CodeRabbit 4394985535）：原来 reload 后无条件 `new.module_paths = dict(old.module_paths)`，
> 换包后显示旧模块名、tooltip 还写"已读取路径"。现在只在**条目身份一致**时承接，否则留空显示"（路径未读取）"。
> ③ **单条历史被拆成字符**（gitar 4394946914 / CodeRabbit 4394985518）：QSettings 的 INI 后端把单元素 list 读回成 `str`，
> `set_history` 迭代字符串会把 `needle` 变成 `n,e,e,d,l,e`。`Window.__init__` 与 `SearchField.set_history` 两侧都先按单条规范化。
> ④ **`fd == 0` 被真值判断误判**（CodeRabbit 4394985502）：`fd = self._fd or os.open(...)`，描述符 0 合法且假值，
> 于是借来的 0 号描述符被丢掉、另开一个，又因 `borrowed` 为真不进 `finally` 关闭——每次读泄漏一个句柄，正好抵消本轮的"读完即放"。
> 改成 `self._fd if borrowed else os.open(...)`。
> ⑤ **借用句柄并发互关**（kody 4394960823）：`open_handle()` 原来在锁外 `yield`，两个借用者共用 `self._fd` 且各自无条件关闭。
> 改为**引用计数** `_borrowers`：第一个进入的人开、最后一个离开的人关；`close()` 清零计数。
> ⑥ **Ctrl+F 涂出假命中**（gitar 4394947025 / CodeRabbit 4394985542）：查找框留着上次的词时，`show_search` 会把光标行直接标成命中并写历史。
> 现在只在"选中内容 == 查找词"时才标记，否则清标记；历史仍记，因为那是用户的查询。
> ⑦ **编辑后高亮错位**（CodeRabbit 4394985515）：改文本后 `_match_range` 的偏移失效。`contentsChanged` 一改就清 `_match_block`/`_match_range` 并重画，
> 顺带让命中片段区间先夹进当前行再画（跨行时不再越界）。
> ⑧ **查找历史被 `strip()` 改写**（CodeRabbit 4394985546，Major）：`remember()` 原来 `strip()` 后还 `setEditText()` 回写，
> 把 `" foo "` 这种查询悄悄改成 `"foo"`、纯空格查询直接变空。现在保留原样，且只在当前框内容不同时才回写。
> **复核后不改**：`docs/STATUS.md` 日期——本项目文档一律用维护者本地时区（`master` 合并点 `65092a0` 的提交时间就是 `2026-10-28 05:59 +0800`），
> 本地确实是 10-28；已在条目标题写明 `UTC+8`，避免再按 UTC 判成"未来日期"。`script_editor/README.md` 的 Windows 限定**采纳**，
> 现在明写"Linux 已实测、Windows 未实机验证"。
> **实测**：新增 `tests/test_gui_search.py` 11 项（嵌套借用不互关、50 次读不泄漏描述符、托盘换包重建/变小不留旧子项、
> 同目录 reload 承接模块名、换包丢弃模块名、重新打开查找不标无关行/标中选中行、历史保留空格、单条 QString→list、
> 编辑即清命中标记）。反证过：把 `replace_archive` 换回 `repoint_archive`，其中 2 项立刻变红。
> 复跑全量 **551 项 OK（59 跳过）**、`ruff check src tests` 0、`docver` OK、`wincompat` 0/0/0。
> **未验**：Windows 实机（"编辑器开着也能改名"仍是推断）、真实双编译器端到端、游戏内表现。

> **2026-10-28：脚本编辑器 0.6.0.dev14（分支 `arena/39bf6796-mxsj-tw-2022`，起点 `65092a0`＝PR #95 合并点）**：
> 用户三条直接反馈，逐条落地——
> ① **「改完生成新包后想让原包改名、用新包替换，但文件被编辑器占着，必须关掉编辑器」**：
> 根因是 `FileReader` 打开包时 `os.open` 一次、之后**整个会话都握着这个句柄**。Windows 上
> `msvcrt`/CRT 的 `open` 用的是 `_SH_DENYNO`（允许读写共享，但**不允许 rename/delete**），
> 所以只要编辑器开着，资源管理器就改不了包名、也换不掉文件。改成**读完即放**：
> 每次读在锁内 `os.open → 读 → os.close`，整包摘要/回读这类批量动作用 `open_handle()` 借一个句柄再还回去；
> `ArchiveDocument` 打开时也不留句柄（`FileReader.__init__` 只用 fstat 取一次修订快照就关掉）。
> 于是 F6 生成新包后，可以直接在资源管理器里给原包改名、把新包改成原包名，再点
> **「文件 → 重新读取已打开的包（改名/替换后用）」**，不必重启编辑器；路径读不到时明确报「可能被改名、移走或删除，请重新打开」。
> **校验没有放松**：`_assert_unchanged()` 依旧同时比对句柄 fstat 与路径 fstat，且现在是在**借来的句柄**上比对后再读，
> 读到的字节与校验的文件是同一个；原有的「打开后被改过就拒绝」的 4 项回归全部照旧通过。
> ② **「默认打开查找、查找框改成可编辑的历史下拉」**：查找栏常驻显示（不再默认 `hide()`），
> 查找框换成 `SearchField(QComboBox)`——可编辑、查过的词自动进历史（去重、最新在前、最多 20 条），
> 随 `QSettings` 的 `find/history` 保存/恢复；对调用方仍提供 `text()/setText()/selectAll()`，既有代码与测试不用改。
> ③ **「命中查找的整行要更明显」**：原来只有光标行（alpha 24，几乎看不见）。现在跳到的命中行整行铺**不透明淡黄**
> `#ffe9a8` 的 FullWidthSelection，命中文字本身再压一段更深的 `#ffb347`；大纲/转到行跳转也走同一套标记，关掉查找栏即清除。
> **实测**：新增 `tests/test_gui_search.py` 12 项（打开包时 `/proc/self/fd` 下无该文件句柄、读/摘要/元数据后仍无、
> 关闭后不再重开、**开着文档能直接 os.rename、随后读它报「已不可读」而不是读到旧字节**、修订不符仍拒绝、
> 查找栏初始可见、查找框是可编辑下拉、历史去重与顺序、从设置恢复历史、命中行整行底色 + 命中文字更深、
> 关闭查找栏清除标记、大纲跳转标记行、替换/改名后「重新读取已打开的包」成功与失踪路径报告）；
> 既有菜单顺序测试因新增菜单项同步更新。复跑 **540 项 OK（59 跳过）**、`ruff` 0、`docver` OK、`wincompat` 0/0/0。
> **未验**：沙箱是 Linux，句柄语义用 `/proc/self/fd` + `os.rename` 实际验证；**Windows 上「编辑器开着也能在资源管理器改名」这条只能靠
> CRT `_SH_DENYNO` 语义推断，必须在实机确认一次**。其余（真实双编译器、游戏内表现）仍未验收。

> **2026-10-27：脚本编辑器「扩充定长条目」实验开关（分支 `arena/89785502-mxsj-tw-2022`，起点 `bb20d1b`）**：
> 用户问「`authored marshal exceeds fixed XOR length; no shrink/rescale` 怎么彻底解决」。先分清两层事实：
> ① **工具层**：`KeyProfile.crypt` 用目录里的固定长度校验，`encode_replacement()` 在 `len(native) > expanded_size`
> 时硬拒绝，这是**保守策略**，不是能力缺失；② **客户端层**：`mxmain` 的 `0x45D48B..0x45D529` 每次**按 seed 和它拿到的 size 现算**
> 4 个边界、到实际负载末端截停**（`cursor += size // 5 + seed // 256`，循环 5 次、取前 4 个），`seed` 只由模块名决定
> ——所以变长条目在算术上是自描述的，客户端不需要另存一份参数表。据此落地一个**默认关闭的实验开关**：
> 新增 `KeyProfile.crypt_variable()`（`bounds_from_keys(keys, len(data))`，原长度下与 `crypt` 等价）、
> `encode_replacement_detailed()`（返回 stored/`native_size`/`resized`，超长且未授权时仍报原文案，超长且授权时按新长度加密，
> 长度无法分成五段就提前拒绝而不是写出不可读的包）、`PreparedBuild.resized`；`allow_resize` 从
> `prepare_build`/`prepare_package`/`publish_package` 一路传到 `build_package`，`verify_output()` 改用
> `crypt_variable` 回读（对原长度等价，对变长条目是唯一正确读法）。GUI 挂在「保存模式」菜单里：
> **扩充定长条目（实验）**，勾选先弹一次风险确认，状态栏/清单预览/宽松写回结果都明写「长度会变、客户端未验收」。
> 写包仍走既有 `write_script()`（它本来就会重排 span 偏移、重算目录 `r2/r3`、回写目录指针），因此**不需要新增条目能力**
> ——`write_script()` 的「不能插入条目」限制与本次开关无关。**实测**：新增 2 项回归（授权后写入变长条目并整包回读逐字节相等、
> 长度无法分成五段时提前拒绝且不留输出文件），`tests/test_native_build.py` 15 项、全套 **490 项 OK（121 跳过）**，
> `ruff` 0，`check_doc_versions.py` OK。**未验**：客户端/游戏是否真按新长度取参、是否有别的定长假设（预分配缓冲区、总量校验、
> 内存段表）——一次实机都没有，所以默认关闭，且**开关打开 ≠ 客户端验收**；Windows 实机写回与 `.fls.bak` 复核仍未做。
> 锁定输入 `data/script.fls`（`8b6e9266…c0d72`）与 `tools/decompiler/script_fls_keys.json`（`43bb090d…daceb`）本轮未改动。
>
> **PR #94 审查复核（同日）**：5 条行级评论（gitar-bot 2 + CodeRabbit 2 + kody 1）逐条对照代码与语料复核——
> **4 条属实已修，1 条驳回**。
> ① **（属实，最严重）** `prepare_build()` 的原生往返回读还在用定长 `crypt()`，所以打开实验开关后 **F6 预览与宽松 Ctrl+S 都会在编译后立刻报
> `boundary rescaling forbidden`**，功能在 GUI 里完全不可用；新加的测试直接调 `build_package` 绕过了这一段，没抓到。已改用 `crypt_variable()`，
> 并补 3 项回归（预览往返、未授权仍拒绝、`prepare_package` 的清单带 `resized`）；**反证过**：把改动退回 `crypt()`，3 项里 2 项立刻红。
> ② **（属实）** 反编译器渲染里**只有 `\xNN` 是转义**，负载里的 0x5C 是**单个**反斜杠而不是 `\\`。旧实现把这对反斜杠当转义，Big5 尾字节
> （`功` = `A5 5C`）被吃掉：语料 `script/login/dgw.py:118` 读成 `成功xb3s…`，正确是 `成功連上遊戲服務器後，用此接口告知DGW服務器`。
> 改成「非 `\xNN` 的反斜杠就是 0x5C」，并给非 raw 字面量加 `_renderer_shaped()` 闸门（只含 `\xNN` 才按渲染读，`\033` 这类手写转义继续拒绝）。
> **全语料对比**（61 个 `.py`、69 处字面量）：1 处读法改变（就是这条），0 处新增噪声，0 处丢失。
> ③ **（属实）** 渲染是**有损**的：原常量若真写着反斜杠加 `xNN`，渲染与单字节 `0xNN` 完全同形，不可区分。所以标注从「（还原）」改成
> **「（反推候选）」**，`RESTORED_NOTE` 明写「候选而不是逐字节证明」。
> ④ **（采纳）** 扩容条目**拒绝**在原地写回游戏客户端目录（`client_root_for()`，在出包前判定）：只放开到副本／F6 新包，非扩容的宽松写回不受影响。
> ⑤ **（驳回）** kody 要求 README 不要写「改模块会连带改 docstring 字节／可写回原包」——宽松模式是用户显式拍板的交付范围，且写前写后校验一个没省；
> 已按 ④ 把「无客户端验收的扩容」从客户端目录里挡掉。
> 复核后全套 **495 项 OK（121 跳过）**、`ruff` 0、`docver` OK、`wincompat` 0/0/0。
>
> **2026-10-27：脚本编辑器 0.6.0.dev13 界面重做（分支 `arena/0c58688a-mxsj-tw-2022`，起点 `4233dc5`＝PR #94 合并点）**：
> 用户原话「这脚本编辑器什么玩意，我只想简单点……写入原包就是写入原包，没有多余步骤，点一下就好」。经一次 ask_user 确认四点
> （打开脚本文件/目录＝`.fls`；生成新包＝弹一次保存对话框；超长条目＝自动按新长度重算；写入原包＝任何地方零确认、照旧留 `.bak`）后重做：
> ① **菜单只剩六个**：文件（新建 .py／打开 .py／打开 .py 目录／保存／另存为／打开 .fls／打开脚本目录／退出）、语料（导出全量解密／加密）、
> 编辑（撤销/恢复/剪切/复制/粘贴/查找/替换/在文件中查找/在文件中替换）、编码（不变）、编译（**写入原包 F5**／**生成新包 F6**）、视图（不变）。
> 删掉：保存模式开关、手工「关联源码到条目」、「检查并采用为源码」按钮、清单预览对话框、导入语料/核验参数/生成 data 清单/另开语料候选、
> 选择 XOR 目录、选择开发编译器、仅导出 pyc、项目菜单项。工具栏＝打开/目录/保存/撤销/恢复/查找/写入原包/生成新包/检查编译器。
> ② **写入原包**：一次调用完成 编译→审计→原生往返→整包重写→回读→留 `<包名>.fls.bak`→原子替换，无任何确认框；**生成新包**：一次保存对话框后写新文件并自动切换来源。
> ③ **自动校验+绑定**取代「检查并采用」：打开条目即真实编译+严格原生往返+整包回读，通过则把工作副本落到 `$MXSCRIPT_HOME/sources/<包名>/`
> （默认 `~/.mxscript`）并写入 Binding，标签变绿「可写包 · 已自动校验并绑定」；失败标红但仍可编辑、可按 F5 重试；无编译器时提示先自检。
> ④ **超长条目自动扩容**（`allow_resize=True` 固定打开，`CapacityError` 仍保留数字供诊断），结果面板明写「N 条按新长度重算（实验功能）」。
> ⑤ 新增 `core/services/corpus_export.py`：整包导出（解密＝标准 pyc，解不开的少数条目落 native 负载并标注；加密＝原样存储字节）+ `manifest.json`（含原包摘要、逐条 sha256、失败清单），目标目录必须不存在。
> ⑥ `core/services/files.py` 增 `save_working_source()`（同文本复用同一副本，不同文本自动 `-2`）与 `default_source_root()`。
> **实测**：新增 `tests/test_gui_reform.py` 13 项（菜单/工具栏形状逐字断言、F5 真写包+备份+摘要更新、F6 不动原包、无绑定源码时拒绝、自动绑定成功/失败/无编译器三态、两种语料导出端到端）；
> 改 6 个既有测试以匹配新菜单与新启停规则。本轮首次在沙箱里**真跑起 Qt**（自建 libGL/libEGL/libxkbcommon/libdbus 等符号桩 + `LD_LIBRARY_PATH`），
> 因此 GUI 测试不再跳过：全量 **507 项 OK（59 跳过）**、`ruff check src tests` 0、`check_doc_versions.py` OK、`check_windows_compat.py script_editor` ERROR/WARNING/INFO 全 0；
> 截图核对了实际布局（`/home/user/mxsj_ui.png`，CJK 字形缺字体显示为方块属沙箱环境）。**未验**：Windows 实机、真实双编译器端到端写回、
> 自动绑定在真实大包上的耗时、Qt 真机观感、游戏内表现（含自动扩容后的变长条目）。
> 
> **2026-10-28：PR #95 审查复核，第一轮（同分支）**：20 条意见（17 条行级评论：gitar 2 + kody 5 + CodeRabbit 10；另 3 条正文 nitpick）逐条对照代码复核——
> **17 条属实已修、2 条驳回、1 条部分属实（只加兜底，见下面的 identity）**。属实且改动行为的有：
> ① **（最危险）`replace_in_files` 会把文件内容翻倍**：`QTextCursor.movePosition(Start)` 不带选区，`insertText` 把新文本**插到开头**、原文留着；
> 改成 `select(Document)` 后整篇替换，替换计数改为编辑成功后再累加；② **自动校验失败会弹模态框**：`Window.task()` 在 `on_error` 后无条件 `fail()`（=`QMessageBox.warning`），
> 打开条目失败一次就弹一次——`task()` 新增 `quiet=True`，`auto_adopt` 用它，失败只标红标签 + 状态栏一句话；
> ③ **自动绑定没查来源**：`auto_adopt` 只看 `source`/`complete`，外部语料 pyc 与原包不一致也能拿到可写绑定（手工 `adopt_recovery` 本来是拒的）。
> 判定抽到无 Qt 的 `core/services/recovery_origin.py`（`standard_sha256()` / `origin_conflict()`），两条路径共用；
> ④ **先落盘后校验**：校验失败会在 `sources/` 留下孤儿 `-2/-3` 副本——改成先 `inspect_module` + `origin_conflict` + `prepare_build`，
> 之后才写工作副本（`Binding.associate` 要求文件已存在，所以写入放在校验后、绑定前，构建失败时把这个新文件删掉）；
> ⑤ **两个同名包共用一份工作副本**：目录名加 `<sha256(包路径)[:10]>`；⑥ **同一条目两个草稿互相顶绑定**：`clear_other_bindings()` 把旧标签降级为
> 「恢复稿 · 已被同条目其它草稿取代绑定」；⑦ **校验失败的草稿按 F5 没救**：`_write_package` 先尝试 `retry_unverified_draft()`（重校验通过即继续写包）。
> 另有 6 条低危（导出目录读写放进逐条 try、native 负载补 size/CRC、取消导出也要报已写目录与条数、`ArchiveDocument()` 移进 try 并在批处理失败时释放读句柄、
> 属性行「写入目标」改用 `binding_for_source()`、`CapacityError` 文案不再指向已删除的「保存模式」菜单、STATUS 本行数据与 `Files` 文案）。
> **驳回 2 条**：kody「语料导出目标必须在仓库外」——用户约束是**不覆盖原始客户端包、生成物写仓库外**，导出目录由用户选择且必须不存在、`guard_output` 已排除原始包；
> kody「写工作副本期间禁用整个窗口」——已有 `jobs` 忙碌门闩 + `task` 串行，禁用整窗会让自动校验期间窗口卡死。
> **实测**：`tests/test_gui_reform.py` 新增 12 项（替换后逐字文本、quiet 失败不弹框、响亮失败仍弹、取消任务仍报结果、同条目换草稿降级、
> 来源不符拒绝绑定、F5 重试后真写包、导出单条读失败只记该条、越界文件名拒绝、identity 净化、py27 负载 CRC 校验、取消导出报目录/条数）。
> 复跑：**519 项 OK（59 跳过）**（本轮 507→519）、`ruff check src tests` 0、`check_doc_versions.py` OK、`check_windows_compat.py script_editor` ERROR/WARNING/INFO 全 0。
> **未验**：以上全部是本机 offscreen 单测；Windows 实机、真实双编译器端到端、游戏内表现与客户端加载均未验收。
> 
> **2026-10-28：PR #95 审查复核，第二轮（针对 `839d09a` 的新意见）**：11 条行级（gitar 1 + kody 4 + CodeRabbit 6）＋ 1 条 outside-diff，逐条复核——
> **8 条属实已修、2 条驳回（同前两轮的理由）、2 条属测试规范已照办**。本轮最要紧的三条都是**上一轮修复引入或暴露的**：
> ① **（真 bug，自己挖的坑）不完整恢复稿永远绑不上**：`auto_adopt` 用 `report.complete` 当闸门，而这是引擎输出的冻结字段；上一轮把「按 F5 重试」接到同一个 `origin` 上，于是标着「补齐后按 F5 会重新校验」却每次都返回 False。
> 改成「文本已改过就跳过完整性闸门」，让真实编译 + 原生往返判定（与已删除的手工路径同一条规则）；
> ② **（真 bug，政策）语料导出会给 1288 写文件**：`read_stored` 不查 `core/policy.py`，导出循环在 `inspect_module`（唯一查策略的地方）之前就读了负载，
> 加密模式直接落存储字节、解密模式落到 native 回退——等于给被排除的条目做 dump。现在逐条 `try` 的第一句就是 `require_module_allowed(archive.vm, index)`，
> 命中记进 `failures`、不读不写；③ **（真 bug）工作副本路径没规范化**：`save_working_source` 返回未 `resolve()` 的路径，`Binding.associate` 存的是 `resolve(strict=True)`，
> `MXSCRIPT_HOME` 相对路径/含符号链接时 `tab.path != binding.source`，`binding_for_source()` 找不到绑定、F5 重试无限起任务、永远写不出去。现在写完立刻 `.resolve()`。
> 其余属实：`replace_in_files` 原来用 `str.replace` **无视「区分大小写」「全字匹配」**（全字匹配开时替换 `x` 会连 `max` 一起改）——改成 `document.find` + `search_flags()` 取匹配区间、倒序替换；
> `new_source_file` 少了 `assert_writable_target()`（另存为/另存草稿/导出都有，只有「新建」能把 .py 写进只读语料目录）；
> 语料导出写入改为「同目录临时文件 + `os.replace`」（半截文件不再冒充完整条目）、`ENOSPC` 立即停并保留已写清单、`manifest.json` 写不进去时报出「已写 N/M 条 + 目录」；
> 两个测试卫生问题（`read_stored` 用 `patch.object` 而不是直接改属性；成功的替换测试补断言「没有弹警告」）。
> **驳回 2 条**：kody 再次要求「导出目录必须在仓库外」与「写盘期间禁用整窗」——理由与上一轮相同（约束针对原始包与生成物；`jobs` 门闩已串行化，禁整窗会让自动校验假死）。
> **实测**：新增 5 项（不完整稿补齐后 F5 绑定并写包、绑定源＝规范化路径、全字匹配/区分大小写的在文件中替换、策略排除的 1288 不读不写、写失败不留半截文件），
> `test_gui_reform.py` 共 42 项；复跑 **524 项 OK（59 跳过）**、`ruff` 0、`docver` OK、`wincompat` 0/0/0。
> **未验**：仍是本机单测；Windows 实机、真实双编译器、游戏内表现未验收。
> 
> **2026-10-28：PR #95 审查复核，第三轮（针对 `2e662f4` 的新意见）**：7 条行级（gitar 1 + kody 3 + CodeRabbit 3）逐条复核——
> **5 条属实已修、1 条驳回、1 条属测试规范已照办**。其中一条是**我自己上一轮引入的新缺陷**：
> ① **有界扫描不报告截断**（gitar + CodeRabbit + kody 三家同报）：上一轮给 `replace_in_files` 加匹配上限时直接 `return ranges`，
> 超过 10000 处就**只改前面那些**、然后照常报「已替换 N 处」——一个大模块里 `x`/`self` 这种短词很容易撞上限，文件被改一半还没人知道。
> 现在 `text_matches()` 返回 `(ranges, complete)`；任一文件不完整就**一处都不改**，状态栏写「超过 10000 处，为免只改一半，未做任何替换；请用更长的查找文本缩小范围」。
> 顺手把同类的**在文件中查找**也统一了：它原本用 `text.find` + 硬编码 5000 上限，既无视「区分大小写／全字匹配」又不说明截断——现在走同一套 `search_flags()` 与同一套完整性标记，结果页和状态栏都会写「已到 N 处上限，结果不完整」。
> ② **磁盘满时不该丢下后面的条目**（CodeRabbit）：上一轮的 `ENOSPC` 直接 `break`，导致 `entries_written` 与 `entries_total` 之间出现**沉默的空档**——失败的临时文件已经删掉，空间可能是被大条目一次吃掉的，后面的小条目其实写得下。改成记完失败继续，manifest 里逐条有据。
> ③ **`manifest.json` 也要原子写**（CodeRabbit）：条目已经改成临时文件+改名，清单还是 `write_text`，中断会留下一个「看起来像真清单」的半截文件。现在共用 `_write_bytes()`；清单确实写不进去时报「已写出 N / M 条 + 目录 + 可先移走再重试」。
> ④ **测试规范**（kody）：成功的 F5 写包测试补断言 `QMessageBox.warning` 调用 0 次。**顺带修掉一个自己写错的测试**——上一轮那条全字匹配测试没注意「区分大小写」默认是勾上的，
> 断言「`X` 不被替换」其实是靠默认勾选通过的；现在显式分两轮：不区分大小写时 `x`/`X` 都替换、`max` 不动；区分大小写时只改小写那处。
> **驳回 1 条**：kody 第三次要求「写工作副本期间禁用整窗」——`jobs` 门闩已把任务串行化，禁整窗会让打开条目时的自动校验假死，理由与前两轮相同。
> **实测**：新增 4 项（超量匹配拒绝且一处不改、在文件中查找报截断、清单写不进去报部分结果、磁盘满后继续写后续条目），`test_gui_reform.py` 共 46 项；
> 复跑 **528 项 OK（59 跳过）**、`ruff` 0、`docver` OK、`wincompat` 0/0/0。**未验**：仍是本机单测。
>
> **2026-10-27：脚本编辑器 0.6.0.dev12 + PR #93 审查复核（分支 `arena/0186dc92-mxsj-tw-2022`）**：
> 用户要求「写包像 UI 编辑器那样有严格／宽松两种模式」，经 ask_user 确认四点后落地 **宽松模式**
> （`Ctrl+S` 一步到位；覆盖前留固定名 `<包名>.fls.bak` 只保最近一份；范围＝任何已打开的包，
> 包在客户端目录内每次额外确认；批量＝同一包内所有已绑定且变动的条目一次写回，上限 64 条）。
> 只放开「写到哪儿」，写前编译/审计/原生往返回读、写后整包独立回读与摘要核对一个没省；
> **默认仍是严格模式**。随后 PR #93 收到 **19 条 AI 审查意见**（gitar-bot 2 + CodeRabbit 10 +
> kody-ai 7；去重后 **15** 个问题，4 个被两个 bot 各自独立提出）：**14 条属实已修，1 条驳回**
> （kody 要求取消宽松模式，与用户已拍板的决策冲突）。
> 修掉的要点：① 探针可能比全量更严（拒绝阈值改为 `max(96×0.5, 全量容差)`）；
> ② 缓存命中的 `excluded` 恒为 0（改按 `verdict.failures` 计算）；③ `raw_source` 沿用 4 MiB
> 预算，会把 worker 刚成功产出的 4–8 MiB 模块判成「无效诊断」（改用 8 MiB 源码预算）；
> ④ `timeout/output_limit/cancelled` 不再进会话缓存，一次超时不会变成整会话永久失败；
> ⑤ 字面量里的成对转义不再提前闭合（**悬停与高亮因此自相矛盾**，实测 `x = '\xa5u\''`
> 有读法但高亮为空）；⑥ `\0` 后接八进制数字被读成 NUL+明文（`'\012'` → `b'\x0012'`）；
> ⑦ `r`/`u` 前缀给出假 cp950 读法（`u'…'` 本是文本，`'\xa5\xaf\033[0m'` 读出终端垃圾）；
> ⑧ `scan()` 达到 4096 上限或分词提前停止时只返回短列表、不说明（新增 `ScanResult.complete/reason`）；
> ⑨ 备份后不校验 `.bak` 摘要（TOCTOU，现改为不符即删除该副本并放弃覆盖）；
> ⑩ `payload` 完全相同的写回仍抛「没有需要写回的改动」（改为空计划 + 状态栏说明并刷新基线）；
> ⑪ `MAX_LOOSE_ENTRIES=64` 因早返回**从未生效**（改到对话框之前无条件执行）；
> ⑫ 宽松写回直连 Qt `triggered`，异常逃逸槽（改走 checked 包装进 `self.fail`）；
> ⑬ Windows 上自身持有的读句柄会让 `os.replace` 共享冲突（写前关闭、失败/空计划后重开）；
> ⑭ 方案文档 §5 的复现脚本替换 `validate_engine` 后不还原（补 `try/finally`）。
> **实测（Linux 3.11.2 / 无 Qt 运行库 / 合成包夹具）**：单测 **482 项通过 / 121 跳过 / 0 失败**
> （本轮新增 21 项，含 6 MiB `raw_source` 通过而 8 MiB+1 拒绝、探针边界、缓存 `excluded`、
> 备份摘要不符、空计划语义、`\012` 与转义引号）；`ruff check script_editor` 全绿；
> 宽松写回单次 I/O ≈0.2 s（`write_script` 0.07 s + `.bak` 0.01 s + `os.replace` 0.05 s）。
> **未验**：Windows 实机（含游戏占用原包时的换名失败路径、句柄释放是否真的够了）、真实双编译器
> 端到端写回、Qt 交互观感（本沙箱缺 `libGL.so.1`）、写回后的游戏内表现——测试通过 ≠ 原生验收。
> 锁定输入 `data/script.fls` `8b6e9266…c0d72`、`tools/decompiler/script_fls_keys.json`
> `43bb090d…daceb` 全程只读未变（所有写回测试都在 `/tmp` 副本或合成包上）。


> **2026-10-27：PR #92 的 AI 审查复核（分支 `arena/797802ec-mxsj-tw-2022`）**：PR 开了 **14** 条 AI 审查意见
> （gitar-bot 3 条 + CodeRabbit 6 条 + kody-ai 5 条；去重后 **12** 个问题，其中 4 个被两个 bot 各自独立提出）。
> **逐条对照代码核实后：12 个问题全部属实、已全部修好。**
> **其中 2 条我在复核时一度误判**：ReDoS 那条我先驳回了、后来证明**是错的**（基准测法有问题，
> 详见 ⑨），同义反复断言那条也是我先漏掉、后来才补上。
> **① 属实且严重（gitar-bot）——「内容丢失」回归测试已失效**：`test_every_original_line_survives` 原来用
> `git show HEAD:docs/STATUS.md` 当拆分前基线，但**拆分本身已被提交后，HEAD 里的 STATUS.md 就是拆分后的
> 381 行版本**，测试变成拿新文件跟它自己比、永远通过，再也抓不到内容丢失。已把基线钉死到
> `PRE_SPLIT_REV = "bc69491"`（最后一次仍含 4,334 行完整 STATUS.md 的提交），并新增
> `test_baseline_is_actually_the_pre_split_file` **自证**基线确实是拆分前那份（行数 >2000 + 含 §3 标题），
> 防止有人把基线改成分拆后的提交又静默失效。**反向验证**：现在从归档文件删掉一段真实历史正文，
> 该测试**确实报 FAIL**，恢复后全绿——修之前它抓不到（这正是意见的要害）。
> **② 属实（gitar-bot + CodeRabbit，两条重复）——测试漏跑 `scan_short_alias`**：CLI 跑 `scan_doc` **和**
> `scan_short_alias` 两个扫描器（后者抓**缩写形式**的声明，即同一行里用短名加版本号、
> 例如「当前资源 0.4.3」那种写法），测试只跑前者，
> 写成缩写形式的漂移会让 CLI 退出码 1 而 unittest 仍绿，**两个闸门口径不一致**。已让测试两者都跑。
> （顺带自证：补上第二个扫描器后，本条自己写的缩写示例立刻被闸门**报了出来**——
> 说明这道闸门是真在抓，不是摆设。）
> **③ 属实（CodeRabbit）——`--allow-missing` 是死代码**：该 flag 声明了但 `args.allow_missing` **从未被读**，
> 帮助文本说「缺失时只跳过」而实现里跳过是**无条件**的；且 README 没写这个 flag。已**删除该 flag**，
> 改为把被跳过的组件**打印出来**（新增 `find_skipped_components()`，同时写进 `--json` 的 `skipped_components`）——
> 组件被改名／删除会**静默**退出闸门，文档里残留的旧版本号就再没人查，这个洞必须可见。补 3 项回归。
> **④ 属实（CodeRabbit）——测试跳过缺失文档**：原 `if not path.is_file(): continue` 会让 README 被改名后
> 闸门因「没东西可查」而**静默放行**。已改为**判失败**（`assertTrue(path.is_file())`）。
> **⑤ 属实（CodeRabbit）——README 保存模式承诺自相矛盾**：§8.2 第 386 行写了宽松模式「直接改写布局所在原包
> （不留备份）」，第 392 行却无条件承诺「「保存回资源包」生成新包、**原包不动**」。照后者操作可能覆盖源包。
> 已在后者加上限定：「**严格模式**下……；**宽松模式下改为直接改写布局所在的原包，不留备份**」。
> **⑥ 属实（CodeRabbit，小）——量词搭配**：「101 **张**客户端地图语料」→「101 **份**客户端地图语料」
> （README 两处、ROADMAP 一处、AGENTS 一处，共 4 处；`docs/STATUS.md` 里 2026-10-23 那条**历史**记录
> 写的是「101 张客户端 `.map` 地图」，讲的是文件本身、不在本次改动范围，**未动**）。
> **⑦ 属实（CodeRabbit）——一条同义反复的断言**：`test_alias_keys_have_no_underscore_collision` 写成
> `set(ALIASES.values()) & set(COMPONENTS.keys()) & set()`，末尾 `& set()` 让它**恒等于空集**、永远通过；
> 且 docstring 描述的检查与代码**不是一回事**（代码比的是 alias 的**值**，而 `ALIASES.values()` 按设计
> **就是**组件键）。已改成真正要查的不变量：**别名键**（`ALIASES` 的 key，即文档里可能出现的写法）
> 不得与**组件键**撞名——撞名会让同一段文字被两个扫描器各匹配一次、产生重复 findings；
> 另补「别名键不得含下划线」与「同一别名不得指向两个组件」两条。**反向验证**：注入真实冲突
> （别名键 `ui_editor`、别名键 `ui_ed`）后两条**确实报 FAIL**，恢复后全绿——修之前它们不可能失败。
> **⑧ 属实（CodeRabbit）——`subprocess` 未指定编码**：`text=True` 在 Windows 上会按**本地代码页**解码
> UTF-8 的 STATUS 内容，代码页外的字符会让 devkit 测试在比对**之前**就失败。已按建议加 `encoding="utf-8"`。
> **⑨ 属实（gitar-bot + CodeRabbit）——`_CONNECT` 指数回溯（ReDoS）——**先记一个教训：
> **我第一轮复核把这���判成「不属实」并驳回了，是错的。** 错在**基准测法**：
> 我当时写的是 `pat.finditer(s)` **但不消费迭代器**，而 `re` 的匹配是惰性的——
> 不遍历就不会真正执行匹配，测出来永远是「0.000 ms」。**必须真的消费**
> （`sum(1 for _ in pat.finditer(s))`）才会付出回溯的代价。gitar-bot 与 CodeRabbit
> 的结论**是对的**，此处向两位致歉。改用消费式计时后实测 `_decl_re`：
> n=12 → 13 ms、n=14 → 53 ms、n=16 → 208 ms、n=18 → 740 ms、n=20 → **2,979 ms**
> ——**每多 2 个空格耗时 ×4**，是教科书级的指数回溯（成因：「分隔符可选 + `\s*`」
> 让一段 n 个连续空白有指数多种等价切分，匹配失败时引擎把这些切分**全部回溯一遍**）。
> **已修**：`_CONNECT` 改为把「可省略的标点」与「空白」**合并进同一个字符类**
> `[\s*/／`~（）()\[\]【】,，、:：—\-]*`——每次重复至少消耗 1 个字符，空白**只能**被
> 唯一一处吃掉，**不存在二义切分** ⇒ 回溯次数线性。实测 n=20 从 2,979 ms → **0.018 ms**，
> n=100,000 也只要 7.8 ms。`_short_decl_re` 同一形状（可选分隔符 + `\s*`）虽是**二次**而非指数
> （n=160 约 10 ms），也一并改成字符类（n=160 → 0.28 ms）。**语义保持**：原先
> `_decl_re` docstring 承诺的 5 种写法（`` `ui_editor`，0.21.0 ``、`` `ui_editor/`，**0.21.0** ``
> 等）逐条实测仍能匹配。**副作用**：整套 devkit 测试从 **8.1 s → 0.49 s**，闸门全量扫 3 份文档
> 从分钟级降到 **58 ms**。已加 `test_no_exponential_backtracking` 回归
> （**消费式**计时，n=40/400 各测一次，超 0.5 s 即失败）。
> **⑩ 属实（kody-ai）——表格里的版本号没人管**：组件能力表里组件名与版本号通常**不在同一单元格**
> （README 的 UI 编辑器行：名字在 cell[1]、版本在 cell[3]，中间隔着描述文字），
> 而正文路径的 `_CONNECT` **跨不过单元格分隔**，这类行**完全没人管**——「表格里写错版本号」
> 能直接溜过闸门。已加 `_table_row_scan()`：**按单元格**处理，组件名在某单元格、
> 版本号在**同一行**后续单元格即算一次声明（限定同行 ⇒ 不会跨行误配）。
> 另排除两类**非**版本声明：依赖/解释器要求（``Python 3.10+``、``SQLite >=3.24``）
> 与章节号引用（``§3.15.9``）。**反向验证**：把 README 的 ``**0.21.0**`` 改成 ``**0.8.4**``
> 后闸门**确实报出** `README.md:78`。
> **⑪ 属实（kody-ai）——缩写形式不认粗体**：`_short_decl_re` 只允许空白/斜杠，
> 认不出仓库里的实际写法 ``当前资源 **0.4.3** / UI **0.21.0**``（`README.md:365`），
> 于是这一行**完全没人管**（旧版单测的样例恰好省掉了 `**`，所以测不出来）。
> 已允许短名与版本号之间夹 **markdown 粗体标记**，并把单测样例换成**真实**写法。
> **⑫ 主动发现并修复（拆分轮遗留）——锚点重名**：`docs/archive/STATUS_HISTORY.md` 里
> master 并行工作记录区的 `### 3.30` 与主线的 `### 3.30` **共用**了锚点 `s3-3-30`
>（92 个锚点里只有 91 个唯一）。重名锚点会让**后一个**同名小节的链接指不到
> ——而「锚点存在」的检查是**通过**的（它只查存在性），所以这类缺陷能一直藏着。
> 已把并行区那个改为 `s3-master-3-30`（与该区「章节编号为各工作线原有历史编号」的语境一致），
> 并新增 `test_anchors_are_unique` 专查重复。**反向验证**：把锚点改回重名，该测试**确实报 FAIL**，
> 恢复后全绿。**未验**：`s3-3-30` / `s3-master-3-30` 目前**没有任何外部链接指向**
> （已全仓 grep 确认），所以改名不影响既有链接。
> **实测**：`tools/devkit/tests` **94 项全过**（本轮 +13：基线自证 1、跳过组件 3、别名不变量 2、
> 锚点唯一 1、表格扫描 4、粗体缩写 1、ReDoS 回归 1）；
> `server/tests/architecture` **161/161 OK**、`local_server` **68/68 OK**（回归未受影响）；
> `check_doc_versions.py` **0 漂移**、退出码 0；`ruff check tools/devkit` **0 报告**；
> `check_windows_compat.py tools/devkit` **0/0/0**；改动文件链接全检 **0 断链、0 缺锚点**。
> **未验 / 边界**：本轮仍**只动文档与只读工具/测试**，不碰产品代码、不改既有测试期望、不动原包；
> `PRE_SPLIT_REV` 钉的是**具体提交 SHA**，浅克隆取不到时该测试会 `skipTest`（不静默通过）；
> Windows 实机未验（本轮无 GUI 改动）。锁定输入 `data/script.fls` / `tools/decompiler/script_fls_keys.json`
> 以 `sha256sum` 核对与预期一致（`8b6e9266…c0d72` / `43bb090d…daceb`），本轮前后均未改动。

> **2026-10-27：STATUS 瘦身——历史轮次归档（分支 `arena/797802ec-mxsj-tw-2022`）**：上一轮修完文档漂移后，
> `docs/STATUS.md` 仍有 **4,334 行 / 537 KB**，其中**只有约 320 行是当前状态**（§1 分支与集成、§2 组件状态与实测、
> 顶部按日期倒序的轮次条目），其余约 4,010 行全是历史轮次记录——这正是「文档与项目实际进展脱节」的**结构性成因**：
> 读者要滚过几千行历史才能到达现状，新成员与 Agent 的检索成本极高。
> 本轮按用户要求「单独一轮做」，**只做搬运与链接修正，不改任何历史正文**。
> **拆分**：按项目已有的归档约定（`docs/archive/README.md` 第 2 条：`git mv` + 横幅 + 修链接 + 登记索引），
> 新建 `docs/archive/STATUS_HISTORY.md`，原样收走 §3（红灯与已知问题 **3.1–3.82**）、§4–§7
> （等待外部输入／下一步／最近变更／如何更新）与历史轮次条目；`docs/STATUS.md` 收到 **341 行**，并在 §8 写明归档去向。
> **原 §编号未改**（3.1、3.49、3.79 等一律保持），另给 92 个 §3.x 小节加了**显式 HTML 锚点** `s3-3-x`
> （不用 GitHub 风格 slug——那些标题含大量中文与符号，slug 又长又脆）。
> **链接改写**：仓库里 **33 处**指向已搬走小节的引用逐条改指归档文件，分三类分别处理——
> ① Markdown 链接 ``[STATUS §3.5](STATUS.md)`` → ``[STATUS_HISTORY §3.5](archive/STATUS_HISTORY.md#s3-3-5)``（相对本文件）；
> ② 反引号代码跨里的路径 `` `docs/STATUS.md` §3.49 `` → `` `docs/archive/STATUS_HISTORY.md` §3.49 ``；
> ③ 纯文本 `STATUS§3.51` → 带链接的 `STATUS_HISTORY §3.51`。
> **首版曾造出嵌套链接**（链接里套链接）与**被反引号包住的假链接**，
> 已 `git checkout` 回退重做——教训：这类改写**不能一刀切正则**，必须按上下文分三类。
> **归档文件内 36 条相对链接**因内容下移一层（`docs/` → `docs/archive/`）而失效，已逐条按 `../` / `../../` 修正。
> **顺带纠错**：`docs/DECOMPILE_CORPUS.md`、`notes/opcode_mapping_and_decompilation.md`、
> `tools/decompiler/output/script_fls_pycdc/README.md` 三处把「回编译管线」指向 `STATUS` 的 §5.2 ④——
> **STATUS 从来没有 §5.2**（其 §5 是「下一步（优先级）」），该引用实指
> `docs/PYTHON_TOOL_CONVENTIONS.md` §5.2（人工清单「剥掉模块顶层那个 return」），
> 属**长期笔误**，已改指正确文档。这三处**不是**本轮拆分造成的 casualty。
> **新增回归**：`tools/devkit/tests/test_status_split.py` **11 项**，把三类静默损坏钉住——
> ① 内容丢失（逐行归一化比对拆分前的 `git show HEAD:docs/STATUS.md`，**4,334 行原文零丢失**，
> 唯一 1 行措辞微调已在测试里显式登记例外并写明理由，新增例外必须写理由不能默默放宽）；
> ② 链接断裂（归档文件与 STATUS 各自的相对链接全部落地）；③ 锚点失效（每个 §3.x 都有 `s3-3-x`，
> 且仓库里所有指向归档文件的锚点链接都能命中）。
> **反向验证**：人为①删锚点 ②改坏归档内链接 ③删正文行，三种破坏**分别被对应的测试抓到**，
> 恢复后全绿——证明这不是「永远通过」的摆设。
> **实测**：`tools/devkit/tests` **81 项全过**（原 70 + 新增 11）；
> `server/tests/architecture` **161/161 OK**、`local_server` **68/68 OK**（回归未受影响）；
> `check_doc_versions.py` 对 README／AGENTS／STATUS **0 漂移**（拆分后仍绿）；`ruff check tools/devkit` **0 报告**；
> `check_windows_compat.py docs` **ERROR 0**（4 个 WARNING 全在 `docs/analysis/evidence/pyside6_6120_refcount_bug_20261026/`
> 冻结取证工件上，**本轮未触碰**，非本轮引入）；改动文件链接全检 **0 断链、0 缺锚点**。
> **未验 / 边界**：本轮**只做文档搬运**，不碰产品代码、不改任何测试期望、不动原包；
> §1–§2 与顶部轮次条目按用户选择**保持原样**（§1 仍是 2026-10-26 UI 编辑器轮的快照，另有横幅标注不是实时值）；
> 未在浏览器里点开每个锚点实测跳转（GitHub 渲染行为未验，但锚点为标准 HTML `<a id>`，Markdown 渲染器通用支持）；
> Windows 实机未验（本轮无 GUI 改动）。锁定输入 `data/script.fls` / `tools/decompiler/script_fls_keys.json`
> 以 `sha256sum` 核对与预期一致（`8b6e9266…c0d72` / `43bb090d…daceb`），本轮前后均未改动。

> **2026-10-27：顶层文档漂移对齐 + 防复发闸门（分支 `arena/797802ec-mxsj-tw-2022`）**：用户指出「有些文档与项目实际进展已经脱节」。
> 本轮**只动文档与新增一个只读检查工具**，不碰产品代码、不改任何测试期望、不动原包。
> **问题是真的，且有一处最严重**：`AGENTS.md` §7「已知坑」写着「GIRB 在 1034/1035 固定样本中仍有 300/429 扇区解不出」——
> 而 `map_editor` v1.0.0（2026-10-23）**已全量解决**：在 101 张客户端 `.map` 语料上 GIRB **11,763/11,763 零失败解出**。
> 一份红线级「长期有效」的接手指南里，把**已解决的问题写成未解决**，任何人照它判断都会出错。
> **已修的事实性错误（7 类）**：① `AGENTS.md` GIRB 条目（补历史／现状分界，并写明 101 图语料不随仓库分发、「全量」只指该次语料）；
> ② `README.md` 地图编辑器行 GIRB 缺口；③ `README.md` §1.3 硬编码基线 `cb2409a`（PR #51）→ 改为「§1–§2 是那一轮的快照，判断当前集成状态用 `git log`／`gh pr list`」；
> ④ `README.md` UI 编辑器 0.8.4 → **0.21.0**（3 处）；⑤ `README.md` 脚本编辑器 0.6.0.dev7 → **0.6.0.dev9**（3 处）；
> ⑥ `README.md` §7.3「GIRB 覆盖率仍有缺口」整段 → 改为当前结论（保留当年去「假成功」的纪律与「语料不随仓库分发」边界）；
> ⑦ `docs/ROADMAP.md` 阶段 E 验收条件里的 1034/1035 旧统计（改写为「历史缺口已取代，但仍不能推广为任意地图覆盖」）。
> **`docs/STATUS.md` §1** 加「本表是 2026-10-26 UI 编辑器轮的快照，不是实时值」横幅与时效性说明，并把该表头改成「当时核实值」、
> 「PR #90 已开、未合并」补注「后于 2026-10-26 11:27 UTC **已合并**」——**不伪造**该轮的分支／起点为「当前」。
> **方案 C（能力描述对齐）**：`README.md` §8.2 UI 编辑器整节重写，补 0.12–0.21 的实际能力
> （画布移动手柄、保存模式严格／宽松、打开／保存／另存为／导出副本重新划分、批量导入布局、
> 资源浏览窗、`.igs`／`.spr` 导入、新建拼名族、图像批处理含 0.21.0 磁盘独立入口、原生 schema 警示）；
> §8.4 脚本编辑器补 dev9 的「未登记包逐条严格解码自动判定」判定变化与实测数字。
> **方案 B（防复发）**：新增只读工具 `tools/devkit/check_doc_versions.py` + 23 项回归 `tools/devkit/tests/test_doc_versions.py`——
> 从各组件 `pyproject.toml` 的 `[project].version` 读真实版本，比对 README／AGENTS／STATUS 的**当前态**版本声明。
> **关键设计**：`docs/STATUS.md` 按设计保留大量历史轮次记录（「UI 编辑器 0.19.0」是当时那版的标题，**是正确事实不是漂移**），
> 所以工具按 ① 行内日期前缀 ② `### 3.xx` 编号历史章节整段 ③「以下保留历史内容」横幅段 三类规则跳过历史叙述，
> 加 `--no-exclude-history` 可严格全量比对。首版曾把 35 条历史记录误判成漂移，逐条定位后收敛到 0——**回归测试钉住「能抓到漂移」也钉住「不误伤历史」**。
> **AGENTS.md §7 新增长期规则**：顶层文档的版本号不许手工维护，改组件版本后同轮同步文档并跑该检查（退出码 1 = 漂移，要改文档不是放宽检查）。
> **实测**：`tools/devkit/tests` **70 项全过**（含新增 25 项；用 Pillow 13.0.0 环境复跑，`test_sprite_parity` 需 Pillow 非本轮引入）；
> `ruff check` 对本轮两个新文件 **0 报告**（ruff 0.17.3）；`check_windows_compat.py tools/devkit` **0/0/0**（文件名 14 项、扫描 13 个）；
> `server/tests/architecture` **161/161 OK**、`local_server` **68/68 OK**（回归未受影响）；
> `check_doc_versions.py` 对真实仓库 **OK 0 漂移**；另做**反向验证**——人为把 README 两处改回 0.8.4，检查器确实报 2 处 ERROR 且退出码 **1**，
> 恢复后退出码 **0**（证明闸门不是「永远通过」）。**未验 / 边界**：该工具只做**静态字符串比对**，
> 不判断某段版本叙述是否**过时**（过时仍需人工看）；GIRB「全量」只指 2026-10-23 那次 101 图语料，**本轮未重跑地图语料测试**（语料在仓外）；
> Windows 实机未验（本轮无 GUI 改动）。锁定输入 `data/script.fls` / `tools/decompiler/script_fls_keys.json`
> 以 `sha256sum` 核对与预期一致（`8b6e9266…c0d72` / `43bb090d…daceb`），本轮前后均未改动。

> **2026-10-26：保护壳入口的 Unicorn 执行探针（分支 `arena/4d3d51ac-mxsj-tw-2022`）**：新增研究专用工具 [`tools/dyprot_unpack/`](../tools/dyprot_unpack/README.md)（`dyprot_emulate.py` + `fake_modules.py` + `win32_env.py` + 14 项回归）。做的事：把 `mxmain.dll` 整个映射进 Unicorn（i386），TEB/PEB 摆在地址 0（unicorn 32 位**忽略 FS 段基址**，`fs:[x]` 实际读 `[x]`），给 859 个导入槽接 Python 桩，并**合成 kernel32/ntdll/user32/advapi32 的假 PE 映像**（含可解析的导出表）——因为实测壳是走「解析导出表」拿 API 的。**已确认**：① 给对导出表后，壳会把 **859/896 个 IAT 槽**重写成假导出表的地址（IAT 有 3,430 字节被改写，映像其余部分零改动）；② **没有任何载荷解密**——`.data` 运行期尾部 `0x93C180`（27 个 `interface` 类型的 `tp_name` 就从这里 `strcpy` 出去）全程为 0，`_dyprot0/1` 一字节未改。**过程更正（同轮，AI 审查发现）**：早期报告的「停因 `eip=0xb40a2330`」其实是**工具自己的 bug**——假 kernel32 等映像的导出表 `AddressOfFunctions` 存了绝对地址（PE 要求 RVA），壳算 `ImageBase + RVA` 正好落到 `0x54080000 + 0x60022330 = 0xb40a2330`。改成写 `位址 - ImageBase` 后，壳的行为立刻变了：它正常解析到桩上、`LocalAlloc(0, 0xa8)`、`GetModuleHandleA("ntdll.dll")`、`GetModuleFileNameW`、`GetProcessWindowStation`/`GetUserObjectInformationW(UOI_NAME)`、`LoadLibraryA("wtsapi32.dll")`，然后**弹出一个消息框**：标题 `mxmain.dll`、正文 `Initialization error 3`（运行期才出现在栈上的字符串，静态映像里没有），关掉消息框后 `FreeLibrary("wtsapi32.dll")` → `ExitProcess(0xDEADBEEF)`，是壳自己的干净退出，不是失控跳飞。（同一轮又修了 `WTSSendMessageW` 的 arity：原型 10 个参数、原先写成 9，少一个 `Timeout` 会少弹 4 字节栈、`pResponse` 指错位置，收尾就表现成“跳进未映射地址 `0x9f594fe0`”——arity 写错的症状永远离原因很远；现在这条由回归测试钉住停因。）顺带把 DLL 入口按 `DllMain(hinst, DLL_PROCESS_ATTACH=1, 0)` 的样子调用（原先 `fdwReason` 读到 0），行为不变。`--trace-tail N` 可留下最后 N 条指令定位跳转来源；`UC_HOOK_CODE` 限定在桩区后同一流程 12.0 s → 0.8 s。仍未解出载荷：`.data` 运行期尾部 `0x93C180` 全程为 0、`_dyprot0/1` 一字节未改；已排除「缺 API 数量」与「异常未派发」，现在的说法是「壳判定初始化失败、走错误分支后跳飞」，失败代码 3 对应哪项检查尚未定位。**未验/边界**：只读原 DLL，不加载 Windows DLL、不联网、不写原档；模拟执行不是启动客户端；结论仍是「静态可得的 46% 已经挖完，剩下 54% 目前只有 Windows 上 `ReadProcessMemory` 转储一条稳路」。依赖 pefile 2024.8.26 + unicorn 2.1.4（缺依赖整档跳过，不影响普通测试）。锁定输入 `data/script.fls` / `tools/decompiler/script_fls_keys.json` 以及只读输入 `mxmain.dll` 以 `sha256sum` 逐项核对与预期一致（`8b6e9266…c0d72` / `43bb090d…daceb` / `637331b5…be424d`），本轮前后均未改动。不涉及原包、脚本或编辑器，无行为变更。

> **2026-10-26：mxmain 给脚本的原生接口清账（类型 + 方法 + 使用率，分支 `arena/4d3d51ac-mxsj-tw-2022`）**：新增 [`notes/mxmain_python_types.md`](../notes/mxmain_python_types.md)，一次把「引擎把哪些类和方法交给脚本」问到边界。**三条通道**：① `Py_InitModule4` 函数模块（82 处，上一轮）；② `.rdata` 静态 `PyTypeObject`（本篇新解：**189 个骨架**，按 CPython 2.5 字段偏移 `+0x0c` tp_name / `+0x54` tp_flags / `+0x74` tp_methods 判定，其中 **9 个引擎类**：`CNetClient`(36 方法)、`CIMShare`(19)、`CServerCommand`(9)、`CShadowObject`(1)、`CObjectCommand`(1)、`CWwiseEngine`/`CCefObject`/`CPopen`/`CPreloadObject`(0)——全部有明文 `tp_name`，`dict`/`list`/`unicode`/`file`/`set` 等 56 个标准类型同时整齐命中，构成扫描器自证）；③ **运行期构造**：紧邻 `CShadowObject` 的 **27 个同形骨架**（`0x7df7a0`–`0x7e0b20`，步长 `0xc0`，共享 `tp_new 0x4659c0`、各自独立 `tp_init`）的 `tp_name`/`tp_methods` 指向 `.data` 未初始化尾部（`0x82b4e0` 起，`va_to_offset()` 返回 `None` 就是「文件里是 0、加载后写入」的硬证据）⇒ `interface.CMapWalkerObject` 这类名字**静态拿不到**；同理脚本里还 `import` 了 `C_slot`/`C_sharemem`/`C_math` 三个**明文 0 命中**的模块 ⇒ 「21 个原生模块 / 322 个方法」是**下界**。**使用率**：681 个已反编译脚本（13.6 MB）按 `C_<模块>.<方法>` 限定名统计，322 个方法里 **81 个被引用、共 283 次**，**241 个零引用**；`C_sys` 独占 200 次（71%，`GetTime`×53、`GetObjects`×21、`IsKeyDown`×21、`LoadFile`×19），`C_imshare`/`C_asyncloader`/`C_object` 等按限定名 0 次——`C_object` 是因为它的属性是**类**（`CTextObject`/`CBaseObject`/`CDisplayLinkDirector` 等，163 处使用点）。**勘误 2 条（本轮推翻上一轮）**：`Process`/`ProcessServerCmd`/`Replay` 是原生类型 **`CNetClient` 的方法**，不是 `C_net` 模块的函数；`CNetClient` 的 36 个方法里**没有 `OnServerCmd`** ⇒ 上一轮的「同名两层会不会重入」**不成立**，脚本 `net.CNet.OnServerCmd(self,icmd)` 是纯 Python 父类调用。**回调链至此闭环**：`CNetClient::ProcessServerCmd` → `0x4ab870` 读 `[cmd+4]` 命令号 → 桥 `0x4576b0` → 脚本 `OnServerCmd(byte)` → 脚本用 `CServerCommand.GetCmd/Unpack*` 读包体。**实测**：纯静态、只读（纯静态、只读；本 PR 新增只读工具与回归测试，但不改动既有工具行为，`ruff` 与 `check_windows_compat` 结论与上一轮相同）；`sha256sum` 逐项核对锁定输入，结果与预期一致：`mxmain.dll` `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`、`data/script.fls` `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`、`tools/decompiler/script_fls_keys.json` `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`。**未验 / 边界**：`tp_getset`/`tp_members` 未解；97 个无名骨架未逐个归类；语料只 681/5,135，「零引用」≠ 没人调；27 个 `interface` 名字「源自 RTTI」是**推断**（写入方应在 `_dyprot*` 内）。**下一步**：真要拿这部分只剩「运行期 dump `interface.__dict__`」一条路，静态再挖收益接近 0。

> **2026-10-26：mxmain.dll「原生 → 脚本回调」清单结案（分支 `arena/4d3d51ac-mxsj-tw-2022`）**：把上一轮留下的「回调名表逐条核 xref」做完，新增结案笔记 [`notes/native_script_callbacks.md`](../notes/native_script_callbacks.md)。**桥只有一支**：`int bridge(PyObject *obj, const char *name, const char *ret_fmt, void *ret_slot, const char *arg_fmt, ...)` 在 `0x4576b0`——取方法 `0x4d7240`、组参调用 `0x457e60`、失败报 `"{} 函数无法获取"`（`0x6b2434`）/`"Can't get method:{}"`（`0x6b2448`）并返回 `-1`。**`.text` 里指向它的 `E8` 调用恰好 16 个（穷举）**，全部实名，分属 12 处宿主位置 / 2 个簇：walker 簇（`CSetDirection` 就是 `CWalkerObject` 家族的**虚表槽 22**，另有 `Stop`×2、`IsWalk`×2）与网络簇（`OnServerCmd`×4、`OnError`×4、`OnSpecialServerCmd`、`OnConnectFail`、`OnConnected`）。网络侧 `0x4ac590` 是**事件码跳表**（`0x4ac61c`），`10001`→`OnConnected()`、`10002`→`OnError("连接中断")`、`10003`→不调脚本、`10004`(`0x2714`)→`OnServerCmd(int)`——**把 2026-10-09 交接的 `0x2714` 说法钉死了**，`0x2714` 是事件码不是包 opcode。反方向同时量清：全镜像 **82 处 `Py_InitModule4`（`0x4e4850`）**，其中 **21 个引擎模块 `C_*` 共至少 322 个脚本可调方法**（下界）（`C_sys` 130、`C_audio` 42、`C_imshare` 27、`C_wwise` 24、`C_imnet`/`C_misc` 14…），其余 61 处是内嵌 CPython 2.5 标准库；另有第二类方法表（`0x7e0ca0`/`0x7e0e00`，`0x7e0c54` 处 `+0x54` 引用，判为运行期填充的自定义类型描述，未确证是 `PyTypeObject`）。**交叉结论**：1 跳内没有任何 `PyMethodDef` 直连桥，2 跳内只有 `C_net.ProcessServerCmd` / `Process` / `Replay` 三条会触发回调 ⇒ **脚本→原生与原生→脚本是两条独立通道**。**勘误 3 条**（已写进新笔记 §7）：`0x6b2434` 与 `0x6b2448` 是两个相邻槽、`OnConnected` 的签名是 `()` 不是 `(i)`、上一轮列的「引用点」其实是压栈位置。**实测**（2026-10-26 复审后重跑）：`python3 -m unittest discover -s tools/data-parser` **46 项 OK（3 跳过）**，其中 `test_mxmain_rtti` **22 项**（11 项自建最小 PE + 11 项真档断言）；`check_windows_compat.py tools/data-parser` 0/0/0；`ruff` 对本轮改动文件 0 报告（`tools/data-parser` 目录另有 82 条**既有**告警，全在未触碰的 `extract_dlg.py` 等，未处理）。锁定输入 `mxmain.dll` / `data/script.fls` / `script_fls_keys.json` 以 `sha256sum` 逐项核对与预期一致（`637331b5…be424d` / `8b6e9266…c0d72` / `43bb090d…daceb`），纯静态、未启动客户端、未监听端口、未改原包。**未验**：`0x6b020c` / `0x6b0228` 两个运行期函数指针槽静态解析不出（后者在事件码 `10003` 分支，可能决定「命令是否交给脚本」）；`C_http` / `C_RenderAgent` 的方法表未定位；`0x49d1xx`–`0x49d9xx` 是热/冷块无填充，宿主函数名未定；`_dyprot*` 内可能有更多调用点。下一步见新笔记 §8。

> **2026-10-26：mxmain.dll 明文 RTTI 解成类图（分支 `arena/4d3d51ac-mxsj-tw-2022`）**：新增只读工具 `tools/data-parser/mxmain_rtti.py`（标准库，22 项回归全过：11 项自建最小 PE 结构锁 + 11 项真档断言）与结案笔记 [`notes/mxmain_rtti_class_map.md`](../notes/mxmain_rtti_class_map.md)。对锁定输入 `mxmain.dll`（`sha256sum` `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`，与 `mx.exe` 同摘要）、`data/script.fls`（`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`）、`tools/decompiler/script_fls_keys.json`（`43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`）——三者前后均未改动——解出 **352 个 TypeDescriptor / 309 个类带 COL（329 条 locator）/ 305 张主虚表 / 1,769 个虚函数槽（另有 24 张次要虚表、149 槽，分布在 18 个类上）/ 309 条继承链（0 解析失败）/ 307 个类的 1,346 处写 vfptr 位置**；`_dyprot0/1` 那 54% 高熵段不参与，结论全部来自明文。实测坑七条已写进工具 docstring 与测试（含复审补的第 5 条：`mov [reg+disp], imm32` 的立即数不紧跟 `C7`，旧版只认 `c7 06` 漏掉 362 处/28%；现报 `site_va`=指令起始与 `imm_va`=立即数两个地址，并保留多重继承的次要虚表）：RTTI 指针是绝对 VA（不是 RVA）、BaseClassDescriptor 步长 28 B（不是 SDK 的 24，用 std 的五层继承链核过）、虚表尾部会接方法名字串（`ii` → `0x00696969` 假指针）、std 的 deleting destructor 入口是奇数地址 `0x5c6085`（对齐假设会砍掉 52 个类）。跨材料互证三条：`type_info@@` 虚表 `0x77cb64` 与 352 条 TD 的 vfptr 一致；`CLZWDecompress` 槽 1 = `0x4c5e40`（`notes/native_tcp_channel.md` 用原生模拟定出的 LZW 解压）、`0x4c5d50` 落在同类写 vfptr 位置。**衍生发现（未结案）**：原生→脚本回调名表在明文 `.rdata`（`0x6bb120` 起，`(i)`+`OnServerCmd`、`()`+`OnError` 成对），桥函数 `0x4576b0`（取不到方法时用 `Can't get method:{}` 提示串），已核 8 条名字的代码引用点；这修掉了「原生符号只能靠运行期探针」的一概而论。**未验**：Windows 实机与运行期对照；`_dyprot` 段内可能还有类；`mdisp=8` 等字段只记录不解释。不涉及原包、脚本、编辑器或 Mock，无行为变更。下一步见笔记 §9。

> **2026-10-26：UI 编辑器 0.21.0（图像批处理独立入口：磁盘进磁盘出）**（分支 `arena/f980d0df-mxsj-tw-2022`，起点 `eac25d9`＝0.20.0）：用户追问「要打开资源窗口才能打开图像编辑吗」——是的，0.20.0 的入口挂在浏览窗上，而浏览窗要先挂载资源包；经 ask_user 确认加独立入口（磁盘批处理）：不挂包、不打开任何布局也能用，挂了包时浏览窗入口与挂账能力照旧保留。① 工具栏「批图」分体按钮（与打开/另存为/导出副本同款：主按钮＝最常用那种，小箭头＝其它来源）：主按钮「选图片文件批处理…」（可多选，过滤器默认 PNG/JPG/BMP/TGA/.igs），小箭头「选文件夹批处理…」（**只扫文件夹顶层**不递归——范围可预期、免得误吞整棵大树；要处理子文件夹就再选一次它），两者都记住上次所在目录（独立 batch_dir 键，不踩打开布局的 last_dir 记忆）；② 参数/预览/清单与浏览窗完全同款——复用同一个 ImageBatchDialog＋run_batch（缩放三模式、亮度/饱和度 0–200%、首图前后对比预览、输出清单确认、永不覆盖重名 -2/-3、单项失败不中断整批）；③ 输出只能写磁盘：磁盘文件没有包内路径，「挂账进包」无从谈起，参数窗以 can_stage=False 构造（挂账单选钮置灰），执行链全程不碰资源解析器；④ 拒收规则同款：范围外后缀「xxx 不在批处理范围」、读不到「读不到文件（原因）」，能处理的照常进参数窗，拒收项最后并进失败清单一起报，成功走状态栏「图像批处理完成 N 张 → 写入 目录」。结构：AssetBrowserMixin 加三方法（batch_images_from_disk/batch_folder_from_disk/_run_disk_batch，纯宿主端不依赖包）、window_setup._build_toolbar 接分体按钮（590 行，≤600 护栏内）、icons.py 加运行时手绘 icon_batch_images（两张叠放照片＋调参滑杆）。**实测**：test_gui_image_batch.py 增 StandaloneDiskBatchTests 7 项（工具栏接线/没挂包端到端 200% 缩放真落盘＋原文件一个字节不动/拒收不中断整批/全拒收不开参数窗/取消静默/文件夹只扫顶层/空文件夹一句话提示）全过；全套 offscreen **932 项：931 通过 / 1 跳过 / 0 错误**（连续两轮）；ruff 0；check_windows_compat 0/0/0（166 文件名项、147 扫描）。本轮沙箱被重置：本地分支第三次回退（既有处方 fetch origin＋reset --mixed FETCH_HEAD 修复，工作区文件无损）；venv 先按惯例重建为 PySide6 6.12.0/Pillow 13.0.0/ruff 0.17.2，全套却在 ~841 项处**两次可复现硬崩**（exit 134，`Fatal Python error: bool_dealloc/none_dealloc`——True/False/None 单例被 C 扩展过度 DECREF）。取证多轮（逐测试 getrefcount(None) 追踪：854 项内 17185→2546、126 项负增量合计 −35438；崩溃点单模块隔离全过；放大循环探针逐操作定位）钉死**最小复现**：纯 QtCore、/proc/self/maps **零桩库加载**、信号**不做任何连接**，`Signal(int).emit(3)` 循环 2000 次即崩（`Signal(str)` 同崩；无参 `Signal()`、findChildren、裸 MainWindow 构造全干净）——即 **shiboken6/PySide6 6.12.0 在本沙箱 Python 3.11.2 上的信号实参转换 refcount bug**，与桩库、与本项目产品代码和测试代码均无关（旧沙箱镜像同版本 6.12.0 曾两轮全绿，差异疑为 Python 微版本，旧镜像已灭失无从核对；最小复现与取证脚本存档于 `docs/analysis/evidence/pyside6_6120_refcount_bug_20261026/`）。处置：**测试环境换装 PySide6 6.11.2**（满足产品依赖声明 `PySide6>=6.4`，产品与测试代码**零改动**），int/str/object 三路信号探针 delta 全零、`QSpinBox.valueChanged`×500 干净。新镜像比上轮精简（缺 libdbus-1/libEGL/libGL/libxkbcommon/libX11-xcb/libnss3/libgtk-3/libharfbuzz 等 81 个真库，且 Qt6 是 BIND_NOW 急切绑定，空桩直接 ImportError）——GL 桩升级为**带符号桩**并按 6.11.2 重生成：带版本符号按消费者 .gnu.version_r 归因＋版本脚本归位，无版本符号按 DT_NEEDED 归因进对应缺失库的哑实现（FUNC 返回 0/OBJECT 零初始化数组，排除 Py*/_Py*，shiboken6 纳入提供者扫描），81 库共 6312 个哑符号，导入链全通。**未验**：Windows 实机、图标与按钮真实观感（图标是运行时 QPainter 手绘，无像素级断言）。**AI 审查复核（PR #90，同日）**：gitar-bot、CodeRabbit、kody 的 12 条行级评论（10 个独立问题）逐条对照代码复核——**7 条属实已修、2 条属实但属冻结取证存档只加注不改工件、1 条前提不成立**——①移除自定义属性键误报「会随 .dlg 保存」警告（`_warn_nonnative_key` 加 `key not in widget.props` 守卫：键已不在 props 的移除操作静默）；②批处理预览全分辨率逐 tick 重算（预览改用 ≤360px 有界工作副本＋缓存 before 图，输出 >1280px 从略预览并标注真实尺寸「批处理照常执行」，`AdjustError`/`MemoryError` 捕获兜底文案）；③输出清单裸文件名与实际落盘重名 -2 后缀不符（`_predicted_name` 按 `unique_target` 规则预演、含批内已预演名的占用，注明执行时仍以落盘瞬间为准——不覆盖优先于预演一致）；④单选 .spr 连带挂账像素搭档后选中被搭档抢走（`_pair_spr` 成功连带后重选回 .spr 本体，属性模式下 OK 回写目标不再错位）；⑤`_batch_process` 取包内字节不设防、单项损坏即整批中止（逐张 `except Exception` 进拒收清单带原因，比照 `run_batch` 既有姿势——`PackError` 是 `UiEditorError` 子类，kody 建议的 `(OSError, ValueError)` 接不住）；⑥取证 README 闸门命令裸文件名无法从仓库根运行（改仓库相对路径并写明判定标准）；⑦sigprobe「没崩就无条件 PROBE-SURVIVED」判定不严（加强为**双窗口负 delta 判定**：任何窗口 true_delta<0、第 2 窗 none_delta<0、或第 1 窗 none_delta≤−10 → `PROBE-REFCOUNT-DRAIN` 退出码 1；第 1 窗吸收一次性常量噪声——干净版实测可现 ±1、+2；加强版在 6.11.2 复跑判定不变：全窗非负、`PROBE-SURVIVED` 退出码 0）。**存档不改 ×2**：refwatch 驱动的 `/tmp` 硬编码日志路径（CodeRabbit，CWE-377）与其对 `TestCase.run` 的补丁未恢复（kody）——两者都是冻结的一次性取证工件，按运行原样存档（驱动跑完即进程退出，进程内补丁无从泄漏影响后续执行；改写它们会让存档与 `reflog_854tests.txt` 的产出过程对不上号），已在取证 README 注明存档口径：sigprobe 是唯一可复用闸门。**前提不成立 ×1**：kody 建议 `test_gui_spr_add.py` 成功路径 7 处补「未出现警告对话框」断言——现有成功测试已精确断言挂账字典与提示文案逐字，所有失败分支文案不同（「未挂上」vs「连带挂账」），未打补丁的 `QMessageBox` 在 offscreen 下会阻塞造成响亮失败，不存在「弹框劫持而测试照绿」的路径。＋7 项回归测试，全套复跑 **939 项：938 通过 / 1 跳过 / 0 错误**（连续两轮）、ruff 0、wincompat 0/0/0（166 文件名项、147 扫描）。审查轮沙箱再次被重置（本地分支第五次回退、venv 与符号桩全灭、gen_stub 脚本丢失），按既有处方修复（fetch＋`reset --mixed FETCH_HEAD`，工作区改动无损）后重建 venv（PySide6 6.11.2/Pillow 13.0.0/ruff 0.17.2）并按存档设计重建生成器重生成符号桩：62 库/15 带版本库/6529 哑符号（重建版提供者过滤更严——系统真库已能提供的符号不再进桩，故库数与原轮 81/6312 不同；以导入链与全套两轮全绿为验收标准，非精确计数）。详见 `ui_editor/README.md` 0.21.0 节。

> **2026-10-26：UI 编辑器 0.20.0（图片批处理：缩放 / 亮度 / 饱和度）**（分支 `arena/f980d0df-mxsj-tw-2022`，起点 `d29cb0e`＝0.19.0）：0.19.0 结论「CButton 等控件游戏内尺寸与观感由图片素材自身决定」的直接后续——把改图工具配进编辑器。用户追问开源轻量图片处理选型并经 ask_user 确认四个决策点（入口＝浏览窗＋可挂账进包、操作＝最小三样缩放/亮度/饱和度、范围＝普通图片＋.igs 往返、预览＝首图前后对比＋输出清单确认）。选型**零新依赖**：Pillow 即轻量开源的标准答案（HPND 许可、已是 pyproject 正式依赖、精灵编解码管线一直在用、venv 实测 13.0.0），OpenCV（wheel 近 100MB）/scikit-image（拖 scipy）/ImageMagick-Wand（外部原生程序）/pyvips（LGPL 原生库）逐一比过不值当。① 浏览窗「批量处理…」按钮（浏览模式且宿主给 fetch_bytes 回调才出现）：多选后先过分筛——拼名族目录、范围外后缀（.spr 是帧时表没像素）、包内读不到字节的拒收并各给一句话原因；② 参数窗：缩放（不缩放/百分比 5–500%/目标尺寸，锁纵横比默认开＝装进目标框，LANCZOS、最短 1px）＋亮度/饱和度（0–200%、100%＝不变），首项前后对比预览（.igs 取第一帧）随参数实时刷新，输出清单逐条确认后才处理；③ **alpha 保真（核心坑）**：Pillow `ImageEnhance` 退化图 alpha=255，直接混合 RGBA 会把透明像素 alpha 拉向 255——精灵全靠透明像素定位，拉坏即观感全毁；实现拆 alpha 只增强 RGB、原样合回，专门回归钉死；④ .igs 往返：decode_sprite 逐帧解 RGBA→逐帧调整→encode_frames 重编码成**新** .igs（包内原容器一个字节不动），保真护栏两道——任一帧锚点非 (0,0) 拒收（编码只写 (0,0)，硬转＝悄悄挪帧）、魔数不在 I0/T0/I1 拒收（真彩 T4/T5/I4 能解不能编）；调色板按调整后像素重建：T0（RGB888）精确保色（测试钉死）、I0（RGB565）必有轻微再量化（容差断言、如实告知）；⑤ 输出二选一（原资源/原文件一律不动）：写磁盘目录（文件名沿用、**永不覆盖**、重名 -2/-3 后缀）或挂账进包（输出路径＝原包路径，同名＝保存时替换包内原资源——清单逐条标注、本窗一次性确认，走 `_stage_one(confirm_same_name=False)` 不逐张打断）；单项失败进清单不中断整批。结构：新零 Qt 核心 `core/image_adjust.py`（尺寸数学/模式归一/拆通道增强/格式与精灵护栏，全部可单测）＋ UI `ui/image_batch.py`（ImageBatchDialog＋run_batch）；image_picker 加 fetch_bytes 回调与 _stage_one 的 confirm_same_name 开关；asset_browser 接线 assets.fetch_bytes；pyproject Pillow 下限 9.0→9.1（Image.Resampling 枚举）、版本号 0.19.0→0.20.0。**实测**：新增 test_image_adjust.py 26 项＋test_gui_image_batch.py 18 项全过（含 alpha 保真回归、.igs 往返与锚点/魔数护栏、挂账/磁盘双模式执行链、浏览窗集成端到端）；全套 offscreen **925 项：924 通过 / 1 跳过 / 0 错误**（连续两轮）；ruff 0；`check_windows_compat` 0/0/0（166 文件名项、147 扫描）。**未验**：Windows 实机、预览与参数真实观感、.igs 重编码后游戏内表现（调色板再量化是格式规则推断＋沙箱实测，未跑客户端）。详见 `ui_editor/README.md` 0.20.0 节。

> **2026-10-26：UI 编辑器 0.19.0（属性行宽度互换 / 原生 schema 警示 / .spr 导入）**（分支 `arena/f980d0df-mxsj-tw-2022`，起点 `330479d`＝PR #89 已合并）：用户同日提三个问题并确认四个决策点后施工。第二项「CButton 的宽、高与自加属性画布生效、游戏无效」先诊断后动手：**非编辑器缺陷、是游戏端机制**——游戏端控件类按 dUIInfo 实例化只读原生模板字段集（游戏自带 UI 编辑器 script.fls entry 3853 widgetconfig，31 种类型与本编辑器模板逐字段静态对照相同，证据 `docs/analysis/evidence/widgetconfig_20261017/`；真包 5309 个 CButton 无一写宽高，游戏内尺寸由图片素材自身决定），多余键忠实保留但引擎不认；用户确认其他修改游戏内生效（排除保存管线）并拍板：**只警示不拦不改**、.spr **自动连带**磁盘同名像素搭档、多选规矩**与 .igs 相同**。① 添加属性行宽度互换：键下拉最小宽＝值输入框自然宽、值框最大宽＝下拉自然宽（构造时实测互换）；② 原生 schema 警示：属性面板写进原生字段集之外的键 → 状态栏直说「会随 .dlg 保存，但游戏会忽略它（只影响画布显示）」；画布缩放松手且动到的维度游戏不读 → 直说「该维度游戏内由图片素材自身决定（要改游戏内观感请改图）」。忽略表**逐维度**：CButton/CSpriteFrame/CTextFrame 宽高都不读、9 种横排读宽不读高、4 种竖排读高不读宽、15 种两个都读不警示，只挪位置不警示（此前「16 种类型不写宽高」系「宽高都缺」的粗化口径，本轮按维度校正）；新数据层 `core/defaults_data.py`（NATIVE_TYPES 31 种 / native_field_set——7 种外部模板返回 None 不妄下断语 / SIZE_IGNORED_NATIVE 逐型逐维度表），与证据 JSON 逐项互检；两个警示方法放 `ui/commands.py`（main_window.py 顶到 600 行护栏，移出后 595）；③ 选图窗「把图片放进包…」过滤器加 `*.spr`：.spr 是 XOR4 加密 INI 帧时表（不是图），单张按原字节挂账并自动连带磁盘同名 `.igs`（退 `.png`）像素搭档——已挂账/包内已有不重复并直说，找不到搭档直说「有帧表而无像素」，`[images]` 变体（像素指外部 .fls 包，官服 56 例中 2 例）点明不随本次导入；多张沿用 0.18.0 .igs 规矩（前缀＋原文件名＋确认清单），搭档在清单成行、已在本批选择不重复；与普通图片混选拒绝、与 .igs 混选允许。**实测**：新增 3 测试文件 31 项＋面板探针 1 项全过；全套 offscreen **881 项：880 通过 / 1 跳过 / 0 错误**（连续两轮）；ruff 0；`check_windows_compat` 0/0/0（162 文件名项、143 扫描）。沙箱 venv 与 stub GL 库本轮重建（PySide6 6.12.0）。**未验**：Windows 实机、警示真实观感、.spr 入包后游戏内表现（像素搭档规则为官服 56 例静态证据推断）。详见 `ui_editor/README.md` 0.19.0 节。

> **2026-10-26：UI 编辑器 0.18.0（.igs 导入 / 只保存新资源 / 画布移动手柄）**（分支 `arena/6180f8d3-mxsj-tw-2022`）：用户同日提三个问题并确认四个决策点（多 .igs＝目录前缀＋原文件名逐张挂账并列清单确认；浏览窗保存按钮＝跟随保存模式目标决议；写**全部**挂账且文案带计数；手柄＝绕过父矩形夹取与祖先选中冻结、吸附保留）后施工。① 选图窗「把图片放进包…」过滤器加入 `*.igs`：单张按**原字节**挂账绝不进精灵转换（转换勾选禁用），多张 `.igs` 按「目录前缀＋原文件名」逐张挂账（确认框逐行列出最终包内路径、前缀可改），与普通图片混选拒绝（与拼名族规矩一致）；② 浏览窗「保存新资源（N）」按钮：把全部挂账图片按保存模式写进包（严格＝编辑器输出包、没存过问一次路径成功后才记住；宽松＝就地写原包），**任何布局条目不读不写**；安全管线与 Ctrl+S 同款（编码闸门＋临时副本＋原位补丁＋原子替换**之前**回读校验＋成功才清挂账），新模块 `ui/staged_save.py`（StagedSaveMixin，基类清单与结构守卫同步更新），`patch_pack_copy_many` 允许 `layouts={}` 并修掉空布局 StopIteration，publish 校验链接受 `res_path=None`（「只写资源」形态：新图逐字节回读＋未改条目保真），成功后 `doc.source_pack` 迁移到写出包（否则下次 Ctrl+S 从原包重拷会悄悄丢掉刚写入的新资源）但不碰布局脏状态与待入包队列；③ 画布移动手柄：选中未锁定控件右上角**外侧**四箭头手柄（场景级顶层图元、zValue 置顶、重叠盖不住），按住拖动＝强制移动，绕过「夹在父矩形内」（子 ≥ 父时普通拖动冻死）与「祖先同时被选中」两大冻结成因（「长按没反应」根治），吸附保留（Alt 禁用）、松手记一步撤销、只搬被握控件；锁定无手柄照旧不能拖，普通拖动规则一字未改。**实测**：新增 3 测试文件 25 项（手柄 8、.igs 7、只存新资源 10）全过；全套 offscreen **841 项：840 通过 / 1 跳过 / 0 错误**（连续两轮）；ruff 0；`check_windows_compat` 0/0/0（159 文件名项、140 扫描）。沙箱 libGL/fontconfig 等 stub 库本轮重建（venv 亦重建，PySide6 6.12.0），teardown 偶发 abort 与基线相同。**未验**：Windows 实机、手柄真实鼠标观感、.igs 入包后游戏内像素级一致。**AI 审查复核（PR #89，同日）**：gitar-bot 与 CodeRabbit 的 8 条行级评论（6 个独立问题）逐条对照代码复核**全部属实**、全部修复——①添加属性下拉被 `addItems` 预选第 0 项永远预填首个候选键（`setCurrentIndex(-1)` 清掉）；②手柄不随父搬动级联选中的子孙、缩放走 `_syncing` 不经 `itemChange` 连自己也不跟（`_grip_follow` 级联＋缩放尾显式跟手）；③剪贴板坏负载粘贴半途抛 `ValueError` 中止、缺 `sWidgetType` 可混进 `.dlg`（递归校验＋状态栏兜底；CodeRabbit 注明属既有边界、非本 PR 引入，照修）；④「保存新资源」嵌套事件循环期间对话框可再点、两次写包赛跑同一目标（写包期间自我禁用，兼治 CodeRabbit 汇总的 lost-update）；⑤多 .igs 挂账把取消同名替换/被拒名字也计数（只计真挂上的）；⑥确认框回车＝是直通就地改写原包（默认按钮＝否，与切宽松模式同一套安全默认）。＋8 项回归测试，全套复跑 **849 项：848 通过 / 1 跳过 / 0 错误**（连续两轮）、ruff 0、wincompat 0/0/0。**复审轮（`526cf5e` 推送后）**：gitar-bot 改判 ✅ Approved（2 closed / 0 open）；CodeRabbit 复审追加 1 条 Minor——本文件 §2 轮次说明仍写 771 项、与组件行 849 项矛盾——**属实**（§1–§2 自称「唯一当前概览」却停在 0.16.0 轮，§1「0.16.0 尚未合并 master」亦过时：PR #74 已于 2026-10-22 合并），已把快照日期、§1 表、§2 轮次说明同步到本轮。详见 `ui_editor/README.md` 0.18.0 节。

> **2026-10-26：UI 编辑器 0.17.0（工具栏「资源」/ 添加属性下拉 / 属性中文名 / 剪切 / iAlign 对齐）**（分支 `arena/6180f8d3-mxsj-tw-2022`）：用户 2026-10-26 提五个功能并逐条确认语义与四个决策点（浏览窗＝复用选图窗除写回属性外全保留；候选集＝普查并集；按钮 iAlign＝九宫 0–8；顺手修文本类原生映射）后施工。① 工具栏「资源」按钮把选图窗当独立浏览器（看/导出/放进包/拼名族保留，「选完写回属性」移除、确定改「关闭」），图标照 `icons.py` 现画风格、未挂包给状态栏指引；② 添加属性名输入改**可编辑下拉**（候选＝47,139 控件普查键并集减当前已有，随选中刷新，手输保留）；③ 属性名悬停中文翻译：新零 Qt 核心 `core/prop_glossary.py`（原生表 39 繁体名＋普查 57 键简体释义，无依据不显示 tooltip）；④ 画布右键「剪切控件」+ Ctrl+X + 编辑菜单：进剪贴板＋走删除护栏、整组一步撤销、取消留副本；⑤ 按钮 iAlign 按原生新式九宫 0–8 即时移位（缺失保持历史画法），顺手把 `CTextFrame`/`CTextFrameEx`/`CRichTextFrame` 修回原生映射（`native_widgetconfig_comparison_20261017.md` §1 的「优先修」），属性面板 iAlign 按类型给具名下拉。结构：复制/剪切/粘贴拆到 `ui/clipboard.py`（ClipboardMixin，commands 顶到 600 行护栏）；导出处理函数提为 `property_panel.make_export_handler` 共用（既有测试补丁命名空间不变）。**实测**：新增 5 文件 34 项全过；全套 offscreen **816 项：815 通过 / 1 跳过 / 0 错误**（连续两轮）；ruff 0；`check_windows_compat` 0/0/0（155 文件名项、136 扫描）。**沙箱特有**：libGL/fontconfig 等为自编译空 stub，stub 环境 teardown 偶发 abort（基线同）、「表单内建 iAlign 下拉再重建」概率触发 stub fontconfig 堆崩——对应测试改为不建该下拉（覆盖率由形状测试保持）；真实 Qt 不走 stub 路径。**未验**：Windows 实机、像素级一致。详见 `ui_editor/README.md` 0.17.0 节。

> **2026-10-24：Windows 原生验收 + P0 两项根因修复（分支 `master`，工作树未提交）**：在本机 Windows 宿主完成 ROADMAP 阶段 B 工程层验收（报告 [`analysis/windows_acceptance_20261024.md`](analysis/windows_acceptance_20261024.md)，项目总览 [`analysis/project_analysis_20261024.md`](analysis/project_analysis_20261024.md)），并当场修复两类**只影响 Windows 开发者**的问题（Linux 检出即 LF，无此问题）：① **`vendor_core` 行尾敏感比对在 autocrlf 检出下自毁**——`load_text` 改 universal newlines、`test_write_is_idempotent` 改临时树夹具（不再写脏真实仓库）、新增 CRLF 检出回归测试；② **CRLF 字节钉伪影族**——`.gitattributes` 为 licenses / catalog jsonl / decompiler 产出与 `batch_decompile.py` / 管线工具源码 / csv_checks staging 与 `*.json` 等 8 处补 `-text`，686 个受影响文件重新签出（进程内复算 blob、逐文件验证归一化后与索引一致，`i/lf w/crlf` 残留 0）。附带修复 `map_npc_reproduction.py` 写 `provenance.json` 的平台依赖（Windows 文本模式 `\n`→`\r\n`）与 `bootstrap.py` E501。**复跑**：架构套件 **161/161 OK**（修复前 1 失败 + 1 错误）、`script_manual validate --verify-evidence --require-full-inventory` 通过（5135/5135）、catalog 34 / review_api 27 / `export_review_csv.py --check` 全过、devkit 45 测仅剩 WIN102 夹具 1 项既有 P2、script_editor 376 测 4 失败均为既有（3×TransportTests P2 + 1×包哈希钉 P1）且原 3 个 GPL 许可错误消除。**§6 人工复核项**：batch_001 manifest 因生成器修改重生，`map_npc_reproduction.py` 哈希行 `cc5e9349`→`7fe0d302`（单行 diff，全新导出与提交版 `diff -r` 亦仅此一行），提交信息须说明。**红灯（不在本轮范围）**：WinError 32 ×23、map_editor 路径分隔符、TransportTests ×3、WIN102 夹具、review_browser_acceptance 的 `python3`/`killpg`、mock_server_v2 `/tmp`、script_editor 包哈希钉 `a45e0e49` vs `8b6e9266`。**下一步**：用户复核 10 个真实修改与 manifest 单行后提交；P1/P2 按验收报告 §8 推进。详见 §3.82。

> **2026-10-23：地图编辑器 `map_editor` 升级至 v1.0.0（全量 101 图逆向实证 + 完整读写编译工作台）**（分支 `arena/651a26cf-mxsj-tw-2022`）：从 Google Drive `MAP/{map.zip,map.z01,map.z02}`（`267,799,770 B`）拉取并在仓外解压校验全部 **101** 张客户端 `.map` 地图（`11,763` 扇区、`20,036` 前景遮罩），结合 `mx.exe`（`0x0060ea90` `LZO1X-1`、`0x00637420` `GEPJ`、`0x004bac30` `CAStar`）与 `data/script.fls` 交叉验证，彻底修复 `v0.1.0` 的 `GIRB` 解压失败（`60/101` 张图报错 → **11,763/11,763 扇区 100% 解出**）、`rb+` 尾部残留字节报错（`test_new2_1054` 等 3 张现行地图 → **101/101 正常打开**）、`LLEC`/`GIRB`/`PrefixRecord` 语义倒置及 57 张变体图缺名问题（重建 `scenes_tw_v2_27_2.json`，**101/101 地图命名与 283 传送点 / 1,293 NPC 全覆盖**）。完整实现 `GEPJ` 编解码与整图切片编译、`.blk` 双向同步、`LLEC` 画笔/矩形/直线/油漆桶、`GIRB` 4×4 动态光照画笔、`PrefixRecord` 2-bit Alpha 前景遮罩增删移与 `IntersectRect` 空间索引重建（`11,763/11,763` 零偏差）、8 方向 `CAStar` 寻路模拟、100 步撤销重做、严苛/宽松保存保护及写后自动重解析校验（98 张标准图 `SHA-256` 100% 一致，3 张 `rb+` 图有效体 `SHA-256` 100% 一致）。**Linux 已验证**：本次修复后 `unittest` **106 项**（103 通过、3 跳过、0 错误；本次沙箱无外部 101 图语料，语料测试跳过；此前已在外部语料完成全量 101 图往返与 `QT_QPA_PLATFORM=offscreen` Studio GUI 核验）、`ruff check map_editor` 零问题、`bootstrap.py --check-only` 零退出、`check_windows_compat.py map_editor` **0 ERROR / 0 WARNING / 0 INFO**；原始客户端资产 `SHA-256` 未变。**Windows 待实测**：真实 Windows 10/11 桌面窗口观感、`build.py` PyInstaller `dist/map-editor/` 真机打包与游戏客户端加载编辑后新地图联调。详见 [`MAP_EDITOR_ANALYSIS.md`](MAP_EDITOR_ANALYSIS.md) 与 [`../map_editor/README.md`](../map_editor/README.md)。

> **2026-10-22：UI 编辑器选图窗批量导出复核修复**（分支 `arena/28ca29c4-mxsj-tw-2022`）：多拼名族一起导出时，按基路径传递已计算的区分前缀，避免文件名退化为 `0l-2.png`；新增选图窗多族导出回归断言。Ruff、`py_compile` 与 `test_asset_export.py` 的 29 项通过；选图窗 GUI 定向测试因系统缺少 `libGL.so.1` 无法启动，未验。

> **2026-10-22 客户端伤害研究归档**（分支 `coderabbit/project-analysis/6aa25aac`，
> 起点 `3264485`；下文其他会话的组件快照不代表本轮测试）：新增
> [研究总笔记](../notes/client_damage_formula.md)与
> [小型证据摘要](evidence/client_damage_20261022.json)，记录 2026-10-21 四轮结果。
> 已定位面板威力、精修、基础目标数折减及回包到飘字路径；3458 停用自动修复后 914 条结构通过，
> 4329 的 18 组密钥/边界候选中 6 组通过、925 条记录一致，4791/2429 仍歧义；3773 候选 103 条。
> 已更正解析失败归因、key DB 真值措辞及旧除法 VA 未复现的限制。
> 本轮复核输入摘要、失败基线、候选/样本、指令窗口/flags、原生地址字节与文档引用；
> 不改原包、key DB、转换器或业务代码，未重跑应用套件或 Windows 客户端。
> **未完成**：最终目标防御/抗性/暴击/随机/取整组合，候选唯一性及定制 VM 原生数值验收。
> 下一步重定位除法 handler、核对歧义记录，并取得固定条件的单变量伤害样本。

> **2026-10-21 项目 skill**：会话分支 `coderabbit/project-analysis/6aa25aac` 已
> fast-forward 同步 master `e65e386`。新增
> [mxsj-project](../.agents/skills/mxsj-project/SKILL.md)，包含最新状态读取、
> 原生 TCP/Mock/编辑器/服务端入口和证据分级流程；仓库源文件同时安装至当前
> 环境的 Codex skills 目录。skill 结构校验、仓库路径检查及安装副本一致性检查
> 通过。此项只改 skill 和状态说明，未重跑应用测试、未启动 Mock 或客户端，
> 不变更此前应用验收结论。新会话可用 `$mxsj-project` 调用。

> **2026-10-20 原生 TCP 专项（分支 `coderabbit/project-analysis/6aa25aac`）**：
> 新增独立 [native_channel 0.1.0](../tools/native_channel/README.md) 与
> [握手/派生/密码器/帧研究](../notes/native_tcp_channel.md)。目标 mxmain 派生、
> 块生成、LZW 解压已离线原生对照；render 同族完整密码器双向 9000 字节及分片
> 对照通过。18 项 stdlib 测试通过；独立目录复制测试通过；Ruff、Windows 静态
> 检查均零报告，bootstrap/离线示例/spec 配置干跑通过。原始包与 DLL 摘要未变。
> **红灯**：目标受保护 init/process 包装器、真实 Windows 客户端连接、EXE 构建
> 尚未验收；严格 LZW END 与原生耗尽隐式结束存在明确差异；不宣称登录/进图。
> 下一步在 Windows 回环环境用假 seed 核验目标密码流、首包、连续包与重连。
> 本专项只新增工具与证据，不改账号、业务、数据库或客户端资源。

> **2026-10-22：UI 编辑器 0.16.0（保存模式：严格 / 宽松）**：用户要「工具栏再加一个
> 工具叫模式，也是小箭头选择，有宽松模式、严格模式；宽松模式所有改动写入原包，
> 严格模式按现在不变；切到宽松要二次提醒确认」。据此加「模式」下拉（在「编码」
> 右边）：**严格**＝原包只读、Ctrl+S 写编辑器自己的输出包（0.14.0 起的老行为，
> 一字未改）；**宽松**＝Ctrl+S 直接改写布局所在的**原包**，不生成新包。切到宽松
> 弹二次确认（写清「不留备份、不可撤销」，默认焦点在「取消」），切回严格不拦但会
> 忘掉「输出包就是原包」，避免下次又静默覆盖。用户口径：**一律回原包**（即便之前
> 严格模式存过新包）、**不留备份**、**模式记住**（重启保持）。宽松模式下工具栏
> 按钮变红、状态栏红字常驻；保存前清单改成「直接改写原资源包」、按钮「确认改写
> 原包」。写前检查、写后逐条校验、临时副本 + 原子替换一条没少。新增 15 项回归，
> 全套 **771 项**（770 通过、1 跳过、0 错误），ruff 0、wincompat 0/0/0。
> 随后复核 PR #74 的 AI 审查——首轮 5 条 + 追加 2 条**全部属实**（切回严格误清新包、
> 队列布局漏清后静默覆盖原包、确认框写错包、校验落在 `os.replace` 之后会毁原包、
> 本文件证据行过时；追加：写包失败被误报成校验失败、审计文档把跳过算成通过），
> 逐条修掉并补 11 项回归，全套 **782 项**（781 通过、1 跳过、0 错误）；判定与证据见
> [`analysis/ai_review_audit_pr74_20261022.md`](analysis/ai_review_audit_pr74_20261022.md)。
> 详见 §3 第三十六轮。未验：Windows 实机；工具栏观感只在 offscreen 截图核对。

> **2026-10-22：UI 编辑器 0.15.0（批量导入布局）**：用户说「我每导入一个布局文件
> 都得保存一次，一次只能选择一个布局文件，没法批量导入」。改成一次选**多个** `.dlg`
> 或**整个文件夹**：对话框里逐行给出「本地文件 → 包内路径 / 新增还是替换」，包内
> 已有的路径标「替换（已有同名布局）」，同一路径被选两次当场拒绝；确定后只把布局
> **排进队列**（左边树上一律显示「（待入新包）」），第一次 Ctrl+S 把整批**一次**
> 写进同一个输出包——只复制一次包体、只校验一次、只做一次原子替换，原包不动；
> 状态栏报「已写入 N 个导入布局」。队列跨「重新读取来源」保留，已保存/已取消的
> 条目会正确销账；删掉了只支持单选的旧 `layout_import_dialog.py`，单条导入仍走
> 同一个对话框（选一个文件即一条）。新增 19 项回归（批量写包 12 + GUI 7），全套
> **744 项**（743 通过、1 跳过、0 错误），ruff 0、wincompat 0/0/0。随后复核 PR #73
> 的 14 条 AI 审查——**全部属实**（同文件二次保存误报、散装另存可覆盖输出包、
> 队列布局不许新建、Windows 覆盖打开中的包等），逐条修掉并补 12 项回归，全套
> **756 项**（755 通过、1 跳过、0 错误）；判定与证据见
> [`analysis/ai_review_audit_pr73_20261022.md`](analysis/ai_review_audit_pr73_20261022.md)。
> 未验：Windows 实机；批量对话框观感只在 offscreen 截图核对。详见 §3 第三十五轮。

> **2026-10-22：UI 编辑器 0.14.0（打开 / 保存 / 导入 / 导出重新规划）**：用户说
> 「这个 ui 编辑器的什么打开保存导入导出搞的我有点迷糊」。按「一个动词只干一件事」
> 重排：**打开**（从哪来，不写文件）、**保存**（回到它来的地方）、**另存为**（换个
> 地方存新的）、**导出副本**（另拿一份，原件不动）。文件菜单合成 `打开 ▸` /
> `另存为 ▸` / `导出副本 ▸` 三段；工具栏 `打开▾ / 保存 / 另存为▾ / 导出副本▾`。
> 保存改成**第一次问一次输出包（默认 `interface_edited.fls`），之后 Ctrl+S 静默写回
> 同一个包**，不再弹框、不再套 `_patched`；标题栏与状态栏常驻「来源 → 去处」。
> 重构过程中修掉四个真问题：`_save_to_pack` 的 `res_path` 未定义（本轮改保存链时
> 写出、第一次保存必崩）、保存后标题滞后、最近打开里不同目录同名文件显示成多行
> 一样、同一文件原地写回时状态栏谎报「改变 0 条」。新增 22 项回归，全套 **724 项**
> （723 通过、1 跳过、0 错误），ruff 0、wincompat 0/0/0。
> 详见 §3 第三十四轮。未验：Windows 实机、新菜单观感。

> **2026-10-22：UI 编辑器 0.13.7（PR #72 AI 审查复核）**：对 20 条行内评论 + 3 条
> 范围外评论 + 1 条 nitpick 逐条对照代码/复现，**只改属实的**。代码修掉 11 处：
> ① 九片子图提示只留文件名（`top/left.png` 变成三个 `left.png`）；② 重挂同名图
> 后缩略图不刷新；③ `probe_pieces` 把 `middle/middle` 数两遍；④ 拼接预览只限高
> 不限宽（三张 1000×40 能撑到约 3000 px）；⑤ 族里一张图读不出仍拼半张；⑥ 改目录
> 路径时每个按键都重新解码预览；⑦ 只写一个轴时保真度误报 1:1；⑧ 多帧整图把
> 「其余帧是悬停/按下」写成事实；⑨ 往已有 `0l/0c/0r` 的目录写 `0/1/2.png` 会被
> 旧族盖住却没提示；⑩ 写包取消会删掉用户选来覆盖的旧文件；⑪ 写包用的
> `pending_import`/`encoding` 改成显式参数（不再挂 `self`，两次写包不互相覆盖）。
> 文档修掉测试分类（**708 项：705 通过、1 跳过、2 项基线**）、`736` 与 `9,310`
> 两套引用计数、截断的 SHA-256、目录探测范围与族类型优先级的旧说法。逐条判定见
> [`analysis/ai_review_audit_pr72_20261022.md`](analysis/ai_review_audit_pr72_20261022.md)。
> 详见 §3 第三十三轮。未验：Windows 实机、像素级一致性。

> **2026-10-22：UI 编辑器 0.13.6**：用户报三处「无响应很久」——整理资源到 100% 后要等、
> 第二次打开选图窗不秒开、新建族也要等。真包逐段量出四个原因并逐条修掉：① 清单第二段
> （核对 2,783 个名字在不在包里，含 729 个族逐块问）**没有进度**，进度条停在 100%——改成
> 两段合成一条 0→100 的进度；② 选图窗每行的族标签每次都重算 `plan`（729 个族 0.46 s）——
> `AssetResolver.family_plan/family_pieces` 按路径缓存；③ 缩略图把 2,758 行全解一遍
> （14.6 s）——只解当前视口（一屏 24 张 0.03 s，滚到哪补到哪）；④ 新建族后 `_refilter()`
> 重建整表（>0.2 s）——只插那一行（0.028 s）。另把写包进度接上（复制按字节、写图按张、
> 校验按条目，可取消），并修掉 `save_to_pack_dialog` **在后台线程里 `mount_pack`/改控件**
> 的线程问题（拆成「写文件」与「界面迁移」两半）。实测：清单 2.29→1.42 s；开窗 1.17/0.88 s
> →0.07/0.05 s；一屏缩略图 14.6 s→0.03 s；写回 2.5–3.7 s 有进度。新增 10 项回归，全套
> **698 项**（695 通过、1 跳过、2 项基线 `QMenu already deleted`），`ruff` 0、wincompat 0/0/0。
> 未验：Windows 机械盘写包耗时、EXE。详见 §3 第三十二轮。

> **2026-10-22：UI 编辑器 0.13.5**：用户在真包上核对效果时发现——画布把 `btn_Login`
> 画得**完全正确**（一整张「登錄遊戲」120×44），但选中它，状态栏写「模拟：资源取不到：
> 画的是编辑器占位框」。原因：这件控件 `.dlg` 里 `iWidth`/`iHeight` 是 0，画布按图片
> 自身尺寸画（兜底），保真度标注却要求"控件宽高 == 图片宽高"才算 1:1，宽高为 0 就
> 一条标注都不给，落到兜底的「无图片素材」。真包 2,708 篇布局、25,708 处图片字段里
> **23,391 处（91%）**没写宽高，即真实布局上绝大多数图片控件都在谎报"没有图片素材"。
> 改法：宽高为 0 按图片自身尺寸算 1:1；多帧整图（登录按钮 3 帧）改报「原生：多帧整图
> （3 帧）：常态画 0 号帧…其余帧留给悬停/按下（序号语义未核实）」。新增 2 项回归，
> 全套 **690 项**（687 通过、1 跳过、2 项基线 `QMenu already deleted`），`ruff` 0。详见 §3 第三十一轮。

> **2026-10-22：UI 编辑器 0.13.4**：用户要求"interface.fls 在谷歌云盘里，你下载来"——已下载 4 个分卷、拼包解压（614,482,967 B / 53,556 条目 / CRC32 `0x4fa12d0b` / SHA-256 `3fb516a9…1fb124`，与语料基线逐字节一致），并用真包逐控件类型复核拼名族。结论：`…\新登陆界面\三态按钮\登录按钮\` 里就是 `0.png`/`1.png`/`2.png` 三张整图（各 120×44，780 个候选名只命中这 3 个）；全包 729 个目录型基路径分布与旧记录一致（序号帧 423 / 九片 130 / 横三片 109 / 按钮横片 36 / 竖三片 22 / 单图 9，认不出 0 个）；**`CTextButton`→按钮横片不成立**——按不同基路径计 `CTextButton` 整图 53、横片 35，`CHPagePngButton` 16/10，`CVPagePngButton` 11/0。改法：新增 `WIDGET_DEFAULT_KINDS`（名字认不出时按真包多数派，按钮给序号帧），`WIDGET_KINDS` 收窄为位置词歧义时才用。详见 §3 第三十轮。

> **2026-10-22：UI 编辑器 0.13.3**：用户报「按按钮横片新建 → 三张图拼在一起」「按逐帧创建 → 变成分散的图片」。复核确认不是渲染 bug，而是**族类型选错**：按钮横片里每张只是按钮的 1/3，序号帧才是"每张一整图 = 一个状态"。旧实现无条件按控件类型选族，把"导出回来的 0/1/2.png"扭成 0l/0c/0r，正好造成用户看到的现象。改法：文件名结构优先（`0/1/2` → 序号帧，`left/middle/right` 这种位置词才听控件的）、对话框新增拼接预览图、族类型与张数说明直说"每张是三分之一/一整张"、选图窗选中目录时写明「里面有哪些图 + 游戏怎么用」。同时如实记下：`WIDGET_KINDS` 的控件→族对应**没有**逐类型实测证据，只是推荐。详见 §3 第二十九轮。

> **2026-10-22：UI 编辑器 0.13.2**：按 PR #71 的 AI 审查逐条复核，只修属实项——Windows 上新建族的 `KeyError`（`str(Path())` 键 vs 原串查）、按钮选 `上/中/下` 与 `①.png` 名导致对话框打不开（两处 `ValueError`）、批量导出两个族丢族名（`0l-2.png`）、`.igs` 族漏判覆盖、族标签每次按键重算、同族换图后预览/切片仍是旧的、族里子图读不出静默少导；README 旧名说反与 STATUS 计数已更正。大小写配位与"清 `_media_cache`"两条判为不属实/不必要。详见 §3 第二十八轮。

> **2026-10-22：UI 编辑器 0.13.1**：图片不用改名——按文件名认「左/中/右」「left/middle/right」「左上/tl/top-left」等别名，与选择顺序无关；认不出时按文件名自然排序（`2` 在 `10` 前），并在对话框逐条列出「哪张 → 哪个条目」。按钮控件优先按按钮命名（`0l/0c/0r`），文件名叫 `left.png` 时会说明"按控件写入"。详见 §3 第二十七轮。

> **2026-10-22：UI 编辑器 0.13.0**：新建拼名族——几张图直接变成一个按钮/边框。选图窗「新建拼名族…」多选图片 → 填族目录 + 自动判定类型（3 张三态横片、9 张九片、N 张序号帧）→ 整族挂账，保存回包时子图随目录引用一起写入。

> **2026-10-22：UI 编辑器 0.12.9**：「从资源包选择」现在能选目录型基路径（三态按钮 `…\登录按钮\`、边框、九宫格），标签带族说明、可只看拼名族；此前三层过滤把它挡在候选之外，只能手打路径。

> **2026-10-22：UI 编辑器 0.12.8**：目录型基路径（三态按钮 `…\登录按钮\`、九宫格/边框）的「导出素材」不再报「导出被拒绝」或「包内找不到」——按拼名族展开成每块子图导出（详见 §3 第二十四轮）。

> **2026-10-21：UI 编辑器 0.12.7**（按 PR #60–#65 的 AI 复核逐条甄别，只修属实项：
> 18 条属实未修全部落地，另补 #60-1 剩余与 #65-1 的文档子项；详见 §3
> 「按 PR #60–#65 复核修属实项」。同日用户口述在 Windows 实机跑通
> `mock_server_v2` 全链路（连接→登录→选角→进游戏→NPC 对话→对话中传送），
> **我方未复现**，不据此宣称认证／事务安全。

> **2026-10-19 更正：UI 编辑器 0.11.0 第一轮安全与动画改进已写入，Windows 原生全量检查已通过；Qt 画布与原生客户端验收仍待完成。正式服恢复，本地服独立化。 `server/` 保持 PR #52 合并前的 `cb2409aa` 状态。本轮在 `local_server/` 内建立独立 `src/mxsj_local_server`、配置、测试与打包结构，从历史实现迁入 SQLite／账号／会话／角色基础及日志，不再依赖正式服包。68 项本地测试通过；其他玩法只有契约边界，协议接入和 GUI 待实现，不宣称完整正式服等价。下文旧“共享实现”描述仅为历史。

> 快照：**2026-10-26，Asia/Shanghai**。§1–§2 是唯一当前概览；下方 §3 及后续编号记录是按日期保留的历史证据，不因其中写有“本轮／最新”就覆盖本表。
> 规则见 [AGENTS](../AGENTS.md)，能力入口见 [README](../README.md)，建议阶段见 [ROADMAP](ROADMAP.md)。
> 旧顶部摘要与组件表已[完整归档](archive/2026-10-18-status-prefix.md)；原 §3.1–§3.73 等章节不搬迁，保留既有引用。
>
> **§1–§2 的时效性说明（2026-10-27 补）**：§1 记录的会话分支／起点是**写它那一轮（2026-10-26 UI 编辑器轮）的快照**，
> 不随 master 前进而自动更新——它不是「当前检出分支」的实时值。判断当前集成状态请用
> `git log` / `git rev-parse HEAD` / `gh pr list` 的实际结果，不要把本表当实时真相。
> 同理，§2 各组件的测试计数只属于**各自那一次实测**，别处的数字不因此失效，
> 也不代表本仓库当前所有套件的统一复跑结果。版本号以各组件 `pyproject.toml` 为准
> （由 `tools/devkit/check_doc_versions.py` 静态校验 README／AGENTS／STATUS 的声明）。

## 1. 分支与集成

> ⚠️ **本表是 2026-10-26 UI 编辑器轮的快照，不是实时值。** 见上方时效性说明。

| 项 | 当时核实值 |
|---|---|
| 会话分支 | `arena/f980d0df-mxsj-tw-2022`（该轮 active，固定名称） |
| 本轮起点 | `eac25d9`（本分支 0.20.0；master 停在 `330479d`＝PR #89 合并点） |
| 集成边界 | ui_editor **0.19.0–0.21.0** 在本分支（该轮 PR #90 **已开、未合并**；后于 2026-10-26 11:27 UTC **已合并**）；0.18.0 及以前已在 master |
| 本轮授权 | 用户追问「要打开资源窗口才能打开图像编辑吗」，经 ask_user 确认加独立入口（磁盘批处理）：直接从磁盘选图/选文件夹处理、不挂包也能用（输出只能写磁盘），挂了包时浏览窗入口与挂账能力照旧保留；0.19.0/0.20.0 的授权详情见各自顶部条目 |
| 本轮证据 | 沙箱 PySide6 **6.11.2** offscreen（带符号 stub GL 库 81 个/6312 哑符号——本轮沙箱被重置：PySide6 6.12.0 的 shiboken 在本沙箱 Python 3.11.2 上有信号实参转换 refcount bug（最小复现：**未连接**的 `Signal(int).emit`×2000 即 `bool_dealloc` 崩溃、零桩库加载，与产品/测试代码无关），测试环境换装 6.11.2、产品与测试代码零改动；新镜像缺 libdbus-1/libEGL/libGL/libxkbcommon 等 81 个真库且 Qt6 为 BIND_NOW 急切绑定，桩从空桩升级为带符号桩，见顶部条目；审查轮沙箱再重置后按存档设计重建生成器重生成 62 库/6529 哑符号，导入链全通）跑 UI 全套 **939 项**：**938 通过、1 跳过、0 错误**（连续两轮；原判 932 项，PR #90 审查复核 +7 回归后复跑）；`ruff check` 0、wincompat 0/0/0（166 文件名项、147 扫描）。**本轮未执行真 `interface.fls` 实测**：全量布局 / 729 个目录型基路径是 0.12.5–0.13.x 的历史结果，不随本轮重跑。Windows 实机未验：图标与按钮观感、批处理参数观感均未验 |

## 2. 组件状态与实测

版本按当前源码元数据核对；测试计数仅属于下列范围，不用于计算项目完成率。

> 本轮只重跑 **ui_editor** 全套（**939 项：938 通过、1 跳过、0 错误**，见上表；含 PR #90 审查复核 +7 回归）；local_server 68 项、资源编辑器 126 项等为历史结果，不算本轮重跑。Windows 侧本轮无任何实机验收（批处理功能只在沙箱 offscreen 验证），GUI／客户端／EXE 未验收。

| 组件 | 当前能力／版本 | 本轮检查与边界 |
|---|---|---|
| 独立 SQLite 本地服 | `local_server/src/mxsj_local_server` 自有实现：账号／会话／角色基础、事务与日志；独立 CLI 和构建入口 | **68/68**；单独复制目录后运行通过。无游戏 TCP／进图／完整玩法／GUI／Windows EXE 验收。正式服目录保持恢复状态 |
| 独立客户端 Web 服务 | [web_server](../web_server/README.md) **0.3.0**：PySide6 GUI、浏览器后台、独立监听启停／暂停、文本发布与回退、访问控制及诊断／审计候选实现 | 历史结果（2026-10-19）：**60 项通过、3 项 GUI 跳过**；Qt 原生 libGL 缺失，GUI／Windows／浏览器视觉交互未验。HTTP 管理与权限边界使用真实回环测试；未知原生更新格式仍未实现 |
| 本地服诊断日志 | 位于本地服 core/observability；JSONL、轮替、脱敏与操作追踪 | 已包含在 2026-10-19 的 68 项回归中；非事务资产审计，Windows 锁／ACL 尚未实机验收；[说明](../local_server/README.md) |
| 静态复核链 | Catalog → FastAPI → React，只读候选数据，不是游戏网关 | Catalog **34**、API **27** 通过；网页类型检查／构建通过，测试 **112 通过、9 跳过**；本轮未做实时后端／真实浏览器验收 |
| 脚本编辑器 | **0.6.0.dev15**，界面重做（文件/语料/编辑/编码/编译/视图 六个菜单、F5 写入原包、F6 生成新包）、打开条目自动校验并绑定、恢复文本 8 MiB 分项预算、打开即缓存、未登记包自动验证、双 VM 原生构建；dev14 起读完即放包句柄、查找栏常驻 + 历史下拉、命中整行高亮；dev15 修审查复核后仍成立的 8 处 | 2026-10-28（本地 UTC+8）：本机 Linux（无 Qt 运行库，用 offscreen 与符号桩库跑 GUI；无真实双编译器）全量 **551 项通过 / 59 跳过 / 0 失败**，`ruff check script_editor` 全绿；跳过＝GUI 缺 `libGL.so.1`、未配真实两套标准编译器、opt-in 外部语料/pycdc。**Windows 实机与真实双编译器端到端写回未验**，游戏内表现未验收；明细见顶部轮次条目 |
| 资源编辑器 | **0.4.3**，后台识别、撤销、原生布局导入／替换、新包保护 | 本轮未跑完整套件；共享核心检查通过。用户曾确认特定大包打开提速，不外推所有资源兼容 |
| UI 编辑器 | **0.21.0**，图像批处理独立入口（工具栏「批图」分体按钮：从磁盘选图/选文件夹（只扫顶层）磁盘进磁盘出、不挂包也能用，参数窗与执行链复用 0.20.0 同一套，can_stage=False 输出只写磁盘，拒收/永不覆盖规矩同款）；0.20.0，图片批处理（浏览窗「批量处理…」：缩放/亮度/饱和度最小三样、首图前后对比预览＋输出清单确认、alpha 拆通道增强保透明、.igs 解码→调整→重编码往返带帧锚点/魔数护栏、输出＝写磁盘永不覆盖或挂账进包同名替换、Pillow 零新依赖）；0.19.0，添加属性行宽度互换（键下拉最小宽＝值框自然宽、值框最大宽＝下拉自然宽）、原生 schema 警示（原生字段集之外的键直说「游戏会忽略」、缩放动到游戏不读的维度直说「由图片素材自身决定」，只说不拦；数据层 NATIVE_TYPES/native_field_set/SIZE_IGNORED_NATIVE 与 2026-10-17 证据逐项互检）、.spr 导入（原字节挂账＋自动连带磁盘同名 .igs/.png 像素搭档＋[images] 变体点明像素在外部包＋多选与 .igs 同规矩）；0.18.0，.igs 导入（单张原字节挂账 / 多张＝前缀＋原文件名并列清单确认）、浏览窗「保存新资源（N）」（写全部挂账、不碰任何布局、目标跟随保存模式、成功才销账）、画布移动手柄（右上角外侧强制移动，根治父矩形夹取/祖先冻结的「拖不动」）；0.17.0，工具栏「资源」浏览窗、添加属性可编辑下拉（普查并集候选）、属性名中文 tooltip（prop_glossary）、画布剪切（一步撤销）、按钮 iAlign 九宫对齐＋文本类原生映射修复；另含 0.16.0 保存模式（严格 / 宽松）；批量导入布局（可多选文件/整个文件夹，导入 N 个只保存一次）；文件菜单按「打开 / 保存 / 另存为 / 导出副本」重排（保存记输出包后静默写回）、标题栏与状态栏显示来源→去处；画布按真包拼名族绘制、按钮真态切片、单图九宫格真实三分、有效尺寸夹父、替换布局状态保留、批量导出不覆盖磁盘、GBK 明文判定、目录型基路径按拼名族导出素材、选图窗可选/新建拼名族、图片按文件名认位、控件类型→拼名族按真包多数派兜底；选图窗族标签/子图清单按路径缓存、缩略图只解可见行、写包按段报进度 | 沙箱 PySide6 **6.11.2** offscreen（带符号 stub GL 库；6.12.0 因本沙箱 shiboken refcount bug 换装、产品代码零改动，见顶部条目）**939 项**：938 通过、1 跳过、0 错误（连续两轮；本轮新增独立入口 7＋审查复核回归 7）；ruff **0**、`check_windows_compat` **0/0/0**。Windows 实机未验。真 `interface.fls` 的全量布局与 729 个基路径是 0.12.5–0.13.x 的历史结果，**本轮未执行**。Windows 全量检查上次为 0.11.0。**与真实客户端像素级一致仍未验** |
| 地图编辑器 | `map_editor` v1.0.0：读写、编译、遮罩／通行／光照编辑、寻路、审计与 CLI | 2026-10-23 完成全量 101 图外部语料验证；Linux 本次 106 项（103 通过、3 跳过；外部语料未挂载，语料测试跳过），ruff 与 Windows 静态检查通过；原生 Windows 实机仍待验，详见本文件顶部记录 |
| 脚本手册 | **0.1.0.dev4**，只读目录、说明、专题与审核链 | 严格来源／完整登记校验通过：**5135 登记／20 说明／16 有限通过／1 排除**；四份战斗说明待非作者独审，专题不继承模块审核 |
| 共享核心／开发工具箱 | `mx_common` 唯一真源，生成副本独立交付 | **4 模块／9 副本一致**；devkit **44 通过**（含 Pillow 精灵交叉测试） |
| 逆向输入与来源 | 原包、key DB、材料映射 | 两份锁定 SHA 匹配；文件名来源映射 **96/96**，不是玩法或全量源码恢复证明 |
| 原生注册 | `tools/registration`；采用 PR #32 的用户确认版本 | 确认仅限当时版本／交互；没有真实注册服务。本轮未重跑；旧 overlay v3/v3.2/v3.3 已作废，禁止分发 |
| 本地 Mock | `mock_server.py` 明文版；`mock_server_v2.py` 原生加密通道（不改 `script.fls`）、JSON 存储 | 用户 **2026-10-21 在 Windows 口述**跑通 v2 全链路：连接→登录→选角→进游戏→NPC 对话→对话中传送地图（**我方未复现**，无抓包/日志）。`--self-test` 回环为上一轮结果；**不是**正式认证／事务保证，也不是完整玩法验收 |

### 当前阻塞项与风险

- **原生验收**：编辑器自洽回读不等于游戏正确；Windows／EXE／真实客户端和完整外部语料没有本轮验收。
- **Mock 误用**：默认准备客户端时可能改包及写开发模式；`--no-patch` 不是完全只读。已有账号未验证密码摘要，快速重登未验证请求 key，不可用于公网账号服务。见 [Mock 边界](MOCK_SERVER.md)。
- **依赖**：本轮 `npm audit` 非零，报告 1 moderate／2 critical，涉及 Vitest 开发依赖链；不等同于生产静态页面漏洞，需核实条件后升级，禁止盲目 `--force`。API 浮动依赖也需后续锁定。
- **自动化**：当前检出无 `.github/workflows`；CI 是建议待办，不是本轮实现。
- **许可／材料**：商业客户端与字体的再分发权利未确认，根目录无 LICENSE；恢复引擎另有许可要求，不把整包当开源工具发行。

### 下一步与未执行范围

1. 后续按授权建立 CI、依赖升级与可重复环境；本轮只记录缺口。
2. 固定编辑器真实样本、Windows／原生验收与回退记录。
3. 本地基础已实现账号／会话／角色元数据持久化；用户于 2026-10-18 同意暂缓原生加密接入，先保留分层边界，后续优先通过 CLI／自动化测试推进共享业务。legacy 凭据／有界 TCP、原生客户端选角／单地图另行接入，不再作为立即迁移 Mock 的任务；详下方决策记录及 [本地入口](../local_server/README.md)。PostgreSQL 同规则适配与专项并发验收仍待实现。
4. 本轮未执行完整编辑器 GUI、Windows EXE、游戏、独立 review-browser 验收套件、真实浏览器或公网服务；不把历史 Qt 桩库结果移植成本轮结论。

### 决策记录：暂缓原生 TCP 加密接入（2026-10-18）

用户在讨论原生协议后续接入成本后确认“行吧。先记录一下”，随后决定交由另一个 Agent 并行攻克原生信道。本会话仅记录并提交决策，不启动实现、客户端改包或联调。

- **现状**：新共享服务尚无 TCP 监听；原生 `C_net / SetSeed` 游戏信道加解密仍未恢复并验证。已有 Hello／部分报文字段证据不能当作完整原生接入；`IMProtocol.dll` 的算法不能替代游戏信道算法。
- **推进顺序**：本会话暂缓原生加密接入，先通过现有操作员 CLI 和自动化测试推进共享业务；原生研究由独立 Agent 并行推进，不要求共享业务等待研究完成；本地 SQLite 与未来正式适配器遵守同一业务规则，不做本地放宽版。
- **保留边界**：TCP 连接 → 可替换的协议适配层（握手、加解密、拆包、字段编解码）→ 认证／会话入口（验证后产生可信 RequestContext）→ 共享业务 → 持久化适配器。不得让业务层依赖 socket、原始包或加密状态。
- **返工预期**：未来主要补协议适配层和联调，原则上不因传输加密重写账号／角色规则、SQLite 事务与幂等；但原生包头、长度、收发状态和握手顺序可能关联，不能承诺只替换一个加密函数。凭据和会话语义仍可能需要局部调整。
- **凭据边界**：旧客户端 MD5 摘要不能冒充当前 `operator-utf8-v1` 的原始密码输入；legacy 认证须单独适配和验收。当前只用假测试账号，不提前引入真实账号迁移负担。
- **测试入口**：若后续确需网络测试，再单独实现显式隔离、默认仅本机的测试入口，不冒充原生协议。本次没有授权立即建立明文 TCP 或新增绕过补丁；原生兼容目标不变。
- **禁止迁入**：旧 Mock 的免密码认证、固定／未验证重登 key、自动客户端改包与加密绕过，不得作为共享服务默认逻辑。共享日志不记录凭据或原始敏感报文。
- **恢复原生接入的验收门槛**：独立算法／报文证据与测试向量、连续多包及双向状态／分段／重连验证，再进行不绕过加密的 Windows 原生客户端联调；未完成前不宣称原生已接通。

**后续明确授权：独立 Agent 可修改 `data/script.fls`，以加快原生任务。**
先备份原包并记录 SHA-256，在隔离测试副本中只修改必要 entry，记录用途与回退方法，并核验未涉及 entry 内容不变；大包和敏感采集数据不提交 Git。此授权不自动扩大到 EXE、DLL、key 文件或共享业务接口。
允许必要的脚本观察／测试／兼容适配；关闭 SetSeed、明文或替代算法仅能算标记清楚的对照实验，不能作为原生加密完成证据。优先交付原生握手→正确解读登录加密包→客户端正确接受响应的最小闭环，并验证双向连续包、分段与重连。最终须分别说明修改客户端与未修改客户端的实测状态、保留补丁及其语义影响。
独立 Agent 负责协议研究／适配，不迁入 Mock 的认证捷径，不改共享账号／角色规则、schema 或事务；接口调整先协调。完整任务说明已在对话提供，当前授权只代表允许开展，不代表任何原生实现已完成。

本轮只更新文档，未重跑代码测试；上方测试数保留的是上一轮日志模块验收结果。
保存时核到本地 HEAD 为 `cb2409aa883814018c8479c5d359a8a845b24d8a`、远端会话分支仍为 `af7d6e5072346bb0e23ec1130eea2f62d3bf4cf5`，工作文件仍含后续实现；本轮不重置或覆盖文件，不把既有差异重新提交。提交前已取回远端提交并核对全部 2793 个受跟踪文件：无缺失，仅本次 docs/STATUS.md 决策记录不同；随后只恢复当前分支指针与索引到远端基线，未覆盖工作文件，未重复提交既有实现。

### 独立 Web 项目决策与基础实现（2026-10-18）

用户明确指定项目名 `web_server`，使用 Python，公告／区服列表／更新分发可独立部署，不依赖游戏服务或原生 TCP 攻克。
本轮建立 `web_server/` 可独立复制运行的标准库 WSGI 基础、开发 runner、显式资源配置和测试。默认仅托管无业务含义的 example.txt，不猜测原生更新清单，不修改 update.ini、server.ini 或原始客户端资源。
支持原始字节 GET／HEAD、ETag／304、缓存控制和仅反映 Web 存活的 healthz；无目录浏览／匿名写入口，资源显式白名单、路径和链接校验、文件与快照大小限制。
运行目录需由可信发布者管理，采用启动快照；多副本切换不是原子发布。开发 runner 不用于公网生产，生产 WSGI／代理、TLS、更新信任链、Range 下载、完整日志及发布管理仍待实现或选型。
验证：`python -m unittest discover -s web_server/tests -v` 14 项；配置 check-only、ruff 和 Windows 静态检查通过。仅本子项目验收，不重跑或继承全仓库运行验收；未进行真实客户端／Windows EXE／生产部署测试。

### Web 已知文本格式落地（2026-10-18）

按用户要求，将已知公告／客服公告／基础区服列表写入 web_server：新增 UTF-8 操作员内容输入、严格 Big5／CRLF 生成器、假数据示例及三个只读 HTTP 路径。生成只写全新 release 目录，不改客户端配置或资源；未知更新接口继续 404。
[LEGACY_FORMATS](../web_server/LEGACY_FORMATS.md) 记录候选代码依据，以及 reserve/type、可选 serverid、列表附加段、HTTP 特性、更新清单与包格式等未核验事项。基础五字段列表不等于完整原生选服兼容；没有伪造更新成功或客户端验收。
本轮 22 项 Web 测试通过，含字节输出、Big5 严格编码、CRLF、字段拒绝、不覆写发布和未知接口 404；lint、配置自检与 Windows 静态检查通过。未运行 Windows 客户端、未探测官方 URL、未重跑游戏服务端测试。

### Web Python 工程规范整改（2026-10-18）

用户指出 web_server 未按 `PYTHON_TOOL_CONVENTIONS.md` 完整交付并要求整改。本轮重排为 `src/mxsj_web_server/{core,gui,data}`，GUI 仅预留边界说明，**不擅自实现仍在讨论的桌面窗口／远程后台**。
新增 pyproject／统一版本 **0.2.1**、包入口、requirements／开发依赖、自检 bootstrap、ASCII／CRLF 双击 BAT、两模式 PyInstaller spec 与构建 BAT；保留 run.py/content.py 为薄 CLI 入口。示例资源迁入包内只读 data；默认可写配置在 APPDATA/MXSJWebServer（无 APPDATA 时为用户主目录），不写安装包；显式发布目录仍由操作员选择。

- **Linux 已做**：35 项 unittest（原功能回归、独立中文空格路径、无副作用自检、版本一致性、依赖镜像流程替身、profile 不覆盖、源程序 HTTP 回环与关闭、spec 两模式结构测试），ruff 零报告，自检及 Windows 静态检查通过；构建 wheel 并在独立 venv、仓库外目录通过入口版本／配置检查。
- **构建阻塞**：onedir／onefile 均实际尝试 PyInstaller 干跑，但缺少 `libpython3.11.so.1.0` 而失败。结构替身测试不是打包成功，本轮无 EXE 产物。
- **Windows 待验**：BAT、自装依赖、两模式 EXE、中文路径、实际 APPDATA 权限、关闭后进程清理、原生客户端读取；Python 3.10 仅语法边界检查，实测解释器为 3.11.2。
- **已知功能边界**：当前是 CLI，注册 console-scripts、EXE console=True；尚无 QApplication、GUI、远程后台、后台开关或 Qt 验收。以后真实 GUI 按 PySide6／gui-scripts／console=False 交付，不能把预留目录称作完成。公网部署、未知更新格式及发布管理仍未实现。

证据：[Web 工程规范检查](analysis/evidence/web_server_standards_20261018.json)。原客户端资源、配置和游戏服务端代码未改。

### Web 管理器与双入口第一版（2026-10-18）

用户确认八模块设计并明确“开始编写”。本轮在独立 web_server 内实现 0.3.0 候选：
- PySide6 本地管理器：菜单、用户指定顺序的工具栏、七个管理页面、独立后台开关、托盘菜单与最小化恢复、关闭二次确认；耗时操作经 Worker，不在 GUI 线程执行。
- 现代浏览器后台：单管理员登录／会话、公告与区服编辑、预览／保存、生成版本／切换回退、设置／ACL、日志导出、公开服务控制。后台监听控制及密码重置仅本地。
- 共用 Manager：SQLite 独立状态与不可变文本版本、全局 revision 冲突保护、发布指针与内容审计同事务；失败不替换已发布内存快照。两项监听默认关闭，用户需保存→生成→发布。
- 安全：随机盐 scrypt、短期内存会话、CSRF／Origin／Host、HTTPS 后台可信代理来源限制、两套 CIDR 名单与有效期、可信转发链、登录／请求限流。单目录单进程锁，绑定失败不自动换端口。
- 公开暂停为503、后台暂停只读、停止释放端口并撤销后台会话；有界线程／请求体／socket 超时。日志轮替、敏感字段排除、写失败告警；监听生命周期诊断不宣称事务审计。

**Linux 已做**：63 项测试中 60 通过、3 GUI 因缺 libGL.so.1 跳过；真实 HTTP 权限／生命周期／发布失败／回退测试，ruff、Windows 静态与 JavaScript 语法检查通过；wheel 独立安装核心和后台资源检查通过。
**未验／阻塞**：完整 bootstrap 自检返回2（Qt原生库缺失），core-only 自检通过；PyInstaller 缺 libpython3.11.so.1.0。没有 Windows EXE、托盘／DPI／窗口截图或真实浏览器交互验收，不将静态／HTTP测试算 GUI 通过。
**功能限制**：单管理员、无 MFA／多人 RBAC／Windows Service 安装；桌面编辑菜单作用于文本控件，表格无全局撤销栈，布局持久化／最近配置未实现。后台设置暂为 JSON 编辑器。原生更新包与清单仍未恢复，禁止假报更新成功；服务不是直接面向公网的抗 DDoS／TLS 产品，须按部署说明加反向代理和网络限制。
证据见 [Web 管理器检查](analysis/evidence/web_server_management_20261018.json)，使用方式见 [README](../web_server/README.md) 与 [管理设计](../web_server/docs/MANAGEMENT.md)。游戏服务、旧 Mock 和原始客户端资源不变。

### 历史导航

以下编号小节已随 §3 一起归档到 [`docs/archive/STATUS_HISTORY.md`](archive/STATUS_HISTORY.md)，
**原编号未改**，按编号去归档文件检索：

- 旧顶部概览：[归档](archive/2026-10-18-status-prefix.md)。
- §3.1–§3.2：架构证据修复、目录寻址结案。
- §3.51–§3.53：手册审核与专题；§3.60–§3.61：UI 0.8.4。
- §3.63–§3.71：脚本原生加载问题及分段修复；§3.72：Mock；§3.73：PR #51 冲突处理。
- 旧 §4–§7 也是历史管理记录；当前等待项／下一步以本节为准。

---

## 8. 历史轮次记录已归档（2026-10-27）

原 §3（红灯与已知问题，3.1–3.82）与 §4–§7（等待外部输入／下一步／最近变更／如何更新）
以及按日期倒序的历史轮次条目，已按 `docs/archive/README.md` 的归档约定整体移至
**[`docs/archive/STATUS_HISTORY.md`](archive/STATUS_HISTORY.md)**，正文原样保留、编号未改。

- 当前状态（本文件的 §1–§2 与顶部轮次条目）仍然以本文为准。
- 需要查历史轮次、PR 复核过程、旧「下一步／待办／计数」时，去归档文件按编号检索。
- 外部文档中形如「STATUS §3.2」「STATUS §3.49」的引用已改写为指向归档文件的对应锚点
  （形如「STATUS_HISTORY §3.2」）；
  **原编号未变**，例如 `STATUS §3.2` → `docs/archive/STATUS_HISTORY.md` 的 §3.2。
- §7「如何更新本文」的归档约定继续有效：**不要删历史行**，超出当前状态范围的内容追加到
  归档文件（或在本文顶部加一条轮次条目并把明细链接过去）。
