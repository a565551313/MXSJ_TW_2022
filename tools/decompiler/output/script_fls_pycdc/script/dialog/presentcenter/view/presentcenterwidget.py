# pycdc 交叉复核产物 · script.fls entry 2413
# co_filename(原始)='script/dialog/presentcenter/view/presentcenterwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2413.pyc (Python 2.5)

import clickimage
import combmacro
import interface
import wrapinterface
from presentcenterdefines import *
MASK_DOUBLE = 0
MASK_ASSIGN = 1
MASK2PATH = {
    MASK_DOUBLE: 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xcb\xab\xbc\xbc\xc4\xdc.igs',
    MASK_ASSIGN: 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xd6\xb8\xb6\xa8.igs' }

class CPresentItemBase(object):
    
    def SetQuantityTxt(self, iQuantity, iOffsetX = 0, iOffsetY = 0):
        self.m_QuantityTxt = interface.CTextObject(self, '%s' % iQuantity, interface.FontLT12E_1, [
            16777215,
            6626570], 0)
        (iW, iH) = self.m_QuantityTxt.GetSize()
        self.m_QuantityTxt.SetPos((44 - iW - 2) + iOffsetX, 28 + iOffsetY)
        self.m_QuantityTxt.SetZ(10)

    
    def SetMask(self, iMask):
        self.m_MaskObj = combmacro.CIMAGE(self, MASK2PATH[iMask])
        self.m_MaskObj.SetZ(10)



class CImgWithTips(interface.CNotifyBox, CPresentItemBase):
    
    def __init__(self, parent, shape, lv, x, y):
        import item
        interface.CNotifyBox.__init__(self, parent, 0, 0, 0, 0, 0)
        self.m_Shape = shape
        self.m_Lv = lv
        self.m_Img = item.CreateItem44Image(self, shape)
        (w, h) = self.m_Img.GetSize()
        self.SetSize(w, h)
        self.SetPos(x, y)
        self.SetZ(1)
        self.InitMask(shape, lv)

    
    def InitMask(self, iShape, iLv):
        if iLv in DOUBLESIGN and iShape in DOUBLESIGN[iLv]:
            self.SetMask(MASK_DOUBLE)
        elif iLv in ASSIGNITEM and iShape in ASSIGNITEM[iLv]:
            self.SetMask(MASK_ASSIGN)
        

    
    def GetShape(self):
        return self.m_Shape

    
    def GetLevel(self):
        return self.m_Lv

    
    def Enter(self):
        par = self.GetPar()
        if par:
            par.OnItemEnter(self)
        

    
    def Leave(self):
        par = self.GetPar()
        if par:
            par.OnItemLeave(self)
        

    
    def MouseWheelDown(self, p):
        oParent = self.GetParent()
        if getattr(oParent, 'MouseWheelDown', None):
            oParent.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        oParent = self.GetParent()
        if getattr(oParent, 'MouseWheelUp', None):
            oParent.MouseWheelUp(p)
        



class CItemClickImg(clickimage.CClickImage, CPresentItemBase):
    
    def __init__(self, oParent, sPath, iMsgID, iX, iY, sUIPath):
        clickimage.CClickImage.__init__(self, oParent, sPath, iMsgID, iX, iY, uipath = sUIPath)
        self.m_sTipsText = None
        self.m_Tip = None
        self.m_PreviewImg = None

    
    def SetTipsInfo(self, sText):
        self.m_sTipsText = sText

    
    def CreatePreviewImg(self, iX = None, iY = None):
        import clickimage
        img = clickimage.CClickImage(self, 'combdialog3/\xd4\xd3\xcd\xbc/\xd0\xc2\xb1\xf8\xcd\xbb\xbb\xf7\xb0\xfc/\xd4\xa4\xc0\xc0.igs', 1, 0, 0)
        (iw, ig) = img.GetSize()
        if iX is None:
            img.SetPos(44 - iw, 0)
        else:
            img.SetPos(iX, iY)
        img.SetZ(100)
        self.m_PreviewImg = img

    
    def OnEnter(self, iMsgID):
        if iMsgID == 1:
            self.m_Tip = wrapinterface.CTextTips(interface.TopmostPanel, 150, '\xc2I\xc0\xbb\xa5i\xa5H\xb9w\xc4\xfd\xa5l\xb3\xea\xc3~', interface.FontLT14_3, owner = self, direct = 1)
            self.m_Tip.SetZ(1000)
        

    
    def OnLeave(self, iMsgID):
        if iMsgID == 1:
            self.m_Tip = None
        

    
    def Enter(self):
        if self.m_sTipsText:
            self.m_Tip = None(None, wrapinterface.CTextTips, interface.TopmostPanel(*150).m_sTipsText, interface.FontLT14_3, owner = self, direct = 1)
            self.m_Tip.SetZ(1000)
        

    
    def Leave(self):
        self.m_Tip = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.LeftUp()
