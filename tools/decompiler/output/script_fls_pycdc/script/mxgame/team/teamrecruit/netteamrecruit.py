# pycdc 交叉复核产物 · script.fls entry 2889
# co_filename(原始)='script/mxgame/team/teamrecruit/netteamrecruit.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2889.pyc (Python 2.5)

import net
import mdteamrecruit
import teamrecruitinterface

def GetNetObj(iSub):
    if teamrecruitinterface.IsOpenNewTeamRecruit():
        return GetTeamRecruitNetObj(iSub)
    else:
        import nethuodong
        netobj = net.PacketPrepare(net.C2GS_HUODONG)
        if netobj:
            sStr = nethuodong.TEAMRECRUIT
            netobj.PacketAddI(len(sStr), 1)
            netobj.PacketAddS(sStr, len(sStr))
            netobj.PacketAddI(iSub, 1)
            LOG_DEBUG('C2S_\xb2\xd5\xb6\xa4\xa9\xdb\xb6\xd2', iSub)
        
        return netobj


def GetTeamRecruitNetObj(iSub):
    import netteam
    oNetObj = netteam.GetTeamRecruitNetObj()
    ORI_SUB_2CUR = {
        1: 1,
        2: 6,
        3: 2,
        4: 7,
        5: 3,
        6: 8,
        7: 4,
        8: 9,
        12: 1,
        13: 6,
        14: 5,
        15: 10,
        16: 11,
        17: 12,
        18: 13,
        19: 14 }
    iSub = ORI_SUB_2CUR.get(iSub, iSub)
    if oNetObj:
        oNetObj.PacketAddI(iSub, 1)
    
    return oNetObj


def C2SRelizeTeam(iTypeList, iTargetList, iTime, iMinGrade, iMaxGrade, iNeedClassList, iGroup, sIntro):
    netobj = GetNetObj(1)
    if netobj:
        iLen = len(iTypeList)
        netobj.PacketAddI(iLen, 1)
        for ID in iTypeList:
            netobj.PacketAddI(ID, 1)
        
        iLen = len(iTargetList)
        netobj.PacketAddI(iLen, 1)
        for iTarget in iTargetList:
            netobj.PacketAddI(iTarget, 1)
        
        netobj.PacketAddI(iTime, 1)
        netobj.PacketAddI(iMinGrade, 2)
        netobj.PacketAddI(iMaxGrade, 2)
        iLen = len(iNeedClassList)
        netobj.PacketAddI(iLen, 1)
        for i in xrange(iLen):
            netobj.PacketAddI(iNeedClassList[i], 1)
        
        netobj.PacketAddI(iGroup, 1)
        netobj.PacketAddPS(sIntro)
        netobj.PacketSend()
    


def C2SRelizeMember(iTargetList, iTime, iGroup, sInrto):
    netobj = GetNetObj(2)
    if netobj:
        iLen = len(iTargetList)
        netobj.PacketAddI(iLen, 1)
        for iTarget in iTargetList:
            netobj.PacketAddI(iTarget, 1)
        
        netobj.PacketAddI(iTime, 1)
        netobj.PacketAddI(iGroup, 1)
        netobj.PacketAddPS(sInrto)
        netobj.PacketSend()
    


def C2SRelizeMember_New(iTargetList, iTime, sInrto):
    netobj = GetNetObj(13)
    if netobj:
        iLen = len(iTargetList)
        netobj.PacketAddI(iLen, 1)
        for iTarget in iTargetList:
            netobj.PacketAddI(iTarget, 1)
        
        netobj.PacketAddI(iTime, 1)
        netobj.PacketAddPS(sInrto)
        netobj.PacketSend()
    


def C2SContactTeam(iPlayerID):
    netobj = GetNetObj(3)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SContactPlayer(iPlayerID):
    netobj = GetNetObj(4)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SCancelTeam(iPlayerID):
    netobj = GetNetObj(5)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SCancelMember(iPlayerID):
    netobj = GetNetObj(6)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SRequestTeamInfo(iFisrt = 0):
    netobj = GetNetObj(7)
    if netobj:
        netobj.PacketAddI(iFisrt, 1)
        netobj.PacketSend()
    


def C2SRequestMemberInfo(iFisrt = 0):
    netobj = GetNetObj(8)
    if netobj:
        netobj.PacketAddI(iFisrt, 1)
        netobj.PacketSend()
    


def C2SChangeTeamGroup():
    netobj = GetNetObj(9)
    if netobj:
        netobj.PacketSend()
    


def C2SChangeTeamRequire():
    netobj = GetNetObj(10)
    if netobj:
        netobj.PacketSend()
    


def C2SChangeMemberGroup():
    netobj = GetNetObj(11)
    if netobj:
        netobj.PacketSend()
    


def C2SRelizeTeam_New(iFriendList, iTargetList, iTime, iMinGrade, iMaxGrade, iNeedClassList, sIntro):
    '''
\t\xa8\xf3\xc4\xb3\xa1Gnet.C2GS_HUODONG
\tsub1\xa1G nethuodong.TEAMRECRUIT
\tsub2: 12
\t'''
    netobj = GetNetObj(12)
    if netobj:
        iLen = len(iFriendList)
        netobj.PacketAddI(iLen, 1)
        for ID in iFriendList:
            netobj.PacketAddI(ID, 4)
        
        iLen = len(iTargetList)
        netobj.PacketAddI(iLen, 1)
        for iTarget in iTargetList:
            netobj.PacketAddI(iTarget, 1)
        
        netobj.PacketAddI(iTime, 1)
        netobj.PacketAddI(iMinGrade, 2)
        netobj.PacketAddI(iMaxGrade, 2)
        iLen = len(iNeedClassList)
        netobj.PacketAddI(iLen, 1)
        for i in xrange(iLen):
            netobj.PacketAddI(iNeedClassList[i], 1)
        
        netobj.PacketAddPS(sIntro)
        netobj.PacketSend()
    


def C2SOpenTeamRecruitDetailDlg(iPlayerID):
    '''C2S\xa5\xb4\xb6}\xa9\xdb\xb6\xd2\xb6\xa4\xa5\xee\xabH\xae\xa7\xac\xc9\xad\xb1
\t\xa8\xf3\xc4\xb3\xa1G net.C2GS_HUODONG
\tsub1: nethuodong.TEAMRECRUIT
\tsub2: 14
\t4b iPlayerID
\t'''
    netobj = GetNetObj(14)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SOpenMemberRecruitDetailDlg(iPlayerID):
    '''C2S\xa5\xb4\xb6}\xb6\xa4\xa5\xee\xa9\xdb\xb6\xd2\xa1A\xa6\xdb\xaf\xf2\xabH\xae\xa7\xac\xc9\xad\xb1
\t\xa8\xf3\xc4\xb3\xa1G net.C2GS_HUODONG
\tsub1: nethuodong.TEAMRECRUIT
\tsub2: 15
\t4b iPlayerID
\t'''
    netobj = GetNetObj(15)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SSubscribeTeamRecruit(iType):
    '''
\t\xc3\xf6\xaa`\xa9\xdb\xb6\xd2/\xa8\xfa\xae\xf8\xc3\xf6\xaa`
\t:param iType: 0-\xa8\xfa\xae\xf8\xc3\xf6\xaa` 1-\xc3\xf6\xaa`
\t:return: None
\t'''
    netobj = GetNetObj(16)
    if netobj:
        netobj.PacketAddI(iType, 1)
        netobj.PacketSend()
    


def C2SSubscribeMemberRecruit(iType, iTargetList, iTime, iNeedClassList):
    '''
\t\xc3\xf6\xaa`\xa6\xdb\xaf\xf2/\xa8\xfa\xae\xf8\xc3\xf6\xaa`
\t:param iType: 0-\xa8\xfa\xae\xf8\xc3\xf6\xaa` 1-\xc3\xf6\xaa`
\t:param iTargetList: \xa5\xf4\xb0\xc8\xa5\xd8\xbc\xd0
\t:param iTime: \xac\xa1\xc5D\xae\xc9\xb6\xa1
\t:param iNeedClassList: \xc2\xbe\xb7~\xadn\xa8D
\t:return: None
\t'''
    netobj = GetNetObj(17)
    if netobj:
        iClassLen = len(iNeedClassList)
        iTargetLen = len(iTargetList)
        netobj.PacketAddI(iType, 1)
        netobj.PacketAddI(iTime, 1)
        netobj.PacketAddI(iClassLen, 1)
        for iClass in iNeedClassList:
            netobj.PacketAddI(iClass, 1)
        
        netobj.PacketAddI(iTargetLen, 1)
        for iTarget in iTargetList:
            netobj.PacketAddI(iTarget, 1)
        
        netobj.PacketSend()
    


def C2SGetSubscribeTeamRecruitState():
    '''
\t\xa7\xf3\xb7s\xa9\xdb\xb6\xd2\xc3\xf6\xaa`\xaa\xac\xbaA
\t'''
    netobj = GetNetObj(18)
    if netobj:
        netobj.PacketSend()
    


def C2SGetSubscribeMemberRecruitState():
    '''
\t\xa7\xf3\xb7s\xa6\xdb\xaf\xf2\xc3\xf6\xaa`\xaa\xac\xbaA
\t'''
    netobj = GetNetObj(19)
    if netobj:
        netobj.PacketSend()
    


def S2CRefreshBtn(netobj):
    bSameGroup = netobj.UnpackInt(1)
    bRequire = netobj.UnpackInt(1)
    bMemberSameGroup = netobj.UnpackInt(1)
    oMgr = mdteamrecruit.GetTeamRecruitMgr()
    oMgr.SetTeamSameGroup(bSameGroup, False)
    oMgr.SetTeamRequire(bRequire, False)
    oMgr.SetMemberSameGroup(bMemberSameGroup, False)


def S2CRefreshTeamList(netobj):
    if teamrecruitinterface.IsOpenNewTeamRecruit():
        S2CRefreshTeamList_New(netobj)
        return None
    
    import avatar
    iLen = netobj.UnpackInt(1)
    dInfoList = []
    for i in xrange(iLen):
        dInfo = { }
        iPlayerID = netobj.UnpackInt(4)
        lAvatar = avatar.UnpackPhotoInt4(netobj)
        iLevel = netobj.UnpackInt(2)
        sLeaderName = netobj.UnpackPS()
        iLen = netobj.UnpackInt(1)
        iClassTypeList = []
        for i in xrange(iLen):
            iType = netobj.UnpackInt(1)
            iClassTypeList.append(iType)
        
        iMinGrade = netobj.UnpackInt(2)
        iMaxGrade = netobj.UnpackInt(2)
        iLen = netobj.UnpackInt(1)
        iNeedClassList = []
        for i in xrange(iLen):
            iNeedClass = netobj.UnpackInt(1)
            iNeedClassList.append(iNeedClass)
        
        iTimeType = netobj.UnpackInt(1)
        iLen = netobj.UnpackInt(1)
        iTargetList = []
        for i in xrange(iLen):
            iTarget = netobj.UnpackInt(1)
            iTargetList.append(iTarget)
        
        sIntro = netobj.UnpackPS()
        iFollowGroup = netobj.UnpackInt(1)
        bSameGroup = netobj.UnpackInt(1)
        bRequire = netobj.UnpackInt(1)
        iStartTime = netobj.UnpackInt(4)
        dInfo['id'] = iPlayerID
        dInfo['avatar'] = lAvatar
        dInfo['level'] = iLevel
        dInfo['name'] = sLeaderName
        dInfo['classlist'] = iClassTypeList
        dInfo['mingrade'] = iMinGrade
        dInfo['needclass'] = iNeedClassList
        dInfo['maxgrade'] = iMaxGrade
        dInfo['time'] = iTimeType
        dInfo['target'] = iTargetList
        dInfo['samegroup'] = bSameGroup
        dInfo['require'] = bRequire
        dInfo['intro'] = sIntro
        dInfo['followgroup'] = iFollowGroup
        dInfo['starttime'] = iStartTime
        dInfoList.append(dInfo)
    
    oMgr = mdteamrecruit.GetTeamRecruitMgr()
    oMgr.SetTeamRecruitList(dInfoList)


def S2CRefreshTeamList_New(netobj):
    import avatar
    iLen = netobj.UnpackInt(1)
    dInfoList = []
    for _ in xrange(iLen):
        iTeamType = netobj.UnpackInt(1)
        iPlayerID = netobj.UnpackInt(4)
        lAvatar = avatar.UnpackPhotoInt4(netobj)
        iLevel = netobj.UnpackInt(2)
        sLeaderName = netobj.UnpackPS()
        iLeaderCls = netobj.UnpackInt(1)
        iOnlineState = netobj.UnpackInt(1)
        iLen = netobj.UnpackInt(1)
        iClsList = [
            iLeaderCls]
        lFriendList = []
        for _ in None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, xrange, iLen):
            iFriendID = netobj.UnpackInt(4)
            iClass = netobj.UnpackInt(1)
            iGrade = netobj.UnpackInt(2)
            sName = netobj.UnpackPS()
            tPhoto = avatar.UnpackPhotoInt4(netobj)
            dFriend = {
                'iPlayerID': iFriendID,
                'sName': sName,
                'iCls': iClass,
                'iGrade': iGrade,
                'tPhoto': tPhoto }
            lFriendList.append(dFriend)
            if iFriendID != iPlayerID:
                iClsList.append(iClass)
                continue
        
        iMinGrade = netobj.UnpackInt(2)
        iMaxGrade = netobj.UnpackInt(2)
        iLen = netobj.UnpackInt(1)
        iNeedClassList = []
        for _ in xrange(iLen):
            iNeedClass = netobj.UnpackInt(1)
            iNeedClassList.append(iNeedClass)
        
        iTimeType = netobj.UnpackInt(1)
        iLen = netobj.UnpackInt(1)
        iTargetList = []
        for _ in xrange(iLen):
            iTarget = netobj.UnpackInt(1)
            iTargetList.append(iTarget)
        
        sInfo = netobj.UnpackPS()
        iFollowGroup = 1
        bSameGroup = netobj.UnpackInt(1)
        bRequire = netobj.UnpackInt(1)
        iStartTime = netobj.UnpackInt(4)
        dInfo = {
            'iTeamType': iTeamType,
            'id': iPlayerID,
            'avatar': lAvatar,
            'level': iLevel,
            'name': sLeaderName,
            'class': iLeaderCls,
            'classlist': iClsList,
            'lFriend': lFriendList,
            'mingrade': iMinGrade,
            'maxgrade': iMaxGrade,
            'time': iTimeType,
            'target': iTargetList,
            'samegroup': bSameGroup,
            'require': bRequire,
            'intro': sInfo,
            'starttime': iStartTime,
            'followgroup': iFollowGroup,
            'needclass': iNeedClassList,
            'iOnlineState': iOnlineState }
        dInfoList.append(dInfo)
    
    oMgr = mdteamrecruit.GetTeamRecruitMgr()
    oMgr.SetTeamRecruitList(dInfoList)


def S2CRefreshMemberList(netobj):
    import avatar
    iLen = netobj.UnpackInt(1)
    dInfoList = []
    for i in xrange(iLen):
        dInfo = { }
        iPlayerID = netobj.UnpackInt(4)
        lAvatar = avatar.UnpackPhotoInt4(netobj)
        iLevel = netobj.UnpackInt(2)
        sName = netobj.UnpackPS()
        iClass = netobj.UnpackInt(1)
        iTime = netobj.UnpackInt(1)
        iLen = netobj.UnpackInt(1)
        iTargetList = []
        for i in xrange(iLen):
            iTarget = netobj.UnpackInt(1)
            iTargetList.append(iTarget)
        
        sIntro = netobj.UnpackPS()
        iFollowGroup = 1
        bSameGroup = netobj.UnpackInt(1)
        iStartTime = netobj.UnpackInt(4)
        iOnlineState = netobj.UnpackInt(1)
        dInfo['id'] = iPlayerID
        dInfo['avatar'] = lAvatar
        dInfo['level'] = iLevel
        dInfo['name'] = sName
        dInfo['class'] = iClass
        dInfo['time'] = iTime
        dInfo['targetlist'] = iTargetList
        dInfo['intro'] = sIntro
        dInfo['samegroup'] = bSameGroup
        dInfo['followgroup'] = iFollowGroup
        dInfo['starttime'] = iStartTime
        dInfo['iOnlineState'] = iOnlineState
        dInfoList.append(dInfo)
    
    oMgr = mdteamrecruit.GetTeamRecruitMgr()
    oMgr.SetMemberRecruitList(dInfoList)


def S2COpenTeamRecruitDetailDlg(netobj):
    '''\xa5\xb4\xb6}\xb6\xa4\xa5\xee\xa9\xdb\xb6\xd2\xabH\xae\xa7\xac\xc9\xad\xb1
\t'''
    import avatar
    iPlayerID = netobj.UnpackInt(4)
    lAvatar = avatar.UnpackPhotoInt4(netobj)
    iLevel = netobj.UnpackInt(2)
    sLeaderName = netobj.UnpackPS()
    iLeaderClass = netobj.UnpackInt(1)
    iLen = netobj.UnpackInt(1)
    iClsList = [
        iLeaderClass]
    lFriendList = []
    for _ in xrange(iLen):
        iFriendID = netobj.UnpackInt(4)
        iClass = netobj.UnpackInt(1)
        iGrade = netobj.UnpackInt(2)
        sName = netobj.UnpackPS()
        tPhoto = avatar.UnpackPhotoInt4(netobj)
        dFriend = {
            'iPlayerID': iFriendID,
            'sName': sName,
            'iCls': iClass,
            'iGrade': iGrade,
            'tPhoto': tPhoto }
        lFriendList.append(dFriend)
        if iFriendID != iPlayerID:
            iClsList.append(iClass)
            continue
    
    iMinGrade = netobj.UnpackInt(2)
    iMaxGrade = netobj.UnpackInt(2)
    iLen = netobj.UnpackInt(1)
    iNeedClassList = []
    for _ in xrange(iLen):
        iNeedClass = netobj.UnpackInt(1)
        iNeedClassList.append(iNeedClass)
    
    iTimeType = netobj.UnpackInt(1)
    iLen = netobj.UnpackInt(1)
    iTargetList = []
    for _ in xrange(iLen):
        iTarget = netobj.UnpackInt(1)
        iTargetList.append(iTarget)
    
    sInfo = netobj.UnpackPS()
    iFollowGroup = 1
    bSameGroup = netobj.UnpackInt(1)
    bRequire = netobj.UnpackInt(1)
    iStartTime = netobj.UnpackInt(4)
    dInfo = {
        'id': iPlayerID,
        'avatar': lAvatar,
        'level': iLevel,
        'name': sLeaderName,
        'class': iLeaderClass,
        'classlist': iClsList,
        'lFriend': lFriendList,
        'mingrade': iMinGrade,
        'maxgrade': iMaxGrade,
        'time': iTimeType,
        'target': iTargetList,
        'samegroup': bSameGroup,
        'require': bRequire,
        'intro': sInfo,
        'starttime': iStartTime,
        'followgroup': iFollowGroup,
        'needclass': iNeedClassList }
    import dlgrecruitdetailteam
    dlgrecruitdetailteam.ShowDlg(iPlayerID, dInfo)


def S2COpenMemberRecruitDlg(netobj):
    '''\xa5\xb4\xb6}\xa6\xdb\xaf\xf2\xa9\xdb\xb6\xd2\xac\xc9\xad\xb1
\t'''
    import avatar
    dInfo = { }
    iPlayerID = netobj.UnpackInt(4)
    lAvatar = avatar.UnpackPhotoInt4(netobj)
    iLevel = netobj.UnpackInt(2)
    sName = netobj.UnpackPS()
    iClass = netobj.UnpackInt(1)
    iTime = netobj.UnpackInt(1)
    iLen = netobj.UnpackInt(1)
    iTargetList = []
    for _ in xrange(iLen):
        iTarget = netobj.UnpackInt(1)
        iTargetList.append(iTarget)
    
    sIntro = netobj.UnpackPS()
    bSameGroup = netobj.UnpackInt(1)
    iStartTime = netobj.UnpackInt(4)
    dInfo['id'] = iPlayerID
    dInfo['avatar'] = lAvatar
    dInfo['level'] = iLevel
    dInfo['name'] = sName
    dInfo['class'] = iClass
    dInfo['time'] = iTime
    dInfo['targetlist'] = iTargetList
    dInfo['intro'] = sIntro
    dInfo['samegroup'] = bSameGroup
    dInfo['starttime'] = iStartTime
    import dlgrecruitdetailmember
    dlgrecruitdetailmember.ShowDlg(iPlayerID, dInfo)


def S2COpenRecruitMain(oNetObj):
    import dlgteamrecruit
    dlgteamrecruit.OpenRecruitMainDlg()


def S2CSubRecruitState(oNetObj):
    '''
\t\xa8\xea\xb7s\xa9\xdb\xb6\xd2\xc3\xf6\xaa`\xaa\xac\xbaA
\t'''
    import mdteamrecruit
    iState = oNetObj.UnpackInt(1)
    oMgr = mdteamrecruit.GetTeamRecruitMgr()
    oMgr.SetSubscribeTeamRecruitState(iState)


def S2CSubRecommendState(oNetObj):
    '''
\t\xa8\xea\xb7s\xa6\xdb\xaf\xf2\xc3\xf6\xaa`\xaa\xac\xbaA
\t'''
    import mdteamrecruit
    iState = oNetObj.UnpackInt(1)
    oMgr = mdteamrecruit.GetTeamRecruitMgr()
    oMgr.SetSubscribeMemberRecruitState(iState)

SUB_FUNC = {
    1: S2CRefreshBtn,
    2: S2CRefreshTeamList,
    3: S2CRefreshMemberList,
    5: S2COpenTeamRecruitDetailDlg,
    6: S2COpenMemberRecruitDlg }

def S2CProcess(netobj):
    iSub = netobj.UnpackInt(1)
    oSubFunc = SUB_FUNC.get(iSub)
    if not oSubFunc:
        return None
    
    import protocolprint
    protocolprint.AppendS2CSubInfo('netteamrecruit', oSubFunc.__name__)
    oSubFunc(netobj)

SUB_FUNC_RECRUIT = {
    1: S2CRefreshBtn,
    2: S2CRefreshTeamList_New,
    3: S2COpenTeamRecruitDetailDlg,
    4: S2CRefreshMemberList,
    5: S2COpenMemberRecruitDlg,
    6: S2COpenRecruitMain,
    7: S2CSubRecruitState,
    8: S2CSubRecommendState }

def S2CTeamRecruit(netobj):
    iSub = netobj.UnpackInt(1)
    oSubFunc = SUB_FUNC_RECRUIT.get(iSub)
    if not oSubFunc:
        return None
    
    import protocolprint
    protocolprint.AppendS2CSubInfo('netteamrecruit', oSubFunc.__name__)
    oSubFunc(netobj)
