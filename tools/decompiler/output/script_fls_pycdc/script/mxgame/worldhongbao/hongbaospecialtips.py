# pycdc 交叉复核产物 · script.fls entry 582
# co_filename(原始)='script/mxgame/worldhongbao/hongbaospecialtips.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_582.pyc (Python 2.5)

import interface
import combdialog
import ui

def Test():
    '''
\timport hongbaospecialtips
\thongbaospecialtips.Test()
\t:return:
\t'''
    import usermacro
    usermacro.MOVE_TEXT('#s(25,D\xa5@\xac\xc9\xac\xf5\xa5]_1003)#GTest123457#n\xb9\xef#GTest123458#n\xb0e\xa5h\xa4F\xaf\xac\xba\xd6\xa1G\xa7\xd6\xbc\xd6\xb9\xda\xb7Q\xa1A\xa4@\xb8\xf4\xa6\xb3\xa7A!', 6, 1)


def CreateHongbaoMoveBar(oParent, sTxt, iTotalW, iTextW):
    return CHongbaoMoveBar(oParent, sTxt, iTotalW, iTextW)


class CHongbaoMoveBar(interface.CBoxObject):
    GOLD_X_OFFSET = -30
    
    def __init__(self, oParent, sTxt, iTotalW, iTextW):
        iH = self.GetHongBaoTxtH(sTxt, iTextW)
        interface.CBoxObject.__init__(self, oParent, iTotalW, iH, 0, 0)
        self.m_oFrameList = []
        self.m_oGoldImg = None
        self.m_oCatImg = None
        self.m_oYanhua = None
        self.CreateBG()

    
    def Start(self):
        self.CreateGold()
        self.CreateCat()
        self.CreateYanhua()

    
    def Stop(self):
        self.m_oCatImg = None
        self.m_oYanhua = None
        self.m_oGoldImg = None

    
    def HideCat(self, *args):
        self.m_oCatImg.SetShow(\xaa\x8d\x80se)

    
    def CreateBG(self):
        (iW, iH) = self.GetSize()
        self.m_oFrameList = combdialog.CreatePngNineFrame(self, 0, 0, iW, iH, 'combdialog4/\xd4\xd3\xcd\xbc/\xca\xc0\xbd\xe7\xba\xec\xb0\xfc/\xba\xec\xb0\xfc\xd7\xa3\xb8\xa3\xba\xe1\xb7\xf9/\xba\xec\xb0\xfc\xba\xe1\xb7\xf9/')

    
    def CreateGold(self):
        (iW, iH) = self.GetSize()
        self.m_oGoldImg = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xca\xc0\xbd\xe7\xba\xec\xb0\xfc/\xbd\xf0\xb1\xd2/\xbd\xf0\xb1\xd2b_.igs', interface.UIPath)
        self.m_oGoldImg.CreateCommand(3, 'animation')
        self.m_oGoldImg.SetPos(iW + self.GOLD_X_OFFSET, 0)
        self.m_oGoldImg.SetZ(10)

    
    def CreateCat(self):
        import misc
        self.m_oCatImg = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xca\xc0\xbd\xe7\xba\xec\xb0\xfc/\xc3\xa8/\xc3\xa8_.igs', interface.UIPath)
        self.m_oCatImg.CreateCommand(3, 'animation')
        self.m_oCatImg.CreatePyCommand(168, misc.Functor(self.HideCat))
        self.m_oCatImg.SetZ(10)
        interface.BottomLeft(self.m_oCatImg, offsetx = 10, offsety = 30)

    
    def CreateYanhua(self):
        self.m_oYanhua = ui.CImage(self, 'combdialog4/\xd4\xd3\xcd\xbc/\xca\xc0\xbd\xe7\xba\xec\xb0\xfc/\xd1\xcc\xbb\xa8/\xd1\xcc\xbb\xa81_.igs', interface.UIPath)
        self.m_oYanhua.SetZ(-1)
        self.m_oYanhua.CreateCommand(3, 'animation')
        interface.BottomCenter(self.m_oYanhua, offsety = 100)

    
    def GetHongBaoTxtH(self, sTxt, iTextW):
        oTxtObj = interface.CRichTextObject(None, iTextW, interface.FontLT14_3, sTxt, 16776960)
        (_, iTxth) = oTxtObj.GetSize()
        if iTxth > 25:
            if iTxth > 40:
                h = iTxth + 5
            else:
                h = 45
        elif iTxth > 20:
            h = iTxth + 5
        else:
            h = 25
        return h
