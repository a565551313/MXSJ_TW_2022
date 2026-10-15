# pycdc 交叉复核产物 · script.fls entry 1678
# co_filename(原始)='script/dialog/dlgpickimg.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1678.pyc (Python 2.5)

import interface
import combdialog
import wrapinterface
import misc
g_PickDlg = None
BK = None
SAVEPATH = 'photo/preview/'

def ModuleReset():
    global g_PickDlg, BK
    g_PickDlg = None
    BK = None


def ShowPicSelect(owner, path, prew, preh, limitedw = 800, limitedh = 600, iType = 0):
    global g_PickDlg, g_PickDlg, g_PickDlg
    import usermacro
    
    try:
        image = interface.CStretchBitmapObject(None, path)
    except:
        image = None
        usermacro.PROMPT_MSG('\xb9\xcf\xa4\xf9\xae\xe6\xa6\xa1\xa5X\xbf\xf9\xa1A\xb5L\xaak\xbf\xef\xa8\xfa\xc1Y\xb2\xa4\xb9\xcf')
        usermacro.NORMAL_MSG('\xb9\xcf\xa4\xf9\xae\xe6\xa6\xa1\xa5X\xbf\xf9\xa1A\xb5L\xaak\xbf\xef\xa8\xfa\xc1Y\xb2\xa4\xb9\xcf')
        return None

    if image and image.GetSize()[0] <= limitedw and image.GetSize()[1] <= limitedh:
        if iType == 1:
            g_PickDlg = CPickYearVoiceImgDlg(owner, path, prew, preh)
        else:
            g_PickDlg = CPickImgDlg(owner, path, prew, preh)
    else:
        usermacro.PROMPT_MSG('\xb9\xcf\xa4\xf9\xa4\xd8\xa4o\xb9L\xa4j\xa1A\xb5L\xaak\xbf\xef\xa8\xfa\xc1Y\xb2\xa4\xb9\xcf')
        usermacro.NORMAL_MSG('\xb9\xcf\xa4\xf9\xa4\xd8\xa4o\xb9L\xa4j\xa1A\xb5L\xaak\xbf\xef\xa8\xfa\xc1Y\xb2\xa4\xb9\xcf')
        g_PickDlg = None


def SetPicImgDlgConfirmCB(oCB):
    if g_PickDlg:
        g_PickDlg.SetConfirmCB(oCB)
    


class CHandleImg(interface.CBoxObject, interface.CHoldObject):
    
    class CHandlePoint(interface.CHoldObject, interface.CImagesObject):
        
        def __init__(self, parent, msgid, offset = (3, 3)):
            interface.CImagesObject.__init__(self, parent, 'combdialog/\xd4\xd3\xcd\xbc/\xcc\xe1\xd0\xd1\xba\xec\xb5\xe3.igs', interface.UIPath)
            self.MessageProcess()
            self.m_MsgID = msgid
            self.m_LastPos = None
            self.m_Offset = offset

        
        def SetLastPos(self):
            import cursor
            (x, y) = cursor.GetPos()
            self.m_LastPos = (x, y)

        
        def Hold(self):
            import cursor
            parent = self.GetParent()
            if parent:
                (x, y) = cursor.GetPos()
                if (x, y) == self.m_LastPos:
                    return None
                
                offsetx = x - self.m_LastPos[0]
                offsety = y - self.m_LastPos[1]
                self.m_LastPos = (x, y)
                parent.Resize(self.m_MsgID, offsetx, offsety)
            

        
        def LeftDown(self):
            interface.CHoldObject.LeftDown(self)
            self.SetLastPos()

        
        def LeftUp(self):
            interface.CHoldObject.LeftUp(self)


    
    def __init__(self, parent, w, h, minw = 20, minh = 20):
        interface.CBoxObject.__init__(self, parent, w, h, 0, 0)
        self.MessageProcess()
        interface.Center(self)
        self.m_MinW = minw
        self.m_MinH = minh
        self.m_MoveRule = [
            ((1, 1), (1, 1)),
            ((0, 1), (0, 1)),
            ((0, 1), (-1, 1)),
            ((0, 0), (-1, 0)),
            ((0, 0), (-1, -1)),
            ((0, 0), (0, -1)),
            ((1, 0), (1, -1)),
            ((1, 0), (1, 0))]
        self.m_Points = []
        for x in xrange(8):
            point = self.CHandlePoint(self, x + 1)
            self.m_Points.append(point)
        
        self.AdjustPoint()
        self.DrawEdge()

    
    def SetSize(self, w, h):
        interface.CBoxObject.SetSize(self, int(w), int(h))
        self.AdjustPoint()
        self.DrawEdge()

    
    def Resize(self, pos, x, y):
        px = self.m_MoveRule[pos - 1][0][0] * x
        py = self.m_MoveRule[pos - 1][0][1] * y
        wx = self.m_MoveRule[pos - 1][1][0] * x
        wy = self.m_MoveRule[pos - 1][1][1] * y
        (rx, ry) = self.GetPos()
        if rx + px <= 0 and px != 0:
            px = -rx
            wx = -rx
        
        if ry + py <= 0 and py != 0:
            py = -ry
            wy = -ry
        
        parent = self.GetParent()
        (rw, rh) = self.GetSize()
        if parent:
            (w, h) = parent.GetSize()
            if rx + px + rw - wx >= w:
                wx = -(w - (rx + px + rw))
            
            if rw - wx <= self.m_MinW:
                wx = 0
                px = 0
            
            if ry + py + rh - wy >= h:
                wy = -(h - (ry + py + rh))
            
            if rh - wy <= self.m_MinH:
                wy = 0
                py = 0
            
        
        self.SetPos(rx + px, ry + py)
        self.SetSize(rw - wx, rh - wy)
        self.GetParent().Adjust()

    
    def LeftDown(self):
        import cursor
        (x, y) = cursor.GetPos()
        self.m_LastCursorPos = [
            x,
            y]
        interface.CHoldObject.LeftDown(self)

    
    def DrawEdge(self):
        (w, h) = self.GetSize()
        self.m_BGs = wrapinterface.DrawEdge(self, w - 3, h - 3, 3, 3)

    
    def AdjustPoint(self):
        if not hasattr(self, 'm_Points'):
            return None
        
        poslist = {
            1: (0, 0),
            2: (0.5, 0),
            3: (1, 0),
            4: (1, 0.5),
            5: (1, 1),
            6: (0.5, 1),
            7: (0, 1),
            8: (0, 0.5) }
        (w, h) = self.GetSize()
        for idx, point in enumerate(self.m_Points):
            point.SetPos(int(w * poslist[idx + 1][0]) - 6, int(h * poslist[idx + 1][1]) - 6)
        

    
    def Hold(self):
        import cursor
        parent = self.GetParent()
        (x, y) = cursor.GetPos()
        wx = x - self.m_LastCursorPos[0]
        wy = y - self.m_LastCursorPos[1]
        if parent:
            (rw, rh) = self.GetSize()
            (rx, ry) = self.GetPos()
            (w, h) = parent.GetSize()
            sx = -1
            sy = -1
            if rx + wx < 0:
                sx = 0
            elif rx + wx + rw > w:
                sx = w - rw
            
            if ry + wy < 0:
                sy = 0
            elif ry + wy + rh > h:
                sy = h - rh
            
            if sx == -1:
                sx = x - interface.HoldX
                self.m_LastCursorPos[0] = x
            
            if sy == -1:
                sy = y - interface.HoldY
                self.m_LastCursorPos[1] = y
            
            self.SetPos(sx, sy)
            self.GetParent().Adjust()
        



class ClimitedHandleImg(CHandleImg):
    
    def __init__(self, parent, w, h, minw = 20, minh = 20):
        CHandleImg.__init__(self, parent, w, h, minw, minh)
        self.m_LimitedSize = (w, h)
        self.m_MoveRule = [
            ((1, 1), (-1, -1)),
            ((0.5, 1), (0, -1)),
            ((0, 1), (1, -1)),
            ((0, 0.5), (1, 0)),
            ((0, 0), (1, 1)),
            ((0.5, 0), (0, 1)),
            ((1, 0), (-1, 1)),
            ((1, 0.5), (-1, 0))]
        self.m_Flag = 0
        self.m_LastScale = 0

    
    def Resize(self, pos, x, y):
        import math
        wx = self.m_MoveRule[pos - 1][1][0] * x
        wy = self.m_MoveRule[pos - 1][1][1] * y
        (rw, rh) = self.GetSize()
        flag = 0
        if (wx >= 0 or wy >= 0 or wx <= 0) and wy <= 0:
            if abs(wx) >= abs(wy):
                flag = 1
                wy = wx * rh / rw
            elif abs(wx) < abs(wy):
                flag = 2
                wx = wy * rw / rh
            
        elif wx > 0:
            flag = 1
            wy = wx * rh / rw
        else:
            flag = 2
            wx = wy * rw / rh
        px = wx * self.m_MoveRule[pos - 1][0][0]
        py = wy * self.m_MoveRule[pos - 1][0][1]
        self.m_Flag = (self.m_Flag + 1) % 2
        if self.m_Flag == 0:
            px = math.ceil(px)
            py = math.ceil(py)
        else:
            px = math.floor(px)
            py = math.floor(py)
        (rx, ry) = self.GetPos()
        if rx - px <= 0 and px != 0:
            px = rx
            wx = rx / self.m_MoveRule[pos - 1][0][0]
            wy = wx * rh / rw
            py = wy * self.m_MoveRule[pos - 1][0][1]
        
        if ry - py <= 0 and py != 0:
            py = ry
            wy = ry / self.m_MoveRule[pos - 1][0][1]
            wx = wy * rw / rh
            px = wx * self.m_MoveRule[pos - 1][0][0]
        
        parent = self.GetParent()
        if parent:
            (w, h) = parent.GetSize()
            if (rx - px) + rw + wx > w:
                wx = 0
                wy = 0
                if pos != 8:
                    py = 0
                
            
            if (ry - py) + rh + wy > h:
                wy = 0
                wx = 0
                if pos != 2:
                    px = 0
                
            
        
        if flag == 1:
            scale = 1 * (rw + wx) / self.m_LimitedSize[0]
        else:
            scale = 1 * (rh + wy) / self.m_LimitedSize[1]
        if scale < 0.3 or abs(scale - self.m_LastScale) < 0.01:
            return None
        
        self.SetScale(scale)
        self.SetPos(rx - int(px), ry - int(py))
        self.GetParent().Adjust()

    
    def SetScale(self, scale):
        self.m_LastScale = scale
        (w, h) = self.m_LimitedSize
        self.SetSize(w * scale, h * scale)



class CPickImg(interface.CBoxObject):
    
    def __init__(self, pic, prew, preh):
        (w, h) = pic.GetSize()
        interface.CBoxObject.__init__(self, pic, w, h, 0, 0)
        self.m_Mask = { }
        for name in ('up', 'down', 'left', 'right'):
            img = interface.CBoxObject(self, 1, 1, 0, 160)
            img.SetZ(0)
            self.m_Mask[name] = img
        
        img = ClimitedHandleImg(self, prew, preh, 260, 260)
        interface.Center(img)
        self.m_Mask['center'] = img
        self.Adjust()

    
    def Adjust(self):
        if 'center' not in self.m_Mask:
            return None
        
        (w, h) = self.GetSize()
        (cx, cy) = self.m_Mask['center'].GetPos()
        (cw, ch) = self.m_Mask['center'].GetSize()
        if cw <= 0 or cy <= 0:
            self.m_Mask['up'].SetShow(False)
        else:
            self.m_Mask['up'].SetShow(True)
            self.m_Mask['up'].SetPos(cx, 0)
            self.m_Mask['up'].SetSize(cw, cy)
        if cw <= 0 or h - cy - ch <= 0:
            self.m_Mask['down'].SetShow(False)
        else:
            self.m_Mask['down'].SetShow(True)
            self.m_Mask['down'].SetPos(cx, cy + ch)
            self.m_Mask['down'].SetSize(cw, h - cy - ch)
        if cx <= 0 or h <= 0:
            self.m_Mask['left'].SetShow(False)
        else:
            self.m_Mask['left'].SetShow(True)
            self.m_Mask['left'].SetPos(0, 0)
            self.m_Mask['left'].SetSize(cx, h)
        if w - cx - cw <= 0 or h <= 0:
            self.m_Mask['right'].SetShow(False)
        else:
            self.m_Mask['right'].SetShow(True)
            self.m_Mask['right'].SetPos(cx + cw, 0)
            self.m_Mask['right'].SetSize(w - cx - cw, h)
        self.m_Mask['center'].SetZ(1000)

    
    def Select(self, savepath):
        self.m_SavePath = savepath
        (x, y) = self.m_Mask['center'].GetScreenPos()
        (w, h) = self.m_Mask['center'].GetSize()
        self.ReleaseTimer()
        self.m_Mask['center'].SetShow(False)
        
        def Shot(obj, x, y, w, h):
            global BK
            BK = interface.CSnapshotBitmapObject(None, savepath, x, y, w, h)
            obj.m_Mask['center'].SetShow(True)

        self.m_Timer = self.CreatePyCommand(2, Shot, x, y, w, h)

    
    def ReleaseTimer(self):
        if getattr(self, 'm_Timer', None):
            self.m_Timer.Release()
            self.m_Timer = None
        



class CPickImgDlg(combdialog.CCombDialog):
    
    class CPreviewDlg(combdialog.CCombDialog):
        
        def __init__(self, owner, w, h, path):
            combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/player_show/preview.dlg')
            self.m_Bg = interface.CStretchBitmapObject(self, path)
            self.m_Owner = misc.WeakRef(owner)
            self.m_Bg.Resize(w, h)
            interface.Center(self)
            interface.Center(self.m_Bg)
            self.Capture(1, 0)

        
        def RightUp(self):
            self.Cancle()

        
        def Cancle(self):
            parent = self.m_Owner.Get()
            if parent and hasattr(parent, 'ClosePreview'):
                parent.ClosePreview()
            

        
        def Confirm(self):
            parent = self.m_Owner.Get()
            if parent and hasattr(parent, 'ConfirmPreview'):
                parent.ConfirmPreview()
            

        
        def OnMessage(self, msgid):
            if msgid in (1, 3):
                self.Cancle()
            elif msgid == 2:
                self.Confirm()
            


    
    def __init__(self, owner, path, prew, preh):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/player_show/pickimg.dlg')
        interface.Center(self)
        self.ResizeBg(path)
        (w, h) = self.m_oImg.GetSize()
        if prew >= w:
            preh = preh * (w - 2) / prew
            prew = w - 2
        
        self.m_PreviewW = prew
        self.m_PreviewH = preh
        self.m_Owner = misc.WeakRef(owner)
        self.m_ConfirmCB = None
        self.ShowPicSelect(self.m_oImg)
        self.InitBtnTips()
        self.Capture(1, 0)
        import \xb4ey
        \xb4ey.RegisterHotKey(\xb4ey.VK_ENTER, self.Shot)

    
    def SetConfirmCB(self, oCB):
        self.m_ConfirmCB = oCB

    
    def ResizeBg(self, path):
        self.m_oImg = interface.CStretchBitmapObject(self, path)
        oBg = self.GetObject('img_Bg')
        (iBgW, iBgH) = oBg.GetSize()
        (iImgW, iImgH) = self.m_oImg.GetSize()
        if iImgW > iBgW and iImgH < iBgH:
            w = iBgW
            h = int((float(iBgW) / iImgW) * iImgH)
        elif iImgW < iBgW and iImgH > iBgH:
            w = int((float(iBgH) / iImgH) * iImgW)
            h = iBgH
        elif iImgW > iBgW and iImgH > iBgH:
            w1 = int((float(iBgH) / iImgH) * iImgW)
            h1 = iBgH
            w2 = int((float(iBgH) / iImgH) * iImgW)
            h2 = iBgH
            if w1 <= iBgW and h1 <= iBgH:
                w = w1
                h = h1
            else:
                w = w2
                h = h2
        else:
            w = iImgW
            h = iImgH
        self.m_oImg.Resize(w, h)
        interface.AlignObjects(self.m_oImg, self.GetObject('img_Bg'), interface.ALIGN_CENTER_MIDDLE)

    
    def InitBtnTips(self):
        btn = self.GetObject('btn_ok')
        if btn:
            btn.m_TipsStr = '\xab\xf6Enter\xc1\xe4\xa5i\xb6i\xa6\xe6\xbaI\xb9\xcf'
            btn.m_TipsDirect = 2
        

    
    def ShowPicSelect(self, pic):
        self.m_Pick = CPickImg(pic, self.m_PreviewW, self.m_PreviewH)
        self.m_Pick.SetZ(1000)
        self.m_Pick.SetShow(True)

    
    def ClosePreview(self, delflag = True):
        import os
        self.m_Panel = None
        self.m_Pick.SetShow(True)
        if delflag and os.path.isfile(self.m_SavePath):
            os.remove(self.m_SavePath)
        

    
    def ConfirmPreview(self):
        if hasattr(self, 'm_Owner') and self.m_Owner:
            owner = self.m_Owner.Get()
            if owner and hasattr(owner, 'ConfirmThumbnail'):
                owner.ConfirmThumbnail(self.m_SavePath)
            
        
        if self.m_ConfirmCB:
            pass
        self.m_ConfirmCB(self.m_SavePath)
        self.CloseWindow()

    
    def ShowPreview(self):
        import screenshotpublic
        self.m_Pick.SetShow(False)
        
        def onfinish(obj):
            obj.m_Panel = CPickImgDlg.CPreviewDlg(obj, obj.m_PreviewW, obj.m_PreviewH, obj.m_SavePath)

        screenshotpublic.WaitForShotOver(self.m_SavePath, 15, '\xbaI\xb9\xcf\xabO\xa6s\xa5\xa2\xb1\xd1\xa1A\xbd\xd0\xad\xab\xb7s\xbaI\xb9\xcf', onfinish, (self,))

    
    def Shot(self):
        import hero
        import os
        self.m_SavePath = SAVEPATH + str(hero.g_ID) + str(int(misc.Time())) + '.jpg'
        if not os.path.isdir(SAVEPATH):
            os.makedirs(SAVEPATH)
        
        self.m_Pick.Select(self.m_SavePath)
        self.ShowPreview()

    
    def CloseWindow(self):
        global g_PickDlg
        g_PickDlg = None
        import \xb4ey
        \xb4ey.RegisterHotKey(\xb4ey.VK_ENTER)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.Shot()
        



class CPickYearVoiceImgDlg(combdialog.CCombDialog):
    
    class CPreviewDlg(combdialog.CCombDialog):
        
        def __init__(self, owner, w, h, path):
            combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog4/yearvoice/preview.dlg')
            self.m_Bg = interface.CStretchBitmapObject(self, path)
            self.m_Owner = misc.WeakRef(owner)
            self.m_Bg.Resize(w, h)
            interface.Center(self)
            interface.Center(self.m_Bg)
            self.Capture(1, 0)

        
        def RightUp(self):
            self.Cancle()

        
        def Cancle(self):
            parent = self.m_Owner.Get()
            if parent and hasattr(parent, 'ClosePreview'):
                parent.ClosePreview()
            

        
        def Confirm(self):
            parent = self.m_Owner.Get()
            if parent and hasattr(parent, 'ConfirmPreview'):
                parent.ConfirmPreview()
            

        
        def OnMessage(self, msgid):
            if msgid in (1, 3):
                self.Cancle()
            elif msgid == 2:
                self.Confirm()
            


    
    def __init__(self, owner, path, prew, preh):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog4/yearvoice/pickimg.dlg')
        interface.Center(self)
        self.ResizeBg(path)
        (w, h) = self.m_oImg.GetSize()
        if prew >= w:
            preh = preh * (w - 2) / prew
            prew = w - 2
        
        self.m_PreviewW = prew
        self.m_PreviewH = preh
        self.m_Owner = misc.WeakRef(owner)
        self.m_ConfirmCB = None
        self.ShowPicSelect(self.m_oImg)
        self.InitBtnTips()
        self.Capture(1, 0)
        import \xb4ey
        \xb4ey.RegisterHotKey(\xb4ey.VK_ENTER, self.Shot)

    
    def SetConfirmCB(self, oCB):
        self.m_ConfirmCB = oCB

    
    def ResizeBg(self, path):
        self.m_oImg = interface.CStretchBitmapObject(self, path)
        oBg = self.GetObject('img_Bg')
        (iBgW, iBgH) = oBg.GetSize()
        (iImgW, iImgH) = self.m_oImg.GetSize()
        if iImgW > iBgW and iImgH < iBgH:
            w = iBgW
            h = int((float(iBgW) / iImgW) * iImgH)
        elif iImgW < iBgW and iImgH > iBgH:
            w = int((float(iBgH) / iImgH) * iImgW)
            h = iBgH
        elif iImgW > iBgW and iImgH > iBgH:
            w1 = int((float(iBgH) / iImgH) * iImgW)
            h1 = iBgH
            w2 = int((float(iBgH) / iImgH) * iImgW)
            h2 = iBgH
            if w1 <= iBgW and h1 <= iBgH:
                w = w1
                h = h1
            else:
                w = w2
                h = h2
        else:
            w = iImgW
            h = iImgH
        self.m_oImg.Resize(w, h)
        interface.AlignObjects(self.m_oImg, self.GetObject('img_Bg'), interface.ALIGN_CENTER_MIDDLE)

    
    def InitBtnTips(self):
        btn = self.GetObject('btn_ok')
        if btn:
            btn.m_TipsStr = '\xab\xf6Enter\xc1\xe4\xa5i\xb6i\xa6\xe6\xbaI\xb9\xcf'
            btn.m_TipsDirect = 2
        

    
    def ShowPicSelect(self, pic):
        self.m_Pick = CPickImg(pic, self.m_PreviewW, self.m_PreviewH)
        self.m_Pick.SetZ(1000)
        self.m_Pick.SetShow(True)

    
    def ClosePreview(self, delflag = True):
        import os
        self.m_Panel = None
        self.m_Pick.SetShow(True)
        if delflag and os.path.isfile(self.m_SavePath):
            os.remove(self.m_SavePath)
        

    
    def ConfirmPreview(self):
        if hasattr(self, 'm_Owner') and self.m_Owner:
            owner = self.m_Owner.Get()
            if owner and hasattr(owner, 'ConfirmThumbnail'):
                owner.ConfirmThumbnail(self.m_SavePath)
            
        
        if self.m_ConfirmCB:
            pass
        self.m_ConfirmCB(self.m_SavePath)
        self.CloseWindow()

    
    def ShowPreview(self):
        import screenshotpublic
        self.m_Pick.SetShow(False)
        
        def onfinish(obj):
            obj.m_Panel = CPickYearVoiceImgDlg.CPreviewDlg(obj, obj.m_PreviewW, obj.m_PreviewH, obj.m_SavePath)

        screenshotpublic.WaitForShotOver(self.m_SavePath, 15, '\xbaI\xb9\xcf\xabO\xa6s\xa5\xa2\xb1\xd1\xa1A\xbd\xd0\xad\xab\xb7s\xbaI\xb9\xcf', onfinish, (self,))

    
    def Shot(self):
        import hero
        import os
        self.m_SavePath = SAVEPATH + str(hero.g_ID) + str(int(misc.Time())) + '.jpg'
        if not os.path.isdir(SAVEPATH):
            os.makedirs(SAVEPATH)
        
        self.m_Pick.Select(self.m_SavePath)
        self.ShowPreview()

    
    def CloseWindow(self):
        global g_PickDlg
        g_PickDlg = None
        import \xb4ey
        \xb4ey.RegisterHotKey(\xb4ey.VK_ENTER)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.Shot()
