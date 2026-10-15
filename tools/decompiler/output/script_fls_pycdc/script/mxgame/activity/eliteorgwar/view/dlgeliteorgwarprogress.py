# pycdc 交叉复核产物 · script.fls entry 191
# co_filename(原始)='script/mxgame/activity/eliteorgwar/view/dlgeliteorgwarprogress.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_191.pyc (Python 2.5)

import combdialog
import interface
import slot
g_Progress = None

def ModuleReset():
    global g_Progress
    g_Progress = None


def RefreshProgress(iProgress):
    global g_Progress
    if not g_Progress:
        g_Progress = CProgressDlg()
    
    g_Progress.RefreshProgress(iProgress)


def CloseProgress():
    if g_Progress:
        g_Progress.CloseWindow()
    


class CProgressDlg(combdialog.CCombDialog, slot.ISignalSubject):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/jyorgwar/data.dlg')
        self.SetIgnoreEsc(True)
        self.ssInit()
        self.InitDlg()
        self.ResetPos()
        self.InitSignal

    
    def InitDlg(self):
        self.m_oKeyNumText = self.GetObject('text_keynum')
        self.m_oKeyNumText.SetText('0')

    
    def InitSignal(self):
        import commoncb
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnMapChange')
        commoncb.RegistCB(commoncb.WAR_START, self, 'OnWarStart')
        commoncb.RegistCB(commoncb.WAR_END, self, 'OnWarEnd')

    
    def RemoveSignal(self):
        import commoncb
        commoncb.RemoveCB(commoncb.SCENE_CHANGE, self, 'OnMapChange')
        commoncb.RemoveCB(commoncb.WAR_START, self, 'OnWarStart')
        commoncb.RemoveCB(commoncb.WAR_END, self, 'OnWarEnd')

    
    def OnMapChange(self, iSceneID, iMapID, iMiniMapID):
        pass

    
    def OnWarStart(self):
        self.SetShow(False)

    
    def OnWarEnd(self):
        self.SetShow(True)

    
    def RefreshProgress(self, iCur):
        self.m_oKeyNumText.SetText('%d' % iCur)

    
    def CloseWindow(self):
        global g_Progress
        self.RemoveSignal()
        g_Progress = None

    
    def ResetPos(self):
        import ratio
        iRw = ratio.WINDOW_WIDTH
        iRh = ratio.WINDOW_HEIGHT
        (_, _, w, h) = self.GetLocData('loc_bg')
        x = -10
        y = iRh / 2 - h
        self.SetPos(x, y)

    
    def OnMessage(self, msgid):
        if msgid == 10:
            self.ShowPreview()
        elif msgid == 11:
            self.ShowInfoDlg()
        

    
    def ShowInfoDlg(self):
        LOG_DEBUG('ShowInfoDlg>>>>>>>>')

    
    def ShowPreview(self):
        LOG_DEBUG('ShowPreview>>>>>>>>')
