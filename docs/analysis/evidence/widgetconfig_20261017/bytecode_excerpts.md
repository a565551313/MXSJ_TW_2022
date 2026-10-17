# 原生转译字节码摘录

仅反汇编；未执行。偏移是转译后函数内部偏移，不是原始 fls 偏移。跳转接缝不作为独立证据；报告采用表值、常量、字段访问和调用链交叉确认。

## entry 3853: <module>/Code2Color4RichText

```text
<module>/Code2Color4RichText
NAMES ['split', 'int', 'eval']
CONSTS None, ',', 0, '0x%s', 1, 3, 5, 7
    0 LOAD_FAST            0     
    3 LOAD_ATTR            0     split
    6 LOAD_CONST           1     ','
    9 CALL_FUNCTION        1     
   12 STORE_FAST           1     
   15 LOAD_FAST            1     
   18 LOAD_CONST           2     0
   21 BINARY_SUBSCR        None  
   22 STORE_FAST           0     
   25 LOAD_GLOBAL          1     int
   28 LOAD_GLOBAL          2     eval
   31 LOAD_CONST           3     '0x%s'
   34 LOAD_FAST            0     
   37 LOAD_CONST           4     1
   40 LOAD_CONST           5     3
   43 33                   None  
   44 22                   None  
   45 CALL_FUNCTION        1     
   48 CALL_FUNCTION        1     
   51 LOAD_GLOBAL          1     int
   54 LOAD_GLOBAL          2     eval
   57 LOAD_CONST           3     '0x%s'
   60 LOAD_FAST            0     
   63 LOAD_CONST           5     3
   66 LOAD_CONST           6     5
   69 33                   None  
   70 22                   None  
   71 CALL_FUNCTION        1     
   74 CALL_FUNCTION        1     
   77 LOAD_GLOBAL          1     int
   80 LOAD_GLOBAL          2     eval
   83 LOAD_CONST           3     '0x%s'
   86 LOAD_FAST            0     
   89 LOAD_CONST           6     5
   92 LOAD_CONST           7     7
   95 33                   None  
   96 22                   None  
   97 CALL_FUNCTION        1     
  100 CALL_FUNCTION        1     
  103 BUILD_LIST           3     
  106 RETURN_VALUE         None  

```

## entry 3853: <module>/TableStyleChgFunc

```text
<module>/TableStyleChgFunc
NAMES ['isdigit', 'int']
CONSTS None, 'None'
    0 LOAD_FAST            0     
    3 LOAD_ATTR            0     isdigit
    6 CALL_FUNCTION        0     
    9 JUMP_IF_FALSE        14    
   12 POP_TOP              None  
   13 LOAD_GLOBAL          1     int
   16 LOAD_FAST            0     
   19 CALL_FUNCTION        1     
   22 RETURN_VALUE         None  
   23 JUMP_FORWARD         5     
   26 POP_TOP              None  
   27 LOAD_CONST           1     'None'
   30 RETURN_VALUE         None  
   31 LOAD_CONST           0     None
   34 RETURN_VALUE         None  

```

## entry 3853: <module>/GetOldFontAlight

```text
<module>/GetOldFontAlight
NAMES []
CONSTS None, '右對齊', '中對齊', '左對齊'
    0 LOAD_CONST           1     '右對齊'
    3 LOAD_CONST           2     '中對齊'
    6 LOAD_CONST           3     '左對齊'
    9 BUILD_LIST           3     
   12 RETURN_VALUE         None  

```

## entry 3853: <module>/GetFontAlight

```text
<module>/GetFontAlight
NAMES []
CONSTS None, '左上', '中上', '右上', '左中', '中中', '右中', '左下', '中下', '右下'
    0 LOAD_CONST           1     '左上'
    3 LOAD_CONST           2     '中上'
    6 LOAD_CONST           3     '右上'
    9 LOAD_CONST           4     '左中'
   12 LOAD_CONST           5     '中中'
   15 LOAD_CONST           6     '右中'
   18 LOAD_CONST           7     '左下'
   21 LOAD_CONST           8     '中下'
   24 LOAD_CONST           9     '右下'
   27 BUILD_LIST           9     
   30 RETURN_VALUE         None  
```

## entry 579: <module>/GetFrameCutClass

```text
<module>/GetFrameCutClass
NAMES ['interface', 'CStretchBitmapObjectExt', 'CCutImagesObject', 'CBitmapObjectWithAlpha', 'CImagesObject']
CONSTS None
    0 LOAD_FAST            1     
    3 JUMP_IF_FALSE        18    
    6 POP_TOP              None  
    7 LOAD_FAST            0     
   10 JUMP_IF_FALSE        11    
   13 POP_TOP              None  
   14 LOAD_GLOBAL          0     interface
   17 LOAD_ATTR            1     CStretchBitmapObjectExt
   20 RETURN_VALUE         None  
   21 JUMP_FORWARD         53    
   24 POP_TOP              None  
   25 LOAD_FAST            1     
   28 JUMP_IF_FALSE        19    
   31 POP_TOP              None  
   32 LOAD_FAST            0     
   35 12                   None  
   36 JUMP_IF_FALSE        11    
   39 POP_TOP              None  
   40 LOAD_GLOBAL          0     interface
   43 LOAD_ATTR            2     CCutImagesObject
   46 RETURN_VALUE         None  
   47 JUMP_FORWARD         27    
   50 POP_TOP              None  
   51 LOAD_FAST            1     
   54 12                   None  
   55 JUMP_IF_FALSE        18    
   58 POP_TOP              None  
   59 LOAD_FAST            0     
   62 JUMP_IF_FALSE        11    
   65 POP_TOP              None  
   66 LOAD_GLOBAL          0     interface
   69 LOAD_ATTR            3     CBitmapObjectWithAlpha
   72 RETURN_VALUE         None  
   73 JUMP_FORWARD         1     
   76 POP_TOP              None  
   77 LOAD_GLOBAL          0     interface
   80 LOAD_ATTR            4     CImagesObject
   83 RETURN_VALUE         None  

```

## entry 579: <module>/GetFileExtention

```text
<module>/GetFileExtention
NAMES []
CONSTS None, '.png', '.igs'
    0 LOAD_FAST            0     
    3 JUMP_IF_FALSE        8     
    6 POP_TOP              None  
    7 LOAD_CONST           1     '.png'
   10 RETURN_VALUE         None  
   11 JUMP_FORWARD         1     
   14 POP_TOP              None  
   15 LOAD_CONST           2     '.igs'
   18 RETURN_VALUE         None  

```

## entry 579: <module>/GetCreateFrameFunc

```text
<module>/GetCreateFrameFunc
NAMES ['CCreateFrameBase', 'CreatePngNineFrame', 'CreateFrame']
CONSTS None
    0 LOAD_FAST            0     
    3 JUMP_IF_FALSE        11    
    6 POP_TOP              None  
    7 LOAD_GLOBAL          0     CCreateFrameBase
   10 LOAD_ATTR            1     CreatePngNineFrame
   13 RETURN_VALUE         None  
   14 JUMP_FORWARD         1     
   17 POP_TOP              None  
   18 LOAD_GLOBAL          0     CCreateFrameBase
   21 LOAD_ATTR            2     CreateFrame
   24 RETURN_VALUE         None  

```

## entry 579: <module>/CTextFrame/SetText

```text
<module>/CTextFrame/SetText
NAMES ['m_Text', 'replace', 'splitlines', 'm_TextObjects', 'len', 'interface', 'CTextObject', 'm_Font', 'm_Color', 'GetSize', 'append', 'enumerate', 'm_Align', 'SetPos', 'm_Space', 'm_Size']
CONSTS None, '\\n', '\n', 0, 1, 2
    0 LOAD_FAST            1     
    3 LOAD_FAST            0     
    6 STORE_ATTR           0     m_Text
    9 LOAD_FAST            1     
   12 LOAD_ATTR            1     replace
   15 LOAD_CONST           1     '\\n'
   18 LOAD_CONST           2     '\n'
   21 CALL_FUNCTION        2     
   24 LOAD_ATTR            2     splitlines
   27 CALL_FUNCTION        0     
   30 STORE_FAST           2     
   33 BUILD_LIST           0     
   36 LOAD_FAST            0     
   39 STORE_ATTR           3     m_TextObjects
   42 LOAD_CONST           3     0
   45 STORE_FAST           3     
   48 SETUP_LOOP           121   
   51 LOAD_FAST            2     
   54 68                   None  
   55 FOR_ITER             113   
   58 STORE_FAST           4     
   61 LOAD_GLOBAL          4     len
   64 LOAD_FAST            4     
   67 CALL_FUNCTION        1     
   70 JUMP_IF_FALSE        94    
   73 POP_TOP              None  
   74 LOAD_GLOBAL          5     interface
   77 LOAD_ATTR            6     CTextObject
   80 LOAD_FAST            0     
   83 LOAD_FAST            4     
   86 LOAD_FAST            0     
   89 LOAD_ATTR            7     m_Font
   92 LOAD_FAST            0     
   95 LOAD_ATTR            8     m_Color
   98 LOAD_CONST           3     0
  101 CALL_FUNCTION        5     
  104 STORE_FAST           5     
  107 LOAD_FAST            5     
  110 LOAD_ATTR            9     GetSize
  113 CALL_FUNCTION        0     
  116 UNPACK_SEQUENCE      2     
  119 STORE_FAST           6     
  122 STORE_FAST           7     
  125 LOAD_FAST            3     
  128 LOAD_FAST            6     
  131 COMPARE_OP           0     
  134 JUMP_IF_FALSE        10    
  137 POP_TOP              None  
  138 LOAD_FAST            6     
  141 STORE_FAST           3     
  144 JUMP_FORWARD         1     
  147 POP_TOP              None  
  148 LOAD_FAST            0     
  151 LOAD_ATTR            3     m_TextObjects
  154 LOAD_ATTR            10    append
  157 LOAD_FAST            5     
  160 CALL_FUNCTION        1     
  163 POP_TOP              None  
  164 JUMP_ABSOLUTE        55    
  167 POP_TOP              None  
  168 JUMP_ABSOLUTE        55    
  171 87                   None  
  172 LOAD_CONST           3     0
  175 STORE_FAST           8     
  178 SETUP_LOOP           150   
  181 LOAD_GLOBAL          11    enumerate
  184 LOAD_FAST            0     
  187 LOAD_ATTR            3     m_TextObjects
  190 CALL_FUNCTION        1     
  193 68                   None  
  194 FOR_ITER             133   
  197 UNPACK_SEQUENCE      2     
  200 STORE_FAST           9     
  203 STORE_FAST           5     
  206 LOAD_FAST            5     
  209 LOAD_ATTR            9     GetSize
  212 CALL_FUNCTION        0     
  215 UNPACK_SEQUENCE      2     
  218 STORE_FAST           6     
  221 STORE_FAST           7     
  224 LOAD_FAST            0     
  227 LOAD_ATTR            12    m_Align
  230 LOAD_CONST           4     1
  233 COMPARE_OP           2     
  236 JUMP_IF_FALSE        18    
  239 POP_TOP              None  
  240 LOAD_FAST            3     
  243 LOAD_FAST            6     
  246 24                   None  
  247 LOAD_CONST           5     2
  250 21                   None  
  251 STORE_FAST           10    
  254 JUMP_FORWARD         37    
  257 POP_TOP              None  
  258 LOAD_FAST            0     
  261 LOAD_ATTR            12    m_Align
  264 LOAD_CONST           5     2
  267 COMPARE_OP           2     
  270 JUMP_IF_FALSE        10    
  273 POP_TOP              None  
  274 LOAD_CONST           3     0
  277 STORE_FAST           10    
  280 JUMP_FORWARD         11    
  283 POP_TOP              None  
  284 LOAD_FAST            3     
  287 LOAD_FAST            6     
  290 24                   None  
  291 STORE_FAST           10    
  294 LOAD_FAST            5     
  297 LOAD_ATTR            13    SetPos
  300 LOAD_FAST            10    
  303 LOAD_FAST            9     
  306 LOAD_FAST            7     
  309 LOAD_FAST            0     
  312 LOAD_ATTR            14    m_Space
  315 BINARY_ADD           None  
  316 20                   None  
  317 CALL_FUNCTION        2     
  320 POP_TOP              None  
  321 LOAD_FAST            7     
  324 STORE_FAST           8     
  327 JUMP_ABSOLUTE        194   
  330 87                   None  
  331 LOAD_FAST            3     
  334 LOAD_GLOBAL          4     len
  337 LOAD_FAST            0     
  340 LOAD_ATTR            3     m_TextObjects
  343 CALL_FUNCTION        1     
  346 LOAD_CONST           4     1
  349 24                   None  
  350 LOAD_FAST            8     
  353 LOAD_FAST            0     
  356 LOAD_ATTR            14    m_Space
  359 BINARY_ADD           None  
  360 20                   None  
  361 LOAD_FAST            8     
  364 BINARY_ADD           None  
  365 BUILD_TUPLE          2     
  368 LOAD_FAST            0     
  371 STORE_ATTR           15    m_Size
  374 LOAD_CONST           0     None
  377 RETURN_VALUE         None  

```

## entry 1963: <module>/CProgress/SetRate

```text
<module>/CProgress/SetRate
NAMES ['max', 'min', 'm_Rate', 'm_ChangeCB', 'callable', 'int', 'm_Width', 'm_Space', 'm_BarObj', 'SetShow', 'False', 'True', 'interface', 'IsNew9Frame', 'm_BarPath', 'UIPath', 'GetOrgSize', 'SetRenderType', 'bitmapframe', 'TITLE_RENDER', 'NEW_9_FRAME_RENDER', 'SetWidth']
CONSTS '\n\t\t:param iRate: 設置百分比 1000為100%\n\t\t:param bForce: 是否強制刷新\n\t\t:return:\n\t\t', 0, 1000, None, 2, 1
    0 LOAD_GLOBAL          0     max
    3 LOAD_CONST           1     0
    6 LOAD_FAST            1     
    9 CALL_FUNCTION        2     
   12 STORE_FAST           1     
   15 LOAD_GLOBAL          1     min
   18 LOAD_CONST           2     1000
   21 LOAD_FAST            1     
   24 CALL_FUNCTION        2     
   27 STORE_FAST           1     
   30 LOAD_FAST            0     
   33 LOAD_ATTR            2     m_Rate
   36 LOAD_FAST            1     
   39 COMPARE_OP           2     
   42 JUMP_IF_FALSE        16    
   45 POP_TOP              None  
   46 LOAD_FAST            2     
   49 12                   None  
   50 JUMP_IF_FALSE        8     
   53 POP_TOP              None  
   54 LOAD_CONST           3     None
   57 RETURN_VALUE         None  
   58 JUMP_FORWARD         1     
   61 POP_TOP              None  
   62 LOAD_FAST            1     
   65 LOAD_FAST            0     
   68 STORE_ATTR           2     m_Rate
   71 LOAD_FAST            0     
   74 LOAD_ATTR            3     m_ChangeCB
   77 JUMP_IF_FALSE        33    
   80 POP_TOP              None  
   81 LOAD_GLOBAL          4     callable
   84 LOAD_FAST            0     
   87 LOAD_ATTR            3     m_ChangeCB
   90 CALL_FUNCTION        1     
   93 JUMP_IF_FALSE        17    
   96 POP_TOP              None  
   97 LOAD_FAST            0     
  100 LOAD_ATTR            3     m_ChangeCB
  103 LOAD_FAST            1     
  106 CALL_FUNCTION        1     
  109 POP_TOP              None  
  110 JUMP_FORWARD         1     
  113 POP_TOP              None  
  114 LOAD_GLOBAL          5     int
  117 LOAD_FAST            0     
  120 LOAD_ATTR            6     m_Width
  123 LOAD_FAST            0     
  126 LOAD_ATTR            7     m_Space
  129 LOAD_CONST           4     2
  132 20                   None  
  133 24                   None  
  134 LOAD_FAST            1     
  137 20                   None  
  138 LOAD_CONST           2     1000
  141 21                   None  
  142 CALL_FUNCTION        1     
  145 STORE_FAST           3     
  148 LOAD_FAST            3     
  151 LOAD_CONST           5     1
  154 COMPARE_OP           0     
  157 JUMP_IF_FALSE        24    
  160 POP_TOP              None  
  161 LOAD_FAST            0     
  164 LOAD_ATTR            8     m_BarObj
  167 LOAD_ATTR            9     SetShow
  170 LOAD_GLOBAL          10    False
  173 CALL_FUNCTION        1     
  176 POP_TOP              None  
  177 LOAD_CONST           3     None
  180 RETURN_VALUE         None  
  181 JUMP_FORWARD         1     
  184 POP_TOP              None  
  185 LOAD_FAST            0     
  188 LOAD_ATTR            8     m_BarObj
  191 LOAD_ATTR            9     SetShow
  194 LOAD_GLOBAL          11    True
  197 CALL_FUNCTION        1     
  200 POP_TOP              None  
  201 LOAD_GLOBAL          12    interface
  204 LOAD_ATTR            13    IsNew9Frame
  207 LOAD_FAST            0     
  210 LOAD_ATTR            14    m_BarPath
  213 LOAD_GLOBAL          12    interface
  216 LOAD_ATTR            15    UIPath
  219 CALL_FUNCTION        2     
  222 JUMP_IF_FALSE        80    
  225 POP_TOP              None  
  226 LOAD_FAST            0     
  229 LOAD_ATTR            8     m_BarObj
  232 LOAD_ATTR            16    GetOrgSize
  235 CALL_FUNCTION        0     
  238 UNPACK_SEQUENCE      2     
  241 STORE_FAST           4     
  244 STORE_FAST           5     
  247 LOAD_FAST            3     
  250 LOAD_FAST            4     
  253 COMPARE_OP           0     
  256 JUMP_IF_FALSE        23    
  259 POP_TOP              None  
  260 LOAD_FAST            0     
  263 LOAD_ATTR            8     m_BarObj
  266 LOAD_ATTR            17    SetRenderType
  269 LOAD_GLOBAL          18    bitmapframe
  272 LOAD_ATTR            19    TITLE_RENDER
  275 CALL_FUNCTION        1     
  278 POP_TOP              None  
  279 JUMP_ABSOLUTE        306   
  282 POP_TOP              None  
  283 LOAD_FAST            0     
  286 LOAD_ATTR            8     m_BarObj
  289 LOAD_ATTR            17    SetRenderType
  292 LOAD_GLOBAL          18    bitmapframe
  295 LOAD_ATTR            20    NEW_9_FRAME_RENDER
  298 CALL_FUNCTION        1     
  301 POP_TOP              None  
  302 JUMP_FORWARD         1     
  305 POP_TOP              None  
  306 LOAD_FAST            0     
  309 LOAD_ATTR            8     m_BarObj
  312 LOAD_ATTR            21    SetWidth
  315 LOAD_FAST            3     
  318 CALL_FUNCTION        1     
  321 POP_TOP              None  
  322 LOAD_CONST           3     None
  325 RETURN_VALUE         None  

```

## entry 1963: <module>/CProgress/CreateBar

```text
<module>/CProgress/CreateBar
NAMES ['m_Width', 'm_Space', 'm_Offset', 'CheckIsImg', 'm_BarPath', 'interface', 'IsNew9Frame', 'UIPath', 'bitmapframe', 'CBitmapHFrame', 'm_BarObj', 'CImageHFrame', 'framewidget', 'CHProgressFrame', 'm_BgObj', 'None', 'GetSize', 'm_Height', 'SetPos', 'SetZ']
CONSTS None, 2, 0, 1
    0 LOAD_FAST            0     
    3 LOAD_ATTR            0     m_Width
    6 LOAD_FAST            0     
    9 LOAD_ATTR            1     m_Space
   12 LOAD_CONST           1     2
   15 20                   None  
   16 24                   None  
   17 STORE_FAST           1     
   20 LOAD_FAST            0     
   23 LOAD_ATTR            2     m_Offset
   26 LOAD_CONST           2     0
   29 BINARY_SUBSCR        None  
   30 LOAD_FAST            0     
   33 LOAD_ATTR            2     m_Offset
   36 LOAD_CONST           3     1
   39 BINARY_SUBSCR        None  
   40 BUILD_TUPLE          2     
   43 STORE_FAST           2     
   46 LOAD_GLOBAL          3     CheckIsImg
   49 LOAD_FAST            0     
   52 LOAD_ATTR            4     m_BarPath
   55 CALL_FUNCTION        1     
   58 JUMP_IF_FALSE        129   
   61 POP_TOP              None  
   62 LOAD_GLOBAL          5     interface
   65 LOAD_ATTR            6     IsNew9Frame
   68 LOAD_FAST            0     
   71 LOAD_ATTR            4     m_BarPath
   74 LOAD_GLOBAL          5     interface
   77 LOAD_ATTR            7     UIPath
   80 CALL_FUNCTION        2     
   83 JUMP_IF_FALSE        70    
   86 POP_TOP              None  
   87 LOAD_GLOBAL          8     bitmapframe
   90 LOAD_ATTR            9     CBitmapHFrame
   93 LOAD_FAST            0     
   96 LOAD_FAST            1     
   99 LOAD_FAST            0     
  102 LOAD_ATTR            4     m_BarPath
  105 LOAD_GLOBAL          5     interface
  108 LOAD_ATTR            7     UIPath
  111 CALL_FUNCTION        4     
  114 LOAD_FAST            0     
  117 STORE_ATTR           10    m_BarObj
  120 LOAD_FAST            0     
  123 LOAD_ATTR            2     m_Offset
  126 LOAD_CONST           2     0
  129 BINARY_SUBSCR        None  
  130 LOAD_FAST            0     
  133 LOAD_ATTR            1     m_Space
  136 BINARY_ADD           None  
  137 LOAD_FAST            0     
  140 LOAD_ATTR            2     m_Offset
  143 LOAD_CONST           3     1
  146 BINARY_SUBSCR        None  
  147 BUILD_TUPLE          2     
  150 STORE_FAST           2     
  153 JUMP_ABSOLUTE        218   
  156 POP_TOP              None  
  157 LOAD_GLOBAL          11    CImageHFrame
  160 LOAD_FAST            0     
  163 LOAD_FAST            0     
  166 LOAD_ATTR            4     m_BarPath
  169 LOAD_GLOBAL          5     interface
  172 LOAD_ATTR            7     UIPath
  175 LOAD_FAST            1     
  178 CALL_FUNCTION        4     
  181 LOAD_FAST            0     
  184 STORE_ATTR           10    m_BarObj
  187 JUMP_FORWARD         28    
  190 POP_TOP              None  
  191 LOAD_GLOBAL          12    framewidget
  194 LOAD_ATTR            13    CHProgressFrame
  197 LOAD_FAST            0     
  200 LOAD_FAST            1     
  203 LOAD_FAST            0     
  206 LOAD_ATTR            4     m_BarPath
  209 CALL_FUNCTION        3     
  212 LOAD_FAST            0     
  215 STORE_ATTR           10    m_BarObj
  218 LOAD_FAST            0     
  221 LOAD_ATTR            14    m_BgObj
  224 LOAD_CONST           0     None
  227 COMPARE_OP           8     
  230 JUMP_IF_FALSE        34    
  233 POP_TOP              None  
  234 LOAD_FAST            0     
  237 LOAD_ATTR            10    m_BarObj
  240 LOAD_ATTR            16    GetSize
  243 CALL_FUNCTION        0     
  246 UNPACK_SEQUENCE      2     
  249 STORE_FAST           3     
  252 STORE_FAST           4     
  255 LOAD_FAST            4     
  258 LOAD_FAST            0     
  261 STORE_ATTR           17    m_Height
  264 JUMP_FORWARD         1     
  267 POP_TOP              None  
  268 LOAD_FAST            0     
  271 LOAD_ATTR            10    m_BarObj
  274 LOAD_ATTR            18    SetPos
  277 LOAD_FAST            2     
  280 140                  0     
  283 POP_TOP              None  
  284 LOAD_FAST            0     
  287 LOAD_ATTR            10    m_BarObj
  290 LOAD_ATTR            19    SetZ
  293 LOAD_CONST           3     1
  296 CALL_FUNCTION        1     
  299 POP_TOP              None  
  300 LOAD_CONST           0     None
  303 RETURN_VALUE         None  

```

## entry 3495: <module>/CUIEditorMgr/InitUILstInfo

```text
<module>/CUIEditorMgr/InitUILstInfo
NAMES ['m_dUILstInfo', 'interface', 'combdialog', 'gamefont', 'C_sys', 'LoadFile', 'UIPath', 'GetSection', 'split', 'len', 'int', 'EDGE', 'True', 'False', 'GRAD', 'MONO', 'append']
CONSTS None, 'dFontList', -1, 'ui.lst', 'Font', 4, 0, 'sName', 1, 'iSize', 2, 'iWeight', 3, 'bEdge', 'bGrad', 'bMono', 8, 5, 6, 'iEdgeRadius', 7, 'iOffsetY'
    0 BUILD_MAP            0     
    3 LOAD_FAST            0     
    6 STORE_ATTR           0     m_dUILstInfo
    9 BUILD_LIST           0     
   12 DUP_TOP              None  
   13 LOAD_FAST            0     
   16 LOAD_ATTR            0     m_dUILstInfo
   19 LOAD_CONST           1     'dFontList'
   22 STORE_SUBSCR         None  
   23 STORE_FAST           1     
   26 LOAD_CONST           2     -1
   29 LOAD_CONST           0     None
   32 IMPORT_NAME          1     interface
   35 STORE_FAST           2     
   38 LOAD_CONST           2     -1
   41 LOAD_CONST           0     None
   44 IMPORT_NAME          2     combdialog
   47 STORE_FAST           3     
   50 LOAD_CONST           2     -1
   53 LOAD_CONST           0     None
   56 IMPORT_NAME          3     gamefont
   59 STORE_FAST           4     
   62 LOAD_GLOBAL          4     C_sys
   65 LOAD_ATTR            5     LoadFile
   68 LOAD_CONST           3     'ui.lst'
   71 LOAD_FAST            2     
   74 LOAD_ATTR            6     UIPath
   77 CALL_FUNCTION        2     
   80 STORE_FAST           5     
   83 LOAD_FAST            3     
   86 LOAD_ATTR            7     GetSection
   89 LOAD_FAST            5     
   92 LOAD_CONST           4     'Font'
   95 CALL_FUNCTION        2     
   98 STORE_FAST           6     
  101 SETUP_LOOP           496   
  104 LOAD_FAST            6     
  107 68                   None  
  108 FOR_ITER             488   
  111 STORE_FAST           7     
  114 LOAD_FAST            7     
  117 LOAD_ATTR            8     split
  120 CALL_FUNCTION        0     
  123 STORE_FAST           8     
  126 BUILD_MAP            0     
  129 STORE_FAST           9     
  132 LOAD_GLOBAL          9     len
  135 LOAD_FAST            8     
  138 CALL_FUNCTION        1     
  141 LOAD_CONST           5     4
  144 COMPARE_OP           2     
  147 JUMP_IF_FALSE        181   
  150 POP_TOP              None  
  151 LOAD_FAST            8     
  154 LOAD_CONST           6     0
  157 BINARY_SUBSCR        None  
  158 LOAD_FAST            9     
  161 LOAD_CONST           7     'sName'
  164 STORE_SUBSCR         None  
  165 LOAD_GLOBAL          10    int
  168 LOAD_FAST            8     
  171 LOAD_CONST           8     1
  174 BINARY_SUBSCR        None  
  175 CALL_FUNCTION        1     
  178 LOAD_FAST            9     
  181 LOAD_CONST           9     'iSize'
  184 STORE_SUBSCR         None  
  185 LOAD_GLOBAL          10    int
  188 LOAD_FAST            8     
  191 LOAD_CONST           10    2
  194 BINARY_SUBSCR        None  
  195 CALL_FUNCTION        1     
  198 LOAD_FAST            9     
  201 LOAD_CONST           11    'iWeight'
  204 STORE_SUBSCR         None  
  205 LOAD_GLOBAL          10    int
  208 LOAD_FAST            8     
  211 LOAD_CONST           12    3
  214 BINARY_SUBSCR        None  
  215 CALL_FUNCTION        1     
  218 LOAD_FAST            4     
  221 LOAD_ATTR            11    EDGE
  224 64                   None  
  225 JUMP_IF_FALSE        7     
  228 POP_TOP              None  
  229 LOAD_GLOBAL          12    True
  232 JUMP_FORWARD         4     
  235 POP_TOP              None  
  236 LOAD_GLOBAL          13    False
  239 LOAD_FAST            9     
  242 LOAD_CONST           13    'bEdge'
  245 STORE_SUBSCR         None  
  246 LOAD_GLOBAL          10    int
  249 LOAD_FAST            8     
  252 LOAD_CONST           12    3
  255 BINARY_SUBSCR        None  
  256 CALL_FUNCTION        1     
  259 LOAD_FAST            4     
  262 LOAD_ATTR            14    GRAD
  265 64                   None  
  266 JUMP_IF_FALSE        7     
  269 POP_TOP              None  
  270 LOAD_GLOBAL          12    True
  273 JUMP_FORWARD         4     
  276 POP_TOP              None  
  277 LOAD_GLOBAL          13    False
  280 LOAD_FAST            9     
  283 LOAD_CONST           14    'bGrad'
  286 STORE_SUBSCR         None  
  287 LOAD_GLOBAL          10    int
  290 LOAD_FAST            8     
  293 LOAD_CONST           12    3
  296 BINARY_SUBSCR        None  
  297 CALL_FUNCTION        1     
  300 LOAD_FAST            4     
  303 LOAD_ATTR            15    MONO
  306 64                   None  
  307 JUMP_IF_FALSE        7     
  310 POP_TOP              None  
  311 LOAD_GLOBAL          12    True
  314 JUMP_FORWARD         4     
  317 POP_TOP              None  
  318 LOAD_GLOBAL          13    False
  321 LOAD_FAST            9     
  324 LOAD_CONST           15    'bMono'
  327 STORE_SUBSCR         None  
  328 JUMP_FORWARD         241   
  331 POP_TOP              None  
  332 LOAD_GLOBAL          9     len
  335 LOAD_FAST            8     
  338 CALL_FUNCTION        1     
  341 LOAD_CONST           16    8
  344 COMPARE_OP           2     
  347 JUMP_IF_FALSE        221   
  350 POP_TOP              None  
  351 LOAD_FAST            8     
  354 LOAD_CONST           6     0
  357 BINARY_SUBSCR        None  
  358 LOAD_FAST            9     
  361 LOAD_CONST           7     'sName'
  364 STORE_SUBSCR         None  
  365 LOAD_GLOBAL          10    int
  368 LOAD_FAST            8     
  371 LOAD_CONST           10    2
  374 BINARY_SUBSCR        None  
  375 CALL_FUNCTION        1     
  378 LOAD_FAST            9     
  381 LOAD_CONST           9     'iSize'
  384 STORE_SUBSCR         None  
  385 LOAD_GLOBAL          10    int
  388 LOAD_FAST            8     
  391 LOAD_CONST           5     4
  394 BINARY_SUBSCR        None  
  395 CALL_FUNCTION        1     
  398 LOAD_FAST            9     
  401 LOAD_CONST           11    'iWeight'
  404 STORE_SUBSCR         None  
  405 LOAD_GLOBAL          10    int
  408 LOAD_FAST            8     
  411 LOAD_CONST           17    5
  414 BINARY_SUBSCR        None  
  415 CALL_FUNCTION        1     
  418 LOAD_FAST            4     
  421 LOAD_ATTR            11    EDGE
  424 64                   None  
  425 JUMP_IF_FALSE        7     
  428 POP_TOP              None  
  429 LOAD_GLOBAL          12    True
  432 JUMP_FORWARD         4     
  435 POP_TOP              None  
  436 LOAD_GLOBAL          13    False
  439 LOAD_FAST            9     
  442 LOAD_CONST           13    'bEdge'
  445 STORE_SUBSCR         None  
  446 LOAD_GLOBAL          10    int
  449 LOAD_FAST            8     
  452 LOAD_CONST           17    5
  455 BINARY_SUBSCR        None  
  456 CALL_FUNCTION        1     
  459 LOAD_FAST            4     
  462 LOAD_ATTR            14    GRAD
  465 64                   None  
  466 JUMP_IF_FALSE        7     
  469 POP_TOP              None  
  470 LOAD_GLOBAL          12    True
  473 JUMP_FORWARD         4     
  476 POP_TOP              None  
  477 LOAD_GLOBAL          13    False
  480 LOAD_FAST            9     
  483 LOAD_CONST           14    'bGrad'
  486 STORE_SUBSCR         None  
  487 LOAD_GLOBAL          10    int
  490 LOAD_FAST            8     
  493 LOAD_CONST           17    5
  496 BINARY_SUBSCR        None  
  497 CALL_FUNCTION        1     
  500 LOAD_FAST            4     
  503 LOAD_ATTR            15    MONO
  506 64                   None  
  507 JUMP_IF_FALSE        7     
  510 POP_TOP              None  
  511 LOAD_GLOBAL          12    True
  514 JUMP_FORWARD         4     
  517 POP_TOP              None  
  518 LOAD_GLOBAL          13    False
  521 LOAD_FAST            9     
  524 LOAD_CONST           15    'bMono'
  527 STORE_SUBSCR         None  
  528 LOAD_GLOBAL          10    int
  531 LOAD_FAST            8     
  534 LOAD_CONST           18    6
  537 BINARY_SUBSCR        None  
  538 CALL_FUNCTION        1     
  541 LOAD_FAST            9     
  544 LOAD_CONST           19    'iEdgeRadius'
  547 STORE_SUBSCR         None  
  548 LOAD_GLOBAL          10    int
  551 LOAD_FAST            8     
  554 LOAD_CONST           20    7
  557 BINARY_SUBSCR        None  
  558 CALL_FUNCTION        1     
  561 LOAD_FAST            9     
  564 LOAD_CONST           21    'iOffsetY'
  567 STORE_SUBSCR         None  
  568 JUMP_FORWARD         1     
  571 POP_TOP              None  
  572 LOAD_FAST            9     
  575 JUMP_IF_FALSE        17    
  578 POP_TOP              None  
  579 LOAD_FAST            1     
  582 LOAD_ATTR            16    append
  585 LOAD_FAST            9     
  588 CALL_FUNCTION        1     
  591 POP_TOP              None  
  592 JUMP_ABSOLUTE        108   
  595 POP_TOP              None  
  596 JUMP_ABSOLUTE        108   
  599 87                   None  
  600 LOAD_CONST           0     None
  603 RETURN_VALUE         None  

```
