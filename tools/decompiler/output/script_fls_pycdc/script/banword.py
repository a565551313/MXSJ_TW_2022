# pycdc 交叉复核产物 · script.fls entry 528
# co_filename(原始)='script/banword.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_528.pyc (Python 2.5)

import re
import cfg
import hero
import interface
import misc
import netcommon
import permission
import pubbanword
import high_risk_word_data
g_CheckMgr = None
g_bIsInitPubTextCheck = False
LINK_PATT = re.compile('#s\\((?P<linkid>\\d+)(,(?P<context>[\\s\\S]+?))?\\)')
EMOTE_PATT = re.compile('#(?P<num>[0-9]+)')
MxWhiteList = [
    '\xa4\xb8&=',
    '\xaa\xf7&=',
    '\xb9\xf4&=',
    '\xb8U&=',
    'w&=',
    'W&=',
    '=&\xb8U',
    '=&W',
    '=&w',
    '=&\xa4\xb8',
    '=&\xaa\xf7',
    '=&\xb9\xf4',
    '=&j&b',
    'j&b&=',
    '\xb4\xab&\xaa\xf7',
    '\xaa\xf7&\xb4\xab',
    '\xa6\xac&j',
    '\xa6\xac&\xaa\xf7',
    '\xa6\xac&\xb9\xf4',
    '\xa6\xac&b',
    'j&\xa6\xac',
    '\xaa\xf7&\xa6\xac',
    '\xb9\xf4&\xa6\xac',
    'b&\xa6\xac',
    '\xaa\xf7&\xa4\xb8',
    '\xa4\xb8&\xaa\xf7',
    '\xb9\xf4&\xa4\xb8',
    '\xa4\xb8&\xb9\xf4',
    'j&\xa4\xb8',
    '\xa4\xb8&j',
    'b&\xa4\xb8',
    '\xa4\xb8&b',
    '\xaa\xf7&\xc0\xb4',
    '\xaa\xf7&\xadn',
    '\xb9\xf4&\xc0\xb4',
    '\xb9\xf4&\xadn',
    'j&\xc0\xb4',
    'j&\xadn',
    'b&\xc0\xb4',
    'b&\xadn',
    '\xa4j&\xb8\xdc',
    '\xa6\xac&\xafq',
    '5&1&7&3']
PROTECT_WORD_LST = [
    '\xa4\xf2\xaf\xf3\xb9\xce',
    '\xb9@\xa8\xb8\xaf\xf3',
    '\xaf\xf3\xb8\xc8\xbbR',
    '\xaf\xf3\xb8s\xbbR',
    '\xac\xa1\xa6\xe5\xaf\xf3',
    '\xa6^\xc5]\xaf\xf3',
    '\xbf\xc3\xa5\xfa\xaf\xf3',
    '\xc2\xfb\xa6\xe5\xa5\xdb',
    '\xa5s\xaa\xe1\xc2\xfb',
    '\xc2\xfb\xaba\xaa\xe1',
    '\xaf\xf3\xb9\xce',
    '\xaf\xf3\xb8s',
    '\xc0s\xaa\xea',
    '\xaf\xf3\xb8\xc8']
WHOLEWORD_WHITE_LIST = [
    '\xb8\xb9',
    '\xb7\xd2',
    '\xb9\xf4',
    '\xbb\xf9']
MxWhiteDict = {
    -1: [],
    0: MxWhiteList,
    1: MxWhiteList,
    3: MxWhiteList,
    5: MxWhiteList,
    6: MxWhiteList,
    9: MxWhiteList,
    11: MxWhiteList,
    15: MxWhiteList,
    17: MxWhiteList }

def CheckEmote(obj, num):
    import baozidata
    if num in baozidata.DATA:
        return True
    elif baozidata.IsSpecialEmote(num):
        return True
    else:
        return False


def GetBanwordString(obj, banword, type):
    return CCheck.m_Condition.GetBufString(banword, type)

pubbanword.CStringData.GetBanwordString = GetBanwordString
pubbanword.CStringData.CheckEmote = CheckEmote
pubbanword.PROTECT_WORD_LST = PROTECT_WORD_LST
NS_LIST = [
    'q&q',
    'q&\xb8s',
    '\xa6\xa9&\xa6\xa9',
    '\xa6\xa9&\xb8s',
    'y&y',
    '\xacn&\xacn',
    '\xa4X&\xa4X',
    'y&\xacn',
    '\xacn&y',
    'y&\xa4X',
    '\xa4X&y',
    '\xb8}&\xa5\xbb']
NS_LIMIT_LEV = 40
BANTYPES = [
    0,
    1,
    2,
    3,
    4,
    101,
    102,
    103,
    104,
    105,
    106,
    107]
MxNeedDct = {
    '\xa4j': [
        '\xa4j\xb8\xdc'] }

def SetWhiteList(ch, activeEdit = None):
    import mainmenu
    import channel
    oChatInput = mainmenu.GetChatInputObj()
    if ch == -1 and activeEdit and oChatInput and oChatInput == activeEdit:
        ch = channel.GetCurChannel()
    
    pubbanword.g_CurWhiteList = MxWhiteDict.get(ch, [])

SetWhiteList(-1)

def InitNewBanWord():
    global g_bIsInitPubTextCheck
    if not g_bIsInitPubTextCheck:
        if permission.IsNewBanWord():
            import pubtextcheck
            pubtextcheck.InitData({ })
        
        g_bIsInitPubTextCheck = True
    


def GetWhiteListByChannel(ch = -1):
    return MxWhiteDict[ch]


def GetProtectEmote(sText):
    iProtectList = []
    oMatchObjList = EMOTE_PATT.finditer(sText)
    for oMatch in oMatchObjList:
        iNum = int(oMatch.group('num'))
        if CheckEmote(None, iNum):
            iProtectList.append((oMatch.start(), oMatch.end() - 1))
            continue
    
    return iProtectList


def GetProtectLink(sText):
    iProtectList = []
    oMatchObjList = LINK_PATT.finditer(sText)
    for oMatch in oMatchObjList:
        iProtectList.append((oMatch.start(), oMatch.end() - 1))
    
    return iProtectList


def GetProtectWord(sText):
    iProtectList = []
    sText = sText.lower()
    for sWord in PROTECT_WORD_LST:
        oPatt = re.compile(sWord)
        for oMatch in oPatt.finditer(sText):
            iKey = (oMatch.start(), oMatch.end() - 1)
            if iKey not in iProtectList:
                iProtectList.append(iKey)
                continue
        
    
    return iProtectList


def UpdateBanWord():
    CLibrary.UpdateBanWord()


def S2CProcess(netobj):
    CLibrary.Process(netobj)


def S2CIsShenheVer(netobj):
    CLibrary.S2CIsShenheVer(netobj)
    CCheck.m_Condition.m_BuffStrings.clear()


def IsValidChat(sText, ch = -1):
    sText = misc.Trad2Simp(sText)
    if permission.IsNewBanWord():
        import pubtextcheck
        lWordWhiteList = GetWhiteListByChannel(ch)
        lProtectList = GetProtectEmote(sText) + GetProtectLink(sText) + GetProtectWord(sText)
        return pubtextcheck.CheckWord(sText, lWordWhiteList, lProtectList)
    else:
        activeEdit = interface.GetActiveEdit()
        SetWhiteList(ch, activeEdit)
        return CCheck.IsValidChat(sText)


def BadWholeWord(sText, ch = -1):
    sText = misc.Trad2Simp(sText)
    if permission.IsNewBanWord():
        import pubtextcheck
        lWordWhiteList = []
        lWordWhiteList += WHOLEWORD_WHITE_LIST
        lChannelWordWhiteList = GetWhiteListByChannel(ch)
        if lChannelWordWhiteList:
            lWordWhiteList += lChannelWordWhiteList
        
        lProtectList = GetProtectEmote(sText) + GetProtectLink(sText) + GetProtectWord(sText)
        LOG_DEBUG('lWordWhiteList = ', lWordWhiteList)
        return not pubtextcheck.CheckWholeWord(sText, False, lWordWhiteList = lWordWhiteList, lProtectList = lProtectList, bCheckNum = False)
    else:
        activeEdit = interface.GetActiveEdit()
        SetWhiteList(ch, activeEdit)
        return not CCheck.IsValidWholeWord(sText)


def BadWord_Channel(ch, sText):
    '''
\t\xc0\xcb\xb4\xfa\xa4\xbd\xab\xcc\xacO\xa7_\xabD\xaak
\t:return: True:\xabD\xaak False:\xa6X\xaak
\t'''
    sText = misc.Trad2Simp(sText)
    if permission.IsNewBanWord():
        import pubtextcheck
        import channel
        if ch in channel.CH_PUBLIC:
            lWordWhiteList = []
            lWordWhiteList += WHOLEWORD_WHITE_LIST
            lChannelWordWhiteList = GetWhiteListByChannel(ch)
            if lChannelWordWhiteList:
                lWordWhiteList += lChannelWordWhiteList
            
            lProtectList = GetProtectEmote(sText) + GetProtectLink(sText) + GetProtectWord(sText)
            if not pubtextcheck.CheckWholeWord(sText, False, lWordWhiteList = lWordWhiteList, lProtectList = lProtectList, bCheckNum = False):
                return True
            
        
        return False
    else:
        SetWhiteList(ch)
        return not CCheck.IsValidOnPubChannel(ch, sText)


def IsValidOnIntrodruce(sText, ch = -1):
    sText = misc.Trad2Simp(sText)
    if permission.IsNewBanWord():
        import pubtextcheck
        lWordWhiteList = GetWhiteListByChannel(ch)
        lProtectList = GetProtectEmote(sText) + GetProtectLink(sText) + GetProtectWord(sText)
        return pubtextcheck.CheckMail(sText, lWordWhiteList, lProtectList)
    elif IsValidChat(sText, ch)[0]:
        pass
    return CCheck.IsValidOnIntrodruce(sText)


def IsValidName(txt, onsale = False, bCheckEx = True):
    txt = misc.Trad2Simp(txt)
    if permission.IsNewBanWord():
        import pubtextcheck
        return pubtextcheck.CheckName(txt, lWordWhiteList = [
            '\xb3p\xbb\xbb'], bCheckAccount = not onsale)
    else:
        return CCheck.IsValidNameEx(txt, onsale, bCheckEx)


def IsRealValidName(txt, onsale = False, bCheckEx = True):
    '''
\t\xb0\xaa\xa6M\xb5\xfc\xb7J\xc0\xcb\xb4\xfa
\t'''
    (bRet, sDangerWords) = CCheck.IsValidHighRiskShieldedWord(txt)
    if bRet:
        (bRet, sDangerWords) = CCheck.IsValidWholeCheckHighRiskShieldedWord(txt)
        if bRet:
            return (True, None)
        
        return (bRet, sDangerWords)
    else:
        return (bRet, sDangerWords)


def IsValidPublicOpinion(sText):
    '''
\t\xa4\xbd\xa6@\xc0\xcb\xb4\xfa\xb1\xc0\xb0e 2021\xa6~\xa4C\xa4@\xc1\xd6\xb1\xa1\xb7s\xbcW\xa6r\xaew
\t'''
    return CCheck.IsValidPublicOpinionWord(sText)


def ChackAndSendMsg(sTranType, sAddName, sMsg):
    (bRet, sDangerWords) = IsRealValidName(sMsg)
    if not bRet:
        for iPos in range(len(sDangerWords) - 1, -1, -1):
            sDanger = sDangerWords[iPos]
            if sDanger in CCheck.m_Condition.m_Library.m_BandHighRiskShieldedWordList + high_risk_word_data.GetWoldList():
                continue
            
            if sDanger in CCheck.m_Condition.m_Library.m_BandWholeHighRiskShieldedWordList + high_risk_word_data.GetAllList():
                continue
            
            LOG_ERR('\xc0\xcb\xa5X\xbf\xf9\xbb~\xb5\xfc\xb7J', sDanger, sMsg)
            sDangerWords.pop(iPos)
        
        if not sDangerWords:
            
            try:
                None(LOG_ERR, sMsg)
                return None
            iCheckFlag = 0
            if sTranType == '\xaa\xb1\xaea\xa9m\xa6W' and sMsg.startswith('\xaa\xb1\xaea') and sMsg[4:].isdigit():
                iCheckFlag = 1
            

        netcommon.C2SUnRealValidName(sTranType, sAddName + sMsg, sDangerWords[0], iCheckFlag)
    


def IsValidName2(txt, onsale = False, bCheckEx = True):
    txt = misc.Trad2Simp(txt)
    return CCheck.IsValidName2(txt, onsale, bCheckEx)


def IsValidOnFriendSendMsg(sender, txt):
    txt = misc.Trad2Simp(txt)
    txt = GetProtectTxt(txt)
    return CCheck.IsValidOnFriendMsg(sender, txt)


def GetProtectTxt(txt):
    import re
    import copy
    patt = re.compile('#s\\([^)]*\\)')
    rawstr = copy.deepcopy(txt)
    match_objs = patt.finditer(rawstr)
    for mo in match_objs:
        txt = txt.replace(rawstr[mo.start():mo.end()], ' ')
    
    return txt


def GetMaskText(txt, isenter = False, bCheckDigit = True):
    txt = misc.Trad2Simp(txt)
    if isenter:
        replaceChar = ('\r', '\n', '\t')
    else:
        replaceChar = '\t'
    for c in replaceChar:
        txt = txt.replace(c, '')
    
    (_, txt) = IsValidChat(txt)
    return txt


def AddCheckWordTask(sTxt, sType):
    global g_CheckMgr
    if type(sTxt) == list:
        newTxtList = []
        for sName in sTxt:
            if type(sName) == tuple:
                (sTupleName, iPid) = sName
                newTxtList.append((misc.Trad2Simp(sTupleName), iPid))
                continue
            newTxtList.append(misc.Trad2Simp(sName))
        
        sTxt = newTxtList
    else:
        sTxt = misc.Trad2Simp(sTxt)
    if not g_CheckMgr:
        g_CheckMgr = CBanCheckMgr()
    
    g_CheckMgr.AddCheckTask(sTxt, sType)


def DelayCheckText():
    if g_CheckMgr:
        g_CheckMgr.StartCheck()
    


class CLibrary(pubbanword.CPubLibrary):
    LB_WCHATEXT = 'chtxxl'
    LB_NAMEEXTEXT = 'namexxl'
    LB_HIGHRISKSHIELDEDWORD = 'hrsword'
    LB_WHOLEHIGHRISKSHIELDEDWORD = 'hhrsword'
    m_TypeExtDict = {
        101: 'S2CBandWordExt',
        102: 'S2CBanNameExt',
        103: 'S2CHighRiskShieldedWord',
        104: 'S2CWholeHighRiskShieldedWord' }
    pubbanword.CPubLibrary.m_TypeDict.update(m_TypeExtDict)
    m_BanWholeChatExList = None
    m_BanWholeChatExVer = 0
    m_BanWholeChatExDict = None
    m_BandHighRiskShieldedWordList = None
    m_BandHighRiskShieldedWordVar = 0
    m_BanHighRiskShieldedWordDict = None
    m_BandWholeHighRiskShieldedWordList = None
    m_BandWholeHighRiskShieldedWordVar = 0
    m_BandWholeHighRiskShieldedWordDict = None
    m_BanNameExList = None
    m_BanNameExVer = 0
    m_BanNameExDict = None
    m_ExtRecvPacketBW = []
    m_ExtRecvPacketName = []
    m_ExtRecvRiskShieldedWord = []
    m_ExtRecvWholeRiskShieldedWord = []
    m_Timer = None
    
    def ResetClear(cls):
        cls.m_TypeExtDict = {
            101: 'S2CBandWordExt',
            102: 'S2CBanNameExt',
            103: 'S2CHighRiskShieldedWord',
            104: 'S2CWholeHighRiskShieldedWord' }
        pubbanword.CPubLibrary.m_TypeDict.update(cls.m_TypeExtDict)
        cls.m_BanWholeChatExList = None
        cls.m_BanWholeChatExVer = 0
        cls.m_BanWholeChatExDict = None
        cls.m_BandHighRiskShieldedWordList = None
        cls.m_BandHighRiskShieldedWordVar = 0
        cls.m_BanHighRiskShieldedWordDict = None
        cls.m_BandWholeHighRiskShieldedWordList = None
        cls.m_BandWholeHighRiskShieldedWordVar = 0
        cls.m_BandWholeHighRiskShieldedWordDict = None
        cls.m_BanNameExList = None
        cls.m_BanNameExVer = 0
        cls.m_BanNameExDict = None
        cls.m_ExtRecvPacketBW = []
        cls.m_ExtRecvPacketName = []
        cls.m_ExtRecvRiskShieldedWord = []
        cls.m_ExtRecvWholeRiskShieldedWord = []
        cls.m_Timer = None

    ResetClear = classmethod(ResetClear)
    
    def GetHeader(cls):
        import netpublic
        netobj = netpublic.PacketPrepare(netpublic.C2GS_SUB_PBZLIST)
        if netobj:
            return netobj
        

    GetHeader = classmethod(GetHeader)
    
    def S2CAskRequest(cls, netobj):
        cls.UpdateBanWord()

    S2CAskRequest = classmethod(S2CAskRequest)
    
    def UpdateBanWord(cls):
        
        def Update(obj, idx):
            if idx > len(BANTYPES) - 1:
                return None
            
            itype = BANTYPES[idx]
            LOG('\xa7\xf3\xb7s\xa6r\xaew', itype)
            if itype == 101:
                cls.ExtBanWordUpdate()
            elif itype == 102:
                cls.ExtBanNameUpdate()
            elif itype == 103:
                cls.ExtHighRiskShieldedWord()
            elif itype == 104:
                cls.ExtWholeHighRiskShieldedWord()
            else:
                cls.BanWordUpdate([
                    itype])
            return (idx + 1,)

        if cls.m_Timer:
            cls.m_Timer.Release()
            cls.m_Timer = None
        
        cls.m_Timer = interface.CBaseObject(None)
        cls.m_Timer.CreatePyCommand(1, Update, 0)

    UpdateBanWord = classmethod(UpdateBanWord)
    
    def S2CBandWordExt(cls, netobj):
        iRecvTimes = netobj.UnpackInt(1)
        iVer = netobj.UnpackInt(4)
        s = netobj.UnpackString(0)
        cls.m_ExtRecvPacketBW.append(s)
        if iRecvTimes > 0:
            if len(cls.m_ExtRecvPacketBW) != iRecvTimes:
                cls.m_ExtRecvPacketBW = []
                cls.ExtBanWordUpdate()
                return None
            
            sData = ''.join(cls.m_ExtRecvPacketBW)
            blst = sData.split('\n')
            cls.SetBanWholeChatExData(iVer, blst)
            cls.SaveBL(cls.LB_WCHATEXT, sData, iVer)
            cls.m_ExtRecvPacketBW = []
        

    S2CBandWordExt = classmethod(S2CBandWordExt)
    
    def S2CBanNameExt(cls, netobj):
        iRecvTimes = netobj.UnpackInt(1)
        iVer = netobj.UnpackInt(4)
        s = netobj.UnpackString(0)
        cls.m_ExtRecvPacketName.append(s)
        if iRecvTimes > 0:
            if len(cls.m_ExtRecvPacketName) != iRecvTimes:
                cls.m_ExtRecvPacketName = []
                cls.ExtBanNameUpdate()
                return None
            
            sData = ''.join(cls.m_ExtRecvPacketName)
            blst = sData.split('\n')
            cls.SetBanNameExData(iVer, blst)
            cls.SaveBL(cls.LB_NAMEEXTEXT, sData, iVer)
            cls.m_ExtRecvPacketName = []
        

    S2CBanNameExt = classmethod(S2CBanNameExt)
    
    def GetBanWholeChatExData(cls):
        if cls.m_BanWholeChatExList is None:
            cls.ReadBanWholeChatExData()
        
        if cls.m_BanWholeChatExDict is None:
            cls.m_BanWholeChatExDict = cls.GetBanWordDict(cls.m_BanWholeChatExList)
        
        return cls.m_BanWholeChatExDict

    GetBanWholeChatExData = classmethod(GetBanWholeChatExData)
    
    def SetBanWholeChatExData(cls, iVer, blst):
        cls.m_BanWholeChatExList = blst
        cls.m_BanWholeChatExVer = iVer
        cls.m_BanWholeChatExDict = cls.GetBanWordDict(blst)

    SetBanWholeChatExData = classmethod(SetBanWholeChatExData)
    
    def ReadBanWholeChatExData(cls):
        (ver, blst) = cls.ReadBL(cls.LB_WCHATEXT)
        cls.SetBanWholeChatExData(ver, blst)

    ReadBanWholeChatExData = classmethod(ReadBanWholeChatExData)
    
    def ExtBanWordUpdate(cls):
        cls.ReadBanWholeChatExData()
        cls.C2SBanVer(101, cls.m_BanWholeChatExVer)

    ExtBanWordUpdate = classmethod(ExtBanWordUpdate)
    
    def SetBanNameExData(cls, iVer, blst):
        cls.m_BanNameExList = blst
        cls.m_BanNameExVer = iVer
        cls.m_BanNameExDict = cls.GetBanWordDict(blst)

    SetBanNameExData = classmethod(SetBanNameExData)
    
    def ReadBanNameExData(cls):
        (ver, blst) = cls.ReadBL(cls.LB_NAMEEXTEXT)
        cls.SetBanNameExData(ver, blst)

    ReadBanNameExData = classmethod(ReadBanNameExData)
    
    def ExtBanNameUpdate(cls):
        cls.ReadBanNameExData()
        cls.C2SBanVer(102, cls.m_BanNameExVer)

    ExtBanNameUpdate = classmethod(ExtBanNameUpdate)
    
    def GetBanNameExData(cls):
        if cls.m_BanNameExList is None:
            cls.ReadBanNameExData()
        
        if cls.m_BanNameExDict is None:
            cls.m_BanNameExDict = cls.GetBanWordDict(cls.m_BanNameExList)
        
        return cls.m_BanNameExDict

    GetBanNameExData = classmethod(GetBanNameExData)
    
    def SetHighRiskShieldedWord(cls, iVer, blst):
        cls.m_BandHighRiskShieldedWordList = blst
        cls.m_BandHighRiskShieldedWordVar = iVer
        cls.m_BanHighRiskShieldedWordDict = cls.GetBanWordDict(blst + high_risk_word_data.GetWoldList())

    SetHighRiskShieldedWord = classmethod(SetHighRiskShieldedWord)
    
    def ReadHighRiskShieldedWord(cls):
        (ver, blst) = cls.ReadBL(cls.LB_HIGHRISKSHIELDEDWORD)
        print 'S2CHighRiskBanWord ver = %d, sum = %d' % (ver, len(blst))
        cls.SetHighRiskShieldedWord(ver, blst)

    ReadHighRiskShieldedWord = classmethod(ReadHighRiskShieldedWord)
    
    def ExtHighRiskShieldedWord(cls):
        cls.ReadHighRiskShieldedWord()
        cls.C2SBanVer(103, cls.m_BandHighRiskShieldedWordVar)

    ExtHighRiskShieldedWord = classmethod(ExtHighRiskShieldedWord)
    
    def S2CHighRiskShieldedWord(cls, netobj):
        iRecvTimes = netobj.UnpackInt(1)
        iVer = netobj.UnpackInt(4)
        s = netobj.UnpackString(0)
        cls.m_ExtRecvRiskShieldedWord.append(s)
        if iRecvTimes > 0:
            if len(cls.m_ExtRecvRiskShieldedWord) != iRecvTimes:
                cls.m_ExtRecvRiskShieldedWord = []
                cls.ExtHighRiskShieldedWord()
                return None
            
            sData = ''.join(cls.m_ExtRecvRiskShieldedWord)
            blst = sData.split('\n')
            cls.SetHighRiskShieldedWord(iVer, blst)
            cls.SaveBL(cls.LB_HIGHRISKSHIELDEDWORD, sData, iVer)
            cls.m_ExtRecvRiskShieldedWord = []
        

    S2CHighRiskShieldedWord = classmethod(S2CHighRiskShieldedWord)
    
    def SetWholeHighRiskShieldedWord(cls, iVer, blst):
        cls.m_BandWholeHighRiskShieldedWordList = blst
        cls.m_BandWholeHighRiskShieldedWordVar = iVer
        cls.m_BanWholeHighRiskShieldedWordDict = cls.GetBanWordDict(blst + high_risk_word_data.GetAllList())

    SetWholeHighRiskShieldedWord = classmethod(SetWholeHighRiskShieldedWord)
    
    def ReadWholeHighRiskShieldedWord(cls):
        (ver, blst) = cls.ReadBL(cls.LB_WHOLEHIGHRISKSHIELDEDWORD)
        print 'S2CWholeHighRiskBanWord ver = %d, sum = %d' % (ver, len(blst))
        cls.SetWholeHighRiskShieldedWord(ver, blst)

    ReadWholeHighRiskShieldedWord = classmethod(ReadWholeHighRiskShieldedWord)
    
    def ExtWholeHighRiskShieldedWord(cls):
        cls.ReadWholeHighRiskShieldedWord()
        cls.C2SBanVer(104, cls.m_BandWholeHighRiskShieldedWordVar)

    ExtWholeHighRiskShieldedWord = classmethod(ExtWholeHighRiskShieldedWord)
    
    def S2CWholeHighRiskShieldedWord(cls, netobj):
        iRecvTimes = netobj.UnpackInt(1)
        iVer = netobj.UnpackInt(4)
        s = netobj.UnpackString(0)
        cls.m_ExtRecvWholeRiskShieldedWord.append(s)
        if iRecvTimes > 0:
            if len(cls.m_ExtRecvWholeRiskShieldedWord) != iRecvTimes:
                cls.m_ExtRecvWholeRiskShieldedWord = []
                cls.ExtWholeHighRiskShieldedWord()
                return None
            
            sData = ''.join(cls.m_ExtRecvWholeRiskShieldedWord)
            blst = sData.split('\n')
            cls.SetWholeHighRiskShieldedWord(iVer, blst)
            cls.SaveBL(cls.LB_WHOLEHIGHRISKSHIELDEDWORD, sData, iVer)
            cls.m_ExtRecvWholeRiskShieldedWord = []
        

    S2CWholeHighRiskShieldedWord = classmethod(S2CWholeHighRiskShieldedWord)
    
    def GetHighRiskShieldedWord(cls):
        if cls.m_BandHighRiskShieldedWordList is None:
            (cls.m_BandHighRiskShieldedWordVar, cls.m_BandHighRiskShieldedWordList) = cls.ReadBL(cls.LB_HIGHRISKSHIELDEDWORD)
        
        if cls.m_BanHighRiskShieldedWordDict is None:
            tmplst = high_risk_word_data.GetWoldList() + cls.m_BandHighRiskShieldedWordList
            cls.m_BanHighRiskShieldedWordDict = cls.GetBanWordDict(tmplst)
        
        return cls.m_BanHighRiskShieldedWordDict

    GetHighRiskShieldedWord = classmethod(GetHighRiskShieldedWord)
    
    def GetWholeHighRiskShieldedWord(cls):
        if cls.m_BandWholeHighRiskShieldedWordList is None:
            (cls.m_BandWholeHighRiskShieldedWordVar, cls.m_BandWholeHighRiskShieldedWordList) = cls.ReadBL(cls.LB_WHOLEHIGHRISKSHIELDEDWORD)
        
        if cls.m_BandWholeHighRiskShieldedWordDict is None:
            tmplst = high_risk_word_data.GetAllList() + cls.m_BandWholeHighRiskShieldedWordList
            cls.m_BandWholeHighRiskShieldedWordDict = cls.GetBanWordDict(tmplst)
        
        return cls.m_BandWholeHighRiskShieldedWordDict

    GetWholeHighRiskShieldedWord = classmethod(GetWholeHighRiskShieldedWord)
    
    def GetHighRiskShieldedWordList(cls):
        if cls.m_BandHighRiskShieldedWordList is None:
            (cls.m_BandHighRiskShieldedWordVar, cls.m_BandHighRiskShieldedWordList) = cls.ReadBL(cls.LB_HIGHRISKSHIELDEDWORD)
        
        return (cls.m_BandHighRiskShieldedWordVar, cls.m_BandHighRiskShieldedWordList)

    GetHighRiskShieldedWordList = classmethod(GetHighRiskShieldedWordList)
    
    def GetWholeHighRiskShieldedWordList(cls):
        if cls.m_BandWholeHighRiskShieldedWordList is None:
            (cls.m_BandWholeHighRiskShieldedWordVar, cls.m_BandWholeHighRiskShieldedWordList) = cls.ReadBL(cls.LB_WHOLEHIGHRISKSHIELDEDWORD)
        
        return (cls.m_BandWholeHighRiskShieldedWordVar, cls.m_BandWholeHighRiskShieldedWordList)

    GetWholeHighRiskShieldedWordList = classmethod(GetWholeHighRiskShieldedWordList)
    
    def GetPublicOpinionWord(cls):
        return high_risk_word_data.PUBLIC_OPINION_DATA

    GetPublicOpinionWord = classmethod(GetPublicOpinionWord)
    
    def SetHighRiskShieldedWordLocalTest(cls, lHighRiskWord, lHighRiskWholeWord):
        tmplst1 = high_risk_word_data.GetWoldList() + lHighRiskWord
        cls.m_BanHighRiskShieldedWordDict = cls.GetBanWordDict(tmplst1)
        tmplst2 = high_risk_word_data.GetAllList() + lHighRiskWholeWord
        cls.m_BandWholeHighRiskShieldedWordDict = cls.GetBanWordDict(tmplst2)

    SetHighRiskShieldedWordLocalTest = classmethod(SetHighRiskShieldedWordLocalTest)


class CCondition(pubbanword.CPubCondition):
    m_Library = CLibrary
    
    def ShowBanWordInfo(cls, txt):
        import clientinterface
        clientinterface.ShowChatDebugInfo(txt)

    ShowBanWordInfo = classmethod(ShowBanWordInfo)
    
    def IsPublicChannel(cls, ch):
        import channel
        return ch in channel.CH_PUBLIC

    IsPublicChannel = classmethod(IsPublicChannel)
    
    def WholeCheckBW(cls, txt):
        import re
        import pubmisc
        txt = re.sub('\xbcC\xc6F', '', txt)
        txt = re.sub('\xae\xe7\xaa\xe1\xb7\xbd\xb0O', '', txt)
        txt = re.sub('=', '', txt)
        strobj = cls.GetBufString(txt, 2)
        checklst = strobj.GetCheckStringList()
        checktxt = ''.join(checklst)
        lb = cls.m_Library
        bandict = lb.GetBanWholeChatData()
        for ch in checklst:
            if len(ch) == 1:
                lst = bandict.get(ch.lower(), [])
            else:
                lst = bandict.get(pubmisc.Hz2Asc(ch), [])
            elst = MxNeedDct.get(ch.lower(), [])
            for word in lst + elst:
                if word in pubbanword.g_CurWhiteList:
                    continue
                
                arr = word.split('&')
                if cls.FindKey(checktxt, arr):
                    cls.ShowBanWordInfo('#R\xab\xcc\xbd\xaa\xb9\xef\xb8\xdc(%s)(\xa5]\xa7tWChat\xa6r\xaew\xab\xcc\xbd\xaa\xb5\xfc%s)' % (txt, arr))
                    return True
                    continue
            
        
        return False

    WholeCheckBW = classmethod(WholeCheckBW)
    
    def WholeCheckHighRiskShieldedWord(cls, txt):
        '''
\t\t\xbe\xe3\xa5y\xc0\xcb\xb4\xfaHighRiskShieldedWord\xa6r\xaew\xaa\xba\xab\xcc\xbd\xaa\xb5\xfc
\t\t'''
        strobj = cls.GetBufString(txt, 2)
        checklst = strobj.GetCheckStringList()
        checktxt = ''.join(checklst)
        import pubmisc
        bandict = cls.m_Library.GetWholeHighRiskShieldedWord()
        for ch in checklst:
            if len(ch) == 1:
                lst = bandict.get(ch.lower(), [])
            else:
                lst = bandict.get(pubmisc.Hz2Asc(ch), [])
            lst = cls.FilterBlackList(lst, pubbanword.g_CurWhiteList)
            for word in lst:
                arr = word.split('&')
                if cls.FindKey(checktxt, arr):
                    return (True, word)
                    continue
            
        
        return (False, None)

    WholeCheckHighRiskShieldedWord = classmethod(WholeCheckHighRiskShieldedWord)
    
    def CheckHighRiskShieldedWord(cls, txt, bNeedBanword = False):
        '''
\t\t\xc0\xcb\xb4\xfaHighRiskShieldedWord\xa6r\xaew\xaa\xba\xab\xcc\xbd\xaa\xb5\xfc
\t\t'''
        lBanword = []
        iBanBitCount = 0
        strobj = cls.GetBufString(txt, 1)
        strchobj = strobj.GetStringCh()
        bandict = cls.m_Library.GetHighRiskShieldedWord()
        for i, ch in enumerate(strchobj.GetWordList()):
            if len(ch) == 1:
                banls = bandict.get(ch.lower(), [])
            else:
                banls = bandict.get(ch, [])
            banls = cls.FilterBlackList(banls, pubbanword.g_CurWhiteList)
            for word in banls:
                strobj.CheckWord(i, word)
                if bNeedBanword:
                    iCurBanBitCount = strchobj.GetBanBitCount()
                    if iBanBitCount != iCurBanBitCount:
                        lBanword.append(word)
                        iBanBitCount = iCurBanBitCount
                    
                iBanBitCount != iCurBanBitCount
            
        
        return (strchobj.HasBandWord(), strchobj.GetResult(), lBanword)

    CheckHighRiskShieldedWord = classmethod(CheckHighRiskShieldedWord)
    
    def CheckPublicOpinionWord(cls, sText):
        '''
\t\t\xbe\xe3\xa5y\xc0\xcb\xb4\xfaPublicOpinion\xa6r\xaew\xaa\xba\xab\xcc\xbd\xaa\xb5\xfc
\t\t'''
        strobj = cls.GetBufString(sText, 2)
        checklst = strobj.GetCheckStringList()
        checktxt = ''.join(checklst)
        import pubmisc
        bandict = cls.m_Library.GetPublicOpinionWord()
        for ch in checklst:
            if len(ch) == 1:
                lst = bandict.get(ch.lower(), [])
            else:
                lst = bandict.get(pubmisc.Hz2Asc(ch), [])
            lst = cls.FilterBlackList(lst, pubbanword.g_CurWhiteList)
            for word in lst:
                checktxt = word.split('&')
                if cls.FindKey(checktxt, checktxt):
                    return (True, word)
                    continue
            
        
        return (False, None)

    CheckPublicOpinionWord = classmethod(CheckPublicOpinionWord)
    
    def IsTooManyNum(cls, txt, ct = 4):
        strobj = cls.GetBufString(txt, 1)
        strchobj = strobj.GetStringCh()
        iBan1 = 0
        curBanChannelQQ = cls.FilterBlackList(pubbanword.BAN_CHANNEL_QQ, pubbanword.g_CurWhiteList)
        for sFilter in curBanChannelQQ:
            iBan1 += strchobj.CountWordTimes(sFilter)
        
        curBanChannelNUM = cls.FilterBlackList(pubbanword.BAN_CHANNEL_NUM, pubbanword.g_CurWhiteList)
        iBan2 = strchobj.CountConnectWords(curBanChannelNUM)
        if iBan1 >= 1 and iBan2 >= ct:
            return True
        
        return False

    IsTooManyNum = classmethod(IsTooManyNum)
    
    def WholeCheckBWEx(cls, txt):
        strobj = cls.GetBufString(txt, 2)
        checklst = strobj.GetCheckStringList()
        checktxt = ''.join(checklst)
        import pubmisc
        import hero
        if hasattr(hero.g_Prop, 'm_GradeLimit') and hero.g_Prop.m_GradeLimit < NS_LIMIT_LEV:
            bandict = cls.m_Library.GetBanWholeChatExData()
            for ch in checklst:
                if len(ch) == 1:
                    lst = bandict.get(ch.lower(), [])
                else:
                    lst = bandict.get(pubmisc.Hz2Asc(ch), [])
                for word in lst:
                    arr = word.split('&')
                    if cls.FindKey(checktxt, arr):
                        cls.ShowBanWordInfo('#R\xab\xcc\xbd\xaa\xb9\xef\xb8\xdc(%s)(\xa5]\xa7tWholeChat\xa6r\xaew\xab\xcc\xbd\xaa\xb5\xfc%s)' % (txt, arr))
                        return True
                        continue
                
            
        
        for word in NS_LIST:
            arr = word.split('&')
            if cls.FindKey(checktxt, arr):
                cls.ShowBanWordInfo('#R\xab\xcc\xbd\xaa\xb9\xef\xb8\xdc(%s)(\xa5]\xa7tWholeChat\xa6r\xaew\xab\xcc\xbd\xaa\xb5\xfc%s)' % (txt, arr))
                return True
                continue
        
        return False

    WholeCheckBWEx = classmethod(WholeCheckBWEx)
    
    def SingleCheckNumExt(cls, txt, onsale):
        banlist = pubbanword.BAN_NUM_LIST[:]
        if onsale:
            if 64 in banlist:
                banlist.remove(64)
            
            if 89 in banlist:
                banlist.remove(89)
            
        
        banlist = cls.FilterBlackList(banlist, pubbanword.g_CurWhiteList)
        import re
        strobj = cls.GetBufString(txt, 1)
        strchobj = strobj.GetStringCh()
        res = []
        pos = 0
        hasbanword = False
        patt = re.compile('[0-9]+')
        match_objs = patt.finditer(txt)
        for mo in match_objs:
            mostr = txt[mo.start():mo.end()]
            if mostr.isdigit() and int(mostr) in banlist and not strchobj.IsProtectCar(mo.start()):
                hasbanword = True
                if pos < mo.start():
                    res.append(txt[pos:mo.start()])
                    res.append(pubbanword.BAN_SIGN * len(mostr))
                    pos = mo.end()
                
            pos < mo.start()
        
        res.append(txt[pos:])
        return (hasbanword, ''.join(res))

    SingleCheckNumExt = classmethod(SingleCheckNumExt)
    
    def WholeCheckAccount(cls, txt):
        strobj = cls.GetBufString(txt, 2)
        lowerstr = txt.lower()
        strchobj = strobj.GetStringCh()
        iBan1 = 0
        banChannelQQ = cls.FilterBlackList(pubbanword.BAN_CHANNEL_QQ, pubbanword.g_CurWhiteList)
        for sFilter in banChannelQQ:
            iBan1 += strchobj.CountWordTimes(sFilter)
        
        banChannelNUM = cls.FilterBlackList(pubbanword.BAN_CHANNEL_NUM, pubbanword.g_CurWhiteList)
        iBan2 = strchobj.CountConnectWords(banChannelNUM)
        digitword = [
            'zero',
            'one',
            'two',
            'three',
            'four',
            'fivesix',
            'seven',
            'eight',
            'nine']
        for word in digitword:
            iBan2 += lowerstr.count(word)
        
        if iBan1 >= 1 and iBan2 >= 7:
            cls.ShowBanWordInfo('#R\xab\xcc\xbd\xaa\xb9\xef\xb8\xdc(%s)(\xa4@\xc3\xfe\xbc\xc6\xa6r\xa4j\xa9\xf31\xa1A\xa4G\xc3\xfe\xbc\xc6\xa6r\xa4j\xa9\xf37)' % txt)
            return True
        
        return False

    WholeCheckAccount = classmethod(WholeCheckAccount)
    
    def ChkNameBW(cls, txt, lNameWhiteList = None):
        if not lNameWhiteList:
            lNameWhiteList = []
        
        strobj = cls.GetBufString(txt, 0)
        strchobj = strobj.GetStringCh()
        checktxt = ''.join(strchobj.GetWordList())
        lb = cls.m_Library
        bandict = lb.GetBanNameData()
        lWhiteList = lNameWhiteList + pubbanword.g_CurWhiteList
        for i, ch in enumerate(strchobj.GetWordList()):
            if len(ch) == 1:
                banls = bandict.get(ch.lower(), [])
            else:
                banls = bandict.get(ch, [])
            banls = cls.FilterBlackList(banls, lWhiteList)
            for word in banls:
                arr = word.split('&')
                bResult = cls.FindKey(checktxt, arr)
                if bResult:
                    LOG_DEBUG('\xa6s\xa6b\xab\xcc\xbd\xaa\xa6r: %s' % checktxt)
                    return True
                    continue
            
        
        return strchobj.HasBandWord()

    ChkNameBW = classmethod(ChkNameBW)
    
    def ChkNameBWEx(cls, txt, lNameWhiteList = None):
        if cls.ChkNameBW(txt, lNameWhiteList):
            return True
        
        if not lNameWhiteList:
            lNameWhiteList = []
        
        strobj = cls.GetBufString(txt, 0)
        strchobj = strobj.GetStringCh()
        checktxt = ''.join(strchobj.GetWordList())
        lb = cls.m_Library
        bandictex = lb.GetBanNameExData()
        lWhiteList = lNameWhiteList + pubbanword.g_CurWhiteList
        for i, ch in enumerate(strchobj.GetWordList()):
            if len(ch) == 1:
                banls = bandictex.get(ch.lower(), [])
            else:
                banls = bandictex.get(ch, [])
            banls = cls.FilterBlackList(banls, lWhiteList)
            for word in banls:
                arr = word.split('&')
                bResult = cls.FindKey(checktxt, arr)
                if bResult:
                    LOG_DEBUG('\xa6s\xa6b\xab\xcc\xbd\xaa\xa6rex: %s' % checktxt)
                    return True
                    continue
            
        
        return strchobj.HasBandWord()

    ChkNameBWEx = classmethod(ChkNameBWEx)


class CCheck(pubbanword.CPubCheck):
    m_Condition = CCondition
    
    def IsValidNameEx(cls, txt, onsale, bCheckEx = True):
        if not cls.IsValidName(txt):
            return False
        
        condition = cls.m_Condition
        (flag1, rlt) = condition.SingleCheckNumExt(txt, onsale)
        (flag2, rlt) = condition.SingleCheckWai(rlt)
        (flag3, rlt) = condition.SingleCheckYY(rlt)
        if onsale:
            flag4 = False
        else:
            flag4 = condition.IsTooManyNum(rlt, 4)
        if flag1 and flag2 and flag3 or flag4:
            if flag1:
                pubbanword.PrintBW('\xa6s\xa6b\xab\xcc\xbd\xaa\xa6r\xa1u89\xa1v\xa1B\xa1u64\xa1v\xa1B\xa1u1989\xa1v\xa1B\xa1u5173\xa1v')
            
            if flag2:
                pubbanword.PrintBW('\xa6s\xa6b\xa1uw\xa1v\xa1B\xa1ua\xa1v\xa1B\xa1ui\xa1v\xaa\xba\xb2\xd5\xa6X')
            
            if flag3:
                pubbanword.PrintBW('\xa6s\xa6b\xa1\xd92\xad\xd3y\xa6r\xb2\xc5')
            
            return False
        
        if bCheckEx:
            return not cls.m_Condition.ChkNameBWEx(txt)
        
        return True

    IsValidNameEx = classmethod(IsValidNameEx)
    
    def IsValidName2(cls, txt, onsale, bCheckEx = True):
        condition = cls.m_Condition
        if not cls.IsValidName(txt):
            strobj = condition.GetBufString(txt, 0)
            strchobj = strobj.GetStringCh()
            rlt = strchobj.GetResult()
            return (False, rlt)
        
        (flag1, rlt) = condition.SingleCheckNumExt(txt, onsale)
        (flag2, rlt) = condition.SingleCheckWai(rlt)
        (flag3, rlt) = condition.SingleCheckYY(rlt)
        if onsale:
            flag4 = False
        else:
            flag4 = condition.IsTooManyNum(rlt, 4)
        if flag1 and flag2 and flag3 or flag4:
            return (False, rlt)
        
        if bCheckEx and condition.ChkNameBWEx(txt):
            strobj = condition.GetBufString(txt, 0)
            strchobj = strobj.GetStringCh()
            rlt = strchobj.GetResult()
            return (False, rlt)
        
        return (True, rlt)

    IsValidName2 = classmethod(IsValidName2)
    
    def IsValidOnPubChannel(cls, ch, txt):
        condition = cls.m_Condition
        if condition.IsPublicChannel(ch):
            if not cls.IsValidWholeWord(txt):
                return False
            
            if condition.WholeCheckBWEx(txt):
                return False
            
            if condition.WholeCheckAccount(txt):
                return False
            
        
        return True

    IsValidOnPubChannel = classmethod(IsValidOnPubChannel)
    
    def IsValidOnFriendMsg(cls, sender, txt):
        if not cls.IsValidWholeWord(txt):
            return False
        
        import friend
        friendship = friend.GetAttrValue(sender, 'm_FriendShip', 0)
        if friendship < 20:
            if cls.m_Condition.WholeCheckAccount(txt):
                return False
            
        
        return True

    IsValidOnFriendMsg = classmethod(IsValidOnFriendMsg)
    
    def IsValidChatEx(cls, txt, bCheckDigit = True):
        condition = cls.m_Condition
        (flag1, rlt) = condition.SingleCheckBW(txt)
        if bCheckDigit:
            (flag2, rlt) = condition.SingleCheckNum(rlt)
        else:
            flag2 = flag1
        (flag3, rlt) = condition.SingleCheckWai(rlt)
        (flag4, rlt) = condition.SingleCheckYY(rlt)
        isValid = not (flag1 | flag2 | flag3 | flag4)
        return (isValid, rlt)

    IsValidChatEx = classmethod(IsValidChatEx)
    
    def IsValidOnIntrodruce(cls, txt):
        if not cls.IsValidWholeWord(txt):
            return False
        
        if cls.m_Condition.WholeCheckAccount(txt):
            return False
        
        return True

    IsValidOnIntrodruce = classmethod(IsValidOnIntrodruce)
    
    def IsValidHighRiskShieldedWord(cls, txt):
        '''
\t\t\xb0\xaa\xa6M\xab\xcc\xbd\xaa\xa6r\xa1A\xb5o\xb2{\xa5\xb2\xb6\xb7\xa5\xdf\xa7Y\xb3B\xb2z
\t\t'''
        (bRet, _, sDangerWords) = cls.m_Condition.CheckHighRiskShieldedWord(txt, bNeedBanword = True)
        if bRet:
            return (False, sDangerWords)
        
        return (True, None)

    IsValidHighRiskShieldedWord = classmethod(IsValidHighRiskShieldedWord)
    
    def IsValidWholeCheckHighRiskShieldedWord(cls, txt):
        '''
\t\t\xb0\xaa\xa6M\xab\xcc\xbd\xaa\xa6r\xa1A\xb5o\xb2{\xa5\xb2\xb6\xb7\xa5\xdf\xa7Y\xb3B\xb2z
\t\t'''
        (bRet, sDangerWord) = cls.m_Condition.WholeCheckHighRiskShieldedWord(txt)
        if bRet:
            return (False, [
                sDangerWord])
        
        return (True, None)

    IsValidWholeCheckHighRiskShieldedWord = classmethod(IsValidWholeCheckHighRiskShieldedWord)
    
    def IsValidPublicOpinionWord(cls, txt):
        '''
\t\t\xa4\xbd\xa6@\xc0\xcb\xb4\xfa\xb1\xc0\xb0e 2021\xa6~\xa4C\xa4@\xc1\xd6\xb1\xa1\xb7s\xbcW\xa6r\xaew
\t\t'''
        (bRet, sDangerWord) = cls.m_Condition.CheckPublicOpinionWord(txt)
        if bRet:
            return (False, [
                sDangerWord])
        
        return (True, None)

    IsValidPublicOpinionWord = classmethod(IsValidPublicOpinionWord)


class CBanCheckMgr(object):
    '''
\t\xbdu\xa4W\xc0\xcb\xacd\xaa\xb1\xaea\xacO\xa7_\xafA\xa4\xce\xa8\xec\xab\xcc\xbd\xaa\xa6r\xa4\xba\xaee\xa1A\xb5o\xb5\xb9\xaaA\xb0\xc8\xbe\xb9\xb0O\xbf\xfd\xa4\xe9\xbbx
\t'''
    sTYPE2INT = {
        'name': '\xaa\xb1\xaea\xa9m\xa6W',
        'orgmembername': '\xa5\xbf\xa6\xa1\xa6\xa8\xad\xfb\xa6W\xba\xd9',
        'orgxuetuname': '\xbe\xc7\xae{\xa6W\xba\xd9',
        'orgjimingname': '\xb0O\xa6W\xa6W\xba\xd9',
        'orgname': '\xa6\xdb\xa4v\xc0\xb0\xac\xa3\xa6W\xba\xd9',
        'orgnamelist': '\xa8\xe4\xa5L\xc0\xb0\xac\xa3\xa6W\xba\xd9',
        'orgintro': '\xc0\xb0\xac\xa3\xa4\xb6\xb2\xd0',
        'title': '\xba\xd9\xbf\xd7',
        'boke': '\xb3\xd5\xab\xc8',
        'pet': '\xc3d\xaa\xab\xa9R\xa6W',
        'show': '\xafu\xa4H\xa8q',
        'shopname': '\xb0\xd3\xa9\xb1\xa6W',
        'shopintro': '\xb0\xd3\xa9\xb1\xc2\xb2\xa4\xb6',
        'storehorsename': '\xad\xdc\xaew\xa6W',
        'flyposname': '\xad\xb8\xa6\xe6\xbaX\xa6\xec\xb8m\xa6W',
        'magicpreceptname': '\xa9\xdb\xa6\xa1\xa4\xe8\xae\xd7',
        'horsepetname': '\xc3d\xaa\xab\xa4\xa7\xaea\xa4p\xb0\xca\xaa\xab',
        'friendmarkname': '\xa6n\xa4\xcd\xb3\xc6\xb5\xf9',
        'actfrdmarkname': '\xbe\xd4\xa4\xcd\xb3\xc6\xb5\xf9',
        'commandname': '\xab\xfc\xb4\xa7\xb3]\xb8m',
        'dailyteamintro': '\xbe\xd4\xb6\xa4\xa9v\xa6\xae',
        'dailyteamname': '\xbe\xd4\xb6\xa4\xa6W',
        'baitanname': '\xc2\\\xc5u\xa6W',
        'orgprename': '\xc5T\xc0\xb3\xc0\xb0\xac\xa3\xa6W',
        'warpreparename': '\xbe\xd4\xabe\xb7\xc7\xb3\xc6\xa4\xe8\xae\xd7',
        'flypostext': '\xa4\xe5\xa6r\xbc\xd2\xa6\xa1\xbaX\xa4l\xa6\xec\xb8m\xa6W' }
    
    def __init__(self):
        self.m_oCheckTaskList = []
        self.m_oCheckTimer = None
        self.m_sPetDefaultNameList = []

    
    def GetHighRiskBanWordVer(self):
        (iHighRiskBanWord, _) = CLibrary.ReadBL(CLibrary.LB_HIGHRISKSHIELDEDWORD)
        (iWholeHighRiskBanWord, _) = CLibrary.ReadBL(CLibrary.LB_WHOLEHIGHRISKSHIELDEDWORD)
        return int(iHighRiskBanWord) + int(iWholeHighRiskBanWord)

    
    def AddCheckTask(self, sTxt, sType):
        import delayloading
        if not hero.GetHeroID():
            return None
        
        sLocal = cfg.GetData('users/local.ini', '%dCheck' % hero.GetHeroID(), sType)
        iHighRiskBanWordVer = self.GetHighRiskBanWordVer()
        if sLocal and int(sLocal) == iHighRiskBanWordVer:
            return None
        
        if type(sTxt) == list:
            for sName in sTxt:
                oTask = misc.Functor(self.CheckTxt, sName, sType)
                self.m_oCheckTaskList.append(oTask)
            
        else:
            oTask = misc.Functor(self.CheckTxt, sTxt, sType)
            self.m_oCheckTaskList.append(oTask)
        if sType not in ('show', 'shopintro', 'title', 'shopname', 'friendmarkname', 'flyposname', 'warpreparename', 'flypostext', 'dailyteamname', 'dailyteamintro', 'actfrdmarkname', 'commandname', 'pet'):
            cfg.SaveData('users/local.ini', '%dCheck' % hero.GetHeroID(), sType, iHighRiskBanWordVer)
        
        if not delayloading.IsShowLoading():
            self.StartCheck()
        

    
    def StartCheck(self):
        import timer
        if self.m_oCheckTimer:
            self.m_oCheckTimer.Release()
        
        self.m_oCheckTimer = timer.Timer(0.033, self.DoCheck, -1, self)

    
    def DoCheck(self):
        if self.m_oCheckTaskList:
            oTask = self.m_oCheckTaskList.pop(0)
            oTask()
        
        if not self.m_oCheckTaskList:
            self.OnFinishTask()
        

    
    def CheckTxt(self, sTxt, sType):
        if sType in ('name', 'orgmembername', 'orgxuetuname', 'orgjimingname', 'orgname', 'orgnamelist', 'title', 'boke', 'pet', 'show', 'shopname', 'storehorsename', 'flyposname', 'magicpreceptname', 'horsepetname', 'friendmarkname', 'commandname', 'dailyteamname', 'baitanname', 'orgprename', 'warpreparename', 'flypostext', 'actfrdmarkname'):
            self.CheckName(sTxt, sType)
        elif sType in ('orgintro', 'shopintro', 'dailyteamintro'):
            self.CheckIntro(sTxt, sType)
        

    
    def CheckName(self, sTxt, sType):
        import wrapui
        if not hero.GetHeroID():
            return None
        
        sTranType = self.sTYPE2INT[sType]
        iPid = 0
        if type(sTxt) == tuple:
            (sName, iPid) = sTxt
        else:
            sName = sTxt
        if sType == 'title':
            
            try:
                (_, sName, _) = wrapui.HandleLink(sName, None)

        elif sType == 'pet':
            if self.IsPetDefaultName(sName):
                return None
            
        
        self.CheckNameForFunc(sName, iPid, sTranType, sType, IsValidName, netcommon.C2SUnValidName)
        if iPid:
            sAdd = '(' + str(iPid) + ')'
        else:
            sAdd = ''
        ChackAndSendMsg(sTranType, sAdd, sName)

    
    def CheckNameForFunc(self, sName, iPid, sTranType, sType, oFunc, oSendFunc):
        if not oFunc(sName):
            if iPid:
                sName = '(' + str(iPid) + ')' + sName
            
            if self.CheckSpecialRule(sName, sType, oFunc):
                return None
            
            oSendFunc(sTranType, sName)
        

    
    def CheckSpecialRule(self, sName, sType, oFunc):
        import misc
        if sType == 'pet':
            if '\xaf\xab\xc3~' in sName or '\xa5P\xc3~' in sName:
                if '\xaf\xab\xc3~' in sName:
                    sNewName = sName.replace('\xaf\xab\xc3~', '')
                    if oFunc(sNewName):
                        return True
                    
                elif '\xa5P\xc3~' in sName:
                    sNewName = sName.replace('\xa5P\xc3~', '')
                    if oFunc(sNewName):
                        return True
                    
                
            elif self.CheckRoleName(sName)[0]:
                sRole = self.CheckRoleName(sName)[1]
                sNewName = sName.replace(sRole, '')
                if oFunc(sNewName):
                    return True
                
            elif '\xaf\xab\xaaZ\xb4L' in sName or '\xb3B\xa4k\xaey' in sName:
                return True
            elif not misc.IsChinese(sName):
                sTmpStr = ''
                sCharList = misc.GetWordsCN(sName)
                for sChar in sCharList:
                    if misc.IsChinese(sChar):
                        sTmpStr += sChar
                        continue
                
                if oFunc(sTmpStr):
                    return True
                
            
        return False

    
    def IsPetDefaultName(self, sName):
        import petdata
        if not self.m_sPetDefaultNameList:
            self.m_sPetDefaultNameList = []
            for dData in petdata.DATA.itervalues():
                self.m_sPetDefaultNameList.append(dData['name'])
            
            self.m_sPetDefaultNameList = set(self.m_sPetDefaultNameList)
        
        return sName in self.m_sPetDefaultNameList

    
    def CheckRoleName(self, sName):
        import createrole
        for sRole in createrole.ROLE:
            if sRole in sName:
                return (True, sRole)
                continue
        
        return (False, '')

    
    def CheckIntro(self, sTxt, sType):
        if not hero.GetHeroID():
            return None
        
        sTranType = self.sTYPE2INT[sType]
        if type(sTxt) == tuple:
            (sTxt, iPid) = sTxt
            sName = '(' + str(iPid) + ')'
        else:
            sTxt = sTxt
            sName = ''
        if not IsValidOnIntrodruce(sTxt):
            netcommon.C2SUnValidName(sTranType, sName + sTxt)
        
        ChackAndSendMsg(sTranType, sName, sTxt)

    
    def OnFinishTask(self):
        global g_CheckMgr
        self.m_oCheckTaskList = []
        if self.m_oCheckTimer:
            self.m_oCheckTimer.Release()
            self.m_oCheckTimer = None
        
        g_CheckMgr = None
