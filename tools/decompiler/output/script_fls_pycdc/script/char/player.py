# pycdc 交叉复核产物 · script.fls entry 1208
# co_filename(原始)='script/char/player.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1208.pyc (Python 2.5)

import chardefine
import charpartdata
import charpath
import descinterface
import horsecolorchangedata
import interface
import misc
import ridedefine
import specialnpcdata
import walker
import walkerchpcache
MULTIHORSE_POS_0 = 0
MULTIHORSE_POS_1 = 1
MULTIHORSE_POS_2 = 2
MULTIHORSE_POS_3 = 3
MULTIHORSE_POS_4 = 4
VIRTUALSCENEIDLST = (9382,)
OFFSET_Y = 10
g_PlayerCB = { }

def ModuleReset():
    global g_PlayerCB
    g_PlayerCB = { }
    CPlayerBase.ResetClear()


def AddPlayerCB(sCBName, oCB):
    g_PlayerCB[sCBName] = oCB


def DelPlayerCB(sCBName):
    if sCBName in g_PlayerCB:
        del g_PlayerCB[sCBName]
    


def CanCallCB(sName, oObj, *args):
    '''\xb0\xf5\xa6\xe6\xa8\xe7\xbc\xc6\xb9_\xa4l\xa1A\xa6\xb3\xb9_\xa4l\xa8\xc3\xa5B\xaa\xf0\xa6^\xac\xb0\xafu\xad\xc8\xae\xc9\xa1A\xbaI\xc2_\xad\xec\xa8\xe7\xbc\xc6\xb0\xf5\xa6\xe6'''
    if sName in g_PlayerCB and callable(g_PlayerCB[sName]):
        
        try:
            return g_PlayerCB[sName](oObj, *args)
        LOG_EXC()
        return False

    
    return False


def SetPlayerShow():
    import world
    for ob in world.g_Objects.values():
        if isinstance(ob, CPlayer):
            ob.CheckShow()
            continue
    


class CPlayerBase(object):
    s_PlayerNum = 0
    s_CheckTime = -1
    
    def ResetClear(cls):
        cls.s_PlayerNum = 0
        cls.s_CheckTime = -1

    ResetClear = classmethod(ResetClear)
    
    def ShowTips(self):
        import hero
        if hero.GetProp('m_Grade', 0) <= 30:
            CPlayerBase.s_PlayerNum += 1
            import main
            import C_sys
            import chatoutput
            import juben
            t = C_sys.GetTime()
            if CPlayerBase.s_CheckTime == 0 or CPlayerBase.s_CheckTime > t:
                CPlayerBase.s_CheckTime = t
                return None
            
            if (CPlayerBase.s_CheckTime == -1 or t >= 18000000 + CPlayerBase.s_CheckTime) and hero.g_Prop.m_Grade <= 30 and CPlayerBase.s_PlayerNum >= 50:
                if not main.g_TickF9 and main.g_TickF10:
                    pass
            None if not (main.g_TickF11) and not juben.IsPlayJuben() else not juben.IsPlayJuben()
        

    
    def __del__(self):
        if CPlayerBase:
            CPlayerBase.s_PlayerNum -= 1
        

    
    def RightDown(self):
        import misc
        import mainmenu
        import world
        import map
        tm = misc.Time()
        if hasattr(self, 'm_prevclick') and tm < self.m_prevclick + 1:
            return None
        
        self.m_prevclick = tm
        minimapid = map.GetCurrentMiniMapID()
        if minimapid in VIRTUALSCENEIDLST:
            return None
        
        scenename = map.GetCurrentSceneName()
        if scenename in map.g_VirtualSceneNamelst:
            return None
        
        if self.UseSnow(tm):
            return None
        
        mainmenu.SetTarget(self)
        if not world.OnMessageProcess():
            import netplayer
            import popmenu
            popmenu.SetPlayerLook(popmenu.POPMENU_TYPE_NORMAO)
            netplayer.C2SPlayerLook(self.m_ID)
        

    
    def UseSnow(self, tm):
        import snowgame
        return snowgame.CAttackerMgr.FightBack(self.m_ID, tm)

    
    def ShowTeamNum(self):
        import world
        import map
        if getattr(self, 'm_Rider', None) and hasattr(self.m_Rider, 'ShowTeamNum'):
            self.m_Rider.ShowTeamNum()
            return None
        
        iShowType = 0
        if world.IsShowLeaderOnly():
            iShowType = 1
        
        if not iShowType and map.CheckCanShowTeamSize():
            iShowType = 2
        
        self.m_TeamNumTxt = None
        self.m_TeamNumTxtBg = None
        iTeamMax = 5
        if misc.IsNationFightServer():
            iTeamMax = 3
        
        if hasattr(self, 'm_Addons') and hasattr(self, 'm_TeamSize') and iShowType:
            import addon
            if addon.LEADER_KEY in self.m_Addons:
                leaderAddon = self.m_Addons[addon.LEADER_KEY]
            elif addon.CHRISTMASLEADER_KEY in self.m_Addons:
                leaderAddon = self.m_Addons[addon.CHRISTMASLEADER_KEY]
            else:
                return None
            iShowNum = self.m_TeamSize
            if iShowType == 2 and hasattr(self, 'm_iLeaveTeamSize'):
                iShowNum -= self.m_iLeaveTeamSize
            
            if iShowNum == 5:
                iColor = 15790320
            else:
                iColor = 456965
            self.m_TeamNumTxt = interface.CTextObject(leaderAddon, '%d/%d' % (iShowNum, iTeamMax), interface.FontLT16_1, iColor, 0)
            self.m_TeamNumTxt.SetPos(-10, -3)
            self.m_TeamNumTxtBg = interface.CBoxObject(self.m_TeamNumTxt, 40, 26, 0, 143)
            self.m_TeamNumTxtBg.SetZ(-1)
            self.m_TeamNumTxtBg.SetPos(-6, -6)
        



class CPlayer(walker.CWalker, CPlayerBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, realShape = None, iIsUseNewRes = None):
        walker.CWalker.__init__(self, parent, iObjID, iCharIdx, desc, realShape = realShape, iIsUseNewRes = iIsUseNewRes)
        self.ShowTips()
        if self.IsLoadMark():
            
            try:
                raise ZeroDivisionError
            LOG_EXC(iObjID, iCharIdx, desc)

        

    
    def GetLoadType(self):
        return 2

    
    def CheckShow(self):
        walker.CWalker.CheckShow(self)
        self.CheckShowNPCAround()

    
    def SetState(self, state, ani = True):
        sCurState = self.m_State
        walker.CWalker.SetState(self, state, ani)
        self.CheckShowNPCAround()
        if state != 'sit' and sCurState == 'sit':
            import hero
            import yardsignal
            if hero.GetHeroID() == self.GetID():
                yardsignal.Emit(yardsignal.SS_YARD_RESET_SITSTATE)
            
        

    
    def CheckShowNPCAround(self):
        import npc
        import world
        import goods
        import nettask
        if self.IsCheckAroud():
            if world.g_HidePlayer & world.MASK_NPCAROUND:
                (x, y) = self.GetPos()
                aroundNpc = npc.GetAroundNpc(x, y)
                if aroundNpc:
                    self.SetShow(False)
                    for fairy in self.m_Fairy.values():
                        fairy.SetShow(False)
                    
                elif not self.GetShow():
                    walker.CWalker.CheckShow(self)
                
            else:
                dRetList = specialnpcdata.GetHideRange(nettask.g_TaskInfo)
                if not dRetList:
                    return None
                
                (x, y) = self.GetPos()
                for obj in world.g_Objects.values():
                    if isinstance(obj, (npc.CNpc, goods.CGoodsBase)) and obj.GetShow():
                        sName = obj.GetName()
                        for dRet in dRetList:
                            if sName in dRet['tNpcName']:
                                (objX, objY) = obj.GetPos()
                                iDist = dRet['range']
                                if x < x:
                                    pass
                                elif x < objX + iDist:
                                    if y < y:
                                        pass
                                    elif y < objY + iDist + 30:
                                        self.SetShow(False)
                                        for fairy in self.m_Fairy.values():
                                            fairy.SetShow(False)
                                        
                                        return None
                                    
                                y < objY + iDist + 30
                                continue
                            objY - iDist
                        
                
                if not self.GetShow():
                    walker.CWalker.CheckShow(self)
                
        

    
    def GetShowWingDesc(self):
        return descinterface.ChangeWalkerWingInfo(self.GetTempObject().GetNeedDesc(), True)

    
    def IsCheckAroud(self):
        import map
        return map.GetCurrentSceneName() != '\xc6Z\xaf\xee\xa4\xdb\xb9\xd2'

    
    def ChangeShape(self, shape, desc):
        walker.CWalker.ChangeShape(self, shape, desc)
        self.CheckShow()

    
    def SetShow(self, iFlag):
        walker.CWalker.SetShow(self, iFlag)
        if getattr(self, 'm_Wing', None):
            self.m_Wing.SetShow(iFlag)
        
        if getattr(self, 'm_Rider', None):
            self.m_Rider.SetShow(iFlag)
        

    
    def SetName(self, realName, id, country, color, top = False, font = None, iSiblingType = 0, dExtend = None):
        import friend
        if font == None:
            font = interface.FontLT16_2
        
        name = friend.GetShowName(id, realName)
        walker.CWalker.SetName(self, name, id, country, color, top, font, iSiblingType, dExtend)
        if dExtend:
            dExtend = misc.DeepCopy(dExtend)
        
        self.m_NameAttr = (realName, id, country, color, top, font, iSiblingType, dExtend)
        self.m_PropName = realName

    
    def RightDown(self):
        if CanCallCB('CPlayer.RightDown', self):
            return None
        
        walker.CWalker.RightDown(self)
        CPlayerBase.RightDown(self)

    
    def Enter(self):
        if CanCallCB('CPlayer.Enter', self):
            return None
        
        walker.CWalker.Enter(self)

    
    def Leave(self):
        if CanCallCB('CPlayer.Leave', self):
            return None
        
        walker.CWalker.Leave(self)



class CYardPlayer(CPlayer):
    '''
\t\xaex\xb0|\xb1M\xa5\xceplayer
\t'''
    
    def __init__(self, *args, **kwargs):
        import herochengshowmgr
        import herochangeshowdefine
        CPlayer.__init__(self, *args, **kwargs)
        herochengshowmgr.GetHeroChangeShow().SetPlayerShow(self.GetID(), True, herochangeshowdefine.TYPE_REASON_OTHER)

    
    def SetState(self, state, ani = True):
        import yardcontext
        if yardcontext.IsPlayerInHotSpring(self.m_ID):
            oMapContext = yardcontext.GetMapContext()
            if oMapContext:
                dInfo = oMapContext.GetYardDataMgr().GetSitInfoByPlayerID(self.m_ID)
                if dInfo and dInfo['shapeID'] == 29314:
                    self.m_emote = 0
                    state = 'stand'
                    ani = True
                    return CPlayer.SetState(self, state, ani)
                
            
            state = 'sit'
            self.m_emote = 7
            ani = True
            self.ReleaseAnimation()
            self.SetDesc(self.GetOrigDesc())
        
        CPlayer.SetState(self, state, ani)

    
    def SetDesc(self, dDesc):
        import chardefine
        import yardcontext
        if yardcontext.IsPlayerInHotSpring(self.m_ID):
            dDesc = misc.DeepCopy(dDesc)
            for sKey in (chardefine.DESC.KEY_HORSE, chardefine.DESC.KEY_FAIRY, chardefine.DESC.KEY_TRACK, chardefine.DESC.KEY_AURA):
                if sKey in dDesc:
                    del dDesc[sKey]
                    continue
            
            dDesc[chardefine.DESC.WING] = [
                0,
                0]
            oMapContext = yardcontext.GetMapContext()
            if oMapContext:
                dInfo = oMapContext.GetYardDataMgr().GetSitInfoByPlayerID(self.m_ID)
                if dInfo and dInfo['shapeID'] == 29314:
                    dDesc[chardefine.DESC.KEY_HORSE] = [
                        100,
                        0,
                        0,
                        0,
                        0,
                        0]
                
            
            self.InitIsUseNewRes(self.m_bSetIsUseNewRes, self.GetShape(), dDesc)
        
        CPlayer.SetDesc(self, dDesc)

    
    def SetServerPos(self, x, y):
        import yardcontext
        import map
        if yardcontext.IsPlayerInHotSpring(self.GetID()):
            (tSitPos, _) = yardcontext.GetPlayerYardHotSpringPos(self.GetID())
            (x, y) = map.GetGameMapObject().ClientPos2ServerPos(*tSitPos)
        elif hasattr(self, 'm_Team'):
            iLeader = self.m_Team[0]
            if yardcontext.IsPlayerInHotSpring(iLeader) and not yardcontext.IsPlayerInHotSpring(self.GetID()):
                (_, tOutPos) = yardcontext.GetPlayerYardHotSpringPos(iLeader)
                (x, y) = map.GetGameMapObject().ClientPos2ServerPos(*tOutPos)
            elif yardcontext.IsPlayerInHotSpring(self.GetID()):
                (tSitPos, _) = yardcontext.GetPlayerYardHotSpringPos(self.GetID())
                (x, y) = map.GetGameMapObject().ClientPos2ServerPos(*tSitPos)
            
        
        CPlayer.SetServerPos(self, x, y)

    
    def SetPos(self, x, y):
        import yardcontext
        import yardviewsignal
        if yardcontext.IsPlayerInHotSpring(self.GetID()):
            (tSitPos, _) = yardcontext.GetPlayerYardHotSpringPos(self.GetID())
            (x, y) = tSitPos
        elif hasattr(self, 'm_Team'):
            iLeader = self.m_Team[0]
            if yardcontext.IsPlayerInHotSpring(iLeader) and not yardcontext.IsPlayerInHotSpring(self.GetID()):
                (_, tOutPos) = yardcontext.GetPlayerYardHotSpringPos(iLeader)
                (x, y) = tOutPos
            elif yardcontext.IsPlayerInHotSpring(self.GetID()):
                (tSitPos, _) = yardcontext.GetPlayerYardHotSpringPos(self.GetID())
                (x, y) = tSitPos
            
        
        CPlayer.SetPos(self, x, y)
        yardviewsignal.Emit(yardviewsignal.SS_PlayerChangePos, self.GetID())

    
    def SetDirection(self, iDirection):
        import yardcontext
        if yardcontext.IsPlayerInHotSpring(self.m_ID):
            iDirection = 0
            oMapContext = yardcontext.GetMapContext()
            if oMapContext:
                dInfo = oMapContext.GetYardDataMgr().GetSitInfoByPlayerID(self.m_ID)
                if dInfo and dInfo['shapeID'] == 29314:
                    iDirection = dInfo['direct'] * 8
                
            
        
        CPlayer.SetDirection(self, iDirection)

    
    def SetRealShow(self, bShow):
        CPlayer.SetShow(self, bShow)

    
    def SetShow(self, iFlag):
        import herochengshowmgr
        import herochangeshowdefine
        herochengshowmgr.GetHeroChangeShow().SetPlayerShow(self.GetID(), iFlag, herochangeshowdefine.TYPE_REASON_OTHER)

    
    def ChangeShape(self, iShapeID, dDesc):
        import yardcontext
        bLock = yardcontext.IsPlayerInHotSpring(self.GetID())
        if getattr(self, 'm_bLockYard', False):
            bLock = False
        
        if not bLock or not hasattr(self, 'm_CharIdx'):
            CPlayer.ChangeShape(self, iShapeID, dDesc)
        



class CMulitHorseBase(walker.CCustomWalkerBase):
    NormalTurnSpeed = 5
    RunTurnSpeed = 3
    STABLE_DATA = {
        0: {
            0: {
                MULTIHORSE_POS_3: 100,
                MULTIHORSE_POS_4: -100 },
            1: {
                MULTIHORSE_POS_3: -100,
                MULTIHORSE_POS_4: 100 },
            2: {
                MULTIHORSE_POS_3: -100,
                MULTIHORSE_POS_4: 100 },
            3: {
                MULTIHORSE_POS_3: 100,
                MULTIHORSE_POS_4: -100 },
            4: {
                MULTIHORSE_POS_3: 100,
                MULTIHORSE_POS_4: 100 },
            5: {
                MULTIHORSE_POS_3: -100,
                MULTIHORSE_POS_4: 100 },
            6: {
                MULTIHORSE_POS_3: 100,
                MULTIHORSE_POS_4: 100 },
            7: {
                MULTIHORSE_POS_3: 100,
                MULTIHORSE_POS_4: -100 } },
        29: {
            0: {
                MULTIHORSE_POS_3: 180,
                MULTIHORSE_POS_4: 180 },
            1: {
                MULTIHORSE_POS_3: 180,
                MULTIHORSE_POS_4: 180 },
            2: {
                MULTIHORSE_POS_3: 180,
                MULTIHORSE_POS_4: -180 },
            3: {
                MULTIHORSE_POS_3: -180,
                MULTIHORSE_POS_4: 180 },
            4: {
                MULTIHORSE_POS_3: 180,
                MULTIHORSE_POS_4: 180 },
            5: {
                MULTIHORSE_POS_3: 180,
                MULTIHORSE_POS_4: -180 },
            6: {
                MULTIHORSE_POS_3: -180,
                MULTIHORSE_POS_4: -180 },
            7: {
                MULTIHORSE_POS_3: -180,
                MULTIHORSE_POS_4: 180 } } }
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType = None, inmap = True, empty = False, chpType = None, realShape = None):
        self.m_ID = iObjID
        self.m_Empty = empty
        self.m_PosType = posType
        self.m_ChpType = chpType
        self.m_MultiHorseID = multiHorseID
        self.m_DragonCount = (0, 0)
        self.m_CharIdx = iCharIdx
        self.m_bSubHorsePlayer = False
        self.m_oRiderPath = charpath.CRiderPath()
        self.m_ChpData = []
        if realShape is None:
            self.m_RealShape = iCharIdx
        else:
            self.m_RealShape = realShape
        iIsUseNewRes = self.GetParent().GetIsRealUseNewRes(iCharIdx)
        walker.CCustomWalkerBase.__init__(self, iObjID, iCharIdx, desc, inmap = inmap, realShape = realShape, iIsUseNewRes = iIsUseNewRes)
        self.LoadChpData()
        self.SetOffset()

    
    def IsMultiHorsePlayer(self):
        return True

    
    def GetAddonH(self):
        return 140

    
    def CheckShow(self):
        import hero
        if self.GetID() == hero.g_ID:
            return None
        
        par = self.GetParent()
        if par and hasattr(par, 'CheckShow') and not getattr(self, 'm_Itering', False):
            self.m_Itering = True
            par.CheckShow()
            self.SetShow(par.GetShow())
            self.m_Itering = False
        

    
    def GetID(self):
        if self.m_ID:
            return self.m_ID
        
        par = self.GetParent()
        if par:
            return par.m_ID
        
        return 0

    
    def SetEmptyRider(self, empty):
        self.m_Empty = empty
        if not empty:
            self.m_Rider = None
        

    
    def IsEmptyRider(self):
        return self.m_Empty

    
    def IsOwnerRider(self):
        if self.m_ID == 0:
            return True
        

    
    def GetIsUseNewRes(self, iShape = None):
        '''
\t\t\xacO\xa7_\xa8\xcf\xa5\xce\xb7s\xb8\xea\xb7\xbd
\t\t'''
        if self.IsOnFiveHorseSingleRide():
            return walker.CCustomWalkerBase.GetIsUseNewRes(self, iShape)
        else:
            oParent = self.GetParent()
            if not oParent:
                return charpath.IsUseNewRes()
            
            return oParent.GetIsUseNewRes()

    
    def GetResPck(self):
        import charpartdata
        import misc
        iShape = self.m_CharIdx
        if charpartdata.GetIsOnlyNewNpc(iShape) or iShape in (113, 233):
            return chardefine.PCK_NEW_CHAR
        
        if misc.IsHasOldChar():
            if iShape in charpartdata.GetNpcData() or iShape < 1000:
                if self.GetIsUseNewRes():
                    return chardefine.PCK_NEW_CHAR
                else:
                    return chardefine.PCK_OLD_CHAR
            else:
                return chardefine.PCK_NEW_CHAR
        else:
            return chardefine.PCK_NEW_CHAR

    
    def GetResPath(self, iCharIdx, state, hero = False):
        if not self.IsOnFiveHorseSingleRide():
            if self.GetIsUseNewRes(self.m_RealShape):
                self.GetPartObject().ClearPart()
                (lAddWeaponPathList, lAddWeaponProPathList) = self.AddWeaponPalReplenish()
                (_, sRealFileName, lWeaponPathList, lWeaponProPathList) = self.m_oRiderPath.GetRiderPath()
                lWeaponPathList = lAddWeaponPathList + lWeaponPathList
                lWeaponProPathList = lAddWeaponProPathList + lWeaponProPathList
                for sPartPath, iPart in enumerate(lWeaponProPathList):
                    self.GetPartObject().AddPalPartList(iPart, sPartPath, lWeaponProPathList[iPos][0])
                
                return (sRealFileName, lWeaponPathList)
            else:
                filename = 'hero/%.4d' % (self.m_RealShape + 500)
                return (filename, [])
        else:
            return walker.CCustomWalkerBase.GetResPath(self, iCharIdx, state, hero)

    
    def AddWeaponPalReplenish(self):
        if self.m_WeaponIdx and self.m_WeaponKind:
            return ([
                [
                    '0000',
                    1]], [
                [
                    'pal.pro',
                    1]])
        
        return ([], [])

    
    def SetShadow(self, bSet):
        pass

    
    def GetHorseDesc(self):
        parObj = self.GetParent()
        if not IsOnSingleHorse(self.m_MultiHorseID, self.m_PosType):
            return [
                0,
                0,
                0]
        
        if self.m_MultiHorseID == ridedefine.HORSE_9:
            if hasattr(parObj, 'm_HorseInfo') and parObj.m_HorseInfo and len(parObj.m_HorseInfo) >= 6:
                iPalIndex = parObj.m_HorseInfo[3]
                iMainPalList = horsecolorchangedata.GetOldMainPartColor(ridedefine.HORSE_9, iPalIndex)
                iFirstPalList = horsecolorchangedata.GetOldFirstPartColor(ridedefine.HORSE_9, iPalIndex)
                return [
                    ridedefine.HORSE_15,
                    1,
                    0,
                    iMainPalList[0],
                    iFirstPalList[2],
                    0]
            
            return [
                ridedefine.HORSE_15,
                1,
                0]
        elif self.m_MultiHorseID == ridedefine.HORSE_10:
            if hasattr(parObj, 'm_HorseInfo') and parObj.m_HorseInfo and len(parObj.m_HorseInfo) >= 6:
                iPalIndex = parObj.m_HorseInfo[3]
                iFirstPalList = horsecolorchangedata.GetOldFirstPartColor(ridedefine.HORSE_10, iPalIndex)
                return [
                    ridedefine.HORSE_16,
                    1,
                    0,
                    iPalIndex,
                    iFirstPalList[2],
                    0]
            
            return [
                ridedefine.HORSE_16,
                1,
                0]
        elif self.m_MultiHorseID == ridedefine.HORSE_29:
            if hasattr(parObj, 'm_HorseInfo') and parObj.m_HorseInfo and len(parObj.m_HorseInfo) >= 6:
                return [
                    ridedefine.HORSE_30,
                    parObj.m_HorseInfo[1],
                    parObj.m_HorseInfo[2],
                    parObj.m_HorseInfo[3],
                    parObj.m_HorseInfo[4],
                    parObj.m_HorseInfo[5]]
            
            return [
                ridedefine.HORSE_30,
                0,
                0]
        
        return [
            0,
            0,
            0]

    
    def RefreshRider(self, state = 'stand'):
        if self.IsEmptyRider():
            self.m_Rider = None
            return None
        
        self.SetNormalRider(state)

    
    def RefreshHorseDesc(self):
        if not hasattr(self, 'm_HorseDesc'):
            return None
        
        if self.m_HorseDesc != self.GetHorseDesc():
            self.RefreshShape()
        

    
    def RefreshShape(self):
        self.m_Rider = None
        self.ReleaseMoveTimer()
        self.LoadChpData()
        self.SetOffset()
        self.ChangeShape(self.m_CharIdx, self.GetDesc())

    
    def GetDesc(self):
        if hasattr(self, 'm_OriDesc'):
            desc = self.m_OriDesc
        else:
            desc = self.m_CharDesc
        return desc

    
    def SetOriDesc(self, desc):
        import copy
        self.m_OriDesc = copy.deepcopy(desc)

    
    def CheckIsUseNewRes(self, iShape, dDesc):
        if self.GetParent():
            iIsUseNewRes = self.GetParent().GetIsRealUseNewRes(iShape)
            self.SetIsUseNewRes(iIsUseNewRes)
        

    
    def ChangeShape(self, shape, desc):
        if not desc:
            desc = {
                'color': [
                    0,
                    0,
                    0],
                'horse': [
                    0,
                    0,
                    0],
                'titleFlash': 0,
                'weapon': [
                    0,
                    0,
                    0],
                'wing': [
                    0,
                    0],
                'Realcolor': [
                    0,
                    0,
                    0] }
        else:
            import copy
            desc = copy.deepcopy(desc)
        self.CheckIsUseNewRes(shape, desc)
        horsePosList = self.GetHorsePosList()
        if self.m_MultiHorseID in chardefine.DOUBLE_HORSE_TOG and self.GetID() in horsePosList:
            pos = horsePosList.index(self.GetID())
            if horsePosList[0] and horsePosList[1] and pos == 0:
                desc = descinterface.ClearWing(desc)
                desc = descinterface.ClearBackDecorate(desc)
            
        elif self.m_MultiHorseID not in list(chardefine.DOUBLE_HORSE) + list(chardefine.FIVE_HORSE_WITH_WING):
            desc = descinterface.ClearWing(desc)
            desc = descinterface.ClearBackDecorate(desc)
        
        self.m_HorseDesc = self.GetHorseDesc()
        if self.m_HorseDesc:
            desc['horse'] = self.m_HorseDesc
            if len(self.m_HorseDesc) == 6:
                desc['NewHorseColor'] = self.m_HorseDesc[3:]
                desc['OldHorseColor'] = self.m_HorseDesc[3:]
            
        
        desc['color'] = desc.get('Realcolor', desc.get('color', [
            0,
            0,
            0]))
        if 'track' in desc:
            del desc['track']
        
        if 'fairy' in desc:
            del desc['fairy']
        
        desc['aura'] = [
            0,
            0]
        self.m_WeaponHsvPalInc = None
        self.m_RiderHsvPalInc = None
        if hasattr(self, 'ClearWeaponHsvPalInc'):
            self.ClearWeaponHsvPalInc()
        
        self.ClearPalProject()
        self.ClearWeaponPalProject()
        self.m_oRiderPath.UpdateDesc(shape, desc, self.m_State)
        self.m_CharIdx = shape
        self.SetDesc(desc)
        self.m_ItemImg = []
        if self.m_State:
            state = self.m_State
            self.m_State = None
            self.SetState(state)
        
        self.CheckShow()

    
    def SetMultiHorseID(self, multiHorseID):
        self.m_MultiHorseID = multiHorseID
        self.ResetShape()

    
    def SetPosType(self, posType):
        self.m_PosType = posType

    
    def SetStableZ(self):
        pos = self.GetCurPos()
        if self.m_MultiHorseID in self.STABLE_DATA:
            iHorseID = self.m_MultiHorseID
        else:
            iHorseID = 0
        z = self.STABLE_DATA[iHorseID][self.m_CDirection].get(pos)
        if z:
            self.SetZ(z)
        

    
    def IsStable(self):
        if self.m_PosType not in (MULTIHORSE_POS_3, MULTIHORSE_POS_4):
            return False
        
        if self.IsTurning():
            return False
        
        return True

    
    def WalkTo(self, newx, newy, speed = 20, oldx = 0, oldy = 0, checkobj = None, dist = 0, wholepath = True):
        pass

    
    def IsTurning(self):
        if hasattr(self, 'm_MoveTimer') and self.m_MoveTimer:
            return True
        
        return False

    
    def ReleaseMoveTimer(self):
        self.SetAlpha(255)
        if hasattr(self, 'm_MoveTimer') and self.m_MoveTimer:
            self.m_MoveTimer.Release()
            self.m_MoveTimer = None
        
        self.GetParent().MultiHorseMoveOver(self)

    
    def SetCurAlpha(self):
        import math
        p = self.GetParent()
        (mx, my) = self.GetPos()
        if p.m_Rider:
            (ux, uy) = p.m_Rider.GetPos()
        else:
            (ux, uy) = p.GetPos()
        (kw, kh) = self.GetKey()
        (mw, mh) = self.GetSize()
        x1 = mx - kw
        y1 = my - kh
        x2 = (mx - kw) + mw
        y2 = my - kh
        x3 = (mx - kw) + mw
        y3 = (my - kh) + mh
        x4 = mx - kw
        y4 = (my - kh) + mh
        d1 = (x1 - ux) ** 2 + (y1 - uy) ** 2
        d2 = (x2 - ux) ** 2 + (y2 - uy) ** 2
        d3 = (x3 - ux) ** 2 + (y3 - uy) ** 2
        d4 = (x4 - ux) ** 2 + (y4 - uy) ** 2
        dd = min(d1, d2, d3, d4)
        if dd >= 250:
            self.SetAlpha(255)
        else:
            alp = int((50 - math.sqrt(dd)) * 192 / 50)
            self.SetAlpha(255 - alp)

    
    def IsOnFiveHorseSingleRide(self):
        if self.m_MultiHorseID in chardefine.FIVE_HORSE and self.m_PosType in (MULTIHORSE_POS_3, MULTIHORSE_POS_4):
            return True
        

    
    def RefreshDirction(self):
        import misc
        import wrapmath
        cdct = self.m_CDirection
        if not (self.m_ChpData) or cdct >= len(self.m_ChpData):
            return None
        
        data = self.m_ChpData[cdct]
        self.m_OffsetData = data
        frame = self.GetParent().GetFrame() % 8
        (self.m_AimX, self.m_AimY) = data[frame]
        (nx, ny) = self.GetPos()
        if nx == self.m_AimX and self.m_AimY == ny:
            return None
        
        self.m_AimDirection = self.GetParent().GetDirection()
        if self.IsOnFiveHorseSingleRide():
            self.m_LastParentPos = self.GetParent().GetPos()
            
            def multiDone(obj, tick):
                (x, y) = obj.GetPos()
                (px, py) = obj.GetParent().GetPos()
                rx = px - obj.m_LastParentPos[0]
                ry = py - obj.m_LastParentPos[1]
                obj.m_LastParentPos = (px, py)
                if rx == 0 and ry == 0:
                    speed = obj.NormalTurnSpeed
                else:
                    speed = obj.RunTurnSpeed
                nextPos = wrapmath.CalculatePoint(x, y, obj.m_AimX, obj.m_AimY, speed)
                if not nextPos:
                    obj.SetDirection(obj.m_AimDirection)
                    obj.SetPos(obj.m_AimX, obj.m_AimY)
                    obj.ReleaseMoveTimer()
                    obj.SetStableZ()
                    return None
                
                (nx, ny) = nextPos
                obj.SetPos(nx, ny)
                if tick % 15 == 0:
                    d = misc.CalDirection((nx - x) + rx, (ny - y) + ry)
                    obj.SetDirection(d)
                
                p = obj.GetParent()
                p.RefreshMultiHorsePlayerZ()
                if obj.GetShow():
                    obj.SetCurAlpha()
                else:
                    obj.SetAlpha(255)
                return (tick + 1,)

            self.ReleaseMoveTimer()
            self.GetParent().SetCoverAlpha(128)
            self.m_MoveTimer = self.CreatePyCommand(1, multiDone, 0)
        elif hasattr(self, 'm_ChpData') and self.m_ChpData:
            data = self.m_ChpData[cdct]
            frame = self.GetParent().GetFrame() % len(data)
            pos = data[frame]
            self.SetPos(*pos)
        else:
            self.SetPos(0, 0)

    
    def CSetDirection(self, d):
        if hasattr(self, 'm_LoadFake') and not (self.m_LoadFake):
            self.m_LoadFake = True
            return None
        
        self.m_CDirection = d
        if self.m_Rider:
            direction = self.GetDirection()
            self.m_Rider.SetDirection(direction)
        
        self.SetOffset()
        walker.CCustomWalkerBase.CSetDirection(self, d)

    
    def GetChpType(self):
        if self.m_ChpType:
            return self.m_ChpType
        

    
    def SetChpType(self, chp):
        self.m_ChpType = chp

    
    def GetCurPos(self):
        if self.m_MultiHorseID == 30:
            return 0
        
        if self.m_ChpType:
            pos = self.m_ChpType
        else:
            pos = self.m_PosType
        return pos

    
    def GetChpPath(self, pos):
        if self.GetIsUseNewRes():
            if not pos:
                pos = 0
            
            return 'horse/%.3d/chp/%.4d/%.4d.chp' % (self.m_MultiHorseID, self.m_RealShape, pos)
        elif pos:
            path = 'hero/horse/%.3d/chp/%.4d/%.4d.chp' % (self.m_MultiHorseID, self.m_RealShape + 500, pos)
        else:
            path = 'hero/horse/%.3d/chp/%.4d/0000.chp' % (self.m_MultiHorseID, self.m_RealShape + 500)
        return path

    
    def GetHorsePosList(self):
        import world
        for _, horsePosList in world.g_TeamHorse.items():
            if self.GetID() in horsePosList:
                return horsePosList
                continue
        
        return []

    
    def GetDataForChpData(self):
        sData = '8 16\n'
        if self.m_MultiHorseID == 16 and self.m_PosType != 0:
            return None
        elif self.m_MultiHorseID == 15 and self.m_PosType != 0:
            return None
        else:
            iHorse = self.m_MultiHorseID
        if iHorse in chardefine.UES_ONLY_POS_HORSE:
            for i in range(1, 9):
                sRFData = charpartdata.HORSE_POS_DATA[iHorse][self.m_PosType + 1][i]
                sMag = '%s, ' % str(sRFData)
                sMag *= 16
                if i != 8:
                    sMag += '\n'
                
                sData += sMag
            
            return walkerchpcache.GetChpDataMgr().FileInfo2ChpData(sData)
        else:
            return None

    
    def GetChpData(self, path):
        if self.GetIsUseNewRes():
            return self.GetDataForChpData()
        else:
            return walkerchpcache.GetChpDataMgr().GetChpData(path, chardefine.PCK_OLD_CHAR)

    
    def LoadChpData(self):
        sKey = self.GetChpDataBufferKey()
        oMgr = walkerchpcache.GetChpDataMgr()
        data = oMgr.GetChpDataByKey(sKey)
        if data:
            self.m_ChpData = data
            return data
        
        self.m_ChpData = self.GetChpData(self.GetChpPath(self.GetCurPos()))
        if self.m_ChpData:
            if self.GetIsUseNewRes():
                oMgr.AddChpDataByKey(sKey, self.m_ChpData)
            
        else:
            self.m_ChpData = None
        return self.m_ChpData

    
    def SetOffset(self):
        if hasattr(self, 'm_CDirection') and self.m_CDirection:
            d = self.m_CDirection
        else:
            d = 0
        if self.m_ChpData:
            data = self.m_ChpData[d]
            self.SetFramesOffset(data)
        

    
    def GetFashionUseShape(self):
        iFashionList = self.m_iFashionList
        if iFashionList and iFashionList[0]:
            iShape = chardefine.FASHION_CHP_CHANGE.get(self.m_RealShape / 100, self.m_RealShape)
        else:
            iShape = self.m_RealShape
        return iShape

    
    def GetChpDataBufferKey(self):
        if self.GetIsUseNewRes():
            sState = getattr(self.GetParent(), 'm_State', chardefine.STATE_STAND)
            sKey = '%s_%s_%s_%s' % (self.GetFashionUseShape(), self.m_MultiHorseID, sState, self.m_PosType)
        else:
            sKey = self.GetChpPath(self.GetCurPos())
        return sKey

    
    def GetTopParent(self):
        import map
        return map.g_Map

    
    def SetDragonglass(self, iNum, iTeamNum = 0):
        self.m_DragonCount = (iNum, iTeamNum)
        if hasattr(self, 'm_NameText'):
            self.m_NameText.SetDragonglass(iNum, iTeamNum)
        

    
    def SetName(self, name, id, country, color, top = False, font = None, iSiblingType = 0, dExtend = None):
        if font == None:
            font = interface.FontLT16_1
        
        if dExtend:
            dExtend = misc.DeepCopy(dExtend)
        
        self.m_NameAttr = (name, id, country, color, top, font, iSiblingType, dExtend)
        parent = self
        if not self.GetParent():
            return None
        
        self.m_NameZ = 0
        if top:
            parent = self.GetTopParent()
        
        
        def CheckMask(obj):
            nt = obj.m_NameText
            (sx, sy) = obj.GetPos()
            (px, py) = obj.GetParent().GetPos()
            x = sx + px
            y = sy + py
            nt.POPMENU_TYPE_NORMAO(y + 200)
            if obj.GetShow() == False:
                nt.POPMENU_TYPE_NORMAO(y)
            
            return ()

        self.m_PropCountry = country
        import friend
        nickName = friend.GetShowName(id, name)
        nameobj = walker.CNameBar(parent, self, nickName, id, iSiblingType, color, font, dExtend)
        if self.m_DragonCount and self.m_DragonCount != (0, 0):
            nameobj.SetDragonglass(*self.m_DragonCount)
        
        (x, y) = (0, 0)
        if top:
            (sx, sy) = (0, 0)
            oParent = self.GetParent()
            (px, py) = oParent.GetPos()
            x = sx + px
            y = sy + py
            oParent.SetBur(nameobj)
        
        (w, h) = nameobj.GetSize()
        nameobj.SetPos(x - w / 2, y + OFFSET_Y)
        nameobj.m_Top = top
        nameobj.SetZ(1)
        self.m_NameText = nameobj
        self.m_PropName = name
        self.m_CheckMaskCmd = self.CreatePyCommand(10, CheckMask)
        if self.m_bSubHorsePlayer:
            self.m_NameText.SetShow(False)
        

    
    def EnterNameAdjust(self):
        if hasattr(self, 'm_NameText') and hasattr(self.m_NameText, 'Active'):
            if self.m_bSubHorsePlayer or self.IsOnFiveHorseSingleRide():
                self.m_NameText.SetShow(True)
                oParent = self.GetParent()
                if oParent and hasattr(oParent, 'm_MultiHorsePlayerList'):
                    oLst = oParent.m_MultiHorsePlayerList
                    for oMultiHorsePlayer in oLst:
                        if oMultiHorsePlayer != self:
                            oMultiHorsePlayer.SetShowName(False)
                            continue
                    
                
            
            self.m_NameText.Active(True)
            if self.m_NameText.m_Top and self.GetParent():
                (sx, sy) = self.GetPos()
                (px, py) = self.GetParent().GetPos()
                x = sx + px
                y = sy + py
                self.m_NameText.SetZ(y + 600)
            
        

    
    def LeaveNameAdjust(self):
        if hasattr(self, 'm_NameText') and hasattr(self.m_NameText, 'Active'):
            self.m_NameText.Active(False)
            if self.m_NameText.m_Top:
                (sx, sy) = self.GetPos()
                
                try:
                    (px, py) = self.GetParent().GetPos()
                except:
                    (px, py) = (0, 0)

                x = sx + px
                y = sy + py
                self.m_NameText.SetZ(y + self.m_NameZ)
            
            if self.m_bSubHorsePlayer or self.IsOnFiveHorseSingleRide():
                self.m_NameText.SetShow(False)
                oParent = self.GetParent()
                if oParent and hasattr(oParent, 'm_MultiHorsePlayerList'):
                    oLst = oParent.m_MultiHorsePlayerList
                    for oMultiHorsePlayer in oLst:
                        iID = oMultiHorsePlayer.m_ID
                        if iID == 0:
                            oMultiHorsePlayer.SetShowName(True)
                            continue
                        oMultiHorsePlayer.SetShowName(False)
                    
                
            
        

    
    def SetSubHorsePlayer(self, bSubHorsePlayer):
        self.m_bSubHorsePlayer = bSubHorsePlayer
        if self.m_bSubHorsePlayer:
            self.SetShowName(False)
        else:
            self.SetShowName(True)

    
    def SetShowName(self, bShowName):
        if hasattr(self, 'm_NameText') and self.m_NameText:
            self.m_NameText.SetShow(bShowName)
        

    
    def Walk(self):
        if self.m_MultiHorseID in chardefine.WALK_ORD_HORSE:
            self.SetState('walk', ani = False)
        elif self.m_MultiHorseID in (29, 30):
            walker.CCustomWalkerBase.Walk(self)
        

    
    def RightUp(self):
        if self.m_ID:
            walker.CCustomWalkerBase.RightUp(self)
        else:
            self.GetParent().RightUp()

    
    def RightDown(self):
        if self.m_ID:
            walker.CCustomWalkerBase.RightDown(self)
        else:
            self.GetParent().RightDown()

    
    def LeftUp(self):
        if self.m_ID:
            walker.CCustomWalkerBase.LeftUp(self)
        else:
            self.GetParent().LeftUp()

    
    def LeftDown(self):
        if self.m_ID:
            walker.CCustomWalkerBase.LeftDown(self)
        else:
            self.GetParent().LeftDown()

    
    def SetAura(self, aura = 0):
        if getattr(self, 'm_Aura', None):
            self.m_Aura = None
        

    
    def DoCreateAura(self, aura = 0):
        if getattr(self, 'm_DelayAura', None):
            self.m_DelayAura = None
        

    
    def ShowTrack(self, track, dist = None):
        if getattr(self, 'm_TrackAni', None):
            self.m_TrackAni = None
        

    
    def DoShowTrack(self, track, dist = None):
        if getattr(self, 'm_TrackAni', None):
            self.m_TrackAni = None
        



class CMapMultiHorsePlayer(walker.CMaskHeroObject, CMulitHorseBase, CPlayerBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType = None, empty = False, chpType = None, realShape = None):
        walker.CMaskHeroObject.__init__(self, parent)
        CMulitHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, empty = empty, chpType = chpType, realShape = realShape)
        self.SetPos(0, 0)

    
    def __del__(self):
        if CPlayerBase:
            CPlayerBase.s_PlayerNum -= 1
        
        import delayctrl
        delayctrl.GetDelayDlgCtrl().DelWalker(self.GetLoadType(), id(self))
        delayctrl.GetDelayOtherCtrl().DelWalker(id(self))

    
    def GetLoadType(self):
        if self.IsOnFiveHorseSingleRide():
            return 2
        else:
            return 3

    
    def Load(self, sPath, sPack, sWeapon = None):
        import delayctrl
        import hero
        self.m_sInPck = sPack
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if not charpath.Exist(sPath, sPack):
                raise SystemError('%s,%s' % (sPath, sPack))
            
            if sPack == 'hero':
                sSpr = '0000/0000.spr'
                sTeamWeapon = [
                    [
                        '0000/001',
                        1]]
            elif sPack == 'newchar':
                sSpr = '0001/0000.spr'
                sTeamWeapon = [
                    [
                        '0001/001',
                        1]]
            else:
                sSpr = sPath
                sTeamWeapon = sWeapon
            if not sWeapon:
                interface.CMapHeroObject.Load(self, sSpr, sPack)
                delayctrl.GetDelayDlgCtrl().AddWalker(self.GetLoadType(), self, sPath, sPack)
            else:
                interface.CMapHeroObject.Load(self, sSpr, sPack, sTeamWeapon)
                delayctrl.GetDelayDlgCtrl().AddWalker(self.GetLoadType(), self, sPath, sPack, sWeapon)
        elif not sWeapon:
            interface.CMapHeroObject.Load(self, sPath, sPack)
        else:
            interface.CMapHeroObject.Load(self, sPath, sPack, sWeapon)

    
    def LoadWeapon(self, lWeaponpath):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            delayctrl.GetDelayDlgCtrl().LoadWeapon(self.GetLoadType(), self, lWeaponpath)
        else:
            interface.CMapHeroObject.LoadWeapon(self, lWeaponpath)

    
    def LoadImagess(self, sPath):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if charpath.Exist(sPath, self.m_sInPck):
                delayctrl.GetDelayDlgCtrl().AddLoadWalkerImagess(self.GetLoadType(), self, sPath)
            else:
                return 1
        else:
            return interface.CMapHeroObject.LoadImagess(self, sPath)

    
    def LoadImages(self, sPath = ''):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if charpath.Exist(sPath, self.m_sInPck):
                delayctrl.GetDelayDlgCtrl().AddLoadWalkerImages(self.GetLoadType(), self, sPath)
            else:
                return 1
        elif sPath:
            return interface.CMapHeroObject.LoadImages(self, sPath)
        else:
            return interface.CMapHeroObject.LoadImages(self)

    
    def RightDown(self):
        CMulitHorseBase.RightDown(self)
        if self.m_ID:
            CPlayerBase.RightDown(self)
        

    
    def SetAlpha(self, alpha):
        walker.CMaskHeroObject.SetAlpha(self, alpha)
        CMulitHorseBase.SetAlpha(self, alpha)

    
    def GetResKey(self):
        (w0, h0) = walker.CMaskHeroObject.GetResKey(self)
        import npcheightdata
        (dw, dh) = npcheightdata.GetFixedData(self.m_RealShape)
        w = w0 + dw
        h = h0 + dh
        return (w, h)

    
    def SetShow(self, bShow):
        if getattr(self, 'm_Wing', None):
            self.m_Wing.SetShow(bShow)
        
        if self.m_Rider:
            self.m_Rider.SetShow(bShow)
        
        walker.CMaskHeroObject.SetShow(self, bShow)

    
    def SetPos(self, x, y):
        walker.CMaskHeroObject.SetPos(self, x, y)
        self.SetMaskZ(y)



class CSecHorseBase(CMulitHorseBase, CPlayerBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType = None, inmap = True, empty = False, chpType = None, realShape = None):
        CMulitHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, inmap = inmap, empty = empty, chpType = chpType, realShape = realShape)

    
    def CheckShow(self):
        walker.CCustomWalkerBase.CheckShow(self)

    
    def IsOwnerRider(self):
        return True

    
    def CheckIsUseNewRes(self, iShape, dDesc):
        if self.GetParent():
            iIsUseNewRes = self.GetParent().GetIsRealUseNewRes(iShape)
            self.SetIsUseNewRes(iIsUseNewRes)
        

    
    def ChangeShape(self, shape, desc):
        import copy
        newDesc = copy.deepcopy(desc)
        parObj = self.GetParent()
        if not parObj:
            return [
                0,
                0,
                0]
        
        if not IsOnSingleHorse(self.m_MultiHorseID, self.m_PosType):
            return [
                0,
                0,
                0]
        
        import copy
        import multihorsemgr
        self.CheckIsUseNewRes(shape, desc)
        if multihorsemgr.HasChangedMainID(parObj.m_ID, self.m_ID):
            origDesc = copy.deepcopy(getattr(self, 'm_OrigDesc', parObj.m_CharDesc))
        else:
            origDesc = copy.deepcopy(getattr(parObj, 'm_OrigDesc', parObj.m_CharDesc))
        if 'horse' in origDesc:
            newDesc['horse'] = origDesc['horse']
        
        if 'OldHorseColor' in origDesc:
            newDesc['OldHorseColor'] = origDesc['OldHorseColor']
        
        if 'NewHorseColor' in origDesc:
            newDesc['NewHorseColor'] = origDesc['NewHorseColor']
        
        walker.CCustomWalkerBase.ChangeShape(self, shape, newDesc)

    
    def GetIsUseNewRes(self, iShape = None):
        '''
\t\t\xc2\xf9\xa4H\xa7\xa4\xc3M \xb4N\xacO\xa6U\xa6\xdb\xa8\xcf\xa5\xce\xa6U\xa6\xdb\xaa\xba
\t\t'''
        return walker.CCustomWalkerBase.GetIsUseNewRes(self, iShape)

    
    def GetResPath(self, iCharIdx, state, hero = False):
        return walker.CCustomWalkerBase.GetResPath(self, iCharIdx, state, hero)

    
    def GetHorseDesc(self):
        parObj = self.GetParent()
        if not parObj:
            return [
                0,
                0,
                0]
        
        if not IsOnSingleHorse(self.m_MultiHorseID, self.m_PosType):
            return [
                0,
                0,
                0]
        
        import copy
        import multihorsemgr
        if multihorsemgr.HasChangedMainID(parObj.m_ID, self.m_ID):
            origDesc = copy.deepcopy(getattr(self, 'm_OrigDesc', parObj.m_CharDesc))
        else:
            origDesc = copy.deepcopy(getattr(parObj, 'm_OrigDesc', parObj.m_CharDesc))
        horseinfo = origDesc.get('horse', [
            0,
            0,
            0])
        return horseinfo

    
    def RefreshRider(self, state = 'stand'):
        walker.CCustomWalkerBase.RefreshRider(self, state)
        nameattr = getattr(self, 'm_NameAttr', None)
        titleattr = getattr(self, 'm_TitleAttr', None)
        if nameattr:
            self.SetName(*nameattr)
        
        if titleattr:
            self.SetTitle(*titleattr)
        



class CMapSecHorsePlayer(CSecHorseBase, walker.CMaskHeroObject, CPlayerBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, ownerID, posType = None, empty = False, chpType = None, realShape = None):
        self.m_HorseOwnerID = ownerID
        (self.m_DesX, self.m_DesY) = (0, 0)
        walker.CMaskHeroObject.__init__(self, parent)
        CSecHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, empty = empty, chpType = chpType, realShape = realShape)
        par = self.GetParent()
        if par:
            (self.m_DesX, self.m_DesY) = par.GetPos()
        
        (ox, oy) = self.GetAimPos()
        self.SetPos(ox, oy)

    
    def __del__(self):
        if CPlayerBase:
            CPlayerBase.s_PlayerNum -= 1
        
        import delayctrl
        delayctrl.GetDelayDlgCtrl().DelWalker(self.GetLoadType(), id(self))
        delayctrl.GetDelayOtherCtrl().DelWalker(id(self))

    
    def GetLoadType(self):
        return 2

    
    def Load(self, sPath, sPack, sWeapon = None):
        import delayctrl
        self.m_sInPck = sPack
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if not charpath.Exist(sPath, sPack):
                raise SystemError('%s,%s' % (sPath, sPack))
            
            if sPack == 'hero':
                sSpr = '0000/0000.spr'
                sTeamWeapon = [
                    [
                        '0000/001',
                        1]]
            elif sPack == 'newchar':
                sSpr = '0001/0000.spr'
                sTeamWeapon = [
                    [
                        '0001/001',
                        1]]
            else:
                sSpr = sPath
                sTeamWeapon = sWeapon
            if not sWeapon:
                interface.CMapHeroObject.Load(self, sSpr, sPack)
                delayctrl.GetDelayDlgCtrl().AddWalker(self.GetLoadType(), self, sPath, sPack)
            else:
                interface.CMapHeroObject.Load(self, sSpr, sPack, sTeamWeapon)
                delayctrl.GetDelayDlgCtrl().AddWalker(self.GetLoadType(), self, sPath, sPack, sWeapon)
        elif not sWeapon:
            interface.CMapHeroObject.Load(self, sPath, sPack)
        else:
            interface.CMapHeroObject.Load(self, sPath, sPack, sWeapon)

    
    def LoadWeapon(self, lWeaponpath):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            delayctrl.GetDelayDlgCtrl().LoadWeapon(self.GetLoadType(), self, lWeaponpath)
        else:
            interface.CMapHeroObject.LoadWeapon(self, lWeaponpath)

    
    def LoadImagess(self, sPath):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if charpath.Exist(sPath, self.m_sInPck):
                delayctrl.GetDelayDlgCtrl().AddLoadWalkerImagess(self.GetLoadType(), self, sPath)
            else:
                return 1
        else:
            return interface.CMapHeroObject.LoadImagess(self, sPath)

    
    def LoadImages(self, sPath = ''):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if charpath.Exist(sPath, self.m_sInPck):
                delayctrl.GetDelayDlgCtrl().AddLoadWalkerImages(self.GetLoadType(), self, sPath)
            else:
                return 1
        elif sPath:
            return interface.CMapHeroObject.LoadImages(self, sPath)
        else:
            return interface.CMapHeroObject.LoadImages(self)

    
    def RightDown(self):
        CSecHorseBase.RightDown(self)
        if self.m_ID:
            CPlayerBase.RightDown(self)
        

    
    def WalkTo(self, newx, newy, speed = 20, oldx = 0, oldy = 0, checkobj = None, dist = 0, wholepath = True):
        self.m_DesX = newx
        self.m_DesY = newy
        self.StartCheckAim()

    DIST = [
        100,
        100,
        100,
        100,
        100,
        140,
        100,
        140]
    DIRECTCOUNT = [
        (1, 1),
        (-1, 1),
        (-1, -1),
        (1, -1),
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 0)]
    DIR2AIMDIR = {
        0: (1, 3),
        1: (2, 0),
        2: (1, 3),
        3: (2, 0),
        4: (5, 7),
        5: (4, 6),
        6: (5, 7),
        7: (4, 6) }
    
    def IsEnableEventPoint(self, x, y):
        import map
        x = x / map.CELLSIZE
        y = y / map.CELLSIZE
        
        try:
            if map.g_Map.GetEventPoint(x, y, 1) <= 0:
                return True
        except:
            return True

        return False

    
    def GetAimPos(self):
        import misc
        import math
        import map
        par = self.GetParent()
        (cx, cy) = self.GetPos()
        mapObj = map.g_Map
        if not par:
            return (cx, cy)
        
        if self.IsEnableEventPoint(self.m_DesX, self.m_DesY):
            px = self.m_DesX
            py = self.m_DesY
        else:
            path = par.GetPath()
            pos = min(len(path) / 2 + len(path) / 3 + len(path) / 4, len(path))
            (px, py) = mapObj.ServerPixelPos2ClientPos(*path[-pos])
            return (px, py)
        direction = misc.CalImagesDirection(par.GetDirection(), 8)
        offset = (0, 0)
        new_direct = []
        minDistance = 9999999
        direct = CMapSecHorsePlayer.DIR2AIMDIR[direction]
        for d in direct:
            new_direct.append(CMapSecHorsePlayer.DIRECTCOUNT[d])
        
        for i, j in enumerate(new_direct):
            current_distance = CMapSecHorsePlayer.DIST[k]
            nx = px + i * current_distance
            ny = py + j * current_distance
            distance = (nx - cx) ** 2 + (ny - cy) ** 2
            offsetX = int(i * current_distance)
            offsetY = int(j * current_distance)
            if distance < minDistance and self.IsEnableEventPoint(px + offsetX, py + offsetY):
                minDistance = distance
                offset = (offsetX, offsetY)
                continue
            None if i and j else None
        
        self.m_Offset = offset
        return (px + offset[0], py + offset[1])

    
    def RefreshDirction(self):
        par = self.GetParent()
        if not par.IsWalk():
            self.StartCheckAim()
        

    
    def StartCheckAim(self):
        (aimX, aimY) = self.GetAimPos()
        walker.CCustomWalkerBase.WalkTo(self, aimX, aimY, 25)
        self.StartWalkToAim()
        import refreshmultihorsepos
        refreshmultihorsepos.CRefreshMultiHorsePos.UpdateMultiHorsePos(self.m_HorseOwnerID)

    
    def StartWalkToAim(self):
        
        def walkAim(obj):
            par = obj.GetParent()
            if obj.IsWalk() or not par:
                return ()
            
            obj.SetDirection(par.GetDirection())
            obj.m_WalkTimer = None

        if not getattr(self, 'm_WalkTimer', None):
            self.m_WalkTimer = self.CreatePyCommand(15, walkAim)
        

    
    def SetName(self, realName, id, country, color, top = False, font = None, iSiblingType = 0, dExtend = None):
        if font == None:
            font = interface.FontLT16_1
        
        import friend
        name = friend.GetShowName(id, realName)
        walker.CCustomWalkerBase.SetName(self, name, id, country, color, top, font, iSiblingType, dExtend)
        if dExtend:
            dExtend = misc.DeepCopy(dExtend)
        
        self.m_NameAttr = (realName, id, country, color, top, font, iSiblingType, dExtend)
        self.m_PropName = realName

    
    def SetDirection(self, d):
        par = self.GetParent()
        if par.IsWalk() or self.IsWalk():
            return None
        
        walker.CMaskHeroObject.SetDirection(self, d)

    
    def IsStable(self):
        if self.m_PosType not in (MULTIHORSE_POS_1,):
            return True
        
        if self.IsTurning():
            return False
        
        return True

    
    def IsTurning(self):
        return self.IsWalk()

    
    def GetParent(self):
        import world
        if world.g_Objects.get(self.m_HorseOwnerID):
            return world.g_Objects[self.m_HorseOwnerID]
        

    
    def SetPos(self, x, y):
        walker.CMaskHeroObject.SetPos(self, x, y)
        self.SetMaskZ(y)



class CSecHorsePlayer(interface.CWalkerObject, CSecHorseBase, CPlayerBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, ownerID, posType = None, empty = False, chpType = None, realShape = None):
        self.m_HorseOwnerID = ownerID
        interface.CWalkerObject.__init__(self, parent)
        CSecHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, False, empty = empty, chpType = chpType, realShape = realShape)
        owner = self.GetParent()
        (x, y) = owner.GetPos()
        self.SetPos(x + 150, y)

    
    def ChangeShape(self, charidx, desc):
        import multihorsemgr
        origDesc = self.GetOrigDesc()
        desc = multihorsemgr.TransformSpeHorse(desc, self.m_PosType)
        walker.CCustomWalkerBase.ChangeShape(self, charidx, desc)

    
    def GetHorseDesc(self):
        import multihorsemgr
        origDesc = self.GetOrigDesc()
        desc = multihorsemgr.TransformSpeHorse(origDesc, self.m_PosType)
        return desc.get('horse', [
            0,
            0,
            0])

    
    def RefreshDirction(self):
        pass

    
    def RightDown(self):
        CSecHorseBase.RightDown(self)
        if self.m_ID:
            CPlayerBase.RightDown(self)
        

    
    def SetAlpha(self, alpha):
        interface.CWalkerObject.SetAlpha(self, alpha)
        CSecHorseBase.SetAlpha(self, alpha)

    
    def GetResKey(self):
        (w0, h0) = interface.CWalkerObject.GetResKey(self)
        import npcheightdata
        (dw, dh) = npcheightdata.GetFixedData(self.m_CharIdx)
        w = w0 + dw
        h = h0 + dh
        return (w, h)

    
    def Enter(self):
        pass

    
    def Leave(self):
        pass

    
    def CheckShow(self):
        pass

    
    def IsDelayLoad(self):
        return False



class CMultiHorsePlayer(interface.CWalkerObject, CMulitHorseBase, CPlayerBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType = None, empty = False, chpType = None, realShape = None):
        interface.CWalkerObject.__init__(self, parent)
        CMulitHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, False, empty = empty, chpType = chpType, realShape = realShape)
        self.m_oCb = None
        self.SetPos(0, 0)

    
    def RightDown(self):
        CMulitHorseBase.RightDown(self)
        if self.m_ID:
            CPlayerBase.RightDown(self)
        

    
    def SetAlpha(self, alpha):
        interface.CWalkerObject.SetAlpha(self, alpha)
        CMulitHorseBase.SetAlpha(self, alpha)

    
    def GetResKey(self):
        (w0, h0) = interface.CWalkerObject.GetResKey(self)
        import npcheightdata
        (dw, dh) = npcheightdata.GetFixedData(self.m_CharIdx)
        w = w0 + dw
        h = h0 + dh
        return (w, h)

    
    def CheckShow(self):
        pass

    
    def Topmost(self):
        pass

    
    def SetCB(self, oCb):
        import misc
        self.m_oCb = misc.Functor(oCb)

    
    def Hold(self):
        if self.m_oCb:
            self.m_oCb()
        

    
    def LeftDown(self):
        if self.m_oCb:
            import cursor
            interface.Hold = interface.CShadowObject(self)
            (mx, my) = cursor.GetPos()
            (objx, objy) = self.GetPos()
            interface.HoldX = mx - objx
            interface.HoldY = my - objy
            self.Capture(1, 1)
            self.IgnoreSonMessage(True)
        else:
            CMulitHorseBase.LeftDown(self)

    
    def LeftUp(self):
        if self.m_oCb:
            if interface.Hold:
                interface.Hold = None
                self.Capture(0)
                self.IgnoreSonMessage(False)
            
        else:
            CMulitHorseBase.LeftUp(self)

    
    def Leave(self):
        if self.m_oCb:
            if interface.Hold and interface.Hold.Get() == self and self.GetShow() == False:
                self.LeftUp()
            
            CMulitHorseBase.Leave(self)
        else:
            CMulitHorseBase.Leave(self)

    
    def IsDelayLoad(self):
        return False



class CNewOldSameMultiHorseBase(CMulitHorseBase, CPlayerBase):
    
    def RefreshDirction(self):
        if self.m_MultiHorseID in chardefine.FIVE_HORSE_WITH_WING:
            CMulitHorseBase.RefreshDirction(self)
        else:
            self.SetPartFrame(self.GetParent().GetFrame())

    
    def GetAddonH(self):
        if self.m_MultiHorseID == 29 and self.m_PosType in (MULTIHORSE_POS_3, MULTIHORSE_POS_4):
            return 200
        
        if self.m_MultiHorseID == ridedefine.HORSE_HUSKY:
            return 150
        elif self.m_MultiHorseID == ridedefine.HORSE_COLD_SEA_DRAGON:
            return 150
        
        return 100

    
    def GetChpPath(self, pos):
        if not pos:
            pos = 0
        
        sState = getattr(self.GetParent(), 'm_State', chardefine.STATE_STAND)
        dState2State = {
            'walk_1': chardefine.STATE_STAND,
            'stand_1': chardefine.STATE_WALK }
        if self.m_MultiHorseID == ridedefine.HORSEID_BOAT:
            sState = chardefine.STATE_STAND
        
        sState = dState2State.get(sState, sState)
        if not sState:
            sState = chardefine.STATE_STAND
        
        if self.GetIsUseNewRes():
            sPath = 'horse/%.3d/chp/%.4d/%s%.4d.chp'
        else:
            sPath = 'horse/%.3d/oldchp/%.4d/%s%.4d.chp'
        return sPath % (self.m_MultiHorseID, self.GetFashionUseShape(), sState, pos)

    
    def GetChpData(self, path):
        return walkerchpcache.GetChpDataMgr().GetChpData(path, chardefine.PCK_HERO)

    
    def SetOffset(self):
        if self.IsOnFiveHorseSingleRide():
            return None
        
        if hasattr(self, 'm_CDirection') and self.m_CDirection:
            d = self.m_CDirection
        else:
            d = 0
        if self.m_ChpData:
            data = self.m_ChpData[d]
            self.SetFramesOffset(data)
            iFrame = None if self.GetParent() else 0
            if iFrame < iFrame:
                pass
            elif iFrame < chardefine.MAX_FRAME:
                self.SetPartFrame(iFrame)
            
        

    
    def InitIsUseNewRes(self, iIsUseNewRes, iCharIdx, dDesc):
        '''
\t\t:param int or dict or None dDesc:
\t\t:return:
\t\t'''
        if iIsUseNewRes is None:
            self.m_bIsUseNewRes = charpath.IsUseNewResWithID(iCharIdx, self)
        else:
            self.m_bIsUseNewRes = iIsUseNewRes

    
    def GetIsUseNewRes(self, iShape = None):
        '''
\t\t\xacO\xa7_\xa8\xcf\xa5\xce\xb7s\xb8\xea\xb7\xbd
\t\t'''
        if self.IsOnFiveHorseSingleRide():
            return True
        
        return walker.CCustomWalkerBase.GetIsUseNewRes(self, iShape)

    
    def GetResPath(self, iCharIdx, state, hero = False):
        if self.m_MultiHorseID in (ridedefine.HORSE_28, ridedefine.HORSEID_BOAT):
            if self.m_MultiHorseID == ridedefine.HORSEID_BOAT and self.m_PosType == MULTIHORSE_POS_1:
                return CMulitHorseBase.GetCharResPath(self, iCharIdx, state)
            elif self.GetIsUseNewRes():
                self.GetPartObject().ClearPart()
                lWeaponPathList = []
                lWeaponProPathList = []
                (lAddWeaponPathList, lAddWeaponProPathList) = self.AddWeaponPalReplenish()
                iFashionList = self.m_iFashionList
                if iFashionList and iFashionList[0]:
                    iFashionType = iFashionList[0]
                    (sFileName, lWeaponPathList, lWeaponProPathList) = charpath.GetCharResFashionPath(self.m_RealShape, self.m_WeaponKind, self.m_WeaponIdx, chardefine.STATE_SIT_ONE_FRAME, iFashionType)
                else:
                    sFileName = '%.4d/body/00' % self.m_RealShape
                    for i in [
                        2,
                        3,
                        4]:
                        lWeaponPathList.append([
                            '%s/%.3d' % (sFileName, i),
                            i])
                        lWeaponProPathList.append([
                            '%.4d/body/%.3d.pro' % (self.m_RealShape, i),
                            i])
                    
                    lWeaponPathList = lAddWeaponPathList + lWeaponPathList
                    lWeaponProPathList = lAddWeaponProPathList + lWeaponProPathList
                for sPartPath, iPart in enumerate(lWeaponPathList):
                    self.GetPartObject().AddPalPartList(iPart, sPartPath, lWeaponProPathList[iPos][0])
                
                return (sFileName, lWeaponPathList)
            else:
                filename = 'hero/%.4d/01' % self.m_RealShape
                return (filename, [])
        elif self.m_MultiHorseID in (ridedefine.HORSE_29, ridedefine.HORSE_30):
            if not self.IsOnFiveHorseSingleRide():
                return CMulitHorseBase.GetCharResPath(self, iCharIdx, state)
            else:
                return CMulitHorseBase.GetResPath(self, iCharIdx, state, hero)
        else:
            return CMulitHorseBase.GetResPath(self, iCharIdx, state, hero)

    
    def RightDown(self):
        CMulitHorseBase.RightDown(self)
        if self.m_ID:
            CMulitHorseBase.RightDown(self)
        

    
    def GetResPck(self):
        import misc
        iShape = self.m_CharIdx
        if iShape in (113, 233):
            return chardefine.PCK_HERO
        
        if misc.IsHasOldChar():
            if self.GetIsUseNewRes():
                return chardefine.PCK_HERO
            else:
                return chardefine.PCK_OLD_CHAR
        else:
            return chardefine.PCK_HERO

    
    def SetState(self, state, ani = True, reset = False):
        if self.m_MultiHorseID in chardefine.ONE_RIDER_FRAME_HORSE:
            ani = False
        
        if self.m_MultiHorseID == ridedefine.HORSE_HUSKY:
            ani = False
        
        if self.m_MultiHorseID in chardefine.FIVE_HORSE_WITH_WING and not self.IsOnFiveHorseSingleRide():
            state = chardefine.STATE_STAND
        
        dState2State = {
            'walk_1': 'stand',
            'stand_1': 'walk' }
        self.LoadChpData()
        self.SetOffset()
        CMulitHorseBase.SetState(self, dState2State.get(state, state), ani, reset)

    
    def LoadData(self):
        if self.m_MultiHorseID in chardefine.OLD_USE_NEW_DOUBLE_HORSE:
            if self.IsOnFiveHorseSingleRide():
                return CMulitHorseBase.LoadData(self)
            
            if self.m_MultiHorseID == ridedefine.HORSE_HUSKY:
                return CMulitHorseBase.LoadData(self)
            
            sPck = self.GetResPck()
            sOtherState = 'stand'
            (sPath, sWeaponPathList) = self.GetResPath(self.m_CharIdx, sOtherState, self.m_CharIdx < 1000)
            self.m_Rider = None
            self.m_WeaponCover = None
            self.ResetNameTitle()
            self.SetPartList([])
            self.LoadWingByState(sOtherState)
            self.SetFairyState(sOtherState)
            if self.m_MultiHorseID in chardefine.HORSETYPE_ONE_STAND_ONE_SIT:
                if self.m_PosType == MULTIHORSE_POS_0:
                    sActName = chardefine.STATE_SIT_ONE_FRAME
                else:
                    sActName = chardefine.STATE_STAND
            elif self.m_MultiHorseID == 28:
                sActName = chardefine.STATE_SIT_ONE_FRAME
            elif self.m_MultiHorseID in (ridedefine.HORSE_29, ridedefine.HORSE_30):
                sActName = chardefine.STATE_STAND
                if self.IsCanUseWeapon12Spr('stand'):
                    if self.IsUseSpecialStand1():
                        sActName = 'stand1_weapon_12'
                    else:
                        sActName = 'stand_weapon_12'
                
            else:
                sActName = self.m_State
                if self.m_MultiHorseID and sActName not in ('walk', 'stand', 'walk_1', 'stand_1'):
                    sActName = 'stand'
                
            sSprPath = '%s/%s.spr' % (sPath, sActName)
            
            try:
                if sWeaponPathList:
                    
                    try:
                        self.Load(sSprPath, sPck, sWeaponPathList)
                        self.m_lWeaponPathList = sWeaponPathList
                        self.ReLoadWeaponPalPro()
                    except SystemError:
                        self.Load(sSprPath, sPck)
                    except:
                        None<EXCEPTION MATCH>SystemError
                    

                None<EXCEPTION MATCH>SystemError
                self.Load(sSprPath, sPck)
                self.m_SprPath = sSprPath
            except SystemError:
                sSprPath = '0000/stand.spr'
                
                try:
                    self.Load(sSprPath, chardefine.PCK_NEW_CHAR)
                    self.m_SprPath = sSprPath
                    return None
                except SystemError:
                    pass
                except:
                    None<EXCEPTION MATCH>SystemError
                


            None<EXCEPTION MATCH>SystemError
        else:
            CMulitHorseBase.LoadData(self)
        if self.m_MultiHorseID in chardefine.ONE_RIDER_FRAME_HORSE:
            self.SetFrame(self.FrameAmount() - 1)
        

    
    def LoadWing(self, wingkind, wingpal = 0):
        if hasattr(self, 'm_Wing'):
            del self.m_Wing
        
        if self.IsEmptyRider():
            return None
        
        if (self.m_MultiHorseID in chardefine.FIVE_HORSE_WITH_WING or self.m_MultiHorseID in chardefine.HORSETYPE_ONE_STAND_ONE_SIT) and self.m_PosType == MULTIHORSE_POS_1:
            return walker.CWalkerBase.LoadWing(self, wingkind, wingpal)
        
        if self.m_MultiHorseID in (ridedefine.HORSE_HUSKY, ridedefine.HORSE_COLD_SEA_DRAGON):
            return CMulitHorseBase.LoadWing(self, wingkind, wingpal)
        



class CMapNewOldSameMultiHorsePlayer(walker.CMaskHeroObject, CNewOldSameMultiHorseBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType = None, empty = False, chpType = None, realShape = None):
        walker.CMaskHeroObject.__init__(self, parent)
        CMulitHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, empty = empty, chpType = chpType, realShape = realShape)
        self.SetPos(0, 0)

    
    def __del__(self):
        if CPlayerBase:
            CPlayerBase.s_PlayerNum -= 1
        
        import delayctrl
        delayctrl.GetDelayDlgCtrl().DelWalker(self.GetLoadType(), id(self))
        delayctrl.GetDelayOtherCtrl().DelWalker(id(self))

    
    def GetLoadType(self):
        if self.IsOnFiveHorseSingleRide():
            return 2
        else:
            return 3

    
    def RightDown(self):
        CMulitHorseBase.RightDown(self)
        if self.m_ID:
            CPlayerBase.RightDown(self)
        

    
    def Load(self, sPath, sPack, sWeapon = None):
        import delayctrl
        import hero
        self.m_sInPck = sPack
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if not charpath.Exist(sPath, sPack):
                raise SystemError('%s,%s' % (sPath, sPack))
            
            if sPack == 'hero':
                sSpr = '0000/0000.spr'
                sTeamWeapon = [
                    [
                        '0000/001',
                        1]]
            elif sPack == 'newchar':
                sSpr = '0001/0000.spr'
                sTeamWeapon = [
                    [
                        '0001/001',
                        1]]
            else:
                sSpr = sPath
                sTeamWeapon = sWeapon
            if not sWeapon:
                interface.CMapHeroObject.Load(self, sSpr, sPack)
                delayctrl.GetDelayDlgCtrl().AddWalker(self.GetLoadType(), self, sPath, sPack)
            else:
                interface.CMapHeroObject.Load(self, sSpr, sPack, sTeamWeapon)
                delayctrl.GetDelayDlgCtrl().AddWalker(self.GetLoadType(), self, sPath, sPack, sWeapon)
        elif not sWeapon:
            interface.CMapHeroObject.Load(self, sPath, sPack)
        else:
            interface.CMapHeroObject.Load(self, sPath, sPack, sWeapon)

    
    def LoadWeapon(self, lWeaponpath):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            delayctrl.GetDelayDlgCtrl().LoadWeapon(self.GetLoadType(), self, lWeaponpath)
        else:
            interface.CMapHeroObject.LoadWeapon(self, lWeaponpath)

    
    def LoadImagess(self, sPath):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if charpath.Exist(sPath, self.m_sInPck):
                delayctrl.GetDelayDlgCtrl().AddLoadWalkerImagess(self.GetLoadType(), self, sPath)
            else:
                return 1
        else:
            return interface.CMapHeroObject.LoadImagess(self, sPath)

    
    def LoadImages(self, sPath = ''):
        import delayctrl
        import hero
        if delayctrl.GetDelayDlgCtrl().IsCanDelay(self.GetLoadType(), self) and self != hero.GetHeroObject() and not isinstance(self.GetParent(), hero.CHero):
            if charpath.Exist(sPath, self.m_sInPck):
                delayctrl.GetDelayDlgCtrl().AddLoadWalkerImages(self.GetLoadType(), self, sPath)
            else:
                return 1
        elif sPath:
            return interface.CMapHeroObject.LoadImages(self, sPath)
        else:
            return interface.CMapHeroObject.LoadImages(self)

    
    def SetAlpha(self, alpha):
        walker.CMaskHeroObject.SetAlpha(self, alpha)
        CMulitHorseBase.SetAlpha(self, alpha)

    
    def GetResKey(self):
        (w0, h0) = walker.CMaskHeroObject.GetResKey(self)
        import npcheightdata
        (dw, dh) = npcheightdata.GetFixedData(self.m_RealShape)
        w = w0 + dw
        h = h0 + dh
        return (w, h)

    
    def SetShow(self, bShow):
        if getattr(self, 'm_Wing', None):
            self.m_Wing.SetShow(bShow)
        
        if self.m_Rider:
            self.m_Rider.SetShow(bShow)
        
        walker.CMaskHeroObject.SetShow(self, bShow)

    
    def SetPos(self, x, y):
        walker.CMaskHeroObject.SetPos(self, x, y)
        self.SetMaskZ(y)



class CNewOldMultiHorsePlayer(interface.CWalkerObject, CNewOldSameMultiHorseBase):
    
    def __init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType = None, empty = False, chpType = None, realShape = None):
        interface.CWalkerObject.__init__(self, parent)
        CMulitHorseBase.__init__(self, parent, iObjID, iCharIdx, desc, multiHorseID, posType, False, empty = empty, chpType = chpType, realShape = realShape)
        self.m_oCb = None
        self.SetPos(0, 0)

    
    def SetAlpha(self, alpha):
        interface.CWalkerObject.SetAlpha(self, alpha)
        CMulitHorseBase.SetAlpha(self, alpha)

    
    def GetResKey(self):
        (w0, h0) = interface.CWalkerObject.GetResKey(self)
        import npcheightdata
        (dw, dh) = npcheightdata.GetFixedData(self.m_CharIdx)
        w = w0 + dw
        h = h0 + dh
        return (w, h)

    
    def CheckShow(self):
        pass

    
    def Topmost(self):
        pass

    
    def SetCB(self, oCb):
        import misc
        self.m_oCb = misc.Functor(oCb)

    
    def Hold(self):
        if self.m_oCb:
            self.m_oCb()
        

    
    def LeftDown(self):
        if self.m_oCb:
            import cursor
            interface.Hold = interface.CShadowObject(self)
            (mx, my) = cursor.GetPos()
            (objx, objy) = self.GetPos()
            interface.HoldX = mx - objx
            interface.HoldY = my - objy
            self.Capture(1, 1)
            self.IgnoreSonMessage(True)
        else:
            CNewOldSameMultiHorseBase.LeftDown(self)

    
    def LeftUp(self):
        if self.m_oCb:
            if interface.Hold:
                interface.Hold = None
                self.Capture(0)
                self.IgnoreSonMessage(False)
            
        else:
            CNewOldSameMultiHorseBase.LeftUp(self)

    
    def Leave(self):
        if self.m_oCb:
            if interface.Hold and interface.Hold.Get() == self and self.GetShow() == False:
                self.LeftUp()
            
            CNewOldSameMultiHorseBase.Leave(self)
        else:
            CNewOldSameMultiHorseBase.Leave(self)

    
    def IsDelayLoad(self):
        return False



def IsOnSingleHorse(multihorseID, posType):
    if multihorseID in chardefine.DOUBLE_HORSE_SPE and posType in (MULTIHORSE_POS_1, MULTIHORSE_POS_0):
        return True
    
    if multihorseID not in chardefine.DOUBLE_HORSE_TOG and multihorseID in chardefine.MULTI_HORSE:
        if posType in (MULTIHORSE_POS_3, MULTIHORSE_POS_4):
            return True
        
    
    return False


def IsPlayerOnRide(pid, horseID, posType):
    if horseID in chardefine.DOUBLE_HORSE_SPE and posType in (MULTIHORSE_POS_0, MULTIHORSE_POS_1):
        return True
    elif horseID in chardefine.MULTI_HORSE:
        return True
    


def CreatePlayer(x, y, id, charidx, desc, realShape = None, iIsUseNewRes = None):
    import map
    import yardcontext
    if not map.GetGameMapObject():
        return None
    
    if yardcontext.IsOpenYardMap():
        cls = CYardPlayer
    else:
        cls = CPlayer
    obj = cls(map.GetGameMapObject(), id, charidx, desc, realShape = realShape, iIsUseNewRes = iIsUseNewRes)
    obj.SetPos(x, y)
    return obj


def Player2HorsePlayer(ownerID, playerID, posType):
    print '\xb4\xb6\xb3q\xa8\xa4\xa6\xe2\xc2\xe0\xa6h\xa4H\xa7\xa4\xc3M\xa8\xa4\xa6\xe2!!!!', playerID, ownerID, posType
    import world
    import hero
    import map
    playerObj = world.g_Objects[playerID]
    ownerObj = world.g_Objects[ownerID]
    horseID = 0
    if 'horse' in ownerObj.m_CharDesc:
        horseID = ownerObj.m_CharDesc['horse'][0]
    
    if not IsPlayerOnRide(playerID, horseID, posType):
        return playerObj
    
    if horseID not in chardefine.MULTI_HORSE_MAIN:
        return playerObj
    
    nameAttr = None
    if hasattr(playerObj, 'm_NameAttr') and playerObj.m_NameAttr:
        nameAttr = playerObj.m_NameAttr
    
    titleAttr = None
    if hasattr(playerObj, 'm_TitleAttr') and playerObj.m_TitleAttr:
        titleAttr = playerObj.m_TitleAttr
    
    team = None
    if hasattr(playerObj, 'm_Team'):
        team = playerObj.m_Team
    
    summTeam = None
    if hasattr(playerObj, 'm_SummTeam'):
        summTeam = playerObj.m_SummTeam
    
    followList = None
    if hasattr(playerObj, 'm_FollowList'):
        followList = playerObj.m_FollowList
    
    origDesc = playerObj.GetOrigDesc()
    chatIdx = playerObj.m_CharIdx
    desc = playerObj.m_CharDesc
    realShape = playerObj.m_RealShape
    obj = ownerObj.CreateMultiHorsePlayer(playerID, chatIdx, desc, posType, realShape = realShape)
    obj.SetOrgLevel(playerObj.GetOrgLevel())
    obj.SetSubHorsePlayer(True)
    if team is not None:
        obj.m_Team = team
    
    if summTeam is not None:
        obj.m_SummTeam = summTeam
    
    if followList is not None:
        obj.m_FollowList = followList
    
    obj.SetOrigDesc(origDesc)
    if nameAttr:
        obj.SetName(*nameAttr)
        if titleAttr:
            obj.SetTitle(*titleAttr)
        
    
    if hero.g_Hero == playerObj:
        hero.g_Hero = obj
        ownerObj.SetShow(True)
        hero.g_Hero.SetShow(True)
        map.g_Map.SetFollowObject(ownerObj)
    
    obj.SetShow(True)
    if hasattr(obj, 'CheckShow'):
        obj.CheckShow()
    
    return obj


def HorsePlayer2Player(ownerID, playerID, x, y, needDel = True):
    print '\xa6h\xa4H\xa7\xa4\xc3M\xa8\xa4\xa6\xe2\xc2\xe0\xb4\xb6\xb3q\xa8\xa4\xa6\xe2!!!!', playerID
    import hero
    import world
    import map
    playerObj = world.g_Objects.get(playerID)
    ownerObj = world.g_Objects.get(ownerID)
    if needDel:
        ownerObj.DelMultiHorsePlayer(playerID)
    
    world.g_Objects[playerID] = None
    team = None
    if hasattr(playerObj, 'm_Team'):
        team = playerObj.m_Team
    
    summTeam = None
    if hasattr(playerObj, 'm_SummTeam'):
        summTeam = playerObj.m_SummTeam
    
    followList = None
    if hasattr(playerObj, 'm_FollowList'):
        followList = playerObj.m_FollowList
    
    origDesc = playerObj.GetOrigDesc()
    import copy
    if hero.g_Hero == playerObj:
        hero.CreateHero(x, y, copy.deepcopy(hero.g_Prop.m_Desc))
        if team is not None:
            hero.g_Hero.m_Team = team
        
        if summTeam is not None:
            hero.g_Hero.m_SummTeam = summTeam
        
        if followList is not None:
            hero.g_Hero.m_FollowList = followList
        
        hero.g_Hero.SetOrigDesc(origDesc)
        import multihorsemgr
        horsePosList = multihorsemgr.GetSingleHorsePos(hero.g_ID)
        if horsePosList:
            hero.g_Hero.RefreshMultiHorse(horsePosList)
        
        hero.g_Hero.ResetShape()
        CheckHideDesc(playerID)
        return hero.g_Hero
    else:
        nameAttr = None
        if hasattr(playerObj, 'm_NameAttr') and playerObj.m_NameAttr:
            nameAttr = playerObj.m_NameAttr
        
        titleAttr = None
        if hasattr(playerObj, 'm_TitleAttr') and playerObj.m_TitleAttr:
            titleAttr = playerObj.m_TitleAttr
        
        charidx = playerObj.m_CharIdx
        realShape = playerObj.m_RealShape
        desc = playerObj.GetOrigDesc()
        iOrgLevel = playerObj.GetOrgLevel()
        (cx, cy) = map.g_Map.ServerPos2ClientPos(x, y)
        iIsUseNewRes = charpath.GetResNewWithShapeDesc(charidx, desc)
        obj = CreatePlayer(cx, cy, playerID, charidx, desc, realShape = realShape, iIsUseNewRes = iIsUseNewRes)
        if not obj:
            return None
        
        if team is not None:
            obj.m_Team = team
        
        if summTeam is not None:
            obj.m_SummTeam = summTeam
        
        if followList is not None:
            obj.m_FollowList = followList
        
        if nameAttr:
            obj.SetName(*nameAttr)
            if titleAttr:
                obj.SetOrgLevel(iOrgLevel)
                obj.SetTitle(*titleAttr)
            
        
        obj.SetOrigDesc(origDesc)
        import multihorsemgr
        horsePosList = multihorsemgr.GetSingleHorsePos(playerID)
        if horsePosList:
            obj.RefreshMultiHorse(horsePosList)
        
        obj.ResetShape()
        CheckHideDesc(playerID)
        return obj


def IsPlayer(obj):
    import hero
    oHero = hero.GetHeroObject()
    if oHero and oHero == obj:
        return False
    
    if isinstance(obj, CPlayer):
        return True
    
    if hasattr(obj, 'IsMultiHorsePlayer') and obj.IsMultiHorsePlayer() and not obj.IsEmptyRider():
        return True
    
    return False


def IsMyself(obj):
    import hero
    oHero = hero.GetHeroObject()
    if oHero and oHero == obj:
        return True
    
    return False


def GetScoreStr(iScore):
    iScore2Str = {
        0: '\xc4y\xc4y\xb5L\xa6W',
        1: '\xa4\xfb\xa4M\xa4p\xb8\xd5',
        2: '\xb9\xf1\xc5S\xc0Y\xa8\xa4',
        3: '\xa4p\xa6\xb3\xa6W\xae\xf0',
        4: '\xc1n\xa6W\xc4N\xb0_',
        5: '\xa6W\xb0\xca\xa5|\xa4\xe8',
        6: '\xa6p\xa4\xe9\xa4\xa4\xa4\xd1',
        7: '\xa7\xde\xaba\xb8s\xb6\xaf',
        8: '\xab\xc2\xbe_\xa4K\xa4\xe8',
        9: '\xbfW\xa8B\xa4\xd1\xa4U',
        10: '\xbb\\\xa5@\xb5L\xc2\xf9',
        11: '\xa5X\xaf\xab\xa4J\xa4\xc6',
        12: '\xa4@\xa5N\xa9v\xaev' }
    return iScore2Str.get(iScore)


def GetForceStr(iForce):
    iForce2Str = {
        1: '\xab\xd2\xb0\xea',
        2: '\xc1p\xb7\xf9' }
    return iForce2Str.get(iForce)


def GetForceRankStr(iRank):
    iRank2Str = {
        16: '\xa4j\xa4\xb8\xab\xd3',
        15: '\xa4\xb8\xab\xd3',
        14: '\xa4W\xb1N',
        13: '\xa4\xa4\xb1N',
        12: '\xa4\xd6\xb1N',
        11: '\xa4W\xae\xd5',
        10: '\xa4\xa4\xae\xd5',
        9: '\xa4\xd6\xae\xd5',
        8: '\xa4W\xb1L',
        7: '\xa4\xa4\xb1L',
        6: '\xa4\xd6\xb1L',
        5: '\xa4W\xa4h',
        4: '\xa4\xa4\xa4h',
        3: '\xa4U\xa4h',
        2: '\xa4W\xb5\xa5\xa7L',
        1: '\xa6C\xa7L' }
    return iRank2Str.get(iRank)


def DoCreatePlayer(cx, cy, pID, iShape, dDesc, realShape, x, y, canFly, direct, emotetype, update_flag, nameColor, playername, country, pOrgID, color, title, titleID, iSiblingType, iOrgLevel, iTitleGrade, dExtend = None):
    import world
    iIsUseNewRes = charpath.GetResNewWithShapeDesc(iShape, dDesc)
    obj = CreatePlayer(cx, cy, pID, iShape, dDesc, realShape = realShape, iIsUseNewRes = iIsUseNewRes)
    if not obj:
        return None
    
    obj.SetOrgLevel(iOrgLevel)
    obj.SetServerPos(x, y)
    obj.SetFlyState(canFly)
    obj.SetTitleGrade(iTitleGrade)
    if direct != 0:
        obj.SetDirection((direct - 1) * 2)
    
    obj.SetEmote(emotetype, False)
    import map
    import netmap
    import mdnattreasure
    minimapid = map.GetCurrentMiniMapID()
    if minimapid == 9382:
        upcolor = interface.COLOR_43
        font = interface.FontLT16_1
        country = 0
    elif update_flag & 128:
        upcolor = interface.COLOR_53
        font = interface.FontLT16E_1
    elif nameColor == 1:
        upcolor = interface.COLOR_42
        font = interface.FontLT16_1
    else:
        upcolor = interface.COLOR_41
        font = interface.FontLT16_1
    obj.SetName(playername, pID, country, upcolor, top = True, font = font, iSiblingType = iSiblingType, dExtend = dExtend)
    titleColor = netmap.ChangePlayerTitleColor(pOrgID, color)
    iColor = mdnattreasure.GetPlayerTitleColor(pID, titleColor)
    obj.SetProp('m_OrgID', pOrgID)
    import delayloading
    import asynctaskqueue
    import asynctaskdefine
    if delayloading.IsShowLoading():
        asynctaskqueue.GetAsyncTaskQueue().AddEmptyTask(asynctaskdefine.TASK_TYPE_OTHER, '', '', misc.Functor(obj.SetTitle1, title, iColor, titleID))
    else:
        obj.SetTitle1(title, iColor, titleID)
    if minimapid != 9382:
        import friend
        if not netmap.IsInBlackRoom():
            friend.GetArdPlayerMgr().Add(pID, playername)
        
    
    obj.CheckShow()
    obj.ChangeNameColor(nameColor)
    import yardcontext
    yardcontext.CheckAndChangePlayerInHotSpring(world.RefershPlayerTeam(pID))
    CheckHideDesc(pID)


def ChangePlayerName(iPlayerID, iUpdateFlag, iNameColor, sPlayerName):
    import map
    import netmap
    import world
    oPlayer = world.GetObj(iPlayerID)
    if not oPlayer:
        return None
    
    iMiniMapID = map.GetCurrentMiniMapID()
    if iMiniMapID == 9382:
        iUpColor = interface.COLOR_43
        iFont = interface.FontLT16_1
    elif iUpdateFlag & 128:
        iUpColor = interface.COLOR_53
        iFont = interface.FontLT16E_1
    elif iNameColor == 1:
        iUpColor = interface.COLOR_42
        iFont = interface.FontLT16_1
    else:
        iUpColor = interface.COLOR_41
        iFont = interface.FontLT16_1
    (_, _, iCountry, _, iTop, _, iSiblingType, dExtend) = oPlayer.m_NameAttr
    oPlayer.SetName(sPlayerName, iPlayerID, iCountry, iUpColor, top = iTop, font = iFont, iSiblingType = iSiblingType, dExtend = dExtend)
    if hasattr(oPlayer, 'm_TitleAttr'):
        oPlayer.SetTitle(*oPlayer.m_TitleAttr)
    
    if iMiniMapID != 9382:
        import friend
        if not netmap.IsInBlackRoom():
            friend.GetArdPlayerMgr().Add(iPlayerID, sPlayerName)
        
    
    oPlayer.CheckShow()
    oPlayer.ChangeNameColor(iNameColor)


def CheckHideDesc(iPlayerID):
    import world
    import mxkitcheninterface
    oPlayer = world.GetObj(iPlayerID)
    if not oPlayer:
        return None
    
    dDesc = misc.DeepCopy(oPlayer.GetTempObject().GetOrdDesc())
    tHideKey = []
    if mxkitcheninterface.CheckGameStart():
        tHideKey = [
            chardefine.DESC.KEY_HORSE,
            chardefine.DESC.WING,
            chardefine.DESC.KEY_FAIRY,
            chardefine.DESC.KEY_TRACK,
            chardefine.DESC.KEY_AURA,
            chardefine.DESC.WEAPON,
            chardefine.DESC.BACK_DECORATE]
    
    LOG_DEBUG('CheckHideDesc>>>>>>>', iPlayerID, tHideKey, mxkitcheninterface.CheckGameStart())
    if tHideKey:
        iGhostBuff = oPlayer.GetGhostBuff()
        dDesc = descinterface.ClearDescByKey(dDesc, tHideKey)
        oPlayer.GetTempObject().SetTempDesc(dDesc)
        oPlayer.SetOrigDesc(dDesc)
        oPlayer.ResetShape()
        oPlayer.RefreshMultiHorse([])
        if iGhostBuff:
            oPlayer.SetGhostBuff(iGhostBuff)
            oPlayer.CheckShow()
