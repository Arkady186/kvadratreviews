#!/usr/bin/env python3
"""Печатная версия «Гида по материалам» ASD (A4) → guide-asd.pdf.

Запуск из корня репозитория:
  python3 -m http.server 8766 &           # локальный сервер
  python3 tools/gen_guide_pdf.py          # соберёт _pdf/guide-print.html и guide-asd.pdf
3D-рендеры образцов (_pdf/fan.png, s0..s4.png, k1.png) снимаются со страницы _r3d.html
(python3 tools/render3d.py). Шрифты: Noto Serif Display и Manrope должны быть установлены в системе.
"""
import html, io, os, re, sys
E = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_HTML = os.path.join(ROOT, '_pdf', 'guide-print.html')
OUT_PDF = os.path.join(ROOT, 'guide-asd.pdf')
SITE = 'arkady186.github.io/kvadratreviews'

P = lambda p: '../' + p  # путь к картинкам сайта из папки _pdf

FACADES = [
    dict(id='ldsp', no='01', name='ЛДСП', sub='ламинированная плита', base='древесная плита', cover='ламинат (декоративное покрытие)',
         pros=['Самый доступный вариант', 'Большой выбор декоров и фактур', 'Хорошо подходит для шкафов, прихожих и детских'],
         cons=['Форма только плоская, без фрезеровки', 'Торцы закрыты кромкой — на стыках её видно', 'Боится воды на срезах'],
         img='img/works/shkafy/shkafy-149-b2c536.webp', s=0, tier=1, where='шкафы, прихожие, детские, корпусная мебель'),
    dict(id='plenka', no='02', name='Плёнка ПВХ', sub='вакуумное прессование', base='МДФ', cover='ПВХ-плёнка',
         pros=['Доступная цена среди фасадов из МДФ', 'Подходят рамочные фасады и фрезеровка', 'Много цветов и декоров под дерево', 'Не боится влаги'],
         cons=['Подходит для кухни не в каждом случае: не любит жар у плиты и духовки', 'Цвет может выгорать на солнце', 'Повреждённое место сложно отремонтировать'],
         img='img/works/kuhni/kuhni-016-b5268e.webp', s=1, tier=1, where='шкафы и гардеробные, классические фасады; на кухне — вдали от плиты и духовки'),
    dict(id='hpl', no='03', name='Пластик HPL', sub='слоистый пластик высокого давления', base='МДФ или ЛДСП', cover='слоистый пластик',
         pros=['Очень прочное, износостойкое покрытие', 'Не боится влаги, бытовой химии и ультрафиолета', 'Много фактур: камень, бетон, дерево, глянец и мат', 'Часто используют в санузлах'],
         cons=['Форма фасада проще: в основном плоские', 'На торцах бывает заметна кромка', 'Дороже плёнки ПВХ'],
         img='img/works/sanuzly/sanuzly-009-32ee6f.webp', s=2, tier=2, where='санузлы, кухни, офисная мебель'),
    dict(id='emal', no='04', name='Эмаль', sub='краска + лак', base='МДФ', cover='слои грунта, краски и лака',
         pros=['Любой цвет — по каталогам RAL и NCS', 'Можно делать фрезеровку и фигурные фасады', '«Монолитный» вид без кромок и стыков', 'Разные эффекты: глянец, мат, металлик, перламутр'],
         cons=['Боится сильных ударов — скол придётся красить заново', 'Дороже плёнки', 'Дольше делается: каждый слой сушится'],
         img='img/works/kuhni/kuhni-026-364306.webp', s=3, tier=2, where='кухни, гостиные, спальни'),
    dict(id='massiv', no='05', name='Массив дерева', sub='дуб, ясень, бук и другие породы', base='цельная древесина', cover='защитный лак, масло или патина',
         pros=['Долговечный, при необходимости его можно отреставрировать', 'Рамочные фасады, резьба, классические формы', 'Премиальный вид'],
         cons=['Самый дорогой вариант', 'Тяжёлый, чувствителен к перепадам влаги и попаданию прямых солнечных лучей', 'Нужен уход и защитное покрытие'],
         img='img/works/kuhni/kuhni-001-81dcf6.webp', s=4, tier=3, where='классические кухни, гостиные, кабинеты'),
]
# Сравнение фасадов: 1 — слабее, 3 — лучше (ориентир, по описаниям выше)
MATRIX = [('Цена', 'tier'), ('Влагостойкость', [2, 2, 3, 2, 1]), ('Стойкость к ударам', [2, 2, 3, 1, 2]), ('Фрезеровка и сложная форма', [0, 2, 1, 3, 3]), ('Выбор цвета и декора', [3, 2, 3, 3, 1])]

CORP = [
    dict(name='ЛДСП', sub='древесная плита с ламинированным покрытием', base='древесные стружки со смолой', cover='ламинат',
         pros=['Доступная цена и большой выбор декоров', 'Подходит для большинства корпусов', 'Жёсткий и стабильный материал'],
         cons=['Боится воды на срезах без кромки', 'Не подлежит перекрашиванию', 'Тяжёлые нагрузки требуют правильной конструкции'], img='img/works/shkafy/shkafy-041-68e668.webp'),
    dict(name='Кромка', sub='защита торцов плиты', base='ПВХ или АБС', cover='закрывает срез плиты',
         pros=['Защищает торцы от влаги и грязи', 'Выбор цвета под корпус или фасад', 'Аккуратный, цельный вид'],
         cons=['Кромка 0,4 мм — самая тонкая, 2 мм — прочнее', 'У мойки и посудомойки торцы лучше закрыть толстой кромкой'], img='img/works/shkafy/shkafy-094-59835d.webp'),
]
TOPS = [
    ('ЛДСП', 'ламинированная плита', 'ЛДСП с закруглённым торцом', (38, 40), ['Доступная цена', 'Много декоров', 'Быстро изготавливается'], ['Боится воды на стыках и срезах', 'Горячее лучше не ставить']),
    ('Компакт-плита HPL', 'слоистый пластик', 'слоистый пластик по всей толщине', (10, 12), ['Очень прочная, влагостойкая и ударостойкая', 'Не боится бытовой химии', 'Тонкая и современная'], ['Цена выше, чем у ЛДСП', 'Торец виден и всегда чёрный — это сам пластик']),
    ('Искусственный камень', 'акриловый', 'акрил и минеральный наполнитель', (12, 40), ['Бесшовные стыки', 'Мелкие царапины шлифуются', 'Мойка может быть встроена заподлицо'], ['Боится горячих сковород', 'Дороже ламинированных столешниц']),
    ('Кварцевый камень', 'кварц + смола', 'кварцевый песок до 90–95%', (20, 40), ['Очень твёрдый, трудно поцарапать', 'Не впитывает жидкости', 'Стойкий цвет'], ['Высокая цена и большой вес', 'Не любит резкий жар']),
    ('Керамогранит', 'керамическая плита', 'обожжённая керамика', (12, 80), ['Не боится жара и царапин', 'Не впитывает жидкости', 'Рисунок под мрамор и бетон'], ['Хрупкая кромка', 'Нужен точный монтаж и аккуратная резка']),
    ('Натуральный камень', 'гранит, мрамор', 'природный камень', None, ['Уникальный рисунок', 'Срок службы — десятилетия', 'Благородный вид'], ['Высокая цена', 'Мрамор боится кислот, нужна пропитка']),
    ('Массив дерева', 'дуб, ясень, ореховое дерево', 'цельная древесина', None, ['Тёплый, живой материал', 'Можно отшлифовать и обновить', 'Подходит для барной стойки и острова'], ['Нужен уход: масло или лак', 'Боится воды вокруг мойки']),
]
FIT = [
    ('Петли с доводчиком', 'фасады шкафов', ['Плавное, тихое закрывание', 'Регулировка в трёх направлениях', 'Снимаются при мытье и сборке'], ['Заявленный ресурс в циклах открывания', 'Тип крепления и угол открывания']),
    ('Выдвижные ящики', 'направляющие скрытого монтажа', ['Ровный, плавный ход', 'Полное выдвижение: виден весь ящик', 'Доводчик в комплекте'], ['Допустимая нагрузка на ящик', 'Ширина и глубина под ваши предметы']),
    ('Подъёмные механизмы', 'верхние шкафы', ['Фасад поднимается вверх, не мешая работе', 'Удобно при ограниченном пространстве'], ['Подбор по весу фасада', 'Плавность хода и фиксация']),
    ('Системы хранения', 'лотки, корзины, карусели', ['Каждому предмету — своё место', 'Использование угла и узких проёмов', 'Порядок без лишних поисков'], ['Размеры под ваш набор посуды', 'Материал: нержавеющая сталь или пластик']),
    ('Ручки и профиль', 'способы открывания', ['Накладные ручки — привычно и недорого', 'Профиль-ручка — гладкий минималистичный фасад', 'Push-to-open — без ручек вообще'], ['Удобство хвата ежедневно', 'Совместимость с фасадом и толщиной']),
]
TIERS = [('Бюджетные', ['ЛДСП', 'Плёнка ПВХ', 'ЛДСП (столешница)'], 't1'), ('Средний сегмент', ['Пластик HPL', 'Эмаль', 'Искусственный камень', 'Компакт-плита'], 't2'), ('Премиум', ['Массив', 'Кварцевый камень', 'Керамогранит'], 't3')]
ROOMS = [('Кухня', 'эмаль или пластик HPL, столешница из кварца или искусственного камня', 'img/works/kuhni/kuhni-024-f7e64c.webp'),
         ('Прихожая', 'фасады из ЛДСП или эмали, полки и столешница — компакт-плита', 'img/works/shkafy/shkafy-110-c408b6.webp'),
         ('Гостиная и спальня', 'эмаль с фрезеровкой или плёнка ПВХ', 'img/works/shkafy/shkafy-138-611244.webp'),
         ('Ванная', 'пластик HPL или эмаль, влагостойкая столешница из искусственного камня', 'img/works/sanuzly/sanuzly-014-8acf25.webp')]

def ul(items, cls): return '<ul class="%s">' % cls + ''.join('<li>%s</li>' % E(x) for x in items) + '</ul>'
def rub(n): return '<span class="rub">' + ''.join('<i class="%s">₽</i>' % ('on' if i < n else '') for i in range(3)) + '</span>'
def dots(n): return '<span class="dots">' + ''.join('<i class="%s"></i>' % ('on' if i < n else '') for i in range(3)) + '</span>' if n else '<span class="no">—</span>'

pages = []
def page(body, cls='', num=True, label=''):
    n = len(pages) + 1
    foot = '' if not num else f'<footer class="pf"><span>ASD · Гид по материалам{(" · " + E(label)) if label else ""}</span><span>{n:02d}</span></footer>'
    pages.append(f'<section class="pg {cls}">{body}{foot}</section>')

# 1. Обложка
page(f'''
<div class="cv-ph"><img src="{P('img/works/kuhni/kuhni-261-10b74b.webp')}" alt=""></div>
<div class="cv-top"><img class="logo" src="{P('img/logo-light.svg')}" alt="ASD"><span>Мебель на заказ · юг России</span></div>
<img class="cv-fan" src="fan.png" alt="">
<div class="cv-tx">
  <div class="kick">Издание 2026</div>
  <h1>Гид по <em>материалам</em></h1>
  <p>Фасады, корпуса, столешницы и фурнитура: из чего сделана мебель, в чём плюсы и минусы и на что смотреть перед заказом.</p>
</div>
<div class="cv-bot"><span>Фасады</span><span>Корпуса</span><span>Столешницы</span><span>Фурнитура</span></div>
''', 'cover', num=False)

# 2. Введение и содержание
toc = [('01', 'Фасады', 'материалы, сравнение, пять разворотов', 3), ('02', 'Корпуса', 'плита и кромка', 9), ('03', 'Столешницы', 'семь материалов и толщины', 10), ('04', 'Фурнитура', 'петли, ящики, механизмы', 12), ('05', 'Цены и подборки', 'по бюджету и по комнатам', 13)]
page(f'''
<div class="in-head"><img class="logo-d" src="{P('img/logo.svg')}" alt="ASD"></div>
<h2 class="h2 big">Как выбрать мебель, которая <em>прослужит долго</em></h2>
<p class="lead">Мебель на заказ собирается из нескольких материалов: фасады видно сразу, корпус держит нагрузку, столешница работает больше всего, а фурнитурой вы пользуетесь каждый день. В этом гиде — простыми словами о каждом из них.</p>
<div class="q3">
  <div><b>1</b><h4>Бюджет</h4><p>Определите, сколько готовы вложить: от этого зависит, какие материалы рассматривать.</p></div>
  <div><b>2</b><h4>Условия</h4><p>Где будет мебель: у воды, у плиты, на солнце? Это главный фильтр для материала.</p></div>
  <div><b>3</b><h4>Вид</h4><p>Гладкий, рамочный, под дерево или камень — выберите стиль и подберите материал под него.</p></div>
</div>
<div class="toc">{''.join(f'<a><b>{no}</b><span><strong>{t}</strong><small>{s}</small></span><i>{p:02d}</i></a>' for no, t, s, p in toc)}</div>
''', 'paper', label='Введение')

# 3. Фасады — обзор
heads = ''.join(f'<th><img src="s{f["s"]}.png" alt=""><span>{E(f["name"])}</span></th>' for f in FACADES)
rows = ''
for lab, vals in MATRIX:
    cells = ''.join('<td>%s</td>' % (rub(f['tier']) if vals == 'tier' else dots(vals[i])) for i, f in enumerate(FACADES))
    rows += f'<tr><th class="rl">{E(lab)}</th>{cells}</tr>'
page(f'''
<div class="sec"><span class="no">01</span><div><h2 class="h2">Фасады</h2><p class="lead">Фасады видно сразу: они определяют внешний вид мебели и то, как она переживёт ежедневное использование. Сравните пять основных материалов — подробности на следующих страницах.</p></div></div>
<table class="mx"><thead><tr><th></th>{heads}</tr></thead><tbody>{rows}</tbody></table>
<p class="note-s">Ориентир по трёхбалльной шкале. Точная стоимость зависит от размеров, цвета и сложности проекта.</p>
<div class="tip"><b>Совет</b><p>Если не можете выбрать между двумя материалами, комбинируйте: например, нижние фасады кухни из пластика HPL, а верхние — в эмали. Так практичность сочетается с красивым цветом.</p></div>
''', 'paper', label='Фасады')

# 4–8. Фасады по одному
for f in FACADES:
    page(f'''
<div class="fp-ph"><img src="{P(f['img'])}" alt=""><span class="fp-no">{f['no']}</span></div>
<img class="fp-s" src="s{f['s']}.png" alt="">
<div class="fp-tx">
  <div class="fp-h"><h2 class="h2">{E(f['name'])}</h2><div class="sub">{E(f['sub'])}</div></div>
  <div class="fp-meta"><div><small>Основа</small><b>{E(f['base'])}</b></div><div><small>Покрытие</small><b>{E(f['cover'])}</b></div><div><small>Цена</small><b>{rub(f['tier'])}</b></div></div>
  <div class="pm"><div><h5>Плюсы</h5>{ul(f['pros'], 'pl')}</div><div><h5>Минусы</h5>{ul(f['cons'], 'mi')}</div></div>
  <div class="where"><small>Где подходит</small><p>{E(f['where'])}</p></div>
</div>''', 'paper fpage', label='Фасады')

# 9. Корпуса
cp = ''.join(f'''<article class="cp"><div class="cp-ph"><img src="{P(c['img'])}" alt=""></div><div class="cp-tx"><h3>{E(c['name'])}</h3><div class="sub">{E(c['sub'])}</div>
<div class="fp-meta s"><div><small>Основа</small><b>{E(c['base'])}</b></div><div><small>Покрытие</small><b>{E(c['cover'])}</b></div></div>
<div class="pm s"><div><h5>Плюсы</h5>{ul(c['pros'], 'pl')}</div><div><h5>Минусы</h5>{ul(c['cons'], 'mi')}</div></div></div></article>''' for c in CORP)
page(f'''<div class="sec"><span class="no">02</span><div><h2 class="h2">Корпуса</h2><p class="lead">Основа любой мебели — корпус: он держит нагрузку и определяет, сколько прослужит мебель.</p></div></div>{cp}''', 'paper', label='Корпуса')

# 10. Столешницы: обзор + толщины
bars = ''
for name, sub, base, th, pr, co in TOPS:
    if not th: continue
    a, b = th
    bars += f'<div class="bar"><span class="bn">{E(name)}</span><span class="bt"><i style="left:{a/80*100:.1f}%;width:{max(1.5,(b-a)/80*100):.1f}%"></i></span><span class="bv">{a}–{b} мм</span></div>'
page(f'''
<div class="sec"><span class="no">03</span><div><h2 class="h2">Столешницы</h2><p class="lead">Столешница работает больше всего: на неё льют, режут и ставят горячее. Сравните материалы по главному.</p></div></div>
<div class="banner"><img src="{P('img/works/kuhni/kuhni-072-4a038c.webp')}" alt=""></div>
<h4 class="h4">Толщина столешниц</h4>
<div class="bars">{bars}<div class="scale"><span>0</span><span>20</span><span>40</span><span>60</span><span>80 мм</span></div></div>
<p class="note-s">Типичные значения. Точную толщину подбираем под проект.</p>
''', 'paper', label='Столешницы')

# 11. Столешницы: карточки
cards = ''.join(f'''<article class="mc"><h3>{E(n)}</h3><div class="sub">{E(s)}</div><p class="mb">{E(b)}{(", " + str(t[0]) + "–" + str(t[1]) + " мм") if t else ""}</p>{ul(pr, 'pl')}{ul(co, 'mi')}</article>''' for n, s, b, t, pr, co in TOPS)
page(f'<h2 class="h2 mid">Семь материалов <em>для столешницы</em></h2><div class="mgrid">{cards}<div class="mc tipc"><b>Совет</b><p>Толщина, обработка торца и стык у мойки влияют на срок службы столешницы больше, чем «название» материала.</p></div></div>', 'paper', label='Столешницы')

# 12. Фурнитура
fc = ''.join(f'''<article class="mc"><h3>{E(n)}</h3><div class="sub">{E(s)}</div>{ul(pr, 'pl')}<h5>На что смотреть</h5>{ul(lk, 'mi')}</article>''' for n, s, pr, lk in FIT)
page(f'''
<div class="sec"><span class="no">04</span><div><h2 class="h2">Фурнитура</h2><p class="lead">Фурнитура — то, чем вы пользуетесь каждый день. Хорошая заметна сразу, плохая — через год.</p></div></div>
<div class="banner sm"><img src="{P('img/works/kuhni/kuhni-076-2e2654.webp')}" alt=""></div>
<div class="mgrid f">{fc}<div class="mc tipc"><b>Совет</b><p>Фурнитуру выбирают вместе с проектом: от неё зависят размеры ящиков, высота шкафов и удобство каждый день.</p></div></div>
''', 'paper', label='Фурнитура')

# 13. Цены и подборки
tiers = ''.join(f'<div class="tier {c}"><h3>{E(n)}</h3><ul>{"".join("<li>%s</li>" % E(i) for i in its)}</ul></div>' for n, its, c in TIERS)
rooms = ''.join(f'<div class="room"><img src="{P(im)}" alt=""><h4>{E(n)}</h4><p>{E(t)}</p></div>' for n, t, im in ROOMS)
page(f'''
<div class="sec"><span class="no">05</span><div><h2 class="h2">Сравнение по цене</h2><p class="lead">Ориентир по ценовым группам: точная стоимость зависит от размеров, цвета и сложности проекта.</p></div></div>
<div class="tiers">{tiers}</div>
<h2 class="h2 mid2">Подборки <em>по помещениям</em></h2>
<div class="rooms">{rooms}</div>
''', 'paper', label='Цены и подборки')

# 14. Задняя обложка
page(f'''
<img class="bk-k" src="k0.png" alt="">
<div class="bk-tx">
  <h2>Не знаете, что <em>выбрать?</em></h2>
  <p>Ответьте на несколько вопросов на сайте — дизайнер ASD подберёт материалы под вашу кухню, бюджет и образ жизни, подготовит проект и покажет образцы.</p>
  <div class="bk-links"><div><small>Опрос для дизайн-проекта</small><b>{SITE}/quiz.html</b></div><div><small>Наши работы и отзывы</small><b>{SITE}</b></div></div>
</div>
<div class="bk-bot"><img class="logo" src="{P('img/logo-light.svg')}" alt="ASD"><span>Мебель на заказ · работаем по югу России</span></div>
''', 'cover back', num=False)

CSS = r'''
@page { size: A4; margin: 0 }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact }
html, body { margin: 0; background: #888 }
body { font-family: Manrope, sans-serif; color: #1A1714; -webkit-font-smoothing: antialiased }
.pg { position: relative; width: 210mm; height: 297mm; overflow: hidden; page-break-after: always; break-after: page; background: #F4F1EC; padding: 18mm 16mm 20mm }
.pg:last-child { page-break-after: auto }
em { font-style: italic; color: #8C6239 }
.h2 { margin: 0; font: 300 30pt/1.02 'Noto Serif Display', serif; letter-spacing: -.02em }
.h2.big { font-size: 34pt; max-width: 15ch; margin-top: 14mm } .h2.mid { font-size: 24pt; margin-bottom: 8mm } .h2.mid2 { font-size: 22pt; margin: 11mm 0 5mm }
.lead { margin: 4mm 0 0; font: 400 10.5pt/1.6 Manrope, sans-serif; color: #4A433C; max-width: 135mm }
.sub { font: 600 7pt/1.3 Manrope, sans-serif; letter-spacing: .16em; text-transform: uppercase; color: #8C6239; margin-top: 2mm }
.pf { position: absolute; left: 16mm; right: 16mm; bottom: 9mm; display: flex; justify-content: space-between; font: 500 7pt Manrope, sans-serif; letter-spacing: .08em; color: #8A8177; border-top: .3mm solid #DCD5CA; padding-top: 3mm }
.pf span:last-child { font: 300 11pt 'Noto Serif Display', serif; color: #B98D5E; letter-spacing: 0 }
/* обложка */
.cover { background: #14120F; color: #FBFAF7; padding: 0 }
.cv-ph { position: absolute; left: 0; right: 0; top: 0; height: 168mm }
.cv-ph img { width: 100%; height: 100%; object-fit: cover; display: block }
.cv-ph::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(20,18,15,.55) 0%, rgba(20,18,15,0) 30%, rgba(20,18,15,.25) 65%, #14120F 100%) }
.cv-top { position: absolute; left: 16mm; right: 16mm; top: 14mm; display: flex; justify-content: space-between; align-items: center; font: 500 8pt Manrope, sans-serif; letter-spacing: .1em; color: #E9E3DA; z-index: 2 }
.logo { height: 11mm } .logo-d { height: 10mm }
.cv-fan { position: absolute; right: 2mm; top: 104mm; width: 98mm; z-index: 3; filter: drop-shadow(0 6mm 8mm rgba(0,0,0,.45)) }
.cv-tx { position: absolute; left: 16mm; right: 16mm; top: 176mm; z-index: 2 }
.kick { font: 600 7.5pt Manrope, sans-serif; letter-spacing: .24em; text-transform: uppercase; color: #C9A074 }
.cv-tx h1 { margin: 5mm 0 0; font: 300 54pt/.95 'Noto Serif Display', serif; letter-spacing: -.035em; max-width: 120mm }
.cv-tx h1 em { color: #E2C7A2 }
.cv-tx p { margin: 7mm 0 0; max-width: 105mm; font: 400 10.5pt/1.6 Manrope, sans-serif; color: #CFC7BC }
.cv-bot { position: absolute; left: 16mm; right: 16mm; bottom: 14mm; display: flex; gap: 0; border-top: .3mm solid rgba(251,250,247,.22) }
.cv-bot span { flex: 1; padding-top: 4mm; font: 300 12pt 'Noto Serif Display', serif; color: #E9E3DA }
/* введение */
.in-head { display: flex; justify-content: space-between }
.q3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6mm; margin: 12mm 0 0 }
.q3 div { background: #FBFAF7; border-radius: 4mm; padding: 6mm 5mm }
.q3 b { display: block; font: 300 28pt/1 'Noto Serif Display', serif; color: #C9A074 }
.q3 h4 { margin: 3mm 0 0; font: 400 13pt 'Noto Serif Display', serif } .q3 p { margin: 2mm 0 0; font: 400 8.5pt/1.55 Manrope, sans-serif; color: #4A433C }
.toc { margin-top: 13mm; border-top: .4mm solid #1A1714 }
.toc a { display: grid; grid-template-columns: 16mm 1fr auto; align-items: center; padding: 4.2mm 0; border-bottom: .3mm solid #DCD5CA }
.toc b { font: italic 300 14pt 'Noto Serif Display', serif; color: #B98D5E } .toc strong { display: block; font: 400 16pt/1.1 'Noto Serif Display', serif; font-weight: 400 }
.toc small { display: block; font: 400 8pt Manrope, sans-serif; color: #8A8177; margin-top: 1mm } .toc i { font: 300 14pt 'Noto Serif Display', serif; font-style: normal; color: #8A8177 }
/* раздел */
.sec { display: flex; gap: 7mm; align-items: flex-start; padding-top: 5mm; border-top: .4mm solid #1A1714; margin-bottom: 8mm }
.sec .no { font: 300 42pt/.85 'Noto Serif Display', serif; color: #C9A074; letter-spacing: -.03em }
/* матрица */
.mx { width: 100%; border-collapse: collapse; margin-top: 4mm }
.mx thead th { vertical-align: bottom; padding: 0 1mm 3mm; font: 400 10pt/1.15 'Noto Serif Display', serif; text-align: center }
.mx thead img { display: block; height: 48mm; margin: 0 auto 2mm }
.mx tbody th.rl { text-align: left; font: 600 7.5pt Manrope, sans-serif; letter-spacing: .06em; color: #4A433C; padding: 3.6mm 2mm 3.6mm 0; width: 34mm }
.mx tbody td { text-align: center; border-top: .3mm solid #DCD5CA; padding: 3.6mm 0 }
.mx tbody tr:first-child td, .mx tbody tr:first-child th { border-top: .4mm solid #1A1714 }
.dots i { display: inline-block; width: 2.4mm; height: 2.4mm; border-radius: 50%; background: #E2DCD3; margin: 0 .6mm } .dots i.on { background: #8C6239 }
.rub i { font-style: normal; font: 600 9pt Manrope, sans-serif; color: #D6CEC2; margin: 0 .3mm } .rub i.on { color: #1A1714 }
.no { color: #A79E93 }
.note-s { margin: 3mm 0 0; font: 400 7.5pt/1.5 Manrope, sans-serif; color: #8A8177 }
.tip { margin-top: 9mm; background: #1D1A16; color: #EDE6DB; border-radius: 5mm; padding: 7mm 8mm; display: grid; grid-template-columns: 26mm 1fr; gap: 4mm }
.tip b { font: 600 7.5pt Manrope, sans-serif; letter-spacing: .2em; text-transform: uppercase; color: #C9A074; padding-top: 1.5mm } .tip p { margin: 0; font: 300 12pt/1.5 'Noto Serif Display', serif }
/* страница фасада */
.fpage { padding: 0 }
.fp-ph { position: absolute; left: 0; right: 0; top: 0; height: 132mm } .fp-ph img { width: 100%; height: 100%; object-fit: cover; display: block }
.fp-no { position: absolute; left: 16mm; top: 12mm; font: 300 40pt/1 'Noto Serif Display', serif; color: #FBFAF7; text-shadow: 0 1mm 4mm rgba(0,0,0,.35) }
.fp-s { position: absolute; right: 14mm; top: 84mm; height: 88mm; z-index: 3; filter: drop-shadow(0 5mm 6mm rgba(20,18,15,.35)) }
.fp-tx { position: absolute; left: 16mm; right: 16mm; top: 142mm }
.fp-h { max-width: 125mm } .fp-h .h2 { font-size: 36pt }
.fp-meta { display: grid; grid-template-columns: 1fr 1.4fr .6fr; gap: 5mm; margin-top: 7mm; padding: 4mm 0; border-top: .4mm solid #1A1714; border-bottom: .3mm solid #DCD5CA }
.fp-meta.s { grid-template-columns: 1fr 1fr; margin-top: 4mm }
.fp-meta small, .where small { display: block; font: 600 6.5pt Manrope, sans-serif; letter-spacing: .18em; text-transform: uppercase; color: #8A8177 }
.fp-meta b { display: block; margin-top: 1.5mm; font: 400 10.5pt/1.35 Manrope, sans-serif }
.pm { display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; margin-top: 8mm } .pm.s { gap: 5mm; margin-top: 4mm }
h5 { margin: 0 0 2mm; font: 600 7pt Manrope, sans-serif; letter-spacing: .18em; text-transform: uppercase; color: #1A1714 }
ul.pl, ul.mi { list-style: none; margin: 0; padding: 0 } ul li { position: relative; padding-left: 5mm; margin: 0 0 2.4mm; font: 400 10.5pt/1.45 Manrope, sans-serif; color: #2E2924 }
ul.pl li::before { content: ""; position: absolute; left: .4mm; top: 1.7mm; width: 1.8mm; height: 1.8mm; background: #B98D5E; transform: rotate(45deg) }
ul.mi li::before { content: ""; position: absolute; left: 0; top: 2.4mm; width: 2.6mm; height: .4mm; background: #B4534A }
.where { margin-top: 8mm; background: #FBFAF7; border-radius: 3mm; padding: 4mm 5mm } .where p { margin: 1.5mm 0 0; font: 300 14pt/1.35 'Noto Serif Display', serif }
/* корпуса */
.cp { display: grid; grid-template-columns: 70mm 1fr; gap: 7mm; margin-bottom: 7mm; background: #FBFAF7; border-radius: 5mm; overflow: hidden; height: 108mm }
.cp-ph img { width: 100%; height: 100%; object-fit: cover; display: block } .cp-tx { padding: 7mm 7mm 6mm 0 }
.cp h3, .mc h3 { margin: 0; font: 300 20pt/1.05 'Noto Serif Display', serif; letter-spacing: -.01em }
.cp ul li { font-size: 9pt }
/* столешницы */
.banner { height: 72mm; border-radius: 5mm; overflow: hidden; margin-bottom: 9mm } .banner.sm { height: 38mm; margin-bottom: 5mm } .banner img { width: 100%; height: 100%; object-fit: cover; display: block }
.h4 { margin: 0 0 4mm; font: 400 16pt 'Noto Serif Display', serif }
.bars { background: #FBFAF7; border-radius: 5mm; padding: 6mm 7mm 4mm }
.bar { display: grid; grid-template-columns: 44mm 1fr 20mm; align-items: center; gap: 4mm; padding: 2.6mm 0 }
.bn { font: 400 9.5pt Manrope, sans-serif } .bv { font: 600 8.5pt Manrope, sans-serif; text-align: right; color: #8C6239 }
.bt { position: relative; height: 3.2mm; background: #ECE6DC; border-radius: 2mm } .bt i { position: absolute; top: 0; bottom: 0; background: #B98D5E; border-radius: 2mm }
.scale { display: grid; grid-template-columns: 44mm 1fr 20mm; gap: 4mm; font: 500 7pt Manrope, sans-serif; color: #8A8177; margin-top: 1mm }
.scale { position: relative } .scale span { display: none }
.mgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm }
.mc { background: #FBFAF7; border-radius: 4mm; padding: 5mm 5.5mm } .mc h3 { font-size: 15pt } .mc .sub { margin-bottom: 2.5mm }
.mc .mb { margin: 0 0 2.5mm; font: 400 8.5pt/1.4 Manrope, sans-serif; color: #6B635A } .mc ul li { font-size: 8.5pt; margin-bottom: 1.4mm } .mc ul.mi { margin-top: 2mm }
.mc h5 { margin-top: 3mm }
.tipc { background: #1D1A16; color: #EDE6DB } .tipc b { font: 600 7pt Manrope, sans-serif; letter-spacing: .2em; text-transform: uppercase; color: #C9A074 } .tipc p { margin: 3mm 0 0; font: 300 11.5pt/1.45 'Noto Serif Display', serif }
.mgrid.f { gap: 4mm } .mgrid.f .mc { padding: 4mm 5mm } .mgrid.f .mc ul li { font-size: 8.2pt }
/* цены и комнаты */
.tiers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm }
.tier { border-radius: 4mm; padding: 6mm 5mm; color: #FBFAF7; min-height: 52mm } .tier h3 { margin: 0 0 3mm; font: 300 16pt/1.1 'Noto Serif Display', serif }
.tier ul { list-style: none; margin: 0; padding: 0 } .tier li { padding: 2mm 0 2mm 0; margin: 0; border-top: .3mm solid rgba(255,255,255,.25); font: 500 8.5pt Manrope, sans-serif; color: inherit }
.tier li::before { display: none } .t1 { background: #8C6239 } .t2 { background: #3A342D } .t3 { background: #C9A074; color: #14120F } .t3 li { border-color: rgba(0,0,0,.18) }
.rooms { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm }
.room { background: #FBFAF7; border-radius: 4mm; overflow: hidden } .room img { width: 100%; height: 50mm; object-fit: cover; display: block }
.room h4 { margin: 3mm 4mm 1mm; font: 400 12pt 'Noto Serif Display', serif } .room p { margin: 0 4mm 4mm; font: 400 7.6pt/1.45 Manrope, sans-serif; color: #4A433C }
/* задняя обложка */
.back .bk-k { position: absolute; left: 18mm; top: 26mm; width: 174mm }
.bk-tx { position: absolute; left: 16mm; right: 16mm; top: 160mm }
.bk-tx h2 { margin: 0; font: 300 40pt/1 'Noto Serif Display', serif; letter-spacing: -.03em } .bk-tx h2 em { color: #E2C7A2 }
.bk-tx p { margin: 6mm 0 0; max-width: 120mm; font: 400 10.5pt/1.6 Manrope, sans-serif; color: #CFC7BC }
.bk-links { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 10mm }
.bk-links div { border: .3mm solid rgba(201,160,116,.45); border-radius: 4mm; padding: 5mm }
.bk-links small { display: block; font: 600 6.5pt Manrope, sans-serif; letter-spacing: .18em; text-transform: uppercase; color: #C9A074 } .bk-links b { display: block; margin-top: 2mm; font: 400 10pt Manrope, sans-serif; color: #FBFAF7; word-break: break-all }
.bk-bot { position: absolute; left: 16mm; right: 16mm; bottom: 14mm; display: flex; justify-content: space-between; align-items: center; border-top: .3mm solid rgba(251,250,247,.22); padding-top: 5mm; font: 500 8pt Manrope, sans-serif; color: #A79E93; letter-spacing: .06em }
'''

doc = f'<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>ASD — Гид по материалам</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
open(OUT_HTML, 'w', encoding='utf-8').write(doc)
print('html', OUT_HTML, len(pages), 'pages')

if '--html-only' in sys.argv: sys.exit()
from playwright.sync_api import sync_playwright
from PIL import Image
def route(r):
    u = r.request.url
    m = re.search(r'/(img/works/.+\.webp)$', u)
    if m:
        im = Image.open(os.path.join(ROOT, m.group(1))).convert('RGB'); im.thumbnail((1250, 1250))
        bio = io.BytesIO(); im.save(bio, 'JPEG', quality=76)
        return r.fulfill(status=200, content_type='image/jpeg', body=bio.getvalue())
    return r.continue_() if u.startswith('http://localhost') else r.abort()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.route('**/*', route)
    pg.goto('http://localhost:8766/_pdf/guide-print.html'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(800)
    pg.pdf(path=OUT_PDF, format='A4', print_background=True, margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'}, prefer_css_page_size=True)
print('pdf', OUT_PDF, os.path.getsize(OUT_PDF))
