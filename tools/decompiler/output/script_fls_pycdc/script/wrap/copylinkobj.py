# pycdc 交叉复核产物 · script.fls entry 4597
# co_filename(原始)='script/wrap/copylinkobj.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_4597.pyc (Python 2.5)

import dlgtalk

def CreateCopyLink(linkid, *args):
    if not CheckLimit(linkid):
        return None
    
    if linkid > 500:
        CreateKuafuLink(linkid, *args)
    else:
        import wrapui
        CommitCopy(wrapui.CreateLink(linkid, *args))


def CreateKuafuLink(linkid, *args):
    
    class send(object):
        
        def __init__(self, linkCls):
            self.m_LinkCls = linkCls

        
        def __call__(self, \x90\xb6nfo, *args):
            text = self.m_LinkCls.Create(\x90\xb6nfo, *args)
            CommitCopy(text)


    import kuafulink
    oMgr = kuafulink.GetLinkMgr()
    cls = oMgr.GetLinkClass(linkid)
    if not cls:
        return None
    
    packFunc = cls.CreatePackFunc(*args)
    oMgr.CreateInfo(linkid, packFunc, send(cls), *args)


def CommitCopy(text):
    if not text:
        return None
    
    import chatinput
    import usermacro
    import wrapui
    edit = chatinput.GetLinkInputEdit()
    if not chatinput.CheckLink(edit):
        (_, save, _) = wrapui.HandleLink(text)
        edit.SetText(save)
        return None
    
    if not IsTextOnly(edit, text):
        usermacro.PROMPT_MSG('\xac\xdb\xa6P\xabH\xae\xa7\xa4\xa3\xaf\xe0\xd6\xdf\xb6K\xa8\xe2\xa6\xb8')
    else:
        edit.AddTxtObj(text)
        edit.Active(True)


def IsTextOnly(edit, text):
    import wrapui
    for _, t in edit.m_Data:
        if t == text:
            return False
            continue
        if wrapui.IsSameKuafuLink(t, text):
            return False
            continue
    
    return True


def CheckLimit(linkID):
    func = g_CheckFunc.get(linkID, None)
    if callable(func):
        return func()
    
    return True


def CheckLycos():
    import chatinput
    import wrapui
    import mainmenu
    import channel
    edit = chatinput.GetLinkInputEdit()
    mainEdit = mainmenu.GetChatInputObj()
    if edit == mainEdit and channel.IsZeroLycosLinkCh():
        import usermacro
        usermacro.PROMPT_MSG('\xb8\xd3\xc0W\xb9D\xa4\xa3\xa4\xe4\xab\xf9\xb5o\xb0e\xa6\xb9\xc3\xec\xb1\xb5')
        return False
    
    (_, _, link_dict) = wrapui.HandleLink(edit.GetText())
    lst = _[1]
    return True


def CheckMapPos():
    import chatinput
    import wrapui
    edit = chatinput.GetLinkInputEdit()
    (_, _, link_dict) = wrapui.HandleLink(edit.GetText())
    lst = _[1]
    return True


def CheckTYImage():
    import chatinput
    import wrapui
    edit = chatinput.GetLinkInputEdit()
    (_, _, link_dict) = wrapui.HandleLink(edit.GetText())
    iHaveSpeEmoteList = _[1]
    lst = _[2]
    return True

g_CheckFunc = {
    54: CheckLycos,
    72: CheckMapPos,
    96: CheckTYImage }
