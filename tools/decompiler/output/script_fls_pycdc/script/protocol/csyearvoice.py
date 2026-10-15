# pycdc 交叉复核产物 · script.fls entry 2454
# co_filename(原始)='script/protocol/csyearvoice.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2454.pyc (Python 2.5)

import huodongdefine
import net
import netpublic
import protocolcount
import netannualdreamvoice

def GS2CPersonalInfo(oNetObj):
    iStage = oNetObj.UnpackInt(1)
    iNo = oNetObj.UnpackInt(4)
    iFamer = oNetObj.UnpackInt(4)
    iVote = oNetObj.UnpackInt(2)
    lInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sSong = oNetObj.UnpackPS(1)
        sUrl = oNetObj.UnpackPS(1)
        iDur = oNetObj.UnpackInt(2)
        sPicUrl = oNetObj.UnpackPS(2)
        iCanChange = oNetObj.UnpackInt(1)
        iState = oNetObj.UnpackInt(1)
        iFame = oNetObj.UnpackInt(4)
        iTopTime = oNetObj.UnpackInt(4)
        lInfo.append([
            sSong,
            sUrl,
            iDur,
            sPicUrl,
            iCanChange,
            iState,
            iFame,
            iTopTime])
    
    protocolcount.ProtocolLog('GS2C=0,iSub=1', 'GS2CPersonalInfo(iStage=%s,iNo=%s,iFamer=%s,iVote=%s,lInfo=%s)' % (iStage, iNo, iFamer, iVote, lInfo))
    netannualdreamvoice.OnPersonalInfo(iStage, iNo, iFamer, iVote, lInfo)


def GS2CFameRecord(oNetObj):
    lRecord = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iNo = oNetObj.UnpackInt(2)
        sName = oNetObj.UnpackPS(1)
        iCnt = oNetObj.UnpackInt(1)
        iType = oNetObj.UnpackInt(1)
        lRecord.append([
            iNo,
            sName,
            iCnt,
            iType])
    
    protocolcount.ProtocolLog('GS2C=0,iSub=2', 'GS2CFameRecord(lRecord=%s)' % lRecord)
    netannualdreamvoice.OnFameRecord(lRecord)


def GS2COpenSendFlower(oNetObj):
    iPID = oNetObj.UnpackInt(4)
    iNum = oNetObj.UnpackInt(4)
    sUrl = oNetObj.UnpackPS(1)
    iServer = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C=0,iSub=3', 'GS2COpenSendFlower(iPID=%s,iNum=%s,sUrl=%s,iServer=%s)' % (iPID, iNum, sUrl, iServer))
    netannualdreamvoice.OnOpenSendFlower(iPID, iNum, sUrl, iServer)


def GS2COpenRegisterUI(oNetObj):
    iStage = oNetObj.UnpackInt(1)
    iIsApprove = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C=0,iSub=4', 'GS2COpenRegisterUI(iStage=%s,iIsApprove=%s)' % (iStage, iIsApprove))
    netannualdreamvoice.OnOpenRegisterUI(iStage, iIsApprove)


def GS2COtherPersonInfo(oNetObj):
    iPID = oNetObj.UnpackInt(4)
    iPShowID = oNetObj.UnpackInt(4)
    iPrettyID = oNetObj.UnpackInt(4)
    iServer = oNetObj.UnpackInt(4)
    iNo = oNetObj.UnpackInt(4)
    sName = oNetObj.UnpackPS(1)
    sOrgName = oNetObj.UnpackPS(1)
    iFame = oNetObj.UnpackInt(4)
    iSex = oNetObj.UnpackInt(1)
    iVote = oNetObj.UnpackInt(2)
    iShape = oNetObj.UnpackInt(2)
    iPhoto1 = oNetObj.UnpackInt(4)
    iPhoto2 = oNetObj.UnpackInt(4)
    iPhoto3 = oNetObj.UnpackInt(4)
    iPhoto4 = oNetObj.UnpackInt(4)
    iIsAttention = oNetObj.UnpackInt(1)
    lInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sSong = oNetObj.UnpackPS(1)
        sUrl = oNetObj.UnpackPS(1)
        iDur = oNetObj.UnpackInt(2)
        sPicUrl = oNetObj.UnpackPS(2)
        iVoiceFame = oNetObj.UnpackInt(4)
        iTopTime = oNetObj.UnpackInt(4)
        lInfo.append([
            sSong,
            sUrl,
            iDur,
            sPicUrl,
            iVoiceFame,
            iTopTime])
    
    protocolcount.ProtocolLog('GS2C=0,iSub=5', 'GS2COtherPersonInfo(iPID=%s,iPShowID=%s,iPrettyID=%s,iServer=%s,iNo=%s,sName=%s,sOrgName=%s,iFame=%s,iSex=%s,iVote=%s,iShape=%s,iPhoto1=%s,iPhoto2=%s,iPhoto3=%s,iPhoto4=%s,iIsAttention=%s,lInfo=%s)' % (iPID, iPShowID, iPrettyID, iServer, iNo, sName, sOrgName, iFame, iSex, iVote, iShape, iPhoto1, iPhoto2, iPhoto3, iPhoto4, iIsAttention, lInfo))
    for None in iServer:
        return None


def GS2CAllSingerInfo(oNetObj):
    iStage = oNetObj.UnpackInt(1)
    iIsApprove = oNetObj.UnpackInt(1)
    lInfo = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iPID = oNetObj.UnpackInt(4)
        iNo = oNetObj.UnpackInt(4)
        sName = oNetObj.UnpackPS(1)
        iServer = oNetObj.UnpackInt(4)
        sOrgName = oNetObj.UnpackPS(1)
        iSex = oNetObj.UnpackInt(1)
        iShape = oNetObj.UnpackInt(2)
        iPhoto1 = oNetObj.UnpackInt(4)
        iPhoto2 = oNetObj.UnpackInt(4)
        iPhoto3 = oNetObj.UnpackInt(4)
        iPhoto4 = oNetObj.UnpackInt(4)
        lVoice = []
        for _index2 in xrange(oNetObj.UnpackInt(1)):
            sSong = oNetObj.UnpackPS(1)
            sUrl = oNetObj.UnpackPS(1)
            iDur = oNetObj.UnpackInt(2)
            sPicUrl = oNetObj.UnpackPS(2)
            iFame = oNetObj.UnpackInt(4)
            iIsTop = oNetObj.UnpackInt(1)
            lVoice.append([
                sSong,
                sUrl,
                iDur,
                sPicUrl,
                iFame,
                iIsTop])
        
        lInfo.append([
            iPID,
            iNo,
            sName,
            iServer,
            sOrgName,
            iSex,
            iShape,
            iPhoto1,
            iPhoto2,
            iPhoto3,
            iPhoto4,
            lVoice])
    
    protocolcount.ProtocolLog('GS2C=0,iSub=6', 'GS2CAllSingerInfo(iStage=%s,iIsApprove=%s,lInfo=%s)' % (iStage, iIsApprove, lInfo))
    netannualdreamvoice.OnAllSingerInfo(iStage, iIsApprove, lInfo)


def GS2CAllSingerIDList(oNetObj):
    iStage = oNetObj.UnpackInt(1)
    iVote = oNetObj.UnpackInt(2)
    lPid = []
    for _index in xrange(oNetObj.UnpackInt(2)):
        iPid = oNetObj.UnpackInt(4)
        iNo = oNetObj.UnpackInt(4)
        iServer = oNetObj.UnpackInt(4)
        sOrgName = oNetObj.UnpackPS(1)
        lVoice = []
        for _index2 in xrange(oNetObj.UnpackInt(1)):
            sUrl = oNetObj.UnpackPS(1)
            iIsTop = oNetObj.UnpackInt(1)
            lVoice.append([
                sUrl,
                iIsTop])
        
        lPid.append([
            iPid,
            iNo,
            iServer,
            sOrgName,
            lVoice])
    
    lAttention = []
    for _index3 in xrange(oNetObj.UnpackInt(1)):
        iPid = oNetObj.UnpackInt(4)
        iServer = oNetObj.UnpackInt(4)
        lVoice = []
        for _index4 in xrange(oNetObj.UnpackInt(1)):
            sUrl = oNetObj.UnpackPS(1)
            iFame = oNetObj.UnpackInt(4)
            lVoice.append([
                sUrl,
                iFame])
        
        lAttention.append([
            iPid,
            iServer,
            lVoice])
    
    iTarget = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C=0,iSub=7', 'GS2CAllSingerIDList(iStage=%s,iVote=%s,lPid=%s,lAttention=%s,iTarget=%s)' % (iStage, iVote, lPid, lAttention, iTarget))
    netannualdreamvoice.OnAllSingerIDList(iStage, iVote, lPid, lAttention, iTarget)


def GS2CRefreshTopInfo(oNetObj):
    sUrl = oNetObj.UnpackPS(1)
    iTopTime = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C=0,iSub=8', 'GS2CRefreshTopInfo(sUrl=%s,iTopTime=%s)' % (sUrl, iTopTime))
    netannualdreamvoice.OnRefreshTopInfo(sUrl, iTopTime)


def GS2CSetAttention(oNetObj):
    iSinger = oNetObj.UnpackInt(4)
    iAttention = oNetObj.UnpackInt(1)
    lstUrl = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sUrl = oNetObj.UnpackPS(1)
        lstUrl.append(sUrl)
    
    protocolcount.ProtocolLog('GS2C=0,iSub=9', 'GS2CSetAttention(TnTSZXO\x00%s,iAttention=%s,lstUrl=%s)' % (iSinger, iAttention, lstUrl))
    netannualdreamvoice.OnSetAttention(iSinger, iAttention, lstUrl)


def GS2CRefreshTicket(oNetObj):
    iType = oNetObj.UnpackInt(1)
    iTicket = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C=0,iSub=10', 'GS2CRefreshTicket(iType=%s,iTicket=%s)' % (iType, iTicket))
    netannualdreamvoice.OnRefreshTicket(iType, iTicket)


def GS2CFameRank(oNetObj):
    iStage = oNetObj.UnpackInt(1)
    lRank = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iPid = oNetObj.UnpackInt(4)
        sName = oNetObj.UnpackPS(1)
        iFame = oNetObj.UnpackInt(4)
        iServer = oNetObj.UnpackInt(4)
        sOrgName = oNetObj.UnpackPS(1)
        iPhoto1 = oNetObj.UnpackInt(4)
        iPhoto2 = oNetObj.UnpackInt(4)
        iPhoto3 = oNetObj.UnpackInt(4)
        iPhoto4 = oNetObj.UnpackInt(4)
        lRank.append([
            iPid,
            sName,
            iFame,
            iServer,
            sOrgName,
            iPhoto1,
            iPhoto2,
            iPhoto3,
            iPhoto4])
    
    protocolcount.ProtocolLog('GS2C=0,iSub=11', 'GS2CFameRank(iStage=%s,lRank=%s)' % (iStage, lRank))
    netannualdreamvoice.OnFameRank(iStage, lRank)


def GS2CRefreshFame(oNetObj):
    iTotalFame = oNetObj.UnpackInt(4)
    sVoiceUrl = oNetObj.UnpackPS(1)
    iVoiceFame = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C=0,iSub=12', 'GS2CRefreshFame(iTotalFame=%s,sVoiceUrl=%s,iVoiceFame=%s)' % (iTotalFame, sVoiceUrl, iVoiceFame))
    netannualdreamvoice.OnRefreshFame(iTotalFame, sVoiceUrl, iVoiceFame)


def GS2CRefreshSingerState(oNetObj):
    iSinger = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C=0,iSub=13', 'GS2CRefreshSingerState(iSinger=%s)' % iSinger)
    netannualdreamvoice.OnRefreshSingerState(iSinger)


def GS2COpenSpecialVedio(oNetObj):
    protocolcount.ProtocolLog('GS2C=0,iSub=14', 'GS2COpenSpecialVedio()')
    netannualdreamvoice.OnOpenSpecialVedio()

g_NetFunction = {
    1: GS2CPersonalInfo,
    2: GS2CFameRecord,
    3: GS2COpenSendFlower,
    4: GS2COpenRegisterUI,
    5: GS2COtherPersonInfo,
    6: GS2CAllSingerInfo,
    7: GS2CAllSingerIDList,
    8: GS2CRefreshTopInfo,
    9: GS2CSetAttention,
    10: GS2CRefreshTicket,
    11: GS2CFameRank,
    12: GS2CRefreshFame,
    13: GS2CRefreshSingerState,
    14: GS2COpenSpecialVedio }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C', '\xb5L\xaak\xb8\xd1\xaaR GS2C=0 \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSUploadVoice(sUrl, iDur, sName, sPic):
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketAddI(iDur, 2)
    oNetObj.PacketAddPS(sName, 1)
    oNetObj.PacketAddPS(sPic, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=1', 'C2GSUploadVoice(sUrl=%s,iDur=%s,sName=%s,sPic=%s)' % (sUrl, iDur, sName, sPic))


def C2GSDeleteVoice(sUrl):
    oNetObj = GetHuoDongNetObj(2)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=2', 'C2GSDeleteVoice(sUrl=%s)' % sUrl)


def C2GSGetPageInfo(lPid):
    oNetObj = GetHuoDongNetObj(3)
    oNetObj.PacketAddI(len(lPid), 1)
    for iPid, sUrl, iServer in lPid:
        oNetObj.PacketAddI(iPid, 4)
        oNetObj.PacketAddPS(sUrl, 1)
        oNetObj.PacketAddI(iServer, 2)
    
    netpublic.SplitPacketSend(oNetObj, net.C2GS_HUODONG)
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=3', 'C2GSGetPageInfo(lPid=%s)' % lPid)


def C2GSOpenFameRecord(iType, iStart, iCnt, iNeedRank):
    oNetObj = GetHuoDongNetObj(4)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketAddI(iStart, 2)
    oNetObj.PacketAddI(iCnt, 1)
    oNetObj.PacketAddI(iNeedRank, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=4', 'C2GSOpenFameRecord(iType=%s,iStart=%s,iCnt=%s,iNeedRank=%s)' % (iType, iStart, iCnt, iNeedRank))


def C2GSSetShowPIC(sVoiceUrl, sPicUrl):
    oNetObj = GetHuoDongNetObj(5)
    oNetObj.PacketAddPS(sVoiceUrl, 1)
    oNetObj.PacketAddPS(sPicUrl, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=5', 'C2GSSetShowPIC(sVoiceUrl=%s,sPicUrl=%s)' % (sVoiceUrl, sPicUrl))


def C2GSVote(iPID, iServer, sUrl, iCnt, iType):
    oNetObj = GetHuoDongNetObj(7)
    oNetObj.PacketAddI(iPID, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketAddI(iCnt, 1)
    oNetObj.PacketAddI(iType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=7', 'C2GSVote(iPID=%s,iServer=%s,sUrl=%s,iCnt=%s,iType=%s)' % (iPID, iServer, sUrl, iCnt, iType))


def C2GSSendFlower(iPID, iServer, iNum, sUrl):
    oNetObj = GetHuoDongNetObj(8)
    oNetObj.PacketAddI(iPID, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketAddI(iNum, 1)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=8', 'C2GSSendFlower(iPID=%s,iServer=%s,iNum=%s,sUrl=%s)' % (iPID, iServer, iNum, sUrl))


def C2GSJubao(iPID, iServer, iReason, sContent, sPicArgs, sVoiceArgs, sNameArgs, sAudioUrl):
    oNetObj = GetHuoDongNetObj(9)
    oNetObj.PacketAddI(iPID, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketAddI(iReason, 1)
    oNetObj.PacketAddPS(sContent, 2)
    oNetObj.PacketAddPS(sPicArgs, 2)
    oNetObj.PacketAddPS(sVoiceArgs, 2)
    oNetObj.PacketAddPS(sNameArgs, 2)
    oNetObj.PacketAddPS(sAudioUrl, 2)
    netpublic.SplitPacketSend(oNetObj, net.C2GS_HUODONG)
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=9', 'C2GSJubao(iPID=%s,iServer=%s,iReason=%s,sContent=%s,sPicArgs=%s,sVoiceArgs=%s,sNameArgs=%s,sAudioUrl=%s)' % (iPID, iServer, iReason, sContent, sPicArgs, sVoiceArgs, sNameArgs, sAudioUrl))


def C2GSOpenSendFlower(iTarget, iServer, sUrl):
    oNetObj = GetHuoDongNetObj(10)
    oNetObj.PacketAddI(iTarget, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=10', 'C2GSOpenSendFlower(iTarget=%s,iServer=%s,sUrl=%s)' % (iTarget, iServer, sUrl))


def C2GSGetSingerInfo(iTarget, iServer):
    oNetObj = GetHuoDongNetObj(11)
    oNetObj.PacketAddI(iTarget, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=11', 'C2GSGetSingerInfo(iTarget=%s,iServer=%s)' % (iTarget, iServer))


def C2GSAdvertise(iTarget, iServer, sUrl):
    oNetObj = GetHuoDongNetObj(12)
    oNetObj.PacketAddI(iTarget, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=12', 'C2GSAdvertise(iTarget=%s,iServer=%s,sUrl=%s)' % (iTarget, iServer, sUrl))


def C2GSSetTop(sUrl):
    oNetObj = GetHuoDongNetObj(13)
    oNetObj.PacketAddPS(sUrl, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=13', 'C2GSSetTop(sUrl=%s)' % sUrl)


def C2GSAttention(iTarget, iServer, iAttention):
    oNetObj = GetHuoDongNetObj(14)
    oNetObj.PacketAddI(iTarget, 4)
    oNetObj.PacketAddI(iServer, 2)
    oNetObj.PacketAddI(iAttention, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=14', 'C2GSAttention(iTarget=%s,iServer=%s,iAttention=%s)' % (iTarget, iServer, iAttention))


def C2GSOpenPersonalInfo():
    oNetObj = GetHuoDongNetObj(15)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=15', 'C2GSOpenPersonalInfo()')


def C2GSOpenRegisterUI():
    oNetObj = GetHuoDongNetObj(16)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=16', 'C2GSOpenRegisterUI()')


def C2GSOpenAllProInfo():
    oNetObj = GetHuoDongNetObj(17)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=17', 'C2GSOpenAllProInfo()')


def GetHuoDongNetObj(iSub):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_HUODONG)
    oNetObj.PacketAddI(len(huodongdefine.YEARVOICE), 1)
    oNetObj.PacketAddS(huodongdefine.YEARVOICE, len(huodongdefine.YEARVOICE))
    oNetObj.PacketAddI(iSub, 1)
    return oNetObj
