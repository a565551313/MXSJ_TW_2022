"""控件属性名的中文释义（零 Qt，可无头测试）。

两个来源：

* **原生中文名**（繁体）：台服客户端内置控件配置表里每个属性键自带
  Big5 名称，证据见 ``docs/analysis/evidence/widgetconfig_20261017/
  native_tables.json``（39 个键）。这里原样收录，不改字。
* **简体释义**：对 47,139 个真实控件普查模板（``defaults_data.py``）
  的全部键补写一句话说明；含义依据普查取值分布、绘制代码
  （``core/painters.py``）与上述原生表交叉核对，**不编造**——
  没有依据的键返回 ``None``，界面就不显示 tooltip。

tooltip 文案由 :func:`tooltip` 组装：简体释义为主，原生繁体名与
简体不一致时括号附注。本模块只给解释，不改任何读写/绘制语义。
"""

from __future__ import annotations

__all__ = ["describe", "native_name", "tooltip"]

# 原生配置表自带的 Big5 中文名（证据：native_tables.json，2026-10-17）。
_NATIVE_TRAD: dict[str, str] = {
    "bAutoNextLine": "自動換行",
    "bClick": "能否點擊",
    "bShowBg": "是否顯示背景",
    "bShowBgLine": "是否顯示背景線",
    "iAlign": "對齊",
    "iCol": "列",
    "iDirection": "方向",
    "iFont": "字體",
    "iHSpace": "水平間距",
    "iHeight": "高",
    "iMsgId": "消息id",
    "iOffsetX": "偏移x",
    "iOffsetY": "偏移y",
    "iRatio": "中間比例",
    "iRow": "行",
    "iRowHeight": "行高",
    "iScrollBarPosType": "滾動條位置類型",
    "iSpace": "行間距",
    "iStep": "滾動像素",
    "iStyle": "樣式",
    "iTeam": "同組id",
    "iTipsDirect": "提示方向",
    "iType": "樣式",
    "iVSpace": "垂直間距",
    "iWidth": "寬",
    "lColor": "顏色",
    "lEnterColor": "進入顏色",
    "lRelationName": "關聯列表",
    "lSubWidth": "列寬",
    "sBarFileName": "bar路徑",
    "sBgFileName": "bg路徑",
    "sFileName": "資源路徑",
    "sName": "控件名",
    "sSoundPath": "音效路徑",
    "sStyle": "風格",
    "sText": "文本",
    "sTips": "提示",
    "sTitle": "標題",
    "sTitles": "表頭",
}

# 简体一句话释义：覆盖普查模板（defaults_data）全部键 + 绘制代码里
# 出现过的 tTextOffset。值语义随控件类型不同的，在括号里点明。
_DESCRIPTIONS: dict[str, str] = {
    "bAutoNextLine": "自动换行（文字超宽时是否折行）",
    "bClick": "能否点击",
    "bLoad": "启动时是否加载资源",
    "bShow": "是否显示",
    "bShowBg": "是否显示背景",
    "bShowBgLine": "是否显示背景线",
    "bShowLine": "是否显示分隔线",
    "iAlign": "对齐（文本对齐方式；数字含义随控件类型不同，"
              "旧文本框 0=右 1=中 2=左，新文本框与按钮 0–8 为九宫）",
    "iCol": "列数",
    "iDirection": "方向（排列/滚动方向）",
    "iFont": "字体序号（索引客户端字体表）",
    "iHSpace": "水平间距",
    "iHeight": "高（为 0 时取图片自身尺寸）",
    "iInputtype": "输入类型（编辑框的输入过滤）",
    "iIsPassword": "是否密码框",
    "iLimit": "字数上限",
    "iMsgId": "消息号（脚本收发消息用的编号）",
    "iOffsetX": "水平偏移",
    "iOffsetY": "垂直偏移",
    "iParentHeight": "父控件高度参照（0 为不跟随父控件）",
    "iRatio": "中间比例（中段拉伸占比）",
    "iRelationNum": "关联数量",
    "iRow": "行数",
    "iRowHeight": "行高",
    "iScrollBarPosType": "滚动条位置类型",
    "iSpace": "行间距",
    "iStep": "滚动像素（每步滚动量）",
    "iStyle": "样式序号（索引 ui.lst 的 TBStyle 等）",
    "iTeam": "同组 id",
    "iTipsDirect": "提示方向",
    "iType": "类型/样式",
    "iVSpace": "垂直间距",
    "iVersion": "版本号（布局字段版本）",
    "iWidth": "宽（为 0 时取图片自身尺寸）",
    "iX": "横坐标（相对父控件）",
    "iY": "纵坐标（相对父控件）",
    "lChildren": "子控件列表（在控件树中管理，不能直接编辑）",
    "lColor": "颜色（文字/前景色组）",
    "lEnterColor": "进入颜色（鼠标悬停时色组）",
    "lRelationName": "关联列表（关联控件名）",
    "lSubWidth": "列宽（表格各列宽度列表）",
    "sBanword": "禁语过滤（敏感词组名）",
    "sBarFileName": "bar 路径（进度条/滚动条资源路径）",
    "sBgFileName": "bg 路径（背景资源路径）",
    "sCls": "控件类（脚本侧类名）",
    "sExtData": "附加数据",
    "sFileName": "资源路径（图片/精灵资源路径）",
    "sName": "控件名（脚本按名取用）",
    "sPath": "路径",
    "sSoundPath": "音效路径",
    "sStyle": "风格（风格名）",
    "sText": "文本",
    "sTips": "提示（悬停提示文本）",
    "sTitle": "标题",
    "sTitles": "表头（表格列标题，换行分隔）",
    "sUesStyle": "使用样式（原生拼写即 Ues）",
    "sWidgetType": "控件类型",
    "tTextOffset": "文本偏移（按钮文字的 (x, y) 偏移）",
}


def describe(key: str) -> str | None:
    """返回属性键的简体一句话释义；没有依据的键返回 ``None``。"""
    return _DESCRIPTIONS.get(key)


def native_name(key: str) -> str | None:
    """返回原生配置表自带的繁体中文名；表里没有的键返回 ``None``。"""
    return _NATIVE_TRAD.get(key)


def tooltip(key: str) -> str | None:
    """组装悬停 tooltip 文案；完全未知的键返回 ``None``（不显示）。"""
    desc = _DESCRIPTIONS.get(key)
    if desc is None:
        return None
    trad = _NATIVE_TRAD.get(key)
    if trad and trad not in desc:
        return f"{desc}（原生名：{trad}）"
    return desc
