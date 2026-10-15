# pycdc 交叉复核产物 · script.fls entry 1406
# co_filename(原始)='script/netwar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1406.pyc (Python 2.5)

import mdlcommandskilltips
import mdlwardecidetime
import misc
import net
import permission
import towerdefence
import war
import prop
import recordvideo
import oldwalkerprocess
import limitserver
import mdwatchwar
import permission
g_WarTimes = 0
g_WarVersion = 0
g_WarLocation = [
    0,
    0]

def ModuleReset():
    global g_WarTimes, g_WarVersion, g_WarLocation
    g_WarTimes = 0
    g_WarVersion = 0
    g_WarLocation = [
        0,
        0]


def C2SWarPerform(id, perform):
    net.g_Net.PacketPrepare(net.C2GS_WAR_PERFORM)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketAddI(perform, 2)
    net.g_Net.PacketSend()


def C2SWarLook(id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_LOOK)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketSend()


def C2SWarAttack(id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_ATTACK)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketSend()


def C2SWarDefend():
    net.g_Net.PacketPrepare(net.C2GS_WAR_DEFEND)
    net.g_Net.PacketSend()


def C2SWarEscape():
    net.g_Net.PacketPrepare(net.C2GS_WAR_ESCAPE)
    net.g_Net.PacketSend()


def C2SWarItem(id, item):
    net.g_Net.PacketPrepare(net.C2GS_WAR_USE)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketAddI(item, 4)
    net.g_Net.PacketSend()


def C2SWarSummon(op, id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON)
    net.g_Net.PacketAddI(op, 1)
    if op == 0:
        net.g_Net.PacketAddI(id, 4)
    
    net.g_Net.PacketSend()


def C2SWarProtect(id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_PROTECT)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketSend()


def C2SWarCatch(id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_CAPTURE)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketSend()


def C2SChild(iChildID):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMONCHILD)
    net.g_Net.PacketAddI(iChildID, 4)
    net.g_Net.PacketSend()


def C2STurnEnd(turnNum):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_WAR_DRAWEND)
    netobj.PacketAddI(turnNum, 1)
    netobj.PacketSend()


def C2SWarSummAttack(id, target):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON_ATTACK)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketAddI(target, 1)
    net.g_Net.PacketSend()


def C2SWarSummPerform(id, target, perform):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON_PERFORM)
    net.g_Net.PacketAddI(target, 1)
    net.g_Net.PacketAddI(perform, 2)
    net.g_Net.PacketSend()


def C2SWarSummGuard(id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON_DEFEND)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketSend()


def C2SWarSummEscape(id):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON_ESCAPE)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketSend()


def C2SWarSummItem(id, target, item):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON_USE)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketAddI(target, 1)
    net.g_Net.PacketAddI(item, 4)
    net.g_Net.PacketSend()


def C2SWarSummProtect(id, target):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SUMMON_PROTECT)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketAddI(target, 1)
    net.g_Net.PacketSend()


def C2SWarExitWatch():
    net.g_Net.PacketPrepare(net.C2GS_WAR_LEAVEWATCH)
    net.g_Net.PacketSend()


def C2SWarBackCommand():
    net.g_Net.PacketPrepare(net.C2GS_WAR_BACKCOMMAND)
    net.g_Net.PacketSend()


def ReduceWarTime():
    global g_WarTimes
    g_WarTimes -= 1


def ReleaseVersion():
    global g_WarVersion
    g_WarVersion = 0


def GetWarVersion():
    return g_WarVersion


def SetWarLocation(warLocation):
    global g_WarLocation, g_WarLocation
    import dlgwarlocationeditor
    testLocation = dlgwarlocationeditor.GetTestWarLocation()
    if testLocation:
        g_WarLocation = [
            testLocation,
            0]
    else:
        g_WarLocation = warLocation


def ReleaseWarLocation():
    global g_WarLocation
    g_WarLocation = [
        0,
        0]


def GetWarLocation():
    return g_WarLocation


def S2CWarStart(netobj):
    global g_WarTimes, g_WarVersion
    import warrecord
    import warriorskillicon
    import warenteranimation
    import dlgwarrecord
    ReleaseVersion()
    ReleaseWarLocation()
    warrecord.StartRecord(netobj)
    g_WarTimes += 1
    cmd = war.CCmd(war.Start)
    cmd.scene = netobj.UnpackInt(2) + 1001
    cmd.alineup = netobj.UnpackInt(1)
    cmd.elineup = netobj.UnpackInt(1)
    cmd.type = netobj.UnpackInt(1)
    cmd.x = netobj.UnpackInt(2)
    cmd.y = netobj.UnpackInt(2)
    cmd.background = netobj.UnpackInt(2)
    g_WarVersion = netobj.UnpackInt(1)
    cmd.startTurn = netobj.UnpackInt(1)
    iAWarLocation = netobj.UnpackInt(1)
    iEWarLocation = netobj.UnpackInt(1)
    SetWarLocation([
        iAWarLocation,
        iEWarLocation])
    cmd.switchtype = 0
    oNetObj = net.GetNet()
    if oNetObj:
        oNetObj.SetServerCmdAbleCache(True)
    
    if warenteranimation.GetWarEnterAniMgr().GetIsShowingAni():
        return None
    
    bIsServerRecord = dlgwarrecord.IsWarRec()
    bIsClientRecord = war.GetReplayWar()
    bIsSureWarType = cmd.type in warenteranimation.SHOW_ANI_WAR_TYPE
    if bIsSureWarType and not bIsServerRecord and not bIsClientRecord:
        pass
    warenteranimation.GetWarEnterAniMgr().SetEnterAniShow(not (cmd.startTurn))
    print '! S2CWarStart scene=%d alineup=%d elineup=%d type=%d x=%d y=%d' % (cmd.scene, cmd.alineup, cmd.elineup, cmd.type, cmd.x, cmd.y)
    war.g_TurnMax = 0
    import main
    import mainmenu
    import warui
    import juben
    import dlgnpc
    import stackcheck
    if juben.IsPlayJuben():
        juben.StopJuBen()
    
    stackcheck.SetBeforeCall(stackcheck.warenteranimation)
    dlgnpc.CloseJuQing()
    dlgnpc.CloseNpcDlg()
    warui.LoadWarriorSelect()
    warui.ReadDefaultMagicID()
    
    try:
        mainmenu.SwitchEnv(True)
    except AttributeError:
        pass

    import warturn
    warturn.MkStartCmd(cmd)
    main.SetWarLoop()
    war.SetProcess(war.NextCmd)
    import nettask
    import timecontrol
    if nettask.GetTaskInfo(3501):
        timecontrol.CTimeControl.SetWarShield(2)
    
    import shortcut
    shortcut.CShortcutMgr.SetWarScheme()
    import warobserver
    warobserver.ClearOldData()
    WarStartCloseDlg()
    warriorskillicon.UpdateLocalDefaultShow()


def WarStartCloseDlg():
    LOG('\xbe\xd4\xb0\xab\xb6}\xa9l\xa1A\xc3\xf6\xb3\xac\xac\xc9\xad\xb1')
    import dlgnewguide
    dlgnewguide.CloseWindow()
    import dlgqunxiong
    dlgqunxiong.SwitchMiniDlg()
    import dlgartifact
    dlgartifact.CloseWindow()
    import mazemap
    mazemap.SwitchGameView(False)
    import dlgjianghu
    dlgjianghu.CloseWindow()


def S2CWarMask(netobj):
    import warmask
    warmask.S2CWarInfo(netobj)


def S2CWarOPCmd(netobj):
    import permission
    iSub = netobj.UnpackInt(1)
    if iSub == 1:
        if permission.IsTestLastWarCmd():
            LOG('\xb6}\xa9l\xb5o\xb0e\xbe\xd4\xb0\xab\xb5\xb2\xba\xe2\xbc\xc6\xbe\xda----------------------')
            netobj.SetServerCmdAbleCache(True)
        
    


def IsWarEnd():
    return g_WarTimes == 0


def S2CWarEnd(netobj):
    LOG('! S2CWarEnd\n')
    import warrecord
    import hero
    if recordvideo.GetVideoMgr().CheckNxtVideo():
        return None
    
    if IsWarEnd():
        return None
    
    ReduceWarTime()
    cmd = war.CCmd(war.End)
    war.g_Turn = war.g_Turn + 1
    war.g_TurnMax = war.g_TurnMax - 1
    war.g_Weather = 0
    warrecord.EndRecord(netobj)
    net.g_Net.Pause(1)
    import timecontrol
    timecontrol.CTimeControl.ReleaseWarShield()
    import mazemap
    mazemap.SwitchGameView(True)
    oNetObj = net.GetNet()
    if oNetObj:
        oNetObj.SetServerCmdAbleCache(False)
    
    if permission.IsTestNewbieProfile():
        hero.SetPlayerExtAttr('iIsFirstWar', 0)
    


def S2CWarTurn(netobj):
    print '! S2CWarTurn'
    import warturn
    import permission
    import warriorskillicon
    warriorskillicon.ClearAllSkillIcon()
    warturn.StoreTurnState()
    cmd = war.CCmd(war.Turn)
    if not netobj.UnpackInt(1):
        cmd.lastcmd = False
    else:
        cmd.lastcmd = True
    recordvideo.GetVideoMgr().AddTurnNum()
    
    try:
        if not war.GetReplayWar():
            import warui
            warui.Hide()
    except:
        pass

    war.g_Turn = war.g_Turn + 1
    war.g_TurnMax = war.g_TurnMax + 1
    import warui
    if war.g_HeroID is None and warui.g_MagicKeyDlg:
        warui.SetMagicKeyDlgShow(False)
    
    import commoncb
    commoncb.TriggerCB(commoncb.WAR_SERVER_TURNCNTCHANGE)
    import preload_interface
    preload_interface.StartParserCmd()
    oNetObj = net.GetNet()
    if oNetObj:
        if not (cmd.lastcmd) or permission.IsTestLastWarCmd():
            oNetObj.SetServerCmdAbleCache(False)
        


def S2CChangeTimer(netobj):
    cmd = war.CCmd(war.ChangeTimer)
    cmd.passTime = netobj.UnpackInt(1)
    cmd.isOprated = netobj.UnpackInt(1)
    cmd.isInMagic = netobj.UnpackInt(1)


def S2CWarAdd(netobj):
    cmd = war.CCmd(war.Add)
    if g_WarVersion >= 1:
        cmd.realid = netobj.UnpackInt(4)
    
    cmd.id = netobj.UnpackInt(1)
    cmd.shape = netobj.UnpackInt(2)
    if war.g_ReplayVer == 1:
        cmd.desc = netobj.UnpackInt(2)
        cmd.dDesc = cmd.desc.copy()
    elif war.g_ReplayVer == 2:
        cmd.desc = netobj.UnpackInt(4)
        cmd.dDesc = cmd.desc.copy()
    else:
        cmd.desc = prop.UnpackDesc(netobj)
        cmd.dDesc = cmd.desc.copy()
        cmd.desc['horse'] = None
    if g_WarVersion >= 1:
        cmd.shape = oldwalkerprocess.SpecialShape(cmd.realid, cmd.shape, cmd.desc)
    
    cmd.allied = netobj.UnpackBit(0, 1)
    cmd.type = netobj.UnpackBit(1, 1)
    cmd.child = netobj.UnpackBit(2, 1)
    _ = netobj.UnpackBit(3, 5)
    cmd.owner_id = netobj.UnpackInt(1)
    cmd.place = 0
    if g_WarVersion <= 2:
        if war.g_ReplayVer in (1, 2, 3):
            cmd.cls = 255
            cmd.grade = 255
        elif war.RECORD_VERSION in (4, 5):
            cmd.cls = netobj.UnpackInt(1)
            cmd.grade = netobj.UnpackInt(1)
        else:
            cmd.place = netobj.UnpackBit(0, 5)
            cmd.cls = netobj.UnpackBit(5, 3)
            cmd.grade = netobj.UnpackInt(1)
    else:
        cmd.place = netobj.UnpackInt(1)
        cmd.cls = netobj.UnpackInt(1)
        cmd.grade = netobj.UnpackInt(1)
    cmd.name = netobj.UnpackString(0)
    cmd.leader = 0
    print '! S2CWarAdd ID:%d shape=%d allied=%d leader=%d type=%d place=%d owner_id=%d name=%s' % (cmd.id, cmd.shape, cmd.allied, cmd.leader, cmd.type, cmd.place, cmd.owner_id, cmd.name), cmd.desc


def S2CWarDel(netobj):
    cmd = war.CCmd(war.Delete)
    cmd.id = netobj.UnpackInt(1)
    print '! S2CWarDel ID:%d' % cmd.id


def S2CWarAttackNormal(netobj):
    cmd = war.CCmd(war.AttackNormal)
    cmd.att_id = netobj.UnpackInt(1)
    cmd.vic_id = netobj.UnpackInt(1)
    print '! S2CWarAttackNormal( attacker_id:%d victim_id=%d' % (cmd.att_id, cmd.vic_id)


def GS2CWarShape(netobj):
    cmd = war.CCmd(war.ChgShape)
    cmd.id = netobj.UnpackInt(1)
    cmd.shape = netobj.UnpackInt(2)
    if war.g_ReplayVer == 1:
        cmd.desc = netobj.UnpackInt(2)
    elif war.g_ReplayVer == 2:
        cmd.desc = netobj.UnpackInt(4)
    else:
        cmd.desc = prop.UnpackDesc(netobj)
        cmd.desc['horse'] = None
    cmd.name = netobj.UnpackString(0)
    print '! GS2CWarShape( id:%d shape=%d name=%s' % (cmd.id, cmd.shape, cmd.name)


def S2CWarAttackNormalEnd(netobj):
    cmd = war.CCmd(war.AttackNormalEnd)
    cmd.id = netobj.UnpackInt(1)
    print '! S2CWarAttackNormalEnd', cmd.id


def S2CWarAttackConverg(netobj):
    cmd = war.CCmd(war.AttackConverg)
    cmd.att_id = netobj.UnpackInt(1)
    cmd.vic_id = netobj.UnpackInt(1)
    print '! S2CWarAttackConverg attacker_id:%d victim_id=%d' % (cmd.att_id, cmd.vic_id)


def S2CWarProtect(netobj):
    cmd = war.CCmd(war.Protect)
    cmd.protector_id = netobj.UnpackInt(1)
    cmd.protege_id = netobj.UnpackInt(1)
    print '! S2CWarPROTECT saver_id:%d id=%d' % (cmd.protector_id, cmd.protege_id)


def S2CWarPerform(netobj):
    cmd = war.CCmd(war.Perform)
    cmd.id = netobj.UnpackInt(1)
    cmd.pid = netobj.UnpackInt(2)
    cmd.vic_ids = []
    for i in xrange(netobj.GetCmdLen() - 3):
        cmd.vic_ids.append(netobj.UnpackInt(1))
    
    LOG_DEBUG('! S2CWarPerform id=%d pid=%d  victim_id:' % (cmd.id, cmd.pid), cmd.vic_ids)
    recordvideo.GetVideoMgr().AddSpecialSkillCnt(cmd.pid)


def S2CWarWState(netobj):
    cmd = war.CCmd(war.State)
    cmd.id = netobj.UnpackInt(1)
    cmd.hurt = netobj.UnpackBit(0, 4)
    cmd.life = netobj.UnpackBit(4, 2)
    cmd.ward = netobj.UnpackBit(6, 2)
    cmd.hp_chg = netobj.UnpackInt(4)
    cmd.resist = netobj.UnpackSigned(1)
    cmd.isplayani = netobj.UnpackInt(1)
    print '! S2CWarWState id:%d hurt=%d life=%d ward=%d hp_chg=%d resist=%d isplayani=%d' % (cmd.id, cmd.hurt, cmd.life, cmd.ward, cmd.hp_chg, cmd.resist, cmd.isplayani)


def S2CWarOtherPerform(netobj):
    iSubType = netobj.UnpackInt(1)
    print '! S2CWarOtherPerform'
    if iSubType == 1:
        cmd = war.CCmd(war.Shield)
        cmd.id = netobj.UnpackInt(1)
        cmd.type = netobj.UnpackInt(1)
        cmd.shield_chg = netobj.UnpackInt(4)
        print '! S2CWarShield id: %d shield_chg: %d type: %d' % (cmd.id, cmd.shield_chg, cmd.type)
    elif iSubType == 2:
        cmd = war.CCmd(war.ExtraEffect)
        cmd.id = netobj.UnpackInt(1)
        cmd.effectid = netobj.UnpackInt(2)
        cmd.turn = netobj.UnpackInt(1)
        print '! S2CWarExtraEffect id: %d effectid: %d turn: %d' % (cmd.id, cmd.effectid, cmd.turn)
    elif iSubType == 3:
        iWarriorID = netobj.UnpackInt(1)
        iShowBar = netobj.UnpackInt(1)
        war.SetHpBarShowInfo(iWarriorID, iShowBar)
        LOG_DEBUG('\xb1\xb1\xa8\xee\xbe\xd4\xa4h\xacO\xa7_\xc5\xe3\xa5\xdc\xa6\xe5\xb1\xf8', iWarriorID, iShowBar)
    elif iSubType == 4:
        iShowType = netobj.UnpackInt(1)
        LOG_DEBUG('\xb1\xb1\xa8\xee\xb2\xe1\xa4\xd1\xae\xf0\xaaw\xc5\xe3\xa5\xdc\xa4\xe8\xa6\xa1', iShowType)
        import chatoutput
        chatoutput.SetChatFloatType(iShowType)
    elif iSubType == 5:
        S2CWarriorNameColor(netobj)
    elif iSubType == 6:
        S2CWarriorHpColor(netobj)
    elif iSubType == 7:
        S2CWarriorSwap(netobj)
    elif iSubType == 8:
        S2CDelTargetLine(netobj)
    elif iSubType == 9:
        S2CWarPerformAtPos(netobj)
    elif iSubType == 10:
        S2CWarJuben(netobj)
    elif iSubType == 11:
        S2CShowPassWarBtn(netobj)
    elif iSubType == 12:
        S2CChangeDirection(netobj)
    elif iSubType == 13:
        S2CPlayMagic(netobj)
    elif iSubType == 14:
        S2CMultiWalkTo(netobj)
    elif iSubType == 15:
        S2CWarNotifyExt(netobj)
    elif iSubType == 16:
        S2CServerShout(netobj)
    elif iSubType == 17:
        S2CWarMPFPPercent(netobj)
    elif iSubType == 18:
        S2CWarDecideWinnerTime(netobj)
    


def S2CServerShout(netobj):
    cmd = war.CCmd(war.ServerShout)
    cmd.iID = netobj.UnpackInt(1)
    cmd.sShoutText = netobj.UnpackPS(1)
    cmd.iType = netobj.UnpackInt(1)


def S2CChangeDirection(netobj):
    iObjID = netobj.UnpackInt(1)
    iDir = netobj.UnpackInt(1)
    cmd = war.CCmd(war.ChangeDir)
    cmd.id = iObjID
    cmd.iDir = iDir
    LOG_DEBUG('! S2CChangeDirection id: %d dir: %d' % (iObjID, iDir))


def S2CPlayMagic(netobj):
    lstObjID = []
    iLen = netobj.UnpackInt(1)
    cmd = war.CCmd(war.PlayMagicAction)
    for _ in range(iLen):
        lstObjID.append(netobj.UnpackInt(1))
    
    cmd.lstObjID = lstObjID
    LOG_DEBUG('\xb1\xb1\xa8\xee\xbc\xbd\xa9\xf1magic\xb0\xca\xa7@', lstObjID)


def S2CMultiWalkTo(netobj):
    dWalkInfo = { }
    iLen = netobj.UnpackInt(1)
    for _ in xrange(iLen):
        iOrder = netobj.UnpackInt(1)
        iPos = netobj.UnpackInt(1)
        dWalkInfo[iOrder] = iPos
    
    cmd = war.CCmd(war.WarriorMultiWalkTo)
    cmd.walkinfo = dWalkInfo
    LOG_DEBUG('\xa6h\xa4H\xa6\xe6\xa8\xab', dWalkInfo)


def S2CWarNotifyExt(netobj):
    '''
\t\xb3q\xa5\xce\xbe\xd4\xb0\xab\xa4\xa4\xae\xf8\xae\xa7\xb4\xa3\xa5\xdc\xa1A\xb7\xd3\xb7hnethero\xa4\xa4\xaa\xbaS2CNotifyExt
\t\xa5\xd8\xabe\xa5u\xa4\xe4\xab\xf94\xa1A\xa6p\xaaG\xa6\xb3\xbb\xdd\xadn\xa5i\xa5H\xa5h\xbc\xd2\xa5\xe9S2CNotifyExt\xaa\xba\xa5N\xbdX
\t'''
    import usermacro
    import wrapinterface
    import permission
    iShowType = netobj.UnpackInt(1)
    itype = netobj.UnpackInt(1)
    iShape = netobj.UnpackInt(4)
    iLen = netobj.UnpackInt(1)
    sMsg = netobj.UnpackString(iLen)
    if permission.GetSpecialVersion():
        if itype == 0 and itype == 4:
            usermacro.AddItemPrpmptTips(iShape, wrapinterface.ReplaceChatIDLink(sMsg), 200)
        else:
            usermacro.MOVE_MSG(itype, iShape, wrapinterface.ReplaceChatIDLink(sMsg), 200, iShowType)
    else:
        usermacro.MOVE_MSG(itype, iShape, wrapinterface.ReplaceChatIDLink(sMsg), 200, iShowType)
    LOG_DEBUG('\xb3q\xa5\xce\xbe\xd4\xb0\xab\xb4\xa3\xa5\xdc', itype)


def S2CDelTargetLine(netobj):
    cmd = war.CCmd(war.DelTargetLine)
    cmd.sourceID = netobj.UnpackInt(1)
    cmd.targetID = netobj.UnpackInt(1)
    LOG_DEBUG('!!!S2CDelTargetLine', cmd.sourceID, cmd.targetID)


def S2CWarPerformAtPos(netobj):
    '''
\t:param netobj:
\t:return:
\t'''
    import magicdata
    cmd = war.CCmd(war.PerformAtPos)
    cmd.id = netobj.UnpackInt(1)
    cmd.pid = netobj.UnpackInt(4)
    cmd.vic_lst = []
    iVicLen = netobj.UnpackInt(1)
    for idx in range(iVicLen):
        iSide = netobj.UnpackInt(1)
        iPlace = netobj.UnpackInt(1)
        cmd.vic_lst.append((10000 + idx, iSide, iPlace))
    
    LOG_DEBUG('!!!S2CWarPerformAtPos', cmd.id, cmd.pid, cmd.vic_lst)
    if magicdata.IsDestMagic(cmd.pid, '\xaa\xab\xb2z'):
        acmd = war.CCmd(war.AttackNormal)
        acmd.att_id = cmd.id
        acmd.vic_id = 10000
        acmd = war.CCmd(war.AttackNormalEnd)
        acmd.clear_lst = cmd.vic_lst
        acmd.id = 0
    


def S2CWarJuben(netobj):
    iJubenID = netobj.UnpackInt(1)
    cmd = war.CCmd(war.WarJuben)
    cmd.iJubenID = iJubenID
    LOG_DEBUG('!!!S2CWarJuben', cmd.iJubenID)


def S2CShowPassWarBtn(netobj):
    import warui
    warui.ShowPassWarBtn()
    LOG_DEBUG('!!!S2CShowWarJumpBtn')


def S2CWarriorSwap(netobj):
    '''
\t\xa5\xe6\xb4\xab\xa6\xec\xb8m
\t'''
    iLen = netobj.UnpackInt(1)
    tWapeList = []
    for _ in range(iLen):
        iOderID = netobj.UnpackInt(1)
        iPlace = netobj.UnpackInt(1)
        tWapeList.append((iOderID, iPlace))
    
    cmd = war.CCmd(war.WarriorSwap)
    cmd.swapinfo = tWapeList


def S2CWarriorHpColor(netobj):
    '''
\t\xacO\xa7_\xa6b\xbe\xd4\xb0\xab\xb3\xf5\xb4\xba\xa4\xa4\xc5\xe3\xa5\xdcboss\xa6\xe5\xb1\xf8(\xa9\xf3\xa4\xd1\xc5]\xc3\xfe\xa6\xfc)
\t'''
    iOrder = netobj.UnpackInt(1)
    iMaxNum = netobj.UnpackInt(1)
    iOwnNum = netobj.UnpackInt(1)
    cmd = war.CCmd(war.ShowWarriorHpBar)
    cmd.iOrder = iOrder
    cmd.iMaxNum = iMaxNum
    cmd.iOwnNum = iOwnNum


def S2CWarriorNameColor(netobj):
    '''
\t\xad\xd7\xa7\xef\xaei\xa5\xdc\xa6W\xa6r\xc3C\xa6\xe2, iType 1 \xb6\xc0\xa6\xe2
\t'''
    iOrder = netobj.UnpackInt(1)
    iType = netobj.UnpackInt(1)
    LOG_DEBUG('\xad\xd7\xa7\xef\xaei\xa5\xdc\xa6W\xa6r\xc3C\xa6\xe2:', iOrder, iType)
    if iType == 1:
        import interface
        war.SetWarriorNameColor(iOrder, interface.COLOR_43)
    


def S2CWarMPFP(netobj):
    ID = netobj.UnpackInt(1)
    iType = netobj.UnpackInt(1)
    value = netobj.UnpackInt(4)
    func = None if iType == 1 else war.FpChange
    cmd = war.CCmd(func)
    cmd.id = ID
    cmd.value = value
    print '! S2CWarMPFP id=%d iType=%d value=%d' % (ID, iType, value)


def S2CWarAddon(netobj):
    cmd = war.CCmd(war.Addon)
    cmd.id = netobj.UnpackInt(1)
    cmd.pid = netobj.UnpackInt(2)
    cmd.turn = netobj.UnpackInt(1)
    cmd.series = netobj.UnpackInt(1)
    cmd.magicId = netobj.UnpackInt(2)
    print '! S2CWarADDON id=%d pid=%d turn=%d cmd.series:%d magicId=%d' % (cmd.id, cmd.pid, cmd.turn, cmd.series, cmd.magicId)


def S2CWarSpecialAddon(netobj):
    cmd = war.CCmd(war.SpecialAddon)
    cmd.id = netobj.UnpackInt(1)
    cmd.pid = netobj.UnpackInt(2)
    cmd.turn = netobj.UnpackInt(1)
    cmd.series = netobj.UnpackInt(1)
    print '! S2CWarSpecialAddon id=%d pid=%d turn=%d' % (cmd.id, cmd.pid, cmd.turn)


def S2CWarWeather(netobj):
    cmd = war.CCmd(war.Weather)
    cmd.weather = netobj.UnpackInt(1)
    war.g_Weather = cmd.weather
    print '! S2CWarWeather weather=%d' % cmd.weather


def S2CWarPlayerChat(netobj):
    cmd = war.CCmd(war.PlayerChat)
    cmd.channel = netobj.UnpackInt(1)
    if cmd.channel == 2:
        cmd.direction = netobj.UnpackInt(1)
    else:
        cmd.direction = 2
    cmd.word = netobj.UnpackString(0)
    print '! S2CWarPlayerChat  channel=%d direction=%d word=%s' % (cmd.channel, cmd.direction, cmd.word)


def S2CWarHPPercent(netobj):
    cmd = war.CCmd(war.HPPercent)
    cmd.id = netobj.UnpackInt(1)
    cmd.per = netobj.UnpackInt(1)
    print '! S2CWarHPPercent id:%d status=%d' % (cmd.id, cmd.per)


def S2CWarMPFPPercent(netobj):
    pid = netobj.UnpackInt(1)
    cmdmp = war.CCmd(war.MPPercent)
    cmdmp.per = netobj.UnpackInt(1)
    cmdmp.id = pid
    cmdfp = war.CCmd(war.FPPercent)
    cmdfp.per = netobj.UnpackInt(1)
    cmdfp.id = pid
    LOG('! S2CWarMPFPPercent id:%d mp status=%d fp status=%d' % (pid, cmdmp.per, cmdfp.per))


def S2CWarDecideWinnerTime(netobj):
    import C_marshal
    sDecideTimeData = netobj.UnpackPS(1)
    dDecideTimeData = C_marshal.loads(sDecideTimeData)
    oCmd = war.CCmd(war.OpenDecideTime)
    oCmd.dDecideTimeData = dDecideTimeData


def S2CWarSummon(netobj):
    cmd = war.CCmd(war.Summon)
    cmd.id = netobj.UnpackInt(1)
    cmd.op = netobj.UnpackInt(1)
    print '! S2CWarSUMMON id=%d' % cmd.id


def S2CWarSummonCatch(netobj):
    cmd = war.CCmd(war.Catch)
    cmd.id = netobj.UnpackInt(1)
    cmd.sumid = netobj.UnpackInt(1)
    cmd.success = netobj.UnpackInt(1)
    print '! S2CWarSummonCatch id=%d sumid=%d success=%d' % (cmd.id, cmd.sumid, cmd.success)


def S2CWarONACT(netobj):
    import world
    iPlayerIndex = netobj.UnpackInt(1)
    obj = world.GetObj(iPlayerIndex)
    if obj:
        obj.m_WaitingTimePercent = 100
    


def S2CBackCommand(netobj):
    import warui
    import hero
    import world
    iPlayerIndex = netobj.UnpackInt(1)
    iPetIndex = netobj.UnpackInt(1)
    iPlayerID = netobj.UnpackInt(4)
    oPlayer = world.GetObj(iPlayerIndex)
    oPet = world.GetObj(iPetIndex)
    if oPlayer:
        oPlayer.m_WaitingTimePercent = 30
    
    if oPet:
        oPet.m_WaitingTimePercent = 30
    
    if iPlayerID == hero.GetHeroID():
        warui.ShowHeroMenu()
    


def S2CPerformName(netobj):
    wid = netobj.UnpackInt(1)
    skill = netobj.UnpackString(0)
    cmd = war.CCmd(war.PerformName)
    cmd.id = wid
    cmd.sktxt = skill
    print '!!!!!S2CPerformName', wid, skill


def C2SWarSpecial(id, sid):
    net.g_Net.PacketPrepare(net.C2GS_WAR_SP)
    net.g_Net.PacketAddI(id, 1)
    net.g_Net.PacketAddI(sid, 2)
    net.g_Net.PacketSend()


def S2CWarSign(netobj):
    msg = netobj.UnpackString(0)
    print 'S2CWarSign = %s' % msg
    import warui
    warui.OnSign(msg)


def C2SSendSign(msg):
    print 'send sign %s' % msg
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_WAR_TEAM)
    netobj.PacketAddS(msg, len(msg))
    netobj.PacketSend()


def C2SLookWarrior(order):
    print 'look warrior'
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_WAR_LOOK)
    netobj.PacketAddI(order, 1)
    netobj.PacketSend()


def S2CWarChildSkill(netobj):
    grade = netobj.UnpackInt(1)
    war.g_ChildGrade = grade
    war.g_ChildSkills = []
    cnt = netobj.UnpackInt(1)
    for i in xrange(cnt):
        skid = netobj.UnpackInt(2)
        war.g_ChildSkills.append(skid)
    
    import pet
    ob = pet.GetActivatePet()
    if ob and isinstance(ob, pet.CChild):
        ob.SetProp('m_Grade', grade)
        ob.UpdateSkill(war.g_ChildSkills)
    


def S2CWarCalledPet(netobj):
    import warui
    warui.g_CallPetLeft = netobj.UnpackInt(1)
    canCallChild = netobj.UnpackInt(1)
    warui.g_CanCallChild = canCallChild
    canAgainCall = netobj.UnpackInt(1)
    calledPetNum = netobj.UnpackInt(1)
    calledPet = []
    for i in xrange(calledPetNum):
        calledPet.append(netobj.UnpackInt(4))
    
    
    try:
        canAgainCall.g_CanCallAgain = None
        warui.g_CallPets = calledPet
        return None



def S2CChangeAction(netobj):
    cmd = war.CCmd(war.ChgAction)
    cmd.id = netobj.UnpackInt(1)
    cmd.action = netobj.UnpackInt(1)
    print '! S2CChangeAction id=%d, action=%d' % (cmd.id, cmd.action)


def S2CWalkTo(netobj):
    print '! S2CWalkTo'
    cmd = war.CCmd(war.WarriorWalkTo)
    cmd.id = netobj.UnpackInt(1)
    cmd.endPlace = netobj.UnpackInt(1)


def S2CWarExtInfo(netobj):
    iIsVideo = netobj.UnpackInt(1)
    iIsWatch = netobj.UnpackInt(1)
    import mdwatchcompetition
    mdwatchcompetition.GetWatchModel().SetIsWarRecord(bool(iIsVideo))
    mdwatchcompetition.GetWatchModel().SetIsWatchWar(bool(iIsWatch))
    LOG('\xbe\xd4\xb0\xab\xc3B\xa5~\xabH\xae\xa7\xa1A\xacO\xa7_\xac\xb0\xbf\xfd\xb9\xb3\xa1G%s\xa1A\xacO\xa7_\xac\xb0\xc6[\xbe\xd4\xa1G%s>' % (iIsVideo, iIsWatch))


def S2CShowSpecialWatchPanel(netobj):
    import mdwatchcompetition
    import watchcompetiondefine
    import avatar
    iLen = netobj.UnpackInt(1)
    dEnemyInfo = { }
    iEnemyIDList = []
    dEnemyPlace = { }
    dAlliedInfo = { }
    iAlliedIDList = []
    dAlliedPlace = { }
    for _ in range(iLen):
        dInfo = { }
        dInfo[watchcompetiondefine.KEY_PLAYER_ID] = iPlayerID = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_PLAYER_CLASS] = war.GetWarriorClass(iPlayerID)
        dInfo[watchcompetiondefine.KEY_PLAYER_GRADE] = war.GetWarriorGrade(iPlayerID)
        dInfo[watchcompetiondefine.KEY_PLAYER_PLACE] = iPlace = war.GetWarriorPlace(iPlayerID)
        dInfo[watchcompetiondefine.KEY_PET_IN_CUR] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_PET_IN_MAX] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_DRUG_CUR] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_DRUG_MAX] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_SP] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_AVATAR] = avatar.UnpackPhotoInt4(netobj)
        if war.IsAllide(iPlayerID):
            dAlliedInfo[iPlayerID] = dInfo
            dAlliedPlace[iPlace] = iPlayerID
            continue
        dEnemyInfo[iPlayerID] = dInfo
        dEnemyPlace[iPlace] = iPlayerID
    
    for iPlace in [
        4,
        2,
        0,
        1,
        3]:
        if iPlace in dAlliedPlace:
            iAlliedIDList.append(dAlliedPlace[iPlace])
            continue
    
    for iPlace in [
        3,
        1,
        0,
        2,
        4]:
        if iPlace in dEnemyPlace:
            iEnemyIDList.append(dEnemyPlace[iPlace])
            continue
    
    import mainmenu
    import warui
    oModel = mdwatchcompetition.GetWatchModel()
    LOG(war.GetWarType(), oModel.IsWarRecord(), oModel.IsWatchWar())
    if warui.IsShowSpecialWatch():
        mainmenu.SwitchSpecialWatchModel(True)
    
    oModel.SetWatchInfo(dEnemyInfo, iEnemyIDList, dAlliedInfo, iAlliedIDList)
    LOG('\xa5\xb4\xb6}\xc6[\xbe\xd4\xad\xb1\xaaO')
    LOG('dEnemyInfo>', dEnemyInfo)
    LOG('iEnemyIDList>', iEnemyIDList)
    LOG('dAlliedInfo>', dAlliedInfo)
    LOG('iAlliedIDList>', iAlliedIDList)


def S2CUpdateSpecialWatchPanelPetInfo(netobj):
    import mdwatchcompetition
    iPlayerID = netobj.UnpackInt(1)
    iCur = netobj.UnpackInt(1)
    iMax = netobj.UnpackInt(1)
    if permission.IsWatchWar():
        mdwatchwar.GetModel().UpdatePetData(iPlayerID, iCur, iMax)
    else:
        mdwatchcompetition.GetWatchModel().UpdatePetInInfo(iPlayerID, iCur, iMax)
    LOG('\xa7\xf3\xb7s\xc6[\xbe\xd4\xad\xb1\xaaO\xc3d\xaa\xab\xabH\xae\xa7', iPlayerID, iCur, iMax)


def S2CUpdateSpecialWatchPanelDrugInfo(netobj):
    import mdwatchcompetition
    iPlayerID = netobj.UnpackInt(1)
    iCur = netobj.UnpackInt(1)
    iMax = netobj.UnpackInt(1)
    if permission.IsWatchWar():
        mdwatchwar.GetModel().UpdateDrugData(iPlayerID, iCur, iMax)
    else:
        mdwatchcompetition.GetWatchModel().UpdateDrugInfo(iPlayerID, iCur, iMax)
    LOG('\xa7\xf3\xb7s\xc6[\xbe\xd4\xad\xb1\xaaO\xc3\xc4\xaa\xab\xabH\xae\xa7', iPlayerID, iCur, iMax)


def S2CUpdateSpecialWatchPanelSpInfo(netobj):
    import mdwatchcompetition
    iPlayerID = netobj.UnpackInt(1)
    iSp = netobj.UnpackInt(1)
    if permission.IsWatchWar():
        mdwatchwar.GetModel().UpdateSpData(iPlayerID, iSp)
    else:
        mdwatchcompetition.GetWatchModel().UpdateSp(iPlayerID, iSp)
    mdlcommandskilltips.GetCommandSkillTipsModel().UpdateSpData(iPlayerID, iSp)
    LOG('\xa7\xf3\xb7s\xc6[\xbe\xd4\xad\xb1\xaaO\xbc\xab\xab\xe3\xad\xc8', iPlayerID, iSp)


def S2CUpdateRecordShowInfo(netobj):
    import warinfo
    iWarriorID = netobj.UnpackInt(1)
    iTurn = netobj.UnpackInt(1)
    sCmd = netobj.UnpackPS(1)
    dInfo = netobj.UnpackMarshal(2)
    warinfo.SetWarInfo(iWarriorID, iTurn, sCmd, dInfo)


def S2CUpateRecordInfo(netobj):
    import watchcompetiondefine
    import avatar
    import warui
    import mainmenu
    dAllInfo = { }
    iLen = netobj.UnpackInt(1)
    for _ in range(iLen):
        dInfo = { }
        dInfo[watchcompetiondefine.KEY_PLAYER_ID] = iPlayerID = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_PET_IN_CUR] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_PET_IN_MAX] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_DRUG_CUR] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_DRUG_MAX] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_SP] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_ATTACK] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_DEFENSE] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_OBSTRUCT] = netobj.UnpackInt(1)
        dInfo[watchcompetiondefine.KEY_AVATAR] = avatar.UnpackPhotoInt4(netobj)
        dAllInfo[iPlayerID] = dInfo
    
    import mdwatchwar
    if warui.IsShowSpecialWatch():
        mainmenu.SwitchNewSpecialWatchModel(True)
    
    mdwatchwar.GetModel().SetPointPanalInfo(dAllInfo)


def S2CUpdateControlPoint(netobj):
    iPlayerId = netobj.UnpackInt(1)
    iAttack = netobj.UnpackInt(1)
    iDefense = netobj.UnpackInt(1)
    iObstruct = netobj.UnpackInt(1)
    mdwatchwar.GetModel().UpdateControlPoint(iPlayerId, iAttack, iDefense, iObstruct)
    mdlcommandskilltips.GetCommandSkillTipsModel().UpdateControlPoint(iPlayerId, iAttack, iDefense, iObstruct)

g_WarRecordInfoFunc = {
    1: S2CWarExtInfo,
    2: S2CWarMPFPPercent,
    3: S2CShowSpecialWatchPanel,
    4: S2CUpdateSpecialWatchPanelPetInfo,
    5: S2CUpdateSpecialWatchPanelDrugInfo,
    6: S2CUpdateSpecialWatchPanelSpInfo,
    7: S2CUpdateRecordShowInfo,
    8: S2CUpateRecordInfo,
    9: S2CUpdateControlPoint }

def S2CWarRecordInfo(netobj):
    iSub = netobj.UnpackInt(1)
    LOG_DEBUG('S2CWarRecordInfo>>', iSub)
    oFunc = g_WarRecordInfoFunc.get(iSub)
    if oFunc:
        pass
    oFunc(netobj)
