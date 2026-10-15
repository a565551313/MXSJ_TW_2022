# pycdc 交叉复核产物 · script.fls entry 875
# co_filename(原始)='script/mxgame/consignmentsalecenter/delegate/dgtconsignmallhuoli.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_875.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/10/26 10:29
\xd7\xf7\xd5\xdf: jj
\xce\xc4\xbc\xfe: dgtconsignmallhuoli
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import autofindpath
import commondialog
import consignmalldefines
import consignmallhuolidefines
import consignmallutil
import cookdata
import delegatebase
import dlgreplacesale
import gamemoduledefines
import hero
import mapdata
import mdconsignmallhuoli
import misc
import netplayer
import netsale
import salemgr
import stopgamemoduleinterface
import timer
import usermacro

class CConsignmallHuoliDelegate(delegatebase.CDelegatePaginationBase):
    
    def Init(self):
        self.m_oPitchTimer = None
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickLocation, self.OnClickLocation)
        oView.ssConnect(oView.SS_ClickSale, self.OnClickSale)
        oView.ssConnect(oView.SS_ClickReplace, self.OnClickReplace)
        oView.ssConnect(oView.SS_ClickSetname, self.OnClickSetname)
        oView.ssConnect(oView.SS_Active, self.OnActive)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UpdateHuoliAndTime, self.OnUpdateHuoliAndTime)
        oModel.ssConnect(oModel.SS_TitleChange, self.OnUpdateTitle)
        oModel.ssConnect(oModel.SS_TrySale, self.OnTrySale)
        oModel.ssConnect(oModel.SS_SaleStateChange, self.OnUpdateSaleState)
        oModel.ssConnect(oModel.SS_LocationChange, self.OnUpdateLocation)
        oModel.ssConnect(oModel.SS_UpdateRemainingTime, self.OnUpdateRemainingTime)
        oMgr = salemgr.GetSaleMgr()
        oMgr.ssConnect(oMgr.SS_BuyFMInfoChg, self.OnShelfInfoChange)
        oMgr.ssConnect(oMgr.SS_BuyCookInfoChg, self.OnShelfInfoChange)
        oMgr.ssConnect(oMgr.SS_BuyMakeInfoChg, self.OnShelfInfoChange)
        oMgr.ssConnect(oMgr.SS_BuyFurnitrueInfoChg, self.OnShelfInfoChange)
        oMgr.ssConnect(oMgr.SS_BuyCraftInfoChg, self.OnShelfInfoChange)
        self.InitTitle()
        self.OnUpdateHuoliAndTime()
        self.OnUpdateRemainingTime()
        self.OnUpdateSaleState()

    
    def GetModel(self):
        return mdconsignmallhuoli.GetSellHuoliModel()

    
    def GetView(self):
        ''':rtype: dlgconsignmallhuoli.CConsignmallHuoliDialog'''
        return delegatebase.CDelegatePaginationBase.GetView(self)

    
    def InitTitle(self):
        self.GetView().CreateListEdit(misc.Functor(self.GetTitleList))
        self.SetDefaultTitle()

    
    def GetTitleList(self):
        sTitleList = consignmallutil.GetTitleList()
        return sTitleList

    
    def SetDefaultTitle(self):
        oModel = self.GetModel()
        sTitleList = self.GetTitleList()
        bHasChangeTitle = False
        for sTitle in sTitleList:
            if sTitle != consignmalldefines.DEFAULT_TITLE:
                bHasChangeTitle = True
                break
                continue
        
        if bHasChangeTitle:
            oModel.SetTitle(sTitleList[0])
            return None
        
        iSkillTypeList = []
        (lstCook, iMakePrice, iCraftPrice, iFurnPrice, dFMPrice) = self.GetSkillSaleState()
        if lstCook:
            iSkillTypeList.append(consignmallhuolidefines.TYPE_COOK)
        
        if iMakePrice:
            iSkillTypeList.extend((consignmallhuolidefines.TYPE_MAKE1, consignmallhuolidefines.TYPE_MAKE2, consignmallhuolidefines.TYPE_MAKE3))
        
        if iCraftPrice:
            iSkillTypeList.append(consignmallhuolidefines.TYPE_CRAFT)
        
        if iFurnPrice:
            iSkillTypeList.append(consignmallhuolidefines.TYPE_FURNITURE)
        
        if dFMPrice:
            iSkillTypeList.append(consignmallhuolidefines.TYPE_FM)
        
        (sName, iID) = self.GetView().GetDefaultName(iSkillTypeList)
        oModel.SetTitle(sName)
        if iID:
            consignmallutil.SaveData('', [
                iID], True)
        

    
    def OnActive(self, bActive):
        if bActive:
            netplayer.C2SGetSaleName()
        
        self.SetPitchTimerActive(bActive)

    
    def OnShelfInfoChange(self, *args):
        self.SetDefaultTitle()

    
    def OnClickLocation(self):
        tMapInfo = self.GetModel().GetLocation()
        if tMapInfo:
            (iSceneID, iX, iY) = tMapInfo
            autofindpath.AutoFind(mapdata.GetSceneName(iSceneID), (iX, iY))
        

    
    def OnClickSale(self):
        LOG_DEBUG('OnClickSale')
        
        oCloseFunc = lambda dlg: netsale.C2SPlayerClose()
        commondialog.ShowMessageBox('\xa5\xbf\xa6b\xb4\xc0\xa8\xad\xc2\\\xc5u\xa1A\xacO\xa7_\xbdT\xbb{\xa6\xac\xc5u?', ('\xbdT\xbb{', '\xa8\xfa\xae\xf8'), (oCloseFunc, None))

    
    def OnClickReplace(self):
        LOG_DEBUG('OnClickReplace')
        oMgr = salemgr.GetSaleMgr()
        if not oMgr.IsCanSale():
            usermacro.PROMPT_MSG('\xbd\xd0\xbf\xef\xbe\xdc\xa4W\xac[\xa7\xde\xaf\xe0\xab\xe1\xa6A\xb6}\xa9l\xc2\\\xc5u')
            return None
        
        sTitle = self.GetView().GetTitleText()
        (bValid, sReason) = consignmallutil.IsTitleValid(sTitle)
        if not bValid:
            usermacro.PROMPT_MSG(sReason)
            return None
        
        self.GetModel().SetTitle(sTitle)
        dlgreplacesale.SetForceShowSet(False)
        netplayer.C2SGetReplaceSaleTime()

    
    def CheckIsCanSetName(self):
        if stopgamemoduleinterface.CheckStop(gamemoduledefines.GAMEMODULE_SALENAME):
            return False
        
        return True

    
    def OnClickSetname(self):
        if self.CheckIsCanSetName():
            self.GetView().ShowSetNameDlg(None, misc.Functor(self.OnCommitSetName))
        

    
    def OnUpdateHuoliAndTime(self):
        oModel = self.GetModel()
        iLeftHuoli = oModel.GetLeftHuoli()
        iLeftTime = oModel.GetLeftStoreTime()
        self.GetView().SetSaleTime(iLeftTime, iLeftHuoli)
        self.GetRemoteRemainingTime()

    
    def OnUpdateRemainingTime(self):
        if self.GetIsInSale():
            iTime = self.GetModel().GetRemainingTime()
            self.GetView().SetRemainingTime(misc.Int2TimeStr(iTime))
        else:
            self.GetView().SetRemainingTime('\xa5\xbc\xc2\\\xc5u')

    
    def OnUpdateTitle(self):
        self.GetView().SetTitle(self.GetModel().GetTitle())

    
    def OnUpdateLocation(self):
        tMapInfo = self.GetModel().GetLocation()
        bInSale = self.GetIsInSale()
        if tMapInfo and bInSale:
            (iSceneID, iX, iY) = tMapInfo
            self.GetView().SetSaleLocation(iSceneID, iX, iY)
        

    
    def OnTrySale(self, bCheckName = True):
        if self.GetIsInSale():
            usermacro.PROMPT_MSG('\xb1z\xa4w\xb8g\xa6b\xc2\\\xc5u\xa4F')
            return None
        
        oView = self.GetView()
        sTitle = oView.GetTitleText()
        if bCheckName:
            if not oView.IsValidName(sTitle):
                self.GetView().ShowSetNameDlg(misc.Functor(self.OnTrySale, False), misc.Functor(self.OnCommitSetName))
                return None
            
        
        oMgr = salemgr.GetSaleMgr()
        if not oMgr.IsCanSale():
            usermacro.PROMPT_MSG('\xa8S\xa6\xb3\xa5\xf4\xa6\xf3\xa5i\xa5H\xa5X\xb0\xe2\xaa\xba\xaa\xab\xab~\xa9\xce\xac\xa1\xa4O\xa4\xa3\xb0\xf7\xa1A\xa4\xa3\xaf\xe0\xc2\\\xc5u')
            return None
        
        (bValid, sReason) = consignmallutil.IsTitleValid(sTitle)
        if not bValid:
            usermacro.PROMPT_MSG(sReason)
            return None
        
        self.GetModel().SetTitle(sTitle)
        import saleaddonmgr
        (_, _, saleaddonmgr.g_bDragLabelInvalid) = saleaddonmgr.GetValidPosForHero()
        oHero = hero.GetHeroObject()
        if oHero:
            (iValidX, iValidY) = oHero.GetPos()
        else:
            (iValidX, iValidY) = (0, 0)
        (lstCook, iMakePrice, iCraftPrice, iFurnPrice, dFMPrice) = self.GetSkillSaleState(bBanInShelfCheck = True)
        self.OnRequestSale(iValidX, iValidY, sTitle, lstCook, iMakePrice, iCraftPrice, iFurnPrice, dFMPrice)

    
    def OnRequestSale(self, iX, iY, sTitle, cooks, makeHuoLi, craftHuoLi, furnPrice, fmPrice):
        import map
        import netsale
        if map.GetGameMapObject():
            (iServerX, iServerY) = map.GetGameMapObject().ClientPos2ServerPos(iX, iY)
        else:
            (iServerX, iServerY) = (0, 0)
        netsale.C2SPlayerSale(iServerX, iServerY, sTitle, [], [], cooks, makeHuoLi, craftHuoLi, furnPrice, fmPrice)
        import walker
        import world
        obj = world.GetObj(hero.g_ID)
        if obj:
            walker.g_SaleLook[obj.GetSaleID()] = (walker.SaleType.Default, True)
            obj.CheckSale()
        

    
    def OnCommitSetName(self, sName):
        if sName:
            self.GetModel().SetTitle(sName)
            consignmallutil.SaveTitle(sName)
        

    
    def OnUpdateSaleState(self):
        self.GetView().SetSaleState(self.GetIsInSale())
        self.GetRemoteRemainingTime()

    
    def GetIsInSale(self):
        import dlgsale
        return dlgsale.IsSale()

    
    def GetSkillSaleState(self, bBanInShelfCheck = False):
        oMgr = salemgr.GetSaleMgr()
        dFMPrice = { }
        dAllInfo = oMgr.GetSaleInfo(salemgr.SALETYPE_FM)
        if dAllInfo:
            for dInfo in dAllInfo.itervalues():
                if dInfo.get('iIsShelf', 0) or bBanInShelfCheck:
                    iFMPrice = dInfo.get('iFMPrice', 0)
                    if iFMPrice:
                        dFMPrice[dInfo['iFMPos']] = iFMPrice
                    
                iFMPrice
            
        
        lstCook = []
        dAllInfo = oMgr.GetSaleInfo(salemgr.SALETYPE_COOKING, { }).get(salemgr.ID_COOK)
        if dAllInfo:
            for dInfo in dAllInfo.itervalues():
                if (dInfo.get('iIsShelf', 0) or bBanInShelfCheck) and dInfo.get('iCookPacketPrice', 0):
                    dData = cookdata.GetData(dInfo.get('iCookID', 0))
                    if 'base_lv' not in dData:
                        continue
                    
                    while None:
                        continue
                
        dInfo = oMgr.GetSaleInfo(salemgr.SALETYPE_MAKE)
        if dInfo:
            if dInfo.get('iIsShelf', 0) or bBanInShelfCheck:
                iMakePrice = dInfo.get('price', 0)
            else:
                iMakePrice = 0
        dInfo = oMgr.GetSaleInfo(salemgr.SALETYPE_FURNISH)
        if dInfo:
            if dInfo.get('iIsShelf', 0) or bBanInShelfCheck:
                iFurnPrice = dInfo.get('iFurnitruePrice', 0)
            else:
                iFurnPrice = 0
        dInfo = oMgr.GetSaleInfo(salemgr.SALETYPE_CRAFT)
        if dInfo:
            if dInfo.get('iIsShelf', 0) or bBanInShelfCheck:
                iCraftPrice = dInfo.get('iCraftPrice', 0)
            else:
                iCraftPrice = 0
        return (lstCook, iMakePrice, iCraftPrice, iFurnPrice, dFMPrice)

    
    def SetPitchTimerActive(self, bActive):
        if bActive and not (self.m_oPitchTimer):
            self.m_oPitchTimer = timer.Timer(1, self.RefreshRemainingTime, -1, self)
        elif not bActive and self.m_oPitchTimer:
            self.m_oPitchTimer.Release()
            self.m_oPitchTimer = None
        

    
    def GetRemoteRemainingTime(self):
        netsale.C2SGetRemainingTime()

    
    def RefreshRemainingTime(self):
        oModel = self.GetModel()
        iTime = oModel.GetRemainingTime()
        if iTime > 0:
            iTime -= 1
        else:
            iTime = 0
        oModel.SetRemainingTime(iTime)
