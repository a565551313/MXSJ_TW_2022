# pycdc 交叉复核产物 · script.fls entry 3428
# co_filename(原始)='script/mxgame/activity/2021duangwu/duangwu2021interface.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_3428.pyc (Python 2.5)

import random
import descinterface
import dialoguecommondata
import duangwu2021define
import interface
import misc
import timer
import wrapinterface

def CreateNpcMode(oParent, iShape, lColor = None):
    import walker
    import chardefine
    dDesc = descinterface.GetDefaultDesc()
    if lColor:
        dDesc[chardefine.DESC.COLOR] = lColor
    
    return walker.CFakeRole(oParent, 0, iShape, dDesc)


def CreateItemImage(oParent, iShape):
    import item
    return item.CreateItem44Image(oParent, iShape)


def Int2TimeStr(iValue, bMustSec = False, \xbc\x8c\xa0\xa3or = ''):
    
    def GetText(sText, \xbc\x8c\xa0\xa3or):
        if \xbc\x8c\xa0\xa3or:
            return '%s%s#n' % (\xbc\x8c\xa0\xa3or, str(sText))
        else:
            return sText

    if iValue < 60:
        result = '%s\xac\xed' % GetText(iValue, \xbc\x8c\xa0\xa3or)
    else:
        result = ''
        if iValue >= 60:
            result += '%s\xa4\xc0\xc4\xc1' % GetText(iValue / 60, \xbc\x8c\xa0\xa3or)
        
        if bMustSec and iValue % 60 != 0:
            result += '%s\xac\xed' % GetText(iValue % 60, \xbc\x8c\xa0\xa3or)
        
    return result


def GetRandomDialogue(lRemove = None):
    dData = dialoguecommondata.GetAllDialogueByKey(duangwu2021define.DIALOGUEKEY)
    lDialogue = _[1]
    return random.choice(lDialogue)


def GetHuoDongDialogue(iID):
    return dialoguecommondata.GetDialogueWithoutInnTips(duangwu2021define.DIALOGUEKEY, iID)


def TextReplace(sText, dReplace):
    for sKey, sValue in dReplace.iteritems():
        sText = sText.replace(sKey, sValue)
    
    return sText


def GetBtnStateByCookState(iState):
    for tCookState, iBtnState in duangwu2021define.COOKSTATETOBTNSTATE.iteritems():
        if iState in tCookState:
            return iBtnState
            continue
    
    return 0


class CBubbleBox(interface.CBoxObject):
    
    def __init__(self, oParent, iW, iFont = interface.FontLT14, iColor = 16777215):
        interface.CBoxObject.__init__(self, oParent, iW, 60, 0, 0)
        self.m_oText = None
        self.m_oBubbleImgList = []
        self.m_oBubbleBox = None
        self.m_iFont = iFont
        self.m_iColor = iColor
        self.m_oTimer = None

    
    def ClearContent(self):
        self.m_oText = None
        self.m_oBubbleBox = None
        self.m_oBubbleImgList = []

    
    def CreateBubble(self, sMsg):
        iAl = 117
        iColor = self.m_iColor
        (iW, _) = self.GetSize()
        self.m_oText = wrapinterface.WrapRichText(self, iW, self.m_iFont, sMsg, iColor)
        interface.Center(self.m_oText)
        (iW, iH) = self.m_oText.GetSize()
        iW += 6
        iH += 6
        self.m_oBubbleBox = interface.CBoxObject(self, iW, iH, 0, iAl)
        interface.Center(self.m_oBubbleBox)
        oEdgeList = wrapinterface.DrawEdge(self.m_oBubbleBox, iW, iH)
        self.m_oBubbleImgList = oEdgeList

    
    def SetShowTime(self, iShowTime):
        if iShowTime:
            self.ClearTimer()
            self.m_oTimer = timer.Timer(iShowTime, self.DoShowTime, 1, self)
        

    
    def DoShowTime(self):
        self.ClearTimer()
        self.ClearContent()

    
    def ClearTimer(self):
        if self.m_oTimer:
            self.m_oTimer.Release()
            self.m_oTimer = None
