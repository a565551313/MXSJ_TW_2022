#!/usr/bin/env python3
"""Offline desktop GUI for the recovered MXSJ maps (Tkinter 8.6+).

No network, no client writes. Requires Python's tkinter package for the desktop
window; use map_gui_html.py for an offline browser GUI on headless machines.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from map_parser import parse_map
from map_viewer import build_grid

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parents[2]
ZOOMS = (0.25, 0.5, 1.0, 2.0)


def cell_at(grid: list[list[int]], x: int, y: int, width: int, height: int) -> int | None:
    """Fast, zero-based raw LLEC lookup in logical pixel coordinates."""
    if x < 0 or y < 0 or x >= width or y >= height:
        return None
    row, col = y // 20, x // 20
    if row >= len(grid) or col >= len(grid[row]):
        return None
    return grid[row][col]


def records_at(records: list[dict], x: int, y: int) -> list[int]:
    result = []
    for record in records:
        box = record["bounds_px"]
        if box["x"] <= x < box["x"] + box["width"] and box["y"] <= y < box["y"] + box["height"]:
            result.append(record["index"])
    return result


def cell_runs(grid: list[list[int]], width: int, height: int):
    """Yield (x, y, run_width, raw_byte) for nonzero values within logical bounds."""
    for row_idx, row in enumerate(grid):
        y = row_idx * 20
        if y >= height:
            break
        col = 0
        while col < len(row) and col * 20 < width:
            value = row[col]
            end = col + 1
            while end < len(row) and end * 20 < width and row[end] == value:
                end += 1
            if value:
                yield col * 20, y, min((end - col) * 20, width - col * 20), value
            col = end


def discover(map_dir: Path, texture_dir: Path) -> dict[str, tuple[Path, Path]]:
    return {p.stem: (p, texture_dir / (p.stem + ".png"))
            for p in sorted(map_dir.glob("*.map")) if (texture_dir / (p.stem + ".png")).is_file()}


def launch(map_dir: Path, texture_dir: Path, initial: str | None = None) -> None:
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
    except ImportError as exc:
        raise RuntimeError("缺少 tkinter。Debian/Ubuntu 可安装 python3-tk；或运行 map_gui_html.py 生成无需 Tk 的离线 GUI。") from exc
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError("没有可用的图形桌面显示（DISPLAY）。请在有桌面的电脑运行，或使用 map_gui_html.py 生成离线浏览器 GUI。") from exc

    class MapApp:
        def __init__(self):
            self.root = root
            root.title("梦想世界 · 离线地图查看器")
            root.geometry("1200x820")
            root.minsize(650, 440)
            self.sources = discover(map_dir, texture_dir)
            self.doc = None
            self.grid = []
            self.original = None
            self.display = None
            self.zoom = 0.5
            self.pin = None
            self.cell_visible = tk.BooleanVar(value=False)
            self.record_visible = tk.BooleanVar(value=True)
            self.status = tk.StringVar(value="选择地图；LLEC 是原始数据，并非已证实的可行走判定")
            self.title_text = tk.StringVar(value="离线地图 · 选择文件")
            self.map_id = tk.StringVar(value="")
            self.x_input = tk.StringVar()
            self.y_input = tk.StringVar()
            self._layout()
            if self.sources:
                choice = initial if initial in self.sources else next(iter(self.sources))
                self.map_id.set(choice)
                self.load(choice)
            else:
                self.status.set(f"在 {map_dir} 和 {texture_dir} 中没有找到成对的 .map / .png")

        def _layout(self):
            style = ttk.Style(root)
            if "clam" in style.theme_names():
                style.theme_use("clam")
            root.configure(bg="#101923")
            bar = ttk.Frame(root, padding=(12, 10))
            bar.pack(fill="x")
            ttk.Label(bar, text="梦想世界  /  MAP VIEWER", font=("TkDefaultFont", 13, "bold")).pack(side="left", padx=(0, 15))
            self.selection = ttk.Combobox(bar, textvariable=self.map_id, values=list(self.sources), state="readonly", width=9)
            self.selection.pack(side="left")
            self.selection.bind("<<ComboboxSelected>>", lambda _: self.load(self.map_id.get()))
            ttk.Button(bar, text="打开 .map…", command=self.open_map).pack(side="left", padx=5)
            ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
            ttk.Button(bar, text="−", width=3, command=lambda: self.set_zoom(-1)).pack(side="left")
            self.zoom_label = ttk.Label(bar, text="50%", width=6, anchor="center")
            self.zoom_label.pack(side="left")
            ttk.Button(bar, text="+", width=3, command=lambda: self.set_zoom(1)).pack(side="left")
            ttk.Button(bar, text="适合窗口", command=self.fit).pack(side="left", padx=8)
            ttk.Checkbutton(bar, text="原始网格", variable=self.cell_visible, command=self.redraw_keep_center).pack(side="left", padx=(10, 0))
            ttk.Checkbutton(bar, text="空间记录", variable=self.record_visible, command=self.redraw_keep_center).pack(side="left", padx=8)
            info = ttk.Frame(root, padding=(12, 2))
            info.pack(fill="x")
            ttk.Label(info, textvariable=self.title_text, font=("TkDefaultFont", 11, "bold")).pack(side="left")
            ttk.Label(info, text="鼠标拖拽平移 · 滚轮滚动 · Ctrl+滚轮缩放 · 橙色=值2、红色=值1、青框=未识别对象", foreground="#876842").pack(side="right")
            view = ttk.Frame(root)
            view.pack(fill="both", expand=True, padx=10, pady=8)
            self.canvas = tk.Canvas(view, background="#090c12", highlightthickness=0, cursor="crosshair")
            hbar = ttk.Scrollbar(view, orient="horizontal", command=self.canvas.xview)
            vbar = ttk.Scrollbar(view, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
            view.rowconfigure(0, weight=1)
            view.columnconfigure(0, weight=1)
            self.canvas.grid(row=0, column=0, sticky="nsew")
            vbar.grid(row=0, column=1, sticky="ns")
            hbar.grid(row=1, column=0, sticky="ew")
            self.canvas.bind("<Motion>", self.motion)
            self.canvas.bind("<Leave>", lambda _: self.status.set("鼠标离开地图 · 原始网格值不等于已证实可走性"))
            self.canvas.bind("<ButtonPress-1>", self.press)
            self.canvas.bind("<B1-Motion>", self.drag)
            self.canvas.bind("<MouseWheel>", self.wheel)
            self.canvas.bind("<Button-4>", lambda e: self.wheel(e, delta=120))
            self.canvas.bind("<Button-5>", lambda e: self.wheel(e, delta=-120))
            self.canvas.bind("<Control-MouseWheel>", self.zoom_wheel)
            root.bind("<plus>", lambda _: self.set_zoom(1))
            root.bind("<minus>", lambda _: self.set_zoom(-1))
            root.bind("<KeyPress-0>", lambda _: self.fit())
            foot = ttk.Frame(root, padding=(12, 8))
            foot.pack(fill="x")
            ttk.Label(foot, textvariable=self.status).pack(side="left", fill="x", expand=True)
            ttk.Label(foot, text="跳转 X / Y:").pack(side="left", padx=4)
            ttk.Entry(foot, textvariable=self.x_input, width=6).pack(side="left")
            ttk.Entry(foot, textvariable=self.y_input, width=6).pack(side="left", padx=4)
            ttk.Button(foot, text="定位", command=self.go_to).pack(side="left")

        def open_map(self):
            filename = filedialog.askopenfilename(parent=root, title="选择地图文件", filetypes=[("梦想世界地图", "*.map"), ("全部", "*")])
            if not filename:
                return
            src = Path(filename)
            png = texture_dir / (src.stem + ".png")
            if not png.is_file():
                png = Path(filedialog.askopenfilename(parent=root, title="选择对应的已解码 PNG", filetypes=[("PNG", "*.png")]))
                if not png.is_file():
                    return
            self.sources[src.stem] = (src, png)
            self.selection.configure(values=list(self.sources))
            self.map_id.set(src.stem)
            self.load(src.stem)

        def load(self, name):
            if name not in self.sources:
                return
            src, png = self.sources[name]
            try:
                doc = parse_map(src)
                image = tk.PhotoImage(file=str(png))
                w, h = doc["header"]["width"], doc["header"]["height"]
                if (image.width(), image.height()) != (w, h):
                    raise ValueError(f"图像尺寸 {image.width()}×{image.height()} 与地图 {w}×{h} 不符")
                self.doc, self.original = doc, image
                self.grid = build_grid(doc)
                self.zoom = 0.5
                self.pin = None
                self.title_text.set(f"地图 {name}  ·  {w} × {h} px  ·  {len(doc['prefix_records'])} 条空间记录")
                self.status.set(f"已加载 {src.name} 与 {png.name}  ·  原始地图只读")
                self.draw()
                root.after_idle(self.fit)
            except Exception as exc:
                messagebox.showerror("地图加载失败", f"{src}\n{png}\n\n{exc}", parent=root)

        def draw(self, preserve: tuple[float, float] | None = None):
            if not self.doc or self.original is None:
                return
            c = self.canvas
            w, h = self.doc["header"]["width"], self.doc["header"]["height"]
            z = self.zoom
            if preserve is None:
                preserve = (w / 2, h / 2)
            c.delete("all")
            # Tk PhotoImage supports integer zoom/subsample only. Avoid a huge
            # temporary zoom(8) allocation for 200% display.
            self.display = (self.original.zoom(2) if z == 2 else self.original if z == 1 else
                            self.original.subsample(2) if z == 0.5 else self.original.subsample(4))
            c.create_image(0, 0, image=self.display, anchor="nw", tags="image")
            if self.cell_visible.get():
                for x, y, run_w, value in cell_runs(self.grid, w, h):
                    color = "#f4b533" if value == 2 else "#e95556" if value == 1 else "#9949ed"
                    c.create_rectangle(x*z, y*z, (x+run_w)*z, min(y+20, h)*z,
                                       fill=color, outline="", stipple="gray25", tags="cells")
            if self.record_visible.get():
                for rec in self.doc["prefix_records"]:
                    box = rec["bounds_px"]
                    x, y, rw, rh = (box[k] for k in ("x", "y", "width", "height"))
                    c.create_rectangle(x*z, y*z, (x+rw)*z, (y+rh)*z,
                                       outline="#31dcee", width=2, tags="records")
            if self.pin:
                x, y = self.pin
                c.create_line(x*z-8, y*z, x*z+8, y*z, fill="#f9e96a", width=2)
                c.create_line(x*z, y*z-8, x*z, y*z+8, fill="#f9e96a", width=2)
            c.configure(scrollregion=(0, 0, w*z, h*z))
            c.update_idletasks()
            vw, vh = max(c.winfo_width(), 1), max(c.winfo_height(), 1)
            c.xview_moveto(max(0, (preserve[0]*z-vw/2) / max(w*z-vw, 1)))
            c.yview_moveto(max(0, (preserve[1]*z-vh/2) / max(h*z-vh, 1)))
            self.zoom_label.configure(text=f"{int(z*100)}%")

        def redraw_keep_center(self):
            if not self.doc:
                return
            center = (self.canvas.canvasx(self.canvas.winfo_width()/2)/self.zoom,
                      self.canvas.canvasy(self.canvas.winfo_height()/2)/self.zoom)
            self.draw(center)

        def set_zoom(self, direction):
            old = ZOOMS.index(self.zoom)
            nxt = max(0, min(len(ZOOMS)-1, old+direction))
            if nxt == old or not self.doc:
                return
            center = ((self.canvas.canvasx(self.canvas.winfo_width()/2))/self.zoom,
                      (self.canvas.canvasy(self.canvas.winfo_height()/2))/self.zoom)
            self.zoom = ZOOMS[nxt]
            self.draw(center)

        def fit(self):
            if not self.doc:
                return
            w, h = self.doc["header"]["width"], self.doc["header"]["height"]
            ratio = min(self.canvas.winfo_width()/w, self.canvas.winfo_height()/h)
            self.zoom = max((z for z in ZOOMS if z <= ratio), default=ZOOMS[0])
            self.draw((w/2, h/2))

        def coords(self, event):
            return int(self.canvas.canvasx(event.x)/self.zoom), int(self.canvas.canvasy(event.y)/self.zoom)

        def motion(self, event):
            if not self.doc:
                return
            x, y = self.coords(event)
            w, h = self.doc["header"]["width"], self.doc["header"]["height"]
            value = cell_at(self.grid, x, y, w, h)
            if value is None:
                self.status.set("地图外")
                return
            records = records_at(self.doc["prefix_records"], x, y)
            tail = f"  ·  空间记录 {','.join(map(str, records))}（类型未知）" if records else ""
            self.status.set(f"像素 ({x}, {y})  ·  LLEC[{x//20},{y//20}] = {value}（原始值，非通行结论）{tail}")

        def press(self, event):
            self.canvas.scan_mark(event.x, event.y)
            self._press = (event.x, event.y)

        def drag(self, event):
            self.canvas.scan_dragto(event.x, event.y, gain=1)

        def wheel(self, event, delta=None):
            if event.state & 0x4:  # Ctrl, including Windows and most X11 Tk builds
                self.zoom_wheel(event, delta=delta)
                return
            amount = delta if delta is not None else event.delta
            if event.state & 0x1:
                self.canvas.xview_scroll(-1 if amount > 0 else 1, "units")
            else:
                self.canvas.yview_scroll(-1 if amount > 0 else 1, "units")

        def zoom_wheel(self, event, delta=None):
            amount = delta if delta is not None else event.delta
            self.set_zoom(1 if amount > 0 else -1)

        def go_to(self):
            if not self.doc:
                return
            try:
                x, y = int(self.x_input.get()), int(self.y_input.get())
                w, h = self.doc["header"]["width"], self.doc["header"]["height"]
                if cell_at(self.grid, x, y, w, h) is None:
                    raise ValueError("坐标超出地图")
            except ValueError as exc:
                messagebox.showwarning("无效坐标", str(exc), parent=root)
                return
            self.pin = x, y
            self.draw((x, y))
            self.status.set(f"定位 ({x}, {y}) · LLEC 原始字节 {cell_at(self.grid, x, y, w, h)}")

    MapApp()
    root.mainloop()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map-dir", type=Path, default=REPO / "map")
    ap.add_argument("--texture-dir", type=Path, default=TOOLS / "map-textures")
    ap.add_argument("--initial", help="initial map ID, e.g. 2303")
    args = ap.parse_args()
    try:
        launch(args.map_dir, args.texture_dir, args.initial)
    except RuntimeError as exc:
        ap.exit(2, f"地图 GUI 无法启动: {exc}\n")


if __name__ == "__main__":
    main()
