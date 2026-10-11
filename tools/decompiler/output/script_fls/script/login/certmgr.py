# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\certmgr.py
import cert
g_NeedAskHasBindPhone = True
g_BindPhone = ''
g_LimitApply = False
g_BindAddress = ''
g_HasInitCert = False
g_IsCertUser = False
g_IsCertRight = False
g_CertLeft = 0
g_IsShowCert = False
g_IsCertLogin = False
g_SendMsgMode = 1
g_LastValKey = None
g_BindPhoneCallBack = None

def ModuleReset():
    global g_BindAddress
    global g_BindPhone
    global g_BindPhoneCallBack
    global g_CertLeft
    global g_HasInitCert
    global g_IsCertLogin
    global g_IsCertRight
    global g_IsCertUser
    global g_IsShowCert
    global g_LastValKey
    global g_LimitApply
    global g_NeedAskHasBindPhone
    global g_SendMsgMode
    g_NeedAskHasBindPhone = True
    g_BindPhone = ''
    g_LimitApply = False
    g_BindAddress = ''
    g_HasInitCert = False
    g_IsCertUser = False
    g_IsCertRight = False
    g_CertLeft = 0
    g_IsShowCert = False
    g_IsCertLogin = False
    g_SendMsgMode = 1
    g_LastValKey = None
    g_BindPhoneCallBack = None
    return


def SetIsShowCert(isShowCert):
    global g_IsShowCert
    g_IsShowCert = isShowCert
    import selectrole
    selectrole.RefreshCertUser()
    return


def GetIsShowCert():
    return g_IsShowCert


def SetIsCertLogin(isCertLogin):
    global g_IsCertLogin
    g_IsCertLogin = isCertLogin
    import selectrole
    selectrole.RefreshCertUser()
    return


def GetIsCertLogin():
    return g_IsCertLogin


def IsCertUser():
    return g_IsCertUser


def SetCertUser(v):
    global g_IsCertUser
    g_IsCertUser = v
    import selectrole
    selectrole.RefreshCertUser()
    return


def StepupCert(username, verifycode):
    global g_HasInitCert
    global g_IsCertRight
    global g_LimitApply
    import netcert, commondialog
    g_LimitApply = 0
    if not g_HasInitCert:
        res = cert.CertInitialize()
        if res < 0 and res != -8:
            return
        g_HasInitCert = True
    address = GetBindAddress()
    res = cert.CertInstall(username, address, verifycode)
    if res >= 0:
        pcinfo = cert.GetPCInfo()
        netcert.C2SSetupRes(1, address, pcinfo)
        SetCertUser(True)
        showTxt = '恭喜！您的証書已成功安裝。'
        commondialog.ShowNewMessageBox(showTxt, ('確定', ))
        g_IsCertRight = True
    else:
        netcert.C2SSetupRes(0)
        SetCertUser(False)
        errorMsg = cert.CERTERRORMSG.get(res, '未知錯誤%d' % res)
        showTxt = '安裝証書失敗，請重新安裝。（%s）' % errorMsg
        commondialog.ShowNewMessageBox(showTxt, ('確定', ))
    return


def GetNeedAskHasBindPhone():
    return g_NeedAskHasBindPhone


def SetBindPhone(phone):
    global g_BindPhone
    global g_BindPhoneCallBack
    global g_NeedAskHasBindPhone
    g_NeedAskHasBindPhone = False
    g_BindPhone = phone
    if g_BindPhoneCallBack:
        g_BindPhoneCallBack()
    g_BindPhoneCallBack = None
    import dlgcertcancel
    dlgcertcancel.RefreshPhoneNumber()
    return


def GetBindPhone():
    return g_BindPhone


def SetBindAddress(addr):
    global g_BindAddress
    g_BindAddress = addr
    return


def GetBindAddress():
    return g_BindAddress


def SetSendMsgMode(iMode):
    global g_SendMsgMode
    g_SendMsgMode = iMode
    return


def GetSendMsgMode():
    return g_SendMsgMode


def ShowNeedCert(leftCnt=0):
    import dlgnpc
    txt = '您在本台電腦沒有安裝証書，無法進入遊戲。請立即申請証書。是否現在申請？（剩餘証書%d個）\nQ我要申請証書進入遊戲\nQ暫時不申請' % leftCnt

    def ApplyCert(msgid):
        import netcert
        if msgid == 1:
            netcert.C2SApplyCert()
        elif msgid == 2:
            netcert.C2SCancle()
        return

    dlgnpc.ShowClientDlg(txt, '', ApplyCert)
    return


def TryDelCert(focusPCInfo, sAccount):
    import netlogin
    myPCInfo = cert.GetPCInfo()
    if sAccount == '':
        sAccount = netlogin.GetCurrAccount()
    if myPCInfo == focusPCInfo:
        print '~~~~~~~~~~嘗試刪除証書', sAccount
        cert.CertUninstall(sAccount)
    return


def Show2980Tips():
    import net, gameurl, dlgnpc

    def done(msgid):
        if msgid == 1:
            net.OpenUrl(gameurl.MAIN2980_URL)
        return

    txt = '2980用戶可以登錄郵箱更換本帳號已綁定的手機號碼（設置→帳戶→修改手機號碼）\nQ登錄2980郵箱\nQ暫不處理\n'
    dlgnpc.ShowClientDlg(txt, '', done)
    return


def NotifySendMsg(sValKey, sPhone, sTarget):
    global g_LastValKey
    import netcert, commondialog
    g_LastValKey = sValKey
    tmp = '#r您的驗証碼是#Y%s#n，請使用手機號（%s****%s）編輯短信#Y%s#n發送到#Y%s#n上。發送短信後請等待30秒，然後點擊下面的「短信已發送」選項。'
    tmpTuple = (sValKey, sPhone[:3], sPhone[-4:], sValKey, sTarget)
    showTxt = tmp % tmpTuple

    def cbFunc(dlg):
        netcert.C2SQuerySendState(sValKey)
        return

    commondialog.ShowNewMessageBox(showTxt, ('短信已發送', ), (cbFunc,))
    return


def ShowVoiceCodeTips():
    import dlgnpc
    txt = '語音驗証碼已成功發送，請耐心等待手機來電。'
    dlgnpc.ShowClientDlg(txt, '', None)
    return


def CheckCodeAns(iType):
    global g_LastValKey
    import commondialog, dlgcertapply, dlgcertcancel, dlgcertman
    if iType == 0:
        showTxt = '網絡可能有延遲，請稍等片刻'
        commondialog.ShowNewMessageBox(showTxt, ('確定', ), (None, ))
    elif iType == 1:
        dlgcertapply.SetCheckCode(g_LastValKey)
        dlgcertcancel.SetCheckCode(g_LastValKey)
        dlgcertman.SetCheckCode(g_LastValKey)
        g_LastValKey = ''
    elif iType == 2:
        showTxt = '驗証碼發送錯誤或者已超時，請重新發送'
        commondialog.ShowNewMessageBox(showTxt, ('確定', ), (None, ))
    return


return
