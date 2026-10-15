# pycdc 交叉复核产物 · script.fls entry 4575
# co_filename(原始)='script/dialog/dlgmulhorse.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4575.pyc (Python 2.5)

import interface
import combdialog
import combmacro
import walker
g_SelMulHorse = None

def ModuleReset():
    global g_SelMulHorse
    g_SelMulHorse = None


class CFakeRole(walker.CFakeRole):
    
    def __init__(self, parent, horseID):
        charidx = 121
        desc = {
            'horse': [
                horseID,
                0,
                0],
            'weapon': [
                0,
                0,
                0],
            'color': [
                0,
                0,
                0],
            'wing': [
                0],
            'Realcolor': [
                0,
                0,
                0] }
        walker.CFakeRole.__init__(self, parent, 0, charidx, desc)
        self.RefreshSow()

    
    def RefreshSow(self):
        import player
        self.CreateMultiHorsePlayer(0, 121, None, player.MULTIHORSE_POS_1, refresh = False, empty = True)
        self.CreateMultiHorsePlayer(0, 121, None, player.MULTIHORSE_POS_2, refresh = False, empty = True)
        self.CreateMultiHorsePlayer(0, 121, None, player.MULTIHORSE_POS_3, refresh = False, empty = True)
        self.CreateMultiHorsePlayer(0, 121, None, player.MULTIHORSE_POS_4, refresh = False, empty = True)
        for pobj in self.m_MultiHorsePlayerList:
            if pobj.m_Rider:
                pobj.m_Rider.SetShow(False)
            
            if pobj.m_PosType in (player.MULTIHORSE_POS_1, player.MULTIHORSE_POS_2):
                pobj.SetShow(False)
                continue
        
        if self.m_Rider:
            self.m_Rider.SetShow(False)
        

    
    def IsRiderWalker(self):
        return True

    
    def SetShadow(self, bSet):
        pass



class CSelMulHorse(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/mulhorse/selmulhorse.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_OldRide = None
        self.m_OldRideCurDirect = 1
        self.m_NewRide = None
        self.m_NewRideCurDirect = 1
        horseid1 = 9
        horseid2 = 10
        self.UpdateOldPhoto(horseid1)
        self.UpdateNewPhoto(horseid2)

    
    def UpdateOldPhoto(self, horseid):
        self.m_OldRide = CFakeRole(self, horseid)
        tempimg = self.GetObject('img_Ride1')
        (x, y) = tempimg.GetPos()
        (w, h) = tempimg.GetSize()
        self.m_OldRide.SetPos(x + w / 2, y + h - 20)
        self.m_OldRide.SetDirection(4)
        self.m_OldRide.SetZ(tempimg.GetZ() + 1)

    
    def UpdateNewPhoto(self, horseid):
        import charpath
        self.m_NewRide = CFakeRole(self, horseid)
        if charpath.IsUseNewRes():
            sName = 'img_Ride3'
        else:
            sName = 'img_Ride2'
        tempimg = self.GetObject(sName)
        (x, y) = tempimg.GetPos()
        (w, h) = tempimg.GetSize()
        self.m_NewRide.SetPos(x + w / 2, y + h - 20)
        self.m_NewRide.SetDirection(4)
        self.m_NewRide.SetZ(tempimg.GetZ() + 1)

    
    def CloseWindow(self):
        global g_SelMulHorse
        g_SelMulHorse = None

    
    def C2SExchange(self, id):
        import netnpc
        netnpc.C2SNpcAnswer(id)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.m_OldRideCurDirect -= 1
            self.m_OldRideCurDirect = (self.m_OldRideCurDirect + 8) % 8
            self.m_OldRide.SetDirection(self.m_OldRideCurDirect * 4)
        elif msgid == 3:
            self.m_OldRideCurDirect += 1
            self.m_OldRideCurDirect %= 8
            self.m_OldRide.SetDirection(self.m_OldRideCurDirect * 4)
        elif msgid == 4:
            self.m_NewRideCurDirect -= 1
            self.m_NewRideCurDirect = (self.m_NewRideCurDirect + 8) % 8
            self.m_NewRide.SetDirection(self.m_NewRideCurDirect * 4)
        elif msgid == 5:
            self.m_NewRideCurDirect += 1
            self.m_NewRideCurDirect %= 8
            self.m_NewRide.SetDirection(self.m_NewRideCurDirect * 4)
        elif msgid in (6, 7):
            id = msgid - 5
            self.C2SExchange(id)
            self.CloseWindow()
        



def Show():
    global g_SelMulHorse
    if not g_SelMulHorse:
        g_SelMulHorse = CSelMulHorse()
