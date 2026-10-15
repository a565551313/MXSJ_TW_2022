# pycdc 交叉复核产物 · script.fls entry 1659
# co_filename(原始)='script/reddotsys/dlgreddot.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1659.pyc (Python 2.5)

import misc
import ui
import interface
import mdreddot
import weakref
RED_POINT_Z = 100

class CRedDotWidget(object):
    
    def __init__(self, oParent, oNode):
        '''
\t\t:param oNode:
\t\t:type oNode: mdreddot.CNode
\t\t:param oParent:
\t\t'''
        self.m_iStatus = oNode.GetTotalVal()
        self.m_oParent = weakref.ref(oParent)
        oNode.ssConnect(oNode.SS_NotifyView, self.Update)

    
    def RenderImg(self):
        '''\xaa\xed\xb2{\xb9\xea\xb2{'''
        raise NotImplementedError

    
    def Update(self, iStatus):
        self.m_iStatus = iStatus
        if not self.RenderImg:
            pass
        self.RenderImg



class CSimpleRedDotWidget(CRedDotWidget):
    SMALL_RED_DOT = 1
    MIDDLE_RED_DOT = 2
    BIG_RED_DOT = 3
    NUM_RED_DOT = 4
    
    def __init__(self, oParent, oNode, iOffsetX = 0, iOffsetY = 0, bNoDigit = True):
        CRedDotWidget.__init__(self, oParent, oNode)
        self.m_iOffsetX = iOffsetX
        self.m_iOffsetY = iOffsetY
        self.m_bNoDigit = bNoDigit
        self.m_iRedDotType = 1
        self.RenderImg()

    
    def RenderImg(self):
        iOffsetX = self.m_iOffsetX
        iOffsetY = self.m_iOffsetY
        if not (self.m_iStatus) or self.m_iStatus <= 0:
            self.m_Img = None
            return None
        
        self.m_Img = self.CreateImage()
        interface.TopRight(self.m_Img, offsetx = iOffsetX, offsety = iOffsetY)
        self.m_Img.SetZ(RED_POINT_Z)

    
    def CreateImage(self):
        if self.m_iRedDotType == self.MIDDLE_RED_DOT:
            sPath = 'number/\xd6\xd0\xba\xec\xb5\xe3.igs'
            sDir = 'misc'
        elif self.m_iRedDotType == self.BIG_RED_DOT:
            sPath = 'number/0.igs'
            sDir = 'misc'
        elif self.m_iRedDotType == self.SMALL_RED_DOT:
            sDir = 'misc'
            if self.m_iStatus > 10 or self.m_bNoDigit:
                sPath = 'number/0.igs'
            else:
                sPath = 'number/%d.igs' % self.m_iStatus
        else:
            sPath = 'combdialog/\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe\xd0\xa1\xba\xec\xb5\xe3.igs'
            sDir = 'interface'
        return ui.CImage(self.m_oParent(), sPath, sDir)



class CUIRedDotWidget(CRedDotWidget):
    
    def __init__(self, oParent, oNode, oRedDotUI):
        CRedDotWidget.__init__(self, oParent, oNode)
        self.m_oRedDotUI = None if oRedDotUI else None
        self.RenderImg()

    
    def RenderImg(self):
        if self.m_iStatus:
            pass
        bShow = self.m_iStatus > 0
        oRedDot = self.GetRedDot()
        if oRedDot:
            oRedDot.SetShow(bShow)
        

    
    def GetRedDot(self):
        if self.m_oRedDotUI:
            return self.m_oRedDotUI()
