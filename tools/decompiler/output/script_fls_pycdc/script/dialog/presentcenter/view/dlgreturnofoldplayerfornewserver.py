# pycdc 交叉复核产物 · script.fls entry 3758
# co_filename(原始)='script/dialog/presentcenter/view/dlgreturnofoldplayerfornewserver.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3758.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/4/20 14:26
\xd7\xf7\xd5\xdf: gesaferoc
\xce\xc4\xbc\xfe: dlgreturnofoldplayerfornewserver
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import time
import activityiconbase
import combdialog
import hero
import huodongreworditemdata
import interface
import makeitemicon
import mdmvpnormal
import misc
import nethdpresentcenter
import pagedlgbase
import slot
import timer
import ui

def BuildSubWnd(oParent):
    return CReturnForNewServerDlg(oParent)


class CReturnForNewServerDlg(combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/new_player_present/welfar/welfar_returngift.dlg')
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.m_DelegateList = []
        self.m_oTittleListPart = CTittleListPart(self.GetObject('tbview_list'), self.OnClickGetItem)
        self.m_oTimer = timer.Timer(1, self.SetTimeText, -1, self)
        self.GetDataMD().ssConnect('m_dReturnRewardInfo', self.OnChangeInfo)
        nethdpresentcenter.C2GSBackManGiftGetInfo()
        self.ShowList()
        self.SetTimeText()

    
    def GetDataMD(self):
        return mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_RETURN_FOR_NEW_SERVER_HD)

    
    def ShowList(self):
        sKey = 'returnfornewsever'
        lInfo = []
        dInfo = self.GetDataMD().GetMdData('m_dReturnRewardInfo', { })
        tLvInfo = ((35, 60015), (45, 60017), (50, 60020))
        for iLv, iID in tLvInfo:
            lInfo.append({
                'iLv': iLv,
                'dInfo': self.GetItemInfo(huodongreworditemdata.GetReword(sKey, iID)),
                'iCanGet': dInfo.get(iID, 1),
                'bShowTips': False,
                'iID': iID })
        
        self.GetTbView().ReloadWithDiffSourceDict(lInfo)

    
    def GetItemInfo(self, dReword):
        dItemList = []
        for iShape, tInfo in dReword.iteritems():
            dItemList.append([
                iShape,
                tInfo[0],
                tInfo[1],
                tInfo[2],
                tInfo[3]])
        
        dItemList.sort(key = (lambda x: x[3]))
        return dItemList

    
    def SetTimeText(self):
        iServerDay = misc.GetServerDay()
        iDayTime = 86400
        oLocTime = time.localtime(misc.GetServerTime() + (13 - iServerDay) * iDayTime)
        tEndTime = (oLocTime.tm_year, oLocTime.tm_mon, oLocTime.tm_mday, 8, 30, 0, 0, 0, 0)
        iListTime = time.mktime(tEndTime) - misc.GetServerTime()
        if iListTime < 0:
            sText = ''
        else:
            sText = '\xb3\xd1\xbel%s' % misc.Int2TimeStr(iListTime)
        self.GetObject('txt_time').SetText(sText)

    
    def GetTbView(self):
        return self.GetObject('tbview_list')

    
    def SetActive(self, bShow):
        self.SetShow(bShow)

    
    def VOpenPage(self, dExtend = None):
        pass

    
    def VClose(self):
        pass

    
    def OnEidtMessage(self, iMsgID):
        pass

    
    def OnMessage(self, iMsgID):
        self.OnEidtMessage(iMsgID)

    
    def OnChangeInfo(self, dData):
        self.ShowList()

    
    def OnClickGetItem(self, iID):
        nethdpresentcenter.C2GSBackManGiftBuyItem(iID)



class CTittleListPart(object):
    
    def __init__(self, oTbViewList, oClickCB):
        self.m_oTbViewList = oTbViewList
        self.m_oClickCB = misc.Functor(oClickCB)
        self.InitTbView()

    
    def InitTbView(self):
        '''
\t\t\xaa\xec\xa9l\xa4\xc6\xb4_\xa5\xce\xaa\xed\xae\xe6
\t\t'''
        self.m_oTbViewList.SetShowRowLine(False)
        self.m_oTbViewList.SetDelegateNewCellOfData(self.TbWeekDgtNewCellOfData)
        self.m_oTbViewList.SetDelegateUpdateCellOfData(self.TbWeekDgtUpdateCellOfData)
        self.m_oTbViewList.SetDelegateAlignOfData(self.TbWeekDgtAlignOfData)

    
    def GetTbAllView(self):
        '''
\t\t:rtype: tableview.CTableView
\t\t'''
        return self.m_oTbViewList

    
    def RefeashIconTittle(self, oIconTittle, oData):
        oIconTittle.SetLeftUpCB(self.m_oClickCB)
        oIconTittle.SetReturnForNewServerInfo(oData)

    
    def TbWeekDgtNewCellOfData(self, oContainer, oData):
        oReturnForNewServerItem = CReturnForNewServerItem(oContainer)
        self.RefeashIconTittle(oReturnForNewServerItem, oData)
        return oReturnForNewServerItem

    
    def TbWeekDgtUpdateCellOfData(self, oCell, oData, bReused):
        if bReused:
            self.RefeashIconTittle(oCell, oData)
        

    
    def TbWeekDgtAlignOfData(self, oData):
        return interface.ALIGN_CENTER_MIDDLE



class CReturnForNewServerItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/new_player_present/welfar/welfar_returngift_item.dlg')
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.m_oItemList = []
        self.m_oAni = None

    
    def SetGradeText(self, sText):
        self.GetObject('txt_grade').SetText('%s\xaf\xc5\xa5i\xbb\xe2\xa8\xfa' % str(sText))

    
    def SetBtnEnable(self, bEnable, sText):
        self.GetObject('btn_getreward').Enable(bEnable)
        self.GetObject('btn_getreward').SetText(sText)
        if bEnable:
            self.m_oAni = oAni = ui.CImage(self.GetObject('btn_getreward'), 'common/hint.igs', interface.UIPath)
            oAni.CreateCommand(2, 'animation')
            oAni.SetZ(1)
            (iW, iH) = self.GetObject('btn_getreward').GetSize()
            oAni.SetPos(iW / 2, iH / 2)
        else:
            self.m_oAni = None

    
    def SetLeftUpCB(self, oCB):
        self.m_oCB = oCB

    
    def SetReturnForNewServerInfo(self, dData):
        iGarde = dData.get('iLv', 0)
        self.m_iID = dData.get('iID', 0)
        self.SetGradeText(iGarde)
        None(self.SetBtnEnable, dData.get('iCanGet', 1) == 2 if dData.get('iCanGet', 1) != 3 else '\xa4w\xbb\xe2\xa8\xfa')
        dData.get('bShowTips', False)
        self.CreateItem(dData.get('dInfo', []))

    
    def CreateItem(self, dInfoList):
        self.m_oItemList = []
        for iShape, iCount, iKey, \xf8\xcf\xeesc, iIndex in enumerate(dInfoList):
            oParent = self.GetObject('img_buylist').GetImage(0, iPos)
            oItem = makeitemicon.CBackItem(oParent)
            oItem.CreateBackNeedItemIcon(iShape, iOwn = iCount, iNeed = 0, bFreeze = False)
            oItem.GetBackNeedItemIcon().SetKey(iKey)
            oItem.SetExtMsg(\xf8\xcf\xeesc)
            self.m_oItemList.append(oItem)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1 and self.m_oCB:
            self.m_oCB(self.m_iID)
        



class CReturnForNewServerIcon(activityiconbase.CActivityIconBase):
    
    def __init__(self, *args):
        activityiconbase.CActivityIconBase.__init__(self, *args)
        self.m_oMyRedPoint = None

    
    def OnServData(self, extData):
        if not self.ReadActiveState():
            self.SetBtnAni(True)
        

    
    def ReadActiveState(self):
        return hero.GetPrivateData('Game', 'clickreturnfornew')

    
    def SaveActiveState(self, bState):
        hero.SavePrivateData('Game', 'clickreturnfornew', bState)

    
    def OnClick(self):
        nethdpresentcenter.C2GSBackManGiftClickIcon()
        self.SaveActiveState(True)
        self.SetBtnAni(False)
