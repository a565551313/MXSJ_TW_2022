# pycdc 交叉复核产物 · script.fls entry 1718
# co_filename(原始)='script/dialog/avaterload.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1718.pyc (Python 2.5)

import os
import time
import cfg
import misc
import timer
import slot
g_AvatarMgr = None
E_MAX_REQUESTAVATAT = 50
E_MAX_SAVENUM = 600
CACHE_VALID_TIME = 600
CACHE_FILE = 'users/avatar_cache.ini'

def ModuleReset():
    global g_AvatarMgr
    g_AvatarMgr = None


def C2SGetAvatar(iUidLst):
    import net
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_OPEN_UI)
    netobj.PacketAddI(42, 1)
    netobj.PacketAddI(255, 1)
    netobj.PacketAddI(len(iUidLst), 1)
    for iUid in iUidLst:
        netobj.PacketAddI(iUid, 4)
    
    netobj.PacketSend()


def Get():
    ''':rtype: CAvaterLoadMgr'''
    global g_AvatarMgr
    if not g_AvatarMgr:
        g_AvatarMgr = CAvaterLoadMgr()
    
    return g_AvatarMgr


class CAvaterLoadMgr(slot.ISignalSubject):
    SS_LoadAvaterFinished = 'LoadAvaterFinished'
    
    def __init__(self):
        self.m_dLoadResult = { }
        self.m_sTypeFirst = ''
        self.m_sCurLoadType = ''
        self.m_lCurLoadQueue = []
        self.m_nLastRequestIndex = 0
        self.m_lLoadQueue = []
        self.m_pRequestTimer = None
        self.m_pFirstRequestTimer = None
        self.m_dType2LoadQueue = { }
        self.m_dID2Type = { }
        self.m_lLastRequestQueue = []
        self.m_pDelaySaveTimer = None
        self.LoadFromCache()
        self.InitSignal()

    
    def LoadFromCache(self):
        sFName = CACHE_FILE
        sSection = 'avatar'
        bCacheValid = True
        
        try:
            if os.path.exists(sFName):
                iChangeTime = os.path.getmtime(sFName)
                iCurTime = time.time()
                if abs(iChangeTime - iCurTime) > CACHE_VALID_TIME:
                    self.m_dLoadResult = { }
                    bCacheValid = False
                
        except:
            pass

        if bCacheValid:
            d = cfg._read(sFName)
            s = { }
            if d is not None:
                s = d.get(sSection)
            
            if s is None:
                s = { }
            
            self.m_dLoadResult = s
        

    
    def Save2Cache(self):
        '''\xc1\xd7\xa7K\xc0W\xc1c\xaa\xbaID \xa5\xbb\xa6a\xa4\xc6 1 s \xc4\xc1\xbcg\xa4@\xa6\xb8
\t\t:return:
\t\t'''
        if self.m_pDelaySaveTimer:
            return None
        
        self.m_pDelaySaveTimer = timer.Timer(1, self.RealSave2LocalCache)

    
    def RealSave2LocalCache(self):
        import cfg
        if self.m_pDelaySaveTimer:
            self.m_pDelaySaveTimer.Release()
            self.m_pDelaySaveTimer = None
        
        if len(self.m_dLoadResult) > E_MAX_SAVENUM:
            lKeys = self.m_dLoadResult.keys()
            lKeys = lKeys[:E_MAX_SAVENUM / 2]
            dSaveData = { }
            for sKey in lKeys:
                dSaveData[sKey] = self.m_dLoadResult[sKey]
            
        else:
            dSaveData = self.m_dLoadResult
        dResult = {
            'avatar': dSaveData }
        cfg._write(CACHE_FILE, dResult)

    
    def SetLoadTypeFirst(self, sType):
        if self.m_sTypeFirst == sType:
            return None
        
        self.m_sTypeFirst = sType
        self.m_sCurLoadType = sType
        self.m_lCurLoadQueue = self.m_dType2LoadQueue.get(self.m_sTypeFirst)
        self.m_nLastRequestIndex = 0

    
    def GetAvatarFromCache(self, iUid):
        if not self.m_dLoadResult:
            return ''
        
        sKey = str(iUid) + '-' + str(misc.GetServerID())
        sKey = sKey.lower()
        sValue = self.m_dLoadResult.get(sKey, '')
        tValue = self.IsIllegalAvatar(sValue)
        if tValue:
            return sValue
        elif sKey in self.m_dLoadResult:
            del self.m_dLoadResult[sKey]
        
        return ''

    
    def IsIllegalAvatar(self, sValue):
        tValue = sValue.split('|')
        if len(tValue) < 1:
            return False
        else:
            
            try:
                sAvatarAtt = tValue[0]
                tPhotoAtt = tuple(sAvatarAtt.split(','))
                return [ long(s) for s in tPhotoAtt ]
            except:
                return False


    
    def ConvertAvatarStr2Tuple(self, sValue):
        tValue = self.IsIllegalAvatar(sValue)
        if not tValue:
            tValue = (-1, -1, -1, -1)
        
        return tValue

    
    def GetAvatar(self, iUid, sType):
        sValue = self.GetAvatarFromCache(iUid)

    
    def CacheAvatar(self, iUid, tAvatarAtt):
        sKey = str(iUid) + '-' + str(misc.GetServerID())
        iTime = int(time.time())
        sValue = str(tAvatarAtt)[1:-1].replace(' ', '') + '|' + str(iTime)
        sOldValue = self.m_dLoadResult.get(sKey, '')
        self.m_dLoadResult[sKey] = sValue
        return sOldValue != sValue

    
    def RecieveAvatar(self, dAvatar):
        lID = dAvatar.keys()
        self.ResetLastRequestState(lID)
        bSave = False
        for iUid, tAvatarAtt in dAvatar.iteritems():
            bChange = self.CacheAvatar(iUid, tAvatarAtt)
            if bChange:
                bSave = True
            
            if iUid in self.m_lLoadQueue:
                self.m_lLoadQueue.remove(iUid)
            
            lType = self.m_dID2Type.get(iUid)
            if not lType:
                continue
            
            self.m_dID2Type[iUid] = []
            for sType in lType:
                lID = self.m_dType2LoadQueue.get(sType)
                if lID and iUid in lID:
                    lID.remove(iUid)
                    continue
            
        
        if bSave:
            self.Save2Cache()
        
        self.ssEmit(self.SS_LoadAvaterFinished, dAvatar)

    
    def DoRequestAvatar(self, iUid, sType):
        self.m_lLoadQueue.append(iUid)
        if sType not in self.m_dType2LoadQueue:
            self.m_dType2LoadQueue[sType] = []
        
        lQueue = self.m_dType2LoadQueue[sType]
        if iUid not in lQueue:
            lQueue.append(iUid)
        
        if iUid not in self.m_dID2Type:
            self.m_dID2Type[iUid] = []
        
        lType = self.m_dID2Type[iUid]
        if sType not in lType:
            lType.append(sType)
        
        if not self.m_pFirstRequestTimer:
            self.m_pFirstRequestTimer = timer.Timer(0, self.DoRequestEventFirst)
        
        if not self.m_pRequestTimer:
            self.m_pRequestTimer = timer.Timer(0.1, self.DoRequestEvent, -1)
        

    
    def DoRequestEventFirst(self):
        if self.m_pFirstRequestTimer:
            self.m_pFirstRequestTimer.Release()
        
        self.DoRequestEvent()

    
    def ResetLastRequestState(self, lID):
        if not self.m_lCurLoadQueue:
            return None
        
        for nID in lID:
            if nID in self.m_lCurLoadQueue:
                nIndex = self.m_lCurLoadQueue.index(nID)
                if nIndex < self.m_nLastRequestIndex:
                    self.m_nLastRequestIndex -= 1
                
            nIndex < self.m_nLastRequestIndex
        

    
    def ReleaseRequestTimer(self):
        if self.m_pRequestTimer:
            self.m_pRequestTimer.Release()
        
        self.m_pRequestTimer = None

    
    def DoRequestEvent(self):
        if not self.m_lLoadQueue:
            self.m_lLastRequestQueue = None
            self.ReleaseRequestTimer()
            return None
        
        if self.m_sTypeFirst:
            if self.m_sCurLoadType == self.m_sTypeFirst:
                if not (self.m_lCurLoadQueue) or self.m_nLastRequestIndex >= len(self.m_lCurLoadQueue):
                    self.m_sCurLoadType = ''
                    self.m_lCurLoadQueue = self.m_lLoadQueue
                    self.m_nLastRequestIndex = 0
                
            else:
                lQueue = self.m_dType2LoadQueue.get(self.m_sTypeFirst)
                if lQueue:
                    self.m_sCurLoadType = self.m_sTypeFirst
                    self.m_lCurLoadQueue = lQueue
                    self.m_nLastRequestIndex = 0
                
        
        nLen = len(self.m_lCurLoadQueue)
        nStart = self.m_nLastRequestIndex
        nEnd = min(self.m_nLastRequestIndex + E_MAX_REQUESTAVATAT, nLen)
        if nEnd > nLen:
            self.m_nLastRequestIndex = 0
        else:
            self.m_nLastRequestIndex = nEnd
        lRequest = self.m_lCurLoadQueue[nStart:nEnd]
        if len(lRequest) < E_MAX_REQUESTAVATAT:
            if self.m_sCurLoadType and self.m_lLoadQueue:
                self.m_lCurLoadQueue = self.m_lLoadQueue
                self.m_sCurLoadType = ''
                self.m_nLastRequestIndex = 0
                nLeft = E_MAX_REQUESTAVATAT - len(lRequest)
                for i, iID in enumerate(self.m_lCurLoadQueue):
                    if iID not in lRequest:
                        nLeft -= 1
                        lRequest.append(iID)
                    
                    if nLeft <= 0:
                        self.m_nLastRequestIndex = i + 1
                        break
                        continue
                
                if self.m_nLastRequestIndex == len(self.m_lCurLoadQueue):
                    self.m_nLastRequestIndex = 0
                
            
        
        if not lRequest:
            self.m_lLastRequestQueue = None
            return None
        
        lOldQueue = self.m_lLastRequestQueue
        self.m_lLastRequestQueue = lRequest
        C2SGetAvatar(lRequest)
        if lOldQueue == lRequest:
            for nID in lOldQueue:
                if nID in self.m_lLoadQueue:
                    self.m_lLoadQueue.remove(nID)
                
                if nID in self.m_lCurLoadQueue:
                    self.m_lCurLoadQueue.remove(nID)
                    continue
            
        

    
    def InitSignal(self):
        self.ssInit()
        self.ssCreate(self.SS_LoadAvaterFinished)

    
    def ReleaseSignal(self):
        self.ssReleaseSignal(self.SS_LoadAvaterFinished)
