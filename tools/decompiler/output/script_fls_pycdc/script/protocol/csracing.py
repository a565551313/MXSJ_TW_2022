# pycdc 交叉复核产物 · script.fls entry 3114
# co_filename(原始)='script/protocol/csracing.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3114.pyc (Python 2.5)

import huodongdefine
import net
import prop
import protocolcount
import netnewracingspeed

def GS2CHuodongState(oNetObj):
    iState = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=1', 'GS2CHuodongState(iState=%s)' % iState)
    netnewracingspeed.OnHuodongState(iState)


def GS2CSyncSpeed(oNetObj):
    iID = oNetObj.UnpackInt(4)
    iSpeed = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=2', 'GS2CSyncSpeed(iID=%s,iSpeed=%s)' % (iID, iSpeed))
    netnewracingspeed.OnSyncSpeed(iID, iSpeed)


def GS2CUpdateBuff(oNetObj):
    lstBuff = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iBuff = oNetObj.UnpackInt(2)
        iTime = oNetObj.UnpackInt(4)
        lstBuff.append([
            iBuff,
            iTime])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=3', 'GS2CUpdateBuff(lstBuff=%s)' % lstBuff)
    netnewracingspeed.OnUpdateBuff(lstBuff)


def GS2CUpdateItemInfo(oNetObj):
    lstItem = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iItemID = oNetObj.UnpackInt(4)
        lstItem.append(iItemID)
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=4', 'GS2CUpdateItemInfo(lstItem=%s)' % lstItem)
    netnewracingspeed.OnUpdateItemInfo(lstItem)


def GS2CUpdateSelfBarriers(oNetObj):
    lstBarrier = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iID = oNetObj.UnpackInt(2)
        iBarrierType = oNetObj.UnpackInt(1)
        iX = oNetObj.UnpackInt(3)
        iY = oNetObj.UnpackInt(3)
        iScale = oNetObj.UnpackInt(1)
        iSymbol = oNetObj.UnpackInt(1)
        lstBarrier.append([
            iID,
            iBarrierType,
            iX,
            iY,
            iScale,
            iSymbol])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=5', 'GS2CUpdateSelfBarriers(lstBarrier=%s)' % lstBarrier)
    netnewracingspeed.OnUpdateSelfBarriers(lstBarrier)


def GS2CClearBarrier(oNetObj):
    iID = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=6', 'GS2CClearBarrier(iID=%s)' % iID)
    netnewracingspeed.OnClearBarrier(iID)


def GS2CStoneProgress(oNetObj):
    iID = oNetObj.UnpackInt(2)
    iCurPro = oNetObj.UnpackInt(1)
    iMaxPro = oNetObj.UnpackInt(1)
    iSpeed = oNetObj.UnpackInt(1)
    lstPusher = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sName = oNetObj.UnpackPS(1)
        lstPusher.append(sName)
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=7', 'GS2CStoneP3.&3ess(iID=%s,iCurPro=%s,iMaxPro=%s,iSpeed=%s,lstPusher=%s)' % (iID, iCurPro, iMaxPro, iSpeed, lstPusher))
    netnewracingspeed.OnStoneProgress(iID, iCurPro, iMaxPro, iSpeed, lstPusher)


def GS2CSetCtrlNpc(oNetObj):
    iNpcID = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=8', 'GS2CSetCtrlNpc(iNpcID=%s)' % iNpcID)
    netnewracingspeed.OnSetCtrlNpc(iNpcID)


def GS2CAddBuff(oNetObj):
    iBuff = oNetObj.UnpackInt(2)
    iTime = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=9', 'GS2CAddBuff(iBuff=%s,iTime=%s)' % (iBuff, iTime))
    netnewracingspeed.OnAddBuff(iBuff, iTime)


def GS2CDelBuff(oNetObj):
    iBuff = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=10', 'GS2CDelBuff(iBuff=%s)' % iBuff)
    netnewracingspeed.OnDelBuff(iBuff)


def GS2CAddBarrierShip(oNetObj):
    iID = oNetObj.UnpackInt(2)
    iBarrierType = oNetObj.UnpackInt(1)
    iSceneID = oNetObj.UnpackInt(2)
    iGroupID = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=11', 'GS2CAddBarrierShip(iID=%s,iBarrierType=%s,iSceneID=%s,iGroupID=%s)' % (iID, iBarrierType, iSceneID, iGroupID))
    netnewracingspeed.OnAddBarrierShip(iID, iBarrierType, iSceneID, iGroupID)


def GS2CPhraseGame(oNetObj):
    iPhraseID = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=12', 'GS2CPhraseGame(iPhraseID=%s)' % iPhraseID)
    netnewracingspeed.OnPhraseGame(iPhraseID)


def GS2CSceneFixID(oNetObj):
    iSceneID = oNetObj.UnpackInt(2)
    iFixID = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=13', 'GS2CSceneFixID(iSceneID=%s,iFixID=%s)' % (iSceneID, iFixID))
    netnewracingspeed.OnSceneFixID(iSceneID, iFixID)


def GS2CDelBarrierShip(oNetObj):
    iID = oNetObj.UnpackInt(2)
    iBarrierType = oNetObj.UnpackInt(1)
    iSceneID = oNetObj.UnpackInt(2)
    iGroupID = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=14', 'GS2CDelBarrierShip(iID=%s,iBarrierType=%s,iSceneID=%s,iGroupID=%s)' % (iID, iBarrierType, iSceneID, iGroupID))
    netnewracingspeed.OnDelBarrierShip(iID, iBarrierType, iSceneID, iGroupID)


def GS2COpenQuesDlg(oNetObj):
    sTitle = oNetObj.UnpackPS(1)
    lstAnswer = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sAnswer = oNetObj.UnpackPS(1)
        lstAnswer.append(sAnswer)
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=15', 'GS2COpenQuesDlg(sTitle=%s,lstAnswer=%s)' % (sTitle, lstAnswer))
    netnewracingspeed.OnOpenQuesDlg(sTitle, lstAnswer)


def GS2COpenDanceDlg(oNetObj):
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=16', 'GS2COpenDanceDlg()')
    netnewracingspeed.OnOpenDanceDlg()


def GS2CCreateRoleEffect(oNetObj):
    iID = oNetObj.UnpackInt(4)
    iAddonID = oNetObj.UnpackInt(2)
    iID.ProtocolLog = 'GS2CCreateRoleEffect(iID=%s,iAddonID=%s)'
    None(None, None % (protocolcount.ProtocolLog, 'GS2C_HUODONG_OP=0,iSub=17'))
    netnewracingspeed.OnCreateRoleEffect(iID, iAddonID)


def GS2CNpcChangeState(oNetObj):
    iID = oNetObj.UnpackInt(4)
    iEmote = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=18', 'GS2CNpcChangeState(iID=%s,iEmote=%s)' % (iID, iEmote))
    netnewracingspeed.OnNpcChangeState(iID, iEmote)


def GS2CPlayEffect(oNetObj):
    iID = oNetObj.UnpackInt(4)
    iEffectID = oNetObj.UnpackInt(2)
    iTimes = oNetObj.UnpackInt(1)
    iInterval = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=19', 'GS2CPlayEffect(iID=%s,iEffectID=%s,iTimes=%s,iInterval=%s)' % (iID, iEffectID, iTimes, iInterval))
    netnewracingspeed.OnPlayEffect(iID, iEffectID, iTimes, iInterval)


def GS2CStartBoxGame(oNetObj):
    lstItem = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iItemID = oNetObj.UnpackInt(4)
        lstItem.append(iItemID)
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=20', 'GS2CStartBoxGame(lstItem=%s)' % lstItem)
    netnewracingspeed.OnStartBoxGame(lstItem)


def GS2CPlayEffectWithRole(oNetObj):
    iID = oNetObj.UnpackInt(4)
    iEffectID = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=21', 'GS2CPlayEffectWithRole(iID=%s,iEffectID=%s)' % (iID, iEffectID))
    netnewracingspeed.OnPlayEffectWithRole(iID, iEffectID)


def GS2CUpdateAimTask(oNetObj):
    lstAimTask = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sDesc = oNetObj.UnpackPS(1)
        iCurrCount = oNetObj.UnpackInt(1)
        iTotalCount = oNetObj.UnpackInt(1)
        iLevel = oNetObj.UnpackInt(1)
        lstAimTask.append([
            sDesc,
            iCurrCount,
            iTotalCount,
            iLevel])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=22', 'GS2CUpdateAimTask(lstAimTask=%s)' % lstAimTask)
    netnewracingspeed.OnUpdateAimTask(lstAimTask)


def GS2COpenTuLangQA(oNetObj):
    sQuestion = oNetObj.UnpackPS(1)
    lstAnswer = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        sName = oNetObj.UnpackPS(1)
        iShap = oNetObj.UnpackInt(2)
        dDesc = prop.UnpackDesc(oNetObj)
        lstAnswer.append([
            sName,
            iShap,
            dDesc])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=23', 'GS2COpenTuLangQA(sQuestion=%s,lstAnswer=%s)' % (sQuestion, lstAnswer))
    netnewracingspeed.OnOpenTuLangQA(sQuestion, lstAnswer)


def GS2CTuLangAnswer(oNetObj):
    iChoose = oNetObj.UnpackInt(1)
    iRight = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=24', 'GS2CTuLangAnswer(iChoose=%s,iRight=%s)' % (iChoose, iRight))
    netnewracingspeed.OnTuLangAnswer(iChoose, iRight)


def GS2CIsLevelRewardSucc(oNetObj):
    iLevel = oNetObj.UnpackInt(1)
    iSucc = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=25', 'GS2CIsLevelRewardSucc(iLevel=%s,iSucc=%s)' % (iLevel, iSucc))
    netnewracingspeed.OnIsLevelRewardSucc(iLevel, iSucc)


def GS2CSetCtrlNpc2(oNetObj):
    iNpcID = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=26', 'GS2CSetCtrlNpc2(iNpcID=%s)' % iNpcID)
    netnewracingspeed.OnSetCtrlNpc2(iNpcID)


def GS2CRoseNum(oNetObj):
    iNum = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0,iSub=27', 'GS2CRoseNum(iNum=%s)' % iNum)
    netnewracingspeed.OnRoseNum(iNum)

g_NetFunction = {
    1: GS2CHuodongState,
    2: GS2CSyncSpeed,
    3: GS2CUpdateBuff,
    4: GS2CUpdateItemInfo,
    5: GS2CUpdateSelfBarriers,
    6: GS2CClearBarrier,
    7: GS2CStoneProgress,
    8: GS2CSetCtrlNpc,
    9: GS2CAddBuff,
    10: GS2CDelBuff,
    11: GS2CAddBarrierShip,
    12: GS2CPhraseGame,
    13: GS2CSceneFixID,
    14: GS2CDelBarrierShip,
    15: GS2COpenQuesDlg,
    16: GS2COpenDanceDlg,
    17: GS2CCreateRoleEffect,
    18: GS2CNpcChangeState,
    19: GS2CPlayEffect,
    20: GS2CStartBoxGame,
    21: GS2CPlayEffectWithRole,
    22: GS2CUpdateAimTask,
    23: GS2COpenTuLangQA,
    24: GS2CTuLangAnswer,
    25: GS2CIsLevelRewardSucc,
    26: GS2CSetCtrlNpc2,
    27: GS2CRoseNum }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_HUODONG_OP', '\xb5L\xaak\xb8\xd1\xaaR GS2C_HUODONG_OP=0 \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSCtrlNpcMove(lstPoint):
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketAddI(len(lstPoint), 1)
    for iX, iY in lstPoint:
        oNetObj.PacketAddI(iX, 3)
        oNetObj.PacketAddI(iY, 3)
    
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=1', 'C2GSCtrlNpcMove(lstPoint=%s)' % lstPoint)


def C2GSUseProp(iItemID):
    oNetObj = GetHuoDongNetObj(2)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=2', 'C2GSUseProp(iItemID=%s)' % iItemID)


def C2GSPushStone(iID):
    oNetObj = GetHuoDongNetObj(3)
    oNetObj.PacketAddI(iID, 2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=3', 'C2GSPushStone(iID=%s)' % iID)


def C2GSUseItem(iItemID):
    oNetObj = GetHuoDongNetObj(4)
    oNetObj.PacketAddI(iItemID, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=4', 'C2GSUseItem(iItemID=%s)' % iItemID)


def C2GSBarrierCatchHero(iBarrierID, iBarrierType):
    oNetObj = GetHuoDongNetObj(5)
    oNetObj.PacketAddI(iBarrierID, 2)
    oNetObj.PacketAddI(iBarrierType, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=5', 'C2GSBarrierCatchHero(iBarrierID=%s,iBarrierType=%s)' % (iBarrierID, iBarrierType))


def C2GSPlayerEnterCircle(iBarrierID, iBarrierType, iMove):
    oNetObj = GetHuoDongNetObj(6)
    oNetObj.PacketAddI(iBarrierID, 2)
    oNetObj.PacketAddI(iBarrierType, 1)
    oNetObj.PacketAddI(iMove, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=6', 'C2GSPlayerEnterCircle(iBarrierID=%s,iBarrierType=%s,iMove=%s)' % (iBarrierID, iBarrierType, iMove))


def C2GSPhraseAnswer(lstChar):
    oNetObj = GetHuoDongNetObj(7)
    oNetObj.PacketAddI(len(lstChar), 1)
    for sChar in lstChar:
        oNetObj.PacketAddPS(sChar, 1)
    
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=7', 'C2GSPhraseAnswer(lstChar=%s)' % lstChar)


def C2GSClickDance():
    oNetObj = GetHuoDongNetObj(8)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=8', 'C2GSClickDance()')


def C2GSClickQuestion(iAnswerID):
    oNetObj = GetHuoDongNetObj(9)
    oNetObj.PacketAddI(iAnswerID, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=9', 'C2GSClickQuestion(iAnswerID=%s)' % iAnswerID)


def C2GSClosePhraseDialog():
    oNetObj = GetHuoDongNetObj(10)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=10', 'C2GSClosePhraseDialog()')


def C2GSUsePropOnRole(iItemID, iID):
    oNetObj = GetHuoDongNetObj(11)
    oNetObj.PacketAddI(iItemID, 4)
    oNetObj.PacketAddI(iID, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=11', 'C2GSUsePropOnRole(iItemID=%s,iID=%s)' % (iItemID, iID))


def C2GSBoxGameClick(iBoxIndex):
    oNetObj = GetHuoDongNetObj(12)
    oNetObj.PacketAddI(iBoxIndex, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=12', 'C2GSBoxGameClick(iBoxIndex=%s)' % iBoxIndex)


def C2GSRewarBoxClick(iRewarBox):
    oNetObj = GetHuoDongNetObj(13)
    oNetObj.PacketAddI(iRewarBox, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=13', 'C2GSRewarBoxClick(iRewarBox=%s)' % iRewarBox)


def C2GSTuLangChoose(iChoose):
    oNetObj = GetHuoDongNetObj(14)
    oNetObj.PacketAddI(iChoose, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0,iSub=14', 'C2GSTuLangChoose(iChoose=%s)' % iChoose)


def GetHuoDongNetObj(iSub):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_HUODONG)
    oNetObj.PacketAddI(len(huodongdefine.RACINGSPEED), 1)
    oNetObj.PacketAddS(huodongdefine.RACINGSPEED, len(huodongdefine.RACINGSPEED))
    oNetObj.PacketAddI(iSub, 1)
    return oNetObj
