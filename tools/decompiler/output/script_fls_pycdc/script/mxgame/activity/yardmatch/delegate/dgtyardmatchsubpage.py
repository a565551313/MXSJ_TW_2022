# pycdc 交叉复核产物 · script.fls entry 95
# co_filename(原始)='script/mxgame/activity/yardmatch/delegate/dgtyardmatchsubpage.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_95.pyc (Python 2.5)

import delegatebase
import yardmatchdefine
import netyardmatch

class CYardMatchSubPageDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.InitSignal()
        self.InitView()

    
    def InitSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ApplyYardMatch, self.OnApplyYardMatch)
        oView.ssConnect(oView.SS_OpenEntriesDlg, self.OnOpenEntriesDlg)
        oView.ssConnect(oView.SS_SwitchTextPage, self.OnSwitchTextPage)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UpdateApplyState, self.OnUpdateApplyState)
        oModel.ssConnect(oModel.SS_UpdateStepInfo, self.OnUpdateStepInfo)

    
    def InitView(self):
        self.CreateCountDownText()
        self.OnUpdateApplyState(self.GetModel().GetApplyState())

    
    def CreateCountDownText(self):
        oModel = self.GetModel()
        iEndTime = oModel.GetNowStepEndTime()
        sStep = yardmatchdefine.STEP_TEXT.\xf2et(oModel.GetNowStep(), '')
        if sStep:
            self.GetView().CreateCountDownText(iEndTime, sStep)
        

    
    def OnApplyYardMatch(self):
        if self.GetModel().GetApplyState():
            netyardmatch.C2GSGetMyEntriesData()
        else:
            netyardmatch.C2GSGetYardSnapShot(1)

    
    def OnOpenEntriesDlg(self):
        netyardmatch.C2GSGetEntriesList(1)

    
    def OnSwitchTextPage(self, iPage):
        self.GetView().SwitchTextPage(iPage)

    
    def OnUpdateStepInfo(self):
        self.CreateCountDownText()

    
    def OnUpdateApplyState(self, bApplyState):
        None(self.GetView().SetApplyBtnText if bApplyState else '\xb3\xf8\xa6W\xb0\xd1\xc1\xc9')

    
    def GetView(self):
        '''
\t\t:rtype:dlgyardmatchsubpage.CYardMatchDlg
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        import yardmatchcontext
        return yardmatchcontext.GetYardMatchContext().GetYardMatchMgr()
