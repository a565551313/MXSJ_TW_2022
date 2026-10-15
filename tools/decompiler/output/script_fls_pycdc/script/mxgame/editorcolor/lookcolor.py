# pycdc 交叉复核产物 · script.fls entry 4599
# co_filename(原始)='script/mxgame/editorcolor/lookcolor.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4599.pyc (Python 2.5)

import C_sys
import interface
import ui
import combdialog
import combmacro
import colordata
import gamefont
SIMHEI = 'simhei.ttf'
LANTING = 'FZLanTingYuan-DB-GBK.ttf'
SONGTI = '\xb2\xd3\xa9\xfa\xc5\xe9'
FONTLIST = [
    ('\xb2\xd3\xa9\xfa\xc5\xe912', 12, SONGTI),
    ('\xb2\xd3\xa9\xfa\xc5\xe914', 14, SONGTI),
    ('\xb2\xd3\xa9\xfa\xc5\xe916', 16, SONGTI),
    ('\xb2\xd3\xa9\xfa\xc5\xe918', 18, SONGTI),
    ('\xb2\xd3\xa9\xfa\xc5\xe920', 20, SONGTI),
    ('\xb2\xd3\xa9\xfa\xc5\xe936', 36, SONGTI),
    ('\xb2\xd3\xa9\xfa\xc5\xe972', 72, SONGTI),
    ('\xb6\xc2\xc5\xe912', 12, SIMHEI),
    ('\xb6\xc2\xc5\xe914', 14, SIMHEI),
    ('\xb6\xc2\xc5\xe916', 16, SIMHEI),
    ('\xb6\xc2\xc5\xe918', 18, SIMHEI),
    ('\xb6\xc2\xc5\xe920', 20, SIMHEI),
    ('\xb6\xc2\xc5\xe936', 36, SIMHEI),
    ('\xb6\xc2\xc5\xe972', 72, SIMHEI),
    ('\xc4\xf5\xabF12', 12, LANTING),
    ('\xc4\xf5\xabF14', 14, LANTING),
    ('\xc4\xf5\xabF16', 16, LANTING),
    ('\xc4\xf5\xabF18', 18, LANTING),
    ('\xc4\xf5\xabF20', 20, LANTING),
    ('\xc4\xf5\xabF36', 36, LANTING),
    ('\xc4\xf5\xabF72', 72, LANTING)]
RADIUSLIST = [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10]
g_oLookColor = None
g_oEditorClolr = None
g_bHexColorEdit = False
g_bColorEdit = False
g_bMoveSigin = False
g_ColorPreviewPanel = None
g_FontPreviewPanel = None
g_FontOffsetPanel = None

def ModuleReset():
    global g_oLookColor, g_oEditorClolr, g_bHexColorEdit, g_bColorEdit, g_bMoveSigin, g_ColorPreviewPanel, g_FontPreviewPanel
    g_oLookColor = None
    g_oEditorClolr = None
    g_bHexColorEdit = False
    g_bColorEdit = False
    g_bMoveSigin = False
    g_ColorPreviewPanel = None
    g_FontPreviewPanel = None


def Show():
    global g_oLookColor
    g_oLookColor = CLookColorDlg()


def ShowColorPreviewPanel():
    global g_ColorPreviewPanel
    g_ColorPreviewPanel = CColorPreviewPanel()


def ShowFontPreviewPanel():
    global g_FontPreviewPanel
    g_FontPreviewPanel = CFontPreviewPanel()


class CLookColorDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/fontcolor/textcolor.dlg')
        interface.Center(self)
        self.CreateList()

    
    def CreateList(self):
        obj = self.GetObject('list')
        for i in xrange(len(colordata.DATA)):
            obj.AddTextItem('\xa4\xe8\xae\xd7%d' % (i + 1))
        
        obj.ResetItems()
        obj.ResetScrollBar()

    
    def ShowDesign(self, dColor):
        tFontInfoList = [
            (interface.FontST14, interface.FontST14E, interface.FontST14G, interface.FontST14E),
            (interface.FontST14, interface.FontST14E, interface.FontST14G, interface.FontST14E),
            (interface.FontLT14, interface.FontLT14E, interface.FontLT14G, interface.FontLT14EG),
            (interface.FontLT14, interface.FontLT14E, interface.FontLT14G, interface.FontLT14EG)]
        self.m_oStyleList = []
        if not dColor:
            import usermacro
            usermacro.PROMPT_MSG('\xb8\xd3\xa4\xe8\xae\xd7\xc3C\xa6\xe2\xaf\xca\xa5\xa2\xa1A\xbd\xd0\xae\xd6\xb9\xef\xc3C\xa6\xe2\xbe\xc9\xaa\xed\xa4\xa4\xa6\xb3\xb5L\xa6\xb9\xa4\xe8\xae\xd7')
            return None
        
        for iIdx, iColor in dColor.items():
            if iIdx == 4:
                continue
            
            iFontIDList = tFontInfoList[iIdx - 1]
            if type(iColor) == int:
                iFontID = iFontIDList[0]
                iOtherFontID = None
            elif len(iColor) == 2:
                iFontID = iFontIDList[1]
                iOtherFontID = iFontIDList[2]
            else:
                iFontID = iFontIDList[3]
                iOtherFontID = None
            oText = combmacro.CTEXT(interface.CTextObject, 'style%d' % iIdx, self, '\xb9\xda\xb7Q\xa5@\xac\xc9\xafu\xa6n\xaa\xb1', iFontID, iColor, align = interface.ALIGN_MIDDLE)
            if iOtherFontID:
                oText.m_Other = interface.CTextObject(oText, '\xb9\xda\xb7Q\xa5@\xac\xc9\xafu\xa6n\xaa\xb1', iOtherFontID, iColor)
                (w, h) = oText.GetSize()
                oText.m_Other.SetPos(0, h + 2)
            
            self.m_oStyleList.append(oText)
        

    
    def CloseWindow(self):
        global g_oLookColor
        g_oLookColor = None

    
    def OnMessage(self, msgid):
        global g_oEditorClolr
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            g_oEditorClolr = CEditorColorDlg(self.GetParent())
        elif msgid < msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE:
            self.ShowDesign(colordata.DATA.get(msgid - 100))
        



class CMyListBox(interface.CListBox):
    
    def OnSelect(self, msgid):
        interface.CListBox.OnSelect(self, msgid)
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'SetFont'):
            oParent.SetFont(self.GetText())
        



class CMyEdit(interface.CEdit):
    
    def AddChar(self, c):
        interface.CEdit.AddChar(self, c)
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'SetText'):
            oParent.SetText(self.GetText())
        

    
    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        oParent = self.GetParent()
        if oParent and hasattr(oParent, 'SetText'):
            oParent.SetText(self.GetText())
        



class CNumEdit(interface.CEdit):
    
    def AddChar(self, char):
        if char.isdigit():
            interface.CEdit.AddChar(self, char)
            self.OnChange()
        
        if hasattr(self, 'm_Max') and self.GetNumber() > self.m_Max:
            self.SetText(str(self.m_Max))
        

    
    def SetMax(self, iMax):
        self.m_Max = iMax

    
    def OnChange(self):
        '''
\t\t\xb3q\xb9Lg_bHexColorEdit\xa1Bg_bColorEdit\xa1Bg_bMoveSigin\xa4T\xad\xd3\xc5\xdc\xb6q\xad\xc8\xa8\xd3\xc1\xd7\xa7K\xb4`\xc0\xf4\xbd\xd5\xa5\xce\xaa\xba\xb2{\xb6H
\t\t'''
        parent = self.GetParent()
        if parent and hasattr(parent, 'OnEditChange') and self in parent.m_oColorUIList and not g_bHexColorEdit and not g_bMoveSigin:
            idx = parent.m_oColorUIList.index(self)
            num = int(self.GetText())
            parent.OnEditChange(idx, num)
        

    
    def LeftDown(self):
        global g_bHexColorEdit, g_bColorEdit, g_bMoveSigin
        self.Active(True)
        g_bHexColorEdit = False
        g_bColorEdit = True
        g_bMoveSigin = False
        interface.CEdit.LeftDown(self)

    
    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        if self.GetText().isdigit():
            self.OnChange()
        



class CHexNumEdit(CNumEdit):
    
    def AddChar(self, char):
        
        try:
            interface.CEdit.AddChar(self, char)
            iNum = eval(self.GetText())
            if hasattr(self, 'm_Max') and iNum > self.m_Max:
                self.SetText(str(hex(self.m_Max)))
            
            self.OnChange()
        except:
            return None


    
    def LeftDown(self):
        global g_bHexColorEdit, g_bColorEdit, g_bMoveSigin
        self.Active(True)
        g_bHexColorEdit = True
        g_bColorEdit = False
        g_bMoveSigin = False
        interface.CEdit.LeftDown(self)

    
    def OnChange(self):
        parent = self.GetParent()
        if parent and hasattr(parent, 'OnHexEditChange') and self in parent.m_oColorValuesHexList and not g_bColorEdit and not g_bMoveSigin:
            idx = parent.m_oColorValuesHexList.index(self)
            num = eval(self.GetText())
            parent.OnHexEditChange(idx, num)
        

    
    def DeleteChar(self):
        interface.CEdit.DeleteChar(self)
        
        try:
            iNum = eval(self.GetText())
            self.OnChange()
        except:
            return None




class CHSlider(interface.CHSlider):
    
    class CBar(interface.CHSlider.CBar):
        
        def MouseWheelDown(self, p):
            self.GetParent().MouseWheelDown(p)

        
        def MouseWheelUp(self, p):
            self.GetParent().MouseWheelUp(p)

        
        def Hold(self):
            global g_bHexColorEdit, g_bColorEdit, g_bMoveSigin
            g_bHexColorEdit = False
            g_bColorEdit = False
            g_bMoveSigin = True
            interface.CHSlider.CBar.Hold(self)


    
    def __init__(self, parent, x, y, w, h, n_max = 100, fname = None, path = None):
        y = y - 10
        h = h + 20
        interface.CHSlider.__init__(self, parent, x, y, w, h, n_max, fname, path)

    
    def LeftUp(self):
        global g_bHexColorEdit, g_bColorEdit, g_bMoveSigin
        g_bHexColorEdit = False
        g_bColorEdit = False
        g_bMoveSigin = True
        interface.CHSlider.LeftUp(self)

    
    def MouseWheelDown(self, p):
        pos = self.GetBarPos()
        pos = pos - p
        if pos < 0:
            pos = 0
        
        self.SetBarPos(pos)

    
    def MouseWheelUp(self, p):
        pos = self.GetBarPos()
        pos = pos + p
        if pos > self.m_nMax:
            pos = self.m_nMax
        
        self.SetBarPos(pos)

    
    def PosChange(self, pos):
        interface.CHSlider.PosChange(self, pos)
        if hasattr(g_oEditorClolr, 'm_oColorLineList') and self in g_oEditorClolr.m_oColorBarList and not g_bHexColorEdit and not g_bColorEdit:
            idx = g_oEditorClolr.m_oColorBarList.index(self)
            g_oEditorClolr.ChangePos(idx, pos)
        



class CEditorColorDlg(combdialog.CCombDialog):
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/fontcolor/textdesign.dlg')
        interface.Center(self)
        self.m_oFont = interface.FontHT12
        self.m_sTxt = '\xb9\xda\xb7Q\xa5@\xac\xc9\xafu\xa6n\xaa\xb1'
        self.m_iColorList = [
            12006177,
            0,
            0]
        self.m_iFontSize = 12
        self.m_sFont = FONTLIST[0][0]
        self.m_iStrength = 0
        self.m_iStyle = 0
        self.m_iEdgeRadius = 0
        self.m_iWeight = 400
        self.m_iN = 0
        self.m_iStorke = 0
        self.m_iColorGrad = 0
        self.m_iBit = 0
        self.CreateFontDesign()
        self.CreateTextBox()
        self.CreateColorLine()
        self.CreateColorBar()
        self.CreateColorValue()
        self.CreateColorValueHex()

    
    def OnEditChange(self, idx, num):
        self.m_oColorBarList[idx].SetBarPos(num)
        self.ChangeColor(idx, num)

    
    def ChangePos(self, idx, num):
        self.m_oColorUIList[idx].SetText(str(num))
        self.ChangeColor(idx, num)

    
    def OnHexEditChange(self, idx, num):
        self.m_iColorList[idx] = num
        for index, iNum in enumerate(self.m_iColorList):
            for idx in xrange(3):
                if idx == 0:
                    iValue = iNum / 65536
                elif idx == 1:
                    iValue = iNum / 256 % 256
                else:
                    iValue = iNum % 256
                self.m_iColorValuesList[index * 3 + idx] = iValue
                self.m_oColorBarList[index * 3 + idx].SetBarPos(iValue)
                self.m_oColorUIList[index * 3 + idx].SetText(str(iValue))
            
        
        self.OnCall()

    
    def ChangeColor(self, idx, icolor):
        self.m_iColorValuesList[idx] = icolor
        for index in (0, 3, 6):
            iColor = self.m_iColorValuesList[index] * 65536 + self.m_iColorValuesList[index + 1] * 256 + self.m_iColorValuesList[index + 2]
            self.m_iColorList[index / 3] = iColor
            self.m_oColorValuesHexList[index / 3].SetText(str(hex(iColor)))
        
        self.OnCall()

    
    def OnCall(self):
        self.m_iN = self.m_iStyle = self.m_iStorke | self.m_iColorGrad | self.m_iBit
        self.CreateFont(self.m_iFontSize, self.m_sFont, self.m_iStrength, self.m_iStyle, self.m_iEdgeRadius, self.m_iWeight, self.m_iN)

    
    def SetFont(self, sFont):
        for tFont in FONTLIST:
            if sFont in tFont:
                self.m_iFontSize = tFont[1]
                self.m_sFont = tFont[2]
                self.OnCall()
                return None
                continue
        
        if int(sFont) in RADIUSLIST:
            self.m_iEdgeRadius = int(sFont)
            self.OnCall()
            return None
        

    
    def SetText(self, sTxt):
        self.m_sTxt = sTxt
        self.OnCall()

    
    def CreateFont(self, iSize = 16, sFont = SONGTI, strength = 0, type = 0, edge_radius = 0, Weight = 400, n = 0):
        '''
\t\tiSize\xa6r\xc5\xe9\xa4j\xa4p\xa1A
\t\tsFont\xa6r\xc5\xe9\xa4\xe5\xa5\xf3\xa1A
\t\tstrength\xa6r\xc5\xe9\xa5[\xb2\xca\xad\xc8\xa1A
\t\ttype\xa1G\xb3]\xb8m\xacO\xa7_\xb4y\xc3\xe4\xa1B\xba\xa5\xb6i\xa6\xe2\xa1B\xa6\xec\xb4\xe8\xacV\xa1A\xa8\xfa\xad\xc8\xac\xb0 NORMAL=0, EDGE=1, GRAD=2, MONO=4 \xaa\xba\xa6\xec\xb9B\xba\xe2\xb2\xd5\xa6X
\t\tedge_radius\xa1G\xa6b\xb4y\xc3\xe4\xaa\xac\xbaA\xa4U\xa1A\xa5\xce\xa9\xf3\xab\xfc\xa9w\xb4y\xc3\xe4\xa6r\xc5\xe9\xc3\xe4\xbdt\xa5b\xae|\xa1A\xc0q\xbb{\xac\xb01\xa1A\xa7Y1\xb9\xb3\xaf\xc0\xaa\xba\xb4y\xc3\xe4

\t\t# \xb2\xd3\xa9\xfa\xc5\xe9\xa6r
\t\tWeight\xa1G0,100-900
\t\tn\xa1G0\xb4\xb6\xb3q,1\xa5]\xc3\xe4,2\xba\xa5\xb6i\xa6\xe2,4\xb1\xd7\xc5\xe9
\t\t'''
        if sFont == SONGTI:
            self.m_oFont = C_sys.CreateFont(sFont, iSize, Weight, n)
        else:
            self.m_oFont = C_sys.CreateFontFromFile(sFont, 0, iSize, 72, strength, type, edge_radius, 0)
        self.ShowDesign(self.m_sTxt, self.m_oFont, self.m_iColorList)

    
    def CreateFontDesign(self):
        self.m_oListBox = combmacro.CLISTBOX(CMyListBox, 'fontdesign', self, 0, interface.FontHT14)
        (x, y) = self.m_oListBox.GetPos()
        self.m_oListBox.SetPos(x, y - 2)
        self.m_oListBox.SetItemProp(2, 16, 300)
        self.m_oListBox.SetReadOnly(True)
        self.m_oListBox.SetText(FONTLIST[0][0])
        self.SetFont(FONTLIST[0][0])
        for tFont in FONTLIST:
            self.m_oListBox.AddTextItem(tFont[0])
        

    
    def CreateStrokeEdit(self):
        self.m_oRadius = combmacro.CLISTBOX(CMyListBox, 'miaobian', self, 0, interface.FontHT14)
        (x, y) = self.m_oRadius.GetPos()
        self.m_oRadius.SetPos(x, y - 2)
        self.m_oRadius.SetItemProp(2, 16, 200)
        self.m_oRadius.SetReadOnly(True)
        self.m_oRadius.SetText(str(RADIUSLIST[0]))
        self.SetFont(str(RADIUSLIST[0]))
        for radius in RADIUSLIST:
            self.m_oRadius.AddTextItem(str(radius))
        

    
    def RemoveStrokEdit(self):
        self.m_oRadius = None
        self.m_iEdgeRadius = 0
        self.OnCall()

    
    def CreateTextBox(self):
        self.m_oTextBox = combmacro.CEDIT(CMyEdit, 'txt', self, 12006177, interface.FontHT14)
        self.m_oTextBox.SetDefaultTips(self.m_sTxt)

    
    def CreateColorLine(self):
        ColorBarList = [
            'RBar',
            'GBar',
            'BBar']
        ColorNameList = [
            'red',
            'green',
            'blue']
        self.m_oColorLineList = []
        for index in xrange(1, 4):
            for idx, sName in enumerate(ColorBarList):
                (x, y) = self.GetObject(sName + str(index)).GetPos()
                fname = 'color/' + '%s.igs' % ColorNameList[idx]
                obj = ui.CImage(self, fname, interface.UIPath)
                obj.SetPos(x + 1, y + 1)
                self.m_oColorLineList.append(obj)
            
        

    
    def CreateColorBar(self):
        self.InitColorList()
        self.m_oColorBarList = []
        for idx, oColor in enumerate(self.m_oColorLineList):
            (w, h) = oColor.GetSize()
            obj = CHSlider(oColor, -6, 10, w + 12, h, 255, 'color/bar.igs', interface.UIPath)
            obj.SetBarPos(self.m_iColorValuesList[idx])
            self.m_oColorBarList.append(obj)
        

    
    def InitColorList(self):
        self.m_iColorValuesList = []
        for iColor in self.m_iColorList:
            values = '%d,%d,%d' % (iColor / 65536, iColor / 256 % 256, iColor % 256)
            for i in values.split(','):
                self.m_iColorValuesList.append(int(i))
            
        

    
    def CreateColorValue(self):
        ColorUIList = [
            'R',
            'G',
            'B']
        self.m_oColorUIList = []
        for index in xrange(3):
            for idx, sName in enumerate(ColorUIList):
                txt = self.m_iColorValuesList[index * 3 + idx]
                obj = combmacro.CEDIT(CNumEdit, sName + str(index + 1), self, 12006177, interface.FontHT14)
                obj.SetText(str(txt))
                obj.SetMax(255)
                (x, y) = obj.GetPos()
                obj.SetPos(x, y - 2)
                self.m_oColorUIList.append(obj)
            
        

    
    def CreateColorValueHex(self):
        self.m_oColorValuesHexList = []
        for index in xrange(3):
            txt = hex(self.m_iColorList[index])
            obj = combmacro.CEDIT(CHexNumEdit, 'color%d' % (index + 1), self, 12006177, interface.FontHT14)
            obj.SetText(str(txt))
            obj.SetMax(16777215)
            (x, y) = obj.GetPos()
            obj.SetPos(x, y - 2)
            self.m_oColorValuesHexList.append(obj)
        

    
    def ShowDesign(self, txt = '\xb9\xda\xb7Q\xa5@\xac\xc9\xafu\xa6n\xaa\xb1', font = interface.FontHT16, color = [
        12006177,
        16777215,
        16777215]):
        '''
\t\t# color\xa1G\xa5i\xa5H\xacO\xa6C\xaa\xed\xa1A\xa6C\xaa\xed\xb3\xcc\xa6h\xa4T\xad\xd3\xad\xc8[0x0, 0x0, 0x0]\xb2\xc4\xa4@\xad\xd3\xa5N\xaa\xed\xa6r\xc5\xe9\xa5\xbf\xb1`\xc3C\xa6\xe2\xad\xc8\xa1A\xb2\xc4\xa4G\xad\xd3\xacO\xb4y\xc3\xe4\xa1A\xb2\xc4\xa4T\xad\xd3\xacO\xba\xa5\xc5\xdc
\t\t'''
        self.m_oTxtList = []
        for i in xrange(3):
            oTxt = combmacro.CTEXT(interface.CTextObject, 'style%d' % (i + 1), self, txt, font, color, align = interface.ALIGN_MIDDLE)
            self.m_oTxtList.append(oTxt)
        

    
    def SetStroke(self):
        oBtn = self.GetObject('btn_miaobian')
        if oBtn.IsSelected():
            oBtn.SetSelect(False)
            self.m_iStorke = 0
            self.m_iN = 0
            self.RemoveStrokEdit()
        else:
            oBtn.SetSelect(True)
            self.m_iStorke = 1
            self.m_iN = 1
            self.CreateStrokeEdit()

    
    def SetColorGrad(self):
        oBtn = self.GetObject('btn_jianbian')
        if oBtn.IsSelected():
            oBtn.SetSelect(False)
            self.m_iColorGrad = 0
        else:
            oBtn.SetSelect(True)
            self.m_iColorGrad = 2
        self.OnCall()

    
    def CloseWindow(self):
        global g_oEditorClolr
        g_oEditorClolr = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.SetStroke()
        elif msgid == 3:
            self.SetColorGrad()
        



class CColorBox(interface.CBoxObject, interface.CBase):
    
    def __init__(self, oParent, iColor, w, h, iStyle):
        interface.CBoxObject.__init__(self, oParent, w, h, 0, 0)
        self.MessageProcess()
        self.m_Color = iColor
        self.m_Style = iStyle
        self.CreateTextObj()
        self.CreateBg()

    
    def CreateTextObj(self):
        if self.m_Color is None:
            return None
        
        sShowTxt = '\xa4\xa4\xa4\xe512AaBb'
        sFontName = None if self.m_Style in (3, 4, 5) else gamefont.TYPE_SONGTI
        if type(self.m_Color) == list or len(self.m_Color) == 2:
            iFontID = gamefont.CreateFont(sFontName, 14, bEdge = True)
            self.m_Text = interface.CTextObject(self, sShowTxt, iFontID, self.m_Color)
            (_, iTxtH) = self.m_Text.GetSize()
            iFontID = gamefont.CreateFont(sFontName, 14, bGrad = True)
            self.m_Text.m_Sub = interface.CTextObject(self.m_Text, sShowTxt, iFontID, self.m_Color)
            self.m_Text.m_Sub.SetPos(0, iTxtH + 1)
        else:
            iFontID = gamefont.CreateFont(sFontName, 14, bEdge = True, bGrad = True)
            self.m_Text = interface.CTextObject(self, sShowTxt, iFontID, self.m_Color)
        len(self.m_Color) == 2
        iFontID = gamefont.CreateFont(sFontName, 14)
        self.m_Text = interface.CTextObject(self, sShowTxt, iFontID, self.m_Color)
        interface.TopMiddle(self.m_Text, offsety = 5)

    
    def CreateBg(self):
        (w, h) = self.GetSize()
        if self.m_Style == 1:
            self.m_Bg = ui.CFrame(self, w, h, 'combdialog/\xc4\xda\xbf\xf2\xbc\xdc/')
        elif self.m_Style == 2:
            self.m_Bg = ui.CFrame(self, w, h, 'combdialog2/\xb9\xab\xd3\xc3\xc4\xda\xbf\xf2/')
        

    
    def Enter(self):
        import wrapinterface
        if not self.m_Color:
            return None
        
        if type(self.m_Color) == list:
            if len(self.m_Color) == 2:
                sTxt = '\xc3C\xa6\xe2\xa1G#r\xa4Q\xb6i\xa8\xee\xa1G#r%s#r%s#r\xa4Q\xa4\xbb\xb6i\xa8\xee\xa1G#r%s#r%s' % (self.Hex2Dec(self.m_Color[0]), self.Hex2Dec(self.m_Color[1]), hex(self.m_Color[0]), hex(self.m_Color[1]))
            else:
                sTxt = '\xc3C\xa6\xe2\xa1G#r\xa4Q\xb6i\xa8\xee\xa1G#r%s#r%s#r%s#r\xa4Q\xa4\xbb\xb6i\xa8\xee\xa1G#r%s#r%s#r%s' % (self.Hex2Dec(self.m_Color[0]), self.Hex2Dec(self.m_Color[1]), self.Hex2Dec(self.m_Color[2]), hex(self.m_Color[0]), hex(self.m_Color[1]), hex(self.m_Color[2]))
        else:
            sTxt = '\xc3C\xa6\xe2\xa1G#r\xa4Q\xb6i\xa8\xee\xa1G%s#r\xa4Q\xa4\xbb\xb6i\xa8\xee\xa1G%s' % (self.Hex2Dec(self.m_Color), hex(self.m_Color))
        (w, _) = self.GetSize()
        self.m_Tips = wrapinterface.CTextTips(None, w, sTxt, interface.FontLT14_3, owner = self, direct = 1, alpha = 255)
        self.m_Tips.SetZ(10)

    
    def Leave(self):
        self.m_Tips = None

    
    def Hex2Dec(self, iHex):
        r = (iHex & 16711680) >> 16
        g = (iHex & 65280) >> 8
        b = iHex & 255
        return (r, g, b)

    
    def MouseWheelDown(self, p):
        oParent = self.GetParent()
        if hasattr(oParent, 'MouseWheelDown'):
            oParent.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        oParent = self.GetParent()
        if hasattr(oParent, 'MouseWheelDown'):
            oParent.MouseWheelUp(p)
        



class CColorPreviewPanel(interface.CPanel):
    
    def __init__(self):
        interface.CPanel.__init__(self, interface.DialogPanel)
        self.MessageProcess()
        self.CreateBg()
        self.CreateCloseBtn()
        self.CreateTabel()

    
    def CreateBg(self):
        (w, h) = self.GetSize()
        self.m_BG = interface.CClickBox(self, w, h, 15658734, 255, 0)
        self.m_BG.SetZ(0)

    
    def CreateCloseBtn(self):
        self.m_CloseBtn = interface.CButton(self, 'dialog/dial/close.igs', 0, 0, 1)
        self.m_CloseBtn.SetZ(1)
        interface.TopRight(self.m_CloseBtn)

    
    def CreateTabel(self):
        self.m_Table = ui.CTable(self, [
            '\xa6W\xba\xd9',
            '\xad\xb7\xae\xe61',
            '\xad\xb7\xae\xe62',
            '\xad\xb7\xae\xe63',
            '\xad\xb7\xae\xe64',
            '\xad\xb7\xae\xe65'], 10, 875, 500, 200, [
            145,
            145,
            145,
            145,
            145,
            145])
        interface.Center(self.m_Table)
        self.m_Table.SetZ(1)
        for iType, dColorInfo in colordata.DATA.items():
            oBox = self.m_Table.AddBoxItem()
            oTxtList = []
            iColor = self.m_Table.GetNormalTextColor()
            iFontID = gamefont.CreateFont(gamefont.TYPE_LANTING, 14)
            oName = interface.CTextObject(oBox, 'COLOR_%d' % iType, iFontID, iColor)
            oTxtList.append(oName)
            for iStyle in range(1, 6):
                iColor = dColorInfo.get(iStyle)
                if iColor is None:
                    if iStyle == 4:
                        iColor = dColorInfo.get(3)
                    elif iStyle == 5:
                        iColor = dColorInfo.get(4)
                        if iColor is None:
                            iColor = dColorInfo.get(3)
                        
                    
                
                w = self.m_Table.GetItemWidth(iStyle)
                h = self.m_Table.m_ItemHeight
                oColor = CColorBox(oBox, iColor, w, h, iStyle)
                oTxtList.append(oColor)
            
            self.m_Table.AddItemExtend(oBox, oTxtList, bChangeColor = False)
        
        self.m_Table.ResetItems()
        self.m_Table.ResetScrollBar()

    
    def ClosePanel(self):
        global g_ColorPreviewPanel
        g_ColorPreviewPanel = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ClosePanel()
        



class CTextBox(interface.CBoxObject, interface.CBase):
    
    def __init__(self, oParent, dFontInfo, iColor, w, h, iStyle, bIsCenter = True):
        interface.CBoxObject.__init__(self, oParent, w, h, 0, 0)
        self.MessageProcess()
        self.m_TextColor = iColor
        self.m_Style = iStyle
        import copy
        self.m_FontInfo = copy.deepcopy(dFontInfo)
        self.CreateTextObj(bIsCenter)
        self.CreateBg()

    
    def CreateTextObj(self, bIsCenter):
        dFontInfo = self.m_FontInfo
        sShowTxt = '\xa4\xa4\xa4\xe512AaBb'
        iFontID = gamefont.CreateFont(dFontInfo['sFontName'], dFontInfo['iFontSize'], dFontInfo['iWeight'], bool(dFontInfo['iEdge']), dFontInfo['iEdgeRadius'], bool(dFontInfo['iGrad']), bool(dFontInfo['iMono']), dFontInfo['iOffsetY'])
        self.m_Text = interface.CTextObject(self, sShowTxt, iFontID, self.m_TextColor)
        if bIsCenter:
            interface.Center(self.m_Text)
        else:
            self.m_Text.SetPos(0, 0)
        self.m_Text.SetZ(1)

    
    def CreateBg(self):
        (w, h) = self.GetSize()
        if self.m_Style == 1:
            self.m_Bg = ui.CFrame(self, w, h, 'combdialog/\xc4\xda\xbf\xf2\xbc\xdc/')
        elif self.m_Style == 2:
            self.m_Bg = ui.CFrame(self, w, h, 'combdialog2/\xb9\xab\xd3\xc3\xc4\xda\xbf\xf2/')
        

    
    def Enter(self):
        import wrapinterface
        dFontInfo = self.m_FontInfo
        sTxt = '\xc5\x11\xa6\x8a\xc2$F\x10@\x11\xc5\x11\xdb\xda\xc2$F\x10@\x11\xd1\xa9\xc8\xb4\xc2$F\x10@\x11\xc6>\xa0\x87\xc2$F\x10@\x11\xc6>\xa0\x87\xc6\x01\xcd\x1f\xc2$F\x10@\x11\xd9\xc6\xa6\xbf\xc2$Fs#r\xa6\xec\xb4\xe8\xacV\xa1G%s#rY\xb6b\xb0\xbe\xb2\xbe\xa1G%s#r' % (dFontInfo['sFontName'], dFontInfo['iFontSize'], dFontInfo['iWeight'], bool(dFontInfo['iEdge']), dFontInfo['iEdgeRadius'], bool(dFontInfo['iGrad']), bool(dFontInfo['iMono']), dFontInfo['iOffsetY'])
        (w, _) = self.GetSize()
        self.m_Tips = wrapinterface.CTextTips(None, w, sTxt, interface.FontLT14_3, owner = self, direct = 1, alpha = 255)
        self.m_Tips.SetZ(10)

    
    def Leave(self):
        self.m_Tips = None

    
    def MouseWheelDown(self, p):
        oParent = self.GetParent()
        if hasattr(oParent, 'MouseWheelDown'):
            oParent.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        oParent = self.GetParent()
        if hasattr(oParent, 'MouseWheelDown'):
            oParent.MouseWheelUp(p)
        



class CFontPreviewPanel(interface.CPanel):
    
    def __init__(self):
        interface.CPanel.__init__(self, interface.DialogPanel)
        self.MessageProcess()
        self.CreateBg()
        self.CreateCloseBtn()
        self.CreateTable()

    
    def CreateBg(self):
        (w, h) = self.GetSize()
        self.m_BG = interface.CClickBox(self, w, h, 15658734, 255, 0)
        self.m_BG.SetZ(0)

    
    def CreateCloseBtn(self):
        self.m_CloseBtn = interface.CButton(self, 'dialog/dial/close.igs', 0, 0, 1)
        self.m_CloseBtn.SetZ(1)
        interface.TopRight(self.m_CloseBtn)

    
    def CreateTable(self):
        import fontdata
        self.m_Table = ui.CTable(self, [
            '\xa6W\xba\xd9',
            '\xad\xb7\xae\xe61',
            '\xad\xb7\xae\xe62',
            '\xad\xb7\xae\xe63',
            '\xad\xb7\xae\xe64',
            '\xad\xb7\xae\xe65'], 10, 875, 500, 200, [
            145,
            145,
            145,
            145,
            145,
            145])
        interface.Center(self.m_Table)
        self.m_Table.SetZ(1)
        for sFont in sorted(fontdata.FONT_DATA.keys()):
            dInfo = fontdata.FONT_DATA[sFont]
            oBox = self.m_Table.AddBoxItem()
            oTxtList = []
            iColor = self.m_Table.GetNormalTextColor()
            iFontID = gamefont.CreateFont(gamefont.TYPE_LANTING, 14)
            oName = interface.CTextObject(oBox, sFont, iFontID, iColor)
            oTxtList.append(oName)
            for iStyle in range(1, 6):
                iOrgStyle = iStyle
                iIdx = iStyle
                if iStyle not in dInfo:
                    iStyle = 0
                
                if iStyle not in dInfo:
                    if iOrgStyle == 4:
                        iStyle = 3
                    
                    if iOrgStyle == 5:
                        if iStyle not in dInfo:
                            iStyle = 4
                        
                        if iStyle not in dInfo:
                            iStyle = 3
                        
                    
                
                dFontInfo = dInfo[iStyle]
                w = self.m_Table.GetItemWidth(iIdx)
                h = self.m_Table.m_ItemHeight
                oText = CTextBox(oBox, dFontInfo, iColor, w, h, iIdx)
                oTxtList.append(oText)
            
            self.m_Table.AddItemExtend(oBox, oTxtList, bChangeColor = False)
        
        self.m_Table.ResetItems()
        self.m_Table.ResetScrollBar()

    
    def ClosePanel(self):
        global g_FontPreviewPanel
        g_FontPreviewPanel = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ClosePanel()
        



def ShowCFontOffsetPanel(bShow):
    global g_FontOffsetPanel
    if g_FontOffsetPanel is None:
        g_FontOffsetPanel = CFontOffsetPanel()
    
    g_FontOffsetPanel.SetShow(bShow)


class CFontOffsetPanel(interface.CPanel):
    
    def __init__(self):
        interface.CPanel.__init__(self, interface.DialogPanel)
        self.MessageProcess()
        self.FilterFontDta('\xc4\xf5\xabF')
        self.CreateBg()
        self.CreateCloseBtn()
        self.CreateTable()

    
    def CreateBg(self):
        (w, h) = self.GetSize()
        self.m_BG = interface.CClickBox(self, w, h, 15658734, 255, 0)
        self.m_BG.SetZ(0)

    
    def CreateCloseBtn(self):
        self.m_CloseBtn = interface.CButton(self, 'dialog/dial/close.igs', 0, 0, 1)
        self.m_CloseBtn.SetZ(1)
        interface.TopRight(self.m_CloseBtn)

    
    def ClosePanel(self):
        global g_FontOffsetPanel
        g_FontOffsetPanel = None

    
    def FilterFontDta(self, sFilter):
        import fontdata
        if not interface.IsStyle4():
            self.m_dFilterData = { }
            return None
        
        dFontsData = fontdata.FONT_DATA
        dFilterData = { }
        for sKey in sorted(dFontsData.keys()):
            dFontData = dFontsData[sKey]
            if 4 in dFontData:
                sFontId = '%s_4' % sKey
                iStyle = 4
            elif fontdata.DEFAULT_STYLE in dFontData:
                sFontId = '%s_%d' % (sKey, fontdata.DEFAULT_STYLE)
                iStyle = fontdata.DEFAULT_STYLE
            elif 3 in dFontData:
                sFontId = '%s_3' % sKey
                iStyle = 3
            else:
                (sFontId, iStyle) = (None, None)
            if sFontId is None and iStyle is None:
                continue
            
            if sFilter not in dFontData[iStyle]['sFontName']:
                continue
            
            dFilterData[sFontId] = dFontData[iStyle]
        
        self.m_dFilterData = dFilterData

    
    def CreateTable(self):
        self.m_Table = ui.CTable(self, [
            '\xa6r\xc5\xe9ID',
            '\xa6r\xc5\xe9\xa6W\xba\xd9',
            '\xbc\xcb\xa8\xd2'], 10, 875, 500, 200, [
            175,
            175,
            175])
        interface.Center(self.m_Table)
        self.m_Table.SetZ(1)
        for sFontId in sorted(self.m_dFilterData.keys()):
            data = self.m_dFilterData[sFontId]
            oBox = self.m_Table.AddBoxItem()
            oTxtList = []
            iColor = self.m_Table.GetNormalTextColor()
            iFontID = gamefont.CreateFont(gamefont.TYPE_LANTING, 14)
            oId = interface.CTextObject(oBox, sFontId, iFontID, iColor)
            oTxtList.append(oId)
            oName = interface.CTextObject(oBox, data['sFontName'], iFontID, iColor)
            oTxtList.append(oName)
            w = self.m_Table.GetItemWidth(0)
            h = self.m_Table.m_ItemHeight
            oText = CTextBox(oBox, data, iColor, w, h, 0, False)
            oTxtList.append(oText)
            self.m_Table.AddItemExtend(oBox, oTxtList, bChangeColor = False)
        
        self.m_Table.ResetItems()
        self.m_Table.ResetScrollBar()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ClosePanel()
