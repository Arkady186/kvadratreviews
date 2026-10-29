/* ASD · 3D-образцы фасадов для «Гида по материалам».
   ASDSamples.mount(host, {onPick(i), single: i, still: true}) */
(function () {
  'use strict';
  var G = window.GL3D; if (!G) return;
  var T = G.tex, hex = G.hex;
  var MATS = [
    { id: 'ldsp', name: 'ЛДСП', note: 'ламинированная плита', tex: function () { return T.wood({ tone: '#C79B6B', dark: 'rgba(110,70,35,', lines: 90, seed: 11 }); }, side: '#B88D5F', gloss: 6 },
    { id: 'plenka', name: 'Плёнка ПВХ', note: 'МДФ, вакуумное прессование', tex: function () { return T.solid({ tone: '#E6E1D7', frame: true, seed: 4 }); }, side: '#E9E5DD', gloss: 14 },
    { id: 'hpl', name: 'Пластик HPL', note: 'слоистый пластик', tex: function () { return T.marble({ tone: '#D9D6D1', vein: '70,68,66', veins: 12, seed: 21 }); }, side: '#1B1A19', gloss: 30 },
    { id: 'emal', name: 'Эмаль', note: 'краска и лак по МДФ', tex: function () { return T.solid({ tone: '#5E6B60', shine: true, seed: 8 }); }, side: '#5E6B60', gloss: 70 },
    { id: 'massiv', name: 'Массив', note: 'цельная древесина', tex: function () { return T.wood({ tone: '#9C6B3E', dark: 'rgba(60,32,12,', lines: 120, knots: 2, planks: 3, seed: 5 }); }, side: '#8A5C33', gloss: 10 }
  ];
  var SW = 1.05, SH = 3.0, SD = 0.1;

  function mount(host, opts) {
    opts = opts || {};
    var cv = document.createElement('canvas');
    cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:pan-y;cursor:grab';
    cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', '3D-образцы фасадов: ЛДСП, плёнка ПВХ, пластик HPL, эмаль, массив');
    host.appendChild(cv);
    var sc; try { sc = new G.Scene(cv, { preserve: !!opts.still, light: [0.35, 0.75, 0.9], ambient: [0.44, 0.43, 0.42], fov: 0.5 }); } catch (e) { cv.remove(); return null; }
    var single = opts.single != null ? opts.single : -1;
    var list = single >= 0 ? [MATS[single]] : MATS;
    var items = list.map(function (m, i) {
      var g = new G.Geo(), w = hex('#FFFFFF'), s = hex(m.side);
      g.box(-SW / 2, -SH / 2, -SD / 2, SW / 2, SH / 2, SD / 2, { front: w, side: s, back: hex(m.side, 0.9) });
      var it = sc.mesh(g, { tex: sc.texture(m.tex()), gloss: m.gloss });
      /* тонкая линия-кромка спереди: подчёркивает толщину */
      return { it: it, m: m, i: i, hov: 0, base: 0 };
    });
    var n = items.length, sel = -1, auto = 0, t0 = performance.now(), yaw = 0, tyaw = 0, pit = 0.06, tpit = 0.06, drag = null, vis = true, raf = 0;
    sc.cam.t = [0, 0, 0];
    sc.cam.dist = single >= 0 ? 8.2 : 11.5; if (single < 0) sc.cam.t = [0, 0.1, 0];
    function layout(t) {
      items.forEach(function (o, i) {
        o.hov += ((i === sel ? 1 : 0) - o.hov) * 0.12;
        if (single >= 0) { o.it.m = G.trs([0, 0, 0], [0, 0, 0]); o.pos = [0, 0, 0]; return; }
        var k = i - (n - 1) / 2, ang = -k * 0.3 * (1 - o.hov * 0.2), breath = Math.sin(t * 0.0008 + i) * 0.012;
        /* веер образцов: все пластины вращаются вокруг общей оси внизу */
        var piv = G.trs([0, -1.9 + o.hov * 0.35, i * 0.03 + o.hov * 0.55], [0, o.hov * 0.12, ang + breath]);
        o.it.m = G.mul(piv, G.trs([0, SH / 2, 0]));
        o.it.tint = sel >= 0 && i !== sel ? [0.9, 0.9, 0.9] : [1, 1, 1];
        var a = ang + breath; o.pos = [-Math.sin(a) * SH * 0.62, -1.9 + o.hov * 0.35 + Math.cos(a) * SH * 0.62, i * 0.03];
      });
    }
    function frame(t) {
      raf = 0;
      if (!opts.still) {
        if (!drag) { tyaw = Math.sin(t * 0.00018) * 0.3 + (single >= 0 ? t * 0.0003 : 0); }
        if (single < 0 && !drag && !hovering && t - auto > 2600) { auto = t; sel = (sel + 1) % n; emit(); }
      } else { tyaw = single >= 0 ? -0.55 : 0.22; tpit = 0.18; }
      yaw += (tyaw - yaw) * (opts.still ? 1 : 0.06); pit += (tpit - pit) * (opts.still ? 1 : 0.06);
      sc.cam.yaw = yaw; sc.cam.pit = pit;
      layout(opts.still ? 0 : t); sc.render();
      if (!opts.still && vis) raf = requestAnimationFrame(frame);
    }
    function emit() { if (opts.onPick) opts.onPick(sel >= 0 ? items[sel].m : null, sel); }
    var hovering = false;
    function pickAt(ev) {
      var r = cv.getBoundingClientRect(), mx = ev.clientX - r.left, my = ev.clientY - r.top, best = -1, bd = 1e9;
      items.forEach(function (o, i) { var p = sc.project(o.pos); if (!p) return; var d = Math.hypot(p[0] - mx, (p[1] - my) * 0.6); if (d < bd) { bd = d; best = i; } });
      return bd < r.width / (n + 1) ? best : -1;
    }
    if (!opts.still) {
      cv.addEventListener('pointermove', function (ev) {
        if (drag) { tyaw = drag.y0 - (ev.clientX - drag.x) * 0.006; tpit = Math.max(-0.1, Math.min(0.6, drag.p0 + (ev.clientY - drag.yy) * 0.004)); return; }
        if (ev.pointerType === 'touch') return;
        var i = pickAt(ev); hovering = i >= 0; if (i !== sel && i >= 0) { sel = i; emit(); } auto = performance.now();
      });
      cv.addEventListener('pointerleave', function () { hovering = false; });
      cv.addEventListener('pointerdown', function (ev) { drag = { x: ev.clientX, yy: ev.clientY, y0: yaw, p0: pit, moved: false, t: performance.now() }; cv.style.cursor = 'grabbing'; });
      window.addEventListener('pointerup', function (ev) {
        if (!drag) return; var click = Math.abs(ev.clientX - drag.x) < 6 && performance.now() - drag.t < 400; drag = null; cv.style.cursor = 'grab';
        if (click) { var i = pickAt(ev); if (i >= 0) { sel = i; emit(); if (opts.onOpen) opts.onOpen(items[i].m, i); } }
        auto = performance.now();
      });
      if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { vis = es[0].isIntersecting; if (vis && !raf) raf = requestAnimationFrame(frame); }).observe(host);
    }
    if (single >= 0 || opts.still) sel = -1; else { sel = 0; emit(); }
    raf = requestAnimationFrame(frame);
    if (opts.still) { frame(0); }
    return { canvas: cv, select: function (i) { sel = i; auto = performance.now(); emit(); }, mats: MATS };
  }
  window.ASDSamples = { mount: mount, MATS: MATS };
})();
