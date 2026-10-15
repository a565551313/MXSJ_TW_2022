# pycdc 交叉复核产物 · script.fls entry 1774
# co_filename(原始)='script/wrap/wrapuserlinklogic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1774.pyc (Python 2.5)

import misc
import netcommon
import pubtimeformat
import timer
g_dIDTip = { }
g_dCBs = { }
g_iCurSeq = 0
LINKICONID_HONGBAO = 603

def ModuleReset():
    global g_dIDTip, g_dCBs, g_iCurSeq
    g_dIDTip = { }
    g_dCBs = { }
    g_iCurSeq = 0


def GenerateSeq():
    global g_iCurSeq
    g_iCurSeq = (g_iCurSeq + 1) % 255
    return g_iCurSeq


def DelCB(iIconID):
    if iIconID in g_dCBs:
        del g_dCBs[iIconID]
    


def AskForIconTips(iIconID, oFini\xb5\xae\x85\x84):
    '''
\t:param oFinishCB:
\t:param iIconID:
\t:return:
\t'''
    if not isinstance(oFini\xb5\xae\x85\x84, misc.Functor):
        oFini\xb5\xae\x85\x84 = misc.Functor(oFini\xb5\xae\x85\x84)
    
    g_dCBs[iIconID] = oFini\xb5\xae\x85\x84
    LOG_DEBUG('AskForIconTips>>>>>>>', iIconID)
    netcommon.C2SRequestUserLinkTips(iIconID)


def OnIconTips(dData):
    LOG_DEBUG('OnIconTips>>>>>>', dData)
    for iIconID, dValue in dData.iteritems():
        oFunc = g_dCBs.get(iIconID, None)
        sTips = dValue
        if iIconID == LINKICONID_HONGBAO:
            sTips = '\xac\xf5\xa5]\xad\xad\xae\xc9\xac\xa1\xb0\xca\xb0\xca\xb4\xc1\xb6\xa1\xb2\xd6\xbfn\xb5o\xa9\xf1\xac\xf5\xa5]\xb9F2000\xa5@\xac\xc9\xb0^\xc4m\xa5i\xc0\xf2\xb1o7\xa4\xd1\xaa\xba\xb2\xe1\xa4\xd1\xbc\xd0\xc5\xd2#r'
            iEndStampTime = int(dValue)
            iLeftTime = iEndStampTime - misc.GetServerCurrentTime()
            sLeftTime = pubtimeformat.PubLeftTimeDayMin(iLeftTime)
            sTips += '\xb3\xd1\xbel\xae\xc9\xb6\xa1\xa1G%s' % sLeftTime
        
        if oFunc:
            
            try:
                oFunc(sTips)
            except:
                LOG_EXC('wrapuserlinklogic.OnIconTips>>>\x08??"?', iIconID)

            del g_dCBs[iIconID]
            continue
