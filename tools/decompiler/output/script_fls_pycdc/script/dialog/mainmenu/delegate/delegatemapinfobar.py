# pycdc 交叉复核产物 · script.fls entry 518
# co_filename(原始)='script/dialog/mainmenu/delegate/delegatemapinfobar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_518.pyc (Python 2.5)

import clickcounter
import hero
import mainmenuctrldata
import md2019double12shop
import mdguide
from mainmenudefines import *
import commoncb
import misc
import delegatebase
import mdpresentcenter
import dlgpresentcenter

class CPosTxtDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xa4H\xaa\xab\xa6\xec\xb8m\xa4\xe5\xa6r\xc5\xe3\xa5\xdc
\t'''
    
    def Init(self):
        oModel = GetModel()
        oModel.ssConnect(oModel.SS_HeroPosChange, self.OnHeroPosChange)
        self.OnHeroPosChange()

    
    def OnHeroPosChange(self):
        import dlgmap
        (x, y) = GetModel().GetHeroPos()
        dlgmap.SetHeroPos(x, y)
        dlgmap.UpdateHeroPosition()
        self.GetView().SetPosTxt(x, y)



class CMapNameDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xa6a\xb9\xcf\xa6W\xa6r\xa4\xe5\xa6r\xc5\xe3\xa5\xdc
\t'''
    
    def Init(self):
        oModel = GetModel()
        oModel.ssConnect(oModel.SS_MapInfoChange, self.OnMapChange)
        self.OnMapChange()

    
    def OnMapChange(self):
        import dlgmap
        sMapName = GetModel().GetMapName()
        dlgmap.SetMapName(sMapName)
        self.GetView().UpdateMapName(sMapName)



class CMapInAndOutDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xab\xb0\xc2\xed/\xb3\xa5\xa5~\xb9\xcf\xa4\xf9\xa4\xc1\xb4\xab
\t'''
    INSIDE_SCENEID = (1025, 1002, 1003, 1001, 1020, 1021, 1019, 1008, 1009, 1007, 1014, 1015, 1013, 1054, 2201, 2202, 9919, 9200, 9444, 1026, 1027, 30, 1080, 1084, 1085, 1086, 1087, 1156, 1157, 1120, 1121, 9169, 9050, 9170, 9942, 9338, 9339, 2151, 2152, 2153, 9350, 9351, 9352, 9386)
    
    def Init(self):
        oModel = GetModel()
        oModel.ssConnect(oModel.SS_MapInfoChange, self.OnMapChange)

    
    def OnMapChange(self):
        iSceneID = GetModel().GetSceneID()
        bInSide = iSceneID in self.INSIDE_SCENEID
        self.GetView().UpdateSceneImg(bInSide)



class CRedPointDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xab\xf6\xb6s\xaa\xba\xac\xf5\xc2I
\t'''
    
    def Init(self):
        import mdpresentcenter
        import hero
        self.GetView().ssConnect(self.GetView().SS_BtnClick, self.OnBtnClick)
        GetModel().ssConnect(GetModel().SS_RedPointStateChange, self.OnRedPointState)
        oPresentModel = mdpresentcenter.GetRedPointModel()
        oPresentModel.ssConnect(oPresentModel.SS_PresentRPChange, self.OnPresentCenterRedPotinState)
        self.OnPresentCenterRedPotinState()
        import mdguide
        oModel = mdguide.GetCGuideMgr()
        oModel.ssConnect(oModel.SS_UpdateGuideID, self.OnUpdateGuideID)
        hero.AddRefreshCallback('CRedPointDelegate', (('m_Grade',),), self.OnGradeUp)
        import commoncb
        commoncb.RegistCB(commoncb.WAR_START, self, 'OnWarStart')
        commoncb.RegistCB(commoncb.WAR_END, self, 'OnWarEnd')
        import mdredpoint
        oModel = mdredpoint.GetCRedPointModel()
        oModel.ssConnect(oModel.SS_UpdateRedPoint, self.OnGoldShopRedDotUpdate)
        import mdconsignmallredpoint
        oModel = mdconsignmallredpoint.GetCConsignmallRedPointMgr()
        oModel.ssConnect(oModel.SS_UpdateKindARedPoint, self.OnConsignmallRedDotUpdate)

    
    def OnConsignmallRedDotUpdate(self, bShow):
        import model_mapinfobar
        oModelMapInfoBar = model_mapinfobar.GetModel()
        oModelMapInfoBar.SetConsignmallRedPoint(bShow)

    
    def OnGoldShopRedDotUpdate(self, iType, bRed, iNum):
        import netreddot
        import model_mapinfobar
        import dlgshopmain
        if iType in (netreddot.DOUBLEELEVEN, netreddot.AVATARFRAMESHOP, netreddot.SHOP_WEEKGIFT) and bRed:
            oModelMapInfoBar = model_mapinfobar.GetModel()
            oModelMapInfoBar.SetGoldShopRedPoint(bRed)
        
        if iType == netreddot.CHARGE_REWARD and bRed and not dlgshopmain.IsOpen():
            oModelMapInfoBar = model_mapinfobar.GetModel()
            oModelMapInfoBar.SetGoldShopRedPoint(bRed)
        

    
    def OnUpdateGuideID(self, iGuideID):
        if iGuideID != 2:
            return None
        

    
    def OnGradeUp(self):
        import hero
        import presentcenterdefines
        iGrade = hero.GetProp('m_Grade')
        bFlyFlag = hero.GetProp('m_FlyFlag')
        if not bFlyFlag and hero.IsLevelChange():
            if iGrade >= 10:
                pass
            elif False and iGrade not in presentcenterdefines.REWARD_HIDEMASK:
                self.SetPresentCenterRedDotShow(True)
            

    
    def OnPresentCenterRedPotinState(self, bShow = None):
        import mdpresentcenter
        if bShow is None:
            bShow = mdpresentcenter.GetRedPointModel().IsPresentRedPointShow()
        
        self.SetPresentCenterRedDotShow(bShow)

    
    def ShowPersentCenterTips(self, bShow):
        self.GetView().NotifyPersentCenterTips(bShow)

    
    def OnPresentCenterClick(self, bShow = None):
        import mdpresentcenter
        if bShow is None:
            bShow = mdpresentcenter.GetRedPointModel().IsPresentRedPointShow()
        
        self.SetPresentCenterRedDotShow(bShow)
        self.GetView().NotifyPersentCenterTips(False)

    
    def SetPresentCenterRedDotShow(self, bShow):
        if misc.IsInKuafuServer():
            self.GetView().NotifyPersentCenterRedDot(False)
        else:
            self.GetView().NotifyPersentCenterRedDot(bShow)

    
    def OnRedPointState(self, iType, bShow):
        if iType == REDPOINT_GOLDSHOP:
            self.GetView().NotifyGoldShop(bShow)
        elif iType == REDPOINT_SCHEDULE:
            self.GetView().NotifySchedule(bShow)
        elif iType == REDPOINT_CONSIGNMALL:
            self.GetView().NotifyConsignmall(bShow)
        

    
    def OnBtnClick(self, iMsgID):
        import mgrschedule
        import mdnewschedule
        import permission
        if iMsgID == MAPINFO_MSG_PRESENT:
            self.OnPresentCenterClick()
        
        if iMsgID == MAPINFO_MSG_SCHEDULE:
            if permission.IsNewSchedule():
                if not GetModel().GetBtnIsShowRedPoint(REDPOINT_SCHEDULE):
                    pass
                self.GetView().NotifySchedule(mdnewschedule.GetNewScheduleModel().CheckHasReward())
            elif not GetModel().GetBtnIsShowRedPoint(REDPOINT_SCHEDULE):
                pass
            self.GetView().NotifySchedule(mgrschedule.GetMgr().CheckHasReward())
        
        if iMsgID == MAPINFO_MSG_GOLDSHOP:
            import model_mapinfobar
            oModel = model_mapinfobar.GetModel()
            oMgr = md2019double12shop.GetModel()
            if not oMgr.GetRedPoint():
                oModel.SetGoldShopRedPoint(False)
            
        

    
    def OnWarStart(self):
        self.GetView().CheckPersentCenterTips()
        self.GetView().SetShowPersentCenterTips(False)

    
    def OnWarEnd(self):
        self.GetView().SetShowPersentCenterTips(True)



class CBtnFuncDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xab\xf6\xb6s\xc2I\xc0\xbb\xaa\xba\xa5\\\xaf\xe0
\t'''
    MSG2FUNC = {
        MAPINFO_MSG_MINIMAP: 'SwitchMinimapByBtn',
        MAPINFO_MSG_QUERY: 'SwitchQuery',
        MAPINFO_MSG_QUESTION: 'SwitchQuestion',
        MAPINFO_MSG_GOLDSHOP: 'SwitchGold',
        MAPINFO_MSG_SCHEDULE: 'SwitchSchedule',
        MAPINFO_MSG_RANK: 'SwitchRank',
        MAPINFO_MSG_PRESENT: 'SwitchPersion',
        MAPINFO_MSG_TJSHOP: 'SwitchTJShop',
        MAPINFO_MSG_CONSIGNMALL: 'SwitchConsignmall' }
    
    def Init(self):
        self.GetView().ssConnect(self.GetView().SS_BtnClick, self.OnBtnClick)

    
    def OnBtnClick(self, iMsgID):
        sFuncName = self.MSG2FUNC.get(iMsgID, None)
        if sFuncName:
            getattr(self, sFuncName)()
        

    
    def SwitchMinimapByBtn(self):
        import dlgmap
        import clickcounter
        dlgmap.SwitchMinimap()
        clickcounter.Log('\xb7\xed\xabe\xa6a\xb9\xcf')

    
    def SwitchQuery(self):
        import nethero
        import clickcounter
        nethero.C2SOpenLycos()
        clickcounter.Log('\xb9\xda\xb7Q\xba\xeb\xc6F')

    
    def SwitchQuestion(self):
        import dlgnewbiequestion
        dlgnewbiequestion.ShowQuesionDlg()

    
    def SwitchGold(self):
        import usermacro
        import dlgshenmoisland
        import dlghuashanduel
        if misc.IsNationFightServer():
            usermacro.PROMPT_MSG('\xa5\xbb\xaaA\xb0\xc8\xbe\xb9\xb8T\xa4\xee\xa6\xb9\xbe\xde\xa7@')
            return None
        
        if dlgshenmoisland.IsShenmoHuodong():
            usermacro.PROMPT_MSG('\xbd\xd0\xaa\xf0\xa6^\xad\xec\xaaA\xa6A\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        if dlghuashanduel.IsInGame():
            usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xa5\xbb\xaaA\xa6A\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        import dlggoldshop
        dlggoldshop.OnSwitchShop()
        clickcounter.Log('\xb0\xd3\xab\xb0')

    
    def SwitchSchedule(self):
        import dlgschedule
        import dlgnewschedule
        import clickcounter
        import usermacro
        import dlgshenmoisland
        import dlghuashanduel
        import permission
        if misc.IsNationFightServer():
            usermacro.PROMPT_MSG('\xa5\xbb\xaaA\xb0\xc8\xbe\xb9\xb8T\xa4\xee\xa6\xb9\xbe\xde\xa7@')
            return None
        
        if dlgshenmoisland.IsShenmoHuodong():
            usermacro.PROMPT_MSG('\xbd\xd0\xaa\xf0\xa6^\xad\xec\xaaA\xa6A\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        if dlghuashanduel.IsInGame():
            usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xa5\xbb\xaaA\xa6A\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        self.GetView().m_CalendarTipsBox = None
        self.GetView().ShowCalendarGuideTips(False)
        if permission.IsNewSchedule():
            dlgnewschedule.ShowSwitch()
        else:
            dlgschedule.SwitchSchedule()
        clickcounter.Log('\xa4\xe9\xbe\xe4')

    
    def SwitchRank(self):
        import dlgrank
        import clickcounter
        import usermacro
        import dlgshenmoisland
        if misc.IsNationFightServer():
            usermacro.PROMPT_MSG('\xa5\xbb\xaaA\xb0\xc8\xbe\xb9\xb8T\xa4\xee\xa6\xb9\xbe\xde\xa7@')
            return None
        
        if dlgshenmoisland.IsShenmoHuodong():
            usermacro.PROMPT_MSG('\xbd\xd0\xaa\xf0\xa6^\xad\xec\xaaA\xa6A\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        if dlgrank.CheckShowRankDlg():
            clickcounter.Log('\xb1\xc6\xa6\xe6\xba]')
        

    
    def SwitchPersion(self):
        import nethdpresentcenter
        import dlgpresentcenter
        import presentcenterdefines
        import hero
        import sound
        import sounddefine
        import usermacro
        sound.Play(sounddefine.PATH_PRESENTCENTER)
        if misc.IsNationFightServer():
            usermacro.PROMPT_MSG('\xa5\xbb\xaaA\xb0\xc8\xbe\xb9\xb8T\xa4\xee\xa6\xb9\xbe\xde\xa7@')
            return None
        
        if dlgpresentcenter.IsOpen():
            dlgpresentcenter.Close()
        elif hero.IsLevelChange() and GetModel().GetIsShowLevel10Tip():
            GetModel().SetIsShowLevel10Tip(False)
            dlgpresentcenter.Open(presentcenterdefines.PAGE_FIRST_CHARGE)
        else:
            dlgpresentcenter.Open()
            nethdpresentcenter.C2SOpenSevenDayDlg()
        import clickcounter
        clickcounter.Log('\xba\xd6\xa7Q\xa4\xa4\xa4\xdf')

    
    def SwitchTJShop(self):
        import dlgtjtradecenter
        dlgtjtradecenter.IntelligentShowSwitch()
        clickcounter.Log('\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf')

    
    def SwitchConsignmall(self):
        import dlgconsignmall
        import sound
        import dlgshenmoisland
        import usermacro
        if dlgshenmoisland.IsShenmoHuodong():
            usermacro.PROMPT_MSG('\xbd\xd0\xaa\xf0\xa6^\xad\xec\xaaA\xa6A\xb6i\xa6\xe6\xbe\xde\xa7@')
            return None
        
        if dlgconsignmall.IsOpen():
            sound.PlaySound(sound.SND_CLOSEDLG)
        else:
            sound.PlaySound(sound.SND_SHOWDLG)
        dlgconsignmall.ShowSwitch()
        clickcounter.Log('\xb1H\xb0\xe2\xa4\xa4\xa4\xdf')



class CCalendarTipsDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xa4\xe9\xbe\xfa\xaa\xba\xb4\xa3\xbf\xf4
\t'''
    
    def Init(self):
        self.GetView().ssConnect(self.GetView().SS_BtnClick, self.OnBtnClick)
        GetModel().ssConnect(GetModel().SS_CalendarTipsChange, self.OnCalendarTips)
        GetModel().ssConnect(GetModel().SS_ShowCalendarGuideTips, self.OnShowGuideTips)

    
    def OnCalendarTips(self, sTipTxt):
        self.GetView().ShowCalendarTipsBox(True, sTipTxt)

    
    def OnBtnClick(self, iMsgID):
        import guidectrl
        import guidedefine
        if iMsgID == MAPINFO_MSG_SCHEDULE:
            self.GetView().ShowCalendarTipsBox(False)
            guidectrl.GetGuideCtrl().ClickOrdObj(guidedefine.GUIDE_MAP_INFO_BAR, 'm_Calendar')
        

    
    def OnShowGuideTips(self):
        self.GetView().ShowCalendarGuideTips(True)



class CMinimapTipsDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.GetView().ssConnect(self.GetView().SS_TipsClick, self.OnTipsClick)

    
    def OnTipsClick(self):
        import copylinkobj
        import key
        import C_sys
        import minimapnpcpos
        import clickcounter
        import dlgmap
        oModel = GetModel()
        iSceneID = oModel.GetSceneID()
        if iSceneID is None:
            return None
        
        if C_sys.IsKeyDown(key.VK_SHIFT):
            if minimapnpcpos.IsMiniMap(iSceneID):
                (x, y) = oModel.GetHeroPos()
                copylinkobj.CreateCopyLink(72, iSceneID, oModel.GetMapName(), x, y)
            
        else:
            dlgmap.SwitchMinimap()
            clickcounter.Log('\xa4p\xa6a\xb9\xcf')



class CSwitchBtnListDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xc2X\xaei\xab\xf6\xb6s\xaa\xba\xa5\\\xaf\xe0
\t'''
    
    def GetView(self):
        ''':rtype: commapinfobar.CMapInfoBarPanel'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        self.GetView().ssConnect(self.GetView().SS_ClickSwitchBtn, self.OnSwitchBtn)
        oModel = GetModel()
        oModel.ssConnect(oModel.SS_BarSwitch, self.OnSwitch)
        oModel.ssConnect(oModel.SS_BarHide, self.OnHideListChange)
        hero.AddRefreshCallback('CSwitchBtnListDelegate', ('m_Grade',), self.OnGradeUpdate)
        import commoncb
        commoncb.RegistCB(commoncb.WAR_START, self, 'OnWarStart')
        commoncb.RegistCB(commoncb.WAR_END, self, 'OnWarEnd')
        self.OnSwitch()

    
    def OnSwitchBtn(self):
        GetModel().SetSwitch(not GetModel().GetSwitch())

    
    def OnGradeUpdate(self):
        lHide = []
        lUnlock = []
        oModel = GetModel()
        iGrade = hero.GetProp('m_Grade', 0)
        lCurHide = oModel.GetHideList()
        for iPartID, iKey in MAPINFO_DATA_KEY.iteritems():
            dInfo = mainmenuctrldata.GetCtrlData(iPartID, iKey)
            if dInfo and dInfo['iUnlockLv'] > iGrade:
                lHide.append(iBtnType)
                continue
            if iBtnType in lCurHide:
                lUnlock.append((iBtnType, dInfo['iGuideID']))
                continue
        
        for _, iGuideID in lUnlock:
            if iGuideID:
                mdguide.GetCGuideMgr().SetGuideID(iGuideID)
                break
                continue
        
        oModel.SetHideList(lHide)

    
    def OnHideListChange(self):
        self.GetView().SetBtnHide(GetModel().GetSwitch(), GetModel().GetHideList())

    
    def OnSwitch(self):
        self.GetView().SwitchShow(GetModel().GetSwitch(), GetModel().GetHideList())

    
    def OnWarStart(self):
        import towerdefence
        oModel = GetModel()
        if towerdefence.IsTowerFight():
            bSwitch = oModel.GetSwitch()
            if bSwitch:
                oModel.SetWarSwitch(bSwitch)
                self.OnSwitchBtn()
            
        else:
            oModel.SetWarSwitch(False)

    
    def OnWarEnd(self):
        import towerdefence
        oModel = GetModel()
        if towerdefence.IsTowerFight():
            bSwitch = oModel.GetSwitch()
            if not bSwitch and oModel.GetWarSwitch():
                self.OnSwitchBtn()
            
        
        oModel.SetWarSwitch(False)



class CAroundFlashDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xbc\xfa\xc0y\xa4\xa4\xa4\xdf\xb0{\xc3{
\t'''
    
    def Init(self):
        self.GetView().ssConnect(self.GetView().SS_BtnClick, self.OnBtnClick)
        GetModel().ssConnect(GetModel().SS_PresentFlash, self.OnAroundFlash)
        commoncb.RegistCB(commoncb.FLY_GET, self, 'OnFlyGetNotice')

    
    def OnBtnClick(self, iMsgID):
        if iMsgID == MAPINFO_MSG_PRESENT:
            self.GetView().SetAroundFlash(False)
        

    
    def OnAroundFlash(self, bFlash):
        self.GetView().SetAroundFlash(bFlash)

    
    def OnFlyGetNotice(self, iStep):
        if iStep == 1:
            self.GetView().SetCrossFlash(True)
        elif iStep == 2:
            if self.GetView().GetCrossFlash():
                self.GetView().SetCrossFlash(False)
            
        



class CShareBtnDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xa4\xc0\xa8\xc9\xab\xf6\xb6s\xc5\xe3\xa5\xdc
\t'''
    
    def Init(self):
        import hero
        hero.AddRefreshCallback('CShareBtnDelegate', (('m_Grade',),), self.OnGradeChange)

    
    def OnGradeChange(self):
        import delayloading
        import frametaskmgr
        import hero
        if hero.IsShenHe():
            return None
        
        if misc.IsTWServer():
            return None
        
        iGrade = hero.GetProp('m_Grade')
        if iGrade and iGrade >= 30:
            if not delayloading.IsShowLoading():
                self.GetView().ShowShareBtn()
            else:
                frametaskmgr.GetFrameTaskMgr().AddAfterLoadingTask(1, self.GetView().ShowShareBtn)
        



class CNotifyAreaDelegate(delegatebase.CDelegateBase):
    '''
\t\xb1\xb1\xa8\xee\xb4\xa3\xbf\xf4\xb0\xcf\xb0\xec
\t'''
    
    def Init(self):
        oView = self.GetView()
        commoncb.RegistCB(commoncb.TEAM_INVITE_NOTIFY, self, 'OnTeamNotify')

    
    def OnTeamNotify(self, bNotify):
        import mainmenudefines
        if bNotify:
            self.GetView().AddNotifyAni('teaminvite', mainmenudefines.NOTIFY_TEAM, misc.Functor(self.OnClickNotify))
        else:
            self.GetView().DelNotifyAni('teaminvite')

    
    def OnClickNotify(self):
        import juben
        if juben.IsPlayJuben():
            return None
        
        import nethero
        nethero.C2SGetPlayerNotify()
        self.OnTeamNotify(False)



def GetModel():
    import model_mapinfobar
    return model_mapinfobar.GetModel()
