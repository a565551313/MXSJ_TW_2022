# pycdc 交叉复核产物 · script.fls entry 4377
# co_filename(原始)='script/yard/yardedit/yardeditdelegate/delegateyardbrushhouse.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4377.pyc (Python 2.5)

'''
import CDelegateYardBrushHouse.py
'''
import misc
import yardeditviewbase
import yardeditblockview
import yardblockdata
import timer
import cursor
import yarddefines
import key
E_VOFF = (0, 20)

class CDelegateYardBrushHouse(yardeditviewbase.CEditViewBase):
    
    def __init__(self, pContext, pEditViewMgr, pBrush):
        yardeditviewbase.CEditViewBase.__init__(self, pContext, pEditViewMgr)
        self.m_wrBrush = misc.WeakRef(pBrush)
        self.m_pBlockView = None
        self.m_pTimer = None
        self.m_vMapCell = None
        self.m_vMapPos = None
        self.m_lPlaceBlock = None
        self.m_lBlock = None
        self.m_nShapeID = None
        self.m_nDirect = 0
        self.m_vOffPos = None

    
    def CloseBrush(self):
        pView = self.GetBrush()
        pView.CloseBrush()

    
    def GetBrush(self):
        return self.m_wrBrush()

    
    def IsInZoom(self, x, y):
        return True

    
    def GetOffPos(self):
        if not self.m_vOffPos:
            pContext = self.GetContext()
            pDataMgr = pContext.GetYardDataMgr()
            vHoursePos = pDataMgr.GetHouseInfoValueByKey('vpos')
            vOffGrid = pDataMgr.GetAttrByKey('vPos')
            pGridConvertLogic = self.GetGridConvertLogic()
            vWordPos = pGridConvertLogic.ServerMapPos2WorldPos(vHoursePos)
            vScreenPos = pGridConvertLogic.CalWindowPosByWorldPos(vOffGrid, vWordPos)
            vCursorPos = cursor.GetCursorPos()
            self.m_vOffPos = ((vScreenPos[0] - vCursorPos[0]) + E_VOFF[0], (vScreenPos[1] - vCursorPos[1]) + E_VOFF[1])
        
        return self.m_vOffPos

    
    def RefreshBlock(self, nShapeID, nDirect = 0):
        self.m_nShapeID = nShapeID
        if not self.m_pBlockView:
            self.m_pBlockView = yardeditblockview.CYardMapItemBlock(self.GetBrush())
            self.m_pBlockView.SetZ(100)
        
        self.m_nDirect = nDirect
        sPath = yardblockdata.GetFurnitureBlockKeyByID(nShapeID, nDirect)
        lBlock = yardblockdata.GetResBlockData(sPath)
        self.m_lBlock = list(lBlock)
        self.m_pBlockView.SetData(lBlock)

    
    def StartMoveWithCurser(self):
        if not self.m_pTimer:
            self.m_pTimer = timer.Timer(0.03, self._MoveWithCurser, -1, oRelayObj = self)
            self.m_vMapCell = None
            self._MoveWithCurser()
        

    
    def _MoveWithCurser(self):
        (x, y) = cursor.GetCursorPos()
        vOffPos = self.GetOffPos()
        x = x + vOffPos[0]
        y = y + vOffPos[1]
        pContext = self.GetContext()
        pDataMgr = pContext.GetYardDataMgr()
        vOffGrid = pDataMgr.GetAttrByKey('vPos')
        pGridConvertLogic = self.GetGridConvertLogic()
        vWorldPos = pGridConvertLogic.CalMapPosByWindowPos(vOffGrid, (x, y))
        vWorldPos = (int(vWorldPos[0]), int(vWorldPos[1]))
        vMapCell = pGridConvertLogic.WorldPos2ServerMapPos(vWorldPos)
        vRealPos = pGridConvertLogic.ServerMapPos2WorldPos(vMapCell)
        if self.m_vMapCell == vMapCell:
            return None
        
        self.m_vMapCell = vMapCell
        self.RefreshPos(vRealPos)

    
    def RefreshPos(self, vRealPos):
        self.m_vMapPos = vRealPos
        pView = self.GetBrush()
        pDataMgr = self.GetContext().GetYardDataMgr()
        pGridConvertLogic = self.GetGridConvertLogic()
        vOffGrid = pDataMgr.GetAttrByKey('vPos')
        vOffPos = pGridConvertLogic.Server2ClientPos(vOffGrid)
        vPos = (int(vRealPos[0] + vOffPos[0]), int(vRealPos[1] + vOffPos[1]))
        pView.SetPos(*vPos)
        if not self.m_lBlock:
            return None
        
        pBlockLogic = self.GetBlockLogic()
        self.m_lPlaceBlock = pBlockLogic.CalBlock(self.m_lBlock, self.m_vMapCell, yarddefines.E_UNIT_HOUSE)
        for vBlock in self.m_lBlock:
            bRed = vBlock in self.m_lPlaceBlock
            self.m_pBlockView.SetBlockRed(vBlock, bRed)
        

    
    def LeftDown(self):
        if not self.m_pTimer:
            return None
        else:
            self.Check2Brush()

    
    def LeftUp(self):
        if not self.m_pTimer:
            self.StartMoveWithCurser()
        
        self.m_vMapCell = None

    
    def Check2Brush(self, *argv):
        if not self.m_vMapCell:
            return None
        
        import usermacro
        if self.m_lPlaceBlock:
            sMsg = yarddefines.E_TIPS.get('furncannotplacetpshouse', '\xa4\xa3\xaf\xe0\xc2\\\xa9\xf1\xb3\xc3\xa8\xe3')
            usermacro.PROMPT_MSG(sMsg)
            return None
        
        pBrush = self.GetBrush()
        pBrushLogic = (None, None, None, None, None, None, None, None, self.GetContext())()
        pBrushLogic.BrushHouse({
            'vpos': self.m_vMapCell })
        pBrush.CloseBrush()
