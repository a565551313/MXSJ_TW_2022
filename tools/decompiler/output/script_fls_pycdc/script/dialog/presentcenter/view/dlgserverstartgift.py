# pycdc 交叉复核产物 · script.fls entry 4359
# co_filename(原始)='script/dialog/presentcenter/view/dlgserverstartgift.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4359.pyc (Python 2.5)

import chardefine
import charpath
import combdialog
import interface
import itemdata
import wrapinterface
import misc
import walker
import tipsclosemgr
import hero
import timer
import nethdnewupgrade
SUBPAGE_RANK = 1
SUBPAGE_UPGRADE = 2
SUMMONLIST = [
    4006,
    4007,
    4008,
    4020]
import dgtserverstartgift

def BuildSubWnd(oParent):
    return CServerStartGift(oParent)


class CServerStartGift(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        import dgtserverstartgift
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/signin/signin_new.dlg')
        self.m_oPartDict = { }
        self.m_dData = { }
        self.m_oNextTimer = None
        self.m_oDelegateList = [
            dgtserverstartgift.CServerStartGiftDelegate(self)]
        self.m_iLeftTime = 0
        self.GetObject('pagedow1').LeftUp()
        self.SetIgnoreEsc(True)

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetData(self, dData):
        '''
\t\t:param dict dData: { iRank: \xb1\xc6\xa6W, iLoginTime: \xb5n\xbf\xfd\xae\xc9\xb6\xa1, iEndTime: \xac\xa1\xb0\xca\xb5\xb2\xa7\xf4\xae\xc9\xb6\xa1 }
\t\t:return:
\t\t'''
        self.m_dData = dData
        iEndTime = dData['iEndTime']
        iCurTime = misc.GetServerCurrentTime()
        iDffTime = iEndTime - iCurTime
        LOG('CServerStartGift Time>>', iEndTime, iCurTime, iDffTime)
        self.SetTime(iDffTime)
        for iPage in (SUBPAGE_UPGRADE, SUBPAGE_RANK):
            oPage = self.GetPage(iPage)
            if oPage:
                oPage.SetData(self.m_dData)
                continue
        

    
    def SetTime(self, iDffTime):
        self.m_iLeftTime = iDffTime
        if self.m_oNextTimer:
            self.m_oNextTimer.Release()
        
        self.UpdateTimeTxt()
        self.m_oNextTimer = timer.Timer(1, self.UpdateTimeTxt, -1, self)

    
    def UpdateTimeTxt(self):
        if self.m_iLeftTime <= 0:
            sMsg = '\xac\xa1\xb0\xca\xa4w\xb5\xb2\xa7\xf4'
        elif self.m_iLeftTime < 60:
            sMsg = '\xb3\xd1\xbel%s\xac\xed' % self.m_iLeftTime
        elif self.m_iLeftTime < 3600:
            sMsg = '\xb3\xd1\xbel%s\xa4\xc0\xc4\xc1' % RoundUp(self.m_iLeftTime, 60)
        elif self.m_iLeftTime < 86400:
            iHour = self.m_iLeftTime / 3600
            iMin = RoundUp(self.m_iLeftTime - iHour * 3600, 60)
            sMsg = '\xb3\xd1\xbel%s\xa4p\xae\xc9%s\xa4\xc0\xc4\xc1' % (iHour, iMin)
        else:
            iDay = self.m_iLeftTime / 86400
            iHour = RoundUp(self.m_iLeftTime - iDay * 3600 * 24, 3600)
            sMsg = '\xb3\xd1\xbel%s\xa4\xd1%s\xa4p\xae\xc9' % (iDay, iHour)
        self.m_iLeftTime -= 1
        self.GetObject('txt_time1').SetText(sMsg)

    
    def SwitchPage(self, iPage):
        for \xb2Part in self.m_oPartDict.itervalues():
            \xb2Part.SetShow(False)
        
        if iPage in self.m_oPartDict:
            self.m_oPartDict[iPage].SetShow(True)
        else:
            oPage = {
                SUBPAGE_RANK: CRankPage,
                SUBPAGE_UPGRADE: CUpGradePage }[iPage](self)
            oPage.SetData(self.m_dData)
            self.m_oPartDict[iPage] = oPage

    
    def GetPage(self, iPage):
        return self.m_oPartDict.get(iPage, None)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 9:
            self.SwitchPage(SUBPAGE_RANK)
        elif iMsgID == 15:
            self.SwitchPage(SUBPAGE_UPGRADE)
        



class CUpGradePage(combdialog.CCombSubWnd):
    ITEMLIST = [
        (25431, 3),
        (25707, 2),
        (25404, 10)]
    TIME_LIMIT = 60
    GRADE_LIMIT = 50
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/signin/lvlupReward_new.dlg')
        self.m_oFakeRoleList = []
        self.m_oItemIconList = []
        self.InitDlg()
        self.SetIgnoreEsc(True)

    
    def SetData(self, dData):
        iLoginTime = dData.get('iLoginTime', 0)
        self.SetLoginTime(iLoginTime / 3600)

    
    def InitDlg(self):
        for iIndex, iShape in enumerate(SUMMONLIST):
            (iX, iY) = self.GetObject('loc_summon%s' % (iIndex + 1)).GetPos()
            oAni = walker.CFakeRole(self, -1, iShape, misc.DeepCopy(chardefine.DESC.DEFAULT))
            oAni.SetPos(iX, iY)
            self.m_oFakeRoleList.append(oAni)
        
        for iShape, iAmount in enumerate(self.ITEMLIST):
            (iX, iY) = self.GetObject('img_reward%s' % (iIndex + 1)).GetPos()
            oIcon = wrapinterface.CItemIcon(self, iShape, iAmount, 100 + iIndex)
            oIcon.SetPos(iX, iY)
            self.m_oItemIconList.append(oIcon)
        
        hero.AddRefreshCallback('CUpGradePage', ('m_Grade',), self.OnGradeUpdate)

    
    def OnGradeUpdate(self):
        self.SetLoginLevel(hero.GetProp('m_Grade'))

    
    def SetLoginTime(self, iTime):
        self.GetObject('txt_time2').ReplaceText({
            '60': '%s/%s' % (iTime, self.TIME_LIMIT) })
        self.GetObject('prg_time').SetRate(min(1000, iTime * 1000 / self.TIME_LIMIT))
        self.GetObject('img_check2').SetShow(iTime < self.TIME_LIMIT)
        self.GetObject('img_check1').SetShow(iTime >= self.TIME_LIMIT)

    
    def SetLoginLevel(self, iLevel):
        self.GetObject('txt_level').ReplaceText({
            '30': str(iLevel) })
        self.GetObject('prg_level').SetRate(min(1000, iLevel * 1000 / self.GRADE_LIMIT))
        self.GetObject('img_check4').SetShow(iLevel < self.GRADE_LIMIT)
        self.GetObject('img_check3').SetShow(iLevel >= self.GRADE_LIMIT)

    
    def OnIconEnter(self, oIcon):
        iShape = oIcon.m_Shape
        (sName, sDesc) = itemdata.GetData(iShape)
        tipsclosemgr.Regist(wrapinterface.CItemTips(iShape, None, sName, sDesc, parent = self))

    
    def OnIconLeave(self, oIcon):
        tipsclosemgr.CheckClose()

    
    def RefreshBtn(self, bEnable, sBtnTxt, sMsg = None):
        oBtn = self.GetObject('txtbtn_def')
        oBtn.FakeEnable(bEnable, sMsg)
        oBtn.SetText(sBtnTxt)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            pass
        elif iMsgID == 2:
            nethdnewupgrade.C2SShowPlayers()
        



class CNewServerUpGradePage(CUpGradePage):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/activity/newserver/signin/lvlupReward_new.dlg')
        self.m_oFakeRoleList = []
        self.m_oItemIconList = []
        self.m_dData = { }
        self.m_iLeftTime = 0
        self.m_oNextTimer = None
        self.InitDlg()
        self.m_oDelegateList = [
            dgtserverstartgift.CNewServerUpGradeDelegate(self)]
        self.SetIgnoreEsc(True)

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetData(self, dData):
        '''
\t\t:param dict dData: { iRank: \xb1\xc6\xa6W, iLoginTime: \xb5n\xbf\xfd\xae\xc9\xb6\xa1, iEndTime: \xac\xa1\xb0\xca\xb5\xb2\xa7\xf4\xae\xc9\xb6\xa1 }
\t\t:return:
\t\t'''
        self.m_dData = dData
        iEndTime = dData['iEndTime']
        iCurTime = misc.GetServerCurrentTime()
        iDffTime = iEndTime - iCurTime
        LOG('CServerStartGift Time>>', iEndTime, iCurTime, iDffTime)
        self.SetTime(iDffTime)
        CUpGradePage.SetData(self, self.m_dData)

    
    def SetTime(self, iDffTime):
        self.m_iLeftTime = iDffTime
        if self.m_oNextTimer:
            self.m_oNextTimer.Release()
        
        self.UpdateTimeTxt()
        self.m_oNextTimer = timer.Timer(1, self.UpdateTimeTxt, -1, self)

    
    def UpdateTimeTxt(self):
        if self.m_iLeftTime <= 0:
            sMsg = '\xac\xa1\xb0\xca\xa4w\xb5\xb2\xa7\xf4'
        elif self.m_iLeftTime < 60:
            sMsg = '\xb3\xd1\xbel%s\xac\xed' % self.m_iLeftTime
        elif self.m_iLeftTime < 3600:
            sMsg = '\xb3\xd1\xbel%s\xa4\xc0\xc4\xc1' % RoundUp(self.m_iLeftTime, 60)
        elif self.m_iLeftTime < 86400:
            iHour = self.m_iLeftTime / 3600
            iMin = RoundUp(self.m_iLeftTime - iHour * 3600, 60)
            sMsg = '\xb3\xd1\xbel%s\xa4p\xae\xc9%s\xa4\xc0\xc4\xc1' % (iHour, iMin)
        else:
            iDay = self.m_iLeftTime / 86400
            iHour = RoundUp(self.m_iLeftTime - iDay * 3600 * 24, 3600)
            sMsg = '\xb3\xd1\xbel%s\xa4\xd1%s\xa4p\xae\xc9' % (iDay, iHour)
        self.m_iLeftTime -= 1
        self.GetObject('txt_time1').SetText(sMsg)



class CRankPage(combdialog.CCombSubWnd):
    TITLE = '\xbd\xd6\xbbP\xaa\xa7\xbeW'
    ITEMLIST = [
        (73491, 1),
        (73492, 1),
        (70239, 40),
        (70240, 4),
        (25431, 12),
        (73492, 1),
        (70239, 25),
        (70240, 2),
        (25431, 8),
        (70239, 25),
        (70240, 2),
        (25431, 8),
        (70239, 15),
        (70240, 1),
        (25431, 6)]
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/signin/rankReward_new.dlg')
        self.m_oItemIconList = []
        self.m_oPetAni = None
        self.InitDlg()
        self.SetIgnoreEsc(True)

    
    def SetData(self, dData):
        if 'iRank' in dData:
            if dData['iRank'] == 0:
                sRank = '\xa5\xbc\xa4W\xba]'
            else:
                sRank = str(dData['iRank'])
            self.GetObject('txt_myrank').SetText(sRank)
        

    
    def InitDlg(self):
        for iShape, iAmount in enumerate(self.ITEMLIST):
            (iX, iY) = self.GetObject('img_reward%s' % (iIndex + 1)).GetPos()
            oIcon = wrapinterface.CItemIcon(self, iShape, iAmount, 100 + iIndex)
            oIcon.SetPos(iX, iY)
            self.m_oItemIconList.append(oIcon)
        
        (iX, iY) = self.GetObject('loc_character').GetPos()
        self.m_oPetAni = self.GetTitleHero()
        self.m_oPetAni.SetPos(iX, iY)
        self.m_oPetAni.SetZ(10)

    
    def GetTitleHero(self):
        (iHeroShape, dDesc) = charpath.GetHeroShow()
        for sName in ('horse', 'track', 'aura'):
            if sName in dDesc:
                del dDesc[sName]
                continue
        
        oPetAni = walker.CFakeRole(self, -1, iHeroShape, dDesc)
        if hero.GetProp('m_FlyFlag') & 128:
            iColor = interface.COLOR_53
            iFont = interface.FontLT16E_1
        elif hero.GetProp('m_NameColor') == 1:
            iColor = interface.COLOR_42
            iFont = interface.FontLT16_1
        else:
            iColor = interface.COLOR_41
            iFont = interface.FontLT16_1
        if hero.GetProp('m_FakeName'):
            sName = hero.GetProp('m_FakeName')
        else:
            sName = hero.GetProp('m_Name')
        oName = hero.GetHeroObject().GetNameObject()
        if oName:
            dExpend = None
        else:
            dExpend = None
        oPetAni.SetName(sName, hero.GetHeroID(), hero.GetProp('m_Country'), iColor, font = iFont, iSiblingType = hero.GetProp('m_iSiblingType', 0), dExtend = dExpend)
        oPetAni.SetTitle2(self.TITLE)
        return oPetAni

    
    def OnIconEnter(self, oIcon):
        iShape = oIcon.m_Shape
        (sName, sDesc) = itemdata.GetData(iShape)
        tipsclosemgr.Regist(wrapinterface.CItemTips(iShape, None, sName, sDesc, parent = self))

    
    def OnIconLeave(self, oIcon):
        tipsclosemgr.CheckClose()

    
    def OnMessage(self, iMsgID):
        import dlgrank
        if iMsgID == 1:
            dlgrank.C2SShowRank(37)
        elif iMsgID == 2:
            nethdnewupgrade.C2SOpenUploadInfo()
        



class CNewServerRankPage(CRankPage):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/activity/newserver/signin/rankReward_new.dlg')
        self.m_dData = { }
        self.m_iLeftTime = 0
        self.m_oNextTimer = None
        self.m_oItemIconList = []
        self.m_oPetAni = None
        self.InitDlg()
        self.m_oDelegateList = [
            dgtserverstartgift.CNewServerRankDelegate(self)]
        self.SetIgnoreEsc(True)

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def SetData(self, dData):
        '''
\t\t:param dict dData: { iRank: \xb1\xc6\xa6W, iLoginTime: \xb5n\xbf\xfd\xae\xc9\xb6\xa1, iEndTime: \xac\xa1\xb0\xca\xb5\xb2\xa7\xf4\xae\xc9\xb6\xa1 }
\t\t:return:
\t\t'''
        self.m_dData = dData
        iEndTime = dData['iEndTime']
        iCurTime = misc.GetServerCurrentTime()
        iDffTime = iEndTime - iCurTime
        LOG('CServerStartGift Time>>', iEndTime, iCurTime, iDffTime)
        self.SetTime(iDffTime)
        CRankPage.SetData(self, self.m_dData)

    
    def SetTime(self, iDffTime):
        self.m_iLeftTime = iDffTime
        if self.m_oNextTimer:
            self.m_oNextTimer.Release()
        
        self.UpdateTimeTxt()
        self.m_oNextTimer = timer.Timer(1, self.UpdateTimeTxt, -1, self)

    
    def UpdateTimeTxt(self):
        if self.m_iLeftTime <= 0:
            sMsg = '\xac\xa1\xb0\xca\xa4w\xb5\xb2\xa7\xf4'
        elif self.m_iLeftTime < 60:
            sMsg = '\xb3\xd1\xbel%s\xac\xed' % self.m_iLeftTime
        elif self.m_iLeftTime < 3600:
            sMsg = '\xb3\xd1\xbel%s\xa4\xc0\xc4\xc1' % RoundUp(self.m_iLeftTime, 60)
        elif self.m_iLeftTime < 86400:
            iHour = self.m_iLeftTime / 3600
            iMin = RoundUp(self.m_iLeftTime - iHour * 3600, 60)
            sMsg = '\xb3\xd1\xbel%s\xa4p\xae\xc9%s\xa4\xc0\xc4\xc1' % (iHour, iMin)
        else:
            iDay = self.m_iLeftTime / 86400
            iHour = RoundUp(self.m_iLeftTime - iDay * 3600 * 24, 3600)
            sMsg = '\xb3\xd1\xbel%s\xa4\xd1%s\xa4p\xae\xc9' % (iDay, iHour)
        self.m_iLeftTime -= 1
        self.GetObject('txt_time1').SetText(sMsg)



def RoundUp(iBigNum, iSmallNum, iRoundUpMin = 0):
    iRet = iBigNum / iSmallNum
    if iBigNum % iSmallNum > iRoundUpMin:
        iRet += 1
    
    return iRet
