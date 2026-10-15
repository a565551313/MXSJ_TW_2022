# pycdc 交叉复核产物 · script.fls entry 3873
# co_filename(原始)='script/debug/warrecordupload.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3873.pyc (Python 2.5)

RECORD_PATH = [
    'record',
    'log/war']
TEMP_RECORD = 'log/game/other%s-%s.mwr'
MAX_SIZE = 2 * 1000000
g_RecordUploadMgr = None

def UploadRecord(iMonth, iDay):
    '''
\t\xa4W\xb6\xc7\xbf\xfd\xb9\xb3
\t'''
    GetRecordUploadMgr().UploadRecords(iMonth, iDay)


class CRecordUploadMgr(object):
    
    def UploadRecords(self, iMonth, iDay):
        import misc
        import gamebackground
        tDataList = self.GetRecordsByDate(iMonth, iDay)
        sUploadList = self.CreateUploadFiles(tDataList)
        if sUploadList:
            gamebackground.GetMultiFileUploadMgrNew().CreateUploadTask(2, 'WarRecord%s_%s' % (iMonth, iDay), sUploadList, misc.Functor(self.OnFinishCB))
        

    
    def OnFinishCB(self, sSucList, sFailList, sTotalList):
        import netopenui
        import hero
        iSuc = len(sSucList)
        iFail = len(sFailList)
        iLeft = len(sTotalList) - iSuc - iFail
        sStr = '%s type:\xbf\xfd\xb9\xb3\xa4W\xb6\xc7 ' % hero.GetRealID()
        if iSuc:
            sStr += '\xa6\xa8\xa5\\%d\xad\xd3\xa1A' % iSuc
        
        if iFail:
            sStr += '\xa5\xa2\xb1\xd1%d\xad\xd3\xa1A' % iFail
        
        if iLeft:
            sStr += '\xb6W\xae\xc9%d\xad\xd3\xa1A' % iLeft
        
        netopenui.C2SUploadFinishInfo(sStr)

    
    def GetRecordsByDate(self, iMonth, iDay):
        import os
        tRltList = []
        for sDir in RECORD_PATH:
            if not os.path.exists(sDir):
                \xa5\xa6G('\xbf\xfd\xb9\xb3\xa6s\xa9\xf1\xb8\xf4\xae|\xa4\xa3\xa6s\xa6b', sDir)
                continue
            
            for sFile in os.listdir(sDir):
                dInfo = GetRecordInfo(os.path.join(sDir, sFile))
                if not dInfo:
                    continue
                
                sPath = '%s/%s' % (sDir, sFile)
                if iMonth == 0 and iDay == 0:
                    tRltList.append((sPath, dInfo))
                    continue
                if dInfo['sDate'] == '%02d%02d' % (iMonth, iDay):
                    tRltList.append((sPath, dInfo))
                    continue
            
        
        return tRltList

    
    def CreateUploadFiles(self, tPathList):
        iBeginTime = 0
        iEndTime = 0
        iTotalSize = 0
        sDumpList = []
        sUploadList = []
        for sPath, dInfo in tPathList:
            if iBeginTime == 0:
                iBeginTime = dInfo['sTime']
            
            if iTotalSize + dInfo['iSize'] > MAX_SIZE:
                sName = TEMP_RECORD % (iBeginTime, iEndTime)
                DumpRecordFile(sDumpList, sName)
                sUploadList.append(sName)
                iTotalSize = 0
                sDumpList = []
                iBeginTime = dInfo['sTime']
                continue
            iTotalSize += dInfo['iSize']
            iEndTime = dInfo['sTime']
            sDumpList.append(sPath)
        
        if sDumpList:
            sName = TEMP_RECORD % (iBeginTime, iEndTime)
            DumpRecordFile(sDumpList, sName)
            sUploadList.append(sName)
        
        return sUploadList



def GetRecordUploadMgr():
    global g_RecordUploadMgr
    if not g_RecordUploadMgr:
        g_RecordUploadMgr = CRecordUploadMgr()
    
    return g_RecordUploadMgr


def GetRecordInfo(sFileName):
    '''
\t\xb3q\xb9L\xbf\xfd\xb9\xb3\xa6W\xba\xd9\xc0\xf2\xa8\xfa\xabH\xae\xa7
\t'''
    import os
    import time
    if not sFileName.endswith('.mwr') or sFileName.endswith('.mxdat'):
        return None
    
    dInfo = { }
    
    try:
        import stat
        st = os.stat(sFileName)
        dInfo['iSize'] = st.st_size
        fTime = os.path.getmtime(sFileName)
        oTime = time.localtime(fTime)
        dInfo['sDate'] = '%02d%02d' % (oTime.tm_mon, oTime.tm_mday)
        dInfo['sTime'] = '%02d%02d' % (oTime.tm_hour, oTime.tm_min)
    except Exception:
        e = None
        \xa5\xa6G('\xc0\xf2\xa8\xfa\xbf\xfd\xb9\xb3\xabH\xae\xa7', str(e))
        return None

    return dInfo


def DumpRecordFile(sFileLst, sTotalFile):
    import misc
    import os
    sNameContentSplit = '=asdfdsssc2355'
    sFileSplit = 'sdhhhhahahaha12v5233'
    oTotalFile = misc.OpenFile(sTotalFile, 'wb')
    for sFileName in None:
        oFile = misc.OpenFile(sFileName, 'rb')
        sContent = oFile.read()
        oFile.close()
        sContent = '%s%s%s%s' % (os.path.basename(sFileName), sNameContentSplit, sContent, sFileSplit)
        oTotalFile.write(sContent)
    
    oTotalFile.close()
