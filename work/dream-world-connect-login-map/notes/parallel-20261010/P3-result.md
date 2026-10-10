# P3-result：连接流程与 Connect() 复核（按 mapping_table_v4.json v4.3-taskB）

> 任务书：`brief-P3-connect-path.md` ｜ 协调表：`README.md`（2026-10-10）
> 复核对象：`notes/co_code_analysis/任务A深入-Connect函数破解报告.md`（基于 v4 映射的旧结论）

---

## 0. 记录要求（README 七项）

### 0.1 执行者与会话
- 执行者：Arena.ai Agent Mode 独立会话（P3 执行者）。
- 开始：2026-10-10 10:24 UTC（首次工具调用）；结束：2026-10-10 11:21 UTC。
- 仓库 / 分支：`a565551313/MXSJ_TW_2022`，分支 `arena/83f1d5bd-mxsj-tw-2022`（基线 commit `52ef64d`）。

### 0.2 输入校验（读取的每个文件及 sha256）

| 文件（相对仓库根） | sha256 |
|---|---|
| `work/dream-world-connect-login-map/notes/parallel-20261010/brief-P3-connect-path.md` | `2d6c439230e77362f8ddf43fb7a6dc871e57a08a83215f0dff1123a0f5d46fb5` |
| `work/dream-world-connect-login-map/notes/parallel-20261010/README.md` | `d801c3cb79d8f5e936faeb8d38a01403e26ad9fd47da4bb611184436f8d80b28` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/任务A深入-Connect函数破解报告.md`（被复核旧报告） | `4f51522a900130ae37034b9dfdbf4eea0171dee209002df3baa499e2a73920b5` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/mapping_table_v4.json`（版本 `4.3-taskB`） | `6b6d3c281c9af835a35a25e0779e1b20b87aad78fdad8b96f7d076fe2ff96d37` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/code_objects.json`（对象元数据，含 co_code_hex） | `ee5f9ef62d65139fc39e30486acfa835d917f8a0cd43a46438270b8574417aaf` |
| `work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin`（entry 516 解出的 Python 2.7 marshal，本次反汇编的真源） | `956b10875b586d47810315a489c7a43afcaee9f29d0864fbde2354306877b736` |
| `work/dream-world-connect-login-map/notes/co_code_analysis/netserver_py_decompiled.md`（对照用旧反编译报告） | `0fe4c39cc36b0721fdf18dcc331527826483b2c43163ff1efb96459f2fcba8b4` |
| `work/dream-world-connect-login-map/notes/loopback-test-plan-20261010.md`（H1–H5 定义） | `b7c17d725351ec735a303e8370efcff774cdf73b75be942ae01859f527fac574` |
| `IMProtocol.dll`（只读反汇编） | `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c` |

### 0.3 工具与版本
- Python 3.11.2（重新解析 marshal、常量池提取、自写反汇编器）。
- 自写"对齐回溯反汇编器"（按 v4.3 表 A/B + 双变体/未知字节 1B/3B 对齐拟合 + 跳转目标对齐评分；完整脚本见附录 D，本次为只读任务未放入 `tools/`）。
- GNU objdump（GNU Binutils for Debian）2.40（IMProtocol.dll 只读反汇编）。
- capstone：未安装，未使用。IDA：未使用（无许可证环境）。
- 未连接任何网络地址，未运行游戏或任何游戏代码。

### 0.4 执行步骤（摘要；命令级明细见附录 A）
1. 通读任务书与协调表；确认只读边界与 7 项记录要求。
2. 读取 `mapping_table_v4.json`，确认版本 `4.3-taskB`（表 A 43 条、表 B 5 条、unknown_hot 16 组、v3_corrections 6 条）。
3. 发现 `code_objects.json` 的 `const_strings` 只保留字符串常量、丢弃整数常量（生成脚本 `co_code_analyzer.py` 第 513–523 行），而 Connect 的端口编码依赖整数常量（256/65536/16777216/4/15 等）→ 重新用只读 marshal 解析器解析 `entry516-five-xor-marshal.bin`，恢复全部常量池（方法与 `decoder-artifacts/decode_entry516.py` 一致）。
4. 按 v4.3 映射实现反汇编器；对表外/双变体字节（0x37/0x6C/0x90/0x40/0x0E/0x0D/0x3D/0x0B/0x1F/0xCF/0x10 等）做 1B/3B 对齐回溯；要求端点精确（end-exact）且优先跳转目标全部落在指令起点。
5. 反汇编：`/CRandomConnectMgr/Connect`(647B)、`/CReselectConnectMgr/Connect`(689B)，及 `SetTimeOutCmd`、`nexttest`、`ConnectTestFail`(两版)、`IsConnectTestFail`、`__init__`(CConnectMgr/CRandom/CReselect/CMXNet)、`GetTestProxyList`、`GetTestServerList`、`RandomConnect`、`NormalReselectServerConnect`、类体（PROXY_CONNECT_TIMEOUT）。
6. 两个 Connect 均得到**唯一**端点精确解；全部 19 个跳转（A2 绝对 / B7、E3、AF、D3、E5 按 pos+3+arg）100% 落在指令边界 → 结构可信。对未映射字节用栈一致性分析定语义（见 §2.5）。
7. Big5 解码全部"混淆"字符串常量（附录 B）——证实它们不是加密，是繁体中文 Big5 文本。
8. objdump 只读反汇编 `IMProtocol.dll`：导出表、WS2_32 导入序号表、`IMP_ConnectNsServer`(RVA 0x10003000) 及其调用链（§5.3）。
9. 撰写本结果文件。未修改任何既有文件。

### 0.5 地址与依据表
见 §5（每个结论对应 偏移/地址 + 文件）。

### 0.6 未完成与未证实
见 §7。

### 0.7 修改记录
- 本次**未修改**任何游戏文件（mx.exe、mxmain.dll、IMProtocol.dll、server.ini 等）、`tools/` 代码、已有文档（含旧报告 `任务A深入-Connect函数破解报告.md`——只指出需改位置，未改动一字节）。
- 唯一新增文件：本结果文件 `P3-result.md`。临时脚本写在仓库外的临时目录，未入库。
- 未使用 `git rm`，未删除任何文件。

---

## 1. 复核方法与总原则

- **真源**：`entry516-five-xor-marshal.bin`（FLS entry 516 = `script\login\netserver.py` 的 marshal 对象树）。`code_objects.json` 的 co_code_hex 与之一致（已比对），但其常量池只剩字符串 → 本报告所有常量引用（`const[N]`）以重新解析 marshal 的结果为准。
- **对象命名**：`index N` 指 `code_objects.json` 数组序号（与 marshal 树中 `<module>` 常量槽一致）；函数内偏移为 co_code 内偏移（十六进制）。
- **判定分级**（按协调表规则 3/4）：
  - ✅ **v4.3 已证实**：字节序列 + 端点精确对齐 + 跳转目标全对齐 + 常量/名字池吻合。
  - ⚠️ **与旧报告（v4）不同**：旧报告结论被 v4.3 复核推翻或改写。
  - 🔶 **推断（强）**：唯一自洽的栈/语义读法，但缺第二样本或运行时证据。
  - ❓ **未证实**：无字节级依据。

---

## 2. v4.3 复核表

### 2.1 CRandomConnectMgr.Connect（647B，index 46，firstlineno 375）

旧报告 §2.1 伪代码逐段对照（偏移 = 该函数 co_code 内偏移）：

| # | 偏移 | v4.3 解码结果 | 旧报告（v4）说法 | 判定 |
|---|---|---|---|---|
| 1 | 0x000–0x017 | `import selectserver`；`import loginhello`（0xE0=IMPORT_NAME @0x006/0x012） | "创建选服和登录配置（字典）" | ⚠️ 与旧报告不同：不是创建字典，是两条 import 语句。v4 把 0xE0 误标 BUILD_MAP，v4.3 修正为 IMPORT_NAME（本函数 2 处即受此修正影响，见 §2.4） |
| 2 | 0x018–0x02D | `serverlist = self.GetTestServerList()`；`proxylist = self.GetTestProxyList()` | 相同 | ✅ v4.3 已证实 |
| 3 | 0x030–0x048 | `if not serverlist: selectserver.Refresh(None); return None`（E3=JUMP_IF_TRUE @0x033→0x4B；Refresh 参数为 `const[0]=None`，CALL arg=1 @0x040） | "if serverlist: Refresh('ipPort'); return 'ipPort'" | ⚠️ 与旧报告不同：**条件极性相反**，且 Refresh 实参是 `None` 不是 `'ipPort'`，返回值是 `None` |
| 4 | 0x04C–0x057 | `if not proxylist: return None`（E3 @0x04F→0x5A） | "if proxylist: return 'ipPort'" | ⚠️ 与旧报告不同：**极性相反**（代理列表为空才直接返回，不发起连接） |
| 5 | 0x05B–0x07C | `proxydata = proxylist[0]`；`proxy = proxydata['ipPort']`；`note = proxydata.get('note')`（0x58=BINARY_SUBSCR @0x061/0x06B；0x5A 在 0x078 处必须是 ROT_TWO，否则 proxy/note 赋值对调，见 §2.5） | "proxydata = proxylist['name']; proxy_ip; proxy_port" | ⚠️ 与旧报告不同：下标是 `proxylist[0]`；键是 `'ipPort'`/`'note'`（不是 'name'） |
| 6 | 0x07F–0x089 | `for d in serverlist:`（D3=SETUP_LOOP @0x07F→0x23A；0x36=GET_ITER @0x085；AF=FOR_ITER @0x086→0x239） | 相同（循环） | ✅ v4.3 已证实（但旧报告把 D3 当 FOR_ITER、0x6C 当 GET_ITER，循环边界读法是错的；v4.3 为 D3=SETUP_LOOP / 36=GET_ITER / AF=FOR_ITER，本函数全部跳转对齐验证通过） |
| 7 | 0x08C–0x0C1 | `name, ip, port, serverid, district = (d['name'], d['ip'], d['port'], d['serverid'], d['district'])`（DE=BUILD_TUPLE 5 @0x0AF；0x6C 三字节 UNPACK arg=5 @0x0B2；5×STORE_FAST） | "解包服务器信息（5 个字段）"，键名乱写 | ✅ v4.3 已证实：5 字段顺序 name→district，键为 'name'/'ip'/'port'/'serverid'/'district' |
| 8 | 0x0C4–0x0DC | `LOG('嘗試連接!!!', name, serverid, bool(proxy))`（CALL arg=4 @0x0D9；`const[10]`=Big5 '嘗試連接!!!'） | "LOG('b373b1b5…', name, serverid, bool(proxy))" | ✅ v4.3 已证实（格式串为 Big5 文本，非加密，见附录 B） |
| 9 | 0x0DD–0x0F2 | `netobj = CMXNet(ip, port, iType=loginhello.TEST_HELLO)`（CALL arg=0x0102=2 位置参数+1 关键字 @0x0EF；关键字名 `const[11]='iType'`） | "CMXNet(ip, port, ':', loginhello['TEST_HELLO'], …)" | ⚠️ 与旧报告不同：**没有 proxy_separator 参数**；第 3 参是关键字 `iType=`，值取自 `loginhello.TEST_HELLO`（属性访问而非下标） |
| 10 | 0x0F5–0x12E | `netobj.m_Hello=False; m_IsFail=False; m_ProxyName=''(const[12]); m_SvrName=name; m_ServerInfo=(district,name,ip,port,serverid)` | 属性表基本一致 | ✅ v4.3 已证实（m_ProxyName 默认空串 `''`，旧报告写 `'.'`/`':'` 是错的） |
| 11 | 0x131–0x140 | `self.m_Nets.append(netobj)` | 相同（先 append 再判代理） | ✅ v4.3 已证实 |
| 12 | 0x141–0x144 | `if proxy:`（B7=POP_JUMP_IF_FALSE @0x144→0x225，+3 相对，目标对齐） | 相同 | ✅ v4.3 已证实 |
| 12a | 0x148–0x164 | `LOG_DEBUG('連接代理!!!!!', proxy, note)`；`p = proxy.find(':')`（`const[14]=':'`） | "LOG_DEBUG('…', proxy, note); p = proxy.find(…)" | ✅ v4.3 已证实（find 的实参就是 `':'`） |
| 12b | 0x167–0x16D | `netobj.m_Proxy = proxy` | 相同 | ✅ v4.3 已证实 |
| 12c | 0x170–0x191 | `netobj.Connect(proxy[:p], int(proxy[p+1:]))`（0x0E=SLICE+2 @0x17C；0x3F=BINARY_ADD(p+1) @0x189；0x0D=SLICE+1 @0x18A；CALL arg=2 @0x18E） | "netobj.Connect(proxy, p, …)" | ⚠️ 与旧报告不同：实参是**切分后的代理 IP** 与 **int(代理端口)**，不是 (proxy, p, …)。`':'` 是代理串 `IP:PORT` 的分隔符 |
| 12d | 0x192–0x19E | `iplst = ip.split('.')`（`const[16]='.'`，CALL arg=1 @0x19B） | "iplst = ip.split(...)"（分隔符未定） | ✅ v4.3 已证实：分隔符是 **`'.'`**（详见 §3.3） |
| 12e | 0x1A1–0x1D4 | `for i in xrange(4): netobj.NakedSend(chr(int(iplst[i])))`（`const[17]=4`；CALL int/chr/NakedSend 各 arg=1 @0x1C7/0x1CA/0x1CD；A2→0x1AE 循环） | "for i in iplst: netobj.NakedSend(chr(port&0xFF), …); netobj.Connect(ip, port)" | ⚠️ 与旧报告不同：循环变量是 **`xrange(4)` 的下标**，不是 IP 列表元素；每次发送的是 **IP 的一个八位组字节**（`chr(int(iplst[i]))`），不是端口低字节；**循环内没有 Connect** |
| 12f | 0x1D5–0x221 | `netobj.NakedSend(chr(port%256) + chr((port//256)%256) + chr((port//65536)%256) + chr((port//16777216)%256))`（常量 `const[18]=256`、`const[19]=65536`、`const[20]=16777216`；0x37(1B)=MOD、0x3D(1B)=FLOORDIV、0x3F=ADD；外层 CALL arg=1 @0x21E） | "netobj.NakedSend(chr(port & 0xFF), …)" | ⚠️ 与旧报告不同：**不是单字节**，是一个 **4 字节字符串 = 端口的小端编码**。对 3134：`3E 0C 00 00`（首字节恰为 port&0xFF=0x3E，这是旧报告"单字节 0x3E"的误读来源） |
| 12g | 0x222 | `JUMP_ABSOLUTE → 0x86`（下一个服务器） | — | ✅ v4.3 已证实 |
| 13 | 0x225–0x236 | **else（无代理）：`netobj.Connect(ip, port)`，仅此一句，无任何 NakedSend**（CALL arg=2 @0x232） | 旧报告把 NakedSend+Connect 写成无条件执行 | ⚠️ 与旧报告不同：**直连分支完全没有 NakedSend** |
| 14 | 0x23A–0x23D | `ShowConnectingDlg()` | 旧报告未提及 | ✅ v4.3 已证实（旧报告遗漏） |
| 15 | 0x241–0x24D | `self.m_Time += 1`（0x30=DUP_TOP @0x244；0x43=INPLACE_ADD @0x24B；0x5A=ROT_TWO @0x24C——栈分析必需，见 §2.5） | 旧报告未提及 | ✅ v4.3 已证实（语义：自增，依据见 §3.4 的交叉验证；旧报告遗漏） |
| 16 | 0x250–0x259 | `self.SetTimeOutCmd()` | 旧报告未提及 | ✅ v4.3 已证实（旧报告遗漏） |
| 17 | 0x25A–0x27B | `if (self.m_Time - 1 != 0) or g_AutoProxy: self.Connect()`（0x23=SUBTRACT @0x263；CMP `!=` @0x267；E3 @0x26A→0x274 为 or 短路跳转——**E3=JUMP_IF_TRUE（非弹栈）由此证实**；B7 @0x271→0x282） | 旧报告未提及 | ✅ v4.3 已证实（旧报告遗漏整个超时重试尾部） |
| 18 | 0x283–0x286 | `return None` | — | ✅ v4.3 已证实 |

**v4.3 重建的 CRandomConnectMgr.Connect（完整伪代码）：**

```python
def Connect(self):
    import selectserver, loginhello
    serverlist = self.GetTestServerList()
    proxylist  = self.GetTestProxyList()
    if not serverlist:
        selectserver.Refresh(None)
        return
    if not proxylist:
        return
    proxydata = proxylist[0]
    proxy, note = proxydata['ipPort'], proxydata.get('note')
    for d in serverlist:
        name, ip, port, serverid, district = (d['name'], d['ip'], d['port'],
                                              d['serverid'], d['district'])
        LOG('嘗試連接!!!', name, serverid, bool(proxy))
        netobj = CMXNet(ip, port, iType=loginhello.TEST_HELLO)
        netobj.m_Hello, netobj.m_IsFail = False, False
        netobj.m_ProxyName, netobj.m_SvrName = '', name
        netobj.m_ServerInfo = (district, name, ip, port, serverid)
        self.m_Nets.append(netobj)
        if proxy:
            LOG_DEBUG('連接代理!!!!!', proxy, note)
            p = proxy.find(':')
            netobj.m_Proxy = proxy
            netobj.Connect(proxy[:p], int(proxy[p+1:]))     # 连到代理
            iplst = ip.split('.')
            for i in xrange(4):
                netobj.NakedSend(chr(int(iplst[i])))        # 4 个 IP 八位组字节
            netobj.NakedSend(chr(port % 256)                # 4 字节小端端口
                           + chr((port // 256) % 256)
                           + chr((port // 65536) % 256)
                           + chr((port // 16777216) % 256))
        else:
            netobj.Connect(ip, port)                        # 直连，无 NakedSend
    ShowConnectingDlg()
    self.m_Time += 1
    self.SetTimeOutCmd()
    if (self.m_Time - 1 != 0) or g_AutoProxy:
        self.Connect()
```

### 2.2 CReselectConnectMgr.Connect（689B，index 52，firstlineno 441）

| # | 偏移 | v4.3 解码结果 | 旧报告（v4）说法 | 判定 |
|---|---|---|---|---|
| 1 | 0x000–0x003 | `lst = []`（CA=BUILD_LIST 0） | 相同 | ✅ |
| 2 | 0x006–0x01B | `import selectserver, loginhello`（0xE0 @0x00C/0x018） | "创建配置字典" | ⚠️ 同 §2.1#1 |
| 3 | 0x01E–0x030 | `serverData, _, _ = selectserver.GetServerInfo()`（0x6C 三字节 UNPACK arg=3 @0x027——GetServerInfo 返回 **3 元组**；`serverData`=第 3 个元素，与 `CConnectMgr.__init__` 中 `m_ServerInfo` 同槽位，见 §2.3） | "serverData = selectserver.GetServerInfo()"（单值） | ⚠️ 与旧报告不同：返回值是 3 元组 |
| 4 | 0x033–0x050 | `for d in serverData.values():` `for slist in d:`（**两层嵌套循环**：D3@0x033→0x98、AF@0x040→0x97；D3@0x046→0x94、AF@0x04D→0x93） | "for _ in serverData: d = _"（单层） | ⚠️ 与旧报告不同：两层循环 |
| 5 | 0x053–0x067 | `if slist['district'] == '推荐區': continue`（`const[3]`=Big5 `b1c0aff2b0cf`=`'推荐區'`；A2→0x4D @0x064） | "if slist == 'name': continue" | ⚠️ 与旧报告不同：比较的是 `slist['district']` 与 Big5 常量 `'推荐區'` |
| 6 | 0x06B–0x090 | `if slist['serverid'] == self.m_ServerID: lst.append(slist)` | "if d['ip']==… and slist==m_ServerID: lst.append(d)" | ⚠️ 与旧报告不同：只有 serverid 一个匹配条件；append 的是内层条目 `slist` |
| 7 | 0x098–0x09E | `self.m_Nets = []`（循环前重置） | 旧报告未提及 | ✅（旧报告遗漏；注意 CRandom 版**不**重置） |
| 8 | 0x0A1–0x0E3 | `for d in lst:` + 5 字段解包（同 §2.1#7，DE 5 @0x0D1、0x6C UNPACK @0x0D4） | 相同（键名乱） | ✅ |
| 9 | 0x0E6–0x0FE | `print '嘗試轉服連接!!!', name, ip, port, serverid, district`（0x0B=PRINT_ITEM×6、0x1F=PRINT_NEWLINE，逗号打印模式；`const[8]`=Big5 `'嘗試轉服連接!!!'`） | 旧报告无此句 | ✅（语义：0x0B/0x1F 为推断（强）——栈序完全吻合 CPython2 `print a, b` 编码模式） |
| 10 | 0x0FF–0x114 | `netobj = CMXNet(ip, port, iType=loginhello.RESELECT_HELLO)`（CALL 0x0102 @0x111） | "CMXNet(ip, port, 'b373…', RESELECT_HELLO,…)" | ⚠️ 同 §2.1#9：第 3 参是关键字 `iType=`，无分隔符参数 |
| 11 | 0x117–0x165 | 属性设置同 §2.1#10；另 `netobj.m_PassPort = (self.m_Idx, self.m_Pwd)`（DE=BUILD_TUPLE 2 @0x15F） | 相同 | ✅ |
| 12 | 0x168–0x184 | `if isinstance(district, str): netobj.m_EntryName = district` | 相同 | ✅ |
| 13 | 0x185–0x191 | `proxy = GetProxy()`；`if proxy:`（B7 @0x191→0x288） | 相同 | ✅ |
| 13a | 0x195–0x1D2 | `print '連接代理!!!!!', proxy`；`p = proxy.find(':')`；`proxyName = GetProxyName()`；`if isinstance(proxyName, str): netobj.m_ProxyName = proxyName` | "proxyName = GetProxyName(); if isinstance… " | ✅（旧报告漏了 find 与打印） |
| 13b | 0x1D3–0x1F4 | `netobj.Connect(proxy[:p], int(proxy[p+1:]))`（0x0E/0x3F/0x0D 同 §2.1#12c；CALL arg=2 @0x1F1） | "netobj.Connect(proxy, p, …)" | ⚠️ 同 §2.1#12c |
| 13c | 0x1F5–0x233 | `iplst = ip.split('.')`（`const[14]='.'`）；`for i in xrange(4): netobj.NakedSend(chr(int(iplst[i])))`（`const[15]=4`） | "for i in iplst: NakedSend…; Connect" | ⚠️ 同 §2.1#12e |
| 13d | 0x238–0x284 | `netobj.NakedSend(<4 字节小端端口串>)`（`const[16]=256`、`const[17]=65536`、`const[18]=16777216`；同 §2.1#12f） | "NakedSend(chr(port&0xFF))" | ⚠️ 同 §2.1#12f |
| 14 | 0x288–0x298 | **else（无代理）：`netobj.Connect(ip, port)`**（CALL arg=2 @0x295） | 无代理分支不存在 NakedSend（旧报告未区分） | ⚠️ 同 §2.1#13 |
| 15 | 0x299–0x2A8 | `self.m_Nets.append(netobj)`（**在 if/else 之后**） | "添加到网络列表"（位置对） | ✅（注意与 CRandom 版相反：此函数 append 在连接之后） |
| 16 | 0x2A9–0x2B0 | 循环回 0xA8；`return None` | — | ✅ |

**与 CRandom 版的结构差异（v4.3 证实）**：CReselect 版**没有** `ShowConnectingDlg`、`m_Time += 1`、`SetTimeOutCmd`、`g_AutoProxy` 重试尾部；候选只遍历一轮，无超时轮换。失败处理走 `CMXNet.OnConnectFail → g_ConnectMgr.OnSocketConnectFail → CConnectMgr.ConnectTestFail`（基类弹窗，index 37，含 `'連接服務器失敗'`/`'確定'` Big5 常量）。

### 2.3 辅助函数复核（均唯一端点精确解）

| 函数（index） | v4.3 结果 | 判定 |
|---|---|---|
| `CRandomConnectMgr` 类体（50） | `PROXY_CONNECT_TIMEOUT = 15`（`const[0]=15`，0x98=STORE_NAME @类体偏移 0x00C–0x00F，names[2]） | ✅ **超时常量值为 15**（旧报告/测试计划 H2 均缺此值；单位未证实，见 §7） |
| `CRandomConnectMgr.__init__`（42） | `CConnectMgr.__init__(self); self.m_Time = 0; self.m_AllTry = False` | ✅ |
| `SetTimeOutCmd`（48） | `nexttest = <函数 const[1]>`；`if getattr(self, 'm_TimeoutCmd', None): self.m_TimeoutCmd.Release()`；`self.m_TimeoutCmd = self.CreatePyCommand(self.PROXY_CONNECT_TIMEOUT, nexttest)` | ✅（旧报告的 netserver_py_decompiled.md §SetTimeOutCmd 与此一致） |
| `nexttest`（47） | `def nexttest(obj): obj.Connect()` | ✅ |
| `CRandom.ConnectTestFail`（49） | `if self.IsConnectTestFail() and self.m_AllTry == False:` `self.m_Time = 0; self.m_AllTry = True; self.Connect()` `else: CConnectMgr.ConnectTestFail(self)` | ✅（旧报告未给出此逻辑） |
| `IsConnectTestFail`（40） | `for netobj in self.m_Nets: if netobj.m_IsFail == False: return False`；`return True`（即"全部失败"才真） | ✅ |
| `GetTestProxyList`（44） | `if not self.m_ProxyInfo: return []`；`ipPort = GetProxy(); name = GetProxyName()`；`extlist = [ {note/ipPort/type 字典} ]`（构造指令 0x30/0x5A/0x05 组合**未解**，见 §7）；`if name != '自動選擇': extlist = extlist + [ {…} ] else: g_AutoProxy = True`；`proxylist = extlist + self.m_ProxyInfo`；**`for t in xrange(self.m_Time): proxylist.pop(0)`**；`return proxylist` | 🔶 主体已证实；extlist 字典构造未证实；**pop(m_Time) 前移代理候选已证实**（偏移 0x0A0–0x0C6） |
| `GetTestServerList`（45） | `if not self.m_ServerInfo: return None`；`IPs = []`；`if g_PriorServer:`（分支内 0xCF/0x10 未解，§7）`else:` `dianXinList=[]; WangTongList=[]`；`for district, districtData in self.m_ServerInfo.iteritems():` `if district.find('電信')>=0: dianXinList = dianXinList + districtData` `elif district.find('網通')>=0: WangTongList = WangTongList + districtData`；`random.shuffle(dianXinList); random.shuffle(WangTongList)`；`IPs = IPs + dianXinList[:5] + WangTongList[:2]`（0x0E=SLICE+2 @0x10F/0x11D 再次证实）；`return IPs` | ✅ 主体已证实（g_PriorServer 分支细节未证实） |
| `CConnectMgr.__init__`（35） | `interface.CBaseObject.__init__(self, None)`；`self.m_Nets = []`；`import selectserver`；`self.m_ServerInfo, _, self.m_ProxyInfo 的槽位 = selectserver.GetServerInfo()` 3 元组解包（0x6C arg=3 @0x031；TOS 优先存 → `m_ServerInfo`=返回值[2]、`m_ProxyInfo`=返回值[0]） | ✅（m_Nets 是**实例属性**，非旧报告所说的类属性） |
| `CMXNet.__init__`（29） | `net.CNet.__init__(self, ip, port)`；`self.m_NetType = iType` | ✅（证实 CMXNet 第 3 参就是 iType，与 §2.1#9 的关键字调用吻合） |
| `RandomConnect`（54） | `g_ConnectMgr = CRandomConnectMgr(); g_ConnectMgr.Connect()` | ✅ |
| `NormalReselectServerConnect`（57） | `g_ConnectMgr = CReselectConnectMgr(serverID, idx, pwd); g_ConnectMgr.Connect()` | ✅ |

### 2.4 v4→v4.3 四条修正对 Connect 的影响（任务书问题 1 的映射部分）

对两个 Connect（647B/689B）做字节普查：

| v4.3 修正 | 是否出现在 Connect 中 | 影响 |
|---|---|---|
| `0x98: MAKE_FUNCTION→STORE_NAME` | 否（两个 Connect 中 0 字节 0x98；0x98 只出现在类体/模块层） | 无影响 |
| `0xE0: BUILD_MAP→IMPORT_NAME` | **是，每个函数 2 处**（CRandom 0x006/0x012；CReselect 0x00C/0x018） | **有影响**：v4 会把两条 import 语句误读为 BUILD_MAP；v4.3 下正确读出 `import selectserver` / `import loginhello`。旧报告伪代码开头"创建配置字典"即 v4 误读的残留 |
| `0xFB: STORE_NAME→MAKE_FUNCTION` | 否（0 字节 0xFB） | 无影响 |
| `0x42: POP_TOP→BUILD_CLASS` | 否（0 字节 0x42；仅出现在模块层类定义尾部） | 无影响 |

**结论**：四条 v4.3 修正中只有 0xE0 影响两个 Connect（各 2 处 import）；但旧报告的错误主要不是来自这四条，而是来自其自拟的 4 条映射（E3/58/6C/D3）中 **3 条是错的**（详见 §6.1），导致循环结构和条件极性整体误读。

### 2.5 本次新确定/修正的 opcode（netserver.py 函数代码对象内）

> ⚠️ **多变体警示**：v4.3 已证明"同字节在不同 code object 中大小/含义不同"（0x6C/0x37 双变体）。下表中 0x30/0x5A 与 v4.3 表 A 的现标注（POP_TOP/NOP）在 netserver.py 的**函数代码对象**中被栈分析否定——这支持"多变体 S 盒"结论，**本报告不覆盖 v4.3 表，建议协调者记为"待核对"**。

| 字节 | 本上下文语义 | 依据 | 置信 |
|---|---|---|---|
| 0x30 | DUP_TOP | CRandom Connect 0x241–0x24D：`LOAD_FAST self` 后仅一次压栈，而 `STORE_ATTR m_Time`（值,对象）序（该序由 0x0F5–0x0FB `LOAD False; LOAD netobj; STORE_ATTR m_Hello` 证实）要求对象在栈上出现两次 → 0x244 必须复制 | 证实（栈必需） |
| 0x5A | ROT_TWO | CRandom Connect 0x065–0x07C：先压 `proxydata['ipPort']` 再压 `proxydata.get('note')`，若 0x078 为 NOP 则 `proxy` 会拿到 note 值（后续对 proxy 做 `find(':')`/`Connect` 必须是 IP:PORT 串）→ 必须交换；0x24C 处 `self.m_Time += 1` 的 DUP/LOAD_ATTR/ADD/ROT/STORE_ATTR 正是 CPython2 `+=` 属性编译模板 | 证实（栈必需） |
| 0x43 | BINARY_ADD / INPLACE_ADD | GetTestServerList 0x0BC/0x0E0（列表拼接 `dianXinList + districtData`）、0x110/0x11E（`IPs + dianXinList[:5]`）；Connect 0x24B（`m_Time += 1` 模板） | 证实（多样本） |
| 0x3F | BINARY_ADD | Connect 0x189（`p+1` 切片下界）；0x1F9/0x20B/0x21D（chr 串拼接） | 证实（多样本） |
| 0x37（1B 变体） | BINARY_MODULO（`%`） | 端口 4 字节编码唯一自洽读法（见 §3.2）；若读作 `//` 或 STORE_SUBSCR 均产生无意义序列 | 🔶 推断（强） |
| 0x3D（1B） | BINARY_FLOOR_DIVIDE（`//`） | 同上（`(port//256)%256` 等） | 🔶 推断（强） |
| 0x0E | SLICE+2（`x[:n]`） | `proxy[:p]`（两函数同位）；`dianXinList[:5]`、`WangTongList[:2]` | 证实（4 样本） |
| 0x0D | SLICE+1（`x[n:]`） | `proxy[p+1:]`（两函数同位） | 证实（2 样本） |
| 0x0B | PRINT_ITEM | CReselect 0x0E6–0x0FE：`const, 0B, name, 0B, …, 0B, 1F` 完全吻合 CPython2 `print a, b, …` 的 PRINT_ITEM×n 编码 | 🔶 推断（强） |
| 0x1F | PRINT_NEWLINE | 同上（句尾 1 个） | 🔶 推断（强） |
| 0x40 | POP_BLOCK | 所有 FOR_ITER 环出口后紧跟（CRandom 0x1D4/0x239；CReselect 0x093/0x097/0x237/0x2AC；IsConnectTestFail 0x02B 等 10+ 处） | 🔶 推断（强） |
| 0xE3 | JUMP_IF_TRUE（非弹栈，跳转基数 pos+3+arg） | v4.3 表中为 `JUMP_IF_TRUE?`（medium）；本函数 0x26A 的 **or 短路跳转**（`A or B:` A 真则直奔 B 后的公共体 0x274）+ `if not X:` 的跳过模式（0x033/0x04F）双重证实 | 证实（本函数内） |
| 0x36/0xAF/0xD3 | GET_ITER / FOR_ITER / SETUP_LOOP | v4.3 表已有；两个 Connect + 5 个辅助函数的循环全部对齐 | 再证（多样本） |

**未解字节**（出现在复核范围内但语义未定）：0x00（参数区高频，未作指令处理）、0xCF 与 0x10（GetTestServerList 的 `g_PriorServer` 分支）、GetTestProxyList `extlist` 构造中的 0x30/0x5A/0x05 组合（与 §2.5 前两行的 Connect 语义不能同时成立，疑为另一变体）。

---

## 3. 任务书四问的回答

### 3.1 Q1：按 v4.3，Connect() 每一步是否仍成立？
见 §2.1/§2.2 逐行表。**成立的部分**：调用序列、5 字段解包、属性设置、m_Nets.append、代理判断。**被推翻的部分**：两个 `if` 的极性（#3/#4）、CMXNet 第 3 参（#9）、`netobj.Connect(proxy[:p], int(proxy[p+1:]))`（#12c）、"for i in iplst: NakedSend+Connect"（#12e——不存在）、NakedSend 单字节说（#12f）、直连分支无 NakedSend（#13）、以及旧报告遗漏的整个尾部（#14–#17）。四条 v4.3 修正中仅 0xE0 涉及 Connect（§2.4）。

### 3.2 Q2：`NakedSend(chr(port & 0xFF))` 是否在 Connect 之前执行？是否单字节 0x3E？
- **不存在这条语句**。实际的 NakedSend 有两种，且**全部位于 `if proxy:` 分支内、在 `netobj.Connect(proxy[:p], int(proxy[p+1:]))` 之后**（CRandom 0x170→0x1D5 顺序；CReselect 0x1D3→0x238 顺序）：
  1. `for i in xrange(4): netobj.NakedSend(chr(int(iplst[i])))` —— 4 次调用，每次 **1 个字节 = 目标 IP 的一个八位组**（'127'→0x7F 等）；
  2. `netobj.NakedSend(chr(port%256)+chr((port//256)%256)+chr((port//65536)%256)+chr((port//16777216)%256))` —— 1 次调用，**4 字节字符串 = 端口小端编码**。
- 对端口 3134：4 字节为 `3E 0C 00 00`。**首字节**恰为 `port & 0xFF = 0x3E`——这就是旧报告"单字节 0x3E"说法的错误来源；实际发送 4 字节，且此前还有 4 个 IP 八位组字节，**合计 8 字节**（4+4）。
- **在 TCP 建立之前还是之后**：静态无法判定——脚本先调用 `netobj.Connect(代理)` 再调用 NakedSend，但 `CNet.Connect`（原生实现）是同步阻塞还是异步事件驱动未知（存在 `OnConnectFail`/`OnError` 回调，提示异步）。**未证实**，需按 loopback-test-plan E1 做运行时观察。
- **直连（无代理）分支没有任何 NakedSend**——这对回环测试（直连 127.0.0.1:3134）意味着：脚本层在连接前后都不主动发字节。
- 用途推断（🔶 推断，非字节证据）：向代理通告目标地址（4 字节 IP + 4 字节小端端口），即代理隧道的寻址头。`NakedSend` 的原生实现未定位（见 §7）。

### 3.3 Q3：`ip.split(...)` 的分隔符与 127.0.0.1 的切分
- 分隔符是 **`'.'`**（`const[16]`（CRandom）/`const[14]`（CReselect），hex `2e`；调用点 0x198/0x1FB，CALL arg=1）。
- `'127.0.0.1'.split('.') == ['127','0','0','1']`，经 `int()` 后为 `[127,0,0,1]`——**切分正确**。
- 切分结果**只**用于 `xrange(4)` 的八位组 NakedSend（`iplst[i]`），**不用于候选迭代**：不存在"对每个 IP 分别 Connect"的负载均衡循环（旧报告 §3.3 步骤 f/g 系误读）。

### 3.4 Q4：连接失败/超时后是否切换候选？超时参数值？
- **`PROXY_CONNECT_TIMEOUT = 15`**（CRandomConnectMgr 类体 `const[0]`，index 50；经 `SetTimeOutCmd` 传入 `self.CreatePyCommand(PROXY_CONNECT_TIMEOUT, nexttest)`）。**数值已证实；单位未证实**（CreatePyCommand 为原生接口；若为秒则与观察到的"由客户端定时关闭"吻合，属推断）。
- **超时路径**：超时命令触发 `nexttest(obj) → obj.Connect()`（即 CRandomConnectMgr.Connect 重入）。重入时：
  - `GetTestProxyList` 先 `for t in xrange(self.m_Time): proxylist.pop(0)`（0x0A0–0x0C6）——**每次重入按已试次数前移代理候选**；
  - `GetTestServerList` 重新 `random.shuffle` 并取 `電信[:5]+網通[:2]`（0x0EC–0x11F）——服务器候选重新随机；
  - 尾部 `(self.m_Time - 1 != 0) or g_AutoProxy` 为真时**立即再次** `self.Connect()`（0x275）——即超时重入后会连续轮换（首次调用 m_Time 0→1 时条件为假，仅 g_AutoProxy 时继续）。
  - **→ 会切换候选：证实**（代理前移 + 服务器重洗牌）。
- **失败路径**：`CMXNet.OnConnectFail`（index 32）→ `g_ConnectMgr.OnSocketConnectFail(netobj)` → `self.ConnectTestFail()`。CRandom 版：仅当 `IsConnectTestFail()`（**所有** netobj 的 m_IsFail 均为 True）且 `m_AllTry == False` 时：`m_Time = 0; m_AllTry = True; self.Connect()`（一次性整轮重连；注意 m_Time 被清零 → 代理列表不前移，但服务器列表重新洗牌）。否则走基类 `CConnectMgr.ConnectTestFail`（index 37：`ShowNewMessageBox('連接服務器失敗', '確定', …)` 及 Refresh 逻辑）。
- **CReselect.Connect 无任何超时/重试逻辑**（无 SetTimeOutCmd/m_Time/g_AutoProxy 字节）——重选服流程失败即弹窗。

---

## 4. H3 / H4 结论（供协调者更新 loopback-test-plan-20261010.md）

### H3「连接前的 NakedSend 单字节被丢弃」——**前提不成立，建议改写或作废**
1. 直连路径（无代理）**根本没有**连接前的 NakedSend（CRandom 0x225–0x236 只有 `Connect(ip, port)`）——回环测试直连 127.0.0.1 时 H3 描述的对象不存在。
2. 代理路径的 NakedSend 在 `Connect(代理)` **之后**，内容为 8 字节（4 个 IP 八位组 + 4 字节小端端口），不是 1 个字节。
3. "被丢弃"无法用静态分析判定（NakedSend 原生实现未定位）——若要保留该假设，需改为："代理分支在 Connect(代理) 后发送 8 字节目标地址，该数据是否到达服务端需运行时验证"。

### H4「127.0.0.1 的候选在 IP 拆分时被错误切分」——**不成立，建议作废**
分隔符为 `'.'`，`'127.0.0.1'` 切分正确（['127','0','0','1']）；且切分结果不参与候选选择（只用于代理分支的 NakedSend 八位组）。不存在因拆分导致的候选错误。

---

## 5. 地址与依据表

### 5.1 脚本层（`entry516-five-xor-marshal.bin` / `code_objects.json`；偏移为各函数 co_code 内偏移）

| 结论 | 函数（index）/偏移 | 依据字节（hex） |
|---|---|---|
| import 两条（0xE0=IMPORT_NAME） | CRandom Connect(46) @0x006,0x012；CReselect(52) @0x00C,0x018 | `8f0100 8f0000 e0 0000`（LC -1, LC None, IMPORT_NAME selectserver） |
| `if not serverlist: Refresh(None); return` | (46) @0x030–0x048 | `c10300 e31500 41 … 8f0000 da0100 41 8f0000 55`（E3→0x4B；Refresh 实参 const[0]=None） |
| `if not proxylist: return` | (46) @0x04C–0x05A | `c10400 e30800 41 8f0000 55` |
| proxy/note 赋值（0x5A=ROT_TWO 栈必需） | (46) @0x065–0x07C | `…58 8f0400 da0100 5a 710600 710700`（const[3]='ipPort', const[4]='note'） |
| 5 字段解包键名 | (46) @0x08C–0x0C1；(52) @0x0AE–0x0E3 | 5×(`c1xx00 8fxx00 58`) + `de0500` + `6c0500`（const[5..9]='name','ip','port','serverid','district'） |
| CMXNet 关键字调用 `iType=` | (46) @0x0DD–0x0F2；(52) @0x0FF–0x114 | `…8f0b00 c10200 d90a00 da0201`（const[11]='iType'; CALL 0x0102=2pos+1kw） |
| `if proxy:`（B7→else） | (46) @0x141–0x144；(52) @0x18E–0x191 | `c10600 b7de00`（目标 0x225）/`c10e00 b7f400`（目标 0x288） |
| `p = proxy.find(':')` | (46) @0x158–0x164；(52) @0x19E–0x1AA | `…d91400 8f0e00 da0100`（const[14]=':'=hex 3a） |
| `Connect(proxy[:p], int(proxy[p+1:]))` | (46) @0x170–0x191；(52) @0x1D3–0x1F4 | `c10600 c10f00 0e 851700 c10600 c10f00 8f0f00 3f 0d da0100 da0200`（0x0E=SLICE+2, 0x3F=ADD, 0x0D=SLICE+1） |
| `iplst = ip.split('.')` | (46) @0x192–0x19E；(52) @0x1F5–0x201 | `c10a00 d91800 8f1000 da0100`（const[16]/[14]='.'=hex 2e） |
| 4×`NakedSend(chr(int(iplst[i])))` | (46) @0x1A1–0x1D4；(52) @0x204–0x237 | `851900 8f1100 da0100 36 af2300 … d91a00 851b00 851700 c11000 c11100 58 da0100 da0100 da0100 41`（const[17]=4） |
| 4 字节小端端口 NakedSend | (46) @0x1D5–0x221；(52) @0x238–0x284 | `…8f1200 37 da0100 … 8f1200 3d 8f1200 37 da0100 3f … 8f1300 3d … 8f1400(16777216) 3d … 3f da0100`（const[18]=256, [19]=65536, [20]=16777216） |
| 直连分支仅 `Connect(ip,port)` | (46) @0x225–0x236；(52) @0x288–0x298 | `c10e00 d91600 c10a00 c10b00 da0200 41 a28600` |
| 尾部：ShowConnectingDlg / m_Time+=1 / SetTimeOutCmd / 重试条件 | (46) @0x23A–0x282 | `851c00 da0000 41`、`c10000 30 d91d00 8f0f00 43 5a c51d00`、`…d91e00 da0000 41`、`…d91d00 8f0f00 23 8f0200 950300 e30700 41 851f00 b70e00 41 … d91600 da0000 41`（0x30=DUP, 0x43=INPLACE_ADD, 0x5A=ROT_TWO, 0x23=SUB, CMP arg=3 `!=`） |
| PROXY_CONNECT_TIMEOUT=15 | 类体(50) @0x008–0x00F | `8f0000 980200`（const[0]=15 → STORE_NAME names[2]） |
| SetTimeOutCmd 全文 | (48) @0x000–0x048 | `8f0100 fb0000 … 850000 c10000 8f0200 8f0000 da0300 b71100 … d90400 d90500 c10100 da0200 … c50200` |
| ConnectTestFail（全败→一次性重连） | (49) @0x000–0x04D | `c10000 d90000 da0000 b73000 … 850200 950200 b72000 … 8f0100 c10000 c50300 …` |
| IsConnectTestFail=全败判定 | (40) @0x000–0x02F | `d32900 … af1e00 … d90100 850200 950200 b70800 …` |
| 代理候选前移 pop(m_Time) | GetTestProxyList(44) @0x0A0–0x0C6 | `d32400 850600 c10000 d90700 da0100 36 af1300 … d90800 8f0500 da0100 41 a2b000 40` |
| 服务器列表 shuffle/截取 | GetTestServerList(45) @0x0EC–0x11F | `d90800 … da0100 41 … 8f0500 0e 43 710200`（dianXinList[:5]；const[5]=5, const[6]=2） |
| GetServerInfo 返回 3 元组 | (52) @0x01E–0x030；(35) @0x028–0x040 | `…da0000 6c0300 710400 710500 710500` |
| CReselect 跳过 `'推荐區'` | (52) @0x053–0x067 | `…8f0200 58 8f0300 950200 b70700 41 a24d00`（const[3]=Big5 b1c0aff2b0cf） |
| m_PassPort=(m_Idx,m_Pwd) | (52) @0x153–0x165 | `…d90f00 …d91000 de0200 …c51100` |

### 5.2 常量池（`entry516-five-xor-marshal.bin` 重新解析）

- CRandom Connect（index 46）consts：`[0]=None, [1]=-1, [2]=0, [3]='ipPort', [4]='note', [5]='name', [6]='ip', [7]='port', [8]='serverid', [9]='district', [10]='嘗試連接!!!'(Big5), [11]='iType', [12]=''（空串）, [13]='連接代理!!!!!'(Big5), [14]=':', [15]=1, [16]='.', [17]=4, [18]=256, [19]=65536, [20]=16777216`。
- CReselect Connect（index 52）consts：`…[14]='.', [15]=4, [16]=256, [17]=65536, [18]=16777216`（同构尾部）。
- CRandomConnectMgr 类体（index 50）consts：`[0]=15`（PROXY_CONNECT_TIMEOUT）。
- **注**：`code_objects.json` 的 `const_strings` 字段不含上述整数（其生成脚本 `co_code_analyzer.py` 513–523 行只收集字符串）——凡引用整数常量一律以 marshal 重解析为准。

### 5.3 原生层（IMProtocol.dll，sha256 见 §0.2；只读 objdump）

| 项目 | 地址（VA） | 依据 |
|---|---|---|
| 导出 `IMP_ConnectNsServer` | **0x10003000**（导出表 ordinal 1，Export RVA 0x3000） | `objdump -p`：Name Pointer Table 首项 |
| 函数序言 + `WSAStartup(0x0202, &wsadata)` | 0x10003000–0x1000302F | `push $0x202; push %eax(=&local); call *0x1001f190`；IAT 槽 0x1001f190 = WS2_32 **ord 115**（按 FirstThunk=0x1001f184 的序号导入顺序 [8,9,15,115,…] 推槽位；0x202=MAKEWORD(2,2) 教科书模式） |
| 内联 `strlen(ip)`（arg1） | 0x10003043–0x1000304F | `lea 0x1(%eax),%edx; mov (%eax),%cl; …; cmp %bl,%cl; jne`（ebx=0） |
| ip 拷入本地字符串对象 | 0x10003051–0x1000305C | `push %eax(len); push %esi(ip); lea 0x14(%esp),%ecx; call 0x10002eb0`（thiscall 构造） |
| 连接入口（全局对象 0x10028B90/0x10028B24） | 0x10003088–0x1000309D | `mov 0xc(%ebp),%ecx; mov 0x10(%ebp),%eax; push %ecx; lea …,%edx; mov 0x10028b90,%ecx; call 0x10001660` |
| 空 ip / arg3==0 → 失败返回 | 0x10001664–0x100016E5 | `cmpl $0x0,0x14(%ebx); jbe …; test %eax,%eax; je …`（错误日志路径 0x100016C3） |
| 连接主体（分配 0x10040 对象、vtable 调用） | 0x10005CB0–0x10005D49 | `push $0x10040; call 0x100087b8 …; mov (%ecx),%eax; mov 0x8(%eax),%edx; call *%edx …` |
| **Winsock `connect` 实际调用点** | **0x100049FE**、**0x10004A3E**（IAT 0x1001f1a0 = WS2_32 **ord 4** connect；各 2 处） | `push $0x10(=sizeof sockaddr_in); lea …,%ecx; push %ecx; push %edx; mov %ax,0x16(%esp); call *0x1001f1a0` |
| Winsock `send` 调用点 | 0x10004913、0x10006200、0x100063BE（IAT 0x1001f1a8 = ord 19 send） | `call *0x1001f1a8`（全库共 3 处） |
| WS2_32 导入方式 | Import Directory（.rdata 0x10023D68），FirstThunk 0x1001F184，全部按序号导入 | ord 序列 [8,9,15,115,10,1,101,4,103,19,16,108,3,11,23,112,111,14] |

> 说明：IMProtocol.dll 是 IM（聊天）协议库，其 `IMP_ConnectNsServer` 连接的是 NS 服务器；它与脚本层 `net.CNet.Connect`（netserver.py 使用）是否同一实现/同一通道**未证实**（CNet 的宿主模块未定位，见 §7）。

---

## 6. 需要更新的旧报告段落（`任务A深入-Connect函数破解报告.md`，仅供协调者修改，本次未改动）

1. **§一 映射表**：`0xE3=JUMP_IF_FALSE`→应为 `JUMP_IF_TRUE(非弹栈)`（or 短路证据）；`0x6C=GET_ITER`→应为 `36=GET_ITER`，`0x6C`=UNPACK_SEQUENCE(3B)/BINARY(1B) 双变体（Connect 中为 3B UNPACK，arg=5/3/2）；`0xD3=FOR_ITER`→应为 `AF=FOR_ITER`、`D3=SETUP_LOOP`；`0x58=BINARY_SUBSCR` 保留。另建议补充 §2.5 的新映射（0x30/0x5A/0x43/0x3F/0x37(1B)/0x3D/0x0E/0x0D/0x0B/0x1F/0x40，含多变体警示）。
2. **§2.1 伪代码**：按 §2.1 表逐项重写——#3/#4 两个 if 极性、#5 proxy/note 取值、#9 CMXNet 签名、#12c 代理 Connect 参数、#12e/12f NakedSend 结构、#13 直连分支、新增 #14–#17 尾部（ShowConnectingDlg/m_Time/SetTimeOutCmd/重试条件）。
3. **§2.2 伪代码**：按 §2.2 表重写——两层嵌套循环、`'推荐區'` 跳过条件、GetServerInfo 3 元组、print 语句、m_Nets 重置与 append 位置、NakedSend 同构修正、删除不存在的超时逻辑描述。
4. **§3.1 CMXNet 构造签名**：`CMXNet(ip, port, iType=…)`，无 proxy_separator 参数；`CMXNet.__init__` 调 `net.CNet.__init__(self, ip, port)` 并存 `m_NetType`。
5. **§3.2 属性表**：`m_Nets` 改为实例属性（CConnectMgr.__init__ 建立；CReselect.Connect 重置）；`m_ProxyName` 默认 `''`；`m_ServerInfo=(district,name,ip,port,serverid)`。
6. **§3.3 连接流程步骤表**：步骤 f/g 重写（NakedSend 仅代理分支、在 Connect(代理) 之后、8 字节内容）；补步骤"直连分支仅 Connect(ip,port)"。
7. **§3.4 NakedSend 说明**：整段重写（见 §3.2）：非"连接前单字节握手"，而是代理分支 Connect 后的 8 字节目标地址（推断用途）。
8. **§3.5 "加密/混淆的字典Key"**：整节替换——不是加密，是 **Big5 编码**（附录 B 全表）。
9. **§四 对比表**：删除"代理分隔符 '.'/':'"行（':' 是 proxy.find 的分隔符、'.' 是 ip.split 的分隔符，均非 CMXNet 参数）；"配置key"行更正为 `iType=` 关键字。
10. **§五 下一步**：第 2 条"破解加密字典key"已完成（Big5）；第 3 条剩余未知 opcode 更新为 0x00/0xCF/0x10/extlist 构造等。
11. **§六 输出文件**：`connect_cracked.json` 从未生成（现状确认）。

---

## 7. 未完成与未证实清单

| # | 事项 | 现状 | 需要什么证据 |
|---|---|---|---|
| 1 | NakedSend 与 TCP 建立的时序（代理分支） | 未证实 | 运行时观察（loopback-test-plan E1：Winsock send/connect 事件顺序） |
| 2 | 0x37(1B)=MOD、0x3D(1B)=FLOORDIV 语义 | 推断（强）：端口 LE 编码唯一自洽读法 | 第二样本函数或运行时字节观察 |
| 3 | `PROXY_CONNECT_TIMEOUT=15` 的**单位** | 未证实（值 15 已证实） | 反汇编 `CreatePyCommand`（原生，宿主模块未定位）或运行时计时 |
| 4 | `NakedSend`（`CNet.NakedSend`）原生实现 | 未定位（不在 netserver.py；宿主 .dll 未确定） | 在 mxmain.dll/mx.exe 中定位导出/注册表 |
| 5 | GetTestProxyList `extlist` 字典构造（0x30/0x5A/0x05 组合） | 未解（与 Connect 中 30/5A 语义冲突，疑多变体） | 下一轮 opcode 挖掘（对齐+栈模拟） |
| 6 | GetTestServerList `g_PriorServer` 分支（0xCF、0x10） | 未解 | 同上 |
| 7 | 超时重连的终止条件（m_Time 超过 proxylist 长度时 `pop(0)` 是否 IndexError） | 未证实 | 栈模拟穷举或运行时 |
| 8 | `CNet.Connect` 是否异步（影响 #1） | 未证实 | 反汇编 CNet 实现或运行时 |
| 9 | IMProtocol.dll `IMP_ConnectNsServer` 与脚本层连接的关系（同一通道？） | 未证实 | 交叉引用分析（超出 P3 范围） |
| 10 | 0x30/0x5A 与 v4.3 表 A 标注（POP_TOP/NOP）的冲突 | 本报告按栈分析在 netserver.py 函数代码对象内否定表标注；**不覆盖表，待协调者复核**（支持已证实的"多变体 S 盒"结论） | 跨模块多样本挖掘 |
| 11 | `ip` 字段是否可能含多 IP（旧报告"负载均衡"猜测） | 未证实（字节层只见 split('.') 取 4 八位组；无多 IP 处理逻辑） | 服务器配置数据格式分析（P4/task-d 范围） |

---

## 附录 A：执行步骤（命令级，可复现）

```bash
# 0) 环境与只读确认
cd /home/user/MXSJ_TW_2022 && git status --short   # 干净
python3 --version                                  # 3.11.2
objdump --version | head -1                        # GNU objdump 2.40

# 1) 输入哈希
sha256sum work/.../brief-P3-connect-path.md work/.../README.md \
          work/.../任务A深入-Connect函数破解报告.md work/.../mapping_table_v4.json \
          work/.../code_objects.json work/.../entry516-five-xor-marshal.bin \
          work/.../netserver_py_decompiled.md work/.../loopback-test-plan-20261010.md \
          IMProtocol.dll

# 2) marshal 重解析（恢复整数常量池）
#    解析器 = decoder-artifacts/decode_entry516.py 的 MarshalReader 逻辑
#    （本会话在临时目录复刻，未改 tools/；对 entry516-five-xor-marshal.bin 只读）
python3 parse_marshal.py        # root=code-object dict, pos==len 校验通过
python3 dump_consts.py          # 输出全部 59 个 code object 的 names/varnames/consts(含 int)

# 3) v4.3 反汇编（脚本见附录 D）
python3 dis_v43.py '/CRandomConnectMgr/Connect' '/CReselectConnectMgr/Connect' \
                  '/CRandomConnectMgr/SetTimeOutCmd' '/CConnectMgr/IsConnectTestFail' ...
#    输出：每函数唯一 end-exact 解；A2 绝对 / B7,E3,AF,D3,E5 = pos+3+arg 全部 OK

# 4) Big5 解码
python3 -c "print(bytes.fromhex('b9c1b8d5b373b1b5212121').decode('big5'))"  # 嘗試連接!!!

# 5) IMProtocol.dll 只读反汇编
objdump -p IMProtocol.dll | sed -n '/Export Address Table/,/^$/p'      # IMP_ConnectNsServer RVA 0x3000
objdump -p IMProtocol.dll | grep -A25 "DLL Name: WS2_32"               # 序号导入表
objdump -d --start-address=0x10003000 --stop-address=0x100030C9 IMProtocol.dll
objdump -d --start-address=0x10001660 --stop-address=0x100016E8 IMProtocol.dll
objdump -d --start-address=0x10005CB0 --stop-address=0x10005D50 IMProtocol.dll
objdump -d IMProtocol.dll | grep -n "call.*\*0x1001f1a0"               # connect → 0x100049FE, 0x10004A3E
objdump -d IMProtocol.dll | grep -n "call.*\*0x1001f1a8"               # send → 0x10004913, 0x10006200, 0x100063BE
```

## 附录 B：Big5 常量解码表（"混淆字符串"全部为 Big5 繁体中文）

| hex | Big5 解码 | 出现位置 |
|---|---|---|
| `b9c1b8d5b373b1b5212121` | 嘗試連接!!! | CRandom.Connect const[10]（LOG 格式） |
| `b9c1b8d5c2e0aa41b373b1b5212121` | 嘗試轉服連接!!! | CReselect.Connect const[8]（print） |
| `b373b1b5a54eb27a2121212121` | 連接代理!!!!! | 两函数 const（print/LOG_DEBUG） |
| `b1c0aff2b0cf` | 推荐區 | CReselect 跳过条件 |
| `b971ab48` | 電信 | GetTestServerList 区名分类 |
| `baf4b371` | 網通 | 同上 |
| `a6dbb0cabfefbedc` | 自動選擇 | GetTestProxyList 代理名比较 |
| `a5bfa662b373b1b5aa41b0c8beb9a4a42e2e2e2e` | 正在連接服務器中.... | ShowConnectingDlg |
| `aaf0a65e` | 返回 | ShowConnectingDlg 按钮 |
| `b373b1b5aa41b0c8beb9a5a2b1d1` | 連接服務器失敗 | CConnectMgr.ConnectTestFail |
| `bd54a977` | 確定 | 同上按钮 |

## 附录 C：关键区段反汇编摘录（v4.3，含未定字节原样标注）

```
# CRandomConnectMgr.Connect @0x1D5–0x221（端口 NakedSend，4 字节小端）
0x1D5  c10e00  LOAD_FAST    netobj
0x1D8  d91a00  LOAD_ATTR    NakedSend
0x1DB  851b00  LOAD_NAME    chr
0x1DE  c10b00  LOAD_FAST    port
0x1E1  8f1200  LOAD_CONST   256
0x1E4  37      BINARY_MODULO(推断)
0x1E5  da0100  CALL         chr(arg=1)
0x1E8  851b00  LOAD_NAME    chr
0x1EB  c10b00  LOAD_FAST    port
0x1EE  8f1200  LOAD_CONST   256
0x1F1  3d      BINARY_FLOORDIV(推断)
0x1F2  8f1200  LOAD_CONST   256
0x1F5  37      BINARY_MODULO(推断)
0x1F6  da0100  CALL         chr(arg=1)
0x1F9  3f      BINARY_ADD
...（65536 / 16777216 两组同构）...
0x21E  da0100  CALL         NakedSend(arg=1)
0x221  41      POP_TOP

# CRandomConnectMgr.Connect @0x23A–0x282（尾部：超时与重试）
0x23A  851c00  LOAD_NAME    ShowConnectingDlg
0x23D  da0000  CALL         (arg=0)
0x240  41      POP_TOP
0x241  c10000  LOAD_FAST    self
0x244  30      DUP_TOP      (栈分析必需)
0x245  d91d00  LOAD_ATTR    m_Time
0x248  8f0f00  LOAD_CONST   1
0x24B  43      INPLACE_ADD
0x24C  5a      ROT_TWO      (栈分析必需)
0x24D  c51d00  STORE_ATTR   m_Time
0x250  c10000  LOAD_FAST    self
0x253  d91e00  LOAD_ATTR    SetTimeOutCmd
0x256  da0000  CALL         (arg=0)
0x259  41      POP_TOP
0x25A  c10000  LOAD_FAST    self
0x25D  d91d00  LOAD_ATTR    m_Time
0x260  8f0f00  LOAD_CONST   1
0x263  23      BINARY_SUBTRACT
0x264  8f0200  LOAD_CONST   0
0x267  950300  COMPARE_OP   !=
0x26A  e30700  JUMP_IF_TRUE -> 0x274   (or 短路)
0x26D  41      POP_TOP
0x26E  851f00  LOAD_NAME    g_AutoProxy
0x271  b70e00  POP_JUMP_IF_FALSE -> 0x282
0x274  41      POP_TOP
0x275  c10000  LOAD_FAST    self
0x278  d91600  LOAD_ATTR    Connect
0x27B  da0000  CALL         (arg=0)
0x27E  41      POP_TOP
0x27F  e50100  JUMP_FORWARD -> 0x283
0x282  41      POP_TOP
0x283  8f0000  LOAD_CONST   None
0x286  55      RETURN_VALUE
```

## 附录 D：反汇编器脚本（本会话使用；只读，未入库）

```python
#!/usr/bin/env python3
"""v4.3-taskB disassembler with alignment-fit for dual/unknown opcodes. Read-only.
用法: python3 dis_v43.py <code路径过滤词...>   # 配合 marshal 解析生成的 all_codes.pkl
"""
import struct, sys, pickle

OPS = {   # mapping_table_v4.json (4.3-taskB) 表A+表B
    0x05:('BINARY_?',1), 0x06:('PUSHER_?',1), 0x08:('IMPORT_STAR',1), 0x09:('BINARY_?',1),
    0x15:('BINARY_?',1), 0x23:('BINARY_SUBTRACT?',1), 0x30:('POP_TOP?',1), 0x36:('GET_ITER',1),
    0x38:('LOAD_LOCALS',1), 0x3F:('BINARY_?',1), 0x41:('POP_TOP',1), 0x42:('BUILD_CLASS',1),
    0x43:('BINARY_?|NOP_?',1), 0x55:('RETURN_VALUE',1), 0x58:('BINARY_SUBSCR',1), 0x5A:('NOP_?',1),
    0x71:('STORE_FAST',3), 0x72:('LOAD_CONST?',3), 0x85:('LOAD_NAME',3), 0x8F:('LOAD_CONST',3),
    0x95:('COMPARE_OP',3), 0x98:('STORE_NAME',3), 0xA2:('JUMP_ABSOLUTE',3), 0xAA:('LOAD_NAME',3),
    0xAD:('IMPORT_FROM',3), 0xAF:('FOR_ITER',3), 0xB7:('POP_JUMP_IF_FALSE',3),
    0xBB:('LOAD_CONST',3), 0xC1:('LOAD_FAST',3), 0xC4:('STORE_NAME',3), 0xC5:('STORE_ATTR',3),
    0xCA:('BUILD_LIST',3), 0xD3:('SETUP_LOOP',3), 0xD9:('LOAD_ATTR',3), 0xDA:('CALL_FUNCTION',3),
    0xDE:('BUILD_TUPLE',3), 0xE0:('IMPORT_NAME',3), 0xE3:('JUMP_IF_TRUE?',3), 0xE5:('JUMP_FORWARD',3),
    0xEA:('LOAD_?',3), 0xFB:('MAKE_FUNCTION',3), 0x91:('LOAD_GLOBAL',3), 0xBF:('STORE_GLOBAL',3),
}
DUAL = {0x37, 0x6C, 0x90}                      # 双变体：尝试 3B/1B
UNKNOWN = {0x40,0x0E,0x0D,0x3D,0x0B,0x1F,0x31,0xCF,0x10,0xC0,0x39,0x9A,0xFC,0x20}
JMP_ABS = {0xA2}; JMP_REL3 = {0xAF,0xD3,0xE5,0xB7}; JMP_E3 = {0xE3}
CMP = ['<','<=','==','!=','>','>=','in','not in','is','is not','exc-match','BAD']

def disasm(code, names, consts, varnames, max_solutions=8):
    n = len(code)
    def cand(pos):
        b = code[pos]
        if b in OPS: yield OPS[b][1], OPS[b][0], b, False
        elif b in DUAL:
            yield 3, 'UNPACK_SEQ?', b, True; yield 1, 'BINARY_/STORE_SUBSCR?', b, True
        elif b in UNKNOWN:
            yield 1, 'UNK', b, True; yield 3, 'UNK', b, True
    solutions = []
    def bt(pos, insns):
        if len(solutions) >= max_solutions: return
        if pos == n: solutions.append(list(insns)); return
        if pos > n: return
        for sz, name, b, amb in cand(pos):
            arg = None
            if sz == 3:
                if pos+3 > n: continue
                arg = code[pos+1] | (code[pos+2] << 8)
                if b in OPS and not amb:            # 参数合理性（CALL 允许 kwarg 高字节）
                    if b == 0xDA:
                        if (arg & 0xFF) > 12 or (arg >> 8) > 4: continue
                    elif b == 0x95:
                        if arg > 11: continue
                    elif b in (0x85,0xAA,0x98,0xC4,0xC5,0xD9,0xE0,0xAD):
                        if arg >= len(names): continue
                    elif b in (0x8F,0xBB,0x72):
                        if arg >= len(consts)+2: continue
                    elif b in (0x71,0xC1):
                        if arg >= len(varnames) and arg >= 4: continue
            insns.append((pos, sz, name, b, arg, amb)); bt(pos+sz, insns); insns.pop()
    bt(0, [])
    def score(sol):                                  # 排序：跳转全对齐 > 未知3B少
        starts = {p for p,_,_,_,_,_ in sol}
        good = bad = 0
        for p,sz,name,b,arg,amb in sol:
            if arg is None: continue
            t = arg if b in JMP_ABS else (p+3+arg if b in JMP_REL3 or b in JMP_E3 else None)
            if t is None: continue
            if t in starts or t == n: good += 1
            else: bad += 1
        unk3 = sum(1 for _,sz,name,_,_,_ in sol if name=='UNK' and sz==3)
        unk1 = sum(1 for _,sz,name,_,_,_ in sol if name=='UNK' and sz==1)
        return (-bad, good, -unk3, -unk1)
    solutions.sort(key=score); return solutions
# show()/main：按 names/varnames/consts 注释输出（含越界警告与 MISALIGNED 标记），略——
# 完整输出逻辑与本报告附录 C 格式一致。
```

---

**P3 执行者**：Arena.ai Agent Mode 会话
**完成时间**：2026-10-10 11:21 UTC
**一句话结论**：按 v4.3 复核，两个 Connect 的真实流程已端点精确重建——NakedSend 并非"连接前单字节 0x3E"，而是代理分支 Connect(代理) 之后发送的 8 字节目标地址（4 个 IP 八位组 + 4 字节小端端口，3134→`3E 0C 00 00`），直连分支无任何 NakedSend；`ip.split('.')` 对 127.0.0.1 切分正确且不用于候选迭代；`PROXY_CONNECT_TIMEOUT=15`，超时经 nexttest→Connect() 前移代理候选并重洗服务器列表，全部失败时一次性整轮重连后弹窗——H3 前提不成立（建议改写），H4 不成立（建议作废）。
