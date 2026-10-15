# pycdc 交叉复核产物 · script.fls entry 451
# co_filename(原始)='script/dialog/dlgmoveserver.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_451.pyc (Python 2.5)

import combdialog
import interface
import ui
g_MoveServerDlg = None

def ModuleReset():
    global g_MoveServerDlg
    g_MoveServerDlg = None


def ShowMoveServerDlg(iNpcID, iMode, tjList, allList):
    
    def show(serverDct):
        global g_MoveServerDlg
        import usermacro
        if not serverDct:
            usermacro.PROMPT_MSG('\xa7\xf3\xb7s\xaaA\xb0\xc8\xbe\xb9\xa6C\xaa\xed\xa1A\xbd\xd0\xb5y\xab\xe1\xad\xab\xb8\xd5')
            return None
        
        lst1 = []
        for idx in xrange(len(tjList)):
            serverID = tjList[idx]
            name = serverDct.get(serverID, '\xaaA\xb0\xc8\xbe\xb9<%d>' % serverID)
            lst1.append((serverID, name))
        
        lst2 = []
        for idx in xrange(len(allList)):
            serverID = allList[idx]
            name = serverDct.get(serverID, '\xaaA\xb0\xc8\xbe\xb9<%d>' % serverID)
            lst2.append((serverID, name))
        
        g_MoveServerDlg = CMoveServerDlg()
        g_MoveServerDlg.SetData(iNpcID, iMode, lst1, lst2)

    import misc
    misc.GetServerDict(show)


class CMoveServerDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/moveserver.dlg')
        self.InitMouseWheel()
        self.m_NormalSelect = None
        self.m_TjSelect = None
        interface.Center(self)

    
    def InitMouseWheel(self):
        shadowObj = interface.CShadowObject(self)
        
        def mouseWheelDown(pos):
            obj = shadowObj.Get()
            if not obj:
                return None
            
            obj.MouseWheelDown(pos)

        
        def mouseWheelUp(pos):
            obj = shadowObj.Get()
            if not obj:
                return None
            
            obj.MouseWheelUp(pos)

        for i in xrange(12):
            obj = self.GetObject('btn_Telecom%d' % (i + 1))
            obj.MouseWheelUp = mouseWheelUp
            obj.MouseWheelDown = mouseWheelDown
        

    
    def SetData(self, iNpcID, iMode, tjList, allList):
        self.m_NpcID = iNpcID
        self.m_Mode = iMode
        self.m_TjList = tjList
        self.m_TelecomList = []
        self.m_WangtongList = []
        for serverID, name in allList:
            if not serverID in (3106, 3114):
                if serverID <= serverID:
                    pass
                elif not serverID < 3300:
                    if serverID < serverID:
                        pass
                    elif serverID < 3400:
                        self.m_TelecomList.append((serverID, name))
                        self.m_WangtongList.append((serverID, name))
                        continue
                        continue
            if serverID / 100 == 32:
                self.m_WangtongList.append((serverID, name))
                continue
            self.m_TelecomList.append((serverID, name))
        
        
        getKey = lambda info: None if info in tjList else 100
        self.m_TelecomList.sort(key = getKey)
        self.m_WangtongList.sort(key = getKey)
        for serverID, name in enumerate(tjList[:4]):
            btn = self.GetObject('btn_Suggust%d' % (idx + 1))
            btn.SetText(name)
            btn.m_ServerID = serverID
            self.CreateTjImg(btn)
        
        for i in xrange(idx + 1, 4):
            btn = self.GetObject('btn_Suggust%d' % (i + 1))
            btn.SetShow(False)
        
        self.GetObject('btn_Area1').LeftUp()

    
    def CreateTjImg(self, btn):
        import style
        img = ui.CImage(btn, 'login/servericon/commend.igs', interface.UIPath)
        (offx, offy) = style.GetIntTuple(self.GetDlgPath(), 'offpos_TjImg')
        img.SetPos(131 + offx, 5 + offy)
        img.SetZ(1)
        btn.m_TjImg = img

    
    def DelTjImg(self, btn):
        btn.m_TjImg = None

    
    def Refresh(self, serverList):
        import combdialog
        import math
        (x, y, w, h) = self.GetLocData('loc_Scroll')
        num = max(int(math.ceil(len(serverList) / 3)), 4)
        self.m_ShowList = serverList
        barClass = None if interface.IsNewStyle() else combdialog.CVScrollBar
        self.m_ScrollBar = barClass(self, h, num, 4, 1)
        self.m_ScrollBar.SetPos(x, y)
        self.m_ScrollBar.SetBarPos(0)

    
    def MouseWheelDown(self, p):
        if hasattr(self, 'm_ScrollBar') and self.m_ScrollBar:
            bp = self.m_ScrollBar.GetPos()
            self.m_ScrollBar.SetBarPos(bp + p)
        

    
    def MouseWheelUp(self, p):
        if hasattr(self, 'm_ScrollBar'):
            del self
            if None.m_ScrollBar:
                bp = self.m_ScrollBar.GetPos()
                self.m_ScrollBar.SetBarPos(bp - p)
            

    
    def RefreshWithPos(self, pos):
        pos *= 3
        lst = self.m_ShowList[pos:pos + 12]
        idx = 0
        for serverID, name in lst:
            btn = self.GetObject('btn_Telecom%d' % (idx + 1))
            btn.SetText(name)
            btn.m_ServerID = serverID
            btn.SetShow(True)
            btn.SetSelect(self.m_NormalSelect == serverID)
            if (serverID, name) in self.m_TjList:
                self.CreateTjImg(btn)
            else:
                self.DelTjImg(btn)
            idx += 1
        
        for i in xrange(idx, 12):
            btnName = 'btn_Telecom%d' % (i + 1)
            btn = self.GetObject(btnName)
            btn.SetSelect(False)
            btn.SetShow(False)
        

    
    def BarChange(self, pos):
        self.RefreshWithPos(pos)

    
    def OnSelectNormal(self, idx):
        btnName = 'btn_Telecom%d' % (idx + 1)
        btn = self.GetObject(btnName)
        self.m_NormalSelect = btn.m_ServerID
        self.m_TjSelect = None

    
    def OnSelectTj(self, idx):
        btnName = 'btn_Suggust%d' % (idx + 1)
        btn = self.GetObject(btnName)
        self.m_TjSelect = btn.m_ServerID
        self.m_NormalSelect = None

    
    def GetSelect(self):
        nameLst = [] + [ 'btn_Suggust%d' % i for i in range(1, 5) ]
        for btnName in nameLst:
            btn = self.GetObject(btnName)
            if btn.IsSelected() and btn.GetShow():
                return btn
                continue
            []
        

    
    def CommitMove(self):
        import netcommon
        import usermacro
        selBtn = self.GetSelect()
        if not selBtn:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xaaA\xb0\xc8\xbe\xb9')
            return None
        
        netcommon.C2SSelectYiminServer(self.m_NpcID, self.m_Mode, selBtn.m_ServerID)

    
    def CloseWindow(self):
        global g_MoveServerDlg
        g_MoveServerDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.CommitMove()
        elif msgid == 28:
            self.Refresh(self.m_TelecomList)
            self.m_NormalSelect = None
            self.m_TjSelect = None
        elif msgid == 29:
            self.Refresh(self.m_WangtongList)
            self.m_NormalSelect = None
            self.m_TjSelect = None
        elif msgid <= msgid:
            pass
        elif msgid <= 146:
            self.OnSelectNormal(msgid - 135)
        elif msgid <= msgid:
            pass
        elif msgid <= 93:
            self.OnSelectTj(msgid - 90)
