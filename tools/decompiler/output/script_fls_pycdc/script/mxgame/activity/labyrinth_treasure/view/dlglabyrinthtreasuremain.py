# pycdc 交叉复核产物 · script.fls entry 4465
# co_filename(原始)='script/mxgame/activity/labyrinth_treasure/view/dlglabyrinthtreasuremain.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4465.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/8/5 10:34
\xd7\xf7\xd5\xdf: gesaferoc
\xce\xc4\xbc\xfe:
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import pagedlgbase
import slot

class CLabyrinthTreasureDlg(combdialog.CCombDialog, slot.ISignalSubject, pagedlgbase.CPageDlgBase):
    sUIName = 'dialog/pizza/maze_main.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        pagedlgbase.CPageDlgBase.__init__(self)
        self.ssInit()
        self.m_DelegateList = []
        self.InitDelegate()

    
    def InitDelegate(self):
        import dgtlabyrinthtreasuremain
        self.m_DelegateList = [
            dgtlabyrinthtreasuremain.CLabyrinthTreasureDgt(self, [
                'btn_maze',
                'btn_relic'])]

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_OpenDlg, dExtend)

    
    def VClose(self):
        self.ssEmit(self.SS_CloseDlg)

    
    def OnEditMessage(self, \xa9\x8d\xb3gID):
        pass

    
    def OnMessage(self, \xa9\x8d\xb3gID):
        self.OnEditMessage(\xa9\x8d\xb3gID)
        self.ssEmit(self.SS_ClickBtn, \xa9\x8d\xb3gID)
        if \xa9\x8d\xb3gID == 1:
            self.VClose()
            self.CloseUI()
