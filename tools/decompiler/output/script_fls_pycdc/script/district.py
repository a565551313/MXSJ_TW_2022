# pycdc 交叉复核产物 · script.fls entry 2652
# co_filename(原始)='script/district.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2652.pyc (Python 2.5)

import interface
import cursor
import map
import net
g_LandState = { }
g_AttentionPosList = []
g_Tips = None

def ModuleReset():
    global g_LandState, g_AttentionPosList, g_Tips
    g_LandState = { }
    g_AttentionPosList = []
    g_Tips = None

HOUSE_POS = ((1, 1593, 1339), (1, 1775, 1429), (1, 1954, 1519), (1, 2129, 1604), (1, 2385, 1740), (1, 2549, 1822), (1, 2808, 1953), (1, 2986, 2042), (1, 3165, 2130), (2, 1281, 1440), (2, 1109, 1526), (2, 932, 1615), (2, 744, 1706), (2, 440, 1857), (2, 254, 1949), (2, 67, 2043), (1, 1480, 1651), (1, 1666, 1743), (1, 1851, 1834), (1, 2026, 1921), (-2, 2414, 2176), (2, 1199, 1808), (2, 1005, 1905), (2, 714, 2068), (-1, 432, 2287), (1, 1438, 1996), (1, 1619, 2085), (1, 1787, 2167), (1, 1969, 2259), (2, 1178, 2177), (2, 987, 2272), (1, 2052, 1141), (1, 2224, 1228), (1, 2401, 1317), (1, 2700, 1462), (1, 2876, 1550), (1, 3053, 1641), (2, 2310, 938), (2, 2495, 849), (2, 2689, 753), (-2, 3093, 718), (1, 2804, 1047), (-2, 3080, 1251), (1, 1055, 1099), (2, 734, 1270), (2, 559, 1358), (2, 381, 1446), (2, 53, 1607), (1, 868, 1007), (1, 697, 922), (1, 412, 774), (1, 228, 680), (-1, 120, 1152), (1, 1330, 777), (1, 1138, 685), (1, 964, 601), (1, 663, 452), (1, 487, 366), (-2, 216, 297), (2, 1804, 743), (2, 1984, 655), (2, 2171, 564), (2, 2353, 476), (2, 2662, 321), (2, 2854, 227), (2, 3051, 131), (2, 1532, 566), (2, 1730, 464), (2, 2012, 318), (2, 2193, 230), (2, 2380, 136), (2, 2563, 47), (1, 1199, 365), (1, 1016, 278), (-2, 722, 199), (-1, 1752, 218), (1, 1340, 56))
FACTORY_HOUSE_POS = ((1, 1589, 944), (1, 2007, 1148), (1, 2425, 1355), (2, 986, 540), (2, 1404, 333), (1, 2197, 255), (1, 2280, 691), (2, 659, 1174), (2, 205, 1400), (2, 1267, 1495), (2, 833, 1709), (2, 112, 2025), (1, 1759, 1749), (1, 2193, 1963), (1, 1347, 2075), (1, 1766, 2283), (2, 663, 2266), (1, 762, 266), (2, 107, 355), (2, 84, 848))
FACTORY_FLY_POS = ((67, 69), (89, 59), (110, 48), (59, 90), (80, 101), (97, 104), (102, 81), (42, 58), (19, 46), (73, 42), (51, 31), (15, 16), (76, 29), (98, 18), (56, 12), (75, 2), (43, 4), (26, 103), (15, 99), (14, 74))
DOORPLATE_POS = {
    1001: ((2, 5794, 1475), (2, 6025, 1364), (2, 6249, 1252), (2, 6462, 1135), (2, 6227, 2133), (2, 6299, 2093), (2, 6467, 2012), (2, 6757, 1873), (2, 6777, 2470), (2, 6993, 2363), (1, 7465, 1827), (1, 7651, 1909), (1, 4960, 2715), (1, 5482, 2982), (2, 4628, 3264), (2, 5239, 3494), (2, 5846, 3702), (1, 4754, 3899), (1, 4925, 4005), (1, 5135, 4120), (2, 4247, 3754), (2, 4028, 3840), (2, 3745, 3982), (2, 3649, 4035), (1, 2909, 4090), (2, 3378, 3605), (2, 3629, 3483), (2, 3795, 3404), (2, 1865, 3471), (1, 2147, 3288)),
    1007: ((1, 671, 2689), (1, 1516, 2802), (2, 1804, 2499), (2, 1015, 2374), (1, 1159, 2309), (1, 1884, 2126), (2, 2640, 2133), (2, 2881, 2016), (2, 2176, 1828), (1, 2474, 1735), (1, 531, 1512), (1, 1187, 1685), (2, 1559, 1405), (2, 819, 1154), (1, 917, 1171), (1, 1261, 580), (1, 2055, 904), (2, 2317, 685), (2, 1799, 335), (1, 1930, 320), (1, 2594, 3768), (2, 3514, 3845), (2, 3926, 3649), (2, 3197, 3462), (1, 3363, 3456), (1, 4226, 3271), (1, 4667, 3486), (2, 5316, 3365), (2, 4659, 2977), (1, 4832, 3043)),
    1013: ((2, 6976, 2842), (2, 7661, 2540), (1, 7743, 2059), (1, 7486, 1913), (2, 6988, 2176), (2, 6616, 2399), (2, 6493, 2420), (2, 6455, 1651), (2, 7463, 1091), (1, 6766, 832), (1, 6514, 709), (1, 6273, 595), (2, 5963, 862), (2, 5713, 1038), (2, 4304, 2692), (2, 4020, 2831), (2, 3686, 2986), (2, 3406, 3179), (2, 3463, 3815), (1, 2812, 4122), (2, 2653, 3559), (2, 2426, 3669), (2, 1991, 3872), (2, 1615, 3235), (2, 1328, 3368), (2, 1163, 3451), (2, 804, 3662), (2, 672, 3674), (2, 524, 2918), (2, 246, 3044)),
    1019: ((2, 5342, 4033), (2, 5540, 3923), (2, 5811, 3783), (2, 4353, 3924), (2, 4646, 3737), (2, 4908, 3611), (2, 5156, 3483), (2, 4099, 3398), (2, 4288, 3306), (2, 4543, 3178), (2, 2546, 3601), (2, 2706, 3526), (2, 3105, 3285), (2, 3345, 3163), (1, 6324, 3624), (1, 6108, 3505), (1, 5843, 3365), (1, 5355, 3137), (1, 5093, 3012), (1, 681, 2964), (1, 244, 2755), (1, 1446, 2762), (1, 1160, 2616), (2, 1861, 2304), (2, 2063, 2185), (2, 2309, 2061), (2, 910, 2189), (2, 1196, 2003), (2, 1466, 1863), (2, 1691, 1753)) }
PLANTPLATE_POS = {
    1001: ((5630, 1530), (5950, 1390), (6070, 1330), (6430, 1170), (6190, 2150), (6410, 2050), (6690, 1890), (6890, 1790), (6630, 2510), (7150, 2310), (7290, 1770), (7910, 2050), (5090, 2750), (5630, 3050), (4710, 3250), (5290, 3470), (5930, 3670), (4690, 3910), (4790, 3950), (5090, 4110), (4430, 3690), (4210, 3790), (3930, 3910), (3490, 4130), (2710, 4010), (3330, 3610), (3750, 3410), (3910, 3390), (1710, 3570), (1950, 3230)),
    1007: ((510, 2610), (1350, 2750), (1770, 2550), (970, 2430), (1230, 2330), (1730, 2050), (2490, 2210), (3050, 1930), (2330, 1770), (2570, 1750), (370, 1470), (1030, 1630), (1470, 1470), (730, 1210), (970, 1190), (1410, 690), (1890, 850), (2490, 610), (1730, 390), (1990, 370), (2750, 3850), (3370, 3930), (3730, 3730), (3070, 3530), (3410, 3470), (4050, 3190), (4510, 3390), (5170, 3450), (4610, 3010), (4990, 3130)),
    1013: ((7150, 2770), (7490, 2630), (7530, 1950), (7310, 1850), (6870, 2210), (6850, 2310), (6310, 2530), (6690, 1570), (7670, 990), (6950, 930), (6690, 810), (6470, 690), (5770, 950), (5530, 1130), (4450, 2630), (4150, 2750), (3890, 2910), (3630, 3050), (3250, 3910), (2610, 4030), (2510, 3630), (2210, 3770), (1790, 3970), (1770, 3170), (1550, 3270), (1070, 3490), (950, 3570), (470, 3770), (690, 2830), (470, 2950)),
    1019: ((5150, 4130), (5430, 3990), (5670, 3850), (4150, 4030), (4490, 3870), (4790, 3670), (4990, 3570), (3930, 3470), (4170, 3370), (4390, 3250), (2390, 3690), (2810, 3470), (3030, 3330), (3210, 3250), (6550, 3750), (6230, 3530), (6050, 3470), (5550, 3230), (5250, 3090), (530, 2890), (430, 2850), (1350, 2710), (1050, 2550), (1770, 2350), (1970, 2250), (2190, 2130), (670, 2290), (1010, 2110), (1350, 1910), (1570, 1830)) }
IMAGES_SEEK = {
    0: (0, 0),
    1: (0, 0),
    2: (13, -20),
    3: (0, 6),
    4: (2, -23),
    5: (4, -8),
    1000: (0, 0),
    1001: (0, 0) }
ID2SHAPE = {
    2002: 2000,
    2003: 2001,
    2004: 2000,
    2005: 2001,
    2006: 2000,
    2007: 2001,
    2008: 2000,
    2009: 2001,
    2010: 2002,
    2011: 2003,
    2012: 2002,
    2013: 2003,
    2014: 2002,
    2015: 2003,
    2016: 2002,
    2017: 2003,
    2018: 2004,
    2019: 2005,
    2020: 2004,
    2021: 2005,
    2022: 2004,
    2023: 2005,
    2024: 2004,
    2025: 2005,
    2026: 2006,
    2027: 2007,
    2028: 2008,
    2029: 2009,
    2030: 2008,
    2031: 2009,
    2032: 2008,
    2033: 2009 }

def SetAttentionList(posList):
    global g_AttentionPosList
    g_AttentionPosList = posList


def GetAttentionList():
    return g_AttentionPosList


class CPlantGan(interface.CBase, interface.CMapAddonObject):
    
    def __init__(self, x, y, pos, direction, num, state):
        fname = 'house\\doorplant%d' % direction
        interface.CMapAddonObject.__init__(self, map.g_Map, 1, fname, 'mapobject')
        self.Place(x, y)
        self.m_dir = direction
        self.m_x = x
        self.m_y = y
        self.m_Pos = pos
        self.m_State = state
        self.m_PlantNum = num
        self.m_Name = None
        self.MessageProcess()
        self.DrawState(state)

    
    def DrawState(self, state):
        import garth
        ischegnshu = state & 1
        isjiaozao = state & 2
        (w, h) = self.GetSize()
        if ischegnshu:
            self.m_stateTip = garth.CFlowerFloat(self, '#43', 10, h)
        elif isjiaozao:
            self.m_stateTip = garth.CFlowerFloat(self, '#10', 10, h)
        

    
    def Enter(self):
        import wrapinterface
        self.SetLight(16)

    
    def Leave(self):
        self.SetLight(8)

    
    def LeftUp(self):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_DISTRICT)
        netobj.PacketAddI(3, 1)
        netobj.PacketAddI(self.m_Pos, 1)
        netobj.PacketSend()

    
    def SetName(self, name):
        global g_Tips
        import wrapinterface
        self.m_Name = name
        if hasattr(self, 'm_Enter'):
            width = len(self.m_Name) * 7 + 7
            g_Tips = wrapinterface.CTextTips(None, width, self.m_Name, interface.FontLT14_3)
        



class CDoorplate(interface.CBase, interface.CMapAddonObject):
    
    def __init__(self, x, y, pos, idx, name = None):
        if map.g_Map.m_ID == 2002:
            fname = 'house\\doorplate2001_%d' % idx
        else:
            fname = 'house\\doorplate%.4d_%d' % (map.g_Map.m_ID, idx)
        interface.CMapAddonObject.__init__(self, map.g_Map, 1, fname, 'mapobject')
        self.Place(x, y)
        self.m_Name = name
        self.m_Pos = pos
        self.MessageProcess()

    
    def Enter(self):
        global g_Tips
        import wrapinterface
        self.SetLight(16)
        self.m_Enter = True
        if self.m_Name:
            width = len(self.m_Name) * 7 + 7
            g_Tips = wrapinterface.CTextTips(None, width, self.m_Name, interface.FontLT14_3)
        else:
            C2SGetDistrictTip(self.m_Pos)
        if cursor.g_CurrCursor is None or cursor.g_CurrCursor == cursor.NORMAL_CURSOR:
            cursor.Load(cursor.CHAT_CURSOR)
        

    
    def Leave(self):
        global g_Tips
        self.SetLight(8)
        g_Tips = None
        self.m_Enter = False
        if cursor.g_CurrCursor == cursor.CHAT_CURSOR:
            cursor.Load(cursor.NORMAL_CURSOR)
        

    
    def LeftUp(self):
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_DISTRICT)
        netobj.PacketAddI(1, 1)
        netobj.PacketAddI(self.m_Pos, 1)
        netobj.PacketSend()

    
    def SetName(self, name):
        global g_Tips
        import wrapinterface
        self.m_Name = name
        if hasattr(self, 'm_Enter') and self.m_Enter:
            width = len(self.m_Name) * 7 + 7
            g_Tips = wrapinterface.CTextTips(None, width, self.m_Name, interface.FontLT14_3)
        



def GetGroupHouseShapeByID(iIdx):
    import guildbuildnewdata
    iShape = None
    iType = iIdx / 100
    iRank = iIdx % 100
    dResource = guildbuildnewdata.GetResourceByTypeRank(iType, iRank)
    if dResource:
        iShape = dResource['iSource']
    
    if iShape is None:
        iShape = 30171
    
    return iShape


class CGroupBuilding(interface.CMapAddonObject):
    
    def __init__(self, parent, x, y, iIdx):
        import yardextraeff
        
        try:
            iShape = GetGroupHouseShapeByID(iIdx)
            interface.CMapAddonObject.__init__(self, parent, 1, 'house\\%.4d' % iShape, 'mapobject')
            self.Place(x, y)
            self.m_oExtraEff = yardextraeff.CExtraEff(self, 'house\\%.4d.ani' % iShape, bUseSprite = True, bUseOffSet = True)
        except:
            LOG_EXC('CGroupBuilding>>>>>>>Failed', iIdx)

        self.m_HouseIdx = iIdx



class CHouse(interface.CMapAddonObject):
    
    def __init__(self, x, y, idx):
        
        try:
            shape = ID2SHAPE.get(idx)
            if shape is None:
                shape = idx
            
            interface.CMapAddonObject.__init__(self, map.g_Map, 1, 'house\\%.4d' % shape, 'mapobject')
        except:
            interface.CMapAddonObject.__init__(self, map.g_Map, 1, 'house\\0000', 'mapobject')

        self.m_HouseIdx = idx
        self.Place(x, y)



def Create():
    dpos = DOORPLATE_POS.get(map.g_Map.m_ID)
    if dpos:
        map.g_Map.m_Houses = { }
        map.g_Map.m_Doorplates = { }
        for i in xrange(len(dpos)):
            (idx, x, y) = dpos[i]
            map.g_Map.m_Doorplates[i + 1] = CDoorplate(x, y, i + 1, idx)
        
    


def CreatePlantCard(houses, doorplates, pos, num, state):
    if map.g_Map.m_ID == 2001:
        
        try:
            (direction, x, y) = HOUSE_POS[pos - 1]
        except IndexError:
            return None

        dir1 = direction
        if direction < 0:
            direction = -direction
            if direction == 1:
                x1 = x
                y1 = y + 100
            else:
                x1 = x - 200
                y1 = y
        elif direction == 1:
            x1 = x
            y1 = y + 130
        else:
            x1 = x + 140
            y1 = y + 75
        doorplates[pos] = CPlantGan(x1, y1, pos, direction, num, state)
    elif map.g_Map.m_ID in (1001, 1007, 1013, 1019):
        doorpos = DOORPLATE_POS.get(map.g_Map.m_ID)
        plantpos = PLANTPLATE_POS.get(map.g_Map.m_ID)
        if doorpos and plantpos:
            
            try:
                (x, y) = plantpos[pos - 1]
                (idir, _, _) = doorpos[pos - 1]
                doorplates[pos] = CPlantGan(x, y, pos, idir, num, state)

        
    


def CreateHouseAndDoorplate(houses, doorplates, pos, type, name):
    if map.g_Map.m_ID == 2001:
        if type >= 50:
            type -= 50
        
        
        try:
            (direction, x, y) = HOUSE_POS[pos - 1]
        except IndexError:
            return None

        if type == 0:
            if pos in houses:
                del houses[pos]
            
        else:
            type -= 1
            if direction == 1 or direction == 2:
                idx = (direction - 1) + type * 2
            else:
                idx = (1000 - direction - 1) + type * 2
            hx = x
            hy = y
            
            try:
                hx += IMAGES_SEEK[idx][0]
                hy += IMAGES_SEEK[idx][1]
            except KeyError:
                return None

            houses[pos] = CHouse(hx, hy, idx)
        if direction < 0:
            direction = -direction
            if direction == 1:
                x += 200
                y += 15
            else:
                x -= 2
                y += 113
        elif direction == 1:
            x -= 140
            y += 65
        else:
            x += 15
            y += 144
    elif map.g_Map.m_ID == 2002:
        if pos - 1 >= len(FACTORY_HOUSE_POS):
            return None
        
        (direction, x, y) = FACTORY_HOUSE_POS[pos - 1]
        if type == 0:
            if pos in houses:
                del houses[pos]
            
        else:
            houses[pos] = CHouse(x, y, (2000 + direction - 1) + (type - 101) * 2)
        if direction == 1:
            x -= 328
            y += 20
        else:
            x += 311
            y += 3
    else:
        return None
    doorplates[pos] = CDoorplate(x, y, pos, direction, name)


def S2CDistrict(netobj):
    global g_LandState
    oMap = map.GetGameMapObject()
    if not oMap:
        return None
    
    
    try:
        houses = map.g_Map.m_Houses
    except:
        houses = { }
        map.g_Map.m_Houses = houses
        map.g_Map.m_Doorplates = { }
        map.g_Map.m_PlantCards = { }

    doorplates = map.g_Map.m_Doorplates
    op = netobj.UnpackInt(1)
    if op == 1:
        pos = netobj.UnpackInt(1)
        type = netobj.UnpackInt(1)
        playerid = netobj.UnpackInt(4)
        name = netobj.UnpackString(0)
        CreateHouseAndDoorplate(houses, doorplates, pos, type, name)
        if pos in houses:
            import hero
            if playerid == hero.g_ID:
                houses[pos].m_IsOwner = True
            else:
                houses[pos].m_IsOwner = False
        
    elif op == 2:
        g_LandState = { }
        n = netobj.GetCmdLen() - 1
        for i in xrange(n / 4):
            nameLen = netobj.UnpackInt(1)
            name = netobj.UnpackString(nameLen)
            CreateHouseAndDoorplate(houses, doorplates, i + 1, netobj.UnpackInt(1), name)
            forSale = netobj.UnpackInt(1)
            isowner = netobj.UnpackInt(1)
            notTakeOver = not netobj.UnpackInt(1)
            isBuyed = netobj.UnpackInt(1)
            if isBuyed:
                g_LandState[i + 1] = 1
            
            if forSale:
                g_LandState[i + 1] = 2
            
            if i + 1 in houses:
                houses[i + 1].m_NotTakeOver = notTakeOver
                houses[i + 1].m_IsOwner = isowner
                continue
        
    elif op == 3:
        pos = netobj.UnpackInt(1)
        dp = doorplates.get(pos)
        if dp:
            name = netobj.UnpackString(0)
            dp.SetName(name)
            import dlgmap
            dlgmap.RefershDistrictTips(pos, name)
            return None
        
    elif op == 4:
        if not None:
            pass
        plantcards = None
        map.g_Map.m_PlantCards = None
        sum = netobj.UnpackInt(1)
        for i in range(sum):
            pos = netobj.UnpackInt(1)
            num = netobj.UnpackInt(1)
            state = netobj.UnpackInt(1)
            if num > 0:
                CreatePlantCard(houses, plantcards, pos, num, state)
                continue
        
    elif op == 5:
        import dlgroomvisit
        dlgroomvisit.GetMiniRoomMap()
    elif op == 6:
        import dlgmillvisit
        dlgmillvisit.GetMiniRoomMap()
    elif op == 7:
        posList = []
        iLen = netobj.UnpackInt(1)
        for i in xrange(iLen):
            pos = netobj.UnpackInt(1)
            posList.append(pos)
        
        SetAttentionList(posList)
    
    import dlgmap
    dlgmap.RefreshMinimap()


def C2SGetDistrictTip(pos):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DISTRICT)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddI(pos, 1)
    netobj.PacketSend()
