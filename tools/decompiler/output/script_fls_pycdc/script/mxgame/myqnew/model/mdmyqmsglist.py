# pycdc 交叉复核产物 · script.fls entry 25
# co_filename(原始)='script/mxgame/myqnew/model/mdmyqmsglist.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_25.pyc (Python 2.5)

import slot
import myqdefine
import json
import \xf1\xf5\xef\xff
KEY_MYQ_CONTENT = ('usergame', 'momentguid', 'moment_content', 'moment_atids', 'moment_voice', 'moment_pics')
KEY_MYQ_USER = ('username', 'userid', 'userpic', 'isfaction')
KEY_MYQ_MSG = ('messageguid', 'addtime', 'type', 'isdel', 'voice', 'atids', 'content', 'commentCount', 'proCount')
g_oMyQMsgListMgr = None

def ModuleReset():
    global g_oMyQMsgListMgr
    g_oMyQMsgListMgr = None


def GetMyQMsgList():
    global g_oMyQMsgListMgr
    if not g_oMyQMsgListMgr:
        g_oMyQMsgListMgr = CMYQMsgListMgr()
    
    return g_oMyQMsgListMgr


class COneMsgData(object):
    
    def __init__(self, iMsgID, dData):
        self.m_iMsgID = iMsgID
        self.m_dData = dData
        self.m_bOldMsg = False
        self.ConvertProp()

    
    def SetIsOldMsgObj(self, bOld):
        self.m_bOldMsg = bOld

    
    def IsOldMsgObj(self):
        return self.m_bOldMsg

    
    def ConvertProp(self):
        import \xf1\xf5\xef\xff
        tKey = ('moment_content', 'username', 'content')
        for sKey in tKey:
            self.m_dData[sKey] = \xf1\xf5\xef\xff.AsciiStr2BinaryStr(self.m_dData.get(sKey, ''))
        

    
    def GetAddTime(self):
        return self.GetValueByKey('addtime')

    
    def GetMsgID(self):
        return self.m_iMsgID

    
    def GetMsgType(self):
        return self.GetValueByKey('type')

    
    def GetCommentCount(self):
        return self.GetValueByKey('commentCount', 0)

    
    def GetCommentPic(self):
        sPic = self.GetValueByKey('moment_pics')
        if not sPic:
            return ''
        else:
            return sPic.split(',')[0]

    
    def GetParseCount(self):
        return self.GetValueByKey('proCount', 0)

    
    def GetGroupType(self):
        iType = self.GetMsgType()
        if iType in (myqdefine.MSG_TYPE_COMMENT_BACK, myqdefine.MSG_TYPE_COMMENT):
            return myqdefine.MSG_TYPE_COMENT_OR_BACK
        else:
            return iType

    
    def GetMomentID(self):
        return self.GetValueByKey('momentguid')

    
    def GetValueByKey(self, sKey, oDefaultValue = None):
        sValue = self.m_dData.get(sKey, oDefaultValue)
        return sValue

    
    def GetContent(self, sKey, iMinLen = 12, sEnd = '...'):
        if sKey in ('moment_content', 'content'):
            sTxt = self.m_dData.get(sKey, '')
            if not sTxt:
                return ''
            
            lOriCN = \xf1\xf5\xef\xff.GetWordsCN(sTxt, 0)
            lWdCN = \xf1\xf5\xef\xff.GetWordsCN(sTxt, iMinLen)
            if lOriCN == lWdCN:
                return sTxt
            else:
                return ''.join(lWdCN) + sEnd
        
        return ''

    
    def GetTouXiang(self):
        import myqinterface
        sPic = self.GetValueByKey('userpic')
        sPic = \xf1\xf5\xef\xff.ReadJson(sPic)
        iUserID = self.GetValueByKey('userid')
        return myqinterface.GetUserRealTouXiang(iUserID, sPic)



class CMYQMsgListMgr(slot.ISignalSubject):
    SS_UpdateMsgList = 'SS_UpdateMsgList'
    SS_DelMsgList = 'SS_DelMsgList(lDel, lDelObj)'
    SS_Clear = 'SS_Clear'
    
    def __init__(self):
        self.ssInit()
        self.m_sIP = ''
        self.m_dAllMsg = { }
        self.m_lMsgUID = []
        self.m_dMoment2MsgID = { }
        self.m_iLastVisitTime = 0
        self.ResetVisitTime()

    
    def ResetVisitTime(self):
        import hero
        import time
        iTime = hero.GetPrivateData('Game', 'myqmsglastrequesttime')
        if not iTime:
            iTime = 0
        else:
            
            try:
                iTime = int(iTime)
            except:
                iTime = 0

        iCurTime = time.time()
        if iCurTime < iTime:
            iTime = min(int(iCurTime), iTime)
        
        self.m_iLastVisitTime = iTime

    
    def IsOldMsg(self, oMsgObj):
        if not self.m_iLastVisitTime:
            return False
        
        return oMsgObj.GetAddTime() < self.m_iLastVisitTime

    
    def GetMsgIDList(self):
        return self.m_lMsgUID

    
    def RefreshMyIP(self, sIP):
        self.m_sIP = sIP

    
    def UpdateMsgList(self, lMsg):
        dMoment2MsgID = { }
        lNewMsgID = []
        dMsgObj = { }
        for dOneMsg in lMsg:
            iMsgID = dOneMsg.get('messageguid')
            if not iMsgID:
                LOG('has not msgguid', dOneMsg)
                continue
            
            oMsgObj = COneMsgData(iMsgID, dOneMsg)
            dMsgObj[iMsgID] = oMsgObj
            if iMsgID not in lNewMsgID:
                lNewMsgID.append(iMsgID)
            
            iMomentID = oMsgObj.GetMomentID()
            if iMomentID not in dMoment2MsgID:
                dMoment2MsgID[iMomentID] = []
            
            lMsgID = dMoment2MsgID[iMomentID]
            if iMsgID not in lMsgID:
                lMsgID.append(iMsgID)
                continue
        
        iSumLen = len(lNewMsgID)
        for iIndex in range(iSumLen):
            iMsgID = lNewMsgID[iSumLen - 1 - iIndex]
            oMsgObj = dMsgObj[iMsgID]
            if not self.IsOldMsg(oMsgObj):
                pass
            bOld = iMsgID in self.m_lMsgUID
            if oMsgObj.GetCommentCount() < 1:
                pass
            bSaftyOld = oMsgObj.GetParseCount() < 1
            if bOld and bSaftyOld:
                oMsgObj.SetIsOldMsgObj(True)
                continue
        
        self.m_dAllMsg = dMsgObj
        self.m_lMsgUID = lNewMsgID
        self.m_dMoment2MsgID = dMoment2MsgID
        self.ssEmit(self.SS_UpdateMsgList)
        self.ResetVisitTime()

    
    def Clear(self):
        self.m_dAllMsg = { }
        self.m_lMsgUID = []
        self.m_dMoment2MsgID = { }
        self.ssEmit(self.SS_Clear)

    
    def DelMsgByID(self, sMsgID, bSignal = False):
        oMsgObj = self.m_dAllMsg[sMsgID]
        if not oMsgObj:
            return None
        
        iMomentID = oMsgObj.GetMomentID()
        if sMsgID in self.m_dAllMsg:
            del self.m_dAllMsg[sMsgID]
        
        if sMsgID in self.m_lMsgUID:
            self.m_lMsgUID.remove(sMsgID)
        
        if iMomentID in self.m_dMoment2MsgID:
            lMMsgID = self.m_dMoment2MsgID[iMomentID]
            if sMsgID in lMMsgID:
                lMMsgID.remove(sMsgID)
            
        
        if bSignal:
            self.ssEmit(self.SS_DelMsgList, (oMsgObj,))
        
        return oMsgObj

    
    def GetMsg(self, iMsgID):
        ''':rtype COneMsgData'''
        return self.m_dAllMsg.get(iMsgID)
