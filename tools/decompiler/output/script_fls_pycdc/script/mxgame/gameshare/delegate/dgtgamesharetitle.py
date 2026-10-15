# pycdc 交叉复核产物 · script.fls entry 4031
# co_filename(原始)='script/mxgame/gameshare/delegate/dgtgamesharetitle.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4031.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/4/10 11:40
\xd7\xf7\xd5\xdf: gesaferoc
\xce\xc4\xbc\xfe: dgtgamesharetitle
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import C_sys
import chardefine
import delegatebase
import dlgtitle
import hero
import key
import mdappearancetittle
import mdheroshapedesc
import mdmvpnormal
import misc
import style
import usermacro
import wrapui

def GetAppearanceTittle():
    return mdappearancetittle.GetAppearanceTittle()


def GetGameShareTitleDlgMgr():
    return mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_GAME_SHARE_TITLE)


def GetRoleShowMgr():
    return mdheroshapedesc.GetRoleShapeDescMgr('CGameShareTitle')


class CGameShareTitleDgt(delegatebase.CDelegatePaginationBase):
    
    def Init(self):
        oView = self.GetView()
        self.m_LeftUpTime = 0
        self.m_iLastSelectID = 0
        self.EidtInit()
        oView.ssConnect(oView.SS_OnClickSelectTittle, self.OnClickSelectTittle)
        oGameShareTitleDlgMgr = GetGameShareTitleDlgMgr()
        oGameShareTitleDlgMgr.ssConnect('iSelectTittleID', self.OnUpdateSelectTittleID)
        self.SetRoleDesc()
        self.SetSelectInfo(None)

    
    def SetRoleDesc(self):
        oView = self.GetView()
        oRoleShowMgr = GetRoleShowMgr()
        oRoleShowMgr.SetHeroShapeDesc()
        oRoleShowMgr.AddDescKeyNotRange(chardefine.DESC.KEY_TRACK)
        oRoleShowMgr.UpdateShapeDesc()
        oView.SetNameInfo()

    
    def SetSelectInfo(self, iSelectTittleID = None):
        if iSelectTittleID is None:
            iSelectTittleID = GetGameShareTitleDlgMgr().GetMdData('iSelectTittleID', 0)
        
        dTittleInfo = GetAppearanceTittle().GetTittleInfo(iSelectTittleID)
        self.ChangeNameColor(iSelectTittleID, dTittleInfo)
        self.ShowDesc(iSelectTittleID)

    
    def ChangeNameColor(self, iTittleID = 0, dTittleInfo = None):
        oView = self.GetView()
        if not iTittleID:
            iTittleID = hero.GetProp('m_TitleID', 0)
            sTittleName = hero.GetProp('m_Title', '')
            iSelectColorNum = hero.GetProp('m_TitleColor', 0)
        else:
            sTittleName = dTittleInfo['title']
            iSelectColorNum = dTittleInfo['color']
        if iSelectColorNum < 100:
            iTittleColor = dlgtitle.GetTitleColors()[iSelectColorNum]
        else:
            iTittleColor = dlgtitle.Colors2[iSelectColorNum - 100]
        iEmoteForTitle = hero.GetProp('m_EmoteForTitle', 0)
        if iEmoteForTitle != 0 and sTittleName != '':
            sTittleName = (sTittleName, iEmoteForTitle)
        
        oView.ChangeNameColor(sTittleName, iTittleColor, iTittleID)

    
    def ShowDesc(self, iSelectTittleID = None, dDesc = ''):
        oView = self.GetView()
        if iSelectTittleID is None:
            iSelectTittleID = GetGameShareTitleDlgMgr().GetMdData('iSelectTittleID', 0)
        
        dInfo = GetAppearanceTittle().GetTittleInfo(iSelectTittleID)
        if 'sDesc' not in dInfo and iSelectTittleID in (110, 967, 968, 969, 970, 971):
            dlgtitle.C2SGetTitleDesc(iSelectTittleID)
        
        if iSelectTittleID <= 0:
            (sName, sLocDesc) = ('\xa6b\xaf\xe0\xa4O\xb9F\xa8\xec\xa4@\xa9w\xbc\xd0\xb7\xc7\xa1B\xb9F\xa6\xa8\xa4@\xa9w\xa6\xa8\xb4N\xa9\xce\xab\xd8\xa5\xdf\xa4@\xa9w\xaa\xc0\xb7|\xc3\xf6\xabY\xae\xc9\xa1A\xb7|\xc0\xf2\xb1o\xa6U\xba\xd8\xa6U\xbc\xcb\xaa\xba\xba\xd9\xbf\xd7\xa1A\xbf\xef\xa4\xa4\xa4w\xb8g\xc0\xf2\xb1o\xaa\xba\xba\xd9\xbf\xd7\xa1A\xc2I\xc0\xbb\xa1u\xa7\xf3\xa7\xef\xba\xd9\xbf\xd7\xa1v\xa5i\xa5H\xb1N\xa8\xe4\xc5\xe3\xa5\xdc\xa6b\xa8\xa4\xa6\xe2\xa6W\xa4\xa7\xa4W', '\xb5L')
        else:
            (sName, sLocDesc) = dlgtitle.GetDesc(iSelectTittleID)
        if not dDesc:
            dDesc = sLocDesc
        
        if iSelectTittleID <= 0:
            dLocDesc = '\xb5L'
        else:
            (_, dLocDesc) = dlgtitle.GetDesc(iSelectTittleID)
        if not dDesc:
            dDesc = dLocDesc
        
        \xf4\xd3\xe8m = style.GetInt('dialog/title.dlg', 'data_output')
        oView.SetDescText('\xba\xd9\xbf\xd7\xa4\xb6\xb2\xd0\xa1G#r' + sName + '#r#r\xba\xd9\xbf\xd7\xc4\xdd\xa9\xca\xa1G#s(114,%d)#r' % \xf4\xd3\xe8m + dDesc)

    
    def OnSelectLink(self):
        import copylinkobj
        import mdmvpnormal
        import dlgtitle
        import dlggetinfo
        import screenshotpublic
        iSelectID = mdmvpnormal.GetNormalMdMgr(mdmvpnormal.TYPE_GAME_SHARE_TITLE).GetMdData('iSelectTittleID')
        dTittleInfo = mdappearancetittle.GetAppearanceTittle().GetTittleInfo(iSelectID)
        if not dTittleInfo:
            return None
        
        sTitleName = dTittleInfo['title']
        info = wrapui.HandLinkFriendNickName(sTitleName)
        if info:
            (id, name, leftInfo) = info
            copylinkobj.CreateCopyLink(12, iSelectID, id, name, leftInfo, hero.g_ID)
        else:
            copylinkobj.CreateCopyLink(12, iSelectID, sTitleName, hero.g_ID)
        bGroup = wrapui.CheckGroupEdit()
        if wrapui.CheckEdit() or bGroup:
            iTitleID = iSelectID
            sName = sTitleName
            dlgtitle.ShowChatTitleInfo(iTitleID, sName)
            oDlgobj = dlggetinfo.GetSkillTip()
            (iW, iH) = oDlgobj.GetSize()
            oData = (-2000, -2000, iW, iH)
            oFunc = screenshotpublic.ScreenShotPetTips
            sFilename = oFunc(oDlgobj, oData, isgroup = bGroup)
            dlggetinfo.g_SkillTip = None
        

    
    def IsDoubleClick(self, iSelectID):
        iNow = C_sys.GetTime()
        if iNow - self.m_LeftUpTime < 3000 and self.m_iLastSelectID == iSelectID:
            self.m_iLastSelectID = iSelectID
            self.m_LeftUpTime = iNow
            return True
        
        self.m_iLastSelectID = iSelectID
        self.m_LeftUpTime = iNow
        return False

    
    def EidtInit(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_ClickFind, self.OnClickFind)

    
    def OnClickFind(self):
        LOG_DEBUG('OnClickFind')

    
    def OnClickSelectTittle(self, iSelectID):
        GetGameShareTitleDlgMgr().SetMdData('iSelectTittleID', iSelectID)
        if C_sys.IsKeyDown(key.VK_SHIFT):
            self.OnSelectLink()
        elif self.IsDoubleClick(iSelectID):
            self.OnSelectLink()
        

    
    def OnUpdateSelectTittleID(self, dInfo):
        self.SetSelectInfo(dInfo['iSelectTittleID'])



class CGameShareTitleList(delegatebase.CDelegateBase):
    
    def Init(self):
        oView = self.GetView()
        oView.ssConnect(oView.SS_OnEditChange, self.OnEditChange)
        oAppearanceTittle = GetAppearanceTittle()
        oAppearanceTittle.ssConnect(oAppearanceTittle.SS_UpdateAllTittleInfo, self.OnUpdateAllTittleInfo)
        oGameShareTitleDlgMgr = GetGameShareTitleDlgMgr()
        oGameShareTitleDlgMgr.ssConnect('iSelectTittleID', self.OnUpdateSelectTittleID)
        dlgtitle.C2SOpenTitle()
        self.UpdateTableView()
        self.AutoSelectTitle()

    
    def OnSearch(self):
        oView = self.GetView()
        oSearchEdit = oView.GetEdit()
        oSearchEdit.CloseList()
        sTxt = oSearchEdit.GetText()
        oAppearanceTittle = GetAppearanceTittle()
        oDictList = misc.DeepCopy(oAppearanceTittle.GetAllTittleInfo())
        bHave = False
        iSelectID = GetGameShareTitleDlgMgr().GetMdData('iSelectTittleID', 0)
        for iPos, dInfoData in enumerate(oDictList):
            (sResult, _, _) = wrapui.HandleLink(dInfoData['title'])
            if sResult == sTxt:
                bHave = True
                iSelectID = dInfoData['titleId']
                continue
        
        if bHave:
            GetGameShareTitleDlgMgr().SetMdData('iSelectTittleID', iSelectID)
            self.AutoSelectTitle()
        else:
            usermacro.PROMPT_MSG('\xbc\xc8\xa5\xbc\xc0\xf2\xb1o\xb8\xd3\xba\xd9\xbf\xd7')

    
    def AutoSelectTitle(self):
        oTableView = self.GetView().GetTbAllView()
        dInfoList = oTableView.GetDataSource()
        for iPos, dInfoData in enumerate(dInfoList):
            if dInfoData['SETSELETSS']:
                oTableView.Reload(iPos / 2)
                return None
                continue
        

    
    def IsUseTittle(self, iTittleID):
        hero = None
        if hero.GetProp('m_TitleID', 0) == iTittleID:
            return True
        
        return False

    
    def GetSelectType(self, iTitleID):
        return iTitleID == GetGameShareTitleDlgMgr().GetMdData('iSelectTittleID', 0)

    
    def UpdateTableView(self):
        oTableView = self.GetView().GetTbAllView()
        oAppearanceTittle = GetAppearanceTittle()
        oDictList = misc.DeepCopy(oAppearanceTittle.GetAllTittleInfo())
        oDictList.sort(mdappearancetittle.CmpTittle)
        dInfoList = []
        for iPos, dInfoData in enumerate(oDictList):
            iTitleID = dInfoData['titleId']
            dInfoData['SETSELETSS'] = self.GetSelectType(iTitleID)
            dInfoData['bNowUse'] = self.IsUseTittle(iTitleID)
            dInfoList.append(dInfoData)
        
        oTableView.SetDataSource(dInfoList)
        oTableView.Reload()

    
    def OnEditChange(self):
        self.OnSearch()

    
    def OnUpdateAllTittleInfo(self, dTittleList):
        self.UpdateTableView()

    
    def OnUpdateSelectTittleID(self, iSelectTittleID):
        self.UpdateTableView()
