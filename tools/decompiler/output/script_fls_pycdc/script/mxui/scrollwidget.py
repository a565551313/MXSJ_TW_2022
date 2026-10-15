# pycdc 交叉复核产物 · script.fls entry 3407
# co_filename(原始)='script/mxui/scrollwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3407.pyc (Python 2.5)

'''
\xb9\xf6\xb6\xaf\xcc\xf5\xbf\xd8\xbc\xfe
'''
import interface
import framewidget
import scrolldata

class CVScrollBar(interface.CContainerObject, interface.CBase):
    
    def __init__(self, oParent, h, n_max = 1, n_page = 1, unit = 1, sType = None, bButtonShow = True):
        interface.CContainerObject.__init__(self, oParent)
        self.MessageProcess()
        self.m_Height = h
        self.m_nMax = n_max
        self.m_nPage = n_page
        self.m_Unit = unit
        self.m_ButtonShow = bButtonShow
        self.m_Bar = None
        self.InitStyle(sType)

    
    def Create(cls, oParent, data, dUIInfo = None):
        if dUIInfo is None:
            h = int(data.pop())
        else:
            h = dUIInfo['iHeight']
        return CVScrollBar(oParent, h)

    Create = classmethod(Create)
    
    def InitStyle(self, sType):
        if sType is None:
            sType = scrolldata.DEFAULT_TYPE
        
        self.m_ScrollInfo = scrolldata.GetScrollInfo(sType)
        self.CreateVFrameIamge(self.m_Height)
        if self.m_ButtonShow:
            
            try:
                self.CreateBarButton()
            self.m_UpButton = None
            self.m_DownButton = None
            self.m_ButtonShow = False

        
        self.ReSetUpDownPOS(self.m_Height, self.m_nMax, self.m_nPage)

    
    def ResetStyle(self, sType, iStyle = None):
        '''
\t\t\xad\xab\xb7s\xb3]\xb8m\xb7\xc6\xb0\xca\xb1\xf8ui
\t\t:param str or None sType: \xb7s\xaa\xba\xc3\xfe\xab\xac
\t\t:param int or None iStyle: \xb3]\xb8m\xc2\xea\xa9w\xaa\xba\xad\xb7\xae\xe6\xc3\xfe\xab\xac None\xb4N\xacO\xb8\xf2\xc0H\xa8t\xb2\xce
\t\t'''
        if sType is None:
            sType = scrolldata.DEFAULT_TYPE
        
        self.m_ScrollInfo = scrolldata.GetScrollInfoByStyle(sType, iStyle)
        self.CreateVFrameIamge(self.m_Height)
        if self.m_ButtonShow:
            
            try:
                self.CreateBarButton()
            self.m_UpButton = None
            self.m_DownButton = None
            self.m_ButtonShow = False

        
        self.ReSetUpDownPOS(self.m_Height, self.m_nMax, self.m_nPage)

    
    def GetBar(self):
        return self.m_Bar

    
    def Reset(self, x, y, h, n_max = 1, n_page = 1, unit = 1):
        self.m_Height = h
        self.CreateVFrameIamge(h)
        self.m_Unit = unit
        self.SetPos(x, y)
        self.Set(n_max, n_page)

    
    def Set(self, n_max, n_page):
        self.m_nMax = n_max
        self.m_nPage = n_page
        if self.m_ButtonShow:
            if n_max <= n_page:
                None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.m_UpButton.Enable, False)
                self.m_DownButton.Enable(False)
            else:
                self.m_UpButton.Enable(True)
                self.m_DownButton.Enable(True)
        
        self.m_Bar.Reset(n_max, n_page)

    
    def GetWidth(self):
        (iw, ih) = self.m_Imagess.GetSize()
        return iw

    
    def GetHeight(self):
        return self.m_Height

    
    def SetBarPos(self, pos):
        self.m_Bar.SetBarPos(pos)
        self.PosChange(self.GetPos())

    
    def SetBarPosIfCallback(self, pos, bCallback = True):
        self.m_Bar.SetBarPos(pos, bCallback)

    
    def GetPos(self):
        return self.m_Bar.m_CurPos

    
    def GetObjPos(self):
        return interface.CContainerObject.GetPos(self)

    
    def GetSize(self):
        return (self.GetWidth(), self.GetHeight())

    
    def GetScrollInfo(self):
        return self.m_ScrollInfo

    
    def ReSetUpDownPOS(self, h, n_max, n_page):
        if n_max <= n_page:
            if self.m_ButtonShow:
                self.m_UpButton.Enable(False)
                self.m_DownButton.Enable(False)
            
        
        h -= self.m_ScrollInfo['tSliderOffset'][1] * 2
        (iOffsetX, iOffsetY) = self.m_ScrollInfo['tSliderOffset']
        self.m_Bar = CSliderBar(self, iOffsetY, n_max, n_page, h)
        self.m_Bar.SetPos(iOffsetX, 0)
        self.Set(n_max, n_page)

    
    def CreateBarButton(self):
        sUpPath = self.GetBtnPath(False)
        sDownPath = self.GetBtnPath(True)
        (x, y) = self.m_ScrollInfo['tUpOffSet']
        self.m_UpButton = CScrollButton(self, sUpPath, x, y, 1)
        self.m_UpButton.SetZ(2)
        (x, y) = self.m_ScrollInfo['tDownOffSet']
        self.m_DownButton = CScrollButton(self, sDownPath, x, y, 2)
        (_, iDownBtnH) = self.m_DownButton.GetSize()
        self.m_DownButton.SetPos(x, (self.m_Height - iDownBtnH) + y)
        self.m_DownButton.SetZ(2)

    
    def CreateVFrameIamge(self, h):
        sPath = self.m_ScrollInfo['sPath']
        (x, y) = self.m_ScrollInfo['tBgOffset']
        self.m_Imagess = framewidget.CVFrame(self, h, sPath)
        self.m_Imagess.SetPos(x, y)

    
    def LeftUp(self):
        if self.m_Bar is None:
            return None
        
        self.ReleaseChangeCmd()

    
    def ReleaseChangeCmd(self):
        if hasattr(self, 'm_ChangeLineCmd') and self.m_ChangeLineCmd:
            self.m_ChangeLineCmd.Release()
            self.m_ChangeLineCmd = None
        

    
    def LeftDown(self):
        import cursor
        
        def LineChange(obj, barobj, cx, cy, sign, curStep, totalStep, stepy, remainy):
            (x, y) = cursor.GetPos()
            bar = barobj.Get()
            if bar and cx == x and cy == y and curStep <= totalStep:
                if curStep == totalStep:
                    posY = (stepy + remainy) * sign
                else:
                    posY = stepy * sign
                bar.SetBarPos(bar.m_CurPos + posY)
                return (barobj, cx, cy, sign, curStep + 1, totalStep, stepy, remainy)
            

        interface.CBase.LeftDown(self)
        if self.m_Bar is None or not (self.m_Bar.m_MoveArea):
            return None
        
        (_, sy) = self.m_Bar.GetScreenPos()
        (cx, cy) = cursor.GetPos()
        step = 6
        if sy + 1 > cy:
            maxy = (sy - cy) * self.m_Bar.m_nMax / self.m_Bar.m_MoveArea
            sign = -1
        else:
            maxy = (cy - sy) * self.m_Bar.m_nMax / self.m_Bar.m_MoveArea
            sign = 1
        stepy = maxy / step
        remainy = maxy % step
        self.m_ChangeLineCmd = self.CreatePyCommand(5, LineChange, interface.CShadowObject(self.m_Bar), cx, cy, sign, 1, step, stepy, remainy)

    
    def PosChange(self, pos):
        par = self.GetParent()
        if par:
            par.BarChange(pos)
        

    
    def GetVScrollBarPath(self):
        return self.m_ScrollInfo['sPath']

    
    def OnMessage(self, msgid, ignore = False):
        import time
        t = time.time() * 1000
        if msgid == 1:
            if hasattr(self, 'm_ClickTime') and t - self.m_ClickTime < 300 and not ignore:
                self.m_Bar.SetBarPos(0)
                return None
            
            self.m_ClickTime = t
            self.m_Bar.SetBarPos(self.m_Bar.m_CurPos - self.m_Unit)
        elif msgid == 2:
            if hasattr(self, 'm_ClickTime') and t - self.m_ClickTime < 300 and not ignore:
                par = self.GetParent()
                if par and hasattr(par, 'OnMaxiBar') and par.OnMaxiBar(self):
                    pass
                else:
                    self.SetBarPos(self.m_nMax)
                return None
            
            self.m_ClickTime = t
            self.m_Bar.SetBarPos(self.m_Bar.m_CurPos + self.m_Unit)
        

    
    def GetBtnPath(self, bDown):
        sRootPath = self.m_ScrollInfo['sPath']
        bIgs = self.m_ScrollInfo['bIgs']
        if bIgs:
            if bDown:
                sPath = sRootPath + 'down.igs'
            else:
                sPath = sRootPath + 'up.igs'
        elif bDown:
            sPath = sRootPath + 'down/'
        else:
            sPath = sRootPath + 'up/'
        return sPath



class CSliderBar(interface.CContainerObject, interface.CHoldObject):
    
    def __init__(self, parent, y, n_max, n_page, h):
        interface.CContainerObject.__init__(self, parent)
        self.m_Y = y
        self.m_Height = h
        self.m_CurPos = 0
        self.Reset(n_max, n_page)
        self.MessageProcess()
        self.SetZ(1)

    
    def Reset(self, n_max, n_page):
        if n_max < 0:
            n_max = 0
        
        if n_max > n_page:
            barh = self.m_Height * n_page / n_max
        else:
            barh = self.m_Height
        if barh < 24:
            barh = 24
        
        self.m_MoveArea = self.m_Height - barh
        self.m_nMax = n_max - n_page
        self.m_nPage = n_page
        if n_max > n_page:
            self.CreateBarImages(barh)
            self.SetShow(True)
        else:
            self.m_Imagess = None
            self.SetShow(False)

    
    def CreateBarImages(self, barh):
        oParent = self.GetParent()
        if oParent:
            dInfo = oParent.GetScrollInfo()
            sPath = dInfo['sPath']
            self.m_Imagess = framewidget.CVFrame(self, barh, sPath + 'bar/', bIsBar = True)
        

    
    def GetPos(self):
        (x, y) = interface.CContainerObject.GetPos(self)
        return (x, y - self.m_Y)

    
    def SetPos(self, x, y):
        interface.CContainerObject.SetPos(self, x, y + self.m_Y)

    
    def Hold(self):
        import cursor
        if self.m_MoveArea == 0:
            return None
        
        (mx, my) = cursor.GetPos()
        (objx, _) = self.GetPos()
        y = my - interface.HoldY
        if y < 0:
            y = 0
        elif y > self.m_MoveArea:
            y = self.m_MoveArea
        
        pos = self.m_nMax * y / self.m_MoveArea
        if pos != self.m_CurPos:
            self.m_CurPos = y * self.m_nMax / self.m_MoveArea
            self.GetParent().PosChange(pos)
        
        self.SetPos(objx, y)

    
    def SetBarPos(self, pos, bCallback = True):
        if pos < 0:
            pos = 0
        elif pos > self.m_nMax:
            pos = max(self.m_nMax, 0)
        
        if self.m_nMax == 0:
            return None
        
        y = pos * self.m_MoveArea / self.m_nMax
        (objx, _) = self.GetPos()
        self.SetPos(objx, y)
        if pos == self.m_CurPos:
            return None
        
        self.m_CurPos = pos
        if bCallback:
            oParent = self.GetParent()
            if oParent:
                oParent.PosChange(pos)
            
        

    
    def LeftDown(self):
        self.Capture(1, 1)
        interface.CHoldObject.LeftDown(self)

    
    def LeftUp(self):
        self.Capture(0)
        interface.CHoldObject.LeftUp(self)

    
    def RightUp(self):
        self.LeftUp()

    
    def MouseWheelDown(self, p):
        par = self.GetParent()
        if getattr(par, 'MouseWheelDown', None):
            par.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        par = self.GetParent()
        if getattr(self, 'MouseWheelUp', None):
            par.MouseWheelUp(p)
        

    
    def SetBarPosWithoutScroll(self, pos):
        if pos < 0:
            pos = 0
        elif pos > self.m_nMax:
            pos = self.m_nMax
        
        if self.m_nMax == 0:
            return None
        
        y = pos * self.m_MoveArea / self.m_nMax
        (objx, _) = self.GetPos()
        self.SetPos(objx, y)
        if pos == self.m_CurPos:
            return None
        
        self.m_CurPos = pos



class CScrollButton(interface.CButton):
    
    def LeftUp(self):
        self.SetFrame(2)
        if hasattr(self, 'm_ChangeLineCmd') and self.m_ChangeLineCmd:
            self.m_ChangeLineCmd.Release()
            self.m_ChangeLineCmd = None
        

    
    def LeftDown(self):
        import cursor
        
        def LineChange(obj, cx, cy):
            par = obj.GetParent()
            (x, y) = cursor.GetPos()
            if par and cx == x and cy == y:
                par.OnMessage(obj.m_MsgID, ignore = True)
                return (cx, cy)
            

        interface.CButton.LeftDown(self)
        (cx, cy) = cursor.GetPos()
        self.m_ChangeLineCmd = self.CreatePyCommand(3, LineChange, cx, cy)
