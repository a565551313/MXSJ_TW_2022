# pycdc 交叉复核产物 · script.fls entry 381
# co_filename(原始)='script/dialog/dlgkeju.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_381.pyc (Python 2.5)

import dlgkejupoetry
import dlgkejuquestion
import interface
import combdialog
import kejudefines
import ui
import timer
import hero
import style
import misc
import simplerankdialog
import map
import permission
g_QuestionDlg = None
g_HuiShiOnTimeDlg = None
g_HuiShiBigRankDlg = None
g_bKejuState = False
g_oResetKejuStateTimer = None
g_bCanSetState = False

def GetTitleByRank(iRank):
    if iRank == 0:
        return ''
    
    if iRank == 1:
        return '\xaa\xac\xa4\xb8'
    
    if iRank == 2:
        return '\xba]\xb2\xb4'
    
    if iRank == 3:
        return '\xb1\xb4\xaa\xe1'
    
    return '\xb6i\xa4h'


def ModuleReset():
    global g_QuestionDlg, g_HuiShiOnTimeDlg, g_HuiShiBigRankDlg, g_bKejuState, g_oResetKejuStateTimer, g_bCanSetState
    g_QuestionDlg = None
    g_HuiShiOnTimeDlg = None
    g_HuiShiBigRankDlg = None
    g_bKejuState = False
    g_oResetKejuStateTimer = None
    g_bCanSetState = False


def ShowTwonExamDlg(iType, dInfo):
    global g_QuestionDlg
    g_QuestionDlg = CTownExamDlg(iType)
    g_QuestionDlg.SetData(dInfo)


def ShowFlySwordDlg(dInfo):
    import mdkejushootgame
    import dlgkejushootgame
    oModel = mdkejushootgame.GetModel()
    oModel.Clear()
    oModel.SetInfo(dInfo)
    oModel.SetSwordNum(dInfo['dContent']['iTimes'])
    dlgkejushootgame.Show()


def RefreshTwonExamDlg(dInfo):
    if not g_QuestionDlg:
        return None
    
    g_QuestionDlg.RefreshDialog(dInfo)


def CloseExamDialog():
    global g_QuestionDlg
    g_QuestionDlg = None


def IsShowProviceExamDlg():
    if g_QuestionDlg:
        pass
    return isinstance(g_QuestionDlg, CProvinceExamDlg)


def ShowProvinceExamDlg(iType, dInfo):
    global g_QuestionDlg
    g_QuestionDlg = CProvinceExamDlg(iType)
    g_QuestionDlg.SetData(dInfo)


def RefreshHuiShi(dInfo):
    if g_QuestionDlg:
        g_QuestionDlg.RefreshHuiShi(dInfo)
    


def RefreshHuiShiJNNum(dInfo):
    if g_QuestionDlg:
        g_QuestionDlg.RefreshHuiShiJNNum(dInfo)
    


def OpenHuiShiOnTimeRankDlg(lstRankInfo, dMyRankInfo, iOpenDlg):
    global g_HuiShiOnTimeDlg
    if iOpenDlg == 1:
        if g_HuiShiOnTimeDlg:
            g_HuiShiOnTimeDlg.ShowBig()
        else:
            g_HuiShiOnTimeDlg = CProvinceOnTimeRankDialog()
    
    if not g_HuiShiOnTimeDlg:
        return None
    
    rankList = []
    for iId, dInfo in enumerate(lstRankInfo):
        iUsedTime = dInfo['iUseTime']
        sTime = '%d\xa4\xc0%d\xac\xed' % (iUsedTime / 60, iUsedTime % 60)
        lstInfo = [
            str(iId + 1),
            dInfo['sName'],
            str(dInfo['iScore']),
            sTime]
        rankList.append(lstInfo)
    
    g_HuiShiOnTimeDlg.SetRankData(rankList)
    iMyRank = dMyRankInfo['iRank']
    iUsedTime = dMyRankInfo['iUseTime']
    sTime = '%d\xa4\xc0%d\xac\xed' % (iUsedTime / 60, iUsedTime % 60)
    sMyRank = None if iMyRank == 0 else str(iMyRank)
    lstInfo = [
        sMyRank,
        hero.GetProp('m_Name', ''),
        str(dMyRankInfo['iScore']),
        sTime]
    g_HuiShiOnTimeDlg.SetMyRankData(lstInfo)


def OpenHuiShiBigRankDlg(lstRankInfo, dMyRankInfo):
    global g_HuiShiBigRankDlg
    if not g_HuiShiBigRankDlg:
        g_HuiShiBigRankDlg = CHuiShiRankDialog(interface.DialogPanel)
    
    lstTitle = [
        '\xb1\xc6\xa6W',
        '\xa6W\xa6r',
        '\xb7|\xb8\xd5\xa4\xc0\xbc\xc6',
        '\xb7|\xb8\xd5\xa5\xce\xae\xc9',
        '\xba\xd9\xbf\xd7']
    lstColumnWidth = [
        50,
        150,
        70,
        100,
        80]
    lstAllRank = []
    for iId, dInfo in enumerate(lstRankInfo):
        iUsedTime = dInfo['iUseTime']
        sTime = '%d\xa4\xc0%d\xac\xed' % (iUsedTime / 60, iUsedTime % 60)
        lstInfo = [
            iId + 1,
            (dInfo['tPhoto'], dInfo['sName'], dInfo['iPlayerID']),
            str(dInfo['iScore']),
            sTime,
            GetTitleByRank(iId + 1)]
        lstAllRank.append(lstInfo)
    
    iMyRank = dMyRankInfo['iRank']
    iUsedTime = dMyRankInfo['iUseTime']
    sTime = '%d\xa4\xc0%d\xac\xed' % (iUsedTime / 60, iUsedTime % 60)
    lstMyRank = [
        iMyRank,
        (dMyRankInfo['tPhoto'], hero.GetProp('m_Name', ''), hero.GetHeroID()),
        str(dMyRankInfo['iScore']),
        sTime,
        GetTitleByRank(iMyRank)]
    g_HuiShiBigRankDlg.SetRankData(lstTitle, lstColumnWidth, lstMyRank, lstAllRank)


def CloseHuiShiOnTimeDlg():
    global g_HuiShiOnTimeDlg
    g_HuiShiOnTimeDlg = None


def CanSetKejuState(bCanSetState):
    global g_bCanSetState
    g_bCanSetState = bCanSetState


def CheckHasKejuTask():
    if g_bCanSetState:
        SetInKejuState(True)
    else:
        SetInKejuState(False)


def IsInKejuState():
    return g_bKejuState == True


def ResetKejuState():
    global g_bKejuState, g_bCanSetState
    g_bKejuState = False
    g_bCanSetState = False


def ReleaseStateTimer():
    global g_oResetKejuStateTimer
    if g_oResetKejuStateTimer:
        g_oResetKejuStateTimer.Release()
        g_oResetKejuStateTimer = None
    


def SetInKejuState(bState):
    global g_bKejuState, g_oResetKejuStateTimer
    g_bKejuState = bState
    if bState:
        ReleaseStateTimer()
        g_oResetKejuStateTimer = timer.Timer(1, ResetKejuState)
    else:
        ReleaseStateTimer()


class CTownExamDlg(combdialog.CCombDialog):
    
    def __init__(self, iType):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/keju/townexam_new.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_oPassExamHook = None
        self.m_oDelayCloseTimer = None
        self.m_iLeftTime = 0
        self.m_oTimer = None
        import mgrschedule
        import mdnewschedule
        if permission.IsNewSchedule():
            mdnewschedule.GetNewScheduleModel().SetLimitTimeActivityActive(1019)
        else:
            mgrschedule.GetMgr().SetLimitTimeActivityActive(1019)
        if iType == kejudefines.TYPE_QUESTION:
            self.m_oSubPart = dlgkejuquestion.CTownQuestionPart(self, self.CloseWindow)
        else:
            self.m_oSubPart = dlgkejupoetry.CKejuPeotryDialog(self, self.CloseWindow, False)

    
    def SetData(self, dInfo):
        self.m_bIsWaiguaCheck = dInfo.get('bIsWaiguaCheck', False)
        self.m_oSubPart.SetData(dInfo)
        self.RefreshDialog(dInfo)
        self.RefreshWaigua()

    
    def RefreshDialog(self, dInfo):
        iScore = dInfo['iScore']
        iExp = dInfo['iExp']
        self.GetObject('txt_exp1').SetText(str(iExp))
        if iScore >= 80:
            if not self.m_oPassExamHook:
                self.m_oPassExamHook = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xb9\xb4.png', interface.UIPath)
                interface.AlignObjects(self.m_oPassExamHook, self.GetObject('loc_pass_exam_gou'), interface.ALIGN_CENTER_MIDDLE)
            
            self.SetShowObject('tips_point', False)
            self.GetObject('txt_point1').SetText('\xa6\xa8\xa5\\\xae\xca\xaf\xc5\xb7|\xb8\xd5')
        else:
            self.m_oPassExamHook = None
            self.SetShowObject('tips_point', True)
            self.GetObject('txt_point1').SetText('%d/80' % iScore)
        self.m_oSubPart.RefreshData(dInfo)

    
    def RefreshWaigua(self):
        if self.m_bIsWaiguaCheck:
            self.GetObject('mainframe').ChgCaptionTxt('\xb8\xd6\xb5\xfc\xc5\xe7\xb5\xfd')
            for sUI in ('txt_point', 'txt_point1', 'tips_point', 'txt_exp', 'txt_exp1', 'm_CloseBtn'):
                self.SetShowObject(sUI, False)
            
            self.m_iLeftTime = 30
            self.ShowTimeLeft()
            if not self.m_oTimer:
                self.m_oTimer = timer.Timer(1, self.ShowTimeLeft, -1, self)
            
            self.SetIgnoreEsc(True)
        

    
    def ShowTimeLeft(self):
        self.m_iLeftTime -= 1
        self.m_oTimeStr = interface.CTextObject(self, '\xad\xcb\xadp\xae\xc9:%s' % self.m_iLeftTime, interface.FontLT14_3, interface.COLOR_285)
        self.m_oTimeStr.SetPos(*self.GetObject('txt_exp1').GetPos())
        if self.m_iLeftTime <= 0:
            self.m_oSubPart.Commit(0, [])
            self.CloseWindow()
        

    
    def RightUp(self):
        if self.m_bIsWaiguaCheck:
            return None
        
        combdialog.CCombDialog.RightUp(self)

    
    def CloseWindow(self):
        global g_QuestionDlg
        g_QuestionDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        



class CProvinceExamDlg(combdialog.CCombDialog):
    
    class MyButton(interface.CImagesObject, interface.CClickObject):
        
        def __init__(self, parent, filename, x, y, msgid = 0, tips = None):
            interface.CImagesObject.__init__(self, parent, filename, 'item')
            interface.CClickObject.__init__(self, msgid)
            self.m_TipsStr = tips
            self.m_FName = filename
            self.m_DisableTips = None
            self.SetZ(2)

        
        def SetRemainNumber(self, remainNumber):
            txt = '%d' % remainNumber
            self.m_RemainTxt = number_txt = interface.CTextObject(self, txt, interface.FontLT12_1, 16777215, 1)
            ox = None if self.m_MsgID == 16 else 0
            (w, h) = (44, 44)
            (sw, sh) = number_txt.GetSize()
            number_txt.SetPos(w - sw, h - sh)

        
        def LeftDown(self):
            self.SetFrame(1)
            interface.CClickObject.LeftDown(self)

        
        def LeftUp(self):
            interface.CClickObject.LeftUp(self)

        
        def Enter(self):
            self.SetLight(12)
            import wrapinterface
            self.m_TipsObj = wrapinterface.CTextTips(None, -1, self.m_TipsStr, interface.FontLT14_3, direct = 1)
            self.m_TipsObj.SetOwner(None)

        
        def Leave(self):
            self.SetLight(8)
            self.m_TipsObj = None

        
        def Enable(self, enable):
            if enable:
                self.SetLight(8)
            else:
                self.SetLight(4)
            interface.CClickObject.Enable(self, enable)

        
        def FlashItself(self, escape, duration = 60):
            
            def flash(\xd4bj, frame, times):
                framecount = \xd4bj.FrameAmount()
                if framecount <= 1 or times == 0:
                    \xd4bj.SetFrame(0)
                    return None
                
                \xd4bj.SetFrame(frame)
                return ((frame + 1) % framecount, times - 1)

            if hasattr(self, 'm_FlashCommand') and self.m_FlashCommand:
                self.m_FlashCommand.Release()
            
            self.m_FlashCommand = self.CreatePyCommand(escape, flash, 0, duration * 30 / escape)

        
        def OnMessage(self, msgid):
            if msgid == self.m_MsgID and getattr(self, 'm_DisableTips', None):
                import usermacro
                usermacro.PROMPT_MSG(self.m_DisableTips)
            else:
                self.GetParent().OnMessage(msgid)


    
    def __init__(self, iType):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/keju/provinceexam_new.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        map.StopMove()
        self.m_iUsedTime = 0
        self.m_dDataDct = { }
        self.m_iTrueNum = 0
        self.m_iScore = 0
        self.m_oCloseTimer = None
        self.m_oUpdateUseTimeTimer = None
        self.m_iGameType = iType
        if iType == kejudefines.TYPE_QUESTION:
            self.m_oSubPart = dlgkejuquestion.CHuishiKejuQuestionPart(self, self.CloseWindow)
        else:
            self.m_oSubPart = dlgkejupoetry.CKejuPeotryDialog(self, self.CloseWindow, True)

    
    def SetData(self, dInfo):
        self.m_dDataDct = dInfo['dContent']
        self.m_iTrueNum = dInfo['iTrueNum']
        self.m_iScore = dInfo['iScore']
        self.m_iUsedTime = dInfo['iUsedTime']
        iExp = dInfo['iExp']
        self.UpdateUseTimeText()
        self.CreateJinNang(self.m_dDataDct['jn'])
        self.GetObject('txt_exp').SetText(str(iExp))
        self.GetObject('txt_point1').SetText(str(self.m_iScore))
        oTxt = self.GetObject('txt_reward')
        (x, y, w, h) = self.GetLocData('btn_reward')
        if self.m_iTrueNum < 10:
            self.m_oRewardView = interface.CViewportObject(self, w + 10, h * (10 - self.m_iTrueNum) / 10)
            self.m_oRewardView.SetPos(*self.GetObject('btn_reward').GetPos())
            self.m_oRewardView.SetZ(10)
            self.m_oRewardImg = ui.CImage(self.m_oRewardView, 'combdialog4/\xd4\xd3\xcd\xbc/dengjilibao.png', interface.UIPath)
            oTxt.ReplaceText({
                '$num': str(self.m_iTrueNum) })
        else:
            oTxt.SetText('\xa7\xb9\xa6\xa8\xb7|\xb8\xd5\xab\xe1\xa6\xdb\xb0\xca\xb5o\xa9\xf1')
        self.m_oSubPart.SetData(dInfo)

    
    def RefreshHuiShi(self, dInfo):
        '''
\t\t\xa8\xea\xb7s\xb7|\xb8\xd5\xac\xc9\xad\xb1
\t\tdInfo = {
\t\t\tiTrueNum:\t\xa5\xbf\xbdT\xc3D\xbc\xc6
\t\t\tiUseNum: \t\xc0\xb0\xac\xa3\xc0A\xc5n\xb3\xd1\xbel\xa6\xb8\xbc\xc6
\t\t\tiExp:\t\t\xb2\xd6\xadp\xb8g\xc5\xe7
\t\t\tiSelect:\t\t\xbf\xef\xbe\xdc\xaa\xba\xbf\xef\xb6\xb5\xa1]\xa8\xb8\xb4c\xc0A\xc5n\xacO\xaaA\xb0\xc8\xbe\xb9\xc0\xb0\xbf\xef\xa1^
\t\t\tiScore:\t\t\xb7|\xb8\xd5\xa4\xc0\xbc\xc6
\t\t}
\t\t:return:
\t\t'''
        iTrueNum = dInfo['iTrueNum']
        iUseNum = dInfo['iUseNum']
        iExp = dInfo['iExp']
        iScore = dInfo['iScore']
        bCorrect = self.m_iTrueNum < iTrueNum
        fDelayTime = None if bCorrect else 2.5
        if not bCorrect:
            self.m_iUsedTime += 25
            self.UpdateUseTimeText()
        
        self.m_iTrueNum = iTrueNum
        self.m_JnDct[3].SetRemainNumber(iUseNum)
        self.GetObject('txt_exp').SetText(str(iExp))
        oTxt = self.GetObject('txt_reward')
        (x, y, w, h) = self.GetLocData('btn_reward')
        if self.m_iTrueNum < 10:
            self.m_oRewardImg = None
            self.m_oRewardView = None
            self.m_oRewardView = interface.CViewportObject(self, w + 10, h * (10 - self.m_iTrueNum) / 10)
            self.m_oRewardView.SetPos(*self.GetObject('btn_reward').GetPos())
            self.m_oRewardView.SetZ(10)
            self.m_oRewardImg = ui.CImage(self.m_oRewardView, 'combdialog4/\xd4\xd3\xcd\xbc/dengjilibao.png', interface.UIPath)
            oTxt.ReplaceText({
                '$num': str(self.m_iTrueNum) })
        else:
            oTxt.SetText('\xa7\xb9\xa6\xa8\xb7|\xb8\xd5\xab\xe1\xa6\xdb\xb0\xca\xb5o\xa9\xf1')
        self.m_iScore = iScore
        self.GetObject('txt_point1').SetText(str(iScore))
        if self.m_oCloseTimer:
            self.m_oCloseTimer.Release()
            self.m_oCloseTimer = None
        
        self.m_oCloseTimer = timer.Timer(fDelayTime, self.CloseWindow)
        self.m_oSubPart.RefreshData(dInfo)

    
    def RefreshHuiShiJNNum(self, dInfo):
        iUseNum = dInfo['iUseNum']
        self.m_JnDct[3].SetRemainNumber(iUseNum)

    
    def UpdateUseTimeText(self):
        self.GetObject('txt_time1').SetText('%d\xa4\xc0%d\xac\xed' % (self.m_iUsedTime / 60, self.m_iUsedTime % 60))
        self.m_iUsedTime += 1
        if not self.m_oUpdateUseTimeTimer:
            self.m_oUpdateUseTimeTimer = timer.Timer(1, self.UpdateUseTimeText, -1, self)
        

    
    def CreateJinNang(self, remainDct):
        idx2shape = {
            0: 30138,
            1: 30155,
            2: 30148,
            3: 30023 }
        idx2tipstr = {
            0: '\xc2I\xc0\xbb\xa8\xcf\xa5\xce\xb4\xbc\xbcz\xc0A\xc5n\xa1A\xb1q\xbf\xf9\xbb~\xaa\xba\xbf\xef\xb6\xb5\xa4\xa4\xa5h\xb0\xa3\xa4@\xad\xd3',
            1: '\xc2I\xc0\xbb\xa8\xcf\xa5\xce\xa8\xb8\xb4c\xc0A\xc5n\xa1A\xa6\xb350%\xaa\xba\xb7\xa7\xb2v\xbf\xef\xbe\xdc\xa5\xbf\xbdT\xb5\xaa\xae\xd7\xa1A50%\xaa\xba\xb7\xa7\xb2v\xbf\xef\xbe\xdc\xbf\xf9\xbb~\xb5\xaa\xae\xd7',
            2: '\xc2I\xc0\xbb\xa8\xcf\xa5\xce\xb5L\xa6r\xc0A\xc5n\xa1A\xbbP\xa1u\xb5L\xa6r\xa8\xcf\xaa\xcc\xa1v\xb6i\xa6\xe6PK\xa1A\xc2\xf4\xc3\xf6\xae\xca\xaf\xc5\xa4U\xa4@\xc3\xf6',
            3: '\xc2I\xc0\xbb\xa5i\xb1N\xc3D\xa5\xd8\xb5o\xb0e\xa6\xdc\xc0\xb0\xac\xa3' }
        self.m_JnDct = { }
        for idx, remain in remainDct.items():
            (x, y) = self.GetObject('jn%d' % idx).GetPos()
            (w, h) = self.GetObject('jn%d' % idx).GetSize()
            tipsStr = idx2tipstr[idx]
            filePath = 'item44/%d.igs' % idx2shape[idx]
            \xd4bj = CProvinceExamDlg.MyButton(self, filePath, x, y, idx + 14, tipsStr)
            (ow, oh) = \xd4bj.GetSize()
            ox = None if idx == 2 else 0
            oy = None if idx == 3 else 0
            \xd4bj.SetPos((w - ow) / 2 + x + ox, (h - oh) / 2 + y + oy)
            \xd4bj.SetRemainNumber(remain)
            if self.m_iGameType == kejudefines.TYPE_POETRY and idx in (0, 1):
                \xd4bj.Enable(False)
            elif remain == 0:
                \xd4bj.Enable(False)
            elif idx == 0 and len(self.m_dDataDct['answerDct']) < 3:
                \xd4bj.Enable(False)
            
            self.m_JnDct[idx] = \xd4bj
        

    
    def OnGetReward(self):
        import usermacro
        if self.m_iTrueNum < 10:
            usermacro.PROMPT_MSG('\xbb\xdd\xadn\xb5\xaa\xb9\xef10\xc3D\xa4~\xaf\xe0\xb6}\xb1\xd2\xc2\xa7\xb2\xb0')
        else:
            usermacro.PROMPT_MSG('\xa7\xb9\xa6\xa8\xb7|\xb8\xd5\xab\xe1\xa6\xdb\xb0\xca\xb5o\xa9\xf1')

    
    def CloseWindow(self):
        global g_QuestionDlg
        g_QuestionDlg = None

    
    def OnMessage(self, iMsgid):
        if iMsgid == 1:
            self.CloseWindow()
        
        if iMsgid == 2:
            self.OnGetReward()
        
        if iMsgid <= iMsgid:
            pass
        elif None:
            self.m_oSubPart.UseJN(iMsgid - 10)
        



class CProvinceOnTimeRankBar(interface.CContainerObject, interface.CDialogBase):
    
    def __init__(self, oClickCB):
        interface.CContainerObject.__init__(self, interface.DialogPanel)
        interface.CDialogBase.__init__(self)
        self.MessageProcess()
        self.m_oText = None
        self.m_oBgList = []
        self.m_oClickCB = oClickCB
        self.InitView()

    
    def InitView(self):
        self.m_MaxBtn = interface.CButton(self, style.GetStr('dlgkeju.CProvinceOnTimeRankBar', 'data_max_btn_path'), 0, 0, 1)
        (iBtnW, iBtnH) = self.m_MaxBtn.GetSize()
        self.m_oText = interface.CRichTextObject(self, 300, interface.FontLT14_3, '\xac\xec\xc1|\xb7|\xb8\xd5\xb1\xc6\xa6W', interface.COLOR_3)
        (iTextW, iTextH) = self.m_oText.GetSize()
        iW = iBtnW + iTextW + 20
        iH = iTextH + 20
        self.m_oBgList = self.CreateBg(-4, -4, iW, iH)
        iOffsetY = style.GetInt('dlgkeju.CProvinceOnTimeRankBar', 'data_trun_txt_offsety')
        self.m_oText.SetPos(iBtnW + 4, iOffsetY)
        self.SetSize(iW, iH + iOffsetY)
        iOffsetY += style.GetInt('dlgkeju.CProvinceOnTimeRankBar', 'data_btn_offset')
        self.m_MaxBtn.SetPos(0, iOffsetY)

    
    def SetPos(self, x, y):
        interface.CContainerObject.SetPos(self, x, y)

    
    def SetSize(self, w, h):
        self.m_Width = w
        self.m_Height = h

    
    def GetSize(self):
        return (self.m_Width, self.m_Height)

    
    def GetOffsetPos(self):
        img = self.m_oBgList[0]
        (imgX, imgY) = img.GetPos()
        return (imgX, imgY)

    
    def Hold(self):
        interface.CDialogBase.Hold(self)
        interface.ResetPosition(self)

    
    def CreateBg(self, iX, iY, iW, iH):
        iSpace = iX
        lstResult = []
        oImg = ui.CImage(self, style.GetPath('dialog/friend/bar01.igs'), interface.UIPath)
        oImg.SetZ(-1)
        oImg.SetPos(iX, iY)
        (iImgW, _) = oImg.GetSize()
        iSpace += iImgW
        lstResult.append(oImg)
        oImg = interface.CCutImagesObject(self, style.GetPath('dialog/friend/bar02.igs'), interface.UIPath)
        oImg.SetZ(-1)
        oImg.SetSize(iW - iImgW - 4, iH)
        oImg.SetPos(iSpace, iY)
        iSpace += oImg.GetSize()[0]
        lstResult.append(oImg)
        oImg = ui.CImage(self, style.GetPath('dialog/friend/bar03.igs'), interface.UIPath)
        oImg.SetZ(-1)
        oImg.SetPos(iSpace, iY)
        lstResult.append(oImg)
        return lstResult

    
    def OnMessage(self, iMsgId):
        if iMsgId == 1:
            if self.m_oClickCB:
                self.m_oClickCB()
            
        



class CProvinceOnTimeRankDialog(combdialog.CCombDialog):
    RANK_LOC_NAME = ('loc_first', 'loc_secend', 'loc_third')
    RANK_FIELD_WIDTH = (45, 95, 75, 80)
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/keju/ontime.dlg')
        interface.g_DialogList.pop()
        self.m_dRankListText = { }
        self.m_lstMyRankText = None
        self.m_oMiniBar = CProvinceOnTimeRankBar(misc.Functor(self.ShowBig))
        self.m_oMiniBar.SetShow(False)
        self.InitPos()
        self.m_oMiniBar.SetPos(*self.GetPos())
        self.m_oCheckCloseTimer = timer.Timer(1, self.OnAutoCheckClose, -1, self)

    
    def InitPos(self):
        import ratio
        iX = 50
        iY = 142
        (iW, iH) = self.GetSize()
        if iX < 0:
            iX = 0
        elif iX > ratio.WINDOW_WIDTH - iW:
            iX = ratio.WINDOW_WIDTH - iW
        
        if iY < 0:
            iY = 0
        elif iY > ratio.WINDOW_HEIGHT - iH:
            iY = ratio.WINDOW_HEIGHT - iH
        
        self.SetPos(iX, iY)

    
    def OnAutoCheckClose(self):
        import mdmxtask
        if 1029 not in mdmxtask.GetMXTaskInfoMgr().GetAllTask():
            CloseHuiShiOnTimeDlg()
        

    
    def SetRankData(self, lstInfo):
        self.m_dRankListText = { }
        for iRank in xrange(3):
            oLoc = self.GetObject(self.RANK_LOC_NAME[iRank])
            (iW, iH) = oLoc.GetSize()
            (iX, iY) = oLoc.GetPos()
            lstText = []
            if iRank < len(lstInfo):
                sInfoList = lstInfo[iRank]
            else:
                sInfoList = [
                    '\xb5\xea\xa6\xec\xa5H\xab\xdd',
                    '\xb5\xea\xa6\xec\xa5H\xab\xdd',
                    '\xb5\xea\xa6\xec\xa5H\xab\xdd',
                    '\xb5\xea\xa6\xec\xa5H\xab\xdd']
            for iId, sField in enumerate(sInfoList):
                oText = ui.CTextObjext(self, self.RANK_FIELD_WIDTH[iId], iH, sField, interface.FontLT14, interface.COLOR_3, iAlign = interface.ALIGN_CENTER_MIDDLE)
                oText.SetPos(iX + sum(self.RANK_FIELD_WIDTH[:iId]), iY)
                lstText.append(oText)
            
            self.m_dRankListText[iRank] = lstText
        

    
    def SetMyRankData(self, lstInfo):
        oLoc = self.GetObject('loc_player')
        (iW, iH) = oLoc.GetSize()
        (iX, iY) = oLoc.GetPos()
        self.m_lstMyRankText = []
        for iId, sField in enumerate(lstInfo):
            oText = ui.CTextObjext(self, self.RANK_FIELD_WIDTH[iId], iH, sField, interface.FontLT14, interface.COLOR_3, iAlign = interface.ALIGN_CENTER_MIDDLE)
            oText.SetPos(iX + sum(self.RANK_FIELD_WIDTH[:iId]), iY)
            self.m_lstMyRankText.append(oText)
        

    
    def ShowMini(self):
        self.m_oMiniBar.SetPos(*self.GetPos())
        self.m_oMiniBar.SetShow(True)

    
    def ShowBig(self):
        self.m_oMiniBar.SetShow(False)
        self.SetPos(*self.m_oMiniBar.GetPos())
        self.SetShow(True)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            CloseHuiShiOnTimeDlg()
        elif iMsgID == 6:
            self.ShowMini()
            self.SetShow(False)
        

    
    def CloseWindow(self):
        pass



class CHuiShiRankDialog(simplerankdialog.CSimpleRankDialog):
    
    def GetUIPath(self):
        return 'dialog/keju/total.dlg'

    
    def CloseWindow(self):
        global g_HuiShiBigRankDlg
        g_HuiShiBigRankDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        



class CFrameButton(interface.CClickBox):
    ENTERLIGHT = 9
    DOWNLIGHT = 6
    NORMALLIGHT = 8
    IDX2ABC = {
        0: 'A',
        1: 'B',
        2: 'C' }
    
    def __init__(self, parent, path, w, h, txt, idx, msgid):
        interface.CClickBox.__init__(self, parent, 0, 0, 0, 0)
        self.m_Path = path
        self.CreateImages(w, h, path)
        self.SetSize(w, h)
        self.m_Msgid = msgid

    
    def GetType(self):
        import style
        iType = style.GetInt('dlgkeju.CFrameButton', 'data_type')
        return iType

    
    def CreateImages(self, w, h, path):
        self.m_Imagess = ui.CFrame(self, w, h, path)

    
    def SetText(self, idx, txt):
        import style
        (x, y) = (10, 15)
        ABC = self.IDX2ABC.get(idx, '')
        self.m_ABC = interface.CTextObject(self, ABC, interface.FontLT14E, [
            6737151,
            3355443,
            10066329], 0)
        self.m_ABC.SetPos(x, y)
        self.m_ABC.SetZ(10)
        (ABCWidth, ABCHight) = self.m_ABC.GetSize()
        if interface.IsStyle2():
            iColor = 16777215
        else:
            iColor = interface.COLOR_55
        self.m_Txt = interface.CRichTextObject(self, 160, interface.FontLT14, txt, iColor)
        iOffsetY = style.GetInt('dlgkeju.CFrameButton', 'data_font_y')
        self.m_Txt.SetPos(x + ABCWidth + 10, y + iOffsetY)
        self.m_Txt.SetZ(10)

    
    def GetSize(self):
        return self.m_Size

    
    def SetAlpha(self, alpha):
        self.m_Imagess.SetAlpha(alpha)

    
    def SetSize(self, w, h):
        interface.CClickBox.SetSize(self, w, h)
        self.m_Size = (w, h)
        self.m_Imagess = ui.CFrame(self, w, h, self.m_Path)

    
    def Enter(self):
        interface.CClickBox.Enter(self)
        self.SetLight(self.ENTERLIGHT)

    
    def LeftDown(self):
        interface.CClickBox.LeftDown(self)
        self.SetLight(self.DOWNLIGHT)

    
    def LeftUp(self):
        interface.CClickBox.LeftUp(self)
        self.SetLight(self.ENTERLIGHT)
        par = self.GetParent()
        if par:
            par.OnMessage(self.m_Msgid)
        

    
    def Leave(self):
        interface.CClickBox.LeftUp(self)
        self.SetLight(self.NORMALLIGHT)

    
    def SetLight(self, light):
        self.m_Imagess.SetLight(light)
