# pycdc 交叉复核产物 · script.fls entry 2564
# co_filename(原始)='script/mxgame/appearance/delegate/delegateoutward/dgtappearancehsv.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2564.pyc (Python 2.5)

'''
'''
import csopenui
import random
import charinterface
import charpath
import commondialog
import delegatebase
import hero
import item
import netappearance
import newmdappearancefreecolor
import mdheroshapedesc
import misc
import netopenui
import usermacro
import chardefine
import hsvpaldata
import permission

def GetSelfRoleShowMgr():
    return mdheroshapedesc.GetRoleShapeDescMgr('CAppearanceShapeMainView')


def GetMakeRoleShowMgr():
    return mdheroshapedesc.GetRoleShapeDescMgr('CMakeHsvPalDlg')


def GetUnFixHSV(iShape, iPart, iHue, iSat, iVal):
    (iUnHue, iUnSat, iUnVal) = hsvpaldata.GetUnFixHSV(iShape, iPart, iHue, iSat, iVal)
    if (iHue, iSat, iVal) != hsvpaldata.GetFixHSV(iShape, iPart, iUnHue, iUnSat, iUnVal):
        for i in range(max(iUnHue - 5, 0), min(iUnHue + 5, 361)):
            for j in range(max(iUnSat - 5, 0), min(iUnSat + 5, 101)):
                for k in range(max(iUnVal - 5, 0), min(iUnVal + 5, 101)):
                    if hsvpaldata.GetFixHSV(iShape, iPart, i, j, k) == (iHue, iSat, iVal):
                        LOG_DEBUG('\xacV\xa6\xe2\xae\xd5\xa5\xbf>>>>>>>\xb5\xb2\xaaG>>', iShape, iPart, i, j, k, ' >>>\xad\xec\xa9l>>', iUnHue, iUnSat, iUnVal)
                        return (i, j, k)
                        continue
                
            
        
    
    return (iUnHue, iUnSat, iUnVal)


class CDelegateHsvBase(delegatebase.CDelegateBase):
    
    def GetView(self):
        ''':rtype: newappearancefreecolorview.CHsvPalDlg'''
        return delegatebase.CDelegateBase.GetView(self)



class CDelegateHsvMakeBase(delegatebase.CDelegateBase):
    
    def GetView(self):
        ''':rtype: newappearancefreecolorview.CMakeHsvPalDlg'''
        return delegatebase.CDelegateBase.GetView(self)



class CDelegateSameHsvBase(delegatebase.CDelegateBase):
    
    def GetView(self):
        ''':rtype: newappearancefreecolorview.CHsvPalDlg or newappearancefreecolorview.CMakeHsvPalDlg'''
        return delegatebase.CDelegateBase.GetView(self)



class CDelegateHsvMain(CDelegateSameHsvBase):
    
    def __init__(self, oView, sRoleType):
        self.m_sRoleType = sRoleType
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oHeroHsvMgr.ssConnect(oHeroHsvMgr.SS_UpdateInitData, self.OnUpdateInitData)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateIsFirstChangeHsv, self.OnUpdateIsFirstChangeHsv)
        self.OnUpdateInitData()
        self.SetIsFirstChangeHsv()

    
    def GetRoleShowMgr(self):
        return mdheroshapedesc.GetRoleShapeDescMgr(self.m_sRoleType)

    
    def SetIsFirstChangeHsv(self, bIsFirstChangeHsv = None):
        '''
\t\t\xb5\xa6\xa6E\xbb\xdd\xa8D\xa1A\xb2\xc4\xa4@\xa6\xb8\xb6}\xb1\xd2\xac\xc9\xad\xb1\xa6p\xaaG\xa8\xad\xa4W\xa8S\xa6\xb3HSV\xacV\xa6\xe2\xa1A\xabh\xa5\xfd\xc5\xe3\xa5\xdc\xb4\xb6\xb3q\xacV\xa6\xe2\xa1A\xaa\xbd\xa8\xec\xa5L\xb6i\xa6\xe6\xb9L\xbe\xde\xa7@
\t\t:param bIsFirstChangeHsv:
\t\t:return:
\t\t'''
        oRoleShowMgr = self.GetRoleShowMgr()
        if bIsFirstChangeHsv is None:
            oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
            bIsFirstChangeHsv = oHsvPalMgr.GetIsFirstChangeHsv()
        
        (_, dHeroDesc) = charpath.GetHeroShow()
        if not bIsFirstChangeHsv and self.m_sRoleType == 'CAppearanceShapeMainView' and not dHeroDesc.get(chardefine.DESC.KEY_HERO_HSV, None):
            oRoleShowMgr.DelDescKeyNotRange(chardefine.DESC.COLOR)
            oRoleShowMgr.AddDescKeyNotRange(chardefine.DESC.KEY_HERO_HSV)
        else:
            oRoleShowMgr.DelDescKeyNotRange(chardefine.DESC.KEY_HERO_HSV)
            oRoleShowMgr.AddDescKeyNotRange(chardefine.DESC.COLOR)
        oRoleShowMgr.UpdateShapeDesc()

    
    def OnUpdateInitData(self):
        oView = self.GetView()
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oView.SetTipsShow(bool(oHeroHsvMgr.GetHasCount()))
        if not oHeroHsvMgr.GetFisrtHsv():
            oView.SetFirsetText('\xacV\xa6\xe2\xaa\xac\xbaA,\xa9\xd2\xa6\xb3\xb3\xa1\xa6\xec\xa5\xc3\xa4[\xacV\xa6\xe2')
        

    
    def OnUpdateIsFirstChangeHsv(self, bIsFirstChangeHsv):
        self.SetIsFirstChangeHsv(bIsFirstChangeHsv)



class CDelegateHuoLiChange(CDelegateSameHsvBase):
    
    def __init__(self, oView, iType):
        self.m_iType = iType
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        hero.AddRefreshCallback('CDelegateHuoLiChange', ('m_Huoli',), self.OnHuoLiChange)
        if self.m_iType == 1:
            oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
            oHeroHsvMgr.ssConnect(oHeroHsvMgr.SS_UpdateInitData, self.OnHuoLiChange)
        

    
    def OnHuoLiChange(self):
        oView = self.GetView()
        if self.m_iType == 1:
            iNeedHuoLi = newmdappearancefreecolor.GetHeroHsvMgr().GetInitNum()
            iHave = item.GetItemNum(25853)
            sMsg = '\xa4\xdb\xb1m'
        else:
            iNeedHuoLi = 300
            iHave = hero.GetProp('m_Huoli')
            sMsg = '\xac\xa1\xa4O'
        if not iNeedHuoLi:
            sShowMsg = ''
        else:
            sShowMsg = '%s\xa1G%d/%d' % (sMsg, iHave, iNeedHuoLi)
        oView.SetHuoLiText(sShowMsg)



class CDelegateHsvPosChange(CDelegateSameHsvBase):
    
    def __init__(self, oView, sRoleType):
        self.m_sRoleType = sRoleType
        delegatebase.CDelegateBase.__init__(self, oView)

    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnSliderChange, self.OnSliderChange)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateUnFixHsv, self.OnUpdateUnFixHsv)

    
    def GetRoleShowMgr(self):
        return mdheroshapedesc.GetRoleShapeDescMgr(self.m_sRoleType)

    
    def OnSliderChange(self, iType, iPos):
        '''\xb1\xf8\xbf\xef\xbe\xdc\xa6^\xbd\xd5'''
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.SetIsFirstChangeHsv(True)
        iChoosePart = oHsvPalMgr.GetChoosePart()
        iLastChoosePart = oHsvPalMgr.GetLastChoosePart()
        if iChoosePart != iLastChoosePart and len(iChoosePart) > 1:
            for iEachType in range(3):
                oHsvPalMgr.SetUnFixHSVHsvPalList(iChoosePart, iEachType, oHsvPalMgr.GetUnFixHSVHsvPal(iLastChoosePart[0], iEachType))
            
        
        oHsvPalMgr.SetUnFixHSVHsvPalList(iChoosePart, iType, iPos)
        oHsvPalMgr.UpdateUnFixHsv()

    
    def OnUpdateUnFixHsv(self):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oView = self.GetView()
        oRoleShowMgr = self.GetRoleShowMgr()
        iShape = oRoleShowMgr.GetShape()
        oRoleShowMgr.SetDescWithKey(chardefine.DESC.KEY_HERO_HSV, oHsvPalMgr.GetHsvPal(iShape))
        oView.OnUpdateUnFixHsv()



class CDelegateHsvPartTapChange(CDelegateSameHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickChangePart, self.OnClickChangePart)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.SetChoosePart([
            0,
            1,
            2])
        oHsvPalMgr.SetLastChoosePart([
            0])
        oView.SetPartBtnSelect(3, True)

    
    def OnClickChangePart(self, iPartList):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.SetLastChoosePart(oHsvPalMgr.GetChoosePart())
        oHsvPalMgr.SetChoosePart(iPartList)
        oHsvPalMgr.UpdateUnFixHsv()



class CDelegateHsvRandom(CDelegateSameHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickRandom, self.OnRandom)

    
    def OnRandom(self):
        '''
\t\t\xae\xda\xbe\xda\xbf\xef\xbe\xdc\xaa\xba\xb3\xa1\xa6\xec\xc0H\xbe\xf7hsv\xbc\xc6\xad\xc8\xa1A\xa8\xe4\xa4\xa4\xa5\xfe\xbf\xef\xae\xc9\xadn\xb9\xef3\xad\xd3\xb3\xa1\xa6\xec\xa6@9\xad\xd3hsv\xad\xc8\xb6i\xa6\xe6\xc0H\xbe\xf7
\t\t'''
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.SetIsFirstChangeHsv(True)
        iChoosePartList = oHsvPalMgr.GetChoosePart()
        dMax = {
            0: 360,
            1: 100,
            2: 100 }
        for iType in range(3):
            oHsvPalMgr.SetUnFixHSVHsvPalList(iChoosePartList, iType, random.randint(0, dMax[iType]))
        
        oHsvPalMgr.UpdateUnFixHsv()



class CDelegateHsvResetSelfPal(CDelegateHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickResetSelfPal, self.OnResetSelfPal)

    
    def OnResetSelfPal(self):
        '''\xc2I\xc0\xbb\xac\xc9\xad\xb1\xc1\xd9\xad\xec'''
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        (_, dDesc) = charpath.GetHeroShow()
        if chardefine.DESC.KEY_HERO_HSV in dDesc:
            iHsvList = dDesc[chardefine.DESC.KEY_HERO_HSV]
            for iPart in range(3):
                iUnFixHSVList = GetUnFixHSV(GetSelfRoleShowMgr().GetShape(), iPart + 1, iHsvList[iPart][0], iHsvList[iPart][1], iHsvList[iPart][2])
                for iType, iPos in enumerate(iUnFixHSVList):
                    oHsvPalMgr.SetUnFixHSVHsvPalList([
                        iPart], iType, iPos)
                
            
        else:
            oHsvPalMgr.ResetUnFixHSVHsvPalList()
        oHsvPalMgr.UpdateUnFixHsv()



class CDelegateHsvOwnTab(CDelegateHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickSelectOwnTab, self.OnSelectOwnTab)
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oHeroHsvMgr.ssConnect(oHeroHsvMgr.SS_UpdateHeroSaveHsv, self.OnUpdateHeroSaveHsv)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_SetImitateColor, self.SetImitateColor)
        self.OnSelectOwnTab(17)
        self.SetHsvOwnTab()

    
    def OnSelectOwnTab(self, iMsgID):
        if iMsgID >= 32:
            iMsgID -= 13
        
        oView = self.GetView()
        oView.SetRegainShow(iMsgID == 17)
        oView.SetOwnCancelShow(iMsgID - 17 != 0)
        self.OnSwitchTap(iMsgID - 17)
        self.RefreshOwnPalCase(iMsgID - 17)

    
    def OnSwitchTap(self, iSwitch):
        oView = self.GetView()
        for i, sButton in enumerate([
            'btn_own1',
            'btn_own2',
            'btn_own3',
            'btn_own4']):
            if i == iSwitch:
                oView.GetObject(sButton).SetSelect(True)
                continue
            oView.GetObject(sButton).SetSelect(False)
        

    
    def RefreshOwnPalCase(self, iKey):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        dPalInfo = newmdappearancefreecolor.GetHeroHsvMgr().GetHeroSelfSaveHsv()
        if iKey == 0:
            oHsvPalMgr.SetKey(iKey)
            (_, dDesc) = charpath.GetHeroShow()
            if 'hsvpal' in dDesc:
                iHsvList = dDesc['hsvpal']
                for iPart in range(3):
                    iUnFixHSVList = GetUnFixHSV(GetSelfRoleShowMgr().GetShape(), iPart + 1, iHsvList[iPart][0], iHsvList[iPart][1], iHsvList[iPart][2])
                    for iType, iPos in enumerate(iUnFixHSVList):
                        oHsvPalMgr.SetUnFixHSVHsvPalList([
                            iPart], iType, iPos)
                    
                
            else:
                oHsvPalMgr.ResetUnFixHSVHsvPalList()
            oHsvPalMgr.UpdateUnFixHsv()
            return None
        
        if iKey not in dPalInfo and iKey != 0:
            usermacro.PROMPT_MSG('\xb7\xed\xabe\xa9|\xa5\xbc\xa6\xac\xc2\xc3\xb9L\xb8\xd3\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa1A\xa6\xac\xc2\xc3\xab\xe1\xa5i\xc0H\xae\xc9\xa8\xd3\xacd\xac\xdd\xbe\xbe')
            return None
        
        oHsvPalMgr.SetIsFirstChangeHsv(True)
        oHsvPalMgr.SetKey(iKey)
        iHsvList = dPalInfo[iKey][1:]
        for iPart in range(3):
            iUnFixHSVList = GetUnFixHSV(GetSelfRoleShowMgr().GetShape(), iPart + 1, iHsvList[3 * iPart], iHsvList[3 * iPart + 1], iHsvList[3 * iPart + 2])
            for iType, iPos in enumerate(iUnFixHSVList):
                oHsvPalMgr.SetUnFixHSVHsvPalList([
                    iPart], iType, iPos)
            
        
        oHsvPalMgr.UpdateUnFixHsv()

    
    def SetImitateColor(self, iShape, tColorList):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oView = self.GetView()
        GetSelfRoleShowMgr().DelDescKeyNotRange(chardefine.DESC.KEY_HERO_HSV)
        for iPart in range(3):
            iUnFixHSVList = GetUnFixHSV(iShape, iPart + 1, tColorList[iPart][0], tColorList[iPart][1], tColorList[iPart][2])
            for iType, iPos in enumerate(iUnFixHSVList):
                oHsvPalMgr.SetUnFixHSVHsvPalList([
                    iPart], iType, iPos)
            
        
        self.SetLogColorList(tColorList)
        oView.SetiPartBtnSelectTrue(0)
        oHsvPalMgr.SetChoosePart([
            0])
        oHsvPalMgr.UpdateUnFixHsv()

    
    def SetLogColorList(self, tColorList):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        tTmpList = oHsvPalMgr.GetHsvPal(hero.GetProp('m_Shape'))
        iLogColorList = []
        for tList in tTmpList:
            iLogColorList.append(tList[0])
            iLogColorList.append(tList[1])
            iLogColorList.append(tList[2])
        
        newmdappearancefreecolor.GetHsvPalMgr().SetCopyColorList(iLogColorList)

    
    def GetHsvByShape(self, lFixHSVHsvPalList, iShape):
        for iHue, iSat, iVal in enumerate(lFixHSVHsvPalList):
            iHue = max(min(iHue, 360), 0)
            iSat = max(min(iSat, 100), 0)
            iVal = max(min(iVal, 100), 0)
            lFixHSVHsvPalList[iPart] = list(hsvpaldata.GetFixHSV(iShape, iPart + 1, iHue, iSat, iVal))
        
        return lFixHSVHsvPalList

    
    def SetHsvOwnTab(self):
        oView = self.GetView()
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        dPosToName = {
            1: 'btn_own2',
            2: 'btn_own3',
            3: 'btn_own4' }
        if permission.IsTestServerByNewYanzhiguan():
            oView.GetObject('btn_own1').SetText('\xb7\xed\xabe', True)
        
        for iPos, iList in oHeroHsvMgr.GetHeroSelfSaveHsv().iteritems():
            if iPos not in dPosToName:
                continue
            
            if permission.IsTestServerByNewYanzhiguan():
                sChineseNum = [
                    '\xa4@',
                    '\xa4G',
                    '\xa4T']
                oView.GetObject(dPosToName[iPos]).SetText('\xa6\xac\xc2\xc3%s' % sChineseNum[iPos - 1], True)
            else:
                oView.GetObject(dPosToName[iPos]).SetText('\xa6\xac\xc2\xc3%d' % iPos)
            oView.GetObject(dPosToName[iPos]).FakeEnable(True)
            del dPosToName[iPos]
        
        for iPos, sName in dPosToName.iteritems():
            if permission.IsTestServerByNewYanzhiguan():
                oView.GetObject(dPosToName[iPos]).SetText('\xb5L', True)
            else:
                oView.GetObject(dPosToName[iPos]).SetText('\xb5L')
            oView.GetObject(dPosToName[iPos]).FakeEnable(False, '\xb7\xed\xabe\xa9|\xa5\xbc\xa6\xac\xc2\xc3\xb9L\xb8\xd3\xbd\xd5\xa6\xe2\xa4\xe8\xae\xd7,\xa6\xac\xc2\xc3\xab\xe1\xa5i\xa5H\xc0H\xae\xc9\xa8\xd3\xacd\xac\xdd\xae@')
            oView.GetObject(dPosToName[iPos]).SetFrame(0)
        

    
    def OnUpdateHeroSaveHsv(self):
        oModel = newmdappearancefreecolor.GetHsvPalMgr()
        bImitateChange = oModel.GetIsImitateChangeHsv()
        if bImitateChange:
            oModel.SetImitateChangeHsv(False)
            return None
        
        self.OnSelectOwnTab(17)
        self.SetHsvOwnTab()



class CDelegateHsvSavePal(CDelegateHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickSavePal, self.OnSavePal)

    
    def OnSavePal(self):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if oHsvPalMgr.GetKey() != 0:
            commondialog.ShowMessageBox('\xacO\xa7_\xabO\xa6s\xb8\xd3\xa4\xe8\xae\xd7\xa1H', ('\xabO\xa6s', '\xbf\xef\xbe\xdc\xb4\xc0\xb4\xab'), (misc.Functor(self.SaveOwnPal), misc.Functor(self.ShowReplaceDlg)), bIsIgnoreCBSelfParameter = True)
        else:
            self.SaveOwnPal()

    
    def SaveOwnPal(self):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        iShape = GetSelfRoleShowMgr().GetShape()
        self.SendSavePal(iShape, oHsvPalMgr.GetHsvPal(iShape))

    
    def SendSavePal(self, iShape, lHsvPallist):
        iHsvPallist = []
        for lInfo in lHsvPallist:
            iHsvPallist.append(lInfo[0])
            iHsvPallist.append(lInfo[1])
            iHsvPallist.append(lInfo[2])
        
        dHeroSaveHsv = newmdappearancefreecolor.GetHeroHsvMgr().GetHeroSelfSaveHsv()
        if 0 in dHeroSaveHsv:
            iLen = len(dHeroSaveHsv) - 1
        else:
            iLen = len(dHeroSaveHsv)
        iKey = 1
        if iLen < 3:
            for i in xrange(1, 4):
                if i not in dHeroSaveHsv:
                    iKey = i
                    break
                    continue
            
            netappearance.C2GSAppearanceSaveFreeDye(1, iKey, iShape, iHsvPallist)
        else:
            commondialog.ShowMessageBox('\xb1z\xb7\xed\xabe\xaa\xba\xa6\xac\xc2\xc3\xa4\xe8\xae\xd7\xa4w\xba\xa1\xacO\xa7_\xb4\xc0\xb4\xab\xa8\xe4\xa4\xa4\xa4@\xba\xd8\xa4\xe8\xae\xd7\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.ShowReplaceDlg), None), bIsIgnoreCBSelfParameter = True)

    
    def ShowReplaceDlg(self):
        oView = self.GetView()
        oView.ShowReplaceDlg()



class CDelegateHsvMakeHsvPal(CDelegateHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickMakeHsvPal, self.OnClickMakeHsvPal)

    
    def OnClickMakeHsvPal(self):
        '''\xbdT\xbb{\xbd\xd5\xa6\xe2'''
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        if oHeroHsvMgr.GetFisrtHsv():
            if oHeroHsvMgr.GetInitNum() > 0:
                sMsg = '\xb4\xb6\xb3q\xacV\xa6\xe2\xa4\xe8\xae\xd7\xb1N\xb3Q\xc2\xd0\xbb\\,\xbdT\xa9w\xadn\xa8\xcf\xa5\xce%d\xa4\xdb\xb1m\xb6i\xa6\xe6\xb8\xd1\xc2\xea\xa8\xc3\xa5B\xacV\xa6\xe2\xb6\xdc\xa1H' % oHeroHsvMgr.GetInitNum()
            else:
                sMsg = '\xad\xec\xa6\xb3\xaa\xba\xacV\xa6\xe2\xa4\xe8\xae\xd7\xb1N\xa4\xa3\xabO\xafd,\xbdT\xa9w\xadn\xb6i\xa6\xe6\xb8\xd1\xc2\xea\xa8\xc3\xa5B\xbd\xd5\xa6\xe2\xb6\xdc\xa1H'
            commondialog.ShowMessageBox(sMsg, ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.OnConfirm), None), bIsIgnoreCBSelfParameter = True)
        else:
            self.OnConfirm()

    
    def OnConfirm(self):
        newmdappearancefreecolor.GetHsvPalMgr().OnConfirm()



class CDelegateHsvDelSavePal(CDelegateHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickDelSavePal, self.OnClickDelSavePal)

    
    def OnClickDelSavePal(self):
        commondialog.ShowMessageBox('\xb1z\xbf\xef\xbe\xdc\xa4F\xa7R\xb0\xa3\xb7\xed\xabe\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa1A\xa7R\xb0\xa3\xab\xe1\xb1N\xb5L\xaak\xab\xec\xb4_\xa1A\xbdT\xbb{\xa7R\xb0\xa3\xa6\xb9\xa4\xe8\xae\xd7\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.CancelOwnSave), None), bIsIgnoreCBSelfParameter = True)

    
    def CancelOwnSave(self):
        iKey = newmdappearancefreecolor.GetHsvPalMgr().GetKey()
        netappearance.C2GSAppearanceDelFreeDye(1, iKey)



class CDelegateHsvMakeTicket(CDelegateHsvMakeBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickMakeHsvPal, self.OnMakeTicket)

    
    def OnMakeTicket(self):
        if hero.GetProp('m_Huoli') < 300:
            usermacro.PROMPT_MSG('\xb1z\xaa\xba\xac\xa1\xa4O\xa4\xa3\xa8\xac!')
            return None
        
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        iShape = GetMakeRoleShowMgr().GetShape()
        iList = []
        for tList in oHsvPalMgr.GetHsvPal(iShape):
            iList.append(tList[0])
            iList.append(tList[1])
            iList.append(tList[2])
        
        netopenui.C2SMakeHsvTicket(iShape, iList)



class CDelegateHsvDelMakeSavePal(CDelegateHsvMakeBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickDelSavePal, self.OnClickDelSavePal)

    
    def OnClickDelSavePal(self):
        commondialog.ShowMessageBox('\xb1z\xbf\xef\xbe\xdc\xa4F\xa7R\xb0\xa3\xb7\xed\xabe\xacV\xa6\xe2\xa4\xe8\xae\xd7\xa1A\xa7R\xb0\xa3\xab\xe1\xb1N\xb5L\xaak\xab\xec\xb4_\xa1A\xbdT\xbb{\xa7R\xb0\xa3\xa6\xb9\xa4\xe8\xae\xd7\xb6\xdc\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.CancelSave), None), bIsIgnoreCBSelfParameter = True)

    
    def CancelSave(self):
        iKey = newmdappearancefreecolor.GetHsvPalMgr().GetSelectMakeKey()
        netappearance.C2GSAppearanceDelFreeDye(2, iKey)



class CDelegateHsvMakeSavePal(CDelegateHsvMakeBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickSavePal, self.SendSavePal)

    
    def SendSavePal(self):
        iShape = GetMakeRoleShowMgr().GetShape()
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        dInfo = oHeroHsvMgr.GetMakeTicketSaveHsv()
        iPos = oHsvPalMgr.GetSelectMakeKey()
        iNewList = []
        for lInfo in oHsvPalMgr.GetHsvPal(iShape):
            iNewList.append(lInfo[0])
            iNewList.append(lInfo[1])
            iNewList.append(lInfo[2])
        
        if iPos == 0 and len(dInfo) >= 10:
            commondialog.ShowMessageBox('\xb1z\xb7\xed\xabe\xaa\xba\xa6\xac\xc2\xc3\xa4\xe8\xae\xd7\xa4w\xba\xa1\xacO\xa7_\xb4\xc0\xb4\xab\xa8\xe4\xa4\xa4\xa4@\xba\xd8\xa4\xe8\xae\xd7\xa1H', ('\xbdT\xa9w', '\xa8\xfa\xae\xf8'), (misc.Functor(self.ShowReplaceDlg), None))
        else:
            for iHavelist in dInfo.itervalues():
                iTempList = iHavelist[1:]
                if iTempList == iNewList and iHavelist[0] == iShape:
                    usermacro.PROMPT_MSG('\xa6\xe7\xcf@\xa4\xa4\xa4w\xa5]\xa7t\xb7\xed\xabe\xac\xdb\xa6P\xaa\xba\xacV\xa6\xe2\xa4\xe8\xae\xd7')
                    return None
                    continue
            
            for i in xrange(10):
                if i + 1 not in dInfo.keys():
                    iPos = i + 1
                    break
                    continue
            
            netappearance.C2GSAppearanceSaveFreeDye(2, iPos, iShape, iNewList)

    
    def ShowReplaceDlg(self):
        oView = self.GetView()
        oView.ShowReplaceDlg()



class CDelegateHsvMakeOwnTab(CDelegateHsvMakeBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickSelectOwnTab, self.OnClickSelectOtherPalTab)
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oHeroHsvMgr.ssConnect(oHeroHsvMgr.SS_UpdateHeroSaveHsv, self.OnUpdateHeroSaveHsv)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateChooseMakeTabType, self.OnUpdateChooseMakeTabType)
        oHsvPalMgr.SetChooseMakeTabType(38)

    
    def SelectOtherPalTab(self, iMsgID):
        '''\xa4\xc1\xb4\xab\xad\xb6\xc3\xb1'''
        dInfo = newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        self.SwitchSaveTap(iMsgID - 38)
        self.RefreshSaveBtn()
        if iMsgID == 38:
            oHsvPalMgr.ResetUnFixHSVHsvPalList()
            oHsvPalMgr.UpdateUnFixHsv()
        elif len(dInfo) == 0:
            usermacro.PROMPT_MSG('\xa7A\xa8S\xa6\xb3\xa6\xac\xc2\xc3\xa4\xe8\xae\xd7')
            return None
        
        oHsvPalMgr.SetSelectMakeKey(dInfo.keys()[0])

    
    def SwitchSaveTap(self, iSwitch):
        oView = self.GetView()
        for i, sButton in enumerate([
            'btn_other1',
            'btn_other2']):
            if i == iSwitch:
                oView.GetObject(sButton).SetSelect(True)
                continue
            oView.GetObject(sButton).SetSelect(False)
        

    
    def RefreshSaveBtn(self):
        oView = self.GetView()
        if len(newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()) <= 0:
            oView.GetObject('btn_other2').FakeEnable(False, '\xb7\xed\xabe\xa9|\xa5\xbc\xa6\xac\xc2\xc3\xb9L\xbd\xd5\xa6\xe2\xa4\xe8\xae\xd7,\xa6\xac\xc2\xc3\xab\xe1\xa5i\xa5H\xc0H\xae\xc9\xa8\xd3\xacd\xac\xdd\xae@')
            oView.GetObject('btn_other2').SetFrame(0)
        else:
            oView.GetObject('btn_other2').FakeEnable(True)

    
    def OnClickSelectOtherPalTab(self, iMsgID):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.SetChooseMakeTabType(iMsgID)

    
    def OnUpdateHeroSaveHsv(self):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if len(newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()) <= 0:
            oHsvPalMgr.SetChooseMakeTabType(38)
        else:
            self.RefreshSaveBtn()

    
    def OnUpdateChooseMakeTabType(self, iChooseMakeTabType):
        self.SelectOtherPalTab(iChooseMakeTabType)



class CDelegateHsvMakeChooseTicket(CDelegateHsvMakeBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickChooseMake, self.OnClickPageChange)
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oHeroHsvMgr.ssConnect(oHeroHsvMgr.SS_UpdateHeroSaveHsv, self.OnUpdateHeroSaveHsv)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateSelectMakeKey, self.OnUpdateSelectMakeKey)

    
    def RefreshSavePal(self):
        oView = self.GetView()
        dInfo = newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if oHsvPalMgr.GetChooseMakeTabType() != 39:
            return None
        
        iHsvList = dInfo.get(oHsvPalMgr.GetSelectMakeKey(), [
            111,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0])
        iShape = iHsvList[0]
        iHsvList = iHsvList[1:]
        for iPart in range(3):
            iUnFixHSVList = GetUnFixHSV(iShape, iPart + 1, iHsvList[3 * iPart], iHsvList[3 * iPart + 1], iHsvList[3 * iPart + 2])
            for iType, iPos in enumerate(iUnFixHSVList):
                oHsvPalMgr.SetUnFixHSVHsvPalList([
                    iPart], iType, iPos)
            
        
        GetMakeRoleShowMgr().SetShape(iShape)
        GetMakeRoleShowMgr().SetDescWithKey(chardefine.DESC.KEY_HERO_HSV, oHsvPalMgr.GetHsvPal(iShape))
        GetMakeRoleShowMgr().UpdateShapeDesc()
        oHsvPalMgr.UpdateUnFixHsv()
        oView.SetOtherSaveText(oHsvPalMgr.GetSelectMakeKey(), iShape)

    
    def OnClickPageChange(self, bAdd):
        dInfo = newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if oHsvPalMgr.GetChooseMakeTabType() != 39:
            return None
        
        iList = dInfo.keys()
        iList.sort()
        iSelectKey = oHsvPalMgr.GetSelectMakeKey()
        if iSelectKey in iList:
            iPos = iList.index(iSelectKey)
            iNewPos = iPos + bAdd
            if iNewPos <= iNewPos:
                pass
            elif iNewPos < len(iList):
                iNewMakeKey = iList[iNewPos]
            else:
                iNewMakeKey = iSelectKey
        elif iList:
            iNewMakeKey = iList[0]
        else:
            return None
        oHsvPalMgr.SetSelectMakeKey(iNewMakeKey)

    
    def OnUpdateHeroSaveHsv(self):
        self.OnClickPageChange(0)

    
    def OnUpdateSelectMakeKey(self, iSelectMakeKey):
        self.RefreshSavePal()



class CDelegateHsvMakeChooseShape(CDelegateHsvMakeBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickShapeChange, self.OnClickShapeChange)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateSelectShape, self.OnUpdateSelectShape)
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateSelectMakeKey, self.OnUpdateSelectMakeKey)
        oHsvPalMgr.ssConnect(oHsvPalMgr.SS_UpdateChooseMakeTabType, self.OnUpdateChooseMakeTabType)
        oHsvPalMgr.SetSelectShape(111)

    
    def OnClickShapeChange(self, iShape):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        oHsvPalMgr.SetSelectShape(iShape)

    
    def OnUpdateSelectShape(self, iShape):
        oView = self.GetView()
        oView.SetSelectShapeText(charinterface.GetHeroShapeName(iShape))
        GetMakeRoleShowMgr().SetShape(iShape)
        GetMakeRoleShowMgr().UpdateShapeDesc()

    
    def OnUpdateSelectMakeKey(self, iSelectMakeKey):
        dInfo = newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        iHsvList = dInfo.get(oHsvPalMgr.GetSelectMakeKey(), [
            111,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0])
        oHsvPalMgr.SetSelectShape(iHsvList[0])

    
    def OnUpdateChooseMakeTabType(self, iChooseMakeTabType):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if iChooseMakeTabType == 38:
            oHsvPalMgr.SetSelectShape(GetMakeRoleShowMgr().GetShape())
        



class CDelegateGiftBox(CDelegateHsvBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickGiftBtn, self.OnClickGiftBtn)
        oView.ssConnect(oView.SS_ClickOthersPayBtn, self.OnClickOthersPayBtn)

    
    def OnClickOthersPayBtn(self):
        import netappearance
        import appearancedefine
        import hero
        import newmdappearancefreecolor
        tmplist = newmdappearancefreecolor.GetHsvPalMgr().GetHsvPal(hero.GetProp('m_Shape'))
        lst = []
        for tList in tmplist:
            lst.append(tList[0])
            lst.append(tList[1])
            lst.append(tList[2])
        
        netappearance.C2GSOpenGiftDlgForHsvColor(appearancedefine.GIFT_TYPE_PAY_FREE_COLOR, lst)

    
    def OnClickGiftBtn(self):
        import netappearance
        import appearancedefine
        netappearance.C2SOpenGiftDlg(appearancedefine.GIFT_TYPE_COLOR_2, 0)
