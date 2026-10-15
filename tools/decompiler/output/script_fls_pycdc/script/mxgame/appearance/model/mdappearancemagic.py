# pycdc 交叉复核产物 · script.fls entry 3403
# co_filename(原始)='script/mxgame/appearance/model/mdappearancemagic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3403.pyc (Python 2.5)

import slot
g_MagicModel = None

def GetModel():
    global g_MagicModel
    if not g_MagicModel:
        g_MagicModel = CMagicPalModel()
    
    return g_MagicModel


class CMagicPalModel(slot.ISignalSubject):
    SS_PalPriceChange = 'OnChange(iMagicID, iCase)'
    
    def __init__(self):
        self.ssInit()
        self.m_dMagicPrice = { }

    
    def UpdatePrice(self, iMagicID, iCase, iRyuNum, iStoneNum, iBanPal):
        if (iMagicID, iCase) in self.m_dMagicPrice and self.m_dMagicPrice[(iMagicID, iCase)] == (iRyuNum, iStoneNum, iBanPal):
            return None
        
        self.m_dMagicPrice[(iMagicID, iCase)] = (iRyuNum, iStoneNum, iBanPal)
        self.ssEmit(self.SS_PalPriceChange, iMagicID, iCase)

    
    def GetPrice(self, iMagicID, iCase):
        () = (iMagicID, iCase)
        return None(None, self.m_dMagicPrice.get)
