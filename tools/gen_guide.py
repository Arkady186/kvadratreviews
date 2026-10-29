import json,html,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(ROOT,'js','works-data.js')).read()
d=json.loads(s[s.index('{'):s.rindex('}')+1])
K=[i for i in d['items'] if i['cat']=='kuhni']
def ph(idx): return K[idx]['full']
E=html.escape
SERIF="'Noto Serif Display', 'Bitstream Charter', Georgia, serif"
SANS="Manrope, Inter, sans-serif"

def ul(items,cls):
    return '<ul class="g-ul %s">'%cls+''.join('<li>%s</li>'%E(x) for x in items)+'</ul>'

MID={'ЛДСП':'ldsp','Плёнка ПВХ':'plenka','Пластик HPL':'hpl','Эмаль':'emal','Массив дерева':'massiv'}
USED=set()
def card(n,name,sub,base,cover,pros,cons,img,flip,alt):
    mid=MID.get(name)
    idattr=''
    if mid and mid not in USED: USED.add(mid); idattr=' id="m-%s"'%mid
    rows=''
    if base: rows+='<div class="g-k">Основа</div><div class="g-v">%s</div>'%E(base)
    if cover: rows+='<div class="g-k">Покрытие</div><div class="g-v">%s</div>'%E(cover)
    return f'''<article class="g-card{' g-flip' if flip else ''}"{idattr} data-in="1" data-tilt="1">
  <div class="g-ph"><img src="{img if isinstance(img,str) else ph(img)}" alt="{E(alt)}" loading="lazy"></img><span class="g-no">{n}</span></div>
  <div class="g-info">
    <h3 class="g-h3">{E(name)}</h3>{('<div class="g-sub">%s</div>'%E(sub)) if sub else ''}
    <div class="g-rule"></div>
    {rows}
    <div class="g-k">Плюсы</div>{ul(pros,'g-pl')}
    <div class="g-k">Минусы</div>{ul(cons,'g-mi')}
  </div>
</article>'''

def note(label,text,dark=True):
    return f'''<aside class="g-note" data-in="1"><div class="g-nl">{E(label)}</div><p>{text}</p></aside>'''

def mini(name,sub,rows):
    body=''.join('<div class="g-k">%s</div>%s'%(E(k),ul(v,'g-pl' if k in('Плюсы','Преимущества') else ('g-mi' if k in ('Минусы','На что смотреть') else 'g-pl')) if isinstance(v,list) else '<div class="g-v">%s</div>'%E(v)) for k,v in rows)
    return f'<article class="g-mini" data-in="1"><h3 class="g-h3 g-h3s">{E(name)}</h3>{("<div class=g-sub>%s</div>"%E(sub)) if sub else ""}<div class="g-rule"></div>{body}</article>'

def sec(no,title,lead,sid):
    return f'''<div class="g-sech" id="{sid}" data-in="1"><span class="g-secno">{no}</span><div><h2 class="g-h2">{title}</h2><p class="g-lead">{E(lead)}</p></div></div>'''

S_=[i for i in d['items'] if i['cat']=='sanuzly']
def phs(i): return S_[i]['full']
SH_=[i for i in d['items'] if i['cat']=='shkafy']
facades=[
 card('01','ЛДСП','ламинированная плита','древесная плита','ламинат (декоративное покрытие)',
  ['Самый доступный вариант','Большой выбор декоров и фактур','Хорошо подходит для шкафов, прихожих и детских'],
  ['Форма только плоская, без фрезеровки','Торцы закрыты кромкой — на стыках её видно','Боится воды на срезах'],SH_[148]['full'],False,'Шкаф с фасадами из ЛДСП'),
 card('02','Плёнка ПВХ','вакуумное прессование','МДФ','ПВХ-плёнка',
  ['Доступная цена среди фасадов из МДФ','Подходят рамочные фасады и фрезеровка','Много цветов и декоров под дерево','Не боится влаги'],
  ['Подходит для кухни не в каждом случае: не любит жар у плиты и духовки','Цвет может выгорать на солнце','Повреждённое место сложно отремонтировать'],15,True,'Кухня с рамочными фасадами из МДФ'),
 card('03','Пластик HPL','слоистый пластик высокого давления','МДФ или ЛДСП','слоистый пластик',
  ['Очень прочное, износостойкое покрытие','Не боится влаги, бытовой химии и ультрафиолета','Много фактур: камень, бетон, дерево, глянец и мат','Часто используют в санузлах'],
  ['Форма фасада проще: в основном плоские','На торцах бывает заметна кромка','Дороже плёнки ПВХ'],phs(8),False,'Тумба в санузле с фасадами из пластика'),
 card('04','Эмаль','краска + лак','МДФ','слои грунта, краски и лака',
  ['Любой цвет — по каталогам RAL и NCS','Можно делать фрезеровку и фигурные фасады','«Монолитный» вид без кромок и стыков','Разные эффекты: глянец, мат, металлик, перламутр'],
  ['Боится сильных ударов — скол придётся красить заново','Дороже плёнки','Дольше делается: каждый слой сушится'],25,True,'Кухня с эмалированными фасадами'),
 card('05','Массив дерева','дуб, ясень, бук и другие породы','цельная древесина','защитный лак, масло или патина',
  ['Долговечный, при необходимости его можно отреставрировать','Рамочные фасады, резьба, классические формы','Премиальный вид'],
  ['Самый дорогой вариант','Тяжёлый, чувствителен к перепадам влаги и попаданию прямых солнечных лучей','Нужен уход и защитное покрытие'],0,False,'Кухня из массива в классическом стиле'),
]
body=[]
body.append(sec('01','Фасады','Фасады видно сразу, они определяют внешний вид мебели и то, как она переживёт ежедневное использование.','facades'))
body+=facades

corp=[
 card('01','ЛДСП','древесная плита с ламинированным покрытием','древесные стружки со смолой','ламинат',
  ['Доступная цена и большой выбор декоров','Подходит для большинства корпусов','Жёсткий и стабильный материал'],
  ['Боится воды на срезах без кромки','Не подлежит перекрашиванию','Тяжёлые нагрузки требуют правильной конструкции'],SH_[40]['full'],True,'Внутреннее наполнение кухонного корпуса'),
 card('02','Кромка','защита торцов плиты','ПВХ или АБС','закрывает срез плиты',
  ['Защищает торцы от влаги и грязи','Выбор цвета под корпус или фасад','Аккуратный, цельный вид'],
  ['Кромка 0,4 мм — самая тонкая, 2 мм — прочнее','У мойки и посудомойки торцы лучше закрыть толстой кромкой'],SH_[93]['full'],False,'Выдвижной ящик с лотком для приборов'),
]
body.append(sec('02','Корпуса','Основа любой мебели — корпус: он держит нагрузку и определяет, сколько прослужит мебель.','korpusa'))
body+=corp

top=[
 mini('ЛДСП','ламинированная плита',[('Основа','ЛДСП с закруглённым торцом, толщина обычно 38–40 мм'),('Плюсы',['Доступная цена','Много декоров','Быстро изготавливается']),('Минусы',['Боится воды на стыках и срезах','Горячее лучше не ставить'])]),
 mini('Компакт-плита HPL','слоистый пластик',[('Основа','слоистый пластик по всей толщине, 10–12 мм'),('Плюсы',['Очень прочная, влагостойкая и ударостойкая','Не боится бытовой химии','Тонкая и современная']),('Минусы',['Цена выше, чем у ЛДСП','Торец виден и всегда чёрный — это сам пластик'])]),
 mini('Искусственный камень','акриловый',[('Основа','акрил и минеральный наполнитель, толщина 12–40 мм'),('Плюсы',['Бесшовные стыки','Мелкие царапины шлифуются','Мойка может быть встроена заподлицо']),('Минусы',['Боится горячих сковород','Дороже ламинированных столешниц'])]),
 mini('Кварцевый камень','кварц + смола',[('Основа','кварцевый песок до 90–95%, толщина 20–40 мм'),('Плюсы',['Очень твёрдый, трудно поцарапать','Не впитывает жидкости','Стойкий цвет']),('Минусы',['Высокая цена и большой вес','Не любит резкий жар'])]),
 mini('Керамогранит','керамическая плита',[('Основа','обожжённая керамика, толщина 12–80 мм'),('Плюсы',['Не боится жара и царапин','Не впитывает жидкости','Рисунок под мрамор и бетон']),('Минусы',['Хрупкая кромка','Нужен точный монтаж и аккуратная резка'])]),
 mini('Натуральный камень','гранит, мрамор',[('Основа','природный камень'),('Плюсы',['Уникальный рисунок','Срок службы — десятилетия','Благородный вид']),('Минусы',['Высокая цена','Мрамор боится кислот, нужна пропитка'])]),
 mini('Массив дерева','дуб, ясень, ореховое дерево',[('Основа','цельная древесина'),('Плюсы',['Тёплый, живой материал','Можно отшлифовать и обновить','Подходит для барной стойки и острова']),('Минусы',['Нужен уход: масло или лак','Боится воды вокруг мойки'])]),
]
body.append(sec('03','Столешницы','Столешница работает больше всего: на неё льют, режут и ставят горячее. Сравните материалы по главному.','stoleshnitsy'))
body.append('<!-- TODO ASD: заменить сведения о столешницах на наши (материалы, толщины, цены) -->')
body.append(f'<div class="g-banner" data-in="1"><img src="{ph(71)}" alt="Кухня со столешницей под мрамор" loading="lazy"></img></div>')
body.append('<div class="g-grid">'+''.join(top)+'</div>')

fit=[
 mini('Петли с доводчиком','фасады шкафов',[('Плюсы',['Плавное, тихое закрывание','Регулировка в трёх направлениях','Снимаются при мытье и сборке']),('На что смотреть',['Заявленный ресурс в циклах открывания','Тип крепления и угол открывания'])]),
 mini('Выдвижные ящики','направляющие скрытого монтажа',[('Плюсы',['Ровный, плавный ход','Полное выдвижение: виден весь ящик','Доводчик в комплекте']),('На что смотреть',['Допустимая нагрузка на ящик','Ширина и глубина под ваши предметы'])]),
 mini('Подъёмные механизмы','верхние шкафы',[('Плюсы',['Фасад поднимается вверх, не мешая работе','Удобно при ограниченном пространстве']),('На что смотреть',['Подбор по весу фасада','Плавность хода и фиксация'])]),
 mini('Системы хранения','лотки, корзины, карусели',[('Плюсы',['Каждому предмету — своё место','Использование угла и узких проёмов','Порядок без лишних поисков']),('На что смотреть',['Размеры под ваш набор посуды','Материал: нержавеющая сталь или пластик'])]),
 mini('Ручки и профиль','способы открывания',[('Плюсы',['Накладные ручки — привычно и недорого','Профиль-ручка — гладкий минималистичный фасад','Push-to-open — без ручек вообще']),('На что смотреть',['Удобство хвата ежедневно','Совместимость с фасадом и толщиной'])]),
]
body.append(sec('04','Фурнитура','Фурнитура — то, чем вы пользуетесь каждый день. Хорошая заметна сразу, плохая — через год.','furnitura'))
body.append(f'<div class="g-banner g-banner2" data-in="1"><img src="{ph(75)}" alt="Выдвижные ящики с лотками" loading="lazy"></img></div>')
body.append('<div class="g-grid">'+''.join(fit)+'</div>')
body.append(note('Совет','Фурнитуру выбирают вместе с проектом, а не в конце: от неё зависят размеры ящиков, высота шкафов и удобство каждый день. Расскажите дизайнеру, как вы готовите и что хранится на кухне.'))

tiers=[('Бюджетные',['ЛДСП','Плёнка ПВХ','ЛДСП (столешница)'],'g-t1'),('Средний сегмент',['Пластик HPL','Эмаль','Искусственный камень','Компакт-плита'],'g-t2'),('Премиум',['Массив','Кварцевый камень','Керамогранит'],'g-t3')]
body.append(sec('05','Сравнение по цене','Ориентир по ценовым группам: точная стоимость зависит от размеров, цвета и сложности проекта.','price'))
body.append('<div class="g-tiers" data-in="1">'+''.join('<div class="g-tier %s"><h3>%s</h3><ul>%s</ul></div>'%(c,E(n),''.join('<li>%s</li>'%E(i) for i in its)) for n,its,c in tiers)+'</div>')
TV_=[i for i in d['items'] if i['cat']=='tv-zony']
rooms=[('Кухня','эмаль или пластик HPL, столешница из кварца или искусственного камня',ph(23)),('Прихожая','фасады из ЛДСП или эмали, полки и столешница — компакт-плита',SH_[109]['full']),('Гостиная и спальня','эмаль с фрезеровкой или плёнка ПВХ',SH_[137]['full']),('Ванная','пластик HPL или эмаль, влагостойкая столешница из искусственного камня',phs(13))]
body.append(sec('06','Подборки по помещениям','Сочетания, которые мы чаще всего предлагаем в проектах.','rooms'))
body.append('<div class="g-rooms" data-in="1">'+''.join('<div class="g-room" data-tilt="1"><img src="%s" alt="%s" loading="lazy"></img><h3>%s</h3><p>%s</p></div>'%(i,E(n),E(n),E(t)) for n,t,i in rooms)+'</div>')

CSS='''
    .g-tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
    .g-tier{border-radius:20px;padding:28px;color:#FBFAF7}.g-tier h3{margin:0 0 16px;font:300 28px/1.1 'Noto Serif Display','Bitstream Charter',serif}
    .g-tier ul{margin:0;padding:0;list-style:none}.g-tier li{padding:9px 0;border-top:1px solid rgba(255,255,255,.25);font:500 15px Manrope,Inter,sans-serif}
    .g-t1{background:#8C6239}.g-t2{background:#3A342D}.g-t3{background:#B98D5E;color:#14120F}.g-t3 li{border-color:rgba(0,0,0,.2)}
    .g-rooms{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
    .g-room{background:#FBFAF7;border:1px solid #DCD5CA;border-radius:20px;overflow:hidden}.g-room img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}
    .g-room h3{margin:16px 18px 6px;font:300 22px/1.1 'Noto Serif Display','Bitstream Charter',serif}.g-room p{margin:0 18px 20px;color:#6B635A;font:400 14px/1.55 Manrope,Inter,sans-serif}
    @media(max-width:900px){.g-tiers{grid-template-columns:1fr}.g-rooms{grid-template-columns:repeat(2,1fr)}}

    html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
    body { margin: 0; background: #F4F1EC; color: #1A1714; font-family: Manrope, Inter, system-ui, sans-serif; -webkit-font-smoothing: antialiased; overflow-x: clip; }
    a { color: inherit; } ::selection { background: #C9A074; color: #14120F; }
    :focus-visible { outline: 2px solid #B98D5E; outline-offset: 3px; }
    .g-wrap { max-width: 1280px; margin: 0 auto; padding: 0 clamp(20px,4vw,56px); }
    .g-hero { padding: calc(84px + clamp(40px,6vw,88px)) 0 clamp(40px,5vw,72px); }
    .g-hero-in { display: grid; grid-template-columns: minmax(0,1.1fr) minmax(0,.9fr); gap: clamp(28px,5vw,72px); align-items: center; }
    .g-eye { display:flex;align-items:center;gap:14px;font:600 11.5px/1 Manrope, Inter, sans-serif;letter-spacing:.24em;text-transform:uppercase;color:#8C6239;margin-bottom:24px }
    .g-eye i { width:36px;height:1px;background:currentColor }
    .g-h1 { margin:0;font:300 clamp(2.6rem,5.6vw,5.4rem)/1 'Noto Serif Display','Bitstream Charter',Georgia,serif;letter-spacing:-.035em;text-wrap:balance }
    .g-h1 em { font-style: italic; color: #8C6239; }
    .g-sub0 { margin:24px 0 0;max-width:48ch;color:#6B635A;font:400 17px/1.7 Manrope, Inter, sans-serif;text-wrap:pretty }
    .g-btns { display:flex;flex-wrap:wrap;gap:12px;margin-top:32px }
    .g-btn { display:inline-flex;align-items:center;height:52px;padding:0 26px;border-radius:999px;text-decoration:none;font:600 15px Manrope, Inter, sans-serif;border:1px solid rgba(26,23,20,.28);background:transparent;color:#1A1714;cursor:pointer;transition:background-color .3s,color .3s,border-color .3s }
    .g-btn:hover { background:#1A1714;color:#FBFAF7;border-color:#1A1714 }
    .g-btn--d { background:#1A1714;color:#FBFAF7;border-color:#1A1714 } .g-btn--d:hover { background:#8C6239;border-color:#8C6239 }
    .g-herophoto { aspect-ratio: 4/5; border-radius: 200px 200px 24px 24px; overflow: hidden; background:#E8E1D6 }
    .g-herophoto img { width:100%;height:100%;object-fit:cover;display:block }
    .g-3dbox { position:relative; background:#E6DFD3 }
    .g-3d { position:absolute; inset:0 0 70px 0; opacity:0; transition:opacity 1s ease }
    .g-3dbox.is-3d .g-3d { opacity:1 } .g-3dbox.is-3d .g-3dfb { opacity:0 } .g-3dfb { transition:opacity .8s ease }
    .g-3dcap { position:absolute; left:24px; right:24px; bottom:22px; display:none; flex-direction:column; gap:4px; text-align:center }
    .g-3dbox.is-3d .g-3dcap { display:flex }
    .g-3dcap b { font:300 clamp(1.5rem,2.2vw,2rem)/1.1 'Noto Serif Display','Bitstream Charter',serif; letter-spacing:-.02em; color:#1A1714 }
    .g-3dcap span { font:500 14px/1.4 Manrope, Inter, sans-serif; color:#6B635A }
    .g-3dhint { position:absolute; top:22%; right:18px; display:none; font:500 12px Manrope, Inter, sans-serif; color:#8A8177; writing-mode:vertical-rl; letter-spacing:.06em }
    .g-3dbox.is-3d .g-3dhint { display:block }
    [data-tilt] { transform-style:preserve-3d; transition:transform .5s cubic-bezier(.2,.8,.2,1), box-shadow .5s ease; will-change:transform }
    [data-tilt].is-tilt { box-shadow:0 30px 60px -36px rgba(26,23,20,.45) }
    .g-tier { transition:transform .5s cubic-bezier(.2,.8,.2,1) }
    .g-toc { display:flex;flex-wrap:wrap;gap:10px;margin-top:40px }
    .g-toc a { display:inline-flex;gap:10px;align-items:center;padding:12px 20px;border-radius:999px;border:1px solid #DCD5CA;background:#FBFAF7;text-decoration:none;font:600 14px Manrope, Inter, sans-serif;transition:all .3s }
    .g-toc a:hover { background:#1A1714;color:#FBFAF7;border-color:#1A1714 } .g-toc b { color:#B98D5E;font:italic 300 16px 'Noto Serif Display','Bitstream Charter',serif }
    .g-sech { display:flex;gap:clamp(18px,3vw,40px);align-items:flex-start;margin:clamp(64px,8vw,112px) 0 clamp(28px,3.4vw,44px);scroll-margin-top:100px;padding-top:28px;border-top:1px solid #1A1714;position:relative }
    .g-sech::before { content:"";position:absolute;left:0;top:-4px;width:7px;height:7px;background:#B98D5E;transform:rotate(45deg) }
    .g-secno { font:300 clamp(3rem,6vw,5.5rem)/.9 'Noto Serif Display','Bitstream Charter',serif;color:#C9A074;letter-spacing:-.03em }
    .g-h2 { margin:0;font:300 clamp(2.2rem,4vw,3.6rem)/1.05 'Noto Serif Display','Bitstream Charter',serif;letter-spacing:-.03em }
    .g-lead { margin:12px 0 0;max-width:56ch;color:#6B635A;font:400 16.5px/1.65 Manrope, Inter, sans-serif }
    .g-card { display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);background:#FBFAF7;border:1px solid #E2DCD3;border-radius:28px;overflow:hidden;margin-bottom:clamp(16px,2vw,28px);box-shadow:0 30px 60px -44px rgba(26,23,20,.3) }
    .g-flip .g-ph { order:2 }
    .g-ph { position:relative;min-height:440px;background:#E8E1D6 } .g-ph img { position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block }
    .g-no { position:absolute;left:20px;top:18px;padding:7px 12px;border-radius:999px;background:rgba(251,250,247,.88);font:600 11.5px/1 Manrope, Inter, sans-serif;letter-spacing:.2em;color:#8C6239 }
    .g-info { padding:clamp(24px,3.2vw,44px) }
    .g-h3 { margin:0;font:300 clamp(1.9rem,2.6vw,2.5rem)/1.05 'Noto Serif Display','Bitstream Charter',serif;letter-spacing:-.02em }
    .g-h3s { font-size:1.65rem }
    .g-sub { margin-top:8px;color:#8C6239;font:600 12px/1.4 Manrope, Inter, sans-serif;letter-spacing:.12em;text-transform:uppercase }
    .g-rule { height:1px;background:#B98D5E;margin:18px 0 6px;width:100% }
    .g-k { margin:16px 0 6px;font:700 11px/1 Manrope, Inter, sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#1A1714 }
    .g-v { color:#6B635A;font:400 15.5px/1.55 Manrope, Inter, sans-serif }
    .g-ul { list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px }
    .g-ul li { position:relative;padding-left:20px;font:400 15px/1.5 Manrope, Inter, sans-serif;color:#3A342E }
    .g-pl li::before { content:"";position:absolute;left:2px;top:.62em;width:6px;height:6px;background:#B98D5E;transform:rotate(45deg) }
    .g-mi li { color:#6B635A } .g-mi li::before { content:"";position:absolute;left:1px;top:.78em;width:9px;height:1.5px;background:#A33A28 }
    .g-note { margin:0 0 clamp(16px,2vw,28px);padding:clamp(22px,3vw,36px) clamp(24px,3.4vw,48px);border-radius:24px;background:#1D1A16;color:#FBFAF7;border-left:4px solid #B98D5E }
    .g-nl { font:700 11px/1 Manrope, Inter, sans-serif;letter-spacing:.24em;text-transform:uppercase;color:#C9A074;margin-bottom:12px }
    .g-note p { margin:0;max-width:78ch;font:300 clamp(1.05rem,1.4vw,1.25rem)/1.6 'Noto Serif Display','Bitstream Charter',serif;color:#EDE6DB }
    .g-banner { height:clamp(220px,30vw,400px);border-radius:28px;overflow:hidden;margin-bottom:clamp(16px,2vw,28px);background:#E8E1D6 } .g-banner img { width:100%;height:100%;object-fit:cover;display:block }
    .g-grid { display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:clamp(14px,1.6vw,22px);margin-bottom:clamp(16px,2vw,28px) }
    .g-mini { background:#FBFAF7;border:1px solid #E2DCD3;border-radius:22px;padding:clamp(20px,2.4vw,30px) }
    .g-cta { margin:clamp(72px,9vw,128px) 0 clamp(64px,8vw,112px);padding:clamp(32px,5vw,72px);border-radius:32px;background:#1D1A16;color:#FBFAF7;display:flex;flex-wrap:wrap;gap:24px;justify-content:space-between;align-items:center }
    .g-cta h2 { margin:0;max-width:18ch;font:300 clamp(2rem,4vw,3.4rem)/1.05 'Noto Serif Display','Bitstream Charter',serif;letter-spacing:-.03em } .g-cta h2 em { color:#E2C7A2;font-style:italic }
    .g-cta p { margin:14px 0 0;max-width:46ch;color:#A79E93;font:400 16px/1.65 Manrope, Inter, sans-serif }
    .g-cta .g-btn { border-color:rgba(251,250,247,.4);color:#FBFAF7 } .g-cta .g-btn--d { background:#B98D5E;border-color:#B98D5E;color:#14120F } .g-cta .g-btn:hover { background:#FBFAF7;color:#14120F;border-color:#FBFAF7 }
    @media (max-width: 860px) {
      .g-hero-in { grid-template-columns: 1fr } .g-herophoto { max-width: 420px; border-radius: 160px 160px 20px 20px }
      .g-card { grid-template-columns: 1fr } .g-flip .g-ph { order: 0 } .g-ph { min-height: 280px }
      .g-sech { flex-direction: column; gap: 6px }
    }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
    @page { size: A4; margin: 10mm }
    @media print {
      * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      [data-dc="SiteHeader"], [data-dc="SiteFooter"], .g-btns, .g-toc, .g-cta .g-btn, .g-3d, .g-3dcap, .g-3dhint { display: none !important; } .g-3dfb { opacity: 1 !important; }
      body { background: #F4F1EC; } .g-hero { padding-top: 24px; } .g-sech { margin-top: 36px; page-break-after: avoid; }
      .g-card, .g-mini, .g-note, .g-banner { page-break-inside: avoid; break-inside: avoid; }
      .g-hero-in { grid-template-columns: minmax(0,1.1fr) minmax(0,.9fr); gap: 28px; } .g-herophoto { aspect-ratio: 4/4.6; max-width: none; border-radius: 160px 160px 20px 20px; }
      .g-card { grid-template-columns: minmax(0,1.05fr) minmax(0,1fr); } .g-flip .g-ph { order: 2; } .g-ph { min-height: 250px; }
      .g-sech { flex-direction: row; gap: 20px; break-after: avoid; break-inside: avoid; } .g-banner { height: 200px; }
      .g-h1 { font-size: 2.6rem; } .g-info { padding: 22px; } .g-k { margin-top: 12px; } .g-cta { margin-top: 40px; }
    }
'''
page=f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <title>Гид по материалам — ASD</title>
  <meta name="description" content="Как выбрать мебель: фасады, корпуса, столешницы и фурнитура — из чего сделано, плюсы и минусы, на что обратить внимание."></meta>
  <meta name="theme-color" content="#F4F1EC"></meta>
  <link rel="icon" href="img/favicon.svg" type="image/svg+xml"></link>
  <link rel="preconnect" href="https://fonts.googleapis.com"></link>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""></link>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&family=Noto+Serif+Display:ital,wght@0,300;0,400;1,300;1,400&display=swap" rel="stylesheet"></link>
  <style>{CSS}</style>
</helmet>

<dc-import name="SiteHeader" active="guide" tone="light" hint-size="100%,0px"></dc-import>

<main>
  <section class="g-hero">
    <div class="g-wrap">
      <div class="g-hero-in">
        <div data-in="1">
          <div class="g-eye"><i></i>Гид по материалам</div>
          <h1 class="g-h1">Как выбрать <em>мебель</em>, которая прослужит долго</h1>
          <p class="g-sub0">Из чего сделаны фасады, корпуса и столешницы, какие у них плюсы и минусы и на что смотреть перед заказом.</p>
          <div class="g-btns">
            <a class="g-btn g-btn--d" href="guide-asd.pdf" download="ASD-gid-po-materialam.pdf">Скачать PDF</a>
            <a class="g-btn" href="Quiz.dc.html">Подобрать с дизайнером</a>
          </div>
          <nav class="g-toc" aria-label="Разделы гида">
            <a href="#facades"><b>01</b>Фасады</a><a href="#korpusa"><b>02</b>Корпуса</a><a href="#stoleshnitsy"><b>03</b>Столешницы</a><a href="#furnitura"><b>04</b>Фурнитура</a><a href="#price"><b>05</b>По цене</a><a href="#rooms"><b>06</b>По помещениям</a>
          </nav>
        </div>
        <div class="g-herophoto g-3dbox" data-in="1">
          <img class="g-3dfb" src="{ph(23)}" alt="Кухня ASD" loading="eager"></img>
          <div id="g3d" class="g-3d" aria-hidden="false"></div>
          <div class="g-3dcap" aria-live="polite"><b id="g3d-name">Образцы фасадов</b><span id="g3d-note">наведите или нажмите на образец</span></div>
          <div class="g-3dhint">Потяните, чтобы повернуть</div>
        </div>
      </div>
    </div>
  </section>

  <div class="g-wrap">
{chr(10).join(body)}

    <section class="g-cta" data-in="1">
      <div>
        <h2>Не знаете, что <em>выбрать?</em></h2>
        <p>Дизайнер ASD подберёт материалы под вашу кухню, бюджет и образ жизни и спроектирует идеальный вариант мебели для вашего дома.</p>
      </div>
      <div class="g-btns" style="margin:0">
        <a class="g-btn g-btn--d" href="Quiz.dc.html">Заполнить опрос</a>
        <a class="g-btn" href="Works.dc.html">Смотреть работы</a>
      </div>
    </section>
  </div>
</main>

<dc-import name="SiteFooter" hint-size="100%,560px"></dc-import>
</x-dc>
<script type="text/x-dc" data-dc-script>
class Component extends DCLogic {{
  reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  componentDidMount() {{
    this.mount3d();
    this.tilt();
    if (this.reduce || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver((es) => es.forEach((e) => {{
      if (!e.isIntersecting) return; io.unobserve(e.target);
      e.target.animate([{{ opacity: 0, transform: 'perspective(1400px) rotateX(12deg) translateY(48px)' }}, {{ opacity: 1, transform: 'none' }}], {{ duration: 1100, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'backwards' }});
    }}), {{ threshold: 0.08 }});
    document.querySelectorAll('[data-in]').forEach((el) => io.observe(el));
  }}
  load(src) {{ return new Promise((res) => {{ const s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = res; document.head.appendChild(s); }}); }}
  mount3d() {{
    const host = document.getElementById('g3d'); if (!host) return;
    this.load('js/gl3d.js').then(() => this.load('js/samples3d.js')).then(() => {{
      if (!window.ASDSamples) return;
      const nm = document.getElementById('g3d-name'), nt = document.getElementById('g3d-note');
      const api = window.ASDSamples.mount(host, {{
        onPick: (m) => {{ if (!m) return; nm.textContent = m.name; nt.textContent = m.note + ' · подробнее ниже'; }},
        onOpen: (m) => {{ const el = document.getElementById('m-' + m.id); if (el) el.scrollIntoView({{ behavior: this.reduce ? 'auto' : 'smooth', block: 'center' }}); }}
      }});
      if (api) host.parentNode.classList.add('is-3d');
    }});
  }}
  tilt() {{
    if (this.reduce || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    document.querySelectorAll('[data-tilt]').forEach((el) => {{
      el.addEventListener('pointermove', (e) => {{
        const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        const k = r.width > 700 ? 3 : 7;
        el.style.transform = 'perspective(1200px) rotateY(' + (x * k) + 'deg) rotateX(' + (-y * k) + 'deg) translateZ(0)'; el.classList.add('is-tilt');
      }});
      el.addEventListener('pointerleave', () => {{ el.style.transform = ''; el.classList.remove('is-tilt'); }});
    }});
  }}
  renderVals() {{ return {{ print: () => window.print() }}; }}
}}
</script>
</body>
</html>
'''
open(os.path.join(ROOT,'design','Guide.dc.html'),'w').write(page)
print(len(page))
