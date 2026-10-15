# pycdc 交叉复核产物 · script.fls entry 160
# co_filename(原始)='script/mxgame/tianji/model/mdtianjicompete.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_160.pyc (Python 2.5)

import slot
import tianjiplandata
g_TianjiCompeteModel = None

def ModuleReset():
    global g_TianjiCompeteModel
    g_TianjiCompeteModel = None


def GetTianjiCompeteModel():
    global g_TianjiCompeteModel
    if not g_TianjiCompeteModel:
        g_TianjiCompeteModel = CTianjiCompeteModel()
    
    return g_TianjiCompeteModel


class CTianjiCompeteModel(slot.ISignalSubject):
    
    def __init__(self):
        self.ssInit()
        self.m_iImgShape = None

    
    def SetImgShape(self, shape):
        self.m_iImgShape = shape

    
    def GetImgShape(self):
        if self.m_iImgShape:
            return self.m_iImgShape
        
        import random
        lstImgShape = tianjiplandata.GetData().keys()
        index = random.randint(0, len(lstImgShape) - 1)
        self.m_iImgShape = lstImgShape[index]
        return lstImgShape[index]

    
    def GetDlgSels(self):
        shape = self.GetImgShape()
        dItem = tianjiplandata.GetShapeData(shape)
        tSels = (dItem['sel1'], dItem['sel2'], dItem['sel3'], dItem['sel4'])
        return tSels

    
    try:
        GetImgPath =             shape = self.GetImgShape()
            dItem = tianjiplandata.GetShapeData(shape)
            return dItem['path']

        
        def GetDlgAnswer(self):
            shape = self.GetImgShape()
            dItem = tianjiplandata.GetShapeData(shape)
            return dItem['answer']

        return <NODE:36>
