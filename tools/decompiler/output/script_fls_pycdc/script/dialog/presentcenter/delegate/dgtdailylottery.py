# pycdc 交叉复核产物 · script.fls entry 4482
# co_filename(原始)='script/dialog/presentcenter/delegate/dgtdailylottery.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4482.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/12/14 14:09
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: dgtdailylottery
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import mddailylottery
import netdailylottery

class CDailyLotteryDgt(delegatebase.CDelegateBase):
    
    def \x8d\xaa\xadt(self):
        oView = self.GetView()
        self.EditInit()

    
    def EditInit(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickChoujiang, self.OnClickChoujiang)
        oView.ssConnect(oView.SS_OpenView, self.OnOpenView)
        oView.ssConnect(oView.SS_EndChoujiang, self.OnEndChoujiang)
        oView.ssConnect(oView.SS_SetCaptrueWindow, self.OnSetCaptrueWindow)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_SetItem, self.OnSetItem)
        oModel.ssConnect(oModel.SS_SetRewardItem, self.OnSetRewardItem)
        oModel.ssConnect(oModel.SS_SetBtnEnable, self.OnSetBtnEnable)

    
    def OnSetItem(self):
        oItemRewardPoolList = self.GetModel().GetRewardPool()
        self.GetView().ShowItem(oItemRewardPoolList)

    
    def OnClickChoujiang(self):
        netdailylottery.C2GSBegin()

    
    def OnEndChoujiang(self, iTargetReward):
        netdailylottery.C2GSEnd(iTargetReward)

    
    def OnOpenView(self):
        netdailylottery.C2GSOpenView()
        self.OnSetItem()

    
    def OnSetRewardItem(self, iCanRun, iRewardIndex):
        self.GetView().Stop(iCanRun, iRewardIndex)

    
    def OnSetBtnEnable(self, iCanRun):
        self.GetView().SetChoujiangBtnEnable(iCanRun)

    
    def OnSetCaptrueWindow(self, bCaptrueWindow):
        self.GetModel().SetCaptrueWindow(bCaptrueWindow)

    
    def GetModel(self):
        return mddailylottery.GetCDailyLotteryMgr()
