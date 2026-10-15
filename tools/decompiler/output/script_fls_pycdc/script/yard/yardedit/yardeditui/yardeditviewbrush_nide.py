# pycdc 交叉复核产物 · script.fls entry 2850
# co_filename(原始)='script/yard/yardedit/yardeditui/yardeditviewbrush_nide.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2850.pyc (Python 2.5)

import yardeditviewbase
import interface
import delegateyardbrushnide
import yardeditviewbrush_furniture
import yarditemnide
import yardothers

class CYardBrushNideView(yardeditviewbase.CEditViewBase, interface.CBoxObject):
    
    def __init__(self, oContext, oEditMgr, oParent):
        yardeditviewbase.CEditViewBase.__init__(self, oContext, oEditMgr)
        interface.CBoxObject.__init__(self, oParent, 1, 1, 0, 0)
        self.m_oShape = None
        self.m_oCloseCallBack = None
        self.m_dExtend = None
        self.m_nAnimalID = None
        self.m_nAnimalID = None
        self.m_oMoveGuide = yardeditviewbrush_furniture.CYardMoveGuideDialog()
        self.m_oDelegate = delegateyardbrushnide.CDelegateYardBrushNide(oContext, oEditMgr, self)

    
    def IsInZoom(self, x, y):
        if self.m_oDelegate:
            return self.m_oDelegate.IsInZoom(x, y)
        
        return False

    
    def CloseBrush(self):
        oContentEdit = self.GetEditViewMgr()
        oContentEdit.ClearBrush()

    
    def GetShapeID(self):
        return self.m_nAnimalID

    
    def Clear(self):
        oYardDataMgr = self.GetContext().GetYardDataMgr()
        oYardDataMgr.SetAttrByKeyValue_Edit('nSelectShape', 0)

    
    def SetData(self, nAnimalID, dExtend):
        self.m_dExtend = dExtend
        self.m_nAnimalID = nAnimalID
        oYardDataMgr = self.GetContext().GetYardDataMgr()
        for dAniData in oYardDataMgr.GetAnimalByIdx:
            if not dAniData:
                LOG('\xa4\xa3\xa6s\xa6b\xaa\xbaani', nAnimalID)
                return None
            
            shapeID = yardothers.GetAniNideShapeID(dAniData['iType'])
            oNide = yarditemnide.CNideObj(self, 0, 0, nAnimalID, shapeID, 0)
            oNide.SetPos(0, 0)
            oNide.SetZ(1)
            self.m_nAnimalID = nAnimalID
            self.SetShape(oNide)
            oYardDataMgr.SetAttrByKeyValue_Edit('nSelectShape', self.m_nAnimalID)
            self.m_oDelegate.RefreshBlock(nAnimalID, shapeID)
            self.m_oDelegate.StartMoveWithCurser()
            return None

    
    def SetShape(self, oShape):
        self.m_oShape = oShape

    
    def GetShape(self):
        return self.m_oShape

    
    def Leave(self):
        pass

    
    def Enter(self):
        pass

    
    def RightDown(self):
        pass

    
    def RightUp(self):
        pass

    
    def LeftDown(self):
        self.m_oDelegate.LeftDown()

    
    def LeftUp(self):
        self.m_oDelegate.LeftUp()
