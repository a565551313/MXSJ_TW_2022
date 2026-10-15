# pycdc 交叉复核产物 · script.fls entry 326
# co_filename(原始)='script/mxgame/goodvoice/delegate/dgtgoodvoice_main.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_326.pyc (Python 2.5)

import delegatebase
import goodvoiceinterface
import goodvoicereportctrl
import netgoodvoice
import logic_audiomgr
import hero
import timer
import interface
g_Test = None

def ModuleReset():
    global g_Test
    g_Test = False


def SetIsTest(bTest):
    global g_Test
    g_Test = bTest


def IsTest():
    return g_Test


class CDgtGoodVoiceMain(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        delegatebase.CDelegateBase.__init__(self, oView)
        self.m_oSelectUniqueID = None
        self.m_lUniqueID = []
        self.m_dUnique2PlayHandleID = { }
        self.m_dHandle2UniqueID = { }
        self.m_oTimer = None
        self.m_iPlayAudioHandle = 0
        self.m_oCurPlayVoiceID = None
        self.Reset()
        self.InitSignal()

    
    def GetView(self):
        ''':rtype:dlggoodvoice_main.CGoodVoiceMainDlg'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        oView = self.GetView()
        oView.SetGetTableCellDataByID(self.CalOneGoodVoiceItemData)

    
    def Reset(self):
        if self.m_iPlayAudioHandle:
            self.OnUIEvent_StopVoice(self.m_oCurPlayVoiceID[1])
        
        oDataMgr = self.GetDataMgr()
        lPlayerID = oDataMgr.GetPlayerList()
        self.m_lUniqueID = self.CalUniqueID(lPlayerID)
        oUniqueID = None if not self.m_lUniqueID else self.m_lUniqueID[0]
        self.SetSelectUniqueID(oUniqueID, False)
        self.OnRefreshListView()
        self.OnRefreshSelectView()

    
    def CalUniqueID(self, lPlayerID):
        import random
        oDataMgr = self.GetDataMgr()
        lUniqueID = []
        for iPlayerID in lPlayerID:
            oGoodVoice = oDataMgr.GetPlayerGoodVoice(iPlayerID)
            lUrl = oGoodVoice.GetVoiceUrl()
            for sUrl in lUrl:
                tUniqueID = (iPlayerID, sUrl)
                lUniqueID.append(tUniqueID)
            
        
        random.shuffle(lUniqueID)
        return lUniqueID

    
    def GetDataMgr(self):
        ''':rtype:  mdgoodvoicemgr.CGoodVoiceMgr'''
        oContext = goodvoiceinterface.GetGoodVoiceContext()
        return oContext.GetGoodVoiceDataMgr()

    
    def InitSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_CloseDlg, self.OnUIEvent_CloseDlg)
        oView.ssConnect(oView.SS_OpenDlg, self.OnUIEvent_OpenDlg)
        oView.ssConnect(oView.SS_Clear, self.OnUIEvent_Clear)
        oView.ssConnect(oView.SS_SelectCell, self.OnUIEvent_Select)
        oView.ssConnect(oView.SS_MoveTableView, self.OnUIEvent_TableViewMove)
        oView.ssConnect(oView.SS_CellEvent, self.OnUIEvent_CellEvent)
        oDataMgr = self.GetDataMgr()
        oDataMgr.ssConnect(oDataMgr.SS_RefreshPlayerList, self.OnDataEvent_RefreshPlayerList)
        oDataMgr.ssConnect(oDataMgr.SS_Clear, self.OnDataEvent_Clear)
        oPlayVoiceLogic = logic_audiomgr.GetAudioMgr().GetPlayLogic()
        oPlayVoiceLogic.ssConnect(oPlayVoiceLogic.SS_StartPlay, self.OnPlayVoiceEvent_Start)
        oPlayVoiceLogic.ssConnect(oPlayVoiceLogic.SS_StopPlay, self.OnPlayVoiceEvent_Stop)
        oPlayVoiceLogic.ssConnect(oPlayVoiceLogic.SS_UpdatePlayRate, self.OnPlayVoiceEvent_Rate)

    
    def OnRefreshListView(self, iStart = 0, bReset = False):
        oView = self.GetView()
        oView.ReloadGoodVoiceListView(self.m_lUniqueID, iStart, bReset)

    
    def CalOneGoodVoiceItemData(self, oUniqueID):
        '''
\t\tDBaseUI2Prop = {
\t\t\t"text_number": "sNumber",
\t\t\t#\xc0Y\xb9\xb3
\t\t\t"text_playername": "sName",
\t\t\t"text_guanxi": "sRelation",
\t\t\t"text_voicename": "sSingName",
\t\t\t"txt_audio_sec": "sTime",
\t\t}
\t\tTAudioProp = ("bPlay", "iRate", "sTime")

\t\tTOthersProp =  ("bSelect", "bReport", "tPhotoAttr", "iShape", "iSex")
\t\t:param oUniqueID:
\t\t:return:
\t\t'''
        import friend
        (iPlayerID, sVoiceUrl) = oUniqueID
        oDataMgr = self.GetDataMgr()
        oOneVoiceData = oDataMgr.GetPlayerGoodVoice(iPlayerID)
        dOneVoice = oOneVoiceData.GetOneVoiceData(sVoiceUrl)
        if dOneVoice is None:
            dOneVoice = { }
        
        sRelation = ''
        iRelationColor = None
        sOrg = oOneVoiceData.GetPropByKey('sOrg')
        iMarryID = hero.GetProp('m_MarryID', 0)
        if iPlayerID == hero.GetHeroID():
            sRelation = ''
            iRelationColor = interface.COLOR_169
        elif iMarryID == iPlayerID:
            sRelation = '\xa6\xf1\xabQ'
        elif friend.IsFriend(iPlayerID):
            sRelation = '\xa6n\xa4\xcd'
        elif sOrg == hero.GetProp('sOrg', '') and sOrg:
            sRelation = '\xa6P\xc0\xb0'
        
        dData = {
            'iPlayerID': iPlayerID,
            'tUniqueID': oUniqueID,
            'sUrl': sVoiceUrl,
            'sNumber': str(oOneVoiceData.GetPropByKey('iID')),
            'sName': oOneVoiceData.GetPropByKey('sName', ''),
            'sRelation': sRelation,
            'iRelationColor': iRelationColor,
            'sSingName': dOneVoice.\x95\x97\x86('sName'),
            'sTime': '%s"' % dOneVoice.\x95\x97\x86('iDur', 0),
            'bPlay': oUniqueID == self.m_oCurPlayVoiceID,
            'iRate': self.GetUrlRate(oUniqueID),
            'bSelect': self.m_oSelectUniqueID == oUniqueID,
            'bReport': hero.GetHeroID() != iPlayerID,
            'tPhotoAttr': oOneVoiceData.GetPropByKey('tPhotoAttr', ()),
            'iShape': oOneVoiceData.GetPropByKey('iShape', 0),
            'iSex': oOneVoiceData.GetPropByKey('iSex', 1) }
        return dData

    
    def OnRefreshSelectView(self):
        oView = self.GetView()
        oView.RefreshSelect(self.m_oSelectUniqueID)

    
    def SetSelectUniqueID(self, oUniqueID, bRefreshView = True):
        if self.m_oSelectUniqueID == oUniqueID:
            return None
        
        self.m_oSelectUniqueID = oUniqueID
        if bRefreshView:
            self.OnRefreshSelectView()
        

    
    def SetCurPlayVoiceUrl(self, oUniqueID):
        if self.m_oCurPlayVoiceID == oUniqueID:
            return None
        
        self.m_iPlayAudioHandle = None
        oOldUniqueID = self.m_oCurPlayVoiceID
        self.m_oCurPlayVoiceID = oUniqueID
        if oOldUniqueID:
            self.OnRefreshOneVoiceView(oOldUniqueID)
        
        if oUniqueID:
            self.OnRefreshOneVoiceView(oUniqueID)
        

    
    def OnRefreshOneVoiceView(self, oUniqueID):
        if oUniqueID not in self.m_lUniqueID:
            return None
        
        iIndex = self.m_lUniqueID.index(oUniqueID)
        oView = self.GetView()
        (iMin, iMax) = oView.GetTableViewRange()
        if iIndex < iMin or iIndex > iMax:
            return None
        
        oView.OnRefreshOneVoiceView(oUniqueID)

    
    def GetUrlRate(self, oUniqueID):
        if self.m_oCurPlayVoiceID != oUniqueID:
            return 1000
        else:
            oPlayLogic = logic_audiomgr.GetAudioMgr().GetPlayLogic()
            iRate = oPlayLogic.GetAudioRate()
            return iRate

    
    def StopPlaying(self):
        self.SetCurPlayVoiceUrl('')
        oPlayLogic = logic_audiomgr.GetAudioMgr().GetPlayLogic()
        oPlayLogic.DoStopPlay()

    
    def OnDataEvent_RefreshPlayerList(self, lPlayerID):
        oView = self.GetView()
        (oUniqueID, iCurMin) = oView.GetTableViewStartData()
        lUniqueID = self.CalUniqueID(lPlayerID)
        self.m_lUniqueID.extend(lUniqueID)
        if len(self.m_lUniqueID) > iCurMin and oUniqueID in self.m_lUniqueID:
            if self.m_lUniqueID[iCurMin] == oUniqueID:
                bReset = False
                iMin = iCurMin
            else:
                bReset = True
                iMin = self.m_lUniqueID.index(oUniqueID)
        else:
            bReset = True
            iMin = 0
            if oUniqueID in self.m_lUniqueID:
                iMin = self.m_lUniqueID.index(oUniqueID)
            
        if oUniqueID in self.m_lUniqueID:
            iMin = self.m_lUniqueID.index(oUniqueID)
        
        self.OnRefreshListView(iMin, bReset)
        self.OnRefreshSelectView()

    
    def OnDataEvent_Clear(self):
        self.Reset()
        if not self.m_lUniqueID:
            self.RequestNextPageIfNeeded()
        

    
    def OnUIEvent_CloseDlg(self):
        oView = self.GetView()
        oView.CloseDlg()
        if self.m_iPlayAudioHandle:
            self.StopPlaying()
        

    
    def OnUIEvent_OpenDlg(self):
        bShow = self.GetView()
        if bShow:
            return None
        
        oView = self.GetView()
        oView.SetShow(True)
        self.Reset()

    
    def OnUIEvent_Select(self, oUniqueID):
        self.SetSelectUniqueID(oUniqueID)

    
    def OnUIEvent_TableViewMove(self, sEvent, iVisibleMin, iVisibleMax, iMax):
        if not self.IsEnableRequest():
            return None
        
        if sEvent == 'down':
            if iVisibleMax != iMax - 1:
                return None
            
            self.RequestNextPageIfNeeded()
        elif sEvent == 'barchange':
            if iVisibleMax == iMax - 1:
                self.RequestNextPageIfNeeded()
            
        

    
    def IsEnableRequest(self):
        return None if not self.m_oTimer else False

    
    def ReleaseTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
        

    
    def RequestNextPageIfNeeded(self):
        self.m_oTimer = timer.Timer(1, self.ReleaseTimer, oRelayObj = self)
        oDataMgr = self.GetDataMgr()
        LOG('RequestNextPageIfNeeded', oDataMgr.IsEnableRequestNext(), len(oDataMgr.m_lAllPlayerList), len(oDataMgr.m_lLeftPlayerList))
        if not oDataMgr.IsEnableRequestNext():
            return None
        
        lNextList = oDataMgr.GetNextRequestList()
        netgoodvoice.C2GSGetPageInfo(lNextList)

    
    def OnUIEvent_CellEvent(self, tUniqueID, sEvent):
        dEventName2Func = {
            'vote': self.OnUIEvent_Vote,
            'pub': self.OnUIEvent_Pub,
            'play': self.OnUIEvent_PlayVoice,
            'sendfllower': self.OnUIEvent_GiveFllower,
            'report': self.OnUIEvent_Report,
            'playerinfo': self.OnUIEvent_Info }
        if sEvent not in dEventName2Func:
            return None
        
        self.SetSelectUniqueID(tUniqueID)
        oFunc = dEventName2Func[sEvent]
        oFunc(tUniqueID)

    
    def OnUIEvent_PlayVoice(self, oUniqueID):
        sWho = oUniqueID[1]
        if oUniqueID == self.m_oCurPlayVoiceID:
            self.OnUIEvent_StopVoice(sWho)
        else:
            oPlayLogic = logic_audiomgr.GetAudioMgr().GetPlayLogic()
            sPath = goodvoiceinterface.UrlAudio2LocalPath(sWho)
            oPlayLogic.DoStopPlay()
            self.SetCurPlayVoiceUrl(oUniqueID)
            if oUniqueID not in self.m_dUnique2PlayHandleID:
                iHandleID = logic_audiomgr.GetAudioMgr().CreateHandle()
                self.m_dUnique2PlayHandleID[oUniqueID] = iHandleID
                self.m_dHandle2UniqueID[iHandleID] = oUniqueID
            
            self.m_iPlayAudioHandle = self.m_dUnique2PlayHandleID[oUniqueID]
            oPlayLogic.OnPlay(sWho, sPath, self.m_iPlayAudioHandle)

    
    def OnUIEvent_StopVoice(self, sWho):
        oPlayLogic = logic_audiomgr.GetAudioMgr().GetPlayLogic()
        if not self.m_oCurPlayVoiceID:
            return None
        
        self.SetCurPlayVoiceUrl('')
        oPlayLogic.DoStopPlay()

    
    def OnUIEvent_Vote(self, oUniqueID):
        iPlayerID = oUniqueID[0]
        netgoodvoice.C2GSVote(iPlayerID)

    
    def OnUIEvent_GiveFllower(self, oUniqueID):
        iPlayerID = oUniqueID[0]
        netgoodvoice.C2GSOpenSendFlowerDlg(iPlayerID)

    
    def OnUIEvent_Pub(self, oUniqueID):
        iPlayerID = oUniqueID[0]
        netgoodvoice.C2GSBroadCastGoodVoice(iPlayerID)

    
    def OnUIEvent_Report(self, oUniqueID):
        iPlayerID = oUniqueID[0]
        goodvoicereportctrl.GetCtrl().OpenReportDlg(iPlayerID)

    
    def OnUIEvent_Info(self, oUniqueID):
        iPlayerID = oUniqueID[0]
        import netfriend
        import dlginfo
        if not iPlayerID:
            return None
        
        dlginfo.ShowInfoDialog(iPlayerID)
        netfriend.C2SFindWithID(iPlayerID, 1)

    
    def OnUIEvent_Clear(self):
        if self.m_iPlayAudioHandle:
            self.StopPlaying()
        

    
    def OnPlayVoiceEvent_Start(self, bSuc, sPath, sUrl, iSumTime, sFailReason, iHandle):
        if iHandle != self.m_iPlayAudioHandle:
            return None
        
        if not bSuc:
            LOG(sFailReason)
            self.SetCurPlayVoiceUrl('')
        

    
    def OnPlayVoiceEvent_Stop(self, sPath, sUrl, iHandle):
        if iHandle != self.m_iPlayAudioHandle:
            return None
        
        self.SetCurPlayVoiceUrl('')

    
    def OnPlayVoiceEvent_Rate(self, sPath, sUrl, iRate, iHandle):
        if iHandle != self.m_iPlayAudioHandle:
            return None
        
        if not self.m_oCurPlayVoiceID:
            return None
        
        if sUrl != self.m_oCurPlayVoiceID[1]:
            return None
        
        self.OnRefreshOneVoiceView(self.m_oCurPlayVoiceID)
