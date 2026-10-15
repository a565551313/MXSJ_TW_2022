# pycdc 交叉复核产物 · script.fls entry 4561
# co_filename(原始)='script/mxgame/activity/fashionactive/dlgfashionactivepub.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4561.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/3/8 15:04
\xd7\xf7\xd5\xdf: \xbf\xec\xc0\xd6\xcb\xae
\xce\xc4\xbc\xfe: dlgfashionactivepub
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import slot
import dlgmengxiang3activitymain
import activitybasedefines
import usermacro
import mdfashiondress

def BuildSubWnd(oParent):
    return CFashionActivePubDlg(oParent)


class CFashionActivePubDlg(combdialog.CCombDialog, slot.ISignalSubject):
    sUIName = 'dialog4/activity/dream3/fashion_main.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.ssInit()

    
    def Hold(self):
        pass

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 2:
            if mdfashiondress.IsFashionXianfu():
                if dlgmengxiang3activitymain.IsOpen():
                    dlgmengxiang3activitymain.CloseMainDlg()
                
                dlgmengxiang3activitymain.DoShow(activitybasedefines.P\xa3\xa5\xa7\xbd\xac\xa7\xb5\xa1\xae\xad\xb6\xaa)
            else:
                usermacro.PROMPT_MSG('\xae\xc9\xb8\xcb\xa8t\xb2\xce\xa5\xbf\xa6b\xad\xad\xaaA\xb4\xfa\xb8\xd5\xa1A\xb7q\xbd\xd0\xb4\xc1\xab\xdd')
