# pycdc 交叉复核产物 · script.fls entry 1803
# co_filename(原始)='script/taiwan/group_fix.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1803.pyc (Python 2.5)

BUILD_MAP = {
    chr(187) + chr(69) + chr(184) + chr(113) + chr(176) + chr(243): TW_NOCHANGE('\xbe\xdb\xd2\xe5\xcc\xc3'),
    chr(171) + chr(67) + chr(192) + chr(115) + chr(176) + chr(243): TW_NOCHANGE('\xc7\xe0\xc1\xfa\xcc\xc3'),
    chr(166) + chr(182) + chr(179) + chr(182) + chr(176) + chr(243): TW_NOCHANGE('\xd6\xec\xc8\xb8\xcc\xc3'),
    chr(165) + chr(213) + chr(170) + chr(234) + chr(176) + chr(243): TW_NOCHANGE('\xb0\xd7\xbb\xa2\xcc\xc3'),
    chr(165) + chr(200) + chr(170) + chr(90) + chr(176) + chr(243): TW_NOCHANGE('\xd0\xfe\xce\xe4\xcc\xc3') }

def RefreshBuildIcon(self, oDataLst):
    import dlggroupbuildnew
    import misc
    self.m_oHeadInfoDict = { }
    for oData in oDataLst:
        iType = oData.GetType()
        sBuildName = oData.GetName()
        iBuildLv = oData.GetLv()
        raise None, None, None, None, None, oData
        iBuildRank = None()
        sUIName = dlggroupbuildnew.NEWTYPE2UINAME[iType]
        oImg = self.GetObject('img_%s' % sUIName)
        sImgName = '%s%d' % (BUILD_MAP.get(sBuildName, sBuildName), max(iBuildRank, 1))
        oImg.SetPath('combdialog4/\xb0\xef\xc5\xc9\xbd\xa8\xd6\xfe/%s.igs' % sImgName)
        oLoc = self.GetObject('loc_%s' % sUIName)
        oHeadInfo = dlggroupbuildnew.CBuildingHeadInfo(self)
        oHeadInfo.SetInfo(sBuildName, iBuildLv)
        oHeadInfo.SetProgress(0, 0)
        (iX, iY) = oLoc.GetPos()
        oHeadInfo.SetPos(iX, iY)
        self.m_oHeadInfoDict[iType] = oHeadInfo
        oHeadInfo.SetLeftUpCB(misc.Functor(self.OnBuildClick, iType))
        oHeadInfo.SetEnterCB(misc.Functor(self.OnBuildEnter, iType))
        oHeadInfo.SetLeaveCB(misc.Functor(self.OnBuildLeave, iType))
        oHotLoc = self.GetObject('hloc_%s' % sUIName)
        oHotLoc.SetEnterCB(misc.Functor(self.OnBuildEnter, iType))
        oHotLoc.SetLeaveCB(misc.Functor(self.OnBuildLeave, iType))
    


def TransUIFunc(dInfoList):
    for dData in dInfoList:
        if dData['sName'] == 'txt_desc':
            dData['sText'] = '1.\xbb\xdd\xadn\xae\xf8\xaf\xd3#CLR3#n$SG#n\xc2I\xa5@\xac\xc9\xb0^\xc4m\xab\xd7\xa9\xce#CLR3#n$Cash#n\xb2{\xaa\xf7'
            for dInfo in dData['lChildren']:
                if dInfo['sName'] == 'txt_desc3':
                    dInfo['sText'] = '2.\xbb\xdd\xadn\xa6b#CLR3#n48\xa4p\xae\xc9#n\xa4\xba\xb1o\xa8\xec#CLR3#n40\xa6W#n\xaa\xb1\xaea\xc5T\xc0\xb3\xa4~\xaf\xe0\xa7\xb9\xa6\xa8\xb3\xd0\xab\xd8'
                
                if dInfo['sName'] == 'txt_desc4':
                    dInfo['sText'] = '3.\xb3\xd0\xab\xd8\xa5\xa2\xb1\xd1\xa4\xa3\xb7|\xaa\xf0\xc1\xd9\xb6O\xa5\xce'
                
                if dInfo['sName'] == 'txt_desc1':
                    dInfo['bShow'] = False
                    continue
            
    
    return dInfoList


def Fix():
    import dlggroupbuildnew
    dlggroupbuildnew.CGroupBuildDlg.RefreshBuildIcon = RefreshBuildIcon
    import combdialog
    combdialog.g_DlgUIUpdateInfo['dialog/group_new/newgroup/groupcreate.dlg'] = TransUIFunc
    combdialog.g_DlgUIUpdateInfo['dialog2/group_new/newgroup/groupcreate.dlg'] = TransUIFunc
    combdialog.g_DlgUIUpdateInfo['dialog4/QDYCFiXSw/newgroup/groupcreate.dlg'] = TransUIFunc
