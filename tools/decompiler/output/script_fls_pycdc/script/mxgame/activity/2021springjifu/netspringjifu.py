# pycdc 交叉复核产物 · script.fls entry 3828
# co_filename(原始)='script/mxgame/activity/2021springjifu/netspringjifu.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3828.pyc (Python 2.5)

import mdspringjifu

def S2CUpdateData(iCmd, dData):
    mdspringjifu.GetSpringJiFuMgr().SetDrawResult(dData)


def OnDialogData(iDailyLogin, iDailyTYF, iHYTicket, iCZTicket, iTicketCnt, iSameFKCnt, iHYGetLimit, iCZGetLimit, iFDStatus, iTTStatus, sData):
    None(None, None, None, None, None, None, None, None, None, None, mdspringjifu.GetSpringJiFuMgr().UpdateItemInfo, iDailyLogin, iDailyTYF, iHYTicket, iCZTicket, iTicketCnt, iSameFKCnt, iHYGetLimit, iCZGetLimit, iFDStatus, iTTStatus, sData)


def OnRedDot(iRedDot):
    mdspringjifu.GetSpringJiFuMgr().SetRedDot(iRedDot)


def C2SDrawLottery(iType, iCmd, dData):
    import minigame101
    minigame101.C2GSGameCmd(iType, iCmd, dData)


def C2SDrawReward():
    import csnewyearjifu
    csnewyearjifu.C2GSDrawReward()


def C2SGetDailogData():
    import csnewyearjifu
    csnewyearjifu.C2GSGetDailogData()


def C2SGetFinishReward(iRewardID):
    import csnewyearjifu
    csnewyearjifu.C2GSGetReward(iRewardID)
