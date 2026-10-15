# pycdc 交叉复核产物 · script.fls entry 3256
# co_filename(原始)='script/mxui/itboxwidget.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3256.pyc (Python 2.5)

import interface
import framewidget
import imagewidget
TYPE2PATH = {
    0: {
        'iType': 0,
        'sPath': None,
        'tItBgOffset': (0, 0),
        'tTitleOffset': (60, 10),
        'iDescSpace': 4,
        'tImgOffset': (5, 5),
        'sTitleFontType': 'FontLT14_3',
        'sTitleColorType': 'COLOR_1',
        'sTitleSelectColorType': 'COLOR_72',
        'sDescFontType': 'FontLT14_3',
        'sDescColorType': 'COLOR_1',
        'sDescSelectColorType': 'COLOR_72' },
    1: {
        'iType': 0,
        'sPath': None,
        'tItBgOffset': (0, 0),
        'tTitleOffset': (60, 10),
        'iDescSpace': 4,
        'tImgOffset': (5, 5),
        'sTitleFontType': 'FontLT14_3',
        'sTitleColorType': 'COLOR_1',
        'sTitleSelectColorType': 'COLOR_72',
        'sDescFontType': 'FontLT14_3',
        'sDescColorType': 'COLOR_1',
        'sDescSelectColorType': 'COLOR_72' },
    2: {
        'iType': 1,
        'sPath': 'combdialog3/\xce\xef\xc6\xb7\xb7\xd6\xc0\xe0\xb8\xf1/',
        'tItBgOffset': (5, 0),
        'tTitleOffset': (5, 4),
        'iDescSpace': 4,
        'tImgOffset': (0, 0),
        'sTitleFontType': 'FontLT14_3',
        'sTitleColorType': 'COLOR_1',
        'sTitleSelectColorType': 'COLOR_72',
        'sDescFontType': 'FontLT14_3',
        'sDescColorType': 'COLOR_1',
        'sDescSelectColorType': 'COLOR_72' },
    3: {
        'iType': 1,
        'sPath': 'combdialog4/\xce\xef\xc6\xb7\xb7\xd6\xc0\xe0\xb8\xf1/',
        'tItBgOffset': (5, 0),
        'tTitleOffset': (5, 4),
        'iDescSpace': 4,
        'tImgOffset': (0, 0),
        'sTitleFontType': 'FontLT14_3',
        'sTitleColorType': 'COLOR_1',
        'sTitleSelectColorType': 'COLOR_72',
        'sDescFontType': 'FontLT14_3',
        'sDescColorType': 'COLOR_1',
        'sDescSelectColorType': 'COLOR_72' } }

class CItBox(interface.CBoxObject, interface.CBase):
    
    def __init__(	, oParent, sFilePath, w = 0, h = 0, iMsgID = 0):
        '''
\t\t\xaa\xab\xab~\xae\xe6\xb1\xb1\xa5\xf3
\t\t:param oParent: \xa4\xf7\xb8`\xc2I
\t\t:param sFilePath: \xb8\xea\xb7\xbd\xb8\xf4\xae|
\t\t:param w: \xbce(\xa4@\xc5\xe9\xc3\xfe\xab\xac\xa4\xa3\xbb\xdd\xadn\xb6\xc7)
\t\t:param h: \xb0\xaa(\xa4@\xc5\xe9\xc3\xfe\xab\xac\xa4\xa3\xbb\xdd\xadn\xb6\xc7)
\t\t'''
        interface.CBoxObject.__init__(	, oParent, w, h, 0, 0)
        	.MessageProcess()
        	.m_ConfigInfo = TYPE2PATH.get(interface.GetStyle())
        	.m_FilePath = sFilePath
        	.m_Type = 	.m_ConfigInfo['iType']
        	.m_Width = w
        	.m_Height = h
        	.m_MsgID = iMsgID
        	.m_BgFrame = None
        	.m_Figure = None
        	.m_ItemBg = None
        	.m_ItemImg = None
        	.m_OldFrame = 0
        	.m_DescColor = [
            None,
            None]
        	.m_TitleColor = [
            None,
            None]
        	.m_Selected = False
        	.m_Title = None
        	.m_Desc = None
        	.CreateBg(0)

    
    def SetTitle(	, sTxt, iFontID = None, iNormalColor = None, iSelectColor = None):
        if iFontID is None:
            sFontType = 	.m_ConfigInfo['sTitleFontType']
            iFontID = getattr(interface, sFontType, None)
            if iFontID is None:
                return None
            
        
        if iNormalColor is None:
            sColorType = 	.m_ConfigInfo['sTitleColorType']
            iNormalColor = getattr(interface, sColorType, None)
            if iNormalColor is None:
                return None
            
        
        if iSelectColor is None:
            sColorType = 	.m_ConfigInfo['sTitleSelectColorType']
            iSelectColor = getattr(interface, sColorType, None)
            if iSelectColor is None:
                return None
            
        
        	.m_TitleColor = [
            iNormalColor,
            iSelectColor]
        (x, y) = 	.GetTitlePos()
        	.m_Title = interface.CTextObject(	, sTxt, iFontID, iNormalColor, 0)
        	.m_Title.SetZ(1)
        	.m_Title.SetPos(x, y)

    
    def SetTitleObj(	, oTitle):
        	.m_Title = oTitle
        if oTitle is None:
            return None
        
        	.m_Title.SetZ(1)
        (x, y) = 	.GetTitlePos()
        	.m_Title.SetPos(x, y)

    
    def SetTitleColor(	, iNormalColor = None, iSelectColor = None):
        if iNormalColor is not None:
            	.m_TitleColor[0] = iNormalColor
        
        if iSelectColor is not None:
            	.m_TitleColor[1] = iSelectColor
        

    
    def SetDesc(	, sDesc, iFontID = None, iNormalColor = None, iSelectColor = None):
        if iFontID is None:
            sFontType = 	.m_ConfigInfo['sDescFontType']
            iFontID = getattr(interface, sFontType, None)
            if iFontID is None:
                return None
            
        
        if iNormalColor is None:
            sColorType = 	.m_ConfigInfo['sDescColorType']
            iNormalColor = getattr(interface, sColorType, None)
            if iNormalColor is None:
                return None
            
        
        if iSelectColor is None:
            sColorType = 	.m_ConfigInfo['sDescSelectColorType']
            iSelectColor = getattr(interface, sColorType, None)
            if iNormalColor is None:
                return None
            
        
        	.m_DescColor = [
            iNormalColor,
            iSelectColor]
        (x, y) = 	.GetDescPos()
        	.m_Desc = interface.CTextObject(	, sDesc, iFontID, iNormalColor, 0)
        	.m_Desc.SetZ(1)
        	.m_Desc.SetPos(x, y)

    
    def SetDescObj(	, oDesc):
        	.m_Desc = oDesc
        if oDesc is None:
            return None
        
        	.m_Desc.SetZ(1)
        (x, y) = 	.GetDescPos()
        	.m_Desc.SetPos(x, y)

    
    def SetDescColor(	, iNormalColor = None, iSelectColor = None):
        if iNormalColor is not None:
            	.m_DescColor[0] = iNormalColor
        
        if iSelectColor is not None:
            	.m_DescColor[1] = iSelectColor
        

    
    def SetItemImg(	, sPath, sPack, iMode = 0):
        tImgOffset = 	.m_ConfigInfo['tImgOffset']
        	.m_ItemImg = imagewidget.CImage(	, sPath, sPack)
        if 	.m_ItemBg:
            if iMode == 0:
                (iImgW, iImgH) = 	.m_ItemImg.GetSize()
                (iBgW, iBgH) = 	.m_ItemBg.GetSize()
                (iBgX, iBgY) = 	.m_ItemBg.GetPos()
                (x, y) = interface.GetAlignXY(iImgW, iImgH, iBgW, iBgH, interface.ALIGN_CENTER_MIDDLE)
                x += iBgX
                y += iBgY
            elif iMode == 1:
                (x, y) = 	.m_ItemBg.GetPos()
            
        else:
            (x, y) = tImgOffset
        	.m_ItemImg.SetPos(x, y)
        	.m_ItemImg.SetZ(2)

    
    def SetItemImgObj(	, oImg, iMode = 0):
        	.m_ItemImg = oImg
        if oImg is None:
            return None
        
        tImgOffset = 	.m_ConfigInfo['tImgOffset']
        if 	.m_ItemBg:
            if iMode == 0:
                (iImgW, iImgH) = 	.m_ItemImg.GetSize()
                (iBgW, iBgH) = 	.m_ItemBg.GetSize()
                (iBgX, iBgY) = 	.m_ItemBg.GetPos()
                (x, y) = interface.GetAlignXY(iImgW, iImgH, iBgW, iBgH, interface.ALIGN_CENTER_MIDDLE)
                x += iBgX
                y += iBgY
            elif iMode == 1:
                (x, y) = 	.m_ItemBg.GetPos()
            
        else:
            (x, y) = tImgOffset
        	.m_ItemImg.SetPos(x, y)
        	.m_ItemImg.SetZ(2)

    
    def GetSize(	):
        return (	.m_Width, 	.m_Height)

    
    def SetSelect(	, b):
        if b:
            	.SetFrame(1)
        else:
            	.SetFrame(0)
        	.ChangeTextColor(b)
        	.m_Selected = b

    
    def GetSelect(	):
        return 	.m_Selected

    
    def SetFrame(	, iFrame):
        if 	.m_OldFrame == iFrame:
            return None
        
        	.m_OldFrame = iFrame
        	.CreateBg(iFrame)

    
    def GetMsgID(	):
        return 	.m_MsgID

    
    def CreateBg(	, iFrame):
        import style
        if 	.m_Type == 0:
            if not 	.m_BgFrame:
                	.m_BgFrame = imagewidget.CImage(	, 	.m_FilePath, interface.UIPath)
                (	.m_Width, 	.m_Height) = 	.m_BgFrame.GetSize()
            
            	.m_BgFrame.SetFrame(iFrame)
        else:
            dTypeInfo = 	.m_ConfigInfo
            sPath = style.GetPath(dTypeInfo['sPath'])
            sBgPath = '%s%d/' % (sPath, iFrame)
            	.m_BgFrame = framewidget.CFrame(	, 	.m_Width, 	.m_Height, sBgPath)
            
            try:
                sFigurePath = '%s\xbb\xa8\xce\xc6/%d.png' % (sPath, iFrame % 2)
                	.m_Figure = imagewidget.CImage(	.m_BgFrame, sFigurePath, interface.UIPath)
                	.m_Figure.SetZ(1)
                interface.CenterRight(	.m_Figure)
            except:
                pass

            	.m_ItemBg = imagewidget.CImage(	.m_BgFrame, 	.m_FilePath, interface.UIPath)
            	.m_ItemBg.SetZ(1)
            (iOffsetX, iOffsetY) = dTypeInfo['tItBgOffset']
            interface.CenterLeft(	.m_ItemBg, iOffsetX, iOffsetY)
        	.SetSize(	.m_Width, 	.m_Height)

    
    def Enter(	):
        if 	.m_Selected:
            	.SetFrame(1)
        else:
            	.SetFrame(2)

    
    def Leave(	):
        if 	.m_Selected:
            	.SetFrame(1)
        else:
            	.SetFrame(0)

    
    def LeftDown(	):
        pass

    
    def LeftUp(	):
        if 	.GetSelect():
            	.SetSelect(False)
        else:
            	.SetSelect(True)
        if not 	.m_MsgID:
            return None
        
        oParent = 	.GetParent()
        if hasattr(oParent, 'OnMessage'):
            oParent.OnMessage(	.m_MsgID)
        

    
    def RightUp(	):
        if not 	.m_MsgID:
            return None
        
        oParent = 	.GetParent()
        if hasattr(oParent, 'OnMessage'):
            oParent.OnMessage(	.m_MsgID + interface.RIGHT_BUTTON_MESSAGE)
        

    
    def GetTitlePos(	):
        (iOffsetX, iOffsetY) = 	.m_ConfigInfo['tTitleOffset']
        if 	.m_ItemBg:
            (x, y) = 	.m_ItemBg.GetPos()
            (w, h) = 	.m_ItemBg.GetSize()
            iOffsetX = iOffsetX + x + w
            iOffsetY = iOffsetY + y
        
        return (iOffsetX, iOffsetY)

    
    def GetDescPos(	):
        (iOffsetX, iOffsetY) = 	.GetTitlePos()
        iSpace = 	.m_ConfigInfo['iDescSpace']
        if 	.m_Title:
            (_, iTitleH) = 	.m_Title.GetSize()
            iOffsetY = iOffsetY + iTitleH + iSpace
        
        return (iOffsetX, iOffsetY)

    
    def ChangeTextColor(	, bSelect):
        iIdx = None if bSelect else 0
        if 	.m_Title:
            iColor = 	.m_TitleColor[iIdx]
            if iColor and hasattr(	.m_Title, 'SetColor'):
                	.m_Title.SetColor(iColor)
            
        
        if 	.m_Desc:
            iColor = 	.m_DescColor[iIdx]
            if iColor and hasattr(	.m_Desc, 'SetColor'):
                	.m_Desc.SetColor(iColor)
            
        


g_Test = None

def Test(sFilePath, w = 0, h = 0, iType = 0, sTitle = '', sDesc = ''):
    global g_Test
    g_Test = CItBox(interface.DialogPanel, sFilePath, w = w, h = h, iType = iType)
    g_Test.SetTitle(sTitle)
    g_Test.SetDesc(sDesc)
    g_Test.SetPos(50, 50)
    g_Test.SetZ(100000)
