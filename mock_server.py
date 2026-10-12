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
     - Sends `GS2C_PROP_INIT = 16` (the `ITEM_SERVERINIT` hero attributes).
       NOTE: `hero.py` (entry 3038) assigns `ITEM_ALL` and `ITEM_SERVERINIT` as
       EMPTY tuples at module level (`BUILD_TUPLE 0`) and fills them at runtime via
       `InitItem`, so neither the "97" nor the "112" figure quoted elsewhere in this
       file is a static client literal.  Count them from the registration path.
     - Sends `GS2C_MAP_SCENE_M = 96` (loads map scene `1025` 清風村 / `1054` 明月城 / `1001` 永澤城).
     - Sends `GS2C_MAP_GOTO_M = 97` (places hero at spawn grid coordinates).
     - Sends `GS2C_MAP_ADD_NPC = 99` (spawns interactive teleporter NPC on the map).
     - Sends `GS2C_NOTIFY = 165` (welcome banner in system prompt & chat window).
     - Handles `C2GS_MAP_MOVE = 54` (walking), `C2GS_HEART_BEAT = 63` -> `GS2C_HEART_BEAT = 63`,
       `C2GS_REQUEST_TIME = 61` -> `GS2C_TIME = 31`, `C2GS_NPC_LOOK = 96` -> `GS2C_NPC_CHAT_EXT = 152`,
       `C2GS_NPC_ANSWER = 98` (map teleportation), and `C2GS_PLAYER_CHAT = 149` (chat & `/tp`).
       The `*_LEGACY` aliases (109/15/55/56/123/...) are also accepted for older
       builds, but they are NOT present in the v2.27.2 client table.

Opcode provenance (verified 2026-10-12)
---------------------------------------
The authoritative C2GS/GS2C numbers are read out of the client itself:
`data/script.fls` entry **3970** = `script\\protocol.py` (module docstring "协议号",
GBK).  412 assignments, 409 integer constants (C2GS=176, GS2C=233), recovered with
**0 unmapped opcodes** over 2476 bytes of `co_code`.  Reproduce with:

    python3 work/dream-world-connect-login-map/tools/extract_protocol_table.py \
        --cross-check-mock mock_server.py

That cross-check is what flagged the constants corrected in this file; run it after
any opcode edit.  Names below that the cross-check reports as `missing_in_client`
are this project's own invention, not client facts.
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

# Client -> GameServer (C2GS) - `data/script.fls` entry 3970 (`script\protocol.py`)
C2GS_LOGIN_ACCOUNT_ENTER = 1
C2GS_LOGIN_PLAYER_ENTER = 2
C2GS_LOGIN_PLAYER_ADD = 3
C2GS_LOGIN_QUIT = 4
C2GS_LOGIN_PLAYER_DEL = 7
C2GS_PING = 8
C2GS_PROP_NEWPOINT = 17
C2GS_PLAYER_SWITCH = 18
C2GS_PLAYER_SYSSWITCH = 21
C2GS_TIME = 31
C2GS_SELECT_SERVER = 41
C2GS_TASK_GET = 48
C2GS_TASK = 49
C2GS_MAP_MOVE = 54
C2GS_SYN_DIREMOTE = 55
C2GS_REQUEST_TIME = 61
C2GS_ANSWERHELLO = 62
C2GS_HEART_BEAT = 63
C2GS_OPEN_UI = 88
C2GS_NPC_LOOK = 96
C2GS_NPC_COMMAND = 97
C2GS_NPC_ANSWER = 98
C2GS_NPC_RBCLICK = 108
C2GS_NPC_INPUT = 115
C2GS_PLAYER_CHAT = 149
C2GS_MIXPACKET = 151
C2GS_CHECKWG = 152
C2GS_PLAYER_CMD = 153
C2GS_GAME_PUBLIC = 209

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

# GameServer -> Client (GS2C) - `data/script.fls` entry 3970 (`script\protocol.py`)
GS2C_HELLO = 1
GS2C_LOGIN_PLAYER_INFO = 3
GS2C_LOGIN_PLAYER_ENTER = 4
GS2C_LOGIN_PLAYER_ADD = 6
GS2C_LOGIN_ERROR = 8
GS2C_LOGIN_PLAYER_DEL = 10
# NOTE (2026-10-12, corrected against the client): the three constants below were
# invented and are NOT in `data/script.fls` entry 3970 (`script\protocol.py`).
# Values 14 / 17 belong to GS2C_BLACKLIST and nothing at all respectively.
# Authoritative table: work/dream-world-connect-login-map/artifacts/protocol_table/
# protocol_opcodes.csv  (regenerate with tools/extract_protocol_table.py)
GS2C_LOGIN_PLAYER_INFO_END = 14   # WRONG in client: 14 = GS2C_BLACKLIST. Unused here.
GS2C_LOGIN_ACCOUNT_INFO = 15
GS2C_PROP_INIT = 16
GS2C_PROP_CHANGE = 152            # was 17; 17 is unused in the client table.
# CAUTION: the client's own table assigns 152 to BOTH GS2C_PROP_CHANGE and
# GS2C_NPC_CHAT_EXT.  Whichever the client registers last in m_NetFunction wins,
# so one of the two is unreachable.  Needs a real-client run to confirm which.
GS2C_TIME = 31
GS2C_TIME_LEGACY = 12
GS2C_SELSERVER = 47
GS2C_SELSERVER_LEGACY = 45
GS2C_HEART_BEAT = 63
GS2C_HEART_BEAT_LEGACY = 69
GS2C_MAP_SCENE_M = 96
GS2C_MAP_GOTO_M = 97
GS2C_MAP_ADD_PLAYER = 98
GS2C_MAP_ADD_NPC = 99
GS2C_MAP_DEL = 85                 # was 100; 100 = GS2C_MAP_ADD_GOODS. Unused here.
GS2C_MAP_EFFECT = 102
GS2C_NPC_CHAT = 144
GS2C_NPC_CHAT_EXT = 152
GS2C_NOTIFY_EXT = 164
GS2C_NOTIFY = 165
GS2C_PLAYER_CHAT = 167
GS2C_MESSAGE = 169
GS2C_GAME_PUBLIC = 209

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
    if not nocheck_path.exists():
        nocheck_path.write_bytes(b"")
        log(f"[OK] Created {nocheck_path} (enables GetSpecialVersion() local/GM mode)")
    else:
        log(f"[OK] Found {nocheck_path} (GetSpecialVersion() == True)")

    if patch_fls:
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


MAX_LEN_BYTES = 2  # CNetClient +0x6990; see frame_gs2c docstring for the evidence.


def frame_gs2c(opcode: int, payload: bytes = b"") -> bytes:
    """
    Wraps a GS2C packet for `CNetClient::RecvPacket` (`0x004ab540`):
      - `body = bytes([opcode]) + payload`
      - If `len(body) < 0xFF`: `bytes([len(body)]) + body`
      - If `len(body) >= 0xFF`: `b'\\xff' + <len(body) as MaxLenBytes little-endian> + body`

    `MaxLenBytes` is **2**, not 3.  Verified 2026-10-12 by disassembling `mx.exe`:
      - `0x4ab540` state 0 reads 1 length byte into `+0x6988`;
      - state 1 compares it to `0xFF` and, on match, calls `ReadBytes(&+0x6988,
        [+0x6990])` — i.e. it reads exactly `MaxLenBytes` continuation bytes;
      - a whole-binary scan finds exactly ONE write to `+0x6990`, at `0x4AB23F`:
        `c7 87 90 69 00 00 02 00 00 00` = `mov dword ptr [edi+0x6990], 2`.
    Writing 3 length bytes left a stray `0x00` at the head of the body, so the
    client read cmd=0x00 and desynced.  Only packets with a body >= 0xFF bytes are
    affected; in this build that is `GS2C_PROP_INIT` (body 404).
    """
    body = bytes([opcode & 0xFF]) + payload
    n = len(body)
    if n < 0xFF:
        return bytes([n]) + body
    if n >= 1 << (8 * MAX_LEN_BYTES):
        raise ValueError(
            f"body {n}B does not fit in MaxLenBytes={MAX_LEN_BYTES}; the client "
            "cannot frame it (split the packet instead)")
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
      - `Shape`: 2B LE (1..12 valid player shapes)
      - `Desc`: 2B LE (color bits)
      - `Level`: 1B
      - `School`: 1B (0=戰士, 1=法師, 2=術士)
      - `Race`: 1B
      - `iPrepareLoad`: 1B (0 or 1)
      - `Point`: 4B LE
      - `Name`: 16B Big5 NUL-padded string
    Total payload = 37 bytes (38 bytes including opcode).
    """
    name_b = encode_big5(role.get("name", "夢想少俠"), 16)
    payload = (
        struct.pack(
            "<IIBHHBBBBI",
            int(role.get("id", 10001)) & 0xFFFFFFFF,
            int(role.get("time", int(time.time()))) & 0xFFFFFFFF,
            int(role.get("icon", 1)) & 0xFF,
            int(role.get("shape", 1)) & 0xFFFF,
            int(role.get("color", 0)) & 0xFFFF,
            int(role.get("level", 60)) & 0xFF,
            int(role.get("school", 1)) & 0xFF,
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
    shape = int(role.get("shape", 1)) & 0xFFFF
    icon = int(role.get("icon", 1)) & 0xFF
    school = int(role.get("school", 1)) & 0xFF
    cash = int(role.get("cash", 888888))
    name_20 = encode_big5(role.get("name", "夢想少俠"), 20)
    org_20 = encode_big5(role.get("faction", "清風明月幫"), 20)
    title_60 = encode_big5(role.get("title", "夢想開拓者"), 60)
    fake_name_20 = encode_big5("", 20)

    buf = bytearray()
    # 1. iPlayerRealID (4B), iPlayerShowID (4B), iPrettyID (4B) -> 12 bytes
    buf.extend(struct.pack("<III", role_id, role_id, 0))

    # 2. All 112 ITEM_SERVERINIT fields in exact `script/hero.py` order (391 bytes):
    # [000] m_Icon(1B), [001] m_Shape(2B), [002] m_Desc(TDESC=1B:0), [003] m_Sex(1B)
    buf.extend(struct.pack("<BHBB", icon, shape, 0, 1))
    # [004] m_Name(20B)
    buf.extend(name_20)
    # [005] m_Grade(1B), [006] m_Cash(8B), [007] m_Saving(4B), [008] m_Exp(4B),
    # [009] m_NextExp(4B), [010] m_NeedExp(4B), [011] m_Class(1B), [012] m_Country(1B: 1=南遙國)
    buf.extend(struct.pack("<BQIIIIBB", level, cash, 1000000, 50000, 100000, 100000, school, 1))
    # [013] sOrg(20B), [014] m_OrgID(4B), [015] m_EmoteForTitle(2B), [016] m_Title(60B), [017] m_TitleID(2B)
    buf.extend(org_20)
    buf.extend(struct.pack("<IH", 1, 0))
    buf.extend(title_60)
    buf.extend(struct.pack("<H", 0))
    # [018..025] m_HP(2B), m_HPMax(2B), m_MP(2B), m_MPMax(2B), m_FP(2B), m_FPMax(2B), m_SP(2B), m_SPMax(2B)
    buf.extend(struct.pack("<HHHHHHHH", 3500, 3500, 2500, 2500, 100, 100, 100, 150))
    # [026..029] m_Huoli(4B), m_Huoli_Max(2B), m_Tili(4B), m_Tili_Max(2B)
    buf.extend(struct.pack("<IHIH", 500, 500, 500, 500))
    # [030..039] m_Att_All, m_Def_All, m_Spe_All, m_Magdef_All, m_Str_All, m_Mag_All, m_Cha_All, m_Dex_All, m_Con_All, m_Point (10 x 2B)
    buf.extend(struct.pack("<HHHHHHHHHH", 1200, 950, 480, 920, 140, 150, 130, 130, 120, 50))
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
    buf.extend(struct.pack("<7B", 8, 2, 1, 0, 150, 1, 0))
    # [065] m_RealShape(2B), [066] m_XiulianTotalNeed(1B), [067] m_PhotoEffect(4B), [068] m_IsGuestLogin(4B)
    buf.extend(struct.pack("<HBII", shape, 0, 0, 0))
    # [069] m_NameColor(1B), [070] m_IsMarried(1B), [071] m_Birthday(2B), [072] m_AutoUpgrade(1B), [073] m_IsDYT(1B)
    buf.extend(struct.pack("<BBHBB", 0, 0, 101, 0, 0))
    # [074] m_Liupai(2B), [075] m_SecondLiupai(2B)
    buf.extend(struct.pack("<HH", 1, 0))
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
    """`GS2C_TIME = 31` (or legacy `12`) -> `mxgw.S2CTime(netobj)` (`t = netobj.UnpackInt(4)`)."""
    op = GS2C_TIME_LEGACY if legacy else GS2C_TIME
    t_ticks = int(time.time() * 10) & 0xFFFFFFFF
    return frame_gs2c(op, struct.pack("<I", t_ticks))


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
            "shape": 1,
            "color": 0,
            "level": 60,
            "school": 1,
            "race": 1,
            "point": 200,
            "cash": 888888,
            "map_id": self.default_map_id,
            "x": m["spawn_x"],
            "y": m["spawn_y"],
            "time": int(time.time()),
        }

    def _load(self) -> None:
        if self.db_path.exists():
            try:
                self.data = json.loads(self.db_path.read_text(encoding="utf-8"))
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
    ) -> dict[str, Any]:
        with self.lock:
            acct = self.data["accounts"].setdefault(account, {"md5_pass": "", "roles": []})
            role_id = int(self.data.get("next_role_id", 10002))
            self.data["next_role_id"] = role_id + 1
            m = MAPS[self.default_map_id]
            new_role = {
                "id": role_id,
                "name": name or f"少俠{role_id}",
                "icon": icon if icon > 0 else 1,
                "shape": shape if 1 <= shape <= 12 else 1,
                "color": color,
                "level": 10,
                "school": major if major in (0, 1, 2) else 0,
                "race": 1,
                "point": 50,
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

    def update_role_pos(self, account: str, role_id: int, map_id: int, x: int, y: int) -> None:
        with self.lock:
            acct = self.data["accounts"].get(account)
            if not acct:
                return
            for r in acct["roles"]:
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
        self.recv_buf = bytearray()
        self.hello_verified = False

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
        if opcode in (C2GS_REQUEST_TIME, C2GS_TIME, C2GS_REQUEST_TIME_LEGACY):
            is_legacy = opcode == C2GS_REQUEST_TIME_LEGACY
            log(f"[C2GS <- {self.addr[1]}] C2GS_REQUEST_TIME (op={opcode})")
            self.send_raw(
                build_gs2c_time(legacy=is_legacy),
                f"GS2C_TIME(op={GS2C_TIME_LEGACY if is_legacy else GS2C_TIME})",
            )
            return

        # 3. Ping & Quiet In-Map State Packets
        if opcode in (
            C2GS_PING,
            C2GS_PING_LEGACY,
            C2GS_PLAYER_SWITCH,
            C2GS_PLAYER_SYSSWITCH,
            C2GS_TASK_GET,
            C2GS_TASK,
            C2GS_ANSWERHELLO,
            C2GS_OPEN_UI,
            C2GS_CHECKWG,
            C2GS_PLAYER_CMD,
        ):
            return

        # 4. `C2GS_GAME_PUBLIC = 209` (`script.fls`) or `250` (`data.fls`)
        if opcode in (C2GS_GAME_PUBLIC, C2GS_GAME_PUBLIC_LEGACY):
            sub = fields[0] if fields else 0
            log(
                f"[C2GS <- {self.addr[1]}] C2GS_GAME_PUBLIC (op={opcode}, sub={sub}, "
                f"len={len(fields)}B)"
            )
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
        self.active_role = role

        # 1. Send GS2C_PROP_INIT = 16 (initializes hero.g_Prop and switches gamectrl to GAMING)
        prop_pkt = build_gs2c_prop_init(role)
        self.send_raw(
            prop_pkt,
            f"GS2C_PROP_INIT(op=16, id={role['id']}, name={role['name']!r}, lv={role['level']})",
        )

        # 2. Enter map scene (GS2C_MAP_SCENE_M = 96 + GS2C_MAP_GOTO_M = 97 + GS2C_MAP_ADD_NPC = 99)
        map_id = int(role.get("map_id", self.store.default_map_id))
        if map_id not in MAPS:
            map_id = 1025
        x = int(role.get("x", MAPS[map_id]["spawn_x"]))
        y = int(role.get("y", MAPS[map_id]["spawn_y"]))
        self.enter_map(map_id, x, y, send_welcome=True)

    def enter_map(self, map_id: int, x: int | None = None, y: int | None = None, send_welcome: bool = False) -> None:
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
        npc_list = m.get("npcs") or ([m["npc"]] if m.get("npc") else [])
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
    # In-Map NPC Dialog & Slash Commands
    # ------------------------------------------------------------------------
    def _on_npc_look(self, npc_id: int) -> None:
        cur_map_id = int(self.active_role.get("map_id", 1025)) if self.active_role else 1025
        m = MAPS.get(cur_map_id, MAPS[1025])
        npc = m["npc"]
        for cand in m.get("npcs", []):
            if int(cand.get("id", 0)) == npc_id:
                npc = cand
                break

        greeting = npc.get(
            "greeting",
            f"少俠好！這裡是#Y{m['name']}#n，我是#G{npc['name']}#n，請問有什麼可以幫您？",
        )
        dialog_text = (
            f"{greeting}\n"
            f"Q傳送至【明月城】(1054)\n"
            f"Q傳送至【清風村】(1025)\n"
            f"Q傳送至【永澤城】(1001)\n"
            f"Q傳送至【香葉城】(1007)\n"
            f"Q傳送至【天水平原】(1005)\n"
            f"Q傳送至【長風島】(1028)\n"
            f"Q恢復滿氣血法力並領取 100 萬兩銀幣\n"
            f"Q角色連升 10 級 (刷新全屬性)\n"
            f"Q我只是路過"
        )
        pkt = build_gs2c_npc_chat_ext(
            npc_id=npc_id,
            icon=int(npc.get("icon", npc.get("shape", 3007))),
            name=str(npc.get("name", "傳送人")),
            msg=dialog_text,
            response_id=100,
        )
        self.send_raw(pkt, f"GS2C_NPC_CHAT_EXT(op=152, id={npc_id}, npc={npc['name']!r})")

    def _on_npc_answer(self, choice: int, response_id: int) -> None:
        tp_targets = {
            1: (1054, "明月城"),
            2: (1025, "清風村"),
            3: (1001, "永澤城"),
            4: (1007, "香葉城"),
            5: (1005, "天水平原"),
            6: (1028, "長風島"),
        }
        if choice in tp_targets:
            target_id, target_name = tp_targets[choice]
            self.enter_map(target_id)
            self.send_raw(
                build_gs2c_notify(f"#G已為您傳送至【{target_name}】({target_id})！#n", sub=2),
                "GS2C_NOTIFY",
            )
        elif choice == 7:
            if self.active_role:
                self.active_role["cash"] = int(self.active_role.get("cash", 888888)) + 1000000
                self.send_raw(build_gs2c_prop_init(self.active_role), "GS2C_PROP_INIT(op=16, heal+cash)")
            self.send_raw(
                build_gs2c_notify("#Y氣血與法力已完全恢復，並獲得 1,000,000 兩銀幣！#n", sub=2),
                "GS2C_NOTIFY",
            )
        elif choice == 8:
            if self.active_role:
                new_lv = min(165, int(self.active_role.get("level", 60)) + 10)
                self.active_role["level"] = new_lv
                self.active_role["point"] = int(self.active_role.get("point", 200)) + 50
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
        if head == "/pos" and self.active_role:
            msg = (
                f"當前角色：{self.active_role['name']} (ID={self.active_role['id']}) "
                f"地圖：{self.active_role.get('map_id')} 座標：({self.active_role.get('x')}, {self.active_role.get('y')})"
            )
            self.send_raw(build_gs2c_notify(msg, sub=2), "GS2C_NOTIFY")
            return
        self.send_raw(
            build_gs2c_notify(
                "可用指令：#Y/tp 1054#n (明月城)、#Y/tp 1025#n (清風村)、#Y/tp 1001#n (永澤城)、#Y/tp 1007#n (香葉城)、#Y/tp 1005#n (天水平原)、#Y/tp 1028#n (長風島)、#Y/pos#n",
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

    # 4. GS2C_PROP_INIT (407 bytes total: 0xFF + 2B len(404) + op(16) + 403B payload)
    #    MaxLenBytes is 2 -- see frame_gs2c for the mx.exe 0x4AB23F evidence.
    prop_pkt = build_gs2c_prop_init(sample_role)
    assert prop_pkt[0] == 0xFF
    ext_len = int.from_bytes(prop_pkt[1:3], "little")
    assert ext_len == 404 and len(prop_pkt) == 3 + 404 and prop_pkt[3] == GS2C_PROP_INIT

    # 4b. Framing regression: the 0xFF escape must be exactly 2 length bytes, and
    #     the byte right after them must be the command byte (not a stray 0x00).
    esc = frame_gs2c(99, b"\xAA" * 299)
    assert esc[0] == 0xFF and len(esc) == 1 + MAX_LEN_BYTES + 300
    assert int.from_bytes(esc[1:1 + MAX_LEN_BYTES], "little") == 300
    assert esc[1 + MAX_LEN_BYTES] == 99, "client would read cmd=0x00 and desync"
    assert frame_gs2c(1, b"\x00" * 8) == bytes([9, 1]) + b"\x00" * 8

    # 5. GS2C_MAP_SCENE_M & GS2C_MAP_GOTO_M & GS2C_MAP_ADD_NPC
    scene_pkt = build_gs2c_map_scene_m(1025, 1025, 1025, 75, 52, "清風村")
    assert scene_pkt[1] == GS2C_MAP_SCENE_M
    goto_pkt = build_gs2c_map_goto_m(75, 52)
    assert len(goto_pkt) == 6 and goto_pkt[0] == 5 and goto_pkt[1] == GS2C_MAP_GOTO_M
    npc_pkt = build_gs2c_map_add_npc(MAPS[1025]["npc"])
    assert npc_pkt[1] == GS2C_MAP_ADD_NPC

    # 6. End-to-end loopback socket test across all 4 stages
    tmp_db = Path("/tmp/test_mock_accounts.json")
    if tmp_db.exists():
        tmp_db.unlink()
    store = AccountStore(tmp_db, default_map_id=1025)

    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind(("127.0.0.1", 0))
    srv_sock.listen(1)
    port = srv_sock.getsockname()[1]

    def _srv_thread() -> None:
        conn, addr = srv_sock.accept()
        sess = ClientSession(conn, addr, store, seed=seed, server_num=3)
        sess.run()

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

    # Helper to read one GS2C frame (MaxLenBytes = 2, see frame_gs2c)
    def recv_gs2c() -> tuple[int, bytes]:
        b0 = cli.recv(1)[0]
        if b0 == 0xFF:
            ext = cli.recv(MAX_LEN_BYTES)
            plen = int.from_bytes(ext, "little")
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
    op6, body6 = recv_gs2c()
    assert op6 == GS2C_MAP_SCENE_M
    op7, body7 = recv_gs2c()
    assert op7 == GS2C_MAP_GOTO_M
    expected_npcs = len(MAPS[1025]["npcs"])
    for _ in range(expected_npcs):
        op_npc, _ = recv_gs2c()
        assert op_npc == GS2C_MAP_ADD_NPC
    op9, body9 = recv_gs2c()
    assert op9 == GS2C_NOTIFY

    # Stage 5: Walk in map (`C2GS_MAP_MOVE = 54`), Click NPC (`C2GS_MIXPACKET = 151` wrapping `C2GS_NPC_LOOK = 96`),
    # Select Teleport Option (`C2GS_NPC_ANSWER = 98`), and Heartbeat (`C2GS_HEART_BEAT = 63`)
    send_c2gs(C2GS_MAP_MOVE, struct.pack("<HHBB", 75, 52, 1, 1))
    # Test C2GS_MIXPACKET = 151 wrapping C2GS_NPC_LOOK = 96
    inner_look = struct.pack("<I", 50001)
    mix_payload = struct.pack("<IBBH", new_role_id, 3, C2GS_NPC_LOOK, len(inner_look)) + inner_look
    send_c2gs(C2GS_MIXPACKET, mix_payload)
    op_chat, _ = recv_gs2c()
    assert op_chat == GS2C_NPC_CHAT_EXT

    # Test C2GS_NPC_ANSWER = 98 (2-byte `responseID=100, choice=1` -> teleport to 明月城 1054)
    send_c2gs(C2GS_NPC_ANSWER, struct.pack("<BB", 100, 1))
    op_tp_scene, _ = recv_gs2c()
    assert op_tp_scene == GS2C_MAP_SCENE_M
    op_tp_goto, _ = recv_gs2c()
    assert op_tp_goto == GS2C_MAP_GOTO_M
    for _ in range(len(MAPS[1054]["npcs"])):
        op_tp_npc, _ = recv_gs2c()
        assert op_tp_npc == GS2C_MAP_ADD_NPC
    op_tp_notify, _ = recv_gs2c()
    assert op_tp_notify == GS2C_NOTIFY

    send_c2gs(C2GS_HEART_BEAT, b"")
    op10, _ = recv_gs2c()
    assert op10 == GS2C_HEART_BEAT

    cli.close()
    srv_sock.close()
    if tmp_db.exists():
        tmp_db.unlink()
    log("[PASS] All stages (選區 -> 登錄 -> 創角/選角 -> 進圖/全圖NPC載入 -> 點擊NPC對話/傳送 -> 移動/心跳) verified 100%!")
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
        help="Ensure nocheck & patch data/script.fls SetSeed bypass, then exit",
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
