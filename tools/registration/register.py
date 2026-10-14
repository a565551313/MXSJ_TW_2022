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
            msg = u'\u672a\u77e5\u932f\u8aa4(%d)' % err
    else:
        msg = dc_error_code.ERROR_MSG[err]
    commondialog.ShowNewMessageBox(msg, u'\u78ba\u5b9a')


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
TERMS_FALLBACK = [
    u'\u6703\u54e1\u670d\u52d9\u689d\u6b3e',
    u'',
    u'\uff08\u6e2c\u8a66\u4f54\u4f4d\uff09\u539f\u689d\u6b3e\u6587\u672c'
    u'\u7531 servicedata \u6a21\u7d44\u63d0\u4f9b\uff0c',
    u'\u672c\u6e2c\u8a66\u5305\u672a\u5305\u542b\u8a72\u6a21\u7d44'
    u'\uff0c\u6b63\u5f0f\u689d\u6b3e\u5f85\u88dc\u3002',
    u'',
    u'\u9ede\u300c\u6211\u540c\u610f\u300d\u7e7c\u7e8c\u586b\u5beb'
    u'\u8a3b\u518a\u8cc7\u6599\uff0c\u9ede\u300c\u6211\u62d2\u7d55\u300d'
    u'\u8fd4\u56de\u3002',
]

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
            return u'請輸入正確格式的密碼'
        if not pwd.isalnum():
            self.m_PwdEdit.Active(True)
            return u'登錄密碼僅可由字母或者數字組成,長度為6~16位。'
        if pwd != self.m_PwdEdit2.GetText():
            self.m_PwdEdit2.Active(True)
            return u'兩次輸入的密碼不匹配'
        email = self.m_EmailEdit.GetText().strip()
        if not self.CheckEmail(email):
            self.m_EmailEdit.Active(True)
            return u'請輸入正確格式的郵箱'
        return None

    def DoSubmit(self):
        import commondialog
        msg = self.DoCheck()
        if msg is not None:
            commondialog.ShowNewMessageBox(msg, u'確定')
            return
        g_AccountInfo['Password'] = self.m_PwdEdit.GetText()
        g_AccountInfo['Email'] = self.m_EmailEdit.GetText().strip()
        # 服务端注册接口未就绪：先留桩，明示未接通（用户定的文案）。
        commondialog.ShowNewMessageBox(
            u'伺服器尚未開放註冊，請稍後再試', u'確定')

    def OnMessage(self, msgid):
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
