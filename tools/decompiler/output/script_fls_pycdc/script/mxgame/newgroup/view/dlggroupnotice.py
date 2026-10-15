# pycdc 交叉复核产物 · script.fls entry 2180
# co_filename(原始)='script/mxgame/newgroup/view/dlggroupnotice.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2180.pyc (Python 2.5)

import combdialog
import interface
import combmacro
g_GroupNoticeDlg = None

def ModuleReset():
    global g_GroupNoticeDlg
    g_GroupNoticeDlg = None


def \xec\xda\xcb\xec\xd7\xd0\xc8(bShow, sNotice = ''):
    global g_GroupNoticeDlg, g_GroupNoticeDlg
    if bShow:
        if not g_GroupNoticeDlg:
            g_GroupNoticeDlg = CGroupNoticeDialog(sNotice)
        
        g_GroupNoticeDlg.\xec\xda\xcb\xec\xd7\xd0\xc8(True)
    else:
        g_GroupNoticeDlg = None


class CGroupNoticeDialog(combdialog.CCombDialog):
    
    def __init__(self, sNotice):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/group_new/group_info/group_msg.dlg')
        interface.Center(self)
        self.GetObject('text_dft_000').SetText(sNotice)

    
    def CloseWindow(self):
        \xec\xda\xcb\xec\xd7\xd0\xc8(False)

    
    def OnMessage(self, iMsgid):
        if iMsgid in (1, 1493172226):
            self.CloseWindow()
