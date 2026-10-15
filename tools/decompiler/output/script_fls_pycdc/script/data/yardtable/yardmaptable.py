# pycdc 交叉复核产物 · script.fls entry 595
# co_filename(原始)='script/data/yardtable/yardmaptable.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_595.pyc (Python 2.5)

'''
\xd7\xa2\xd2\xe2\xa3\xba
\t\xcd\xac\xb2\xbd\xd6\xd0\xd0\xc4\xb5\xe3\xa3\xba \xc8\xe7\xb9\xfb\xd0\xe8\xd2\xaa\xb2\xe2\xca\xd4\xb4\xab\xcb\xcd\xb5\xe3\xce\xbb\xd6\xc3\xb5\xc4\xca\xb1\xba\xf2\xd0\xe8\xd2\xaa\xc8\xb7\xc8\xcf\xc1\xbd\xb6\xcb\xb5\xc4\xd6\xd0\xd0\xc4\xb5\xe3\xd7\xf8\xb1\xea\xca\xc7\xb7\xf1\xb6\xd4\xd3\xa6\xa3\xac\xb7\xf1\xd4\xf2\xbb\xe1\xb3\xf6\xcf\xd6\xbc\xc6\xcb\xe3\xba\xf3\xc9\xe8\xd6\xc3\xb5\xc4\xb4\xab\xcb\xcd\xb5\xe3\xce\xbb\xd6\xc3\xba\xcd\xb2\xdf\xbb\xae\xb2\xbb\xd2\xbb\xd6\xc2

'''

def GetMapData(nMapID):
    dData = DATA.get(nMapID)
    if not dData:
        LOG('nMapID:', nMapID)
    
    return dData


def GetAllMapID():
    return sorted(DATA.keys())


def GetMapZoom(nMapID):
    sModel = 'yardmapzoom%s' % nMapID
    
    try:
        m = __import__(sModel)
        dZoom = m.DATA
        return dZoom
    except:
        return { }



def GetMapOthersZoom(nMapID):
    sModel = 'yardmapzoom%s' % nMapID
    
    try:
        m = __import__(sModel)
        dZoom = m.DATA_OTHER_ZOOM
        return dZoom
    except:
        return { }



def GetExtraMapZoom(nMapID, iZoomID):
    sModel = 'yardmapzoom%s' % nMapID
    
    try:
        m = __import__(sModel)
        dZoom = m.DATA_OTHER_ZOOM
        return dZoom.get(iZoomID)
    except:
        return { }



def IsYardMap(nMapID):
    return nMapID in DATA


def GetMapIDByGrade(nGrade):
    for nMapID, dMap in DATA.iteritems():
        if dMap['grade'] == nGrade:
            return nMapID
            continue
    
    if nGrade > 5:
        LOG('illegalgrade:', nGrade)
        return 2504
    else:
        return 2501

DATA = {
    2501: {
        'beauty': 200,
        'center': (900, 22530),
        'editscale': 12,
        'grade': 1,
        'mapsize': (1800, 1200),
        'maxGrid': (25, 20),
        'scale': 20 },
    2502: {
        'beauty': 1200,
        'center': (1350, 900),
        'editscale': 8,
        'grade': 2,
        'mapsize': (2700, 1800),
        'maxGrid': (30, 35),
        'scale': 18 },
    2503: {
        'beauty': 2200,
        'center': (1800, 1200),
        'editscale': 6,
        'grade': 3,
        'mapsize': (3600, 2400),
        'maxGrid': (38, 35),
        'scale': 16 },
    2504: {
        'beauty': None,
        'center': (2250, 1500),
        'editscale': 4.8,
        'grade': 4,
        'mapsize': (4500, 3000),
        'maxGrid': (50, 50),
        'scale': 14 } }
