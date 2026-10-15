# pycdc 交叉复核产物 · script.fls entry 1068
# co_filename(原始)='script/mxgame/makeequip/delegate/dgtconvenientpurchase.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1068.pyc (Python 2.5)

import autofindpath
import builddefine
import delegatebase
import getitemaccessdata
import itemdefine
import permission
import mdconvenientpurchase
import opendlgdata
import usermacro

class CGetAccessDlgDelegate(delegatebase.CDelegateBase):
    '''
\t\xa7\xd6\xb1\xb6\xc0\xf2\xa8\xfa
\t'''
    
    def __init__(self, oView):
        self.m_dGetItem = { }
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def GetView(self):
        ''':rtype: dlggetaccess.CGetAccessDlg'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickAItem, self.OnClickAItem)
        oView.ssConnect(oView.SS_SetItemShape, self.OnSetItemShape)
        oView.ssConnect(oView.SS_CloseWindow, self.OnCloseWindow)
        dData = mdconvenientpurchase.GetConvenientPurchaseMgr().GetNowNeedItem()
        if dData:
            self.SetNeedItem(builddefine.TYPE_NEED_ITEM, dData)
        

    
    def SetGetItemData(self, dData):
        self.m_dGetItem = dData

    
    def GetGetItemData(self):
        return self.m_dGetItem

    
    def SetNeedItem(self, sType, dNeedItemData):
        oView = self.GetView()
        if sType != builddefine.TYPE_NEED_ITEM:
            oView.ClearAccessItem()
            return None
        
        iNeedID = getitemaccessdata.GetItemID(dNeedItemData[builddefine.KEY_NEED_SHAPE], dNeedItemData[builddefine.KEY_NEED_ITEM_CLASS], dNeedItemData[builddefine.KEY_NEED_ITEM_LV])
        LOG_DEBUG('\xaa\xab\xab~\xac\xdd\xac\xdd', iNeedID, dNeedItemData)
        iNum = max(dNeedItemData[builddefine.KEY_NEED_AMOUNT], dNeedItemData.get(builddefine.KEY_NEED_AMOUNT_SUM, 0))
        oView.SetShowItem(dNeedItemData[builddefine.KEY_NEED_SHAPE], iNum)
        dGetItemList = getitemaccessdata.GetItemGetWay(iNeedID)
        iNeedGold = dNeedItemData[builddefine.KEY_NEED_GOLD]
        iNeedMXB = dNeedItemData[builddefine.KEY_NEED_MXB]
        iNeedCash = dNeedItemData[builddefine.KEY_NEED_CASH]
        if not dGetItemList and iNeedGold == 0 and iNeedMXB == 0 and iNeedCash:
            oView.ClearAccessItem()
            return None
        
        iKeyData = { }
        if iNeedGold != 0:
            sTxt = '%d#956\xa5@\xac\xc9\xb0^\xc4m\xc1\xca\xb6R' % iNeedGold
            oAccessItem = oView.CreateAccessItem('SG')
            oAccessItem.SetText(sTxt)
        
        if iNeedMXB != 0:
            sTxt = '%d#969\xb9\xda\xb7Q\xb9\xf4\xc1\xca\xb6R' % iNeedMXB
            oAccessItem = oView.CreateAccessItem('MXB')
            oAccessItem.SetText(sTxt)
        
        if iNeedCash != 0:
            sTxt = '%d#970\xb2{\xaa\xf7\xc1\xca\xb6R' % iNeedCash
            oAccessItem = oView.CreateAccessItem('CASH')
            oAccessItem.SetText(sTxt)
        
        for dData in dGetItemList:
            iKeyData[dData['sName']] = dData
            oAccessItem = oView.CreateAccessItem(dData['sName'])
            oAccessItem.SetText(dData['sName'])
        
        iKeyData['dItemData'] = dNeedItemData
        self.SetGetItemData(iKeyData)

    
    def OnSetItemShape(self, iShape, sName):
        oMgr = mdconvenientpurchase.GetConvenientPurchaseMgr()
        oMgr.SetItemShape(iShape, sName)

    
    def OnCloseWindow(self):
        oMgr = mdconvenientpurchase.GetConvenientPurchaseMgr()
        oMgr.SetItemShape(0, '')

    
    def OnClickAItem(self, sKey):
        import netopenui
        import iteminterface
        import misc
        dData = self.GetGetItemData()
        dItemData = dData['dItemData']
        iShape = dItemData[builddefine.KEY_NEED_SHAPE]
        iClass = dItemData[builddefine.KEY_NEED_ITEM_CLASS]
        iLv = dItemData[builddefine.KEY_NEED_ITEM_LV]
        iSG = dItemData[builddefine.KEY_NEED_GOLD]
        iMXB = dItemData[builddefine.KEY_NEED_MXB]
        iAmount = dItemData[builddefine.KEY_NEED_AMOUNT]
        iAmountType = dItemData[builddefine.KEY_NEED_AMOUNT_TYPE]
        iAmountSum = dItemData[builddefine.KEY_NEED_AMOUNT_SUM]
        if sKey == 'SG':
            netopenui.C2SItemAccessDlgBuy(iShape, iLv, iClass, iSG, iAmount, iAmountType, iAmountSum, iPriceType = 1)
        elif sKey == 'MXB':
            netopenui.C2SItemAccessDlgBuy(iShape, iLv, iClass, iMXB, iAmount, iAmountType, iAmountSum, iPriceType = 0)
        elif sKey == 'CASH':
            netopenui.C2SItemAccessDlgBuy(iShape, iLv, iClass, iMXB, iAmount, iAmountType, iAmountSum, iPriceType = 2)
        elif sKey == '\xa5X\xb0\xe2\xb1H\xb0\xe2\xa5d' and misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xb8\xf3\xaaA\xb5L\xaak\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
            return None
        elif sKey == '\xb1H\xb0\xe2\xa4\xa4\xa4\xdf':
            self.OpenConsignMall(dData[sKey]['iGetWayID'])
        else:
            dGotoData = dData[sKey]
            sGetWayKey = dGotoData['sGetWayKey']
            iGetWayID = dGotoData['iGetWayID']
            if misc.IsNewBuildEquipment():
                if iGetWayID == 1006:
                    sGetWayKey = '\xb5\xa1\xa4f'
                    iGetWayID = '\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf'
                
            
            if sGetWayKey == '\xb5\xa1\xa4f':
                if '\xba\xeb\xab~\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf' in iGetWayID:
                    self.SetTJBuyItem()
                elif '\xa5\xe6\xa9\xf6\xa4\xa4\xa4\xdf' in iGetWayID:
                    self.SetTradeCenterBuyItem()
                elif '\xc0\xb0\xac\xa3\xb0\xd3\xa9\xb1' in iGetWayID:
                    self.OpenGroupShop(iShape)
                elif '\xa4l\xa4k\xb0\xd3\xab\xb0' in iGetWayID:
                    self.OpenChildStore(iShape, 1)
                elif '\xa4l\xa4k\xb0\xf6\xbei\xb0\xd3\xab\xb0' in iGetWayID:
                    self.OpenChildStore(iShape, 2)
                elif '\xad\xad\xae\xc9\xb3\xc3\xa8\xe3\xb0\xd3\xab\xb0' in iGetWayID:
                    self.OpenYardFurStore(iShape, 2)
                elif '\xc1\xeb\xb3y' in iGetWayID:
                    self.OpenDZBag()
                elif '\xa4\xe9\xb5{' in iGetWayID:
                    self.OpenSceduleDlg()
                elif iShape in getitemaccessdata.SHAPE2STOREID:
                    iShape = getitemaccessdata.SHAPE2STOREID[iShape]
                
                if iShape in [
                    itemdefine.ID_ITEM_EQUIP_BOOK,
                    itemdefine.ID_ITEM_EQUIP_IRON]:
                    iGetWayID = '%s,%s,%s,%s' % (iGetWayID, iShape, iClass, iLv)
                
                if iteminterface.IsEquip(iShape):
                    iGetWayID = '%s,%s,%s,%s' % (iGetWayID, iShape, iClass, iLv)
                else:
                    iGetWayID = '%s,%s' % (iGetWayID, iShape)
                opendlgdata.OpenDlg(iGetWayID)
            elif sGetWayKey == '\xa6a\xc2I':
                iPlaceID = iGetWayID
                dPlaceData = getitemaccessdata.GetPlaceInfo(iPlaceID)
                if not dPlaceData:
                    return None
                
                autofindpath.AutoFind(dPlaceData['sScene'], dPlaceData['tPos'], sNpcName = dPlaceData['sNpcName'])
            
        if not self.DoNotCloseAfterBuy(sKey, iShape):
            self.GetView().CloseWindow()
        

    
    def SetTJBuyItem(self):
        import dlgtjtradecenter
        import dlgtradecentermainframe
        oMgr = mdconvenientpurchase.GetConvenientPurchaseMgr()
        (iShape, sName) = oMgr.GetItemShape()
        dlgtradecentermainframe.SetTradeCenterTopmost()
        if iShape:
            dlgtjtradecenter.OpenDlgWi\xbf\xa3\x98\xa3\xaa\xbb\xae(iShape, sName)
        

    
    def DoNotCloseAfterBuy(self, sKey, iShape):
        if sKey in ('SG', 'MXB'):
            pass
        return iShape in (73287, 25751, 25755, 25759, 25763, 25767)

    
    def SetTradeCenterBuyItem(self):
        import dlgtradecenter_market
        import misc
        oMgr = mdconvenientpurchase.GetConvenientPurchaseMgr()
        (iShape, sName) = oMgr.GetItemShape()
        if sName:
            dlgtradecenter_market.SetClientNeed(sName)
        
        if misc.IsNewBuildEquipment():
            import netnpc
            netnpc.C2STradeCenterEnterShop(1)
        else:
            import netcommon
            netcommon.C2SQuickBuy(102)

    
    def OpenGroupShop(self, iShape):
        import groupcontext
        import groupdefines
        import usermacro
        import hero
        sOrg = hero.GetProp('sOrg', None)
        if not sOrg:
            usermacro.PROMPT_MSG('\xa7A\xc1\xd9\xa8S\xa6\xb3\xa5[\xa4J\xc0\xb0\xac\xa3')
            return None
        
        pGroupContext = groupcontext.Get()
        dExtendData = {
            'page': groupdefines.E_WAREFAREPAGE_SHOP,
            'extend': {
                'iSelectShape': iShape } }
        pGroupContext.OpenGroupDlg(groupdefines.E_GROUPPAGE_WELFARE, dExtendData)

    
    def OpenChildStore(self, iShape, iOpenType):
        '''
\t\t:param iShape: \xaa\xab\xab~shape
\t\t:param iOpenType: \xa5\xb4\xb6}\xb3~\xae| 1-\xbfW\xa5\xdf\xb0\xd3\xab\xb0 2-\xb0\xf6\xbei\xb0\xd3\xab\xb0
\t\t:return:
\t\t'''
        import netnewchild
        netnewchild.C2SChildStoreOpen(iShape, iOpenType)

    
    def OpenSceduleDlg(self):
        import dlgschedule
        import dlgnewschedule
        if permission.IsNewSchedule():
            dlgnewschedule.ShowSwitch()
        else:
            dlgschedule.SwitchSchedule()

    
    def OpenDZBag(self):
        import makeequipctrl
        if makeequipctrl.GetMakeEquipDlgCtrl().IsOpenMakeEquipDlg():
            makeequipctrl.GetMakeEquipDlgCtrl().GetEquipDlg().ShowBag()
        
        usermacro.PROMPT_MSG('\xbd\xd0\xb1q\xa5\xaa\xb0\xbc\xadI\xa5]\xa4\xc0\xad\xb6\xbf\xef\xbe\xdc\xa9\xd2\xbb\xdd\xa7\xf7\xae\xc6')

    
    def OpenYardFurStore(self, iShape, iOpenType):
        import netyard
        netyard.C2SYardOpenShop(iOpenType)

    
    def OpenConsignMall(self, sKey):
        import dlgconsignmall
        import consignmalldefines
        dlgconsignmall.ShowConsignmallByType(consignmalldefines.SHELFNAME2TYPE.get(sKey, consignmalldefines.ZAHUO_SHELF_ID))
