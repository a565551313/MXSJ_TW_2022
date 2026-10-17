#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夢想世界》(MXSJ TW 2022, v2.27.2) Full-Flow Local Mock Server
==============================================================
Simulates the complete normal player lifecycle:
  1. 選區 (Server Selection):
     - Listens on TCP 0.0.0.0:3134 (matching `server.ini` "縮小燈(推薦站)").
     - Immediately sends `GS2C_HELLO = 1` upon TCP connection (server-first handshake).
     - Verifies the client's 25-byte `NakedSend` seed reply (`S2CHello` in `netlogin.py`).
  2. 賬號密碼登錄 (Account & Password Login):
     - Handles `C2GS_GAME_PUBLIC = 250` (sub `113` device fingerprint).
     - Handles `C2GS_LOGIN_ACCOUNT_ENTER = 1` (account, MD5 password, MAC, SimpleEncrypt HWID).
     - Sends `GS2C_LOGIN_ACCOUNT_INFO = 15` + `GS2C_LOGIN_PLAYER_INFO = 3` (role list).
  3. 創建或選擇角色 (Character Creation or Character Selection):
     - Handles `C2GS_LOGIN_PLAYER_ADD = 3` (create role) -> replies with
       `GS2C_LOGIN_PLAYER_INFO = 3` + `GS2C_LOGIN_PLAYER_ADD = 6`.
     - Handles `C2GS_LOGIN_PLAYER_DEL = 7` (delete role) -> replies with
       `GS2C_LOGIN_PLAYER_DEL = 10`.
     - Handles `C2GS_LOGIN_PLAYER_ENTER = 2` (select role & enter game).
  4. 進入地圖與世界交互 (Entering the Map & In-Map Interactions):
     - Sends `GS2C_PROP_INIT = 16` (all 97 `ITEM_SERVERINIT` hero attributes from `hero.py`).
     - Sends `GS2C_MAP_SCENE_M = 96` (loads map scene `1025` 清風村 / `1054` 明月城 / `1001` 永澤城).
     - Sends `GS2C_MAP_GOTO_M = 97` (places hero at spawn grid coordinates).
     - Sends `GS2C_MAP_ADD_NPC = 99` (spawns interactive teleporter NPC on the map).
     - Sends `GS2C_NOTIFY = 165` (welcome banner in system prompt & chat window).
     - Handles `C2GS_MAP_MOVE = 54` (walking), `C2GS_HEART_BEAT = 109` -> `GS2C_HEART_BEAT = 69`,
       `C2GS_REQUEST_TIME = 15` -> `GS2C_TIME = 12`, `C2GS_NPC_LOOK = 55` -> `GS2C_NPC_CHAT_EXT = 152`,
       `C2GS_NPC_ANSWER = 98` (map teleportation), and `C2GS_PLAYER_CHAT = 149` (chat & `/tp` commands).
  5. GM / 開發模式 (Developer Mode):
     - `ensure_client_ready()` writes `nocheck` as `[game] gm=1` (not an empty file).
       `permission.InitSpecialVersion()` only needs the file to exist, but
       `permission.IsOpenGm()` reads the `[game]` section of THIS file, so an empty
       `nocheck` leaves `$`-commands in the chat box silently dropped.

OPCODE NOTE (audited 2026-10-16 against the client's own tables)
---------------------------------------------------------------
Every opcode below was re-checked against `data/script.fls` `idx=3970`
(`script/protocol.py`) and the client's dispatch table in `idx=3176` (`script/net.py`),
which registers handlers as `table[GS2C_XXX] = {...}` in source order (a later
registration with the same number shadows an earlier one).  Three values in the
upstream copy contradicted those tables and are corrected here; each site carries
an inline comment saying what the client actually does.  The legacy `_LEGACY`
aliases are kept so the mock still answers older `data.fls` builds.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import socket
import struct
import sys
import threading
import time
import zlib
from pathlib import Path
from typing import Any

# ============================================================================
# 1. Protocol Constants (`data/script.fls` `idx=3970` `script/protocol.py`)
# ============================================================================

# Client -> GameServer (C2GS) - Authentic `data/script.fls` v2.27.2 opcodes
C2GS_LOGIN_ACCOUNT_ENTER = 1
C2GS_LOGIN_PLAYER_ENTER = 2
C2GS_LOGIN_PLAYER_ADD = 3
C2GS_LOGIN_QUIT = 4
C2GS_LOGIN_PLAYER_DEL = 7
C2GS_PING = 8
C2GS_QUICKLOGIN = 13
C2GS_PLAYER_ADJUSTPOINT = 16
# Client sends `C2GS_PLAYER_UPGRADE = 152` (`script/nethero.py::C2SUpgrade`); the same
# number is also `C2GS_CHECKWG` in the client's table (its own ambiguity), so accept both.
C2GS_PLAYER_UPGRADE = 152
C2GS_PLAYER_UPGRADE_LEGACY = 17
C2GS_PROP_NEWPOINT = 17
C2GS_PLAYER_SWITCH = 18
C2GS_PLAYER_SYSSWITCH = 21
C2GS_TIME = 31
C2GS_ITEM_OP = 32
C2GS_ITEM_LOCK = 38
C2GS_SELECT_SERVER = 41
C2GS_TASK_GET = 48
C2GS_TASK = 49
C2GS_MAP_MOVE = 54
C2GS_SYN_DIREMOTE = 55
C2GS_REQUEST_TIME = 61
C2GS_ANSWERHELLO = 62
C2GS_HEART_BEAT = 63
C2GS_TITLE = 67
C2GS_SCHEDULE_LEGACY = 69
C2GS_SCHEDULE = 82
C2GS_OPEN_UI_LEGACY = 60
C2GS_OPEN_UI = 88
C2GS_ITEMSHOP = 89
C2GS_HUODONG = 90
C2GS_NPC_LOOK = 96
C2GS_NPC_COMMAND = 97
C2GS_NPC_ANSWER = 98
C2GS_NPC_RBCLICK = 108
C2GS_NPC_INPUT = 115
C2GS_SUMMON_RELEASE = 128
C2GS_SUMMON_PROPVIEW = 129
C2GS_SUMMON_RENAME = 130
C2GS_SUMMON_FIGHT = 131
C2GS_SUMMON_SHOW = 132
C2GS_SUMMON_HIDE = 133
C2GS_SUMMON_POINT = 134
C2GS_GET_SUMMON_INFO = 144
C2GS_GET_ITEM_INFO = 145
C2GS_PLAYER_CHAT = 149
C2GS_MIXPACKET = 151
C2GS_CHECKWG = 152
C2GS_PLAYER_CMD = 153
C2GS_GET_ITEM_INFO_EXT = 156
C2GS_ASSISTANT_OP = 192
C2GS_GAME_PUBLIC = 209
C2GS_SUMMON_TALENT = 229
C2GS_OPEN_UI_NEW = 230

# Legacy `data/data.fls` C2GS opcodes (kept for backwards-compatible fallback)
C2GS_REQUEST_TIME_LEGACY = 15
C2GS_NPC_LOOK_LEGACY = 55
C2GS_NPC_ANSWER_LEGACY = 56
C2GS_NPC_INPUT_LEGACY = 59
C2GS_PING_LEGACY = 77
C2GS_SELSERVER_LEGACY = 80
C2GS_HEART_BEAT_LEGACY = 109
C2GS_PLAYER_CHAT_LEGACY = 123
C2GS_SELECT_SERVER_LEGACY = 247
C2GS_GAME_PUBLIC_LEGACY = 250

# GameServer -> Client (GS2C) - Authentic `data/script.fls` v2.27.2 opcodes
GS2C_HELLO = 1
GS2C_LOGIN_PLAYER_INFO = 3
GS2C_LOGIN_PLAYER_ENTER = 4
GS2C_LOGIN_PLAYER_ADD = 6
GS2C_LOGIN_ERROR = 8
GS2C_LOGIN_PLAYER_DEL = 10
GS2C_OTHER_ASSISTANT = 11
GS2C_QUICKLOGIN = 12
GS2C_LOGIN_PLAYER_INFO_END = 14
GS2C_LOGIN_ACCOUNT_INFO = 15
GS2C_PROP_INIT = 16
# `script/protocol.py` says `GS2C_PROP_CHANGE = 152`, but `script/net.py` registers
# `GS2C_NPC_CHAT_EXT` (also 152) *later* in source order, so the single-prop-change
# handler is shadowed and unreachable in v2.27.2; opcode 17 has no handler at all.
# => Prop changes are sent as a one-entry `GS2C_PROP_CHANGELIST = 61` instead
#    (`nethero.S2CMultiPropChange` = `[count:1B] + count * S2CPropChange(...)`).
GS2C_PROP_CHANGE = 152  # reference only - unreachable, do NOT send
GS2C_PROP_RESIST = 18
GS2C_PROP_POWER = 19
GS2C_PROP_PHOTO = 20
GS2C_PROP_SWITCH = 21
GS2C_TIME = 31
GS2C_TIME_LEGACY = 12
GS2C_ITEM_KEY = 32
GS2C_ITEM_ADD = 33
GS2C_ITEM_DEL = 34
GS2C_ITEM_AMOUNT = 35
GS2C_ITEM_POS = 36
GS2C_ITEM_LOCK = 39
GS2C_ITEM_ATTRDESC = 42
GS2C_SELSERVER = 47
GS2C_SELSERVER_LEGACY = 45
GS2C_SUMM_INFO = 48
GS2C_SUMM_SKILL = 49
GS2C_SUMM_SET_FIGHT = 50
GS2C_SUMM_PROP_VIEW = 51
GS2C_SUMM_PROP_STATE = 52
GS2C_SUMMON_KEY = 53
GS2C_SUMM_EQUIP = 54
GS2C_SCHEDULE = 57
GS2C_PROP_CHANGELIST = 61
GS2C_HEART_BEAT = 63
GS2C_HEART_BEAT_LEGACY = 69
GS2C_SKILL_LEVEL = 65
GS2C_OPEN_UI = 89
GS2C_MAP_SCENE_M = 96
GS2C_MAP_GOTO_M = 97
GS2C_MAP_ADD_PLAYER = 98
GS2C_MAP_ADD_NPC = 99
# Client: `GS2C_MAP_DEL = 85` (idx=3970); 100 is `GS2C_MAP_ADD_GOODS` in the same table,
# so sending 100 here would be parsed by `netmap.S2CMapAddGoods` instead.
GS2C_MAP_DEL = 85
GS2C_MAP_EFFECT = 102
GS2C_MAP_SUMMON = 105
# Client's name/value is `GS2C_CHANGE_SHAPE = 106` -> `netmap.S2CChangeShape`;
# 107 is `GS2C_MAP_STORE` (`netmap.S2CMapStore`) in the same table.
GS2C_CHANGE_SHAPE = 106
GS2C_NPC_CHAT = 144
GS2C_NPC_CHAT_EXT = 152
GS2C_SUMMON_INFO = 161
GS2C_ITEM_INFO = 162
GS2C_NOTIFY_EXT = 164
GS2C_NOTIFY = 165
GS2C_HUODONG_OP = 166
GS2C_PLAYER_CHAT = 167
GS2C_MESSAGE = 169
GS2C_ITEM_INFO_EX = 190
GS2C_TIME_SECOND = 192
GS2C_TITLE = 200
GS2C_ITEM_OTHER = 205
GS2C_GAME_PUBLIC = 209
GS2C_ADD_MULTIITEM = 210
GS2C_SUMM_ADD = 220
GS2C_SUMM_REMOVE = 221
GS2C_SUMMON_TALENT = 233
GS2C_OPEN_UI_NEW = 234

# Playable character shapes from `script/login/createrole.py`, `script/hero.py` (`idx=3038`),
# and `script/oldwalkerprocess.py` (`idx=2086`):
#   Male (sex=1):   111 (愛德華), 112 (隆), 121 (浪人), 122 (星虎), 131 (凌風), 132 (霹靂火)
#   Female (sex=2): 211 (莉莉絲), 212 (雪蓮), 221 (玉馨), 222 (燕歌行), 231 (明月姬), 232 (晚秋)
# Note: If `m_RealShape` is not in `hero.VALID_SHAPE_LIST`, `avatar.GetDefaultPhoto()` returns `[]`,
# which causes `CStateDialog.__init__` (`dlgstate.py` line 606) to crash with `IndexError` and
# leaves the Character Attributes window (`人物屬性`) blank!
VALID_PLAYER_SHAPES: tuple[int, ...] = (
    111, 112, 113, 121, 122, 131, 132,
    211, 212, 221, 222, 231, 232, 233,
)
LEGACY_SHAPE_MAP: dict[int, int] = {
    1: 111, 2: 112, 3: 121, 4: 122, 5: 131, 6: 132,
    7: 211, 8: 212, 9: 221, 10: 222, 11: 231, 12: 232,
}
SHAPE_DEFAULT_ICON: dict[int, int] = {
    111: 1, 112: 2, 113: 1, 121: 3, 122: 4, 131: 5, 132: 6,
    211: 14, 212: 15, 221: 16, 222: 17, 231: 18, 232: 19, 233: 18,
}
SHAPE_NAMES: dict[int, str] = {
    111: "愛德華(男)", 112: "隆(男)", 121: "浪人(男)", 122: "星虎(男)", 131: "凌風(男)", 132: "霹靂火(男)",
    211: "莉莉絲(女)", 212: "雪蓮(女)", 221: "玉馨(女)", 222: "燕歌行(女)", 231: "明月姬(女)", 232: "晚秋(女)",
}


def normalize_player_shape(shape: int) -> int:
    if shape in VALID_PLAYER_SHAPES:
        return shape
    return LEGACY_SHAPE_MAP.get(shape, 111)


def get_sex_for_shape(shape: int) -> int:
    return 2 if normalize_player_shape(shape) >= 200 else 1


def normalize_liupai(liupai: int, major: int = 1) -> int:
    if 1001 <= liupai <= 1014:
        return liupai
    if 1 <= liupai <= 14:
        return 1000 + liupai
    # Default liupai by major: 1(戰士)->1001(劍), 2(法師)->1007(道家), 3(術士)->1010(佛家)
    return {1: 1001, 2: 1007, 3: 1010, 4: 1012, 5: 1013, 6: 1014}.get(major, 1001)

# Movement step offsets from `script/nethero.py` (`idx=826`, `C2SMapMove`):
# Directions 1..8 map to `_offset[d - 1]`
MOVE_STEP_OFFSETS: tuple[tuple[int, int], ...] = (
    (1, -1),
    (-1, -1),
    (-1, 1),
    (1, 1),
    (0, -1),
    (-1, 0),
    (0, 1),
    (1, 0),
)

# Authentic map definitions & NPC tables extracted from `data/script.fls`:
#   - `idx=1301` (`script/data/mapdata.py`)
#   - `idx=2804` (`script/data/minimapnpcpos.py`)
#   - `idx=1799` (`script/data/npcname2realnamedata.py`)
#   - `idx=3935` (`script/data/charpartdata.py` `NPC_DATA`: valid human shapes `3001..3040`, creatures `2010..2990`)
# Note: `npc_type` (`iNpcType`) matches `minimapnpcpos.DATA_POS` element `v[2]` so clicking
# any NPC on the Tab Mini-Map (`dlgmap`) walks to that NPC and triggers `C2SNpcLook`!
MAPS: dict[int, dict[str, Any]] = {
    1025: {
        "scene": 1025,
        "mapid": 1025,
        "minimapid": 1025,
        "name": "清風村",
        "spawn_x": 75,
        "spawn_y": 52,
        "npc": {
            "id": 50001,
            "shape": 3007,
            "icon": 3007,
            "npc_type": 4480,
            "x": 71,
            "y": 49,
            "dir": 3,
            "name": "清風村傳送人",
            "title": "驛站傳送",
            "greeting": "少俠好！我是#Y清風村驛站傳送人#n，可免費送您前往各大主城與練級場景！",
        },
        "npcs": [
            {"id": 50001, "shape": 3007, "icon": 3007, "npc_type": 4480, "x": 71, "y": 49, "dir": 3, "name": "清風村傳送人", "title": "驛站傳送", "greeting": "少俠好！我是#Y清風村驛站傳送人#n，可免費送您前往各大主城與練級場景！"},
            {"id": 51001, "shape": 3034, "icon": 3034, "npc_type": 4495, "x": 77, "y": 64, "dir": 3, "name": "新手指導員", "title": "新手指引", "greeting": "歡迎來到《夢想世界》#Y清風村#n！按 #GTab#n 鍵可打開小地圖點擊任意 NPC 自動尋路。"},
            {"id": 51002, "shape": 3016, "icon": 3016, "npc_type": 4152, "x": 107, "y": 80, "dir": 3, "name": "倉庫管理員", "title": "清風村倉庫", "greeting": "少俠行走江湖，貴重物品放在我這兒最安全不過了！"},
            {"id": 51003, "shape": 3007, "icon": 3007, "npc_type": 2001, "x": 175, "y": 142, "dir": 1, "name": "車伕", "title": "驛站車伕", "greeting": "客官要去#Y天水平原#n還是#Y明月城#n？坐我的馬車眨眼就到！"},
            {"id": 51004, "shape": 3021, "icon": 3021, "npc_type": 3021, "x": 35, "y": 123, "dir": 3, "name": "村長", "title": "清風村村長", "greeting": "清風徐來，水波不興。年輕人，外面的世界很精彩，去明月城看看吧！"},
            {"id": 51005, "shape": 3028, "icon": 3028, "npc_type": 4140, "x": 67, "y": 18, "dir": 3, "name": "點卡寄售人", "title": "寄售中心", "greeting": "這裡可以辦理點卡與世貢寄售，童叟無欺！"},
            {"id": 51006, "shape": 3012, "icon": 3012, "npc_type": 1101, "x": 45, "y": 71, "dir": 3, "name": "技能教師", "title": "流派武學", "greeting": "刀槍劍戟、法術巫術，唯有勤學苦練方能領悟精妙招式！"},
            {"id": 51007, "shape": 3015, "icon": 3015, "npc_type": 4345, "x": 116, "y": 121, "dir": 3, "name": "魯大嬸", "title": "清風村民", "greeting": "我家小貝一大早就跑出去玩了，少俠若見到她請幫我叫她回家吃飯。"},
            {"id": 51008, "shape": 3019, "icon": 3019, "npc_type": 4346, "x": 76, "y": 102, "dir": 3, "name": "魯小貝", "title": "清風村民", "greeting": "嘻嘻，清風村的蝴蝶真好看，你也來陪我玩嗎？"},
            {"id": 51009, "shape": 3024, "icon": 3024, "npc_type": 4187, "x": 130, "y": 121, "dir": 3, "name": "食品店老闆", "title": "食品店", "greeting": "剛出爐的香噴噴包子與佳餚，出門歷練必備！"},
            {"id": 51010, "shape": 3017, "icon": 3017, "npc_type": 4347, "x": 56, "y": 119, "dir": 3, "name": "王捕頭", "title": "清風治安", "greeting": "近來長風島偶有海盜出沒，少俠若實力精進，不妨前去歷練一番！"},
            {"id": 51011, "shape": 2010, "icon": 2010, "npc_type": 2010, "x": 25, "y": 105, "dir": 3, "name": "幸運小兔", "title": "吉祥萌寵", "greeting": "咕啾咕啾～摸摸幸運小兔，今天一定會有好運氣喔！"},
            {"id": 51012, "shape": 3020, "icon": 3020, "npc_type": 1027, "x": 154, "y": 71, "dir": 3, "name": "藥店老闆", "title": "藥店", "greeting": "金創藥、還魂丹應有盡有，少俠需要補充氣血法力嗎？"},
            {"id": 51013, "shape": 3014, "icon": 3014, "npc_type": 1028, "x": 150, "y": 39, "dir": 3, "name": "雜貨店老闆", "title": "雜貨店", "greeting": "飛行旗、火把、藏寶鏟，走南闖北的雜貨全在這兒！"},
            {"id": 51014, "shape": 3022, "icon": 3022, "npc_type": 1081, "x": 124, "y": 30, "dir": 3, "name": "裝備店老闆", "title": "裝備店", "greeting": "好馬配好鞍，少俠挑一件趁手的兵器與防具吧！"},
        ],
        "portals": [
            {"x": 183, "y": 11, "radius": 4, "target_map": 1028, "target_x": 10, "target_y": 105, "desc": "長風島"},
            {"x": 175, "y": 142, "radius": 3, "target_map": 1005, "target_x": 20, "target_y": 25, "desc": "天水平原"},
        ],
    },
    1054: {
        "scene": 1054,
        "mapid": 1054,
        "minimapid": 1054,
        "name": "明月城",
        "spawn_x": 222,
        "spawn_y": 135,
        "npc": {
            "id": 50002,
            "shape": 3007,
            "icon": 3007,
            "npc_type": 4403,
            "x": 218,
            "y": 132,
            "dir": 3,
            "name": "明月城傳送師",
            "title": "明月驛站",
            "greeting": "明月照九州，天下英雄匯聚於此！請問少俠想去哪裡？",
        },
        "npcs": [
            {"id": 50002, "shape": 3007, "icon": 3007, "npc_type": 4403, "x": 218, "y": 132, "dir": 3, "name": "明月城傳送師", "title": "明月驛站", "greeting": "明月照九州，天下英雄匯聚於此！請問少俠想去哪裡？"},
            {"id": 52001, "shape": 3001, "icon": 3001, "npc_type": 1001, "x": 238, "y": 145, "dir": 3, "name": "古木牙", "title": "活動使者", "greeting": "天下英雄齊聚明月城！老夫古木牙特為少俠準備了豐厚福利！"},
            {"id": 52002, "shape": 3017, "icon": 3017, "npc_type": 3017, "x": 241, "y": 171, "dir": 3, "name": "除魔師", "title": "除魔任務", "greeting": "四方妖魔蠢蠢欲動，少俠可願領取除魔令為民除害？"},
            {"id": 52003, "shape": 3036, "icon": 3036, "npc_type": 4925, "x": 223, "y": 180, "dir": 3, "name": "明威", "title": "天選使者", "greeting": "天選之戰，巔峰對決！唯有真正的強者方能名列天選金榜！"},
            {"id": 52004, "shape": 3033, "icon": 3033, "npc_type": 4991, "x": 200, "y": 164, "dir": 3, "name": "穿行者", "title": "副本接引", "greeting": "時空裂隙已開，少俠可願隨我穿越異界挑戰秘境副本？"},
            {"id": 52005, "shape": 2020, "icon": 2020, "npc_type": 4460, "x": 186, "y": 183, "dir": 3, "name": "神獸小飛豬", "title": "神獸仙獸進修", "greeting": "哼哼～別看我胖嘟嘟，天下神獸仙獸都要找我進修呢！"},
            {"id": 52006, "shape": 3011, "icon": 3011, "npc_type": 4102, "x": 190, "y": 108, "dir": 3, "name": "仙流道人", "title": "召喚獸煉妖", "greeting": "天地靈獸，造化萬千。少俠想為愛寵洗煉資質還是打書？"},
            {"id": 52007, "shape": 3008, "icon": 3008, "npc_type": 4333, "x": 208, "y": 103, "dir": 3, "name": "金大有", "title": "支線任務", "greeting": "聽說江湖上最近出了不少奇聞異事，少俠有興趣探聽一番嗎？"},
            {"id": 52008, "shape": 3029, "icon": 3029, "npc_type": 4981, "x": 262, "y": 159, "dir": 3, "name": "幫派學徒指引人", "title": "師徒管理", "greeting": "良師益友伴江湖，拜師學藝或收徒授業皆可找我登記！"},
            {"id": 52009, "shape": 3018, "icon": 3018, "npc_type": 4485, "x": 250, "y": 107, "dir": 3, "name": "項鏢師", "title": "運鏢任務", "greeting": "威遠鏢局信譽第一！少俠若能護送鏢銀平安抵達，必有重謝！"},
            {"id": 52010, "shape": 3016, "icon": 3016, "npc_type": 4152, "x": 135, "y": 129, "dir": 3, "name": "倉庫管理員", "title": "明月城倉庫", "greeting": "明月城皇家庫房，固若金湯，少俠儘管放心存放！"},
            {"id": 52011, "shape": 3009, "icon": 3009, "npc_type": 4171, "x": 129, "y": 86, "dir": 3, "name": "遊方道士", "title": "寶圖任務", "greeting": "貧道夜觀天象，得知江山社稷圖流落強盜之手，少俠可願去奪回藏寶圖？"},
            {"id": 52012, "shape": 3032, "icon": 3032, "npc_type": 4978, "x": 129, "y": 56, "dir": 3, "name": "葉羽尋", "title": "圖鑒任務", "greeting": "收集天下魔物圖鑒，知己知彼百戰不殆！"},
            {"id": 52013, "shape": 3028, "icon": 3028, "npc_type": 4968, "x": 103, "y": 130, "dir": 3, "name": "萬福", "title": "精品交易", "greeting": "奇珍異寶、神兵靈寵，明月城精品交易行應有盡有！"},
            {"id": 52014, "shape": 3031, "icon": 3031, "npc_type": 4801, "x": 131, "y": 160, "dir": 3, "name": "安雪瑤", "title": "選美大會", "greeting": "雲想衣裳花想容，春風拂檻露華濃。本屆選美盛典期待您的參與！"},
            {"id": 52015, "shape": 3025, "icon": 3025, "npc_type": 4440, "x": 105, "y": 215, "dir": 3, "name": "紅娘", "title": "姻緣牽線", "greeting": "願天下有情人終成眷屬，千里姻緣一線牽！"},
            {"id": 52016, "shape": 3026, "icon": 3026, "npc_type": 4831, "x": 67, "y": 202, "dir": 3, "name": "義千豪", "title": "結拜使者", "greeting": "義結金蘭，同生共死！與好友結拜可在此立下盟誓！"},
            {"id": 52017, "shape": 3027, "icon": 3027, "npc_type": 4191, "x": 82, "y": 172, "dir": 3, "name": "造型師", "title": "服飾染色", "greeting": "換一身華麗染色與造型，讓少俠在人群中風采奪目！"},
            {"id": 52018, "shape": 3014, "icon": 3014, "npc_type": 4406, "x": 64, "y": 134, "dir": 3, "name": "交易總管", "title": "寄售交易", "greeting": "公平交易，互通有無！"},
            {"id": 52019, "shape": 3013, "icon": 3013, "npc_type": 4498, "x": 47, "y": 111, "dir": 3, "name": "物品店總管", "title": "物品商會", "greeting": "商會店鋪琳瑯滿目，少俠想採購還是開設店鋪？"},
            {"id": 52020, "shape": 3005, "icon": 3005, "npc_type": 4563, "x": 62, "y": 82, "dir": 3, "name": "工藝師", "title": "巧匠工藝", "greeting": "精雕細琢，巧奪天工！"},
            {"id": 52021, "shape": 3006, "icon": 3006, "npc_type": 4561, "x": 79, "y": 79, "dir": 3, "name": "傢具師", "title": "庭院傢具", "greeting": "溫馨庭院少不了精緻傢具，來看看最新圖紙吧！"},
            {"id": 52022, "shape": 3004, "icon": 3004, "npc_type": 4104, "x": 14, "y": 76, "dir": 3, "name": "鑒定師", "title": "裝備鑒定", "greeting": "未鑒定的神兵寶甲，經老夫慧眼一識便知凡品或神器！"},
            {"id": 52023, "shape": 3003, "icon": 3003, "npc_type": 4183, "x": 17, "y": 89, "dir": 3, "name": "鐵匠", "title": "打造鑲嵌", "greeting": "千錘百煉出精鋼，打造、鑲嵌寶石儘管交給我！"},
            {"id": 52024, "shape": 3012, "icon": 3012, "npc_type": 1104, "x": 31, "y": 159, "dir": 3, "name": "技能教師", "title": "武學傳授", "greeting": "明月城武館匯聚天下百藝，少俠想鑽研哪門功夫？"},
            {"id": 52025, "shape": 3024, "icon": 3024, "npc_type": 4187, "x": 179, "y": 78, "dir": 3, "name": "食品店老闆", "title": "食品店", "greeting": "八珍玉食、瓊漿玉液，客官裡面請！"},
            {"id": 52026, "shape": 3022, "icon": 3022, "npc_type": 1082, "x": 198, "y": 72, "dir": 3, "name": "裝備店老闆", "title": "裝備店", "greeting": "明月城名匠打造的兵器防具，件件皆是精品！"},
            {"id": 52027, "shape": 3014, "icon": 3014, "npc_type": 1079, "x": 223, "y": 69, "dir": 3, "name": "雜貨店老闆", "title": "雜貨店", "greeting": "飛行旗、如意寶玉、百貨雜物應有盡有！"},
            {"id": 52028, "shape": 3020, "icon": 3020, "npc_type": 1078, "x": 244, "y": 68, "dir": 3, "name": "藥店老闆", "title": "藥店", "greeting": "靈丹妙藥、濟世救人，出門在外多備些丹藥吧！"},
            {"id": 52029, "shape": 3007, "icon": 3007, "npc_type": 4509, "x": 259, "y": 74, "dir": 3, "name": "車伕", "title": "玩家之家", "greeting": "少俠要回溫馨的玩家之家休息，還是前往四國首都？"},
            {"id": 52030, "shape": 3007, "icon": 3007, "npc_type": 2003, "x": 215, "y": 26, "dir": 3, "name": "船夫", "title": "四國傳送人", "greeting": "乘風破浪往來四國首都，少俠請登船！"},
            {"id": 52031, "shape": 3034, "icon": 3034, "npc_type": 4982, "x": 178, "y": 27, "dir": 3, "name": "禮包精靈", "title": "新手禮包", "greeting": "少俠需要領取冒險補給嗎？點擊下方選項即可免費領取銀幣與等級提升！"},
            {"id": 52032, "shape": 3035, "icon": 3035, "npc_type": 4410, "x": 201, "y": 45, "dir": 3, "name": "禮物仙子", "title": "節日禮物領取人", "greeting": "佳節同慶，祝少俠在夢想世界事事順心！"},
            {"id": 52033, "shape": 3010, "icon": 3010, "npc_type": 4839, "x": 299, "y": 67, "dir": 3, "name": "東方朔", "title": "祈福算命", "greeting": "天機不可洩露，今日少俠吉星高照，宜出城歷練！"},
            {"id": 52034, "shape": 3030, "icon": 3030, "npc_type": 4810, "x": 294, "y": 132, "dir": 3, "name": "修煉指導人", "title": "修煉任務", "greeting": "修煉攻法防抗，方能突破武學瓶頸！"},
            {"id": 52035, "shape": 3021, "icon": 3021, "npc_type": 4103, "x": 302, "y": 111, "dir": 3, "name": "老江湖", "title": "江湖百曉", "greeting": "老夫走南闖北數十年，這天下事沒有我不知道的！"},
            {"id": 52036, "shape": 3023, "icon": 3023, "npc_type": 4651, "x": 324, "y": 149, "dir": 3, "name": "幫派總管", "title": "幫派管理", "greeting": "創立幫派、廣納賢才，與兄弟們共創一方霸業！"},
            {"id": 52037, "shape": 3037, "icon": 3037, "npc_type": 4920, "x": 260, "y": 205, "dir": 3, "name": "金總管", "title": "寶物拍賣", "greeting": "天下奇珍拍賣會，價高者得！"},
        ],
        "portals": [
            {"x": 1, "y": 20, "radius": 5, "target_map": 1005, "target_x": 195, "target_y": 75, "desc": "天水平原"},
        ],
    },
    1001: {
        "scene": 1001,
        "mapid": 1001,
        "minimapid": 1001,
        "name": "永澤城",
        "spawn_x": 75,
        "spawn_y": 60,
        "npc": {
            "id": 50003,
            "shape": 3007,
            "icon": 3007,
            "npc_type": 4480,
            "x": 71,
            "y": 58,
            "dir": 3,
            "name": "永澤城傳送人",
            "title": "四國驛站",
            "greeting": "這裡是南遙國都#Y永澤城#n！請問少俠想前往何處？",
        },
        "npcs": [
            {"id": 50003, "shape": 3007, "icon": 3007, "npc_type": 4480, "x": 71, "y": 58, "dir": 3, "name": "永澤城傳送人", "title": "四國驛站", "greeting": "這裡是南遙國都#Y永澤城#n！請問少俠想前往何處？"},
            {"id": 53001, "shape": 3013, "icon": 3013, "npc_type": 4992, "x": 66, "y": 84, "dir": 3, "name": "擺攤區傳送人", "title": "商業集市", "greeting": "永澤城集市熱鬧非凡，少俠也來逛逛吧！"},
            {"id": 53002, "shape": 3016, "icon": 3016, "npc_type": 4152, "x": 59, "y": 49, "dir": 3, "name": "倉庫管理員", "title": "永澤城倉庫", "greeting": "南遙國皇家倉庫，安全可靠！"},
            {"id": 53003, "shape": 3007, "icon": 3007, "npc_type": 2005, "x": 10, "y": 8, "dir": 3, "name": "車伕", "title": "驛站車伕", "greeting": "客官要前往明月城還是其他四國都城？"},
            {"id": 53004, "shape": 3038, "icon": 3038, "npc_type": 4215, "x": 102, "y": 63, "dir": 3, "name": "南遙國王", "title": "南遙之主", "greeting": "朕統御南遙，唯願國泰民安、四海昇平！勇士若立功勳，朕必重賞！"},
            {"id": 53005, "shape": 3028, "icon": 3028, "npc_type": 4405, "x": 117, "y": 36, "dir": 3, "name": "錢莊老闆", "title": "永澤錢莊", "greeting": "金銀匯兌、童叟無欺！"},
            {"id": 53006, "shape": 3015, "icon": 3015, "npc_type": 4226, "x": 24, "y": 77, "dir": 3, "name": "宋姨娘", "title": "永澤居民", "greeting": "永澤城四季如春，真是安居樂業的好地方。"},
            {"id": 53007, "shape": 3019, "icon": 3019, "npc_type": 4281, "x": 20, "y": 22, "dir": 3, "name": "桃葉兒", "title": "永澤居民", "greeting": "桃花塢裡桃花庵，少俠見過城外的桃花林嗎？"},
            {"id": 53008, "shape": 3017, "icon": 3017, "npc_type": 4331, "x": 85, "y": 61, "dir": 3, "name": "吳教頭", "title": "禁軍教頭", "greeting": "南遙禁軍個個以一當十，少俠可敢切磋兩招？"},
            {"id": 53009, "shape": 3020, "icon": 3020, "npc_type": 1029, "x": 81, "y": 31, "dir": 3, "name": "藥店老闆", "title": "藥店", "greeting": "南遙上等草藥煉製的丹丸，包管藥到病除！"},
            {"id": 53010, "shape": 3014, "icon": 3014, "npc_type": 1030, "x": 52, "y": 25, "dir": 3, "name": "雜貨店老闆", "title": "雜貨店", "greeting": "南北雜貨一應俱全，客官隨便挑！"},
            {"id": 53011, "shape": 3022, "icon": 3022, "npc_type": 1083, "x": 27, "y": 45, "dir": 3, "name": "裝備店老闆", "title": "裝備店", "greeting": "百煉兵刃、精工鎧甲，少俠請過目！"},
        ],
        "portals": [],
    },
    1007: {
        "scene": 1007,
        "mapid": 1007,
        "minimapid": 1007,
        "name": "香葉城",
        "spawn_x": 65,
        "spawn_y": 55,
        "npc": {
            "id": 50004,
            "shape": 3007,
            "icon": 3007,
            "npc_type": 4480,
            "x": 62,
            "y": 52,
            "dir": 3,
            "name": "香葉城傳送人",
            "title": "四國驛站",
            "greeting": "這裡是天寧國都#Y香葉城#n！請問少俠想前往何處？",
        },
        "npcs": [
            {"id": 50004, "shape": 3007, "icon": 3007, "npc_type": 4480, "x": 62, "y": 52, "dir": 3, "name": "香葉城傳送人", "title": "四國驛站", "greeting": "這裡是天寧國都#Y香葉城#n！請問少俠想前往何處？"},
            {"id": 54001, "shape": 3013, "icon": 3013, "npc_type": 4992, "x": 66, "y": 84, "dir": 3, "name": "擺攤區傳送人", "title": "商業集市", "greeting": "香葉城商賈雲集，快來看看吧！"},
            {"id": 54002, "shape": 3016, "icon": 3016, "npc_type": 4152, "x": 59, "y": 49, "dir": 3, "name": "倉庫管理員", "title": "香葉城倉庫", "greeting": "貴重物品交給我保管，萬無一失！"},
            {"id": 54003, "shape": 3007, "icon": 3007, "npc_type": 2005, "x": 10, "y": 8, "dir": 3, "name": "車伕", "title": "驛站車伕", "greeting": "客官想去哪座城市？"},
            {"id": 54004, "shape": 3038, "icon": 3038, "npc_type": 4259, "x": 102, "y": 63, "dir": 3, "name": "天寧國王", "title": "天寧之主", "greeting": "天寧古國，香葉飄香。歡迎遠道而來的少俠！"},
            {"id": 54005, "shape": 3028, "icon": 3028, "npc_type": 4405, "x": 117, "y": 36, "dir": 3, "name": "錢莊老闆", "title": "香葉錢莊", "greeting": "天寧錢莊信譽卓著！"},
            {"id": 54006, "shape": 3008, "icon": 3008, "npc_type": 4260, "x": 24, "y": 77, "dir": 3, "name": "陳百萬", "title": "香葉富商", "greeting": "和氣生財，日進斗金！"},
            {"id": 54007, "shape": 3021, "icon": 3021, "npc_type": 4330, "x": 85, "y": 61, "dir": 3, "name": "護林長老", "title": "香葉長老", "greeting": "守護山林草木，方得天地庇佑。"},
            {"id": 54008, "shape": 3031, "icon": 3031, "npc_type": 4288, "x": 20, "y": 22, "dir": 3, "name": "綠姬", "title": "香葉才女", "greeting": "一曲清歌動九城，少俠可願聽我撫琴一曲？"},
            {"id": 54009, "shape": 3020, "icon": 3020, "npc_type": 1039, "x": 81, "y": 31, "dir": 3, "name": "藥店老闆", "title": "藥店", "greeting": "百草靈藥，應有盡有！"},
            {"id": 54010, "shape": 3014, "icon": 3014, "npc_type": 1040, "x": 52, "y": 25, "dir": 3, "name": "雜貨店老闆", "title": "雜貨店", "greeting": "客官需要什麼雜貨儘管開口！"},
            {"id": 54011, "shape": 3022, "icon": 3022, "npc_type": 1084, "x": 27, "y": 45, "dir": 3, "name": "裝備店老闆", "title": "裝備店", "greeting": "上好兵刃甲冑，助少俠縱橫江湖！"},
        ],
        "portals": [],
    },
    1005: {
        "scene": 1005,
        "mapid": 1005,
        "minimapid": 1005,
        "name": "天水平原",
        "spawn_x": 30,
        "spawn_y": 30,
        "npc": {
            "id": 50005,
            "shape": 3007,
            "icon": 3007,
            "npc_type": 4480,
            "x": 26,
            "y": 28,
            "dir": 3,
            "name": "天水平原傳送人",
            "title": "驛站傳送",
            "greeting": "這裡是連接清風村與明月城的#Y天水平原#n！",
        },
        "npcs": [
            {"id": 50005, "shape": 3007, "icon": 3007, "npc_type": 4480, "x": 26, "y": 28, "dir": 3, "name": "天水平原傳送人", "title": "驛站傳送", "greeting": "這裡是連接清風村與明月城的#Y天水平原#n！"},
            {"id": 55001, "shape": 3018, "icon": 3018, "npc_type": 4301, "x": 16, "y": 65, "dir": 3, "name": "愛蘿俠士", "title": "平原游俠", "greeting": "天水平原風光壯麗，少俠也是來此遊歷的嗎？"},
            {"id": 55002, "shape": 3010, "icon": 3010, "npc_type": 4302, "x": 111, "y": 106, "dir": 3, "name": "月夜先生", "title": "隱世高人", "greeting": "明月出天山，蒼茫雲海間。"},
        ],
        "portals": [
            {"x": 200, "y": 75, "radius": 6, "target_map": 1054, "target_x": 10, "target_y": 22, "desc": "明月城"},
        ],
    },
    1028: {
        "scene": 1028,
        "mapid": 1028,
        "minimapid": 1028,
        "name": "長風島",
        "spawn_x": 15,
        "spawn_y": 105,
        "npc": {
            "id": 50006,
            "shape": 3007,
            "icon": 3007,
            "npc_type": 4480,
            "x": 12,
            "y": 102,
            "dir": 3,
            "name": "長風島傳送人",
            "title": "海島驛站",
            "greeting": "海風吹拂的#Y長風島#n，少俠要返回清風村還是前往明月城？",
        },
        "npcs": [
            {"id": 50006, "shape": 3007, "icon": 3007, "npc_type": 4480, "x": 12, "y": 102, "dir": 3, "name": "長風島傳送人", "title": "海島驛站", "greeting": "海風吹拂的#Y長風島#n，少俠要返回清風村還是前往明月城？"},
            {"id": 56001, "shape": 3035, "icon": 3035, "npc_type": 4410, "x": 138, "y": 92, "dir": 3, "name": "珊瑚仙子", "title": "珊瑚迷宮守衛", "greeting": "前方就是神秘的珊瑚迷宮，少俠小心海浪！"},
            {"id": 56002, "shape": 3021, "icon": 3021, "npc_type": 3021, "x": 65, "y": 62, "dir": 3, "name": "海島漁夫", "title": "長風島漁民", "greeting": "今日海面風平浪靜，正是出海垂釣的好時節！"},
        ],
        "portals": [
            {"x": 5, "y": 108, "radius": 4, "target_map": 1025, "target_x": 178, "target_y": 14, "desc": "清風村"},
        ],
    },
}


def _open_all_portals() -> None:
    """傳送點全開：每個場景都補上通往**其餘所有場景**的傳送陣（無等級/任務門檻）。

    既有（手工按原版主城動線寫的）傳送陣保留；缺的方向按場景 id 排序補在
    (3, 10+8*i) 這條左側邊線上，半徑 4 —— mock 自己的地圖資料是合成的，
    這裡只保證「任何場景都能走到任何場景」，不會動客戶端任何檔案。
    """
    for mid, m in MAPS.items():
        have = {int(p.get("target_map", 0)) for p in m.get("portals", [])}
        others = [o for o in sorted(MAPS) if o != mid and o not in have]
        for i, target in enumerate(others):
            m.setdefault("portals", []).append(
                {
                    "x": 3,
                    "y": 10 + 8 * i,
                    "radius": 4,
                    "target_map": target,
                    "target_x": int(MAPS[target].get("spawn_x", 20)),
                    "target_y": int(MAPS[target].get("spawn_y", 20)),
                    "desc": MAPS[target]["name"],
                }
            )


_open_all_portals()


def ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(msg: str) -> None:
    print(f"[{ts()}] {msg}", flush=True)


def encode_big5(text: str, fixed_len: int | None = None) -> bytes:
    raw = text.encode("cp950", errors="replace")
    if fixed_len is not None:
        if len(raw) >= fixed_len:
            return raw[:fixed_len]
        return raw + b"\x00" * (fixed_len - len(raw))
    return raw


def decode_big5(raw: bytes) -> str:
    raw = raw.split(b"\x00", 1)[0]
    return raw.decode("cp950", errors="replace")


def simple_decrypt(data: bytes) -> bytes:
    """Inverse of `netlogin.SimpleEncrypt` (`key = [73, 84, 71, 213, 21, 90]`)."""
    key = (73, 84, 71, 213, 21, 90)
    out = bytearray(len(data))
    for i, b in enumerate(data):
        out[i] = (b - key[i % 6]) & 0xFF
    return bytes(out)


def compute_hello_reply_bytes(seed: int) -> bytes:
    """
    Computes the exact 25-byte `NakedSend` payload sent by `netlogin.S2CHello(netobj)`:
      seed = ((0x100000000 + seed) % 3227993 + 2562088) ^ 6636321
    First 3 bytes are little-endian `seed & 0xFFFFFF`.
    """
    s = ((0x100000000 + (seed & 0xFFFFFFFF)) % 3227993 + 2562088) ^ 6636321
    return bytes([s & 0xFF, (s >> 8) & 0xFF, (s >> 16) & 0xFF])


# ============================================================================
# 2. Client Environment Auto-Patcher (`nocheck`, `server.ini`, `script.fls`)
# ============================================================================

# In `script/login/netlogin.py` (entry idx=4082, eid=0xcf8ea6e5), `S2CHello` executes:
#   net.g_Net.SetSeed(seed)
# which in VM #1 bytecode is the 16-byte sequence:
#   \x85\x04\x00 (LOAD_GLOBAL 4 'net')
#   \xd9\x05\x00 (LOAD_ATTR 5 'g_Net')
#   \xd9\x06\x00 (LOAD_ATTR 6 'SetSeed')
#   \xc1\x01\x00 (LOAD_FAST 1 'seed')
#   \xda\x01\x00 (CALL_FUNCTION 1)
#   \x41         (POP_TOP)
# Replacing those 16 bytes with `\x8f\x00\x00\x41` * 4 (`LOAD_CONST 0; POP_TOP` * 4)
# keeps `CNetClient`'s `[ebx+0xea]` cipher flag at `0` (100% plaintext/uncompressed)
# without changing the entry length or any jump/line-number offsets.
NETLOGIN_IDX = 4082
NETLOGIN_EID = 0xCF8EA6E5
NETLOGIN_KEYS = [137, 51, 151, 253, 157]
NETLOGIN_BOUNDS = [6793, 13651, 20415, 27234]
SETSEED_ORIG_BYTES = b"\x85\x04\x00\xd9\x05\x00\xd9\x06\x00\xc1\x01\x00\xda\x01\x00A"
SETSEED_NOP_EXACT_BYTES = b"\x8f\x00\x00\x41\x8f\x00\x00\x41\x8f\x00\x00\x41\xc1\x00\x00\x41"
SETSEED_NOP_BYTES = b"\x8f\x00\x00A" * 4


def _xor_segments(data: bytes, keys: list[int], bounds: list[int]) -> bytes:
    pts = [0] + bounds + [len(data)]
    chunks = []
    for i in range(5):
        k = keys[i]
        seg = data[pts[i] : pts[i + 1]]
        chunks.append(bytes(b ^ k for b in seg))
    return b"".join(chunks)


def patch_script_fls_setseed(repo_root: Path, restore: bool = False) -> bool:
    """
    Patches (or restores) `idx=4082` (`script\\login\\netlogin.py`) in `data/script.fls`
    so `net.g_Net.SetSeed(seed)` is bypassed and all C2GS/GS2C traffic remains plaintext.
    """
    fls_path = repo_root / "data" / "script.fls"
    bak_path = repo_root / "data" / "script.fls.bak"
    if not fls_path.exists():
        log(f"[WARN] {fls_path} not found; skipping client script.fls check.")
        return False

    if restore:
        if bak_path.exists():
            shutil.copy2(bak_path, fls_path)
            log(f"[OK] Restored original {fls_path} from {bak_path}")
            return True
        log(f"[INFO] No backup {bak_path} found; checking if in-place restore is needed...")

    arch = bytearray(fls_path.read_bytes())
    if arch[:4] != b"0SLF":
        log(f"[WARN] {fls_path} is not a 0SLF archive.")
        return False

    count = struct.unpack_from("<I", arch, 4)[0]
    idx_off = struct.unpack_from("<I", arch, 8)[0]
    if NETLOGIN_IDX >= count:
        return False

    raw_ent = struct.unpack_from("<IIII", arch, idx_off + NETLOGIN_IDX * 16)
    eid, r1, r2, r3 = raw_ent
    if eid != NETLOGIN_EID:
        log(f"[WARN] script.fls idx={NETLOGIN_IDX} eid=0x{eid:08x} != 0x{NETLOGIN_EID:08x}")
        return False

    clen = (((r1 * eid + 0x0DF25E) & 0xFFFFFFFF) ^ r2) & 0xFFFFFFFF
    doff = (((r2 * NETLOGIN_IDX * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ r3) & 0xFFFFFFFF
    exp = zlib.decompress(bytes(arch[doff : doff + clen]))
    dec = _xor_segments(exp, NETLOGIN_KEYS, NETLOGIN_BOUNDS)

    if restore:
        if SETSEED_NOP_EXACT_BYTES in dec:
            patched_dec = dec.replace(SETSEED_NOP_EXACT_BYTES, SETSEED_ORIG_BYTES, 1)
        elif SETSEED_NOP_BYTES in dec:
            patched_dec = dec.replace(SETSEED_NOP_BYTES, SETSEED_ORIG_BYTES, 1)
        else:
            log("[OK] data/script.fls already has original SetSeed bytecode.")
            return True
    else:
        if SETSEED_NOP_EXACT_BYTES in dec or SETSEED_NOP_BYTES in dec:
            log("[OK] data/script.fls already patched (SetSeed bypass active).")
            return True
        if SETSEED_ORIG_BYTES not in dec:
            log("[WARN] Could not locate SetSeed bytecode pattern in script/login/netlogin.py.")
            return False
        if not bak_path.exists():
            shutil.copy2(fls_path, bak_path)
            log(f"[OK] Backed up original archive to {bak_path}")
        patched_dec = dec.replace(SETSEED_ORIG_BYTES, SETSEED_NOP_EXACT_BYTES, 1)

    # Rebuild entry 4082 (in-place if compressed size matches original clen=13869)
    new_exp = _xor_segments(patched_dec, NETLOGIN_KEYS, NETLOGIN_BOUNDS)
    new_comp = zlib.compress(new_exp, 9)
    if len(new_comp) == clen:
        arch[doff : doff + clen] = new_comp
        fls_path.write_bytes(bytes(arch))
        action = "Restored SetSeed in" if restore else "Patched SetSeed bypass in-place in"
        log(f"[OK] {action} {fls_path} (idx={NETLOGIN_IDX}, clen={clen})")
        return True

    out_header_and_table = bytearray(arch[: idx_off + count * 16])
    out_data = bytearray()
    for idx in range(count):
        e_id, e_r1, e_r2, e_r3 = struct.unpack_from("<IIII", arch, idx_off + idx * 16)
        e_clen = (((e_r1 * e_id + 0x0DF25E) & 0xFFFFFFFF) ^ e_r2) & 0xFFFFFFFF
        e_doff = (((e_r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ e_r3) & 0xFFFFFFFF
        chunk = new_comp if idx == NETLOGIN_IDX else arch[e_doff : e_doff + e_clen]
        new_doff = idx_off + count * 16 + len(out_data)
        new_clen = len(chunk)
        new_r2 = (((e_r1 * e_id + 0x0DF25E) & 0xFFFFFFFF) ^ new_clen) & 0xFFFFFFFF
        new_r3 = (((new_r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ new_doff) & 0xFFFFFFFF
        struct.pack_into("<IIII", out_header_and_table, idx_off + idx * 16, e_id, e_r1, new_r2, new_r3)
        out_data.extend(chunk)

    fls_path.write_bytes(bytes(out_header_and_table) + bytes(out_data))
    action = "Restored SetSeed in" if restore else "Patched SetSeed bypass in"
    log(f"[OK] {action} {fls_path} (idx={NETLOGIN_IDX} script\\login\\netlogin.py)")
    return True


NOCHECK_SECTION = "game"
NOCHECK_GM_KEY = "gm"
NOCHECK_GM_VALUE = "1"


def ensure_nocheck_gm(nocheck_path: Path) -> str:
    """Guarantees `nocheck` carries `[game] gm=1`; returns one log line.

    One file, two mutually independent switches -- both are needed:

    * `permission.InitSpecialVersion()` is literally `os.path.exists('nocheck')`,
      so an **empty** file already releases the ~9 `GetSpecialVersion()` gates.
    * `permission.IsOpenGm()` is `GetPermission('gm')`, which reads **this file's
      `[game]` section** (`cfg.GetSysDict('nocheck')` -> `cfg.readanalyser`);
      the value must be exactly the string `'1'`.

    With an empty file the second one is false, and `clientcommand.DoCommand`
    returns on its very first line (`if not permission.IsOpenGm(): return`).
    A `$command` typed in the chat box is then dropped before it is even sent
    as a chat packet -- which is exactly the "typing commands does nothing" symptom.

    `cfg.readanalyser` lowercases **keys only** (`parts[0].strip().lower()`);
    section names are stored verbatim, so the header must be `[game]`.

    Reads/writes as latin-1 so any pre-existing non-UTF8 bytes round-trip untouched.
    """
    header = f"[{NOCHECK_SECTION}]"
    entry = f"{NOCHECK_GM_KEY}={NOCHECK_GM_VALUE}"

    if not nocheck_path.exists():
        nocheck_path.write_text(f"{header}\n{entry}\n", encoding="latin-1")
        return f"[OK] Created {nocheck_path} with {header} {entry} (GM $ commands enabled)"

    try:
        text = nocheck_path.read_text(encoding="latin-1")
    except OSError as exc:
        return f"[WARN] 無法讀取 {nocheck_path}: {exc}"

    lines = text.splitlines()
    section_at = next((i for i, line in enumerate(lines) if line.strip() == header), None)

    if section_at is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines += [header, entry]
    else:
        end = len(lines)
        for i in range(section_at + 1, len(lines)):
            if lines[i].strip().startswith("["):
                end = i
                break
        key_at = None
        for i in range(section_at + 1, end):
            key, sep, _value = lines[i].partition("=")
            if sep and key.strip().lower() == NOCHECK_GM_KEY:
                key_at = i
                break
        if key_at is None:
            lines.insert(end, entry)
        elif lines[key_at].partition("=")[2].strip() == NOCHECK_GM_VALUE:
            return f"[OK] Found {nocheck_path} with {header} {entry}"
        else:
            lines[key_at] = entry

    nocheck_path.write_text("\n".join(lines) + "\n", encoding="latin-1")
    return f"[OK] Fixed {nocheck_path}: {header} {entry} (GM $ commands enabled)"


def _is_git_tracked(path: Path) -> bool:
    """True if `path` is tracked by the surrounding git work tree (best effort)."""
    import subprocess

    try:
        out = subprocess.run(
            ["git", "ls-files", "--error-unmatch", path.name],
            cwd=str(path.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0


def ensure_client_ready(repo_root: Path, patch_fls: bool = True) -> None:
    """Ensures `nocheck`, `server.ini`, and `data/script.fls` are ready for local play."""
    fls_path = repo_root / "data" / "script.fls"
    if not fls_path.exists():
        log("=" * 72)
        log(f"[WARN] 未在當前目錄找到遊戲客戶端檔案: {fls_path}")
        log("[WARN] 請務必將 mock_server.py 放到遊戲根目錄 (與 mx.exe、server.ini 同級) 後再運行！")
        log("       否則客戶端在收到 GS2C_HELLO 後會開啟 SetSeed 封包加密，導致卡在「正在登錄中....」。")
        log("=" * 72)
        return

    nocheck_path = repo_root / "nocheck"
    log(ensure_nocheck_gm(nocheck_path))

    if patch_fls:
        if _is_git_tracked(fls_path):
            log("=" * 72)
            log(f"[WARN] {fls_path} 是 git 追蹤的檔案，為了不動到倉庫內容，本次【不】打補丁。")
            log("[WARN] 若確實要用本機客戶端連進來，請自行在複製出來的客戶端目錄執行：")
            log("       python mock_server.py --patch-client     # 打補丁（先備份 .bak）")
            log("       python mock_server.py --restore-client   # 還原")
            log("=" * 72)
            return
        try:
            patch_script_fls_setseed(repo_root, restore=False)
        except PermissionError:
            log("=" * 72)
            log(f"[ERROR] 無法寫入 {fls_path} (檔案正被 mx.exe 佔用)！")
            log("請先【完全關閉 mx.exe 遊戲客戶端】，再重新運行 python mock_server.py 打補丁，然後再啟動 mx.exe！")
            log("=" * 72)


# ============================================================================
# 3. Framing & Packet Builders (Server -> Client GS2C)
# ============================================================================


# Continuation bytes after the `0xFF` escape of a long body.
#
# The constructor of the native client sets this field to 2, but the client's own
# script layer overrides it at connect time, so the wire format this client really
# reads is **3** bytes:
#   * `mx.exe` VA 0x4AB23F (constructor): `c7 87 90 69 00 00 02 00 00 00` -> `[+0x6990] = 2`
#   * `mx.exe` VA 0x4AB5B7 (`CNetClient::RecvPacket`, 0x4AB540): reads `[+0x6990]`
#     continuation bytes after seeing `0xFF`
#   * `mx.exe` VA 0x468400 (`net.SetMaxLenBytes` implementation, PyMethodDef at
#     0x7E0FD0): `8b 4d fc 8d 41 fe 83 f8 02 77 1b 8b ... 89 88 90 69 00 00` =
#     accept only 2/3/4, then `mov [eax+0x6990], ecx` - the SAME field as above
#   * `data/script.fls` idx=3176 (`script/net.py`), `CNet.__init__`: `self.SetMaxLenBytes(3)`
#     runs on every client-side connection, so the effective value is 3.
# Sending 2 continuation bytes makes the client read the opcode byte as part of the
# length (e.g. `FF 94 01 10 ...` -> L = 0x100194) and it waits forever: the only long
# packet in this build is `GS2C_PROP_INIT` (body 404 B), i.e. the packet that switches
# the client from the loading screen into the map.
MAX_LEN_BYTES = 3


def frame_gs2c(opcode: int, payload: bytes = b"") -> bytes:
    """
    Wraps a GS2C packet for `CNetClient::RecvPacket` (`0x004ab540`):
      - `body = bytes([opcode]) + payload`
      - If `len(body) < 0xFF`: `bytes([len(body)]) + body`
      - If `len(body) >= 0xFF`: `b'\\xff' + <len(body) as MAX_LEN_BYTES little-endian> + body`
        (`MAX_LEN_BYTES = 3`, see the comment above - do not lower it to 2)
    """
    body = bytes([opcode & 0xFF]) + payload
    n = len(body)
    if n < 0xFF:
        return bytes([n]) + body
    if n >= 1 << (8 * MAX_LEN_BYTES):
        raise ValueError(
            f"body {n}B does not fit in MAX_LEN_BYTES={MAX_LEN_BYTES}; "
            "the client cannot frame it (split the packet instead)"
        )
    return b"\xff" + n.to_bytes(MAX_LEN_BYTES, "little") + body


def build_gs2c_hello(seed: int = 0x12345678, server_num: int = 3, is_cert: int = 0) -> bytes:
    """
    `GS2C_HELLO = 1` -> `netlogin.S2CHello(netobj)`:
      - `seed = netobj.UnpackInt(4)`
      - `g_ServerNum = netobj.UnpackInt(2)`
      - `isUseCertServer = netobj.UnpackInt(1)`
    """
    payload = struct.pack("<IHB", seed & 0xFFFFFFFF, server_num & 0xFFFF, is_cert & 0xFF)
    return frame_gs2c(GS2C_HELLO, payload)


def build_gs2c_login_account_info(role_count: int, cur_time: int | None = None, vid: int = 1) -> bytes:
    """
    `GS2C_LOGIN_ACCOUNT_INFO = 15` -> `netlogin.S2CLoginAccountInfo(netobj)`:
      - `Count = netobj.UnpackInt(1)`
      - `CurrentTime = netobj.UnpackInt(4)`
      - `vid = netobj.UnpackInt(1)` (1..5 valid; 99 triggers '數據已經轉移')
    """
    if cur_time is None:
        cur_time = int(time.time())
    payload = struct.pack("<BIB", role_count & 0xFF, cur_time & 0xFFFFFFFF, vid & 0xFF)
    return frame_gs2c(GS2C_LOGIN_ACCOUNT_INFO, payload)


def build_gs2c_login_player_info(role: dict[str, Any]) -> bytes:
    """
    `GS2C_LOGIN_PLAYER_INFO = 3` -> `netlogin.S2CLoginRoleInfo(netobj)`:
      - `ID`: 4B LE
      - `time`: 4B LE
      - `Icon`: 1B
      - `Shape`: 2B LE (111..232 playable human shapes)
      - `Desc`: 2B LE (color bits)
      - `Level`: 1B
      - `School`: 1B (1=戰士, 2=法師, 3=術士, ...)
      - `Race`: 1B
      - `iPrepareLoad`: 1B (0 or 1)
      - `Point`: 4B LE
      - `Name`: 16B Big5 NUL-padded string
    Total payload = 37 bytes (38 bytes including opcode).
    """
    shape = normalize_player_shape(int(role.get("shape", 111)))
    icon = int(role.get("icon", 0))
    if icon <= 0:
        icon = SHAPE_DEFAULT_ICON.get(shape, 1)
    school = int(role.get("school", 1))
    if school <= 0:
        school = 1
    name_b = encode_big5(role.get("name", "夢想少俠"), 16)
    payload = (
        struct.pack(
            "<IIBHHBBBBI",
            int(role.get("id", 10001)) & 0xFFFFFFFF,
            int(role.get("time", int(time.time()))) & 0xFFFFFFFF,
            icon & 0xFF,
            shape & 0xFFFF,
            int(role.get("color", 0)) & 0xFFFF,
            int(role.get("level", 60)) & 0xFF,
            school & 0xFF,
            int(role.get("race", 1)) & 0xFF,
            int(role.get("prepare_load", 0)) & 0xFF,
            int(role.get("point", 100)) & 0xFFFFFFFF,
        )
        + name_b
    )
    return frame_gs2c(GS2C_LOGIN_PLAYER_INFO, payload)


def build_gs2c_login_player_add() -> bytes:
    """
    `GS2C_LOGIN_PLAYER_ADD = 6` -> `netlogin.S2CLoginPlayerAdd(netobj)`:
      No fields unpacked; closes `createrole`, shows '恭喜您，創建角色成功！',
      selects the newly added role, and invokes `selectrole.EnterGame()`.
    """
    return frame_gs2c(GS2C_LOGIN_PLAYER_ADD, b"")


def build_gs2c_login_player_del(role_id: int) -> bytes:
    """
    `GS2C_LOGIN_PLAYER_DEL = 10` -> `netlogin.S2CLoginDelRole(netobj)`:
      - `id = netobj.UnpackInt(4)`
    """
    return frame_gs2c(GS2C_LOGIN_PLAYER_DEL, struct.pack("<I", role_id & 0xFFFFFFFF))


def build_gs2c_login_error(code: int) -> bytes:
    """
    `GS2C_LOGIN_ERROR = 7` -> `netlogin.S2CLoginError(netobj)`:
      - `iCode = netobj.UnpackInt(2)`
    """
    return frame_gs2c(GS2C_LOGIN_ERROR, struct.pack("<H", code & 0xFFFF))


def build_gs2c_prop_init(role: dict[str, Any]) -> bytes:
    """
    `GS2C_PROP_INIT = 16` -> `nethero.S2CPropInit(netobj)`:
      1. `iPlayerRealID = netobj.UnpackInt(4)`
      2. `prop.UnPackPlayerID(iPlayerRealID, netobj)`:
         - `iPlayerShowID = netobj.UnpackInt(4)`
         - `iPrettyID = netobj.UnpackInt(4)`
      3. `hero.CreateProp(netobj)` (`script/hero.py` in `data/script.fls`):
         Iterates through all 112 `ITEM_SERVERINIT` entries in exact declaration order:
           - `TBYTE` (0): 1B
           - `TWORD` (1): 2B LE
           - `TDWORD` (2): 4B LE
           - `TDESC` (4): 1B count (=0)
           - `TLONG` (5): 8B LE
           - `n > 6`: fixed-length string of `n` bytes (Big5, NUL-padded)
    Total payload = 12 + 391 = 403 bytes.
    """
    role_id = int(role.get("id", 10001)) & 0xFFFFFFFF
    level = int(role.get("level", 60)) & 0xFF
    shape = normalize_player_shape(int(role.get("shape", 111))) & 0xFFFF
    sex = get_sex_for_shape(shape) & 0xFF
    icon = int(role.get("icon", 0)) & 0xFF
    if icon <= 0:
        icon = SHAPE_DEFAULT_ICON.get(shape, 1) & 0xFF
    school = int(role.get("school", 1)) & 0xFF
    if school <= 0:
        school = 1
    liupai = normalize_liupai(int(role.get("liupai", 1001)), school) & 0xFFFF
    cash = int(role.get("cash", 888888))
    title_id = int(role.get("title_id", 101)) & 0xFFFF
    title_color = int(role.get("title_color", 0)) & 0xFF
    name_20 = encode_big5(role.get("name", "夢想少俠"), 20)
    org_20 = encode_big5(role.get("faction", "清風明月幫"), 20)
    title_60 = encode_big5(role.get("title", "夢想開拓者"), 60)
    fake_name_20 = encode_big5("", 20)

    str_all = int(role.get("str_all", 100 + level * 2)) & 0xFFFF
    mag_all = int(role.get("mag_all", 100 + level * 2)) & 0xFFFF
    cha_all = int(role.get("cha_all", 90 + level * 2)) & 0xFFFF
    dex_all = int(role.get("dex_all", 90 + level * 2)) & 0xFFFF
    con_all = int(role.get("con_all", 100 + level * 2)) & 0xFFFF
    free_point = int(role.get("point", 50)) & 0xFFFF

    att_all = int(role.get("att_all", 450 + str_all * 5)) & 0xFFFF
    def_all = int(role.get("def_all", 350 + con_all * 4)) & 0xFFFF
    spe_all = int(role.get("spe_all", 180 + dex_all * 3)) & 0xFFFF
    magdef_all = int(role.get("magdef_all", 320 + mag_all * 4)) & 0xFFFF
    hp_max = int(role.get("hp_max", 1200 + con_all * 15)) & 0xFFFF
    mp_max = int(role.get("mp_max", 800 + mag_all * 10)) & 0xFFFF

    buf = bytearray()
    # 1. iPlayerRealID (4B), iPlayerShowID (4B), iPrettyID (4B) -> 12 bytes
    buf.extend(struct.pack("<III", role_id, role_id, 0))

    # 2. All 112 ITEM_SERVERINIT fields in exact `script/hero.py` order (391 bytes):
    # [000] m_Icon(1B), [001] m_Shape(2B), [002] m_Desc(TDESC=1B:0), [003] m_Sex(1B: 1=男, 2=女)
    buf.extend(struct.pack("<BHBB", icon, shape, 0, sex))
    # [004] m_Name(20B)
    buf.extend(name_20)
    # [005] m_Grade(1B), [006] m_Cash(8B), [007] m_Saving(4B), [008] m_Exp(4B),
    # [009] m_NextExp(4B), [010] m_NeedExp(4B), [011] m_Class(1B), [012] m_Country(1B: 1=南遙國)
    buf.extend(struct.pack("<BQIIIIBB", level, cash, 1000000, 150000, 100000, 100000, school, 1))
    # [013] sOrg(20B), [014] m_OrgID(4B), [015] m_EmoteForTitle(2B), [016] m_Title(60B), [017] m_TitleID(2B)
    buf.extend(org_20)
    buf.extend(struct.pack("<IH", 1, 0))
    buf.extend(title_60)
    buf.extend(struct.pack("<H", title_id))
    # [018..025] m_HP(2B), m_HPMax(2B), m_MP(2B), m_MPMax(2B), m_FP(2B), m_FPMax(2B), m_SP(2B), m_SPMax(2B)
    buf.extend(struct.pack("<HHHHHHHH", hp_max, hp_max, mp_max, mp_max, 100, 100, 100, 150))
    # [026..029] m_Huoli(4B), m_Huoli_Max(2B), m_Tili(4B), m_Tili_Max(2B)
    buf.extend(struct.pack("<IHIH", 500, 500, 500, 500))
    # [030..039] m_Att_All, m_Def_All, m_Spe_All, m_Magdef_All, m_Str_All, m_Mag_All, m_Cha_All, m_Dex_All, m_Con_All, m_Point (10 x 2B)
    buf.extend(struct.pack("<HHHHHHHHHH", att_all, def_all, spe_all, magdef_all, str_all, mag_all, cha_all, dex_all, con_all, free_point))
    # [040] m_Switch(4B), [041] m_GridPoint(1B)
    buf.extend(struct.pack("<IB", 0, 20))
    # [042] m_SkillExp(4B), [043] m_PFPoint(4B), [044] m_StoryPoint(2B)
    buf.extend(struct.pack("<IIH", 200000, 500, 100))
    # [045..055] m_Gold, m_UI, m_DoubleExp, m_BuChangExp, m_HeFuExp, m_FixZYQHExp, m_ShuiJingExp,
    #            m_OrgOffer, m_OrgOffer_Max, m_OrgCoin, m_CookPoint (11 x 4B)
    buf.extend(struct.pack("<11I", 88888, 0, 200, 0, 0, 0, 0, 500, 500, 1000, 500))
    # [056] m_FightCash(8B), [057] m_ShenWuBi(4B)
    buf.extend(struct.pack("<QI", 500000, 100000))
    # [058..064] m_SummonMax, m_BagMax, m_VIP, m_FlyFlag, m_GradeLimit, m_Force, m_TitleColor (7 x 1B)
    buf.extend(struct.pack("<7B", 8, 2, 1, 0, 150, 1, title_color))
    # [065] m_RealShape(2B), [066] m_XiulianTotalNeed(1B), [067] m_PhotoEffect(4B), [068] m_IsGuestLogin(4B)
    buf.extend(struct.pack("<HBII", shape, 0, 0, 0))
    # [069] m_NameColor(1B), [070] m_IsMarried(1B), [071] m_Birthday(2B), [072] m_AutoUpgrade(1B), [073] m_IsDYT(1B)
    buf.extend(struct.pack("<BBHBB", 0, 0, 101, 0, 0))
    # [074] m_Liupai(2B), [075] m_SecondLiupai(2B)
    buf.extend(struct.pack("<HH", liupai, 0))
    # [076..080] m_GradeTolJHP, m_GetJHMax4Grade, m_SumCBExp, m_SumHFExp, m_TradeVolumeOfDay (5 x 4B)
    buf.extend(struct.pack("<5I", 0, 0, 0, 0, 0))
    # [081] m_FakeName(20B)
    buf.extend(fake_name_20)
    # [082] m_HideTree(1B), [083] m_ReserveExp(8B), [084] m_DebtCash(4B)
    buf.extend(struct.pack("<BQI", 0, 100000, 0))
    # [085..098] m_HasChangeName(1B), m_Lineup(1B), m_RideCBExp(2B), m_OrgServer(2B),
    #            m_UserState(1B), m_FlyState(1B), m_PriorHorseID(1B), m_HuoyueTotal(2B),
    #            m_DoubleExpCnt(1B), m_AccountAfterData(1B), m_LeftSGPoint(1B),
    #            m_iSiblingType(2B), m_iHasSpecialDance(1B), m_iVIPAutoBuy(1B)
    buf.extend(struct.pack("<BBHHBBBHBBBHBB", 0, 0, 0, 3, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0))
    # [099] m_iSorce(4B), [100] m_AccountID(4B), [101] m_iOrgLevel(1B)
    buf.extend(struct.pack("<IIB", 15000, role_id, 5))
    # [102..106] m_Resist_Xian, m_Resist_Gui, m_Resist_Yao, m_Resist_Zhi, m_Resist_Nian (5 x 2B)
    buf.extend(struct.pack("<5h", 10, 10, 10, 10, 10))
    # [107] m_JiebaiID(4B), [108] m_MarryID(4B), [109] m_iTitleGrade(1B), [110] m_iPrettyID(4B), [111] m_bShowPrettyID(1B)
    buf.extend(struct.pack("<IIBIB", 0, 0, 0, 0, 0))

    assert len(buf) == 403, f"Expected 403 bytes for GS2C_PROP_INIT, got {len(buf)}"
    return frame_gs2c(GS2C_PROP_INIT, bytes(buf))


def _frame_prop_change(entry: bytes) -> bytes:
    """Wraps ONE prop change into `GS2C_PROP_CHANGELIST = 61` (`[count=1] + entry`).

    Why not the dedicated `GS2C_PROP_CHANGE` opcode: see the constant comment above -
    it is shadowed by `GS2C_NPC_CHAT_EXT` in this client build and 17 has no handler,
    so a single prop change can only reach the client through the changelist packet
    (`nethero.S2CMultiPropChange`, which loops `S2CPropChange` per entry).
    """
    return frame_gs2c(GS2C_PROP_CHANGELIST, bytes([1]) + entry)


def build_gs2c_prop_change_word(idx: int, val: int) -> bytes:
    """`GS2C_PROP_CHANGELIST`, one 2-byte `TWORD` field at `ITEM_SERVERINIT[idx]`."""
    return _frame_prop_change(struct.pack("<BH", idx & 0xFF, val & 0xFFFF))


def build_gs2c_prop_change_byte(idx: int, val: int) -> bytes:
    """`GS2C_PROP_CHANGELIST`, one 1-byte `TBYTE` field at `ITEM_SERVERINIT[idx]`."""
    return _frame_prop_change(struct.pack("<BB", idx & 0xFF, val & 0xFF))


def build_gs2c_prop_change_str(idx: int, text: str, fixed_len: int) -> bytes:
    """`GS2C_PROP_CHANGELIST`, one fixed-length string field at `ITEM_SERVERINIT[idx]`."""
    return _frame_prop_change(bytes([idx & 0xFF]) + encode_big5(text, fixed_len))


def build_gs2c_open_ui_new_attr(sub_type: int) -> bytes:
    """
    `GS2C_OPEN_UI_NEW = 234` (`iMain=8, iSub=1..7`) -> `netattribute.S2CProcess(iSub, netobj)`:
    Populates the 7 tabs of `屬性總覽` (`dlgattributemain.py` when clicking `查看屬性`):
      - `iSub=1` (`流派抗性` `S2CSchoolResist`): 12 x signed 2B (`<12h`)
      - `iSub=2` (`其它抗性` `S2COtherResist`):  5 x signed 1B (`<5b`)
      - `iSub=3` (`修煉`     `S2CXiulianInfo`):  `<5BIBBBBI` (18 bytes)
      - `iSub=4` (`卦象`     `S2CGuaXiang`):     `iLen=1B` + `iLen * <BB`
      - `iSub=5` (`星圖`     `S2CXingTu`):       `iLen=1B` + `iLen * <BB`
      - `iSub=6` (`法寶`     `S2CFaBao`):        `<BB` (`iMainFaBaoID`, `iSubFaBaoID`)
      - `iSub=7` (`魔石`     `S2CMoShi`):        `<BB` (`iLevel`, `iPercent`)
    """
    header = struct.pack("<HB", 8, sub_type & 0xFF)
    if sub_type == 1:
        body = struct.pack("<12h", 15, 15, 15, 12, 12, 12, 12, 10, 10, 10, 10, 10)
    elif sub_type == 2:
        body = struct.pack("<5b", 10, 10, 10, 10, 10)
    elif sub_type == 3:
        body = struct.pack("<5BIBBBBI", 10, 10, 10, 10, 10, 50000, 20, 20, 20, 10, 80000)
    elif sub_type == 4:
        body = struct.pack("<B", 3) + struct.pack("<BBBBBB", 1, 5, 2, 5, 3, 5)
    elif sub_type == 5:
        body = struct.pack("<B", 2) + struct.pack("<BBBB", 1, 3, 2, 3)
    elif sub_type == 6:
        body = struct.pack("<BB", 1, 2)
    else:
        body = struct.pack("<BB", 5, 80)
    return frame_gs2c(GS2C_OPEN_UI_NEW, header + body)


def build_gs2c_open_ui_autopoint(role: dict[str, Any]) -> bytes:
    """
    `GS2C_OPEN_UI = 89` (`sub=235`) -> `netopenui.S2CHeroAutoPoint(netobj)`:
      - `sub`: 1B (235)
      - `bSelect`: 1B (0 or 1)
      - `point[0..4]`: 5 x 1B (total = 5 points per level, e.g. 3, 0, 1, 1, 0)
    """
    ap = role.get("autopoint", [3, 0, 1, 1, 0])
    b_sel = int(role.get("autopoint_enable", 1)) & 0xFF
    payload = struct.pack("<BBBBBBB", 235, b_sel, ap[0], ap[1], ap[2], ap[3], ap[4])
    return frame_gs2c(GS2C_OPEN_UI, payload)


PLAYER_TITLES: list[dict[str, Any]] = [
    {"id": 101, "title": "夢想開拓者", "desc": "踏入《夢想世界》的先驅少俠專屬稱謂。", "color": 0},
    {"id": 102, "title": "清風明月俠", "desc": "遊歷清風村與明月城的瀟灑少俠。", "color": 1},
    {"id": 103, "title": "天選之人", "desc": "氣運加身、萬眾矚目的傳奇稱謂。", "color": 2},
    {"id": 104, "title": "名動江湖", "desc": "武藝超群、威震四方的江湖名宿。", "color": 3},
]


def build_gs2c_open_ui_titles(role: dict[str, Any]) -> bytes:
    """
    `GS2C_OPEN_UI = 89` (`sub=183, mode=1`) -> `netopenui.S2CRefreshTitle(netobj)`:
      - `sub`: 1B (183)
      - `mode`: 1B (1)
      - `iTitleNum`: 2B LE
      - `total`: 2B LE
      - For each title (`UnpackTitleNetObj`):
          `iLen`: 1B + `sTitle` (Big5)
          `iTitleID`: 2B LE
          `iCanColor`: 1B
          `iCanDel`: 1B
          `iTop`: 1B
          `iColor`: 1B
          (if `iColor > 0`: `iColorTime`: 1B)
      - `iSelectTitle`: 2B LE
    """
    sel_id = int(role.get("title_id", 101)) & 0xFFFF
    buf = bytearray(struct.pack("<BBHH", 183, 1, len(PLAYER_TITLES), len(PLAYER_TITLES)))
    for t in PLAYER_TITLES:
        tb = encode_big5(t["title"])
        color = int(t.get("color", 0)) & 0xFF
        buf.append(len(tb) & 0xFF)
        buf.extend(tb)
        buf.extend(struct.pack("<HBBBB", int(t["id"]) & 0xFFFF, 1, 0, 0, color))
        if color > 0:
            buf.append(30)  # iColorTime (days)
    buf.extend(struct.pack("<H", sel_id))
    return frame_gs2c(GS2C_OPEN_UI, bytes(buf))


def build_gs2c_title_desc(title_id: int) -> bytes:
    """
    `GS2C_TITLE = 200` (`sub=1`) -> `dlgtitle.S2CTitle`:
      - `sub`: 1B (1)
      - `id`: 2B LE
      - `len`: 1B + `desc` (Big5)
    """
    desc = "《夢想世界》少俠專屬榮譽稱謂。"
    for t in PLAYER_TITLES:
        if int(t["id"]) == title_id:
            desc = t["desc"]
            break
    db = encode_big5(desc)
    return frame_gs2c(GS2C_TITLE, struct.pack("<BHB", 1, title_id & 0xFFFF, len(db) & 0xFF) + db)


STARTER_ITEMS: list[dict[str, Any]] = [
    # Equipped items (`pos = 1..9` in `itemdefine.py` `EQUIPPOS_*`)
    {"id": 20001, "shape": 60030, "pos": 1, "qty": 1, "flag": 64, "name": "飾金軟帽", "ext": "基礎屬性$防禦 +33"},
    {"id": 20002, "shape": 50030, "pos": 2, "qty": 1, "flag": 64, "name": "青霜劍", "ext": "基礎屬性$攻擊 +108"},
    {"id": 20003, "shape": 61030, "pos": 3, "qty": 1, "flag": 64, "name": "精鐵軟甲", "ext": "基礎屬性$防禦 +72"},
    {"id": 20004, "shape": 66030, "pos": 4, "qty": 1, "flag": 64, "name": "幼龍腰帶", "ext": "基礎屬性$氣血 +336"},
    {"id": 20005, "shape": 63030, "pos": 5, "qty": 1, "flag": 64, "name": "風火腕輪", "ext": "基礎屬性$防禦 +20"},
    {"id": 20007, "shape": 64030, "pos": 7, "qty": 1, "flag": 64, "name": "翠微珠鏈", "ext": "基礎屬性$防禦 +24"},
    {"id": 20008, "shape": 65020, "pos": 8, "qty": 1, "flag": 64, "name": "螢火指環", "ext": "基礎屬性$防禦 +7"},
    {"id": 20009, "shape": 62030, "pos": 9, "qty": 1, "flag": 64, "name": "飛狼履", "ext": "基礎屬性$速度 +24"},
    # Inventory items (`pos = 20..59` in `行囊`)
    {"id": 20020, "shape": 21100, "pos": 20, "qty": 30, "flag": 64, "name": "金創藥", "ext": "恢復氣血 200 點"},
    {"id": 20021, "shape": 30031, "pos": 21, "qty": 1, "flag": 64, "name": "飛行旗", "ext": "記錄座標並瞬間傳送"},
    {"id": 20022, "shape": 70662, "pos": 22, "qty": 10, "flag": 64, "name": "還童丹", "ext": "洗煉召喚獸資質與技能"},
    {"id": 20023, "shape": 25405, "pos": 23, "qty": 1, "flag": 64, "name": "魔獸要訣", "ext": "記載著召喚獸技能的古籍"},
    {"id": 20024, "shape": 25814, "pos": 24, "qty": 5, "flag": 64, "name": "經驗心得", "ext": "使用後獲得豐厚角色經驗"},
    {"id": 20025, "shape": 51030, "pos": 25, "qty": 1, "flag": 64, "name": "柳葉刀", "ext": "基礎屬性$攻擊 +108"},
]


def build_gs2c_item_add(it: dict[str, Any], item_type: int = 1, add_type: int = 0) -> bytes:
    """
    `GS2C_ITEM_ADD = 33` -> `netitem.S2CItemAdd(netobj)`:
      - `iItemType`: 1B (1 -> `ITEM_NORMAL = 0`)
      - `id`: 4B LE
      - `shape`: 4B LE
      - `special_flag`: 4B LE
      - `quantity`: 2B LE
      - `pos`: 1B (`1..9` = equipped, `20..59` = inventory bag)
      - `iDataLen`: 2B LE (`2`)
      - `sData`: `b"{}"` (`C_marshal.loads(b"{}")` -> `{}`)
      - `iType`: 1B (`0`)
    """
    ext_marshal = b"{}"
    payload = (
        struct.pack(
            "<BIIIHBH",
            item_type & 0xFF,
            int(it["id"]) & 0xFFFFFFFF,
            int(it["shape"]) & 0xFFFFFFFF,
            int(it.get("flag", 64)) & 0xFFFFFFFF,
            int(it.get("qty", 1)) & 0xFFFF,
            int(it["pos"]) & 0xFF,
            len(ext_marshal),
        )
        + ext_marshal
        + bytes([add_type & 0xFF])
    )
    return frame_gs2c(GS2C_ITEM_ADD, payload)


def build_gs2c_item_key_end() -> bytes:
    """`GS2C_ITEM_KEY = 32` (`sub=2`) -> `netitem.S2CItemKey`: marks `item.g_ItemSendEnd = True`."""
    return frame_gs2c(GS2C_ITEM_KEY, b"\x02")


def build_gs2c_item_pos(id1: int, pos1: int, id2: int = 0, pos2: int = 0, itype: int = 1) -> bytes:
    """`GS2C_ITEM_POS = 36` -> `netitem.S2CItemPos`: moves/swaps items between inventory and equipment slots."""
    payload = struct.pack("<BIBIB", itype & 0xFF, id1 & 0xFFFFFFFF, pos1 & 0xFF, id2 & 0xFFFFFFFF, pos2 & 0xFF)
    return frame_gs2c(GS2C_ITEM_POS, payload)


def build_gs2c_item_info(item_id: int, ext_str: str = "", key: int = 64, itype: int = 0) -> bytes:
    """`GS2C_ITEM_INFO = 162` -> `nethero.S2CItemInfo`: populates item hover tooltip."""
    return frame_gs2c(GS2C_ITEM_INFO, struct.pack("<BII", itype & 0xFF, key & 0xFFFFFFFF, item_id & 0xFFFFFFFF) + encode_big5(ext_str))


def build_gs2c_skills(level: int = 60) -> list[bytes]:
    """
    `GS2C_SKILL_LEVEL = 65` -> `netskill.S2CSkillProcess(netobj)`:
      - `iSub = 1` (`S2CSkill`): `<BB` `1, count` + `count * <HBBBBIIBBBBI` (23B per skill)
      - `iSub = 2` (`S2CMagic`): `<BHBHHIBB` (`2, mtype=2, lv=1, id, nextid=0, exp=100, point=0, aexp=0`)
    """
    pkts: list[bytes] = []
    # Main combat & life skills (`skill.py` / `netskill.py`)
    skills = [
        (1, 2, level, level + 10),   # 劍術
        (2, 2, level, level + 10),   # 刀法
        (3, 2, level, level + 10),   # 槍法
        (7, 3, level, level + 10),   # 道家法術
        (301, 1, level, level + 10), # 強身術
    ]
    buf = bytearray(struct.pack("<BB", 1, len(skills)))
    for sid, stype, slv, slimit in skills:
        buf.extend(struct.pack("<HBBBBIIBBBBI", sid, stype, slv, slimit, slv, 100, 1000, 0, 10, 100, 0, 1000))
    pkts.append(frame_gs2c(GS2C_SKILL_LEVEL, bytes(buf)))

    # Combat magic spells (`mtype = 2`)
    for mid in (101, 102, 103):
        m_pkt = struct.pack("<BHBHHIBB", 2, 2, 1, mid, 0, 1000, 0, 0)
        pkts.append(frame_gs2c(GS2C_SKILL_LEVEL, m_pkt))
    return pkts


STARTER_PETS: list[dict[str, Any]] = [
    {
        "id": 50001,
        "name": "小兔子",
        "shape": 2040,
        "grade": 30,
        "hp": 1280,
        "mp": 650,
        "fp": 100,
        "damage": 520,
        "defense": 410,
        "speed": 360,
        "magdef": 380,
        "str": 95,
        "con": 85,
        "mag": 60,
        "cha": 70,
        "dex": 90,
        "point": 25,
        "skills": [101, 106, 115],
        "birthkey": 1,  # MARK_ISBAOBAO
    },
    {
        "id": 50002,
        "name": "仙獸青雲龍",
        "shape": 4023,
        "grade": 60,
        "hp": 3200,
        "mp": 1800,
        "fp": 100,
        "damage": 1150,
        "defense": 920,
        "speed": 680,
        "magdef": 890,
        "str": 180,
        "con": 160,
        "mag": 170,
        "cha": 150,
        "dex": 165,
        "point": 50,
        "skills": [201, 206, 215, 224],
        "birthkey": 8,  # MARK_ISXIANPET
    },
]


def build_gs2c_summ_add(pet_info: dict[str, Any]) -> bytes:
    """
    `GS2C_SUMM_ADD = 220` -> `netpet.S2CSummAllInfo(netobj)`:
      1. `pid`: 4B LE
      2. `pet.UpdateSummonProp`:
         - `name`: 20B Big5
         - `shape`: 2B LE (`2040` 小兔子, `4023` 仙獸青雲龍)
         - `desc`: `UnpackDesc` (`1B = 0`)
         - `BASE_PROP[4:]` (34 fields = 90 bytes)
         - `m_iGraphStar`(1B), `m_iGraphLock`(1B), `m_iCanJinXiu`(1B)
      3. `UnpackSummonSkill`: `skillNum`(1B), `hfSkillNum`(1B), `skills`(`2B * N`), `tempBindLen`(1B=0)
      4. `UnpackSummonKey`: `key`(2B=0), `birthkey`(1B), `unbindtime`(4B=0)
      5. `iTalentLen`(1B=0) (`limitserver.IsTestGameServer('summontalent') == True`)
      6. `iSaveState`(1B=0), `UnpackSummonEquip`(`1B=0`), `iTraceID`(4B), `iTraceNo`(4B)
    """
    pid = int(pet_info["id"]) & 0xFFFFFFFF
    name_20 = encode_big5(pet_info.get("name", "小兔子"), 20)
    shape = int(pet_info.get("shape", 2040)) & 0xFFFF
    grade = int(pet_info.get("grade", 30)) & 0xFF
    hp = int(pet_info.get("hp", 1200))
    mp = int(pet_info.get("mp", 600))
    fp = int(pet_info.get("fp", 100))
    dmg = int(pet_info.get("damage", 500))
    df = int(pet_info.get("defense", 400))
    spd = int(pet_info.get("speed", 350))
    mdf = int(pet_info.get("magdef", 350))
    p_str = int(pet_info.get("str", 90))
    p_con = int(pet_info.get("con", 80))
    p_mag = int(pet_info.get("mag", 60))
    p_cha = int(pet_info.get("cha", 70))
    p_dex = int(pet_info.get("dex", 85))
    p_pt = int(pet_info.get("point", 25))
    skills = list(pet_info.get("skills", [101, 106]))
    birthkey = int(pet_info.get("birthkey", 1)) & 0xFF

    buf = bytearray()
    buf.extend(struct.pack("<I", pid))
    buf.extend(name_20)
    buf.extend(struct.pack("<HB", shape, 0))  # shape(2B) + UnpackDesc(1B=0)
    # BASE_PROP[4:]:
    # m_Grade(1B), m_HP..m_Magdef(10 x 4B), m_Str..m_Point(6 x 2B), m_Exp..m_Life(4 x 4B),
    # m_bIsColorCompensate(1B), m_iSumScore(2B), m_MoLingGuo..m_MaxShenXian(5 x 1B),
    # Update_Flag..m_Tunshi(4 x 4B), m_FuMo(5B), m_FuMoExt(5B)
    buf.extend(
        struct.pack(
            "<B10I6H4IBH5B4I",
            grade,
            hp, mp, fp, hp, mp, fp,
            dmg, df, spd, mdf,
            p_str, p_con, p_mag, p_cha, p_dex, p_pt,
            10000, 50000, 50000, 65000,
            0, 1850, 0, 0, 10, 0, 10,
            0, 0, 0, 0,
        )
    )
    buf.extend(struct.pack("<BHHBHH", 0, 0, 0, 0, 0, 0))  # m_FuMo(5B), m_FuMoExt(5B)
    buf.extend(struct.pack("<BBB", 1, 0, 0))  # m_iGraphStar, m_iGraphLock, m_iCanJinXiu
    # UnpackSummonSkill
    buf.extend(struct.pack("<BB", len(skills), 0))
    for sk in skills:
        buf.extend(struct.pack("<H", int(sk) & 0xFFFF))
    buf.append(0)  # iTempBindSkillIDList len = 0
    # UnpackSummonKey: key(2B), birthkey(1B), unbindtime(4B)
    buf.extend(struct.pack("<HBI", 0, birthkey, 0))
    # iTalentLen(1B=0), iSaveState(1B=0), equips len(1B=0), iTraceID(4B), iTraceNo(4B)
    buf.extend(struct.pack("<BBBII", 0, 0, 0, pid, 1))
    return frame_gs2c(GS2C_SUMM_ADD, bytes(buf))


def build_gs2c_summ_set_fight(pid: int) -> bytes:
    """`GS2C_SUMM_SET_FIGHT = 50` -> `netpet.S2CSetFight(netobj)` (`pid: 4B`)."""
    return frame_gs2c(GS2C_SUMM_SET_FIGHT, struct.pack("<I", pid & 0xFFFFFFFF))


def build_gs2c_summ_prop_view(pid: int) -> bytes:
    """
    `GS2C_SUMM_PROP_VIEW = 51` -> `netpet.S2CPropView(netobj)`:
      - `pid`: 4B LE
      - `extra_zz`: 2B LE
      - `ADV_PROP` (18 fields = 30 bytes):
          `Ability_Attack..Ability_Speed` (5 x 2B), `Update_Flag`(4B), `Update_Max`(4B),
          `PromoteZZ`(1B), `PromoteMax`(2B), `Resist_Lidi..Resist_Nian` (9 x 1B)
    """
    payload = struct.pack(
        "<IH5HIIBH9b",
        pid & 0xFFFFFFFF,
        50,
        1520, 1480, 1450, 1500, 1490,
        0, 0,
        2, 5,
        10, 10, 10, 10, 10, 10, 10, 10, 10,
    )
    return frame_gs2c(GS2C_SUMM_PROP_VIEW, payload)


def build_gs2c_map_summon(owner_id: int, pet_info: dict[str, Any] | None) -> bytes:
    """
    `GS2C_MAP_SUMMON = 105` -> `netmap.S2CMapSummon(netobj)`:
    Spawns or recalls the player's following summon beast on the map!
    """
    if not pet_info:
        return frame_gs2c(GS2C_MAP_SUMMON, struct.pack("<IBB", owner_id & 0xFFFFFFFF, 0, 0))
    nb = encode_big5(pet_info.get("name", "小兔子"))
    shape = int(pet_info.get("shape", 2040)) & 0xFFFF
    payload = (
        struct.pack("<IBBBHB", owner_id & 0xFFFFFFFF, 1, 1, 0, shape, 0)
        + bytes([len(nb) & 0xFF])
        + nb
        + b"\x00"
    )
    return frame_gs2c(GS2C_MAP_SUMMON, payload)


def build_gs2c_map_change_shape(role_id: int, shape: int, title: str = "夢想開拓者", title_id: int = 101) -> bytes:
    """
    `GS2C_CHANGE_SHAPE = 106` -> `netmap.S2CChangeShape(netobj)`:
      - `iObjID`: 4B LE
      - `iShape`: 2B LE
      - `desc`: `prop.UnpackDesc` (`1B = 0`)
      - `iCountry`: 1B (`(direct << 3) | country`)
      - `iSiblingBadge`: 2B LE
      - `iEmoteType`: 1B
      - `iTitleID`: 2B LE
      - `iEmoteTitleID`: 2B LE
      - `iLen`: 1B + `sTitle` (`iLen` bytes)
      - `iColor`: 1B
      - `iOrgID`: 4B LE
      - `iOrgLevel`: 1B
      - `iNameColorIdx`: 1B
      - `bCanFly`: 1B
      - `iPriorHorseID`: 1B
      - `iTitleGrade`: 1B
      - `bShowPrettyID`: 1B
    """
    tb = encode_big5(title) if title else b""
    payload = (
        struct.pack(
            "<IHBBHBHHB",
            role_id & 0xFFFFFFFF,
            shape & 0xFFFF,
            0,  # prop.UnpackDesc (1B = 0)
            (3 << 3) | 1,  # iDirect=3, iCountry=1
            0,  # iSiblingBadge
            0,  # iEmoteType
            title_id & 0xFFFF,
            0,  # iEmoteTitleID
            len(tb) & 0xFF,
        )
        + tb
        + struct.pack("<BIBBBBBB", 1, 0, 0, 0, 0, 0, 0, 0)
    )
    return frame_gs2c(GS2C_CHANGE_SHAPE, payload)


def build_gs2c_map_scene_m(
    scene: int,
    mapid: int,
    minimapid: int,
    x: int,
    y: int,
    scenename: str,
    has_rainbow: int = 0,
    direct: int = 3,
) -> bytes:
    """
    `GS2C_MAP_SCENE_M = 96` -> `netmap.S2CMapSceneM(netobj)`:
      - `scene = netobj.UnpackInt(2)`
      - `mapid = netobj.UnpackInt(2)`
      - `minimapid = netobj.UnpackInt(2)`
      - `x = netobj.UnpackInt(2)`
      - `y = netobj.UnpackInt(2)`
      - `iLen = netobj.UnpackInt(1)`
      - `scenename = netobj.UnpackString(iLen)`
      - `hasRainbow = netobj.UnpackInt(1)`
      - `iDirect = netobj.UnpackInt(1)`
    """
    name_b = encode_big5(scenename)
    payload = (
        struct.pack(
            "<HHHHHB",
            scene & 0xFFFF,
            mapid & 0xFFFF,
            minimapid & 0xFFFF,
            x & 0xFFFF,
            y & 0xFFFF,
            len(name_b) & 0xFF,
        )
        + name_b
        + struct.pack("<BB", has_rainbow & 0xFF, direct & 0xFF)
    )
    return frame_gs2c(GS2C_MAP_SCENE_M, payload)


def build_gs2c_map_goto_m(x: int, y: int) -> bytes:
    """
    `GS2C_MAP_GOTO_M = 97` -> `netmap.S2CMapGotoM(netobj)`:
      - `x = netobj.UnpackInt(2)`
      - `y = netobj.UnpackInt(2)`
    """
    return frame_gs2c(GS2C_MAP_GOTO_M, struct.pack("<HH", x & 0xFFFF, y & 0xFFFF))


def build_gs2c_map_add_npc(npc: dict[str, Any]) -> bytes:
    """
    `GS2C_MAP_ADD_NPC = 99` -> `netmap.S2CMapAddNpc(netobj)`:
      - `iRealPlayerID` (4B)
      - `iShape` (2B)
      - `x` (2B), `y` (2B)
      - `UnPackPlayerID`: `iPlayerShowID` (4B), `iPrettyID` (4B)
      - `iTitleID` (2B)
      - `iBlock` (1B)
      - `desc` (`UnpackDesc`: 1B count=0)
      - `iDirect` (1B)
      - `iNpcType` (2B)
      - `iCounty` (1B)
      - `iAddonID` (2B)
      - `iLen` (1B) + `sTitle` (Big5) + `iHasTitleEffect` (1B=0)
      - `iHasEffect` (1B=0)
      - `iLen` (2B) + `sName` (Big5)
      - `bClearColorDif` (1B=0)
      - `iBaiTan` (1B=0)
      - `iDelayLoad` (1B=0)
      - `iMode` (1B=0)
    """
    npc_id = int(npc.get("id", 50001)) & 0xFFFFFFFF
    shape = int(npc.get("shape", 3007)) & 0xFFFF
    x = int(npc.get("x", 71)) & 0xFFFF
    y = int(npc.get("y", 49)) & 0xFFFF
    dir_val = int(npc.get("dir", 3)) & 0xFF
    npc_type = int(npc.get("npc_type", shape)) & 0xFFFF
    title_b = encode_big5(npc.get("title", "驛站傳送"))
    name_b = encode_big5(npc.get("name", "清風村傳送人"))

    buf = bytearray()
    buf.extend(struct.pack("<IHHH", npc_id, shape, x, y))
    buf.extend(struct.pack("<II", npc_id, 0))  # UnPackPlayerID
    buf.extend(struct.pack("<HBBBHBH", 0, 0, 0, dir_val, npc_type, 0, 0))
    if title_b:
        buf.append(len(title_b) & 0xFF)
        buf.extend(title_b)
        buf.append(0)  # iHasTitleEffect = 0
    else:
        buf.append(0)
    buf.append(0)  # iHasEffect = 0
    buf.extend(struct.pack("<H", len(name_b) & 0xFFFF))
    buf.extend(name_b)
    buf.extend(struct.pack("<BBBB", 0, 0, 0, 0))  # bClearColorDif, iBaiTan, iDelayLoad, iMode
    return frame_gs2c(GS2C_MAP_ADD_NPC, bytes(buf))


def build_gs2c_npc_chat_ext(
    npc_id: int,
    icon: int,
    name: str,
    msg: str,
    response_id: int = 100,
) -> bytes:
    """
    `GS2C_NPC_CHAT_EXT = 152` -> `netnpc.S2CNpcChatExt(netobj)`:
      - `responseID = netobj.UnpackInt(4)`
      - `ranKey = netobj.UnpackInt(2)` (`icon = ranKey & 32767`)
      - `bAddBuffer = bool(netobj.UnpackInt(1))`
      - `npctype = netobj.UnpackInt(4)`
      - `name = common.UnpackString(netobj)` (1B len + Big5 string)
      - `msg = netobj.UnpackString(0)` (remaining Big5 string; `\\nQ選項` creates clickable buttons)
    """
    name_b = encode_big5(name)
    msg_b = encode_big5(msg)
    payload = (
        struct.pack(
            "<IHBIB",
            response_id & 0xFFFFFFFF,
            icon & 0x7FFF,
            0,
            npc_id & 0xFFFFFFFF,
            len(name_b) & 0xFF,
        )
        + name_b
        + msg_b
    )
    return frame_gs2c(GS2C_NPC_CHAT_EXT, payload)


# ============================================================================
# 3b. 原版 NPC 佈局（entry 2601 `npcposdata` / 2804 / 1799 的导出）
# ============================================================================
# 客户端里「一般 NPC 點他彈哪幾個選單」在服務端，但 NPC 的識別資料是齊的：
#   `notes/npc_dialogue_and_options/out/npc_layout.json`
#   （由 `notes/npc_dialogue_and_options/make_npc_layout.py` 從已入庫 CSV 生成，
#     1,335 條 / 430 場景 / 337 個 npcid）
# mock 用它把每個場景的 NPC 換成**原版站位與名字**，對話正文按客戶端原格式
# （`dlgnpc.ParseWord1`：`P`/`N(icon,name)` 開頭、`Q`/`L`/`M`/`R`/`O` 為選項）重建。
NPC_LAYOUT: dict[str, Any] = {}
NPC_LAYOUT_PATH: Path | None = None


def load_npc_layout(path: Path | None) -> Path | None:
    """載入原版 NPC 佈局；找不到就回 None（此時沿用 mock 內建 NPC 名單）。"""
    global NPC_LAYOUT, NPC_LAYOUT_PATH
    candidates: list[Path] = []
    if path is not None:
        candidates.append(path)
    here = Path(__file__).resolve().parent
    candidates += [
        here / "npc_layout.json",
        here / "notes" / "npc_dialogue_and_options" / "out" / "npc_layout.json",
    ]
    for cand in candidates:
        try:
            data = json.loads(cand.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and isinstance(data.get("scenes"), dict):
            NPC_LAYOUT = data
            NPC_LAYOUT_PATH = cand
            return cand
    return None


def authentic_npcs(scene_id: int, limit: int = 0) -> list[dict[str, Any]]:
    """回傳某場景的**全部**原版 NPC（含站位/名字/分類）；`limit > 0` 時才截斷。

    原版單場景最多 52 個（明月城 1054），所以預設不截斷＝「還原所有 NPC」；
    保留 `limit` 供呼叫方（如自檢或除錯）限縮。"""
    scenes = NPC_LAYOUT.get("scenes")
    if not isinstance(scenes, dict):
        return []
    sc = scenes.get(str(scene_id))
    if not isinstance(sc, dict):
        return []
    out = []
    rows = sc.get("npcs") or []
    if limit and limit > 0:
        rows = rows[:limit]
    for n in rows:
        if not isinstance(n, dict):
            continue
        out.append(
            {
                "id": int(n.get("npcid") or 0) or (70000 + len(out)),
                "shape": int(n.get("icon") or 3007),
                "icon": int(n.get("icon") or 3007),
                "npc_type": int(n.get("type") or 0) or int(n.get("icon") or 3007),
                "x": int(n.get("x") or 0),
                "y": int(n.get("y") or 0),
                "dir": 3,
                "name": str(n.get("name") or "神秘人"),
                "real_name": str(n.get("real_name") or ""),
                "title": str(n.get("real_name") or sc.get("name") or ""),
                "kind": str(n.get("kind") or "default"),
                "shape_key": str(n.get("shape") or ""),
                "authentic": True,
            }
        )
    return out


def is_teleporter(npc: dict[str, Any]) -> bool:
    """傳送人：mock 自帶的、或原版資料裡名字含「傳送/車伕」的 NPC。"""
    if npc.get("teleporter") or npc.get("kind") == "transport":
        return True
    name = str(npc.get("name") or "")
    return any(w in name for w in ("傳送", "車伕", "船伕"))


def map_npc_spawn_list(map_id: int) -> list[dict[str, Any]]:
    """某場景實際下發的 NPC 名單 = 原版站位（entry 2601）+ mock 自己的傳送人。"""
    m = MAPS.get(map_id) or {}
    authentic = authentic_npcs(int(m.get("scene", map_id)))
    out = list(authentic)
    used = {int(n["id"]) for n in out}
    for own in m.get("npcs") or ([m["npc"]] if m.get("npc") else []):
        if authentic and not is_teleporter(own):
            continue
        # 原版 npcid 可能與 mock 自編 id 撞號（例：永澤城傳送人 4405 撞「錢莊」4405），
        # 撞號就給自編 NPC 換一個高位 id，避免客戶端點 A 觸發 B。
        if int(own.get("id", 0)) in used:
            own = dict(own)
            nid = int(own.get("id", 0)) + 100000
            while nid in used:
                nid += 1
            own["id"] = nid
        used.add(int(own["id"]))
        out.append(own)
    return out


def scene_display_name(scene_id: int) -> str:
    scenes = NPC_LAYOUT.get("scenes")
    if isinstance(scenes, dict):
        sc = scenes.get(str(scene_id))
        if isinstance(sc, dict) and sc.get("name"):
            return str(sc["name"])
    if scene_id in MAPS:
        return str(MAPS[scene_id]["name"])
    return f"場景{scene_id}"


def npc_dialogue_text(npc: dict[str, Any]) -> str:
    """按 `dlgnpc.ParseWord1` 的原格式生成對話正文（`P N(icon,name)` + `Q選項`）。"""
    name = str(npc.get("name") or "神秘人")
    real = str(npc.get("real_name") or "")
    kind = str(npc.get("kind") or "default")
    icon = int(npc.get("icon") or 3007)
    if kind == "shop":
        body = f"客官您好，這裡是#Y{name}#n。"
        if real and real != name:
            body = f"客官您好，我是#Y{real}#n，負責{name}的買賣。"
        opts = ["我想買東西", "我想賣東西", "我先看看"]
    elif kind == "storage":
        body = "少俠的貴重物品放在我這兒最安全，倉庫隨時為您開放。"
        opts = ["我要存取物品", "我想擴充倉庫", "沒事了"]
    elif kind == "king":
        body = f"朕乃此地之主#Y{real or name}#n。少俠有事啟奏，無事退朝。"
        opts = ["拜見國王", "我想了解國事", "告退"]
    elif kind == "teacher":
        body = "武學之道，貴在專精。少俠想學哪一門流派的心法招式？"
        opts = ["我想學習技能", "我想重置技能", "我只是看看"]
    elif kind == "guide":
        body = "初入江湖的少俠，按 #GTab#n 開小地圖可以點 NPC 自動尋路；想練級就往城外走。"
        opts = ["哪裡適合練級？", "怎麼操作？", "謝謝"]
    elif kind == "quest":
        body = "此地事務繁忙，少俠若有力氣，不妨幫我跑一趟。"
        opts = ["我想接任務", "我想回報任務", "我再想想"]
    elif kind == "transport":
        body = f"我是#Y{name}#n，可免費送您前往各大主城與練級場景！"
        opts = []  # 傳送人由 _on_npc_look 單獨處理（保留可用的傳送選項）
    else:
        body = npc.get("greeting") or f"這位少俠面生得很，路過{scene_display_name(int(npc.get('scene', 0)))}可要進來坐坐？"
        opts = ["我想聽聽這裡的傳聞", "沒事了"]
    lines = [f"P N({icon},{name})", body]
    lines += [f"Q{opt}" for opt in opts]
    return "\n".join(lines)


def build_gs2c_notify(msg: str, sub: int = 2) -> bytes:
    """
    `GS2C_NOTIFY = 165` -> `netchat.S2CSysNotify(netobj)`:
      - `iSub = netobj.UnpackInt(1)` (1=center prompt, 2=center prompt + chat box)
      - `msg = netobj.UnpackString(0)` (Big5)
    """
    return frame_gs2c(GS2C_NOTIFY, bytes([sub & 0xFF]) + encode_big5(msg))


def build_gs2c_player_chat(ch: int, role_id: int, role_name: str, word: str) -> bytes:
    """
    `GS2C_PLAYER_CHAT = 167` -> `netchat.S2CPlayerChat(netobj)`:
      - `ch = netobj.UnpackInt(1)`
      - `word = netobj.UnpackString(0)` formatted as `#(role_id,role_name)#word`
    """
    formatted = f"#({role_id},{role_name})#{word}"
    return frame_gs2c(GS2C_PLAYER_CHAT, bytes([ch & 0xFF]) + encode_big5(formatted))


def build_gs2c_heartbeat(legacy: bool = False) -> bytes:
    """`GS2C_HEART_BEAT = 63` (or legacy `69`) -> `heartbeatcheck.S2CHeartBeat(netobj)`."""
    op = GS2C_HEART_BEAT_LEGACY if legacy else GS2C_HEART_BEAT
    return frame_gs2c(op, b"")


def build_gs2c_time(legacy: bool = False) -> bytes:
    """
    `GS2C_TIME = 31` (or legacy `12`) -> `mxgw.S2CTime(netobj)` (`t = netobj.UnpackInt(4)`).
    MUST be sent in **centiseconds (100 ticks/sec)**, NEVER Unix seconds!
    """
    op = GS2C_TIME_LEGACY if legacy else GS2C_TIME
    t = monotonic_centiseconds()
    return frame_gs2c(op, struct.pack("<I", t))


# ============================================================================
# 2b. Time Sync Architecture (`mxgw.py` vs `dlgcalendar.py` vs `misc.py`)
# ============================================================================
# 客戶端有兩套完全獨立、單位不同的時間協議，切勿混用：
#
# 1. 反變速齒輪看門狗 (`script/core/mxgw.py` + `mxmain.dll` `C_sys.GetTime` @ `0x4545b0`)：
#    - 請求：`C2GS_REQUEST_TIME = 61` (`0x3D`)
#    - 回應：`GS2C_TIME = 31` (`0x1F`) -> `mxgw.S2CTime(netobj)`
#    - 關鍵逆向實證：`mxmain.dll` 中 `C_sys.GetTime()` (`0x4545b0`) 執行：
#        `eax = timeGetTime() - g_StartTickMs; eax = eax * 10;`
#      返回值單位是 **0.1 毫秒 (10,000 ticks/sec)**！（例如 `dgtbaseopt.py` 中 10 秒冷卻寫作 `+ 100000`）。
#      而 `CreatePyCommand(750 / 1200 / 5400)` 的參數是 **30 FPS 幀數**（即 25 秒、40 秒、180 秒）。
#    - 在 `mxgw.SecondGetResult(t)` 中：
#        `cdt = g_ClientSecondTime / 100 - g_ClientFirstTime / 100`  (單位：**厘秒 centiseconds = 100 ticks/sec**)
#        `sdt = t - g_ServerTime + 550`                              (容差：550 厘秒 = 5.50 秒)
#      若伺服器發送 Unix 秒 (1 tick/sec)，在 40 秒週期內 `cdt ≈ 4000` 而 `sdt ≈ 40 + 550 = 590`，
#      必然觸發 `cdt > sdt`，累計滿 3 次即斷線並報「網絡錯誤(007)，請退出遊戲。」！
#    - 正確做法：`GS2C_TIME = 31` 必須發送自伺服器啟動起算的單調遞增 **厘秒 (100 ticks/sec)**，
#      初始基準為 `10,000`（可連續運行 497 天不溢位 32 位元無符號整數），且**僅在收到 `C2GS_REQUEST_TIME` 時回覆**。
#
# 2. 遊戲內日曆 (`dlgcalendar.py`) 與日程表 (`dlgschedule.py`/`dlgnewschedule.py`/`misc.py`)：
#    - `misc.GetServerCurrentTime()` 計算公式為：
#        `iCurrentTick = C_sys.GetTickCount() / 1000`
#        `return (iCurrentTick - g_RecordTime) + g_ServerTime`
#      客戶端啟動時 `g_ServerTime = int(time.time())`，但 **`g_RecordTime = 0`**！
#      若伺服器未下發觸發 `misc.SetServerTime(tm)` 的封包，`g_RecordTime` 維持為 `0`，
#      導致 `GetServerCurrentTime()` 把 **Windows 開機至今的系統運行秒數 (`GetTickCount()/1000`)**
#      直接加到當前 Unix 時間上，造成本機日程/日曆時間嚴重超前數天至數週！
#    - 正確做法：在角色登入、瞬連重登、以及收到 `C2GS_OPEN_UI = 88 (isub=241)` / `C2GS_SCHEDULE = 82` 時，
#      主動下發：
#        a) `GS2C_OPEN_UI = 89, isub = 241, iTime = unix_seconds` (`netopenui.S2CRefreshServerTime` -> `misc.SetServerTime`)
#        b) `GS2C_PROP_SWITCH = 21, isub = 6` (`nethero.S2CPropSwitch` -> `misc.SetServerTime` + 開服天數/等級上限)
#        c) `GS2C_TIME_SECOND = 192, iTime = unix_seconds` (`dlgcalendar.S2CTime`)
_SERVER_START_MONO = time.monotonic()
_CENTI_LAST_SENT = 10000
_TIME_LAST_SENT = 0


def monotonic_centiseconds() -> int:
    """單調不減的 100Hz 厘秒計數器（供 `GS2C_TIME = 31` / `mxgw.S2CTime` 使用）。"""
    global _CENTI_LAST_SENT
    elapsed_cs = int((time.monotonic() - _SERVER_START_MONO) * 100) + 10000
    now_cs = elapsed_cs & 0x7FFFFFFF
    if now_cs < _CENTI_LAST_SENT:
        now_cs = _CENTI_LAST_SENT
    _CENTI_LAST_SENT = now_cs
    return now_cs


def monotonic_unix_seconds() -> int:
    """標準 Unix 秒，且單調不減（供日曆 `GS2C_TIME_SECOND = 192` 與 `misc.SetServerTime` 使用）。"""
    global _TIME_LAST_SENT
    now = int(time.time()) & 0xFFFFFFFF
    if now < _TIME_LAST_SENT:
        now = _TIME_LAST_SENT
    _TIME_LAST_SENT = now
    return now


def build_gs2c_time_second(unix_ts: int | None = None) -> bytes:
    """`GS2C_TIME_SECOND = 192` -> `dlgcalendar.S2CTime(netobj)` (`g_Time = netobj.UnpackInt(4)`)."""
    t = monotonic_unix_seconds() if unix_ts is None else (int(unix_ts) & 0xFFFFFFFF)
    return frame_gs2c(GS2C_TIME_SECOND, struct.pack("<I", t))


def build_gs2c_refresh_server_time(unix_ts: int | None = None) -> bytes:
    """
    `GS2C_OPEN_UI = 89, isub = 241` -> `netopenui.S2CRefreshServerTime(netobj)`:
    calls `misc.SetServerTime(iTime)` which sets `g_ServerTime = iTime` AND
    `g_RecordTime = C_sys.GetTickCount() / 1000`.
    """
    t = monotonic_unix_seconds() if unix_ts is None else (int(unix_ts) & 0xFFFFFFFF)
    return frame_gs2c(GS2C_OPEN_UI, struct.pack("<BI", 241, t))


def build_gs2c_prop_switch_server_time(
    unix_ts: int | None = None,
    server_state: int = 1,
    open_days: int = 365,
    max_level: int = 165,
    next_days: int = 30,
    next_max_level: int = 170,
    server_name: str = "縮小燈",
) -> bytes:
    """
    `GS2C_PROP_SWITCH = 21, isub = 6` -> `nethero.S2CPropSwitch(netobj)`:
    calls `misc.SetServerTime(tm)` and initializes server open days / max level.
    """
    t = monotonic_unix_seconds() if unix_ts is None else (int(unix_ts) & 0xFFFFFFFF)
    payload = struct.pack(
        "<BIHHHHB16sB",
        6,
        t,
        server_state & 0xFFFF,
        open_days & 0xFFFF,
        max_level & 0xFFFF,
        next_days & 0xFFFF,
        next_max_level & 0xFF,
        encode_big5(server_name, 16),
        1,
    )
    return frame_gs2c(GS2C_PROP_SWITCH, payload)


def build_gs2c_schedule_sync() -> list[bytes]:
    """
    `GS2C_SCHEDULE = 57` (`dlgnewschedule.S2CSchedule` / `dlgschedule.S2CSchedule`):
      - `iSub = 1`: `[1, iCount=0, iDefaultShow=0]` (`<BBB`)
      - `iSub = 2`: `[2, iCount=0]` (`<BB`)
      - `iSub = 4`: `[4, iTotalAct=100, iCurAct=200, iCount=0, iOpenedCount=0]` (`<BHHBB`)
      - `iSub = 7`: `[7, bFirstOpen=0]` (`<BB`)
    """
    return [
        frame_gs2c(GS2C_SCHEDULE, struct.pack("<BBB", 1, 0, 0)),
        frame_gs2c(GS2C_SCHEDULE, struct.pack("<BB", 2, 0)),
        frame_gs2c(GS2C_SCHEDULE, struct.pack("<BHHBB", 4, 100, 200, 0, 0)),
        frame_gs2c(GS2C_SCHEDULE, struct.pack("<BB", 7, 0)),
    ]


def build_gs2c_schedule_week(unix_ts: int | None = None) -> bytes:
    """
    `GS2C_OPEN_UI = 89, isub = 222, iisub = 4` -> `dlgnewschedule.S2CNewSchedule`:
    7-day week preview starting from local time (`iTime:4B` + 7 * `(day_ts:4B, count:1B)`).
    """
    base_ts = monotonic_unix_seconds() if unix_ts is None else (int(unix_ts) & 0xFFFFFFFF)
    buf = bytearray(struct.pack("<BBI", 222, 4, base_ts))
    for day_idx in range(7):
        day_ts = (base_ts + day_idx * 86400) & 0xFFFFFFFF
        buf.extend(struct.pack("<IB", day_ts, 0))
    return frame_gs2c(GS2C_OPEN_UI, bytes(buf))


def build_gs2c_set_rate(isset: int = 1) -> bytes:
    """
    `GS2C_OTHER_ASSISTANT = 11, isub = 42` -> `netcommon.S2CSetRate(netobj)`:
    calls `main.SetRate()` which reads `ratio` and `scale` from `mx.ini`,
    sets `ratio.RATIO` (`1` or `2`), and calls `game.FullScreen()` (`C_sys.WndResize` + `C_sys.SetWndScale`).
    """
    return frame_gs2c(GS2C_OTHER_ASSISTANT, struct.pack("<BB", 42, isset & 0xFF))


def build_gs2c_prop_switch_setting(switch_val: int) -> bytes:
    """
    `GS2C_PROP_SWITCH = 21, isub = 1` -> `nethero.S2CPropSwitch(netobj)`:
    updates `dlgsysopt.g_Settings` and calls `dlgsysopt.ResetSaved()` -> `game.FullScreen()`,
    applying any saved window resolution (`scale`) immediately!
    """
    return frame_gs2c(GS2C_PROP_SWITCH, struct.pack("<BI", 1, switch_val & 0xFFFFFFFF))


def build_gs2c_prop_switch_price(price_val: int) -> bytes:
    """`GS2C_PROP_SWITCH = 21, isub = 9` -> `dlgsysopt.InitPrice(iPrice)`."""
    return frame_gs2c(GS2C_PROP_SWITCH, struct.pack("<BI", 9, price_val & 0xFFFFFFFF))


def build_gs2c_quicklogin_key(login_key: int = 0x514C4B59, itype: int = 1) -> bytes:
    """
    `GS2C_QUICKLOGIN = 12, isub = 1` -> `netquicklogin.S2CLoginKey(netobj)`:
    sets `netquicklogin.g_LoginKey = key` so `RestartQuickLogin` (triggered when saving
    resolution/ratio or UI style in System Settings) can send `C2SRequestQuickLogin(key, pid)`.
    """
    return frame_gs2c(GS2C_QUICKLOGIN, struct.pack("<BIB", 1, login_key & 0xFFFFFFFF, itype & 0xFF))


def build_gs2c_quicklogin_success() -> bytes:
    """
    `GS2C_QUICKLOGIN = 12, isub = 2` -> `netquicklogin.S2CLoginSuccess(netobj)`:
    closes quicklogin dialog and runs `resetcontrol.DoNewResetClear()`.
    Must be sent BEFORE `GS2C_PROP_INIT = 16` during QuickLogin so `DoNewResetClear()`
    does not wipe the newly created `addon` HUD panel.
    """
    return frame_gs2c(GS2C_QUICKLOGIN, b"\x02")


def build_gs2c_newchar_switch_ui(ui_style: int) -> bytes:
    """
    `GS2C_HUODONG_OP = 166`, `'newchar'`, `iSub = 12` (`S2C_SWITCH_UI`) ->
    `netnewcharres.S2CSwitchUIStyle(netobj)`: saves new UI style to `mx.ini` and triggers
    `newoptglobalfunc.ChangeStyleQuickLogin(iRealStyle)`.
    """
    tag = b"newchar"
    payload = bytes([len(tag)]) + tag + struct.pack("<BB", 12, ui_style & 0xFF)
    return frame_gs2c(GS2C_HUODONG_OP, payload)


# ============================================================================
# 4. Persistent Account & Role Store (`mock_accounts.json`)
# ============================================================================


class AccountStore:
    def __init__(self, db_path: Path, default_map_id: int = 1025) -> None:
        self.db_path = db_path
        self.default_map_id = default_map_id if default_map_id in MAPS else 1025
        self.lock = threading.Lock()
        self.data: dict[str, Any] = {"next_role_id": 10002, "accounts": {}}
        self._load()

    def _default_role(self, role_id: int = 10001, name: str = "夢想少俠") -> dict[str, Any]:
        m = MAPS[self.default_map_id]
        return {
            "id": role_id,
            "name": name,
            "icon": 1,
            "shape": 111,
            "color": 0,
            "level": 60,
            "school": 1,
            "liupai": 1001,
            "race": 1,
            "point": 200,
            "cash": 888888,
            "map_id": self.default_map_id,
            "x": m["spawn_x"],
            "y": m["spawn_y"],
            "time": int(time.time()),
        }

    def _migrate_roles(self) -> bool:
        """Auto-upgrades any saved roles in `mock_accounts.json` with invalid `shape` (e.g. `1`) to human shapes (`111..232`)."""
        changed = False
        for acct in self.data.get("accounts", {}).values():
            for r in acct.get("roles", []):
                old_shape = int(r.get("shape", 111))
                new_shape = normalize_player_shape(old_shape)
                if old_shape != new_shape:
                    r["shape"] = new_shape
                    changed = True
                if int(r.get("icon", 0)) <= 0:
                    r["icon"] = SHAPE_DEFAULT_ICON.get(new_shape, 1)
                    changed = True
                if int(r.get("school", 0)) <= 0:
                    r["school"] = 1
                    changed = True
                old_lp = int(r.get("liupai", 0))
                new_lp = normalize_liupai(old_lp, int(r["school"]))
                if old_lp != new_lp:
                    r["liupai"] = new_lp
                    changed = True
        return changed

    def _load(self) -> None:
        if self.db_path.exists():
            try:
                self.data = json.loads(self.db_path.read_text(encoding="utf-8"))
                if self._migrate_roles():
                    self._save()
                    log("[DB] Auto-repaired legacy character shape/liupai in mock_accounts.json -> human shape (111..232)")
                return
            except Exception as exc:
                log(f"[WARN] Failed to load {self.db_path}: {exc}; initializing fresh store.")
        # Seed default account
        self.data = {
            "next_role_id": 10002,
            "accounts": {
                "player01": {
                    "md5_pass": "",
                    "roles": [self._default_role(10001, "夢想少俠")],
                }
            },
        }
        self._save()

    def _save(self) -> None:
        try:
            self.db_path.write_text(
                json.dumps(self.data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            log(f"[WARN] Could not save {self.db_path}: {exc}")

    def get_or_create_account(self, account: str, md5_pass: str) -> list[dict[str, Any]]:
        with self.lock:
            acct = self.data["accounts"].get(account)
            if acct is None:
                role_id = int(self.data.get("next_role_id", 10002))
                self.data["next_role_id"] = role_id + 1
                acct = {
                    "md5_pass": md5_pass,
                    "roles": [self._default_role(role_id, "夢想少俠")],
                }
                self.data["accounts"][account] = acct
                self._save()
                log(f"[DB] Auto-registered new account '{account}' with default role ID={role_id}")
            return list(acct["roles"])

    def add_role(
        self,
        account: str,
        name: str,
        icon: int,
        shape: int,
        color: int,
        major: int,
        liupai: int = 1001,
    ) -> dict[str, Any]:
        with self.lock:
            acct = self.data["accounts"].setdefault(account, {"md5_pass": "", "roles": []})
            role_id = int(self.data.get("next_role_id", 10002))
            self.data["next_role_id"] = role_id + 1
            m = MAPS[self.default_map_id]
            norm_shape = normalize_player_shape(shape)
            norm_major = major if 1 <= major <= 6 else 1
            norm_liupai = normalize_liupai(liupai, norm_major)
            norm_icon = icon if icon > 0 else SHAPE_DEFAULT_ICON.get(norm_shape, 1)
            new_role = {
                "id": role_id,
                "name": name or f"少俠{role_id}",
                "icon": norm_icon,
                "shape": norm_shape,
                "color": color,
                "level": 30,
                "school": norm_major,
                "liupai": norm_liupai,
                "race": 1,
                "point": 100,
                "cash": 888888,
                "map_id": self.default_map_id,
                "x": m["spawn_x"],
                "y": m["spawn_y"],
                "time": int(time.time()),
            }
            # Keep max 3 roles for selectrole UI (3 slots)
            if len(acct["roles"]) >= 3:
                acct["roles"] = acct["roles"][-2:]
            acct["roles"].append(new_role)
            self._save()
            return new_role

    def delete_role(self, account: str, role_id: int) -> bool:
        with self.lock:
            acct = self.data["accounts"].get(account)
            if not acct:
                return False
            before = len(acct["roles"])
            acct["roles"] = [r for r in acct["roles"] if int(r.get("id", 0)) != role_id]
            self._save()
            return len(acct["roles"]) < before

    def get_role(self, account: str, role_id: int) -> dict[str, Any] | None:
        with self.lock:
            acct = self.data["accounts"].get(account)
            if acct:
                for r in acct["roles"]:
                    if int(r.get("id", 0)) == role_id:
                        return r
            # Fallback search across all accounts
            for a in self.data["accounts"].values():
                for r in a.get("roles", []):
                    if int(r.get("id", 0)) == role_id:
                        return r
            return None

    def get_role_and_account(self, role_id: int) -> tuple[str, dict[str, Any]] | None:
        with self.lock:
            for acct_name, acct in self.data.get("accounts", {}).items():
                for r in acct.get("roles", []):
                    if int(r.get("id", 0)) == role_id:
                        return acct_name, r
            return None

    def update_role_pos(self, account: str, role_id: int, map_id: int, x: int, y: int) -> None:
        with self.lock:
            acct = self.data["accounts"].get(account)
            if acct:
                for r in acct["roles"]:
                    if int(r.get("id", 0)) == role_id:
                        r["map_id"] = map_id
                        r["x"] = x
                        r["y"] = y
                        self._save()
                        return
            for a in self.data.get("accounts", {}).values():
                for r in a.get("roles", []):
                    if int(r.get("id", 0)) == role_id:
                        r["map_id"] = map_id
                        r["x"] = x
                        r["y"] = y
                        self._save()
                        return


# ============================================================================
# 5. Per-Connection Session Handler
# ============================================================================


class ClientSession:
    def __init__(
        self,
        conn: socket.socket,
        addr: tuple[str, int],
        store: AccountStore,
        seed: int = 0x13572468,
        server_num: int = 3,
    ) -> None:
        self.conn = conn
        self.addr = addr
        self.store = store
        self.seed = seed
        self.server_num = server_num
        self.account: str = "player01"
        self.active_role: dict[str, Any] | None = None
        self.items: dict[int, dict[str, Any]] = {int(it["id"]): dict(it) for it in STARTER_ITEMS}
        self.pets: dict[int, dict[str, Any]] = {int(p["id"]): dict(p) for p in STARTER_PETS}
        self.recv_buf = bytearray()
        self.hello_verified = False
        self.login_key: int = 0x514C4B59
        self.sys_switch: int = 0
        self.max_price: int = 99999999
        self.split_cmd: int | None = None
        self.split_buf = bytearray()

    def send_raw(self, data: bytes, label: str = "") -> None:
        self.conn.sendall(data)
        if label:
            log(f"[GS2C -> {self.addr[0]}:{self.addr[1]}] {label} ({len(data)}B): {data[:32].hex()}")

    def _read_some(self) -> bool:
        chunk = self.conn.recv(4096)
        if not chunk:
            return False
        self.recv_buf.extend(chunk)
        return True

    def run(self) -> None:
        log(f"[CONNECT] Accepted TCP connection from {self.addr[0]}:{self.addr[1]}")
        try:
            # Step 1: Server speaks FIRST with GS2C_HELLO = 1!
            hello_pkt = build_gs2c_hello(seed=self.seed, server_num=self.server_num, is_cert=0)
            self.send_raw(
                hello_pkt,
                f"GS2C_HELLO(op=1, seed=0x{self.seed:08x}, server_num={self.server_num})",
            )

            while True:
                if not self.recv_buf:
                    if not self._read_some():
                        log(f"[DISCONNECT] {self.addr[0]}:{self.addr[1]} closed connection.")
                        break

                # Check for background probe (`TEST_HELLO = '13245\x00'` from dgwconnecttest.py)
                if self.recv_buf.startswith(b"13245\x00"):
                    log(f"[PROBE] Received dgwconnecttest TEST_HELLO ('13245\\x00') from {self.addr}")
                    del self.recv_buf[:6]
                    continue

                # Check for 12-byte loginhello header ('31323620' / '32323620' / '33323620')
                if len(self.recv_buf) >= 12 and self.recv_buf[:4] in (b"126 ", b"226 ", b"326 "):
                    hdr = bytes(self.recv_buf[:12])
                    log(f"[PROBE] Received 12B loginhello header {hdr!r} from {self.addr}")
                    del self.recv_buf[:12]
                    continue

                # Check for 25-byte NakedSend seed reply from netlogin.S2CHello
                if not self.hello_verified:
                    expected_3b = compute_hello_reply_bytes(self.seed)
                    if len(self.recv_buf) >= 25 and self.recv_buf[:3] == expected_3b:
                        naked = bytes(self.recv_buf[:25])
                        del self.recv_buf[:25]
                        self.hello_verified = True
                        log(
                            f"[C2GS <- {self.addr[0]}:{self.addr[1]}] Verified 25B S2CHello NakedSend reply "
                            f"(seed_3b={expected_3b.hex()}). Client is now opening Login UI (loginin.py)!"
                        )
                        continue
                    # Also tolerate any 25-byte NakedSend where bytes 3..24 are 0x00 or 0x20
                    if len(self.recv_buf) >= 25 and all(b in (0x00, 0x20) for b in self.recv_buf[3:25]):
                        naked = bytes(self.recv_buf[:25])
                        del self.recv_buf[:25]
                        self.hello_verified = True
                        log(
                            f"[C2GS <- {self.addr[0]}:{self.addr[1]}] Accepted 25B NakedSend reply "
                            f"({naked[:4].hex()}...). Client is now opening Login UI!"
                        )
                        continue

                # Parse C2GS framed packet:
                # Native `CPacket::Finalize` (`0x004aae50`) sends:
                #   buf[0] = opcode (1B)
                #   buf[1] = len(fields) + 1 (1B)
                #   buf[2 : 2 + len(fields)] = fields
                #   buf[1 + buf[1]] = 0x00 (1B trailing NUL)
                if len(self.recv_buf) < 2:
                    if not self._read_some():
                        break
                    continue

                b0 = self.recv_buf[0]
                b1 = self.recv_buf[1]
                c2gs_total = 2 + b1

                # Detect unpatched SetSeed stream cipher immediately after S2CHello:
                # If SetSeed was NOT bypassed in data/script.fls (e.g. mock_server.py was not
                # placed in the game root directory, or mx.exe was not restarted after patching),
                # the first packet after NakedSend (C2GS_LOGIN_ACCOUNT_ENTER) arrives encrypted.
                if self.hello_verified and self.account == "default":
                    if b0 not in (
                        C2GS_LOGIN_ACCOUNT_ENTER,
                        C2GS_HEART_BEAT,
                        C2GS_HEART_BEAT_LEGACY,
                        C2GS_REQUEST_TIME,
                        C2GS_REQUEST_TIME_LEGACY,
                        C2GS_TIME,
                        C2GS_PING,
                        C2GS_PING_LEGACY,
                        C2GS_SELECT_SERVER,
                        C2GS_SELECT_SERVER_LEGACY,
                        C2GS_SELSERVER_LEGACY,
                    ):
                        log("=" * 72)
                        log("[ERROR] 檢測到客戶端發送了 SetSeed 加密封包 (導致卡在「正在登錄中....」)！")
                        log("原因：mock_server.py 未放在遊戲根目錄 (mx.exe 所在目錄)，或打補丁後未重啟 mx.exe。")
                        log("解決方法：")
                        log("  1. 先完全關閉遊戲客戶端 (mx.exe)")
                        log("  2. 將 mock_server.py 複製到遊戲根目錄 (與 mx.exe、server.ini 同級)")
                        log("  3. 在遊戲根目錄下運行: python mock_server.py")
                        log("  4. 確認控制台顯示 [OK] Patched SetSeed bypass in .../data/script.fls 後，再啟動 mx.exe")
                        log("=" * 72)
                        return

                while len(self.recv_buf) < c2gs_total:
                    if not self._read_some():
                        return

                # Verify whether this is native CPacket framing `[opcode][len+1][fields][0x00]`
                # or synthetic `[len][opcode][fields]` framing:
                if self.recv_buf[c2gs_total - 1] == 0x00:
                    opcode = b0
                    fields = bytes(self.recv_buf[2 : c2gs_total - 1])
                    del self.recv_buf[:c2gs_total]
                else:
                    # Fallback for `[len][opcode][fields]`
                    pkt_len = b0
                    while len(self.recv_buf) < 1 + pkt_len:
                        if not self._read_some():
                            return
                    opcode = self.recv_buf[1]
                    fields = bytes(self.recv_buf[2 : 1 + pkt_len])
                    del self.recv_buf[: 1 + pkt_len]

                self.handle_c2gs_packet(opcode, fields)

        except ConnectionResetError:
            log(f"[DISCONNECT] {self.addr[0]}:{self.addr[1]} reset connection.")
        except Exception as exc:
            log(f"[ERROR] Session {self.addr[0]}:{self.addr[1]} exception: {exc}")
        finally:
            try:
                self.conn.close()
            except Exception:
                pass

    def handle_c2gs_packet(self, opcode: int, fields: bytes) -> None:
        # 0. Unwrap C2GS_MIXPACKET = 151 (`script/net.py` `WrapPacketSend` for `C2GS_MAP_MOVE` / `C2GS_NPC_LOOK`)
        if opcode == C2GS_MIXPACKET:
            if len(fields) >= 8:
                role_id = struct.unpack_from("<I", fields, 0)[0]
                flag = fields[4]
                if flag == 3:
                    inner_cmd = fields[5]
                    inner_size = struct.unpack_from("<H", fields, 6)[0]
                    inner_fields = fields[8 : 8 + inner_size]
                    log(
                        f"[C2GS <- {self.addr[1]}] C2GS_MIXPACKET (op=151, role={role_id}, "
                        f"flag=3 -> inner_cmd={inner_cmd}, size={inner_size}B)"
                    )
                    self.handle_c2gs_packet(inner_cmd, inner_fields)
                    return
                if flag == 0 and len(fields) >= 9:
                    inner_cmd = fields[5]
                    inner_size = struct.unpack_from("<H", fields, 6)[0]
                    chunk_len = fields[8]
                    inner_fields = fields[9 : 9 + min(inner_size, chunk_len)]
                    log(
                        f"[C2GS <- {self.addr[1]}] C2GS_MIXPACKET (op=151, role={role_id}, "
                        f"flag=0 -> inner_cmd={inner_cmd}, size={inner_size}B)"
                    )
                    self.handle_c2gs_packet(inner_cmd, inner_fields)
                    return
            return

        # 1. Heartbeat (`C2GS_HEART_BEAT = 63` in `script.fls`, `109` in `data.fls`)
        if opcode in (C2GS_HEART_BEAT, C2GS_HEART_BEAT_LEGACY):
            is_legacy = opcode == C2GS_HEART_BEAT_LEGACY
            log(f"[C2GS <- {self.addr[1]}] C2GS_HEART_BEAT (op={opcode})")
            self.send_raw(
                build_gs2c_heartbeat(legacy=is_legacy),
                f"GS2C_HEART_BEAT(op={GS2C_HEART_BEAT_LEGACY if is_legacy else GS2C_HEART_BEAT})",
            )
            return

        # 2. Time Sync (`C2GS_REQUEST_TIME = 61` / `C2GS_TIME = 31` in `script.fls`, `15` in `data.fls`)
        #    Note: `mxgw` and `dlgcalendar.C2SGetServerTime()` both send `C2GS_REQUEST_TIME = 61`.
        #    Reply with `GS2C_TIME = 31` (100Hz centiseconds for `mxgw`) AND `GS2C_TIME_SECOND = 192`
        #    (Unix seconds for `dlgcalendar.S2CTime`). Both client handlers are guarded.
        if opcode in (C2GS_REQUEST_TIME, C2GS_TIME, C2GS_REQUEST_TIME_LEGACY):
            is_legacy = opcode == C2GS_REQUEST_TIME_LEGACY
            log(f"[C2GS <- {self.addr[1]}] C2GS_REQUEST_TIME (op={opcode})")
            self.send_raw(
                build_gs2c_time(legacy=is_legacy),
                f"GS2C_TIME(op={GS2C_TIME_LEGACY if is_legacy else GS2C_TIME}, unit=centiseconds)",
            )
            if not is_legacy:
                self.send_raw(
                    build_gs2c_time_second(),
                    f"GS2C_TIME_SECOND(op={GS2C_TIME_SECOND}, unit=seconds)",
                )
            return

        # 3. System Settings Switch (`C2GS_PLAYER_SYSSWITCH = 21` -> `nethero.C2SSaveSetting` / `C2SSavePrice` / `C2SSaveSystemData`)
        if opcode == C2GS_PLAYER_SYSSWITCH:
            self._on_player_sysswitch(fields)
            return

        # 4. Open UI / Refresh Server Time (`C2GS_OPEN_UI = 88` or legacy `60`)
        if opcode in (C2GS_OPEN_UI, C2GS_OPEN_UI_LEGACY):
            isub = fields[0] if fields else 0
            if isub == 241:
                # `nethero.C2SRefreshServerTime()` -> reply with `GS2C_OPEN_UI = 89, isub = 241`
                log(f"[C2GS <- {self.addr[1]}] C2GS_OPEN_UI (op={opcode}, isub=241 C2SRefreshServerTime)")
                self.send_raw(
                    build_gs2c_refresh_server_time(),
                    "GS2C_OPEN_UI(op=89, isub=241 S2CRefreshServerTime)",
                )
                self.send_raw(
                    build_gs2c_time_second(),
                    "GS2C_TIME_SECOND(op=192, S2CTime)",
                )
            return

        # 5. In-Game Calendar & Schedule (`C2GS_SCHEDULE = 82` or legacy `69`)
        if opcode in (C2GS_SCHEDULE, C2GS_SCHEDULE_LEGACY):
            isub = fields[0] if fields else 1
            log(f"[C2GS <- {self.addr[1]}] C2GS_SCHEDULE (op={opcode}, isub={isub})")
            self.send_raw(
                build_gs2c_refresh_server_time(),
                "GS2C_OPEN_UI(op=89, isub=241 S2CRefreshServerTime)",
            )
            self.send_raw(
                build_gs2c_time_second(),
                "GS2C_TIME_SECOND(op=192, S2CTime)",
            )
            if isub == 1:
                for pkt in build_gs2c_schedule_sync():
                    self.send_raw(pkt, "GS2C_SCHEDULE(op=57)")
            elif isub == 2:
                self.send_raw(
                    build_gs2c_schedule_week(),
                    "GS2C_OPEN_UI(op=89, isub=222, iisub=4 ScheduleWeek)",
                )
            return

        # 6. HuoDong / UI Style Switch (`C2GS_HUODONG = 90` -> `'newchar'` `C2SSwitchUIStyle`)
        if opcode == C2GS_HUODONG:
            self._on_huodong(fields)
            return

        # 7. QuickLogin (`C2GS_QUICKLOGIN = 13` -> resolution/ratio/UI-style switch & reconnect)
        if opcode == C2GS_QUICKLOGIN:
            self._on_quicklogin(fields)
            return

        # 8. Ping & Quiet In-Map State Packets
        if opcode in (
            C2GS_PING,
            C2GS_PING_LEGACY,
            C2GS_PLAYER_SWITCH,
            C2GS_TASK_GET,
            C2GS_TASK,
            C2GS_ANSWERHELLO,
            # NOTE: `C2GS_CHECKWG` deliberately NOT here - it shares 152 with
            # `C2GS_PLAYER_UPGRADE` and is disambiguated below by payload length.
            C2GS_PLAYER_CMD,
        ):
            return

        # 9. `C2GS_GAME_PUBLIC = 209` (`script.fls`) or `250` (`data.fls`)
        if opcode in (C2GS_GAME_PUBLIC, C2GS_GAME_PUBLIC_LEGACY):
            sub = fields[0] if fields else 0
            log(
                f"[C2GS <- {self.addr[1]}] C2GS_GAME_PUBLIC (op={opcode}, sub={sub}, "
                f"len={len(fields)}B)"
            )
            # Sub 5 = C2GS_SUB_SPLIT (`netpublic.SplitPacketSend`, e.g. `SaveHideGamehotkey` -> `C2SSaveSystemData`)
            if sub == 5 and len(fields) >= 3:
                flag = fields[1]
                if flag == 0 and len(fields) >= 4:
                    self.split_cmd = fields[2]
                    chunk_len = fields[3]
                    self.split_buf = bytearray(fields[4 : 4 + chunk_len])
                elif flag in (1, 2):
                    chunk_len = fields[2]
                    self.split_buf.extend(fields[3 : 3 + chunk_len])
                    if flag == 2 and self.split_cmd is not None:
                        reassembled_cmd = self.split_cmd
                        reassembled_fields = bytes(self.split_buf)
                        self.split_cmd = None
                        self.split_buf.clear()
                        log(
                            f"[C2GS <- {self.addr[1]}] Reassembled C2GS_SUB_SPLIT -> "
                            f"cmd={reassembled_cmd}, len={len(reassembled_fields)}B"
                        )
                        self.handle_c2gs_packet(reassembled_cmd, reassembled_fields)
                return
            # Sub 52 = C2GS_SUB_GM_NEW (`C2SPlayerWizard`)
            if sub == 52 and len(fields) >= 3:
                jlen = struct.unpack_from("<H", fields, 1)[0]
                cmd_bytes = fields[3 + jlen :]
                cmd_str = decode_big5(cmd_bytes)
                log(f"[GM CMD] Player executed wizard command: {cmd_str!r}")
                self._handle_chat_or_gm_command(cmd_str)
            return

        # 5. Login / Role Creation / Role Selection
        if opcode == C2GS_LOGIN_ACCOUNT_ENTER:
            self._on_login_account_enter(fields)
            return

        if opcode == C2GS_LOGIN_PLAYER_ADD:
            self._on_login_player_add(fields)
            return

        if opcode == C2GS_LOGIN_PLAYER_DEL:
            self._on_login_player_del(fields)
            return

        if opcode == C2GS_LOGIN_PLAYER_ENTER:
            self._on_login_player_enter(fields)
            return

        if opcode in (C2GS_SELECT_SERVER, C2GS_SELECT_SERVER_LEGACY, C2GS_SELSERVER_LEGACY):
            log(f"[C2GS <- {self.addr[1]}] C2GS_SELECT_SERVER (op={opcode})")
            reply_op = GS2C_SELSERVER if opcode == C2GS_SELECT_SERVER else GS2C_SELSERVER_LEGACY
            pkt = frame_gs2c(reply_op, struct.pack("<BIB", 1, self.server_num, 1))
            self.send_raw(pkt, f"GS2C_SELSERVER(op={reply_op})")
            return

        # 6. Map Movement (`C2GS_MAP_MOVE = 54`)
        if opcode == C2GS_MAP_MOVE:
            if len(fields) >= 4:
                x, y = struct.unpack_from("<HH", fields, 0)
                trace_steps = fields[5 : 5 + fields[4]] if len(fields) >= 5 else b""
                dest_x, dest_y = x, y
                for step_dir in trace_steps:
                    if 1 <= step_dir <= 8:
                        dx, dy = MOVE_STEP_OFFSETS[step_dir - 1]
                        dest_x += dx
                        dest_y += dy
                log(
                    f"[C2GS <- {self.addr[1]}] C2GS_MAP_MOVE (op=54): "
                    f"start=({x},{y}) -> dest=({dest_x},{dest_y}) (steps={len(trace_steps)})"
                )
                if self.active_role:
                    cur_map_id = int(self.active_role.get("map_id", 1025))
                    self.active_role["x"] = dest_x
                    self.active_role["y"] = dest_y
                    self.store.update_role_pos(
                        self.account,
                        int(self.active_role["id"]),
                        cur_map_id,
                        dest_x,
                        dest_y,
                    )
                    # Check if player stepped onto a map portal exit
                    m = MAPS.get(cur_map_id)
                    if m:
                        for portal in m.get("portals", []):
                            px, py = int(portal["x"]), int(portal["y"])
                            rad = int(portal.get("radius", 4))
                            if abs(dest_x - px) <= rad and abs(dest_y - py) <= rad:
                                t_map = int(portal["target_map"])
                                tx, ty = int(portal["target_x"]), int(portal["target_y"])
                                log(
                                    f"[PORTAL] Player stepped on portal ({px},{py}) -> "
                                    f"teleporting to {t_map} ({tx},{ty})"
                                )
                                self.enter_map(t_map, tx, ty)
                                self.send_raw(
                                    build_gs2c_notify(
                                        f"#G已通過傳送陣抵達【{MAPS[t_map]['name']}】({t_map})！#n",
                                        sub=2,
                                    ),
                                    "GS2C_NOTIFY",
                                )
                                break
            return

        # 7. NPC Click / Dialogue (`C2GS_NPC_LOOK = 96`, `C2GS_NPC_RBCLICK = 108`, or legacy `55`)
        if opcode in (C2GS_NPC_LOOK, C2GS_NPC_RBCLICK, C2GS_NPC_LOOK_LEGACY):
            # Note: In `script.fls`, opcode 55 is `C2GS_SYN_DIREMOTE` (`dir:1B, emote:1B` = 2 bytes),
            # whereas legacy `C2GS_NPC_LOOK` is `npcid:4B` (4 bytes).
            if opcode == C2GS_SYN_DIREMOTE and len(fields) < 4:
                return
            if len(fields) >= 4:
                npc_id = struct.unpack_from("<I", fields, 0)[0]
                log(f"[C2GS <- {self.addr[1]}] C2GS_NPC_LOOK (op={opcode}): npc_id={npc_id}")
                self._on_npc_look(npc_id)
            return

        # 8. NPC Dialogue Option Selection (`C2GS_NPC_ANSWER = 98` or legacy `56`)
        if opcode in (C2GS_NPC_ANSWER, C2GS_NPC_ANSWER_LEGACY, C2GS_NPC_COMMAND, C2GS_NPC_INPUT, C2GS_NPC_INPUT_LEGACY):
            if len(fields) >= 2:
                # Note: `netnpc.C2SNpcAnswer(iAnswer, responseID)` in `script.fls` (`idx=731`) sends:
                #   responseID: 1B (`netobj.PacketAddI(responseID, 1)`)
                #   num (iAnswer): 1B (`netobj.PacketAddI(num, 1)`)
                # whereas in `data.fls` it sent `iAnswer:4B, responseID:4B` (8 bytes)!
                if len(fields) >= 8:
                    choice, resp_id = struct.unpack_from("<II", fields, 0)
                else:
                    resp_id, choice = fields[0], fields[1]
                log(
                    f"[C2GS <- {self.addr[1]}] C2GS_NPC_ANSWER (op={opcode}): "
                    f"choice={choice}, responseID={resp_id}"
                )
                self._on_npc_answer(choice, resp_id)
            return

        # 9. Player Chat (`C2GS_PLAYER_CHAT = 149` in `script.fls` or `123` in `data.fls`)
        if opcode in (C2GS_PLAYER_CHAT, C2GS_PLAYER_CHAT_LEGACY):
            if len(fields) >= 1:
                ch = fields[0]
                # In `script.fls` (`idx=3257` `script/netchat.py`), `C2SPlayerChat` packs:
                #   ch: 1B, len(word): 2B LE, word: N bytes
                if opcode == C2GS_PLAYER_CHAT and len(fields) >= 3:
                    wlen = struct.unpack_from("<H", fields, 1)[0]
                    word = decode_big5(fields[3 : 3 + wlen])
                else:
                    word = decode_big5(fields[1:])
                log(f"[C2GS <- {self.addr[1]}] C2GS_PLAYER_CHAT (op={opcode}, ch={ch}): {word!r}")
                if word.startswith("/") or word.startswith("$"):
                    self._handle_chat_or_gm_command(word)
                elif self.active_role:
                    chat_pkt = build_gs2c_player_chat(
                        ch=ch,
                        role_id=int(self.active_role["id"]),
                        role_name=str(self.active_role["name"]),
                        word=word,
                    )
                    self.send_raw(chat_pkt, f"GS2C_PLAYER_CHAT(op=167, word={word!r})")
            return

        if opcode == C2GS_LOGIN_QUIT:
            log(f"[C2GS <- {self.addr[1]}] C2GS_LOGIN_QUIT (op=4)")
            return

        # 10. Character Attribute Point Allocation (`C2GS_PLAYER_ADJUSTPOINT = 16`)
        if opcode == C2GS_PLAYER_ADJUSTPOINT:
            self._on_player_adjustpoint(fields)
            return

        # 11. Character Level-Up & Stat Allocation (`C2GS_PLAYER_UPGRADE = 152` in v2.27.2;
        #     the legacy 17 is accepted too so older builds keep working).
        #     `nethero.C2SUpgrade` sends an EMPTY payload, which distinguishes it from
        #     `C2GS_CHECKWG`, the other client constant carrying 152.
        if opcode == C2GS_PLAYER_UPGRADE_LEGACY or (opcode == C2GS_PLAYER_UPGRADE and not fields):
            self._on_player_upgrade()
            return
        if opcode == C2GS_CHECKWG:  # op=152 with a payload: anti-cheat ping, stay silent
            log(f"[C2GS <- {self.addr[1]}] C2GS_CHECKWG (op=152, len={len(fields)}B) ignored")
            return

        # 12. Assistant Operations (`C2GS_ASSISTANT_OP = 192` -> upgrade check, auto-point, etc.)
        if opcode == C2GS_ASSISTANT_OP:
            sub = fields[0] if fields else 0
            log(f"[C2GS <- {self.addr[1]}] C2GS_ASSISTANT_OP (op=192, sub={sub})")
            if sub == 21:
                # CanUpgrade response (`GS2C_OTHER_ASSISTANT = 11`, `sub=37`, `state=1, exp=0, flag=0, cash=0`)
                self.send_raw(
                    frame_gs2c(GS2C_OTHER_ASSISTANT, struct.pack("<BBIBI", 37, 1, 0, 0, 0)),
                    "GS2C_OTHER_ASSISTANT(sub=37, CanUpgrade=1)",
                )
            elif sub in (73, 110):
                self._on_player_upgrade()
            return

        # 13. Open New UI (`C2GS_OPEN_UI_NEW = 230` -> `查看屬性 / 屬性總覽` `iMain=162, sub=49, iType=1..7`)
        if opcode == C2GS_OPEN_UI_NEW:
            if len(fields) >= 4:
                i_main, i_sub, i_type = struct.unpack_from("<HBB", fields, 0)
                log(f"[C2GS <- {self.addr[1]}] C2GS_OPEN_UI_NEW (op=230, main={i_main}, sub={i_sub}, type={i_type})")
                if i_main == 162 and i_sub == 49:
                    self.send_raw(
                        build_gs2c_open_ui_new_attr(i_type),
                        f"GS2C_OPEN_UI_NEW(op=234, main=8, sub={i_type})",
                    )
            return

        # 14. Character Titles (`C2GS_TITLE = 67` -> `稱謂` dialog)
        if opcode == C2GS_TITLE:
            self._on_title_op(fields)
            return

        # 15. Inventory & Equipment Operations (`C2GS_ITEM_OP = 32`, `C2GS_GET_ITEM_INFO_EXT = 156`, `C2GS_GET_ITEM_INFO = 145`)
        if opcode == C2GS_ITEM_OP:
            self._on_item_op(fields)
            return

        if opcode in (C2GS_GET_ITEM_INFO_EXT, C2GS_GET_ITEM_INFO):
            if len(fields) >= 4:
                item_id = struct.unpack_from("<I", fields, 0)[0]
                itype = fields[4] if len(fields) >= 5 else 0
                it = self.items.get(item_id)
                ext_str = it.get("ext", "") if it else ""
                self.send_raw(
                    build_gs2c_item_info(item_id, ext_str=ext_str, key=64, itype=itype),
                    f"GS2C_ITEM_INFO(op=162, id={item_id})",
                )
            return

        # 16. Summon Beast (召喚獸) Operations (`128..134`)
        if opcode == C2GS_SUMMON_PROPVIEW and len(fields) >= 4:
            pid = struct.unpack_from("<I", fields, 0)[0]
            log(f"[C2GS <- {self.addr[1]}] C2GS_SUMMON_PROPVIEW (op=129, pid={pid})")
            self.send_raw(build_gs2c_summ_prop_view(pid), f"GS2C_SUMM_PROP_VIEW(op=51, pid={pid})")
            return

        if opcode == C2GS_SUMMON_FIGHT and len(fields) >= 4:
            pid = struct.unpack_from("<I", fields, 0)[0]
            log(f"[C2GS <- {self.addr[1]}] C2GS_SUMMON_FIGHT (op=131, pid={pid})")
            self.send_raw(build_gs2c_summ_set_fight(pid), f"GS2C_SUMM_SET_FIGHT(op=50, pid={pid})")
            return

        if opcode == C2GS_SUMMON_SHOW and len(fields) >= 4:
            pid = struct.unpack_from("<I", fields, 0)[0]
            log(f"[C2GS <- {self.addr[1]}] C2GS_SUMMON_SHOW (op=132, pid={pid})")
            p_info = self.pets.get(pid) or STARTER_PETS[0]
            owner_id = int(self.active_role["id"]) if self.active_role else 10001
            self.send_raw(build_gs2c_map_summon(owner_id, p_info), f"GS2C_MAP_SUMMON(op=105, show pid={pid})")
            self.send_raw(build_gs2c_notify(f"#G召喚獸【{p_info['name']}】已出現在您身旁跟隨！#n", sub=1), "GS2C_NOTIFY")
            return

        if opcode == C2GS_SUMMON_HIDE and len(fields) >= 4:
            pid = struct.unpack_from("<I", fields, 0)[0]
            log(f"[C2GS <- {self.addr[1]}] C2GS_SUMMON_HIDE (op=133, pid={pid})")
            owner_id = int(self.active_role["id"]) if self.active_role else 10001
            self.send_raw(build_gs2c_map_summon(owner_id, None), f"GS2C_MAP_SUMMON(op=105, hide pid={pid})")
            return

        if opcode == C2GS_SUMMON_RENAME and len(fields) >= 5:
            pid = struct.unpack_from("<I", fields, 0)[0]
            new_name = decode_big5(fields[4:]).strip()
            if new_name and pid in self.pets:
                self.pets[pid]["name"] = new_name
                self.send_raw(build_gs2c_summ_add(self.pets[pid]), f"GS2C_SUMM_ADD(op=220, rename={new_name!r})")
            return

        if opcode == C2GS_SUMMON_POINT and len(fields) >= 5:
            sub = fields[0]
            pid = struct.unpack_from("<I", fields, 1)[0]
            if sub == 1 and len(fields) >= 15 and pid in self.pets:
                a0, a1, a2, a3, a4 = struct.unpack_from("<5H", fields, 5)
                p = self.pets[pid]
                spent = a0 + a1 + a2 + a3 + a4
                if spent <= int(p.get("point", 0)):
                    p["str"] = int(p.get("str", 90)) + a0
                    p["mag"] = int(p.get("mag", 60)) + a1
                    p["con"] = int(p.get("con", 80)) + a2
                    p["dex"] = int(p.get("dex", 85)) + a3
                    p["cha"] = int(p.get("cha", 70)) + a4
                    p["point"] = int(p.get("point", 0)) - spent
                    p["damage"] = int(p.get("damage", 500)) + a0 * 4
                    p["defense"] = int(p.get("defense", 400)) + a2 * 3
                    p["speed"] = int(p.get("speed", 350)) + a3 * 3
                    p["magdef"] = int(p.get("magdef", 350)) + a1 * 3
                    p["hp"] = int(p.get("hp", 1200)) + a2 * 12
                    p["mp"] = int(p.get("mp", 600)) + a1 * 8
                    self.send_raw(build_gs2c_summ_add(p), f"GS2C_SUMM_ADD(op=220, pid={pid} addpoint)")
            return

        log(
            f"[C2GS <- {self.addr[1]}] Unhandled opcode={opcode} (0x{opcode:02x}), "
            f"fields({len(fields)}B)={fields[:32].hex()}"
        )

    # ------------------------------------------------------------------------
    # Stage 2: Account & Password Login (`C2GS_LOGIN_ACCOUNT_ENTER = 1`)
    # ------------------------------------------------------------------------
    def _on_login_account_enter(self, fields: bytes) -> None:
        """
        Supports both `data/script.fls` (`idx=4082`, real `mx.exe` client `netlogin.C2SLoginIn`)
        and `data/data.fls` (`netlogin.C2SLoginIn`):
          - `data/script.fls` (`idx=4082`):
              `iScriptV1`: 1B (`0` or `0x80`)
              `CLIENT_VERSION[1]`: 1B (`2`)
              `CLIENT_VERSION[2]`: 2B LE (`27`)
              `name`: 32B
              `pwd`: 20B
              `C_sys.GetVersion()`: 4B
              `update.ini Version`: 4B
              `localip`: 4B
              `adsid`: 8B
              `len(tgId)`: 1B + `tgId`
              `driveid`: 4B
              `mac`: len(mac)B
          - `data/data.fls` (legacy/bot script):
              `sub`: 1B (`0`) + `account`: 40B + `md5_pass`: 32B + ...
        """
        if len(fields) >= 56 and (fields[1:4] == b"\x02\x1b\x00" or len(fields) < 150):
            v1 = fields[0]
            v2 = fields[1]
            v3 = struct.unpack_from("<H", fields, 2)[0]
            acct_raw = fields[4:36]
            pwd_raw = fields[36:56]
            account = decode_big5(acct_raw).strip() or "player01"
            md5_pass = decode_big5(pwd_raw).strip()
            log(
                f"[LOGIN] C2GS_LOGIN_ACCOUNT_ENTER (op=1, script.fls v={v1 & 0x7F}.{v2}.{v3}): "
                f"account={account!r}, pwd={md5_pass!r}"
            )
        else:
            sub = fields[0] if len(fields) >= 1 else 0
            acct_raw = fields[1:41] if len(fields) >= 41 else fields[1:]
            pwd_raw = fields[41:73] if len(fields) >= 73 else b""
            mac_raw = fields[100:106] if len(fields) >= 106 else b""
            hw_enc = fields[107:167] if len(fields) >= 167 else b""

            account = decode_big5(acct_raw).strip() or "player01"
            md5_pass = decode_big5(pwd_raw).strip()
            mac_hex = mac_raw.hex(":") if mac_raw else "n/a"
            hw_dec = simple_decrypt(hw_enc) if hw_enc else b""
            cpuid = decode_big5(hw_dec[20:40]) if len(hw_dec) >= 40 else ""
            log(
                f"[LOGIN] C2GS_LOGIN_ACCOUNT_ENTER (op=1, sub={sub}): "
                f"account={account!r}, md5={md5_pass!r}, mac={mac_hex}, cpuid={cpuid!r}"
            )

        self.account = account
        roles = self.store.get_or_create_account(account, md5_pass)

        # Send GS2C_LOGIN_ACCOUNT_INFO = 15
        acct_pkt = build_gs2c_login_account_info(role_count=len(roles), vid=1)
        self.send_raw(acct_pkt, f"GS2C_LOGIN_ACCOUNT_INFO(op=15, count={len(roles)}, vid=1)")

        # Send GS2C_LOGIN_PLAYER_INFO = 3 for each role
        for r in roles:
            r_pkt = build_gs2c_login_player_info(r)
            self.send_raw(
                r_pkt,
                f"GS2C_LOGIN_PLAYER_INFO(op=3, id={r['id']}, name={r['name']!r}, lv={r['level']})",
            )

    # ------------------------------------------------------------------------
    # Stage 3A: Character Creation (`C2GS_LOGIN_PLAYER_ADD = 3`)
    # ------------------------------------------------------------------------
    def _on_login_player_add(self, fields: bytes) -> None:
        """
        Unpacks `netlogin.C2SCreateRole`:
          - `sub`: 1B (1)
          - `name`: 20B (Big5)
          - `icon`: 1B
          - `shape`: 2B LE
          - `color`: 2B LE
          - `major`: 1B (0=戰士, 1=法師, 2=術士)
          - `randflag`: 1B
          - `liupai`: 2B LE
        Total = 30 bytes.
        """
        if len(fields) < 30:
            log(f"[WARN] C2GS_LOGIN_PLAYER_ADD fields too short ({len(fields)}B)")
            return

        sub = fields[0]
        name = decode_big5(fields[1:21]).strip() or "新創少俠"
        icon, shape, color, major, randflag, liupai = struct.unpack_from("<BHHBBH", fields, 21)
        log(
            f"[CREATE_ROLE] C2GS_LOGIN_PLAYER_ADD (op=3, sub={sub}): "
            f"name={name!r}, icon={icon}, shape={shape}, color={color}, "
            f"major={major}, randflag={randflag}, liupai={liupai}"
        )

        new_role = self.store.add_role(
            account=self.account,
            name=name,
            icon=icon,
            shape=shape,
            color=color,
            major=major,
            liupai=liupai,
        )

        # 1. Send GS2C_LOGIN_PLAYER_INFO = 3 so `netlogin.g_RoleInfo` includes the new role
        info_pkt = build_gs2c_login_player_info(new_role)
        self.send_raw(
            info_pkt,
            f"GS2C_LOGIN_PLAYER_INFO(op=3, new_id={new_role['id']}, name={new_role['name']!r})",
        )

        # 2. Send GS2C_LOGIN_PLAYER_ADD = 6 so `S2CLoginPlayerAdd` shows success & enters game
        add_pkt = build_gs2c_login_player_add()
        self.send_raw(add_pkt, "GS2C_LOGIN_PLAYER_ADD(op=6)")

    # ------------------------------------------------------------------------
    # Stage 3B: Character Deletion (`C2GS_LOGIN_PLAYER_DEL = 7`)
    # ------------------------------------------------------------------------
    def _on_login_player_del(self, fields: bytes) -> None:
        if len(fields) < 4:
            return
        role_id = struct.unpack_from("<I", fields, 0)[0]
        log(f"[DEL_ROLE] C2GS_LOGIN_PLAYER_DEL (op=7): role_id={role_id}")
        self.store.delete_role(self.account, role_id)
        self.send_raw(
            build_gs2c_login_player_del(role_id),
            f"GS2C_LOGIN_PLAYER_DEL(op=10, role_id={role_id})",
        )

    # ------------------------------------------------------------------------
    # Stage 4: Character Selection & Entering Map (`C2GS_LOGIN_PLAYER_ENTER = 2`)
    # ------------------------------------------------------------------------
    def _on_login_player_enter(self, fields: bytes) -> None:
        if len(fields) < 4:
            return
        role_id = struct.unpack_from("<I", fields, 0)[0]
        log(f"[ENTER_GAME] C2GS_LOGIN_PLAYER_ENTER (op=2): role_id={role_id}")

        role = self.store.get_role(self.account, role_id)
        if role is None:
            roles = self.store.get_or_create_account(self.account, "")
            role = roles[0]
            role["id"] = role_id
        self._enter_role_world(role, send_welcome=True)

    def _enter_role_world(self, role: dict[str, Any], send_welcome: bool = True) -> None:
        self.active_role = role
        self.sys_switch = int(role.get("sys_switch", self.sys_switch))
        self.max_price = int(role.get("max_price", self.max_price))

        # 1. Send GS2C_PROP_INIT = 16 (initializes hero.g_Prop and switches gamectrl to GAMING)
        prop_pkt = build_gs2c_prop_init(role)
        self.send_raw(
            prop_pkt,
            f"GS2C_PROP_INIT(op=16, id={role['id']}, name={role['name']!r}, shape={role.get('shape')}, lv={role['level']})",
        )

        # 2. Send Starter Equipment (`pos=1..9`) & Inventory Items (`pos=20..59`) + ItemSendEnd
        for it in self.items.values():
            self.send_raw(build_gs2c_item_add(it), f"GS2C_ITEM_ADD(op=33, id={it['id']}, pos={it['pos']}, name={it['name']!r})")
        self.send_raw(build_gs2c_item_key_end(), "GS2C_ITEM_KEY(op=32, sub=2 ItemSendEnd)")

        # 3. Send Starter Skills & Combat Magic (`GS2C_SKILL_LEVEL = 65`)
        for sk_pkt in build_gs2c_skills(int(role.get("level", 60))):
            self.send_raw(sk_pkt, "GS2C_SKILL_LEVEL(op=65)")

        # 4. Send Starter Summon Beasts (`GS2C_SUMM_ADD = 220` + `GS2C_SUMM_SET_FIGHT = 50`)
        for p_info in self.pets.values():
            self.send_raw(build_gs2c_summ_add(p_info), f"GS2C_SUMM_ADD(op=220, pid={p_info['id']}, name={p_info['name']!r})")
        first_pet_id = next(iter(self.pets.keys()), 50001)
        self.send_raw(build_gs2c_summ_set_fight(first_pet_id), f"GS2C_SUMM_SET_FIGHT(op=50, pid={first_pet_id})")

        # 5. Enter map scene (GS2C_MAP_SCENE_M = 96 + GS2C_MAP_GOTO_M = 97 + GS2C_MAP_ADD_NPC = 99)
        map_id = int(role.get("map_id", self.store.default_map_id))
        if map_id not in MAPS:
            map_id = 1025
        x = int(role.get("x", MAPS[map_id]["spawn_x"]))
        y = int(role.get("y", MAPS[map_id]["spawn_y"]))
        self.enter_map(map_id, x, y, send_welcome=send_welcome)

        # 6. Post-login world sync:
        #    - Resolution & ratio initialization (`GS2C_OTHER_ASSISTANT = 11, isub=42` -> `main.SetRate()`)
        #    - System settings switch (`GS2C_PROP_SWITCH = 21, isub=1` -> `dlgsysopt.ResetSaved()`)
        #    - Server time & calendar sync (`GS2C_PROP_SWITCH = 21, isub=6`, `GS2C_OPEN_UI = 89, isub=241`, `GS2C_TIME_SECOND = 192`)
        #    - QuickLogin key (`GS2C_QUICKLOGIN = 12, isub=1` -> `netquicklogin.S2CLoginKey`)
        #    Note: NEVER send `GS2C_TIME = 31` here unsolicited (`mxgw.S2CTime` only expects it after `C2GS_REQUEST_TIME = 61`).
        self._send_world_bootstrap_sync()

    def _send_world_bootstrap_sync(self) -> None:
        now_sec = monotonic_unix_seconds()
        self.send_raw(build_gs2c_set_rate(1), "GS2C_OTHER_ASSISTANT(op=11, isub=42 S2CSetRate)")
        self.send_raw(
            build_gs2c_prop_switch_setting(self.sys_switch),
            f"GS2C_PROP_SWITCH(op=21, isub=1 setting=0x{self.sys_switch:08x})",
        )
        self.send_raw(
            build_gs2c_prop_switch_server_time(now_sec),
            f"GS2C_PROP_SWITCH(op=21, isub=6 server_time={now_sec})",
        )
        self.send_raw(
            build_gs2c_refresh_server_time(now_sec),
            f"GS2C_OPEN_UI(op=89, isub=241 S2CRefreshServerTime={now_sec})",
        )
        self.send_raw(
            build_gs2c_time_second(now_sec),
            f"GS2C_TIME_SECOND(op=192, S2CTime={now_sec})",
        )
        self.send_raw(
            build_gs2c_quicklogin_key(self.login_key, 1),
            f"GS2C_QUICKLOGIN(op=12, isub=1 login_key=0x{self.login_key:08x})",
        )

    def _on_player_sysswitch(self, fields: bytes) -> None:
        if not fields:
            return
        sub = fields[0]
        if sub == 1 and len(fields) >= 5:
            # `nethero.C2SSaveSetting(setting:4B)` -> reply with `GS2C_PROP_SWITCH = 21, isub = 1`
            # which triggers `dlgsysopt.ResetSaved()` -> `game.FullScreen()` (`SetWndSize` + `SetWndScale`).
            switch_val = struct.unpack_from("<I", fields, 1)[0]
            self.sys_switch = switch_val
            if self.active_role is not None:
                self.active_role["sys_switch"] = switch_val
                self.store._save()
            log(f"[SYSOPT] C2GS_PLAYER_SYSSWITCH (op=21, sub=1 C2SSaveSetting): switch=0x{switch_val:08x}")
            self.send_raw(
                build_gs2c_prop_switch_setting(switch_val),
                f"GS2C_PROP_SWITCH(op=21, isub=1 setting=0x{switch_val:08x})",
            )
        elif sub == 7 and len(fields) >= 5:
            # `nethero.C2SSavePrice(price:4B)` -> reply with `GS2C_PROP_SWITCH = 21, isub = 9`
            price_val = struct.unpack_from("<I", fields, 1)[0]
            self.max_price = price_val
            if self.active_role is not None:
                self.active_role["max_price"] = price_val
                self.store._save()
            log(f"[SYSOPT] C2GS_PLAYER_SYSSWITCH (op=21, sub=7 C2SSavePrice): price={price_val}")
            self.send_raw(
                build_gs2c_prop_switch_price(price_val),
                f"GS2C_PROP_SWITCH(op=21, isub=9 price={price_val})",
            )
        elif sub in (2, 3, 5):
            # `nethero.C2SSaveSystemData` (hotkeys / system data)
            log(f"[SYSOPT] C2GS_PLAYER_SYSSWITCH (op=21, sub={sub} C2SSaveSystemData, len={len(fields)}B)")
            if self.active_role is not None:
                self.active_role[f"sysdata_{sub}"] = fields[1:].decode("latin-1", errors="ignore")
                self.store._save()

    def _on_huodong(self, fields: bytes) -> None:
        if len(fields) < 2:
            return
        tag_len = fields[0]
        if len(fields) < 1 + tag_len:
            return
        tag = fields[1 : 1 + tag_len].decode("ascii", errors="ignore")
        rest = fields[1 + tag_len :]
        log(f"[C2GS <- {self.addr[1]}] C2GS_HUODONG (op=90, tag={tag!r}, rest={rest.hex()})")
        if tag == "newchar" and len(rest) >= 2 and rest[0] == 11:
            # `netnewcharres.C2SSwitchUIStyle(style)` sends `iSub=11, iStyle=style+1`
            ui_style = rest[1]
            if self.active_role is not None:
                self.active_role["ui_style"] = ui_style
                self.store._save()
            self.send_raw(
                build_gs2c_newchar_switch_ui(ui_style),
                f"GS2C_HUODONG_OP(op=166, newchar S2CSwitchUIStyle={ui_style})",
            )

    def _on_quicklogin(self, fields: bytes) -> None:
        if not fields:
            return
        sub = fields[0]
        if sub == 1:
            # `netquicklogin.C2SRefreshLoginKey()`
            log(f"[QUICKLOGIN] C2GS_QUICKLOGIN (op=13, sub=1 C2SRefreshLoginKey)")
            self.send_raw(
                build_gs2c_quicklogin_key(self.login_key, 1),
                f"GS2C_QUICKLOGIN(op=12, isub=1 login_key=0x{self.login_key:08x})",
            )
        elif sub == 2 and len(fields) >= 9:
            # `netquicklogin.C2SRequestQuickLogin(key:4B, pid:4B)`
            # Triggered when saving resolution/ratio (`視野擴大` <-> `800*600`/`1024*768`/`1280*960`)
            # or switching UI style (`界面風格`) in System Settings (`dgtbaseopt.Save()`).
            req_key, pid = struct.unpack_from("<II", fields, 1)
            log(
                f"[QUICKLOGIN] C2GS_QUICKLOGIN (op=13, sub=2 C2SRequestQuickLogin): "
                f"key=0x{req_key:08x}, pid={pid}"
            )
            found = self.store.get_role_and_account(pid)
            if found is not None:
                acct_name, role = found
                self.account = acct_name
            else:
                roles = self.store.get_or_create_account(self.account, "")
                role = roles[0]
                role["id"] = pid
            # 1. Send `GS2C_QUICKLOGIN = 12, isub = 2` (`S2CLoginSuccess`) FIRST so
            #    `resetcontrol.DoNewResetClear()` runs BEFORE `S2CPropInit` builds the HUD!
            self.send_raw(
                build_gs2c_quicklogin_success(),
                "GS2C_QUICKLOGIN(op=12, isub=2 S2CLoginSuccess)",
            )
            # 2. Re-enter role world (sends `GS2C_PROP_INIT`, items, skills, pets, map, NPCs,
            #    and `_send_world_bootstrap_sync()` which runs `S2CSetRate` -> `main.SetRate()`).
            self._enter_role_world(role, send_welcome=False)
            self.send_raw(
                build_gs2c_notify("#G系統設置已成功切換並生效！#n", sub=1),
                "GS2C_NOTIFY(op=165, QuickLogin complete)",
            )

    def enter_map(self, map_id: int, x: int | None = None, y: int | None = None, send_welcome: bool = False) -> None:
        if map_id not in MAPS:
            # 傳送點全開：客戶端資料裡有 430 個場景，mock 只內建 6 個；
            # 走到/傳送到未知場景時就地建場（名字取自 entry 2601/2804 匯出的場景表），
            # 而不是悄悄退回清風村（舊行為會讓玩家以為傳送失敗）。
            MAPS[map_id] = {
                "scene": map_id,
                "mapid": map_id,
                "minimapid": map_id,
                "name": scene_display_name(map_id),
                "spawn_x": 10,
                "spawn_y": 10,
                "npc": {},
                "npcs": [],
                "portals": [],
            }
            _open_all_portals()
        m = MAPS.get(map_id, MAPS[1025])
        spawn_x = x if x is not None else int(m["spawn_x"])
        spawn_y = y if y is not None else int(m["spawn_y"])

        if self.active_role:
            self.active_role["map_id"] = m["scene"]
            self.active_role["x"] = spawn_x
            self.active_role["y"] = spawn_y
            self.store.update_role_pos(
                self.account,
                int(self.active_role["id"]),
                int(m["scene"]),
                spawn_x,
                spawn_y,
            )

        # 1. GS2C_MAP_SCENE_M = 96
        scene_pkt = build_gs2c_map_scene_m(
            scene=m["scene"],
            mapid=m["mapid"],
            minimapid=m["minimapid"],
            x=spawn_x,
            y=spawn_y,
            scenename=m["name"],
            has_rainbow=0,
            direct=3,
        )
        self.send_raw(
            scene_pkt,
            f"GS2C_MAP_SCENE_M(op=96, scene={m['scene']} {m['name']!r}, x={spawn_x}, y={spawn_y})",
        )

        # 2. GS2C_MAP_GOTO_M = 97
        goto_pkt = build_gs2c_map_goto_m(spawn_x, spawn_y)
        self.send_raw(goto_pkt, f"GS2C_MAP_GOTO_M(op=97, x={spawn_x}, y={spawn_y})")

        # 3. GS2C_MAP_ADD_NPC = 99 (spawn all authentic map NPCs + teleporter NPC)
        #    原版站位優先：entry 2601 `npcposdata` 匯出的該場景 NPC 名單（名字/座標/類別），
        #    再接上 mock 自己的傳送人（傳送點由它提供），避免自編 NPC 蓋掉原版人物。
        npc_list = map_npc_spawn_list(int(m["scene"]))
        for npc_item in npc_list:
            npc_pkt = build_gs2c_map_add_npc(npc_item)
            self.send_raw(
                npc_pkt,
                f"GS2C_MAP_ADD_NPC(op=99, id={npc_item['id']}, shape={npc_item['shape']}, "
                f"type={npc_item.get('npc_type', 0)}, name={npc_item['name']!r}, pos=({npc_item['x']},{npc_item['y']}))",
            )

        # 4. Welcome notification
        npc = m.get("npc") or (npc_list[0] if npc_list else {"name": "傳送人"})
        if send_welcome and self.active_role:
            msg = (
                f"#G歡迎來到《夢想世界》本地模擬伺服器！#n"
                f"當前地圖：#Y{m['name']}({m['scene']})#n 座標：({spawn_x},{spawn_y})，已載入 #G{len(npc_list)}#n 位地圖 NPC。"
                f"可點擊身旁的【{npc['name']}】、按 #YTab#n 打開小地圖點擊任意 NPC 尋路，或輸入 #R/tp 1054#n 傳送至明月城！"
            )
            self.send_raw(build_gs2c_notify(msg, sub=2), "GS2C_NOTIFY(op=165)")

    # ------------------------------------------------------------------------
    # Character Attributes, Point Allocation, Level-Up, Titles, Items & GM
    # ------------------------------------------------------------------------
    def _on_player_adjustpoint(self, fields: bytes) -> None:
        if not fields or not self.active_role:
            return
        sub = fields[0]
        log(f"[C2GS <- {self.addr[1]}] C2GS_PLAYER_ADJUSTPOINT (op=16, sub={sub})")
        r = self.active_role
        lv = int(r.get("level", 60))
        if sub == 1 and len(fields) >= 6:
            # Manual point allocation: `sub=1, a0(Str), a1(Mag), a2(Con), a3(Dex), a4(Cha)`
            a_str, a_mag, a_con, a_dex, a_cha = fields[1:6]
            spent = a_str + a_mag + a_con + a_dex + a_cha
            free_pt = int(r.get("point", 50))
            if spent <= free_pt and spent > 0:
                r["str_all"] = int(r.get("str_all", 100 + lv * 2)) + a_str
                r["mag_all"] = int(r.get("mag_all", 100 + lv * 2)) + a_mag
                r["con_all"] = int(r.get("con_all", 100 + lv * 2)) + a_con
                r["dex_all"] = int(r.get("dex_all", 90 + lv * 2)) + a_dex
                r["cha_all"] = int(r.get("cha_all", 90 + lv * 2)) + a_cha
                r["point"] = free_pt - spent
                self.store._save()
                self.send_raw(build_gs2c_prop_init(r), "GS2C_PROP_INIT(op=16, adjustpoint)")
                self.send_raw(build_gs2c_notify(f"#G成功分配 {spent} 點潛力點！剩餘潛力點：{r['point']}#n", sub=1), "GS2C_NOTIFY")
        elif sub == 2:
            # Open Auto-Point Allocation dialog (`GS2C_OPEN_UI = 89, sub=235`)
            self.send_raw(build_gs2c_open_ui_autopoint(r), "GS2C_OPEN_UI(op=89, sub=235 AutoPoint)")
        elif sub == 3 and len(fields) >= 7:
            # Save Auto-Point settings: `sub=3, p0..p4, bSelect`
            p0, p1, p2, p3, p4, b_sel = fields[1:7]
            r["autopoint"] = [p0, p1, p2, p3, p4]
            r["autopoint_enable"] = b_sel
            self.store._save()
            self.send_raw(build_gs2c_open_ui_autopoint(r), "GS2C_OPEN_UI(op=89, sub=235 AutoPointSaved)")
            self.send_raw(build_gs2c_notify("#G自動分配潛力點方案已保存！#n", sub=1), "GS2C_NOTIFY")
        elif sub == 4:
            r["autopoint_enable"] = 0
            self.store._save()
            self.send_raw(build_gs2c_open_ui_autopoint(r), "GS2C_OPEN_UI(op=89, sub=235 AutoPointCancel)")
        elif sub == 5:
            # Auto allocate remaining points using saved ratio
            ap = r.get("autopoint", [3, 0, 1, 1, 0])
            free_pt = int(r.get("point", 50))
            if free_pt >= 5 and sum(ap) == 5:
                sets = free_pt // 5
                r["str_all"] = int(r.get("str_all", 100 + lv * 2)) + ap[0] * sets
                r["mag_all"] = int(r.get("mag_all", 100 + lv * 2)) + ap[1] * sets
                r["con_all"] = int(r.get("con_all", 100 + lv * 2)) + ap[2] * sets
                r["dex_all"] = int(r.get("dex_all", 90 + lv * 2)) + ap[3] * sets
                r["cha_all"] = int(r.get("cha_all", 90 + lv * 2)) + ap[4] * sets
                r["point"] = free_pt - sets * 5
                self.store._save()
                self.send_raw(build_gs2c_prop_init(r), "GS2C_PROP_INIT(op=16, auto_addpoint)")
                self.send_raw(build_gs2c_notify("#G已按自動加點方案分配潛力點！#n", sub=1), "GS2C_NOTIFY")

    def _on_player_upgrade(self) -> None:
        if not self.active_role:
            return
        r = self.active_role
        old_lv = int(r.get("level", 60))
        if old_lv >= 165:
            self.send_raw(build_gs2c_notify("#Y您已達到最高等級 165 級！#n", sub=1), "GS2C_NOTIFY")
            return
        new_lv = old_lv + 1
        r["level"] = new_lv
        r["str_all"] = int(r.get("str_all", 100 + old_lv * 2)) + 1
        r["mag_all"] = int(r.get("mag_all", 100 + old_lv * 2)) + 1
        r["con_all"] = int(r.get("con_all", 100 + old_lv * 2)) + 1
        r["dex_all"] = int(r.get("dex_all", 90 + old_lv * 2)) + 1
        r["cha_all"] = int(r.get("cha_all", 90 + old_lv * 2)) + 1
        r["point"] = int(r.get("point", 50)) + 5
        self.store._save()
        self.send_raw(build_gs2c_prop_init(r), f"GS2C_PROP_INIT(op=16, upgrade lv={new_lv})")
        self.send_raw(
            build_gs2c_notify(f"#G恭喜少俠升至 {new_lv} 級！獲得 5 點潛力點！#n", sub=2),
            "GS2C_NOTIFY",
        )

    def _on_title_op(self, fields: bytes) -> None:
        if not fields or not self.active_role:
            return
        sub = fields[0]
        log(f"[C2GS <- {self.addr[1]}] C2GS_TITLE (op=67, sub={sub})")
        r = self.active_role
        if sub == 6:
            # Open Title dialog (`GS2C_OPEN_UI = 89, sub=183, mode=1`)
            self.send_raw(build_gs2c_open_ui_titles(r), "GS2C_OPEN_UI(op=89, sub=183 Titles)")
        elif sub == 8 and len(fields) >= 3:
            # Get description for title_id (`GS2C_TITLE = 200, sub=1`)
            tid = struct.unpack_from("<H", fields, 1)[0]
            self.send_raw(build_gs2c_title_desc(tid), f"GS2C_TITLE(op=200, sub=1, tid={tid})")
        elif sub in (3, 4) and len(fields) >= 3:
            # Select/change title (`sub=3: ChooseTitle(id:2B, color:1B)`)
            tid = struct.unpack_from("<H", fields, 1)[0]
            tcolor = fields[3] if len(fields) >= 4 else 0
            title_str = ""
            for t in PLAYER_TITLES:
                if int(t["id"]) == tid:
                    title_str = t["title"]
                    if tcolor == 0:
                        tcolor = int(t.get("color", 0))
                    break
            r["title_id"] = tid
            r["title"] = title_str
            r["title_color"] = tcolor
            self.store._save()
            # Update m_Title (idx=16), m_TitleID (idx=17), m_TitleColor (idx=64)
            self.send_raw(build_gs2c_prop_change_str(16, title_str, 60), f"GS2C_PROP_CHANGELIST(m_Title={title_str!r})")
            self.send_raw(build_gs2c_prop_change_word(17, tid), f"GS2C_PROP_CHANGELIST(m_TitleID={tid})")
            self.send_raw(build_gs2c_prop_change_byte(64, tcolor), f"GS2C_PROP_CHANGELIST(m_TitleColor={tcolor})")
            self.send_raw(build_gs2c_open_ui_titles(r), "GS2C_OPEN_UI(op=89, sub=183 Titles)")
            if title_str:
                self.send_raw(build_gs2c_notify(f"#G稱謂已更換為【{title_str}】！#n", sub=1), "GS2C_NOTIFY")

    def _on_item_op(self, fields: bytes) -> None:
        if not fields:
            return
        sub = fields[0]
        log(f"[C2GS <- {self.addr[1]}] C2GS_ITEM_OP (op=32, sub={sub})")
        if sub == 1 and len(fields) >= 6:
            # Drag / Move / Equip / Unequip item (`itemID:4B, destPos:1B`)
            item_id = struct.unpack_from("<I", fields, 1)[0]
            dest_pos = fields[5]
            it1 = self.items.get(item_id)
            if not it1:
                return
            old_pos = int(it1["pos"])
            # Check if another item is already at dest_pos
            it2 = None
            for cand in self.items.values():
                if int(cand["id"]) != item_id and int(cand["pos"]) == dest_pos:
                    it2 = cand
                    break
            it1["pos"] = dest_pos
            if it2:
                it2["pos"] = old_pos
                self.send_raw(
                    build_gs2c_item_pos(item_id, dest_pos, int(it2["id"]), old_pos),
                    f"GS2C_ITEM_POS(swap {item_id}->{dest_pos}, {it2['id']}->{old_pos})",
                )
            else:
                self.send_raw(
                    build_gs2c_item_pos(item_id, dest_pos, 0, 0),
                    f"GS2C_ITEM_POS(move {item_id}->{dest_pos})",
                )
        elif sub == 7 and len(fields) >= 5:
            # Use item (`itemID:4B`)
            item_id = struct.unpack_from("<I", fields, 1)[0]
            it = self.items.get(item_id)
            if it:
                # If equipment in bag (`pos >= 20`), equip it to its matching slot!
                shape = int(it["shape"])
                pos = int(it["pos"])
                equip_slot_map = {
                    60030: 1, 50030: 2, 51030: 2, 61030: 3,
                    66030: 4, 63030: 5, 64030: 7, 65020: 8, 62030: 9,
                }
                if pos >= 20 and shape in equip_slot_map:
                    target_slot = equip_slot_map[shape]
                    self._on_item_op(struct.pack("<BIB", 1, item_id, target_slot))
                else:
                    self.send_raw(
                        build_gs2c_notify(f"#G使用了【{it.get('name', '物品')}】！#n", sub=1),
                        "GS2C_NOTIFY",
                    )

    # ------------------------------------------------------------------------
    # In-Map NPC Dialog & Slash Commands
    # ------------------------------------------------------------------------
    def _on_npc_look(self, npc_id: int) -> None:
        cur_map_id = int(self.active_role.get("map_id", 1025)) if self.active_role else 1025
        m = MAPS.get(cur_map_id, MAPS[1025])
        npc = m["npc"]
        # 以**實際下發**的名單查（原版站位 + 傳送人），不是 mock 內建設定
        all_npcs = map_npc_spawn_list(cur_map_id)
        for cand in all_npcs:
            if int(cand.get("id", 0)) == npc_id:
                npc = cand
                break
        self.last_npc = dict(npc)
        self.last_npc["map_id"] = cur_map_id

        if is_teleporter(npc):
            # 傳送人：保留**可用**的傳送選項（「傳送點全開」就是這裡每個城市都能進）
            greeting = npc.get(
                "greeting",
                f"少俠好！這裡是#Y{m['name']}#n，我是#G{npc['name']}#n，想到哪裡去？",
            )
            dialog_text = greeting + "\n" + "\n".join(
                f"Q傳送至【{MAPS[mid]['name']}】({mid})" for mid in sorted(MAPS)
            )
            if self.active_role:
                dialog_text += "\nQ恢復滿氣血法力並領取 100 萬兩銀幣"
                dialog_text += "\nQ角色連升 10 級 (刷新全屬性)"
            dialog_text += "\nQ我只是路過"
        else:
            dialog_text = npc_dialogue_text(npc)

        pkt = build_gs2c_npc_chat_ext(
            npc_id=npc_id,
            icon=int(npc.get("icon", npc.get("shape", 3007))),
            name=str(npc.get("name", "神秘人")),
            msg=dialog_text,
            response_id=100,
        )
        tag = "原版" if npc.get("authentic") else "內建"
        self.send_raw(
            pkt,
            f"GS2C_NPC_CHAT_EXT(op=152, id={npc_id}, {tag} npc={npc['name']!r}, kind={npc.get('kind', 'teleporter')})",
        )

    def _on_npc_answer(self, choice: int, response_id: int) -> None:
        npc = getattr(self, "last_npc", None) or {}
        if not is_teleporter(npc):
            # 一般 NPC：選項一律回「敬請期待」（原版選單在服務端，客戶端只有 NPC 識別資料）
            self.send_raw(
                build_gs2c_npc_chat_ext(
                    npc_id=int(npc.get("id", 0)) & 0xFFFFFFFF,
                    icon=int(npc.get("icon", npc.get("shape", 3007))),
                    name=str(npc.get("name", "神秘人")),
                    msg=f"P N({int(npc.get('icon', 3007))},{npc.get('name', '神秘人')})\n"
                    f"（選項「{choice}」）這個功能#Y敬請期待#n，少俠改日再來看看。\nQ我知道了",
                    response_id=100,
                ),
                f"GS2C_NPC_CHAT_EXT(op=152, id={npc.get('id')}, 敬請期待 choice={choice})",
            )
            return

        tp_targets = {i: mid for i, mid in enumerate(sorted(MAPS), start=1)}
        if choice in tp_targets:
            target_id = tp_targets[choice]
            target_name = MAPS[target_id]["name"]
            self.enter_map(target_id)
            self.send_raw(
                build_gs2c_notify(f"#G已為您傳送至【{target_name}】({target_id})！#n", sub=2),
                "GS2C_NOTIFY",
            )
        elif choice == len(tp_targets) + 1:
            if self.active_role:
                self.active_role["cash"] = int(self.active_role.get("cash", 888888)) + 1000000
                self.store._save()
                self.send_raw(build_gs2c_prop_init(self.active_role), "GS2C_PROP_INIT(op=16, heal+cash)")
            self.send_raw(
                build_gs2c_notify("#Y氣血與法力已完全恢復，並獲得 1,000,000 兩銀幣！#n", sub=2),
                "GS2C_NOTIFY",
            )
        elif choice == len(tp_targets) + 2:
            if self.active_role:
                new_lv = min(165, int(self.active_role.get("level", 60)) + 10)
                self.active_role["level"] = new_lv
                self.active_role["point"] = int(self.active_role.get("point", 200)) + 50
                self.store._save()
                self.send_raw(build_gs2c_prop_init(self.active_role), f"GS2C_PROP_INIT(op=16, lv={new_lv})")
                self.send_raw(
                    build_gs2c_notify(f"#G恭喜少俠！等級已提升至 {new_lv} 級，各項屬性大幅提升！#n", sub=2),
                    "GS2C_NOTIFY",
                )

    def _handle_chat_or_gm_command(self, cmd: str) -> None:
        parts = cmd.strip().split()
        if not parts:
            return
        head = parts[0].lower()
        if head in ("/tp", "$goto", "/goto") and len(parts) >= 2:
            try:
                target_map = int(parts[1])
                tx = int(parts[2]) if len(parts) >= 4 else None
                ty = int(parts[3]) if len(parts) >= 4 else None
                if target_map in MAPS:
                    self.enter_map(target_map, tx, ty)
                    self.send_raw(
                        build_gs2c_notify(f"#G已傳送至 {MAPS[target_map]['name']} ({target_map})！#n", sub=2),
                        "GS2C_NOTIFY",
                    )
                    return
            except ValueError:
                pass
        if head == "/shape" and len(parts) >= 2 and self.active_role:
            try:
                new_shape = normalize_player_shape(int(parts[1]))
                r = self.active_role
                r["shape"] = new_shape
                r["icon"] = SHAPE_DEFAULT_ICON.get(new_shape, 1)
                self.store._save()
                role_id = int(r["id"])
                self.send_raw(build_gs2c_prop_init(r), f"GS2C_PROP_INIT(shape={new_shape})")
                self.send_raw(build_gs2c_map_change_shape(role_id, new_shape), f"GS2C_CHANGE_SHAPE(shape={new_shape})")
                sname = SHAPE_NAMES.get(new_shape, str(new_shape))
                self.send_raw(
                    build_gs2c_notify(f"#G角色外型已切換為：{sname} (shape={new_shape})！#n", sub=2),
                    "GS2C_NOTIFY",
                )
                return
            except ValueError:
                pass
        if head == "/pos" and self.active_role:
            msg = (
                f"當前角色：{self.active_role['name']} (ID={self.active_role['id']}, 外型={self.active_role.get('shape')}) "
                f"地圖：{self.active_role.get('map_id')} 座標：({self.active_role.get('x')}, {self.active_role.get('y')})"
            )
            self.send_raw(build_gs2c_notify(msg, sub=2), "GS2C_NOTIFY")
            return
        self.send_raw(
            build_gs2c_notify(
                "可用指令：#Y/tp 1054#n(明月城) #Y/tp 1025#n(清風村) #Y/tp 1001#n(永澤城) #Y/shape 111..232#n(切換外型：111愛德華/112隆/121浪人/122星虎/131凌風/132霹靂火/211莉莉絲/212雪蓮/221玉馨/222燕歌行/231明月姬/232晚秋) #Y/pos#n",
                sub=2,
            ),
            "GS2C_NOTIFY",
        )


# ============================================================================
# 6. Built-In Protocol Self-Test (`--self-test`)
# ============================================================================


def run_self_test() -> int:
    """
    Verifies all GS2C packet builders and C2GS parsers against the exact field
    sizes and offsets expected by `netlogin.py`, `nethero.py`, `prop.py`, and `netmap.py`.
    """
    log("Running full protocol self-test (選區 -> 賬號密碼登錄 -> 創建/選擇角色 -> 進入地圖)...")

    # 1. GS2C_HELLO (9 bytes total: len=8, op=1, seed=4B, server_num=2B, cert=1B)
    seed = 0x13572468
    hello = build_gs2c_hello(seed=seed, server_num=3, is_cert=0)
    assert len(hello) == 9 and hello[0] == 8 and hello[1] == GS2C_HELLO

    # 0. Long-packet framing: 0xFF + 3 continuation bytes (see MAX_LEN_BYTES above).
    assert MAX_LEN_BYTES == 3, "client's CNet.__init__ calls SetMaxLenBytes(3)"
    esc = frame_gs2c(99, b"\x00" * 300)
    assert esc[0] == 0xFF and len(esc) == 1 + MAX_LEN_BYTES + 301
    assert int.from_bytes(esc[1 : 1 + MAX_LEN_BYTES], "little") == 301, "body length = 301"
    assert esc[1 + MAX_LEN_BYTES] == 99, "next byte must be the opcode, not 0x00"
    u_seed, u_srv, u_cert = struct.unpack_from("<IHB", hello, 2)
    assert (u_seed, u_srv, u_cert) == (seed, 3, 0)
    r3 = compute_hello_reply_bytes(seed)
    assert len(r3) == 3

    # 2. GS2C_LOGIN_ACCOUNT_INFO (8 bytes total: len=7, op=15, count=1B, time=4B, vid=1B)
    acct_info = build_gs2c_login_account_info(role_count=2, cur_time=1700000000, vid=1)
    assert len(acct_info) == 8 and acct_info[0] == 7 and acct_info[1] == GS2C_LOGIN_ACCOUNT_INFO

    # 3. GS2C_LOGIN_PLAYER_INFO (39 bytes total: len=38, op=3, payload=37B)
    sample_role = {
        "id": 10001,
        "name": "夢想少俠",
        "icon": 1,
        "shape": 1,
        "color": 0,
        "level": 60,
        "school": 1,
        "race": 1,
        "point": 200,
    }
    p_info = build_gs2c_login_player_info(sample_role)
    assert len(p_info) == 39 and p_info[0] == 38 and p_info[1] == GS2C_LOGIN_PLAYER_INFO
    assert decode_big5(p_info[23:39]) == "夢想少俠"

    # 4. GS2C_PROP_INIT (408 bytes total: 0xFF + 3B len(404) + op(16) + 403B payload)
    prop_pkt = build_gs2c_prop_init(sample_role)
    assert prop_pkt[0] == 0xFF
    ext_len = int.from_bytes(prop_pkt[1 : 1 + MAX_LEN_BYTES], "little")
    assert (
        ext_len == 404
        and len(prop_pkt) == 1 + MAX_LEN_BYTES + 404
        and prop_pkt[1 + MAX_LEN_BYTES] == GS2C_PROP_INIT
    ), "long body (entry-map PROP_INIT) framing"

    # 5. GS2C_MAP_SCENE_M & GS2C_MAP_GOTO_M & GS2C_MAP_ADD_NPC
    scene_pkt = build_gs2c_map_scene_m(1025, 1025, 1025, 75, 52, "清風村")
    assert scene_pkt[1] == GS2C_MAP_SCENE_M
    goto_pkt = build_gs2c_map_goto_m(75, 52)
    assert len(goto_pkt) == 6 and goto_pkt[0] == 5 and goto_pkt[1] == GS2C_MAP_GOTO_M
    npc_pkt = build_gs2c_map_add_npc(MAPS[1025]["npc"])
    assert npc_pkt[1] == GS2C_MAP_ADD_NPC

    # 5b. Opcode audit regressions (client `idx=3970` protocol.py + `idx=3176` net.py):
    #     these three must never drift back to the values the upstream copy had.
    assert GS2C_MAP_DEL == 85, "GS2C_MAP_DEL must be 85 (100 is GS2C_MAP_ADD_GOODS)"
    assert GS2C_CHANGE_SHAPE == 106, "GS2C_CHANGE_SHAPE must be 106 (107 is GS2C_MAP_STORE)"
    assert C2GS_PLAYER_UPGRADE == 152 and C2GS_PLAYER_UPGRADE_LEGACY == 17

    # Prop changes ride a 1-entry GS2C_PROP_CHANGELIST (61), because 152 is shadowed
    # by GS2C_NPC_CHAT_EXT and 17 has no handler in this client build.
    pc_word = build_gs2c_prop_change_word(17, 101)
    assert pc_word[1] == GS2C_PROP_CHANGELIST == 61
    assert pc_word[2:] == bytes([1, 17]) + struct.pack("<H", 101), "1-entry changelist payload"
    pc_byte = build_gs2c_prop_change_byte(64, 3)
    assert pc_byte[2:] == bytes([1, 64, 3])
    pc_str = build_gs2c_prop_change_str(16, "開拓者", 60)
    assert pc_str[2:] == bytes([1, 16]) + encode_big5("開拓者", 60)

    shape_pkt = build_gs2c_map_change_shape(10001, 5)
    assert shape_pkt[1] == GS2C_CHANGE_SHAPE

    # 5c. GM mode: `nocheck` must carry `[game] gm=1`, not be an empty file.
    tmp_nocheck = Path("/tmp/test_mock_nocheck")
    if tmp_nocheck.exists():
        tmp_nocheck.unlink()
    ensure_nocheck_gm(tmp_nocheck)
    assert tmp_nocheck.read_text(encoding="latin-1").splitlines()[:2] == ["[game]", "gm=1"]
    tmp_nocheck.write_text("gm=0\n[game]\nother=2\n", encoding="latin-1")
    ensure_nocheck_gm(tmp_nocheck)
    lines = tmp_nocheck.read_text(encoding="latin-1").splitlines()
    assert lines[0] == "gm=0" and "other=2" in lines           # unrelated keys preserved
    assert lines.index("[game]") < lines.index("gm=1")          # gm=1 inside [game]
    assert lines.index("gm=1") < len(lines)
    assert "Found" in ensure_nocheck_gm(tmp_nocheck)  # idempotent
    tmp_nocheck.unlink()
    # 5d. Time sync (007 watchdog vs Calendar/Schedule Unix seconds):
    #     - `GS2C_TIME = 31` (`mxgw.S2CTime`) MUST be centiseconds (100 ticks/sec) so
    #       `sdt = t - g_ServerTime + 550 >= cdt = (G2 - G1) / 100` (where `C_sys.GetTime` is 10,000 ticks/sec).
    #     - `GS2C_TIME_SECOND = 192` (`dlgcalendar.S2CTime`) and `GS2C_OPEN_UI = 89, isub = 241`
    #       (`netopenui.S2CRefreshServerTime` -> `misc.SetServerTime`) MUST be Unix seconds.
    time_pkt = build_gs2c_time()
    assert time_pkt[1] == GS2C_TIME == 31
    assert len(time_pkt) == 2 + 4, "GS2C_TIME payload must be 4 bytes"
    sent_cs = struct.unpack_from("<I", time_pkt, 2)[0]
    assert sent_cs >= 10000, f"GS2C_TIME centisecond counter must start >= 10000, got {sent_cs}"
    assert struct.unpack_from("<I", build_gs2c_time(), 2)[0] >= sent_cs, "GS2C_TIME must be monotonic"
    # Verify mxgw.SecondGetResult math over 25s (750 frames), 40s (1200 frames), and 180s (5400 frames):
    for interval_sec in (25, 40, 180):
        g1 = 1_000_000
        g2 = g1 + interval_sec * 10000  # C_sys.GetTime() is 0.1ms (10,000 ticks/sec)
        cdt = g2 // 100 - g1 // 100     # centiseconds
        srv_t1 = sent_cs
        srv_t2 = srv_t1 + interval_sec * 100
        sdt = srv_t2 - srv_t1 + 550
        assert cdt <= sdt, f"mxgw 007 check failed for {interval_sec}s: cdt={cdt} > sdt={sdt}"

    tsec_pkt = build_gs2c_time_second()
    assert tsec_pkt[1] == GS2C_TIME_SECOND == 192
    sent_unix = struct.unpack_from("<I", tsec_pkt, 2)[0]
    assert abs(sent_unix - int(time.time())) <= 5, f"GS2C_TIME_SECOND must be Unix seconds, got {sent_unix}"
    ref_pkt = build_gs2c_refresh_server_time()
    assert ref_pkt[1] == GS2C_OPEN_UI == 89 and ref_pkt[2] == 241
    assert abs(struct.unpack_from("<I", ref_pkt, 3)[0] - int(time.time())) <= 5

    # 5e. 傳送點全開：每個場景都能走到其他所有場景。
    for mid, mm in MAPS.items():
        targets = {int(p["target_map"]) for p in mm.get("portals", [])}
        missing = [o for o in MAPS if o != mid and o not in targets]
        assert not missing, f"map {mid} missing portals to {missing}"

    # 5f. 原版 NPC 佈局（若使用者帶了 npc_layout.json）。
    if NPC_LAYOUT:
        assert authentic_npcs(1025), "scene 1025 must have authentic NPCs"
        shop = next((n for n in authentic_npcs(1054) if n.get("kind") == "shop"), None)
        assert shop is not None, "scene 1054 must contain a shop NPC"
        body = npc_dialogue_text(shop)
        assert body.startswith("P N(") and "\nQ" in body, "dialogue must use the original P/Q line format"
        assert scene_display_name(1001) == "永澤城"
        assert len(authentic_npcs(1054)) == 52, "明月城應還原全部 52 個原版 NPC（不截斷）"
        assert len(authentic_npcs(1025)) == 14, "清風村應為 14 個原版 NPC"
        trunc = [sid for sid in [int(k) for k in list(NPC_LAYOUT["scenes"])]
                 if len(map_npc_spawn_list(sid)) < len(authentic_npcs(sid))]
        assert not trunc, f"下發名單不得少於原版名單，被截斷的場景：{trunc[:5]}"
        log(f"[PASS] 原版 NPC 佈局：{len(NPC_LAYOUT['scenes'])} 場景 / "
            f"{sum(len(v.get('npcs') or []) for v in NPC_LAYOUT['scenes'].values())} NPC 全部還原"
            f"（1054 明月城 {len(authentic_npcs(1054))} 個、1025 清風村 {len(authentic_npcs(1025))} 個）。")
    else:
        log("[WARN] 未載入 npc_layout.json：原版 NPC 佈局檢查跳過（--npc-layout 可指定）。")

    # 5g. 屬性面板（GS2C_PROP_INIT = 16）：載荷必須是 12 + 391 = 403 位元組，
    #     因此線上封包必然 >255 → 依賴 3 位元組長度前綴（見 MAX_LEN_BYTES）。
    sample = {"id": 10001, "name": "測試", "level": 60, "shape": 111}
    prop_pkt = build_gs2c_prop_init(sample)
    # 403B 載荷 → 走 `0xFF` 逃逸：`0xFF | len(3B) | opcode | payload`
    assert prop_pkt[0] == 0xFF, "PROP_INIT (403B payload) must use the 0xFF escape"
    assert prop_pkt[4] == GS2C_PROP_INIT == 16
    assert int.from_bytes(prop_pkt[1:4], "little") == 404, "frame length = opcode(1) + 403"
    assert MAX_LEN_BYTES == 3, "PROP_INIT cannot be framed with a 2-byte length"

    log("[PASS] Opcode audit + GM-mode (nocheck) regressions verified.")

    # 6. End-to-end loopback socket test across all 4 stages
    tmp_db = Path("/tmp/test_mock_accounts.json")
    if tmp_db.exists():
        tmp_db.unlink()
    store = AccountStore(tmp_db, default_map_id=1025)

    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind(("127.0.0.1", 0))
    srv_sock.listen(4)
    port = srv_sock.getsockname()[1]

    def _srv_thread() -> None:
        while True:
            try:
                conn, addr = srv_sock.accept()
            except OSError:
                break
            sess = ClientSession(conn, addr, store, seed=seed, server_num=3)
            threading.Thread(target=sess.run, daemon=True).start()

    t = threading.Thread(target=_srv_thread, daemon=True)
    t.start()

    cli = socket.create_connection(("127.0.0.1", port), timeout=5.0)
    # Stage 1: Receive GS2C_HELLO from server first
    h_rx = cli.recv(9)
    assert h_rx == hello, "Stage 1 GS2C_HELLO mismatch"
    # Send 25-byte NakedSend reply
    cli.sendall(compute_hello_reply_bytes(seed) + b"\x00" * 22)

    # Helper to send native CPacket C2GS frame `[opcode][len+1][fields][0x00]`
    def send_c2gs(op: int, f: bytes) -> None:
        cli.sendall(bytes([op, len(f) + 1]) + f + b"\x00")

    # Helper to read one GS2C frame
    def recv_gs2c() -> tuple[int, bytes]:
        b0 = cli.recv(1)[0]
        if b0 == 0xFF:
            ext = cli.recv(MAX_LEN_BYTES)
            plen = int.from_bytes(ext + b"\x00" * (4 - MAX_LEN_BYTES), "little")
        else:
            plen = b0
        body = b""
        while len(body) < plen:
            body += cli.recv(plen - len(body))
        return body[0], body[1:]

    # Stage 2: Send C2GS_LOGIN_ACCOUNT_ENTER = 1
    # Real v2.27.2 `netlogin.C2SLoginIn` layout (entry 4082), verified 2026-10-12
    # from the bytecode: PacketAddS(name, 32) at co_code 176, PacketAddS(pwd, 20)
    # at co_code 192.  `fields` excludes the cmd byte, so name is at 4..35 and
    # pwd at 36..55.  The previous 40B/32B shape only matched the `data/data.fls`
    # bot path, so this test was exercising the wrong parser branch.
    login_fields = (
        b"\x00"                                  # iScriptV1 (0 or 0x80 if mini)
        + b"\x02"                                # CLIENT_VERSION[1]
        + struct.pack("<H", 27)                  # CLIENT_VERSION[2]
        + encode_big5("testuser01", 32)          # name   (32B fixed)
        + encode_big5("e10adc3949ba59abbe56e057f20f883e", 20)  # pwd (20B fixed)
        + b"\x00" * 4                            # C_sys.GetVersion()
        + b"\x02\x1b\x00\x00"                    # update.ini [Setting] Version
        + b"\x7f\x00\x00\x01"                    # localip
        + b"\x00" * 8                            # adsid (hi, lo)
        + b"\x00"                                # len(tgId) = 0
        + b"\x00" * 4                            # driveid
        + b"\x11\x22\x33\x44\x55\x66"            # mac (no length prefix)
    )
    assert len(login_fields) == 87
    assert login_fields[1:4] == b"\x02\x1b\x00", "must take the script.fls branch"
    assert login_fields[4:36].startswith(b"testuser01")
    send_c2gs(C2GS_LOGIN_ACCOUNT_ENTER, login_fields)
    op1, body1 = recv_gs2c()
    assert op1 == GS2C_LOGIN_ACCOUNT_INFO and body1[0] == 1
    op2, body2 = recv_gs2c()
    assert op2 == GS2C_LOGIN_PLAYER_INFO and len(body2) == 37

    # Stage 3: Send C2GS_LOGIN_PLAYER_ADD = 3 (create new character)
    create_fields = (
        b"\x01"
        + encode_big5("劍俠客", 20)
        + struct.pack("<BHHBBH", 2, 3, 1, 0, 0, 1)
    )
    send_c2gs(C2GS_LOGIN_PLAYER_ADD, create_fields)
    op3, body3 = recv_gs2c()
    assert op3 == GS2C_LOGIN_PLAYER_INFO
    new_role_id = struct.unpack_from("<I", body3, 0)[0]
    assert decode_big5(body3[21:37]) == "劍俠客"
    op4, body4 = recv_gs2c()
    assert op4 == GS2C_LOGIN_PLAYER_ADD and body4 == b""

    # Stage 4: Send C2GS_LOGIN_PLAYER_ENTER = 2 (enter game with newly created role)
    send_c2gs(C2GS_LOGIN_PLAYER_ENTER, struct.pack("<I", new_role_id))
    op5, body5 = recv_gs2c()
    assert op5 == GS2C_PROP_INIT and len(body5) == 403
    # Verify human shape (111..232) at m_Shape (offset 13) and m_RealShape
    u_shape = struct.unpack_from("<H", body5, 13)[0]
    assert u_shape in VALID_PLAYER_SHAPES, f"Expected human shape in VALID_PLAYER_SHAPES, got {u_shape}"
    for _ in range(len(STARTER_ITEMS)):
        op_it, _ = recv_gs2c()
        assert op_it == GS2C_ITEM_ADD
    op_ikey, _ = recv_gs2c()
    assert op_ikey == GS2C_ITEM_KEY
    for _ in range(4):
        op_sk, _ = recv_gs2c()
        assert op_sk == GS2C_SKILL_LEVEL
    for _ in range(len(STARTER_PETS)):
        op_pet, _ = recv_gs2c()
        assert op_pet == GS2C_SUMM_ADD
    op_pfight, _ = recv_gs2c()
    assert op_pfight == GS2C_SUMM_SET_FIGHT
    op6, body6 = recv_gs2c()
    assert op6 == GS2C_MAP_SCENE_M
    op7, body7 = recv_gs2c()
    assert op7 == GS2C_MAP_GOTO_M
    expected_npcs = len(map_npc_spawn_list(1025))
    for _ in range(expected_npcs):
        op_npc, _ = recv_gs2c()
        assert op_npc == GS2C_MAP_ADD_NPC
    op9, body9 = recv_gs2c()
    assert op9 == GS2C_NOTIFY
    # Verify post-login world bootstrap sync packets (resolution rate, sys_switch, server time, calendar, quicklogin key)
    op_rate, body_rate = recv_gs2c()
    assert op_rate == GS2C_OTHER_ASSISTANT and body_rate == b"\x2a\x01"
    op_sw1, body_sw1 = recv_gs2c()
    assert op_sw1 == GS2C_PROP_SWITCH and body_sw1[0] == 1
    op_sw6, body_sw6 = recv_gs2c()
    assert op_sw6 == GS2C_PROP_SWITCH and body_sw6[0] == 6
    op_ref, body_ref = recv_gs2c()
    assert op_ref == GS2C_OPEN_UI and body_ref[0] == 241
    op_tsec, body_tsec = recv_gs2c()
    assert op_tsec == GS2C_TIME_SECOND and len(body_tsec) == 4
    op_qlk, body_qlk = recv_gs2c()
    assert op_qlk == GS2C_QUICKLOGIN and body_qlk[0] == 1
    login_key = struct.unpack_from("<I", body_qlk, 1)[0]
    assert login_key == 0x514C4B59

    # Stage 5: Walk in map (`C2GS_MAP_MOVE = 54`), Click NPC (`C2GS_MIXPACKET = 151` wrapping `C2GS_NPC_LOOK = 96`),
    # Select Teleport Option (`C2GS_NPC_ANSWER = 98`), Open Attribute View (`C2GS_OPEN_UI_NEW = 230`),
    # Open Titles (`C2GS_TITLE = 67`), View Summon Beast (`C2GS_SUMMON_PROPVIEW = 129`), and Heartbeat (`C2GS_HEART_BEAT = 63`)
    send_c2gs(C2GS_MAP_MOVE, struct.pack("<HHBB", 75, 52, 1, 1))
    # Test C2GS_MIXPACKET = 151 wrapping C2GS_NPC_LOOK = 96
    inner_look = struct.pack("<I", 50001)
    mix_payload = struct.pack("<IBBH", new_role_id, 3, C2GS_NPC_LOOK, len(inner_look)) + inner_look
    send_c2gs(C2GS_MIXPACKET, mix_payload)
    op_chat, _ = recv_gs2c()
    assert op_chat == GS2C_NPC_CHAT_EXT

    # Test C2GS_NPC_ANSWER = 98 (2-byte `responseID=100, choice=1`)
    # 傳送人選項 1 = `sorted(MAPS)[0]`（傳送點全開後由 MAPS 決定，不再硬編碼城市）
    tp_first = sorted(MAPS)[0]
    send_c2gs(C2GS_NPC_ANSWER, struct.pack("<BB", 100, 1))
    op_tp_scene, _ = recv_gs2c()
    assert op_tp_scene == GS2C_MAP_SCENE_M
    op_tp_goto, _ = recv_gs2c()
    assert op_tp_goto == GS2C_MAP_GOTO_M
    for _ in range(len(map_npc_spawn_list(tp_first))):
        op_tp_npc, _ = recv_gs2c()
        assert op_tp_npc == GS2C_MAP_ADD_NPC
    op_tp_notify, _ = recv_gs2c()
    assert op_tp_notify == GS2C_NOTIFY

    # Test 一般 NPC（原版站位）：點擊 -> 原格式對話；選項 -> 一律回「敬請期待」
    plain = next((n for n in map_npc_spawn_list(tp_first) if not is_teleporter(n)), None)
    assert plain is not None, "該場景應至少有一個非傳送人 NPC"
    send_c2gs(C2GS_MIXPACKET, struct.pack("<IBBH", new_role_id, 3, C2GS_NPC_LOOK, 4) + struct.pack("<I", plain["id"]))
    op_plain, body_plain = recv_gs2c()
    assert op_plain == GS2C_NPC_CHAT_EXT
    assert b"P N(" in body_plain, "原版對話格式：P N(icon,name) 開頭"
    assert b"Q" in body_plain, "原版對話必須帶選項（Q 開頭的行）"
    send_c2gs(C2GS_NPC_ANSWER, struct.pack("<BB", 100, 1))
    op_expect, body_expect = recv_gs2c()
    assert op_expect == GS2C_NPC_CHAT_EXT, "一般 NPC 的選項必須回對話（不是傳送）"
    assert "敬請期待".encode("big5") in body_expect, "選項回覆必須是「敬請期待」"

    # Test 查看屬性 / 屬性總覽 (`C2GS_OPEN_UI_NEW = 230` -> `GS2C_OPEN_UI_NEW = 234`)
    send_c2gs(C2GS_OPEN_UI_NEW, struct.pack("<HBB", 162, 49, 1))
    op_attr, body_attr = recv_gs2c()
    assert op_attr == GS2C_OPEN_UI_NEW and struct.unpack_from("<HB", body_attr, 0) == (8, 1)

    # Test 稱謂 (`C2GS_TITLE = 67, sub=6` -> `GS2C_OPEN_UI = 89, sub=183`)
    send_c2gs(C2GS_TITLE, b"\x06")
    op_title, body_title = recv_gs2c()
    assert op_title == GS2C_OPEN_UI and body_title[0] == 183

    # Test 召喚獸資質查看 (`C2GS_SUMMON_PROPVIEW = 129` -> `GS2C_SUMM_PROP_VIEW = 51`)
    send_c2gs(C2GS_SUMMON_PROPVIEW, struct.pack("<I", 50001))
    op_pview, _ = recv_gs2c()
    assert op_pview == GS2C_SUMM_PROP_VIEW

    # Level-up must be dispatched on the client's own opcode (152) *and* the legacy 17.
    # Each upgrade emits PROP_INIT + NOTIFY, so drain both and ignore interleaved noise.
    def upgrade_round(op: int) -> list[int]:
        send_c2gs(op, b"")
        seen: list[int] = []
        while not (GS2C_PROP_INIT in seen and GS2C_NOTIFY in seen):  # PROP_INIT + NOTIFY
            op_i, _ = recv_gs2c()
            seen.append(op_i)
            assert len(seen) < 6, f"upgrade(op={op}) produced no GS2C_PROP_INIT"
        return seen

    assert GS2C_PROP_INIT in upgrade_round(C2GS_PLAYER_UPGRADE), "upgrade(152) dispatch failed"
    assert GS2C_PROP_INIT in upgrade_round(C2GS_PLAYER_UPGRADE_LEGACY), "upgrade(17) dispatch failed"
    # A 152 packet WITH a payload is the colliding C2GS_CHECKWG and must be swallowed.
    send_c2gs(C2GS_CHECKWG, b"\x00\x01\x02\x03")
    send_c2gs(C2GS_HEART_BEAT, b"")
    op_check, _ = recv_gs2c()
    assert op_check == GS2C_HEART_BEAT, f"CHECKWG(152,payload) not swallowed: op={op_check}"

    send_c2gs(C2GS_HEART_BEAT, b"")
    op10, _ = recv_gs2c()
    assert op10 == GS2C_HEART_BEAT

    # Stage 6A: Time Sync (`C2GS_REQUEST_TIME = 61`) & Calendar/Schedule (`C2GS_OPEN_UI = 88, isub=241`, `C2GS_SCHEDULE = 82`)
    send_c2gs(C2GS_REQUEST_TIME, b"")
    op_t1, body_t1 = recv_gs2c()
    assert op_t1 == GS2C_TIME and struct.unpack_from("<I", body_t1, 0)[0] >= 10000
    op_t2, body_t2 = recv_gs2c()
    assert op_t2 == GS2C_TIME_SECOND and abs(struct.unpack_from("<I", body_t2, 0)[0] - int(time.time())) <= 5

    send_c2gs(C2GS_OPEN_UI, b"\xf1")  # isub = 241 (`nethero.C2SRefreshServerTime`)
    op_r1, body_r1 = recv_gs2c()
    assert op_r1 == GS2C_OPEN_UI and body_r1[0] == 241
    op_r2, body_r2 = recv_gs2c()
    assert op_r2 == GS2C_TIME_SECOND and abs(struct.unpack_from("<I", body_r2, 0)[0] - int(time.time())) <= 5

    send_c2gs(C2GS_SCHEDULE, b"\x01")
    op_sc_ref, _ = recv_gs2c()
    assert op_sc_ref == GS2C_OPEN_UI
    op_sc_ts, _ = recv_gs2c()
    assert op_sc_ts == GS2C_TIME_SECOND
    for expected_sub in (1, 2, 4, 7):
        op_sc, body_sc = recv_gs2c()
        assert op_sc == GS2C_SCHEDULE and body_sc[0] == expected_sub

    send_c2gs(C2GS_SCHEDULE, b"\x02")
    assert recv_gs2c()[0] == GS2C_OPEN_UI
    assert recv_gs2c()[0] == GS2C_TIME_SECOND
    op_wk, body_wk = recv_gs2c()
    assert op_wk == GS2C_OPEN_UI and body_wk[0] == 222 and body_wk[1] == 4

    # Stage 6B: System Settings Save (`C2GS_PLAYER_SYSSWITCH = 21`, `C2GS_GAME_PUBLIC = 209 sub=5`, `C2GS_HUODONG = 90`)
    send_c2gs(C2GS_PLAYER_SYSSWITCH, struct.pack("<BI", 1, 0x12345678))
    op_sys1, body_sys1 = recv_gs2c()
    assert op_sys1 == GS2C_PROP_SWITCH and body_sys1 == struct.pack("<BI", 1, 0x12345678)

    send_c2gs(C2GS_PLAYER_SYSSWITCH, struct.pack("<BI", 7, 50000000))
    op_sys7, body_sys7 = recv_gs2c()
    assert op_sys7 == GS2C_PROP_SWITCH and body_sys7 == struct.pack("<BI", 9, 50000000)

    # Split packet (`netpublic.SplitPacketSend` -> `C2GS_GAME_PUBLIC = 209, sub = 5`)
    hotkey_payload = b"\x02" + b"1:112|2:113|" * 22
    chunk0 = hotkey_payload[:200]
    chunk1 = hotkey_payload[200:]
    send_c2gs(C2GS_GAME_PUBLIC, bytes([5, 0, C2GS_PLAYER_SYSSWITCH, len(chunk0)]) + chunk0)
    send_c2gs(C2GS_GAME_PUBLIC, bytes([5, 2, len(chunk1)]) + chunk1)

    # UI Style switch (`C2GS_HUODONG = 90`, `'newchar'`, `iSub = 11`, `iStyle = 4`)
    send_c2gs(C2GS_HUODONG, b"\x07newchar\x0b\x04")
    op_hd, body_hd = recv_gs2c()
    assert op_hd == GS2C_HUODONG_OP and body_hd == b"\x07newchar\x0c\x04"

    cli.close()

    # Stage 6C: QuickLogin Reconnect (`netquicklogin.Connect` -> `RestartQuickLogin` -> `C2GS_QUICKLOGIN = 13, sub = 2`)
    cli_ql = socket.create_connection(("127.0.0.1", port), timeout=5.0)
    h_ql = cli_ql.recv(9)
    assert h_ql == hello, "QuickLogin GS2C_HELLO mismatch"
    cli_ql.sendall(compute_hello_reply_bytes(seed) + b"\x00" * 22)
    ql_fields = struct.pack("<BII", 2, login_key, new_role_id)
    cli_ql.sendall(bytes([C2GS_QUICKLOGIN, len(ql_fields) + 1]) + ql_fields + b"\x00")

    def recv_gs2c_ql() -> tuple[int, bytes]:
        b0 = cli_ql.recv(1)[0]
        if b0 == 0xFF:
            ext = cli_ql.recv(MAX_LEN_BYTES)
            plen = int.from_bytes(ext + b"\x00" * (4 - MAX_LEN_BYTES), "little")
        else:
            plen = b0
        body = b""
        while len(body) < plen:
            body += cli_ql.recv(plen - len(body))
        return body[0], body[1:]

    # First packet on QuickLogin MUST be `GS2C_QUICKLOGIN = 12, isub = 2` (`S2CLoginSuccess`)
    op_ql_ok, body_ql_ok = recv_gs2c_ql()
    assert op_ql_ok == GS2C_QUICKLOGIN and body_ql_ok == b"\x02"
    # Followed by `GS2C_PROP_INIT = 16` and full world entry
    op_ql_prop, body_ql_prop = recv_gs2c_ql()
    assert op_ql_prop == GS2C_PROP_INIT and len(body_ql_prop) == 403
    cli_ql.close()

    srv_sock.close()
    if tmp_db.exists():
        tmp_db.unlink()
    log("[PASS] All stages (選區 -> 登錄 -> 創角/選角 -> 進圖/全圖NPC載入 -> 點擊NPC對話/傳送 -> 移動/心跳/時間日曆同步/系統設置與分辨率瞬連) verified 100%!")
    return 0


# ============================================================================
# 7. CLI Entry Point
# ============================================================================


def find_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    here = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    candidates = [here, cwd, *here.parents, *cwd.parents]
    for base in [here.parent, cwd.parent, Path.home() / "Desktop", Path.home() / "Downloads"]:
        if base.exists():
            candidates.extend([base / "MXSJ_TW_2022", base / "梦想世界", base / "夢想世界"])
    for drive in ("C:/", "D:/", "E:/", "F:/"):
        dpath = Path(drive)
        if dpath.exists():
            candidates.extend([dpath / "MXSJ_TW_2022", dpath / "Games" / "MXSJ_TW_2022"])
    for cand in candidates:
        if (cand / "data" / "script.fls").exists() and (cand / "mx.exe").exists():
            return cand.resolve()
    for cand in candidates:
        if (cand / "data" / "script.fls").exists() or (cand / "mx.exe").exists():
            return cand.resolve()
    return here


def main() -> int:
    parser = argparse.ArgumentParser(
        description="《夢想世界》(MXSJ TW 2022) Local Mock Server (選區 -> 登錄 -> 創角/選角 -> 進入地圖)"
    )
    parser.add_argument(
        "--npc-layout",
        default=None,
        help="原版 NPC 佈局 JSON（預設找 mock_server.py 同目錄的 npc_layout.json "
        "或 notes/npc_dialogue_and_options/out/npc_layout.json）",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3134, help="Bind TCP port (default: 3134)")
    parser.add_argument(
        "--root",
        default=None,
        help="Path to MXSJ_TW_2022 game root directory (auto-detected if placed in game root)",
    )
    parser.add_argument(
        "--map",
        type=int,
        default=1025,
        choices=[1025, 1054, 1001, 1007, 1005, 1028],
        help="Default spawn map ID: 1025=清風村, 1054=明月城, 1001=永澤城, 1007=香葉城, 1005=天水平原, 1028=長風島 (default: 1025)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to persistent account/role JSON store (default: <repo>/mock_accounts.json)",
    )
    parser.add_argument(
        "--no-patch",
        action="store_true",
        help="Do not auto-patch data/script.fls (SetSeed bypass) on startup",
    )
    parser.add_argument(
        "--patch-client",
        action="store_true",
        help="Ensure nocheck ([game] gm=1) & patch data/script.fls SetSeed bypass, then exit",
    )
    parser.add_argument(
        "--restore-client",
        action="store_true",
        help="Restore original data/script.fls from data/script.fls.bak, then exit",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run end-to-end protocol self-test and exit",
    )
    args = parser.parse_args()

    repo_root = find_repo_root(args.root)

    layout_path = load_npc_layout(Path(args.npc_layout) if args.npc_layout else None)
    if layout_path is not None:
        total = sum(len(sc.get("npcs") or []) for sc in NPC_LAYOUT["scenes"].values())
        log(f"[NPC] 原版佈局已載入：{layout_path}（{len(NPC_LAYOUT['scenes'])} 場景 / {total} NPC）")
    else:
        log("[NPC] 未找到 npc_layout.json，沿用內建 NPC 名單（可用 --npc-layout 指定）")

    if args.self_test:
        return run_self_test()

    if args.restore_client:
        ok = patch_script_fls_setseed(repo_root, restore=True)
        return 0 if ok else 1

    if args.patch_client:
        ensure_client_ready(repo_root, patch_fls=True)
        return 0

    ensure_client_ready(repo_root, patch_fls=not args.no_patch)

    db_path = Path(args.db) if args.db else (repo_root / "mock_accounts.json")
    store = AccountStore(db_path=db_path, default_map_id=args.map)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.host, args.port))
    srv.listen(16)

    m = MAPS[args.map]
    log("=" * 72)
    log(f"《夢想世界》本地模擬伺服器已啟動！監聽於 {args.host}:{args.port}")
    log(f"預設出生場景：{m['name']} (map_id={args.map}, 座標=({m['spawn_x']}, {m['spawn_y']}))")
    log("完整支援流程：")
    log("  1. 選區：選擇【縮小燈(推薦站)】(127.0.0.1:3134) -> 自動完成 GS2C_HELLO 握手")
    log("  2. 登錄：輸入任意非純數字賬號 (如 player01) 與 >=6 位密碼 (如 123456)")
    log("  3. 角色：可直接選擇預設角色【夢想少俠】進入遊戲，或點擊【創建角色】新建角色")
    log("  4. 進圖：完整載入角色屬性與地圖場景，支援點擊傳送人 NPC 切換【清風村/明月城/永澤城】")
    log("=" * 72)

    try:
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(
                target=ClientSession(conn, addr, store, server_num=3).run,
                daemon=True,
            )
            t.start()
    except KeyboardInterrupt:
        log("Shutting down mock_server.py...")
    finally:
        srv.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
