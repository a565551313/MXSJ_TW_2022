# pycdc 交叉复核产物 · script.fls entry 288
# co_filename(原始)='script/mxgame/activity/yardmatch/view/dlgyardmatchminicard.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_288.pyc (Python 2.5)

import combdialog
import dgtyardmatchentriesmini
import slot
import pubimage

class CYardMatchEntriesMiniDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    sUIName = 'dialog4/activity/tingyuan/minicard.dlg'
    SS_MiniEntriesVote = 'SS_MiniEntriesVote()'
    SS_MiniEntriesOpenCard = 'SS_MiniEntriesOpenCard()'
    
    def __init__(self, oParent, iEntriesID):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_iEntriesID = iEntriesID
        self.m_oDelegateList = []
        self.InitDelegate()

    
    def InitDelegate(self):
        self.m_oDelegateList = [
            dgtyardmatchentriesmini.CYardMatchEntriesMiniDelegate(self)]

    
    def CreateYardMapImg(self, sUrl):
        (iX, iY, iW, iH) = self.GetLocData('loc_photo')
        self.m_YardMapImg = None(pubimage.CreatImgObj, self, iW, iH)
        self.m_YardMapImg.SetPos(iX, iY)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            self.ssEmit(self.SS_MiniEntriesVote, self.m_iEntriesID)
        elif iMsgID == 3:
            self.ssEmit(self.SS_MiniEntriesOpenCard, self.m_iEntriesID)
