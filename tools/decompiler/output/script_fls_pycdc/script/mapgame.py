# pycdc 交叉复核产物 · script.fls entry 1739
# co_filename(原始)='script/mapgame.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1739.pyc (Python 2.5)

import interface
import C_sys
import map
import ui
import world
import nethuodong
import item
import mainmenu
import misc
import snowgame
g_MapgameObj = { }
g_MapEffect = []
g_CachedGamemapID = -1

def ModuleReset():
    global g_MapgameObj, g_MapEffect, g_CachedGamemapID
    g_MapgameObj = { }
    g_MapEffect = []
    g_CachedGamemapID = -1


def LoadMapObject():
    global g_CachedGamemapID
    if misc.IsInKuafuServer():
        return None
    
    g_MapgameObj.clear()
    mapid = -1
    if map.g_Map:
        mapid = map.g_Map.m_ID
    
    import delayloading
    g_CachedGamemapID = mapid
    if not delayloading.IsShowLoading():
        DoLoadMapObject()
    


def DoLoadMapObject():
    global g_CachedGamemapID
    import mapgamedata
    if g_CachedGamemapID == -1:
        return None
    
    mapid = g_CachedGamemapID
    g_CachedGamemapID = -1
    data = mapgamedata.GetData(mapid)
    if not data:
        return None
    
    for dct in data:
        g_MapgameObj[dct['id']] = obj = CreateGood(dct)
        if obj:
            obj.SetData(dct)
            continue
    


def CreateGood(dct):
    
    try:
        if dct['type'] == '\xbd\xb9\xbd\xba':
            return CButterFlyObjcet(dct['shape'], dct['X'], dct['Y'], dct['direction'])
    except:
        return None



class CMapGameObjcet(object):
    
    def SetData(self, data):
        self.m_Data = data

    
    def CreateMgcEffect(self):
        if not self.GetShow():
            return None
        
        mgc = self.m_Data.get('mgc', None)
        if mgc:
            (x, y) = self.GetPos()
            mgc_lst = mgc.split(';')
            import netmap
            import random
            mgcid = random.choice(mgc_lst)
            mgcid = int(mgcid)
            t = self.m_Data.get('time', 0)
            self.Hide(t)
            if mgcid:
                netmap.PlayMagicEffect(map.g_Map, mgcid, x, y)
            
        

    
    def Hide(self, t):
        
        def func(obj, step):
            if step > 0:
                return (step - 1,)
            else:
                obj.SetShow(True)

        if getattr(self, 'm_HideCmd', None):
            self.m_HideCmd.Release()
            self.m_HideCmd = None
        
        if t:
            self.SetShow(False)
            self.m_HideCmd = self.CreatePyCommand(1, func, t)
        else:
            self.SetShow(True)



class CButterFlyObjcet(interface.CMapWalkerObject, world.CObject, CMapGameObjcet):
    
    class CClickBox(interface.CClickBox):
        
        def Enter(self):
            if getattr(self, 'm_ParentNotify'):
                par = self.GetParent()
                if hasattr(par, 'OnBoxEnter'):
                    par.OnBoxEnter(self)
                
            

        
        def Leave(self):
            if getattr(self, 'm_ParentNotify'):
                par = self.GetParent()
                if hasattr(par, 'OnBoxLeave'):
                    par.OnBoxLeave(self)
                
            


    
    def __init__(self, shape, x, y, direction):
        interface.CMapWalkerObject.__init__(self, map.g_Map)
        self.m_Shape = shape
        self.m_Path = 'res/mapgame/%.4d.spr' % shape
        self.Load(self.m_Path, 'magic')
        (x, y) = map.g_Map.ServerPos2ClientPos(x, y)
        self.SetPos(x, y)
        self.m_AniHandle = self.CreateCommand(0, 'animation')
        self.m_Time = 0
        (rw, rh) = self.GetResKey()
        (w, h) = self.GetResSize()
        self.m_Box = box = CButterFlyObjcet.CClickBox(self, w, h, color = 16711680, alpha = 0)
        box.SetPos(-rw, -rh)
        box.m_ParentNotify = True
        x -= rw
        y -= rh
        import hero
        if not hero.g_Hero:
            return None
        
        
        def _check(obj):
            (hx, hy) = hero.g_Hero.GetPos()
            cx = None if hx - x > 0 else x - hx
            cy = None if hy - y > 0 else y - hy
            if cx < 150 and cy < 150 and obj.CheckMgcEffectTime():
                obj.CreateMgcEffect()
            
            return ()

        self.m_FlyCommand = self.CreatePyCommand(10, _check)
        self.SetDirection(direction)

    
    def CSetDirection(self, d):
        pass

    
    def OnBoxEnter(self, par):
        self.Enter()

    
    def OnBoxLeave(self, par):
        self.Leave()

    
    def Leave(self):
        import cursor
        cursor.Load(cursor.NORMAL_CURSOR)

    
    def Enter(self):
        import cursor
        cursor.Load(cursor.TAKE_CURSOR)

    
    def LeftUp(self):
        pass

    
    def RightUp(self):
        import mainmenudefines
        nethuodong.C2SCatchButterFly()
        dct = item.GetItemsByShape(72375)
        if dct:
            for itemobj in dct.values():
                if not getattr(itemobj, 'm_InfoExt', None) or itemobj.m_InfoExt == '\xa4w\xb9L\xb4\xc1':
                    continue
                
                infoLst = itemobj.m_InfoExt.split('\xa1G')
                catchNum = int(infoLst[1])
                if catchNum < 10:
                    obj = mainmenu.GetMainmenuBtn(mainmenudefines.BTN_ITEM)
                    (ex, ey) = obj.GetScreenPos()
                    (w, h) = obj.GetSize()
                    sx = ex - 20
                    sy = ey - 200
                    (rw, rh) = self.GetResKey()
                    sx += rw
                    sy += rh
                    ex = ex + w / 2
                    ey = ey + h / 2 + rh
                    self.Hide(900)
                    self.CreateEffect(sx, sy, ex, ey)
                    return None
                    continue
            
        
        self.CreateMgcEffect()

    
    def CheckMgcEffectTime(self):
        t = C_sys.GetTime()
        if t - self.m_Time < 60000:
            return False
        
        self.m_Time = t
        return True

    
    def CreateEffect(self, sx, sy, ex, ey):
        import math
        import random
        par = interface.MainPanel
        shape2real = {
            10072: 10077,
            10073: 10076 }
        shape = shape2real.get(self.m_Shape, self.m_Shape)
        self.m_Btf = btf = interface.CSpriteObject(par, 'res/mapgame/%.4d.spr' % shape, 'magic')
        btf.CreateCommand(1, 'animation')
        btf.SetPos(sx, sy)
        btf.SetZ(10000)
        n = int(math.sqrt((ex - sx) * (ex - sx) + (ey - sy) * (ey - sy)) / 8)
        xr1 = random.randint(20, 80)
        yr1 = random.randint(20, 80)
        btf.m_PosList = lst = C_sys.GetHermiteCurve(sx, sy, ex, ey, xr1, yr1, xr1 - 100, yr1 - 100, n)
        lst.append((ex, ey))
        lst.reverse()
        
        def MoveEffect(obj, step = 15):
            btfobj = obj.m_Btf
            if btfobj.m_PosList:
                (x, y) = btfobj.m_PosList.pop()
                btfobj.SetPos(x, y)
                return (step,)
            elif step == 15:
                obj.m_Btf.SetShow(False)
                return (step - 1,)
            elif step > 0:
                return (step - 1,)
            else:
                obj.m_Btf = None
                obj.m_MoveCmd = None

        if getattr(self, 'm_MoveCmd', None):
            self.m_MoveCmd.Release()
            self.m_MoveCmd = None
        
        self.m_MoveCmd = self.CreatePyCommand(1, MoveEffect)



def ShowThrowAni(ownerID, x, y, shape, \x82\x80\x8be = 2):
    endPos = map.g_Map.ServerPos2ClientPos(x, y)
    ani = CTrowItem(ownerID, endPos, \x82\x80\x8be, shape, EndThrowAni, ownerID, x, y)
    g_MapEffect.append(ani)


def EndThrowAni(ownerID, x, y):
    import map
    (sx, sy) = map.g_Map.ServerPos2ClientPos(x, y)
    endAniObj = interface.CBaseObject(None)
    endAniObj.m_EndAni = interface.CSpriteObject(map.g_Map, 'res/\xd5\xd9\xbb\xbd\xb3\xe8\xce\xef\xb3\xf6\xb3\xa1\xd1\xcc_0.spr', 'magic')
    endAniObj.m_EndAni.CreateCommand(0, 'one_off_animation')
    endAniObj.m_EndAni.SetPos(sx, sy)
    
    def doEnd(obj, idx):
        idx += 1
        if idx == 1:
            import hero
            if hero.g_ID == ownerID:
                import netcommon
                netcommon.C2SEndThrowAni(x, y)
            
            return (idx,)
        elif idx == 2:
            endAniObj.m_EndAni = None
        

    endAniObj.CreatePyCommand(12, doEnd, 0)


def RemoveFromMapEffect(obj):
    g_MapEffect.remove(obj)


class CTrowItem(interface.CBaseObject, snowgame.CLineBase):
    
    def __init__(self, ownerID, endPos, \x82\x80\x8be, shape, callBack = None, *arg):
        interface.CBaseObject.__init__(self, map.g_Map)
        snowgame.CLineBase.__init__(self, \x82\x80\x8be)
        self.m_OwnerID = ownerID
        self.m_EndPos = endPos
        self.m_CallBack = callBack
        self.m_Arg = arg
        self.CreateItem(shape)
        self.SetZ(10000)
        self.Throw()

    
    def CreateItem(self, shape):
        self.m_ItemObj = item.CreateItem44Image(self, shape)
        (w, h) = self.m_ItemObj.GetResSize()
        self.m_ItemObj.SetPos(-w, h)

    
    def GetPlayerObj(self, pid):
        import world
        player = world.GetObj(pid)
        return player

    
    def GetStartPos(self):
        owner = self.GetPlayerObj(self.m_OwnerID)
        if owner:
            return owner.GetPos()
        
        return (0, 0)

    
    def GetEndPos(self):
        return self.m_EndPos

    
    def Throw(self):
        (bezier, stepAmount) = self.GetRandomLine()
        
        def shoot(obj, stepremain, stepamount):
            if stepremain > stepamount * 2 / 3:
                obj.PlayEmote(obj.GetPlayerObj(obj.m_OwnerID), 'stand')
            
            if stepremain < stepamount:
                curTime = 1 * stepremain / (stepamount - 1)
                (posx, posy) = bezier.GetPos(curTime)
                obj.SetPos(posx, posy)
                return (stepremain + 1, stepamount)
            else:
                obj.EndThrow()
                return None

        self.ReleaseCmd()
        self.ShowAttackEffect()
        self.m_ThrowCmd = self.CreatePyCommand(1, shoot, 0, stepAmount)

    
    def ReleaseCmd(self):
        if getattr(self, 'm_ThrowCmd', None):
            self.m_ThrowCmd.Release()
            self.m_ThrowCmd = None
        

    
    def ShowAttackEffect(self):
        player = self.GetPlayerObj(self.m_OwnerID)
        self.PlayEmote(player, 'attack')

    
    def EndThrow(self):
        if callable(self.m_CallBack):
            self.m_CallBack(*self.m_Arg)
        
        self.ReleaseCmd()
        RemoveFromMapEffect(self)

    STATE2IDX = {
        'clap': 1,
        'cry': 2,
        'dance': 3,
        'hi': 4,
        'love': 5,
        'laugh': 6,
        'sit': 7,
        'walk': 8,
        'attack': 9,
        'hit': 10,
        'magic': 11,
        'guard': 12,
        'die': 13 }
    
    def PlayEmote(self, player, emote):
        if not player:
            return None
        
        if emote == 'stand':
            player.SetEmote(0)
        else:
            emoteIdx = self.STATE2IDX.get(emote, 0)
            player.PlayEmote(emoteIdx)

    
    def GetSecondBezier(self):
        import math
        import map
        import random
        (startx, starty) = self.GetStartPos()
        (endx, endy) = self.GetEndPos()
        endy -= 5 * map.CELLSIZE
        speed = 300
        dx = endx - startx
        dy = endy - starty
        stepAmount = max(1, int(math.sqrt((dx * dx + dy * dy) / speed)))
        if dx == 0:
            midy = starty + dy / 2
            midx = startx + abs(dy)
        else:
            midx = endx - dx / 2
            rand = random.randint(15, 25)
            midy = min(starty, endy) - rand * map.CELLSIZE
        bezier = snowgame.CSecondBezier(snowgame.CPoint(startx, starty), snowgame.CPoint(midx, midy), snowgame.CPoint(endx, endy))
        return (bezier, stepAmount)
