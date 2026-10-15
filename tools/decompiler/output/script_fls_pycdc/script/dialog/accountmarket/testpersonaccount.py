# pycdc 交叉复核产物 · script.fls entry 3100
# co_filename(原始)='script/dialog/accountmarket/testpersonaccount.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:58Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3100.pyc (Python 2.5)

import dlgpersonaccout
import mdpersonaccount
import misc
import testbaseobj

class CTestFunc(testbaseobj.CTestBase):
    
    def TestS2CRoleList(cls):
        '''
\t\tmork function
\t\tdef S2CRoleList(netobj):

\t\t\tiNow = misc.GetServerCurrentTime()
\t\t\tiPointCard = netobj.UnpackInt(4)  # \xbe\xd4\xb7\xf9\xc2I\xbc\xc6
\t\t\tiFee = netobj.UnpackInt(4)  # \xa4\xe2\xc4\xf2\xb6O
\t\t\tiHasSubscribed = netobj.UnpackInt(1) # \xacO\xa7_\xa4w\xb8g\xadq\xbe\\\xb9L\xa4\xe1\xabH\xae\xa7
\t\t\tplayerData = []
\t\t\twhile True:
\t\t\t\tplayerID = netobj.UnpackInt(4)  # ID
\t\t\t\tif playerID == 0:
\t\t\t\t\tbreak
\t\t\t\tplayerGrade = netobj.UnpackInt(1)  # \xb5\xa5\xaf\xc5
\t\t\t\tplayerClass = netobj.UnpackInt(1)  # \xc2\xbe\xb7~
\t\t\t\tplayerTime = netobj.UnpackInt(4)  # \xaei\xa5\xdc\xb4\xc1\xb3\xd1\xbel\xae\xc9\xb6\xa1
\t\t\t\tplayerPrice = netobj.UnpackInt(4)  # \xbb\xf9\xae\xe6
\t\t\t\tplayerUpTime = netobj.UnpackInt(4)  # \xafu\xa5\xbf\xbaI\xa6\xdc\xb3\xd1\xbel\xae\xc9\xb6\xa1
\t\t\t\tplayerFeiSheng = neto=5q
1/><4\x161+wnv\x7f\x7f|\x7f\xf2\xe7\xf5\x1f\xe3\x8f\xf8\x8c\x7fo\xfe\x18\xf7\x0c\xf9\xec\xf2\xe7\xf5\x1f\x7fn\xfe\x18\xfb\xfc\xf8\xe6\xf3\xa3\xf2\xe7\xf5\x1f\x7fm\xfe\x18\xf8\xe6\xf3\xa3\xf2\xe7\xf5\x1fUVVVV/3>&:-\x0c:-):-\x7fb\x7f}\xed\xee\xfa\x1f\xf5\xa7\xe5.}UVVVV/3>&:-\x1b>+>q>//:1;ww/3>&:-\x16\x1bs\x7f,+-w/3>&:-\x18->;:vs\x7f,+-w/3>&:-\x1c3>,,vs\x7f/3>&:-\x0b62:\x7ft\x7f6\x110(s\x7f,+-w/3>&:-\x0f-6<:vs\x7f/3>&:-
/\x0b62:\x7ft\x7f6\x110(s\x7f/3>&:-\x19:6\x0c7:18s/3>&:-\x0c:-):-vvUUVVV/3>&:-\x1b>+>q>//:1;wwjjjnmos,+-wnmovs,+-wnvs6\x110(\x7ft\x7fiouioumks,+-wgggvs6\x110(\x7ft\x7fiouioumjs\x7fos\x7f}\xed\xee\xfa\x1f\xf5\xa7\xe5.}vvUVVV/3>&:-\x1b>+>q>//:1;wwjjjnmns,+-wnmnvs,+-wmvs6\x110(\x7ft\x7fiouioumks,+-wgggvs6\x110(\x7ft\x7fiouioumjs\x7fns\x7f}\xed\xee\xfa\x1f\xf5\xa7\xe5.}vvUUVVV/3>&:-\x1b>+>q>//:1;wwjjjnmms,+-wnmmvs,+-wlvs6\x110(\x7ft\x7fiouioumks,+-wgggvs6\x110(\x7ft\x7fiouioumjs\x7fms\x7f}\xed\xee\xfa\x1f\xf5\xa7\xe5.}vvUVVV;38/:-,01><<0*+q\x0c70(\x0c(6+<7wvUVVV0\x120;:3\x7fb\x7f2;/:-,01><<0*1+q\x18:+\x0f:-,01\x1e<<0*1+\x120;:3wvUVVV0\x120;:3q\xb2\x84\x95\xb3\x8e\x8d\x84\xad\x88\x92\x95\xc9\x91\x8d\x80\x98\x84\x93\xa5\x80\x95\x80\xc8\xeb\xe8\xe8\xe8\x8e\xac\x8e\x85\x84\x8d\xcf\xb2\x84\x95\xb4\x8f\x88\x8e\x8f\xb1\x8e\x88\x8f\x95\xc9\x88\xb1\x8e\x88\x8f\x95\xa2\x80\x93\x85\xc8\xeb\xe8\xe8\xe8\x83\xa9\x80\x92\xb2\x94\x83\x92\x82\x93\x88\x83\x84\x85\xc1\xdc\xc1\x88\xa9\x80\x92\xb2\x94\x83\x92\x82\x93\x88\x83\x84\x85\xc1\xdc\xdc\xc1\xd0\xeb\xe8\xe8\xe8\x8e\xac\x8e\x85\x84\x8d\xcf\xb2\x84\x95\xb2\x94\x83\x92\x82\x93\x88\x83\x84\xc9\x83\xa9\x80\x92\xb2\x94\x83\x92\x82\x93\x88\x83\x84\x85\xc8\xeb\xe8\xe8\xe8\x8e\xac\x8e\x85\x84\x8d\xcf\xb2\x84\x95\xa7\x84\x84\xc9\x88\xa7\x84\x84\xc8\xeb\xe8\xe8'''
        dlgpersonaccout.ShowMarketMainSwitch()
        iPointCard = 88888
        iFee = 666
        iHasSubscribed = 1
        iNow = misc.GetServerCurrentTime()
        playerData = []
        playerData.append((555120, str(120), str(1), iNow + 86400, str(888), iNow + 90000, 0, 3101))
        playerData.append((555121, str(121), str(2), iNow + 86400, str(888), iNow + 90000, 1, 33564))
        playerData.append((555122, str(122), str(3), iNow + 79200, str(888), iNow + 90000, 2, 33554))
        playerData.append((555122, str(122), str(3), iNow + 79200, str(888), iNow + 90000, 2, 30001))
        playerData.append((555122, str(122), str(3), iNow + 79200, str(888), iNow + 90000, 2, 33564))
        oModel = mdpersonaccount.GetPersonAccountModel()
        oModel.SetRoleList(playerData)
        oModel.SetUnionPoint(iPointCard)
        bHasSubscribed = iHasSubscribed == 1
        None.SetSubscribe(bHasSubscribed)
        oModel.SetFee(iFee)

    TestS2CRoleList = classmethod(TestS2CRoleList)
