# pycdc 交叉复核产物 · script.fls entry 4861
# co_filename(原始)='script/architect.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4861.pyc (Python 2.5)

import interface
import ui
import world
import map

class CArchObject(interface.CMapAddonObject, interface.CBase):
    DIR2VALUE = {
        1: 'r',
        2: 'l' }
    
    def __init__(self, parent, city, direct, component, x, y):
        
        try:
            interface.CMapAddonObject.__init__(self, parent, 1, 'architect/%d/%s%d' % (city, self.DIR2VALUE[direct], component), 'mapobject')
        except:
            interface.CMapAddonObject.__init__(self, parent, 1, 'architect/1/l1', 'mapobject')

        interface.CBase.__init__(self)
        self.MessageProcess()
        self.Place(x, y)

    
    def SetOwner(self, owner):
        if owner:
            self.m_Owner = interface.CShadowObject(owner)
        else:
            self.m_Owner = None

    
    def GetOwner(self):
        if getattr(self, 'm_Owner', False):
            return self.m_Owner.Get()
        

    
    def CoverCondition(self):
        owner = self.GetOwner()
        if owner:
            return owner.OnCover(self)
        
        return False

    
    def Enter(self):
        owner = self.GetOwner()
        if owner:
            owner.OnEnter(self)
        

    
    def Leave(self):
        owner = self.GetOwner()
        if owner:
            owner.OnLeave(self)
        

    
    def LeftDown(self):
        owner = self.GetOwner()
        if not owner and owner.OnLeftDown():
            map.g_Map.LeftDown()
        

    
    def LeftUp(self):
        import cursor
        import C_sys
        import npc
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            if isinstance(obj, npc.CNpc):
                obj.LeftUp()
                return None
                continue
        
        owner = self.GetOwner()
        if not owner and owner.OnLeftUp():
            map.g_Map.LeftUp()
        

    
    def RightDown(self):
        owner = self.GetOwner()
        if not owner and owner.OnRightDown():
            map.g_Map.RightDown()
        

    
    def RightUp(self):
        import cursor
        import C_sys
        import goods
        (x, y) = cursor.GetPos()
        objects = C_sys.GetObjects(x, y)
        for obj in objects:
            if isinstance(obj, goods.CGoodsBase):
                obj.RightUp()
                return None
                continue
        
        owner = self.GetOwner()
        if not owner and owner.OnRightUp():
            map.g_Map.RightUp()
        



class CArchManager(interface.CBaseObject, world.CObject):
    COMP2Z = {
        1: 0,
        2: 0,
        3: 10000,
        4: 10000,
        5: 20000,
        6: 20000 }
    BUILDING2DATA = {
        8001: (1,),
        8002: (2,),
        8003: (2, 3),
        8004: (2, 4, 5),
        8005: (2, 4, 6) }
    CITY2COLOR = {
        1: '\xbe\xed',
        2: '\xba\xf1',
        3: '\xb6\xc0',
        4: '\xc2\xc5' }
    
    def __init__(self, id, x, y):
        interface.CBaseObject.__init__(self, map.g_Map)
        world.CObject.__init__(self, id)
        self.SetPos(x, y)
        self.m_IgnoreMapDel = True

    
    def CreateWorker(self, x, y):
        import walker
        walkerobj = walker.CreateWalker(x, y, 0, [
            3002,
            3007,
            3004,
            3023][self.m_City - 1], 0)
        walkerobj.m_IgnoreMapDel = True
        walkerobj.SetState('work')
        (x, y) = self.GetPos()
        x += 170
        y -= 250
        walkerobj.SetPos(x, y)
        walkerobj.SetDirection(0)
        self.m_WalkerObj = walkerobj
        spr = interface.CMapSpriteObject(self.m_WalkerObj, 'architect/ani/big_fog.spr', 'mapobject')
        spr.SetZ(-1)
        spr.CreateCommand(1, 'animation')
        self.m_SpriteObj = spr
        
        def _move(obj, times):
            (x, y) = obj.GetPos()
            y = y - 180
            if times % 2:
                x -= 150
                y -= 70
                obj.m_WalkerObj.SetDirection(8)
            else:
                x += 170
                y -= 70
                obj.m_WalkerObj.SetDirection(0)
            obj.m_WalkerObj.SetPos(x, y)
            return (times + 1,)

        self.m_WorkerCommand = self.CreatePyCommand(300, _move, 1)

    
    def SetInvester(self, name):
        if name:
            self.m_Invester = interface.CTextObject(map.g_Map, '\xa7\xeb\xb8\xea\xa4H\xa1G%s' % name, interface.FontLT16_1, interface.COLOR_43, 0)
            self.m_Invester.m_Bk = interface.CTextObject(self.m_Invester, '\xa7\xeb\xb8\xea\xa4H\xa1G%s' % name, interface.FontLT16_1, 2105376, 0)
            self.m_Invester.m_Bk.SetZ(-1)
            self.m_Invester.m_Bk.SetPos(1, 1)
            (x, y) = self.GetPos()
            (w, _) = self.m_Invester.GetSize()
            self.m_Invester.SetPos(x - w / 2, y - 500)
            self.m_Invester.SetZ(10000)
        else:
            self.m_Invester = None

    
    def RefreshSchedule(self, schedule):
        if schedule == 3000 or not (self.m_Invester):
            self.m_ScheduleBottom = None
            return None
        
        if not hasattr(self, 'm_Schedule'):
            color = self.CITY2COLOR[self.m_City]
            self.m_ScheduleBottom = ui.CImage(self.m_Invester, 'combdialog/\xd4\xd3\xcd\xbc/\xbd\xf8\xb6\xc8\xcc\xf5\xb5\xd7.igs', interface.UIPath)
            self.m_Schedule = interface.CProgressObject(self.m_ScheduleBottom, 'combdialog/\xd4\xd3\xcd\xbc/%s\xc9\xab\xbd\xf8\xb6\xc8\xcc\xf5.igs' % color, interface.UIPath)
            (\xba\xa4, ih) = self.m_Invester.GetSize()
            (sw, sh) = self.m_ScheduleBottom.GetSize()
            x = (\xba\xa4 - sw) / 2
            self.m_ScheduleBottom.SetPos(x, ih + 4)
        
        self.m_Schedule.SetRate(schedule / 3)

    
    def Refresh(self, data):
        self.m_Objects = []
        for city, direct, comp in data:
            arch_obj = self.CreateArch(city, direct, comp)
            self.m_Objects.append(arch_obj)
        

    
    def CreateArch(self, city, direct, comp):
        (x, y) = self.GetPos()
        arch_obj = CArchObject(map.g_Map, city, direct, comp, x, y)
        arch_obj.SetZ(y + self.COMP2Z[comp])
        arch_obj.SetOwner(self)
        arch_obj.m_Data = (city, direct, comp)
        return arch_obj

    
    def GetResSize(self):
        if self.m_Objects:
            arch_obj = self.m_Objects[0]
            return arch_obj.GetResSize()
        
        return (0, 0)

    
    def GetResKey(self):
        if self.m_Objects:
            arch_obj = self.m_Objects[0]
            return arch_obj.GetResKey()
        
        return (0, 0)

    
    def OnCover(self, obj):
        return True

    
    def OnEnter(self, obj):
        import cursor
        cursor.Load(cursor.CHAT_CURSOR)

    
    def OnLeave(self, obj):
        import cursor
        cursor.Load(cursor.NORMAL_CURSOR)

    
    def OnLeftDown(self):
        return True

    
    def OnLeftUp(self):
        import map
        map.StopMove()
        if not map.AllowMove():
            return None
        
        import misc
        tm = misc.Time()
        if hasattr(self, 'm_prevclick') and tm < self.m_prevclick + 0.5:
            return None
        
        self.m_prevclick = tm
        import hero
        import math
        import map
        import autofindpath
        (hx, hy) = hero.g_Hero.GetPos()
        (x, y) = self.GetPos()
        y = y - 180
        autofindpath.SafeStopAuto(self.m_ID)
        dist = math.sqrt((hy - y) * (hy - y) + (hx - x) * (hx - x))
        if dist < 15 * map.CELLSIZE:
            import netnpc
            import dlgnpc
            netnpc.C2SNpcLook(self.m_ID)
            dlgnpc.g_ShowTask = True
        else:
            dy = int(y + (hy - y) * 6 * map.CELLSIZE / dist)
            dx = int(x + (hx - x) * 6 * map.CELLSIZE / dist)
            hero.WalkTo(dx, dy)
        return True

    
    def OnRightDown(self):
        return False

    
    def OnRightUp(self):
        return False



def CreateArchitect(x, y, id, name, city, building, direct, schedule):
    arch_obj = CArchManager(id, x, y + 180)
    arch_obj.m_Direct = direct - 1
    arch_obj.m_City = city
    data = [ (city, direct, comp) for comp in arch_obj.BUILDING2DATA[building] ]
    arch_obj.Refresh(data)
    return arch_obj
