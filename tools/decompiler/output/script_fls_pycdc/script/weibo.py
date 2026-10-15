# pycdc 交叉复核产物 · script.fls entry 1864
# co_filename(原始)='script/weibo.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1864.pyc (Python 2.5)

import net
import misc
import interface
URL_DEBUG = 0

def Trans(txt):
    return txt


class CHttpObject(net.CHttpObject):
    
    def __init__(self, url, name, callback, *arg):
        self.m_Callback = callback
        self.m_Arg = arg
        import whitewebsite
        if not whitewebsite.CheckUrlIsInWhite(url):
            return None
        
        (server, port, file) = net.GetUrlInfo(url)
        net.CNetClient.__init__(self)
        self.Connect(server, port)
        name = misc.Quote(name)
        hoststr = server
        info = 'GET /n/%s HTTP/1.1\r\n' % name + 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4\r\n' + 'Host: %s\r\n' % hoststr + 'Connection: Close\r\n\r\n'
        info = Trans(info)
        self.NakedSend(info)
        if URL_DEBUG:
            print '\xc3\xec\xb1\xb5\xa1G', url
            print 'info:', info
        
        self.m_Data = ''
        
        def NetProcess(obj):
            data = self.Process()
            if data:
                self.m_Data += data
            
            return ()

        self.m_Timer = interface.CBaseObject(None)
        self.m_Timer.CreatePyCommand(0, NetProcess)
        net.g_HttpObjectList.append(self)



def 
,;4itWeiBoName(dlg, name):
    if name.startswith('@'):
        name = name[1:]
    
    if not name:
        return None
    
    web = 'http://m.weibo.cn'
    txt = misc.ConventToUtf8String(name)
    CHttpObject(web, txt, OnReceiveProcess, [
        name,
        dlg])


def OnReceiveProcess(data, succeed, args):
    import netnpc
    import usermacro
    name = args[0].replace('\t', '')
    if not succeed and data:
        netnpc.C2SNpcInput(args[1], name + '|-1')
        return None
    
    uid = GetWeiBoID(data)
    txt = name + '|' + uid
    netnpc.C2SNpcInput(args[1], txt)
    print '--weibo C2SNpcInput----', args[1], txt


def GetWeiBoID(data):
    import re
    uidpatt = re.compile('"uid":"(?P<uid>[0-9]+)"')
    matchobj = uidpatt.search(data)
    if matchobj:
        uid = str(matchobj.group('uid'))
        return uid
    
    return '0'
