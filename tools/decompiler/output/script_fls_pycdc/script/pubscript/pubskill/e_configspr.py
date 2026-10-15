# pycdc 交叉复核产物 · script.fls entry 2516
# co_filename(原始)='script/pubscript/pubskill/e_configspr.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2516.pyc (Python 2.5)

import os
SECTION_IMAGE = 'images'
SECTION_FRAMES = 'frames'
SECTION_INFO = 'info'
SPR_FILENAME = 'FileName1'
SPR_PACKAGE = 'PackageName'
SPR_BATCH = 'BranchPath'
SPR_SCALE = 'Scale'
SPR_TRANSPARENCY = 'Alpha'
SPR_DYE = 'PalPro'
SPR_HIT = 'AttackHitFrame'
SPR_HURT = 'AttackHurtFrame'
SPR_SPACE = 'AttackSpace'
SPR_KEYS = 'KeyFrames'
SPR_STARTFRAME = 'StartFrame'
SPR_LAUNCHFRAME = 'LaunchFrame'
g_CacheDict = { }

def SaveData(path, key, value, section = SECTION_IMAGE):
    d = _ReadSetting(path)
    if d is None:
        d = { }
    
    if not d.get(SECTION_FRAMES):
        d[SECTION_FRAMES] = {
            SECTION_FRAMES: [] }
    
    s = d.get(section)
    if s is None:
        s = { }
        d[section] = s
    
    if key == SPR_FILENAME and hasattr(value, '__iter__'):
        num = 1
        for fileName in value:
            key = 'FileName%s' % num
            s[key] = fileName
            num += 1
        
    else:
        s[key] = value
    _write(path, d)


def GetData(path, key = None, default = None, section = SECTION_IMAGE):
    d = _ReadSetting(path)
    if d is None:
        return default
    
    s = d.get(section)
    if s is None:
        return default
    
    if not key:
        return s
    
    if key == SPR_FILENAME:
        num = 1
        fileName = 'FileName%s' % num
        fileList = []
        while fileName in s:
            fileList.append(s[fileName])
            num += 1
            fileName = 'FileName%s' % num
        if len(fileList) == 1:
            return fileList[0]
        
        return fileList
    else:
        r = s.get(key, default)
        return r


def ClearCache(path):
    global g_CacheDict
    if path in g_CacheDict:
        del g_CacheDict
    


def _ReadSetting(fname):
    d = { }
    sec = None
    if not os.path.exists(fname):
        
        try:
            os.rename(fname + '_', fname)
        return None

    
    
    try:
        f = open(fname, 'rt')
        for line in f:
            s = line.strip()
            if not s:
                continue
            
            if s[0] == '[' and s[-1] == ']':
                d[s[1:-1]] = { }
                sec = d[s[1:-1]]
                continue
            if sec is not None:
                l = s.split('=')
                if len(l) == 2:
                    sec[l[0].strip()] = l[1].strip()
                elif SECTION_FRAMES not in sec:
                    sec[SECTION_FRAMES] = []
                
                sec[SECTION_FRAMES].append(s)
                continue
        
        f.close()
    except:
        return None

    return d


def _write(fname, d):
    l = []
    for s, sv in d.items():
        l.append('[%s]\n' % s)
        if s == SECTION_FRAMES:
            for k in sv[SECTION_FRAMES]:
                l.append('%s\n' % k)
            
        for k, v in sv.items():
            l.append('%s=%s\n' % (k, v))
        
    
    temp = fname + '_'
    
    try:
        f = open(temp, 'wt')
        f.writelines(l)
        f.close()
        if os.path.exists(fname):
            os.remove(fname)
        
        os.rename(temp, fname)
    except:
        return False

    return True
