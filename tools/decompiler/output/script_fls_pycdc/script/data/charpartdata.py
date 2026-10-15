# pycdc 交叉复核产物 · script.fls entry 3935
# co_filename(原始)='script/data/charpartdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3935.pyc (Python 2.5)

import permission

def GetTestData(sAttr, oValue):
    '''
\t\xa6p\xaaG\xa6b\xb4\xfa\xb8\xd5\xbc\xd2\xa6\xa1\xa4U\xa1A\xc0\xf2\xa8\xfanew_name\xaa\xba\xbc\xc6\xbe\xda
\t:param sAttr:
\t:param oValue:
\t:return:
\t'''
    if permission.IsUseNewChar():
        oModel = __import__('new_%s' % __name__)
        if not oModel:
            return oValue
        
        oTestValue = getattr(oModel, sAttr, None)
        if oTestValue is None:
            return oValue
        else:
            return oTestValue
    else:
        return oValue


def GetNpcData():
    return GetTestData('NPC_DATA', NPC_DATA)


def GetHorseData():
    return GetTestData('HORSE_DATA', HORSE_DATA)


def GetFairyData():
    return GetTestData('FAIRY_DATA', FAIRY_DATA)


def GetAuraData():
    return GetTestData('AURA_DATA', AURA_DATA)


def GetTrackData():
    return GetTestData('TRACK_DATA', TRACK_DATA)


def GetHorsePosData():
    return GetTestData('HORSE_POS_DATA', HORSE_POS_DATA)


def GetNpcComponent(iShape):
    '''
\t\xc0\xf2\xa8\xfaNPC\xa9\xce\xa5l\xb3\xea\xc3~\xaa\xba\xa5\xb2\xadn\xb2\xd5\xa5\xf3
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('lComponent', [])[:]


def GetNpcAccessories(iShape):
    '''
\t\xc0\xf2\xa8\xfaNPC\xa9\xce\xa5l\xb3\xea\xc3~\xaa\xba\xb8\xcb\xb9\xa2
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('lAccessories', [])[:]


def GetNpcProAccPart(iShape):
    '''
\t\xc0\xf2\xa8\xfaNPC\xa9\xce\xa5l\xb3\xea\xc3~\xaa\xba\xb8\xcb\xb9\xa2\xb8j\xa9w\xacV\xa6\xe2
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('lProAccPart', [])[:]


def GetNpcShadow(iShape):
    '''
\t\xacO\xa7_\xa7t\xa6\xb3\xb7s\xaa\xba\xb3\xb1\xbcv
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('iShadow', 0)


def GetNpcSpeStand(iShape):
    '''
\t\xacO\xa7_\xa7t\xa6\xb3\xb7s\xaa\xba\xafS\xae\xed\xb0\xca\xa7@
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('iSpeStand', 0)


def GetNpcBlink(iShape):
    '''
\t\xacO\xa7_\xa7t\xa6\xb3\xafw\xb2\xb4
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('iBlink', 0)


def GetNpcProPart(iShape):
    '''
\t\xacO\xa7_\xa7t\xa6\xb3\xafw\xb2\xb4
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('lProPart', [])


def GetNpcHigh(iShape):
    '''
\t\xacO\xa7_\xa7t\xa6\xb3\xafw\xb2\xb4
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('iResHigh', None)


def GetNpcChangeZ(iShape):
    '''
\t\xc0\xf2\xa8\xfaNPC\xa9\xce\xa5l\xb3\xea\xc3~\xaa\xba\xb8\xcb\xb9\xa2
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetNpcData().get(iShape, { }).get('iChangeZ', 0)


def GetHorseComponent(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa7\xa4\xc3M\xaa\xba\xa5\xb2\xadn\xb2\xd5\xa5\xf3
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('lComponent', [])[:]


def GetHorseAccessories(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa7\xa4\xc3M\xaa\xba\xb8\xcb\xb9\xa2
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('lAccessories', [])[:]


def GetRiderPartPos(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa4H\xaa\xab\xb9\xef\xa9\xf3\xa7\xa4\xc3M\xaa\xba\xb4\xe8\xacV\xbch\xaf\xc5
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('lHeroPos', [])[:]


def GetRiderType(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa7\xa4\xc3M\xaa\xba\xaa\xed\xb2{\xc3\xfe\xa7O
\t\xaa\xf0\xa6^
\t1 -> \xafB\xb0\xca\xc3M\xa6\xe6\xa7\xa4\xc3M
\t2 -> \xa5\xad\xc3\xad\xc3M\xa6\xe6\xa7\xa4\xc3M
\t3 -> \xad\xb8\xa6\xe6\xa7\xa4\xc3M
\t4 -> \xad\xb8\xba\xd0\xa7\xa4\xc3M
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('iType', 1)


def GetRiderMulType(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa7\xa4\xc3M\xaa\xba\xa6h\xa4H\xc4\xdd\xa9\xca\xc3\xfe\xa7O
\t\xaa\xf0\xa6^
\t1 -> \xb3\xe6\xa6\xec\xb8m\xa7\xa4\xc3M
\t2 -> \xc2\xf9\xa6\xec\xb8m\xa7\xa4\xc3M
\t3 -> \xa4T\xa6\xec\xb8m\xa7\xa4\xc3M \xa4\xad\xa4H\xa7\xa4\xc3M
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('iMulType', 1)


def GetRiderHigh(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa7\xa4\xc3M\xaa\xba\xb0\xaa\xab\xd7
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('iRiderHigh', 0)


def GetFemaleType(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa4k\xa9\xca\xa8\xa4\xa6\xe2\xaa\xba\xafS\xae\xed\xaa\xac\xbaA \xa5\xce\xa8\xd3\xbc\xd0\xbbx\xacO\xa7_\xa8\xcf\xa5\xce\xb8\xf3\xbbL\xb8\xea\xb7\xbd
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('iFemaleType', 0)


def GetAccessoriesPart(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa6@\xa5\xce\xbch\xaf\xc5
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('lAccessoriesPart', { })


def GetHorseCvrInfo(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xa6@\xa5\xce\xbch\xaf\xc5
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('dCvrInfo', { })


def GetPalBindList(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xb8j\xa9w\xb2\xd5\xa5\xf3
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('lPalBind', [])[:]


def GetAccPalBindList(iShape):
    '''
\t\xc0\xf2\xa8\xfa\xb8\xcb\xb9\xa2\xb8j\xa9w\xb2\xd5\xa5\xf3
\t:param int iShape: \xa7\xa4\xc3MID
\t'''
    return GetHorseData().get(iShape, { }).get('lPalAccBind', [])[:]


def GetIsOnlyNewNpc(iShape):
    '''
\t\xacO\xa7_\xb1j\xa8\xee\xc5\xe3\xa5\xdc\xb7s\xaa\xba\xb3y\xab\xac
\t:param int iShape: \xb3y\xab\xac\xbds\xb8\xb9
\t'''
    return GetNpcData().get(iShape, { }).get('iOnlyNew', 0)


def GetIsOnlyNewFairy(iShape):
    '''
\t\xacO\xa7_\xb1j\xa8\xee\xc5\xe3\xa5\xdc\xb7s\xaa\xba\xb3y\xab\xac
\t:param int iShape: \xb3y\xab\xac\xbds\xb8\xb9
\t'''
    return GetFairyData().get(iShape, { }).get('iOnlyNew', 0)


def GetHorseRiderOffset(iHorseID, iPos, iDir):
    '''
\t\xc0\xf2\xa8\xfa\xc3M\xa4\xe2\xb0\xbe\xb2\xbe\xa6\xec\xb8m
\t:param iHorseID: \xa7\xa4\xc3Mid
\t:param iPos: \xa7\xa4\xc3M\xa6\xec\xb8m
\t:param iDir: \xa4\xe8\xa6V
\t'''
    dHorsePosData = GetHorsePosData()
    if iHorseID not in dHorsePosData:
        return (0, 0)
    
    if iPos not in dHorsePosData[iHorseID]:
        return (0, 0)
    
    if iDir not in dHorsePosData[iHorseID][iPos]:
        return (0, 0)
    
    return dHorsePosData[iHorseID][iPos][iDir]


def GetHorseShadow(iShape):
    '''
\t\xacO\xa7_\xa7t\xa6\xb3\xb7s\xaa\xba\xb3\xb1\xbcv
\t:param int iShape: \xb3y\xab\xacID
\t'''
    return GetHorseData().get(iShape, { }).get('iShadow', 0)


def GetIsOnlyNewAura(iShape):
    '''
\t\xacO\xa7_\xb1j\xa8\xee\xc5\xe3\xa5\xdc\xb7s\xaa\xba\xb3y\xab\xac
\t:param int iShape: \xb3y\xab\xac\xbds\xb8\xb9
\t'''
    return GetAuraData().get(iShape, { }).get('iOnlyNew', 0)


def GetIsOnlyNewTrack(iShape):
    '''
\t\xacO\xa7_\xb1j\xa8\xee\xc5\xe3\xa5\xdc\xb7s\xaa\xba\xb3y\xab\xac
\t:param int iShape: \xb3y\xab\xac\xbds\xb8\xb9
\t'''
    return GetTrackData().get(iShape, { }).get('iOnlyNew', 0)


def GetSpeWingColorChange(iWing, sState, iClientType, iColor):
    dInfo = SPE_WING_PAL_DATA.get(iWing, { }).get(iColor, { })
    if not dInfo or not (dInfo.get('iClientType', 3) & iClientType):
        return (sState, [
            iColor])
    else:
        sRes = dInfo.get('sRes', '')
        tColor = dInfo.get('tColor', [
            0])
        return (sRes.replace('[state]', sState), tColor)

NPC_DATA = {
    0: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            2],
        'lComponent': [
            1],
        'lProAccPart': [
            2],
        'lProPart': [
            1],
        'sName': '\xa4\xf2\xaf\xf3\xb9\xce' },
    2010: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            2],
        'lComponent': [
            1],
        'lProAccPart': [
            2],
        'lProPart': [
            1],
        'sName': '\xa4\xf2\xaf\xf3\xb9\xce' },
    2020: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3)],
        'sName': '\xa4p\xafQ\xc0t' },
    2030: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4p\xbbe\xb8\xc1' },
    2040: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            2],
        'lComponent': [
            1],
        'lProAccPart': [
            2],
        'lProPart': [
            1],
        'sName': '\xa4p\xa8\xdf\xa4l' },
    2050: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3)],
        'sName': '\xa8\xeb\xe7\xb3' },
    2060: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4s\xbd\xde' },
    2070: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2],
        'lProAccPart': [
            1],
        'lProPart': [
            2],
        'sName': '\xaa\xf7\xaa\xe1\xb9\xab' },
    2080: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': 100,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4],
        'lProAccPart': [
            1],
        'lProPart': [
            0,
            (2, 3),
            4],
        'sName': '\xae\xe7\xaa\xe1\xa5P\xa4l' },
    2081: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': 100,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xabC\xb5\xec\xa9\xc7' },
    2090: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3)],
        'sName': '\xb3D' },
    2100: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb1j\xb5s' },
    2110: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            0,
            2,
            (1, 3)],
        'sName': '\xad\xb8\xb8\xe9' },
    2130: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4],
        'lProAccPart': [
            1],
        'lProPart': [
            (2, 3)],
        'sName': '\xafT' },
    2140: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            2],
        'lComponent': [
            1,
            4],
        'lProAccPart': [
            2],
        'lProPart': [
            1],
        'sName': '\xb0\xad\xa4\xf5' },
    2150: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            0,
            (1, 2, 3)],
        'sName': '\xa4h\xa7L' },
    2160: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 3),
            2],
        'sName': '\xa4p\xbf\xdf\xa4k' },
    2170: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3)],
        'sName': '\xa4j\xbf\xc0\xc3\xc9' },
    2180: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5],
        'lProPart': [
            0,
            2,
            (1, 3)],
        'sName': '\xb3\xbd\xac\xfc\xa4H' },
    2190: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            (2, 5),
            3],
        'sName': '\xa8\xdf\xbe\xd4\xa4h' },
    2200: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            3,
            5],
        'sName': '\xa8\xdf\xb2\xbd\xaa\xc1' },
    2260: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4],
        'lProAccPart': [
            1],
        'lProPart': [
            2,
            3,
            4],
        'sName': '\xa4p\xc5]\xc0Y' },
    2270: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3)],
        'sName': '\xbeu\xc5\\' },
    2300: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2],
        'lProAccPart': [
            1],
        'lProPart': [
            2],
        'sName': '\xa4j\xaf\xf3\xb9\xce' },
    2350: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            0,
            (2, 3),
            5],
        'sName': '\xa8\xdf\xabi\xa4h' },
    2360: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            0,
            3,
            (2, 5)],
        'sName': '\xa8\xdf\xa4\xd1\xa8\xcf' },
    2380: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            3],
        'lComponent': [
            1,
            2],
        'lProAccPart': [
            3],
        'lProPart': [
            (0, 1, 2)],
        'sName': '\xafP\xa4\xf5\xb3\xbe' },
    2390: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            3],
        'lComponent': [
            1,
            2],
        'lProAccPart': [
            3],
        'lProPart': [
            2,
            (0, 1)],
        'sName': '\xc5]\xe7\xb2' },
    2400: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            (2, 3, 5)],
        'sName': '\xa5\xa8\xc1\xaf' },
    2420: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4],
        'lProAccPart': [
            1],
        'lProPart': [
            (2, 3)],
        'sName': '\xc1l\xaa\xea' },
    2430: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            (2, 3)],
        'sName': '\xc5]\xbbj\xb5\xef' },
    2440: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            2,
            3,
            5],
        'sName': '\xa6\xba\xa4`\xc3M\xa4h' },
    2450: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            2,
            3,
            5],
        'sName': '\xc5I\xa4M\xedL\xab\xcd' },
    2460: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xabC\xb5\xec\xabL\xab\xc8' },
    2470: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xaf\xab\xa7L' },
    2480: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xaf\xab\xa8\xcf' },
    2490: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3)],
        'sName': '\xbcv\xafT' },
    2500: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2)],
        'lComponent': [
            3,
            4,
            5,
            6],
        'lProAccPart': [
            (1, 2)],
        'lProPart': [
            3,
            4,
            5],
        'sName': '\xafT\xabi\xa4h' },
    2510: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 3),
            2],
        'sName': '\xa5\xd5\xc0s' },
    2540: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            2,
            3,
            4],
        'sName': '\xaa\xea\xc0Y\xa9\xc7' },
    2550: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4,
            6],
        'lProAccPart': [
            5],
        'lProPart': [
            (1, 2, 3, 6)],
        'sName': '\xb3\xb7\xbb\xf1\xb0\xc4' },
    2570: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            1],
        'lProPart': [
            2,
            3,
            5],
        'sName': '\xa4\xf4\xb4\xb9\xa4k\xa7\xaf' },
    2580: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            6,
            7,
            5],
        'sName': '\xa4\xec\xa4D\xa5\xec' },
    2590: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            6,
            7],
        'sName': '\xa8\xdf\xaf\xab\xa9x' },
    2600: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            3,
            2],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            3,
            2],
        'lProPart': [
            4,
            6,
            5],
        'sName': '\xa4`\xc6F\xabi\xa4h' },
    2610: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            (0, 6),
            7],
        'sName': '\xa4\xfb\xc5]\xb7\xfe\xadx' },
    2630: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            4,
            5,
            6],
        'sName': '\xaa\xb0\xac\xfc\xa4H' },
    2650: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            4,
            5,
            6],
        'sName': '\xbfO\xaf\xab' },
    2660: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            (4, 5),
            0,
            6],
        'sName': '\xaa\xa2\xc5]' },
    2710: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            (2, 3),
            (4, 9)],
        'lComponent': [
            5,
            6,
            7,
            8],
        'lProAccPart': [
            1,
            (2, 3),
            (4, 9)],
        'lProPart': [
            (0, 5, 6, 7)],
        'sName': '\xbcC\xc6F' },
    2770: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5,
            6,
            7],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5,
            6,
            7],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb0{\xb9q\xabL' },
    2780: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5,
            6,
            7],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5,
            6,
            7],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4p\xb2\xfc\xa5P' },
    2810: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2),
            4,
            5],
        'lComponent': [
            3,
            6,
            7,
            8],
        'lProAccPart': [
            (4, 5)],
        'lProPart': [
            7],
        'sName': '\xc5]\xaf\xab' },
    2820: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            (2, 3),
            (7, 8)],
        'lComponent': [
            4,
            5,
            6,
            9],
        'lProAccPart': [
            1,
            (2, 3),
            (7, 8)],
        'lProPart': [
            5,
            6,
            9],
        'sName': '\xbeK\xbf\xdf\xabL' },
    2830: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            7],
        'lComponent': [
            3,
            4,
            5,
            6],
        'lProAccPart': [
            1,
            2,
            7],
        'lProPart': [
            3,
            5,
            6],
        'sName': '\xa4\xd1\xad\xbb\xaa\xb0' },
    2930: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            4,
            5,
            6],
        'sName': '\xb5\\\xb5]\xa5P\xa4l' },
    2950: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5,
            6,
            7],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5,
            6,
            7],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xc2I\xc2I' },
    2960: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5,
            6,
            7],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5,
            6,
            7],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa6\xba\xaf\xab' },
    2970: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 10),
            (6, 7),
            (8, 9)],
        'lComponent': [
            2,
            3,
            4,
            5],
        'lProAccPart': [
            (1, 10),
            (6, 7),
            (8, 9)],
        'lProPart': [
            2],
        'sName': '\xb3\xb7\xa4H\xa4\xfd' },
    2980: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5,
            6,
            7],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5,
            6,
            7],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4p\xbd\xb9\xa5P' },
    2990: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            4,
            1,
            (2, 3, 5)],
        'lComponent': [
            6,
            7,
            8,
            9],
        'lProAccPart': [
            4,
            1,
            (2, 3, 5)],
        'lProPart': [
            6,
            7,
            8],
        'sName': '\xa7\xd9\xab\xdf\xa8\xcf\xaa\xcc' },
    3001: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3' },
    3002: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xaaZ\xbe\xb9\xa9\xb1\xa6\xd1\xc1\xf3' },
    3006: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3' },
    3007: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa8\xae\xa5\xed' },
    3012: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xaa\xf9\xbd\xc3' },
    3013: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            4,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            4,
            2,
            3],
        'sName': '\xa4p\xa8k\xab\xc4' },
    3014: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4p\xa4k\xab\xc4' },
    3015: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb6]\xb0\xf3' },
    3016: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xae\xd1\xa5\xcd' },
    3017: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa6\xbf\xb4\xf2\xabL\xab\xc8' },
    3019: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4X\xf8U' },
    3020: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb4I\xaea\xa4p\xa9j' },
    3022: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb0\xd3\xa4H' },
    3023: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xadW\xa4O' },
    3024: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4\xa4\xa6~\xa4j\xc2T' },
    3029: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa7\xf8\xaa\xf8' },
    3030: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xbcp\xaf\xab' },
    3031: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4\xe5\xa9x' },
    3032: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xaaZ\xa9x' },
    3033: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb2\xbd\xaa\xc1' },
    3034: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa6\xbf\xb4\xf2\xae\xf6\xa4l' },
    3036: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa9M\xa9|' },
    3037: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa5D\xab\xf9' },
    3038: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xb0\xa3\xc5]\xaev' },
    3039: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa5P\xa4k' },
    3040: {
        'iBlink': 5,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 1,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4k\xabL\xab\xc8' },
    3091: {
        'iBlink': 0,
        'iChangeZ': -90,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xac\xe8\xc4@\xaf\xab\xbe\xf0' },
    3092: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xach\xbe\xf0' },
    3093: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xbe\xf0\xad]' },
    4005: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            (4, 6)],
        'sName': '\xb9\xda\xb7Q\xa5\xf8\xc3Z' },
    4006: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            (4, 5, 6)],
        'sName': '\xa4p\xad\xb8\xbd\xde' },
    4007: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7,
            8],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            6,
            (7, 8)],
        'sName': '\xa4p\xa5\xd5\xb9\xab' },
    4008: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (6, 7),
            8,
            (9, 10, 11, 12, 13)],
        'lComponent': [
            1,
            2,
            3,
            4,
            5],
        'lProAccPart': [
            (6, 7),
            8,
            (9, 10, 11, 12, 13)],
        'lProPart': [
            (1, 2, 3, 5)],
        'sName': '\xac\xf5\xaa\xa2\xc0s' },
    4009: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2),
            (3, 5, 10),
            6],
        'lComponent': [
            4,
            7,
            8,
            9],
        'lProAccPart': [
            (1, 2),
            (3, 5, 10),
            6],
        'lProPart': [
            (7, 9),
            8],
        'sName': '\xa4j\xba\xb5\xbf\xdf' },
    4010: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (3, 7),
            1,
            2],
        'lComponent': [
            4,
            5,
            6,
            8],
        'lProAccPart': [
            (3, 7),
            1,
            2],
        'lProPart': [
            (5, 6, 8)],
        'sName': '\xa5C\xa4\xf1\xa8\xdf' },
    4012: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            (2, 3),
            (5, 6)],
        'lComponent': [
            4,
            7,
            8,
            9],
        'lProAccPart': [
            1,
            (2, 3),
            (5, 6)],
        'lProPart': [
            7,
            8,
            9],
        'sName': '\xa6p\xb7N\xbf\xdf' },
    4014: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2),
            (3, 7),
            (8, 9)],
        'lComponent': [
            4,
            5,
            6,
            10],
        'lProAccPart': [
            (1, 2),
            (3, 7),
            (8, 9)],
        'lProPart': [
            5,
            6,
            10],
        'sName': '\xa4p\xba\xd6\xa4\xfb' },
    4018: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (5, 6),
            (1, 2),
            (3, 10)],
        'lComponent': [
            4,
            7,
            8,
            9],
        'lProAccPart': [
            (1, 2),
            (3, 10),
            (5, 6)],
        'lProPart': [
            7,
            8,
            9],
        'sName': '\xa4p\xa4\xd1\xb0\xa8' },
    4019: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2),
            3,
            7],
        'lComponent': [
            4,
            5,
            6,
            8],
        'lProAccPart': [
            (1, 2),
            3,
            7],
        'lProPart': [
            0,
            (5, 8),
            6],
        'sName': '\xbc\xd6\xa6\xcf\xa6\xcf' },
    4020: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2),
            (3, 7),
            8],
        'lComponent': [
            4,
            5,
            6,
            9],
        'lProAccPart': [
            (1, 2),
            (3, 7),
            8],
        'lProPart': [
            5,
            6,
            9],
        'sName': '\xa4p\xc6F\xb5U' },
    4023: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            (3, 5)],
        'lComponent': [
            4,
            6,
            7,
            8,
            9],
        'lProAccPart': [
            1,
            2,
            (3, 5)],
        'lProPart': [
            7,
            8,
            6],
        'sName': '\xabC\xb6\xb3\xc0s' },
    4027: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            3,
            (1, 2),
            (9, 10)],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            3,
            (1, 2),
            (9, 10)],
        'lProPart': [
            5,
            6,
            7],
        'sName': '\xa5\xf8\xc3Z\xac\xd3' },
    4028: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            7],
        'lComponent': [
            3,
            4,
            5,
            6],
        'lProAccPart': [
            1,
            2,
            7],
        'lProPart': [
            3,
            4,
            5],
        'sName': '\xa8\xdf\xbcC\xab\xc8' },
    4041: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            (2, 3),
            7],
        'lComponent': [
            4,
            5,
            6,
            8],
        'lProAccPart': [
            1,
            (2, 3),
            7],
        'lProPart': [
            5,
            6,
            8],
        'sName': '\xb3p\xbb\xbb' },
    4042: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            6,
            7],
        'sName': '\xa9\xfa\xa6\xd0' },
    4043: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            6,
            7],
        'sName': '\xb5\xa3\xc4_' },
    4044: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            5,
            6,
            7],
        'sName': '\xabC\xbe\xc8' },
    4045: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            3,
            (2, 7)],
        'lComponent': [
            4,
            5,
            6,
            8],
        'lProAccPart': [
            1,
            3,
            (2, 7)],
        'lProPart': [
            5,
            6,
            8],
        'sName': '\xc4\xc6\xae\xfc' },
    4046: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            (2, 9),
            7],
        'lComponent': [
            3,
            4,
            5,
            6],
        'lProAccPart': [
            1,
            (2, 9),
            7],
        'lProPart': [
            3,
            5,
            6],
        'sName': '\xb9p\xa4\xd6' },
    4104: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            2,
            3],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            1,
            2,
            3],
        'lProPart': [
            4,
            6,
            7],
        'sName': '\xad\xec\xa9l\xa4H' },
    4106: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 0,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [],
        'lProPart': [
            (1, 3),
            2],
        'sName': '\xa7\xeb\xa5\xdb\xa8\xae' },
    4107: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 0,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [],
        'lProPart': [
            (1, 3),
            2],
        'sName': '\xa9\xb8\xa8\xae' },
    4402: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xafP\xb5K\xbb\xc8\xc4_\xbdc' },
    5100: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            2,
            3,
            (1, 4, 5)],
        'lComponent': [
            6,
            7,
            8,
            9],
        'lProAccPart': [
            (1, 2),
            3,
            (4, 5)],
        'lProPart': [
            (6, 7),
            8],
        'sName': '\xab\xb6\xa4\xec\xafT' },
    5101: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2, 5),
            (3, 4),
            (11, 6)],
        'lComponent': [
            7,
            8,
            9,
            10],
        'lProAccPart': [
            (1, 2, 5),
            (3, 4),
            (11, 6)],
        'lProPart': [
            (7, 8),
            9],
        'sName': '\xb5q\xa4\xeb\xaf\xab' },
    5102: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            1,
            (2, 4),
            3],
        'lComponent': [
            5,
            6,
            7,
            8],
        'lProAccPart': [
            1,
            (2, 4),
            3],
        'lProPart': [
            0,
            6,
            (7, 8)],
        'sName': '\xbb\xb7\xa5j\xa6u\xa7\xc7' },
    5103: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            3,
            2,
            1],
        'lComponent': [
            4,
            5,
            6,
            7],
        'lProAccPart': [
            3,
            2,
            1],
        'lProPart': [
            0,
            6,
            5],
        'sName': '\xbfK\xb5K\xbe\xd4\xaf\xab' },
    5104: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (6, 8, 9, 13),
            11,
            (7, 10, 12)],
        'lComponent': [
            1,
            2,
            3,
            4,
            5],
        'lProAccPart': [
            (6, 8, 9, 13),
            11,
            (7, 10, 12)],
        'lProPart': [
            2,
            (3, 4)],
        'sName': '\xb1s\xc6F\xa4\xd6\xa4k-\xaak\xb3N' },
    5105: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (6, 8, 9, 13),
            11,
            (7, 10, 12)],
        'lComponent': [
            1,
            2,
            3,
            4,
            5],
        'lProAccPart': [
            (6, 8, 9, 13),
            11,
            (7, 10, 12)],
        'lProPart': [
            2,
            (3, 4)],
        'sName': '\xb1s\xc6F\xa4\xd6\xa4k-\xaa\xab\xb2z' },
    8004: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 0,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2, 3, 11),
            (10, 12)],
        'lComponent': [
            4,
            5,
            6,
            7,
            8,
            9],
        'lProAccPart': [
            (1, 2, 3, 11),
            (10, 12)],
        'lProPart': [
            4,
            5,
            6],
        'sName': '\xa9b\xb9p\xb0\xa8' },
    8027: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            0],
        'lProAccPart': [],
        'lProPart': [
            0],
        'sName': '\xa5\xfa\xacW' },
    8034: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            0],
        'sName': '\xad\xbb\xc5n' },
    8061: {
        'iBlink': 0,
        'iChangeZ': -90,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 1,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xc0\xb0\xac\xa3\xb8t\xbe\xf0' },
    8062: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa5\xa8\xa4j\xa4s\xbd\xde' },
    8063: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4j\xa4s\xbd\xde' },
    8065: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xa5\xf8\xc3Z\xb3J' },
    8066: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xad\xbb\xc5n\xb4\xa3\xa5\xdc\xafS\xae\xc4' },
    8067: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 2,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xad\xbb\xc5n\xb4\xa3\xa5\xdc\xafS\xae\xc42' },
    8075: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 2,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xa4j\xc5]\xae\xf0' },
    8077: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 0,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            (1, 2, 3, 7, 8, 9, 10, 11, 12),
            (14, 15)],
        'lComponent': [
            4,
            5,
            6,
            13],
        'lProAccPart': [
            (1, 2, 3, 7, 8, 9, 10, 11, 12),
            (14, 15)],
        'lProPart': [
            4,
            5,
            6],
        'sName': '\xb9a\xc5L\xa4p\xd8p' },
    8078: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            5],
        'lComponent': [
            1,
            2,
            3,
            4],
        'lProAccPart': [
            5],
        'lProPart': [
            1,
            2,
            3],
        'sName': '\xa4j\xa4O\xb0\xad\xa4\xfd' },
    8092: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xbd\xd5\xa6\xe2\xb1\xf8' },
    8093: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xbc@\xb1\xa1\xbd\xb9\xbd\xba' },
    8094: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [
            0],
        'lComponent': [
            0],
        'lProAccPart': [],
        'lProPart': [
            0],
        'sName': '\xb4\xb9\xb6\xf0' },
    8102: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xb0}\xa5\xdb' },
    8103: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xc5]\xaf\xab\xbcC' },
    8104: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xbfE\xac\xa1\xb0}\xa5\xdb' },
    8106: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            0],
        'lProAccPart': [],
        'lProPart': [
            0],
        'sName': '\xb6\xc7\xb0e\xaa\xf9' },
    9000: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xbcC12' },
    9001: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xbcC13' },
    9002: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xb5\xa712' },
    9003: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xb5\xa713' },
    9004: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xae\xb112' },
    9005: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xae\xb113' },
    9006: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xa4M12' },
    9007: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xa4M13' },
    9008: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xbaj12' },
    9009: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xbaj13' },
    9010: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xb7t\xbe\xb912' },
    9011: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': None,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [
            1],
        'sName': '\xb7t\xbe\xb913' },
    9998: {
        'iBlink': 0,
        'iChangeZ': 0,
        'iOnlyNew': 1,
        'iResHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'lAccessories': [],
        'lComponent': [
            1],
        'lProAccPart': [],
        'lProPart': [],
        'sName': '\xaa\xc5\xafS\xae\xc4' } }
for HORSE_DATA in {
    'dCvrInfo': {
        1: 5,
        2: 6,
        3: 7,
        4: 8,
        5: 9,
        6: 10,
        7: 11,
        8: 12,
        9: 13,
        10: 14,
        11: 15,
        12: 16,
        101: 1,
        102: 2,
        103: 3,
        104: 4 },
    'iBlink': 0,
    'iFemaleType': 1,
    'iMulType': 1 }:
    None[4] = {
        1: {
            'dCvrInfo': {
                1: 5,
                2: 6,
                3: 7,
                4: 8,
                5: 9,
                6: 10,
                7: 11,
                8: 12,
                9: 13,
                10: 14,
                11: 15,
                101: 1,
                102: 2,
                103: 3,
                104: 4 },
            'iBlink': 0,
            'iFemaleType': 1,
            'iMulType': 1,
            'iRiderHigh': 23,
            'iShadow': 0,
            'iSpeStand': 0,
            'iType': 1,
            'lAccessories': [
                (1, 2, 9),
                (10, 11)],
            'lAccessoriesPart': { },
            'lComponent': [
                3,
                4,
                5,
                6,
                7,
                8],
            'lHeroPos': [
                1],
            'lPalAccBind': [
                (1, 2, 9),
                (10, 11)],
            'lPalBind': [
                (3, 4, 5, 7, 8),
                (6,)],
            'sName': '\xbfK\xb5K\xaa\xea' },
        2: {
            'dCvrInfo': {
                1: 5,
                2: 6,
                3: 7,
                4: 8,
                5: 9,
                6: 10,
                7: 11,
                8: 12,
                101: 1,
                102: 2,
                103: 3,
                104: 4 },
            'iBlink': 0,
            'iFemaleType': 1,
            'iMulType': 1,
            'iRiderHigh': 5,
            'iShadow': 0,
            'iSpeStand': 0,
            'iType': 1,
            'lAccessories': [
                (1, 2, 3, 7),
                (8,)],
            'lAccessoriesPart': { },
            'lComponent': [
                4,
                5,
                6],
            'lHeroPos': [
                1],
            'lPalAccBind': [
                (1, 2, 3, 7),
                (8,)],
            'lPalBind': [
                (5,),
                (4, 6)],
            'sName': '\xb4H\xc1\xf7\xba\xb5' },
        3: {
            'dCvrInfo': {
                1: 5,
                2: 6,
                3: 7,
                4: 8,
                5: 9,
                6: 10,
                7: 11,
                8: 12,
                9: 13,
                10: 14,
                11: 15,
                12: 16,
                13: 17,
                14: 18,
                101: 1,
                102: 2,
                103: 3,
                104: 4 },
            'iBlink': 0,
            'iFemaleType': 1,
            'iMulType': 1,
            'iRiderHigh': 0,
            'iShadow': 0,
            'iSpeStand': 0,
            'iType': 1,
            'lAccessories': [
                (1, 2, 3),
                (11, 12, 13, 14)],
            'lAccessoriesPart': { },
            'lComponent': [
                4,
                5,
                6,
                7,
                8,
                9,
                10],
            'lHeroPos': [
                1],
            'lPalAccBind': [
                (1, 2, 3),
                (11, 12, 13, 14)],
            'lPalBind': [
                (5, 7),
                (4, 10)],
            'sName': '\xa4\xf4\xc6F\xb3\xc0' },
        'iRiderHigh': None,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2, 3, 11),
            (10, 12)],
        'lAccessoriesPart': { },
        'lComponent': [
            4,
            5,
            6,
            7,
            8,
            9],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2, 3, 11),
            (10, 12)],
        'lPalBind': [
            (5, 8),
            (4,)],
        'sName': '\xa9b\xb9p\xb0\xa8' }
    None[5] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 15,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2),
            (6,)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2),
            (6,)],
        'lPalBind': [
            (4, 5),
            (3,)],
        'sName': '\xc5]\xb4\xb9\xaf\xf3' }
    None[6] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 19,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1,),
            (5, 6, 8)],
        'lAccessoriesPart': { },
        'lComponent': [
            2,
            3,
            4],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (5, 6, 8)],
        'lPalBind': [
            (3,),
            (2, 4)],
        'sName': '\xa9]\xb0\\' }
    None[7] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 2,
        'lAccessories': [
            (1, 2),
            (10, 11)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5,
            6,
            7,
            8],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2),
            (10, 11)],
        'lPalBind': [
            (3, 5, 7),
            (4, 6)],
        'sName': '\xc5]\xb4\xb9\xbc\xc9\xc0s' }
    None[8] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 18,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 2,
        'lAccessories': [
            (1, 9),
            (10, 11)],
        'lAccessoriesPart': { },
        'lComponent': [
            2,
            3,
            4,
            5,
            6,
            7,
            8],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (9, 10, 11)],
        'lPalBind': [
            (4, 6),
            (3, 5, 7, 8)],
        'sName': '\xadn\xb6\xeb\xb3\xb0\xbe\xd4\xb3\xbe' }
    None[9] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            101: 1,
            105: 2,
            106: 3 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 3,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10],
        'lHeroPos': [
            1],
        'lPalAccBind': [],
        'lPalBind': [
            (0,),
            (3, 4)],
        'sName': '\xb4I\xb6Q\xaa\xf7\xb3\xbd' }
    None[10] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            14: 18,
            101: 1,
            105: 2,
            106: 3 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 3,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (0,)],
        'lPalBind': [
            (3, 5, 6, 7, 8, 9, 10),
            (4,)],
        'sName': '\xa8g\xc3T\xbe\xd4\xbe\xf7' }
    None[11] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 1,
        'iMulType': 1,
        'iRiderHigh': 19,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2, 9),
            (10, 11)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5,
            6,
            7,
            8],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2),
            (9, 10, 11)],
        'lPalBind': [
            (3, 4, 5, 7),
            (6, 8)],
        'sName': '\xba\xd1\xa4\xf4\xc4Q\xc5\xef' }
    None[12] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 1,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [
            (1,),
            (2,)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5,
            6],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (2,)],
        'lPalBind': [
            (0, 3, 4, 6),
            (5,)],
        'sName': '\xa6N\xb2\xbb\xc4_\xa4\xeb' }
    None[13] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1,),
            (2,)],
        'lAccessoriesPart': { },
        'lComponent': [],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (2,)],
        'lPalBind': [
            (3, 4, 5),
            (6, 7, 8)],
        'sName': '\xa8\xaa\xb2\xb4\xb7\xe0\xf8l' }
    None[14] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 1,
        'iMulType': 1,
        'iRiderHigh': 12,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2),
            (12, 13)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2),
            (12, 13)],
        'lPalBind': [
            (4, 5, 6, 7),
            (8, 9, 10, 11)],
        'sName': '\xac\xc2\xc4n\xa5\xc9\xa8\xdf' }
    None[15] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            101: 1 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 16,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11],
        'lHeroPos': [
            1],
        'lPalAccBind': [],
        'lPalBind': [
            (0,),
            (3, 4)],
        'sName': '\xb4I\xb6Q\xaa\xf7\xb3\xbd\xa4p\xa7\xa4\xc3M' }
    None[16] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            101: 1 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 11,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4,
            5,
            6],
        'lHeroPos': [
            1],
        'lPalAccBind': [],
        'lPalBind': [
            (0,),
            (1, 2, 3, 4)],
        'sName': '\xa8g\xc3T\xbe\xd4\xbe\xf7\xa4p\xa7\xa4\xc3M' }
    None[17] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': -32,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [
            (1, 2),
            (7,)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5,
            6],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2),
            (7,)],
        'lPalBind': [
            (0, 3, 5, 6),
            (4,)],
        'sName': '\xafP\xb5K\xb8\xac\xc4\xaa' }
    None[18] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            14: 18,
            15: 19,
            16: 20,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 1,
        'iMulType': 1,
        'iRiderHigh': 33,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 8, 9, 10, 15, 16),
            (11, 12, 13, 14)],
        'lAccessoriesPart': { },
        'lComponent': [
            2,
            3,
            4,
            5,
            6,
            7],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 8, 9),
            (10, 11, 12, 13, 14, 15, 16)],
        'lPalBind': [
            (3, 5, 6, 7),
            (2, 4)],
        'sName': '\xbd\xf1\xb6\xb3\xaa\xb0' }
    None[19] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 1,
        'iMulType': 1,
        'iRiderHigh': 12,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 2,
        'lAccessories': [
            (1,),
            (6,)],
        'lAccessoriesPart': { },
        'lComponent': [
            2,
            3,
            4,
            5],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (6,)],
        'lPalBind': [
            (2, 3, 5),
            (4,)],
        'sName': '\xa6a\xa5\xc8\xc0t' }
    None[20] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            101: 1 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 4,
        'lAccessories': [
            (3,),
            (5,)],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            4],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (3,),
            (5,)],
        'lPalBind': [
            (0, 4),
            (1,)],
        'sName': '\xbd\xac\xb5\xd8' }
    None[21] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            101: 1 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 4,
        'lAccessories': [
            (3,),
            (5,)],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (3,),
            (5,)],
        'lPalBind': [
            (0, 1),
            (2,)],
        'sName': '\xa4\xd1\xe6\xa2' }
    None[22] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            101: 1 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 4,
        'lAccessories': [
            (1,),
            (4, 5)],
        'lAccessoriesPart': { },
        'lComponent': [
            6,
            7],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (4, 5)],
        'lPalBind': [
            (6,),
            (7,)],
        'sName': '\xaf}\xaa\xc5' }
    None[23] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            14: 18,
            15: 19,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 1,
        'iMulType': 2,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2, 3, 7, 8, 9, 10, 11, 12),
            (14, 15)],
        'lAccessoriesPart': {
            14: 13,
            15: 4 },
        'lComponent': [
            4,
            5,
            6,
            13],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2, 3, 7, 8, 9, 10, 11, 12),
            (14, 15)],
        'lPalBind': [
            (6, 13),
            (5,)],
        'sName': '\xb9a\xc5L\xa4p\xd8p' }
    None[24] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 2,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 7, 8, 9, 11),
            (10,)],
        'lAccessoriesPart': {
            10: 0,
            11: 1 },
        'lComponent': [
            2,
            3,
            4,
            5,
            6],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 7, 8, 9, 11),
            (10,)],
        'lPalBind': [
            (3, 5, 6),
            (4,)],
        'sName': '\xa4E\xbe]\xb6\xb3\xc0s' }
    None[25] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2, 3, 7),
            (10, 11, 12)],
        'lAccessoriesPart': {
            10: 2,
            11: 7,
            12: 5 },
        'lComponent': [
            4,
            5,
            6,
            8,
            9],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2, 3, 7),
            (10, 11, 12)],
        'lPalBind': [
            (4, 6, 9),
            (5,)],
        'sName': '\xc2\xf9\xa4l\xb2\xa2\xa4\xdf(\xc2\xc5)' }
    None[26] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2, 3, 7),
            (10, 11, 12)],
        'lAccessoriesPart': {
            10: 2,
            11: 7,
            12: 5 },
        'lComponent': [
            4,
            5,
            6,
            8,
            9],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2, 3, 7),
            (10, 11, 12)],
        'lPalBind': [
            (4, 6, 9),
            (5,)],
        'sName': '\xc2\xf9\xa4l\xb2\xa2\xa4\xdf(\xaf\xbb)' }
    None[27] = {
        'dCvrInfo': {
            1: 6,
            2: 7,
            3: 8,
            4: 9,
            5: 10,
            6: 11,
            7: 12,
            8: 13,
            9: 14,
            10: 15,
            11: 16,
            12: 17,
            13: 18,
            14: 19,
            15: 20,
            101: 1,
            102: 2,
            103: 3,
            104: 5,
            107: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 28,
        'iShadow': 1,
        'iSpeStand': 0,
        'iType': 5,
        'lAccessories': [
            (5, 6, 13, 15),
            (7, 8, 12, 14)],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4,
            9,
            10,
            11],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (5, 6, 13, 15),
            (7, 8, 12, 14)],
        'lPalBind': [
            (1, 2, 3, 4),
            (0, 9, 10, 11)],
        'sName': '\xb3v\xa4\xe9\xaa\xf7\xa4\xfb' }
    None[28] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 2,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 3,
        'lAccessories': [
            (9, 10),
            (1, 2, 8, 12, 13)],
        'lAccessoriesPart': { },
        'lComponent': [
            3,
            4,
            5,
            6,
            7,
            11],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (9, 10),
            (1, 2, 8, 12, 13)],
        'lPalBind': [
            (0, 4, 7, 11),
            (3, 5, 6)],
        'sName': '\xa4\xd1\xabC\xbe\xa5\xa8\xf7' }
    None[29] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            101: 1,
            105: 2,
            106: 3 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 3,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 5,
        'lAccessories': [
            (1,),
            (5, 7, 8)],
        'lAccessoriesPart': { },
        'lComponent': [
            2,
            3,
            4,
            6,
            9,
            10,
            11],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1,),
            (5, 7, 8)],
        'lPalBind': [
            (2, 3),
            (0, 4, 6)],
        'sName': '\xa4\xd1\xae\xf0\xb6\xb3\xa4j' }
    None[30] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            101: 1 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 5,
        'lAccessories': [],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4],
        'lHeroPos': [
            1],
        'lPalAccBind': [],
        'lPalBind': [
            (2, 3),
            (0, 1, 4)],
        'sName': '\xa4\xd1\xae\xf0\xb6\xb3\xa4p' }
    None[31] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 2,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 2, 12),
            (3, 4, 5, 6, 11)],
        'lAccessoriesPart': { },
        'lComponent': [
            7,
            8,
            9,
            10,
            13],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 2, 12),
            (3, 4, 5, 6, 11)],
        'lPalBind': [
            (9,),
            (10,)],
        'sName': '\xa4j\xaa\xaf' }
    None[32] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            14: 18,
            15: 19,
            16: 20,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 2,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (1, 3, 4),
            (2, 14)],
        'lAccessoriesPart': { },
        'lComponent': [
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            15,
            16],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 3, 4),
            (2, 14)],
        'lPalBind': [
            (5, 6, 7, 8, 12, 13),
            (9, 10, 11, 15, 16)],
        'sName': '\xacP\xaae\xa4\xeb\xa6\xe0' }
    None[33] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            14: 18,
            15: 19,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 2,
        'lAccessories': [
            (1, 3, 4),
            (2, 5, 14, 15)],
        'lAccessoriesPart': { },
        'lComponent': [
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (1, 3, 4),
            (2, 5, 14, 15)],
        'lPalBind': [
            (6, 7),
            (8, 11, 12, 13, 9, 10)],
        'sName': '\xa5\xf8\xc3Z\xa4\xfd' }
    None[34] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (3, 2, 9),
            (1, 5, 6)],
        'lAccessoriesPart': { },
        'lComponent': [
            4,
            7,
            8,
            10],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (3, 2, 9),
            (1, 5, 6)],
        'lPalBind': [
            (4,),
            (0, 7, 8, 10)],
        'sName': '\xa9\xaf\xb9B\xbd\xde' }
    None[35] = {
        'dCvrInfo': {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 9,
            6: 10,
            7: 11,
            8: 12,
            9: 13,
            10: 14,
            11: 15,
            12: 16,
            13: 17,
            101: 1,
            105: 2 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 2,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 1,
        'lAccessories': [
            (5, 6, 7, 13),
            (8, 9, 10)],
        'lAccessoriesPart': { },
        'lComponent': [
            1,
            2,
            3,
            4,
            11,
            12],
        'lHeroPos': [
            1],
        'lPalAccBind': [
            (5, 6, 7, 13),
            (8, 9, 10)],
        'lPalBind': [
            (4, 12),
            (0, 1, 2, 3, 11)],
        'sName': '\xacP\xa8\xb0\xc0s' }
    None[100] = {
        'dCvrInfo': {
            1: 5,
            101: 1,
            102: 2,
            103: 3,
            104: 4 },
        'iBlink': 0,
        'iFemaleType': 0,
        'iMulType': 1,
        'iRiderHigh': 0,
        'iShadow': 0,
        'iSpeStand': 0,
        'iType': 0,
        'lAccessories': [],
        'lAccessoriesPart': { },
        'lComponent': [
            1],
        'lHeroPos': [
            1],
        'lPalAccBind': [],
        'lPalBind': [
            (1,)],
        'sName': '\xb9\xda\xa4\xdb\xc2\xfe\xc6H' }
    HORSE_POS_DATA = {
        9: {
            1: {
                1: (-16, -48),
                2: (8, -27),
                3: (-7, -49),
                4: (-2, -45),
                5: (1, -42),
                6: (-1, -40),
                7: (2, -36),
                8: (-9, -45) },
            2: {
                1: (-89, -2),
                2: (-15, -53),
                3: (56, -6),
                4: (12, 33),
                5: (-70, -31),
                6: (54, -44),
                7: (67, 22),
                8: (-50, 33) },
            3: {
                1: (13, -48),
                2: (87, -1),
                3: (-21, 30),
                4: (-55, -19),
                5: (70, -37),
                6: (56, 23),
                7: (-64, 23),
                8: (-48, -45) },
            4: {
                1: (-81, 87),
                2: (-141, -44),
                3: (165, -76),
                4: (114, 74),
                5: (-142, 33),
                6: (-8, -121),
                7: (158, 21),
                8: (-3, 92) },
            5: {
                1: (168, -53),
                2: (109, 82),
                3: (-47, 87),
                4: (-99, -100),
                5: (154, 38),
                6: (4, 114),
                7: (-145, 21),
                8: (-1, -110) } },
        10: {
            1: {
                1: (0, 5),
                2: (20, 5),
                3: (11, 11),
                4: (5, 15),
                5: (6, 30),
                6: (10, 15),
                7: (5, 15),
                8: (10, 5) },
            2: {
                1: (-100, -25),
                2: (40, -55),
                3: (120, 15),
                4: (-35, 60),
                5: (-55, -20),
                6: (110, -35),
                7: (60, 55),
                8: (-85, 15) },
            3: {
                1: (-20, -55),
                2: (120, -15),
                3: (30, 55),
                4: (-120, 25),
                5: (55, -20),
                6: (110, 25),
                7: (-50, 55),
                8: (-90, -50) },
            4: {
                1: (-105, 41),
                2: (-100, -94),
                3: (89, -80),
                4: (106, 57),
                5: (-145, -50),
                6: (-2, -104),
                7: (150, -40),
                8: (-35, 59) },
            5: {
                1: (97, -71),
                2: (122, 22),
                3: (-143, 49),
                4: (-93, -75),
                5: (145, -50),
                6: (-2, 91),
                7: (-150, -40),
                8: (-35, -105) } },
        12: {
            1: {
                1: (13, -29),
                2: (-14, -27),
                3: (-26, -41),
                4: (22, -42),
                5: (1, -5),
                6: (-28, -35),
                7: (-1, -41),
                8: (24, -36) } },
        23: {
            1: {
                1: (2, -7),
                2: (0, -7),
                3: (-15, -11),
                4: (11, -20),
                5: (0, 2),
                6: (-13, -7),
                7: (0, -24),
                8: (12, -16) },
            2: {
                1: (-27, -17),
                2: (25, -18),
                3: (13, -6),
                4: (-14, -9),
                5: (0, -9),
                6: (22, -14),
                7: (0, -7),
                8: (-23, -15) } },
        24: {
            1: {
                1: (8, -50),
                2: (-1, -48),
                3: (-15, -51),
                4: (13, -51),
                5: (0, -42),
                6: (-4, -50),
                7: (0, -50),
                8: (8, -50) },
            2: {
                1: (-23, -60),
                2: (26, -59),
                3: (14, -46),
                4: (-12, -44),
                5: (0, -68),
                6: (30, -50),
                7: (0, -28),
                8: (-24, -50) } },
        27: {
            1: {
                1: (-36, -26),
                2: (65, -44),
                3: (66, 32),
                4: (-44, 9),
                5: (5, -62),
                6: (94, -21),
                7: (7, 23),
                8: (-72, -20) } },
        28: {
            1: {
                1: (8, -50),
                2: (-1, -48),
                3: (-15, -51),
                4: (13, -51),
                5: (0, -42),
                6: (-4, -50),
                7: (0, -50),
                8: (8, -50) },
            2: {
                1: (-23, -60),
                2: (26, -59),
                3: (14, -46),
                4: (-12, -44),
                5: (0, -68),
                6: (30, -50),
                7: (0, -28),
                8: (-24, -50) } },
        31: {
            1: {
                1: (-5, -22),
                2: (0, -28),
                3: (-5, -29),
                4: (-2, -29),
                5: (2, -33),
                6: (2, -24),
                7: (-1, -33),
                8: (0, -20) },
            2: {
                1: (-33, -34),
                2: (32, -33),
                3: (28, -11),
                4: (-28, -10),
                5: (1, -52),
                6: (40, -23),
                7: (0, -12),
                8: (-40, -18) } } }
    FAIRY_DATA = {
        6038: {
            'iOnlyNew': 1,
            'sName': '\xa9\xdb\xb0]\xbf\xdf' },
        6039: {
            'iOnlyNew': 1,
            'sName': '\xc6F\xb5\xea\xf3\xcb' },
        6040: {
            'iOnlyNew': 1,
            'sName': '\xa4\xf5\xc4Q\xc5\xef' },
        6041: {
            'iOnlyNew': 1,
            'sName': '\xba\xb5\xbf\xdf\xadD\xb9F' },
        6048: {
            'iOnlyNew': 1,
            'sName': '\xb3v\xa4\xe9\xaa\xf7\xa4\xfb' },
        6051: {
            'iOnlyNew': 1,
            'sName': '\xa5]\xa4l\xa5\xf5\xbc}' },
        6052: {
            'iOnlyNew': 1,
            'sName': '\xa5]\xa4l\xc1y\xac\xf5' },
        6053: {
            'iOnlyNew': 1,
            'sName': '\xa5]\xa4l\xbfE\xb0\xca' } }
    AURA_DATA = {
        14: {
            'iOnlyNew': 1,
            'sName': '\xa9]\xabB\xac\xf5\xbd\xac' },
        15: {
            'iOnlyNew': 1,
            'sName': '\xafI\xban\xa4\xa7\xa4\xdf' },
        16: {
            'iOnlyNew': 1,
            'sName': '\xa6B\xb4\xb9' },
        17: {
            'iOnlyNew': 1,
            'sName': '\xaa\xea\xbez' },
        18: {
            'iOnlyNew': 1,
            'sName': '\xabC\xc0s' } }
    TRACK_DATA = {
        14: {
            'iOnlyNew': 1,
            'sName': '\xa9]\xabB\xb2\xfc\xc5\xca' },
        15: {
            'iOnlyNew': 1,
            'sName': '\xbfR\xad\xec\xa4\xa7\xa4\xf5' },
        16: {
            'iOnlyNew': 1,
            'sName': '\xa6B\xb4\xb9' },
        17: {
            'iOnlyNew': 1,
            'sName': '\xaa\xea\xbez' } }
    SPE_WING_PAL_DATA = {
        24: {
            5: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    5] },
            6: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    6] },
            7: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    7] },
            8: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    8] },
            9: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    9] },
            10: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    10] },
            11: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    11] } },
        26: {
            5: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    5] },
            6: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    6] },
            7: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    7] },
            8: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    8] },
            9: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    9] },
            10: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    10] },
            11: {
                'iClientType': 3,
                'sRes': '[state]1',
                'tColor': [
                    11] } } }
    return None
