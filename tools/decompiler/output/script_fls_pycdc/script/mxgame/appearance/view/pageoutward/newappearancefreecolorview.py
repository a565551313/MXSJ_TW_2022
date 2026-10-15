# pycdc 交叉复核产物 · script.fls entry 2405
# co_filename(原始)='script/mxgame/appearance/view/pageoutward/newappearancefreecolorview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2405.pyc (Python 2.5)

import copy
import appearancedefine
import chardefine
import charinterface
import combdialog
import combmacro
import delegateappearanceoperate
import dgtappearancehsv
import interface
import mdheroshapedesc
import misc
import netappearance
import netopenui
import newmdappearancefreecolor
import permission
import roleshapdesc
import selectrolecolor
import slot
import style
import walker
import csopenui
ROLELIST = [
    '\xb3p\xbb\xbb\xabL',
    '\xc5R\xc6E\xa4\xf5',
    '\xad\xb7\xb9a\xa8\xe0',
    '\xad\xe2\xaai\xbfP',
    '\xb6\xb3\xb5L\xa4\xdf',
    '\xa4\xd1\xc2\xcd\xa4l',
    '\xb2H\xb2M\xac\xee',
    '\xa5\xc9\xc3\xb9\xabb',
    '\xc3t\xb4\xf0\xa4l',
    '\xaa\xa2\xa6p\xad\xb7',
    '\xa4d\xa4\xdb\xbd\xba',
    '\xb5\xb5\xb9\xe4\xb5M',
    '\xb2\xf6\xab\xd5\xb4H']
ROLENAME2SHAPE = {
    '\xb3p\xbb\xbb\xabL': 111,
    '\xc5R\xc6E\xa4\xf5': 112,
    '\xad\xb7\xb9a\xa8\xe0': 212,
    '\xad\xe2\xaai\xbfP': 211,
    '\xb6\xb3\xb5L\xa4\xdf': 122,
    '\xa4\xd1\xc2\xcd\xa4l': 121,
    '\xb2H\xb2M\xac\xee': 222,
    '\xa5\xc9\xc3\xb9\xabb': 221,
    '\xc3t\xb4\xf0\xa4l': 131,
    '\xaa\xa2\xa6p\xad\xb7': 132,
    '\xa4d\xa4\xdb\xbd\xba': 231,
    '\xb5\xb5\xb9\xe4\xb5M': 232,
    '\xb2\xf6\xab\xd5\xb4H': 113 }
g_ReplaceDlg = None
g_bAskType = False

def ModuleReset():
    global g_ReplaceDlg, g_bAskType
    g_ReplaceDlg = None
    g_bAskType = False


def GetRoleShowMgr():
    return mdheroshapedesc.GetRoleShapeDescMgr('CAppearanceShapeMainView')


def GetMakeRoleShowMgr():
    return mdheroshapedesc.GetRoleShapeDescMgr('CMakeHsvPalDlg')


def IsCanHsvColor():
    global g_bAskType
    g_bAskType = False
    netappearance.C2GSAppearanceTGF()


def GetCanHsvColor():
    return g_bAskType


def SetCanHsvColor():
    global g_bAskType
    g_bAskType = True


class CHSlider(interface.CHSlider):
    
    class CBar(interface.CHSlider.CBar):
        
        def MouseWheelDown(self, p):
            self.GetParent().MouseWheelDown(p)

        
        def MouseWheelUp(self, p):
            self.GetParent().MouseWheelUp(p)

        
        def SetBarPos(self, iPos):
            self.SetBarPosNotCB(iPos)
            self.GetParent().PosChange(iPos)

        
        def SetBarPosNotCB(self, iPos):
            if iPos == self.m_CurPos:
                return None
            
            if iPos < 0:
                iPos = 0
            elif iPos > self.m_nMax:
                iPos = self.m_nMax
            
            x = iPos * self.m_MoveArea / self.m_nMax
            (_, objy) = self.GetPos()
            self.SetPos(x, objy)
            self.m_CurPos = iPos


    
    def __init__(self, parent, x, y, w, h, n_max = 100, fname = None, path = None):
        interface.CHSlider.__init__(self, parent, x, y, w, h, n_max, fname, path)

    
    def SetBarPosNotCB(self, pos):
        self.m_Bar.SetBarPosNotCB(pos)

    
    def MouseWheelDown(self, p):
        pos = self.GetBarPos()
        pos = pos - p
        if pos < 0:
            pos = 0
        
        self.SetBarPos(pos)

    
    def MouseWheelUp(self, p):
        pos = self.GetBarPos()
        pos = pos + p
        if pos > self.m_nMax:
            pos = self.m_nMax
        
        self.SetBarPos(pos)

    
    def SetEnable(self, enable):
        self.m_Bar.Enable(enable)
        self.Enable(enable)



class CHsvPalDlgMain(combdialog.CCombSubWnd, slot.ISignalSubject):
    
    def __init__(self, oParent):
        if permission.IsTestServerByNewYanzhiguan():
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/appearance_newstyle/appearance/freecolor_new.dlg')
        else:
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/appearance_new/appearance/freecolor_new.dlg')
        interface.Center(self)
        self.ssInit()
        IsCanHsvColor()
        self.m_oOpenDlg = None
        self.GetScreenPos()
        self.InitDlg()
        self.ChooseMainPage()
        self.SetIgnoreEsc(True)

    
    def OnCloseWindow(self):
        self.m_oOpenDlg = None
        newmdappearancefreecolor.GetHsvPalMgr().ClearData()

    
    def InitDlg(self):
        for oObj in self.m_Frames.itervalues():
            oObj.SetShow(False)
        
        oHeroHsvMgr = newmdappearancefreecolor.GetHeroHsvMgr()
        oHeroHsvMgr.ssConnect(oHeroHsvMgr.SS_UpdateInitData, self.OnUpdateInitData)
        import commoncb
        commoncb.RegistCB(commoncb.CONFIRM_CHANGE_RES_TYPE_CB, self, 'OnChangeResType')

    
    def ChooseMainPage(self):
        newmdappearancefreecolor.GetHsvPalMgr().ClearData()
        self.SetShowObject('btn_make', True)
        self.SetShowObject('btn_return', False)
        self.m_oOpenDlg = None
        self.m_oOpenDlg = CHsvPalDlg(self)
        dDesc = GetRoleShowMgr().GetDesc()
        oRoleObj = self.m_oOpenDlg.m_oRoleView.GetRoleObj()
        dDescInfo = misc.DeepCopy(dDesc)
        if 'fashion' in dDescInfo:
            del dDescInfo['fashion']
        
        oRoleObj.SetDesc(dDescInfo)
        oRoleObj.GetNewWalker().LoadData()

    
    def ChooseSavePage(self):
        if not GetCanHsvColor():
            IsCanHsvColor()
            return None
        
        newmdappearancefreecolor.GetHsvPalMgr().ClearData()
        self.SetShowObject('btn_make', False)
        self.SetShowObject('btn_return', True)
        self.m_oOpenDlg = None
        self.m_oOpenDlg = CMakeHsvPalDlg(self)

    
    def OnUpdateInitData(self):
        SetCanHsvColor()

    
    def OnChangeResType(self):
        if not GetCanHsvColor():
            IsCanHsvColor()
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 44:
            self.ChooseMainPage()
        else:
            self.ChooseSavePage()



class CHsvPalDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_ClickRandom = 'OnClickRandom()'
    SS_ClickResetSelfPal = 'OnClickResetSelfPal()'
    SS_ClickSelectOwnTab = 'OnClickSelectOwnTa(iType)'
    SS_ClickMakeHsvPal = 'OnClickMakeHsvPal()'
    SS_ClickSavePal = 'OnClickSavePal()'
    SS_ClickDelSavePal = 'OnClickDelSavePal()'
    SS_OnSliderChange = 'OnSliderChange(iType, iPos)'
    SS_ClickChangePart = 'OnClickChangePart(iPartList)'
    SS_ClickGiftBtn = 'OnClickGiftBtn()'
    SS_ClickOthersPayBtn = 'SS_ClickOthersPayBtn'
    
    def __init__(self, oParent):
        if permission.IsTestServerByNewYanzhiguan():
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/appearance_newstyle/appearance/freecolor_new.dlg')
        else:
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/appearance_new/appearance/freecolor_new.dlg')
        interface.Center(self)
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_oRoleView = roleshapdesc.CChangeDirRole(self.GetObject('loc_icon'), 'CAppearanceShapeMainView')
        self.m_oCtrlBtnDict = { }
        self.InitDlg()
        self.m_DDD = [
            dgtappearancehsv.CDelegateHsvPosChange(self, 'CAppearanceShapeMainView'),
            dgtappearancehsv.CDelegateHsvMain(self, 'CAppearanceShapeMainView'),
            dgtappearancehsv.CDelegateHsvPartTapChange(self),
            dgtappearancehsv.CDelegateHsvRandom(self),
            dgtappearancehsv.CDelegateHsvResetSelfPal(self),
            dgtappearancehsv.CDelegateHsvOwnTab(self),
            dgtappearancehsv.CDelegateHsvMakeHsvPal(self),
            dgtappearancehsv.CDelegateHsvSavePal(self),
            dgtappearancehsv.CDelegateHsvDelSavePal(self),
            dgtappearancehsv.CDelegateHuoLiChange(self, 1),
            dgtappearancehsv.CDelegateGiftBox(self)]

    
    def InitDlg(self):
        self.InitBtn()
        self.InitSlider()
        self.InitSatProgress()
        self.ChooseMainPage()
        self.OnUpdateUnFixHsv()

    
    def InitSatProgress(self):
        '''\xacV\xa6\xe2\xc5\xdc\xa6\xe2\xb1\xf8'''
        self.m_oSatProcessObj = CPalProcess(self)
        (x, y) = self.GetObject('loc_satprogress').GetPos()
        z = self.GetObject('loc_satprogress').GetZ()
        self.m_oSatProcessObj.SetPos(x, y)
        self.m_oSatProcessObj.SetZ(z)

    
    def InitBtn(self):
        for sLoc, iType in {
            'loc_ShowRide': appearancedefine.PART_SHOW_HORSE,
            'loc_ShowAura': appearancedefine.PART_SHOW_WING,
            'loc_ShowWing': appearancedefine.PART_SHOW_AURA }.iteritems():
            self.m_oCtrlBtnDict[sLoc] = selectrolecolor.CRolePartCtrl(self.GetObject(sLoc), [
                'CAppearanceShapeMainView'], iType)
        

    
    def InitSlider(self):
        '''\xaa\xec\xa9l\xa4\xc6\xa4T\xad\xd3\xa9\xec\xb0\xca\xb1\xf8'''
        self.m_oHueSlider = combmacro.CHSLIDER(CHSlider, 'loc_hue', self, 360, 'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xbc\xfd\xcd\xb7/0.png')
        sPath = style.GetStr('dialog/sysopt_new.dlg', 'data_music', iUseStyle = 3)
        self.m_oSatSlider = combmacro.CHSLIDER(CHSlider, 'loc_sat', self, 100, sPath)
        self.m_oValSlider = combmacro.CHSLIDER(CHSlider, 'loc_val', self, 100, sPath)

    
    def ChooseMainPage(self):
        self.GetObject('txt_name').SetText(charinterface.GetHeroShapeName(GetRoleShowMgr().GetShape()))
        for sName in [
            'btn_make',
            'btn_return',
            'frame_dft_000',
            'text_dft_003',
            'btn_owncancel',
            'txt_othersave',
            'btn_prepage',
            'btn_nextpage',
            'btn_othersave',
            'btn_othercancel',
            'img_othersave',
            'btn_other1',
            'btn_other2',
            'btn_return',
            'btn_generate']:
            self.SetShowObject(sName, False)
        

    
    def SetHuoPos(self, iHuoPos):
        self.m_oHueSlider.SetBarPosNotCB(iHuoPos)
        self.m_oSatProcessObj.SetHue(iHuoPos)

    
    def SetSatPos(self, iSatPos):
        self.m_oSatSlider.SetBarPosNotCB(iSatPos)
        self.GetObject('txt_sat').SetText('%d%%' % iSatPos)

    
    def SetValPos(self, iValPos):
        self.m_oValSlider.SetBarPosNotCB(iValPos)
        self.GetObject('txt_val').SetText('%d%%' % iValPos)

    
    def SetRegainShow(self, bShow):
        '''\xc1\xd9\xad\xec\xab\xf6\xb6s\xa5i\xa8\xa3\xa9\xca'''
        self.SetShowObject('btn_ownRegain', bShow)

    
    def SetOwnCancelShow(self, bShow):
        '''\xa7R\xb0\xa3\xa4\xe8\xae\xd7\xa5i\xa8\xa3\xa9\xca'''
        self.SetShowObject('btn_owncancel', bShow)

    
    def SetHuoLiText(self, sText):
        self.GetObject('txt_need').SetText(sText)

    
    def SetTipsShow(self, bShow):
        self.SetShowObject('img_Tips2', bShow)

    
    def SetFirsetText(self, sText):
        self.GetObject('txt_firset').SetText(sText)

    
    def SetPartBtnSelect(self, iPart, bSelect):
        '''\xbf\xef\xbe\xdc\xb3\xa1\xa5\xf3\xab\xf6\xb6s'''
        dData = {
            0: 'btn_head',
            1: 'txtbtn_dft_018',
            2: 'txtbtn_dft_008',
            3: 'txtbtn_dft_012' }
        self.GetObject(dData[iPart]).SetSelect(bSelect)

    
    def SetiPartBtnSelectTrue(self, iPart):
        dData = {
            0: 'btn_head',
            1: 'txtbtn_dft_018',
            2: 'txtbtn_dft_008',
            3: 'txtbtn_dft_012' }
        for _, sName in dData.iteritems():
            self.GetObject(sName).SetSelect(False)
        
        self.GetObject(dData[iPart]).SetSelect(True)

    
    def UpdateHsvPal(self):
        '''
\t\t\xb6i\xab\xd7\xb1\xf8\xb6i\xa6\xe6\xa4\xc1\xb4\xab\xae\xc9\xa5u\xbb\xdd\xadn\xa7\xef\xc5\xdc\xacV\xa6\xe2\xa7Y\xa5i,\xb5L\xbb\xdd\xad\xab\xb7s\xb3\xd0\xab\xd8\xa4H\xaa\xab
\t\t'''
        dDesc = GetRoleShowMgr().GetDesc()
        oRoleObj = self.m_oRoleView.GetRoleObj()
        oRoleObj.SetDesc(dDesc)
        if oRoleObj.m_MultiHorsePlayerList:
            oReal = oRoleObj.m_MultiHorsePlayerList[0]
            oMuDesc = oReal.GetOrigDesc()
            for sKey in ('horse', 'aura', 'track', 'fairy', 'fashion'):
                if sKey in oMuDesc:
                    del oMuDesc[sKey]
                    continue
            
            if chardefine.DESC.KEY_HERO_HSV in dDesc:
                oMuDesc[chardefine.DESC.KEY_HERO_HSV] = copy.deepcopy(dDesc[chardefine.DESC.KEY_HERO_HSV])
            
            oReal.SetDesc(oMuDesc)
        else:
            oRider = oRoleObj.GetRider()
            if oRider:
                oRider.SetHorseInfo(GetRoleShowMgr().GetShape(), dDesc, GetRoleShowMgr().GetState())
            
            oRoleObj.GetNewWalker().LoadRiderPal()

    
    def ShowReplaceDlg(self):
        global g_ReplaceDlg
        iShape = GetRoleShowMgr().GetShape()
        dDesc = GetRoleShowMgr().GetDesc()
        lCurPal = newmdappearancefreecolor.GetHsvPalMgr().GetHsvPal(iShape)
        lOtherPal = newmdappearancefreecolor.GetHeroHsvMgr().GetHeroSelfSaveHsv()
        g_ReplaceDlg = CRepalceDlg(True, iShape, dDesc, lCurPal, lOtherPal)

    
    def OnUpdateUnFixHsv(self):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if oHsvPalMgr.GetChoosePart():
            iPart = oHsvPalMgr.GetChoosePart()[0]
            (iHuoPos, iSatPos, iValPos) = oHsvPalMgr.GetUnFixHSVHsvPalList(iPart)
        else:
            (iHuoPos, iSatPos, iValPos) = (0, 0, 0)
        self.SetHuoPos(max(min(iHuoPos, 360), 0))
        self.SetSatPos(max(min(iSatPos, 100), 0))
        self.SetValPos(max(min(iValPos, 100), 0))
        self.UpdateHsvPal()

    
    def OnSliderChange(self, oCtrl, iPos):
        '''\xb1\xf8\xbf\xef\xbe\xdc\xa6^\xbd\xd5'''
        if oCtrl == self.m_oHueSlider:
            self.ssEmit(self.SS_OnSliderChange, 0, iPos)
        elif oCtrl == self.m_oSatSlider:
            self.ssEmit(self.SS_OnSliderChange, 1, iPos)
        elif oCtrl == self.m_oValSlider:
            self.ssEmit(self.SS_OnSliderChange, 2, iPos)
        

    
    def OnMessage(self, iMsgID):
        if not delegateappearanceoperate.IsAppearanceCanOperate('\xa7A\xb2{\xa6b\xa5\xbf\xc5\xdc\xb4\xab\xa4F\xa8\xad\xa7\xce\xa1A\xa6b\xac\xdd\xa4\xa3\xb3z\xa7A\xa5\xbb\xb4L\xaa\xba\xae\xc9\xad\xd4\xa7\xda\xa8S\xaak\xb4\xc0\xa7A\xacV\xa6\xe2'):
            if iMsgID not in (31, 21, 22, 23):
                return None
            
        
        if not GetCanHsvColor():
            IsCanHsvColor()
            if iMsgID not in (31, 21, 22, 23):
                return None
            
        
        if iMsgID == 1:
            self.ssEmit(self.SS_ClickGiftBtn)
        elif iMsgID == 42:
            self.ssEmit(self.SS_ClickResetSelfPal)
        elif iMsgID in (21, 22, 23):
            self.ssEmit(self.SS_ClickChangePart, [
                iMsgID - 21])
        elif iMsgID == 24:
            self.ssEmit(self.SS_ClickMakeHsvPal)
        elif iMsgID == 31:
            self.ssEmit(self.SS_ClickChangePart, range(3))
        elif iMsgID in (17, 18, 32, 33):
            self.ssEmit(self.SS_ClickSelectOwnTab, iMsgID)
        elif iMsgID == 27:
            self.ssEmit(self.SS_ClickSavePal)
        elif iMsgID == 40:
            self.ssEmit(self.SS_ClickDelSavePal)
        elif iMsgID == 43:
            self.ssEmit(self.SS_ClickRandom)
        elif iMsgID == 56:
            self.ssEmit(self.SS_ClickOthersPayBtn)
        



class CMakeHsvPalDlg(combdialog.CCombSubWnd, slot.ISignalSubject):
    SS_ClickRandom = 'OnClickRandom()'
    SS_ClickSelectOwnTab = 'OnClickSelectOwnTab(iType)'
    SS_ClickMakeHsvPal = 'OnClickMakeHsvPal()'
    SS_ClickSavePal = 'OnClickSavePal()'
    SS_ClickDelSavePal = 'OnClickDelSavePal()'
    SS_OnSliderChange = 'OnSliderChange(iType, iPos)'
    SS_ClickChangePart = 'OnClickChangePart(iPartList)'
    SS_ClickChooseMake = 'ClickChooseMake(iAdd)'
    SS_ClickShapeChange = 'OnClickShapeChange(iShape)'
    
    def __init__(self, oParent):
        if permission.IsTestServerByNewYanzhiguan():
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/appearance_newstyle/appearance/freecolor_new.dlg')
        else:
            combdialog.CCombDialog.__init__(self, oParent, 'dialog4/appearance_new/appearance/freecolor_new.dlg')
        interface.Center(self)
        self.ssInit()
        self.SetIgnoreEsc(True)
        self.m_oRoleView = roleshapdesc.CChangeDirRole(self.GetObject('loc_icon'), 'CMakeHsvPalDlg')
        self.InitDlg()
        self.m_DDD = [
            dgtappearancehsv.CDelegateHsvPosChange(self, 'CMakeHsvPalDlg'),
            dgtappearancehsv.CDelegateHsvMain(self, 'CMakeHsvPalDlg'),
            dgtappearancehsv.CDelegateHsvPartTapChange(self),
            dgtappearancehsv.CDelegateHsvRandom(self),
            dgtappearancehsv.CDelegateHsvMakeChooseTicket(self),
            dgtappearancehsv.CDelegateHuoLiChange(self, 2),
            dgtappearancehsv.CDelegateHsvMakeOwnTab(self),
            dgtappearancehsv.CDelegateHsvMakeSavePal(self),
            dgtappearancehsv.CDelegateHsvMakeTicket(self),
            dgtappearancehsv.CDelegateHsvMakeChooseShape(self),
            dgtappearancehsv.CDelegateHsvDelMakeSavePal(self)]

    
    def InitDlg(self):
        self.InitSatProgress()
        self.CreateSaveDownList()
        self.InitSlider()
        self.ChooseSavePage()
        self.GetObject('btn_make').SetSelect(True)

    
    def SetHuoPos(self, iHuoPos):
        self.m_oHueSlider.SetBarPosNotCB(iHuoPos)
        self.m_oSatProcessObj.SetHue(iHuoPos)

    
    def SetSatPos(self, iSatPos):
        self.m_oSatSlider.SetBarPosNotCB(iSatPos)
        self.GetObject('txt_sat').SetText('%d%%' % iSatPos)

    
    def SetValPos(self, iValPos):
        self.m_oValSlider.SetBarPosNotCB(iValPos)
        self.GetObject('txt_val').SetText('%d%%' % iValPos)

    
    def SetTipsShow(self, bShow):
        self.SetShowObject('img_Tips2', bShow)

    
    def SetFirsetText(self, sText):
        self.GetObject('txt_firset').SetText(sText)

    
    def SetHuoLiText(self, sText):
        self.GetObject('txt_need').SetText(sText)

    
    def SetOtherSaveText(self, iKey, iShape):
        self.GetObject('txt_othersave').SetText('\xa4\xe8\xae\xd7%s\xa1P%s' % (misc.NumToChinese(iKey), charinterface.GetHeroShapeName(iShape)))

    
    def SetSelectShapeText(self, sText):
        self.m_ListBox.SetText(sText)

    
    def InitSatProgress(self):
        '''\xacV\xa6\xe2\xc5\xdc\xa6\xe2\xb1\xf8'''
        self.m_oSatProcessObj = CPalProcess(self)
        (x, y) = self.GetObject('loc_satprogress').GetPos()
        z = self.GetObject('loc_satprogress').GetZ()
        self.m_oSatProcessObj.SetPos(x, y)
        self.m_oSatProcessObj.SetZ(z)

    
    def InitSlider(self):
        '''\xaa\xec\xa9l\xa4\xc6\xa4T\xad\xd3\xa9\xec\xb0\xca\xb1\xf8'''
        self.m_oHueSlider = combmacro.CHSLIDER(CHSlider, 'loc_hue', self, 360, 'combdialog4/\xc8\xfd\xcc\xac\xb0\xb4\xc5\xa5/\xbc\xfd\xcd\xb7/0.png')
        sPath = style.GetStr('dialog/sysopt_new.dlg', 'data_music', iUseStyle = 3)
        self.m_oSatSlider = combmacro.CHSLIDER(CHSlider, 'loc_sat', self, 100, sPath)
        self.m_oValSlider = combmacro.CHSLIDER(CHSlider, 'loc_val', self, 100, sPath)

    
    def CreateSaveDownList(self):
        '''\xb3\xd0\xab\xd8\xa4U\xa9\xd4\xb5\xe6\xb3\xe6'''
        self.m_ListBox = combmacro.CLISTBOX(interface.CListBox, 'loc_shape', self, interface.COLOR_5, interface.FontLT14_3)
        iLen = len(ROLELIST)
        self.m_ListBox.SetListBoxChangeCB(self.OnShapeChange)
        self.m_ListBox.SetItemProp(4, 16, iLen * 16)
        self.m_ListBox.SetReadOnly(True)
        for sName in ROLELIST:
            self.m_ListBox.AddTextItem(sName)
        

    
    def ChooseSavePage(self):
        self.m_ListBox.OnSelect(1)
        for sName in [
            'text_dft_024',
            'txt_firset',
            'btn_owncancel',
            'btn_ownRegain',
            'text_dft_000',
            'txt_name',
            'btn_owncancel',
            'btn_make',
            'btn_return',
            'btn_own1',
            'btn_own2',
            'btn_own3',
            'btn_own4',
            'btn_ownsave',
            'btn_comfirm']:
            self.SetShowObject(sName, False)
        

    
    def SetPartBtnSelect(self, iPart, bSelect):
        '''\xbf\xef\xbe\xdc\xb3\xa1\xa5\xf3\xab\xf6\xb6s'''
        dData = {
            0: 'btn_head',
            1: 'txtbtn_dft_018',
            2: 'txtbtn_dft_008',
            3: 'txtbtn_dft_012' }
        self.GetObject(dData[iPart]).SetSelect(bSelect)

    
    def ShowReplaceDlg(self):
        global g_ReplaceDlg
        iShape = GetMakeRoleShowMgr().GetShape()
        dDesc = GetMakeRoleShowMgr().GetDesc()
        lCurPal = newmdappearancefreecolor.GetHsvPalMgr().GetHsvPal(iShape)
        lOtherPal = newmdappearancefreecolor.GetHeroHsvMgr().GetMakeTicketSaveHsv()
        g_ReplaceDlg = CRepalceDlg(False, iShape, dDesc, lCurPal, lOtherPal)

    
    def UpdateHsvPal(self):
        '''
\t\t\xb6i\xab\xd7\xb1\xf8\xb6i\xa6\xe6\xa4\xc1\xb4\xab\xae\xc9\xa5u\xbb\xdd\xadn\xa7\xef\xc5\xdc\xacV\xa6\xe2\xa7Y\xa5i,\xb5L\xbb\xdd\xad\xab\xb7s\xb3\xd0\xab\xd8\xa4H\xaa\xab
\t\t'''
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        dDesc = GetMakeRoleShowMgr().GetDesc()
        dDesc['hsvpal'] = oHsvPalMgr.GetHsvPal(GetMakeRoleShowMgr().GetShape())
        oRoleObj = self.m_oRoleView.GetRoleObj()
        oRoleObj.SetDesc(dDesc)
        if oRoleObj.m_MultiHorsePlayerList:
            oReal = oRoleObj.m_MultiHorsePlayerList[0]
            oMuDesc = oReal.GetOrigDesc()
            for sKey in ('horse', 'aura', 'track', 'fairy'):
                if sKey in oMuDesc:
                    del oMuDesc[sKey]
                    continue
            
            oMuDesc['hsvpal'] = oHsvPalMgr.GetHsvPal(GetMakeRoleShowMgr().GetShape())
            oReal.SetDesc(oMuDesc)
        else:
            oRoleObj.GetNewWalker().LoadRiderPal()

    
    def OnUpdateUnFixHsv(self):
        oHsvPalMgr = newmdappearancefreecolor.GetHsvPalMgr()
        if oHsvPalMgr.GetChoosePart():
            iPart = oHsvPalMgr.GetChoosePart()[0]
            (iHuoPos, iSatPos, iValPos) = oHsvPalMgr.GetUnFixHSVHsvPalList(iPart)
        else:
            (iHuoPos, iSatPos, iValPos) = (0, 0, 0)
        self.SetHuoPos(max(min(iHuoPos, 360), 0))
        self.SetSatPos(max(min(iSatPos, 100), 0))
        self.SetValPos(max(min(iValPos, 100), 0))
        self.UpdateHsvPal()

    
    def OnSliderChange(self, oCtrl, iPos):
        '''\xb1\xf8\xbf\xef\xbe\xdc\xa6^\xbd\xd5'''
        if oCtrl == self.m_oHueSlider:
            self.ssEmit(self.SS_OnSliderChange, 0, iPos)
        elif oCtrl == self.m_oSatSlider:
            self.ssEmit(self.SS_OnSliderChange, 1, iPos)
        elif oCtrl == self.m_oValSlider:
            self.ssEmit(self.SS_OnSliderChange, 2, iPos)
        

    
    def OnShapeChange(self):
        idx = self.m_ListBox.GetSelected() - 1
        if idx < 0:
            return None
        else:
            sKey = self.m_ListBox.m_TextList[idx]
            self.ssEmit(self.SS_ClickShapeChange, ROLENAME2SHAPE[sKey])
            return None

    
    def OnMessage(self, iMsgID):
        if not delegateappearanceoperate.IsAppearanceCanOperate('\xa7A\xb2{\xa6b\xa5\xbf\xc5\xdc\xb4\xab\xa4F\xa8\xad\xa7\xce\xa1A\xa6b\xac\xdd\xa4\xa3\xb3z\xa7A\xa5\xbb\xb4L\xaa\xba\xae\xc9\xad\xd4\xa7\xda\xa8S\xaak\xb4\xc0\xa7A\xacV\xa6\xe2'):
            if iMsgID not in (31, 21, 22, 23):
                return None
            
        
        if not GetCanHsvColor():
            IsCanHsvColor()
            if iMsgID not in (31, 21, 22, 23):
                return None
            
        
        if iMsgID in (21, 22, 23):
            self.ssEmit(self.SS_ClickChangePart, [
                iMsgID - 21])
        elif iMsgID == 31:
            self.ssEmit(self.SS_ClickChangePart, range(3))
        elif iMsgID == 43:
            self.ssEmit(self.SS_ClickRandom)
        elif iMsgID in (38, 39):
            self.ssEmit(self.SS_ClickSelectOwnTab, iMsgID)
        elif iMsgID == 29:
            self.ssEmit(self.SS_ClickChooseMake, 1)
        elif iMsgID == 30:
            self.ssEmit(self.SS_ClickChooseMake, -1)
        elif iMsgID == 37:
            self.ssEmit(self.SS_ClickDelSavePal)
        elif iMsgID == 26:
            self.ssEmit(self.SS_ClickMakeHsvPal)
        elif iMsgID == 36:
            self.ssEmit(self.SS_ClickSavePal)
        



class CRepalceDlg(combdialog.CCombDialog):
    
    def __init__(self, bOwn, iShape, dDesc, iCurPal, lOtherPal):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog4/freecolor/replace.dlg')
        interface.Center(self)
        lOtherPal = self.ChangeOhterPal(lOtherPal)
        self.m_iCurIndex = 0
        self.m_bOwn = bOwn
        self.m_iManLen = len(lOtherPal)
        self.m_lOtherPal = lOtherPal
        self.m_iShape = iShape
        self.m_iCurPal = iCurPal
        self.InitRole(iShape, dDesc, iCurPal)
        self.SetIgnoreEsc(True)

    
    def ChangeOhterPal(self, lOtherPal):
        lOtherPal = copy.deepcopy(lOtherPal)
        if 0 in lOtherPal:
            del lOtherPal[0]
        
        return lOtherPal

    
    def InitRole(self, iShape, dDesc, iCurPal):
        self.m_dLeftDesc = copy.deepcopy(dDesc)
        self.m_dLeftDesc['hsvpal'] = iCurPal
        self.m_oLeftRole = walker.CFakeRole(self.GetObject('loc_icon'), 0, iShape, self.m_dLeftDesc)
        self.m_dRightDesc = copy.deepcopy(dDesc)
        self.ChangePos(0)

    
    def ChangePos(self, iAdd):
        iList = self.m_lOtherPal.keys()
        iList.sort()
        if self.m_iCurIndex in iList:
            iPos = iList.index(self.m_iCurIndex)
            iPos += iAdd
            if iPos <= iPos:
                pass
            elif iPos < self.m_iManLen:
                self.m_iCurIndex = iList[iPos]
            
        elif iList:
            self.m_iCurIndex = iList[0]
        else:
            return None
        self.GetObject('text_dft_003').SetText('\xa6\xac\xc2\xc3\xa4\xe8\xae\xd7%s' % misc.NumToChinese(self.m_iCurIndex))
        iShape = self.m_lOtherPal[self.m_iCurIndex][0]
        lList = self.m_lOtherPal[self.m_iCurIndex][1:]
        self.m_dRightDesc['hsvpal'] = [
            lList[:3],
            lList[3:6],
            lList[6:]]
        self.m_oRightRole = walker.CFakeRole(self.GetObject('loc_ico1'), 0, iShape, self.m_dRightDesc)

    
    def OnChangeLeft(self):
        self.ChangePos(-1)

    
    def OnChangeRight(self):
        self.ChangePos(1)

    
    def CloseWindow(self):
        global g_ReplaceDlg
        g_ReplaceDlg = None

    
    def RepalcePal(self):
        iTmpList = []
        for lInfo in self.m_iCurPal:
            iTmpList.append(lInfo[0])
            iTmpList.append(lInfo[1])
            iTmpList.append(lInfo[2])
        
        if self.m_bOwn:
            netappearance.C2GSAppearanceSaveFreeDye(1, self.m_iCurIndex, self.m_iShape, iTmpList)
        else:
            netappearance.C2GSAppearanceSaveFreeDye(2, self.m_iCurIndex, self.m_iShape, iTmpList)
        self.CloseWindow()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 29:
            self.OnChangeRight()
        elif iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 30:
            self.OnChangeLeft()
        elif iMsgID == 31:
            self.RepalcePal()
        



class CPalProcess(walker.CFakeRole):
    
    def __init__(self, oParent):
        walker.CFakeRole.__init__(self, oParent, 0, 8092, 0)
        self.m_iHue = 0

    
    def SetHue(self, iHue):
        if iHue == self.m_iHue:
            return None
        
        self.m_iHue = iHue
        self.SetHsvPalInc((0, 0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 360, 360, iHue, 0, 0))
