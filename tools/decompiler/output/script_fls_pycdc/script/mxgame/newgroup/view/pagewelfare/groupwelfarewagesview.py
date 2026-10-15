# pycdc 交叉复核产物 · script.fls entry 4616
# co_filename(原始)='script/mxgame/newgroup/view/pagewelfare/groupwelfarewagesview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4616.pyc (Python 2.5)

import misc
import grouppagebase
import combdialog
import delegategroupwelfarewages
import boxwidget
import group
import interface
import delegatesysloadlogic
import hero
import pagedlgbase
import groupdefines

class CGroupWelfareWagesView(grouppagebase.CGroupPageBase, combdialog.CCombSubWnd, pagedlgbase.COnePageDlgBase):
    
    def __init__(self, pContext, pMainDlg):
        self.sUIName = 'dialog/group_new/group_fuli/group_wages.dlg'
        grouppagebase.CGroupPageBase.__init__(self, pContext, pMainDlg)
        combdialog.CCombSubWnd.__init__(self, pMainDlg)
        self.m_pDelegate = None
        self.m_pSysLoadDelegate = None
        self.m_oTable = self.GetObject('tab_member')
        self.m_oTableItemFont = self.GetObject('text_tangzhu').GetFont()
        self.m_oHotArea = None
        self.m_tPlayerInfoList = None
        self.m_oTips = None
        self.InitDelegate(pContext)
        self.InitHotArea()

    
    def InitShowLogic(self):
        import showlogic_welfarewages
        self.m_oShowLogic = showlogic_welfarewages.CShowLogicWelfareWages(self)

    
    def InitDelegate(self, pContext):
        self.m_pDelegate = delegategroupwelfarewages.CDelegateGroupWelfareWages(self, pContext)
        self.m_pSysLoadDelegate = delegatesysloadlogic.CDelegateSysLoadLogic()

    
    def VOpenPage(self, dExtend = None):
        self.m_pDelegate.OnOpenPage(dExtend)

    
    def VClose(self):
        self.m_pSysLoadDelegate.Clear()
        self.m_pDelegate.OnClose()

    
    def InitHotArea(self):
        oPar = self.GetObject('text_devote')
        (w, h) = oPar.GetSize()
        self.m_oHotArea = boxwidget.CHotBox(oPar, w, h, 0)
        pEnterCallBack = misc.Functor(self.OnHotEnter)
        pLeaveCallBack = misc.Functor(self.OnHotLeave)
        self.m_oHotArea.SetEnterCB(pEnterCallBack)
        self.m_oHotArea.SetLeaveCB(pLeaveCallBack)

    
    def RefreshTable(self, lPlayerInfo, iThisWeekMoney, iLastWeekMoney, tPlayerInfoList):
        self.m_oTable.Clear()
        self.m_tPlayerInfoList = tPlayerInfoList
        for iIndex, dInfo in enumerate(lPlayerInfo):
            oBox = self.m_oTable.AddBoxItem()
            oItemList = []
            sName = dInfo['name']
            iGrade = dInfo.get('grade', 100)
            iClass = dInfo.get('cls', 1)
            sClass = hero.id2class(iClass)
            sGradeText = '%d\xaf\xc5%s' % (iGrade, sClass)
            iID = dInfo.get('pid')
            bangGong = dInfo.get('offermax', 0)
            iAffair = dInfo['affair']
            sAffair = group.lv2txt(iAffair)
            iGold = dInfo['gold']
            iBanGon = dInfo['banggon']
            while None:
                for sTxt in (sGradeText, sAffair, str, bangGong, str(iBanGon), str(iGold)):
                    oItem = interface.CTextObject(oBox, sTxt, self.m_oTableItemFont, interface.COLOR_1)
                    oItemList.append(oItem)
                dAlignInfo = { }
                dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
                dAlignInfo['tOffset'] = (0, 0)
                self.m_oTable.AlignItem(oItemList[0], 0, interface.ALIGN_LEFT_MIDDLE, (45, 0))
                if iID:
                    wrItem = misc.WeakRef(oItemList[0])
                    if iIndex > groupdefines.E_AVATAR_NOFRAMELOAD_NUM:
                        pFunc = misc.Functor(self.LoadAvatar, wrItem, iID)
                        self.m_pSysLoadDelegate.Add2Queue(pFunc)
                    else:
                        self.LoadAvatar(wrItem, iID)
            iIndex > groupdefines.E_AVATAR_NOFRAMELOAD_NUM
        
        self.m_oTable.ResetItems()
        self.m_oTable.ResetScrollBar()
        self.RefreshAllMoney(iThisWeekMoney, iLastWeekMoney)

    
    def LoadAvatar(self, wrItem, iId):
        import grouppagefactory
        oItem = wrItem()
        if not oItem:
            return False
        
        pParent = oItem
        oItem.m_oAvatar = grouppagefactory.CreateAvatar(pParent, iId, {
            'offx': 5,
            'type': 'groupwage' })

    
    def RefreshAllMoney(self, iThisWeekMoney, iLastWeekMoney):
        iExraMoney = 0
        if self.m_tPlayerInfoList:
            for sName, iMoney in self.m_tPlayerInfoList:
                iExraMoney += iMoney
            
        
        sTxt = str(iThisWeekMoney)
        if iExraMoney:
            sTxt += ' + %d' % iExraMoney
        
        self.GetObject('text_devote').SetText(sTxt)

    
    def RefreshTanZhuEliteInfo(self, iTanZhuBanGon, iTanZhuGold, iEliteBanGon, iEliteGold):
        self.GetObject('text_tangzhu_03').SetText(str(iTanZhuBanGon))
        self.GetObject('text_tangzhu_04').SetText(str(iTanZhuGold))
        self.GetObject('text_jingying_03').SetText(str(iEliteBanGon))
        self.GetObject('text_jingying_04').SetText(str(iEliteGold))

    
    def OnHotEnter(self):
        import wrapinterface
        sTxt = ''
        if self.m_tPlayerInfoList:
            for sName, iMoney in enumerate(self.m_tPlayerInfoList):
                sTxt += '#G%s#n\xc3B\xa5~\xb5o\xa9\xf1\xa4F%d\xa4u\xb8\xea' % (sName, iMoney)
                if idx != len(self.m_tPlayerInfoList) - 1:
                    sTxt += '#r'
                    continue
            
        
        if not sTxt:
            return None
        
        self.m_oTips = wrapinterface.CTextTips(self, -1, sTxt, interface.FontLT14_3, direct = 1)

    
    def OnHotLeave(self):
        self.m_oTips = None

    
    def OnMessage(self, iMsgID):
        if iMsgID == 5:
            self.m_pDelegate.OnWages2Group()
