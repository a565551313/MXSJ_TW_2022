# pycdc 交叉复核产物 · script.fls entry 1522
# co_filename(原始)='script/yard/yardplayerhome/delegate/delegateyardhome_info.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1522.pyc (Python 2.5)

import delegatebase
import misc
import netyardhome
import hero
import yardinterface
import yardhomedefines
HOUSE_TYPE2_NAME = {
    1: '\xa5\xc1\xa6v',
    2: '\xb5\xd8\xa6v',
    3: '\xbb\xa8\xa6v' }
FENGSHUI_TYPE2_NAME = {
    1: '\xad\xb7\xa4\xbf\xa4\xf5\xb2\xa7',
    2: '\xabj\xb1j\xa6w\xa9~',
    3: '\xa8}\xa6v\xa6n\xa6a',
    4: '\xba\xd6\xa5\xfa\xc1\xf4\xb2{',
    5: '\xba\xd6\xac\xe7\xac\xd5\xaa\xf9',
    6: '\xb5\xb5\xae\xf0\xaaF\xa8\xd3',
    7: '\xb4I\xb6Q\xba\xd6\xb7\xbd' }
MSG_EVENT = ('visitset', 'yardrank', 'openpet', 'myyard', 'levelup', 'resetfengshui')

class CDelegateHomeInfo(delegatebase.CDelegateBase):
    
    def __init__(self, oView, iPlayerID = None):
        delegatebase.CDelegateBase.__init__(self, oView)
        if not iPlayerID:
            iPlayerID = hero.GetHeroID()
        
        self.m_iPlayerID = None
        self.SetPlayerID(iPlayerID)
        self.InitViewSignal()
        self.InitView()

    
    def InitView(self):
        self.RefreshBaseView()

    
    def InitViewSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_Event_HomeInfo_Part, self.OnHomeInfoPartEvent)

    
    def SetModelSignal(self, oPlayerDataMgr, bSignal):
        oModel = oPlayerDataMgr.GetHomeInfoDataMgr()
        oFunc = oModel.ssDisconnect
        if bSignal:
            oFunc = oModel.ssConnect
        
        oFunc(oModel.SS_UpdateHomeBaseInfo, self.OnUpdateHomeBaseInfo)

    
    def SetPlayerID(self, iPlayerID):
        iOldPlayerID = self.m_iPlayerID
        if self.m_iPlayerID == iPlayerID:
            return None
        
        if iOldPlayerID:
            oOldYardHomeData = self.GetYardHomeData(iOldPlayerID)
            self.SetModelSignal(oOldYardHomeData, False)
        
        self.m_iPlayerID = iPlayerID
        oCurYardHomeData = self.GetYardHomeData(iPlayerID)
        self.SetModelSignal(oCurYardHomeData, True)
        self.RefreshBaseView()

    
    def GetYardHomeData(self, iPlayerID = None):
        ''':rtype yardhome_oneplayer.CYardHome_OnePlayer'''
        oContext = yardinterface.GetYardHomeContext()
        oPlayerHomeData = oContext.GetYardHome(iPlayerID)
        return oPlayerHomeData

    
    def OnUpdateHomeBaseInfo(self, *args):
        self.RefreshBaseView()

    
    def OnHomeInfoPartEvent(self, sEvent):
        dEvent2Func = {
            'visitset': self.OnEvent_OpenVisitSetDlg,
            'yardrank': self.OnEvent_OpenYardRankDlg,
            'openpet': self.OnEvent_OpenPet,
            'myyard': self.OnEvent_GotoMyYard,
            'levelup': self.OnEvent_LevelUp,
            'resetfengshui': self.OnEvent_ResetFengShui }
        if sEvent not in dEvent2Func:
            return None
        
        oEvent = dEvent2Func[sEvent]
        oEvent()

    
    def OnEvent_OpenVisitSetDlg(self):
        if misc.IsInKuafuServer():
            return None
        
        netyardhome.C2SYardHome_Visitors()
        LOG('\xa5\xb4\xb6}\xb3X\xab\xc8\xb3]\xb8m')

    
    def OnEvent_OpenYardRankDlg(self):
        import dlgrank
        dlgrank.C2SShowRank(105)

    
    def OnEvent_OpenPet(self):
        netyardhome.C2SYardHome_OpenPet()
        LOG('\xa5\xb4\xb6}\xa9\xd0\xab\xce\xc3d\xab\xc7')

    
    def OnEvent_GotoMyYard(self):
        if not yardhomedefines.IsCanJumpMap():
            return None
        
        oCurYardHomeData = self.GetYardHomeData(self.m_iPlayerID)
        oHouseData = oCurYardHomeData.GetHomeInfoDataMgr().GetBaseInfo()
        if oHouseData.get('iNewHome', 0):
            netyardhome.C2SYardHome_BackYard()
        else:
            netyardhome.C2SYardHome_BackHome_Normal()

    
    def OnEvent_LevelUp(self):
        import netyard
        netyard.C2SRequestOpenUpHouse()

    
    def OnEvent_ResetFengShui(self):
        import dlgresetyardfengshui
        oCurYardHomeData = self.GetYardHomeData(self.m_iPlayerID)
        dBaseInfo = oCurYardHomeData.GetHomeInfoDataMgr().GetBaseInfo()
        iFengShui = dBaseInfo.get('iFengShui', 1)
        sFengShui = FENGSHUI_TYPE2_NAME.get(iFengShui, '')
        dBaseInfo['sFengShui'] = sFengShui
        dlgresetyardfengshui.ShowDlg(dBaseInfo)

    
    def RefreshBaseView(self):
        oCurYardHomeData = self.GetYardHomeData(self.m_iPlayerID)
        dBaseInfo = oCurYardHomeData.GetHomeInfoDataMgr().GetBaseInfo()
        iNewHome = dBaseInfo.get('iNewHome', 0)
        sName = dBaseInfo.get('sName', '\xaa\xb1\xaea\xa4\xa7\xaea')
        iHouseType = dBaseInfo.get('iHouseType', 0)
        iFengShui = dBaseInfo.get('iFengShui', 1)
        sFengShui = FENGSHUI_TYPE2_NAME.get(iFengShui, '')
        iLevel = dBaseInfo.get('iLevel', 0)
        iBeauty = dBaseInfo.get('iBeauty', 0)
        iRenqi = dBaseInfo.get('iRenqi', 0)
        \xb0\x8b\xb8nk = dBaseInfo.get('\xb0\x8b\xb8nk', 0)
        if \xb0\x8b\xb8nk == 0 or \xb0\x8b\xb8nk > 20:
            \xb0\x8b\xb8nk = '\xa5\xbc\xa4W\xba]'
        
        dRefresh = {
            'iNewHome': iNewHome,
            'sFengShui': sFengShui,
            'sName': sName,
            'sRank': '\xa1G' + str(\xb0\x8b\xb8nk),
            'bSelf': self.m_iPlayerID in (hero.GetHeroID(), hero.GetProp('m_MarryID')) }
        if iNewHome:
            sHouseType = HOUSE_TYPE2_NAME.get(iHouseType, '')
            sHoseDesc = '%s%s\xaf\xc5\xaex\xb0|' % (sHouseType, iLevel)
            if iHouseType == 1:
                pass
            dExtend = {
                'sHoseDesc': sHoseDesc,
                'sBeauty': str(iBeauty),
                'sRenqi': str(iRenqi),
                'bShowLeveLUpBtn': dRefresh['bSelf'] }
            dRefresh.update(dExtend)
        else:
            sHouseType = HOUSE_TYPE2_NAME.get(iHouseType, '')
            sHoseDesc = '%s \xaex\xb0|' % sHouseType
            dRefresh['sHoseDesc'] = sHoseDesc
        self.GetView().RefreshHomeInfoView(dRefresh)
