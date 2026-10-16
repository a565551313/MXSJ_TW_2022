# N4 网络四篇退修响应（20261016 新 cohort）

## 身份、基线与范围

- 实际作者：全新 N4 会话，不是旧 E；逻辑 owner=E/domain=network 保留，四份 JSON author 已标 N4/原稿 E。
- 固定分支：`arena/b0da7f97-mxsj-tw-2022`。初始工作区干净，无已有改动需另造保存提交；先推送当前分支，再 fetch A，merge 用户指定的 `9b0dea799768aaacbb967ffc59f45753970752be`（Already up to date）。补取 shallow 历史，`7d32e5340b0ab4168f725d238d767ad6232f715d` 祖先检查通过；未跟随浮动 A 顶端工作。
- 只改 `script_manual/annotations/network/`；未改 main/login 正文、reviews、src/schema/tests、总表、STATUS、原包/参数/编辑器/启动器。按任务卡更具体边界，根 STATUS 由 A 接收后更新。
- 四篇原位修订，无同身份第二份；未自行批准，四份历史 A_delegate review 预期 stale，交 N7 以新 JSON 原字节重审。
- 本报告的“已修”仅指有限静态说明，不表示候选源码正确、网络可运行或游戏验收。

## 十项逐一回应

R 行 = 含六行恢复头的本轮候选行；`functions[限定名]` 为 JSON 中按 name 定位，不是数组索引。精确摘录/文件行映射见 `N4_reproduction.json.template` 的 excerpt_ranges。

| 历史发现 | 候选证据 | JSON 位置与处理 |
|---|---|---|
| N1 · net 组包顺序 | 3176 R901–904；`n4_net_prepare` | `net.json/functions[CNet.PacketPrepare]/summary` 改为先 `CNetClient.PacketPrepare`、返回后记 `m_NetHead`。共用报告 §2.3 同步，不保证原生发送/回调。 |
| N2 · 低档预算 | 3176 R55–70；`n4_net_lowest` | `functions[LowestUnpackParams]/summary` 与新增修改问答区分初次写 2、随后 `iRate=GetCurFrame()/30`、末次写 `2/iRate`；iRate=2 时算式为 1，不是最终固定 2。与命令队列每次最多 2 条是不同配置。 |
| N3 · 查名/低队列异常 | 3176 R696–708、R1323–1343；`n4_net_name/queue` | `functions[CNet.GetServerName]/summary` 明示 `_[1]` 与 x 不对应，正常查名未确认；`functions[CNetServerCommandQueue]/summary`、`functions[...Loop]/summary/branches` 说明低队列赋为 None 后 End，不保证低队列可消费；修改问答、limitations、共用报告均同步。没有修候选。 |
| Q1 · 重置作用域 | 871 R13–40；`n4_quick_reset` | `netquicklogin.json/functions[ModuleReset]/summary` 只列七个已声明 global 且赋值的状态。顶层点击/失败初值均 False；再次调用时失败标志无赋值、点击标志为未声明 global 的局部同名赋值。新增修改问答与 limitations、共用报告均区分初值与重置效果。 |
| Q2 · 断线问答证据 | 871 R73–80/R92–99/R192–197/R206–244；3176 R856–873 | `modification_guides[断线后不弹瞬连框/不重连]/answer/evidence` 不再只引旧 18–62 状态段，分别引用清 Key、CanQuickConnect/Connect showdlg 与 net.OnError 原行。**选择收缩 main 断言**：本轮未恢复 main，不将窗口触发当作本问答已证事实；给 N2 的协审补充要求其独立核实际条件和调用行。保留 OnError 正确的先后及退出/重登/正在瞬连守卫。 |
| S1 · 属性不等于握手 | 516 R280–295/R426–446/R510–516；`n4_server_prepare/connect/reselect_hello` | `netserver.json/functions[CMXNet]/summary`、`functions[CMXNet.OnServerCmd]/summary/branches` 和同名类问答统一为 hasattr；False 亦满足，非已握手门禁。共用报告 §5.2、limitations 同步。 |
| S2 · 二层组包顺序 | 516 R287–290；3176 R901–904 | `functions[CMXNet.PacketPrepare]/summary`：先基类 net.CNet.PacketPrepare，再记 m_iCmd；同时引用基类原行，基类又是先原生再记 m_NetHead。不把两层顺序混为一项。 |
| S3 · 刷新完整条件 | 516 R68–100；`n4_server_refresh` | `functions[RefreshServerInfo]/summary/branches` 拆版本门禁、float 解析异常、成功 else 的完整 `(tm is None or tm>now or now-tm>1200)`、谓词为假四种路径。未来时间戳即使差<=1200也刷新；异常仅置 None、不进 else。resources 的 refreshserver 说明、文案问答及共用报告同步。HTTP 文案构造在外层，非前述门禁的 if 体，不承诺请求成功。 |
| S4 · 递归谓词 | 516 R426–476；`n4_server_connect` | `functions[CRandomConnectMgr]/summary`、`functions[...Connect]/summary/branches` 及代理修改问答完整写 ShowConnectingDlg → m_Time 自增 → SetTimeOutCmd → `(m_Time-1 != 0) or g_AutoProxy`。递增后 m_Time=2 且非自动也递归，不是只首轮自动扩一次；保留空列表提前 return 与终止/真实轮数未知。共用报告及 limitations 同步，未把 OR 修成 AND。 |
| C1 · 无代理尝试次数 | 2170 R164–197；`n4_connect_attempts` | `connect.json/functions[DoConnect]/summary/branches` 与新增问答：预算>0且有代理前两条各一次；无代理按 IsDianXin 取 target_idx=0/1，仅一次。预算<=0仍直接兜底。三处 Fail 双回调、Success 未被引用原样保留，未保证 RestarConfirm 成功链。共用报告 §3.2 同步。 |

## 全篇同步与数量

- 四篇类/函数总数 **157 不变**（net52/connect24/quick29/server52）；所有限定名、signature、身份、逻辑 owner、来源状态未改。
- 已列分支 **43 → 48**：net23→24（Loop 低队列）；connect7不变；quick6不变；server7→11（属性存在但 False 新增1、刷新1条拆4条净增3）。不把没有 if 的重置/预算赋值伪造为新分支。
- 修改指南 **15→18**：net5→6、connect3→4、quick3→4、server4不变。新增三问覆盖预算/异常、尝试次数与重置作用域。
- 共用 E 报告仅四篇引用，已全部重钉 sources SHA；旧证据行数与位置不变，纠错原位完成。历史 E 的五条恢复记录仍注明 E 来源，不冒充 N4 又恢复了 main。
- 新证据 `evidence_n4_network.md`：15段302行，R前缀之外逐字保留，非完整源码。机器回执使用 `.json.template`，不被 annotation loader 当作第二份正文。
- 前轮 OnError、SetMaxLenBytes 冲突、StartQuickTimer、SetServerRoleInfo/OnLogin 后 Show(False) 的函数记录逐字保留并与基线比较通过；DGW/main serverid 缺链、低队列异常、成功回调缺口、计时单位未知未删。

## 来源复现与实际命令

独立外置环境：`/home/user/n4-env`，Python3.11.2 / uncompyle6 3.9.3 / xdis6.1.8 / spark-parser1.9.0 / click8.5.0；工具未改。

```text
/home/user/n4-env/bin/python tools/decompiler/recover_entries.py --out /home/user/n4-recovery --entries 3176,2170,871,516 --decompile-timeout 30 --report /home/user/n4-recovery/report.json
```

4/4 baseline/recovered/decompile_ok/source，repaired=False。稳定头第1–4、6行逐字等于前序 A 收据，keys/bounds另逐项等于锁定参数表；仅精确去前六行后正文4/4相同，871/516正文另与仓库无头候选逐字节一致。完整候选/恢复报告/日志留仓库外；本轮没有恢复4293或1288、没有 import/exec/eval 游戏模块、没有请求业务 URL。

| 文件 | SHA256 |
|---|---|
| data/script.fls | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72` |
| data/data.fls | `5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c` |
| tools/decompiler/script_fls_keys.json | `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb` |
| tools/decompiler/recover_entries.py | `152dbc28864a10c8b7188df7ae91c8039b0b8c0b056d98591e407b897e39c458` |
| tools/decompiler/batch_decompile.py | `a74742231e04c018c3f63452cfc859c20c6404fd73891eae9076bfcf8185b4e8` |

候选整文件、去头正文、四份新 JSON 的实际 SHA、证据行范围见 `N4_reproduction.json.template`；未扩大忽略范围凑摘要。

## Linux 已做 / Windows 待验 / 已知差异

命令中的 python/ruff 使用 `/home/user/n4-env/bin/` 对应可执行文件。

- `PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --require-full-inventory --repository .`：退出0，5135登记/20说明/3通过/1排除；四篇 review **stale 警告属预期**，未修改旧审核恢复“通过”。
- `PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest discover -s script_manual/tests -v`：**82项，71通过、11跳过、0失败/错误**。PySide6 6.10.3已安装，直接导入QtWidgets报缺 `libGL.so.1`，真实GUI未执行，skip不算通过。
- `ruff check script_manual script_manual/script_manual.spec`：通过。
- `python tools/devkit/check_windows_compat.py script_manual --strict`：0 ERROR/0 WARNING/0 INFO；最终含新增文件复查，路径/脚本数见机器收据。
- `python -m mxsj_manual build --verify-evidence --require-full-inventory --repository . --output /home/user/n4-manual-site-final`（同PYTHONPATH）：完整20篇单HTML构建通过，四stale警告保留。**未运行真实浏览器或jsdom**，构建不等于浏览器验收。
- 外置字节/元数据检查：15/15段302/302行精确匹配；157函数名/签名和原身份不变；前轮四类关键记录未回退；共用报告行数未移动；越界路径无变更。仅辅助检查，不冒充语义自动验收。
- `git diff --check`：通过。
- Windows/EXE、原生线格式、真实计时器、游戏/账号/服务端/抓包未测，无 runtime_verified 新结论。

## 剩余与交 A/N7

1. 十项文档已按候选退修，仍需 N7 对新原字节独立审核；旧四篇退修记录已 stale，本作者不写 reviews。
2. main 最终正文属 N2；本轮仅在 `main_network_review_for_c.md` §4 提协审，main窗口条件/触发行须 N2 独立取证，未靠旧状态段代证。
3. 原候选的查名推导式、低队列赋值、ModuleReset作用域、OR递归、未引用Success、StartQuickTimer和DGW缺链继续未知；未回码对象/原生/实机核定，不能改判“游戏bug已修”。
4. 帧续读2/3冲突与计时真实单位未裁决；HTTP调用不等于请求成功，客户端协议调用不等于服务端接受。
5. 本轮只退修四篇；5135目录/B签名和其他领域问题不在边界，未顺手接管或宣称全量完成。

提交后新 PR 仅到 A 固定集成分支，head 以最终交付回复/PR API 实际读回的完整 SHA 为准（避免将本报告自身提交号写进自身造成循环摘要）；不会自行合并。
