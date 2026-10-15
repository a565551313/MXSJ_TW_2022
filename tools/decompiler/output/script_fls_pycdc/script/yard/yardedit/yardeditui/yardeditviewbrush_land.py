# pycdc 交叉复核产物 · script.fls entry 4196
# co_filename(原始)='script/yard/yardedit/yardeditui/yardeditviewbrush_land.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4196.pyc (Python 2.5)

import yardeditviewbase
import yardbrushshape
import interface
import delegateyardbrushland

class CYardBrushLandView(yardeditviewbase.CEditViewBase, interface.CBoxObject):
    
    def __init__(self, pContext, pEditMgr, pParent):
        yardeditviewbase.CEditViewBase.__init__(self, pContext, pEditMgr)
        interface.CBoxObject.__init__(self, pParent, 1, 1, 0, 0)
        self.m_dExtend = None
        self.m_pCloseCallBack = None
        self.m_pDelegate = delegateyardbrushland.CDelegateYardBrushLand(pContext, pEditMgr, self)
        self.m_pShapeCmp = yardbrushshape.CYardBrushShapeCmp(pContext, pEditMgr)
        self.m_pText = interface.CRichTextObject(self, 1000, interface.FontHT14, '')
        interface.Center(self.m_pText)
        vPos = self.m_pText.GetPos()
        self.m_pText.SetPos(vPos[0], 60)
        self.m_pText.SetZ(10000)

    
    def RefreshNum(self, sTxt):
        self.m_pText.SetText(sTxt)
        interface.Center(self.m_pText)
        vPos = self.m_pText.GetPos()
        self.m_pText.SetPos(vPos[0] + 40, 80)

    
    def IsInZoom(self, x, y):
        return self.m_pDelegate.IsInZoom(x, y)

    
    def CloseBrush(self):
        pContentEdit = self.GetEditViewMgr()
        pContentEdit.ClearBrush()

    
    def SetData(self, nShapeID, iSize = 3):
        self.m_pDelegate.SetData(nShapeID, iSize)

    
    def GetShapeCmp(self):
        return self.m_pShapeCmp

    
    def \xf0eave(self):
        pass

    
    def Enter(self):
        pass

    
    def RightDown(self):
        pass

    
    def RightUp(self):
        pass

    
    def LeftDown(self):
        self.m_pDelegate.LeftDown()

    
    def LeftUp(self):
        self.m_pDelegate.LeftUp()
