# pycdc 交叉复核产物 · script.fls entry 2236
# co_filename(原始)='script/mxgame/skill/netskill.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2236.pyc (Python 2.5)


def GetSkillNetObj(iSub):
    pass


def S2CSkill(netobj):
    import hero
    import misc
    iSkillLen = netobj.UnpackInt(1)
    for _ in range(iSkillLen):
        iSkillID = netobj.UnpackInt(2)
        iSkillLv = netobj.UnpackInt(1)
        iSkillLimit = netobj.UnpackInt(1)
        iTrueLv = netobj.UnpackInt(1)
        iIsInList = netobj.UnpackInt(1)
        bIsInLearnList = iIsInList == 1
        iPoint = netobj.UnpackInt(4)
        iPointMax = netobj.UnpackInt(4)
        iIsXiuLian = netobj.UnpackInt(1)
        bIsXiuLian = iIsXiuLian == 1
        iRankAddLevel = netobj.UnpackInt(1)
        iRideAddLevel = netobj.UnpackInt(1)
        iAddLevel = netobj.UnpackInt(1)
        iTime = netobj.UnpackInt(4)
        dExtend = {
            'bIsXiuLian': bIsXiuLian,
            'iAddLevel': iAddLevel,
            'iRankAddLevel': iRankAddLevel,
            'iRideAddLevel': iRideAddLevel,
            'iTime': iTime }
        hero.UpdateSkill(hero.ST_SKILL + 1, iSkillID, iSkillLv, limit = iSkillLimit, truelv = iTrueLv, exp = iPoint, maxp = iPointMax, binlist = bIsInLearnList, dExtend = dExtend)
    
    import skillmagicsignal
    skillmagicsignal.Emit(skillmagicsignal.SS_XIULIAN_SKILLLVUPDATE)


def S2CMagic(netobj):
    import hero
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    iBid = netobj.UnpackInt(2)
    iPoint = netobj.UnpackInt(2)
    iCash = netobj.UnpackInt(4)
    iHighLv = netobj.UnpackInt(1)
    iMaxLv = netobj.UnpackInt(1)
    hero.UpdateMagic(iSkillID, iSkillLv, iPoint, iCash, iHighLv, iMaxLv)
    if hero.IsReadyMagic(iSkillID):
        hero.UpdateSkill(hero.ST_MAGICREADY + 1, iSkillID, iSkillLv, limit = iMaxLv)
    
    import misc
    if not misc.IsSkillEqupipServer():
        import block
        block.UpdateSkillBlock(iSkillID, iBid)
    


def S2CPassive(netobj):
    import hero
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    hero.UpdateSkill(hero.ST_PASSIVE + 1, iSkillID, iSkillLv)
    iBid = netobj.UnpackInt(2)
    import misc
    if not misc.IsSkillEqupipServer():
        import block
        block.UpdateSkillBlock(iSkillID, iBid)
    


def S2CTitle(netobj):
    import hero
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    iColor = netobj.UnpackInt(1)
    iCanDel = netobj.UnpackInt(1)
    sTitle = netobj.UnpackString(0)
    hero.UpdateSkill(hero.ST_TITLE + 1, iSkillID, iSkillLv, sTitle, iscandel = iCanDel)
    if iSkillLv != 0:
        setattr(hero.g_Skills[hero.ST_TITLE][iSkillID], 'm_Color', iColor)
    


def S2CAbility(netobj):
    import hero
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    hero.UpdateSkill(hero.ST_ABILITY + 1, iSkillID, iSkillLv)


def S2CShortcut(netobj):
    import dlgaction
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    iMagicID = netobj.UnpackInt(2)
    if iSkillLv != 1:
        return None
    
    dlgaction.SetShortcut(iSkillID, iMagicID)


def S2CMagicReady(netobj):
    import hero
    import mainmenu
    import warui
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    
    try:
        if mainmenu.IsWar() and isinstance(warui.g_HeroMenu, warui.CHeroMenu):
            bShow = warui.g_HeroMenu.GetShow()
            warui.g_HeroMenu = warui.CHeroMenu()
            warui.g_HeroMenu.SetShow(bShow)
    except:
        pass

    hero.UpdateSkill(hero.ST_MAGICREADY + 1, iSkillID, iSkillLv)


def S2CSpeMagic(netobj):
    import hero
    import warui
    import main
    iSkillID = netobj.UnpackInt(2)
    iSkillLv = netobj.UnpackInt(1)
    hero.UpdateSkill(hero.ST_SPECIAL + 1, iSkillID, iSkillLv)
    warui.RefershSpecialDialog()
    if not main.InWar() or not warui.IsSummonMenu():
        warui.ShowMagicShortKey()
    


def S2CSetSkillID(netobj):
    iSkillID = netobj.UnpackInt(2)
    import pagexiulian_interface
    pagexiulian_interface.SetXiulianSkill(iSkillID)


def S2CSkillExp(netobj):
    iExp = netobj.UnpackInt(4)
    iExpNext = netobj.UnpackInt(4)
    import pagexiulian_interface
    pagexiulian_interface.SetExp(iExp, iExpNext)


def S2CSkillShowXiulianAdd(netobj):
    import pagexiulian_interface
    import hero
    bShow = netobj.UnpackInt(1) == 1
    pagexiulian_interface.SetXiulianShowAdd(bShow)
    iSkillLen = netobj.UnpackInt(1)
    for _ in range(iSkillLen):
        iSkillID = netobj.UnpackInt(2)
        iXiulianAdd = netobj.UnpackInt(2)
        iNewLimit = netobj.UnpackInt(2)
        hero.UpdateXiuLianAdd(iSkillID, iXiulianAdd)
        hero.UpdateNewLimit(iSkillID, iNewLimit)
    
    import skillmagicsignal
    skillmagicsignal.Emit(skillmagicsignal.SS_XIULIAN_SKILLLVUPDATE)

S2CSkillFunc = {
    1: S2CSkill,
    2: S2CMagic,
    3: S2CPassive,
    4: S2CAbility,
    5: S2CTitle,
    6: S2CShortcut,
    7: S2CMagicReady,
    8: S2CSpeMagic,
    9: S2CSetSkillID,
    10: S2CSkillExp,
    11: S2CSkillShowXiulianAdd }

def S2CSkillProcess(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CSkillFunc:
        del iSub[:]
        'S2CSkillProcess-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I'.S2CSkillFunc = LOG
        return None
    
    import protocolprint
    oFunc = S2CSkillFunc[iSub]
    protocolprint.AppendS2CSubInfo('S2CSkillProcess', oFunc.__name__)
    if iSub == 2:
        oFunc(netobj)
    else:
        CheckInWar(netobj, oFunc, iSub)

WAR_CACHE = [
    2,
    7]

def CheckInWar(netobj, oFunc, iSub):
    import main
    import net
    import war
    if main.InWar() and iSub in WAR_CACHE:
        cmd = war.CCmd(war.ServerCmd)
        cmd.netobj = net.CNetServerCommand(netobj)
        cmd.func = oFunc
    else:
        oFunc(netobj)
