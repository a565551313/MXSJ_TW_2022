# pycdc 交叉复核产物 · script.fls entry 952
# co_filename(原始)='script/mxgame/activity/2021duangwu/netduanwu2021.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_952.pyc (Python 2.5)

import csduanwu2021
import duangwu2021define
import duangwu2021interface
import misc

def GetServerCurrentTime():
    return misc.GetServerCurrentTime()


def OnRefreshPageRedDot():
    import md2021duangwumain
    md2021duangwumain.GetC2021DuangWuMainMd().SetTodayTipsRedDot(1)


def OnRefreshMainDlgData(lZongziInfo, iProgress, iRewardList):
    dZongziList = { }
    for iIdx, lItem in enumerate(lZongziInfo):
        (iID, iEndTime, iTolHelpTime, iState) = lItem
        dItem = {
            duangwu2021define.KEY_ID: iID,
            duangwu2021define.KEY_REMAININGTIME: iEndTime - iTolHelpTime - GetServerCurrentTime(),
            duangwu2021define.KEY_STATE: duangwu2021interface.GetBtnStateByCookState(iState) }
        dZongziList[iIdx + 1] = dItem
    
    dAwardData = {
        duangwu2021define.KEY_PROGRESS: iProgress,
        duangwu2021define.KEY_REWARDLIST: iRewardList }
    import md2021duangwumain
    oModel = md2021duangwumain.GetC2021DuangWuMainMd()
    oModel.SetZongziListData(dZongziList)
    oModel.SetAwardData(dAwardData)


def OnRefreshSeekHelpListRedDot():
    import mdreddot
    mdreddot.GetMgr().Update(duangwu2021define.RED_SEEKHELPLIST, 1)


def OnOpenMaterialSource(iID, iShow, iZongyeNoumiAmount, iZongyeNoumiSumAmount, lClues):
    import dlg2021duangwumaterialsource
    dlg2021duangwumaterialsource.Show(iID, iShow, iZongyeNoumiAmount, iZongyeNoumiSumAmount, lClues)


def OnOpenCooking(iType, iSpeedUped, iID, iSumSpeedUpTime, iEndTime, iSumTime, iHeroID, oHeroPhoto, iHeroName, lHelp):
    dCookRate = {
        duangwu2021define.KEY_SPEEDUPTIME: iSumSpeedUpTime,
        duangwu2021define.KEY_REMAININGTIME: max(iEndTime - iSumSpeedUpTime - GetServerCurrentTime(), 0),
        duangwu2021define.KEY_TIME: iSumTime }
    dHeroInfo = {
        duangwu2021define.KEY_ID: iHeroID,
        duangwu2021define.KEY_PHOTO: oHeroPhoto,
        duangwu2021define.KEY_NAME: iHeroName }
    lHelpPlayer = []
    for lItem in lHelp:
        dItem = {
            duangwu2021define.KEY_ID: lItem[0],
            duangwu2021define.KEY_PHOTO: lItem[1],
            duangwu2021define.KEY_NAME: lItem[2],
            duangwu2021define.KEY_SPEEDUPTIME: lItem[3] }
        lHelpPlayer.append(dItem)
    
    import md2021duangwucooking
    oModel = md2021duangwucooking.GetCCookingModel(iType)
    oModel.SetHelpPlayerList(lHelpPlayer)
    oModel.SetCookRate(dCookRate)
    oModel.SetTargetPlayerInfo(dHeroInfo)
    oModel.SetZongziID(iID)
    oModel.SetSpeedUped(iSpeedUped)
    import dlg2021duangwucooking
    dlg2021duangwucooking.Show(iType)


def OnOpenPersonalHelpDlg(iZongziID, lFriend, lGroup):
    dFriendList = []
    for lItem in lFriend:
        dItem = {
            duangwu2021define.KEY_ID: lItem[0],
            duangwu2021define.KEY_PHOTO: lItem[1],
            duangwu2021define.KEY_NAME: lItem[2],
            duangwu2021define.KEY_TEXT: duangwu2021interface.GetRandomDialogue() }
        dFriendList.append(dItem)
    
    dGroupList = []
    for lItem in lGroup:
        dItem = {
            duangwu2021define.KEY_ID: lItem[0],
            duangwu2021define.KEY_PHOTO: lItem[1],
            duangwu2021define.KEY_NAME: lItem[2],
            duangwu2021define.KEY_TEXT: duangwu2021interface.GetRandomDialogue() }
        dGroupList.append(dItem)
    
    import md2021duangwupersonalhelp
    oModel = md2021duangwupersonalhelp.GetC2021DuanguPersonalHelpModel()
    oModel.SetListByType(duangwu2021define.TYPE_FRIEND, dFriendList)
    oModel.SetListByType(duangwu2021define.TYPE_GROUP, dGroupList)
    oModel.SetZongziID(iZongziID)
    import dlg2021duangwupersonalhelp
    dlg2021duangwupersonalhelp.Show()


def OnPlaySpeedUpAnimation(iCurrSpeedUpTime, iSumSpeedUpTime, iEndTime, iSumTime):
    iRemainingTime = iEndTime - iSumSpeedUpTime - GetServerCurrentTime()
    fBeforeProgress = float(iSumTime - iRemainingTime - iCurrSpeedUpTime) / iSumTime
    fAfterProgress = float(iSumTime - iRemainingTime) / iSumTime
    import dlg2021duangwuspeedup
    dlg2021duangwuspeedup.Show(iCurrSpeedUpTime, fBeforeProgress, fAfterProgress)


def OnOpenSeekHelpList(iType, lSeekHelp, lHelpedMe):
    dSeekHelpList = []
    for lItem in lSeekHelp:
        (iPlayerID, oPlayerP70+o, iPlayerName, sMsg, iZongZiNo, iSpeedUpTime, iEndTime, iSumTime) = lItem
        dItem = {
            duangwu2021define.KEY_ID: iPlayerID,
            duangwu2021define.KEY_PHOTO: oPlayerP70+o,
            duangwu2021define.KEY_NAME: iPlayerName,
            duangwu2021define.KEY_TEXT:  if sMsg else duangwu2021interface.GetRandomDialogue(),
            duangwu2021define.KEY_IDX: iZongZiNo,
            duangwu2021define.KEY_REMAININGTIME: iEndTime - iSpeedUpTime - GetServerCurrentTime(),
            duangwu2021define.KEY_TIME: iSumTime,
            duangwu2021define.KEY_TYPE: duangwu2021define.TYPE_SEEKHELP }
        dSeekHelpList.append(dItem)
    
    dHelpedMeList = []
    for lItem in lHelpedMe:
        dItem = {
            duangwu2021define.KEY_ID: lItem[0],
            duangwu2021define.KEY_PHOTO: lItem[1],
            duangwu2021define.KEY_NAME: lItem[2],
            duangwu2021define.KEY_IDX: lItem[3],
            duangwu2021define.KEY_SPEEDUPTIME: lItem[4],
            duangwu2021define.KEY_TYPE: duangwu2021define.TYPE_HELPEDME }
        dHelpedMeList.append(dItem)
    
    import md2021duangwuhelplist
    oModel = md2021duangwuhelplist.GetC2021DuanguHelpListModelModel()
    oModel.SetListByType(duangwu2021define.TYPE_SEEKHELP, dSeekHelpList)
    oModel.SetListByType(duangwu2021define.TYPE_HELPEDME, dHelpedMeList)
    import dlg2021duangwuhelplist
    if iType == 1:
        dlg2021duangwuhelplist.Show()
    


def OnIllustratedbooksDlg(lZongzi):
    import dlg2021duangwuIllustratedbooks
    dlg2021duangwuIllustratedbooks.Show(lZongzi)


def OnRefreshStartCookDot(iShow, iZongziID):
    import md2021duangwumain
    md2021duangwumain.GetC2021DuangWuMainMd().SetStartCookRedDot(iShow, iZongziID)


def OnRefreshAwardRedDot(iShow):
    import md2021duangwumain
    md2021duangwumain.GetC2021DuangWuMainMd().SetAwardRedDot(iShow)


def OnRefreshIllustratedbookRedDot():
    import md2021duangwumain
    md2021duangwumain.GetC2021DuangWuMainMd().SetIllustratedbookRedDot(1)


def C2GSRequestMainDlgData():
    csduanwu2021.C2GSRequestMainDlgData()


def C2GSClickZongziActBtn(iID, iBtnState):
    csduanwu2021.C2GSClickZongziActBtn(iID, iBtnState)


def C2GSReceiveAward(iIdx):
    csduanwu2021.C2GSReceiveAward(iIdx)


def C2GSInitiateHelp(iZongziID):
    csduanwu2021.C2GSInitiateHelp(iZongziID)


def C2GSHelpSpeedUp(iTargetID, iZongziID):
    csduanwu2021.C2GSHelpSpeedUp(iTargetID, iZongziID)


def C2GSOpenPersonalHelpDlg(iZongziID):
    csduanwu2021.C2GSOpenPersonalHelpDlg(iZongziID)


def C2GSSeekHelp(iTargetID, sMsg, iZongziID):
    csduanwu2021.C2GSSeekHelp(iTargetID, sMsg, iZongziID)


def C2GSOpenSeekHelpList():
    csduanwu2021.C2GSOpenSeekHelpList()


def C2GSSpeedUp(iType, iTargetID, iZongziID):
    csduanwu2021.C2GSSpeedUp(iType, iTargetID, iZongziID)


def C2GSIllustratedbooksDlg():
    csduanwu2021.C2GSIllustratedbooksDlg()
