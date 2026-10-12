#!/usr/bin/env python3
"""Reproduce frozen v3 overlay and small UI caption assets.

Usage: python3 prepare_visual_assets.py --python25 /path/to/CPython-2.5.6/python
Requires Pillow; uses the font already shipped in this repository, not a font download.
No game script is executed by the compiler.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'visual_assets'
FONT = ROOT / 'Fonts/FZLanTingYuan-DB-GBK.ttf'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def font(size):
    return ImageFont.truetype(str(FONT), size)


def center(draw, box, text, size, fill):
    f = font(size)
    b = draw.textbbox((0, 0), text, font=f)
    x = (box[0]+box[2] - (b[2]-b[0]))/2 - b[0]
    y = (box[1]+box[3] - (b[3]-b[1]))/2 - b[1]
    draw.text((x, y), text, font=f, fill=fill)


def images():
    OUT.mkdir(exist_ok=True)
    image = Image.new('RGBA', (80, 24))
    center(ImageDraw.Draw(image), (0, 0, 80, 24), '注册账号', 15, '#474e9a')
    image.save(OUT / 'home_register.png')
    # Whole gold buttons, including captions; no dependence on old login art.
    for name, text in [('agree', '同意'), ('reject', '拒绝'),
                       ('back', '上一步'), ('register', '注册账号')]:
        image = Image.new('RGBA', (112, 34))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, 111, 33), radius=4, fill='#b99748')
        for y in range(2, 32):
            t = float(y-2)/29
            color = tuple(int(a+(b-a)*t) for a,b in zip((255,240,170),(226,191,86)))
            draw.line((2, y, 109, y), fill=color)
        draw.rounded_rectangle((2, 2, 109, 31), radius=3, outline='#fff0bd')
        center(draw, (0, 0, 112, 34), text, 16, '#805522')
        image.save(OUT / (name + '.png'))
    image = Image.new('RGBA', (240, 34), '#eeedf9')
    center(ImageDraw.Draw(image), (0, 0, 240, 34), '注册协议', 18, '#6657bb')
    image.save(OUT / 'terms_title.png')
    image = Image.new('RGBA', (200, 28))
    center(ImageDraw.Draw(image), (0, 0, 200, 28), '离线预览说明', 14, '#6657bb')
    image.save(OUT / 'info.png')
    image = Image.new('RGBA', (400, 300))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, 399, 299), radius=16, fill=(238, 236, 250, 253), outline='#c7b4d9', width=2)
    draw.line((26, 53, 374, 53), fill='#d6bf8a', width=1)
    center(draw, (0, 9, 400, 49), '注册账号', 23, '#6456ad')
    for title, top in [('邮箱', 70), ('密码', 128), ('确认密码', 186)]:
        draw.rounded_rectangle((124, top, 382, top+34), radius=5, fill='#fbfaff', outline='#b9aed1', width=1)
        center(draw, (16, top, 118, top+34), title, 16, '#51477e')
    center(draw, (0, 233, 400, 254), '本地校验预览 · 不会创建真实账号', 12, '#7b7099')
    image.save(OUT / 'form_card.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python25', required=True)
    parser.add_argument('--code-only', action='store_true', help='keep existing frozen PNGs; no Pillow needed')
    args = parser.parse_args()
    version = subprocess.check_output([args.python25, '-S', '-c', 'import sys; print sys.version_info[:3]']).decode().strip()
    if version != '(2, 5, 6)':
        raise ValueError('CPython 2.5.6 required')
    if not args.code_only:
        global Image, ImageDraw, ImageFont
        from PIL import Image, ImageDraw, ImageFont
        images()
    subprocess.run([args.python25, '-S', '-c',
        "import marshal,sys; s=open(sys.argv[1],'rb').read(); c=compile(s,'home_registration_entry.py','exec'); open(sys.argv[2],'wb').write(marshal.dumps(c,2))",
        str(HERE / 'home_registration_entry.py'), str(OUT / 'home_entry.py25')], check=True)
    subprocess.run([args.python25, '-S', '-c',
        "import marshal,sys; s=open(sys.argv[1],'rb').read(); c=compile(s,'registration_visual_overlay.py','exec'); open(sys.argv[2],'wb').write(marshal.dumps(c,2))",
        str(HERE / 'registration_visual_overlay.py'), str(OUT / 'overlay.py25')], check=True)
    manifest = {'compiler': 'CPython 2.5.6', 'compiler_source': 'https://github.com/python/cpython/tree/v2.5.6',
                'source_sha256': sha((HERE / 'registration_visual_overlay.py').read_bytes()),
                'compiled_sha256': sha((OUT / 'overlay.py25').read_bytes()),
                'font_sha256': sha(FONT.read_bytes()),
                'home_source_sha256': sha((HERE / 'home_registration_entry.py').read_bytes()),
                'home_compiled_sha256': sha((OUT / 'home_entry.py25').read_bytes()),
                'assets': {p.name: sha(p.read_bytes()) for p in sorted(OUT.glob('*.png'))}}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
