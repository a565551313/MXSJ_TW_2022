# pycdc 交叉复核产物 · script.fls entry 524
# co_filename(原始)='script/mxgame/assembly/view/base/dlgbaseassembly.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_524.pyc (Python 2.5)

import interface
import style
import combmacro

class CCustomAssemblyItem(interface.CClickBox):
    
    def __init__(self, oParent, iShape, msgid, bShowLock = True):
        interface.CClickBox.__init__(self, oParent, 44, 44, 16711680, 0, msgid)
        self.m_oItem = None
        self.m_dItemData = None
        self.m_dItemStateData = None
        self.m_Tips = None
        self.m_IsSelected = False
        self.m_iShape = -1
        sPath = style.GetStr('dlgxingzuo.CXingZuoItem', 'data_select')
        self.m_SelBox = combmacro.CIMAGE(self, sPath)
        self.m_bShowLock = bShowLock
        self.m_oLockImg = None
        if self.m_bShowLock:
            self.SetUnLock(False)
        
        self.m_SelBox.SetPos(-2, -2)
        self.m_SelBox.SetShow(False)
        self.SetShape(iShape)

    
    def SetUnLock(self, ilock):
        if not ilock:
            sFilename = style.GetStr('dlgxingzuo.CXingZuoItem', 'data_xingzuo')
            (iOffx, iOffy) = (0, 0)
        else:
            sFilename = style.GetStr('dlgxingzuo.CXingZuoItem', 'data_duihao')
            (iOffx, iOffy) = (8, 8)
        self.m_iLock = ilock
        import combmacro
        oImg = self.m_oLockImg = combmacro.CIMAGE(self, sFilename)
        (iW, iH) = self.GetSize()
        (iImgW, iImgH) = oImg.GetSize()
        iX = iW - iImgW
        iY = iH - iImgH
        oImg.SetPos(iX + iOffx, iY + iOffy)
        oImg.SetZ(20)

    
    def SetSelect(self, sel):
        self.m_SelBox.SetShow(sel)
        self.m_IsSelected = sel

    
    def SetItemData(self, dItem):
        self.m_dItemData = dItem
        iShape = 0
        if self.m_dItemData:
            pass
        iShape = self.m_dItemData.get('shape', 0)
        self.SetShape(iShape)

    
    def GetItemData(self):
        return self.m_dItemData

    
    def SetItemStateData(self, dStateData):
        self.m_dItemStateData = dStateData

    
    def GetItemState(self):
        return self.m_dItemStateData

    
    def UpdateItemState(self):
        if not self.m_dItemStateData:
            self.SetUnLock(False)
        else:
            self.SetUnLock(True)

    
    def ResetItemState(self):
        self.m_dItemStateData = None
        if self.m_iShape and self.m_bShowLock:
            self.SetUnLock(False)
        else:
            None(None, None, None, None, *self).SetShow(False)

    
    def SetShape(self, iShape):
        self.m_iShape = iShape
        if iShape:
            import item
            self.m_oItem = item.CreateItem44Image(self, iShape)
        elif self.m_oItem:
            self.m_oItem = None
        
        if self.m_oLockImg:
            if iShape:
                pass
            self.m_oLockImg.SetShow(self.m_bShowLock)
        

    
    def GetShape(self):
        return self.m_iShape

    
    def Enter(self):
        if not self.m_iShape:
            return None
        
        self.m_SelBox.SetShow(True)
        import itemdata
        import wrapinterface
        (sName, sExplain) = itemdata.GetData(self.m_iShape)
        self.m_Tips = wrapinterface.CItemTips(self.m_iShape, '', sName, sExplain, '', charcount = 32)

    
    def Leave(self):
        if not self.m_IsSelected:
            self.m_SelBox.SetShow(False)
        
        self.m_Tips = None
