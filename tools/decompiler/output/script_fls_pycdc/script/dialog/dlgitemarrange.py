# pycdc 交叉复核产物 · script.fls entry 471
# co_filename(原始)='script/dialog/dlgitemarrange.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_471.pyc (Python 2.5)

import c2sitemuicom
import interface
import net
import permission
import wrapinterface
import combdialog
import item
WITHOUT_ARRANGE_ITEM_LIST = [
    30036,
    25013,
    31031,
    40031,
    25052,
    25053,
    25424,
    30031,
    25421,
    30044]
g_ItemLock = None
g_PrevShape = None
g_PrevIdx = 0

def ModuleReset():
    global g_ItemLock, g_PrevShape, g_PrevIdx
    g_ItemLock = None
    g_PrevShape = None
    g_PrevIdx = 0


class CItemLock(combdialog.CCombDialog):
    
    def __init__(self, msgs):
        combdialog.CCombDialog.__init__(self, interface.CapturePanel, 'dialog/itemlock.dlg')
        interface.Center(self)
        self.Capture(1, 0)
        self.m_InterfaceItems = { }
        self.m_Boxs_Data = [
            ('itembox', item.ITEM_START, 30),
            ('fight_item_box', item.ITEM_FIGHT_START, 10),
            ('itembox2', item.ITEM_SCOPE, 40)]
        for k, v in enumerate(self.m_Boxs_Data):
            obj = self.GetObject(v[0])
            for i in xrange(v[2]):
                pos = i + v[1]
                (x, \xa9) = obj.m_Imagess[i].GetPos()
                iit = item.CInterfaceItem(obj, x, \xa9, pos + 100, self.m_InterfaceItems)
                iit.Refresh(pos)
                if hasattr(iit.m_SelBox, 'SetFrame'):
                    iit.m_SelBox.SetFrame(0)
                    continue
            
        
        self.UpdateBag()
        self.m_SelectItemPos = []
        import combmacro
        self.m_Note = combmacro.CRICHTEXT(interface.CRichTextObject, 'msgs', self, msgs, interface.FontLT14_3, interface.COLOR_4, align = interface.ALIGN_LEFT | interface.ALIGN_MIDDLE)

    
    def UpdateBag(self, num = None):
        import hero
        if num is None:
            num = hero.g_Prop.m_BagMax
        
        for i in xrange(num, 40):
            pos = i + item.ITEM_SCOPE
            iit = self.m_InterfaceItems.get(pos)
            if iit:
                iit.Enable(False)
                continue
        

    
    def GetSelectedItem(self):
        select_item = []
        for i, idx in enumerate(self.m_InterfaceItems):
            iif = self.m_InterfaceItems[idx]
            it = iif.GetItem()
            if iif.IsSelected():
                select_item.append(idx)
                continue
        
        return select_item

    
    def Refresh(self, data):
        for v in data:
            if v in self.m_InterfaceItems:
                it = self.m_InterfaceItems[v]
                if not hasattr(it, 'm_EnableFlag') and it.m_EnableFlag == False:
                    it.Select(True)
                
            it.m_EnableFlag == False
        

    
    def OnMessage(self, msgid):
        print 'msgid', msgid
        import item
        if msgid == 1:
            self.SetShow(False)
        
        if msgid == 3:
            self.m_SelectItemPos = self.GetSelectedItem()
            C2SItemLock(self.m_SelectItemPos)
            self.OnMessage(1)
        elif msgid - 100 <= msgid - 100:
            pass
        elif msgid - 100 < item.ITEM_FIGHT_SCOPE + 40:
            idx = msgid - 100
            iif = self.m_InterfaceItems[idx]
            iif.Select(not iif.IsSelected())
        



def ShowLock(data = None):
    global g_ItemLock
    if data is None:
        data = []
    
    g_ItemLock = CItemLock('\xa5\xaa\xc1\xe4\xa5i\xc2\xea\xa9w\xa9\xce\xb8\xd1\xc2\xea\xaa\xab\xab~\xae\xe6\xa4l\xa1A\xc2\xea\xa9w\xae\xe6\xa4l\xb8\xcc\xaa\xba\xaa\xab\xab~\xa4\xa3\xb7|\xb3Q\xa6\xdb\xb0\xca\xbe\xe3\xb2z#r\xb5\xf9\xa1G\xa4\xa3\xb7|\xa6\xdb\xb0\xca\xbe\xe3\xb2z\xad\xb8\xa6\xe6\xc3\xfe\xb9D\xa8\xe3')
    g_ItemLock.Refresh(data)


def ItemWithoutArrange():
    posLst = []
    import hero
    for i in xrange(item.ITEM_START, item.ITEM_SCOPE + hero.g_Prop.m_BagMax):
        iif = GetItemWithPos(i)
        if iif and iif.m_Shape in WITHOUT_ARRANGE_ITEM_LIST:
            posLst.append(iif.m_Pos)
            continue
    
    import withoutarrangedata
    import itemdata
    for i in xrange(item.ITEM_FIGHT_START, item.ITEM_FIGHT_SCOPE):
        iif = GetItemWithPos(i)
        if iif:
            if iif.m_Shape in withoutarrangedata.DATA or itemdata.IsType(iif.m_Shape, 'weapon'):
                posLst.append(iif.m_Pos)
                continue
    
    return posLst


def ArrangeItem(data):
    import hero
    max_bag = hero.g_Prop.m_BagMax
    interfaceItems = []
    itemPos = { }
    empty = []
    data.extend(ItemWithoutArrange())
    for i in xrange(item.ITEM_START, item.ITEM_SCOPE + max_bag):
        if i not in data:
            iif = GetItemWithPos(i)
            if iif:
                it = interface.CBaseObject(None)
                it.m_ID = iif.m_ID
                it.m_Shape = iif.m_Shape
                it.m_Pos = iif.m_Pos
                it.m_Quantity = iif.m_Quantity
                it.m_Key = iif.m_Key
                it.m_ExtName = iif.GetExtName()
                itemPos[it.m_Pos] = it
                interfaceItems.append(it)
            
            empty.append(i)
            continue
    
    for i in xrange(item.ITEM_FIGHT_START, item.ITEM_FIGHT_SCOPE):
        if i not in data:
            iif = GetItemWithPos(i)
            if iif:
                it = interface.CBaseObject(None)
                it.m_ID = iif.m_ID
                it.m_Shape = iif.m_Shape
                it.m_Pos = iif.m_Pos
                it.m_Quantity = iif.m_Quantity
                it.m_Key = iif.m_Key
                it.m_ExtName = iif.GetExtName()
                itemPos[it.m_Pos] = it
                interfaceItems.append(it)
            
            empty.append(i)
            continue
    
    import itemprioritydata
    prioList = itemprioritydata.GetPrioList()
    prioData = itemprioritydata.GetPrioData()
    specialPrioList = itemprioritydata.GetSpePrioList()
    specialPrioData = itemprioritydata.GetSpePrioData()
    
    def keyFunc(it):
        shape = it.m_Shape
        if shape in prioList:
            prio = prioData[shape]
            return (0, prio)
        
        for func in specialPrioList:
            if func(shape):
                prio = specialPrioData[func]
                equipPriority = itemprioritydata.GetEquipPriority(shape)
                return (0, prio + equipPriority)
                continue
        
        return (1, shape)

    
    def keyfunc2(it):
        global g_PrevShape, g_PrevIdx, g_PrevShape
        if not g_PrevShape:
            g_PrevShape = it.m_Shape
        
        if it.m_Shape != g_PrevShape:
            g_PrevIdx += 1
            g_PrevShape = it.m_Shape
        
        if it.m_Key & 64 != 0:
            return (g_PrevIdx, 0)
        else:
            return (g_PrevIdx, it.m_Quantity)

    
    def keyfunc3(it):
        global g_PrevShape, g_PrevIdx, g_PrevShape
        if not g_PrevShape:
            g_PrevShape = it.m_Shape
        
        if it.m_Shape != g_PrevShape:
            g_PrevIdx += 1
            g_PrevShape = it.m_Shape
        
        if it.m_Key & 64 != 0:
            return (g_PrevIdx, 0)
        else:
            return (g_PrevIdx, it.m_ExtName)

    interfaceItems.sort(key = keyFunc)
    interfaceItems.sort(key = keyfunc2)
    interfaceItems.sort(key = keyfunc3)
    len_items = len(interfaceItems)
    empty.sort(cmp)
    action = []
    m1 = { }
    m2 = { }
    for i, v in enumerate(empty):
        if i < len_items:
            it = interfaceItems[i]
            if v != it.m_Pos:
                action.append((it.m_Pos, v))
                m1[v] = it.m_Pos
                m2[it.m_Pos] = v
            
        v != it.m_Pos
    
    operation = []
    for v in action:
        if m1[v[1]] != v[1]:
            operation.append((m1[v[1]], v[1]))
            if v[1] in m2:
                m1[m2[v[1]]] = m1[v[1]]
                m2[m1[v[1]]] = m2[v[1]]
            
        v[1] in m2
    
    C2SItemArrange(operation)


def GetItemWithPos(pos):
    itype = item.ITEM_NORMAL
    it = item.g_Items[itype].get(pos)
    if it:
        return it
    


def C2SItemLock(data):
    if permission.IsOpenUICom():
        netobj = c2sitemuicom.GetUIComItemNetObj(19)
    else:
        netobj = net.g_Net
        netobj.PacketPrepare(net.C2GS_OPEN_UI)
        netobj.PacketAddI(81, 1)
    netobj.PacketAddI(len(data), 1)
    for v in data:
        netobj.PacketAddI(v, 1)
    
    netobj.PacketSend()


def C2SItemArrange(data):
    if len(data) > 120:
        return None
    
    netobj = net.g_Net
    netobj.PacketPrepare(net.C2GS_OPEN_UI)
    netobj.PacketAddI(82, 1)
    netobj.PacketAddI(len(data), 1)
    for v in data:
        netobj.PacketAddI(v[0], 1)
        netobj.PacketAddI(v[1], 1)
    
    netobj.PacketSend()
