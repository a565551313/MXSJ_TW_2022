# pycdc 交叉复核产物 · script.fls entry 2704
# co_filename(原始)='script/yard/yardmap/view/yardmapanimal.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2704.pyc (Python 2.5)

import chatoutput
import cursor
import interface
import map
import misc
import world
import yardcontext
import yardmapbase
import yardplayfishmgr
import yardmapz
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
    1000: ((77, 676), (76, 797), (73, 905), (247, 611), (260, 770), (281, 905), (428, 559), (464, 721), (491, 892), (589, 382), (783, 484), (996, 518), (1211, 532), (1350, 403), (1341, 62), (1358, 217), (632, 571), (700, 742), (777, 893), (888, 655), (1017, 854), (1139, 706), (1278, 883), (1298, 673)) }
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
AQUATIC_OBJECTID = 29900

def CanPlace(x, y, speobj):
    oMap = map.GetGameMapObject()
    for dx, dy in ((20, 0), (-50, -50), (20, -50), (-50, 0)):
        if not interface.CMapAddonObject.CanPlace(oMap.m_Point, x + dx, y + dy, speobj):
            return False
            continue
    
    return True


def FindSpace(speobj, list):
    import misc
    for i in list:
        (x, y) = list[misc.RandInt(0, len(list) - 1)]
        if CanPlace(x, y, speobj):
            return (x, y)
            continue
    
    for x, y in list:
        if CanPlace(x, y, speobj):
            return (x, y)
            continue
    
    return (x, y)


class CAquatic(interface.CMapWalkerObject, yardmapbase.CYardMapBase, interface.CBase):
    '''
\t\xb7s\xaex\xb0|\xaa\xba\xa4\xf4\xa4\xa4\xb3\xbd\xa4\xa3\xaf\xe0\xa6b\xa8\xab\xc2\xc2\xaex\xb0|\xaa\xba\xc5\xde\xbf\xe8\xa1A\xa6]\xac\xb0\xa4\xf4\xa6\xc0\xacO\xaa\xb1\xaea\xa6\xdb\xa4v\xb3]\xb8m\xa6\xec\xb8m\xaa\xba\xa1A\xb5L\xaak\xa8\xcf\xa5\xce\xc2\xc2\xaa\xa9spe\xb3]\xb8m\xa6\xec\xb8m

\t\xb3\xbd\xb8s\xbb\xdd\xadn\xbf\xef\xbe\xdc\xa9\xd2\xa5H\xb6i\xa6\xe6\xae\xf8\xae\xa7\xb3B\xb2z
\t'''
    
    def __init__(self, oParent, pContext, tFishID, sType, iPosX, iPosY):
        yardmapbase.CYardMapBase.__init__(self, oParent, pContext)
        interface.CMapWalkerObject.__init__(self, oParent)
        self.m_MaskObj = interface.CMapWalkerMaskObject(map.GetMaskPanel(), self)
        self.m_Path = 'furniture\\animal\\%.3d\\' % sType
        self.m_iFishID = tFishID
        self.m_iLandPosX = iPosX
        self.m_iLandPosY = iPosY
        self.m_iMovePosX = iPosX
        self.m_iMovePosY = iPosY
        self.m_oMoveTimerHandler = None
        self.m_Speed = ANI_SPEED_DATA.get(sType, 5)
        (self.m_CircleX, self.m_CircleY) = self.GetContext().GetGridConvertLogic().Server2ClientPos((iPosX, iPosY))
        self.m_CircleX += 40
        self.m_CircleY += 20
        self.CreatePyCommand(5, misc.Functor(self.CheckShowFalseAura))
        self.SetPos(self.m_CircleX, self.m_CircleY)
        self.SetState('stand')
        self.m_AniHandle = self.CreateCommand(0, 'animation')
        self.m_oWalkHandle = None
        self.m_bAlwaysShow = True
        self.Stop()
        self.MessageProcess()

    
    def SetAlwaysShow(self, bShow):
        self.m_bAlwaysShow = bShow

    
    def StopMoveTimerHandler(self):
        if self.m_oWalkHandle:
            self.m_oWalkHandle.Release()
            self.m_oWalkHandle = None
        
        self.Stop()
        if self.m_oMoveTimerHandler:
            self.m_oMoveTimerHandler.Release()
            self.m_oMoveTimerHandler = None
        

    
    def SetSay(self):
        
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

    
    def SetState(self, sState):
        
        try:
            self.Load(self.m_Path + sState + '.spr', 'mapobject')
        except:
            self.Load(self.m_Path + 'stand.spr', 'mapobject')


    
    def CSetDirection(self, d):
        pass

    
    def Stop(self):
        import misc
        self.SetState('stand')
        if self.m_oMoveTimerHandler:
            self.m_oMoveTimerHandler.Release()
        
        (self.m_iMovePosX, self.m_iMovePosY) = yardcontext.GetMapContext().GetGridConvertLogic().Client2ServerPos_Round(self.GetPos())
        self.m_oMoveTimerHandler = self.CreatePyCommand(misc.RandInt(30, 60), misc.Functor(self.Move))

    
    def CheckWater(self):
        tLBPos = (self.m_iMovePosX - 1, self.m_iMovePosY)
        tRTPos = (self.m_iMovePosX + 1, self.m_iMovePosY)
        tLTPos = (self.m_iMovePosX, self.m_iMovePosY - 1)
        tRBPos = (self.m_iMovePosX, self.m_iMovePosY + 1)
        tPosList = [
            tLBPos,
            tRTPos,
            tLTPos,
            tRBPos]
        dLandList = yardcontext.GetMapContext().GetYardDataMgr().m_dLand
        dCanMoveList = []
        for tPos in tPosList:
            if tPos in dLandList:
                if 10015 in dLandList[tPos]:
                    dCanMoveList.append(tPos)
                
            10015 in dLandList[tPos]
        
        return dCanMoveList

    
    def Move(self, *args):
        dLandList = yardcontext.GetMapContext().GetYardDataMgr().m_dLand
        iCurPosX = self.m_iMovePosX
        iCurPosY = self.m_iMovePosY
        if (iCurPosX, iCurPosY) in dLandList:
            if 10015 in dLandList[(iCurPosX, iCurPosY)]:
                dWaterAreaList = self.CheckWater()
                if len(dWaterAreaList) > 0:
                    tRandomPos = dWaterAreaList[misc.RandInt(0, len(dWaterAreaList) - 1)]
                    (x, y) = self.GetContext().GetGridConvertLogic().Server2ClientPos(tRandomPos)
                    x += 40
                    y += 20
                    self.m_iMovePosX = tRandomPos[0]
                    self.m_iMovePosY = tRandomPos[1]
                else:
                    (x, y) = self.GetContext().GetGridConvertLogic().Server2ClientPos((self.m_iMovePosX, self.m_iMovePosY))
                    x += 40 + misc.RandInt(-2, 2)
                    y += 20 + misc.RandInt(-1, 1)
                self.WalkTo(x, y)
                return None
            else:
                LOG_DEBUG('\xb3\xbd\xa4\xa3\xa6b\xa4\xf4\xb8\xcc\xa1A\xa4\xa3\xaf\xe0\xb0\xca')
        else:
            LOG_DEBUG('\xb8\xd3\xa6a\xb9\xcf\xa8S\xa6s\xbc\xc6\xbe\xda\xa1A\xa9\xce\xaa\xcc\xacO\xc0q\xbb{\xaa\xba\xaf\xf3\xa6a')
        if self.m_oMoveTimerHandler:
            self.m_oMoveTimerHandler.Release()
        
        self.m_oMoveTimerHandler = self.CreatePyCommand(misc.RandInt(30, 60), misc.Functor(self.Move))

    
    def CheckWalkTo(self, iCircleX, iCircleY):
        D_SIZE = 2
        oMapObj = yardplayfishmgr.GetYardPlayFishMgr().GetFishCustomMapObject()
        (aK`ifoePosX, iChangePosY) = yardcontext.GetMapContext().GetYardDataMgr().GetAttrByKey('vSize')
        (iNewPosX, iNewPosY) = yardcontext.GetMapContext().GetGridConvertLogic().Client2ServerPos_Round(self.GetPos())
        tPathList = oMapObj.GetPath((iNewPosX - D_SIZE) + aK`ifoePosX, (iNewPosY - D_SIZE) + iChangePosY, (iCircleX - D_SIZE) + aK`ifoePosX, (iCircleY - D_SIZE) + iChangePosY, 1, 1)
        tPathList = [ (x - aK`ifoePosX, y - iChangePosY) for x, y in tPathList ]
        tPathList.insert(0, (iNewPosX, iNewPosY))
        tPathList = [ self.GetContext().GetGridConvertLogic().Server2ClientPos((x, y)) for x, y in tPathList ]
        tPathList = [ (x + 40, y + 20) for x, y in tPathList ]
        tPathList.insert(0, tPathList[0])
        self.m_oMoveTimerHandler = None
        self.SetState('walk')
        self.SetPath(tPathList, 0, self.m_Speed)

    
    def WalkTo(self, newx, newy):
        args = { }
        args['whole_path'] = 0
        args['end_x'] = newx
        args['end_y'] = newy
        args['speed'] = self.m_Speed
        args['linear'] = 1
        self.SetState('walk')
        if self.m_oWalkHandle:
            self.m_oWalkHandle.Release()
        
        self.m_oWalkHandle = self.CreateCommand(0, 'walk', args)

    
    def LeftUp(self):
        import dlgyardplayfishfeedtips
        if not isinstance(self.m_iFishID, tuple):
            return None
        
        dlgyardplayfishfeedtips.CreateYardPlayFishFeedTipsDlg(self.m_iFishID)

    
    def LeftDown(self):
        pass

    
    def CheckShowFalseAura(self, *args):
        '''\xc0\xcb\xacd\xa6\xe6\xa8\xab\xaa\xba\xc1\xf4\xc2\xc3\xb0\xcf\xb0\xec'''
        vWorldPos = self.GetPos()
        pConvertGridLogic = self.GetContext().GetGridConvertLogic()
        (iBlockStartX, iBlockStartY) = pConvertGridLogic.ClientPos2ServerMapPos(vWorldPos)
        pBlockLogic = self.GetContext().GetMapBlockLogic()
        bShow = True
        for iPosX in (-1, 0, 1):
            for iPosY in (-1, 0, 1):
                if pBlockLogic.IsBrideBlock((iBlockStartX + iPosX, iBlockStartY + iPosY)):
                    bShow = False
                    break
                    continue
            
        
        if self.m_bAlwaysShow:
            pass
        self.SetShow(bShow)
        return ()



class CNideAni(interface.CMapWalkerObject):
    
    def __init__(self, parent, shape):
        interface.CMapWalkerObject.__init__(self, parent)
        self.m_Path = 'furniture/animal/%.5d/stand.spr' % shape
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



class CShowObject(world.CObject, interface.CMapAddonObject, yardmapbase.CYardMapBase):
    
    def __init__(self, parent, pContext, x, y, idx, shape, direction):
        yardmapbase.CYardMapBase.__init__(self, parent, pContext)
        blk = True
        
        try:
            filename = self.GetFurnitureName(shape, direction)
            interface.CMapAddonObject.__init__(self, parent, blk, filename, 'mapobject')
        except SystemError:
            filename = self.GetFurnitureName(shape, 0)
            interface.CMapAddonObject.__init__(self, parent, blk, filename, 'mapobject')

        pMap = self.GetMap()
        self.m_FName = filename
        self.m_Idx = idx
        self.Place(x, y, pMap.GetRoom().GetSpaceObject(shape)[0])

    
    def GetFileName(self):
        return self.m_FName

    
    def GetFurnitureName(self, shape, direction):
        name = 'furniture/%.5d%s' % (shape, chr(ord('a') + direction))
        return name



class CNide(CShowObject):
    
    def __init__(self, parent, pContext, x, y, idx, shape, direction):
        CShowObject.__init__(self, parent, pContext, x, y, idx, shape, direction)
        self.m_oAnimal = CNideAni(self, shape)
        nZ = yardmapz.GetNormalFurnitureZ(x, y)
        self.SetZ(nZ)

    
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
        self.m_oAnimal.SetShow(isShow)



class CAnimal(interface.CMapWalkerObject, world.CObject, yardmapbase.CYardMapBase):
    
    def __init__(self, parent, pContext, idx, type, flag):
        import chardefine
        yardmapbase.CYardMapBase.__init__(self, parent, pContext)
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

        if flag:
            import hero
            (x, y) = hero.g_Hero.GetPos()
        else:
            (x, y) = self.CalAnimalBrithPlace()
        self.m_CircleX = x
        self.m_CircleY = y
        self.SetPos(x, y)
        self.m_AniHandle = self.CreateCommand(0, 'animation')
        self.m_Type = 0
        if type in (31, 32):
            self.m_Type = 1
        
        self.CreatePyCommand(40, misc.Functor(self.WalkTimer))

    
    def CalAnimalBrithPlace(self):
        '''\xadp\xba\xe2\xb0\xca\xaa\xab\xaa\xba \xa5X\xa5\xcd\xa6\xec\xb8m
\t\t:return:
\t\t'''
        import yards2ctools
        import newfurnituredata
        pGridConvertLogic = self.GetContext().GetGridConvertLogic()
        pYardDataMgr = self.GetYardDataMgr()
        dHouseInfo = pYardDataMgr.GetHouseInfo()
        nHouseID = dHouseInfo['shapeID']
        vPos = dHouseInfo['vpos']
        dBrithPlace = newfurnituredata.GetAnimalZoomByHouseID(nHouseID)
        tCenter = dBrithPlace.get('center', (0, 0, 2))
        (iOffX, iOffY, iR) = tCenter
        iRange = yards2ctools.GetBaseID(iR)
        vWorldPos = pGridConvertLogic.ServerMapPos2WorldPos(vPos)
        vWorldPos = (vWorldPos[0] + iOffX * 20, vWorldPos[1] - iOffY * 20)
        iRand = misc.RandInt(0, iRange)
        vDest = None
        (oSpaceObj, _) = self.GetMap().GetRoom().GetSpaceObject(0)
        for i in xrange(iRand):
            (x, y) = yards2ctools.ID2Pos(iRand)
            x = vWorldPos[0] + x * 20
            y = vWorldPos[0] + y * 20
            if CanPlace(x, y, oSpaceObj):
                vDest = (x, y)
                break
                continue
        
        if not vDest:
            vDest = (vWorldPos[0] + 200, vWorldPos[1])
        
        return vDest

    
    def WalkTimer(self, *args):
        import hero
        dx = misc.RandInt(-80, 80)
        dy = misc.RandInt(-80, 80)
        (mx, my) = self.GetPos()
        if self.m_Type == 1:
            if not None(None, *hero.GetHeroObject):
                return ()
            
            (x, y) = hero.GetHeroObject().GetPos()
            if abs(mx - x) > 81 and abs(my - y) > 81 or misc.RandInt(0, 3) == 0:
                self.WalkTo(x + dx, y + dy)
            
        elif misc.RandInt(0, 2) == 0:
            self.WalkTo(mx + dx, my + dy)
        
        return ()

    
    def SetFrame(self):
        pass

    
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
        pMap = self.GetMap()
        if self.m_Type != 1:
            (speobj, ml) = pMap.GetRoom().GetSpaceObject(0)
            if not CanPlace(x, y, speobj):
                return None
            
        
        args = { }
        args['whole_path'] = 0
        args['end_x'] = x
        args['end_y'] = y
        args['speed'] = self.m_Speed
        self.SetState('walk')
        self.CreateCommand(0, 'walk', args)



class CAnimalOP(CShowObject):
    
    def __init__(self, parent, pContext, x, y, idx, direction):
        CShowObject.__init__(self, parent, pContext, x, y, idx, 29999, direction)
        self.m_X = x
        self.m_Y = y
        self.m_ID = 29999
        self.m_Direction = direction
        self.m_Idx = 0
        self.MessageProcess()

    
    def Enter(self):
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
