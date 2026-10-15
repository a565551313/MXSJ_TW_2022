# pycdc 交叉复核产物 · script.fls entry 1846
# co_filename(原始)='script/mxgame/activity/acteye/view/dlgacteyerank.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1846.pyc (Python 2.5)

'''
\xbb\xf0\xd1\xdb\xbd\xf0\xbe\xa6\xc5\xc5\xd0\xd0\xb0\xf1
'''
import acteyedefine
import interface
import wrapinterface
import combdialog
import slot
g_RankDlg = None

def ModuleReset():
    global g_RankDlg
    if g_RankDlg:
        g_RankDlg.Release()
    
    g_RankDlg = None


def Show():
    global g_RankDlg
    if not g_RankDlg:
        g_RankDlg = CActEyeRankPanel()
    


def CloseWindow():
    global g_RankDlg
    if g_RankDlg:
        g_RankDlg.Release()
    
    g_RankDlg = None


class CActEyeRankPanel(interface.CPanel):
    
    def __init__(self):
        interface.CPanel.__init__(self, interface.DialogPanel)
        self.m_oDialog = CActEyeRankDlg(self)
        (iW, iH) = self.m_oDialog.GetSize()
        self.m_oBackGround = interface.CBoxObject(self, iW, iH, 0, 80)
        self.SetPos(50, 60)

    
    def SetBgShow(self, \xf1\xc0how):
        self.m_oBackGround.SetShow(\xf1\xc0how)

    
    def Release(self, *args):
        interface.CPanel.Release(self, *args)
        if self.m_oDialog:
            self.m_oDialog.Release()
        



class CActEyeRankDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_OnMinClick = 'SS_OnMinClick'
    SS_OnMaxClick = 'SS_OnMaxClick'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/eyes/data.dlg')
        self.m_oDelegate = None
        self.m_oPlayerNameList = []
        self.m_oPlayerKillNumList = []
        self.m_oMyKillNum = None
        self.m_CountDownCmd = None
        self.ssInit()
        self.InitDelegate()
        self.InitDialog()
        self.SetIgnoreEsc(True)

    
    def InitDelegate(self):
        import dgtacteyerank
        self.m_oDelegate = dgtacteyerank.CActEyeRankDelegate(self)

    
    def InitDialog(self):
        for i in xrange(5):
            oPlayerName = self.GetObject('loc_playername%d' % (i + 1))
            oPlayerName.SetText('')
            self.m_oPlayerNameList.append(oPlayerName)
            oLoc = self.GetObject('loc_killnum%d' % (i + 1))
            oPlayerKillNum = interface.CTextObject(self, '', interface.FontLT14, interface.COLOR_3)
            interface.AlignObjects(oPlayerKillNum, oLoc, interface.ALIGN_CENTER)
            self.m_oPlayerKillNumList.append(oPlayerKillNum)
        
        oLoc = self.GetObject('loc_mykillnum')
        self.m_oMyKillNum = interface.CTextObject(self, '', interface.FontLT14, interface.COLOR_3)
        interface.AlignObjects(self.m_oMyKillNum, oLoc, interface.ALIGN_CENTER)
        self.GetObject('btn_max').SetShow(False)
        oLoc = self.GetObject('loc_time')
        self.m_oCountDownText = interface.CTextObject(self, '', interface.FontLT14, interface.COLOR_3)
        interface.AlignObjects(self.m_oCountDownText, oLoc, interface.ALIGN_CENTER)

    
    def RefreshData(self, dInfoList):
        for i in xrange(5):
            self.m_oPlayerKillNumList[i].SetText('')
            self.m_oPlayerNameList[i].SetText('')
        
        for dInfo in dInfoList:
            iRank = dInfo['rank']
            iRank = None if iRank <= 5 else 5
            self.m_oPlayerKillNumList[iRank - 1].SetText(str(dInfo['killnum']))
            self.m_oPlayerNameList[iRank - 1].SetText(dInfo['name'])
        

    
    def SetMyKillNum(self, iMyKillNum):
        self.m_oMyKillNum.SetText(str(iMyKillNum))

    
    def MaxAndMin(self, \xf1\xc0how):
        for obj in self.m_Frames.itervalues():
            obj.SetShow(\xf1\xc0how)
        
        for i in xrange(5):
            self.m_oPlayerNameList[i].SetShow(\xf1\xc0how)
            self.m_oPlayerKillNumList[i].SetShow(\xf1\xc0how)
        
        self.m_oMyKillNum.SetShow(\xf1\xc0how)
        self.m_oCountDownText.SetShow(\xf1\xc0how)
        if \xf1\xc0how:
            self.GetObject('btn_max').SetShow(False)
            self.GetObject('btn_min').SetShow(True)
        else:
            self.GetObject('btn_max').SetShow(True)
            self.GetObject('btn_min').SetShow(False)
        if self.m_oCountDownText:
            self.m_oCountDownText.SetShow(\xf1\xc0how)
        
        self.GetParent().SetBgShow(\xf1\xc0how)

    
    def StartCountDown(self, iSecond):
        self.Release()
        self.m_iSecond = iSecond
        
        def CountDown(obj):
            obj.m_iSecond -= 1
            if obj.m_iSecond <= 0:
                obj.m_iSecond = 0
                CloseWindow()
            
            obj.m_oCountDownText.SetText('%d\xac\xed' % obj.m_iSecond)
            return ()

        self.m_CountDownCmd = self.CreatePyCommand(30, CountDown)

    
    def Release(self, *args):
        if self.m_CountDownCmd:
            self.m_CountDownCmd.Release()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 6:
            self.ssEmit(self.SS_OnMinClick)
        elif iMsgID == 7:
            self.ssEmit(self.SS_OnMaxClick)
