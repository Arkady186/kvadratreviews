#!/usr/bin/env python3
"""Сборка страниц из шаблонов Claude Design (*.dc.html) в обычные статические страницы.

Берёт шаблон разметки ({{ путь }}, sc-if, sc-for, style-hover, onClick…) и скрипт компонента,
компилирует шаблон в обычную JS-функцию и кладёт рядом лёгкий рантайм js/dc.js
(без React и Babel с CDN). Запуск:  python3 tools/build_dc.py <папка_с_dc_html> <папка_сайта>
"""
import re, sys, json, os

SRC, OUT = sys.argv[1], sys.argv[2]
VOID = {'img', 'input', 'br', 'hr', 'meta', 'link', 'source', 'wbr'}
PAGES = {'Home': 'index.html', 'Works': 'works.html', 'Reviews': 'reviews.html', 'Quiz': 'quiz.html', 'Guide': 'guide.html'}
LINKS = {'Home.dc.html': 'index.html', 'Works.dc.html': 'works.html', 'Reviews.dc.html': 'reviews.html', 'Quiz.dc.html': 'quiz.html', 'Guide.dc.html': 'guide.html'}
uid = [0]
css_rules = []


def relink(s):
    for a, b in LINKS.items():
        s = s.replace(a, b)
    return s


TAG = re.compile(r'<!--.*?-->|<(/?)([a-zA-Z][\w:-]*)((?:\s+[^\s=>/"\']+(?:\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>"\']+))?)*)\s*(/?)>', re.S)
ATTR = re.compile(r'([^\s=>/"\']+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>"\']+)))?')


def parse(tpl):
    root = {'tag': '#root', 'attrs': [], 'kids': []}
    stack = [root]
    pos = 0
    for m in TAG.finditer(tpl):
        if m.start() > pos:
            stack[-1]['kids'].append({'text': tpl[pos:m.start()]})
        pos = m.end()
        if m.group(0).startswith('<!--'):
            continue
        close, name, attrs, selfc = m.group(1), m.group(2), m.group(3), m.group(4)
        if close:
            if name in VOID:
                continue
            # закрыть до ближайшего открытого такого же тега
            for i in range(len(stack) - 1, 0, -1):
                if stack[i]['tag'] == name:
                    del stack[i:]
                    break
            continue
        at = []
        for am in ATTR.finditer(attrs or ''):
            val = am.group(2) if am.group(2) is not None else am.group(3) if am.group(3) is not None else am.group(4)
            at.append((am.group(1), val))
        node = {'tag': name, 'attrs': at, 'kids': []}
        stack[-1]['kids'].append(node)
        if name in VOID or selfc:
            continue
        stack.append(node)
    if pos < len(tpl):
        stack[-1]['kids'].append({'text': tpl[pos:]})
    return root


EXPR = re.compile(r'\{\{\s*([\w.]+)\s*\}\}')
PURE = re.compile(r'^\s*\{\{\s*([\w.]+)\s*\}\}\s*$')


def path(p, scope):
    parts = p.split('.')
    head = parts[0]
    base = head if head in scope else 'v.' + head
    return base + ''.join('?.' + x for x in parts[1:])


def jstr(s):
    return json.dumps(s, ensure_ascii=False)


def text_code(t, scope):
    # поведение как у JSX: переносы строк с отступами схлопываются
    if not t.strip() and '\n' in t:
        return ''
    t2 = re.sub(r'\s*\n\s*', ' ', t)
    if t.startswith(('\n', '\r')) or re.match(r'\s*\n', t):
        t2 = t2.lstrip()
    if re.search(r'\n\s*$', t):
        t2 = t2.rstrip()
    out, pos = [], 0
    for m in EXPR.finditer(t2):
        if m.start() > pos:
            out.append('__o+=' + jstr(t2[pos:m.start()]) + ';')
        out.append('__o+=__E(' + path(m.group(1), scope) + ');')
        pos = m.end()
    if pos < len(t2):
        out.append('__o+=' + jstr(t2[pos:]) + ';')
    return ''.join(out)


def decl_important(s):
    ds = [d.strip() for d in s.split(';') if d.strip()]
    return ';'.join(d + ' !important' for d in ds)


def gen(node, scope, comp):
    if 'text' in node:
        return text_code(node['text'], scope)
    tag = node['tag']
    kids = node['kids']
    if tag == '#root':
        return ''.join(gen(k, scope, comp) for k in kids)
    if tag == 'sc-if':
        v = dict(node['attrs']).get('value', '')
        m = PURE.match(v)
        cond = path(m.group(1), scope)
        return '__o+="<!--?-->";if(' + cond + '){' + ''.join(gen(k, scope, comp) for k in kids) + '}__o+="<!--/-->";'
    if tag == 'sc-for':
        a = dict(node['attrs'])
        lst = path(PURE.match(a['list']).group(1), scope)
        var = a['as']
        return '__o+="<!--?-->";for(const ' + var + ' of (' + lst + '||[])){' + ''.join(gen(k, scope | {var}, comp) for k in kids) + '}__o+="<!--/-->";'
    if tag == 'dc-import':
        a = dict(node['attrs'])
        props = {k: v for k, v in a.items() if k not in ('name',) and not k.startswith('hint-')}
        ph = '<div data-dc="%s"%s style="display:contents"></div>' % (
            a['name'], ''.join(' data-p-%s="%s"' % (k, v) for k, v in props.items()))
        return '__o+=' + jstr(ph) + ';'
    # обычный элемент
    code = ['__o+=' + jstr('<' + tag) + ';']
    hover = focus = None
    classes = None
    for name, val in node['attrs']:
        if name.startswith('hint-') or name in ('data-screen-label',):
            continue
        if name == 'style-hover':
            hover = val
            continue
        if name == 'style-focus':
            focus = val
            continue
        if val is None:
            code.append('__o+=' + jstr(' ' + name) + ';')
            continue
        if name == 'class':
            classes = val
            continue
        if re.match(r'^on[A-Z]', name):
            ev = name[2:].lower()
            code.append('__o+=" data-on-%s=\\""+__H(%s)+"\\"";' % (ev, path(PURE.match(val).group(1), scope)))
            continue
        if name == 'ref':
            code.append('__o+=" data-ref=\\""+__H(%s)+"\\"";' % path(PURE.match(val).group(1), scope))
            continue
        m = PURE.match(val)
        if m:
            bool_str = name.startswith(('aria-', 'data-'))
            code.append(
                '{const __v=%s;if(__v!==undefined&&__v!==null&&__v!==false){__o+=%s+(__v===true?%s:__E(__v))+"\\"";}%s}' % (
                    path(m.group(1), scope), jstr(' ' + name + '="'), '"true"' if bool_str else '""',
                    ('else if(__v===false){__o+=%s;}' % jstr(' ' + name + '="false"')) if bool_str else ''))
        elif '{{' in val:
            parts, pos = [], 0
            for mm in EXPR.finditer(val):
                if mm.start() > pos:
                    parts.append(jstr(val[pos:mm.start()]))
                parts.append('__E(' + path(mm.group(1), scope) + ')')
                pos = mm.end()
            if pos < len(val):
                parts.append(jstr(val[pos:]))
            code.append('__o+=%s+%s+"\\"";' % (jstr(' ' + name + '="'), '+'.join(parts)))
        else:
            code.append('__o+=' + jstr(' ' + name + '="' + val.replace('"', '&quot;') + '"') + ';')
    if hover or focus:
        uid[0] += 1
        cls = 'dc%d' % uid[0]
        if hover:
            css_rules.append('.%s:hover{%s}' % (cls, decl_important(hover)))
        if focus:
            css_rules.append('.%s:focus{%s}' % (cls, decl_important(focus)))
        classes = (classes + ' ' if classes else '') + cls
    if classes:
        code.append('__o+=' + jstr(' class="' + classes + '"') + ';')
    if tag in VOID:
        code.append('__o+=">";')
        return ''.join(code)
    code.append('__o+=">";')
    code.extend(gen(k, scope, comp) for k in kids)
    code.append('__o+=' + jstr('</' + tag + '>') + ';')
    return ''.join(code)


def compile_file(fname, comp_name):
    src = open(os.path.join(SRC, fname), encoding='utf-8').read()
    src = relink(src)
    body = re.search(r'<x-dc>(.*?)</x-dc>', src, re.S).group(1)
    script = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', src, re.S).group(1)
    helm = ''
    m = re.search(r'<helmet>(.*?)</helmet>', body, re.S)
    if m:
        helm = m.group(1)
        body = body.replace(m.group(0), '')
    body = body.replace('color:#E2C7A2;white-space:nowrap">ASD · Кухня на заказ', 'color:#E2C7A2">ASD · Кухня на заказ')
    script = script.replace('const set = this.PREVIEW_FILES;', 'const set = null;')  # в превью были только часть фото
    tree = parse(body)
    fn = '(function(v,__H,__E){let __o="";' + gen(tree, set(), comp_name) + 'return __o;})'
    return fn, script, helm


def fix_helmet(h):
    h = re.sub(r'</(meta|link)>', '', h)
    return h.strip()


def define(name, fn, script):
    return 'DC.define(%s,(function(){%s\nreturn Component;})(),%s);\n' % (jstr(name), script, fn)


# --- шапка и подвал (общие)
site_js = ''
for n in ('SiteHeader', 'SiteFooter'):
    fn, script, _ = compile_file(n + '.dc.html', n)
    site_js += define(n, fn, script)

pages = {}
for n, out in PAGES.items():
    fn, script, helm = compile_file(n + '.dc.html', n)
    helm = fix_helmet(helm)
    pages[out] = (define(n, fn, script), helm)

os.makedirs(os.path.join(OUT, 'js'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'css'), exist_ok=True)
open(os.path.join(OUT, 'js', 'dc-site.js'), 'w', encoding='utf-8').write(site_js)
open(os.path.join(OUT, 'css', 'dc.css'), 'w', encoding='utf-8').write('\n'.join(css_rules) + '\n')

for out, (js, helm) in pages.items():
    name = [k for k, v in PAGES.items() if v == out][0]
    html = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n' \
        + helm + '\n<link rel="stylesheet" href="css/dc.css">\n</head>\n<body>\n' \
        + '<div data-dc="%s" style="display:contents"></div>\n' % name \
        + '<noscript><p style="padding:40px;font:16px sans-serif">Для работы сайта нужен включённый JavaScript.</p></noscript>\n' \
        + '<script src="js/dc.js"></script>\n<script src="js/dc-site.js"></script>\n<script>\n' + js + '\nDC.start();\n</script>\n</body>\n</html>\n'
    open(os.path.join(OUT, out), 'w', encoding='utf-8').write(html)
    print('ok', out, len(html))
print('css rules', len(css_rules))
