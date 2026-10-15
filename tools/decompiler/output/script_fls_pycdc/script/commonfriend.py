# pycdc 交叉复核产物 · script.fls entry 1223
# co_filename(原始)='script/commonfriend.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1223.pyc (Python 2.5)

import permission
import mdaddfriend
TYPE_FRIEND = 0
TYPE_ACFRIEND = 1

def ModuleReset():
    CRequestManage.Clear()
    CAcFrdRequestManage.ResetClear()
    CFrdRequestManage.ResetClear()


class CRequestManage:
    
    def AddRequestObj(cls, ID, obj):
        cls.s_RequestObjDct[ID] = obj

    AddRequestObj = classmethod(AddRequestObj)
    
    def GetRequestObj(cls, ID):
        return cls.s_RequestObjDct.get(ID, None)

    GetRequestObj = classmethod(GetRequestObj)
    
    def AddRequestID(cls, ID):
        if ID in cls.s_RequestList:
            cls.s_RequestList.remove(ID)
        
        cls.s_RequestList.append(ID)

    AddRequestID = classmethod(AddRequestID)
    
    def GetRequestList(cls):
        return cls.s_RequestList

    GetRequestList = classmethod(GetRequestList)
    
    def SetUnReadAmount(cls, amount):
        cls.s_RequestAmount = amount

    SetUnReadAmount = classmethod(SetUnReadAmount)
    
    def GetUnReadAmount(cls):
        return cls.s_RequestAmount

    GetUnReadAmount = classmethod(GetUnReadAmount)
    
    def Clear(cls):
        cls.s_RequestObjDct = { }
        cls.s_RequestList = []
        cls.s_RequestAmount = 0

    Clear = classmethod(Clear)


class CRequest:
    
    def SetData(self, dInfo):
        self.SetNickName(dInfo['nick'])
        self.SetReadStatus(dInfo['status'])

    
    def SetNickName(self, sName):
        self.m_NickName = sName

    
    def SetReadStatus(self, iStatus):
        self.m_ReadStatus = iStatus

    
    def SetLinkType(self, linkType):
        self.m_LinkType = linkType

    
    def SetRequestTime(self, iTime):
        self.m_RequestTime = iTime

    
    def GetNickName(self):
        if hasattr(self, 'm_NickName') and self.m_NickName and ',' not in self.m_NickName:
            return self.m_NickName
        
        return '<%d>' % self.m_ID

    
    def GetReadStatus(self):
        return getattr(self, 'm_ReadStatus', 0)

    
    def GetLinkType(self):
        return getattr(self, 'm_LinkType', 0)

    
    def GetRequestTime(self):
        return getattr(self, 'm_RequestTime', None)



class CAcFrdRequestManage(CRequestManage):
    s_RequestObjDct = { }
    s_RequestList = []
    s_RequestAmount = 0
    s_IsGetRequest = False
    
    def ResetClear(cls):
        cls.s_RequestObjDct = { }
        cls.s_RequestList = []
        cls.s_RequestAmount = 0
        cls.s_IsGetRequest = False

    ResetClear = classmethod(ResetClear)
    
    def GetRequest(cls):
        if cls.s_IsGetRequest:
            return None
        
        cls.s_IsGetRequest = True
        import netaccountfriend
        netaccountfriend.C2SCheckRequest()

    GetRequest = classmethod(GetRequest)
    
    def dAAw@TP@stID2Status(cls, ID, status):
        if (ID, status) in cls.s_RequestList:
            cls.s_RequestList.remove((ID, status))
        
        cls.s_RequestList.append((ID, status))

    dAAw@TP@stID2Status = classmethod(dAAw@TP@stID2Status)


class CAcFrdRequest(CRequest):
    
    def __init__(self, ID):
        self.m_ID = ID
        CAcFrdRequestManage.AddRequestObj(ID, self)

    
    def SetData(self, dInfo):
        self.SetType(dInfo['type'])
        self.SetNickName(dInfo['nick'])
        self.SetReadStatus(dInfo.get('status', 0))

    
    def SetType(self, iType):
        self.m_Type = iType



class CFrdRequestManage(CRequestManage):
    s_RequestObjDct = { }
    s_RequestList = []
    s_RequestAmount = 0
    s_IsFirstRefresh = True
    s_IsFlash = False
    
    def ResetClear(cls):
        cls.s_RequestObjDct = { }
        cls.s_RequestList = []
        cls.s_RequestAmount = 0
        cls.s_IsFirstRefresh = True
        cls.s_IsFlash = False

    ResetClear = classmethod(ResetClear)
    
    def ComputeUnRead(cls):
        iAmount = 0
        for obj in cls.s_RequestObjDct.values():
            if obj.GetReadStatus() == 0:
                iAmount += 1
                continue
        
        cls.s_RequestAmount = iAmount
        if iAmount and cls.s_IsFirstRefresh:
            cls.s_IsFirstRefresh = False
            cls.SetIsFlash(True)
        

    ComputeUnRead = classmethod(ComputeUnRead)
    
    def SetIsFlash(cls, bFlash):
        cls.s_IsFlash = bFlash
        import mainmenu
        mainmenu.RefreshPlayerNotify()

    SetIsFlash = classmethod(SetIsFlash)
    
    def GetIsFlash(cls):
        return cls.s_IsFlash

    GetIsFlash = classmethod(GetIsFlash)
    
    def DoReadRequest(cls):
        import netfriend
        if not cls.GetIsFlash():
            return None
        
        cls.SetIsFlash(False)
        netfriend.C2SOpenApplyFriendDlg()

    DoReadRequest = classmethod(DoReadRequest)


class CFrdRequest(CRequest):
    
    def __init__(self, ID):
        self.m_ID = ID
        CFrdRequestManage.AddRequestObj(ID, self)

    
    def SetData(self, dInfo):
        self.SetFrdType(dInfo['frdtype'])
        self.SetNickName(dInfo['nick'])
        self.SetReadStatus(dInfo.get('status', 0))
        self.SetLinkType(dInfo.get('linkType', 0))
        self.SetRequestTime(dInfo.get('time', None))

    
    def SetFrdType(self, frdType):
        self.m_FrdType = frdType

    
    def GetFrdType(self):
        return self.m_FrdType



def Type2Cls(iFrdType):
    (clsManage, clsObj) = None if iFrdType == TYPE_FRIEND else (CAcFrdRequestManage, CAcFrdRequest)
    return (clsManage, clsObj)


def SetRequestList(rqList, iFrdType = TYPE_FRIEND):
    (clsManage, clsObj) = Type2Cls(iFrdType)
    clsManage.Clear()
    for ID, dInfo in rqList:
        obj = clsObj(ID)
        obj.SetData(dInfo)
        if iFrdType:
            clsManage.dAAw@TP@stID2Status(ID, dInfo.get('status', 0))
            continue
        clsManage.AddRequestID(ID)
    
    if iFrdType == TYPE_FRIEND and not permission.IsOpenNewFriend():
        clsManage.ComputeUnRead()
        AmountRefresh()
    


def GetRequestList(iFrdType = TYPE_FRIEND):
    (clsManage, _) = Type2Cls(iFrdType)
    return clsManage.GetRequestList()


def RefreshRequestState(ID, iStatus, iFrdType = TYPE_FRIEND):
    obj = GetRequestObj(ID, iFrdType)
    if not obj:
        return None
    
    obj.SetReadStatus(iStatus)


def AddFrdRequest(ID, iFriendType, name, linkType, rtime):
    if not permission.IsOpenNewFriend():
        (clsManage, clsObj) = Type2Cls(TYPE_FRIEND)
        None = {
            'frdtype': iFriendType,
            'status': name } / 'nick'


def SetFriendFlash(bFlash):
    (clsManage, clsObj) = Type2Cls(TYPE_FRIEND)
    clsManage.SetIsFlash(bFlash)


def AddAcFrdRequest(ID, iType, name):
    (clsManage, clsObj) = Type2Cls(TYPE_ACFRIEND)
    dInfo = {
        'type': iType,
        'nick': name,
        'status': 0 }
    obj = clsObj(ID)
    obj.SetData(dInfo)
    clsManage.dAAw@TP@stID2Status(ID, dInfo['status'])


def GetRequestObj(ID, iFrdType = TYPE_FRIEND):
    (clsManage, _) = Type2Cls(iFrdType)
    return clsManage.GetRequestObj(ID)


def GetUnReadAmount(iFrdType = -1):
    if not permission.IsOpenNewFriend():
        if iFrdType in (TYPE_FRIEND, TYPE_ACFRIEND):
            (clsManage, _) = Type2Cls(iFrdType)
            iAmount = clsManage.GetUnReadAmount()
        else:
            iAmount = CAcFrdRequestManage.GetUnReadAmount()
    else:
        return mdaddfriend.GetAddFriendModel().GetRedPointNum()
    return iAmount


def SetUnReadAmount(iAmount, iFrdType = TYPE_FRIEND):
    (clsManage, _) = Type2Cls(iFrdType)
    clsManage.SetUnReadAmount(iAmount)
    AmountRefresh()


def AmountRefresh():
    import commoncb
    commoncb.TriggerCB(commoncb.FRIEND_UNREAD_MSG)
    import dlgfriend
    dlgfriend.RefreshSysMsgAmount()
