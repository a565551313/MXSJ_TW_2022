# pycdc 交叉复核产物 · script.fls entry 2077
# co_filename(原始)='script/mxgame/return/netreturnreward.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2077.pyc (Python 2.5)

import net
import returnrewardmgr
import dlgreturnreward

def C2SSelectEquip(iType, iShape):
    netobj = GetNetObj(1)
    if netobj:
        netobj.PacketAddI(iType, 1)
        netobj.PacketAddI(iShape, 4)
        netobj.PacketSend()
    


def C2SBuyPayPresent(iType):
    netobj = GetNetObj(2)
    if netobj:
        netobj.PacketAddI(iType, 1)
        netobj.PacketSend()
    


def C2SOpenProccessPresent():
    netobj = GetNetObj(3)
    if netobj:
        netobj.PacketSend()
    


def C2SSwitchTmpWing(iType):
    netobj = GetNetObj(4)
    if netobj:
        netobj.PacketAddI(iType, 1)
        netobj.PacketSend()
    


def C2SSwitchTmpHorse(iType):
    netobj = GetNetObj(5)
    if netobj:
        netobj.PacketAddI(iType, 1)
        netobj.PacketSend()
    


def C2SSelectPlayer(iPlayerID):
    netobj = GetNetObj(6)
    if netobj:
        netobj.PacketAddI(iPlayerID, 4)
        netobj.PacketSend()
    


def C2SFirstReward():
    netobj = GetNetObj(7)
    if netobj:
        netobj.PacketSend()
    


def C2SRequestTips(iShape):
    netobj = GetNetObj(8)
    if netobj:
        netobj.PacketAddI(iShape, 4)
        netobj.PacketSend()
    


def C2SOpenExp(iOpen):
    netobj = GetNetObj(9)
    if netobj:
        netobj.PacketAddI(iOpen, 1)
        netobj.PacketSend()
    


def C2SAskOpenReturnRewardDialog():
    netobj = GetNetObj(10)
    if netobj:
        netobj.PacketSend()
    


def S2COpenChuanGong(netobj):
    bInKuafu = netobj.UnpackInt(1)
    iShowWingBtn = netobj.UnpackInt(1)
    iWearTmpWing = netobj.UnpackInt(1)
    iShowHouseBtn = netobj.UnpackInt(1)
    iWearHouseBtn = netobj.UnpackInt(1)
    iPayPresent = netobj.UnpackInt(1)
    iExpRatio = netobj.UnpackInt(1)
    iShowBtnType = netobj.UnpackInt(1)
    iFirstFlg = netobj.UnpackInt(1)
    iTodayRewardCnt = netobj.UnpackInt(1)
    iChuanGongCnt = netobj.UnpackInt(1)
    iLeftTime = netobj.UnpackInt(4)
    iTodayProcess = netobj.UnpackInt(4)
    iAllProcess = netobj.UnpackInt(4)
    iRewardProcessLB = netobj.UnpackInt(4)
    iOpenExp = netobj.UnpackInt(1)
    iExtraExp = netobj.UnpackInt(1)
    iExtraExpMax = netobj.UnpackInt(1)
    iGetExp = netobj.UnpackInt(4)
    i2020PlayerID = netobj.UnpackInt(4)
    dTaskInfoList = []
    iTaskLen = netobj.UnpackInt(2)
    for _ in xrange(iTaskLen):
        dTaskInfo = { }
        dTaskInfo['iTaskID'] = netobj.UnpackInt(2)
        dTaskInfo['iProgress'] = netobj.UnpackInt(2)
        dTaskInfo['iComplete'] = netobj.UnpackInt(1)
    
    iOpenSeamail = netobj.UnpackInt(1)
    oMgr = returnrewardmgr.GetReturnRewardMgr()
    oMgr.SetKuaFuState(bInKuafu)
    oMgr.SetShowWingBtn(iShowWingBtn, iWearTmpWing)
    oMgr.SetShowHouseBtn(iShowHouseBtn, iWearHouseBtn)
    oMgr.SetActiveDlgInfo(iFirstFlg, iTodayRewardCnt, iChuanGongCnt, iTodayProcess, iAllProcess, iRewardProcessLB)
    oMgr.SetLeftTime(iLeftTime)
    oMgr.SetPayPresent(iPayPresent, iShowBtnType)
    oMgr.SetExpRatio(iExpRatio)
    oMgr.SetExtraExp(iOpenExp, iExtraExp)
    oMgr.SetExtraExpMax(iExtraExpMax)
    oMgr.SetGetExp(iGetExp)
    oMgr.Set2020PlayerID(i2020PlayerID)
    oMgr.Set2020TaskList(dTaskInfoList)
    oMgr.SetOpenSeamail(iOpenSeamail)
    import md2020return
    for dTaskInfo in dTaskInfoList:
        if dTaskInfo['iComplete'] and not dTaskInfo['iGot']:
            md2020return.GetModel().SetBackRedPoint(md2020return.GetModel().RedPoint_Reward, 1)
            break
            continue
        netobj.UnpackInt
    


def S2CUpdateTips(netobj):
    iTips = netobj.UnpackString(0)
    returnrewardmgr.GetReturnRewardMgr().UpdateItemTips(iTips)


def S2CShowExitTips(netobj):
    iType = netobj.UnpackInt(1)
    oMgr = returnrewardmgr.GetReturnRewardMgr()
    oMgr.SetExitTipsType(iType)


def S2CFirstLoginBUFF(netobj):
    oMgr = returnrewardmgr.GetReturnRewardMgr()
    oMgr.SetFirstLoginAni(True)


def S2CFistLoginLink(netobj):
    import autofindpath
    oMgr = returnrewardmgr.GetReturnRewardMgr()
    oMgr.SetFirstLoginLink(True)
    autofindpath.SetNearFindFlag(True)


def S2COpenReturnItem(netobj):
    import dlgreturnreward
    dlgreturnreward.OpenShiGuangXinJian()


def S2CServerOpenReturnReward(netobj):
    import dlgreturnreward
    iState = netobj.UnpackInt(1)
    dlgreturnreward.RealOpenRewardDlg(iState)

SUB_FUNC = {
    1: None,
    2: S2COpenChuanGong,
    3: None,
    4: S2CUpdateTips,
    5: S2CShowExitTips,
    6: S2CFirstLoginBUFF,
    7: S2CFistLoginLink,
    8: S2COpenReturnItem,
    9: S2CServerOpenReturnReward }

def S2CReturnRewardProcess(netobj):
    iSub = netobj.UnpackInt(1)
    oSubFunc = SUB_FUNC.get(iSub)
    if not oSubFunc:
        return None
    
    import protocolprint
    protocolprint.AppendS2CSubInfo('netreturnreward', oSubFunc.__name__)
    oSubFunc(netobj)


def GetNetObj(iSub):
    import nethuodong
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    if netobj:
        sStr = nethuodong.RETURNREWARD
        netobj.PacketAddPS(sStr)
        netobj.PacketAddI(iSub, 1)
    
    return netobj
