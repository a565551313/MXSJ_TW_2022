# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcipher\cipher.py
import marshal, zlib, traceback, pubcore
g_Logger = pubcore.GetPubLogger(__name__)

def Encrypt(src):
    s = ''
    for i in xrange(len(src)):
        c = src[i]
        t = ord(c)
        m = i % 9
        a = abs(m - 9) + 1
        t = t + m * a
        t = t % 256
        s += chr(t)

    encryptstr = marshal.dumps(s)
    encryptstr = zlib.compress(encryptstr, 9)
    return encryptstr


def Decrypt(src):
    s = zlib.decompress(src)
    s = marshal.loads(s)
    encryptstr = ''
    for i in xrange(len(s)):
        c = s[i]
        t = ord(c)
        m = i % 9
        a = abs(m - 9) + 1
        t = t - m * a
        if t < 0:
            t += 256
        encryptstr += chr(t)

    return encryptstr


def LoadFile(sPath):
    try:
        f = open(sPath, 'rb')
        src = f.read()
    except Exception as e:
        pubcore.EmitErrorPush()
        traceback.print_stack()

    try:
        head, data = src.split('\r\n', 1)
        head = int(head)
    except Exception as e:
        g_Logger.debug('cipher.LoadFile: 非加密文件，直接返回', sPath)
        return src

    if head >= 0:
        g_Logger.debug('cipher.LoadFile: 已经是明文', sPath)
        return data
    else:
        return Decrypt(data)


def SaveFile(data, sPath, head=1):
    try:
        f = open(sPath, 'wb')
        f.write(str(-head) + '\r\n')
        if head > 0:
            f.write(Encrypt(data))
        else:
            f.write(data)
    except Exception as e:
        pubcore.EmitErrorPush()
        traceback.print_stack()
