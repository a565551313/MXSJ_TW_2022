# pycdc 交叉复核产物 · script.fls entry 4955
# co_filename(原始)='script/mxgame/team/teamrecruit/dlgrecruitpublish.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:03Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4955.pyc (Python 2.5)

'''
\xb5o\xa7G\xa9\xdb\xb6\xd2
$trybuildorg pid 5 \xd5\xd0\xc4\xbc 5 5 5 5

1.\xb5\xe3\xbb\xf7\xa3\xba\xc6\xe4\xcb\xfc\xb6\xd3\xd4\xb1\xb5\xc4\xbc\xd3\xba\xc5\xa3\xba\xcc\xed\xbc\xd3\xba\xc3\xd3\xd1\xc1\xd0\xb1\xed

1.C2S: \xbf\xcd\xbb\xa7\xb6\xcb\xbb\xf1\xc8\xa1\xd3\xc5\xbb\xdd\xc9\xcc\xb3\xc7\xca\xfd\xbe\xdd\xb7\xa2\xc8\xe7\xcf\xc2\xd0\xad\xd2\xe9
\t\xa8\xf3\xc4\xb3\xa1G0x46
\tiSub: 53
\tiType: 1b\t# 1:\xd5\xe4\xc6\xb7 0:\xc7\xc9\xbd\xb3 2:\xd0\xc2\xc8\xcb\xcc\xd8\xbb\xdd 3:\xd3\xc5\xbb\xdd\xc9\xcc\xb3\xc7

2.S2C\xa3\xba\xb7\xfe\xce\xf1\xc6\xf7\xca\xd5\xb5\xbd\xc9\xcf\xca\xf6\xd0\xad\xd2\xe9\xb7\xb5\xbb\xd8\xd3\xc5\xbb\xdd\xbc\xd2\xbe\xdf\xc9\xcc\xb5\xea\xca\xfd\xbe\xdd
nettrade \xb5\xc4 CPageShop\xd4\xf6\xbc\xd3 furnitureyhstore \xc0\xe0\xcb\xc6 \xa1\xb0furniturezhpstore\xa1\xb1\xa3\xbb \xd7\xd6\xb6\xce\xc8\xe7\xcf\xc2
1 \tiPage #\xd4\xdd\xca\xb1\xb2\xbb\xd3\xc3
1\tiLen
\t4 iShape
\t2 iNum
\t4 iPrice
'''
import combdialog
import hero
import interface
import misc
import delegatedlgrecruitpublish
import mdteamrecruit
import commondialog
import permission
import slot
import ui
import teamrecruitinterface
import mddailyteam
POS_2_PLAYERLOC = {
    1: 'herobox0',
    2: 'herobox1',
    3: 'herobox2',
    4: 'herobox3',
    5: 'herobox4',
    6: 'herobox5',
    7: 'herobox6',
    8: 'herobox7' }
MSGID_2_TIME = {
    4: 1,
    5: 2 }
TIME_TYPE_2_UINAME = {
    1: 'btn_day',
    2: 'btn_night' }
MSCID_2_CLASS = {
    6: 0,
    7: 1,
    8: 2,
    9: 3 }
CLASS_TYPE_2UINAME = {
    0: 'btn_zhanshi',
    1: 'btn_fashi',
    2: 'btn_fojia',
    3: 'btn_fengxi' }
MSGID_2_TARGET = {
    10: 0,
    11: 1,
    12: 2,
    13: 3 }
TARGET_TYPE_2UINAME = {
    0: 'btn_chumo',
    1: 'btn_richang',
    2: 'btn_tiaozhan',
    3: 'btn_bangzhan' }

class CMultiEdit(interface.CMultilineEdit):
    m_oDefaultTips = None
    m_bDefaultTipsWeak = False
    
    def SetDefaultTipObj(self, oTips, bWeak = True):
        self.m_bDefaultTipsWeak = bWeak
        if bWeak:
            self.m_oDefaultTips = misc.WeakRef(oTips)
        else:
            self.m_oDefaultTips = oTips

    
    def Active(self, bActive):
        interface.CMultilineEdit.Active(self, bActive)
        bShow = True
        if bActive:
            bShow = False
        else:
            sTxt = self.GetText()
            if not sTxt:
                bShow = False
            
        if not self.m_oDefaultTips:
            return None
        
        if not self.m_bDefaultTipsWeak:
            self.m_oDefaultTips.SetShow(bShow)
        else:
            self.m_oDefaultTips().SetShow(bShow)



class CDlgRecuitPublish(combdialog.CCombDialog, slot.ISignalSubject):
    S_UIPATH_OLD = 'dialog/teamrecruit/recruitmember_new.dlg'
    S_UIPATH = 'dialog/teamrecruit/recruitmember_new2.dlg'
    S_UIPATH_TEMPTEAM = 'dialog/teamrecruit/recruitmember_trainee.dlg'
    SS_CLOSEDLG = 'SS_CloseDlg'
    SS_OPENDLG = 'SS_OpenDlg'
    SS_ADDFRIEND = 'SS_ADDFriend'
    SS_SELECT_TIME = 'SS_SelectActiveTime(iDay)'
    SS_SELECT_CLS = 'SS_SelectCls(iCls)'
    SS_SELECT_TARGET = 'SS_SelectTarget(iTarget)'
    SS_GRADEEDIT_CHANGED = 'SS_GRADEEDIT_CHANGED'
    SS_PUBLISHRECUIT = 'SS_PUBLISHRECUIT'
    SS_OPENFRIENDDETAIL = 'SS_OpenFriendDetail'
    SS_DELFRIEND = 'SS_DelFriend'
    
    def __init__(self, oParent):
        if mddailyteam.IsTempWarTeam():
            combdialog.CCombDialog.__init__(self, oParent, self.S_UIPATH_TEMPTEAM)
        else:
            combdialog.CCombDialog.__init__(self, oParent, self.S_UIPATH)
        self.ssInit()
        self.Topmost()
        interface.Center(self)
        self.m_oCloseCallBack = None
        self.m_oInterEdit = None
        self.m_oMinEdit = None
        self.m_oMaxEdit = None
        self.m_dPlayerUI = { }
        self.m_lFriend = []
        self.m_sOriTxt = ''
        self.m_dPos2Click = { }
        self.InitDlg()
        self.m_oDelegate = delegatedlgrecruitpublish.CDelegateRecruitPublishDlg(self)

    
    def SetCloseCallBack(self, oCloseCallBack):
        self.m_oCloseCallBack = misc.Functor(oCloseCallBack)

    
    def InitDlg(self):
        self.CreateEdit()
        self.InitAvatarClickBox()
        self.GetObject('btn_addmember').SetZ(1000)

    
    def InitAvatarClickBox(self):
        for iPos, sUIName in POS_2_PLAYERLOC.iteritems():
            if not self.GetObject(sUIName):
                continue
            
            (iX, iY, iW, iH) = self.GetLocData(sUIName)
            oBox = interface.CClickBox(self, iW, iH, 255, 0)
            self.m_dPos2Click[iPos] = oBox
            oBox.SetLeftUpCB(misc.Functor(self.OnLeftClickPhotoBox, iPos))
            oBox.SetRightUpCB(misc.Functor(self.OnRightClickPhotoBox, iPos))
            oBox.SetPos(iX, iY)
            oBox.SetShow(False)
            teamrecruitinterface.RegisterHotBoxEnterLeaveEvent(self, oBox)
        

    
    def CreateEdit(self):
        '''txt_na12'''
        global dlgteamrecruit
        import dlgteamrecruit
        (iX, iY, iW, iH) = self.GetLocData('loc_intro')
        iInterColor = dlgteamrecruit.GetColor(7)
        iFont = dlgteamrecruit.GetFont('FontLT14_3')
        self.m_oInterEdit = CMultiEdit(self, iInterColor, iFont, iX, iY, iW, iH, 14)
        self.m_oInterEdit.SetLimit(50)
        self.m_oInterEdit.SetDefaultTipObj(self.GetObject('txt_na12'))
        self.m_sOriTxt = self.GetObject('txt_na12').GetText()
        iColorGrade = dlgteamrecruit.GetColor(44)
        iFontGrade = dlgteamrecruit.GetFont('Fontlt14_3')
        dlgteamrecruit = None
        (iX, iY, iW, iH) = None.GetLocData('txt_level1')
        self.m_oMinEdit = ui.CNumberEdit(self, iColorGrade, iFontGrade, iX, iY + 2, iW, iH)
        self.m_oMinEdit.SetCharChangeCB(misc.Functor(self.OnNumberEditChanged, 'iMinGrade'))
        (iX, iY, iW, iH) = self.GetLocData('txt_level2')
        self.m_oMaxEdit = ui.CNumberEdit(self, iColorGrade, iFontGrade, iX, iY + 2, iW, iH)
        self.m_oMaxEdit.SetCharChangeCB(misc.Functor(self.OnNumberEditChanged, 'iMaxGrade'))
        self.m_oMaxEdit.Enable(False)
        self.m_oMinEdit.Enable(False)
        self.GetObject('txt_level1').SetShow(False)
        self.GetObject('txt_level2').SetShow(False)

    
    def RefreshCostTipsShow(self, bShow):
        self.GetObject('text_dft_000').SetShow(bShow)

    
    def RefreshPubBtn(self, bMyTeam):
        sTxt = None if not bMyTeam else '\xad\xd7\xa7\xef\xa9\xdb\xb6\xd2'
        self.GetObject('btn_pe1').SetText(sTxt)

    
    def GetInterDesc(self):
        return self.m_oInterEdit.GetText()

    
    def SetShow(self, bShow):
        combdialog.CCombDialog.SetShow(self, bShow)
        self.Topmost()

    
    def OnOpenDlg(self):
        self.ssEmit(self.SS_OPENDLG)

    
    def OnNumberEditChanged(self, sType):
        if sType == 'iMinGrade':
            oEdit = self.m_oMinEdit
        else:
            oEdit = self.m_oMaxEdit
        if not oEdit.GetText():
            return None
        
        iNum = int(oEdit.GetText())
        self.ssEmit(self.SS_GRADEEDIT_CHANGED, sType, iNum)

    
    def OnLeftClickPhotoBox(self, iPos):
        if len(self.m_lFriend) < iPos:
            return None
        
        iPlayerID = self.m_lFriend[iPos - 1]
        self.ssEmit(self.SS_DELFRIEND, iPlayerID)

    
    def OnRightClickPhotoBox(self, iPos):
        if len(self.m_lFriend) < iPos:
            return None
        
        iPlayerID = self.m_lFriend[iPos - 1]
        self.ssEmit(self.SS_OPENFRIENDDETAIL, iPlayerID)

    
    def SetGradeEditTxt(self, sType, iNum):
        if sType == 'iMinGrade':
            oEdit = self.m_oMinEdit
        else:
            oEdit = self.m_oMaxEdit
        if oEdit.GetText() == str(iNum):
            return None
        
        oEdit.SetText(str(iNum))

    
    def SetIntroTxt(self, sTxt):
        self.m_oInterEdit.SetText('')
        if not sTxt:
            sTxt = self.m_sOriTxt
        
        self.GetObject('txt_na12').SetText(sTxt)
        self.GetObject('txt_na12').SetShow(True)

    
    def OnCloseDlg(self, *args):
        if self.m_oCloseCallBack:
            self.m_oCloseCallBack()
        

    
    def RefreshFriend(self, lFriendInfo):
        lFriend = [ oFriend['iPlayerID'] for oFriend in lFriendInfo ]
        self.m_lFriend = list(lFriend)
        dOldPlayer = self.m_dPlayerUI
        self.m_dPlayerUI = { }
        for oFriend in lFriendInfo:
            iPlayerID = oFriend['iPlayerID']
            if iPlayerID in dOldPlayer:
                self.m_dPlayerUI[iPlayerID] = dOldPlayer[iPlayerID]
                continue
            None if self.m_lFriend and self.m_lFriend == lFriend else []
            self.m_dPlayerUI[iPlayerID] = self.CreatePlayerView(oFriend)
        
        for iPosID, sUIName in POS_2_PLAYERLOC.iteritems():
            if not self.GetObject(sUIName):
                continue
            
            if len(lFriend) >= iPosID:
                iPlayerID = lFriend[iPosID - 1]
                oPlayerItem = self.m_dPlayerUI[iPlayerID]
                sUIName = POS_2_PLAYERLOC[iPosID]
                oPlace = self.GetObject(sUIName)
                interface.AlignObjects(oPlayerItem, oPlace, interface.ALIGN_CENTER_MIDDLE)
                self.m_dPos2Click[iPosID].SetShow(True)
                continue
            self.m_dPos2Click[iPosID].SetShow(False)
        
        oAddBtn = self.GetObject('btn_addmember')
        oAddBtn.SetShow(False)
        iMinGrade = iMaxGrade = hero.GetProp('m_Grade')
        for dFriend in lFriendInfo:
            iCurGrade = dFriend['iGrade']
            if iCurGrade > iMaxGrade:
                iMaxGrade = iCurGrade
            
            if iCurGrade < iMinGrade:
                iMinGrade = iCurGrade
                continue
        
        iFinalMinGrade = min(iMinGrade, iMaxGrade - 20)
        iFinalMaxGrade = max(iMaxGrade, iMinGrade + 20)
        self.m_oMinEdit.SetText(str(iFinalMinGrade))
        self.m_oMaxEdit.SetText(str(iFinalMaxGrade))

    
    def CreatePlayerView(self, dFriend):
        tPhtoAttr = dFriend['tPhoto']
        iClass = dFriend['iCls']
        iGrade = dFriend['iGrade']
        iPlayerID = dFriend['iPlayerID']
        oAvater = teamrecruitinterface.CreatePlayerView(self, iPlayerID, tPhtoAttr, iGrade, iClass)
        oAvater.SetZ(100)
        return oAvater

    
    def OnRefreshTime(self, lTime):
        for iType, sUIName in TIME_TYPE_2_UINAME.iteritems():
            oUIObj = self.GetObject(sUIName)
            if not oUIObj:
                continue
            
            bSel = iType in lTime
            oUIObj.SetSelect(bSel)
        

    
    def OnRefreshCls(self, lCls):
        for iTCls, sUIName in CLASS_TYPE_2UINAME.iteritems():
            oUIObj = self.GetObject(sUIName)
            if not oUIObj:
                continue
            
            bSel = iTCls in lCls
            oUIObj.SetSelect(bSel)
        

    
    def OnRefreshTarget(self, lTarget):
        for iTarget, sUIName in TARGET_TYPE_2UINAME.iteritems():
            oUIObj = self.GetObject(sUIName)
            if not oUIObj:
                continue
            
            bSel = iTarget in lTarget
            oUIObj.SetSelect(bSel)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_CLOSEDLG)
        elif iMsgID == 2:
            self.ssEmit(self.SS_PUBLISHRECUIT)
        elif iMsgID == 3:
            self.ssEmit(self.SS_ADDFRIEND)
        elif iMsgID in MSGID_2_TIME:
            iValue = MSGID_2_TIME.get(iMsgID)
            self.ssEmit(self.SS_SELECT_TIME, iValue)
        elif iMsgID in MSCID_2_CLASS:
            iCls = MSCID_2_CLASS.get(iMsgID)
            self.ssEmit(self.SS_SELECT_CLS, iCls)
        elif iMsgID in MSGID_2_TARGET:
            iTarget = MSGID_2_TARGET.get(iMsgID)
            self.ssEmit(self.SS_SELECT_TARGET, iTarget)
