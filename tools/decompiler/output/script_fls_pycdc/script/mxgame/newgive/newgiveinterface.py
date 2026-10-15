# pycdc 交叉复核产物 · script.fls entry 3473
# co_filename(原始)='script/mxgame/newgive/newgiveinterface.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3473.pyc (Python 2.5)

import emsdefine
import givedefine
import permission

def OpenNewGiveDlg(iPage = givedefine.PAGE_GIVEITEM):
    import netopenui
    netopenui.C2SAskCanOpenNewGiveDlg(iPage)


def S2COpenNewGiveDlg(iPage):
    import dlgnewgivemain
    import mdmvpnormal
    import friend
    import usermacro
    import dialoguecommondata
    dlgnewgivemain.CNewGiveDlg.OpenUI(iPage)
    iSelectID = mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEW_GIVE).GetMdData('m_iSelectID', 0)
    if iSelectID and not friend.IsFriend(iSelectID):
        sMsg = dialoguecommondata.GetDialogue('newgive', 1050)
        usermacro.MOVE_MSG(-1, 0, sMsg)
        usermacro.NORMAL_MSG(sMsg)
    


def IsGiveMsg(sMsg):
    import wrapchatbg
    import re
    pat = re.compile(wrapchatbg.INT_TYPE_2_WRAP_TEXT[wrapchatbg.CHATITEM_PRESENT_GET])
    return pat.search(sMsg) is not None


def CheckInShowServer():
    '''
\t\xa4\xa3\xa5i\xa6b\xabD\xa4\xd1\xbf\xef\xaa\xba\xb4\xb6\xb3q\xb8\xf3\xaaA\xc5\xe3\xa5\xdc,True\xb2\xc5\xa6X\xc5\xe3\xa5\xdc\xb1\xf8\xa5\xf3
\t:return:
\t'''
    import misc
    bKuaFu = misc.IsInKuafuServer()
    if bKuaFu:
        return misc.IsTianXuanServer()
    
    return True


def AddSendSuccessChat(iPlayer, iSendTime, sName, dItemLst):
    import dlgtalk
    import wrapchatbg
    import itemdata
    import history_encryptnew
    import interface
    oTalk = dlgtalk.GetTalkDlg(iPlayer)
    sMsg = '\xb1z\xa6V#G%s#n\xc3\xd8\xb0e\xa4F' % sName
    for idx, dItem in enumerate(dItemLst):
        sMsg += '#G%s*%d' % (itemdata.GetData(dItem['iShape'])[0], dItem['iAmount'])
        if idx + 1 < len(dItemLst):
            sMsg += '\xa1B'
            continue
    
    if oTalk:
        oTalk.AddChat('', sMsg, pid = iPlayer, iChatType = wrapchatbg.CHATITEM_OTHER)
    else:
        history_encryptnew.CAdapter.WriteHistoryByID(iPlayer, GetRealMsgByType(sMsg, wrapchatbg.CHATITEM_OTHER, sName))


def GetRealMsgByType(sMsg, iChatType, sName):
    import wrapchatbg
    import misc
    realMsg = wrapchatbg.ConvertChatText(iChatType, sMsg)
    hisStr = '#Y%s  ' % sName + '#c00c000%d-%02d-%02d %02d:%02d:%02d#n#r' % misc.LocalTime()[:6] + realMsg
    return hisStr


def GetHavePresentSum(iPlayer):
    import mdmxnewems
    iSum = 0
    for iEmsID, iSendID in mdmxnewems.GetMxNewEmsMgr().GetAllEmsInfo().iteritems():
        oEms = None
        if iPlayer == iSendID and oEms and oEms.GetProp(oEms.KEY_SHOW_TYPE) == 2 and oEms.GetProp(oEms.KEY_GET_ACCESSORY_MARK) == emsdefine.KEY_GET_ACCESSORY_MARK_NOT_GET:
            iSum += 1
            continue
    
    return None if iSum < 50 else 50


def GetAllUnGetSum():
    import mdmxnewems
    iSum = 0
    for tEms, oEms in mdmxnewems.GetMxNewEmsMgr().GetAllEmsInfo().iteritems():
        if oEms and oEms.GetProp(oEms.KEY_SHOW_TYPE) == emsdefine.EMS_SHOWTYPE_GIVE and oEms.GetProp(oEms.KEY_GET_ACCESSORY_MARK) == emsdefine.KEY_GET_ACCESSORY_MARK_NOT_GET:
            iSum += 1
            continue
    
    return iSum


def SetDefaultSelect(iPlayer):
    import mdmvpnormal
    mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEW_GIVE).SetMdData('m_iTopID', iPlayer)
    mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEW_GIVE).SetMdData('m_iSelectID', iPlayer)
    
    try:
        pass
    except:
        None(None, mdmvpnormal.GetNormalMdMgr)
        return None



def SetGivePlayer(iPlayer, sName):
    import friend
    import mdmvpnormal
    if not friend.IsFriend(iPlayer, 0):
        mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEW_GIVE).SetMdData('m_dPlayer', {
            'iPlayerID': iPlayer,
            'sName': sName })
    
    mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEW_GIVE).SetMdData('m_iTopID', iPlayer)
    mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_NEW_GIVE).SetMdData('m_iSelectID', iPlayer)


def GetGiveTips():
    return givedefine.GIVE_NEWTIPS + '#r\xa5k\xc1\xe4\xa8\xfa\xae\xf8\xbe\xde\xa7@'


def CheckIsTimeOut(sChat):
    return True


def SetFriendBtnNotify():
    import mdmxnewems
    import friend
    import mainmenu
    import dlgtalk
    import commoncb
    oMxNewEmsMgr = mdmxnewems.GetMxNewEmsMgr()
    dInfo = oMxNewEmsMgr.GetFirstHaveGiveEms().items()
    oMgr = friend.GetControl()
    for iPlayerID, bHave in dInfo:
        if bHave:
            oMgr.AddFriendNotifyEx(iPlayerID, not dlgtalk.GetTalkDlg(iPlayerID), 0)
        
        if dlgtalk.GetTalkDlg(iPlayerID):
            oMxNewEmsMgr.SetFirstHaveGiveEms(iPlayerID, False)
            continue
    
    if dInfo:
        mainmenu.RefreshPlayerNotify()
        commoncb.TriggerCB(commoncb.FRIEND_UNREAD_MSG)
    


def UpdatePlayerNotify(tDelList):
    import friend
    import commoncb
    oMgr = friend.GetControl()
    for iEmsID, iSendID in tDelList:
        oMgr.AddFriendNotify(iSendID, False, 0)
    
    commoncb.TriggerCB(commoncb.FRIEND_UNREAD_MSG)


def GetExtTipsByShape(iShape):
    return givedefine.SHAPE2EXT.get(iShape, '')
