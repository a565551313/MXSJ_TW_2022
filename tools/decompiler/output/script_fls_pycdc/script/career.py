# pycdc 交叉复核产物 · script.fls entry 3685
# co_filename(原始)='script/career.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3685.pyc (Python 2.5)

import playerphoto
import usermacro
import gameurl
g_Debug = False

def ModuleReset():
    global g_Debug
    g_Debug = False

SERVER = gameurl.CAREER_URL
CAREER_PAGE_URL = gameurl.CAREER_PAGE_URL
CAREER_TESTURL = 'http://192.168.181.23:9989'
CAREER_PAGE_TESTURL = 'http://10.32.4.77:824/2015/mxlife/?id=%s'
PASSPORT = '36323de1b18f4d928e5c0d0321ba0e25'
MSG_FAIL = '\xba\xf4\xb5\xb8\xc1c\xa6\xa3\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5'
MSG_WAIT = '\xbd\xd0\xb5\xa5\xab\xdd\xba\xf4\xaf\xb8\xc5T\xc0\xb3'
MSG_WAIT_LOGIN = '\xaaA\xb0\xc8\xbe\xb9\xc1c\xa6\xa3\xa1A\xbd\xd0\xb5y\xab\xe1\xa6A\xb8\xd5'

def UploadPlayerInfo(dct):
    import hero
    import misc
    propObj = hero.g_Prop
    dct['gm_sex'] = propObj.m_Sex
    dct['gm_school'] = hero.GetLiupai()
    dct['gm_xlnum'] = 0
    for ID, obj in hero.g_Skills[hero.ST_SKILL].items():
        if ID <= ID:
            pass
        elif not ID <= 2258:
            continue
        
        if obj.m_TrueLv >= 25:
            dct['gm_xlnum'] += 1
            continue
        2251
    
    dct['gm_fly'] = propObj.m_FlyFlag
    dct['gm_grade'] = propObj.m_Grade
    dct['gm_name'] = propObj.m_Name
    dct['gm_orgname'] = propObj.sOrg
    dct['gm_servername'] = misc.GetServerName()
    DoUpload(dct)


def ShowCareer():
    import nethero
    import usermacro
    if CheckDataState():
        usermacro.PROMPT_MSG(MSG_WAIT)
        nethero.C2SOpenMxLife()
    else:
        usermacro.PROMPT_MSG(MSG_WAIT_LOGIN)


def CanShowCareer():
    return True


def CheckDataState():
    import hero
    import misc
    import C_sys
    if hero.PropInitFinish() and C_sys.GetTime() - misc.g_RecordTime > 40000:
        return True
    
    return False

OP_UPDATE_INFO = 1

def OnUploadSucceed():
    pass

WEBFUNC = {
    OP_UPDATE_INFO: OnUploadSucceed }

def OnUploadError():
    pass

ERRORFUNC = {
    OP_UPDATE_INFO: OnUploadError }

def OnError(optype):
    func = ERRORFUNC.get(optype)
    if func:
        func()
    


def OnSucces(optype):
    func = WEBFUNC.get(optype)
    if func:
        func()
    


def DoUpload(data):
    import hero
    import misc
    serverid = misc.GetServerID()
    gameid = hero.g_ID
    web = '%s/api/gameapi.aspx?gate=mx&passport=%s&module=com&act=gameinfo&serverid=%d&gameid=%s' % (SERVER, PASSPORT, serverid, gameid)
    if g_Debug:
        print None(None, None, None, None, None)
        print data
    
    playerphoto.UploadFile(web, None, data, OnReceiveProcess, OP_UPDATE_INFO)


def OpenCareerUrl(guid):
    print 'OpenCareerUrl!!!', guid
    import net
    web = CAREER_PAGE_URL % guid
    net.OpenUrl(web)


def OnReceiveProcess(data, succeed, optype):
    
    try:
        print '\xacO\xa7_\xa6\xa8\xa5\\:%s, \xbe\xde\xa7@\xc3\xfe\xab\xac:%s ' % (succeed, optype)
        print data
    except:
        pass

    if not succeed and data:
        usermacro.PROMPT_MSG(MSG_FAIL)
        OnError(optype)
        return None
    
    (head, body) = data.split('\r\n\r\n', 1)
    if not body:
        usermacro.PROMPT_MSG(MSG_FAIL)
        OnError(optype)
        return None
    
    analyser = playerphoto.CAnalyser(body)
    d = analyser.GetData()
    if not d:
        print '\xb8\xd1\xaaR\xbc\xc6\xbe\xda\xa5X\xbf\xf9:', optype
        OnError(optype)
        return None
    
    extdata = d.get('ext_data')
    if not extdata:
        OnError(optype)
        return None
    
    guid = extdata.get('GUID')
    if guid and len(guid) == 32:
        OpenCareerUrl(guid)
        OnSucces(optype)
    else:
        OnError(optype)
