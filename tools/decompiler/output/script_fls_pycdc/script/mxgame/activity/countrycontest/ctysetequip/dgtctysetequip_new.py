# pycdc 交叉复核产物 · script.fls entry 2563
# co_filename(原始)='script/mxgame/activity/countrycontest/ctysetequip/dgtctysetequip_new.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2563.pyc (Python 2.5)

import delegatebase
import mdctysetequip
import misc
import netctysetequip
import ctyequipdata
import ctysetequipdefine
import specialeffectdata
import usermacro
SS_TJNUMCHANGE = 'TJNUMCHANGE'
SS_SXNUMCHANGE = 'SXNUMCHANGE'
SS_BSNUMCHANGE = 'BSNUMCHANGE'

class CSetEquipDgt(delegatebase.CDelegateBase):
    JEWELCLICKID = 3
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_EQUIPCLICK, self.EquipClick)
        oView.ssConnect(oView.SS_SETTINGCHANGE, self.BoxLstClick)
        oView.ssConnect(oView.SS_SXNUMCHANGE, self.SXBtnNumClick)
        oView.ssConnect(oView.SS_BSNUMCHANGE, self.BSBtnNumClick)
        oView.ssConnect(oView.SS_RESETSETTING, self.ResetEquipSetting)
        oView.ssConnect(oView.SS_SAVESETTING, self.SaveData)
        oView.ssConnect(oView.SS_SAVEORCHANGECLICK, self.ChangeOrSaveClick)
        oView.ssConnect(oView.SS_ONCLOSE, self.OnClose)
        oView.ssConnect(oView.SS_REQUESTEQUIPINFO, self.RequestEquipInfo)
        oModel = self.GetModel()
        oModel.ssConnect(oModel.SS_UPDATECLICKEQUIPINFO, self.UpdateClickEquipInfo)
        oModel.ssConnect(oModel.SS_UPDATEBASEATTR, self.UpdateBaseAttrInfo)
        oModel.ssConnect(oModel.SS_UPDATEROLEMODEL, self.UpdateAttrModelInfo)
        oModel.ssConnect(oModel.SS_UPDATEROLEATTR, self.UpdateAttrInfo)
        oModel.ssConnect(oModel.SS_UPDATEWEAPONSHAPE, self.UpdateWeaponShape)

    
    def GetView(self):
        '''
\t\t:rtype: dlgctysetequip_new.CSetEquipDlg
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def GetModel(self):
        return mdctysetequip.GetEquipModel()

    
    def UpdateWeaponShape(self, iWeaponShape):
        self.GetView().SetWeaponEquip(iWeaponShape)

    
    def UpdateAttrInfo(self, dInfo):
        self.GetView().RefreshProp(dInfo)

    
    def UpdateAttrModelInfo(self, dInfo):
        self.GetView().RefreshPlayerAni(dInfo)

    
    def ChangeOrSaveClick(self, iMsg):
        tSaveMsg = [
            3,
            4,
            5]
        bSave = iMsg in tSaveMsg
        if bSave:
            iClickID = tSaveMsg.index(iMsg) + 1
            if not self.CheckCanSave():
                return None
            
        else:
            iClickID = [
                6,
                7,
                8].index(iMsg) + 1
        oView = self.GetView()
        oView.OnChangeOrSaveClick(iClickID, bSave)
        if iClickID == 1:
            if ctysetequipdefine.EQUIPKEY.get(self.GetModel().GetSelectEquipIndex()) == '\xc5@\xb5\xc3':
                iRow = 0
            else:
                iRow = 1
            oView.UpdateAddAttrState(not bSave, iRow)
        elif iClickID == 2:
            oView.UpdateJewelState(not bSave)
        elif iClickID == 3:
            oView.UpdateEffectState(not bSave)
        
        self.UpdateAddAttrInfo()
        if bSave:
            self.SaveData()
        

    
    def UpdateBaseAttrInfo(self):
        self.GetView().UpdateAttr(self.GetModel().GetBaseAttrDic(), 'text_attrname', 'text_attrnum')

    
    def UpdateAddAttrInfo(self):
        dic = self.GetModel().GetAddAttrDic()
        if dic:
            self.GetView().UpdateAddAttr(dic, 'text_addattrname', 'text_addattrnum')
        

    
    def ResetEquipSetting(self):
        import dlgnpc
        import misc
        dlgnpc.ShowClientDlg('\xbdT\xbb{\xb1N#B\xa1u%s\xa1v#n\xc1\xd9\xad\xec\xac\xb0#B\xa8t\xb2\xce\xb1\xc0\xaf\xf2\xa4\xe8\xae\xd7#n\xa1A\xbdT\xbb{\xc1\xd9\xad\xec\xb6\xdc\xa1H\nQ\xbdT\xbb{\xc1\xd9\xad\xec\nQ\xaa\xf0\xa6^\xb3]\xb8m\xac\xc9\xad\xb1' % self.GetModel().GetSelectEquipName(), '', misc.Functor(self.Reset))

    
    def Reset(self, iSel):
        if iSel == 1:
            iPart = GetModel.GetSelectEquipIndex()
            netctysetequip.C2SResetEquipSetting(iPart, self.GetView().GetProjectID())
        

    
    def SaveData(self):
        oModel = self.GetModel()
        if not self.CheckCanSave():
            return None
        
        if oModel.GetSelectEquipIndex() != 0:
            netctysetequip.C2SSaveEquipInfo(oModel.GetEquipData(), self.GetProjectID())
        

    
    def CheckCanSave(self):
        oModel = self.GetModel()
        if not oModel.JewelLevelIsMax() and oModel.GetSelectEquipIndex() != 2:
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xc4_\xa5\xdb\xc1`\xb5\xa5\xaf\xc5\xa4\xa3\xb5\xa5\xa9\xf39\xa1A\xbd\xd0\xbd\xd5\xbe\xe3\xa6\xdc\xc1`\xb5\xa5\xaf\xc5\xac\xb09\xaf\xc5')
            return False
        
        if not oModel.CheckEffectPointIsEnough():
            usermacro.PROMPT_MSG('\xafS\xae\xc4\xc2I\xa4\xa3\xa8\xac')
            return False
        
        return True

    
    def UpdateClickEquipInfo(self):
        oModel = self.GetModel()
        oView = self.GetView()
        sEffectName = oModel.GetUseEffectName()
        oView.UpdateBoxLst(oView.FrameSkill, sEffectName, oModel.GetEffectSkillLst(), oModel.GetSelectEquipIndex())
        oView.RefreshEffectPoint(oModel.GetUseEffectPoint())
        if sEffectName == '\xb5L':
            sEffectName = ''
        else:
            sEffectName = oModel.GetEffectWrapTxt()
        oView.RefreshEffectWrap(sEffectName)
        sSkillTxt = oModel.GetSpecialSkillTxt()
        oView.RefreshSkillWrap(sSkillTxt)
        self.UpdateBaseAttrInfo()
        self.UpdateAddAttrInfo()
        for idx in range(len(oView.FrameAddattr)):
            iPart = oModel.GetSelectEquipIndex()
            if idx == 1 and ctysetequipdefine.EQUIPKEY.get(iPart) == '\xc5@\xb5\xc3':
                oView.UpdateBoxLst(oView.FrameAddattr[idx], '\xa4\xa3\xa5i\xbf\xef', [], iPart)
                oView.RefreshAddAttrNum(idx, 0)
                continue
            
            (iID, iNum) = oModel.GetAddAttrInfoByPos(idx)
            sAttrName = ctysetequipdefine.AddAttrKeyToName.get(iID, '\xb5L')
            oView.UpdateBoxLst(oView.FrameAddattr[idx], sAttrName, oModel.GetAddAttrLst(), iPart)
            oView.RefreshAddAttrNum(idx, iNum)
        
        for idx in range(len(oView.FrameJewel)):
            (id, lvl) = oModel.GetJewelsInfoByPos(idx)
            iPart = oModel.GetSelectEquipIndex()
            if iPart == 2:
                name = '\xa4\xa3\xa5i\xc6^\xb4O'
            else:
                name = ctysetequipdefine.GetJewelsNameByID(id)
            oView.UpdateBoxLst(oView.FrameJewel[idx], name, oModel.GetJewelsLst(), iPart)
            oView.RefreshJewelLevel(idx, lvl)
        
        oView.RefreshJewelAttr(oModel.GetEquipJewelAttr())
        oView.ChangeSkillBtn(ctysetequipdefine.EQUIPKEY.get(oModel.GetSelectEquipIndex()) == '\xaak\xc4_')
        oView.InitBtnState()
        oView.SetNoneSkillState(not oModel.GetEffectSkillLst())
        oView.ChangeJewelChangeBtn(oModel.GetSelectEquipIndex() in (6, 7))
        if ctysetequipdefine.EQUIPKEY.get(oModel.GetSelectEquipIndex()) == '\xaaZ\xbe\xb9':
            oView.RefreshJewelLevelTips('')
            oView.SetChangeOrSaveState(2, False)
        else:
            str = '\xc1\xeb\xb3y\xb5\xa5\xaf\xc5:9'
            oView.RefreshJewelLevelTips(str)

    
    def BoxLstClick(self, sKey, sTxt):
        oModel = self.GetModel()
        oView = self.GetView()
        if sKey == oView.FrameSkill:
            if sTxt != '\xb5L':
                iIndex = sTxt.index('(')
                sTxt = sTxt[:iIndex]
                effectID = specialeffectdata.GetKeybyName(sTxt)
                iCostPoint = ctyequipdata.GetEffectPointByKey(effectID)
                LOG_DEBUG('\xb7\xed\xabe\xafS\xa7\xdeID\xa1G%d, \xae\xf8\xaf\xd3\xafS\xa7\xde\xc2I\xa1G%d' % (effectID, iCostPoint))
                oModel.ChangeSpecialEffect(effectID, iCostPoint)
                oView.RefreshEffectPoint(oModel.GetUseEffectPoint())
            else:
                oModel.CancelSpecailEffect()
                oView.RefreshEffectPoint(oModel.GetUseEffectPoint())
        elif sKey in oView.FrameAddattr:
            iPos = int(oView.FrameAddattr.index(sKey))
            sBeforeName = oModel.GetAddAttrNameByPos(iPos)
            if sBeforeName == sTxt:
                return None
            
            iID = ctysetequipdefine.GetAddAttrKeyByName(sTxt)
            if oModel.CheckHasSameAddAttr(iID):
                oView.ReturnBack(sKey, sBeforeName)
                usermacro.PROMPT_MSG('\xa6s\xa6b\xac\xdb\xa6P\xaa\xfe\xa5[\xc4\xdd\xa9\xca')
                return None
            
            if sTxt == '\xb5L':
                oModel.RemoveAddAttrByPos(iPos)
                usermacro.PROMPT_MSG('\xb2\xbe\xb0\xa3\xa6\xa8\xa5\\')
                oView.RefreshAddAttrNum(iPos, 0)
                return None
            
            oModel.ChangeAddAttrByPos(iPos, iID)
            (id, num) = oModel.GetAddAttrInfoByPos(iPos)
            oView.RefreshAddAttrNum(iPos, num)
        elif sKey in oView.FrameJewel:
            iPos = int(oView.FrameJewel.index(sKey))
            sBeforeName = oModel.GetJewelNamePosByPos(iPos)
            if sBeforeName == sTxt:
                return None
            
            iJewelID = ctysetequipdefine.GetJewelIDByName(sTxt)
            if sTxt == '\xb5L':
                oModel.RemoveJewelPosByPos(iPos)
                usermacro.PROMPT_MSG('\xb2\xbe\xb0\xa3\xa6\xa8\xa5\\')
                oView.RefreshJewelLevel(iPos, 0)
                self.UpdateBSNum()
                oView.RefreshJewelBoxSelect(iPos, sTxt)
                return None
            
            if oModel.CheckHasSameJewel(iJewelID):
                usermacro.PROMPT_MSG('\xa6s\xa6b\xac\xdb\xa6P\xc4_\xa5\xdb')
                oView.ReturnBack(sKey, sBeforeName)
                return None
            
            if sBeforeName == '\xb5L':
                if oModel.GetCurJewelLevel() >= oModel.GetJewelMaxLevel():
                    oModel.ChangeJewelByPos(iPos, iJewelID)
                    oModel.ChangeJewelLevelMaxOrMin(iPos, False)
                    self.UpdateBSNum()
                    return None
                
            
            oModel.ChangeJewelByPos(iPos, iJewelID)
            dicJewels = oModel.GetJewelsDic()
            for k, v in dicJewels.items():
                oView.RefreshJewelLevel(k, v['iLevel'])
            
        

    
    def EquipClick(self, iMsgID):
        import commondialog
        iEquipIndex = iMsgID % 100
        oWkSelf = misc.WeakRef(self)
        
        def Save(*args):
            oSelf = oWkSelf()
            oView = oSelf.GetView()
            oModel = oSelf.GetModel()
            if not oSelf.CheckCanSave():
                return None
            
            oSelf.SaveData()
            oModel.SetSelectEquipIndex(iEquipIndex)
            oView.RefreshSelectEquipByIndex(iEquipIndex)
            netctysetequip.C2SRequestEquipInfoByPart(iEquipIndex, oSelf.GetProjectID())

        
        def Change(o = ((None, None), None)):
            oSelf = oWkSelf()
            oView = oSelf.GetView()
            oModel = oSelf.GetModel()
            oModel.SetSelectEquipIndex(iEquipIndex)
            oView.RefreshSelectEquipByIndex(iEquipIndex)
            netctysetequip.C2SRequestEquipInfoByPart(iEquipIndex, oSelf.GetProjectID())

        if self.GetModel().CheckDataIsChange():
            commondialog.ShowMessageBox('\xb7\xed\xabe\xc1\xd9\xa5\xbc\xbdT\xa9w\xa4\xe8\xae\xd7\xa1A\xbdT\xa9w\xabO\xa6s\xa7A\xb7\xed\xabe\xaa\xba\xb8\xcb\xb3\xc6\xb3]\xb8m\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (Save, Change))
            return None
        
        Change()

    
    def GetProjectID(self):
        return self.GetView().GetProjectID()

    
    def RequestEquipInfo(self):
        netctysetequip.C2SRequestEquipInfo(self.GetProjectID())

    
    def OnClose(self, oCB):
        oModel = self.GetModel()
        if oModel.CheckDataIsChange():
            self.GetView().ShowTips('\xa5\xbb\xac\xc9\xad\xb1\xaa\xba\xb3]\xb8m\xb5o\xa5\xcd\xa7\xef\xc5\xdc\xa1A\xacO\xa7_\xabO\xa6s\xb3]\xb8m\xa1H\nQ\xabO\xa6s\nQ\xa4\xa3\xabO\xa6s\nQ\xa8\xfa\xae\xf8', misc.Functor(self.OnConfirmSave, oCB))
            return None
        
        if oCB:
            pass
        oCB()

    
    def OnConfirmSave(self, oCB, iSelect):
        if iSelect == 1:
            self.SaveData()
        elif iSelect == 3:
            return None
        
        if oCB:
            pass
        oCB()

    
    def TJBtnNumClick(self, iMsgID):
        oModel = self.GetModel()
        iPos = iMsgID / 10
        iBtnIdx = iMsgID % 10
        sBeforeName = oModel.GetSpecialSkillNameByPos(iPos)
        if sBeforeName == '\xb5L':
            return None
        
        (ID, iLevel) = oModel.GetSpecialSkillInfo(iPos)
        tPoints = ctyequipdata.GetSkillPointsByKey(ID)
        if iBtnIdx == 2:
            if iLevel >= len(tPoints):
                usermacro.PROMPT_MSG('\xa4w\xb6W\xa5X\xbdd\xb3\xf2')
                return None
            
            if oModel.GetMaxSpecialSkillPoint() < tPoints[iLevel] + oModel.GetSpecialSkillPoint():
                usermacro.PROMPT_MSG('\xafS\xa7\xde\xc2I\xa4\xa3\xa8\xac')
                return None
            
            oModel.ChangeSpecailSkill(iPos, ID, iLevel + 1)
            oModel.AddSpecialSkillPoint(tPoints[iLevel])
        elif iLevel == 1:
            usermacro.PROMPT_MSG('\xa4w\xb6W\xa5X\xbdd\xb3\xf2')
            return None
        
        oModel.ChangeSpecailSkill(iPos, ID, iLevel - 1)
        oModel.AddSpecialSkillPoint(-tPoints[iLevel - 1])

    
    def SXBtnNumClick(self, iMsgID):
        import interface
        oModel = self.GetModel()
        iTMsgID = iMsgID
        if iMsgID >= interface.RIGHT_BUTTON_MESSAGE:
            iTMsgID = iMsgID - interface.RIGHT_BUTTON_MESSAGE
        
        iBtnIdx = None
        iPos = None
        tBtnMsgID = ([
            10,
            11], [
            12,
            13])
        for idx in xrange(len(tBtnMsgID)):
            if iTMsgID in tBtnMsgID[idx]:
                iPos = idx
                iBtnIdx = tBtnMsgID[idx].index(iTMsgID) + 1
                break
                continue
        
        if iBtnIdx is None or iPos is None:
            return None
        
        (ID, Num) = oModel.GetAddAttrInfoByPos(iPos)
        if ID == 6:
            usermacro.PROMPT_MSG('\xa4\xa3\xa5i\xc5\xdc\xa7\xf3\xb8\xd3\xc4\xdd\xa9\xca\xc2I')
            return None
        
        if ID == 0:
            return None
        
        if iBtnIdx == 2:
            if oModel.GetSingeAddAttrMaxPoint() <= Num:
                usermacro.PROMPT_MSG('\xb3\xe6\xc4\xdd\xa9\xca\xb3\xcc\xb0\xaa35\xa1A\xb3\xcc\xa7C15')
                return None
            
            if iMsgID >= interface.RIGHT_BUTTON_MESSAGE:
                oModel.ChangeAddAttrNumMaxOrMin(iPos, True)
                self.UpdateSXNum()
                return None
            
            oModel.ChangeAddAttrCostByPos(iPos, 1)
        elif oModel.GetSingeAddAttrMinPoint() >= Num:
            usermacro.PROMPT_MSG('\xb3\xe6\xc4\xdd\xa9\xca\xb3\xcc\xb0\xaa35\xa1A\xb3\xcc\xa7C15')
            return None
        
        if iMsgID >= interface.RIGHT_BUTTON_MESSAGE:
            oModel.ChangeAddAttrNumMaxOrMin(iPos, False)
            self.UpdateSXNum()
            return None
        
        oModel.ChangeAddAttrCostByPos(iPos, -1)
        self.UpdateSXNum()

    
    def UpdateSXNum(self):
        oModel = self.GetModel()
        for idx in range(2):
            (id, num) = oModel.GetAddAttrInfoByPos(idx)
            self.GetView().RefreshAddAttrNum(idx, num)
        

    
    def BSBtnNumClick(self, iMsgID):
        import interface
        oModel = self.GetModel()
        oView = self.GetView()
        iTMsgID = iMsgID
        if iMsgID >= interface.RIGHT_BUTTON_MESSAGE:
            iTMsgID = iMsgID - interface.RIGHT_BUTTON_MESSAGE
        
        iBtnIdx = None
        iPos = None
        tBtnMsgID = ([
            14,
            15], [
            16,
            17])
        for idx in xrange(len(tBtnMsgID)):
            if iTMsgID in tBtnMsgID[idx]:
                iPos = idx
                iBtnIdx = tBtnMsgID[idx].index(iTMsgID) + 1
                break
                continue
        
        if iBtnIdx is None or iPos is None:
            return None
        
        (ID, Num) = oModel.GetJewelsInfoByPos(iPos)
        if ID == 0:
            return None
        
        if iBtnIdx == 2:
            iSingleMax = oModel.GetSingleJewelMaxLevel(ID)
            if Num >= iSingleMax:
                if iSingleMax == 9:
                    usermacro.PROMPT_MSG('\xa4w\xb6W\xa5X\xbdd\xb3\xf2')
                else:
                    usermacro.PROMPT_MSG('\xa7\xdc\xa9\xca\xc4_\xa5\xdb\xb3\xcc\xb0\xaa8\xaf\xc5')
                return None
            
            if not oModel.CheckJewelCanAdd(iPos):
                usermacro.PROMPT_MSG('\xa4w\xb6W\xa5X\xbdd\xb3\xf2')
                return None
            
            if iMsgID >= interface.RIGHT_BUTTON_MESSAGE:
                oModel.ChangeJewelLevelMaxOrMin(iPos, True)
                self.UpdateBSNum()
                return None
            
            oModel.ChangeJewelLevelByPos(iPos, 1)
        elif Num <= 1:
            self.BoxLstClick(oView.FrameJewel[Num], '\xb5L')
            return None
        
        if iMsgID >= interface.RIGHT_BUTTON_MESSAGE:
            oModel.ChangeJewelLevelMaxOrMin(iPos, False)
            self.UpdateBSNum()
            return None
        
        oModel.ChangeJewelLevelByPos(iPos, -1)
        self.UpdateBSNum()

    
    def UpdateBSNum(self):
        oView = self.GetView()
        oModel = self.GetModel()
        for k, v in oModel.GetJewelsDic().items():
            oView.RefreshJewelLevel(k, v['iLevel'])
        



class CMagicEquipSetDelegate(delegatebase.CDelegateBase):
    
    def __init__(self, oView):
        self.m_iOrgTXIDList = []
        self.m_dOrgTJInfo = { }
        self.m_iBaseTJPoint = 0
        self.m_iBaseTXPoint = 0
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def GetView(self):
        '''
\t\t:rtype: dlgctysetequip_new.CMagicEquipSetDlg
\t\t:return:
\t\t'''
        return delegatebase.CDelegateBase.GetView(self)

    
    def Init(self):
        self.InitDlg()
        self.InitSignal()

    
    def InitDlg(self):
        oModel = mdctysetequip.GetEquipModel()
        dAllTJInfoList = oModel.GetSpecialSkillDetialList()
        dAllTXInfoList = oModel.GetEffectSkillDetialLst()
        dTmpTJInfoDict = oModel.GetAllSpecialSkillInfo()
        iCurTXID = oModel.GetEffectID()
        dCurTJInfoDict = { }
        for _, dInfo in dTmpTJInfoDict.iteritems():
            iSkillID = dInfo['ID']
            dCurTJInfoDict[iSkillID] = dInfo['iLevel']
        
        if iCurTXID:
            iCurTXIDList = [
                iCurTXID]
        else:
            iCurTXIDList = []
        import copy
        self.m_iOrgTXIDList = iCurTXIDList[:]
        self.m_dOrgTJInfo = copy.deepcopy(dCurTJInfoDict)
        iAllUseTJPoint = oModel.GetSpecialSkillPoint()
        iMagicUseTJPoint = 0
        for iTJID, iTimes in dCurTJInfoDict.iteritems():
            iMagicUseTJPoint += ctyequipdata.GetSkillCost(iTJID, iTimes)
        
        self.m_iBaseTJPoint = iAllUseTJPoint - iMagicUseTJPoint
        iAllUseTXPoint = oModel.GetUseEffectPoint()
        iMagicUseTXPoint = 0
        for iTXID in iCurTXIDList:
            iMagicUseTXPoint += ctyequipdata.GetEffectPointByKey(iTXID)
        
        self.m_iBaseTXPoint = iAllUseTXPoint - iMagicUseTXPoint
        oView = self.GetView()
        oView.RefreshTXList(dAllTXInfoList, iCurTXIDList)
        oView.RefreshTJList(self.SortTJList(dAllTJInfoList, dCurTJInfoDict), dCurTJInfoDict)
        self.RefreshTJPoint()
        self.RefreshTXPoint()

    
    def InitSignal(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_DoClose, self.OnClose)
        oView.ssConnect(oView.SS_DoSave, self.OnSave)
        oView.ssConnect(oView.SS_TJChg, self.OnTJChg)
        oView.ssConnect(oView.SS_TXChg, self.OnTXChg)

    
    def OnClose(self):
        import commondialog
        import misc
        if self.IsChange():
            commondialog.ShowMessageBox('\xb7\xed\xabe\xc1\xd9\xa5\xbc\xbdT\xa9w\xa4\xe8\xae\xd7\xa1A\xbdT\xa9w\xabO\xa6s\xa7A\xb7\xed\xabe\xaa\xba\xb8\xcb\xb3\xc6\xb3]\xb8m\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.OnSave), misc.Functor(self.DoClose)))
        else:
            self.GetView().DoClose()

    
    def DoClose(self, *args):
        self.GetView().DoClose()

    
    def OnSave(self, *args):
        if not self.CheckPoint():
            return None
        
        if not self.IsChange():
            usermacro.PROMPT_MSG('\xa7\xde\xaf\xe0\xa4\xe8\xae\xd7\xa8S\xb5o\xa5\xcd\xc5\xdc\xa4\xc6')
            return None
        
        dTJInfo = self.GetView().GetSelectTJInfo()
        iTXIDList = self.GetView().GetSelectTXList()
        if iTXIDList:
            iTXID = iTXIDList[0]
        else:
            iTXID = 0
        iTXUsePoint = self.GetUseTXPoint()
        oModel = mdctysetequip.GetEquipModel()
        oModel.ChangeSpecailSkillByDict(dTJInfo)
        oModel.ChangeSpecialEffect(iTXID, iTXUsePoint)
        netctysetequip.C2SSaveEquipInfo(oModel.GetEquipData(), self.GetView().GetProjectID())
        self.GetView().DoClose()

    
    def OnTJChg(self, iTJID, bSelect, iTimes):
        if bSelect and len(self.GetView().GetSelectTJInfo()) > 4:
            self.GetView().CancelTJ(iTJID)
            usermacro.PROMPT_MSG('\xaak\xc4_\xb3\xcc\xa6h\xc4\xe2\xb1a4\xba\xd8\xafS\xa7\xde')
            return None
        
        self.RefreshTJPoint()

    
    def OnTXChg(self, iTXID, bSelect):
        self.RefreshTXPoint()

    
    def RefreshTXPoint(self):
        iUseTXPoint = self.GetUseTXPoint()
        iMaxTXPoint = mdctysetequip.MAX_EFFECTPOINT
        self.GetView().SetTXPoint(iUseTXPoint, iMaxTXPoint)

    
    def GetUseTXPoint(self):
        iUseTXPoint = self.m_iBaseTXPoint
        iTXIDList = self.GetView().GetSelectTXList()
        for iTXID in iTXIDList:
            iUseTXPoint += ctyequipdata.GetEffectPointByKey(iTXID)
        
        return iUseTXPoint

    
    def RefreshTJPoint(self):
        iUseTJPoint = self.GetUseTJPoint()
        iMaxTJPoint = mdctysetequip.GetEquipModel().GetMaxSpecialSkillPoint()
        self.GetView().SetTJPoint(iUseTJPoint, iMaxTJPoint)

    
    def GetUseTJPoint(self):
        iUseTJPoint = self.m_iBaseTJPoint
        dTJInfo = self.GetView().GetSelectTJInfo()
        for iTJID, iTimes in dTJInfo.iteritems():
            iUseTJPoint += ctyequipdata.GetSkillCost(iTJID, iTimes)
        
        return iUseTJPoint

    
    def IsChange(self):
        iTXIDList = self.GetView().GetSelectTXList()
        if self.m_iOrgTXIDList == iTXIDList:
            bTXChg = False
        else:
            bTXChg = True
        bTJChg = False
        dTJInfo = self.GetView().GetSelectTJInfo()
        if len(dTJInfo) != len(self.m_dOrgTJInfo):
            bTJChg = True
        else:
            for iTJID, iTimes in dTJInfo.iteritems():
                if iTJID not in self.m_dOrgTJInfo:
                    bTJChg = True
                    break
                
                if self.m_dOrgTJInfo[iTJID] != iTimes:
                    bTJChg = True
                    break
                    continue
            
        if bTJChg or bTXChg:
            return True
        else:
            return False

    
    def CheckPoint(self):
        iUseTXPoint = self.GetUseTXPoint()
        iMaxTXPoint = mdctysetequip.MAX_EFFECTPOINT
        if iUseTXPoint > iMaxTXPoint:
            usermacro.PROMPT_MSG('\xafS\xae\xc4\xc2I\xb6W\xa5X\xa4W\xad\xad\xa1A\xbd\xd0\xad\xab\xb7s\xbd\xd5\xbe\xe3')
            return False
        
        iUseTJPoint = self.GetUseTJPoint()
        iMaxTJPoint = mdctysetequip.GetEquipModel().GetMaxSpecialSkillPoint()
        if iUseTJPoint > iMaxTJPoint:
            usermacro.PROMPT_MSG('\xafS\xa7\xde\xc2I\xb6W\xa5X\xa4W\xad\xad\xa1A\xbd\xd0\xad\xab\xb7s\xbd\xd5\xbe\xe3')
            return False
        
        return True

    
    def SortTJList(self, dAllTJInfoList, dCurTJInfoDict):
        dTmpList1 = []
        dTmpList2 = []
        for dInfo in dAllTJInfoList:
            if dInfo['iID'] in dCurTJInfoDict:
                dTmpList1.append(dInfo)
                continue
            dTmpList2.append(dInfo)
        
        return dTmpList1 + dTmpList2
