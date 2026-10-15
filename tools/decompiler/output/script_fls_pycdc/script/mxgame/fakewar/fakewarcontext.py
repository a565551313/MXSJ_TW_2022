# pycdc 交叉复核产物 · script.fls entry 1692
# co_filename(原始)='script/mxgame/fakewar/fakewarcontext.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1692.pyc (Python 2.5)

g_WarMgr = None

def ModuleReset():
    global g_WarMgr
    g_WarMgr = None


def SetFakeWarMgr(oWarMgr):
    '''
\t\xb3]\xb8m\xb8\xd1\xaaR\xaa\xba\xa4W\xa4U\xa4\xe5\xa1A\xbb\xdd\xadn\xa6b\xbd\xd5\xa5\xce\xab\xe1\xa6A\xb8m\xac\xb0None\xa1A\xa4\xa3\xb5M\xb7|\xa5X\xb2{\xb0\xdd\xc3D
\t:param oWarMgr:
\t:return:
\t'''
    global g_WarMgr, g_WarMgr
    if oWarMgr:
        g_WarMgr = oWarMgr
    else:
        g_WarMgr = None


def GetFakeWarMgr():
    return g_WarMgr


def GetAttacker():
    if not g_WarMgr:
        return None
    
    return g_WarMgr.GetWarriorMgr().GetAttacker()


def GetVictim():
    if not g_WarMgr:
        return None
    
    return g_WarMgr.GetWarriorMgr().GetVictim()


def GetWarriorByID(iWarriorID):
    if not g_WarMgr:
        return None
    
    return g_WarMgr.GetWarriorMgr().GetWarriorByID(iWarriorID)


def AddWarrior(iWarriorID, oWarrior):
    if not g_WarMgr:
        return None
    
    return g_WarMgr.GetWarriorMgr().AddWarrior(iWarriorID, oWarrior)


def DelWarrior(iWarriorID):
    return None if not g_WarMgr else g_WarMgr.GetWarriorMgr().DelWarrior(iWarriorID)


def AddFakeWarrior(oWarrior):
    if not g_WarMgr:
        return None
    
    return g_WarMgr.GetWarriorMgr().AddFakeWarrior(oWarrior)


def ClearAllFakeWarrior():
    if not g_WarMgr:
        return None
    
    return g_WarMgr.ClearAllFakeWarrior()
