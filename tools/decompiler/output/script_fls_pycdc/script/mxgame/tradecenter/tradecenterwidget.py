# pycdc 交叉复核产物 · script.fls entry 4539
# co_filename(原始)='script/mxgame/tradecenter/tradecenterwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4539.pyc (Python 2.5)

import style
import interface
import wrapinterface
import misc

class CDirButton(interface.CContainerObject):
    
    def __init__(self, parent, txt, hasChild, isub = 0, isParentDir = False):
        interface.CContainerObject.__init__(self, parent)
        self.m_HasChild = hasChild
        self.m_Isub = isub
        self.m_IsExpand = False
        self.m_IsParentDir = isParentDir
        self.m_tID = (None, None)
        self.SetExpandIcon()
        self.SetText(txt)

    
    def SetNeedTextShow(self, bShowNeed):
        if bShowNeed:
            oNeedTxt = interface.CTextObject(self, '\xbb\xdd', interface.FontLT12_1, 16711680, 0)
            oNeedTxt.SetPos(84, 5)
            oNeedTxt.SetZ(10)
        else:
            oNeedTxt = None
        self.m_oNeedTxt = oNeedTxt

    
    def SetExpandIcon(self):
        import ui
        if not self.m_IsParentDir:
            return None
        
        if (self.m_IsExpand or self.m_IsParentDir) and not (self.m_HasChild):
            filename = style.GetStr('dlgtjtradecenter.CDirButton', 'data_unexpand')
        else:
            filename = style.GetStr('dlgtjtradecenter.CDirButton', 'data_expand')
        self.m_ExpandIcon = ui.CImage(self, filename, interface.UIPath)
        (x, y) = style.GetIntTuple('dlgtjtradecenter.CDirButton', 'data_expand')
        self.m_ExpandIcon.SetPos(x, y)

    
    def GetTextFontColor(self):
        if self.m_IsParentDir:
            font = interface.FontLT14_18
            color = interface.COLOR_332
        else:
            font = interface.FontLT14_3
            color = interface.COLOR_310
        return (font, color)

    
    def SetText(self, txt):
        self.m_DirName = txt
        (font, color) = self.GetTextFontColor()
        self.m_TxtObj = interface.CTextObject(self, txt, font, color, 0)
        (x, y) = style.GetIntTuple('dlgtjtradecenter.CDirButton', 'pos_txt')
        if not self.m_IsParentDir:
            x += 5
        
        if interface.IsNewStyle():
            x += 3
        
        self.m_TxtObj.SetPos(x, y)

    
    def GetText(self):
        return self.m_DirName

    
    def SetID(self, iParentID, iChildID = None):
        self.m_tID = (iParentID, iChildID)

    
    def GetID(self):
        return self.m_tID

    
    def LeftUp(self):
        self.GetParent().LeftUp(self)

    
    def BtnSelect(self, bSelect):
        pass



class CNewDirButton(CDirButton):
    
    def GetTextFontColor(self):
        if self.m_IsParentDir:
            font = interface.FontLT14_18
        else:
            font = interface.FontLT14_3
        color = interface.COLOR_332
        return (font, color)

    
    def BtnSelect(self, bSelect):
        if bSelect:
            self.m_TxtObj.SetColor(interface.COLOR_326)
        else:
            self.m_TxtObj.SetColor(interface.COLOR_332)



class CDirListObject(interface.CBaseObject):
    
    def __init__(self, oParent, oList):
        interface.CBaseObject.__init__(self, oParent)
        self.m_oListWR = misc.WeakRef(oList)
        self.m_dData = { }
        self.m_SelectedID = (None, None)
        self.m_bIsSmartMode = False
        self.m_oExpandCB = None

    
    def SetExpandCB(self, \xeb\xc7\xc6):
        self.m_oExpandCB = \xeb\xc7\xc6

    
    def SetSmartMode(self, bSmartMode):
        self.m_bIsSmartMode = bSmartMode

    
    def SetData(self, dDir):
        '''
\t\t:param list dDir: {"ID":id, "sName":name, "lChild": []}
\t\t:return:
\t\t'''
        self.m_dData = dDir
        self.RefreshDir((None, None))

    
    def SetSelect(self, iIdx):
        tNewSelectedID = self.GetIDByIndex(iIdx)
        self.RefreshDir(tNewSelectedID)

    
    def SetSelectByID(self, tID):
        self.RefreshDir(tID)

    
    def GetSelectedID(self):
        return self.m_SelectedID

    
    def GetIDByIndex(self, iIdx):
        oBox = self.m_oListWR().GetItemByIndex(iIdx)
        return oBox.m_RealObj.GetID()

    
    def GetIDByName(self, tName):
        for iParentID, sName, childList in self.m_dData:
            if tName[0] != sName:
                continue
            
            tRet = [
                iParentID,
                None]
            for iChildID, sChildName in childList:
                if sChildName == tName[1]:
                    tRet[1] = iChildID
                    break
                    continue
            
            return tuple(tRet)
        

    
    def GetItemByIndex(self, iIndex):
        return self.m_oListWR().m_Items[iIndex]

    
    def GetItemByID(self, tID):
        for oItem in self.m_oListWR().m_Items:
            if oItem.m_RealObj.GetID() == tID:
                return oItem
                continue
        

    
    def GetItems(self):
        return self.m_oListWR().m_Items

    
    def RefreshDir(self, tNewSelectedID):
        if tNewSelectedID == (None, None):
            (iSelectParentID, iSelectChildID) = self.m_SelectedID
        else:
            (iOldSelectParentID, iOldSelectChildID) = self.m_SelectedID
            (iSelectParentID, iSelectChildID) = tNewSelectedID
            if iSelectParentID == iOldSelectParentID and iSelectChildID == None:
                for iParentID, sName, tChildList in self.m_dData:
                    if iParentID == iSelectParentID:
                        if tChildList:
                            (iSelectParentID, iSelectChildID) = (None, None)
                        
                        break
                        continue
                
            
        iBefExpand = self.GetExpandIdx()
        oDirList = self.m_oListWR()
        iPos = oDirList.m_VScrollBar.GetPos()
        oDirList.Clear()
        if interface.IsNewStyle():
            oCls = CNewDirButton
        else:
            oCls = CDirButton
        for iParentID, sName, childList in enumerate(self.m_dData):
            box = oDirList.AddBoxItem()
            bIsSeletedDir = iParentID == iSelectParentID
            if childList and not bIsSeletedDir:
                box.m_RealObj = oCls(box, sName, True, 0, True)
            else:
                box.m_RealObj = oCls(box, sName, False, 0, True)
            if bIsSeletedDir and not childList:
                box.Select(True)
                box.m_RealObj.BtnSelect(True)
            
            box.m_ID = iParentID
            box.m_bIsChild = False
            box.m_RealObj.SetID(iParentID, None)
            if not bIsSeletedDir:
                continue
            
            for iChildID, sChildName in enumerate(childList):
                box = oDirList.AddBoxItem()
                box.m_RealObj = oCls(box, sChildName, False, 0, False)
                box.m_ID = iChildID
                box.m_bIsChild = True
                box.m_RealObj.SetID(iParentID, iChildID)
                if iChildID == iSelectChildID:
                    box.Select(True)
                    box.m_RealObj.BtnSelect(True)
                    continue
                if iSelectChildID is None and idx == 0:
                    iSelectChildID = iChildID
                    box.Select(True)
                    box.m_RealObj.BtnSelect(True)
                    continue
            
        
        oDirList.ResetItems()
        oDirList.ResetScrollBar()
        if self.GetExpandIdx() != iBefExpand:
            iPos = self.GetSmartPos(iPos)
        
        oDirList.m_VScrollBar.SetBarPos(iPos)
        if interface.IsNewStyle():
            oDirList.ShowLineForItems()
        
        self.m_SelectedID = (iSelectParentID, iSelectChildID)
        if self.m_oExpandCB:
            self.m_oExpandCB()
        

    
    def GetSmartPos(self, iOriPos):
        if not self.m_bIsSmartMode:
            return iOriPos
        
        iState = 0
        iPreParentCnt = 0
        iAftParentCnt = 0
        iChildCnt = 0
        for oItem in self.m_oListWR().GetItems():
            if oItem.m_bIsChild:
                if iState == 0:
                    iState = 1
                
            elif iState == 1:
                iState = 2
            
            if iState == 0:
                iPreParentCnt += 1
                continue
            if iState == 1:
                iChildCnt += 1
                continue
            if iState == 2:
                iAftParentCnt += 1
                continue
        
        iCanseeCnt = self.m_oListWR().GetRowNum()
        if iPreParentCnt + iChildCnt - iOriPos <= iCanseeCnt:
            return iOriPos
        
        if 1 + iChildCnt > iCanseeCnt:
            return iPreParentCnt - 1
        
        if iAftParentCnt:
            return iPreParentCnt + iChildCnt + 1 - iCanseeCnt
        
        return iPreParentCnt + iChildCnt - iCanseeCnt

    
    def GetExpandIdx(self):
        for idx, oItem in enumerate(self.m_oListWR().GetItems()):
            if oItem.m_bIsChild:
                return idx
                continue
        
        return -1



class CAmountEdit(wrapinterface.CNumberEdit):
    
    def SetMaxNum(self, num):
        self.m_MaxNum = num

    
    def AddChar(self, char):
        wrapinterface.CNumberEdit.AddChar(self, char)
        if not hasattr(self, 'm_Ignore') and self.m_Ignore:
            self._OnChange()
        

    
    def DeleteChar(self):
        wrapinterface.CNumberEdit.DeleteChar(self)
        self._OnChange()

    
    def _OnChange(self):
        amount = self.GetAmount()
        if hasattr(self, 'm_MaxNum') and amount > self.m_MaxNum:
            self.m_Ignore = True
            self.SetText(str(self.m_MaxNum))
            self.m_Ignore = False
        
        if self.GetParent() and hasattr(self.GetParent(), 'OnEditChange'):
            self.GetParent().OnEditChange(self)
        

    
    def GetAmount(self):
        
        try:
            amount = int(self.GetText())
        except ValueError:
            amount = 0

        return amount
