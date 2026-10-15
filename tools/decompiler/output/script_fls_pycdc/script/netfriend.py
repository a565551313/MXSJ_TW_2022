# pycdc 交叉复核产物 · script.fls entry 4238
# co_filename(原始)='script/netfriend.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4238.pyc (Python 2.5)

import avatar
import friend
import net
import prop
import protocolprint
import mdaddfriend
import searchfrienddefine
import dlgsearchfriendmain

def S2CFindFriend(netobj):
    iLen = netobj.UnpackInt(1)
    lPlayer = []
    import common
    for i in xrange(iLen):
        pid = prop.UnpackPlayerID(netobj)
        showID = netobj.UnpackInt(4)
        shape = netobj.UnpackInt(1)
        name = common.UnpackString(netobj)
        lPlayer.append((pid, name))
    
    import dlgfriend
    dlgfriend.ShowPlayerList(lPlayer)


def S2CFriendAdd(netobj):
    ftype = netobj.UnpackInt(1)
    iPlayerID = prop.UnpackPlayerID(netobj)
    oMgr = friend.GetControl()
    obj = oMgr.CreatePlayer(iPlayerID)
    obj.m_FriendType = ftype
    obj.m_ZmAccountID = netobj.UnpackInt(4)
    obj.m_Grade = netobj.UnpackInt(2)
    obj.m_Vip = netobj.UnpackInt(1)
    obj.m_Blog = netobj.UnpackInt(4)
    obj.m_Icon = netobj.UnpackInt(1)
    obj.m_FriendShip = netobj.UnpackInt(4)
    obj.m_Relation = netobj.UnpackInt(1)
    obj.m_STRelation = netobj.UnpackInt(1)
    iGroup = netobj.UnpackInt(1)
    obj.m_FriendGroup = friend.GetFrdMgr().ChangeGroup(iGroup)
    obj.m_Vip20 = netobj.UnpackInt(1)
    obj.m_Vip30 = netobj.UnpackInt(1)
    obj.m_Game200Hour = netobj.UnpackInt(1)
    obj.m_Mobile = netobj.UnpackInt(1)
    obj.m_Team = netobj.UnpackInt(1)
    import common
    obj.m_MarkName = common.UnpackString(netobj)
    obj.m_Name = netobj.UnpackString(20)
    lPhoto = avatar.UnpackPhotoInt4(netobj)
    obj.m_PhotoArr = avatar.Int2PhotoArr(lPhoto[0], lPhoto[1], lPhoto[2], lPhoto[3])
    iShape = netobj.UnpackInt(2)
    dDesc = prop.UnpackDesc(netobj)
    obj.SetRoleViewInfo((iShape, dDesc))
    obj.m_Class = netobj.UnpackInt(1)
    obj.m_HuiGui = netobj.UnpackInt(1)
    obj.m_ZhaoMuName = netobj.UnpackString(16)
    avatar.UnpackAvatarData(netobj, iPlayerID)
    iGroupID = netobj.UnpackInt(4)
    obj.m_iGroupID = iGroupID
    import hero
    lastTime = hero.GetPrivateData('latestchat', str(iPlayerID))
    if lastTime and lastTime.isdigit():
        obj.m_LastChatTime = int(lastTime)
    
    oMgr.Add2Folder(iPlayerID, oMgr.Type2FolderName(ftype))
    oMgr.OpenTalkDlg(iPlayerID)
    import dlgfriend
    dlgfriend.CheckIsShowAddLimitBtn()
    import dlginfo
    dlginfo.ForcedRefreshInfoDlg(iPlayerID)
    import groupcontext
    import groupdefines
    import netgroup
    oContext = groupcontext.Get()
    oGroupMgr = oContext.GetGroupDataMgr()
    if oContext.IsOpenDestPage(groupdefines.E_GROUPPAGE_INFO) and oGroupMgr.IsPlayerInMember(iPlayerID):
        netgroup.C2SGetMemberList()
    
    import mdnewbuyflower
    oMgr = mdnewbuyflower.GetCBuyFlowerMgr()
    oMgr.RefreshFriendShip()
    RefreshCharMenuList(iPlayerID, obj.m_ZmAccountID)
    import logicrefreshuserinfo
    logicrefreshuserinfo.RefreshUserInfo(iPlayerID)
    import banword
    if obj.m_MarkName:
        banword.AddCheckWordTask([
            (obj.m_MarkName, iPlayerID)], 'friendmarkname')
    


def RefreshCharMenuList(iPid, iAccountId):
    '''
\t\xa8\xea\xb7s\xac\xc9\xad\xb1\xa4W\xaa\xbaMenuList\xa1A\xb6\xc8\xa5]\xacA\xa5k\xc1\xe4\xa4H\xaa\xab\xa9\xce\xa5k\xc1\xe4\xb6\xa4\xa5\xee\xc0Y\xb9\xb3\xbcu\xa5X\xaa\xba\xa8\xba\xa8\xe2\xba\xd8MenuList
\t'''
    import mainmenu
    import teamui
    if mainmenu.IsWar():
        return None
    
    if not mainmenu.g_MainMenu:
        return None
    
    if teamui.g_PopMenu and teamui.g_PopMenu.GetShow():
        sName = getattr(teamui.g_PopMenu, 'm_ObjectName', '')
        iExistId = getattr(teamui.g_PopMenu, 'm_ObjectID', -1)
        if sName and iExistId == iPid:
            teamui.CreatePopMenu(iPid, sName, iAccountId, bKeepPosition = True)
        
    
    oTargetObj = mainmenu.g_MainMenu.GetTargetObj()
    if not oTargetObj:
        return None
    
    if not isinstance(oTargetObj, mainmenu.CTargetFrame) and not isinstance(oTargetObj, mainmenu.CTargetPngFrame):
        return None
    
    if getattr(oTargetObj, 'm_ObjectID', -1) != iPid:
        return None
    
    oPopMenu = getattr(oTargetObj, 'm_PopMenu', None)
    if oPopMenu and oPopMenu.GetShow():
        oTargetObj.SetAccountID(iAccountId)
    


def S2CFriendDel(netobj):
    ftype = netobj.UnpackInt(1)
    pid = netobj.UnpackInt(4)
    oMgr = friend.GetControl()
    oMgr.DelFriend(pid, oMgr.Type2FolderName(ftype))
    import dlgfriend
    dlgfriend.CheckIsShowAddLimitBtn()
    import mdnewbuyflower
    oMgr = mdnewbuyflower.GetCBuyFlowerMgr()
    oMgr.RefreshFriendShip()


def S2CAuth(netobj):
    pid = prop.UnpackPlayerID(netobj)
    name = netobj.UnpackString(20)
    iType = netobj.UnpackInt(1)
    friend.Auth(pid, name, iType)


def S2CRequest(netobj):
    pid = prop.UnpackPlayerID(netobj)
    iType = netobj.UnpackInt(1)
    name = netobj.UnpackString(20)
    msg = netobj.UnpackString(0)
    friend.Request(pid, name, iType, msg)


def S2CLimit(netobj):
    limit = netobj.UnpackInt(1)
    friend.GetFrdMgr().SetAmountLimit(limit)
    import dlgfriend
    dlgfriend.CheckIsShowAddLimitBtn()


def S2CBanList(netobj):
    bBan = netobj.UnpackInt(1)
    pid = prop.UnpackPlayerID(netobj)
    name = netobj.UnpackString(0)
    import friend
    import netchat
    oMgr = friend.GetControl()
    sName = friend.CFolderBan.DIRNAME
    if not bBan:
        oMgr.RemoveFromFolder(pid, sName)
        netchat.RemoveIgnorUser(pid)
    else:
        obj = oMgr.CreatePlayer(pid)
        obj.m_Name = name
        oMgr.Add2Folder(pid, sName)
        netchat.AddIgnoreUser(pid)


def S2CPermit(netobj):
    '''
\t\xa8\xf3\xc4\xb3\xa1GGS2C_FRIEND
\tsub: 5
\t:param netobj:
\t:return:
\t'''
    import permission
    addpermit = netobj.UnpackInt(1)
    msgpermit = netobj.UnpackInt(1)
    iAutoPush = netobj.UnpackInt(1)
    friend.GetExtMgr().SetPushPermit(iAutoPush)
    if permission.IsOpenFriendPushMsg():
        iPushFriend = netobj.UnpackInt(1)
        friend.GetExtMgr().SetPushFriendPermit(iPushFriend)
    
    reply = netobj.UnpackInt(1)
    showOldName = netobj.UnpackInt(1)
    l = netobj.UnpackInt(1)
    if l > 0:
        sReply = netobj.UnpackString(l)
    else:
        sReply = None
    iSameCityPermit = netobj.UnpackInt(1)
    sIntro = netobj.UnpackString(0)
    oExt = friend.GetExtMgr()
    oExt.SetAddPermit(addpermit)
    oExt.SetMsgPermit(msgpermit)
    oExt.SetShowOldName(showOldName)
    oExt.SetSameCityPermit(iSameCityPermit)


def S2CFriendInfo(netobj):
    import dlgtalk
    import dlginfo
    import mainmenu
    import popmenu
    import avatar
    iPlayerID = prop.UnpackPlayerID(netobj)
    obj = friend.GetControl().CreatePlayer(iPlayerID)
    obj.m_Name = netobj.UnpackString(20)
    obj.m_Blog = netobj.UnpackInt(4)
    bBirthDay = netobj.UnpackInt(1)
    obj.m_Grade = netobj.UnpackInt(1)
    obj.m_Class = netobj.UnpackInt(1)
    obj.m_Country = netobj.UnpackInt(1)
    obj.m_iShowSkillID = netobj.UnpackInt(4)
    obj.m_iShowSkillLevel = netobj.UnpackInt(1)
    lPhoto = avatar.UnpackPhotoInt4(netobj)
    obj.m_PhotoArr = mainmenu.Int2PhotoArr(lPhoto[0], lPhoto[1], lPhoto[2], lPhoto[3])
    iShape = netobj.UnpackInt(2)
    dDesc = prop.UnpackDesc(netobj)
    obj.SetRoleViewInfo((iShape, dDesc))
    avatar.UnpackAvatarData(netobj, iPlayerID)
    lBadge = []
    for i in range(8):
        lBadge.append(netobj.UnpackInt(2))
    
    obj.m_Badge = lBadge
    obj.m_OrgName = netobj.UnpackString(20)
    titleLen = netobj.UnpackInt(1)
    if titleLen:
        obj.m_Title = netobj.UnpackString(titleLen)
    else:
        obj.m_Title = ''
    bShowOldName = netobj.UnpackInt(1)
    iLen = netobj.UnpackInt(1)
    lOldName = []
    for i in xrange(iLen):
        lOldName.append(netobj.UnpackString(22))
    
    obj.m_OldNameDct = {
        'bShow': bShowOldName,
        'nameList': lOldName }
    bShowCG = netobj.UnpackInt(1)
    obj.m_iLiuPai = netobj.UnpackInt(2)
    obj.m_Intro = netobj.UnpackString(0)
    obj.Apply()
    dlgtalk.RefreshInfo(iPlayerID, obj.m_Name, obj.m_Blog, bBirthDay)
    dlginfo.RefreshInfo(iPlayerID, obj.m_Name, obj.m_Blog, bBirthDay)
    if popmenu.GetPlayerLookType() != popmenu.POPMENU_TYPE_TEAM:
        mainmenu.RefreshTargetMenu(iPlayerID, bShowCG)
    
    import logicrefreshuserinfo
    logicrefreshuserinfo.RefreshUserInfo(iPlayerID)


def S2CPlayerInfo(netobj):
    iPlayerID = prop.UnpackPlayerID(netobj)
    obj = friend.GetControl().CreatePlayer(iPlayerID)
    obj.m_Vip = netobj.UnpackInt(1)
    obj.m_Blog = netobj.UnpackInt(4)
    obj.m_Icon = netobj.UnpackInt(1)
    obj.m_Name = netobj.UnpackString(20)
    obj.m_Grade = netobj.UnpackInt(1)
    obj.m_Class = netobj.UnpackInt(1)
    obj.m_Country = netobj.UnpackInt(1)
    obj.m_Online = netobj.UnpackInt(1)
    obj.m_iShowSkillID = netobj.UnpackInt(4)
    obj.m_iShowSkillLevel = netobj.UnpackInt(1)
    lPhoto = avatar.UnpackPhotoInt4(netobj)
    obj.m_PhotoArr = avatar.Int2PhotoArr(lPhoto[0], lPhoto[1], lPhoto[2], lPhoto[3])
    iShape = netobj.UnpackInt(2)
    dDesc = prop.UnpackDesc(netobj)
    obj.SetRoleViewInfo((iShape, dDesc))
    avatar.UnpackAvatarData(netobj, iPlayerID)
    lBadge = []
    for i in range(8):
        lBadge.append(netobj.UnpackInt(2))
    
    obj.m_Badge = lBadge
    obj.m_Mobile = netobj.UnpackInt(1)
    obj.m_OrgName = netobj.UnpackString(20)
    titleLen = netobj.UnpackInt(1)
    if titleLen:
        obj.m_Title = netobj.UnpackString(titleLen)
    else:
        obj.m_Title = ''
    bShowCG = netobj.UnpackInt(1)
    obj.m_Intro = netobj.UnpackString(0)
    obj.Apply()
    import dlgtalk
    import dlginfo
    import mainmenu
    import popmenu
    import chatoutput
    dlgtalk.RefreshInfo(iPlayerID, obj.m_Name, obj.m_Blog, 1)
    dlginfo.RefreshInfo(iPlayerID, obj.m_Name, obj.m_Blog, 1)
    if popmenu.GetPlayerLookType() != popmenu.POPMENU_TYPE_TEAM:
        mainmenu.RefreshTargetMenu(iPlayerID, bShowCG)
    
    chatoutput.ReCreateChannelMenu(iPlayerID)
    import groupviewsignal
    groupviewsignal.Emit(groupviewsignal.SS_UPDATE_PLAYERINFO, obj)
    import logicrefreshuserinfo
    logicrefreshuserinfo.RefreshUserInfo(iPlayerID)


def S2COnline(netobj):
    pid = netobj.UnpackInt(4)
    iInKuaFu = netobj.UnpackInt(1)
    obj = friend.GetControl().GetSafePlayer(pid)
    if obj:
        import time
        obj.m_Online = True
        obj.m_Time = time.time()
        obj.m_iKuaFu = iInKuaFu
        obj.Apply()
    


def S2COffline(netobj):
    pid = netobj.UnpackInt(4)
    obj = friend.GetControl().GetSafePlayer(pid)
    if obj:
        obj.m_Online = False
        obj.Apply()
    


def S2CLastPlayer(netobj):
    iType = netobj.UnpackInt(1)
    pid = prop.UnpackPlayerID(netobj)
    name = netobj.UnpackPS()
    oMgr = friend.GetControl()
    obj = oMgr.CreatePlayer(pid)
    obj.m_Name = name
    oMgr.Add2Folder(pid, friend.CFolderLast.DIRNAME)
    obj.Apply()


def S2CLatelyTeamPlayerByOnce(netobj):
    iLen = netobj.UnpackInt(2)
    for i in range(iLen):
        S2CLatelyTeamPlayer(netobj)
    


def S2CLatelyTeamPlayer(netobj):
    iPlayerID = prop.UnpackPlayerID(netobj)
    sName = netobj.UnpackPS()
    lPhoto = avatar.UnpackPhotoInt4(netobj)
    avatar.UnpackAvatarData(netobj, iPlayerID)
    iOnline = netobj.UnpackInt(1)
    oMgr = friend.GetControl()
    oObj = oMgr.CreatePlayer(iPlayerID)
    oObj.m_Online = iOnline
    oObj.m_PhotoArr = avatar.Int2PhotoArr(lPhoto[0], lPhoto[1], lPhoto[2], lPhoto[3])
    oObj.m_Name = sName
    oMgr.Add2Folder(iPlayerID, friend.CFolderLatelyTeam.DIRNAME)
    oObj.Apply()


def S2CRemoveFromFolderByOnce(netobj):
    iLen = netobj.UnpackInt(2)
    for i in range(iLen):
        S2CRemoveFromFolder(netobj)
    


def S2CRemoveFromFolder(netobj):
    iPlayerID = prop.UnpackPlayerID(netobj)
    oMgr = friend.GetControl()
    oMgr.RemoveFromFolder(iPlayerID, friend.CFolderLatelyTeam.DIRNAME)


def S2CAchieveScore(netobj):
    import modelpersondataopt
    import hero
    import dlginfo
    iPid = prop.UnpackPlayerID(netobj)
    iScore = netobj.UnpackInt(4)
    iRank = netobj.UnpackInt(2)
    bShow = netobj.UnpackInt(1)
    if hero.GetHeroID() == iPid:
        oPersonModel = modelpersondataopt.GetPersonDataOptMdl()
        oPersonModel.SetAchieve(iScore, iRank)
        oPersonModel.SetAchieveSwitch(bShow)
    
    oFriend = friend.GetControl().GetSafePlayer(iPid)
    if oFriend:
        dct = {
            'score': iScore,
            'rank': iRank }
        oFriend.m_AchieveDct = dct
    
    dlginfo.UpdateAchieve(iPid, iScore, iRank)


def S2CFriendsGroup(netobj):
    iLen = netobj.UnpackInt(1)
    dGroup = {
        1: '\xa7\xda\xaa\xba\xa6n\xa4\xcd' }
    for i in xrange(iLen):
        iGroup = netobj.UnpackInt(1)
        name = netobj.UnpackString(14)
        dGroup[iGroup] = name
    
    friend.GetFrdMgr().UpdateGroupDct(dGroup)


def S2CFriendsNote(netobj):
    dct = { }
    lens = netobj.UnpackInt(1)
    for i in range(lens):
        theme = netobj.UnpackString(12)
        num = netobj.UnpackInt(2)
        if not num:
            txt = ''
        else:
            txt = netobj.UnpackString(num)
        dct[theme] = txt
    
    import dlgfriend
    dlgfriend.GetNoteDialog(dct)


def S2CRefershTeamIcon(netobj):
    pid = prop.UnpackPlayerID(netobj)
    inTeam = netobj.UnpackInt(1)
    obj = friend.GetControl().GetSafePlayer(pid)
    if obj:
        obj.m_Team = inTeam
        obj.Apply(False)
    


def S2CFindResult(netobj):
    result = netobj.UnpackInt(1)
    if result:
        pid = prop.UnpackPlayerID(netobj)
        import dlginfo
        dlginfo.ShowInfoDialog(pid)
    else:
        import usermacro
        usermacro.PROMPT_MSG('\xacd\xb5L\xa6\xb9\xa4H\xa1A\xbd\xd0\xbdT\xbb{\xab\xe1\xa6A\xb6i\xa6\xe6\xacd\xb8\xdf')


def S2CSetRequestList(netobj):
    import commonfriend
    rqList = []
    iLen = netobj.UnpackInt(1)
    for i in xrange(iLen):
        pid = prop.UnpackPlayerID(netobj)
        iMode = netobj.UnpackInt(1)
        linkType = netobj.UnpackInt(1)
        iNameLen = netobj.UnpackInt(1)
        sName = netobj.UnpackString(iNameLen)
        iState = netobj.UnpackInt(1)
        rtime = netobj.UnpackInt(4)
        dInfo = {
            'frdtype': iMode,
            'nick': sName,
            'status': iState,
            'linkType': linkType,
            'time': rtime }
        rqList.append((pid, dInfo))
    
    commonfriend.SetRequestList(rqList)


def S2CAddRequest(netobj):
    import commonfriend
    pid = prop.UnpackPlayerID(netobj)
    iMode = netobj.UnpackInt(1)
    linkType = netobj.UnpackInt(1)
    iNameLen = netobj.UnpackInt(1)
    sName = netobj.UnpackString(iNameLen)
    iState = netobj.UnpackInt(1)
    rtime = netobj.UnpackInt(4)
    commonfriend.AddFrdRequest(pid, iMode, sName, linkType, rtime)


def S2CUpdateFriendSystemMsg(netobj):
    '''
\t\xa7\xf3\xb7s\xa7\xda\xaa\xba\xa6n\xa4\xcd\xb0\xca\xbaA\xabH\xae\xa7
\t:param netobj:
\t:return:
\t'''
    iLen = netobj.UnpackInt(2)
    dFriendMsglst = []
    for i in range(iLen):
        iID = None(None, None, None, None, None, None, None, netobj.UnpackInt, 4)
        sMsg = netobj.UnpackPS()
        dFriendMsglst.append({
            'iID': iID,
            'sMsg': sMsg })
    
    import accountfriend
    accountfriend.SetAllAccountSystemMsg(dFriendMsglst)


def S2CPlayerRelation(netobj):
    dRelation = { }
    iLen = netobj.UnpackInt(1)
    for _ in xrange(iLen):
        iPlayerID = netobj.UnpackInt(4)
        iRelation = netobj.UnpackInt(4)
        dRelation[iPlayerID] = iRelation
    
    print '>>>S2CPlayerRelation>', dRelation
    friend.GetArdPlayerMgr().UpdateSortKey(dRelation)


class CImpress(object):
    s_Sub2FuncName = {
        1: 'S2CLocation',
        2: 'S2CGameDynamic',
        3: 'S2CAppraise',
        4: 'S2CNewAppraise' }
    
    def Process(cls, netobj):
        iSub = netobj.UnpackInt(1)
        name = cls.s_Sub2FuncName.get(iSub)
        print 'netfriend CImpress', name
        if name:
            func = getattr(cls, name, None)
            if func:
                func(netobj)
                protocolprint.AppendS2CSubInfo('netgroup.CImpress', func.__name__, iSub)
            
        

    Process = classmethod(Process)
    
    def S2CLocation(cls, netobj):
        pid = netobj.UnpackInt(4)
        obj = friend.CreatePlayer(pid)
        obj.m_Location = netobj.UnpackString(0)

    S2CLocation = classmethod(S2CLocation)
    
    def S2CGameDynamic(cls, netobj):
        import common
        pid = netobj.UnpackInt(4)
        lDynamics = []
        iLen = netobj.UnpackInt(1)
        for i in xrange(iLen):
            iTime = netobj.UnpackInt(4)
            sDynamic = common.UnpackString(netobj)
            lDynamics.append((iTime, sDynamic))
        
        lDynamics.sort(key = (lambda t: t[0]))
        obj = friend.CreatePlayer(pid)
        obj.m_DynamicList = lDynamics

    S2CGameDynamic = classmethod(S2CGameDynamic)
    
    def S2CAppraise(cls, netobj):
        data = []
        pid = netobj.UnpackInt(4)
        obj = friend.CreatePlayer(pid)
        addnum = netobj.UnpackInt(1)
        iLen = netobj.UnpackInt(1)
        for i in xrange(iLen):
            aid = netobj.UnpackInt(4)
            iTime = netobj.UnpackInt(4)
            istop = netobj.UnpackInt(1)
            clen = netobj.UnpackInt(1)
            content = netobj.UnpackString(clen)
            data.append([
                aid,
                iTime,
                istop,
                content])
        
        obj.m_AppraiseData = data
        import dlghistory
        import dlgfriend
        dlghistory.RefreshAppraise(data)
        dlgfriend.RefreshNewNum(addnum, pid)

    S2CAppraise = classmethod(S2CAppraise)
    
    def S2CNewAppraise(cls, netobj):
        aid = netobj.UnpackInt(4)
        addnum = netobj.UnpackInt(1)
        import dlgfriend
        dlgfriend.RefreshNewNum(addnum, -1)

    S2CNewAppraise = classmethod(S2CNewAppraise)
    
    def C2SPacketPrepare(cls):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(33, 1)
        return netobj

    C2SPacketPrepare = classmethod(C2SPacketPrepare)
    
    def GetAllImpress(cls, pid):
        netobj = cls.C2SPacketPrepare()
        netobj.PacketAddI(1, 1)
        netobj.PacketAddI(pid, 4)
        netobj.PacketSend()
        print 'GetAllImpress'

    GetAllImpress = classmethod(GetAllImpress)
    
    def C2SGetLocation(cls, pid):
        return None
        netobj = cls.C2SPacketPrepare()
        netobj.PacketAddI(2, 1)
        netobj.PacketAddI(pid, 4)
        netobj.PacketSend()

    C2SGetLocation = classmethod(C2SGetLocation)
    
    def CS2GetGetDynamic(cls, pid):
        netobj = cls.C2SPacketPrepare()
        netobj.PacketAddI(3, 1)
        netobj.PacketAddI(pid, 4)
        netobj.PacketSend()

    CS2GetGetDynamic = classmethod(CS2GetGetDynamic)
    
    def C2SAddFriendLimit(cls):
        '''\xbd\xd0\xa8D\xbcW\xa5[\xa6n\xa4\xcd\xa4W\xad\xad'''
        netobj = cls.C2SPacketPrepare()
        netobj.PacketAddI(33, 1)
        netobj.PacketSend()

    C2SAddFriendLimit = classmethod(C2SAddFriendLimit)
    
    def GetAllAppraise(cls, pid):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(34, 1)
        netobj.PacketAddI(1, 1)
        netobj.PacketAddI(pid, 4)
        netobj.PacketSend()

    GetAllAppraise = classmethod(GetAllAppraise)
    
    def C2SAddAppraise(cls, pid, scontent):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(34, 1)
        netobj.PacketAddI(2, 1)
        netobj.PacketAddI(pid, 4)
        netobj.PacketAddS(scontent, len(scontent))
        netobj.PacketSend()

    C2SAddAppraise = classmethod(C2SAddAppraise)
    
    def C2STopAppraise(cls, sid, istop):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(34, 1)
        netobj.PacketAddI(3, 1)
        netobj.PacketAddI(sid, 4)
        netobj.PacketAddI(istop, 1)
        netobj.PacketSend()

    C2STopAppraise = classmethod(C2STopAppraise)
    
    def C2SDelAppraise(cls, sid):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(34, 1)
        netobj.PacketAddI(4, 1)
        netobj.PacketAddI(sid, 4)
        netobj.PacketSend()

    C2SDelAppraise = classmethod(C2SDelAppraise)
    
    def C2SViewAppraise(cls):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(34, 1)
        netobj.PacketAddI(5, 1)
        netobj.PacketSend()

    C2SViewAppraise = classmethod(C2SViewAppraise)


def S2CSearchFriendInfo(netobj):
    dPlayerDataLst = []
    iPlayerLen = netobj.UnpackInt(1)
    for iPlayerIdx in range(iPlayerLen):
        iLevel = netobj.UnpackInt(1)
        iJob = netobj.UnpackInt(1)
        iState = netobj.UnpackInt(1)
        iCommonFriend = netobj.UnpackInt(1)
        iPlayerID = netobj.UnpackInt(4)
        (p1, p2, p3, p4) = avatar.UnpackPhotoInt4(netobj)
        sPlayerName = netobj.UnpackPS()
        sFriendName = 'XXXXXX'
        iFriendID = iPlayerID
        iSameCity = netobj.UnpackInt(1)
        dPlayerDataLst.append({
            'bSameCity': iSameCity,
            'iLevel': iLevel,
            'iJob': iJob,
            'iState': iState,
            'iCommonFriend': iCommonFriend,
            'iPlayerID': iPlayerID,
            'sFriendName': sFriendName,
            'sPlayerName': sPlayerName,
            'iFriendID': iFriendID,
            'tPhoto': (p1, p2, p3, p4) })
    
    dlgsearchfriendmain.OpenPage()
    mdaddfriend.GetSearchMainModel().UpdateCurPage(searchfrienddefine.PAGE_SEARCH_FRIEND)
    mdaddfriend.GetSearchModel().UpdateSearchInfo(dPlayerDataLst)
    LOG_DEBUG(dPlayerDataLst)


def S2CApplyFriendResult(netobj):
    '''
\t\xaa\xb1\xaea\xabH\xae\xa7\xa7\xf3\xb7s\xa6^\xbd\xd5
\t:param netobj: 1\xa1B\xa4w\xa6\xa8\xa5\\\xb5o\xb0_\xa5\xd3\xbd\xd0 2\xa1B\xa4w\xb2K\xa5[ 3\xa1B\xa4w\xa9\xda\xb5\xb4
\t:return:
\t'''
    iPlayerID = netobj.UnpackInt(4)
    iState = netobj.UnpackInt(1)
    mdaddfriend.GetSearchMainModel().UpdatePlayerState(iPlayerID, iState)
    if iState == 2:
        import qixiinterface
        qixiinterface.ChatWithFriend(iPlayerID)
    


def S2COpenApplyFriendDlg(netobj):
    dPlayerDataLst = []
    iPlayerLen = netobj.UnpackInt(1)
    for iPlayerIdx in range(iPlayerLen):
        iFriendType = netobj.UnpackInt(1)
        iLevel = netobj.UnpackInt(1)
        iJob = netobj.UnpackInt(1)
        iState = netobj.UnpackInt(1)
        iCommonFriend = netobj.UnpackInt(1)
        iPlayerID = netobj.UnpackInt(4)
        iReportState = netobj.UnpackInt(4)
        iIgnoreState = netobj.UnpackInt(4)
        (p1, p2, p3, p4) = avatar.UnpackPhotoInt4(netobj)
        avatar.UnpackAvatarData(netobj, iPlayerID)
        sPlayerName = netobj.UnpackPS()
        sExtTips = netobj.UnpackPS()
        iApplyTime = netobj.UnpackInt(4)
        iSameCity = netobj.UnpackInt(1)
        dPlayerDataLst.append({
            'bSameCity': iSameCity,
            'iLevel': iLevel,
            'iJob': iJob,
            'iState': iState,
            'iCommonFriend': iCommonFriend,
            'iPlayerID': iPlayerID,
            'iReportState': iReportState,
            'sPlayerName': sPlayerName,
            'iFriendType': iFriendType,
            'iIgnoreState': iIgnoreState,
            'sExtTips': sExtTips,
            'tPhoto': (p1, p2, p3, p4),
            'iApplyTime': iApplyTime })
    
    dlgsearchfriendmain.OpenPage()
    mdaddfriend.GetSearchMainModel().UpdateCurPage(searchfrienddefine.PAGE_APPLY_FRIEND)
    mdaddfriend.GetAddFriendModel().UpdateApplyInfo(searchfrienddefine.PAGE_APPLY_FRIEND, dPlayerDataLst)


def S2COpenRecommendFriendDlg(netobj):
    dPlayerDataLst = []
    iPlayerLen = netobj.UnpackInt(1)
    for iPlayerIdx in range(iPlayerLen):
        iLevel = netobj.UnpackInt(1)
        iJob = netobj.UnpackInt(1)
        iState = netobj.UnpackInt(1)
        iCommonFriend = netobj.UnpackInt(1)
        iPlayerID = netobj.UnpackInt(4)
        iGroup = netobj.UnpackInt(1)
        (p1, p2, p3, p4) = avatar.UnpackPhotoInt4(netobj)
        avatar.UnpackAvatarData(netobj, iPlayerID)
        sPlayerName = netobj.UnpackPS()
        iSameCity = netobj.UnpackInt(1)
        dPlayerDataLst.append({
            'iLevel': iLevel,
            'iJob': iJob,
            'iState': iState,
            'iCommonFriend': iCommonFriend,
            'iPlayerID': iPlayerID,
            'iGroup': iGroup,
            'sPlayerName': sPlayerName,
            'tPhoto': (p1, p2, p3, p4),
            'bSameCity': iSameCity })
    
    mdaddfriend.GetAddFriendModel().UpdateRecommendInfo(searchfrienddefine.PAGE_RECOMMAND_FRIEND, dPlayerDataLst)


def S2CUpdateRedPoint(netobj):
    '''
\t\xa7\xf3\xb7s\xac\xf5\xc2I
\t:param netobj:
\t:return:
\t'''
    import mdaddfriend
    iRedPointNum = netobj.UnpackInt(1)
    mdaddfriend.GetAddFriendModel().SetRedPointNum(iRedPointNum)


def S2CRefreshInfoIconState(netobj):
    import dlginfo
    iPlayerID = prop.UnpackPlayerID(netobj)
    oPlayer = friend.GetControl().CreatePlayer(iPlayerID)
    iIconState = netobj.UnpackInt(4)
    iHaveHorseOrFairy = netobj.UnpackInt(1)
    iNumber = netobj.UnpackInt(1)
    oPlayer.SetIconState(iIconState)
    oPlayer.SetWalkStateTypeAndNum(iHaveHorseOrFairy, iNumber)
    if iHaveHorseOrFairy and not iNumber:
        LOG('\xad\xd3\xa4H\xabH\xae\xa7\xac\xc9\xad\xb1--- \xaaA\xb0\xc8\xbe\xb9\xbc\xc6\xbe\xda\xa6\xb3\xbb~ Pid: %d, \xc3M\xad\xbc\xbc\xd2\xa6\xa1: %d, \xbds\xb8\xb9: %d' % (iPlayerID, iHaveHorseOrFairy, iNumber))
    
    dlginfo.RefreshInfo(iPlayerID, '', getattr(oPlayer, 'm_Blog', ''), False)

g_Func = {
    1: S2CAuth,
    2: S2CRequest,
    3: S2CLimit,
    4: S2CBanList,
    5: S2CPermit,
    6: S2CFriendInfo,
    7: S2CPlayerInfo,
    8: S2COnline,
    9: S2COffline,
    10: S2CLastPlayer,
    14: S2CAchieveScore,
    15: S2CFriendsGroup,
    16: S2CFriendsNote,
    18: S2CRefershTeamIcon,
    19: S2CFindResult,
    20: S2CSetRequestList,
    21: S2CAddRequest,
    23: CImpress.Process,
    24: S2CApplyFriendResult,
    26: S2CSearchFriendInfo,
    27: S2COpenRecommendFriendDlg,
    22: S2COpenApplyFriendDlg,
    25: S2CUpdateRedPoint,
    30: S2CUpdateFriendSystemMsg,
    31: S2CPlayerRelation,
    32: S2CLatelyTeamPlayerByOnce,
    33: S2CRemoveFromFolderByOnce,
    34: S2CRefreshInfoIconState }

def S2CFriend(netobj):
    itype = netobj.UnpackInt(1)
    print '=============S2CFriend============', itype
    func = g_Func.get(itype)
    if callable(func):
        protocolprint.AppendS2CSubInfo('netfriend', func.__name__, itype)
        func(netobj)
    


def C2SAddFriend(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SAddTemp(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SDelFriend(pid, delme):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(9, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(delme, 1)
    netobj.PacketSend()


def C2SRemoveStranger(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(10, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SSetPermit(addpermit, msgpermit, sopermit, iPush = 0, iPushFriend = 0, iOpenCity = 0):
    '''
\t\xa8\xf3\xc4\xb3\xa1GC2GS_FRIEND
\tsub : 3
\t1b addpermit
\t1b msgpermit
\t1b sopermit
\t1b ipush
\t1b icitypermit
\t1b pushfriend
\t'''
    import permission
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(3, 1)
    netobj.PacketAddI(addpermit, 1)
    netobj.PacketAddI(msgpermit, 1)
    netobj.PacketAddI(sopermit, 1)
    netobj.PacketAddI(iPush, 1)
    netobj.PacketAddI(iOpenCity, 1)
    if permission.IsOpenFriendPushMsg():
        netobj.PacketAddI(iPushFriend, 1)
    
    netobj.PacketSend()


def C2SSendAuth(pid, iType, msg):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(iType, 1)
    netobj.PacketAddS(msg, len(msg))
    netobj.PacketSend()


def C2SAnswerAuth(pid, answer):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(5, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(answer, 1)
    netobj.PacketSend()


def C2SSendHint(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(6, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SSendMail(pid, msg, iToZhanMeng):
    '''
\t\t\xa5\xd1\xa9\xf3\xbf\xe9\xa4J\xae\xd8\xb2{\xa6b\xa4@\xa6\xb8\xb3\xcc\xa6h\xaf\xe0\xbf\xe9\xa4J3\xb1\xf8\xc3\xec\xb1\xb5\xa1A\xa6\xfd\xacY\xa8\xc7\xc3\xec\xb1\xb5\xb9L\xaa\xf8\xbe\xc9\xadP\xa8\xf3\xc4\xb3\xb0e\xa4\xa3\xb9L\xa5h\xa1A
\t\t\xa9\xd2\xa5H\xb2{\xa6b\xb6i\xa6\xe6\xa4\xc0\xa7\xe5\xb5o\xb0e\xa1A\xb3W\xabh\xac\xb0\xa1G
\t\t1\xa1B\xa6\xb3\xc3\xec\xb1\xb5\xae\xc9\xb5o\xb0e\xa8\xe2\xb1\xf8\xc3\xec\xb1\xb5\xb9L\xa5h\xa1A\xa4\xa3\xa8\xac\xa8\xe2\xb1\xf8\xae\xc9\xb5o\xa4@\xb1\xf8\xb9L\xa5h
\t\t2\xa1B\xa8\xe4\xbel\xa4\xe5\xa5\xbb\xaa\xbd\xb1\xb5\xb5o\xb9L\xa5h
\t'''
    import re
    netobj = net.g_Net
    tmpMsgLst = re.split('([#s(].*?[)])', msg)
    oMsgLst = []
    for sMsg in tmpMsgLst:
        if sMsg != '':
            oMsgLst.append(sMsg)
            continue
    
    iMsgLstLen = len(oMsgLst)
    iIndex = 0
    sMsg = ''
    while iIndex < iMsgLstLen:
        if oMsgLst[iIndex].startswith('#s('):
            if iIndex + 1 < iMsgLstLen:
                sMsg = oMsgLst[iIndex] + oMsgLst[iIndex + 1]
                iIndex += 2
            else:
                sMsg = oMsgLst[iIndex]
                iIndex += 1
            netobj.PacketPrepare(net.C2GS_FRIEND)
            netobj.PacketAddI(7, 1)
            netobj.PacketAddI(pid, 4)
            netobj.PacketAddI(iToZhanMeng, 1)
            netobj.PacketAddS(sMsg, len(sMsg))
            import netpublic
            netpublic.SplitPacketSend(netobj, net.C2GS_FRIEND)
            sMsg = ''
            continue
        sMsg += oMsgLst[iIndex]
        netobj.PacketPrepare(net.C2GS_FRIEND)
        netobj.PacketAddI(7, 1)
        netobj.PacketAddI(pid, 4)
        netobj.PacketAddI(iToZhanMeng, 1)
        netobj.PacketAddS(sMsg, len(sMsg))
        import netpublic
        netpublic.SplitPacketSend(netobj, net.C2GS_FRIEND)
        sMsg = ''
        iIndex += 1


def C2SGetInfo(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(8, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SSetGroup(pid, group):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(11, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(group, 1)
    netobj.PacketSend()


def C2SFindWithID(pid, force, iServerID = 0):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(12, 1)
    netobj.PacketAddI(0, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(iServerID, 4)
    netobj.PacketAddI(force, 1)
    netobj.PacketSend()


def C2SFindWithName(name):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(12, 1)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddS(name, len(name))
    netobj.PacketSend()


def C2SBanPlayer(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(13, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SUnbanPlayer(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(14, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SRemoveLast(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(15, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SSendSysmail(pid, msg):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(16, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddS(msg, len(msg))
    netobj.PacketSend()


def C2SSetIntro(msg):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(17, 1)
    netobj.PacketAddS(msg, len(msg))
    netobj.PacketSend()


def C2SSetReply(reply, msg):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(18, 1)
    if reply:
        netobj.PacketAddI(1, 1)
    else:
        netobj.PacketAddI(0, 1)
    if msg is not None:
        netobj.PacketAddS(msg, len(msg))
    
    netobj.PacketSend()


def C2SChangeName(pid, name):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(21, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddS(name, len(name))
    netobj.PacketSend()


def C2SRejectReply(userid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(22, 1)
    netobj.PacketAddI(userid, 4)
    netobj.PacketSend()


def C2SSetAchieve(arg):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(23, 1)
    netobj.PacketAddI(arg, 1)
    netobj.PacketSend()


def C2SGetAchieve(pid, iServerID = 0):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(24, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketAddI(iServerID, 4)
    netobj.PacketSend()


def C2SFriendsRename(group, name):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(25, 1)
    netobj.PacketAddI(group, 1)
    netobj.PacketAddS(name, 14)
    netobj.PacketSend()


def C2SFriendsDel(group):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(26, 1)
    netobj.PacketAddI(group, 1)
    netobj.PacketSend()


def C2SWriteNote(idx, content):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(27, 1)
    netobj.PacketAddI(idx, 1)
    if idx:
        for key in content.keys():
            netobj.PacketAddS(key, 12)
            netobj.PacketAddI(len(content[key]), 2)
            netobj.PacketAddS(content[key], len(content[key]))
        
    
    import netpublic
    netpublic.SplitPacketSend(netobj, net.C2GS_FRIEND)


def C2SOpenNote():
    net.g_Net.PacketPrepare(net.C2GS_FRIEND)
    net.g_Net.PacketAddI(28, 1)
    net.g_Net.PacketSend()


def C2SVoiceRecognize(pid, msg):
    net.g_Net.PacketPrepare(net.C2GS_FRIEND)
    net.g_Net.PacketAddI(29, 1)
    net.g_Net.PacketAddI(pid, 4)
    net.g_Net.PacketAddS(msg, len(msg))
    net.g_Net.PacketSend()


def C2SFindPlayerByID(pid):
    net.g_Net.PacketPrepare(net.C2GS_FRIEND)
    net.g_Net.PacketAddI(30, 1)
    net.g_Net.PacketAddI(pid, 4)
    net.g_Net.PacketSend()


def C2SChangeRequestType(pid, iType):
    net.g_Net.PacketPrepare(net.C2GS_FRIEND)
    net.g_Net.PacketAddI(31, 1)
    net.g_Net.PacketAddI(pid, 4)
    net.g_Net.PacketAddI(iType, 1)
    net.g_Net.PacketSend()


def C2SOpenRequestUi(pid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(32, 1)
    netobj.PacketAddI(pid, 4)
    netobj.PacketSend()


def C2SSetSkillShow(iSkillID):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(35, 1)
    netobj.PacketAddI(iSkillID, 4)
    netobj.PacketSend()


def C2SCloseApplyPage():
    '''
\t\xc3\xf6\xb3\xac\xa5\xd3\xbd\xd0\xac\xc9\xad\xb1\xa1G\xab\xe1\xba\xdd\xbb\xdd\xadn\xadp\xba\xe2\xa5\xd3\xbd\xd0\xac\xc9\xad\xb1\xaa\xba\xac\xf5\xc2I\xbc\xc6\xb6q
\t:return:
\t'''
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(40, 1)
    netobj.PacketSend()


def C2SOpenRecommendFriendDlg():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(36, 1)
    netobj.PacketSend()


def C2SOpenApplyFriendDlg():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(37, 1)
    netobj.PacketSend()


def C2SSearchFriendInfo(sTxt):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(38, 1)
    netobj.PacketAddS(sTxt, len(sTxt))
    netobj.PacketSend()


def C2SChangeRecommendFriend():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(39, 1)
    netobj.PacketSend()


def C2SFindPlayerWithName(playername):
    import netpublic
    netobj = netpublic.PacketPrepare(netpublic.C2GS_SUB_FINDFRIEND)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddS(playername, len(playername))
    netobj.PacketSend()


def C2SQueryRelation(iPlayerIDList):
    import netpublic
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(41, 1)
    print 'C2SQueryRelation>>>>>', iPlayerIDList
    netobj.PacketAddI(len(iPlayerIDList), 1)
    for iID in iPlayerIDList:
        netobj.PacketAddI(iID, 4)
    
    netpublic.SplitPacketSend(netobj, net.C2GS_FRIEND)


def C2SGive(iPlayerID):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(42, 1)
    netobj.PacketAddI(iPlayerID, 4)
    netobj.PacketSend()


def C2SClickIcon(iPlayerID, iIconID):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(43, 1)
    netobj.PacketAddI(iPlayerID, 4)
    netobj.PacketAddI(iIconID, 1)
    netobj.PacketSend()


def C2SSendIconState(iPlayerID, iIconID):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_FRIEND)
    netobj.PacketAddI(44, 1)
    netobj.PacketAddI(iPlayerID, 4)
    netobj.PacketAddI(iIconID, 1)
    netobj.PacketSend()
