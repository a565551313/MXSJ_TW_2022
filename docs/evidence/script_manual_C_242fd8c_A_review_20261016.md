# C login 第二轮 A 预审（2026-10-16）

审查评论：https://github.com/a565551313/MXSJ_TW_2022/pull/35#issuecomment-6203416829

## A第二轮预审：仍需修改（固定head 242fd8c941997f22a47f06069554cebba20d79a3）

本次使用A远端固定底座e49cb00，在仓库外覆盖C的5个login文件复审，未合并、不代替H独立审核。

**已确认修复**：selectserver.Show不再误绑4806；LoginOk函数summary已纠正；ShowLogin引用移到701–708；Python2恢复证据改为.py.txt、原字节未被格式化；strict validate含来源SHA/行号通过，ruff含spec通过，wincompat 0/0/0。A的dev2回归78项：67通过/11 GUI因当前环境未装Qt而跳过/0失败，不能记作78实过。

### 仍阻塞的内容

1. **同一结论未全文同步**：`loginin.json:1051`问答仍写“LoginOk保存账号；网络连接由netserver.RandomConnect与netlogin处理”，与已改正的函数summary矛盾。请统一为LoginOk校验并C2SLoginIn，OnLogin才SaveAccount；没有证据的RandomConnect顺序不要串成已确认调用链。

2. **条件仍与引用候选不符**：`loginin.json:560`写“TW按g_LangVersion…非TW直接ShowService”，但候选701–708实际仅判断`main.g_LangVersion == 0`，没有IsTWServer条件。OnMessage(2)的协议勾选检查也仅在`not misc.IsTWServer()`内（源575–585），不是全客户端都以勾选为前提。请按实际条件说明，不推定TW/HK对应关系。

3. **更换来源不等于证据完整覆盖**：
   - OnMessage(2)分支的Claim现在只引246–267的loginok，仍不包含消息条件575–585或OnLogin 657–661；
   - `main.json`登录问答只引loginok2=246–267，却同时解释OnMessage与OnLogin；
   - 公告问答引用mp_refresh=260–283及mp_layout=50–86，缺News地址选择/读取所在OnMessage(30) 226–244；
   - 注册问答只引register的307–543，仍无法证明mainpage入口或confirm布局；
   - loginin的main主循环问答仍引自身show段642–663。
   请逐个Claim列足实际来源/行段，或删去不受支持的断言、仅留“参见entry”导航。不要把“范围存在”当“内容对应”。

4. **关系方向/kind未完成复核**：register中“调用mainpage.Show返回首页”仍被标upstream calls，实际相对register是downstream；loginin读取register.g_AccountInfo仍标calls，应区分数据引用；main.json中的mainpage/loginin/register显示关系也请检查是否有实际调用证据，而不是由模块职责推出调用边。

5. **保真问题尚未回应**：main的.py.txt SHA仍为f048f22c…，与首轮.py逐字节相同；329/374行仍是`'sNz!!!!!'`，785行仍有`'hXCN…'`形态。改名与“字节级复制”只证明复制未再改字节，不能说明此前恢复/解码没有丢字节。
   请补原始候选输出摘要、工具/依赖锁、编码及Big5/后处理方法。若无法证明可逆，明确标记有损和不可靠范围，收缩来源状态与结论；也可使用保字节转义审阅稿重新建立证据。**不要手工猜改中文字串。** 三份旧稿的note新增包SHA/entry/co_filename文字仍只是声明，需可复核的来源关联记录；没有则保留historical_unverified_origin，而不是声称完整来源已核。

C继续只改annotations/login/，不要改A测试/schema/归属。请全文查找重复结论并逐项回应，修订后更新同一PR，无需另开。报告/来源字节或行号变化时同步重算SHA和引用。E的网络协审可用来交叉核对登录后隐藏面板等链路，但不同恢复引擎版本不要混称同一文本。

本轮不合并，不写H accepted。Windows/EXE/游戏未验。

## 本轮环境与保存边界

- 只读审阅游戏候选，未执行游戏脚本；未改C内容。
- 隔离快照：`/home/user/manual-review-c2-242fd8c/`，A底座e49cb00 + C固定五文件。
- 本轮来源验证：20历史种子 / 4说明 / H accepted 0；不等于完整目录或内容验收。
- 结构/SHA/行号验证通过；ruff==0.17.0与jsonschema==4.25.1，ruff含spec通过；wincompat 67文件名/26脚本，ERROR/WARNING/INFO均0。
- unittest本轮78项中67通过、11 GUI跳过；没有失败。先前A dev2三组78/78零跳过是历史结果，不能混用。
- 本地分支名保持A，但HEAD异常为8212b26且有大量既有工作区变化；远端A仍e49cb00。初期未改Git元数据；之后通过临时索引确认全部工作文件与远端A一致（仅本报告与STATUS补充），备份原索引后仅对齐同分支HEAD/index，未覆盖工作文件、未reset/checkout/stash/强推。操作收据见`git_metadata_alignment_20261016.json`。本报告随后作为A检查点提交推送；审查结论亦已记录到PR评论。
