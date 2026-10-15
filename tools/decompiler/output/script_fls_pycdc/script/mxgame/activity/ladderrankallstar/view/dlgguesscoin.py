# pycdc 交叉复核产物 · script.fls entry 682
# co_filename(原始)='script/mxgame/activity/ladderrankallstar/view/dlgguesscoin.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_682.pyc (Python 2.5)

import combdialog
import interface
import slot
import ladderrankallstardefine

def ShowGuessVoteDlg():
    CGuessVoteDlg.OpenUI()


def GetGuessVoteDlg():
    return CGuessVoteDlg.IsOpen()


def CloseGuessVoteDlg():
    CGuessVoteDlg.CloseUI()


def ShowGuessCoinDlg():
    CGetGuessCoinDlg.OpenUI()


class CGuessVoteDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_OnGuessBtnClick = 'OnGuessBtnClick '
    SS_OpenGetGuessMoneyDlg = 'SS_OpenGetGuessMoneyDlg '
    sUIName = 'dialog4/allstarrank/allstar/guess.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.m_DelegateList = []
        self.ssInit()
        self.m_oNumEditA = None
        self.m_oNumEditB = None
        interface.Center(self)
        self.InitDlg()
        self.InitDelegate()

    
    def InitDelegate(self):
        import dgtguesscoin
        self.m_DelegateList = [
            dgtguesscoin.CGuessVoteDgt(self)]

    
    def SetTeamInfo(self, lstInfo):
        (sNameA, iNumA, sServerNameA, iSupportTicketA, sNameB, iNumB, sServerNameB, iSupportTicketB) = lstInfo
        self.UpdateLeftTeamInfo(iNumA, sNameA)
        self.UpdateRightTeamInfo(iNumB, sNameB)
        self.UpdateLeftTeamServer(sServerNameA)
        self.UpdateRightTeamServer(sServerNameB)
        self.UpdateSupport(iSupportTicketA, iSupportTicketB)

    
    def UpdateLeftTeamInfo(self, iNumA, sNameA = None):
        if sNameA:
            self.GetObject('txt_nameA').SetText(sNameA)
            self.GetObject('txt_nameAA').SetText(sNameA)
        
        self.GetObject('txt_numA').SetText('\xa4w\xc4v\xb2q:%d' % iNumA)
        bShow = iNumA > 0
        self.SetShowObject('txt_nameA', bShow)
        self.SetShowObject('txt_nameAA', not bShow)
        self.SetShowObject('txt_ServerA', bShow)
        self.SetShowObject('txt_ServerAA', not bShow)
        self.SetShowObject('txt_numA', bShow)

    
    def UpdateRightTeamInfo(self, iNumB, sNameB = None):
        if sNameB:
            self.GetObject('txt_nameB').SetText(sNameB)
            self.GetObject('txt_nameBB').SetText(sNameB)
        
        self.GetObject('txt_numB').SetText('\xa4w\xc4v\xb2q:%d' % iNumB)
        bShow = iNumB > 0
        self.SetShowObject('txt_nameB', bShow)
        self.SetShowObject('txt_nameBB', not bShow)
        self.SetShowObject('txt_ServerB', bShow)
        self.SetShowObject('txt_ServerBB', not bShow)
        self.SetShowObject('txt_numB', bShow)

    
    def UpdateRightTeamServer(self, sServerNameR):
        self.GetObject('txt_ServerB').SetText(sServerNameR)
        self.GetObject('txt_ServerBB').SetText(sServerNameR)

    
    def UpdateLeftTeamServer(self, sServerNameL):
        self.GetObject('txt_ServerA').SetText(sServerNameL)
        self.GetObject('txt_ServerAA').SetText(sServerNameL)

    
    def UpdateSupport(self, iSupportTicketA, iSupportTicketB):
        iNum = iSupportTicketA + iSupportTicketB
        if iNum == 0:
            iPercentA = 0
            iPercentB = 0
        else:
            iPercentA = int((float(iSupportTicketA) / iNum) * 100)
            iPercentB = 100 - iPercentA
        self.GetObject('txt_support1').SetText('\xa4\xe4\xab\xf9\xb2v:%s%%' % iPercentA)
        self.GetObject('txt_support2').SetText('\xa4\xe4\xab\xf9\xb2v:%s%%' % iPercentB)

    
    def SetTime(self, sTime):
        self.GetObject('txt_time').SetText(sTime)

    
    def SetStage(self, sStage):
        self.GetObject('txt_match').SetText(sStage)

    
    def SetGuessMoney(self, iMoney):
        self.GetObject('text_money').SetText(str(iMoney))

    
    def SetMaxGuessMoney(self, iMoney):
        self.GetObject('txt_max').SetText(str(iMoney))

    
    def GetSupportGroup(self):
        bAShow = self.GetObject('txt_numA').GetShow()
        bBShow = self.GetObject('txt_numB').GetShow()
        if bAShow:
            return ladderrankallstardefine.GUESS_COIN_LEFT
        elif bBShow:
            return ladderrankallstardefine.GUESS_COIN_RIGHT
        else:
            return ladderrankallstardefine.GUESS_COIN_OTHER

    
    def InitDlg(self):
        import wrapedit
        (x, y, w, h) = self.GetLocData('txt_Ateam')
        self.m_oNumEditA = wrapedit.CLimitNumberEdit(self, interface.COLOR_3, interface.FontLT14_3, x, y, w, h)
        self.m_oNumEditA.SetTextAlign(interface.ALIGN_CENTER_MIDDLE)
        self.m_oNumEditA.SetText('0')
        (x, y, w, h) = self.GetLocData('txt_Bteam')
        self.m_oNumEditB = wrapedit.CLimitNumberEdit(self, interface.COLOR_3, interface.FontLT14_3, x, y, w, h)
        self.m_oNumEditB.SetTextAlign(interface.ALIGN_CENTER_MIDDLE)
        self.m_oNumEditB.SetText('0')

    
    def UpdateEditMaxNum(self, iNum):
        self.m_oNumEditA.SetMaxNum(iNum)
        self.m_oNumEditB.SetMaxNum(iNum)

    
    def ResetEditA(self):
        self.m_oNumEditA.SetText('0')

    
    def ResetEditB(self):
        self.m_oNumEditB.SetText('0')

    
    def GetEditA(self):
        sText = self.m_oNumEditA.GetText()
        if sText:
            return int(sText)
        else:
            return 0

    
    def GetEditB(self):
        sText = [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            self].GetText()
        if sText:
            return int(sText)
        else:
            return 0

    
    def SetBoxEnterCB(self, oCBA, oCBB):
        oHotBoxA = self.GetObject('hloc_teamA')
        oHotBoxB = self.GetObject('hloc_teamB')
        if oHotBoxA:
            oHotBoxA.SetEnterCB(oCBA)
        
        if oHotBoxB:
            oHotBoxB.SetEnterCB(oCBB)
        

    
    def SetBoxLeaveCB(self, oCB):
        oHotBoxA = self.GetObject('hloc_teamA')
        oHotBoxB = self.GetObject('hloc_teamB')
        if oHotBoxA:
            oHotBoxA.SetLeaveCB(oCB)
        
        if oHotBoxB:
            oHotBoxB.SetLeaveCB(oCB)
        

    
    def CloseWindow(self):
        CGuessVoteDlg.CloseUI()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        
        if iMsgID == 2:
            self.ssEmit(self.SS_OpenGetGuessMoneyDlg)
        elif iMsgID == 3:
            self.ssEmit(self.SS_OnGuessBtnClick, self.GetEditA(), 0)
        elif iMsgID == 4:
            self.ssEmit(self.SS_OnGuessBtnClick, self.GetEditB(), 1)
        



class CGetGuessCoinDlg(combdialog.CCombDialog):
    sUIName = 'dialog4/allstarrank/allstar/allstar_guess_getitem.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        interface.Center(self)
        self.m_oIcon = None
        self.InitIcon()

    
    def InitIcon(self):
        import ui
        (x, y) = self.GetObject('loc_icon').GetPos()
        self.m_oIcon = ui.CI&*ge(self, 'item44/10104.igs', 'item')
        self.m_oIcon.SetPos(x, y)

    
    def CloseWindow(self):
        CGetGuessCoinDlg.CloseUI()

    
    def ShowSchedule(self):
        import dlgschedule
        import dlgnewschedule
        import permission
        if permission.IsNewSchedule():
            dlgnewschedule.ShowSwitch()
        else:
            dlgschedule.SwitchSchedule()

    
    def ShowMatchSchedule(self):
        import dlgladderrankallstarmain
        dlgladderrankallstarmain.ShowDlg()

    
    def ShowGuessShop(self):
        import dlgladderrankguessmain
        if not dlgladderrankguessmain.CGuessMainDlg.IsOpen():
            dlgladderrankguessmain.ShowGuessMainDlg(ladderrankallstardefine.TYPE_GAME_GUESS_GUESS_MALL)
        else:
            oGuessMain = dlgladderrankguessmain.CGuessMainDlg.GetUI()
            oGuessMain.SetMatchBtnShow(ladderrankallstardefine.TYPE_GAME_GUESS_GUESS_MALL)
            oGuessMain.OpenClickPage(ladderrankallstardefine.TYPE_GAME_GUESS_GUESS_MALL)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 3:
            self.ShowSchedule()
        elif iMsgID == 4:
            self.ShowMatchSchedule()
        elif iMsgID == 5:
            self.ShowGuessShop()
