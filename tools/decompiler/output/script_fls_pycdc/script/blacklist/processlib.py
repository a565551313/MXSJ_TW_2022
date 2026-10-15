# pycdc 交叉复核产物 · script.fls entry 4314
# co_filename(原始)='script/blacklist/processlib.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4314.pyc (Python 2.5)

import C_sys
g_ProcessDct = { }
g_ProcessPathList = []
g_ModuleList = []

def ModuleReset(mode = 0):
    global g_ProcessDct, g_ProcessPathList, g_ModuleList
    g_ProcessDct = { }
    g_ProcessPathList = []
    g_ModuleList = []


def GetProcessDict():
    '''\xc0\xf2\xa8\xfa\xb6i\xb5{ID:\xa5i\xb0\xf5\xa6\xe6\xa4\xe5\xa5\xf3\xa6W\xaa\xba\xacM\xaeg\xc3\xf6\xabY
\t'''
    global g_ProcessDct
    if not g_ProcessDct:
        (result, g_ProcessDct) = C_sys.GetProcessDict()
    
    return None()


def GetProcessPathList():
    '''\xa6C\xaa\xed\xa4\xe8\xa6\xa1\xc0\xf2\xa8\xfa\xa9\xd2\xa6\xb3\xb6i\xb5{\xaa\xba\xa5i\xb0\xf5\xa6\xe6\xa4\xe5\xa5\xf3\xb8\xf4\xae|
\t'''
    if not g_ProcessPathList:
        for path in C_sys.GetModuleFileName():
            if not path:
                continue
            
            if path == '<unknown>':
                continue
            
            g_ProcessPathList.append(path)
        
    
    return g_ProcessPathList


def GetModuleList():
    '''\xc0\xf2\xa8\xfa\xb7\xed\xabe\xb6i\xb5{\xaa\xbadll\xbc\xd2\xb6\xf4\xa6C\xaa\xed
\t'''
    global g_ModuleList
    if not g_ModuleList:
        (result, g_ModuleList) = C_sys.GetModuleList()
    
    return g_ModuleList


def GetSelfName():
    '''\xc0\xf2\xa8\xfa\xb7\xed\xabe\xb6i\xb5{\xaa\xba\xa5i\xb0\xf5\xa6\xe6\xa4\xe5\xa5\xf3\xa6W\xba\xd9
\t'''
    lst = GetModuleList()
    if lst:
        import os
        return os.path.basename(lst[0])
    
    return 'mxmain.dll'
