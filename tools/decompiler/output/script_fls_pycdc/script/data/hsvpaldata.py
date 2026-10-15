# pycdc 交叉复核产物 · script.fls entry 230
# co_filename(原始)='script/data/hsvpaldata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_230.pyc (Python 2.5)

HUE_OFFSET = 361
SAT_OFFSET = 102
VAL_OFFSET = 102
HUE_OFFSET_NEW = 10000
SAT_OFFSET_NEW = 1
VAL_OFFSET_NEW = 1
DEFAULT_PREPAL = (0, 0, 0, 0, 0, 0, 0, 0, 0)
DEFAULT_DATA = {
    'tHSV': (0, 100, 100),
    'tPreCase': None,
    'tRange': (0, 0, 360, 360),
    'tSatFix': (0, 1),
    'tValFix': (0, 1) }

def GetFixHSV(iShape, iPart, iHue, iSat, iVal):
    return GetOldFixHSV(iShape, iPart, iHue, iSat, iVal)


def GetUnFixHSV(iShape, iPart, iHue, iSat, iVal):
    if iHue >= HUE_OFFSET_NEW:
        return GetNewUnFixHsv(iShape, iPart, iHue, iSat, iVal)
    else:
        return GetOldUnFixHSV(iShape, iPart, iHue, iSat, iVal)


def GetPalParam(iShape, iPart, iHue, iSat, iVal):
    if iHue >= HUE_OFFSET_NEW:
        return GetNewPalParam(iShape, iPart, iHue, iSat, iVal)
    else:
        return GetOldPalParam(iShape, iPart, iHue, iSat, iVal)


def GetOldFixHSV(iShape, iPart, iHue, iSat, iVal):
    '''
\t\xaa\xb1\xaea\xbd\xd5\xbe\xe3\xbc\xc6\xbe\xda\xab\xe1\xa1A\xc0\xf2\xa8\xfa\xacV\xa6\xe2\xa4\xe8\xae\xd7
\t:param int iShape: \xacV\xa6\xe2\xb3y\xab\xac
\t:param int iPart: \xacV\xa6\xe2\xb3\xa1\xa6\xec
\t:param int iHue: \xbd\xd5\xbe\xe3\xaa\xba\xa6\xe2\xac\xdb\xad\xc8 0 ~ 360
\t:param int iSat: \xbd\xd5\xbe\xe3\xaa\xba\xaf\xc2\xab\xd7\xad\xc8 0 ~ 100
\t:param int iVal: \xbd\xd5\xbe\xe3\xaa\xba\xa6W\xab\xd7\xad\xc8 0 ~ 100
\t:rtype: tuple
\t'''
    if iShape not in DATA:
        dInfo = DEFAULT_DATA
    else:
        dInfo = DATA[iShape][iPart]
    dSpecialInfo = GetSpecialInfo(iShape, iPart, 'S')
    dHueSpecialInfo = GetHueSpecialInfo(iShape, iPart, iHue)
    if dHueSpecialInfo and iSat >= dHueSpecialInfo['iMin'] and iVal >= dHueSpecialInfo['iMin']:
        k = SpecialK(dSpecialInfo, dInfo, dHueSpecialInfo)
        iHueSatLen = (1 - k) * (iSat - dHueSpecialInfo['iMin'])
    else:
        k = dInfo['tSatFix'][1]
        iHueSatLen = 0
    if dSpecialInfo:
        if iSat >= dSpecialInfo['iMax']:
            iSatLen = int(k * (iSat - dSpecialInfo['iMax']) + dSpecialInfo['iMax'] + iHueSatLen)
        else:
            iSatLen = iSat + iHueSatLen
    else:
        iSatLen = int(k * iSat + iHueSatLen)
    dSpecialInfo = GetSpecialInfo(iShape, iPart, 'V')
    if dSpecialInfo:
        if iVal >= dSpecialInfo['iMax']:
            iValLen = int(dInfo['tValFix'][1] * (iVal - dSpecialInfo['iMax']) + dSpecialInfo['iMax'])
        else:
            iValLen = iVal
    else:
        iValLen = int(dInfo['tValFix'][1] * iVal)
    iHue = (iHue - dInfo['tHSV'][0]) + HUE_OFFSET
    iSat = (iSatLen + dInfo['tSatFix'][0] - dInfo['tHSV'][1]) + SAT_OFFSET
    iVal = (iValLen + dInfo['tValFix'][0] - dInfo['tHSV'][2]) + VAL_OFFSET
    return (iHue, iSat, iVal)


def SpecialK(dSpecialInfo, dInfo, dHueSpecialInfo):
    if dHueSpecialInfo:
        if dSpecialInfo:
            iMax = dSpecialInfo['iMax']
        else:
            iMax = 0
        return dInfo['tSatFix'][1] * (100 - iMax) / (dHueSpecialInfo['iMin'] - iMax)
    else:
        return dInfo['tSatFix'][1]


def SatUnFix(dSpecialInfo, dInfo, iSat, dHueSpecialInfo):
    iSat += -SAT_OFFSET + dInfo['tHSV'][1] - dInfo['tSatFix'][0]
    if dHueSpecialInfo:
        if dSpecialInfo:
            iMax = dSpecialInfo['iMax']
        else:
            iMax = 0
        iMaxSat = iMax + SpecialK(dSpecialInfo, dInfo, dHueSpecialInfo) * (dHueSpecialInfo['iMin'] - iMax)
        if iSat >= iMaxSat:
            return int(round((iSat - iMaxSat) + dHueSpecialInfo['iMin']))
        
    
    if dSpecialInfo:
        if iSat >= dSpecialInfo['iMax']:
            return int((iSat - dSpecialInfo['iMax']) / dInfo['tSatFix'][1]) + dSpecialInfo['iMax']
        else:
            return iSat
    
    return int(iSat / dInfo['tSatFix'][1])


def ValUnFix(dSpecialInfo, dInfo, iVal):
    iVal += -VAL_OFFSET + dInfo['tHSV'][2] - dInfo['tValFix'][0]
    if dSpecialInfo:
        if iVal >= dSpecialInfo['iMax']:
            return int((iVal - dSpecialInfo['iMax']) / dInfo['tValFix'][1]) + dSpecialInfo['iMax']
        else:
            return iVal
    
    return int(iVal / dInfo['tValFix'][1])


def GetOldUnFixHSV(iShape, iPart, iHue, iSat, iVal):
    if iShape not in DATA:
        dInfo = DEFAULT_DATA
    else:
        dInfo = DATA[iShape][iPart]
    iHue = iHue + dInfo['tHSV'][0] - HUE_OFFSET
    dSpecialInfo = GetSpecialInfo(iShape, iPart, 'S')
    iSat = SatUnFix(dSpecialInfo, dInfo, iSat, GetHueSpecialInfo(iShape, iPart, iHue))
    dSpecialInfo = GetSpecialInfo(iShape, iPart, 'V')
    iVal = ValUnFix(dSpecialInfo, dInfo, iVal)
    return (iHue, iSat, iVal)


def GetOldPalParam(iShape, iPart, iHue, iSat, iVal):
    '''
\t\xc0\xf2\xa8\xfa\xacV\xa6\xe2\xa4\xe8\xae\xd7
\t:param int iShape: \xacV\xa6\xe2\xb3y\xab\xac
\t:param int iPart: \xacV\xa6\xe2\xb3\xa1\xa6\xec
\t:param int iHue: \xbd\xd5\xbe\xe3\xaa\xba\xa6\xe2\xac\xdb\xad\xc8 -180 ~ 180
\t:param int iSat: \xbd\xd5\xbe\xe3\xaa\xba\xaf\xc2\xab\xd7\xad\xc8 -100 ~ 100
\t:param int iVal: \xbd\xd5\xbe\xe3\xaa\xba\xa6W\xab\xd7\xad\xc8 -100 ~ 100
\t:rtype: tuple
\t'''
    if iShape not in DATA:
        dInfo = DEFAULT_DATA
    else:
        dInfo = DATA[iShape][iPart]
    (iL1, iL2, iR1, iR2) = dInfo['tRange']
    if iHue <= 0 and iSat <= 0 or iVal <= 0:
        return None
    
    tHueSatSpecialCase = None
    tSatSpecialCase = None
    tValSpecialCase = None
    if iShape in SPECIAL_DATA and iPart in SPECIAL_DATA[iShape]:
        dSpecialInfo = SPECIAL_DATA[iShape][iPart]
        iOriVal = None
        dSatSpecial = dSpecialInfo.get('S', None)
        dValSpecial = dSpecialInfo.get('H', None)
        dHueSpecialInfo = GetHueSpecialInfo(iShape, iPart, iHue + dInfo['tHSV'][0] - HUE_OFFSET)
        if dSatSpecial or dHueSpecialInfo:
            iOriSat = SatUnFix(dSatSpecial, dInfo, iSat, dHueSpecialInfo)
            if dHueSpecialInfo:
                iOriVal = ValUnFix(dValSpecial, dInfo, iVal)
                if iOriSat >= dHueSpecialInfo['iMin'] and iOriVal >= dHueSpecialInfo['iMin']:
                    for dRange in dHueSpecialInfo['tRange']:
                        (iSatLeft, iSatRight) = dRange['tCondition']
                        if iOriSat <= iOriSat:
                            pass
                        elif iOriSat <= iSatRight:
                            tHueSatSpecialCase = dRange['tPalCase']
                            break
                            continue
                    
                
            
            if dSatSpecial and not tHueSatSpecialCase:
                if iOriSat < dSatSpecial['iMax']:
                    for dSpecialCase in dSatSpecial['tRange']:
                        (iMin, iMax) = dSpecialCase['tCondition']
                        if iOriSat <= iOriSat:
                            pass
                        elif iOriSat <= iMax:
                            tSatSpecialCase = dSpecialCase['tPalCase']
                            break
                            continue
                    
                else:
                    iSat -= dSatSpecial['iMax']
            
        
        if dValSpecial:
            if iOriVal is None:
                iOriVal = ValUnFix(dValSpecial, dInfo, iVal)
            
            if iOriVal < dValSpecial['iMax']:
                for dSpecialCase in dValSpecial['tRange']:
                    (iMin, iMax) = dSpecialCase['tCondition']
                    if iOriVal <= iOriVal:
                        pass
                    elif iOriVal <= iMax:
                        tValSpecialCase = dSpecialCase['tPalCase']
                        break
                        continue
                
            else:
                iVal -= dValSpecial['iMax']
        
    
    if tHueSatSpecialCase:
        return (tHueSatSpecialCase, (0, 0, 360, 360, 0, 0, iVal - VAL_OFFSET))
    
    if tSatSpecialCase:
        return (tSatSpecialCase, (0, 0, 360, 360, 0, 0, 0))
    
    if tValSpecialCase:
        return (tValSpecialCase, (0, 0, 360, 360, 0, iSat - SAT_OFFSET, 0))
    
    if dInfo['tPreCase']:
        return (dInfo['tPreCase'], (iL1, iL2, iR1, iR2, iHue - HUE_OFFSET, iSat - SAT_OFFSET, iVal - VAL_OFFSET))
    else:
        return (DEFAULT_PREPAL, (iL1, iL2, iR1, iR2, iHue - HUE_OFFSET, iSat - SAT_OFFSET, iVal - VAL_OFFSET))


def GetSpecialInfo(iShape, iPart, sKey):
    if iShape not in SPECIAL_DATA and iPart not in SPECIAL_DATA[iShape] or sKey not in SPECIAL_DATA[iShape][iPart]:
        return None
    
    return SPECIAL_DATA[iShape][iPart][sKey]


def GetHueSpecialInfo(iShape, iPart, iHue):
    if iShape not in SPECIAL_DATA and iPart not in SPECIAL_DATA[iShape] or 'HS' not in SPECIAL_DATA[iShape][iPart]:
        return None
    
    dHueSpecialInfo = GetSpecialInfo(iShape, iPart, 'HS')
    for dSpecial in dHueSpecialInfo:
        if iHue <= iHue:
            pass
        elif iHue <= dSpecial['tHueRange'][1]:
            return dSpecial
            continue
    


def GetNewFixHsv(iShape, iPart, iHue, iSat, iVal):
    return (iHue + HUE_OFFSET_NEW, iSat + SAT_OFFSET_NEW, iVal + VAL_OFFSET_NEW)


def GetNewUnFixHsv(iShape, iPart, iHue, iSat, iVal):
    return (iHue - HUE_OFFSET_NEW, iSat - SAT_OFFSET_NEW, iVal - VAL_OFFSET_NEW)


def GetNewPalParam(iShape, iPart, iHue, iSat, iVal):
    if iHue <= 0 and iSat <= 0 or iVal <= 0:
        return None
    
    if iShape not in DATA:
        dInfo = DEFAULT_DATA
    else:
        dInfo = DATA[iShape][iPart]
    iHue -= HUE_OFFSET_NEW
    iSat -= SAT_OFFSET_NEW
    iVal -= VAL_OFFSET_NEW
    if iShape in SPECIAL_DATA and iPart in SPECIAL_DATA[iShape]:
        iSatCutLen = 0
        dSpecialInfo = SPECIAL_DATA[iShape][iPart]
        if 'HS' in dSpecialInfo:
            for dHueSatSpecial in dSpecialInfo['HS']:
                (iMin, iMax) = dHueSatSpecial['tHueRange']
                if iHue <= iHue:
                    pass
                elif iHue <= iMax:
                    if iSat >= dHueSatSpecial['iMin'] and iVal >= dHueSatSpecial['iMin']:
                        for dRange in dHueSatSpecial['tRange']:
                            (iSatLeft, iSatRight) = dRange['tCondition']
                            if iSat <= iSat:
                                pass
                            elif iSat <= iSatRight:
                                return (dRange['tPalCase'], (0, 0, 360, 360, 0, 0, int(dInfo['tValFix'][1] * iVal) + dInfo['tValFix'][0] - dInfo['tHSV'][2]))
                                continue
                        
                    
                    iSatCutLen = dHueSatSpecial['iMin']
                    continue
            
        
        if 'S' in dSpecialInfo:
            dSatSpecial = dSpecialInfo['S']
            if iSat < dSatSpecial['iMax']:
                for dSpecialCase in dSatSpecial['tRange']:
                    (iMin, iMax) = dSpecialCase['tCondition']
                    if iSat <= iSat:
                        pass
                    elif iSat <= iMax:
                        return (dSpecialCase['tPalCase'], (0, 0, 360, 360, 0, 0, 0))
                        continue
                
            
            if iSatCutLen:
                iSat = ((iSat - dSpecialInfo['iMax']) + iSatCutLen - 100) * dInfo['tSatFix'][1] * (100 - dSpecialInfo['iMax']) / (iSatCutLen - dSpecialInfo['iMax'])
            else:
                iSat = (iSat - dSatSpecial['iMax']) * dInfo['tSatFix'][1]
        elif iSatCutLen:
            iSat = (iSat + iSatCutLen - 100) * dInfo['tSatFix'][1] * 100 / iSatCutLen
        else:
            iSat = iSat * dInfo['tSatFix'][1]
        if 'V' in dSpecialInfo:
            dValSpecial = dSpecialInfo['V']
            if iVal < dValSpecial['iMax']:
                for dSpecialCase in dValSpecial['tRange']:
                    (iMin, iMax) = dSpecialCase['tCondition']
                    if iVal <= iVal:
                        pass
                    elif iVal <= iMax:
                        return (dSpecialCase['tPalCase'], (0, 0, 360, 360, 0, int(iSat) + dInfo['tSatFix'][0] - dInfo['tHSV'][1], 0))
                        continue
                
            
            iVal = (iVal - dValSpecial['iMax']) * dInfo['tValFix'][1]
        else:
            iVal = int(dInfo['tValFix'][1] * iVal)
    
    (iL1, iL2, iR1, iR2) = dInfo['tRange']
    iHue -= dInfo['tHSV'][0]
    iSat = int(iSat) + dInfo['tSatFix'][0] - dInfo['tHSV'][1]
    iVal = int(iVal) + dInfo['tValFix'][0] - dInfo['tHSV'][2]
    if dInfo['tPreCase']:
        return (dInfo['tPreCase'], (iL1, iL2, iR1, iR2, iHue, iSat, iVal))
    else:
        return (DEFAULT_PREPAL, (iL1, iL2, iR1, iR2, iHue, iSat, iVal))

DATA = {
    111: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 272, 296, 272, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.65),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (196, 100, 100),
            'tPreCase': (255, 0, 0, 0, 255, 0, 0, 0, 255),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.9),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 0, 12, 512, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.73),
            'tValFix': (0, 0.95) } },
    112: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 204, 156, 152, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 0.93) },
        2: {
            'tHSV': (35, 100, 100),
            'tPreCase': (255, 0, 0, 0, 255, 0, 0, 0, 255),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (40, 0.5),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 240, 160, 0, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) } },
    113: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 404, 0, 448, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.65),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (125, 100, 100),
            'tPreCase': (0, 124, 24, 400, 276, 216, 0, 64, 80),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.9),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 120, 352, 0, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.5),
            'tValFix': (0, 1) } },
    121: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 144, 300, 348, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.65),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 264, 52, 172, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 108, 64, 344, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.6),
            'tValFix': (0, 1) } },
    122: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 192, 132, 292, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (80, 100, 100),
            'tPreCase': (0, 112, 0, 36, 255, 0, 0, 0, 60),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.8),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 188, 64, 268, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) } },
    131: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 28, 220, 64, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.8),
            'tValFix': (0, 0.85) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 172, 176, 136, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.6),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (150, 100, 100),
            'tPreCase': (164, 0, 0, 416, 24, 124, 212, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 1),
            'tValFix': (0, 1) } },
    132: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 120, 255, 496, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 0.85) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 180, 392, 416, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.8),
            'tValFix': (0, 0.9) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 72, 255, 84, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.5),
            'tValFix': (0, 1) } },
    211: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 240, 276, 264, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 132, 148, 120, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 0.95) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 0, 255, 156, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.6),
            'tValFix': (0, 1) } },
    212: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 240, 316, 252, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 0, 188, 132, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 132, 172, 68, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 1),
            'tValFix': (0, 1) } },
    221: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 236, 104, 192, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (60, 100, 100),
            'tPreCase': None,
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 1),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (325, 100, 100),
            'tPreCase': None,
            'tRange': (0, 0, 360, 360),
            'tSatFix': (90, 0.11),
            'tValFix': (0, 1.16) } },
    222: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 0, 60, 412, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 0.8) },
        2: {
            'tHSV': (0, 100, 100),
            'tPreCase': (224, 64, 40, 0, 232, 0, 108, 44, 44),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (75, 0.29),
            'tValFix': (0, 1.2) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 140, 0, 191, 255, 200, 0, 136, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 1),
            'tValFix': (0, 1) } },
    231: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 60, 212, 152, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 0, 0, 512, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 372, 0, 308, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) } },
    232: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 308, 255, 112, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (230, 100, 100),
            'tPreCase': None,
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 1),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 116, 176, 244, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.6),
            'tValFix': (0, 1) } },
    233: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 244, 468, 0, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 512, 284, 0, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.75),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 20, 32, 512, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.7),
            'tValFix': (0, 1) } } }
SPECIAL_DATA = {
    111: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (112, 208, 112, 268, 252, 188, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (132, 208, 112, 308, 252, 188, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (132, 216, 112, 308, 284, 188, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (144, 132, 40, 376, 48, 260, 188, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (196, 132, 16, 412, 48, 224, 84, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (220, 132, 28, 480, 48, 224, 92, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (0, 40, 232, 44, 72, 304, 0, 48, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (16, 40, 216, 72, 72, 272, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (16, 40, 244, 84, 72, 288, 0, 20, 0) }] }] } },
    112: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (244, 24, 0, 56, 244, 28, 0, 0, 88) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (248, 32, 0, 44, 232, 128, 0, 0, 8) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (248, 24, 0, 104, 228, 28, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (244, 16, 16, 40, 260, 24, 0, 0, 220) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (204, 52, 0, 16, 260, 76, 0, 0, 152) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (204, 60, 0, 20, 260, 100, 0, 0, 112) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (76, 116, 0, 88, 196, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (92, 132, 32, 116, 196, 148, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (92, 128, 100, 116, 196, 96, 0, 0, 0) }] }] } },
    113: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (204, 144, 52, 276, 264, 132, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (212, 156, 56, 320, 244, 180, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (236, 160, 52, 320, 244, 168, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (292, 192, 108, 320, 284, 308, 0, 0, 108) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (404, 172, 156, 420, 304, 304, 0, 0, 116) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (504, 224, 168, 512, 412, 260, 0, 0, 116) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (140, 100, 108, 128, 168, 252, 0, 0, 116) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (276, 76, 128, 212, 204, 252, 0, 0, 116) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (316, 132, 140, 188, 260, 396, 0, 0, 96) }] }] } },
    121: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (255, 160, 80, 372, 276, 92, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (212, 160, 108, 372, 255, 128, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (255, 160, 112, 372, 296, 120, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (28, 100, 40, 0, 212, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (40, 108, 36, 16, 224, 16, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (40, 120, 36, 16, 244, 16, 0, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (43, 50),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (0, 136, 0, 0, 220, 0, 0, 0, 104) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (40, 116, 0, 48, 200, 0, 0, 0, 64) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (64, 116, 0, 0, 232, 0, 0, 0, 52) }] }] } },
    122: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (244, 32, 0, 32, 236, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (244, 40, 0, 32, 236, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (244, 48, 0, 32, 256, 0, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (16, 132, 0, 0, 220, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (36, 132, 0, 28, 220, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (56, 124, 0, 28, 220, 0, 0, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (128, 80, 48, 92, 192, 64, 112, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (164, 80, 56, 92, 212, 64, 56, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (164, 100, 52, 144, 220, 64, 56, 0, 0) }] }] } },
    131: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (244, 0, 0, 0, 228, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (256, 0, 0, 16, 228, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (264, 12, 0, 52, 228, 0, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (52, 128, 44, 188, 148, 108, 0, 72, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (124, 128, 44, 236, 148, 108, 0, 48, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (180, 128, 44, 236, 148, 144, 0, 36, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (255, 20, 0, 496, 0, 0, 156, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (255, 32, 0, 464, 36, 0, 132, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (255, 48, 0, 464, 64, 0, 88, 0, 0) }] }] } },
    132: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (68, 160, 0, 88, 296, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (88, 160, 0, 108, 296, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (92, 184, 0, 108, 340, 0, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (192, 152, 0, 292, 304, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (216, 152, 0, 340, 304, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (216, 200, 0, 340, 368, 0, 0, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (104, 128, 0, 240, 176, 20, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (76, 180, 0, 240, 212, 80, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (104, 252, 0, 240, 296, 80, 0, 0, 0) }] }] } },
    211: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (45, 52),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (72, 264, 28, 240, 244, 56, 0, 84, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (88, 264, 28, 260, 244, 56, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (120, 268, 28, 304, 216, 56, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (45, 52),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (48, 116, 0, 72, 192, 0, 0, 40, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (68, 116, 0, 104, 188, 0, 0, 24, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (68, 116, 0, 104, 188, 0, 0, 24, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (45, 52),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (0, 136, 72, 0, 88, 512, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (44, 180, 0, 0, 156, 400, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (44, 136, 72, 0, 88, 512, 0, 0, 0) }] }] } },
    212: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (176, 132, 92, 356, 256, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (180, 190, 124, 360, 360, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (208, 204, 92, 384, 368, 0, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (72, 72, 84, 56, 168, 100, 32, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (64, 68, 116, 100, 132, 164, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (64, 68, 108, 100, 132, 164, 0, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (0, 116, 64, 40, 116, 180, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (8, 116, 64, 144, 116, 132, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (80, 116, 64, 208, 116, 132, 0, 0, 0) }] }] } },
    221: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (46, 53),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (108, 104, 60, 112, 264, 136, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (108, 120, 96, 112, 304, 108, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (140, 96, 96, 156, 268, 108, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (46, 53),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (84, 76, 132, 116, 140, 256, 0, 0, 216) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (84, 88, 104, 116, 164, 164, 0, 0, 108) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (108, 88, 104, 116, 176, 164, 0, 0, 92) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (46, 53),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (124, 100, 0, 104, 240, 48, 0, 128, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (156, 48, 48, 236, 184, 0, 52, 72, 32) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (100, 88, 48, 220, 144, 60, 0, 100, 0) }] }],
            'S': {
                'iMax': 11,
                'tRange': [
                    {
                        'tCondition': (0, 3),
                        'tPalCase': (0, 0, 256, 0, 0, 496, 0, 0, 248) },
                    {
                        'tCondition': (4, 7),
                        'tPalCase': (0, 8, 260, 0, 16, 512, 0, 0, 272) },
                    {
                        'tCondition': (8, 11),
                        'tPalCase': (0, 20, 260, 0, 36, 512, 0, 16, 260) }] },
            'V': {
                'iMax': 14,
                'tRange': [
                    {
                        'tCondition': (0, 2),
                        'tPalCase': (12, 28, 0, 28, 48, 0, 16, 28, 0) },
                    {
                        'tCondition': (3, 5),
                        'tPalCase': (0, 0, 108, 0, 0, 208, 0, 0, 112) },
                    {
                        'tCondition': (6, 8),
                        'tPalCase': (0, 0, 136, 0, 0, 272, 0, 0, 144) },
                    {
                        'tCondition': (9, 11),
                        'tPalCase': (0, 0, 180, 0, 0, 360, 0, 0, 184) },
                    {
                        'tCondition': (12, 14),
                        'tPalCase': (0, 0, 212, 0, 0, 424, 0, 0, 212) }] } } },
    222: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (60, 80, 16, 60, 144, 40, 60, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (68, 80, 28, 44, 168, 40, 72, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (76, 80, 28, 52, 168, 40, 48, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (144, 140, 56, 288, 108, 44, 0, 72, 56) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (156, 140, 56, 304, 96, 52, 0, 88, 20) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (104, 136, 124, 260, 108, 76, 0, 92, 0) }] }],
            'S': {
                'iMax': 14,
                'tRange': [
                    {
                        'tCondition': (0, 2),
                        'tPalCase': (12, 28, 220, 8, 64, 420, 0, 40, 208) },
                    {
                        'tCondition': (3, 5),
                        'tPalCase': (0, 28, 224, 0, 64, 420, 0, 40, 208) },
                    {
                        'tCondition': (6, 8),
                        'tPalCase': (0, 32, 212, 0, 64, 412, 0, 40, 200) },
                    {
                        'tCondition': (9, 11),
                        'tPalCase': (0, 32, 204, 0, 64, 400, 0, 40, 192) },
                    {
                        'tCondition': (12, 14),
                        'tPalCase': (0, 32, 196, 0, 64, 380, 0, 40, 184) }] },
            'V': {
                'iMax': 17,
                'tRange': [
                    {
                        'tCondition': (0, 2),
                        'tPalCase': (0, 32, 0, 0, 60, 0, 0, 36, 0) },
                    {
                        'tCondition': (3, 5),
                        'tPalCase': (0, 44, 0, 0, 84, 0, 0, 52, 0) },
                    {
                        'tCondition': (6, 8),
                        'tPalCase': (0, 44, 8, 0, 80, 24, 0, 48, 16) },
                    {
                        'tCondition': (9, 11),
                        'tPalCase': (0, 48, 20, 0, 84, 56, 0, 48, 36) },
                    {
                        'tCondition': (12, 14),
                        'tPalCase': (0, 48, 48, 0, 76, 120, 0, 52, 48) },
                    {
                        'tCondition': (15, 17),
                        'tPalCase': (0, 44, 72, 0, 76, 160, 0, 52, 64) }] } },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (140, 92, 60, 204, 164, 132, 0, 0, 160) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (148, 96, 36, 152, 204, 152, 0, 80, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (156, 80, 52, 180, 164, 164, 0, 0, 0) }] }] } },
    231: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (100, 76, 84, 264, 68, 124, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (100, 92, 84, 260, 88, 116, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (100, 96, 84, 212, 124, 136, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (176, 76, 0, 228, 136, 60, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (176, 108, 0, 228, 176, 60, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (116, 160, 92, 148, 212, 204, 0, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (48, 55),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (204, 128, 40, 120, 255, 100, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (184, 160, 84, 264, 204, 144, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (184, 164, 80, 264, 228, 128, 0, 0, 0) }] }] } },
    232: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (255, 144, 0, 360, 292, 0, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (255, 180, 0, 360, 324, 0, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (255, 180, 16, 360, 324, 36, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (100, 128, 84, 236, 116, 172, 240, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (0, 180, 104, 152, 152, 200, 232, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (0, 180, 116, 224, 152, 208, 208, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (49, 56),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (0, 188, 0, 8, 268, 68, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (0, 188, 72, 8, 268, 152, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (0, 188, 128, 8, 268, 200, 0, 0, 0) }] }] } },
    233: {
        1: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (46, 51),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (296, 24, 140, 396, 240, 24, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (244, 96, 148, 396, 292, 24, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (272, 84, 120, 372, 292, 24, 0, 0, 0) }] }] },
        2: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (46, 51),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (228, 132, 60, 292, 252, 148, 0, 0, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (216, 196, 48, 348, 236, 148, 0, 0, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (220, 228, 48, 384, 236, 148, 0, 0, 0) }] }] },
        3: {
            'HS': [
                {
                    'iMin': 92,
                    'tHueRange': (46, 51),
                    'tRange': [
                        {
                            'tCondition': (92, 94),
                            'tPalCase': (52, 96, 36, 108, 128, 100, 0, 52, 0) },
                        {
                            'tCondition': (95, 97),
                            'tPalCase': (100, 92, 0, 156, 128, 52, 0, 36, 0) },
                        {
                            'tCondition': (98, 100),
                            'tPalCase': (104, 96, 0, 176, 128, 52, 0, 40, 0) }] }] } } }
OLDCHARDATA = {
    111: {
        1: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 0, 208, 324, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.8),
            'tValFix': (0, 1) },
        2: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 264, 232, 240, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.65),
            'tValFix': (0, 1) },
        3: {
            'tHSV': (120, 100, 100),
            'tPreCase': (0, 0, 0, 512, 344, 512, 0, 0, 0),
            'tRange': (0, 0, 360, 360),
            'tSatFix': (0, 0.8),
            'tValFix': (0, 1) } } }
