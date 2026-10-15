# pycdc 交叉复核产物 · script.fls entry 1523
# co_filename(原始)='script/mxgame/mail/model/mdmail.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1523.pyc (Python 2.5)

import slot
import maildefine
g_MailMgr = None
g_ItemMailMgr = None

def ModuleReset():
    global g_MailMgr
    g_MailMgr = None
    GetItemMailMgr().Clear()


def GetMailMgr():
    ''':rtype: CSystemMailgMgr'''
    global g_MailMgr
    if not g_MailMgr:
        g_MailMgr = CSystemMailgMgr()
    
    return g_MailMgr


def GetItemMailMgr():
    ''':rtype: CItemMailMgr'''
    global g_ItemMailMgr
    if not g_ItemMailMgr:
        g_ItemMailMgr = CItemMailMgr()
    
    return g_ItemMailMgr


class CSystemMailgMgr(slot.ISignalSubject):
    
    def __init__(self):
        self.m_dMailInfoLi = []
        self.InitListener()

    
    def InitListener(self):
        self.ssInit()
        self.ssCreate(maildefine.SS_UpdateMailInfoList)

    
    def SetMailInfoList(self, dInfoList):
        '''
\t\t\xb3]\xb8m\xa8t\xb2\xce/\xa4\xbd\xa7i\xb6l\xa5\xf3\xa4\xba\xaee\xa6C\xaa\xed
\t\t:param dInfoList:
\t\t[
\t\t{
\t\t\tiId,\t\xb6l\xa5\xf3ID
\t\t\tsTitle,\t\xbc\xd0\xc3D
\t\t\tiSendId,\t\xb1H\xa5\xf3\xa4HID
\t\t\tsSendName,\t\xb1H\xa5\xf3\xa4H\xa6W\xa6r
\t\t\tiState,\t\xb6l\xa5\xf3\xaa\xac\xbaA0-\xa5\xbc\xbb\xe2\xa8\xfa,1-\xa4w\xbb\xe2\xa8\xfa,2-\xa4w\xb9L\xb4\xc1
\t\t\tiSendTime,\t\xb5o\xb0e\xae\xc9\xb6\xa1
\t\t\tdRewardList,\t\xbc\xfa\xc0y\xaa\xab\xab~\xa6C\xaa\xed[
\t\t\t\t{
\t\t\t\t\t\tiShapeId\t4,
\t\t\t\t\t\tiAmount\t1,
\t\t\t\t}
\t\t\t]
\t\t\tiOverTime,\t\xa8\xec\xb4\xc1\xae\xc9\xb6\xa1
\t\t\tiLookState,\t1\t\xacd\xac\xdd\xaa\xac\xbaA0-\xa5\xbc\xacd\xac\xdd\xa1A1-\xa4w\xacd\xac\xdd
\t\t},
\t\t]
\t\t'''
        self.m_dMailInfoLi = dInfoList
        self.m_dMailInfoLi.sort(key = (lambda data: data['iSendTime']))
        self.ssEmit(maildefine.SS_UpdateMailInfoList)

    
    def GetMailInfoList(self):
        return self.m_dMailInfoLi



class CItemMailMgr(slot.ISignalSubject):
    '''
\t\xaa\xab\xab~\xc3\xfe\xb6l\xa5\xf3\xba\xde\xb2z\xa4u\xa8\xe3
\t'''
    SS_UpdateItemMailCount = 'UpdateItemMailCount(iItemMailCount)'
    
    def __init__(self):
        self.ssInit()
        self.m_iItemMailCount = 0

    
    def SetItemMailCount(self, iItemMailCount):
        self.m_iItemMailCount = iItemMailCount
        self.EmitItemMailCount(iItemMailCount)

    
    def GetItemMailCount(self):
        return self.m_iItemMailCount

    
    def Clear(self):
        self.m_iItemMailCount = 0

    
    def EmitItemMailCount(self, iItemMailCount):
        self.ssEmit(self.SS_UpdateItemMailCount, iItemMailCount)



def TestData():
    Model = GetMailMgr()
    dMailInfoList = [
        {
            'iId': 1,
            'sTitle': '\xbc\xd0\xc3D1',
            'iSendId': 10087,
            'sSendName': 'test10087',
            'iState': 0,
            'iSendTime': 11101010,
            'dRewardList': [
                {
                    'iShape': 72819,
                    'iAmount': 1 },
                {
                    'iShape': 72819,
                    'iAmount': 1 }],
            'iOverTime': 14000000,
            'iLookState': 0 },
        {
            'iId': 2,
            'sTitle': '\xbc\xd0\xc3D2',
            'iSendId': 10088,
            'sSendName': 'test10088',
            'iState': 0,
            'iSendTime': 11101010,
            'dRewardList': [
                {
                    'iShape': 72819,
                    'iAmount': 1 },
                {
                    'iShape': 72819,
                    'iAmount': 1 },
                {
                    'iShape': 72819,
                    'iAmount': 1 }],
            'iOverTime': 14000000,
            'iLookState': 0 },
        {
            'iId': 3,
            'sTitle': '\xbc\xd0\xc3D3',
            'iSendId': 10089,
            'sSendName': 'test10089',
            'iState': 0,
            'iSendTime': 11101010,
            'dRewardList': [],
            'iOverTime': 14000000,
            'iLookState': 0 }]
    Model.SetMailInfoList(dMailInfoList)
