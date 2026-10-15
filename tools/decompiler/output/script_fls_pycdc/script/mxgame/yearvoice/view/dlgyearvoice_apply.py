# pycdc 交叉复核产物 · script.fls entry 158
# co_filename(原始)='script/mxgame/yearvoice/view/dlgyearvoice_apply.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_158.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/8/12 19:28
\xd7\xf7\xd5\xdf: wz
\xce\xc4\xbc\xfe: dlgyearvoice_apply
\xbd\xe9\xc9\xdc\xa3\xba
================================================================================
'''
import combdialog
import interface
import slot
import pagedlgbase
import dgtyearvoice_apply
import misc
import yearvoice_define
AUDIO_SHOWPROP = ('bHasVoice', 'sTime', 'iRate', 'sAudioTips', 'bShowVoiceAni')
AUDIOPART_CONFIG = {
    'spr_play': {
        'sPropKey': 'bShowVoiceAni',
        'sCondition': True,
        'sType': 'show' },
    'btn_Play': {
        'sPropKey': 'bHasVoice',
        'sCondition': True,
        'sType': 'show' },
    'btn_audio': {
        'sPropKey': 'bHasVoice',
        'sCondition': False,
        'sType': 'show' },
    'txt_audio_sec': {
        'sPropKey': 'sTime',
        'sType': 'text' },
    'progress_audio': {
        'sPropKey': 'iRate',
        'sType': 'progress' },
    'text_audiotips': {
        'sPropKey': 'sAudioTips',
        'sType': 'text' } }
BTN_SHOW_PROP = ('bHasVoice', 'bPlay', 'sRecordState')
BTN2_CONFIG = {
    'btn_upvoice': {
        'sPropKey': 'bBaoMing',
        False: (19, '\xa4W\xb6\xc7\xad\xb5\xc0W'),
        True: (5, '\xb3\xf8\xa6W\xb0\xd1\xc1\xc9') },
    'btn_recording': {
        'sPropKey': 'sRecordState',
        'record': (8, '\xb6}\xa9l\xbf\xfd\xbbs'),
        'rerecord': (18, '\xad\xab\xb7s\xbf\xfd\xbbs'),
        'stoprecord': (28, '\xb0\xb1\xa4\xee\xbf\xfd\xbbs') },
    'btn_audition': {
        'sPropKey': 'bPlay',
        False: (4, '\xb8\xd5\xc5\xa5\xad\xb5\xc0W'),
        True: (14, '\xbc\xc8\xb0\xb1\xad\xb5\xc0W') } }

class CYearVoiceApplyDlg(combdialog.CCombSubWnd, slot.ISignalSubject, pagedlgbase.COnePageDlgBase):
    SS_CloseDlg = 'SS_CloseDlg()'
    SS_OpenDlg = 'SS_OpenDlg()'
    SS_StartRecord = 'SS_StartRecord()'
    SS_ReRecord = 'SS_ReRecord()'
    SS_StopRecord = 'SS_StopRecord()'
    SS_BaoMing = 'SS_LocalBaoMing()'
    SS_PlayVoice = 'SS_PlayVoice()'
    SS_StopPlayVoice = 'SS_StopPlayVoice()'
    SS_DelVoice = 'SS_DelVoice()'
    SS_Send2Server = 'SS_Send2Server()'
    SS_OpenChangeNameDlg = 'SS_OpenChangeNameDlg()'
    SS_ChangePhoto = 'SS_ChangePhoto()'
    SS_Clear = 'SS_Clear()'
    SS_InitPhoto = 'SS_InitPhoto(sPath)'
    SS_ShowRule = 'SS_ShowRule()'
    
    def __init__(self, oParent):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog4/yearvoice/enroll.dlg')
        pagedlgbase.COnePageDlgBase.__init__(self)
        del ssInit
        self()
        self.m_oEditText = None
        self.m_sOri = ''
        self.m_oPhoto = None
        self.m_oParent = oParent
        self.m_oDelegate = None
        self.m_oCloseCallBack = None
        self.m_DelegateList = []
        self.SetIgnoreEsc(True)
        self.InitDlg()
        self.InitDelegate()

    
    def InitDlg(self):
        self.m_oEditText = self.GetObject('rtxt_name')
        self.m_sOri = self.m_oEditText.GetText()
        self.SetTime()

    
    def SetCloseCallBack(self, oCloseCallBack):
        self.m_oCloseCallBack = misc.Functor(oCloseCallBack)

    
    def InitDelegate(self):
        self.m_DelegateList = [
            dgtyearvoice_apply.CYearVoiceApplyDelegate(self)]

    
    def VOpen(self):
        self.ssEmit(self.SS_OpenDlg)

    
    def VOpenPage(self, dExtend = None):
        self.SetShow(True)

    
    def VClose(self):
        self.SetShow(False)

    
    def GetSingName(self):
        \xbc\x81\xaeme = self.m_oEditText.GetText()
        if \xbc\x81\xaeme == self.m_sOri:
            return ''
        else:
            return \xbc\x81\xaeme

    
    def CloseDlg(self):
        if self.m_oCloseCallBack:
            self.m_oCloseCallBack()
        

    
    def GetBgZ(self):
        return self.GetObject('img_changpianbg').GetZ()

    
    def InitPhoto(self, sPath):
        self.m_oPhoto = interface.CBitmapObject(self, sPath, interface.UIPath)
        (ix, iy) = self.GetObject('loc_voicephoto').GetPos()
        self.m_oPhoto.SetPos(ix, iy)
        self.m_oPhoto.SetZ(self.GetBgZ() - 1)

    
    def SetSingName(self, \xbc\x81\xaeme):
        self.m_oEditText.SetText(\xbc\x81\xaeme)

    
    def SetTime(self):
        sTime = yearvoice_define.GetBaoMingDate()
        self.GetObject('text_deline').SetText(sTime)

    
    def RefreshBtn(self, dData):
        for sUIName, dConfig in BTN2_CONFIG.iteritems():
            sPropKey = dConfig['sPropKey']
            oValue = dData[sPropKey]
            (iMsgID, sBtnName) = dConfig[oValue]
            oBtn = self.GetObject(sUIName)
            oBtn.SetText(sBtnName)
            oBtn.m_MsgID = iMsgID
        
        bBaoMing = dData['bBaoMing']
        self.RefreshBaoMingUITitle(bBaoMing)

    
    def RefreshBaoMingUITitle(self, bBaoMing):
        sTittle = None if bBaoMing else '\xb3\xf8\xa6W\xb0\xd1\xc1\xc9'
        self.GetObject('btn_upvoice').SetText(sTittle)

    
    def RefreshVoice(self, dData, bPart = False):
        for sUIName, dConfig in AUDIOPART_CONFIG.iteritems():
            sPropKey = dConfig['sPropKey']
            sType = dConfig['sType']
            if sPropKey not in dData and bPart:
                continue
            
            if sType == 'show':
                oCondition = dConfig['sCondition']
                oValue = dData.get(sPropKey, False)
                bShow = oValue == oCondition
                self.SetShowObject(sUIName, bShow)
                continue
            if sType == 'text':
                sText = dData.get(sPropKey, '')
                bShow = None if sText else False
                self.SetShowObject(sUIName, bShow)
                oTextObj = self.GetObject(sUIName)
                oTextObj.SetText(sText)
                continue
            if sType == 'progress':
                iRate = dData[sPropKey]
                oProgress = self.GetObject(sUIName)
                oProgress.SetRate(iRate)
                continue
        

    
    def ChangePhoto(self, sPath):
        if sPath in yearvoice_define.DPHOTO:
            self.m_oPhoto = interface.CBitmapObject(self, sPath, interface.UIPath)
        else:
            self.m_oPhoto = interface.CBitmapObject(self, sPath)
        (ix, iy) = self.GetObject('loc_voicephoto').GetPos()
        self.m_oPhoto.SetPos(ix, iy)
        self.m_oPhoto.SetZ(self.GetBgZ() - 1)

    
    def SetNameText(self, sNameText):
        self.GetObject('rtxt_name').SetText(str(sNameText))

    
    def OnEditMessage(self, iMsgID):
        if iMsgID == 1:
            self.ssEmit(self.SS_StartRecord)
        elif iMsgID == 2:
            self.ssEmit(self.SS_DelVoice)
        elif iMsgID == 3:
            self.ssEmit(self.SS_PlayVoice)
        elif iMsgID == 4:
            self.ssEmit(self.SS_PlayVoice)
        elif iMsgID == 5:
            self.ssEmit(self.SS_Send2Server)
        elif iMsgID == 6:
            self.ssEmit(self.SS_OpenChangeNameDlg)
        elif iMsgID == 7:
            self.ssEmit(self.SS_ChangePhoto)
        elif iMsgID == 8:
            self.ssEmit(self.SS_StartRecord)
        elif iMsgID == 9:
            self.ssEmit(self.SS_ShowRule)
        elif iMsgID == 14:
            self.ssEmit(self.SS_StopPlayVoice)
        elif iMsgID == 18:
            self.ssEmit(self.SS_ReRecord)
        elif iMsgID == 19:
            self.ssEmit(self.SS_BaoMing)
        elif iMsgID == 28:
            self.ssEmit(self.SS_StopRecord)
        

    
    def OnMessage(self, iMsgID):
        self.OnEditMessage(iMsgID)
