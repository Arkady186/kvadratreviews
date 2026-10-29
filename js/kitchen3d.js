/* ASD · 3D-модель кухни для блока «Дизайн-проект»: чертёж «собирается» в объём.
   ASDKitchen3D.mount(host) -> { play(i), stop() } */
(function () {
  'use strict';
  var G = window.GL3D; if (!G) return;
  var hex = G.hex;
  var C = { line: hex('#C9A074'), front: hex('#ECE6DB'), front2: hex('#C7A27A'), body: hex('#D9D1C4'), top: hex('#FFFFFF'), dark: hex('#2B2824'), steel: hex('#8F8A84'), floor: hex('#C9A074') };

  /* Элемент: [x0,y0,z0,x1,y1,z1, тип]. Ось Z — от стены к нам, стена в z=0. */
  function straight() {
    var a = [], x = -2.1;
    [0.6, 0.6, 0.8, 0.6].forEach(function (w, i) { a.push([x, 0.1, 0, x + w - 0.004, 0.86, 0.6, i === 2 ? 'oven' : 'base']); x += w; });
    a.push([x, 0.1, 0, x + 0.6, 0.86, 0.6, 'sink']); x += 0.6;
    a.push([x, 0, 0, x + 0.62, 2.25, 0.62, 'tall']);
    a.push([-2.14, 0.86, 0, x + 0.004, 0.9, 0.63, 'top']);
    var u = -2.1; [0.6, 0.6, 0.8, 0.6, 0.6].forEach(function (w, i) { if (i !== 2) a.push([u, 1.45, 0, u + w - 0.004, 2.25, 0.34, 'wall']); else a.push([u + 0.1, 1.55, 0, u + w - 0.1, 1.75, 0.45, 'hood']); u += w; });
    return a;
  }
  function corner() {
    var a = [], x = -1.6;
    [0.6, 0.8, 0.6].forEach(function (w, i) { a.push([x, 0.1, 0, x + w - 0.004, 0.86, 0.6, i === 1 ? 'oven' : 'base']); x += w; });
    a.push([x, 0.1, 0, x + 0.6, 0.86, 0.6, 'sink']); x += 0.6;
    a.push([-2.2, 0.1, 0, -1.604, 0.86, 0.6, 'base']);
    var z = 0.6; [0.6, 0.6, 0.6].forEach(function (d) { a.push([-2.2, 0.1, z, -1.6, 0.86, z + d - 0.004, 'base']); z += d; });
    a.push([-2.24, 0.86, 0, x + 0.004, 0.9, 0.63, 'top']); a.push([-2.24, 0.86, 0.63, -1.57, 0.9, z + 0.004, 'top']);
    var u = -1.6; [0.6, 0.8, 0.6, 0.6].forEach(function (w, i) { if (i !== 1) a.push([u, 1.45, 0, u + w - 0.004, 2.25, 0.34, 'wall']); else a.push([u + 0.12, 1.55, 0, u + w - 0.12, 1.75, 0.45, 'hood']); u += w; });
    a.push([-2.2, 0, 2.4, -1.58, 2.25, 3.0, 'tall']);
    return a;
  }
  function island() {
    var a = straight().filter(function (e) { return e[6] !== 'tall'; });
    a.push([-1.0, 0.1, 1.55, 1.0, 0.86, 2.35, 'isl']);
    a.push([-1.05, 0.86, 1.5, 1.05, 0.9, 2.55, 'top']);
    return a;
  }
  var KITS = [straight, corner, island];

  function mount(host) {
    var cv = document.createElement('canvas');
    cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block';
    cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', '3D-модель кухни по чертежу');
    host.appendChild(cv);
    var sc; try { sc = new G.Scene(cv, { light: [-0.35, 0.85, 0.7], ambient: [0.5, 0.48, 0.45], fov: 0.62 }); } catch (e) { cv.remove(); return null; }
    var wood = sc.texture(G.tex.wood({ tone: '#BC9367', dark: 'rgba(100,62,30,', lines: 80, seed: 12 }));
    var parts = [], floor = null, raf = 0, t0 = 0, playing = false, vis = true, onDone = null;

    function build(i) {
      sc.items = []; parts = [];
      var fl = new G.Geo();
      for (var k = -6; k <= 6; k++) { fl.line([k * 0.5, 0, -0.2], [k * 0.5, 0, 3.6], C.floor); }
      for (var m = 0; m <= 7; m++) { fl.line([-3, 0, -0.2 + m * 0.54], [3, 0, -0.2 + m * 0.54], C.floor); }
      /* контур стен */
      fl.line([-2.6, 0, 0], [2.6, 0, 0], C.floor); fl.line([-2.6, 2.6, 0], [2.6, 2.6, 0], C.floor); fl.line([-2.6, 0, 0], [-2.6, 2.6, 0], C.floor); fl.line([2.6, 0, 0], [2.6, 2.6, 0], C.floor);
      if (i % KITS.length === 1) { fl.line([-2.2, 0, 0], [-2.2, 0, 3.4], C.floor); fl.line([-2.2, 2.6, 0], [-2.2, 2.6, 3.4], C.floor); fl.line([-2.2, 0, 3.4], [-2.2, 2.6, 3.4], C.floor); }
      floor = sc.mesh(fl, { lines: true, alpha: 0.3 });
      KITS[i % KITS.length]().forEach(function (e, n) {
        var g = new G.Geo(), x0 = e[0], y0 = e[1], z0 = e[2], x1 = e[3], y1 = e[4], z1 = e[5], ty = e[6], tex = null, gloss = 8, col;
        if (ty === 'top') { col = { front: C.top, side: hex('#E7E2DA'), top: hex('#F2EEE8') }; tex = null; gloss = 40; }
        else if (ty === 'oven' || ty === 'hood') col = { front: C.dark, side: C.steel };
        else if (ty === 'tall' || ty === 'isl') { col = { front: hex('#FFFFFF'), side: C.front2 }; tex = wood; }
        else if (ty === 'wall') col = { front: C.front, side: C.body };
        else col = { front: C.front, side: C.body };
        g.box(x0, y0, z0, x1, y1, z1, col);
        /* декоративные детали фасада: ручка-профиль, стекло духовки, мойка */
        var d = new G.Geo();
        if (ty === 'base' || ty === 'sink' || ty === 'isl') d.box(x0 + 0.05, y1 - 0.05, z1, x1 - 0.05, y1 - 0.035, z1 + 0.012, { front: C.steel });
        if (ty === 'oven') d.box(x0 + 0.08, y0 + 0.12, z1, x1 - 0.08, y1 - 0.22, z1 + 0.01, { front: hex('#4A4540') });
        if (ty === 'sink') d.box(x0 + 0.08, y1 + 0.041, z0 + 0.1, x1 - 0.08, y1 + 0.043, z1 - 0.12, { front: C.steel, top: C.steel });
        if (ty === 'wall') d.box(x0 + 0.05, y0 + 0.035, z1, x1 - 0.05, y0 + 0.05, z1 + 0.012, { front: C.steel });
        var ed = new G.Geo().edges(x0, y0, z0, x1, y1, z1, C.line);
        var solid = sc.mesh(g, { tex: tex, gloss: gloss, alpha: 0 }), det = sc.mesh(d, { gloss: 30, alpha: 0 }), edge = sc.mesh(ed, { lines: true, alpha: 0 });
        parts.push({ solid: solid, det: det, edge: edge, n: n, y: (y0 + y1) / 2 });
      });
    }
    function ease(k) { return k < 0 ? 0 : k > 1 ? 1 : 1 - Math.pow(1 - k, 3); }
    function frame(now) {
      raf = 0; if (!playing) return;
      var t = (now - t0) / 1000, N = parts.length;
      parts.forEach(function (p, i) {
        var e1 = ease((t - i * 0.12) / 0.7), e2 = ease((t - 1.6 - i * 0.09) / 0.8);
        var dy = (1 - e1) * 0.5;
        var M = G.trs([0, dy, 0]);
        p.edge.m = M; p.solid.m = M; p.det.m = M;
        p.edge.alpha = e1 * (1 - e2 * 0.55);
        p.solid.alpha = e2; p.det.alpha = e2;
      });
      floor.alpha = 0.3 * ease(t / 0.8);
      var yaw = 0.95 - Math.min(t, 14) * 0.045;
      sc.cam.t = [0, 1.0, 1.0]; sc.cam.yaw = yaw; sc.cam.pit = 0.42 - Math.min(t, 10) * 0.012; sc.cam.dist = 6.7 - ease(t / 6) * 0.5;
      sc.render();
      if (t > 1.6 + N * 0.09 + 5.5 && onDone) { var f = onDone; onDone = null; f(); }
      if (vis) raf = requestAnimationFrame(frame);
    }
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { vis = es[0].isIntersecting; if (vis && playing && !raf) raf = requestAnimationFrame(frame); }).observe(host);
    return {
      play: function (i, done) { build(i); playing = true; onDone = done || null; t0 = performance.now(); if (!raf) raf = requestAnimationFrame(frame); },
      stop: function () { playing = false; },
      still: function (i) { build(i); playing = true; t0 = performance.now() - 9000; onDone = null; frame(performance.now()); playing = false; }
    };
  }
  window.ASDKitchen3D = { mount: mount };
})();
