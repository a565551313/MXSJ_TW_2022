# pycdc 交叉复核产物 · script.fls entry 301
# co_filename(原始)='script/mxgame/activity/annualbeauty/view/beautycontestblog/bloglistview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_301.pyc (Python 2.5)

import combdialog
import interface
import slot
import blogitemcom
import ui
import wraptextobj
import usermacro
import dialoguecommondata

class CBloglist(combdialog.CCombSubWnd, slot.ISignalSubject):
    
    def __init__(self, parent, sDispatcherName):
        combdialog.CCombSubWnd.__init__(self, parent, 'dialog4/annualbeautycontest/fusaiflyer/bloglist.dlg')
        self.m_IsIgnoreEsc = False
        self.ssInit()
        self.m_sDispatcherName = sDispatcherName
        self.InitData()
        self.InitView()

    
    def InitData(self):
        self.m_dWbIDList = []
        self.m_dWbContents = None
        self.m_dReplyWbIDList = []
        self.m_dReplyWbContents = None
        self.m_oCutListUI = None
        self.m_ReportListUI = None
        self.m_textCloseReport = None
        self.m_dCurReportWbData = None
        self.m_MainReportUI = None
        self.m_MainReportCutList = None
        self.m_oReplyEdit = None
        self.m_dReplyParentWbData = None

    
    def InitView(self):
        oContent = self.GetObject('loc_cutList')
        (iW, iH) = oContent.GetSize()
        oList = ui.CCutList(oContent, iW, iH, sBarStyle = 'SCROLL_STYLE_4')
        oList.SetMouseWheelSpeed(20)
        oList.SetBarShow(False)
        oList.ClearItem()
        self.m_oCutListUI = oList
        (x, y, w, h) = self.GetLocData('edt_input')
        self.m_oReplyEdit = interface.CEdit(self, 4210829, interface.FontLT14, x, y, w, h)
        oText = self.GetObject('text_closeReportInput')
        (iX, iY) = oText.GetPos()
        iColor = oText.GetColor()
        \x8c\xa3\x8a\x8bt = oText.GetFont()
        sDesc = oText.GetText()
        oText.SetShow(False)
        self.m_textCloseReport = wraptextobj.CUnderLineClickText(self, iX, iY, sDesc, iColor, 16711680, \x8c\xa3\x8a\x8bt, msgid = 10)
        self.CreateReportComponents()
        self.ShowReportComponents(False)

    
    def CreateReportComponents(self, tLocation = None):
        if tLocation is None:
            (x, y, w, h) = self.GetLocData('loc_reportCutList')
        else:
            (x, y, w, h) = tLocation
        self.m_ReportListUI = ui.CCutList(self, w, h, bBarInPanel = True, sBarStyle = 'SCROLL_STYLE_4')
        self.m_ReportListUI.SetPos(x, y)
        self.m_ReportListUI.SetMouseWheelSpeed(20)
        self.m_ReportListUI.SetBarShow(False)

    
    def ShowReportComponents(self, bShow):
        '''\xa6^\xb4_\xad\xb6\xad\xb1'''
        if self.m_oReplyEdit:
            pass
        self.m_oReplyEdit.SetShow(bShow)
        if self.m_MainReportUI:
            pass
        self.m_MainReportUI.SetShow(bShow)
        if self.m_MainReportCutList:
            pass
        self.m_MainReportCutList.SetShow(bShow)
        if self.m_ReportListUI:
            pass
        self.m_ReportListUI.SetShow(bShow)
        if self.m_textCloseReport:
            pass
        self.m_textCloseReport.SetShow(bShow)
        self.GetObject('frame_reportBg').SetShow(bShow)
        self.GetObject('frame_inputBg').SetShow(bShow)
        self.GetObject('btn_Emote').SetShow(bShow)
        self.GetObject('btn_fabu').SetShow(bShow)
        if self.m_oCutListUI:
            pass
        self.m_oCutListUI.SetShow(not bShow)

    
    def UpdateDate(self, dData, isMe = False, dReportWb = None):
        '''
\t\t:param dData: \xb7L\xb3\xd5\xa6C\xaa\xed
\t\t:param isMe: \xacO\xa7_\xacO\xa6\xdb\xa4v
\t\t:param dReportWb: \xb7\xed\xabe\xa6^\xb4_\xaa\xba\xb7L\xb3\xd5
\t\t'''
        LOG_DEBUG('\xbc\xc6\xbe\xda', dData)
        LOG_DEBUG('isMe', isMe)
        LOG_DEBUG('\xa6^\xbd\xc6\xbc\xc6\xbe\xda', dReportWb)
        if not dData:
            self.m_dCurReportWbData = None
            self.m_dReplyParentWbData = None
            self.ShowReportComponents(False)
            if self.m_oCutListUI:
                pass
            self.m_oCutListUI.SetShow(False)
            return None
        
        if dReportWb:
            self.RefreshReplyPanel(dData, isMe, dReportWb)
        else:
            self.RefreshBlogPanel(dData, isMe)

    
    def RefreshBlogPanel(self, dData, isMe):
        self.ShowReportComponents(False)
        self.m_dWbIDList = dData.get('itemlist', [])
        self.m_dWbContents = dData.get('dWbcontent')
        self.m_oCutListUI.ClearItem()
        for dwbid in self.m_dWbIDList:
            iWbID = int(dwbid['wbid'])
            dWbData = self.m_dWbContents[iWbID]
            oItem = blogitemcom.CBlogItemCom(self.m_oCutListUI, self.m_sDispatcherName)
            oItem.SetBlogItemData(1, iWbID, dWbData, isMe)
            self.m_oCutListUI.AddItem(oItem)
        
        self.m_oCutListUI.Refresh()
        self.m_oCutListUI.SetShow(True)

    
    def RefreshReplyPanel(self, dData, isMe, dReportWb):
        import blogitemreport
        import hero
        self.m_dCurReportWbData = dReportWb
        self.m_dReplyParentWbData = dReportWb
        (x, y, w, h) = self.GetLocData('loc_reportedBlog')
        self.m_MainReportCutList = ui.CCutPanel(self, w, h, 'SCROLL_STYLE_4', True)
        self.m_MainReportCutList.SetPos(x, y)
        self.m_MainReportUI = blogitemreport.CBlogItemReport(self.m_MainReportCutList, self.m_sDispatcherName)
        self.m_MainReportUI.SetData(dReportWb)
        self.m_MainReportCutList.AddItem(self.m_MainReportUI)
        self.ShowReportComponents(True)
        self.m_oReplyEdit.SetDefaultTips('\xa6^\xb4_:%s' % dReportWb['nick'])
        self.m_dReplyWbIDList = dData.get('itemlist', [])
        self.m_dReplyWbContents = dData.get('dWbcontent')
        self.CreateReportComponents(None)
        for dwbid in self.m_dReplyWbIDList:
            iWbID = int(dwbid['wbid'])
            dWbData = self.m_dReplyWbContents[iWbID]
            oItem = blogitemcom.CBlogItemCom(self.m_ReportListUI, self.m_sDispatcherName)
            if not hero.GetRealID() == dWbData['gameid']:
                pass
            oItem.SetBlogItemData(2, iWbID, dWbData, hero.GetRealID() == dReportWb['gameid'])
            self.m_ReportListUI.AddItem(oItem)
            for dChildWbID in dwbid.get('childrenitems', []):
                iChildWbID = int(dChildWbID['wbid'])
                dReplyWbData = self.m_dReplyWbContents[iChildWbID]
                oItem = blogitemcom.CBlogItemCom(self.m_ReportListUI, self.m_sDispatcherName)
                if not hero.GetRealID() == dReplyWbData['gameid']:
                    pass
                oItem.SetBlogItemData(2, iChildWbID, dReplyWbData, hero.GetRealID() == dReportWb['gameid'], dWbData)
                self.m_ReportListUI.AddItem(oItem)
            
        
        self.m_ReportListUI.Refresh()
        self.m_ReportListUI.SetShow(True)

    
    def SetReportObj(self, dWbData):
        self.m_dCurReportWbData = dWbData
        self.m_oReplyEdit.SetText('')
        self.m_oReplyEdit.SetDefaultTips('\xa6^\xb4_:%s' % dWbData['nick'])

    
    def UpdateItemZan(self, iWbId, iPoint):
        bSucceed = False
        if self.m_ReportListUI:
            for oItem in self.m_ReportListUI.GetItems():
                if iWbId == oItem.GetWbID():
                    oItem.AddZan()
                    bSucceed = True
                    continue
            
        
        if self.m_MainReportUI:
            if iWbId == self.m_MainReportUI.GetWbID() or bSucceed:
                self.m_MainReportUI.AddZan()
            
        
        if self.m_oCutListUI:
            for oItem in self.m_oCutListUI.GetItems():
                if iWbId == oItem.GetWbID():
                    oItem.AddZan()
                    continue
            
        

    
    def UpdateReplyObj(self, sServId, iPid, iWbId):
        if iWbId in self.m_dReplyWbContents:
            self.SetReportObj(self.m_dReplyWbContents[iWbId])
        elif iWbId in self.m_dWbContents:
            self.SetReportObj(self.m_dWbContents[iWbId])
        

    
    def DelBlogById(self, iWbid):
        if self.m_MainReportUI:
            if self.m_MainReportUI.GetWbID() == iWbid and self.m_MainReportUI.GetShow():
                self.GoMainPage()
                return None
            
        
        if self.m_oCutListUI:
            iRlt = None
            for iIdx, oItem in enumerate(self.m_oCutListUI.GetItems()):
                if iWbid == oItem.GetWbID():
                    iRlt = iIdx
                    continue
            
            if iRlt is not None:
                oItem = self.m_oCutListUI.GetItemByIdx(iRlt)
                if oItem:
                    pass
                self.m_oCutListUI.RemoveItem(oItem)
            
        
        if self.m_ReportListUI:
            iRlt = None
            for iIdx, oItem in enumerate(self.m_ReportListUI.GetItems()):
                if iWbid == oItem.GetWbID():
                    iRlt = iIdx
                    continue
            
            if iRlt is not None:
                oItem = self.m_ReportListUI.GetItemByIdx(iRlt)
                if oItem:
                    pass
                self.m_ReportListUI.RemoveItem(oItem)
            
        

    
    def GoMainPage(self):
        import bloginteractiondispatcher
        oDispatcher = bloginteractiondispatcher.GetInstance(self.m_sDispatcherName)
        oDispatcher.ssEmit(bloginteractiondispatcher.SS_RefreshBlog)

    
    def OnHideComment(self):
        self.GoMainPage()

    
    def OnAddEmotion(self):
        import dlgbaozi
        dlgbaozi.ShowBaoziAndBubble()
        oBtn = self.GetObject('btn_Emote')
        if hasattr(oBtn, 'ReleaseLastEmoteDlg'):
            self.GetObject('btn_Emote').ReleaseLastEmoteDlg()
        

    
    def OnSendRely(self):
        import hero
        import httpannualbeautycontest
        import misc
        import fusaidefine
        import banword
        if not self.m_dCurReportWbData:
            return None
        
        sStr = self.m_oReplyEdit.GetText()
        if not sStr:
            return None
        
        if not banword.IsValidChat(sStr)[0] or banword.BadWholeWord(sStr):
            usermacro.PROMPT_MSG(dialoguecommondata.GetDialogue('beautycontest', 1003))
            return None
        
        import accountfriend
        httpannualbeautycontest.SendBlog(misc.Functor(self.CallBackSendBlog), misc.GetServerID(), hero.GetHeroID(), hero.GetHeroName(), fusaidefine. 7">+_PLAYER_BLOG, self.m_dCurReportWbData['wbid'], fusaidefine.ACTIVITY_ID, sStr, '', '', accountfriend.GetHeroAttr('accountID'))

    
    def CallBackSendBlog(self, data, bSucceed, *args):
        import httpplayershow
        import usermacro
        data = httpplayershow.Parse(data, bSucceed)
        if not bSucceed:
            usermacro.PROMPT_MSG('\xb5o\xa7G\xa5\xa2\xb1\xd1')
            return None
        
        iCode = data.get('Code')
        if iCode:
            sMsg = data.get('Message', '\xa5\xa2\xb1\xd1')
            usermacro.PROMPT_MSG(sMsg)
            return None
        
        usermacro.PROMPT_MSG('\xa6^\xb4_\xa6\xa8\xa5\\')
        self.m_oReplyEdit.Clear()
        self.RefreshReplyBlog()

    
    def RefreshReplyBlog(self):
        if not self.m_dReplyParentWbData:
            return None
        
        import bloginteractiondispatcher
        oDispatcher = bloginteractiondispatcher.GetInstance(self.m_sDispatcherName)
        oDispatcher.ssEmit(bloginteractiondispatcher.SS_RefreshReply, self.m_dReplyParentWbData['gameid'], self.m_dReplyParentWbData['serverid'], self.m_dReplyParentWbData['wbid'])

    
    def OnMessage(self, iMsgID):
        if iMsgID == 10:
            self.OnHideComment()
        elif iMsgID == 3:
            self.OnSendRely()
        elif iMsgID == 4:
            self.OnAddEmotion()
