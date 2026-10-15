# pycdc 交叉复核产物 · script.fls entry 3989
# co_filename(原始)='script/handobj.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:00Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3989.pyc (Python 2.5)

import cursor
import interface
import key
import skilliconpath
g_HandObj = None
TYPE_ITEM = 'Item'
TYPE_VIR_ITEM = 'Vir_Item'
TYPE_SHOP = 'Shop'
TYPE_SKILL = 'Skill'
TYPE_BLOCK = 'Block'
TYPE_BAGS = 'Bags'
TYPE_DLGIMG = 'dlgimg'
TYPE_SH = 'SH'
TYPE_LINK = 'Link'
TYPE_PLOT = 'Plot'
TYPE_HOTKEYICON = 'hotkeyicon'
TYPE_HOLDHOTKEYICON = 'holdhotkey'
TYPE_HOLDTEXT = 'holdtext'
TYPE_HOLDTASKSWAP = 'holdtaskswap'
TYPE_HOLDITEM = 'holditem'
TYPE_HOLDBBMAKEICON = 'holdbbmake'
TYPE_HOLDCARDMAKEICON = 'holdCardmake'
TYPE_HOLDTATTOO = 'holdtattoo'
TYPE_HOLDMAGICICON = 'holdmagicicon'
TYPE_YARD_LAND = 'holdyardland'
TYPE_WARPREPAREITEM = 'warprepareitem'
cursor.AddNotLoadCursor('handobj', 'g_HandObj')

def HandItem(itemid, interfaceitems, accept, callback, *args):
    global g_HandObj
    import item
    it = item.GetItem(itemid)
    if it is None:
        print 'Invalid item id!'
        return None
    
    g_HandObj = item.CreateItem44Image(cursor.Cursor, it.m_Shape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_ITEM
    g_HandObj.m_ID = itemid
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    g_HandObj.m_InterfaceItems = interfaceitems
    key.RegisterRightButtonHotKey(Clear)


def IsHoldItemByID(iItemIDList):
    if g_HandObj and g_HandObj.m_Type == TYPE_ITEM and g_HandObj.m_ID in iItemIDList:
        return True
    else:
        return False


def HandHoldItem(itemid, interfaceitems, accept, callback, *args):
    global g_HandObj
    import item
    it = item.GetItem(itemid)
    if it is None:
        print 'Invalid item id!'
        return None
    
    g_HandObj = item.CreateItem44Image(cursor.Cursor, it.m_Shape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_HOLDITEM
    g_HandObj.m_ID = itemid
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    g_HandObj.m_InterfaceItems = interfaceitems
    key.RegisterLeftButtonHotKey(CheckHoldHand)
    key.RegisterRightButtonHotKey(Clear)


def HandDlgImg(id, uipath, ipath, callback, *args):
    global g_HandObj
    import ui
    
    try:
        g_HandObj = ui.CImage(cursor.Cursor, ipath, uipath)
    except:
        return None

    (w, h) = g_HandObj.GetSize()
    g_HandObj.SetPos(-w / 2, -h / 2)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_DLGIMG
    g_HandObj.m_ID = id
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterRightButtonHotKey(Clear)


def HandBagItem(bagid, pos, shape, interfaceitems, accept, callback, *args):
    global g_HandObj
    import item
    g_HandObj = item.CreateItem44Image(cursor.Cursor, shape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_BAGS
    g_HandObj.m_BagID = bagid
    g_HandObj.m_ID = -1
    g_HandObj.m_Pos = pos
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    g_HandObj.m_InterfaceItems = interfaceitems
    key.RegisterRightButtonHotKey(Clear)


def HandSHItem(itemid, shape, interfaceitems, accept, callback, *args):
    global g_HandObj
    import item
    g_HandObj = item.CreateItem44Image(cursor.Cursor, shape)
    g_HandObj.SetPos(-25, -25)
    while None:
        g_HandObj.m_Type = TYPE_SH
        g_HandObj.m_ID = itemid
        g_HandObj.m_Shape = shape
        g_HandObj.m_Accept = accept
        g_HandObj.m_Callback = callback
        g_HandObj.m_Args = args
        g_HandObj.m_InterfaceItems = interfaceitems
        key.RegisterRightButtonHotKey(Clear)
        return None


def HandSHOPItem(itemid, shape, interfaceitems, accept, callback, *args):
    global g_HandObj
    import item
    g_HandObj = item.CreateItem44Image(cursor.Cursor, shape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_SHOP
    g_HandObj.m_ID = itemid
    g_HandObj.m_Shape = shape
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    g_HandObj.m_InterfaceItems = interfaceitems
    key.RegisterRightButtonHotKey(Clear)


def HandMagicIcon(magicid, accept = None):
    global g_HandObj
    import ui
    (sPath, sPack) = skilliconpath.GetSummonSkillIconPath(magicid)
    g_HandObj = ui.CImage(cursor.Cursor, sPath, sPack)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_SKILL
    g_HandObj.m_ID = magicid
    g_HandObj.m_Accept = accept
    key.RegisterRightButtonHotKey(Clear)


def HandBlockShape(bid, fname, space, accept, callback, *args):
    global g_HandObj
    import block
    g_HandObj = block.CBlockShape(cursor.Cursor, bid, fname, space)
    (x, y) = g_HandObj.GetCenter()
    g_HandObj.SetPos(-x, -y)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_BLOCK
    g_HandObj.m_ID = bid
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterRightButtonHotKey(Clear)


def HandLinkImg(link_id, callback, *args):
    global g_HandObj
    import dlglink
    g_HandObj = dlglink.CHoldIcon(cursor.Cursor, link_id)
    g_HandObj.SetZ(-1)
    (w, h) = g_HandObj.GetSize()
    g_HandObj.SetPos(-w / 2, -h / 2)
    g_HandObj.m_Type = TYPE_LINK
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterRightButtonHotKey(Clear)


def HandPlotItem(id, shape, callback, *args):
    global g_HandObj
    import item
    g_HandObj = item.CreateItem44Image(cursor.Cursor, shape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_ID = id
    g_HandObj.m_Type = TYPE_PLOT
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterRightButtonHotKey(Clear)


def HandHaidaoItem(id, shape, callback, *args):
    global g_HandObj, g_HandObj
    import itemdata
    
    try:
        g_HandObj = interface.CStretchImagesObject(cursor.Cursor, 'item44/%.5d.igs' % itemdata.Shape2Image(shape), 'item')
    except:
        (sPath, sPack) = skilliconpath.GetSummonSkillIconPath(shape)
        g_HandObj = interface.CStretchImagesObject(cursor.Cursor, sPath, sPack)

    (w, _) = g_HandObj.GetSize()
    g_HandObj.SetScale(44 / w)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_ID = id
    g_HandObj.m_Type = TYPE_PLOT
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterRightButtonHotKey(Clear)


def HandMapTxtImg(px, py, res, text, font, color):
    global g_HandObj, g_HandObj
    import map
    (cx, cy) = cursor.GetPos()
    if interface.IsNewStyle():
        g_HandObj = interface.CSpriteBitmapObject(cursor.Cursor, res, interface.UIPath)
    else:
        g_HandObj = interface.CSpriteObject(cursor.Cursor, res, 'effect')
    (x, y) = cursor.GetCursorPos()
    
    try:
        (mapx, mapy) = map.g_Map.GetPos()
        x -= mapx
        y -= mapy
    except AttributeError:
        pass

    g_HandObj.m_X = x
    g_HandObj.m_Y = y
    g_HandObj.m_TextLabel = interface.CTextObject(cursor.Cursor, text, font, color)
    g_HandObj.m_TextLabel.SetZ(1)
    curx = px - cx
    cury = py - cy
    g_HandObj.SetPos(curx, cury)
    txtwidth = interface.GetTextWidth(text, font)
    g_HandObj.m_TextLabel.SetPos(curx - txtwidth / 2, cury - 23)
    g_HandObj.m_Callback = ClearUp
    g_HandObj.m_Args = (x, y)
    key.RegisterLeftButtonHotKey(Clear)


def HandShortcutIcon(idx, sFileName, sPackage, accept, callback, *args):
    global g_HandObj
    import shortcut
    g_HandObj = shortcut.CSkillIcon(cursor.Cursor, sFileName, sPackage)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_HOTKEYICON
    g_HandObj.m_ID = idx
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterRightButtonHotKey(Clear)


def HandHoldShortcutIcon(idx, sFileName, sPackage):
    global g_HandObj
    import shortcut
    g_HandObj = shortcut.CSkillIcon(cursor.Cursor, sFileName, sPackage)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_HOLDHOTKEYICON
    g_HandObj.m_ID = idx
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = None
    g_HandObj.m_Args = None
    key.RegisterLeftButtonHotKey(CheckHoldHand)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldBBMakeIcon(iExpType, handDct):
    global g_HandObj
    import dlgbbmake
    g_HandObj = dlgbbmake.CreateBBMakeIcon(cursor.Cursor, handDct)
    g_HandObj.m_Type = TYPE_HOLDBBMAKEICON
    g_HandObj.m_ExpType = iExpType
    g_HandObj.m_HandDct = handDct
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = None
    g_HandObj.m_Args = None
    key.RegisterLeftButtonHotKey(dlgbbmake.CheckHoldHand)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldBBCardMakeIcon(cardid, interfaceitems, htype, accept, callback, *args):
    global g_HandObj
    import dlgbbcardmake
    import item
    card = dlgbbcardmake.GetCard(cardid)
    print cardid
    if card is None:
        print 'Invalid item id!'
        return None
    
    g_HandObj = item.CreateItem44Image(cursor.Cursor, card.m_Shape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_HOLDCARDMAKEICON
    g_HandObj.m_ExpType = htype
    g_HandObj.m_ID = cardid
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    g_HandObj.m_InterfaceItems = interfaceitems
    key.RegisterLeftButtonHotKey(CheckHoldHand)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldTattooIcon(iExpType, handDct):
    global g_HandObj
    import dlgtattoo
    g_HandObj = dlgtattoo.CreateTattooIcon(cursor.Cursor, handDct)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_HOLDTATTOO
    g_HandObj.m_ExpType = iExpType
    g_HandObj.m_HandDct = handDct
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = None
    g_HandObj.m_Args = None
    key.RegisterLeftButtonHotKey(CheckHoldHand)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldTaskSwap(taskObj, taskid, dlg, callback):
    global g_HandObj
    g_HandObj = taskObj
    g_HandObj.m_Type = TYPE_HOLDTASKSWAP
    g_HandObj.m_TaskID = taskid
    g_HandObj.m_ParentDlg = dlg
    g_HandObj.m_Accept = None
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = (dlg,)
    key.RegisterLeftButtonHotKey(CheckHoldHandAndClear)
    key.RegisterRightButtonHotKey(Clear)


def HandWarPrepareItem(tItemID, iShape, callback, *args):
    global g_HandObj
    import item
    g_HandObj = item.CreateItem44Image(cursor.Cursor, iShape)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_WARPREPAREITEM
    g_HandObj.m_ID = tItemID
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterLeftButtonHotKey(Clear)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldText(txt, font, color, callback, *args):
    global g_HandObj
    
    def holdCallback(*args):
        key.RegisterLeftButtonHotKey()
        callback(*args)

    g_HandObj = interface.CTextObject(cursor.Cursor, txt, font, color)
    (w, h) = g_HandObj.GetSize()
    g_HandObj.SetPos(-w / 2, -h / 2)
    g_HandObj.m_Type = TYPE_HOLDTEXT
    g_HandObj.m_Callback = holdCallback
    g_HandObj.m_Args = args
    key.RegisterLeftButtonHotKey(Clear)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldMagicIcon(sFileName, sPackage, callback, *args):
    global g_HandObj
    
    def holdCallback(*args):
        key.RegisterLeftButtonHotKey()
        callback(*args)

    import shortcut
    g_HandObj = shortcut.CSkillIcon(cursor.Cursor, sFileName, sPackage)
    g_HandObj.SetPos(-25, -25)
    g_HandObj.SetZ(-1)
    g_HandObj.m_Type = TYPE_HOLDMAGICICON
    g_HandObj.m_Callback = holdCallback
    g_HandObj.m_Args = args
    key.RegisterLeftButtonHotKey(Clear)
    key.RegisterRightButtonHotKey(Clear)


def HandHoldObj(obj, callback, *args):
    global g_HandObj
    
    def holdCallback(*args):
        key.RegisterLeftButtonHotKey()
        callback(*args)

    g_HandObj = obj
    g_HandObj.m_Type = TYPE_HOLDTEXT
    g_HandObj.m_Callback = holdCallback
    g_HandObj.m_Args = args
    key.RegisterLeftButtonHotKey(Clear)
    key.RegisterRightButtonHotKey(Clear)


def HandYardItemForLand(oObj, accept, callback, *args):
    '''
\t\xae\xb3\xb0_\xa4@\xad\xd3\xaa\xab\xab~\xa9\xf1\xa6b\xaex\xb0|\xa6a\xb9\xcf\xa4W
\t'''
    global g_HandObj
    g_HandObj = oObj
    g_HandObj.m_Type = TYPE_YARD_LAND
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterLeftButtonHotKey(CheckHoldHandAndAccept)
    key.RegisterRightButtonHotKey(CheckHoldHandAndClear)


def HandYardItemForLand_Continue(oObj, accept, callback, *args):
    '''
\t\xae\xb3\xb0_\xa4@\xad\xd3\xaa\xab\xab~\xa9\xf1\xa6b\xaex\xb0|\xa6a\xb9\xcf\xa4W
\t'''
    global g_HandObj
    g_HandObj = oObj
    g_HandObj.m_Type = TYPE_YARD_LAND
    g_HandObj.m_Accept = accept
    g_HandObj.m_Callback = callback
    g_HandObj.m_Args = args
    key.RegisterLeftButtonHotKey(CheckHoldHandAndAccept_Continue)
    key.RegisterRightButtonHotKey(CheckHoldHandAndClear)


def SetSaleShow(obj, x, y):
    obj.SetShow(True)
    (curx, cury) = obj.GetPos()
    obj.SetPos(curx + x, cury + y)
    obj.m_X = curx + x
    obj.m_Y = cury + y


def CheckHoldHand():
    global g_HandObj
    import cursor
    import key
    import C_sys
    (x, y) = cursor.GetCursorPos()
    handObj = g_HandObj
    key.RegisterLeftButtonHotKey()
    key.RegisterRightButtonHotKey()
    g_HandObj = None
    objLst = C_sys.GetObjects(x, y)
    if handObj and objLst and len(objLst):
        if hasattr(objLst[0], 'OnHoldHand'):
            objLst[0].OnHoldHand(handObj)
        
    


def ClearUp(hx, hy):
    import world
    import addon
    import map
    (x, y) = cursor.GetCursorPos()
    
    try:
        (mapx, mapy) = map.g_Map.GetPos()
        x -= mapx
        y -= mapy
    except AttributeError:
        pass

    x = x - hx
    y = y - hy
    key.RegisterLeftButtonHotKey()
    for obj in world.g_Objects.values():
        if hasattr(obj, 'm_Addons'):
            for k in (addon.SALE_KEY, addon.SLOOK_KEY, addon.SSIGN_KEY):
                addons = obj.m_Addons.get(k)
                if addons and not addons.GetShow():
                    SetSaleShow(addons, x, y)
                    return None
                    continue
            
    


def Clear():
    global g_HandObj
    if g_HandObj:
        hand = g_HandObj
        key.RegisterRightButtonHotKey()
        key.RegisterLeftButtonHotKey()
        g_HandObj = None
        if hasattr(hand, 'm_Callback') and hand.m_Callback:
            hand.m_Callback(*hand.m_Args)
        
    


def CheckHoldHandAndClear():
    global g_HandObj
    (x, y) = cursor.GetCursorPos()
    handObj = g_HandObj
    g_HandObj = None
    key.RegisterLeftButtonHotKey()
    key.RegisterRightButtonHotKey()
    if not handObj:
        return None
    
    import C_sys
    objLst = C_sys.GetObjects(x, y)
    if objLst and len(objLst) and hasattr(objLst[0], 'OnHoldHand'):
        objLst[0].OnHoldHand(handObj)
    
    if hasattr(handObj, 'm_Callback') and handObj.m_Callback:
        handObj.m_Callback(*handObj.m_Args)
    


def Accept():
    global g_HandObj
    if g_HandObj:
        hand = g_HandObj
        key.RegisterLeftButtonHotKey()
        key.RegisterRightButtonHotKey()
        g_HandObj = None
        if hand.m_Accept:
            hand.m_Accept()
        
    


def CheckHoldHandAndAccept():
    global g_HandObj
    (x, y) = cursor.GetCursorPos()
    handObj = g_HandObj
    g_HandObj = None
    key.RegisterLeftButtonHotKey()
    key.RegisterRightButtonHotKey()
    if not handObj:
        return None
    
    import C_sys
    objLst = C_sys.GetObjects(x, y)
    if objLst and len(objLst) and hasattr(objLst[0], 'OnHoldHand'):
        objLst[0].OnHoldHand(handObj)
    
    if handObj.m_Accept:
        handObj.m_Accept()
    


def CheckHoldHandAndAccept_Continue():
    (x, y) = cursor.GetCursorPos()
    handObj = g_HandObj
    if not handObj:
        return None
    
    import C_sys
    objLst = C_sys.GetObjects(x, y)
    if objLst and len(objLst) and hasattr(objLst[0], 'OnHoldHand'):
        objLst[0].OnHoldHand(handObj)
    
    if handObj.m_Accept:
        handObj.m_Accept()
    


def IsHand():
    return g_HandObj is not None


def GetHand(typestr):
    if g_HandObj and g_HandObj.m_Type == typestr:
        return g_HandObj
