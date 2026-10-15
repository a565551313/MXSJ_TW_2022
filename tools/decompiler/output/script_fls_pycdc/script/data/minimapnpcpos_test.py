# pycdc 交叉复核产物 · script.fls entry 4897
# co_filename(原始)='script/data/minimapnpcpos_test.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4897.pyc (Python 2.5)

import permission
VER2MASK = {
    0: 1,
    1: 2,
    2: 4 }

def InitTestData():
    data = DATA_POS[1054].values()
    if data:
        data = data[0]
    
    iTarget = -1
    for iIdx, tInfo in enumerate(data):
        if tInfo[0] == '\xbe\xd4\xb6\xa4\xa8\xcf\xaa\xcc':
            iTarget = iIdx
            break
            continue
    
    if iTarget < 0:
        data.insert(33, ('\xbe\xd4\xb6\xa4\xa8\xcf\xaa\xcc', '\xb5L\xc2\xf9', 5025, 1, (30, 200), 0, None, 255, 'z', 0, 0, '\xb5L\xc2\xf9', None, None))
    


def ver2mask(ver):
    
    try:
        return VER2MASK[ver]
    except:
        return 0



def GetData(mapid):
    import misc
    if misc.IsFreshManServer() and mapid == 1054:
        mapid = 1055
    
    if DATA_POS.has_key(mapid):
        data = DATA_POS[mapid].values()
        if data:
            data = data[0]
        
        data = DelShenHeNpc(data)
    else:
        data = []
    return data


def GetMapNpcNames(mapid):
    import npcname2realnamedata
    if mapid == 1054:
        mapid = 1055
    
    npcDict = DATA_POS.get(mapid, { })
    npcLst = npcDict.values()
    if npcLst:
        npcLst = npcLst[0]
    
    npcNameLst = []
    for npcInfo in npcLst:
        sName = npcInfo[0]
        if IsNeedDelShenHeNpc(sName):
            continue
        
        sName = npcname2realnamedata.GetRealName(sName)
        npcNameLst.append(sName)
    
    return npcNameLst


def GetNpcPosByMapAndName(iMapID, sName):
    tNpcDict = DATA_POS.get(iMapID, { })
    tNpcList = tNpcDict.values()
    if tNpcList:
        tNpcList = tNpcList[0]
    
    for tNpcInfo in tNpcList:
        if tNpcInfo[0] == sName:
            return tNpcInfo[4]
            continue
    


def GetNpcNameByMapAndName(iMapID, sName):
    tNpcList = GetData(iMapID)
    for tNpcInfo in tNpcList:
        if tNpcInfo[0] == sName:
            return tNpcInfo[11]
            continue
    


def IsNeedDelShenHeNpc(sName):
    import hero
    if hero.IsShenHe():
        return sName in ('\xc2\xa7\xa5]\xba\xeb\xc6F', '\xaf\xb5\xc4_\xb0\xd3\xa4H', '\xbf\xef\xac\xfc\xa4j\xb7|\xa5q\xbb\xf6', '\xa9\xdb\xb8u\xa4j\xa8\xcf', '\xc2I\xa5d\xb1H\xb0\xe2\xa4H')
    else:
        return False


def DelShenHeNpc(tNpcList):
    import hero
    if hero.IsShenHe():
        tTmpList = []
        for tInfo in tNpcList:
            if IsNeedDelShenHeNpc(tInfo[0]):
                continue
                continue
            tTmpList.append(tInfo)
        
        return tTmpList
    else:
        return tNpcList


def IsMiniMap(mapid):
    return DATA_POS.has_key(mapid)


def GetShidaodianClass(iSceneID):
    import defines
    if iSceneID in (1061, 1064, 1067, 1070):
        return defines.CAREER_ZS
    elif iSceneID in (1062, 1065, 1068, 1071):
        return defines.CAREER_FS
    elif iSceneID in (1063, 1066, 1069, 1072):
        return defines.CAREER_SS
    


def GetMiniData(mapid):
    
    try:
        return DATA_WENZI[mapid]
    except KeyError:
        return None


DATA_POS = {
    1001: {
        '\xa5\xc3\xbfA\xab\xb0': [
            ('\xc2\\\xc5u\xb0\xcf\xb6\xc7\xb0e\xa4H', None, 4992, 1, (67, 81), 0, None, 255, 'btqcsr', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (63, 51), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xa8\xae\xa5\xed', None, 2004, 1, (8, 5), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xabn\xbb\xbb\xb0\xea\xa4\xfd', None, 4216, 0, (113, 63), 0, None, 255, 'nygw', 0, 0, None, None, None),
            ('\xbf\xfa\xb2\xf8', None, 4405, 1, (124, 29), 0, None, 255, 'qzlb', 0, 0, '\xbf\xfa\xb2\xf8\xa6\xd1\xc1\xf3', None, None),
            ('\xa7\xba\xab\xbc\xaeQ', None, 4218, 0, (27, 69), 0, None, 255, 'syn', 0, 0, None, None, None),
            ('\xae\xe7\xb8\xad\xa8\xe0', None, 4280, 0, (94, 17), 0, None, 255, 'lye', 0, 0, None, None, None),
            ('\xa7d\xb1\xd0\xc0Y', None, 4228, 0, (84, 56), 0, None, 255, 'wjt', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (55, 38), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xa5\xc3\xbfA\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (8, 49), 0, None, 255, 'yzcsr', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1016, 2, (68, 26), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1083, 2, (28, 32), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1002: {
        '\xb2M\xb7\xcb\xab\xb0': [
            ('\xb5\xf4\xc1_\xa9\xb1', None, 1006, 2, (97, 124), 0, None, 255, 'cfdlb', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (16, 36), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xb3\xaf\xa4\xd2\xa4H', None, 4207, 0, (159, 73), 0, None, 255, 'cfr', 0, 0, None, None, None),
            ('\xb3\xaf\xad\xfb\xa5~', None, 4208, 0, (35, 129), 0, None, 255, 'cyw', 0, 0, None, None, None),
            ('\xa4u\xb7~\xb0\xcf', None, 4601, 1, (175, 132), 0, None, 255, 'gyqjyr', 0, 0, None, None, None),
            ('\xa4\xbd\xae]\xb6~', None, 4205, 0, (39, 11), 0, None, 255, 'gsx', 0, 0, None, None, None),
            ('\xadJ\xa5b\xa5P', None, 4209, 0, (123, 127), 0, None, 255, 'hbx', 0, 0, None, None, None),
            ('\xb2M\xb7\xcb\xab\xb0\xb0\xd3\xa4H', None, 4753, 1, (78, 105), 0, None, 255, 'qxcsr', 0, 0, None, None, None),
            ('\xb2M\xb7\xcb\xab\xb0\xb0\xd3\xa4H', None, 4765, 1, (163, 33), 0, None, 255, 'qxcsr', 0, 0, None, None, None),
            ('\xad\xba\xb9\xa2\xa9\xb1', None, 1063, 2, (31, 27), 0, None, 255, 'ssdlb', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9\xa9\xb1', None, 1005, 2, (117, 37), 0, None, 255, 'wqdlb', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1007, 2, (66, 117), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xb9C\xabL', None, 4470, 1, (194, 36), 0, None, 255, 'yx', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1008, 2, (169, 66), 0, None, 255, 'zhdlb', 0, 0, None, None, None),
            ('\xbb\xaf\xa6\xd1\xa7B', None, 4206, 0, (80, 15), 0, None, 255, 'zlb', 0, 0, None, None, None)] },
    1003: {
        '\xa8\xa6\xabB\xc2\xed': [
            ('\xaa\xfc\xa8}', None, 4210, 0, (152, 38), 0, None, 255, 'al', 0, 0, None, None, None),
            ('\xb5\xf4\xc1_\xa9\xb1', None, 1010, 2, (81, 61), 0, None, 255, 'cfdlb', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (61, 47), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xa8\xa6\xabB\xc2\xed\xb0\xd3\xa4H', None, 4752, 1, (104, 84), 0, None, 255, 'gyzsr', 0, 0, None, None, None),
            ('\xa8\xa6\xabB\xc2\xed\xb0\xd3\xa4H', None, 4764, 1, (46, 40), 0, None, 255, 'gyzsr', 0, 0, None, None, None),
            ('\xa6\xd1\xb9A\xa4\xd2', None, 4114, 1, (21, 8), 0, None, 255, 'lnf', 0, 0, None, None, None),
            ('\xa7\xf5\xae\xb7\xc0Y', None, 4214, 0, (119, 98), 0, None, 255, 'lbt', 0, 0, None, None, None),
            ('\xa7\xf5\xa6\xd1\xba~', None, 4212, 0, (69, 22), 0, None, 255, 'llh', 0, 0, None, None, None),
            ('\xa7\xf5\xb1C\xb1C', None, 4211, 0, (120, 20), 0, None, 255, 'lpp', 0, 0, None, None, None),
            ('\xad\xba\xb9\xa2\xa9\xb1', None, 1064, 2, (96, 68), 0, None, 255, 'ssdlb', 0, 0, None, None, None),
            ('\xb5L\xa9\xc0\xa9M\xa9|', None, 4213, 0, (16, 58), 0, None, 255, 'wlhs', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9\xa9\xb1', None, 1009, 2, (74, 97), 0, None, 255, 'wqdlb', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1011, 2, (140, 59), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1012, 2, (92, 101), 0, None, 255, 'zhdlb', 0, 0, None, None, None)] },
    1004: {
        '\xb2M\xb7\xcb\xa5\xad\xad\xec': [
            ('\xacy\xae\xf6\xa1P\xa4P\xa4\xfa', None, 4321, 0, (133, 108), 0, None, 255, 'llt', 0, 0, None, None, None),
            ('\xa4\xfd\xa4G', None, 4298, 0, (108, 18), 0, None, 255, 'we', 0, 0, None, None, None),
            ('\xa4p\xacP', None, 4220, 0, (13, 57), 0, None, 255, 'xx', 0, 0, None, None, None),
            ('\xa4p\xa4\xeb', None, 4221, 0, (13, 50), 0, None, 255, 'xy', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (106, 48), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1005: {
        '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec': [
            ('\xb7R\xc5\xda\xabL\xa4h', None, 0, 1, (16, 65), 0, None, 255, 'alxs', 0, 0, None, None, None),
            ('\xa4\xeb\xa9]\xa5\xfd\xa5\xcd', None, 0, 1, (111, 106), 0, None, 255, 'yyxs', 0, 0, None, None, None)] },
    1006: {
        '\xb7s\xa4\xeb\xa5\xad\xad\xec': [
            ('\xaaL\xa4p\xb3\xb7', None, 4297, 0, (169, 81), 0, None, 255, 'lxx', 0, 0, None, None, None),
            ('\xaaL\xa4p\xabB', None, 4296, 0, (99, 42), 0, None, 255, 'lxy', 0, 0, None, None, None),
            ('\xabC\xb7\xcf\xa1P\xb3\xb7\xa4\xf6', None, 4318, 0, (99, 100), 0, None, 255, 'qyt', 0, 0, None, None, None),
            ('\xd6\xdf\xa4g\xc4q\xa6\xd1\xc1\xf3', None, 4136, 1, (69, 47), 0, None, 255, 'ntklb', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (41, 108), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1007: {
        '\xad\xbb\xb8\xad\xab\xb0': [
            ('\xc2\\\xc5u\xb0\xcf\xb6\xc7\xb0e\xa4H', None, 4992, 1, (66, 84), 0, None, 255, 'btqcsr', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (59, 49), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xa8\xae\xa5\xed', None, 2005, 1, (10, 8), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xb3\xaf\xa6\xca\xb8U', None, 4260, 0, (24, 77), 0, None, 255, 'cbw', 0, 0, None, None, None),
            ('\xc5@\xaaL\xaa\xf8\xa6\xd1', None, 4330, 0, (85, 61), 0, None, 255, 'hlzl', 0, 0, None, None, None),
            ('\xba\xf1\xaeV', None, 4288, 0, (20, 22), 0, None, 255, 'lj', 0, 0, None, None, None),
            ('\xbf\xfa\xb2\xf8', None, 4405, 1, (117, 36), 0, None, 255, 'qzlb', 0, 0, '\xbf\xfa\xb2\xf8\xa6\xd1\xc1\xf3', None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xa4\xfd', None, 4259, 0, (102, 63), 0, None, 255, 'tngw', 0, 0, None, None, None),
            ('\xad\xbb\xb8\xad\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (16, 73), 0, None, 255, 'xycsr', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1039, 2, (81, 31), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1040, 2, (52, 25), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1084, 2, (27, 45), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1008: {
        '\xaa\xda\xaf\xf3\xc2\xed': [
            ('\xad\xdc\xaew', None, 4152, 1, (56, 64), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xaa\xda\xaf\xf3\xc2\xed\xb0\xd3\xa4H', None, 0, 1, (56, 20), 0, None, 255, 'fczsr', 0, 0, None, None, None),
            ('\xaa\xda\xaf\xf3\xc2\xed\xb0\xd3\xa4H', None, 0, 1, (150, 59), 0, None, 255, 'fczsr', 0, 0, None, None, None),
            ('\xb3\xa2\xa6\xd1\xa5\xfd\xa5\xcd', None, 4248, 0, (75, 45), 0, None, 255, 'glxs', 0, 0, None, None, None),
            ('\xbc@\xb1\xa1\xa7\xde\xaf\xe0\xb1\xd0\xaev', '\xc6F\xb3q\xa5P\xa4l', 1121, 1, (75, 98), 0, None, 255, 'jqjnxz', 0, 0, '\xc6F\xb3q\xa5P\xa4l', None, None),
            ('\xa6\xd1\xb9A\xa4\xd2', '\xb9A\xa7@\xaa\xab\xba\xd8\xb4\xd3', 4115, 1, (103, 106), 0, None, 255, 'lnf', 0, 0, None, None, None),
            ('\xa7\xf5\xae\xb7\xc0Y', None, 4214, 0, (129, 97), 0, None, 255, 'lbt', 0, 0, None, None, None),
            ('\xa7f\xae\xd1\xa5\xcd', None, 4249, 0, (125, 56), 0, None, 255, 'lss', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1031, 2, (118, 69), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1032, 2, (145, 72), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xa9\xdb\xb8u\xa4j\xa8\xcf', None, 0, 1, (13, 59), 0, None, 255, 'zpds', 0, 0, None, None, None),
            ('\xa9\xdb\xa6\xa1\xad\xab\xb8m\xaa\xcc', '\xb2\xf6\xb9\xa3\xa9y', 4424, 1, (27, 23), 0, None, 255, 'zsczz', 0, 0, '\xb2\xf6\xb9\xa3\xa9y', None, None),
            ('\xa6\xb6\xaf\xe0', None, 4334, 0, (44, 97), 0, None, 255, 'zn', 0, 0, None, None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1087, 2, (41, 39), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1009: {
        '\xa5j\xa4\xec\xaf\xab\xbcq': [
            ('\xaa\xfc\xc0\xe9\xa9h\xaeQ', None, 4253, 0, (9, 35), 0, None, 255, 'acgn', 0, 0, None, None, None),
            ('\xb5\xf4\xc1_\xa9\xb1', None, 1034, 2, (124, 39), 0, None, 255, 'cfdlb', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (150, 100), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xa4j\xb2\xbd\xa5q', None, 4255, 0, (46, 96), 0, None, 255, 'djs', 0, 0, None, None, None),
            ('\xa4u\xb7~\xb0\xcf', None, 4602, 1, (2, 84), 0, None, 255, 'gyqjyr', 0, 0, None, None, None),
            ('\xa5j\xa4\xec\xaf\xab\xbcq\xb0\xd3\xa4H', None, 4756, 1, (37, 80), 0, None, 255, 'gmsmsr', 0, 0, None, None, None),
            ('\xa5j\xa4\xec\xaf\xab\xbcq\xb0\xd3\xa4H', None, 4768, 1, (166, 27), 0, None, 255, 'gmsmsr', 0, 0, None, None, None),
            ('\xad\xba\xb9\xa2\xa9\xb1', None, 1070, 2, (132, 35), 0, None, 255, 'ssdlb', 0, 0, None, None, None),
            ('\xa4\xfd\xa4j\xc2T', None, 4254, 0, (59, 25), 0, None, 255, 'wds', 0, 0, None, None, None),
            ('\xa7\xc5\xb9D\xa4H', None, 4337, 0, (50, 116), 0, None, 255, 'wdr', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9\xa9\xb1', None, 1033, 2, (103, 63), 0, None, 255, 'wqdlb', 0, 0, None, None, None),
            ('\xa4p\xaa\xea', None, 4257, 0, (117, 9), 0, None, 255, 'xh', 0, 0, None, None, None),
            ('\xa4p\xaa\xe1', None, 4258, 0, (179, 125), 0, None, 255, 'xh', 0, 0, None, None, None),
            ('\xa4p\xc0s', None, 4256, 0, (160, 130), 0, None, 255, 'xl', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1035, 2, (71, 44), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xb9C\xabL', None, 4470, 1, (77, 139), 0, None, 255, 'yx', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1036, 2, (58, 39), 0, None, 255, 'zhdlb', 0, 0, None, None, None)] },
    1010: {
        '\xad\xbb\xb8\xad\xc2O\xaaL': [
            ('\xaa\xe1\xcc\xb0\xad\xbb', None, 4301, 0, (45, 108), 0, None, 255, 'hlx', 0, 0, None, None, None),
            ('\xaa\xe1\xa5P\xa4l', None, 4320, 0, (113, 56), 0, None, 255, 'hxz', 0, 0, None, None, None),
            ('\xa4\xfd\xc3\xc4\xaev', None, 4300, 0, (114, 96), 0, None, 255, 'wys', 0, 0, None, None, None),
            ('\xd6\xdf\xa4g\xc4q\xa6\xd1\xc1\xf3', None, 4137, 1, (65, 59), 0, None, 255, 'ntklb', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (106, 21), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1011: {
        '\xba\xf1\xc6W\xaaL\xa6a': [
            ('\xad\xb8\xa4\xd1\xa5P\xa4l', None, 4303, 0, (24, 43), 0, None, 255, 'ftxz', 0, 0, None, None, None),
            ('\xacy\xae\xf6\xa1P\xa4P\xa4\xfa', None, 4321, 0, (149, 47), 0, None, 255, 'llt', 0, 0, None, None, None),
            ('\xc1\xa7\xbe\xf6\xa4\xd2', None, 4302, 0, (151, 108), 0, None, 255, 'xqf', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (159, 22), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1012: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL': [
            ('\xad\xb7\xb6h\xb9\xd0', None, 4316, 0, (71, 26), 0, None, 255, 'fyc', 0, 0, None, None, None),
            ('\xa8~\xa8\xeb\xa1P\xacP\xa4\xeb', None, 4328, 0, (51, 131), 0, None, 255, 'xyl', 0, 0, None, None, None),
            ('\xb3\xe0\xbb\xee\xb0\xad', None, 4345, 0, (231, 31), 0, None, 255, 'shg', 0, 0, None, None, None),
            ('\xb6\xb3\xb8\xcc\xc1\xf7', None, 4317, 0, (222, 123), 0, None, 255, 'yls', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (33, 118), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1013: {
        '\xa4\xd1\xbba\xab\xb0': [
            ('\xa4\xda\xaee\xa8\xe0', None, 4332, 0, (17, 84), 0, None, 255, 'bre', 0, 0, None, None, None),
            ('\xc2\\\xc5u\xb0\xcf\xb6\xc7\xb0e\xa4H', None, 4992, 1, (77, 78), 0, None, 255, 'btqcsr', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (65, 58), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xa8\xae\xa5\xed', None, 2006, 1, (5, 14), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xafT\xaaZ\xa1P\xc2_\xa4\xfa', None, 4338, 0, (114, 30), 0, None, 255, 'lwsz', 0, 0, None, None, None),
            ('\xb0\xa8\xb0\xd1\xb1N', None, 4292, 0, (87, 66), 0, None, 255, 'mcj', 0, 0, None, None, None),
            ('\xbf\xfa\xb2\xf8', None, 4405, 1, (108, 38), 0, None, 255, 'qzlb', 0, 0, '\xbf\xfa\xb2\xf8\xa6\xd1\xc1\xf3', None, None),
            ('\xb2M\xb4P\xb0\xea\xa4\xfd', None, 4269, 0, (110, 75), 0, None, 255, 'qlgw', 0, 0, None, None, None),
            ('\xa4\xd1\xbba\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (36, 71), 0, None, 255, 'tccsr', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1060, 2, (67, 32), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1061, 2, (44, 18), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1085, 2, (29, 35), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1014: {
        '\xb6\xb3\xb3\xb6\xa8\xa6': [
            ('\xaa\xfc\xc0\xe9\xa9h\xaeQ', None, 4253, 0, (93, 38), 0, None, 255, 'acgn', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (27, 81), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xb3f\xaa\xab\xb0\xd3\xa4H', None, 5014, 1, (72, 48), 0, None, 255, 'hwsr', 0, 0, None, None, None),
            ('\xa5\xf4\xb0\xc8\xc3\xec\xab\xfc\xa4\xde', '\xa4\xd1\xbe\xf7\xa6\xd1\xa4H', 4473, 1, (145, 94), 0, None, 255, 'rwlzy', 0, 0, '\xa4\xd1\xbe\xf7\xa6\xd1\xa4H', None, None),
            ('\xa4\xd1\xbf\xef\xa8\xcf\xaa\xcc', '\xa9\xfa\xab\xc2', 4925, 1, (131, 105), 0, None, 255, 't', 0, 0, '\xa9\xfa\xab\xc2', None, None),
            ('\xa8\xb5\xa4s\xa6\xd1\xba~', None, 4265, 0, (145, 79), 0, None, 255, 'xslh', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1052, 2, (149, 33), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb8\xad\xb2\xce\xbb\xe2', None, 4268, 0, (45, 82), 0, None, 255, 'ytl', 0, 0, None, None, None),
            ('\xb9C\xc0\xb8\xb3]\xb8m\xba\xde\xb2z\xad\xfb', None, 4422, 1, (39, 20), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb9C\xabL', 'PK\xa5\xd3\xbd\xd0', 4470, 1, (133, 21), 0, None, 255, 'yx', 0, 0, None, None, None),
            ('\xb6\xb3\xb3\xb6\xa8\xa6\xb0\xd3\xa4H', None, 0, 1, (112, 11), 0, None, 255, 'yqgsr', 0, 0, None, None, None),
            ('\xb6\xb3\xb3\xb6\xa8\xa6\xb0\xd3\xa4H', None, 0, 1, (126, 36), 0, None, 255, 'yqgsr', 0, 0, None, None, None),
            ('\xb6\xb3\xb9C\xb9D\xa4h', None, 4264, 0, (114, 26), 0, None, 255, 'yyds', 0, 0, None, None, None),
            ('\xb0}\xc0\xe7\xa5\\\xc1Z', '\xc2\xed\xc5]\xb1N\xadx', 5011, 1, (125, 49), 0, None, 255, 'zyrw', 50, 45, '\xc2\xed\xc5]\xb1N\xadx', None, None),
            ('\xc2\xbe\xb7~\xa4\xc1\xb4\xab\xa4H', None, 4842, 1, (11, 65), 0, None, 255, 'zyqhr', 0, 0, None, None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1088, 2, (83, 92), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1015: {
        '\xa5\xad\xa6w\xb4\xe4': [
            ('\xb5\xf4\xc1_\xa9\xb1', None, 1055, 2, (70, 118), 0, None, 255, 'cfdlb', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (103, 107), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xa4u\xb7~\xb0\xcf', None, 4603, 1, (156, 119), 0, None, 255, 'gyqjyr', 0, 0, None, None, None),
            ('\xa5\xad\xa6w\xb4\xe4\xb0\xd3\xa4H', None, 4762, 1, (47, 107), 0, None, 255, 'pagsr', 0, 0, None, None, None),
            ('\xa5\xad\xa6w\xb4\xe4\xb0\xd3\xa4H', None, 4774, 1, (161, 51), 0, None, 255, 'pagsr', 0, 0, None, None, None),
            ('\xad\xba\xb9\xa2\xa9\xb1', None, 1073, 2, (64, 113), 0, None, 255, 'ssdlb', 0, 0, None, None, None),
            ('\xa4\xfd\xa6\xd1\xc1\xf3', None, 4266, 0, (190, 67), 0, None, 255, 'wlb', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9\xa9\xb1', None, 1054, 2, (110, 124), 0, None, 255, 'wqdlb', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1056, 2, (58, 71), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xb8\xad\xb2\xce\xbb\xe2', None, 4268, 0, (21, 21), 0, None, 255, 'yzl', 0, 0, None, None, None),
            ('\xae\xef\xa4k\xabL', None, 4267, 0, (95, 69), 0, None, 255, 'ynx', 0, 0, None, None, None),
            ('\xb9C\xabL', None, 4470, 1, (111, 43), 0, None, 255, 'yx', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1057, 2, (130, 105), 0, None, 255, 'zhdlb', 0, 0, None, None, None)] },
    1016: {
        '\xaf\xee\xa6\xd0\xa5b\xaeq': [
            ('\xb3\xaf\xa5|\xae\xfc', None, 4306, 0, (133, 105), 0, None, 255, 'csh', 0, 0, None, None, None),
            ('\xad]\xa6\xa8', None, 4307, 0, (81, 62), 0, None, 255, 'mc', 0, 0, None, None, None),
            ('\xa4\xfd\xaa\xea', None, 4323, 0, (67, 99), 0, None, 255, 'wh', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (25, 95), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1017: {
        '\xa4\xd1\xbba\xb0\xaa\xa6a': [
            ('\xbfp\xa4T\xad\xa6', None, 4322, 0, (72, 118), 0, None, 255, 'msl', 0, 0, None, None, None),
            ('\xabC\xab\xbc', None, 4305, 0, (140, 56), 0, None, 255, 'qy', 0, 0, None, None, None),
            ('\xa5\xdb\xb3f\xad\xa6', None, 4304, 0, (193, 135), 0, None, 255, 'shl', 0, 0, None, None, None),
            ('\xd6\xdf\xa4g\xc4q\xa6\xd1\xc1\xf3', None, 4138, 1, (82, 35), 0, None, 255, 'ntklb', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (51, 135), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1018: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a': [
            ('\xc2\xc3\xa9]\xb2\xde', None, 4313, 0, (128, 80), 0, None, 255, 'cyl', 0, 0, None, None, None),
            ('\xb7\xa1\xbaq', None, 4312, 0, (177, 141), 0, None, 255, 'cg', 0, 0, None, None, None),
            ('\xa6\xd1\xba\xae\xa4\xd2', None, 4975, 1, (81, 22), 0, None, 255, 'lyf', 0, 0, None, None, None),
            ('\xafW\xaa\xe1\xbf\xdf', None, 4326, 0, (40, 52), 0, None, 255, 'lhm', 0, 0, None, None, None),
            ('\xc6F\xad\xb7\xb6\xf0\xa6u\xc5@\xa4H', None, 4484, 1, (135, 18), 0, None, 255, 'lftshr', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (26, 28), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1019: {
        '\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5': [
            ('\xc2\\\xc5u\xb0\xcf\xb6\xc7\xb0e\xa4H', None, 4992, 1, (76, 68), 0, None, 255, 'btqcsr', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (60, 48), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xb2\xee\xa4\xd2', None, 2007, 1, (18, 18), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xae\xfc\xa9\xb3\xaf\xab\xb7\xb5\xb0\xd3\xa4H', None, 0, 1, (15, 62), 0, None, 255, 'hdsdsr', 0, 0, None, None, None),
            ('\xb2V\xb2V\xaa\xfc\xa4C', None, 4245, 0, (110, 31), 0, None, 255, 'hhaq', 0, 0, None, None, None),
            ('\xa5[\xac\xa5\xb0\xea\xa4\xfd', None, 4242, 0, (114, 70), 0, None, 255, 'jlgw', 0, 0, None, None, None),
            ('\xa4F\xb5M\xa9M\xa9|', None, 4246, 0, (89, 60), 0, None, 255, 'lrhs', 0, 0, None, None, None),
            ('\xbf\xfa\xb2\xf8', None, 4405, 1, (18, 78), 0, None, 255, 'qzlb', 0, 0, '\xbf\xfa\xb2\xf8\xa6\xd1\xc1\xf3', None, None),
            ('\xc3\xc4\xa9\xb1', None, 1027, 2, (57, 28), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb3\xbd\xa4H\xa4\xbd\xa5D', None, 4243, 0, (33, 67), 0, None, 255, 'yrgz', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1028, 2, (25, 14), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1086, 2, (23, 33), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1020: {
        '\xaf[\xbc\xfe\xb4\xe4': [
            ('\xb5\xf4\xc1_\xa9\xb1', None, 1018, 2, (87, 58), 0, None, 255, 'cfdlb', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (91, 101), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xa5\xb4\xba\xae\xa6\xd1\xb1i', None, 4229, 0, (81, 22), 0, None, 255, 'dylz', 0, 0, None, None, None),
            ('\xa7\xf9\xa4\xbd\xa4l', None, 4231, 0, (48, 73), 0, None, 255, 'dgz', 0, 0, None, None, None),
            ('\xa6\xd1\xb9A\xa4\xd2', None, 4117, 1, (17, 57), 0, None, 255, 'lnf', 0, 0, None, None, None),
            ('\xaf[\xbc\xfe\xb4\xe4\xb0\xd3\xa4H', None, 4758, 1, (58, 88), 0, None, 255, 'llxsr', 0, 0, None, None, None),
            ('\xaf[\xbc\xfe\xb4\xe4\xb0\xd3\xa4H', None, 4770, 1, (101, 45), 0, None, 255, 'llxsr', 0, 0, None, None, None),
            ('\xad\xba\xb9\xa2\xa9\xb1', None, 1066, 2, (97, 66), 0, None, 255, 'ssdlb', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9\xa9\xb1', None, 1017, 2, (38, 48), 0, None, 255, 'wqdlb', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1019, 2, (119, 49), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1020, 2, (67, 59), 0, None, 255, 'zhdlb', 0, 0, None, None, None),
            ('\xac\xc3\xaf]\xbei\xb4\xde\xa4H', None, 4135, 1, (47, 32), 0, None, 255, 'zzyzr', 0, 0, None, None, None),
            ('\xa9P\xa4p\xa5\xc9', None, 4230, 0, (129, 86), 0, None, 255, 'zxy', 0, 0, None, None, None)] },
    1021: {
        '\xacP\xc1\xf7\xab\xb0': [
            ('\xaa\xfc\xa4\xeb\xa9h\xaeQ', None, 4234, 0, (125, 16), 0, None, 255, 'aygn', 0, 0, None, None, None),
            ('\xb5\xf4\xc1_\xa9\xb1', None, 1022, 2, (101, 93), 0, None, 255, 'cfdlb', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (88, 84), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xa4u\xb7~\xb0\xcf', None, 4604, 1, (12, 31), 0, None, 255, 'gyqjyr', 0, 0, None, None, None),
            ('\xad\xba\xb9\xa2\xa9\xb1', None, 1067, 2, (80, 93), 0, None, 255, 'ssdlb', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9\xa9\xb1', None, 1021, 2, (129, 58), 0, None, 255, 'wqdlb', 0, 0, None, None, None),
            ('\xa4p\xa5V\xa4l', None, 4235, 0, (149, 115), 0, None, 255, 'xdz', 0, 0, None, None, None),
            ('\xacP\xc1\xf7\xab\xb0\xb0\xd3\xa4H', None, 4759, 1, (82, 42), 0, None, 255, 'xscsr', 0, 0, None, None, None),
            ('\xacP\xc1\xf7\xab\xb0\xb0\xd3\xa4H', None, 4771, 1, (40, 129), 0, None, 255, 'xscsr', 0, 0, None, None, None),
            ('\xbfP\xc4\xe5\xad\xb8', None, 4233, 0, (125, 144), 0, None, 255, 'yyf', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1023, 2, (54, 76), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xb9C\xabL', None, 4470, 1, (170, 128), 0, None, 255, 'yx', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1024, 2, (115, 38), 0, None, 255, 'zhdlb', 0, 0, None, None, None),
            ('\xbd\xde\xad\xbe\xa4p\xb3\xb3', None, 4232, 0, (92, 23), 0, None, 255, 'zgxt', 0, 0, None, None, None)] },
    1022: {
        '\xb8\xa8\xa4\xe9\xae\xfc\xc6W': [
            ('\xb2\xee\xa4\xd2', None, 2008, 1, (31, 100), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xab\xb8\xbfA\xae\xfc', None, 4309, 0, (78, 12), 0, None, 255, 'jzh', 0, 0, None, None, None),
            ('\xabC\xb7\xcf\xa1P\xb3\xb7\xa4\xf6', None, 4318, 0, (145, 105), 0, None, 255, 'qyt', 0, 0, None, None, None),
            ('\xad\xf0\xb9\xda\xc2\xf7', None, 4308, 0, (81, 58), 0, None, 255, 'tml', 0, 0, None, None, None),
            ('\xa4\xfd\xc3\xc4\xaev', None, 4300, 0, (16, 69), 0, None, 255, 'wys', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (20, 87), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1023: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4': [
            ('\xc0\xb0\xac\xa3\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 4655, 1, (145, 98), 0, None, 255, 'bpjnjs', 0, 0, None, None, None),
            ('\xb2\xee\xa4\xd2', None, 2013, 1, (67, 31), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xbcz\xa9\xfa\xc1I\xaev', None, 4314, 0, (104, 88), 0, None, 255, 'hmcs', 0, 0, None, None, None),
            ('\xa6\xd1\xba\xae\xa4\xd2', None, 0, 1, (44, 45), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xc0O\xbbn\xa1P\xc2O\xaaL\xaf\xb5\xbby', None, 4327, 0, (149, 57), 0, None, 255, 'nst', 0, 0, None, None, None),
            ('\xb6\xad\xad\xe2\xbe]', None, 4315, 0, (59, 42), 0, None, 255, 'ylx', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (130, 40), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1024: {
        '\xacy\xa5\xfa\xaeq': [
            ('\xbc\xe9\xa6\xc1\xc3\xc9', None, 4325, 0, (145, 83), 0, None, 255, 'cxx', 0, 0, None, None, None),
            ('\xadJ\xaa\xf7\xa4M', None, 4311, 0, (61, 57), 0, None, 255, 'hjd', 0, 0, None, None, None),
            ('\xd1\xe1\xc1\xf8\xba\xd1', None, 4310, 0, (184, 104), 0, None, 255, 'qxb', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (150, 27), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1025: {
        '\xb2M\xad\xb7\xa7\xf8': [
            ('\xad\xdc\xaew', None, 4152, 1, (107, 80), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xa8\xae\xa5\xed', None, 2001, 1, (175, 142), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa7\xf8\xaa\xf8', None, 3021, 0, (35, 123), 0, None, 255, 'cz', 0, 0, None, None, None),
            ('\xc2I\xa5d\xb1H\xb0\xe2\xa4H', None, 4140, 1, (67, 18), 0, None, 255, 'dkjsr', 0, 0, None, None, None),
            ('\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1101, 1, (45, 71), 0, None, 255, 'zdjnds', 0, 0, None, None, None),
            ('\xbe|\xa4j\xc2T', None, 4202, 0, (157, 42), 0, None, 255, 'lds', 0, 0, None, None, None),
            ('\xbe|\xa4p\xa8\xa9', None, 4204, 0, (145, 22), 0, None, 255, 'lxb', 0, 0, None, None, None),
            ('\xad\xb9\xab~\xa9\xb1', None, 4187, 2, (173, 59), 0, None, 255, 'spdlb', 0, 0, None, None, None),
            ('\xa4\xfd\xae\xb7\xc0Y', None, 4347, 0, (56, 119), 0, None, 255, 'wbt', 0, 0, None, None, None),
            ('\xb7s\xa4\xe2\xab\xfc\xbe\xc9\xad\xfb', None, 4495, 1, (77, 64), 0, None, 255, 'xszdy', 0, 0, None, None, None),
            ('\xa9\xaf\xb9B\xa4p\xa8\xdf', None, 0, 1, (25, 105), 0, None, 255, 'xyxt', 20, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (102, 127), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1004, 2, (130, 132), 0, None, 255, 'zhdlb', 0, 0, None, None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1081, 2, (70, 129), 0, None, 255, 'zbdlb', 0, 0, None, None, None)] },
    1026: {
        '\xbe\xa4\xa9\xfa\xc2\xed': [
            ('\xa6\xe3\xcc\xf5\xad\xeb\xa1P\xb2\xe2\xad\xb7', None, 5006, 0, (22, 60), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xa4K\xa8\xf6\xa9v\xaev', '\xa4\xd1\xa4\xb8\xa4l', 4953, 1, (86, 59), 0, None, 255, 'bgzqlzr', 0, 0, '\xa4\xd1\xa4\xb8\xa4l', None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (41, 53), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xba\xd9\xbf\xd7\xbb\xe2\xa8\xfa\xa4H', '\xb3\xd5\xb3\xae\xabJ', 4876, 1, (102, 44), 0, None, 255, 'cwlqr', 0, 0, '\xb3\xd5\xb3\xae\xabJ', None, None),
            ('\xbe\xa4\xa9\xfa\xc2\xf8\xb3f\xb0\xd3', None, 1008, 2, (67, 40), 0, None, 255, 'lmzhs', 0, 0, None, None, None),
            ('\xa4d\xb7\xcb\xaf\xbe\xa1P\xad\xb7\xbbR', None, 4340, 0, (39, 66), 0, None, 255, 'tzs', 0, 0, None, None, None),
            ('\xa4\xd1\xb0\xae', '\xa4\xd1\xac\xc9\xb6\xc7\xb0e\xa4H', 4919, 1, (89, 19), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xa6\xe8\xa4i\xa1P\xc2O\xaaL\xaf\xb5\xbby', None, 4341, 0, (64, 57), 0, None, 255, 'tys', 0, 0, None, None, None),
            ('\xc1\xa8\xc1\xa8\xa6w\xa1P\xa8\xaa\xc0\xfb', None, 4339, 0, (40, 31), 0, None, 255, 'tw', 0, 0, None, None, None),
            ('\xb2\xe2\xad\xb7\xa1P\xbc\xb3\xae\xd2', '\xb9D\xa8\xe3\xb8\xd1\xb8j', 4478, 1, (99, 65), 0, None, 255, 'lfps', 0, 0, None, None, None)] },
    1027: {
        '\xa9]\xb9\xf5\xc2\xed': [
            ('\xaa\xfc\xaf\xaa\xb5\xdc\xa1P\xacP\xa4\xeb', '\xc4_\xa5\xdb\xbaK\xb0\xa3', 4918, 1, (24, 60), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (33, 38), 0, None, 255, 'c', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xafP\xb6\xa7\xbeW\xa1P\xa6\xe5\xa4\xfa', None, 4342, 0, (32, 19), 0, None, 255, 'lw', 0, 0, None, None, None),
            ('\xafP\xb6\xa7\xbe\xd4\xafT\xa1P\xa6\xe5\xa4\xfa', None, 5007, 0, (75, 67), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xaf\xab\xbe\xb9\xc1\xeb\xb3y\xa4H', '\xaf}\xb0}\xa4l', 4921, 1, (64, 37), 0, None, 255, 's', 0, 0, '\xaf}\xb0}\xa4l', None, None),
            ('\xb6\xb6\xa4\xd1\xa1P\xc1\xfc\xad\xb7', None, 4343, 0, (93, 16), 0, None, 255, 'znljj', 0, 0, None, None, None),
            ('\xa4\xd1\xb0\xae', '\xa4\xd1\xac\xc9\xb6\xc7\xb0e\xa4H', 4919, 1, (20, 15), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xa7\xa4\xc3M\xa8\xcf\xaa\xcc', '\xa7\xa4\xc3M\xbb\xe2\xa8\xfa\xa4H', 4882, 1, (45, 40), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1028: {
        '\xaa\xf8\xad\xb7\xaeq': [
            ('\xbf\xfa\xa8q\xa4~', None, 4348, 0, (63, 57), 0, None, 255, 'qxc', 0, 0, None, None, None)] },
    1029: {
        '\xafe\xad\xb7\xa8\xa6': [
            ('\xa4\xbb\xb9D\xafu\xa7g', None, 0, 1, (24, 62), 0, None, 255, 'ldzj', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (100, 47), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1030: {
        '\xb4H\xa4\xeb\xb4\xcb\xaaL': [
            ('\xad\xd3\xa4H\xa4\xdf\xaak\xb1\xd0\xaev', None, 4858, 1, (125, 56), 0, None, 255, 'g', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (152, 25), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1031: {
        '\xbcv\xafT\xad\xec': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (170, 25), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1032: {
        '\xb8H\xb9\xda\xc0\xad': [
            ('\xad\xd3\xa4H\xa4\xdf\xaak\xb1\xd0\xaev', '\xa4\xb8\xc6F\xb9C\xa5P', 4858, 1, (82, 23), 0, None, 255, 'g', 0, 0, '\xa4\xb8\xc6F\xb9C\xa5P', None, None),
            ('\xacP\xa8\xcf', '\xacP\xac\xc9\xa4Q\xa4G\xaec\xa5\xf4\xb0\xc8', 4885, 1, (181, 125), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xbe\xd4\xbeW\xa1P\xacP\xa4\xeb', None, 4344, 0, (101, 69), 0, None, 255, 'pxljj', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (45, 25), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1033: {
        '\xaa\xf7\xba\xf1\xa8F\xacw': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (191, 45), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1034: {
        '\xad\xd7\xc3\xb9\xb4\xcb\xaaL': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (233, 51), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1036: {
        '\xac\xc0\xb7\xe4\xb0g\xaec1': [
            ('\xb2M\xad\xb7\xa7\xf8\xb6\xc7\xb0e\xa4H', None, 4480, 1, (71, 49), 0, None, 255, 'rg', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (24, 61), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1039: {
        '\xc6F\xa5\xdb\xb6\xf01\xbch': [
            ('\xafP\xb5K\xb0\xad', None, 4346, 0, (42, 28), 0, None, 255, 'lyg', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (25, 15), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1040: {
        '\xc6F\xa5\xdb\xb6\xf02\xbch': [
            ('\xbd\xe6\xae\xd1\xa4p\xb3c', None, 4419, 1, (65, 48), 0, None, 255, 'msxf', 0, 0, None, None, None)] },
    1043: {
        '\xa5j\xa4\xec\xb2\xbd\xbe\xc21\xbch': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (74, 72), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1049: {
        '\xa8F\xbaz\xb0g\xaec\xa4@\xbch': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (128, 33), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1051: {
        '\xa8F\xbaz\xb0g\xaec': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (127, 26), 0, None, 255, 'zdjjr', 0, 0, None, None, None),
            ('\xad\xdf\xa7\xaf\xadx\xb9\xce\xa5\xaa\xb2\xce\xbb\xe2', None, 4844, 1, (93, 50), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1054: {
        '\xa9\xfa\xa4\xeb\xab\xb0': [
            ('\xc0\xb0\xac\xa3\xc1`\xba\xde', None, 4651, 1, (324, 149), 0, None, 255, 'bpzg', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4', None, 0, 1, (332, 138), 0, None, 255, 'gzjy', 0, 60, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb0\xea\xbe\xd4', None, 0, 1, (332, 138), 0, None, 255, 'gzjy', 0, 0, None, None, None),
            ('\xc4_\xb9\xcf\xa5\xf4\xb0\xc8', '\xb9C\xa4\xe8\xb9D\xa4h', 4171, 1, (129, 86), 0, None, 255, 'yfds', 18, 0, '\xb9C\xa4\xe8\xb9D\xa4h', None, None),
            ('\xc4_\xaa\xab\xa9\xe7\xbd\xe6', '\xaa\xf7\xc1`\xba\xde', 4920, 1, (260, 205), 0, None, 255, 'b', 0, 0, '\xaa\xf7\xc1`\xba\xde', None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (135, 129), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xbcp\xaf\xab\xa5\xf4\xb0\xc8', '\xad\xb9\xc3\xd0\xa7I\xb4\xab', 4190, 1, (260, 41), 0, None, 255, 'cs', 0, 0, '\xad\xb9\xc3\xd0', None, None),
            ('\xb0\xa3\xc5]\xa5\xf4\xb0\xc8', '\xb0\xa3\xc5]\xaev', 3017, 1, (241, 171), 0, None, 255, 'cms', 0, 0, '\xb0\xa3\xc5]\xaev', None, None),
            ('\xb0\xc6\xa5\xbb\xb1\xb5\xa4\xde', '\xac\xef\xa6\xe6\xaa\xcc', 4991, 1, (200, 164), 0, None, 255, 'fbjy', 30, 0, '\xac\xef\xa6\xe6\xaa\xcc', None, None),
            ('\xa4u\xb7~\xb0\xcf', None, 4601, 1, (319, 170), 0, None, 255, '', 0, 0, '\xa4u\xb7~\xb0\xcf\xb1\xb5\xa4\xde\xa4H', None, None),
            ('\xa4u\xc3\xc0\xaev', None, 4563, 1, (62, 82), 0, None, 255, 'gys', 0, 0, None, None, None),
            ('\xac\xf5\xaeQ', None, 4440, 1, (105, 215), 0, None, 255, 'hn', 20, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xa8\xcf\xaa\xcc', '\xa5j\xa4\xec\xa4\xfa', 1001, 1, (238, 145), 0, None, 255, 'hdsz', 0, 0, '\xa5j\xa4\xec\xa4\xfa', None, None),
            ('\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1104, 1, (31, 159), 0, None, 255, 'jnjs', 0, 0, None, None, None),
            ('\xb3\xc3\xa8\xe3\xaev', None, 4561, 1, (79, 79), 0, None, 255, 'jjs', 0, 0, None, None, None),
            ('\xc5\xb3\xa9w\xaev', None, 4104, 1, (14, 76), 0, None, 255, 'jds', 0, 0, None, None, None),
            ('\xa5\xe6\xa9\xf6\xc1`\xba\xde', None, 4406, 1, (64, 134), 0, None, 255, 'jysh', 0, 0, '\xa5\xe6\xa9\xf6\xc1`\xba\xde', None, None),
            ('\xb5\xb2\xab\xf4\xa8\xcf\xaa\xcc', '\xb8q\xa4d\xbb\xa8', 4831, 1, (67, 202), 0, None, 255, 'j', 0, 0, '\xb8q\xa4d\xbb\xa8', None, None),
            ('\xba\xeb\xab~\xa5\xe6\xa9\xf6', '\xb8U\xba\xd6', 4968, 1, (103, 130), 0, None, 255, 'tjjyg', 0, 0, '\xb8U\xba\xd6', None, None),
            ('\xa9~\xa5\xc1\xb0\xcf', None, 4501, 1, (332, 126), 0, None, 255, '', 0, 0, '\xa9~\xa5\xc1\xb0\xcf\xb1\xb5\xa4\xde\xa4H', None, None),
            ('\xb3\xd2\xb0\xc8\xa4\xa4\xa4\xb6', '\xc5\xe9\xa4O\xa5\xb4\xa4u', 4451, 1, (20, 152), 0, None, 255, 'lwzjr', 0, 0, '\xb3\xd2\xb0\xc8\xa4\xa4\xa4\xb6\xa4H', None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (302, 111), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xc2\xa7\xa5]\xba\xeb\xc6F', None, 4982, 1, (178, 27), 0, None, 255, 'lbjl', 12, 0, None, None, None),
            ('\xc2\xa7\xaa\xab\xa5P\xa4l', '\xb8`\xa4\xe9\xc2\xa7\xaa\xab\xbb\xe2\xa8\xfa\xa4H', 4410, 1, (201, 45), 0, None, 255, 'lwxz', 20, 0, None, None, None),
            ('\xbb\xe2\xbbR', None, 4820, 1, (326, 110), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (105, 164), 0, None, 255, 'mycsr', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (213, 209), 0, None, 255, 'mycsr', 0, 0, None, None, None),
            ('\xac\xe8\xba\xd6', '\xaaF\xa4\xe8\xae\xd2', 4839, 1, (299, 67), 0, None, 255, 's', 0, 0, '\xaaF\xa4\xe8\xae\xd2', None, None),
            ('\xbf\xfa\xb9\xda\xb1g', None, 4349, 0, (240, 215), 0, None, 255, 'qma', 0, 0, None, None, None),
            ('\xaf\xab\xaf\xb5\xa4H', None, 4830, 1, (299, 26), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xaf\xab\xc3~\xa4p\xad\xb8\xbd\xde', '\xaf\xab\xc3~\xa5P\xc3~\xb6i\xad\xd7', 4460, 1, (186, 183), 0, None, 255, 'ssxfz', 30, 0, None, None, None),
            ('\xaev\xae{\xba\xde\xb2z', '\xab\xf4\xaev\xa4\xce\xbe\xc7\xae{\xa5\xf4\xb0\xc8', 4981, 1, (262, 159), 0, None, 255, 'bpxtzyr', 0, 0, '\xc0\xb0\xac\xa3\xbe\xc7\xae{\xab\xfc\xa4\xde\xa4H', None, None),
            ('\xad\xb9\xab~\xa9\xb1', None, 4187, 2, (179, 78), 0, None, 255, 'spd', 0, 0, '\xad\xb9\xab~\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xa5|\xb0\xea\xb6\xc7\xb0e\xa4H', '\xb2\xee\xa4\xd2', 2003, 1, (215, 26), 0, None, 255, 'sgcsr', 0, 0, '\xb2\xee\xa4\xd2', None, None),
            ('\xa4\xd1\xbf\xef\xa8\xcf\xaa\xcc', '\xa9\xfa\xab\xc2', 4925, 1, (223, 180), 0, None, 255, 't', 0, 0, '\xa9\xfa\xab\xc2', None, None),
            ('\xc5K\xa6K', None, 4183, 1, (17, 89), 0, None, 255, 'tj', 0, 0, None, None, None),
            ('\xb9\xcf\xc5\xb3\xa5\xf4\xb0\xc8', '\xb8\xad\xa6\xd0\xb4M', 4978, 1, (129, 56), 0, None, 255, 'tjyjy', 32, 0, '\xb8\xad\xa6\xd0\xb4M', None, None),
            ('\xaa\xb1\xaea\xa4\xa7\xaea', '\xa8\xae\xa5\xed', 4509, 1, (259, 74), 0, None, 255, 'cf', 0, 0, '\xa8\xae\xa5\xed', None, None),
            ('\xaa\xab\xab~\xb0\xd3\xb7|', None, 4498, 1, (47, 111), 0, None, 255, '', 0, 45, '\xaa\xab\xab~\xa9\xb1\xc1`\xba\xde', None, None),
            ('\xad\xd7\xb7\xd2\xa5\xf4\xb0\xc8', '\xad\xd7\xb7\xd2\xab\xfc\xbe\xc9\xa4H', 4810, 1, (294, 132), 0, None, 255, 'x', 30, 0, '\xad\xd7\xb7\xd2\xab\xfc\xbe\xc9\xa4H', None, None),
            ('\xbf\xef\xac\xfc', '\xa6w\xb3\xb7\xba\xbd', 4801, 1, (131, 160), 0, None, 255, 's', 0, 0, '\xa6w\xb3\xb7\xba\xbd', None, None),
            ('\xb7\xcf\xaa\xe1\xa8\xcf\xaa\xcc', '\xa4\xf5\xbbR', 0, 1, (123, 221), 0, None, 255, 'h', 20, 0, '\xa4\xf5\xbbR', None, None),
            ('\xc3\xc4\xa7\xf7\xb0\xd3\xa4H', None, 4442, 1, (15, 140), 0, None, 255, 'ycsr', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1078, 2, (244, 68), 0, None, 255, 'ydlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb6l\xacF\xa4\xa4\xa4\xdf', None, 4452, 1, (279, 81), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb9B\xc3\xf0\xa5\xf4\xb0\xc8', '\xb6\xb5\xc3\xf0\xaev', 4485, 1, (250, 107), 0, None, 255, 'ybrw', 30, 0, '\xb6\xb5\xc3\xf0\xaev', None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1079, 2, (223, 69), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb3y\xab\xac\xaev', None, 4191, 1, (82, 172), 0, None, 255, 'rss', 0, 0, None, None, None),
            ('\xbe\xd4\xb6\xa4\xa8\xcf\xaa\xcc', '\xb5L\xc2\xf9', 5025, 1, (30, 200), 0, None, 255, 'z', 0, 0, '\xb5L\xc2\xf9', None, None),
            ('\xa5l\xb3\xea\xc3~\xb7\xd2\xa7\xaf', '\xa5P\xacy\xb9D\xa4H', 4102, 1, (190, 108), 0, None, 255, 'xldr', 0, 0, '\xa5P\xacy\xb9D\xa4H', None, None),
            ('\xa4\xe4\xbdu\xa5\xf4\xb0\xc8', '\xaa\xf7\xa4j\xa6\xb3', 4333, 1, (208, 103), 0, None, 255, 'jdy', 0, 0, '\xaa\xf7\xa4j\xa6\xb3', None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1082, 2, (198, 72), 0, None, 255, 'zbdlb', 0, 0, None, None, None)] },
    1055: {
        '\xa9\xfa\xa4\xeb\xab\xb0': [
            ('\xc0\xb0\xac\xa3\xbe\xc7\xae{', '\xbe\xc7\xae{\xa5\xf4\xb0\xc8\xbb\xe2\xa8\xfa\xa4H', 3029, 1, (262, 159), 0, None, 255, 'bpxtzyr', 0, 0, '\xc0\xb0\xac\xa3\xbe\xc7\xae{\xab\xfc\xa4\xde\xa4H', None, None),
            ('\xc0\xb0\xac\xa3\xc1`\xba\xde', None, 4651, 1, (324, 149), 0, None, 255, 'bpzg', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb0\xea\xbe\xd4', None, 0, 1, (332, 138), 0, None, 255, 'gzjy', 0, 0, None, None, None),
            ('\xc4_\xb9\xcf\xa5\xf4\xb0\xc8', '\xb9C\xa4\xe8\xb9D\xa4h', 4171, 1, (129, 86), 0, None, 255, 'yfds', 18, 0, '\xb9C\xa4\xe8\xb9D\xa4h', None, None),
            ('\xc4_\xaa\xab\xa9\xe7\xbd\xe6', '\xaa\xf7\xc1`\xba\xde', 4920, 1, (260, 205), 0, None, 255, 'b', 20, 55, '\xaa\xf7\xc1`\xba\xde', None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (135, 129), 0, None, 255, 'ck', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xbcp\xaf\xab\xa5\xf4\xb0\xc8', '\xad\xb9\xc3\xd0\xa7I\xb4\xab', 4190, 1, (260, 41), 0, None, 255, 'cs', 0, 0, None, None, None),
            ('\xb0\xa3\xc5]\xa5\xf4\xb0\xc8', '\xb0\xa3\xc5]\xaev', 3017, 1, (241, 171), 0, None, 255, 'cms', 0, 0, '\xb0\xa3\xc5]\xaev', None, None),
            ('\xb0\xc6\xa5\xbb\xb1\xb5\xa4\xde', '\xac\xef\xa6\xe6\xaa\xcc', 0, 1, (200, 164), 0, None, 255, 'fbjy', 30, 0, '\xac\xef\xa6\xe6\xaa\xcc', None, None),
            ('\xa4u\xb7~\xb0\xcf', None, 4601, 1, (319, 170), 0, None, 255, '', 0, 0, '\xa4u\xb7~\xb0\xcf\xb1\xb5\xa4\xde\xa4H', None, None),
            ('\xa4u\xc3\xc0\xaev', None, 4563, 1, (62, 82), 0, None, 255, 'gys', 0, 0, None, None, None),
            ('\xac\xf5\xaeQ', None, 4440, 1, (105, 215), 0, None, 255, 'hn', 25, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xa8\xcf\xaa\xcc', '\xa5j\xa4\xec\xa4\xfa', 1001, 1, (238, 145), 0, None, 255, 'hdsz', 0, 0, '\xa5j\xa4\xec\xa4\xfa', None, None),
            ('\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1104, 1, (31, 159), 0, None, 255, 'jnjs', 0, 0, None, None, None),
            ('\xb3\xc3\xa8\xe3\xaev', None, 4561, 1, (79, 79), 0, None, 255, 'jjs', 0, 0, None, None, None),
            ('\xc5\xb3\xa9w\xaev', None, 4104, 1, (14, 76), 0, None, 255, 'jds', 0, 0, None, None, None),
            ('\xa5\xe6\xa9\xf6\xc1`\xba\xde', None, 4406, 1, (64, 134), 0, None, 255, 'jysh', 0, 0, None, None, None),
            ('\xb5\xb2\xab\xf4\xa8\xcf\xaa\xcc', '\xb8q\xa4d\xbb\xa8', 4831, 1, (67, 202), 0, None, 255, 'j', 0, 55, '\xb8q\xa4d\xbb\xa8', None, None),
            ('\xaa\xf7\xa4j\xa6\xb3', '\xa4\xe4\xbdu\xa5\xf4\xb0\xc8\xbb\xe2\xa8\xfa\xa4H', 4333, 0, (208, 103), 0, None, 255, 'jdy', 0, 0, None, None, None),
            ('\xba\xeb\xab~\xa5\xe6\xa9\xf6', '\xb8U\xba\xd6', 4968, 1, (103, 130), 0, None, 255, 'tjjyg', 0, 0, '\xb8U\xba\xd6', None, None),
            ('\xa9~\xa5\xc1\xb0\xcf', None, 4501, 1, (332, 126), 0, None, 255, '', 0, 0, '\xa9~\xa5\xc1\xb0\xcf\xb1\xb5\xa4\xde\xa4H', None, None),
            ('\xb3\xd2\xb0\xc8\xa4\xa4\xa4\xb6', '\xc5\xe9\xa4O\xa5\xb4\xa4u', 4451, 1, (20, 152), 0, None, 255, 'lwzjr', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (302, 111), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xc2\xa7\xa5]\xba\xeb\xc6F', None, 4982, 1, (178, 27), 0, None, 255, 'lbjl', 12, 0, None, None, None),
            ('\xc2\xa7\xaa\xab\xa5P\xa4l', '\xb8`\xa4\xe9\xc2\xa7\xaa\xab\xbb\xe2\xa8\xfa\xa4H', 4410, 1, (201, 45), 0, None, 255, 'lwxz', 20, 0, None, None, None),
            ('\xbb\xe2\xbbR', None, 4820, 1, (326, 110), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (105, 164), 0, None, 255, 'mycsr', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb0\xd3\xa4H', None, 0, 1, (213, 209), 0, None, 255, 'mycsr', 0, 0, None, None, None),
            ('\xbf\xfa\xb9\xda\xb1g', None, 4349, 0, (240, 215), 0, None, 255, 'qma', 0, 0, None, None, None),
            ('\xaf\xab\xaf\xb5\xa4H', None, 4830, 1, (299, 26), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xaf\xab\xc3~\xa4p\xad\xb8\xbd\xde', '\xaf\xab\xc3~\xa5P\xc3~\xb6i\xad\xd7', 4460, 2, (186, 183), 0, None, 255, 'ssxfz', 30, 0, None, None, None),
            ('\xad\xb9\xab~\xa9\xb1', None, 4187, 2, (179, 78), 0, None, 255, 'spd', 0, 0, '\xad\xb9\xab~\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xa5|\xb0\xea\xb6\xc7\xb0e\xa4H', '\xb2\xee\xa4\xd2', 2003, 1, (215, 26), 0, None, 255, 'sgcsr', 0, 0, None, None, None),
            ('\xba\xe2\xa9R', '\xaaF\xa4\xe8\xae\xd2', 4839, 1, (299, 67), 0, None, 255, 's', 0, 0, '\xaaF\xa4\xe8\xae\xd2', None, None),
            ('\xc5K\xa6K', None, 4183, 1, (17, 89), 0, None, 255, 'tj', 0, 0, None, None, None),
            ('\xb9\xcf\xc5\xb3\xa5\xf4\xb0\xc8', '\xb8\xad\xa6\xd0\xb4M', 4978, 1, (129, 56), 0, None, 255, 'tjyjy', 32, 0, '\xb8\xad\xa6\xd0\xb4M', None, None),
            ('\xaa\xb1\xaea\xa4\xa7\xaea', '\xa8\xae\xa5\xed', 4509, 1, (259, 74), 0, None, 255, 'cf', 0, 0, '\xa8\xae\xa5\xed', None, None),
            ('\xaa\xab\xab~\xb0\xd3\xb7|', None, 4498, 1, (47, 111), 0, None, 255, '', 0, 45, '\xaa\xab\xab~\xa9\xb1\xc1`\xba\xde', None, None),
            ('\xa5P\xacy\xb9D\xa4H', '\xa5l\xb3\xea\xc3~\xb7\xd2\xa7\xaf', 4102, 1, (190, 108), 0, None, 255, 'xldr', 0, 0, None, None, None),
            ('\xad\xd7\xb7\xd2\xa5\xf4\xb0\xc8', '\xad\xd7\xb7\xd2\xab\xfc\xbe\xc9\xa4H', 4810, 1, (294, 132), 0, None, 255, 'x', 32, 0, '\xad\xd7\xb7\xd2\xab\xfc\xbe\xc9\xa4H', None, None),
            ('\xb7\xcf\xaa\xe1\xa8\xcf\xaa\xcc', '\xa4\xf5\xbbR', 0, 1, (123, 221), 0, None, 255, 'h', 20, 0, '\xa4\xf5\xbbR', None, None),
            ('\xc3\xc4\xa7\xf7\xb0\xd3\xa4H', None, 4442, 1, (15, 140), 0, None, 255, 'ycsr', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1078, 2, (244, 68), 0, None, 255, 'ydlb', 0, 0, '\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb2\xbe\xa5\xc1\xa8\xcf\xaa\xcc', None, 0, 1, (181, 216), 0, None, 255, 'ymsz', 0, 0, None, None, None),
            ('\xb6l\xacF\xa4\xa4\xa4\xdf', None, 4452, 1, (276, 80), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa6\xd0\xc6F\xa5P\xa4l', None, 4932, 1, (110, 36), 0, None, 255, 'y', 50, 55, None, None, None),
            ('\xb9B\xc3\xf0\xa5\xf4\xb0\xc8', '\xb6\xb5\xc3\xf0\xaev', 4485, 1, (250, 107), 0, None, 255, 'ybrw', 32, 0, '\xb6\xb5\xc3\xf0\xaev', None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1079, 2, (223, 69), 0, None, 255, 'zhdlb', 0, 0, '\xc2\xf8\xb3f\xa9\xb1\xa6\xd1\xc1\xf3', None, None),
            ('\xb3y\xab\xac\xaev', None, 4191, 1, (82, 172), 0, None, 255, 'rss', 0, 0, None, None, None),
            ('\xbe\xd4\xb6\xa4\xa8\xcf\xaa\xcc', '\xb5L\xc2\xf9', 5025, 1, (30, 200), 0, None, 255, 'z', 0, 0, '\xb5L\xc2\xf9', None, None),
            ('\xb8\xcb\xb3\xc6\xa9\xb1', None, 1082, 2, (198, 72), 0, None, 255, 'zbdlb', 0, 0, '\xb8\xcb\xb3\xc6\xa9\xb1\xa6\xd1\xc1\xf3', None, None)] },
    1060: {
        '\xae\xd1\xa5\xab': [
            ('\xae\xd1\xa5\xab\xb6\xc7\xb0e\xa4H', None, 4445, 1, (57, 42), 0, None, 255, 'sscsr', 0, 0, None, None, None)] },
    1073: {
        '\xc6F\xad\xb7\xb6\xf01\xbch': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (84, 76), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1076: {
        '\xbbR\xb7|\xb7\xc7\xb3\xc6\xc6UA': [
            ('\xbbR\xaa\xcc', None, 4819, 1, (120, 76), 0, None, 255, 'w', 0, 0, None, None, None)] },
    1077: {
        '\xbbR\xb7|\xb7\xc7\xb3\xc6\xc6UB': [
            ('\xbbR\xaa\xcc', None, 4819, 1, (120, 76), 0, None, 255, 'w', 0, 0, None, None, None)] },
    1078: {
        '\xbbR\xb7|\xb7\xc7\xb3\xc6\xc6UC': [
            ('\xbbR\xaa\xcc', None, 4819, 1, (120, 76), 0, None, 255, 'w', 0, 0, None, None, None)] },
    1079: {
        '\xbbR\xc6UA': [
            ('\xad\xdc\xaew', None, 4152, 1, (22, 65), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (33, 78), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbb\xe2\xbbR', None, 4820, 1, (38, 52), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbd\xe6\xb3\xf8\xb5\xa3', None, 4872, 1, (71, 74), 0, None, 255, 'm', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (63, 51), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1078, 2, (66, 36), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1104, 1, (31, 93), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (42, 66), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1080: {
        '\xbbR\xc6UB': [
            ('\xad\xdc\xaew', None, 4152, 1, (22, 65), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (33, 78), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbb\xe2\xbbR', None, 4820, 1, (38, 52), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbd\xe6\xb3\xf8\xb5\xa3', None, 4872, 1, (71, 74), 0, None, 255, 'm', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (63, 51), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1078, 2, (66, 36), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1104, 1, (31, 93), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (42, 66), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1081: {
        '\xbbR\xc6UC': [
            ('\xad\xdc\xaew', None, 4152, 1, (22, 65), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xa6\xbf\xb4\xf2\xa6\xca\xbe\xe5\xa5\xcd', None, 4923, 1, (14, 83), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (33, 78), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbb\xe2\xbbR', None, 4820, 1, (38, 52), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbd\xe6\xb3\xf8\xb5\xa3', None, 4872, 1, (71, 74), 0, None, 255, 'm', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (63, 51), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1078, 2, (66, 36), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1104, 1, (31, 93), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (42, 66), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1084: {
        '\xabn\xbb\xbb\xad\xba\xaeu\xbe\xdd\xa5x': [
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (167, 92), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (111, 93), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (113, 79), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (165, 79), 0, None, 255, 'j', 0, 0, None, None, None)] },
    1085: {
        '\xa4\xd1\xb9\xe7\xad\xba\xaeu\xbe\xdd\xa5x': [
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (167, 92), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (111, 93), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (113, 79), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (165, 79), 0, None, 255, 'j', 0, 0, None, None, None)] },
    1086: {
        '\xb2M\xb4P\xad\xba\xaeu\xbe\xdd\xa5x': [
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (167, 92), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (111, 93), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (113, 79), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (165, 79), 0, None, 255, 'j', 0, 0, None, None, None)] },
    1087: {
        '\xa5[\xac\xa5\xad\xba\xaeu\xbe\xdd\xa5x': [
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 4840, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (167, 92), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (111, 93), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (113, 79), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4840, 1, (165, 79), 0, None, 255, 'j', 0, 0, None, None, None)] },
    1089: {
        '\xb5L\xa8\xfd\xae\xd1\xc2N': [
            ('\xbf\xfa\xb2\xf8\xa6\xd1\xc1\xf3', None, 4505, 1, (27, 37), 0, None, 255, 'q', 0, 0, None, None, None),
            ('\xb5L\xa8\xfd\xa5\xfd\xa5\xcd', None, 4967, 1, (36, 32), 0, None, 255, 'w', 0, 0, None, None, None)] },
    1090: {
        '\xb6\xeb\xafZ\xaeq': [
            ('\xae\xc8\xb9C\xba\xde\xb2z\xad\xfb', None, 0, 1, (116, 70), 0, None, 255, 'l', 0, 0, None, None, None)] },
    1091: {
        '\xac\xa5\xb6\xa7\xab\xb0': [
            ('\xa9s\xa9Z', None, 0, 1, (116, 66), 0, None, 255, 'm', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (49, 43), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1092: {
        '\xb3\\\xa9\xf7\xab\xb0\xad\xa5': [
            ('\xa7\xf9\xbb\xb7', None, 0, 1, (56, 78), 0, None, 255, 'd', 0, 0, None, None, None),
            ('\xa4\xd5\xa8q', None, 0, 1, (21, 106), 0, None, 255, 'k', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (84, 85), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1094: {
        '\xc9\xfa\xa4\xf4\xc3\xf6': [
            ('\xa4\xcb\xb3\xdf', None, 0, 1, (115, 48), 0, None, 255, 'b', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (106, 93), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1095: {
        '\xe2l\xb6\xa7\xab\xb0': [
            ('\xadJ\xafZ', None, 0, 1, (90, 84), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xa4\xfd\xb4\xd3', None, 0, 1, (179, 136), 0, None, 255, 'w', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (130, 105), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1096: {
        '\xb6\xc0\xaae\xb4\xe7\xa4f': [
            ('\xaf\xb3\xb5X', None, 0, 1, (53, 123), 0, None, 255, 'q', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (74, 100), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1097: {
        '\xacy\xb6\xb3\xb1\xda\xb3\xa1\xb8\xa8': [
            ('\xaa\xea\xc0Y\xad\xa9\xaa\xf8', None, 0, 1, (42, 22), 0, None, 255, 'n', 0, 0, None, None, None),
            ('\xa4E\xbe\xa4\xad\xa9\xaa\xf8', None, 0, 1, (105, 50), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xafT\xa4H\xad\xa9\xaa\xf8', None, 0, 1, (30, 84), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xacy\xb6\xb3\xa4j\xb2\xbd\xa5q', None, 0, 1, (93, 54), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xa6\xba\xa4`\xad\xa9\xaa\xf8', None, 0, 1, (139, 30), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xa7l\xa6\xe5\xad\xa9\xaa\xf8', None, 0, 1, (156, 74), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (72, 84), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1098: {
        '\xa4\xf5\xacP': [
            ('\xa6\xe3\xb4\xb5\xaa\xba\xa9\xbe\xa6\xda', None, 0, 1, (42, 42), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xa6w\xaaN\xa1P\xbe\xa4\xa9\xf9', None, 0, 1, (112, 77), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (21, 68), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xa7\xac\xc9\xa4\xa7\xaa\xf9', None, 0, 1, (41, 16), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1099: {
        '\xab\xa2\xa9i\xaf\xc7\xb6\xf0\xaf\xab\xbcq': [
            ('\xaa\xfc\xa7V\xa4\xf1\xb4\xb5\xadx\xb9\xce', None, 0, 1, (68, 18), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xaa\xfc\xa7V\xa4\xf1\xb4\xb5\xadx\xb9\xce', None, 0, 1, (95, 66), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xaa\xfc\xa7V\xa4\xf1\xb4\xb5\xadx\xb9\xce', None, 0, 1, (142, 60), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (14, 49), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xa7\xac\xc9\xa4\xa7\xaa\xf9', None, 0, 1, (56, 88), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1100: {
        '\xb4\xb5\xaa\xe2\xa7J\xb4\xb5\xb0g\xaec': [
            ('\xbb\\\xafS\xaa\xba\xaf\xf0\xb4\xc6\xa4\xa7\xaa\xf9', None, 0, 1, (146, 53), 0, None, 255, 'g', 0, 0, None, None, None),
            ('\xaew\xa7B\xa9\xd4\xaa\xba\xb7N\xa7\xd3', None, 0, 1, (156, 24), 0, None, 255, 'k', 0, 0, None, None, None),
            ('\xb9\xcf\xa5d\xaa\xba\xa4`\xaa\xcc\xa4\xa7\xb8\xf4', None, 0, 1, (108, 105), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xa6\xab\xafS\xaa\xba\xb4\xbc\xbcz\xa4\xa7\xa5\xfa', None, 0, 1, (32, 89), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (35, 45), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xa5\xec\xa7\xf9\xa5d\xafS\xaa\xba\xbc\xa4\xb1\xe6', None, 0, 1, (27, 20), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xa7\xac\xc9\xa4\xa7\xaa\xf9', None, 0, 1, (92, 30), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1101: {
        '\xa4j\xaa\xf7\xa6r\xb6\xf0\xa4\xba': [
            ('\xb4_\xa5\xcd\xaa\xcc\xb9\xcf\xafS\xbc\xaf\xb4\xb5', None, 0, 1, (92, 49), 0, None, 255, 'f', 0, 0, None, None, None),
            ('\xaa\xf7\xad\xe8\xaa\xba\xa4g\xa4\xb8\xaf\xc0', None, 0, 1, (149, 21), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xa8g\xbc\xc9\xaa\xba\xa4\xf4\xa4\xb8\xaf\xc0', None, 0, 1, (166, 90), 0, None, 255, 'k', 0, 0, None, None, None),
            ('\xb8t\xb3D\xaew\xa7B\xa9\xd4', None, 0, 1, (115, 67), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xb8v\xadh\xaa\xba\xad\xb7\xa4\xb8\xaf\xc0', None, 0, 1, (38, 40), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (105, 102), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xa8`\xbfN\xaa\xba\xa4\xf5\xa4\xb8\xaf\xc0', None, 0, 1, (50, 91), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1107: {
        '\xbe\xf7\xb1\xf1\xa4\xa7\xb3\xa3': [
            ('\xbe\xf7\xb1\xf1\xa4k\xac\xd3', None, 0, 1, (80, 57), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xbe\xf7\xb1\xf1\xa4\xa7\xa4\xfd', None, 0, 1, (39, 80), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xa6\xe5\xb8{\xba\xbf\xc4R', None, 0, 1, (22, 31), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (117, 39), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad\xab\xb8\xcb\xb3\xcd\xae\xa6', None, 0, 1, (140, 84), 0, None, 255, 'z', 0, 0, None, None, None),
            ('\xc0\xeb\xa4E\xab\xd5', None, 0, 1, (144, 26), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1111: {
        '\xc0s\xbb\xf1\xc2\xed': [
            ('\xab\xe4\xd9\xe7', None, 0, 1, (21, 116), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (48, 91), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1112: {
        '\xa4\xd1\xb4\xf9\xa5\xad\xad\xec': [
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (149, 33), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xa9\xf6\xaee\xa4j\xaev', None, 0, 1, (99, 62), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1120: {
        '\xa4\xd1\xbf\xef\xc4v\xa7\xde\xb3\xf5': [
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 0, 1, (150, 97), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (170, 88), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xa4\xb8\xb3q\xafu\xa7g', None, 4929, 1, (161, 93), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1121: {
        '\xa4\xd1\xbf\xef\xc4v\xa7\xde\xb3\xf5': [
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 0, 1, (150, 97), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (170, 88), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xb8\xb3q\xafu\xa7g', None, 4929, 1, (161, 93), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1126: {
        '\xb2M\xad\xb7\xa7\xf8': [
            ('\xa8\xae\xa5\xed', None, 2012, 1, (175, 142), 0, None, 255, 'cf', 0, 0, None, None, None)] },
    1154: {
        '\xa9\xfa\xa4\xeb\xab\xb0': [
            ('\xb0\xa3\xc5]\xaev', None, 3017, 1, (241, 171), 0, None, 255, 'cms', 0, 0, None, None, None),
            ('\xb2\xee\xa4\xd2', None, 2009, 1, (215, 26), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xb8\xf3\xaaA\xbfN\xc2\xf9', None, 5015, 1, (262, 182), 0, None, 255, 'kfss', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (302, 111), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xad\xb9\xab~\xa9\xb1', None, 4187, 2, (179, 77), 0, None, 255, 'spd', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (17, 89), 0, None, 255, 'tj', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1078, 2, (245, 71), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1079, 2, (222, 68), 0, None, 255, 'zhdlb', 0, 0, None, None, None)] },
    1156: {
        '\xa8\xa4\xb0\xab\xa4j\xb7|\xb2{\xb3\xf5': [
            ('\xbd\xde\xc4_', None, 0, 1, (86, 67), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1157: {
        '\xa4\xd1\xaa\xc5\xadn\xb6\xeb': [
            ('\xad\xdc\xaew', None, 4152, 1, (101, 27), 0, None, 255, 'c', 0, 0, '\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, None),
            ('\xa6a\xa9[', '\xa4H\xac\xc9\xb6\xc7\xb0e\xa4H', 4928, 1, (78, 49), 0, None, 255, 'd', 0, 0, None, None, None),
            ('\xad\xb8\xaa@\xab\xfc\xa4\xde\xa4H', None, 4977, 1, (117, 43), 0, None, 255, 'fszyr', 0, 0, None, None, None),
            ('\xafT\xaf}\xaa\xc5', None, 4362, 0, (7, 54), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbbX\xad\xb1\xa9\xc7\xab\xc8', None, 4358, 0, (144, 54), 0, None, 255, 'm', 0, 0, None, None, None),
            ('\xc5]\xbcS\xa4\xd1', None, 4361, 0, (36, 112), 0, None, 255, 'm', 0, 0, None, None, None),
            ('\xaf\xab\xaaZ\xb4L', None, 4360, 0, (122, 70), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xa4\xd1\xa6a\xa7T\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (12, 70), 0, None, 255, 'tdjjyr', 0, 0, None, None, None),
            ('\xa4\xd1\xac\xc9\xa8\xcd\xbd\xc3', None, 4364, 0, (118, 77), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xa8\xdf\xb5\xb5\xb7L', None, 4363, 0, (115, 30), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1042, 2, (64, 81), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xc2\xf8\xb3f\xa9\xb1', None, 1041, 2, (44, 77), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1158: {
        '\xaa\xec\xb6\xb3\xael\xa8\xa6': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (63, 77), 0, None, 255, 'z', 0, 0, None, None, None)] },
    1159: {
        '\xaa\xec\xb6\xb3\xa5\xad\xad\xec': [
            ('\xaf\xab\xac\xfd', None, 4962, 1, (55, 26), 0, None, 255, 's', 0, 0, None, None, None)] },
    1161: {
        '\xb6\xc2\xb4\xcb\xaaL': [
            ('\xa5\xd5\xab\xd5\xc4\xf5', None, 0, 1, (236, 113), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb6\xc7\xb0e\xaev', None, 4403, 1, (218, 132), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (210, 105), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    1162: {
        '\xc4\xf5\xadY\xa6x': [
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb6\xc7\xb0e\xaev', None, 4403, 1, (31, 35), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4p\xbd\xba', None, 0, 1, (46, 29), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (30, 15), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    1163: {
        '\xb6\xc2\xb4\xcb\xaaL\xb2`\xb3B': [
            ('\xb6\xc2\xa4s\xa6\xd1\xa7\xaf', None, 0, 1, (149, 121), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xbe\xab\xbe', None, 0, 1, (30, 97), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb6\xc7\xb0e\xaev', None, 4403, 1, (92, 134), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (85, 125), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    1171: {
        '\xc5\xdb\xb4b\xa4\xa7\xb8\xf4': [
            ('\xc5]\xb1\xda\xa6\xca\xa4\xd2\xaa\xf8', None, 0, 1, (45, 83), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2\xf6\xaa\xea', None, 0, 1, (15, 23), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbd\xf1\xb6\xb3', None, 0, 1, (20, 26), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (74, 60), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb3v\xa4\xe9', None, 0, 1, (101, 69), 0, None, 255, '', 0, 0, None, None, None)] },
    1172: {
        '\xb8U\xc5]\xb2\xbd\xbe\xc2': [
            ('\xa6\xe5\xb8\xaa', None, 0, 1, (32, 90), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (40, 50), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1173: {
        '\xaf\xb5\xa5\xdb\xbco\xbcV': [
            ('\xc5Q\xa4\xd1\xb0\xad\xae\xab', None, 0, 1, (154, 79), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (130, 100), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1174: {
        '\xa4\xd6\xb2b\xa4\xd1\xabn\xaa\xf9': [
            ('\xabn\xa4Z', None, 0, 1, (93, 53), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (100, 25), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1175: {
        '\xb2b\xc4^\xa8c\xba\xbb': [
            ('\xc5Q\xa4\xd1\xc0s\xc3C', None, 0, 1, (56, 73), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb6\xad\xa6w', None, 0, 1, (51, 75), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (40, 60), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1176: {
        '\xc5]\xb4\xb9\xadn\xb6\xeb': [
            ('\xb3\xd5\xa4\xe5\xc5r', None, 4393, 0, (118, 34), 0, None, 255, '', 0, 0, None, None, None),
            ('\xaf\xab\xb2\xde', None, 4963, 1, (120, 8), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb7\xb9\xa4\xd1\xc6F', None, 4392, 0, (54, 26), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (96, 26), 0, None, 255, '', 0, 0, None, None, None)] },
    1178: {
        '\xb0\xc6\xa5\xbb\xb7\xc7\xb3\xc6\xc6U': [
            ('\xb0\xc6\xa5\xbb', None, 4993, 1, (125, 80), 0, None, 255, 'fb', 0, 0, None, None, None),
            ('\xb0g\xaec\xa1B\xa4\xbb\xb9D', None, 0, 1, (150, 80), 0, None, 255, 'mg', 0, 0, None, None, None),
            ('\xad\xb9\xab~\xa9\xb1', None, 4187, 2, (140, 115), 0, None, 255, 'spd', 0, 0, None, None, None)] },
    1179: {
        '\xb0\xc6\xa5\xbb\xb7\xc7\xb3\xc6\xc6U': [
            ('\xa4j\xac\xea\xaav\xa4\xf4', None, 5019, 1, (190, 85), 0, None, 255, 'dyzs', 0, 0, None, None, None),
            ('\xab\xca\xaf\xab\xba]', None, 4990, 1, (140, 105), 0, None, 255, 'fsb', 0, 0, None, None, None),
            ('\xa5\xfa\xbcv\xa7\xc7\xa6\xb1', None, 4989, 1, (140, 85), 0, None, 255, 'gyxq', 0, 0, None, None, None),
            ('\xbe\xf7\xb1\xf1\xab\xd2\xb0\xea', None, 4988, 1, (140, 65), 0, None, 255, 'jxdg', 0, 0, None, None, None),
            ('\xc0H\xbe\xf7\xb0\xc6\xa5\xbb\xa1P\xba\xeb\xad^', None, 4994, 1, (90, 85), 0, None, 255, 'sjfbjy', 0, 0, None, None, None),
            ('\xa8\xb8\xaf\xab\xa5l\xb3\xea', None, 5016, 1, (190, 105), 0, None, 255, 'xszh', 0, 0, None, None, None),
            ('\xad^\xc6F\xb7\xb5', None, 5023, 1, (190, 65), 0, None, 255, 'yld', 0, 0, None, None, None)] },
    1180: {
        '\xb0\xc6\xa5\xbb\xb7\xc7\xb3\xc6\xc6U': [
            ('\xad\xb9\xab~\xa9\xb1', None, 4187, 2, (61, 45), 0, None, 255, 'spd', 0, 0, None, None, None),
            ('\xbe\xc7\xae{\xab\xfc\xa4\xde\xa4H', None, 4192, 1, (38, 35), 0, None, 255, 'xtzyr', 0, 0, None, None, None)] },
    1181: {
        '\xb6\xb3\xb3\xb6\xa8\xa6': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1182: {
        '\xb2M\xb7\xcb\xa5\xad\xad\xec': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1183: {
        '\xaa\xda\xaf\xf3\xc2\xed': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1184: {
        '\xb8\xa8\xa4\xe9\xae\xfc\xc6W': [
            ('\xb2\xee\xa4\xd2', None, 2010, 1, (26, 103), 0, None, 255, 'cf', 0, 0, None, None, None)] },
    1186: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (26, 28), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1190: {
        '\xb5\xb4\xc0s\xc0\xad': [
            ('\xbbD\xa5\xf2', None, 5701, 1, (100, 77), 0, None, 255, 'wz', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (132, 64), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1191: {
        '\xc2\xcf\xc0s\xc0\xad': [
            ('\xb0\xaa\xa9\xfa', None, 5702, 1, (64, 123), 0, None, 255, 'gm', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (40, 85), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb0K\xacx', None, 5703, 1, (97, 56), 0, None, 255, 'yh', 0, 0, None, None, None)] },
    1192: {
        '\xb4\xc2\xbaq': [
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (49, 43), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xccH\xa4v', None, 5704, 1, (136, 29), 0, None, 255, 'dj', 0, 0, None, None, None),
            ('\xac\xf4\xa4\xfd', None, 5705, 1, (58, 71), 0, None, 255, 'zw', 0, 0, None, None, None)] },
    1194: {
        '\xb1\xeb\xa4\xd1\xa5j\xab\xb0': [
            ('\xb6\xb3\xa4d\xba\xbd', None, 4888, 0, (121, 101), 0, None, 255, 'yty', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (118, 27), 0, None, 255, '', 0, 0, None, None, None)] },
    1196: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (130, 40), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1197: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (33, 118), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1198: {
        '\xafe\xad\xb7\xa8\xa6': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (100, 47), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1200: {
        '\xb8H\xb9\xda\xc0\xad': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (45, 25), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1201: {
        '\xaa\xf7\xba\xf1\xa8F\xacw': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (191, 45), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1202: {
        '\xad\xd7\xc3\xb9\xb4\xcb\xaaL': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (233, 51), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1203: {
        '\xb8\xa8\xb3\xb7\xa6B\xad\xec': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1204: {
        '\xaa\xec\xb6\xb3\xael\xa8\xa6': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (63, 77), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1205: {
        '\xaa\xec\xb6\xb3\xa5\xad\xad\xec': [
            ('\xaf\xab\xac\xfd', None, 4962, 1, (55, 26), 0, None, 255, 'sy', 0, 0, None, None, None)] },
    1206: {
        '\xc5]\xb4\xb9\xadn\xb6\xeb': [
            ('\xb3\xd5\xa4\xe5\xc5r', None, 4393, 0, (118, 34), 0, None, 255, 'bwl', 0, 0, None, None, None),
            ('\xaf\xab\xb2\xde', None, 4963, 1, (120, 8), 0, None, 255, 'sl', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (96, 26), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1207: {
        '\xb8t\xb2\xaa\xael\xa8\xa6': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1208: {
        '\xb1\xeb\xa4\xd1\xa5j\xab\xb0': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (118, 27), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1209: {
        '\xbe\xa4\xa9\xfa\xc2\xed': [
            ('\xa4\xd1\xb0\xae', None, 4919, 1, (89, 19), 0, None, 255, 'tq', 0, 0, None, None, None)] },
    1210: {
        '\xb0O\xbe\xd0\xa4\xa7\xa4t': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1211: {
        '\xbe\xa4\xa9\xfa\xc2\xed': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1212: {
        '\xba\xab\xaf[\xb5\xd8\xa4\xa7\xaea': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1213: {
        '\xb4H\xa4\xeb\xb4\xcb\xaaL': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1214: {
        '\xba\xab\xaf[\xb5\xd8\xa4\xa7\xb9\xda': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1215: {
        '\xafe\xad\xb7\xa8\xa6': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1217: {
        '\xc5]\xb1\xda\xb0\xf2\xa6a': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1218: {
        '\xbbB\xbbA\xa4\xa7\xb9\xd2': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1219: {
        '\xafT\xb1\xda\xba\xca\xa8c': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1220: {
        '\xa8\xdf\xb1\xda\xba\xca\xa8c': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1221: {
        '\xb0g\xaec\xb7\xc7\xb3\xc6\xc6U': [
            ('\xaa\xf7\xa6r\xb6\xf0', None, 0, 1, (98, 69), 0, None, 255, 'jzt', 0, 0, None, None, None),
            ('\xaa\xf7\xa6r\xb6\xf0', None, 0, 1, (98, 95), 0, None, 255, 'jzt', 0, 0, None, None, None),
            ('\xaf\xb3\xac\xd3\xb3\xae', None, 0, 1, (138, 69), 0, None, 255, 'qhl', 0, 0, None, None, None),
            ('\xaf\xb3\xac\xd3\xb3\xae', None, 0, 1, (138, 95), 0, None, 255, 'qhl', 0, 0, None, None, None),
            ('\xa7l\xa6\xe5\xa5j\xb3\xf9', None, 0, 1, (178, 69), 0, None, 255, 'xxg', 0, 0, None, None, None),
            ('\xa7l\xa6\xe5\xa5j\xb3\xf9', None, 0, 1, (178, 95), 0, None, 255, 'xxg', 0, 0, None, None, None)] },
    1222: {
        '\xa9]\xb9\xf5\xc2\xed': [
            ('\xa4\xd1\xb0\xae', None, 4919, 1, (20, 15), 0, None, 255, 'tq', 0, 0, None, None, None)] },
    1223: {
        '\xa4\xd1\xaa\xc5\xadn\xb6\xeb': [
            ('\xa6a\xa9[', None, 4928, 1, (78, 49), 0, None, 255, 'dk', 0, 0, None, None, None)] },
    1238: {
        '\xa5P\xc6F\xaeq': [
            ('\xab_\xc0I\xb1\xb5\xa4\xde\xa4H', None, 5018, 1, (34, 94), 0, None, 255, 'mxjyr', 0, 0, None, None, None)] },
    1239: {
        '\xa5P\xc6F\xaeq2': [
            ('\xab_\xc0I\xb1\xb5\xa4\xde\xa4H', None, 5018, 1, (34, 94), 0, None, 255, 'mxjyr', 0, 0, None, None, None)] },
    1240: {
        '\xa5P\xc6F\xaeq3': [
            ('\xab_\xc0I\xb1\xb5\xa4\xde\xa4H', None, 5018, 1, (34, 94), 0, None, 255, 'mxjyr', 0, 0, None, None, None)] },
    1241: {
        '\xa5P\xc6F\xaeq4': [
            ('\xab_\xc0I\xb1\xb5\xa4\xde\xa4H', None, 5018, 1, (34, 94), 0, None, 255, 'mxjyr', 0, 0, None, None, None)] },
    1242: {
        '\xa5P\xc6F\xaeq5': [
            ('\xab_\xc0I\xb1\xb5\xa4\xde\xa4H', None, 5018, 1, (34, 94), 0, None, 255, 'mxjyr', 0, 0, None, None, None)] },
    1301: {
        '\xab_\xc0I\xaea\xa6\xe6\xb7|\xa4@\xbch': [
            ('\xc4_\xaa\xab\xb5n\xb0O\xa4H', None, 0, 1, (62, 33), 0, None, 255, 'bwdjr', 0, 0, None, None, None),
            ('\xb7|\xaa\xf8', None, 0, 1, (66, 44), 0, None, 255, 'mxhhhz', 0, 0, None, None, None),
            ('\xbc\xfa\xab~\xa7I\xb4\xab\xa4H', None, 0, 1, (46, 40), 0, None, 255, 'jpdhr', 0, 0, None, None, None),
            ('\xc2\xc5\xc0s', None, 0, 1, (73, 41), 0, None, 255, 'll', 0, 0, None, None, None),
            ('\xb0g\xaec\xb6\xc7\xb0e\xa4H', None, 0, 1, (45, 23), 0, None, 255, 'mgcsr', 0, 0, None, None, None),
            ('\xa4\xe5\xb3\xd5', None, 0, 1, (59, 47), 0, None, 255, 'wb', 0, 0, None, None, None)] },
    1302: {
        '\xab\xd5\xc6F\xae\xfc\xb0\xec': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1303: {
        '\xab_\xc0I\xaea\xa6\xe6\xb7|\xa4G\xbch': [
            ('\xa4K\xa8\xf6\xa9v\xaev', None, 0, 1, (47, 44), 0, None, 255, 'bgzs', 0, 0, None, None, None)] },
    1305: {
        '\xa4\xd3\xa5\xad\xc2\xed': [
            ('\xa8\xeb\xab\xc8\xad\xba\xbb\xe2', None, 0, 1, (142, 21), 0, None, 255, 'cksl', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xb0\xab\xa4h', None, 0, 1, (60, 76), 0, None, 255, 'mozds', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xaak\xc4_', None, 0, 1, (63, 30), 0, None, 255, 'mzfb', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xb2\xce\xab\xd3', None, 0, 1, (102, 23), 0, None, 255, 'mzts', 0, 0, None, None, None),
            ('\xa5\xa3\xc1\xf5\xb0\xab\xa4h', None, 0, 1, (71, 80), 0, None, 255, 'nlds', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (28, 88), 0, None, 255, 'ydlb', 0, 0, None, None, None),
            ('\xc2\xed\xaa\xf8', None, 0, 1, (86, 91), 0, None, 255, 'zz', 0, 0, None, None, None)] },
    1307: {
        '\xa8\xb8\xaf\xab\xc0\xe7\xa6a': [
            ('\xb2\xc4\xa4G\xc0\xe7\xa6a', None, 0, 1, (115, 85), 0, None, 255, 'dryd', 0, 0, None, None, None),
            ('\xb2\xc4\xa4T\xc0\xe7\xa6a', None, 0, 1, (29, 76), 0, None, 255, 'dsyd', 0, 0, None, None, None),
            ('\xb2\xc4\xa5|\xc0\xe7\xa6a', None, 0, 1, (58, 19), 0, None, 255, 'dsyd', 0, 0, None, None, None),
            ('\xb2\xc4\xa4\xad\xc0\xe7\xa6a', None, 0, 1, (76, 60), 0, None, 255, 'dwyd', 0, 0, None, None, None),
            ('\xb2\xc4\xa4@\xc0\xe7\xa6a', None, 0, 1, (117, 25), 0, None, 255, 'dyyd', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (45, 100), 0, None, 255, 'yd', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (108, 50), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    1308: {
        '\xb0g\xb9\xda\xa4\xdb\xb9\xd2': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1310: {
        '\xb5\xd8\xaeL\xa4E\xa6{': [
            ('\xa6\xca\xa4t\xc2k\xae\xfc\xa4f', None, 0, 1, (85, 53), 0, None, 255, 'f', 0, 0, None, None, None),
            ('\xa6@\xa4u\xc0\xe7\xa6a', None, 0, 1, (131, 129), 0, None, 255, 'g', 0, 0, None, None, None),
            ('\xc5@\xc4[\xaf\xab\xb1N', None, 0, 1, (117, 25), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xc6F\xa6\xc0\xa4J\xa4f', None, 0, 1, (155, 81), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xa4s\xae\xfc\xb8t\xbe\xf0', None, 0, 1, (42, 109), 0, None, 255, 'w', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 0, 2, (67, 103), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 0, 2, (71, 36), 0, None, 255, 'y', 0, 0, None, None, None)] },
    1313: {
        '\xc0s\xb2W': [
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 4427, 1, (136, 90), 0, None, 255, 'zdjjr', 0, 0, None, None, None)] },
    1315: {
        '\xae\xc9\xaa\xc5\xb5\xf5\xbb\xd8': [
            ('\xb2{\xa5@\xb6\xc7\xb0e\xaa\xf9', None, 0, 1, (21, 69), 0, None, 255, 'xscsm', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (55, 70), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    1316: {
        '\xb5L\xa6W\xa7\xf8\xb2\xf8': [
            ('\xc5]\xaf\xab\xaak\xb0}', None, 0, 1, (113, 21), 0, None, 255, 'mzjt', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xb1^\xad\xef', None, 0, 1, (47, 98), 0, None, 255, 'mzgs', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xba\xca\xa8c', None, 0, 1, (116, 65), 0, None, 255, 'mzjl', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (75, 70), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    1317: {
        '\xbb\xc5\xb4H\xa6B\xad\xec': [
            ('\xb6\xc7\xb0e\xaa\xf9', None, 0, 1, (22, 137), 0, None, 255, 'csm', 0, 0, None, None, None)] },
    1318: {
        '\xab\xd5\xb7t\xb2`\xae\xfc': [
            ('\xb6\xc7\xb0e\xaa\xf9', None, 0, 1, (15, 47), 0, None, 255, 'csm', 0, 0, None, None, None)] },
    1319: {
        '\xa5\xbd\xa4\xe9\xb2`\xb2W': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1320: {
        '\xb5\xb4\xb1K\xb9\xea\xc5\xe7\xab\xc7': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1321: {
        '\xb0O\xbe\xd0\xad\xcb\xbcv': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1322: {
        '\xacP\xa4\xeb\xb6\xa1\xbb\xd8': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1323: {
        '\xad^\xc6F\xb7\xb5': [
            ('\xa5\xcd\xa9R\xaa\xe1\xb6\xe9', None, 0, 1, (63, 91), 0, None, 255, 'smhy', 0, 0, None, None, None),
            ('\xb8t\xb7\xb5\xa4\xa7\xaa\xf9', None, 0, 1, (21, 23), 0, None, 255, 'sdzm', 0, 0, None, None, None),
            ('\xb8t\xa5\xfa', None, 9001, 2, (13, 8), 0, None, 255, 'sg', 0, 0, None, None, None),
            ('\xb8t\xa5\xfa', None, 9002, 2, (61, 51), 0, None, 255, 'sg', 0, 0, None, None, None),
            ('\xa5\xc3\xf9\xda\xa4j\xc6U', None, 0, 1, (79, 53), 0, None, 255, 'yhzt', 0, 0, None, None, None),
            ('\xaa\xbe\xc3\xd1\xc4_\xaew', None, 0, 1, (143, 46), 0, None, 255, 'zsbk', 0, 0, None, None, None),
            ('\xa6\xdc\xb0\xaa\xb7\xb5\xb0\xf3', None, 0, 1, (127, 85), 0, None, 255, 'rydt', 0, 0, None, None, None)] },
    1324: {
        '\xa9\xfa\xa4\xeb\xab\xb0\xabn\xaa\xf9': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1326: {
        '\xad\xc5\xa4k\xab\xd5\xbb\xee': [
            ('\xa5\xd5\xab\xd5\xc4\xf5', None, 0, 1, (153, 82), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb6\xc2\xa4s\xa6\xd1\xa7\xaf', None, 0, 1, (18, 133), 0, None, 255, '', 0, 0, None, None, None),
            ('\xaa\xea\xafT\xa4G\xb1N', None, 0, 1, (93, 125), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xbe\xab\xbe', None, 0, 1, (143, 123), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4p\xbd\xba', None, 0, 1, (103, 16), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (108, 129), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (157, 20), 0, None, 255, '', 0, 0, None, None, None)] },
    1327: {
        '\xb7\xc9\xae\xfc\xacw': [
            ('\xba\xd1\xad\xe2\xa8\xe0', None, 5027, 0, (203, 70), 0, None, 255, 'ble', 0, 0, None, None, None),
            ('\xb7\xc9\xac\xd5\xac\xd5', None, 5028, 0, (31, 43), 0, None, 255, 'cyy', 0, 0, None, None, None),
            ('\xb2\xee\xa4\xd2', None, 2014, 1, (192, 13), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa4\xf4\xa4\xeb', None, 5026, 0, (41, 110), 0, None, 255, 'sy', 0, 0, None, None, None)] },
    1328: {
        '\xad\xc5\xa4k\xab\xd5\xbb\xee\xa5@\xac\xc9': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1412: {
        '\xa9\xfa\xa4\xeb\xab\xb01': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1413: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a1': [
            ('\xbe\xd4\xbeW\xa1P\xacP\xa4\xeb', None, 1004, 1, (35, 45), 0, None, 255, 'zfxy', 0, 0, None, None, None)] },
    1414: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa41': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1415: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL1': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1416: {
        '\xafe\xad\xb7\xa8\xa61': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1417: {
        '\xa9]\xb9\xf5\xc2\xed1': [
            ('\xb6\xb6\xa4\xd1\xa1P\xc1\xfc\xad\xb7', None, 1005, 1, (93, 16), 0, None, 255, 'stjf', 0, 0, None, None, None)] },
    1422: {
        '\xa9\xfa\xa4\xeb\xab\xb02': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1423: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a2': [
            ('\xbe\xd4\xbeW\xa1P\xacP\xa4\xeb', None, 1004, 1, (35, 45), 0, None, 255, 'zfxy', 0, 0, None, None, None)] },
    1424: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa42': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1425: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL2': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1426: {
        '\xafe\xad\xb7\xa8\xa62': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1427: {
        '\xa9]\xb9\xf5\xc2\xed2': [
            ('\xb6\xb6\xa4\xd1\xa1P\xc1\xfc\xad\xb7', None, 1005, 1, (93, 16), 0, None, 255, 'stjf', 0, 0, None, None, None)] },
    1432: {
        '\xa9\xfa\xa4\xeb\xab\xb03': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1433: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a3': [
            ('\xbe\xd4\xbeW\xa1P\xacP\xa4\xeb', None, 1004, 1, (35, 45), 0, None, 255, 'zfxy', 0, 0, None, None, None)] },
    1434: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa43': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1435: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL3': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1436: {
        '\xafe\xad\xb7\xa8\xa63': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1437: {
        '\xa9]\xb9\xf5\xc2\xed3': [
            ('\xb6\xb6\xa4\xd1\xa1P\xc1\xfc\xad\xb7', None, 1005, 1, (93, 16), 0, None, 255, 'stjf', 0, 0, None, None, None)] },
    1442: {
        '\xa9\xfa\xa4\xeb\xab\xb04': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1443: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a4': [
            ('\xbe\xd4\xbeW\xa1P\xacP\xa4\xeb', None, 1004, 1, (35, 45), 0, None, 255, 'zfxy', 0, 0, None, None, None)] },
    1444: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa44': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1445: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL4': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1446: {
        '\xafe\xad\xb7\xa8\xa64': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1447: {
        '\xa9]\xb9\xf5\xc2\xed4': [
            ('\xb6\xb6\xa4\xd1\xa1P\xc1\xfc\xad\xb7', None, 1005, 1, (93, 16), 0, None, 255, 'stjf', 0, 0, None, None, None)] },
    1452: {
        '\xa9\xfa\xa4\xeb\xab\xb05': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1453: {
        '\xa4\xd3\xae\xa7\xaaL\xa6a5': [
            ('\xbe\xd4\xbeW\xa1P\xacP\xa4\xeb', None, 1004, 1, (35, 45), 0, None, 255, 'zfxy', 0, 0, None, None, None)] },
    1454: {
        '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa45': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1455: {
        '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL5': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1456: {
        '\xafe\xad\xb7\xa8\xa65': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    1457: {
        '\xa9]\xb9\xf5\xc2\xed5': [
            ('\xb6\xb6\xa4\xd1\xa1P\xc1\xfc\xad\xb7', None, 1005, 1, (93, 16), 0, None, 255, 'stjf', 0, 0, None, None, None)] },
    2007: {
        '\xb3\xb7\xa4H\xaex\xb0|': [
            ('\xb3\xb7\xa4H', None, 0, 1, (42, 35), 0, None, 255, '', 0, 0, None, None, None)] },
    2151: {
        '\xa4p\xb0|\xa4l': [
            ('\xa8\xae\xa5\xed', None, 0, 1, (26, 7), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xc3d\xaa\xab\xa4\xa7\xaea', None, 0, 1, (17, 23), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xaa\xe1\xa5\xd0', None, 0, 1, (29, 11), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xa4p\xb0\xca\xaa\xab\xad\xd7\xb7\xd2', '\xa5\xfa\xc0Y\xc3~\xa4\xfd', 0, 1, (10, 20), 0, None, 255, 'x', 20, 0, '\xa5\xfa\xc0Y\xc3~\xa4\xfd', None, None)] },
    2152: {
        '\xa4\xa4\xb0|\xa4l': [
            ('\xa8\xae\xa5\xed', None, 0, 1, (42, 5), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xc3d\xaa\xab\xa4\xa7\xaea', None, 0, 1, (31, 21), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xaa\xe1\xa5\xd0', None, 0, 1, (41, 10), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xa4p\xb0\xca\xaa\xab\xad\xd7\xb7\xd2', '\xa5\xfa\xc0Y\xc3~\xa4\xfd', 0, 1, (20, 20), 0, None, 255, 'x', 20, 0, '\xa5\xfa\xc0Y\xc3~\xa4\xfd', None, None)] },
    2153: {
        '\xa4j\xb0|\xa4l': [
            ('\xa8\xae\xa5\xed', None, 0, 1, (54, 8), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xc3d\xaa\xab\xa4\xa7\xaea', None, 0, 1, (25, 29), 0, None, 255, 'c', 0, 0, None, None, None),
            ('\xaa\xe1\xa5\xd0', None, 0, 1, (50, 11), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xa4p\xb0\xca\xaa\xab\xad\xd7\xb7\xd2', '\xa5\xfa\xc0Y\xc3~\xa4\xfd', 0, 1, (17, 24), 0, None, 255, 'x', 20, 0, '\xa5\xfa\xc0Y\xc3~\xa4\xfd', None, None)] },
    2201: {
        '\xc0\xb0\xac\xa3': [
            ('\xa5\xd5\xaa\xea\xb0\xf3\xb0\xf3\xa5D', '\xa6u\xc5@\xc3~\xb0V\xbdm', 4671, 1, (26, 84), 0, (3011, 3012), 255, 'bhttz', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xac\xa1\xb0\xca\xba\xde\xb2z\xad\xfb', '\xc0\xb0\xac\xa3\xac\xa1\xb0\xca', 4668, 1, (22, 61), 0, None, 255, 'ncgly', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xb2\xbd\xa5q', '\xac\xe8\xc3\xab\xaf\xac\xba\xd6', 4669, 1, None, 0, (3023, 3024), 255, 'bpjs', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xaev\xb7\xdd', '\xa4\xba\xacF\xab\xd8\xb3]', 4664, 1, (108, 62), 0, None, 255, 'bpsy', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xbe\xc7\xae{\xab\xfc\xbe\xc9\xad\xfb', '\xbe\xc7\xae{\xac\xdb\xc3\xf6', 4980, 1, (64, 53), 0, None, 255, 'bpxtzdy', 0, 0, None, None, None),
            ('\xba\xd6\xa7Q\xc1`\xba\xde', '\xba\xd6\xa7Q\xac\xdb\xc3\xf6', 4666, 1, (99, 42), 0, None, 255, 'flzg', 0, 0, None, None, None),
            ('\xabC\xc0s\xb0\xf3\xb0\xf3\xa5D', '\xa6w\xa9w\xab\xd7\xa4\xce\xb8\xea\xa7\xf7', 4670, 1, (61, 57), 0, (3017, 3018), 255, 'qlttz', 0, 0, None, None, None),
            ('\xa6u\xc5@\xc3~', '\xb4M\xc4_\xc3~\xa5\xf4\xb0\xc8', 4667, 1, None, 0, (3025, 3026), 255, 'shs', 0, 0, None, None, None),
            ('\xae\xd1\xb0|\xc1`\xba\xde', '\xa7\xde\xaf\xe0\xa4\xdf\xaak', 4665, 1, None, 0, (3021, 3022), 255, 'syzg', 0, 0, None, None, None),
            ('\xa5\xc8\xaaZ\xb0\xf3\xb0\xf3\xa5D', '\xc1\xc8\xa8\xfa\xc0\xb0\xb0^\xa9M\xb8\xea\xa7\xf7', 4673, 1, (115, 46), 0, None, 255, 'xwttz', 0, 0, None, None, None),
            ('\xa6\xb6\xb3\xb6\xb0\xf3\xb0\xf3\xa5D', '\xc0\xb0\xac\xa3\xa5~\xa5\xe6', 4672, 1, (64, 14), 0, None, 255, 'zqttz', 0, 0, None, None, None)] },
    2202: {
        '\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xa5\xd5\xaa\xea\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (9, 19), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xabC\xc0s\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (7, 152), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xa5\xc8\xaaZ\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (257, 145), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xa6\xb6\xb3\xb6\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (272, 17), 0, None, 255, 'bzjyr', 0, 0, None, None, None)] },
    2203: {
        '\xc0\xb0\xac\xa3': [
            ('\xa5\xd5\xaa\xea\xb0\xf3\xb0\xf3\xa5D', '\xa6u\xc5@\xc3~\xb0V\xbdm', 4671, 1, (21, 81), 0, None, 255, 'bhttz', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xac\xa1\xb0\xca\xba\xde\xb2z\xad\xfb', '\xc0\xb0\xac\xa3\xac\xa1\xb0\xca', 4668, 1, (59, 59), 0, None, 255, 'ncgly', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xaev\xb7\xdd', '\xa4\xba\xacF\xab\xd8\xb3]', 4664, 1, (104, 97), 0, None, 255, 'bpsy', 0, 0, None, None, None),
            ('\xc0\xb0\xac\xa3\xbe\xc7\xae{\xab\xfc\xbe\xc9\xad\xfb', '\xbe\xc7\xae{\xac\xdb\xc3\xf6', 4980, 1, (77, 79), 0, None, 255, 'bpxtzdy', 0, 0, None, None, None),
            ('\xba\xd6\xa7Q\xc1`\xba\xde', '\xba\xd6\xa7Q\xac\xdb\xc3\xf6', 4666, 1, (144, 106), 0, None, 255, 'flzg', 0, 0, None, None, None),
            ('\xabC\xc0s\xb0\xf3\xb0\xf3\xa5D', '\xa6w\xa9w\xab\xd7\xa4\xce\xb8\xea\xa7\xf7', 4670, 1, (166, 47), 0, None, 255, 'qlttz', 0, 0, None, None, None),
            ('\xa6u\xc5@\xc3~', '\xb4M\xc4_\xc3~\xa5\xf4\xb0\xc8', 4667, 1, (35, 132), 0, None, 255, 'shs', 0, 0, None, None, None),
            ('\xa5\xc8\xaaZ\xb0\xf3\xb0\xf3\xa5D', '\xc1\xc8\xa8\xfa\xc0\xb0\xb0^\xa9M\xb8\xea\xa7\xf7', 4673, 1, (60, 119), 0, None, 255, 'xwttz', 0, 0, None, None, None),
            ('\xa6\xb6\xb3\xb6\xb0\xf3\xb0\xf3\xa5D', '\xc0\xb0\xac\xa3\xa5~\xa5\xe6', 4672, 1, (107, 24), 0, None, 255, 'zqttz', 0, 0, None, None, None)] },
    2301: {
        '\xa5\xab\xb6\xb0': [
            ('\xa6w\xa5\xfe\xab\xc5\xb6\xc7\xad\xfb', None, 4852, 1, (228, 111), 0, None, 255, 'a', 0, 0, None, None, None),
            ('\xad\xdc\xaew', None, 4152, 1, (37, 74), 0, None, 255, 'ck', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 4509, 1, (124, 130), 0, None, 255, 'jqcf', 0, 0, None, None, None),
            ('\xc2I\xa5d\xb1H\xb0\xe2\xa4H', None, 4140, 1, (20, 106), 0, None, 255, 'dkjsr', 0, 0, None, None, None),
            ('\xa4u\xc3\xc0\xaev', None, 4563, 1, (174, 121), 0, None, 255, 'gys', 0, 0, None, None, None),
            ('\xb3\xc3\xa8\xe3\xaev', None, 4561, 1, (147, 106), 0, None, 255, 'jjs', 0, 0, None, None, None),
            ('\xc5\xb3\xa9w\xaev', None, 4104, 1, (112, 138), 0, None, 255, 'jds', 0, 0, None, None, None),
            ('\xaa\xf7\xa5\xdb\xa5P\xaf\xce', None, 4101, 1, (78, 137), 0, None, 255, 'jsxw', 0, 0, None, None, None),
            ('\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf', None, 4968, 1, (158, 112), 0, None, 255, 'jpjyzx', 0, 0, None, None, None),
            ('\xb3\xd2\xb0\xc8\xa4\xa4\xa4\xb6\xa4H', None, 4451, 1, (128, 96), 0, None, 255, 'lwzjr', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (101, 102), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xc2\xa7\xb3\xa1\xa9x\xad\xfb', None, 4422, 1, (208, 130), 0, None, 255, 'lbgy', 0, 0, None, None, None),
            ('\xc2\xb3\xad\xb9\xb0\xd3\xa4H', None, 4435, 1, (58, 125), 0, None, 255, 'nssr', 0, 0, None, None, None),
            ('\xaf\xab\xc3~\xa4p\xad\xb8\xbd\xde', None, 4460, 1, (40, 46), 0, None, 255, 'ssxfz', 0, 0, None, None, None),
            ('\xa5\xcd\xb2\xa3\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1107, 1, (59, 67), 0, None, 255, 'scjnjs', 0, 0, None, None, None),
            ('\xa4\xd1\xbe\xf7\xa6\xd1\xa4H', None, 4473, 1, (146, 141), 0, None, 255, 'tjlr', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 4183, 1, (75, 120), 0, None, 255, 'tj', 0, 0, None, None, None),
            ('\xa5P\xacy\xb9D\xa4H', None, 4102, 1, (95, 129), 0, None, 255, 'xldr', 0, 0, None, None, None),
            ('\xad\xd7\xb7\xd2\xab\xfc\xbe\xc9\xa4H', None, 4810, 1, (12, 78), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xc3\xc4\xa7\xf7\xb0\xd3\xa4H', None, 4442, 1, (116, 110), 0, None, 255, 'ycsr', 0, 0, None, None, None),
            ('\xb9C\xab\xc8\xba\xde\xb2z\xad\xfb', None, 0, 1, (140, 120), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb3y\xab\xac\xaev', None, 4191, 1, (51, 140), 0, None, 255, 'rss', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xa7\xde\xaf\xe0\xb1\xd0\xaev', None, 1104, 1, (71, 72), 0, None, 255, 'zdjnjs', 0, 0, None, None, None),
            ('\xc2\xbe\xb7~\xa4\xc1\xb4\xab\xa4H', None, 4842, 1, (21, 83), 0, None, 255, 'z', 0, 0, None, None, None)] },
    2302: {
        '\xaev\xb9D\xb7\xb5': [
            ('\xc2\xbe\xb7~\xbe\xc9\xaev', None, 0, 1, (29, 32), 0, None, 255, 'zyds', 0, 0, None, None, None)] },
    2999: {
        '\xa4\xd1\xc5]\xb7\xb5': [
            ('\xa4\xd1\xc5]\xb7\xb5\xb6\xc7\xb0e\xa8\xcf\xaa\xcc', None, 0, 1, (21, 79), 0, None, 255, 'm', 0, 0, None, None, None)] },
    9001: {
        '\xb9\xda\xb9\xd2': [
            ('\xb9\xda\xb9\xd2\xac\xdd\xaa\xf9\xa4H', None, 0, 1, (94, 98), 0, None, 255, '', 0, 0, None, None, None)] },
    9002: {
        '\xb9\xda\xb9\xd2\xbch': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9014: {
        '\xab\xe1\xb0|': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9015: {
        '\xbe\xa4\xa9\xfa\xc2\xed': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9016: {
        '\xa9]\xb9\xf5\xc2\xed': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9017: {
        '\xa5\xc3\xbfA\xab\xb0': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9018: {
        '\xad\xbb\xb8\xad\xab\xb0': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9019: {
        '\xa4\xd1\xbba\xab\xb0': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9020: {
        '\xac\xa1\xb0\xca\xb7\xc7\xb3\xc6\xc6U': [
            ('\xac\xa1\xb0\xca\xab\xfc\xa4\xde\xa4H', None, 1001, 1, (140, 78), 0, None, 255, 'hdzyr', 0, 0, None, None, None)] },
    9021: {
        '\xba\xeb\xad^\xc0\xb0\xbe\xd4\xbe\xd4\xb3\xf5': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9022: {
        '\xba\xeb\xad^\xc0\xb0\xbe\xd4\xbe\xd4\xb3\xf5': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9039: {
        '\xb0\xaa\xb6\xf0\xa4@\xbch': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9040: {
        '\xb0\xaa\xb6\xf0\xa4G\xbch': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9041: {
        '\xb0\xaa\xb6\xf0\xa4T\xbch': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9042: {
        '\xb0\xaa\xb6\xf0\xa5|\xbch': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9043: {
        '\xb6\xf0\xb3\xbb': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9046: {
        '\xacP\xaey\xb2y\xc1\xc9\xb3\xf5': [
            ('\xac\xf5\xb6\xa4\xbb\xe2\xb6\xa4', None, 0, 1, (62, 44), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xac\xf5\xb6\xa4\xbb\xe2\xb6\xa4', None, 0, 1, (62, 123), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xc2\xc5\xb6\xa4\xbb\xe2\xb6\xa4', None, 0, 1, (216, 44), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xc2\xc5\xb6\xa4\xbb\xe2\xb6\xa4', None, 0, 1, (216, 123), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xacP\xa8\xcf', None, 0, 1, (139, 78), 0, None, 255, 'x', 0, 0, None, None, None)] },
    9047: {
        '\xb0\xaa\xb6\xf0\xa4\xad\xbch': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9048: {
        '\xaf\xf3\xb8s\xbbR\xb7\xc7\xb3\xc6\xc6U': [
            ('\xaf\xf3\xb8s\xbbR\xa8\xcf\xaa\xcc', None, 0, 1, (139, 78), 0, None, 255, 'c', 0, 0, None, None, None)] },
    9049: {
        '\xaf\xf3\xb8s\xbbR\xb3\xf5': [
            ('\xaf\xf3\xb8s\xbbR\xa6Z', None, 4855, 1, (139, 78), 0, None, 255, 'c', 0, 0, None, None, None)] },
    9050: {
        '\xba\xeb\xad^\xb2\xd5\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xa5\xd5\xaa\xea\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (9, 19), 0, None, 255, 'b', 0, 0, None, None, None),
            ('\xabC\xc0s\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (7, 152), 0, None, 255, 'q', 0, 0, None, None, None),
            ('\xa5\xc8\xaaZ\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (257, 145), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xa6\xb6\xb3\xb6\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (272, 17), 0, None, 255, 'z', 0, 0, None, None, None)] },
    9052: {
        '\xba\xeb\xad^\xb2\xd5\xa5|\xb0\xea\xbe\xd4\xb3\xf5': [
            ('\xa5\xd5\xaa\xea\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (9, 19), 0, None, 255, 'b', 0, 0, None, None, None),
            ('\xabC\xc0s\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (7, 152), 0, None, 255, 'q', 0, 0, None, None, None),
            ('\xa5\xc8\xaaZ\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (257, 145), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xa6\xb6\xb3\xb6\xb2\xd5\xb6\xb0\xb5\xb2\xa4H', None, 4425, 1, (272, 17), 0, None, 255, 'z', 0, 0, None, None, None)] },
    9082: {
        '\xb8t\xb6\xf0\xb6\xaf\xa7L\xb7\xc7\xb3\xc6\xc6U': [
            ('\xb8t\xb6\xf0\xa5\xfd\xaa\xbe', None, 0, 1, (114, 83), 0, None, 255, 's', 0, 0, None, None, None)] },
    9083: {
        '\xb8t\xb6\xf0\xb6\xaf\xa7L\xac\xa1\xb0\xca\xc6U': [
            ('\xa4\xdb\xbcv\xa4\xa7\xaa\xf9\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (217, 44), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xafT\xb1\xda\xa6u\xc5@\xaa\xcc', None, 0, 1, (257, 145), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xaf\xab\xb8t\xa4\xa7\xb6\xf0', None, 0, 1, (139, 78), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xa8\xdf\xb1\xda\xa6u\xc5@\xaa\xcc', None, 0, 1, (21, 24), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xacP\xaa\xc5\xa4\xa7\xaa\xf9\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (75, 116), 0, None, 255, 'x', 0, 0, None, None, None)] },
    9084: {
        '\xacP\xaa\xc5\xa4\xa7\xaa\xf9': [
            ('\xa5e\xa4R\xaev', None, 0, 1, (37, 35), 0, None, 255, 'z', 0, 0, None, None, None)] },
    9085: {
        '\xa4\xdb\xbcv\xa4\xa7\xaa\xf9': [
            ('\xa4\xdb\xbcv\xa8\xcf\xaa\xcc', None, 0, 1, (37, 35), 0, None, 255, 'h', 0, 0, None, None, None)] },
    9092: {
        '\xbb\xc8\xaae': [
            ('\xa4\xfb\xad\xa6', None, 0, 1, (37, 85), 0, None, 255, 'n', 0, 0, None, None, None),
            ('\xc2\xb4\xa4k', None, 0, 1, (197, 21), 0, None, 255, 'z', 0, 0, None, None, None)] },
    9113: {
        '\xa8\xaa\xbb\xc9\xaf\xab\xa5\xdb\xb7\xb5': [
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9114: {
        '\xa5\xc8\xc5K\xaf\xab\xa5\xdb\xb7\xb5': [
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9115: {
        '\xaf\xc2\xbb\xc8\xaf\xab\xa5\xdb\xb7\xb5': [
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9116: {
        '\xba\xbf\xb7\xea\xaf\xab\xa5\xdb\xb7\xb5': [
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9117: {
        '\xaa\xf7\xa8F\xaf\xab\xa5\xdb\xb7\xb5': [
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaf\xab\xa5\xdb\xb7\xb5\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9120: {
        '\xa5\xd5\xa6\xcf\xaec': [
            ('\xa5\xd5\xa6\xcf\xaec\xacP\xc5]', None, 0, 1, (69, 29), 0, None, 255, 'b', 0, 0, None, None, None)] },
    9121: {
        '\xaa\xf7\xa4\xfb\xaec': [
            ('\xaa\xf7\xa4\xfb\xaec\xacP\xc5]', None, 0, 1, (85, 65), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9122: {
        '\xc2\xf9\xa4l\xaec': [
            ('\xc2\xf9\xa4l\xaec\xacP\xc5]', None, 0, 1, (42, 28), 0, None, 255, 's', 0, 0, None, None, None)] },
    9123: {
        '\xa5\xa8\xc3\xc9\xaec': [
            ('\xa5\xa8\xc3\xc9\xaec\xacP\xc5]', None, 0, 1, (42, 28), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9124: {
        '\xb7\xe0\xa4l\xaec': [
            ('\xb7\xe0\xa4l\xaec\xacP\xc5]', None, 0, 1, (21, 69), 0, None, 255, 's', 0, 0, None, None, None)] },
    9125: {
        '\xb3B\xa4k\xaec': [
            ('\xb3B\xa4k\xaec\xacP\xc5]', None, 0, 1, (21, 69), 0, None, 255, 'c', 0, 0, None, None, None)] },
    9126: {
        '\xa4\xd1\xaf\xaf\xaec': [
            ('\xa4\xd1\xaf\xaf\xaec\xacP\xc5]', None, 0, 1, (52, 87), 0, None, 255, 't', 0, 0, None, None, None)] },
    9127: {
        '\xa4\xd1\xe7\xb2\xaec': [
            ('\xa4\xd1\xe7\xb2\xaec\xacP\xc5]', None, 0, 1, (52, 87), 0, None, 255, 't', 0, 0, None, None, None)] },
    9128: {
        '\xaeg\xa4\xe2\xaec': [
            ('\xaeg\xa4\xe2\xaec\xacP\xc5]', None, 0, 1, (96, 63), 0, None, 255, 's', 0, 0, None, None, None)] },
    9129: {
        '\xbc\xaf\xbd~\xaec': [
            ('\xbc\xaf\xbd~\xaec\xacP\xc5]', None, 0, 1, (96, 63), 0, None, 255, 'm', 0, 0, None, None, None)] },
    9130: {
        '\xa4\xf4\xb2~\xaec': [
            ('\xa4\xf4\xb2~\xaec\xacP\xc5]', None, 0, 1, (93, 50), 0, None, 255, 's', 0, 0, None, None, None)] },
    9131: {
        '\xc2\xf9\xb3\xbd\xaec': [
            ('\xc2\xf9\xb3\xbd\xaec\xacP\xc5]', None, 0, 1, (93, 50), 0, None, 255, 's', 0, 0, None, None, None)] },
    9148: {
        '\xc0\xb0\xbe\xd4\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (110, 92), 0, None, 255, 'ydlb', 0, 0, None, None, None)] },
    9156: {
        '\xbe\xa4\xa9\xfa\xc2\xed': [
            ('\xa8\xdf\xaf\xab\xa4\xa7\xb6\xf0', None, 0, 1, (56, 49), 0, None, 255, 's', 0, 0, None, None, None)] },
    9157: {
        '\xa9]\xb9\xf5\xc2\xed': [
            ('\xafT\xaf\xab\xa4\xa7\xb6\xf0', None, 0, 1, (63, 39), 0, None, 255, 's', 0, 0, None, None, None)] },
    9158: {
        '\xa5\xad\xa6w\xb4\xe4': [
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (52, 101), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (145, 43), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9159: {
        '\xa5j\xa4\xec\xaf\xab\xbcq': [
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (46, 96), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (102, 51), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9160: {
        '\xacP\xc1\xf7\xab\xb0': [
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (54, 69), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (136, 98), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9161: {
        '\xb2M\xb7\xcb\xab\xb0': [
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (32, 79), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (149, 113), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9162: {
        '\xb4H\xa4\xeb\xb4\xcb\xaaL': [
            ('\xbe\xa4\xa9\xfa\xc2\xed\xb6\xc7\xb0e\xa4H', None, 0, 1, (154, 19), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xbe\xa4\xa9\xfa\xc2\xed\xb6\xc7\xb0e\xa4H', None, 0, 1, (169, 86), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xa9]\xb9\xf5\xc2\xed\xb6\xc7\xb0e\xa4H', None, 0, 1, (29, 58), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xa9]\xb9\xf5\xc2\xed\xb6\xc7\xb0e\xa4H', None, 0, 1, (39, 122), 0, None, 255, 'y', 0, 0, None, None, None)] },
    9167: {
        '\xaf\xc8\xbdc\xc4v\xa7\xde\xb3\xf5': [
            ('\xbe\xdd\xa5x\xb0\xcf', None, 0, 1, (140, 78), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xb6\xc3\xb0\xab\xac\xb6\xa6\xcb', None, 0, 1, (133, 113), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xb6\xb0\xb5\xb2\xa4H', None, 0, 1, (186, 105), 0, None, 255, 'z', 0, 0, None, None, None)] },
    9169: {
        '\xa4\xf5\xb6\xb3\xaec': [
            ('\xa4\xf5\xb6\xb3\xb9D\xa4H', None, 0, 1, (134, 113), 0, None, 255, 'h', 0, 0, None, None, None)] },
    9170: {
        '\xa4\xd1\xbf\xef\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 0, 1, (150, 100), 0, None, 255, 'l', 0, 0, None, None, None),
            ('\xa4\xd1\xac\xc9\xbd\xc3\xa4h', None, 0, 1, (7, 152), 0, None, 255, 'q', 0, 0, None, None, None),
            ('\xa4\xd1\xac\xc9\xbd\xc3\xa4h', None, 0, 1, (9, 19), 0, None, 255, 'b', 0, 0, None, None, None),
            ('\xa4\xd1\xac\xc9\xbd\xc3\xa4h', None, 0, 1, (257, 145), 0, None, 255, 'x', 0, 0, None, None, None),
            ('\xa4\xd1\xac\xc9\xbd\xc3\xa4h', None, 0, 1, (272, 17), 0, None, 255, 'z', 0, 0, None, None, None),
            ('\xc5K\xa6K', None, 0, 1, (143, 112), 0, None, 255, 't', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (120, 100), 0, None, 255, 'y', 0, 0, None, None, None)] },
    9172: {
        '\xa4\xd1\xaa\xc5\xb8t\xa6a': [
            ('\xb9\xda\xaa\xc5\xc6F', None, 0, 1, (118, 67), 0, None, 255, 'm', 0, 0, None, None, None)] },
    9173: {
        '\xb6\xb3\xae\xfc\xaa\xc5\xb4\xe4': [
            ('\xb9\xda\xad\xb8\xaa\xe1', None, 0, 1, (54, 74), 0, None, 255, 'm', 0, 0, None, None, None)] },
    9199: {
        '\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (7, 152), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (9, 19), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (257, 145), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (272, 17), 0, None, 255, 'y', 0, 0, None, None, None)] },
    9200: {
        '\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (139, 78), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xa4\xf1\xaaZ\xb6\xb0\xb5\xb2\xa4H', None, 0, 1, (100, 78), 0, None, 255, 's', 0, 0, None, None, None),
            ('\xb2\xd5\xb6\xa4\xa4\xf1\xaaZ\xb6\xb0\xb5\xb2\xa4H', None, 0, 1, (180, 78), 0, None, 255, 'j', 0, 0, None, None, None)] },
    9202: {
        '\xc2\xc3\xc4_\xa6a': [
            ('\xab\xd5\xc6F\xb2\xee\xa4\xd2', None, 0, 1, (81, 65), 0, None, 255, '', 0, 0, None, None, None)] },
    9224: {
        '\xa5\xaa\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa5[\xac\xa5\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 99), 0, None, 255, '', 0, 0, None, None, None),
            ('\xabn\xbb\xbb\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (138, 12), 0, None, 255, '', 0, 0, None, None, None)] },
    9225: {
        '\xa5k\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa5[\xac\xa5\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (36, 96), 0, None, 255, '', 0, 0, None, None, None),
            ('\xabn\xbb\xbb\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 37), 0, None, 255, '', 0, 0, None, None, None)] },
    9226: {
        '\xa5\xaa\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa5[\xac\xa5\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 99), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2M\xb4P\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (138, 12), 0, None, 255, '', 0, 0, None, None, None)] },
    9227: {
        '\xa5k\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa5[\xac\xa5\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (36, 96), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2M\xb4P\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 37), 0, None, 255, '', 0, 0, None, None, None)] },
    9228: {
        '\xa5\xaa\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xabn\xbb\xbb\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (138, 12), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 99), 0, None, 255, '', 0, 0, None, None, None)] },
    9229: {
        '\xa5k\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xabn\xbb\xbb\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 37), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (36, 96), 0, None, 255, '', 0, 0, None, None, None)] },
    9230: {
        '\xa5\xaa\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xb2M\xb4P\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (138, 12), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 99), 0, None, 255, '', 0, 0, None, None, None)] },
    9231: {
        '\xa5k\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xb2M\xb4P\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 37), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (36, 96), 0, None, 255, '', 0, 0, None, None, None)] },
    9232: {
        '\xabn\xbb\xbb\xb0\xea\xb0\xf2\xa6a': [
            ('\xabn\xbb\xbb\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (32, 50), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (99, 17), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (28, 15), 0, None, 255, '', 0, 0, None, None, None)] },
    9233: {
        '\xb2M\xb4P\xb0\xea\xb0\xf2\xa6a': [
            ('\xb2M\xb4P\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (79, 59), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (102, 19), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (19, 19), 0, None, 255, '', 0, 0, None, None, None)] },
    9234: {
        '\xabn\xbb\xbb\xb0\xea\xb0\xf2\xa6a': [
            ('\xabn\xbb\xbb\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (32, 50), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (99, 17), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (28, 15), 0, None, 255, '', 0, 0, None, None, None)] },
    9235: {
        '\xb2M\xb4P\xb0\xea\xb0\xf2\xa6a': [
            ('\xb2M\xb4P\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (79, 59), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (102, 19), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (19, 19), 0, None, 255, '', 0, 0, None, None, None)] },
    9236: {
        '\xa5[\xac\xa5\xb0\xea\xb0\xf2\xa6a': [
            ('\xa5[\xac\xa5\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (90, 53), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (96, 25), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9237: {
        '\xa5[\xac\xa5\xb0\xea\xb0\xf2\xa6a': [
            ('\xa5[\xac\xa5\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (90, 53), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (96, 25), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9238: {
        '\xa4\xd1\xb9\xe7\xb0\xea\xb0\xf2\xa6a': [
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (48, 54), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (98, 30), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (25, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9239: {
        '\xa4\xd1\xb9\xe7\xb0\xea\xb0\xf2\xa6a': [
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (48, 54), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (98, 30), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (25, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9271: {
        '\xa5\xaa\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xabn\xbb\xbb\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (138, 12), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2M\xb4P\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 99), 0, None, 255, '', 0, 0, None, None, None)] },
    9272: {
        '\xa5k\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xabn\xbb\xbb\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 37), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2M\xb4P\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (36, 96), 0, None, 255, '', 0, 0, None, None, None)] },
    9273: {
        '\xa5\xaa\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa5[\xac\xa5\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 99), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (138, 12), 0, None, 255, '', 0, 0, None, None, None)] },
    9274: {
        '\xa5k\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa5[\xac\xa5\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (36, 96), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 37), 0, None, 255, '', 0, 0, None, None, None)] },
    9275: {
        '\xabn\xbb\xbb\xb0\xea\xb0\xf2\xa6a': [
            ('\xabn\xbb\xbb\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (32, 50), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (99, 17), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (28, 15), 0, None, 255, '', 0, 0, None, None, None)] },
    9276: {
        '\xa4\xd1\xb9\xe7\xb0\xea\xb0\xf2\xa6a': [
            ('\xa4\xd1\xb9\xe7\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (48, 54), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (98, 30), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (25, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9277: {
        '\xb2M\xb4P\xb0\xea\xb0\xf2\xa6a': [
            ('\xb2M\xb4P\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (79, 59), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (102, 19), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (19, 19), 0, None, 255, '', 0, 0, None, None, None)] },
    9278: {
        '\xa5[\xac\xa5\xb0\xea\xb0\xf2\xa6a': [
            ('\xa5[\xac\xa5\xb0\xea\xb9\xcf\xc4\xcb', None, 0, 1, (90, 53), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (96, 25), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (24, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9301: {
        '\xa5\xd5\xa6\xcf\xaec': [
            ('\xba\xbf\xb5X\xad}\xba\xb8', None, 0, 1, (69, 29), 0, None, 255, '', 0, 0, None, None, None)] },
    9302: {
        '\xaa\xf7\xa4\xfb\xaec': [
            ('\xaa\xfc\xb4\xb5\xb2\xf6\xa5N', None, 0, 1, (85, 65), 0, None, 255, '', 0, 0, None, None, None)] },
    9303: {
        '\xc2\xf9\xa4l\xaec': [
            ('\xa6w\xa5\xac\xa7Q', None, 0, 1, (42, 28), 0, None, 255, '', 0, 0, None, None, None)] },
    9304: {
        '\xa5\xa8\xc3\xc9\xaec': [
            ('\xbfp\xa6C', None, 0, 1, (42, 28), 0, None, 255, '', 0, 0, None, None, None)] },
    9305: {
        '\xb7\xe0\xa4l\xaec': [
            ('\xb6O\xa4\xc1\xba\xb8', None, 0, 1, (21, 69), 0, None, 255, '', 0, 0, None, None, None)] },
    9306: {
        '\xb3B\xa4k\xaec': [
            ('\xab\xa2\xb0\xa8\xa6C', None, 0, 1, (21, 69), 0, None, 255, '', 0, 0, None, None, None)] },
    9307: {
        '\xa4\xd1\xaf\xaf\xaec': [
            ('\xafQ\xa6C', None, 0, 1, (52, 87), 0, None, 255, '', 0, 0, None, None, None)] },
    9308: {
        '\xa4\xd1\xe7\xb2\xaec': [
            ('\xa4\xda\xa4\xf1\xba\xb8', None, 0, 1, (52, 87), 0, None, 255, '', 0, 0, None, None, None)] },
    9309: {
        '\xaeg\xa4\xe2\xaec': [
            ('\xa6w\xbcw\xa4\xc1\xba\xb8', None, 0, 1, (96, 63), 0, None, 255, '', 0, 0, None, None, None)] },
    9310: {
        '\xbc\xaf\xbd~\xaec': [
            ('\xab\xa2\xa5\xa7\xba\xb8', None, 0, 1, (34, 88), 0, None, 255, '', 0, 0, None, None, None)] },
    9311: {
        '\xa4\xf4\xb2~\xaec': [
            ('\xa5[\xa6\xca\xa7Q', None, 0, 1, (93, 50), 0, None, 255, '', 0, 0, None, None, None)] },
    9312: {
        '\xc2\xf9\xb3\xbd\xaec': [
            ('\xa4\xda\xa4\xc1', None, 0, 1, (93, 50), 0, None, 255, '', 0, 0, None, None, None)] },
    9321: {
        '\xa4\xda\xa7O\xb6\xf01\xbch': [
            ('\xb4c\xc5]\xbd\xf7\xc4\xa3', None, 0, 1, (19, 57), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb4c\xc5]\xbd\xf7\xc4\xa3', None, 0, 1, (38, 10), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb4c\xc5]\xbd\xf7\xc4\xa3', None, 0, 1, (79, 25), 0, None, 255, '', 0, 0, None, None, None)] },
    9322: {
        '\xa4\xda\xa7O\xb6\xf02\xbch': [
            ('\xb4c\xc5]\xb5\xb2\xac\xc9\xaev', None, 0, 1, (12, 41), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb4c\xc5]\xb5\xb2\xac\xc9\xaev', None, 0, 1, (34, 68), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb4c\xc5]\xb5\xb2\xac\xc9\xaev', None, 0, 1, (93, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9323: {
        '\xa4\xda\xa7O\xb6\xf03\xbch': [
            ('\xb4c\xc5]\xc5@\xaak', None, 0, 1, (109, 53), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xa2\xac\xf0\xb4\xb5', None, 0, 1, (80, 81), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xb8\xaf\xab\xb8\xcb\xb3\xc6', None, 0, 1, (113, 49), 0, None, 255, '', 0, 0, None, None, None)] },
    9332: {
        '\xb3\xb7\xa5M\xc6U': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9333: {
        '\xa5D\xc6U': [
            ('\xa5D\xc6U\xb6\xc7\xb0e\xa4H', None, 0, 1, (38, 35), 0, None, 255, '', 0, 0, None, None, None)] },
    9334: {
        '\xb0g\xac\xc9': [
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 0, 1, (112, 88), 0, None, 255, '', 0, 0, None, None, None)] },
    9335: {
        '\xb0g\xac\xc9': [
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 0, 1, (112, 88), 0, None, 255, '', 0, 0, None, None, None)] },
    9336: {
        '\xb0g\xac\xc9': [
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 0, 1, (112, 88), 0, None, 255, '', 0, 0, None, None, None)] },
    9337: {
        '\xc5]\xb1\xda\xaf\xb5\xb1K\xb0\xf2\xa6a': [
            ('\xc0\xb0\xac\xa3\xb9\xcf\xc4\xcb', None, 4394, 0, (60, 98), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc2y\xc5]\xa6\xe6\xb0\xca\xab\xfc\xb4\xa7\xa9x', None, 4401, 1, (48, 107), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc2y\xc5]\xa6\xe6\xb0\xca\xaav\xc0\xf8\xaev', None, 4402, 1, (36, 111), 0, None, 255, '', 0, 0, None, None, None)] },
    9338: {
        '\xa4H\xaa\xab\xbf\xef\xbe\xdc\xc6U': [
            ('\xa8\xa4\xa6\xe2\xb9w\xb3]\xba\xde\xb2z\xad\xfb', None, 0, 1, (103, 79), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xa4\xa6\xe2\xb9w\xb3]\xba\xde\xb2z\xad\xfb', None, 0, 1, (140, 96), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xa4\xa6\xe2\xb9w\xb3]\xba\xde\xb2z\xad\xfb', None, 0, 1, (175, 79), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbe\xdd\xa5x\xba\xde\xb2z\xad\xfb', None, 0, 1, (139, 78), 0, None, 255, '', 0, 0, None, None, None)] },
    9339: {
        '\xa5\xfe\xb0\xea\xaa\xa7\xc5Q\xc1\xc9\xc6U': [
            ('\xc1\xc9\xa8\xc6\xba\xde\xb2z\xad\xfb', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9340: {
        '\xc6[\xbe\xd4\xc6U': [
            ('\xbe\xd4\xb0\xab\xbf\xfd\xb9\xb3\xad\xfb', None, 0, 1, (119, 78), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xbf\xfd\xb9\xb3\xad\xfb', None, 0, 1, (139, 60), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xbf\xfd\xb9\xb3\xad\xfb', None, 0, 1, (139, 140), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbe\xd4\xb0\xab\xbf\xfd\xb9\xb3\xad\xfb', None, 0, 1, (163, 78), 0, None, 255, '', 0, 0, None, None, None)] },
    9344: {
        '\xc4_\xc2\xc3\xb7\xc7\xb3\xc6\xc6U': [
            ('\xc4_\xc2\xc3\xc2y\xa4H', None, 0, 1, (140, 78), 0, None, 255, 'b', 0, 0, None, None, None)] },
    9345: {
        '\xc4_\xc2\xc3\xa4j\xc6U': [
            ('\xc4_\xc2\xc3\xc2y\xa4H', None, 0, 1, (140, 78), 0, None, 255, 'b', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 3006, 1, (140, 116), 0, None, 255, 'y', 0, 0, None, None, None)] },
    9346: {
        '\xad\xd7\xc3\xb9\xb4\xcb\xaaL': [
            ('\xa5\xd5\xb4H\xb0\xf2\xa6a\xa4\xde\xb8\xf4\xa4H', None, 0, 1, (10, 128), 0, None, 255, '', 0, 0, None, None, None),
            ('\xafP\xb5K\xb0\xf2\xa6a\xa4\xde\xb8\xf4\xa4H', None, 0, 1, (271, 22), 0, None, 255, '', 0, 0, None, None, None)] },
    9347: {
        '\xb8t\xb2\xaa\xael\xa8\xa6': [
            ('\xbb\xe2\xa7L', None, 0, 1, (15, 108), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xc6\xb0\xc8\xa9x', None, 0, 1, (153, 34), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xa7L', None, 0, 1, (151, 42), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb1\xd2\xa4j\xac\xb6', None, 0, 1, (42, 41), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb1\xd2\xa4j\xac\xb6', None, 0, 1, (60, 91), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb1\xd2\xa4j\xac\xb6', None, 0, 1, (130, 80), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5D\xab\xd3', None, 0, 1, (148, 30), 0, None, 255, '', 0, 0, None, None, None)] },
    9348: {
        '\xb8\xa8\xb3\xb7\xa6B\xad\xec': [
            ('\xbb\xe2\xa7L', None, 0, 1, (221, 15), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xc6\xb0\xc8\xa9x', None, 0, 1, (35, 131), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xa7L', None, 0, 1, (50, 128), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb1\xd2\xa4j\xac\xb6', None, 0, 1, (61, 78), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb1\xd2\xa4j\xac\xb6', None, 0, 1, (133, 75), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb1\xd2\xa4j\xac\xb6', None, 0, 1, (179, 128), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5D\xab\xd3', None, 0, 1, (21, 137), 0, None, 255, '', 0, 0, None, None, None)] },
    9349: {
        '\xaa\xec\xb6\xb3\xa5\xad\xad\xec': [
            ('\xb1i\xa4\xd1\xaev', None, 4977, 1, (34, 45), 0, None, 255, '', 0, 0, None, None, None)] },
    9350: {
        '\xb9\xda\xb7Q\xaei\xc4\xfd\xc0]\xa4@\xbch': [
            ('\xa7L\xc1{\xab\xb0\xa4U', None, 0, 1, (132, 63), 0, None, 255, '', 0, 0, None, None, None),
            ('\xabD\xa4Z\xaa\xba\xb1B\xc2\xa7', None, 0, 1, (182, 70), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5[\xac\xa5\xb0\xea\xa4\xfd', None, 0, 1, (158, 54), 0, None, 255, '', 0, 0, None, None, None),
            ('\xafT\xb1\xda\xa4\xa7\xa4\xfd', None, 0, 1, (118, 54), 0, None, 255, '', 0, 0, None, None, None),
            ('\xabn\xbb\xbb\xb0\xea\xa4\xfd', None, 0, 1, (159, 73), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4d\xa8\xbd\xa8\xab\xb3\xe6\xc3M', None, 0, 1, (187, 88), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb2M\xb4P\xb0\xea\xa4\xfd', None, 0, 1, (100, 95), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb8s\xb6\xaf\xb3v\xb3\xc0', None, 0, 1, (86, 83), 0, None, 255, '', 0, 0, None, None, None),
            ('\xaf\xab\xc3~\xa5P\xc3~', None, 0, 1, (110, 78), 0, None, 255, '', 0, 0, None, None, None),
            ('\xacD\xbe\xd4\xaf\xab\xa4\xd1\xa7L', None, 0, 1, (141, 83), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa7l\xa6\xe5\xb0\xad', None, 0, 1, (191, 76), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xdf\xa4\xdf\xac\xdb\xa6L', None, 0, 1, (90, 64), 0, None, 255, '', 0, 0, None, None, None),
            ('\xad\xd7\xbb\xb7', None, 1002, 2, (83, 116), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa7\xa4\xc3M\xaei\xa5\xdc', None, 0, 1, (162, 98), 0, None, 255, '', 0, 0, None, None, None)] },
    9351: {
        '\xb9\xda\xb7Q\xaei\xc4\xfd\xc0]\xa4G\xbch': [
            ('\xaa\xfc\xa7V\xa4\xf1\xb4\xb5', None, 0, 1, (93, 97), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbe\xf7\xb1\xf1\xab\xd2\xb0\xea', None, 0, 1, (97, 86), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xa4\xb0\xab\xa4j\xb7|', None, 0, 1, (89, 71), 0, None, 255, '', 0, 0, None, None, None),
            ('\xaf\xf0\xb6a\xa8\xeb\xaf\xb3', None, 0, 1, (188, 81), 0, None, 255, '', 0, 0, None, None, None),
            ('\xafT\xb1\xda\xb6i\xa4\xc6', None, 0, 1, (154, 75), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb5\xde\xc3d\xa4j\xb6\xb0\xa6X', None, 0, 1, (166, 98), 0, None, 255, '', 0, 0, None, None, None),
            ('\xac\xe8\xc2\xa7', None, 1104, 1, (82, 116), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xa4\xfd', None, 0, 1, (165, 59), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xdf\xb1\xda\xb6i\xa4\xc6', None, 0, 1, (127, 77), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa8\xdf\xb1\xda\xa4\xa7\xa4\xfd', None, 0, 1, (146, 89), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbb\xb7\xa5j\xb3\xa1\xb8\xa8', None, 0, 1, (128, 54), 0, None, 255, '', 0, 0, None, None, None)] },
    9352: {
        '\xc4Q\xc5\xef\xac}': [
            ('\xc4Q\xc5\xef\xb9D\xa4H', None, 0, 1, (105, 7), 0, None, 255, '', 0, 0, None, None, None)] },
    9353: {
        '\xb6\xc0\xa9\xfc\xael\xa8\xa6': [
            ('\xbba\xa4\xf5\xb0\xf2\xa6a', None, 0, 1, (175, 15), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbba\xa4\xf5\xa5k\xb8\xf4\xa8\xbe\xbfm\xc2I', None, 0, 1, (150, 88), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbba\xa4\xf5\xa4\xa4\xb8\xf4\xa8\xbe\xbfm\xc2I', None, 0, 1, (105, 52), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbba\xa4\xf5\xa5D\xb1N', None, 0, 1, (155, 30), 0, None, 255, '', 0, 0, None, None, None),
            ('\xbba\xa4\xf5\xa5\xaa\xb8\xf4\xa8\xbe\xbfm\xc2I', None, 0, 1, (100, 21), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xe1\xb6\xd4\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (54, 127), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xe1\xb6\xd4\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (159, 15), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xb6\xc7\xb0e\xa4H', None, 0, 1, (15, 99), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xeb\xb6\xc7\xb0e\xa4H', None, 0, 1, (141, 17), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb3\xa5\xa5~\xa9\xc7\xc3~\xb1_\xa5\xde', None, 0, 1, (60, 50), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb3\xa5\xa5~\xa9\xc7\xc3~\xb1_\xa5\xde', None, 0, 1, (103, 100), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb5\xb5\xaa\xa2\xb0\xf2\xa6a', None, 0, 1, (30, 123), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb5\xb5\xaa\xa2\xa5k\xb8\xf4\xa8\xbe\xbfm\xc2I', None, 0, 1, (12, 62), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb5\xb5\xaa\xa2\xa4\xa4\xb8\xf4\xa8\xbe\xbfm\xc2I', None, 0, 1, (36, 86), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb5\xb5\xaa\xa2\xa5D\xb1N', None, 0, 1, (35, 108), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb5\xb5\xaa\xa2\xa5\xaa\xb8\xf4\xa8\xbe\xbfm\xc2I', None, 0, 1, (86, 134), 0, None, 255, '', 0, 0, None, None, None)] },
    9354: {
        '\xb7\xc7\xb3\xc6\xa4j\xc6U': [
            ('\xad\xdc\xaew\xba\xde\xb2z\xad\xfb', None, 0, 1, (135, 92), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xb9\xa4\xd1\xbe\xf7', None, 0, 1, (139, 78), 0, None, 255, '', 0, 0, None, None, None)] },
    9355: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xe7\xb8\xb3D\xa7\xaf', None, 0, 1, (42, 28), 0, None, 255, 'fsy', 0, 0, None, None, None)] },
    9356: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xbba\xafT\xa7\xaf', None, 0, 1, (35, 26), 0, None, 255, 'cly', 0, 0, None, None, None)] },
    9357: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xae\xe7\xaa\xe1\xa7\xaf', None, 0, 1, (42, 28), 0, None, 255, 'thy', 0, 0, None, None, None)] },
    9358: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xa5\xa8\xc3\xc9\xa7\xaf', None, 0, 1, (35, 26), 0, None, 255, 'jxy', 0, 0, None, None, None)] },
    9359: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xa7Q\xa4\xf6\xab\xcd', None, 0, 1, (37, 26), 0, None, 255, 'lzy', 0, 0, None, None, None)] },
    9360: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xa4H\xb3\xbd\xa7\xaf', None, 0, 1, (85, 67), 0, None, 255, 'ryy', 0, 0, None, None, None)] },
    9361: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xb4c\xba\xb5\xa7\xaf', None, 0, 1, (37, 26), 0, None, 255, 'exy', 0, 0, None, None, None)] },
    9362: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xa4j\xa4O\xa4\xfb\xa7\xaf', None, 0, 1, (85, 67), 0, None, 255, 'dlny', 0, 0, None, None, None)] },
    9363: {
        '\xad\xab\xb6\xa7\xb5n\xb0\xaa': [
            ('\xbdE\xc5]', None, 0, 1, (92, 20), 0, None, 255, 'wm', 0, 0, None, None, None)] },
    9372: {
        '\xbe\xd4\xb3\xf5\xb7\xc7\xb3\xc6\xc6U': [
            ('\xa4T\xa4Q\xa4\xbb\xadp\xb6\xc7\xb0e\xa4H', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9373: {
        '\xbe\xd4\xb3\xf5\xbf\xef\xbe\xdc\xc6U': [
            ('\xa4T\xa4Q\xa4\xbb\xadp\xb6\xc7\xb0e\xa4H', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9374: {
        '\xa4T\xa4Q\xa4\xbb\xadp\xbe\xd4\xb3\xf5': [
            ('\xa4T\xa4Q\xa4\xbb\xadp\xb6\xc7\xb0e\xa4H', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9380: {
        '\xaf\xab\xaf\xb5\xaeq': [
            ('\xaa\xfc\xd0\xb1\xaak\xaev', None, 1044, 2, (42, 22), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xda\xb9\xcf\xbe|', None, 1043, 2, (93, 54), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4E\xa4Q\xbe\xa4\xad\xa9\xaa\xf8', None, 1042, 2, (105, 50), 0, None, 255, '', 0, 0, None, None, None)] },
    9381: {
        '\xac\xa1\xb0\xca\xb7\xc7\xb3\xc6\xc6U': [
            ('\xa9\xfa\xa4\xeb\xab\xb0\xb6\xc7\xb0e\xa4H', None, 2002, 1, (139, 78), 0, None, 255, '', 0, 0, None, None, None)] },
    9382: {
        '\xc6Z\xaf\xee\xa4\xdb\xb9\xd2': [
            ('\xb8\xad\xba\xb8\xa4\xe5', None, 2011, 1, (68, 69), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb8\xad\xba\xb8\xa4\xe5', None, 2012, 1, (161, 71), 0, None, 255, '', 0, 0, None, None, None)] },
    9386: {
        '\xa4\xf5\xb6\xb3\xaec': [
            ('', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9387: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xaaQ\xa6\xcb', None, 0, 1, (65, 100), 0, None, 255, '', 0, 0, None, None, None)] },
    9388: {
        '\xac\xfc\xad\xb9\xa7{\xa6a\xb9\xcf': [
            ('\xb6\xc7\xbb\xa1\xaa\xba\xb3\xb7\xa4k', None, 0, 1, (140, 82), 0, None, 255, '', 0, 0, None, None, None)] },
    9389: {
        '\xa6a\xba\xbb\xb9D': [
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (74, 72), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb4H\xa6a\xba\xbb\xa8\xcf', None, 0, 1, (37, 9), 0, None, 255, '', 0, 0, None, None, None),
            ('\xaa\xa2\xa6a\xba\xbb\xa8\xcf', None, 0, 1, (20, 57), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc2\xe0\xbd\xfc\xc0F\xc3\xb9', None, 0, 1, (84, 30), 0, None, 255, '', 0, 0, None, None, None)] },
    9390: {
        '\xbej\xb0\xad\xb9D': [
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (65, 13), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc5@\xa8\xad\xbej\xb0\xad', None, 0, 1, (19, 26), 0, None, 255, '', 0, 0, None, None, None),
            ('\xafe\xa6\xe6\xbej\xb0\xad', None, 0, 1, (36, 48), 0, None, 255, '', 0, 0, None, None, None),
            ('\xad\xb9\xa4O\xbej\xb0\xad', None, 0, 1, (112, 62), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa7]\xc6F\xbej\xb0\xad', None, 0, 1, (102, 17), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa9]\xc3\xb9\xabb', None, 0, 1, (80, 50), 0, None, 255, '', 0, 0, None, None, None)] },
    9391: {
        '\xafb\xa5\xcd\xb9D': [
            ('\xbba\xaaL\xc3~', None, 0, 1, (26, 19), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (86, 25), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa9\xfa\xa4\xf5\xc3~', None, 0, 1, (29, 74), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xe3\xad\xb7\xc3~', None, 0, 1, (93, 79), 0, None, 255, '', 0, 0, None, None, None)] },
    9392: {
        '\xad\xd7\xc3\xb9\xb9D': [
            ('\xaa\xfc\xad\xd7\xc3\xb9\xa4\xfd', None, 0, 1, (90, 69), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (71, 38), 0, None, 255, '', 0, 0, None, None, None)] },
    9393: {
        '\xad\xd7\xc3\xb9\xa4\xdb\xb9\xd2': [
            ('\xaa\xfc\xad\xd7\xc3\xb9\xa4\xfd', None, 0, 1, (94, 57), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (66, 60), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa6a\xad\xd7\xc3\xb9', None, 0, 1, (15, 93), 0, None, 255, '', 0, 0, None, None, None),
            ('\xad\xb7\xad\xd7\xc3\xb9', None, 0, 1, (20, 10), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xf5\xad\xd7\xc3\xb9', None, 0, 1, (162, 87), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb9p\xad\xd7\xc3\xb9', None, 0, 1, (167, 10), 0, None, 255, '', 0, 0, None, None, None)] },
    9394: {
        '\xa4H\xb6\xa1\xb9D': [
            ('\xaff\xadW', None, 0, 1, (67, 29), 0, None, 255, '', 0, 0, None, None, None),
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (42, 28), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa6\xd1\xadW', None, 0, 1, (17, 48), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa5\xcd\xadW', None, 0, 1, (21, 14), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa6\xba\xadW', None, 0, 1, (68, 7), 0, None, 255, '', 0, 0, None, None, None)] },
    9395: {
        '\xa4\xd1\xac\xc9\xb9D': [
            ('\xb6\xc7\xb0e\xb6\xf0\xc6F', None, 0, 1, (93, 21), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xd2\xc4\xc0\xa4\xd1', None, 0, 1, (21, 69), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xf5\xacP', None, 0, 1, (57, 47), 0, None, 255, '', 0, 0, None, None, None),
            ('\xaa\xf7\xacP', None, 0, 1, (57, 70), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xec\xacP', None, 0, 1, (62, 10), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4\xf4\xacP', None, 0, 1, (16, 20), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa4g\xacP', None, 0, 1, (95, 63), 0, None, 255, '', 0, 0, None, None, None)] },
    9396: {
        '\xc0\xb0\xac\xa3\xa7G\xb0}\xa4j\xc6U': [
            ('\xae]\xc2\xc1', None, 0, 1, (140, 78), 0, None, 255, '', 0, 0, None, None, None)] },
    9408: {
        '\xad\xb7\xb6\xb3\xbf\xfd': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9409: {
        '\xb6\xc2\xb4\xcb\xaaL\xa9]\xb0g\xb5\xea\xb9\xd2': [
            ('\xa5\xd5\xab\xd5\xc4\xf5', None, 0, 1, (236, 113), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 1003, 2, (218, 132), 0, None, 255, '', 0, 0, None, None, None)] },
    9410: {
        '\xc4\xf5\xadY\xa6x': [
            ('\xa4p\xbd\xba', None, 0, 1, (46, 29), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 1003, 2, (31, 35), 0, None, 255, '', 0, 0, None, None, None)] },
    9411: {
        '\xb6\xc2\xb4\xcb\xaaL\xbe\xa4\xa5\xfa\xb2b\xa4g': [
            ('\xb6\xc2\xa4s\xa6\xd1\xa7\xaf', None, 0, 1, (149, 121), 0, None, 255, '', 0, 0, None, None, None),
            ('\xab\xbe\xab\xbe', None, 0, 1, (30, 97), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 1003, 2, (92, 134), 0, None, 255, '', 0, 0, None, None, None)] },
    9412: {
        '\xaf\xab\xaf\xb5\xae\xfc\xb0\xec': [
            ('\xc2\xf9\xb3\xbd\xaec\xacP\xc5]', None, 0, 1, (51, 40), 0, None, 255, '', 0, 0, None, None, None)] },
    9418: {
        '\xb9\xda\xb9\xd2\xa5X\xb5o\xc6U': [
            ('\xb9\xda\xb9\xd2\xac\xdd\xaa\xf9\xa4H', None, 0, 1, (140, 78), 0, None, 255, '', 0, 0, None, None, None)] },
    9419: {
        '\xa4\xd1\xa6r\xb7\xc7\xb3\xc6\xc6U': [
            ('\xb6\xc7\xb0e\xa9x', None, 0, 1, (138, 78), 0, None, 255, 'csg', 0, 0, None, None, None)] },
    9420: {
        '\xa6a\xa6r\xb7\xc7\xb3\xc6\xc6U': [
            ('\xb6\xc7\xb0e\xa9x', None, 0, 1, (138, 78), 0, None, 255, 'csg', 0, 0, None, None, None)] },
    9421: {
        '\xb6\xc0\xa4\xd1\xa8F\xbaz': [
            ('\xb6\xc7\xb0e\xa9x', None, 0, 1, (12, 122), 0, None, 255, 'csg', 0, 0, None, None, None),
            ('\xb6\xc7\xb0e\xa9x', None, 0, 1, (226, 9), 0, None, 255, 'csg', 0, 0, None, None, None),
            ('\xaf\xab\xaaZ\xb4L', None, 0, 1, (146, 77), 0, None, 255, 'swz', 0, 0, None, None, None)] },
    9422: {
        '\xb6\xb3\xae\xfc\xa5P\xb9\xd2': [
            ('\xad^\xb6\xaf\xa4\xa7\xb6\xf0', None, 0, 1, (85, 35), 0, None, 255, 'yxzt', 0, 0, None, None, None)] },
    9428: {
        '\xc0\xb0\xbe\xd4\xa4\xf1\xaaZ\xb3\xf5': [
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (7, 152), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (9, 19), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (257, 145), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H', None, 0, 1, (272, 17), 0, None, 255, 'bzjyr', 0, 0, None, None, None),
            ('\xa4\xf1\xaaZ\xb3\xf5\xb6\xc7\xb0e\xad\xfb', None, 0, 1, (140, 76), 0, None, 255, 'bwccsy', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (110, 92), 0, None, 255, 'ydlb', 0, 0, None, None, None)] },
    9429: {
        '\xa7\xf0\xa4\xe8\xb0\xf2\xa6a': [
            ('\xa7\xf0\xa4\xe8\xb9\xcf\xc4\xcb', None, 0, 1, (142, 108), 0, None, 255, 'gftt', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (114, 19), 0, None, 255, 'yljcss', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (37, 108), 0, None, 255, 'zljcss', 0, 0, None, None, None)] },
    9430: {
        '\xa6u\xa4\xe8\xb0\xf2\xa6a': [
            ('\xa6u\xa4\xe8\xb9\xcf\xc4\xcb', None, 0, 1, (55, 30), 0, None, 255, 'sftt', 0, 0, None, None, None),
            ('\xa5k\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (126, 91), 0, None, 255, 'yljcss', 0, 0, None, None, None),
            ('\xa5\xaa\xb8\xf4\xadx\xb6\xc7\xb0e\xaev', None, 0, 1, (14, 96), 0, None, 255, 'zljcss', 0, 0, None, None, None)] },
    9431: {
        '\xa5k\xb8\xf4\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa7\xf0\xa4\xe8\xb0\xf2\xa6a\xa4J\xa4f', None, 0, 1, (24, 99), 0, None, 255, 'gfjdrk', 0, 0, None, None, None),
            ('\xa6u\xa4\xe8\xb0\xf2\xa6a\xa4J\xa4f', None, 0, 1, (138, 12), 0, None, 255, 'sfjdrk', 0, 0, None, None, None)] },
    9432: {
        '\xa5\xaa\xb8\xf4\xb6i\xa7\xf0\xb8\xf4\xbdu': [
            ('\xa7\xf0\xa4\xe8\xb0\xf2\xa6a\xa4J\xa4f', None, 0, 1, (36, 96), 0, None, 255, 'gfjdrk', 0, 0, None, None, None),
            ('\xa6u\xa4\xe8\xb0\xf2\xa6a\xa4J\xa4f', None, 0, 1, (126, 37), 0, None, 255, 'sfjdrk', 0, 0, None, None, None)] },
    9433: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (65, 46), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9434: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (82, 48), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9435: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (50, 30), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9436: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (100, 70), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9437: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (40, 55), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9438: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (120, 68), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9439: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (103, 63), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9440: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (113, 60), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9441: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (120, 55), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9442: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (100, 70), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9443: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (85, 60), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9444: {
        '\xad^\xb6\xaf\xa4j\xb7|\xb7\xc7\xb3\xc6\xc6U': [
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (7, 152), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (9, 19), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (257, 145), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xa4j\xb7|\xb1\xb5\xab\xdd\xa4H', None, 4425, 1, (272, 17), 0, None, 255, 'y', 0, 0, None, None, None)] },
    9445: {
        '\xc3~\xaf\xab\xa4s': [
            ('\xc3\xc4\xa9\xb1', None, 1015, 2, (130, 38), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9446: {
        '\xab_\xc0I\xc0\xe7\xa6a': [
            ('\xab_\xc0I\xa4\xde\xbe\xc9\xa4H', None, 0, 1, (139, 78), 0, None, 255, 'mxydr', 0, 0, None, None, None)] },
    9448: {
        '\xad\xab\xa5\xcd\xa4\xa7\xa6a': [
            ('\xad\xab\xa5\xcd\xa4\xa7\xaa\xf9', None, 0, 1, (36, 38), 0, None, 255, 'cszm', 0, 0, None, None, None)] },
    9449: {
        '\xacy\xb6\xb3\xb3\xa1\xb8\xa8': [
            ('\xacy\xb6\xb3\xa4\xf3\xb1\xda\xb1\xda\xaa\xf8', None, 0, 1, (94, 56), 0, None, 255, 'lyszzz', 0, 0, None, None, None)] },
    9450: {
        '\xa4E\xbe\xa4\xb3\xa1\xb8\xa8': [
            ('\xa4E\xbe\xa4\xa4\xf3\xb1\xda\xad\xba\xbb\xe2', None, 0, 1, (94, 56), 0, None, 255, 'jlszsl', 0, 0, None, None, None)] },
    9451: {
        '\xaaw\xaaw\xb9\xea\xc5\xe7\xb3\xf5': [
            ('\xa4d\xb7\xcb\xaf\xbe\xa1P\xad\xb7\xbbR', None, 0, 1, (110, 90), 0, None, 255, 'qxwfw', 0, 0, None, None, None),
            ('\xa6\xe8\xa4i\xa1P\xc2O\xaaL\xb1K\xbby', None, 0, 1, (170, 90), 0, None, 255, 'xxclmy', 0, 0, None, None, None),
            ('\xc1\xa8\xc1\xa8\xa6w\xa1P\xa8\xaa\xc0\xfb', None, 0, 1, (140, 68), 0, None, 255, 'wwact', 0, 0, None, None, None)] },
    9452: {
        '\xc5]\xb4\xb9\xb5\xf5\xc1_': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9453: {
        '\xaf\xab\xa4\xa7\xa4\xe8\xa6\xe0': [
            ('\xb9\xda\xa4\xa7\xacP', None, 0, 1, (33, 88), 0, None, 255, 'mzx', 0, 0, None, None, None)] },
    9454: {
        '\xa6u\xa4\xe8\xa5D\xab\xb0': [
            ('\xa6u\xa4\xe8\xab\xfc\xb4\xa7', None, 0, 1, (68, 37), 0, None, 255, 'sfzh', 0, 0, None, None, None)] },
    9455: {
        '\xa6u\xa4\xe8\xa5D\xab\xb0': [
            ('\xa6u\xa4\xe8\xab\xfc\xb4\xa7', None, 0, 1, (56, 34), 0, None, 255, 'sfzh', 0, 0, None, None, None)] },
    9456: {
        '\xa6u\xa4\xe8\xa5D\xab\xb0': [
            ('\xa6u\xa4\xe8\xab\xfc\xb4\xa7', None, 0, 1, (72, 54), 0, None, 255, 'sfzh', 0, 0, None, None, None)] },
    9457: {
        '\xa6u\xa4\xe8\xa5D\xab\xb0': [
            ('\xa6u\xa4\xe8\xab\xfc\xb4\xa7', None, 0, 1, (62, 34), 0, None, 255, 'sfzh', 0, 0, None, None, None)] },
    9458: {
        '\xa6\xe8\xaa\xf9': [
            ('\xab\xb0\xaa\xf9\xa6u\xb1N', None, 0, 1, (61, 68), 0, None, 255, 'cmsj', 0, 0, None, None, None),
            ('\xa7\xf0\xa4\xe8\xc0\xe7\xa6a', None, 0, 1, (152, 19), 0, None, 255, 'gfyd', 0, 0, None, None, None)] },
    9459: {
        '\xaaF\xaa\xf9': [
            ('\xab\xb0\xaa\xf9\xa6u\xb1N', None, 0, 1, (61, 68), 0, None, 255, 'cmsj', 0, 0, None, None, None),
            ('\xa7\xf0\xa4\xe8\xc0\xe7\xa6a', None, 0, 1, (152, 19), 0, None, 255, 'gfyd', 0, 0, None, None, None)] },
    9460: {
        '\xa7\xf0\xa4\xe8\xc0\xe7\xa6a': [
            ('\xa7\xf0\xa4\xe8\xab\xfc\xb4\xa7', None, 0, 1, (122, 66), 0, None, 255, 'gfzh', 0, 0, None, None, None),
            ('\xa6V\xaaF\xaa\xf9\xb6i\xb5o', None, 0, 1, (14, 112), 0, None, 255, 'xdmjf', 0, 0, None, None, None),
            ('\xa6V\xabn\xaa\xf9\xb6i\xb5o', None, 0, 1, (14, 3), 0, None, 255, 'xnmjf', 0, 0, None, None, None)] },
    9461: {
        '\xaaZ\xaaL\xa4j\xb7|': [
            ('\xbfW\xa9t\xa8D\xb1\xd1', None, 0, 1, (168, 92), 0, None, 255, 'dgqb', 0, 0, None, None, None),
            ('\xa4\xe8\xa4V', None, 0, 1, (140, 97), 0, None, 255, 'fz', 0, 0, None, None, None),
            ('\xad^\xb6\xaf\xaei\xb0\xcf', None, 0, 1, (109, 94), 0, None, 255, 'yxzq', 0, 0, None, None, None)] },
    9463: {
        '\xae\xfc\xa5~\xa5P\xb9\xd21\xbch': [
            ('\xaf\xab\xbd\xde\xa6u\xbd\xc3', None, 0, 1, (22, 97), 0, None, 255, 'szsw', 0, 0, None, None, None)] },
    9464: {
        '\xae\xfc\xa5~\xa5P\xb9\xd22\xbch': [
            ('\xaf\xab\xa4\xfb\xa6u\xbd\xc3', None, 0, 1, (122, 71), 0, None, 255, 'snsw', 0, 0, None, None, None)] },
    9465: {
        '\xae\xfc\xa5~\xa5P\xb9\xd23\xbch': [
            ('\xaf\xab\xa8\xdf\xa6u\xbd\xc3', None, 0, 1, (75, 60), 0, None, 255, 'stsw', 0, 0, None, None, None)] },
    9466: {
        '\xae\xfc\xa5~\xa5P\xb9\xd24\xbch': [
            ('\xaf\xab\xb9\xab\xa6u\xbd\xc3', None, 0, 1, (21, 69), 0, None, 255, 'sssw', 0, 0, None, None, None)] },
    9467: {
        '\xae\xfc\xa5~\xa5P\xb9\xd25\xbch': [
            ('\xa5P\xb9\xd2\xaf\xab\xa6\xcf', None, 0, 1, (56, 25), 0, None, 255, 'xjsy', 0, 0, None, None, None)] },
    9468: {
        '\xa8M\xbe\xd4\xa4\xd1\xa4U\xb7|\xb3\xf5': [
            ('\xa5[\xac\xa5\xb0\xea\xa4\xfd', None, 0, 1, (168, 92), 0, None, 255, 'jlgw', 0, 0, None, None, None),
            ('\xb3Z\xa8\xe6', None, 0, 1, (140, 78), 0, None, 255, 'jl', 0, 0, None, None, None),
            ('\xabn\xbb\xbb\xb0\xea\xa4\xfd', None, 0, 1, (112, 92), 0, None, 255, 'nygw', 0, 0, None, None, None),
            ('\xb2M\xb4P\xb0\xea\xa4\xfd', None, 0, 1, (168, 64), 0, None, 255, 'qlgw', 0, 0, None, None, None),
            ('\xa4\xd1\xb9\xe7\xb0\xea\xa4\xfd', None, 0, 1, (112, 64), 0, None, 255, 'tngw', 0, 0, None, None, None)] },
    9469: {
        '\xb9C\xc0\xb8\xad\xe3\xb3\xc6\xc6U': [
            ('\xb4I\xa5\xd2\xa4\xd1\xa4U\xb6\xc7\xb0e\xa4H', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9470: {
        '\xb9C\xc0\xb8\xbf\xef\xbe\xdc\xc6U': [
            ('\xb4I\xa5\xd2\xa4\xd1\xa4U\xb6\xc7\xb0e\xa4H', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9471: {
        '\xb4I\xa5\xd2\xa4\xd1\xa4U': [
            ('\xb4I\xa5\xd2\xa4\xd1\xa4U\xb6\xc7\xb0e\xa4H', None, 0, 1, (140, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9472: {
        '\xa4\xd1\xc5]\xb7\xb5': [
            ('\xa4\xd1\xc5]boss', None, 0, 1, (88, 64), 0, None, 255, 'tmboss', 0, 0, None, None, None)] },
    9473: {
        '\xaf\xab\xaec\xb7\xc7\xb3\xc6\xc6U': [
            ('\xab_\xc0I\xa4\xfd', None, 1001, 1, (140, 78), 0, None, 255, 'mxw', 0, 0, None, None, None)] },
    9474: {
        '\xb6\xb3\xb5\xea\xa4W\xaec\xa4@\xbch': [
            ('\xb6\xc7\xb0e\xaak\xb0}', None, 1006, 1, (44, 82), 0, None, 255, 'csfz', 0, 0, None, None, None),
            ('\xad\xf3\xab\xa2\xa4G\xb1N', None, 1002, 1, (58, 71), 0, None, 255, 'hhej', 0, 0, None, None, None),
            ('\xab_\xc0I\xa4\xfd', None, 2001, 1, (25, 9), 0, None, 255, 'mxw', 0, 0, None, None, None)] },
    9475: {
        '\xb6\xb3\xb5\xea\xa4W\xaec\xa4G\xbch': [
            ('\xb6\xc7\xb0e\xaak\xb0}', None, 1007, 1, (94, 8), 0, None, 255, 'csfz', 0, 0, None, None, None),
            ('\xab_\xc0I\xa4\xfd', None, 3001, 1, (108, 109), 0, None, 255, 'mxw', 0, 0, None, None, None),
            ('\xa4T\xa4~\xb0}\xa1P\xa6a', None, 1010, 1, (40, 16), 0, None, 255, 'sczd', 0, 0, None, None, None),
            ('\xa4T\xa4~\xb0}\xa1P\xa4H', None, 1011, 1, (86, 44), 0, None, 255, 'sczr', 0, 0, None, None, None),
            ('\xa4T\xa4~\xb0}\xa1P\xa4\xd1', None, 1009, 1, (29, 48), 0, None, 255, 'sczt', 0, 0, None, None, None)] },
    9476: {
        '\xb6\xb3\xb5\xea\xa4W\xaec\xa4T\xbch': [
            ('\xab_\xc0I\xa4\xfd', None, 4001, 1, (30, 102), 0, None, 255, 'mxw', 0, 0, None, None, None),
            ('\xb6\xb3\xb5\xea\xa4W\xa5P', None, 1017, 1, (115, 20), 0, None, 255, 'yxsx', 0, 0, None, None, None)] },
    9477: {
        '\xb5\xd8\xa4s\xbd\xd7\xbcC': [
            ('\xac\xa1\xb0\xca\xa5D\xab\xf9\xa4H', None, 1001, 1, (140, 97), 0, None, 255, 'hdzcr', 0, 0, None, None, None)] },
    9484: {
        '\xa4H\xb1\xda\xb0\xf2\xa6a': [
            ('\xa7L\xc0\xe7', None, 5006, 1, (60, 32), 0, None, 255, 'by', 0, 0, None, None, None),
            ('\xa7L\xc0\xe7\xbdb\xb6\xf0', None, 5003, 1, (99, 18), 0, None, 255, 'byjt', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5008, 1, (6, 6), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5009, 1, (4, 73), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5010, 1, (111, 10), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xaa\xf7\xaew', None, 5005, 1, (70, 5), 0, None, 255, 'jk', 0, 0, None, None, None),
            ('\xaa\xf7\xaew\xbdb\xb6\xf0', None, 5002, 1, (27, 17), 0, None, 255, 'jkjt', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 5001, 1, (100, 56), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xb9\xcf\xc4\xcb', None, 5007, 1, (57, 68), 0, None, 255, 'tt', 0, 0, None, None, None),
            ('\xb9\xcf\xc4\xcb\xbdb\xb6\xf0', None, 5004, 1, (32, 52), 0, None, 255, 'ttjt', 0, 0, None, None, None)] },
    9485: {
        '\xa8\xdf\xb1\xda\xb0\xf2\xa6a': [
            ('\xa7L\xc0\xe7', None, 5006, 1, (126, 47), 0, None, 255, 'by', 0, 0, None, None, None),
            ('\xa7L\xc0\xe7\xbdb\xb6\xf0', None, 5003, 1, (134, 20), 0, None, 255, 'byjt', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5008, 1, (12, 6), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5009, 1, (151, 6), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5010, 1, (12, 106), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xaa\xf7\xaew', None, 5005, 1, (119, 78), 0, None, 255, 'jk', 0, 0, None, None, None),
            ('\xaa\xf7\xaew\xbdb\xb6\xf0', None, 5002, 1, (42, 17), 0, None, 255, 'jkjt', 0, 0, None, None, None),
            ('\xb9\xcf\xc4\xcb', None, 5007, 1, (84, 90), 0, None, 255, 'tt', 0, 0, None, None, None),
            ('\xb9\xcf\xc4\xcb\xbdb\xb6\xf0', None, 5004, 1, (33, 80), 0, None, 255, 'ttjt', 0, 0, None, None, None),
            ('\xc1\xa8\xc1\xa8\xa6w', None, 5001, 1, (130, 104), 0, None, 255, 'wwa', 0, 0, None, None, None)] },
    9486: {
        '\xa4\xd1\xac\xc9\xb0\xf2\xa6a': [
            ('\xa7L\xc0\xe7', None, 5006, 1, (69, 44), 0, None, 255, 'by', 0, 0, None, None, None),
            ('\xa7L\xc0\xe7\xbdb\xb6\xf0', None, 5003, 1, (27, 22), 0, None, 255, 'byjt', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5008, 1, (12, 78), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5009, 1, (7, 14), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5010, 1, (114, 12), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xaa\xf7\xaew', None, 5005, 1, (81, 10), 0, None, 255, 'jk', 0, 0, None, None, None),
            ('\xaa\xf7\xaew\xbdb\xb6\xf0', None, 5002, 1, (103, 19), 0, None, 255, 'jkjt', 0, 0, None, None, None),
            ('\xaf\xab\xaaZ\xb4L', None, 5001, 1, (99, 64), 0, None, 255, 'swz', 0, 0, None, None, None),
            ('\xb9\xcf\xc4\xcb', None, 5007, 1, (63, 62), 0, None, 255, 'tt', 0, 0, None, None, None),
            ('\xb9\xcf\xc4\xcb\xbdb\xb6\xf0', None, 5004, 1, (25, 62), 0, None, 255, 'ttjt', 0, 0, None, None, None)] },
    9487: {
        '\xa4\xbd\xa6@\xbe\xd4\xb3\xf5': [
            ('\xa8\xae\xa5\xed', None, 5004, 1, (41, 12), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5005, 1, (19, 109), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 5006, 1, (150, 30), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xaa\xf7\xc4q', None, 5001, 1, (9, 63), 0, None, 255, 'jk', 0, 0, None, None, None),
            ('\xaa\xf7\xc4q', None, 5002, 1, (76, 32), 0, None, 255, 'jk', 0, 0, None, None, None),
            ('\xaa\xf7\xc4q', None, 5003, 1, (132, 108), 0, None, 255, 'jk', 0, 0, None, None, None)] },
    9489: {
        '\xaa\xb1\xaea\xa8\xa3\xad\xb1\xb7|': [
            ('\xac\xa1\xb0\xca\xa5D\xab\xf9\xa4H', None, 1001, 1, (140, 97), 0, None, 255, 'hdzcr', 0, 0, None, None, None)] },
    9492: {
        '\xac\xa1\xb0\xca\xb7\xc7\xb3\xc6\xc6U': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9493: {
        '\xaf\xab\xb1\xda\xc0\xe7\xa6a': [
            ('\xb0\xc6\xa9x', None, 0, 1, (121, 63), 0, None, 255, 'fg', 0, 0, None, None, None),
            ('\xc4q\xb3\xf5\xa6u\xbd\xc3', None, 0, 1, (22, 63), 0, None, 255, 'kcsw', 0, 0, None, None, None),
            ('\xabe\xbdu\xb6\xc7\xb0e', None, 0, 1, (32, 14), 0, None, 255, 'sssw', 0, 0, None, None, None),
            ('\xb8t\xbcC', None, 0, 1, (114, 66), 0, None, 255, 'sj', 0, 0, None, None, None)] },
    9494: {
        '\xc5]\xb1\xda\xc0\xe7\xa6a': [
            ('\xc4q\xb3\xf5\xa6u\xbd\xc3', None, 0, 1, (8, 58), 0, None, 255, 'kcsw', 0, 0, None, None, None),
            ('\xb8\xf4\xa6\xe8\xaak', None, 0, 1, (121, 73), 0, None, 255, 'lxf', 0, 0, None, None, None),
            ('\xc5]\xb1N', None, 0, 1, (131, 72), 0, None, 255, 'mj', 0, 0, None, None, None),
            ('\xabe\xbdu\xb6\xc7\xb0e', None, 0, 1, (14, 107), 0, None, 255, 'dysw', 0, 0, None, None, None)] },
    9495: {
        '\xabe\xbdu': [
            ('\xa6a\xa4U\xc4q\xb3\xf5\xa4J\xa4f', None, 0, 1, (142, 88), 0, None, 255, 'dxkcrk', 0, 0, None, None, None),
            ('\xadx\xa4\xf5\xb6\xc2\xb0\xd3', None, 0, 1, (29, 37), 0, None, 255, 'jhhs', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xa5\xfd\xbeW', None, 0, 1, (30, 104), 0, None, 255, 'mzxf', 0, 0, None, None, None),
            ('\xc5]\xb1\xda\xa5D\xab\xd3', None, 0, 1, (62, 77), 0, None, 255, 'mzzs', 0, 0, None, None, None),
            ('\xabe\xbdu\xb1N\xadx', None, 0, 1, (126, 13), 0, None, 255, 'qxjj', 0, 0, None, None, None),
            ('\xaf\xab\xaf\xb5\xac}\xa5\xde\xa4J\xa4f', None, 0, 1, (134, 102), 0, None, 255, 'smdxrk', 0, 0, None, None, None),
            ('\xaf\xab\xb1\xda\xa5D\xab\xd3', None, 0, 1, (71, 67), 0, None, 255, 'szzs', 0, 0, None, None, None)] },
    9496: {
        '\xa6a\xa4U\xc4q\xb3\xf5': [
            ('\xb9P\xa6a\xc3~', None, 0, 1, (100, 107), 0, None, 255, 'dds', 0, 0, None, None, None)] },
    9497: {
        '\xaf\xab\xaf\xb5\xac}\xa5\xde': [
            ('\xac}\xa5\xde\xa6u\xbd\xc3', None, 0, 1, (87, 65), 0, None, 255, 'dxsw', 0, 0, None, None, None)] },
    9498: {
        '\xb8\xf3\xaaA\xc0\xb0\xac\xa3\xc1p\xc1\xc9': [
            ('\xa4\xf1\xaaZ\xb3\xf5\xbe\xc9\xaev', None, 0, 1, (140, 79), 0, None, 255, 'bwcds', 0, 0, None, None, None)] },
    9499: {
        '\xb8\xf3\xaaA\xc0\xb0\xac\xa3\xc1p\xc1\xc9': [
            ('\xc0\xb0\xac\xa3\xadx\xaev', None, 0, 1, (134, 9), 0, None, 255, 'bpjs', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 0, 1, (39, 108), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xadx\xbaX', None, 0, 1, (126, 15), 0, None, 255, 'jq', 0, 0, None, None, None)] },
    9500: {
        '\xb8\xf3\xaaA\xc0\xb0\xac\xa3\xc1p\xc1\xc9': [
            ('\xc0\xb0\xac\xa3\xadx\xaev', None, 0, 1, (134, 9), 0, None, 255, 'bpjs', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 0, 1, (39, 108), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xadx\xbaX', None, 0, 1, (126, 15), 0, None, 255, 'jq', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9501: {
        '\xb8\xf3\xaaA\xc0\xb0\xac\xa3\xc1p\xc1\xc9': [
            ('\xa8\xae\xa5\xed', None, 0, 1, (11, 127), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa8\xae\xa5\xed', None, 0, 1, (270, 22), 0, None, 255, 'cf', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9502: {
        '\xc0\xb0\xac\xa3\xc1p\xc1\xc9\xb7\xc7\xb3\xc6\xc6U': [
            ('\xc0\xb0\xac\xa3\xadx\xaev', None, 0, 1, (55, 37), 0, None, 255, 'bpjs', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9503: {
        '\xa4T\xac\xc9\xa4j\xb6\xc3\xb0\xab\xb7|\xb3\xf5': [
            ('\xa7I\xb4\xab\xbc\xfa\xc0y', None, 1001, 1, (122, 78), 0, None, 255, 'dhjl', 0, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 1003, 1, (205, 115), 0, None, 255, 'hdcsr', 0, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 1004, 1, (214, 51), 0, None, 255, 'hdcsr', 0, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 1005, 1, (68, 52), 0, None, 255, 'hdcsr', 0, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xb6\xc7\xb0e\xa4H', None, 1006, 1, (74, 115), 0, None, 255, 'hdcsr', 0, 0, None, None, None),
            ('\xac\xa1\xb0\xca\xb1\xc6\xa6\xe6\xba]', None, 1007, 1, (140, 96), 0, None, 255, 'phb', 0, 0, None, None, None),
            ('\xa5d\xb5P\xb3c\xb0\xe2', None, 1002, 1, (157, 78), 0, None, 255, 'kpfs', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9504: {
        '\xa8M\xbe\xd4\xc0s\xb2W': [
            ('\xa5\xa8\xc0s', None, 0, 1, (84, 66), 0, None, 255, 'jl', 0, 0, None, None, None),
            ('\xa5\xa8\xc0s', None, 0, 1, (92, 63), 0, None, 255, 'jl', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xafP\xb5K\xc0s\xa8\xcf', None, 2002, 1, (150, 35), 0, None, 255, 'lyls', 0, 0, None, None, None),
            ('\xa5\xc8\xa6B\xc0s\xa8\xcf', None, 2001, 1, (30, 100), 0, None, 255, 'xbls', 0, 0, None, None, None)] },
    9505: {
        '\xad^\xc6F\xb7\xb5': [
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (106, 6), 0, None, 255, 'jgzhg', 0, 0, None, None, None),
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (113, 78), 0, None, 255, 'jgzhg', 0, 0, None, None, None),
            ('\xafT\xaf\xab\xa4\xa7\xb6\xf0', None, 0, 1, (33, 19), 0, None, 255, 'lszt', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9506: {
        '\xad^\xc6F\xb7\xb5': [
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (9, 9), 0, None, 255, 'jgzhg', 0, 0, None, None, None),
            ('\xb6i\xa7\xf0\xab\xfc\xb4\xa7\xa9x', None, 0, 1, (13, 81), 0, None, 255, 'jgzhg', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xa8\xdf\xaf\xab\xa4\xa7\xb6\xf0', None, 0, 1, (99, 65), 0, None, 255, 'tszt', 0, 0, None, None, None)] },
    9507: {
        '\xad^\xc6F\xb7\xb5': [
            ('\xafT\xb1\xda\xa6u\xbd\xc3', None, 0, 1, (9, 9), 0, None, 255, 'lzsw', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xa8\xdf\xb1\xda\xa6u\xbd\xc3', None, 0, 1, (191, 8), 0, None, 255, 'tzsw', 0, 0, None, None, None)] },
    9508: {
        '\xad^\xc6F\xb7\xb5': [
            ('\xafT\xb1\xda\xa6u\xbd\xc3', None, 0, 1, (12, 112), 0, None, 255, 'lzsw', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None),
            ('\xa8\xdf\xb1\xda\xa6u\xbd\xc3', None, 0, 1, (168, 109), 0, None, 255, 'tzsw', 0, 0, None, None, None)] },
    9509: {
        '\xae\xfc\xb0\xd3\xb6\xc7\xa9_\xac\xa1\xb0\xca\xc6U': [
            ('\xaf\xe8\xae\xfc\xa9\xdb\xb6\xd2\xa8\xcf', None, 1001, 1, (343, 226), 0, None, 255, 'hhzms', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (441, 193), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9510: {
        '\xa8M\xbe\xd4\xc0s\xb2W': [
            ('\xb8t\xc6F\xc0s\xa8\xcf', None, 7002, 1, (87, 64), 0, None, 255, 'slls', 0, 0, None, None, None)] },
    9511: {
        '\xc0s\xb4\xb9\xb1K\xa6a': [
            ('\xc0s\xb4\xb9\xb8t\xa8\xcf', None, 7003, 1, (55, 25), 0, None, 255, 'ljss', 0, 0, None, None, None)] },
    9512: {
        '\xa4\xd1\xac\xc9\xb1\xc6\xa6\xec\xc1\xc9': [
            ('\xb0\xab\xbe\xd4\xaa\xf7\xa5P', None, 0, 1, (140, 79), 0, None, 255, 'dzjx', 0, 0, None, None, None)] },
    9513: {
        '\xb7\xc7\xb3\xc6\xc6U': [
            ('\xac\xa1\xb0\xca\xb1\xb5\xa4\xde\xa4H', None, 1001, 1, (139, 78), 0, None, 255, 'ljh', 0, 0, None, None, None)] },
    9514: {
        '\xa4\xd1\xbf\xef\xa5\xfe\xa9\xfa\xacP': [
            ('\xc3\xc4\xa9\xb1\xa6\xd1\xc1\xf3', None, 0, 1, (170, 88), 0, None, 255, 'y', 0, 0, None, None, None),
            ('\xa4\xb8\xb3q\xafu\xa7g', None, 0, 1, (161, 93), 0, None, 255, 'y', 0, 0, None, None, None)] },
    9515: {
        '\xa8M\xb3\xd3\xa4\xa7\xa6a': [
            ('\xbe\xd4\xb6\xa4\xba\xde\xb2z\xad\xfb', None, 1002, 1, (130, 80), 0, None, 255, '', 0, 0, None, None, None)] },
    9900: {
        '\xb0\xc6\xa5\xbb\xb7\xc7\xb3\xc6\xc6U': [
            ('\xaf\xab\xaaZ\xb4L', None, 0, 1, (140, 78), 0, None, 255, 'swz', 0, 0, None, None, None)] },
    9901: {
        '\xc5]\xb4\xb9\xadn\xb6\xeb': [
            ('\xa4\xd1\xb2M', None, 0, 1, (69, 70), 0, None, 255, 'tq', 0, 0, None, None, None),
            ('\xb1O\xa4\xe2', None, 0, 1, (22, 72), 0, None, 255, 'ts', 0, 0, None, None, None),
            ('\xb1O\xa4\xe2', None, 0, 1, (31, 103), 0, None, 255, 'ts', 0, 0, None, None, None),
            ('\xb1O\xa4\xe2', None, 0, 1, (32, 44), 0, None, 255, 'ts', 0, 0, None, None, None),
            ('\xb1O\xa4\xe2', None, 0, 1, (94, 108), 0, None, 255, 'ts', 0, 0, None, None, None),
            ('\xb1O\xa4\xe2', None, 0, 1, (120, 85), 0, None, 255, 'ts', 0, 0, None, None, None),
            ('\xb1O\xa4\xe2', None, 0, 1, (148, 93), 0, None, 255, 'ts', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (55, 90), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9902: {
        '\xb8t\xb2\xaa\xael\xa8\xa6': [
            ('\xa8\xaa\xa1P\xa6\xe5\xa4\xfa', None, 0, 1, (79, 44), 0, None, 255, 'cxy', 0, 0, None, None, None),
            ('\xa8\xaa\xa1P\xb0}\xa4M', None, 0, 1, (21, 57), 0, None, 255, 'czd', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (120, 70), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9903: {
        '\xa5|\xb6H\xa7x\xc0s\xb0}': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9904: {
        '\xa4K\xaf\xee\xa4\xdb\xbcv\xb0}': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9905: {
        '\xa4Q\xa4\xe8\xb5\xb4\xb1\xfe\xb0}': [
            ('.', None, 0, 1, None, 0, None, 255, '', 0, 0, None, None, None)] },
    9906: {
        '\xaeI\xb0\xa9\xa4\xa7\xa6a': [
            ('\xc5]\xbb\xee', None, 0, 1, (132, 68), 0, None, 255, 'mh', 0, 0, None, None, None),
            ('\xc5]\xbez', None, 0, 1, (141, 66), 0, None, 255, 'mp', 0, 0, None, None, None),
            ('\xc5]\xaf\xab', None, 0, 1, (119, 60), 0, None, 255, 'ms', 0, 0, None, None, None),
            ('\xc3\xc4\xa9\xb1', None, 1003, 2, (135, 100), 0, None, 255, 'yd', 0, 0, None, None, None)] },
    9907: {
        '\xc5]\xb1\xda\xc0\xe7\xa6a': [
            ('\xb9@\xa8\xb8', None, 1005, 1, (87, 20), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc5]\xaf\xab\xa4\xc0\xa8\xad', None, 1003, 1, (80, 38), 0, None, 255, '', 0, 0, None, None, None)] },
    9942: {
        '\xa4\xd1\xac\xc9\xc4v\xa7\xde\xb3\xf5': [
            ('\xc4v\xa7\xde\xb3\xf5\xb6\xc7\xb0e\xa4H', None, 0, 1, (7, 152), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc4v\xa7\xde\xb3\xf5\xb6\xc7\xb0e\xa4H', None, 0, 1, (9, 19), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc4v\xa7\xde\xb3\xf5\xb6\xc7\xb0e\xa4H', None, 0, 1, (257, 145), 0, None, 255, '', 0, 0, None, None, None),
            ('\xc4v\xa7\xde\xb3\xf5\xb6\xc7\xb0e\xa4H', None, 0, 1, (272, 17), 0, None, 255, '', 0, 0, None, None, None),
            ('\xa6\xd1\xa6\xbf\xb4\xf2', None, 4103, 1, (130, 100), 0, None, 255, '', 0, 0, None, None, None)] },
    9945: {
        '\xa4O\xb6q\xa4\xa7\xad\xec': [
            ('\xa7L\xb2\xc5', None, 0, 1, (171, 121), 0, None, 255, 'b', 0, 0, None, None, None),
            ('\xa4\xf5\xc3\xc4', None, 0, 1, (123, 77), 0, None, 255, 'h', 0, 0, None, None, None),
            ('\xb0\xf2\xa6a\xa4\xde\xb8\xf4\xa4H', None, 0, 1, (226, 9), 0, None, 255, 'j', 0, 0, None, None, None),
            ('\xaaZ\xbe\xb9', None, 0, 1, (50, 48), 0, None, 255, 'w', 0, 0, None, None, None)] },
    9950: {
        '\xa5\xa2\xb8\xa8\xaa\xba\xaf\xab\xb7\xb5': [
            ('\xac\xf5\xa4\xe8\xa7L\xaa\xf8', None, 1013, 2, (20, 168), 0, None, 255, 'hfjdbz', 0, 0, None, None, None),
            ('\xc2\xc5\xa4\xe8\xa7L\xaa\xf8', None, 1014, 2, (337, 9), 0, None, 255, 'lfjdbz', 0, 0, None, None, None),
            ('\xa5\xf8\xc3Z\xa6\xe6\xaa\xcc', None, 1015, 2, (361, 188), 0, None, 255, 'qexz', 0, 0, None, None, None)] } }
None['npcName'] = None(None, None, None, None, None, None, None, None, None, None, {
    30: {
        (44, 118): {
            'desc': '',
            'jumpPos': (44, 118),
            'name': '\xa5\xab\xb6\xb0\xa5X\xa4f',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (104, 30): {
            'desc': '',
            'jumpPos': (104, 30),
            'name': '\xa5\xab\xb6\xb0\xa5X\xa4f',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (204, 30): {
            'desc': '',
            'jumpPos': (204, 30),
            'name': '\xa5\xab\xb6\xb0\xa5X\xa4f',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1001: {
        (2, 2): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (2, 2),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2004,
            'npcName': '\xa8\xae\xa5\xed',
            'servergrade': 0 },
        (45, 90): {
            'desc': '',
            'jumpPos': (45, 90),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (125, 18): {
            'desc': '20\xaf\xc5',
            'jumpPos': (127, 15),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1002: {
        (5, 141): {
            'desc': '25\xaf\xc5',
            'jumpPos': (5, 141),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1003: {
        (147, 4): {
            'desc': '25\xaf\xc5',
            'jumpPos': (147, 4),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (151, 111): {
            'desc': '20\xaf\xc5',
            'jumpPos': (151, 111),
            'name': '\xb7s\xa4\xeb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1004: {
        (10, 117): {
            'desc': '',
            'jumpPos': (10, 115),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (154, 27): {
            'desc': '',
            'jumpPos': (154, 27),
            'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1005: {
        (16, 13): {
            'desc': '\xb7s\xa4\xe2\xa7\xf8',
            'jumpPos': (16, 13),
            'name': '\xb2M\xad\xb7\xa7\xf8',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (198, 113): {
            'desc': '',
            'jumpPos': (198, 113),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1006: {
        (44, 139): {
            'desc': '\xabn\xbb\xbb\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (44, 139),
            'name': '\xa5\xc3\xbfA\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (95, 5): {
            'desc': '\xabn\xbb\xbb\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (95, 5),
            'name': '\xa8\xa6\xabB\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1007: {
        (2, 2): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (2, 2),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2005,
            'npcName': '\xa8\xae\xa5\xed',
            'servergrade': 0 },
        (42, 95): {
            'desc': '',
            'jumpPos': (42, 95),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (122, 23): {
            'desc': '20\xaf\xc5',
            'jumpPos': (130, 26),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1008: {
        (35, 111): {
            'desc': '20\xaf\xc5',
            'jumpPos': (35, 111),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (144, 3): {
            'desc': '25\xaf\xc5',
            'jumpPos': (144, 3),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1009: {
        (189, 16): {
            'desc': '25\xaf\xc5',
            'jumpPos': (189, 16),
            'name': '\xba\xf1\xc6W\xaaL\xa6a',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1010: {
        (9, 24): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (9, 24),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (128, 8): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (128, 8),
            'name': '\xad\xbb\xb8\xad\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1011: {
        (61, 144): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (61, 144),
            'name': '\xa5j\xa4\xec\xaf\xab\xbcq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (180, 7): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (180, 7),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1012: {
        (6, 122): {
            'desc': '30\xaf\xc5',
            'jumpPos': (6, 122),
            'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (97, 79): {
            'desc': '45\xaf\xc5',
            'jumpPos': (97, 79),
            'name': '\xa5j\xa4\xec\xb2\xbd\xbe\xc2\xa4@\xbch',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (162, 145): {
            'desc': '60\xaf\xc5',
            'jumpPos': (158, 141),
            'name': '\xafe\xad\xb7\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1013: {
        (3, 8): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (3, 8),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2006,
            'npcName': '\xa8\xae\xa5\xed',
            'servergrade': 0 },
        (51, 95): {
            'desc': '',
            'jumpPos': (51, 95),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (120, 20): {
            'desc': '20\xaf\xc5',
            'jumpPos': (133, 15),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1014: {
        (9, 114): {
            'desc': '25\xaf\xc5',
            'jumpPos': (9, 114),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1015: {
        (12, 124): {
            'desc': '25\xaf\xc5',
            'jumpPos': (12, 124),
            'name': '\xaf\xee\xa6\xd0\xa5b\xaeq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1016: {
        (12, 111): {
            'desc': '\xb2M\xb4P\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (12, 111),
            'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (145, 10): {
            'desc': '\xb2M\xb4P\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (145, 10),
            'name': '\xa5\xad\xa6w\xb4\xe4',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1017: {
        (18, 140): {
            'desc': '\xb2M\xb4P\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (18, 140),
            'name': '\xa4\xd1\xbba\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (33, 12): {
            'desc': '\xb2M\xb4P\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (33, 12),
            'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1018: {
        (5, 127): {
            'desc': '30\xaf\xc5',
            'jumpPos': (5, 127),
            'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (6, 5): {
            'desc': '',
            'jumpPos': (6, 5),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (58, 125): {
            'desc': '25\xaf\xc5',
            'jumpPos': (58, 125),
            'name': '\xc6F\xa5\xdb\xb6\xf0\xa4@\xbch',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (135, 40): {
            'desc': '25\xaf\xc5',
            'jumpPos': (135, 18),
            'name': '\xc6F\xad\xb7\xb6\xf0\xa4@\xbch',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1019: {
        (10, 13): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (10, 13),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2007,
            'npcName': '\xb2\xee\xa4\xd2',
            'servergrade': 0 },
        (54, 92): {
            'desc': '',
            'jumpPos': (54, 92),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (120, 14): {
            'desc': '20\xaf\xc5',
            'jumpPos': (133, 14),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1020: {
        (6, 74): {
            'desc': '25\xaf\xc5',
            'jumpPos': (6, 74),
            'name': '\xacy\xa5\xfa\xaeq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (134, 114): {
            'desc': '20\xaf\xc5',
            'jumpPos': (134, 114),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1021: {
        (186, 32): {
            'desc': '25\xaf\xc5',
            'jumpPos': (186, 32),
            'name': '\xacy\xa5\xfa\xaeq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1022: {
        (13, 4): {
            'desc': '',
            'jumpPos': (13, 4),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (28, 108): {
            'desc': '\xb3q\xa9\xb9\xa6U\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (25, 102),
            'name': '\xb4\xe4\xa4f',
            'npcID': 2008,
            'npcName': '\xb2\xee\xa4\xd2',
            'servergrade': 0 } } }, {
    30: {
        (44, 118): {
            'desc': '',
            'jumpPos': (44, 118),
            'name': '\xa5\xab\xb6\xb0\xa5X\xa4f',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (104, 30): {
            'desc': '',
            'jumpPos': (104, 30),
            'name': '\xa5\xab\xb6\xb0\xa5X\xa4f',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (204, 30): {
            'desc': '',
            'jumpPos': (204, 30),
            'name': '\xa5\xab\xb6\xb0\xa5X\xa4f',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1001: {
        (2, 2): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (2, 2),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2004,
            'npcName': '\xa8\xae\xa5\xed',
            'servergrade': 0 },
        (45, 90): {
            'desc': '',
            'jumpPos': (45, 90),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (125, 18): {
            'desc': '20\xaf\xc5',
            'jumpPos': (127, 15),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1002: {
        (5, 141): {
            'desc': '25\xaf\xc5',
            'jumpPos': (5, 141),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1003: {
        (147, 4): {
            'desc': '25\xaf\xc5',
            'jumpPos': (147, 4),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (151, 111): {
            'desc': '20\xaf\xc5',
            'jumpPos': (151, 111),
            'name': '\xb7s\xa4\xeb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1004: {
        (10, 117): {
            'desc': '',
            'jumpPos': (10, 115),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (154, 27): {
            'desc': '',
            'jumpPos': (154, 27),
            'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1005: {
        (16, 13): {
            'desc': '\xb7s\xa4\xe2\xa7\xf8',
            'jumpPos': (16, 13),
            'name': '\xb2M\xad\xb7\xa7\xf8',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (198, 113): {
            'desc': '',
            'jumpPos': (198, 113),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1006: {
        (44, 139): {
            'desc': '\xabn\xbb\xbb\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (44, 139),
            'name': '\xa5\xc3\xbfA\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (95, 5): {
            'desc': '\xabn\xbb\xbb\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (95, 5),
            'name': '\xa8\xa6\xabB\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1007: {
        (2, 2): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (2, 2),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2005,
            'npcName': '\xa8\xae\xa5\xed',
            'servergrade': 0 },
        (42, 95): {
            'desc': '',
            'jumpPos': (42, 95),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (122, 23): {
            'desc': '20\xaf\xc5',
            'jumpPos': (130, 26),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1008: {
        (35, 111): {
            'desc': '20\xaf\xc5',
            'jumpPos': (35, 111),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (144, 3): {
            'desc': '25\xaf\xc5',
            'jumpPos': (144, 3),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1009: {
        (189, 16): {
            'desc': '25\xaf\xc5',
            'jumpPos': (189, 16),
            'name': '\xba\xf1\xc6W\xaaL\xa6a',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1010: {
        (9, 24): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (9, 24),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (128, 8): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (128, 8),
            'name': '\xad\xbb\xb8\xad\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1011: {
        (61, 144): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (61, 144),
            'name': '\xa5j\xa4\xec\xaf\xab\xbcq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (180, 7): {
            'desc': '\xa4\xd1\xb9\xe7\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (180, 7),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1012: {
        (6, 122): {
            'desc': '30\xaf\xc5',
            'jumpPos': (6, 122),
            'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (97, 79): {
            'desc': '45\xaf\xc5',
            'jumpPos': (97, 79),
            'name': '\xa5j\xa4\xec\xb2\xbd\xbe\xc2\xa4@\xbch',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (162, 145): {
            'desc': '60\xaf\xc5',
            'jumpPos': (158, 141),
            'name': '\xafe\xad\xb7\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1013: {
        (3, 8): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (3, 8),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2006,
            'npcName': '\xa8\xae\xa5\xed',
            'servergrade': 0 },
        (51, 95): {
            'desc': '',
            'jumpPos': (51, 95),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (120, 20): {
            'desc': '20\xaf\xc5',
            'jumpPos': (133, 15),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1014: {
        (9, 114): {
            'desc': '25\xaf\xc5',
            'jumpPos': (9, 114),
            'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1015: {
        (12, 124): {
            'desc': '25\xaf\xc5',
            'jumpPos': (12, 124),
            'name': '\xaf\xee\xa6\xd0\xa5b\xaeq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1016: {
        (12, 111): {
            'desc': '\xb2M\xb4P\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (12, 111),
            'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (145, 10): {
            'desc': '\xb2M\xb4P\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (145, 10),
            'name': '\xa5\xad\xa6w\xb4\xe4',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1017: {
        (18, 140): {
            'desc': '\xb2M\xb4P\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (18, 140),
            'name': '\xa4\xd1\xbba\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (33, 12): {
            'desc': '\xb2M\xb4P\xb0\xea\xab\xb0\xa5\xab',
            'jumpPos': (33, 12),
            'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1018: {
        (5, 127): {
            'desc': '30\xaf\xc5',
            'jumpPos': (5, 127),
            'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (6, 5): {
            'desc': '',
            'jumpPos': (6, 5),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (58, 125): {
            'desc': '25\xaf\xc5',
            'jumpPos': (58, 125),
            'name': '\xc6F\xa5\xdb\xb6\xf0\xa4@\xbch',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (135, 40): {
            'desc': '25\xaf\xc5',
            'jumpPos': (135, 18),
            'name': '\xc6F\xad\xb7\xb6\xf0\xa4@\xbch',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1019: {
        (10, 13): {
            'desc': '\xa5|\xb0\xea',
            'jumpPos': (10, 13),
            'name': '\xa9\xfa\xa4\xeb\xab\xb0',
            'npcID': 2007,
            'npcName': '\xb2\xee\xa4\xd2',
            'servergrade': 0 },
        (54, 92): {
            'desc': '',
            'jumpPos': (54, 92),
            'name': '\xaev\xb9D\xb7\xb5',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (120, 14): {
            'desc': '20\xaf\xc5',
            'jumpPos': (133, 14),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1020: {
        (6, 74): {
            'desc': '25\xaf\xc5',
            'jumpPos': (6, 74),
            'name': '\xacy\xa5\xfa\xaeq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (134, 114): {
            'desc': '20\xaf\xc5',
            'jumpPos': (134, 114),
            'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1021: {
        (186, 32): {
            'desc': '25\xaf\xc5',
            'jumpPos': (186, 32),
            'name': '\xacy\xa5\xfa\xaeq',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 } },
    1022: {
        (13, 4): {
            'desc': '',
            'jumpPos': (13, 4),
            'name': '\xaa\xda\xaf\xf3\xc2\xed',
            'npcID': None,
            'npcName': None,
            'servergrade': 0 },
        (28, 108): {
            'desc': '\xb3q\xa9\xb9\xa6U\xb0\xea\xad\xba\xb3\xa3',
            'jumpPos': (25, 102),
            'name': '\xb4\xe4\xa4f',
            'npcID': 2008,
            'npcName': '\xb2\xee\xa4\xd2',
            'servergrade': 0 } } }, { }, **{ } >> {
    'desc': '40\xaf\xc5',
    'jumpPos': (34, 117),
    'name': '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL',
    'npcID': None })
None['servergrade'] = 0
None[(34, 117)] = None
None[(69, 21)] = {
    'desc': '',
    'jumpPos': (67, 31),
    'name': '\xb7\xc9\xae\xfc\xacw',
    'npcID': 2013,
    'npcName': '\xb2\xee\xa4\xd2',
    'servergrade': 0 }
None[(156, 32)] = {
    'desc': '20\xaf\xc5',
    'jumpPos': (156, 32),
    'name': '\xa4\xd3\xae\xa7\xaaL\xa6a',
    'npcID': None,
    'npcName': None,
    'servergrade': 0 }
None[1023] = None
None[1024] = {
    (15, 115): {
        'desc': '\xa5[\xac\xa5\xb0\xea\xab\xb0\xa5\xab',
        'jumpPos': (15, 115),
        'name': '\xacP\xc1\xf7\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (188, 18): {
        'desc': '\xa5[\xac\xa5\xb0\xea\xab\xb0\xa5\xab',
        'jumpPos': (188, 18),
        'name': '\xaf[\xbc\xfe\xb4\xe4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1025] = {
    (175, 142): {
        'desc': '15\xaf\xc5',
        'jumpPos': (175, 142),
        'name': '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec',
        'npcID': 2001,
        'npcName': '\xa8\xae\xa5\xed',
        'servergrade': 0 },
    (183, 11): {
        'desc': '3\xaf\xc5',
        'jumpPos': (183, 11),
        'name': '\xaa\xf8\xad\xb7\xaeq',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1026] = {
    (6, 5): {
        'desc': '60\xaf\xc5',
        'jumpPos': (6, 5),
        'name': '\xafe\xad\xb7\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (8, 84): {
        'desc': '70\xaf\xc5',
        'jumpPos': (8, 84),
        'name': '\xb8H\xb9\xda\xc0\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1027] = {
    (110, 4): {
        'desc': '60\xaf\xc5',
        'jumpPos': (110, 4),
        'name': '\xafe\xad\xb7\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (117, 86): {
        'desc': '70\xaf\xc5',
        'jumpPos': (117, 81),
        'name': '\xb8H\xb9\xda\xc0\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1028] = {
    (5, 108): {
        'desc': '\xb7s\xa4\xe2\xa7\xf8',
        'jumpPos': (5, 108),
        'name': '\xb2M\xad\xb7\xa7\xf8',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (142, 95): {
        'desc': '5\xaf\xc5',
        'jumpPos': (142, 95),
        'name': '\xac\xc0\xb7\xe4\xb0g\xaec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1029] = {
    (5, 120): {
        'desc': '',
        'jumpPos': (8, 115),
        'name': '\xa9]\xb9\xf5\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (21, 4): {
        'desc': '40\xaf\xc5',
        'jumpPos': (21, 4),
        'name': '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (192, 115): {
        'desc': '',
        'jumpPos': (192, 115),
        'name': '\xbe\xa4\xa9\xfa\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1032] = {
    (2, 142): {
        'desc': '75\xaf\xc5',
        'jumpPos': (2, 142),
        'name': '\xaa\xf7\xba\xf1\xa8F\xacw',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (6, 5): {
        'desc': '',
        'jumpPos': (6, 5),
        'name': '\xa9]\xb9\xf5\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (194, 16): {
        'desc': '',
        'jumpPos': (194, 16),
        'name': '\xbe\xa4\xa9\xfa\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1033] = {
    (7, 130): {
        'desc': '80\xaf\xc5',
        'jumpPos': (7, 130),
        'name': '\xad\xd7\xc3\xb9\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (142, 81): {
        'desc': '95\xaf\xc5',
        'jumpPos': (142, 81),
        'name': '\xa8F\xbaz\xb0g\xaec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (230, 5): {
        'desc': '70\xaf\xc5',
        'jumpPos': (230, 5),
        'name': '\xb8H\xb9\xda\xc0\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1034] = {
    (10, 131): {
        'desc': '85\xaf\xc5',
        'jumpPos': (10, 131),
        'name': '\xb8\xa8\xb3\xb7\xa6B\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (275, 25): {
        'desc': '75\xaf\xc5',
        'jumpPos': (275, 25),
        'name': '\xaa\xf7\xba\xf1\xa8F\xacw',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1035] = {
    (230, 6): {
        'desc': '80\xaf\xc5',
        'jumpPos': (230, 6),
        'name': '\xad\xd7\xc3\xb9\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1036] = {
    (13, 83): {
        'desc': '3\xaf\xc5',
        'jumpPos': (13, 83),
        'name': '\xaa\xf8\xad\xb7\xaeq',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1039] = {
    (3, 42): {
        'desc': '30\xaf\xc5',
        'jumpPos': (3, 42),
        'name': '\xc6F\xa5\xdb\xb6\xf0\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (5, 4): {
        'desc': '20\xaf\xc5',
        'jumpPos': (5, 4),
        'name': '\xa4\xd3\xae\xa7\xaaL\xa6a',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1040] = {
    (2, 43): {
        'desc': '35\xaf\xc5',
        'jumpPos': (2, 43),
        'name': '\xc6F\xa5\xdb\xb6\xf0\xa4T\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (74, 14): {
        'desc': '25\xaf\xc5',
        'jumpPos': (74, 14),
        'name': '\xc6F\xa5\xdb\xb6\xf0\xa4@\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1041] = {
    (107, 85): {
        'desc': '30\xaf\xc5',
        'jumpPos': (107, 85),
        'name': '\xc6F\xa5\xdb\xb6\xf0\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1043] = {
    (46, 81): {
        'desc': '40\xaf\xc5',
        'jumpPos': (46, 81),
        'name': '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (113, 3): {
        'desc': '50\xaf\xc5',
        'jumpPos': (113, 3),
        'name': '\xa5j\xa4\xec\xb2\xbd\xbe\xc2\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1044] = {
    (6, 86): {
        'desc': '55\xaf\xc5',
        'jumpPos': (6, 86),
        'name': '\xa5j\xa4\xec\xb2\xbd\xbe\xc2\xa4T\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (29, 2): {
        'desc': '45\xaf\xc5',
        'jumpPos': (29, 2),
        'name': '\xa5j\xa4\xec\xb2\xbd\xbe\xc2\xa4@\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1045] = {
    (115, 13): {
        'desc': '50\xaf\xc5',
        'jumpPos': (115, 13),
        'name': '\xa5j\xa4\xec\xb2\xbd\xbe\xc2\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1051] = {
    (93, 50): {
        'desc': '100\xaf\xc5',
        'jumpPos': (93, 50),
        'name': '\xa8\xdf\xaf\xab\xb7\xb5\xbf\xf2\xa7}',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (108, 4): {
        'desc': '75\xaf\xc5',
        'jumpPos': (108, 4),
        'name': '\xaa\xf7\xba\xf1\xa8F\xacw',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1052] = {
    (5, 20): {
        'desc': '105\xaf\xc5',
        'jumpPos': (5, 20),
        'name': '\xa8\xdf\xa9Z\xa5d\xaa\xf9\xb3\xae\xb9\xd3',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (193, 11): {
        'desc': '95\xaf\xc5',
        'jumpPos': (193, 11),
        'name': '\xa8F\xbaz\xb0g\xaec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1053] = {
    (235, 153): {
        'desc': '100\xaf\xc5',
        'jumpPos': (235, 153),
        'name': '\xa8\xdf\xaf\xab\xb7\xb5\xbf\xf2\xa7}',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1054] = {
    (1, 20): {
        'desc': '15\xaf\xc5',
        'jumpPos': (5, 19),
        'name': '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (38, 71): {
        'desc': '',
        'jumpPos': (38, 71),
        'name': '\xc2\\\xc5u',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (82, 120): {
        'desc': '',
        'jumpPos': (82, 120),
        'name': '\xc2\\\xc5u',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (98, 56): {
        'desc': '',
        'jumpPos': (98, 56),
        'name': '\xc2\\\xc5u',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (205, 235): {
        'desc': '',
        'jumpPos': (203, 222),
        'name': '\xab_\xc0I\xaea\xa6\xe6\xb7|',
        'npcID': None,
        'npcName': None,
        'servergrade': 45 },
    (226, 20): {
        'desc': '',
        'jumpPos': (209, 29),
        'name': '\xa5|\xb0\xea\xad\xba\xb3\xa3',
        'npcID': 2003,
        'npcName': '\xb2\xee\xa4\xd2',
        'servergrade': 0 },
    (328, 98): {
        'desc': '',
        'jumpPos': (328, 98),
        'name': '\xbe\xdd\xa5x',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (341, 164): {
        'desc': '',
        'jumpPos': (341, 164),
        'name': '\xc0\xb0\xac\xa3',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (350, 240): {
        'desc': '20\xaf\xc5',
        'jumpPos': (346, 230),
        'name': '\xa4\xd3\xae\xa7\xaaL\xa6a',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1055] = {
    (7, 102): {
        'desc': '',
        'jumpPos': (7, 102),
        'name': '\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (12, 11): {
        'desc': '',
        'jumpPos': (12, 11),
        'name': '\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (191, 102): {
        'desc': '',
        'jumpPos': (191, 102),
        'name': '\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (192, 10): {
        'desc': '',
        'jumpPos': (192, 10),
        'name': '\xc0\xb0\xbe\xd4\xb1\xb5\xa4\xde\xa4H',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1060] = {
    (73, 52): {
        'desc': '',
        'jumpPos': (73, 52),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1073] = {
    (4, 7): {
        'desc': '30\xaf\xc5',
        'jumpPos': (4, 7),
        'name': '\xc6F\xad\xb7\xb6\xf0\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (106, 84): {
        'desc': '20\xaf\xc5',
        'jumpPos': (106, 84),
        'name': '\xa4\xd3\xae\xa7\xaaL\xa6a',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1074] = {
    (4, 80): {
        'desc': '35\xaf\xc5',
        'jumpPos': (4, 80),
        'name': '\xc6F\xad\xb7\xb6\xf0\xa4T\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (23, 3): {
        'desc': '25\xaf\xc5',
        'jumpPos': (23, 3),
        'name': '\xc6F\xad\xb7\xb6\xf0\xa4@\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1075] = {
    (114, 4): {
        'desc': '30\xaf\xc5',
        'jumpPos': (114, 4),
        'name': '\xc6F\xad\xb7\xb6\xf0\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1076] = {
    (4, 20): {
        'desc': '\xa4\xa4\xa5\xdf\xab\xb0\xa5\xab',
        'jumpPos': (4, 20),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1077] = {
    (4, 20): {
        'desc': '\xa4\xa4\xa5\xdf\xab\xb0\xa5\xab',
        'jumpPos': (4, 20),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1078] = {
    (4, 20): {
        'desc': '\xa4\xa4\xa5\xdf\xab\xb0\xa5\xab',
        'jumpPos': (4, 20),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1079] = {
    (4, 32): {
        'desc': '',
        'jumpPos': (4, 32),
        'name': '\xbbR\xb7|\xb7\xc7\xb3\xc6\xc6UA',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1080] = {
    (4, 32): {
        'desc': '',
        'jumpPos': (4, 32),
        'name': '\xbbR\xb7|\xb7\xc7\xb3\xc6\xc6U',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1081] = {
    (4, 32): {
        'desc': '\xa4\xa4\xa5\xdf\xab\xb0\xa5\xab',
        'jumpPos': (4, 32),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1091] = {
    (129, 77): {
        'desc': '',
        'jumpPos': (129, 77),
        'name': '\xac\xa5\xb6\xa7\xab\xb0\xaaF',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1092] = {
    (26, 102): {
        'desc': '',
        'jumpPos': (26, 102),
        'name': '\xaaF\xc0\xad\xc3\xf6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1094] = {
    (119, 41): {
        'desc': '',
        'jumpPos': (119, 41),
        'name': '\xc2\xed\xb0\xea\xa6x',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1095] = {
    (64, 81): {
        'desc': '',
        'jumpPos': (64, 81),
        'name': '\xc5\xe6\xaf\xb8',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1096] = {
    (48, 134): {
        'desc': '',
        'jumpPos': (48, 134),
        'name': '\xb6\xc0\xaae\xb4\xe7\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (91, 68): {
        'desc': '',
        'jumpPos': (91, 68),
        'name': '\xb7\xc6\xa6{',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1099] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1100] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1101] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1102] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1112] = {
    (84, 53): {
        'desc': '',
        'jumpPos': (84, 53),
        'name': '\xa4\xec\xbe\xf4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1126] = {
    (175, 142): {
        'desc': '15\xaf\xc5',
        'jumpPos': (175, 142),
        'name': '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (183, 11): {
        'desc': '3\xaf\xc5',
        'jumpPos': (183, 11),
        'name': '\xaa\xf8\xad\xb7\xaeq',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1154] = {
    (1, 20): {
        'desc': '15\xaf\xc5',
        'jumpPos': (5, 19),
        'name': '\xa4\xd1\xa4\xf4\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (226, 20): {
        'desc': '20\xaf\xc5',
        'jumpPos': (209, 29),
        'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
        'npcID': 2009,
        'npcName': '\xb2\xee\xa4\xd2',
        'servergrade': 0 },
    (350, 240): {
        'desc': '20\xaf\xc5',
        'jumpPos': (346, 230),
        'name': '\xa4\xd3\xae\xa7\xaaL\xa6a',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1157] = {
    (21, 5): {
        'desc': '115\xaf\xc5',
        'jumpPos': (21, 5),
        'name': '\xaa\xec\xb6\xb3\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1158] = {
    (5, 4): {
        'desc': '125\xaf\xc5',
        'jumpPos': (5, 4),
        'name': '\xaa\xec\xb6\xb3\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (147, 115): {
        'desc': '',
        'jumpPos': (147, 115),
        'name': '\xa4\xd1\xaa\xc5\xadn\xb6\xeb',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1159] = {
    (55, 15): {
        'desc': '135\xaf\xc5',
        'jumpPos': (55, 15),
        'name': '\xc5]\xb4\xb9\xadn\xb6\xeb',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (141, 115): {
        'desc': '115\xaf\xc5',
        'jumpPos': (141, 115),
        'name': '\xaa\xec\xb6\xb3\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1161] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1162] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1163] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1171] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1172] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1173] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1174] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1175] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1176] = {
    (26, 109): {
        'desc': '145\xaf\xc5',
        'jumpPos': (26, 109),
        'name': '\xb8t\xb2\xaa\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (120, 25): {
        'desc': '125\xaf\xc5',
        'jumpPos': (120, 25),
        'name': '\xaa\xec\xb6\xb3\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1177] = {
    (14, 108): {
        'desc': '150\xaf\xc5',
        'jumpPos': (14, 108),
        'name': '\xb1\xeb\xa4\xd1\xa5j\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (145, 2): {
        'desc': '135\xaf\xc5',
        'jumpPos': (145, 2),
        'name': '\xc5]\xb4\xb9\xadn\xb6\xeb',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1178] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1179] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1180] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1181] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (11, 111): {
        'desc': '25\xaf\xc5',
        'jumpPos': (11, 111),
        'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1182] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (12, 113): {
        'desc': '',
        'jumpPos': (12, 113),
        'name': '\xaa\xda\xaf\xf3\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (152, 29): {
        'desc': '',
        'jumpPos': (152, 29),
        'name': '\xb6\xb3\xb3\xb6\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1183] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (35, 111): {
        'desc': '20\xaf\xc5',
        'jumpPos': (35, 111),
        'name': '\xb8\xa8\xa4\xe9\xae\xfc\xc6W',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (144, 3): {
        'desc': '25\xaf\xc5',
        'jumpPos': (144, 3),
        'name': '\xb2M\xb7\xcb\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1184] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (13, 4): {
        'desc': '',
        'jumpPos': (13, 4),
        'name': '\xaa\xda\xaf\xf3\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (14, 104): {
        'desc': '\xa4\xa4\xa5\xdf\xab\xb0\xa5\xab',
        'jumpPos': (14, 104),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1185] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (16, 13): {
        'desc': '\xb7s\xa4\xe2\xa7\xf8',
        'jumpPos': (16, 13),
        'name': '\xb2M\xad\xb7\xa7\xf8',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (198, 113): {
        'desc': '',
        'jumpPos': (198, 113),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1186] = {
    (5, 127): {
        'desc': '30\xaf\xc5',
        'jumpPos': (5, 127),
        'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (6, 5): {
        'desc': '',
        'jumpPos': (6, 5),
        'name': '\xa9\xfa\xa4\xeb\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1190] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1191] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1192] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1194] = {
    (8, 4): {
        'desc': '160\xaf\xc5',
        'jumpPos': (8, 4),
        'name': '\xc0s\xb2W',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (155, 3): {
        'desc': '145\xaf\xc5',
        'jumpPos': (155, 3),
        'name': '\xb8t\xb2\xaa\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1196] = {
    (34, 117): {
        'desc': '40\xaf\xc5',
        'jumpPos': (34, 117),
        'name': '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (156, 32): {
        'desc': '20\xaf\xc5',
        'jumpPos': (156, 32),
        'name': '\xa4\xd3\xae\xa7\xaaL\xa6a',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1197] = {
    (6, 122): {
        'desc': '30\xaf\xc5',
        'jumpPos': (6, 122),
        'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (162, 145): {
        'desc': '60\xaf\xc5',
        'jumpPos': (162, 145),
        'name': '\xafe\xad\xb7\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1198] = {
    (10, 117): {
        'desc': '',
        'jumpPos': (10, 117),
        'name': '\xa9]\xb9\xf5\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (21, 4): {
        'desc': '40\xaf\xc5',
        'jumpPos': (21, 4),
        'name': '\xbf\xc3\xa4\xf5\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (192, 115): {
        'desc': '',
        'jumpPos': (192, 115),
        'name': '\xbe\xa4\xa9\xfa\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1200] = {
    (4, 140): {
        'desc': '75\xaf\xc5',
        'jumpPos': (4, 140),
        'name': '\xaa\xf7\xba\xf1\xa8F\xacw',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (6, 5): {
        'desc': '',
        'jumpPos': (6, 5),
        'name': '\xa9]\xb9\xf5\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (194, 16): {
        'desc': '',
        'jumpPos': (194, 16),
        'name': '\xbe\xa4\xa9\xfa\xc2\xed',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1201] = {
    (3, 136): {
        'desc': '80\xaf\xc5',
        'jumpPos': (3, 136),
        'name': '\xad\xd7\xc3\xb9\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (230, 5): {
        'desc': '70\xaf\xc5',
        'jumpPos': (230, 5),
        'name': '\xb8H\xb9\xda\xc0\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1202] = {
    (9, 133): {
        'desc': '85\xaf\xc5',
        'jumpPos': (9, 133),
        'name': '\xb8\xa8\xb3\xb7\xa6B\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (276, 25): {
        'desc': '75\xaf\xc5',
        'jumpPos': (276, 25),
        'name': '\xaa\xf7\xba\xf1\xa8F\xacw',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1203] = {
    (230, 6): {
        'desc': '80\xaf\xc5',
        'jumpPos': (230, 6),
        'name': '\xad\xd7\xc3\xb9\xb4\xcb\xaaL',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1204] = {
    (5, 4): {
        'desc': '125\xaf\xc5',
        'jumpPos': (5, 4),
        'name': '\xaa\xec\xb6\xb3\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (147, 115): {
        'desc': '',
        'jumpPos': (147, 115),
        'name': '\xa4\xd1\xaa\xc5\xadn\xb6\xeb',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1205] = {
    (55, 15): {
        'desc': '135\xaf\xc5',
        'jumpPos': (55, 15),
        'name': '\xc5]\xb4\xb9\xadn\xb6\xeb',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (141, 115): {
        'desc': '115\xaf\xc5',
        'jumpPos': (141, 115),
        'name': '\xaa\xec\xb6\xb3\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1206] = {
    (26, 109): {
        'desc': '145\xaf\xc5',
        'jumpPos': (26, 109),
        'name': '\xb8t\xb2\xaa\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (120, 25): {
        'desc': '125\xaf\xc5',
        'jumpPos': (120, 25),
        'name': '\xaa\xec\xb6\xb3\xa5\xad\xad\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1207] = {
    (14, 108): {
        'desc': '150\xaf\xc5',
        'jumpPos': (14, 108),
        'name': '\xb1\xeb\xa4\xd1\xa5j\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (145, 2): {
        'desc': '135\xaf\xc5',
        'jumpPos': (145, 2),
        'name': '\xc5]\xb4\xb9\xadn\xb6\xeb',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1208] = {
    (8, 4): {
        'desc': '160\xaf\xc5',
        'jumpPos': (8, 4),
        'name': '\xc0s\xb2W',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (155, 3): {
        'desc': '145\xaf\xc5',
        'jumpPos': (155, 3),
        'name': '\xb8t\xb2\xaa\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1209] = {
    (6, 5): {
        'desc': '60\xaf\xc5',
        'jumpPos': (6, 5),
        'name': '\xafe\xad\xb7\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (8, 84): {
        'desc': '70\xaf\xc5',
        'jumpPos': (8, 84),
        'name': '\xb8H\xb9\xda\xc0\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1210] = {
    (63, 39): {
        'desc': '',
        'jumpPos': (63, 39),
        'name': '\xae\xc9\xaa\xc5\xa8\xcf\xaa\xcc',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1211] = {
    (39, 66): {
        'desc': '',
        'jumpPos': (39, 66),
        'name': '\xa4d\xb7\xcb\xaf\xbe',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1213] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1214] = {
    (178, 128): {
        'desc': '',
        'jumpPos': (178, 128),
        'name': '\xba\xab\xaf[\xb5\xd8',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1215] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1217] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1218] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1219] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1220] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1221] = {
    (137, 63): {
        'desc': '',
        'jumpPos': (137, 63),
        'name': '\xa7C\xb6i\xab\xd7',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (137, 116): {
        'desc': '',
        'jumpPos': (137, 116),
        'name': '\xb0\xaa\xb6i\xab\xd7',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1222] = {
    (116, 83): {
        'desc': '70\xaf\xc5',
        'jumpPos': (116, 83),
        'name': '\xb8H\xb9\xda\xc0\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1223] = {
    (21, 5): {
        'desc': '115\xaf\xc5',
        'jumpPos': (21, 5),
        'name': '\xaa\xec\xb6\xb3\xael\xa8\xa6',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1238] = {
    (10, 107): {
        'desc': '',
        'jumpPos': (10, 107),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (139, 90): {
        'desc': '',
        'jumpPos': (139, 90),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1239] = {
    (10, 107): {
        'desc': '',
        'jumpPos': (10, 107),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (139, 90): {
        'desc': '',
        'jumpPos': (139, 90),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1240] = {
    (10, 107): {
        'desc': '',
        'jumpPos': (10, 107),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (139, 90): {
        'desc': '',
        'jumpPos': (139, 90),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1241] = {
    (10, 107): {
        'desc': '',
        'jumpPos': (10, 107),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (139, 90): {
        'desc': '',
        'jumpPos': (139, 90),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1242] = {
    (10, 107): {
        'desc': '',
        'jumpPos': (10, 107),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (139, 90): {
        'desc': '',
        'jumpPos': (139, 90),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1301] = {
    (23, 52): {
        'desc': '',
        'jumpPos': (23, 52),
        'name': '\xab_\xc0I\xaea\xa6\xe6\xb7|\xa4G\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1303] = {
    (15, 35): {
        'desc': '',
        'jumpPos': (15, 35),
        'name': '\xab_\xc0I\xaea\xa6\xe6\xb7|\xa4@\xbch',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1304] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1305] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1307] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1308] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1313] = {
    (144, 110): {
        'desc': '150\xaf\xc5',
        'jumpPos': (144, 110),
        'name': '\xb1\xeb\xa4\xd1\xa5j\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1314] = {
    (144, 110): {
        'desc': '150\xaf\xc5',
        'jumpPos': (144, 110),
        'name': '\xb1\xeb\xa4\xd1\xa5j\xab\xb0',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1315] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': '  ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1316] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': '  ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1317] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1318] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1319] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1320] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1321] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1322] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1323] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': '  ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1324] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': '  ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[1327] = {
    (201, 6): {
        'desc': '30\xaf\xc5',
        'jumpPos': (192, 13),
        'name': '\xa4\xdb\xb9\xd2\xae\xfc\xa9\xa4',
        'npcID': 2014,
        'npcName': '\xb2\xee\xa4\xd2',
        'servergrade': 0 } }
None[2001] = {
    (5, 108): {
        'desc': '',
        'jumpPos': (5, 108),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (6, 27): {
        'desc': '',
        'jumpPos': (6, 27),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (6, 98): {
        'desc': '',
        'jumpPos': (6, 98),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (7, 61): {
        'desc': '',
        'jumpPos': (7, 61),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (11, 7): {
        'desc': '',
        'jumpPos': (11, 7),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (29, 117): {
        'desc': '',
        'jumpPos': (29, 117),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (81, 111): {
        'desc': '',
        'jumpPos': (81, 111),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (115, 12): {
        'desc': '',
        'jumpPos': (115, 12),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (148, 57): {
        'desc': '',
        'jumpPos': (148, 57),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (149, 84): {
        'desc': '',
        'jumpPos': (149, 84),
        'name': '\xc0\xb0\xac\xa3\xa4p\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (154, 23): {
        'desc': '',
        'jumpPos': (154, 23),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (154, 100): {
        'desc': '',
        'jumpPos': (154, 100),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[2002] = {
    (5, 63): {
        'desc': '',
        'jumpPos': (5, 63),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (46, 80): {
        'desc': '',
        'jumpPos': (46, 80),
        'name': '\xab\xfc\xa5\xdc\xb5P',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (114, 37): {
        'desc': '',
        'jumpPos': (114, 37),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[2201] = {
    (40, 34): {
        'desc': '',
        'jumpPos': (40, 34),
        'name': '\xa5X\xa4f',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[2999] = {
    (5, 52): {
        'desc': '',
        'jumpPos': (5, 52),
        'name': '\xa4\xd1\xc5]\xb7\xb5',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (15, 82): {
        'desc': '',
        'jumpPos': (15, 82),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[3012] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[4048] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9167] = {
    (140, 78): {
        'desc': '',
        'jumpPos': (140, 78),
        'name': '\xbe\xdd\xa5x\xb0\xcf',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9185] = {
    (93, 17): {
        'desc': '',
        'jumpPos': (93, 17),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9337] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9338] = {
    (140, 75): {
        'desc': '',
        'jumpPos': (140, 75),
        'name': '\xa8\xa4\xa6\xe2\xbf\xef\xbe\xdc\xb0\xcf\xb0\xec',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9342] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9343] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9412] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9452] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9453] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9901] = {
    (22, 72): {
        'desc': '',
        'jumpPos': (22, 72),
        'name': '\xc5]\xadx\xa4p\xb6\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (31, 103): {
        'desc': '',
        'jumpPos': (31, 103),
        'name': '\xc5]\xadx\xa4p\xb6\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (32, 44): {
        'desc': '',
        'jumpPos': (32, 44),
        'name': '\xc5]\xadx\xa4p\xb6\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (69, 70): {
        'desc': '',
        'jumpPos': (69, 70),
        'name': '\xa4\xd1\xb2M',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (94, 108): {
        'desc': '',
        'jumpPos': (94, 108),
        'name': '\xc5]\xadx\xa4p\xb6\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (120, 85): {
        'desc': '',
        'jumpPos': (120, 85),
        'name': '\xc5]\xadx\xa4p\xb6\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (148, 93): {
        'desc': '',
        'jumpPos': (148, 93),
        'name': '\xc5]\xadx\xa4p\xb6\xa4',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9902] = {
    (21, 57): {
        'desc': '',
        'jumpPos': (21, 57),
        'name': '\xbe\xd4\xb3\xf5\xbd\xee\xbd\xf1\xaa\xcc',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (79, 44): {
        'desc': '',
        'jumpPos': (79, 44),
        'name': '\xa9H\xad\xfd\xa4\xa7\xb3\xb1\xbcv',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9903] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9904] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9905] = {
    (1, 1): {
        'desc': '',
        'jumpPos': (1, 1),
        'name': ' ',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9906] = {
    (119, 60): {
        'desc': '',
        'jumpPos': (119, 60),
        'name': '\xc5]\xaf\xab',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (132, 68): {
        'desc': '',
        'jumpPos': (132, 68),
        'name': '\xc5]\xa4\xb2',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (141, 66): {
        'desc': '',
        'jumpPos': (141, 66),
        'name': '\xc5]\xa4\xb2',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
None[9907] = {
    (80, 38): {
        'desc': '',
        'jumpPos': (80, 38),
        'name': '\xc5]\xaf\xab\xa4\xc0\xa8\xad',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 },
    (87, 20): {
        'desc': '',
        'jumpPos': (87, 20),
        'name': '\xb9@\xa8\xb8',
        'npcID': None,
        'npcName': None,
        'servergrade': 0 } }
DATA_WENZI = None
