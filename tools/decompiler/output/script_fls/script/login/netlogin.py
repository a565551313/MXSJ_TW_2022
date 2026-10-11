# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\netlogin.py
import net, C_sys, C_object, C_debug, versions
g_CurrentTime = None
g_Balance = 0
g_CurrAccount = ''
g_BuyCardRecordPage = None
g_BuyCardRecordFlag = 0
g_ConsumePage = None
g_ConsumeFlag = 0
g_ServerNum = 0
CLIENT_VERSION = versions.CLIENT_VERSION
C_debug.ColorPrint('red', '\n腳本號:%s\n' % str(CLIENT_VERSION))

def GetScriptVersion():
    global CLIENT_VERSION
    return CLIENT_VERSION


def GetCurrAccount():
    global g_CurrAccount
    return g_CurrAccount


def C2SLoginIn(name, pwd):
    global g_CurrAccount
    import commondialog
    commondialog.ShowMessageBox('正在登錄中....', '取消')
    g_CurrAccount = name
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_LOGIN_ACCOUNT_ENTER)
    iScriptV1 = CLIENT_VERSION[0]
    import main
    if main.g_MiniVersion == 1:
        iScriptV1 |= 128
    netobj.PacketAddI(iScriptV1, 1)
    netobj.PacketAddI(CLIENT_VERSION[1], 1)
    netobj.PacketAddI(CLIENT_VERSION[2], 2)
    netobj.PacketAddS(name, 32)
    netobj.PacketAddS(pwd, 20)
    (n1, n2, n3) = C_sys.GetVersion()
    netobj.PacketAddI(n1, 1)
    netobj.PacketAddI(n2, 1)
    netobj.PacketAddI(n3, 2)
    import cfg
    ver = cfg.GetData('update.ini', 'Setting', 'Version')
    (s1, s2, s3) = ver.split('.')
    try:
        n1, n2, n3 = int(s1), int(s2), int(s3)
    except:
        (n1, n2, n3) = (0, 0, 0)

    netobj.PacketAddI(n1, 1)
    netobj.PacketAddI(n2, 1)
    netobj.PacketAddI(n3, 2)
    try:
        localip = C_sys.GetLocalIP()
    except:
        localip = [
         0, 0, 0, 0]

    import permission
    if permission.GetOverdoVersion():
        import random
        localip = [
         192, 168, random.randint(0, 254), random.randint(0, 254)]
    for v in localip:
        netobj.PacketAddI(v, 1)

    import misc
    try:
        adsid = long(main.g_Adsid)
    except:
        adsid = 0

    netobj.PacketAddI(adsid >> 32, 4)
    netobj.PacketAddI(adsid & 4294967295L, 4)
    import register
    tgId = ''
    if hasattr(register, 'g_TGID'):
        tgId = register.g_TGID
    netobj.PacketAddI(len(tgId), 1)
    netobj.PacketAddS(tgId, len(tgId))
    try:
        driveid = C_sys.GetDriveID()
    except:
        driveid = 0

    if permission.GetOverdoVersion():
        driveid = 0
    netobj.PacketAddI(driveid, 4)
    import certmgr, cert
    isCertLogin = certmgr.GetIsCertLogin()
    if isCertLogin:
        (res, encryptKey, oldKey) = cert.CertSign(name, isCache=1)
        if res >= 0:
            iELen = len(encryptKey)
            netobj.PacketAddI(iELen, 1)
            netobj.PacketAddS(encryptKey, iELen)
            netobj.PacketAddS(oldKey, 32)
        else:
            netobj.PacketAddI(0, 1)
        pcinfo = cert.GetPCInfo(isCache=1)
        if not pcinfo:
            pcinfo = '0' * 32
        netobj.PacketAddS(pcinfo, 32)
    try:
        mac = misc.GetMAC()
    except:
        mac = '0'

    if permission.GetOverdoVersion():
        mac = '0'
    netobj.PacketAddS(mac, len(mac))
    if isCertLogin:
        import netpublic
        netpublic.SplitPacketSend(netobj, net.C2GS_LOGIN_ACCOUNT_ENTER)
    else:
        netobj.PacketSend()
    if isCertLogin:
        cert.SendErrLogCache()
    return


def C2SLoginPlayerEnter(id):
    print 'id=%d' % id
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_LOGIN_PLAYER_ENTER)
    netobj.PacketAddI(id, 4)
    netobj.PacketSend()
    return


def C2GSRoleInfoLog(iHasUsedDay, sFirstLoginAccount):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_LOGIN_PLAYER_ADD_ENTER)
    oNetObj.PacketAddI(3, 1)
    oNetObj.PacketAddI(iHasUsedDay, 2)
    oNetObj.PacketAddPS(sFirstLoginAccount, 1)
    oNetObj.PacketSend()
    return


def C2SLoginPlayerAdd(name, icon, shape, color, major, randflag, liupai):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_LOGIN_PLAYER_ADD)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddS(name, 20)
    netobj.PacketAddI(icon, 1)
    netobj.PacketAddI(shape, 2)
    netobj.PacketAddI(color + color * 8 + color * 64, 2)
    netobj.PacketAddI(major, 1)
    netobj.PacketAddI(randflag, 1)
    netobj.PacketAddI(liupai, 2)
    netobj.PacketSend()
    return


def C2SBindAccount(name):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(6, 1)
    netobj.PacketAddS(name, len(name))
    netobj.PacketSend()
    return


def C2SReleaseBind(name):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(7, 1)
    netobj.PacketAddS(name, len(name))
    netobj.PacketSend()
    return


def C2SGetAccountBalance():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(2, 1)
    netobj.PacketSend()
    return


def C2SChgPwd(oldpwd, newpwd):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddS(oldpwd, 20)
    netobj.PacketAddS(newpwd, 20)
    netobj.PacketSend()
    return


def C2SSetLocalPwd(size, oldpwd, newpwd):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(8, 1)
    netobj.PacketAddI(size, 2)
    netobj.PacketAddS(oldpwd, 20)
    netobj.PacketAddS(newpwd, 20)
    netobj.PacketSend()
    return


def C2SLocalPwdSuccess():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(9, 1)
    netobj.PacketSend()
    return


def C2SReEnterAnswer(dlg):
    netobj = net.g_Net
    if not netobj:
        return
    if not hasattr(dlg, 'm_ResponseIdx'):
        return
    netobj.PacketPrepare(net.C2GS_REENTER_KUAFU)
    netobj.PacketAddI(dlg.m_ResponseIdx + 1, 1)
    netobj.PacketSend()
    return


def C2SExchgGameTime(userid, days):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(5, 1)
    netobj.PacketAddI(userid, 4)
    netobj.PacketAddI(days, 1)
    netobj.PacketSend()
    return


def C2SExchgGamePoint(userid, point):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(12, 1)
    netobj.PacketAddI(userid, 4)
    netobj.PacketAddI(point, 2)
    netobj.PacketSend()
    return


def C2SLeaveQueue(msgbox):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_LOGIN_QUEUE)
    netobj.PacketSend()
    return


def C2SGetConsumeRecord(pagenum):
    global g_ConsumePage
    g_ConsumePage = pagenum
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(3, 1)
    netobj.PacketAddI(pagenum, 1)
    netobj.PacketSend()
    return


def C2SGetBuyCardRecord(pagenum):
    global g_BuyCardRecordPage
    g_BuyCardRecordPage = pagenum
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(4, 1)
    netobj.PacketAddI(pagenum, 1)
    netobj.PacketSend()
    return


def C2SLoginLocalPW(buf):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_LOGIN_LOCALPW)
    netobj.PacketAddBinaryS(buf, len(buf))
    netobj.PacketSend()
    return


def C2SAccount():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(16, 1)
    netobj.PacketSend()
    return


def C2SReConnect(idx, pwd):
    import net
    netobj = net.g_Net
    netobj.PacketPrepare(9)
    netobj.PacketAddI(CLIENT_VERSION[0], 1)
    netobj.PacketAddI(CLIENT_VERSION[1], 1)
    netobj.PacketAddI(CLIENT_VERSION[2], 2)
    netobj.PacketAddI(idx, 4)
    netobj.PacketAddS(pwd, 20)
    (n1, n2, n3) = C_sys.GetVersion()
    netobj.PacketAddI(n1, 1)
    netobj.PacketAddI(n2, 1)
    netobj.PacketAddI(n3, 2)
    import cfg
    ver = cfg.GetData('update.ini', 'Setting', 'Version')
    (s1, s2, s3) = ver.split('.')
    try:
        n1, n2, n3 = int(s1), int(s2), int(s3)
    except:
        (n1, n2, n3) = (0, 0, 0)

    netobj.PacketAddI(n1, 1)
    netobj.PacketAddI(n2, 1)
    netobj.PacketAddI(n3, 2)
    try:
        localip = C_sys.GetLocalIP()
    except:
        localip = [
         0, 0, 0, 0]

    for v in localip:
        netobj.PacketAddI(v, 1)

    import misc
    try:
        mac = misc.GetMAC()
    except:
        mac = '0'

    netobj.PacketAddS(mac, len(mac))
    netobj.PacketSend()
    return


def S2CHello(netobj):
    global g_PingTimer
    global g_ServerNum
    seed = netobj.UnpackInt(4)
    g_ServerNum = netobj.UnpackInt(2)
    isUseCertServer = netobj.UnpackInt(1)
    import certmgr
    certmgr.SetIsCertLogin(isUseCertServer)
    net.g_Net.SetSeed(seed)
    net.g_Net.m_Hello = True
    print 'seed1:%x' % seed
    seed = 4294967296L + seed
    seed = seed % 3227993 + 2562088 ^ 6636321
    netobj.NakedSend(chr(seed % 256) + chr(seed / 256 % 256) + chr(seed / 65536 % 256) + ' ' + ' ' * 21)
    import audio
    audio.InitChatAudio()
    if hasattr(net.g_Net, 'm_ReConnect'):
        import netquicklogin

        def DelayConnect(obj, dummy):
            if not net.g_Net.IsSent():
                return (
                 dummy,)
            C2SReConnect(net.g_Net.m_Idx, net.g_Net.m_Pwd)
            delattr(net.g_Net, 'm_ReConnect')
            net.g_Net.m_Idx = None
            net.g_Net.m_Pwd = None
            return

        delayobj = C_object.CBaseObject(None)
        delayobj.CreatePyCommand(0, DelayConnect, delayobj)
        netquicklogin.SetCanQuickLogin(True)
        return
    if hasattr(net.g_Net, 'm_QuickLogin'):

        def DelayQuickLogin(obj, dummy):
            if not net.g_Net.IsSent():
                return (
                 dummy,)
            import netquicklogin
            netquicklogin.C2SRequestQuickLogin(net.g_Net.m_LoginKey, net.g_Net.m_HeroID)
            delattr(net.g_Net, 'm_QuickLogin')
            return

        delayobj = C_object.CBaseObject(None)
        delayobj.CreatePyCommand(0, DelayQuickLogin, delayobj)
        return
    import selectserver
    selectserver.Show(False)
    import commondialog
    commondialog.HideMessageBox()
    import loginin
    loginin.ShowLogin()

    def Ping(obj):
        import net
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_PING)
        netobj.PacketSend()
        return ()

    g_PingTimer = C_object.CBaseObject(None)
    g_PingTimer.CreatePyCommand(9000, Ping)
    import mainpage
    mainpage.Show(False)
    return


InputDlg = None

def S2CLoginMessage(netobj):
    global InputDlg
    isub = netobj.UnpackInt(1)
    print 'S2CLoginMessage isub = ', isub
    if isub == 1:
        import loginin
        email = netobj.UnpackString(0)
        loginin.ShowSetDYT(email)
    elif isub == 2:
        result = {}
        result['idcard'] = netobj.UnpackInt(1)
        result['gadvpass'] = netobj.UnpackInt(1)
        result['qq'] = netobj.UnpackInt(1)
        result['mobile'] = netobj.UnpackInt(1)
        result['name'] = netobj.UnpackInt(1)
        import dlgsysopt, dlgitem
        if dlgsysopt.g_SysOptDialog:
            dlgsysopt.g_SysOptDialog.SetShow(True)
            dlgsysopt.g_SysOptDialog.GoAccountPage(71, result)
            if dlgitem.g_ItemDialog:
                dlgitem.g_ItemDialog.SetShow(False)
        else:
            dlgsysopt.ShowSwitch(71)
            dlgsysopt.g_SysOptDialog.GoAccountPage(71, result)
    elif isub == 3:
        import usermacro, loginin, selectrole, selectserver, net
        usermacro.PROMPT_MSG('您的遊戲密碼已經激活，請使用該密碼登錄遊戲。')
        loginin.CloseUpgrade()
        selectrole.Show(False)
        selectserver.Show(True)
        net.g_Net.Disconnect()
    elif isub == 10:

        def BeUpdate(dlg):
            import net
            netobj = net.g_Net
            netobj.PacketPrepare(net.C2GS_DYT)
            netobj.PacketAddI(11, 1)
            netobj.PacketSend()
            return

        flag = netobj.UnpackInt(1)
        import commondialog, main, misc
        if not flag:
            commondialog.ShowMessageBox('您的帳號未升級為多益通帳號，#Y請於2013年1月1日前升級，否則屆時帳號將無法登錄遊戲#n。#r（注意：升級後原帳號的本地密碼將會失效，新升級的多益通帳號暫不提供本地密碼服務）', ('立即升級',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          '暫不升級'), (BeUpdate, None))
        else:
            commondialog.ShowMessageBox('您的帳號未升級為多益通帳號，#Y暫停使用#n，升級為多益通帳號後可繼續使用#r（注意：升級後原帳號的本地密碼將會失效，新升級的多益通帳號暫不提供本地密碼服務）', ('立即升級',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   '重新登錄'), (BeUpdate, main.doreturn))
    elif isub == 11:
        itype = netobj.UnpackInt(1)
        mail = netobj.UnpackString(0)
        import loginin
        print 'S2CLoginMessage itype = ', itype
        if itype == 1:
            C2SReqDYTUseEmailCode('')
        elif itype == 2:
            loginin.ShowUsePasswordDlg()
        elif itype == 3:
            loginin.ShowFinallyPathDlg(0)
        elif itype == 4:
            loginin.ShowEmailCodeDlg(mail)
    elif isub == 13:
        import loginin
        loginin.ShowConfirmDlg()
    elif isub == 14:
        import loginin
        loginin.g_TempMailPwd = None
        imode = netobj.UnpackInt(1)
        email = netobj.UnpackString(0)
        if imode in (1, 2):
            import commondialog
            commondialog.ShowMessageBox('您的原遊戲帳號已成功升級到多益通帳號：#Y%s#n，請重新進入遊戲並#Y使用升級後的多益通帳號登錄#n#r您的原遊戲帳號（包括原註冊帳號、數字帳號及自定義帳號）將不能使用' % email, ('我知道了', ))
            loginin.CloseUpgrade()
        elif imode == 3:
            import usermacro
            usermacro.PROMPT_MSG('成功提交升級為多益通的申請。30天的確認期滿後可以確認正式將帳號升級為多益通')
            loginin.CloseUpgrade()
        elif imode == 11:
            import usermacro
            usermacro.PROMPT_MSG('驗証碼已發送至您的註冊郵箱中，請注意查收。')
        elif imode == 12:
            import usermacro
            usermacro.PROMPT_MSG('您的原遊戲帳號已成功升級到多益通帳號：#Y%s#n，請重新進入遊戲並#Y使用升級後的多益通帳號登錄#n#r您的原遊戲帳號（包括原註冊帳號、數字帳號及自定義帳號）將不能使用' % email)
        elif imode == 13:
            import usermacro
            usermacro.PROMPT_MSG('您已成功取消多益通升級申請')
        if imode in (1, 2, 3, 12):
            import selectrole, selectserver, net
            selectrole.Show(False)
            selectserver.Show(True)
            net.g_Net.Disconnect()
        if imode in (1, 2, 12):
            loginin.g_DefaultAccount = email
            loginin.SaveAccount(email)
    elif isub == 15:
        imode = netobj.UnpackInt(1)
        sz = netobj.UnpackInt(1)
        email = netobj.UnpackString(sz)
        secs = netobj.UnpackString(0)
        import commondialog

        def RealCancel(dlg):
            C2SUpdateDYT(0)
            return

        def RealUpdate(dlg):
            C2SUpdateDYT(1)
            return

        def CancelUpdate(dlg):
            commondialog.ShowMessageBox('確定要取消您的多益通升級嗎？取消後若再次升級將需要重新等待30天。', ('確定取消',
                                                                                                                                                                                                                                                              '不要取消'), (RealCancel, None))
            return

        def SureToUpdate(dlg):
            commondialog.ShowMessageBox('確定要將您的帳號升級為#Y%s#n嗎？升級成功後，原帳號將無法繼續登錄遊戲。' % email, ('確定升級',
                                                                                                                                                                                                                                                                          '暫不升級'), (RealUpdate, None))
            return

        if imode == 1:
            secs = int(secs)
            min_day = 1
            if secs >= min_day * 3600 * 24:
                msg = '您的帳號正在升級為多益通#Y%s#n，需要等待#Y%d#n天後方可成功升級。升級後原帳號無法使用，需使用多益通進行登錄' % (email, secs / 86400)
            else:
                msg = '您的帳號正在升級為多益通#Y%s#n，需要等待小於%d天後方可成功升級。升級後原帳號無法使用，需使用多益通進行登錄' % (email, min_day)
            dlg = commondialog.ShowMessageBox(msg, ('我知道了',
                                                    '取消升級'), (None, CancelUpdate))
            dlg.m_AutoCancel = False
        elif imode == 2:
            secs = int(secs) / 86400
            if secs > 0:
                dlg = commondialog.ShowMessageBox('您的帳號已可以升級為多益通帳號#Y%s#n，請確認升級。如果在#Y%d#n天內沒有確認，將導致升級失敗' % (email, secs), ('確定升級',
                                                                                                                                                                                                                                                                                                                                          '取消升級'), (SureToUpdate, CancelUpdate))
                dlg.m_AutoCancel = False
            else:
                commondialog.ShowMessageBox('您的多益通#Y%s#n在規定時間內未確認升級，現已幫您取消本次升級，請重新升級' % email, ('我知道了', ), (RealCancel,))
    elif isub == 16:

        def callback(msgid):
            import net, gameurl
            if msgid == 2:
                url = gameurl.DYT_RESET_WEB_URL
            elif msgid == 3:
                url = gameurl.DYT_RESET_GAME_URL
            else:
                return
            net.OpenUrl(url)
            return

        import dlgnpc
        s = '您的多益通網站密碼與多益通遊戲密碼相同，建議修改為不同密碼\nL暫不修改\nL重設多益通網站密碼\nL重設多益通遊戲密碼'
        dlgnpc.ShowClientDlg(s, '', callback)
    elif isub == 17:
        sEmail = netobj.UnpackString(0)
        err_msg = '該多益通帳號目前處於升級確認期，暫時無法登錄。請使用原帳號（#Y%s#n）登錄。' % sEmail
        import commondialog
        commondialog.ShowMessageBox(err_msg, '確定')
    elif isub == 18:
        import loginin
        loginin.HintExistSameEmail()
    elif isub == 21:
        name = netobj.UnpackString(0)

        def callback(msgid):
            global InputDlg
            import net, gameurl
            if msgid == 2:

                def _ok(dlg, txt):
                    C2S2980Code(txt)
                    return

                import commondialog
                commondialog.ShowInputDialog('請輸入您的2980郵箱密碼，輸入正確可直接將遊戲密碼修改成2980郵箱密碼', _ok, True)
                InputDlg = commondialog.InputDialog
            elif msgid == 3:
                import dlgnpc

                def call(msgid):
                    import net
                    if msgid == 1:
                        net.OpenUrl('http://www.2980.com/getPwd.aspx?pwdmod=web')
                    elif msgid == 2:
                        net.OpenUrl('http://www.2980.com/getPwd.aspx')
                    return

                s = '請選擇重置2980郵箱密碼的方式\nL使用填寫的QQ號或手機號重置2980郵箱密碼\nL我換了手機號，申請使用通行証遊戲密碼重置2980郵箱密碼'
                dlgnpc.ShowClientDlg(s, '', call)
            else:
                return
            return

        import dlgnpc
        s = '由於優化了2980郵箱密碼的找回流程，為了更方便記憶，建議將您的遊戲登錄密碼修改為與2980郵箱密碼一致\nL暫不修改\nL將2980郵箱密碼作為遊戲密碼\nL我忘記了2980郵箱密碼'
        dlgnpc.ShowClientDlg(s, '', callback)
    elif isub == 22:
        InputDlg = None
        import usermacro
        usermacro.PROMPT_MSG('已成功將遊戲密碼修改為2980郵箱密碼')
    return


g_LoginErrorCallback = None

def S2CLoginError(netobj):
    err_id = netobj.UnpackInt(1)
    if g_LoginErrorCallback != None:
        if err_id != 0:
            import dc_error_code, loginin
            if err_id == 156:
                msg = '密碼錯誤，或該帳號未升級為多益通，請在帳號後面加上@mx後再登錄（如下所示）#r#Y%s@mx#n' % loginin.g_LoginEmail
            elif dc_error_code.ERROR_MSG.has_key(err_id):
                msg = dc_error_code.ERROR_MSG[err_id]
            else:
                msg = '未知錯誤(%d)' % err_id
            g_LoginErrorCallback(err_id, msg)
            if err_id == 156:
                import loginin, selectrole, selectserver, net
                loginin.CloseUpgrade()
                selectrole.Show(False)
                selectserver.Show(True)
                net.g_Net.Disconnect()
        else:
            g_LoginErrorCallback(None, None)
    return


def S2CLoginLocalPW(netobj):
    n1 = netobj.UnpackInt(1)
    n2 = netobj.UnpackInt(1)
    n3 = netobj.UnpackInt(1)
    import pwdcard
    pwdcard.Show(n1, n2, n3)
    return


def C2SPwdCard(n1, n2, n3):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_LOGIN_LOCALPW)
    netobj.PacketAddI(n1, 1)
    netobj.PacketAddI(n2, 1)
    netobj.PacketAddI(n3, 1)
    netobj.PacketSend()
    return


g_LoginRoleInfo = None

def GetLoginRoleInfo():
    global g_LoginRoleInfo
    return g_LoginRoleInfo


def EnterSelectRole():
    import dlgnationfight, commondialog
    if dlgnationfight.g_NationFightRegister:
        commondialog.HideMessageBox()
        return
    import loginin
    loginin.OnLogin()
    loginin.Show(False)
    commondialog.HideMessageBox()
    import point2month
    point2month.Show(False)
    import selectrole
    selectrole.Show(True)
    import banword
    banword.UpdateBanWord()
    return


def S2CLoginAccountInfo(netobj):
    global g_CurrentTime
    global g_LoginAccountInfo
    global g_LoginRoleInfo
    g_LoginAccountInfo = {}
    g_LoginRoleInfo = []
    g_LoginAccountInfo['Count'] = netobj.UnpackInt(1)
    g_CurrentTime = netobj.UnpackInt(4)
    import selectserver
    vid = netobj.UnpackInt(1)
    _vid2ver = {1: 2, 2: 1, 3: 0}
    try:
        selectserver.g_ServerVersion = _vid2ver[vid]
        print 'game version = %d' % selectserver.g_ServerVersion
    except:
        print 'game version error'

    g_LoginAccountInfo['CurCount'] = 0
    if g_LoginAccountInfo['Count'] == 0:
        EnterSelectRole()
    return


def S2CLoginRoleInfo(netobj):
    info = {}
    info['ID'] = netobj.UnpackInt(4)
    info['time'] = netobj.UnpackInt(4)
    info['Icon'] = netobj.UnpackInt(1)
    info['Shape'] = netobj.UnpackInt(2)
    info['Desc'] = netobj.UnpackInt(2)
    info['Level'] = netobj.UnpackInt(1)
    info['School'] = netobj.UnpackInt(1)
    info['Race'] = netobj.UnpackInt(1)
    if info['Race'] not in (0, 1, 2, 3, 4):
        info['Race'] = 0
    info['iPrepareLoad'] = netobj.UnpackInt(1)
    n = netobj.UnpackSigned(4)
    info['Point'] = n
    info['Name'] = netobj.UnpackString(16)
    info['Photo'] = (info['Icon'] - 1) % 12 + 1
    for (idx, inf) in enumerate(g_LoginRoleInfo):
        if inf['ID'] == info['ID']:
            g_LoginRoleInfo[idx] = info
            break
    else:
        g_LoginRoleInfo.append(info)
        g_LoginAccountInfo['CurCount'] += 1

    if g_LoginAccountInfo['CurCount'] == g_LoginAccountInfo['Count']:
        EnterSelectRole()
    return


def S2CLoginQueue(netobj):
    queue_pos = netobj.UnpackInt(2)
    import selectserver
    try:
        servername = selectserver.g_LoginServer[1]
    except:
        servername = ''

    import cfg
    cfg.SaveData('mx.ini', 'Game', 'refreshserver', '0')
    import commondialog
    commondialog.ShowMessageBox('%s 已滿#r你現在的排隊位置是：%d' % (servername, queue_pos), '取消', C2SLeaveQueue)
    return


def S2CLoginRoleEnter(netobj):
    return


def _EnterAdminRole():
    import commondialog
    commondialog.HideMessageBox()
    import selectrole
    if selectrole.GetShow():
        selectrole.Show(False)
        import point2month
        point2month.Show(True, selectrole.g_SelectRoleIdx)
    else:
        selectrole.Show(True)
    return


def _EnterSelectRole(msgbox):
    import createrole
    createrole.Show(False)
    import commondialog
    commondialog.HideMessageBox()
    import selectrole
    selectrole.Show(True)
    return


def _EnterAdminNewRole(msgbox):
    import createrole
    createrole.Show(False)
    import commondialog
    commondialog.HideMessageBox()
    import selectrole
    selectrole.Show(True)
    return


def _GotoConversion(msgbox):
    import commondialog
    commondialog.ShowMessageBox('新創建的角色最好轉換遊戲時間後再進入遊戲！', '確定', _EnterAdminNewRole)
    return


def S2CLoginPlayerAdd(netobj):
    import commondialog
    commondialog.ShowMessageBox('恭喜您，創建角色成功！', '確定', _EnterAdminNewRole)
    return


def C2SCardCharge(account, code, pwd, mode):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(10, 1)
    netobj.PacketAddS(account, 20)
    netobj.PacketAddS(code, 12)
    netobj.PacketAddS(pwd, 8)
    netobj.PacketAddI(mode, 1)
    netobj.PacketSend()
    return


def C2SDelRole(uid):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(11, 1)
    netobj.PacketAddI(uid, 4)
    netobj.PacketSend()
    return


def S2CLoginDelRole(netobj):
    uid = netobj.UnpackInt(4)
    if g_LoginRoleInfo == None:
        return
    for info in g_LoginRoleInfo:
        if info['ID'] == uid:
            g_LoginRoleInfo.remove(info)
            import commondialog, selectrole
            commondialog.HideMessageBox()
            selectrole.Show(True)
            break

    return


def S2CAccountManage(netobj):
    global g_Balance
    global g_BuyCardRecordFlag
    global g_ConsumeFlag
    type = netobj.UnpackInt(1)
    if type == 1:
        balance = netobj.UnpackInt(4)
        g_Balance = balance
        _EnterAdminRole()
    elif type == 2:
        ERRTXT = {54: '新舊密碼相同', 91: '身份証號碼錯誤', 
           40: '您的操作沒有成功，可能是舊密碼不正確或帳號不存在。', 
           21: '操作出現異常，請重試。'}
        import commondialog
        errnum = netobj.UnpackInt(1)
        if errnum == 0:
            commondialog.ShowMessageBox('密碼修改成功！', '確定')
        else:
            if ERRTXT.has_key(errnum):
                txt = '密碼修改失敗！' + ERRTXT[errnum]
            else:
                txt = '密碼修改失敗！'
            if errnum == 91:

                def doexit(dlg):
                    import main
                    main.CloseGame()
                    return

                commondialog.ShowMessageBox(txt, '確定', (doexit,))
            else:
                commondialog.ShowMessageBox(txt, '確定')
    elif type == 3:
        linenum = netobj.UnpackInt(1)
        result = []
        for i in xrange(linenum):
            time = netobj.UnpackInt(4)
            desc = netobj.UnpackInt(1)
            code = netobj.UnpackString(32)
            point = netobj.UnpackInt(4)
            left = netobj.UnpackInt(4)
            result.append((time, desc, code, point, left))

        if len(result) <= 23:
            g_ConsumeFlag = 1
        else:
            g_ConsumeFlag = 0
        import selectrole
        selectrole.Show(False)
        import commondialog
        commondialog.HideMessageBox()
        import accountinfo
        if len(result) > 23:
            accountinfo.ShowAccountConsume(True, result[:23])
        else:
            accountinfo.ShowAccountConsume(True, result)
    elif type == 4:
        linenum = netobj.UnpackInt(1)
        result = []
        for i in xrange(linenum):
            time = netobj.UnpackInt(4)
            cardType = netobj.UnpackString(20)
            cardCode = netobj.UnpackString(16)
            cardPwd = netobj.UnpackString(16)
            result.append((time, cardType, cardCode, cardPwd))

        if len(result) <= 24:
            g_BuyCardRecordFlag = 1
        else:
            g_BuyCardRecordFlag = 0
        import selectrole
        selectrole.Show(False)
        import commondialog
        commondialog.HideMessageBox()
        import accountinfo
        if len(result) > 24:
            accountinfo.ShowBuyCardRecord(True, result[:24])
        else:
            accountinfo.ShowBuyCardRecord(True, result)
    elif type == 5:
        userid = netobj.UnpackInt(4)
        limit_time = netobj.UnpackInt(4)
        left_balance = netobj.UnpackInt(4)

        def _Charge(dlg):
            return

        import commondialog, point2month
        if limit_time <= 0:
            point2month.Show(True)
            commondialog.ShowMessageBox('轉換遊戲時間失敗！', '確定')
            return
        for ri in g_LoginRoleInfo:
            if ri['ID'] == userid:
                ri['time'] = limit_time
                g_Balance = left_balance
                point2month.Show(True)
                commondialog.ShowMessageBox('轉換遊戲時間成功！', '確定')
                return

        point2month.Show(True)
        commondialog.ShowMessageBox('轉換遊戲時間失敗！', '確定')
    elif type in (6, 7):
        ret = netobj.UnpackInt(1)
        point = netobj.UnpackInt(4)
        g_Balance = point
        import selfaccount, dlgsecurity
        selfaccount.Success(type, ret, point)
        dlgsecurity.Success(type, ret, point)
    elif type == 8:
        import localpwd
        localpwd.CreateLocalPwdFile(netobj)
    elif type == 9:
        import localpwd
        localpwd.CreateFail(netobj)
    elif type == 10:
        import localpwd
        localpwd.CreateSuccess(netobj)
    elif type == 11:
        ret = netobj.UnpackInt(1)
        point = netobj.UnpackInt(2)
        left = netobj.UnpackInt(4)
        import cardcharge
        cardcharge.ChargeSuccess(ret, point)
    elif type == 12:
        print 'modify info'
        import modifyinfo
        modifyinfo.Show()
    elif type == 13:
        import register
        register.ShowConfirmDlg(0)
    elif type == 14:
        import dlgnationfight
        dlgnationfight.ShowNationFightConfirm()
    elif type == 15:
        flag = netobj.UnpackInt(1)
        import selectrole
        selectrole.g_AccountFlag = flag
    return


def S2CReEnterKuaFu(netobj):
    import dlgnpc, commondialog
    word = netobj.UnpackString(0)
    pages = dlgnpc.ParseWord(word)
    if not pages:
        return
    page = pages[0]
    if not page:
        return
    text = page.get('text', '')
    question = page['question']
    lQuest = [_[1] for (_, sQuest) in question]
    lQuest = tuple(lQuest)
    dlg = commondialog.ShowNewMessageBox(text, lQuest, tuple([C2SReEnterAnswer] * len(lQuest)))
    return


def C2SModifyInfo(name, identity):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(13, 1)
    netobj.PacketAddS(name, 16)
    netobj.PacketAddS(identity, len(identity))
    netobj.PacketSend()
    return


def C2SConfirmRegInfo():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_ACCOUNT_MANAGE)
    netobj.PacketAddI(14, 1)
    netobj.PacketSend()
    return


def C2SCheckEmail():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(15, 1)
    netobj.PacketSend()
    return


def C2SReqDYTUseEmailCode(emailcode):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(12, 1)
    netobj.PacketAddS(emailcode, len(emailcode))
    netobj.PacketSend()
    return


def C2SReqDYTUsePassword(password):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(13, 1)
    netobj.PacketAddS(password, len(password))
    netobj.PacketSend()
    return


def C2SAffirmUseDYT():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(16, 1)
    netobj.PacketSend()
    return


def C2SDYTCloseDlg():
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(99, 1)
    netobj.PacketSend()
    return


def C2SSetActive(pwd):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(1, 1)
    netobj.PacketAddS(pwd, len(pwd))
    netobj.PacketSend()
    return


def C2SPrivateInfo(info):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(2, 1)
    netobj.PacketAddS(info, len(info))
    netobj.PacketSend()
    return


def C2SReqDYTUseEMail(email, password):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(14, 1)
    netobj.PacketAddI(len(email), 1)
    netobj.PacketAddS(email, len(email))
    netobj.PacketAddS(password, len(password))
    netobj.PacketSend()
    return


def C2SUpdateDYT(flag):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(17, 1)
    netobj.PacketAddI(flag, 1)
    netobj.PacketSend()
    return


def C2SAffirmUseSameEmail(email, password):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(18, 1)
    netobj.PacketAddI(len(email), 1)
    netobj.PacketAddS(email, len(email))
    netobj.PacketAddS(password, len(password))
    netobj.PacketSend()
    return


def C2S2980Code(txt):
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_DYT)
    netobj.PacketAddI(21, 1)
    netobj.PacketAddS(txt, len(txt))
    netobj.PacketSend()
    return


def C2SUpdateUserInfo(isub):
    return
    import netpublic, C_sys, mainpage, platform
    netobj = netpublic.GetHeader(netpublic.C2GS_UPDATE_URS_INFO)
    netobj.PacketAddI(isub, 1)
    if isub == 1:
        ver_txt = ''
        try:
            version = platform.uname()
            if len(version) >= 4:
                ver_txt = version[0] + version[2] + '-' + version[3]
            else:
                ver_txt = ('').join(version[:2])
        except:
            print '版本獲取錯誤'
        else:
            wndsize = C_sys.GetScreenResolution()
            wndsize_txt = '%dX%d' % (wndsize[0], wndsize[1])
            tgid = mainpage.GetTGID()
            netobj.PacketAddI(0, 1)
            netobj.PacketAddI(len(ver_txt), 1)
            netobj.PacketAddS(ver_txt, len(ver_txt))
            netobj.PacketAddI(len(wndsize_txt), 1)
            netobj.PacketAddS(wndsize_txt, len(wndsize_txt))
            netobj.PacketAddI(len(str(tgid)), 1)
            netobj.PacketAddS(str(tgid), len(str(tgid)))
            netobj.PacketSend()
    return


return
