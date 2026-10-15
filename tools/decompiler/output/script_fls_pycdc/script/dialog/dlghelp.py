# pycdc 交叉复核产物 · script.fls entry 4355
# co_filename(原始)='script/dialog/dlghelp.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4355.pyc (Python 2.5)

g_Help = None

def ModuleReset():
    global g_Help
    g_Help = None


def Show(dlgid):
    dlgid = -1
    import dreamtooldata
    import sound
    sound.PlaySound(sound.SND_SHOWDLG)
    if isinstance(dlgid, str):
        ShowHelper(dlgid)
        return None
    
    data = dreamtooldata.GetItem([
        '\xa8\xe4\xa5L',
        '\xac\xc9\xad\xb1\xc0\xb0\xa7U'])['childs']
    for d in data:
        if d.get('itemID') == dlgid:
            ShowHelper(d.get('title', ''))
            return None
            continue
    
    LOG(dlgid, '\xb5\xc8(M)5D4#U')


def ShowHelper(txt):
    import dlgtool_lycos_new
    dlgtool_lycos_new.ShowHelper(txt, capture = False)
