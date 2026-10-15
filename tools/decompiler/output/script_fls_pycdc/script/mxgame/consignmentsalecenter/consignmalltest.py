# pycdc 交叉复核产物 · script.fls entry 3460
# co_filename(原始)='script/mxgame/consignmentsalecenter/consignmalltest.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3460.pyc (Python 2.5)

import consignmalldefines
import mdconsignmallbuy
import netconsignmall
import random
import usermacro
SKILLCONFIG = {
    consignmalldefines.SKILLTYPE_COOKING: {
        'iID': (1114,),
        'iRange': (50, 89) },
    consignmalldefines.SKILLTYPE_MAKE: {
        'iID': (1111, 1112, 1113),
        'iRange': (50, 89) },
    consignmalldefines.SKILLTYPE_CRAFT: {
        'iID': (1117,),
        'iRange': (50, 89) },
    consignmalldefines.SKILLTYPE_FURNISH: {
        'iID': (1116,),
        'iRange': (50, 89) },
    consignmalldefines.SKILLTYPE_FM: {
        'iID': (2008, 2009, 2010, 2011, 2012, 2013, 2015, 2028),
        'iRange': (1, 5) } }
SKILLMAP = {
    '\xa4u\xc3\xc0': consignmalldefines.SKILLTYPE_CRAFT,
    '\xb3\xc3\xa8\xe3': consignmalldefines.SKILLTYPE_FURNISH,
    '\xb2i\xb6\xb9': consignmalldefines.SKILLTYPE_COOKING,
    '\xa5\xb4\xb3y': consignmalldefines.SKILLTYPE_MAKE,
    '\xaa\xfe\xc5]': consignmalldefines.SKILLTYPE_FM }

def TestSkill(sSkillType, iNum):
    if sSkillType in SKILLMAP:
        iSkillType = SKILLMAP[sSkillType]
    else:
        usermacro.PROMPT_MSG('\xb0\xd1\xbc\xc6\xa6\xb3\xbb~\xa1I\xa1I\xa5u\xa4\xe4\xab\xf9\xbf\xe9\xa4J%s\xa4\xa4\xaa\xba\xa4@\xad\xd3' % str(SKILLMAP.keys()))
        return None
    oModel = mdconsignmallbuy.GetBuyModel()
    oShelf = oModel.GetSkillShelfBySkillType(iSkillType)
    iShelfVersion = oShelf.GetShelfVersion()
    if iSkillType == consignmalldefines.SKILLTYPE_COOKING:
        lstPlayersSkill = []
        for idx in xrange(iNum):
            dConfig = SKILLCONFIG[iSkillType]
            iOwner = 100001 + idx
            iPrice = 450 * random.randint(50, 250) / 100
            iSkillLevel = random.randint(dConfig['iRange'][0], dConfig['iRange'][1])
            iRefPrice = 450
            lstCook = [
                11,
                12]
            lstPlayersSkill.append([
                iOwner,
                iPrice,
                iSkillLevel,
                iRefPrice,
                lstCook])
        
        netconsignmall.OnAllCookSkill(iShelfVersion, lstPlayersSkill)
    else:
        lstPlayer = []
        for idx in xrange(iNum):
            dConfig = SKILLCONFIG[iSkillType]
            iOwner = 100001 + idx
            lstNormalSkill = []
            iSkillID = dConfig['iID'][random.randint(0, len(dConfig['iID']) - 1)]
            iPrice = 450 * random.randint(50, 200) / 100
            iSkillLevel = random.randint(dConfig['iRange'][0], dConfig['iRange'][1])
            iRefPrice = 450
            lstNormalSkill.append([
                iSkillID,
                iPrice,
                iSkillLevel,
                iRefPrice])
            if iSkillType == consignmalldefines.SKILLTYPE_MAKE:
                iSubSkillID = consignmalldefines.MAKESKILL[iSkillID]
                iSubSkillLevel = random.randint(0, 5)
                lstNormalSkill.append([
                    iSubSkillID,
                    iPrice,
                    iSubSkillLevel,
                    iRefPrice])
            
            lstPlayer.append([
                iOwner,
                lstNormalSkill])
            None = None
            continue
            None.OnAllNormalSkill(iShelfVersion, iSkillType, lstPlayer)
            return None
