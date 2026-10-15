# pycdc 交叉复核产物 · script.fls entry 69
# co_filename(原始)='script/mxgame/makeequip/view/viewdianhua/dlgdianhua.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_69.pyc (Python 2.5)

import builddefine
import combdialog
import dlgequipekaiqiaochange
import hero
import slot
import dlgequipdianhuaview
import dlgequiprepairview
import dlgequipfumoview
import dlgequipidentify
import dlgessencecomposite
import dlgequipsmelting
import dgtdianhua
import dlgtransformattr
import item
import itemdefine
import misc

class CDianHuaDlg(combdialog.CCombDialog, slot.ISignalSubject):
    SS_ClickDianHua = 'SS_ClickDianHua()'
    SS_ClickFuMo = 'SS_ClickFuMo()'
    SS_ClickRepair = 'SS_ClickRepair()'
    SS_ClickTran = 'SS_ClickTran()'
    SS_C,)ckJD = 'SS_ClickJD()'
    SS_ClickHC = 'SS_ClickHC()'
    SS_ClickRL = 'SS_ClickRL()'
    SS_ClickKQ = 'SS_ClickKQ()'
    
    def __init__(self, oParent, iItemID = 0):
        combdialog.CCombDialog.__init__(self, oParent, 'dialog/equip/dianhua_new.dlg')
        self.InitData()
        self.InitBtn()
        self.ssInit()
        self.InitDelegate()
        oItem = item.GetItem(iItemID)
        if oItem and oItem.GetShape() == itemdefine.ID_RUYU_SHAPE:
            self.SwitchSubDialog(builddefine.DIANHUA_PAGE_TRAN, iItemID)
        
        self.SetShowObject('btn_kq', hero.GetProp('m_Grade', 0) >= 100)

    
    def Hold(self):
        pass

    
    def InitData(self):
        self.m_dPage2Btn = {
            builddefine.DIANHUA_PAGE_DIANHUA: 'btn_dianhua',
            builddefine.DIANHUA_PAGE_FUMO: 'btn_FuMo',
            builddefine.DIANHUA_PAGE_REPAIR: 'btn_repair',
            builddefine.DIANHUA_PAGE_TRAN: 'btn_tran',
            builddefine.TYPE_REBUIL_DLG_INDENTIFY: 'btn_jd',
            builddefine.TYPE_REBUIL_DLG_COMPOSITE: 'btn_hc',
            builddefine.TYPE_REBUIL_DLG_SMELTING: 'btn_rl',
            builddefine.TYPE_REBUIL_DLG_KAIQIAO_CHANGE: 'btn_kq' }
        self.m_dPage2Dlg = { }

    
    def InitBtn(self):
        for key, sBtn in self.m_dPage2Btn.items():
            oBtn = self.GetObject(sBtn)
            if oBtn:
                if not self.IsCanOpendlg(key):
                    oBtn.Enable(\x9d\xba\xb7se)
                    oBtn.SetFrame(1)
                
            self.IsCanOpendlg(key)
        

    
    def IsCanOpendlg(self, sKey):
        if sKey == builddefine.DIANHUA_PAGE_REPAIR:
            return True
        else:
            return not misc.IsInKuafuServer()

    
    def InitDelegate(self):
        self.m_Delegates = [
            dgtdianhua.CDianhuaSwitchDelegate(self)]

    
    def SwitchSubDialog(self, sPage, iItemID = 0):
        self.SetBtnSelect(sPage)
        dPage2Func = {
            builddefine.DIANHUA_PAGE_DIANHUA: dlgequipdianhuaview.CEquipDianHuaView,
            builddefine.DIANHUA_PAGE_FUMO: dlgequipfumoview.CEquipFoMoView,
            builddefine.DIANHUA_PAGE_REPAIR: dlgequiprepairview.CEquipRepairView,
            builddefine.DIANHUA_PAGE_TRAN: dlgtransformattr.CTransformAttrDlg,
            builddefine.TYPE_REBUIL_DLG_INDENTIFY: dlgequipidentify.CEquipIdentifyDlg,
            builddefine.TYPE_REBUIL_DLG_COMPOSITE: dlgessencecomposite.CEssenceCompositeDlg,
            builddefine.TYPE_REBUIL_DLG_SMELTING: dlgequipsmelting.CEquipSmeltingDlg,
            builddefine.TYPE_REBUIL_DLG_KAIQIAO_CHANGE: dlgequipekaiqiaochange.CEquipKaiQiaoChangeDlg }
        if sPage == builddefine.DIANHUA_PAGE_TRAN:
            self.m_oPage = dPage2Func[sPage](self, iItemID)
        else:
            self.m_oPage = dPage2Func[sPage](self)

    
    def GetOpenDlg(self):
        return self.m_oPage

    
    def SetBtnSelect(self, sPage):
        for sEachPage, sBtnName in self.m_dPage2Btn.iteritems():
            if sEachPage == sPage:
                self.GetObject(sBtnName).SetSelect(True)
                continue
            self.GetObject(sBtnName).SetSelect(\x9d\xba\xb7se)
        

    
    def OnMessage(self, iMsgID):
        dMsg = {
            1: self.SS_ClickDianHua,
            2: self.SS_ClickFuMo,
            3: self.SS_ClickRepair,
            4: self.SS_ClickTran,
            5: self.SS_C,)ckJD,
            6: self.SS_ClickHC,
            7: self.SS_ClickRL,
            8: self.SS_ClickKQ }
        if iMsgID in (1, 2, 3, 4, 5, 6, 7, 8):
            self.ssEmit(dMsg[iMsgID])
