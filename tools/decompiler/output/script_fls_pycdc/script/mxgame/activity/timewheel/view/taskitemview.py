# pycdc 交叉复核产物 · script.fls entry 4842
# co_filename(原始)='script/mxgame/activity/timewheel/view/taskitemview.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:02Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4842.pyc (Python 2.5)

import combdialog
import interface
import timewheeldefine
import ui
import pubtimeformat
import monsterdata
import avatar
import wheeltimedata
UI_NAMEKEY = ('loc_bg', 'frame_bg', 'txt_taskname', 'img_task')
UI_OTHERS = ('txt_desc1', 'txt_desc2', 'loc_img_status')
UI_DISCOUNT = ('txt_price_ori', 'img_redline', 'txt_price_cur', 'img_discount')
STATE_2_CONFIG = {
    timewheeldefine.TASKITEM_NORMAL: {
        'txt_desc1': 'sDurable' },
    timewheeldefine.TASKITEM_WEITUO: {
        'loc_img_status': 'tStatusPath' },
    timewheeldefine.TASKITEM_WEITUO_OTHERS: {
        'txt_desc1': 'sDurable',
        'txt_desc2': 'sDesc2' },
    timewheeldefine.TASKITEM_GETWEITUO: {
        'txt_desc1': 'sDurable',
        'txt_desc2': 'sDesc2' } }
UI2PROP_CONFIG = {
    'txt_taskname': 'sName',
    'img_task': 'iIcon',
    'txt_desc1': 'sDurable',
    'loc_img_status': 'tStatusPath',
    'txt_desc2': 'sDesc2',
    'txt_price_ori': 'sOriPrice',
    'img_redline': 'bRedLine',
    'txt_price_cur': 'sCurPrice',
    'img_discount': 'bDiscount' }

class CTaskItemView(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, onClickCallBack):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/shiguangzhilun/taskitem_new.dlg')
        self.m_onClickCallBack = onClickCallBack
        self.m_oDelegateList = []
        self.m_iType = 0
        self.m_dData = { }
        self.m_oIcon = None
        self.m_oFrament = None
        self.m_oStateIcon = None

    
    def UpdateInfo(self, dData):
        dOldData = self.m_dData
        if self.m_dData == dData:
            return None
        
        self.m_dData = dData
        self.m_iType = dData['iType']
        self.UpdateText()
        self.UpdateIcon(dOldData)
        self.UpdateOtherUI(dOldData)
        self.UpdateDiscountUI()
        self.UpdateWeekCard()

    
    def UpdateText(self):
        self.GetObject('txt_taskname').SetText(self.m_dData.get('sName', ''))

    
    def UpdateIcon(self, dOldData):
        dData = self.m_dData
        iIconID = dData['iIcon']
        if dOldData.get('iIcon') != iIconID:
            (x, y) = self.GetObject('img_task').GetPos()
            if monsterdata.IsMonster(iIconID):
                self.m_oIcon = ui.CImage(self, 'photo/summon/%04d.igs' % 4005, 'misc')
                self.m_oFrament = ui.CImage(self.m_oIcon, 'combdialog4/\xd4\xd3\xcd\xbc/\xcb\xe9\xc6\xac\xbd\xc7\xb1\xea44.png', interface.UIPath)
                interface.TopRight(self.m_oFrament)
            else:
                self.m_oIcon = ui.CImage(self, 'item44/%d.igs' % iIconID, 'item')
                self.m_oFrament = None
            self.m_oIcon.SetPos(x, y)
        

    
    def UpdateOtherUI(self, dOldData):
        dData = self.m_dData
        for sUIName in UI_OTHERS:
            sPropKey = UI2PROP_CONFIG[sUIName]
            bShow = sPropKey in dData
            if not self.GetObject(sUIName):
                continue
            
            self.SetShowObject(sUIName, bShow)
            if sPropKey == 'tStatusPath':
                if not bShow:
                    self.m_oStateIcon = None
                elif dOldData.get(sPropKey) != dData[sPropKey]:
                    self.CreateStatusIcon(dData[sPropKey])
                
            bShow
            if bShow and sPropKey not in ('loc_img_status',):
                self.GetObject(sUIName).SetText(dData[sPropKey])
                continue
        

    
    def UpdateDiscountUI(self):
        dData = self.m_dData
        for sUIName in UI_DISCOUNT:
            sPropKey = UI2PROP_CONFIG[sUIName]
            sValue = dData.get(sPropKey, '')
            bShow = None if sValue else False
            self.SetShowObject(sUIName, bShow)
            if not self.GetObject(sUIName):
                LOG('not exist sUIName:', sUIName)
                continue
            
            if bShow and sUIName not in ('img_redline', 'img_discount'):
                self.GetObject(sUIName).SetText(sValue)
                continue
        

    
    def UpdateWeekCard(self):
        dData = self.m_dData
        self.SetShowObject('img_weekcard', False)
        if 'iWeekCardHaveBuy' in dData:
            bHaveWeekCard = dData['iWeekCardHaveBuy'] == 1
            bShowGray = dData['bWeekCardShowGray']
            self.SetShowObject('img_weekcard', bHaveWeekCard)
            sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xd4\xc2\xbf\xa8.png'
            if bShowGray:
                sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xd4\xc2\xbf\xa8-\xbb\xd2.png'
            
            self.GetObject('img_weekcard').SetPath(sPath)
        else:
            self.SetShowObject('img_weekcard', False)
        self.GetObject('img_weekcard').SetZ(10)

    
    def CreateStatusIcon(self, tPath):
        (sPath, sPacket) = tPath
        self.m_oStateIcon = ui.CImage(self, sPath, sPacket)
        (x, y) = self.GetObject('loc_img_status').GetPos()
        self.m_oStateIcon.SetPos(x, y)

    
    def GetType(self):
        return self.m_iType

    
    def SetSelect(self, bSelect):
        self.GetObject('frame_bg').GetImage(0, 0).SetFrame(bSelect)
        if self.m_dData.get('bGray', False) and not bSelect:
            self.SetGray()
        

    
    def SetGray(self):
        if not interface.IsStyle1() and not interface.IsStyle2():
            self.GetObject('txt_taskname').SetColor(6513507)
            self.GetObject('txt_desc1').SetColor(6513507)
        
        self.m_oIcon.SetGrey()

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        if self.m_onClickCallBack:
            self.m_onClickCallBack(self.m_iType)
        



class CWeekCardItemView(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, onClickCallBack):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/shiguangzhilun/weekcard_item.dlg')
        self.m_onClickCallBack = onClickCallBack
        self.m_iType = 0
        self.m_dData = { }
        self.m_oIcon = None
        self.m_oFrament = None
        self.m_oStateIcon = None

    
    def UpdateInfo(self, dData):
        dOldData = self.m_dData
        if self.m_dData == dData:
            return None
        
        self.m_dData = dData
        self.m_iType = dData['iType']
        self.UpdateText()
        self.UpdateIcon(dOldData)
        self.UpdateWeekCard()

    
    def UpdateText(self):
        iLevel = self.m_dData['iLevel']
        iMaxLevel = self.m_dData['iMaxLevel']
        if iLevel > 0 and iMaxLevel > 1:
            dIntByDesc = {
                1: '\xa2\xb9',
                2: '\xa2\xba',
                3: '\xa2\xbb',
                4: '\xa2\xbc',
                5: '\xa2\xbd',
                6: '\xa2\xbe',
                7: '\xa2\xbf',
                8: '\xa2\xc0',
                9: '\xa2\xc1' }
            sName = '%s%s' % (self.m_dData['sName'], dIntByDesc.get(iLevel, ''))
        else:
            sName = self.m_dData['sName']
        self.GetObject('txt_taskname').SetText(sName)
        self.GetObject('txt_price').SetText(str(self.m_dData['iPrice']))

    
    def UpdateIcon(self, dOldData):
        dData = self.m_dData
        iIconID = dData['iIcon']
        if dOldData.get('iIcon') != iIconID:
            (x, y) = self.GetObject('img_wc').GetPos()
            if monsterdata.IsMonster(iIconID):
                self.m_oIcon = ui.CImage(self, 'photo/summon/%04d.igs' % 4005, 'misc')
                self.m_oFrament = ui.CImage(self.m_oIcon, 'combdialog4/\xd4\xd3\xcd\xbc/\xcb\xe9\xc6\xac\xbd\xc7\xb1\xea44.png', interface.UIPath)
                interface.TopRight(self.m_oFrament)
            else:
                self.m_oIcon = ui.CImage(self, 'item44/%d.igs' % iIconID, 'item')
                self.m_oFrament = None
            self.m_oIcon.SetPos(x, y)
        

    
    def UpdateWeekCard(self):
        dData = self.m_dData
        bHaveWeekCard = dData['iHaveBuy'] == 1
        self.SetShowObject('img_weekcard', bHaveWeekCard)
        self.SetShowObject('btn_time', bHaveWeekCard)
        self.SetShowObject('tips_time', bHaveWeekCard)
        self.SetPriceShow(not bHaveWeekCard)
        self.GetObject('img_weekcard').SetZ(10)
        sTime = pubtimeformat.MakeTimeYearSecD(dData['iEndTime'])
        iLeftGetDay = dData['iLeftGetDay']
        iTodayLeft = None if dData['iTodayLeft'] else 1
        if self.m_iType == timewheeldefine.TIMEWHEEL_QUICKBAOTU:
            iTodayLeft = 1
        
        iMaxTime = dData['iWeekCardMax']
        if not iMaxTime:
            iMaxTime = 0
        
        iLevel = dData['iLevel']
        iMaxTime = None if iLevel else iMaxTime
        sText = '\xa4\xb5\xa4\xe9\xbb\xe2\xa8\xfa\xa4\xeb\xa5d\xa1G%s/1\xa1]\xa5i\xc0\xf2\xb1o%s\xa6\xb8\xa5[\xb3t\xa1^' % (iTodayLeft, iMaxTime)
        sText += '#r\xa4\xeb\xa5d\xb3\xd1\xbel\xa6\xb8\xbc\xc6\xa1G%d' % iLeftGetDay
        sText += '#r\xa4\xeb\xa5d\xab\xf9\xc4\xf2\xae\xc9\xb6\xa1\xa1G#Y%s#n' % sTime
        self.GetObject('tips_time').SetTips(sText)

    
    def GetType(self):
        return self.m_iType

    
    def SetSelect(self, bSelect):
        self.GetObject('frame_bg').GetImage(0, 0).SetFrame(bSelect)

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        if self.m_onClickCallBack:
            self.m_onClickCallBack(self.m_iType)
        

    
    def SetPriceShow(self, bShow):
        self.SetShowObject('txt_price', bShow)
        self.SetShowObject('img_sg', bShow)



class CPublishTaskItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, oCheckCB, oSelectCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/shiguangzhilun/taskitem_new2.dlg')
        self.m_oIcon = None
        self.m_iType = 0
        self.m_bCheck = False
        self.m_bSelect = False
        self.m_oCheckCB = oCheckCB
        self.m_oSelectCB = oSelectCB

    
    def UpdateItem(self, dInfo):
        global SetPos
        self.m_iType = dInfo.get('iType', 0)
        self.SetSelect(dInfo.get('bSelect', False))
        self.m_bCheck = dInfo.get('bCheck', False)
        self.GetObject('btn_click').SetSelect(self.m_bCheck)
        self.m_oIcon = ui.CImage(self, 'item44/%d.igs' % dInfo['iIcon'], 'item')
        (iX, iY) = self.GetObject('img_task').GetPos()
        SetPos = self.m_oIcon
        None(iX, iY)
        self.GetObject('txt_taskname').SetText(dInfo.get('sName', ''))
        self.SetShowObject('img_yueka', dInfo.get('bHaveMonthCard', False))
        bShowGray = dInfo.get('bWeekCardShowGray', False)
        sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xd4\xc2\xbf\xa8.png'
        if bShowGray:
            sPath = 'combdialog3/\xd4\xd3\xcd\xbc/\xbd\xc7\xb1\xea/\xd4\xc2\xbf\xa8-\xbb\xd2.png'
        
        self.GetObject('img_yueka').SetPath(sPath)
        self.GetObject('img_yueka').SetZ(10)

    
    def LeftUp(self):
        if not self.m_bSelect:
            self.SetSelect(True)
            self.m_oSelectCB(self.m_iType)
        

    
    def LeftDown(self):
        pass

    
    def GetType(self):
        return self.m_iType

    
    def UpdateCheck(self):
        bCheck = not (self.m_bCheck)
        self.m_bCheck = bCheck
        self.m_oCheckCB(self.m_iType, self.m_bCheck)

    
    def SetSelect(self, bSelect):
        self.m_bSelect = bSelect
        self.GetObject('frame_bg').GetImage(0, 0).SetFrame(bSelect)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.UpdateCheck()
        



class CFriendOrderItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, oSelectCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/shiguangzhilun/nonefriendnew.dlg')
        self.m_oAvator = None
        self.m_iId = 0
        self.m_bSelect = False
        self.m_oSelectCB = oSelectCB

    
    def UpdateItem(self, dInfo):
        self.m_iId = dInfo.get('iPlayerID', 0)
        self.m_bSelect = dInfo.get('bSelect', False)
        self.GetObject('btn_click').SetSelect(self.m_bSelect)
        self.CreateActerPhotoIcon(dInfo['lstPhoto'])
        self.GetObject('text_name').SetText(dInfo.get('sName', ''))

    
    def CreateActerPhotoIcon(self, lstOrderPhoto):
        self.m_oAvator = avatar.GetSmallImgBy4Int(self.GetObject('loc_touxiang'), long(lstOrderPhoto[0]), long(lstOrderPhoto[1]), long(lstOrderPhoto[2]), long(lstOrderPhoto[3]), 1, 0.72, iPlayerID = self.m_iId)

    
    def UpdateSelect(self):
        bSelect = not (self.m_bSelect)
        self.GetObject('btn_click').SetSelect(bSelect)
        self.m_bSelect = bSelect
        self.m_oSelectCB(self.m_iId, self.m_bSelect)

    
    def OnMessage(self, iMsgID):
        if iMsgID == 1:
            self.UpdateSelect()
        



class CTakeBackItem(combdialog.CCombSubWnd):
    
    def __init__(self, oParent, oSelectCB):
        combdialog.CCombSubWnd.__init__(self, oParent, 'dialog/shiguangzhilun/taskitem_new4.dlg')
        self.m_oIcon = None
        self.m_iType = 0
        self.m_oSelectCB = oSelectCB
        self.SetIgnoreEsc(True)

    
    def UpdateInfo(self, dData):
        iType = dData['iType']
        iIconID = dData['iIcon']
        sName = dData['sName']
        iStorageNum = dData['iStorageNum']
        iCanTakeBackLoopNum = dData['iCanTakeBackLoopNum']
        bCanTakeBack = dData['bCanTakeBack']
        self.GetObject('txt_taskname').SetText(sName)
        iTaskType = wheeltimedata.GetTakeBackeDataByTaskType(iType)
        if iTaskType == timewheeldefine.TASK_TYPE_NUM:
            sDesc = '\xb7\xed\xabe\xc0x\xb3\xc6\xa1G%d\xa6\xb8' % iStorageNum
            sCanBackDesc = '\xa5i\xb0l\xa6^\xa1G%d\xa6\xb8' % iCanTakeBackLoopNum
        else:
            sDesc = '\xb7\xed\xabe\xc0x\xb3\xc6\xa1G%d\xc0\xf4' % iStorageNum
            sCanBackDesc = '\xa5i\xb0l\xa6^\xa1G%d\xc0\xf4' % iCanTakeBackLoopNum
        self.GetObject('txt_desc2').SetText(sCanBackDesc)
        self.GetObject('txt_desc1').SetText(sDesc)
        self.SetShowObject('img_zhuihui', bCanTakeBack)
        self.GetObject('img_zhuihui').SetZ(1)
        self.UpdateIcon(iIconID)
        self.SetType(iType)

    
    def SetType(self, iType):
        self.m_iType = iType

    
    def GetType(self):
        return self.m_iType

    
    def UpdateIcon(self, iIconID):
        (iX, iY) = self.GetObject('img_task').GetPos()
        self.m_oIcon = ui.CImage(self, 'item44/%d.igs' % iIconID, 'item')
        self.m_oIcon.SetPos(iX, iY)

    
    def LeftDown(self):
        pass

    
    def LeftUp(self):
        if self.m_oSelectCB:
            self.m_oSelectCB(self.m_iType)
        

    
    def SetSelect(self, bSelect):
        self.GetObject('frame_bg').GetImage(0, 0).SetFrame(bSelect)
