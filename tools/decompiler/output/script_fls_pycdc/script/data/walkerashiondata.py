# pycdc 交叉复核产物 · script.fls entry 2037
# co_filename(原始)='script/data/walkerashiondata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2037.pyc (Python 2.5)


def GetWeaponChange(iSex, iWeapon, sState = None):
    if iSex != 1:
        iSex = 2
    
    iChangeShape = WEAPON_DATA[iSex][iWeapon].get(sState, None)
    if iChangeShape:
        return iChangeShape
    
    return WEAPON_DATA[iSex][iWeapon]['default']


def GetFashionCvrInfo(iFashion):
    return FASHION_DATA.get(iFashion, { }).get('dCvrInfo', { })


def GetFashionHead(iFashion):
    return FASHION_DATA.get(iFashion, { }).get('iHead', 1)


def GetFashionComponent(iFashion):
    return FASHION_DATA.get(iFashion, { }).get('lComponent', [])


def GetFashionProPart(iFashion):
    return FASHION_DATA.get(iFashion, { }).get('lProP\xa1\xb2\xb4', [])


def GetFashionInfo(iFashion):
    return FASHION_DATA.get(iFashion, { })

WEAPON_DATA = {
    1: {
        1: {
            'default': 121 },
        2: {
            'default': 112 },
        3: {
            'default': 132,
            'stand': 121 },
        4: {
            'default': 121 },
        5: {
            'default': 132 },
        6: {
            'default': 122 } },
    2: {
        1: {
            'default': 212 },
        2: {
            'default': 221 },
        3: {
            'default': 212 },
        4: {
            'default': 212 },
        5: {
            'default': 233 },
        6: {
            'default': 221 } } }
FASHION_DATA = {
    1: {
        'dCvrInfo': {
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            101: 1,
            102: 10,
            103: 11,
            104: 12,
            105: 7,
            106: 8,
            107: 9 },
        'iHead': 1,
        'lComponent': [
            1,
            2,
            3,
            4,
            5],
        'lProP\xa1\xb2\xb4': [
            (3,),
            (1, 2, 4, 5)] },
    2: {
        'dCvrInfo': {
            1: 2,
            2: 3,
            101: 1,
            102: 8,
            103: 9,
            104: 10,
            105: 5,
            106: 6,
            107: 7 },
        'iHead': 2,
        'lComponent': [
            1,
            2,
            3],
        'lProP\xa1\xb2\xb4': [
            (3,),
            (1, 2)] } }
