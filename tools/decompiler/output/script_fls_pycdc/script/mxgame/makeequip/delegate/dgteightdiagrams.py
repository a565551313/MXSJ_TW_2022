# pycdc 交叉复核产物 · script.fls entry 3492
# co_filename(原始)='script/mxgame/makeequip/delegate/dgteightdiagrams.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3492.pyc (Python 2.5)

import delegatebase
import item
import itemdata
import itemdefine
import netitem

class CEquipListDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_sSelectTag = ''
        self.m_iLastSelPos = 0
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def GetView(self):
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        raise '\xbb\xdd\xadn\xab\xfc\xa9w\xb9\xef\xc0\xb3\xaa\xbaModel'

    
    def Init(self):
        self.OnRefershItems()
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_ItemChange, self.OnItemChange)
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickBag, self.OnClickBag)
        oView.ssConnect(oView.SS_AlreadyEquip, self.OnClickAlreadyEquip)
        oItemModel = GetItemModel()
        oItemModel.ssConnect(oItemModel.SS_BAG_ADD_ITEM, self.OnAddItem)
        oItemModel.ssConnect(oItemModel.SS_BAG_DEL_ITEM, self.OnDelItem)

    
    def OnItemChange(self, dInfo):
        self.OnClickItem(dInfo)
        self.CheckValid()

    
    def OnClickBag(self):
        self.m_sSelectTag = '\xadI\xa5]'
        oView = self.GetView()
        self.RefreshItemsByTag()
        if self.m_iLastSelPos in oView.GetInterfaceItem():
            oSelItem = oView.GetInterfaceItem()[self.m_iLastSelPos]
            oSelItem.LeftUp()
        
        self.CheckValid()

    
    def OnClickAlreadyEquip(self):
        self.m_sSelectTag = '\xa4w\xac\xef\xc0\xb9'
        oView = self.GetView()
        self.RefreshItemsByTag()
        if self.m_iLastSelPos in oView.GetInterfaceItem():
            oSelItem = oView.GetInterfaceItem()[self.m_iLastSelPos]
            oSelItem.LeftUp()
        
        self.CheckValid()

    
    def IsValidType(self, oItem):
        return itemdata.IsType(oItem.GetShape(), 'equip')

    
    def IsItemEnable(self, itemObj, miteralDict, shapeDict):
        if itemObj.IsSelected():
            return True
        
        iShape = itemObj.GetItem().GetShape()
        for sType in self.GetCheckItemType():
            if itemdata.IsType(iShape, sType) and miteralDict[sType] == 0:
                return True
                continue
        
        return False

    
    def GetCheckItemType(self):
        raise '\xab\xfc\xa9w\xa5i\xa5H\xc5\xe3\xa5\xdc\xaa\xba\xaa\xab\xab~\xc3\xfe\xab\xac'

    
    def IsClickSelItem(self, iItemID):
        iPos = item.GetItem(iItemID).GetPos()
        self.m_iLastSelPos = iPos
        oView = self.GetView()
        if iPos in oView.GetInterfaceItem():
            oSelItem = oView.GetInterfaceItem()[iPos]
            if oSelItem.IsSelected():
                for idx, oInputItem in enumerate(oView.GetInputItems()):
                    if oInputItem and oInputItem.GetItem().GetPos() == iPos:
                        oSelItem.Select(False)
                        oView.ClearInputItem(idx)
                        self.m_iLastSelPos = 0
                        self.CheckValid()
                        return True
                        continue
                
            
        
        return False

    
    def OnClickItem(self, dInfo):
        iPos = item.GetItem(dInfo['iSelItemID']).GetPos()
        oView = self.GetView()
        if iPos in oView.GetInterfaceItem():
            oSelItem = oView.GetInterfaceItem()[iPos]
            if oSelItem.GetItem() is None:
                return None
            
            oSelItem.Select(True)
            if itemdata.IsType(oSelItem.GetItem().GetShape(), 'equip'):
                oView.RefershEquipInfo(dInfo)
            else:
                oView.RefershMaterialInfo(dInfo)
        

    
    def CheckValid(self):
        oView = self.GetView()
        itemTypes = self.GetCheckItemType()
        if not itemTypes:
            return None
        
        shapeDict = dict((lambda .0: for tp in .0:
(tp, 0))(itemTypes))
        miteralDict = dict((lambda .0: for tp in .0:
(tp, 0))(itemTypes))
        for inputObj in oView.GetInputItems():
            if inputObj and inputObj.GetItem():
                iShape = inputObj.GetItem().GetShape()
                if itemdata.IsType(iShape, itemTypes[0]):
                    miteralDict[itemTypes[0]] += 1
                    shapeDict[itemTypes[0]] = iShape
                elif len(itemTypes) > 1:
                    if itemdata.IsType(iShape, itemTypes[1]):
                        miteralDict[itemTypes[1]] += 1
                        shapeDict[itemTypes[1]] = iShape
                    
                
            itemdata.IsType(iShape, itemTypes[0])
        
        for itemObj in oView.GetInterfaceItem().itervalues():
            if itemObj.GetItem():
                bEnable = self.IsItemEnable(itemObj, miteralDict, shapeDict)
                itemObj.Enable(bEnable)
                itemObj.ShowShadow(not bEnable)
                continue
        

    
    def OnAddItem(self, iItemID, iShape, iSpecialFlag, iQuantity, iType, iPos):
        if self.IsValidType(item.GetItem(iItemID)):
            self.OnRefershItems()
        

    
    def OnDelItem(self, oItem):
        if self.IsValidType(oItem):
            self.OnRefershItems()
        

    
    def OnRefershItems(self):
        allItemDict = item.GetItems()
        dType2Items = {
            '\xadI\xa5]': [],
            '\xa4w\xac\xef\xc0\xb9': [] }
        for iItemPos, oItem in allItemDict.items():
            if self.IsValidType(oItem):
                if iItemPos <= iItemPos:
                    pass
                elif iItemPos <= itemdefine.EQUIP_ENDPOS:
                    dType2Items['\xa4w\xac\xef\xc0\xb9'].append([
                        iItemPos,
                        oItem])
                elif iItemPos <= iItemPos:
                    pass
                elif iItemPos <= item.ITEM_FIGHT_SCOPE:
                    dType2Items['\xadI\xa5]'].append([
                        iItemPos,
                        oItem])
                
            iItemPos <= item.ITEM_FIGHT_SCOPE
        
        oModel = self.GetModel()
        oModel.SetType2Items(dType2Items)

    
    def GetInputItemIDs(self):
        oView = self.GetView()
        itemidList = []
        for oInputItem in oView.GetInputItems():
            itemidList.append(oInputItem.GetItemId())
        
        return itemidList

    
    def UpdatePutItem(self, iItemID, idx = 0):
        oItem = item.GetItem(iItemID)
        if not itemdata.IsType(oItem.GetShape(), 'equip'):
            return None
        
        oModel = self.GetModel()
        oIdList = oModel.GetLastPutItemIdList()
        iLastId = oIdList[idx]

    
    def RefreshItemsByTag(self):
        dType2Items = self.GetModel().GetType2Items()
        self.GetView().RefershItems(dType2Items['\xa4w\xac\xef\xc0\xb9'] + dType2Items['\xadI\xa5]'])



def GetItemModel():
    import mdpropitem
    return mdpropitem.GetModel()
