# pycdc 交叉复核产物 · script.fls entry 728
# co_filename(原始)='script/dialog/dlgexchangeflyride.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_728.pyc (Python 2.5)

import interface
import combdialog
import combmacro
import walker
g_ExchangeFlyRide = None

def ModuleReset():
    global g_ExchangeFlyRide
    g_ExchangeFlyRide = None


class CExchangeFlyRide(combdialog.CCombDialog):
    
    def __init__(self, shape, exchangeDesc):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/ride/exchangeflyride.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_Ride = None
        self.m_RideCurDirect = 0
        self.m_Shape = shape
        self.SetExchangeDesc(exchangeDesc)
        self.GetObject('btn_Sel1').SetSelect(True)
        self.GetObject('btn_Sel2').SetSelect(True)
        self.m_SelDuanjin = True
        self.m_SelBeiji = True
        self.UpdatePhoto(shape)

    
    def UpdatePhoto(self, shape):
        import hero
        import copy
        charidx = hero.g_Hero.m_CharIdx
        desc = copy.deepcopy(hero.g_Hero.m_CharDesc)
        
        try:
            desc.Eop('track')
        except KeyError:
            pass

        desc['wing'] = [
            0]
        desc['horse'] = [
            shape,
            1,
            2,
            0,
            0,
            0]
        if not self.m_SelBeiji:
            desc['horse'][2] = 0
        
        if not self.m_SelDuanjin:
            desc['horse'][1] = 0
        
        self.m_Ride = walker.CFakeRole(self, 0, charidx, desc, hero.g_Hero.m_RealShape)
        tempimg = self.GetObject('img_Ride')
        (x, y) = tempimg.GetPos()
        (w, h) = tempimg.GetSize()
        self.m_Ride.SetPos(x + w / 2, y + h + 20)

    
    def SetExchangeDesc(self, exchangeDesc):
        self.m_ExchangeDesc = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_Desc', self, exchangeDesc, interface.FontLT14_3, interface.COLOR_4, align = interface.ALIGN_LEFT | interface.ALIGN_TOP)

    
    def CloseWindow(self):
        global g_ExchangeFlyRide
        g_ExchangeFlyRide = None

    
    def C2SExchange(self):
        import netnpc
        import C2SNpcAnswer(1)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 4:
            self.C2SExchange()
            self.CloseWindow()
        elif msgid == 2:
            self.m_RideCurDirect -= 1
            self.m_RideCurDirect = (self.m_RideCurDirect + 8) % 8
            self.m_Ride.SetDirection(self.m_RideCurDirect * 4)
        elif msgid == 3:
            self.m_RideCurDirect += 1
            self.m_RideCurDirect %= 8
            self.m_Ride.SetDirection(self.m_RideCurDirect * 4)
        elif msgid == 5:
            self.m_SelDuanjin = not (self.m_SelDuanjin)
            self.UpdatePhoto(self.m_Shape)
        elif msgid == 6:
            self.m_SelBeiji = not (self.m_SelBeiji)
            self.UpdatePhoto(self.m_Shape)
        



def Show(rideType, exchangeDesc):
    global g_ExchangeFlyRide
    if not g_ExchangeFlyRide:
        g_ExchangeFlyRide = CExchangeFlyRide(rideType, exchangeDesc)
