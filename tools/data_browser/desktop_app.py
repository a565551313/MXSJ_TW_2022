#!/usr/bin/env python3
"""
MXSJ Game Data Browser - Desktop GUI / Native TUI Application
Can run as:
  1. Desktop GUI (Tkinter) when running on local Windows / Mac / Linux desktop with display.
  2. Desktop Terminal TUI (Interactive Curses/Terminal GUI) when running inside terminal/SSH.
"""

import sys
import os
import sqlite3
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "../data-export/game_data.sqlite")

def get_data(table, query=""):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if table == "equipment":
        if query:
            cur.execute("SELECT * FROM equipment WHERE name LIKE ? OR type LIKE ? OR base_attr LIKE ?",
                        (f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            cur.execute("SELECT * FROM equipment ORDER BY level, id")
    elif table == "scenes":
        if query:
            cur.execute("SELECT * FROM scenes WHERE scene_name LIKE ? OR category LIKE ?",
                        (f"%{query}%", f"%{query}%"))
        else:
            cur.execute("SELECT * FROM scenes ORDER BY scene_id")
    elif table == "skills":
        if query:
            cur.execute("SELECT * FROM skills WHERE class_type LIKE ? OR target_type LIKE ?",
                        (f"%{query}%", f"%{query}%"))
        else:
            cur.execute("SELECT * FROM skills ORDER BY skill_id")
    elif table == "npc_dialogs":
        if query:
            cur.execute("SELECT * FROM npc_dialogs WHERE content LIKE ?", (f"%{query}%",))
        else:
            cur.execute("SELECT * FROM npc_dialogs ORDER BY dialog_id")
    elif table == "reward_gifts":
        if query:
            cur.execute("SELECT * FROM reward_gifts WHERE gift_name LIKE ?", (f"%{query}%",))
        else:
            cur.execute("SELECT * FROM reward_gifts ORDER BY gift_id")
    else:
        return []
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def run_tkinter_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title("夢想世界 (MXSJ) 遊戲數據桌面瀏覽器")
    root.geometry("980x640")
    root.minsize(800, 500)

    # Styling
    style = ttk.Style()
    style.theme_use("clam")

    # Top Toolbar
    top_frame = ttk.Frame(root, padding=10)
    top_frame.pack(fill=tk.X)

    ttk.Label(top_frame, text="數據模塊:").pack(side=tk.LEFT, padx=(0, 5))
    table_var = tk.StringVar(value="equipment")
    table_combo = ttk.Combobox(top_frame, textvariable=table_var, state="readonly", width=18)
    table_combo["values"] = ("equipment", "scenes", "skills", "npc_dialogs", "reward_gifts")
    table_combo.pack(side=tk.LEFT, padx=5)

    ttk.Label(top_frame, text="搜索:").pack(side=tk.LEFT, padx=(15, 5))
    search_var = tk.StringVar()
    search_entry = ttk.Entry(top_frame, textvariable=search_var, width=25)
    search_entry.pack(side=tk.LEFT, padx=5)

    # Treeview for Table
    table_frame = ttk.Frame(root, padding=10)
    table_frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_rowconfigure(0, weight=1)

    # Status Bar
    status_var = tk.StringVar(value="就緒")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W, padding=4)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def refresh_data(*args):
        table = table_var.get()
        query = search_var.get().strip()
        data = get_data(table, query)

        # Clear existing
        tree.delete(*tree.get_children())
        tree["columns"] = []

        if not data:
            status_var.set(f"表 [{table}] 無數據或無匹配結果")
            return

        cols = list(data[0].keys())
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col.upper())
            tree.column(col, width=130, anchor=tk.W)

        for row in data:
            tree.insert("", tk.END, values=[row[c] for c in cols])

        status_var.set(f"已加載表 [{table}] 共 {len(data)} 條記錄")

    search_entry.bind("<KeyRelease>", refresh_data)
    table_combo.bind("<<ComboboxSelected>>", refresh_data)
    ttk.Button(top_frame, text="查詢", command=refresh_data).pack(side=tk.LEFT, padx=5)

    refresh_data()
    root.mainloop()

def run_terminal_tui():
    """Terminal-based interactive desktop browser (no X11 required)"""
    tables = ["equipment", "scenes", "skills", "npc_dialogs", "reward_gifts"]
    curr_tab_idx = 0
    query = ""

    while True:
        curr_table = tables[curr_tab_idx]
        data = get_data(curr_table, query)
        
        print("\033c", end="") # clear screen
        print("================================================================================")
        print("          夢想世界 (MXSJ) 遊戲數據終端桌面瀏覽器 (TUI Desktop Edition)          ")
        print("================================================================================")
        print(" [數據表標籤]: ", end="")
        for i, t in enumerate(tables):
            if i == curr_tab_idx:
                print(f"[\033[1;32m{i+1}. {t.upper()}\033[0m] ", end="")
            else:
                print(f"{i+1}. {t} ", end="")
        print("\n--------------------------------------------------------------------------------")
        print(f" 當前搜索關鍵字: '{query}' | 總記錄數: {len(data)}")
        print("--------------------------------------------------------------------------------")

        if not data:
            print("  (無匹配數據)")
        else:
            cols = list(data[0].keys())
            header_line = " | ".join(f"{c.upper():<12}" for c in cols[:5])
            print(" " + header_line)
            print(" " + "-" * min(78, len(header_line) + 4))
            for row in data[:18]:
                vals = [str(row[c])[:15] for c in cols[:5]]
                print(" " + " | ".join(f"{v:<12}" for v in vals))
            if len(data) > 18:
                print(f" ... 還有 {len(data)-18} 條記錄未完全展開")

        print("================================================================================")
        print(" 操作指令: [1-5] 切換表 | [s 關鍵字] 搜索 | [c] 清除搜索 | [q] 退出")
        print("================================================================================")
        try:
            cmd = input(" 請輸入命令 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出瀏覽器。")
            break

        if cmd.lower() == 'q':
            print("再見！")
            break
        elif cmd in ('1', '2', '3', '4', '5'):
            curr_tab_idx = int(cmd) - 1
            query = ""
        elif cmd.startswith("s "):
            query = cmd[2:].strip()
        elif cmd.lower() == 'c':
            query = ""

def main():
    # If tkinter is available and DISPLAY is set, launch Tkinter GUI
    if "DISPLAY" in os.environ:
        try:
            import tkinter
            run_tkinter_gui()
            return
        except Exception:
            pass
    # Otherwise run terminal interactive TUI
    run_terminal_tui()

if __name__ == "__main__":
    main()
