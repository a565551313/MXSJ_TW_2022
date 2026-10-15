# pycdc 交叉复核产物 · script.fls entry 375
# co_filename(原始)='script/data/rainbowdata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_375.pyc (Python 2.5)


def GetAllNormalPoints(mapID):
    tempLst = []
    for rainbowID, pointLst in NORMALBLK.get(mapID, { }).items():
        tempLst.extend(pointLst)
    
    return tempLst


def GetAllRainbowPoints(mapID):
    tempLst = []
    for rainbowID, pointLst in RAINBOWBLK.get(mapID, { })():
        tempLst.extend(pointLst)
    
    return tempLst


def GetAllFlyRainbowPoints(mapID):
    tempLst = []
    for rainbowID, pointLst in FLYRAINBOWBLK.get(mapID, { }).items():
        tempLst.extend(pointLst)
    
    return tempLst


def GetNormalPoints(mapID, rainbowID):
    return NORMALBLK.get(mapID, { }).get(rainbowID, { })


def GetRainbowPoints(mapID, rainbowID):
    return RAINBOWBLK.get(mapID, { }).get(rainbowID, { })


def GetAllRainbowAni(mapID):
    tempLst = []
    for rainbowID, aniInfo in ANIDATA.get(mapID, { }).items():
        tempLst.extend(aniInfo)
    
    return tempLst


def GetRainbowAni(mapID, rainbowID):
    return ANIDATA.get(mapID, { }).get(rainbowID, [])

NORMALBLK = { }
RAINBOWBLK = { }
FLYRAINBOWBLK = { }
ANIDATA = {
    1054: {
        0: [
            (262, 670, 450),
            (262, 770, 490),
            (262, 1030, 450),
            (262, 1150, 610),
            (262, 1370, 710),
            (264, 710, 470),
            (264, 810, 490),
            (264, 1030, 400),
            (264, 1090, 590),
            (264, 1250, 650),
            (265, 790, 550)] } }
