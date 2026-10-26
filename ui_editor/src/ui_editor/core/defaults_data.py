"""各控件类型的默认属性模板（新建控件时用）。

数据来源：对已解密的 2,706 个布局、47,139 个真实控件做普查，
每种类型取出现最频繁的字段集，字段值取众数（坐标归零、宽高
取正值中位数、字符串留空）。手工微调请改本文件。
"""

# ruff: noqa: E501  （普查生成的模板数据，一行一类型便于核查）
from __future__ import annotations

DEFAULT_PROPS: dict[str, dict] = {
    'CAutoDlgBase': {'bLoad': True, 'bShow': True, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sCls': '', 'sName': '', 'sPath': '', 'sWidgetType': 'CAutoDlgBase'},
    'CBitmapFrame': {'bLoad': True, 'bShow': True, 'iHeight': 100, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 226, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CBitmapFrame'},
    'CBitmapHFrame': {'bLoad': True, 'bShow': True, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 131, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CBitmapHFrame'},
    'CBitmapVFrame': {'bLoad': True, 'bShow': True, 'iHeight': 290, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CBitmapVFrame'},
    'CBorder': {'bLoad': True, 'bShow': True, 'iHeight': 130, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 252, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CBorder'},
    'CBox': {'bLoad': True, 'bShow': True, 'iCol': 1, 'iHSpace': 0, 'iHeight': 24, 'iParentHeight': 0, 'iRow': 1, 'iVSpace': 0, 'iVersion': 7, 'iWidth': 100, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sWidgetType': 'CBox'},
    'CBoxWithTips': {'bLoad': True, 'bShow': True, 'iHeight': 20, 'iParentHeight': 0, 'iTipsDirect': 1, 'iVersion': 7, 'iWidth': 55, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sTips': '', 'sWidgetType': 'CBoxWithTips'},
    'CButton': {'bLoad': True, 'bShow': True, 'iMsgId': 1, 'iParentHeight': 0, 'iRelationNum': 0, 'iTeam': 0, 'iTipsDirect': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'lRelationName': [], 'sFileName': '', 'sName': '', 'sSoundPath': '', 'sTips': '', 'sWidgetType': 'CButton'},
    'CCombCheckButton': {'bLoad': True, 'bShow': True, 'iCol': 1, 'iDirection': 0, 'iHSpace': 2, 'iHeight': 52, 'iParentHeight': 0, 'iRow': 1, 'iVSpace': 2, 'iVersion': 7, 'iWidth': 173, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CCombCheckButton'},
    'CDataWidget': {'bLoad': True, 'bShow': True, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sExtData': '', 'sName': '', 'sWidgetType': 'CDataWidget'},
    'CEdit': {'bLoad': True, 'bShow': True, 'iFont': 0, 'iHeight': 20, 'iInputtype': 1, 'iIsPassword': 0, 'iLimit': 0, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 160, 'iX': 0, 'iY': 0, 'lChildren': [], 'lColor': [], 'sBanword': '', 'sName': '', 'sText': '', 'sWidgetType': 'CEdit'},
    'CFrame': {'bLoad': True, 'bShow': True, 'iHeight': 196, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 291, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CFrame'},
    'CHFrame': {'bLoad': True, 'bShow': True, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 91, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CHFrame'},
    'CHPageButton': {'bLoad': True, 'bShow': True, 'iMsgId': 2, 'iParentHeight': 0, 'iRelationNum': 0, 'iStyle': 36, 'iTeam': 1, 'iTipsDirect': 0, 'iVersion': 7, 'iWidth': 50, 'iX': 0, 'iY': 0, 'lChildren': [], 'lRelationName': [], 'sFileName': '', 'sName': '', 'sSoundPath': '', 'sText': '', 'sTips': '', 'sWidgetType': 'CHPageButton'},
    'CHPagePngButton': {'bLoad': True, 'bShow': True, 'iMsgId': 2, 'iParentHeight': 0, 'iRelationNum': 0, 'iStyle': 43, 'iTeam': 0, 'iTipsDirect': 0, 'iVersion': 7, 'iWidth': 80, 'iX': 0, 'iY': 0, 'lChildren': [], 'lRelationName': [], 'sFileName': '', 'sName': '', 'sSoundPath': '', 'sText': '', 'sTips': '', 'sWidgetType': 'CHPagePngButton'},
    'CHPngFrame': {'bLoad': True, 'bShow': True, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 100, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CHPngFrame'},
    'CHotBox': {'bLoad': True, 'bShow': True, 'iHeight': 44, 'iMsgId': 1, 'iParentHeight': 0, 'iTipsDirect': 2, 'iVersion': 7, 'iWidth': 57, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sTips': '', 'sWidgetType': 'CHotBox'},
    'CImagesFrame': {'bLoad': True, 'bShow': True, 'iCol': 1, 'iHSpace': 0, 'iParentHeight': 0, 'iRow': 1, 'iVSpace': 0, 'iVersion': 7, 'iWidth': 205, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CImagesFrame'},
    'CList': {'bLoad': True, 'bShow': True, 'iHeight': 220, 'iMsgId': 100, 'iParentHeight': 0, 'iRow': 6, 'iVersion': 7, 'iWidth': 230, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sWidgetType': 'CList'},
    'CMainFrame': {'bLoad': True, 'bShow': True, 'iHeight': 390, 'iParentHeight': 0, 'iRatio': 25, 'iType': 1, 'iVersion': 7, 'iWidth': 460, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sTitle': '', 'sWidgetType': 'CMainFrame'},
    'CPngList': {'bLoad': True, 'bShow': True, 'iHeight': 288, 'iMsgId': 100, 'iParentHeight': 0, 'iRow': 5, 'iVersion': 7, 'iWidth': 187, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sWidgetType': 'CPngList'},
    'CPngNineFrame': {'bLoad': True, 'bShow': True, 'iHeight': 143, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 234, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CPngNineFrame'},
    'CPngTable': {'bLoad': True, 'bShow': True, 'iHeight': 356, 'iMsgId': 100, 'iParentHeight': 0, 'iRow': 11, 'iVersion': 7, 'iWidth': 437, 'iX': 0, 'iY': 0, 'lChildren': [], 'lSubWidth': [], 'sName': '', 'sTitles': '', 'sWidgetType': 'CPngTable'},
    'CProgress': {'bLoad': True, 'bShow': True, 'iOffsetX': 0, 'iOffsetY': 0, 'iParentHeight': 0, 'iSpace': 0, 'iType': 0, 'iVersion': 7, 'iWidth': 187, 'iX': 0, 'iY': 0, 'lChildren': [], 'sBarFileName': '', 'sBgFileName': '', 'sName': '', 'sWidgetType': 'CProgress'},
    'CRichTextFrame': {'bClick': 0, 'bLoad': True, 'bShow': True, 'iAlign': 4, 'iFont': 0, 'iHeight': 20, 'iMsgId': 0, 'iParentHeight': 0, 'iVersion': 7, 'iWidth': 120, 'iX': 0, 'iY': 0, 'lChildren': [], 'lColor': [], 'lEnterColor': [], 'sName': '', 'sText': '', 'sWidgetType': 'CRichTextFrame'},
    'CSpriteFrame': {'bLoad': True, 'bShow': True, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CSpriteFrame'},
    'CTable': {'bLoad': True, 'bShow': True, 'iHeight': 287, 'iMsgId': 100, 'iParentHeight': 0, 'iRow': 10, 'iVersion': 7, 'iWidth': 360, 'iX': 0, 'iY': 0, 'lChildren': [], 'lSubWidth': [], 'sName': '', 'sTitles': '', 'sWidgetType': 'CTable'},
    'CTableView': {'bLoad': True, 'bShow': True, 'bShowBg': 1, 'bShowBgLine': 1, 'bShowLine': 1, 'iCol': 1, 'iHeight': 289, 'iParentHeight': 0, 'iRowHeight': 60, 'iScrollBarPosType': 1, 'iStep': 60, 'iVersion': 7, 'iWidth': 288, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sStyle': '', 'sWidgetType': 'CTableView'},
    'CTextButton': {'bLoad': True, 'bShow': True, 'iMsgId': 2, 'iParentHeight': 0, 'iRelationNum': 0, 'iStyle': 0, 'iTeam': 0, 'iTipsDirect': 0, 'iVersion': 7, 'iWidth': 80, 'iX': 0, 'iY': 0, 'lChildren': [], 'lRelationName': [], 'sFileName': '', 'sName': '', 'sSoundPath': '', 'sText': '', 'sTips': '', 'sWidgetType': 'CTextButton'},
    'CTextFrame': {'bLoad': True, 'bShow': True, 'iAlign': 1, 'iFont': 0, 'iParentHeight': 0, 'iSpace': 5, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'lColor': [], 'sName': '', 'sText': '', 'sWidgetType': 'CTextFrame'},
    'CTextFrameEx': {'bAutoNextLine': True, 'bLoad': True, 'bShow': True, 'iAlign': 4, 'iFont': 0, 'iHeight': 20, 'iParentHeight': 0, 'iVSpace': 0, 'iVersion': 7, 'iWidth': 84, 'iX': 0, 'iY': 0, 'lChildren': [], 'lColor': [], 'sName': '', 'sText': '', 'sWidgetType': 'CTextFrameEx'},
    'CTitleTableView': {'bLoad': True, 'bShow': True, 'bShowBg': 1, 'bShowBgLine': 1, 'bShowLine': 1, 'iCol': 3, 'iHeight': 312, 'iParentHeight': 0, 'iRowHeight': 30, 'iScrollBarPosType': 1, 'iStep': 60, 'iVersion': 7, 'iWidth': 450, 'iX': 0, 'iY': 0, 'lChildren': [], 'lSubWidth': [], 'sName': '', 'sTitles': '', 'sUesStyle': '', 'sWidgetType': 'CTitleTableView'},
    'CVFrame': {'bLoad': True, 'bShow': True, 'iHeight': 403, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CVFrame'},
    'CVPageButton': {'bLoad': True, 'bShow': True, 'iMsgId': 11, 'iParentHeight': 0, 'iRelationNum': 0, 'iStyle': 38, 'iTeam': 1, 'iTipsDirect': 0, 'iVersion': 7, 'iWidth': 60, 'iX': 0, 'iY': 0, 'lChildren': [], 'lRelationName': [], 'sFileName': '', 'sName': '', 'sSoundPath': '', 'sText': '', 'sTips': '', 'sWidgetType': 'CVPageButton'},
    'CVPagePngButton': {'bLoad': True, 'bShow': True, 'iMsgId': 3, 'iParentHeight': 0, 'iRelationNum': 0, 'iStyle': 44, 'iTeam': 1, 'iTipsDirect': 0, 'iVersion': 7, 'iWidth': 0, 'iX': 0, 'iY': 0, 'lChildren': [], 'lRelationName': [], 'sFileName': '', 'sName': '', 'sSoundPath': '', 'sText': '', 'sTips': '', 'sWidgetType': 'CVPagePngButton'},
    'CVPngFrame': {'bLoad': True, 'bShow': True, 'iHeight': 50, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sFileName': '', 'sName': '', 'sWidgetType': 'CVPngFrame'},
    'CVPngScrollBar': {'bLoad': True, 'bShow': True, 'iHeight': 234, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sWidgetType': 'CVPngScrollBar'},
    'CVScrollBar': {'bLoad': True, 'bShow': True, 'iHeight': 354, 'iParentHeight': 0, 'iVersion': 7, 'iX': 0, 'iY': 0, 'lChildren': [], 'sName': '', 'sWidgetType': 'CVScrollBar'},
}


#: 游戏自带 UI 编辑器（data/script.fls entry 3853
#: script/uieditor/widgetconfig.py 的 DEFAULT_VALUE）有默认模板的类型，
#: 共 31 种。2026-10-17 静态对照：这 31 种的字段集与 DEFAULT_PROPS
#: 逐项相同（docs/analysis/native_widgetconfig_comparison_20261017.md、
#: evidence/widgetconfig_20261017/default_comparison.json 的
#: all_shared_field_sets_equal=true）。对这些类型，「游戏会读的键」＝
#: 模板字段集；另外 7 种外部模板（CAutoDlgBase、CBitmap*Frame、
#: CDataWidget、CEdit、CTitleTableView）没有原生模板，不下断言。
NATIVE_TYPES: frozenset = frozenset({
    "CBorder", "CBox", "CBoxWithTips", "CButton", "CCombCheckButton",
    "CFrame", "CHFrame", "CHPageButton", "CHPagePngButton", "CHPngFrame",
    "CHotBox", "CImagesFrame", "CList", "CMainFrame", "CPngList",
    "CPngNineFrame", "CPngTable", "CProgress", "CRichTextFrame",
    "CSpriteFrame", "CTable", "CTableView", "CTextButton", "CTextFrame",
    "CTextFrameEx", "CVFrame", "CVPageButton", "CVPagePngButton",
    "CVPngFrame", "CVPngScrollBar", "CVScrollBar",
})


def native_field_set(wtype: str) -> frozenset | None:
    """类型的原生模板字段集；无原生模板的类型返回 None（没证据不下结论）。"""
    if wtype not in NATIVE_TYPES:
        return None
    return frozenset(DEFAULT_PROPS.get(wtype, ()))


def _size_ignored() -> dict:
    out = {}
    for t in NATIVE_TYPES:
        fields = DEFAULT_PROPS.get(t, {})
        dims = tuple(name for name, key in (("width", "iWidth"),
                                            ("height", "iHeight"))
                     if key not in fields)
        if dims:
            out[t] = dims
    return out


#: 原生类型里「游戏不读的维度」：CButton/CSpriteFrame/CTextFrame 宽高
#: 都不读，横排类（CHFrame 等 9 种）只读 iWidth、高由图定，竖排类
#: （CVFrame 等 4 种）只读 iHeight、宽由图定。真包 5309 个带图 CButton
#: 无一写宽高（docs/analysis/evidence/fidelity_autosize_20261022.json）。
#: 编辑这些维度只影响画布显示，游戏内尺寸由图片素材自身决定。
SIZE_IGNORED_NATIVE: dict = _size_ignored()
