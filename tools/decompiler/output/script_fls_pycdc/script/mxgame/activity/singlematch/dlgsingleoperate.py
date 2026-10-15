# pycdc 交叉复核产物 · script.fls entry 3035
# co_filename(原始)='script/mxgame/activity/singlematch/dlgsingleoperate.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3035.pyc (Python 2.5)

import combdialog
import interface
import singlematchmgr
import netsinglematch
import ui
g_SingleOperateDlg = None
g_ResultDlg = None

def ModuleReset():
    global g_SingleOperateDlg, g_ResultDlg
    g_SingleOperateDlg = None
    g_ResultDlg = None


def ShowOperateDlg(bStatus):
    global g_SingleOperateDlg, g_SingleOperateDlg
    if bStatus:
        if not g_SingleOperateDlg:
            g_SingleOperateDlg = CSingleOperateDlg()
        
        g_SingleOperateDlg.SetShow(True)
    elif g_SingleOperateDlg:
        g_SingleOperateDlg = None
    


def RefreshMatchStatus(iStatus):
    if not g_SingleOperateDlg:
        return None
    
    g_SingleOperateDlg.RefreshBtnMatch(iStatus)


def ShowSingleResultDlg(dResultData):
    global g_ResultDlg
    if not g_ResultDlg:
        g_ResultDlg = CResultDialog(dResultData)
    
    g_ResultDlg.SetShow(True)


class CResultDialog(combdialog.CCombDialog):
    
    def __init__(self, dResultData):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/single_match/result.dlg')
        interface.Center(self)
        self.RefreshResultData(dResultData)

    
    def RefreshResultData(self, dResultData):
        '''
\t\t\xa8\xea\xb7s\xbe\xd4\xb3\xf8\xbc\xc6\xbe\xda
\t\t:param dResultData:
\t\t{
\t\t\tiStatus:\t\xbe\xd4\xb0\xab\xb5\xb2\xaaG0-\xa5\xa2\xb1\xd1\xa1A1-\xb3\xd3\xa7Q\xa1A2-\xa5\xad\xa7\xbd
\t\t\tiStagePoint:\t\xb7\xed\xabe\xb3\xd3\xc2I
\t\t\tiAddType:\t\xb3\xd3\xc2I\xbcW\xa5[/\xb4\xee\xa4\xd6\t0/1
\t\t\tiAddPoint:\t\xa7\xef\xc5\xdc\xaa\xba\xb3\xd3\xc2I\xbc\xc6\xad\xc8
\t\t\tdMyResultData:\t\xa7\xda\xa4\xe8\xbe\xd4\xb0\xab\xbc\xc6\xbe\xda
\t\t\tdEnemyResultData:\t\xbc\xc4\xa4\xe8\xbe\xd4\xb0\xab\xbc\xc6\xbe\xda
\t\t\t\t{
\t\t\t\t\tiId:\t\xa8\xa4\xa6\xe2ID
\t\t\t\t\tsName\xa1G\t\xa8\xa4\xa6\xe2\xa6W\xa6r
\t\t\t\t\tiLv:\t\xa8\xa4\xa6\xe2\xb5\xa5\xaf\xc5
\t\t\t\t\tiClass:\t\xa8\xa4\xa6\xe2\xc2\xbe\xb7~
\t\t\t\t\tiLiupai:\t\xa8\xa4\xa6\xe2\xacy\xac\xa3
\t\t\t\t\tiStage:\t\xa8\xa4\xa6\xe2\xacq\xa6\xec
\t\t\t\t}
\t\t}
\t\t'''
        iResultStatus = dResultData['iStatus']
        self.RefreshImg(iResultStatus)
        dMyResultInfo = dResultData['dMyResultData']
        iStage = dMyResultInfo['iStage']
        iStagePoint = dResultData['iStagePoint']
        self.RefreshTextPoint(iStage, iStagePoint)
        iAddType = dResultData['iAddType']
        iAddPoint = dResultData['iAddPoint']
        self.RefreshPointProgress(iStage, iStagePoint, iAddType, iAddPoint)
        dEnemyResultInfo = dResultData['dEnemyResultData']
        self.RefreshWarInfo(dMyResultInfo, dEnemyResultInfo)

    
    def RefreshImg(self, iStatus):
        oImgWin = self.GetObject('img_win')
        oImgLose = self.GetObject('img_lose')
        oImgWin.SetShow(iStatus == 1)
        oImgLose.SetShow(iStatus == 0)
        LOG_DEBUG('iStatus: ', iStatus)

    
    def RefreshTextPoint(self, iStage, iStagePoint):
        sTextStage = singlematchmgr.GetStage(iStage)
        oTextStage = self.GetObject('text_stage')
        sTextStage = '%s%d\xb3\xd3\xc2I' % (sTextStage, iStagePoint)
        oTextStage.SetText(sTextStage)

    
    def RefreshPointProgress(self, iStage, iStagePoint, iAddType, iAddPoint):
        sSignList = [
            '-',
            '+']
        if iStage >= 12:
            sMaxPoint = '--'
            iCurProgress = 0
        else:
            iMaxPoint = 100
            sMaxPoint = str(iMaxPoint)
            iCurProgress = iStagePoint * 1 / iMaxPoint
        sTextProgress = '%d(%s%d)/%s' % (iStagePoint, sSignList[iAddType], iAddPoint, sMaxPoint)
        oTextProgress = self.GetObject('text_pro')
        oTextProgress.SetText(sTextProgress)
        oPointPro = self.GetObject('pro_point')
        LOG_DEBUG('iCurProgress: ', iCurProgress)
        oPointPro.SetRate(iCurProgress * 1000)

    
    def RefreshWarInfo(self, dMyInfo, dEnemyInfo):
        import hero
        sTextNameList = [
            'my',
            'enemy']
        dInfoList = [
            dMyInfo,
            dEnemyInfo]
        for \xad\x8dndex, data in enumerate(dInfoList):
            sInfoName = sTextNameList[\xad\x8dndex]
            sTextName = 'text_%s_name' % sInfoName
            oTextName = self.GetObject(sTextName)
            oTextName.SetText(data['sName'])
            sTextLevel = 'text_%s_lv' % sInfoName
            oTextLevel = self.GetObject(sTextLevel)
            sClass = hero.id2class(data['iClass'])
            sLevel = '%d\xaf\xc5%s' % (data['iLv'], sClass)
            oTextLevel.SetText(sLevel)
            sTextStage = 'text_%s_stage' % sInfoName
            oTextStage = self.GetObject(sTextStage)
            sStage = singlematchmgr.GetStage(data['iStage'])
            oTextStage.SetText(sStage)
        

    
    def CloseWindow(self):
        global g_ResultDlg
        g_ResultDlg = None

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        



class CSingleOperateDlg(combdialog.CCombDialog):
    
    def __init__(self):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/single_match/roominfo.dlg')
        self.m_RedPoint = None
        self.m_iMatchStatus = 0
        self.m_sBtnNameList = [
            'btn_match',
            'btn_exchange',
            'btn_reward',
            'btn_zhanji',
            'btn_leave',
            'btn_buy']
        self.SetIgnoreEsc(True)
        self.InitDialog()
        self.InitListener()
        self.ResetPos()

    
    def RefreshBtnMatch(self, iStatus):
        self.m_iMatchStatus = iStatus
        if self.m_iMatchStatus:
            sBtnText = '\xbc\xc8\xb0\xb1\xa4\xc7\xb0t'
        else:
            sBtnText = '\xb6}\xa9l\xa4\xc7\xb0t'
        oBtn = self.GetObject('btn_match')
        oBtn.SetText(sBtnText)

    
    def ResetPos(self):
        self.SetPos(35, 68)

    
    def InitListener(self):
        import commoncb
        oMgr = singlematchmgr.GetMgr()
        oMgr.ssConnect(oMgr.SS_RewardChange, self.RefreshRedPoint)
        oMgr.ssConnect(oMgr.SS_MyInfoChange, self.RefreshCharInfo)
        commoncb.RegistCB(commoncb.WAR_START, self, 'SetShow', False)

    
    def InitDialog(self):
        oBtnMax = self.GetObject('btn_max')
        oBtnMax.SetShow(False)
        oBtnMatch = self.GetObject('btn_match')
        oBtnMatch.SetText('\xb6}\xa9l\xa4\xc7\xb0t')

    
    def CreateRedPoint(self):
        oBtn = self.GetObject('btn_reward')
        (w, _) = oBtn.GetSize()
        self.m_RedPoint = ui.CImage(oBtn, 'combdialog/\xd4\xd3\xcd\xbc/\xcc\xe1\xca\xbe\xd0\xa1\xba\xec\xb5\xe3.igs', 'interface')
        self.m_RedPoint.SetPos(w - 10, -2)
        self.m_RedPoint.SetZ(1)

    
    def RefreshRedPoint(self):
        oMgr = singlematchmgr.GetMgr()
        bTakenAllReward = oMgr.IsTakeAllReward()
        if bTakenAllReward:
            self.m_RedPoint = None
        else:
            self.CreateRedPoint()

    
    def RefreshCharInfo(self):
        pass

    
    def OnMatch(self):
        iNextStatus = int(not (self.m_iMatchStatus))
        self.m_iMatchStatus = iNextStatus
        LOG_DEBUG('iNextStatus: ', iNextStatus)
        netsinglematch.C2SRequestMatch(iNextStatus)
        self.RefreshBtnMatch(iNextStatus)

    
    def OnLeave(self):
        LOG_DEBUG('\xaa\xf0\xa6^\xad\xec\xaaA')
        netsinglematch.C2SGoBackServer()

    
    def OnCombatGains(self):
        LOG_DEBUG('\xacd\xac\xdd\xbe\xd4\xc1Z')
        netsinglematch.C2SShowWarResultDlg()

    
    def OnReward(self):
        LOG_DEBUG('\xacd\xac\xdd\xbc\xfa\xc0y')
        netsinglematch.C2SShowRewardDlg()

    
    def OnSwitch(self, idx):
        oBtnMin = self.GetObject('btn_min')
        oBtnMax = self.GetObject('btn_max')
        oBtnMin.SetShow(idx)
        oBtnMax.SetShow(not idx)
        for sName in self.m_sBtnNameList:
            self.GetObject(sName).SetShow(idx)
        
        if idx:
            self.GetObject('bg').SetSize(206, 175)
        else:
            self.GetObject('bg').SetSize(206, 60)

    
    def OnExchange(self):
        import netcommon
        netcommon.C2SRemoteShopping(12)

    
    def OnBuy(self):
        netsinglematch.C2SBuyDrug()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.OnMatch()
        elif msgid == 2:
            self.OnLeave()
        elif msgid == 3:
            self.OnReward()
        elif msgid == 4:
            self.OnCombatGains()
        elif msgid == 5:
            self.OnExchange()
        elif msgid in (6, 7):
            self.OnSwitch(msgid - 6)
        elif msgid == 10:
            self.OnBuy()
