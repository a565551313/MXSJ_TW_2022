# pycdc 交叉复核产物 · script.fls entry 3461
# co_filename(原始)='script/gamefont.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3461.pyc (Python 2.5)

import C_sys
COMPAREFUNC_EQUAL = 0
COMPAREFUNC_NOEQUAL = 1
COMPAREFUNC_LESS = 2
COMPAREFUNC_GREATER = 3
NORMAL = 0
EDGE = 1
GRAD = 2
MONO = 4
TYPE_SIMHEI = '\xb6\xc2\xc5\xe9'
TYPE_LANTING = '\xa4\xe8\xa5\xbf\xc4\xf5\xabF'
TYPE_HUAWENXINGKAI = '\xb5\xd8\xa4\xe5\xa6\xe6\xb7\xa2'
TYPE_SONGTI = '\xb2\xd3\xa9\xfa\xc5\xe9'
TYPE_KAITI_BIG5 = 'BIG5\xbc\xd0\xb7\xa2\xc5\xe9'
TYPE_KAITI = '\xb7\xa2\xc5\xe9'
TYPE_LISHU = '\xc1\xf5\xae\xd1'
FONT_DICT = {
    TYPE_LANTING: 'FZLanTingYuan-DB-GBK.ttf',
    TYPE_SIMHEI: 'simhei.ttf',
    TYPE_HUAWENXINGKAI: 'STXINGKA.TTF',
    TYPE_SONGTI: '\xb2\xd3\xa9\xfa\xc5\xe9',
    TYPE_KAITI_BIG5: 'BIG5\xbc\xd0\xb7\xa2\xc5\xe9',
    TYPE_KAITI: '\xb7\xa2\xc5\xe9',
    TYPE_LISHU: 'SIMLI.TTF' }
LINK_FONT_INFO = { }
FONTFROMFILE = [
    TYPE_LANTING,
    TYPE_HUAWENXINGKAI,
    TYPE_SIMHEI,
    TYPE_LISHU]
g_FontDict = { }
g_DefaultFontName = ''
g_FontSize = { }

def CreateFont(sFontName, iFontSize, iWeight = 400, bEdge = False, iEdgeRadius = 1, bGrad = False, bMono = False, iOffsetY = 0):
    '''
\t\xb3\xd0\xab\xd8\xa6r\xc5\xe9
\t:param sFontN;7?`z\xfcr\xc5\xe9\xa6W\xba\xd9
\t:param iFontSize: \xa6r\xb8\xb9
\t:param iWeight: \xb2\xca\xab\xd7
\t:param bEdge: \xacO\xa7_\xa5]\xc3\xe4
\t:param iEdgeRadius: \xa5]\xc3\xe4\xa5b\xae|
\t:param bGrad: \xacO\xa7_\xba\xa5\xc5\xdc
\t:param bMono: \xacO\xa7_\xa6\xec\xb4\xe8\xacV
\t:param iOffsetY: y\xb6b\xb0\xbe\xb2\xbe
\t:return: \xa6r\xc5\xe9ID
\t'''
    iFontID = CreateOneFont(sFontName, iFontSize, iWeight, bEdge, iEdgeRadius, bGrad, bMono, iOffsetY)
    if sFontName in LINK_FONT_INFO:
        dLinkInfo = LINK_FONT_INFO[sFontName]
        if hasattr(C_sys, 'SetLinkFontID') and hasattr(C_sys, 'AddLinkFontUseCondition'):
            if dLinkInfo:
                iLinkFont = CreateOneFont(dLinkInfo['sLinkFontName'], iFontSize, iWeight, bEdge, iEdgeRadius, bGrad, bMono, iOffsetY)
                C_sys.SetLinkFontID(iFontID, iLinkFont)
                for iCompareFunc, iCompareVal in dLinkInfo['tCompare']:
                    C_sys.AddLinkFontUseCondition(iFontID, iCompareFunc, iCompareVal)
                
            else:
                C_sys.SetLinkFontID(iFontID, 0)
        
    
    return iFontID


def CreateOneFont(sFontName, iFontSize, iWeight = 400, bEdge = False, iEdgeRadius = 1, bGrad = False, bMono = False, iOffsetY = 0):
    tKey = (sFontName, iFontSize, iWeight, bEdge, iEdgeRadius, bGrad, bMono, iOffsetY)
    if tKey in g_FontDict:
        return g_FontDict[tKey]
    else:
        iType = NORMAL
        if bEdge:
            iType |= EDGE
        
        if bGrad:
            iType |= GRAD
        
        if bMono:
            iType |= MONO
        
        import interface
        import misc
        if misc.IsTWServer() and interface.GCODE == interface.BIG5:
            if sFontName not in (TYPE_LANTING, TYPE_LISHU):
                sFontName = TYPE_KAITI_BIG5
            
        elif [
            None,
            None,
            None,
            None,
            None,
            sFontName,
            FONT_DICT]:
            sFontName = TYPE_SONGTI
        
        sFontFileName = FONT_DICT[sFontName]
        if sFontName in FONTFROMFILE:
            iFontIdx = 0
            iDPI = 72
            if iWeight == 400:
                iStrength = 1
            elif iWeight == 600:
                iStrength = 32
            elif iWeight == 800:
                iStrength = 64
            else:
                iStrength = 1
            iFontID = C_sys.CreateFontFromFile(sFontFileName, iFontIdx, iFontSize, iDPI, iStrength, iType, iEdgeRadius, iOffsetY)
        else:
            iFontID = C_sys.CreateFont(sFontFileName, iFontSize, iWeight, iType)
        g_FontDict[tKey] = iFontID
        UpdataFontSize(iFontID)
        return iFontID


def InitDefaultFontName(iStyleIdx):
    '''
\t\xaa\xec\xa9l\xa4\xc6\xc0q\xbb{\xa6r\xc5\xe9\xa4\xe5\xa5\xf3\xa6W\xba\xd9
\t:param iStyleIdx: \xad\xb7\xae\xe6\xaf\xc1\xa4\xde
\t'''
    global g_DefaultFontName, g_DefaultFontName, g_DefaultFontName, g_DefaultFontName
    if iStyleIdx == 0:
        g_DefaultFontName = TYPE_SONGTI
    elif iStyleIdx == 1:
        g_DefaultFontName = TYPE_SONGTI
    else:
        g_DefaultFontName = TYPE_LANTING
    import interface
    import misc
    if misc.IsTWServer() and interface.GCODE == interface.BIG5:
        g_DefaultFontName = TYPE_KAITI_BIG5
    


def GetDefaultFontName():
    return g_DefaultFontName


def GetFontSize(iFontID):
    '''
\t\xc0\xf2\xa8\xfa\xa6r\xc5\xe9ID\xa5\xcd\xa6\xa8\xaa\xba\xa6r\xc5\xe9\xa4j\xa4p
\t:param iFontID: \xa6r\xc5\xe9ID
\t:return: iSize
\t'''
    return g_FontSize.get(iFontID, 14)


def UpdataFontSize(iFontID):
    import interface
    iSize = interface.CTextObject(None, '\xb0\xea', iFontID, 0, 0).GetSize()[0]
    g_FontSize[iFontID] = iSize
    interface.UpdateFontSize(iFontID, iSize)


def ClearFontInof():
    global g_FontDict, g_DefaultFontName, g_FontSize
    g_FontDict = { }
    g_DefaultFontName = ''
    g_FontSize = { }
