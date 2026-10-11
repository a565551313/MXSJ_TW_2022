# uncompyle6 version 3.9.3
# Python bytecode version base 2.5 (62131)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: script\pubscript\dyautologin.py
import gamevar

def DecryptString(inputstr):
    import device, time
    interval = 30
    t1 = int(time.time() / interval)
    print 'time.time()', t1
    mac = device.GetMAC()
    str1 = _DecryptString(inputstr, mac, t1)
    if str1.find(gamevar.DYAUTOLOGIN_KEY) == 0:
        return str1[len(gamevar.DYAUTOLOGIN_KEY):]
    str1 = _DecryptString(inputstr, mac, t1 - 1)
    if str1.find(gamevar.DYAUTOLOGIN_KEY) == 0:
        return str1[len(gamevar.DYAUTOLOGIN_KEY):]
    print 'error!!decry37cfaild'
    return ''


def _DecryptString(to_dec, mac_key, time_key):
    dec_len = len(to_dec)
    mac_len = len(mac_key)
    arr = []
    j = 0
    i = 0
    while i < dec_len - 1:
        low = int(to_dec[i], 16)
        i = i + 1
        high = int(to_dec[i], 16)
        i = i + 1
        ch = low * 16 + high
        mc = mac_key[j % mac_len]
        cr = ch ^ ord(mc)
        cr = cr ^ time_key & 255
        cr = cr ^ time_key >> 8 & 255
        j = j + 1
        arr.append(chr(cr))

    return ('').join(arr)


return
