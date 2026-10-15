# pycdc 交叉复核产物 · script.fls entry 4557
# co_filename(原始)='script/mxgame/autoupgrade/delegate/dgtautoupgrade.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4557.pyc (Python 2.5)

import dlgnpc
import dlgpresentcenter
import netautoupgrade
import presentcenterdefines
import slot
import delegatebase
import mdautoupgrde

class CAutoUpgradeDgt(delegatebase.CDelegateBase, slot.ISignalSubject):
    
    def Init(self):
        oMgr = mdautoupgrde.GetMgr()
        oMgr.ssConnect(oMgr.SS_UpdateDiscount, self.OnUpdateDiscount)
        oMgr.ssConnect(oMgr.SS_UpdateEquipExt, self.OnUpdateEquipExt)
        oMgr.ssConnect(oMgr.SS_UpdateDetail, self.OnRefreshDetail)
        \xc0\xf9\xc6\xca\xd8 = self.GetView()
        \xc0\xf9\xc6\xca\xd8.ssConnect(\xc0\xf9\xc6\xca\xd8.SS_EnterEquip, self.OnEnterEquip)
        \xc0\xf9\xc6\xca\xd8.ssConnect(\xc0\xf9\xc6\xca\xd8.SS_SelectGrade, self.OnSelectGrade)
        \xc0\xf9\xc6\xca\xd8.ssConnect(\xc0\xf9\xc6\xca\xd8.SS_ConfirmOK, self.OnConfirmOK)
        \xc0\xf9\xc6\xca\xd8.ssConnect(\xc0\xf9\xc6\xca\xd8.SS_ClickNeverShow, self.OnClickNeverShow)
        self.OnUpdateDiscount()

    
    def OnRefreshDetail(self, dInfo):
        \xc0\xf9\xc6\xca\xd8 = self.GetView()
        \xc0\xf9\xc6\xca\xd8.RefreshDetail(dInfo)

    
    def OnUpdateDiscount(self):
        iDisCount = mdautoupgrde.GetMgr().GetDiscount()
        \xc0\xf9\xc6\xca\xd8 = self.GetView()
        if \xc0\xf9\xc6\xca\xd8:
            \xc0\xf9\xc6\xca\xd8.UpdateBuyDiscount(iDisCount)
            \xc0\xf9\xc6\xca\xd8.ChangeSG()
        

    
    def OnUpdateEquipExt(self, iGrade, iType):
        self.GetView().ShowEquip(mdautoupgrde.GetMgr().GetAllEquipExt())

    
    def OnEnterEquip(self, iGrade, iType):
        sExt = mdautoupgrde.GetMgr().GetEquipExt(iGrade, iType)
        if sExt is None:
            netautoupgrade.C2SGetEquipInfo(iGrade, iType)
        

    
    def OnSelectGrade(self, iGrade):
        self.GetView().SetGradeString('%s\xaf\xc5' % iGrade)
        self.GetView().ShowEquip(mdautoupgrde.GetMgr().GetAllEquipExt())

    
    def OnConfirmOK(self, iGrade, iXiulian, iWing, iLiupai, iHorse):
        if iWing not in mdautoupgrde.GetMgr().GetWingInfo():
            iWing = 0
        
        netautoupgrade.C2SSubmit(iGrade, iXiulian, iWing, iLiupai, iHorse)
        dlgpresentcenter.Close()

    
    def OnClickNeverShow(self):
        dlgnpc.ShowClientDlg('\xdb8\xd0(\xca#\xde\x00\xd3\xd4\xd16\xb2\x94\xd2\xab\xd2\xcc\xdb\xbe\xda\xc6T.\xd6*\xdc\x96\xb3\x85\xd3\xc3\xd2\x1e\xdc\x12\xde\xce\xd0\xa9\xd8\x97\xc6\xa7\xd9\x01\xde\x8d\xd3\x9c\xdc\xc7\xa1]31\xa1A159\xa1^\xb3B\xa8\xcf\xa5\xce\xa7\xd6\xb3t\xb4\xa3\xa4\xc9\xa5\\\xaf\xe0\xa1^#n\nQ\xbdT\xa9w\nQ\xa8\xfa\xae\xf8', '', self.OnNpcClick)

    
    def OnNpcClick(self, iMsgID):
        if iMsgID == 1:
            netautoupgrade.C2GSNeverShowUpgradePage()
            dlgpresentcenter.Close()
            dlgpresentcenter.Open(presentcenterdefines.PAGE_GRADE_GIFT)
        



class CAutoUpgradeBtnCtrlDgt(delegatebase.CDelegateBase, slot.ISignalSubject):
    
    def Init(self):
        \xc0\xf9\xc6\xca\xd8 = self.GetView()
        \xc0\xf9\xc6\xca\xd8.ssConnect(\xc0\xf9\xc6\xca\xd8.SS_SelectGrade, self.OnSelectGrade)

    
    def OnSelectGrade(self, iGrade):
        for iSetGrade, sName in {
            88: 'img_down1',
            110: 'img_down2' }.iteritems():
            self.GetView().SetShowObject(sName, iGrade == iSetGrade)
