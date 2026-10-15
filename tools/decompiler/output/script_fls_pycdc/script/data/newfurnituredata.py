# pycdc 交叉复核产物 · script.fls entry 244
# co_filename(原始)='script/data/newfurnituredata.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_244.pyc (Python 2.5)

FURNITURE_YARD = 1
FURNITURE_ROOM = 2
FURNITURE_COMMON = 3
FURNITURE_LAYER_LAND = 0
FURNITURE_LAYER_NORMAL = 1
FURNITURE_LAYER_EFF = 2
FUR_SHOWTYPE_DIZHUAN = 2
FUR_SHOWTYPE_WEILAN = 3
FUR_SHOWTYPE_ZHIWU = 4
FUR_SHOWTYPE_SHUIJING = 5
FUR_SHOWTYPE_NORMAL = 1
FUR_SHOWTYPE_WALL = 6
FUR_SHOWTYPE_DIMAO = 7
SIT_QIUQIAN = 1
SIT_QIPIAN = 2
SIT_HOTSPRING = 3
E_HOTSPRING_ID = 29306
E_BAIHUDT_ID = 29361
FUR_TYPE_BED = 0
FUR_TYPE_DESK = 1
FUR_TYPE_SEAT = 2
FUR_TYPE_CHAIR = 3
FUR_TYPE_CURTAIN = 4
FUR_TYPE_CARPET = 5
FUR_TYPE_CABINET = 6
FUR_TYPE_TAI_DECOR = 7
FUR_TYPE_SCREEN = 8
FUR_TYPE_PIC = 9
FUR_TYPE_PLANT = 10
FUR_TYPE_VASE = 11
FUR_TYPE_WATER = 20
FUR_TYPE_HUAPU = 31
FUR_TYPE_BRIDGE = 33
FUR_TYPE_BRICK = 36
TYPE2NAME = {
    0: '\xa7\xc9',
    1: '\xae\xe0',
    2: '\xb9\xb9',
    3: '\xb4\xc8',
    4: '\xb5\xa1\xa9\xa9',
    5: '\xa6a\xb4\xe0',
    6: '\xcf@\xa4l',
    7: '\xa5x\xb9\xa2',
    8: '\xab\xcc\xad\xb7',
    9: '\xb1\xbe\xb5e',
    10: '\xb4\xd3\xaa\xab',
    11: '\xaa\xe1\xb2~',
    20: '\xa4\xf4\xa4\xa4\xb9\xa2\xaa\xab',
    21: '\xbcv\xbe\xc0',
    22: '\xae\xe0',
    23: '\xac\xd6\xb4\xba',
    24: '\xb9\xb9',
    25: '\xb4\xba\xc6[\xb4\xd3\xaa\xab',
    26: '\xc2\xf8\xb9\xa2',
    27: '\xb8\xf4',
    28: '\xabF',
    29: '\xb0|\xc0\xf0',
    30: '\xaa\xf9',
    31: '\xaa\xe1\xaeE',
    32: '\xb3\xf2\xc4\xe6',
    33: '\xbe\xf4',
    35: '\xa4p\xba\xdb',
    36: '\xa4\xf4\xa4\xa4\xb9\xa2\xaa\xab' }
DIDRANGE = {
    (29000, 29024): '\xa7\xc9',
    (29025, 29049): '\xae\xe0',
    (29050, 29074): '\xb9\xb9',
    (29075, 29099): '\xb4\xc8',
    (29100, 29124): '\xb5\xa1\xa9\xa9',
    (29125, 29149): '\xa6a\xb4\xe0',
    (29150, 29174): '\xcf@\xa4l',
    (29175, 29199): '\xa5x\xb9\xa2',
    (29200, 29224): '\xab\xcc\xad\xb7',
    (29225, 29249): '\xb1\xbe\xb5e',
    (29500, 29524): '\xa4\xf4\xa4\xa4\xb9\xa2\xaa\xab',
    (29775, 29799): '\xaa\xe1\xaeE',
    (29875, 29899): '\xa4p\xba\xdb',
    (29900, 29924): '\xa4\xf4\xa4\xa4\xb9\xa2\xaa\xab' }

def GetData(furn_id):
    
    try:
        return DATA[furn_id]
    except KeyError:
        dData = {
            'ani': None,
            'base_cost': 160,
            'beauty': 4,
            'beauty_limit': None,
            'cost': 1,
            'desc': '\xa4\xa3\xa9\xfa\xb3\xc3\xa8\xe3',
            'direct': None,
            'grade': None,
            'layer': None,
            'lianxuplace': None,
            'lv': 1,
            'name': '\xa5\xbc\xaa\xbe<%d>' % furn_id,
            'pagename': None,
            'pre': None,
            'special': None,
            'subtype': None,
            'type': 4,
            'invalid': True,
            'zoff': None }
        return dData



def IsFurniture(iShape):
    '''\xacO\xa7_\xac\xb0\xb3\xc3\xa8\xe3'''
    if iShape not in DATA:
        return False
    
    return DATA[iShape]['subtype'] in TYPE2NAME


def GetFurnitureType(shape):
    ftype = (shape - 29000) / 25
    return TYPE2NAME.get(ftype, '')


def IsAniFurniure(shape):
    dData = GetData(shape)
    if dData.get('ani'):
        return True
    else:
        return False


def IsStableFur(iFurID):
    dData = GetData(iFurID)
    sStablePath = dData.get('stablepath', '')
    if sStablePath:
        return True
    else:
        return False


def GetFurniturePath(shape, direction = 0):
    sDefault = 'furniture/%.5d%s.igs' % (shape, chr(ord('a') + direction))
    sPath = sDefault
    if shape in (29800, 29801, 29802):
        sPath = 'furniture/%.5d%s_new.igs' % (shape, chr(ord('a') + direction))
    
    return sPath


def GetFurStablePath(iFurID, iDirect):
    dData = GetData(iFurID)
    sStablePath = dData.get('stablepath', '')
    if sStablePath:
        tPath = sStablePath.split('/')
        sPackage = tPath[0]
        sPath = sStablePath[len(sPackage) + 1:]
        sEnd = chr(ord('a') + iDirect)
        sPath = '%s%s.igs' % (sPath, sEnd)
        return (sPackage, sPath)
    else:
        sPath = GetFurniturePath(iFurID, iDirect)
        return ('mapobject', sPath)


def GetFurnish(lv):
    l = []
    for k, v in DATA.items():
        if v['lv'] <= lv:
            if not IsSpecialFurnish(k):
                l.append(k)
            
        IsSpecialFurnish(k)
    
    return l


def IsSpecialFurnish(furn_id):
    SpecialFurnish = (25602, 25932, 25933, 25798)
    if furn_id in SpecialFurnish:
        return True
    else:
        return False


def GetAllFurnish(lv):
    l = []
    specialFurn = []
    for k, v in DATA.items():
        if v['lv'] <= lv:
            if IsSpecialFurnish(k):
                specialFurn.append(k)
            else:
                l.append(k)
        IsSpecialFurnish(k)
    
    l.sort(key = (lambda x: GetData(x)['lv']))
    specialFurn.sort(key = (lambda x: GetData(x)['lv']))
    l.extend(specialFurn)
    return l


def GetAllID():
    return ORDER


def GetLayerTypeAndWeightByShapeID(nShapeID):
    '''
\t:param nShapeID:
\t:return: layerBazeZ, weightZ
\t'''
    nLayerType = FURNITURE_LAYER_NORMAL
    nLayerWeight = 0
    dData = DATA.get(nShapeID)
    if dData and dData.get('layer'):
        sLayer = dData['layer']
        tLayer = sLayer.split(',')
        if tLayer:
            nLayerType = int(tLayer[0])
            if len(tLayer) > 1:
                nLayerWeight = int(tLayer[1])
            
        
    
    return (nLayerType, nLayerWeight)


def GetLayerZByLayerType(nLayerType):
    if nLayerType not in LAYER:
        LOG('not defined layertype', nLayerType)
        nLayerType = FURNITURE_LAYER_NORMAL
    
    dLayerInfo = LAYER[nLayerType]
    nLayerZ = dLayerInfo['pre']
    return nLayerZ


def GetFurShowType2ShapeList():
    dFurShowType2ShapeList = { }
    for nShapeID, dItem in DATA.iteritems():
        nShowType = dItem.get('pagename', FUR_SHOWTYPE_NORMAL)
        if nShowType not in dFurShowType2ShapeList:
            dFurShowType2ShapeList[nShowType] = []
        
        lShow = dFurShowType2ShapeList[nShowType]
        lShow.append(nShapeID)
    
    return dFurShowType2ShapeList


def GetFurZOffY(iShapeID):
    dData = GetData(iShapeID)
    iRate = dData.get('zoff', None)
    if iRate:
        iRate = 100 / iRate
    else:
        return 0
    return iRate


def GetSiteTable(nShapeID):
    return SITE.get(nShapeID, { })


def GetSiteList(nShapeID):
    dData = GetSiteTable(nShapeID)
    if not dData:
        return []
    
    lSit = []
    for sPos in ('a', 'b', 'c', 'd', 'e'):
        sKey = 'pos%s' % sPos
        if sKey in dData and dData.get(sKey, None):
            lSit.append(sPos)
            continue
    
    return lSit


def IsEnableSitOtherPlace(nShapeID):
    if nShapeID in (29306,):
        return True
    else:
        return False


def SitApha2Index(sAlpha):
    dSit2Index = {
        'a': 1,
        'b': 2,
        'c': 3,
        'd': 4,
        'e': 5 }
    return dSit2Index.get(sAlpha, 1)


def SitIndex2Apha(index):
    dSit2Index = {
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd' }
    return dSit2Index.get(index, 'a')


def GetAnimalZoomByHouseID(nHouseID):
    dHouse = ANIMAL_BRITH.get(nHouseID, { })
    return dHouse


def GetHorseChangePos(iHorse):
    return SPE_HORSE_DATA.get(iHorse, (0, 0))

ANIMAL_BRITH = {
    29302: {
        'center': (13, 9, 4),
        'name': None } }
SITE = {
    2: {
        'directa': 1,
        'directb': 7,
        'directc': None,
        'directd': None,
        'name': '2\xaf\xc5\xa4\xd1\xb5M\xb7\xc5\xacu',
        'playname': None,
        'posa': (17, 13),
        'posb': (22, 12),
        'posc': None,
        'posd': None,
        'sitstartpos': (460, 130),
        'zooma': (17, 13, 3),
        'zoomb': (22, 12, 3),
        'zoomc': None,
        'zoomd': None },
    3: {
        'directa': 1,
        'directb': 7,
        'directc': None,
        'directd': None,
        'name': '3\xaf\xc5\xa4\xd1\xb5M\xb7\xc5\xacu',
        'playname': None,
        'posa': (20, 255),
        'posb': (25, 16),
        'posc': None,
        'posd': None,
        'sitstartpos': (540, 260),
        'zooma': (20, 255, 3),
        'zoomb': (25, 16, 3),
        'zoomc': None,
        'zoomd': None },
    4: {
        'directa': 1,
        'directb': 7,
        'directc': None,
        'directd': None,
        'name': '4\xaf\xc5\xa4\xd1\xb5M\xb7\xc5\xacu',
        'playname': None,
        'posa': (20, 255),
        'posb': (25, 16),
        'posc': None,
        'posd': None,
        'sitstartpos': (540, 260),
        'zooma': (20, 255, 3),
        'zoomb': (25, 16, 3),
        'zoomc': None,
        'zoomd': None },
    29305: {
        'directa': 20,
        'directb': 7,
        'directc': None,
        'directd': None,
        'name': '\xacP\xa8\xb0\xb4\xd1\xbdL',
        'playname': 2,
        'posa': (-3, 2),
        'posb': (3.5, 5),
        'posc': None,
        'posd': None,
        'sitstartpos': None,
        'zooma': (-3, 2, 2),
        'zoomb': (2, 6, 2),
        'zoomc': None,
        'zoomd': None },
    29306: {
        'directa': 1,
        'directb': 2,
        'directc': 2,
        'directd': 2,
        'name': '\xbd\xac\xaa\xe1\xb7\xc5\xacu',
        'playname': 3,
        'posa': (4, 8),
        'posb': (6, 6),
        'posc': (3, 5),
        'posd': (1, 6),
        'sitstartpos': None,
        'zooma': (4, 8, 5),
        'zoomb': (6, 6, 5),
        'zoomc': (3, 5, 4),
        'zoomd': (1, 6, 5) },
    29314: {
        'directa': 1,
        'directb': None,
        'directc': None,
        'directd': None,
        'name': '\xc2\xfe\xc6H',
        'playname': 1,
        'posa': (0, 0),
        'posb': None,
        'posc': None,
        'posd': None,
        'sitstartpos': None,
        'zooma': (1, 5, 2),
        'zoomb': None,
        'zoomc': None,
        'zoomd': None } }
LAYER = {
    0: {
        'name': '\xa6a\xbfj\xb3\xc3\xa8\xe3',
        'pre': 0 },
    1: {
        'name': '\xb4\xb6\xb3q\xb3\xc3\xa8\xe3',
        'pre': 1 },
    2: {
        'name': '\xafS\xae\xc4\xb3\xc3\xa8\xe3',
        'pre': 2 },
    3: {
        'name': '\xa6a\xb4\xe0\xb3\xc3\xa8\xe3',
        'pre': 0.5 } }
ORDER = [
    29341,
    29700,
    29701,
    29702,
    29703,
    29704,
    29200,
    29201,
    29202,
    29203,
    29204,
    29205,
    29206,
    29207,
    29768,
    29725,
    29726,
    29727,
    29225,
    29226,
    29227,
    29228,
    29229,
    29230,
    29231,
    29232,
    29233,
    29234,
    29750,
    29751,
    29752,
    29753,
    29754,
    29755,
    29756,
    29757,
    29758,
    29759,
    29760,
    29761,
    29250,
    29251,
    29252,
    29253,
    29254,
    29255,
    29256,
    29257,
    29258,
    29259,
    29260,
    29775,
    29776,
    29777,
    29800,
    29801,
    29802,
    29343,
    29629,
    29301,
    29303,
    29304,
    29345,
    29306,
    29307,
    29308,
    29310,
    29311,
    29312,
    29825,
    29826,
    29827,
    29828,
    29829,
    29830,
    29831,
    29832,
    29833,
    29322,
    29323,
    29324,
    29325,
    29326,
    29327,
    29328,
    29329,
    29330,
    29331,
    29332,
    29333,
    29334,
    29346,
    29336,
    29337,
    29850,
    29851,
    29852,
    29853,
    29854,
    29855,
    29856,
    29857,
    29858,
    29347,
    29348,
    29349,
    29350,
    29351,
    29352,
    29353,
    29354,
    29355,
    29356,
    29357,
    29358,
    29359,
    29360,
    29361,
    29362,
    29363,
    29364,
    29365,
    29366,
    29367,
    29368,
    29369,
    29370,
    29371,
    29372,
    25798,
    29305,
    25932,
    29314,
    29315,
    29316,
    29317,
    29318,
    29319,
    29998,
    29999,
    29320,
    29500,
    29501,
    29502,
    29000,
    29001,
    29002,
    29003,
    29004,
    29005,
    29006,
    29007,
    29025,
    29026,
    29027,
    29028,
    29029,
    29032,
    29033,
    29034,
    29050,
    29051,
    29052,
    29053,
    29054,
    29055,
    29763,
    29335,
    29762,
    29075,
    29076,
    29077,
    29078,
    29079,
    29764,
    29765,
    29600,
    29601,
    29602,
    29603,
    29766,
    29338,
    29340,
    29767,
    29100,
    29101,
    29102,
    29103,
    29104,
    29105,
    29106,
    29107,
    29342,
    29769,
    29625,
    29626,
    29627,
    29628,
    29770,
    29344,
    29771,
    29339,
    29125,
    29126,
    29127,
    29128,
    29129,
    29132,
    29133,
    29134,
    25933,
    29650,
    29651,
    29652,
    29150,
    29151,
    29152,
    29153,
    29154,
    29155,
    29156,
    29157,
    29675,
    29676,
    29677,
    29175,
    29176,
    29177,
    29178,
    29179,
    29180,
    29181,
    29182]
# WARNING: Decompyle incomplete
