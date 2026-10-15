# pycdc 交叉复核产物 · script.fls entry 1216
# co_filename(原始)='script/dialog/choosespecialbook/dgtchoosespecialbook.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1216.pyc (Python 2.5)

import delegatebase
import mdchoosespecialbook
import nethandleui

class CAllStarGuessMainDgt(delegatebase.CDelegateBase):
    
    def GetView(self):
        '''
\t\t:rtype: dlgchoosespecialbook.CChooseBookDlg
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnBookItemClick, self.OnBookItemClick)
        None(None(None, None, None, None, *oView.ssConnect, **oView), self.OnConfirmBtnClick)
        oModel = mdchoosespecialbook.GetChooseBookModel()
        oModel.ResetSelect()
        oModel.ssConnect(oModel.SS_OpenChooseDlg, self.OpenChooseDlg)

    
    def OnBookItemClick(self, iSkillID):
        oModel = mdchoosespecialbook.GetChooseBookModel()
        oModel.SetSelectIdx(oModel.GetIdxBySkillID(iSkillID))
        self.GetView().UpdateOpenBtnState(iSkillID)

    
    def OnConfirmBtnClick(self):
        oModel = mdchoosespecialbook.GetChooseBookModel()
        if oModel.GetSelectIdx() == -1:
            return None
        
        nethandleui.C2SUseSpeShoujue(oModel.GetSequence(), oModel.GetSelectIdx() + 1)
        self.GetView().CloseWindow()

    
    def OpenChooseDlg(self):
        import dgtinsidewarjob
        dBookDataLst = mdchoosespecialbook.GetChooseBookModel().GetBookData()
        iNeedRow = dgtinsidewarjob.GetRowNum(len(dBookDataLst), 3)
        self.GetView().UpdateBookList(dBookDataLst, iNeedRow, 3)
