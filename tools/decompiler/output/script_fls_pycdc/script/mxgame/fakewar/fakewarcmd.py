# pycdc 交叉复核产物 · script.fls entry 1868
# co_filename(原始)='script/mxgame/fakewar/fakewarcmd.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1868.pyc (Python 2.5)

import fakewardefine
import fakewarmagic
import fakewarpfm
import fakewarwarrior
import magicmgr
import war

def Addon(oWarMgr, cmd):
    DoAddonAction(oWarMgr, cmd.id, cmd.pid, cmd.turn, cmd.series)
    oWarMgr.GetCmdMgr().NextCmd()


def Add(oWarMgr, cmd):
    warrior_id = cmd.id
    allied = cmd.allied
    obj = fakewarwarrior.CreateWarrior(oWarMgr, oWarMgr.GetWarBackGround(), warrior_id, allied, cmd.m_iShape, cmd.m_Desc, cmd.m_iPlace)
    faced = {
        True: 16,
        False: 0 }[allied]
    obj.SetDirection(faced)
    obj.m_Allied = allied
    obj.m_OrigDirection = faced
    (obj.m_OrigX, obj.m_OrigY) = obj.GetPos()
    oWarMgr.GetWarriorMgr().AddWarrior(warrior_id, obj)
    oWarMgr.GetCmdMgr().NextCmd()


def PerformName(oWarMgr, cmd):
    id = cmd.id
    sktxt = cmd.sktxt
    obj = oWarMgr.GetWarriorMgr().GetWarriorByID(id)
    print 'PerformName!!!!!!', id, sktxt
    if obj:
        obj.Trigger(sktxt)
    
    oWarMgr.GetCmdMgr().NextCmd()


def Perform(oWarMgr, cmd):
    if not magicmgr.g_MagicKind:
        magicmgr.ReadMagicKind()
    
    if cmd.pid in war.IGONRE_PERFORM:
        oWarMgr.GetCmdMgr().NextCmd()
        return None
    
    GetMagicInfo(oWarMgr, cmd.id, cmd.vic_ids)
    oWarMgr.GetWarriorMgr().SetVictimIDList(cmd.vic_ids)
    attacker = oWarMgr.GetWarriorMgr().GetAttacker()
    import magicperformdata
    (iOffx, iOffy) = oWarMgr.GetMagicOffset()
    if magicperformdata.IsNewMagic(cmd.pid):
        dAttackInfo = {
            'iProtectID': 0,
            'iAttackID': cmd.id,
            'iVicList': cmd.vic_ids,
            'bFightBack': False,
            'bDamageBack': False,
            'tWarDemoOffSet': (iOffx, iOffy) }
        import magicperform
        magicperform.Start(oWarMgr.GetNewMagicType(), cmd.pid, dAttackInfo)
        oWarMgr.GetCmdMgr().SetProcess(None)
        return None
    else:
        fakewarmagic.PerformMagicName(oWarMgr, cmd)
    iWaitList = [
        cmd.id]
    iWaitList.extend(cmd.vic_ids)
    if fakewarpfm.CreatePerform(oWarMgr, cmd):
        pass
    else:
        attacker.PushBackAction(attacker.Magic, cmd)
    oWarMgr.GetCmdMgr().SetWait(iWaitList)
    attacker.NextAction()


def AttackNormal(oWarMgr, cmd):
    oWarriorMgr = oWarMgr.GetWarriorMgr()
    oWarriorMgr.SetAttackerID(cmd.att_id)
    oWarriorMgr.SetVictimID(cmd.vic_id)
    attacker = oWarriorMgr.GetAttacker()
    victim = oWarriorMgr.GetVictim()
    GetStateInfo(oWarMgr, attacker)
    GetStateInfo(oWarMgr, victim)
    attacker.LoadAttackInfo()
    if oWarMgr.GetMagicMgr().GetSkipRush():
        oWarMgr.GetMagicMgr().SetSkipRush(False)
    else:
        (x, y) = war.GetOrderPos(attacker, victim)
        attacker.PushBackAction(attacker.Rush, x, y)
    attacker.PushBackAction(attacker.AttackPre)
    attacker.PushBackAction(attacker.Attack)
    attacker.PushBackAction(attacker.ClearKeyCallback)
    acmd = oWarMgr.GetCmdMgr().CmdFind(fakewardefine.CMD_ATTACKNORMALEND)
    if acmd:
        if not victim.IsSuperPosition(victim.m_OrigX, victim.m_OrigY):
            if not victim.IsDied():
                victim.PushBackAction(victim.GoBack, 43, True)
            
        
        if not attacker.IsSuperPosition(victim.m_OrigX, victim.m_OrigY):
            if not attacker.IsDied():
                attacker.PushBackAction(attacker.GoBack, 43, True)
            
        
        if acmd.id != 0:
            follower = oWarriorMgr.GetWarriorByID(acmd.id)
            if follower and not follower.IsDied():
                follower.PushBackAction(follower.GoBack, 43, True)
                attacker.AddFollower(acmd.id)
            
        
    
    attacker.NextAction()
    oWarMgr.GetCmdMgr().SetWait([
        cmd.att_id,
        cmd.vic_id])


def AttackNormalEnd(oWarMgr, cmd):
    oWarMgr.GetCmdMgr().NextCmd()


def ChgShape(oWarMgr, cmd):
    obj = oWarMgr.GetWarriorMgr().GetWarriorByID(cmd.id)
    if obj:
        cmd.shape = war.TransformShape(cmd.shape)
        ChgShapeByArg(obj, cmd.shape, cmd.name, cmd.desc)
    
    oWarMgr.GetCmdMgr().NextCmd()


def Turn(oWarMgr, cmd):
    for obj in oWarMgr.GetWarriorMgr().GetAllWarriorDict().values():
        if hasattr(obj, 'Turn'):
            obj.Turn()
            continue
    
    oWarMgr.GetCmdMgr().NextCmd()


def State(oWarMgr, cmd):
    obj = oWarMgr.GetWarriorMgr().GetWarriorByID(cmd.id)
    if obj:
        if cmd.hp_chg:
            obj.m_Hurt = cmd.hurt
            obj.CreateModifyHP(cmd.hp_chg)
            if cmd.hp_chg < 0 and obj.m_State == 'die':
                obj.Guard()
                obj.m_Life = war.WARRIOR_LIFE_NORMAL
            
        
        if cmd.life == war.WARRIOR_LIFE_DEAD:
            pass
        obj.Die()
        oWarMgr.GetCmdMgr().SetWait([
            cmd.id])
    
    obj.m_Life = cmd.life
    obj.m_Resist = 0
    oWarMgr.GetCmdMgr().NextCmd()


def CustomCmd(oWarMgr, cmd):
    if cmd.callFunc(oWarMgr, cmd):
        oWarMgr.GetCmdMgr().NextCmd()
    


def MPFPChange(oWarMgr, oCmd):
    oWarrior = oWarMgr.GetWarriorMgr().GetWarriorByID(oCmd.id)
    if not oWarrior:
        return None
    
    if oCmd.iType == 1:
        oWarrior.CreateModifyMP(oCmd.iValue)
    elif oCmd.iType == 2:
        oWarrior.CreateModifyFP(oCmd.iValue)
    else:
        raise Exception('\xb5\xa6\xa6E\xa7A\xaa\xf8\xc2I\xa4\xdf\xa1A\xc3\xfe\xab\xac\xbf\xf9\xa4F')
    oWarMgr.GetCmdMgr().NextCmd()

CMDDICT = {
    fakewardefine.CMD_ADDON: Addon,
    fakewardefine.CMD_ADD: Add,
    fakewardefine.CMD_ATTACKNORMAL: AttackNormal,
    fakewardefine.CMD_ATTACKNORMALEND: AttackNormalEnd,
    fakewardefine.CMD_CHGSHAPE: ChgShape,
    fakewardefine.CMD_PERFORM: Perform,
    fakewardefine.CMD_PERFORMNAME: PerformName,
    fakewardefine.CMD_STATE: State,
    fakewardefine.CMD_TURN: Turn,
    fakewardefine.CMD_CUSTOM: CustomCmd,
    fakewardefine.CMD_MPFP: MPFPChange }

def DoAddonAction(oWarMgr, id, pid, turn, series):
    obj = oWarMgr.GetWarriorMgr().GetWarriorByID(id)
    if obj:
        obj.SetAddon(pid, turn, series)
    


def ChgShapeByArg(obj, shape, name, desc):
    if obj.m_State != 'die':
        obj.SetState('stand', False)
    
    obj.m_StandSize = 0
    del obj.m_StandSize
    obj.ChangeShape(shape, desc)
    if obj.m_State == 'die':
        obj.SetState('die', False)
        obj.SetFrame(obj.FrameAmount() - 1)
    
    obj.m_Desc = desc


def GetMagicInfo(oWarMgr, att_id, iVicIDList):
    oWarriorMgr = oWarMgr.GetWarriorMgr()
    oWarriorMgr.SetAttackerID(att_id)
    oWarriorMgr.SetVictimID(iVicIDList[0])
    attacker = oWarriorMgr.GetAttacker()
    attacker.LoadAttackInfo()
    GetStateInfo(oWarMgr, attacker)
    for iVicID in iVicIDList:
        if att_id != iVicID:
            victim = oWarriorMgr.GetWarriorByID(iVicID)
            GetStateInfo(oWarMgr, victim)
            continue
    


def GetStateInfo(oWarMgr, obj):
    if obj is None:
        return None
    
    oCmdMgr = oWarMgr.GetCmdMgr()
    statecmd = oCmdMgr.CmdFind(fakewardefine.CMD_STATE, 'id', obj.m_ID)
    if statecmd:
        obj.m_Ward = statecmd.ward
        obj.m_Hurt = statecmd.hurt
        obj.m_Life = statecmd.life
        obj.m_HPChg = statecmd.hp_chg
        obj.m_Resist = 0
    else:
        obj.m_Ward = war.WARRIOR_WARD_NONE
        obj.m_Hurt = war.WARRIOR_HURT_NONE
        obj.m_Life = war.WARRIOR_LIFE_NORMAL
        obj.m_HPChg = 0
        obj.m_Resist = 0
    obj.m_AddonCmds = []
    while None:
        pcmd = oCmdMgr.CmdFind(fakewardefine.CMD_ADDON, 'id', obj.m_ID)
        if pcmd:
            obj.m_AddonCmds.append(pcmd)
            continue
        break
        continue
        pCmd = oCmdMgr.CmdFind(fakewardefine.CMD_PERFORMNAME, 'id', obj.m_ID)
        obj.m_TriggerText = []
        if pCmd:
            obj.m_TriggerText.append(pCmd.sktxt)
