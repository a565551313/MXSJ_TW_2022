# N4 网络退修：有限候选原行摘录

实际作者：全新 N4 会话（非旧 E）。仅静态读取/比较，不执行或导入候选，不访问业务 URL。
来源：交接 9b0dea799768aaacbb967ffc59f45753970752be；恢复白名单仅 3176/2170/871/516。
这是小证据摘录，不是完整源码。R 行含恢复头；每个 Rxxxx| 分隔符后的内容逐字保留。
恢复命令：`/home/user/n4-env/bin/python tools/decompiler/recover_entries.py --out /home/user/n4-recovery --entries 3176,2170,871,516 --decompile-timeout 30 --report /home/user/n4-recovery/report.json`。
默认 Big5 开启、uncompyle6；Python 3.11.2 / uncompyle6 3.9.3 / xdis 6.1.8 / spark-parser 1.9.0 / click 8.5.0。
只移除精确前六行作正文比较；稳定头 1–4、6 与 A 前序收据逐字相同，只有生成时间行 5 可不同。
四正文摘要 4/4 等于前序 A/E；871/516 正文另与仓库无头候选逐字节相同。未恢复 main；main 旧协审仅供 N2 核对。
原包/参数/工具摘要及逐条结果见 `N4_reproduction.json.template`；1288 未定点提取，未读其 payload。

- entry 3176 `script/net.py`；完整候选 SHA256 `fbf1282b883d9724614a934941f49b71f1b34249870e4baf653cde2577647984`；正文 SHA256 `4cad123e0121c3c18cf24a6af59d1827da28517478b5c92e90f98bf664092c50`；1364 行；baseline/decompile_ok/source。
- entry 2170 `script/connect.py`；完整候选 SHA256 `6d49e1b3a7f2667fd9dfd898ddcc42806c9035679a5ad532079c63564a15d684`；正文 SHA256 `0a46ea6fb77879332c53531a1a746556782b9fc48a1fb01f6330e97c8c775e24`；295 行；baseline/decompile_ok/source。
- entry 871 `script/netquicklogin.py`；完整候选 SHA256 `cd9d3167c9602cbf76b1c110dd54884e78217fa700f5ec5a7709a7231172b215`；正文 SHA256 `36def1780a9bb229e98b850339eee91827ed6f6f972f330f52fa3f23183597b9`；313 行；baseline/decompile_ok/source。
- entry 516 `script/login/netserver.py`；完整候选 SHA256 `736cda1e2ea8ca4b376cf028c5d424938a09af9bf1053533ebd828d06b2b8741`；正文 SHA256 `1fccc33d2d20540680c6af62e2bfdcf850291a855ed4bf626374262b8702c94b`；584 行；baseline/decompile_ok/source。

## n4_net_lowest · entry 3176 · R55–R70

```text
R0055|def LowestUnpackParams():
R0056|    global MAX_PROCESS_SERVER_CMD_TIMES
R0057|    global MAX_PROCESS_SERVER_CMD_TIME_PER_FRAME
R0058|    global MAX_PROCESS_SERVER_CMD_TIME_PER_TIME
R0059|    global MIN_UNPACK_PACKET_NUM_PER_FRAME
R0060|    global UNPACK_PACKET_NUM_PER_PROCESS
R0061|    import setfps
R0062|    GetNet().SetProcessSvrCmdNumPerFrame(2)
R0063|    iRate = setfps.GetCurFrame() / 30
R0064|    MAX_PROCESS_SERVER_CMD_TIME_PER_FRAME = 0.016 / iRate
R0065|    MAX_PROCESS_SERVER_CMD_TIMES = 2 / iRate
R0066|    MAX_PROCESS_SERVER_CMD_TIME_PER_TIME = MAX_PROCESS_SERVER_CMD_TIME_PER_FRAME / 2 / iRate
R0067|    UNPACK_PACKET_NUM_PER_PROCESS = 2 / iRate
R0068|    MIN_UNPACK_PACKET_NUM_PER_FRAME = 2 / iRate
R0069|    GetNet().SetProcessSvrCmdNumPerFrame(UNPACK_PACKET_NUM_PER_PROCESS)
R0070|    return
```

## n4_net_name · entry 3176 · R696–R708

```text
R0696|    def GetServerName(self):
R0697|        import selectserver, C_sys
R0698|        cs = self.m_IP + ' ' + str(self.m_Port)
R0699|        f = misc.OpenFile(selectserver.SERVERINI, 'rb')
R0700|        s = f.read()
R0701|        s = C_sys.RecordString(s)
R0702|        serverinfo = [_[1] for x in s.splitlines() if x.strip() != '']
R0703|        for server in serverinfo:
R0704|            if server.find(cs) != -1:
R0705|                infos = server.split(' ')
R0706|                return infos[0]
R0707|
R0708|        return ''
```

## n4_net_error · entry 3176 · R856–R873

```text
R0856|    def OnError(self, msg=None):
R0857|        import main, netquicklogin
R0858|        if not netquicklogin.IsQuickConnect() and not netquicklogin.CanQuickConnect():
R0859|            main.HideWindow(exit=False)
R0860|        if not self.m_Hello:
R0861|            self.OnConnectFail()
R0862|            return
R0863|        if hasattr(self, 'm_IsRelogin') and self.m_IsRelogin:
R0864|            return
R0865|        if hasattr(self, 'm_IsExit') and self.m_IsExit:
R0866|            return
R0867|        if not netquicklogin.IsQuickConnect():
R0868|            if netquicklogin.CanQuickConnect():
R0869|                netquicklogin.Connect(sReason='網絡中斷-2')
R0870|            else:
R0871|                LOG('連接錯誤')
R0872|                ShowError(msg)
R0873|        return
```

## n4_net_prepare · entry 3176 · R901–R904

```text
R0901|    def PacketPrepare(self, a):
R0902|        CNetClient.PacketPrepare(self, a)
R0903|        self.m_NetHead = a
R0904|        return
```

## n4_net_queue · entry 3176 · R1323–R1343

```text
R1323|    def Loop(self):
R1324|        if not g_Net:
R1325|            self.End()
R1326|            return
R1327|        oQueue = None
R1328|        if self.m_oHQueue:
R1329|            oQueue = self.m_oHQueue
R1330|        elif self.m_oLQueue:
R1331|            self.m_oLQueue = oQueue
R1332|        if not oQueue:
R1333|            self.End()
R1334|        else:
R1335|            for _ in range(self.PROCESS_NUM_PER_TIME):
R1336|                if oQueue:
R1337|                    (iCmd, oServerCommand) = oQueue.popleft()
R1338|                    oFunc = g_Net.GetFunc(iCmd)
R1339|                    if oFunc and callable(oFunc):
R1340|                        print '處理協議:', iCmd
R1341|                        oFunc(oServerCommand)
R1342|
R1343|        return
```

## n4_quick_reset · entry 871 · R13–R40

```text
R0013|QUICKLOGIN_SECOND = 10
R0014|g_LoginKey = None
R0015|g_DoRestart = True
R0016|g_oStartQucikTimer = None
R0017|g_bCanDoQuickLogin = False
R0018|g_Timer = None
R0019|g_ConnectObj = None
R0020|g_MaintainFlag = False
R0021|g_bHasClickQuickLogin = False
R0022|g_bHasQuickLoginFail = False
R0023|
R0024|def ModuleReset():
R0025|    global g_ConnectObj
R0026|    global g_DoRestart
R0027|    global g_LoginKey
R0028|    global g_MaintainFlag
R0029|    global g_Timer
R0030|    global g_bCanDoQuickLogin
R0031|    global g_oStartQucikTimer
R0032|    g_LoginKey = None
R0033|    g_DoRestart = True
R0034|    g_oStartQucikTimer = None
R0035|    g_bCanDoQuickLogin = False
R0036|    g_Timer = None
R0037|    g_ConnectObj = None
R0038|    g_MaintainFlag = False
R0039|    g_bHasClickQuickLogin = False
R0040|    return
```

## n4_quick_clear_force · entry 871 · R73–R80

```text
R0073|def S2CForceLoginOut(netobj):
R0074|    global g_LoginKey
R0075|    itype = netobj.UnpackInt(1)
R0076|    g_LoginKey = None
R0077|    import juben
R0078|    if juben.IsPlayJuben():
R0079|        juben.StopJuBen(True)
R0080|    return
```

## n4_quick_clear_delete · entry 871 · R92–R99

```text
R0092|def S2CDelLoginKey(netobj):
R0093|    global g_LoginKey
R0094|    g_LoginKey = None
R0095|    import juben
R0096|    if juben.IsPlayJuben():
R0097|        juben.StopJuBen(True)
R0098|    return
R0099|
```

## n4_quick_logout · entry 871 · R192–R197

```text
R0192|def NormalLogout():
R0193|    global g_LoginKey
R0194|    if g_LoginKey and net.g_Net:
R0195|        C2SSendLoginKey(g_LoginKey)
R0196|        g_LoginKey = None
R0197|    return
```

## n4_quick_connect · entry 871 · R206–R244

```text
R0206|def Connect(showdlg=True, sReason=''):
R0207|    import selectserver
R0208|    proxy = selectserver.g_Proxy
R0209|    ip = selectserver.g_LastVisit[2]
R0210|    port = selectserver.g_LastVisit[3]
R0211|
R0212|    def cancel(dlg):
R0213|        dlg.Release()
R0214|        ClearConnectTimer()
R0215|        net.ShowError(None)
R0216|        return
R0217|
R0218|    def done(dlg, i):
R0219|        dlg.SetMessage('網絡異常斷開，嘗試重新連接中' + '.' * (i % 9))
R0220|        return (i + 1,)
R0221|
R0222|    import commondialog
R0223|    if showdlg:
R0224|        dlg = commondialog.ShowMessageBox('網絡異常斷開，嘗試重新連接中', '取消', cancel)
R0225|        dlg.CreatePyCommand(15, done, 0)
R0226|    StartConnectTimer(proxy, ip, port)
R0227|    return
R0228|
R0229|
R0230|def ClearConnectTimer():
R0231|    global g_Timer
R0232|    if g_Timer:
R0233|        g_Timer.Release()
R0234|    g_Timer = None
R0235|    return
R0236|
R0237|
R0238|def IsQuickConnect():
R0239|    return g_Timer
R0240|
R0241|
R0242|def CanQuickConnect():
R0243|    import hero
R0244|    return g_LoginKey and hero.g_ID
```

## n4_server_refresh · entry 516 · R68–R100

```text
R0068|def RefreshServerInfo():
R0069|    import permission, cfg, net, misc
R0070|    if not permission.GetSpecialVersion() and not permission.GetOverdoVersion():
R0071|        try:
R0072|            tm = float(cfg.GetData('mx.ini', 'Game', 'refreshserver'))
R0073|        except:
R0074|            tm = None
R0075|        else:
R0076|            now = misc.Time()
R0077|            if tm is None or tm > now or now - tm > 1200:
R0078|                import selectserver
R0079|                selectserver.Refresh(None)
R0080|
R0081|    def getMsg(data, flag):
R0082|        global g_ErrorAnsMsg
R0083|        if flag and len(data) > 0:
R0084|            try:
R0085|                (head, body) = data.split('\r\n\r\n')
R0086|                dErrorInfo = {}
R0087|                lstErrorInfo = body.split('\r\n')
R0088|                for sInfo in lstErrorInfo:
R0089|                    (sServerID, sErrorInfo) = sInfo.split(':', 1)
R0090|                    dErrorInfo[sServerID] = sErrorInfo
R0091|
R0092|                g_ErrorAnsMsg = dErrorInfo
R0093|            except ValueError:
R0094|                pass
R0095|
R0096|        return
R0097|
R0098|    web = cfg.GetData('update.ini', 'Setting', 'BulletinURL')
R0099|    net.CHttpObject(web, 'get', getMsg)
R0100|    return
```

## n4_server_prepare · entry 516 · R280–R295

```text
R0280|class CMXNet(net.CNet):
R0281|
R0282|    def __init__(self, ip, port, iType=0):
R0283|        net.CNet.__init__(self, ip, port)
R0284|        self.m_NetType = iType
R0285|        return
R0286|
R0287|    def PacketPrepare(self, icmd):
R0288|        net.CNet.PacketPrepare(self, icmd)
R0289|        self.m_iCmd = icmd
R0290|        return
R0291|
R0292|    def OnServerCmd(self, icmd):
R0293|        if hasattr(self, 'm_Hello'):
R0294|            net.CNet.OnServerCmd(self, icmd)
R0295|        return
```

## n4_server_connect · entry 516 · R426–R476

```text
R0426|    def Connect(self):
R0427|        import selectserver, loginhello
R0428|        serverlist = self.GetTestServerList()
R0429|        proxylist = self.GetTestProxyList()
R0430|        if not serverlist:
R0431|            selectserver.Refresh(None)
R0432|            return
R0433|        if not proxylist:
R0434|            return
R0435|        proxydata = proxylist[0]
R0436|        proxy, note = proxydata['ipPort'], proxydata.get('note')
R0437|        for d in serverlist:
R0438|            (name, ip, port, serverid, district) = (
R0439|             d['name'], d['ip'], d['port'], d['serverid'], d['district'])
R0440|            LOG('嘗試連接!!!', name, serverid, bool(proxy))
R0441|            netobj = CMXNet(ip, port, iType=loginhello.TEST_HELLO)
R0442|            netobj.m_Hello = False
R0443|            netobj.m_IsFail = False
R0444|            netobj.m_ProxyName = ''
R0445|            netobj.m_SvrName = name
R0446|            netobj.m_ServerInfo = (district, name, ip, port, serverid)
R0447|            self.m_Nets.append(netobj)
R0448|            if proxy:
R0449|                LOG_DEBUG('連接代理!!!!!', proxy, note)
R0450|                p = proxy.find(':')
R0451|                netobj.m_Proxy = proxy
R0452|                netobj.Connect(proxy[:p], int(proxy[p + 1:]))
R0453|                iplst = ip.split('.')
R0454|                for i in xrange(4):
R0455|                    netobj.NakedSend(chr(int(iplst[i])))
R0456|
R0457|                netobj.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
R0458|            else:
R0459|                netobj.Connect(ip, port)
R0460|
R0461|        ShowConnectingDlg()
R0462|        self.m_Time += 1
R0463|        self.SetTimeOutCmd()
R0464|        if self.m_Time - 1 != 0 or g_AutoProxy:
R0465|            self.Connect()
R0466|        return
R0467|
R0468|    def SetTimeOutCmd(self):
R0469|
R0470|        def nexttest(obj):
R0471|            obj.Connect()
R0472|            return
R0473|
R0474|        if getattr(self, 'm_TimeoutCmd', None):
R0475|            self.m_TimeoutCmd.Release()
R0476|        self.m_TimeoutCmd = self.CreatePyCommand(self.PROXY_CONNECT_TIMEOUT, nexttest)
```

## n4_server_reselect_hello · entry 516 · R510–R516

```text
R0510|        for d in lst:
R0511|            (name, ip, port, serverid, district) = (
R0512|             d['name'], d['ip'], d['port'], d['serverid'], d['district'])
R0513|            print '嘗試轉服連接!!!', name, ip, port, serverid, district
R0514|            netobj = CMXNet(ip, port, iType=loginhello.RESELECT_HELLO)
R0515|            netobj.m_Hello = False
R0516|            netobj.m_IsFail = False
```

## n4_connect_attempts · entry 2170 · R164–R197

```text
R0164|def DoConnect(idx, pwd, proxy_port_ip_list, proxy):
R0165|    global g_DelaySecond
R0166|    if g_DelaySecond <= 0:
R0167|        import main
R0168|        main.RestarConfirmEx(idx, pwd, proxy_port_ip_list)
R0169|        return
R0170|
R0171|    def Success(netobj):
R0172|        print '成功連接到了：', netobj.GetServerName(), netobj.GetInfo()
R0173|        ClearAttempt()
R0174|        import main, selectserver
R0175|        selectserver.g_Proxy = netobj.m_Proxy
R0176|        main.RestarConfirm(netobj.m_IP, netobj.m_Port, idx, pwd)
R0177|        return
R0178|
R0179|    def Fail(netobj):
R0180|        import main
R0181|        main.RestarConfirmEx(idx, pwd, proxy_port_ip_list)
R0182|        return
R0183|
R0184|    if proxy:
R0185|        (_, port, ip) = proxy_port_ip_list[0]
R0186|        ConnectAttempt(ip, port, proxy, Fail, g_DelaySecond, Fail)
R0187|        (_, port, ip) = proxy_port_ip_list[1]
R0188|        ConnectAttempt(ip, port, proxy, Fail, g_DelaySecond, Fail)
R0189|    else:
R0190|        import net
R0191|        if IsDianXin(net.g_Net.m_IP):
R0192|            target_idx = 0
R0193|        else:
R0194|            target_idx = 1
R0195|        (proxy, port, ip) = proxy_port_ip_list[target_idx]
R0196|        ConnectAttempt(ip, port, proxy, Fail, g_DelaySecond, Fail)
R0197|    return
```
