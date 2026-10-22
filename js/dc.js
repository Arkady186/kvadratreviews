/* Лёгкий рантайм для страниц, собранных tools/build_dc.py.
   Компонент = класс с state / renderVals() и скомпилированный шаблон.
   Перерисовка — «умное» обновление DOM на месте (фокус в полях, анимации и ссылки на узлы сохраняются). */
(function () {
  'use strict';
  if (!window.React) window.React = { createRef: function () { return { current: null }; } };

  var registry = {};
  var ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' };
  function E(v) { return v === undefined || v === null ? '' : String(v).replace(/[&<>"]/g, function (c) { return ESC[c]; }); }

  function DCLogic() {}
  DCLogic.prototype.setState = function (patch, cb) {
    var cur = this.state || {};
    var p = typeof patch === 'function' ? patch(cur, this.props) : patch;
    this.state = Object.assign({}, cur, p);
    if (cb) (this._cbs = this._cbs || []).push(cb);
    this._schedule();
  };
  DCLogic.prototype._schedule = function () {
    var self = this;
    if (self._pending || !self._host) return;
    self._pending = true;
    Promise.resolve().then(function () { self._pending = false; self._render(); });
  };
  DCLogic.prototype._render = function () {
    var handlers = (this._handlers = []);
    var H = function (x) { handlers.push(x); return handlers.length - 1; };
    var vals = this.renderVals();
    var html = this._tpl(vals, H, E);
    var t = document.createElement('template');
    t.innerHTML = html;
    morphChildren(this._host, t.content, this);
    mountNested(this._host);
    var cbs = this._cbs; this._cbs = null;
    if (cbs) cbs.forEach(function (f) { try { f(); } catch (e) { console.error(e); } });
  };

  function mountNested(host) {
    host.querySelectorAll('[data-dc]').forEach(function (el) {
      if (el.__dc) return;
      var props = {};
      for (var i = 0; i < el.attributes.length; i++) {
        var a = el.attributes[i];
        if (a.name.indexOf('data-p-') === 0) props[a.name.slice(7)] = a.value;
      }
      mount(el, el.getAttribute('data-dc'), props);
    });
  }

  function mount(el, name, props) {
    var def = registry[name];
    if (!def) { console.error('DC: нет компонента', name); return; }
    var inst = new def.cls();
    inst.props = props || {};
    inst.state = inst.state || {};
    inst._host = el; inst._tpl = def.tpl;
    el.__dc = inst;
    inst._render();
    if (inst.componentDidMount) inst.componentDidMount();
  }

  /* ---------- обновление DOM ---------- */
  function isHost(n) { return n.nodeType === 1 && n.hasAttribute('data-dc'); }

  function syncAttrs(o, n, inst) {
    var prev = o.__a || (o.__a = {});
    var seen = {};
    var tag = o.tagName;
    for (var i = 0; i < n.attributes.length; i++) {
      var a = n.attributes[i];
      seen[a.name] = 1;
      if (a.name === 'value' && (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT')) {
        o.__val = a.value; continue;
      }
      if (prev[a.name] !== a.value) {
        prev[a.name] = a.value;
        try { o.setAttribute(a.name, a.value); } catch (e) {}
      }
    }
    for (var k in prev) {
      if (!seen[k]) { delete prev[k]; if (k !== 'value') o.removeAttribute(k); }
    }
    if (o.__val !== undefined && !n.hasAttribute('value')) o.__val = undefined;
  }

  var EVMAP = { mouseenter: 1, mouseleave: 1 };
  function bindEl(o, inst) {
    var ev = o.__ev || (o.__ev = {}), ls = o.__ls || (o.__ls = {});
    for (var i = 0; i < o.attributes.length; i++) {
      var a = o.attributes[i];
      if (a.name.indexOf('data-on-') === 0) {
        var type = a.name.slice(8);
        var fn = inst._handlers[+a.value];
        ev[type] = typeof fn === 'function' ? fn : null;
        if (!ls[type]) {
          ls[type] = true;
          (function (type) {
            o.addEventListener(type, function (e) { var f = o.__ev[type]; if (!e.nativeEvent) { try { e.nativeEvent = e; } catch (x) {} } if (f) f(e); }, type === 'touchstart' || type === 'touchend' ? { passive: true } : false);
          })(type);
        }
      } else if (a.name === 'data-ref') {
        var r = inst._handlers[+a.value];
        if (r && typeof r === 'object') r.current = o;
      }
    }
  }

  function bindTree(root, inst) {
    if (root.nodeType !== 1) return;
    bindEl(root, inst);
    for (var c = root.firstChild; c; c = c.nextSibling) if (!isHost(c)) bindTree(c, inst);
  }

  function applyValue(o) {
    if (o.__val !== undefined && o.value !== o.__val) o.value = o.__val;
  }

  function morphNode(o, n, inst) {
    if (n.nodeType === 3) { if (o.nodeValue !== n.nodeValue) o.nodeValue = n.nodeValue; return; }
    syncAttrs(o, n, inst);
    bindEl(o, inst);
    if (isHost(n)) return;
    var tg = o.tagName, isField = tg === 'SELECT' || tg === 'INPUT' || tg === 'TEXTAREA';
    if (n.hasAttribute('data-ref') && !n.firstChild) { if (isField) applyValue(o); return; } // содержимое такого узла ведёт код компонента
    morphChildren(o, n, inst);
    if (isField) applyValue(o);
  }

  function morphChildren(op, np, inst) {
    var o = op.firstChild, n = np.firstChild;
    while (n) {
      var nn = n.nextSibling;
      if (!o) {
        op.appendChild(n); bindTree(n, inst); applyInit(n);
      } else if (o.nodeType === n.nodeType && (o.nodeType === 3 || o.tagName === n.tagName)) {
        morphNode(o, n, inst);
        o = o.nextSibling;
      } else {
        op.replaceChild(n, o); bindTree(n, inst); applyInit(n);
        o = n.nextSibling;
      }
      n = nn;
    }
    while (o) { var nx = o.nextSibling; op.removeChild(o); o = nx; }
  }

  function applyInit(root) {
    if (root.nodeType !== 1) return;
    var all = [root].concat([].slice.call(root.querySelectorAll('input,textarea,select')));
    all.forEach(function (el) {
      if (el.hasAttribute && el.hasAttribute('value') && /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) {
        el.__val = el.getAttribute('value'); applyValue(el);
      }
    });
  }

  /* ---------- API ---------- */
  window.DCLogic = DCLogic;
  window.DC = {
    define: function (name, cls, tpl) { registry[name] = { cls: cls, tpl: tpl }; },
    start: function () {
      var go = function () { mountNested(document.body); };
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
    }
  };
})();
