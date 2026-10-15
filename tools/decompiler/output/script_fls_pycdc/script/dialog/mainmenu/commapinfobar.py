# pycdc 交叉复核产物 · script.fls entry 4409
# co_filename(原始)='script/dialog/mainmenu/commapinfobar.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4409.pyc (Python 2.5)

import guidectrl
import guidedefine
import mainmenudefines
import misc
import permission
import ratio
import slot
import interface
import style
import ui
import wrapinterface
import combdialog
import comactivityiconcenter
import hero
import mdreddot
import dlgreddot
MAP_NAME_CUT_LEN = 7

def BuildComponent(oParent):
    return CMapInfoBarPanel(oParent)


def GetMapNameCutLen():
    if permission.IsOpenNewMainmenu():
        return 4
    
    return MAP_NAME_CUT_LEN


class CMapInfoBarPanel(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_BtnClick = 'OnBtnClick(iBtnType)'
    SS_TipsClick = 'OnTipsClick()'
    SS_ClickSwitchBtn = 'OnSwitchBtn()'
    SS_ClickNotify = 'OnNotifyClick(iNotifyType)'
    BTNCONFIG = {
        mainmenudefines.MAPINFO_MSG_MINIMAP: ('mainmenu/mapbtn.igs', '\xb7\xed\xabe\xa6a\xb9\xcf(TAB)'),
        mainmenudefines.MAPINFO_MSG_GOLDSHOP: ('mainmenu/goldingot.igs', '\xb0\xd3\xab\xb0'),
        mainmenudefines.MAPINFO_MSG_SCHEDULE: ('mainmenu/calendar.igs', '\xa4\xe9\xbe\xe4'),
        mainmenudefines.MAPINFO_MSG_RANK: ('mainmenu/rankbtn.igs', '\xb1\xc6\xa6\xe6\xba]'),
        mainmenudefines.MAPINFO_MSG_PRESENT: ('mainmenu/rewardcenter.igs', '\xba\xd6\xa7Q\xa4\xa4\xa4\xdf'),
        mainmenudefines.MAPINFO_MSG_TJSHOP: ('mainmenu/mxbbtn.igs', '\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf'),
        mainmenudefines.MAPINFO_MSG_CONSIGNMALL: ('mainmenu/consignmall.igs', '\xb1H\xb0\xe2\xa4\xa4\xa4\xdf') }
    BTNORDER = [
        mainmenudefines.MAPINFO_MSG_MINIMAP,
        mainmenudefines.MAPINFO_MSG_RANK,
        mainmenudefines.MAPINFO_MSG_GOLDSHOP,
        mainmenudefines.MAPINFO_MSG_TJSHOP,
        mainmenudefines.MAPINFO_MSG_CONSIGNMALL,
        mainmenudefines.MAPINFO_MSG_SCHEDULE,
        mainmenudefines.MAPINFO_MSG_PRESENT]
    BTNORDER_NEW = [
        mainmenudefines.MAPINFO_MSG_SCHEDULE,
        mainmenudefines.MAPINFO_MSG_MINIMAP,
        mainmenudefines.MAPINFO_MSG_RANK,
        mainmenudefines.MAPINFO_MSG_GOLDSHOP,
        mainmenudefines.MAPINFO_MSG_TJSHOP,
        mainmenudefines.MAPINFO_MSG_CONSIGNMALL,
        mainmenudefines.MAPINFO_MSG_PRESENT]
    
    def __init__(self, oParent):
        if permission.IsOpenNewMainmenu():
            sUIName = 'dialog/mainmenu/com_mapinfobar_new.dlg'
        else:
            sUIName = 'dialog/mainmenu/com_mapinfobar.dlg'
        combdialog.CCombSubWnd.__init__(self, oParent, sUIName)
        self.SetIgnoreEsc(True)
        self.m_MapName = ''
        self.m_SceneID = ''
        self.m_NameLst = []
        self.m_ShowNameIdx = 0
        self.m_DelayTimer = None
        self.m_dBtnDict = { }
        self.m_ScaleBtn = None
        self.m_GoldIngot = None
        self.m_PresentCenter = None
        self.m_Calendar = None
        self.m_ConsignmallBtn = None
        self.m_ActivityIconCenter = None
        self.m_NotifyRedTips = None
        self.m_NotifyMsgTips = None
        self.m_ScheduleRedPoint = None
        self.m_RollAni = None
        self.m_FlashAni = None
        self.m_ShopRedTips = None
        self.m_CalendarTipsBox = None
        self.m_NotifyBoxs = []
        self.m_MiniMapTips = None
        self.m_NotifyBtns = []
        self.m_CalendarGuideTipsID = None
        self.m_oNewBieTaskBnt = None
        self.ssInit()
        self.UpdateSize()
        self.CreateStyle1BG()
        self.CreateNotifyBox()
        self.CreateBtn()
        self.CreateActivityIcon()
        self.InitRedDot()
        self.InitDelegate()

    
    def SetMapInfo(self, iSceneID, sMapName, x, y):
        LOG_WARN('\xc2\xc2\xb1\xb5\xa4f\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I\xa1I\xa1ISetMapInfo')

    
    def LeftUp(self):
        pass

    
    def LeftDown(self):
        pass

    
    def GetBtnOrder(self):
        if permission.IsOpenNewMainmenu():
            return self.BTNORDER_NEW
        
        return self.BTNORDER

    
    def GetRedDotRes(self):
        if permission.IsOpenNewMainmenu():
            return ('number/0.igs', 'misc')
        
        return ('combdialog/\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe\xd0\xa1\xba\xec\xb5\xe3.igs', interface.UIPath)

    
    def SetPosTxt(self, x, y):
        for sName in [
            'txt_posx1',
            'txt_posx2',
            'txt_posx3']:
            oTxt = self.GetObject(sName)
            if oTxt:
                pass
            oTxt.SetText(str(x))
        
        for sName in [
            'txt_posy1',
            'txt_posy2',
            'txt_posy3']:
            oTxt = self.GetObject(sName)
            if oTxt:
                pass
            oTxt.SetText(str(y))
        

    
    def UpdateMapName(self, sMapName):
        self.m_MapName = sMapName
        sMapName = self.GetShowMapName()
        self.SetMapNameTxt(sMapName)

    
    def UpdateSceneImg(self, bShowIn):
        oImg = self.GetObject('img_in')
        if not oImg and permission.IsOpenNewMainmenu():
            pass
        oImg.SetShow(bShowIn)
        oImg = self.GetObject('img_out')
        if not oImg and permission.IsOpenNewMainmenu():
            pass
        oImg.SetShow(not bShowIn)

    
    def UpdatePosition(self, x, y):
        import dlgmap
        dlgmap.SetHeroPos(x, y)
        self.SetPosTxt(x, y)

    
    def NotifyPersentCenterRedDot(self, bNotify = True):
        if not self.m_PresentCenter:
            return None
        
        if bNotify:
            self.m_NotifyRedTips = ui.CImage(self.m_PresentCenter, *self.GetRedDotRes())
            if permission.IsOpenNewMainmenu():
                (iSizeW, iSizeY) = (0, 0)
            else:
                (iSizeW, iSizeY) = self.m_NotifyRedTips.GetSize()
            interface.TopRight(self.m_NotifyRedTips, -iSizeW / 2, iSizeY / 2)
        else:
            self.m_NotifyRedTips = None

    
    def NotifyPersentCenterTips(self, bNotify = True):
        if not self.m_PresentCenter:
            return None
        
        import dlgguidetips
        import activityicondefine
        if bNotify:
            oItem = self.m_ActivityIconCenter.GetItemByID(activityicondefine.FIRST_CHARGE_BTN)
            if oItem and oItem.IsTipsShow():
                return None
            
            sText = '\xb1z\xa6\xb3\xbc\xfa\xc0y\xa5i\xa5H\xbb\xe2\xa8\xfa'
            if not self.m_NotifyMsgTips:
                (w, h) = self.m_PresentCenter.GetSize()
                self.m_NotifyMsgTips = dlgguidetips.CGuideTips(self.m_PresentCenter, sText, 1, 0, -20, w, h)
            
        else:
            self.m_NotifyMsgTips = None

    
    def GetActivityIconH(self):
        return self.m_ActivityIconCenter.GetActivityIconH()

    
    def CheckPersentCenterTips(self):
        if self.m_NotifyMsgTips and not self.m_NotifyMsgTips.GetShow():
            self.m_NotifyMsgTips = None
        

    
    def SetShowPersentCenterTips(self, bShow):
        if self.m_NotifyMsgTips:
            self.m_NotifyMsgTips.SetShow(bShow)
        

    
    def NotifySchedule(self, bNotify = True):
        if not self.m_Calendar:
            return None
        
        if bNotify:
            self.m_ScheduleRedPoint = ui.CImage(self.m_Calendar, *self.GetRedDotRes())
            if permission.IsOpenNewMainmenu():
                (iSizeW, iSizeY) = (0, 0)
            else:
                (iSizeW, iSizeY) = self.m_ScheduleRedPoint.GetSize()
            interface.TopRight(self.m_ScheduleRedPoint, -iSizeW / 2, iSizeY / 2)
        else:
            self.m_ScheduleRedPoint = None

    
    def SetAroundFlash(self, bFlash):
        if not self.m_PresentCenter:
            return None
        
        if bFlash:
            if permission.IsOpenNewMainmenu():
                self.m_RollAni = ui.CImage(self.m_PresentCenter, 'common/hint2.igs', interface.UIPath)
                self.m_RollAni.CreateCommand(1, 'animation')
                self.m_RollAni.SetPos(20, 20)
                self.m_RollAni.SetZ(300)
            else:
                self.m_RollAni = interface.CStretchSpriteObject(self.m_PresentCenter, 'item44/select.spr', 'item')
                self.m_RollAni.CreateCommand(1, 'animation')
                self.m_RollAni.SetPos(11, 10)
                self.m_RollAni.SetZ(300)
                self.m_RollAni.SetScale(0.5)
        else:
            self.m_RollAni = None

    
    def SetCrossFlash(self, bFlash):
        if not self.m_PresentCenter:
            return None
        
        if bFlash:
            import style
            hint_path = style.GetPath('common/hint.igs')
            self.m_FlashAni = ui.CImage(self, hint_path, interface.UIPath)
            self.m_FlashAni.CreateCommand(2, 'animation')
            (x, y) = self.m_PresentCenter.GetPos()
            if permission.IsOpenNewMainmenu():
                self.m_FlashAni.SetPos(x + 20, y + 20)
            else:
                self.m_FlashAni.SetPos(x + 11, y + 10)
            self.m_FlashAni.SetZ(10)
        else:
            import commoncb
            commoncb.TriggerCB(commoncb.FLY_GET, 3)
            self.m_FlashAni = None

    
    def GetCrossFlash(self):
        return self.m_FlashAni

    
    def NotifyGoldShop(self, bNotify = True):
        if not self.m_GoldIngot:
            return None
        
        if bNotify:
            self.m_ShopRedTips = ui.CImage(self.m_GoldIngot, *self.GetRedDotRes())
            if permission.IsOpenNewMainmenu():
                (iSizeW, iSizeY) = (0, 0)
            else:
                (iSizeW, iSizeY) = self.m_ShopRedTips.GetSize()
            interface.TopRight(self.m_ShopRedTips, -iSizeW / 2, iSizeY / 2)
        else:
            self.m_ShopRedTips = None

    
    def NotifyConsignmall(self, bNotify = True):
        if not self.m_ConsignmallBtn:
            return None
        
        if bNotify:
            self.m_ConsignmallTips = ui.CImage(self.m_ConsignmallBtn, *self.GetRedDotRes())
            if permission.IsOpenNewMainmenu():
                (iSizeW, iSizeY) = (0, 0)
            else:
                (iSizeW, iSizeY) = self.m_ConsignmallTips.GetSize()
            interface.TopRight(self.m_ConsignmallTips, -iSizeW / 2, iSizeY / 2)
        else:
            self.m_ConsignmallTips = None

    
    def ShowCalendarTipsBox(self, bShow, tipsTxt = ''):
        if bShow and tipsTxt:
            self.m_Calendar.FlashItself(5)
            (iW, iH) = self.m_Calendar.GetSize()
            self.m_CalendarTipsBox = wrapinterface.CCombTipsBox(self.m_Calendar, tipsTxt, 4, iW - 3, iH - 10, 140, 50, 30)
        else:
            self.m_CalendarTipsBox = None

    
    def ShowCalendarGuideTips(self, bShow):
        if not self.m_Calendar:
            return None
        
        import dlgguidetips
        if bShow:
            if self.m_CalendarGuideTipsID:
                dlgguidetips.RemoveTips(self.m_CalendarGuideTipsID)
            
            (w, h) = self.m_Calendar.GetSize()
            (self.m_CalendarGuideTipsID, _) = dlgguidetips.CreateTips(dlgguidetips.TYPE_OUT_WAR, self.m_Calendar, '\xacd\xac\xdd\xa7\xf3\xa6h\xaa\xb1\xaak\xa1I', 1, 0, -20, w, h)
        elif self.m_CalendarGuideTipsID:
            dlgguidetips.RemoveTips(self.m_CalendarGuideTipsID)
        

    
    def SwitchShow(self, bSwitchShow, lCurHideBtn):
        import style
        iStyle = interface.GetStyle() + 1
        if iStyle == 1 and not permission.IsOpenNewMainmenu():
            self.m_oBtnBG.SwitchShow(bSwitchShow)
            self.m_oBtnBG.SetBtnNum(len(self.GetBtnOrder()) - len(lCurHideBtn))
            if bSwitchShow:
                self.LayoutStyle1Btn(lCurHideBtn)
            else:
                self.m_ScaleBtn.SetPos(16, 25)
        elif bSwitchShow:
            sPath = 'mainmenu/scalebtn.igs'
        else:
            sPath = 'mainmenu2/icon_open.igs'
        (x, y) = self.m_ScaleBtn.GetPos()
        self.m_ScaleBtn = interface.CButton(self, style.GetPath(sPath), x, y, 6)
        for iBtnType in self.GetBtnOrder():
            if iBtnType not in lCurHideBtn:
                oBtn = self.GetBtnByType(iBtnType)
                if oBtn:
                    oBtn.SetShow(bSwitchShow)
                
            oBtn
        
        import dlgmap
        dlgmap.SetNotifyBtnShow()

    
    def CreateStyle1BG(self):
        if interface.IsStyle1():
            oBg = self.GetObject('img_bg').GetImage(0, 0)
            self.m_oBtnBG = CStyle1BtnBG(self, oBg)
            self.m_oBtnBG.SetZ(self.GetObject('img_bg').GetZ())
            self.m_oBtnBG.SetPos(*self.GetObject('img_bg').GetPos())
        else:
            self.m_oBtnBG = None

    
    def SetBtnHide(self, bSwitchShow, lHideBtn):
        for iBtnType in self.GetBtnOrder():
            if iBtnType in lHideBtn:
                if self.GetBtnByType(iBtnType):
                    pass
                self.GetBtnByType(iBtnType).SetShow(False)
                continue
            if bSwitchShow:
                if self.GetBtnByType(iBtnType):
                    pass
                self.GetBtnByType(iBtnType).SetShow(True)
                continue
        
        self.LayoutBtn(lHideBtn)
        if interface.IsStyle1():
            self.m_oBtnBG.SetBtnNum(len(self.GetBtnOrder()) - len(lHideBtn))
        

    
    def ShowShareBtn(self):
        obj = self.GetObject('loc_share')
        if obj:
            import dlgsnapshotshare
            btn = dlgsnapshotshare.CreateCSnapshotShareBtn(self)
            (x, y) = obj.GetPos()
            btn.SetPos(x, y)
        

    
    def AddActivityIcon(self, oActivityIconData, oClass):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.AddItem(oActivityIconData, oClass)
            import world
            world.ShowHotKeyTips()
        

    
    def DelActivityIcon(self, iActiviyID):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.DelItem(iActiviyID)
        

    
    def UpdateActivityIcon(self, oActivityIconData):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.UpdateItem(oActivityIconData)
        

    
    def ResetActivityIcons(self):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.ResetItems()
        

    
    def ShowIconFlash(self, iActiviyID):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.ShowItemFlash(iActiviyID)
        

    
    def ShowIconAni(self, iActivityID, bOpen):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.ShowItemAni(iActivityID, bOpen)
        

    
    def SetShowActivityIcon(self, bShow):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.SetCenterShow(bShow)
        

    
    def SetDouble12RedPoint(self, bShow):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.SetDouble12RedPoint(bShow)
        

    
    def Set2020ReturnRedPoint(self, iRedPoint):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.Set2020ReturnRedPoint(iRedPoint)
        

    
    def SetRookieBackRedPoint(self, iRedPoint):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.SetRookieBackRedPoint(iRedPoint)
        

    
    def SetSevenAimRedPoint(self, bShow):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.SetSevenAimRedPoint(bShow)
        

    
    def SetActMainRedPoint(self, iActiviyID, bShow):
        if self.m_ActivityIconCenter:
            self.m_ActivityIconCenter.SetActMainIconRedPoint(iActiviyID, bShow)
        

    
    def AddNotifyAni(self, sKey, sPathKey, oLeftUpCB):
        self.DelNotifyItem(sKey)
        oNotifyBtn = CNotifyBtn(interface.MainPanel, mainmenudefines.NOTIFY_RES_MAP[sPathKey], interface.UIPath, oLeftUpCB)
        oNotifyBtn.Topmost()
        oNotifyBtn.CreateCommand(1, 'animation')
        self.AddNotifyItem(sKey, oNotifyBtn)

    
    def DelNotifyAni(self, sKey):
        self.DelNotifyItem(sKey)

    
    def ShowSiblingOpenDlgNotify(self, bShow):
        if bShow:
            oLeftUpCB = misc.Functor(self.OnNotifyMsg, mainmenudefines.NOTIFY_SIBLING_OPEN_DLG)
            oSiblingOpenDlgNotify = CNotifyBtn(interface.MainPanel, 'mainmenu/mail.spr', interface.UIPath, oLeftUpCB)
            oSiblingOpenDlgNotify.Topmost()
            oSiblingOpenDlgNotify.CreateCommand(1, 'animation')
            self.AddNotifyItem(mainmenudefines.NOTIFY_SIBLING_OPEN_DLG, oSiblingOpenDlgNotify)
        else:
            self.DelNotifyItem(mainmenudefines.NOTIFY_SIBLING_OPEN_DLG)

    
    def GetNewBieTaskBntCtrl(self):
        import dlgnewguide
        if not self.m_oNewBieTaskBnt:
            self.m_oNewBieTaskBnt = dlgnewguide.CShortCutBtnCtrl(self.GetObject('loc_XiaoXin'))
        
        return self.m_oNewBieTaskBnt

    
    def InitDelegate(self):
        import delegatemapinfobar
        import dgtsiblingbtn
        import dgtsiblinginvite
        import delegateactivityicon
        import dgtgroupcombine
        self.m_Delegates = [
            delegatemapinfobar.CMapNameDelegate(self),
            delegatemapinfobar.CMapInAndOutDelegate(self),
            delegatemapinfobar.CPosTxtDelegate(self),
            delegatemapinfobar.CRedPointDelegate(self),
            delegatemapinfobar.CBtnFuncDelegate(self),
            delegatemapinfobar.CCalendarTipsDelegate(self),
            delegatemapinfobar.CMinimapTipsDelegate(self),
            delegatemapinfobar.CSwitchBtnListDelegate(self),
            delegatemapinfobar.CAroundFlashDelegate(self),
            delegatemapinfobar.CShareBtnDelegate(self),
            delegatemapinfobar.CNotifyAreaDelegate(self),
            dgtsiblingbtn.CSiblingOpenDlgTipsDelegate(self),
            dgtsiblingbtn.CSiblingTipsDelegate(self),
            dgtsiblinginvite.CInviteBtnDelegate(self),
            delegateactivityicon.CDgtActivityIcon(self),
            dgtgroupcombine.CMainTipsDelegate(self)]

    
    def GetBtnByType(self, iBtnType):
        return self.m_dBtnDict.get(iBtnType, None)

    
    def GetResPath(self, sPath):
        if permission.IsOpenNewMainmenu():
            sPath += '_new'
            return style.GetPath(sPath)
        elif ratio.Is1024x768():
            return style.GetPath(sPath + '_big')
        
        return style.GetPath(sPath)

    
    def GetScaleBtnPosX(self):
        if ratio.Is1024x768():
            sPosName = 'offx_ScaleBtn_big'
        else:
            sPosName = 'offx_ScaleBtn'
        return style.GetInt('commapinfobar.CMapInfoBarPanel', sPosName)

    
    def InitRedDot(self):
        oRedMgr = mdreddot.GetMgr()
        oNode = oRedMgr.GetNode('\xb0\xd3\xab\xb0\xa1A\xa8C\xb6g\xc2\xa7\xa5]\xa1A\xadq\xbe\\')
        self.m_oGoldRedDot = dlgreddot.CSimpleRedDotWidget(self.m_GoldIngot, oNode, iOffsetX = -4, iOffsetY = 4)

    
    def CreateActivityIcon(self):
        oLoc = self.GetObject('loc_ActivityIconCenter')
        if oLoc:
            (iX, iY, _, _) = self.GetLocData('loc_ActivityIconCenter')
            self.m_ActivityIconCenter = comactivityiconcenter.CComActivityCenter(self)
            self.m_ActivityIconCenter.SetPos(iX, iY)
        

    
    def CreateBtn(self):
        '''
\t\t\xbac\xab\xd8\xa5\xaa\xa4W\xa8\xa4\xb0\xbc\xc3\xe4\xa5\\\xaf\xe0\xab\xf6\xb6s
\t\t'''
        for iBtnType in self.GetBtnOrder():
            (sFilePath, sMsg) = self.BTNCONFIG[iBtnType]
            if permission.IsOpenNewMainmenu() and iBtnType == mainmenudefines.MAPINFO_MSG_MINIMAP:
                continue
            
            self.m_dBtnDict[iBtnType] = wrapinterface.CButtonWithTips(self, self.GetResPath(sFilePath), 0, 0, self.ProcessBtnTips(sMsg), iBtnType)
            self.m_dBtnDict[iBtnType].SetPlaySound(False)
        
        self.m_ScaleBtn = interface.CButton(self, style.GetPath('mainmenu/scalebtn.igs'), 0, 0, 6)
        self.m_GoldIngot = self.m_dBtnDict[mainmenudefines.MAPINFO_MSG_GOLDSHOP]
        self.m_PresentCenter = self.m_dBtnDict[mainmenudefines.MAPINFO_MSG_PRESENT]
        self.m_Calendar = self.m_dBtnDict[mainmenudefines.MAPINFO_MSG_SCHEDULE]
        self.m_ConsignmallBtn = self.m_dBtnDict[mainmenudefines.MAPINFO_MSG_CONSIGNMALL]
        self.m_MapBtn = self.m_dBtnDict.get(mainmenudefines.MAPINFO_MSG_MINIMAP, None)
        self.LayoutBtn()
        self.InitGuide()

    
    def InitGuide(self):
        oGuideCtrl = guidectrl.GetGuideCtrl()
        oGuideCtrl.AddWefOrdObj(self, guidedefine.GUIDE_MAP_INFO_BAR, 'm_Calendar', self.m_Calendar)
        for iBtnType in self.GetBtnOrder():
            oBtn = self.m_dBtnDict.get(iBtnType, None)
            if oBtn:
                oGuideCtrl.AddWefOrdObj(self.GetParent(), guidedefine.GUIDE_MAP_INFO_BAR, 'BTN%s' % iBtnType, self.m_dBtnDict[iBtnType])
                continue
        
        for sBtn in ('loc_guide',):
            oBtn = self.GetObject(sBtn)
            if oBtn:
                oGuideCtrl.AddWefOrdObj(self.GetParent(), guidedefine.GUIDE_MAP_INFO_BAR, sBtn, oBtn)
                continue
        

    
    def LayoutBtn(self, lHideBtn = ()):
        iStyle = interface.GetStyle() + 1
        if permission.IsOpenNewMainmenu():
            self.LayoutNewBtn(lHideBtn)
        elif iStyle == 1:
            self.LayoutStyle1Btn(lHideBtn)
        elif iStyle == 2:
            self.LayoutStyle2Btn(lHideBtn)
        elif iStyle == 3:
            self.LayoutStyle3Btn(lHideBtn)
        else:
            self.LayoutStyle4Btn(lHideBtn)

    
    def GetShowBtnList(self, lHideBtn):
        oSortList = []
        for iBtnType in self.GetBtnOrder():
            oBtn = self.GetBtnByType(iBtnType)
            if oBtn and iBtnType not in lHideBtn:
                oSortList.append(oBtn)
                continue
        
        return oSortList

    
    def LayoutStyle1Btn(self, lHideBtn = ()):
        oSortList = self.GetShowBtnList(lHideBtn)
        oSortList.append(self.m_ScaleBtn)
        (x, y) = (9, 28)
        iSize = len(oSortList)
        for iIdx, oBtn in enumerate(oSortList):
            oBtn.SetPos(x, y)
            (_, h) = oBtn.GetSize()
            if iIdx == iSize - 2:
                y += h + 5
                x += 3
                continue
            y += h + 3
        

    
    def LayoutStyle2Btn(self, lHideBtn = ()):
        oSortList = self.GetShowBtnList(lHideBtn)
        oSortList.insert(0, self.m_ScaleBtn)
        if ratio.Is1024x768():
            (mx, y) = (4, 42)
        else:
            (mx, y) = (10, 42)
        for iIdx, oBtn in enumerate(oSortList):
            if iIdx == 0:
                x = mx + self.GetScaleBtnPosX()
            else:
                x = mx
            oBtn.SetPos(x, y)
            (_, h) = oBtn.GetSize()
            y += h
        

    
    def LayoutStyle3Btn(self, lHideBtn = ()):
        oSortList = self.GetShowBtnList(lHideBtn)
        oSortList.insert(0, self.m_ScaleBtn)
        if ratio.Is1024x768():
            (mx, y) = (4, 54)
        else:
            (mx, y) = (4, 54)
        for iIdx, oBtn in enumerate(oSortList):
            if iIdx == 0:
                x = mx + self.GetScaleBtnPosX()
            else:
                x = mx
            oBtn.SetPos(x, y)
            (_, h) = oBtn.GetSize()
            y += h - 2
        

    
    def LayoutStyle4Btn(self, lHideBtn = ()):
        oSortList = self.GetShowBtnList(lHideBtn)
        oSortList.insert(0, self.m_ScaleBtn)
        if ratio.Is1024x768():
            (mx, y) = (4, 80)
            dY = -3
        else:
            (mx, y) = (4, 80)
            dY = 0
        for iIdx, oBtn in enumerate(oSortList):
            if iIdx == 0:
                x = mx + self.GetScaleBtnPosX()
            else:
                x = mx
            oBtn.SetPos(x, y)
            (_, h) = oBtn.GetSize()
            h += dY
            y += h
        

    
    def LayoutNewBtn(self, lHideBtn = ()):
        oSortList = self.GetShowBtnList(lHideBtn)
        self.m_ScaleBtn.SetPos(*self.GetObject('loc_btn_hide').GetPos())
        (iStartX, iStartY) = self.GetObject('loc_btn_startpos').GetPos()
        for iIdx, oBtn in enumerate(oSortList):
            oBtn.SetPos(iStartX, iStartY)
            (_, iH) = oBtn.GetSize()
            iStartY += iH
        

    
    def ProcessBtnTips(self, sOrgTips):
        import key
        import dlgsysopt
        dTips2Key = {
            '\xa4\xe9\xbe\xe4': '\xa4\xe9\xbe\xe4\xac\xc9\xad\xb1',
            '\xb9\xda\xb7Q\xba\xeb\xc6F': '\xb9\xda\xb7Q\xba\xeb\xc6F',
            '\xb1H\xb0\xe2\xa4\xa4\xa4\xdf': '\xb1H\xb0\xe2\xa4\xa4\xa4\xdf\xac\xc9\xad\xb1',
            '\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf': '\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf' }
        if sOrgTips in dTips2Key:
            sTips = sOrgTips + '(' + key.hotkey2txt(dlgsysopt.g_HotKeys[dTips2Key[sOrgTips]]) + ')'
        else:
            sTips = sOrgTips
        return sTips

    
    def SetMapNameTxt(self, sTxt):
        for sName in [
            'txt_name1',
            'txt_name2',
            'txt_name3']:
            oTxt = self.GetObject(sName)
            if oTxt:
                pass
            oTxt.SetText(sTxt)
        
        self.AlignMapName()

    
    def AlignMapName(self):
        (x, y, w, h) = self.GetLocData('loc_name')
        oTxt = self.GetObject('txt_name1')
        (iTxtW, iTxtH) = oTxt.GetSize()
        (iOffsetX, iOffsetY) = interface.GetAlignXY(iTxtW, iTxtH, w, h, interface.ALIGN_CENTER_MIDDLE)
        x += iOffsetX
        y += iOffsetY
        oTxt.SetPos(x, y)
        oTxt = self.GetObject('txt_name2')
        if oTxt:
            oTxt.SetPos(x + 1, y)
        
        oTxt = self.GetObject('txt_name3')
        if oTxt:
            oTxt.SetPos(x + 2, y + 1)
        

    
    def UpdateSize(self):
        oImg = self.GetObject('img_bg')
        if not oImg:
            return None
        
        (self.m_Width, self.m_Height) = oImg.GetSize()

    
    def CreateNotifyBox(self):
        self.m_NotifyBoxs = []
        for sLocName in [
            'loc_tips1',
            'loc_tips2']:
            oLoc = self.GetObject(sLocName)
            if not oLoc:
                continue
            
            (x, y, w, h) = self.GetLocData(sLocName)
            oBox = CNotifyBox(self, w, h, 65280, 0, 7)
            oBox.SetPos(x, y)
            self.m_NotifyBoxs.append(oBox)
        

    
    def GetShowMapName(self):
        if not self.m_MapName:
            return ''
        
        import misc
        sTxtList = misc.GetWordsCN(self.m_MapName)
        self.m_NameLst = sTxtList
        sTxtList = sTxtList[:GetMapNameCutLen()]
        return ''.join(sTxtList)

    
    def RollShowName(self):
        iSize = len(self.m_NameLst)
        if iSize <= GetMapNameCutLen():
            self.m_ShowNameIdx = 0
            self.ReleaseTimer()
            return None
        
        if self.m_ShowNameIdx > iSize - GetMapNameCutLen():
            self.m_ShowNameIdx = 0
            self.ReleaseTimer()
            return None
        
        iStart = self.m_ShowNameIdx
        iEnd = self.m_ShowNameIdx + GetMapNameCutLen()
        tShowList = self.m_NameLst[iStart:iEnd]
        sShow = ''.join(tShowList)
        self.SetMapNameTxt(sShow)
        self.m_ShowNameIdx += 1

    
    def ReleaseTimer(self):
        if self.m_DelayTimer:
            self.m_DelayTimer.Release()
            self.m_DelayTimer = None
        

    
    def AddNotifyItem(self, iNotifyType, oNotifyItem):
        self.DelNotifyItem(iNotifyType)
        self.m_NotifyBtns.append((iNotifyType, oNotifyItem))
        self.RefreshNotifyItem()

    
    def DelNotifyItem(self, iNontifyType):
        iDelIdx = -1
        for iType, oItem in enumerate(self.m_NotifyBtns):
            if iType == iNontifyType:
                iDelIdx = idx
                break
                continue
        
        if iDelIdx >= 0:
            self.m_NotifyBtns.pop(iDelIdx)
            self.RefreshNotifyItem()
        

    
    def RefreshNotifyItem(self):
        (iStartX, iStartY) = None(self.GetObject, **'loc_notify').GetPos()
        for _, oItem in self.m_NotifyBtns:
            oItem.SetPos(iStartX, iStartY)
            (_, iH) = oItem.GetSize()
            iStartY += iH
        

    
    def OnMapBarEnter(self):
        import timer
        sTips = '\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xa5i\xa5\xb4\xb6}\xa1u\xa4p\xa6a\xb9\xcf\xa1v(Tab\xc1\xe4)'
        self.m_MiniMapTips = wrapinterface.CTextTips(self, -1, sTips, interface.FontLT14_3)
        (x, y, _, _) = self.GetLocData('loc_pos')
        self.m_MiniMapTips.SetPos(x, y)
        self.ReleaseTimer()
        if len(self.m_NameLst) > GetMapNameCutLen():
            self.m_DelayTimer = timer.Timer(0.3, self.RollShowName, -1)
        

    
    def OnMapBarLeave(self):
        self.m_MiniMapTips = None
        self.ReleaseTimer()
        sMapName = self.GetShowMapName()
        self.SetMapNameTxt(sMapName)

    
    def OnMessage(self, iMsgID):
        import nettask
        nettask.CloseTaskTips(1, iMsgID)
        if iMsgID == 6:
            self.ssEmit(self.SS_ClickSwitchBtn)
        elif iMsgID == 7:
            self.ssEmit(self.SS_TipsClick)
            guidectrl.GetGuideCtrl().ClickOrdObj(guidedefine.GUIDE_MAP_INFO_BAR, 'loc_guide')
        elif iMsgID in self.GetBtnOrder():
            guidectrl.GetGuideCtrl().ClickOrdObj(guidedefine.GUIDE_MAP_INFO_BAR, 'BTN%s' % iMsgID)
        
        self.ssEmit(self.SS_BtnClick, iMsgID)

    
    def OnNotifyMsg(self, iNotifyType):
        self.ssEmit(self.SS_ClickNotify, iNotifyType)



class CStyle1BtnBG(interface.CBaseObject):
    
    def __init__(self, oParent, oOriBG):
        interface.CBaseObject.__init__(self, oParent)
        self.m_oOriBG = oOriBG
        self.m_oBGList = []
        self.m_bSwitchShow = False
        self.m_iBtnNum = 6

    
    def SetBtnNum(self, iBtnNum):
        if self.m_iBtnNum != iBtnNum:
            self.m_iBtnNum = iBtnNum
            self.RefreshShow()
        

    
    def SwitchShow(self, bShow):
        if self.m_bSwitchShow != bShow:
            self.m_bSwitchShow = bShow
            self.RefreshShow()
        

    
    def RefreshShow(self):
        iBtnNum = self.m_iBtnNum
        if iBtnNum == 6 or not (self.m_bSwitchShow):
            self.m_oBGList = []
            self.m_oOriBG.SetShow(True)
            if not self.m_bSwitchShow:
                self.m_oOriBG.SetFrame(0)
            else:
                self.m_oOriBG.SetFrame(1)
        else:
            self.m_oOriBG.SetShow(False)
            self.m_oBGList = []
            (iStartX, iY) = (0, 0)
            sPathList = [
                ('mainmenu/mapinfo002_1.igs', 0)]
            for _ in range(iBtnNum - 1):
                sPathList.append(('mainmenu/mapinfo002_2.igs', 5))
            
            sPathList.append(('mainmenu/mapinfo002_3.igs', 6))
            for sPath, iOffsetX in sPathList:
                oImg = ui.CImage(self, sPath, interface.UIPath)
                (iW, iH) = oImg.GetSize()
                oImg.SetPos(iStartX + iOffsetX, iY)
                iY += iH
                self.m_oBGList.append(oImg)
            



class CNotifyBox(interface.CClickBox):
    
    def Enter(self):
        oParent = self.GetParent()
        if oParent and getattr(oParent, 'OnMapBarEnter'):
            oParent.OnMapBarEnter()
        

    
    def Leave(self):
        oParent = self.GetParent()
        if oParent and getattr(oParent, 'OnMapBarLeave'):
            oParent.OnMapBarLeave()
        



class CNotifyBtn(interface.CSpriteObject, interface.CBase):
    
    def __init__(self, parent, fname, path, oLeftUpCB):
        interface.CSpriteObject.__init__(self, parent, fname, path)
        self.MessageProcess()
        self.m_oLeftUpCB = oLeftUpCB

    
    def LeftUp(self):
        if self.m_oLeftUpCB:
            self.m_oLeftUpCB()
        


g_Test = None

def Test():
    global g_Test
    g_Test = CMapInfoBarPanel(interface.DialogPanel)
    g_Test.SetPos(100, 100)
    g_Test.SetZ(100000)
