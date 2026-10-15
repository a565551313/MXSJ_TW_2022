# pycdc 交叉复核产物 · script.fls entry 864
# co_filename(原始)='script/mxgame/delaywalker/model/delayloading.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_864.pyc (Python 2.5)

'''
\xc4\xa3\xbf\xe9\xcb\xb2\xc1\xac\xb2\xbb\xc7\xe5\xc0\xed
'''
import C_sys
import commoncb
import net
import operactrl
import permission
import slot
import interface
import timer
import time
import misc
import setfps
TEST = False
g_DelayLoadingMgr = None
LOADING_MAX_TIME = 2.5
FIRST_BOOT_LOADING_MAX_TIME = 7
DELAY_LOAD_WARUI_MAGIC_SHORT_KEY_TIME = 4
DELAY_LOAD_MAP_ANI_TIME = 5
DELAY_LOAD_MAP_OBJECT_TIME = 6
DELAY_LOAD_TASK_FOLLOW_REWARD_TIME = 7
DELAY_BANWORD_CHECK_TEXT_TIME = 8
DELAY_REFRESH_FRIEND_LIST = 9
DELAY_DOWNLOADDEFAULT = 10

def ModuleReset():
    GetDelayLoadingMgr().OnReSetTimer()


def GetDelayLoadingMgr():
    ''':rtype: CDelayLoadingMgr'''
    global g_DelayLoadingMgr
    if not g_DelayLoadingMgr:
        g_DelayLoadingMgr = CDelayLoadingMgr()
    
    return g_DelayLoadingMgr


def IsShowLoading():
    if not g_DelayLoadingMgr:
        return False
    
    return g_DelayLoadingMgr.IsShowLoding()


def EndProfile():
    import gameprofile as g
    g.SetState(0)


def StartProfile():
    import gameprofile as g
    import misc
    timer.Timer(0.033, misc.Functor(g.SetState, 1))
    timer.Timer(4.5, misc.Functor(g.SetState, 0))


class CDelayLoadingMgr(slot.ISignalSubject):
    SS_ClientStable = 'SS_ClientStable()'
    
    def __init__(self):
        self.ssInit()
        self.m_oBaseObject = interface.CBaseObject(None)
        self.m_oTimer = None
        self.m_iStableFpsInterval = setfps.GetCurFrame()
        self.m_iIntervalLow = 2
        self.m_iIntervalHigh = 8
        self.m_iStableFpsNum = 12
        import plotprodelay
        if not plotprodelay.IsNeedPreLoad() or not misc.IsUseNewRes():
            self.m_iMaxTime = None if not misc.IsFirstClientSinceSystemBoot() else FIRST_BOOT_LOADING_MAX_TIME
        else:
            self.m_iMaxTime = FIRST_BOOT_LOADING_MAX_TIME * 4
        self.m_iMaxCheckCount = 30
        self.m_bFirstType = True
        self.m_iFpsIntervalQue = []
        self.m_iStartTime = time.time()
        self.m_oLoadingDlg = None
        commoncb.RegistCB(commoncb.WAR_START, self, 'OnWarStart')
        self.m_fCountStartTime = self.m_iStartTime
        import frametaskmgr
        frametaskmgr.GetFrameTaskMgr().SetIsLoading(True)
        import mapani
        mapani.SetLoadAniEnabled(False)
        net.InitNetServerCommandQueue()

    
    def IsShowLoding(self):
        return bool(self.m_oLoadingDlg)

    
    def ResetMaxTime(self, iMaxTime):
        self.m_iMaxTime = iMaxTime

    
    def ResetMaxCheckCount(self, iMaxCheckCount):
        self.m_iMaxCheckCount = iMaxCheckCount
        self.m_iFpsIntervalQue = self.m_iFpsIntervalQue[:self.m_iMaxCheckCount - 1]

    
    def StartClientStable(self):
        net.GetNet().SetProcessSvrCmdNumPerFrame(2)
        net.MAX_PROCESS_SERVER_CMD_TIMES = 8
        net.UNPACK_PACKET_NUM_PER_PROCESS = 2
        net.MIN_UNPACK_PACKET_NUM_PER_FRAME = 2
        self.CloseClientStable()
        self.m_oTimer = timer.Timer(0.0167, self.OnCheckFps, -1, self)

    
    def CloseClientStable(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
        
        self.m_oTimer = None
        self.m_iFpsIntervalQue = []

    
    def GetIsLoading(self):
        return self.m_oTimer is not None

    
    def InitCBs(self):
        pass

    
    def CheckClientStable(self):
        iLen = len(self.m_iFpsIntervalQue)
        if iLen < self.m_iMaxCheckCount:
            return False
        
        vStableFrames = self.m_iFpsIntervalQue[-(self.m_iStableFpsNum):]
        iTimeLow = self.m_iStableFpsInterval - self.m_iIntervalLow
        iTimeHigh = self.m_iStableFpsInterval + self.m_iIntervalHigh
        for iFrame in vStableFrames:
            if iFrame < iFrame:
                pass
            elif not iFrame < iTimeHigh:
                return False
                continue
        
        iFirstFrame = self.m_iFpsIntervalQue[0]
        iPreFrame = iFirstFrame
        for iFrame in self.m_iFpsIntervalQue:
            if iFrame > iPreFrame:
                if iFrame < iFrame:
                    pass
                elif not iFrame < iTimeHigh:
                    return False
                
            iFrame < iTimeHigh
            iPreFrame = iFrame
        
        return True

    
    def OnCreateBox(self):
        import dlgloading
        import cursor
        self.m_oLoadingDlg = dlgloading.CLoadingDlg(None)
        self.m_oLoadingDlg.SetZ(199999999)
        operactrl.GetperaCtrl().SetPlayType('Loading', 1)
        cursor.SetCursorShow(False)
        self.m_fCountStartTime = time.time()
        import delayload
        delayload.MAX_LOAD_NUM_PER_FRAME *= delayload.REDUCE_MAX_LOAD_NUM_PER_FRAME_RATE

    
    def OnDelBox(self):
        import gamectrl
        self.m_oLoadingDlg = None
        operactrl.GetperaCtrl().SetPlayType('Loading', 0)
        import performancecount
        if performancecount.IsOpenPerformanceCount(performancecount.TYPE_GAME_START):
            performancecount.GetPerformanceCountManager().OnLoadingDlgClosed()
        
        import charpath
        LOG('\xa5[\xb8\xfc\xae\xc9\xb6\xa1:', time.time() - self.m_fCountStartTime - 0.5, '\xacO\xa7_\xad\xba\xa6\xb8\xb1\xd2\xb0\xca\xab\xc8\xa4\xe1\xba\xdd\xa1G', misc.IsFirstClientSinceSystemBoot(), '\xacO\xa7_\xa8\xcf\xa5\xce\xb7s\xb8\xea\xb7\xbd:', charpath.IsUseNewRes())
        self.AfterDeleteBox()

    
    def AfterDeleteBox(self):
        import frametaskmgr
        import mapgame
        import banword
        import mdshitu1
        import hero
        import mainmenu
        import mapani
        import defaulticodownload
        import cg
        oFrameTaskMgr = frametaskmgr.GetFrameTaskMgr()
        oFrameTaskMgr.AddAfterLoadingTask(0.033, net.OnLoadingFinish)
        oFrameTaskMgr.AddAfterLoadingTask(DELAY_LOAD_MAP_ANI_TIME, mapani.DelayLoadMapAni)
        oFrameTaskMgr.AddAfterLoadingTask(DELAY_LOAD_MAP_OBJECT_TIME, mapgame.DoLoadMapObject)
        oFrameTaskMgr.AddAfterLoadingTask(DELAY_BANWORD_CHECK_TEXT_TIME, banword.DelayCheckText)
        oFrameTaskMgr.AddAfterLoadingTask(DELAY_REFRESH_FRIEND_LIST, mdshitu1.DelayRefreshFriendListDlg)
        oFrameTaskMgr.AddAfterLoadingTask(DELAY_DOWNLOADDEFAULT, defaulticodownload.StartCheck)
        if hero.g_ID:
            oFrameTaskMgr.AddAfterLoadingTask(0.033, mainmenu.SwitchChatWnd)
        
        oFrameTaskMgr.SetIsLoading(False)
        oFrameTaskMgr.OnLoadingFinish()
        if cg.GetCgId() == cg.CGID_NEWBIE:
            cg.SetCgWaitTime(90)
        

    
    def OnCheckFps(self):
        if len(self.m_iFpsIntervalQue) == self.m_iMaxCheckCount:
            self.m_iFpsIntervalQue.pop(0)
        
        self.m_iFpsIntervalQue.append(C_sys.GetFPS())
        if self.CheckClientStable() or time.time() - self.m_iStartTime > self.m_iMaxTime:
            self.ssEmit(self.SS_ClientStable)
            net.ResetUnpackParams()
            self.CloseClientStable()
            return ()
        
        return ()

    
    def OnChangeScene(self):
        import innerversion
        import selectrole
        import permission
        if not TEST:
            return None
        
        ()
        if not permission.GetPermission('openloadbox'):
            self.AfterDeleteBox()
            return None
        

    
    def OnWarStart(self):
        self.ssEmit(self.SS_ClientStable)
        self.CloseClientStable()

    
    def OnReSetTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = timer.Timer(0.033, self.OnCheckFps, -1, self)
        
        if self.m_oLoadingDlg:
            self.m_oLoadingDlg.ReSetTimer()
