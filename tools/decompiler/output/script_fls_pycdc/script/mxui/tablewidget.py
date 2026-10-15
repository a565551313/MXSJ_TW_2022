# pycdc 交叉复核产物 · script.fls entry 4507
# co_filename(原始)='script/mxui/tablewidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4507.pyc (Python 2.5)

import interface
import framewidget
import scrollwidget
import boxwidget
import tabledata
import fontdata
import ui
import sound

class CTable(interface.CBaseObject, interface.CBase):
    
    def __init__(self, oParent, sTitles, iRow, w, h, iMsgID, iWidthList, sType = None):
        interface.CBaseObject.__init__(self, oParent)
        self.MessageProcess()
        self.m_Row = iRow
        self.m_Size = (w, h)
        self.m_Titles = sTitles
        self.m_MsgID = iMsgID
        self.m_Widths = iWidthList
        self.m_KeepShowDict = { }
        self.m_Head = 0
        self.m_Items = []
        self.m_bCreateVerticalLine = True
        self.InitStyle(sType)

    
    def Create(cls, oParent, sDataList, dUIInfo = None):
        if dUIInfo is None:
            sTitles = sDataList.pop()
            sTitles = sTitles.replace('\\n', '\n')
            sTitleList = sTitles.split()
            iRow = int(sDataList.pop())
            w = int(sDataList.pop())
            h = int(sDataList.pop())
            iMsgID = int(sDataList.pop())
            iWidthList = []
            for _ in range(len(sDataList)):
                iWidthList.append(int(sDataList.pop()))
            
        else:
            sTitles = dUIInfo['sTitles']
            sTitles = sTitles.replace('\\n', '\n')
            sTitleList = sTitles.split()
            iRow = dUIInfo['iRow']
            w = dUIInfo['iWidth']
            h = dUIInfo['iHeight']
            iMsgID = dUIInfo['iMsgId']
            iWidthList = list(dUIInfo['lSubWidth'])
        return CTable(oParent, sTitleList, iRow, w, h, iMsgID, iWidthList)

    Create = classmethod(Create)
    
    def InitStyle(self, sType):
        if sType is None:
            sType = tabledata.DEFAULT_TYPE
        
        self.m_TableInfo = tabledata.GetTableInfo(sType)
        self.m_TableInfo = tabledata.GetTableInfo(sType)
        self.m_NormalTxtColor = self.m_TableInfo['iNormalColor']
        self.m_SelectTxtColor = self.m_TableInfo['iSelectColor']
        self.m_EnterTxtColor = self.m_TableInfo['iEnterColor']
        self.m_TitleObjects = []
        self.m_TitleFrames = []
        self.m_Objects = []
        (iItWidth, iTitleHeight) = self.CreateTitle(self.m_Titles)
        iSpace = self.m_TableInfo['iSpace']
        self.m_ItemStartY = iTitleHeight + iSpace
        iItSumHeight = self.m_Size[1] - self.m_ItemStartY
        self.m_ItemWidth = iItWidth
        self.m_ItemHeight = iItSumHeight / self.m_Row
        self.CraeteItemLine(iItWidth, iItSumHeight)
        self.CreateScrollBar()
        self.ResetItems()
        self.ResetScrollBar()

    
    def GetItemSize(self):
        return (self.m_ItemWidth, self.m_ItemHeight)

    
    def GetItems(self):
        return self.m_Items

    
    def GetItem(self, iIdx):
        if iIdx <= iIdx:
            pass
        elif iIdx < len(self.m_Items):
            return self.m_Items[iIdx]
        else:
            return None

    
    def GetItemIdx(self, oItem):
        if oItem not in self.m_Items:
            return -1
        
        return self.m_Items.index(oItem)

    
    def ScrollToItem(self, oItem, bTop = True):
        iIdx = self.GetItemIdx(oItem)
        if iIdx == -1:
            return None
        
        iSumLen = len(self.m_Items)
        iShowLen = self.m_Row
        if iSumLen <= iShowLen:
            return None
        
        if bTop:
            iMaxPos = iSumLen - iShowLen
            iPos = min(iMaxPos, iIdx)
        else:
            iMinPos = (iIdx - iShowLen) + 1
            iPos = max(0, iMinPos)
        if iPos >= 0 and self.m_VScrollBar:
            self.m_VScrollBar.SetBarPos(iPos)
        

    
    def InsertItem(self, oItem, idx):
        self.m_Items.insert(idx, oItem)

    
    def GetSelectItem(self):
        for oItem in self.m_Items:
            if oItem.IsSelected():
                return oItem
                continue
        

    
    def SetTitle(self, iIdx, sTitle, color = None, font = None):
        import fontdata
        if color is None:
            color = self.m_TableInfo['iTitleColor']
        
        if font is None:
            sFontType = self.m_TableInfo['sTitleFontType']
            font = fontdata.GetFont(sFontType)
        
        iSize = len(self.m_Widths)
        if iIdx <= iIdx:
            pass
        elif iIdx < iSize:
            bTFStrength = self.m_TableInfo['bTFStrength']
            if bTFStrength:
                oTitle = interface.COverstrikingTextObject(self, sTitle, font, color, 0)
            else:
                oTitle = interface.CTextObject(self, sTitle, font, color, 0)
            self.m_TitleObjects[iIdx] = oTitle
            self.m_TitleObjects[iIdx].SetZ(1)
            (iTxtW, iTxtH) = oTitle.GetSize()
            iTitleH = self.m_TitleFrames[0].GetSize()[1]
            iTitleW = self.m_Widths[iIdx]
            (x, y) = interface.GetAlignXY(iTxtW, iTxtH, iTitleW, iTitleH, interface.ALIGN_CENTER_MIDDLE)
            iStartX = sum(self.m_Widths[:iIdx])
            oTitle.SetPos(iStartX + x, y)
            oTitle.SetZ(1)
        

    
    def BarChange(self, pos):
        self.ResetItems(pos)

    
    def GetSize(self):
        return self.m_Size

    
    def Clear(self):
        self.m_Head = 0
        for it in self.m_Items:
            it.m_CombBoxs = None
        
        self.m_Items = []
        self.m_KeepShowDict = { }
        self.m_VScrollBar.Set(0, self.m_Row)
        self.m_VScrollBar.SetBarPos(0)

    
    def AddBoxItem(self, iInserIdx = None):
        sItNormalPath = self.m_TableInfo['sItNormalPath']
        sItEnterPath = self.m_TableInfo['sItEnterPath']
        sItSelectPath = self.m_TableInfo['sItSelectPath']
        return CCombCheckBox(self, self.m_Items, self.m_ItemWidth, self.m_ItemHeight, sItNormalPath, sItEnterPath, sItSelectPath, msgid = len(self.m_Items) + 1, iInserIdx = iInserIdx)

    
    def AddItem(self, oItem):
        if not hasattr(oItem, 'GetSize'):
            return None
        
        self.m_Items.append(oItem)

    
    def AddItemExtend(self, oItem, oItemList, dAlignInfo = None, bChangeColor = True):
        if dAlignInfo is None:
            dAlignInfo = { }
            dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
            dAlignInfo['tOffset'] = (0, 0)
        
        iAlign = dAlignInfo.get('iAlign', interface.ALIGN_CENTER_MIDDLE)
        tOffset = dAlignInfo.get('tOffset', (0, 0))
        if bChangeColor:
            sAttrName = 'm_TextObjects'
        else:
            sAttrName = 'm_SubObjects'
        setattr(oItem, sAttrName, [])
        oTmpList = getattr(oItem, sAttrName)
        for i, oSubItem in enumerate(oItemList):
            self.AlignItem(oSubItem, i, iAlign, tOffset)
            oTmpList.append(oSubItem)
        
        return oItem

    
    def AddTextItem(self, sTxtList, color = None, hot = None, font = None, iEnterColor = None, iSelectColor = None, dAlignInfo = None, iInsertIdx = None, oCreateDelegate = None):
        import fontdata
        if font is None:
            sFontType = self.m_TableInfo['sFontType']
            font = fontdata.GetFont(sFontType)
        
        oItem = self.AddBoxItem(iInsertIdx)
        
        try:
            self.SetItemText(oItem, sTxtList, color, font, iEnterColor, iSelectColor, dAlignInfo, oCreateDelegate)
        except:
            self.SetItemText(oItem, sTxtList, color, font, iEnterColor, iSelectColor, dAlignInfo)

        if hot is not None:
            if hot == -1:
                oHotArea = CHotArea(oItem, self.m_ItemWidth, self.m_ItemHeight, alpha = 0)
            else:
                oHotArea = CHotArea(oItem, self.m_Widths[hot], self.m_ItemHeight, alpha = 0)
                iOffsetX = sum(self.m_Widths[:hot])
                oHotArea.SetPos(iOffsetX, 0)
            oItem._HotArea = oHotArea
        
        return oItem

    
    def SetItemText(self, oItem, sTxtList, color = None, font = None, iEnterColor = None, iSelectColor = None, dAlignInfo = None, oCreateDelegate = None):
        import fontdata
        if iEnterColor is None:
            if color is None:
                iEnterColor = self.m_EnterTxtColor
            else:
                iEnterColor = color
        
        if iSelectColor is None:
            if color is None:
                iSelectColor = self.m_SelectTxtColor
            else:
                iSelectColor = color
        
        if color is None:
            color = self.m_NormalTxtColor
        
        if font is None:
            sFontType = self.m_TableInfo['sFontType']
            font = fontdata.GetFont(sFontType)
        
        if dAlignInfo is None:
            dAlignInfo = { }
            dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
            dAlignInfo['tOffset'] = (0, 0)
        
        iAlign = dAlignInfo.get('iAlign', interface.ALIGN_CENTER_MIDDLE)
        tOffset = dAlignInfo.get('tOffset', (0, 0))
        oItem.UpdateTxtColor(iNormalColor = color, iSelectColor = iSelectColor, iEnterColor = iEnterColor)
        oItem.m_TextObjects = []
        sTxtList = None if type(sTxtList) != str else sTxtList.split()
        for i, sTxt in enumerate(sTxtList):
            oTxtObj = None
            if oCreateDelegate:
                iWidth = self.m_Widths[i]
                oTxtObj = oCreateDelegate(oItem, sTxt, font, color, i, iWidth)
            
            if not oTxtObj:
                oTxtObj = interface.CTextObject(oItem, sTxt, font, color, 0)
            
            oTxtObj.m_Txt = sTxt
            self.AlignItem(oTxtObj, i, iAlign, tOffset)
            oItem.m_TextObjects.append(oTxtObj)
        

    
    def AddMulLineItem(self, sTxtList, color = None, font = None, iEnterColor = None, iSelectColor = None, dAlignInfo = None):
        import fontdata
        if color == None:
            color = self.m_NormalTxtColor
        
        if font is None:
            sFontType = self.m_TableInfo['sFontType']
            font = fontdata.GetFont(sFontType)
        
        oItem = self.AddBoxItem()
        self.SetItemMulLine(oItem, sTxtList, color, font, iEnterColor, iSelectColor, dAlignInfo)
        return oItem

    
    def AddRichTextItem(self, sTxtList, color = None, font = None, iEnterColor = None, iSelectColor = None, dAlignInfo = None):
        return self.AddMulLineItem(sTxtList, color, font, iEnterColor, iSelectColor, dAlignInfo)

    
    def SetItemMulLine(self, oItem, sTxtList, color = None, font = None, iEnterColor = None, iSelectColor = None, dAlignInfo = None):
        import fontdata
        if iEnterColor is None:
            if color is None:
                iEnterColor = self.m_EnterTxtColor
            else:
                iEnterColor = color
        
        if iSelectColor is None:
            if color is None:
                iSelectColor = self.m_SelectTxtColor
            else:
                iSelectColor = color
        
        if color is None:
            color = self.m_NormalTxtColor
        
        if font is None:
            sFontType = self.m_TableInfo['sFontType']
            font = fontdata.GetFont(sFontType)
        
        if dAlignInfo is None:
            dAlignInfo = { }
            dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
            dAlignInfo['tOffset'] = (0, 0)
        
        iAlign = dAlignInfo.get('iAlign', interface.ALIGN_CENTER_MIDDLE)
        tOffset = dAlignInfo.get('tOffset', (0, 0))
        oItem.UpdateTxtColor(iNormalColor = color, iSelectColor = iSelectColor, iEnterColor = iEnterColor)
        oItem.m_TextObjects = []
        iOffsetX = 0
        for i, sTxt in enumerate(sTxtList):
            oTxtObj = interface.CRichTextObject(oItem, self.m_Widths[i], font, sTxt, color)
            self.AlignItem(oTxtObj, i, iAlign, tOffset)
            iOffsetX += self.m_Widths[i]
            oItem.m_TextObjects.append(oTxtObj)
        

    
    def KeepItemShow(self, iIndex, bShow):
        self.m_KeepShowDict[iIndex] = bShow

    
    def ResetItems(self, head = -1):
        if len(self.m_Items) == 0:
            return None
        
        if head < 0:
            head = self.m_Head
        
        if head >= len(self.m_Items):
            head = len(self.m_Items) - 1
        
        self.m_Head = head
        for iIdx, oItem in enumerate(self.m_Items):
            if not self.m_KeepShowDict.get(iIdx, False):
                oItem.SetShow(False)
                continue
        
        for i in xrange(head, head + self.m_Row):
            if i < len(self.m_Items):
                self.m_Items[i].SetPos(0, self.m_ItemStartY + (i - head) * self.m_ItemHeight)
                self.m_Items[i].SetShow(True)
                continue
        

    
    def ResetScrollBar(self, \x8b\x91\x8fust = False):
        import combdialog
        if combdialog.IsUseNewTable():
            if not self.m_TableInfo['bIgs']:
                \x8b\x91\x8fust = True
            
        
        if not \x8b\x91\x8fust:
            if len(self.m_Items) <= self.m_Row:
                self.m_VScrollBar.SetShow(False)
            else:
                self.m_VScrollBar.SetShow(True)
        else:
            self.m_VScrollBar.SetShow(True)
        self.m_VScrollBar.Set(len(self.m_Items), self.m_Row)

    
    def ResetScrollBarToHead(self, \x8b\x91\x8fust = False):
        self.ResetScrollBar(\x8b\x91\x8fust = \x8b\x91\x8fust)
        self.m_VScrollBar.SetBarPosIfCallback(self.m_Head, False)

    
    def GetItemX(self, iIdx):
        x = 0
        for i in xrange(iIdx):
            x += self.m_Widths[i]
        
        return x

    
    def GetItemWidth(self, iIdx):
        return self.m_Widths[iIdx]

    
    def GetTableInfo(self):
        return self.m_TableInfo

    
    def GetNormalTextColor(self):
        return self.m_NormalTxtColor

    
    def GetSelectTextColor(self):
        return self.m_SelectTxtColor

    
    def GetEnterTextColor(self):
        return self.m_EnterTxtColor

    
    def ClickItemByIndex(self, iIndex):
        if len(self.m_Items) == 0:
            return None
        
        if iIndex < 0:
            iIndex = 0
        
        if iIndex >= len(self.m_Items):
            iIndex = len(self.m_Items) - 1
        
        oItem = self.m_Items[iIndex]
        oItem.LeftUp()

    
    def SetTitleFramesShow(self, bShow):
        for oTitle in self.m_TitleObjects:
            oTitle.SetShow(bShow)
        
        for oTitleFrame in self.m_TitleFrames:
            oTitleFrame.SetShow(bShow)
        

    
    def SetIsCreateVerticalLine(self, bCreate):
        self.m_bCreateVerticalLine = bCreate

    
    def AlignItem(self, oItem, iIdx, iAlign, tOffset):
        if 0 > iIdx or iIdx >= len(self.m_Widths):
            return None
        
        (iItW, iItH) = oItem.GetSize()
        iBoxW = self.m_Widths[iIdx]
        iBoxH = self.m_ItemHeight
        (x, y) = interface.GetAlignXY(iItW, iItH, iBoxW, iBoxH, iAlign)
        iStartX = sum(self.m_Widths[:iIdx])
        oItem.SetPos(iStartX + x + tOffset[0], y + tOffset[1])

    
    def CreateTitle(self, sTitleList):
        import combdialog
        sFontType = self.m_TableInfo['sTitleFontType']
        iTitleFontID = fontdata.GetFont(sFontType)
        iTitleColor = self.m_TableInfo['iTitleColor']
        sTitlePath = self.m_TableInfo['sTitlePath']
        bTFStrength = self.m_TableInfo['bTFStrength']
        sTitleSplitPath = self.m_TableInfo['sTitleSplitPath']
        bWhole = self.m_TableInfo['bWhole']
        oScroll = scrollwidget.CVScrollBar(self, 100, sType = self.m_TableInfo['sScrollType'])
        if combdialog.IsUseNewTable():
            iScrollW = oScroll.GetWidth() + self.m_TableInfo['iScrollSpace']
        else:
            iScrollW = 1
        if bWhole:
            oTitleFrame = framewidget.CHFrame(self, sum(self.m_Widths) + iScrollW, sTitlePath)
            self.m_TitleFrames.append(oTitleFrame)
        else:
            for i, _ in enumerate(sTitleList):
                oTitleFrame = framewidget.CHFrame(self, self.m_Widths[i] + 1, sTitlePath)
                oTitleFrame.SetPos(sum(self.m_Widths[:i]), 0)
                self.m_TitleFrames.append(oTitleFrame)
            
        iTitleH = self.m_TitleFrames[0].GetSize()[1]
        if sTitleSplitPath:
            for i, _ in enumerate(sTitleList):
                if i == 0:
                    continue
                
                oImg = ui.CImage(self, sTitleSplitPath, interface.UIPath)
                (_, iImgH) = oImg.GetSize()
                oImg.SetPos(sum(self.m_Widths[:i]), (iTitleH - iImgH) / 2)
                self.m_TitleFrames.append(oImg)
            
        
        iWidth = 0
        iHeight = iTitleH
        iSize = len(sTitleList)
        for i, sTxt in enumerate(sTitleList):
            if bTFStrength:
                oTitle = interface.COverstrikingTextObject(self, sTxt, iTitleFontID, iTitleColor, 0)
            else:
                oTitle = interface.CTextObject(self, sTxt, iTitleFontID, iTitleColor, 0)
            (iTxtW, iTxtH) = oTitle.GetSize()
            iItW = self.m_Widths[i]
            (x, y) = interface.GetAlignXY(iTxtW, iTxtH, iItW, iHeight, interface.ALIGN_CENTER_MIDDLE)
            iStartX = sum(self.m_Widths[:i])
            oTitle.SetPos(iStartX + x, y)
            oTitle.SetZ(1)
            oHotBox = CHotbox(self, iWidth, 0, self.m_Widths[i], iHeight)
            oHotBox.m_Index = i
            self.m_TitleObjects.append(oTitle)
            self.m_Objects.append(oHotBox)
            iWidth += self.m_Widths[i]
        
        return (iWidth, iHeight)

    
    def CraeteItemLine(self, w, h):
        sBgPath = self.m_TableInfo['sBgPath']
        sSplitPath = self.m_TableInfo['sSplitPath']
        iItAlpha = self.m_TableInfo['iItAlpha']
        iOffsetY = self.m_ItemStartY
        iItH = h / self.m_Row
        iItW = w
        if type(sBgPath) == str:
            oBg = framewidget.CFrame(self, w, iItH * self.m_Row, sBgPath)
            oBg.SetPos(0, iOffsetY)
            oBg.SetZ(-1)
            self.m_Objects.append(oBg)
            for iIdx in xrange(1, self.m_Row):
                oLine = framewidget.CHFrame(self, w, sSplitPath)
                oLine.SetPos(0, iOffsetY + iIdx * iItH - 1)
                oLine.SetZ(1)
                self.m_Objects.append(oLine)
            
        else:
            (iColor1, iColor2) = sBgPath
            for iIdx in xrange(self.m_Row):
                if iIdx & 1 == 0:
                    iColor = iColor1
                else:
                    iColor = iColor2
                oBox = interface.CBoxObject(self, iItW, iItH, iColor, iItAlpha)
                oBox.SetZ(-1)
                oBox.SetPos(0, iOffsetY + iIdx * iItH)
                self.m_Objects.append(oBox)
            
            for iIdx in xrange(self.m_Row + 1):
                oLine = interface.CBoxObject(self, iItW, 1, sSplitPath, 255)
                oLine.SetPos(0, iOffsetY + iIdx * iItH)
                oLine.SetZ(1)
                self.m_Objects.append(oLine)
            
            if self.m_bCreateVerticalLine:
                iPosX = 0
                oLine = interface.CBoxObject(self, 1, iItH * self.m_Row, sSplitPath, 255)
                oLine.SetPos(iPosX, iOffsetY)
                oLine.SetZ(1)
                self.m_Objects.append(oLine)
                for iWidth in self.m_Widths:
                    iPosX += iWidth
                    oLine = interface.CBoxObject(self, 1, iItH * self.m_Row, sSplitPath, 255)
                    oLine.SetPos(iPosX, iOffsetY)
                    oLine.SetZ(1)
                    self.m_Objects.append(oLine)
                
            

    
    def CreateScrollBar(self):
        bScrollTop = self.m_TableInfo['bScrollTop']
        sScrollType = self.m_TableInfo['sScrollType']
        iScrollSpace = self.m_TableInfo['iScrollSpace']
        if bScrollTop:
            iHeight = self.m_Size[1]
            self.m_VScrollBar = scrollwidget.CVScrollBar(self, iHeight, sType = sScrollType)
            self.m_VScrollBar.SetPos(self.m_ItemWidth + iScrollSpace, 0)
        else:
            iHeight = self.m_Size[1] - self.m_ItemStartY
            self.m_VScrollBar = scrollwidget.CVScrollBar(self, iHeight, sType = sScrollType)
            self.m_VScrollBar.SetPos(self.m_ItemWidth + iScrollSpace, self.m_ItemStartY)

    
    def OnHotEnter(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnHotEnter'):
            parent.OnHotEnter(it)
        

    
    def OnHotLeave(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnHotLeave'):
            parent.OnHotLeave(it)
        

    
    def OnHotLeftUp(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnHotLeftUp'):
            parent.OnHotLeftUp(it)
        

    
    def OnHotLeftDown(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnHotLeftDown'):
            parent.OnHotLeftDown(it)
        

    
    def OnHotRightUp(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnHotRightUp'):
            parent.OnHotRightUp(it)
        

    
    def OnHotRightDown(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnHotRightDown'):
            parent.OnHotRightDown(it)
        

    
    def OnItemEnter(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnItemEnter'):
            parent.OnItemEnter(it)
        

    
    def OnItemLeave(self, it):
        parent = self.GetParent()
        if hasattr(parent, 'OnItemLeave'):
            parent.OnItemLeave(it)
        

    
    def MouseWheelDown(self, p):
        if p > 0 and hasattr(self, 'm_VScrollBar'):
            bp = self.m_VScrollBar.GetPos()
            self.m_VScrollBar.SetBarPos(bp + p)
        

    
    def MouseWheelUp(self, p):
        if p > 0 and hasattr(self, 'm_VScrollBar'):
            bp = self.m_VScrollBar.GetPos()
            self.m_VScrollBar.SetBarPos(bp - p)
        

    
    def OnMessage(self, msgid):
        self.GetParent().OnMessage(msgid + self.m_MsgID)

    
    def GetScrollBar(self):
        return self.m_VScrollBar



class CHotbox(interface.CBoxObject, interface.CBase):
    
    def __init__(self, parent, x, y, w, h):
        interface.CBoxObject.__init__(self, parent, w, h, 0, 0)
        self.SetPos(x, y)
        self.MessageProcess()

    
    def LeftUp(self):
        parent = self.GetParent().GetParent()
        if hasattr(parent, 'OnHotBoxClick'):
            parent.OnHotBoxClick(self)
        

    
    def Enter(self):
        parent = self.GetParent().GetParent()
        if hasattr(parent, 'OnHotBoxEnter'):
            parent.OnHotBoxEnter(self)
        

    
    def Leave(self):
        
        try:
            parent = self.GetParent().GetParent()
        except:
            return None

        if parent and hasattr(parent, 'OnHotBoxLeave'):
            parent.OnHotBoxLeave(self)
        



class CHotArea(interface.CClickBox):
    
    def Enter(self):
        oIt = self.GetParent()
        if oIt:
            oItParent = oIt.GetParent()
            if oItParent:
                pass
            oItParent.OnHotEnter(oIt)
            oIt.Enter()
        

    
    def Leave(self):
        oIt = self.GetParent()
        if oIt:
            oItParent = oIt.GetParent()
            if oItParent:
                pass
            oItParent.OnHotLeave(oIt)
            oIt.Leave()
        

    
    def LeftDown(self):
        oIt = self.GetParent()
        if oIt:
            oItParent = oIt.GetParent()
            if oItParent:
                pass
            oItParent.OnHotLeftDown(oIt)
            oIt.LeftDown()
        

    
    def LeftUp(self):
        oIt = self.GetParent()
        if oIt:
            oItParent = oIt.GetParent()
            if oItParent:
                pass
            oItParent.OnHotLeftUp(oIt)
            oIt.LeftUp()
        

    
    def RightDown(self):
        oIt = self.GetParent()
        if oIt:
            oItParent = oIt.GetParent()
            if oItParent:
                pass
            oItParent.OnHotRightDown(oIt)
            oIt.RightDown()
        

    
    def RightUp(self):
        oIt = self.GetParent()
        if oIt:
            oItParent = oIt.GetParent()
            if oItParent:
                pass
            oItParent.OnHotRightUp(oIt)
            oIt.RightUp()
        

    
    def MouseWheelDown(self, p):
        self.GetParent().MouseWheelDown(p)

    
    def MouseWheelUp(self, p):
        self.GetParent().MouseWheelUp(p)



class CCombCheckBox(boxwidget.CCheckBox):
    
    def __init__(self, oParent, oCombBoxList, w, h, normal_color = -1, enter_color = -1, select_color = -1, msgid = 0, alpha = 256, iInserIdx = None):
        boxwidget.CCheckBox.__init__(self, oParent, w, h, normal_color, enter_color, select_color, alpha, msgid)
        self.m_bPlaySound = True
        self.m_iSoundType = sound.SND_BUTTON
        self.m_NormalTxtColor = oParent.GetNormalTextColor()
        self.m_SelectTxtColor = oParent.GetSelectTextColor()
        self.m_EnterTxtColor = oParent.GetEnterTextColor()
        self.m_CombBoxs = oCombBoxList
        self.m_MultiSelect = False
        if iInserIdx is not None:
            oCombBoxList.insert(iInserIdx, self)
        else:
            oCombBoxList.append(self)

    
    def SetMultiSelect(self, bSet):
        self.m_MultiSelect = bSet

    
    def UpdateTxtColor(self, iNormalColor = None, iSelectColor = None, iEnterColor = None):
        if iNormalColor is not None:
            self.m_NormalTxtColor = iNormalColor
        
        if iSelectColor is not None:
            self.m_SelectTxtColor = iSelectColor
        
        if iEnterColor is not None:
            self.m_EnterTxtColor = iEnterColor
        

    
    def Select(self, bSelect, bSpecial = False):
        if self.m_Selected == bSelect and not bSpecial:
            return None
        
        self.m_Selected = bSelect
        if bSelect:
            self.SetBg(self.m_SelectColor)
            self.RefreshTextColor(self.m_SelectTxtColor)
        else:
            self.SetBg(self.m_NormalColor)
            self.RefreshTextColor(self.m_NormalTxtColor)

    
    def LeftUp(self):
        interface.CClickObject.LeftUp(self)
        import C_sys
        tm = C_sys.GetTime()
        if hasattr(self, 'm_LeftUpTime'):
            if tm - self.m_LeftUpTime <= tm - self.m_LeftUpTime:
                pass
            elif tm - self.m_LeftUpTime < 5000 and self.m_DoubleClikcCB:
                self.m_DoubleClikcCB()
            
        
        self.m_LeftUpTime = tm
        if self.m_SelectColor == -1:
            return None
        
        if self.m_MultiSelect:
            self.Select(not (self.m_Selected))
        elif not self.m_Selected:
            if self.m_CombBoxs:
                for cb in self.m_CombBoxs:
                    cb.Select(False)
                
            
            self.Select(True)
        

    
    def OnMessage(self, msgid):
        if hasattr(self.GetParent(), 'OnMessage'):
            self.GetParent().OnMessage(msgid)
        

    
    def Enter(self):
        boxwidget.CCheckBox.Enter(self)
        if not self.m_Selected:
            self.RefreshTextColor(self.m_EnterTxtColor)
        
        oParent = self.GetParent()
        if hasattr(oParent, 'OnItemEnter'):
            oParent.OnItemEnter(self)
        

    
    def Leave(self):
        boxwidget.CCheckBox.Leave(self)
        if not self.m_Selected:
            self.RefreshTextColor(self.m_NormalTxtColor)
        
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'OnItemLeave'):
            oParent.OnItemLeave(self)
        

    
    def RefreshTextColor(self, iColor):
        self.SetTextColor(iColor)

    
    def SetTextColor(self, iColor):
        oTextObject = getattr(self, 'm_TextObject', None)
        oTextObjectList = getattr(self, 'm_TextObjects', None)
        if oTextObject and hasattr(oTextObject, 'SetColor'):
            oTextObject.SetColor(iColor)
        
        if oTextObjectList:
            for oText in oTextObjectList:
                if oText and hasattr(oText, 'SetColor'):
                    oText.SetColor(iColor)
                    continue
            
        


g_TestObj = None

def TestCreateTable():
    global g_TestObj
    import interface
    import combdialog
    sTitles = [
        '5555',
        '6666']
    iRow = 5
    w = 150
    h = 200
    iMsgID = 200
    iWidthList = [
        65,
        60]
    oNew = CTable(interface.DialogPanel, sTitles, iRow, w, h, iMsgID, iWidthList)
    oNew.ResetItems()
    oNew.ResetScrollBar()
    oNew.SetPos(50, 50)
    oNew.SetZ(10000000)
    sTitles = '5555\n6666'
    if interface.GetStyle() == 2:
        oOld = combdialog.CPngTable(interface.DialogPanel, [
            60,
            65,
            iMsgID,
            h,
            w,
            iRow,
            sTitles])
    else:
        oOld = combdialog.CTable(interface.DialogPanel, [
            60,
            65,
            iMsgID,
            h,
            w,
            iRow,
            sTitles])
    oOld.ResetItems()
    oOld.ResetScrollBar()
    oOld.SetPos(300, 50)
    oOld.SetZ(10000000)
    g_TestObj = [
        oNew,
        oOld]
    return (oNew, oOld)


def TestAddText():
    (oNew, oOld) = TestCreateTable()
    for i in range(20):
        if i % 3 == 1:
            oNew.AddTextItem([
                'txt_%d' % i,
                'txt_%d' % i], iEnterColor = 65535, iSelectColor = 16711935)
            continue
        oNew.AddTextItem([
            'txt_%d' % i,
            'txt_%d' % i])
    
    oNew.ResetItems()
    oNew.ResetScrollBar()
    for i in range(20):
        oOld.AddTextItem([
            'txt_%d' % i,
            'txt_%d' % i])
    
    oOld.ResetItems()
    oOld.ResetScrollBar()


def TestAddMulLine():
    (oNew, oOld) = TestCreateTable()
    for i in range(20):
        if i % 3 == 1:
            oNew.AddMulLineItem([
                'txt_%d#r111' % i,
                'txt_%d' % i], iEnterColor = 65535, iSelectColor = 16711935, dAlignInfo = {
                'iAlign': interface.ALIGN_LEFT_MIDDLE,
                'tOffset': (2, 0) })
            continue
        oNew.AddMulLineItem([
            'txt_%d#r111' % i,
            'txt_%d' % i])
    
    oNew.ResetItems()
    oNew.ResetScrollBar()
    for i in range(20):
        oOld.AddMulLineItem([
            'txt_%d#r111' % i,
            'txt_%d' % i])
    
    oOld.ResetItems()
    oOld.ResetScrollBar()


def TestSetTitle():
    (oNew, oOld) = TestCreateTable()
    oNew.SetTitle(0, '\xc4\xb3\xa4@\xc4\xb3', color = 16711680, font = None)
    oOld.SetTitle(0, '\xc4\xb3\xa4@\xc4\xb3', color = 16711680, font = None)
