# pycdc 交叉复核产物 · script.fls entry 1312
# co_filename(原始)='script/mxgame/activity/2021summer/dgt/logicshow_dgtsummeractmain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1312.pyc (Python 2.5)

import logic_dlgshowmain
import definesshowkey
import activitybasedefines
SUBPAGE_2_SHOWKEY = {
    activitybasedefines.PAGE_SUMMERDISCOUNT: [
        definesshowkey.SUMMERACT_SUMMERDISCOUNT],
    activitybasedefines.PAGE_SUMMERSIGNIN: [
        definesshowkey.SUMMERACT_SUMMERSIGNIN] }

class CDgtSummerActMainShowLogic(logic_dlgshowmain.CShowLogicMain):
    
    def __init__(self, oDlg):
        logic_dlgshowmain.CShowLogicMain.__init__(self, definesshowkey.SUMMERACT_MAIN, '', oDlg)
        self.\x9b\x84\xa3\xa4\xb9()

    
    def \x9b\x84\xa3\xa4\xb9(self):
        self.SetCurSub([], True)

    
    def VSetFutureSubPage(self, iSubPage):
        if self.m_iFurtureSubPage == iSubPage:
            return None
        
        self.m_iFurtureSubPage = iSubPage
        self.SetCurSub(SUBPAGE_2_SHOWKEY.get(iSubPage, []), self.VIsNeedSubShowLogic(iSubPage))

    
    def VIsNeedSubShowLogic(self, iPage):
        if iPage in SUBPAGE_2_SHOWKEY:
            return True
        else:
            return False

    
    def VDoDlgRealShowEvent(self, bShow):
        if bShow:
            self.DoDelayShowEvent()
        
        oDlg = self.GetDlg()
        oDlg.DoDlgRealShowLogic(bShow)
