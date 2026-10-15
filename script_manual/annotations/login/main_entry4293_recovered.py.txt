# MXSJ 恢复产物 · script.fls entry 4293 (id=0xd93f1735)
# co_filename(原始)='script/main.py'
# 转译阶段=baseline  密钥修复=False
# keys=[234, 15, 89, 63, 82] bounds=[9772, 19571, 29383, 39151]
# 生成时间=2026-10-15T14:41:11Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# uncompyle6 version 3.9.4.dev0
# Python bytecode version base 2.5 (62131)
#   Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\main.py
import globalhotkeyfunc, key, C_sys, gamectrl, time, log, permission, mdtasktrace
g_DisableHotKey = False
g_RelogServerName = None
g_RelogTips = ''
g_IsDgwConnect = False
g_MiniVersion = 0
g_LangVersion = 0
g_iCurFrame = 0
g_IgnoreResLoaderCheck = False
Quit = False

def InitSize():
    import game, gamectrl
    gamectrl.InitUIStyle()
    game.FullScreen(0)
    return


def IsIgnoreResLoaderCheck():
    global g_IgnoreResLoaderCheck
    return g_IgnoreResLoaderCheck


def SetIgnoreResLoaderCheck(bCheck):
    global g_IgnoreResLoaderCheck
    g_IgnoreResLoaderCheck = bCheck
    return


def StartStep1(mode=0):
    import charpath, cfg
    cfg.SetCanSave(False)
    charpath.InitUseNewRes()
    gamectrl.OnGameStart(mode)
    return


def Start(mode=0):
    StartStep1(mode)
    import innerversion, misc
    if innerversion.IsInnerVer() and not misc.IsTWServer():
        InnerStart()
    return


def InnerStart():
    import gmcommanddata
    gmcommanddata.UIMix()
    gmcommanddata.CGetMXCCName()
    return


def OutPutError():
    import time, os
    if not os.path.exists('err'):
        os.makedirs('err')
    txt = '%d-%d-%d-%d-%d-%d' % time.localtime(time.time())[:6]
    filename = 'err/%s.txt' % txt
    return


def CloseGame():
    import statisticsignal
    statisticsignal.Emit(statisticsignal.SS_CLOSE_GAME)
    import yardviewsignal
    yardviewsignal.Emit(yardviewsignal.SS_CLOSE_GAME_SAVE2LOCAL)
    import netquicklogin, net
    netquicklogin.NormalLogout()
    if net.g_Net:
        net.g_Net.m_IsExit = True
    import serversource
    serversource.WhenQuitGame()
    import blacklist
    blacklist.DestroyScaner()
    SaveServerData()
    SaveClientData()
    import audio
    audio.ReleaseChatAudio()
    import permission
    if permission.IsOpenNewSoundBnk():
        import newsoundinterface
        newsoundinterface.CloseSound()
    import juben
    juben.CheckJubenSkipAndEsc()
    import toolkit
    toolkit.ClearRegCode()
    import crashrpt
    crashrpt.CrashUninstall()
    import recordvideo
    recordvideo.CRecordVideo.DealEnd()
    import pubdyflyer, pubbigdatadefines, mdbigdata
    if mdbigdata.GetBigDataModel().GetValue('iCloseEventLogSend') == 0:
        mdbigdata.GetBigDataModel().OnChange('iCloseEventLogSend', 1)
        pubdyflyer.C2BLogEvent(pubbigdatadefines.CLOSE_EVENT)

    def DoCloseGame(obj, dummy=None):
        global Quit
        Quit = True
        key.RegisterHotKey(key.LEFT_BUTTON_UP)
        key.RegisterHotKey(key.LEFT_BUTTON_DOWN)
        key.RegisterHotKey(key.RIGHT_BUTTON_UP)
        import device, item, war
        device.ReleaseDevice()
        item.ReleaseAllInterfaceCallback()
        import qcprofilemgr
        if qcprofilemgr.IsQCProfile():
            qcprofilemgr.GetQCProfileManager().StopProfile()
        if permission.GMCanAdopt():
            import newcommandmgr
            newcommandmgr.SVNOnlyUpdate()
        return

    import interface
    obj = interface.CBaseObject(None)
    obj.CreatePyCommand(30, DoCloseGame, obj)
    import gameprofile
    gameprofile.EndCheckDlgShowTime()
    print 'End'
    return


def SaveServerData():
    import net, dlgbaozi, clickcounter, hotkeycounter, dlgsale, imnewgamemgr, cursorclicklog, scheduleclicklog, activityclicklog, personaccoutlog
    netobj = net.g_Net
    if netobj:
        call_lst = (
         dlgbaozi.C2SSendBaozi, clickcounter.C2SSendLog, hotkeycounter.C2SSendHotKeyCount, dlgsale.C2SSavePriceLst,
         imnewgamemgr.C2SSendImNewGameClickLog, cursorclicklog.GetCurSorClickLog().SendLog,
         scheduleclicklog.GetScheduleClickLog().SendLog, activityclicklog.GetActivityClickLog().SendLog,
         personaccoutlog.GetClickLogMgr().SendLog)
        for callback in call_lst:
            if callback():
                netobj.ProcessServerCmd()

        return True
    return False


def Restart(flag=0, logout=True):
    global Loop
    global RestartTimes
    global g_DelayF11
    global g_DelayF9
    global g_ExitDialog
    import chatwnd, fishgame, seawar, skillbar, magicmgr
    SaveServerData()
    SaveClientData()
    fishgame.GameOver()
    magicmgr.CMagicNameMgr.Clear()
    seawar.EndWar()
    skillbar.ShowMagicBar(None)
    chatwnd.Show(False)
    ClearHotKey()
    key.RegisterHotKey(key.VK_CLOSE)
    import blacklist
    blacklist.DestroyScaner()
    C_sys.ClearAllCommand()
    import cardgame
    cardgame.ClearAllWarInfo()
    import world
    world.ClearAllObject()
    import map
    map.Clear()
    import sound
    sound.StopAllLoopSample()
    if logout:
        import netquicklogin
        netquicklogin.NormalLogout()
    import clientcommand
    if permission.GMCanAdopt():
        clientcommand.GMLog()
    import net
    if net.g_Net:
        net.g_Net.ProcessServerCmd()
        net.g_Net.Disconnect()
    net.g_Net = net.CFakeNet()
    import pubhttp
    pubhttp.Clear()
    import pubhttps
    pubhttps.Clear()
    g_ExitDialog = None
    import blacklist
    blacklist.g_SentType = {}
    import audioroom
    audioroom.GetMgr().DoLogout()
    import netprotocol
    netprotocol.ResetProtocol()
    ClearCmdParam()
    import getzminfo
    getzminfo.StopSend()
    Loop = AfterRestart
    RestartTimes = 2
    if g_DelayF9:
        g_DelayF9.Release()
        g_DelayF9 = None
    if g_DelayF11:
        g_DelayF11.Release()
        g_DelayF11 = None
    import interface
    interface.g_ActiveEdit = None
    interface.g_DefaultEdit = None
    chatpanel = chatwnd.g_MainPanel
    import resetcontrol
    bIsQuickLogin = flag == 2
    resetcontrol.DoReset(bIsQuickLogin, logout)
    LOG('========= restart %s===========' % flag)
    StartStep1(flag)
    import resloadasyncmgr
    resloadasyncmgr.OnRestart()
    import newcommandmgr
    newcommandmgr.UpdateLoop()
    import chatwnd
    chatwnd.g_MainPanel = chatpanel
    return


g_RestartSaveList = None
g_RestartSaveObjs = [
 (
  'netserver', ['g_Proxy', 'g_LoginServerIP', 'g_LoginServePort', 'g_LoginServer', 'g_KFServerID', 
   'g_LoginServerID']),
 (
  'dlgshutdown', ['g_DelayTime', 'g_Keyword', 'g_NoShutdown', 'g_SetTime']),
 (
  'warui', ['g_PrevBoutCmd', 'g_DefaultMagicID', 'g_PetID2DefaultMagicID', 'g_RecentMagic']),
 (
  'dlgautofight', ['g_Turn', 'g_StateObj', 'g_CanRecover', 'g_HaspetAction']),
 (
  'misc', ['g_InterNet']),
 (
  'chatoutput', ['g_Chats']),
 (
  'chatinput', ['HistoryString', 'CurrentString']),
 (
  'channel', ['g_Channel']),
 (
  'dlgnewbiequestion', ['g_QuestionText']),
 (
  'loginin', ['g_LoginEmail']),
 (
  'dlgmap', ['g_SceneID2NpcInfo']),
 (
  'netquicklogin', ['g_LoginKey']),
 (
  'audioroom', ['g_KuafuServer']),
 (
  'mgrscreenshot', ['g_ScreenShotPath']),
 (
  'hidecatcat', ['g_GameFlag']),
 (
  'wrapui', ['g_OrgWelcome'])]

def RestartSave():
    global g_RestartSaveList
    global g_RestartSaveObjs
    lst = []
    for (modeName, attrList) in g_RestartSaveObjs:
        mode = __import__(modeName)
        for attr in attrList:
            lst.append(getattr(mode, attr, None))

    g_RestartSaveList = lst
    return


def RestartRestore():
    global g_RestartSaveList
    if not g_RestartSaveList:
        return
    i = 0
    for (modeName, attrList) in g_RestartSaveObjs:
        mode = __import__(modeName)
        for attr in attrList:
            setattr(mode, attr, g_RestartSaveList[i])
            i += 1

    g_RestartSaveList = None
    return


def RestartQuickLogin(loginKey, heroID):
    import selectserver, netlogin, world, misc, chatoutput, netserver
    proxy = selectserver.g_Proxy
    ip = selectserver.g_LastVisit[2]
    port = selectserver.g_LastVisit[3]
    lastVisit = selectserver.g_LastVisit
    loginServer = selectserver.g_LoginServer
    ca = netlogin.g_CurrAccount
    if g_DelayF9:
        tickf9 = g_DelayF9.m_Tick
    else:
        tickf9 = 0
    if g_DelayF11:
        tickf11 = g_DelayF11.m_Tick
    else:
        tickf11 = 0
    hidebar = world.g_HideSaleBar
    RestartSave()
    Restart(2, False)
    import net, selectserver, netlogin, map, chatoutput, netquicklogin, netserver
    net.g_Net = net.CFakeNet()
    netlogin.g_CurrAccount = ca
    if tickf9 or tickf11 or hidebar:
        import common
        map.PushDelayCall(common.CCfgFunctor(tickf9, tickf11, hidebar))
    netquicklogin.g_LoginKey = loginKey
    selectserver.g_LastVisit = lastVisit
    selectserver.g_LoginServer = loginServer
    if g_IsDgwConnect:
        netquicklogin.DoDgwQuickLogin(loginKey, heroID, serverid)
        return
    else:
        netobj = selectserver.CMXNet(ip, port)
        netobj.m_Hello = False
        netobj.m_QuickLogin = True
        netobj.m_HeroID = heroID
        netobj.m_LoginKey = loginKey
        if proxy:
            print 'sNz!!!!!', proxy
            p = proxy.find(':')
            netobj.m_Proxy = proxy
            netobj.Connect(proxy[:p], int(proxy[p + 1:]))
            iplst = ip.replace('.', ' ').split()
            for i in xrange(4):
                netobj.NakedSend(chr(int(iplst[i])))

            netobj.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
        else:
            netobj.Connect()
    net.g_Net = netobj
    return


def RestarConfirm(ip, port, idx, pwd):
    import selectserver, netlogin, world, misc
    proxy = selectserver.g_Proxy
    ca = netlogin.g_CurrAccount
    if g_DelayF9:
        tickf9 = g_DelayF9.m_Tick
    else:
        tickf9 = 0
    if g_DelayF11:
        tickf11 = g_DelayF11.m_Tick
    else:
        tickf11 = 0
    hidebar = world.g_HideSaleBar
    import chatoutput
    chatoutput.ChatsRecordFilter()
    RestartSave()
    Restart(2)
    import net, selectserver, netlogin, map, netserver
    net.g_Net = net.CFakeNet()
    netlogin.g_CurrAccount = ca
    if tickf9 or tickf11 or hidebar:
        import common
        map.PushDelayCall(common.CCfgFunctor(tickf9, tickf11, hidebar))
    RestartRestore()
    netobj = selectserver.CMXNet(ip, port)
    netobj.m_Hello = False
    netobj.m_ReConnect = True
    netobj.m_Idx = idx
    netobj.m_Pwd = pwd
    if proxy:
        print 'sNz!!!!!', proxy
        p = proxy.find(':')
        netobj.m_Proxy = proxy
        netobj.Connect(proxy[:p], int(proxy[p + 1:]))
        iplst = ip.replace('.', ' ').split()
        for i in xrange(4):
            netobj.NakedSend(chr(int(iplst[i])))

        netobj.NakedSend(chr(port % 256) + chr(port / 256 % 256) + chr(port / 65536 % 256) + chr(port / 16777216 % 256))
    else:
        netobj.Connect()
    net.g_Net = netobj
    import netquicklogin
    netquicklogin.StartQuickTimer()
    return


def RestarConfirmEx(idx, pwd, proxy_port_ip_list):
    import netlogin, world, misc, selectserver, netserver
    ca = netlogin.g_CurrAccount
    if g_DelayF9:
        tickf9 = g_DelayF9.m_Tick
    else:
        tickf9 = 0
    if g_DelayF11:
        tickf11 = g_DelayF11.m_Tick
    else:
        tickf11 = 0
    hidebar = world.g_HideSaleBar
    RestartSave()
    Restart(2)
    import net, connect
    net.g_Net = net.CFakeNet()
    connect.KuaFuConnect(idx, pwd, proxy_port_ip_list)
    import netlogin
    netlogin.g_CurrAccount = ca
    if tickf9 or tickf11 or hidebar:
        import common, map
        map.PushDelayCall(common.CCfgFunctor(tickf9, tickf11, hidebar))
    import selectserver, netserver
    RestartRestore()
    import netquicklogin
    netquicklogin.StartQuickTimer()
    return


def GetCurFrame():
    global g_iCurFrame
    return g_iCurFrame


def MainLoop(mousex, mousey):
    global g_iCurFrame
    g_iCurFrame += 1
    if Quit:
        return 1
    import freetimetaskqueue
    freetimetaskqueue.UpdateStartTime()
    import cursor, interface, net
    cursor.Loop(mousex, mousey)
    if interface.Hold is not None:
        hold = interface.Hold.Get()
        if hold is None:
            interface.Hold = None
        elif not C_sys.IsActiveWindow():
            hold.LeftUp()
        else:
            try:
                p = hold.GetParent()
                while True:
                    if p == interface.MainPanel:
                        hold.Hold()
                        break
                    p = p.GetParent()

            except AttributeError:
                pass

    import addon
    addon.Hold()
    if net.g_Net:
        if IsTestMultiProcessServerCmd():
            NetMultiProcessServerCmd()
        else:
            net.g_Net.ProcessServerCmd()
    import netserver
    netserver.ProcessServerCmd()
    import connect
    connect.ProcessServerCmd()
    import netquicklogin
    netquicklogin.ProcessServerCmd()
    import pubhttp
    pubhttp.NetProcess()
    import pubhttps
    pubhttps.NetProcess()
    import imnet
    imnet.ProcessIMCmd()
    import ping
    ping.Loop()
    import dgw
    dgw.Loop()
    import cardgamecmdmgr
    cardgamecmdmgr.CGameActionMgr.PerForm()
    import pubmain
    pubmain.Loop()
    import timer
    timer.Loop(timer.TimeForTimer())
    CModuleLoop.Loop()
    import yibug
    yibug.YBLoop()
    import loginterface
    loginterface.Loop()
    if permission.IsOpenNewSoundBnk():
        import newsoundinterface
        newsoundinterface.Loop()
    log.Loop()
    return 0


class CModuleLoop(object):
    m_Loops = {}

    @classmethod
    def Loop(cls):
        for (modname, loopfunc) in cls.m_Loops.items():
            func = getattr(__import__(modname), loopfunc)
            func()

        return

    @classmethod
    def AddLoop(cls, modname, loopfunc):
        cls.m_Loops[modname] = loopfunc
        return

    @classmethod
    def DelLoop(cls, modname):
        try:
            del cls.m_Loops[modname]
        except KeyError:
            pass

        return


def IsTestMultiProcessServerCmd():
    return True


def NetMultiProcessServerCmd():
    import net, dragonlogmgr
    fTotalTime = 0
    iUnpackNum = 0
    net.g_UnpackNumThisFrame = 0
    for i in xrange(net.MAX_PROCESS_SERVER_CMD_TIMES):
        fTime = time.time()
        net.g_Net.ProcessServerCmd()
        if iUnpackNum == net.g_UnpackNumThisFrame:
            break
        fDeltaTime = time.time() - fTime
        fTotalTime += fDeltaTime
        iUnpackNum += net.UNPACK_PACKET_NUM_PER_PROCESS
        if iUnpackNum >= net.MIN_UNPACK_PACKET_NUM_PER_FRAME:
            if fDeltaTime >= net.MAX_PROCESS_SERVER_CMD_TIME_PER_TIME:
                break
            if fTotalTime >= net.MAX_PROCESS_SERVER_CMD_TIME_PER_FRAME:
                break

    if permission.IsOpenDragonpkNetLog():
        dragonlogmgr.CollectUnpackTime(fTotalTime)
    return


def WarLoop(mousex, mousey):
    import dlgwarrecord
    if not dlgwarrecord.IsWarRecPause():
        import war
        war.Process(True)
    r = MainLoop(mousex, mousey)
    return r


def AfterRestart(mousex, mousey):
    global RestartTimes
    RestartTimes -= 1
    if RestartTimes == 0:
        SetMainLoop()
        import blacklist
        if blacklist.NeedCheck():
            blacklist.StartCheck()
    return 0


def SetWarLoop():
    global Loop
    Loop = WarLoop
    return


def SetMainLoop():
    global Loop
    Loop = MainLoop
    return


Loop = MainLoop

def InWar():
    return Loop == WarLoop


g_HideWindowData = {}

def GetHideWindowData(aimString):
    global g_HideWindowData
    return g_HideWindowData.get(aimString)


def CalHideWindowData():
    ClearHideWindowData()
    import interface, dlgnpc
    npcDlgNum = 0
    for shadow in interface.g_DialogList:
        if shadow and isinstance(shadow.Get(), dlgnpc.CNpcDlgBase):
            npcDlgNum += 1

    g_HideWindowData['npcDlgNum'] = npcDlgNum
    return


def ClearHideWindowData():
    global g_HideWindowData
    g_HideWindowData = {}
    return


def HideWindow(exit=True):
    import interface, combdialog, world, dlgwarrecord, netgm, wrapinterface
    netgm.SynHotKeyEsc()
    import popupmgr
    oTempList = interface.g_DialogList
    num = len(oTempList)
    cnt = popupmgr.GetPopupMgr().EscFunc()
    CalHideWindowData()
    try:
        import handobj
        if handobj.IsHand():
            cnt += 1
        handobj.Clear()
        if world.g_RightClickCallback:
            world.g_RightClickCallback()
            cnt += 1
    except:
        pass

    dlg = None
    bSend = False
    for idx in xrange(num - 1, -1, -1):
        if num != len(oTempList) and not bSend:
            LOG('DialogList׳QܡAнT{D', dlg)
            bSend = True
        if idx >= len(oTempList):
            continue
        ds = oTempList[idx]
        if ds is None or not ds.Get() or getattr(ds.Get(), 'm_IsIgnoreEsc', False):
            continue
        if isinstance(ds.Get(), dlgwarrecord.CRecordCtrlDlg):
            cnt += 1
            continue
        dlg = ds.Get()
        if dlg and dlg.GetShow():
            cnt += 1
            if hasattr(dlg, 'CloseWindow'):
                dlg.CloseWindow()
            elif hasattr(dlg, 'm_CloseBtn') and isinstance(dlg.m_CloseBtn, interface.CButton):
                dlg.m_CloseBtn.LeftUp()
            elif isinstance(dlg, combdialog.CCombDialog) and dlg.GetObject('m_CloseBtn'):
                print 'combdialog.m_CloseBtn.LeftUp()'
                dlg.GetObject('m_CloseBtn').LeftUp()
            else:
                dlg.SetShow(False)

    for refobj in wrapinterface.g_TipsRefList:
        obj = refobj.Get()
        if obj and obj.GetShow():
            cnt += 1
            obj.SetShow(False)

    import mainmenu, dlgmap, dlgworldmap, zoomui
    try:
        mainmenu.g_MainMenu.ShowTarget(None)
    except:
        pass

    if dlgmap.IsMinimapShow():
        dlgmap.HideMinimap()
        cnt += 1
    if dlgworldmap.IsWorldMapShow():
        dlgworldmap.HideW9$ldMap()
        cnt += 1
    if zoomui.IsZoomShow():
        zoomui.HideZoom()
        cnt += 1
    if cnt == 0 and exit:
        import popmenu
        popmenu.CQuitItem.OnExit()
    ClearHideWindowData()
    return


def CancelWindow():
    import interface, commondialog
    for ds in interface.g_DialogList:
        dlg = ds.Get()
        if dlg and dlg.GetShow():
            try:
                if isinstance(dlg, commondialog.CMessageBox) and hasattr(dlg, 'm_bCloseFunc') and dlg.m_bCloseFunc:
                    dlg.DoCancel()
            except AttributeError:
                pass

    return


g_ExitDialog = None

def SaveClientData():
    import ratio, dlgmap, teamui
    mdtasktrace.GetModel().SaveLocal()
    dlgmap.SaveFindDialogInfo()
    import history_encryptnew
    history_encryptnew.save_last()
    import chatinput
    chatinput.SaveHistoryInput()
    import abtest
    abtest.SaveServerFlag()
    teamui.SendReturnLog()
    import dlgbaozi
    dlgbaozi.SaveEmoteText()
    import yardviewsignal
    yardviewsignal.Emit(yardviewsignal.SS_SAVEYARD_LOCAL_IFNEEDED)
    return


def ExitGame():
    global Quit
    if not gamectrl.IsShowMainPage():
        Quit = True
        return
    import hero, net
    if hasattr(hero, 'g_ID') and hero.g_ID and not C_sys.IsKeyDown(key.VK_CTRL) and net.g_Net:
        RealExit(True, ('bqAȾH...', 'bqAȾH...', 'bqAȾH...', 'bqAȾH...'))
    else:
        RealExit(True, None)
    if net.g_Net and hasattr(hero, 'g_ID') and hero.g_ID:
        import netsale
        netsale.C2SCheckOfflineSale()
    return


def doexit(dlg=None):
    import dlgexitinfo
    dlgexitinfo.C2IMScreenShotPath()
    CloseGame()
    return


def doreturn(dlg):
    global g_ExitDialog
    import net, log
    log.DelMgr()
    import statisticsignal
    statisticsignal.Emit(statisticsignal.SS_RETURNLOGIN)

    def _relogin(obj, t, dummy):
        if t < 30:
            return (
             t + 1, dummy)
        elif net.g_Net and not net.g_Net.IsSent() and t < 90:
            return (
             t + 1, dummy)
        import taiwanspecial
        taiwanspecial.Reset800x600WhenLogin()
        Restart()
        return

    dlg.CreatePyCommand(1, _relogin, 1, dlg)
    import netquicklogin
    netquicklogin.NormalLogout()
    if net.g_Net:
        net.g_Net.m_IsRelogin = True
    g_ExitDialog = None
    return


def docancel(dlg):
    global g_ExitDialog
    g_ExitDialog = None
    return


def RealExit(bPopupDialog, daymsg):
    global g_ExitDialog
    import commondialog, hero, cfg
    cfg.WriteMXIniBackUp()
    if bPopupDialog == True:
        if g_ExitDialog:
            doexit(None)
            return
        if hasattr(hero, 'g_Hero') and hero.g_Hero and hero.g_Hero.IsSale():
            import usermacro
            usermacro.PROMPT_MSG('hXCN۰ʶiJu\\uA')
        if daymsg:
            import dlgexitinfo
            dlgexitinfo.OpenExitInfoDlg()
        else:
            g_ExitDialog = commondialog.ShowNewMessageBox('ATw{bNnhXC?', ('sn', '}C',
                                                                          ''), (doreturn, doexit, docancel))
    elif g_ExitDialog:
        g_ExitDialog.UpdateDayMsg(daymsg)
    return


def ClearHotKey():
    _magickeys = (key.VK_F1, key.VK_F2, key.VK_F3, key.VK_F4, key.VK_F5, key.VK_F6, key.VK_F7, key.VK_F8)
    _chatkeys = (key.VK_PAGEUP, key.VK_PAGEDOWN, (key.VK_ALT, key.VK_1), (key.VK_ALT, key.VK_2), (key.VK_ALT, key.VK_3),
     (
      key.VK_ALT, key.VK_4), (key.VK_ALT, key.VK_5), (key.VK_ALT, key.VK_6), (key.VK_ALT, key.VK_7), (key.VK_ALT, key.VK_S),
     (
      key.VK_ALT, key.VK_COMMA), (key.VK_ALT, key.VK_PERIOD),
     key.VK_WAVE)
    _emotekeys = ((key.VK_CTRL, key.VK_1), (key.VK_CTRL, key.VK_2), (key.VK_CTRL, key.VK_3), (key.VK_CTRL, key.VK_4),
     (
      key.VK_CTRL, key.VK_5), (key.VK_CTRL, key.VK_6), (key.VK_CTRL, key.VK_7), (key.VK_CTRL, key.VK_8),
     (
      key.VK_CTRL, key.VK_9), (key.VK_CTRL, key.VK_0), (key.VK_CTRL, key.VK_DEC), (key.VK_CTRL, key.VK_EQUAL),
     (
      key.VK_CTRL, key.VK_WAVE))
    _default = (key.VK_ESCAPE, key.VK_ENTER, key.VK_TAB, key.VK_F9)
    for k in _magickeys:
        key.RegisterHotKey(k)

    for k in _chatkeys:
        key.RegisterHotKey(k)

    for k in _emotekeys:
        key.RegisterHotKey(k)

    for k in _default:
        key.RegisterHotKey(k)

    key.RegisterHotKeyEx(key.VK_CTRL)
    key.RegisterHotKeyEx(key.VK_SHIFT)
    key.RegisterHotKeyEx(-key.VK_CTRL)
    key.RegisterHotKeyEx(-key.VK_SHIFT)
    import dlgsysopt
    for hk in dlgsysopt.g_HotKeys.values():
        key.RegisterHotKey(hk)

    return


g_DelayF9 = None
g_TickF9 = False

def IsHidePlayer():
    return True if g_DelayF9 else False


def ReleaseF9():
    global g_DelayF9
    if g_DelayF9:
        g_DelayF9.Release()
        g_DelayF9 = None
    return


def switchplayer(tick=-1):
    global g_DelayF9
    global g_TickF9
    import world, acteyectrl, usermacro, walkerhidecheck
    if acteyectrl.GetActEyeCtrl().IsBegin():
        usermacro.PROMPT_MSG('ʵLkϥΦ\\')
        return
    walkerhidecheck.GetChecker().OnSwitchPlayerShow(not world.g_HidePlayer & 1)
    world.HideCourty(10, not world.g_HidePlayer & 1)
    world.HidePlayer(1, not world.g_HidePlayer & 1)
    if g_DelayF9:
        ReleaseF9()
    else:

        def CancelF9(obj, tick):
            obj.m_Tick = tick
            if tick > 0:
                import world
                world.ShowHotKeyTips()
                return (tick - 1,)
            switchplayer()
            return

        if tick < 0:
            tick = 1800
        import interface, misc
        g_DelayF9 = interface.CBaseObject(None)
        if not misc.IsTWServer():
            g_DelayF9.CreatePyCommand(30, CancelF9, tick)
        g_DelayF9.m_Tick = tick
        import clickcounter
        clickcounter.Log('F9')
    g_TickF9 = True
    return


g_TickF10 = False

def switchsalebar(hidebar=-1):
    global g_TickF10
    import world
    if hidebar < 0:
        hidebar = not world.g_HideSaleBar
    world.HideCourty(11, hidebar)
    world.HideSaleBar(hidebar)
    if hidebar:
        import clickcounter
        clickcounter.Log('F10')
    g_TickF10 = True
    return


g_DelayF11 = None
g_TickF11 = False

def ReleaseF11():
    global g_DelayF11
    if g_DelayF11:
        g_DelayF11.Release()
        g_DelayF11 = None
    return


def switchteamleader(tick=-1):
    global g_DelayF11
    global g_TickF11
    import world, acteyectrl, usermacro
    if acteyectrl.GetActEyeCtrl().IsBegin():
        usermacro.PROMPT_MSG('ʵLkϥΦ\\')
        return
    v = not world.g_HidePlayer & 32
    world.HideCourty(10, v)
    world.HidePlayer(32, v)
    if v:
        import clickcounter
        clickcounter.Log('F11')
    if g_DelayF11:
        ReleaseF11()
    else:

        def CancelF11(obj, tick):
            obj.m_Tick = tick
            if tick > 0:
                import world
                world.ShowHotKeyTips()
                return (tick - 1,)
            switchteamleader()
            return

        if tick < 0:
            tick = 3600
        import interface
        g_DelayF11 = interface.CBaseObject(None)
        g_DelayF11.CreatePyCommand(30, CancelF11, tick)
        g_DelayF11.m_Tick = tick
    g_TickF11 = True
    return


def switchdialog():
    import world
    world.HideDialog(not world.g_HideDialog)
    import clickcounter
    clickcounter.Log('F12')
    return


g_SnapshotBG = None
Snapshotback = None

def selecthotmagic(idx):
    import dlgsysopt
    if dlgsysopt.DoFKeyCallback(idx + 1):
        return
    if C_sys.IsKeyDown(key.VK_ALT):
        return
    import warui
    oShortcut = warui.GetMagicShortKeyDlg()
    if not oShortcut:
        return
    import shortcut, statisticsignal
    shortcut.CShortcut.DoWithPos(oShortcut.GetShortcutType(), idx)
    statisticsignal.Emit(statisticsignal.SS_WAR_MAGIC_WAY, 'ֱ')
    return


def RegisterDefaultHotKey():
    import interface
    key.RegisterHotKey(key.VK_CLOSE, ExitGame)
    key.RegisterHotKey(key.VK_ESCAPE, HideWindow)
    key.RegisterHotKey(key.VK_ENTER, interface.DefaultButtonClick)
    import reimport
    if permission.GetSpecialVersion():
        reimport.RegisterReloadHotKey()

    def Snapshot():
        global Snapshotback
        global g_SnapshotBG
        global g_SnapshotID
        try:
            import os
            os.mkdir('screen')
        except:
            pass

        try:
            g_SnapshotID += 1
        except:
            g_SnapshotID = 0

        import interface, time
        timetxt = '%d%02d%02d-%02d%02d%02d' % time.localtime()[:6]
        if g_SnapshotBG:
            pass
        else:
            path = 'screen/%s-%04d.bmp' % (timetxt, g_SnapshotID)
            g_SnapshotBG = interface.CSnapshotBitmapObject(None, path)
            g_SnapshotBG.SetZ(999)

            def _refrashback(obj):
                global g_SnapshotBG
                import usermacro, mgrscreenshot
                mgrscreenshot.AddScreenShotPath(path)
                usermacro.NORMAL_MSG('IϦ\\AwOsܹCؿU#s(55,screen)#Y\U000e7a21C')
                g_SnapshotBG = None
                return

            Snapshotback = interface.CBaseObject(None)
            Snapshotback.CreatePyCommand(5, _refrashback)
        return

    key.RegisterHotKey(-key.VK_SNAPSHOT, Snapshot)
    return


def RegisterChatHotKey():
    import chatoutput
    key.RegisterHotKey(key.VK_PAGEUP, chatoutput.PageUp)
    key.RegisterHotKey(key.VK_PAGEDOWN, chatoutput.PageDown)
    import chatinput
    key.RegisterAltHotKey(key.VK_1, chatinput.SpeedChat, 0)
    key.RegisterAltHotKey(key.VK_2, chatinput.SpeedChat, 1)
    key.RegisterAltHotKey(key.VK_3, chatinput.SpeedChat, 3)
    key.RegisterAltHotKey(key.VK_4, chatinput.SpeedChat, 11)
    key.RegisterAltHotKey(key.VK_5, chatinput.SpeedChat, 26)
    key.RegisterAltHotKey(key.VK_6, chatinput.SpeedChat, 5)
    key.RegisterAltHotKey(key.VK_7, chatinput.SpeedChat, 6)
    RegisterChannelHotKey()
    _magickeys = (
     key.VK_F1, key.VK_F2, key.VK_F3, key.VK_F4, key.VK_F5, key.VK_F6, key.VK_F7, key.VK_F8)
    for (idx, k) in enumerate(_magickeys):
        key.RegisterHotKey(k, selecthotmagic, idx)

    key.RegisterHotKey(key.VK_F9, switchplayer)
    key.RegisterHotKey(key.VK_F10, switchsalebar)
    key.RegisterHotKey(key.VK_F11, switchteamleader)
    key.RegisterHotKey(key.VK_F12, switchdialog)

    def OnHotEnter():
        import interface
        edit = interface.GetActiveEdit()
        if edit and hasattr(edit, 'OnHotEnter'):
            edit.OnHotEnter()
        return

    key.RegisterAltHotKey(key.VK_S, OnHotEnter)
    return


def RegisterChannelHotKey():
    import audiomgr
    for k in (key.VK_COMMA, key.VK_PERIOD, key.VK_WAVE):
        key.RegisterHotKey(k)

    key.RegisterAltHotKey(key.VK_WAVE, audiomgr.OnStartWithHotkey)

    def switchchannel(inc):
        import hero, chatinput, channel
        if C_sys.IsKeyDown(key.VK_SHIFT) or C_sys.IsKeyDown(key.VK_CTRL):
            return
        preIdx = chatinput.ChannelID2Index(channel.g_Channel)
        showLst = chatinput.ComputeShowList()
        try:
            idx = showLst.index(preIdx)
            iLen = len(showLst)
            idx = (idx + inc + iLen) % iLen
        except ValueError:
            idx = 0

        channelID = chatinput.Index2ChannelID(showLst[idx])
        channel.SetChannel(channelID)
        return

    def PressChenelKey():
        import interface, mainmenu
        edit = interface.GetActiveEdit()
        oChatInput = mainmenu.GetChatInputObj()
        if oChatInput is not None:
            chat_input = oChatInput
        else:
            return
        if edit == chat_input:
            switchchannel(1)
        return

    key.RegisterAltHotKey(key.VK_COMMA, switchchannel, -1)
    key.RegisterAltHotKey(key.VK_PERIOD, switchchannel, 1)
    key.RegisterAltHotKey(key.VK_0, PressChenelKey)
    return


def OnSwitchSkillDlg():
    import skillmagicdefines, skillmagicsignal
    skillmagicsignal.Emit(skillmagicsignal.SS_SKILLMAGIC_SWITCHOPEN, skillmagicdefines.S_PAGE_SKILL)
    return


def OnSwitchMagicDlg():
    import skillmagicdefines, skillmagicsignal
    skillmagicsignal.Emit(skillmagicsignal.SS_SKILLMAGIC_SWITCHOPEN, skillmagicdefines.S_PAGE_MAGIC)
    return


def SwitchHotKey(IsWar, bOldWar=None):
    global g_DisableHotKey
    import dlgsysopt
    if g_DisableHotKey:
        return
    hotkeys = dlgsysopt.g_HotKeys
    for hk in hotkeys.values():
        key.RegisterHotKey(hk)

    key.RegisterHotKey(key.VK_TAB)

    def mainmenumsg(msgid):
        import mainmenu
        mainmenu.g_MainMenu.OnHotKeyMsg(msgid)
        return

    def openstate():
        import mainmenu
        mainmenu.g_MainMenu.m_HeroFrame.ssEmit(mainmenu.g_MainMenu.m_HeroFrame.SS_ClickIcon)
        return

    def opensummon():
        import mainmenu
        mainmenu.g_MainMenu.m_SummonFrame.ssEmit(mainmenu.g_MainMenu.m_SummonFrame.SS_ClickIcon)
        return

    def teamop():
        import mainmenu, teamui
        mainmenu.SetTeamBtnAniShow(False)
        teamui.MakeTeam()
        return

    def dobbmake():
        import popmenu, nethero, misc
        if misc.IsNationFightServer():
            return
        import dlgbbcardmake
        if not popmenu.CBBCardItem.BBMakeValid():
            return
        if dlgbbcardmake.IsOpen():
            dlgbbcardmake.Show(False)
        else:
            nethero.C2SBBCardMakeOpen()
        return

    def doachieve():
        import misc, netachieve, dlgachieve, hero
        if misc.IsNationFightServer():
            return
        if dlgachieve.GetAchieveDlg() is None:
            netachieve.CAchieve.C2SGetRecentAchieve(hero.g_ID)
        else:
            dlgachieve.Show(False)
        return

    def openLycos():
        import nethero
        nethero.C2SOpenLycos()
        return

    def openSysopt():
        import dlgsysopt
        dlgsysopt.ShowSwitch()
        return

    def switchHideAround():
        import dlgsysopt
        dlgsysopt.SwitchNpcAround()
        return

    def gamescreenshot():
        import mgrscreenshot
        mgr = mgrscreenshot.CShotManage()
        mgr.Show(mgr.TYPE_SAVEGAMESHOT)
        return

    def openCalender():
        import dlgschedule, dlgnewschedule
        if permission.IsNewSchedule():
            dlgnewschedule.ShowSwitch()
        else:
            dlgschedule.SwitchSchedule()
        return

    def openZhidao():
        import netzhidao
        netzhidao.C2SOpen(1)
        return

    import world, dlgmap, dlgride, dlgworldmap
    if not IsWar:
        key.RegisterCtrlHotKey(key.VK_1, globalhotkeyfunc.DoEmote, key.VK_1, 1)
        key.RegisterCtrlHotKey(key.VK_2, globalhotkeyfunc.DoEmote, key.VK_2, 2)
        key.RegisterCtrlHotKey(key.VK_3, globalhotkeyfunc.DoEmote, key.VK_3, 12)
        key.RegisterCtrlHotKey(key.VK_4, globalhotkeyfunc.DoEmote, key.VK_4, 3)
        key.RegisterCtrlHotKey(key.VK_5, globalhotkeyfunc.DoEmote, key.VK_5, 13)
        key.RegisterCtrlHotKey(key.VK_6, globalhotkeyfunc.DoEmote, key.VK_6, 4)
        key.RegisterCtrlHotKey(key.VK_7, globalhotkeyfunc.DoEmote, key.VK_7, 9)
        key.RegisterCtrlHotKey(key.VK_8, globalhotkeyfunc.DoEmote, key.VK_8, 8)
        key.RegisterCtrlHotKey(key.VK_9, globalhotkeyfunc.DoEmote, key.VK_9, 10)
        key.RegisterCtrlHotKey(key.VK_0, globalhotkeyfunc.DoEmote, key.VK_0, 11)
        key.RegisterCtrlHotKey(key.VK_DEC, globalhotkeyfunc.DoEmote, key.VK_DEC, 7)
        key.RegisterCtrlHotKey(key.VK_EQUAL, globalhotkeyfunc.DoEmote, key.VK_EQUAL, 6)
        key.RegisterCtrlHotKey(key.VK_WAVE, globalhotkeyfunc.DoEmote, key.VK_WAVE, 5)
    key.RegisterHotKey(hotkeys['Hɭ'], openstate)
    key.RegisterHotKey(hotkeys['l~ɭ'], opensummon)
    key.RegisterHotKey(hotkeys['ޯɭ'], OnSwitchSkillDlg)
    key.RegisterHotKey(hotkeys['ۦɭ'], OnSwitchMagicDlg)
    key.RegisterHotKey(hotkeys['nͬɭ'], mainmenumsg, 9)
    key.RegisterHotKey(hotkeys['~ɭ'], mainmenumsg, 2)
    key.RegisterHotKey(hotkeys['yɭ'], mainmenumsg, 4)
    key.RegisterHotKey(hotkeys['Ȭɭ'], mainmenumsg, 6)
    key.RegisterHotKey(hotkeys['ɭ'], teamop)
    key.RegisterHotKey(hotkeys['ɭ'], mainmenumsg, 7)
    key.RegisterHotKey(hotkeys[''], mainmenumsg, 20)
    key.RegisterHotKey(hotkeys['ʧ@'], mainmenumsg, 21)
    key.RegisterHotKey(hotkeys['ۤ'], dobbmake)
    key.RegisterHotKey(hotkeys['N'], doachieve)
    key.RegisterHotKey(hotkeys['tγ]m'], openSysopt)
    key.RegisterHotKey(hotkeys['NPCP\U000aac6ea'], switchHideAround)
    key.RegisterHotKey(hotkeys['CI'], gamescreenshot)
    key.RegisterHotKey(key.VK_TAB, dlgmap.SwitchMinimap)
    key.RegisterHotKey(hotkeys['@ɦa'], dlgworldmap.ShowSwitchWorldMap)
    key.RegisterHotKey(hotkeys['Mɭ'], dlgride.ShowSwitch)
    import warui
    key.RegisterHotKey(hotkeys['۰ʾ\u0530'], warui.AutoFight)
    key.RegisterHotKey(hotkeys['ڷQF'], openLycos)
    key.RegisterHotKey(hotkeys['ɭ'], openCalender)
    key.RegisterHotKey(hotkeys['ڷQD'], openZhidao)
    key.RegisterHotKey(hotkeys['H⤤߬ɭ'], globalhotkeyfunc.OpenConsignmall)
    key.RegisterHotKey(hotkeys['~'], globalhotkeyfunc.OpenTjTradeCenter)
    if IsWar:
        import mxv, warui

        def defaultattack():
            if mxv.g_Panel:
                return
            import misc, war, bgdata
            if war.g_HeroID is None:
                return
            if war.g_WarType >= bgdata.WARTYPE_PK:
                if war.g_TurnCount <= 1 and misc.Time() - war.g_WarStartTime < 3:
                    return
            if warui.IsCanQuickAct():
                t = warui.GetTurn()
                if t == 1:
                    ob = warui.GetPrevBoutTarget(1)
                    if ob:
                        warui.PhyAttack(ob)
                elif t == 2:
                    ob = warui.GetPrevBoutTarget(2)
                    if ob:
                        warui.SummonAttack(ob)
                elif t == 3:
                    ob = warui.GetPrevBoutTarget(1)
                    if ob:
                        warui.HerdboyAttack(ob)
            return

        def doact(act):
            if mxv.g_Panel:
                return
            if warui.IsCanQuickAct(act):
                warui.g_HeroMenu.OnMessage(act)
            return

        def openwardlg(act):
            if mxv.g_Panel:
                return
            oWarDlg = getattr(warui, 'g_MagicDialog', None)
            if oWarDlg and oWarDlg.GetShow():
                oWarDlg.CloseWindow()
            else:
                doact(act)
            return

        def usedefaultmagic():
            if mxv.g_Panel:
                return
            import war, usermacro, pet
            if war.g_HeroID and warui.IsCanQuickAct():
                ob = warui.GetPrevBoutTarget()
                flag = False
                if isinstance(warui.g_HeroMenu, warui.CSummonMenu):
                    petobj = pet.GetActivatePet()
                    if len(pet.GetInitActiveSkills(petobj, True)) == 0:
                        flag = True
                if ob and warui.UseDefaultMagic(ob, flag) == False and flag == False and hasattr(ob, 'GetDefaultMagicID') and ob.GetDefaultMagicID() is None:
                    usermacro.PROMPT_MSG('٨S]mq{kN')
            return

        def selectdefaultmagic():
            if mxv.g_Panel:
                return
            import war
            if war.g_HeroID and warui.IsCanQuickAct():
                warui.SelectDefaultMagic()
            return

        key.RegisterHotKey(hotkeys['m'], doact, 4)
        key.RegisterHotKey(hotkeys['O@'], doact, 5)
        key.RegisterHotKey(hotkeys['A'], doact, 7)
        key.RegisterHotKey(hotkeys['q{'], defaultattack)
        key.RegisterHotKey(hotkeys['q{kN'], usedefaultmagic)
        key.RegisterHotKey(hotkeys['q{kN'], selectdefaultmagic)
        key.RegisterHotKey(hotkeys['\u0530D'], doact, 3)
        key.RegisterHotKey(hotkeys['kNC'], openwardlg, 1)
        key.RegisterHotKey(hotkeys['Ԫpɭ'], warui.DoCommandOpt, 1)
        key.RegisterHotKey(hotkeys['SަC'], openwardlg, 2)
        if warui.IsShowWarriorSelect():
            key.RegisterHotKeyEx(key.VK_CTRL, world.WarCtrlDownCondition)
            key.RegisterHotKeyEx(key.VK_SHIFT, world.WarCtrlDownCondition)
            key.RegisterHotKeyEx(-key.VK_CTRL, world.WarCtrlUpCondition)
            key.RegisterHotKeyEx(-key.VK_SHIFT, world.WarCtrlUpCondition)
    else:
        key.RegisterHotKey(hotkeys[''], mainmenumsg, 1)
        key.RegisterHotKey(hotkeys[''], world.SwapSelect)
        key.RegisterHotKey(hotkeys[''], world.GiveSelect)
        key.RegisterHotKeyEx(key.VK_CTRL)
        key.RegisterHotKeyEx(key.VK_SHIFT)
        key.RegisterHotKeyEx(-key.VK_CTRL)
        key.RegisterHotKeyEx(-key.VK_SHIFT)
    import modelbaseopt
    modelbaseopt.GetCBaseOptionModel().RegisterBossHotKey()
    return


def RegisterSelectMagicHotKey(bIsRegister):
    _magickeys = (key.VK_F1, key.VK_F2, key.VK_F3, key.VK_F4, key.VK_F5, key.VK_F6, key.VK_F7, key.VK_F8)
    for (idx, k) in enumerate(_magickeys):
        if bIsRegister:
            key.RegisterHotKey(k, selecthotmagic, idx)
        else:
            key.RegisterHotKey(k, None)

    return


def OnSysHotkey(key):
    return
    import commondialog

    def doexit(dlg):
        CloseGame()
        return

    def doconntinue(dlg):
        return

    commondialog.ShowMessageBox('z(%s)QU, oivTzbw, ĳzˬdt, d차, T{tΦwAiC?' % key, ('~C', '}C'), (doconntinue, doexit))


def SysUpdate(p, s):
    C_sys.Update(p, s)
    return


g_Adsid = ''

def CmdParam(p):
    global g_Adsid
    if p:
        if type(p) == str:
            if p.find('loadres:') != -1:
                SetIgnoreResLoaderCheck(True)
                import resloadasyncmgr
                resloadasyncmgr.Instance().SetIsResLoadAsyncServer()
    import log
    log.StartLog()
    print 'ǤJѼƬ', p
    if type(p) != str:
        return
    import re
    patt1 = re.compile('^adsid=(?P<adsid>[0-9]+).*')
    mobj1 = patt1.match(p)
    if mobj1:
        adsid = mobj1.group('adsid')
        if adsid:
            g_Adsid = adsid
        print 'ѪRadsidG', g_Adsid
    if p.startswith('@'):
        import pubdylogin
        pubdylogin.CmdParam(p)
        return
    if mobj1:
        return
    import param
    param.RunAferStartParam(p)
    return


def ClearCmdParam():
    import pubdylogin
    pubdylogin.CYWLoginInfoMgr.ClearCmdParam()
    return


def OnCrash():
    import crashrpt
    crashrpt.OnCrash()
    return 'Ȥݲ`AШϥθ귽״_״_᭫}Ȥ'


def OnError(errContent):
    print errContent
    return


def OnWalkerError(WalkerObjList):
    print 'VL{o{pUCWalkerObjectﹳSJ귽G'
    for WalkerObj in WalkerObjList:
        LOG('WalkerError', getattr(WalkerObj, 'm_SprPath', ''))

    return


def OnSpriteError(lst):
    print 'q}hspr~AJsprɵo{ʤְ\U000a5eeaframerq'
    for (filename, package) in lst:
        LOG('Error Spr', filename, package)

    return


def GetOneoff():
    import pubdylogin
    return pubdylogin.CYWLoginInfoMgr.GetOneoff()


def IsOneoff():
    import pubdylogin
    return pubdylogin.CYWLoginInfoMgr.IsOneoff()


def IsOneoff2():
    import pubdylogin
    if not pubdylogin.CanUseNewVersion():
        return False
    import pubdylogin
    return pubdylogin.CYWLoginInfoMgr.GetDYLoginKey()


def OnSizeRestored():
    gamectrl.OnSizeRestored()
    return


def SetRate(FullScreen=False):
    import ratio, cfg
    sRate = ratio.GetRatio() if FullScreen else cfg.GetData('mx.ini', 'Game', 'ratio')
    try:
        iRate = int(sRate)
    except:
        iRate = 2

    (workAreaW, workAreaH) = C_sys.GetWorkArea()
    if iRate > 1 and (workAreaH < 768 or workAreaW < 1024):
        iRate = 1
    if iRate == ratio.RATIO_800X600:
        ratio.Set800x600()
    elif iRate == ratio.RATIO_1366X768:
        ratio.Set1366X768()
    elif iRate == ratio.RATIO_1024X768:
        ratio.Set1024x768()
    elif iRate == ratio.RATIO_1366X708:
        ratio.Set1366X708()
    return


def SetRateTryTime():
    import cfg
    try:
        settry = cfg.GetData('mx.ini', 'Game', 'SetTryTime')
    except:
        settry = 'False'

    if settry == 'True':
        SetTryTime(180)
    cfg.SaveData('mx.ini', 'Game', 'SetTryTime', 'False')
    cfg.SaveData('mx.ini', 'Game', 'answer', '0')
    return


g_TryTimeObject = None

def SetTryTime(time):
    global g_TryTimeObject

    def ChangeTime(obj, second, dlg):
        import commondialog, cfg, netquicklogin
        second -= 1
        if second:

            def DoExit(obj):
                cfg.SaveData('mx.ini', 'Game', 'answer', '1')
                commondialog.HideMessageBox()
                return

            def DoSave(obj):
                cfg.SaveData('mx.ini', 'Game', 'answer', '1')
                import usermacro
                usermacro.PROMPT_MSG('zfҦ]mwOdAz]iHqL#Yt-tγ]m#n#Ynͬɭ]ms#nA#Ytγ]m#nӽո`fҦjpC')
                commondialog.HideMessageBox()
                return

            def DoReturn(obj):
                cfg.SaveData('mx.ini', 'Game', 'answer', '1')
                try:
                    oldrate = int(cfg.GetData('mx.ini', 'Game', 'oldratio'))
                except:
                    oldrate = 1

                cfg.SaveData('mx.ini', 'Game', 'ratio', str(oldrate))
                netquicklogin.Connect(False, 'fjp')
                return

            try:
                answer = int(cfg.GetData('mx.ini', 'Game', 'answer'))
            except:
                answer = 0
            else:
                if answer:
                    return
                if dlg:
                    dlg.m_Text = dlg.SetMessage('O_Ode]mfjpҦH#r#Y%d#n٭^e]m' % second)
                else:
                    dlg = commondialog.ShowMessageBox('O_Ode]mfjpҦH#r#Y%d#n٭^e]m' % second, ('Od]m',
                                                                                             '٭'), (DoSave, DoReturn))
                    dlg.m_ExitFunc = DoExit
                    dlg.m_AutoCancel = False
                    dlg.Capture(0)
                return (second, dlg)
        else:
            try:
                oldrate = int(cfg.GetData('mx.ini', 'Game', 'oldratio'))
            except:
                oldrate = 1

            cfg.SaveData('mx.ini', 'Game', 'ratio', str(oldrate))
            netquicklogin.Connect(False, 'fjp-2')
            return
        return

    if g_TryTimeObject:
        g_TryTimeObject.Release()
        g_TryTimeObject = None
    import interface
    g_TryTimeObject = interface.CBaseObject(None)
    g_TryTimeObject.CreatePyCommand(30, ChangeTime, time, None)
    return


def OnError(ErrorContent):
    import errorchk
    if ErrorContent:
        ErrorContent = ErrorContent.replace('\n', '\r\n')
        errorchk.CChecker.ParseLogTxt(ErrorContent)
        errorchk.CChecker.SendErrLog()
    return


return
