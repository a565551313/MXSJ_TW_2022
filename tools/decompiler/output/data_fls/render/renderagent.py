# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\render\renderagent.py
import C_sys, C_object
from renderprotocol import *
import crashinfo
g_Scene = None
g_RenderAgent = None
g_Director = None

def Start():
    global g_RenderAgent
    crashinfo.BaseInfo()
    crashinfo.StartInfo('Start RenderAgent')
    agent = CRenderAgent()
    if not agent.InitProcRender():
        crashinfo.StartInfo('Start RenderAgent Fail')
        return
    g_RenderAgent = agent
    g_RenderAgent.SetPos(0, 0)
    crashinfo.StartInfo('Start RenderAgent Success')


def AddRenderObj(sClientID, sTaskID, obj, width, height, extends):
    g_RenderAgent.AddRenderObj(sClientID, sTaskID, obj, width, height, extends)


def DelRenderObj(sClientID, iTaskID):
    g_RenderAgent.DelRenderObj(sClientID, iTaskID)


def OnC2RQuit(sClientID):
    g_RenderAgent.OnClientDisconnect(sClientID)


def GetRenderAgent():
    if g_RenderAgent:
        return g_RenderAgent.m_RenderAgent


def GetRenderTaskInfo(sTaskID):
    if g_RenderAgent:
        return g_RenderAgent.GetTaskInfo(sTaskID)
    else:
        return


class CRenderLayer(C_object.CLayer):
    m_RenderAgent = None
    m_Scene = None
    m_Director = None
    m_Camera = None
    m_FrameBuffer = None
    m_FilePath = None
    CLEAR_COLOR = (0, 0, 0, 255)

    def InitCommunicate(self):
        import C_sharemem
        renderAgent = C_sharemem.CProcRenderAgent.GetInstance()
        success = renderAgent.InitAgent(SHAREUTIL_3D_RENDERER_NAME)
        if not success:
            crashinfo.StartInfo('InitAgent:Fail')
            NormalLog('InitAgent:Fail')
            import main
            main.MainLoopQuit(True)
            return False

        def OnClientDisconnect(obj, lPid):
            for iPid in lPid:
                sClientID = '%s%d' % (CLIENT_NAME, iPid)
                obj.OnClientDisconnect(sClientID)

        import pubcore.function
        renderAgent.SetMsgCallback(self.OnClientMessage)
        renderAgent.SetDisconnectCallback(pubcore.function.Functor(OnClientDisconnect, self))
        self.m_RenderAgent = renderAgent
        return True

    def InitRender(self, width, height):
        C_object.SetAsync(False)
        self.m_Scene = C_object.CScene()
        self.m_Director = C_object.CDisplayLinkDirector.GetInstance()
        self.m_Director.RunWithScene(self.m_Scene)
        self.m_Scene.AddChild(self)
        C_sys.SetDisableBackgroundPaused(True)
        C_sys.SetPackageFilesSearchMode(1)
        C_sys.SetPakDecompressMode(3)
        C_sys.LoadPackageFiles('config/packlist.ini')
        self.m_Director.SetNotSwapBuffer(True)
        self.m_Director.SetAnimationInterval(1 / 60.0)
        self.m_Director.SetConfigInfo('fb_blend_type', 1)
        camera = C_object.CCamera()
        camera.InitOrthographic(width, height, -1024, 1024, left=-width / 2, bottom=-height / 2)
        camera.SetCameraFlag(1)
        camera.SetPos(0, 0, z=300)
        camera.LookAt(0, 0, 0, 0, 1, 0)
        self.AddChild(camera)
        frameBuffer = C_object.CFrameBuffer(width, height)
        frameBuffer.SetClearColor(*self.CLEAR_COLOR)
        camera.SetFrameBuffer(frameBuffer)
        self.m_Camera = camera
        self.m_FrameBuffer = frameBuffer

    def CaptureScreen(self, rect_lst, *args, **kwargs):
        if self.m_FilePath:
            sFilePath = self.m_FilePath
            self.m_FilePath = None
        else:
            sFilePath = ''

        def OnCaptureScreenOver(oTexture, func, rect_lst, *args, **kwargs):
            for data in rect_lst:
                x, y, w, h = data[:4]
                sPixelData, iBytePerPixel = oTexture.DumpPixelData(reload=True, offsetX=x, offsetY=y, width=w, height=h)
                func(data, sPixelData, iBytePerPixel, *args, **kwargs)

        screenShot = C_object.CScreenShot()
        callfunc = C_object.CCallFunc(OnCaptureScreenOver, self.OnCaptureScreen, rect_lst, *args, **kwargs)
        screenShot.GetCameraTextureWithCallFunc(1, callfunc, outputPath=sFilePath)
        return

    def OnClientMessage(self, sClientID, iHeader):
        crashinfo.CommunicateInfo('sClientID=%s; iHeader=%d' % (sClientID, iHeader))
        if self.m_RenderAgent:
            import netrender
            netrender.ProcessC2R(self.m_RenderAgent, sClientID, iHeader)

    def OnClientDisconnect(self, sClientID):
        return

    def OnCaptureScreen(self, data, sPixelData, iBytePerPixel, *args, **kwargs):
        return


class CRenderAgent(CRenderLayer):

    def __init__(self):
        CRenderLayer.__init__(self)
        self.m_Side = 256
        import C_math
        self.m_Quad = C_math.CRegionQuadtree(self.m_Side, 3)
        self.m_TaskDict = {}
        self.m_TaskList = []
        self.m_CurrentLoopID = 0
        self.m_WaitStep = 0

    def GetTaskInfo(self, sTaskID):
        return self.m_TaskDict.get(sTaskID)

    def InitProcRender(self):
        if not self.InitCommunicate():
            return False
        self.InitRender(self.m_Side, self.m_Side)
        import pubcore.timer
        self.m_LoopTimer = pubcore.timer.Timer(1 / 30.0, self.RenderLoop, -1)
        return True

    def RenderLoop(self):
        if self.m_WaitStep > 0:
            self.m_WaitStep -= 1
            return
        else:
            if not self.m_TaskList:
                return
            for sTaskID, dTaskData in self.m_TaskDict.iteritems():
                obj = dTaskData['obj']
                obj.SetShow(False)

            fb_width, fb_height = self.m_Side, self.m_Side
            task_lst = []
            rect_lst = []
            for idx, sTaskID in enumerate(self.m_TaskList):
                dTaskData = self.m_TaskDict[sTaskID]
                obj_width = dTaskData['width']
                obj_height = dTaskData['height']
                x, y = self.m_Quad.GetRegion(1 + idx, obj_width, obj_height)
                if x == 0 and y == 0:
                    break
                task_lst.append(sTaskID)
                obj = dTaskData['obj']
                obj.SetShow(True)
                obj.SetPos(x - fb_width / 2, y - fb_height / 2)
                extends = dTaskData['extends']
                rect_lst.append((x, fb_height - y - obj_height, obj_width, obj_height, sTaskID, extends))

            self.m_CurrentLoopID += 1
            self.m_WaitStep = 10
            if not task_lst:
                sTaskID = self.m_TaskList[0]
                self.OnCaptureScreen((0, 0, 0, 0, sTaskID, []), None, 4, self.m_CurrentLoopID)
                return
            size = len(task_lst)
            if len(self.m_TaskList) != size:
                self.m_TaskList = self.m_TaskList[size:] + task_lst
            self.CaptureScreen(rect_lst, self.m_CurrentLoopID)
            return

    def OnClientDisconnect(self, sClientID):
        NormalLog('OnClientDisconnect %s' % sClientID)
        task_lst = []
        for sTaskID, dTaskData in self.m_TaskDict.iteritems():
            if dTaskData['sClientID'] == sClientID:
                task_lst.append(sTaskID)

        NormalLog('任务列表 %s' % task_lst)
        for sTaskID in task_lst:
            del self.m_TaskDict[sTaskID]
            self.m_TaskList.remove(sTaskID)

    def OnCaptureScreen(self, data, sPixelData, iBytePerPixel, loopid):
        if loopid != self.m_CurrentLoopID:
            NormalLog('截图渲染超时，已经略过此任务')
            return
        else:
            self.m_WaitStep = 0
            _, _, width, height, sTaskID, extends = data
            dTaskData = self.m_TaskDict.get(sTaskID)
            if not dTaskData:
                return
            sClientID = dTaskData['sClientID']
            if sPixelData is None:
                sPixelData = ''
                iSuccess = 0
            else:
                iSuccess = 1
            info = 'sClientID=%s;sTaskID=%s;iSuccess=%d;' % (sClientID, sTaskID, iSuccess)
            crashinfo.DealInfo(info)
            import netrender
            result = netrender.R2CDoneRenderTask(self.m_RenderAgent, sClientID, iSuccess, sTaskID, iBytePerPixel, sPixelData, width, height, extends)
            info += 'result=%d;' % result
            crashinfo.DealInfo(info)
            if not (iSuccess and result):
                NormalLog(info)
            return

    def AddRenderObj(self, sClientID, sTaskID, obj, width, height, extends):
        dTaskData = {'sClientID': sClientID, 
           'obj': obj, 
           'width': width, 
           'height': height, 
           'extends': extends}
        if sTaskID in self.m_TaskDict:
            NormalLog('存在重复Add情况：%s-%s' % (sClientID, sTaskID))
        else:
            self.m_TaskList.append(sTaskID)
        self.m_TaskDict[sTaskID] = dTaskData

    def DelRenderObj(self, sClientID, sTaskID):
        if sTaskID in self.m_TaskDict:
            del self.m_TaskDict[sTaskID]
            self.m_TaskList.remove(sTaskID)
