# pycdc 交叉复核产物 · script.fls entry 106
# co_filename(原始)='script/mxgame/shitu/shitutest.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:53Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_106.pyc (Python 2.5)

import dlgshitu1
import mdshitu1
import shitudefine
g_CShitugTest = None

def GetShituTest():
    global g_CShitugTest
    if not g_CShitugTest:
        g_CShitugTest = CShituTest()
    
    return g_CShitugTest


class CShituTest(object):
    
    def TestFindMastetDlg(self):
        '''
\t\t\xb4M\xaev\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFindMastetDlg()
\t\t'''
        dlgshitu1.ShowFindMasterDlg()
        iRelateTchNum = 1
        iNormalTchNum = 2
        iRelateTchMax = 2
        iTotalTchMax = 5
        dPlayerInfoList = [
            {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_ACTIVE_TYPE: 0,
                shitudefine.KEY_CHUSHI_NUM: 20,
                shitudefine.KEY_MASTER_SCORE: 100,
                shitudefine.KEY_SAME_GROUP: 1,
                shitudefine.KEY_HAS_REQUEST: 0,
                shitudefine.KEY_SORT_SCARE: 125,
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            {
                shitudefine.KEY_PLAYER_ID: 2,
                shitudefine.KEY_ACTIVE_TYPE: 1,
                shitudefine.KEY_CHUSHI_NUM: 21,
                shitudefine.KEY_MASTER_SCORE: 120,
                shitudefine.KEY_SAME_GROUP: 0,
                shitudefine.KEY_HAS_REQUEST: 1,
                shitudefine.KEY_SORT_SCARE: 95,
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            {
                shitudefine.KEY_PLAYER_ID: 3,
                shitudefine.KEY_ACTIVE_TYPE: 0,
                shitudefine.KEY_CHUSHI_NUM: 20,
                shitudefine.KEY_MASTER_SCORE: 100,
                shitudefine.KEY_SAME_GROUP: 1,
                shitudefine.KEY_HAS_REQUEST: 0,
                shitudefine.KEY_SORT_SCARE: 95,
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            {
                shitudefine.KEY_PLAYER_ID: 4,
                shitudefine.KEY_ACTIVE_TYPE: 1,
                shitudefine.KEY_CHUSHI_NUM: 21,
                shitudefine.KEY_MASTER_SCORE: 120,
                shitudefine.KEY_SAME_GROUP: 0,
                shitudefine.KEY_HAS_REQUEST: 0,
                shitudefine.KEY_SORT_SCARE: 1101,
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            {
                shitudefine.KEY_PLAYER_ID: 5,
                shitudefine.KEY_ACTIVE_TYPE: 0,
                shitudefine.KEY_CHUSHI_NUM: 20,
                shitudefine.KEY_MASTER_SCORE: 100,
                shitudefine.KEY_SAME_GROUP: 1,
                shitudefine.KEY_HAS_REQUEST: 0,
                shitudefine.KEY_SORT_SCARE: 1234,
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            {
                shitudefine.KEY_PLAYER_ID: 6,
                shitudefine.KEY_ACTIVE_TYPE: 1,
                shitudefine.KEY_CHUSHI_NUM: 21,
                shitudefine.KEY_MASTER_SCORE: 120,
                shitudefine.KEY_SAME_GROUP: 0,
                shitudefine.KEY_HAS_REQUEST: 0,
                shitudefine.KEY_SORT_SCARE: 44,
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            {
                shitudefine.KEY_PLAYER_ID: 7,
                shitudefine.KEY_ACTIVE_TYPE: 1,
                shitudefine.KEY_CHUSHI_NUM: 21,
                shitudefine.KEY_MASTER_SCORE: 120,
                shitudefine.KEY_SAME_GROUP: 0,
                shitudefine.KEY_HAS_REQUEST: 0,
                shitudefine.KEY_SORT_SCARE: 125,
                shitudefine.KEY_PLAYER_ONLINE: 1 }]
        import avatar
        dExtInfo = {
            1: {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_PLAYER_NAME: '125\xaa\xb1\xaea1',
                shitudefine.KEY_PLAYER_LV: 101,
                shitudefine.KEY_PLAYER_CLASS: 0,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            2: {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_PLAYER_NAME: '95\xaa\xb1\xaea2',
                shitudefine.KEY_PLAYER_LV: 102,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            3: {
                shitudefine.KEY_PLAYER_ID: 3,
                shitudefine.KEY_PLAYER_NAME: '95\xaa\xb1\xaea3',
                shitudefine.KEY_PLAYER_LV: 103,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            4: {
                shitudefine.KEY_PLAYER_ID: 4,
                shitudefine.KEY_PLAYER_NAME: '1101\xaa\xb1\xaea4',
                shitudefine.KEY_PLAYER_LV: 104,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            5: {
                shitudefine.KEY_PLAYER_ID: 5,
                shitudefine.KEY_PLAYER_NAME: '1234\xaa\xb1\xaea5',
                shitudefine.KEY_PLAYER_LV: 105,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            6: {
                shitudefine.KEY_PLAYER_ID: 6,
                shitudefine.KEY_PLAYER_NAME: '44\xaa\xb1\xaea6',
                shitudefine.KEY_PLAYER_LV: 106,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            7: {
                shitudefine.KEY_PLAYER_ID: 7,
                shitudefine.KEY_PLAYER_NAME: '125\xaa\xb1\xaea7',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 } }
        mdshitu1.GetFindMasterModel().SetMasterNum(iRelateTchNum, iNormalTchNum, iRelateTchMax, iTotalTchMax)
        mdshitu1.GetFindMasterModel().SetMasterInfoList(dPlayerInfoList)
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExtInfo)

    
    def TestFindMasterSettingDlg(self):
        '''
\t\t\xb4M\xaev\xb3]\xb8m\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFindMasterSettingDlg()
\t\t'''
        iOnlineType = 1
        iSchoolType = 0
        iSexType = 2
        import dlgshitu1
        dlgshitu1.ShowFindMasterIntentionDlg()
        mdshitu1.GetFindMasterSettingModel().SetConfig(iOnlineType, iSchoolType, iSexType)

    
    def TestShutuDlg(self):
        '''
\t\t\xa6\xac\xae{\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestShutuDlg()
\t\t'''
        dlgshitu1.ShowShoutuDlg()
        import avatar
        iPlayerIDList = [
            1,
            2,
            3,
            4,
            5,
            6,
            7]
        dPlayerInfoDict = {
            1: {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea1',
                shitudefine.KEY_PLAYER_LV: 101,
                shitudefine.KEY_PLAYER_CLASS: 0,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            2: {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea2',
                shitudefine.KEY_PLAYER_LV: 102,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            3: {
                shitudefine.KEY_PLAYER_ID: 3,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea3',
                shitudefine.KEY_PLAYER_LV: 103,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            4: {
                shitudefine.KEY_PLAYER_ID: 4,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea4',
                shitudefine.KEY_PLAYER_LV: 104,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            5: {
                shitudefine.KEY_PLAYER_ID: 5,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea5',
                shitudefine.KEY_PLAYER_LV: 105,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            6: {
                shitudefine.KEY_PLAYER_ID: 6,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea6',
                shitudefine.KEY_PLAYER_LV: 106,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            7: {
                shitudefine.KEY_PLAYER_ID: 7,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea7',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 } }
        mdshitu1.GetShoutuModel().SetTudiIDList(iPlayerIDList)
        mdshitu1.GetShoutuModel().SetExInfo(1, 3, 5, 1)
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dPlayerInfoDict)

    
    def TestShoutuSettingDlg(self):
        '''
\t\t\xa6\xac\xae{\xb3]\xb8m\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestShoutuSettingDlg()
\t\t'''
        iAcceptFlag = 1
        iCurTudiNum = 2
        iRecruitTudi30 = 6
        iHuoYe7 = 1200
        iStatus = 29
        iActive = 1
        dlgshitu1.ShowShoutuSettingDlg()
        mdshitu1.GetShoutuSettingModel().SetConfig(iAcceptFlag, iCurTudiNum, iRecruitTudi30, iHuoYe7, iStatus, iActive)

    
    def TestRequestFileDlg(self):
        '''
\t\t\xae{\xa7\xcc\xa5\xd3\xbd\xd0\xc0\xc9\xae\xd7\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestRequestFileDlg()
\t\t'''
        dlgshitu1.ShowRequestFileDlg()
        iPlayerID = 1
        sGroup = '\xc0\xb0\xac\xa3111'
        (iHuoyue, iGold, iVip) = (0, 0, 1)
        import avatar
        dExInfo = {
            1: {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea1',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 } }
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExInfo)
        mdshitu1.GetRequestFileModel().SetPlayerInfo(iPlayerID, sGroup, iHuoyue, iGold, iVip)

    
    def TestTudiRequestNum(self):
        '''
\t\t\xae{\xa7\xcc\xa5\xd3\xbd\xd0\xbc\xc6\xb6q\xc5\xdc\xa4\xc6
\t\timport shitutest
\t\tshitutest.GetShituTest().TestTudiRequestNum()
\t\t'''
        iIDList = [
            1,
            2,
            3,
            4]
        if not mdshitu1.GetFriendListModel():
            return None

    
    def TestFindMasterRequestState(self):
        '''
\t\t\xb4M\xaev\xa5\xd3\xbd\xd0\xaa\xac\xbaA\xc5\xdc\xa4\xc6
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFindMastetDlg()
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFindMasterRequestState()
\t\t'''
        iMasterID = 1
        mdshitu1.GetFindMasterModel().SetMasterHasRequest(iMasterID)

    
    def TestRelationshipDlg(self):
        '''
\t\t\xaev\xae{\xc3\xf6\xabY\xac\xc9\xad\xb1
\t\timport shitutest
\t\tshitutest.GetShituTest().TestRelationshipDlg()
\t\t'''
        dlgshitu1.ShowRelationshipDlg()
        dTudInfoList = [
            {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_NEAR_POINT: 111,
                shitudefine.KEY_IS_NEAR: 1,
                shitudefine.KEY_IS_MASTER: False },
            {
                shitudefine.KEY_PLAYER_ID: 2,
                shitudefine.KEY_NEAR_POINT: 222,
                shitudefine.KEY_IS_NEAR: 0,
                shitudefine.KEY_IS_MASTER: False }]
        dMasterInfoList = [
            {
                shitudefine.KEY_PLAYER_ID: 3,
                shitudefine.KEY_NEAR_POINT: 333,
                shitudefine.KEY_IS_NEAR: 1,
                shitudefine.KEY_IS_MASTER: True },
            {
                shitudefine.KEY_PLAYER_ID: 4,
                shitudefine.KEY_NEAR_POINT: 444,
                shitudefine.KEY_IS_NEAR: 0,
                shitudefine.KEY_IS_MASTER: True }]
        import avatar
        dExInfo = {
            1: {
                shitudefine.KEY_PLAYER_ID: 1,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea1',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            2: {
                shitudefine.KEY_PLAYER_ID: 2,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea2',
                shitudefine.KEY_PLAYER_LV: 102,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            3: {
                shitudefine.KEY_PLAYER_ID: 3,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea3',
                shitudefine.KEY_PLAYER_LV: 103,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            4: {
                shitudefine.KEY_PLAYER_ID: 4,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea4',
                shitudefine.KEY_PLAYER_LV: 104,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 } }
        mdshitu1.GetRelationshipModel().SetMemberList(dTudInfoList, dMasterInfoList)
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExInfo)

    
    def TestTudiShouyeDlg(self):
        '''
\t\t\xae{\xa7\xcc\xb1\xc2\xb7~\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestTudiShouyeDlg()
\t\t'''
        dlgshitu1.ShowTudiShouyeDlg()
        dTaskInfoList = [
            {
                shitudefine.KEY_TASK_ID: 1000,
                shitudefine.KEY_PLAYER_NAME: '\xb5o\xa7G\xaa\xcc1111',
                shitudefine.KEY_TASK_CUR: 9,
                shitudefine.KEY_TASK_SUM: 20 },
            {
                shitudefine.KEY_TASK_ID: 1001,
                shitudefine.KEY_PLAYER_NAME: '\xb5o\xa7G\xaa\xcc2222',
                shitudefine.KEY_TASK_CUR: 5,
                shitudefine.KEY_TASK_SUM: 5 },
            {
                shitudefine.KEY_TASK_ID: 1000,
                shitudefine.KEY_PLAYER_NAME: '\xb5o\xa7G\xaa\xcc2222',
                shitudefine.KEY_TASK_CUR: 5,
                shitudefine.KEY_TASK_SUM: 20 }]
        iCurRate = 15
        iSumRate = 100
        mdshitu1.GetTudiShouyeModel().SetTudiShouyeInfo(iCurRate, iSumRate, dTaskInfoList)

    
    def TestMasterAssessDlg(self):
        '''
\t\t\xaev\xa4\xf7\xb5\xfb\xbb\xf9\xac\xc9\xad\xb1
\t\timport shitutest
\t\tshitutest.GetShituTest().TestMasterAssessDlg()
\t\t'''
        dlgshitu1.ShowMasterAssessDlg()
        iPlayerID = 1001
        import avatar
        dExInfo = {
            1001: {
                shitudefine.KEY_PLAYER_ID: 1001,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea1',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 } }
        mdshitu1.GetMasterAssessModel().SetPlayerInfo(iPlayerID)
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExInfo)

    
    def TestFriendShituListDlg(self):
        '''
\t\t\xa6n\xa4\xcd\xa6C\xaa\xed\xa4\xa4\xaa\xba\xaa\xba\xaev\xae{\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFriendShituListDlg()
\t\tshitutest.GetShituTest().TestFriendShituListDlgEx()
\t\t'''
        bShowBaiShi = False
        bShowShouTu = False
        iIsChuShi = 1
        dInfoList = [
            {
                shitudefine.KEY_PLAYER_ID: 1001,
                shitudefine.KEY_RELATIONSHIP: 0,
                shitudefine.KEY_IS_CHUSHI: 0 },
            {
                shitudefine.KEY_PLAYER_ID: 1002,
                shitudefine.KEY_RELATIONSHIP: 1,
                shitudefine.KEY_IS_CHUSHI: 0 },
            {
                shitudefine.KEY_PLAYER_ID: 1003,
                shitudefine.KEY_RELATIONSHIP: 6,
                shitudefine.KEY_IS_CHUSHI: 0 },
            {
                shitudefine.KEY_PLAYER_ID: 1004,
                shitudefine.KEY_RELATIONSHIP: 6,
                shitudefine.KEY_IS_CHUSHI: 1 },
            {
                shitudefine.KEY_PLAYER_ID: 1005,
                shitudefine.KEY_RELATIONSHIP: 8,
                shitudefine.KEY_IS_CHUSHI: 0 },
            {
                shitudefine.KEY_PLAYER_ID: 1006,
                shitudefine.KEY_RELATIONSHIP: 7,
                shitudefine.KEY_IS_CHUSHI: 0 },
            {
                shitudefine.KEY_PLAYER_ID: 1007,
                shitudefine.KEY_RELATIONSHIP: 8,
                shitudefine.KEY_IS_CHUSHI: 1 }]
        iIdentity = shitudefine.IDENTITY_TUDI_IN
        for dInfo in dInfoList:
            if dInfo[shitudefine.KEY_RELATIONSHIP] in (shitudefine.RELATION_TUDI, shitudefine.RELATION_TUDI_NEAR):
                iIdentity = shitudefine.IDENTITY_SHIFU
                break
                continue
            if dInfo[shitudefine.KEY_RELATIONSHIP] in (shitudefine.RELATION_SHIFU, shitudefine.RELATION_SHIFU_NEAR):
                if iIsChuShi:
                    iIdentity = shitudefine.IDENTITY_TUDI_OUT
                else:
                    iIdentity = shitudefine.IDENTITY_TUDI_IN
            iIsChuShi
        
        LOG_DEBUG('>>bShowBaiShi>', bShowBaiShi)
        LOG_DEBUG('>>bShowShouTu>', bShowShouTu)
        LOG_DEBUG('>>iIdentity>', iIdentity)
        oModel = mdshitu1.GetFriendListModel()
        oModel.SetIsShowBaiShi(bShowBaiShi)
        oModel.SetIsShowShouTu(bShowShouTu)
        oModel.SetIdentity(iIdentity)
        oModel.SetTongMenList(dInfoList)

    
    def TestFriendShituListDlgEx(self):
        '''
\t\t\xa6n\xa4\xcd\xa6C\xaa\xed\xa4\xa4\xaa\xba\xaa\xba\xaev\xae{\xac\xc9\xad\xb1\xb4\xfa\xb8\xd5 \xc3B\xa5~\xabH\xae\xa7
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFriendShituListDlgEx()
\t\t'''
        import avatar
        dExInfo = {
            1001: {
                shitudefine.KEY_PLAYER_ID: 1001,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea1\xaev\xa4\xf7',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            1002: {
                shitudefine.KEY_PLAYER_ID: 1002,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea2\xaev\xa5S',
                shitudefine.KEY_PLAYER_LV: 102,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            1003: {
                shitudefine.KEY_PLAYER_ID: 1003,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea3\xae{\xa7\xcc',
                shitudefine.KEY_PLAYER_LV: 45,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            1004: {
                shitudefine.KEY_PLAYER_ID: 1004,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea4\xae{\xa7\xcc\xa5X\xaev',
                shitudefine.KEY_PLAYER_LV: 54,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            1005: {
                shitudefine.KEY_PLAYER_ID: 1005,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea5\xbf\xcb\xb6\xc7\xae{\xa7\xcc',
                shitudefine.KEY_PLAYER_LV: 35,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            1006: {
                shitudefine.KEY_PLAYER_ID: 1006,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea6\xbf\xcb\xb6\xc7\xaev\xa4\xf7',
                shitudefine.KEY_PLAYER_LV: 135,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            1007: {
                shitudefine.KEY_PLAYER_ID: 1007,
                shitudefine.KEY_PLAYER_NAME: '\xbf\xcb\xb6\xc7\xae{\xa7\xcc\xa5X\xaev',
                shitudefine.KEY_PLAYER_LV: 135,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 } }
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExInfo)

    
    def TestShifuShouyeDlg(self):
        '''
\t\t\xaev\xa4\xf7\xb1\xc2\xb7~\xac\xc9\xad\xb1
\t\timport shitutest
\t\tshitutest.GetShituTest().TestFriendShituListDlg()
\t\tshitutest.GetShituTest().TestFriendShituListDlgEx()
\t\tshitutest.GetShituTest().TestShifuShouyeDlg()
\t\tshitutest.GetShituTest().TestRefresMasterShouyeInfo()
\t\t'''
        dlgshitu1.ShowShifuShouyeDlg()
        import avatar
        dExtInfo = {
            1003: {
                shitudefine.KEY_PLAYER_ID: 1003,
                shitudefine.KEY_PLAYER_NAME: '123123',
                shitudefine.KEY_PLAYER_LV: 45,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 } }
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExtInfo)

    
    def TestRefresMasterShouyeInfo(self):
        '''
\t\t\xaev\xa4\xf7\xb1\xc2\xb7~\xabH\xae\xa7
\t\timport shitutest
\t\tshitutest.GetShituTest().TestRefresMasterShouyeInfo()
\t\t'''
        iPlayerID = 1003
        iDegree = 15
        iDegreeMax = 100
        iIsAllot = 1
        iNear = 1000
        dTaskInfoDict = {
            1000: {
                shitudefine.KEY_TASK_CUR: 5,
                shitudefine.KEY_TASK_SUM: 20,
                shitudefine.KEY_TASK_ID: 1000 },
            1001: {
                shitudefine.KEY_TASK_CUR: 20,
                shitudefine.KEY_TASK_SUM: 20,
                shitudefine.KEY_TASK_ID: 1001 } }
        mdshitu1.GetMasterShouyeModel().SetTudiShouyeInfo(iPlayerID, iDegree, iDegreeMax, iIsAllot, dTaskInfoDict, iNear)

    
    def TestShouyeTipsDlg(self):
        '''
\t\t\xb1\xc2\xb7~\xabH\xae\xa7\xac\xc9\xad\xb1
\t\timport shitutest
\t\tshitutest.GetShituTest().TestShouyeTipsDlg()
\t\t'''
        iPlayerID = 1003
        iDegree = 15
        iDegreeMax = 100
        iIsAllot = 1
        dTaskInfoDict = {
            1000: {
                shitudefine.KEY_TASK_CUR: 5,
                shitudefine.KEY_TASK_SUM: 20,
                shitudefine.KEY_TASK_ID: 1000 },
            1001: {
                shitudefine.KEY_TASK_CUR: 20,
                shitudefine.KEY_TASK_SUM: 20,
                shitudefine.KEY_TASK_ID: 1001 } }
        dlgshitu1.ShouShouyeTipsDlg(iPlayerID, None)
        mdshitu1.GetMasterShouyeModel().SetTudiShouyeInfo(iPlayerID, iDegree, iDegreeMax, iIsAllot, dTaskInfoDict)

    
    def TestChushiListDlg(self):
        '''
\t\t\xa5X\xaev\xa6C\xaa\xed\xac\xc9\xad\xb1
\t\timport shitutest
\t\tshitutest.GetShituTest().TestChushiListDlg()
\t\t'''
        import dlgshitu1
        dlgshitu1.ShowChushiDialog()
        dInfoList = [
            {
                shitudefine.KEY_PLAYER_ID: 1001,
                shitudefine.KEY_ASSESS_GRADE: 1,
                shitudefine.KEY_REWARD_NUM: 1,
                shitudefine.KEY_ASSESS_DEGREE: 20 },
            {
                shitudefine.KEY_PLAYER_ID: 1002,
                shitudefine.KEY_ASSESS_GRADE: 2,
                shitudefine.KEY_REWARD_NUM: 0,
                shitudefine.KEY_ASSESS_DEGREE: 50 },
            {
                shitudefine.KEY_PLAYER_ID: 1003,
                shitudefine.KEY_ASSESS_GRADE: 3,
                shitudefine.KEY_REWARD_NUM: 3,
                shitudefine.KEY_ASSESS_DEGREE: 90 },
            {
                shitudefine.KEY_PLAYER_ID: 1004,
                shitudefine.KEY_ASSESS_GRADE: 4,
                shitudefine.KEY_REWARD_NUM: 4,
                shitudefine.KEY_ASSESS_DEGREE: 100 }]
        import avatar
        dExInfo = {
            1001: {
                shitudefine.KEY_PLAYER_ID: 1001,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea1',
                shitudefine.KEY_PLAYER_LV: 107,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 },
            1002: {
                shitudefine.KEY_PLAYER_ID: 1002,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea2',
                shitudefine.KEY_PLAYER_LV: 102,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            1003: {
                shitudefine.KEY_PLAYER_ID: 1003,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea3',
                shitudefine.KEY_PLAYER_LV: 103,
                shitudefine.KEY_PLAYER_CLASS: 2,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 1 },
            1004: {
                shitudefine.KEY_PLAYER_ID: 1004,
                shitudefine.KEY_PLAYER_NAME: '\xaa\xb1\xaea4',
                shitudefine.KEY_PLAYER_LV: 104,
                shitudefine.KEY_PLAYER_CLASS: 1,
                shitudefine.KEY_PLAYER_ICON: 1,
                shitudefine.KEY_PLAYER_AVATAR: avatar.PhotoArr2Int(avatar.GetHeroPhoto()),
                shitudefine.KEY_PLAYER_ONLINE: 0 } }
        mdshitu1.GetChushiListModel().SetChushiInfoList(dInfoList)
        mdshitu1.GetPlayerExInfoModel().SetPlayerExInfoDict(dExInfo)
