# pycdc 交叉复核产物 · script.fls entry 2720
# co_filename(原始)='script/mxgame/makeequip/delegate/dgttransformattr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2720.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/25 14:16
\xd7\xf7\xd5\xdf: sanli
\xce\xc4\xbc\xfe: dgttransformattr
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import delegatebase
import item
import mdpropitem
import mdtransformattr
import usermacro
import transformattrdefine

class CTransformAttrDelegate(delegatebase.CDelegateBase):
    
    def Init(self):
        self.m_DelayTimer = None
        self.m_DelayCount = 0
        self.EditInit()
        self.RefreshItemList()

    
    def EditInit(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_CLICKEQUIP, self.OnClickEquip)
        oView.ssConnect(oView.SS_CLICKEQUIPTAB, self.RefreshEquipList)
        oView.ssConnect(oView.SS_CLICKBAGTAB, self.RefreshItemList)
        oView.ssConnect(oView.SS_ClickCurAttr, self.OnClickCurAttr)
        oView.ssConnect(oView.SS_TRANSFORMAttr, self.OnTransformAttr)
        oView.ssConnect(oView.SS_ClickMode, self.OnClickMode)
        oView.ssConnect(oView.SS_ClickAttr, self.OnClickAttr)
        oView.ssConnect(oView.SS_TransformAttrShow, self.OnTransformAttrShow)
        oView.ssConnect(oView.SS_PutDownAllEquip, self.OnPutDownEquip)
        oView.ssConnect(oView.SS_ONTRANSBTNCLICK, self.OnTransBtnClick)
        oView.ssConnect(oView.SS_ShowTips, self.OnShowTips)
        oMgr = self.GetModel()
        oMgr.ssConnect(oMgr.SS_ShowAttrInfo, self.ShowCurrentAttr)
        oMgr.ssConnect(oMgr.SS_ShowSelectAttrInfo, self.ShowCanTransformAttr)
        oMgr.ssConnect(oMgr.SS_UpdateEquip, self.UpdateItem)
        oModel = mdpropitem.GetModel()
        oModel.ssConnect(oModel.SS_BAG_ADD_ITEM, self.OnItemAdd)
        oModel.ssConnect(oModel.SS_BAG_DEL_ITEM, self.OnItemDel)
        oModel.ssConnect(oModel.SS_BAG_ITEM_NUM_CHANGE, self.OnItemNumChange)

    
    def GetView(self):
        ''':rtype: dlgtransformattr.CTransformAttrDlg'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        return mdtransformattr.GetTransformAttrMgr()

    
    def OnShowTips(self):
        iRYOwnNum = item.GetItemNum(transformattrdefine.RUYUSHAPE)
        oMgr = mdtransformattr.GetTransformAttrMgr()
        iMode = oMgr.GetSelectMode()
        if iMode == transformattrdefine.MODE_RANDOM:
            iRYNeedNum = oMgr.GetRandomRYNum()
        else:
            iRYNeedNum = oMgr.GetCertainRYNum()
        if iRYOwnNum > iRYNeedNum:
            iTransNum = 0
            iCostNum = iRYNeedNum
        else:
            iTransNum = iRYNeedNum - iRYOwnNum
            iCostNum = iRYOwnNum
        oView = self.GetView()
        oView.CreateTips(iTransNum, iCostNum)

    
    def ShowCurrentAttr(self):
        oView = self.GetView()
        oMgr = self.GetModel()
        tAttrList = oMgr.GetAttrList()
        oView.ClearBtnState()
        oView.ClearMode()
        self.ShowNeedRYNum()
        oView.ShowCurrentAttr(tAttrList)
        if oMgr.GetSelectAttr() and oMgr.GetSelectMode():
            self.ShowCanTransformAttr()
        else:
            oView.ShowRightAttr(False)
        oView.EnableAttr()

    
    def ShowCanTransformAttr(self):
        oMgr = mdtransformattr.GetTransformAttrMgr()
        if oMgr.GetSelectMode() == 1:
            return None
        
        oView = self.GetView()
        oView.ShowRightAttr(True)
        if not oMgr.GetSelectMode() or not oMgr.GetSelectAttr():
            oView.ShowRightAttr(False)
        
        oMgr = mdtransformattr.GetTransformAttrMgr()
        sSelectAttr = oMgr.GetSelectAttr()
        tAttrList = oMgr.GetAttrList()
        sTmpAttrList = oMgr.GetHasAttrList()
        oView = self.GetView()
        oView.ShowCanTransformAttr(sSelectAttr, tAttrList, sTmpAttrList)

    
    def OnTransBtnClick(self):
        oMgr = self.GetModel()
        oMgr.SetUseSGState(not oMgr.GetUseSGState())
        self.GetView().SetAutoCost(oMgr.GetUseSGState())
        self.ShowNeedRYNum()

    
    def CheckEquipOnWear(self, iPos):
        return iPos in xrange(transformattrdefine.EQUIP_START_POS, transformattrdefine.EQUIP_END_POS + 1)

    
    def OnClickEquip(self, iItemID, iIndex):
        oMgr = self.GetModel()
        oView = self.GetView()
        oItem = item.GetItem(iItemID)
        if not oItem:
            return None
        
        iEquip = oMgr.GetEquipID()
        oEquip = item.GetItem(iEquip)
        if oEquip == oItem:
            oMgr.SetEquipID(0)
            oView.ClearEquip()
        else:
            oMgr.SetEquipID(iItemID)
            oMgr.RequestAttrInfo()
            oView.ShowEquip(iIndex)

    
    def OnPutDownEquip(self):
        oMgr = self.GetModel()
        oView = self.GetView()
        oMgr.SetEquipID(0)
        oView.ClearEquip()
        oView.ClearSelect()

    
    def CheckEquip(self, iShape):
        import itemdata
        if itemdata.IsType(iShape, 'equip'):
            return True
        
        return False

    
    def OnItemChange(self):
        oMgr = self.GetModel()
        oView = self.GetView()
        iShowType = oMgr.GetShowType()
        if iShowType == transformattrdefine.TYPE_BAG:
            self.RefreshItemList()
        else:
            self.RefreshEquipList()
        if oMgr.GetEquipID():
            self.ShowNeedRYNum()
        

    
    def OnItemNumChange(self, iItemID, iOldNum, iNewNum):
        self.ShowNeedRYNum()

    
    def OnTransformAttrShow(self, bShow):
        oMgr = self.GetModel()
        if bShow:
            if oMgr.GetEquipID():
                oMgr.RequestAttrInfo()
            
        

    
    def OnClickCurAttr(self, iType):
        oMgr = self.GetModel()
        if not iType:
            oMgr.SetSelectAttr('')
            return None
        
        tAttrList = oMgr.GetAttrList()
        if iType - 1 >= len(tAttrList):
            return None
        
        iAttr = tAttrList[iType - 1][0]
        sAttr = mdtransformattr.GetAttrDesc(iAttr)
        oMgr.SetSelectAttr(sAttr)

    
    def OnClickMode(self, iType):
        oMgr = self.GetModel()
        oView = self.GetView()
        if not iType:
            oMgr.SetSelectMode(iType)
            self.ShowNeedRYNum()
            return None
        
        oMgr.SetSelectMode(iType - 6)
        iMode = oMgr.GetSelectMode()
        self.ShowNeedRYNum()
        self.RefreshCanTranAttr(iMode)

    
    def RefreshCanTranAttr(self, iMode):
        oView = self.GetView()
        if iMode == 1:
            oView.ShowRightAttr(False)
        else:
            self.ShowCanTransformAttr()
            oView.ShowRightAttr(True)

    
    def ShowNeedRYNum(self):
        import hero
        oMgr = mdtransformattr.GetTransformAttrMgr()
        iRYOwnNum = item.GetItemNum(transformattrdefine.RUYUSHAPE)
        iMode = oMgr.GetSelectMode()
        oView = self.GetView()
        if iMode == transformattrdefine.MODE_RANDOM:
            iRYNeedNum = oMgr.GetRandomRYNum()
        else:
            iRYNeedNum = oMgr.GetCertainRYNum()
        bNeedShow = iRYNeedNum > iRYOwnNum
        bAutoCost = oMgr.GetUseSGState()
        if bAutoCost and bNeedShow:
            if iMode == transformattrdefine.MODE_RANDOM:
                iMXBNeedNum = oMgr.GetNeedMXBRandom()
            else:
                iMXBNeedNum = oMgr.GetNeedMXBCertain()
            oView.ShowNeedMXB(hero.GetProp('m_ShenWuBi', 0), iMXBNeedNum)
            return None
        
        oView.ShowNeedRYNum(iRYNeedNum, iRYOwnNum)

    
    def OnClickAttr(self, iType):
        oMgr = self.GetModel()
        if not iType:
            oMgr.SetSelectTranAttr('')
            return None
        
        sHasAttrList = oMgr.GetHasAttrList()
        sAttrList = []
        for sAttr in transformattrdefine.TYPE2ATTR.itervalues():
            if sAttr not in sHasAttrList:
                sAttrList.append(sAttr)
                continue
        
        sSelectTranAttr = sAttrList[iType - 3]
        oMgr.SetSelectTranAttr(sSelectTranAttr)

    
    def OnTransformAttr(self):
        oMgr = self.GetModel()
        sOldAttr = oMgr.GetSelectAttr()
        iOldAttr = mdtransformattr.GetAttrType(sOldAttr)
        iEquip = oMgr.GetEquipID()
        if not iEquip:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xadn\xc2\xe0\xb4\xab\xaa\xba\xb8\xcb\xb3\xc6')
            return None
        
        iItemID = iEquip
        sNewAttr = oMgr.GetSelectTranAttr()
        iNewAttr = mdtransformattr.GetAttrType(sNewAttr)
        iMode = oMgr.GetSelectMode()
        if not sOldAttr:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xadn\xc2\xe0\xb4\xab\xaa\xba\xc4\xdd\xa9\xca')
            return None
        elif not sNewAttr and iMode == 2:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xadn\xc2\xe0\xb4\xab\xaa\xba\xa5\xd8\xbc\xd0\xc4\xdd\xa9\xca')
            return None
        elif not iMode:
            usermacro.PROMPT_MSG('\xbd\xd0\xa5\xfd\xbf\xef\xbe\xdc\xadn\xc2\xe0\xb4\xab\xaa\xba\xc3\xfe\xab\xac')
            return None
        
        oMgr.ConfirmTransform(iItemID, iOldAttr, iMode, iNewAttr)

    
    def UpdateItem(self):
        oView = self.GetView()
        oView.RefreshItemList()

    
    def DelayUpdate(self):
        if self.m_DelayCount >= transformattrdefine.DELAY_FRAME:
            self.ReleaseDelayTimer()
            while None:
                return None
        self.m_DelayCount >= transformattrdefine.DELAY_FRAME
        self.m_DelayCount += 1

    
    def ReleaseDelayTimer(self):
        if self.m_DelayTimer:
            self.m_DelayTimer.Release()
            self.m_DelayTimer = None
        
        self.m_DelayCount = 0

    
    def OnDelayItemChange(self):
        if self.m_DelayTimer:
            return None
        
        import timer
        self.m_DelayTimer = timer.Timer(0.033, self.DelayUpdate, iRepeat = -1, oRelayObj = self)

    
    def OnItemAdd(self, iItemID, shape, special_flag, quantity, iType, pos):
        self.OnDelayItemChange()

    
    def OnItemDel(self, oItem):
        self.OnDelayItemChange()

    
    def RefreshItemList(self):
        oMgr = self.GetModel()
        oMgr.RequestEquipInfo()
        oMgr.SetShowType(transformattrdefine.TYPE_BAG)

    
    def RefreshEquipList(self):
        oMgr = self.GetModel()
        oMgr.RequestEquipInfo()
        oMgr.SetShowType(transformattrdefine.TYPE_EQUIP)
