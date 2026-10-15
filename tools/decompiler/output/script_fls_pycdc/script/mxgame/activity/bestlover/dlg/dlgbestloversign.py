# pycdc 交叉复核产物 · script.fls entry 1787
# co_filename(原始)='script/mxgame/activity/bestlover/dlg/dlgbestloversign.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1787.pyc (Python 2.5)

import avatar
import banword
import combdialog
import combmacro
import hero
import interface
import netbestlover
import usermacro

class CBestLoverSignDlg(combdialog.CCombDialog):
    sUIName = 'dialog4/activity/bestlovers/bestlovers_enroll.dlg'
    
    def __init__(self, oParent, dInfo):
        combdialog.CCombDialog.__init__(self, oParent)
        self.m_oEditLst = { }
        self.m_iLeaderID = dInfo[0]['iPlayerID']
        self.m_iMerberID = dInfo[1]['iPlayerID']
        self.InitEdit()
        self.SetPlayerInfo(dInfo)
        self.InitBtnsShow()

    
    def InitBtnsShow(self):
        self.SetShowObject('btn_enroll', self.IsLeader())
        self.SetShowObject('loc_memeber', False)

    
    def IsLeader(self):
        GetRealID = hero.GetRealID()
        return self.m_iLeaderID

    
    def InitEdit(self):
        dEdit2Tips = {
            'txt_combinename': ('\xbf\xe9\xa4J\xa6W\xa6r', combmacro.CEDIT, interface.CEdit, 14),
            'txt_declaration': ('\xbf\xe9\xa4J\xab\xc5\xa8\xa5', combmacro.CMLEDIT, interface.CMultilineEdit, 52) }
        bLeader = self.IsLeader()
        for sTips, oCreateFunc, oClass, iLimitNum in dEdit2Tips.iteritems():
            oLocText = self.GetObject(sUIName)
            oEdit = oCreateFunc(oClass, sUIName, self, oLocText.GetColor(), interface.FontLT14_3, 0, 0)
            if bLeader:
                sTips = sTips
            else:
                sTips = '\xbd\xd0\xb5\xa5\xab\xdd\xb6\xa4\xaa\xf8\xbds\xbf\xe8\xb3\xf8\xa6W\xabH\xae\xa7'
            oEdit.SetLimit(iLimitNum)
            oEdit.SetDefaultTips(sTips, color = oLocText.GetColor())
            if bLeader:
                pass
            oEdit.Active(sUIName == 'txt_combinename')
            oEdit.Enable(bLeader)
            self.m_oEditLst[sUIName] = oEdit
        
        self.m_oEditLst['txt_declaration'].SetLineLimit(2)

    
    def RefreshInfo(self, dInfo):
        '''
\t\t:param dInfo:sDeclaration, sTeamName
\t\t:return:
\t\t'''
        dKey2Text = {
            'sDeclaration': 'txt_declaration',
            'sTeamName': 'txt_combinename' }
        for sKey, sTextName in dKey2Text.iteritems():
            self.m_oEditLst[sTextName].SetText(dInfo[sKey])
        
        self.SetShowObject('loc_memeber', True)

    
    def SetPlayerInfo(self, dDetailLst):
        self.m_oAvatarLst = []
        for index, dDetail in enumerate(dDetailLst):
            lstPhoto = avatar.TransPhotoInt(*dDetail['lstPhoto'])
            lstPhoto = avatar.Int2PhotoArr(*lstPhoto)
            oAvatarImg = avatar.GetCreateBigAvatarImg(self.GetObject('img_photo%d' % (index + 1)), lstPhoto, dDetail['iPlayerID'])
            self.m_oAvatarLst.append(oAvatarImg)
            self.GetObject('txt_name%d' % (index + 1)).SetText(dDetail['sPlayerName'])
        

    
    def OnBtnJoinClick(self):
        dText2Type = {
            'txt_combinename': '\xb1\xa1\xabQ\xb2\xd5\xa6X\xa6W',
            'txt_declaration': '\xc4v\xbf\xef\xab\xc5\xa8\xa5' }
        lstText = []
        for sUIName, sType in dText2Type.iteritems():
            sEditText = self.m_oEditLst[sUIName].GetText()
            if not sEditText:
                usermacro.PROMPT_MSG('%s\xc1\xd9\xa5\xbc\xb6\xf1\xbcg' % sType)
                return None
            
            if not banword.IsValidOnIntrodruce(sEditText):
                usermacro.PROMPT_MSG('%s\xa6s\xa6b\xab\xcc\xbd\xaa\xa6r\xa1A\xbd\xd0\xad\xab\xb7s\xbf\xe9\xa4J' % sType)
                return None
            
            lstText.append(sEditText)
        
        netbestlover.C2GSConfirmSignUp(self.m_iLeaderID, self.m_iMerberID, lstText[0], lstText[1])

    
    def CloseWindow(self):
        netbestlover.C2GSRefuseJoin(self.m_iLeaderID)
        self.CloseUI()

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.CloseWindow()
        elif iMsgID == 7:
            netbestlover.C2GSConfirmSign(self.m_iLeaderID)
        elif iMsgID == 8:
            netbestlover.C2GSRequestFix(self.m_iLeaderID)
        elif iMsgID == 6:
            self.OnBtnJoinClick()
