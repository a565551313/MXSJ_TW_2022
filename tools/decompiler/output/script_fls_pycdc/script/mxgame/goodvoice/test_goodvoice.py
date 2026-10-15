# pycdc 交叉复核产物 · script.fls entry 2795
# co_filename(原始)='script/mxgame/goodvoice/test_goodvoice.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2795.pyc (Python 2.5)

'''
import test_goodvoice as t
t.OpenOtherGoodVoice()

t.OpenMainGoodVoice(1)

t.OpenBaoMingDlg()
t.OpenMyVoice()




t.Reload()


'''
import goodvoicecontext
import mdmygoodvoice
import goodvoiceinterface

def Reload():
    tValue = ('dgtgoodvoice_main', 'dlggoodvoice_main', 'dlggoodvoice_item', 'dlggoodvoice_self', 'dgtgoodvoice_self', 'dgtgoodvoice_others', 'dlggoodvoice_others', 'dlggoodvoice_edit', 'dgtgoodvoice_edit', 'dlgmygoodvoice', 'dgtmygoodvoice', 'dlgvoiceitem', 'dlgeditgoodvoice', 'dgteditgoodvoice', 'dlggoodvoicemain', 'dgtgoodvoicemain', 'logic_audiomgr', 'logic_uploadaudio', 'logic_recordaudio', 'logic_playaudio', 'goodvoicecontext', 'goodvoiceinterface', 'mdmygoodvoice', 'mdgoodvoicemgr', 'dlgeditvoicename', 'netgoodvoice')
    for sModel in tValue:
        
        try:
            oModel = __import__(sModel)
            reload(oModel)
        continue
        continue

    


def OpenMainGoodVoice(iPage = 1):
    import random
    import misc
    lPlayerInfo = []
    iPageNum = 5
    iMaxPage = 100
    iRandomSeed = 1
    tUrl = [
        'http://voice1.duoyi.com:82/gv/pp/200622/1004/cedb27059af754618a452283c856f9b6.mdya',
        'http://voice1.duoyi.com:82/gv/pp/200622/1004/cedb27059af754618a452283c856f9b6.mdya']
    import dgtgoodvoice_main
    dgtgoodvoice_main.SetIsTest(True)
    for i in xrange(iPageNum):
        lVoice = []
        for iIndex in xrange(2):
            sUrl = tUrl[iIndex]
            sSongName = 'hfl_test_%s' % iIndex
            iDur = random.choice([
                60,
                180,
                240])
            iState = random.choice([
                0,
                1])
            dVoice = {
                'sName': sSongName,
                'sUrl': sUrl,
                'iDur': iDur,
                'iState': iState,
                'iSendTime': misc.Time() + iDur }
            lVoice.append(dVoice)
        
        iNum = i + iPageNum * (iPage - 1)
        iPlayerID = 2222221 + iNum
        sName = 'test_%s' % iPlayerID
        sOrg = 'test'
        iGrade = random.randint(30, 150)
        iCountry = 1
        iClass = random.choice([
            1,
            2,
            3])
        iSex = random.choice([
            1,
            2])
        iFame = 0
        iShape = random.choice([
            111,
            112,
            121])
        tPhotoAttr = []
        sTittle = 'tittle_%s' % random.randint(100, 1000)
        dPlayer = {
            'iID': iNum,
            'sName': sName,
            'iPlayerID': iPlayerID,
            'iGrade': iGrade,
            'iCountry': iCountry,
            'sOrg': sOrg,
            'iRenqi': iFame,
            'lVoice': lVoice,
            'iCls': iClass,
            'sTittle': sTittle,
            'iSex': iSex,
            'iShape': iShape,
            'tPhotoAttr': tPhotoAttr }
        lPlayerInfo.append(dPlayer)
    
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oGoodDataMgr = oContext.GetGoodVoiceDataMgr()
    None(None, None, None, None, None, None, None, None, None, None, None, None, None, oGoodDataMgr)(lPlayerInfo)
    oContext.OpenGoodVoiceMainDlg()


def OpenMyVoice():
    import random
    import misc
    import hero
    lVoice = []
    tUrl = [
        'http://et.oa.com:6060/gv/pp/200616/2216/23166385a97b420.dya',
        'http://et.oa.com:6060/gv/pp/200616/2216/23166385a97b421.dya']
    for iIndex in xrange(2):
        sUrl = tUrl[iIndex]
        sSongName = 'hfl_test_%s' % iIndex
        iDur = random.choice([
            60,
            180,
            240])
        iState = random.choice([
            0,
            1])
        dVoice = {
            'sName': sSongName,
            'sUrl': sUrl,
            'iDur': iDur,
            'iState': iState,
            'iSendTime': misc.Time() + iDur }
        lVoice.append(dVoice)
    
    iNum = 11
    iPlayerID = hero.GetHeroID()
    sName = 'test_%s' % iPlayerID
    sOrg = 'test'
    iGrade = random.randint(30, 150)
    iCountry = 1
    iClass = random.choice([
        1,
        2,
        3])
    iSex = random.choice([
        1,
        2])
    iFame = 0
    iShape = random.choice([
        111,
        112,
        121])
    tPhotoAttr = []
    sTittle = 'tittle_%s' % random.randint(100, 1000)
    dPlayer = {
        'iID': iNum,
        'sName': sName,
        'iPlayerID': iPlayerID,
        'iGrade': iGrade,
        'iCountry': iCountry,
        'sOrg': sOrg,
        'iRenqi': iFame,
        'lVoice': lVoice,
        'iCls': iClass,
        'sTittle': sTittle,
        'iSex': iSex,
        'iShape': iShape,
        'tPhotoAttr': tPhotoAttr }
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oMyDataMgr = oContext.GetMyGoodVoiceData()
    oMyDataMgr.UpdateData(dPlayer)
    oContext = goodvoicecontext.GetGoodVoiceContext()
    oContext.OpenMyGoodVoiceDlg()


def OpenOtherGoodVoice(iPlayerID = 2222222):
    import random
    import misc
    lVoice = []
    tUrl = [
        'http://et.oa.com:6060/gv/pp/200616/2216/23166385a97b420.dya',
        'http://et.oa.com:6060/gv/pp/200616/2216/23166385a97b421.dya']
    for iIndex in xrange(2):
        sUrl = tUrl[iIndex]
        sSongName = 'hfl_test_%s' % iIndex
        iDur = random.choice([
            60,
            180,
            240])
        iState = random.choice([
            0,
            1])
        dVoice = {
            'sName': sSongName,
            'sUrl': sUrl,
            'iDur': iDur,
            'iState': iState,
            'iSendTime': misc.Time() + iDur }
        lVoice.append(dVoice)
    
    iNum = 11
    iPlayerID = iPlayerID
    sName = 'test_%s' % iPlayerID
    sOrg = 'test'
    iGrade = random.randint(30, 150)
    iCountry = 1
    iClass = random.choice([
        1,
        2,
        3])
    iSex = random.choice([
        1,
        2])
    iFame = 0
    iShape = random.choice([
        111,
        112,
        121])
    tPhotoAttr = []
    sTittle = 'tittle_%s' % random.randint(100, 1000)
    import prop
    oPlayerIDObj = prop.CPlayerID(iPlayerID)
    oPlayerIDObj.SetShowID(111122)
    oPlayerIDObj.SetPrettyID(8888)
    dPlayer = {
        'iID': iNum,
        'sName': sName,
        'iPlayerID': iPlayerID,
        'oPlayerID': oPlayerIDObj,
        'iGrade': iGrade,
        'iCountry': iCountry,
        'sOrg': sOrg,
        'iRenqi': iFame,
        'lVoice': lVoice,
        'iCls': iClass,
        'sTittle': sTittle,
        'iSex': iSex,
        'iShape': iShape,
        'tPhotoAttr': tPhotoAttr }
    import mdgoodvoicemgr
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oOnePlayerCard = mdgoodvoicemgr.CPlayerGoodVoice(iPlayerID)
    oOnePlayerCard.RefreshDetailInfo(dPlayer)
    oContext.ShowOtherPlayerGoodVoiceDlg(oOnePlayerCard)


def OpenBaoMingDlg():
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oContext.ShowBaoMingDlg()


def ShowRecordVoiceEdit():
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oContext.ShowRecordVoiceEdit()


def MyVoiceData(bEmpty = False, iNum = 2):
    import goodvoiceinterface
    import random
    import misc
    reload(mdmygoodvoice)
    lVoice = []
    sUrlOri = 'testhfl_%s.mp3'
    for iIndex in xrange(iNum):
        sUrl = 'http://et.oa.com:6060/gv/pp/200616/2216/23166385a97b420.dya'
        sSongName = 'hfl_test_%s' % iIndex
        iDur = random.choice([
            60,
            180,
            240])
        iState = random.choice([
            0,
            1])
        dVoice = {
            'sName': sSongName,
            'sUrl': sUrl,
            'iDur': iDur,
            'iState': iState,
            'iSendTime': misc.Time() + iDur }
        lVoice.append(dVoice)
    
    iNo = 0
    iRenqi = 0
    if bEmpty:
        iNo = 1
        iRenqi = 1000
    
    dData = {
        'iID': iNo,
        'iRenqi': iRenqi,
        'lVoice': lVoice }
    LOG('lenVoice:', len(lVoice))
    import goodvoiceinterface
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oMyVoiceDataMgr = oContext.GetMyGoodVoiceData()
    oMyVoiceDataMgr.UpdateData(dData)


def OpenRecord():
    lFlowerRecord = []
    for i in xrange(100):
        dData = {
            'iTime': 1591262050 + i,
            'iPlayerID': 111,
            'sName': '%d' % i,
            'iNum': i }
        lFlowerRecord.append(dData)
    
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oContext.OpenFlowerRecordDlg(lFlowerRecord)


def OpenMain(iCurPage = 10):
    iMaxPage = 100
    iRandomSeed = 300
    lPlayerInfo = []
    iPage = iCurPage
    iPageNum = 13
    iBase = (iCurPage - 1) * iPageNum
    for i in range(iPageNum):
        (iNum, iPlayerID, sName, sOrg) = (i + 1 + iBase, 22222 + i + iBase, 'test_%s' % (2222 + i + iBase), '\xb5L')
        dPlayer = {
            'iPlayerID': iPlayerID,
            'iID': iNum,
            'sName': sName,
            'sOrg': sOrg }
        lPlayerInfo.append(dPlayer)
    
    LOG('OpenMain:', iCurPage, iPage)
    oContext = goodvoiceinterface.GetGoodVoiceContext()
    oGoodDataMgr = oContext.GetGoodVoiceDataMgr()
    oGoodDataMgr.AddPlayerList(lPlayerInfo)
    oContext.OpenGoodVoiceMainDlg()


def SwitchKFJSRank():
    import dlgrank
    dlgrank.g_bTestKFJSData = not (dlgrank.g_bTestKFJSData)


def TestKFJSRank():
    import hero
    import dlgrank
    import misc
    lData = []
    iSize = 10
    for i in range(iSize):
        sOrg = 'ORIG_TEST_%s' % i
        iRank = i + 1
        sServer = 'server_%s' % i % 5
        iServerID = iRank
        if i == 1:
            sOrg = hero.GetProp('sOrg', '\xa8S\xa6\xb3\xc0\xb0\xac\xa3')
            iServerID = misc.GetOrgServerID()
        
        iWinPoint = 1000 - i * 10
        iLevel = i * 10 + 1
        lData.append((i + 1, iRank, iServerID, sServer, sOrg, iWinPoint, iLevel))
    
    dlgrank.Show(106, lData)
