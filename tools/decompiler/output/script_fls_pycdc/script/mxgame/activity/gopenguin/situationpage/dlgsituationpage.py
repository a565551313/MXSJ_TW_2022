# pycdc 交叉复核产物 · script.fls entry 738
# co_filename(原始)='script/mxgame/activity/gopenguin/situationpage/dlgsituationpage.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_738.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/1/6 14:25
\xd7\xf7\xd5\xdf: jw
\xce\xc4\xbc\xfe: dlgsituation
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import combmacro
import gopenguinfine
import interface
import slot
import pagedlgbase
import timer
import ui

class CSituationPageDlg(combdialog.CCombDialog, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_OnClickVoteBtn = 'SS_OnClickVoteBtn(iTarget)'
    SS_OnClickChangeIdx = 'SS_OnClickChangeIdx(iType)'
    SS_OnClickIdxListBox = 'SS_OnClickIdxListBox(iIdx)'
    sUIName = 'dialog/activity/leijisi/leijisi_page1.dlg'
    dPatModelUI = {
        1: {
            'Parent': 'loc_icon1',
            'Dialog': 'text_talk1',
            'DialogBg': 'img_talk1',
            'VoteRatio': 'txt_grade',
            'Vote': 'text_zhichi1',
            'VoteBg': 'frame_zhichi_1',
            'Name': 'text_shenshou1' },
        2: {
            'Parent': 'loc_icon2',
            'Dialog': 'text_talk2',
            'DialogBg': 'img_talk2',
            'VoteRatio': 'txt_grade2',
            'Vote': 'text_zhichi2',
            'VoteBg': 'frame_zhichi_2',
            'Name': 'text_shenshou2' },
        3: {
            'Parent': 'loc_icon3',
            'Dialog': 'text_talk3',
            'DialogBg': 'img_talk3',
            'VoteRatio': 'txt_grade3',
            'Vote': 'text_zhichi3',
            'VoteBg': 'frame_zhichi_3',
            'Name': 'text_shenshou3' } }
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        pagedlgbase.COnePageDlgBase.__init__(self)
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_DelegateList = []
        self.m_dPetRole = { }
        self.m_dBubble = { }
        self.m_iNormalColor = self.GetObject('txt_grade').GetColor()
        self.m_iMaxColor = 16711680
        self.m_oListBox = None
        self.m_oTimer = None
        self.InitDlg()
        self.InitDelegate()

    
    def InitDlg(self):
        oText = self.GetObject('text_title')
        oText.SetShow(False)
        self.m_oListBox = combmacro.CLISTBOX(interface.CListBox, 'loc_SortType', self, oText.GetColor(), oText.GetFont())
        self.m_oListBox.SetReadOnly(True)
        self.m_oListBox.SetItemProp(2, 16, 90)
        self.m_oListBox.SetTextAlign(interface.ALIGN_CENTER_MIDDLE)
        self.m_oListBox.SetListBoxChangeCB(self.OnListBoxItmeClick)
        for dData in self.dPatModelUI.itervalues():
            self.GetObject(dData.get('Dialog')).SetText('')
        

    
    def Hold(self):
        pass

    
    def InitDelegate(self):
        import dgtsituationpege
        self.m_DelegateList = [
            dgtsituationpege.CSituationPageDgt(self)]

    
    def OnListBoxItmeClick(self):
        self.ssEmit(self.SS_OnClickIdxListBox, self.m_oListBox.GetSelected())

    
    def UpdateListBox(self, lItmes):
        self.m_oListBox.Reset()
        for sItem in lItmes:
            self.m_oListBox.AddTextItem(sItem)
        

    
    def UpdatePetData(self, dPetData):
        for idx, dData in dPetData.iteritems():
            dUIData = self.dPatModelUI.get(idx)
            if not dUIData:
                continue
            
            oVote = self.GetObject(dUIData.get('Vote'))
            iVote = dData.get(gopenguinfine.KEY_VOTE)
            oVote.SetShow(bool(iVote))
            oVote.SetText('\xa4w\xa4\xe4\xab\xf9\xa1G%s\xb2\xbc' % iVote)
            self.SetShowObject(dUIData['VoteBg'], bool(iVote))
            oVoteRatio = self.GetObject(dUIData.get('VoteRatio'))
            oVoteRatio.SetText('%d%%' % dData.get(gopenguinfine.KEY_VOREROTIO, 0))
            if dData.get(gopenguinfine.KEY_RAD):
                iColor = self.m_iMaxColor
            else:
                iColor = self.m_iNormalColor
            oVoteRatio.SetColor(iColor)
        

    
    def UpdatePetModel(self, dPetMode):
        '''
\t\t:type dPetMode: dict
\t\t'''
        import wrapinterface
        for iIdx, dData in dPetMode.iteritems():
            dUIData = self.dPatModelUI.get(iIdx)
            if not dUIData:
                continue
            
            oPerent = self.GetObject(dUIData.get('Parent'))
            iShape = dData.get(gopenguinfine.KEY_SHAPE)
            dDesc = dData.get(gopenguinfine.KEY_DESC)
            oPetRole = self.m_dPetRole.get(iIdx)
            if oPetRole and oPetRole.GetDesc() == dDesc and oPetRole.GetPhoto().GetShape() == iShape:
                continue
            
            oPetRole = wrapinterface.CPetAni(oPerent, dData.get(gopenguinfine.KEY_SHAPE, 0), dData.get(gopenguinfine.KEY_DESC, { }))
            oPetRole.ReleaseRandomAni()
            oText = self.GetObject(dUIData.get('Name'))
            oText.SetText(dData.get(gopenguinfine.KEY_NAME))
            self.m_dPetRole[iIdx] = oPetRole
        
        self.CreateRandomAni()

    
    def UpdatePetDialogue(self, iIdx, sText = '', bShow = True):
        dUIData = self.dPatModelUI.get(iIdx)
        if not dUIData:
            return None
        
        oText = self.GetObject(dUIData.get('Dialog'))
        oText.SetShow(bShow)
        if bShow:
            self.SetBubble(iIdx, sText, oText, oText.GetFont(), oText.GetColor())
        

    
    def SetBubble(self, sKey, sText, oParent, iFont, iColor):
        import gopenguininterface
        oBubble = gopenguininterface.CBubbleBox(oParent, iFont, iColor)
        interface.Center(oBubble)
        oBubble.CreateBubble(0, sText)
        self.m_dBubble[sKey] = oBubble

    
    def CreateRandomAni(self):
        self.RandomAni()
        self.ClearTimer()
        self.m_oTimer = timer.Timer(3, self.RandomAni, -1, self)

    
    def ClearTimer(self):
        if self.m_oTimer:
            pass
        self.m_oTimer.Release()

    
    def RandomAni(self):
        import random
        for oPetRole in self.m_dPetRole.itervalues():
            if not oPetRole:
                continue
            
            oPetRole.SetState(random.choice([
                'stand',
                'walk']))
        

    
    def UpdateCurIdx(self, sText):
        self.m_oListBox.SetText('%s\xb3\xf5\xa6\xb8' % sText)

    
    def UpdateCurVote(self, sText):
        self.GetObject('text_ticketnum').SetText(str(sText))

    
    def UpdateCurScore(self, sText):
        self.GetObject('text_gradenum').SetText(str(sText))

    
    def UpdateUnFinalVote(self, sText):
        None(None, None, self)('text_surplus1').SetText(str(sText))

    
    def VOpenPage(self, dExtend = None):
        self.SetShow(True)
        self.ssEmit(self.SS_OpenDlg, dExtend)

    
    def VClose(self):
        self.SetShow(False)
        self.ClearTimer()

    
    def OnMessage(self, iMsgID):
        if iMsgID in (1, 2, 3):
            self.ssEmit(self.SS_OnClickVoteBtn, iMsgID)
        elif iMsgID in (4, 5):
            self.ssEmit(self.SS_OnClickChangeIdx, [
                4,
                5].index(iMsgID))
