#!/usr/bin/env python3
"""Снимает 3D-рендеры образцов и кухни для PDF-гида в папку _pdf/ (нужен сервер на :8766)."""
import os
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, '_pdf'); os.makedirs(OUT, exist_ok=True)
jobs = [('fan', '', 900, 1000)] + [('s%d' % i, 's=%d' % i, 600, 900) for i in range(5)] + [('k%d' % i, 'k=%d' % i, 1400, 900) for i in range(3)]
with sync_playwright() as p:
    b = p.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    for name, qs, w, h in jobs:
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
        pg.goto(f'http://localhost:8766/tools/render3d.html?{qs}&w={w}&h={h}'); pg.wait_for_timeout(1200)
        f = os.path.join(OUT, name + '.png'); pg.locator('#h').screenshot(path=f, omit_background=True); pg.close()
        im = Image.open(f); bb = im.getchannel('A').getbbox()
        if bb: im = im.crop((max(0, bb[0] - 20), max(0, bb[1] - 20), min(im.width, bb[2] + 20), min(im.height, bb[3] + 20)))
        im.thumbnail((1400, 1400)); im.save(f, optimize=True); print(name, im.size)
