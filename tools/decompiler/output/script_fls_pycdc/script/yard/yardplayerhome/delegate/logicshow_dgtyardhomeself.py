# pycdc 交叉复核产物 · script.fls entry 3940
# co_filename(原始)='script/yard/yardplayerhome/delegate/logicshow_dgtyardhomeself.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3940.pyc (Python 2.5)

import logic_dlgshowbase
import definesshowkey
import yardinterface

class CDgtYardSelfShowLogic(logic_dlgshowbase.CShowLogicBase):
    
    def __init__(self, oDlg):
        logic_dlgshowbase.CShowLogicBase.__init__(self, definesshowkey.YARDHOME_SELF, definesshowkey.YARDHOME_MAIN, oDlg)
        self.VInit()

    
    def GetYardHomeData(self, iPlayerID = None):
        ''':rtype yardhome_oneplayer.CYardHome_OnePlayer'''
        oContext = yardinterface.GetYardHomeContext()
        oPlayerHomeData = oContext.GetYardHome(iPlayerID)
        del oPlayerHomeData

    
    def VInit(self):
        self.InitSignal()
        self.CheckIsOpenShowLock()

    
    def InitSignal(self):
        oPlayerDataMgr = self.GetYardHomeData()
        oModel = oPlayerDataMgr.GetHomeInfoDataMgr()
        oModel.ssConnect(oModel.SS_UpdateHomeBaseInfo, self.OnUpdateHomeBaseInfo_Signal)

    
    def OnUpdateHomeBaseInfo_Signal(self, *args):
        self.DelayCheckIsOpenShowLock()

    
    def VDoDlgRealShowEvent(self, bRealShow):
        if not bRealShow:
            oDlg = self.GetDlg()
            oDlg.DoDlgRealShowLogic(False)
        else:
            self.DoDelayShowEvent()
            oDlg = self.GetDlg()
            oDlg.DoDlgRealShowLogic(True)

    
    def VIsOpenSelfConditionShowLock(self):
        oCurYardHomeData = self.GetYardHomeData()
        dBaseInfo = oCurYardHomeData.GetHomeInfoDataMgr().GetBaseInfo()
        if dBaseInfo:
            return True
        else:
            return False
