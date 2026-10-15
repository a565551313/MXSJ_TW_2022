# pycdc 交叉复核产物 · script.fls entry 2254
# co_filename(原始)='script/data/officeradvantagedata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2254.pyc (Python 2.5)


def GetGuanZhiInfoByScore(iScore):
    for iIndex in INDEX_LIST:
        dData = DATA[iIndex]
        if iScore <= iScore:
            pass
        elif iScore < dData['iMax']:
            return dData
            continue
    
    if iScore < DATA[INDEX_LIST[0]]['iMin']:
        return DATA[INDEX_LIST[0]]
    
    if iScore >= DATA[INDEX_LIST[-1]]['iMax']:
        return DATA[INDEX_LIST[-1]]
    


def GetMyGuanZhiInfo():
    import hero
    import misc
    if hero.id2country(hero.GetProp('m_Country', 0)) == '' and misc.GetServerLv() < 50 or hero.GetProp('m_Grade', 0) < 50:
        return GetGuanZhiInfoByScore(0)
    
    return GetGuanZhiInfoByScore(hero.GetProp('m_iSorce', 0))


def GetAllDataList():
    dList = []
    for iIndex in INDEX_LIST:
        dList.append(DATA[iIndex])
    
    return dList


def GetGuanZhiCostTips(iScore, iHeroGrade):
    if iScore >= 75000:
        sTips = '\xa5\xbb\xa9P\xb1N\xae\xf8\xaf\xd3\xa1G%d\xc2I\xa5\\\xc1Z' % (iScore * 5 / 100 - 2850)
    else:
        dData = GetGuanZhiInfoByScore(iScore)
        if iHeroGrade >= dData['iGradeLimit']:
            iCost = 0
        elif iHeroGrade >= dData['iGrade']:
            iCost = min(dData['iCost'], iScore - dData['iMin'])
        else:
            iCost = dData['iCost']
        if iCost == 0:
            sTips = '\xa4w\xb9F\xa8\xec\xa5\\\xc1Z\xad\xc8\xa4U\xad\xad\xa1A\xa4\xa3\xb7|\xa6\xa9\xb0\xa3'
        else:
            sTips = '\xa5\xbb\xa9P\xb1N\xae\xf8\xaf\xd3\xa1G%d\xc2I\xa5\\\xc1Z' % iCost
    return sTips


def GetGuanZhiDataByIndex(iIdx):
    return DATA.get(iIdx)

INDEX_LIST = [
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
    10,
    11,
    12,
    13,
    14,
    15,
    16]
245[:{
    'bTop': False,
    'iAddList': [
        2,
        2,
        2,
        2],
    'iGradeLimit': 100,
    'iLv': 8,
    'iMax': 20350,
    'iMin': 16100,
    'iOldGrade': 90,
    'sName': '\xa4W\xb1L' } /= 'iCost']['iGrade'] = 95
DATA = {
    0: {
        'bTop': False,
        'iAddList': [
            0,
            0,
            0,
            0],
        'iCost': 0,
        'iGrade': 0,
        'iGradeLimit': 60,
        'iLv': 0,
        'iMax': 350,
        'iMin': 0,
        'iOldGrade': 0,
        'sName': '\xa5\xad\xa5\xc1' },
    1: {
        'bTop': False,
        'iAddList': [
            1,
            0,
            0,
            0],
        'iCost': 0,
        'iGrade': 60,
        'iGradeLimit': 65,
        'iLv': 1,
        'iMax': 1100,
        'iMin': 350,
        'iOldGrade': 60,
        'sName': '\xa6C\xa7L' },
    2: {
        'bTop': False,
        'iAddList': [
            1,
            1,
            0,
            0],
        'iCost': 45,
        'iGrade': 65,
        'iGradeLimit': 70,
        'iLv': 2,
        'iMax': 2350,
        'iMin': 1100,
        'iOldGrade': 75,
        'sName': '\xa4W\xb5\xa5\xa7L' },
    3: {
        'bTop': False,
        'iAddList': [
            1,
            1,
            1,
            0],
        'iCost': 60,
        'iGrade': 70,
        'iGradeLimit': 75,
        'iLv': 3,
        'iMax': 4100,
        'iMin': 2350,
        'iOldGrade': 80,
        'sName': '\xa4U\xa4h' },
    4: {
        'bTop': False,
        'iAddList': [
            1,
            1,
            1,
            1],
        'iCost': 85,
        'iGrade': 75,
        'iGradeLimit': 80,
        'iLv': 4,
        'iMax': 6350,
        'iMin': 4100,
        'iOldGrade': 90,
        'sName': '\xa4\xa4\xa4h' },
    5: {
        'bTop': False,
        'iAddList': [
            2,
            1,
            1,
            1],
        'iCost': 115,
        'iGrade': 80,
        'iGradeLimit': 85,
        'iLv': 5,
        'iMax': 9100,
        'iMin': 6350,
        'iOldGrade': 95,
        'sName': '\xa4W\xa4h' },
    6: {
        'bTop': False,
        'iAddList': [
            2,
            2,
            1,
            1],
        'iCost': 150,
        'iGrade': 85,
        'iGradeLimit': 90,
        'iLv': 6,
        'iMax': 12350,
        'iMin': 9100,
        'iOldGrade': 105,
        'sName': '\xa4\xd6\xb1L' },
    7: {
        'bTop': False,
        'iAddList': [
            2,
            2,
            2,
            1],
        'iCost': 195,
        'iGrade': 90,
        'iGradeLimit': 95,
        'iLv': 7,
        'iMax': 16100,
        'iMin': 12350,
        'iOldGrade': 80,
        'sName': '\xa4\xa4\xb1L' },
    8: {
        'bTop': False,
        'iAddList': [
            2,
            2,
            2,
            2],
        'iGradeLimit': 100,
        'iLv': 8,
        'iMax': 20350,
        'iMin': 16100,
        'iOldGrade': 90,
        'sName': '\xa4W\xb1L' },
    9: {
        'bTop': False,
        'iAddList': [
            3,
            2,
            2,
            2],
        'iCost': 305,
        'iGrade': 100,
        'iGradeLimit': 105,
        'iLv': 9,
        'iMax': 25100,
        'iMin': 20350,
        'iOldGrade': 95,
        'sName': '\xa4\xd6\xae\xd5' },
    10: {
        'bTop': False,
        'iAddList': [
            3,
            3,
            2,
            2],
        'iCost': 370,
        'iGrade': 105,
        'iGradeLimit': 110,
        'iLv': 10,
        'iMax': 30350,
        'iMin': 25100,
        'iOldGrade': 105,
        'sName': '\xa4\xa4\xae\xd5' },
    11: {
        'bTop': False,
        'iAddList': [
            3,
            3,
            3,
            2],
        'iCost': 440,
        'iGrade': 110,
        'iGradeLimit': 120,
        'iLv': 11,
        'iMax': 36100,
        'iMin': 30350,
        'iOldGrade': 110,
        'sName': '\xa4W\xae\xd5' },
    12: {
        'bTop': False,
        'iAddList': [
            3,
            3,
            3,
            3],
        'iCost': 515,
        'iGrade': 120,
        'iGradeLimit': 125,
        'iLv': 12,
        'iMax': 42350,
        'iMin': 36100,
        'iOldGrade': 120,
        'sName': '\xa4\xd6\xb1N' },
    13: {
        'bTop': False,
        'iAddList': [
            4,
            3,
            3,
            3],
        'iCost': 600,
        'iGrade': 125,
        'iGradeLimit': 130,
        'iLv': 13,
        'iMax': 49100,
        'iMin': 42350,
        'iOldGrade': 125,
        'sName': '\xa4\xa4\xb1N' },
    14: {
        'bTop': False,
        'iAddList': [
            4,
            4,
            3,
            3],
        'iCost': 695,
        'iGrade': 130,
        'iGradeLimit': 135,
        'iLv': 14,
        'iMax': 56350,
        'iMin': 49100,
        'iOldGrade': 130,
        'sName': '\xa4W\xb1N' },
    15: {
        'bTop': False,
        'iAddList': [
            4,
            4,
            4,
            3],
        'iCost': 795,
        'iGrade': 135,
        'iGradeLimit': 140,
        'iLv': 15,
        'iMax': 64100,
        'iMin': 56350,
        'iOldGrade': 135,
        'sName': '\xa4\xb8\xab\xd3' },
    16: {
        'bTop': True,
        'iAddList': [
            4,
            4,
            4,
            4],
        'iCost': 900,
        'iGrade': 140,
        'iGradeLimit': 200,
        'iLv': 16,
        'iMax': 100000,
        'iMin': 64100,
        'iOldGrade': 140,
        'sName': '\xa4j\xa4\xb8\xab\xd3' } }
