# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubnet\http.py
import os, C_object, pubcore
g_Logger = pubcore.GetPubLogger(__name__)
HTTP_BOUNDARY = '----------7dc7d35b0017c'
DEFAULT_TIMEOUT = 10
DEFAULT_TIMEOUT_FRAME = 300
SIMFLAG = False
g_UploadMgr = None
g_HttpObjectList = []

def OnRestartClear():
    Clear()


def Clear():
    global g_HttpObjectList
    global g_UploadMgr
    g_UploadMgr = None
    g_HttpObjectList = []
    return


def HttpGet(url, dGet, timeout, callback, *arg):
    sSpace = '?'
    sParameter = ''
    for k, v in dGet.iteritems():
        sParameter += '%s%s=%s' % (sSpace, k, v)
        sSpace = '&'

    url = url + sParameter
    CHttpObject(url, timeout, callback, *arg)
    return url


def Get(url, dGet, timeout, callback, *arg):
    sSpace = '?'
    sParameter = ''
    for k, v in dGet.iteritems():
        sParameter += '%s%s=%s' % (sSpace, k, v)
        sSpace = '&'

    url = url + sParameter
    CHttpObject(url, timeout, callback, *arg)
    return url


def HttpReq(sMethod, sUrl, dGet, fTimeOut, callback, *arg, **karg):
    sSpace = '?'
    sParameter = ''
    for k, v in dGet.iteritems():
        sParameter += '%s%s=%s' % (sSpace, k, v)
        sSpace = '&'

    sUrl = sUrl + sParameter
    CHttpObject(sUrl, fTimeOut, callback, sMethod=sMethod, *arg, **karg)
    return sUrl


def HttpPost(url, dPostFile, dPostArg, callback, *arg):
    pMgr = GetUploadMgr()
    pMgr.RequestUpload(url, dPostFile, dPostArg, callback, *arg)


def Post(url, dPostFile, dPostArg, callback, *arg):
    pMgr = GetUploadMgr()
    pMgr.RequestUpload(url, dPostFile, dPostArg, callback, *arg)


def PostEx(sUrl, sIP, dPostFile, dPostArg, pCallFunc, *args):
    pMgr = GetUploadMgr()
    pMgr.RequestUpload(url=sUrl, ip=sIP, dctPostFile=dPostFile, dctForms=dPostArg, callback=pCallFunc, *args)


def RemoveHttpObj(httpObj):
    if httpObj in g_HttpObjectList:
        g_HttpObjectList.remove(httpObj)


def GetUploadMgr():
    global g_UploadMgr
    if not g_UploadMgr:
        g_UploadMgr = CHttpUploadMgr()
    return g_UploadMgr


def GetUrlInfo(url):
    if url.find('http://') == 0:
        url = url[7:]
        p = url.find('/')
        if p >= 0:
            server = url[:p]
            filename = url[p:]
        else:
            server = url
            filename = '/'
        p = server.find(':')
    if p != -1:
        port = int(server[p + 1:])
        server = server[:p]
    else:
        port = 80
    return (
     server, port, filename)


class CHttpObject(object):

    def __init__(self, url, timeout, callback, *arg, **kw):
        self.m_RequestObj = C_object.CHttpRequestObject()
        self.m_RequestObj.SetCallback(self.OnRequestCallBack)
        self.m_Callback = callback
        self.m_Arg = arg
        self.m_UrlInfo = url
        self.m_TimeOut = timeout
        self.m_HttpMethod = kw.get('sMethod', 'GET')
        self.m_ReadTimeOut = kw.get('iReadTimeOut')
        g_HttpObjectList.append(self)
        self.SendRequest()

    def SendRequest(self):
        headerlist = [
         'Accept-Charset: utf-8',
         'Connection:Close']
        if self.m_ReadTimeOut:
            self.m_RequestObj.SendRequest(self.m_UrlInfo, headerlist, '', self.m_TimeOut, self.m_HttpMethod, 'request', SIMFLAG, readTimeOut=self.m_ReadTimeOut)
        else:
            self.m_RequestObj.SendRequest(self.m_UrlInfo, headerlist, '', self.m_TimeOut, self.m_HttpMethod, 'request', SIMFLAG)

    def OnRequestCallBack(self, *args):
        bSuccess = args[0]
        reponseData = args[1]
        extendArg = args[3:]
        if self.m_Callback:
            self.m_Callback(bSuccess, reponseData, *(self.m_Arg + extendArg))
        RemoveHttpObj(self)


class CHttpUploadMgr(object):

    def __init__(self):
        self.m_ObjList = []
        self.m_RequestData = []
        self.m_TaskID = 0

    def Clear(self):
        self.m_ObjList = []
        self.m_RequestData = []
        self.m_TaskID = 0

    def RequestUpload(self, url, dctPostFile, dctForms, callback, *args, **kw):
        self.m_TaskID += 1
        ipStr = kw.get('ip', '')
        data = [self.m_TaskID, url, dctPostFile,
         dctForms, (callback, args), False, ipStr]
        self.m_RequestData.insert(0, data)
        self.Process()

    def Process(self):
        if len(self.m_ObjList):
            g_Logger.debug('队列还有:%d' % len(self.m_ObjList))
            return
        for data in self.m_RequestData:
            if data[5] == False:
                taskid = data[0]
                url = data[1]
                dctPostFile = data[2]
                dctForms = data[3]
                ip = data[6]
                self.UploadFile(url, dctPostFile, dctForms, taskid, ip=ip)
                break

    def UploadFile(self, url, dctPostFile, dctForms, taskid, ip=''):
        obj = CHttpUploadObject(url, dctPostFile, dctForms, self.ResProcess, taskid, ip=ip)
        self.m_ObjList.append(obj)

    def ResProcess(self, httpobj, succeed, data, taskid, *args):
        if httpobj in self.m_ObjList:
            self.m_ObjList.remove(httpobj)
        request = None
        for i, v in enumerate(self.m_RequestData):
            if v[0] == taskid:
                request = self.m_RequestData.pop(i)
                break

        if succeed == True:
            if data:
                if request:
                    callback, args = request[4]
                    if callback:
                        callback(True, data, *args)
        elif request:
            callback, args = request[4]
            if callback:
                callback(False, data, *args)
        self.Process()
        return


class CHttpUploadObject(object):

    def __init__(self, url, dctPostFile, dctForms, callback, *arg, **kw):
        self.m_RequestObj = C_object.CHttpRequestObject()
        self.m_RequestObj.SetCallback(self.OnRequestCallBack)
        self.m_Callback = callback
        self.m_Arg = arg
        self.m_dctPostFile = dctPostFile
        self.m_dctForms = dctForms
        self.m_UrlInfo = url
        self.m_IP = kw.get('ip', '')
        self.SendRequest()

    def SendRequest(self):
        httpbody = ''
        for pname, fname in self.m_dctPostFile.items():
            if fname:
                ext = fname[fname.rfind('.') + 1:].lower()
                if ext == 'jpg':
                    sFileType = 'image/pjpeg'
                elif ext == 'gif':
                    sFileType = 'image/gif'
                elif ext == 'mdya':
                    sFileType = 'audio/mdya'
                else:
                    sFileType = 'text/plain'
                try:
                    f = open(fname, 'rb+')
                    sFileContent = f.read()
                    f.close()
                except IOError:
                    sFileContent = ''

                httpbody += '--%s\r\n' % HTTP_BOUNDARY + 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (pname, os.path.basename(fname)) + 'Content-Type: %s\r\n\r\n' % sFileType + '%s\r\n' % sFileContent

        if self.m_dctForms:
            for sForm, sValue in self.m_dctForms.iteritems():
                httpbody += '--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (
                 HTTP_BOUNDARY, sForm, sValue)

        httpbody += '--%s--\r\n' % HTTP_BOUNDARY
        headerlist = [
         'Content-Type: multipart/form-data; boundary=%s' % HTTP_BOUNDARY,
         'Accept-Charset: utf-8',
         'Content-Length: %s' % len(httpbody)]
        self.m_RequestObj.SendRequest(self.m_UrlInfo, headerlist, httpbody, DEFAULT_TIMEOUT, 'POST', 'request', SIMFLAG)

    def OnRequestCallBack(self, *args):
        bSuccess = args[0]
        reponseData = args[1]
        extendArg = args[3:]
        if self.m_Callback:
            self.m_Callback(self, bSuccess, reponseData, *(self.m_Arg + extendArg))
