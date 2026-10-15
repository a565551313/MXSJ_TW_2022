# pycdc 交叉复核产物 · script.fls entry 1828
# co_filename(原始)='script/mxui/sliderwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1828.pyc (Python 2.5)

import cursor
import framewidget
import imagewidget
import interface
import ui
import misc
TYPE_DRAG = 1
TYPE_CUT = 2

class CSlider(interface.CContainerObject, interface.CBase):
    
    def __init__(self, oParent, w, sBgPath, sSliderPath, sBarPath, iType, tOffset, iSpace):
        interface.CContainerObject.__init__(self, oParent)
        self.m_Width = w
        self.m_Height = 0
        self.m_BgPath = sBgPath
        self.m_SliderPath = sSliderPath
        self.m_Type = iType
        self.m_Offset = tOffset
        self.m_Space = iSpace
        self.m_BarPath = sBarPath
        self.m_BgObj = None
        self.m_BarObj = None
        self.m_SliderObj = None
        self.m_Rate = 1000
        self.m_HotAreaObj = None
        self.m_ChangeCB = None
        self.m_bShowBg = len(self.m_BgPath) > 0
        self.CreateBg()
        self.CreateSlider()
        self.CreateBar()
        self.CreateHotArea()
        self.SetRate(0)

    
    def Create(cls, oParent, sDataList, dUIInfo = None):
        if dUIInfo is None:
            w = int(sDataList.pop())
            sBgPath = sDataList.pop()
            sSliderPath = sDataList.pop()
            sBarPath = sDataList.pop()
            iType = int(sDataList.pop())
            iOffsetX = int(sDataList.pop())
            iOffsetY = int(sDataList.pop())
            iBarSpace = int(sDataList.pop())
        else:
            w = dUIInfo['iWidth']
            sBgPath = dUIInfo['sBgPath']
            sBarPath = dUIInfo['sBarPath']
            sSliderPath = dUIInfo['sSliderPath']
            iType = dUIInfo['iType']
            iOffsetX = dUIInfo['iOffsetX']
            iOffsetY = dUIInfo['iOffsetY']
            iBarSpace = dUIInfo['iSpace']
        return CSlider(oParent, w, sBgPath, sSliderPath, sBarPath, iType, (iOffsetX, iOffsetY), iBarSpace)

    Create = classmethod(Create)
    
    def GetInitInfo(self):
        return (self.m_Width, self.m_BgPath, self.m_SliderPath, self.m_BarPath, self.m_Type, self.m_Offset, self.m_Space)

    
    def GetSize(self):
        return (self.m_Width, self.m_Height)

    
    def CreateHotArea(self):
        self.m_HotAreaObj = ui.CHotBox(self, self.m_Width, self.m_Height, 0)
        self.m_HotAreaObj.SetMouseWheelEnable(True)
        self.m_HotAreaObj.SetLeftUpCB(misc.qBnctor(self.OnSliderLeftUp))

    
    def OnSliderLeftUp(self):
        (sx, _) = self.GetScreenPos()
        (mx, _) = cursor.GetPos()
        p = (mx - sx) * self.m_Width / self.m_BarObj.m_MoveArea
        self.m_BarObj.SetBarPos(p)

    
    def SetRate(self, iRate, bForce = False):
        '''
\t\t:param iRate: \xb3]\xb8m\xa6\xca\xa4\xc0\xa4\xf1 1000\xac\xb0100%
\t\t:param bForce: \xacO\xa7_\xb1j\xa8\xee\xa8\xea\xb7s
\t\t:return:
\t\t'''
        iRate = max(0, iRate)
        iRate = min(1000, iRate)
        if self.m_Rate == iRate and not bForce:
            return None
        
        self.m_Rate = iRate
        if self.m_ChangeCB and callable(self.m_ChangeCB):
            self.m_ChangeCB(iRate)
        
        w = int((self.m_Width - self.m_Space * 2) * iRate / 1000)
        if w < 1:
            self.m_SliderObj.SetShow(False)
            return None
        
        self.m_SliderObj.SetShow(True)
        self.m_SliderObj.SetWidth(w)

    
    def GetRate(self):
        return self.m_Rate

    
    def SetChangeCB(self, oFunc, *args):
        import misc
        self.m_ChangeCB = misc.qBnctor(oFunc, *args)

    
    def ChangeBarPath(self, sPath):
        self.m_SliderPath = sPath
        self.CreateSlider()
        self.SetRate(self.GetRate(), bForce = True)

    
    def GetBarPath(self):
        return self.m_SliderPath

    
    def CreateBg(self):
        if not self.m_bShowBg:
            return None
        
        if CheckIsImg(self.m_BgPath):
            oImg = imagewidget.CImage(None, self.m_BgPath, interface.UIPath)
            (_, h) = oImg.GetSize()
            self.m_Height = h
            self.m_BgObj = CImageHFrame(self, self.m_BgPath, interface.UIPath, self.m_Width)
        else:
            self.m_BgObj = framewidget.CHFrame(self, self.m_Width, self.m_BgPath)
            (_, h) = self.m_BgObj.GetSize()
            self.m_Height = h

    
    def CreateSlider(self):
        iBarW = self.m_Width - self.m_Space * 2
        if CheckIsImg(self.m_SliderPath):
            self.m_SliderObj = CImageHFrame(self, self.m_SliderPath, interface.UIPath, iBarW)
        else:
            self.m_SliderObj = framewidget.CHProgressFrame(self, iBarW, self.m_SliderPath)
        if self.m_BgObj is None:
            (_, h) = self.m_SliderObj.GetSize()
            self.m_Height = h
        
        self.m_SliderObj.SetPos(self.m_Offset[0], self.m_Offset[1])
        self.m_SliderObj.SetZ(1)

    
    def CreateBar(self):
        self.m_BarObj = CSliderBar(self, self.m_Width, self.m_BarPath, interface.UIPath)
        self.m_BarObj.SetPos(self.m_Offset[0], self.m_Offset[1])
        self.m_BarObj.SetZ(2)

    
    def OnBarPosChange(self, *args):
        self.SetRate(self.m_BarObj.GetRate())

    
    def SetLight(self, iLight):
        if not self.m_SliderObj:
            return None
        
        self.m_SliderObj.SetLight(iLight)

    
    def MouseWheelDown(self, p):
        pos = self.m_BarObj.GetBarPos()
        pos = pos - p
        if pos < 0:
            pos = 0
        
        self.m_BarObj.SetBarPos(pos)

    
    def MouseWheelUp(self, p):
        pos = self.m_BarObj.GetBarPos()
        pos = pos + p
        if pos > self.m_BarObj.m_nMax:
            pos = self.m_BarObj.m_nMax
        
        self.m_BarObj.SetBarPos(pos)



class CSliderBar(interface.CBoxObject, interface.CHoldObject):
    
    def __init__(self, parent, n_max, fname, path):
        (w, h) = parent.GetSize()
        barw = 6
        barh = h + 10
        interface.CBoxObject.__init__(self, parent, barw, barh, 4489440, 0)
        if interface.IsIgsPath(fname):
            self.m_Image = interface.CImagesObject(self, fname, path)
        else:
            self.m_Image = interface.CBitmapObject(self, fname, path)
        (barw, barh) = self.m_Image.GetSize()
        self.SetSize(barw, barh)
        self.m_nMax = n_max
        self.m_MoveArea = w - barw
        self.m_CurPos = 0
        self.SetPos(0, -(barh - h) / 2)
        self.MessageProcess()

    
    def Hold(self):
        (mx, my) = cursor.GetPos()
        (_, objy) = self.GetPos()
        HoldX = self.GetHold()[1]
        x = mx - HoldX
        if x < 0:
            x = 0
        elif x > self.m_MoveArea:
            x = self.m_MoveArea
        
        pos = self.m_nMax * x / self.m_MoveArea
        if pos != self.m_CurPos:
            self.m_CurPos = x * self.m_nMax / self.m_MoveArea
            self.GetParent().OnBarPosChange(pos)
        
        self.SetPos(x, objy)

    
    def GetBarPos(self):
        return self.m_CurPos

    
    def SetBarPos(self, pos):
        if pos < 0:
            pos = 0
        elif pos > self.m_nMax:
            pos = self.m_nMax
        
        x = pos * self.m_MoveArea / self.m_nMax
        (_, objy) = self.GetPos()
        self.SetPos(x, objy)
        if pos == self.m_CurPos:
            return None
        
        self.m_CurPos = pos
        self.GetParent().OnBarPosChange(pos)

    
    def GetRate(self):
        return (self.m_CurPos / float(self.m_nMax)) * 1000

    
    def LeftDown(self):
        self.Capture(1, 1)
        interface.CHoldObject.LeftDown(self)

    
    def LeftUp(self):
        self.Capture(0)
        interface.CHoldObject.LeftUp(self)

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        self.GetParent().MouseWheelUp(p)



class CImageHFrame(interface.CViewportObject, interface.CBase):
    OFFSET = 10
    
    def __init__(self, oParent, sPath, sPack, w):
        interface.CViewportObject.__init__(self, oParent, 1, 1)
        self.m_iMaxWidth = w
        self.m_iImgHeight = 1
        self.m_sPath = sPath
        self.m_sPack = sPack
        self.m_oLeftImg = None
        self.m_oRightImg = None
        self.m_oMiddleImgList = []
        self.SetImage(sPath, sPack)

    
    def SetImage(self, sPath, sPack):
        self.m_sPath = sPath
        self.m_sPack = sPack
        oRefer = imagewidget.CImage(None, self.m_sPath, self.m_sPack)
        (oImgW, oImgH) = oRefer.GetSize()
        self.m_iImgHeight = oImgH
        self.SetSize(self.m_iMaxWidth, oImgH)
        if oImgW < self.OFFSET:
            LOG_WARN('\xb9\xcf\xa4\xf9\xb2\xa7\xb1`\xa1A\xbce\xab\xd7\xbb\xdd\xadn>=%d\xb9\xb3\xaf\xc0 %d' % (self.OFFSET, oImgW))
        
        self.m_oLeftImg = interface.CViewportObject(self, self.OFFSET, oImgH)
        self.m_oLeftImg.m_oRealImg = imagewidget.CImage(self.m_oLeftImg, self.m_sPath, self.m_sPack)
        self.m_oRightImg = interface.CViewportObject(self, self.OFFSET, oImgH)
        self.m_oRightImg.m_oRealImg = None(None, None(None, None, None, imagewidget.CImage, self.m_oRightImg, **self), self.m_sPack)
        self.m_oRightImg.m_oRealImg.SetPos(self.OFFSET - oImgW, 0)
        self.m_oRightImg.SetPos(self.m_iMaxWidth - self.OFFSET, 0)
        iMidW = oImgW - self.OFFSET * 2
        self.m_oMiddleImgList = []
        if iMidW <= 0:
            return None
        
        iSumMidW = self.m_iMaxWidth - self.OFFSET * 2
        if iSumMidW > iMidW:
            iSum = 0
            iOffset = self.OFFSET
            import misc
            while iSum < iSumMidW:
                if iSum + iMidW > iSumMidW:
                    iRealW = iSumMidW - iSum
                else:
                    iRealW = iMidW
                oImg = interface.CViewportObject(self, iRealW, oImgH)
                oImg.m_oRealImg = imagewidget.CImage(oImg, self.m_sPath, self.m_sPack)
                oImg.m_oRealImg.SetPos(-(self.OFFSET), 0)
                oImg.SetPos(iOffset, 0)
                iOffset += iMidW
                iSum += iMidW
                oImg.SetZ(iSum)
                self.m_oMiddleImgList.append(oImg)
        else:
            oImg = interface.CViewportObject(self, iSumMidW, oImgH)
            oImg.m_oRealImg = imagewidget.CImage(oImg, self.m_sPath, self.m_sPack)
            oImg.m_oRealImg.SetPos(-(self.OFFSET), 0)
            oImg.SetPos(self.OFFSET, 0)
            self.m_oMiddleImgList.append(oImg)

    
    def SetWidth(self, w):
        self.SetSize(w, self.m_iImgHeight)

    
    def SetLight(self, iLight):
        for obj in [
            self.m_oLeftImg,
            self.m_oRightImg] + self.m_oMiddleImgList:
            if hasattr(obj, 'm_oRealImg') and hasattr(obj.m_oRealImg, 'SetLight'):
                obj.m_oRealImg.SetLight(iLight)
                continue
        



def CheckIsImg(sPath):
    if not sPath.endswith('.png'):
        pass
    return sPath.endswith('.igs')
