#!/usr/bin/env python3
"""Генератор блоков главной: «Как мы работаем» (5 анимированных сцен) и «Дополнительные услуги».

Вставляет разметку и стили в design/Home.dc.html между маркерами:
  <!-- hw:start --> … <!-- hw:end -->            (секции)
  /* hw:css:start */ … /* hw:css:end */          (стили в <helmet>)
Иллюстрации — векторные (SVG) с CSS-анимацией: играют только когда блок на экране,
при «уменьшении движения» в системе показывается статичная финальная картинка.
Запуск:  python3 tools/gen_process.py && python3 tools/build_dc.py design .
"""
import os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'design', 'Home.dc.html')

INK, WALL, WALL2, FLOOR, FLOOR2 = '#1A1714', '#EFE8DD', '#E5DCCE', '#DCCDB8', '#CFBFA8'
CAR, CARD, CREAM, PAPER = '#B98D5E', '#8C6239', '#F4F1EC', '#FBFAF7'
SAGE, SAGED, DARK, DARK2 = '#7C8C86', '#3F4A46', '#2B2622', '#241F1B'
SKIN, SKIN2, HAIR, HAIR2 = '#E8B896', '#C98F6A', '#3A2A20', '#6B4A33'
RED, YEL, STEEL = '#E2513B', '#E2A93B', '#8E9592'


def o(x, y):
    """transform-origin в координатах рисунка"""
    return 'transform-origin:%gpx %gpx' % (x, y)


def limb(pts, w, c):
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round"></polyline>' % (
        ' '.join('%g,%g' % p for p in pts), c, w)


def circ(x, y, r, c, extra=''):
    return '<circle cx="%g" cy="%g" r="%g" fill="%s"%s></circle>' % (x, y, r, c, extra)


def rect(x, y, w, h, c, rx=0, extra=''):
    return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"%s></rect>' % (x, y, w, h, rx, c, extra)


def path(d, c, extra=''):
    return '<path d="%s" fill="%s"%s></path>' % (d, c, extra)


def line(x1, y1, x2, y2, c, w=1, extra=''):
    return '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="round"%s></line>' % (x1, y1, x2, y2, c, w, extra)


def face(cx, cy, d, smile=True):
    """глаз, бровь и улыбка в профиль; d=1 — смотрит вправо"""
    s = circ(cx + 5 * d, cy - 1, 1.25, INK)
    s += line(cx + 3.2 * d, cy - 4.6, cx + 6.6 * d, cy - 5, INK, .9, ' opacity=".7"')
    if smile:
        s += path('M%g %g q%g 2.4 %g 0' % (cx + 3 * d, cy + 4.5, 2.2 * d, 4.4 * d), 'none', ' stroke="%s" stroke-width=".9" stroke-linecap="round"' % INK)
    s += circ(cx + 7 * d, cy + 2.6, 1.6, '#E79A84', ' opacity=".45"')
    return s


def shoe(x, y, d, c=INK):
    return '<ellipse cx="%g" cy="%g" rx="7" ry="3.4" fill="%s"></ellipse>' % (x + 2.5 * d, y, c)


def svg(content, label):
    return ('<svg viewBox="0 0 320 240" role="img" aria-label="%s" preserveAspectRatio="xMidYMid slice" '
            'style="display:block;width:100%%;height:100%%">%s</svg>') % (label, content)


def room(wall=WALL, floor=FLOOR, fy=192, planks=True):
    s = rect(0, 0, 320, fy, wall) + rect(0, fy, 320, 240 - fy, floor) + rect(0, fy - 4, 320, 4, '#E2D6C5')
    if planks:
        for i, y in enumerate(range(fy + 12, 240, 14)):
            s += line(0, y, 320, y, FLOOR2, 1, ' opacity=".8"')
            for x in range(18 + (i % 2) * 40, 320, 80):
                s += line(x, y - 14 + 1, x, y - 1, FLOOR2, 1, ' opacity=".7"')
    return s


# ---------------------------------------------------------------- 1. Знакомимся
def scene_meet():
    s = room()
    # окно с растением
    s += rect(16, 26, 70, 86, PAPER, 2) + rect(21, 31, 60, 76, '#D5E1E2') + path('M21 31 L52 31 L21 70 Z', '#fff', ' opacity=".45"')
    s += line(51, 31, 51, 107, PAPER, 3) + line(21, 69, 81, 69, PAPER, 3) + rect(12, 110, 78, 5, '#E2D6C5', 1)
    s += '<g class="a-sway" style="%s">' % o(34, 108)
    for (dx, dy, rx, ry, a, c) in [(-6, -10, 4, 9, -30, SAGE), (5, -11, 4, 9, 30, '#5F7068'), (0, -15, 3.6, 10, 0, '#6C7D76'), (-9, -4, 3, 7, -60, '#5F7068'), (9, -5, 3, 7, 60, SAGE)]:
        s += '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s" transform="rotate(%g %g %g)"></ellipse>' % (34 + dx, 98 + dy, rx, ry, c, a, 34 + dx, 98 + dy)
    s += '</g>' + path('M26 98 h16 l-2 12 h-12 z', CAR)
    # часы
    s += circ(194, 46, 14, PAPER, ' stroke="%s" stroke-width="2"' % DARK)
    for a in range(0, 360, 30):
        r1 = 11 if a % 90 else 9.5
        s += line(194 + r1 * math.sin(math.radians(a)), 46 - r1 * math.cos(math.radians(a)), 194 + 12 * math.sin(math.radians(a)), 46 - 12 * math.cos(math.radians(a)), DARK, .9)
    s += line(194, 46, 189, 40, DARK, 2) + '<g class="a-spin8" style="%s">%s</g>' % (o(194, 46), line(194, 46, 194, 36, CAR, 1.3)) + circ(194, 46, 1.6, DARK)
    # картина с кухней
    s += rect(232, 30, 66, 46, DARK, 1.5) + rect(236, 34, 58, 38, CREAM)
    s += rect(240, 38, 50, 10, CAR, 1) + line(256.7, 38, 256.7, 48, CARD, .7) + line(273.3, 38, 273.3, 48, CARD, .7)
    s += rect(238, 55, 54, 2, INK) + rect(240, 57, 50, 11, CARD, 1) + line(256.7, 57, 256.7, 68, '#6E4C2C', .7) + line(273.3, 57, 273.3, 68, '#6E4C2C', .7)
    # стол
    s += rect(96, 146, 128, 7, CARD, 2) + rect(100, 153, 120, 3, '#6E4C2C') + line(108, 156, 108, 190, '#6E4C2C', 4) + line(212, 156, 212, 190, '#6E4C2C', 4)
    # образцы фасадов веером
    for i, (a, c) in enumerate([(-34, CAR), (-12, PAPER), (12, SAGED), (34, '#C9A074')]):
        s += '<g style="--a:%gdeg;%s" class="a-fan"><rect x="155" y="118" width="10" height="28" rx="2" fill="%s" stroke="%s" stroke-width=".8"></rect></g>' % (a, o(160, 146), c, '#CBBBA5')
    s += circ(160, 145, 1.6, DARK)
    # стулья
    s += rect(34, 112, 6, 50, SAGED, 3) + rect(34, 156, 42, 6, SAGED, 3) + line(40, 162, 37, 190, DARK, 3) + line(72, 162, 75, 190, DARK, 3)
    s += rect(282, 112, 6, 50, SAGED, 3) + rect(244, 156, 44, 6, SAGED, 3) + line(282, 162, 285, 190, DARK, 3) + line(248, 162, 245, 190, DARK, 3)
    # менеджер (смотрит вправо)
    s += limb([(54, 156), (82, 159), (85, 189)], 9, DARK2) + limb([(58, 155), (88, 157), (92, 189)], 9, DARK)
    s += shoe(86, 191, 1) + shoe(93, 191, 1)
    s += limb([(56, 122), (62, 142), (98, 147)], 7, DARK2) + circ(100, 147, 3.4, SKIN2)
    s += path('M45 158 Q43 132 50 120 Q56 111 66 111 Q75 113 77 124 L75 158 Z', DARK) + path('M60 112 L64 121 L68 112 Z', PAPER)
    s += rect(60, 104, 7, 9, SKIN2, 2)
    s += '<g class="a-nod2" style="%s">' % o(63, 110) + circ(63, 97, 11, SKIN) + path('M52 97 Q51 84 64 84 Q75 84 76 93 Q69 89 62 91 Q57 95 57 102 Q53 103 52 97 Z', HAIR) + circ(58, 99, 2.2, SKIN2) + face(63, 97, 1) + '</g>'
    s += '<g class="a-gesture" style="%s">' % o(69, 121) + limb([(69, 121), (84, 137), (106, 140)], 7, DARK) + circ(108, 139.5, 3.6, SKIN) + '</g>'
    # клиентка (смотрит влево)
    s += limb([(266, 156), (238, 159), (235, 189)], 9, '#4A3B30') + limb([(262, 155), (232, 157), (228, 189)], 9, '#5B4838')
    s += shoe(234, 191, -1, '#6E4C2C') + shoe(227, 191, -1, '#6E4C2C')
    s += limb([(266, 122), (270, 142), (246, 148)], 7, '#6B7B75') + circ(244, 148, 3.4, SKIN2)
    s += path('M275 158 Q277 132 270 120 Q264 111 254 111 Q245 113 243 124 L245 158 Z', SAGE) + path('M252 112 Q257 118 262 112', 'none', ' stroke="%s" stroke-width="1"' % PAPER)
    s += rect(253, 104, 7, 9, SKIN2, 2)
    s += '<g class="a-nod" style="%s">' % o(257, 110) + path('M268 96 Q270 112 272 124 Q266 126 262 118 Z', HAIR2) + circ(257, 97, 11, SKIN) + path('M245 96 Q245 84 257 84 Q270 84 269 98 L271 116 Q266 118 262 112 L262 100 Q260 92 251 93 Q247 95 245 99 Z', HAIR2) + circ(262, 104, 1.2, '#C9A074') + face(257, 97, -1) + '</g>'
    s += limb([(248, 121), (238, 137), (222, 143)], 7, SAGE) + circ(220, 143, 3.4, SKIN)
    # чашка с паром
    s += rect(208, 135, 9, 11, PAPER, 1.5, ' stroke="#CBBBA5" stroke-width=".8"') + path('M217 138 q4 0 4 3 q0 3 -4 3', 'none', ' stroke="#CBBBA5" stroke-width="1.2"')
    for i, x in enumerate((210, 214)):
        s += '<path class="a-steam" style="animation-delay:%gs" d="M%g 131 q-3 -4 0 -8 q3 -4 0 -8" fill="none" stroke="#B9AA95" stroke-width="1.2" stroke-linecap="round"></path>' % (i * .9, x)
    # облачка
    s += '<g class="a-pop-a" style="%s">' % o(246, 92)
    s += rect(214, 46, 64, 38, '#000', 10, ' opacity=".06" transform="translate(2 3)"') + rect(214, 46, 64, 38, PAPER, 10) + path('M238 83 L247 95 L252 83 Z', PAPER)
    s += rect(224, 53, 44, 9, 'none', 1.5, ' stroke="%s" stroke-width="1.4"' % CARD) + line(238.7, 53, 238.7, 62, CARD, 1) + line(253.3, 53, 253.3, 62, CARD, 1)
    s += line(222, 70, 270, 70, INK, 1.4) + rect(224, 71, 44, 8, CAR, 1) + line(238.7, 71, 238.7, 79, CARD, .8) + line(253.3, 71, 253.3, 79, CARD, .8)
    s += '</g><g class="a-pop-b" style="%s">' % o(84, 88)
    s += rect(78, 44, 58, 34, '#000', 10, ' opacity=".07" transform="translate(2 3)"') + rect(78, 44, 58, 34, CAR, 10) + path('M86 77 L80 90 L98 77 Z', CAR)
    s += '<g class="a-dots">' + ''.join('<circle class="a-bounce" style="animation-delay:%gs;%s" cx="%g" cy="61" r="3" fill="%s"></circle>' % (i * .15, o(95 + 12 * i, 61), 95 + 12 * i, PAPER) for i in range(3)) + '</g>'
    s += '<path class="a-check" pathLength="1" d="M97 61 l6 6 l13 -12" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>' % PAPER
    s += '</g>'
    return svg(s, 'Менеджер и клиентка обсуждают будущую кухню за столом')


# ---------------------------------------------------------------- 2. Замер
def scene_measure():
    s = rect(0, 0, 262, 196, WALL) + path('M262 0 L320 0 L320 240 L262 196 Z', WALL2) + path('M0 196 L262 196 L320 240 L0 240 Z', FLOOR)
    for y in (210, 225):
        s += line(0, y, 262 + (y - 196) * 58 / 44, y, FLOOR2, 1)
    s += rect(0, 192, 262, 4, '#E2D6C5') + path('M262 192 L320 232 L320 236 L262 196 Z', '#D9CCB9')
    s += path('M298 6 L302 8 L302 225 L298 222 Z', '#D6CABA')  # стояк
    # окно, подоконник, батарея, розетка
    s += rect(150, 38, 70, 80, PAPER, 2) + rect(155, 43, 60, 70, '#D5E1E2') + path('M155 43 L188 43 L155 86 Z', '#fff', ' opacity=".45"')
    s += line(185, 43, 185, 113, PAPER, 3) + rect(146, 116, 78, 6, '#E2D6C5', 1)
    s += rect(156, 140, 58, 30, '#F6F2EC', 3, ' stroke="#DDD3C5" stroke-width="1"') + ''.join(line(162 + i * 7, 144, 162 + i * 7, 166, '#DDD3C5', 1.2) for i in range(8))
    s += rect(232, 166, 12, 12, PAPER, 2, ' stroke="#D6CABA" stroke-width="1"') + circ(236, 172, 1, '#B5A894') + circ(240, 172, 1, '#B5A894')
    # размерная линия
    s += line(10, 24, 258, 24, CARD, 1) + line(10, 18, 10, 30, CARD, 1) + line(258, 18, 258, 30, CARD, 1)
    s += path('M10 24 l7 -3 v6 z', CARD) + path('M258 24 l-7 -3 v6 z', CARD)
    s += rect(98, 14, 76, 20, PAPER, 10, ' stroke="%s" stroke-width=".9"' % CARD)
    for i, t in enumerate(['· · ·', '1 120', '2 360', '3 450 мм']):
        s += '<text class="a-num%d" x="136" y="28" text-anchor="middle" font-family="Manrope, sans-serif" font-size="11" font-weight="700" fill="%s">%s</text>' % (i, INK, t)
    # ящик с инструментами
    s += rect(150, 184, 40, 18, CARD, 2) + rect(150, 184, 40, 5, '#6E4C2C', 2) + path('M162 184 v-5 h16 v5', 'none', ' stroke="%s" stroke-width="2"' % DARK) + rect(167, 189, 6, 4, YEL, 1)
    # лазер
    s += '<line class="a-beam" pathLength="1" x1="140" y1="125" x2="262" y2="125" stroke="%s" stroke-width="1.6" stroke-dasharray="1 1"></line>' % RED
    s += '<g class="a-ldot" style="%s">%s%s</g>' % (o(262, 125), circ(262, 125, 7, RED, ' opacity=".22"'), circ(262, 125, 2.6, RED))
    # замерщик (смотрит вправо)
    s += limb([(100, 152), (96, 197)], 9, DARK) + limb([(108, 152), (114, 197)], 9, DARK2) + shoe(97, 199, 1) + shoe(116, 199, 1)
    s += limb([(94, 114), (88, 128)], 8, CARD)
    s += path('M89 154 L88 120 Q90 107 104 105 Q118 107 120 120 L119 154 Z', CAR) + path('M98 106 L104 114 L110 106 Z', PAPER)
    s += '<text x="94" y="126" font-family="Manrope, sans-serif" font-size="5.5" font-weight="700" fill="%s">ASD</text>' % PAPER
    s += rect(88, 150, 32, 5, '#5A3E25') + rect(110, 145, 10, 10, YEL, 2) + circ(115, 150, 2.4, DARK)
    s += rect(101, 97, 7, 9, SKIN2, 2)
    s += '<g class="a-look" style="%s">' % o(104, 104) + circ(104, 90, 11, SKIN) + path('M93 91 Q92 84 97 81 L99 92 Z', HAIR) + circ(99, 92, 2.2, SKIN2) + face(104, 90, 1)
    s += path('M92 88 Q92 76 104 76 Q116 76 116 88 Z', SAGED) + path('M112 86 L127 87 Q129 89 126 91 L112 90 Z', SAGED) + circ(104, 76.5, 1.5, CAR) + '</g>'
    s += limb([(88, 128), (84, 140), (90, 143)], 6, SKIN)
    s += rect(70, 128, 24, 32, PAPER, 2, ' stroke="%s" stroke-width="1"' % CARD) + rect(77, 125, 10, 5, '#5A3E25', 1)
    s += '<path class="a-plan" pathLength="1" d="M74 135 h16 v19 h-16 z M74 146 h7 M84 135 v6" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"></path>' % CARD
    s += limb([(115, 112), (122, 121)], 8, CAR) + limb([(122, 121), (127, 128), (136, 125)], 6, SKIN) + circ(137, 125, 3.5, SKIN)
    s += rect(133, 120, 11, 10, DARK, 2) + rect(135, 122, 5, 3, '#9FD0B0', .5) + circ(144, 125, 1.5, RED)
    return svg(s, 'Замерщик измеряет помещение лазерным дальномером')


# ---------------------------------------------------------------- 3. Дизайн-проект
def scene_design():
    s = room(fy=196)
    # полка с книгами
    s += rect(36, 56, 54, 4, CARD, 1)
    for (x, w, h, c) in [(40, 6, 22, SAGED), (47, 5, 18, CAR), (53, 7, 20, SAGE), (61, 5, 16, '#C9A074')]:
        s += rect(x, 56 - h, w, h, c, 1)
    s += path('M68 56 L74 40 L79 42 L73 56 Z', DARK) + rect(234, 4, 0, 0, PAPER)
    s += ''
    # подвесной светильник
    s += line(104, 0, 104, 28, DARK, 1.2) + path('M92 40 L116 40 L110 28 L98 28 Z', DARK) + circ(104, 41, 3.5, '#F7D9A8')
    s += '<path class="a-glow" d="M94 40 L114 40 L146 132 L62 132 Z" fill="#F7D9A8" opacity=".16"></path>'
    # монитор
    s += rect(128, 28, 180, 114, '#1F1C19', 6) + rect(134, 34, 168, 102, PAPER, 2) + rect(134, 34, 14, 102, '#F0EBE3', 2)
    s += ''.join(rect(138, 40 + i * 10, 6, 6, '#CBBBA5' if i else CAR, 1.2) for i in range(5))
    s += rect(150, 36, 150, 6, '#F0EBE3') + ''.join(circ(156 + i * 6, 39, 1.3, c) for i, c in enumerate((RED, YEL, '#7DBA84')))
    # заливка проекта (появляется после эскиза)
    f = '<g class="a-fill">'
    f += rect(164, 50, 122, 26, '#EFE6D6', 1) + rect(160, 92, 130, 4, SAGED, 1) + rect(164, 96, 122, 26, CAR, 1) + rect(164, 122, 122, 4, DARK, 0)
    f += rect(164, 80, 122, 12, '#E9E2D7') + ''.join(line(164, 80 + i * 4, 286, 80 + i * 4, '#DDD3C5', .5) for i in range(1, 3))
    f += rect(226, 92, 22, 3, STEEL, 1) + path('M236 92 v-7 q0 -3 4 -3 h3', 'none', ' stroke="%s" stroke-width="1.4"' % STEEL)
    for x in (178, 208, 238, 268):
        f += rect(x, 72, 8, 1.6, DARK) + rect(x, 99, 8, 1.6, DARK)
    f += rect(276, 38, 20, 11, CAR, 3) + '<text x="286" y="46.5" text-anchor="middle" font-family="Manrope, sans-serif" font-size="7" font-weight="700" fill="%s">3D</text>' % PAPER
    f += '</g>'
    s += f
    # эскиз линиями (рисуется)
    sk = 'M164 50 h122 v26 h-122 z M204.7 50 v26 M245.3 50 v26 M160 92 h130 v4 h-130 z M164 96 h122 v26 h-122 z M194.5 96 v26 M225 96 v26 M255.5 96 v26 M164 126 h122 M164 109 h30.5'
    s += '<path class="a-sketch" pathLength="1" d="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"></path>' % (sk, INK)
    s += '<g class="a-cursor">%s</g>' % path('M0 0 L0 11 L3 8 L5.5 13 L7.5 12 L5 7 L9 7 Z', INK, ' stroke="%s" stroke-width=".8"' % PAPER)
    # стойка монитора и стол
    s += rect(212, 142, 12, 22, DARK) + rect(196, 162, 44, 5, DARK, 2.5)
    s += rect(70, 166, 250, 8, CARD, 2) + rect(74, 174, 6, 50, '#6E4C2C') + rect(308, 174, 6, 50, '#6E4C2C')
    for i, c in enumerate((CREAM, CAR, SAGED, '#C9A074')):
        s += rect(258 + i * 2, 159 - i * 2.4, 30, 2.6, c, .8)
    s += rect(84, 152, 10, 14, PAPER, 1.5, ' stroke="#CBBBA5" stroke-width=".8"') + path('M94 155 q4 0 4 3 q0 3 -4 3', 'none', ' stroke="#CBBBA5" stroke-width="1.2"')
    s += '<path class="a-steam" d="M88 148 q-3 -4 0 -8 q3 -4 0 -8" fill="none" stroke="#B9AA95" stroke-width="1.2" stroke-linecap="round"></path>'
    s += rect(102, 161, 40, 5, DARK, 1.5) + rect(106, 162, 32, 2, '#3A3430', 1)
    # кресло
    s += rect(30, 170, 44, 6, SAGED, 3) + rect(28, 126, 7, 48, SAGED, 3) + line(52, 176, 52, 206, DARK, 3)
    s += line(38, 210, 66, 210, DARK, 3) + circ(38, 213, 2.6, DARK) + circ(66, 213, 2.6, DARK)
    # дизайнер (смотрит вправо)
    s += limb([(48, 170), (82, 173), (86, 207)], 9, DARK2) + limb([(52, 169), (88, 171), (93, 207)], 9, DARK) + shoe(88, 209, 1) + shoe(95, 209, 1)
    s += limb([(48, 128), (56, 150), (98, 158)], 7, '#34403C') + circ(100, 158, 3.4, SKIN2)
    s += path('M38 172 Q36 140 44 127 Q50 119 61 119 Q71 121 73 133 L70 172 Z', SAGED) + path('M54 120 Q60 126 66 120', 'none', ' stroke="%s" stroke-width="1.2"' % SAGE)
    s += rect(57, 112, 7, 9, SKIN2, 2)
    s += '<g class="a-nod2" style="%s">' % o(60, 116) + circ(47, 93, 5.5, HAIR) + circ(60, 104, 11, SKIN) + path('M49 103 Q48 91 60 91 Q71 91 72 99 Q65 96 58 98 Q55 103 55 109 Q50 109 49 103 Z', HAIR)
    s += circ(55, 106, 2.2, SKIN2) + face(60, 104, 1) + circ(65.5, 103.5, 3.2, 'none', ' stroke="%s" stroke-width="1"' % INK) + line(62.3, 103, 56, 102, INK, .9) + '</g>'
    s += '<g class="a-scribble" style="%s">' % o(112, 154) + limb([(66, 128), (80, 146), (112, 154)], 7, SAGED) + circ(114, 155, 3.5, SKIN) + line(113, 157, 121, 147, INK, 1.6) + '</g>'
    return svg(s, 'Дизайнер рисует проект кухни на компьютере')


# ---------------------------------------------------------------- 4. Производство
def scene_make():
    s = room(wall='#E8E2D9', floor='#D5CEC3', fy=198, planks=False)
    s += line(0, 216, 320, 216, '#C9C1B4', 1) + line(120, 198, 104, 240, '#C9C1B4', 1) + line(250, 198, 262, 240, '#C9C1B4', 1)
    # перфопанель с инструментами
    s += rect(16, 26, 92, 72, '#D9C9AF', 3)
    for y in range(32, 96, 8):
        for x in range(22, 106, 8):
            s += circ(x, y, .9, '#BFAE91')
    s += rect(26, 36, 4, 30, CARD, 1) + rect(20, 32, 16, 7, SAGED, 1.5)
    s += path('M46 36 a5 5 0 1 1 0 8 l-3 28 h-3 l3 -28 a5 5 0 0 1 3 -8', SAGED)
    s += path('M62 34 h34 v12 l-4 -2 l-4 3 l-4 -3 l-4 3 l-4 -3 l-4 3 l-4 -3 l-6 2 z', '#9AA39F') + rect(56, 34, 8, 12, CARD, 2)
    s += rect(66, 60, 30, 26, 'none', 2, ' stroke="%s" stroke-width="2.4"' % SAGED) + line(72, 73, 90, 73, SAGED, 2)
    # полка с плитами
    s += rect(212, 64, 96, 4, CARD, 1)
    for i, c in enumerate(('#8C6239', '#F4F1EC', '#C9A074', '#EADBC1', SAGED)):
        s += rect(216, 58 - i * 5, 86, 5, c, 1, ' stroke="#00000014" stroke-width=".6"')
    # светильник
    s += line(164, 0, 164, 16, DARK, 1.2) + path('M148 28 L180 28 L172 16 L156 16 Z', SAGED) + circ(164, 29, 3.5, '#F7D9A8')
    s += '<path class="a-glow" d="M150 28 L178 28 L214 140 L114 140 Z" fill="#F7D9A8" opacity=".14"></path>'
    # станок
    s += rect(124, 157, 140, 40, '#5E6B66', 3) + rect(128, 197, 10, 5, DARK, 1) + rect(250, 197, 10, 5, DARK, 1)
    s += ''.join(line(136, 166 + i * 5, 170, 166 + i * 5, '#4F5B57', 1.4) for i in range(5))
    s += rect(228, 163, 28, 22, SAGED, 3) + rect(232, 167, 20, 6, '#24302D', 1.5)
    s += '<circle class="a-blink" cx="236" cy="178" r="2" fill="#7DDA8B"></circle>' + circ(244, 178, 2, RED) + circ(251, 178, 2.6, YEL)
    s += rect(92, 150, 200, 7, '#A9B1AD', 2) + rect(92, 150, 200, 2, '#C5CBC8', 1)
    # пильный диск (вращается), видна верхняя часть
    s += '<clipPath id="hwClipBlade"><rect x="170" y="110" width="60" height="40"></rect></clipPath>'
    teeth = ''.join('%s%g %g' % ('M' if i == 0 else 'L', 196 + (20 if i % 2 == 0 else 16.5) * math.cos(math.radians(i * 11.25)), 152 + (20 if i % 2 == 0 else 16.5) * math.sin(math.radians(i * 11.25))) for i in range(32)) + 'Z'
    s += '<g clip-path="url(#hwClipBlade)"><g class="a-saw" style="%s">%s%s%s%s</g></g>' % (
        o(196, 152), path(teeth, '#C8CDCB', ' stroke="#8E9592" stroke-width=".8"'), circ(196, 152, 11, '#B7BDBA'),
        ''.join(line(196, 152, 196 + 10 * math.cos(math.radians(a)), 152 + 10 * math.sin(math.radians(a)), '#9AA19E', 1.4) for a in range(0, 360, 60)), circ(196, 152, 3, '#5E6B66'))
    s += path('M178 128 Q196 116 214 128 L214 133 L178 133 Z', YEL) + line(196, 116, 196, 104, DARK, 2) + rect(186, 100, 20, 5, DARK, 1.5)
    # плита едет к диску
    s += '<g class="a-board">' + rect(36, 140, 122, 10, '#D8B585', 1.2, ' stroke="%s" stroke-width="1"' % CARD) + rect(36, 140, 122, 2.4, '#EBD3AE', 1)
    s += ''.join(path('M%g 146 q20 -1.4 40 0' % x, 'none', ' stroke="#B98D5E" stroke-width=".7"') for x in (42, 84, 112)) + '</g>'
    # опилки
    for i in range(10):
        s += '<circle class="a-dust" style="animation-delay:%.2fs;--dx:%dpx;--dy:%dpx" cx="184" cy="138" r="%.1f" fill="#C9A074"></circle>' % (i * .16, -14 - (i * 7) % 22, -10 - (i * 11) % 18, 1.4 + (i % 3) * .6)
    # стопка готовых деталей
    for i, c in enumerate(('#EADBC1', '#B98D5E', '#F4F1EC', '#C9A074', '#EADBC1')):
        s += rect(270, 200 - i * 5, 44, 5, c, 1, ' stroke="#00000014" stroke-width=".6"')
    s += '<g class="a-stack">' + rect(270, 170, 44, 5, CAR, 1, ' stroke="#00000014" stroke-width=".6"') + '</g>'
    # мастер (смотрит вправо): наушники, очки, фартук, перчатки
    s += limb([(56, 160), (51, 206)], 9, DARK) + limb([(64, 160), (70, 206)], 9, DARK2) + shoe(52, 208, 1) + shoe(72, 208, 1)
    s += limb([(52, 122), (72, 138), (90, 145)], 7, '#6B7B75') + circ(92, 145, 3.8, YEL)
    s += path('M45 162 L44 126 Q46 113 60 111 Q74 113 76 126 L75 162 Z', SAGE) + path('M50 128 L70 128 L72 162 L48 162 Z', CAR)
    s += line(52, 128, 50, 114, CARD, 1.6) + line(68, 128, 70, 114, CARD, 1.6) + rect(55, 138, 10, 7, CARD, 1.5)
    s += rect(57, 103, 7, 9, SKIN2, 2)
    s += circ(60, 96, 11, SKIN) + path('M49 95 Q49 83 61 83 Q72 83 72 92 Q65 88 58 90 Q54 94 54 100 Q50 100 49 95 Z', HAIR) + face(60, 96, 1, smile=False)
    s += path('M50 93 Q50 80 61 80 Q72 80 72 93', 'none', ' stroke="%s" stroke-width="2.6"' % YEL) + rect(48, 91, 6, 11, YEL, 3)
    s += rect(63, 91.5, 10, 5, '#9FD0E0', 2, ' stroke="%s" stroke-width=".8" opacity=".9"' % INK)
    s += '<g class="a-push">' + limb([(68, 122), (86, 136), (102, 143)], 7, SAGE) + circ(104, 143, 3.8, YEL) + '</g>'
    return svg(s, 'Мастер в цехе распиливает плиту для мебели')


# ---------------------------------------------------------------- 5. Доставка и монтаж
def scene_install():
    s = room(fy=200)
    # фартук из плитки
    s += rect(34, 104, 272, 44, '#F4F1EC') + ''.join(line(34, 104 + i * 11, 306, 104 + i * 11, '#E3D9CB', .8) for i in range(1, 4))
    s += ''.join(line(34 + i * 17, 104 + (i % 2) * 0, 34 + i * 17, 148, '#E3D9CB', .8) for i in range(1, 16))
    s += line(34, 42, 278, 42, '#9AA39F', 2)  # монтажная шина
    # верхние шкафы: левый и правый уже висят
    for x in (34, 198):
        s += rect(x, 40, 76, 56, '#EFE6D6', 2, ' stroke="#D8CBB6" stroke-width="1"') + line(x + 38, 40, x + 38, 96, '#D8CBB6', 1)
        s += rect(x + 30, 88, 6, 1.8, DARK) + rect(x + 40, 88, 6, 1.8, DARK) + rect(x, 96, 76, 3, '#00000010')
    # столешница и нижние шкафы
    s += rect(30, 146, 280, 6, SAGED, 1.5) + rect(30, 146, 280, 1.5, '#5C6863')
    s += rect(34, 152, 272, 42, CAR) + rect(34, 194, 272, 6, DARK)
    for x in (102, 170, 238):
        s += line(x, 152, x, 194, CARD, 1.2)
    s += line(34, 166, 102, 166, CARD, 1.2) + line(34, 180, 102, 180, CARD, 1.2)
    for x in (62, 128, 140, 196, 208, 264, 276):
        s += rect(x, 156, 8, 1.8, DARK)
    s += path('M132 146 v-14 q0 -6 7 -6 q6 0 6 5', 'none', ' stroke="%s" stroke-width="2.2" stroke-linecap="round"' % STEEL) + rect(128, 144, 10, 2.5, STEEL, 1)
    # коробка ASD
    s += rect(10, 204, 52, 32, '#C9A074', 2) + rect(10, 204, 52, 6, '#D9B98E', 2) + rect(32, 204, 8, 32, '#E2D2B4')
    s += '<text x="22" y="226" font-family="Manrope, sans-serif" font-size="8" font-weight="800" fill="%s">ASD</text>' % CARD
    # монтируемый шкаф + уровень (едут вместе)
    s += '<g class="a-lift">' + rect(116, 40, 76, 56, '#EFE6D6', 2, ' stroke="#D8CBB6" stroke-width="1"') + line(154, 40, 154, 96, '#D8CBB6', 1)
    s += rect(146, 88, 6, 1.8, DARK) + rect(156, 88, 6, 1.8, DARK)
    s += '<g class="a-level">' + rect(128, 33, 52, 7, YEL, 2) + rect(149, 34.5, 11, 4, '#CFEAD6', 1.5) + '<circle class="a-bubble" cx="154.5" cy="36.5" r="1.6" fill="#7DBA84"></circle>' + line(140, 34, 140, 39, '#B98A2E', .8) + line(168, 34, 168, 39, '#B98A2E', .8) + '</g>'
    s += '</g>'
    s += '<g class="a-ok" style="%s">' % o(206, 30) + circ(206, 30, 10, CAR) + path('M201 30 l3.5 3.5 l7 -7', 'none', ' stroke="%s" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"' % PAPER) + '</g>'
    # стремянка и монтажник с шуруповёртом (смотрит влево)
    s += line(240, 236, 256, 200, '#9AA39F', 3) + line(276, 236, 262, 200, '#9AA39F', 3) + rect(248, 198, 22, 4, '#7E8783', 1) + line(246, 218, 270, 218, '#9AA39F', 2.4)
    s += limb([(256, 160), (254, 198)], 9, '#2F3A37') + limb([(262, 160), (264, 198)], 9, '#26302D') + shoe(253, 200, -1) + shoe(263, 200, -1)
    s += limb([(266, 124), (270, 142), (262, 150)], 7, '#34403C')
    s += path('M247 162 L246 128 Q248 115 260 113 Q272 115 274 128 L273 162 Z', SAGED) + line(252, 128, 252, 116, CAR, 1.8) + line(268, 128, 268, 116, CAR, 1.8)
    s += rect(256, 105, 7, 9, SKIN2, 2)
    s += circ(259, 98, 11, SKIN) + path('M270 97 Q271 85 259 85 Q248 85 247 94 Q254 90 260 92 Q264 96 264 102 Q269 102 270 97 Z', HAIR) + circ(264, 100, 2.2, SKIN2) + face(259, 98, -1)
    s += path('M270 96 Q270 84 258 84 Q246 84 246 96 Z', CAR) + path('M250 94 L236 95 Q234 97 237 99 L250 98 Z', CAR)
    s += '<g class="a-drill" style="%s">' % o(214, 84)
    s += limb([(252, 120), (236, 108), (220, 92)], 7, SAGED) + circ(218, 90, 3.6, SKIN)
    s += rect(200, 79, 18, 9, YEL, 3) + rect(210, 86, 6, 12, DARK, 1.5) + rect(194, 81, 7, 5, STEEL, 1) + line(194, 83.5, 186, 83.5, '#5E6B66', 1.4)
    s += '<g class="a-spark">' + line(184, 79, 180, 75, YEL, 1.1) + line(183, 88, 179, 92, YEL, 1.1) + line(182, 83.5, 177, 83.5, YEL, 1.1) + '</g></g>'
    # монтажник спиной, держит шкаф
    s += limb([(148, 192), (145, 232)], 10, '#2F3A37') + limb([(160, 192), (164, 232)], 10, '#26302D') + shoe(144, 235, -1) + shoe(165, 235, 1)
    s += '<g class="a-lift">' + limb([(144, 160), (134, 128), (128, 100)], 7, SAGED) + circ(128, 98, 3.8, SKIN) + limb([(164, 160), (174, 128), (180, 100)], 7, SAGED) + circ(180, 98, 3.8, SKIN) + '</g>'
    s += path('M137 196 L136 160 Q139 146 154 144 Q169 146 172 160 L171 196 Z', SAGED) + line(144, 196, 146, 147, CAR, 2) + line(164, 196, 162, 147, CAR, 2)
    s += rect(142, 176, 24, 10, '#34403C', 2)
    s += rect(151, 136, 7, 9, SKIN2, 2) + circ(154, 130, 11, SKIN) + path('M143 131 Q142 118 154 118 Q166 118 165 131 Q163 138 154 139 Q145 138 143 131 Z', HAIR)
    s += path('M142 126 Q142 116 154 116 Q166 116 166 126 Z', CAR) + circ(143, 131, 2, SKIN2) + circ(165, 131, 2, SKIN2)
    return svg(s, 'Монтажники вешают шкаф и проверяют его уровнем')


STEPS = [
    ('Знакомимся', 'Обсудим задачи и поможем с выбором — даже технику', scene_meet, False),
    ('Замер', 'Специалист с опытом точно измерит помещение', scene_measure, True),
    ('Дизайн-проект', 'Покажем будущую мебель в вашем интерьере', scene_design, True),
    ('Производство', 'Изготовим мебель точно по согласованному проекту', scene_make, False),
    ('Доставка и монтаж', 'Бережно привезём и аккуратно соберём у вас дома', scene_install, False),
]

CSS = r'''
.hw-row { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:16px; list-style:none; margin:0; padding:0; }
.hw-step { position:relative; min-width:0; }
.hw-art { position:relative; aspect-ratio:4/3; border-radius:18px; overflow:hidden; background:#EFE8DD; box-shadow:0 0 0 1px rgba(26,23,20,.06); transform:translateZ(0); }
.hw[data-play] .hw-art { animation:hw-active 16s cubic-bezier(.2,.8,.2,1) infinite; animation-delay:calc(var(--i) * 3.2s); }
@keyframes hw-active { 0%,18% { transform:translateY(-8px); box-shadow:0 0 0 2px #B98D5E, 0 26px 40px -26px rgba(140,98,57,.75); } 25%,100% { transform:none; box-shadow:0 0 0 1px rgba(26,23,20,.06); } }
.hw-num { position:absolute; left:12px; top:10px; z-index:2; display:grid; place-items:center; width:30px; height:30px; border-radius:50%; background:#FBFAF7; color:#8C6239; font:400 17px/1 'Noto Serif Display', serif; box-shadow:0 6px 14px -8px rgba(26,23,20,.5); }
.hw-free { position:absolute; right:10px; bottom:10px; z-index:2; padding:6px 10px 5px; border-radius:999px; background:#8C6239; color:#FBFAF7; font:700 10px/1.2 Manrope, sans-serif; letter-spacing:.12em; text-transform:uppercase; white-space:nowrap; box-shadow:0 6px 14px -8px rgba(26,23,20,.6); }
.hw-track { position:relative; height:2px; margin:0 0 22px; background:#DCD2C3; border-radius:2px; }
.hw-track i { position:absolute; top:-5px; width:12px; height:12px; margin-left:-6px; border-radius:50%; background:#F4F1EC; border:2px solid #B98D5E; box-sizing:border-box; }
.hw-track b { position:absolute; left:10%; top:-7px; width:16px; height:16px; margin-left:-8px; border-radius:50%; background:#B98D5E; box-shadow:0 0 0 6px rgba(185,141,94,.22); }
.hw[data-play] .hw-track b { animation:hw-travel 16s linear infinite; }
.hw-track s { position:absolute; left:0; top:0; height:2px; width:0; background:#B98D5E; text-decoration:none; }
.hw[data-play] .hw-track s { animation:hw-fillbar 16s linear infinite; }
@keyframes hw-travel { 0% { left:0; } 100% { left:100%; } }
@keyframes hw-fillbar { 0% { width:0; } 100% { width:100%; } }
.hw svg * { animation-play-state:paused !important; }
.hw[data-play] svg * { animation-play-state:running !important; }
.hw svg [class^="a-"] { transform-box:view-box; }
/* сцена 1 */
.a-sway { animation:hw-sway 4s ease-in-out infinite alternate; }
@keyframes hw-sway { from { transform:rotate(-4deg); } to { transform:rotate(4deg); } }
.a-spin8 { animation:hw-spin 8s linear infinite; }
@keyframes hw-spin { to { transform:rotate(360deg); } }
.a-fan { transform:rotate(var(--a)); animation:hw-fan 8s cubic-bezier(.3,.7,.2,1) infinite; }
@keyframes hw-fan { 0%,6% { transform:rotate(0); } 18%,88% { transform:rotate(var(--a)); } 100% { transform:rotate(0); } }
.a-gesture { animation:hw-gesture 2.6s ease-in-out infinite alternate; }
@keyframes hw-gesture { from { transform:rotate(-7deg); } to { transform:rotate(5deg); } }
.a-nod { animation:hw-nod 8s ease-in-out infinite; }
@keyframes hw-nod { 0%,48%,100% { transform:none; } 54% { transform:rotate(-7deg); } 60% { transform:none; } 66% { transform:rotate(-7deg); } 72% { transform:none; } }
.a-nod2 { animation:hw-nod2 8s ease-in-out infinite; }
@keyframes hw-nod2 { 0%,100% { transform:none; } 20%,34% { transform:rotate(4deg); } 46% { transform:none; } }
.a-steam { animation:hw-steam 2.4s ease-out infinite; }
@keyframes hw-steam { 0% { transform:translateY(4px); opacity:0; } 40% { opacity:.9; } 100% { transform:translateY(-6px); opacity:0; } }
.a-pop-a { animation:hw-pop-a 8s cubic-bezier(.3,1.4,.5,1) infinite; }
@keyframes hw-pop-a { 0%,4% { transform:scale(0); opacity:0; } 11%,40% { transform:scale(1); opacity:1; } 45%,100% { transform:scale(0); opacity:0; } }
.a-pop-b { animation:hw-pop-b 8s cubic-bezier(.3,1.4,.5,1) infinite; }
@keyframes hw-pop-b { 0%,46% { transform:scale(0); opacity:0; } 53%,90% { transform:scale(1); opacity:1; } 96%,100% { transform:scale(0); opacity:0; } }
.a-dots { animation:hw-dots 8s step-end infinite; }
@keyframes hw-dots { 0% { opacity:1; } 66% { opacity:0; } 100% { opacity:1; } }
.a-bounce { animation:hw-bounce .9s ease-in-out infinite; }
@keyframes hw-bounce { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-3px); } }
.a-check { stroke-dasharray:1; stroke-dashoffset:0; animation:hw-check 8s ease-out infinite; }
@keyframes hw-check { 0%,66% { stroke-dashoffset:1; } 74%,100% { stroke-dashoffset:0; } }
/* сцена 2 */
.a-beam { stroke-dasharray:1; animation:hw-beam 7s ease-out infinite; }
@keyframes hw-beam { 0%,8% { stroke-dashoffset:1; opacity:1; } 18%,86% { stroke-dashoffset:0; opacity:1; } 92%,100% { stroke-dashoffset:0; opacity:0; } }
.a-ldot { animation:hw-ldot 7s ease-out infinite; }
@keyframes hw-ldot { 0%,17% { opacity:0; transform:scale(.4); } 21% { opacity:1; transform:scale(1.4); } 26%,86% { opacity:1; transform:scale(1); } 92%,100% { opacity:0; } }
.a-num0, .a-num1, .a-num2 { opacity:0; }
.a-num0 { animation:hw-n0 7s step-end infinite; }
.a-num1 { animation:hw-n1 7s step-end infinite; }
.a-num2 { animation:hw-n2 7s step-end infinite; }
.a-num3 { animation:hw-n3 7s step-end infinite; }
@keyframes hw-n0 { 0% { opacity:1; } 22% { opacity:0; } 100% { opacity:1; } }
@keyframes hw-n1 { 0% { opacity:0; } 22% { opacity:1; } 28% { opacity:0; } }
@keyframes hw-n2 { 0% { opacity:0; } 28% { opacity:1; } 34% { opacity:0; } }
@keyframes hw-n3 { 0% { opacity:0; } 34% { opacity:1; } 94% { opacity:0; } }
.a-plan { stroke-dasharray:1; animation:hw-plan 7s ease-in-out infinite; }
@keyframes hw-plan { 0%,40% { stroke-dashoffset:1; } 70%,94% { stroke-dashoffset:0; } 100% { stroke-dashoffset:1; } }
.a-look { animation:hw-look 7s ease-in-out infinite; }
@keyframes hw-look { 0%,14%,100% { transform:none; } 20%,36% { transform:rotate(-5deg); } 46%,70% { transform:rotate(8deg); } }
/* сцена 3 */
.a-glow { animation:hw-glow 3s ease-in-out infinite alternate; }
@keyframes hw-glow { from { opacity:.1; } to { opacity:.22; } }
.a-sketch { stroke-dasharray:1; animation:hw-sketch 9s ease-in-out infinite; }
@keyframes hw-sketch { 0%,4% { stroke-dashoffset:1; } 40%,94% { stroke-dashoffset:0; } 100% { stroke-dashoffset:1; } }
.a-fill { animation:hw-fillin 9s ease-in-out infinite; }
@keyframes hw-fillin { 0%,40% { opacity:0; } 52%,90% { opacity:1; } 96%,100% { opacity:0; } }
.a-cursor { transform:translate(270px,112px); animation:hw-cursor 9s ease-in-out infinite; }
@keyframes hw-cursor { 0% { transform:translate(166px,52px); } 12% { transform:translate(286px,60px); } 22% { transform:translate(166px,98px); } 32% { transform:translate(282px,118px); } 42% { transform:translate(226px,92px); } 56% { transform:translate(286px,44px); } 70%,100% { transform:translate(250px,112px); } }
.a-scribble { animation:hw-scribble 1.3s ease-in-out infinite; }
@keyframes hw-scribble { 0%,100% { transform:translate(0,0); } 25% { transform:translate(3px,-1.5px); } 50% { transform:translate(-1px,1px); } 75% { transform:translate(2px,1px); } }
/* сцена 4 */
.a-saw { animation:hw-spin .45s linear infinite; }
.a-board { animation:hw-board 6s ease-in-out infinite; }
@keyframes hw-board { 0% { transform:translateX(-14px); opacity:0; } 6% { opacity:1; } 72% { transform:translateX(74px); opacity:1; } 80%,100% { transform:translateX(74px); opacity:0; } }
.a-push { animation:hw-push 6s ease-in-out infinite; }
@keyframes hw-push { 0%,6% { transform:translateX(-6px); } 30% { transform:translateX(4px); } 72%,100% { transform:translateX(-6px); } }
.a-dust { opacity:0; animation:hw-dust 1.1s ease-out infinite; }
@keyframes hw-dust { 0% { transform:translate(0,0); opacity:0; } 15% { opacity:.95; } 100% { transform:translate(var(--dx),var(--dy)); opacity:0; } }
.a-blink { animation:hw-blink 1s steps(2,jump-none) infinite; }
@keyframes hw-blink { 0% { opacity:1; } 100% { opacity:.2; } }
.a-stack { animation:hw-stack 6s cubic-bezier(.3,1.3,.5,1) infinite; }
@keyframes hw-stack { 0%,74% { transform:translateY(-22px); opacity:0; } 82%,94% { transform:none; opacity:1; } 100% { transform:none; opacity:0; } }
/* сцена 5 */
.a-lift { animation:hw-lift 8s cubic-bezier(.3,.9,.3,1) infinite; }
@keyframes hw-lift { 0% { transform:translateY(12px); } 26% { transform:translateY(-3px); } 32%,100% { transform:none; } }
.a-drill { animation:hw-drill 8s linear infinite; }
@keyframes hw-drill { 0%,30% { transform:translate(8px,6px) rotate(6deg); } 36% { transform:none; } 37% { transform:translate(.6px,.3px); } 38% { transform:none; } 39% { transform:translate(-.5px,.4px); } 40% { transform:none; } 41% { transform:translate(.6px,-.3px); } 42% { transform:none; } 43% { transform:translate(-.6px,.3px); } 44% { transform:none; } 45% { transform:translate(.5px,.4px); } 46%,54% { transform:none; } 62%,100% { transform:translate(8px,6px) rotate(6deg); } }
.a-spark { opacity:0; animation:hw-sparkle 8s linear infinite; }
@keyframes hw-sparkle { 0%,36% { opacity:0; } 37%,46% { opacity:1; } 47%,100% { opacity:0; } }
.a-level { animation:hw-levelin 8s ease-out infinite; }
@keyframes hw-levelin { 0%,52% { opacity:0; transform:translateY(-8px); } 58%,92% { opacity:1; transform:none; } 98%,100% { opacity:0; } }
.a-bubble { animation:hw-bubble 8s ease-in-out infinite; }
@keyframes hw-bubble { 0%,58% { transform:translateX(-5px); } 70%,100% { transform:none; } }
.a-ok { animation:hw-ok 8s cubic-bezier(.3,1.5,.5,1) infinite; }
@keyframes hw-ok { 0%,72% { transform:scale(0); opacity:0; } 78%,93% { transform:scale(1); opacity:1; } 98%,100% { transform:scale(0); opacity:0; } }
@media (max-width: 900px) {
  .hw-row { display:flex; overflow-x:auto; scroll-snap-type:x mandatory; gap:12px; margin:0 calc(-1 * clamp(20px,4vw,56px)); padding:4px clamp(20px,4vw,56px) 10px; scrollbar-width:none; -webkit-overflow-scrolling:touch; }
  .hw-row::-webkit-scrollbar { display:none; }
  .hw-step { flex:0 0 min(74vw,300px); scroll-snap-align:start; scroll-margin-left:clamp(20px,4vw,56px); }
  .hw-track { display:none; }
  .hw[data-play] .hw-art { animation:none; }
}
@media (min-width: 901px) { .hw-swipe { display:none !important; } }
/* доп. услуги */
.xs-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }
.xs-tile { position:relative; display:flex; flex-direction:column; gap:12px; padding:16px 16px 18px; border-radius:16px; background:#F4F1EC; box-shadow:0 0 0 1px rgba(26,23,20,.05); transition:transform .35s cubic-bezier(.2,.8,.2,1), box-shadow .35s, background .35s; }
.xs-tile:hover { transform:translateY(-4px); background:#FBFAF7; box-shadow:0 0 0 1px rgba(185,141,94,.5), 0 18px 30px -22px rgba(26,23,20,.45); }
.xs-tile svg { width:52px; height:52px; overflow:visible; }
.xs-call { transition:background .3s, color .3s; } .xs-call:hover { background:#1A1714; color:#FBFAF7 !important; }
.xs-tag { position:absolute; right:14px; top:14px; font:600 9.5px/1 Manrope, sans-serif; letter-spacing:.16em; text-transform:uppercase; color:#8C6239; }
.xs-name { font:600 14.5px/1.3 Manrope, sans-serif; color:#1A1714; }
.xs svg * { animation-play-state:paused !important; transform-box:view-box; }
.xs[data-play] svg * { animation-play-state:running !important; }
.x-bounce { animation:hw-xbounce 2.4s ease-in-out infinite; }
@keyframes hw-xbounce { 0%,60%,100% { transform:none; } 70% { transform:translateY(-3px); } 80% { transform:translateY(1px); } 88% { transform:none; } }
.x-drum { animation:hw-spin 2.2s linear infinite; }
.x-steam { animation:hw-steam 2.2s ease-out infinite; }
.x-rock { animation:hw-rock 3s ease-in-out infinite; }
@keyframes hw-rock { 0%,100% { transform:rotate(0); } 50% { transform:rotate(-6deg); } }
.x-z { opacity:0; animation:hw-z 3s ease-out infinite; }
@keyframes hw-z { 0% { opacity:0; transform:translate(0,0) scale(.6); } 30% { opacity:1; } 100% { opacity:0; transform:translate(8px,-14px) scale(1.1); } }
.x-roll { animation:hw-roll 2.8s ease-in-out infinite alternate; }
@keyframes hw-roll { from { transform:translateY(0); } to { transform:translateY(-20px); } }
.x-paint { transform-origin:0 50px; animation:hw-paint 2.8s ease-in-out infinite alternate; }
@keyframes hw-paint { from { transform:scaleY(.2); } to { transform:scaleY(1); } }
.x-drop { animation:hw-drop 1.8s cubic-bezier(.5,0,1,.6) infinite; }
@keyframes hw-drop { 0%,20% { transform:translateY(0) scale(.3); opacity:0; } 35% { transform:translateY(0) scale(1); opacity:1; } 90% { transform:translateY(16px); opacity:1; } 100% { transform:translateY(18px); opacity:0; } }
.x-sun { animation:hw-spin 12s linear infinite; }
.x-grow { animation:hw-grow 3.4s ease-in-out infinite alternate; }
@keyframes hw-grow { from { transform:scale(.7); } to { transform:scale(1.05); } }
@media (max-width: 900px) { .xs-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; } .xs-wrap { grid-template-columns:minmax(0,1fr) !important; } .xs-tile { flex-direction:row; align-items:center; gap:10px; padding:10px 12px; border-radius:14px; } .xs-tile svg { width:38px; height:38px; flex:none; } .xs-tag { display:none; } .xs-name { font-size:13.5px; } }
@media (prefers-reduced-motion: reduce) { .hw *, .xs * { animation:none !important; } .a-num0, .a-num1, .a-num2, .a-dots { display:none; } .a-num3, .a-dust { opacity:1; } }
'''


def step_html(i, title, text, scene, free):
    badge = '<span class="hw-free">Бесплатно</span>' if free else ''
    return ('<li class="hw-step" data-reveal="%d" style="--i:%d">'
            '<div class="hw-art"><span class="hw-num">%d</span>%s%s</div>'
            '<h3 style="margin:14px 0 0;font:400 clamp(1.15rem,1.5vw,1.4rem)/1.2 \'Noto Serif Display\', serif;letter-spacing:-.01em">%s</h3>'
            '<p style="margin:6px 0 0;color:#6B635A;font:400 14px/1.55 Manrope, sans-serif;text-wrap:pretty">%s</p>'
            '</li>') % (i, i, i + 1, badge, scene(), title, text)


SVC = [
    ('Подбор', 'Диваны', '<path d="M8 30 h36 v10 h-36 z M6 24 a4 4 0 0 1 8 0 v16 h-8 z M38 24 a4 4 0 0 1 8 0 v16 h-8 z M10 44 v4 M42 44 v4" fill="none" stroke="#1A1714" stroke-width="1.5" stroke-linejoin="round"/><g class="x-bounce"><rect x="14" y="20" width="12" height="10" rx="3" fill="#B98D5E"/><rect x="27" y="20" width="12" height="10" rx="3" fill="#C9A074"/></g><path d="M14 18 q12 -10 25 0" fill="none" stroke="#1A1714" stroke-width="1.5"/>'),
    ('Подбор', 'Бытовая техника', '<rect x="10" y="4" width="32" height="44" rx="3" fill="none" stroke="#1A1714" stroke-width="1.5"/><line x1="10" y1="13" x2="42" y2="13" stroke="#1A1714" stroke-width="1.5"/><circle cx="16" cy="8.5" r="1.6" fill="#B98D5E"/><circle cx="22" cy="8.5" r="1.6" fill="#1A1714"/><circle cx="26" cy="30" r="11" fill="none" stroke="#1A1714" stroke-width="1.5"/><g class="x-drum" style="transform-origin:26px 30px"><circle cx="26" cy="30" r="7.5" fill="#E9E1D4"/><path d="M19 30 q3.5 -4 7 0 t7 0" fill="none" stroke="#B98D5E" stroke-width="1.6"/><circle cx="23" cy="26" r="1.2" fill="#B98D5E"/></g>'),
    ('Подбор', 'Столы', '<path d="M4 22 h44 M8 22 v24 M44 22 v24 M12 30 h28" fill="none" stroke="#1A1714" stroke-width="1.5" stroke-linecap="round"/><rect x="4" y="19" width="44" height="4" rx="1" fill="#B98D5E"/><rect x="20" y="11" width="9" height="8" rx="1.5" fill="none" stroke="#1A1714" stroke-width="1.4"/><path d="M29 13 q3 0 3 2.5 t-3 2.5" fill="none" stroke="#1A1714" stroke-width="1.3"/><path class="x-steam" d="M24 8 q-2 -3 0 -6" fill="none" stroke="#B98D5E" stroke-width="1.3" stroke-linecap="round"/>'),
    ('Подбор', 'Стулья', '<g class="x-rock" style="transform-origin:16px 48px"><path d="M16 4 v26 M16 30 h22 v18 M16 30 v18 M20 39 h14" fill="none" stroke="#1A1714" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><rect x="13" y="4" width="7" height="22" rx="3" fill="#B98D5E"/><rect x="14" y="27" width="26" height="4" rx="1.5" fill="#C9A074"/></g>'),
    ('Подбор', 'Матрасы', '<rect x="4" y="26" width="44" height="14" rx="4" fill="#F4E9DA" stroke="#1A1714" stroke-width="1.5"/><path d="M4 33 h44" stroke="#B98D5E" stroke-width="1.2" stroke-dasharray="3 3"/><rect x="8" y="20" width="14" height="6" rx="3" fill="#B98D5E"/><path d="M6 40 v6 M46 40 v6" stroke="#1A1714" stroke-width="1.5" stroke-linecap="round"/><text class="x-z" x="32" y="18" font-family="Manrope, sans-serif" font-size="9" font-weight="700" fill="#8C6239">z</text><text class="x-z" style="animation-delay:1.5s" x="38" y="14" font-family="Manrope, sans-serif" font-size="7" font-weight="700" fill="#8C6239">z</text>'),
    ('Помощь', 'Ремонт', '<rect x="6" y="6" width="22" height="42" fill="#EFE8DD"/><rect class="x-paint" x="6" y="6" width="22" height="44" fill="#C9A074" opacity=".55"/><g class="x-roll"><rect x="4" y="30" width="26" height="8" rx="3" fill="#B98D5E" stroke="#1A1714" stroke-width="1.4"/><path d="M30 34 h8 v12 h-12 v6" fill="none" stroke="#1A1714" stroke-width="1.5" stroke-linejoin="round"/><rect x="23" y="51" width="6" height="2" fill="#1A1714"/></g>'),
    ('Помощь', 'Установка сантехники', '<path d="M8 20 h12 a10 10 0 0 1 10 10 v4" fill="none" stroke="#1A1714" stroke-width="5" stroke-linecap="round"/><path d="M8 20 h12 a10 10 0 0 1 10 10 v4" fill="none" stroke="#E9E1D4" stroke-width="2.4" stroke-linecap="round"/><rect x="10" y="10" width="8" height="5" rx="1.5" fill="#B98D5E"/><line x1="14" y1="15" x2="14" y2="19" stroke="#1A1714" stroke-width="1.5"/><path class="x-drop" style="transform-origin:30px 38px" d="M30 36 q-3 4 0 5 q3 -1 0 -5 z" fill="#7FB3C8"/><path d="M18 50 h24" stroke="#1A1714" stroke-width="1.5" stroke-linecap="round"/>'),
    ('Помощь', 'Обустройство балконов', '<g class="x-sun" style="transform-origin:40px 10px"><circle cx="40" cy="10" r="4" fill="#E2A93B"/><path d="M40 1 v3 M40 16 v3 M31 10 h3 M46 10 h3 M34 4 l2 2 M44 14 l2 2 M46 4 l-2 2 M36 14 l-2 2" stroke="#E2A93B" stroke-width="1.2" stroke-linecap="round"/></g><path d="M4 30 h44 M4 48 h44 M8 30 v18 M16 30 v18 M24 30 v18 M32 30 v18 M40 30 v18 M48 30 v18" fill="none" stroke="#1A1714" stroke-width="1.4"/><rect x="10" y="22" width="12" height="8" rx="1.5" fill="#B98D5E"/><g class="x-grow" style="transform-origin:16px 22px"><ellipse cx="13" cy="15" rx="3" ry="6" fill="#7C8C86" transform="rotate(-25 13 15)"/><ellipse cx="19" cy="15" rx="3" ry="6" fill="#5F7068" transform="rotate(25 19 15)"/><ellipse cx="16" cy="12" rx="2.4" ry="7" fill="#6C7D76"/></g>'),
]


def section():
    steps = ''.join(step_html(i, t, d, f, fr) for i, (t, d, f, fr) in enumerate(STEPS))
    track = '<div class="hw-track" aria-hidden="true">' + ''.join('<i style="left:%g%%"></i>' % (10 + 20 * i) for i in range(5)) + '<s></s><b></b></div>'
    hw = ('<section id="process" class="hw" data-play-scope="" data-screen-label="04 Process" style="padding:clamp(48px,5.5vw,80px) 0 clamp(40px,4.5vw,64px);background:#F4F1EC;overflow:hidden">'
          '<div style="max-width:1440px;margin:0 auto;padding:0 clamp(20px,4vw,56px)">'
          '<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:16px 40px;margin-bottom:clamp(24px,3vw,40px)">'
          '<div data-reveal="0">'
          '<div style="display:flex;align-items:center;gap:14px;font:600 11.5px/1 Manrope, sans-serif;letter-spacing:.24em;text-transform:uppercase;color:#8C6239;margin-bottom:16px"><span style="width:36px;height:1px;background:currentColor"></span>Как мы работаем</div>'
          '<h2 style="margin:0;font:300 clamp(2rem,3.6vw,3.4rem)/1.02 \'Noto Serif Display\', serif;letter-spacing:-.03em;text-wrap:balance">От вашей идеи — к <em style="font-style:italic;color:#8C6239">уюту в доме</em></h2>'
          '</div>'
          '<div data-reveal="1" style="display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px">'
          '<span style="display:inline-flex;align-items:center;gap:10px;padding:11px 18px;border-radius:999px;background:#1A1714;color:#FBFAF7;font:600 14px/1.2 Manrope, sans-serif">'
          '<span style="width:8px;height:8px;border-radius:50%;background:#C9A074;box-shadow:0 0 0 4px rgba(201,160,116,.25)"></span>Замер и дизайн-проект — бесплатно</span>'
          '<span class="hw-swipe" style="font:500 13px/1 Manrope, sans-serif;color:#8C6239">Листайте →</span>'
          '</div></div>'
          + track +
          '<ol class="hw-row">' + steps + '</ol>'
          '</div></section>')
    tiles = ''.join('<div class="xs-tile" data-reveal="%d"><span class="xs-tag">%s</span><svg viewBox="0 0 52 52" aria-hidden="true">%s</svg><span class="xs-name">%s</span></div>' % (
        i % 4, tag, ic, name) for i, (tag, name, ic) in enumerate(SVC))
    xs = ('<section id="extra" class="xs" data-play-scope="" data-screen-label="04b Extra" style="padding:clamp(48px,5.5vw,84px) 0;background:#FBFAF7">'
          '<div class="xs-wrap" style="max-width:1440px;margin:0 auto;padding:0 clamp(20px,4vw,56px);display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,2fr);gap:28px clamp(32px,4vw,64px);align-items:center">'
          '<div data-reveal="0">'
          '<div style="display:flex;align-items:center;gap:14px;font:600 11.5px/1 Manrope, sans-serif;letter-spacing:.24em;text-transform:uppercase;color:#8C6239;margin-bottom:16px"><span style="width:36px;height:1px;background:currentColor"></span>Дополнительные услуги</div>'
          '<h2 style="margin:0;font:300 clamp(1.9rem,3vw,2.9rem)/1.05 \'Noto Serif Display\', serif;letter-spacing:-.03em;text-wrap:balance">Поможем не только <em style="font-style:italic;color:#8C6239">с мебелью</em></h2>'
          '<p style="margin:14px 0 0;max-width:36ch;color:#6B635A;font:400 15px/1.6 Manrope, sans-serif;text-wrap:pretty">Подберём всё для уютного дома и поможем с ремонтом — не придётся искать других мастеров.</p>'
          '<a href="tel:+79185513330" style="display:inline-flex;align-items:center;gap:10px;margin-top:20px;padding:12px 20px;border-radius:999px;border:1px solid #1A1714;font:600 14px/1 Manrope, sans-serif;text-decoration:none" class="xs-call">Обсудить по телефону<span aria-hidden="true">→</span></a>'
          '</div>'
          '<div class="xs-grid">' + tiles + '</div>'
          '</div></section>')
    return hw + '\n\n  ' + xs


def main():
    src = open(TPL, encoding='utf-8').read()
    block = '  <!-- hw:start -->\n  ' + section() + '\n  <!-- hw:end -->'
    if '<!-- hw:start -->' in src:
        src = re.sub(r'  <!-- hw:start -->.*?<!-- hw:end -->', lambda m: block, src, flags=re.S)
    else:
        a = src.index('  <section id="process"')
        b = src.index('</section>', a) + len('</section>')
        src = src[:a] + block + src[b:]
    css = '/* hw:css:start */' + CSS + '/* hw:css:end */'
    if '/* hw:css:start */' in src:
        src = re.sub(r'/\* hw:css:start \*/.*?/\* hw:css:end \*/', lambda m: css, src, flags=re.S)
    else:
        src = src.replace('  </style>\n</helmet>', '    ' + css + '\n  </style>\n</helmet>', 1)
    js = ('    this.playScope();\n')
    if 'this.playScope();' not in src:
        src = src.replace('    this.reveal();\n    if (!this.reduce) {', '    this.reveal();\n' + js + '    if (!this.reduce) {', 1)
        src = src.replace('  heroIn() {', '''  playScope() {
    // анимации иллюстраций играют только когда блок виден на экране
    const els = document.querySelectorAll('[data-play-scope]');
    if (!('IntersectionObserver' in window)) { els.forEach((el) => el.setAttribute('data-play', '')); return; }
    this.playIo = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) en.target.setAttribute('data-play', ''); else en.target.removeAttribute('data-play'); }), { threshold: 0.08 });
    els.forEach((el) => this.playIo.observe(el));
  }
  heroIn() {''', 1)
    open(TPL, 'w', encoding='utf-8').write(src)
    print('ok', len(src))


if __name__ == '__main__':
    main()
