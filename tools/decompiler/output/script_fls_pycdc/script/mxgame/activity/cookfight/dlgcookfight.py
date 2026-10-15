# pycdc 交叉复核产物 · script.fls entry 696
# co_filename(原始)='script/mxgame/activity/cookfight/dlgcookfight.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_696.pyc (Python 2.5)

import interface
import combdialog
import slot
import commoncb
g_CookFightDlg = None
g_CookFightMinDlg = None
g_CollectDlg = None
g_CollectMinDlg = None
g_SettingDlg = None
DAY_LIST = ('\xa4\xb5\xa4\xd1', '\xa9\xfa\xa4\xd1')
MINUTE_LIST = ('0', '10', '20', '30', '40', '50')

def ModuleReset():
    global g_CookFightDlg, g_CookFightMinDlg, g_CollectDlg, g_CollectMinDlg
    g_CookFightDlg = None
    g_CookFightMinDlg = None
    g_CollectDlg = None
    g_CollectMinDlg = None


def ShowCookFightDlg():
    global g_CookFightDlg
    if not g_CookFightDlg:
        g_CookFightDlg = CCookFightDlg()
    else:
        g_CookFightDlg.SetShow(True)
        g_CookFightDlg.Topmost()


def ShowCookFightMinDlg():
    global g_CookFightMinDlg
    if not g_CookFightMinDlg:
        g_CookFightMinDlg = CCookFightMinDlg()
    else:
        g_CookFightMinDlg.SetShow(True)
        g_CookFightMinDlg.Topmost()


def GetCookFightDlg():
    return g_CookFightDlg


def GetCookFightMinDlg():
    return g_CookFightMinDlg


def CloseCookFightDlg():
    global g_CookFightDlg
    if g_CookFightDlg:
        g_CookFightDlg = None
    


def CloseCookFightMinDlg():
    global g_CookFightMinDlg
    if g_CookFightMinDlg:
        g_CookFightMinDlg = None
    


def ShowCollectDlg():
    global g_CollectDlg
    if not g_CollectDlg:
        g_CollectDlg = CCollectDlg()
    else:
        g_CollectDlg.SetShow(True)
        g_CollectDlg.Topmost()


def ShowCollectMinDlg():
    global g_CollectMinDlg
    if not g_CollectMinDlg:
        g_CollectMinDlg = CCollectMiniDlg()
    else:
        g_CollectMinDlg.SetShow(True)
        g_CollectMinDlg.Topmost()


def GetCollectDlg():
    return g_CollectDlg


def GetCollectMinDlg():
    return g_CollectMinDlg


def CloseCollectDlg():
    global g_CollectDlg
    if g_CollectDlg:
        g_CollectDlg = None
    


def CloseCollectMinDlg():
    global g_CollectMinDlg
    if g_CollectMinDlg:
        g_CollectMinDlg = None
    


def ShowSetting():
    global g_SettingDlg
    if not g_SettingDlg:
        g_SettingDlg = CSettingDlg()
    else:
        g_CollectMinDlg.SetShow(True)
        g_CollectMinDlg.Topmost()


class CCookFightDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ShowMini = 'SS_ShowMini(True)'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/cookfight/cookfight.dlg')
        self.ssInit()
        interface.BottomLeft(self, 0, -25)
        self.SetIgnoreEsc(True)
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnSceneChange')
        self.OnSceneChange()

    
    def IsMiniDlg(self):
        return False

    
    def OnSceneChange(self, *args):
        import map
        import mapdefine
        if map.GetCurrentMapID() not in mapdefine.GROUP_MAP_ID_EX:
            self.ssEmit(self.SS_ShowMini, True)
        

    
    def SetTitle(self, sTitle):
        oTitle = self.GetObject('txt_title')
        if oTitle:
            pass
        oTitle.SetText(sTitle)

    
    def \xcbetName(self, iIdx, sName):
        oName = self.GetObject('txt_name%d' % iIdx)
        if oName:
            pass
        oName.SetText(sName)

    
    def SetTips(self, sTips):
        oTips = self.GetObject('txt_tips')
        if oTips:
            pass
        oTips.SetText(sTips)

    
    def SetProgress(self, iIdx, iRate):
        oProgress = self.GetObject('progress_%d' % iIdx)
        if oProgress:
            pass
        oProgress.SetRate(iRate)

    
    def SetFinishProgress(self, iRate):
        iRate = min(iRate, 1000)
        oProgress = self.GetObject('progress_finish')
        if oProgress:
            pass
        oProgress.SetRate(iRate)
        oTxt = self.GetObject('txt_finish')
        oTxt.SetText('%d%%' % iRate / 10)
        oTxt.SetZ(1)

    
    def SetBestStart(self, iIdx, iBestRatio, iCurRatio):
        oBestStar = self.GetObject('img_star%d' % iIdx)
        oBlackStar = self.GetObject('img_bstar%d' % iIdx)
        if iCurRatio >= iBestRatio:
            oBestStar.SetPath('combdialog/\xd4\xd3\xcd\xbc/\xd0\xc71.igs')
        else:
            oBestStar.SetPath('combdialog/\xd4\xd3\xcd\xbc/\xd0\xc72.igs')
        (iLocX, iLocY, iLocW, iLocH) = self.GetLocData('progress_%d' % iIdx)
        (iStarW, iStarH) = oBestStar.GetSize()
        iPosX = iLocW * iBestRatio / 1000
        oBestStar.SetPos(iLocX + iPosX - iStarW / 2, iLocY + (iLocH - iStarH) / 2)
        oBestStar.SetShow(True)
        oBestStar.SetZ(1)
        oBlackStar.SetShow(False)

    
    def SetBlackStart(self, iIdx, iBestRatio, iCurRatio):
        oBestStar = self.GetObject('img_star%d' % iIdx)
        oBlackStar = self.GetObject('img_bstar%d' % iIdx)
        if iCurRatio >= iBestRatio:
            oBlackStar.SetPath('combdialog/\xd4\xd3\xcd\xbc/\xbb\xc6\xd0\xc71.igs')
        else:
            oBlackStar.SetPath('combdialog/\xd4\xd3\xcd\xbc/\xbb\xc6\xd0\xc72.igs')
        (iLocX, iLocY, iLocW, iLocH) = self.GetLocData('progress_%d' % iIdx)
        (iStarW, iStarH) = oBlackStar.GetSize()
        iPosX = iLocW * iBestRatio / 1000
        oBlackStar.SetPos(iLocX + iPosX - iStarW / 2, iLocY + (iLocH - iStarH) / 2)
        oBlackStar.SetShow(True)
        oBlackStar.SetZ(2)
        oBestStar.SetShow(False)

    
    def ShowBackTips(self, sTxt, iDark):
        oTxt1 = self.GetObject('txt_dark_tips1')
        oTxt2 = self.GetObject('txt_dark_tips2')
        oTxt3 = self.GetObject('txt_dark_tips3')
        if sTxt:
            oTxt2.SetText(sTxt)
            if iDark:
                oTxt1.SetShow(False)
                oTxt2.SetShow(False)
                oTxt3.SetShow(True)
            else:
                oTxt1.SetShow(True)
                oTxt2.SetShow(True)
                oTxt3.SetShow(False)
        else:
            oTxt1.SetShow(False)
            oTxt2.SetShow(False)
            oTxt3.SetShow(False)

    
    def SetNxtHeatChange(self, bShow, bUp, sHeat, sTips):
        oImgFire = self.GetObject('img_huoyan')
        oImgWeather = self.GetObject('img_shuidi')
        oImgUp = self.GetObject('img_up')
        oImgDown = self.GetObject('img_down')
        oTxt1 = self.GetObject('txt_fire_tips1')
        oTxt2 = self.GetObject('txt_fire_tips2')
        oTips = self.GetObject('tips_change')
        if bShow:
            oImgFire.SetShow(bUp)
            oImgWeather.SetShow(not bUp)
            oImgUp.SetShow(bUp)
            oImgDown.SetShow(not bUp)
            oTxt1.SetShow(True)
            oTxt2.SetShow(True)
            oTxt2.SetText(sHeat)
            oTips.SetShow(True)
            oTips.SetTips(sTips)
        else:
            oImgFire.SetShow(False)
            oImgWeather.SetShow(False)
            oImgUp.SetShow(False)
            oImgDown.SetShow(False)
            oTxt1.SetShow(False)
            oTxt2.SetShow(False)
            oTips.SetShow(False)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ShowMini, True)
        



class CCookFightMinDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ShowMini = 'SS_ShowMini(False)'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/cookfight/cookfightmin.dlg')
        self.ssInit()
        interface.BottomLeft(self, 0, -225)
        self.SetIgnoreEsc(True)
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnSceneMiniChange')
        self.OnSceneMiniChange()

    
    def IsMiniDlg(self):
        return True

    
    def Enter(self):
        import wrapinterface
        self.m_oTips = wrapinterface.CTextTips(self, 150, '\xb0h\xa5X\xb6\xa4\xa5\xee\xa5i\xc3\xf6\xb3\xac\xb8\xd3\xac\xc9\xad\xb1', interface.FontLT14, owner = self)

    
    def Leave(self):
        self.m_oTips = None

    
    def OnSceneMiniChange(self, *args):
        import map
        import mapdefine
        if map.GetCurrentMapID() in mapdefine.GROUP_MAP_ID_EX:
            self.ssEmit(self.SS_ShowMini, False)
        

    
    def SetTitle(self, sTitle):
        oTitle = self.GetObject('txt_title')
        if oTitle:
            pass
        oTitle.SetText(sTitle)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ShowMini, False)
        



class CCollectDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ShowMini = 'SS_ShowMini(True)'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/cookfight/cookcolletion.dlg')
        self.ssInit()
        interface.BottomLeft(self, 0, -25)
        self.SetIgnoreEsc(True)
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnSceneChange')

    
    def OnSceneChange(self, *args):
        import map
        import mapdefine
        if map.GetCurrentMapID() not in mapdefine.GROUP_MAP_ID_EX:
            self.ssEmit(self.SS_ShowMini, True)
        

    
    def IsMiniDlg(self):
        return False

    
    def SetDesc(self, sDesc):
        oTxt = self.GetObject('txt_tips')
        if oTxt:
            pass
        oTxt.SetText(sDesc)

    
    def SetTitle(self, sTitle):
        oTitle = self.GetObject('txt_title')
        if oTitle:
            pass
        oTitle.SetText(sTitle)

    
    def \xcbetName(self, iIdx, sName):
        oName = self.GetObject('txt_name%d' % iIdx)
        if oName:
            pass
        oName.SetText(sName)

    
    def SetTips(self, sTips):
        oTips = self.GetObject('txt_tips')
        if oTips:
            pass
        oTips.SetText(sTips)

    
    def SetProgress(self, iIdx, iRate):
        oProgress = self.GetObject('progress_%d' % iIdx)
        if oProgress:
            pass
        oProgress.SetRate(iRate)

    
    def SetBestStart(self, iIdx, iBestRatio, iCurRatio):
        oStar = self.GetObject('img_star%d' % iIdx)
        if iCurRatio >= iBestRatio:
            oStar.SetPath('combdialog/\xd4\xd3\xcd\xbc/\xd0\xc71.igs')
        else:
            oStar.SetPath('combdialog/\xd4\xd3\xcd\xbc/\xd0\xc72.igs')
        (iLocX, iLocY, iLocW, iLocH) = self.GetLocData('progress_%d' % iIdx)
        (iStarW, iStarH) = oStar.GetSize()
        iPosX = iLocW * iBestRatio / 1000
        oStar.SetPos(iLocX + iPosX - iStarW / 2, iLocY + (iLocH - iStarH) / 2)
        oStar.SetZ(1)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ShowMini, True)
        



class CCollectMiniDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ShowMini = 'SS_ShowMini(False)'
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/cookfight/cookfightmin.dlg')
        self.ssInit()
        interface.BottomLeft(self, 0, -225)
        self.SetIgnoreEsc(True)
        commoncb.RegistCB(commoncb.SCENE_CHANGE, self, 'OnSceneMiniChange')

    
    def IsMiniDlg(self):
        return True

    
    def OnSceneMiniChange(self, *args):
        import map
        import mapdefine
        if map.GetCurrentMapID() in mapdefine.GROUP_MAP_ID_EX:
            self.ssEmit(self.SS_ShowMini, False)
        

    
    def SetTitle(self, sTitle):
        oTitle = self.GetObject('txt_title')
        if oTitle:
            pass
        oTitle.SetText(sTitle)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_ShowMini, False)
        



class CSettingDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/cookfight/cookbattle_new.dlg')
        interface.Center(self)
        self.m_oTimeEdit = None
        self.m_iMinute = 0
        self.m_iDate = 0
        self.InitEdit()
        self.RefreshDaySelect(self.m_iDate)
        self.RefreshMinuteSelect(self.m_iMinute)

    
    def InitEdit(self):
        import combmacro
        import wrapedit
        self.m_oTimeEdit = combmacro.CEDIT(wrapedit.CLimitNumberEdit, 'loc_time', self, interface.COLOR_5, interface.FontLT14_3)
        self.m_oTimeEdit.SetLimit(2)
        self.m_oTimeEdit.SetMaxNum(22)
        self.m_oTimeEdit.Active(True)

    
    def CloseWindow(self):
        global g_SettingDlg
        g_SettingDlg = None

    
    def GetInputTime(self):
        if not self.CheckTimeVaild():
            return None
        
        sTime = self.m_oTimeEdit.GetText()
        return int(sTime)

    
    def CheckTimeVaild(self):
        import usermacro
        import time
        import datetime
        sTime = self.m_oTimeEdit.GetText()
        if not sTime.isdigit():
            usermacro.PROMPT_MSG('\xbd\xd0\xb6\xf1\xbcg\xa5\xbf\xbdT\xaa\xba\xae\xc9\xb6\xa1')
            return False
        else:
            iTime = int(sTime)
        iCurTime = self.GetCurTime()
        iCurTimeList = time.localtime(iCurTime)
        iMinute = self.GetMinute()
        iLocalTime = time.localtime(iCurTime)
        oCurDate = datetime.datetime(iLocalTime.tm_year, iLocalTime.tm_mon, iLocalTime.tm_mday)
        iWeekDay = oCurDate.weekday() + 1
        if iTime == 22 and iMinute > 0:
            usermacro.PROMPT_MSG('\xa5i\xa5H\xb3]\xb8m\xaa\xba\xb3\xcc\xb1\xdf\xae\xc9\xb6\xa1\xac\xb022\xc2I00\xa4\xc0')
            return False
        
        if self.GetSelectDay() == 1:
            iStartTimeList = list(iCurTimeList[:3]) + [
                iTime,
                iMinute,
                0,
                0,
                0,
                0]
            iStartTime = time.mktime(iStartTimeList)
            iNextSecond = 6000
            if iStartTime < iCurTime + iNextSecond:
                iEarliestTime = iCurTime + iNextSecond
                iEarliestTimeList = time.localtime(iEarliestTime)
                LOG_DEBUG('>>>>iCurTimeList>>>>>>>>>', iCurTimeList)
                LOG_DEBUG('>>>>iLowestTimeList>>>>>>', iEarliestTimeList)
                (iLowestHour, iLowestMinute) = self.CorrectionEarliestTime(iEarliestTimeList[3], iEarliestTimeList[4])
                if iLowestHour >= 24 or iEarliestTimeList[2] != iCurTimeList[2]:
                    usermacro.PROMPT_MSG('\xa4\xb5\xa4\xd1\xa4\xd3\xb1\xdf\xa4F\xa1A\xc1\xd9\xacO\xb3]\xb8m\xa9\xfa\xa4\xd1\xb6}\xb1\xd2\xa7a')
                else:
                    usermacro.PROMPT_MSG('\xa5i\xa5H\xb3]\xb8m\xaa\xba\xb3\xcc\xa6\xad\xb6}\xb1\xd2\xae\xc9\xb6\xa1\xac\xb0\xa4\xb5\xa4\xd1\xaa\xba%02d\xc2I%02d\xa4\xc0' % (iLowestHour, iLowestMinute))
                return False
            
        
        if self.GetSelectDay() != 1 and iWeekDay == 7:
            usermacro.PROMPT_MSG('\xa5u\xaf\xe0\xb3]\xb8m\xa5\xbb\xa9P\xaa\xba\xae\xc9\xb6\xa1\xb6}\xb1\xd2')
            return False
        
        return True

    
    def CorrectionEarliestTime(self, iHour, iMinute):
        if iMinute < iMinute:
            pass
        elif iMinute <= 10:
            iLowestHour = iHour
            iLowestMinute = 10
        elif iMinute < iMinute:
            pass
        elif iMinute <= 20:
            iLowestHour = iHour
            iLowestMinute = 20
        elif iMinute < iMinute:
            pass
        elif iMinute <= 30:
            iLowestHour = iHour
            iLowestMinute = 30
        elif iMinute < iMinute:
            pass
        elif iMinute <= 40:
            iLowestHour = iHour
            iLowestMinute = 40
        elif iMinute < iMinute:
            pass
        elif iMinute <= 50:
            iLowestHour = iHour
            iLowestMinute = 50
        elif iMinute < iMinute:
            pass
        elif iMinute <= 59:
            iLowestHour = iHour + 1
            iLowestMinute = 0
        else:
            iLowestHour = iHour
            iLowestMinute = 0
        return (iLowestHour, iLowestMinute)

    
    def GetCurTime(self):
        import misc
        import time
        iCurTime = misc.GetServerCurrentTime()
        iCurTimeList = time.localtime(iCurTime)
        iSec = iCurTimeList[5]
        if iSec > 0:
            iCompensation = 60 - iSec
        else:
            iCompensation = 0
        iCurTime += iCompensation
        return iCurTime

    
    def GetDay(self):
        import misc
        import time
        iCurTime = misc.GetServerCurrentTime()
        if self.GetSelectDay() == 2:
            iCurTime += 86400
        
        iTimeList = time.localtime(iCurTime)
        sWeek = time.strftime('%w', iTimeList)
        if sWeek.isdigit():
            iWeek = int(sWeek)
            if iWeek == 0:
                iWeek = 7
            
            return iWeek
        

    
    def GetMinute(self):
        return [
            0,
            10,
            20,
            30,
            40,
            50][self.GetSelectMunite() - 1]

    
    def ChangeTime(self):
        import commondialog
        import misc
        iDay = self.GetDay()
        iTime = self.GetInputTime()
        iMinute = self.GetMinute()
        if iTime is None or iDay is None:
            return None
        
        
        def OKFunc(dlg):
            import group
            import netgroup
            obj = dlg.m_ShadowObj.Get()
            if obj:
                LOG_DEBUG('\xb3]\xb8m\xc0\xb0\xac\xa3\xac\xfc\xad\xb9\xa7{\xae\xc9\xb6\xa1>', group.COOK_FIGHT_HD_ID, dlg.m_Day, dlg.m_Time, dlg.m_Minute)
                netgroup.C2SSetHDOpenTime(group.COOK_FIGHT_HD_ID, dlg.m_Day, dlg.m_Time, dlg.m_Minute)
                obj.CloseWindow()
            

        sDay = ('\xa4\xb5\xa4\xd1', '\xa9\xfa\xa4\xd1')[self.GetSelectDay() - 1]
        sTips = '\xac\xa1\xb0\xca\xae\xc9\xb6\xa1\xa8C\xa4\xd1\xa5u\xaf\xe0\xb3]\xb8m\xa4@\xa6\xb8\xa1A\xa7A\xbdT\xa9w\xadn\xa6b%s\xaa\xba%d\xc2I%d\xa4\xc0\xb6i\xa6\xe6\xac\xa1\xb0\xca\xb6\xdc\xa1H' % (sDay, iTime, iMinute)
        dlg = commondialog.ShowMessageBox(sTips, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (OKFunc, None))
        dlg.m_ShadowObj = misc.WeakRef(self)
        dlg.m_Day = iDay
        dlg.m_Time = iTime
        dlg.m_Minute = iMinute

    
    def GetSelectDay(self):
        if self.m_iDate == 0:
            return 1
        else:
            return self.m_iDate + 1

    
    def GetSelectMunite(self):
        if self.m_iMinute == 0:
            return 1
        else:
            return self.m_iMinute + 1

    
    def RefreshDaySelect(self, iIdx):
        if iIdx < 0:
            return None
        elif iIdx > len(DAY_LIST) - 1:
            return None
        else:
            sDay = DAY_LIST[iIdx]
            self.m_iDate = iIdx
            self.GetObject('txt_date').SetText(sDay)
            bShowAddBtn = iIdx == len(DAY_LIST) - 1
            bShowReduceBtn = iIdx == 0
            self.SetAddBtnShow('btn_right', not bShowAddBtn)
            self.SetAddBtnShow('btn_left', not bShowReduceBtn)

    
    def RefreshMinuteSelect(self, iIdx):
        if iIdx < 0:
            return None
        elif iIdx > len(MINUTE_LIST) - 1:
            return None
        else:
            sMinute = MINUTE_LIST[iIdx]
            self.m_iMinute = iIdx
            self.GetObject('txt_min').SetText(sMinute)
            bShowAddBtn = iIdx == len(MINUTE_LIST) - 1
            bShowReduceBtn = iIdx == 0
            self.SetAddBtnShow('btn_add', not bShowAddBtn)
            self.SetAddBtnShow('btn_reduce', not bShowReduceBtn)

    
    def SetAddBtnShow(self, sBtnName, bShow):
        oUI = self.GetObject(sBtnName)
        oUI.SetShow(bShow)

    
    def SetReduceBtnShow(self, sBtnName, bShow):
        oUI = self.GetObject(sBtnName)
        oUI.SetShow(bShow)

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            self.ChangeTime()
        elif msgid == 3:
            self.RefreshDaySelect(self.m_iDate - 1)
        elif msgid == 4:
            self.RefreshDaySelect(self.m_iDate + 1)
        elif msgid == 5:
            self.RefreshMinuteSelect(self.m_iMinute - 1)
        elif msgid == 6:
            self.RefreshMinuteSelect(self.m_iMinute + 1)
        elif msgid == interface.RIGHT_BUTTON_MESSAGE + 5:
            self.RefreshMinuteSelect(0)
        elif msgid == interface.RIGHT_BUTTON_MESSAGE + 6:
            self.RefreshMinuteSelect(len(MINUTE_LIST) - 1)
