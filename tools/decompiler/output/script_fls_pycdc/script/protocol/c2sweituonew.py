# pycdc 交叉复核产物 · script.fls entry 2785
# co_filename(原始)='script/protocol/c2sweituonew.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2785.pyc (Python 2.5)

import net
import protocolcount
import nettimewheeldelegate
import avatar
import netpublic

def GS2CWeituoInfo(oNetObj):
    lstWeituo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iType = oNetObj.UnpackInt(1)
        iState = oNetObj.UnpackInt(1)
        iDur = oNetObj.UnpackInt(4)
        iPublisher = oNetObj.UnpackInt(4)
        sPublisherName = oNetObj.UnpackPS(1)
        iPlayerID = oNetObj.UnpackInt(4)
        sActerName = oNetObj.UnpackPS(1)
        iRelation = oNetObj.UnpackInt(1)
        iDay = oNetObj.UnpackInt(1)
        iProcess = oNetObj.UnpackInt(1)
        iMaxProcess = oNetObj.UnpackInt(1)
        iPublishTime = oNetObj.UnpackInt(1)
        iStartTime = oNetObj.UnpackInt(4)
        iKeepTime = oNetObj.UnpackInt(4)
        iComCnt = oNetObj.UnpackInt(1)
        iDone = oNetObj.UnpackInt(1)
        iServerTaskCount = oNetObj.UnpackInt(1)
        iPlayerDoneCnt = oNetObj.UnpackInt(1)
        iSysDoneCnt = oNetObj.UnpackInt(1)
        iTodayDone = oNetObj.UnpackInt(1)
        iVaildTime = oNetObj.UnpackInt(1)
        iCurTime = oNetObj.UnpackInt(1)
        lstPhoto = avatar.UnpackPhotoInt4(oNetObj)
        dFrm = avatar.UnpackAvatarFrm(iPlayerID)(oNetObj)
        iHaveMonthCard = oNetObj.UnpackInt(1)
        iFreeTimes = oNetObj.UnpackInt(1)
        iMmonthCardCurTime = oNetObj.UnpackInt(1)
        iSpeedTimes = oNetObj.UnpackInt(1)
        lstWeituo.append([
            iType,
            iState,
            iDur,
            iPublisher,
            sPublisherName,
            iPlayerID,
            sActerName,
            iRelation,
            iDay,
            iProcess,
            iMaxProcess,
            iPublishTime,
            iStartTime,
            iKeepTime,
            iComCnt,
            iDone,
            iServerTaskCount,
            iPlayerDoneCnt,
            iSysDoneCnt,
            iTodayDone,
            iVaildTime,
            iCurTime,
            lstPhoto,
            dFrm,
            iHaveMonthCard,
            iFreeTimes,
            iMmonthCardCurTime,
            iSpeedTimes])
    
    iAllDur = oNetObj.UnpackInt(4)
    iOrderGroup = oNetObj.UnpackInt(1)
    iOrderHYX = oNetObj.UnpackInt(1)
    lstQuick = []
    for _index2 in xrange(oNetObj.UnpackInt(1)):
        iQuickZhiye = oNetObj.UnpackInt(1)
        iQuickZhiyeType = oNetObj.UnpackInt(1)
        iQuickXiulian = oNetObj.UnpackInt(1)
        lstQuick.append([
            iQuickZhiye,
            iQuickZhiyeType,
            iQuickXiulian])
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=1', 'GS2CWeituoInfo(lstWeituo=%s,iAllDur=%s,iOrderGroup=%s,iOrderHYX=%s,lstQuick=%s)' % (lstWeituo, iAllDur, iOrderGroup, iOrderHYX, lstQuick))
    nettimewheeldelegate.OnWeituoInfo(lstWeituo, iAllDur, iOrderGroup, iOrderHYX, lstQuick)


def GS2CPublishInfo(oNetObj):
    iMode = oNetObj.UnpackInt(1)
    lstFrd = []
    for _index in xrange(oNetObj.UnpackInt(2)):
        iPlayerID = oNetObj.UnpackInt(4)
        sName = oNetObj.UnpackPS(1)
        lstPhoto = avatar.UnpackPhotoInt4(oNetObj)
        dFrm = avatar.UnpackAvatarFrm(iPlayerID)(oNetObj)
        lstFrd.append([
            iPlayerID,
            sName,
            lstPhoto,
            dFrm])
    
    lstBatchWeituoInfo = []
    for _index2 in xrange(oNetObj.UnpackInt(1)):
        iType = oNetObj.UnpackInt(1)
        iDay = oNetObj.UnpackInt(1)
        iTime = oNetObj.UnpackInt(4)
        lstBatchWeituoInfo.append([
            iType,
            iDay,
            iTime])
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=2', 'GS2CPublishInfo(iMode=%s,lstFrd=%s,lstBatchWeituoInfo=%s)' % (iMode, lstFrd, lstBatchWeituoInfo))
    nettimewheeldelegate.OnPublishInfo(iMode, lstFrd, lstBatchWeituoInfo)


def GS2CPublishRes(oNetObj):
    iType = oNetObj.UnpackInt(1)
    iRes = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=3', 'GS2CPublishRes(iType=%s,iRes=%s)' % (iType, iRes))
    nettimewheeldelegate.OnPublishRes(iType, iRes)


def GS2CPickInfo(oNetObj):
    lstType = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iType = oNetObj.UnpackInt(1)
        iState = oNetObj.UnpackInt(1)
        iCnt = oNetObj.UnpackInt(1)
        lstWeituo = []
        for _index2 in xrange(oNetObj.UnpackInt(4)):
            iCash = oNetObj.UnpackInt(4)
            iPlayerID = oNetObj.UnpackInt(4)
            sPublisher = oNetObj.UnpackPS(1)
            iCon = oNetObj.UnpackInt(4)
            lstPhoto = avatar.UnpackPhotoInt4(oNetObj)
            dFrm = avatar.UnpackAvatarFrm(iPlayerID)(oNetObj)
            None([
                (None, None, None, None, None, None, None, lstWeituo.append),
                iPlayerID,
                sPublisher,
                iCon,
                lstPhoto,
                dFrm])
        
        lstType.append([
            iType,
            iState,
            iCnt,
            lstWeituo])
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=4', 'GS2CPickInfo(lstType=%s)' % lstType)
    nettimewheeldelegate.OnPickInfo(lstType)


def GS2COpenClauseDlg(oNetObj):
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=5', 'GS2COpenClauseDlg()')
    nettimewheeldelegate.OnOpenClauseDlg()


def GS2CUpdateEntrustType(oNetObj):
    iType = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=6', 'GS2CUpdateEntrustType(iType=%s)' % iType)
    nettimewheeldelegate.OnUpdateEntrustType(iType)


def GS2CCloseWeituoUI(oNetObj):
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=7', 'GS2CCloseWeituoUI()')
    nettimewheeldelegate.OnCloseWeituoUI()


def GS2COneWeituoInfo(oNetObj):
    lstWeituo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iType = oNetObj.UnpackInt(1)
        iState = oNetObj.UnpackInt(1)
        iDur = oNetObj.UnpackInt(4)
        iPublisher = oNetObj.UnpackInt(4)
        sPublisherName = oNetObj.UnpackPS(1)
        iPlayerID = oNetObj.UnpackInt(4)
        sActerName = oNetObj.UnpackPS(1)
        iRelation = oNetObj.UnpackInt(1)
        iDay = oNetObj.UnpackInt(1)
        iProcess = oNetObj.UnpackInt(1)
        iMaxProcess = oNetObj.UnpackInt(1)
        iPublishTime = oNetObj.UnpackInt(1)
        iStartTime = oNetObj.UnpackInt(4)
        iKeepTime = oNetObj.UnpackInt(4)
        iComCnt = oNetObj.UnpackInt(1)
        iDone = oNetObj.UnpackInt(1)
        iServerTaskCount = oNetObj.UnpackInt(1)
        iPlayerDoneCnt = oNetObj.UnpackInt(1)
        iSysDoneCnt = oNetObj.UnpackInt(1)
        iTodayDone = oNetObj.UnpackInt(1)
        iVaildTime = oNetObj.UnpackInt(1)
        iCurTime = oNetObj.UnpackInt(1)
        lstPhoto = avatar.UnpackPhotoInt4(oNetObj)
        dFrm = avatar.UnpackAvatarFrm(iPlayerID)(oNetObj)
        iHaveMonthCard = oNetObj.UnpackInt(1)
        iFreeTimes = oNetObj.UnpackInt(1)
        iMmonthCardCurTime = oNetObj.UnpackInt(1)
        iSpeedTimes = oNetObj.UnpackInt(1)
        lstWeituo.append([
            iType,
            iState,
            iDur,
            iPublisher,
            sPublisherName,
            iPlayerID,
            sActerName,
            iRelation,
            iDay,
            iProcess,
            iMaxProcess,
            iPublishTime,
            iStartTime,
            iKeepTime,
            iComCnt,
            iDone,
            iServerTaskCount,
            iPlayerDoneCnt,
            iSysDoneCnt,
            iTodayDone,
            iVaildTime,
            iCurTime,
            lstPhoto,
            dFrm,
            iHaveMonthCard,
            iFreeTimes,
            iMmonthCardCurTime,
            iSpeedTimes])
    
    iAllDur = oNetObj.UnpackInt(4)
    iOrderGroup = oNetObj.UnpackInt(1)
    iOrderHYX = oNetObj.UnpackInt(1)
    lstQuick = []
    for _index2 in xrange(oNetObj.UnpackInt(1)):
        iQuickZhiye = oNetObj.UnpackInt(1)
        iQuickZhiyeType = oNetObj.UnpackInt(1)
        iQuickXiulian = oNetObj.UnpackInt(1)
        lstQuick.append([
            iQuickZhiye,
            iQuickZhiyeType,
            iQuickXiulian])
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=8', 'GS2COneWeituoInfo(lstWeituo=%s,iAllDur=%s,iOrderGroup=%s,iOrderHYX=%s,lstQuick=%s)' % (lstWeituo, iAllDur, iOrderGroup, iOrderHYX, lstQuick))
    nettimewheeldelegate.OnOneWeituoInfo(lstWeituo, iAllDur, iOrderGroup, iOrderHYX, lstQuick)


def GS2CPickWeituoInfo(oNetObj):
    iType = oNetObj.UnpackInt(1)
    iProcess = oNetObj.UnpackInt(1)
    iMaxProcess = oNetObj.UnpackInt(1)
    iEndTime = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=9', 'GS2CPickWeituoInfo(iType=%s,iProcess=%s,iMaxProcess=%s,iEndTime=%s)' % (iType, iProcess, iMaxProcess, iEndTime))
    nettimewheeldelegate.OnPickWeituoInfo(iType, iProcess, iMaxProcess, iEndTime)


def GS2COpenWeituo(oNetObj):
    iType = oNetObj.UnpackInt(1)
    iPageParam = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=10', 'GS2COpenWeituo(iType=%s,iPageParam=%s)' % (iType, iPageParam))
    nettimewheeldelegate.OnOpenWeituo(iType, iPageParam)


def GS2CRefreshLinkWeituoState(oNetObj):
    iPubID = oNetObj.UnpackInt(4)
    lTypeInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iPubType = oNetObj.UnpackInt(1)
        iTime = oNetObj.UnpackInt(4)
        iState = oNetObj.UnpackInt(1)
        sActerName = oNetObj.UnpackPS(1)
        lTypeInfo.append([
            iPubType,
            iTime,
            iState,
            sActerName])
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=11', 'GS2CRefreshLinkWeituoState(iPubID=%s,lTypeInfo=%s)' % (iPubID, lTypeInfo))
    nettimewheeldelegate.OnRefreshLinkWeituoState(iPubID, lTypeInfo)


def GS2CEntrustData(oNetObj):
    iType = oNetObj.UnpackInt(1)
    lstEntrustData = None
    if iType == 2:
        lstEntrustData = []
        for _index in xrange(oNetObj.UnpackInt(2)):
            iPlayerId = oNetObj.UnpackInt(4)
            sPlayerName = oNetObj.UnpackPS(1)
            iZhiye = oNetObj.UnpackInt(1)
            iXiulian = oNetObj.UnpackInt(1)
            iTiaoWu = oNetObj.UnpackInt(1)
            iYunBiao = oNetObj.UnpackInt(1)
            iTaskLink = oNetObj.UnpackInt(1)
            iWaBao = oNetObj.UnpackInt(1)
            iTuJian = oNetObj.UnpackInt(1)
            iMxKeTang = oNetObj.UnpackInt(1)
            lstEntrustData.append([
                iPlayerId,
                sPlayerName,
                iZhiye,
                iXiulian,
                iTiaoWu,
                iYunBiao,
                iTaskLink,
                iWaBao,
                iTuJian,
                iMxKeTang])
        
    elif iType == 3:
        lstEntrustData = []
        for _index2 in xrange(oNetObj.UnpackInt(2)):
            iTimeTag = oNetObj.UnpackInt(4)
            iPlayerId = oNetObj.UnpackInt(4)
            sPlayerName = oNetObj.UnpackPS(1)
            iTaskType = oNetObj.UnpackInt(1)
            lstEntrustData.append([
                iTimeTag,
                iPlayerId,
                sPlayerName,
                iTaskType])
        
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=12', 'GS2CEntrustData(iType=%s,lstEntrustData=%s)' % (iType, lstEntrustData))
    nettimewheeldelegate.OnEntrustData(iType, lstEntrustData)


def GS2CEntrustChange(oNetObj):
    iModel = oNetObj.UnpackInt(1)
    iTask = oNetObj.UnpackInt(1)
    lstOrderPid = []
    for _index in xrange(oNetObj.UnpackInt(2)):
        iPid = oNetObj.UnpackInt(4)
        lstOrderPid.append(iPid)
    
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=13', 'GS2CEntrustChange(iModel=%s,iTask=%s,lstOrderPid=%s)' % (iModel, iTask, lstOrderPid))
    nettimewheeldelegate.OnEntrustChange(iModel, iTask, lstOrderPid)


def GS2CGetRewardSucceed(oNetObj):
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=14', 'GS2CGetRewardSucceed()')
    nettimewheeldelegate.OnGetRewardSucceed()


def GS2COpenQuickGetReward(oNetObj):
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=15', 'GS2COpenQuickGetReward()')
    nettimewheeldelegate.OnOpenQuickGetReward()


def GS2CSetNewTaskInformState(oNetObj):
    iState = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=16', 'GS2CSetNewTaskInformState(iState=%s)' % iState)
    nettimewheeldelegate.OnSetNewTaskInformState(iState)


def GS2CSetOrgEntrustLinkState(oNetObj):
    iState = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_ENTRUST=0xed,iSub=17', 'GS2CSetOrgEntrustLinkState(iState=%s)' % iState)
    nettimewheeldelegate.OnSetOrgEntrustLinkState(iState)

g_NetFunction = {
    1: GS2CWeituoInfo,
    2: GS2CPublishInfo,
    3: GS2CPublishRes,
    4: GS2CPickInfo,
    5: GS2COpenClauseDlg,
    6: GS2CUpdateEntrustType,
    7: GS2CCloseWeituoUI,
    8: GS2COneWeituoInfo,
    9: GS2CPickWeituoInfo,
    10: GS2COpenWeituo,
    11: GS2CRefreshLinkWeituoState,
    12: GS2CEntrustData,
    13: GS2CEntrustChange,
    14: GS2CGetRewardSucceed,
    15: GS2COpenQuickGetReward,
    16: GS2CSetNewTaskInformState,
    17: GS2CSetOrgEntrustLinkState }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_ENTRUST', '\xb5L\xaak\xb8\xd1\xaaR GS2C_ENTRUST=0xed \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSOpenWeituo():
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(1, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=1', 'C2GSOpenWeituo()')


def C2GSDrawReward(iType):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(2, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=2', 'C2GSDrawReward(iType=%s)' % iType)


def C2GSOpenPublish(iType, iModel):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(3, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iModel, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=3', 'C2GSOpenPublish(iType=%s,iModel=%s)' % (iType, iModel))


def C2GSPublish(lstWeituo, lstTarget):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(4, 1)
    oNetObj.PacketAddI(len(lstWeituo), 2)
    for iType, iDay, iTime in lstWeituo:
        oNetObj.PacketAddI(iType, 1)
        oNetObj.PacketAddI(iDay, 1)
        oNetObj.PacketAddI(iTime, 4)
    
    oNetObj.PacketAddI(len(lstTarget), 2)
    for iTarget in lstTarget:
        oNetObj.PacketAddI(iTarget, 4)
    
    netpublic.SplitPacketSend(oNetObj, net.C2GS_ENTRUST)
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=4', 'C2GSPublish(lstWeituo=%s,lstTarget=%s)' % (lstWeituo, lstTarget))


def C2GSOpenPick():
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(5, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=5', 'C2GSOpenPick()')


def C2GSPick(iTargetID, iType):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(6, 1)
    oNetObj.PacketAddI(iTargetID, 4)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=6', 'C2GSPick(iTargetID=%s,iType=%s)' % (iTargetID, iType))


def C2GSGoToWeituo():
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(7, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=7', 'C2GSGoToWeituo()')


def C2GSCancelWeituo(iType):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(8, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=8', 'C2GSCancelWeituo(iType=%s)' % iType)


def C2GSConfirmClause(iType):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(9, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=9', 'C2GSConfirmClause(iType=%s)' % iType)


def C2GSAskEntrustSelect():
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(10, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=10', 'C2GSAskEntrustSelect()')


def C2GSSetEntrustSelect(iType):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(11, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=11', 'C2GSSetEntrustSelect(iType=%s)' % iType)


def C2GSRequestLinkWeituoState(iPubID, iTypeLst):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(12, 1)
    oNetObj.PacketAddI(iPubID, 4)
    oNetObj.PacketAddI(len(iTypeLst), 1)
    for iType in iTypeLst:
        oNetObj.PacketAddI(iType, 1)
    
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=12', 'C2GSRequestLinkWeituoState(iPubID=%s,iTypeLst=%s)' % (iPubID, iTypeLst))


def C2GSRequestEntrustData(iType):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(13, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=13', 'C2GSRequestEntrustData(iType=%s)' % iType)


def C2GSShowEntrustConsume(iTaskTag):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(14, 1)
    oNetObj.PacketAddI(iTaskTag, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=14', 'C2GSShowEntrustConsume(iTaskTag=%s)' % iTaskTag)


def C2GSChangeEntrust(iType, iModel):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(15, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iModel, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=15', 'C2GSChangeEntrust(iType=%s,iModel=%s)' % (iType, iModel))


def C2GSQuickGetReward():
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(16, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=16', 'C2GSQuickGetReward()')


def C2GSRequestNewTaskInformState():
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(17, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=17', 'C2GSRequestNewTaskInformState()')


def C2GSChangeNewTaskInformState(iState):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(18, 1)
    oNetObj.PacketAddI(iState, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=18', 'C2GSChangeNewTaskInformState(iState=%s)' % iState)


def C2GSChangeQuickAcceptState(iType, iState):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(19, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iState, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=19', 'C2GSChangeQuickAcceptState(iType=%s,iState=%s)' % (iType, iState))


def C2GSChangeZhiyeRewardType(iGrade):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_ENTRUST)
    oNetObj.PacketAddI(20, 1)
    oNetObj.PacketAddI(iGrade, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_ENTRUST=0xec,iSub=20', 'C2GSChangeZhiyeRewardType(iGrade=%s)' % iGrade)
