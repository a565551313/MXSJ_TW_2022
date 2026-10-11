# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\render\netrender.py
from renderprotocol import *
import crashinfo
g_sLastClientID = None

def TaskAdd(agent, *args):
    for value in args:
        value_type = type(value)
        if value_type in (int, long, bool):
            agent.TaskAddI(value)
        elif value_type == str:
            agent.TaskAddBinary(value)
        else:
            raise NotImplementedError('未知数据类型的压包：type:%s;value=%s' % (value_type, value))


def TaskUnpack(agent):
    result = []
    for i in range(0, 1000):
        iValue = agent.TaskUnpackInt()
        if iValue is not None:
            result.append(iValue)
            continue
        iBinary = agent.TaskUnpackBinary()
        if iBinary is not None:
            result.append(iBinary)

    return result


def ProcessC2RAddRenderTask(renderAgent, sClientID):
    args = TaskUnpack(renderAgent)
    iType, sTaskID = args[:2]
    msg = 'ProcessC2RAddRenderTask sClientID=%s;iType=%d;sTaskID=%s;' % (sClientID, iType, repr(sTaskID))
    crashinfo.CommunicateInfo(msg)
    NormalLog(msg)
    import rendertask
    rendertask.ProcessC2RAdd(sClientID, *args)


def ProcessC2RDelRenderTask(renderAgent, sClientID):
    iType, sTaskID = TaskUnpack(renderAgent)
    msg = 'ProcessC2RDelRenderTask sClientID=%s;iType=%d;sTaskID=%s;' % (sClientID, iType, repr(sTaskID))
    crashinfo.CommunicateInfo(msg)
    NormalLog(msg)
    import rendertask
    rtobj = rendertask.GetTask(iType)
    rtobj.OnC2RDel(sClientID, sTaskID)


def ProcessC2ROnlineUpdate(renderAgent, sClientID):
    sName, sCode = TaskUnpack(renderAgent)
    msg = 'C2ROnlineUpdate sClientID=%s;sName=%s;' % (sClientID, sName)
    crashinfo.CommunicateInfo(msg)
    NormalLog(msg)
    import renderonlineupdate
    renderonlineupdate.OnlineUpdate(sName, sCode)


def ProcessC2RQuit(renderAgent, sClientID):
    import renderagent
    renderagent.OnC2RQuit(sClientID)


def ProcessC2RVersion(renderAgent, sClientID):
    import version
    sys_version = version.GetSysVersion()
    script_version = version.GetScriptVersion()
    R2CVersion(sClientID, sys_version, script_version)


def ProcessPalUpdate(renderAgent, sClientID):
    import renderagent
    lArgs = TaskUnpack(renderAgent)
    iTaskID = lArgs[0]
    iLen = lArgs[1]
    lstPal = []
    for iIndex in xrange(iLen):
        iVal = lArgs[iIndex + 2]
        if 180 < iVal <= 360:
            iVal = -(360 - iVal)
        lstPal.append(iVal)

    NormalLog('ProcessPalUpdate', iTaskID, lstPal)
    dTaskInfo = renderagent.GetRenderTaskInfo(iTaskID)
    if dTaskInfo and dTaskInfo['obj']:
        dTaskInfo['obj'].SetPalCase(lstPal)
    NormalLog('ProcessEnd')


def ProcessKillRender(renderAgent, sClientID):
    import main
    main.MainLoopQuit(True)


def ProcessKeepAlive(renderAgent, sClientID):
    R2CKeepAlive(sClientID)


PROCESS_C2R_DICT = {PR_C2R_ADD_RENDER_TASK: ProcessC2RAddRenderTask, 
   PR_C2R_DEL_RENDER_TASK: ProcessC2RDelRenderTask, 
   PR_C2R_ONLINE_UPDATE: ProcessC2ROnlineUpdate, 
   PR_C2R_QUIT: ProcessC2RQuit, 
   PR_C2R_VERSION: ProcessC2RVersion, 
   PR_C2R_KEEPALIVE_MX: ProcessKeepAlive, 
   PR_C2R_RENDER_TASK_PAL_UPDATE: ProcessPalUpdate, 
   PR_C2R_KILL_RENDER: ProcessKillRender}

def ProcessC2R(renderAgent, sClientID, iHeader):
    global g_sLastClientID
    g_sLastClientID = sClientID
    func = PROCESS_C2R_DICT.get(iHeader)
    if func:
        func(renderAgent, sClientID)
    else:
        NormalLog('ProcessC2R Unknow Header. 0x%X' % iHeader)


def R2CDoneRenderTask(renderAgent, sClientID, iSuccess, iTaskID, iBytePerPixel, sPixelData, width, height, extends):
    renderAgent.TaskPrepare(PR_R2C_DONE_RENDER_TASK)
    TaskAdd(renderAgent, iSuccess, iTaskID, iBytePerPixel, sPixelData, width, height, *extends)
    return renderAgent.TaskSend(sClientID)


def R2CVersion(sClientID, sys_version, script_version):
    import renderagent
    renderAgent = renderagent.GetRenderAgent()
    renderAgent.TaskPrepare(PR_R2C_VERSION)
    TaskAdd(renderAgent, *sys_version)
    TaskAdd(renderAgent, *script_version)
    return renderAgent.TaskSend(sClientID)


def R2CKeepAlive(sClientID):
    import renderagent
    renderAgent = renderagent.GetRenderAgent()
    renderAgent.TaskPrepare(PR_R2C_KEEPALIVE_MX)
    return renderAgent.TaskSend(sClientID)


def R2CErrUpload(sErr):
    if g_sLastClientID is None:
        return
    else:
        import renderagent
        renderAgent = renderagent.GetRenderAgent()
        renderAgent.TaskPrepare(PR_R2C_ERR_UPLOAD)
        TaskAdd(renderAgent, sErr)
        return renderAgent.TaskSend(g_sLastClientID)
