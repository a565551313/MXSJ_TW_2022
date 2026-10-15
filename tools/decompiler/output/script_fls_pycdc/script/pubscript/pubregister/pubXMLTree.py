# pycdc 交叉复核产物 · script.fls entry 1029
# co_filename(原始)='script/pubscript/pubregister/pubXMLTree.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1029.pyc (Python 2.5)

import re

class XMLNode:
    
    def __init__(self):
        self.m_name = None
        self.m_lsChildren = []
        self.m_txt = ''

    
    def GetSection(self, name):
        for node in self.m_lsChildren:
            if node.m_name == name:
                return node
                continue
        

    
    def GetElems(self, name):
        nodelist = []
        for node in self.m_lsChildren:
            if node.m_name == name:
                nodelist.append(node)
                continue
        
        return nodelist

    
    def GetChildren(self):
        return self.m_lsChildren



class XMLParser:
    
    def __init__(self, document):
        self.m_document = document
        self.m_stack = []
        self.m_root = None

    
    def Parse(self):
        document = self.m_document
        patt = re.compile('<?[^)]+?>')
        mo = patt.search(document)
        if mo:
            document = document[:mo.start()] + document[mo.end():]
        
        while document:
            patt = re.compile('[\\s]+<')
            mo = patt.search(document)
            if mo:
                document = document.replace(mo.group(), '<')
                continue
            patt = re.compile('>[\\s]+')
            mo = patt.search(document)
            if mo:
                document = document.replace(mo.group(), '>')
                continue
            break
        patt = re.compile('<[^<>]+>')
        mo = patt.search(document)
        if not mo:
            self.ClearUp()
            return None
        
        self.m_root = XMLNode()
        self.m_root.m_name = document[mo.start() + 1:mo.end() - 1].split()[0]
        self.m_stack.append(self.m_root)
        document = document[mo.end():]
        while document:
            node = self.m_stack.pop()
            if document[0] != '<':
                patt = re.compile('[^<>]+')
                mo = patt.search(document)
                node.m_txt += mo.group()
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
                patt = re.compile('</[^<>]+>')
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
            patt = re.compile('<[^<>]+>')
            mo = patt.search(document)
            if not mo:
                self.ClearUp()
                return None
                continue
            if document[mo.end() - 2] != '/':
                tempnode = XMLNode()
                tempnode.m_name = document[mo.start() + 1:mo.end() - 1].split()[0]
                [
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    node.m_lsChildren](tempnode)
                self.m_stack.append(node)
                self.m_stack.append(tempnode)
                document = document[mo.end():]
                continue
                continue
            tempnode = XMLNode()
            tempnode.m_name = document[mo.start() + 1:mo.end() - 2].split()[0]
            node.m_lsChildren.append(tempnode)
            self.m_stack.append(node)
            document = document[mo.end():]
            continue

    
    def ClearUp(self):
        self.m_stack = []
        self.m_root = None
        self.m_document = None
