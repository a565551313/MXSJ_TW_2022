# pycdc 交叉复核产物 · script.fls entry 2969
# co_filename(原始)='script/mxgame/dailyteam/logicshowdailyteam/showlogic_dgtdailyteaminfo.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2969.pyc (Python 2.5)

import logic_dlgshowbase
import definesshowkey

class CShowLogicDailySubTask(logic_dlgshowbase.CShowLogicBase):
    
    def __init__(self, oDlg):
        logic_dlgshowbase.CShowLogicBase.__init__(self, definesshowkey.DAILY_TEAM_INFO, definesshowkey.DAILY_MAIN, oDlg)
        self.m_bHasRecieveData = False
        self.\xcf\xd0\xf7\xf0\xed()

    
    def \xcf\xd0\xf7\xf0\xed(self):
        self.InitSignal()
        self.CheckIsOpenShowLock()

    
    def GetModel(self):
        ''':rtype mddailyteam.CWarTeamInfoModel'''
        import mddailyteam
        return mddailyteam.GetWarTeamInfoModel()

    
    def InitSignal(self):
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UpdateTeamInfo, self.OnUpdateTeamInfo_Signal)

    
    def OnUpdateTeamInfo_Signal(self, *args):
        self.m_bHasRecieveData = True
        self.CheckIsOpenShowLock()

    
    def VIsOpenSelfConditionShowLock(self):
        if self.m_bHasRecieveData:
            self.m_bHasRecieveData = False
            return True
        
        oModel = self.GetModel()
        if oModel.GetTeamInfo():
            return True
        else:
            return False
