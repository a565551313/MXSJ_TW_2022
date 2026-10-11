# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\dgw.py
import C_dgw, json, misc
STATE_STOP = 0
STATE_RESPONSE = 1
STATE_TESTING = 2
g_State = STATE_STOP
g_Callback = None
g_WarnningList = []

def ModuleReset():
    global g_Callback
    global g_State
    global g_WarnningList
    g_State = STATE_STOP
    g_Callback = None
    g_WarnningList = []
    C_dgw.StopEcho()
    return


def Loop():
    global g_State
    if g_State == STATE_RESPONSE:
        data = C_dgw.GetResponseData()
        if data:
            (iType, result, data) = data
            if data:
                data = data.decode('utf-8').encode('gbk')
            g_State = STATE_TESTING
            OnRequestCallback(iType, result, data)
    elif g_State == STATE_TESTING:
        pass
    return


def StartRequest(json_config, callback, *args):
    r"""\xaeھ\xdajson_config\xa4\xba\xb0t\xb8m\xa6r\xacq\xa8ӱҰ\xcaDGW\xbdШD\xaaA\xb0Ⱦ\xb9\xa1A\xa6A\xa6\xac\xa8\xec\xa4\xcf\xf5X\xab\xe1\xa1A\xb1N\xb5\xb2\xaaG\xa6^\xbdզ\xdccallback\xa4\xa4
        """
    global g_Callback
    global g_State
    StopRequest()
    if callable(callback):
        g_Callback = (
         callback, args)
    json_config = misc.ConventToUtf8String(json_config)
    result = C_dgw.AccessRequest(json_config)
    print result
    if result > 0:
        g_State = STATE_RESPONSE
    else:
        g_State = STATE_STOP
        warning_msg = 'AccessRequest   %s' % GetDgwError(result)
        AddWarning(warning_msg)
        OnCallback(json.write({'result': result, 'desc': warning_msg}))
    return


def StopRequest():
    r"""\xb0\xb1\xa4\xeeDGW\xbdШD
        """
    global g_State
    if g_State:
        g_State = STATE_STOP
        C_dgw.StopEcho()
    return


def StartEcho():
    C_dgw.AccessResponse()
    return


def GetServerList():
    r"""\xc0\xf2\xa8\xfa\xa5i\xa5ΪA\xb0Ⱦ\xb9\xa6C\xaa\xed\xa1A\xae榡\xac\xb0[(\xa9и\xb9, \xb7~\xb0ȪA\xa6a\xa7}, udpPort, tcpPort, \xacO\xa7_\xb9\xea\xc5\xe9\xaaA), ...]
        """
    (size, servers) = C_dgw.GetTargetServers()
    if size < 0:
        AddWarning('GetTargetServers   %s' % GetDgwError(size))
        return []
    return servers


def GetAverateDelay(ip, udpPort, tcpPort):
    r"""\xb3\xe6\xa6\xec\xb2@\xac\xed\xa1A\xaa\xf0\xa6^\xb3̪\xf1\xa4@\xa6\xb8\xb4\xfa\xb3t\xaa\xba\xb9\xea\xaeɩ\xb5\xae\xc9(\xa4\xba\xb3\xa1\xa5\xad\xa7\xa12\xac\xed\xa7\xf3\xb7s\xa4@\xa6\xb8)
        """
    result = C_dgw.GetDelay(2, ip, udpPort, tcpPort)
    if result < 0:
        AddWarning('GetDelay(2, %s, %d, %d)   %s' % (ip, udpPort, tcpPort, GetDgwError(result)))
        return 3000
    return result


def GetTenDelay(ip, udpPort, tcpPort):
    r"""\xb3\xe6\xa6\xec\xb2@\xac\xed\xa1A\xaa\xf0\xa6^\xab\xfc10\xa6\xb8\xb4\xfa\xb3t\xaa\xba\xa5\xad\xa7\xa1\xa9\xb5\xae\xc9
        """
    result = C_dgw.GetDelay(1, ip, udpPort, tcpPort)
    if result < 0:
        AddWarning('GetDelay(1, %s, %d, %d)   %s' % (ip, udpPort, tcpPort, GetDgwError(result)))
        return 3000
    return result


def GetEchoWithNormal(normal):
    r"""\xc0\xf2\xa8\xfa\xb7~\xb0ȪA\xb9\xef\xc0\xb3\xaa\xba\xb4\xfa\xb3t\xaaA
        """
    (result, echo) = C_dgw.GetParam(1, normal)
    if result <= 0:
        AddWarning('GetParam(1, %s)   %s' % (normal, GetDgwError(result)))
        return ''
    return echo


def SetSuccessServer(ip, udpPort, tcpPort):
    r"""\xa6\xa8\xa5\\xb3s\xa4W\xb9C\xc0\xb8\xaaA\xb0Ⱦ\xb9\xab\xe1\xa1A\xa5Φ\xb9\xb1\xb5\xa4f\xa7i\xaa\xbeDGW\xaaA\xb0Ⱦ\xb9
        """
    result = C_dgw.SetStatus(7, 1, '%s:%d:%d' % (ip, udpPort, tcpPort))
    if result <= 0:
        AddWarning('SetStatus(7, 1, "%s:%d:%d")   %s' % (ip, udpPort, tcpPort, GetDgwError(result)))
    return


def SetFail(feedback_msg):
    r"""\xa6VDGW\xaaA\xb0Ⱦ\xb9\xb5o\xb0e\xbf\xf9\xbb~\xa4\xcf\xf5X
        """
    result = C_dgw.HttpSend(feedback_msg)
    if result <= 0:
        AddWarning('HttpSend(%s)   %s' % (feedback_msg, GetDgwError(result)))
    return


def OnRequestCallback(iType, result, data):
    if iType == 1:
        AddWarning('GetResponseData 1,%d:%s' % (result, data))
        OnCallback(json.write({'result': result, 'desc': data}))
    elif iType == 2:
        if result == 0:
            OnCallback(data)
        else:
            AddWarning('GetResponseData 2,%d:%s' % (result, data))
            OnCallback(json.write({'result': result, 'desc': (GetRequestError(result))}))
    else:
        AddWarning('GetResponseData %d,%d:%s' % (iType, result, data))
        OnCallback(json.write({'result': (-1), 'desc': 'GetResponseData type值異常'}))
    return


def OnCallback(error_msg):
    global g_Callback
    if g_Callback:
        (callback, args) = g_Callback
        g_Callback = None
        callback(error_msg, *args)
    return


def AddWarning(warning_msg):
    g_WarnningList.append(warning_msg)
    LOG_WARN('[dgw warning]', warning_msg)
    print warning_msg
    return


def GetWarning():
    return ('\n').join(g_WarnningList)


DGW_SUCCESS = 1
DGW_FAILED = 0
DGW_OTHER_ERR = -1
DGW_NOT_INIT = -2
DGW_PARAM_ERR = -3
DGW_JSON_READ_FAILED = -4
DGW_JSON_READ_PART_FAILED = -5
DGW_INI_READ_FAILED = -6
DGW_NO_DEFAULT_LINK_SERVER = -7
DGW_NO_ECHO_SERVER = -8
DGW_SOCKET_ERROR_NORMAL_LINK = -9
DGW_RECVBUF_LENGTH_LACK = -10
DGW_CONNECT_SAME_SERVER = -11
DGW_ALREADY_STARTUDP = -12
DGW_ALREADY_STOPUDP = -13
DGW_ADDRESS_NOT_EXIST = -20
DGW_NO_ECHO_RESULT = -21
DGW_ECHO_AREADY_START = -22
DGW_ECHO_NOT_START = -23
DGW_ECHO_PART_NOTFOUND = -24
DGW_NO_PROXY_SERVER = -25
DGW_NOT_PROXY_SERVER = -26
DGW_VER1_REFUSE = -48
DGW_VER2_REFUSE = -49
DGW_HTTP_INIT_FAILED = -50
DGW_HTTP_SERVERS_READ_FAILED = -51
DGW_HTTP_REQUEST_FAILED = -52
DGW_HTTP_WAIT = -53
DGW_ACCESS_JSON_PARSE_FAILED = -54
DGW_ACCESS_JSON_READ_FAILED = -55
DGW_HTTP_RET_ERROR = -56
DGW_AUDIO_FAILED = -57
ErrorDict = {1: '成功', 
   0: '失敗', 
   (-1): ' 其他錯誤', 
   (-2): ' 沒有初始化.(用InitUdp初始化)', 
   (-3): ' 參數錯誤 ', 
   (-4): 'json讀取失敗(json字符串格式不對導致)\nInitUdp返回此值，可以繼續使用其它接口，但StartUdp時選擇連接服服務器可能會不準確，因為不知道用戶的運營商與經緯度, 除非通過Update來更新\nUpdate返回此值，表示更新失敗', 
   (-5): 'json字符串格式基本正確，但只有部分內容可以成功解析, 剩餘內容無法解析\nInitUdp返回此值,可以繼續使用其它接口，後面需要通過Update來更新服務器信息。\nUpdate返回此值，表示更新失敗', 
   (-6): '配置文件讀取失敗(可以使用udp業務數據通信功能，但無法測速)', 
   (-7): '沒找到要連接的服務器\n需要重新InitUdp,或者在StartUdp中傳入服務器地址,或者用Update更新', 
   (-8): '沒有測速服務器(讀完配置文件沒找到或者找到測速服務器到啟動測速失敗,所以不能進行測速,但可正常使用udp收發業務數據)\n需要重新InitUdp, 或者用Update更新', 
   (-9): '創建業務數據通信線路失敗。（非測速udp）', 
   (-10): 'UdpRecvFrom傳入的長度太小，導致本次獲取數據失敗', 
   (-11): b"StartU+?co\xea'\xfc<\xeb\x0f\xe2\x9c\xeb8\xf7(\xfc<\xb1\xb5\xaa\xba\xaaA\xb0\xc8\xbe\xb9", 
   (-12): '已經啟動了業務數據通信功能。(一期功能中 Update 時，需要先StopUdp)', 
   (-13): '已經停止了業務數據通信功能', 
   (-20): '地址不存在或者是沒有對應的測速線路', 
   (-21): '1.GetDelay(1,x,x)獲取平均延時，表示 10次測速之後，才計算出平均延時;\n2.GetDelay(2,x,x)獲取當前實時延時，表示暫未獲取結果。', 
   (-22): '測速功能已經啟動了', 
   (-23): '測速功能沒有啟動(StopEcho時返回)', 
   (-24): '至少有一個業務服務器，沒有在配置文件中找到對應的測速線路\n其他找到的測試線路會啟動測速', 
   (-25): '沒有代理服。(假如關閉了對實體服測速，但收到的所有業務服都是實體服)', 
   (-26): '不是代理服。(調用StartUdp時傳入了指定的服務器地址，並且這個服務器是實體服，但已經停止了對實體服測速)', 
   (-48): '使用一期功能時不能調用二期的部分接口', 
   (-49): '使用二期功能時不能調用一期的部分接口', 
   (-50): 'Http功能初始化失敗', 
   (-51): '讀DGW接入服的配置文件失敗', 
   (-52): 'Http請求失敗', 
   (-53): '已經成功請求，請等待結果返回', 
   (-54): 'AccessRequest中傳入的json格式不正確', 
   (-55): 'AccessRequest中傳入的json中缺少關鍵字段（"proid"或"bsid"或"port"）', 
   (-56): 'http接入服返回錯誤', 
   (-57): 'only for IM use DGW. '}

def GetDgwError(error):
    return '%d:%s' % (error, ErrorDict.get(error, '未知錯誤'))


RequestErrorDict = {1: '業務服務器響應超時', 
   2: '業務服務器負載滿', 
   3: '無可用的dgw代理', 
   4: 'DGW接入服務響應超時', 
   5: '短時間請求太多', 
   6: '被禁止請求', 
   7: '非法請求,一般格式不對', 
   8: 'http頭有問題', 
   9: 'http方法有問題', 
   10: '參數問題'}

def GetRequestError(error):
    return '%d:%s' % (error, RequestErrorDict.get(error, '未知訪問錯誤'))


def Test():

    def OnRequestTest(msg):
        dct = json.read(msg)
        if dct.get('result') != 0:
            print '測試用例失敗'
            return
        print '獲取服務器列表成功'
        for value in dct['servers']:
            print value['s'][0]['normal']

        def DelayFunc(obj, shadow, func, tick):
            print func.__name__
            for (_, ip, udp_port, tcp_port, _) in GetServerList():
                print ip, udp_port, tcp_port, func(ip, udp_port, tcp_port)

            if tick > 0:
                return (
                 shadow, func, tick - 1)
            return

        import interface
        obj = interface.CBaseObject(None)
        obj.CreatePyCommand(30, DelayFunc, obj, GetAverateDelay, 20)
        obj.CreatePyCommand(30, DelayFunc, obj, GetTenDelay, 0)
        return

    json_config = '{\n"proid" : 2,\n"bsid" : 20103,\n"port" : 7777,\n"conf":"dgw.ini",\n"echo_real" : 1,\n"switch_open" : 1,\n"switch_limit" : 50,\n"packet_len_limit" : 512\n}'
    StartRequest(json_config, OnRequestTest)
    return


return
