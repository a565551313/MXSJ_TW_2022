# pycdc 交叉复核产物 · script.fls entry 1955
# co_filename(原始)='script/mxgame/activity/annualbeauty/view/beautycontestblog/fusairecommendcontent.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1955.pyc (Python 2.5)

import annualbeautydefine
import blogitem
import combdialog
import dgtfusaibloglist
import dgtrecommandcontent
import friend
import fusaicontentbase
import hero
import interface
import misc
import serverdata
import slot

def GetTabColor(iPid, sGName):
    import hero
    sMyGName = hero.GetProp('sOrg')
    if iPid == hero.g_ID:
        color = interface.COLOR_169
    elif (friend.IsFriend(iPid, 0) or sMyGName) and sGName and sMyGName == sGName:
        color = interface.COLOR_58
    else:
        color = None
    return color


class CRecoommandBlogItem(blogitem.CBlogItem):
    
    def __init__(self, parent, sDispatcherName):
        blogitem.CBlogItem.__init__(self, parent, sDispatcherName)
        self.m_CallBackFunc = None

    
    def SetCallBack(self, oFunc):
        self.m_CallBackFunc = oFunc

    
    def OnClickReviewBtn(self):
        '''\xc2\xd0\xbb\\\xb1\xbc\xb3o\xad\xd3\xa4\xe8\xaak'''
        if callable(self.m_CallBackFunc):
            self.m_CallBackFunc()
        

    
    def OnClickZanBtn(self):
        '''\xc2\xd0\xbb\\\xb1\xbc\xb3o\xad\xd3\xa4\xe8\xaak'''
        if callable(self.m_CallBackFunc):
            self.m_CallBackFunc()
        



class CRecommandContent(combdialog.CCombSubWnd, slot.ISignalSubject, fusaicontentbase.CFusaiContentBase):
    SS_ReqRecommandInfo = 'SS_ReqRecommandInfo()'
    SS_OnGotoMainPage = 'SS_OnGotoMainPage(dFlyerInfo)'
    SS_OpenBidding = 'SS_OpenBidding(iPid, iServid)'
    SS_FlyerIconChange = 'SS_FlyerIconChange'
    SS_NextPic = 'SS_NextPic'
    SS_PerPic = 'SS_PerPic'
    
    def __init__(self, oParent, sDispatcherName):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/annualbeautycontest/fusaiflyer/recommendpanel.dlg')
        oTb = self.GetObject('tab_preview_data')
        oTb.InitStyle('TABLE_BEAUTY')
        self.ssInit()
        self.m_IsIgnoreEsc = True
        self.InitData(sDispatcherName)
        self.InitView()
        self.InitDelegate()

    
    def InitData(self, sDispatcherName):
        self.m_sDispatcherName = sDispatcherName
        self.m_oRecommendList = []
        self.m_dFlyerInfo = { }
        self.m_iPid = 0
        self.m_iServerId = 0
        self.m_oPic = None
        self.m_tClickInfo = None
        self.m_dContributeList = []

    
    def InitView(self):
        self.m_blogitem = None
        (iX1, iY1) = self.GetObject('loc_Text1').GetPos()
        self.m_oDelTxt = interface.CClickRichText(self, iX1, iY1, 160, '#u\xb6i\xa4J\xa5D\xad\xb6', 8995744, 2645120, interface.FontLT14, msgid = 10)

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtrecommandcontent.CDgtRecommandContent(self, self.m_sDispatcherName),
            dgtfusaibloglist.CDgtFlyerIconItem(self)]

    
    def ResetView(self):
        self.ssEmit(self.SS_ReqRecommandInfo)

    
    def GetContributeInfo(self, iPid, iServId):
        for dInfo in self.m_dContributeList:
            if int(dInfo.get('iPartServID', 0)) == iServId and int(dInfo.get('iPartPid', 0)) == iPid:
                return dInfo
                continue
        

    
    def SetShowAuctionBtn(self, bShow):
        self.GetObject('btn_auction').SetShow(bShow)

    
    def CreateRecoommandBlogItem(self):
        import ui
        (x, y, w, h) = self.GetLocData('loc_blogPos')
        self.m_oCutPanel = ui.CCutPanel(self, w, h, 'SCROLL_STYLE_4', True)
        del ui
        None.m_oCutPanel.SetPos(x, y)
        self.m_blogitem = CRecoommandBlogItem(self.m_oCutPanel, self.m_sDispatcherName)
        self.m_blogitem.SetCallBack(misc.Functor(self.ConfirmGoToMainPage))
        self.m_oCutPanel.AddItem(self.m_blogitem)
        self.m_oCutPanel.SetBarShow(False)

    
    def ConfirmGoToMainPage(self):
        
        def Go(obj):
            self.OnChangeMainPage()

        import commondialog
        commondialog.ShowMessageBox('\xacO\xa7_\xa5\xb4\xb6}\xaa\xb1\xaea\xa5D\xad\xb6\xa1H', ('\xbdT\xbb{', '\xa8\xfa\xae\xf8'), (Go, None))

    
    def GetID(self):
        return self.m_iPid

    
    def GetServerID(self):
        return self.m_iServerId

    
    def CreatePic(self, sPath):
        if sPath is None:
            self.m_oPic = None
        else:
            oLocPhoto = self.GetObject('loc_Phot1')
            self.m_oPic = interface.CStretchBitmapObject(self, sPath)
            self.m_oPic.SetSize(*oLocPhoto.GetSize())
            interface.AlignObjects(self.m_oPic, oLocPhoto, interface.ALIGN_CENTER_MIDDLE)

    
    def GetPicLeftBtn(self):
        pass

    
    def GetPicRightBtn(self):
        pass

    
    def ShowPanel(self, bReqServe, dFlyInfo):
        '''\xb1\xc0\xaf\xf2\xad\xb6\xaa\xba\xabH\xae\xa7\xa9MdFlyInfo\xa8S\xa4\xb0\xbb\xf2\xc3\xf6\xc1p\xa1AdFlyInfo\xacO\xb7\xed\xabe\xb6\xc7\xb3\xe6\xaa\xba\xaa\xb1\xaea\xabH\xae\xa7,\xb1\xc0\xaf\xf2\xad\xb6\xacO\xa5L\xa4H\xaa\xba\xabH\xae\xa7'''
        self.m_dFlyerInfo = dFlyInfo
        self.ResetView()
        self.SetShow(True)
        if bReqServe:
            self.ssEmit(self.SS_ReqRecommandInfo)
        

    
    def HidePanel(self):
        self.SetShow(False)

    
    def SetWebBlogData(self, dBlogData):
        dwbidlist = dBlogData.get('itemlist', [])
        dwbcontents = dBlogData.get('dWbcontent')
        if dwbidlist:
            self.CreateRecoommandBlogItem()
            self.m_blogitem.SetSelfBlog(False)
            self.m_blogitem.SetData(dwbidlist[0], dwbcontents[dwbidlist[0]['wbid']])
            self.m_oCutPanel.RefreshRealSize()
            self.m_oCutPanel.RefreshItemPos()
            self.SetShowObject('rtxt_noinfo', False)
        else:
            self.m_oCutPanel = None
            self.m_blogitem = None
            self.SetShowObject('rtxt_noinfo', True)

    
    def SetSysRecommendInfo(self, dSysRecommendInfo):
        dFlyerInfo = dSysRecommendInfo.get('flyerInfo')
        self.m_dFlyerInfo = dFlyerInfo
        self.m_iPid = dFlyerInfo[annualbeautydefine.KEY_PID]
        self.m_iServerId = dFlyerInfo[annualbeautydefine.KEY_SERVERID]
        self.m_oDelTxt.SetShow(True)
        self.GetObject('text_nickName').SetText(dFlyerInfo.get(annualbeautydefine.KEY_NAME, ''))
        self.GetObject('text_point').SetText(str(dFlyerInfo.get(annualbeautydefine.KEY_TICKET, '')))
        self.ssEmit(self.SS_FlyerIconChange)
        dContributeList = dSysRecommendInfo.get('dContributeList')
        self.m_dContributeList = dContributeList
        oTb = self.GetObject('tab_preview_data')
        oTb.Clear()
        iLen = len(dContributeList)
        for iIdx in xrange(iLen):
            dContribute = dContributeList[iIdx]
            sServName = serverdata.GetServerNameByID(dContribute.get('iServId'))
            sPartName = dContribute.get('sPartName')
            iPid = dContribute.get('iPid')
            color = GetTabColor(iPid, '')
            sName = dContribute.get('sName')
            sName = friend.GetShowName(iPid, sName)
            iContribution = dContribute.get('iContribution', 0)
            oItem = oTb.AddTextItem([
                '\xb2\xc4%s' % misc.NumToChinese(iIdx + 1),
                sPartName,
                sName,
                sServName,
                str(iContribution)], color)
            oItem.m_iPid = int(dContribute.get('iPartPid', 0))
            oItem.m_iServId = int(dContribute.get('iPartServID', 0))
        
        oTb.ResetItems()
        oTb.ResetScrollBar()

    
    def OnChangeMainPage(self):
        self.ssEmit(self.SS_OnGotoMainPage, self.m_dFlyerInfo)

    
    def OnGotoBidding(self):
        '''\xb0\xd1\xbbP\xc4v\xbb\xf9'''
        self.ssEmit(self.SS_OpenBidding, hero.GetHeroID(), misc.GetServerID())

    
    def ClickItem(self, iIdx):
        if self.m_tClickInfo is None:
            self.m_tClickInfo = (misc.Time(), iIdx)
            return None
        
        oItem = self.GetObject('tab_preview_data').GetItem(iIdx)
        if not oItem:
            return None
        
        iCurTime = misc.Time()
        if iCurTime - self.m_tClickInfo[0] < 0.3 and iIdx == self.m_tClickInfo[1]:
            self.m_tClickInfo = (iCurTime, iIdx)
            dInfo = self.GetContributeInfo(oItem.m_iPid, oItem.m_iServId)
            if not dInfo:
                return None
            
            dFlyerInfo = {
                annualbeautydefine.KEY_IDX: dInfo['iIdx'],
                annualbeautydefine.KEY_PID: dInfo['iPartPid'],
                annualbeautydefine.KEY_SERVERID: dInfo['iPartServID'],
                annualbeautydefine.KEY_NAME: dInfo['sPartName'],
                annualbeautydefine.REPORT_KEY_VOICEURL: dInfo['sVideoUrl'],
                annualbeautydefine.KEY_TICKET: dInfo['iTicket'] }
            self.ssEmit(self.SS_OnGotoMainPage, dFlyerInfo)
        else:
            self.m_tClickInfo = (iCurTime, iIdx)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 10:
            self.OnChangeMainPage()
        elif iMsgID == 35:
            self.OnGotoBidding()
        elif iMsgID < iMsgID:
            pass
        elif iMsgID < 500:
            self.ClickItem(iMsgID - 201)
