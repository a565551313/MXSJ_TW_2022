# pycdc 交叉复核产物 · script.fls entry 4775
# co_filename(原始)='script/preloadres/preload_emote.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4775.pyc (Python 2.5)

import datapreloademote
import misc
import permission
import interface
g_bHasPreloadRes = False
g_oCachedResObjList = []
g_iStartTime = 0

def PreloadEmote():
    global g_bHasPreloadRes, g_oCachedResObjList
    import asynctaskqueue
    import asynctaskdefine
    if g_bHasPreloadRes:
        return None
    
    iTime = misc.Time()
    g_bHasPreloadRes = True
    g_oCachedResObjList = []
    oQueue = asynctaskqueue.GetAsyncTaskQueue()
    lData = datapreloademote.GetData()
    oQueue.InsertEmptyTask(asynctaskdefine.TASK_TYPE_OTHER, '', '', misc.Functor(OnLoadAllFinish))
    setPng = set()
    setSpr = set()
    setIgs = set()
    for sPath, sPack in lData:
        if sPath.endswith('.png'):
            setPng.add((sPath, sPack))
            continue
        if sPath.endswith('.igs'):
            setIgs.add((sPath, sPack))
            continue
        if sPath.endswith('.spr'):
            setSpr.add((sPath, sPack))
            continue
    
    for sSpr, sPack in setSpr:
        oQueue.InsertAsyncLoadSprTask(asynctaskdefine.TASK_TYPE_OTHER, sSpr, sPack, misc.Functor(OnLoadOneSprFinish, sSpr, sPack))
    
    for sIgs, sPack in setIgs:
        oQueue.InsertAsyncLoadIgsTask(asynctaskdefine.TASK_TYPE_OTHER, sIgs, sPack, misc.Functor(OnLoadOneIgsFinish, sIgs, sPack))
    
    for None in setPng:
        pass
    
    oQueue.InsertEmptyTask(asynctaskdefine.TASK_TYPE_OTHER, '', '', misc.Functor(OnStartLoadEmote))
    LOG('start PreloadEmote:', misc.Time() - iTime)


def OnStartLoadEmote(*args):
    global g_iStartTime
    g_iStartTime = misc.Time()
    LOG('\xb6}\xa9l\xb9w\xa5[\xb8\xfc\xaa\xed\xb1\xa1: ', misc.Time() - g_iStartTime)


def OnLoadAllFinish(*args):
    LOG('\xa5[\xb8\xfc\xaa\xed\xb1\xa1\xb5\xb2\xa7\xf4\xa1G', misc.Time() - g_iStartTime)


def OnLoadOneSprFinish(sPath, sPack, oTask):
    if not permission.IsPreloadUIRes():
        return None
    
    
    try:
        oObj = interface.CSpriteObject(None, sPath, sPack)
        oObj.SetShow(False)
        g_oCachedResObjList.append(oObj)
    except:
        pass



def OnLoadOnePngFinish(sPath, sPack, oTask):
    if not permission.IsPreloadUIRes():
        return None
    
    
    try:
        oObj = interface.CBitmapObject(None, sPath, sPack)
        oObj.SetShow(False)
        g_oCachedResObjList.append(oObj)
    except:
        pass



def OnLoadOneIgsFinish(sPath, sPack, oTask):
    if not permission.IsPreloadUIRes():
        return None
    
    
    try:
        oObj = interface.CImagesObject(None, sPath, sPack)
        oObj.SetShow(False)
        g_oCachedResObjList.append(oObj)
    except:
        pass
