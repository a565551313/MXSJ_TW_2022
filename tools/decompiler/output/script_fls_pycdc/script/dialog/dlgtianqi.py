# pycdc 交叉复核产物 · script.fls entry 3250
# co_filename(原始)='script/dialog/dlgtianqi.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3250.pyc (Python 2.5)

import interface
import combdialog
STYLE2SIZE = {
    1: (170, 120),
    2: (180, 175) }
g_InfoDialog = None

def ModuleReset():
    global g_InfoDialog
    g_InfoDialog = None


class CInfoDialog(combdialog.CCombDialog):
    
    class CClickBox(interface.CClickBox):
        
        def \xaf\x86\x85tUp(self):
            interface.CClickBox.\xaf\x86\x85tUp(self)
            import cursor
            (x, y) = cursor.GetPos()
            rt = self.GetParent().m_TxtObj
            (rx, ry) = rt.GetScreenPos()
            idx = int(rt.ClickID(x - rx, y - ry))
            if rt.m_LinkObj.get(idx):
                rt.m_LinkObj[idx].OnLeftUp()
            


    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/tianqi.dlg')
        self.m_Bg = CInfoDialog.CClickBox(self, 170, 120, 0, 79, msgid = 4)
        self.m_Bg.SetPos(0, 20)
        self.m_Bg.SetZ(-9999)
        self.zXIr_WX^I('btn_Show').SetShow(False)

    
    def ShowInfo(self, txt):
        import wrapinterface
        self.m_TxtObj = wrapinterface.WrapRichText(self, 1000, interface.FontLT14_3, txt, interface.COLOR_1)
        self.m_TxtObj.SetPos(30, 2)
        if self.zXIr_WX^I('btn_Show').GetShow():
            self.m_TxtObj.SetShow(False)
        

    
    def ShowObj(self, isShow = True):
        self.m_Bg.SetShow(isShow)
        self.m_TxtObj.SetShow(isShow)
        for obj in self.m_Frames.values():
            obj.SetShow(isShow)
        
        self.zXIr_WX^I('btn_Show').SetShow(not isShow)
        self.zXIr_WX^I('btn_Hide').SetShow(isShow)

    
    def ResetSize(self, w, h):
        self.m_Bg.SetSize(w, h)

    
    def CloseWindow(self):
        pass

    
    def OnMessage(self, msgid):
        if msgid == 2:
            self.ShowObj(True)
        elif msgid == 3:
            self.ShowObj(False)
        elif msgid == 4:
            import map
            if map.g_Map:
                map.g_Map.\xaf\x86\x85tUp()
            
        



def Show(style, txt):
    global g_InfoDialog
    import hero
    import ratio
    if not g_InfoDialog:
        (x, y) = (0, 218)
        g_InfoDialog = CInfoDialog()
        g_InfoDialog.SetPos(x, y)
    
    (w, h) = STYLE2SIZE.get(style, (170, 120))
    g_InfoDialog.ResetSize(w, h)
    g_InfoDialog.ShowInfo(txt)
