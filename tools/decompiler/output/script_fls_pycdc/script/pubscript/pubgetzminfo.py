# pycdc 交叉复核产物 · script.fls entry 3028
# co_filename(原始)='script/pubscript/pubgetzminfo.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3028.pyc (Python 2.5)

'''\xb4\xf3\xca\xfd\xbe\xdd\xcd\xb3\xbc\xc6\xd5\xbd\xc3\xcb\xd0\xc5\xcf\xa2
\xbf\xcd\xbb\xa7\xb6\xcb\xb1\xbe\xb5\xd8\xc5\xd0\xb6\xcf\xd3\xd0\xce\xde\xb0\xb2\xd7\xb0\xd5\xbd\xc3\xcb\xa1\xa2\xd4\xcb\xd0\xd0\xd5\xbd\xc3\xcb\xa1\xa2\xb1\xbe\xb4\xce\xc6\xf4\xb6\xaf\xca\xc7\xb7\xf1\xd3\xc9\xd5\xbd\xc3\xcb\xc6\xf4\xb6\xaf\xc1\xcb\xd3\xce\xcf\xb7\xbf\xcd\xbb\xa7\xb6\xcb\xa3\xac\xb0\xd1\xbd\xe1\xb9\xfb\xb7\xa2\xb8\xf8\xb4\xf3\xca\xfd\xbe\xdd\xd7\xf6\xcd\xb3\xbc\xc6
'''
import pubimtools
import pubnetbigdata
import pubtoolkit
import interface
g_HasSended = False
g_ZMState = None

def StartSend(zmlogin, heroid, scriptversion):
    global g_ZMState
    g_ZMState = CSendZMState(zmlogin, heroid, scriptversion)


def StopSend():
    global g_ZMState
    if g_ZMState:
        g_ZMState.StopSend()
        g_ZMState = None
    


class CSendZMState(interface.CBaseObject):
    
    def __init__(self, zmlogin, heroid, scriptversion):
        interface.CBaseObject.__init__(self, None)
        
        def SleepFunc(obj):
            obj.GetResult(zmlogin, heroid, scriptversion)

        self.m_Cmd = self.CreatePyCommand(1800, SleepFunc)

    
    def StopSend(self):
        if getattr(self, 'm_Cmd', None):
            self.m_Cmd.Release()
            self.m_Cmd = None
        

    
    def GetResult(self, zmlogin, heroid, scriptversion):
        import pubsubgather
        import time
        import pubmisc
        serverID = pubtoolkit.GetSvrID()
        IP = pubtoolkit.GetIP()
         = pubsubgather.GetDYTID()
        current = pubtoolkit.GetServerTime()
        flag = GetFlag(zmlogin)
        format_lst = [
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current)),
            '%d' % serverID,
            'c_event_mx_1.0',
            '1',
            'yiwang_entergame',
            '.'.join(map(str, scriptversion)),
            'windows %s' % pubmisc.GetSYSVersion(),
            ,
            '%d' % heroid,
            '%d' % flag,
            '3',
            IP,
            '',
            pubtoolkit.GetMAC(),
            '',
            '']
        content = '\t'.join(format_lst)
        format_desc = '{"headers":{},"body":"' + content + '"}'
        result = pubmisc.ConventToUtf8String('[' + format_desc + ']')

    
    def HttpSendResult(self, result):
        import pubgameurl
        url = pubgameurl.GetUrl('\xa4j\xbc\xc6\xbe\xda\xa4W\xb6\xc7')
        pubnetbigdata.CUpLoad(url, result, self.CallBack)

    
    def CallBack(self, data, success):
        global g_HasSended
        if not success:
            print '\xb3s\xb1\xb5\xa4j\xbc\xc6\xbe\xda\xbf\xf9\xbb~%s' % data
        else:
            g_HasSended = True



def GetFlag(zmlogin):
    flag = 1
    if zmlogin:
        flag = 4
    elif pubimtools.IsImRunning():
        flag = 3
    elif pubimtools.IsIMSetuped():
        flag = 2
    
    return flag
