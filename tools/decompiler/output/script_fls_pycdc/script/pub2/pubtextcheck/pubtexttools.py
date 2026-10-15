# pycdc 交叉复核产物 · script.fls entry 271
# co_filename(原始)='script/pub2/pubtextcheck/pubtexttools.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_271.pyc (Python 2.5)

import string
import pubdelegate_v2
import pubmisc_v2
import pubtextcheckdefines

def StripSpace(str):
    '''\xa5h\xb1\xbc\xa4\xe5\xa5\xbb\xa4\xa4\xb6}\xc0Y\xa1B\xb5\xb2\xa7\xc0\xa1B\xb3s\xc4\xf2\xaa\xba\xaa\xc5\xae\xe6
\t'''
    str = str.strip()
    lStr = str.split(' ')
    lNewStr = []
    for sWord in lStr:
        lNewStr.append(sWord)
    
    sNewStr = ''.join(lNewStr)
    lStr = sNewStr.split('\xa1@')
    lNewStr = []
    for sWord in lStr:
        lNewStr.append(sWord)
    
    sNewStr = ''.join(lNewStr)
    return sNewStr


def GetCheckText(\xefOri):
    '''\xb9\xef\xa5\xce\xa9\xf3\xc0\xcb\xb4\xfa\xaa\xba\xa6r\xb2\xc5\xa6\xea\xb0\xb5\xa4@\xa8\xc7\xb3B\xb2z\xa1A\xc2\xe0\xa4\xc6\xac\xb0\xc2\xb2\xc5\xe9\xa4p\xbcg

\t\xad\xec\xa6\xeasOri\xa9M\xb8g\xb9L\xa5\xbb\xa8\xe7\xbc\xc6\xb3B\xb2z\xaa\xba\xb7s\xa6\xeasDest\xaa\xbautf8\xa6r\xb2\xc5\xa6\xea\xaa\xf8\xab\xd7\xc0\xb3\xabO\xab\xf9\xa4@\xadP\xa1A
\t\xa7_\xabh\xb7|\xbe\xc9\xadP\xb3\xa1\xa4\xc0\xc0\xcb\xb4\xfa\xa5\\\xaf\xe0\xa5\xa2\xae\xc4\xa1I\xa1I\xa1I
\t'''
    sDest = Convert2Simple(\xefOri)
    sDest = DB2SB(sDest)
    for sWord in pubtextcheckdefines.SPECIAL_WORD:
        if string.find(sDest, sWord):
            sDest = pubmisc_v2.ConventToUtf8String(sDest)
            sDest = sDest.lower()
            sDest = pubmisc_v2.ConventToGBKString(sDest)
            return sDest
            continue
    
    return sDest.lower()


def Convert2Simple(sText):
    '''\xc1c\xc5\xe9\xc2\xe0\xc2\xb2\xc5\xe9
\t'''
    return pubdelegate_v2.Convert2Simple(sText)


def GetNumAmount(sText, bIgnoreFirstNum = False):
    '''\xb2\xce\xadp\xbc\xc6\xa6r\xbc\xc6\xb6q
\t'''
    lMatchs = pubtextcheckdefines.NUMPATT.finditer(sText)
    iPreEnd = -1
    iMaxNum = 0
    iAmount = 0
    for mo in lMatchs:
        if (bIgnoreFirstNum or iPreEnd == -1 or mo.start() > iPreEnd + pubtextcheckdefines.NUMCHECK_DIS) and iPreEnd != -1:
            iPreEnd = mo.end()
            if iAmount > iMaxNum:
                iMaxNum = iAmount
                iAmount = 0
                continue
            continue
        
        iPreEnd = mo.end()
        iAmount += 1
    
    if iAmount > iMaxNum:
        iMaxNum = iAmount
    
    return iMaxNum


def GetIMCharAmount(sText):
    """\xb2\xce\xadpim\xb3n\xa5\xf3\xa6W\xc3\xf6\xc1\xe4\xa6r\xb2\xc5\xbc\xc6\xb6q

\t\xa8\xd2\xa1G\xa1u\xa7\xda\xaa\xbaqq123456\xa5[\xa4@\xa4U\xa1\xa8 -> \xaa\xf0\xa6^\xad\xc8\xac\xb02\xa1A\xa9R\xa4\xa4\xa4F\xa8\xe2\xa6\xb8'q'
\t"""
    lMatchs = pubtextcheckdefines.IMCHAR.findall(sText)
    return len(lMatchs)


def CheckAccount(sText, iNumCount, bIgnoreFirstNum = False):
    iIMCnt = GetIMCharAmount(sText)
    iNumCnt = GetNumAmount(sText, bIgnoreFirstNum)
    if iIMCnt >= 1 and iNumCnt >= iNumCount:
        return False
    
    return True


def CheckEmote(iStart, sText):
    '''\xaa\xed\xb1\xa1\xc0\xcb\xb4\xfa
\t'''
    iCount = 0
    i = iStart - 1
    while i >= 0:
        idx = i
        i -= 1
        if sText[idx] == '#':
            iCount += 1
            continue
        
        break
    return iCount % 2 != 0


def CheckBanChar(sText):
    '''\xafS\xae\xed\xa6r\xb2\xc5\xc0\xcb\xb4\xfa

\t\xb1N\xafS\xae\xed\xa6r\xb2\xc5\xb4\xc0\xb4\xab\xac\xb0\xaa\xc5\xae\xe6
\t'''
    for char in pubtextcheckdefines.BAN_CHARS:
        if char in sText:
            sText = sText.replace(char, ' ')
            continue
    
    return sText


def IsGbkChar(char):
    return False


def DB2SB(sRawStr):
    '''
\t\xa5\xfe\xa8\xa4\xc2\xe0\xa5b\xa8\xa4
\t:param sRawStr:
\t:return:
\t'''
    
    try:
        sSBStr = ''
        flag = 0
        index = 0
        iRawStrLength = len(sRawStr)
        while index < iRawStrLength:
            char = sRawStr[index]
            n = ord(char)
            if flag == 0:
                if n == 163:
                    flag = 1
                elif n >= 160:
                    sSBStr += char
                    flag = 2
                else:
                    sSBStr += char
                    if n >= 128:
                        index += 1
                        if index >= iRawStrLength:
                            break
                        
                        sSBStr += sRawStr[index]
                    
            elif flag == 1:
                if n == 168:
                    sSBStr += '\xa1]'
                elif n == 169:
                    sSBStr += '\xa1^'
                elif n == 172:
                    sSBStr += '\xa1A'
                elif n > 128:
                    sSBStr += chr(n - 128)
                else:
                    sSBStr += sRawStr[index - 1] + char
                flag = 0
            elif flag == 2:
                sSBStr += char
                flag = 0
            
            index += 1
    except:
        sSBStr = sRawStr

    return sSBStr


def IsNameCharLegal(sName):
    '''\xa7P\xc2_\xa6r\xb2\xc5\xacO\xa7_\xa6b\xab\xfc\xa9w\xaa\xba\xa6r\xb2\xc5\xb0\xcf\xb6\xa1\xa6C\xaa\xed\xa4\xa4
\t'''
    import pubignorechardata
    SPECIAL = [
        ' ',
        '\xa1@']
    length = len(sName)
    i = 0
    while i < length:
        ch = sName[i]
        ascii = ord(ch)
        if ascii > 128:
            i += 1
            ch = ch + sName[i]
            ascii2 = ord(sName[i])
            if ascii2 < 160:
                if ch not in pubignorechardata.GetData():
                    return False
                
            
        if ch in SPECIAL:
            return False
        
        i += 1
    return True
