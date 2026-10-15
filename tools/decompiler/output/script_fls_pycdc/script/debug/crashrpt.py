# pycdc 交叉复核产物 · script.fls entry 1001
# co_filename(原始)='script/debug/crashrpt.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1001.pyc (Python 2.5)

import misc
import C_sys
IS_USE_BUG = True
SERVER = 'http://statistics.duoyi.com/game/uploadfile/mx'
TEST_SERVER = 'http://10.17.64.84:8121/game/uploadfile/mx'
FILE_FOLDER = 'Log/history/crashlog/'
INSTALL_SUCCEES = 0
g_CrashResult = None
g_PacketList = []
g_FileName = ''

def ModuleReset():
    global g_PacketList
    g_PacketList = []

ModuleReset()

def AddWalkerRes(*args):
    import sys
    last_type = getattr(sys, 'last_type', [])
    if not isinstance(last_type, list):
        last_type = []
    
    if len(last_type) > 20:
        last_type.pop(0)
    
    last_type.append(args)
    sys.last_type = last_type


def AddWalkerResOk(*args):
    import sys
    last_value = getattr(sys, 'last_value', [])
    if not isinstance(last_value, list):
        last_value = []
    
    if len(last_value) > 20:
        last_value.pop(0)
    
    last_value.append(args)
    sys.last_value = last_value


def AddMap(*args):
    import sys
    last_map = getattr(sys, 'last_map', [])
    if not isinstance(last_map, list):
        last_map = []
    
    if len(last_map) > 20:
        last_map.pop(0)
    
    last_map.append(args)
    sys.last_map = last_map


def CrashInstall():
    import os
    import pubbugly
    import misc
    if misc.IsTWServer():
        return None
    
    if not os.path.isdir(FILE_FOLDER):
        
        try:
            os.makedirs(FILE_FOLDER)
        except BaseException:
            pass
        except:
            None<EXCEPTION MATCH>BaseException
        

    None<EXCEPTION MATCH>BaseException
    pubbugly.ChangeCrashInfo(CrashAddCRFile)


def CrashAddCRFile():
    filename = GetFileName()
    C_sys.AddCRFile(filename)
    C_sys.AddCRFile('ESLog')


def CrashUninstall():
    global g_FileName
    import os
    import misc
    if misc.IsTWServer():
        return None
    
    filename = GetFileName()
    
    try:
        if os.path.exists(filename):
            os.remove(filename)
        
        g_FileName = ''
    except BaseException:
        pass

    C_sys.CrashUninstall()


def OnCrash():
    import misc
    if misc.IsTWServer():
        return None
    
    SaveRecordData()


def RecordPacketData(icmd, isC2S = False):
    import netprotocol
    if isC2S:
        icmd = netprotocol.ReplaceCmd2RealCmd(icmd)
        packet = 'c0x%x' % icmd
    else:
        packet = 's0x%x' % icmd
    if len(g_PacketList) >= 4000:
        del g_PacketList[0]
    
    g_PacketList.append(packet)


def GetFileName():
    global g_FileName, g_FileName, g_FileName, g_FileName
    import os
    if not g_FileName:
        g_FileName = ''
        tm = misc.LocalTime()
        del tm
        g_FileName = None % ('CRF_%04d%02d%02d%02d%02d%02d.crashlog'[0], tm[1], tm[2], tm[3], tm[4], tm[5])
        num = 1
        while os.path.exists(g_FileName):
            g_FileName = g_FileName[:-9] + '_%d' % num + g_FileName[-9:]
            num += 1
        g_FileName = FILE_FOLDER + g_FileName
    
    
    try:
        fd = open(g_FileName, 'wb+')
        fd.close()
    except:
        pass

    return g_FileName


def SaveRecordData():
    import cfg
    
    try:
        cfg.SaveData('mx.ini', 'Game', 'rescrash', '1')
    except:
        pass

    sMsg = ''
    import netlogin
    import hero
    import sys
    info = str(netlogin.g_CurrAccount)
    if hero.g_ID:
        info += '-%s' % hero.g_ID
    
    lst = [
        info]
    
    try:
        tm = misc.LocalTime()
    except Exception:
        e = None
        tm = [
            0,
            0,
            0,
            0,
            0,
            0]
        info = 'misc.LocalTime() Error:%s' % e
        lst.append(info)

    info = '%d\xa6~%d\xa4\xeb%d\xa4\xe9%d\xae\xc9%d\xa4\xc0%d\xac\xed' % (tm[0], tm[1], tm[2], tm[3], tm[4], tm[5])
    lst.append(info)
    lst.extend(g_PacketList)
    
    try:
        info = 'ErrorLog: %s-%s' % (getattr(sys, 'last_type', ''), getattr(sys, 'last_value', ''))
        lst.append(info)
    except:
        pass

    lst.append(sMsg)
    
    try:
        import model_mapinfobar
        o = model_mapinfobar.GetModel()
        (x, y) = o.GetHeroPos()
        name = o.GetMapName()
        lst.append('pos:%s %s %s' % (name, x, y))
    except:
        pass

    
    try:
        import setfps
        import charpath
        lst.append('FPS:%s' % setfps.GetCurFrame())
        lst.append('Char:%s' % charpath.IsUseNewRes())
    except:
        pass

    
    try:
        data = EncryptPacketData('\n'.join(lst))
    except Exception:
        e = None
        print 'EncryptPacketData() Error', e
        return None

    
    try:
        filename = GetFileName()
    except Exception:
        e = None
        print 'GetFileName() Error', e
        return None

    
    try:
        open(filename, 'wb').write(data)
    except Exception:
        e = None
        print 'open("%s", "wb").write(data) Error' % filename, e



def GameStartTips():
    import cfg
    import chatoutput
    result = cfg.GetData('mx.ini', 'Game', 'rescrash')
    if result == '1':
        cfg.SaveData('mx.ini', 'Game', 'rescrash', '0')
        chatoutput.AddChat('#Y\xc0\xcb\xb4\xfa\xa8\xec\xb9C\xc0\xb8\xba\xdd\xb5o\xa5\xcd\xb2\xa7\xb1`\xc3\xf6\xb3\xac\xb1\xa1\xaap\xa1C\xadY\xb4\xa3\xa5\xdc\xbf\xf9\xbb~\xbdX-1\xa1A\xbd\xd0\xc3\xf6\xb3\xac\xa9\xd2\xa6\xb3\xb9C\xc0\xb8\xb5\xa1\xa4f\xb1\xd2\xb0\xca\xb9C\xc0\xb8\xa5\xd8\xbf\xfd\xa4U\xa1u\xb8\xea\xb7\xbd\xad\xd7\xb4_\xbe\xb9\xa1v\xb6i\xa6\xe6\xad\xd7\xb4_\xa1C\xa6p\xaaG\xa4\xa3\xaf\xe0\xb8\xd1\xa8M\xa1A\xbd\xd0\xa4\xce\xae\xc9\xc1p\xc3\xb4\xab\xc8\xaaA\xb3B\xb2z#Y\xa1C#n')
    


def EncryptPacketData(txt):
    import base64
    import random
    import string
    import zlib
    txt = base64.b64encode(txt)
    newtxt = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    fkey = ord(newtxt[0]) % 10 + 1
    for i in xrange(len(txt)):
        c = txt[i]
        o = ord(c)
        o += i % fkey
        o -= (i % 8) * fkey
        if o < 0:
            o += 256
        
        o %= 256
        newtxt += chr(o)
    
    newtxt = zlib.compress(newtxt)
    return newtxt


def DecryptPacketData(txt):
    import base64
    import zlib
    txt = zlib.decompress(txt)
    fkey = ord(txt[0]) % 10 + 1
    txt = txt[4:]
    newtxt = ''
    for i in xrange(len(txt)):
        c = txt[i]
        o = ord(c)
        o += (i % 8) * fkey
        o -= i % fkey
        if o < 0:
            o += 256
        
        o %= 256
        newtxt += chr(o)
    
    newtxt = base64.b64decode(newtxt)
    return newtxt


def DecryptFile(filename):
    
    try:
        f = file(filename, 'rb')
    except Exception:
        e = None
        LOG_DEBUG('DecryptFile\xa5\xb4\xb6}\xa4\xe5\xa5\xf3\xa5\xa2\xb1\xd1', str(e))
        return None

    data = f.read()
    f.close()
    data = DecryptPacketData(data)
    
    try:
        f = file(filename + '.txt', 'wb')
    except Exception:
        e = None
        LOG_DEBUG('DecryptFile\xb3\xd0\xab\xd8\xa4\xe5\xa5\xf3\xa5\xa2\xb1\xd1', str(e))
        return None

    f.write(data)
    f.close()
    LOG_DEBUG('DecryptFile\xa7\xb9\xa6\xa8')
