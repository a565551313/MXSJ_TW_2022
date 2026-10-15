# pycdc 交叉复核产物 · script.fls entry 4064
# co_filename(原始)='script/history_encrypt.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4064.pyc (Python 2.5)

All_Data = [
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
    179,
    181,
    191,
    193,
    197,
    199,
    211,
    223,
    227,
    229,
    233,
    239,
    241,
    251,
    257,
    263,
    269,
    271,
    277,
    281,
    283,
    293,
    307,
    311,
    313,
    317,
    331,
    337,
    347,
    349,
    353,
    359,
    367,
    373,
    379,
    383,
    389,
    397,
    401,
    409,
    419,
    421,
    431,
    433,
    439,
    443,
    449,
    457,
    461,
    463,
    467,
    479,
    487,
    491,
    499,
    503,
    509,
    521,
    523,
    541,
    547,
    557]
DEBUG = False
g_Record_list = []
g_Historydata = { }
Path = ''
X = N = D = P = Q = 0
E = 65537

def ModuleReset():
    global g_Record_list, g_Historydata, Path, X, N, D, P, Q, E
    g_Record_list = []
    g_Historydata = { }
    Path = ''
    X = N = D = P = Q = 0
    E = 65537


def gcd(m, n):
    while n:
        m = n
        n = m % n
    return m


def SetPath(path):
    global Path
    Path = path + '/'
    
    try:
        import os
        os.mkdir(path)
    except:
        pass



def genkey(key = 10098):
    global P, Q, P, Q, P, Q, N, X, E, D
    BIG_NUM = []
    P_INT = 0
    Q_INT = 0
    key1 = str(key)
    keyword = int(key1[-2:])
    if keyword < 10:
        keyword = int(key1[-1:])
    
    if keyword > 98:
        P = All_Data[98]
        Q = All_Data[99]
    elif keyword < 10:
        P = All_Data[11]
        Q = All_Data[5]
    else:
        P = All_Data[keyword]
        Q = All_Data[keyword >> 1]
    N = P * Q
    X = (P - 1) * (Q - 1)
    while True:
        if gcd(X, E) == 1:
            break
        
        E += 2
    n = 1
    while (n * X + 1) % E != 0:
        n += 1
    D = (n * X + 1) / E


def rsa_encrypt(msg):
    enc = []
    for c in msg:
        enc.append(pow(ord(c), E, N))
    
    return enc


def rsa_decrypt(cmsg):
    dec = []
    tmp = []
    for ec in cmsg:
        tmp.append(pow(ec, D, N))
    
    for c in tmp:
        dec.append('%c' % c)
    
    return dec


def parse_data(data):
    Record_list = []
    num = data[0]
    get_num = data[1:int(num) + 1]
    start = int(num) + 1
    dispath = 0
    for i in range(0, int(get_num)):
        record_num = data[start + dispath:start + dispath + 1]
        change_num = int(record_num)
        Record_list.append(int(data[start + dispath + 1:start + dispath + 1 + change_num]))
        dispath += change_num + 1
    
    dec = rsa_decrypt(Record_list)
    end_data = ''.join(dec)
    return end_data


def write_data(id, msgdata):
    genkey(id)
    if id not in g_Historydata:
        print '\xa5i\xaf\xe0\xa8S\xa6\xb9\xa4\xe5\xa5\xf31'
        g_Historydata[id] = ''
    
    if g_Historydata[id] == msgdata:
        return None
    
    g_Historydata[id] = msgdata
    data = rsa_encrypt(msgdata)
    temp_msg = ''
    filename = Path + str(id) + '.xmx'
    
    try:
        myfile = open(filename, 'w')
        data1 = str(len(data))
        temp_msg += str(len(data1))
        None += None(None, None, None, None, None, None, *temp_msg)
        temp_msg_other = ''
        for i in data:
            temp = str(i)
            temp_msg_other += str(len(temp)) + temp
        
        temp_msg += temp_msg_other
        myfile.write(temp_msg)
        myfile.close()
    except IOError:
        return None



def write_all_data(id, msgdata):
    genkey(id)
    msg = ''
    for i in msgdata:
        msg += i
    
    g_Historydata[id] = msg
    data = rsa_encrypt(msg)
    temp_msg = ''
    filename = Path + str(id) + '.xmx'
    
    try:
        myfile = open(filename, 'w')
        data1 = str(len(data))
        temp_msg += str(len(data1))
        temp_msg += data1
        for i in data:
            temp = str(i)
            temp_msg += str(len(temp))
            temp_msg += temp
        
        myfile.write(temp_msg)
        myfile.close()
    except IOError:
        return None



def read_allperson(data):
    num = data[0]
    start = int(num) + 1
    dispath = 0
    for i in range(0, int(num)):
        record_num = data[start + dispath:start + dispath + 1]
        change_num = int(record_num)
    


def read_data(id):
    genkey(id)
    key1 = str(id)
    keyword = int(key1[-2:])
    if keyword < 10:
        
        try:
            filename = Path + str(id) + '.gmx'
            myfile = open(filename, 'r')
        print '\xb8\xc9\xa4B'
        g_Historydata[id] = ''
        myfile = open(filename, 'w')
        return None

    
    
    try:
        if id in g_Historydata and g_Historydata[id]:
            return g_Historydata[id]
        
        filename = Path + str(id) + '.xmx'
        myfile = open(filename, 'r')
        temp_msg = ''
        mydata = myfile.read()
        data = parse_data(mydata)
        g_Historydata[id] = data
        myfile.close()
        return data
    except:
        print '\xa5i\xaf\xe0\xa8S\xa6\xb9\xa4\xe5\xa5\xf32'
        g_Historydata[id] = ''
        return None
