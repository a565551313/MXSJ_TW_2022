# pycdc 交叉复核产物 · script.fls entry 3815
# co_filename(原始)='script/core/garth.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3815.pyc (Python 2.5)

import chardefine
import chatoutput
import cursor
import interface
import map
import room
import world
import wrapinterface
import farmtouchlogic
AQUATIC_POS_DATA = {
    2151: ((40, 433), (137, 401), (40, 509), (140, 520), (229, 457), (352, 442), (631, 38), (768, 38), (923, 38), (1067, 40), (768, 128), (926, 146), (1139, 134), (762, 250), (912, 274), (1070, 238), (1101, 358), (1224, 254)),
    2152: ((67, 774), (113, 651), (244, 736), (415, 667), (956, 78), (1001, 156), (929, 264), (838, 303), (832, 418), (941, 414), (1061, 364), (1166, 307), (1188, 201), (1064, 246), (1106, 165), (971, 330)),
    2153: ((78, 1022), (232, 948), (1102, 124), (1176, 450), (1680, 674), (1636, 800), (1792, 862), (1958, 924), (2090, 996), (1834, 694), (1938, 796), (2098, 868), (2050, 706), (2140, 618)) }
ANI_SPEED_DATA = {
    1: 1,
    2: 5,
    3: 2,
    4: 1,
    5: 4,
    6: 4,
    7: 3,
    8: 4,
    31: 10,
    32: 10,
    91: 8,
    92: 8,
    93: 8,
    94: 8,
    95: 8,
    96: 8,
    97: 8,
    98: 8,
    99: 8,
    121: 8,
    122: 6,
    123: 6,
    124: 7,
    125: 8 }
ANIMAL_POS_DATA = {
    2151: ((77, 676), (76, 797), (73, 905), (247, 611), (260, 770), (281, 905), (428, 559), (464, 721), (491, 892), (589, 382), (783, 484), (996, 518), (1211, 532), (1350, 403), (1341, 62), (1358, 217), (632, 571), (700, 742), (777, 893), (888, 655), (1017, 854), (1139, 706), (1278, 883), (1298, 673)),
    2152: ((136, 950), (136, 1098), (366, 900), (374, 1074), (578, 796), (578, 960), (576, 1112), (790, 686), (804, 898), (840, 1082), (1010, 582), (1028, 802), (1082, 1032), (1246, 482), (1280, 686), (1302, 888), (1334, 1080), (1382, 288), (1470, 180), (1516, 442), (1524, 636), (1578, 864), (1620, 1064), (1876, 1094), (1840, 846), (1808, 602), (1772, 348)),
    2153: ((128, 1232), (134, 1382), (330, 1116), (342, 1330), (558, 1024), (568, 1212), (568, 1388), (800, 902), (798, 1120), (802, 1360), (1042, 750), (1048, 996), (1048, 1232), (1192, 1390), (1528, 1384), (1834, 1376), (2072, 1290), (1778, 1142), (1398, 1150), (1468, 974), (1252, 834), (1284, 606), (1716, 328), (1456, 70), (2060, 106)) }
ANIMAL_SHADOW_DATA = {
    31: 1,
    32: 1,
    33: 1,
    34: 1,
    35: 1,
    36: 1,
    37: 1,
    38: 1,
    121: 1,
    123: 1,
    124: 1,
    125: 1 }
ANIMAL_OP_POS_DATA = {
    2151: (330, 530),
    2152: (600, 675),
    2153: (500, 905) }
ROAD_INFO_DATA = (((654, 641), (806, 717), (958, 793), (1110, 869), (1262, 946), (1413, 1022)), ((619, 492), (769, 566), (919, 639), (1070, 713), (1221, 787)), ((654, 641), (806, 717), (958, 793), (1110, 869), (1262, 946), (1413, 1022)))
DOOR_INFO_DATA = {
    29825: (('29825a', 418 + 1300 / 2, 968), ('29825b', 538, 1118), ('29825b', 706, 1034), ('29825b', 1403, 687)),
    29826: (('29826a', 418 + 1300 / 2, 968), ('29826b', 548, 1116), ('29826b', 718, 1031), ('29826b', 1428, 677)),
    29827: (('29827a', 418 + 1300 / 2, 968), ('29827b', 537, 1071), ('29827b', 714, 983), ('29827b', 1438, 621)),
    29828: (('29828a', 903 + 1300 / 2, 1131), ('29828b', 658, 1424), ('29828b', 836, 1335), ('29828b', 1015, 1246), ('29828b', 1194, 1157), ('29828b', 1974, 768)),
    29829: (('29829a', 903 + 1300 / 2, 1131), ('29829b', 638, 1410), ('29829b', 818, 1320), ('29829b', 999, 1230), ('29829b', 1180, 1140), ('29829b', 1948, 758)),
    29830: (('29830a', 903 + 1300 / 2, 1131), ('29830b', 608, 1454), ('29830b', 792, 1362), ('29830b', 976, 1270), ('29830b', 1159, 1179), ('29830b', 1956, 782)),
    29831: (('29831a', 1168 + 1300 / 2, 1414), ('29831b', 594, 1828), ('29831b', 786, 1733), ('29831b', 978, 1637), ('29831b', 1170, 1541), ('29831b', 1360, 1446), ('29831b', 2166, 1041), ('29831b', 2354, 946)),
    29832: (('29832a', 1168 + 1300 / 2, 1324), ('29832b', 836, 1690), ('29832b', 1009, 1603), ('29832b', 1183, 1516), ('29832b', 1357, 1429), ('29832b', 2283, 967)),
    29833: (('29833a', 1168 + 1300 / 2, 1324), ('29833b', 832, 1697), ('29833b', 1006, 1610), ('29833b', 1180, 1523), ('29833b', 1354, 1436), ('29833b', 2108, 1060), ('29833b', 2282, 973)) }
PLANT_INFO_DATA = {
    11: (1, 1, 0, 0, 1, 1, 1),
    12: (1, 1, 0, 0, 1, 1, 1),
    13: (1, 1, 0, 0, 1, 1, 1),
    14: (1, 1, 0, 0, 1, 1, 1),
    15: (1, 1, 0, 0, 1, 1, 1),
    16: (1, 1, 0, 0, 1, 1, 1),
    17: (1, 1, 0, 0, 1, 1, 1),
    18: (1, 1, 0, 0, 1, 1, 1),
    19: (1, 1, 0, 0, 1, 1, 1),
    20: (1, 1, 0, 0, 1, 1, 1),
    21: (2, 2, 0, 0, 2, 2, 2),
    22: (2, 2, 0, 0, 2, 2, 2),
    23: (2, 2, 0, 0, 2, 2, 2),
    24: (2, 2, 0, 0, 2, 2, 2),
    25: (2, 3, 0, 0, 3, 3, 3),
    26: (2, 3, 0, 0, 3, 3, 3),
    27: (2, 3, 0, 0, 3, 3, 3),
    28: (2, 3, 0, 0, 3, 3, 3),
    29: (3, 0, 0, 0, 0, 0, 0),
    30: (3, 0, 0, 0, 0, 0, 0),
    31: (3, 0, 0, 0, 0, 0, 0),
    32: (3, 0, 0, 0, 0, 0, 0),
    33: (4, 0, 0, 0, 0, 0, 0),
    34: (4, 0, 0, 0, 0, 0, 0),
    35: (4, 0, 0, 0, 0, 0, 0),
    36: (4, 0, 0, 0, 0, 0, 0),
    37: (4, 0, 0, 0, 0, 0, 0) }
PLANT_POS_DATA = ((0, -10), (-35, 0), (23, -30), (35, 0), (-23, -30))
F_EARTH_X = 64
F_EARTH_Y = 34
FARM_POS_DATA = {
    2151: (200, 750),
    2152: (480, 950),
    2153: (700, 1150) }
FARM_SIZE_DATA = {
    2151: (3, 3),
    2152: (3, 4),
    2153: (4, 4) }
F_EARTH_POS_DATA = {
    2151: ((2, 0), (3, 1), (4, 2), (1, 1), (2, 2), (3, 3), (0, 2), (1, 3), (2, 4)),
    2152: ((2, 0), (3, 1), (4, 2), (5, 3), (1, 1), (2, 2), (3, 3), (4, 4), (0, 2), (1, 3), (2, 4), (3, 5)),
    2153: ((2, 0), (3, 1), (4, 2), (5, 3), (1, 1), (2, 2), (3, 3), (4, 4), (0, 2), (1, 3), (2, 4), (3, 5), (-1, 3), (0, 4), (1, 5), (2, 6)) }

class CPoint(interface.CMapAddonObject):
    
    def __init__(self, parent):
        interface.CMapAddonObject.__init__(self, parent, 1, 'furniture\\animal\\point', 'mapobject')



class CGarden(room.CFurniture):
    
    def __init__(self, parent, x, y, idx, id, direction):
        room.CFurniture.__init__(self, parent, x, y, idx, id, direction)
        self.m_X = x
        self.m_Y = y
        self.m_ID = id
        self.m_Direction = direction
        self.MessageProcess()
        self.ClearPlant()

    
    def ClearPlant(self):
        self.m_Plant = { }

    
    def PlacePlant(self, type, pos, state, phase, pal = 0):
        print 'type,pos,state,phase,pal', type, pos, state, phase, pal
        info = PLANT_INFO_DATA[type]
        pkind = info[1 + state * 3 + phase]
        if pkind == 0:
            filename = 'furniture\\plant\\%.2d%d%d%d' % (type, self.m_Direction, phase + 1, state)
        else:
            filename = 'furniture\\plant\\%d%d%d%d' % (pkind, self.m_Direction, phase + 1, state)
        if info[0] == 1:
            (dx, dy) = PLANT_POS_DATA[self.m_Direction * 2 + pos]
        else:
            (dx, dy) = PLANT_POS_DATA[0]
        x = self.m_X + dx
        y = self.m_Y + dy
        
        try:
            obj = CPlant(self.GetParent(), filename, x, y, 0, 5, 0, pal)
            obj.SetRealParent(self)
        except:
            return None

        self.m_Plant[pos] = obj

    
    def Enter(self):
        if world.g_ConverCondition == world.RemoveFurnitureCondition or world.g_ConverCondition == world.SeedCondition:
            world.CObject.Enter(self)
        else:
            interface.CMapAddonObject.SetLight(self, 16)
            self.m_Borther.SetLight(16)
            for idx in self.m_Plant:
                self.m_Plant[idx].SetLight(16)
            

    
    def Leave(self):
        if world.g_ConverCondition == world.RemoveFurnitureCondition or world.g_ConverCondition == world.SeedCondition:
            world.CObject.Leave(self)
        else:
            interface.CMapAddonObject.SetLight(self, 8)
            self.m_Borther.SetLight(8)
            for idx in self.m_Plant:
                self.m_Plant[idx].SetLight(8)
            

    
    def LeftUp(self):
        if world.g_ConverCondition == world.RemoveFurnitureCondition or world.g_ConverCondition == world.SeedCondition:
            world.CObject.LeftUp(self)
        else:
            import netroom
            netroom.DoLook(self.m_Idx)
            self.SetLight(8)
            return None

    
    def SetLight(self, light):
        interface.CMapAddonObject.SetLight(self, light)
        interface.CMapAddonObject.SetLight(self.m_Borther, light)
        for p in self.m_Plant.values():
            if isinstance(p, interface.CMapAddonObject):
                interface.CMapAddonObject.SetLight(p, light)
                continue
        



class CAnimalOP(room.CFurniture):
    
    def __init__(self, parent, x, y, idx, direction):
        room.CFurniture.__init__(self, parent, x, y, idx, 29999, direction)
        self.m_X = x
        self.m_Y = y
        self.m_ID = 29999
        self.m_Direction = direction
        self.m_Idx = 0
        self.MessageProcess()

    
    def Enter(self):
        print 'enter', world.g_ConverCondition
        if world.g_ConverCondition == world.NormalCondition:
            interface.CMapAddonObject.SetLight(self, 16)
            cursor.Load(cursor.CHAT_CURSOR)
        

    
    def Leave(self):
        if world.g_ConverCondition == world.NormalCondition:
            interface.CMapAddonObject.SetLight(self, 8)
            cursor.Load(cursor.NORMAL_CURSOR)
        

    
    def LeftUp(self):
        if world.g_ConverCondition == world.NormalCondition:
            import netroom
            netroom.C2SAnimalOP()
            return None
        



class CNideAni(interface.CMapWalkerObject):
    
    def __init__(self, parent, id):
        interface.CMapWalkerObject.__init__(self, parent)
        self.m_Path = 'furniture/animal/%.5d/stand.spr' % id
        self.SetState(1)
        self.m_AniHandle = self.CreateCommand(0, 'animation')
        self.m_MaskObj = interface.CMapWalkerMaskObject(map.GetMaskPanel(), self)

    
    def SetState(self, string):
        self.Load(self.m_Path, 'mapobject')

    
    def WalkTo(self, x, y):
        self.SetState(1)

    
    def CSetDirection(self, d):
        pass

    
    def Stop(self):
        pass



class CNide(room.CFurniture):
    
    def __init__(self, parent, x, y, idx, id, direction):
        room.CFurniture.__init__(self, parent, x, y, idx, id, direction)
        self.m_Animal = CNideAni(self, id)

    
    def Enter(self):
        if world.g_ConverCondition == world.RemoveAnimalCondition:
            world.CObject.Enter(self)
            interface.CMapAddonObject.SetLight(self, 16)
        

    
    def Leave(self):
        if world.g_ConverCondition == world.RemoveAnimalCondition:
            world.CObject.Leave(self)
            interface.CMapAddonObject.SetLight(self, 8)
        

    
    def LeftUp(self):
        if world.g_ConverCondition == world.RemoveAnimalCondition:
            world.CObject.LeftUp(self)
        

    
    def ShowAnimal(self, isShow):
        self.m_Animal.SetShow(isShow)



def MouseClick(x, y):
    import yardmapanimal
    if world.g_ConverCondition == world.PlantCondition:
        import room
        room.DoCancel()
    
    
    try:
        (speobj, ml) = map.g_Map.m_Room.GetSpaceObject(29900)
        import misc
        if CanPlace(x, y, speobj):
            for _, obj in map.g_Map.g_Animals.iteritems():
                if isinstance(obj, (yardmapanimal.CAquatic, CAquatic)):
                    obj.CheckWalkTo(x + misc.RandInt(-10, 10), y + misc.RandInt(-10, 10))
                    continue
            
            return False
    except:
        pass

    return True


def CanPlace(x, y, speobj):
    for dx, dy in ((20, 0), (-50, -50), (20, -50), (-50, 0)):
        if not interface.CMapAddonObject.CanPlace(map.g_Map.m_Point, x + dx, y + dy, speobj):
            return False
            continue
    
    return True


def FindSpace(speobj, list):
    import misc
    for i in list:
        (x, y) = list[misc.RandInt(0, len(list) - 1)]
        print 'CanPlace', x, y
        if CanPlace(x, y, speobj):
            return (x, y)
            continue
    
    for x, y in list:
        if CanPlace(x, y, speobj):
            return (x, y)
            continue
    
    return (x, y)


class CAquatic(interface.CMapWalkerObject):
    
    def __init__(self, parent, type):
        interface.CMapWalkerObject.__init__(self, parent)
        self.m_MaskObj = interface.CMapWalkerMaskObject(map.GetMaskPanel(), self)
        self.m_Path = 'furniture\\animal\\%.3d\\' % type
        self.SetState('stand')
        
        try:
            self.m_Speed = ANI_SPEED_DATA[type]
        except:
            self.m_Speed = 5

        pos = AQUATIC_POS_DATA.get(map.g_Map.m_Room.m_ID)
        (speobj, ml) = map.g_Map.m_Room.GetSpaceObject(29900)
        (x, y) = FindSpace(speobj, pos)
        self.m_CircleX = x
        self.m_CircleY = y
        self.SetPos(self.m_CircleX, self.m_CircleY)
        self.m_AniHandle = self.CreateCommand(0, 'animation')
        self.Stop()
        
        def SetFrameType(ob):
            a = misc.RandInt(0, 1)
            if a == 0:
                chatoutput.AddChatFloat(self, '\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K')
            else:
                chatoutput.AddChatFloat(self, '!@#$%^&*!@#$%^&')
            return ()

        
        def SetFrameType1(ob):
            if self.time_type == 1:
                self.time_type = 0
                self.CreatePyCommand(3600, SetFrameType)
                return None
            
            a = misc.RandInt(0, 1)
            if a == 0:
                chatoutput.AddChatFloat(self, '\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K')
            else:
                chatoutput.AddChatFloat(self, '!@#$%^&*!@#$%^&')
            self.time_type += 1
            return ()

        import misc
        self.time_type = 0
        kk = misc.RandInt(0, 3600)

    
    def SetState(self, state):
        
        try:
            self.Load(self.m_Path + state + '.spr', 'mapobject')
        except:
            self.Load(self.m_Path + 'stand.spr', 'mapobject')


    
    def CSetDirection(self, d):
        pass

    
    def Stop(self):
        import misc
        self.SetState('stand')
        
        def Move(obj):
            (speobj, ml) = map.g_Map.m_Room.GetSpaceObject(29900)
            (x, y) = obj.GetPos()
            dx = misc.RandInt(-30, 30)
            dy = misc.RandInt(-30, 30)
            step = misc.RandInt(2, 10)
            for i in xrange(step):
                x += dx
                y += dy
                if not CanPlace(x, y, speobj):
                    x -= dx
                    y -= dy
                    break
                    continue
            
            if i == 0:
                obj.CreatePyCommand(1, Move)
                return None
            
            obj.WalkTo(x, y)

        self.CreatePyCommand(misc.RandInt(10, 40), Move)

    
    def CheckWalkTo(self, x2, y2):
        (speobj, ml) = map.g_Map.m_Room.GetSpaceObject(29900)
        (x1, y1) = self.GetPos()
        dw = x1 - x2
        dh = y1 - y2
        dw = abs(dw) / 5
        dh = abs(dh) / 5
        if x1 < x2:
            dx = 5
        else:
            dx = -5
        if y1 < y2:
            dy = 5
        else:
            dy = -5
        f = 0
        if dw > dh:
            dw += 1
            for i in xrange(dw):
                if not CanPlace(x1, y1, speobj):
                    return None
                
                f += dh
                if f >= dw:
                    f -= dw
                    y1 += dy
                
                x1 += dx
            
        else:
            dh += 1
            for i in xrange(dh):
                if not CanPlace(x1, y1, speobj):
                    return None
                
                f += dw
                if f >= dh:
                    f -= dh
                    x1 += dx
                
                y1 += dy
            
        self.WalkTo(x2, y2)

    
    def WalkTo(self, newx, newy):
        args = { }
        args['whole_path'] = 0
        args['end_x'] = newx
        args['end_y'] = newy
        args['speed'] = self.m_Speed
        args['linear'] = 1
        self.SetState('walk')
        self.CreateCommand(0, 'walk', args)



class CAnimal(interface.CMapWalkerObject, world.CObject):
    
    def __init__(self, parent, idx, type, flag):
        interface.CMapWalkerObject.__init__(self, parent)
        self.m_MaskObj = interface.CMapWalkerMaskObject(map.GetMaskPanel(), self)
        self.m_Idx = idx
        self.m_Path = 'furniture\\animal\\%.3d\\' % type
        self.SetState('stand')
        if type in ANIMAL_SHADOW_DATA:
            self.m_Shadow = interface.CMapImagesObject(self, 'shadow1.igs', chardefine.PCK_CHAR)
            self.m_Shadow.SetZ(-1)
        
        
        try:
            self.m_Speed = ANI_SPEED_DATA[type]
        except:
            self.m_Speed = 10

        pos = ANIMAL_POS_DATA.get(map.g_Map.m_Room.m_ID)
        if flag:
            import hero
            (x, y) = hero.g_Hero.GetPos()
        else:
            (speobj, ml) = map.g_Map.m_Room.GetSpaceObject(0)
            (x, y) = FindSpace(speobj, pos)
        self.m_CircleX = x
        self.m_CircleY = y
        self.SetPos(x, y)
        self.m_AniHandle = self.CreateCommand(0, 'animation')
        self.m_Type = 0
        if type in (31, 32):
            self.m_Type = 1
        
        
        def Timer(obj):
            import misc
            import hero
            dx = misc.RandInt(-80, 80)
            dy = misc.RandInt(-80, 80)
            (mx, my) = obj.GetPos()
            if obj.m_Type == 1:
                (x, y) = hero.g_Hero.GetPos()
                if abs(mx - x) > 81 and abs(my - y) > 81 or misc.RandInt(0, 3) == 0:
                    obj.WalkTo(x + dx, y + dy)
                
            elif misc.RandInt(0, 2) == 0:
                obj.WalkTo(mx + dx, my + dy)
            
            return ()

        self.CreatePyCommand(40, Timer)
        
        def SetFrameType(ob):
            a = misc.RandInt(0, 1)
            if a == 0:
                chatoutput.AddChatFloat(self, '\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K')
            else:
                chatoutput.AddChatFloat(self, '!@#$%^&*!@#$%^&')
            return ()

        
        def SetFrameType1(ob):
            if self.time_type == 1:
                self.time_type = 0
                self.CreatePyCommand(3600, SetFrameType)
                return None
            
            a = misc.RandInt(0, 1)
            if a == 0:
                chatoutput.AddChatFloat(self, '\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K\xa1K')
            else:
                chatoutput.AddChatFloat(self, '!@#$%^&*!@#$%^&')
            self.time_type += 1
            return ()

        import misc
        self.time_type = 0
        kk = misc.RandInt(0, 3600)

    
    def CSetDirection(self, d):
        pass

    
    def SetState(self, state):
        
        try:
            self.Load(self.m_Path + state + '.spr', 'mapobject')
        except:
            self.Load(self.m_Path + 'stand.spr', 'mapobject')


    
    def Stop(self):
        self.SetState('stand')

    
    def WalkTo(self, x, y):
        if self.m_Type != 1:
            (speobj, ml) = map.g_Map.m_Room.GetSpaceObject(0)
            if not CanPlace(x, y, speobj):
                return None
            
        
        args = { }
        args['whole_path'] = 1
        args['end_x'] = x
        args['end_y'] = y
        args['speed'] = self.m_Speed
        self.SetState('walk')
        self.CreateCommand(0, 'walk', args)



def CreateDoor(parent, id, idx):
    Doors = []
    for i, info in enumerate(DOOR_INFO_DATA[idx]):
        (name, x, y) = info
        door = CMapFurnObject(parent, True, 'furniture\\' + name, 'mapobject')
        Doors.append(door)
        door.Place(x, y, map.g_Map.m_Room.GetSpaceObject(id)[0])
    
    return Doors


def CreateRoad(parent, id, idx):
    Roads = []
    name = 'furniture\\' + '%da' % idx
    for x, y in ROAD_INFO_DATA[id - 2151]:
        x += 200
        y += 20
        road = CMapFurnObject(parent, False, name, 'mapobject')
        Roads.append(road)
        road.Place(x, y)
    
    return Roads


def Init(id):
    map.g_Map.m_Point = CPoint(map.g_Map)
    if id >= 2151 and id <= 2153 and hasattr(map.g_Map, 'm_MiniMapID') and map.g_Map.m_MiniMapID != 9999:
        (x, y) = ANIMAL_OP_POS_DATA[id]
        map.g_Map.m_Room.m_AnimalOP = CAnimalOP(map.g_Map, x, y, 291, 0)
        if map.GetCurrentSceneID() not in (1162,):
            map.g_Map.g_Farm = CFarm(id)
        
    


def GetFarmTouchLogic():
    oFarm = getattr(map.GetGameMapObject(), 'g_Farm', None)
    if oFarm:
        return oFarm.GetFarmTouchLogic()
    else:
        return None


class CField(world.CObject, interface.CMapAddonObject):
    
    def __init__(self, parent, x, y, pos):
        interface.CMapAddonObject.__init__(self, map.g_Map, False, 'furniture/earth', 'mapobject')
        self.MessageProcess()
        self.Place(x, y)
        self.m_X = x
        self.m_Y = y
        self.m_Pos = pos
        self.m_Plant = None
        self.ClearObject()
        self.m_Box = CFarmBox(self, self.m_X - 30, self.m_Y - 15, pos)

    
    def ClearObject(self):
        if self.m_Plant:
            self.m_Plant.Release()
            self.m_Plant = None
        

    
    def SetPlant(self, plant):
        self.m_Plant = plant

    
    def GetPlant(self):
        
        try:
            return map.g_Map.g_Plant[self.m_Plant]
        except:
            return None


    
    def IsFarmBox(self):
        if isinstance(self.m_Box, CFarmBox):
            return True
        else:
            return False

    
    def Enter(self):
        if not self.IsFarmBox():
            if world.g_ConverCondition == world.PlantCondition:
                LightControl(self.m_Pos, 16)
            
        else:
            oFarmTouchLogic = GetFarmTouchLogic()
            if oFarmTouchLogic:
                pass
            oFarmTouchLogic.OnTouchEvent_Field('enter', self, {
                'iPos': self.m_Pos })

    
    def Leave(self):
        if not self.IsFarmBox():
            if world.g_ConverCondition == world.PlantCondition:
                LightControl(self.m_Pos, 8)
            
        else:
            oFarmTouchLogic = GetFarmTouchLogic()
            if oFarmTouchLogic:
                pass
            oFarmTouchLogic.OnTouchEvent_Field('leave', self, {
                'iPos': self.m_Pos })

    
    def LeftUp(self):
        if not self.IsFarmBox():
            if world.g_ConverCondition == world.PlantCondition:
                world.CObject.LeftUp(self)
            
        else:
            oFarmTouchLogic = GetFarmTouchLogic()
            if oFarmTouchLogic:
                pass
            oFarmTouchLogic.OnTouchEvent_Field('leftup', self, {
                'iPos': self.m_Pos })

    
    def SetLight(self, light):
        interface.CMapAddonObject.SetLight(self, light)

    
    def GetMyPos(self):
        return self.m_Pos



def AddPlant(idx, iType, iDir, iStep, iState, placeid, pal, iCanOp = 0):
    if getattr(map.g_Map, 'g_Farm', None):
        map.g_Map.g_Farm.CreatePlant(idx, iType, iDir, iStep, iState, placeid, pal, iCanOp)
    


def DelPlant(idx):
    if idx in map.g_Map.g_Plant:
        del map.g_Map.g_Plant[idx]
    


def RefreshEarthLight():
    if map.g_Map.g_Farm:
        map.g_Map.g_Farm.RefreshEarthLight()
    


class CFarm(world.CObject, interface.CBaseObject):
    
    def __init__(self, idx):
        interface.CBaseObject.__init__(self, None)
        self.m_oFarmTouchLogic = farmtouchlogic.CYardFarmTouchLogic(map.g_Map, LightControl)
        self.m_fstyle = idx
        (self.m_X, self.m_Y) = FARM_POS_DATA[idx]
        (self.m_Row, self.m_Col) = FARM_SIZE_DATA[idx]
        self.m_Objects = { }
        self.ClearObject()

    
    def GetFarmTouchLogic(self):
        return self.m_oFarmTouchLogic

    
    def GetFarmStyle(self):
        return self.m_fstyle

    
    def ClearObject(self):
        for obj in self.m_Objects.itervalues():
            if obj:
                obj.ClearObject()
                continue
        
        self.m_Objects = { }
        data = F_EARTH_POS_DATA.get(self.m_fstyle)
        for i, f in enumerate(data):
            dx = f[0] * F_EARTH_X
            dy = f[1] * F_EARTH_Y
            obj = CField(self, self.m_X + dx, self.m_Y + dy, i + 1)
            self.m_oFarmTouchLogic.AddFieldObj(obj)
            self.m_Objects[i + 1] = obj
        

    
    def CreatePlant(self, idx, iType, iDir, iStep, iState, placeid, pal, iCanOp = 0):
        pos = min(placeid)
        field = self.m_Objects[pos]
        fname = self.GetPlantFileName(iType, iDir, iStep)
        offpos = self.GetPlantOffPos(fname, iType, iDir)
        print 'fname', fname
        
        try:
            obj = CPlant(map.g_Map, 'furniture\\plant\\%s' % fname, field.m_X + offpos[0], field.m_Y + offpos[1], idx, iStep, iState, pal, iCanOp)
        except:
            obj = None

        map.g_Map.g_Plant[idx] = obj
        for i in placeid:
            self.m_Objects[i].SetPlant(idx)
        

    
    def CheckPlantedByID(self, iPlaceID):
        if iPlaceID not in self.m_Objects:
            return False
        
        if self.m_Objects[iPlaceID].GetPlant():
            return True
        
        return False

    
    def GetPlantOffPos(self, fname, itype, idir):
        _specile = {
            '3010': (-33, 13),
            '3021': (-40, 14),
            '2010': (-30, 14),
            '3121': (25, 15),
            '25020': (-18, 10),
            '25030': (-15, 15),
            '27030': (-30, 15),
            '26020': (-44, 10),
            '23020': (-30, 15),
            '23030': (-30, 15),
            '28020': (-30, 15),
            '21020': (-30, 15),
            '21030': (-30, 15),
            '24020': (-30, 15),
            '24030': (-30, 15),
            '36020': (-35, 25),
            '36030': (-35, 25),
            '36120': (40, 35),
            '36130': (40, 35),
            '37020': (-45, 30),
            '37030': (-30, 20),
            '37120': (40, 25),
            '37130': (30, 20) }
        _offPos = {
            (1, 0): (0, -4),
            (1, 1): (0, -4),
            (2, 0): (-44, 14),
            (2, 1): (30, 14) }
        pos = _specile.get(fname)
        print pos
        if pos:
            return pos
        else:
            data = [
                1,
                0]
            if itype <= itype:
                pass
            elif itype <= 37:
                data[0] = 2
            
            if idir:
                data[1] = 1
            
            print _offPos[tuple(data)]
            return _offPos[tuple(data)]

    
    def GetPlantFileName(self, iType, iDir, iStep):
        _step = {
            1: 10,
            2: 20,
            3: 30,
            4: 30,
            5: 21 }
        _type = {
            1: (11, 20),
            2: (21, 24),
            3: (25, 37) }
        for i, v in _type.items():
            if iType <= iType:
                pass
            elif iType <= v[1]:
                break
                continue
        else:
            return None
        filename = ''
        if i == 3 and iStep != 5:
            import C_sys
            filename = '%d%d%d' % (iType, iDir, _step[iStep])
            a = C_sys.LoadFile('furniture/plant/%s.igs' % filename, 'mapobject')
            if a is None:
                filename = ''
            
            if filename != '':
                print filename
                return filename
            
        
        if iStep == 1 or iStep == 5:
            filename = '%d%d%d' % (i, iDir, _step[iStep])
            if iStep == 5 and iType == 36:
                filename = '%d%d%d' % (2, iDir, _step[iStep])
            
        else:
            filename = '%d%d%d' % (iType, iDir, _step[iStep])
        print filename
        return filename

    
    def RefreshEarthLight(self):
        for obj in self.m_Objects.values():
            obj.SetLight(8)
        

    
    def Enter(self):
        pass

    
    def Leave(self):
        pass

    
    def LeftUp(self):
        pass



def GetFarm():
    if not map.GetGameMapObject():
        return None
    
    return map.GetGameMapObject().GetFarmObject()


def GetPlaceID(iType, iDir, iPos):
    iPlaceidList = []
    oFarm = GetFarm()
    if not oFarm:
        return []
    
    (iRow, iCol) = FARM_SIZE_DATA[oFarm.GetFarmStyle()]
    if oFarm.CheckPlantedByID(iPos):
        return []
    
    if iType <= iType:
        pass
    elif iType <= 37:
        if iDir and iPos % iCol != 0:
            if not oFarm.CheckPlantedByID(iPos + 1):
                iPlaceidList = [
                    iPos,
                    iPos + 1]
            elif iPos % iCol == 1 or oFarm.CheckPlantedByID(iPos - 1):
                iPlaceidList = []
            else:
                iPlaceidList = [
                    iPos,
                    iPos - 1]
        elif iDir and iPos % iCol == 0:
            if not oFarm.CheckPlantedByID(iPos - 1):
                iPlaceidList = [
                    iPos,
                    iPos - 1]
            else:
                iPlaceidList = []
        elif iDir == 0 and iPos + iCol <= iRow * iCol:
            if not oFarm.CheckPlantedByID(iPos + iCol):
                iPlaceidList = [
                    iPos,
                    iPos + iCol]
            elif iPos in range(1, iCol + 1) or oFarm.CheckPlantedByID(iPos - iCol):
                iPlaceidList = []
            else:
                iPlaceidList = [
                    iPos,
                    iPos - iCol]
        elif iDir == 0 and iPos + iCol >= iRow * iCol:
            if not oFarm.CheckPlantedByID(iPos - iCol):
                iPlaceidList = [
                    iPos,
                    iPos - iCol]
            else:
                iPlaceidList = []
        
    else:
        iPlaceidList = [
            iPos]
    return iPlaceidList


def LightControl(pos, light):
    import room
    palceid = GetPlaceID(room.g_PlaceID, room.g_PlaceDirection, pos)
    for i in palceid:
        plant = map.g_Map.g_Farm.m_Objects[i].GetPlant()
        if plant is None:
            map.g_Map.g_Farm.m_Objects[i].SetLight(light)
            continue
    


def IsHasEmptyFarmExcept(tPlaceID = None):
    import map
    oMap = map.GetGameMapObject()
    oFarm = oMap.g_Farm
    dField = oFarm.m_Objects
    bFull = True
    for iPlaceID, oField in dField.iteritems():
        if tPlaceID and iPlaceID in tPlaceID:
            continue
        
        if not oField.GetPlant():
            bFull = False
            LOG('iPlaceID:', iPlaceID, 'oField:', oField.GetPlant())
            break
            continue
    
    return not bFull


def IsEnableQuickFarmEff():
    import yardinterface
    if not yardinterface.IsInYardMap():
        oMap = map.GetGameMapObject()
        if not oMap:
            return False
        
        dBaseInfo = oMap.GetBaseInfo()
        if not dBaseInfo or not dBaseInfo.get('iOwnerID', 0):
            return False
        
    
    return True


class CBox(interface.CBoxObject, world.CObject):
    
    def __init__(self, parent, x, y, pos):
        self.m_ID = None
        self.m_dPropInfo = { }
        interface.CBoxObject.__init__(self, map.g_Map, 65, 38, 0, 0)
        self.SetPos(x - 5, y)
        self.SetZ(100000)
        self.MessageProcess()
        self.m_owner = interface.CShadowObject(parent)
        self.m_Pos = pos

    
    def Enter(self):
        if world.g_ConverCondition == world.PlantCondition:
            LightControl(self.m_owner.Get().m_Pos, 16)
        else:
            obj = self.GetPlant()
            if obj:
                obj.SetLight(16)
                cursor.Load(cursor.CHAT_CURSOR)
            

    
    def Leave(self):
        if world.g_ConverCondition == world.PlantCondition:
            LightControl(self.m_owner.Get().m_Pos, 8)
        else:
            obj = self.GetPlant()
            if obj:
                obj.SetLight(8)
                cursor.Load(cursor.NORMAL_CURSOR)
            else:
                cursor.Load(cursor.NORMAL_CURSOR)

    
    def LeftUp(self):
        if world.g_ConverCondition == world.PlantCondition:
            world.CObject.LeftUp(self)
        elif world.g_ConverCondition == world.PlantItemCondition:
            world.CObject.LeftUp(self)
        else:
            obj = self.GetPlant()
            if obj:
                obj.ClickPlant()
            else:
                import map
                if hasattr(map, 'g_Map') and map.g_Map is not None:
                    map.g_Map.LeftUp()
                

    
    def GetPlant(self):
        owner = self.m_owner.Get()
        if isinstance(owner, CField):
            return owner.GetPlant()
        

    
    def GetMyPos(self):
        return self.m_Pos



class CFarmBox(CBox):
    
    def Enter(self):
        dExtend = {
            'iPos': self.m_owner.Get().m_Pos }
        oFarmTouchLogic = GetFarmTouchLogic()
        if oFarmTouchLogic:
            pass
        oFarmTouchLogic.OnTouchEvent_Box('enter', self, dExtend)

    
    def Leave(self):
        dExtend = {
            'iPos': self.m_owner.Get().m_Pos }
        oFarmTouchLogic = GetFarmTouchLogic()
        if oFarmTouchLogic:
            pass
        oFarmTouchLogic.OnTouchEvent_Box('leave', self, dExtend)

    
    def LeftUp(self):
        oFarmTouchLogic = GetFarmTouchLogic()
        if oFarmTouchLogic:
            pass
        oFarmTouchLogic.OnTouchEvent_Box('leftup', self)



class CPlant(world.CObject, interface.CMapAddonObject):
    
    def __init__(self, parent, filename, x, y, idx, iStep, iState, pal = 0, iCanOp = 0):
        self.m_Pal = pal
        self.m_Path = filename
        self.m_RealParent = None
        interface.CMapAddonObject.__init__(self, parent, True, filename, 'mapobject')
        f = filename.split('\\')
        lastFileName = f[len(f) - 1]
        self.m_LenOfName = len(lastFileName)
        self.m_FileName = lastFileName
        if self.m_LenOfName == 4:
            self.LoadPalProject('furniture/plant/%s.pro' % lastFileName[:1], 'mapobject')
        elif self.m_LenOfName == 5:
            self.LoadPalProject('furniture/plant/%s.pro' % lastFileName[:2], 'mapobject')
        
        
        try:
            if pal != 0:
                self.SetPalProject(pal)
        except:
            pass

        self.MessageProcess()
        self.Place(x, y)
        self.SetZ(self.GetZ() + 1)
        self.m_idx = idx
        self.m_iState = iState
        self.m_iStep = iStep
        self.m_iCanOp = iCanOp
        self.DrawState()

    
    def IsCanShowRewardFlower43(self):
        import hero
        if self.m_iStep != 4:
            return False
        
        if self.m_iCanOp == 1:
            return True
        
        oMapObj = map.GetGameMapObject()
        return False

    
    def DrawState(self):
        (x, y) = self.GetPos()
        (w, h) = self.GetSize()
        if self.IsCanShowRewardFlower43():
            self.m_Text = CFlowerFloat(self, '#43', 10, h)
        elif self.m_iState == 1:
            self.m_Text = CFlowerFloat(self, '#10', 10, h)
        

    
    def SetRealParent(self, parent):
        import misc
        self.m_RealParent = misc.WeakRef(parent)

    
    def GetRealParent(self):
        if self.m_RealParent:
            return self.m_RealParent()
        

    
    def Enter(self):
        oRealParent = self.GetRealParent()
        if oRealParent:
            oRealParent.Enter()
        

    
    def Leave(self):
        oRealParent = self.GetRealParent()
        if oRealParent:
            oRealParent.Leave()
        

    
    def LeftUp(self):
        oRealParent = self.GetRealParent()
        if oRealParent:
            oRealParent.LeftUp()
            return None
        
        import cursor
        import map
        import C_sys
        (x, y) = cursor.GetCursorPos()
        objlst = C_sys.GetObjects(x, y)
        for obj in objlst:
            if isinstance(obj, map.CMap):
                obj.LeftUp()
                break
                continue
        

    
    def ClickPlant(self):
        import netroom
        netroom.ClickPlant(self.m_idx)

    
    def SetLight(self, light):
        interface.CMapAddonObject.SetLight(self, light)



class CFlowerFloat(interface.CBoxObject):
    
    def __init__(self, parent, msg, dx = 0, dy = 0):
        interface.CBoxObject.__init__(self, parent, 10, 10, 0, 117)
        self.m_Msg = wrapinterface.WrapRichText(self, 10, interface.FontLT14_3, msg, normalcolor = 16777215)
        self.m_Msg.SetPos(0, 0)
        self.m_Msg.SetZ(1)
        (w, h) = self.m_Msg.GetSize()
        self.SetSize(w, h)
        self.SetPos(-dx, -dy)
        self._drawedge()

    
    def _drawedge(self, has_point = True):
        self.m_Edge = []
        (w, h) = self.GetSize()
        self.m_Edge = wrapinterface.DrawEdge(self, w, h, 0, 0, has_point)



class CMapFurnObject(interface.CMapAddonObject):
    
    def __init__(self, parent, isBlk, path, pack):
        interface.CMapAddonObject.__init__(self, parent, isBlk, path, pack)
        self.m_Path = path
