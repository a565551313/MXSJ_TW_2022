# pycdc 交叉复核产物 · script.fls entry 390
# co_filename(原始)='script/mxgame/appearance/delegate/delegateoutward/delegateappearanceaura.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_390.pyc (Python 2.5)

'''
================================================================================
\xd7\xf7\xd5\xdf: jiangweichao
\tdelegateappearanceaura\xa3\xba\xd1\xd5\xd6\xb5\xb9\xdd - \xb9\xe2\xbb\xb7\xbd\xc5\xd3\xa1\xb4\xfa\xc0\xed
================================================================================
'''
import appearancedelegatebase
import permission
MAX_COLOR_PLAN = 11

class CDelegateAura(appearancedelegatebase.CDelegateBase):
    
    def __init__(self, pView, pContext, iPage):
        appearancedelegatebase.CDelegateBase.__init__(self, pView, pContext)
        self.m_SelfPage = iPage
        self.InitSignal()
        self.InitView()
        self.InitModel()
        self.InitRoleView()

    
    def InitSignal(self):
        '''
\t\t\xb5\xf9\xa5U\xabH\xb8\xb9\xa6^\xbd\xd5
\t\t'''
        import mdpropitem
        oView = self.GetView()
        oView.ssConnect(oView.SS_VOpenAuraDlg, self.OnVOpenAuraDlg)
        oView.ssConnect(oView.SS_VCloseAuraDlg, self.OnVCloseAuraDlg)
        oView.ssConnect(oView.SS_RecordSelect, self.OnRecordSelect)
        oView.ssConnect(oView.SS_ChangeColorPlan, self.OnChangeColorPlan)
        oView.ssConnect(oView.SS_ClickPreview, self.OnPreview)
        oView.ssConnect(oView.SS_ClickBuy, self.OnBuy)
        oView.ssConnect(oView.SS_ClickDye, self.OnDye)
        oView.ssConnect(oView.SS_ClickWear, self.OnWear)
        oView.ssConnect(oView.SS_DefaultSelect, self.OnDefauleSelect)
        oView.ssConnect(oView.SS_SendGift, self.OnSendGift)
        oView.ssConnect(oView.SS_ClickItem, self.OnClickItem)
        oView.ssConnect(oView.SS_ClickResetDye, self.OnResetDye)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_OnRefreshTab, self.OnViewTabChange)
        oModel.ssConnect(oModel.SS_OneItemInfoChange, self.OnOneItemInfoChange)
        oModel.ssConnect(oModel.SS_AssemblyColorChange, self.OnAssemblyColorChange)
        oModel.ssConnect(oModel.SS_AssemblyDataInfoChange, self.OnAssemblyDataInfoChange)
        oModel.ssConnect(oModel.SS_ServChangeWearState, self.OnServChangeWearState)
        oPropItem = mdpropitem.GetModel()
        oPropItem.ssConnect(oPropItem.SS_UpdateBagChange, self.UpdateColorMaterial)

    
    def GetModel(self):
        import mdappearanceaura
        return mdappearanceaura.GetAuraMgr()

    
    def GetRoleModel(self):
        import mdheroshapedesc
        return mdheroshapedesc.GetRoleShapeDescMgr('CAppearanceShapeMainView')

    
    def InitView(self):
        oView = self.GetView()
        oView.InitView(self.m_SelfPage)

    
    def InitModel(self):
        import hero
        dDesc = hero.GetProp('m_Desc')
        lstAura = dDesc.get('aura', (1, 0))
        if isinstance(lstAura, int):
            if lstAura < 1:
                lstAura = 1
            
            lstAura = (lstAura, 0)
        
        iAura = lstAura[0]
        lstTrack = dDesc.get('track', (1, 0))
        if isinstance(lstTrack, int):
            if lstTrack < 1:
                lstTrack = 1
            
            lstTrack = (lstTrack, 0)
        
        iTrack = lstTrack[0]
        oModel = self.GetModel()
        bInit = oModel.GetInit()
        if not bInit:
            oModel.SetRecordSelect(1, iAura - 1)
            oModel.SetRecordSelect(2, iTrack - 1)
            oModel.SetCurColorPlans(lstAura[1], lstTrack[1])
            oModel.SetInit()
        
        oModel.OnRefreshTab()
        oRoleModel = self.GetRoleModel()
        iShape = oRoleModel.GetShape()
        if iShape == 0:
            oRoleModel.SetHeroShapeDesc()
        
        oRoleModel.UpdateShapeDesc()
        self.OnUpdateRole()

    
    def InitRoleView(self):
        oView = self.GetView()
        oView.InitRoleView()

    
    def OnRecordSelect(self, iSelect, iShape):
        '''
\t\t\xb0O\xbf\xfd\xbf\xef\xa4\xa4\xaa\xba\xbf\xef\xb6\xb5
\t\t:param iSelect: \xbf\xef\xb6\xb5\xaf\xc1\xa4\xde
\t\t:param iShape: \xbf\xef\xb6\xb5ID -1 \xac\xb0\xaa\xc5
\t\t:return:
\t\t'''
        iTab = self.m_SelfPage
        oModel = self.GetModel()
        iPreSelect = oModel.GetRecordSelectByTab(iTab)
        if iPreSelect != iSelect:
            dData = oModel.GetAssemblyColorByShape(iTab - 1, iShape)
            iColorPlan = 0
            if dData:
                iColorPlan = dData.get('color', 0)
            
            oModel.SetCurColorPlan(iTab, iColorPlan)
        
        oModel.SetRecordSelect(iTab, iSelect)
        self.UpdateOperationBtnState(iShape, iTab, iSelect)
        self.OnUpdateRole()
        oView = self.GetView()
        oView.RefreshBtnGive(iShape)

    
    def OnChangeColorPlan(self, iAdd):
        oModel = self.GetModel()
        iCurColorPlan = oModel.GetCurColorPlanByTab(self.m_SelfPage)
        iCurColorPlan += iAdd + MAX_COLOR_PLAN
        iCurColorPlan %= MAX_COLOR_PLAN
        oModel.SetCurColorPlan(self.m_SelfPage, iCurColorPlan)

    
    def OnPreview(self):
        import popupdefine
        import popupmgr
        oModel = self.GetModel()
        (iAuraIdx, iFootPrintIdx) = oModel.GetRecordSelectData()
        (iAuraColor, iFootPrintColor) = oModel.GetCurColorPlan()
        oRoleModle = self.GetRoleModel()
        blackSet = oRoleModle.GetDescKeyNotRange()
        aura = None if 'aura' in blackSet else [
            iAuraIdx + 1,
            iAuraColor]
        footprint = [
            iFootPrintIdx + 1,
            iFootPrintColor]
        horse = 'horse' in blackSet
        wing = 'wing' in blackSet
        args = [
            aura,
            footprint,
            horse,
            wing]
        popupmgr.GetPopupMgr().OpenUI(popupdefine.CAssemblyPreviewDlg, None, args)

    
    def OnBuy(self):
        import netxingzuo
        oModel = self.GetModel()
        idx = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
        func = [
            netxingzuo.CXingZuo.C2SBuyAura,
            netxingzuo.CXingZuo.C2SBuyTrack][self.m_SelfPage - 1]
        iShape = oModel.GetShapeIdByIdx(self.m_SelfPage, idx)
        func(iShape)

    
    def OnDye(self):
        import netxingzuo
        oModel = self.GetModel()
        idx = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
        iShape = oModel.GetShapeIdByIdx(self.m_SelfPage, idx)
        iType = self.m_SelfPage - 1
        sType = [
            'aura',
            'track'][iType]
        dType = {
            'aura': netxingzuo.CXingZuo.C2SDyeAuraColor,
            'track': netxingzuo.CXingZuo.C2SDyeTrackColor }
        oFunc = dType.get(sType)
        if oFunc:
            oFunc(iShape, 2)
        

    
    def OnResetDye(self):
        import netxingzuo
        iType = self.m_SelfPage - 1
        sType = [
            'aura',
            'track'][iType]
        dType = {
            'aura': netxingzuo.CXingZuo.C2SDyeAuraColor,
            'track': netxingzuo.CXingZuo.C2SDyeTrackColor }
        oModel = self.GetModel()
        idx = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
        iShape = oModel.GetShapeIdByIdx(self.m_SelfPage, idx)
        oFunc = dType.get(sType)
        if callable(oFunc):
            oFunc(iShape, 1)
        

    
    def OnWear(self):
        import netxingzuo
        oModel = self.GetModel()
        idx = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
        bWear = oModel.IsWearByIndex(self.m_SelfPage - 1, idx)
        iShape = oModel.GetShapeIdByIdx(self.m_SelfPage, idx)
        if bWear:
            func = [
                netxingzuo.CXingZuo.C2STakeOffAura,
                netxingzuo.CXingZuo.C2STakeOffTrack][self.m_SelfPage - 1]
        else:
            func = [
                netxingzuo.CXingZuo.C2SWearAura,
                netxingzuo.CXingZuo.C2SWearTrack][self.m_SelfPage - 1]
        func(iShape)

    
    def OnDefauleSelect(self, iShape):
        oView = self.GetView()
        oModel = self.GetModel()
        dInfo = oModel.GetItemDataByShape(self.m_SelfPage, iShape)
        idx = dInfo['idx']
        oView.DefaultSelect(idx)

    
    def UpdateOperationBtnState(self, iShape, iTab, iSelect):
        oView = self.GetView()
        oModel = self.GetModel()
        if iShape > -1:
            bWear = oModel.IsWearByIndex(iTab - 1, iSelect)
            bOwn = oModel.IsOwnByShape(iTab - 1, iShape)
            oView.UpdateOperationBtnsState(bWear, bOwn)
            oView.UpdateBtnPos(bOwn, iShape)
            dInfo = oModel.GetItemDataByShape(iTab, iShape)
            oView.UpdateAssemblyDetailInfo(bOwn, dInfo)
            self.UpdateColorMaterial()
        else:
            oView.UpdateOperationBtnsState(False, False)
            oView.UpdateBtnPos(False, iShape)

    
    def UpdateCurColorPlan(self):
        oView = self.GetView()
        oModel = self.GetModel()
        (iAuraColorPlan, iFootPrintColorPlan) = oModel.GetCurColorPlan()
        if self.m_SelfPage == 1:
            oView.UpdateColorPlan(iAuraColorPlan)
        elif self.m_SelfPage == 2:
            oView.UpdateColorPlan(iFootPrintColorPlan)
        
        self.OnUpdateRole()

    
    def OnUpdateRole(self):
        oView = self.GetView()
        if oView.GetShow():
            oModel = self.GetModel()
            oRoleModel = self.GetRoleModel()
            (iAuraIdx, iFootPrintIdx) = oModel.GetRecordSelectData()
            (iAuraColorPlan, iFootPrintColorPlan) = oModel.GetCurColorPlan()
            dDesc = { }
            if self.m_SelfPage == 1:
                dDesc['aura'] = [
                    iAuraIdx + 1,
                    iAuraColorPlan]
            elif self.m_SelfPage == 2:
                dDesc['track'] = [
                    iFootPrintIdx + 1,
                    iFootPrintColorPlan]
            
            oRoleModel.UpdateDesc(dDesc)
            oRoleModel.UpdateShapeDesc()
        

    
    def UpdateColorMaterial(self):
        import item
        oView = self.GetView()
        oModel = self.GetModel()
        iIndex = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
        iShape = oModel.GetShapeIdByIdx(self.m_SelfPage, iIndex)
        lMaterial = oModel.GetColorMaterial(iShape)
        lHave = []
        for iShape, iNum in lMaterial:
            lHave.append(item.GetItemQuantity(iShape))
        
        oView.UpdateColorMaterialInfo(lMaterial, lHave)

    
    def OnViewTabChange(self):
        '''
\t\t\xa4\xc1\xb4\xab\xbc\xd0\xc5\xd2\xa1A\xa8\xea\xb7s\xa9\xd2\xa6\xb3\xbc\xd0\xc5\xd2\xa4U\xaa\xba\xb3\xa1\xa5\xf3
\t\t'''
        oModel = self.GetModel()
        iTab = self.m_SelfPage
        iSelectIdx = oModel.GetRecordSelectByTab(iTab)
        oView = self.GetView()
        lstItem = oModel.GetItemsDataByIdx(iTab)
        dServData = oModel.GetAssemblysInfoByTabIndex(iTab)
        oView.SetItemDatas(lstItem, iSelectIdx)
        if dServData:
            for iShape, dData in dServData.iteritems():
                oView.UpdateItemState(iShape, dData)
            
        
        if lstItem:
            oView.RemoveFlash()
            for idx, dData in enumerate(lstItem):
                bWear = oModel.IsWearByIndex(iTab - 1, idx)
                iShape = dData.get('shape', 0)
                if bWear:
                    oView.SetFlash(bWear, iShape)
                    break
                    continue
            
        
        oModel.RefreshCurColorPlan()
        self.UpdateCurColorPlan()

    
    def OnOneItemInfoChange(self, iType, iShape):
        '''
\t\t\xb3\xe6\xa5\xf3\xb3\xa1\xa5\xf3\xc4\xdd\xa9\xca\xb5o\xa5\xcd\xa7\xef\xc5\xdc
\t\t:param iType: \xa5\xfa\xc0\xf4/\xb8}\xa6L
\t\t:param iShape: \xb3\xa1\xa5\xf3\xaf\xc1\xa4\xde
\t\t'''
        pass

    
    def OnServChangeWearState(self, bWear, iShape):
        oView = self.GetView()
        oView.UpdateOperationBtnsState(bWear, True)
        oView.UpdateBtnPos(True, iShape)
        if bWear:
            oView.SetFlash(bWear, iShape)
        else:
            oView.RemoveFlash()

    
    def OnAssemblyDataInfoChange(self, iType, iShape):
        '''
\t\t\xa7\xf3\xb7s\xbe\xd6\xa6\xb3\xaa\xac\xbaA/\xacV\xa6\xe2\xad\xc8
\t\t:param iType:
\t\t:param iShape:
\t\t:return:
\t\t'''
        oModel = self.GetModel()
        iTab = self.m_SelfPage
        if iTab == iType + 1:
            dStateData = oModel.GetAssemblyColorByShape(iType, iShape)
            oView = self.GetView()
            oView.UpdateItemState(iShape, dStateData)
            iSelect = oModel.GetRecordSelectByTab(iTab)
            if iSelect + 1 == dStateData.get('num', None):
                oModel.SetCurColorPlan(iTab, dStateData.get('color', 0))
                None(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, self.UpdateOperationBtnState, iShape, iTab, iSelect)
            
        

    
    def OnAssemblyColorChange(self):
        self.UpdateCurColorPlan()

    
    def OnSendGift(self):
        import netappearance
        import appearancedefine
        oModel = self.GetModel()
        idx = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
        iShape = oModel.GetShapeIdByIdx(self.m_SelfPage, idx)
        giftType = [
            appearancedefine.GIFT_TYPE_HALO,
            appearancedefine.GIFT_TYPE_FOOTPRINT][self.m_SelfPage - 1]
        netappearance.C2SOpenGiftDlg(giftType, iShape)

    
    def OnClickItem(self, iIndex):
        oView = self.GetView()
        (dItemInfo, oIcon) = oView.GetItemDataByIndex(iIndex)
        if dItemInfo:
            iTab = self.m_SelfPage
            sType = None if iTab == 1 else 'track'
            iShape = dItemInfo.get('shape', -1)
            if permission.CheckClickShowSource(sType, iShape):
                oView.SelectItemGrid(iIndex)
            
        

    
    def OnVOpenAuraDlg(self):
        oView = self.GetView()
        oRoleModel = self.GetRoleModel()
        oModel = self.GetModel()
        if self.m_SelfPage == 2:
            idx = oModel.GetRecordSelectData()[self.m_SelfPage - 1]
            iColor = oModel.GetCurColorPlanByTab(self.m_SelfPage)
            dDesc = {
                'track': [
                    idx + 1,
                    iColor] }
            oRoleModel.UpdateDesc(dDesc)
            oRoleModel.DelDescKeyNotRange('track')
        
        oRoleModel.UpdateShapeDesc()
        oView.SetShow(True)

    
    def OnVCloseAuraDlg(self):
        oView = self.GetView()
        oView.SetShow(False)
        oRoleModel = self.GetRoleModel()
        if self.m_SelfPage == 2:
            oRoleModel.AddDescKeyNotRange('track')
            oRoleModel.UpdateShapeDesc()
