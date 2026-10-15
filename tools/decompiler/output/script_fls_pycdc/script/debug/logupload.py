# pycdc 交叉复核产物 · script.fls entry 2769
# co_filename(原始)='script/debug/logupload.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2769.pyc (Python 2.5)

import publogupload
g_Upload = None

def ModuleReset():
    global g_Upload
    g_Upload = None


def GetUploadObj():
    global g_Upload
    if not g_Upload:
        g_Upload = CUpload()
    
    return g_Upload


def Upload(itype, msg):
    GetUploadObj().UploadLog(itype, msg)


def UploadBebugLog(msg):
    GetUploadObj().UploadLog(CUpload.TYPE_DEBUG, msg)


def UploadLoginLog(msg):
    GetUploadObj().UploadLog(CUpload.TYPE_LOGIN, msg)


def UploadGMReportLog(msg):
    GetUploadObj().UploadLog(CUpload.TYPE_GM_REPORT, msg)


def UploadClicksLog(msg):
    GetUploadObj().UploadLog(CUpload.TYPE_CLICKS, msg)


def UploadC2SLog(msg):
    GetUploadObj().UploadLog(CUpload.TYPE_C2S_INVALID, msg)


def UploadBBDKLog(msg):
    GetUploadObj().UploadLog(CUpload.TYPE_BBDK, msg)


class CUpload(publogupload.CUpload):
    
    def GetBaseData(self):
        import netlogin
        import hero
        import net
        import pubtoolkit
        import versions
        import C_sys
        import pubbigdatafunc
        gate = 'mx_tw'
        if net.g_Net:
            server_id = str(pubtoolkit.GetSvrID())
            server_name = net.g_Net.GetServerName()
            account = netlogin.GetCurrAccount()
        else:
            server_id = '0'
            server_name = '\xa5\xbc\xaa\xbe\xaaA\xb0\xc8\xbe\xb9'
            account = '0'
        hero_id = str(hero.g_ID)
        import misc
        baseInfo = {
            'gate': gate,
            'script_ver': versions.GetFullVersion(),
            'server_id': server_id,
            'server_name': misc.BIG52UTF8(server_name),
            'hero_id': hero_id,
            'account': account,
            'engine_ver': '%s(%s)' % ('.'.join(map(str, versions.GetEngineVersion())), C_sys.IsLogDebug()),
            'mac': str(pubbigdatafunc.GetMAC()) }
        return baseInfo

    
    def UploadLog(self, itype, msg, msg_md5 = None, bIsUTF8 = False):
        '''
\t\t\xa4W\xb6\xc7Log
\t\t:param itype: \xbf\xf9\xbb~\xc3\xfe\xab\xac
\t\t:param msg: \xbf\xf9\xbb~\xabH\xae\xa7
\t\t:param msg_md5: md5
\t\t:return:
\t\t'''
        global RealUploadLog
        import frametaskmgr
        import misc
        import item
        import delayloading
        if not item.IsItemSendEnd() or delayloading.IsShowLoading():
            RealUploadLog = self
            None(frametaskmgr.GetFrameTaskMgr().AddAfterLoadingTask, 30(misc.Functor, itype, msg, msg_md5))
        else:
            self.RealUploadLog(itype, msg, msg_md5)

    
    def RealUploadLog(self, itype, msg, msg_md5 = None):
        result = publogupload.CUpload.UploadLog(self, itype, msg, msg_md5)
        if result:
            (url, data, log_md5) = result
            import pubhttp
            pubhttp.CUpload(url, { }, data, self.OnSendLogResult, log_md5)
        

    
    def GetUrl(self):
        '''
\t\t\xae\xda\xbe\xda\xa4\xba\xba\xf4\xa8\xd3\xc0\xf2\xa8\xfa\xb1\xc0\xb0e\xa6a\xa7}
\t\t:return:
\t\t'''
        import pubgameurl
        if self.IsInner():
            return pubgameurl.GetUrl('\xb3\xf8\xbf\xf9\xabH\xae\xa7\xa4\xba\xaaA')
        else:
            return pubgameurl.GetUrl('\xb3\xf8\xbf\xf9\xabH\xae\xa7')

    
    def IsInner(self):
        '''
\t\t\xa7P\xc2_\xa4\xba\xa5~\xba\xf4
\t\t:return:
\t\t'''
        import permission
        return permission.IsInNet()
