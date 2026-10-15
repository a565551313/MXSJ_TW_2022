# pycdc 交叉复核产物 · script.fls entry 4349
# co_filename(原始)='script/mxgame/activity/2018worldcup/dlgworldcup.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4349.pyc (Python 2.5)

import combdialog
import interface
import worldcupmgr
import ui
g_MatchInfoDlg = None
g_GuessDlg = None
g_VoteDlg = None
g_RankDlg = None
g_HistoryDlg = None
COUNTRY_DICT = {
    0: '\xabX\xc3\xb9\xb4\xb5',
    1: '\xa8F\xafS\xaa\xfc\xa9\xd4\xa7B',
    2: '\xaeJ\xa4\xce',
    3: '\xafQ\xa9\xd4\xa6c',
    4: '\xb8\xb2\xb5\xe5\xa4\xfa',
    5: '\xa6\xe8\xafZ\xa4\xfa',
    6: '\xbc\xaf\xac\xa5\xad\xf4',
    7: '\xa5\xec\xae\xd4',
    8: '\xaak\xb0\xea',
    9: '\xbfD\xa4j\xa7Q\xa8\xc8',
    10: '\xaf\xb5\xbe|',
    11: '\xa4\xa6\xb3\xc1',
    12: '\xaa\xfc\xae\xda\xa7\xca',
    13: '\xa6B\xaeq',
    14: '\xa7J\xc3\xb9\xa6a\xa8\xc8',
    15: '\xa5\xa7\xa4\xe9\xa7Q\xa8\xc8',
    16: '\xa4\xda\xa6\xe8',
    17: '\xb7\xe7\xa4h',
    18: '\xad\xf4\xb4\xb5\xb9F\xbe\xa4\xa5[',
    19: '\xb6\xeb\xba\xb8\xba\xfb\xa8\xc8',
    20: '\xbcw\xb0\xea',
    21: '\xbe\xa5\xa6\xe8\xad\xf4',
    22: '\xb7\xe7\xa8\xe5',
    23: '\xc1\xfa\xb0\xea',
    24: '\xa4\xf1\xa7Q\xae\xc9',
    25: '\xa4\xda\xae\xb3\xb0\xa8',
    26: '\xac\xf0\xa5\xa7\xb4\xb5',
    27: '\xad^\xae\xe6\xc4\xf5',
    28: '\xaai\xc4\xf5',
    29: '\xb6\xeb\xa4\xba\xa5[\xba\xb8',
    30: '\xad\xf4\xad\xdb\xa4\xf1\xa8\xc8',
    31: '\xa4\xe9\xa5\xbb' }

def ModuleReset():
    global g_MatchInfoDlg, g_GuessDlg, g_VoteDlg, g_RankDlg, g_HistoryDlg
    g_MatchInfoDlg = None
    g_GuessDlg = None
    g_VoteDlg = None
    g_RankDlg = None
    g_HistoryDlg = None


def OpenMatchInfoDlg():
    global g_MatchInfoDlg
    if not g_MatchInfoDlg:
        g_MatchInfoDlg = CMatchInfoDlg()
        return None
    
    if not g_MatchInfoDlg.GetShow():
        g_MatchInfoDlg.SetShow(True)
    


def OpenSupportTeamDlg(iType):
    global g_VoteDlg
    if not g_VoteDlg:
        g_VoteDlg = CVoteDlg(iType)
        return None
    
    if not g_VoteDlg.GetShow():
        g_VoteDlg.SetShow(True)
    


def OpenChampionTeamDlg(iType, lChampionRatio):
    global g_VoteDlg
    if not g_VoteDlg:
        g_VoteDlg = CVoteDlg(iType, lChampionRatio)
        return None
    
    if not g_VoteDlg.GetShow():
        g_VoteDlg.SetShow(True)
    
    if iType == 5 and g_VoteDlg:
        g_VoteDlg.RefreshRatio(lChampionRatio)
    


def OpenRankDlg():
    global g_RankDlg
    if not g_RankDlg:
        worldcupmgr.GetWorldCupMgr().RequestPlayerInfo()
        g_RankDlg = CRankDlg()
        return None
    
    if not g_RankDlg.GetShow():
        g_RankDlg.SetShow(True)
    


def ShowInfo(id, name, kind, coutry, ilv, arr):
    if g_RankDlg:
        g_RankDlg.ShowInfo(id, name, kind, coutry, ilv, arr)
    


class CMatchInfoDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog3/worldcup/saicheng.dlg')
        interface.Center(self)
        self.m_CurPage = 0
        self.m_oImageList = []
        self.m_iMatchIDList = []
        self.RefreshMatchInfo()
        self.RefreshBtn()

    
    def RefreshMatchInfo(self):
        dMatchInfoList = worldcupmgr.GetWorldCupMgr().GetMatchInfo()
        (iVoteTime, iWinRatio) = worldcupmgr.GetWorldCupMgr().GetGuessInfo()
        self.GetObject('txt_votetime').SetText('\xa7U\xab\xc2\xa6\xb8\xbc\xc6\xa1G%d' % iVoteTime)
        self.GetObject('txt_winratio').SetText('\xb3\xd3\xb2v\xa1G%.1f%%' % iWinRatio)
        if not dMatchInfoList:
            self.ClearAllMatch()
            return None
        
        for i in xrange(4):
            self.SetMatchShow(i, True)
        
        self.m_iMatchIDList = []
        self.m_oImageList = []
        self.ClearAllMatch()
        if len(dMatchInfoList) > 0:
            self.GetObject('txt_votetim1').SetShow(False)
        
        for index, dInfo in enumerate(dMatchInfoList[self.m_CurPage * 4:self.m_CurPage * 4 + 4]):
            self.SetMatchShow(index, True)
            sTime = GetStringTime(dInfo['iTime'])
            iIndex = sTime.find(' ')
            sTime = sTime[:iIndex] + '\n' + sTime[iIndex + 1:]
            self.GetObject('txt_time%d' % index).SetText(sTime)
            sCountryLeft = GetCountryName(dInfo['iCountryNum1'])
            sCountryRight = GetCountryName(dInfo['iCountryNum2'])
            self.GetObject('txt_country%d0' % index).SetText(sCountryLeft)
            self.GetObject('txt_country%d1' % index).SetText(sCountryRight)
            oImag = ui.CImage(self, 'combdialog/worldcup/duiqismall/%d.png' % dInfo['iCountryNum1'], interface.UIPath)
            (x, y) = self.GetObject('loc_country%d0' % index).GetPos()
            oImag.SetPos(x, y)
            self.m_oImageList.append(oImag)
            oImag = ui.CImage(self, 'combdialog/worldcup/duiqismall/%d.png' % dInfo['iCountryNum2'], interface.UIPath)
            (x, y) = self.GetObject('loc_country%d1' % index).GetPos()
            oImag.SetPos(x, y)
            self.m_oImageList.append(oImag)
            iMatchID = dInfo['iMatchID']
            self.m_iMatchIDList.append(iMatchID)
            if index == 0:
                sRoundInfo = GetMatchState(dInfo['iRoundInfo'])
                self.GetObject('txt_round').SetText(sRoundInfo)
            
            if not dInfo['iCanGuess']:
                self.GetObject('btn_cheer%d' % index).FakeEnable(False, '\xa5\xd8\xabe\xa4\xa3\xa5i\xa7U\xab\xc2\xa1G\xb1N\xa9\xf3\xa9\xfa\xa4\xe918\xae\xc9\xb6}\xb1\xd2\xa7U\xab\xc2\xa9\xce\xa4\xf1\xc1\xc9\xa4w\xb6}\xa9l')
                continue
            self.GetObject('btn_cheer%d' % index).FakeEnable(True)
        

    
    def RefreshBtn(self):
        dMatchList = worldcupmgr.GetWorldCupMgr().GetMatchInfo()
        if self.m_CurPage * 4 + 4 >= len(dMatchList):
            self.GetObject('btn_nextpage').Enable(False)
        else:
            self.GetObject('btn_nextpage').Enable(True)
        if self.m_CurPage == 0:
            self.GetObject('btn_prepage').Enable(False)
        else:
            self.GetObject('btn_prepage').Enable(True)

    
    def SetMatchShow(self, iIndex, bShow):
        self.GetObject('img_bg%d' % iIndex).SetShow(bShow)
        self.GetObject('txt_time%d' % iIndex).SetShow(bShow)
        self.GetObject('loc_country%d0' % iIndex).SetShow(bShow)
        self.GetObject('loc_country%d1' % iIndex).SetShow(bShow)
        self.GetObject('txt_country%d0' % iIndex).SetShow(bShow)
        self.GetObject('txt_country%d1' % iIndex).SetShow(bShow)
        self.GetObject('btn_cheer%d' % iIndex).SetShow(bShow)

    
    def ClearAllMatch(self):
        for iIndex in xrange(4):
            self.SetMatchShow(iIndex, False)
        

    
    def OpenGuessDlg(self, id):
        global g_GuessDlg
        dMatchList = worldcupmgr.GetWorldCupMgr().GetMatchInfo()
        if not dMatchList:
            return None
        
        dInfo = dMatchList[self.m_CurPage * 4 + id - 1]
        iMatch = dInfo['iMatchID']
        iNumberLeft = dInfo['iCountryNum1']
        iNumberRight = dInfo['iCountryNum2']
        iTime = dInfo['iTime']
        \xe4Round = dInfo['iRoundInfo']
        g_GuessDlg = CGuessDlg(iMatch, iNumberLeft, iNumberRight, iTime, \xe4Round)
        worldcupmgr.GetWorldCupMgr().OpenGuessDlg(iMatch)

    
    def OpenHistoryDlg(self):
        global g_HistoryDlg
        worldcupmgr.GetWorldCupMgr().RequestHistory()
        g_HistoryDlg = CHistoryDlg()

    
    def CloseWindow(self):
        global g_MatchInfoDlg
        g_MatchInfoDlg = None

    
    def OnMessage(self, msgid):
        if msgid in (1, 2, 3, 4):
            self.OpenGuessDlg(msgid)
        elif msgid == 5:
            self.m_CurPage -= 1
            self.RefreshMatchInfo()
            self.RefreshBtn()
        elif msgid == 6:
            self.m_CurPage += 1
            self.RefreshMatchInfo()
            self.RefreshBtn()
        elif msgid == 7:
            self.CloseWindow()
        elif msgid == 8:
            self.OpenHistoryDlg()
        



class CNumberEdit(ui.CNumberEdit):
    
    def __init__(self, parent, iColor, font, x, y, w, h, linecolor = 0, overstriking = False):
        ui.CNumberEdit.__init__(self, parent, iColor, font, x, y, w, h, linecolor, overstriking)
        self.m_iMaxNum = 0

    
    def SetCountryName(self, sName, sPos):
        self.m_sName = sName
        self.m_sPos = sPos

    
    def SetLeftUpCB(self, oFunc):
        self.m_oLeftUpCB = oFunc

    
    def SetMaxNum(self, iNum):
        self.m_iMaxNum = iNum

    
    def GetMaxNum(self):
        return self.m_iMaxNum

    
    def LeftUp(self):
        if interface.Hold and interface.Hold.Get() == self:
            interface.Hold = None
            self.Capture(0)
            self.IgnoreSonMessage(False)
            if self.m_oLeftUpCB:
                self.m_oLeftUpCB(self.m_sName, self.m_sPos)
            
        

    
    def AddChar(self, char):
        ui.CNumberEdit.AddChar(self, char)
        if char.isdigit():
            iNum = int(self.GetText())
            if iNum > self.m_iMaxNum:
                self.SetText(str(self.m_iMaxNum))
            
        



class CGuessDlg(combdialog.CCombDialog):
    
    def __init__(self, iMatch, iNumberLeft, iNumberRight, iTime, iRoundInfo):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog3/worldcup/zhuwei.dlg')
        interface.Center(self)
        self.m_iMatch = iMatch
        self.m_iNumberLeft = iNumberLeft
        self.m_iNumberRight = iNumberRight
        self.m_iLeftPoint = 0
        self.m_iRightPoint = 0
        self.m_iAllCash = 0
        self.m_oPointTips = None
        self.m_Clock = None
        self.m_bFisrtRefresh = True
        (self.m_iMinPoint, self.m_iMaxPoint) = GetMaxMinPoint(iRoundInfo)
        self.InitDlg(iNumberLeft, iNumberRight, iTime, iRoundInfo)
        self.SetupSignal()
        self.SetShow(False)

    
    def SetupSignal(self):
        oMgr = worldcupmgr.GetWorldCupMgr()
        oMgr.ssConnect(oMgr.SS_VoteCashChange, self.RefreshVoteCash)

    
    def InitDlg(self, iNumberLeft, iNumberRight, iTime, iRoundInfo):
        import combmacro
        import misc
        sNameLeft = GetCountryName(iNumberLeft)
        sNameRight = GetCountryName(iNumberRight)
        self.GetObject('txt_time').SetText(GetStringTime(iTime))
        sRound = GetMatchState(iRoundInfo)
        self.GetObject('txt_round').SetText(sRound)
        self.GetObject('txt_countryleft').SetText(sNameLeft)
        self.SetPropPos(sNameLeft, self.GetObject('txt_countryleft'))
        self.GetObject('txt_countryright').SetText(sNameRight)
        self.SetPropPos(sNameRight, self.GetObject('txt_countryright'))
        self.GetObject('txt_maxvote').SetText('\xa5\xbb\xb3\xf5\xb3\xcc\xa6h\xa5i\xa7U\xab\xc2\xa1G%d\xbfn\xa4\xc0' % self.m_iMaxPoint)
        (x, _, w, _) = self.GetLocData('txt_cash')
        (_, y, w1, _) = self.GetLocData('txt_maxvote')
        iDeltX = (w - w1) / 2
        self.GetObject('txt_maxvote').SetPos(x + iDeltX, y)
        (x1, y1) = self.GetObject('loc_countryleft').GetPos()
        (x2, y2) = self.GetObject('loc_countryright').GetPos()
        self.o_ImgCountryLeft = ui.CImage(self, 'combdialog/worldcup/duiqibig/%d.png' % iNumberLeft, interface.UIPath)
        self.o_ImgCountryRight = ui.CImage(self, 'combdialog/worldcup/duiqibig/%d.png' % iNumberRight, interface.UIPath)
        (w, h) = self.o_ImgCountryLeft.GetSize()
        self.o_ImgCountryLeft.SetSize(int(w * 1.2), int(h * 1.2))
        (w, h) = self.o_ImgCountryRight.GetSize()
        self.o_ImgCountryRight.SetSize(int(w * 1.2), int(h * 1.2))
        self.o_ImgCountryLeft.SetPos(x1, y1)
        self.o_ImgCountryRight.SetPos(x2, y2)
        self.m_oEditLeft = combmacro.CEDIT(CNumberEdit, 'loc_numleft', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oEditLeft.SetCountryName(sNameLeft, 'left')
        self.m_oEditLeft.SetLeftUpCB(misc.Functor(self.CreateTips))
        self.m_oEditLeft.SetCharChangeCB(misc.Functor(self.SetEditPos, self.GetObject('loc_price1'), self.m_oEditLeft))
        self.m_oEditLeft.SetMaxNum(self.m_iMaxPoint)
        self.m_oEditRight = combmacro.CEDIT(CNumberEdit, 'loc_numright', self, interface.COLOR_5, interface.FontLT14_3, interface.COLOR_5)
        self.m_oEditRight.SetCountryName(sNameRight, 'right')
        self.m_oEditRight.SetLeftUpCB(misc.Functor(self.CreateTips))
        self.m_oEditRight.SetCharChangeCB(misc.Functor(self.SetEditPos, self.GetObject('loc_price2'), self.m_oEditRight))
        self.m_oEditRight.SetMaxNum(self.m_iMaxPoint)

    
    def RefreshVoteCash(self, iRatio1, iRatio2, iAllCash, iVotePoint1, iVotePoint2):
        self.m_iAllCash = iAllCash
        self.GetObject('txt_voteleft').SetText('%d%%' % iRatio1)
        self.GetObject('txt_voteright').SetText('%d%%' % iRatio2)
        self.RefreshHasVote(iVotePoint1, iVotePoint2, iAllCash)
        self.SetShow(True)
        worldcupmgr.GetWorldCupMgr().ReciveVotePoint(self.m_iMatch, 1)

    
    def RefreshHasVote(self, iPoint1, iPoint2, iAllCash):
        self.m_iLeftPoint = iPoint1
        self.m_iRightPoint = iPoint2
        if self.m_bFisrtRefresh:
            if self.m_oEditLeft:
                iMaxNum = self.m_oEditLeft.GetMaxNum()
                self.m_oEditLeft.SetMaxNum(iMaxNum - iPoint1 - iPoint2)
            
            if self.m_oEditRight:
                iMaxNum = self.m_oEditRight.GetMaxNum()
                self.m_oEditRight.SetMaxNum(iMaxNum - iPoint1 - iPoint2)
            
        
        self.m_bFisrtRefresh = False
        sTxt = '\xa5i\xa5\xce\xbfn\xa4\xc0\n%d' % iAllCash
        self.GetObject('txt_cash').SetText(sTxt)
        self.GetObject('txt_hasvote1').SetText('\xa4w\xa7U\xab\xc2\xa1G%d\xbfn\xa4\xc0' % iPoint1)
        (x, _, w, _) = self.GetLocData('btn_004')
        (_, y, w1, _) = self.GetLocData('txt_hasvote1')
        iDeltX = (w1 - w) / 2
        self.GetObject('txt_hasvote1').SetPos(x - iDeltX, y)
        self.GetObject('txt_hasvote2').SetText('\xa4w\xa7U\xab\xc2\xa1G%d\xbfn\xa4\xc0' % iPoint2)
        (x, _, w, _) = self.GetLocData('btn_006')
        (_, y, w1, _) = self.GetLocData('txt_hasvote2')
        iDeltX = (w1 - w) / 2
        self.GetObject('txt_hasvote2').SetPos(x - iDeltX, y)

    
    def SetEditPos(self, oTar, oAttch):
        (x, y) = oTar.GetPos()
        sTxt = oAttch.GetText()
        if len(sTxt) == 1:
            oAttch.SetPos(x + 32, y)
        elif len(sTxt) == 2:
            oAttch.SetPos(x + 30, y)
        elif len(sTxt) == 3:
            oAttch.SetPos(x + 26, y)
        else:
            oAttch.SetPos(x + 22, y)

    
    def SetPropPos(self, sTxt, obj):
        if len(sTxt) == 6:
            (x, y) = obj.GetPos()
            obj.SetPos(x - 7, y)
        elif len(sTxt) == 8:
            (x, y) = obj.GetPos()
            obj.SetPos(x - 18, y)
        elif len(sTxt) == 10:
            (x, y) = obj.GetPos()
            obj.SetPos(x - 30, y)
        

    
    def CreateTips(self, sName, sPos):
        import timer
        import wrapinterface
        self.CloseTips()
        if self.m_iLeftPoint or self.m_iRightPoint:
            if self.m_iMaxPoint <= self.m_iLeftPoint + self.m_iRightPoint:
                sTxt = '\xb1z\xa5\xbb\xb3\xf5\xa7U\xab\xc2\xa4w\xb9F\xa4W\xad\xad,\xb5L\xaak\xc4~\xc4\xf2\xa7U\xab\xc2'
            else:
                sTxt = '#R%s\xb6\xa4#n\xaa\xba\xa7U\xab\xc2\xbdd\xb3\xf2\xac\xb0: #R%d#n ~ #R%d#n' % (sName, self.m_iMinPoint, self.m_iMaxPoint - (self.m_iLeftPoint + self.m_iRightPoint))
        else:
            sTxt = '#R%s\xb6\xa4#n\xaa\xba\xa7U\xab\xc2\xbdd\xb3\xf2\xac\xb0: #R%d#n ~ #R%d#n' % (sName, self.m_iMinPoint, self.m_iMaxPoint)
        if sPos == 'left':
            oPar = self.m_oEditLeft
        else:
            oPar = self.m_oEditRight
        self.m_oPointTips = wrapinterface.CCombTipsBox(oPar, sTxt, 6, 5, 0, 250, 35, 0, 0)
        self.m_Clock = timer.Timer(5, self.CloseTips)

    
    def CloseTips(self):
        if self.m_Clock:
            self.m_Clock.Release()
            self.m_Clock = None
        
        if self.m_oPointTips:
            self.m_oPointTips = None
        

    
    def VotePoint(self, iMatch, iSide, iPoint, dlg):
        worldcupmgr.GetWorldCupMgr().VotePoint(iMatch, iSide, iPoint)
        if self.m_oEditLeft:
            iMaxNum = self.m_oEditLeft.GetMaxNum()
            self.m_oEditLeft.SetMaxNum(iMaxNum - iPoint)
        
        if self.m_oEditRight:
            iMaxNum = self.m_oEditRight.GetMaxNum()
            self.m_oEditRight.SetMaxNum(iMaxNum - iPoint)
        
        self.m_iAllCash -= iPoint
        self.RefreshHasVote(self.m_iLeftPoint, self.m_iRightPoint, self.m_iAllCash)

    
    def CheckPoint(self, iType):
        import usermacro
        import commondialog
        import misc
        oEditList = [
            self.m_oEditLeft,
            self.m_oEditRight]
        iNumList = [
            self.m_iNumberLeft,
            self.m_iNumberRight]
        if oEditList[iType - 1].GetText() == '':
            iPoint = 0
        else:
            iPoint = int(oEditList[iType - 1].GetText())
        iCountryID = int(iNumList[iType - 1])
        if iPoint + self.m_iLeftPoint + self.m_iRightPoint > self.m_iMaxPoint:
            usermacro.PROMPT_MSG('\xa5\xbb\xb3\xf5\xc1`\xa6@\xa7\xeb\xa4J\xaa\xba\xbfn\xa4\xc0\xa4\xa3\xa5i\xb6W\xb9L\xa4W\xad\xad')
            return None
        
        if iPoint > self.m_iAllCash:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xa7U\xab\xc2\xbfn\xa4\xc0\xb6W\xa5X\xa4F\xa5i\xa5\xce\xbfn\xa4\xc0')
            return None
        
        if iPoint < self.m_iMinPoint:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xa7U\xab\xc2\xbfn\xa4\xc0\xb9L\xa4p,#R%s\xb6\xa4#n\xb3\xcc\xa7C\xa7U\xab\xc2\xbfn\xa4\xc0\xac\xb0#R%d#n' % (GetCountryName(iCountryID), self.m_iMinPoint))
            return None
        
        if iPoint > self.m_iMaxPoint:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xa7U\xab\xc2\xbfn\xa4\xc0\xb9L\xa4j,#R%s#n\xb6\xa4\xb3\xcc\xa4j\xa7U\xab\xc2\xbfn\xa4\xc0\xac\xb0#R%d#n' % (GetCountryName(iCountryID), self.m_iMaxPoint))
            return None
        
        dlg = commondialog.ShowMessageBox('\xa7A\xbdT\xa9w\xadn\xae\xf8\xaf\xd3#R%d#n\xc3\xe0\xc1\xf9\xbfn\xa4\xc0,\xb9\xef%s\xb6i\xa6\xe6\xa7U\xab\xc2\xb6\xdc?' % (iPoint, GetCountryName(iCountryID)), ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.VotePoint, self.m_iMatch, iType - 1, iPoint), None))

    
    def CloseWindow(self):
        global g_GuessDlg
        import mainmenu
        if self.m_Clock:
            self.m_Clock.Release()
            self.m_Clock = None
        
        worldcupmgr.GetWorldCupMgr().ReciveVotePoint(self.m_iMatch, 0)
        g_GuessDlg = None
        if mainmenu.GetChatInputObj():
            mainmenu.GetChatInputObj().Active(True)
        

    
    def OnMessage(self, msgid):
        if msgid in (1, 2):
            self.CheckPoint(msgid)
        elif msgid == 3:
            self.CloseWindow()
        



class CBoxButton(interface.CClickBox):
    
    def __init__(self, oParent, oMesPar, sBoxPath, sFlagPath, sName, w, h, iMsgid):
        interface.CClickBox.__init__(self, oParent, w, h, 0, 0, iMsgid)
        self.m_oMesPar = oMesPar
        self.m_oBox = None
        self.m_oImage = None
        self.m_oName = None
        self.m_oRatioTxt = None
        self.m_bIsSelect = False
        self.InitBox(oParent, sBoxPath, sFlagPath, sName, w, h)

    
    def InitBox(self, oParent, sBoxPath, sFlagPath, sName, w, h):
        import ui
        self.m_oBox = ui.CFrame(oParent, w, h, sBoxPath)
        self.m_oImage = ui.CImage(oParent, sFlagPath, interface.UIPath)
        self.m_oName = interface.CTextObject(oParent, sName, interface.FontLT12, 689141)
        self.m_oImage.SetPos(38, 10)
        (x, y) = self.m_oImage.GetPos()
        (w, h) = self.m_oImage.GetSize()
        (w1, _) = self.m_oName.GetSize()
        iDeltX = (w - w1) / 2
        self.m_oName.SetPos(x + iDeltX, 65)
        z = oParent.GetZ()
        self.m_oImage.SetZ(z + 10)
        self.m_oName.SetZ(z + 10)

    
    def LeftUp(self):
        self.m_bIsSelect = True
        if self.m_oName:
            self.m_oName.SetColor(12006177)
        
        if self.m_oRatioTxt:
            self.m_oRatioTxt.SetColor(12006177)
        
        self.m_oMesPar.Get().OnMessage(self.m_MsgID)

    
    def MouseWheelDown(self, p):
        if g_VoteDlg:
            g_VoteDlg.m_oList.MouseWheelDown(p)
        

    
    def MouseWheelUp(self, p):
        if g_VoteDlg:
            g_VoteDlg.m_oList.MouseWheelUp(p)
        



class CVoteDlg(combdialog.CCombDialog):
    BG_W = 140
    BG_H = 102
    
    def __init__(self, iType, lChampionRatio = None):
        if iType in (3, 4):
            sPath = 'dialog3/worldcup/guanjun.dlg'
        else:
            sPath = 'dialog3/worldcup/zhichi.dlg'
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, sPath)
        self.m_iType = iType
        self.m_oList = self.GetObject('list_box')
        self.m_oList.InitStyle('LIST_STYLE_3')
        self.m_oImageList = []
        self.m_oSelect = None
        self.m_iLastSel = -1
        interface.Center(self)
        self.InitDlg()
        if self.m_iType in (3, 4):
            self.RefreshRatio(lChampionRatio)
        

    
    def InitDlg(self):
        import interface
        import misc
        sBoxPath = 'combdialog3/\xcd\xb8\xc3\xf7\xb5\xd7\xbf\xf2/'
        (w, _) = self.m_oList.GetSize()
        for j in xrange(8):
            oBox = interface.CBoxObject(self.m_oList, w, 90, 0, 0)
            oBox.m_oList = []
            for i in xrange(4):
                oParBox = interface.CBoxObject(oBox, w, 90, 0, 0)
                oParBox.SetPos(i * 145 + 5, 2)
                sFlagPath = 'combdialog/worldcup/duiqismall/%d.png' % (i + j * 4)
                sName = GetCountryName(i + j * 4)
                iMsgid = i + j * 4
                obj = misc.WeakRef(self)
                oParBox.m_oBox = CBoxButton(oParBox, obj, sBoxPath, sFlagPath, sName, self.BG_W, self.BG_H, iMsgid)
                oBox.m_oList.append(oParBox)
            
            self.m_oList.AddItem(oBox)
        
        self.m_oList.ResetItems()
        self.m_oList.ResetScrollBar()

    
    def RefreshRatio(self, lChampionRatio):
        for iIndex, iRatio in enumerate(lChampionRatio):
            iRow = iIndex / 4
            iCol = iIndex - 4 * iRow
            oBox = self.m_oList.m_Items[iRow].m_oList[iCol].m_oBox
            iRatio = round(iRatio / 10, 1)
            oBox.m_oRatioTxt = interface.CTextObject(oBox, str(iRatio) + '%', interface.FontLT12, 689141)
            if oBox.m_bIsSelect:
                oBox.m_oRatioTxt.SetColor(12006177)
            
            (x, y) = oBox.m_oImage.GetPos()
            (w, h) = oBox.m_oImage.GetSize()
            (w1, _) = oBox.m_oRatioTxt.GetSize()
            iDeltX = (w - w1) / 2
            oBox.m_oRatioTxt.SetPos(x + iDeltX, 82)
            z = oBox.GetZ()
            oBox.m_oRatioTxt.SetZ(z + 10)
        
        worldcupmgr.GetWorldCupMgr().ReciveChampionRatio(1)

    
    def OnSelectBox(self, msgid):
        import ui
        if self.m_oSelect:
            self.m_oSelect = None
        
        if self.m_iLastSel and msgid != self.m_iLastSel:
            iRow = self.m_iLastSel / 4
            iCol = self.m_iLastSel - 4 * iRow
            oBox = self.m_oList.m_Items[iRow].m_oList[iCol].m_oBox
            oBox.m_bIsSelect = False
            if oBox.m_oName:
                oBox.m_oName.SetColor(689141)
            
            if oBox.m_oRatioTxt:
                oBox.m_oRatioTxt.SetColor(689141)
            
        
        iRow = msgid / 4
        iCol = msgid - 4 * iRow
        oBox = self.m_oList.m_Items[iRow].m_oList[iCol]
        self.m_oSelect = ui.CImage(oBox.m_oBox, 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xb1\xc0\xf8\xbd\xe7\xc3\xe6/\xd4\xd3\xcd\xbc/xiaodikuang.png', interface.UIPath)
        self.m_oSelect.SetSize(self.BG_W, self.BG_H)
        self.m_oSelect.SetZ(self.m_oSelect.GetParent().GetZ() + 1)
        self.m_iLastSel = msgid

    
    def OnVote(self, dlg):
        worldcupmgr.GetWorldCupMgr().SupportTeam(self.m_iType, self.m_iLastSel)
        if self.m_iType in (0, 3):
            self.CloseWindow()
        

    
    def OnEnsureVote(self):
        import misc
        import usermacro
        import commondialog
        if self.m_iLastSel == -1:
            usermacro.PROMPT_MSG('\xb1z\xc1\xd9\xa5\xbc\xbf\xef\xbe\xdc\xa4\xe4\xab\xf9\xaa\xba\xb2y\xb6\xa4!')
            return None
        
        sTxt = ''
        sCancelStr = '\xa8\xfa\xae\xf8'
        if self.m_iType == 0:
            sTxt = '\xa7A\xbdT\xa9w\xadn\xbf\xef\xbe\xdc#R%s\xb6\xa4#n\xb6\xa4#n\xa7@\xac\xb0\xa4\xe4\xab\xf9\xaa\xba\xb2y\xb6\xa4\xb6\xdc\xa1H#r\xa1]#R\xa4@\xb8g\xbf\xef\xa9w\xa1A\xb5L\xaak\xa7\xf3\xb4\xab\xa1A\xbd\xd0\xb7V\xad\xab\xbf\xef\xbe\xdc#n\xa1^' % GetCountryName(self.m_iLastSel)
            sCancelStr = '\xa7\xda\xa6A\xb7Q\xb7Q'
        elif self.m_iType == 2:
            sTxt = '\xa7A\xbdT\xa9w\xadn\xbb\xe2\xa8\xfa#R%s\xb6\xa4#n\xaa\xba\xb1M\xc4\xdd\xb2y\xb0g\xbc\xd0\xbbx\xa9M\xb2y\xb0g\xba\xd9\xbf\xd7\xb6\xdc\xa1H(\xbf\xef\xbe\xdc\xab\xe1\xadY\xb7Q\xa7\xf3\xb4\xab\xb1N\xae\xf8\xaf\xd310\xc3\xe0\xc1\xf9\xad\xec\xa9l\xbfn\xa4\xc0)' % GetCountryName(self.m_iLastSel)
        elif self.m_iType == 3:
            sTxt = '\xa7A\xbdT\xa9w\xadn\xaf\xac\xba\xd6#R%s\xb6\xa4#n\xb9\xdc\xaba\xb6\xdc\xa1H(\xbf\xef\xa9w\xab\xe1\xa6p\xbb\xdd\xa7\xf3\xb4\xab\xa1A\xbb\xdd\xae\xf8\xaf\xd3100\xc3\xe0\xc1\xf9\xa7U\xab\xc2\xbfn\xa4\xc0)' % GetCountryName(self.m_iLastSel)
        elif self.m_iType == 4:
            sTxt = '\xa7A\xbdT\xa9w\xa7\xf3\xa7\xef\xac\xb0\xaf\xac\xba\xd6#R%s\xb6\xa4#n\xb9\xdc\xaba\xb6\xdc\xa1H(\xbb\xdd\xae\xf8\xaf\xd3100\xc3\xe0\xc1\xf9\xa7U\xab\xc2\xbfn\xa4\xc0)' % GetCountryName(self.m_iLastSel)
        elif self.m_iType == 1:
            worldcupmgr.GetWorldCupMgr().SupportTeam(self.m_iType, self.m_iLastSel)
        
        if sTxt:
            dlg = commondialog.ShowMessageBox(sTxt, ('\xbdT\xa9w', sCancelStr), (misc.Functor(self.OnVote), None))
        

    
    def CloseWindow(self):
        global g_VoteDlg
        g_VoteDlg = None
        worldcupmgr.GetWorldCupMgr().ReciveChampionRatio(0)

    
    def OnMessage(self, msgid):
        if msgid >= 0 and msgid <= 31:
            self.OnSelectBox(msgid)
        elif msgid == 32:
            self.CloseWindow()
        elif msgid == 33:
            self.OnEnsureVote()
        



class CRankDlg(combdialog.CCombDialog):
    STARTY = 84
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog3/worldcup/rank.dlg')
        self.m_oTable = self.GetObject('table_rank')
        self.m_oTable.InitStyle('TABLE_STYLE_3')
        interface.Center(self)
        self.UpdatePlayerInfo()

    
    def UpdatePlayerInfo(self):
        import friend
        import hero
        lPlayerInfo = worldcupmgr.GetWorldCupMgr().GetPlayerInfo()
        for iIndex, dData in enumerate(lPlayerInfo):
            oBox = self.m_oTable.AddBoxItem()
            oItemList = []
            sRank = str(dData['rank'])
            sName = dData['name']
            sPoint = str(dData['WinPoint'])
            iTime = dData['GuessTime']
            sTime = str(iTime)
            iWinTime = dData['WinTime']
            iPlayerID = dData['ID']
            if iTime and iWinTime:
                iWinRatio = round(iWinTime / (iTime + 0), 3) * 100
                sWinPercent = '%.1f%%' % iWinRatio
            else:
                sWinPercent = '0%'
            color = 1787729
            if friend.IsFriend(iPlayerID, 0):
                color = 1221678
            
            iMyID = hero.GetRealID()
            if iPlayerID == iMyID:
                color = 15565312
            
            for sTxt in (sRank, sName, sPoint, sTime, sWinPercent):
                oItem = interface.CTextObject(oBox, sTxt, interface.FontLT14, color)
                oItemList.append(oItem)
            
            dAlignInfo = { }
            dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
            dAlignInfo['tOffset'] = (0, 3)
            self.m_oTable.AddItemExtend(oBox, oItemList, dAlignInfo = dAlignInfo, bChangeColor = False)
        
        self.m_oTable.ResetItems()
        self.m_oTable.ResetScrollBar()

    
    def ShowInfo(self, id, name, kind, coutry, ilv, arr):
        import combmacro
        self.m_Infos = []
        import avatar
        self.m_Photo = avatar.GetBigImgBy4Int(self, arr[0], arr[1], arr[2], arr[3], iPlayerID = id)
        (x, y) = self.GetObject('box_icon').GetPos()
        self.m_Photo.SetPos(x + 6, y + 6)
        self.m_ID = id
        self.m_Name = name
        lst = [
            ('txt_name', name),
            ('txt_id', '%d' % id),
            ('txt_class', kind),
            ('txt_coutry', coutry),
            ('txt_lv', '%d' % ilv)]
        for obj_name, txt in lst:
            txtobj = combmacro.CTEXT(interface.CTextObject, obj_name, self, txt, interface.FontLT14, 12006177)
            self.m_Infos.append(txtobj)
        

    
    def CloseWindow(self):
        global g_RankDlg
        g_RankDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid > msgid:
            pass
        elif msgid >= 101:
            iID = msgid - 101
            lPlayerInfo = worldcupmgr.GetWorldCupMgr().GetPlayerInfo()
            iPlayerID = lPlayerInfo[iID]['ID']
            worldcupmgr.GetWorldCupMgr().RequestPlayerInfoByID(iPlayerID)
        



class CHistoryDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog3/worldcup/history.dlg')
        self.m_oTable = self.GetObject('table_history')
        self.m_oTable.InitStyle('TABLE_STYLE_3')
        interface.Center(self)
        self.SetShow(False)
        self.SetupSignal()

    
    def SetupSignal(self):
        oMgr = worldcupmgr.GetWorldCupMgr()
        oMgr.ssConnect(oMgr.SS_RefreshHistory, self.RefreshHistory)

    
    def RefreshHistory(self, iRewardPoint, dInfolist):
        mgr = worldcupmgr.GetWorldCupMgr()
        (iVoteTime, iVoteRatio) = mgr.GetGuessInfo()
        self.GetObject('txt_votetime').SetText('\xa7\xb9\xa6\xa8\xa7U\xab\xc2\xa6\xb8\xbc\xc6\xa1G%d' % iVoteTime)
        self.GetObject('txt_winratio').SetText('\xb3\xd3\xb2v\xa1G%.1f%%' % iVoteRatio)
        self.GetObject('txt_winrati1').SetText('\xc1`\xb2b\xc1\xc8\xbfn\xa4\xc0\xa1G%d' % iRewardPoint)
        for dInfo in dInfolist:
            oBox = self.m_oTable.AddBoxItem()
            oItemList = []
            sTime = GetStringTime(dInfo['time'])
            oTxtTime = interface.CTextObject(oBox, sTime, interface.FontLT14, 1787729)
            oItemList.append(oTxtTime)
            sCountry1 = GetCountryName(dInfo['country1'])
            sCountry2 = GetCountryName(dInfo['country2'])
            if dInfo['side'] == 0:
                sCountry1 = '#ced8200' + sCountry1 + '#n#c1B4751'
            else:
                sCountry2 = '#ced8200' + sCountry2 + '#n#c1B4751'
            iResult = dInfo['result']
            if iResult == 1:
                sResult = '#c1B4751%s(%s) - %s(%s)' % (sCountry1, '#cb73321\xb3\xd3#n#c1B4751', sCountry2, '#c0a83f5\xadt#n#c1B4751')
            elif iResult == 2:
                sResult = '#c1B4751%s(%s) - %s(%s)' % (sCountry1, '#c0a83f5\xadt#n#c1B4751', sCountry2, '#cb73321\xb3\xd3#n#c1B4751')
            else:
                sResult = '#c1B4751%s(\xa5\xad) - %s(\xa5\xad)' % (sCountry1, sCountry2)
            oTxtResult = interface.CRichTextObject(oBox, 300, interface.FontLT14, sResult)
            oItemList.append(oTxtResult)
            iRatio = dInfo['ratio']
            if dInfo['side'] == 0:
                sRatio = '%d%%' % iRatio
            else:
                sRatio = '%d%%' % (100 - iRatio)
            oTxtRatio = interface.CTextObject(oBox, sRatio, interface.FontLT14, 1787729)
            oItemList.append(oTxtRatio)
            bWin = dInfo['win']
            if bWin:
                sWin = '\xa6\xa8\xa5\\'
                color = 12006177
            else:
                sWin = '\xbf\xf2\xbe\xd1'
                color = 689141
            oTxtWin = interface.CTextObject(oBox, sWin, interface.FontLT14, color)
            oItemList.append(oTxtWin)
            iWinPoint = dInfo['point']
            if bWin:
                txt = '+ %d' % iWinPoint
            else:
                txt = '- %d' % iWinPoint
            oTxtPoint = interface.CTextObject(oBox, txt, interface.FontLT14, color)
            oItemList.append(oTxtPoint)
            dAlignInfo = { }
            dAlignInfo['iAlign'] = interface.ALIGN_CENTER_MIDDLE
            dAlignInfo['tOffset'] = (0, 3)
            self.m_oTable.AddItemExtend(oBox, oItemList, dAlignInfo = dAlignInfo, bChangeColor = False)
        
        self.m_oTable.ResetItems()
        self.m_oTable.ResetScrollBar()
        self.SetShow(True)

    
    def CloseWindow(self):
        global g_HistoryDlg
        g_HistoryDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        



def GetCountryName(iId):
    return COUNTRY_DICT[iId]


def GetCountryID(sName):
    for key, name in COUNTRY_DICT.items():
        if name == sName:
            return key
            continue
    
    return 0


def GetStringTime(iTime):
    import time
    tTime = time.localtime(iTime)
    if tTime[4] == 0:
        sMin = '00'
        sTxt = '%d\xa4\xeb%d\xa4\xe9 %d:%s' % (tTime[1], tTime[2], tTime[3], sMin)
    else:
        sTxt = '%d\xa4\xeb%d\xa4\xe9 %d:%s' % (tTime[1], tTime[2], tTime[3], tTime[4])
    return sTxt


def GetMaxMinPoint(\xe4Round):
    if \xe4Round == 1:
        return (1, 50)
    elif \xe4Round == 4:
        return (1, 100)
    elif \xe4Round == 5:
        return (1, 200)
    elif \xe4Round == 6:
        return (1, 400)
    elif \xe4Round == 7:
        return (1, 400)
    elif \xe4Round == 8:
        return (1, 1000)
    else:
        return (1, 50)


def GetMatchState(iState):
    dInfo = {
        1: '\xa4p\xb2\xd5\xc1\xc9 \xb2\xc4\xa4@\xbd\xfc',
        2: '\xa4p\xb2\xd5\xc1\xc9 \xb2\xc4\xa4G\xbd\xfc',
        3: '\xa4p\xb2\xd5\xc1\xc9 \xb2\xc4\xa4T\xbd\xfc',
        4: '\xa4K\xa4\xc0\xa4\xa7\xa4@\xa8M\xc1\xc9',
        5: '\xa5|\xa4\xc0\xa4\xa7\xa4@\xa8M\xc1\xc9',
        6: '\xa5b\xa8M\xc1\xc9',
        7: '\xa9u\xadx\xc1\xc9',
        8: '\xa8M\xc1\xc9' }
    return dInfo.get(iState, '\xa4p\xb2\xd5\xc1\xc9 \xb2\xc4\xa4@\xbd\xfc')
