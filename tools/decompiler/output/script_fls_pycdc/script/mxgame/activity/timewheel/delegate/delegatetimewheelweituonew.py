# pycdc 交叉复核产物 · script.fls entry 2860
# co_filename(原始)='script/mxgame/activity/timewheel/delegate/delegatetimewheelweituonew.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2860.pyc (Python 2.5)

import delegatebase
import timewheeldefine
import timewheelinterface
import nettimewheeldelegate
import misc
import friend
import dlgtalk
import usermacro
import time
import wheeltimeweituodata

class CWeituoDelegateDgt(delegatebase.CDelegateBase):
    
    def __init__(self, oParent):
        delegatebase.CDelegateBase.__init__(self, oParent)
        self.InitSignal()
        self.OnUpdateQuickAcceptReward()

    
    def InitSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_Open, self.OnOpen)
        oView.ssConnect(oView.SS_Close, self.OnClose)
        oView.ssConnect(oView.SS_InitView, self.RefreshWeiTuoList)
        oView.ssConnect(oView.SS_ClickTaskItem, self.OnClickTaskItem)
        oView.ssConnect(oView.SS_RefreshUnPublishPanal, self.OnRefreshUnPublishPanal)
        oView.ssConnect(oView.SS_RefreshPublishPanal, self.OnRefreshPublishPanal)
        oView.ssConnect(oView.SS_RefreshHavePanal, self.OnRefreshHavePanal)
        oView.ssConnect(oView.SS_OpenOnceDelegateDlg, self.OnOpenPublishDlg)
        oView.ssConnect(oView.SS_OpenBatchDelegateDlg, self.OnOpenPublishDlg)
        oView.ssConnect(oView.SS_CancelTask, self.OnCanaelTask)
        oView.ssConnect(oView.SS_OpenChatBox, self.OnOpenChatBox)
        oView.ssConnect(oView.SS_RefreshGetTaskPanal, self.OnRefreshGetTaskPanal)
        oView.ssConnect(oView.SS_RefreshTimerText, self.OnRefreshTimerText)
        oView.ssConnect(oView.SS_GetTaskReward, self.OnGetTaskReward)
        oView.ssConnect(oView.SS_OpenChangeDelegateDlg, self.OnOpenPublishDlg)
        oView.ssConnect(oView.SS_EditWeituoData, self.OnEditWeituoData)
        oView.ssConnect(oView.SS_MakeSureChangeData, self.OnMakeSureChangeData)
        oView.ssConnect(oView.SS_WatchTaskExpend, self.OnWatchTaskExpend)
        oView.ssConnect(oView.SS_ClickZhiyeText, self.OnClickZhiyeText)
        oView.ssConnect(oView.SS_SelectZhiyeBtn, self.OnSelectZhiyeBtn)
        oView.ssConnect(oView.SS_SelectXiulianBtn, self.OnSelectXiulianBtn)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_ChangeTaskSelect, self.OnChangeTaskListSelect)
        oModel.ssConnect(oModel.SS_RefreshHavePanalWeituoData, self.OnRefreshHavePanalWeituoData)
        oModel.ssConnect(oModel.SS_RefreshWeituoTaskList, self.RefreshWeiTuoList)
        oModel.ssConnect(oModel.SS_GetRewardSucceed, self.OnGetRewardSucceed)
        oModel.ssConnect(oModel.SS_UpdateQuickAcceptReward, self.OnUpdateQuickAcceptReward)

    
    def GetView(self):
        '''
\t\t:return: dlgtimewheelweituonew.CTimeWheelWeiTuoDlg
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        return timewheelinterface.GetTimeWheelTaskDelegateDataMgr()

    
    def OnOpen(self, dExtend):
        oView = self.GetView()
        oView.SetShow(True)

    
    def OnClose(self):
        oView = self.GetView()
        oView.SetShow(False)
        oView.ClearCutDownTimer()

    
    def InitViewPanal(self):
        pass

    
    def RefreshWeiTuoList(self):
        '''\xa8\xea\xb7s\xa9e\xb0U\xa5\xf4\xb0\xc8\xa6C\xaa\xed'''
        oModel = self.GetModel()
        iWeituoTypeList = oModel.GetWeituoTypeList()
        dWeituoInfoList = []
        iGreyIdList = []
        for iType in iWeituoTypeList:
            dWeituoInfo = misc.DeepCopy(oModel.GetWeituoDescInfo(iType))
            sState = oModel.GetWeituoState(iType)
            if oModel.IsHaveMonthCard(iType):
                dWeituoInfo['iWeekCardHaveBuy'] = 1
                dWeituoInfo['bWeekCardShowGray'] = not oModel.IsCanUseMonthCardFreePublish(iType)
            
            if sState == '':
                continue
            
            dWeituoInfo['iType'] = iType
            if sState == '\xa5i\xbb\xe2\xa8\xfa':
                dWeituoInfo['tStatusPath'] = ('combdialog4/\xd4\xd3\xcd\xbc/\xca\xb1\xb9\xe2\xd6\xae\xc2\xd6/\xbf\xc9\xc1\xec\xc8\xa1.png', 'interface')
            elif sState == '\xa9e\xb0U\xa4\xa4':
                dWeituoInfo['tStatusPath'] = ('combdialog4/\xd4\xd3\xcd\xbc/\xca\xb1\xb9\xe2\xd6\xae\xc2\xd6/\xce\xaf\xcd\xd0\xd6\xd0.png', 'interface')
            elif sState == '\xa4w\xb5o\xa7G':
                if oModel.IsPublishNextDay(iType):
                    dWeituoInfo['tStatusPath'] = ('combdialog4/\xd4\xd3\xcd\xbc/\xca\xb1\xb9\xe2\xd6\xae\xc2\xd6/\xb4\xfd\xb7\xa2\xb2\xbc.png', 'interface')
                    iGreyIdList.append(iType)
                else:
                    dWeituoInfo['tStatusPath'] = ('combdialog4/\xd4\xd3\xcd\xbc/\xca\xb1\xb9\xe2\xd6\xae\xc2\xd6/\xd2\xd1\xb7\xa2\xb2\xbc.png', 'interface')
            elif sState == '\xa4w\xa7\xb9\xa6\xa8':
                dWeituoInfo['sDurable'] = sState
                iGreyIdList.append(iType)
            elif sState == '\xa4w\xbb\xe2\xa8\xfa':
                iHaveDone = oModel.GetWeituoFinishTime(iType)
                dWeituoInfo['sDurable'] = sState
                dWeituoInfo['sDesc2'] = '\xa7\xb9\xa6\xa8\xbc\xc6:%s' % str(iHaveDone)
            else:
                dWeituoInfo['sDurable'] = sState
                if oModel.IsPublishNextDay(iType):
                    iGreyIdList.append(iType)
                
            dWeituoInfoList.append(dWeituoInfo)
        
        self.GetView().UpdataWeituoList(dWeituoInfoList)
        self.GetView().RefreshListGrey(iGreyIdList)
        self.InitSelect()

    
    def InitSelect(self):
        '''\xc0q\xbb{\xbf\xef\xa4\xa4'''
        oModel = self.GetModel()
        iSelect = oModel.GetCurTaskItemSelect()
        iTypeList = oModel.GetWeituoTypeList()
        for iType in iTypeList:
            bSelect = oModel.IsCanGetReward(iType)
            if bSelect:
                self.OnClickTaskItem(iType)
                return None
                continue
        
        if iSelect == -1:
            self.OnClickTaskItem(iTypeList[0])
        else:
            self.OnClickTaskItem(iSelect)

    
    def OnClickTaskItem(self, iType):
        '''\xa7\xf3\xb7s\xbf\xef\xa4\xa4\xa8\xea\xb7s\xa5k\xb0\xbc\xac\xc9\xad\xb1'''
        self.GetModel().SetCurTaskItemSelect(iType)
        self.RefreshRightView(iType)

    
    def RefreshRightView(self, iType):
        '''\xa8\xea\xb7s\xa5k\xb0\xbc\xac\xc9\xad\xb1'''
        sState = self.GetModel().GetWeituoState(iType)
        sRole = self.GetModel().GetRoleOfTask(iType)
        oView = self.GetView()
        if sState in ('\xa5i\xbb\xe2\xa8\xfa', '\xa9e\xb0U\xa4\xa4', '\xa4w\xa7\xb9\xa6\xa8') and sRole == '\xb5o\xa7G\xaa\xcc':
            oView.SwitchPanalModel('have')
        elif sState == '\xa4w\xb5o\xa7G' and sRole == '\xb5o\xa7G\xaa\xcc':
            oView.SwitchPanalModel('publish')
        elif sRole == '\xb1\xb5\xa8\xfc\xaa\xcc':
            oView.SwitchPanalModel('get')
        elif sState == '':
            return None
        else:
            oView.SwitchPanalModel('unpublish')

    
    def OnRefreshUnPublishPanal(self):
        '''\xa5\xbc\xb5o\xa7G\xb1\xa1\xaap\xa4U\xaa\xba\xa8\xea\xb7s\xa4\xe8\xaak'''
        self.GetView().ClearCutDownTimer()
        oModel = self.GetModel()
        iType = oModel.GetCurTaskItemSelect()
        bPublishNextDay = oModel.IsPublishNextDay(iType)
        sTaskDesc = oModel.GetWeituoDescText(iType)
        bMonthCardFreePub = oModel.IsCanUseMonthCardFreePublish(iType)
        sMonthCardToPubTimes = ''
        if bMonthCardFreePub:
            iMonthCardToPubTimes = oModel.GetMonthCardToWeituoTimes(iType)
            sTaskName = oModel.GetWeituoTaskName(iType)
            sMonthCardToPubTimes = '#CLR3#n%d\xa6\xb8%s\xa4\xeb\xa5d\xa5i\xa7K\xb6O\xb5o\xa7G1\xa6\xb8\xa9e\xb0U#n' % (iMonthCardToPubTimes, sTaskName)
        
        if bPublishNextDay:
            sPublishDesc = '\xa5i\xb5o\xa7G#CLR3#n\xa9\xfa\xa4\xe9#n\xa9e\xb0U'
        else:
            sPublishDesc = self.GetPublishDesc()
        dWeituoPanalInfo = {
            'sTaskDesc': sTaskDesc,
            'sPublishDesc': sPublishDesc,
            'bMonthCardFreePub': bMonthCardFreePub,
            'sMonthCardToPubTimes': sMonthCardToPubTimes,
            'iType': iType }
        self.GetView().RefreshUnPublishPanal(dWeituoPanalInfo)

    
    def GetPublishDesc(self):
        '''
\t\t\xc0\xf2\xa8\xfa\xa9e\xb0U\xa4\xe5\xa5\xbb\xa1A
\t\t:return:
\t\t'''
        sNewTime = time.strftime('%m-%d', misc.LocalTime(misc.GetServerCurrentTime()))
        dPhonePublishData = wheeltimeweituodata.GetPhoneData()
        for sTimeRange, dData in dPhonePublishData.iteritems():
            (sStartTime, sEndTime) = self.CalStartAndEndTime(sTimeRange)
            if sNewTime >= sStartTime and sNewTime <= sEndTime:
                return dData['sDesc']
                continue
        
        return '\xa5i\xb5o\xa7G\xa4\xb5\xa4\xe9\xa9e\xb0U'

    
    def CalStartAndEndTime(self, sTimeRange):
        '''
\t\t\xadp\xba\xe2\xb6}\xa9l\xae\xc9\xb6\xa1\xa9M\xb5\xb2\xa7\xf4\xae\xc9\xb6\xa1
\t\t:param sTimeRange:\xae\xc9\xb6\xa1\xb0\xcf\xb6\xa1
\t\t:return:
\t\t'''
        sStartTime = sTimeRange.split('-')[0]
        sStartTime = '%s-%s' % (sStartTime.split('.')[0], sStartTime.split('.')[1])
        sEndTime = sTimeRange.split('-')[1]
        sEndTime = '%s-%s' % (sEndTime.split('.')[0], sEndTime.split('.')[1])
        return (sStartTime, sEndTime)

    
    def OnRefreshPublishPanal(self):
        '''\xa4w\xb5o\xa7G\xb1\xa1\xaap\xa4U\xaa\xba\xa8\xea\xb7s\xa4\xe8\xaak'''
        self.GetView().ClearCutDownTimer()
        oModel = self.GetModel()
        iType = oModel.GetCurTaskItemSelect()
        iDays = oModel.GetWeituoDaysByType(iType)
        iDefaultDur = oModel.GetTaskDefaultDurByType(iType)
        iTaskCount = oModel.GetWeituoCurTaskTimes(iType)
        iFrozenDur = iDays * iTaskCount * iDefaultDur
        sTaskDesc = self.GetModel().GetWeituoDescText(iType)
        bPublishNextDay = self.GetModel().IsPublishNextDay(iType)
        dWeituoPanalInfo = {
            'sTaskDesc': sTaskDesc,
            'sTips':  if bPublishNextDay else '\xa9e\xb0U\xb5\xa5\xab\xdd\xbb\xe2\xa8\xfa\xa4\xa4',
            'iWeituoDays': iDays,
            'iFrozenDur': iFrozenDur,
            'iType': iType }
        self.GetView().RefreshPublishPanal(dWeituoPanalInfo)

    
    def OnRefreshHavePanal(self):
        '''\xa9e\xb0U\xa4\xa4\xb1\xa1\xaap\xa4U\xaa\xba\xa8\xea\xb7s\xa4\xe8\xaak'''
        self.GetView().ClearCutDownTimer()
        oModel = self.GetModel()
        iType = oModel.GetCurTaskItemSelect()
        sState = oModel.GetWeituoState(iType)
        sDesc = oModel.GetWeituoRewardDescByType(iType)
        iDays = oModel.GetWeituoDaysByType(iType)
        iDefaultDur = oModel.GetTaskDefaultDurByType(iType)
        iTaskCount = oModel.GetWeituoCurTaskTimes(iType)
        iFrozenDur = iDays * iTaskCount * iDefaultDur
        lstPhoto = oModel.GetActerPhotoByType(iType)
        (iActerID, sActerName) = oModel.GetActerIdAndNameByType(iType)
        sRelation = oModel.GetRelationShipByType(iType)
        dWeituoPanalInfo = {
            'sState': sState,
            'sDesc': sDesc,
            'lstPhoto': lstPhoto,
            'iActerID': iActerID,
            'sActerName': sActerName,
            'sRelation': sRelation,
            'iWeituoDays': iDays,
            'iFrozenDur': iFrozenDur,
            'iType': iType }
        self.GetView().RefreshHavePanal(dWeituoPanalInfo)
        self.RequestWeituoChangeData()

    
    def RequestWeituoChangeData(self):
        '''\xbd\xd0\xa8D\xaaA\xb0\xc8\xba\xdd\xb7\xed\xabe\xa9e\xb0U\xaa\xba\xabH\xae\xa7'''
        iType = self.GetModel().GetCurTaskItemSelect()
        nettimewheeldelegate.C2GSChangeEntrust(iType, 0)

    
    def OnEditWeituoData(self, sType):
        '''\xbds\xbf\xe8\xb7\xed\xabe\xaa\xba\xa9e\xb0U\xabH\xae\xa7'''
        iDays = self.GetModel().GetLoaclTaskData()['iDay']
        if iDays <= 0:
            usermacro.PROMPT_MSG('\xa9e\xb0U\xa4w\xa7\xb9\xa6\xa8,\xa5i\xa8\xcf\xa5\xce\xb5o\xa7G\xa9e\xa6\xab\xa5\\\xaf\xe0\xb5o\xa7G\xa9\xfa\xa4\xe9\xa9e\xb0U')
        
        iServerDay = self.GetModel().GetServerTaskData()['iDay']
        continue
        sType == 'up'
        if iDays in range(1, 5):
            iDays += 1
        
        iDays in range(1, 5)
        if sType == 'down':
            if iDays in range(2, 6):
                iDays -= 1
            
        
        self.GetModel().EditLocalTaskData('iDay', iDays)
        self.GetView().SetShowMakeSureBtn(iDays != iServerDay)

    
    def OnRefreshHavePanalWeituoData(self, sType, oValue):
        '''\xa8\xea\xb7s\xbc\xc6\xbe\xda\xb9\xef\xc0\xb3\xaa\xba\xac\xc9\xad\xb1\xa4\xba\xaee'''
        self.GetView().RefreshHavePanalWeituoData(sType, oValue)

    
    def OnMakeSureChangeData(self):
        '''\xc2I\xc0\xbb\xbdT\xa9w\xad\xd7\xa7\xef'''
        dChangeData = self.GetModel().GetLoaclTaskData()
        lstWeituo = [
            [
                dChangeData['iTask'],
                dChangeData['iDay'],
                dChangeData['iCount']]]
        lstTarget = dChangeData['lstOrderPid']
        nettimewheeldelegate.C2SPublish(lstWeituo, lstTarget)

    
    def OnRefreshGetTaskPanal(self):
        '''\xa9e\xb0U\xa5\xf4\xb0\xc8\xbb\xe2\xa8\xfa\xaa\xcc\xaa\xba\xac\xc9\xad\xb1\xa8\xea\xb7s\xa4\xe8\xaak'''
        oModel = self.GetModel()
        iSelect = oModel.GetCurTaskItemSelect()
        sTaskDesc = oModel.GetWeituoDescText(iSelect)
        sPublisherName = oModel.GetWeituoPublisherID(iSelect)
        iHaveDoneNum = oModel.GetWeituoHaveDoneNum(iSelect)
        iTotalNum = oModel.GetWeituoTotalNum(iSelect)
        iDeadLine = oModel.GetWeituoEndTime(iSelect)
        iLeftTime = iDeadLine - misc.GetServerCurrentTime()
        dGetPanalInfo = {
            'iType': iSelect,
            'sTaskDesc': sTaskDesc,
            'sPublisherName': '\xa4w\xb1\xb5\xa8\xfa%s\xaa\xba\xa9e\xb0U' % sPublisherName,
            'sRateText': '%d/%d' % (iHaveDoneNum, iTotalNum),
            'bEnd': iLeftTime < 0 }
        self.GetView().RefreshGetPanal(dGetPanalInfo)
        self.GetView().CreateCutDownTimer()

    
    def OnRefreshTimerText(self):
        '''\xad\xcb\xadp\xae\xc9\xa8\xea\xb7s'''
        oModel = self.GetModel()
        iSelect = oModel.GetCurTaskItemSelect()
        iDeadLine = oModel.GetWeituoEndTime(iSelect)
        iLeftTime = iDeadLine - misc.GetServerCurrentTime()
        if iLeftTime < 0:
            self.GetView().ClearCutDownTimer()
            self.GetView().TaskTimeEnd(iLeftTime < 0)
        else:
            iHour = iLeftTime / 3600
            iMinute = (iLeftTime % 3600) / 60
            iSecond = iLeftTime % 60
            sTimer = '%s:%s:%s' % (self.CalculateStrTimer(iHour), self.CalculateStrTimer(iMinute), self.CalculateStrTimer(iSecond))
            self.GetView().RefreshTimerText(sTimer)

    
    def CalculateStrTimer(self, iTimer):
        '''\xadp\xae\xc9\xa4\xe5\xa5\xbb\xc2\xe0\xb4\xab'''
        if iTimer in range(10, 60):
            return str(iTimer)
        elif iTimer in range(0, 10):
            return '0%d' % iTimer
        else:
            return '00'

    
    def OnChangeTaskListSelect(self, iCurSelect):
        self.GetView().RefreshListSelect(iCurSelect)

    
    def OnOpenPublishDlg(self, sMode):
        dMode = {
            'change': 0,
            'Once': 1,
            'batch': 2 }
        iType = self.GetModel().GetCurTaskItemSelect()
        nettimewheeldelegate.C2SOpenPublishDlg(iType, dMode[sMode])

    
    def OnCanaelTask(self):
        iType = self.GetModel().GetCurTaskItemSelect()
        nettimewheeldelegate.C2SCancelWeituo(iType)

    
    def OnOpenChatBox(self):
        oModel = self.GetModel()
        iType = self.GetModel().GetCurTaskItemSelect()
        iActerID = oModel.GetWeituoActerID(iType)
        if iActerID <= 1:
            import dlgnpc
            dlgnpc.ShowClientDlg('\xb5L\xaak\xa6V\xaf\xab\xaf\xb5\xa4H\xb5o\xb0_\xb2\xe1\xa4\xd1', '', None, 111)
            return None
        else:
            dlgtalk.ShowTalkDialog(iActerID, friend.GetFriendName(iActerID), friend.GetFriendIcon(iActerID))

    
    def OnGetTaskReward(self):
        import dlgquickgetweituoreward
        iSelect = self.GetModel().GetCurTaskItemSelect()
        nettimewheeldelegate.C2SGetReward(iSelect)
        dlgquickgetweituoreward.CloseMiniDlg()

    
    def OnWatchTaskExpend(self):
        import dlgquickgetweituoreward
        iSelect = self.GetModel().GetCurTaskItemSelect()
        nettimewheeldelegate.C2SGetReward(iSelect)
        dlgquickgetweituoreward.CloseMiniDlg()

    
    def OnGetRewardSucceed(self):
        self.GetModel().SetCurTaskItemSelect(-1)

    
    def OnClickZhiyeText(self):
        import dlgacceptrewardconfig
        dlgacceptrewardconfig.OpenAcceptRewardDlg()

    
    def OnUpdateQuickAcceptReward(self):
        oModel = self.GetModel()
        bQuickZhiye = oModel.GetZhiyeQuickAcceptReward()
        bQuickXiulian = oModel.GetXiulianQuickAcceptReward()
        iQuickZhiyeType = oModel.GetQuickZhiyeType()
        self.GetView().RefreshQuickAcceptReward(bQuickZhiye, iQuickZhiyeType, bQuickXiulian)

    
    def OnSelectZhiyeBtn(self):
        oModel = self.GetModel()
        bQuickZhiye = oModel.GetZhiyeQuickAcceptReward()
        iQuickZhiyeType = oModel.GetQuickZhiyeType()
        if not bQuickZhiye and not iQuickZhiyeType:
            usermacro.PROMPT_MSG('\xbd\xd0\xb3]\xb8m\xa7\xd6\xb1\xb6\xbb\xe2\xbc\xfa\xa4\xe8\xae\xd7\xab\xe1\xb6i\xa6\xe6\xa4\xc4\xbf\xef')
            return None
        
        oModel.SetZhiyeQuickAcceptReward(not bQuickZhiye)
        nettimewheeldelegate.C2GSChangeQuickAcceptState(timewheeldefine.TIMEWHEEL_ZHIYE, int(not bQuickZhiye))

    
    def OnSelectXiulianBtn(self):
        oModel = self.GetModel()
        bQuickXiulian = oModel.GetXiulianQuickAcceptReward()
        oModel.SetXiulianQuickAcceptReward(not bQuickXiulian)
        nettimewheeldelegate.C2GSChangeQuickAcceptState(timewheeldefine.TIMEWHEEL_XIULIAN, int(not bQuickXiulian))
