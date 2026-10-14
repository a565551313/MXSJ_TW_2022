# -*- coding: utf-8 -*-
# login/register 模塊原生重寫版（第二期：現行風格表單）
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
#   4. 規格（用戶 2026-10-14 拍板）：先過協議頁（login/regterms.dlg，
#      服務條款 dlg 的拷貝，寫法照 loginin.CServiceMessageDialog）->
#      表單（login/regform.dlg，照改密頁現行風格新作：帳號/密碼/確認
#      密碼/郵箱四框 + 上一步/確認註冊/返回首頁三按鈕）-> 樁提示。
#      單帳號/密碼 6~16 位字母數字；勾選五帳號時基礎帳號 6~14 位，
#      產生原帳號、_1、_2、_3、_4，共用密碼/郵箱。真註冊仍待服務端。
def _Diag(text):
    """ASCII 階段日誌：每個原生呼叫前/後各寫一筆並關檔。

    不記錄表單值或異常文字；日誌寫入失敗不阻止 UI。
    同步原生呼叫若不返回，只能保留最後階段，不能靠 except 救回死鎖。
    """
    try:
        try:
            f = open("photo\\register_diag.txt", "ab")
        except IOError:
            # 測試副本缺 photo 目錄時退回遊戲工作目錄，不創建/覆蓋資源。
            f = open("register_diag.txt", "ab")
        try:
            f.write((str(text) + "\n").encode("ascii", "replace"))
        finally:
            f.close()
    except Exception:
        pass


def _DiagFailure(stage):
    """Log code locations and a static missing attribute, never exception values."""
    try:
        import sys

        kind, error, trace = sys.exc_info()
        _Diag("%s EXC type=%s" % (stage, kind.__name__))
        names = set()
        count = 0
        while trace is not None and count < 12:
            code = trace.tb_frame.f_code
            names.update(code.co_names)
            filename = code.co_filename.replace("\\", "/").split("/")[-1]
            if filename not in ("register.py", "combmacro.py", "interface.py",
                                "pubinterface.py", "combdialog.py"):
                filename = "other"
            _Diag("%s frame=%s:%s line=%s pc=%s" % (
                stage, filename, code.co_name, trace.tb_lineno, trace.tb_lasti))
            trace = trace.tb_next
            count += 1
        # Python 2.5 has no AttributeError.name. Only emit a name already present
        # in static co_names, not arbitrary exception text or object repr/values.
        if kind is AttributeError and len(error.args) == 1:
            text = error.args[0]
            marker = " has no attribute '"
            if isinstance(text, str) and marker in text and text.endswith("'"):
                attribute = text.rsplit(marker, 1)[1][:-1]
                if (attribute in names and 0 < len(attribute) <= 64
                        and all(c in "abcdefghijklmnopqrstuvwxyz"
                                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
                                for c in attribute)):
                    _Diag("%s missing_attribute=%s" % (stage, attribute))
    except Exception:
        _Diag("%s exception metadata unavailable" % (stage,))


def _ImportRuntime():
    # 首次點擊可能卡在模塊導入，不能等類定義完才開始寫日誌。
    _Diag("module import C_sys begin")
    import C_sys

    _Diag("module import C_sys ready")
    _Diag("module import combdialog begin")
    import combdialog

    _Diag("module import combdialog ready")
    _Diag("module import combmacro begin")
    import combmacro

    _Diag("module import combmacro ready")
    _Diag("module import interface begin")
    import interface

    _Diag("module import interface ready")
    return C_sys, combdialog, combmacro, interface


_Diag("phase2-diag2 module begin")
C_sys, combdialog, combmacro, interface = _ImportRuntime()

g_AccountInfo = {}
g_CDKey = "1234567890123456"
g_ConfirmDlg = None
g_RegisterPanel = None


def ModuleReset():
    global g_AccountInfo
    global g_CDKey
    global g_ConfirmDlg
    global g_RegisterPanel
    g_AccountInfo = {}
    g_CDKey = "1234567890123456"
    g_ConfirmDlg = None
    g_RegisterPanel = None


def IsValid(txt):
    _invalid = (
        '"',
        "'",
        "/",
        "\\",
        "=",
        "+",
        "|",
        ";",
        ":",
        "[",
        "]",
        "{",
        "}",
        "?",
        "*",
        ",",
        "(",
        ")",
        "&",
        "^",
        "%",
        "$",
        "#",
        "!",
        "~",
        "`",
    )
    for c in _invalid:
        if c in txt:
            return False
    return True


def ShowError(err, ecode=0, errmsg=""):
    import commondialog
    import dc_error_code

    if err not in dc_error_code.ERROR_MSG:
        if errmsg:
            msg = errmsg + "-%d" % err
        else:
            msg = MSG_UNKNOWN_ERR + "-%d" % err
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
        combdialog.CCombPanel.__init__(self, parent, "login/confirm.dlg")
        self.Topmost()
        import chatoutput
        import servicedata

        result = [line[1:] for line in servicedata.CONFIRM_MSG.split("\n")]
        output = self.GetObject("output")
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        self.m_PublicTxtBox = chatoutput.COutput(
            self,
            w,
            h,
            0,
            0,
            result,
            txt_font=interface.FontLT14_3,
            txt_color=interface.COLOR_1,
        )
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
                    selectrole.g_SelectRoleDlg.GetObject("btn_Login")
                )
            ShowConfirmDlg(1)
        elif msgid == 2:
            import main
            import sound
            import sounddefine

            sound.Play(sounddefine.PATH_BTN_SOUND)
            main.CloseGame()


# ---------------------------------------------------------------------------
# 註冊第二期：協議頁（regterms.dlg） + 四字段/五帳號表單（regform.dlg）
# ---------------------------------------------------------------------------

# servicedata 缺失時的佔位條款（正式條款待補，見文件頭第 3 點）。
# UI 文字一律用 Big5 字節串（與原版模塊常量逐字節同編碼）。實機教訓：
# 傳 unicode 給原生彈框會在其內部做字節拼接時解碼失敗、靜默無反應。
# 確定
BTN_OK = "\xbdT\xa9w"
# 請輸入正確格式的密碼
MSG_PWD_FORMAT = "\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xae\xe6\xa6\xa1\xaa\xba\xb1K\xbdX"
# 登錄密碼僅可由字母或者數字組成,長度為6~16位。
MSG_PWD_ALNUM = (
    "\xb5n\xbf\xfd\xb1K\xbdX\xb6\xc8\xa5i"
    "\xa5\xd1\xa6r\xa5\xc0\xa9\xce\xaa\xcc\xbc\xc6"
    "\xa6r\xb2\xd5\xa6\xa8,\xaa\xf8\xab\xd7\xac"
    "\xb06~16\xa6\xec\xa1C"
)
# 兩次輸入的密碼不匹配
MSG_PWD_MISMATCH = (
    "\xa8\xe2\xa6\xb8\xbf\xe9\xa4J\xaa\xba\xb1K\xbdX\xa4\xa3\xa4\xc7\xb0t"
)
# 請輸入正確格式的郵箱
MSG_EMAIL_FORMAT = (
    "\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xae\xe6\xa6\xa1\xaa\xba\xb6l\xbdc"
)
# 伺服器尚未開放註冊，請稍後再試
MSG_STUB = (
    "\xa6\xf8\xaaA\xbe\xb9\xa9|\xa5\xbc\xb6}"
    "\xa9\xf1\xb5\xf9\xa5U\xa1A\xbd\xd0\xb5y"
    "\xab\xe1\xa6A\xb8\xd5"
)
# 未知錯誤
MSG_UNKNOWN_ERR = "\xa5\xbc\xaa\xbe\xbf\xf9\xbb~"
# 註冊提交出錯，請回報管理員
MSG_SUBMIT_ERR = (
    "\xb5\xf9\xa5U\xb4\xa3\xa5\xe6\xa5X\xbf\xf9"
    "\xa1A\xbd\xd0\xa6^\xb3\xf8\xba\xde\xb2z"
    "\xad\xfb"
)
# 請輸入正確格式的帳號
MSG_ACC_FORMAT = (
    "\xbd\xd0\xbf\xe9\xa4J\xa5\xbf\xbdT\xae\xe6\xa6\xa1\xaa\xba\xb1b\xb8\xb9"
)
# 帳號只能為數字或字母
PROMPT_ACC_ALNUM = (
    "#Y\xb1b\xb8\xb9\xa5u\xaf\xe0\xac\xb0\xbc\xc6\xa6r\xa9\xce\xa6r\xa5\xc0"
)
# 密碼只能為數字或字母
PROMPT_PWD_ALNUM = "#Y\xb1K\xbdX\xa5u\xaf\xe0\xac\xb0\xbc\xc6\xa6r\xa9\xce\xa6r\xa5\xc0"
# 單帳號模式提示
HINT_FORM = (
    "\xb3\xe6\xb1b\xb8\xb9\xbc\xd2\xa6\xa1\xa1G"
    "#r\xb1b\xb8\xb9\xa9M\xb1K\xbdX"
    "\xac\xb06~16\xa6\xec\xa6r\xa5\xc0"
    "\xa9\xce\xbc\xc6\xa6r\xa1F\xbd\xd0\xb6\xf1"
    "\xbcg\xb1`\xa5\xce\xb6l\xbdc\xa1C"
    "#r\xa4\xc4\xbf\xef\xa4U\xa4\xe8\xa5i"
    "\xa4@\xa6\xb8\xb5\xf9\xa5U\xa4\xad\xad\xd3"
    "\xb1b\xb8\xb9\xa1C"
)

# 五帳號模式的基礎帳號須為6~14位字母或數字，請縮短帳號以預留_1至_4後綴。
MSG_ACC_BATCH_FORMAT = (
    "\xa4\xad\xb1b\xb8\xb9\xbc\xd2\xa6\xa1\xaa\xba"
    "\xb0\xf2\xc2\xa6\xb1b\xb8\xb9\xb6\xb7\xac\xb0"
    "6~14\xa6\xec\xa6r\xa5\xc0\xa9\xce"
    "\xbc\xc6\xa6r\xa1A\xbd\xd0\xc1Y\xb5u"
    "\xb1b\xb8\xb9\xa5H\xb9w\xafd_1"
    "\xa6\xdc_4\xab\xe1\xba\xf3\xa1C"
)

# 五帳號模式提示：6~14 位基礎帳號、原帳號及 _1~_4、共用密碼和郵箱。
HINT_FORM_FIVE = (
    "\xa4\xad\xb1b\xb8\xb9\xbc\xd2\xa6\xa1\xa1G"
    "#r\xb0\xf2\xc2\xa6\xb1b\xb8\xb96~"
    "14\xa6\xec\xa6r\xa5\xc0\xa9\xce\xbc\xc6"
    "\xa6r\xa1A\xb1K\xbdX6~16"
    "\xa6\xec\xa1C#r\xb2\xa3\xa5\xcd\xad\xec"
    "\xb1b\xb8\xb9\xa4\xce_1\xa6\xdc_4"
    "\xab\xe1\xba\xf3\xa1A\xa4\xad\xad\xd3\xb1b"
    "\xb8\xb9\xa6@\xa5\xce\xb1K\xbdX\xa9M"
    "\xb6l\xbdc\xa1C"
)

# #r#r以下為待註冊的五個帳號（尚未註冊）：#r
MSG_BATCH_PLAN = (
    "#r#r\xa5H\xa4U\xac\xb0\xab\xdd"
    "\xb5\xf9\xa5U\xaa\xba\xa4\xad\xad\xd3\xb1b"
    "\xb8\xb9\xa1]\xa9|\xa5\xbc\xb5\xf9\xa5U"
    "\xa1^\xa1G#r"
)

# 註冊完成！以下%d個帳號已建立：#r
MSG_COMPLETE_HEADER = (
    "\xb5\xf9\xa5U\xa7\xb9\xa6\xa8\xa1I\xa5H"
    "\xa4U%d\xad\xd3\xb1b\xb8\xb9\xa4w"
    "\xab\xd8\xa5\xdf\xa1G#r"
)

# 原生登入註冊勾選框皮膚（GBK 路徑，ui_res_style1 實證）
IMG_FIVE_CHECK = (
    "combdialog/\xb5"
    "\xc7\xc2\xbc\xd7\xa2\xb2\xe1/\xb0\xb4\xc5\xa5"
    "/\xb9\xb4\xd1\xa1\xbf\xf2.igs"
)

# servicedata 缺失時的佔位條款（Big5 字節串，正式條款待補，見文件頭）。
TERMS_FALLBACK = [
    ("\xb7|\xad\xfb\xaaA\xb0\xc8\xb1\xf8\xb4\xda"),
    "",
    (
        "\xa1]\xb4\xfa\xb8\xd5\xa6\xfb\xa6\xec\xa1^"
        "\xad\xec\xb1\xf8\xb4\xda\xa4\xe5\xa5\xbb\xa5\xd1"
        " servicedata"
        " \xbc\xd2\xb2\xd5\xb4\xa3\xa8\xd1\xa1A"
    ),
    (
        "\xa5\xbb\xb4\xfa\xb8\xd5\xa5]\xa5\xbc\xa5]"
        "\xa7t\xb8\xd3\xbc\xd2\xb2\xd5\xa1A\xa5\xbf"
        "\xa6\xa1\xb1\xf8\xb4\xda\xab\xdd\xb8\xc9\xa1C"
    ),
    "",
    (
        "\xc2I\xa1u\xa7\xda\xa6P\xb7N\xa1v"
        "\xc4~\xc4\xf2\xb6\xf1\xbcg\xb5\xf9\xa5U"
        "\xb8\xea\xae\xc6\xa1A\xc2I\xa1u\xa7\xda"
        "\xa9\xda\xb5\xb4\xa1v\xaa\xf0\xa6^\xa1C"
    ),
]


def _PlayBtnSound():
    import sound

    sound.Play("action/button.wav")


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

        return [line[1:] for line in servicedata.SERVICE_MSG.split("\n")]
    except Exception:
        return list(TERMS_FALLBACK)


class CRegTermsPanel(combdialog.CCombPanel):
    """協議頁：login/regterms.dlg（服務條款 dlg 的拷貝），寫法照
    loginin.CServiceMessageDialog。msgid 1=我同意（進表單），其餘=回首頁。
    """

    def __init__(self, parent):
        _Diag("terms layout begin")
        combdialog.CCombPanel.__init__(self, parent, "login/regterms.dlg")
        _Diag("terms layout ready")
        _Diag("terms import chatoutput begin")
        import chatoutput

        _Diag("terms import chatoutput ready")
        _Diag("terms source begin")
        result = _LoadTermsLines()
        _Diag("terms source ready")
        _Diag("terms anchor begin")
        output = self.GetObject("loc_msg")
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        _Diag("terms anchor ready")
        _Diag("terms geometry w=%s h=%s" % (w, h))
        # 原 COutput.__init__ 將可用行寬設為 w-20（entry 4832 pc78..88）。
        # 非正行寬/高度不送進原生排版；這是防禦，不代表本次卡屏根因。
        if w <= 20 or h <= 0:
            raise ValueError("invalid terms geometry")
        _Diag("terms output create begin")
        self.m_PublicTxtBox = chatoutput.COutput(
            self,
            w,
            h,
            0,
            0,
            result,
            txt_font=interface.FontLT14_3,
            txt_color=interface.COLOR_1,
        )
        _Diag("terms output create ready")
        _Diag("terms output position begin")
        self.m_PublicTxtBox.SetPos(x, y)
        _Diag("terms output position ready")
        _Diag("terms output cursor begin")
        self.m_PublicTxtBox.SetChatCursor(0)
        _Diag("terms output cursor ready")
        _Diag("terms output reset begin")
        self.m_PublicTxtBox.ResetFromCursor()
        _Diag("terms output reset ready")
        _Diag("terms output scroll begin")
        self.m_PublicTxtBox.ScrollTo(0)
        _Diag("terms output scroll ready")

    def OnMessage(self, msgid):
        _Diag("terms msgid=%s" % (msgid,))
        _PlayBtnSound()
        if msgid == 1:
            Step(1)
        else:
            _ReturnHome()
        return True


_ACCOUNT_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _IsAsciiAlnum(txt):
    if not txt:
        return False
    for char in txt:
        if char not in _ACCOUNT_CHARS:
            return False
    return True


def BuildRegistrationAccounts(account, register_five=False):
    """只生成候選名稱，不代表註冊成功；下劃線僅由自動後綴產生。"""
    maximum = 14 if register_five else 16
    if len(account) < 6 or len(account) > maximum or not _IsAsciiAlnum(account):
        raise ValueError("invalid base account")
    accounts = [account]
    if register_five:
        accounts.extend([account + "_%d" % n for n in range(1, 5)])
    return accounts


class CRegAccountEdit(interface.CEdit):
    """帳號輸入框：只允許數字或字母（照 chgpwd.CPwdEdit 的打法）。"""

    def AddChar(self, c):
        if _IsAsciiAlnum(c):
            interface.CEdit.AddChar(self, c)
        else:
            import usermacro

            usermacro.PROMPT_MSG(PROMPT_ACC_ALNUM)


class CRegPwdEdit(interface.CEdit):
    """密碼輸入框：只允許數字或字母。"""

    def AddChar(self, c):
        if _IsAsciiAlnum(c):
            interface.CEdit.AddChar(self, c)
        else:
            import usermacro

            usermacro.PROMPT_MSG(PROMPT_PWD_ALNUM)


def _CreateFormEdit(parent, edit_class, name, limit):
    """Same native CEDIT call; separate lookup, font, factory and limit markers."""
    stage = "form edit %s" % (name,)
    _Diag("%s anchor begin" % (stage,))
    anchor = parent.GetObject(name)
    if anchor is None:
        _Diag("%s anchor missing" % (stage,))
        raise ValueError("missing form edit anchor")
    _Diag("%s anchor ready" % (stage,))
    _Diag("%s factory resolve begin" % (stage,))
    factory = combmacro.CEDIT
    _Diag("%s factory resolve ready" % (stage,))
    _Diag("%s font resolve begin" % (stage,))
    font = interface.FONT_EDIT
    _Diag("%s font resolve ready" % (stage,))
    _Diag("%s factory call begin" % (stage,))
    edit = factory(edit_class, name, parent, 0, font, linecolor=0)
    _Diag("%s factory call ready" % (stage,))
    _Diag("%s limit begin" % (stage,))
    edit.SetLimit(limit)
    _Diag("%s limit ready" % (stage,))
    return edit


class CRegFormPanel(combdialog.CCombPanel):
    """表單頁（login/regform.dlg）：msgid 1=上一步（回協議），
    2=確認註冊（校驗後留樁），3=返回首頁，4=切換註冊五個帳號。
    四框：帳號/密碼/確認密碼/郵箱；勾選默認關閉。

    """

    def __init__(self, parent):
        _Diag("form layout begin")
        combdialog.CCombPanel.__init__(self, parent, "login/regform.dlg")
        _Diag("form layout ready")
        _Diag("form import C_object begin")
        import C_object

        _Diag("form import C_object ready")
        _Diag("form account begin")
        self.m_AccountEdit = _CreateFormEdit(
            self, CRegAccountEdit, "account", 16
        )
        _Diag("form account ready")
        _Diag("form password begin")
        self.m_PwdEdit = _CreateFormEdit(
            self, CRegPwdEdit, "pwd", 16
        )
        self.m_PwdEdit.m_IsPassword = True
        _Diag("form password ready")
        _Diag("form confirmation begin")
        self.m_PwdEdit2 = _CreateFormEdit(
            self, CRegPwdEdit, "pwd2", 16
        )
        self.m_PwdEdit2.m_IsPassword = True
        _Diag("form confirmation ready")
        _Diag("form email begin")
        self.m_EmailEdit = _CreateFormEdit(
            self, interface.CEdit, "email", 50
        )
        _Diag("form email ready")
        _Diag("form tab begin")
        self.m_AccountEdit.SetNextEdit(self.m_PwdEdit)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_EmailEdit)
        self.m_EmailEdit.SetNextEdit(self.m_AccountEdit)
        _Diag("form tab ready")
        _Diag("form hint begin")
        self.m_Text = combmacro.CRICHTEXT(
            C_object.CRichTextObject,
            "txt",
            self,
            HINT_FORM,
            interface.FONT_EDIT,
            interface.COLOR_EDIT,
        )
        _Diag("form hint ready")
        _Diag("form checkbox begin")
        self.m_FiveCheck = combmacro.CIMGCHECKBOX(
            interface.CImageCheckBox, "chk_five", self, IMG_FIVE_CHECK, True, 4
        )
        # 原生工廠綁 .dlg 錨點，放大命中區使方框/文字都可點擊。
        (w, h) = self.GetObject("chk_five").GetSize()
        self.m_FiveCheck.SetSize(w, h)
        _Diag("form checkbox ready")
        self.m_RegistrationRequests = []
        # 只有日後真實請求送出時才可設置 pending；留樁不設置，不能假報成功。
        self.m_PendingAccounts = None
        _Diag("form defaults begin")
        self.SetRegisterFive(False)
        _Diag("form defaults ready")
        _Diag("form focus begin")
        self.m_AccountEdit.Active(True)
        _Diag("form focus ready")

    def SetRegisterFive(self, enabled):
        self.m_FiveCheck.SetCheck(bool(enabled))
        if enabled:
            self.m_AccountEdit.SetLimit(14)
            self.m_Text.SetText(HINT_FORM_FIVE)
        else:
            self.m_AccountEdit.SetLimit(16)
            self.m_Text.SetText(HINT_FORM)
        # 已核對原版 SetLimit 只改 m_Limit，絕不截掉已有的輸入。

    def CheckEmail(self, email):
        if len(email) < 5 or len(email) > 50:
            return False
        import re

        patt = re.compile("^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$")
        return patt.match(email) is not None

    def DoCheck(self):
        """校验通过返回 None，否则返回要提示的文案（口径同旧版 DoCheck）。"""
        account = self.m_AccountEdit.GetText()
        register_five = self.m_FiveCheck.IsSelected()
        maximum = 14 if register_five else 16
        if len(account) < 6 or len(account) > maximum or not _IsAsciiAlnum(account):
            self.m_AccountEdit.Active(True)
            if register_five:
                return MSG_ACC_BATCH_FORMAT
            return MSG_ACC_FORMAT
        pwd = self.m_PwdEdit.GetText()
        if len(pwd) < 6 or len(pwd) > 16:
            self.m_PwdEdit.Active(True)
            return MSG_PWD_FORMAT
        if not _IsAsciiAlnum(pwd):
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

        _Diag("submit start")
        self.m_RegistrationRequests = []
        self.m_PendingAccounts = None
        try:
            msg = self.DoCheck()
            _Diag("check done fail=%s" % (msg is not None))
            if msg is not None:
                commondialog.ShowNewMessageBox(msg, BTN_OK)
                _Diag("fail box shown")
                return
            accounts = BuildRegistrationAccounts(
                self.m_AccountEdit.GetText(), self.m_FiveCheck.IsSelected()
            )
            pwd = self.m_PwdEdit.GetText()
            email = self.m_EmailEdit.GetText().strip()
            self.m_RegistrationRequests = [
                {"Account": account, "Password": pwd, "Email": email}
                for account in accounts
            ]
            # 保留 loginin 用的單個預填帳號接口，第一個仍是基礎帳號。
            g_AccountInfo["Account"] = accounts[0]
            g_AccountInfo["Password"] = pwd
            g_AccountInfo["Email"] = email
            _Diag("prepared count=%d" % len(accounts))
            # 未接服務端，不設 pending，不調完成回調；文案明示尚未註冊。
            msg = MSG_STUB
            if len(accounts) == 5:
                msg += MSG_BATCH_PLAN + "#r".join(accounts)
            commondialog.ShowNewMessageBox(msg, BTN_OK)
            _Diag("stub box shown")
        except Exception:
            import sys

            _Diag("EXC type=%s" % sys.exc_info()[0].__name__)
            try:
                commondialog.ShowMessageBox(MSG_SUBMIT_ERR, BTN_OK)
            except Exception:
                _Diag("err box failed too")

    def OnRegistrationComplete(self, registered_accounts):
        """預留給真實服務端回覆：五個全成功才報五個；留樁永遠不走此路。

        接通時須在送出真實請求後記錄 m_PendingAccounts（帳號列表，不含密碼）。
        只接收完整成功列表；部分成功、重複、陌生/過期回覆均不能報全成功。
        """
        expected = self.m_PendingAccounts
        if self is not g_RegisterPanel:
            return False
        if not expected or not isinstance(registered_accounts, (list, tuple)):
            return False
        if len(expected) not in (1, 5):
            return False
        if len(registered_accounts) != len(expected):
            return False
        if sorted(registered_accounts) != sorted(expected):
            return False
        import commondialog

        msg = MSG_COMPLETE_HEADER % len(expected) + "#r".join(expected)
        commondialog.ShowNewMessageBox(msg, BTN_OK)
        self.m_PendingAccounts = None
        _Diag("registration complete count=%d" % len(expected))
        return True

    def OnMessage(self, msgid):
        _Diag("form msgid=%s" % (msgid,))
        _PlayBtnSound()
        if msgid == 1:
            self.m_PendingAccounts = None
            Step(0)
        elif msgid == 2:
            self.DoSubmit()
        elif msgid == 3:
            self.m_PendingAccounts = None
            _ReturnHome()
        elif msgid == 4:
            # CImageCheckBox.LeftUp 先發消息，再自動翻轉；manual=True 交給
            # 本處翻轉一次，避免一次點擊勾上又自動取消。
            self.SetRegisterFive(not self.m_FiveCheck.IsSelected())
        return True


_PANELS = [CRegTermsPanel, CRegFormPanel]


def _RecoverEntry():
    # 首頁的原入口先 Show(False)，僅對會返回的 Python 異常作盡力回復。
    # 不清除仍正常顯示的舊註冊頁，不聲稱能撤銷部分原生構造或中止原生阻塞。
    _Diag("entry recovery begin")
    try:
        C_sys.InputSecrecy(0)
        _Diag("entry recovery secrecy ready")
    except Exception:
        _Diag("entry recovery secrecy failed")
    try:
        _Diag("entry recovery home begin")
        import mainpage

        mainpage.Show(True)
        _Diag("entry recovery home ready")
    except Exception:
        _Diag("entry recovery home failed")


def Step(n):
    global g_RegisterPanel
    _Diag("step=%s begin" % (n,))
    try:
        panel = _PANELS[n](interface.DialogPanel)
    except Exception:
        _DiagFailure("step=%s" % (n,))
        if g_RegisterPanel is None:
            _RecoverEntry()
        return False
    # 構造完成才發布；回上一頁/下一頁失敗時，原頁引用保持不動。
    g_RegisterPanel = panel
    _Diag("step=%s ready" % (n,))
    return True


def Show(s):
    global g_RegisterPanel
    if s:
        _Diag("phase2-diag2 show open begin")
        try:
            _Diag("input secrecy on begin")
            C_sys.InputSecrecy(1)
            _Diag("input secrecy on ready")
            return Step(0)
        except Exception:
            import sys

            _Diag("show EXC type=%s" % (sys.exc_info()[0].__name__,))
            if g_RegisterPanel is None:
                _RecoverEntry()
            return False
    else:
        _Diag("show close begin")
        g_RegisterPanel = None
        C_sys.InputSecrecy(0)
        _Diag("show close ready")


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

        path = "photo\\register"
        if os.path.exists(path):
            import shutil

            shutil.rmtree(path)
    except Exception:
        pass


_Diag("phase2-diag2 module ready")
