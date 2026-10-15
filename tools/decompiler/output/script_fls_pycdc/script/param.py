# pycdc 交叉复核产物 · script.fls entry 1904
# co_filename(原始)='script/param.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1904.pyc (Python 2.5)

import os
import C_sys
g_DelayRunTimer = None
g_ExcelMgr = None

def ModuleReset():
    global g_DelayRunTimer
    g_DelayRunTimer = None


def RunAferStartParam(p):
    global g_DelayRunTimer
    sInfoList = p.split(' ')
    p = sInfoList[0]
    if p in CMD2CALLNOW:
        CMD2CALLNOW[p](*sInfoList[1:])
        return None
    
    for cmdName in FIRSTCALLNAME:
        if p.startswith(cmdName):
            CmdParam(p)
            return None
            continue
    
    
    def done(obj):
        CmdParam(p)

    if g_DelayRunTimer:
        g_DelayRunTimer.Release()
    
    import interface
    g_DelayRunTimer = interface.CBaseObject(None)
    g_DelayRunTimer.CreatePyCommand(1, done)


def CmdParam(p):
    import usermacro
    cmdDataList = p.strip().split(',')
    for cmdData in cmdDataList:
        cmdargs = cmdData.strip().split(':')
        if not len(cmdargs):
            continue
        
        if not CMD2CALL.get(cmdargs[0]):
            print 'CmdParam\xb0\xd1\xbc\xc6\xae\xe6\xa6\xa1\xa6\xb3\xbb~!%s' % cmdData
            return None
        
        cmd = CMD2CALL.get(cmdargs[0])
        args = cmdargs[1:]
        
        try:
            if args:
                cmd(*args)
            else:
                cmd()
        continue
        except TypeError:
            usermacro.PROMPT_MSG('CmdParam\xb0\xd1\xbc\xc6\xae\xe6\xa6\xa1\xa6\xb3\xbb~!' + cmdData)
            return None
            continue

        None<EXCEPTION MATCH>TypeError
    


def AutoSuperPfm(*args):
    import main
    import war
    import testwar
    import loginin
    import gamectrl
    loginin.Show(False)
    war.SetReplayWar(True)
    main.SetWarLoop()
    text = ','.join(args)
    
    gamectrl.IsShowMainPage = lambda : None
    testwar.TestSuperPerform(text.split(';'))


def AutoNewMagic(*args):
    import main
    import war
    import testwar
    import loginin
    import gamectrl
    import innerversion
    if not innerversion.IsInnerVer():
        return None
    
    import testnewmagic
    if len(args) > 0 and args[0] == 'createspr':
        testnewmagic.Igs2Spr()
        return None
    
    loginin.Show(False)
    war.SetReplayWar(True)
    
    gamectrl.IsShowMainPage = lambda : None
    main.SetWarLoop()
    testwar.TestNewMagic()


def ShowDlgMgr():
    import buildstyle
    buildstyle.ShowDlgMgrPanel()


def AutoLogin(*args):
    import misc
    if misc.IsTWServer():
        import twautologin
        (sServer, sAccount, sPwd) = args[:3]
        twautologin.AutoLogin(sAccount, sPwd, sServer)
        return None
    
    
    try:
        if len(args) == 5:
            (areaname, servername, account, pwd, pid) = args
        else:
            (areaname, servername, account, pwd) = args
            pid = account[1:]
    except:
        print '\xb0\xd1\xbc\xc6\xbf\xf9\xbb~', args
        return None

    if not account.startswith('#'):
        print '\xabD\xaak\xbd\xe3\xb8\xb9'
        return None
    
    
    def AutoLogin(obj, dummy, areaname, servername, account, pwd, pid, step):
        if step == 0:
            import loginin
            loginin.AutoLogin(account, pwd, areaname, servername)
        
        import selectrole
        if selectrole.GetShow():
            import netlogin
            netlogin.C2SLoginPlayerEnter(pid)
            return None
        
        return (dummy, areaname, servername, account, pwd, int(pid), step + 1)

    import interface
    timer = interface.CBaseObject(None)
    timer.CreatePyCommand(10, AutoLogin, timer, areaname, servername, account, pwd, pid, 0)


def EPTest(*args):
    AutoLogin(*args)
    import eprotecttest
    eprotecttest.SetEPTest()


def GMTools(*args):
    import gmtools
    gmtools.GMLoginAndDoSomething(*args)


def ChangeExist():
    
    def Exist(sPath, sPck):
        import os
        if os.path.exists('%s/%s' % (sPck, sPath)):
            return True
        else:
            return C_sys.Exist(sPath, sPck)

    import charpath
    charpath.Exist = Exist


def LoadRes(*args):
    import C_sound
    import sound
    import gamectrl
    import permission
    C_sys.SetCaption('\xb9\xda\xb7Q\xa5@\xac\xc9\xb8\xea\xb7\xbd\xa5[\xb3t\xbe\xb9')
    C_sound.SetMusicVolume(0, 1)
    C_sound.SetSampleVolume(0)
    if permission.IsOpenNewSoundBnk():
        import newsoundinterface
        newsoundinterface.SetMusicVolume(0)
        newsoundinterface.SetSampleVolume(0)
    
    sound.SetPlayMusic(False)
    sound.SetPlaySample(False)
    gamectrl.SetShowMainPage(None)


def RecordVideo(*args):
    
    try:
        arg = ':'.join(args)
        (hWnd, fileName, beginBout, endBout, step, isPlayMusic) = arg.split(';')
    except:
        print '\xb0\xd1\xbc\xc6\xbf\xf9\xbb~', args
        import main
        main.CloseGame()
        return None

    import recordvideo
    recordvideo.CRecordVideo.SetInfo(fileName, int(beginBout), int(endBout), int(hWnd), int(step), int(isPlayMusic))


def ReplayVideo(sFileName):
    print ('play video %', sFileName)
    import recordvideo
    recordvideo.CRecordVideo.Replay(sFileName)


def QuickReplayVideo(sFileName):
    print ('play video %', sFileName)
    import recordvideo
    recordvideo.CRecordVideo.SetInfo(sFileName, int(0), int(30), int(0), int(1), int(0))


def FilterVideo(sPath, iMiniTurn = -1, iMaxTurn = -1, iSpecialCnt = -1):
    import recordvideo
    recordvideo.StartFliter(sPath, int(iMiniTurn), int(iMaxTurn), int(iSpecialCnt))


def AutoReplay(sPathDir, iCount = 4, sQuick = 'False'):
    print ('AutoReplay ---->%s' % sPathDir, sQuick)
    lstFileNames = []
    Listdir(sPathDir, lstFileNames)
    lstFileNames.sort()
    print lstFileNames
    import recordvideo
    recordvideo.CRecordVideo.AutoReplay(lstFileNames, iCount, sQuick)


def Listdir(path, lstFileName):
    for sFile in os.listdir(path):
        file_path = os.path.join(path, sFile)
        if os.path.isdir(file_path):
            Listdir(file_path, lstFileName)
            continue
        if os.path.splitext(file_path)[1] == '.mwr':
            lstFileName.append(file_path)
            continue
    

CMD2CALL = {
    'dlgmgr': ShowDlgMgr,
    'super_pfm': AutoSuperPfm,
    'AutoLogin': AutoLogin,
    'RecordVideo': RecordVideo,
    'testnewmagic': AutoNewMagic,
    'gmtools': GMTools,
    'changeexist': ChangeExist,
    'EPTest': EPTest }
FIRSTCALLNAME = ('RecordVideo',)

def DoTest(sType = None):
    import gamectrl
    import testcode
    import main
    gamectrl.SetShowMainPage(None)
    
    main.SetRate = lambda : None
    testcode.DoTest(sType = sType)


class CExcelMgr(object):
    
    def Init(cls, sExcelPath):
        global g_ExcelMgr
        if not g_ExcelMgr:
            g_ExcelMgr = CExcelMgr(sExcelPath)
        

    Init = classmethod(Init)
    
    def Get(cls):
        return g_ExcelMgr

    Get = classmethod(Get)
    
    def __init__(self, sExcelPath):
        self.m_ExcelPath = sExcelPath
        self.m_DataPath = sExcelPath + '/data'
        self.ImportOldExcel()
        self.AddInitToNewExcel()
        self.ReplaceOld()
        self.Clear()

    
    def ImportOldExcel(self):
        import sys
        sys.path.append(self.m_ExcelPath)
        for sRoot, sDirList, sFileList in os.walk(self.m_DataPath):
            if '\\.svn' in sRoot:
                continue
            
            for sFile in sFileList:
                if not sFile.endswith('.py') or sFile == '__init__.py':
                    continue
                
                __import__(sFile[:-3])
            
        

    
    def AddInitToNewExcel(self):
        for sRoot, sDirList, sFileList in os.walk(self.m_DataPath):
            sName = '__init__.py'
            if '\\.svn' in sRoot:
                continue
            
            if sName not in sFileList:
                sPath = os.path.join(sRoot, sName)
                oFile = open(sPath, 'w')
                oFile.close()
                continue
        

    
    def GetModule(self, sPath):
        import sys
        sPath = sPath[len(self.m_ExcelPath) + 1:]
        sPath = sPath.replace('/', '.')
        sPath = sPath.replace('\\', '.')
        __import__(sPath)
        return sys.modules[sPath]

    
    def ReplaceOld(self):
        import sys
        for sRoot, sDirList, sFileList in os.walk(self.m_DataPath):
            if '\\.svn' in sRoot:
                continue
            
            for sFile in sFileList:
                if not sFile.endswith('.py') or sFile == '__init__.py':
                    continue
                
                sPath = os.path.join(sRoot, sFile[:-3])
                oModule = self.GetModule(sPath)
                sys.modules[sFile[:-3]] = oModule
            
        

    
    def Clear(self):
        import sys
        import resetcontrol
        sDataList = [
            'param']
        for sRoot, sDirList, sFileList in os.walk(self.m_DataPath):
            if '\\.svn' in sRoot:
                continue
            
            sPack = sRoot[len(self.m_ExcelPath) + 1:]
            sPack = sPack.replace('/', '.')
            sPack = sPack.replace('\\', '.')
            if sPack not in sDataList:
                sDataList.append(sPack)
            
            for sFile in sFileList:
                if not sFile.endswith('.py') or sFile == '__init__.py':
                    continue
                
                sPath = os.path.join(sRoot, sFile[:-3])
                sPath = sPath[len(self.m_ExcelPath) + 1:]
                sPath = sPath.replace('/', '.')
                sPath = sPath.replace('\\', '.')
                sDataList.append(sPath)
                sDataList.append(sFile[:-3])
            
        
        for k in sys.modules.keys():
            if k not in sys.builtin_module_names and k not in resetcontrol.IGNORE_MODULE and k not in sDataList:
                m = sys.modules[k]
                for attr in dir(m):
                    if attr in sDataList:
                        print '>attr>', k, attr
                        continue
                
        
        print '\xa4W\xad\xb1\xaa\xba\xbc\xd2\xb6\xf4\xa4w\xb8g\xb3Q\xaa\xec\xa9l\xa4\xc6\xa4F\xa1A\xbc\xf6\xa7\xf3\xb7|\xa5\xa2\xae\xc4'

    
    def Reload(self):
        import netquicklogin
        for sRoot, sDirList, sFileList in os.walk(self.m_DataPath):
            if '\\.svn' in sRoot:
                continue
            
            for sFile in sFileList:
                if not sFile.endswith('.py') or sFile == '__init__.py':
                    continue
                
                oModule = __import__(sFile[:-3])
                reload(oModule)
            
        
        netquicklogin.Connect(False, '\xad\xab\xb7s\xb8\xfc\xa4J')



def TestWalker():
    import innerversion
    if not innerversion.IsInnerVer():
        return None
    
    
    def Set(*args):
        return False

    import versions
    versions.g_EngineVersion = (1, 0, 0)
    versions.IsNewEngine = Set

PJ = os.path.join
sMsg = ''
sLog = ''

def Check(sIgsPath, sSprPath, sCvrPath, sPck, iConDataCount = 0):
    global sMsg, sLog, sLog, sLog, sLog, sLog, sLog, sLog, sLog
    import C_sys
    import C_object
    import misc
    iIgsdata = C_sys.LoadFile(sIgsPath, sPck)
    if iIgsdata:
        
        try:
            oImg = C_object.CImagesObject(None, sIgsPath, sPck)
            iDir = oImg.DirectionAmount()
            iFrame = oImg.FrameAmount()
            sMsg += '%s\t%s\t%s\t%s\n' % (sPck, sIgsPath, iFrame, iDir)
            sSprdata = C_sys.LoadFile(sSprPath, sPck)
            if not sSprdata:
                sLog += 'Spr\xa4\xa3\xa6s\xa6b, sPck-%s, sIgsPath-%s\n' % (sPck, sIgsPath)
            else:
                data = misc.FindSection(sSprdata, 'frames')[1:]
                frameAmount = len(data)
                if iFrame != frameAmount:
                    sLog += 'Spr\xb4V\xbc\xc6\xa4\xa3\xa4\xc7\xb0t, sPck-%s, sIgsPath-%s, iFrame-%s, frameAmount-%s\n' % (sPck, sIgsPath, iFrame, frameAmount)
                
            sCvrdata = C_sys.LoadFile(sCvrPath, sPck)
            if not sCvrdata:
                sLog += 'Cvr\xa4\xa3\xa6s\xa6b,%s,%s\n' % (sPck, sIgsPath)
            elif 'ver2' not in sCvrdata:
                return None
            else:
                sAAList = sCvrdata.split('\n')
                if len(sAAList) < 3:
                    sLog += 'Cvr\xbf\xf9\xbb~, sPck-%s, sIgsPath-%s\n' % (sPck, sIgsPath)
                    return None
                
                iCount = 0
                bC = False
                for i in range(len(sAAList[2:])):
                    sl = sAAList[i + 2].split()
                    if not sl:
                        continue
                    
                    iCount += 1
                    sl = [ int(x) for x in sl ]
                    if len(sl) != len(set(sl)):
                        bC = True
                        continue
                    []
                
                if iCount != iDir * iFrame:
                    sLog += 'Cvr\xa4\xe8\xa6V\xb4V\xbc\xc6\xbf\xf9\xbb~, sPck-%s, sIgsPath-%s, iCount-%s, iDir * iFrame-%s, iDir-%s, iFrame-%s\n' % (sPck, sIgsPath, iCount, iDir * iFrame, iDir, iFrame)
        sLog += '\xb3B\xb2z\xb2\xa7\xb1`, sPck-%s, sIgsPath-%s\n' % (sPck, sIgsPath)

    


def CheckFile(sSourcePath, sPath, sList, iConDataCount = 0):
    sSearchPath = './%s/%s' % (sPath, sSourcePath)
    for path, dirlist, filelist in os.walk(sSearchPath):
        if 'shadow' in path:
            continue
        
        for file in filelist:
            if file.endswith('.igs'):
                sFile = file[:-4]
                if sFile in sList:
                    sDirPath = path[path.index(sSourcePath):].replace('\\', '/')
                    sIgsPath = '%s/%s.igs' % (sDirPath, sFile)
                    sSprPath = '%s/%s.spr' % (sSourcePath, sFile)
                    sCvrPath = '%s/%s.cvr' % (sSourcePath, sFile)
                    Check(sIgsPath, sSprPath, sCvrPath, sPath, iConDataCount)
                
            sFile in sList
        
    


def CheckCvrSpr():
    import charpartdata
    import chardefine
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xb6}\xa9l\xc0\xcb\xacd\xa5l\xb3\xea\xc3~>>>>>>>>>>>>>>>>>>>>'
    sPath = 'newchar'
    sList = [
        'stand',
        'walk',
        'attack',
        'magic',
        'hit',
        'guard',
        'die',
        'defend']
    iList = range(2001, 8088)
    for i in iList:
        if i not in charpartdata.GetNpcData():
            continue
        
        iConDataCount = len(charpartdata.GetNpcComponent(i))
        iAss = charpartdata.GetNpcAccessories(i)
        if iAss:
            for iAssE in iAss:
                if type(iAssE) == tuple:
                    iConDataCount += len(iAssE)
                    continue
                iConDataCount += 1
            
        
        sSourcePath = '%.4d' % i
        CheckFile(sSourcePath, sPath, sList, iConDataCount)
    
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xc0\xcb\xacd\xa5l\xb3\xea\xc3~\xa7\xb9\xb2\xa6>>>>>>>>>>>>>>>>>>>>'
    C_sys.CacheRelease()
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xb6}\xa9l\xc0\xcb\xacd\xa4H\xaa\xab>>>>>>>>>>>>>>>>>>>>'
    sPath = 'hero'
    sList = [
        'stand',
        'walk',
        'attack',
        'magic',
        'hit',
        'guard',
        'die',
        'defend',
        'attacka',
        'attackb',
        'attackc',
        'attackd',
        'attacke',
        'attackf',
        'attackg',
        'clap',
        'cry',
        'dance',
        'love',
        'laugh',
        'sit',
        'angry']
    for i in chardefine.HERO_SHAPE_LIST:
        for iii in range(7):
            sSourcePath = '%.4d/body/%.2d' % (i, iii)
            CheckFile(sSourcePath, sPath, sList)
        
    
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xb6}\xa9l\xc0\xcb\xacd\xae\xc9\xb8\xcb>>>>>>>>>>>>>>>>>>>>'
    for i in (100, 200):
        for iii in range(7):
            sSourcePath = 'fashion/01/%.4d/%.2d' % (i, iii)
            CheckFile(sSourcePath, sPath, sList)
        
        for iii in ('horse1', 'horse2'):
            sSourcePath = 'fashion/01/%.4d/%s' % (i, iii)
            CheckFile(sSourcePath, sPath, sList)
        
    
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xc0\xcb\xacd\xa4H\xaa\xab\xa7\xb9\xb2\xa6>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xb6}\xa9l\xc0\xcb\xacd\xaf\xcd\xbbH>>>>>>>>>>>>>>>>>>>>'
    sPath = 'hero'
    sList = [
        'stand',
        'walk',
        'guard',
        'die']
    iList = range(1, 20)
    for i in iList:
        sSourcePath = 'wing/%.3d' % i
        CheckFile(sSourcePath, sPath, sList)
    
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>)"E\x8dF$R\xa1N\xb9\xb2\xa6>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xb6}\xa9l\xc0\xcb\xacd\xa7\xa4\xc3M>>>>>>>>>>>>>>>>>>>>'
    sPath = 'hero'
    sList = [
        'stand',
        'walk']
    iList = range(1, 27)
    for i in iList:
        sSourcePath = 'horse/%.3d' % i
        CheckFile(sSourcePath, sPath, sList)
    
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>\xc0\xcb\xacd\xa7\xa4\xc3M\xa7\xb9\xb2\xa6>>>>>>>>>>>>>>>>>>>>'
    fd = open('igs\xabH\xae\xa7.txt', 'w+')
    fd.write(sMsg)
    fd.close()
    fd = open('\xbf\xf9\xbb~\xabH\xae\xa7.txt', 'w+')
    fd.write(sLog)
    fd.close()


def FindNullIgs():
    import gamerestools
    gamerestools.FindNullIgs()


def AutoDelFrame(sSprPath, sCvrPath, sSpr):
    import C_object
    obj = C_object.CWalkerObject(None)
    
    obj.CSetDirection = lambda *vArgs: None
    obj.Load(sSpr, 'hero')
    obj.CreateCommand(0, 'animation')
    frames = obj.DirectionAmount()
    fspr = open(sSprPath, 'r')
    vspr = fspr.readlines()
    fspr.close()
    fspr = open(sSprPath, 'w')
    vspr_w = vspr[:1 + (len(vspr) - 1) / 2]
    vspr_w = [ s.replace(' 2', ' 4') for s in vspr_w ]
    vspr_w = [ s.replace(' 3', ' 4') for s in vspr_w ]
    fspr.write(''.join(vspr_w))
    fspr.close()
    fcvr = open(sCvrPath, 'r')
    vcvr = fcvr.readlines()
    fcvr.close()
    fcvr = open(sCvrPath, 'w')
    count = len(vcvr)
    vcvr_w = _[3]
    fcvr.write(''.join(vcvr_w))
    fcvr.close()


def AutoDelBodyFrame(sRoot):
    iLen = len(sRoot)
    for i in xrange(111, 1000):
        sPath = os.path.join(sRoot, '%04d' % i)
        if os.path.exists(sPath):
            sBodyPath = os.path.join(sPath, 'body')
            vFilePath = os.listdir(sBodyPath)
            for sName in vFilePath:
                sFolderPath = os.path.join(sBodyPath, sName)
                if os.path.isdir(sFolderPath):
                    vFile = os.listdir(sFolderPath)
                    if 'stand.spr' in vFile and 'stand.cvr' in vFile:
                        sSpr = os.path.join(sFolderPath, 'stand.spr')
                        sCvr = os.path.join(sFolderPath, 'stand.cvr')
                        AutoDelFrame(sSpr, sCvr, sSpr[iLen + 1:])
                    
                'stand.cvr' in vFile
            
    


def AutoDelHorseFrame(sRoot):
    iLen = len(sRoot)
    for i in xrange(111, 1000):
        sPath = os.path.join(sRoot, '%04d' % i)
        if os.path.exists(sPath):
            vHorseList = os.listdir(sPath)
            for sHorseName in vHorseList:
                if not sHorseName.startswith('horse'):
                    continue
                
                sFolderPath = os.path.join(sPath, sHorseName)
                if os.path.isdir(sFolderPath):
                    vFile = os.listdir(sFolderPath)
                    if 'stand.spr' in vFile and 'stand.cvr' in vFile:
                        sSpr = os.path.join(sFolderPath, 'stand.spr')
                        sCvr = os.path.join(sFolderPath, 'stand.cvr')
                        AutoDelFrame(sSpr, sCvr, sSpr[iLen + 1:])
                    
                'stand.cvr' in vFile
            
    
    sPath = os.path.join(sRoot, 'horse')
    if os.path.exists(sPath):
        vHorseList = os.listdir(sPath)
        for sHorseName in vHorseList:
            sFolderPath = os.path.join(sPath, sHorseName)
            if os.path.isdir(sFolderPath):
                vFile = os.listdir(sFolderPath)
                if 'stand.spr' in vFile and 'stand.cvr' in vFile:
                    sSpr = os.path.join(sFolderPath, 'stand.spr')
                    sCvr = os.path.join(sFolderPath, 'stand.cvr')
                    AutoDelFrame(sSpr, sCvr, sSpr[iLen + 1:])
                
            'stand.cvr' in vFile
        
    


def AutoDelWingCvr(sRoot):
    iLen = len(sRoot)
    sPath = os.path.join(sRoot, 'wing')
    if os.path.exists(sPath):
        vWingList = os.listdir(sPath)
        for sWingName in vWingList:
            sFolderPath = os.path.join(sPath, sWingName)
            if os.path.isdir(sFolderPath):
                vFile = os.listdir(sFolderPath)
                if 'stand.spr' in vFile and 'stand.cvr' in vFile:
                    sSpr = os.path.join(sFolderPath, 'stand.spr')
                    sCvr = os.path.join(sFolderPath, 'stand.cvr')
                    AutoDelFrame(sSpr, None, sSpr[iLen + 1:])
                    os.remove(sCvr)
                
            'stand.cvr' in vFile
        
    


def AutoDelHeroFrame(*args):
    print '\n\n\n\n\n\n\n\n\n\n'
    sRoot = os.path.join(os.getcwd(), 'hero')
    dType2Func = {
        'body': AutoDelBodyFrame,
        'horse': AutoDelHorseFrame,
        'wing': AutoDelWingCvr }
    for sType in args:
        if sType in dType2Func:
            dType2Func[sType](sRoot)
            continue
    
    print '\n\n\n\n\n\n\n\n\n\n'


def AutoDetectIgsPal(*args):
    print '\n\n\n\n\n\n\n\n\n\n'
    print '====\xafu\xb1m\xa6\xe2igs\xa4\xce\xacV\xa6\xe2\xb1\xa1\xaap\xc0\xcb\xb4\xfa\xb6}\xa9l====\n'
    AUTO_DETECT_IGS_PAL_ROOT = os.getcwd()
    iLen = len(AUTO_DETECT_IGS_PAL_ROOT)
    OPJ = os.path.join
    oSprFilePathList = []
    oIgsFilePathList = []
    dResult = { }
    for sRoot, oDirList, oFileList in os.walk(AUTO_DETECT_IGS_PAL_ROOT):
        for sFileName in oFileList:
            if sFileName.endswith('.spr'):
                oSprFilePathList.append((sRoot, sFileName))
            
            if sFileName.endswith('.igs'):
                oIgsFilePathList.append((sRoot, sFileName))
                continue
        
    
    for sRoot, sFileName in oSprFilePathList:
        sSprFullPath = OPJ(sRoot, sFileName)
        fSpr = open(sSprFullPath, 'r')
        sIgs = ''
        bFindPalPro = False
        oSprLines = fSpr.readlines()
        fSpr.close()
        for sLine in oSprLines:
            sLine = sLine.strip()
            if sLine.endswith('.igs'):
                sIgs = sLine.split('=')[-1]
            
            if not bFindPalPro:
                pass
            bFindPalPro = sLine.find('PalPro') != -1
            if bFindPalPro and sIgs:
                break
                continue
        
        if sIgs and bFindPalPro:
            oIgsPathList = []
            sIgsPath = OPJ(sRoot, sIgs)
            while os.path.exists(sIgsPath):
                fIgs = open(sIgsPath)
                sIgsFirstLine = fIgs.readline()
                sIgsStart = sIgsFirstLine[:2]
                if sIgsStart == 'IG':
                    oIgsLines = fIgs.readlines()
                    fIgs.close()
                    sFolderName = oIgsLines[0].strip()
                    sPathName = oIgsLines[1].strip()
                    oIgsPathList.append((sIgsPath[iLen + 1:], False))
                    sIgsPath = OPJ(OPJ(AUTO_DETECT_IGS_PAL_ROOT, sFolderName), sPathName)
                elif sIgsStart in ('T4', 'T5', 'T6', 'T7'):
                    oIgsPathList.append((sIgsPath[iLen + 1:], True))
                    fIgs.close()
                    print '\xafu\xb1m\xa6\xe2\xb9\xcf\xa4\xf9:', sIgsPath
                    break
                else:
                    break
                sIgsStart == 'IG'
                break
                continue
                if oIgsPathList and oIgsPathList[-1][-1]:
                    if len(oIgsPathList) > 1:
                        oIgsList = [ v[0] for v in oIgsPathList ]
                        dResult[sSprFullPath[iLen + 1:]] = ' -> '.join(oIgsList)
                    else:
                        dResult[sSprFullPath[iLen + 1:]] = oIgsPathList[0][0]
                
                oIgsPathList[-1][-1]
            for sSpr, sIgs in dResult.iteritems():
                print '\xafu\xb1m\xa6\xe2\xb9\xcf\xa4\xf9\xacV\xa6\xe2:', sSpr, ' ', sIgs
            
    print '\n\n\n\n\n\n\n\n\n\n'
    dResult = []
    for sRoot, sIgsPath in oIgsFilePathList:
        sIgsPath = OPJ(sRoot, sIgsPath)
        oIgsPathList = []
        while os.path.exists(sIgsPath):
            fIgs = open(sIgsPath)
            sIgsFirstLine = fIgs.readline()
            sIgsStart = sIgsFirstLine[:2]
            if sIgsStart == 'IG':
                oIgsLines = fIgs.readlines()
                fIgs.close()
                sFolderName = oIgsLines[0].strip()
                sPathName = oIgsLines[1].strip()
                oIgsPathList.append((sIgsPath[iLen + 1:], False))
                sIgsPath = OPJ(OPJ(AUTO_DETECT_IGS_PAL_ROOT, sFolderName), sPathName)
            elif sIgsStart in ('T4', 'T5', 'T6', 'T7'):
                oIgsPathList.append((sIgsPath[iLen + 1:], True))
                fIgs.close()
                print '\xafu\xb1m\xa6\xe2\xb9\xcf\xa4\xf9:', sIgsPath
                break
            else:
                break
            sIgsStart == 'IG'
            break
            continue
            if oIgsPathList and oIgsPathList[-1][-1]:
                if len(oIgsPathList) > 1:
                    oIgsList = [ v[0] for v in oIgsPathList ]
                    dResult.extend(oIgsList)
                else:
                    dResult.append(oIgsPathList[0][0])
        len(oIgsPathList) > 1
    
    for sIgs in dResult:
        print '\xafu\xb1m\xa6\xe2\xb9\xcf\xa4\xf9\xacV\xa6\xe2:', sIgs
    
    print '\n====\xafu\xb1m\xa6\xe2igs\xa4\xce\xacV\xa6\xe2\xb1\xa1\xaap\xc0\xcb\xb4\xfa\xb5\xb2\xa7\xf4===='
    print '\n\n\n\n\n\n\n\n\n\n'


def AutoDetectZhenCaiSeRes(*vArgs):
    if len(vArgs) != 1:
        return None
    
    AUTO_DETECT_ZHEN_CAI_SE_ROOT = vArgs[0]
    if not os.path.exists(AUTO_DETECT_ZHEN_CAI_SE_ROOT):
        return None
    
    print '\n\n\n\n\n\n\n\n\n\n'
    print '====\xafu\xb1m\xa6\xe2igs\xc0\xcb\xb4\xfa\xb6}\xa9l\xa1A\xc0\xcb\xb4\xfa\xb8\xf4\xae|:%s====\n' % AUTO_DETECT_ZHEN_CAI_SE_ROOT
    iLen = len(AUTO_DETECT_ZHEN_CAI_SE_ROOT)
    OPJ = os.path.join
    oIgsFilePathList = []
    for sRoot, oDirList, oFileList in os.walk(AUTO_DETECT_ZHEN_CAI_SE_ROOT):
        for sFileName in oFileList:
            if sFileName.endswith('.igs'):
                oIgsFilePathList.append((sRoot, sFileName))
                continue
        
    
    for sRoot, sFileName in oIgsFilePathList:
        sIgsPath = OPJ(sRoot, sFileName)
        while None:
            sPreIgsPath = sIgsPath
            if os.path.exists(sIgsPath):
                fIgs = open(sIgsPath)
                sIgsFirstLine = fIgs.readline()
                sIgsStart = sIgsFirstLine[:2]
                if sIgsStart == 'IG':
                    oIgsLines = fIgs.readlines()
                    fIgs.close()
                    sFolderName = oIgsLines[0].strip()
                    sPathName = oIgsLines[1].strip()
                    sIgsPath = OPJ(OPJ(AUTO_DETECT_ZHEN_CAI_SE_ROOT, sFolderName), sPathName)
                elif sIgsStart in ('T4', 'T5', 'T6', 'T7'):
                    fIgs.close()
                    print '\xafu\xb1m\xa6\xe2\xb9\xcf\xa4\xf9:', sIgsPath
                    break
                else:
                    break
            if sPreIgsPath != sIgsPath:
                print '%s \xb9\xef\xc0\xb3\xaa\xba\xb9\xea\xbb\xda\xb8\xea\xb7\xbd %s \xa4\xa3\xa6s\xa6b' % (sPreIgsPath, sIgsPath)
            
            break
            continue
    print '\n====\xafu\xb1m\xa6\xe2igs\xc0\xcb\xb4\xfa\xb5\xb2\xa7\xf4===='
    print '\n\n\n\n\n\n\n\n\n\n'


def ListFrameUseInfo(*args):
    '''\xb2\xce\xadp\xb9C\xc0\xb8UI\xa4\xa4\xa8\xcf\xa5\xce\xaec\xae\xe6\xb8\xea\xb7\xbd\xaa\xba\xb1\xa1\xaap\xa1A\xb2\xce\xadp\xa5X\xa8\xd3\xa4\xa7\xab\xe1\xb4\xa3\xa8\xd1\xb5\xb9\xb5\xa6\xa6E\xa1A\xb5\xa6\xa6E\xad\xd7\xa7\xef\xaec\xae\xe6\xb8\xea\xb7\xbd\xb9\xcf\xa4\xf9\xa4j\xa4p\xa1A\xa5[\xa7\xd6\xb9C\xc0\xb8\xa4\xa4\xb3\xd0\xab\xd8\xb9\xef\xb6H\xaa\xba\xb3t\xab\xd7'''
    import tabledata
    import listdata
    import scrolldata
    sCwdPath = os.getcwd()
    oDlgFilePathList = []
    dResult = { }
    for sRoot, oDirList, oFileList in os.walk(sCwdPath):
        for sFileName in oFileList:
            if sFileName.endswith('.dlg'):
                oDlgFilePathList.append((sRoot, sFileName))
                continue
        
    
    for sFolder, sFileName in oDlgFilePathList:
        sFilePath = os.path.join(sFolder, sFileName)
        f = open(sFilePath, 'r')
        oLineList = f.readlines()
        f.close()
        dResult[sFilePath] = { }
        for sLine in oLineList:
            sLine = sLine.strip()
            if not sLine:
                continue
            
            oWordList = sLine.split(' ')
            if not oWordList:
                continue
            
            if len(oWordList) < 2:
                continue
            
            sClassName = oWordList[1]
            if sClassName in ('CHFrame', 'CHPngFrame', 'CVFrame', 'CVPngFrame', 'CFrame', 'CPngNineFrame', 'CBorder', 'CMainFrame', 'CPngTable', 'CPngList', 'CVScrollBar', 'CVPngScrollBar'):
                if sClassName not in dResult[sFilePath]:
                    dResult[sFilePath][sClassName] = []
                
                if sClassName in ('CMainFrame',):
                    iType = oWordList[7]
                    dResult[sFilePath][sClassName].append((oWordList[0], 'combdialog/\xd6\xf7\xbf\xf2\xbc\xdc/%.3d/' % int(iType)))
                elif sClassName in ('CPngTable',):
                    for _t, _d in tabledata.DATA.iteritems():
                        for _style, _data in _d.iteritems():
                            if type(_data['sBgPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sBgPath']))
                            
                            if type(_data['sItEnterPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sItEnterPath']))
                            
                            if type(_data['sItSelectPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sItSelectPath']))
                            
                            if type(_data['sSplitPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sSplitPath']))
                            
                            if type(_data['sTitlePath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sTitlePath']))
                            
                            for _st, _sd in scrolldata.DATA.iteritems():
                                for _sstyle, _sdata in _sd.iteritems():
                                    dResult[sFilePath][sClassName].append((oWordList[0], _sdata['sPath']))
                                
                            
                        
                    
                elif sClassName in ('CPngList',):
                    for _t, _d in listdata.DATA.iteritems():
                        for _style, _data in _d.iteritems():
                            if type(_data['sBgPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sBgPath']))
                            
                            if type(_data['sItEnterPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sItEnterPath']))
                            
                            if type(_data['sItSelectPath']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sItSelectPath']))
                            
                            if type(_data['sSplitLine']) == str:
                                dResult[sFilePath][sClassName].append((oWordList[0], _data['sSplitLine']))
                            
                            for _st, _sd in scrolldata.DATA.iteritems():
                                for _sstyle, _sdata in _sd.iteritems():
                                    dResult[sFilePath][sClassName].append((oWordList[0], _sdata['sPath']))
                                
                            
                        
                    
                elif sClassName in ('CVScrollBar', 'CVPngScrollBar'):
                    for _st, _sd in scrolldata.DATA.iteritems():
                        for _sstyle, _sdata in _sd.iteritems():
                            dResult[sFilePath][sClassName].append((oWordList[0], _sdata['sPath']))
                        
                    
                else:
                    dResult[sFilePath][sClassName].append((oWordList[0], oWordList[4]))
            sClassName in ('CMainFrame',)
        
    
    iLen = len(sCwdPath) + 1
    oContentList = []
    oContentSet = set()
    for sFilePath, dClassData in dResult.iteritems():
        if not dClassData:
            continue
        
        oContentList.append(sFilePath[iLen:])
        for sClassName, vPathList in dClassData.iteritems():
            oContentList.append('\t' + sClassName)
            for vPathData in vPathList:
                (sObjName, sPath) = vPathData
                oContentList.append('\t\t' + sObjName + ' -> ' + sPath)
                oContentSet.add(sPath)
            
        
        oContentList.append('\n')
    
    f = open('ui_frame_use_info.txt', 'w')
    f.write('\n'.join(list(oContentSet)) + '\n\n\n\n\n' + '\n'.join(oContentList))
    f.close()


def CountLoadUITimeLoad():
    import combdialog
    sCwdPath = os.getcwd()
    sInterfacePath = os.path.join(sCwdPath, 'interface')
    iLen = len(sInterfacePath) + 1
    oDlgFilePathList = []
    dResult = { }
    for sRoot, oDirList, oFileList in os.walk(sInterfacePath):
        for sFileName in oFileList:
            if sFileName.endswith('.dlg'):
                oDlgFilePathList.append(os.path.join(sRoot, sFileName))
                continue
        
    
    oDlgFilePathList = [ s[iLen:] for s in oDlgFilePathList ]
    oFailFileList = []
    for sDlgPath in oDlgFilePathList:
        
        try:
            dTimeInfo = { }
            combdialog.LoadDialog(None, sDlgPath)
        continue
        []
        oFailFileList.append(sDlgPath)
        continue

    
    for sDlgPath in oDlgFilePathList:
        
        try:
            dTimeInfo = { }
            combdialog.LoadDialog(None, sDlgPath)
            dResult[sDlgPath] = dTimeInfo
        continue
        oFailFileList.append(sDlgPath)
        continue

    
    vTimeData = []
    fAllTime = 0
    for sDlgPath, dTimeInfo in dResult.iteritems():
        fTotalTime = 0
        vData = []
        for sUIName, fTime in dTimeInfo.iteritems():
            fTotalTime += fTime
            vData.append((sUIName, fTime))
        
        fAllTime += fTotalTime
        vData.sort(key = (lambda v: v[1]), reverse = True)
        vTimeData.append((sDlgPath, fTotalTime, vData))
    
    vTimeData.sort(key = (lambda v: v[1]), reverse = True)
    sContent = '\xa5[\xb8\xfc\xa9\xd2\xa6\xb3UI\xc1`\xa5\xce\xae\xc9: %.2f \xb2@\xac\xed\n' % fAllTime * 1000
    sContent += '\n'
    for sDlgPath, fTotalTime, vData in vTimeData:
        sContent += '%s -> %.2f \xb2@\xac\xed\n' % (sDlgPath, fTotalTime * 1000)
        for sUIName, fTime in vData:
            if fTime <= 0.001:
                continue
            
            sContent += '\t%s -> %.2f \xb2@\xac\xed\n' % (sUIName, fTime * 1000)
        
        sContent += '\n'
    
    f = open('all_dlg_load_time.txt', 'w')
    f.write(sContent)
    f.close()


def CountLoadUITimeResult():
    sFile1 = 'all_dlg_load_time_\xb7s.txt'
    sFile2 = 'all_dlg_load_time_\xc2\xc2.txt'
    dInfo1 = { }
    dInfo2 = { }
    f = open(sFile1, 'r')
    vLines1 = f.readlines()
    f.close()
    f = open(sFile2, 'r')
    vLines2 = f.readlines()
    f.close()
    for sLine in vLines1:
        if sLine.find('.dlg') != -1:
            sLine = sLine.strip()
            v = sLine.split(' -> ')
            dInfo1[v[0]] = float(v[1].split(' ')[0])
            continue
    
    for sLine in vLines2:
        if sLine.find('.dlg') != -1:
            sLine = sLine.strip()
            v = sLine.split(' -> ')
            dInfo2[v[0]] = float(v[1].split(' ')[0])
            continue
    
    sContent = ''
    vUpData = []
    vDownData = []
    vEqualData = []
    for sDlgPath, fTime2 in dInfo2.iteritems():
        if sDlgPath not in dInfo1:
            print '\xc2\xc2\xac\xc9\xad\xb1 %s \xa6b\xb7s\xac\xc9\xad\xb1\xa4\xa4\xa7\xe4\xa4\xa3\xa8\xec' % sDlgPath
            continue
        
        fTime1 = dInfo1[sDlgPath]
        if fTime2 > fTime1:
            vUpData.append((sDlgPath, fTime2 - fTime1, fTime2, fTime1))
            continue
        if fTime2 == fTime1:
            vEqualData.append((sDlgPath, 0, 0, 0))
            continue
        vDownData.append((sDlgPath, fTime1 - fTime2, fTime2, fTime1))
    
    vUpData.sort(key = (lambda v: v[1]), reverse = True)
    vDownData.sort(key = (lambda v: v[1]), reverse = True)
    for sDlgPath, fDelTime, fOldTime, fNewTime in vUpData:
        None += sContent % ('%s \xad\xec\xa8\xd3\xa5[\xb8\xfc\xae\xc9\xb6\xa1 %s \xb2@\xac\xed\xa1A\xb2{\xa6b\xa5[\xb8\xfc\xae\xc9\xb6\xa1 %s \xb2@\xac\xed\xa1A\xad\xb0\xa7C\xa4F %s \xb2@\xac\xed, \xc1Y\xb5u\xae\xc9\xb6\xa1 %.2f \xad\xbf \n', sDlgPath, fOldTime, fNewTime, fDelTime / fDelTime if fNewTime > 0.1 else fDelTime)
    
    sContent += '\n\n'
    for sDlgPath, fDelTime, fOldTime, fNewTime in vEqualData:
        sContent += '%s \xa5[\xb8\xfc\xae\xc9\xb6\xa1\xb5L\xc5\xdc\xa4\xc6\n' % (sDlgPath,)
    
    sContent += '\n\n'
    for sDlgPath, fDelTime, fOldTime, fNewTime in vDownData:
        None += sContent % ('%s \xad\xec\xa8\xd3\xa5[\xb8\xfc\xae\xc9\xb6\xa1 %s \xb2@\xac\xed\xa1A\xb2{\xa6b\xa5[\xb8\xfc\xae\xc9\xb6\xa1 %s \xb2@\xac\xed\xa1A\xbcW\xa5[\xa4F %s \xb2@\xac\xed \xbcW\xa5[\xae\xc9\xb6\xa1 %.2f \xad\xbf \n', sDlgPath, fOldTime, fNewTime, fDelTime / fDelTime if fOldTime > 0.1 else fDelTime)
    
    sContent += '\n\n'
    f = open('load_all_dlg_delta_time.txt', 'w')
    f.write(sContent)
    f.close()


def DelayCountLoadUITime(*vArgs):
    CountLoadUITimeResult()


def StartPydevd():
    import gmcommanddata
    gmcommanddata.StartPydevd()


def AutoCreateUI():
    import gamectrl
    import innerversion
    import autosimpleuiselect
    import timer
    if not innerversion.IsInnerVer():
        return None
    
    
    def Create():
        autosimpleuiselect.ShowUISelectDlg()

    gamectrl.SetShowMainPage(None)
    timer.Timer(0.5, Create)


def StartUIEditor():
    import timer
    import misc
    import interface
    if misc.GetMAC() != '90004e73cec6':
        return None
    
    import dlguieditor
    timer.Timer(0.5, dlguieditor.CreateUIEditor)
    timer.Timer(3, misc.Functor(interface.SetDefaultButton, None))


def StartQCProfile(*vArgs):
    if len(vArgs) != 2:
        LOG('QCProfile\xa9R\xa5O\xa6\xe6\xb0\xd1\xbc\xc6\xbf\xf9\xbb~')
        return None
    
    import qcprofilemgr
    qcprofilemgr.GetQCProfileManager().StartProfile(*vArgs)


def ListFrameDiffenceBetweenNewAndOldZhanHuanShou(*vArgs):
    sRootPath = os.getcwd()
    sRootPath = sRootPath.replace('\\', '/')
    if sRootPath.endswith('/'):
        sRootPath = sRootPath[:-1]
    
    sNewChar = sRootPath + '/newchar'
    sChar = sRootPath + '/char'
    dChar = { }
    dNewChar = { }
    vNewCharIds = os.listdir(sNewChar)
    vCharIds = os.listdir(sChar)
    vCharIds = _[1]
    vNewCharIds = _[2]
    vDiffA = set(vCharIds).difference(set(vNewCharIds))
    vDiffB = set(vNewCharIds).difference(set(vCharIds))
    vDiffAll = vDiffA.union(vDiffB)
    for sDir, vIdList, dInfo in [
        (sChar, vCharIds, dChar),
        (sNewChar, vNewCharIds, dNewChar)]:
        for sId in vIdList:
            dInfo[sId] = { }
            for sName in [
                'attack.spr',
                'magic.spr']:
                sFilePath = sDir + '\\' % (sId, sName)
                if not os.path.exists(sFilePath):
                    dInfo[sId][sName] = 0
                    continue
                [] if sId in vDiffAll else []
                iFrame = 0
                
                try:
                    f = open(sFilePath, 'r')
                    vLines = f.readlines()
                    f.close()
                    iStart = 0
                    for i, sLine in enumerate(vLines):
                        sLine = sLine.strip()
                        if sLine == '[frames]':
                            iStart = i
                            break
                            continue
                        []
                    
                    for sLine in vLines[iStart + 1:]:
                        sLine = sLine.strip()
                        if not sLine:
                            break
                        
                        if sLine.startswith('['):
                            break
                        
                        vNum = sLine.split(' ')
                        iFrame += int(vNum[-1])
                except Exception:
                    []
                    e = []
                    print '\xc5\xaa\xa8\xfa\xa4\xe5\xa5\xf3\xa5X\xbf\xf9', Exception, e
                except:
                    []

                dInfo[sId][sName] = iFrame
            
        
    
    sContent = 'char\xa6\xb3newchar\xa8S\xa6\xb3\xaa\xbaID:\n'
    sContent += ' '.join(vDiffA)
    sContent += '\n\n'
    sContent += 'newchar\xa6\xb3char\xa8S\xa6\xb3\xaa\xbaID:\n'
    sContent += ' '.join(vDiffB)
    sContent += '\n\n'
    sContent += '\xb4V\xbc\xc6\xaet\xb2\xa7:\n'
    for sId, dInfoChar in dChar.iteritems():
        bFlag = False
        for sName, iNum in dInfoChar.iteritems():
            if iNum != dNewChar[sId][sName]:
                if not bFlag:
                    sContent += sId
                    sContent += '\n'
                    bFlag = True
                
                sContent += 'char\t\t%s = %s\n' % (sName, iNum)
                sContent += 'newchar\t\t%s = %s\n' % (sName, dNewChar[sId][sName])
                continue
        
        if bFlag:
            sContent += '\n'
            continue
    
    sOutput = sRootPath + '/new_old_char_frame_difference.txt'
    f = open(sOutput, 'w')
    f.write(sContent)
    f.close()


def ListAllStyleUIRes():
    import os
    sExePath = os.path.normpath(os.getcwd()).replace('\\', '/')
    sUIFileRoot = os.path.normpath(os.path.join(sExePath, 'script/uifile')).replace('\\', '/')
    if not os.path.exists(sUIFileRoot):
        print '\xb8\xf4\xae|\xa4\xa3\xa6s\xa6b:', sUIFileRoot
        return None
    
    vDirList = [
        ('%s/interface/' % sExePath, 'dialog/'),
        ('%s/interface/' % sExePath, 'dialog2/'),
        ('%s/interface/' % sExePath, 'dialog3/'),
        ('%s/interface/' % sExePath, 'dialog4/'),
        ('%s/interface/' % sExePath, 'war/'),
        ('%s/interface/' % sExePath, 'war2/'),
        ('%s/interface/' % sExePath, 'war3/'),
        ('%s/interface/' % sExePath, 'war4/'),
        ('%s/interface/' % sExePath, 'war5/')]
    dStyleResult = {
        'dialog': [],
        'dialog2': [],
        'dialog3': [],
        'dialog4': [],
        'others': [] }
    setMissRes = set()
    for sDir, sDialog in vDirList:
        for sRoot, sDirList, sFileList in os.walk(sDir + sDialog):
            for sFileName in sFileList:
                if not sFileName.endswith('.dlg'):
                    continue
                
                sDlgFullPath = os.path.join(sRoot, sFileName).replace('\\', '/')
                sModulePath = sDlgFullPath[len(sDir):].replace('/', '_')[:-4].replace('.', '_')
                oModule = None
                
                try:
                    oModule = __import__(sModulePath)
                except:
                    print '\xbc\xd2\xb6\xf4 %s \xa4\xa3\xa6s\xa6b\xa1I' % sModulePath
                    continue

                UI_INFO = oModule.UI_INFO
                vAllWidget = []
                for dUIInfo in UI_INFO:
                    vAllWidget.append(dUIInfo)
                
                while vAllWidget:
                    dUIInfo = vAllWidget.pop(0)
                    if dUIInfo['lChildren']:
                        for dInfo in dUIInfo['lChildren']:
                            vAllWidget.append(dInfo)
                        
                    
                    sResPath = dUIInfo.get('sFileName', '')
                    if not sResPath:
                        continue
                    
                    sFullResPath = os.path.normpath(os.path.join(sDir, sResPath)).replace('\\', '/')
                    if not os.path.exists(sFullResPath):
                        setMissRes.add((sDlgFullPath, sFullResPath))
                    
                    vTemp = []
                    if os.path.isdir(sFullResPath):
                        _temp1 = os.listdir(sFullResPath)
                        _temp2 = []
                        for _file in _temp1:
                            _temp2.append(os.path.normpath(os.path.join(sFullResPath, _file)).replace('\\', '/'))
                        
                        while _temp2:
                            _temp = _temp2.pop()
                            if os.path.isfile(_temp):
                                vTemp.append(_temp)
                                continue
                            _temp1 = os.listdir(_temp)
                            for _file in _temp1:
                                _temp2.append(os.path.normpath(os.path.join(_temp, _file)).replace('\\', '/'))
                            
                    else:
                        vTemp.append(sFullResPath)
                    for _path in vTemp:
                        if not os.path.exists(_path):
                            setMissRes.add((sDlgFullPath, _path))
                        
                        if not _path.endswith('.png') and not _path.endswith('.igs'):
                            continue
                        
                        _path = _path[len(sDir):]
                        _path2 = sDlgFullPath[len(sDir):]
                        if _path2.startswith('dialog'):
                            iIndex = _path2.find('/')
                            _dialog = _path2[:iIndex]
                            dStyleResult[_dialog].append(_path)
                            continue
                        dStyleResult['others'].append(_path)
                    
            
        
    
    dDialog2FileName = {
        'dialog': 'ui_res_style1.py',
        'dialog2': 'ui_res_style2.py',
        'dialog3': 'ui_res_style3.py',
        'dialog4': 'ui_res_style4.py',
        'dialog5': 'ui_res_style5.py',
        'others': 'ui_res_others.py' }
    sDataFolder = os.path.normpath(os.path.join(sExePath, 'script/data')).replace('\\', '/')
    for sKey, vData in dStyleResult.iteritems():
        sPath = os.path.join(sDataFolder, dDialog2FileName[sKey])
        f = open(sPath, 'w')
        sContent = '# coding:gbk\n\n'
        sContent += 'STYLE_UI_RES_LIST=[\n'
        for _s in set(vData):
            sContent += "\t'" + _s.replace('\\', '/') + "',\n"
        
        sContent += ']'
        f.write(sContent)
        f.close()
    


def InitAirtest(*args):
    import sys
    sPathList = [
        'data',
        'data/mxbhtree']
    for sPath in sPathList:
        if sPath not in sys.path:
            sys.path.append(sPath)
            continue
    
    import poco
    poco.StartAirTest()


def ListAllItemRes():
    import os
    sExePath = os.path.normpath(os.getcwd()).replace('\\', '/')
    sFileRoot = os.path.normpath(os.path.join(sExePath, 'item/item44')).replace('\\', '/')
    vFileName = os.listdir(sFileRoot)
    sDataPath = os.path.normpath(os.path.join(sExePath, 'script/data/item_res_list.py')).replace('\\', '/')
    f = open(sDataPath, 'w')
    sContent = '# coding:gbk\n\n'
    sContent += 'ITEM_RES_LIST=[\n'
    for _s in set(vFileName):
        sContent += "\t'" + _s.replace('\\', '/') + "',\n"
    
    sContent += ']'
    f.write(sContent)
    f.close()


def ScanCurPathFileWithPNG():
    import os
    sExePath = os.path.normpath(os.getcwd()).replace('\\', '/')
    sFileRoot = os.path.normpath(os.path.join(sExePath, '')).replace('\\', '/')
    excludeName = [
        sFileRoot + '/.svn',
        sFileRoot + '/script']
    sDataPath = os.path.normpath(os.path.join(sExePath, 'fileWithPNG.txt')).replace('\\', '/')
    f = open(sDataPath, 'w')
    sContent = 'RootPath:\t' + sFileRoot + '\n\n'
    f.write(sContent)
    for sRoot, sDirList, sFileList in os.walk(sFileRoot):
        bCheck = 0
        for item in excludeName:
            if sRoot[:len(item)].replace('\\', '/') == item:
                bCheck = 1
                break
                continue
        
        if bCheck == 1:
            continue
        
        for sFileName in sFileList:
            print sFileName
            if os.path.splitext(sFileName)[1] == '.PNG':
                sContent += 'FileName: ' + sFileName + '\tRootPath: ' + sRoot + '\t\n'
                continue
        
    
    f.write(sContent)
    f.close()


def StartYunGame():
    import gamectrl
    gamectrl.SetYunGameFlag(True)


def DoUITrans():
    import misc
    if misc.GetMAC() != '90004e73cec6':
        return None
    
    import uitrans_s4tos1
    import uitrans_s4tos2
    import uitrans_s4tos3
    uitrans_s4tos1.DoWalk()
    uitrans_s4tos1.DoTransform()
    uitrans_s4tos2.DoWalk()
    uitrans_s4tos2.DoTransform()
    uitrans_s4tos3.DoWalk()
    uitrans_s4tos3.DoTransform()

CMD2CALLNOW = {
    'testmode': DoTest,
    'excelmodel': CExcelMgr.Init,
    'testwalker': TestWalker,
    'replayVideo': ReplayVideo,
    'autoReplay': AutoReplay,
    'quickReplayVideo': QuickReplayVideo,
    'CheckCvrSpr': CheckCvrSpr,
    'FindNullIgs': FindNullIgs,
    'auto_del_hero_frame': AutoDelHeroFrame,
    'auto_detect_igs_pal': AutoDetectIgsPal,
    'list_frame_use_info': ListFrameUseInfo,
    'list_frame_difference_between_new_and_old_zhs': ListFrameDiffenceBetweenNewAndOldZhanHuanShou,
    'count_load_ui_time': DelayCountLoadUITime,
    'filter_video': FilterVideo,
    'pydevd': StartPydevd,
    'autocreateui': AutoCreateUI,
    'uieditor': StartUIEditor,
    'qcprofile': StartQCProfile,
    'auto_detect_zhen_cai_se': AutoDetectZhenCaiSeRes,
    'airtest': InitAirtest,
    'scan_curpath_PNG': ScanCurPathFileWithPNG,
    'yungame': StartYunGame,
    'uitrans': DoUITrans }
