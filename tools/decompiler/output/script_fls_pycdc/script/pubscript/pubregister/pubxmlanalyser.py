# pycdc 交叉复核产物 · script.fls entry 573
# co_filename(原始)='script/pubscript/pubregister/pubxmlanalyser.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_573.pyc (Python 2.5)

import pubXMLTree

def GetData(data):
    analyser = CAnalyser(data)
    return analyser.GetData()


def Parse(data, succeed):
    if not succeed and data:
        return False
    
    (head, body) = data.split('\r\n\r\n', 1)
    if not body:
        return False
    
    ana = CAnalyser(body)
    d = ana.GetData()
    if not d:
        return False
    
    return d


class XMLParser(pubXMLTree.XMLParser):
    PattDict = { }
    
    def GetPattern(self, expression):
        if expression not in self.PattDict:
            import re
            self.PattDict[expression] = re.compile(expression)
        
        return self.PattDict[expression]

    
    def Parse(self):
        document = self.m_document
        patt = self.GetPattern('<?[^)]+?>')
        mo = patt.search(document)
        if mo:
            document = document[:mo.start()] + document[mo.end():]
        
        patt = self.GetPattern('<![^)]+?>')
        mo = patt.search(document)
        if mo:
            document = document[:mo.start()] + document[mo.end():]
        
        while document:
            patt = self.GetPattern('[\\s]+<')
            mo = patt.search(document)
            if mo:
                document = document.replace(mo.group(), '<')
                continue
            patt = self.GetPattern('>[\\s]+')
            mo = patt.search(document)
            if mo:
                document = document.replace(mo.group(), '>')
                continue
            break
        patt = self.GetPattern('<[^<^>]+>')
        mo = patt.search(document)
        if not mo:
            self.ClearUp()
            return None
        
        self.m_root = pubXMLTree.XMLNode()
        self.m_root.m_name = document[mo.start() + 1:mo.end() - 1].split()[0]
        self.m_stack.append(self.m_root)
        document = document[mo.end():]
        while document:
            if not self.m_stack:
                return None
            
            node = self.m_stack.pop()
            if document[0] != '<':
                patt = self.GetPattern('[^<^>]+')
                mo = patt.search(document)
                tmptxt = mo.group()
                patt = self.GetPattern('&lt;!\\[CDATA\\[(?P<txt>[\\s\\S]*)\\]\\]&gt;')
                tmpmo = patt.search(tmptxt)
                if tmpmo:
                    tmptxt = tmpmo.group('txt')
                
                node.m_txt += tmptxt
                document = document[mo.end():]
                self.m_stack.append(node)
                continue
                continue
            node
            
            try:
                document[1]
            except BaseException:
                self.ClearUp()
                return None

            if document[1] == '/':
                patt = self.GetPattern('</[^<^>]+>')
                mo = patt.search(document)
                if not mo:
                    self.ClearUp()
                    return None
                
                if node.m_name != document[mo.start() + 2:mo.end() - 1].split()[0]:
                    self.ClearUp()
                    return None
                else:
                    document = document[mo.end():]
            node.m_name != document[mo.start() + 2:mo.end() - 1].split()[0]
            patt = self.GetPattern('<[^<^>]+>')
            mo = patt.search(document)
            if not mo:
                self.ClearUp()
                return None
                continue
            if document[mo.end() - 2] != '/':
                tempnode = pubXMLTree.XMLNode()
                tempnode.m_name = document[mo.start() + 1:mo.end() - 1].split()[0]
                node.m_lsChildren.append(tempnode)
                self.m_stack.append(node)
                self.m_stack.append(tempnode)
                document = document[mo.end():]
                continue
                continue
            tempnode = pubXMLTree.XMLNode()
            tempnode.m_name = document[mo.start() + 1:mo.end() - 2].split()[0]
            node.m_lsChildren.append(tempnode)
            self.m_stack.append(node)
            document = document[mo.end():]
            continue



class CAnalyser(object):
    
    def __init__(self, document):
        parser = XMLParser(document)
        parser.Parse()
        self.m_Tree = parser.m_root
        self.m_Data = { }
        self.DoTrans()

    
    def DoTrans(self):
        if not self.m_Tree:
            return None
        
        root = self.m_Tree
        l = root.GetChildren()
        for node in l:
            if node.m_name not in 'plist':
                root = node
                break
                continue
        
        self.Trans(root, True, None)

    
    def GetData(self):
        return self.m_Data

    
    def IsParentObj(self, node):
        return node.m_name in ('dict', 'array')

    
    def GetParentObj(self, node):
        if node.m_name == 'dict':
            return { }
        elif node.m_name == 'array':
            return []
        else:
            return None

    
    def GetChildObj(self, node):
        if node.m_name == 'string':
            return node.m_txt
        elif node.m_name == 'integer':
            return int(node.m_txt)
        elif node.m_name in ('true', 'false'):
            return 'true' == node.m_name
        else:
            return None

    
    def Trans(self, curnode, is_root, parentobj):
        nodetype = curnode.m_name
        childnodes = curnode.GetChildren()
        childcnt = len(childnodes)
        if nodetype == 'dict' and childcnt != 0 and childcnt % 2 == 0:
            for idx in xrange(0, childcnt, 2):
                key_node = childnodes[idx]
                value_node = childnodes[idx + 1]
                if key_node.m_name == 'key':
                    pass
                None if self.IsParentObj(value_node) else is_root
            
        elif nodetype == 'array':
            if is_root:
                self.m_Data['array'] = []
                parentobj = self.m_Data['array']
            
            for idx in xrange(0, childcnt):
                node = childnodes[idx]
                if self.IsParentObj(node):
                    obj = self.GetParentObj(node)
                    parentobj.append(obj)
                    self.Trans(node, False, obj)
                    continue
                obj = self.GetChildObj(node)
                parentobj.append(obj)
