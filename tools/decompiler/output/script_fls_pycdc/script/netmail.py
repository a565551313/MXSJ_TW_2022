# pycdc 交叉复核产物 · script.fls entry 2725
# co_filename(原始)='script/netmail.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2725.pyc (Python 2.5)

import net
import prop
g_DelayCall = None
g_dCallCounter = { }

def ModuleReset():
    global g_DelayCall, g_dCallCounter
    g_DelayCall = None
    g_dCallCounter = { }


def S2CPlayerMail(netobj):
    import avatar
    uShow = netobj.UnpackInt(1)
    pid = prop.UnpackPlayerID(netobj)
    icon = netobj.UnpackInt(1)
    photo = avatar.UnpackPhotoInt4(netobj)
    name = netobj.UnpackString(20)
    tm = netobj.UnpackInt(4)
    mode = netobj.UnpackInt(1)
    msg = netobj.UnpackString(0)
    if mode == 3:
        return None
    
    if mode == 4:
        mode = 0
    
    import dlgtalk
    dlgtalk.OnPlayerMail(uShow, pid, name, icon, photo, tm, msg, mode)


def DelayS2CPlayerMailNotify(obj, pid, itype):
    global g_DelayCall
    import dlgtalk
    import sound
    dlgtalk.OnPlayerMailNotifyLimit(pid, itype, g_dCallCounter.get(pid, 1))
    import sounddefine
    sound.Play(sounddefine.PATH_FRIENDMAIL)
    g_DelayCall = None
    LOG_DEBUG('\xa5\xb4\xa6L\xad\xc8\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I%s' % g_dCallCounter.get(pid, '\xa8S\xa6\xb3\xad\xc8\xa1I\xa1I\xa1I'))
    if pid in g_dCallCounter:
        del g_dCallCounter[pid]
    


def S2CPlayerMailNotify(netobj):
    pid = netobj.UnpackInt(4)
    itype = netobj.UnpackInt(1)
    DelayCall(pid, itype)


def DelayCall(pid, itype, bAdd = True):
    global g_DelayCall
    import interface
    import hero
    import time
    g_DelayCall = interface.CBaseObject(None)
    g_DelayCall.CreatePyCommand(30, DelayS2CPlayerMailNotify, pid, itype)
    g_DelayCall.m_PID = pid
    if bAdd:
        if pid not in g_dCallCounter:
            g_dCallCounter[pid] = 1
        else:
            g_dCallCounter[pid] += 1
    
    t = int(time.time())
    hero.SavePrivateData('latestchat', str(pid), t)
    import friend
    oMgr = friend.GetControl()
    obj = oMgr.GetSafePlayer(pid)
    if not obj:
        return None
    
    obj.m_LastChatTime = t
    obj.Apply()


def S2CStopMailNotify(netobj):
    pid = netobj.UnpackInt(4)
    import friend
    import dlgtalk
    import mainmenu
    name = friend.GetFriendName(pid)
    if name != None:
        dlgtalk.ReceiveCall(pid, name)
    
    mainmenu.RefreshPlayerNotify()


def S2CSystemMailNotify(netobj):
    import dlgsysmail
    import sound
    import mdmailcenter
    import delayloading
    mdmailcenter.GetModel().RefreshHasSysMail(True)
    if not delayloading.IsShowLoading():
        import sounddefine
        sound.Play(sounddefine.PATH_FRIENDMAIL)
    


def S2CShowAllSystemMail(netobj):
    dMsgInfo = { }
    import dlgsysmail
    iMsgCount = netobj.UnpackInt(1)
    sMsgList = []
    for i in range(iMsgCount):
        iTime = netobj.UnpackInt(4)
        iMsgLen = netobj.UnpackInt(2)
        sInfo = netobj.UnpackString(iMsgLen)
        sMsgList.append((iTime, sInfo))
        dMsgInfo[(iTime, sInfo)] = {
            'bIsNew': True }
    
    if sMsgList:
        dlgsysmail.ShowMail(sMsgList, dMsgInfo)
    


def S2CRequestNotify(netobj):
    import dlgtalk
    pID = netobj.UnpackInt(4)
    dlgtalk.OnRequestFrdNotify(pID)


def S2CAddSelfChat(netobj):
    pID = netobj.UnpackInt(4)
    tm = netobj.UnpackInt(4)
    mode = netobj.UnpackInt(1)
    msg = netobj.UnpackString(0)
    import dlgtalk
    dlgtalk.AddSelfChat(pID, tm, msg, mode)

MailFunc = {
    1: S2CPlayerMail,
    2: S2CPlayerMailNotify,
    3: S2CStopMailNotify,
    4: S2CSystemMailNotify,
    5: S2CShowAllSystemMail,
    6: S2CRequestNotify,
    7: S2CAddSelfChat }

def S2CMail(netobj):
    import netnewems
    iType = netobj.UnpackInt(1)
    if iType >= 8:
        netnewems.S2CNewEmsProcess(netobj, iType)
    else:
        MailFunc[iType](netobj)


def S2CSpecialMail(netobj):
    S2CMail(netobj)
    return True


def C2SGetMail(itype, target):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_READMAIL)
    netobj.PacketAddI(itype, 1)
    netobj.PacketAddI(target, 4)
    netobj.PacketSend()


def C2SSendEms(recvid, name, validtime, itemLst, recvcash, title, content, iInterfaceIdx = 0):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(iInterfaceIdx, 4)
    netobj.PacketAddI(recvid, 4)
    netobj.PacketAddS(name, 20)
    netobj.PacketAddI(validtime, 1)
    iLen = len(itemLst)
    netobj.PacketAddI(iLen, 1)
    for itemID, amount in itemLst:
        netobj.PacketAddI(itemID, 4)
        netobj.PacketAddI(amount, 2)
    
    netobj.PacketAddI(recvcash, 4)
    netobj.PacketAddI(len(title), 1)
    netobj.PacketAddS(title, len(title))
    netobj.PacketAddS(content, len(content))
    netobj.PacketSend()


def C2SGetRecvName(recvid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(recvid, 4)
    netobj.PacketSend()


def C2SReadMail(senderid, mailid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(3, 1)
    netobj.PacketAddI(senderid, 4)
    netobj.PacketAddI(mailid, 4)
    netobj.PacketSend()


def C2SDelMail(senderid, mailid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(senderid, 4)
    netobj.PacketAddI(mailid, 4)
    netobj.PacketSend()


def C2SGetMailItem(senderid, mailid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(5, 1)
    netobj.PacketAddI(senderid, 4)
    netobj.PacketAddI(mailid, 4)
    netobj.PacketSend()


def C2SRts(senderid, mailid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(6, 1)
    netobj.PacketAddI(senderid, 4)
    netobj.PacketAddI(mailid, 4)
    netobj.PacketSend()


def C2SGetMailItemInfo(senderid, mailid, idx):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(7, 1)
    netobj.PacketAddI(senderid, 4)
    netobj.PacketAddI(mailid, 4)
    netobj.PacketAddI(idx, 1)
    netobj.PacketSend()


def C2SEmsBlackListOperate(operation, target, iWithTips = 1):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(8, 1)
    netobj.PacketAddI(operation, 1)
    netobj.PacketAddI(target, 4)
    netobj.PacketAddI(iWithTips, 1)
    netobj.PacketSend()


def C2SGetAllMail():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_EMS)
    netobj.PacketAddI(9, 1)
    netobj.PacketSend()


def S2CEms(netobj):
    import dlgems
    iSub = netobj.UnpackInt(1)
    print 'iSub', iSub
    if iSub == 1:
        num = netobj.UnpackInt(1)
        data = []
        for i in xrange(num):
            pid = prop.UnpackPlayerID(netobj)
            name = netobj.UnpackString(20)
            online = netobj.UnpackInt(1)
            data.append((pid, name, online))
        
        iInterfaceIdx = netobj.UnpackInt(4)
        import dlgemail
        dlgemail.Show(data, iInterfaceIdx = iInterfaceIdx)
    elif iSub == 2:
        name = netobj.UnpackString(20)
        import dlgemail
        import dlgwishgift
        dlgemail.ShowRecvName(name)
        dlgwishgift.ShowRecvName(name)
    elif iSub == 3:
        iMailNum = netobj.UnpackInt(2)
        tMailLst = []
        for iIdx in xrange(iMailNum):
            mailid = netobj.UnpackInt(4)
            senderid = netobj.UnpackInt(4)
            name = netobj.UnpackString(20)
            sendtime = netobj.UnpackInt(4)
            validtime = netobj.UnpackInt(4)
            savetime = netobj.UnpackInt(4)
            itemLst = []
            iLen = netobj.UnpackInt(1)
            for i in range(iLen):
                shape = netobj.UnpackInt(4)
                amount = netobj.UnpackInt(2)
                sName = netobj.UnpackPS(1)
                bModel = bool(netobj.UnpackInt(1))
                itemLst.append((shape, amount, sName, bModel))
            
            length = netobj.UnpackInt(1)
            title = netobj.UnpackString(length)
            tMailLst.append((mailid, senderid, name, sendtime, validtime, savetime, iLen, itemLst, title))
        
        dlgems.AddMailsToBox(tMailLst)
    elif iSub == 4:
        senderid = netobj.UnpackInt(4)
        mailid = netobj.UnpackInt(4)
        sendername = netobj.UnpackString(20)
        recvcash = netobj.UnpackInt(4)
        remain = netobj.UnpackInt(4)
        data = [
            senderid,
            mailid,
            sendername,
            recvcash,
            remain]
        itemLst = []
        iLen = netobj.UnpackInt(1)
        for i in range(iLen):
            shape = netobj.UnpackInt(4)
            amount = netobj.UnpackInt(1)
            sName = netobj.UnpackPS(1)
            bModel = bool(netobj.UnpackInt(1))
            itemLst.append((shape, amount, sName, bModel))
        
        length = netobj.UnpackInt(1)
        title = netobj.UnpackString(length)
        content = netobj.UnpackString(0)
        dlgems.ReadMail(data, itemLst, title, content)
    elif iSub == 5:
        pass
    elif iSub == 6:
        senderid = netobj.UnpackInt(4)
        mailid = netobj.UnpackInt(4)
        dlgems.DelMailItem(senderid, mailid)
    elif iSub == 7:
        senderid = netobj.UnpackInt(4)
        mailid = netobj.UnpackInt(4)
        ext = netobj.UnpackString(0)
        dlgems.RefreshItemTip(senderid, mailid, ext)
        import dlgmainmail
        dlgmainmail.RefreshItemIconTips(ext)
    elif iSub == 10:
        dlgems.ShowBlackList()
    elif iSub == 11:
        operation = netobj.UnpackInt(1)
        target = netobj.UnpackInt(4)
        name = netobj.UnpackString(0)
        if operation == 1:
            dlgems.ShowBlackList((target, name))
        elif operation == 2:
            dlgems.DelBlackList(target)
        
    elif iSub == 12:
        dlgems.CloseAll()
    elif iSub == 13:
        pass
    


def S2CChargeHistory(netobj):
    iType = netobj.UnpackInt(1)
    msg = netobj.UnpackString(0)
    rec = []
    
    try:
        for l in msg.split('|'):
            (tm, pt, reason, left) = l.split(',')
            rec.append((int(tm), pt, left, reason))
    except:
        pass

    import dlgsysmail
    import dlgcheckrecharge
    if iType == 1:
        dlgsysmail.ShowPointRec(rec)
    else:
        dlgcheckrecharge.Show(rec)
