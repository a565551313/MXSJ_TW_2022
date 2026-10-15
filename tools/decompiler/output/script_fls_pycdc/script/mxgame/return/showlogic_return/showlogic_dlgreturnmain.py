# pycdc 交叉复核产物 · script.fls entry 679
# co_filename(原始)='script/mxgame/return/showlogic_return/showlogic_dlgreturnmain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_679.pyc (Python 2.5)

import logic_dlgshowmain
import definesshowkey
import returnrewarddefines
SUBPAGE_2_SHOWKEY = {
    returnrewarddefines.PAGE_RETURN_WISH: [
        definesshowkey.RETURN_WISH],
    returnrewarddefines.PAGE_REWARD_TASK: [
        definesshowkey.RETURN_TASK],
    returnrewarddefines.PAGE_HELP: [
        definesshowkey.RETURN_HELP],
    returnrewarddefines.PAGE_RETURN_COLLECT: [
        definesshowkey.RETURN_RETURNJK] }

class CDgtReturnMainLogic(logic_dlgshowmain.CShowLogicMain):
    
    def __init__(self, oDlg):
        logic_dlgshowmain.CShowLogicMain.__init__(self, definesshowkey.RETURN_MAIN, '', oDlg)
        self.VInit()

    
    def VInit(self):
        self.SetCurSub([], True)

    
    def VSetFutureSubPage(self, iSubPage):
        if self.m_iFurtureSubPage == iSubPage:
            return None
        
        self.m_iFurtureSubPage = iSubPage
        None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.SetCurSub, SUBPAGE_2_SHOWKEY.get(iSubPage, []), self.VIsNeedSubShowLogic(iSubPage))

    
    def VIsNeedSubShowLogic(self, iPage):
        if iPage in SUBPAGE_2_SHOWKEY:
            return True
        else:
            return False
