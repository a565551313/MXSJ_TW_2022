# pycdc 交叉复核产物 · script.fls entry 3465
# co_filename(原始)='script/mxgame/activity/survive/dlgsurvive.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3465.pyc (Python 2.5)

'''
\xb4\xf3\xcc\xd3\xc9\xb1
'''
import math
import avatar
import banword
import chardefine
import combdialog
import combmacro
import commoncb
import copy
import cursor
import dlgitem
import dlgmagic
import dlgmap
import dlgminipanel
import dlgpet
import dlgstate
import dlgsysopt
import dlgtaskfollow
import hero
import interface
import item
import itemdata
import key
import magicmgr
import mainmenu
import map
import mapani
import misc
import netitem
import netmap
import mxnumbers
import player
import popmenu
import random
import ratio
import shortcut
import skillicondata
import survivemgr
import surviverdefine
import timer
import tipsclosemgr
import ui
import usermacro
import walker
import warui
import world
import wrapinterface
import wrapmath
g_Func = { }
g_UseMapItemFlag = False
g_VirBagDlg = None
g_GameSurviveCtrl = None

def ModuleReset():
    global g_UseMapItemFlag, g_VirBagDlg, g_GameSurviveCtrl
    if g_GameSurviveCtrl:
        g_GameSurviveCtrl.ModuleReset()
    
    g_UseMapItemFlag = False
    g_VirBagDlg = None
    g_GameSurviveCtrl = None


def FuncError(func):
    
    def RealFunc(*args, **kwags):
        
        try:
            return func(*args, **kwags)
        except:
            LOG_EXC('%s\xa8\xe7\xbc\xc6\xb0\xf5\xa6\xe6\xbf\xf9\xbb~' % str(func))


    return RealFunc


def GetGameSurviveCtrl():
    ''':rtype: CGameSurviveCtrl'''
    global g_GameSurviveCtrl
    if not g_GameSurviveCtrl:
        g_GameSurviveCtrl = CGameSurviveCtrl()
    
    return g_GameSurviveCtrl


def DelGameSurviveCtrl():
    if g_GameSurviveCtrl:
        g_GameSurviveCtrl.GameEnd()
    


def SwitchVirBagDlg():
    global g_VirBagDlg
    if not g_VirBagDlg:
        g_VirBagDlg = CVirBagDlg()
    else:
        g_VirBagDlg.SetShow(not g_VirBagDlg.GetShow())


def SwitchMinimap():
    '''\xa5\xb4\xb6}\xa4p\xa6a\xb9\xcf dlgmap.SwitchMinimap'''
    if not surviverdefine.IS_OPEN_SURVIVE:
        return False
    
    if survivemgr.GetSurviveMgr().IsInSurviveGame():
        if mainmenu.IsWar():
            return True
        
        GetGameSurviveCtrl().SwitchMinimap()
        return True
    
    return False


def IsSelectNpc(obj):
    '''\xacO\xa7_\xbf\xef\xa4\xa4Npc'''
    import npc
    if not obj:
        return False
    
    if obj.m_ID < 0:
        return False
    
    if isinstance(obj, npc.CNpc) and not isinstance(obj, npc.CClientNpc):
        if obj.GetName() == '\xb3\xb7\xa4k':
            return False
        
        return True
    else:
        return False


def IsMapSelectMap(obj):
    '''\xacO\xa7_\xbf\xef\xa4\xa4\xa6a\xb9\xcf'''
    PRINT(obj)
    return False


def IsSelectMap():
    '''\xacO\xa7_\xbf\xef\xa4\xa4\xa6a\xb9\xcf'''
    import map
    if not world.g_EnterCursor:
        return None
    
    CommitUseItem(map.GetGameMapObject())


def CommitUseItem(obj):
    '''\xbdT\xbb{\xa8\xcf\xa5\xce\xaa\xab\xab~'''
    import netsurvive
    import map
    NormalSelect()
    if isinstance(obj, map.CMap):
        (iClientX, iClientY) = GetCursorMapClientPos()
        (iCurX, iCurY) = map.GetGameMapObject().ClientPos2ServerPos(iClientX, iClientY)
        iTagerID = iCurX * 1000 + iCurY
        netsurvive.C2SSurviveFileUse(world.g_UseItemID, iTagerID, iNpcList = GetNearObject(iClientX, iClientY))
    else:
        iTagerID = obj.m_ID
        netitem.C2SVirItemUse(world.g_UseItemID, iTagerID)
    g_VirBagDlg.SetShow(False)


def NormalSelect():
    '''\xb2M\xb2z\xbf\xef\xbe\xdc'''
    world.g_SelectTips = None
    world.g_EscTips = None
    world.SetMessageProcess(None, None, world.NormalCondition, None)
    world.g_CurrType = 0


def GetCursorMapClientPos():
    import cursor
    import map
    (iCurX, iCurY) = cursor.GetCursorPos()
    (iMapX, iMapY) = map.GetGameMapObject().GetPos()
    iCurX -= iMapX
    iCurY -= iMapY
    return (iCurX, iCurY)


def GetNearObject(iCurX, iCurY):
    iNpcList = []
    oObjList = world.GetAllObj()
    for iObjID, obj in oObjList.iteritems():
        (iObjPosX, iObjPosY) = obj.GetPos()
        if (iObjPosX - iCurX) ** 2 + (iObjPosY - iCurY) ** 2 < surviverdefine.NEAR_DISTANT ** 2:
            iNpcList.append(iObjID)
            continue
    
    return iNpcList


class CGameSurviveCtrl(object):
    '''
\t\xa4j\xb0k\xb1\xfe\xb9C\xc0\xb8\xb1\xb1\xbbs\xbe\xb9
\t\xa4j\xb0k\xb1\xfe\xaa\xba\xa9\xd2\xa6\xb3\xa5\\\xaf\xe0\xb3\xa3\xa6\xb3\xb3o\xad\xd3\xc3\xfe\xba\xde\xb2z\xb1\xb1\xa8\xee
\t'''
    
    def __init__(self):
        self.m_ClassChooseDlg = None
        self.m_PlayerNumPal = None
        self.m_VirStateDlg = None
        self.m_WorldBagDlg = None
        self.m_WorldMapDlg = None
        self.m_GameOverDlg = None
        self.m_MiniMapDlg = None
        self.m_PlayerInfoDlg = None
        self.m_UseItemForEquitDlg = None
        self.m_QuickOperateTips = None
        self.m_QuickOperateDlg = None
        self.m_SurviveAdviceDlg = None
        self.m_iLastHP = 0
        self.m_bIsFirstOpen = False
        self.m_bIsShowSnowGril = False
        self.m_bIsShowMagic = True
        self.m_DelTimer = None
        self.m_bGameInitFlag = False
        self.m_iHp = 0
        self.m_oTxtObj = None
        self.m_CollideEffectData = { }
        self.m_oSuperBoxMagic = None
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateGameStart, self.OnGameFlagChange)

    
    def GameInit(self):
        '''
\t\t\xb9C\xc0\xb8\xaa\xec\xa9l\xa4\xc6
\t\t\xa8\xe7\xbc\xc6\xacy\xb5{\xb9L\xa6h\xbe\xc9\xadP\xa6p\xaaG\xa4\xa4\xb6\xa1\xa5X\xb2{\xb3\xf8\xbf\xf9\xa1A\xab\xe1\xad\xb1\xb4\xc0\xb4\xab\xc5\xde\xbf\xe8\xa5\xa2\xae\xc4
\t\t\xa9\xd2\xa5H\xb6i\xa6\xe6\xa4\xc0\xc3\xfe\xb3B\xb2z
\t\t'''
        if not surviverdefine.IS_OPEN_SURVIVE:
            return None
        
        if self.m_bGameInitFlag:
            return None
        
        self.m_bGameInitFlag = True
        
        try:
            self.OnWarSwitch(mainmenu.IsWar())
        except:
            LOG_EXC('\xbe\xd4\xb0\xab\xb4\xc0\xb4\xab\xa5X\xb2{\xb0\xdd\xc3D')

        
        try:
            self.RegistSlot()
        except:
            LOG_EXC('\xaa\xec\xa9l\xa4\xc6\xabH\xb8\xb9\xa5X\xb2{\xb0\xdd\xc3D')

        survivemgr.ChangeItemData()
        survivemgr.ChangeShadowPetDnData()
        
        try:
            self.ChangeGameFun()
        except:
            LOG_EXC('\xb4\xc0\xb4\xab\xb9C\xc0\xb8\xa8\xe7\xbc\xc6')

        hero.EngineTimeSyn(1, 90)

    
    def GameEnd(self):
        '''\xb9C\xc0\xb8\xb5\xb2\xa7\xf4'''
        if not self.m_bGameInitFlag:
            return None
        
        self.m_bGameInitFlag = False
        self.CloseClassDlg()
        self.CloseGameTips()
        self.ClosePlayerNumPal()
        self.ClaerSlot()
        self.ReChangeGameFun()
        hero.EngineTimeSyn(0)
        survivemgr.GetSurviveMgr().GameClear()

    
    def ModuleReset(self):
        self.ClaerSlot()
        self.ReChangeGameFun()
        hero.EngineTimeSyn(0)

    
    def RegistSlot(self):
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateMatchInfo, self.OnGameMatchFlagChange)
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateWorldBagID, self.OnGameOpenWolrdBag)
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateGameEndInfo, self.OnGameEndInfo)
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnSceneChange')
        commoncb.RegistCB(commoncb.MAP_ONHAND, self, 'OnAbandonItems')
        commoncb.RegistCB(commoncb.STATE_CHANGE, self, 'OnStateChange')
        hero.AddRefreshCallback('CGameSurviveCtrl', (('m_Desc', 0, 0), ('m_Shape', 0, 0)), self.OnSetHeroPhoto)
        hero.AddRefreshCallback('CGameSurviveCtrl', (('m_Class', 0, 0),), self.OnHeroClassChange)
        hero.AddRefreshCallback('CGameSurviveCtrl', (('m_HP', 0, 0),), self.OnHeroHPChange)
        hero.AddSkillUpdateCallBack('CGameSurviveCtrl', misc.Functor(self.OnSkillUpdateCallBack))

    
    def ClaerSlot(self):
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssDisconnect(oSurviveMgr.SS_UpdateMatchInfo, self.OnGameMatchFlagChange)
        oSurviveMgr.ssDisconnect(oSurviveMgr.SS_UpdateWorldBagID, self.OnGameOpenWolrdBag)
        oSurviveMgr.ssDisconnect(oSurviveMgr.SS_UpdateGameEndInfo, self.OnGameEndInfo)
        commoncb.RemoveCB(commoncb.SCENE_CHANGE, self, 'OnSceneChange')
        commoncb.RemoveCB(commoncb.MAP_ONHAND, self, 'OnAbandonItems')
        commoncb.RemoveCB(commoncb.STATE_CHANGE, self, 'OnStateChange')
        hero.RemoveSkillUpdateCallBack('CGameSurviveCtrl')

    
    def ChangeGameFun(self):
        '''
\t\t\xb4\xc0\xb4\xab\xb9C\xc0\xb8\xb1\xb5\xa4f
\t\t\xa4U\xad\xb1\xb0\xca\xbaA\xaa\xba\xb4\xc0\xb4\xab\xa8\xe7\xbc\xc6\xa1A\xab\xe1\xad\xb1\xa8S\xb0\xdd\xc3D\xa6b\xa8\xec\xb9\xef\xc0\xb3\xaa\xba\xbc\xd2\xb6\xf4
\t\t'''
        if not surviverdefine.IS_OPEN_SURVIVE:
            return None
        
        if g_Func:
            return None
        
        self.ChangeMainMenu(True)
        g_Func['mapani.CAni.SetAniShow'] = mapani.CAni.SetAniShow
        mapani.CAni.SetAniShow = MapAniCAniSetAniShow
        g_Func['warui.UseItem'] = warui.UseItem
        warui.UseItem = OpenWarBagDlg
        g_Func['map.AllowMove'] = map.AllowMove
        map.AllowMove = MapAllowMove
        g_Func['item.GetWeaponShape'] = item.GetWeaponShape
        item.GetWeaponShape = GetWeaponShape
        dlgpet.g_PetDialog = CVirSumonStateDlg()
        dlgpet.ShowSwitch()
        self.DelMapGoToAni()
        self.ShieldGameBuff()
        self.ChangePlayerCB()
        surviverdefine.LogSurvive('\xb4\xc0\xb4\xab\xa8\xe7\xbc\xc6\xa6\xa8\xa5\\')

    
    def ReChangeGameFun(self):
        '''
\t\t\xc1\xd9\xad\xec\xb4\xc0\xb4\xab
\t\t'''
        global g_Func
        if not g_Func:
            return None
        
        self.ChangeMainMenu(False)
        mapani.CAni.SetAniShow = g_Func['mapani.CAni.SetAniShow']
        warui.UseItem = g_Func['warui.UseItem']
        map.AllowMove = g_Func['map.AllowMove']
        item.GetWeaponShape = g_Func['item.GetWeaponShape']
        dlgpet.g_PetDialog = None
        self.ReChangePlayerCB()
        g_Func = { }
        surviverdefine.LogSurvive('\xb8\xd1\xb0\xa3\xb4\xc0\xb4\xab\xa8\xe7\xbc\xc6\xa6\xa8\xa5\\')

    
    def ChangeMainMenu(self, bIsChange):
        '''\xa5D\xae\xd8\xac[\xb4\xc0\xb4\xab'''
        if hasattr(mainmenu.g_MainMenu, 'm_IsWar'):
            bIsWar = mainmenu.g_MainMenu.m_IsWar
        else:
            bIsWar = False

    
    def GameWarStart(self):
        '''\xb9C\xc0\xb8\xb6}\xa9l\xa1A\xb6i\xa4J\xa5\xbf\xa6\xa1\xb9C\xc0\xb8\xa4j\xc6U'''
        self.CloseGameTips()
        self.CloseClassDlg()
        self.ShowPlayerNumPal()

    
    def GameNotChooseRole(self):
        '''\xa5\xbc\xbf\xef\xbe\xdc\xa8\xa4\xa6\xe2'''
        self.OpenClassDlg()
        self.ShowGameTips()
        self.ClosePlayerNumPal()
        survivemgr.GetSurviveMgr().GameClear()

    
    def GameChooseRole(self):
        '''\xbf\xef\xbe\xdc\xa8\xa4\xa6\xe2\xa7\xb9\xa6\xa8'''
        self.CloseClassDlg()
        self.ShowGameTips()
        self.ClosePlayerNumPal()

    
    def ShieldGameBuff(self):
        '''\xab\xcc\xbd\xaaBuff\xc5\xe3\xa5\xdc\xa1A\xb6\xc8\xabO\xafd\xb9C\xc0\xb8\xa4\xa4\xaa\xbaBuff'''
        import netstate
        for iState in netstate.g_State.keys():
            if iState not in surviverdefine.BUFF_LIST:
                netstate.StateRemove(iState)
                continue
        

    
    def ChangePlayerCB(self):
        player.AddPlayerCB('CPlayer.RightDown', PlayerRightDown)
        player.AddPlayerCB('CPlayer.Enter', PlayerEnter)
        player.AddPlayerCB('CPlayer.Leave', PlayerLeave)

    
    def ReChangePlayerCB(self):
        player.DelPlayerCB('CPlayer.RightDown')
        player.DelPlayerCB('CPlayer.Enter')
        player.DelPlayerCB('CPlayer.Leave')

    
    def OpenWorldMap(self):
        '''\xc5\xe3\xa5\xdc\xa5@\xac\xc9\xa6a\xb9\xcf\xac\xc9\xad\xb1'''
        if not survivemgr.GetSurviveMgr().IsInGameWarMap():
            usermacro.PROMPT_MSG(surviverdefine.MSG_OPEN_WORLD_MAP)
            return None
        
        if not self.m_WorldMapDlg:
            self.m_WorldMapDlg = CNewWorldMap()
            self.m_WorldMapDlg.Topmost()
        

    
    def CloseWorldMap(self):
        '''\xc3\xf6\xb3\xac\xa5@\xac\xc9\xac\xc9\xad\xb1'''
        if self.m_WorldMapDlg:
            self.m_WorldMapDlg = None
        

    
    def SwichWorldMap(self):
        '''\xa5@\xac\xc9\xa6a\xb9\xcf\xa4\xc1\xb4\xab'''
        if self.m_WorldMapDlg:
            self.CloseWorldMap()
        else:
            self.OpenWorldMap()

    
    def OpenPlayerInfoDlg(self, sPid, sName, iShape):
        '''\xc5\xe3\xa5\xdc\xa8\xe4\xa5L\xaa\xb1\xaea\xabH\xae\xa7\xbc\xc6\xbe\xda'''
        import netsurvive
        if not self.m_PlayerInfoDlg:
            netsurvive.C2SAskPlayerInfo(sPid)
            self.m_PlayerInfoDlg = CInfoDialog(sPid, sName, iShape)
            self.m_PlayerInfoDlg.Topmost()
        

    
    def ClosePlayerInfoDlg(self):
        '''\xc3\xf6\xb3\xac\xa8\xe4\xa5L\xaa\xb1\xaea\xabH\xae\xa7\xbc\xc6\xbe\xda'''
        if self.m_PlayerInfoDlg:
            self.m_PlayerInfoDlg = None
        

    
    def UpdatePlayerLevel(self, sPid, iLv):
        if self.m_PlayerInfoDlg:
            self.m_PlayerInfoDlg.SetGrade(sPid, iLv)
        

    
    def OpenWorldBagDlg(self):
        '''\xc5\xe3\xa5\xdc\xa6a\xb9\xcf\xadI\xa5]\xac\xc9\xad\xb1'''
        if not g_VirBagDlg or not g_VirBagDlg.GetShow():
            SwitchVirBagDlg()
        
        if not self.m_WorldBagDlg:
            self.m_WorldMapDlg = CWorldBagDlg(g_VirBagDlg)
            self.m_WorldMapDlg.SetDefaultPos()
        

    
    def CloseWorldBagDlg(self):
        '''\xc3\xf6\xb3\xac\xa6a\xb9\xcf\xadI\xa5]\xac\xc9\xad\xb1'''
        if self.m_WorldMapDlg:
            self.m_WorldMapDlg = None
        

    
    def IsOpenWorldBagDlg(self):
        '''\xbe\xd4\xb3\xf5\xadI\xa5]\xacO\xa7_\xa5\xb4\xb6}'''
        if self.m_WorldMapDlg:
            return True
        else:
            return False

    
    def OpenClassDlg(self):
        '''\xc5\xe3\xa5\xdc\xbf\xef\xbe\xdc\xacy\xac\xa3\xac\xc9\xad\xb1'''
        if survivemgr.GetSurviveMgr().GetGameStartFlag() == surviverdefine.TYPE_GAME_CHOOSE_ROLE:
            pass
        
        if not self.m_ClassChooseDlg:
            self.m_ClassChooseDlg = CClassChooseDlg()
            interface.Center(self.m_ClassChooseDlg)
            self.m_ClassChooseDlg.Topmost()
        

    
    def CloseClassDlg(self):
        '''\xc3\xf6\xb3\xac\xbf\xef\xbe\xdc\xacy\xac\xa3\xac\xc9\xad\xb1'''
        if self.m_ClassChooseDlg:
            self.m_ClassChooseDlg = None
        

    
    def ShowSurviveAdviceDlg(self):
        '''\xc5\xe3\xa5\xdc\xb7N\xa8\xa3\xa4\xcf\xf5X\xac\xc9\xad\xb1'''
        self.m_SurviveAdviceDlg = CSurviveAdviceDlg()
        interface.Center(self.m_SurviveAdviceDlg)

    
    def CloseSurviveAdviceDlg(self):
        '''\xc3\xf6\xb3\xac\xb7N\xa8\xa3\xa4\xcf\xf5X\xac\xc9\xad\xb1'''
        self.m_SurviveAdviceDlg = None

    
    def ShowGameTips(self):
        '''\xc5\xe3\xa5\xdc\xa5\xaa\xa4W\xa8\xa4\xaa\xbaTips\xabH\xae\xa7'''
        self.CloseGameTips()
        bIsMatch = survivemgr.GetSurviveMgr().GetGameMatchFlag()
        dlgminipanel.g_MiniPanel = CSurvivePanel(interface.CoverPanel, bIsMatch, True)

    
    def CloseGameTips(self):
        '''\xc3\xf6\xb3\xac\xa5\xaa\xa4W\xa8\xa4\xaa\xbaTips\xabH\xae\xa7'''
        import dlgminipanel
        if dlgminipanel.g_MiniPanel:
            dlgminipanel.g_MiniPanel.ClosePanel()
            dlgminipanel.g_MiniPanel = None
        

    
    def ShowPlayerNumPal(self):
        '''\xc5\xe3\xa5\xdc\xb9C\xc0\xb8\xa4\xa4\xb3\xd1\xbel\xaa\xb1\xaea\xabH\xae\xa7'''
        self.m_PlayerNumPal = CPlayerNumPalDlg()

    
    def ClosePlayerNumPal(self):
        '''\xc3\xf6\xb3\xac\xb9C\xc0\xb8\xa4\xa4\xb3\xd1\xbel\xaa\xb1\xaea\xabH\xae\xa7'''
        self.m_PlayerNumPal = None

    
    def ShowGameOverDlg(self):
        '''\xa5\xb4\xb6}\xb5\xb2\xba\xe2\xac\xc9\xad\xb1'''
        if not self.m_GameOverDlg:
            self.m_GameOverDlg = CGameOverDlg()
            interface.Center(self.m_GameOverDlg)
            self.m_GameOverDlg.Topmost()
        

    
    def CloseGameOverDlg(self):
        '''\xc3\xf6\xb3\xac\xb5\xb2\xba\xe2\xac\xc9\xad\xb1'''
        if self.m_GameOverDlg:
            self.m_GameOverDlg = None
        

    
    def DelMapInFo(self, *args):
        '''\xac\xa1\xb0\xca\xab\xcc\xbd\xaa\xa4p\xa6a\xb9\xcf\xa4W\xaa\xba\xa4\xe5\xa5\xbb'''
        self.m_DelTimer.Release()
        self.m_DelTimer = None
        self.DelMapGoToAni()
        PRINT(args)

    
    def ShowMinimap(self):
        '''\xa5\xb4\xb6}\xa4p\xa6a\xb9\xcf'''
        import map
        if not (self.m_MiniMapDlg) and map.GetGameMapObject():
            (iMapW, iMapH) = map.GetGameMapObject().GetSize()
            self.m_MiniMapDlg = CMinimap(interface.DialogPanel, map.GetCurrentSceneID(), map.GetCurrentMapID(), map.GetCurrentMiniMapID(), iMapW, iMapH, map.g_Map.m_Virtual)
            self.m_MiniMapDlg.Topmost()
        
        self.m_MiniMapDlg.AskSuperBoxInfo()
        self.m_MiniMapDlg.CloseSuperBox()

    
    def CloseMinimap(self):
        '''\xc3\xf6\xb3\xac\xa4p\xa6a\xb9\xcf'''
        self.m_MiniMapDlg = None

    
    def SwitchMinimap(self):
        if not self.m_MiniMapDlg:
            self.ShowMinimap()
        else:
            self.m_MiniMapDlg.SetShow(not self.m_MiniMapDlg.GetShow())
            if self.m_MiniMapDlg.GetShow():
                self.m_MiniMapDlg.AskSuperBoxInfo()
                self.m_MiniMapDlg.CloseSuperBox()
            

    
    def ShowUseItemForEquitDlg(self, iUesItemID, iUesItemShape):
        '''\xa5\xb4\xb6}\xb9\xef\xaa\xab\xab~\xa8\xcf\xa5\xce\xaa\xba\xb9\xef\xb8\xdc\xae\xd8'''
        if not self.m_UseItemForEquitDlg:
            self.m_UseItemForEquitDlg = CUseItemForEquitDlg()
        
        self.m_UseItemForEquitDlg.SetUseItemID(iUesItemID, iUesItemShape)

    
    def CloseUseItemForEquitDlg(self):
        '''\xc3\xf6\xb3\xac\xb9\xef\xaa\xab\xab~\xa8\xcf\xa5\xce\xaa\xba\xb9\xef\xb8\xdc\xae\xd8'''
        self.m_UseItemForEquitDlg = None

    
    def DelMapGoToAni(self):
        import mapani
        for iAni in range(len(mapani.g_MapAniObjects)):
            oAni = mapani.g_MapAniObjects[iAni]
            if oAni and isinstance(oAni, mapani.CAni) and oAni.GetFileName() == surviverdefine.TYPE_GO_TO_MARK:
                mapani.g_MapAniObjects[iAni] = None
                continue
        

    
    def GetVirStateDlg(self):
        return self.m_VirStateDlg

    
    def SwichVirStateDlg(self):
        if dlgstate.g_StateDialog:
            dlgstate.g_StateDialog = None
        
        if not self.m_VirStateDlg:
            self.m_VirStateDlg = CVirStateDlg()
            self.m_VirStateDlg.Topmost()
        else:
            self.m_VirStateDlg = None

    
    def ShowQuickOperateTips(self):
        self.m_QuickOperateTips = CQuickOperateTips()
        self.m_QuickOperateTips.SetPos(21, 287)

    
    def CloseQuickOperateTips(self):
        self.m_QuickOperateTips = None

    
    def ShowQuickOperateDlg(self):
        if survivemgr.GetSurviveMgr().GetGameStartFlag() in [
            surviverdefine.TYPE_GAME_NOT_CHOOSE_ROLE,
            surviverdefine.TYPE_GAME_END]:
            usermacro.PROMPT_MSG('\xa8\xa4\xa6\xe2\xbf\xef\xbe\xdc\xa7\xb9\xa6\xa8\xab\xe1\xa4~\xaf\xe0\xb6i\xa6\xe6\xb8\xd3\xbe\xde\xa7@')
            return None
        
        if mainmenu.IsWar():
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xa7\xd6\xb1\xb6\xb3]\xb8m')
            return None
        
        self.m_QuickOperateDlg = CQuickOperateDlg()
        interface.Center(self.m_QuickOperateDlg)

    
    def CloseQuickOperateDlg(self):
        self.m_QuickOperateDlg = None

    
    def ShortcutSkillChange(self, iSkillType, iSkillID, iSkillLevel):
        '''\xa7\xde\xaf\xe0\xa7\xd6\xb1\xb6\xc4\xe6\xaa\xba\xb5o\xa5\xcd\xc5\xdc\xa4\xc6'''
        oSkillData = shortcut.CShortcutMgr.GetSchemeData(shortcut.SHORTCUT_SURVIVE, surviverdefine.SHORTCUT_SKILL_PAGE)
        oItemData = shortcut.CShortcutMgr.GetSchemeData(shortcut.SHORTCUT_SURVIVE, surviverdefine.SHORTCUT_ITEM_PAGE)
        oSkillData = copy.deepcopy(oSkillData)
        oItemData = copy.deepcopy(oItemData)
        for iPos in oItemData.keys():
            oItemData[iPos + 8] = oItemData[iPos]
            del oItemData[iPos]
        
        if iSkillLevel == 0:
            for iPos in oSkillData.keys():
                if iSkillID == oSkillData[iPos][1]:
                    del oSkillData[iPos]
                    break
                    continue
            
        elif iSkillType != hero.ST_MAGICREADY:
            return None
        else:
            iPosLise = range(8)
            for iPos in oSkillData.keys():
                if oSkillData[iPos][0] == 255:
                    continue
                
                iPosLise.remove(iPos)
                if iSkillID == oSkillData[iPos][1]:
                    oSkillData[iPosLise[0]] = oSkillData[iPos]
                    del oSkillData[iPos]
                    break
                    continue
            elif iPosLise:
                oSkillData[iPosLise[0]] = (shortcut.TYPE_MAGIC, iSkillID, 0)
            
        oData = { }
        oData.update(oSkillData)
        oData.update(oItemData)
        shortcut.CShortcutMgr.InitShortcutsData(shortcut.SHORTCUT_SURVIVE, oData)
        if not mainmenu.IsWar():
            shortcut.CShortcutMgr.SetCurScheme(shortcut.SHORTCUT_SURVIVE, 1)
        

    
    def ShowHPAdd(self, iProSent, iStep):
        '''\xa5[\xa6\xe5\xae\xc4\xaaG'''
        if mainmenu.IsWar():
            return None
        
        if iStep == 1:
            oHero = hero.GetHeroObject()
            netmap.PlayMagicEffect(oHero, 2702, -104, 0)
        
        iNum = hero.GetProp('m_HPMax', 0)
        iNowHp = hero.GetProp('m_HP', 0)
        self.m_iLastHP = iNowHp
        if iNowHp == iNum:
            return None
        
        if survivemgr.GetSurviveMgr().IsInSurviveGame():
            oTxtObj = mxnumbers.CNumber(hero.GetHeroObject(), 'hp', iNum * iProSent / 1000)
            (_, iH) = hero.g_Hero.GetSize()
            oTxtObj.SetPos(0, -iH - 20)
        

    
    def ShowHeroHpChange(self, iProSent):
        '''\xb1\xbc\xa6\xe5\xa7\xef\xc5\xdc'''
        if mainmenu.IsWar():
            return None
        
        iNum = hero.GetProp('m_HPMax', 0)
        oMgr = survivemgr.GetSurviveMgr()
        iMapID = map.GetCurrentMapID()
        iMapPos = surviverdefine.GetSceneIDWithMapID(iMapID)
        iWeather = oMgr.GetWeatherData(iMapPos)
        if iWeather == surviverdefine.TYPE_WEATHER_SNOW:
            oTxtObj = mxnumbers.CNumber(hero.g_Hero, 'hit', iNum * iProSent / 1000)
            (_, iH) = hero.g_Hero.GetSize()
            oTxtObj.SetPos(0, -iH - 20)
            oTxtObj.m_oBoxObject = interface.CBoxObject(interface.TopmostPanel, ratio.WINDOW_WIDTH, ratio.WINDOW_HEIGHT, interface.COLOR_25, 48)
        

    
    def ShowCollideEffect(self, iScene, iPosX, iPosY, iSID, iGID):
        '''\xc5\xe3\xa5\xdc\xbdd\xb3\xf2\xae\xc4\xaaG \xb3\xb7\xa4k \xa4\xf5\xb5K'''
        if not map.GetGameMapObject():
            return None
        
        oSnowGirlCtrl = CSnowGirlCtrl(iPosX, iPosY)
        oSnowGirlCtrl.SetDisInfo(iSID, iGID, iScene)
        oSnowGirlCtrl.InitSnowGirl()
        oSnowGirlCtrl.OnHeroPosChange(*map.GetGameMapObject().ClientPos2ServerPos(*hero.GetHeroPos()))
        self.m_CollideEffectData[iGID] = oSnowGirlCtrl
        if iSID == surviverdefine.TYPE_SNOW_GIRL:
            self.ShowSnowGril(iScene, iPosX, iPosY, surviverdefine.TYPE_MAP_SNOW_GIRL)
        

    
    def CloseCollideEffect(self, iGID):
        '''\xa7R\xb0\xa3\xae\xc4\xaaG'''
        if iGID in self.m_CollideEffectData:
            oSnowGirlCtrl = self.m_CollideEffectData[iGID]
            iSID = oSnowGirlCtrl.m_iEff
            oSnowGirlCtrl.Clear()
            self.m_CollideEffectData[iGID] = None
            del self.m_CollideEffectData[iGID]
            if iSID == surviverdefine.TYPE_SNOW_GIRL:
                self.CloseSnowGril(surviverdefine.TYPE_MAP_SNOW_GIRL)
            
        

    
    def ShowSnowGril(self, iScene, iPosX, iPosY, iType):
        '''\xc5\xe3\xa5\xdc\xb3\xb7\xa4k\xa6b\xa4p\xa6a\xb9\xcf\xa4W'''
        if not self.m_MiniMapDlg:
            self.ShowMinimap()
            self.SwitchMinimap()
        
        if iType == surviverdefine.TYPE_MAP_SNOW_GIRL:
            self.m_bIsShowSnowGril = True
            self.m_MiniMapDlg.ShowSnowGril(iScene, iPosX, iPosY)
            if self.m_PlayerNumPal:
                self.m_PlayerNumPal.SetTimeText()
            
        elif iType == surviverdefine.TYPE_MAP_SUPER_BOX:
            self.m_MiniMapDlg.ShowSuperBox(iScene, iPosX, iPosY)
        

    
    def CloseSnowGril(self, iType):
        '''\xa7R\xb0\xa3\xb3\xb7\xa4k\xa6b\xa4p\xa6a\xb9\xcf\xa4W'''
        if iType == surviverdefine.TYPE_MAP_SNOW_GIRL:
            self.m_bIsShowSnowGril = False
            if self.m_MiniMapDlg:
                self.m_MiniMapDlg.CloseSnowGril()
            
        elif iType == surviverdefine.TYPE_MAP_SUPER_BOX:
            if self.m_MiniMapDlg:
                self.m_MiniMapDlg.CloseSuperBox()
            
        

    
    def HotKey(self, IsWar):
        hotkeys = dlgsysopt.g_HotKeys
        if not IsWar:
            key.RegisterHotKey(hotkeys['\xa5\xe6\xa9\xf6'])
            key.RegisterHotKey(hotkeys['\xb5\xb9\xa4\xa9'])
            key.RegisterHotKey(hotkeys['\xa7\xde\xaf\xe0\xac\xc9\xad\xb1'])
            key.RegisterHotKey(hotkeys['\xa5\xf4\xb0\xc8\xac\xc9\xad\xb1'])
            key.RegisterHotKey(hotkeys['\xb6\xa4\xa5\xee\xac\xc9\xad\xb1'])
            key.RegisterHotKey(hotkeys['\xc0\xb0\xac\xa3\xac\xc9\xad\xb1'])
            key.RegisterHotKey(hotkeys['\xa4\xdb\xa4\xc6'])
            key.RegisterHotKey(hotkeys['\xa6\xa8\xb4N'])
            key.RegisterHotKey(hotkeys['\xa7\xa4\xc3M\xac\xc9\xad\xb1'])
        

    
    def ShowMagic(self, iID, iTime):
        '''\xc5\xe3\xa5\xdc\xafS\xae\xc4'''
        oGoods = world.GetObj(iID)
        if not oGoods:
            return None
        
        if not map.GetGameMapObject():
            return None
        
        (iPosX, iPosY) = oGoods.GetPos()
        iLastTime = iTime - misc.GetServerCurrentTime()
        if iLastTime <= 0:
            return None
        
        self.m_oSuperBoxMagic = CSuperBoxMagicCtrl()
        self.m_oSuperBoxMagic.SetLastTime(iLastTime)
        self.m_oSuperBoxMagic.StartMagic(iPosX, iPosY)

    
    def OnGameFlagChange(self, iFlag):
        '''\xb9C\xc0\xb8\xacy\xb5{\xac\xdb\xc3\xf6\xa6^\xbd\xd5\xa1A\xad\xab\xadn\xaa\xba\xacy\xb5{\xa8\xe7\xbc\xc6'''
        if not surviverdefine.IS_OPEN_SURVIVE:
            return None
        
        surviverdefine.LogSurvive('\xb9C\xc0\xb8\xaa\xac\xbaA\xc5\xdc\xa7\xf3', iFlag)
        if iFlag in surviverdefine.TYPE_GAME_IN_GAME_LIST:
            self.GameInit()
        else:
            self.GameEnd()
        if iFlag == surviverdefine.TYPE_GAME_NOT_CHOOSE_ROLE:
            self.GameNotChooseRole()
        elif iFlag == surviverdefine.TYPE_GAME_CHOOSE_ROLE:
            self.GameChooseRole()
        elif iFlag == surviverdefine.TYPE_GAME_START:
            self.GameWarStart()
        

    
    def OnSceneChange(self, iScene, iMapID, iMiniMapID):
        self.m_DelTimer = interface.CBaseObject(None)
        self.m_DelTimer.CreatePyCommand(2, self.DelMapInFo)
        self.CloseWorldMap()
        if self.m_PlayerNumPal:
            self.m_PlayerNumPal.InitData()
            self.m_PlayerNumPal.InitTest()
        
        for iGID in self.m_CollideEffectData.keys():
            self.CloseCollideEffect(iGID)
        
        PRINT(iScene, iMapID, iMiniMapID)

    
    def OnGameMatchFlagChange(self, iGameMatchFlag):
        if survivemgr.GetSurviveMgr().GetGameStartFlag() in [
            surviverdefine.TYPE_GAME_NOT_CHOOSE_ROLE,
            surviverdefine.TYPE_GAME_CHOOSE_ROLE]:
            self.ShowGameTips()
        
        PRINT(iGameMatchFlag)

    
    def OnGameOpenWolrdBag(self, iWolrdBagID):
        if iWolrdBagID and not (self.m_WorldMapDlg):
            self.OpenWorldBagDlg()
        else:
            import handobj
            if handobj.GetHand(handobj.TYPE_VIR_ITEM) or handobj.GetHand(handobj.TYPE_BAGS):
                handobj.Clear()
            
            self.CloseWorldBagDlg()

    
    def OnAbandonItems(self, oHand):
        import handobj
        import misc
        import commondialog
        if oHand.m_Type == handobj.TYPE_VIR_ITEM:
            
            def DoDrop(iItemPos, dlg):
                import netitem
                netitem.C2SVirItemDrag(iItemPos, 0)
                PRINT(dlg)

            handobj.Accept()
            it = item.GetItem(oHand.m_ID)
            it.SetHide(False)
            item.ShowItem(it.m_Type, it.m_Pos)
            commondialog.ShowMessageBox('\xb1z\xbdT\xa9w\xadn\xa5\xe1\xb1\xf3\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(DoDrop, it.m_Pos), None), stopMove = False)
        elif oHand.m_Type == handobj.TYPE_BAGS:
            handobj.Accept()
            it = item.g_Items[item.ITEM_BAGS].get(oHand.m_BagID, { }).get(oHand.m_Pos)
            it.SetHide(False)
            item.ShowItem(item.ITEM_BAGS, oHand.m_Pos, oHand.m_BagID)
            usermacro.PROMPT_MSG('\xa4\xa3\xaf\xe0\xa5\xe1\xb1\xf3\xaa\xab\xab~')
        elif oHand.m_Type == handobj.TYPE_HOTKEYICON:
            handobj.Accept()
            if shortcut.CShortcutMgr.GetCurShortcutType() == shortcut.SHORTCUT_SURVIVE:
                usermacro.PROMPT_MSG('\xb7\xed\xabe\xac\xa1\xb0\xca\xa4\xa3\xaf\xe0\xa8\xfa\xae\xf8\xb3]\xb8m')
            
        

    
    def OnGameEndInfo(self, dGameEndInfo):
        self.ShowGameOverDlg()
        PRINT(dGameEndInfo)

    
    def OnStateChange(self, iStateID, bAddFlag):
        import netstate
        bAddFlag
        if iStateID not in surviverdefine.BUFF_LIST:
            netstate.StateRemove(iStateID)
            return None
        

    
    def OnSetHeroPhoto(self):
        import hero
        import avatar
        iShape = hero.g_Prop.m_Shape
        avatar.g_DefaultPhoto = [
            14,
            238,
            238,
            iShape,
            14,
            238,
            238,
            238,
            14,
            238,
            238,
            238,
            14,
            238,
            238,
            238]
        hero.g_PropPhoto = None
        if self.m_MiniMapDlg:
            self.m_MiniMapDlg.RefreshHeroIcon()
        
        if self.m_VirStateDlg:
            self.m_VirStateDlg.RefreshPhoto()
        
        if mainmenu.g_MainMenu:
            mainmenu.g_MainMenu.m_HeroFrame.UpdateIcon()
        

    
    def OnHeroHPChange(self):
        pass

    
    def OnHeroClassChange(self):
        iClass = hero.GetProp('m_Class', 0)
        if iClass != 0:
            setattr(hero.g_Prop, 'm_Class', 0)
        

    
    def OnWarSwitch(self, IsWar):
        if not survivemgr.GetSurviveMgr().IsInSurviveGame():
            return None
        
        
        try:
            warui.ShowMagicShortKey(iShortcutType = shortcut.SHORTCUT_SURVIVE)
            if not g_VirBagDlg:
                SwitchVirBagDlg()
                SwitchVirBagDlg()
            
            if not IsWar:
                shortcut.CShortcutMgr.SetCurScheme(shortcut.SHORTCUT_SURVIVE, 1)
            else:
                shortcut.CShortcutMgr.SetCurScheme(shortcut.SHORTCUT_SURVIVE, 0)
                self.CloseWorldMap()
                self.CloseMinimap()
                self.CloseWorldBagDlg()
                self.CloseQuickOperateDlg()
            self.HotKey(IsWar)
        except:
            LOG_EXC('\xac\xa1\xb0\xca\xa4\xa4\xa4\xc1\xb4\xab\xbe\xd4\xb0\xab\xa5X\xb2{\xb0\xdd\xc3D')


    
    def OnItemChange(self):
        oSkillData = shortcut.CShortcutMgr.GetSchemeData(shortcut.SHORTCUT_SURVIVE, surviverdefine.SHORTCUT_SKILL_PAGE)
        oSkillData = copy.deepcopy(oSkillData)
        iShapeList = []
        for oItem in item.g_Items[item.ITEM_VIR_BAGS].values():
            if oItem.m_Shape not in skillicondata.ITEM_DATA:
                continue
            
            iShapeList.append(oItem.m_Shape)
        
        iShapeList = set(iShapeList)
        oData = shortcut.CShortcutMgr.GetSchemeData(shortcut.SHORTCUT_SURVIVE, surviverdefine.SHORTCUT_ITEM_PAGE)
        oData = copy.deepcopy(oData)
        iValuseData = { }
        for iPos in oData.keys():
            tValue = oData[iPos]
            iValuseData[tValue[1]] = iPos + 8
            del oData[iPos]
            oData[iPos + 8] = tValue
        
        iAddSet = iShapeList - set(iValuseData.keys())
        iDelSet = set(iValuseData.keys()) - iShapeList
        for iDelShape in iDelSet:
            iDelPos = iValuseData[iDelShape]
            shortcut.CShortcutMgr.RemoveHotkey(shortcut.SHORTCUT_SURVIVE, iDelPos)
            del oData[iDelPos]
        
        iSetPos = list(set(range(8, 16)) - set(oData.keys()))
        iSetPos.sort()
        for iAddShapeID in iAddSet:
            
            try:
                oData[iSetPos[0]] = (shortcut.TYPE_SURVIVE, iAddShapeID, 0)
                iSetPos.pop(0)
            continue
            break
            continue

        
        oData.update(oSkillData)
        shortcut.CShortcutMgr.InitShortcutsData(shortcut.SHORTCUT_SURVIVE, oData)
        if not mainmenu.IsWar():
            shortcut.CShortcutMgr.SetCurScheme(shortcut.SHORTCUT_SURVIVE, 1)
        else:
            shortcut.CShortcutMgr.SetCurScheme(shortcut.SHORTCUT_SURVIVE, 0)

    
    def OnSkillUpdateCallBack(self, iSkillType, iSkillID, iSkillLevel):
        self.ShortcutSkillChange(iSkillType, iSkillID, iSkillLevel)

    
    def OnTransparentTrap(self, oGoods):
        oGoods.m_oShowBox = interface.CBoxObject(oGoods, 100, 100, interface.COLOR_25, 255)



class CLookInfoItem(popmenu.CItemBase):
    
    def GetText(self, *args):
        return '\xacd\xac\xdd\xabH\xae\xa7'

    
    def OnClick(self, oMenu):
        GetGameSurviveCtrl().OpenPlayerInfoDlg(oMenu.m_ObjectID, oMenu.m_ObjectName, oMenu.m_ShapeID)



class CInfoDialog(combdialog.CCombDialog):
    '''
\t\xaa\xfe\xaa\xf1\xa4H\xabH\xae\xa7\xb9\xef\xb8\xdc\xae\xd8
\t'''
    
    def __init__(self, pid, sName, iShape):
        self.m_iPID = pid
        self.m_sName = sName
        self.m_iGrade = 0
        self.m_iShape = iShape
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/friend/stranger.dlg')
        interface.Center(self)
        self.m_Photo = None
        self.m_Items = []
        self.InitDlg()

    
    def InitDlg(self):
        sNotValidList = [
            'btn_zhanyou',
            'btn_haoyou',
            'txtbadge1',
            'txtbadge2',
            'ps_btn',
            'showmyq',
            'showblog']
        for sName in sNotValidList:
            self.GetObject(sName).SetShow(False)
        
        self.SetAvatar()
        self.RefreshInfo()

    
    def SetGrade(self, iPid, iGrade):
        '''\xb3]\xb8m\xb5\xa5\xaf\xc5'''
        if iPid != self.m_iPID:
            raise surviverdefine.ServerError('\xb5o\xb0e\xaa\xbaID\xa4\xa3\xa4\xc7\xb0t')
        
        self.m_iGrade = iGrade
        self.RefreshInfo()

    
    def SetAvatar(self):
        '''\xb3]\xb8m\xc0Y\xb9\xb3'''
        iArrList = [
            14,
            238,
            238,
            self.m_iShape,
            14,
            238,
            238,
            238,
            14,
            238,
            238,
            238,
            14,
            238,
            238,
            238]
        self.m_Photo = avatar.CBigAvatarImg(self.GetObject('box_icon'), iArrList)
        self.m_Photo.SetPos(7, 6)

    
    def RefreshInfo(self):
        sTxtList = [
            str(self.m_iPID),
            self.m_sName,
            '%d\xaf\xc5' % self.m_iGrade,
            '\xbe\xd4\xa4h']
        sUIName = ('txt_id', 'txt_name', 'txt_grade', 'txt_class')
        self.m_Items = []
        for idx, t in enumerate(sTxtList):
            if t is not None and self.GetObject(sUIName[idx]):
                self.m_Items.append(combmacro.CRICHTEXT(interface.CRichTextObject, sUIName[idx], self, t, interface.FontLT14_3, interface.COLOR_9))
                continue
        

    
    def OnMessage(self, msgid):
        if msgid == 2:
            GetGameSurviveCtrl().ClosePlayerInfoDlg()
        else:
            usermacro.PROMPT_MSG(surviverdefine.MSG_OPERATOR_ERROR)



def PopTargetMenu(parent, x, y, targetID, name, iShowMask = 0):
    itemList = []
    popmenu.CGMForbidSayItem(itemList)
    popmenu.CSendMessage(itemList, targetID)
    popmenu.CMakeFrdItem(itemList, targetID)
    popmenu.CMakeAcountFrdItem(itemList, targetID)
    popmenu.CMakeTempFrdItem(itemList, targetID)
    popmenu.CActionItem(itemList)
    popmenu.CReportItem(itemList)
    popmenu.CIntroduceGroupItem(itemList, targetID)
    CLookInfoItem(itemList)
    popmenu.CLookFightItem(itemList, targetID)
    popmenu.CFightItem(itemList, iShowMask)
    oPopObj = wrapinterface.CMenuList(parent, itemList, x, y)
    oPopObj.m_ObjectID = targetID
    oPopObj.m_ObjectName = name
    oPopObj.m_Channel = 0
    oPopObj.SetRightUpShield(True)
    return oPopObj


class CTargetPngFrame(mainmenu.CTargetPngFrame):
    
    def CreatePopMenu(self):
        (x, y) = self.GetPos()
        (offsetX, offsetY) = None if interface.IsNewStyle() else (0, 0)
        self.m_PopMenu = PopTargetMenu(interface.DialogPanel, x + offsetX + 4, y + offsetY + 44, self.m_ObjectID, self.m_ObjectName, iShowMask = 2)
        if self.m_PopMenu:
            self.m_PopMenu.Capture(0, 0)
            self.m_PopMenu.SetZ(-1)
            accountID = getattr(self, 'm_AccountID', None)
            oPlayer = world.GetObj(self.m_ObjectID)
            if oPlayer:
                self.m_PopMenu.m_ShapeID = oPlayer.m_Shape
            else:
                self.m_PopMenu.m_ShapeID = 111
            if accountID:
                self.m_PopMenu.m_AccountID = accountID
            
        



class CTargetFrame(mainmenu.CTargetFrame):
    
    def CreatePopMenu(self):
        (x, y) = self.GetPos()
        self.m_PopMenu = PopTargetMenu(interface.DialogPanel, x + 4, y + 44, self.m_ObjectID, self.m_ObjectName, iShowMask = 2)
        if self.m_PopMenu:
            self.m_PopMenu.Capture(0, 0)
            self.m_PopMenu.SetZ(-1)
            world.GetObj(self.m_ObjectID)
            oPlayer = world.GetObj(self.m_ObjectID)
            if oPlayer:
                self.m_PopMenu.m_ShapeID = oPlayer.m_Shape
            else:
                self.m_PopMenu.m_ShapeID = 111
            accountID = getattr(self, 'm_AccountID', None)
            if accountID:
                self.m_PopMenu.m_AccountID = accountID
            
        



class CMainMenu(mainmenu.CMainMenu):
    
    def ShowTarget(self, target):
        import ratio
        if ratio.Is1024x768():
            (x, y) = (716, 61)
        elif ratio.Is1366x768() or ratio.Is1366x708():
            (x, y) = (1058, 61)
        elif ratio.Is1280x960():
            (x, y) = (972, 253)
        else:
            (x, y) = (492, 61)
        if target is not None:
            targetClass = None if interface.IsNewStyle() else CTargetFrame
            self.m_Target = targetClass(self, target, x, y)
        else:
            self.m_Target = None



class CSurvivePanel(dlgminipanel.CMiniPanel):
    TYPE2STATE = {
        0: '\xb7\xc7\xb3\xc6\xa4\xa4***',
        1: '\xa4\xc7\xb0t\xa4\xa4***' }
    ID2NAME = {
        0: '#u\xa5[\xa4J\xa4\xc7\xb0t#n',
        1: '#u\xa8\xfa\xae\xf8\xa4\xc7\xb0t#n',
        3: '#u\xb0e\xa7\xda\xa5X\xb3\xf5#n' }
    
    class CClickText(interface.CClickRichText):
        
        def LeftUp(self):
            import netsurvive
            if hasattr(self, 'm_ID'):
                if self.m_ID == 1:
                    netsurvive.C2SJoinSurvive(False)
                elif self.m_ID == 0:
                    if survivemgr.GetSurviveMgr().GetGameStartFlag() == surviverdefine.TYPE_GAME_NOT_CHOOSE_ROLE:
                        GetGameSurviveCtrl().OpenClassDlg()
                        return None
                    
                    netsurvive.C2SJoinSurvive(True)
                elif self.m_ID == 3:
                    netsurvive.C2SLeaveActivate()
                elif self.m_ID == 4:
                    GetGameSurviveCtrl().OpenClassDlg()
                elif self.m_ID == 5:
                    GetGameSurviveCtrl().ShowQuickOperateDlg()
                elif self.m_ID == 6:
                    import netsurvive
                    netsurvive.C2SAskGuidelines()
                elif self.m_ID == 7:
                    GetGameSurviveCtrl().ShowSurviveAdviceDlg()
                
            
            interface.CClickRichText.LeftUp(self)


    
    class CTextBox(dlgminipanel.CKuafuMatchPanel.CTextBox):
        
        def __init__(self, parent, showIDList, title):
            self.m_oTimer = None
            self.m_iTimer = 0
            dlgminipanel.CKuafuMatchPanel.CTextBox.__init__(self, parent, showIDList, title)

        
        def CreateClickTexts(self, showIDList):
            self.CreateExtText()
            hSpace = 25
            if '\xa4\xc7\xb0t\xa4\xa4' in self.m_Ext:
                hSpace = 50
            
            parent = self.GetParent()
            for idx, ID in enumerate(showIDList):
                txt = parent.ID2NAME[ID]
                obj = parent.CClickText(self, 0, 15, 100, txt, 2616824, interface.COLOR_25, interface.FontLT12_1)
                obj.m_ID = ID
                obj.SetPos(30, hSpace + 20 * (idx + 1))
                self.m_ClickTextList.append(obj)
            

        
        def CreateExtText(self):
            if '\xa4\xc7\xb0t\xa4\xa4' in self.m_Ext and '\xb7\xed\xabe\xa4\xc7\xb0t' not in self.m_Ext and '\xb9w\xadp\xae\xc9\xb6\xa1' not in self.m_Ext:
                self.m_Ext = self.m_Ext + '#r\xb9w\xadp\xae\xc9\xb6\xa1%d\xac\xed' % survivemgr.GetSurviveMgr().GetMatchTime()
                self.m_Ext = self.m_Ext + '#r\xa4w\xa4\xc7\xb0t%d\xac\xed' % self.m_iTimer
            
            obj = interface.CRichTextObject(self, 300, interface.FontLT12_1, self.m_Ext, 16777215)
            obj.SetPos(30, 25)
            if not getattr(self, 'm_ClickTextList', None):
                self.m_ClickTextList = []
                self.m_ClickTextList.append(obj)
            else:
                self.m_ClickTextList[0] = obj

        
        def ResetSize(self):
            (w, h) = (110, 20)
            hSpace = 25
            if hasattr(self, 'm_ClickTextList') and self.m_ClickTextList:
                for obj in self.m_ClickTextList:
                    if obj.GetShow():
                        h += hSpace
                        continue
                
                if '\xa4\xc7\xb0t\xa4\xa4' in self.m_Ext:
                    h += hSpace
                
            
            self.SetSize(w, h)

        
        def RefreshState(self, state):
            self.ShowClickTexts(state == 1)
            if state == 1:
                if not self.m_oTimer:
                    self.m_iTimer = 0
                    self.m_oTimer = timer.Timer(1, self.OnRefreshState, -1)
                
            elif self.m_oTimer:
                self.m_oTimer.Release()
            
            self.m_oTimer = None
            self.CreateExtText()
            self.ResetSize()
            self.SetAlpha(80)

        
        def OnRefreshState(self):
            self.m_iTimer += 1
            self.CreateExtText()
            self.ResetSize()
            self.SetAlpha(80)

        
        def SetLiuPaiInfo(self, info):
            parent = self.GetParent()
            titleObj = interface.CTextObject(self, '\xa8\xa4\xa6\xe2\xabH\xae\xa7:', interface.FontLT12_1, 16776960, 0)
            infoObj = interface.CTextObject(self, info, interface.FontLT12_1, 16777215, 0)
            openText = parent.CClickText(self, 0, 15, 100, '#u\xbf\xef\xbe\xdc\xacy\xac\xa3', 2616824, interface.COLOR_25, interface.FontLT12_1)
            openText.m_ID = 4
            if not getattr(self, 'm_ClickTextList', None):
                self.m_ClickTextList = []
            elif not getattr(self, 'm_HasLiuPai', None):
                pass
            
            self.m_ClickTextList = self.m_ClickTextList[:-6]
            hSpace = 25
            if '\xa4\xc7\xb0t\xa4\xa4' in self.m_Ext:
                hSpace = 50
            
            iLen = len(self.m_ClickTextList)
            titleObj.SetPos(30, hSpace + 20 * (iLen + 1))
            infoObj.SetPos(30, hSpace + 20 * (iLen + 2))
            openText.SetPos(30, hSpace + 20 * (iLen + 3))
            self.m_ClickTextList.extend([
                titleObj,
                infoObj,
                openText])
            oTextData = {
                5: '\xa7\xd6\xb1\xb6\xbe\xde\xa7@',
                6: '\xb7s\xa4\xe2\xab\xfc\xa4\xde',
                7: '\xb7N\xa8\xa3\xa4\xcf\xf5X' }
            hSpace += 15
            for iID, sTest in oTextData.iteritems():
                oText = parent.CClickText(self, 0, 15, 100, '#u%s' % sTest, 2616824, interface.COLOR_25, interface.FontLT12_1)
                oText.m_ID = iID
                oText.SetPos(30, hSpace + 20 * (iLen + iID - 1))
                self.m_ClickTextList.append(oText)
            
            self.m_HasLiuPai = True


    
    def __init__(self, parent, iState, isShowLink):
        sFrame = '#Y\xa4\xc7\xb0t\xaa\xac\xbaA:#n#r%s' % self.GetState(iState)
        showIDLst = self.GetShowIDLst(iState, isShowLink)
        dlgminipanel.CMiniPanel.__init__(self, parent, showIDLst, sFrame)
        self.SetChangeStateCmd(iState)
        self.RefreshClass()
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateLiuPaiInfo, self.RefreshClass)
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateMatchTime, self.RefreshClass)

    
    def RefreshClass(self, iLiuPai = None):
        if not iLiuPai:
            iLiuPai = survivemgr.GetSurviveMgr().GetLiuPaiInfo()
        
        liuPai = {
            1: '\xbcC\xaak',
            2: '\xa4M\xaak',
            3: '\xb5\xa7\xaak' }.get(iLiuPai, '')
        self.m_TextBox.SetLiuPaiInfo('%s %s' % (liuPai, '\xbe\xd4\xa4h'))
        self.RefreshState()

    
    def GetShowIDLst(self, iState, isShowLink):
        idLst = []
        if isShowLink and iState in self.ID2NAME:
            idLst.append(iState)
        
        idLst.append(3)
        return idLst

    
    def GetState(self, iState, iTurn = 0):
        sState = self.TYPE2STATE.get(iState, '')
        reNewDct = {
            0: '.  ',
            1: '.. ',
            2: '...' }
        reNew = reNewDct.get(iTurn, '.  ')
        return sState.replace('***', reNew)

    
    def SetChangeStateCmd(self, iState):
        self.ReleaseChangeStateCmd()
        
        def doChange(obj, iTurn):
            iTurn = (iTurn + 1) % 3
            sState = obj.GetState(iState, iTurn)
            obj.m_TextBox.ResetExt(sState)
            return (iTurn,)

        self.m_StateCmd = self.CreatePyCommand(10, doChange, 0)

    
    def ReleaseChangeStateCmd(self):
        if getattr(self, 'm_StateCmd', None):
            self.m_StateCmd.Release()
            self.m_StateCmd = None
        

    
    def ClosePanel(self):
        self.ReleaseChangeStateCmd()
        hero.RemoveRefreshCallback('minipanel', (('m_Class', 0, 0), ('m_Liupai', 0, 0)))
        import dlgminipanel
        dlgminipanel.g_MiniPanel = None



class CClassChooseItem(interface.CImagesObject, interface.CBase):
    '''\xc2I\xbf\xef\xacy\xac\xa3\xc3\xfe'''
    
    def __init__(self, oParent, sIgsPath, sPsk):
        interface.CImagesObject.__init__(self, oParent, sIgsPath, sPsk)
        self.MessageProcess()
        self.m_MsgCB = None
        self.m_FlashObj = None

    
    def SetMsgCB(self, oMsgCB):
        self.m_MsgCB = oMsgCB

    
    def SetFlash(self, bFlash):
        if bFlash:
            z = self.GetZ()
            oFlashObj = interface.CStretchSpriteBox(self, 'item44/select.spr', 'item', 0)
            oFlashObj.SetScale(1.2)
            (a, b) = oFlashObj.GetResKey()
            (c, d) = oFlashObj.GetSize()
            oFlashObj.SetPos(c - a, d - b)
            oFlashObj.SetZ(z + 1)
            oFlashObj.CreateCommand(1, 'animation')
        else:
            oFlashObj = None
        self.m_FlashObj = oFlashObj

    
    def LeftUp(self):
        if self.m_MsgCB:
            self.m_MsgCB()
        



class CClassChooseDlg(combdialog.CCombDialog):
    '''\xacy\xac\xa3\xbf\xef\xbe\xdc\xac\xc9\xad\xb1'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_CHOOSE_CLASS)
        self.m_oButtonData = { }
        self.m_iSelectID = None
        self.m_oClassDescRichText = None
        self.m_oFakeRoleWalkerObject = None
        self.m_iRoleWeaponID = None
        self.m_iRoleShapeID = None
        self.m_SummonType = 0
        self.m_iHeroFeature = 0
        self.m_SummonAni = None
        self.m_dSelectDesc = None
        self.InitDlg()

    
    def InitDlg(self):
        self.InitChooseClassImgButton()
        iLiuPaiInfo = survivemgr.GetSurviveMgr().GetLiuPaiInfo()
        if not iLiuPaiInfo:
            self.RandomShape()
            iLiuPaiInfo = random.randint(1, 3)
            self.GetObject('noname%d' % (8 + random.choice(surviverdefine.INFO_FEATURE.keys()))).LeftUp()
        else:
            self.m_dSelectDesc = copy.deepcopy(hero.GetProp('m_Desc'))
            self.m_iRoleShapeID = hero.GetProp('m_Shape')
            iSummon = self.m_dSelectDesc.get('summon', None)
            iRandSum = random.choice(surviverdefine.INFO_FEATURE.keys())
            if not iSummon:
                iSummon = iRandSum
            else:
                for iType, iSum in surviverdefine.INFO_FEATURE.iteritems():
                    if iSummon == iSum:
                        iSummon = iType
                        break
                        continue
                else:
                    iSummon = iRandSum
            oButton = self.GetObject('noname%d' % (8 + iSummon))
            if oButton:
                oButton.LeftUp()
            
        self.CreateHeroPlayer()
        self.OnSelectButton(iLiuPaiInfo)

    
    def InitClassDesc(self):
        '''\xaa\xec\xa9l\xa4\xc6\xacy\xac\xa3\xb4y\xadz'''
        sClassDesc = surviverdefine.INFO_CLASS_DATA.get(self.m_iRoleWeaponID, '')
        oUIObject = self.GetObject('txt_Desc')
        (iRichTextW, _) = oUIObject.GetSize()
        self.m_oClassDescRichText = interface.CRichTextObject(oUIObject, iRichTextW, interface.FontLT14_3, sClassDesc, interface.COLOR_91)

    
    def CreateHeroPlayer(self):
        self.m_oFakeRoleWalkerObject = walker.CFakeRole(self.GetObject('img_Photo'), -1, self.m_iRoleShapeID, self.m_dSelectDesc)
        self.m_oFakeRoleWalkerObject.SetPos(50, 108)

    
    def CreateSumPlayer(self, iType):
        import hero
        import walker
        self.m_SummonType = surviverdefine.INFO_FEATURE[iType]
        desc = {
            'summon': self.m_SummonType,
            'summontype': 1,
            'wing': [
                0,
                0,
                0] }
        self.m_SummonAni = walker.CFakeRole(self.GetObject('img_Photo'), -1, hero.g_Prop.m_RealShape, desc)
        self.m_SummonAni.SetPos(28, 74)
        self.m_SummonAni.SetAlpha(144)
        self.m_iHeroFeature = iType - 3

    
    def InitChooseClassImgButton(self):
        '''\xaa\xec\xa9l\xa4\xc6\xacy\xac\xa3\xbf\xef\xbe\xdc\xab\xf6\xb6s'''
        import misc
        import skilliconpath
        sIgsPathData = [
            ('noname6', 1, '817.igs'),
            ('noname7', 2, '2413.igs'),
            ('noname8', 3, '1203.igs')]
        for sUIName, iMsgID, sIgsPath in sIgsPathData:
            (sPath, sPack) = skilliconpath.GetSkillIconPack(skilliconpath.TYPE_SUMMON_SKILL, sIgsPath)
            oButton = CClassChooseItem(self.GetObject(sUIName), sPath, sPack)
            interface.Center(oButton)
            oButton.SetMsgCB(misc.Functor(self.OnSelectButton, iMsgID))
            self.m_oButtonData[iMsgID] = oButton
        

    
    def GetSelectID(self):
        '''\xc0\xf2\xa8\xfa\xb7\xed\xabe\xbf\xef\xa4\xa4\xaa\xbaID'''
        return self.m_iSelectID

    
    def RandomShape(self):
        self.m_iRoleShapeID = random.choice(surviverdefine.INFO_HERO_SHAPE)
        dDesc = copy.deepcopy(surviverdefine.INFO_HERO_DESC)
        dDesc['color'] = [
            random.randint(0, 8),
            random.randint(0, 8),
            random.randint(0, 8)]
        if not self.m_iRoleWeaponID:
            self.m_iRoleWeaponID = surviverdefine.TYPE_CLASS_SWORD
        
        dDesc['weapon'] = [
            self.m_iRoleWeaponID,
            1,
            random.randint(0, 8)]
        self.m_dSelectDesc = dDesc

    
    def ChangeWeapon(self):
        if not self.m_iRoleWeaponID:
            self.m_iRoleWeaponID = surviverdefine.TYPE_CLASS_SWORD
        
        self.m_dSelectDesc['weapon'] = [
            self.m_iRoleWeaponID] + self.m_dSelectDesc['weapon'][1:]

    
    def HeroPlayerAttack(self):
        self.m_oFakeRoleWalkerObject.SetState('attack')

    
    def OnSelectButton(self, iMsgID):
        if self.m_iSelectID == iMsgID:
            return None
        
        if self.m_iSelectID:
            self.m_oButtonData[self.m_iSelectID].SetFlash(False)
        
        self.m_iSelectID = iMsgID
        self.m_iRoleWeaponID = surviverdefine.MSG_ID_TO_WEAPON_ID[self.m_iSelectID]
        self.m_oButtonData[iMsgID].SetFlash(True)
        self.ChangeWeapon()
        self.CreateHeroPlayer()
        self.InitClassDesc()
        self.HeroPlayerAttack()

    
    def OnConfirmSelect(self):
        import netsurvive
        if self.m_iSelectID and self.m_dSelectDesc:
            dDesc = {
                0: self.m_dSelectDesc['color'],
                1: self.m_dSelectDesc['weapon'] }
            netsurvive.C2SSelectClass(self.m_iRoleShapeID, self.m_iSelectID, self.m_iHeroFeature, dDesc)
        

    
    def CloseWindow(self):
        GetGameSurviveCtrl().CloseClassDlg()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 2:
            self.RandomShape()
            self.CreateHeroPlayer()
        elif iMsgID == 3:
            self.OnConfirmSelect()
        elif iMsgID in (4, 5, 6):
            self.CreateSumPlayer(iMsgID)
        



class CQuickOperateTips(combdialog.CCombDialog):
    '''\xa7\xd6\xb1\xb6\xbe\xde\xa7@Tips'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_EOPERATE_TIPS)
        self.InitDlg()

    
    def InitDlg(self):
        self.GetObject('btn_max').SetShow(False)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            GetGameSurviveCtrl().ShowQuickOperateDlg()
        elif iMsgID == 2:
            import netsurvive
            netsurvive.C2SAskGuidelines()
        elif iMsgID == 3:
            GetGameSurviveCtrl().ShowSurviveAdviceDlg()
        elif iMsgID == 6:
            for obj in self.m_Frames.values():
                obj.SetShow(False)
            
            self.GetObject('btn_max').SetShow(True)
            self.GetObject('bg').SetShow(False)
        elif iMsgID == 7:
            for obj in self.m_Frames.values():
                obj.SetShow(True)
            
            self.GetObject('bg').SetShow(True)
            self.GetObject('btn_max').SetShow(False)
        



class CQuickOperateDlg(combdialog.CCombDialog):
    '''\xa7\xd6\xb1\xb6\xbe\xde\xa7@\xac\xc9\xad\xb1'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_KUAIJIE)
        self.m_iPetID = None
        (self.m_Width, self.m_Height) = self.GetObject('noname12').GetSize()
        self.InitSlot()
        self.InitDlg()

    
    def InitSlot(self):
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oMgr = oSurviveMgr.GetPointMgr()
        oMgr.ssConnect(oMgr.SS_UpdatePetPoint, self.OnShowPetPoint)
        oMgr.ssConnect(oMgr.SS_UpdateHeroPoint, self.OnShowHeroPoint)
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateConFig, self.OnAutoBtnChange)

    
    def InitDlg(self):
        import netsurvive
        netsurvive.C2SHeroOpenAutoDlg()
        dlgpet.g_PetDialog.OpenAutoAssignDlg()
        self.m_iPetID = combmacro.GetSelectedItemFromList(dlgpet.g_PetDialog.GetObject('lst_summon')).m_PID
        survivemgr.GetSurviveMgr().GetPointMgr().SetIsPetGetFlag(True)
        survivemgr.GetSurviveMgr().GetPointMgr().SetIsHeroGetFlag(True)
        self.SetAutoBtn(1)
        self.SetAutoBtn(2)

    
    def SetAutoBtn(self, iType):
        bIsAuto = survivemgr.GetSurviveMgr().GetUesConfigData(iType, 0)
        if iType == 1:
            sName = 'btn_item2'
        elif iType == 2:
            sName = 'btn_item1'
        else:
            return None
        oBtn = self.GetObject(sName)
        if bIsAuto:
            oBtn.SetSelect(True)
        else:
            oBtn.SetSelect(False)

    
    def OnPetMessage(self, iMsgID):
        import netsurvive
        if self.GetObject('btn_pet%d' % iMsgID).GetSelect():
            self.GetObject('btn_pet%d' % iMsgID).SetSelect(False)
            iMsgID = 0
            bType = False
        else:
            for iMsg in range(1, 4):
                self.GetObject('btn_pet%d' % iMsg).SetSelect(False)
            
            self.GetObject('btn_pet%d' % iMsgID).SetSelect(True)
            bType = True
        if iMsgID in surviverdefine.QUICK_OPERATE_PET:
            netsurvive.C2SSetAutoPoint(self.m_iPetID, surviverdefine.QUICK_OPERATE_PET[iMsgID], bType, 100)
        else:
            survivemgr.GetSurviveMgr().GetPointMgr().SetIsPetGetFlag(False)
            dlgpet.ShowPetDialog()
            dlgpet.g_PetDialog.OpenAutoAssignDlg()

    
    def OnHeroMessage(self, iMsgID):
        import netsurvive
        iMsgID -= 3
        if self.GetObject('btn_role%d' % iMsgID).GetSelect():
            self.GetObject('btn_role%d' % iMsgID).SetSelect(False)
            iMsgID = 0
            bType = False
        else:
            for iMsg in range(1, 4):
                self.GetObject('btn_role%d' % iMsg).SetSelect(False)
            
            self.GetObject('btn_role%d' % iMsgID).SetSelect(True)
            bType = True
        if iMsgID in surviverdefine.QUICK_OPERATE_HERO:
            netsurvive.C2SHeroSetAutoPoint(surviverdefine.QUICK_OPERATE_HERO[iMsgID], bType)
        else:
            survivemgr.GetSurviveMgr().GetPointMgr().SetIsHeroGetFlag(False)
            if not GetGameSurviveCtrl().GetVirStateDlg():
                GetGameSurviveCtrl().SwichVirStateDlg()
            
            netsurvive.C2SHeroOpenAutoDlg()

    
    def OnShowHeroPoint(self):
        iPointList = survivemgr.GetSurviveMgr().GetPointMgr().GetHeroPoint().get('attrList', [
            0,
            0,
            0,
            0,
            0])
        for iKey, iList in surviverdefine.QUICK_OPERATE_HERO.iteritems():
            if iPointList == iList:
                break
                continue
        else:
            iKey = 3
        for iMsg in range(1, 4):
            self.GetObject('btn_role%d' % iMsg).SetSelect(False)
        
        oBtn = self.GetObject('btn_role%d' % iKey)
        if oBtn:
            oBtn.SetSelect(True)
        

    
    def OnShowPetPoint(self):
        self.m_iPetID = combmacro.GetSelectedItemFromList(dlgpet.g_PetDialog.GetObject('lst_summon')).m_PID

    
    def OnAutoBtnChange(self, iType, iVal):
        self.SetAutoBtn(iType)

    
    def RightDown(self):
        GetGameSurviveCtrl().CloseQuickOperateDlg()

    
    def OnMessage(self, iMsgID):
        if iMsgID in (1, 2, 3):
            self.OnPetMessage(iMsgID)
        elif iMsgID in (4, 5, 6):
            self.OnHeroMessage(iMsgID)
        elif iMsgID == 7:
            import netsurvive
            netsurvive.C2SConfig(2, 1 - survivemgr.GetSurviveMgr().GetUesConfigData(2, 0))
        elif iMsgID == 8:
            import netsurvive
            netsurvive.C2SConfig(1, 1 - survivemgr.GetSurviveMgr().GetUesConfigData(1, 0))
        elif iMsgID == 9:
            GetGameSurviveCtrl().CloseQuickOperateDlg()
        



class CMapIcon(dlgmap.CMapIcon):
    
    def LeftUp(self):
        dlgmap.CMapIcon.LeftUp(self)
        self.GetParent().LeftUp()



class CMinimap(dlgmap.CMinimap):
    '''
\t\xad\xab\xbcg\xa4p\xa6a\xb9\xcf\xabH\xae\xa7
\t'''
    
    def RegistSlot(self):
        import commoncb
        dlgmap.CMinimap.RegistSlot(self)
        oSurviveMgr = survivemgr.GetSurviveMgr()
        commoncb.RegistCB(commoncb.HERO_CHANGEPOS, self, 'OnHeroPosChange')
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnUpdateSceneChange')
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateMiniMapGoToInfo, self.OnUpdateMapGoToInfo)
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateWeather, self.OnUpdateWeather)

    
    def WriteTxt(self):
        '''
\t\t\xad\xab\xbcg\xb3\xd0\xab\xd8\xa6a\xb9\xcf\xb6\xc7\xb0e\xc2I
\t\t'''
        self.m_AddressTxtObjs = []
        dMapGoToInfo = survivemgr.GetSurviveMgr().GetMiniMapData(self.m_MapID)
        if not dMapGoToInfo:
            return None
        
        (iMiniMapW, iMiniMapH) = self.GetSize()
        iMiniMapW -= self._EDGE_WIDTH * 2
        iMiniMapH -= self._EDGE_WIDTH * 2
        for tGoToPos, sText in dMapGoToInfo.iteritems():
            (offset_x, offset_y) = self._GetOffset(tGoToPos[0], tGoToPos[1])
            for iID, dInfo in surviverdefine.MAP_INFO_DATA.iteritems():
                if dInfo['name'] == sText:
                    iWeather = survivemgr.GetSurviveMgr().GetWeatherData(iID)
                    if iWeather == surviverdefine.TYPE_WEATHER_WIND:
                        iColor = 16776960
                    elif iWeather == surviverdefine.TYPE_WEATHER_SNOW:
                        iColor = interface.COLOR_25
                    else:
                        iColor = 65280
                    break
                    continue
            else:
                iColor = 65280
            oNameTextObj = dlgmap.CClickRichTextBox(self, interface.FontST14E, sText, iColor)
            oNameTextObj.m_NameObj = interface.CTextObject(oNameTextObj, sText, interface.FontST14E, iColor)
            oNameTextObj.m_NameObj.SetZ(1000)
            oNameTextObj.m_NpcPos = (tGoToPos[0], tGoToPos[1])
            (nw, nh) = oNameTextObj.GetSize()
            (dw, dh) = (0, 0)
            nx = offset_x - nw / 2
            ny = offset_y - nh / 2
            (dx, dy) = (0, 0)
            minx = min(nx, dx)
            maxx = max(nx + nw, dx + dw)
            miny = ny
            maxy = ny + nh
            if minx < 0:
                nx = nx - minx
                dx = dx - minx
            elif maxx > iMiniMapW:
                nx -= maxx - iMiniMapW
                dx -= maxx - iMiniMapW
            
            if miny < 0:
                ny = ny - miny
                dy = dy - miny
            elif maxy > iMiniMapH:
                ny -= maxy - iMiniMapH
                dy -= maxy - iMiniMapH
            
            oNameTextObj.SetPos(int(nx + self._EDGE_WIDTH), int(ny + self._EDGE_WIDTH))
            oNameTextObj.SetZ(1000)
            self.m_AddressTxtObjs.append((oNameTextObj, None))
        

    
    def ShowSnowGril(self, iScene, iPosX, iPosY):
        self.AddNpcIcon(iScene, iPosX, iPosY, '\xb3\xb7\xa4k', '\xb3\xb7\xa4k\xb7|\xc0\xb0\xa7U\xa7A#r(%d, %d)', 2)

    
    def CloseSnowGril(self):
        self.CloseNpcIcon(2)

    
    def ShowSuperBox(self, iScene, iPosX, iPosY):
        '''\xaei\xa5\xdc\xb6W\xaf\xc5\xc4_\xbdc'''
        self.AddNpcIcon(iScene, iPosX, iPosY, '\xb4c\xc5]\xc4_\xbdc', '\xb4c\xc5]\xc4_\xbdc\xa4\xa4\xa6\xb3\xa4j\xb6q\xc4_\xaa\xab#r(%d, %d)', 1)

    
    def CloseSuperBox(self):
        self.CloseNpcIcon(1)

    
    def AddNpcIcon(self, iScene, iPosX, iPosY, sName, sTips, iDex):
        icon = CMapIcon(self, 'common/npc01.igs', interface.UIPath, 0)
        icon.m_Index = iDex
        icon.m_NID = 0
        icon.m_NpcName = sName
        icon.SetZ(1003)
        icon.SetPos(int(self._EDGE_WIDTH + iPosX * map.CELLSIZE / self.m_Scale[0]), int(self.GetSize()[1] - iPosY * map.CELLSIZE / self.m_Scale[1]))
        sMsg = sTips % (iPosX, iPosY)
        icon.m_Msg = sMsg
        icon.m_Txt = interface.CTextObject(icon, icon.m_NpcName, interface.FontST12E, 6676297)
        (iw, ih) = icon.m_Txt.GetSize()
        icon.m_Txt.SetPos(-iw / 2, -8 - ih)
        if not self.m_Icons:
            self.m_Icons = { }
        
        if 1 not in self.m_Icons:
            self.m_Icons[1] = { }
        
        self.m_Icons[1][iDex] = icon
        self.SetTextInfo()

    
    def CloseNpcIcon(self, iDex):
        if 1 in self.m_Icons and iDex in self.m_Icons[1]:
            self.m_Icons[1][iDex] = None
        

    
    def RefreshFlyIcons(self):
        pass

    
    def CreateHideBtns(self):
        '''\xab\xcc\xbd\xaa\xab\xf6\xb6s\xa5\\\xaf\xe0'''
        return None

    
    def ShowNpcIcon(self, idx):
        '''\xab\xcc\xb9\xf5NPC\xc5\xe3\xa5\xdc'''
        return None

    
    def RefreshMineralBtn(self):
        pass

    
    def RefreshTreeBtn(self):
        pass

    
    def SetIconsShow(self, iVirtual):
        if iVirtual is True:
            for btn in self.m_Btns.values():
                btn.SetShow(False)
            
            self.m_Btns[self.TYPE_WORLD].SetShow(True)
        

    
    def ShowTipsBox(self):
        if not GetGameSurviveCtrl().m_bIsFirstOpen:
            GetGameSurviveCtrl().m_bIsFirstOpen = True
            (iW, _) = self.GetSize()
            args = ('#G\xacd\xac\xdd\xb8\xd4\xb2\xd3\xbb\xa1\xa9\xfa#n', 5, iW - 5, -13, 100, 35)
            self.m_PointBox = wrapinterface.CCombTipsBox(self, *args)
        else:
            self.m_PointBox = None

    
    def CreateTextBtn(self):
        '''\xb3\xd0\xab\xd8\xb8\xd4\xb2\xd3\xabH\xae\xa7\xab\xf6\xb6s\xab\xf6\xb6s\xa1A\xb4\xa3\xa5\xdc\xabH\xae\xa7\xa1ATips\xabH\xae\xa7'''
        self.ShowTipsBox()
        self.SetTextInfo()
        (iW, iH) = self.GetSize()
        self.m_Btns[1] = ui.CImage(self, 'combdialog3/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xcc\xe1\xca\xbe\xb0\xb4\xc5\xa5/0.png', interface.UIPath)
        self.m_Btns[1].SetPos(iW - 16, -24)
        (w, h) = self.m_Btns[1].GetSize()
        self.m_Btns[2] = interface.CNotifyBox(self, w, h, alpha = 0, msgid = 1)
        self.m_Btns[2].SetPos(iW - 16, -24)

    
    def SetTextInfo(self):
        '''\xb3]\xb8m\xb7\xed\xabe\xa6a\xb9\xcf\xaa\xba\xaa\xed\xc0Y\xb4\xa3\xa5\xdc\xabH\xae\xa7'''
        iSceneID = surviverdefine.GetSceneIDWithMapID(self.m_MapID)
        iWeather = survivemgr.GetSurviveMgr().GetWeatherData(iSceneID)
        if GetGameSurviveCtrl().m_bIsShowSnowGril:
            iWeather = surviverdefine.TYPE_GRIL_SNOW
        
        sMsg = surviverdefine.INFO_MINIMAP_TIPS_DATA.get(iWeather, '')
        self.m_Btns[4] = interface.CRichTextObject(self, 1000, interface.FontLT16, sMsg, interface.COLOR_3)
        self.m_Btns[4].SetPos(0, -24)

    
    def AskSuperBoxInfo(self):
        iSceneID = surviverdefine.GetSceneIDWithMapID(self.m_MapID)
        if iSceneID in surviverdefine.MAP_INFO_DATA:
            survivemgr.GetSurviveMgr().AskMiniMapData(iSceneID)
        

    
    def LeftUp(self):
        import C_sys
        if self.OnCopeMapPosLink():
            return None
        
        import mainmenu
        import stackcheck
        if mainmenu.IsWar():
            return None
        
        import sound
        import sounddefine
        sound.Play(sounddefine.PATH_CLICKMAP)
        import autofindpath
        if autofindpath.IsAutoWalk():
            autofindpath.StopAuto()
        
        import wrapui
        wrapui.ReleaseClickNpcTimer()
        if dlgmap.g_AutoGoto:
            self.AutoGoto()
            return None
        
        if dlgmap.g_AutoWalk:
            import cursor
            (cx, cy) = cursor.GetCursorPos()
            (w, h) = self.GetSize()
            w -= self._EDGE_WIDTH * 2
            h -= self._EDGE_WIDTH * 2
            (x, y) = self.GetPos()
            x += self._EDGE_WIDTH
            y += self._EDGE_WIDTH
            if cx >= x and cx < x + w and cy >= y and cy < y + h:
                x = cx - x
                y = cy - y
                import map
                import hero
                dx = int(x * self.m_Scale[0])
                dy = int(y * self.m_Scale[1])
                stackcheck.SetBeforeCall(stackcheck.KEY_AUTOWALK)
                map.AutoWalk(dx, dy, (self._EDGE_WIDTH + x, self._EDGE_WIDTH + y))
                self.CreateDestAni(x, y)
            
        elif dlgmap.g_SetPath:
            import key
            if C_sys.IsKeyDown(key.VK_SHIFT):
                import cursor
                (cx, cy) = cursor.GetCursorPos()
                (x, y) = self.GetPos()
                x = cx - x
                y = cy - y
                (w, h) = self.GetSize()
                y = h - y
                import map
                dx = int((x - self._EDGE_WIDTH) * self.m_Scale[0] / map.CELLSIZE)
                dy = int((y - self._EDGE_WIDTH) * self.m_Scale[1] / map.CELLSIZE)
                self.CreateDestAni(x - self._EDGE_WIDTH, y - self._EDGE_WIDTH)
                self._addmappoint(dx, dy)
            
        else:
            interface.CBase.LeftUp(self)
        dlgmap.SetClickNpcInfo(None)

    
    def OnHeroPosChange(self, iPosX, iPosY):
        PRINT(iPosX, iPosY)
        self.UpdateHeroPosition()
        dlgmap.DrawMiniMapPath(self)

    
    def OnUpdateMapGoToInfo(self, iSceneID, dGoToData):
        PRINT(iSceneID, dGoToData)
        self.WriteTxt()

    
    def OnUpdateWeather(self, iSceneID, iWeatherType):
        PRINT(iSceneID, iWeatherType)
        self.SetTextInfo()
        self.WriteTxt()

    
    def OnUpdateSceneChange(self, scene, mapid, minimapid):
        PRINT(scene, mapid, minimapid)
        GetGameSurviveCtrl().CloseMinimap()

    
    def OnEnter(self, msgid):
        if msgid == 1:
            self.m_Btns[3] = wrapinterface.CTextTips(self, -1, surviverdefine.MSG_MINIMAP_TIPS, interface.FontLT14_3, direct = 1)
            self.m_Btns[3].SetZ(2)
            if self.m_PointBox:
                self.m_PointBox = None
            
        

    
    def OnLeave(self, msgid):
        if msgid == 1:
            self.m_Btns[3] = None
        

    
    def OnMessage(self, msgid):
        if msgid == 8:
            GetGameSurviveCtrl().OpenWorldMap()
        



class CWorldMap(combdialog.CCombDialog):
    '''
\t\xa4j\xb0k\xb1\xfe\xa5@\xac\xc9\xa6a\xb9\xcf\xac\xc9\xad\xb1
\t\xbc\xc8\xae\xc9\xb1\xf3\xa5\xce
\t'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_WORLD_MAP)
        interface.Center(self)
        self.m_HeroSpr = None
        self.InitDlg()
        self.InitSlot()

    
    def InitDlg(self):
        self.InitWeatherInfo()
        self.InitRoleInMapPos()

    
    def InitSlot(self):
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateWeather, self.OnWeatherChange)

    
    def InitWeatherInfo(self):
        '''\xaa\xec\xa9l\xa4\xc6\xa4\xd1\xae\xf0\xabH\xae\xa7'''
        for iMapPos, sMapName in surviverdefine.MAP_INFO_DATA.iteritems():
            iWeatherType = survivemgr.GetSurviveMgr().GetWeatherData(iMapPos)
            self.SetMapItemWeatherInfo(iMapPos, iWeatherType)
        

    
    def InitRoleInMapPos(self):
        '''\xaa\xec\xa9l\xa4\xc6\xa8\xa4\xa6\xe2\xa6b\xa6a\xb9\xcf\xa4W\xaa\xba\xa6\xec\xb8m'''
        import map
        iMapID = map.GetCurrentMapID()
        iMapPos = surviverdefine.GetSceneIDWithMapID(iMapID)
        oMapItem = self.GetObject('btn_%s' % iMapPos % 1000)
        self.m_HeroSpr = interface.CSpriteObject(oMapItem, 'common/hero.spr', interface.UIPath)
        self.m_HeroSpr.CreateCommand(1, 'animation')
        interface.Center(self.m_HeroSpr, 5, 10)
        self.m_HeroSpr.SetZ(3)

    
    def SetMapItemWeatherInfo(self, iMapPos, iWeatherType):
        oMapItem = self.GetObject('btn_%s' % iMapPos % 1000)
        if iWeatherType:
            if iWeatherType == surviverdefine.TYPE_WEATHER_SNOW:
                self.SetMapItemColor(oMapItem, interface.COLOR_25)
            elif iWeatherType == surviverdefine.TYPE_WEATHER_WIND:
                self.SetMapItemColor(oMapItem, 16776960)
            
        

    
    def SetMapItemColor(self, oBtn, iColor):
        if not oBtn:
            return None
        
        oBtn.SetTextColor(iColor)
        oBtn.m_Color = iColor
        oBtn.m_EnterColor = iColor

    
    def CloseWindow(self):
        GetGameSurviveCtrl().CloseWorldMap()

    
    def RightDown(self):
        self.CloseWindow()

    
    def OnWeatherChange(self, iSceneID, iWeatherType):
        self.SetMapItemWeatherInfo(iSceneID, iWeatherType)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        



class CSceneItem(interface.CBoxObject):
    ROOM_WIDTH = 80
    ROOM_HEIGHT = 44
    COLOR = 65280
    ALPHA = 0
    
    def __init__(self, parent):
        interface.CBoxObject.__init__(self, parent, self.ROOM_WIDTH, self.ROOM_HEIGHT, self.COLOR, self.ALPHA)
        self.m_Imagess = { }
        self.m_IDText = None
        self.Refresh([
            1,
            1,
            1,
            1])

    
    def Refresh(self, data):
        self.m_Imagess = { }
        idx2X = {
            1: 1,
            2: self.ROOM_WIDTH / 2 + 2,
            3: self.ROOM_WIDTH / 2 + 2,
            4: 1 }
        idx2Y = {
            1: 0,
            2: 0,
            3: self.ROOM_HEIGHT / 2,
            4: self.ROOM_HEIGHT / 2 }
        for i in (1, 2, 3, 4):
            if data[i - 1]:
                path = 'vmap/room%d.igs' % (4 + i)
            else:
                path = 'vmap/room%d.igs' % i
            igs = ui.CImage(self, path, 'mapobject')
            igs.SetPos(idx2X[i], idx2Y[i])
            self.m_Imagess[i] = igs
        

    
    def SetID(self, mapid):
        if mapid:
            x = mapid / 4 + 1
            y = mapid % 4
            if y == 0:
                y = 4
                x -= 1
            
            mapid = (y - 1) * 4 + x
            mapid += 1000
            self.m_IDText = interface.CTextObject(self, surviverdefine.MAP_INFO_DATA[mapid]['name'], interface.FontLT12E_1, [
                1210424,
                16777215], 0)
            self.m_IDText.SetZ(1)
            (w, h) = self.GetSize()
            (tw, th) = self.m_IDText.GetSize()
            self.m_IDText.SetPos((w - tw) / 2, (h - th) / 2)
        else:
            self.m_IDText = None

    
    def SetTestColor(self, iColor):
        if self.m_IDText:
            self.m_IDText.SetColor(iColor)
        



class CRoadItem(interface.CBoxObject):
    ROAD_WIDTH = 54
    ROAD_HEIGHT = 26
    COLOR = 65280
    ALPHA = 0
    
    def __init__(self, parent):
        interface.CBoxObject.__init__(self, parent, self.ROAD_WIDTH, self.ROAD_HEIGHT, self.COLOR, self.ALPHA)
        self.m_Image = None
        self.Refresh(1)

    
    def Refresh(self, data):
        if data:
            path = 'vmap/road1.igs'
        else:
            path = 'vmap/road2.igs'
        self.m_Image = ui.CImage(self, path, 'mapobject')



class CNewWorldMap(interface.CContainerObject, interface.CBase):
    SPACE_X = 68
    SPACE_Y = 38
    TYPE_FLY = 0
    TYPE_BOX = 1
    TYPE_BOSS = 2
    TYPE_STOVE = 3
    TYPE_OTHER = 4
    TYPE_PLAYER = 5
    
    def __init__(self):
        self.m_Base = 4
        interface.CContainerObject.__init__(self, interface.DialogPanel)
        self.m_Width = (self.m_Base + self.m_Base - 1) * self.SPACE_X
        self.m_Height = (self.m_Base + self.m_Base - 1) * self.SPACE_Y
        self.MessageProcess()
        self.SetPos((world.WINDOW_WIDTH - self.m_Width) / 2, (world.WINDOW_HEIGHT - self.m_Height) / 2 - 50)
        self.Topmost()
        self.m_Rooms = { }
        self.m_Roads = { }
        self.m_Hero = None
        self.InitDlg()
        self.InitSlot()

    
    def InitDlg(self):
        iList = range(1, 17)
        self.RefreshRoom(iList)
        iRoadList = [
            (1, 2),
            (2, 3),
            (3, 4)]
        iTmpList = []
        for i in range(4):
            [] += [ (ii + 4 * i, jj + 4 * i) for ii, jj in iRoadList ]
        
        iRoadList = [
            (1, 5),
            (5, 9),
            (9, 13)]
        for i in range(4):
            [] += [ (ii + i, jj + i) for ii, jj in iRoadList ]
        
        self.RefreshRoad(iTmpList)
        self.Refresh()
        self.InitWeatherInfo()
        self.InitRoleInMapPos()

    
    def InitSlot(self):
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateWeather, self.OnWeatherChange)

    
    def InitWeatherInfo(self):
        '''\xaa\xec\xa9l\xa4\xc6\xa4\xd1\xae\xf0\xabH\xae\xa7'''
        for iMapPos, sMapName in surviverdefine.MAP_INFO_DATA.iteritems():
            iWeatherType = survivemgr.GetSurviveMgr().GetWeatherData(iMapPos)
            self.SetMapItemWeatherInfo(iMapPos, iWeatherType)
        

    
    def InitRoleInMapPos(self):
        '''\xaa\xec\xa9l\xa4\xc6\xa8\xa4\xa6\xe2\xa6b\xa6a\xb9\xcf\xa4W\xaa\xba\xa6\xec\xb8m'''
        import map
        iMapID = map.GetCurrentMapID()
        iMapPos = surviverdefine.GetSceneIDWithMapID(iMapID)
        if not iMapPos:
            return None
        
        self.m_Hero = interface.CSpriteObject(self.m_Rooms[self.ChangePosID(iMapPos % 1000)], 'common/hero.spr', interface.UIPath)
        self.m_Hero.CreateCommand(1, 'animation')
        interface.Center(self.m_Hero, 5, 10)
        self.m_Hero.SetZ(3)

    
    def ChangePosID(self, iPos):
        x = iPos / 4 + 1
        y = iPos % 4
        if y == 0:
            y = 4
            x -= 1
        
        return (y - 1) * 4 + x

    
    def SetMapItemWeatherInfo(self, iMapPos, iWeatherType):
        oMapItem = self.m_Rooms[self.ChangePosID(iMapPos % 1000)]
        if iWeatherType:
            if iWeatherType == surviverdefine.TYPE_WEATHER_SNOW:
                self.SetMapItemColor(oMapItem, interface.COLOR_25)
            elif iWeatherType == surviverdefine.TYPE_WEATHER_WIND:
                self.SetMapItemColor(oMapItem, 16776960)
            
        

    
    def SetMapItemColor(self, oMapItem, iColor):
        if not oMapItem:
            return None
        
        oMapItem.SetTestColor(iColor)

    
    def CloseWindow(self):
        GetGameSurviveCtrl().CloseWorldMap()

    
    def RightDown(self):
        self.CloseWindow()

    
    def LeftDown(self):
        oMap = map.GetGameMapObject()
        if oMap:
            oMap.LeftDown()
        

    
    def LeftUp(self):
        oMap = map.GetGameMapObject()
        if oMap:
            oMap.LeftUp()
        

    
    def OnWeatherChange(self, iSceneID, iWeatherType):
        self.SetMapItemWeatherInfo(iSceneID, iWeatherType)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        

    
    def Refresh(self):
        poslist = [
            (-(self.m_Base), 0),
            (0, 1),
            (0, self.m_Base),
            (-1, 0)]
        for v, room in self.m_Rooms.iteritems():
            data = [ (v + a, v + b) in self.m_Roads for a, b in poslist ]
            room.Refresh(data)
        

    
    def RefreshRoom(self, rooms, bClear = True):
        if bClear:
            self.m_Rooms = { }
        
        w = self.m_Width
        h = self.m_Height
        x = 0
        y = h / 2
        base = self.m_Base
        for v in rooms:
            if bClear == False and v in self.m_Rooms:
                continue
            
            room = CSceneItem(self)
            room.SetID(v)
            ix = (v - 1) / base + (v - 1) % base
            iy = (v - 1) / base - (v - 1) % base
            room.SetPos(x + ix * self.SPACE_X, y + iy * self.SPACE_Y)
            room.SetZ(1)
            room.m_RoomID = v
            self.m_Rooms[v] = room
        

    
    def RefreshRoad(self, roads):
        self.m_Roads = { }
        w = self.m_Width
        h = self.m_Height
        x = 48
        y = h / 2 - 10
        base = self.m_Base
        for a, b in roads:
            a = min(a, b)
            b = max(a, b)
            road = CRoadItem(self)
            v = b - a
            if v == 1:
                ix = (a - 1) / base + (a - 1) % base
                iy = (a - 1) / base - (a - 1) % base
                road.Refresh(False)
            elif v == self.m_Base:
                ix = (a - 1) / base + (a - 1) % base
                iy = ((a - 1) / base - (a - 1) % base) + 1
                road.Refresh(True)
            
            road.SetPos(x + ix * self.SPACE_X, y + iy * self.SPACE_Y)
            road.SetZ(2)
            self.m_Roads[(a, b)] = road
        



class CVirStateDlg(dlgstate.CStateDialog):
    
    def AddHeroPropCallBack(self):
        STATE_INFOS = (('m_Name', 0, 0, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, dlgstate.GetTextClass()), ('m_Country', 0, 3, interface.ALIGN_LEFT | interface.ALIGN_MIDDLE, dlgstate.GetTextClass()))
        hero.CreateCombDlgItem('txt_info', 'StateDlg', STATE_INFOS, self)
        hero.AddRefreshCallback('StateDlg', dlgstate.STATE_TILIHUOLI, self.RefreshTilihuoli)
        stateInfpLst = [
            (dlgstate.STATE_ATTRS, self.ShowAttrChange),
            (dlgstate.STATE_POINTS, self.ShowAttrChange),
            (dlgstate.ATTR_POINTS, self._refreshpoint),
            ([
                [
                    'm_AutoUpgrade']], self._refreshpoint)]
        for stateLst, callBack in stateInfpLst:
            hero.AddRefreshCallback('StateDlg', stateLst, callBack)
        
        propInfoLst = [
            ('m_NextExp', '', self.ShowExp),
            ('m_SkillExp', '', self.ShowExp),
            ('m_Grade', '', self.ShowClass),
            ('m_Grade', 'AutoAssignBtn', self.RefreshAssignBtn),
            ('m_Class', '', self.ShowClass),
            ('m_Title', '', self.ShowName),
            ('m_VIP', '', self.ShowVIP)]
        for propName, callBackkey, callBack in propInfoLst:
            if not callBackkey:
                callBackkey = 'StateDlg'
            
            propitem = hero.g_Name2PropItem[propName]
            propitem.AddRefreshCallbackWithID(callBackkey, callBack)
        

    
    def RefreshTilihuoli(self):
        '''\xab\xcc\xbd\xaa\xc5\xe9\xa4O'''
        obj = self.GetObject('txt_info')
        self.m_Tili = combmacro.CreateIFTextWithObject(obj, interface.CRichTextObject, 0, 6, '0/300', interface.FontLT14_3, interface.COLOR_9)
        self.m_Huoli = combmacro.CreateIFTextWithObject(obj, interface.CRichTextObject, 0, 7, '0/300', interface.FontLT14_3, interface.COLOR_9)

    
    def SendPoint(self):
        import nethero
        if hasattr(self, 'm_FightPoint') and self.m_FightPoint:
            if len(self.m_FightPoint) == 5 and max(self.m_FightPoint) > 0:
                nethero.C2SPropPoint(self.m_FightPoint)
            
        

    
    def OnCommitPoint(self):
        import netsurvive
        total = 0
        for num in self.m_Points[:5]:
            total += num
        
        if total <= 0:
            return None
        
        if mainmenu.IsRealWar():
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xa4\xc0\xb0t\xc2I\xbc\xc6')
        else:
            netsurvive.C2SAddAdjustPoint(self.m_Points[:5])
            self.m_FightPoint = None

    
    def ShowAutoAssign(self, dataDct = None):
        survivemgr.GetSurviveMgr().GetPointMgr().SetHeroPoint(dataDct)
        if survivemgr.GetSurviveMgr().GetPointMgr().GetIsHeroGetFlag():
            survivemgr.GetSurviveMgr().GetPointMgr().SetIsHeroGetFlag(False)
            return None
        
        self.m_AutoAssignDlg = CHeroAutoAssignDlg(self)
        self.m_AutoAssignDlg.SetData(dataDct)

    
    def SwitchAutoAssignDlg(self):
        import netsurvive
        if hasattr(self, 'm_AutoAssignDlg') and self.m_AutoAssignDlg:
            self.OnAutoAssignClose()
        else:
            netsurvive.C2SHeroOpenAutoDlg()

    
    def RefreshAssignBtn(self):
        self.GetObject('btn_AutoAssign').SetShow(True)

    
    def CreateAvatatBox(self):
        iconBox = self.GetObject('box_icon')
        (x, y) = iconBox.GetPos()
        z = self.m_Photo.GetZ()
        self.m_AvatarBox = dlgstate._AvatarBox(self, 154, 213, alpha = 0)
        self.m_AvatarBox.SetZ(z + 1)
        self.m_AvatarBox.SetPos(x, y)

    
    def ShowTitleCircle(self, bShow):
        pass

    
    def OnUpGrade(self):
        usermacro.PROMPT_MSG(surviverdefine.MSG_ONUPGRADE_ERROR)

    
    def RightUp(self):
        GetGameSurviveCtrl().SwichVirStateDlg()

    
    def OnMessage(self, iMsgID):
        if iMsgID in (1, 22, 26, 27):
            usermacro.PROMPT_MSG(surviverdefine.MSG_OPERATOR_ERROR)
            return None
        
        dlgstate.CStateDialog.OnMessage(self, iMsgID)
        if iMsgID == 25:
            if not dlgmagic.g_MagicDialog:
                return None
            
            for iKey in [
                'loc_LinkText',
                'btn_HotKey',
                'btn_block',
                'btn_Equip']:
                dlgmagic.g_MagicDialog.GetObject(iKey).SetShow(False)
            
            dlgmagic.g_MagicDialog.m_LinkTextList = []
        



class CVirSumonStateDlg(dlgpet.CPetDialog):
    
    def __init__(self):
        dlgpet.CPetDialog.__init__(self)
        self.m_PetcDialog = CVirSumonAttachDlg(self)

    
    def RefreshPets(self, :/tID = None):
        import pet
        lstObj = self.GetObject('lst_summon')
        lstObj.InitPosXLst([
            10,
            105])
        preLoc = -1
        if len(lstObj.m_Items) == len(pet.g_SortPets):
            if hasattr(lstObj, 'm_VScrollBar') and lstObj.m_VScrollBar:
                preLoc = lstObj.m_VScrollBar.GetPos()
            
        
        if pet.g_SortPets:
            if not :/tID:
                :/tID = self.GetSelectPetID()
            
            lstObj.Clear()
            for p in pet.g_SortPets:
                p.m_UpdateProp = True
                self.AddPet(p)
            
        
        if :/tID:
            for oItem in lstObj.m_Items:
                if oItem.m_PID == :/tID:
                    dlgpet.SetMutex()
                    oItem.LeftUp()
                    dlgpet.RefreshMutex()
                    continue
            
        
        if preLoc != -1:
            lstObj.m_VScrollBar.SetBarPos(preLoc)
        

    
    def OnCommitPoint(self):
        total = 0
        for num in self.m_Points[:5]:
            total += num
        
        if total <= 0:
            return None
        
        selItem = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if selItem is None:
            return None
        
        if mainmenu.IsWar():
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xb5L\xaak\xa4\xc0\xb0t\xc2I\xbc\xc6\xa1I')
        else:
            import netsurvive
            netsurvive.C2SSumonAdjustPoint(selItem.m_PID, self.m_Points[:5])
            self.ClearFightPoint()
            self.m_BakPoints = [
                0,
                0,
                0,
                0,
                0,
                0]

    
    def OnRefushCommitPoint(self, iList, level):
        iCount = 0
        for i in iList:
            iCount += i
        
        sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if sel:
            import pet
            pobj = pet.GetPet(sel.m_PID)
            if pobj:
                iPoint = pobj.GetProp('m_Point')
                ilv = pobj.GetProp('m_Grade')
                if level < ilv:
                    return None
                
                iNum = iPoint / iCount
                if iNum >= 1:
                    import netsurvive
                    []([], [ i * iNum for i in iList ][:5])
                
            
        

    
    def OpenAutoAssignDlg(self):
        import netsurvive
        itemObj = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
        if itemObj:
            netsurvive.C2SOpenAutoDlg(itemObj.m_PID)
        

    
    def CreateAutoAssign(self, pid, dataDict = None):
        if not dataDict and not getattr(self, 'm_AutoAssignDlg', None):
            return None
        
        dPetPointDict = copy.deepcopy(dataDict)
        dPetPointDict['pid'] = pid
        survivemgr.GetSurviveMgr().GetPointMgr().SetPetPoint(dPetPointDict)
        if survivemgr.GetSurviveMgr().GetPointMgr().GetIsPetGetFlag():
            survivemgr.GetSurviveMgr().GetPointMgr().SetIsPetGetFlag(False)
            return None
        
        self.m_AutoAssignDlg = CAutoAssignDlg(self)
        self.m_AutoAssignDlg.SetData(pid, dataDict)

    
    def CheckShowBtn(self, point, pobj):
        dlgpet.CPetDialog.CheckShowBtn(self, point, pobj)
        self.GetObject('btn_tuijian').SetShow(False)

    
    def AddPet(self, pobj, autoselect = True):
        import pet
        lst_summon = self.GetObject('lst_summon')
        it = lst_summon.AddTextItem('%-12s%4d' % (pobj.m_Prop.m_Name, pobj.m_Prop.m_Grade))
        it.m_PID = pobj.m_ID
        if pet.GetActivatePet() == pobj:
            it.SetTextColor(interface.COLOR_260)
        
        lst_summon.ResetItems()
        lst_summon.ResetScrollBar()
        sel = combmacro.GetSelectedItemFromList(lst_summon)
        if sel is None and autoselect:
            it.Select(True)
            self.SelectPet(it.m_PID)
        
        if pet.GetActivatePet() == pobj:
            dlgpet.SetMutex()
            dlgpet.RefreshMutex()
        
        return it

    
    def OnMessage(self, msgid):
        if msgid == 2:
            self.m_RenameDlg = None
            self.SetShow(False)
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                self.m_Points = [
                    0] * 6
                self.OnShowPoints(sel.m_PID)
                self.m_BakPoints = [
                    0] * 6
            
        elif msgid == 4:
            if self.IsAutoAssignShow():
                self.OnAutoAssignClose()
            else:
                self.OpenAutoAssignDlg()
        elif msgid == 6:
            self.m_PetcDialog.ShowSwitch()
        elif msgid in (7, 13, 14, 15, 16):
            _id2attr = {
                7: 0,
                13: 1,
                14: 2,
                15: 3,
                16: 4 }
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                import pet
                pobj = pet.GetPet(sel.m_PID)
                if pobj:
                    if self.m_Points[5] + pobj.GetProp('m_Point') > 0 and self.m_Points[_id2attr[msgid]] < 255:
                        self.m_Points[_id2attr[msgid]] += 1
                        self.m_Points[5] -= 1
                        self.OnShowPoints(sel.m_PID)
                        import copy
                        self.m_BakPoints = copy.deepcopy(self.m_Points)
                        self.GetObject('btn_tuijian').SetShow(False)
                        self.GetObject('btn_Sure').SetShow(True)
                    
                
            
        elif msgid in (8, 23, 22, 20, 19):
            _id2attr = {
                8: 0,
                23: 1,
                22: 2,
                20: 3,
                19: 4 }
            sel = combmacro.GetSelectedItemFromList(self.GetObject('lst_summon'))
            if sel:
                import pet
                pobj = pet.GetPet(sel.m_PID)
                if pobj:
                    if self.m_Points[5] < 0 and self.m_Points[_id2attr[msgid]] > 0:
                        self.m_Points[_id2attr[msgid]] -= 1
                        self.m_Points[5] += 1
                        self.OnShowPoints(sel.m_PID)
                        import copy
                        self.m_BakPoints = copy.deepcopy(self.m_Points)
                        if self.m_Points == [
                            0,
                            0,
                            0,
                            0,
                            0,
                            0]:
                            point = pobj.GetProp('m_Point')
                            if pobj.m_Prop.m_Grade <= 60:
                                pass
                            self.GetObject('btn_tuijian').SetShow(point % 5 == 0)
                            self.GetObject('btn_Sure').SetShow(False)
                        else:
                            self.GetObject('btn_Sure').SetShow(True)
                            self.GetObject('btn_tuijian').SetShow(False)
                    
                
            
        elif msgid < msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE:
            pass
        elif msgid == 5:
            self.OnCommitPoint()
        elif msgid < msgid:
            pass
        elif msgid < interface.RIGHT_BUTTON_MESSAGE + 50:
            idx = msgid - interface.RIGHT_BUTTON_MESSAGE
            if idx in (7, 13, 14, 15, 16):
                self.AddAllPoints(idx)
            elif idx in (8, 23, 22, 20, 19):
                self.SubAllPoints(idx)
            
        else:
            usermacro.PROMPT_MSG(surviverdefine.MSG_OPERATOR_ERROR)



class CVirSumonAttachDlg(dlgpet.CPetcDialog):
    
    def AdjustColor(self, name, info, initColor):
        color = initColor
        if name in ('Ability_Attack', 'Ability_Defense', 'Ability_Con', 'Ability_Magic', 'Ability_Speed'):
            color = interface.COLOR_25
        
        if name == 'm_Life':
            bShow = not ('\xa5\xc3\xa5\xcd' == info)
            self.GetObject('img_Tips').SetShow(bShow)
            self.m_TipsInfo[5].SetShow(bShow)
        
        if interface.IsNewStyle() and name in ('m_AttackType', 'm_Life'):
            color = interface.COLOR_1
        
        return color



class CHeroAutoAssignDlg(dlgstate.CAutoAssignDlg):
    
    def OnSave(self):
        if mainmenu.IsWar():
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xb8\xd3\xbe\xde\xa7@')
            return None
        
        import netsurvive
        dct = self.GetEditValues()
        attrList = dct['attrList']
        bSelect = dct['bSelect']
        netsurvive.C2SHeroSetAutoPoint(dct['attrList'], bSelect)
        dataDct = {
            'attrList': attrList,
            'bSelect': bSelect }
        survivemgr.GetSurviveMgr().GetPointMgr().SetHeroPoint(dataDct)
        self.SetData(dataDct)

    
    def OnCancel(self):
        dct = { }
        dct['attrList'] = [
            0,
            0,
            0,
            0,
            0]
        dct['bSelect'] = 0
        self.SetData(dct)
        import netsurvive
        netsurvive.C2SHeroCancelAuto()



class CAutoAssignDlg(dlgpet.CAutoAssignDlg):
    
    def OnCancel(self):
        import netsurvive
        dct = { }
        dct['attrList'] = [
            0,
            0,
            0,
            0,
            0]
        dct['bSelect'] = 0
        dct['limitLevel'] = 0
        self.SetData(self.m_Pid, dct)
        netsurvive.C2SCancelAuto(self.m_Pid)

    
    def OnSave(self):
        if mainmenu.IsWar():
            usermacro.PROMPT_MSG('\xbe\xd4\xb0\xab\xa4\xa4\xa4\xa3\xaf\xe0\xb6i\xa6\xe6\xb8\xd3\xbe\xde\xa7@')
            return None
        
        import netsurvive
        attrList = []
        for idx in self.m_AttrIdxList:
            attrName = self.IDX2INFO[idx][0]
            obj = getattr(self, attrName)
            attrList.append(obj.GetNumber())
        
        bSelect = None if self.m_CheckBtn.IsSelected() else 0
        level = self.m_LevelEdit.GetNumber()
        netsurvive.C2SSetAutoPoint(self.m_Pid, attrList, bSelect, level)
        self.GetParent().OnRefushCommitPoint(attrList, level)
        survivemgr.GetSurviveMgr().GetPointMgr().SetPetPoint({
            'attrList': attrList })



class CInterfaceItem(item.CInterfaceBase):
    
    def __init__(self, parent, x, y, msgid, interfaceitems = None):
        interface.CBoxObject.__init__(self, parent, 44, 44, 16711680, 0)
        interface.CClickObject.__init__(self, msgid)
        self.m_SelBox = ui.CImage(self, 'combdialog3/\xb5\xc0\xbe\xdf\xbf\xf2/\xd1\xa1\xd6\xd0\xbf\xf2/xuanzhongkuang3.png', interface.UIPath)
        self.m_PosBox = ui.CImage(self, 'combdialog3/\xb5\xc0\xbe\xdf\xbf\xf2/\xd1\xa1\xd6\xd0\xbf\xf2/xuanzhongkuang.png', interface.UIPath)
        self.m_PosBox.SetPos(-1, -2)
        self.m_SelBox.SetPos(-1, -2)
        self.m_SelBox.SetShow(False)
        self.m_PosBox.SetShow(False)
        self.SetPos(x, y)
        self.m_Item = None
        self.m_ItemImg = None
        self.m_UsedRedMark = None
        self.m_InterfaceItems = interfaceitems
        self.m_BagID = item.ITEM_VIR_BAGS

    
    def ShowDisabledBackground(self, is_show):
        import combmacro
        if is_show:
            self.m_DisabledBG = combmacro.CIMAGE(self, 'combdialog3/\xb5\xc0\xbe\xdf\xbf\xf2/daojukuangmengban.png', interface.UIPath)
            self.m_DisabledBG.SetZ(-1)
        else:
            self.m_DisabledBG = None

    
    def ShowShadow(self, isShow = True):
        import combmacro
        if isShow:
            self.m_Shadow = combmacro.CIMAGE(self, 'combdialog3/\xb5\xc0\xbe\xdf\xbf\xf2/daojukuang1touming.png', interface.UIPath)
            self.m_Shadow.SetAlpha(144)
            self.m_Shadow.SetZ(1000)
        else:
            self.m_Shadow = None

    
    def SetItem(self, oItem):
        if oItem:
            oItem.SetHide(False)
        
        item.CInterfaceBase.SetItem(self, oItem)
        GetGameSurviveCtrl().OnItemChange()
        if self.m_PosBox.GetShow():
            self.Leave()
            self.Enter()
        

    
    def AskDesc(self, oItem):
        import netitem
        netitem.C2SVirItemString(oItem.m_ID)

    
    def Enter(self):
        '''\xb8\xcb\xb3\xc6\xb9\xef\xa4\xf1\xb3o\xb8\xcc\xbcg\xaa\xba\xab\xdc\xb6\xc3\xa1A\xa6p\xaaG\xa6\xb3\xc0u\xa4\xc6Tips\xaa\xba\xadp\xb9\xba\xa1A\xb3o\xb8\xcc\xb4N\xa6n\xc0u\xa4\xc6\xa4F'''
        
        def DoCmp(obj, pos):
            import C_sys
            import key
            if C_sys.IsKeyDown(key.VK_CTRL) and obj.GetShow():
                if not hasattr(obj, 'm_CompTips') or obj.m_CompTips is None:
                    it = item.GetTypeItemWithPos(item.ITEM_VIR_BAGS, pos)
                    obj.ClearCtrlDesc()
                    it.m_InfoExt = ''
                    import netitem
                    netitem.C2SVirItemString(it.m_ID)
                    obj.m_CompTips = dlggetinfo.ShowCompItemInfo(it, obj)
                    obj.SetAttach(obj.m_CompTips, 2)
                    obj.m_CompTips.m_OwnerTips = interface.CShadowObject(obj)
                    self.Leave()
                else:
                    obj.m_CompTips.ResetPosition()
            elif hasattr(obj, 'm_CompTips') and obj.m_CompTips:
                obj.SetAttach(None)
                obj.m_CompTips = None
                obj.SetCtrlDesc()
            
            return (pos,)

        import dlggetinfo
        if tipsclosemgr.IsHandle():
            return None
        
        self.m_PosBox.SetShow(True)
        if self.m_Item is None or self.m_ItemImg.GetShow() is False:
            return None
        
        self.m_Item.m_InfoExt = ''
        self.AskDesc(self.m_Item)
        if self.m_Item.m_Shape in dlggetinfo.SPECIAL_SHAPE:
            item.g_ItemTips = dlggetinfo.ShowRealShapeItemInfo(self.m_Item.m_Shape, self.m_Item.m_ID, self.m_Item.m_Key, self.m_Item.m_InfoExt)
        else:
            item.g_ItemTips = dlggetinfo.NewItemInfo(self.m_Item.m_ID, self.m_Item.m_Shape, self.m_Item.m_InfoExt, None, self.m_Item.m_Key)
            if hasattr(item.g_ItemTips, 'm_CompAni'):
                item.g_ItemTips.m_CompAni.Release()
            
            iItemPos = itemdata.GetEquipPos(self.m_Item.m_Shape)
            it = item.GetTypeItemWithPos(item.ITEM_VIR_BAGS, iItemPos)
            if it is not None and it.m_ID != self.m_Item.m_ID:
                item.g_ItemTips.m_CompAni = item.g_ItemTips.CreatePyCommand(5, DoCmp, iItemPos)
            
        dlggetinfo.g_ItemInfoTips[0][0] = interface.CShadowObject(item.g_ItemTips)
        item.g_ItemTips.SetOwner(self)
        tipsclosemgr.Regist(item.g_ItemTips)

    
    def OnHand(self, hand):
        import handobj
        it = None
        if hand.m_Type not in [
            handobj.TYPE_BAGS,
            handobj.TYPE_VIR_ITEM]:
            handobj.Accept()
            return None
        
        if it:
            item.PlaySound(it.m_Shape, item.SOUND_PUT)
        

    
    def Use(self):
        if self.m_Item:
            self.SurviveUseItem(self.m_Item)
        

    
    def SurviveUseItem(self, oItem):
        global g_UseMapItemFlag
        iItemShape = oItem.m_Shape
        iItemID = oItem.m_ID
        if mainmenu.IsWar():
            return None
        
        if iItemShape == surviverdefine.ITEM_SHAPE_MASQUERADE:
            world.g_UseItemID = iItemID
            world.g_SelectTips = world.CSelectTips(surviverdefine.MSG_USE_CAMOUUFLAGE)
            world.SetMessageProcess(cursor.MAGIC_ENTER_CURSOR, cursor.TEAM_LEAVE_CURSOR, IsSelectNpc, CommitUseItem, NormalSelect)
        elif iItemShape in [
            surviverdefine.ITEM_SHAPE_EXPLOSION_TRAP,
            surviverdefine.ITEM_SHAPE_FIRE_SOURCE]:
            world.g_UseItemID = iItemID
            world.g_SelectTips = world.CSelectTips(surviverdefine.MSG_USE_EXPLOSION_TRAP)
            world.SetMessageProcess(cursor.MAGIC_ENTER_CURSOR, cursor.MAGIC_ENTER_CURSOR, IsMapSelectMap, CommitUseItem, NormalSelect)
            g_UseMapItemFlag = True
        

    
    def SetItemByPos(self, pos):
        it = item.g_Items[item.ITEM_VIR_BAGS].get(pos)
        if it:
            self.SetItem(it)
        else:
            self.SetItem(None)

    
    def Take(self):
        if self.m_ItemImg is None or self.m_Item.IsHide():
            return None
        
        self.m_Item.SetHide(True)
        item.ShowItem(self.m_Item.m_Type, self.m_Pos)
        import handobj
        handobj.HandItem(self.m_Item.m_ID, self.m_InterfaceItems, None, self.Put)
        handobj.GetHand(handobj.TYPE_ITEM).m_Type = handobj.TYPE_VIR_ITEM
        item.PlaySound(self.m_Item.m_Shape, item.SOUND_TAKE)

    
    def SetPlusBackground(self, flag):
        import style
        if flag:
            imgClass = None if interface.IsNewStyle() else interface.CImagesObject
            self.m_PlusBackground = imgClass(self, style.GetPath('combdialog/\xd4\xd3\xcd\xbc/\xbc\xd3\xba\xc5.igs'), interface.UIPath)
            self.m_PlusBackground.SetZ(-1)
            interface.Center(self.m_PlusBackground)
        else:
            self.m_PlusBackground = None



class CWorldInterfaceItem(CInterfaceItem):
    
    def __init__(self, parent, x, y, msgid, interfaceitems = None):
        item.CInterfaceBase.__init__(self, parent, x, y, msgid, interfaceitems)
        self.m_BagID = 4

    
    def AskDesc(self, oItem):
        iWorldBagID = survivemgr.GetSurviveMgr().GetWorldBagID()
        if not iWorldBagID:
            return None
        
        import netsurvive
        netsurvive.C2SWorldBagDesc(iWorldBagID, oItem.m_Pos)

    
    def SetItemByPos(self, pos):
        it = item.g_Items[item.ITEM_BAGS].get(self.m_BagID, { }).get(pos)
        if it:
            self.SetItem(it)
        else:
            self.SetItem(None)

    
    def Put(self):
        if self.m_Item:
            if hasattr(self.m_Item, 'SetHide'):
                self.m_Item.SetHide(False)
            
            item.ShowItem(self.m_Item.m_Type, self.m_Pos, self.m_BagID)
            item.PlaySound(self.m_Item.m_Shape, item.SOUND_PUT)
        

    
    def Take(self):
        if self.m_ItemImg is None or self.m_Item.IsHide():
            return None
        
        self.m_Item.SetHide(True)
        item.ShowItem(self.m_Item.m_Type, self.m_Pos, self.m_BagID)
        import handobj
        handobj.HandBagItem(self.m_BagID, self.m_Pos, self.m_Item.m_Shape, self.m_InterfaceItems, None, self.Put)
        item.PlaySound(self.m_Item.m_Shape, item.SOUND_TAKE)



class CEquipInterface(CInterfaceItem):
    
    def SetEquip(self, itemID, dest = -1):
        it = item.GetItem(itemID)
        if not it:
            return False
        
        import itemdata
        import netitem
        bEquip = itemdata.IsType(it.m_Shape, 'equip')
        if not bEquip:
            return False
        
        if (dest == -1 or item.IsEquipPos(dest)) and not item.IsEquipPos(it.m_Pos):
            item.UseItem(it)
        else:
            netitem.C2SVirItemDrag(it.m_Pos, dest)
        return True

    
    def LeftUp(self):
        self.ReleaseHoldHand()
        CInterfaceItem.LeftUp(self)

    
    def LeftDown(self):
        CInterfaceItem.LeftDown(self)
        import C_sys
        import key
        if not C_sys.IsKeyDown(key.VK_SHIFT) and self.m_Item:
            self.DelayHoldHand()
        

    
    def OnHoldHand(self, hand):
        import handobj
        if hand.m_Type == handobj.TYPE_HOLDITEM and hand.m_InterfaceItems == self.m_InterfaceItems:
            if self.m_Item and hand.m_ID == self.m_Item.m_ID:
                self.LeftUp()
                return None
            
            self.SetEquip(hand.m_ID, self.m_Pos)
            
            def delayEnter(obj, itemID):
                it = item.GetItem(itemID)
                if it and obj.m_InterfaceItems[it.m_Pos].IsEnter():
                    obj.m_InterfaceItems[it.m_Pos].Enter()
                

            self.CreatePyCommand(5, delayEnter, hand.m_ID)
        

    
    def DelayHoldHand(self):
        self.ReleaseHoldHand()
        
        def hand(obj):
            import handobj
            if hasattr(obj, 'm_DelayHand') and obj.m_DelayHand and obj.m_Item and not handobj.IsHand():
                handobj.HandHoldItem(self.m_Item.m_ID, self.m_InterfaceItems, None, None)
            

        self.m_HoldHandAni = self.CreatePyCommand(6, hand)
        self.m_DelayHand = True

    
    def ReleaseHoldHand(self):
        self.m_DelayHand = False
        if hasattr(self, 'm_HoldHandAni') and self.m_HoldHandAni:
            self.m_HoldHandAni.Release()
            self.m_HoldHandAni = None
            import handobj
            handobj.Clear()
        

    
    def SetItem(self, it):
        import style
        self.m_SpecialEffect = None
        CInterfaceItem.SetItem(self, it)
        if it:
            path = 'combdialog3/\xd4\xd3\xcd\xbc/\xd7\xb0\xb1\xb8\xc0\xb8/zhuangbeikuang2.png'
            classtype = interface.CBitmapObject
            self.m_EquipBackground = classtype(self, style.GetPath(path), interface.UIPath)
            self.m_EquipBackground.SetZ(-1)
        else:
            self.m_EquipBackground = None

    
    def SetTips(self, tips1, tips2, delay = 0):
        self.m_Info = tips1
        self.m_InfoNone = tips2
        self.m_Delay = delay
        if not hasattr(self, 'm_Tips'):
            self.m_Tips = None
        
        if not hasattr(self, 'm_TipsDelay'):
            self.m_TipsDelay = None
        

    
    def RefreshSpecialEffect(self, sShow):
        
        def GetOffset():
            if interface.IsStyle1():
                return (-1, -1)
            elif interface.IsStyle2():
                return (0, 0)
            else:
                return (-3, -3)

        
        def GetPos():
            if interface.IsStyle1():
                return (1, 1)
            elif interface.IsStyle2():
                return (1, 1)
            else:
                return (2, 2)

        self.m_SpecialEffect = None
        if not sShow:
            return None
        
        if not self.m_Item and getattr(self.m_Item, 'm_InfoExt', ''):
            return None
        
        info = getattr(self.m_Item, 'm_InfoExt', '')
        import re
        val = re.search('\xad@.{1,2}\xab\xd7\\$(?P<value1>\\d+)/(?P<value2>\\d+)', info)
        if not val or int(val.group('value1')) >= 20:
            return None
        
        (w, h) = self.GetSize()
        (offw, offh) = GetOffset()
        (x, y) = GetPos()
        self.m_SpecialEffect = eff = interface.CBoxObject(self, w + offw, h + offh, interface.COLOR_25, 112)
        eff.SetPos(x, y)
        if interface.IsNewStyle():
            eff.m_Round = ui.CImage(eff, 'combdialog3/\xd4\xd3\xcd\xbc/\xd7\xb0\xb1\xb8\xc0\xb8/zhuangbeibiankuang.png', interface.UIPath)
            eff.m_Round.SetPos(-x, -y)
        

    
    def Enter(self):
        if tipsclosemgr.IsHandle():
            return None
        
        CInterfaceItem.Enter(self)
        if self.m_Info is None:
            return None
        
        
        def showtips(obj):
            import wrapinterface
            tips = obj.m_Info
            if getattr(obj, 'm_SpecialEffect', None):
                tips = ''.join([
                    obj.m_Info,
                    '#r\xb8\xd3\xb8\xcb\xb3\xc6\xad@\xa4[\xab\xd7\xa4\xa3\xa8\xac20\xa1A\xab\xd8\xc4\xb3\xb1z\xba\xc9\xa7\xd6\xad\xd7\xb2z'])
            
            if obj.m_Item is None:
                tips = obj.m_InfoNone
            
            obj.m_Tips = wrapinterface.CTextTips(obj.GetParent(), -1, tips, interface.FontLT14_3, direct = 1)
            obj.m_Tips.SetOwner(obj)

        if self.m_Delay == 0:
            showtips(self)
        else:
            self.m_TipsDelay = self.CreatePyCommand(self.m_Delay, showtips)

    
    def Leave(self):
        self.m_PosBox.SetShow(False)
        if self.m_TipsDelay:
            self.m_TipsDelay.Release()
            self.m_TipsDelay = None
        
        self.m_Tips = None
        self.SetAlpha(0)
        import item
        tipsclosemgr.CheckClose()
        item.g_ItemTips = None



class CVirBagDlg(combdialog.CCombDialog):
    '''
\t\xb5\xea\xc0\xc0\xadI\xa5]\xac\xc9\xad\xb1
\t'''
    
    def __init__(self):
        self.m_ShowDlgSound = False
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_VIR_BAG)
        interface.Center(self)
        self.m_InterfaceItems = { }
        self.m_Boxs = []
        self.m_oFakeRoleWalkerObject = None
        self.m_LastSelPos = None
        self.CreateItemAreas()
        self.CreateHeroPlayer()
        hero.AddRefreshCallback('CVirBagDlg', (('m_Desc', 0, 0), ('m_RealShape', 0, 0)), self.CreateHeroPlayer)

    
    def CreateItemAreas(self):
        self.m_Boxs = [
            (self.GetObject('area_item'), self.GetObject('area_fight'), self.GetObject('splitline'))]
        item.AddInterfaceCallback(self.m_InterfaceItems, item.ITEM_VIR_BAGS, oRefObj = self)
        self.SetEquipTips()
        combmacro.CITEMAREA(CInterfaceItem, 'area_item', self, item.ITEM_START, self.m_InterfaceItems)

    
    def SetEquipTips(self):
        import combmacro
        for i, v in enumerate(dlgitem.EQUIP_LOC):
            (objname, tip) = v
            (x, y, w, h) = self.GetLocData(objname)
            iit = CEquipInterface(self, x, y, i + 1 + 100, self.m_InterfaceItems)
            iit.Refresh(i + 1)
            iit.SetTips(tip, tip)
            combmacro.BindObject(objname, self, iit)
        

    
    def CreateHeroPlayer(self):
        import hero
        import copy
        dDesc = hero.GetProp('m_Desc', { })
        dDesc = copy.copy(dDesc)
        if 'summon' in dDesc:
            del dDesc['summon']
        
        if 'summontype' in dDesc:
            del dDesc['summontype']
        
        iShape = hero.GetProp('m_Shape', 111)
        self.m_oFakeRoleWalkerObject = walker.CFakeRole(self.GetObject('loc_EquipArea'), -1, iShape, dDesc)
        interface.Center(self.m_oFakeRoleWalkerObject, 22, 100)

    
    def UseItem(self, msgid):
        hero.AddRefreshCallback('CVirBagDlg', (('m_Desc', 0, 0), ('m_RealShape', 0, 0)), self.CreateHeroPlayer)
        import netitem
        pos = msgid - 100
        self.m_LastSelPos = pos
        if not survivemgr.GetSurviveMgr().IsInGameWarMap():
            usermacro.PROMPT_MSG('\xb9C\xc0\xb8\xb6}\xa9l\xab\xe1\xa4~\xaf\xe0\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        if pos not in self.m_InterfaceItems:
            return None
        
        it = self.m_InterfaceItems[pos]
        oItem = it.GetItem()
        if oItem is None:
            return None
        
        if oItem.m_Shape in surviverdefine.ITEM_SPECIAL_LIST:
            it.Use()
        elif oItem.m_Shape in surviverdefine.ITEM_USE_FOR_EQUIP_LIST:
            GetGameSurviveCtrl().ShowUseItemForEquitDlg(it.GetItem().m_ID, it.GetItem().m_Shape)
        else:
            netitem.C2SVirItemUse(it.GetItem().m_ID)

    
    def SelectItem(self, msgid):
        if not survivemgr.GetSurviveMgr().IsInGameWarMap():
            usermacro.PROMPT_MSG('\xb9C\xc0\xb8\xb6}\xa9l\xab\xe1\xa4~\xaf\xe0\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        pos = msgid - 100
        it = self.m_InterfaceItems[pos]
        it.Take()

    
    def OnMessage(self, msgid):
        if msgid == 2:
            self.SetShow(False)
            if GetGameSurviveCtrl().IsOpenWorldBagDlg():
                iID = survivemgr.GetSurviveMgr().GetWorldBagID()
                if iID:
                    import netsurvive
                    netsurvive.C2SCloseWorldBag(survivemgr.GetSurviveMgr().GetWorldBagID())
                
            
        elif msgid <= msgid:
            pass
        elif msgid < 600:
            self.SelectItem(msgid)
        
        msgid = msgid - interface.RIGHT_BUTTON_MESSAGE
        if msgid < msgid:
            pass
        elif msgid < 500:
            self.UseItem(msgid)
        



class CUseItemForEquitDlg(CVirBagDlg):
    '''\xb9\xef\xb8\xcb\xb3\xc6\xa8\xcf\xa5\xce\xb9D\xa8\xe3'''
    
    def __init__(self):
        self.m_ShowDlgSound = False
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_USE_FOR_EQUIT)
        interface.Center(self)
        self.m_InterfaceItems = { }
        self.m_Boxs = []
        self.m_LastSelPos = None
        self.m_iWillBeUsedID = None
        self.CreateItemAreas()
        self.CreateHeroPlayer()
        hero.AddRefreshCallback('CUseItemForEquitDlg', (('m_Desc', 0, 0), ('m_Shape', 0, 0)), self.CreateHeroPlayer)

    
    def SetUseItemID(self, iUseItemID, iUesItemShape):
        self.m_iWillBeUsedID = iUseItemID
        self.CheckValid(iUesItemShape)

    
    def CheckValid(self, iUesItemShape):
        import itemdata
        if iUesItemShape in surviverdefine.ITEM_USE_FOR_EQUIP_DATA:
            sType = surviverdefine.ITEM_USE_FOR_EQUIP_DATA[iUesItemShape]
        else:
            sType = 'equip'
        for iit in self.m_InterfaceItems.values():
            bValid = True
            if iit and iit.GetItem():
                it = iit.GetItem()
                if not itemdata.IsType(it.m_Shape, sType):
                    bValid = False
                
                iit.Enable(bValid)
                iit.ShowShadow(not bValid)
                continue
        

    
    def UseItem(self, msgid):
        import netitem
        pos = msgid - 100
        self.m_LastSelPos = pos
        if pos not in self.m_InterfaceItems:
            return None
        
        oItem = self.m_InterfaceItems[pos]
        it = oItem.GetItem()
        if it is None:
            return None
        
        if self.m_iWillBeUsedID is None:
            return None
        
        if self.m_iWillBeUsedID in surviverdefine.ITEM_USE_FOR_EQUIP_DATA:
            sType = surviverdefine.ITEM_USE_FOR_EQUIP_DATA[self.m_iWillBeUsedID]
        else:
            sType = 'equip'
        if not itemdata.IsType(it.m_Shape, sType):
            oItem.Enable(False)
            oItem.ShowShadow(True)
            return None
        else:
            netitem.C2SVirItemUse(self.m_iWillBeUsedID, oItem.GetItem().m_ID)
            GetGameSurviveCtrl().CloseUseItemForEquitDlg()

    
    def OnMessage(self, msgid):
        import usermacro
        if msgid == 2:
            GetGameSurviveCtrl().CloseUseItemForEquitDlg()
        elif msgid <= msgid:
            pass
        elif msgid < 600:
            self.UseItem(msgid)
        
        msgid = msgid - interface.RIGHT_BUTTON_MESSAGE
        if msgid < msgid:
            pass
        elif msgid < 500:
            usermacro.PROMPT_MSG(surviverdefine.MSG_USE_ITEM_FOR_EQUIT)
            return None
        



class CWarVirBagDlg(warui.CItemDialog):
    '''
\t\xbe\xd4\xb0\xab\xa4\xa4\xa8\xcf\xa5\xce\xaa\xba\xb5\xea\xc0\xc0\xadI\xa5]\xac\xc9\xad\xb1
\t'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_WAR_VIR_BAG)
        interface.Center(self)
        self.m_SelFunc = None
        self.m_InstFunc = None
        import item
        self.m_InterfaceItems = { }
        combmacro.CITEMAREA(CInterfaceItem, 'area_item', self, item.ITEM_START, self.m_InterfaceItems, 100)
        item.AddInterfaceCallback(self.m_InterfaceItems, item.ITEM_VIR_BAGS, oRefObj = self)
        self.CheckValid()
        self.CheckDrugs()

    
    def Release(self):
        import item
        item.ReleaseInterfaceCallback(self.m_InterfaceItems, item.ITEM_VIR_BAGS)

    
    def CheckValid(self):
        for iit in self.m_InterfaceItems.values():
            bValid = True
            if iit and iit.GetItem():
                it = iit.GetItem()
                if it.m_Shape not in surviverdefine.ITEM_USE_FOR_WAR_LIST:
                    bValid = False
                
                iit.Enable(bValid)
                iit.ShowShadow(not bValid)
                continue
        

    
    def OnItemSelect(self, iPos):
        import item
        oItem = item.GetTypeItemWithPos(item.ITEM_VIR_BAGS, iPos)
        if oItem is None:
            return None
        
        if self.m_InstFunc and self.m_InstFunc(oItem):
            return None
        
        warui.g_ItemID = oItem.m_ID
        if self.m_SelFunc:
            self.m_SelFunc(self.m_DoFunc, oItem.m_Shape)
            warui.EnableWarUI(False)
        

    
    def ReleaseDrugUseTimes(self, times = 8):
        '''
\t\t\xab\xcc\xbd\xaa\xb3\xd1\xbel\xc3\xc4\xc0W
\t\t'''
        pass

    
    def OnMessage(self, iMsgID):
        LOG_DEBUG('dlgsurvive OnMessage %d' % iMsgID)
        if iMsgID == 2:
            self.SetShow(False)
        elif iMsgID <= iMsgID:
            pass
        elif iMsgID < 600:
            self.OnItemSelect(iMsgID - 100)
        
        if iMsgID > interface.RIGHT_BUTTON_MESSAGE:
            iMsgID = iMsgID - interface.RIGHT_BUTTON_MESSAGE
            iPos = iMsgID - 100
            import item
            it = item.GetTypeItemWithPos(item.ITEM_VIR_BAGS, iPos)
            if it is None:
                self.SetShow(False)
            
        



class CWorldBagDlg(combdialog.CCombDialog):
    '''
\t\xa6a\xb9\xcf\xa4W\xaa\xba\xadI\xa5]\xac\xc9\xad\xb1
\t'''
    
    def GetWorldBagItemWithID(cls, iItemID):
        iBagID = 4
        for oItem in item.g_Items[item.ITEM_BAGS][iBagID].values():
            if oItem and oItem.m_ID == iItemID:
                break
                continue
        else:
            oItem = None
        if not oItem:
            raise surviverdefine.ServerError(iItemID)
        
        return oItem

    GetWorldBagItemWithID = classmethod(GetWorldBagItemWithID)
    
    def __init__(self, oRelyObject):
        self.m_ShowDlgSound = False
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_WORLD_BAG)
        self.m_oRelyObject = misc.WeakRef(oRelyObject)
        self.m_InterfaceItems = { }
        self.m_Boxs = []
        self.SetIgnoreEsc(True)
        self.m_LastSelPos = None
        self.CreateItemAreas()
        self.SetDefaultPos()

    
    def CreateItemAreas(self):
        self.m_Boxs = [
            (self.GetObject('area_item'), self.GetObject('area_fight'), self.GetObject('splitline'))]
        item.AddInterfaceCallback(self.m_InterfaceItems, item.ITEM_BAGS, oRefObj = self)
        combmacro.CITEMAREA(CWorldInterfaceItem, 'area_item', self, 1, self.m_InterfaceItems)

    
    def UseItem(self, msgid):
        import netsurvive
        pos = msgid - 100
        it = self.m_InterfaceItems[pos]
        oNowItem = it.GetItem()
        if not oNowItem:
            return None
        
        iWorldBagID = survivemgr.GetSurviveMgr().GetWorldBagID()
        if not iWorldBagID:
            return None
        
        if itemdata.IsType(oNowItem.m_Shape, 'equip'):
            netsurvive.C2SWorldBagUseItem(iWorldBagID, oNowItem.m_Pos)
        else:
            iWorldBagID = survivemgr.GetSurviveMgr().GetWorldBagID()
            if iWorldBagID:
                netsurvive.C2SWorldBagExcPos(iWorldBagID, oNowItem.m_Pos, item.ITEM_VIR_BAGS, 0)
            

    
    def SelectItem(self, msgid):
        pos = msgid - 100
        it = self.m_InterfaceItems[pos]
        it.Take()

    
    def SetDefaultPos(self, offx = 0, offy = 0):
        oRelyObj = self.m_oRelyObject.Get()
        if not oRelyObj or not oRelyObj.GetShow():
            interface.Center(self)
        else:
            import ratio
            iMaxW = ratio.WINDOW_WIDTH
            (w, _) = oRelyObj.GetSize()
            (x, y) = oRelyObj.GetPos()
            (ow, _) = self.GetSize()
            if x + w + offx + ow / 2 <= iMaxW:
                self.SetPos(w + offx + x, offy + y)
            else:
                self.SetPos(-w + offx + x, offy + y)

    
    def OnMessage(self, msgid):
        if msgid == 2:
            import netsurvive
            import mainmenu
            iID = survivemgr.GetSurviveMgr().GetWorldBagID()
            if iID:
                netsurvive.C2SCloseWorldBag(survivemgr.GetSurviveMgr().GetWorldBagID())
            else:
                GetGameSurviveCtrl().CloseWorldBagDlg()
            if mainmenu.IsWar():
                GetGameSurviveCtrl().CloseWorldBagDlg()
            
        elif msgid <= msgid:
            pass
        elif msgid < 600:
            self.SelectItem(msgid)
        
        msgid = msgid - interface.RIGHT_BUTTON_MESSAGE
        if msgid < msgid:
            pass
        elif msgid < 600:
            self.UseItem(msgid)
        



class CPlayerNumPalDlg(combdialog.CCombDialog):
    '''\xc5\xe3\xa5\xdc\xb7\xed\xabe\xaa\xb1\xaea\xb3\xd1\xbel\xaa\xb1\xaea\xbc\xd0\xc5\xd2'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_LAST_PROSNED_TIPS)
        self.m_iNowNum = 0
        self.m_iAllNum = 0
        self.m_iNowType = 0
        self.m_iKillNum = 0
        self.m_iNowMark = 0
        self.m_iMinnet = 0
        self.m_iSencond = 0
        self.m_oBox = None
        self.SetIgnoreEsc(True)
        self.m_Timer = None
        self.GetObject('btn_max').SetShow(False)
        self.SetPos(40, 55)
        self.m_TestInfoData = {
            'loc_people': None,
            'loc_alarm': None,
            'loc_kill': None,
            'loc_score': None }
        self.RegistSlot()
        self.InitData()
        self.InitTest()

    
    def RegistSlot(self):
        oSurviveMgr = survivemgr.GetSurviveMgr()
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateInGameData, self.OnInGameData)
        oSurviveMgr.ssConnect(oSurviveMgr.SS_UpdateWeather, self.OnWeatherChange)

    
    def InitData(self):
        import map
        oMgr = survivemgr.GetSurviveMgr()
        iMapID = map.GetCurrentMapID()
        iMapPos = surviverdefine.GetSceneIDWithMapID(iMapID)
        self.m_iNowNum = oMgr.GetInGameData('\xb3\xd1\xbel\xa4H\xbc\xc6')
        self.m_iAllNum = oMgr.GetInGameData('\xaa\xb1\xaea\xc1`\xbc\xc6')
        self.m_iKillNum = oMgr.GetInGameData('\xc0\xbb\xb1\xfe\xa4H\xbc\xc6')
        self.m_iNowMark = oMgr.GetInGameData('\xb7\xed\xabe\xbfn\xa4\xc0')
        self.m_iMinnet = oMgr.GetInGameData('\xb3\xd1\xbel\xae\xc9\xb6\xa1') / 60
        self.m_iSencond = oMgr.GetInGameData('\xb3\xd1\xbel\xae\xc9\xb6\xa1') % 60
        self.m_iNowType = oMgr.GetWeatherData(iMapPos)
        self.CreateBgBox()

    
    def CreateBgBox(self):
        self.GetObject('bg').SetShow(False)
        (iW, iH) = self.GetObject('bg').GetSize()
        self.m_oBox = interface.CBoxObject(self, iW, iH, 0, 80)
        self.m_oBox.SetPos(*self.GetObject('bg').GetPos())
        self.m_oBox.SetZ(self.GetObject('bg').GetZ())
        self.m_oBox.SetShow(not self.GetObject('btn_max').GetShow())

    
    def InitTest(self):
        self.SetText()
        self.StartTimer()

    
    def SetText(self):
        oPraent = self.GetObject('loc_people')
        tData = self.GetLocData('loc_people')
        sTest = '%d/%d' % (self.m_iNowNum, self.m_iAllNum)
        oTest = interface.CRichTextObject(oPraent, tData[2], interface.FontLT14, sTest, 16776960)
        interface.Center(oTest)
        self.m_TestInfoData['loc_people'] = oTest
        oPraent = self.GetObject('loc_kill')
        tData = self.GetLocData('loc_kill')
        sTest = '%d' % self.m_iKillNum
        oTest = interface.CRichTextObject(oPraent, tData[2], interface.FontLT14, sTest, 16776960)
        interface.Center(oTest)
        self.m_TestInfoData['loc_kill'] = oTest
        oPraent = self.GetObject('loc_score')
        tData = self.GetLocData('loc_score')
        sTest = '%d' % self.m_iNowMark
        oTest = interface.CRichTextObject(oPraent, tData[2], interface.FontLT14, sTest, 16776960)
        interface.Center(oTest)
        self.m_TestInfoData['loc_score'] = oTest

    
    def SetTimeText(self):
        oPraent = self.GetObject('loc_alarm')
        tData = self.GetLocData('loc_alarm')
        if GetGameSurviveCtrl().m_bIsShowSnowGril:
            sTest = '\xa5\xdf\xa7Y\xa8\xec\xb3\xb7\xa4k\xa8\xad\xc3\xe4\xa1I\xa1I\xa1I'
        elif self.m_iNowType == surviverdefine.TYPE_WEATHER_SNOW:
            sTest = '\xa5\xdf\xa7Y\xb0k\xc2\xf7\xbc\xc9\xb3\xb7\xb0\xcf\xb0\xec\xa1I\xa1I\xa1I'
        else:
            sTest = '\xb6Z\xc2\xf7\xa4U\xa6\xb8\xbc\xc9\xb3\xb7\xc1\xd9\xb3\xd1#R%d#n\xa4\xc0#R%d#n\xac\xed' % (self.m_iMinnet, self.m_iSencond)
        oTest = interface.CRichTextObject(oPraent, tData[2] + 100, interface.FontLT14, sTest, 16776960)
        interface.Center(oTest)
        self.m_TestInfoData['loc_alarm'] = oTest

    
    def StartTimer(self):
        import timer
        self.EndTimer()
        self.m_Timer = timer.Timer(1, self.OnTimerLoop, -1)

    
    def EndTimer(self):
        if self.m_Timer:
            self.m_Timer.Release()
            self.m_Timer = None
        

    
    def OnInGameData(self, sKey, iNum):
        PRINT(sKey, iNum)
        self.InitData()
        self.InitTest()

    
    def OnTimerLoop(self):
        self.SetTimeText()

    
    def OnWeatherChange(self, iSceneID, iWeatherType):
        self.InitData()
        self.InitTest()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            GetGameSurviveCtrl().SwichWorldMap()
        
        if msgid == 2:
            GetGameSurviveCtrl().ShowQuickOperateDlg()
        elif msgid == 6:
            for obj in self.m_Frames.values():
                obj.SetShow(False)
            
            for obj in self.m_TestInfoData.values():
                if obj:
                    obj.SetShow(False)
                    continue
            
            self.m_oBox.SetShow(False)
            self.GetObject('btn_max').SetShow(True)
            self.GetObject('bg').SetShow(False)
        elif msgid == 7:
            for obj in self.m_Frames.values():
                obj.SetShow(True)
            
            for obj in self.m_TestInfoData.values():
                if obj:
                    obj.SetShow(True)
                    continue
            
            self.m_oBox.SetShow(True)
            self.GetObject('bg').SetShow(False)
            self.GetObject('btn_max').SetShow(False)
        



class CRichTextWithTips(interface.CBoxObject, interface.CBase):
    
    def __init__(self, oParent, iW, iH, sTips):
        interface.CBoxObject.__init__(self, oParent, iW, iH, 16776960, 0)
        self.MessageProcess()
        self.m_sTip = sTips
        self.m_oTipObj = None
        self.m_oText = None

    
    def SetText(self, sText):
        self.m_oText = interface.CRichTextObject(self, 100, interface.FontLT16_1, sText, 4147404)
        interface.Center(self.m_oText, offsety = 2)

    
    def Enter(self):
        if not self.m_sTip:
            return None
        
        self.m_oTipObj = wrapinterface.CTextTips(self.GetParent(), -1, self.m_sTip, interface.FontLT14_3, direct = 1)
        self.m_oTipObj.SetOwner(self)

    
    def Leave(self):
        self.m_oTipObj = None



class CGameOverDlg(combdialog.CCombDialog):
    '''\xb9C\xc0\xb8\xb5\xb2\xba\xe2\xac\xc9\xad\xb1'''
    
    def __init__(self):
        import ratio
        combdialog.CCombDialog.__init__(self, interface.TopmostPanel, surviverdefine.PATH_DLG_GAME_END)
        self.m_BoxPal = interface.CBoxObject(interface.TopmostPanel, ratio.WINDOW_WIDTH, ratio.WINDOW_HEIGHT, 0, 170)
        self.Capture(1)
        self.m_TextData = { }
        self.m_oTipsList = []
        self.SetTextInfo()

    
    def SetTextInfo(self):
        dGameEndInfo = survivemgr.GetSurviveMgr().GetGameEndInfo()
        if dGameEndInfo[surviverdefine.GAME_END_I_RANK] == 1:
            sMsg = surviverdefine.MSG_GAME_END_WIN
        else:
            sMsg = surviverdefine.MSG_GAME_END_LOST
        iFontID = interface.FontLT16_1
        iFontColor = 1787472
        sShowData = {
            'loc_kill_player': ('%s\xa4H\xa1A\xc0\xf2\xb1o#R%s#n\xbfn\xa4\xc0' % (dGameEndInfo[surviverdefine.GAME_END_I_KILLEDMAN], dGameEndInfo[surviverdefine.GAME_END_I_SCORE4]), iFontID, iFontColor),
            'loc_reward': ('\xb2\xc4%s\xa6W\xa1A\xc0\xf2\xb1o#R%s#n\xbfn\xa4\xc0' % (dGameEndInfo[surviverdefine.GAME_END_I_RANK], dGameEndInfo[surviverdefine.GAME_END_I_SCORE5]), iFontID, iFontColor),
            'loc_integral': ('#R%s#n\xa4\xc0' % dGameEndInfo[surviverdefine.GAME_END_I_TOTALSCORE], iFontID, iFontColor),
            'loc_kill_npc': ('%s\xacP*0.4=#R%s#n\xa4\xc0' % (dGameEndInfo[surviverdefine.GAME_END_I_MONSTERSTAR], dGameEndInfo[surviverdefine.GAME_END_I_SCORE3]), iFontID, iFontColor),
            'loc_box': ('%s\xad\xd3*1=#R%s#n\xa4\xc0' % (dGameEndInfo[surviverdefine.GAME_END_I_OPENBOX], dGameEndInfo[surviverdefine.GAME_END_I_SCORE2]), iFontID, iFontColor),
            'loc_time': ('%s\xa4\xc0\xc4\xc1*1=#R%s#n\xa4\xc0' % (dGameEndInfo[surviverdefine.GAME_END_I_LIFETIME] / 60, dGameEndInfo[surviverdefine.GAME_END_I_SCORE1]), iFontID, iFontColor),
            'loc_title': (sMsg, iFontID, iFontColor) }
        for sObjName, tInfo in sShowData.iteritems():
            oTextObj = interface.CRichTextObject(self.GetObject(sObjName), 300, tInfo[1], tInfo[0], tInfo[2])
            interface.CenterLeft(oTextObj)
            self.m_TextData[sObjName] = oTextObj
        
        self.SetTipsInfo(dGameEndInfo[surviverdefine.GAME_END_L_TIPS])

    
    def SetTipsInfo(self, iTipsList):
        '''\xb3]\xb8m\xc0\xf2\xb1o\xaa\xba\xb5\xfb\xbb\xf9'''
        i = 0
        for iNum in iTipsList:
            if iNum not in surviverdefine.TIPS_LIST:
                continue
            
            i += 1
            if i > 6:
                break
            
            dData = surviverdefine.TIPS_LIST[iNum]
            oLoc = self.GetObject('loc_tips_%d' % i)
            tSize = oLoc.GetSize()
            oTest = CRichTextWithTips(oLoc, tSize[0], tSize[1], dData['sTips'])
            interface.Center(oTest)
            oTest.SetText(dData['sName'])
            self.m_oTipsList.append(oTest)
        

    
    def OnMessage(self, msgid):
        if msgid == 1:
            GetGameSurviveCtrl().CloseGameOverDlg()
        



class CSurviveAdviceDlg(combdialog.CCombDialog):
    '''\xb7N\xa8\xa3\xa4\xcf\xf5X\xac\xc9\xad\xb1'''
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, surviverdefine.PATH_DLG_ADVICE)
        self.m_ContentEdit = None
        self.InitDialog()

    
    def InitDialog(self):
        self.m_ContentEdit = combmacro.CMLEDIT(interface.CMultilineEdit, 'loc', self, interface.COLOR_1, interface.FontLT14_3, 0, interface.COLOR_3)
        self.m_ContentEdit.Active(True)
        self.m_ContentEdit.SetLimit(200)

    
    def CloseWindow(self):
        GetGameSurviveCtrl().CloseSurviveAdviceDlg()

    
    def OnSubmit(self):
        content = self.m_ContentEdit.GetText()
        if len(content) <= 15:
            usermacro.PROMPT_MSG(surviverdefine.MSG_ADVICE_WORD_LESS)
            return None
        
        if not banword.IsValidChat(content)[0]:
            usermacro.PROMPT_MSG(surviverdefine.MSG_ADVICE_WORD_BAN)
            return None
        
        import netsurvive
        netsurvive.C2SSendSurviveAdvice(content)
        usermacro.PROMPT_MSG(surviverdefine.MSG_ADVICE_SUCCESS)
        self.CloseWindow()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.OnSubmit()
        



class CSnowGirlCtrl(object):
    '''\xb3\xb7\xa4k\xb1\xb1\xa8\xee\xbe\xb9\xa1A\xa4\xf5\xb5K\xb1\xb1\xa8\xee\xbe\xb9'''
    
    def Test(cls):
        '''
\t\timport dlgsurvive as a
\t\ta.CSnowGirlCtrl.Test()
\t\t'''
        (iPosX, iPosY) = hero.GetHeroPos()
        (iPosX, iPosY) = map.GetGameMapObject().ClientPos2ServerPos(iPosX, iPosY)
        cls.m_Test = cls(iPosX, iPosY)
        cls.m_Test.SetDisInfo(surviverdefine.TYPE_FIRE, 11, 111)
        cls.m_Test.InitSnowGirl()

    Test = classmethod(Test)
    
    def __init__(self, iPosX, iPosY):
        (iPosX, iPosY) = map.GetGameMapObject().ServerPos2ClientPos(iPosX, iPosY)
        self.m_iPosX = iPosX
        self.m_iPosY = iPosY
        self.m_iRadius = None
        self.m_iEff = None
        self.m_iID = None
        self.m_iScene = None
        self.m_bIn = False
        self.m_tPosLiat = []
        self.m_oObj = []

    
    def InitSnowGirl(self):
        '''\xb3\xb7\xa4k\xaa\xec\xa9l\xa4\xc6'''
        self.ShowSnowAround()
        self.InitCBs()

    
    def Clear(self):
        self.ClearCBs()

    
    def InitCBs(self):
        commoncb.RegistCB(commoncb.HERO_CHANGEPOS, self, 'OnHeroPosChange')

    
    def ClearCBs(self):
        commoncb.RemoveCB(commoncb.HERO_CHANGEPOS, self, 'OnHeroPosChange')

    
    def OnHeroPosChange(self, x, y):
        import netsurvive
        oMap = map.GetGameMapObject()
        if not oMap:
            return None
        
        (x, y) = oMap.ServerPos2ClientPos(x, y)
        bIn = wrapmath.PtInPolygon((x, y), self.m_tPosLiat)
        if bIn == self.m_bIn:
            return None
        
        self.m_bIn = bIn
        netsurvive.C2SCollide(self.m_iID, self.m_bIn)

    
    def SetDisInfo(self, iEff, iID, iScene):
        '''\xb3]\xb8m\xb1\xb1\xa8\xee\xa6^\xbd\xd5'''
        self.m_iEff = iEff
        self.m_iID = iID
        self.m_iScene = iScene

    
    def CreateMapObject(self):
        if self.m_iEff == surviverdefine.TYPE_SNOW_GIRL:
            return interface.CMapSpriteObject(map.GetGameMapObject(), '8041/stand.spr', chardefine.PCK_CHAR)
        elif self.m_iEff == surviverdefine.TYPE_FIRE:
            return interface.CMapSpriteObject(map.GetGameMapObject(), '6002.spr', 'goods')
        else:
            LOG_ERR('\xc3\xfe\xab\xac\xa5X\xb2{\xb0\xdd\xc3D', self.m_iEff)

    
    def ShowSnowAround(self):
        if self.m_iEff == surviverdefine.TYPE_SNOW_GIRL:
            self.m_iRadius = 400
        elif self.m_iEff == surviverdefine.TYPE_FIRE:
            self.m_iRadius = 200
        else:
            raise surviverdefine.ServerError('\xc3\xfe\xab\xac\xa4\xa3\xa4\xc7\xb0t_%s' % self.m_iEff)
        self.m_tPosLiat = []
        iA = 1 * self.m_iRadius
        iB = 0.5 * self.m_iRadius
        for iNum in range(16):
            iRad = iNum * float(2 * math.pi) / 16
            iPosX = self.m_iPosX + iA * math.cos(iRad)
            iPosY = self.m_iPosY - iB * math.sin(iRad)
            self.m_tPosLiat.append((iPosX, iPosY))
        
        for iPosX, iPosY in self.m_tPosLiat:
            oBox = self.CreateMapObject()
            oBox.CreateCommand(0, 'animation')
            oBox.m_Shadow = interface.CMapImagesObject(oBox, 'shadow.igs', chardefine.PCK_CHAR)
            oBox.m_Shadow.SetZ(-1)
            oBox.m_Shadow.SetPos(0, -20)
            oBox.SetPos(int(iPosX), int(iPosY) + 20)
            self.m_oObj.append(oBox)
        

    
    def OnPlayerEnter(self):
        pass



def PlayMagicEffect(parent, id, x, y):
    timeobj = interface.CBaseObject(None)
    if netmap.IsShowMagic(parent):
        
        try:
            ms = magicmgr.CMagicObject(parent, '%.4da.mgc' % id, x - 400, y - 380, 10000)
        except:
            ms = None

        if not ms:
            
            try:
                ms = magicmgr.CMagicObject(parent, '%.4db.mgc' % id, x - 400, y - 380, 10000)
            ms = None

        
        if not ms:
            
            try:
                ms = magicmgr.CMagicObject(parent, '%.4d.mgc' % id, x, y, 10000)
            ms = None

        
        if not ms:
            ms = magicmgr.CMagicObject(parent, '1001.mgc', x, y, 10000)
        
        timeobj.ms = ms
        
        def NextFrame(obj, f, shadow):
            if shadow.Get() and obj.ms.NextFrame(f, True):
                if not GetGameSurviveCtrl().m_bIsShowMagic:
                    netmap.g_MagicEffect.remove(obj)
                    return None
                
                return (f + 1, shadow)
            else:
                return (0, shadow)

        timeobj.CreatePyCommand(1, NextFrame, 0, interface.CShadowObject(parent))
        netmap.g_MagicEffect.append(timeobj)
    


class CSuperBoxMagicCtrl(object):
    
    def Test(cls):
        import hero
        cls.s_Test = cls()
        cls.s_Test.SetLastTime(10)
        cls.s_Test.StartMagic(*hero.GetHeroPos())

    Test = classmethod(Test)
    
    def __init__(self):
        self.m_iTimeList = [
            (60, 5, 756),
            (5, 0, 23420)]
        self.m_iLastTime = 0
        self.m_bChangeFlag = False
        self.m_iNowID = None
        self.m_oTimer = None
        self.m_iPosX = 0
        self.m_iPosY = 0

    
    def SetLastTime(self, iTime):
        self.m_iLastTime = iTime

    
    def StartMagic(self, x, y):
        self.m_iPosX = x
        self.m_iPosY = y
        self.StartTime()
        for iTimeStar, iTimeEnd, iID in self.m_iTimeList:
            if self.m_iLastTime >= self.m_iLastTime:
                pass
            elif self.m_iLastTime > iTimeEnd:
                self.PlayMagicEffect(iID, x, y)
                self.m_iNowID = iID
                break
                continue
        elif self.m_oTimer:
            self.m_oTimer.Release()
        

    
    def OnChangeMagic(self):
        self.m_bChangeFlag = False
        for iTimeStar, iTimeEnd, iID in self.m_iTimeList:
            if self.m_iLastTime >= self.m_iLastTime:
                pass
            elif self.m_iLastTime > iTimeEnd:
                self.m_iNowID = iID
                self.PlayMagicEffect(iID, self.m_iPosX, self.m_iPosY)
                continue
        

    
    def ClreaMagic(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
        

    
    def StartTime(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = timer.Timer(1, self.OnTime, -1)

    
    def OnTime(self):
        self.m_iLastTime -= 1
        LOG_DEBUG(self.m_iLastTime)
        for iTimeStar, iTimeEnd, iID in self.m_iTimeList:
            if self.m_iLastTime >= self.m_iLastTime:
                pass
            elif self.m_iLastTime > iTimeEnd:
                if self.m_iNowID != iID:
                    self.m_bChangeFlag = True
                    break
                
            self.m_iNowID != iID
        
        if self.m_iLastTime <= 0:
            if self.m_oTimer:
                self.m_oTimer.Release()
            
        

    
    def PlayMagicEffect(self, id, x, y):
        if id == 756:
            y += 100
        
        oMap = map.GetGameMapObject()
        timeobj = interface.CBaseObject(None)
        if netmap.IsShowMagic(oMap):
            
            try:
                ms = magicmgr.CMagicObject(oMap, '%.4da.mgc' % id, x - 400, y - 380, 10000)
            except:
                ms = None

            if not ms:
                
                try:
                    ms = magicmgr.CMagicObject(oMap, '%.4db.mgc' % id, x - 400, y - 380, 10000)
                ms = None

            
            if not ms:
                
                try:
                    ms = magicmgr.CMagicObject(oMap, '%.4d.mgc' % id, x, y, 10000)
                ms = None

            
            if not ms:
                ms = magicmgr.CMagicObject(oMap, '1001.mgc', x, y, 10000)
            
            timeobj.ms = ms
            
            def NextFrame(obj, f, shadow, oCtrl):
                if not oCtrl.Get():
                    netmap.g_MagicEffect.remove(obj)
                    return None
                
                if oCtrl.Get().m_bChangeFlag:
                    netmap.g_MagicEffect.remove(obj)
                    oCtrl.Get().OnChangeMagic()
                
                if shadow.Get() and obj.ms.NextFrame(f, True):
                    return (f + 1, shadow, oCtrl)
                elif obj in netmap.g_MagicEffect:
                    netmap.g_MagicEffect.remove(obj)
                
                if oCtrl.Get().m_iNowID == 23420:
                    return None
                
                oCtrl.Get().OnChangeMagic()

            if id == 23420:
                if self.m_iLastTime >= 5:
                    iFrame = 0
                else:
                    iFrame = self.m_iLastTime * 30
            else:
                iFrame = 0
            timeobj.CreatePyCommand(1, NextFrame, iFrame, interface.CShadowObject(oMap), misc.WeakRef(self))
            netmap.g_MagicEffect.append(timeobj)
        



def PlayerRightDown(oPlayer):
    if survivemgr.GetSurviveMgr().IsInSurviveGame():
        dDesc = oPlayer.GetOrigDesc()
        if 'summon' in dDesc and dDesc['summon'] in range(101, 113):
            return True
        
        walker.CWalker.RightDown(oPlayer)
        if not world.OnMessageProcess():
            pass
        
        mainmenu.SetTarget(oPlayer)
        return True
    else:
        return False


def PlayerEnter(oPlayer):
    if survivemgr.GetSurviveMgr().IsInSurviveGame():
        dDesc = oPlayer.GetOrigDesc()
        if 'summon' in dDesc and dDesc['summon'] in range(101, 113):
            if world.g_ConverCondition and world.g_ConverCondition(oPlayer) and world.g_LeftClickCallback:
                walker.CWalker.LeftUp(oPlayer)
                return False
            
            import cursor
            walker.CWalker.Enter(oPlayer)
            cursor.Load(cursor.CHAT_CURSOR)
            return True
        else:
            return False
    else:
        return False


def PlayerLeave(oPlayer):
    if survivemgr.GetSurviveMgr().IsInSurviveGame():
        dDesc = oPlayer.GetOrigDesc()
        if 'summon' in dDesc and dDesc['summon'] in range(101, 113):
            if world.g_ConverCondition and world.g_ConverCondition(oPlayer) and world.g_LeftClickCallback:
                walker.CWalker.LeftUp(oPlayer)
                return False
            
            import cursor
            walker.CWalker.Leave(oPlayer)
            if cursor.g_CurrCursor != cursor.NORMAL_CURSOR:
                cursor.Load(cursor.NORMAL_CURSOR)
            
            return True
        else:
            return False
    else:
        return False


def MapAniCAniSetAniShow(self, filename, x, y):
    if filename == 'ani\\\xb4\xab\xcb\xcd\xb5\xe3.spr' and survivemgr.GetSurviveMgr().IsInSurviveGame():
        self.SetShow(False)
    else:
        g_Func['mapani.CAni.SetAniShow'](self, filename, x, y)


def OpenWarBagDlg(selfunc, dofunc, instfunc = None):
    import warui
    
    try:
        if survivemgr.GetSurviveMgr().IsInSurviveGame():
            warui.g_ItemDialog = CWarVirBagDlg()
        else:
            warui.g_ItemDialog.SetShow(not warui.g_ItemDialog.GetShow())
    except:
        if survivemgr.GetSurviveMgr().IsInSurviveGame():
            warui.g_ItemDialog = CWarVirBagDlg()
        else:
            warui.g_ItemDialog = warui.CItemDialog()

    warui.g_ItemDialog.SetFunc(selfunc, dofunc, instfunc)
    warui.g_ItemDialog.ReleaseDrugUseTimes(warui.GetDrugUseTimes())


def MapAllowMove():
    global g_UseMapItemFlag
    if g_UseMapItemFlag:
        g_UseMapItemFlag = False
        IsSelectMap()
        return False
    
    return g_Func['map.AllowMove']


def DlgTaskFollowCTaskFrameSetShow(self, bShow):
    bShow = False
    g_Func['dlgtaskfollow.CTaskFrame.SetShow'](self, bShow)


def GetWeaponShape():
    return item.GeTypeWeaponShape(item.ITEM_VIR_BAGS)


def ShowSwitchError(*args):
    LOG_DEBUG(args)
    usermacro.PROMPT_MSG(surviverdefine.MSG_OPERATOR_ERROR)


def PRINT(*args):
    pass
