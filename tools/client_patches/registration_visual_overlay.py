# -*- coding: utf-8 -*-
# Compiled with CPython 2.5.6. Executed as CODE (not source) in register's module
# namespace. Uses only native controls; never instantiates the login controller.
import sys

_ValidatedForm = CRegPanel2
_VISUAL_PATH = 'photo'
_VISUAL_PREFIX = 'registration_preview_v3/'
_PREVIEW_TEXT = u'''介面預覽說明\n\n這是註冊介面的離線測試版本，不是正式服務條款。\n\n一、測試範圍\n本次僅測試協議頁、註冊表單、本地校驗與返回操作。\n\n二、不要填寫真實資料\n請勿輸入真實郵箱、常用密碼、手機號碼或其他個人資料。\n可使用 preview@example.invalid 作為測試郵箱。\n\n三、不會建立帳號\n即使表單檢查通過，也只顯示離線提示，不送出註冊請求。\n\n四、按鈕行為\n同意：進入註冊資料頁。\n拒絕：返回首頁，不影響原本選區後的服務條款流程。\n\n五、正式服務之前\n正式協議、隱私說明、帳號政策及服務端驗證仍需另行完成。\n本頁不代表使用者已接受任何正式營運條款。\n\n請以測試副本操作，並保留原始檔案備份。\n\n介面預覽 v3.3'''


def _picture(parent, name, x, y):
    obj = ui.CImage(parent, _VISUAL_PREFIX + name + '.png', _VISUAL_PATH)
    width, height = obj.GetSize()
    if width <= 0 or height <= 0:
        raise RuntimeError('preview image has no dimensions: ' + name)
    obj.SetPos(x, y)
    obj.SetZ(1)
    return obj


def _buttons(panel, msgid):
    result = []
    for obj in panel.m_Frames.values():
        if getattr(obj, 'm_MsgID', None) == msgid:
            result.append(obj)
    return result


def _caption(button, name, size):
    # Preserve the real button and its hit area. The image only carries glyphs,
    # avoiding the TW byte-string font path for simplified Chinese captions.
    if not hasattr(button, 'SetText'):
        raise RuntimeError('preview caption needs a text button')
    w, h = button.GetSize()
    # Load first. If the image fails, retain the existing clickable caption.
    caption = _picture(button, name, (w-size[0])//2, (h-size[1])//2)
    button.SetText('')
    button.m_PreviewCaption = caption


def _action(panel, name, msgid, x, y, width=112, height=34):
    # Native signature is (parent, w, h, COLOR, ALPHA, msgid), NOT x/y.
    # Hide the original whole control: old captions may be baked into its art.
    button = interface.CClickBox(panel, width, height, 0, 0, msgid)
    button.SetPos(x, y)
    button.SetZ(2)
    button.m_PreviewCaption = _picture(button, name, 0, 0)
    return button


def GetData(home):
    # Compatibility helper only; v3.2+ mainpage owns its independent caption.
    # Message 2 is the registration action, not an anonymous resource name.
    try:
        buttons = _buttons(home, 2)
        if len(buttons) != 1:
            raise RuntimeError('registration homepage button is ambiguous')
        _caption(buttons[0], 'home_register', (80, 24))
        print 'RegistrationVisualPreview v3.3: homepage caption installed'
    except Exception:
        # An unsupported resource/control shape must remain visible in logs.
        print 'RegistrationVisualPreview v3.3:', sys.exc_info()[1]
        print 'RegistrationVisualPreview v3.3: homepage caption NOT installed'


class CRegPanel1(combdialog.CCombPanel):
    def __init__(self, parent):
        combdialog.CCombPanel.__init__(self, parent, 'login/service.dlg')
        output = self.GetObject('loc_msg')
        if output is None:
            raise RuntimeError('preview service layout lacks loc_msg')
        import chatoutput
        w, h = output.GetSize()
        x, y = output.GetPos()
        lines = [line + '#r' for line in _PREVIEW_TEXT.split('\n')]
        self.m_PublicTxtBox = chatoutput.COutput(self, w, h, 0, 0, lines,
            txt_font=interface.FontLT14_3, txt_color=interface.COLOR_1)
        self.m_PublicTxtBox.SetPos(x, y)
        self.m_PublicTxtBox.SetChatCursor(0)
        self.m_PublicTxtBox.ResetFromCursor()
        self.m_PublicTxtBox.ScrollTo(0)
        self.m_PreviewTitle = _picture(self, 'terms_title', 280, 83)
        self.m_PreviewActions = {}
        for msgid, caption in ((1, 'agree'), (2, 'reject')):
            buttons = _buttons(self, msgid)
            if len(buttons) != 1:
                raise RuntimeError('preview service button is ambiguous')
            old = buttons[0]
            x, y = old.GetPos()
            w, h = old.GetSize()
            replacement = _action(self, caption, msgid, x+(w-112)//2, y+(h-34)//2)
            old.SetShow(False)
            old.Enable(False)
            self.m_PreviewActions[msgid] = replacement
        print 'RegistrationVisualPreview v3.3: agreement ready'

    def OnMessage(self, msgid):
        if msgid == 1:
            Step(1)
        elif msgid in (2, 3):
            import mainpage
            mainpage.Show(True)
            Show(False)


class CRegPanel2(_ValidatedForm):
    def __init__(self, parent):
        # Load ONLY the visual layout: CLoginIn.__init__, LoginOk, saved account
        # loading, timers, browser links and network disconnects are never used.
        combdialog.CCombPanel.__init__(self, parent, 'login_new/newlogin_800.dlg')
        for obj in self.m_Frames.values():
            msgid = getattr(obj, 'm_MsgID', None)
            if msgid is not None:
                obj.SetShow(False)
                if hasattr(obj, 'Enable'):
                    obj.Enable(False)
        for name in ('edt_Name', 'edt_Pwd', 'chk_protect', 'chk_agree', 'box_URL',
                     'btn_Protect', 'btn_Music'):
            obj = self.GetObject(name)
            if obj is not None:
                obj.SetShow(False)
        self.m_PreviewCard = _picture(self, 'form_card', 200, 138)
        self.m_EmailEdit = CMailEdit(self, 0x805B45, interface.FontLT14_3, 340, 214, 226, 22, linecolor=0x805B45)
        self.m_EmailEdit.SetLimit(32)
        self.m_PwdEdit = CRegEdit(self, 0x805B45, interface.FontLT14_3, 340, 272, 226, 22, linecolor=0x805B45)
        self.m_PwdEdit.SetLimit(16)
        self.m_PwdEdit.m_IsPassword = True
        self.m_PwdEdit2 = CRegEdit(self, 0x805B45, interface.FontLT14_3, 340, 330, 226, 22, linecolor=0x805B45)
        self.m_PwdEdit2.SetLimit(16)
        self.m_PwdEdit2.m_IsPassword = True
        self.m_EmailEdit.SetNextEdit(self.m_PwdEdit)
        self.m_PwdEdit.SetNextEdit(self.m_PwdEdit2)
        self.m_PwdEdit2.SetNextEdit(self.m_EmailEdit)
        # Use the engine's existing focus/Flash/Tab implementation, not a
        # second timer. Give the caret contrast and an explicit foreground Z.
        for edit in (self.m_EmailEdit, self.m_PwdEdit, self.m_PwdEdit2):
            edit.SetZ(2)
            edit.m_Line.SetZ(1)
        self.m_PreviewActions = {}
        for msgid, caption, x in ((1, 'back', 270), (2, 'register', 430)):
            self.m_PreviewActions[msgid] = _action(self, caption, msgid, x, 468)
        self.m_PreviewInfo = _action(self, 'info', 3, 300, 394, 200, 28)
        self.m_PreviewInfoLabel = self.m_PreviewInfo.m_PreviewCaption
        self.m_EmailEdit.Active(True)
        print 'RegistrationVisualPreview v3.3: registration form ready'

    def OnActive(self, activeIdx, flag):
        # The old tooltip placeholders are not part of the new layout.
        return

    def OnButtonEnter(self, btn):
        return

    def OnButtonLeave(self, btn):
        return


# The obsolete 2980 class's constant slot stores this overlay. Keep a harmless
# type for legacy isinstance checks; its entry points remain disabled by v2.2.
class CRegPanel2_2980:
    pass
