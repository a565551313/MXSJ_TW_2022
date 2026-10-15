# pycdc 交叉复核产物 · script.fls entry 1195
# co_filename(原始)='script/mxgame/warui/dlgwarmagic.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1195.pyc (Python 2.5)

'''
================================================================================
\xca\xb1\xbc\xe4: 2020/4/20 17:26
\xd7\xf7\xd5\xdf: jwc
\xce\xc4\xbc\xfe: dlgwarmagic
\xbd\xe9\xc9\xdc\xa3\xba\xd5\xbd\xb6\xb7\xd6\xd0\xd5\xd0\xca\xbd\xbd\xe7\xc3\xe6 - \xd6\xf7\xbd\xe7\xc3\xe6
================================================================================
'''
import combdialog
import combmacro
import interface
import slot
import pagedlgbase
import war
import world

class CWarMagicMainDialog(combdialog.CCombDialog, slot.ISignalSubject, pagedlgbase.CPageDlgBase):
    SS_SetArrowAni = 'SS_SetArrowAni(iIndex)'
    SS_SetFirstWarMagic = 'SS_SetFirstWarMagic(iMagicID)'
    
    def __init__(self):
        import ratio
        combdialog.CCombDialog.__init__(self, interface.DialogPanel, 'war/magic_new.dlg')
        pagedlgbase.CPageDlgBase.__init__(self)
        self.ssInit()
        self.m_DelegateList = []
        self.m_CtrlName2Pos = { }
        self.m_oDescList = []
        self.m_sBuffEffect = ''
        self.m_oPosTimer = None
        self.InitDelegate()
        tPos = ratio.GetPrivatePosByRate('War', 'magicdlgpos')
        if tPos:
            (iX, iY) = tPos
            self.SetPos(iX, iY)
        else:
            interface.Center(self)

    
    def InitDelegate(self):
        import dgtwarmagic
        self.m_DelegateList = [
            dgtwarmagic.CWarMagicDelegate(self, [
                'btn_normal',
                'btn_icon'])]

    
    def HidePageBtn(self):
        self.SetShowObject('btn_normal', False)
        self.SetShowObject('btn_icon', False)

    
    def RecordCtrlPos(self):
        self.m_CtrlName2Pos = {
            'txt_mp': (),
            'txt_fp': () }
        for sObjName in self.m_CtrlName2Pos.keys():
            (x, y) = self.GetObject(sObjName).GetPos()
            self.m_CtrlName2Pos[sObjName] = (x, y)
        

    
    def ResetCtrlPos(self):
        for sObjName in self.m_CtrlName2Pos.keys():
            self.GetObject(sObjName).SetShow(True)
            (x, y) = self.m_CtrlName2Pos[sObjName]
            self.GetObject(sObjName).SetPos(x, y)
        

    
    def RefreshDesc(self, dInfo):
        self.m_oDescList = []
        if dInfo:
            self.RefreshTitle(dInfo)
            self.RefreshMagicProp(dInfo)
        

    
    def RefreshTitle(self, dInfo):
        oTitle = combmacro.CTEXT(interface.CTextObject, 'loc_title', self, dInfo['sName'], interface.FontLT14_10, interface.COLOR_102)
        (x, _) = oTitle.GetPos()
        (w, _) = oTitle.GetSize()
        (_, y) = self.GetObject('img_point').GetPos()
        self.GetObject('img_point').SetPos(x + w + 2, y)
        self.m_oDescList.append(oTitle)

    
    def GetPercentTxt(self):
        return '%'

    
    def RefreshMagicProp(self, dInfo):
        import magicdata
        import magicinfo
        import hero
        import item
        import itemdata
        import jingxiu
        import wraprichtext
        dMagic = magicdata.GetData(dInfo['iMagicID'])
        dLiupai2Skill = {
            11: 1001,
            12: 1005,
            13: 1004,
            14: 1002,
            15: 1003,
            16: 1011,
            17: 1014,
            21: 1008,
            22: 1007,
            23: 1006,
            24: 1010,
            25: 1009 }
        
        try:
            sLiupai = {
                11: '\xbcC\xb3N',
                12: '\xb5\xa7\xaak',
                13: '\xae\xb1\xaak',
                14: '\xa4M\xaak',
                15: '\xbaj\xb3N',
                16: '\xb7t\xbe\xb9',
                17: '\xb0\xad\xa8\xa6',
                21: '\xa6\xf2\xbe\xc7',
                22: '\xb9D\xaea',
                23: '\xbe\xa7\xbe\xc7',
                24: '\xa7\xc5\xb3N',
                25: '\xb3\xb1\xb6\xa7\xb3N',
                27: '\xa8\xe4\xa5\xa6' }[dMagic['type']]
        except:
            sLiupai = '-'

        
        try:
            slv = dInfo['iLV']
        except:
            slv = 1

        
        try:
            gslv = hero.g_Skills[hero.ST_SKILL][dLiupai2Skill[dMagic['type']]].m_Level
        except:
            gslv = 0

        pow = eval(dMagic['pow'])
        if pow == 0:
            pow = '-'
        else:
            pow = str(pow)
        powrate = eval(dMagic['powrate'])
        if powrate == 0:
            powrate = '-'
        else:
            powrate = '%d%%' % powrate
        xinfarate = magicinfo.GetXinfaRate(dInfo['iMagicID'])
        mlv_str = str(dInfo['iLV'])
        if dMagic['type'] == 27:
            mlv_str = '-'
        
        mid = dInfo['iMagicID']
        
        try:
            hlv = hero.g_Skills[hero.ST_MAGIC][mid].m_HighLv
        except:
            hlv = 0

        high = {
            'res_n': 0,
            'res_p': 0,
            'res_d': 0,
            'res_m': 0,
            'power_txt': '',
            'power': 0,
            'speed_txt': '',
            'speed': 0,
            'ar_txt': '',
            'ar': 0,
            'eff_txt': '',
            'eff': 0,
            'fp': 0,
            'mp': 0,
            'ext_attack': 0,
            'ext_define': 0,
            'ext_disturb': 0 }
        if hlv > 0:
            jx_data = jingxiu.GetData(mid)
            high['power'] = jx_data['power'] * hlv
            if high['power'] > 0:
                high['power_txt'] = '+%d' % high['power']
            else:
                high['power_txt'] = ''
            high['speed'] = jx_data['speed'] * hlv
            if high['speed'] < 0:
                high['speed_txt'] = '%d' % high['speed']
            elif high['speed'] > 0:
                high['speed_txt'] = '+%d' % high['speed']
            
            high['ar'] = jx_data['ar'] * hlv
            if high['ar'] < 0:
                high['ar_txt'] = '%d' % high['ar']
            elif high['ar'] > 0:
                high['ar_txt'] = '+%d' % high['ar']
            
            high['eff'] = jx_data['eff'] * hlv
            if high['eff'] > 0:
                high['eff_txt'] = '+%d' % high['eff']
            else:
                high['eff_txt'] = ''
            high['res_p'] = jx_data['res_p'] * hlv
            high['res_d'] = jx_data['res_d'] * hlv
            high['res_m'] = jx_data['res_m'] * hlv
            high['res_n'] = jx_data['res_n'] * hlv
            high['mp'] = jx_data['mp'] * hlv
            high['fp'] = jx_data['fp'] * hlv
            for key in ('ext_attack', 'ext_define', 'ext_disturb'):
                if jx_data[key]:
                    high[key] = jx_data[key] * hlv
                    continue
            
        
        if dInfo['iMagicID'] in (1428,) and 'effcount' in dMagic and eval(dMagic['effcount']) > eval(dMagic['maxeffcount']):
            fpstr = dMagic['fp']
            fpstr = fpstr.replace(dMagic['effcount'], dMagic['maxeffcount'])
        
        
        try:
            ar = '%d' % eval(dMagic['ar'])
        except:
            ar = '-'

        iDefaultColor = interface.COLOR_56
        iDeepColor = interface.COLOR_177
        iRedColr = interface.COLOR_220
        res_n = '%d%%' % (dMagic['res_n'] + high['res_n'])
        res_p = '%d%%' % (dMagic['res_p'] + high['res_p'])
        res_d = '%d%%' % (dMagic['res_d'] + high['res_d'])
        res_m = '%d%%' % (dMagic['res_m'] + high['res_m'])
        costRate = self.GetCostRate()
        maxslv = self.GetMaxSlv(slv, mid)
        (mpExtCost, fpExtCost) = hero.GetExtCost(mid, hlv)
        all_prop = [
            ('loc_level', self.GetJingXiuLevel(mlv_str, hlv), False, iDefaultColor, interface.COLOR_30),
            ('loc_class', dMagic['class'], False, iDefaultColor, interface.COLOR_30),
            ('loc_stype', dMagic['stype'], False, iDefaultColor, interface.COLOR_30),
            ('loc_pow', '%s%s' % (pow, high['power_txt']), False, iDefaultColor, interface.COLOR_30),
            ('loc_speed', '%d%s%s' % (eval(dMagic['speed']), high['speed_txt'], self.GetPercentTxt()), False, iDefaultColor, interface.COLOR_30),
            ('loc_ar', '%s%s' % (ar, high['ar_txt']), False, iDefaultColor, interface.COLOR_30),
            ('loc_powrate', '%s%s' % (powrate, high['eff_txt']), False, iDefaultColor, interface.COLOR_30),
            ('loc_res_putong', res_n, eval(res_n.replace('%', '')) < 0, iDeepColor, iRedColr),
            ('loc_res_lidi', res_p, eval(res_p.replace('%', '')) < 0, iDeepColor, iRedColr),
            ('loc_res_lingqiao', res_d, eval(res_d.replace('%', '')) < 0, iDeepColor, iRedColr),
            ('loc_res_qungong', res_m, eval(res_m.replace('%', '')) < 0, iDeepColor, iRedColr),
            ('loc_ap', '%d/%d' % (int(dMagic['at'] * xinfarate + high['ext_attack']), hero.g_Prop.m_At), high['ext_attack'] + int(dMagic['at'] * xinfarate) > hero.g_Prop.m_At, iDefaultColor, interface.COLOR_30),
            ('loc_dp', '%d/%d' % (int(dMagic['df'] * xinfarate + high['ext_define']), hero.g_Prop.m_Df), high['ext_define'] + int(dMagic['df'] * xinfarate) > hero.g_Prop.m_Df, iDefaultColor, interface.COLOR_30),
            ('loc_rp', '%d/%d' % (int(dMagic['dp'] * xinfarate + high['ext_disturb']), hero.g_Prop.m_Dp), high['ext_disturb'] + int(dMagic['dp'] * xinfarate) > hero.g_Prop.m_Dp, iDefaultColor, interface.COLOR_30),
            ('loc_mp', '%d/%d' % (int(eval(dMagic['mana']) * xinfarate + mpExtCost + high['mp']), hero.g_Prop.m_MP), int(eval(dMagic['mana']) * xinfarate) + high['mp'] > hero.g_Prop.m_MP, iDefaultColor, interface.COLOR_30),
            ('loc_fp', '%d/%d' % (int(eval(dMagic['fp']) + fpExtCost + high['fp']), hero.g_Prop.m_FP), eval(dMagic['fp']) + high['mp'] > hero.g_Prop.m_FP, iDefaultColor, interface.COLOR_30)]
        if dMagic['type'] in magicdata.NEEDWEAPON and magicdata.NEEDWEAPON[dMagic['type']] != itemdata.GetWeaponType(item.GetWeaponShape()):
            color = interface.COLOR_30
        else:
            color = iDefaultColor
        self.m_oDescList.append(combmacro.CTEXT(interface.CTextObject, 'loc_liupai', self, sLiupai, interface.FontLT14_3, color))
        self.ResetCtrlPos()
        for \xc8\xc5\xca\xc6\xce, txt, inv, color, invcolor in all_prop:
            if \xc8\xc5\xca\xc6\xce == 'loc_mp' and int(eval(dMagic['mana']) * xinfarate) == 0 and high['mp'] == 0:
                (x, y) = self.GetObject('txt_mp').GetPos()
                self.GetObject('txt_fp').SetPos(x, y)
                self.GetObject('txt_mp').SetShow(False)
                continue
            elif \xc8\xc5\xca\xc6\xce == 'loc_fp' and int(eval(dMagic['fp'])) == 0 and high['fp'] == 0:
                self.GetObject('txt_fp').SetShow(False)
                continue
            
            if \xc8\xc5\xca\xc6\xce == 'loc_fp' and not self.GetObject('txt_mp').GetShow():
                \xc8\xc5\xca\xc6\xce = 'loc_mp'
            
            if self.GetObject(\xc8\xc5\xca\xc6\xce):
                itemobj = combmacro.CTEXT(interface.CTextObject, \xc8\xc5\xca\xc6\xce, self, txt, interface.FontLT14_3, color)
                if inv:
                    itemobj.SetColor(invcolor)
                
                self.m_oDescList.append(itemobj)
                continue
        
        self.m_oDescList.append(combmacro.CSCROLLTEXT(wraprichtext.CScrollRichText, self, 'loc_desc', interface.ReplaceRed(self.GetDescText(mid, hlv, high['eff'], high['ar'])), interface.FontLT14_3, False, interface.COLOR_4, pReplaceColorFunc = self.RelaceLinkStrColor))

    
    def GetCostRate(self):
        oObj = world.GetObj(war.g_HeroID)
        iAddonID = 189
        if oObj and hasattr(oObj, 'm_AddonsExt') and iAddonID in oObj.m_AddonsExt:
            sExtDesc = oObj.m_AddonsExt[iAddonID]
            if sExtDesc:
                iLV = sExtDesc.get('lv')
                if iLV:
                    return 1 + (44 + iLV * 6) / 100
                
            
        
        return 1

    
    def GetMaxSlv(self, slv, iMagicID):
        import magicmaxdata
        if iMagicID in magicmaxdata.DATA:
            return magicmaxdata.DATA[iMagicID]
        
        return slv

    
    def GetDescText(self, iMagicID, iHlv, iEff, iAr):
        import magicinfo
        import highlvdescdata
        import magicdata
        import permission
        dData = magicdata.GetData(iMagicID)
        (sDesc, self.m_sBuffEffect) = magicinfo.GetMagicDesc(iMagicID)
        hlv = iHlv
        if 'formula6' in sDesc:
            iFormula6 = eval(dData['formula6'])
            sDesc = sDesc.replace('$formula6', str(iFormula6))
        
        if '$formula7' in sDesc:
            iFormula7 = int(eval(dData['formula7']))
            if iFormula7 < 100:
                sDesc = sDesc.replace('$formula7', '#r\xb6\xcb\xae`\xb5\xb2\xaaG\xa1G\xa5\xbf\xb1`\xb6\xcb\xae`\xaa\xba%d%%' % iFormula7)
            elif iFormula7 > 100:
                sDesc = sDesc.replace('$formula7', '#r\xb6\xcb\xae`\xb5\xb2\xaaG\xa1G+%d%%' % (iFormula7 - 100))
            else:
                sDesc = sDesc.replace('$formula7', '')
        
        if '$formula8' in sDesc:
            iFormula8 = int(eval(dData['formula8']))
            if iFormula8 > 0:
                sDesc = sDesc.replace('$formula8', '#r\xa6\xdb\xa8\xad\xa9R\xa4\xa4\xb2v\xa1G+%d%%' % iFormula8)
            elif iFormula8 < 0:
                sDesc = sDesc.replace('$formula8', '#r\xa6\xdb\xa8\xad\xa9R\xa4\xa4\xb2v\xa1G%d%%' % iFormula8)
            else:
                sDesc = sDesc.replace('$formula8', '')
        
        if '$blood' in sDesc:
            sDesc = sDesc.replace('$blood', str(eval(dData['blood'])))
        
        if iEff > 0:
            sDesc = sDesc.replace('$powrate', '+%d' % int(iEff))
        else:
            sDesc = sDesc.replace('$powrate', '')
        if iAr > 0:
            sDesc = sDesc.replace('$ar', '+%d' % int(iAr))
        else:
            sDesc = sDesc.replace('$ar', '')
        if iHlv:
            sHihgLvDesc = highlvdescdata.GetMagicDesc(iMagicID, iHlv)
            if sHihgLvDesc:
                if not sDesc.endswith('#r#r'):
                    if sDesc.endswith('#r'):
                        sDesc += '#r'
                    else:
                        sDesc += '#r#r'
                
                sDesc += '%s' % sHihgLvDesc
            
        
        if interface.IsStyle3():
            sDesc = sDesc.replace('#G', '#c12a42e')
        elif interface.IsStyle4():
            sDesc = sDesc.replace('#G', '#c109126')
        
        return sDesc

    
    def GetJingXiuLevel(self, slv, highlv):
        if highlv > 0:
            return '%s+%d' % (slv, highlv)
        
        return slv

    
    def RelaceLinkStrColor(self, sOriStr, dLinkObj):
        import wrapui
        for _, oLinkObj in dLinkObj.items():
            
            try:
                sLinkOri = oLinkObj.GetResult()
                if not sLinkOri:
                    continue
                
                sNewTxt = oLinkObj.GetResult('#cff8c00')
                sOriStr = sOriStr.replace(sLinkOri, sNewTxt)
            except:
                pass

            if isinstance(oLinkObj, wrapui.CLinkBuffer):
                oLinkObj.SetEffectTxt(self.m_sBuffEffect)
                continue
        
        return sOriStr

    
    def SetArrowAni(self, iIndex):
        self.ssEmit(self.SS_SetArrowAni, iIndex)

    
    def SetFirstWarMagic(self, iFirstWarMagic):
        self.ssEmit(self.SS_SetFirstWarMagic, iFirstWarMagic)

    
    def DelaySaveDlgPos(self):
        import timer
        if self.m_oPosTimer:
            self.m_oPosTimer.Release()
            self.m_oPosTimer = None
        
        self.m_oPosTimer = timer.Timer(0.1, self.SaveDlgPos)

    
    def SaveDlgPos(self):
        import ratio
        (iX, iY) = self.GetPos()
        ratio.SavePrivatePosByRate('War', 'magicdlgpos', '%d,%d' % (iX, iY))

    
    def VOpenPage(self, dExtend = None):
        self.ssEmit(self.SS_OpenDlg, dExtend)

    
    def VClose(self):
        self.ssEmit(self.SS_CloseDlg)

    
    def Hold(self):
        combdialog.CCombDialog.Hold(self)
        self.DelaySaveDlgPos()

    
    def CloseWindow(self):
        import warui
        warui.g_MagicDialog = None

    
    def OnMessage(self, iMsgID):
        self.ssEmit(self.SS_ClickBtn, iMsgID)
        if iMsgID == 2:
            self.VClose()
