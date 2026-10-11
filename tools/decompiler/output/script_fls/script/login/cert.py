# -*- coding: utf-8 -*-
# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\login\cert.py
"""
//dll\\xbdӿڶ\\xa8\\xd2壺

//\\xd7\\xf7  \\xd3\\xc3: \\xb3\\xf5ʼ\\xbb\\xaf\\xb8\\xf7\\xb8\\xf6\\xb2\\xce\\xca\\xfd\\xa3\\xac\\xb0\\xfc\\xc0\\xa8\\xb4\\xb4\\xbd\\xa8\\xc8\\xd5־\\xceļ\\xfe\\xa3\\xa8ͨ\\xb9\\xfd\\xb6\\xc1\\xc5\\xe4\\xd6\\xc3\\xceļ\\xfe\\xbe\\xf6\\xb6\\xa8\\xcaǷ\U00074d3d\\xa8\\xa3\\xa9\\xa1\\xa3\\xca\\xd7\\xcf\\xc8Ӧ\\xb8õ\\xf7\\xd3ñ\\xbe\\xba\\xaf\\xca\\xfd\\xa1\\xa3
//              ע\\xa3\\xbaֻ\\xc4\\xdcһ\\xb4ε\\xf7\\xd3ó\\xf5ʼ\\xbb\\xaf\\xd5\\xfdȷ\\xa3\\xac\\xbc\\xb4\\xb3\\xf5ʼ\\xbb\\xaf\\xb3ɹ\\xa6\\xba\\xf3\\xd4ٳ\\xf5ʼ\\xbb\\xaf\\xbb᷵\\xbb\\xd8ʧ\\xb0ܣ\\xacȷ\\xb1\\xa3\\xcd\\xf8\\xc2\\xe7\\xb5\\xd8ַ\\xbaͶ˿\\xda\\xd2Լ\\xb0·\\xbe\\xb6\\xc9\\xe8\\xd6\\xc3\\xd5\\xfdȷ\\xa1\\xa3
//\\xb7\\xb5\\xbb\\xd8ֵ: const char*:                       // \\xb4\\xe6\\xb7\\xc5\\xd5\\xfb\\xca\\xfd\\xd7ַ\\xfb\\xb4\\xae\\xa1\\xa3\\xb4\\xf3\\xd3ڵ\\xc8\\xd3\\xda0\\xb1\\xedʾ\\xb3ɹ\\xa6\\xa3\\xacС\\xd3\\xda0\\xb1\\xedʾʧ\\xb0ܡ\\xa3
const char* DYCERT_Init(
        const char* szProtocol,         // ֻ\\xc4\\xdc\\xcaǡ\\xb0http\\xa1\\xb1\\xbb\\xf2\\xd5ߡ\\xb0https\\xa1\\xb1
        const char* szHost,                     // \\xd6\\xf7\\xbb\\xfa\\xb5\\xd8ַ\\xa3\\xac\\xb1\\xc8\\xc8硰192.168.165.86\\xa1\\xb1\\xa3\\xac\\xa1\\xb0dy.henhaoji.com\\xa1\\xb1
        const char* szPort,                     // \\xc9\\xe8\\xd6\\xc3\\xc7\\xeb\\xc7\\xf3\\xb5Ķ˿ںţ\\xac\\xb1\\xc8\\xc8硰443\\xa1\\xb1\\xa3\\xac\\xa1\\xb08080\\xa1\\xb1
        const char* szRootCertPath,     // \\xb8\\xf9֤\\xca\\xe9\\xb5\\xc4·\\xbe\\xb6\\xc3\\xfb\\xd7֣\\xac\\xb1\\xc8\\xc8硰Dyca/duoyica.crt\\xa1\\xb1
        const char* szRootCertName, // \\xb8\\xf9֤\\xca\\xe9\\xb5\\xc4\\xc3\\xfb\\xd7֣\\xac\\xb1\\xc8\\xc8硰DuoYi Network Root CA\\xa1\\xb1
        const char* pParam                      // \\xb1\\xa3\\xc1\\xf4\\xc0\\xa9չ\\xd3\\xc3
);

//\\xd7\\xf7  \\xd3\\xc3: \\xb0\\xb2װP12֤\\xca飬\\xd0\\xe8Ҫ\\xccṩ\\xd3û\\xa7\\xc3\\xfb\\xd7֣\\xac\\xba\\xaf\\xca\\xfd\\xc4ڲ\\xbf\\xbb\\xe1\\xb8\\xf9\\xbe\\xdd\\xd3û\\xa7\\xc3\\xfb\\xba\\xcdpc\\xd0\\xc5Ϣ\\xd7\\xe9\\xbaϳ\\xc9֤\\xca\\xe9\\xc3\\xfb\\xd7֡\\xa3\\xbb\\xe1\\xd7Զ\\xaf\\xb0\\xb2װ\\xb8\\xf9֤\\xca\\xe9
//                      ע\\xa3\\xba\\xd0\\xe8Ҫ\\xcfȵ\\xf7\\xd3\\xc3DYCERT_Init\\xa1\\xa3\\xc8\\xe7\\xb9\\xfb\\xd4\\xdaDYCERT_Init\\xd6\\xd0\\xc9\\xe8\\xd6õķ\\xfe\\xce\\xf1\\xc6\\xf7\\xb5\\xd8ַ\\xbaͶ˿ڴ\\xed\\xce\\xf3\\xbb\\xf2\\xd5߷\\xfe\\xce\\xf1\\xc6\\xf7\\xb2\\xbbͨ\\xa3\\xac\\xd3п\\xc9\\xc4ܻᵼ\\xd6º\\xaf\\xca\\xfdԼ20\\xc3\\xeb\\xba\U000f7d7b\\xd8ʧ\\xb0ܡ\\xa3
//\\xb7\\xb5\\xbb\\xd8ֵ: const char* \\xa3\\xba               // \\xb4\\xe6\\xb7\\xc5\\xd5\\xfb\\xca\\xfd\\xd7ַ\\xfb\\xb4\\xae\\xb1\\xedʾ\\xa3\\xac\\xb4\\xf3\\xd3ڵ\\xc8\\xd3\\xda0\\xb1\\xedʾ\\xb3ɹ\\xa6\\xa3\\xacС\\xd3\\xda0\\xb1\\xedʾʧ\\xb0ܡ\\xa3
const char* DYCERT_InstallP12(
        const char* szUName,            // \\xd3û\\xa7\\xc3\\xfb\\xa3\\xac3<=\\xb3\\xa4\\xb6\\xc8<64\\xd7ֽڡ\\xa3\\xc8\\xf4ʹ\\xd3÷\\xc7ascii\\xc2\\xeb\\xbb\\xe1\\xb3\\xf6\\xce\\xca\\xcc⡣
        const char* szPlace,            // ʹ\\xd3õص\\xe3\\xb2\\xce\\xca\\xfd
        const char* szVerifyCode,       // \\xb7\\xfe\\xce\\xf1\\xb6˷\\xa2\\xc0\\xb4\\xb5\\xc4\\xca\\xdaȨ\\xc2\\xeb
        const char* szGate                      // \\xd3\\xceϷ\\xb1\\xea\\xbcǣ\\xacͳһ\\xd3\\xc3'my'
);

//\\xd7\\xf7  \\xd3\\xc3: \\xbb\\xf1ȡָ\\xb6\\xa8\\xd3û\\xa7\\xc3\\xfb\\xb5\\xc4֤\\xca飬\\xd3\\xc3֤\\xca\\xe9\\xb6\\xd4ָ\\xb6\\xa8\\xd1\\xe9֤\\xc2\\xeb\\xbd\\xf8\\xd0\\xd0ǩ\\xc3\\xfb\\xa1\\xa3
//                      ע\\xa3\\xba\\xd0\\xe8Ҫ\\xcfȵ\\xf7\\xd3\\xc3DYCERT_Init\\xb3\\xf5ʼ\\xbb\\xaf
//\\xb7\\xb5\\xbb\\xd8ֵ: const char* \\xa3\\xba               // \\xb7\\xfe\\xce\\xf1\\xc6\\xf7\\xb5ķ\\xb5\\xbb\\xd8\\xc4\\xda\\xc8ݣ\\xac\\xd5\\xfd\\xb3\\xa3\\xbb᷵\\xbbأ\\xba\\xa1\\xb0result=0;token=KLFDSCXf432543fds\\xa1\\xb1\\xa1\\xa3ʧ\\xb0ܻ᷵\\xbbش\\xed\\xce\\xf3\\xc2룺\\xa1\\xb0result=-1000;\\xa1\\xb1\\xb5ȡ\\xa3
const  char* DYCERT_CheckP12(
        const char* szUName,            // \\xd3û\\xa7\\xc3\\xfb\\xd7֣\\xac\\xd4\\xddʱֻ֧\\xb3\\xd6ascii\\xb1\\xe0\\xc2롣
        const char* szVerifyKey         // 32λ\\xd1\\xe9֤\\xc2\\xeb
);

// \\xd7\\xf7  \\xd3\\xc3: ɾ\\xb3\\xfdָ\\xb6\\xa8\\xd3û\\xa7\\xb5\\xc4֤\\xca飬ֻ\\xd0\\xe8Ҫ\\xd4ڿͻ\\xa7\\xb6\\xcbɾ\\xb3\\xfd\\xa3\\xac\\xb2\\xbb\\xd3\\xc3֪ͨ\\xb7\\xfe\\xce\\xf1\\xc6\\xf7\\xba\\xcd\\xca\\xfd\\xbe\\xdd\\xd6\\xd0\\xd0\\xc4
//                      ע\\xa3\\xba\\xd0\\xe8Ҫ\\xcfȵ\\xf7\\xd3\\xc3DYCERT_Init\\xa1\\xa3\\xc8\\xe7\\xb9\\xfb\\xd4\\xdaDYCERT_Init\\xd6\\xd0\\xc9\\xe8\\xd6õķ\\xfe\\xce\\xf1\\xc6\\xf7\\xb5\\xd8ַ\\xbaͶ˿ڴ\\xed\\xce\\xf3\\xbb\\xf2\\xd5߷\\xfe\\xce\\xf1\\xc6\\xf7\\xb2\\xbbͨ\\xa3\\xac\\xd3п\\xc9\\xc4ܻᵼ\\xd6º\\xaf\\xca\\xfdԼ20\\xc3\\xeb\\xba\U000f7d7b\\xd8ʧ\\xb0ܡ\\xa3
// \\xb7\\xb5\\xbb\\xd8ֵ: const char* \\xa3\\xba              // \\xb4\\xe6\\xb7\\xc5\\xd5\\xfb\\xca\\xfd\\xd7ַ\\xfb\\xb4\\xae\\xb1\\xedʾ\\xa3\\xac \\xb4\\xf3\\xd3ڵ\\xc8\\xd3\\xda0\\xb1\\xedʾ\\xb3ɹ\\xa6\\xa3\\xacС\\xd3\\xda0\\xb1\\xedʾʧ\\xb0ܡ\\xa3Ҳ\\xbf\\xc9\\xd2\\xd4ͨ\\xb9\\xfdGetLastError()\\xb5õ\\xbd\\xb4\\xed\\xce\\xf3\\xc2룬\\xce\u07b4\\xed\\xce\U000f7d7b\\xd80\\xa1\\xa3
const char* DYCERT_UninstallP12(
        const char* szUName,            // \\xd3û\\xa7\\xc3\\xfb\\xa3\\xac3<=\\xb3\\xa4\\xb6\\xc8<64\\xd7ֽڡ\\xa3\\xc8\\xf4ʹ\\xd3÷\\xc7ascii\\xc2\\xeb\\xbb\\xe1\\xb3\\xf6\\xce\\xca\\xcc⡣
        const char* pParam                      // \\xb1\\xa3\\xc1\\xf4\\xc0\\xa9չ\\xd3\\xc3
);

// \\xd7\\xf7  \\xd3\\xc3:  1.\\xbb\\xf1ȡ\\xb1\\xbe\\xbb\\xfa\\xb5Ļ\\xfa\\xc6\\xf7\\xd0\\xc5Ϣ\\xc2\\xeb(szFuncFlag==""ʱ)
//                      2.\\xbb\\xf1ȡ\\xc9\\xcfһ\\xb8\\xf6\\xba\\xaf\\xca\\xfd\\xb5ĵ\\xf7\\xd3\\xc3\\xc8\\xd5־(szFuncFlag=="GetErrLog"ʱ)
//                      (\\xb2\\xbb\\xd0\\xe8Ҫ\\xb0\\xb2װ֤\\xca\\xe9)
// \\xb7\\xb5\\xbb\\xd8ֵ: const char* \\xa3\\xba
//                      1.\\xbb\\xf1ȡ\\xb1\\xbe\\xbb\\xfa\\xb5Ļ\\xfa\\xc6\\xf7\\xd0\\xc5Ϣ\\xc2\\xebʱ\\xa3\\xac\\xb7\\xb5\\xbb\\xd8\\xd7ַ\\xfb\\xb4\\xae\\xb1\\xedʾ\\xb5Ļ\\xfa\\xc6\\xf7\\xd0\\xc5Ϣ\\xa1\\xa3\\xd5\\xfd\\xb3\\xa3\\xc7\\xe9\\xbf\\xf6\\xb7\\xb5\\xbb\\xd832\\xd7ֽڳ\\xa4\\xb6Ȼ\\xfa\\xc6\\xf7\\xc2룻\\xc8\\xe7\\xb9\\xfb\\xb3\\xf6\\xb4\\xed\\xa3\\xac\\xb7\\xb5\\xbb\\xd8\\xd7ַ\\xfb\\xb4\\xae\\xa1\\xb0-100\\xa1\\xb1\\xb5ȣ\\xac\\xb1\\xedʾ\\xb4\\xed\\xce\\xf3\\xc2롣
//                      2.\\xbb\\xf1ȡ\\xc9\\xcfһ\\xb8\\xf6\\xba\\xaf\\xca\\xfd\\xb5ĵ\\xf7\\xd3\\xc3\\xc8\\xd5־ʱ\\xa3\\xac\\xb7\\xb5\\xbb\\xd8\\xc8\\xd5־\\xd0\\xc5Ϣ\\xa1\\xa3\\xb3\\xf6\\xb4\\xed\\xb7\\xb5\\xbb\\xd8\\xd7ַ\\xfb\\xb4\\xae\\xa1\\xb0-100\\xa1\\xb1\\xb5\\xc8
const char* DYCERT_GetPCInfo(
        const char* szFuncFlag          // \\xb4\\xab"GetErrLog"\\xbb\\xf1ȡ\\xc8\\xd5־\\xa3\\xac\\xb4\\xab\\xbfջ\\xf1ȡPCINFO
);

// \\xd7\\xf7  \\xd3\\xc3: \\xb8\\xf9\\xbe\\xdd\\xd3û\\xa7\\xc3\\xfb\\xc0\\xb4\\xbb\\xf1ȡ\\xbf\\xc9\\xd3\\xc3֤\\xca\\xe9\\xb5\\xc4\\xc3\\xfb\\xd7֣\\xac\\xb2\\xbb\\xd0\\xe8Ҫ\\xb0\\xb2װ֤\\xca\\xe9
// \\xb7\\xb5\\xbb\\xd8ֵ: const char* \\xa3\\xba              // \\xd5\\xfd\\xb3\\xa3\\xb7\\xb5     j\x01\x16\x04z|\x18\\x81\\x80ed\x0fh\x07vd\x16x[qIed\x11\x1e\x00        bZ`\x18\x02\x00װ֤\\xca飻\\xc8\\xe7\\xb9\\xfb\\xb3\\xf6\\xb4\\xed\\xa3\\xac\\xb7\\xb5\\xbb\\xd8\\xd7ַ\\xfb\\xb4\\xae\\xa1\\xb0-100\\xa1\\xb1\\xb5ȣ\\xac\\xb1\\xedʾ\\xb4\\xed\\xce\\xf3\\xc2롣       
const char* DYCERT_GetCertName(
        const char* szUName,            // \\xd3û\\xa7\\xc3\\xfb\\xa3\\xac3<=\\xb3\\xa4\\xb6\\xc8<64\\xd7ֽڡ\\xa3\\xc8\\xf4ʹ\\xd3÷\\xc7ascii\\xc2\\xeb\\xbb\\xe1\\xb3\\xf6\\xce\\xca\\xcc⡣
        const char* pParam                      // \\xb1\\xa3\\xc1\\xf4\\xc0\\xa9չ\\xd3\\xc3
);
"""
import C_cert
g_HasInitCert = 0
g_TmpErrText = []
OUT_PROTOCOL = 'https'
OUT_HOST = 'dy.henhaoji.com'
OUT_PORT = '443'
OUTTEST_PROTOCOL = 'http'
OUTTEST_HOST = '192.168.165.86'
OUTTEST_PORT = '8080'
INNER_PROTOCOL = 'http'
INNER_HOST = '192.168.191.60'
INNER_PORT = '8080'
NETERROR = (-204, -404, -208)
CERT_TRYLIST = [
 ('http', '61.142.132.113', '8080')]
GATE = 'my'
CERTERRORMSG = {0: '安裝或驗証正常。', 
   (-2): '待擴展參數不能傳非空的值', 
   (-3): '傳入的用戶名等參數一定要非空', 
   (-4): '沒有初始化，即沒有調用DYCERT_Init', 
   (-5): '要求輸入用戶名字長度在[3,64)區間中', 
   (-8): '已經初始化，即已經調用過DYCERT_Init且成功，現在只支持一次成功初始化', 
   100: '証書客戶端操作正常', 
   (-101): '証書客戶端內存分配失敗', 
   (-102): '証書客戶端轉換編碼錯誤，在驗証証書提取証書內容時出錯', 
   (-103): '証書客戶端從服務器端的証書中提取証書上下文錯誤', 
   (-104): '証書客戶端打開証書庫錯誤', 
   (-105): '証書客戶端把証書上下文（即証書）添加到証書庫錯誤', 
   (-106): '証書客戶端刪除舊的証書錯誤，刪除証書時出現', 
   (-107): '証書客戶端在証書庫裡沒有找到証書，查找証書時出現', 
   (-108): '安裝根証書失敗，由於根証書會彈出框，很大可能用戶會拒絕安裝根証書', 
   (-109): '玩家取消証書的安裝', 
   (-110): '玩家取消了根証書，請玩家在安裝根証書過程中點擊確認', 
   (-111): '証書客戶端從服務器獲取的P12証書無效', 
   (-112): '証書客戶端從安裝的P12証書導入出錯', 
   (-113): '証書客戶端從導入的証書庫中找不到証書上下文', 
   200: '連接証書服務器正常', 
   (-201): '証書服務器，打開服務器出錯，沒有正確連接服務器', 
   (-202): '關閉各個句柄出錯', 
   (-203): '証書服務器，打開請求鏈接出錯', 
   (-204): '發送証書請求失敗，請等候再試', 
   (-205): '証書服務器，獲取服務器返回碼失敗，比如服務器返回404，卻沒有收到', 
   (-206): '証書服務器，沒有建立和服務的通信鏈接', 
   (-207): '証書服務器，返回頭不符合規定，比如要求返回result=0+証書內容，如果返回頭不是result=0，則出錯', 
   (-404): '無法訪問証書服務器', 
   (-500): '証書服務器返回空', 
   (-501): '傳給服務器的用戶名無效', 
   (-502): '傳給服務器的序列號無效，現在不需要序列號了', 
   (-503): '傳給服務器的用戶名長度無效', 
   (-504): '傳給服務器的電腦標識長度無效', 
   (-505): '傳給服務器的序列號重複，現在不需要序列號了', 
   (-506): '服務器讀取証書錯誤，驗証証書時出現', 
   (-507): '服務器創建証書失敗，申請証書時出現', 
   (-508): '服務器保存數據庫出錯', 
   (-601): '申請証書時傳入的驗証碼錯誤', 
   1000: '數字証書相關操作正常', 
   (-1001): '沒有正確初始化', 
   (-1002): '內存分配失敗', 
   (-1003): '不能正確獲取電腦標識', 
   (-1004): '驗証証書時解析証書的序列號有錯', 
   (-1005): '獲取HCRYPTPROV句柄失敗', 
   (-1006): '從証書中導出公鑰失敗', 
   (-1007): '創建bio失敗', 
   (-1008): '從bio中獲取公鑰失敗', 
   (-1009): 'base64加密失敗', 
   (-1010): '創建簽名出錯', 
   (-1011): '創建簽名之前的預處理出錯，比如分配內存，或者要簽名的數據太長', 
   (-1012): '獲取私鑰出錯', 
   (-1013): '創建hash出錯，簽名用的是SHA1，調用CryptCreateHash出錯', 
   (-1014): '調用CryptHashData出錯', 
   (-1015): '調用CryptSignHash出錯', 
   (-1016): '調用Base64Encode出錯', 
   1100: '設置配置正常', 
   (-1101): '協議不正確，只能是http或者https', 
   (-1102): '主機域名或者ip出錯', 
   (-1103): '端口號不正確', 
   (-1104): '根証書獲取路徑出錯，只需正確設置即可', 
   (-1105): '根証書名字出錯，只需正確設置即可', 
   1200: '日誌相關初始化正常', 
   (-1201): '日誌相關初始化錯誤', 
   (-10000): '証書操作引發致命錯誤'}

def CertInitialize(isCache=0):
    global g_HasInitCert
    import cfg
    if g_HasInitCert:
        res = 0
    else:
        (protocol, host, port) = GetCertServer()
        try:
            iUseIP = int(cfg.GetData('mx.ini', 'Game', 'isdirect'))
        except:
            iUseIP = 0

        if iUseIP == 2:
            try:
                sFinal = ''
                temp = cfg.GetData('mx.ini', 'Game', 'directiii')
                for (idx, i) in enumerate(temp):
                    sFinal += '趕r'(ord(i) + idx)

                host = sFinal
            except:
                pass

        elif iUseIP == 1:
            host = '121.201.116.99'
        try:
            res = C_cert.DYCERT_Init(protocol, host, port, 'Dyca/duoyica.crt', 'DuoYi Network Root CA', '')
        except:
            res = '-1'

        res = CheckResErr(res, 'DYCERT_Init', isCache)
        if res >= 0 or res == -8:
            g_HasInitCert = 1
    return res


def CertInstall(username, address, verifycode, isCache=0):
    tmpRet = CertInitialize(isCache)
    if tmpRet < 0 and tmpRet != -8:
        return tmpRet
    username = username.lower()
    res = CertInstallBySingleTime(username, address, verifycode, isCache)
    if GetCodeByRes(res) in NETERROR:
        tmpres = CertInstallByMultiTimes(username, address, verifycode, isCache)
        if tmpres is not None:
            res = tmpres
    res = CheckResErr(res, 'DYCERT_InstallP12', isCache)
    return res


def CertInstallByMultiTimes(username, address, verifycode, isCache=0):
    sInstallRes = None
    for (sProtocol, sHost, iPort) in CERT_TRYLIST:
        try:
            res = C_cert.DYCERT_Init(sProtocol, sHost, iPort, 'Dyca/duoyica.crt', 'DuoYi Network Root CA', '')
        except:
            res = '-1'

        if GetCodeByRes(res) >= 0:
            sInstallRes = CertInstallBySingleTime(username, address, verifycode, isCache)
            if GetCodeByRes(sInstallRes) not in NETERROR:
                break

    return sInstallRes


def CertInstallBySingleTime(username, address, verifycode, isCache=0):
    try:
        res = C_cert.DYCERT_InstallP12(username, address, verifycode, GATE)
    except:
        res = '-1'

    return res


def GetCodeByRes(sRes):
    try:
        if sRes.startswith('-') and sRes[1:].isdigit():
            return 0 - int(sRes[1:])
        elif sRes.isdigit():
            return int(sRes)
        else:
            return -1
    except:
        return -1

    return


def CertCheck(username, sValiCode, isCache=0):
    import re
    tmpRet = CertInitialize(isCache)
    if tmpRet < 0 and tmpRet != -8:
        return (tmpRet, '')
    username = username.lower()
    try:
        retStr = C_cert.DYCERT_CheckP12(username, sValiCode)
    except:
        retStr = 'result=-1;'

    if retStr == '-10000':
        res = retStr
        token = ''
    elif not retStr:
        res = '-1'
        token = ''
    else:
        pat = re.compile('result=(?P<res>-?\\d+);(token=(?P<token>.*))?', flags=re.DOTALL)
        mat = pat.match(retStr)
        if mat:
            res = mat.group('res')
            token = mat.group('token') if mat.group('token') is not None else ''
        else:
            res = '-1'
            token = ''
    res = CheckResErr(res, 'DYCERT_CheckP12', isCache)
    return (res, token)


def GetPCInfo(isCache=0):
    try:
        res = C_cert.DYCERT_GetPCInfo('')
    except:
        res = '-1'

    tmpRet = CheckResErr(res, 'DYCERT_GetPCInfo', isCache)
    if tmpRet < 0:
        res = '0' * 32
    return res


def CertUninstall(username, isCache=0):
    tmpRet = CertInitialize(isCache)
    if tmpRet < 0 and tmpRet != -8:
        return tmpRet
    username = username.lower()
    try:
        res = C_cert.DYCERT_UninstallP12(username, '')
    except:
        res = '-1'

    res = CheckResErr(res, 'DYCERT_UninstallP12', isCache)
    return res


def CertGetCertName(username, isCache=0):
    username = username.lower()
    try:
        res = C_cert.DYCERT_GetCertName(username, '')
    except:
        res = '-1'

    tmpRet = CheckResErr(res, 'DYCERT_GetCertName', isCache)
    if tmpRet < 0:
        res = ''
    return res


def GetLastFuncLog(isCache=0):
    try:
        res = C_cert.DYCERT_GetPCInfo('GetErrLog')
    except:
        res = '-1'

    if res == '-10000':
        SendErrLog('証書接口致命錯誤(GetLastFuncLog)', '錯誤碼:-10000', isCache)
        res = ''
    elif res and res.startswith('-') and res[1:].isdigit():
        iRes = int(res)
        reason = '錯誤碼:%d' % iRes
        SendErrLog('証書邏輯異常(GetLastFuncLog)', reason, isCache)
        res = ''
    elif not res:
        res = ''
    return res


def CertSign(username, isCache=0):
    username = username.lower()
    the32ValiCode = Create32ValiCode()
    (res, valKey) = CertCheck(username, the32ValiCode, isCache)
    return (res, valKey, the32ValiCode)


def GetCertServer():
    import os, main, permission, gamectrl
    if permission.IsInNet():
        return (INNER_PROTOCOL, INNER_HOST, INNER_PORT)
    elif gamectrl.IsOutTestCert():
        return (OUTTEST_PROTOCOL, OUTTEST_HOST, OUTTEST_PORT)
    else:
        GetCertServerAddr()
        return (OUT_PROTOCOL, OUT_HOST, OUT_PORT)
    return


def GetCertServerAddr():
    return


def SendErrLog(sTitle, sDetail, isCache=0):
    global g_TmpErrText
    import netcert
    sTitle = sTitle[:50]
    sDetail = sDetail[-180:]
    if isCache:
        g_TmpErrText.append((sTitle, sDetail))
    else:
        netcert.C2SErrorLog(sTitle, sDetail)
    return


def SendErrLogCache():
    global g_TmpErrText
    import netcert
    for (title, detail) in g_TmpErrText:
        netcert.C2SErrorLog(title, detail)

    g_TmpErrText = []
    return


def Create32ValiCode():
    import misc
    keyList = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    keyLen = len(keyList)
    res = []
    for i in range(32):
        curIdx = misc.RandInt(0, keyLen - 1)
        res.append(keyList[curIdx])

    resStr = ('').join(res)
    return resStr


def CheckResErr(res, flagStr='', isCache=0):
    if res == '-10000':
        logStr = GetLastFuncLog(isCache)
        SendErrLog('証書接口致命錯誤(%s)' % flagStr, logStr, isCache)
        return -10000
    elif not res:
        reason = '証書邏輯返回了空值(%s)' % flagStr
        reason = AddExLog(reason, isCache)
        SendErrLog('証書邏輯異常(%s)' % flagStr, reason, isCache)
        return -1
    elif res.startswith('-') and res[1:].isdigit():
        iRes = int(res)
        reason = '錯誤碼:%d' % iRes
        reason = AddExLog(reason, isCache)
        if iRes != -107 and iRes != -8:
            SendErrLog('証書邏輯異常(%s)' % flagStr, reason, isCache)
        return iRes
    elif res.isdigit():
        return int(res)
    else:
        return 0
    return


def AddExLog(reason, isCache=0):
    if len(reason) < 160:
        logStr = GetLastFuncLog(isCache)
        left = 160 - len(reason) + 10
        otherTxt = logStr[-left:].replace('\n', '|')
        reason += '|Ex:...' + otherTxt
    return reason


def TestErrorCert():
    import usermacro, cfg
    if not hasattr(C_cert, 'Old_DYCERT_Init'):
        C_cert.Old_DYCERT_Init = C_cert.DYCERT_Init
    C_cert.DYCERT_Init = C_cert.Old_DYCERT_Init
    if not hasattr(C_cert, 'Old_DYCERT_InstallP12'):
        C_cert.Old_DYCERT_InstallP12 = C_cert.DYCERT_InstallP12
    C_cert.DYCERT_InstallP12 = C_cert.Old_DYCERT_InstallP12
    if not hasattr(C_cert, 'Old_DYCERT_CheckP12'):
        C_cert.Old_DYCERT_CheckP12 = C_cert.DYCERT_CheckP12
    C_cert.DYCERT_CheckP12 = C_cert.Old_DYCERT_CheckP12
    if not hasattr(C_cert, 'Old_DYCERT_UninstallP12'):
        C_cert.Old_DYCERT_UninstallP12 = C_cert.DYCERT_UninstallP12
    C_cert.DYCERT_UninstallP12 = C_cert.Old_DYCERT_UninstallP12
    if not hasattr(C_cert, 'Old_DYCERT_GetPCInfo'):
        C_cert.Old_DYCERT_GetPCInfo = C_cert.DYCERT_GetPCInfo
    C_cert.DYCERT_GetPCInfo = C_cert.Old_DYCERT_GetPCInfo
    if not hasattr(C_cert, 'Old_DYCERT_GetCertName'):
        C_cert.Old_DYCERT_GetCertName = C_cert.DYCERT_GetCertName
    C_cert.DYCERT_GetCertName = C_cert.Old_DYCERT_GetCertName
    C_cert.GetErrLogDYCERT_GetPCInfo = C_cert.Old_DYCERT_GetPCInfo
    C_cert.NormalDYCERT_GetPCInfo = C_cert.Old_DYCERT_GetPCInfo

    def DYCERT_GetPCInfo(a):
        if a == 'GetErrLog':
            res = C_cert.GetErrLogDYCERT_GetPCInfo(a)
        else:
            res = C_cert.NormalDYCERT_GetPCInfo(a)
        return res

    C_cert.DYCERT_GetPCInfo = DYCERT_GetPCInfo
    filename = 'testcerterror.ini'
    msgtxt = filename
    error1 = cfg.GetData(filename, 'Cert', 'DYCERT_Init')
    if error1 is not None:
        msgtxt += '#r' + '初始化証書時會換回出錯%s' % error1

        def DYCERT_Init(a1, b1, c1, d1, e1, f1):
            usermacro.PROMPT_MSG('初始化証書時會換回出錯%s' % error1)
            return error1

        C_cert.DYCERT_Init = DYCERT_Init
    error2 = cfg.GetData(filename, 'Cert', 'DYCERT_InstallP12')
    if error2 is not None:
        msgtxt += '#r' + '安裝証書時會換回出錯%s' % error2

        def DYCERT_InstallP12(a1, b1, c1, d1):
            usermacro.PROMPT_MSG('安裝証書時會換回出錯%s' % error2)
            return error2

        C_cert.DYCERT_InstallP12 = DYCERT_InstallP12
    error3 = cfg.GetData(filename, 'Cert', 'DYCERT_CheckP12')
    if error3 is not None:
        msgtxt += '#r' + '生成加密碼時會換回出錯%s' % error3

        def DYCERT_CheckP12(a1, b1):
            usermacro.PROMPT_MSG('生成加密碼時會換回出錯%s' % error3)
            return error3

        C_cert.DYCERT_CheckP12 = DYCERT_CheckP12
    error4 = cfg.GetData(filename, 'Cert', 'DYCERT_UninstallP12')
    if error4 is not None:
        msgtxt += '#r' + '卸載証書時會換回出錯%s' % error4

        def DYCERT_UninstallP12(a1, b1):
            usermacro.PROMPT_MSG('卸載証書時會換回出錯%s' % error4)
            return error4

        C_cert.DYCERT_UninstallP12 = DYCERT_UninstallP12
    error5 = cfg.GetData(filename, 'Cert', 'DYCERT_GetPCInfo')
    if error5 is not None:
        msgtxt += '#r' + '獲取本機的機器信息碼時會換回出錯%s' % error5

        def DYCERT_GetPCInfo2(a1):
            usermacro.PROMPT_MSG('獲取本機的機器信息碼時會換回出錯%s' % error5)
            return error5

        C_cert.NormalDYCERT_GetPCInfo = DYCERT_GetPCInfo2
    error6 = cfg.GetData(filename, 'Cert', 'DYCERT_GetCertName')
    if error6 is not None:
        msgtxt += '#r' + '根據用戶名來獲取可用証書的名字時會換回出錯%s' % error6

        def DYCERT_GetCertName(a1, b1):
            usermacro.PROMPT_MSG('根據用戶名來獲取可用証書的名字時會換回出錯%s' % error6)
            return error6

        C_cert.DYCERT_GetCertName = DYCERT_GetCertName
    error7 = cfg.GetData(filename, 'Cert', 'GetErrLog')
    if error7 is not None:
        msgtxt += '#r' + '獲取日誌時候時返回出錯%s' % error7

        def GetErrLog(a1):
            usermacro.PROMPT_MSG('獲取日誌時候時返回出錯%s' % error7)
            return error7

        C_cert.GetErrLogDYCERT_GetPCInfo = GetErrLog
    usermacro.PROMPT_MSG(msgtxt, lastsecond=30)
    return


return
