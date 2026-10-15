# C提交559386b的A集成预审（不是H独立审核）

- 日期：2026-10-15；A工作分支 `arena/61deb9e5-mxsj-tw-2022`。
- 被审：`arena/160274ce-mxsj-tw-2022`，提交 `559386b3a44015d4bf7a4b4f0651b09d3257b87b`。
- 结论：**需要修改，尚未接纳/合入；不能把schema通过当作内容审核通过。** A不代替H，不写H accepted记录。本次未开/合PR；查询未见该head的打开PR。

## 已做与通过范围

1. 固定分支工作树干净；fetch C对象，不切分支、不cherry-pick、不merge。
2. 相对底座cc5c1ba，仅5个文件变化，全部在`script_manual/annotations/login/`：4份正文及main恢复证据。没有发现跨目录修改。
3. 在仓库外建立C覆盖的手册副本与仅含所需证据的镜像，未执行游戏源码。严格validate（含来源SHA/闭区间行范围）退出0：20目录/4说明/0 H通过。
4. 4份正文共155个类/函数记录、30个消息分支；这里只是记录数量，**不表示逐项解释已核实或覆盖完整**。
5. A未将C数据写入正式目录或预览，现行底座仍20历史种子/1待审样板/0 H通过。

## 必改问题

### P1：模块跳转身份错位

`mainpage.json`约524–540行的关系，symbol=`selectserver.Show`，却绑定entry **4806**。固定旧catalog里4806是`script/login/loginin.py`，4844才是`script/login/selectserver.py`。候选`mainpage.py:114–118`明确调用selectserver，而非loginin。

- 修为正确身份并接受“尚未编入目录”的提示，或暂设module=null并注明待B确认；不能为了可点击而绑定错模块。
- A原始样板也有此链路错误；C已纠正了文字但仍保留错身份。A承认种子错误，不将责任全部推给C。
- 全面复核relationships的模块身份、方向与kind。比如register中“调用mainpage.Show返回首页”相对register是downstream calls；读取`register.g_AccountInfo`不应标函数calls。纯“由某模块控制”的描述不能无证据变成调用边。

### P1：登录提交与账号保存被混为一谈

`loginin.json` LoginOk说明（约185行）及登录链路问答（约1051行）写“LoginOk保存账号”。

但其引用候选`loginin.py:246–265`为：读取账号/密码、必要校验、`netlogin.C2SLoginIn(user,password)`、设置`g_LoginErrorCallback`。账号保存位于**另一函数**`OnLogin():657–661`的`LoginIn.SaveAccount()`。需要区分登录按钮、提交、错误回调与成功后保存；RandomConnect的调用位置也应单独给出证据，而不是一句话串成未证实的顺序。

### P1：证据行号有效，但并不支持被标为static_reviewed的结论

机器只能检查哈希/行号存在，以下抽查已经发现语义不对应：

- `loginin.json` 的LoginOk引用`show=642–663`，不包含定义在246–265的LoginOk。
- ShowLogin引用`service=664–700`，而ShowLogin定义在701–709，刚好不在范围内。
- `main.json`公告、登录、注册的问答引用`mainloop=425–492`；该段主循环不能证明mainpage公告失败条件、register布局或loginin提交链。
- `mainpage.json`引用自身OnMessage的`messages`证明register回调对mainpage的上游调用，缺少实际register来源。

请逐个Claim复核，而非只改以上几个例子。跨模块结论应增加实际来源与精确证据，或者仅提供“参见entry”导航，删除不受支持的解释；依据不足保持inferred。static_reviewed指作者核对了对应证据，不是“有个合法证据ID”。

### P1：Python 2证据被工具代码检查当成Python 3源码

`main_entry4293_recovered.py`包含Python 2语法（如第128行`print 'End'`）。对C覆盖后的完整script_manual跑ruff实际报**38个问题**，包括invalid-syntax。这不是annotation数量变化导致的测试基线问题。

请改为明确的只读证据扩展名，例如`.py.txt`，更新sources.path与SHA/行号；不要自动格式化/移植游戏候选以消除ruff。保留原文和来源，不让工具代码检查或用户误把它当新Python 3工具执行。

### P1：main证据出现有损字符串形态，需澄清恢复/解码过程

C的main证据SHA为`f048f22c…`。与A此前独立只读恢复的保字节转义稿（仓库外，SHA `934ccca70741301ad7598d53405fa9ece686869ed4b85a1fdfda854c83bf34cc`）比较，除头部、排版外，可见：

- A稿的`'\\xb3s\\xb1\\xb5\\xa5N\\xb2z!!!!!'`在C稿329/374行变成`'sNz!!!!!'`。
- A稿的退出提示字节转义，在C稿785行呈`'hXCN۰ʶiJu\\\\uA'`等不完整字符形态。

这不是凭两个不同SHA断言算法有错，而是要求C提供原始候选输出摘要、恢复命令/版本、解码和后处理步骤，澄清是否用了ignore/replace或不可逆转换。当前不能当作保真文本证据接受。推荐保留原始字节摘要，提供可逆转义的UTF8审阅稿并记录转换方法，不静默丢弃字节。

三个旧候选的`source_status`由historical提升为recovered_complete，也需说明原包entry与候选的来源关联及“完整”的判断依据。若只有旧仓库文本静态阅读，应保留historical_unverified_origin；候选内部可见事实可以静态核对，但不能把来源核实也一并升级。新main注明u6=3.9.4.dev0，与另外三个旧稿u6=3.9.3要继续分开。

## A负责的问题，不要求C改公共工具

现有测试把生产annotations当测试夹具，所以扩容后不仅有1→4计数，还有“公告只命中337”的假设和仓库证据准备问题。A负责把固定单元夹具与真实内容冒烟分开，**不会仅把所有断言改为4来凑通过**。

- 只跑catalog测试：20项执行完成，8个失败报告（含subTest），主要涉及数量和搜索命中假设；不是8个已确认产品缺陷。
- 全套75项尝试在GUI证据复验处因夹具缺少新增来源而出现模态错误窗口，等待超时后A终止自己启动的进程；本次**没有完整回归结果**，不宣称全套通过，也不把所有失败归因于C。
- 这不抵销上面已独立复现的内容错链、无关证据和ruff问题。

## C修订后交付

继续在C自己的固定分支修订，仅改`annotations/login/`，不要改A测试/schema/任务表。提交修复SHA及逐项回应，可以开PR到A分支`arena/61deb9e5-mxsj-tw-2022`，不要开到master、不要自行合并。随后由A再预审、H独立审，E/F协审相关网络/战斗链路。未实机项保持未实机。
