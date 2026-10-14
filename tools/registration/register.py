# -*- coding: utf-8 -*-
# login/register 模塊原生重寫版（第一期：管道驗證）
#
# 本文件是 script.fls 條目 4007（script\login\register.py）的權威源碼，
# 由 tools/registration/build_native_registration.py 用 CPython 2.5.6 編譯、
# 經 tools/decompiler/pack_and_encrypt.py 混淆加密後寫回新包。
# 源碼為 UTF-8（coding 宣告在首行）：繁體字串用字面或 \uXXXX 轉義，
# GBK 字節路徑（如步驟圖）用 \xXX 逐字節轉義，勿改其編碼。
#
# 與舊版（運營商時代）的差異（均已在 README.md 記賬）：
#   1. 刪除全部舊運營商網絡流程（HTTP 註冊、2980 郵箱/手機驗證、圖形驗證碼），
#      提交先留樁：校驗通過只彈「伺服器尚未開放註冊，請稍後再試」。
#   2. 保留對外接口 Show / ShowConfirmDlg / CConfirm / g_AccountInfo /
#      g_ConfirmDlg / g_RegisterPanel / ModuleReset，loginin、netlogin、
#      selectrole、mainpage 的既有調用不受影響。
#   3. 條款文本原由外部模塊 servicedata.SERVICE_MSG 提供；該模塊不在本
#      版本 script.fls 內，缺失時退回本文件內的佔位條款（正式條款待補）。
#   4. 規格（用戶 2026-10-14 拍板）：先過條款頁 -> 表單（密碼/確認密碼/
#      郵箱，第一期沿用舊 reg2.dlg 版式，郵箱即帳號；獨立帳號框待第二期
#      改版 layout 後加入）-> 樁提示。
import C_sys
import combdialog
import combmacro
import interface
import ui

g_AccountInfo = {}
g_CDKey = '1234567890123456'
g_ConfirmDlg = None
g_RegisterPanel = None


def ModuleReset():
    global g_AccountInfo
    global g_CDKey
    global g_ConfirmDlg
    global g_RegisterPanel
    g_AccountInfo = {}
    g_CDKey = '1234567890123456'
    g_ConfirmDlg = None
    g_RegisterPanel = None


def IsValid(txt):
    _invalid = ('"', "'", '/', '\\', '=', '+', '|', ';', ':', '[', ']', '{',
                '}', '?', '*', ',', '(', ')', '&', '^', '%', '$', '#', '!',
                '~', '`')
    for c in _invalid:
        if c in txt:
            return False
    return True


def ShowError(err, ecode=0, errmsg=''):
    import commondialog
    import dc_error_code
    if err not in dc_error_code.ERROR_MSG:
        if errmsg:
            msg = errmsg + '-%d' % err
        else:
            msg = MSG_UNKNOWN_ERR + '-%d' % err
    else:
        msg = dc_error_code.ERROR_MSG[err]
    commondialog.ShowNewMessageBox(msg, BTN_OK)


# ---------------------------------------------------------------------------
# 帳號確認框（login/confirm.dlg）：netlogin/selectrole 既有流程，原樣保留。
# ---------------------------------------------------------------------------

def ShowConfirmDlg(flag):
    global g_ConfirmDlg
    if flag == 1:
        g_ConfirmDlg = None
    else:
        g_ConfirmDlg = CConfirm(interface.DialogPanel)


class CConfirm(combdialog.CCombPanel):

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/confirm.dlg')
        self.Topmost()
        import chatoutput
        import servicedata
        result = [line[1:] for line in servicedata.CONFIRM_MSG.split('\n')]
        output = self.GetObject('output')
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        self.m_PublicTxtBox = chatoutput.COutput(
            self, w, h, 0, 0, result, txt_font=interface.FontLT14_3,
            txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.SetChatCursor(0)
        self.m_PublicTxtBox.ResetFromCursor()

    def OnMessage(self, msgid):
        if msgid == 1:
            import netlogin
            import selectrole
            import sound
            import sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            netlogin.C2SConfirmRegInfo()
            if selectrole.g_SelectRoleDlg:
                interface.SetDefaultButton(
                    selectrole.g_SelectRoleDlg.GetObject('btn_Login'))
            ShowConfirmDlg(1)
        elif msgid == 2:
            import main
            import sound
            import sounddefine
            sound.Play(sounddefine.PATH_BTN_SOUND)
            main.CloseGame()


# ---------------------------------------------------------------------------
# 註冊第一期：條款頁（login/reg1.dlg） + 表單頁（login/reg2.dlg）
# ---------------------------------------------------------------------------

# servicedata 缺失時的佔位條款（正式條款待補，見文件頭第 3 點）。
# UI 文字一律用 Big5 字節串（與原版模塊常量逐字節同編碼）。實機教訓：
# 傳 unicode 給原生彈框會在其內部做字節拼接時解碼失敗、靜默無反應。
BTN_OK = '\xbdT\xa9w'  # 確定
MSG_PWD_FORMAT = '\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xae\xe6\xa6\xa1\xaa\xba\xb1K\xbdX'  # 請輸入正確格式的密碼
MSG_PWD_ALNUM = '\xb5n\xbf\xfd\xb1K\xbdX\xb6\xc8\xa5i\xa5\xd1\xa6r\xa5\xc0\xa9\xce\xaa\xcc\xbc\xc6\xa6r\xb2\xd5\xa6\xa8,\xaa\xf8\xab\xd7\xac\xb06~16\xa6\xec\xa1C'  # 登錄密碼僅可由字母或者數字組成,長度為6~16位。
MSG_PWD_MISMATCH = '\xa8\xe2\xa6\xb8\xbf\xe9\xa4J\xaa\xba\xb1K\xbdX\xa4\xa3\xa4\xc7\xb0t'  # 兩次輸入的密碼不匹配
MSG_EMAIL_FORMAT = '\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xae\xe6\xa6\xa1\xaa\xba\xb6l\xbdc'  # 請輸入正確格式的郵箱
MSG_STUB = '\xa6\xf8\xaaA\xbe\xb9\xa9|\xa5\xbc\xb6}\xa9\xf1\xb5\xf9\xa5U\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5'  # 伺服器尚未開放註冊，請稍後再試
MSG_UNKNOWN_ERR = '\xa5\xbc\xaa\xbe\xbf\xf9\xbb~'  # 未知錯誤
MSG_SUBMIT_ERR = '\xb5\xf9\xa5U\xb4\xa3\xa5\xe6\xa5X\xbf\xf9\xa1A\xbd\xd0\xa6^\xb3\xf8\xba\xde\xb2z\xad\xfb'  # 註冊提交出錯，請回報管理員

# servicedata 缺失時的佔位條款（Big5 字節串，正式條款待補，見文件頭）。
TERMS_FALLBACK = [
    '\xb7|\xad\xfb\xaaA\xb0\xc8\xb1\xf8\xb4\xda',
    '',
    '\xa1]\xb4\xfa\xb8\xd5\xa6\xfb\xa6\xec\xa1^\xad\xec\xb1\xf8\xb4\xda\xa4\xe5\xa5\xbb\xa5\xd1 servicedata \xbc\xd2\xb2\xd5\xb4\xa3\xa8\xd1\xa1A',
    '\xa5\xbb\xb4\xfa\xb8\xd5\xa5]\xa5\xbc\xa5]\xa7t\xb8\xd3\xbc\xd2\xb2\xd5\xa1A\xa5\xbf\xa6\xa1\xb1\xf8\xb4\xda\xab\xdd\xb8\xc9\xa1C',
    '',
    '\xc2I\xa1u\xa7\xda\xa6P\xb7N\xa1v\xc4~\xc4\xf2\xb6\xf1\xbcg\xb5\xf9\xa5U\xb8\xea\xae\xc6\xa1A\xc2I\xa1u\xa7\xda\xa9\xda\xb5\xb4\xa1v\xaa\xf0\xa6^\xa1C',
]


def _Diag(text):
    """第一期診斷：把註冊流程的關鍵節點寫到 photo\\register_diag.txt。

    客戶端會吞掉 OnMessage 裡的腳本異常（界面上只是「沒反應」），
    沒有這支日誌就無從定位。純 ASCII 寫入，永不拋錯。
    """
    try:
        f = open('photo\\register_diag.txt', 'a')
        f.write(str(text) + '\n')
        f.close()
    except Exception:
        pass

# 步驟圖（GBK 字節路徑，與舊版常量逐字節一致，勿改編碼）。
IMG_STEP_TERMS = 'combdialog/\xd4\xd3\xcd\xbc/\xcd\xac\xd2\xe2\xcc\xf5\xbf\xee.igs'
IMG_STEP_FORM = 'combdialog/\xd4\xd3\xcd\xbc/\xcc\xee\xd0\xb4\xd7\xca\xc1\xcf.igs'


def _PlayBtnSound():
    import sound
    sound.Play('action/button.wav')


def _ReturnHome():
    Show(False)
    try:
        import mainpage
        mainpage.Show(True)
    except Exception:
        import main
        main.doreturn(interface.CBaseObject(None))


def _LoadTermsLines():
    try:
        import servicedata
        return [line[1:] for line in servicedata.SERVICE_MSG.split('\n')]
    except Exception:
        return list(TERMS_FALLBACK)


class CRegTermsPanel(combdialog.CCombPanel):
    """條款頁：msgid 1=我同意（進表單），其餘=返回首頁。"""

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg1.dlg')
        import chatoutput
        result = _LoadTermsLines()
        output = self.GetObject('output')
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        self.m_PublicTxtBox = chatoutput.COutput(
            self, w, h, 0, 0, result, txt_font=interface.FontLT12_1,
            txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.Refresh()
        self.m_PublicTxtBox.ScrollTo(0)
        try:
            self.m_ImgStep = ui.CImage(self, IMG_STEP_TERMS, 'interface')
            (x, y) = self.GetObject('reginfo1').GetPos()
            self.m_ImgStep.SetPos(x, y)
            self.m_ImgStep.SetFrame(1)
        except Exception:
            self.m_ImgStep = None

    def OnMessage(self, msgid):
        _PlayBtnSound()
        if msgid == 1:
            Step(1)
        else:
            _ReturnHome()
        return True


class CRegFormPanel(combdialog.CCombPanel):
    """表單頁：msgid 1=上一步（回條款），2=確認（校驗後留樁）。

    舊 reg2.dlg 無獨立帳號框，郵箱即帳號（原版式如此）；2980 連結與
    圖形驗證碼在新流程中不出現，相關佔位控件一律隱藏。
    """

    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/reg2.dlg')
        self.m_PwdEdit = combmacro.CEDIT(
            interface.CEdit, 'pwd', self, 16777215, interface.FontLT14_3,
            linecolor=16777215)
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit2 = combmacro.CEDIT(
            interface.CEdit, 'pwd2', self, 16777215, interface.FontLT14_3,
            linecolor=16777215)
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.m_IsPassword = True
        self.m_EmailEdit = combmacro.CEDIT(
            interface.CEdit, 'email', self, 16777215, interface.FontLT14_3,
            linecolor=16777215)
        self.m_EmailEdit.SetLimit(32)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_EmailEdit)
        self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        # 舊流程的確認郵箱/圖形驗證碼佔位一律隱藏（版式上仍在 dlg 裡）。
        for name in ('email2', 'edt_Code', 'txt_Mail2', 'img_Mail2Bg',
                     'txt_Code', 'txt_CodeBg', 'txt_RefershCode', 'youxiang'):
            try:
                obj = self.GetObject(name)
                if obj is not None:
                    obj.SetShow(False)
            except Exception:
                pass
        try:
            self.m_ImgStep = ui.CImage(self, IMG_STEP_FORM, 'interface')
            (x, y) = self.GetObject('reginfo2').GetPos()
            self.m_ImgStep.SetPos(x, y)
            self.m_ImgStep.SetFrame(1)
        except Exception:
            self.m_ImgStep = None
        self.m_PwdEdit.Active(True)

    def CheckEmail(self, email):
        if len(email) < 5 or len(email) > 50:
            return False
        import re
        patt = re.compile('^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$')
        return patt.match(email) is not None

    def DoCheck(self):
        """校验通过返回 None，否则返回要提示的文案（口径同旧版 DoCheck）。"""
        pwd = self.m_PwdEdit.GetText()
        if len(pwd) < 6 or len(pwd) > 16:
            self.m_PwdEdit.Active(True)
            return MSG_PWD_FORMAT
        if not pwd.isalnum():
            self.m_PwdEdit.Active(True)
            return MSG_PWD_ALNUM
        if pwd != self.m_PwdEdit2.GetText():
            self.m_PwdEdit2.Active(True)
            return MSG_PWD_MISMATCH
        email = self.m_EmailEdit.GetText().strip()
        if not self.CheckEmail(email):
            self.m_EmailEdit.Active(True)
            return MSG_EMAIL_FORMAT
        return None

    def DoSubmit(self):
        import commondialog
        _Diag('submit start')
        try:
            msg = self.DoCheck()
            _Diag('check done fail=%s' % (msg is not None))
            if msg is not None:
                commondialog.ShowNewMessageBox(msg, BTN_OK)
                _Diag('fail box shown')
                return
            g_AccountInfo['Password'] = self.m_PwdEdit.GetText()
            g_AccountInfo['Email'] = self.m_EmailEdit.GetText().strip()
            # 服務端註冊接口未就緒：先留樁，明示未接通（用戶定的文案）。
            commondialog.ShowNewMessageBox(MSG_STUB, BTN_OK)
            _Diag('stub box shown')
        except Exception:
            import sys
            _Diag('EXC %r' % (sys.exc_info()[1],))
            try:
                commondialog.ShowMessageBox(MSG_SUBMIT_ERR, BTN_OK)
            except Exception:
                _Diag('err box failed too')

    def OnMessage(self, msgid):
        _Diag('form msgid=%s' % (msgid,))
        _PlayBtnSound()
        if msgid == 1:
            Step(0)
        elif msgid == 2:
            self.DoSubmit()
        # msgid 3（2980 連結）/4（驗證碼刷新）已不建立控件，忽略。
        return True


_PANELS = [CRegTermsPanel, CRegFormPanel]


def Step(n):
    global g_RegisterPanel
    g_RegisterPanel = _PANELS[n](interface.DialogPanel)


def Show(s):
    global g_RegisterPanel
    if s:
        C_sys.InputSecrecy(1)
        Step(0)
    else:
        g_RegisterPanel = None
        C_sys.InputSecrecy(0)


# --- 舊版對外雜項接口：保留簽名，避免其他模塊引用時出錯 ---

def ShowRegisterCheckCode(imgbytes, vregval):
    # 图形验证码流程已删除，保留空接口。
    return None


def ShowRegisterCodeFail():
    return None


def SetCheckCode(checkcode):
    return False


def ClearRegCode():
    try:
        import os
        path = 'photo\\register'
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)
    except Exception:
        pass
