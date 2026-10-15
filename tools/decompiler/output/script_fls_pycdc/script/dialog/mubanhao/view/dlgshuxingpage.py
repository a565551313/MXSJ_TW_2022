# pycdc 交叉复核产物 · script.fls entry 2882
# co_filename(原始)='script/dialog/mubanhao/view/dlgshuxingpage.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_2882.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2021/4/12 19:46
\xd7\xf7\xd5\xdf: lzj
\xce\xc4\xbc\xfe: dlgshuxingpage
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import misc
import slot
import componentclass
import mubanhaodefines
import walker
import hero
import item
import ui
import style
import interface
import tipsclosemgr
import wrapinterface

def BuildSubWnd(oParent):
    return CShuxingPageDlg(oParent)


class CShuxingPageDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_ClickGradeBtn = 'SS_ClickGradeBtn(iGrade)'
    SS_ClickLevelBtn = 'SS_ClickLevel(iLevel)'
    SS_ClickRecommend = 'SS_ClickRecommend()'
    SS_ClickClear = 'SS_ClickClear()'
    SS_ClickSaveDot = 'SS_ClickSaveDot()'
    SS_ClickSaveGrade = 'SS_ClickSaveGrade()'
    SS_EquipEnter = 'SS_EquipEnter(iPos)'
    sUIName = 'dialog4/mubanhao/shuxing.dlg'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent)
        self.ssInit()
        self.m_DelegateList = []
        self.InitDelegate()
        self.InitDlg()

    
    def InitDelegate(self):
        import dgtshuxingpage
        self.m_DelegateList = [
            dgtshuxingpage.CShuxingPageDgt(self)]

    
    def SetActive(self, bActive):
        self.SetShow(bActive)

    
    def InitDlg(self):
        self.m_oGradeEdit = componentclass.CNumberEdit(self, 'edit_dengji', 30, 165, iDefaultNum = 30, iDelayTime = 0.5, iStep = 5, iID = 1, sLeftTips = '\xb5\xa5\xaf\xc5\xa5u\xaf\xe0\xbf\xe9\xa4J30-165', sRightTips = '\xb5\xa5\xaf\xc5\xa5u\xaf\xe0\xbf\xe9\xa4J30-165')
        self.m_oGradeEdit.SetActive(True)
        self.m_oTizhiEdit = componentclass.CNumberEdit(self, 'edit_Tizhi', 0, 8, oChangeCB = misc.Functor(self.OnDotEditChange), iID = 2)
        self.m_oLiliangEdit = componentclass.CNumberEdit(self, 'edit_Liliang', 0, 8, oChangeCB = misc.Functor(self.OnDotEditChange), iID = 3)
        self.m_oMoliEdit = componentclass.CNumberEdit(self, 'edit_Magic', 0, 8, oChangeCB = misc.Functor(self.OnDotEditChange), iID = 4)
        self.m_oMeiliEdit = componentclass.CNumberEdit(self, 'edit_Meili', 0, 8, oChangeCB = misc.Functor(self.OnDotEditChange), iID = 5)
        self.m_oMinjieEdit = componentclass.CNumberEdit(self, 'edit_Minjie', 0, 8, oChangeCB = misc.Functor(self.OnDotEditChange), iID = 6)
        self.m_dEquipItems = { }
        self.m_ModifyEditLst = []
        self.UpdateRole()

    
    def UpdateRole(self):
        self.m_oRoleView = walker.CFakeRole(self.GetObject('ani_Player'), 0, hero.GetProp('m_Shape', 111), self.GetPlayerDesc())
        self.m_oRoleView.SetDirection(4)
        oLoc = self.GetObject('ani_Player')
        (iW, iH) = oLoc.GetSize()
        self.m_oRoleView.SetPos(iW / 2, 0)

    
    def UpdateRealEquip(self, oItems):
        for iIdx, sTuple in enumerate(mubanhaodefines.EQUIP_LOC):
            iRealIdx = iIdx + 1
            if iRealIdx not in oItems:
                continue
            
            (sObjName, _) = sTuple
            (iX, iY, iW, iH) = self.GetLocData(sObjName)
            oEquip = CEquip(self, iX, iY, iIdx + 1 + 100)
            oEquip.SetEquipInfo(iRealIdx)
            oItemData = oItems[iRealIdx]
            oItem = item.CItem(-1, oItemData['iShape'], 0, 1, 0, 0)
            oItem.m_InfoExt = oItemData['dExt']
            oEquip.SetItem(oItem)
            self.m_dEquipItems[iRealIdx] = oEquip
        

    
    def OnEquipEnter(self, iPos):
        self.ssEmit(self.SS_EquipEnter, iPos)

    
    def ReFreshAllAttr(self, oProp):
        for sProp in mubanhaodefines.PROP_TUPLE:
            self.RefreshAtrr(sProp, oProp)
        

    
    def RefreshAtrr(self, sProp, oProp):
        if sProp not in mubanhaodefines.PROP_2_NAME:
            return None
        
        sName = mubanhaodefines.PROP_2_NAME[sProp]
        oTxt = self.GetObject(sName)
        if not oTxt:
            return None
        
        if sProp in mubanhaodefines.SPECIAL_2_ATTRLIST:
            sAttrList = mubanhaodefines.SPECIAL_2_ATTRLIST[sProp]
            iProp = getattr(oProp, sAttrList[1], 0)
            \xa6\x81\xadt = '%s/%s' % (getattr(oProp, sAttrList[0], 0), iProp)
        else:
            iProp = getattr(oProp, sProp, 0)
            \xa6\x81\xadt = str(iProp)
        oTxt.SetText(\xa6\x81\xadt)

    
    def GetPlayerDesc(self):
        import hero
        dCharDesc = misc.DeepCopy(hero.GetProp('m_Desc'))
        if 'horse' in dCharDesc:
            del dCharDesc['horse']
        
        if 'track' in dCharDesc:
            del dCharDesc['track']
        
        if 'fairy' in dCharDesc:
            dCharDesc['fairy'] = [
                dCharDesc['fairy'][0],
                [
                    0,
                    0]]
        
        if 'aura' in dCharDesc:
            del dCharDesc['aura']
        
        return dCharDesc

    
    def SetGrade(self, iGrade):
        self.m_oGradeEdit.SetEditText(iGrade)

    
    def GetGrade(self):
        return self.m_oGradeEdit.GetCurNum()

    
    def SetDotList(self, iDataList):
        self.m_oTizhiEdit.SetEditText(iDataList[0])
        self.m_oLiliangEdit.SetEditText(iDataList[1])
        self.m_oMoliEdit.SetEditText(iDataList[2])
        self.m_oMeiliEdit.SetEditText(iDataList[3])
        self.m_oMinjieEdit.SetEditText(iDataList[4])

    
    def GetDotList(self):
        iDotList = []
        for iIdx, _ in enumerate(mubanhaodefines.IDX_2_INFO):
            oObj = self.GetDotObj(iIdx)
            if not oObj:
                return None
            
            iDotList.append(oObj.GetCurNum())
        
        return iDotList

    
    def GetDotObj(self, iIdx):
        (sName, _, _) = mubanhaodefines.IDX_2_INFO[iIdx + 1]
        return getattr(self, sName, None)

    
    def OnDotEditChange(self, iID, iEditNum):
        iTotal = 0
        oCurObj = self.GetDotObj(iID - 2)
        if not oCurObj:
            return None
        
        self.RecordModify(oCurObj)
        for iIdx, _ in enumerate(mubanhaodefines.IDX_2_INFO):
            oObj = self.GetDotObj(iIdx)
            if not oObj:
                return None
            
            iNum = oObj.GetCurNum()
            iTotal += iNum
        
        if iTotal > 8:
            oCurObj.SetColor(16711680)
        else:
            for oObj in self.m_ModifyEditLst:
                oObj = oObj.Get()
                oObj.SetColor(16317440)
            

    
    def RecordModify(self, oEditObj):
        oObj = misc.WeakRef(oEditObj)
        if self.m_ModifyEditLst.count(oObj) == 0:
            self.m_ModifyEditLst.append(oObj)
        

    
    def OnEditMessage(self, iMsgID):
        if iMsgID == 5:
            self.ssEmit(self.SS_ClickRecommend)
        elif iMsgID == 31:
            self.ssEmit(self.SS_ClickSaveDot)
        elif iMsgID == 32:
            self.ssEmit(self.SS_ClickClear)
        elif iMsgID == 36:
            self.ssEmit(self.SS_ClickSaveGrade)
        elif iMsgID == 37:
            self.ssEmit(self.SS_ClickGradeBtn, mubanhaodefines.GRADE_BTN_30)
        elif iMsgID == 38:
            self.ssEmit(self.SS_ClickGradeBtn, mubanhaodefines.GRADE_BTN_69)
        elif iMsgID == 39:
            self.ssEmit(self.SS_ClickGradeBtn, mubanhaodefines.GRADE_BTN_89)
        elif iMsgID == 40:
            self.ssEmit(self.SS_ClickGradeBtn, mubanhaodefines.GRADE_BTN_110)
        elif iMsgID == 41:
            self.ssEmit(self.SS_ClickGradeBtn, mubanhaodefines.GRADE_BTN_140)
        elif iMsgID == 10:
            self.ssEmit(self.SS_ClickLevelBtn, mubanhaodefines.LEVEL_LOW)
        elif iMsgID == 42:
            self.ssEmit(self.SS_ClickLevelBtn, mubanhaodefines.LEVEL_MID)
        elif iMsgID == 43:
            self.ssEmit(self.SS_ClickLevelBtn, mubanhaodefines.LEVEL_HIGH)
        

    
    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)



class CEquipInterface(item.CInterfaceItem):
    
    def Refresh(self, iPos):
        if self.m_InterfaceItems is not None:
            self.m_InterfaceItems[iPos] = self
        
        self.m_Pos = iPos

    
    def SetItem(self, oItem):
        self.m_SpecialEffect = None
        item.CInterfaceItem.SetItem(self, oItem)
        if oItem:
            self.m_EquipBackground = ui.CImage(self, style.GetPath('combdialog/\xd4\xd3\xcd\xbc/equip_bg.igs'), interface.UIPath)
            self.m_EquipBackground.SetZ(-1)
        else:
            self.m_EquipBackground = None

    
    def SetTips(self, sTips1, sTips2, iDelay = 0):
        self.m_Info = sTips1
        self.m_InfoNone = sTips2
        self.m_Delay = iDelay
        if not hasattr(self, 'm_Tips'):
            self.m_Tips = None
        
        if not hasattr(self, 'm_TipsDelay'):
            self.m_TipsDelay = None
        

    
    def Enter(self):
        import dlgshenmoisland
        if tipsclosemgr.IsHandle():
            return None
        
        item.CInterfaceItem.Enter(self)
        if self.m_Info is None:
            return None
        
        if dlgshenmoisland.IsShenmoHuodong():
            return None
        
        
        def ShowTips(oObj):
            sTips = oObj.m_Info
            if oObj.m_Item is None:
                sTips = oObj.m_InfoNone
            
            oObj.m_Tips = wrapinterface.CTextTips(oObj.GetParent(), -1, sTips, interface.FontLT14_3, direct = 1)
            oObj.m_Tips.SetOwner(oObj)

        if self.m_Delay == 0:
            ShowTips(self)
        else:
            self.m_TipsDelay = self.CreatePyCommand(self.m_Delay, ShowTips)

    
    def Leave(self):
        self.m_PosBox.SetShow(False)
        if self.m_TipsDelay:
            self.m_TipsDelay.Release()
            self.m_TipsDelay = None
        
        self.m_Tips = None
        self.SetAlpha(0)
        tipsclosemgr.CheckClose()
        item.g_ItemTips = None



class CEquip(item.CInterfaceFakeItem):
    
    def SetEquipInfo(self, iPos):
        self.m_iPos = iPos

    
    def Enter(self):
        item.CInterfaceFakeItem.Enter(self)
        self.GetParent().OnEquipEnter(self.m_iPos)
