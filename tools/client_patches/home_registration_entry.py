# -*- coding: ascii -*-
# CPython 2.5.6 authored fragments, inlined into mainpage's two methods.
# ui and Show are the EXISTING mainpage globals. No registration import at home.

def install_caption(self):
    try:
        buttons = [obj for obj in self.m_Frames.values()
                   if getattr(obj, 'm_MsgID', None) == 2]
        if len(buttons) != 1:
            raise RuntimeError('ambiguous registration button')
        button = buttons[0]
        if not hasattr(button, 'SetText'):
            raise RuntimeError('registration button has no text')
        w, h = button.GetSize()
        picture = ui.CImage(button, 'registration_preview_v3/home_register.png', 'photo')
        iw, ih = picture.GetSize()
        if iw <= 0 or ih <= 0:
            raise RuntimeError('empty registration caption')
        picture.SetPos((w - 80)//2, (h - 24)//2)
        picture.SetZ(1)
        button.SetText('')
        button.m_PreviewCaption = picture
    except Exception, error:
        print 'RegistrationPreview v3.2: homepage caption NOT installed:', error


def open_registration(self):
    # The only registration import in this entry is inside the click action.
    try:
        import register
        register.Show(True)
    except Exception, error:
        print 'RegistrationPreview v3.2: cannot open registration:', error
        return
    # Never hide home before import AND construction have succeeded.
    Show(False)
    import sound
    sound.Play('action/button.wav')
