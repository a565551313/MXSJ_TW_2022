# pycdc 交叉复核产物 · script.fls entry 1510
# co_filename(原始)='script/mxgame/activity/2021springactivity/dgt/dgt2021springactivity.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1510.pyc (Python 2.5)

import dgtactivitybase
import md2021springactivity

class CRewardBtnDelegate(dgtactivitybase.CRewardBtnDelegate):
    '''
\t\xb1\xb1\xa8\xee\xb4\xab\xad\xb6\xab\xf6\xb6s\xc5\xde\xbf\xe8
\t'''
    
    def GetModel(self):
        '''
\t\t:rtype: md2021springactivity.CActivityModel
\t\t'''
        return md2021springactivity.GetModel()

    
    def SelectDefaultBtn(self):
        oBaseModel = self.GetBaseModel()
        oModel = self.GetModel()
        iPageList = oBaseModel.GetPageList(self.m_iBaseType)
        iRedPointTabIdx = None
        iAutoSelectPage = oModel.GetAutoSelectPage()
        if iAutoSelectPage is not None and iAutoSelectPage in iPageList:
            oModel.ClearAutoSelectPage()
            
            try:
                None.OnBtnClick(iAutoSelectPage)
                return None
            if iRedPointTabIdx is None:
                iLastSelectPage = oModel.GetLastSelectPage()
                if iLastSelectPage is not None and iLastSelectPage != self.m_iLastPage and iLastSelectPage in iPageList:
                    iRedPointTabIdx = iLastSelectPage
                
            

        if iRedPointTabIdx is not None and iRedPointTabIdx in iPageList:
            self.OnBtnClick(iRedPointTabIdx)
        elif self.m_iLastPage in iPageList:
            self.GetView().SetBtnSelected(self.m_iLastPage)
        elif iPageList:
            self.OnBtnClick(iPageList[0])
        else:
            self.GetView().SwitchEmpty()

    
    def NeedRequestData(self, iRewardType):
        return False

    
    def OnRealSwitch(self, iRewardType):
        self.m_iLastPage = iRewardType
        oModel = self.GetModel()
        oView = self.GetView()
        oModel.SetLastSelectPage(iRewardType)
        self.GetView().SetShow(True)
        oModel.AddHasClickPage(iRewardType)
        oView.SetBtnSelected(iRewardType)
        oView.SwitchPage(iRewardType)

    
    def CheckIsCanSwitchPage(self, iRewardType):
        import presentcenterdefines
        import stopgamemoduleinterface
        if iRewardType in presentcenterdefines.PAGE2MODULEID:
            if stopgamemoduleinterface.CheckStop(presentcenterdefines.PAGE2MODULEID[iRewardType]):
                return False
            
        
        return True
