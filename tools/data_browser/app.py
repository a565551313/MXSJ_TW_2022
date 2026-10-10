#!/usr/bin/env python3
"""
MXSJ Game Data Browser
Interactive Web & CLI Interface for exploring extracted Dream World game data tables.
"""

import http.server
import socketserver
import json
import sqlite3
import os
import sys
import urllib.parse

PORT = 8080
DB_PATH = os.path.join(os.path.dirname(__file__), "../data-export/game_data.sqlite")

def query_db(table, search=""):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    if table == "equipment":
        if search:
            cur.execute("SELECT * FROM equipment WHERE name LIKE ? OR type LIKE ? OR base_attr LIKE ?",
                        (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cur.execute("SELECT * FROM equipment ORDER BY level, id")
    elif table == "scenes":
        if search:
            cur.execute("SELECT * FROM scenes WHERE scene_name LIKE ? OR category LIKE ?",
                        (f"%{search}%", f"%{search}%"))
        else:
            cur.execute("SELECT * FROM scenes ORDER BY scene_id")
    elif table == "npc_dialogs":
        if search:
            cur.execute("SELECT * FROM npc_dialogs WHERE content LIKE ?", (f"%{search}%",))
        else:
            cur.execute("SELECT * FROM npc_dialogs ORDER BY dialog_id")
    elif table == "reward_gifts":
        if search:
            cur.execute("SELECT * FROM reward_gifts WHERE gift_name LIKE ?", (f"%{search}%",))
        else:
            cur.execute("SELECT * FROM reward_gifts ORDER BY gift_id")
    elif table == "skills":
        if search:
            cur.execute("SELECT * FROM skills WHERE class_type LIKE ? OR target_type LIKE ?",
                        (f"%{search}%", f"%{search}%"))
        else:
            cur.execute("SELECT * FROM skills ORDER BY skill_id")
    else:
        return []

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>夢想世界 (MXSJ) 遊戲數據瀏覽器</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --accent: #38bdf8;
            --text: #f8fafc;
            --muted: #94a3b8;
            --border: #334155;
            --header-bg: #1e293b;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }
        h1 {
            font-size: 24px;
            margin: 0;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .badge {
            background: #0284c7;
            font-size: 12px;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab-btn {
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .tab-btn:hover {
            border-color: var(--accent);
        }
        .tab-btn.active {
            background: var(--accent);
            color: #0f172a;
            border-color: var(--accent);
            font-weight: bold;
        }
        .search-box {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px 16px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 6px;
            font-size: 14px;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
        }
        .table-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: left;
        }
        th {
            background: #273549;
            color: var(--accent);
            padding: 12px 16px;
            font-weight: 600;
            border-bottom: 1px solid var(--border);
        }
        td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text);
        }
        tr:last-child td {
            border-bottom: none;
        }
        tr:hover {
            background: rgba(56, 189, 248, 0.05);
        }
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 8px;
        }
        .stat-val {
            font-size: 22px;
            font-weight: bold;
            color: var(--accent);
            margin-top: 4px;
        }
        .stat-label {
            font-size: 12px;
            color: var(--muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚔️ 夢想世界 (MXSJ) 遊戲數據瀏覽器 <span class="badge">Task D Live Browser</span></h1>
            <div style="font-size: 13px; color: var(--muted);">Data Source: script.fls & skill.fls (Decrypted)</div>
        </header>

        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-label">武器防具裝備總數</div>
                <div class="stat-val" id="stat-equip">30 件</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">註冊地圖/場景總數</div>
                <div class="stat-val" id="stat-scene">57 個</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">NPC 隨機台詞庫</div>
                <div class="stat-val" id="stat-npc">40 條</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">流派招式與法術</div>
                <div class="stat-val" id="stat-skill">50+ 門</div>
            </div>
        </div>

        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('equipment')">🗡️ 武器與防具裝備 (Equipment)</button>
            <button class="tab-btn" onclick="switchTab('scenes')">🗺️ 地圖與場景劃分 (Scenes)</button>
            <button class="tab-btn" onclick="switchTab('skills')">✨ 戰鬥招式與流派 (Skills)</button>
            <button class="tab-btn" onclick="switchTab('npc_dialogs')">💬 NPC 經典互動語錄 (NPC Chat)</button>
            <button class="tab-btn" onclick="switchTab('reward_gifts')">🎁 坐騎與珍品禮包 (Gifts)</button>
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="搜索道具名稱、裝備類型、屬性加成、場景名稱..." oninput="handleSearch()">
        </div>

        <div class="table-card">
            <table id="dataTable">
                <thead>
                    <tr id="tableHead"></tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>

    <script>
        let currentTab = 'equipment';
        let searchTimer = null;

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('searchInput').value = '';
            loadData();
        }

        function handleSearch() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                loadData();
            }, 250);
        }

        async function loadData() {
            const search = encodeURIComponent(document.getElementById('searchInput').value);
            const res = await fetch(`/api/data?table=${currentTab}&search=${search}`);
            const data = await res.json();
            renderTable(data);
        }

        function renderTable(data) {
            const thead = document.getElementById('tableHead');
            const tbody = document.getElementById('tableBody');
            thead.innerHTML = '';
            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--muted); padding: 32px;">查無相關遊戲數據</td></tr>';
                return;
            }

            const headers = Object.keys(data[0]);
            headers.forEach(h => {
                const th = document.createElement('th');
                th.innerText = h.toUpperCase();
                thead.appendChild(th);
            });

            data.forEach(row => {
                const tr = document.createElement('tr');
                headers.forEach(h => {
                    const td = document.createElement('td');
                    td.innerText = row[h];
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
        }

        loadData();
    </script>
</body>
</html>
"""

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif url.path == "/api/data":
            query = urllib.parse.parse_qs(url.query)
            table = query.get("table", ["equipment"])[0]
            search = query.get("search", [""])[0]
            data = query_db(table, search)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

def run_server():
    server_address = ("0.0.0.0", PORT)
    with socketserver.TCPServer(server_address, RequestHandler) as httpd:
        print(f"[*] Live Browser server listening on http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        table = sys.argv[2] if len(sys.argv) > 2 else "equipment"
        search = sys.argv[3] if len(sys.argv) > 3 else ""
        items = query_db(table, search)
        print(f"=== MXSJ Game Data: {table.upper()} (Found {len(items)}) ===")
        for it in items[:25]:
            print(it)
    else:
        run_server()
