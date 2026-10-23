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
#   3. 條款文本取外部模塊 servicedata.SERVICE_MSG。2026-10-15 實測更正：
#      該模塊在本版 script.fls 內（條目 1931 自報 script\data\servicedata.py，
#      SERVICE_MSG/SERVICE_MSG2 兩套按 main.g_LangVersion 切換），所以真機走的是
#      正式條款；缺失兜底只在離線桩件環境生效。但歸檔裡的 servicedata **沒有**
#      CONFIRM_MSG（其 pyc 名字表只有兩個 SERVICE_*，兩側歸檔亦無任何定義者），
#      **每行末尾補 `#r`**：原版寫法是 `[s + '#r' for s in MSG.split('\n')]`，
#      反編譯器把 py2 列表推導的隱藏累加器 `_[1]` 印成了下標，舊版照抄成
#      `line[1:]`（吃掉每行首字符）——2026-10-23 用 marshal 反彙編核實後改正。
#      舊客戶端 CConfirm 直接取該屬性屬構造即報錯的死路，故本文件為確認框另設
#      CONFIRM_FALLBACK 明示兜底；包內一旦補上該常量，自動改用原文。
#   4. 規格（用戶 2026-10-14 拍板，2026-10-22 換版式）：先過協議頁
#      （login_new/agreement.dlg，寫法照 loginin.CServiceMessageDialog）->
#      表單（login_new/register2027.dlg：edt_account/edt_Pwd/edt_Pwd_1/
#      edt_email 四框 + btn_fiveaccount/btn_isee 兩個勾選 +
#      btn_Back/btn_register 兩按鈕）-> 樁提示。
#      協議頁另有用戶後加的 btn_back（回登錄首頁），消息號按版式現讀。
#      單帳號/密碼 6~16 位字母數字；勾選五帳號時基礎帳號 6~14 位，
#      產生原帳號、_1、_2、_3、_4，共用密碼/郵箱。真註冊仍待服務端。
#   5. 字色（2026-10-22 第二輪，用戶實機反饋）：四框與顯示行必須是白字。
#      .dlg 裡的顏色屬性搬不過來——輸入框/顯示行是腳本用 CEDIT / CRICHTEXT
#      在版式錨點上另建的控件，顏色只認構造參數；照 loginin.py 登錄頁
#      （edt_Name / edt_Pwd 都傳 16777215）預設白字，並在版式錨點有 GetColor()
#      且非 0 時改用版式值，方便日後在佈局裡直接改色。
import C_sys
import combdialog
import combmacro
import interface

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

        result = _LoadConfirmLines()
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
# 五帳號模式的基礎帳號須為6~14位字母或數字，請縮短帳號以預留_1至_4後綴。
MSG_ACC_BATCH_FORMAT = (
    "\xa4\xad\xb1b\xb8\xb9\xbc\xd2\xa6\xa1\xaa\xba"
    "\xb0\xf2\xc2\xa6\xb1b\xb8\xb9\xb6\xb7\xac\xb0"
    "6~14\xa6\xec\xa6r\xa5\xc0\xa9\xce"
    "\xbc\xc6\xa6r\xa1A\xbd\xd0\xc1Y\xb5u"
    "\xb1b\xb8\xb9\xa5H\xb9w\xafd_1"
    "\xa6\xdc_4\xab\xe1\xba\xf3\xa1C"
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

# ---------------------------------------------------------------------------
# 版式（2026-10-22 用戶重新設計）：兩頁都在 login_new/ 下。
# 表單頁的勾選框用的是版式自帶的三態按鈕（用戶從登錄頁整塊複製），
# 不再由腳本疊 CImageCheckBox——原生 .dlg 勾選走 GetObject(...).IsSelected()
# / SetSelect(...)，這正是 loginin.py（entry 4806）在用的那兩個名字。
# ---------------------------------------------------------------------------
DLG_TERMS = "login_new/agreement.dlg"
DLG_FORM = "login_new/register2027.dlg"

# 勾選按鈕的消息號：版式裡原本兩個都是 50，分不出點的是哪個。
# 交付的 register2027_msg.dlg 把「同意」改成 51；腳本兩種都認。
ID_FIVE_CHECK = 50
ID_CONSENT_CHECK = 51

# 表單提示（版式 txt_Wrong，90x20 的小字框）只放短句，詳細原因仍走彈框。
# 請先同意協議
LABEL_CONSENT = "\xbd\xd0\xa5\xfd\xa6\x50\xb7\x4e\xa8\xf3\xc4\xb3"
# 帳號6~16位
LABEL_ACC = "\xb1\x62\xb8\xb9\x36\x7e\x31\x36\xa6\xec"
# 帳號6~14位
LABEL_ACC_FIVE = "\xb1\x62\xb8\xb9\x36\x7e\x31\x34\xa6\xec"
# 密碼6~16位
LABEL_PWD = "\xb1\x4b\xbd\x58\x36\x7e\x31\x36\xa6\xec"
# 密碼只能字母數字
LABEL_PWD_ALNUM = (
    "\xb1\x4b\xbd\x58\xa5\x75\xaf\xe0\xa6\x72"
    "\xa5\xc0\xbc\xc6\xa6\x72"
)
# 兩次密碼不同
LABEL_PWD_DIFF = "\xa8\xe2\xa6\xb8\xb1\x4b\xbd\x58\xa4\xa3\xa6\x50"
# 郵箱格式錯誤
LABEL_EMAIL = "\xb6\x6c\xbd\x63\xae\xe6\xa6\xa1\xbf\xf9\xbb\x7e"
# 基礎帳號6~14位（勾上「註冊五個賬號」後的常駐提示）
LABEL_FIVE_MODE = "\xb0\xf2\xc2\xa6\xb1\x62\xb8\xb9\x36\x7e\x31\x34\xa6\xec"

# 請勾選「同意用戶協議和註冊條款」（措辭照 loginin.py 的 chk_agree 提示）
MSG_CONSENT = (
    "\xbd\xd0\xa4\xc4\xbf\xef\xa1\x75"
    "\xa6\x50\xb7\x4e\xa5\xce\xa4\xe1"
    "\xa8\xf3\xc4\xb3\xa9\x4d\xb5\xf9"
    "\xa5\x55\xb1\xf8\xb4\xda\xa1\x76"
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


# 本版歸檔沒有 servicedata.CONFIRM_MSG（實測：entry 1931 的 pyc 名字表只有
# SERVICE_MSG / SERVICE_MSG2，兩個歸檔裡也都找不到任何定義者），所以確認框必須
# 有明示兜底，否則 CConfirm 構造即 AttributeError——舊客戶端就是這條死路。
CONFIRM_FALLBACK = [
    "\xbdT\xbb{\xb5\xf9\xa5U",
    "",
    (
        "\xbdT\xa9w\xadn\xb5\xf9\xa5U\xb3o\xad\xd3\xb1b\xb8\xb9\xb6\xdc"
        "\xa1H"
    ),
    "",
    (
        "\xa1]\xa5\xbb\xaa\xa9\xa5\xbb\xc2k\xc0\xc9\xa5\xbc\xb4\xa3\xa8"
        "\xd1 servicedata.CONFIRM_MSG\xa1A\xa6\xb9\xac\xb0\xa9\xfa\xa5"
        "\xdc\xb0\xc2\xa9\xb3\xa4\xe5\xae\xd7\xa1F\xb8\xc9\xa4W\xab\xe1"
        "\xa6\xdb\xb0\xca\xa7\xef\xa5\xce\xad\xec\xa4\xe5\xa1C\xa1^"
    ),
]


def _Diag(text):
    """第一期診斷：把註冊流程的關鍵節點寫到 photo\\register_diag.txt。

    客戶端會吞掉 OnMessage 裡的腳本異常（界面上只是「沒反應」），
    沒有這支日誌就無從定位。純 ASCII 寫入，永不拋錯。
    """
    try:
        f = open("photo\\register_diag.txt", "ab")
        f.write((str(text) + "\n").encode("ascii", "replace"))
        f.close()
    except Exception:
        pass


def _DiagFailure(where):
    """記「哪裡炸了」，只記異常類型名，絕不記異常值（可能含玩家輸入）。"""
    try:
        import sys

        exc = sys.exc_info()[0]
        name = exc is not None and exc.__name__ or "unknown"
        _Diag("%s failed type=%s" % (where, name))
    except Exception:
        _Diag("%s failed (no metadata)" % where)


def _RecoverEntry():
    """開頁失敗時把客戶端撈回來：解除輸入遮蔽、回首頁。

    半開的註冊界面會讓人以為號還能不能填，所以寧可退回首頁也不能卡在這裡。
    每一步都單獨兜底，回收本身出錯也不能再拋。
    """
    _Diag("entry recovery begin")
    try:
        C_sys.InputSecrecy(0)
        _Diag("entry recovery secrecy ready")
    except Exception:
        _Diag("entry recovery secrecy failed")
    try:
        import mainpage

        mainpage.Show(True)
        _Diag("entry recovery home ready")
    except Exception:
        _Diag("entry recovery home failed")


def _EditFont():
    """編輯框字體：照 chgpwd.py 用 interface.FONT_EDIT；萬一本版客戶端沒這個
    常量，退回舊版實機走通時用的 FontLT14_3，並把實際選了哪個寫進日誌。"""
    font = getattr(interface, "FONT_EDIT", None)
    if font is None:
        _Diag("font fallback FontLT14_3")
        return interface.FontLT14_3
    _Diag("font FONT_EDIT")
    return font


# 白字 0xFFFFFF。實證：loginin.py 登錄頁的 edt_Name 用
# CUserEdit(self, 16777215, ...)、edt_Pwd 用
# combmacro.CEDIT(CPasswordEdit, 'edt_Pwd', self, 16777215, ...)，
# 兩處都是白字；註冊頁四框與提示行照這個來。
COLOR_TEXT_WHITE = 16777215


def _LayoutColor(parent, name):
    """取版式錨點的字色；版式沒寫（0/取不到）就用白字。

    為什麼要在這裡讀：CEDIT / CRICHTEXT 建的是腳本自己的控件，字色只認
    **構造參數**，.dlg 裡給 CBox 加的顏色屬性不會自動帶過來——2026-10-22
    用戶在佈局裡加 ICOLOR 沒生效就是這個原因。原版也這麼做：dlgitembill1
    的 CreateBookAmountEdit 先 GetObject('txt_num').GetColor() 再傳給 CEDIT。
    取不到 API 不是錯，退回白字即可（舊版這裡退回黑色，實機反饋要白的）。
    """
    try:
        obj = parent.GetObject(name)
        if obj is not None:
            color = obj.GetColor()
            if color:
                _Diag("color %s layout=%s" % (name, color))
                return color
    except Exception:
        _Diag("color %s api missing" % name)
    _Diag("color %s fallback white" % name)
    return COLOR_TEXT_WHITE


def _CreateFormEdit(parent, edit_class, name, limit, font):
    """按 chgpwd.py 的 CEDIT 調用建編輯框，但先確認版式錨點在不在。

    register2027.dlg 沒導入/導入路徑填錯時，原生工厂只會讓界面「點了沒反應」；
    這裡先查 GetObject，缺就留一條明確的 anchor missing 記錄再拋。
    """
    _Diag("form edit %s anchor begin" % name)
    if parent.GetObject(name) is None:
        _Diag("form edit %s anchor missing" % name)
        raise ValueError("missing form edit anchor")
    _Diag("form edit %s factory begin" % name)
    # 顏色優先取版式錨點，否則白字（照登錄頁）；linecolor 與登錄頁一致取 0。
    edit = combmacro.CEDIT(
        edit_class, name, parent, _LayoutColor(parent, name), font, linecolor=0
    )
    _Diag("form edit %s factory ready" % name)
    edit.SetLimit(limit)
    _Diag("form edit %s ready" % name)
    return edit


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


def _RichLines(lines):
    """把純文本行變成 COutput 要的富文本行：每行末尾補 `#r`（換行標記）。

    原版四處寫法一致（`CRegPanel1`/`CConfirm`/`CServiceMessageDialog`/
    `mainpage._WriteTxtBox` 的資料來源）：
        result = [s + '#r' for s in servicedata.SERVICE_MSG.split('\n')]
    反編譯器把 py2 列表推導的隱藏累加器印成了 `_[1]`，2026-10-22 那版照抄成
    `line[1:]`，結果是每行少一個字、還沒有換行標記。2026-10-23 反彙編
    entry 4007/4806 的 `__init__` 核實：`LOAD_CONST '#r'` + `BINARY_ADD`，
    就是 `s + '#r'`。這裡按原版重寫。
    """
    return [line + "#r" for line in lines]


def _LoadTermsLines():
    try:
        import servicedata

        return _RichLines(servicedata.SERVICE_MSG.split("\n"))
    except Exception:
        return _RichLines(TERMS_FALLBACK)


def _LoadConfirmLines():
    """確認框正文：優先取包內 servicedata.CONFIRM_MSG。

    本版歸檔裡沒有這個常量（實測見 CONFIRM_FALLBACK 上方註釋），所以缺失時
    退回明示兜底；舊客戶端那種「不判空直接取屬性」的寫法會導致構造即
    AttributeError，這裡不再照抄。包內一旦補上該常量，自動改用原文。"""
    try:
        import servicedata

        return _RichLines(servicedata.CONFIRM_MSG.split("\n"))
    except Exception:
        return _RichLines(CONFIRM_FALLBACK)


class CRegTermsPanel(combdialog.CCombPanel):
    """協議頁：login_new/agreement.dlg，寫法照 loginin.CServiceMessageDialog。
    msgid 1=同意（進表單），其餘=回首頁（新版式裡 2 是「拒絕」）。
    """

    def __init__(self, parent):
        # 換版式後日誌第一行帶版本標記：用戶只看這一行就能確認新腳本已生效。
        # 尾碼 b = 第二輪（白字 + btn_back）。
        _Diag("terms layout begin build=2027-10-22c")
        combdialog.CCombPanel.__init__(self, parent, DLG_TERMS)
        _Diag("terms layout ready")
        # btn_back 是用戶在 agreement.dlg 本機加的，消息號以版式為準；
        # 沒這個按鈕就是 None（老版式照樣能跑）。
        self.m_BackMsgId = _LayoutMsgId(self, "btn_back")
        if self.m_BackMsgId == 1:
            # 1 是「我同意」，撞號會讓同意永遠進不了表單，日誌裡必須看得見。
            _Diag("terms WARN btn_back msgid=1 conflicts with agree")
        import chatoutput

        result = _LoadTermsLines()
        _Diag("terms anchor begin")
        output = self.GetObject("loc_msg")
        if output is None:
            _Diag("terms anchor missing")
            raise ValueError("missing terms anchor loc_msg")
        (w, h) = output.GetSize()
        (x, y) = output.GetPos()
        if w <= 0 or h <= 0:
            _Diag("terms geometry invalid %sx%s" % (w, h))
            raise ValueError("invalid terms geometry")
        _Diag("terms anchor ready")
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
        self.m_PublicTxtBox.ScrollTo(0)
        _Diag("terms ready")

    def OnMessage(self, msgid):
        _PlayBtnSound()
        _Diag("terms msgid=%s" % (msgid,))
        if msgid == 1:
            Step(1)
        elif self.m_BackMsgId is not None and msgid == self.m_BackMsgId:
            _Diag("terms btn_back -> home")
            _ReturnHome()
        else:
            # 新版式 2=拒絕；其餘（含日後再加的按鈕）一律回登錄首頁。
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


def _LayoutMsgId(parent, name):
    """讀版式按鈕自己的消息號；取不到就返回 None。

    btn_back 是用戶後加進 agreement.dlg 的，腳本寫死消息號就會和他在佈局裡
    填的對不上。原生對象帶 ``m_MsgID``（loginin.py / mainpage.py 的
    OnButtonEnter 就是拿 ```btn.m_MsgID`` 判斷），照讀即可。
    """
    try:
        obj = parent.GetObject(name)
        if obj is None:
            _Diag("msgid anchor missing %s" % name)
            return None
        msgid = obj.m_MsgID
        _Diag("msgid %s=%s" % (name, msgid))
        return msgid
    except Exception:
        _Diag("msgid %s api missing" % name)
        return None


class _LayoutCheck(object):
    """版式裡的勾選按鈕（用戶從登錄頁整塊複製的三態按鈕）。

    原生 .dlg 勾選是``GetObject(name).IsSelected() / SetSelect(bool)``，
    而且**引擎自己負責翻轉**——實機走通的 loginin.py（entry 4806）在
    OnMessage 裡只讀 ``GetObject('chk_agree').IsSelected()``，從不自己翻；
    它還同時讀 ``btn_Protect``，說明多個勾選框互不排斥。所以這裡照抄：
    點擊消息只用來刷新提示，狀態一律問引擎要，腳本絕不手動翻（手動翻會和
    引擎各翻一次＝看起來沒反應）。

    某版客戶端若沒有這兩個方法，就退回腳本自己記狀態（界面上不會變，
    但流程仍能走完），並把退化寫進日誌，不讓整頁開不起來。
    """

    def __init__(self, obj, name):
        self.obj = obj
        self.name = name
        self.native = False
        self.state = False
        try:
            self.state = bool(obj.IsSelected())
            self.native = True
            _Diag("check %s ready=%d" % (name, int(self.state)))
        except Exception:
            _Diag("check %s read api missing" % name)

    def Get(self):
        if self.native:
            try:
                self.state = bool(self.obj.IsSelected())
                return self.state
            except Exception:
                _Diag("check %s read failed" % self.name)
                self.native = False
        return self.state

    def Set(self, flag):
        """只在初始化/腳本主動改模式時用；點擊一律交給引擎。"""
        self.state = bool(flag)
        if self.native:
            try:
                self.obj.SetSelect(self.state)
            except Exception:
                _Diag("check %s write api missing" % self.name)
                self.native = False


class CRegFormPanel(combdialog.CCombPanel):
    """表單頁（login_new/register2027.dlg）。

    消息號：1=上一步（回協議）、2=確認註冊、50=「註冊五個賬號」、
    51=「同意用戶協議和註冊條款」。兩個勾選框在版式裡原本同為 50，
    分不出點的是哪個；交付的 register2027_msg.dlg 已把同意改成 51，
    腳本對「共用 50」的舊版式也做了狀態差容錯（見 _CheckClick）。
    四個輸入框：edt_account / edt_Pwd / edt_Pwd_1（確認）/ edt_email。
    """

    def __init__(self, parent):
        _Diag("form layout begin")
        combdialog.CCombPanel.__init__(self, parent, DLG_FORM)
        _Diag("form layout ready")
        import C_object

        font = _EditFont()
        self.m_AccountEdit = _CreateFormEdit(
            self, CRegAccountEdit, "edt_account", 16, font
        )
        self.m_PwdEdit = _CreateFormEdit(self, CRegPwdEdit, "edt_Pwd", 16, font)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit2 = _CreateFormEdit(
            self, CRegPwdEdit, "edt_Pwd_1", 16, font
        )
        self.m_PwdEdit2.m_IsPassword = True
        self.m_EmailEdit = _CreateFormEdit(
            self, interface.CEdit, "edt_email", 50, font
        )
        _Diag("form tab begin")
        self.m_AccountEdit.SetNextEdit(self.m_PwdEdit)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_EmailEdit)
        self.m_EmailEdit.SetNextEdit(self.m_AccountEdit)
        _Diag("form tab ready")
        # 勾選框直接來自版式。缺了也不能讓整頁開不起來：
        # 五個賬號取不到就當「沒勾」，同意框取不到就不拿它當前置條件。
        self.m_FiveCheck = self._layout_check("btn_fiveaccount")
        self.m_Consent = self._layout_check("btn_isee")
        self.m_Hint = self._create_hint(C_object)
        self.m_RegistrationRequests = []
        # 只有日後真實請求送出時才可設置 pending；留樁不設置，不能假報成功。
        self.m_PendingAccounts = None
        self.SetRegisterFive(False)
        self.m_AccountEdit.Active(True)

    def _layout_check(self, name):
        try:
            obj = self.GetObject(name)
        except Exception:
            obj = None
        if obj is None:
            _Diag("check anchor missing %s" % name)
            return None
        check = _LayoutCheck(obj, name)
        check.Set(False)  # 用戶口徑：兩個勾選默認都不勾
        return check

    def _create_hint(self, C_object):
        """提示小字（版式 txt_Wrong）。取不到/建不起來都不影響表單：
        詳細原因照樣會彈框，絕不會「點了什麼都沒發生」。"""
        try:
            if self.GetObject("txt_Wrong") is None:
                _Diag("hint anchor missing txt_Wrong")
                return None
            hint = combmacro.CRICHTEXT(
                C_object.CRichTextObject, "txt_Wrong", self, "", _EditFont(),
                _LayoutColor(self, "txt_Wrong")
            )
            _Diag("hint ready")
            return hint
        except Exception:
            _DiagFailure("hint")
            return None

    def _ShowHint(self, text):
        if self.m_Hint is None:
            return
        try:
            self.m_Hint.SetText(text)
        except Exception:
            _DiagFailure("hint settext")

    def _Fail(self, label, msg):
        """短句寫在版式的提示框裡，完整原因交給彈框。"""
        self._ShowHint(label)
        return msg

    def IsRegisterFive(self):
        return self.m_FiveCheck is not None and self.m_FiveCheck.Get()

    def SetRegisterFive(self, enabled):
        if self.m_FiveCheck is not None:
            self.m_FiveCheck.Set(bool(enabled))
        self.SyncFiveMode()

    def SyncFiveMode(self):
        """按「五個賬號」當前狀態同步帳號位數上限與常駐提示。

        已核對原版 SetLimit 只改 m_Limit，絕不截掉已有的輸入。
        """
        five = self.IsRegisterFive()
        self.m_AccountEdit.SetLimit(14 if five else 16)
        self._ShowHint(LABEL_FIVE_MODE if five else "")

    def CheckEmail(self, email):
        if len(email) < 5 or len(email) > 50:
            return False
        import re

        patt = re.compile("^[_\\.\\-a-z0-9A-Z]+@[_\\.\\-a-z0-9A-Z]+$")
        return patt.match(email) is not None

    def DoCheck(self):
        """校验通过返回 None，否则返回要提示的文案（口径同旧版 DoCheck）。"""
        if self.m_Consent is not None and not self.m_Consent.Get():
            return self._Fail(LABEL_CONSENT, MSG_CONSENT)
        account = self.m_AccountEdit.GetText()
        register_five = self.IsRegisterFive()
        maximum = 14 if register_five else 16
        if len(account) < 6 or len(account) > maximum or not _IsAsciiAlnum(account):
            self.m_AccountEdit.Active(True)
            if register_five:
                return self._Fail(LABEL_ACC_FIVE, MSG_ACC_BATCH_FORMAT)
            return self._Fail(LABEL_ACC, MSG_ACC_FORMAT)
        pwd = self.m_PwdEdit.GetText()
        if len(pwd) < 6 or len(pwd) > 16:
            self.m_PwdEdit.Active(True)
            return self._Fail(LABEL_PWD, MSG_PWD_FORMAT)
        if not _IsAsciiAlnum(pwd):
            self.m_PwdEdit.Active(True)
            return self._Fail(LABEL_PWD_ALNUM, MSG_PWD_ALNUM)
        if pwd != self.m_PwdEdit2.GetText():
            self.m_PwdEdit2.Active(True)
            return self._Fail(LABEL_PWD_DIFF, MSG_PWD_MISMATCH)
        email = self.m_EmailEdit.GetText().strip()
        if not self.CheckEmail(email):
            self.m_EmailEdit.Active(True)
            return self._Fail(LABEL_EMAIL, MSG_EMAIL_FORMAT)
        return None

    def DoSubmit(self):
        import commondialog

        _Diag("submit start")
        self.m_RegistrationRequests = []
        self.m_PendingAccounts = None
        # 提交前按勾選框的**當前**狀態再同步一次：客戶端若把點擊消息排在
        # 引擎翻轉之前，OnMessage 裡讀到的會是上一次的值，這裡以提交時為準。
        self.SyncFiveMode()
        try:
            msg = self.DoCheck()
            _Diag("check done fail=%s" % (msg is not None))
            if msg is not None:
                commondialog.ShowNewMessageBox(msg, BTN_OK)
                _Diag("fail box shown")
                return
            accounts = BuildRegistrationAccounts(
                self.m_AccountEdit.GetText(), self.IsRegisterFive()
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

    def _CheckClick(self):
        """勾選框被點了一下：引擎已經翻過了，我們只按新狀態刷新提示。

        兩個勾選框共用同一個消息號（舊版式都是 50）也不影響——這裡不需要
        知道點的是哪個，把五個賬號模式的提示與位數上限重算一遍就行。
        """
        _Diag("check five=%d consent=%d" % (
            int(self.IsRegisterFive()),
            int(self.m_Consent is not None and self.m_Consent.Get()),
        ))
        self.SyncFiveMode()

    def OnMessage(self, msgid):
        _Diag("form msgid=%s" % (msgid,))
        _PlayBtnSound()
        if msgid == 1:
            self.m_PendingAccounts = None
            Step(0)
        elif msgid == 2:
            self.DoSubmit()
        elif msgid == ID_FIVE_CHECK or msgid == ID_CONSENT_CHECK:
            self._CheckClick()
        else:
            _Diag("form msgid unhandled")
        return True


_PANELS = [CRegTermsPanel, CRegFormPanel]


def Step(n):
    """切頁。客戶端會把 OnMessage 裡的腳本異常吞掉（界面只是「沒反應」），

    所以這里必須自己接住：留日誌、給玩家一個明說「開不了」的彈框，再把人
    回收回首頁。絕不允許出現「點了什麼都沒發生」。
    """
    global g_RegisterPanel
    _Diag("step=%s begin" % n)
    try:
        panel = _PANELS[n](interface.DialogPanel)
    except Exception:
        _DiagFailure("step=%s" % n)
        g_RegisterPanel = None
        _RecoverEntry()
        try:
            import commondialog

            commondialog.ShowNewMessageBox(MSG_UNKNOWN_ERR, BTN_OK)
        except Exception:
            _DiagFailure("step=%s box" % n)
        return
    g_RegisterPanel = panel
    _Diag("step=%s ready" % n)


def Show(s):
    global g_RegisterPanel
    if s:
        _Diag("show begin")
        try:
            C_sys.InputSecrecy(1)
            Step(0)
            _Diag("show ready")
        except Exception:
            _DiagFailure("show")
            g_RegisterPanel = None
            _RecoverEntry()
    else:
        g_RegisterPanel = None
        C_sys.InputSecrecy(0)
        _Diag("show closed")


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
