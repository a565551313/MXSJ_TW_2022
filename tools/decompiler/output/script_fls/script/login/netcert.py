# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\netcert.py
import net, cert, certmgr

def S2CInstandCert(netobj):
    sCode = netobj.UnpackString(32)
    sUserName = netobj.UnpackString(0)
    certmgr.StepupCert(sUserName, sCode)
    return


def S2CCheckCert(netobj):
    isCertLogin = netobj.UnpackInt(1)
    certmgr.SetIsCertLogin(isCertLogin)
    return


def S2CMobileCheck(netobj):
    iResult = netobj.UnpackInt(1)
    if iResult == 0:
        iReason = netobj.UnpackInt(1)
        resDct = {1: '驗証碼驗証錯誤', 2: '驗証碼驗証還沒結果，請等待', 3: '驗証碼驗証超時', 4: '驗証碼失敗，因為綁定手機達到上限'}
        res = resDct.get(iReason, '申請綁定手機失敗(-%d)' % iReason)
        if res:
            import usermacro
            usermacro.PROMPT_MSG(res)
    else:
        import usermacro
        usermacro.PROMPT_MSG('申請綁定手機成功')
    return


def S2CShowCertApply(netobj):
    sPhone = netobj.UnpackString(11)
    certmgr.SetBindPhone(sPhone)
    import dlgcertapply
    dlgcertapply.Show(sPhone)
    return


def S2CShowCertAbout(netobj):
    import dlgcertabout
    dlgcertabout.Show()
    return


def S2CShowCertMange(netobj):
    import dlgcertman
    dlgcertman.Show()
    return


def S2CShowCertLook(netobj):
    import dlgcertlook
    dlgcertlook.Show()
    import dlgcertman
    if dlgcertman.g_CertMan:
        dlgcertman.g_CertMan.CloseWindow()
    return


def S2CCertItemData(netobj):
    certItem = []
    iPage = netobj.UnpackInt(1)
    iHasNext = netobj.UnpackInt(1)
    iLen = netobj.UnpackInt(1)
    for i in range(iLen):
        iTmpLen = netobj.UnpackInt(2)
        sCertID = netobj.UnpackString(iTmpLen)
        iTmpLen = netobj.UnpackInt(2)
        sCertName = netobj.UnpackString(iTmpLen)
        iTmpLen = netobj.UnpackInt(2)
        sCertMac = netobj.UnpackString(iTmpLen)
        iTmpLen = netobj.UnpackInt(2)
        iBindTime = netobj.UnpackString(iTmpLen)
        tmpDict = {}
        tmpDict['CertID'] = sCertID
        tmpDict['Address'] = sCertName
        tmpDict['Mac'] = sCertMac
        tmpDict['Time'] = iBindTime
        certItem.append(tmpDict)

    import dlgcertlook
    dlgcertlook.RefreshData(certItem, iPage, iHasNext)
    return


def S2CNotDYT(netobj):

    def f1(dlg):
        C2SWantDYT()
        return

    def f2(dlg):
        C2SCancle()
        return

    import commondialog
    msg = '尊敬的玩家：#r    您的賬號並非多益通賬號，只有多益通賬號才可申請安全証書，現在是否要將其升級成多益通賬號？'
    commondialog.ShowMessageBox(msg, ('升級', '取消'), (f1, f2))
    return


def S2CCertAns(netobj):
    isOK = netobj.UnpackInt(1)
    iLeftNum = netobj.UnpackInt(1)
    certmgr.g_IsCertRight = isOK
    if certmgr.g_CertLeft != iLeftNum:
        certmgr.g_CertLeft = iLeftNum
    print '這個客戶端是否驗証証書成功', isOK
    if certmgr.IsCertUser() and not certmgr.g_IsCertRight:
        certmgr.ShowNeedCert(certmgr.g_CertLeft)
    if not isOK:
        len = netobj.UnpackInt(1)
        reason = netobj.UnpackString(len)
        reasonDict = {'ok': '解密簽名串成功且結果與32位驗証碼相等', 
           'misspcinfo': '缺少pcinfo（客戶端錯誤碼153）', 
           'missvalcode': '缺少驗証碼', 
           'misssign': '缺少簽名串', 
           'notfoundcert': '根據pcinfo找不到對應的cert數據', 
           'certformaterror': 'cert格式錯誤', 
           'valerror': '驗証失敗（可以理解為數據中心從cert獲取的公鑰和客戶端的私鑰不匹配）'}
        reasonSting = reasonDict.get(reason, '未知原因')
        print '這個客戶端驗証証書失敗 !!!!', reason, reasonSting
    import gamectrl
    if gamectrl.IsSkipCert():
        C2SPasscheckCert()
    import netserver
    print '這個客戶端是否驗証証書成功', isOK
    if certmgr.IsCertUser() and not certmgr.g_IsCertRight:
        certmgr.ShowNeedCert(certmgr.g_CertLeft)
        if hasattr(net.g_Net, 'm_ServerInfo') and not netserver.IsSelectServerOver():
            (field, name, ip, port, serverid) = net.g_Net.m_ServerInfo
            netserver.TransferServer(field, name, ip, port, serverid, autoenterselrole=True)
            return
    return


def S2CApplyCert(netobj):
    import dlgcertapplymenu
    dlgcertapplymenu.Show()
    return


def S2CGHasSendSMS(netobj):
    txt = '已經向手機發送驗証碼，請查收'
    import usermacro
    usermacro.PROMPT_MSG(txt)
    return


def S2CBindPhone(netobj):
    import usermacro
    usermacro.PROMPT_MSG('請先進入遊戲綁定手機，才能安裝証書')
    return


def S2CBindAns(netobj):
    import usermacro
    usermacro.PROMPT_MSG('您輸入的驗証碼已經過時，請重新獲取')
    return


def S2CApplyTooMuch(netobj):
    txt = '您今日已成功申請三次証書，今日已無法再次申請。'
    import usermacro
    usermacro.PROMPT_MSG(txt)
    return


def S2CSendCodeResult(netobj):
    import usermacro
    sub = netobj.UnpackInt(1)
    if sub == 1:
        result = netobj.UnpackInt(1)
        ilen = netobj.UnpackInt(1)
        if ilen <= 0:
            mail = ''
        else:
            mail = netobj.UnpackString(ilen)
        if result:
            usermacro.PROMPT_MSG('換綁授權碼已經發送至您的郵箱，請查收')
        else:
            usermacro.PROMPT_MSG('換綁授權碼無法發送至您的郵箱%s，請檢查郵箱狀態或聯繫管理員' % mail)
    elif sub == 2:
        result = netobj.UnpackInt(1)
        if result:
            usermacro.PROMPT_MSG('申請已提交，經過30天的確認期後即可成功更換手機。')
            import dlgcertcancel
            dlgcertcancel.CloseChangePhone()
        else:
            usermacro.PROMPT_MSG('修改綁定手機失敗')
    elif sub == 3:
        pass
    elif sub == 5:
        isIn = netobj.UnpackInt(1)
        print '是否處於手機換綁確認期', isIn
        if isIn == 1:
            sPhone = netobj.UnpackString(11)
            iStTime = netobj.UnpackInt(4)
            iDoTime = netobj.UnpackInt(4)
        else:
            iDoTime = 0
        import dlgcertcancel
        dlgcertcancel.SetChangeBindTime(iDoTime)
    return


def S2CCertMaxNum(netobj):
    msg = '証書數量達到上限30個，請通過「管理証書」注銷其它設備上的証書'
    import usermacro
    usermacro.PROMPT_MSG(msg)
    return


def S2CNeedSelectCert(netobj):
    msg = '你的賬號已申請安全証書，請在「証書相關」中選擇証書'
    import usermacro
    usermacro.PROMPT_MSG(msg)
    return


def S2CCertSucced(netobj):
    msg = '恭喜！驗証通過，您可以對本多益通賬號的証書進行管理。'
    import usermacro
    usermacro.PROMPT_MSG(msg)
    return


def S2CCancelCertAns(netobj):
    import usermacro
    iResult = netobj.UnpackInt(1)
    curPCInfo = ''
    sAccount = ''
    iCert'eft = 0
    if iResult:
        showTxt = '您賬號申請的証書服務已註銷。'
        curPCInfo = netobj.UnpackString(32)
        iLen = netobj.UnpackInt(1)
        sAccount = netobj.UnpackString(iLen)
        iCert'eft = netobj.UnpackInt(1)
    else:
        showTxt = '您賬號申請証書服務註銷失敗。'
    (
     sAccount, iCert'eft)
    import commondialog
    commondialog.ShowMessageBox(showTxt, ('確定', ))
    if curPCInfo:
        certmgr.TryDelCert(curPCInfo, sAccount)
    return


def S2CSecurityCodeTooFast(netobj):
    msg = '您嘗試獲取驗証碼操作過於頻繁，請稍候再嘗試'
    import usermacro
    usermacro.PROMPT_MSG(msg)
    return


def S2CInstallCertSucced(netobj):
    global g_IsCertRight
    g_IsCertRight = True
    showTxt = '恭喜！您的証書已成功安裝。'
    import commondialog
    commondialog.ShowMessageBox(showTxt, ('確定', ))
    import dlgcertapply
    if dlgcertapply.g_CertApplyDlg:
        dlgcertapply.g_CertApplyDlg.CloseWindow()
    return


def S2CSecurityCodeSucced(netobj):
    sPhone = netobj.UnpackString(11)
    showTxt = '已經向手機%s %s %s發送驗証碼，請查收' % (sPhone[:3], sPhone[3:7], sPhone[7:])
    import commondialog
    commondialog.ShowMessageBox(showTxt, ('確定', ))
    return


def S2CIsCertUser(netobj):
    isCertUser = netobj.UnpackInt(1)
    certmgr.SetCertUser(isCertUser)
    import gamectrl
    if gamectrl.IsSkipCert():
        C2SPasscheckCert()
    return


def S2CInDYTUpdateTime(netobj):
    msg = '多益通賬號正處於升級確認期，請耐心等待'
    import usermacro
    usermacro.PROMPT_MSG(msg)
    return


def S2CSecurityCodeFail(netobj):
    msg = '您輸入的驗証碼有誤，請重新輸入'
    import usermacro
    usermacro.PROMPT_MSG(msg)
    return


def S2CCloseCertAns(netobj):
    iType = netobj.UnpackInt(1)
    import usermacro
    if iType == 1:
        usermacro.PROMPT_MSG('授權碼已經發送至您的郵箱，請查收')
    elif iType == 2:
        iRes = netobj.UnpackInt(1)
        if iRes:
            showTxt = '您已經停用了証書功能'
            import dlgcertcancel
            dlgcertcancel.ShowMailCode(False)
        else:
            showTxt = '授權碼錯誤'
        usermacro.PROMPT_MSG(showTxt)
    elif iType == 3:
        iRes = netobj.UnpackInt(1)
        lenMail = netobj.UnpackInt(1)
        if lenMail <= 0:
            sMail = ''
        else:
            sMail = netobj.UnpackString(lenMail)
        if iRes:
            pass
        elif sMail:
            sMail = '（%s）' % sMail
        showTxt = '關閉証書授權碼無法發送至您的郵箱%s，請檢查郵箱狀態或聯繫管理員' % sMail
        usermacro.PROMPT_MSG(showTxt)
    return


def S2CHeroPhone(netobj):
    sPhone = netobj.UnpackString(11)
    certmgr.SetBindPhone(sPhone)
    return


def S2CAccoutRelation(netobj):
    import netlogin, cert, pubdlggetpass
    iLen = netobj.UnpackInt(1)
    sEmail = netobj.UnpackString(iLen)
    iLen = netobj.UnpackInt(1)
    sMobile = netobj.UnpackString(iLen)
    curaccount = netlogin.g_CurrAccount
    accountlist = []
    if pubdlggetpass.IsPhoneAccount(curaccount):
        if curaccount.find('@') >= 0:
            newaccount = curaccount[:-9]
        else:
            newaccount = curaccount + '@2980.com'
        accountlist.append(newaccount)
        accountlist.append(sEmail)
        newaccount = sEmail
    else:
        accountlist.append(sMobile)
        accountlist.append(sMobile[:-9])
        newaccount = sMobile
    certmgr.g_IsCertRight = False
    print 'S2CAccoutRelation', sEmail, sMobile, netlogin.g_CurrAccount
    C2STryOtherAccout(accountlist)
    return


CRTT_FUNC_LIST = {1: S2CInstandCert, 
   2: S2CCheckCert, 
   3: S2CMobileCheck, 
   4: S2CShowCertApply, 
   5: S2CShowCertAbout, 
   6: S2CShowCertMange, 
   7: S2CShowCertLook, 
   8: S2CCertItemData, 
   9: S2CNotDYT, 
   10: S2CCertAns, 
   11: S2CApplyCert, 
   12: S2CGHasSendSMS, 
   13: S2CBindPhone, 
   14: S2CBindAns, 
   15: S2CApplyTooMuch, 
   16: S2CSendCodeResult, 
   17: S2CCertMaxNum, 
   18: S2CNeedSelectCert, 
   19: S2CCertSucced, 
   20: S2CCancelCertAns, 
   21: S2CSecurityCodeTooFast, 
   22: S2CInstallCertSucced, 
   23: S2CSecurityCodeSucced, 
   24: S2CIsCertUser, 
   25: S2CInDYTUpdateTime, 
   26: S2CSecurityCodeFail, 
   27: S2CCloseCertAns, 
   28: S2CHeroPhone, 
   33: S2CAccoutRelation}

def S2CCert(netobj):
    global CRTT_FUNC_LIST
    isub = netobj.UnpackInt(1)
    func = CRTT_FUNC_LIST.get(isub)
    if callable(func):
        print '安全証書協議!!!' * 2, isub, func.__name__
        func(netobj)
    else:
        print '多益通証書協議  S2CCert 錯誤!!!!!!'
    return


def C2SNewCert():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(1, 1)
    netobj.PacketSend()
    return


def C2SApplyCert():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(2, 1)
    netobj.PacketSend()
    return


def C2SCertCenter():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(3, 1)
    netobj.PacketSend()
    return


def C2SGetKeyWith(sPhone):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(iMode, 1)
    netobj.PacketAddI(iOP, 1)
    netobj.PacketSend()
    print 'C2SMsgMode 短信驗証模式', iMode, iOP
    return


def C2SQuerySendState(sValKey):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(5, 1)
    netobj.PacketAddS(sPhone, 11)
    netobj.PacketSend()
    return


def C2SApplyBind(sPhone, sValiKey):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(6, 1)
    netobj.PacketAddS(sPhone, 11)
    netobj.PacketAddS(sValiKey, 32)
    netobj.PacketSend()
    return


def C2SGetValiKey(iFrom):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(7, 1)
    netobj.PacketAddI(iFrom, 1)
    netobj.PacketSend()
    return


def C2SSend6ValKey(sValKey):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(8, 1)
    netobj.PacketAddS(sValKey, 6)
    netobj.PacketSend()
    return


def C2SSend32ValKey(sValKey):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(9, 1)
    netobj.PacketAddS(sValKey, 32)
    netobj.PacketSend()
    return


def C2SManageCert():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(10, 1)
    netobj.PacketSend()
    return


def C2SSetupRes(iResult, sAdd='', sPCInfo=''):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(11, 1)
    netobj.PacketAddI(iResult, 1)
    if iResult and sAdd and sPCInfo:
        addLen = len(sAdd)
        netobj.PacketAddI(addLen, 1)
        netobj.PacketAddS(sAdd, addLen)
        pcinfoLen = len(sPCInfo)
        netobj.PacketAddI(pcinfoLen, 1)
        netobj.PacketAddS(sPCInfo, pcinfoLen)
    netobj.PacketSend()
    return


def C2SWantStopCert():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(12, 1)
    netobj.PacketAddI(1, 1)
    netobj.PacketSend()
    print '>>>>>>>>>>>>> jkang test: C2SWantStopCert(12-1)'
    return


def C2SConfirmStopCert(sValiKey):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(12, 1)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddS(sValiKey, 8)
    netobj.PacketSend()
    print '>>>>>>>>>>>>> jkang test: C2SConfirmStopCert(12-2)', sValiKey
    return


def C2SChangePage(iNowPage):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(13, 1)
    netobj.PacketAddI(iNowPage, 1)
    netobj.PacketSend()
    return


def C2SWantDYT():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(14, 1)
    netobj.PacketSend()
    return


def C2SDelCert(iPage, pcinfo, sCertID):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(15, 1)
    netobj.PacketAddI(iPage, 1)
    netobj.PacketAddS(pcinfo, 32)
    netobj.PacketAddI(len(sCertID), 2)
    netobj.PacketAddS(sCertID, len(sCertID))
    netobj.PacketSend()
    return


def C2SApplyChangePhone(sPhone):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(16, 1)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddS(sPhone, 11)
    netobj.PacketSend()
    return


def C2SChangePhone(phoneCode, mailCode):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(16, 1)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddS(mailCode, 8)
    netobj.PacketAddS(phoneCode, 6)
    netobj.PacketSend()
    return


def C2SStopChangePhone():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(16, 1)
    netobj.PacketAddI(4, 1)
    netobj.PacketSend()
    return


def C2SSend6ValKey2(sValKey):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(17, 1)
    netobj.PacketAddS(sValKey, 6)
    netobj.PacketSend()
    return


def C2SAskPhoneNum():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(18, 1)
    netobj.PacketSend()
    print '請求綁定的手機號碼    !!!!!!!'
    return


def C2SPasscheckCert():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(19, 1)
    netobj.PacketSend()
    print '請求服務端跳過証書檢測    !!!!!!!'
    return


def C2STryOtherAccout(account, res, encryptKey, oldKey, pcinfo):
    netobj = net.PacketPrepare(net.C2GS_CERTIFICATE)
    if netobj:
        netobj.PacketAddI(20, 1)
        iLen = len(account)
        netobj.PacketAddI(iLen, 1)
        netobj.PacketAddS(account, iLen)
        if res >= 0:
            iELen = len(encryptKey)
            netobj.PacketAddI(iELen, 1)
            netobj.PacketAddS(encryptKey, iELen)
            netobj.PacketAddS(oldKey, 32)
        else:
            netobj.PacketAddI(0, 1)
        netobj.PacketAddS(pcinfo, 32)
        print '請求服務端檢驗另外一個賬號 .', account
        import netpublic
        netpublic.SplitPacketSend(netobj, net.C2GS_CERTIFICATE)
    return


def C2SErrorLog(sTitle, sReason):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(98, 1)
    titleLen = len(sTitle)
    if titleLen > 50:
        sTitle = sTitle[:50]
        titleLen = 50
    netobj.PacketAddI(titleLen, 1)
    netobj.PacketAddS(sTitle, titleLen)
    reasonLen = len(sReason)
    if reasonLen > 180:
        sReason = sReason[:180]
        reasonLen = 180
    netobj.PacketAddI(reasonLen, 1)
    netobj.PacketAddS(sReason, reasonLen)
    netobj.PacketSend()
    return


def C2SCancle():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_CERTIFICATE)
    netobj.PacketAddI(99, 1)
    netobj.PacketSend()
    return


def C2STryOtherAccout(accountlist):
    import cert
    netobj = net.PacketPrepare(net.C2GS_CERTIFICATE)
    if netobj:
        netobj.PacketAddI(20, 1)
        hascertaccountlist = []
        encryptKeylist = []
        oldKeylist = []
        for account in accountlist:
            (res, encryptKey, oldKey) = cert.CertSign(account, isCache=1)
            if res >= 0:
                hascertaccountlist.append(account)
                encryptKeylist.append(encryptKey)
                oldKeylist.append(oldKey)
            print '檢驗：', account, '有証書', res >= 0, res

        accountstr = (',').join(hascertaccountlist)
        iLen = len(accountstr)
        netobj.PacketAddI(iLen, 1)
        if iLen:
            netobj.PacketAddS(accountstr, iLen)
        if encryptKeylist:
            encryptKeyStr = (',').join(encryptKeylist)
            iELen = len(encryptKeyStr)
            netobj.PacketAddI(iELen, 2)
            netobj.PacketAddBinaryS(encryptKeyStr, iELen)
            oldKeyStr = (',').join(oldKeylist)
            iLen = len(oldKeyStr)
            netobj.PacketAddI(iLen, 1)
            netobj.PacketAddBinaryS(oldKeyStr, iLen)
        else:
            netobj.PacketAddI(0, 2)
            netobj.PacketAddI(0, 1)
        pcinfo = cert.GetPCInfo(isCache=1)
        if not pcinfo:
            pcinfo = '0' * 32
        print '機器信息：', pcinfo
        netobj.PacketAddS(pcinfo, 32)
        print '請求服務端檢驗其他賬號 .', hascertaccountlist
        import netpublic
        netpublic.SplitPacketSend(netobj, net.C2GS_CERTIFICATE)
    return


return
