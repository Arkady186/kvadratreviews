#!/usr/bin/env python3
"""Генератор чертежей кухонь для главной страницы.

Берёт первую кухню (прямая, 3200 мм) из <svg> в index.html как есть,
строит ещё две (с колонной-холодильником и окном; с духовой колонной и витринами)
и пишет все три в js/kitchens.js (window.KITCHENS).
Запуск из корня проекта:  python3 tools/gen_kitchens.py
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = 0.24            # px на мм (масштаб 1:20)
X0 = 110.0          # левая стенка
FLOOR = 520.0
DEFS = ('<defs><linearGradient id="scan-g" x1="0" x2="1"><stop offset="0" stop-color="#DDBF85" stop-opacity="0"/>'
        '<stop offset=".85" stop-color="#DDBF85" stop-opacity=".28"/><stop offset="1" stop-color="#F3E3BC" stop-opacity=".7"/>'
        '</linearGradient></defs>')


def n(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


class Kitchen:
    def __init__(self, width_mm, tag1):
        self.W = width_mm
        self.xe = X0 + width_mm * S
        self.fills, self.lines, self.texts = [], [], []
        self.tag1 = tag1

    # --- координаты
    def X(self, mm): return X0 + mm * S
    def Y(self, mm): return FLOOR - mm * S

    # --- примитивы
    def ln(self, d, t, path, cls=''):
        self.lines.append(f'<path class="ln {cls}" pathLength="1" style="--d:{d:.2f};--t:{t}s" d="{path}"/>')

    def rect(self, d, t, x, y, w, h, cls=''):
        self.ln(d, t, f'M{n(x)} {n(y)}h{n(w)}v{n(h)}h{n(-w)}Z', cls)

    def fill(self, d, x, y, w, h, kind='f-cab'):
        self.fills.append(f'<rect class="fill {kind}" style="--d:{d:.2f}" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"/>')

    def poly(self, d, pts, kind='f-app'):
        self.fills.append(f'<polygon class="fill {kind}" style="--d:{d:.2f}" points="{pts}"/>')

    def seg(self, d, t, x1, y1, x2, y2, cls='thin'):
        self.ln(d, t, f'M{n(x1)} {n(y1)}L{n(x2)} {n(y2)}', cls)

    # --- общие части
    def shell(self):
        self.ln(0.0, 1.2, f'M{n(X0 - 36)} {n(FLOOR)}H{n(self.xe + 36)}')
        self.ln(0.2, 1.0, f'M{n(X0)} {n(FLOOR)}V-20', 'thin')
        self.ln(0.3, 1.0, f'M{n(self.xe)} {n(FLOOR)}V-20', 'thin')
        self.rect(0.6, 1.0, X0, self.Y(100), self.W * S, 100 * S)           # цоколь

    def base(self, a, b, i):
        x, w = self.X(a), (b - a) * S
        d = 0.9 + 0.18 * i
        self.rect(d, 1.0, x, self.Y(850), w, 750 * S)
        self.fill(5.0 + 0.1 * i, x + 1, self.Y(850) + 1, w - 2, 750 * S - 2)

    def slab(self, a, b, left_over=False, right_over=False):
        x1 = self.X(a) - (7.2 if left_over else 0)
        x2 = self.X(b) + (7.2 if right_over else 0)
        y, h = self.Y(850) - 9.1, 9.1
        self.rect(1.9, 1.6, x1, y, x2 - x1, h)
        self.fill(5.2, x1, y, x2 - x1, h, 'f-top')

    def wall(self, a, b, i, glass=False):
        x, w = self.X(a), (b - a) * S
        d = 2.4 + 0.2 * i
        y, h = self.Y(2000), 550 * S
        self.rect(d, 1.0, x, y, w, h)
        self.fill(5.1 + 0.1 * i, x + 1, y + 1, w - 2, h - 2)
        if glass:                                                          # витрина: два блика-диагонали
            self.seg(4.1, 0.6, x + w * .18, y + h * .78, x + w * .38, y + h * .2)
            self.seg(4.2, 0.6, x + w * .28, y + h * .85, x + w * .5, y + h * .3)

    def drawers(self, a, b, count):
        x, w = self.X(a), (b - a) * S
        top, hh = self.Y(850), 750 * S
        for k in range(1, count):
            self.ln(4.2 + .1 * k, .6, f'M{n(x)} {n(top + hh * k / count)}H{n(x + w)}', 'thin')
        for k in range(count):
            cy = top + hh * (k + .5) / count
            self.ln(4.4 + .08 * k, .5, f'M{n(x + w * .22)} {n(cy)}H{n(x + w * .78)}', 'thin')

    def doors2(self, a, b):
        x, w = self.X(a), (b - a) * S
        top = self.Y(850)
        self.ln(4.0, .6, f'M{n(x + w / 2)} {n(top)}V{n(self.Y(100))}', 'thin')
        for dx in (-6, 6):
            self.ln(4.1, .5, f'M{n(x + w / 2 + dx)} {n(top + 12)}L{n(x + w / 2 + dx)} {n(top + 30)}', 'thin')

    def door1(self, a, b, left=False):
        x, w = self.X(a), (b - a) * S
        hx = x + 12 if left else x + w - 12
        self.ln(4.3, .5, f'M{n(hx)} {n(self.Y(850) + 12)}L{n(hx)} {n(self.Y(850) + 36)}', 'thin')

    def sink(self, a, b):
        x, w = self.X(a), (b - a) * S
        cx = x + w / 2
        sy = self.Y(850) - 9.1
        self.ln(3.4, .9, f'M{n(cx - 50)} {n(sy)}L{n(cx - 38)} {n(sy + 22)}H{n(cx + 38)}L{n(cx + 50)} {n(sy)}')
        self.fill(5.6, cx - 50, sy, 100, 22, 'f-sink')
        self.ln(3.9, .9, f'M{n(cx + 26)} {n(sy)}V{n(sy - 34)}Q{n(cx + 26)} {n(sy - 48)} {n(cx + 12)} {n(sy - 48)}H{n(cx - 2)}')

    def hob(self, a, b):
        x, w = self.X(a), (b - a) * S
        cx = x + w / 2
        sy = self.Y(850) - 9.1
        pw = min(w - 28, 140)
        self.rect(3.3, .7, cx - pw / 2, sy - 10, pw, 10)
        self.fill(5.5, cx - pw / 2, sy - 10, pw, 10, 'f-app')
        for off in (-pw * .26, pw * .26):
            self.ln(3.5, .5, f'M{n(cx + off - 17)} {n(sy - 14)}h34', 'thin')
            self.ln(3.6, .4, f'M{n(cx + off - 9)} {n(sy - 18)}h18', 'thin')

    def oven_under(self, a, b):
        x, w = self.X(a), (b - a) * S
        top = self.Y(850)
        self.rect(3.7, 1.0, x + 14, top + 16, w - 28, 148, 'thin')
        self.fill(5.4, x + 14, top + 16, w - 28, 148, 'f-app')
        self.rect(3.9, .8, x + 30, top + 46, w - 60, 64, 'thin')
        self.ln(4.2, .5, f'M{n(x + 20)} {n(top + 28)}H{n(x + w - 20)}', 'thin')
        for k in range(3):
            self.ln(4.3, .3, f'M{n(x + w * (.28 + .22 * k))} {n(top + 22)}h0.1')

    def hood(self, a, b):
        x1, x2 = self.X(a), self.X(b)
        cx, hw = (x1 + x2) / 2, (x2 - x1) / 2
        by, ty, ct = self.Y(1450), self.Y(1450) - 60, self.Y(2000)
        off = hw * .38
        self.ln(2.9, 1.0, f'M{n(x1)} {n(by)}L{n(x1 + off)} {n(ty)}V{n(ct)}')
        self.ln(2.95, 1.0, f'M{n(x2)} {n(by)}L{n(x2 - off)} {n(ty)}V{n(ct)}')
        self.ln(3.0, .7, f'M{n(x1)} {n(by)}H{n(x2)}')
        self.ln(3.1, .5, f'M{n(x1 + off)} {n(ct)}H{n(x2 - off)}', 'thin')
        self.poly(5.5, f'{n(x1)},{n(by)} {n(x2)},{n(by)} {n(x2 - off)},{n(ty)} {n(x1 + off)},{n(ty)}')

    # --- размерные линии и подписи
    def dims(self, cuts, tag2='Масштаб 1 : 20'):
        ys, yt = 554, 594
        self.ln(5.6, 1.0, f'M{n(X0)} {ys}H{n(self.xe)}', 'dim')
        for c in cuts:
            self.ln(5.7, .4, f'M{n(self.X(c))} {ys - 7}V{ys + 7}', 'dim')
        self.ln(6.2, 1.0, f'M{n(X0)} {yt}H{n(self.xe)}', 'dim')
        for xx in (X0, self.xe):
            self.ln(6.3, .4, f'M{n(xx)} {yt - 7}V{yt + 7}', 'dim')
        vx = self.xe + 52
        self.ln(6.0, 1.2, f'M{n(vx)} {n(FLOOR)}V{n(self.Y(2000))}', 'dim')
        for yy in (FLOOR, self.Y(850), self.Y(1450), self.Y(2000)):
            self.ln(6.1, .4, f'M{n(vx - 7)} {n(yy)}H{n(vx + 7)}', 'dim')
        for k in range(len(cuts) - 1):
            a, b = cuts[k], cuts[k + 1]
            self.texts.append(f'<text x="{n(self.X((a + b) / 2))}" y="545" text-anchor="middle" class="cnt" data-val="{b - a}" style="--d:{5.9 + .12 * k:.2f}">0</text>')
        self.texts.append(f'<text x="{n(self.X(self.W / 2))}" y="585" text-anchor="middle" class="cnt" data-val="{self.W}" style="--d:6.4">0</text>')
        for yy, v, d in ((422, 850, 6.2), (248, 600, 6.41), (110, 550, 6.56)):
            self.texts.append(f'<text x="{n(vx + 14)}" y="{yy}" class="cnt" data-val="{v}" style="--d:{d}">0</text>')
        tx = self.X(0) + 28.8
        self.texts.append(f'<text class="tag" x="{n(tx)}" y="-6" style="--d:6.8">{self.tag1}</text>')
        self.texts.append(f'<text class="tag" x="{n(tx)}" y="15" style="--d:7.0">{tag2}</text>')

    def svg(self):
        scan = f'<rect class="scan" x="50" y="16" width="60" height="504"/>'
        return '\n  '.join([DEFS, ''.join(self.fills), ''.join(self.lines), ''.join(self.texts), scan])


def kitchen_column():
    """3000 мм: колонна-холодильник · ящики · мойка под окном · плита с вытяжкой · узкий пенал."""
    k = Kitchen(3000, 'Встроенный холодильник · фурнитура Blum')
    k.shell()
    # колонна-холодильник 0–600 на всю высоту
    x, w = k.X(0), 600 * S
    k.rect(0.9, 1.0, x, k.Y(2000), w, 1900 * S)
    k.fill(5.0, x + 1, k.Y(2000) + 1, w - 2, 1900 * S - 2, 'f-app')
    k.ln(2.2, .6, f'M{n(x)} {n(k.Y(700))}H{n(x + w)}', 'thin')
    k.ln(2.4, .5, f'M{n(x + w - 12)} {n(k.Y(1900))}V{n(k.Y(1500))}', 'thin')
    k.ln(2.5, .5, f'M{n(x + w - 12)} {n(k.Y(620))}V{n(k.Y(420))}', 'thin')
    k.ln(2.6, .4, f'M{n(x + 10)} {n(k.Y(1930))}H{n(x + w - 10)}', 'thin')
    # базовые модули
    mods = [(600, 1200, 'dr'), (1200, 2100, 'sink'), (2100, 2700, 'hob'), (2700, 3000, 'pull')]
    for i, (a, b, kind) in enumerate(mods):
        k.base(a, b, i + 1)
        if kind == 'dr': k.drawers(a, b, 3)
        if kind == 'sink': k.doors2(a, b); k.sink(a, b)
        if kind == 'hob': k.oven_under(a, b); k.hob(a, b)
        if kind == 'pull': k.drawers(a, b, 4)
    k.slab(600, 3000, right_over=True)
    # верхние шкафы: над ящиками и над узким пеналом, над плитой вытяжка
    k.wall(600, 1200, 0); k.door1(600, 1200)
    k.wall(2700, 3000, 3)
    k.hood(2100, 2700)
    # окно над мойкой
    wx, wy = k.X(1250), k.Y(1900)
    ww, wh = 800 * S, 750 * S
    k.rect(2.3, 1.2, wx, wy, ww, wh)
    k.rect(2.7, .9, wx + 6, wy + 6, ww - 12, wh - 12, 'thin')
    k.ln(3.1, .7, f'M{n(wx + ww / 2)} {n(wy + 6)}V{n(wy + wh - 6)}', 'thin')
    k.ln(3.2, .7, f'M{n(wx + 6)} {n(wy + wh * .38)}H{n(wx + ww - 6)}', 'thin')
    k.ln(3.3, .8, f'M{n(k.X(1200))} {n(wy + wh + 8)}H{n(k.X(2100))}', 'thin')
    k.dims([0, 600, 1200, 2100, 2700, 3000])
    return k.svg()


def kitchen_tall():
    """3300 мм: мойка под витриной · посудомойка · духовая колонна · плита с вытяжкой · открытые полки."""
    k = Kitchen(3300, 'Витрины со стеклом · духовая колонна')
    k.shell()
    # духовая колонна 1500–2100 на всю высоту
    x, w = k.X(1500), 600 * S
    k.rect(0.9, 1.0, x, k.Y(2000), w, 1900 * S)
    k.fill(5.0, x + 1, k.Y(2000) + 1, w - 2, 1900 * S - 2, 'f-cab')
    k.ln(2.3, .6, f'M{n(x)} {n(k.Y(600))}H{n(x + w)}', 'thin')                  # нижний ящик
    k.ln(2.35, .5, f'M{n(x + w * .22)} {n(k.Y(350))}H{n(x + w * .78)}', 'thin')
    k.rect(2.5, .9, x + 8, k.Y(1150), w - 16, 550 * S, 'thin')                    # духовка
    k.fill(5.4, x + 8, k.Y(1150), w - 16, 550 * S, 'f-app')
    k.rect(2.7, .8, x + 20, k.Y(1060) , w - 40, 280 * S, 'thin')
    k.ln(2.8, .5, f'M{n(x + 14)} {n(k.Y(1130))}H{n(x + w - 14)}', 'thin')
    k.rect(2.9, .9, x + 8, k.Y(1500), w - 16, 330 * S, 'thin')                    # микроволновка
    k.fill(5.5, x + 8, k.Y(1500), w - 16, 330 * S, 'f-app')
    k.rect(3.0, .8, x + 18, k.Y(1450) , (w - 36) * .66, 230 * S, 'thin')
    k.ln(3.1, .5, f'M{n(x + w - 16)} {n(k.Y(1450))}V{n(k.Y(1250))}', 'thin')
    k.ln(3.2, .5, f'M{n(x + 14)} {n(k.Y(1560))}H{n(x + w - 14)}', 'thin')         # нижняя кромка верхнего шкафа
    k.ln(3.3, .5, f'M{n(x + w - 12)} {n(k.Y(1580))}V{n(k.Y(1760))}', 'thin')
    # базовые модули
    mods = [(0, 900, 'sink'), (900, 1500, 'dw'), (2100, 3000, 'hob'), (3000, 3300, 'pull')]
    for i, (a, b, kind) in enumerate(mods):
        k.base(a, b, i)
        if kind == 'sink': k.doors2(a, b); k.sink(a, b)
        if kind == 'dw':
            xx, ww = k.X(a), (b - a) * S
            k.ln(4.0, .8, f'M{n(xx + 16)} {n(k.Y(850) + 18)}H{n(xx + ww - 16)}', 'thin')
            k.rect(4.2, .8, xx + 22, k.Y(850) + 34, ww - 44, 100, 'thin')
            k.fill(5.3, xx + 22, k.Y(850) + 34, ww - 44, 100, 'f-app')
        if kind == 'hob': k.drawers(a, b, 3); k.hob(a, b)
        if kind == 'pull': k.drawers(a, b, 4)
    k.slab(0, 1500, left_over=True)
    k.slab(2100, 3300, right_over=True)
    # верхние шкафы
    k.wall(0, 900, 0, glass=True); k.wall(900, 1500, 1); k.door1(900, 1500)
    k.hood(2100, 3000)
    # открытые полки 3000–3300
    sx, sw = k.X(3000), 300 * S
    k.ln(2.4, 1.0, f'M{n(sx)} {n(k.Y(2000))}V{n(k.Y(1450))}')
    k.ln(2.5, 1.0, f'M{n(sx + sw)} {n(k.Y(2000))}V{n(k.Y(1450))}')
    for j, hh in enumerate((2000, 1730, 1450)):
        k.ln(2.6 + .15 * j, .8, f'M{n(sx)} {n(k.Y(hh))}H{n(sx + sw)}', '' if j in (0, 2) else 'thin')
    k.rect(3.8, .5, sx + 10, k.Y(1730) - 16, 14, 16, 'thin')
    k.rect(3.9, .5, sx + 30, k.Y(1730) - 22, 12, 22, 'thin')
    k.rect(4.0, .5, sx + 14, k.Y(1450) - 14, 22, 14, 'thin')
    k.dims([0, 900, 1500, 2100, 3000, 3300])
    return k.svg()


def first_kitchen():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    m = re.search(r'<svg[^>]*id="kitchen-svg"[^>]*>(.*?)</svg>', html, re.S) or \
        re.search(r'<div class="bp[^>]*id="bp"[^>]*>\s*<svg[^>]*>(.*?)</svg>', html, re.S)
    return m.group(1).strip()


if __name__ == '__main__':
    src = ROOT / 'js' / 'kitchens.js'
    # первая кухня берётся из заранее сохранённого файла (чтобы не зависеть от разметки index.html)
    base_file = ROOT / 'tools' / 'kitchen-1.svg.txt'
    if not base_file.exists():
        base_file.write_text(first_kitchen(), encoding='utf-8')
    k1 = base_file.read_text(encoding='utf-8')
    arr = [k1, kitchen_column(), kitchen_tall()]
    src.write_text('/* Сгенерировано tools/gen_kitchens.py — три чертежа кухонь для главной */\n'
                   'window.KITCHENS = ' + json.dumps(arr, ensure_ascii=False) + ';\n', encoding='utf-8')
    print('ok', [len(a) for a in arr])
