# pycdc 交叉复核产物 · script.fls entry 1638
# co_filename(原始)='script/mxgame/yearvoice/yearvoicereportctrl.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1638.pyc (Python 2.5)

import misc
import yearvoicecontext
g_oCtrl = None

def ModuleReset():
    global g_oCtrl
    g_oCtrl = None


def GetCtrl():
    global g_oCtrl
    if not g_oCtrl:
        g_oCtrl = CYearVoiceReportCtrl()
    
    return g_oCtrl


class CYearVoiceReportCtrl(object):
    
    def __init__(self):
        self.m_iCurReportPlayerID = None
        self.m_sAskUrl = []
        self.m_dReportData = { }

    
    def OpenReportDlg(self, iPlayerID, sUrls):
        oContext = yearvoicecontext.GetYearVoiceContext()
        oPlayer = oContext.GetProGoodVoiceMgr().GetPlayerGoodVoice(sUrls)
        dPlayer = { }
        if oPlayer:
            dPlayer = oPlayer.GetData()
        
        if not dPlayer:
            dPlayer = oContext.GetMyGoodVoiceMgr().GetOtherData()
        
        if not dPlayer:
            LOG_DEBUG('\xa7\xe4\xa4\xa3\xa8\xec\xb8\xd3\xaa\xb1\xaea\xaa\xba\xabH\xae\xa7')
            return None
        
        if self.m_iCurReportPlayerID == iPlayerID:
            return None
        
        self.m_iCurReportPlayerID = iPlayerID
        lVoice = []
        lVoiceInfo = dPlayer.get('lVoice', [])
        for \x88\xbaoice in lVoiceInfo:
            if \x88\xbaoice.get('sUrl', '') == sUrls:
                lVoice.append(\x88\xbaoice)
                break
                continue
        
        self.m_dReportData = {
            'sName': dPlayer.get('sName', ''),
            'lVoice': lVoice,
            'iServerID': dPlayer.get('iServer', misc.GetServerID()) }
        if self.m_dReportData:
            self.CallReport()
            self.m_iCurReportPlayerID = None
        

    
    def CallReport(self):
        import dlgreport
        dlgreport.C2GSNewOpenReport(self.m_iCurReportPlayerID, self.m_dReportData['sName'], dlgreport.TYPE_YEARVOICE_AUDIO, dData = self.m_dReportData)
