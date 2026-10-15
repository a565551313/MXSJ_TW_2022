# pycdc 交叉复核产物 · script.fls entry 3042
# co_filename(原始)='script/numbereffect.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3042.pyc (Python 2.5)

import interface
import ui
g_CountdownTimer = None

def ModuleReset():
    global g_CountdownTimer
    g_CountdownTimer = None


def PlayCountdown(iNumber = 9, txt = None):
    global g_CountdownTimer
    import mainmenu
    if g_CountdownTimer:
        ReleaseCountdown()
    
    
    def countdown(obj, iTick):
        if iTick <= 0 or mainmenu.IsWar():
            ReleaseCountdown()
            return None
        
        obj.SetNum(iTick)
        return (iTick - 1,)

    g_CountdownTimer = CTimerObj(iNumber, txt)
    g_CountdownTimer.CreatePyCommand(30, countdown, iNumber - 1)


def ReleaseCountdown():
    global g_CountdownTimer
    if g_CountdownTimer:
        g_CountdownTimer.Release()
        g_CountdownTimer = None
    


class CTimerObj(interface.CBaseObject):
    
    def __init__(self, iTick, txt = None):
        import ratio
        interface.CBaseObject.__init__(self, None)
        self.SetZ(500)
        if ratio.Is1024x768():
            (x, y) = (500, 125)
        elif ratio.Is1366x768() or ratio.Is1366x708():
            (x, y) = (700, 125)
        elif ratio.Is1280x960():
            (x, y) = (620, 125)
        else:
            (x, y) = (400, 125)
        self.SetPos(x, y)
        numberObj1 = ui.CImage(self, 'number.igs', 'war')
        
        try:
            (w, h) = None.GetSize()
            numberObj1.SetPos(-w, 0)
            numberObj2 = ui.CImage(self, 'number.igs', 'war')
            self.m_Images = (numberObj1, numberObj2)
            self.SetNum(iTick)
            self.SetText(txt)
            return None


    
    def SetNum(self, iNumber):
        (numberObj1, numberObj2) = self.m_Images
        numberObj1.SetShow(iNumber >= 10)
        numberObj1.SetFrame(iNumber / 10)
        numberObj2.SetFrame(iNumber % 10)

    
    def SetText(self, txt):
        import gamefont
        self.m_TextObj = None
        if txt:
            offset = 20
            if self.m_Images[0].GetShow():
                offset = 0
            
            font = gamefont.CreateFont(gamefont.TYPE_SONGTI, 36, 600, bEdge = True, bGrad = True)
            self.m_TextObj = interface.CTextObject(self, txt, font, [
                16239450,
                16233017,
                16221696])
            (w, h) = self.m_TextObj.GetSize()
            self.m_TextObj.SetPos(-w / 2 + offset, -h - 10)
