# pycdc 交叉复核产物 · script.fls entry 110
# co_filename(原始)='script/yard/collectshow/view/dlghorseexhibition.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_110.pyc (Python 2.5)

import combdialog
import slot
import interface
import makeitemicon
import itemdefine

def Show():
    CHorseExhibitionDlg.OpenUI()


def Close():
    CHorseExhibitionDlg.CloseUI()


class CHorseExhibitionDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_GetOwnHorseInfo = 'OnGetOwnHorseInfo()'
    SS_RefreshHorseModel = 'OnRefreshHorseModel(iPos)'
    SS_RefreshCurSelectPos = 'OnRefreshCurSelectPos(iPos)'
    SS_RefreshHorseEquipChipNums = 'OnRefreshHorseEquipChipNums(iPos)'
    SS_RefreshShowBtnMode = 'OnRefreshShowBtnMode()'
    SS_AskShowFurnitur = 'OnAskShowFurnitur(sModel)'
    sUIName = 'dialog4/yard/mount/horse_main.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombDialog.__init__(self, oParent)
        self.ssInit()
        self.m_oDelegateList = []
        self.m_NotifyBoxlst = []
        self.m_oDuanJinLingIcon = None
        self.m_oBeiJiGuang = None
        self.m_oAni = None
        self.m_sShowModel = ''
        self.InitDelegate()
        self.InitData()

    
    def InitData(self):
        self.SetNeedNumBox()
        self.ssEmit(self.SS_GetOwnHorseInfo)

    
    def InitDelegate(self):
        import delegatehorseexhibition
        self.m_oDelegateList = [
            delegatehorseexhibition.CHorseExhibitionDelegate(self)]

    
    def SetNeedNumBox(self):
        self.m_oDuanJinLingIcon = makeitemicon.CNeedItemIcon(self.GetObject('img_item1'), itemdefine.ID_ITEM_HORSE_DECORATE, 20, 4)
        self.m_oBeiJiGuang = makeitemicon.CNeedItemIcon(self.GetObject('img_item2'), itemdefine.ID_ITEM_HORSE_LIGHT, 21, 4)

    
    def RefreshHorseList(self, dHorseList):
        oHorseList = self.GetObject('lst_ride')
        oHorseList.Clear()
        for dHorseInfo in dHorseList:
            oHorseList.AddTextItem(dHorseInfo['sName'], interface.COLOR_22)
        
        oHorseList.ResetItems()
        oHorseList.ResetScrollBar()

    
    def SetItemLeftDown(self, iPos):
        self.GetObject('lst_ride').GetItemByIndex(iPos).LeftUp()

    
    def RefreshHorseEquipChipNum(self, iHvaeNumList, iNeed):
        self.m_oDuanJinLingIcon.SetNeedTxt(iHvaeNumList[0], iNeed)
        self.m_oBeiJiGuang.SetNeedTxt(iHvaeNumList[1], iNeed)

    
    def RefreshHorseModel(self, dDesc, iDir = 1):
        import multihorsemgr
        import walker
        oPosObj = self.GetObject('loc_mount')
        if 'horse' in dDesc and dDesc['horse'] and dDesc['horse'][0] in (25, 26):
            pos = 0
            if dDesc['horse'][0] == 26:
                pos = 1
            
            dDesc = multihorsemgr.TransformSpeHorse(dDesc, pos)
            ani = walker.CFakeRole(self, 1, 0, dDesc)
            (x, y) = oPosObj.GetPos()
            (w, h) = oPosObj.GetSize()
            ani.SetPos(x + w / 2, y + h - 20)
            self.m_DirFrame = 4
        else:
            ani = walker.CFakeRole(self, 1, 0, dDesc)
            (x, y) = oPosObj.GetPos()
            ani.SetPos(x + 4, y + 2)
            self.m_DirFrame = 8
        ani.ClearRider()
        ani.SetDirection(iDir)
        
        try:
            ani.SetZ(oPosObj() + 1)
            ani.m_Shadow = None
        except:
            oPosObj.m_oAni = ani.SetZ
            return None


    
    def ClickOnHorse(self, iPos):
        self.ssEmit(self.SS_RefreshCurSelectPos, iPos)
        self.ssEmit(self.SS_RefreshShowBtnMode)
        self.ssEmit(self.SS_RefreshHorseModel, iPos)
        self.ssEmit(self.SS_RefreshHorseEquipChipNums, iPos)

    
    def ClickShowBtn(self):
        self.ssEmit(self.SS_AskShowFurnitur, self.m_sShowModel)

    
    def RefreshShowBtn(self, sText, sModel):
        self.GetObject('btn_zhanshi').SetText(sText)
        self.m_sShowModel = sModel

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            Close()
        elif iMsgID == 2:
            self.ClickShowBtn()
        elif iMsgID > 100:
            self.ClickOnHorse(iMsgID - 101)
