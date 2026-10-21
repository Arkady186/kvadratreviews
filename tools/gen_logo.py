#!/usr/bin/env python3
"""Рисует логотип ASD (контуры букв из Poppins Medium, OFL) → img/logo.svg, logo-light.svg, favicon.svg."""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT = sys.argv[1] if len(sys.argv) > 1 else '/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
OUT = Path(__file__).resolve().parent.parent / 'img'
OUT.mkdir(exist_ok=True)
f = TTFont(FONT); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm
TRACK = 0.075 * upm


def word(text, height):
    """возвращает (path d, ширина, высота) — буквы по базовой линии, высота капители = height"""
    cap = f['OS/2'].sCapHeight; k = height / cap
    x, parts = 0.0, []
    for ch in text:
        g = gs[cmap[ord(ch)]]
        pen = SVGPathPen(gs, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
        g.draw(TransformPen(pen, (k, 0, 0, -k, x * k, height)))
        parts.append(pen.getCommands()); x += g.width + TRACK
    # ширина без последнего трекинга и без левого/правого боковых зазоров
    bp = BoundsPen(gs); gs[cmap[ord(text[0])]].draw(bp); lsb = bp.bounds[0]
    bp = BoundsPen(gs); gs[cmap[ord(text[-1])]].draw(bp); rsb = gs[cmap[ord(text[-1])]].width - bp.bounds[2]
    w = (x - TRACK - lsb - rsb) * k
    return ' '.join(parts), w, lsb * k


H = 100.0
d, W, lsb = word('ASD', H)
PAD, EX = 6, 3.2               # поля и «толщина» объёмных букв
VW, VH = W + 2 * PAD + EX, H + 2 * PAD + EX


def svg(vw, vh, body, extra=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw:.1f} {vh:.1f}" fill="none"{extra}>{body}</svg>\n'


def wordmark(face, edge, ex, shadow):
    g = f'<g transform="translate({PAD - lsb:.2f} {PAD})">'
    return (f'<defs><linearGradient id="m" x1="0" y1="0" x2="0" y2="1">{face}</linearGradient></defs>'
            f'{g}<path d="{d}" fill="{edge}" transform="translate({ex} {ex})"/>'
            f'<path d="{d}" fill="{shadow}" opacity=".35" transform="translate({ex + 2.2} {ex + 3.4})"/>'
            f'<path d="{d}" fill="url(#m)"/>'
            f'<path d="{d}" stroke="#fff" stroke-opacity=".35" stroke-width=".7" fill="none"/></g>')


silver = ('<stop offset="0" stop-color="#F7F8F8"/><stop offset=".38" stop-color="#CBD0D2"/>'
          '<stop offset=".5" stop-color="#9FA5A9"/><stop offset=".62" stop-color="#D9DCDE"/><stop offset="1" stop-color="#8A9094"/>')
ink = ('<stop offset="0" stop-color="#3B4B44"/><stop offset=".5" stop-color="#1F2B26"/><stop offset="1" stop-color="#101814"/>')

# на тёмном фоне: серебро, как буквы на фото
(OUT / 'logo-light.svg').write_text(svg(VW, VH, wordmark(silver, '#5B6468', EX, '#000')), encoding='utf-8')
# на светлом фоне: графит с латунной гранью
(OUT / 'logo.svg').write_text(svg(VW, VH, wordmark(ink, '#B8924A', EX * .8, '#8C6B2C')), encoding='utf-8')

# значок для вкладки браузера
fs = 64; kk = 0.76 * fs / W
fav = (f'<rect width="{fs}" height="{fs}" fill="#16201C"/><rect x="{fs - 17}" y="{fs - 17}" width="17" height="17" fill="#B8924A"/>'
       f'<defs><linearGradient id="m" x1="0" y1="0" x2="0" y2="1">{silver}</linearGradient></defs>'
       f'<g transform="translate({(fs - W * kk) / 2 - lsb * kk:.2f} {(fs - H * kk) / 2 - 2:.2f}) scale({kk:.4f})"><path d="{d}" fill="url(#m)"/></g>')
(OUT / 'favicon.svg').write_text(svg(fs, fs, fav), encoding='utf-8')
print('ok', round(VW), round(VH))
