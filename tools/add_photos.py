#!/usr/bin/env python3
"""
Добавляет НОВЫЕ фото к уже опубликованным, ничего не пересобирая и не удаляя.

  python tools/add_photos.py newfoto

В папке newfoto те же подпапки, что и в photos: kuhni, shkafy, sanuzly, tv-zony, ofis
(подпапки внутри раздела становятся подразделами). Фото сжимаются так же, как в process_photos.py
(полная версия до 1800 px и миниатюра до 640 px, WebP), одинаковые фото пропускаются —
в том числе те, что уже есть на сайте. Файл js/works-data.js дополняется.
"""
import hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from process_photos import ROOT, OUT, EXT, FULL, THUMB, category_for, natural, save   # noqa: E402
from PIL import Image, ImageOps

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'newfoto'
DATA = ROOT / 'js' / 'works-data.js'


def main():
    if not SRC.exists():
        sys.exit(f'Нет папки {SRC}')
    text = DATA.read_text(encoding='utf-8')
    data = json.loads(text[text.index('window.WORKS = ') + len('window.WORKS = '):].rstrip().rstrip(';'))
    items = data['items']
    seen = {m.group(1) for i in items for m in [re.search(r'-\d{3}-([0-9a-f]{6})\.webp$', i['full'])] if m}
    nums = {}
    for i in items:
        m = re.search(r'-(\d{3})-[0-9a-f]{6}\.webp$', i['full'])
        if m: nums[i['cat']] = max(nums.get(i['cat'], 0), int(m.group(1)))
    added = {}
    for folder in sorted([d for d in SRC.iterdir() if d.is_dir()], key=lambda d: d.name):
        cid = category_for(folder.name)
        if not cid:
            print(f'  пропускаю папку «{folder.name}»: не знаю такого раздела'); continue
        files = sorted([f for f in folder.rglob('*') if f.suffix.lower() in EXT], key=natural)
        for f in files:
            rel = f.relative_to(folder)
            sub = rel.parts[0] if len(rel.parts) > 1 else ''
            digest = hashlib.sha1(f.read_bytes()).hexdigest()
            if digest[:6] in seen:
                print(f'  уже есть / дубль: {cid}/{f.name}'); continue
            try:
                img = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
            except Exception as e:
                print(f'  не открылось {f.name}: {e}'); continue
            if min(img.size) < 200: continue
            seen.add(digest[:6]); nums[cid] = nums.get(cid, 0) + 1
            name = f'{cid}-{nums[cid]:03d}-{digest[:6]}.webp'
            fw, fh = save(img, OUT / cid / name, FULL, 82)
            tw, th = save(img, OUT / cid / ('t-' + name), THUMB, 78)
            new = {'cat': cid, 'sub': sub, 'full': f'img/works/{cid}/{name}', 'thumb': f'img/works/{cid}/t-{name}', 'w': fw, 'h': fh, 'tw': tw, 'th': th}
            last = max((k for k, i in enumerate(items) if i['cat'] == cid), default=len(items) - 1)
            items.insert(last + 1, new)             # в конец своего раздела
            added[cid] = added.get(cid, 0) + 1
    js = ('/* Этот файл создают скрипты tools/process_photos.py и tools/add_photos.py. Вручную менять не нужно. */\n'
          'window.WORKS = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n')
    DATA.write_text(js, encoding='utf-8')
    print('Добавлено:', added or 'ничего', '| всего', len(items))


if __name__ == '__main__':
    main()
