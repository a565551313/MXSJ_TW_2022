# pycdc 交叉复核产物 · script.fls entry 3806
# co_filename(原始)='script/dialog/dlginfo.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3806.pyc (Python 2.5)

import appearancedefine
import avatar
import charpath
import combdialog
import combmacro
import descinterface
import gamemoduledefines
import hero
import interface
import mdappearancechangecolor
import mdavatar
import mdopendlgmgr
import netplayerphoto
import netteam
import newappearancecontext
import newappearancedefine
import newmdappearancefreecolor
import oldwalkerprocess
import permission
import stopgamemoduleinterface
import style
import teammgr
import teamui
import ui
import usermacro
import world
import wrapinterface
import misc
import timer
import clickcounter
import friend
import dialoguecommondata
import ridedata
import ridedefine
import dlgnpc
g_InfoDlg = { }
g_ReNamedlg = None
g_DeleteDlg = None
g_bSwitchBtnTips = True
TIME_REFRESH = 15
DLG_TYPE_FRIEND = 1
DLG_TYPE_BAN = 2
DLG_TYPE_TEMP_FRIEND = 3
DLG_TYPE_STRANGER = 0
POPMENU_TYPE_STRANGER = 0
POPMENU_TYPE_FRIEND = 1
POPMENU_TYPE_TEMPFRIEND = 2
POPMENU_TYPE_BAN = 3
PLAYERSHOW_PICDEFULT_NAME = 'mxdefault.jpg'
ICONID_TO_BTNNAME = {
    1: 'btn_haoyouxiu',
    2: 'btn_jiayuan',
    3: 'btn_shizhuang',
    4: 'btn_ride',
    5: 'btn_zhandui',
    6: 'btn_shitu',
    7: 'btn_yuyin',
    8: 'btn_zhenrenxiu' }
PLAYERSHOW_ICONID = 8
FASHION_ICONID = 3
HORSE_ICONID = 4
VOICE_CARD = 7
MYQ_ICONID = 1
ICON_SORT_DICT = {
    'btn_haoyouxiu': 1,
    'btn_jiayuan': 2,
    'btn_shizhuang': 3,
    'btn_ride': 4,
    'btn_zhandui': 5,
    'btn_shitu': 6,
    'btn_yuyin': 7,
    'btn_zhenrenxiu': 8 }
ICON_TIPS = {
    'btn_haoyouxiu': ('\xa6n\xa4\xcd\xa8q', '\xb5o\xb0e\xa5\xf4\xb7N\xa6n\xa4\xcd\xa8q\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0'),
    'btn_jiayuan': ('\xaa\xb1\xaea\xa4\xa7\xaea', '\xbe\xd6\xa6\xb3\xaea\xb6\xe9\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0'),
    'btn_zhandui': ('\xbe\xd4\xb6\xa4', '\xb2\xd5\xab\xd8\xbe\xd4\xb6\xa4\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0'),
    'btn_shitu': ('\xaev\xae{', '\xb1a\xbb\xe2\xae{\xa7\xcc\xa5X\xaev\xab\xe1\xc2I\xabG'),
    'btn_zhenrenxiu': ('\xafu\xa4H\xa8q', '\xa6b\xafu\xa4H\xa8q\xa4W\xb6\xc7\xa6\xdb\xa4v\xb7\xd3\xa4\xf9\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0'),
    'btn_shizhuang': ('\xae\xc9\xb8\xcb', '\xac\xef\xc0\xb9\xae\xc9\xb8\xcb\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0'),
    'btn_yuyin': ('\xc1n\xad\xb5\xa6W\xa4\xf9', '\xbf\xfd\xbbs\xc1n\xad\xb5\xa6W\xa4\xf9\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0'),
    'btn_ride': ('\xa7\xa4\xc3M', '\xc3M\xad\xbc\xa5\xf4\xb7N\xa7\xa4\xc3M\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0') }
MSGID_TO_LOGSTR = {
    100: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xa6n\xa4\xcd\xa8q', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xa6n\xa4\xcd\xa8q-\xa5\xbc\xc2I\xabG'),
    101: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xaea\xb6\xe9', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xaea\xb6\xe9-\xa5\xbc\xc2I\xabG'),
    102: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xbe\xd4\xb6\xa4', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xbe\xd4\xb6\xa4-\xa5\xbc\xc2I\xabG'),
    103: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xaev\xae{', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xaev\xae{-\xa5\xbc\xc2I\xabG'),
    104: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xafu\xa4H\xa8q', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xafu\xa4H\xa8q-\xa5\xbc\xc2I\xabG'),
    105: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xae\xc9\xb8\xcb', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xae\xc9\xb8\xcb-\xa5\xbc\xc2I\xabG'),
    106: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xbby\xad\xb5', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xbby\xad\xb5-\xa5\xbc\xc2I\xabG'),
    107: ('\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xa7\xa4\xc3M', '\xc0\xc9\xae\xd7\xb9\xcf\xbc\xd0-\xa7\xa4\xc3M-\xa5\xbc\xc2I\xabG') }

def ModuleReset():
    global g_InfoDlg, g_ReNamedlg, g_DeleteDlg, g_bSwitchBtnTips
    g_InfoDlg = { }
    g_ReNamedlg = None
    g_DeleteDlg = None
    g_bSwitchBtnTips = True


def DelInfoDlg(iPlayerID):
    if g_InfoDlg.get(iPlayerID, None):
        del g_InfoDlg[iPlayerID]
    


def GetInfoDlg(iPlayerID):
    ''':rtype: CInfoDialog or None'''
    return g_InfoDlg.get(iPlayerID, None)


def SetInfoDlg(iPlayerID, oInfoDlg):
    '''
\t:param int iPlayerID: ID
\t:param CInfoDialog oInfoDlg: \xb9\xef\xb9\xb3
\t'''
    g_InfoDlg[iPlayerID] = oInfoDlg


def LogInfoIconClick(iID, bLightUp):
    if iID in MSGID_TO_LOGSTR:
        None(clickcounter.Log[MSGID_TO_LOGSTR[iID] if bLightUp else 1])
    


class _AvatarBox(interface.CClickBox):
    
    def __init__(self, parent, w, h, color = 0, alpha = 0, msgid = 0):
        interface.CClickBox.__init__(self, parent, w, h, color, alpha, msgid)
        self.m_lPhotoArr = None

    
    def SetPhotoArr(self, lPhotoArr):
        self.m_lPhotoArr = lPhotoArr

    
    def GetPhotoArr(self):
        return self.m_lPhotoArr



def SetPlayershowBtn(data, success, *args):
    pid = args[0]
    dlg = GetInfoDlg(pid)
    if dlg is None or dlg.IsShenHe():
        return None
    
    import httpplayershow
    resp = httpplayershow.Parse(data, success)
    btn = dlg.GetObject('ps_btn')
    if resp == False:
        btn.SetShow(0)
        return None
    
    ext_data = resp.get('ext_data', { })
    count = ext_data.get('records', 0)
    if count == 0:
        btn.SetShow(0)
        return None
    else:
        btn.SetShow(1)
    import misc
    if misc.IsTWServer():
        btn.SetShow(0)
    


def GetPlayerShowRealPicCount(dInfo):
    dPicFolderInfo = dInfo.get('ext_data', { })
    lPicInfo = dPicFolderInfo.get('items', { })
    iPicCount = dPicFolderInfo.get('records', 0)
    for dPic in lPicInfo:
        if PLAYERSHOW_PICDEFULT_NAME in dPic.get('imgsrc_b', ''):
            iPicCount -= 1
            continue
    
    return iPicCount


def RefreshPlayershowIconState(data, success, iPid):
    import httpplayershow
    import netfriend
    oDlg = GetInfoDlg(iPid)
    if oDlg is None or oDlg.IsShenHe():
        return None
    
    dResp = httpplayershow.Parse(data, success)
    if not dResp:
        return None
    
    iCount = GetPlayerShowRealPicCount(dResp)
    if iCount == 0:
        return None
    else:
        netfriend.C2SSendIconState(iPid, PLAYERSHOW_ICONID)
        LightUpInfoIconByID(iPid, PLAYERSHOW_ICONID)
        oDlg.RefreshInfoIconState(iPid)


def LightUpInfoIconByID(iPlayerID, iIconID):
    oPlayer = friend.GetControl().GetSafePlayer(iPlayerID)
    if oPlayer:
        iIconState = oPlayer.GetIconState()
        iIconState |= 1 << iIconID - 1
        oPlayer.SetIconState(iIconState)
    


def GetInfoIconStateByID(iPlayerID, iIconID):
    oPlayer = friend.GetControl().GetSafePlayer(iPlayerID)
    if oPlayer:
        iIconState = oPlayer.GetIconState()
        return iIconState & 1 << iIconID - 1
    
    return False


class CInfoDialog(combdialog.CCombDialog):
    
    class CMyListBox(interface.CListBox):
        
        def __init__(self, parent, color, font, x, y, w, h, fname = 'combdialog/\xca\xfa\xb9\xf6\xb6\xaf\xcc\xf5/down.igs'):
            interface.CListBox.__init__(self, parent, color, font, x, y, w, h, fname)
            self.m_DownButton.m_ParentNotify = True

        
        def OnButtonEnter(self, btn):
            import wrapinterface
            self.m_Tips = wrapinterface.CTextTips(None, -1, self.m_TipsText, interface.FontLT14_3, direct = 1)
            self.m_Tips.SetOwner(self.m_DownButton)

        
        def SetTipsText(self, txt):
            self.m_TipsText = txt

        
        def OnButtonLeave(self, btn):
            self.m_Tips = None

        
        def OnSelect(self, sel, notify = True):
            self.m_List = None

        
        def Enter(self):
            pass

        
        def Leave(self):
            pass


    
    def __init__(self, iPlayerID, iServerID = 0, iChannel = -1, iRealID = 0):
        import netfriend
        import httpplayershow
        self.m_oAvatarBox = None
        self.m_oAvatarImage = None
        self.m_oRoleViewDlg = None
        self.m_oOnlineText = None
        self.m_bDefaultAvatar = True
        self.m_sWalkerAndAvatorStateTip = ''
        self.m_bShowRoleFirst = False
        self.m_PID = iPlayerID
        self.m_iServerID = iServerID
        self.m_iChannel = iChannel
        self.m_iRealID = iRealID
        self.m_ShowBadge = True
        self.m_oRefreshTimer = None
        if friend.IsFriend(iPlayerID, 0):
            self.IsPreMoved(1)
            combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/friend/infonew_test.dlg')
            self.m_DlgHelpID = 5054
            self.m_Flag = False
            self.CheckFriendBtnValid()
            self.SetType(DLG_TYPE_FRIEND)
            self.GetObject('btn_copy').SetZ(2)
        elif friend.IsBan(iPlayerID):
            self.IsPreMoved(2)
            combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/friend/unban_test.dlg')
            self.m_ShowBadge = False
            self.m_Flag = True
            self.SetType(DLG_TYPE_BAN)
        elif friend.IsFriend(iPlayerID, 1):
            self.IsPreMoved(3)
            combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/friend/infonew2_test.dlg')
            self.SetShowObject('showblog', False)
            self.m_DlgHelpID = 5055
            self.m_Flag = False
            self.SetType(DLG_TYPE_TEMP_FRIEND)
            self.GetObject('btn_copy').SetZ(2)
        else:
            self.IsPreMoved(4)
            combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/friend/strangernew_test.dlg')
            self.m_Flag = False
            self.SetType(DLG_TYPE_STRANGER)
            self.GetObject('btn_zhanyou').SetShow(misc.IsInKuafuServer())
            self.GetObject('btn_haoyou').SetShow(not misc.IsInKuafuServer())
            self.GetObject('btn_copy').SetZ(2)
        interface.Center(self)
        SetInfoDlg(iPlayerID, self)
        self.m_Pos = self.GetPos()
        self.IsShenHe()
        self.m_RefreshTime = 0
        self.RefreshInfo()
        self.RefreshOldName()
        self.RefreshCopyNameImg()
        self.CreateCurStateTipsText(g_bSwitchBtnTips)
        self.CreateSwitchWalkerAndAvatorStateTips()
        self.m_IsBrith = None
        self.m_Content = None
        self.m_oPopMenu = None
        netfriend.C2SGetAchieve(iPlayerID, self.m_iServerID)
        self.ChangeBtnGiveName()
        mdavatar.GetAvatarModel().ResetSpecialFlag()
        oModel = teammgr.GetTeamMgr()
        oModel.ssConnect(oModel.SS_TeamListChanged, self.RefreshMakeTeamBtnText)

    
    def UpdateHorseRecordIcon(self):
        oFriend = friend.GetControl().GetSafePlayer(self.m_PID)
        iHorseOrFairy = oFriend.GetWalkState()
        if iHorseOrFairy == 3:
            iHorseId = oFriend.GetWalkStateNumber()
        elif iHorseOrFairy == 8:
            iFairy = oFriend.GetWalkStateNumber()
            iHorseId = ridedata.GetHorseIdByFairyId(iFairy)
        else:
            iHorseId = ridedefine.HORSE_PAIGE_PIGGY
        if not iHorseId:
            iHorseId = ridedefine.HORSE_PAIGE_PIGGY
        
        sPath = 'combdialog4/\xba\xc3\xd3\xd1\xbd\xe7\xc3\xe6/\xba\xc3\xd3\xd1\xb1\xea\xca\xb6/\xd7\xf8\xc6\xef/%d/' % iHorseId
        self.GetObject('btn_ride').SetPath(sPath)

    
    def ChangeRefreshTime(self):
        if self.m_oRefreshTimer:
            self.m_oRefreshTimer.Release()
            self.m_oRefreshTimer = None
        
        self.m_oRefreshTimer = timer.Timer(TIME_REFRESH, misc.Functor(self.SwitchAvatarAndWalker), iRepeat = -1, oRelayObj = self)

    
    def ChangeBtnGiveName(self):
        if not friend.IsBan(self.m_PID):
            if self.GetObject('btn_give'):
                pass
            self.GetObject('btn_give').SetText('\xc3\xd8 \xb0e')
        elif self.GetObject('btn_give'):
            pass
        self.GetObject('btn_give').SetText('\xb5\xb9 \xa4\xa9')

    
    def IsPreMoved(self, iType):
        funcDct = {
            1: (lambda idx: friend.IsFriend(idx, 0)),
            2: (lambda idx: friend.IsBan(idx)),
            3: (lambda idx: friend.IsFriend(idx, 1)),
            4: (lambda idx: if not friend.IsFriend(idx, 0) and friend.IsBan(idx):
passnot friend.IsFriend(idx, 1)) }
        func = funcDct[iType]
        for idx in g_InfoDlg:
            if func(idx) and g_InfoDlg[idx] and g_InfoDlg[idx].GetPos() == g_InfoDlg[idx].m_Pos:
                del g_InfoDlg[idx]
                return None
                continue
        

    
    def IsShenHe(self):
        if hero.IsShenHe():
            self.m_ShowBadge = False
            for name in ('showblog', 'ps_btn', 'btn_DYFriend', 'txtbadge1', 'txtbadge2', 'img', 'txtbadge', 'achieve'):
                obj = self.GetObject(name)
                if obj:
                    obj.SetShow(False)
                    continue
            
        

    
    def SetType(self, iType):
        self.m_InfoType = iType

    
    def ShowBlogBtn(self):
        self.m_Blog = None
        
        try:
            blogID = int(hero.GetPrivateData('FriendInfo', '%d' % self.m_PID))
        except:
            blogID = 0

        if blogID:
            import dreamblogdata
            dreamblogdata.SetBID2UserID(blogID, self.m_PID)
        
        obj = self.GetObject('showblog')
        if not obj or self.IsShenHe():
            return None
        
        if blogID and not (self.m_Flag) and self.m_PID == hero.g_ID:
            obj.SetShow(not misc.IsInKuafuServer())
            self.m_Blog = blogID
        else:
            obj.SetShow(False)

    
    def IsFriendDlg(self):
        return self.m_InfoType == DLG_TYPE_FRIEND

    
    def CheckFriendBtnValid(self):
        if not friend.IsFriend(self.m_PID, 0):
            return None
        
        nameList = [
            'btn_DYFriend',
            'btn_Refresh']
        if misc.IsTWServer():
            showNameList = [
                'btn_Refresh']
        else:
            showNameList = [
                'btn_DYFriend']
        for objName in nameList:
            self.GetObject(objName).SetShow(objName in showNameList)
        

    
    def RequestOtherStyle(self):
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xbc\xc8\xa4\xa3\xa4\xe4\xab\xf9\xb8\xf3\xaaA\xa8\xcf\xa5\xce')
            return None
        
        netplayerphoto.C2SOpenChildren()
        netplayerphoto.C2SOpenChrismas()
        mdopendlgmgr.GetNetSendMgr().RegistNetCB(self.OpenAppearanceAvatar)

    
    def CheckMYQBtn(self):
        if hero.IsShenHe():
            self.SetShowObject('showmyq', False)
            return None
        
        if misc.IsNationFightServer():
            self.SetShowObject('showmyq', False)
            return None
        
        oBtn = self.GetObject('showmyq')
        if oBtn:
            pass
        oBtn.SetText('\xa6n\xa4\xcd\xa8q')
        if self.m_PID == hero.g_ID:
            oMyq = self.GetObject('showmyq')
            if oMyq:
                (x, y) = oMyq.GetPos()
                oBlog = self.GetObject('showblog')
                if oBlog:
                    pass
                oBlog.SetPos(x, y)
            
        

    
    def OpenFriendMYQ(self, bOpenPublishDlg = False):
        import avatar
        import myqinterface
        import myqdefine
        iFriendID = self.m_PID
        oFriend = friend.GetControl().GetSafePlayer(iFriendID)
        lPhotoArr = getattr(oFriend, 'm_PhotoArr', None)
        if lPhotoArr:
            lAvatar = avatar.PhotoArr2Int(lPhotoArr)
        else:
            lAvatar = avatar.PhotoArr2Int(avatar.GetShapeDefaultPhoto(None))
        myqinterface.CacheFriendInfo(iFriendID, friend.GetShowName(iFriendID), lAvatar)
        myqinterface.OpenFriendMainDlg(iFriendID)
        if bOpenPublishDlg:
            myqinterface.ShowIssueNewDlg(0, myqdefine.TALK_TYPE)
        

    
    def SwitchAvatarAndWalker(self):
        global g_bSwitchBtnTips
        if self.m_oAvatarImage:
            pass
        bFlag = self.m_oAvatarImage.GetShow()
        g_bSwitchBtnTips = not bFlag
        self.SetCopyBtnShow(not bFlag)
        self.CreateCurStateTipsText(g_bSwitchBtnTips)
        self.CreateSwitchWalkerAndAvatorStateTips()
        if self.m_oAvatarImage:
            pass
        self.m_oAvatarImage.SetShow(not bFlag)
        if self.m_oAvatarBox:
            pass
        self.m_oAvatarBox.SetShow(not bFlag)
        if self.m_oRoleViewDlg:
            pass
        self.m_oRoleViewDlg.SetShow(bFlag)

    
    def IsTopmost(self):
        max_z = 0
        for shadow in interface.g_DialogList:
            dlg = shadow.Get()
            if dlg and dlg.GetShow():
                max_z = max(dlg.GetZ(), max_z)
                continue
        
        return self.GetZ() >= max_z

    
    def OnGroupTJ(self, pid):
        import group
        import wraptextobj
        if not misc.IsInKuafuServer() and group.CanIntroduce(pid):
            obj = self.GetObject('txt_group')
            (x, y) = obj.GetPos()
            self.m_GroupTJText = wraptextobj.CUnderLineClickText(self, x + 5, y + 5, '\xb1\xc0\xaf\xf2\xa5[\xa4J\xa5\xbb\xc0\xb0', interface.COLOR_347, interface.COLOR_347, interface.FontLT14_3, 10)
        else:
            self.m_GroupTJText = None

    
    def ShowInformation(self, data):
        self.m_Infos = []
        txt = str(data)
        txt = txt.replace('\n', '#r')
        obj = self.GetObject('loc_desc')
        (x, y) = obj.GetPos()
        (w, h) = obj.GetSize()
        self.m_Content = interface.CScrollRichText(self, x + 3, y + 3, w - 25, h)
        self.m_Content.AddTxt(txt, interface.FontLT14_3, 0)
        self.m_Content.ResetScrollBar(False)
        self.m_Content.Refresh()

    
    def UpdateAchieve(self, pid, score, paiming):
        if self.GetObject('achieve') and not hero.IsShenHe():
            msg = '\xa6\xa8\xb4N\xc1`\xbfn\xa4\xc0\xa1G%d ' % score
            if paiming:
                if paiming <= 10:
                    msg += '\xb1\xc6\xa6W\xa1G\xb2\xc4%d\xa6W' % paiming
                else:
                    msg += '\xb1\xc6\xa6W\xa1G%d\xa6W' % paiming
            else:
                msg += '\xb1\xc6\xa6W\xa1G500\xa6W\xa5H\xab\xe1'
            color = interface.COLOR_86
            self.m_AchieveTxt = combmacro.CTEXT(interface.CTextObject, 'achieve', self, msg, interface.FontLT14_3, color)
        
        self.m_PID = pid
        if self.m_Items:
            self.DrawIDTxtObj(self.m_Items[0])
        

    
    def ReBlog(self, blog, isbrith):
        import dreamblogdata
        dreamblogdata.SetBID2UserID(blog, self.m_PID)
        if self.m_Flag or self.IsShenHe():
            return None
        
        hero.SavePrivateData('FriendInfo', '%d' % self.m_PID, str(blog))
        if blog and self.m_PID == hero.g_ID:
            self.SetShowObject('showblog', not misc.IsInKuafuServer())
        else:
            self.SetShowObject('showblog', False)
        self.m_Blog = blog

    
    class CCopyNameClickBox(interface.CClickBox):
        
        def __init__(self, parent, w, h, color = 0, alpha = 0, msgid = 0):
            interface.CBoxObject.__init__(self, parent, w, h, color, alpha)
            interface.CClickObject.__init__(self, msgid)

        
        def LeftUp(self):
            par = self.GetParent()
            if hasattr(par, 'CopyName'):
                par.CopyName()
            


    
    class CCopyNameImage(wrapinterface.CImageWithTips):
        
        def LeftUp(self):
            par = self.GetParent()
            if hasattr(par, 'CopyName'):
                par.CopyName()
            


    
    def RefreshCopyNameImg(self):
        if self.m_InfoType != 0:
            return None
        
        obj = self.GetObject('box_nameimg')
        (x, y) = obj.GetPos()
        path = style.GetPath('\xd4\xd3\xcd\xbc\\\xcc\xe1\xca\xbe.igs')
        self.m_CopyNameImg = self.CCopyNameImage(self, path, 'shift+\xa5\xaa\xc1\xe4\xc2I\xc0\xbb\xa6W\xa6r\xa5i\xbd\xc6\xbbs\xa8\xec\xb0\xc5\xb6K\xaaO')
        self.m_CopyNameImg.SetPos(x, y)
        (x, y, w, h) = self.GetLocData('box_namearea')
        self.m_NameCopyBox = self.CCopyNameClickBox(self, w, h)
        self.m_NameCopyBox.SetPos(x, y)

    
    def CopyName(self):
        import key
        import C_sys
        if not C_sys.IsKeyDown(key.VK_SHIFT):
            return None
        
        name = getattr(self, 'm_Name', None)
        if name:
            import C_sys
            import usermacro
            C_sys.SetClipboardData(name)
            usermacro.PROMPT_MSG('\xa6\xa8\xa5\\\xbd\xc6\xbbs\xa8\xec\xb0\xc5\xb6K\xaaO')
        

    
    def RefreshOldName(self):
        self.m_OldNameListBox = None
        dInfo = friend.GetAttrValue(self.m_PID, 'm_OldNameDct')
        if not friend.IsFriend(self.m_PID, 0):
            return None
        
        lst = []
        txt = '\xb9\xef\xa4\xe8\xbc\xc8\xb5L\xb4\xbf\xa5\xce\xa6W'
        if dInfo:
            if dInfo['bShow']:
                if not dInfo.get('nameList'):
                    return None
                
                for name in dInfo['nameList']:
                    if name.startswith('\xaa\xb1\xaea'):
                        lst = []
                        return None
                    
                    lst.append(name)
                    txt = '\xc2I\xc0\xbb\xacd\xac\xdd\xaa\xb1\xaea\xb4\xbf\xa5\xce\xa6W'
                
                lst.reverse()
            else:
                txt = '\xb5L\xaak\xacd\xac\xdd\xa1A\xb9\xef\xa4\xe8\xa5\xbc\xa4\xb9\xb3\\\xacd\xac\xdd\xb4\xbf\xa5\xce\xa6W'
        
        self.m_OldNameListBox = combmacro.CLISTBOX(self.CMyListBox, 'pos_oldName', self, interface.COLOR_9, interface.FontLT14_3)
        self.m_OldNameListBox.SetItemProp(2, 16, min(2, len(lst)) * 18)
        self.m_OldNameListBox.SetTipsText(txt)
        for name in lst[:2]:
            self.m_OldNameListBox.AddTextItem(name)
        
        self.m_OldNameListBox.SetReadOnly(True)

    
    class CGroupListBox(interface.CListBox):
        
        def init(self, group):
            self.m_Group = group
            self.m_Msg2Group = { }
            mgrFolder = friend.GetFrdMgr()
            tmp = mgrFolder.GetGroupIDs()
            size = len(tmp)
            if size <= 5:
                self.SetItemProp(2, 16, size * 18)
            else:
                self.SetItemProp(2, 16, 90)
            for i in xrange(size):
                self.m_Msg2Group[i + 1] = tmp[i]
                self.AddTextItem(mgrFolder.Group2Name(tmp[i]))
            
            if group in tmp:
                idx = tmp.index(group) + 1
            else:
                idx = 1
            self.OnSelect(idx)

        
        def OnSelect(self, sel):
            interface.CListBox.OnSelect(self, sel)
            if sel >= interface.RIGHT_BUTTON_MESSAGE:
                return None
            
            g = self.m_Msg2Group.get(sel)
            if self.m_Group == g:
                return None
            
            mgrFolder = friend.GetFrdMgr()
            if mgrFolder.Group2Name(g):
                import netfriend
                netfriend.C2SSetGroup(self.GetParent().m_PID, g)
                self.m_Group = g
            


    
    def RefreshRoleView(self, oPlayer):
        import descinterface
        tRoleViewInfo = oPlayer.GetRoleViewInfo()
        if tRoleViewInfo:
            dDesc = tRoleViewInfo[1]
            self.m_bShowRoleFirst = descinterface.IsHasFashion(dDesc)
        else:
            self.m_bShowRoleFirst = False
        if tRoleViewInfo and tRoleViewInfo[0] != 0:
            oDlg = CRoleViewDialog(self, self.m_PID)
            (iX, iY, _, _) = self.GetLocData('box_icon')
            oDlg.SetPos(iX, iY)
            oDlg.SetZ(0)
            oDlg.SetShow(False)
            oDlg.SetRoleViewInfo(tRoleViewInfo)
            self.m_oRoleViewDlg = oDlg
            oBtn = self.GetObject('btn_change')
            if oBtn:
                oBtn.SetShow(True)
                oBtn.SetZ(2)
            
        else:
            self.m_oRoleViewDlg = None
            self.SetShowObject('btn_change', False)

    
    def RefreshAvatarView(self, oPlayer):
        import avatar
        import dlgshenmoisland
        self.m_oAvatarBox = None
        self.m_oAvatarImage = None
        self.m_oOnlineText = None
        iIcon = getattr(oPlayer, 'm_Icon', None)
        if iIcon:
            bFlag = True
            lPhotoArr = getattr(oPlayer, 'm_PhotoArr', None)
            (iX, iY, iW, iH) = self.GetLocData('box_icon')
            if lPhotoArr is not None and len(lPhotoArr) == 16:
                for v in lPhotoArr:
                    if v != 0:
                        bFlag = False
                        break
                        continue
                
            
            if bFlag:
                if iIcon % 2 == 1:
                    oPlayer.m_PhotoArr = lPhotoArr = [
                        0,
                        8,
                        0,
                        100,
                        7,
                        1,
                        0,
                        0,
                        0,
                        5,
                        2,
                        6,
                        0,
                        0,
                        7,
                        0]
                else:
                    oPlayer.m_PhotoArr = lPhotoArr = [
                        0,
                        10,
                        0,
                        300,
                        8,
                        2,
                        0,
                        0,
                        0,
                        6,
                        4,
                        6,
                        0,
                        0,
                        8,
                        0]
            
            iShenmoShapeList = [
                2480,
                2630,
                2690,
                2770,
                2780,
                2890,
                3054,
                3058,
                3059,
                3060,
                3061,
                3062]
            lPhoto = avatar.PhotoArr2Int(lPhotoArr)
            if dlgshenmoisland.IsShenmoHuodong() and lPhoto[0] in iShenmoShapeList:
                oAvatarImg = ui.CImage(self.GetObject('box_icon'), '\xd4\xd3\xcd\xbc/shenmo/140_200/%d.png' % lPhoto[0], interface.UIPath)
            else:
                oAvatarImg = avatar.GetCreateBigAvatarImg(self.GetObject('box_icon'), lPhotoArr, self.m_PID)
                self.m_bDefaultAvatar = avatar.IsDefaultPhoto(lPhotoArr)
                self.SetCopyBtnShow(True)
                _onlinetext = {
                    2: ('\xbe\xd4\xb7\xf9\xa6b\xbdu', [
                        16724016,
                        16777215]),
                    1: ('\xa6b\xbdu', [
                        16724016,
                        16777215]),
                    0: ('\xc2\xf7\xbdu', [
                        16724016,
                        16777215]) }
                if getattr(oPlayer, 'm_Online', 0):
                    iOnline = 1
                elif getattr(oPlayer, 'm_DYOnline', 0):
                    iOnline = 2
                else:
                    iOnline = 0
                self.m_oOnlineText = interface.CTextObject(self, _onlinetext[iOnline][0], interface.FontLT12E_1, _onlinetext[iOnline][1])
                (iTextW, iTextH) = self.m_oOnlineText.GetSize()
                (iOffX, iOffY) = style.GetIntTuple('dlginfo.CInfoDialog', 'data_info_offset')
                self.m_oOnlineText.SetPos(iX + iW - iOffX - iTextW, iY + iH - iOffY - iTextH)
                self.m_oOnlineText.SetZ(1)
            oAvatarImg.SetPos(7, 6)
            self.m_oAvatarImage = oAvatarImg
            oBox = _AvatarBox(self, 154, 213, msgid = 30)
            oBox.SetZ(1)
            None(None(None, None, None, None, None, None, oBox.SetPos), iY)
            oBox.SetPhotoArr(lPhotoArr)
            self.m_oAvatarBox = oBox
        

    
    def RefreshShowSkillIcon(self, iSkillID, iLevel):
        import skillmagicdefines
        import liftskilldescdata
        oLocIcon = self.GetObject('loc_icon')
        oBgIcon = self.GetObject('bg_icon')
        oLvl = self.GetObject('text_skilllvl')
        oTxtBadge5 = self.GetObject('txtbadge5')
        oTxtBadge3 = self.GetObject('txtbadge3')
        if oLocIcon is not None and iSkillID is not None and iSkillID != 0 and oLvl is not None:
            pass
        bShowLifeSkill = iLevel is not None
        if oLvl:
            oLvl.SetShow(bShowLifeSkill)
        
        if oLocIcon:
            oLocIcon.SetShow(bShowLifeSkill)
        
        if oTxtBadge5:
            oTxtBadge5.SetShow(bShowLifeSkill)
        
        if oTxtBadge3:
            oTxtBadge3.SetShow(bShowLifeSkill)
        
        if not bShowLifeSkill:
            self.m_pBitMap = None
        
        if oBgIcon:
            oBgIcon.SetShow(bShowLifeSkill)
        
        if bShowLifeSkill:
            (sPath, sPack) = skillmagicdefines.GetCharSkillPathByID(iSkillID)
            self.m_pBitMap = ui.CImage(self, sPath, sPack)
            (_, sDesc, sMark) = liftskilldescdata.GetSkillInfoByID(iSkillID)
            (x1, y1) = oLocIcon.GetPos()
            self.m_pBitMap.SetSize(29, 29)
            self.m_pBitMap.SetPos(x1, y1)
            self.m_oSkillTips = wrapinterface.CBoxWithTips(self, x1, y1, 29, 29, sDesc, font = interface.FontLT14_3)
            oTxtBadge5.SetText(sMark)
            oLvl.SetText('%d\xaf\xc5' % iLevel)
        

    
    def DrawIDTxtObj(self, oTextObject):
        import prettynuminterface
        import prop
        iPlayerID = self.m_PID
        if not isinstance(iPlayerID, prop.CPlayerID):
            oSafePlayer = friend.GetControl().GetSafePlayer(self.m_PID)
            if oSafePlayer:
                iPlayerID = oSafePlayer.GetPlayerID()
            
        
        if not isinstance(iPlayerID, prop.CPlayerID):
            if oTextObject:
                oTextObject.SetShow(False)
            
        else:
            self.m_oPrettyNumView = prettynuminterface.DrawIDTxtObj(self, iPlayerID, oTextObject)
        self.m_PID = iPlayerID

    
    def RefreshInfo(self, iNewPlayerID = None):
        global g_bSwitchBtnTips
        import hero
        import wrapui
        import dlgbadge
        import banword
        if iNewPlayerID is not None:
            self.m_PID = iNewPlayerID
        
        iPlayerID = self.m_PID
        oMgr = friend.GetControl()
        oPlayer = oMgr.GetUpdatePlayer(iPlayerID)
        name = getattr(oPlayer, 'm_Name', '')
        sGroup = getattr(oPlayer, 'm_OrgName', '')
        sTitle = getattr(oPlayer, 'm_Title', '')
        (sTitle, _, _) = wrapui.HandleLink(sTitle)
        grade = getattr(oPlayer, 'm_Grade', None)
        iClass = getattr(oPlayer, 'm_Class', None)
        iCountry = getattr(oPlayer, 'm_Country', None)
        iShowSkillID = getattr(oPlayer, 'm_iShowSkillID', None)
        iShowSkillLevel = getattr(oPlayer, 'm_iShowSkillLevel', None)
        self.RefreshRoleView(oPlayer)
        self.RefreshShowSkillIcon(iShowSkillID, iShowSkillLevel)
        obj = self.GetObject('btn_pingbi')
        if obj:
            obj.Enable(name)
        
        if hero.GetHeroID() == iPlayerID:
            self.GetObject('btn_linshi').Enable(False)
            self.GetObject('btn_haoyou').Enable(False)
            self.GetObject('btn_pingbi').Enable(False)
            if self.GetObject('btn_jiyu'):
                pass
            self.GetObject('btn_jiyu').Enable(False)
            if self.GetObject('btn_give'):
                pass
            self.GetObject('btn_give').Enable(False)
            self.GetObject('btn_zudui').Enable(False)
            self.GetObject('btn_jiaoyi').Enable(False)
        
        txts = [
            str(world.GetUIShowID(iPlayerID)),
            name,
            None,
            None,
            None,
            sGroup,
            sTitle]
        if grade is not None:
            txts[2] = '%d\xaf\xc5' % grade
        
        if iClass is not None:
            txts[3] = hero.id2class(iClass)
        
        if iCountry is not None:
            txts[4] = hero.id2country(iCountry)
        
        vip = getattr(oPlayer, 'm_Vip', False) != 0
        if iCountry is not None and grade >= 50:
            force = hero.GetForce(iCountry)
        else:
            force = 0
        if friend.IsFriend(iPlayerID) and self.GetObject('txt_field'):
            if txts[3] is not None:
                txts[2] = txts[2] + txts[3]
                txts[3] = None
            
            if friend.IsFriend(iPlayerID, 0):
                iGroup = getattr(oPlayer, 'm_FriendGroup', 0)
                iShip = getattr(oPlayer, 'm_FriendShip', 0)
                sRelation = friend.CRelationItem.GetRltTextWithID(iPlayerID)
                self.m_GroupListBox = combmacro.CLISTBOX(self.CGroupListBox, 'txt_field', self, interface.COLOR_9, interface.FontLT14_3)
                self.m_GroupListBox.init(iGroup)
                self.m_GroupListBox.SetReadOnly(True)
                self.m_RelationTxt = combmacro.CTEXT(interface.CTextObject, 'txt_relation', self, '%-6d%13s' % (iShip, sRelation), interface.FontLT14_3, interface.COLOR_9, 0)
            
        elif friend.IsBan(iPlayerID):
            if txts[3] is not None:
                txts[2] = txts[2] + txts[3]
                txts[3] = None
            
        
        _ctrls = ('txt_id', 'txt_name', 'txt_grade', 'txt_class', 'txt_country', 'txt_group')
        self.m_Name = txts[1]
        self.m_Items = []
        for idx, t in enumerate(txts[:-1]):
            if t is not None and self.GetObject(_ctrls[idx]):
                self.m_Items.append(combmacro.CRICHTEXT(interface.CRichTextObject, _ctrls[idx], self, t, interface.FontLT14_3, interface.COLOR_9))
                continue
        
        (x, y, w, h) = self.GetLocData('title')
        item = wrapinterface.CRollTextObject(self, w, h, x, y, txts[6], interface.FontLT14_3, interface.COLOR_9, align = interface.ALIGN_LEFT, limit = 10, itype = 2)
        banword.AddCheckWordTask([
            (txts[6], iPlayerID)], 'title')
        self.m_Items.append(item)
        self.DrawIDTxtObj(self.m_Items[0])
        if friend.IsFriend(iPlayerID, 0):
            txtname2 = friend.GetFriendName2(iPlayerID)
            if txtname2:
                self.m_namectl = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_name2', self, txtname2, interface.FontLT14_3, interface.COLOR_9)
            
            self.CreateMarkName()
        
        self.SetShowObject('btn_VIP', vip)
        self.RefreshAvatarView(oPlayer)
        g_bSwitchBtnTips = not (self.m_bShowRoleFirst)
        if self.m_oAvatarImage:
            if self.m_oAvatarImage:
                pass
            self.m_oAvatarImage.SetShow(g_bSwitchBtnTips)
            self.SetCopyBtnShow(g_bSwitchBtnTips)
        
        if self.m_oAvatarBox:
            if self.m_oAvatarBox:
                pass
            self.m_oAvatarBox.SetShow(g_bSwitchBtnTips)
        
        if self.m_oRoleViewDlg:
            self.m_oRoleViewDlg.SetShow(not g_bSwitchBtnTips)
        
        badge = getattr(oPlayer, 'm_Badge', None)
        if self.m_ShowBadge and badge:
            self.m_bigimg = dlgbadge.SetBigBadgeByIdx(self, 'img', badge)
            desc = dlgbadge.GetFriendBadgeTxt(badge)
            if desc:
                color = interface.COLOR_188
                font = interface.FontLT14_4
                self.m_txtbadge = combmacro.CRICHTEXT(wrapinterface.WrapRichText, 'txtbadge', self, desc, font, color, align = interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)
            else:
                self.m_txtbadge = None
        else:
            self.m_bigimg = None
            self.m_txtbadge = None
        if self.m_ShowBadge:
            valid = dlgbadge.CheckBadgeVaild(badge)
            self.GetObject('txtbadge1').SetShow(valid)
            self.GetObject('txtbadge2').SetShow(valid)
        
        self.OnGroupTJ(iPlayerID)
        self.InitMouseEvent()
        self.ChangeRefreshTime()
        if not self.m_InfoType == DLG_TYPE_BAN:
            self.UpdateHorseRecordIcon()
            self.RefreshInfoIconState(iPlayerID)
        
        self.RefreshMakeTeamBtnText()

    
    def RefreshInfoIconState(self, iPlayerID):
        import httpplayershow
        if not GetInfoIconStateByID(self.m_PID, PLAYERSHOW_ICONID):
            httpplayershow.SearchPlayerShow(RefreshPlayershowIconState, '', misc.GetOrigServerID(), '', 1, str(iPlayerID), True, iPlayerID)
        
        oActivateIconList = []
        oUnactivateIconList = []
        for iIconID in ICONID_TO_BTNNAME:
            if not GetInfoIconStateByID(self.m_PID, iIconID):
                self.GetObject(ICONID_TO_BTNNAME[iIconID]).SetAllFrameGrey(True)
                self.GetObject(ICONID_TO_BTNNAME[iIconID]).SetTips(ICON_TIPS[ICONID_TO_BTNNAME[iIconID]][1], iTipsDirect = 2)
                oUnactivateIconList.append(ICONID_TO_BTNNAME[iIconID])
                continue
            self.GetObject(ICONID_TO_BTNNAME[iIconID]).SetAllFrameGrey(False)
            self.GetObject(ICONID_TO_BTNNAME[iIconID]).SetTips(ICON_TIPS[ICONID_TO_BTNNAME[iIconID]][0], iTipsDirect = 2)
            oActivateIconList.append(ICONID_TO_BTNNAME[iIconID])
        
        oActivateIconList = sorted(oActivateIconList, key = (lambda x: ICON_SORT_DICT[x]))
        oUnactivateIconList = sorted(oUnactivateIconList, key = (lambda x: ICON_SORT_DICT[x]))
        oActivateIconList.extend(oUnactivateIconList)
        for iNum in xrange(0, len(oActivateIconList)):
            if not self.GetObject('img_icon%d' % iNum):
                break
            
            interface.AlignObjects(self.GetObject(oActivateIconList[iNum]), self.GetObject('img_icon%d' % iNum), interface.ALIGN_MIDDLE)
        

    
    def SetCopyBtnShow(self, bShow):
        if bShow and self.m_bDefaultAvatar:
            bShow = False
        
        self.SetShowObject('btn_copy', bShow)

    
    def CreateMarkName(self):
        import wrapinterface
        if not misc.IsInKuafuServer() and self.GetObject('txt_name2'):
            self.SetShowObject('btn_MarkName', True)
            (x, y, w, h) = self.GetLocData('txt_name2')
            self.m_NameClickBox = wrapinterface.CBoxWithTips(self, x + 5, y + 1, w - 20, h - 1, '\xb2K\xa5[\xa9\xce\xad\xd7\xa7\xef\xa6n\xa4\xcd\xb3\xc6\xb5\xf9\xa6W', font = interface.FontLT14_3, msgid = 21)
        else:
            self.SetShowObject('btn_MarkName', False)
            self.m_NameClickBox = None

    
    def InitMouseEvent(self):
        
        def _TextMouseEvent(dlg):
            if dlg.IsTopmost():
                obj = dlg._GetTips()
                if obj is None or obj != dlg.m_LastEnter:
                    if dlg.m_LastEnter:
                        dlg.m_LastEnter.OnLeave()
                        dlg.m_LastEnter = None
                    
                
                if obj and obj != dlg.m_LastEnter:
                    obj.OnEnter()
                    dlg.m_LastEnter = obj
                
            elif dlg.m_LastEnter:
                dlg.m_LastEnter.OnLeave()
                dlg.m_LastEnter = None
            
            return ()

        self.m_LastEnter = None
        self.CreatePyCommand(5, _TextMouseEvent)

    
    def _GetTips(self):
        if self.m_txtbadge is None:
            return None
        
        import cursor
        (x, y) = cursor.GetPos()
        rt = self.m_txtbadge
        if rt.GetShow():
            (rx, ry) = rt.GetScreenPos()
            id = int(rt.ClickID(x - rx, y - ry))
            if rt.m_LinkObj.get(id):
                return rt.m_LinkObj[id]
            
        

    
    def ShowPlayerShow(self, bOpenUploadDlg = False):
        import dlgplayershow
        oPlayershow = dlgplayershow.GetPlayerShow(True)
        oPlayershow.SearchPlayerShow(gameid = self.m_PID, serverID = misc.GetServerID())
        if bOpenUploadDlg:
            oPlayershow.OpenUploadDlg()
            oPlayershow.OnClickUploadBtn()
        

    
    def OnClickMakeTeam(self):
        if self.IsValidKickMember():
            iPlayerID = self.m_PID
            oDlg = teamui.GetTeamDialog()
            if oDlg:
                oDlg.KickMemberByID(iPlayerID)
            
        else:
            netteam.C2SMakeTeam(self.m_PID)
        self.RefreshMakeTeamBtnText()

    
    def RefreshMakeTeamBtnText(self):
        if self.m_InfoType != DLG_TYPE_BAN:
            if self.m_InfoType == DLG_TYPE_STRANGER:
                sBtnName = 'btn_zudui'
            else:
                sBtnName = 'noname6'
            if self.IsValidKickMember():
                self.GetObject(sBtnName).SetText('\xbd\xd0\xc2\xf7\xb6\xa4\xad\xfb')
            else:
                self.GetObject(sBtnName).SetText('\xb2\xd5\xb6\xa4')
        

    
    def IsValidKickMember(self):
        bIsTeammate = False
        oMgr = teammgr.GetTeamMgr()
        bLeader = oMgr.IsLeader()
        if not bLeader:
            return False
        
        dTeammateInfoList = teammgr.GetTeamMgr().GetTeamList()
        for dTeammateInfo in dTeammateInfoList:
            if self.m_PID == dTeammateInfo.get('id', 0):
                bIsTeammate = True
                break
                continue
        
        if bIsTeammate:
            pass
        return bLeader

    
    def OnReport(self):
        import dlgreport
        import defines
        iCh = self.m_iChannel
        if iCh >= 0:
            iServerID = self.m_iServerID
            iRealID = self.m_iRealID
            if iServerID and iRealID:
                dData = {
                    'iServerID': iServerID,
                    'iKuaFuID': self.m_PID,
                    'iRealID': iRealID }
                dlgreport.C2GSNewOpenReport(self.m_iRealID, self.m_Name, iCh, dData)
            elif iCh in defines.NONAME_REPORT_TUPLE:
                dData = {
                    'iTime': self.m_iRealID }
                dlgreport.C2GSNewOpenReport(self.m_PID, self.m_Name, iCh, dData, bForce = True)
            else:
                dlgreport.C2GSNewOpenReport(self.m_PID, self.m_Name, iCh)
        else:
            dlgreport.C2GSNewOpenReport(self.m_PID, self.m_Name, dlgreport.TYPE_TITLE)

    
    def OnClickExtraFunction(self, iType):
        if self.m_oPopMenu and self.m_oPopMenu.GetShow():
            self.m_oPopMenu = None
        elif not self.m_oPopMenu:
            self.CreatePopMenu(iType)
        else:
            self.m_oPopMenu.SetShow(True)

    
    def CreatePopMenu(self, iType):
        import nethdorgchuangong
        import dlgreport
        import popmenu
        if misc.GetKuaFuArenaFlag():
            iShowMask = 1
        else:
            iShowMask = 2
        dChuanGong = nethdorgchuangong.GetChuanGong()
        bShow = dChuanGong.get(self.m_PID, False)
        bOnlyReport = dlgreport.IsKuaFuReport(self.m_iServerID, self.m_iChannel)
        if iType == POPMENU_TYPE_STRANGER:
            if self.m_InfoType == DLG_TYPE_TEMP_FRIEND:
                iType = POPMENU_TYPE_TEMPFRIEND
                sBtnName = 'noname9'
            else:
                sBtnName = 'btn_pingbi'
        elif iType == POPMENU_TYPE_FRIEND:
            sBtnName = 'btn_DYFriend'
        else:
            sBtnName = 'noname6'
        (iX, iY) = self.GetObject(sBtnName).GetPos()
        (iOffX, iOffY) = style.GetOffset('friendinfopopmenu', 'btnOffset')
        self.m_oPopMenu = popmenu.PopFriendInfoMenu(self, iX + iOffX, iY + iOffY, self.m_PID, self.m_Name, self.m_iChannel, iShowMask, bShow, bOnlyReport, iType)
        self.m_oPopMenu.SetRightUpShield(False)

    
    def OnBan(self):
        import usermacro
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xb8\xf3\xaaA\xa4\xa3\xa4\xb9\xb3\\\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
            return None
        
        import dlgshieldtempfriendmsgconfirm
        dlgshieldtempfriendmsgconfirm.OpenShieldTempFriendMsgConfirmDlg(misc.Functor(self.OnConfirmBan))

    
    def OnConfirmBan(self, iType):
        if iType == 0:
            return None
        
        friend.BanPlayer(self.m_PID, iBanType = iType, iWithTips = 0)
        del g_InfoDlg[self.m_PID]

    
    def OnUnBan(self):
        import usermacro
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xb8\xf3\xaaA\xa4\xa3\xa4\xb9\xb3\\\xa8\xcf\xa5\xce\xa6\xb9\xa5\\\xaf\xe0')
            return None
        
        friend.UnbanPlayer(self.m_PID, iWithTips = 0)
        del g_InfoDlg[self.m_PID]

    
    def LeftUp(self):
        if self.IsCanUseQuickLogin():
            import gmcommanddata
            gmcommanddata.AutoLogin(str(self.m_PID))
        
        combdialog.CCombDialog.LeftUp(self)

    
    def RightUp(self):
        if self.IsCanUseQuickLogin():
            import os
            import netserver
            import C_sys
            (sArea, sServer) = netserver.g_LoginServer
            if C_sys.IsLogDebug():
                sLoginCmd = 'ClientLoaderWithLog.exe'
            else:
                sLoginCmd = 'mxmain.dll'
            os.system('start %s p AutoLogin:%s:%s:#%d:11111111:%d' % (sLoginCmd, sArea, sServer, self.m_PID, self.m_PID))
        
        combdialog.CCombDialog.RightUp(self)

    
    def IsCanUseQuickLogin(self):
        import innerversion
        import cursor
        if permission.IsOpenAutoLogin():
            (x, y) = cursor.GetPos()
            (ix, iy) = self.GetObject('txt_id').GetScreenPos()
            (iw, ih) = self.GetObject('txt_id').GetSize()
            if x < x:
                pass
            elif x < ix + iw:
                if y < y:
                    pass
                elif y < iy + ih:
                    return True
                
            return False
        else:
            return False

    
    def Introduce2Group(self):
        import dlgnpc
        dlgnpc.ShowClientDlg('\xbdT\xbb{\xb1\xc0\xaf\xf2#Y%s#n\xa5[\xa4J\xa5\xbb\xc0\xb0\xb6\xdc\nQ\xbdT\xa9w\nQ\xa8\xfa\xae\xf8' % self.m_Name, '', misc.Functor(self.DoIntroduce2Group))

    
    def DoIntroduce2Group(self, iMsgID):
        import group
        if iMsgID == 1:
            group.Introduce2Group(self.m_PID, self.m_Name)
        

    
    def OnOpenNewGive(self):
        import newgiveinterface
        newgiveinterface.SetGivePlayer(self.m_PID, self.m_Name)
        newgiveinterface.OpenNewGiveDlg()

    
    def CreateSwitchWalkerAndAvatorStateTips(self):
        self.GetObject('btn_change').SetTips(self.m_sWalkerAndAvatorStateTip, 2)

    
    def CreateCurStateTipsText(self, bTrue):
        if bTrue:
            self.m_sWalkerAndAvatorStateTip = '\xc2I\xc0\xbb\xacd\xac\xdd\xa4H\xaa\xab\xb3y\xab\xac'
        else:
            self.m_sWalkerAndAvatorStateTip = '\xc2I\xc0\xbb\xacd\xac\xdd\xc0Y\xb9\xb3\xa8q'

    
    def OpenAppearanceAvatar(self):
        newappearancecontext.Get().OpenAppDlg(nPage = newappearancedefine.MAIN_PAGE_AVATAR, bNewPage = True)
        if self.m_oAvatarImage:
            iAttrList = misc.DeepCopy(self.m_oAvatarImage.GetAttrList())
            dPalData = avatar.GetAvatarColorByID(self.m_PID)
            mdavatar.GetAvatarModel().RefreshImitateAvatar(iAttrList, dPalData)
        

    
    def OnClickMYQIcon(self, iMsgID):
        import dlgnpc
        bLight = GetInfoIconStateByID(self.m_PID, MYQ_ICONID)
        if self.CheckKuaFuServer(iMsgID, bLight):
            return None
        
        if bLight:
            self.OpenFriendMYQ()
        elif self.m_PID == hero.GetRealID():
            dlgnpc.ShowClientDlg('\xb5o\xb0e\xa5\xf4\xb7N\xa6n\xa4\xcd\xa8q\xb0\xca\xbaA\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0\nQ\xb5o\xa7G\xb0\xca\xbaA', '', misc.Functor(self.HandleMYQDlgNpc))
        
        LogInfoIconClick(iMsgID, bLight)

    
    def OnClickPlayerShowIcon(self, iMsgID):
        bLight = GetInfoIconStateByID(self.m_PID, PLAYERSHOW_ICONID)
        if self.CheckKuaFuServer(iMsgID, bLight):
            return None
        
        if bLight:
            self.ShowPlayerShow()
        elif self.m_PID == hero.GetRealID():
            dlgnpc.ShowClientDlg('\xa6b\xafu\xa4H\xa8q\xa4W\xb6\xc7\xa6\xdb\xa4v\xb7\xd3\xa4\xf9\xab\xe1\xc2I\xabG\xb9\xcf\xbc\xd0\nQ\xa4W\xb6\xc7\xb7\xd3\xa4\xf9', '', misc.Functor(self.HandlePlayerShowDlgNpc))
        
        LogInfoIconClick(iMsgID, bLight)

    
    def HandleMYQDlgNpc(self, iMsgID):
        if iMsgID == 1:
            self.OpenFriendMYQ(True)
        

    
    def HandlePlayerShowDlgNpc(self, iMsgID):
        if iMsgID == 1:
            self.ShowPlayerShow(True)
        

    
    def OnClickInfoIcon(self, iMsgID):
        import netfriend
        sIconName = self.GetObjectNameByMsgID(iMsgID)
        for iIconID in ICONID_TO_BTNNAME:
            if ICONID_TO_BTNNAME[iIconID] == sIconName:
                netfriend.C2SClickIcon(self.m_PID, iIconID)
                if iMsgID in MSGID_TO_LOGSTR:
                    None(clickcounter.Log[MSGID_TO_LOGSTR[iMsgID] if GetInfoIconStateByID(self.m_PID, iIconID) else 1])
                
                break
                continue
        

    
    def OnClickSpecialIcon(self, iMsgID, iIconId):
        import dlgnpc
        bLight = GetInfoIconStateByID(self.m_PID, iIconId)
        if self.CheckKuaFuServer(iMsgID, bLight):
            return None
        
        bMySelf = self.m_PID == hero.GetRealID()
        if not bLight and bMySelf:
            if iIconId == FASHION_ICONID:
                dlgnpc.ShowClientDlg(dialoguecommondata.GetDialogue('recordiconfunc', 1005), '', misc.Functor(self.OnOpenApparenceDlg, newappearancedefine.SUB_PAGE_FASHIONDRESS, { }))
            elif iIconId == HORSE_ICONID:
                dlgnpc.ShowClientDlg(dialoguecommondata.GetDialogue('recordiconfunc', 1006), '', misc.Functor(self.OnOpenApparenceDlg, newappearancedefine.MAIN_PAGE_HORSE, { }))
            elif iIconId == VOICE_CARD:
                dlgnpc.ShowClientDlg(dialoguecommondata.GetDialogue('recordiconfunc', 1007), '', misc.Functor(self.RequestOpenVoiceCardView))
            
            LogInfoIconClick(iMsgID, bLight)
        elif bLight:
            self.OnClickInfoIcon(iMsgID)
        

    
    def RequestOpenVoiceCardView(self, iMagId):
        if iMagId:
            import netvoicecard
            netvoicecard.C2GSOpenUI(self.m_PID)
        

    
    def OnOpenApparenceDlg(self, iPage, dExtend, iMsgID):
        if iMsgID:
            newappearancecontext.Get().OpenAppDlg(iPage, dExtendData = dExtend, bNewPage = True)
        

    
    def CheckKuaFuServer(self, iMsgId, bLightUp):
        LogInfoIconClick(iMsgId, bLightUp)
        bKuafuServer = misc.IsInKuafuServer()
        if bKuafuServer:
            usermacro.PROMPT_MSG('\xbd\xd0\xa6^\xad\xec\xaaA\xa8\xcf\xa5\xce\xb8\xd3\xa5\\\xaf\xe0')
        
        return bKuafuServer

    
    def OnMessage(self, msgid):
        global g_ReNamedlg
        import netctrycontest
        import usermacro
        import dlgtalk
        if msgid == 1:
            t = misc.Time()
            if t - self.m_RefreshTime <= t - self.m_RefreshTime:
                pass
            elif t - self.m_RefreshTime < 10:
                usermacro.PROMPT_MSG(usermacro.TRYAGAIN)
                return None
            
            self.m_RefreshTime = t
            import netfriend
            netfriend.C2SGetInfo(self.m_PID)
        elif msgid == 2:
            if g_InfoDlg.get(self.m_PID):
                del g_InfoDlg[self.m_PID]
            
        elif msgid == 4:
            self.OnClickMakeTeam()
        elif msgid == 5:
            self.OnOpenNewGive()
        elif msgid == 6:
            import netplayer
            netplayer.C2SRequestTrade(self.m_PID)
        elif msgid == 7:
            import dlgdreamblog
            if self.m_Blog:
                dlgdreamblog.OtherMainPage(int(self.m_Blog))
            
        elif msgid == 8:
            import dlgbrith
            dlgbrith.ShowSend(self.m_PID, self.m_Name)
        elif msgid == 9:
            import nethero
            nethero.C2SInviteMXS(self.m_PID)
        elif msgid == 10:
            self.Introduce2Group()
        elif msgid == 11:
            import dlgtalk
            dlgtalk.ShowTalkDialog(self.m_PID, friend.GetFriendName(self.m_PID), friend.GetFriendIcon(self.m_PID))
            if self.m_PID in g_InfoDlg:
                del g_InfoDlg[self.m_PID]
            
        elif msgid == 13:
            clickcounter.Log('\xb2\xe1\xa4\xd1\xb0O\xbf\xfd')
            dlg = dlgtalk.ShowTalkDialog(self.m_PID, friend.GetFriendName(self.m_PID), friend.GetFriendIcon(self.m_PID))
            if dlg:
                dlg.ShowHistory()
            
        elif msgid == 14:
            ShowDeleteDlg(self.m_PID, '\xbdT\xbb{\xadn\xbbP%s\xc2_\xa5\xe6\xb6\xdc\xa1H' % self.m_Name)
        elif msgid == 15:
            import netfriend
            netfriend.C2SAddFriend(self.m_PID)
            clickcounter.Log('\xc0\xc9\xae\xd7\xac\xc9\xad\xb1-\xb2K\xa5[\xa6n\xa4\xcd')
        elif msgid == 16:
            import netfriend
            netfriend.C2SAddTemp(self.m_PID)
            self.OnMessage(2)
        elif msgid == 17:
            self.OnClickExtraFunction(POPMENU_TYPE_STRANGER)
        elif msgid == 18:
            self.OnUnBan()
        elif msgid == 19:
            import popmenu
            import cursor
            mx = cursor.GetX()
            my = cursor.GetY()
            self.m_PopMenu = popmenu.PopTargetMenu(interface.MainPanel, mx, my, self.m_PID, self.m_Name)
        elif msgid == 20:
            aid = getattr(self, 'm_AccountID', 0)
            if aid:
                import netaccountfriend
                netaccountfriend.C2SAddFriendByID(aid, '')
            elif misc.IsNationFightServer():
                netctrycontest.C2SAddAccountFriend(self.m_PID)
            
            clickcounter.Log('\xc0\xc9\xae\xd7\xac\xc9\xad\xb1-\xb2K\xa5[\xbe\xd4\xa4\xcd')
        elif msgid == 21:
            if stopgamemoduleinterface.CheckStop(gamemoduledefines.GAMEMODULE_FRIENDNICKNAME):
                return None
            
            g_ReNamedlg = CRenameDialog(self, self.m_PID, 50, 120)
        elif msgid == 22:
            self.ShowPlayerShow()
        elif msgid == 23:
            self.OnClickExtraFunction(POPMENU_TYPE_FRIEND)
        elif msgid == 30:
            import dlggm
            if permission.IsGM():
                name = friend.GetAttrValue(self.m_PID, 'm_Name', None)
                grade = friend.GetAttrValue(self.m_PID, 'm_Grade', None)
                dlggm.ShowGMdlg(self.m_PID, name, grade, self.m_oAvatarBox.GetPhotoArr())
            
        elif msgid == 31:
            import dlgitembill
            dlgitembill.ShowVIPDialog()
        elif msgid == 32:
            import dlgnpc
            dlgnpc.ShowClientDlg('\xaaA\xb0\xc8\xbe\xb9\xb6}\xaaA\xae\xc9\xb6\xa1\xba\xa11\xad\xd3\xa4\xeb\xa1]30\xa4\xd1\xa1^\xa1A\xa6P\xae\xc9\xb5\xa5\xaf\xc5\xa4W\xad\xad\xb6}\xa9\xf1\xa8\xec50\xaf\xc5\xa5H\xab\xe1\xa1A\xa4Z50\xaf\xc5\xa5H\xa4W\xaa\xba\xa9\xd2\xa6\xb3\xaa\xb1\xaea\xb1N\xb9\xba\xa4\xc0\xac\xb0\xa1u\xafT\xb1\xda\xab\xd2\xb0\xea\xa1v\xbbP\xa1u\xa8\xdf\xb1\xda\xc1p\xb7\xf9\xa1v\xa8\xe2\xa4j\xb0}\xc0\xe7#r\xa1i\xac\xdb\xc3\xf6\xa5\xf4\xb0\xc8NPC\xa1j#r\xb6\xb3\xb3\xb6\xa8\xa6\xb0}\xc0\xe7\xa5\xf4\xb0\xc8\xbb\xe2\xa8\xfa\xa4H\xa1u\xc2\xed\xc5]\xb1N\xadx\xa1v', '', None)
        elif msgid == 33:
            self.OpenFriendMYQ()
        elif msgid == 34:
            self.SwitchAvatarAndWalker()
        elif msgid == 35:
            clickcounter.Log('\xbc\xd2\xa5\xe9\xa6n\xa4\xcd\xc0Y\xb9\xb3\xa8q')
            self.RequestOtherStyle()
        elif msgid == 36:
            self.OnClickExtraFunction(POPMENU_TYPE_BAN)
        elif msgid == 37:
            self.OnReport()
        elif msgid in (101, 102, 103):
            self.OnClickInfoIcon(msgid)
        elif msgid == 100:
            self.OnClickMYQIcon(msgid)
        elif msgid == 104:
            self.OnClickPlayerShowIcon(msgid)
        elif msgid == 105:
            self.OnClickSpecialIcon(msgid, FASHION_ICONID)
        elif msgid == 106:
            self.OnClickSpecialIcon(msgid, VOICE_CARD)
        elif msgid == 107:
            self.OnClickSpecialIcon(msgid, HORSE_ICONID)
        



class CRenameDialog(interface.CResizeDialog):
    
    def __init__(self, parent, pid, x, y):
        interface.CResizeDialog.__init__(self, parent, x, y, 300, 120)
        
        class CNameEdit(interface.CNormalEdit):
            
            def MsgEnter(self):
                self.GetParent().OnMessage(1)


        self.m_PID = pid
        self.m_Text = interface.CTextObject(self, '\xbd\xd0\xbf\xe9\xa4J\xb7s\xaa\xba\xb3\xc6\xb5\xf9\xa6W\xa1G', interface.FontLT14_3, interface.COLOR_268, 0)
        self.m_Text.SetPos(20, 20)
        self.m_Input = CNameEdit(self, interface.COLOR_372, interface.FontLT14_3, 20, 56, 243)
        self.m_Input.SetLimit(16)
        color = interface.COLOR_385
        width = style.GetInt('dlginfo.CRenameDialog', 'data_init_width')
        self.m_BtnOK = interface.CTextButton(self, style.GetPath('common/btn_msgbox.igs'), 111, 84, '\xbdT\xa9w', color, interface.FontLT14_3, 1, width)
        self.m_CloseBtn = interface.CTextButton(self, style.GetPath('common/btn_msgbox.igs'), 202, 84, '\xa8\xfa\xae\xf8', color, interface.FontLT14_3, 2, width)
        nickname = friend.GetFriendName2(pid)
        if nickname:
            self.m_Input.SetText(nickname)
            self.m_Input.SetSelect(0, len(nickname))
        
        self.m_Input.Active(True)

    
    def ChangeNickName(self):
        import usermacro
        import banword
        import misc
        txt = self.m_Input.GetText().strip()
        if not banword.IsValidChat(txt)[0]:
            usermacro.PROMPT_MSG('\xb3\xc6\xb5\xf9\xa6W\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby')
            return None
        
        if not banword.IsValidName(txt):
            usermacro.PROMPT_MSG('\xb3\xc6\xb5\xf9\xa6W\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb5\xfc\xbby')
            return None
        
        SPECIAL_CHAR = (' ', '~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '\\', '|', '[', '{', ']', '}', ';', ':', "'", '"', ',', '<', '.', '>', '/', '?')
        txtlist = misc.GetWordsCN(txt)
        for word in SPECIAL_CHAR:
            if word in txtlist:
                usermacro.PROMPT_MSG('\xb3\xc6\xb5\xf9\xa6W\xa4\xa4\xa5]\xa7t\xb9H\xb8T\xb2\xc5\xb8\xb9')
                return None
                continue
        
        import netfriend
        netfriend.C2SChangeName(self.m_PID, txt)
        par = self.GetParent()
        if par:
            par.m_namectl = combmacro.CRICHTEXT(interface.CRichTextObject, 'txt_name2', par, txt, interface.FontLT14_3, interface.COLOR_9)
        
        self.OnMessage(2)

    
    def OnMessage(self, msgid):
        global g_ReNamedlg
        if msgid == 1:
            self.ChangeNickName()
        elif msgid == 2:
            self.m_Input.Active(False)
            g_ReNamedlg = None
        



def ShowInfoDialog(iPlayerID, iServerID = 0, iChannel = -1, iRealID = 0):
    if iPlayerID not in g_InfoDlg:
        CInfoDialog(iPlayerID, iServerID, iChannel, iRealID)
    else:
        g_InfoDlg[iPlayerID].Topmost()
    return g_InfoDlg[iPlayerID]


def ForcedRefreshInfoDlg(pid):
    if pid in g_InfoDlg:
        CInfoDialog(pid)
    


def RefreshInfo(pid, pname, blog, IsBirthDay):
    oDlg = GetInfoDlg(pid)
    if oDlg:
        oDlg.RefreshInfo(pid)
        oDlg.ReBlog(blog, IsBirthDay)
    


def RefreshAccountBtn(pID):
    dlg = GetInfoDlg(pID)
    if dlg and dlg.IsFriendDlg():
        dlg.CheckFriendBtnValid()
    


def RefreshOldName(pid, isShow, oldNameList):
    oDlg = GetInfoDlg(pid)
    if oDlg:
        oDlg.RefreshOldName()
    


def UpdateAchieve(pid, score, paiming):
    oDlg = GetInfoDlg(pid)
    if oDlg:
        oDlg.UpdateAchieve(pid, score, paiming)
    


def ShowDeleteDlg(pid, txt):
    global g_DeleteDlg, g_DeleteDlg
    import accountfriend
    accountID = accountfriend.GetRoleAccountID(pid)
    if accountID:
        g_DeleteDlg = CDeleteMergeFrdDlg(pid, accountID, txt)
    else:
        g_DeleteDlg = CDeleteDlg(pid, txt)


class CDeleteDlg(combdialog.CCombDialog):
    
    def __init__(self, pid, txt):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/friend/delete.dlg')
        interface.Center(self)
        self.m_PID = pid
        self.m_Text = txt
        color = interface.COLOR_3
        self.m_Txt = combmacro.CTEXT(interface.CTextObject, 'text_box', self, txt, interface.FontLT14_3, color)
        self.Capture(1, 0)

    
    def CloseWindow(self):
        global g_DeleteDlg
        g_DeleteDlg = None

    
    def RightUp(self):
        self.CloseWindow()

    
    def GetSize(self):
        return self.GetObject('mainframe').GetSize()

    
    def OnMessage(self, msgid):
        if msgid == 1:
            self.CloseWindow()
        elif msgid == 2:
            if self.GetObject('btn_sel').IsSelected():
                delme = 1
            else:
                delme = 0
            import netfriend
            netfriend.C2SDelFriend(self.m_PID, delme)
            del g_InfoDlg[self.m_PID]
            self.CloseWindow()
        



class CDeleteMergeFrdDlg(combdialog.CCombDialog):
    
    def __init__(self, pid, accountID, sDelNormal):
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'dialog/friend/deletefriend.dlg')
        self.m_ID = pid
        self.m_AccountID = accountID
        self.m_DelNormalStr = sDelNormal
        interface.Center(self)

    
    def OnDelete(self):
        global g_DeleteDlg
        if self.GetObject('btn_DelNormal').IsSelected():
            g_DeleteDlg = CDeleteDlg(self.m_ID, self.m_DelNormalStr)
        elif self.GetObject('btn_DelAccount').IsSelected():
            import commondialog
            import accountfriend
            accountID = self.m_AccountID
            oAccount = accountfriend.GetAccountObj(accountID)
            if oAccount is None:
                return None
            
            msg = '\xbdT\xa9w\xadn\xa7R\xb0\xa3\xbbP#R%s#n\xaa\xba\xbe\xd4\xa4\xcd\xc3\xf6\xabY\xb6\xdc\xa1H\xc2\xf9\xa4\xe8\xb3\xa3\xb1N\xb1q\xb9\xef\xa4\xe8\xaa\xba\xbe\xd4\xb7\xf9\xa6n\xa4\xcd\xa6C\xaa\xed\xa4\xa4\xa7R\xb0\xa3\xa1C' % oAccount.GetName()
            
            def DoDelete(dlg):
                import netaccountfriend
                netaccountfriend.C2SDeleteFriend(accountID)

            commondialog.ShowMessageBox(msg, ('\xbdT\xa9w\xa7R\xb0\xa3', '\xa4\xa3\xadn\xa7R\xb0\xa3'), (DoDelete, None), stopMove = False)
            self.CloseWindow()
        

    
    def CloseWindow(self):
        global g_DeleteDlg
        g_DeleteDlg = None

    
    def OnMessage(self, msgid):
        if msgid in (1, 3):
            self.CloseWindow()
        elif msgid == 2:
            self.OnDelete()
        



class CRoleViewDialog(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, iPid):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/friend/info_zaoxing.dlg')
        self.m_oRoleView = None
        self.m_iDir = 0
        self.m_iCount = 0
        self.m_iPid = iPid
        self.m_iColorType = 0
        self.m_iColorList = []
        self.m_iFriendShape = 0
        self.InitDialog()

    
    def SetDlgShow(self, bShow):
        self.m_iCount = 0
        self.SetDirBtnShow(0)

    
    def InitDialog(self):
        for sFrameName in ('hloc_choose', 'btn_turnL', 'btn_turnR'):
            oFrame = self.GetObject(sFrameName)
            oFrame.SetEnterCB(misc.Functor(self.SetDirBtnShow, 1))
            oFrame.SetLeaveCB(misc.Functor(self.SetDirBtnShow, -1))
        

    
    def SetRoleViewInfo(self, tRoleViewInfo):
        import walker
        (iShape, dDesc) = tRoleViewInfo
        self.m_iFriendShape = oldwalkerprocess.SpecialShape(0, iShape, dDesc)
        self.m_iColorType = descinterface.IsUseColor(dDesc)
        if self.m_iColorType in (1, 2):
            self.SetShowObject('btn_copy', True)
            if self.m_iColorType == appearancedefine.SUB_PAGE_CHANGECOLOR:
                iHeroShape = hero.GetProp('m_Shape')
                dChangeDesc = charpath.ChangeDesc(iHeroShape, dDesc)
                if charpath.IsUseNewRes():
                    self.m_iColorList = dChangeDesc['color']
                else:
                    self.m_iColorList = dChangeDesc['OldHeroColor']
            else:
                self.m_iColorList = dDesc['hsvpal']
        
        oWalker = walker.CreateFakeWalker(self, -1, iShape, self.GetRoleDesc(dDesc))
        oLoc = self.GetObject('loc_zaoxing')
        oWalker.SetPos(*oLoc.GetPos())
        oWalker.SetZ(oLoc.GetZ())
        self.m_oRoleView = oWalker
        self.ChangeDir(0)

    
    def GetRoleDesc(self, dDesc):
        import descinterface
        dMyDesc = misc.DeepCopy(dDesc)
        dMyDesc = descinterface.ClearHorse(dMyDesc)
        dMyDesc = descinterface.ClearTrack(dMyDesc)
        return dMyDesc

    
    def ChangeDir(self, iDir):
        self.m_iDir = (self.m_iDir + iDir) % 8
        self.m_oRoleView.SetDirection(self.m_iDir * 4)
        oDlg = GetInfoDlg(self.m_iPid)
        if oDlg:
            oDlg.ChangeRefreshTime()
        

    
    def SetDirBtnShow(self, iChange):
        self.m_iCount += iChange
        bShow = self.m_iCount > 0
        self.SetShowObject('btn_turnL', bShow)
        self.SetShowObject('btn_turnR', bShow)
        oDlg = GetInfoDlg(self.m_iPid)
        if oDlg:
            oDlg.ChangeRefreshTime()
        

    
    def OpenAppDlg(self):
        if misc.IsInKuafuServer():
            usermacro.PROMPT_MSG('\xbc\xc8\xa4\xa3\xa4\xe4\xab\xf9\xb8\xf3\xaaA\xa8\xcf\xa5\xce')
            return None
        
        newappearancecontext.Get().OpenAppDlg(nPage = appearancedefine.MAIN_PAGE_OUTWARD, dExtendData = {
            'page': appearancedefine.SUB_PAGE_HERO,
            'extend': {
                'iShapePage': self.m_iColorType } })
        iOtherSex = self.m_iFriendShape / 100
        if self.m_iColorType == 1:
            mdappearancechangecolor.GetModel().SetImitateColor(self.m_iColorList, iOtherSex, self.m_iFriendShape)
        elif self.m_iColorType == 2:
            newmdappearancefreecolor.GetHsvPalMgr().SetImitateUnFixHSVHsvPalList(self.m_iFriendShape, self.m_iColorList, iOtherSex)
        

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.ChangeDir(-1)
        elif iMsgID == 2:
            self.ChangeDir(1)
        elif iMsgID == 4:
            clickcounter.Log('\xbc\xd2\xa5\xe9\xa6n\xa4\xcd\xacV\xa6\xe2')
            self.OpenAppDlg()
