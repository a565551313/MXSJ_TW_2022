#!/usr/bin/env python3
"""Generate a self-contained, offline, interactive browser GUI for .map files.

Python standard library only. Embeds every matching .map and recovered PNG
from the selected directories; the HTML makes NO network requests and needs NO server.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import struct

from map_parser import parse_map
from map_viewer import build_grid

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parents[2]


HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>梦想世界 · 离线地图查看器</title>
<style>
:root{color-scheme:dark;--bg:#0b111a;--panel:#121c29;--line:#2b3e4e;--text:#e6eef2;--muted:#8ba1ae;--aqua:#76e1d5;--gold:#ffc172}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.55 system-ui,-apple-system,"Microsoft YaHei",sans-serif}
button,input{font:inherit}button{cursor:pointer}button:focus-visible,input:focus-visible{outline:2px solid var(--aqua);outline-offset:2px}
.app{height:100dvh;min-height:420px;display:grid;grid-template-columns:270px minmax(0,1fr);grid-template-rows:62px minmax(0,1fr) 50px}
header{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;padding:0 23px;background:#101a26;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:13px}.mark{width:36px;height:36px;border:1px solid #77dbd0;border-radius:10px;display:grid;place-items:center;color:#8ee9db;font-size:20px;background:#1b353e}
.brand h1{margin:0;font-size:16px;letter-spacing:.03em}.brand small{display:block;font-size:11px;font-weight:400;color:var(--muted);letter-spacing:.15em}
.header-note{color:var(--muted);font-size:12px}.header-note b{color:var(--aqua)}
aside{background:var(--panel);border-right:1px solid var(--line);overflow:auto;padding:19px 13px 25px}.label{font-size:11px;font-weight:700;letter-spacing:.13em;color:#819cad;text-transform:uppercase;margin:0 10px 12px}
.map-card{border:1px solid #304452;background:#172330;border-radius:11px;display:flex;gap:12px;align-items:center;width:100%;padding:9px;margin:0 0 9px;text-align:left;color:var(--text);transition:background .15s,border-color .15s}
.map-card:hover{background:#223444}.map-card.active{border-color:#71dacf;background:#1d3a42;box-shadow:inset 3px 0 0 #79e7d8}.thumb{height:54px;width:70px;object-fit:cover;background:#05080e;border-radius:6px}.card-id{font-size:16px;font-weight:700}.card-meta{font-size:11px;color:#9cb2bd}
.side-rule{height:1px;background:var(--line);margin:20px 9px}.toggle{display:flex;align-items:center;gap:9px;padding:8px 10px;cursor:pointer;color:#cedde3}.toggle input{accent-color:#65ded2;width:16px;height:16px}
.key{color:var(--gold);font-weight:700}.legend{padding:2px 10px;color:#a9bcc6;font-size:12px}.legend div{margin:7px 0;display:flex;align-items:center;gap:8px}.sw{width:11px;height:11px;border-radius:3px;display:inline-block}.warn{font-size:12px;line-height:1.65;color:#a8b8c2;background:#1b2a36;border:1px solid #334756;padding:12px;border-radius:9px;margin:18px 9px 0}
main{position:relative;min-width:0;min-height:0;overflow:hidden;background:radial-gradient(circle at 50% 50%,#192636,#090e15 78%)}
.toolbar{position:absolute;z-index:2;top:14px;left:16px;display:flex;gap:5px;align-items:center;background:#14212ee8;border:1px solid #344d5a;border-radius:10px;padding:5px;box-shadow:0 10px 25px #0006}
.tool{background:transparent;color:#e2ecee;border:0;border-radius:7px;padding:5px 9px;min-width:29px}.tool:hover{background:#324f5a}.zoom-value{width:53px;text-align:center;color:var(--aqua);font-size:12px;font-weight:700}
.map-info{position:absolute;z-index:2;top:16px;right:16px;padding:7px 11px;border:1px solid #3a5361;border-radius:8px;background:#14212ee8;color:#bcd0d7;font-size:12px}
#view{width:100%;height:100%;display:block;cursor:grab;touch-action:none}#view.dragging{cursor:grabbing}
footer{grid-column:1/-1;background:#111c28;border-top:1px solid var(--line);display:flex;align-items:center;padding:0 18px;gap:12px;white-space:nowrap;overflow:hidden}.status{flex:1;overflow:hidden;text-overflow:ellipsis;color:#d3e7e9;font-variant-numeric:tabular-nums}.hint{color:#91a8b1;font-size:12px}.goto{display:flex;align-items:center;gap:5px;color:var(--muted)}.goto input{width:60px;padding:4px 6px;background:#172936;border:1px solid #425866;color:var(--text);border-radius:5px}.goto button{background:#254d55;border:1px solid #468e92;border-radius:6px;padding:4px 8px;color:#e1fcf8}
@media(max-width:760px){.app{grid-template-columns:1fr;grid-template-rows:54px 130px minmax(0,1fr) 48px}header{padding:0 13px}.header-note,.hint{display:none}aside{border-right:0;border-bottom:1px solid var(--line);padding:8px 10px;overflow:auto}.label,.side-rule,.legend,.warn,.toggle{display:none}#maplist{display:flex;gap:6px;min-width:max-content}.map-card{min-width:140px;margin:0;padding:5px}.thumb{width:48px;height:48px}.map-info{display:none}.goto{display:none}}
</style></head><body>
<div class="app"><header><div class="brand"><div class="mark">◈</div><h1>梦想世界 · 地图查看器<small>OFFLINE MAP EXPLORER</small></h1></div><div class="header-note"><b>●</b> 本地资源 · 无网络连接</div></header>
<aside><div class="label">地图列表 / MAP LIBRARY</div><div id="maplist"></div><div class="side-rule"></div>
<div class="label">图层 / LAYERS</div><label class="toggle"><input id="cells" type="checkbox"> 原始 LLEC 网格</label><label class="toggle"><input id="objects" type="checkbox" checked> 空间记录边框</label><label class="toggle"><input id="sectors" type="checkbox"> 分块边界</label>
<div class="side-rule"></div><div class="label">图例 / LEGEND</div><div class="legend"><div><i class="sw" style="background:#ef5659"></i>字节值 1（非通行结论）</div><div><i class="sw" style="background:#ffc172"></i>字节值 2（用途未明）</div><div><i class="sw" style="background:#63e0e4"></i>空间记录（类型未明）</div></div>
<div class="warn"><span class="key">研究提示</span><br>底图已恢复；LLEC 值与可行走性尚未完成运行时验证。红色不等于已证实的碰撞区域；青色不等于 NPC 或传送点。</div></aside>
<main><div class="toolbar"><button class="tool" id="minus" title="缩小">−</button><span class="zoom-value" id="zoom">--%</span><button class="tool" id="plus" title="放大">+</button><button class="tool" id="fit" title="适合窗口">适合窗口</button><button class="tool" id="actual" title="原始大小">100%</button></div>
<div class="map-info" id="info">正在加载…</div><canvas id="view" aria-label="可缩放、可拖动的地图视图"></canvas></main>
<footer><div class="status" id="status">准备就绪</div><div class="hint">拖拽平移 · 滚轮缩放 · 点击定位 · + / − 调整</div><div class="goto">坐标 <input id="coordX" type="number" min="0" max="1999" placeholder="X"><input id="coordY" type="number" min="0" max="1499" placeholder="Y"><button id="go">定位</button></div></footer></div>
<script>
"use strict";
const maps=__PAYLOAD__;
const $=id=>document.getElementById(id), canvas=$('view'), ctx=canvas.getContext('2d');
let current=null, image=new Image(), scale=1, px=0, py=0, pin=null, dragging=false, moved=false, lastX=0,lastY=0,startX=0,startY=0,raf=0;
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function viewport(){return {w:canvas.clientWidth,h:canvas.clientHeight}}
function fit(){if(!current)return;const {w,h}=viewport();scale=clamp(Math.min((w-54)/current.w,(h-54)/current.h),.18,3.5);px=(w-current.w*scale)/2;py=(h-current.h*scale)/2;drawSoon()}
function drawSoon(){if(raf)return;raf=requestAnimationFrame(()=>{raf=0;draw()})}
function draw(){let {w,h}=viewport(), dpr=window.devicePixelRatio||1;
 if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);
 if(!current||!image.complete){return}
 ctx.save();ctx.translate(px,py);ctx.scale(scale,scale);ctx.imageSmoothingEnabled=scale<1;
 ctx.drawImage(image,0,0,current.w,current.h);
 if($('cells').checked){let c0=clamp(Math.floor(-px/scale/20),0,Math.ceil(current.w/20)),c1=clamp(Math.ceil((w-px)/scale/20),0,Math.ceil(current.w/20));
 let r0=clamp(Math.floor(-py/scale/20),0,Math.ceil(current.h/20)),r1=clamp(Math.ceil((h-py)/scale/20),0,Math.ceil(current.h/20));
 for(let y=r0;y<r1;y++){for(let x=c0;x<c1;x++){let v=current.cells[y*112+x];if(!v)continue;
 ctx.fillStyle=v===1?'rgba(240,75,78,.32)':v===2?'rgba(255,193,86,.66)':'rgba(145,73,236,.65)';ctx.fillRect(x*20,y*20,20,20)}}}
 if($('sectors').checked){ctx.beginPath();ctx.strokeStyle='rgba(255,255,255,.38)';ctx.lineWidth=1/scale;
 for(let x=320;x<current.w;x+=320){ctx.moveTo(x,0);ctx.lineTo(x,current.h)}for(let y=240;y<current.h;y+=240){ctx.moveTo(0,y);ctx.lineTo(current.w,y)}ctx.stroke()}
 if($('objects').checked){ctx.strokeStyle='#4de6f1';ctx.lineWidth=2/scale;for(const o of current.records)ctx.strokeRect(o.x,o.y,o.w,o.h)}
 if(pin){ctx.beginPath();ctx.lineWidth=2/scale;ctx.strokeStyle='#ffdc6c';ctx.moveTo(pin.x-12/scale,pin.y);ctx.lineTo(pin.x+12/scale,pin.y);ctx.moveTo(pin.x,pin.y-12/scale);ctx.lineTo(pin.x,pin.y+12/scale);ctx.stroke()}
 ctx.restore();$('zoom').textContent=Math.round(scale*100)+'%'}
function position(e){let b=canvas.getBoundingClientRect();return {sx:e.clientX-b.left,sy:e.clientY-b.top}}
function world(sx,sy){return {x:Math.floor((sx-px)/scale),y:Math.floor((sy-py)/scale)}}
function showPoint(sx,sy){if(!current)return;let {x,y}=world(sx,sy);
 if(x<0||y<0||x>=current.w||y>=current.h){$('status').textContent='地图区域外 · 拖动或滚轮缩放';return}
 let col=Math.floor(x/20),row=Math.floor(y/20),v=current.cells[row*112+col];let hits=current.records.filter(o=>x>=o.x&&y>=o.y&&x<o.x+o.w&&y<o.y+o.h).map(o=>o.id);
 $('status').textContent=`地图 ${current.id} · 像素 (${x}, ${y}) · LLEC[${col}, ${row}] = ${v}（原始值，不代表通行判定）`+(hits.length?' · 空间记录 '+hits.join(',')+'（类型未明）':'')}
function zoomAt(factor,sx,sy){if(!current)return;let before=world(sx,sy),old=scale;scale=clamp(scale*factor,.18,3.5);px=sx-before.x*scale;py=sy-before.y*scale;drawSoon()}
function select(id){let m=maps.find(m=>m.id===id);if(!m)return;current=m;pin=null;const loading=new Image();image=loading;loading.onload=()=>{if(current!==m)return;fit();$('info').textContent=`${m.id}  ·  ${m.w} × ${m.h}  ·  ${m.records.length} 条空间记录`; $('status').textContent=`已加载地图 ${id}，可拖拽查看，切换左侧图层`;drawSoon()};loading.onerror=()=>{if(current===m)$('status').textContent='本地图像未能加载'};loading.src=m.img;
 for(const el of document.querySelectorAll('.map-card'))el.classList.toggle('active',el.dataset.id===id)}
for(const m of maps){let btn=document.createElement('button');btn.className='map-card';btn.dataset.id=m.id;let im=document.createElement('img');im.className='thumb';im.src=m.img;im.alt='';let labels=document.createElement('div');let name=document.createElement('div');name.className='card-id';name.textContent=m.id;let meta=document.createElement('div');meta.className='card-meta';meta.textContent=`${m.w} × ${m.h} · ${m.records.length} 记录`;labels.append(name,meta);btn.append(im,labels);btn.addEventListener('click',()=>select(m.id));$('maplist').append(btn)}
canvas.addEventListener('pointerdown',e=>{canvas.setPointerCapture(e.pointerId);dragging=true;moved=false;let p=position(e);lastX=startX=p.sx;lastY=startY=p.sy;canvas.classList.add('dragging')});
canvas.addEventListener('pointermove',e=>{let p=position(e);if(dragging){px+=p.sx-lastX;py+=p.sy-lastY;lastX=p.sx;lastY=p.sy;if(Math.hypot(p.sx-startX,p.sy-startY)>4)moved=true;drawSoon()}showPoint(p.sx,p.sy)});
canvas.addEventListener('pointerup',e=>{let p=position(e);if(dragging&&!moved&&current){let q=world(p.sx,p.sy);if(q.x>=0&&q.y>=0&&q.x<current.w&&q.y<current.h){pin=q;drawSoon();showPoint(p.sx,p.sy)}}dragging=false;canvas.classList.remove('dragging')});
canvas.addEventListener('wheel',e=>{e.preventDefault();let p=position(e);zoomAt(e.deltaY<0?1.18:1/1.18,p.sx,p.sy)},{passive:false});
for(const id of ['cells','objects','sectors'])$(id).addEventListener('change',drawSoon);
$('plus').onclick=()=>{let {w,h}=viewport();zoomAt(1.3,w/2,h/2)};$('minus').onclick=()=>{let {w,h}=viewport();zoomAt(1/1.3,w/2,h/2)};
$('fit').onclick=fit;$('actual').onclick=()=>{if(!current)return;let {w,h}=viewport(),before=world(w/2,h/2);scale=1;px=w/2-before.x;py=h/2-before.y;drawSoon()};
$('go').onclick=()=>{if(!current)return;let x=Number($('coordX').value),y=Number($('coordY').value);if(!$('coordX').value||!$('coordY').value||!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x>=current.w||y>=current.h){$('status').textContent='请输入地图范围内的整数像素坐标';return}pin={x,y};let {w,h}=viewport();px=w/2-x*scale;py=h/2-y*scale;drawSoon();showPoint(w/2,h/2)};
window.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT')return;let {w,h}=viewport();if(e.key==='+'||e.key==='=')zoomAt(1.3,w/2,h/2);if(e.key==='-')zoomAt(1/1.3,w/2,h/2);if(e.key==='0')fit()});
new ResizeObserver(drawSoon).observe(canvas);if(maps.length)select(maps[0].id);else $('status').textContent='无地图，请先运行 gepj_decoder.py 导出 PNG';
</script></body></html>'''


def build_payload(map_dir: Path, texture_dir: Path) -> list[dict]:
    result = []
    for path in sorted(map_dir.glob("*.map")):
        png_path = texture_dir / (path.stem + ".png")
        if not png_path.is_file():
            continue
        doc = parse_map(path)
        png = png_path.read_bytes()
        if png[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack_from(">II", png, 16) != (doc["header"]["width"], doc["header"]["height"]):
            raise ValueError(f"PNG 与地图尺寸不符: {png_path}")
        grid = build_grid(doc)
        result.append({"id": path.stem, "w": doc["header"]["width"], "h": doc["header"]["height"],
                       "img": "data:image/png;base64," + base64.b64encode(png).decode("ascii"),
                       "cells": [v for row in grid for v in row],
                       "records": [{"id": r["index"], **r["bounds_px"], "w": r["bounds_px"]["width"],
                                    "h": r["bounds_px"]["height"]} for r in doc["prefix_records"]]})
    return result


def generate(map_dir: Path, texture_dir: Path, output: Path) -> tuple[int, int]:
    items = build_payload(map_dir, texture_dir)
    if not items:
        raise ValueError("没有找到成对的 .map 与 PNG；先用 gepj_decoder.py 恢复底图")
    payload = json.dumps(items, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(HTML.replace("__PAYLOAD__", payload), encoding="utf-8")
    return len(items), output.stat().st_size


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map-dir", type=Path, default=REPO / "map")
    ap.add_argument("--texture-dir", type=Path, default=TOOLS / "map-textures")
    ap.add_argument("--output", type=Path, default=TOOLS / "map-viewer.html")
    args = ap.parse_args()
    count, size = generate(args.map_dir, args.texture_dir, args.output)
    print(f"已生成离线 GUI：{args.output}（{count} 张地图，{size/1024/1024:.1f} MiB）")


if __name__ == "__main__":
    main()
