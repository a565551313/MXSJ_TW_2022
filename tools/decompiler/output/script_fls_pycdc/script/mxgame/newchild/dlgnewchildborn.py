# pycdc 交叉复核产物 · script.fls entry 2613
# co_filename(原始)='script/mxgame/newchild/dlgnewchildborn.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2613.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: chenglong
\tdlgnewchildborn\xa3\xba\xd0\xc2\xd7\xd3\xc5\xae--\xcc\xa5\xb6\xf9\xc9\xfa\xb2\xfa
================================================================================
'''
import combdialog
import interface
import combmacro
import timer
import misc
import chatoutput
import ui
g_DeliverDlg = None
g_Effect = None

def ModuleReset():
    global g_DeliverDlg, g_Effect
    g_DeliverDlg = None
    g_Effect = None


def ShowManDialog(iTime):
    global g_DeliverDlg
    g_DeliverDlg = CManDeliver(iTime)


def ShowWomanDialog(iTime):
    global g_DeliverDlg
    g_DeliverDlg = CWomanDeliver(iTime)


def AddTipsTxt(sText):
    if g_DeliverDlg:
        g_DeliverDlg.RefreshBornInfo(sText)
    


def RefreshProgress(iProgress):
    if g_DeliverDlg:
        g_DeliverDlg.RefreshBornProgress(iProgress)
    


def AddTaskCD(iTask, iTime):
    if g_DeliverDlg:
        g_DeliverDlg.CreateTaskCDTimer(iTask, iTime)
    


def RefreshNowTask(iTask):
    if isinstance(g_DeliverDlg, CManDeliver):
        g_DeliverDlg.RefreshNowTask(iTask)
    


def CloseDialog():
    if g_DeliverDlg:
        g_DeliverDlg.OnFinish()
    


def TransTimeToString(iTime):
    '''
\t:param iTime: \xb7\xed\xabe\xb3\xd1\xbel\xac\xed\xbc\xc6(int)
\t:return: \xb7\xed\xabe\xb3\xd1\xbel\xae\xc9\xb6\xa1\xa1]str\xa1^
\t'''
    iMin = iTime / 60
    if iMin < 10:
        sMin = '0' + str(iMin)
    else:
        sMin = str(iMin)
    iSec = iTime % 60
    if iSec < 10:
        sSec = '0' + str(iSec)
    else:
        sSec = str(iSec)
    return sMin + ':' + sSec


def PlayChildBornEffect():
    global g_Effect
    g_Effect = CChildBornEffect()


class CWomanDeliver(combdialog.CCombDialog):
    BORN_PROGRESS_NUM = 40
    XULI_TIME = 3
    STOP_CURSOR_TIME = 20
    
    def __init__(self, iTime):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/newchild/childbornwoman.dlg')
        interface.Center(self)
        self.m_sChatList = []
        self.m_iBornProgress = 0
        self.m_iXuLiTime = 0
        self.m_iStopCursorTime = 0
        self.m_iGameState = 0
        self.m_oXuLiTimer = None
        self.m_oStopCursorTimer = None
        self.m_oMoveCursorTimer = None
        self.m_oBornTimer = None
        self.m_iCursorMoveSpeed = 5
        self.m_ShowBox = None
        self.m_oCursor = self.GetObject('img_cursor')
        (x, y, w, h) = self.GetLocData('frame_cursor')
        self.m_iCursorMinX = x
        self.m_iCursorMaxX = x + w
        self.m_iFinishTime = 0
        self.m_oTipsList = None
        self.InitPlay(iTime)
        self.InitDlg()

    
    def InitDlg(self):
        self.GetObject('txt_timeborn').SetText(TransTimeToString(self.m_iFinishTime))
        self.RefreshBornProgress()
        np|t}ist = [
            'txt_cd',
            'img_cd',
            'txt_cddesc',
            'txt_stop',
            'img_stop',
            'txt_stopdesc']
        for sName in np|t}ist:
            self.GetObject(sName).SetShow(False)
        
        (x, y, w, h) = self.GetLocData('loc_cursorcheck')
        self.m_ShowBox = interface.CBoxObject(self, w, h, 16711680, 136)
        self.m_ShowBox.SetPos(x, y)

    
    def InitPlay(self, iTime):
        self.m_iFinishTime = iTime - misc.GetServerCurrentTime()
        self.m_oBornTimer = timer.Timer(1, misc.Functor(self.RefreshBornTime), -1, self)

    
    def CreateTaskCDTimer(self, iTask, iTime):
        pass

    
    def RefreshBornInfo(self, sText):
        '''
\t\t\xa8\xea\xb7s\xa5\xcd\xb2\xa3\xabH\xae\xa7\xa4\xe5\xa5\xbb
\t\t:param sText: \t\xa4\xe5\xa5\xbb\xb4y\xadz
\t\t'''
        self.m_sChatList.append(sText)
        self.m_oTipsList = combmacro.COUTPUT(chatoutput.COutput, 'loc_tipstxt', self, interface.COLOR_1, 0, self.m_sChatList)
        self.m_oTipsList.SetFontInfo(interface.FontLT14_3, interface.COLOR_1)
        self.m_oTipsList.Refresh()

    
    def RefreshBornProgress(self, iProgress = 0):
        '''
\t\t\xa8\xea\xb7s\xa5\xcd\xb2\xa3\xb6i\xab\xd7
\t\t:param iProgress:\t\xbcW\xa5[\xb6i\xab\xd7\xad\xc8
\t\t'''
        self.m_iBornProgress = iProgress
        self.GetObject('progress_born').SetRate(self.m_iBornProgress * 1000 / self.BORN_PROGRESS_NUM)
        self.GetObject('txt_progress').SetText(str(self.m_iBornProgress) + '/' + str(self.BORN_PROGRESS_NUM))

    
    def RefreshBornTime(self):
        self.m_iFinishTime -= 1
        self.GetObject('txt_timeborn').SetText(TransTimeToString(self.m_iFinishTime))
        if self.m_iFinishTime <= 0:
            self.OnFinish()
        

    
    def RefreshXuLiTime(self):
        self.m_iXuLiTime -= 1
        self.GetObject('txt_cd').SetText(TransTimeToString(self.m_iXuLiTime))
        if self.m_iXuLiTime <= 0:
            self.OnXuLiCD()
        

    
    def RefreshStopCursorTime(self):
        self.m_iStopCursorTime -= 1
        self.GetObject('txt_stop').SetText(TransTimeToString(self.m_iStopCursorTime))
        if self.m_iStopCursorTime <= 0:
            self.OnStopCursor()
        

    
    def RefreshCursorPos(self):
        (iPosx, iPosy) = self.m_oCursor.GetPos()
        iPosx = min(max(iPosx + self.m_iCursorMoveSpeed, self.m_iCursorMinX), self.m_iCursorMaxX)
        self.m_oCursor.SetPos(iPosx, iPosy)
        if iPosx == self.m_iCursorMaxX or iPosx == self.m_iCursorMinX:
            self.m_iCursorMoveSpeed *= -1
        

    
    def OnXuLi(self):
        np|t}ist = [
            'txt_stop',
            'img_stop',
            'txt_stopdesc']
        for sName in np|t}ist:
            self.GetObject(sName).SetShow(True)
        
        self.GetObject('btn_act').SetText('\xb0\xb1\xa4\xee')
        self.m_iStopCursorTime = self.STOP_CURSOR_TIME
        self.GetObject('txt_stop').SetText(TransTimeToString(self.m_iStopCursorTime))
        self.m_iXuLiTime = self.XULI_TIME
        self.GetObject('txt_cd').SetText(TransTimeToString(self.m_iXuLiTime))
        self.m_oStopCursorTimer = timer.Timer(1, misc.Functor(self.RefreshStopCursorTime), -1, self)
        self.m_oMoveCursorTimer = timer.Timer(0.033, misc.Functor(self.RefreshCursorPos), -1, self)
        self.m_iGameState = 1

    
    def OnStopCursor(self):
        np|t}ist = [
            'txt_stop',
            'img_stop',
            'txt_stopdesc']
        for sName in np|t}ist:
            self.GetObject(sName).SetShow(False)
        
        np|t}ist = [
            'txt_cd',
            'img_cd',
            'txt_cddesc']
        for sName in np|t}ist:
            self.GetObject(sName).SetShow(True)
        
        if self.m_oStopCursorTimer:
            self.m_oStopCursorTimer.Release()
        
        self.m_oStopCursorTimer = None
        if self.m_oMoveCursorTimer:
            self.m_oMoveCursorTimer.Release()
        
        self.m_oMoveCursorTimer = None
        oBtn = self.GetObject('btn_act')
        oBtn.SetText('\xc2I\xc0\xbb\xbbW\xa4O')
        oBtn.Enable(False)
        self.m_oXuLiTimer = timer.Timer(1, misc.Functor(self.RefreshXuLiTime), -1, self)
        self.m_iGameState = 2
        (x, y, w, h) = self.GetLocData('loc_cursorcheck')
        (iPosx, _) = self.m_oCursor.GetPos()
        (iCursorWidth, _) = self.m_oCursor.GetSize()
        if iPosx + iCursorWidth - 1 <= iPosx + iCursorWidth - 1:
            pass
        elif iPosx + iCursorWidth - 1 <= x + w:
            self.OnSendSuccess()
        

    
    def OnSendSuccess(self):
        import netnewchild
        netnewchild.C2SWomanGameSuccess()

    
    def OnXuLiCD(self):
        np|t}ist = [
            'txt_cd',
            'img_cd',
            'txt_cddesc']
        for sName in np|t}ist:
            self.GetObject(sName).SetShow(False)
        
        if self.m_oXuLiTimer:
            self.m_oXuLiTimer.Release()
        
        self.m_oXuLiTimer = None
        self.GetObject('btn_act').Enable(True)
        self.m_iGameState = 0

    
    def OnClickActionBtn(self):
        if self.m_iGameState == 0:
            self.OnXuLi()
        elif self.m_iGameState == 1:
            self.OnStopCursor()
        else:
            return None

    
    def OnFinish(self):
        self.ReleaseTimers()
        np|t}ist = [
            'txt_cd',
            'img_cd',
            'txt_cddesc',
            'txt_stop',
            'img_stop',
            'txt_stopdesc']
        for sName in np|t}ist:
            self.GetObject(sName).SetShow(False)
        
        self.m_iGameState = 2
        timer.Timer(2, misc.Functor(self.OnCloseWindow))

    
    def ReleaseTimers(self):
        if self.m_oXuLiTimer:
            self.m_oXuLiTimer.Release()
        
        self.m_oXuLiTimer = None
        if self.m_oStopCursorTimer:
            self.m_oStopCursorTimer.Release()
        
        self.m_oStopCursorTimer = None
        if self.m_oBornTimer:
            self.m_oBornTimer.Release()
        
        self.m_oBornTimer = None
        if self.m_oMoveCursorTimer:
            self.m_oMoveCursorTimer.Release()
        
        self.m_oMoveCursorTimer = None

    
    def OnCloseWindow(self):
        global g_DeliverDlg
        self.ReleaseTimers()
        g_DeliverDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OnCloseWindow()
        elif iMsgID == 5:
            self.OnClickActionBtn()
        



class CManDeliver(combdialog.CCombDialog):
    BORN_PROGRESS_NUM = 40
    TASK_ICON = [
        22306,
        71070,
        23009,
        23005]
    TASK_TIPS = [
        '\xac\xb0\xa7A\xaa\xba\xa9d\xa4l\xa7\xe4\xb1\xf8\xa4\xf2\xa4y\xc0\xbf\xc0\xbf\xc1y',
        '\xb5N\xa4@\xa4U\xbc\xf6\xa4\xf4\xac~\xac~\xa4\xf2\xa4y\xa7a',
        '\xb9\xda\xc6L\xb7|\xa4z\xc2Z\xa4l\xa4k\xaa\xba\xa5X\xa5\xcd\xa1A\xbbP\xb9\xda\xc6L\xbe\xd4\xb0\xab\xb6i\xa6\xe6\xc5X\xbb\xb0',
        '\xb5\xb9\xbbP\xa5\xbf\xa8\xaf\xadW\xa5\xcd\xb2\xa3\xaa\xba\xa9d\xa4l\xa4@\xa8\xc7\xb9\xaa\xc0y\xa7a']
    
    def __init__(self, iTime):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/newchild/childbornman.dlg')
        interface.Center(self)
        self.m_iTaskIdx = 0
        self.m_oTaskIconList = []
        self.m_sChatList = []
        self.m_iFinishTime = 0
        self.m_oBornTimer = None
        self.m_iBornProgress = 0
        self.m_iNowTask = 0
        self.m_oTipsList = None
        self.m_dTaskCDDict = {
            1: { },
            2: { },
            3: { },
            4: { } }
        self.InitPlay(iTime)
        self.InitDlg()

    
    def InitDlg(self):
        self.GetObject('txt_time').SetText(TransTimeToString(self.m_iFinishTime))
        self.RefreshBornProgress(self.m_iBornProgress)
        for iIdx in xrange(4):
            self.GetObject('txt_timetask%d' % (iIdx + 1)).SetShow(False)
        
        self.CreateTaskIcon()
        self.OnRefreshBtnState()

    
    def InitPlay(self, iTime):
        self.m_iFinishTime = iTime - misc.GetServerCurrentTime()
        self.m_oBornTimer = timer.Timer(1, misc.Functor(self.RefreshBornTime), -1, self)

    
    def CreateTaskIcon(self):
        self.m_oTaskIconList = []
        oTaskBG = self.GetObject('box_tasks')
        (px, py) = oTaskBG.GetPos()
        for idx in xrange(4):
            iMsgID = 11 + idx
            (x, y) = oTaskBG.GetImage(0, idx).GetPos()
            sFile = 'item44/%d.igs' % self.TASK_ICON[idx]
            sPack = 'item'
            oTaskIcon = CTaskIcon(self, sFile, sPack, iMsgID)
            oTaskIcon.SetTips(self.TASK_TIPS[idx], iTipsDir = 2)
            oTaskIcon.SetPos(px + x, py + y)
            self.m_oTaskIconList.append(oTaskIcon)
        

    
    def RefreshNowTask(self, iTask):
        '''
\t\t\xa8\xea\xb7s\xb7\xed\xabe\xb1\xb5\xa5\xcd\xa5\xf4\xb0\xc8
\t\t'''
        self.m_iNowTask = iTask
        for idx, oIcon in enumerate(self.m_oTaskIconList):
            if idx + 1 == iTask:
                oIcon.ShowNowImage(True)
                continue
            oIcon.ShowNowImage(False)
        
        self.OnClickTask(iTask)

    
    def RefreshBornInfo(self, sText):
        '''
\t\t\xa8\xea\xb7s\xa5\xcd\xb2\xa3\xabH\xae\xa7\xa4\xe5\xa5\xbb
\t\t:param sText: \t\xa4\xe5\xa5\xbb\xb4y\xadz
\t\t'''
        self.m_sChatList.append(sText)
        self.m_oTipsList = None(None, None, None, None, None, None, None, None, None, None, None, None, None, combmacro.COUTPUT, chatoutput.COutput, 'loc_tipstxt', self, interface.COLOR_1, 0, self.m_sChatList)
        self.m_oTipsList.SetFontInfo(interface.FontLT14_3, interface.COLOR_1)
        self.m_oTipsList.Refresh()

    
    def RefreshBornProgress(self, iProgress):
        '''
\t\t\xa8\xea\xb7s\xa5\xcd\xb2\xa3\xb6i\xab\xd7
\t\t:param iProgress:\t\xb7\xed\xabe\xb6i\xab\xd7\xad\xc8
\t\t'''
        self.m_iBornProgress = iProgress
        self.GetObject('progress_born').SetRate(self.m_iBornProgress * 1000 / self.BORN_PROGRESS_NUM)
        self.GetObject('txt_progress').SetText(str(self.m_iBornProgress) + '/' + str(self.BORN_PROGRESS_NUM))

    
    def SetTaskTimeText(self, iIdx, iTime):
        oText = self.GetObject('txt_timetask%d' % iIdx)
        if iTime < 0:
            oText.SetShow(False)
        else:
            oText.SetShow(True)
            oText.SetText(TransTimeToString(iTime))

    
    def CreateTaskCDTimer(self, iTask, iTime):
        '''
\t\t\xa7\xb9\xa6\xa8\xa5\xf4\xb0\xc8\xab\xe1\xa5\xf4\xb0\xc8CD
\t\t:param iTask: \xa5\xf4\xb0\xc8\xbds\xb8\xb9
\t\t:param iTime: \xa5\xf4\xb0\xc8\xb5\xb2\xa7\xf4\xae\xc9\xb6\xa1\xc2W
\t\t'''
        if iTask in (1, 2, 3, 4):
            iLeftTime = iTime - misc.GetServerCurrentTime()
            if iLeftTime > 0:
                self.m_dTaskCDDict[iTask]['iTime'] = iLeftTime
                if self.m_dTaskCDDict[iTask].get('oTimer', None):
                    self.m_dTaskCDDict[iTask]['oTimer'].Release()
                    self.m_dTaskCDDict[iTask]['oTimer'] = None
                
                self.m_dTaskCDDict[iTask]['oTimer'] = timer.Timer(1, misc.Functor(self.RefreshTaskTimeTxt, iTask), -1, self)
                self.SetTaskTimeText(iTask, iLeftTime)
                self.m_oTaskIconList[iTask - 1].ShowGreyImage(True)
                self.OnRefreshBtnState()
            
        

    
    def RefreshTaskTimeTxt(self, iIdx):
        '''
\t\t\xa8\xea\xb7s\xa5\xf4\xb0\xc8CD
\t\t:param iIdx:\t\xb2\xc4\xb4X\xad\xd3\xa4\xe5\xa5\xbb
\t\t'''
        if iIdx in (1, 2, 3, 4):
            self.m_dTaskCDDict[iIdx]['iTime'] -= 1
            self.SetTaskTimeText(iIdx, self.m_dTaskCDDict[iIdx]['iTime'])
            if self.m_dTaskCDDict[iIdx]['iTime'] < 0:
                self.m_dTaskCDDict[iIdx]['oTimer'].Release()
                self.m_dTaskCDDict[iIdx]['oTimer'] = None
                self.m_oTaskIconList[iIdx - 1].ShowGreyImage(False)
                self.OnRefreshBtnState()
            
        

    
    def RefreshBornTime(self):
        self.m_iFinishTime -= 1
        self.GetObject('txt_time').SetText(TransTimeToString(self.m_iFinishTime))
        if self.m_iFinishTime <= 0:
            self.ReleaseTimers()
        

    
    def OnFinish(self):
        self.ReleaseTimers()
        timer.Timer(2, self.OnCloseWindow)

    
    def OnAddTask(self):
        import netnewchild
        import usermacro
        if self.m_iTaskIdx <= self.m_iTaskIdx:
            pass
        elif self.m_iTaskIdx <= 4:
            netnewchild.C2SGetTask(self.m_iTaskIdx)
        else:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xad\xd3\xa5\xf4\xb0\xc8')

    
    def OnFinishTask(self):
        import netnewchild
        import usermacro
        if self.m_iTaskIdx <= self.m_iTaskIdx:
            pass
        elif self.m_iTaskIdx <= 4:
            netnewchild.C2SFinishTask(self.m_iTaskIdx)
        else:
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4@\xad\xd3\xa5\xf4\xb0\xc8')

    
    def OnClickTask(self, iTask):
        import usermacro
        if self.m_iNowTask != 0 and iTask != self.m_iNowTask:
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xa6\xb3\xa5\xbf\xa6b\xb6i\xa6\xe6\xaa\xba\xa5\xf4\xb0\xc8')
            return None
        
        if self.m_dTaskCDDict.get(iTask, { }).get('iTime', -1) >= 0:
            usermacro.PROMPT_MSG('\xbd\xd0\xb5\xa5\xab\xdd\xa7N\xabo\xae\xc9\xb6\xa1\xb5\xb2\xa7\xf4\xa6A\xbb\xe2\xa8\xfa')
            return None
        
        self.m_iTaskIdx = iTask
        for idx, oTaskIcon in enumerate(self.m_oTaskIconList):
            oTaskIcon.ShowSelectBox(idx + 1 == iTask)
        
        self.OnRefreshBtnState()

    
    def OnRefreshBtnState(self):
        if self.m_iTaskIdx <= self.m_iTaskIdx:
            pass
        elif self.m_iTaskIdx <= 4:
            bEnable = True
            if self.m_dTaskCDDict.get(self.m_iTaskIdx, { }).get('iTime') >= 0:
                bEnable = False
            
            self.GetObject('btn_get').Enable(bEnable)
        else:
            self.GetObject('btn_get').Enable(True)
        self.GetObject('btn_get').Enable(self.m_iNowTask == 0)
        self.GetObject('btn_finish').Enable(self.m_iNowTask != 0)

    
    def ReleaseTimers(self):
        if self.m_oBornTimer:
            self.m_oBornTimer.Release()
        
        self.m_oBornTimer = None
        for dic in self.m_dTaskCDDict.itervalues():
            if dic.get('oTimer'):
                dic['oTimer'].Release()
                dic['oTimer'] = None
                continue
        

    
    def OnCloseWindow(self):
        global g_DeliverDlg
        self.ReleaseTimers()
        g_DeliverDlg = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.OnCloseWindow()
        elif iMsgID == 5:
            self.OnAddTask()
        elif iMsgID == 6:
            self.OnFinishTask()
        elif iMsgID in (11, 12, 13, 14):
            self.OnClickTask(iMsgID - 10)
        



class CTaskIcon(ui.CImageBox):
    
    def __init__(self, oParent, sPath, sDir, iMsgID):
        ui.CImageBox.__init__(self, oParent, sPath, sDir, iMsgID)
        self.m_SelBox = ui.CImage(self, 'common/select.igs', interface.UIPath)
        self.m_SelBox.SetZ(1)
        self.m_SelBox.SetPos(-1, -1)
        self.m_SelBox.SetShow(False)
        self.m_NowImg = ui.CImage(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xbd\xf8\xd0\xd0\xd6\xd0.png', interface.UIPath)
        self.m_NowImg.SetZ(3)
        self.m_NowImg.SetPos(-4, -2)
        self.m_NowImg.SetShow(False)
        self.m_GreyImg = ui.CImage(self, sPath, sDir)
        self.m_GreyImg.SetZ(3)
        self.m_GreyImg.SetGrey()
        self.m_GreyImg.SetShow(False)

    
    def ShowSelectBox(self, bShow):
        self.m_SelBox.SetShow(bShow)

    
    def ShowNowImage(self, bShow):
        self.m_NowImg.SetShow(bShow)

    
    def ShowGreyImage(self, bShow):
        self.m_GreyImg.SetShow(bShow)



class CChildBornEffect(object):
    EFFECT_TIME = 5
    EFFECT_INTERVAL = 0.05
    EFFECT_COUNT = int(EFFECT_TIME / EFFECT_INTERVAL)
    
    def __init__(self):
        self.m_oSpr1 = None
        self.m_oSpr2 = None
        self.m_oTimer = None
        self.m_iCount = 0
        self.Play()

    
    def Play(self):
        import ratio
        oParent = interface.TopmostPanel
        (x, y) = ratio.GetPosBy800x600(400, 135)
        self.m_oSpr1 = interface.CSpriteObject(oParent, 'combdialog4/\xd4\xd3\xcd\xbc/\xd7\xd3\xc5\xae\xcf\xe0\xb9\xd8/babyborn1.spr', interface.UIPath)
        self.m_oSpr1.SetPos(x, y)
        self.m_oSpr2 = interface.CSpriteObject(oParent, 'combdialog4/\xd4\xd3\xcd\xbc/\xd7\xd3\xc5\xae\xcf\xe0\xb9\xd8/babyborn2.spr', interface.UIPath)
        self.m_oSpr2.SetPos(x, y)
        self.m_oSpr2.SetShow(False)
        self.m_oTimer = timer.Timer(self.EFFECT_INTERVAL, self.DoPlayEffect, iRepeat = -1, oRelayObj = self)

    
    def DoPlayEffect(self):
        self.m_iCount += 1
        if self.m_iCount <= 9:
            self.m_oSpr1.SetShow(True)
            self.m_oSpr2.SetShow(False)
            self.m_oSpr1.NextFrame()
        elif self.m_iCount <= self.EFFECT_COUNT:
            self.m_oSpr1.SetShow(False)
            self.m_oSpr2.SetShow(True)
            self.m_oSpr2.NextFrame()
        else:
            self.Stop()

    
    def Stop(self):
        global g_Effect
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = None
        self.m_oSpr1 = None
        self.m_oSpr2 = None
        g_Effect = None
