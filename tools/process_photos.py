#!/usr/bin/env python3
"""
Готовит фото работ для сайта.

Как пользоваться:
  1. Скачайте фото из облака в папки (подпапки внутри раздела станут подразделами):
       photos/kuhni/        Кухни
       photos/shkafy/       Шкафы
       photos/sanuzly/      Санузлы
       photos/tv-zony/      ТВ-зоны
       photos/ofis/         Офисная мебель
     Пример подраздела: photos/kuhni/угловые/IMG_001.jpg
  2. Запустите:  python tools/process_photos.py     (нужен Pillow: pip install pillow)
  3. Скрипт сожмёт фото (папка img/works/) и обновит js/works-data.js.
"""
import hashlib, json, os, re, sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'photos'
OUT = ROOT / 'img' / 'works'

CATEGORIES = [
    ('kuhni',   'Кухни',          'Кухни по размерам вашей квартиры',               ['кухни', 'кухня', 'kitchen']),
    ('shkafy',  'Шкафы',          'Шкафы-купе, гардеробные, встроенные системы',     ['шкафы', 'шкаф', 'wardrobe']),
    ('sanuzly', 'Санузлы',        'Мебель и отделка для ванных комнат',              ['сан узлы', 'санузлы', 'санузел', 'сан узел', 'bath']),
    ('tv-zony', 'ТВ-зоны',        'Стенки, тумбы и панели под телевизор',            ['тв-зоны', 'тв зоны', 'тв', 'tv', 'tv-zony']),
    ('ofis',    'Офисная мебель', 'Столы, шкафы и ресепшн для офисов',               ['офисная мебель', 'офис', 'office']),
]
EXT = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
FULL, THUMB = 1800, 640


def norm(s):
    return re.sub(r'\s+', ' ', s.strip().lower())


def category_for(folder):
    n = norm(folder)
    for cid, _, _, aliases in CATEGORIES:
        if n == cid or n in aliases:
            return cid
    return None


def natural(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', str(p))]


def save(img, path, longest, q):
    im = img.copy()
    im.thumbnail((longest, longest), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, 'WEBP', quality=q, method=6)
    return im.size


def main():
    if not SRC.exists():
        sys.exit(f'Нет папки {SRC}. Создайте её и положите фото по разделам.')
    items, seen = [], set()
    for cid, *_ in CATEGORIES:
        (OUT / cid).mkdir(parents=True, exist_ok=True)
    for folder in sorted([d for d in SRC.iterdir() if d.is_dir()], key=lambda d: d.name):
        cid = category_for(folder.name)
        if not cid:
            print(f'  пропускаю папку «{folder.name}»: не знаю такого раздела'); continue
        files = sorted([f for f in folder.rglob('*') if f.suffix.lower() in EXT], key=natural)
        n = 0
        for f in files:
            rel = f.relative_to(folder)
            sub = rel.parts[0] if len(rel.parts) > 1 else ''
            digest = hashlib.sha1(f.read_bytes()).hexdigest()
            if digest in seen:
                continue                       # одинаковые файлы не дублируем
            seen.add(digest)
            try:
                img = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
            except Exception as e:
                print(f'  не открылось {f.name}: {e}'); continue
            if min(img.size) < 200:
                continue
            n += 1
            name = f'{cid}-{n:03d}-{digest[:6]}.webp'
            fw, fh = save(img, OUT / cid / name, FULL, 82)
            tw, th = save(img, OUT / cid / ('t-' + name), THUMB, 78)
            items.append({'cat': cid, 'sub': sub, 'full': f'img/works/{cid}/{name}', 'thumb': f'img/works/{cid}/t-{name}',
                          'w': fw, 'h': fh, 'tw': tw, 'th': th})
        print(f'  {folder.name}: {n} фото')
    # убираем из img/works файлы, которых больше нет в списке
    keep = {ROOT / i['full'] for i in items} | {ROOT / i['thumb'] for i in items}
    for f in OUT.rglob('*.webp'):
        if f not in keep:
            f.unlink()

    data = {'categories': [{'id': c, 'title': t, 'text': x} for c, t, x, _ in CATEGORIES], 'items': items}
    js = ('/* Этот файл создаёт скрипт tools/process_photos.py. Вручную менять не нужно:\n'
          '   разложите фото по папкам photos/<раздел>/ и запустите скрипт заново. */\n'
          'window.WORKS = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
    (ROOT / 'js' / 'works-data.js').write_text(js, encoding='utf-8')
    size = sum(f.stat().st_size for f in OUT.rglob('*.webp')) / 1e6
    print(f'Готово: {len(items)} фото, {size:.1f} МБ в img/works/')


if __name__ == '__main__':
    main()
