# pycdc 交叉复核产物 · script.fls entry 3651
# co_filename(原始)='script/mxgame/consignmentsalecenter/view/showlogic_consignhuoli.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3651.pyc (Python 2.5)

import logic_dlgshowbase
import definesshowkey

class CShowLogicConsignHuoli(logic_dlgshowbase.CShowLogicBase):
    
    def __init__(self, oDlg):
        logic_dlgshowbase.CShowLogicBase.__init__(self, definesshowkey.CONSIGNMALL_HUOLI_PAGE, definesshowkey.CONSIGNMALL_MAIN, oDlg)
        self.m_bHasRecieveData = False
        self.\xb4\xab\x8c\x8b\x96()

    
    def \xb4\xab\x8c\x8b\x96(self):
        self.InitSignal()
        self.CheckIsOpenShowLock()

    
    def InitSignal(self):
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_HuoLiSaleDataReady, self.OnHuoLiSaleDataReady_Signal)

    
    def OnHuoLiSaleDataReady_Signal(self, *args):
        self.m_bHasRecieveData = True
        self.DelayCheckIsOpenShowLock()

    
    def VIsOpenSelfConditionShowLock(self):
        return self.m_bHasRecieveData

    
    def GetModel(self):
        import salemgr
        return salemgr.GetSaleMgr()
