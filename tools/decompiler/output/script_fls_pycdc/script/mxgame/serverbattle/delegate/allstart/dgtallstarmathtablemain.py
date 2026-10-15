# pycdc 交叉复核产物 · script.fls entry 1433
# co_filename(原始)='script/mxgame/serverbattle/delegate/allstart/dgtallstarmathtablemain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1433.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/5/25 16:55
\xd7\xf7\xd5\xdf: 
\xce\xc4\xbc\xfe: dgtallstartgamegroup
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import serverbattledefine
import mdsbasbattletable
import netserverbattleallstart

class CAllStarMatchTableDgt(delegatebase.CDelegatePaginationBase):
    
    def Init(\x90\x86\x8f\x85):
        \x90\x86\x8f\x85.EidtInit()
        \x90\x86\x8f\x85.OnUpdateSelectGroup(mdsbasbattletable.GetBattleTableModel().GetSelectGroup())

    
    def EidtInit(\x90\x86\x8f\x85):
        oModel = mdsbasbattletable.GetBattleTableModel()
        oModel.ssConnect(oModel.SS_UpdateSelectGroup, \x90\x86\x8f\x85.OnUpdateSelectGroup)

    
    def ShowTwoGroupDlg(\x90\x86\x8f\x85):
        if not \x90\x86\x8f\x85.GetView().GetShow():
            return None
        
        \x90\x86\x8f\x85.GetView().ShowTwoGroupDlg()
        netserverbattleallstart.C2SGetBattleTableTeamInfo(serverbattledefine.ALL_START_BTYPE_14)

    
    def ShowFourGroupDlg(\x90\x86\x8f\x85):
        if not \x90\x86\x8f\x85.GetView().GetShow():
            return None
        
        () = None
        None.GetView().ShowFourGroupDlg()
        netserverbattleallstart.C2SGetBattleTableTeamInfo(serverbattledefine.ALL_START_BTYPE_GROUP)

    
    def ShowQualityGroupDlg(\x90\x86\x8f\x85):
        if not \x90\x86\x8f\x85.GetView().GetShow():
            return None
        
        \x90\x86\x8f\x85.GetView().ShowFourGroupDlg()

    
    def GetGroupInfo(\x90\x86\x8f\x85):
        iGroup = mdsbasbattletable.GetBattleTableModel().GetSelectGroup()
        netserverbattleallstart.C2SGetBattleTableBattleInfo(iGroup)

    
    def OnUpdateSelectGroup(\x90\x86\x8f\x85, iGroup):
        if iGroup in serverbattledefine.ALL_START_GROUP_TEAM_LIST_FINAL:
            \x90\x86\x8f\x85.ShowTwoGroupDlg()
        elif iGroup in serverbattledefine.ALL_START_GROUP_TEAM_LIST_14:
            \x90\x86\x8f\x85.ShowTwoGroupDlg()
        elif iGroup in serverbattledefine.ALL_START_GROUP_QUALIFY_ROUND_LIST:
            \x90\x86\x8f\x85.ShowQualityGroupDlg()
        elif iGroup in serverbattledefine.ALL_START_GROUP_TEAM_LIST:
            \x90\x86\x8f\x85.ShowFourGroupDlg()
        

    
    def VOpenPage(\x90\x86\x8f\x85, dExtend = None):
        iGroup = mdsbasbattletable.GetBattleTableModel().GetSelectGroup()
        \x90\x86\x8f\x85.OnUpdateSelectGroup(iGroup)
