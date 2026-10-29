/* ASD · маленький 3D-движок на чистом WebGL (без библиотек).
   Используется в «Гиде по материалам» (образцы материалов) и на главной (3D-модель кухни). */
(function () {
  'use strict';

  /* ---------- математика (матрицы по столбцам, как в WebGL) ---------- */
  function perspective(f, a, n, fa) { var t = 1 / Math.tan(f / 2), r = 1 / (n - fa); return [t / a, 0, 0, 0, 0, t, 0, 0, 0, 0, (n + fa) * r, -1, 0, 0, 2 * n * fa * r, 0]; }
  function norm(a) { var l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function lookAt(e, t, u) {
    var f = norm([t[0] - e[0], t[1] - e[1], t[2] - e[2]]), s = norm(cross(f, u)), w = cross(s, f);
    return [s[0], w[0], -f[0], 0, s[1], w[1], -f[1], 0, s[2], w[2], -f[2], 0,
      -(s[0] * e[0] + s[1] * e[1] + s[2] * e[2]), -(w[0] * e[0] + w[1] * e[1] + w[2] * e[2]), f[0] * e[0] + f[1] * e[1] + f[2] * e[2], 1];
  }
  function mul(a, b) { var o = new Array(16); for (var i = 0; i < 4; i++) for (var j = 0; j < 4; j++) { var s = 0; for (var k = 0; k < 4; k++) s += a[k * 4 + j] * b[i * 4 + k]; o[i * 4 + j] = s; } return o; }
  function ident() { return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; }
  function trs(t, r, s) { /* t=[x,y,z], r=[rx,ry,rz] (радианы, порядок Y·X·Z), s=[sx,sy,sz] */
    r = r || [0, 0, 0]; s = s || [1, 1, 1];
    var cx = Math.cos(r[0]), sx = Math.sin(r[0]), cy = Math.cos(r[1]), sy = Math.sin(r[1]), cz = Math.cos(r[2]), sz = Math.sin(r[2]);
    var X = [1, 0, 0, 0, 0, cx, sx, 0, 0, -sx, cx, 0, 0, 0, 0, 1],
      Y = [cy, 0, -sy, 0, 0, 1, 0, 0, sy, 0, cy, 0, 0, 0, 0, 1],
      Z = [cz, sz, 0, 0, -sz, cz, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
      S = [s[0], 0, 0, 0, 0, s[1], 0, 0, 0, 0, s[2], 0, 0, 0, 0, 1],
      T = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, t[0], t[1], t[2], 1];
    return mul(T, mul(Y, mul(X, mul(Z, S))));
  }
  function hex(h, k) { k = k == null ? 1 : k; return [parseInt(h.slice(1, 3), 16) / 255 * k, parseInt(h.slice(3, 5), 16) / 255 * k, parseInt(h.slice(5, 7), 16) / 255 * k]; }

  /* ---------- геометрия ---------- */
  /* Меш: массив вершин [x,y,z, nx,ny,nz, u,v, r,g,b] */
  function Geo() { this.v = []; }
  Geo.prototype.vert = function (p, n, uv, c) { this.v.push(p[0], p[1], p[2], n[0], n[1], n[2], uv[0], uv[1], c[0], c[1], c[2]); };
  Geo.prototype.quad = function (a, b, c, d, n, col, uv) {
    uv = uv || [[0, 1], [1, 1], [1, 0], [0, 0]];
    this.vert(a, n, uv[0], col); this.vert(b, n, uv[1], col); this.vert(c, n, uv[2], col);
    this.vert(a, n, uv[0], col); this.vert(c, n, uv[2], col); this.vert(d, n, uv[3], col);
  };
  /* Коробка; cols = {front, back, top, bottom, side} — цвет граней; front получает UV 0..1 */
  Geo.prototype.box = function (x0, y0, z0, x1, y1, z1, cols) {
    var f = cols.front, s = cols.side || f, t = cols.top || s, b = cols.bottom || s, bk = cols.back || s;
    this.quad([x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1], [0, 0, 1], f);
    this.quad([x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0], [0, 0, -1], bk, [[0, 0], [0, 0], [0, 0], [0, 0]]);
    this.quad([x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0], [0, 1, 0], t, [[0, 0], [0, 0], [0, 0], [0, 0]]);
    this.quad([x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], [0, -1, 0], b, [[0, 0], [0, 0], [0, 0], [0, 0]]);
    this.quad([x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [1, 0, 0], s, [[0, 0], [0, 0], [0, 0], [0, 0]]);
    this.quad([x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0], [-1, 0, 0], s, [[0, 0], [0, 0], [0, 0], [0, 0]]);
    return this;
  };
  /* Рёбра коробки линиями */
  Geo.prototype.edges = function (x0, y0, z0, x1, y1, z1, col) {
    var P = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
      E = [0, 1, 1, 2, 2, 3, 3, 0, 4, 5, 5, 6, 6, 7, 7, 4, 0, 4, 1, 5, 2, 6, 3, 7], n = [0, 1, 0], me = this;
    E.forEach(function (i) { me.vert(P[i], n, [0, 0], col); });
    return this;
  };
  Geo.prototype.line = function (a, b, col) { this.vert(a, [0, 1, 0], [0, 0], col); this.vert(b, [0, 1, 0], [0, 0], col); return this; };

  var VS = 'attribute vec3 p;attribute vec3 n;attribute vec2 uv;attribute vec3 c;' +
    'uniform mat4 vp;uniform mat4 m;varying vec3 vn;varying vec2 vu;varying vec3 vc;varying vec3 vw;' +
    'void main(){vec4 w=m*vec4(p,1.);vw=w.xyz;gl_Position=vp*w;vn=mat3(m)*n;vu=uv;vc=c;}';
  var FS = 'precision mediump float;varying vec3 vn;varying vec2 vu;varying vec3 vc;varying vec3 vw;' +
    'uniform sampler2D tx;uniform float useTex;uniform float unlit;uniform float gloss;uniform float alpha;uniform vec3 eye;uniform vec3 L;uniform vec3 amb;uniform vec3 tint;' +
    'void main(){vec3 base=vc;float isF=step(.001,vu.x+vu.y);if(useTex>.5&&isF>.5){base=texture2D(tx,vu).rgb*vc;}' +
    'if(unlit>.5){gl_FragColor=vec4(base*tint,alpha);return;}' +
    'vec3 N=normalize(vn);float d=max(dot(N,L),0.);vec3 V=normalize(eye-vw);vec3 H=normalize(L+V);' +
    'float sp=gloss>0.?pow(max(dot(N,H),0.),gloss)*min(gloss/40.,1.):0.;float rim=pow(1.-max(dot(N,V),0.),3.)*.18;' +
    'vec3 col=base*(amb+d*.66)+vec3(sp*.55)+rim;gl_FragColor=vec4(col*tint,alpha);}';

  function Scene(canvas, opts) {
    opts = opts || {};
    var gl = canvas.getContext('webgl', { antialias: true, alpha: true, premultipliedAlpha: false, preserveDrawingBuffer: !!opts.preserve }) || canvas.getContext('experimental-webgl');
    if (!gl) throw new Error('no webgl');
    this.gl = gl; this.cv = canvas; this.items = []; this.dpr = Math.min(window.devicePixelRatio || 1, opts.maxDpr || 2);
    function sh(t, s) { var o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; }
    var pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr); gl.useProgram(pr);
    this.A = { p: gl.getAttribLocation(pr, 'p'), n: gl.getAttribLocation(pr, 'n'), uv: gl.getAttribLocation(pr, 'uv'), c: gl.getAttribLocation(pr, 'c') };
    var U = this.U = {}; ['vp', 'm', 'tx', 'useTex', 'unlit', 'gloss', 'alpha', 'eye', 'L', 'amb', 'tint'].forEach(function (k) { U[k] = gl.getUniformLocation(pr, k); });
    gl.enable(gl.DEPTH_TEST); gl.enable(gl.BLEND); gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
    var L = norm(opts.light || [0.45, 0.8, 0.65]); gl.uniform3f(U.L, L[0], L[1], L[2]);
    var a = opts.ambient || [0.42, 0.42, 0.42]; gl.uniform3f(U.amb, a[0], a[1], a[2]);
    this.cam = { yaw: 0, pit: 0.25, dist: 10, t: [0, 0, 0], fov: opts.fov || 0.6 };
    this.clear = opts.clear || [0, 0, 0, 0];
  }
  Scene.prototype.mesh = function (geo, o) {
    var gl = this.gl, b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(geo.v), gl.STATIC_DRAW);
    var it = Object.assign({ buf: b, count: geo.v.length / 11, mode: gl.TRIANGLES, tex: null, gloss: 0, alpha: 1, unlit: 0, m: ident(), tint: [1, 1, 1], visible: true, depthWrite: true }, o || {});
    if (o && o.lines) it.mode = gl.LINES;
    this.items.push(it); return it;
  };
  Scene.prototype.texture = function (canvas) {
    var gl = this.gl, t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, canvas);
    var pot = (canvas.width & (canvas.width - 1)) === 0 && (canvas.height & (canvas.height - 1)) === 0;
    if (pot) { gl.generateMipmap(gl.TEXTURE_2D); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); }
    else gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return t;
  };
  Scene.prototype.size = function () {
    var w = this.cv.clientWidth, h = this.cv.clientHeight, d = this.dpr;
    if (this.cv.width !== Math.round(w * d) || this.cv.height !== Math.round(h * d)) { this.cv.width = Math.round(w * d); this.cv.height = Math.round(h * d); }
    this.gl.viewport(0, 0, this.cv.width, this.cv.height);
  };
  Scene.prototype.eye = function () {
    var c = this.cam; return [c.t[0] + c.dist * Math.sin(c.yaw) * Math.cos(c.pit), c.t[1] + c.dist * Math.sin(c.pit), c.t[2] + c.dist * Math.cos(c.yaw) * Math.cos(c.pit)];
  };
  Scene.prototype.render = function () {
    var gl = this.gl, U = this.U, A = this.A; this.size();
    var asp = this.cv.width / Math.max(1, this.cv.height), E = this.eye();
    var VP = mul(perspective(this.cam.fov, asp, 0.1, 400), lookAt(E, this.cam.t, [0, 1, 0]));
    this.VP = VP; this.asp = asp;
    gl.clearColor(this.clear[0], this.clear[1], this.clear[2], this.clear[3]); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.uniformMatrix4fv(U.vp, false, new Float32Array(VP)); gl.uniform3f(U.eye, E[0], E[1], E[2]);
    var list = this.items.filter(function (i) { return i.visible && i.alpha > 0.003; });
    list.sort(function (a, b) { return (a.alpha < 1) - (b.alpha < 1); });
    for (var i = 0; i < list.length; i++) {
      var it = list[i];
      gl.depthMask(it.alpha >= 1 && it.depthWrite);
      gl.bindBuffer(gl.ARRAY_BUFFER, it.buf);
      var st = 44;
      gl.enableVertexAttribArray(A.p); gl.vertexAttribPointer(A.p, 3, gl.FLOAT, false, st, 0);
      gl.enableVertexAttribArray(A.n); gl.vertexAttribPointer(A.n, 3, gl.FLOAT, false, st, 12);
      gl.enableVertexAttribArray(A.uv); gl.vertexAttribPointer(A.uv, 2, gl.FLOAT, false, st, 24);
      gl.enableVertexAttribArray(A.c); gl.vertexAttribPointer(A.c, 3, gl.FLOAT, false, st, 32);
      gl.uniformMatrix4fv(U.m, false, new Float32Array(it.m));
      gl.uniform1f(U.useTex, it.tex ? 1 : 0); if (it.tex) { gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, it.tex); gl.uniform1i(U.tx, 0); }
      gl.uniform1f(U.unlit, it.unlit || it.mode === gl.LINES ? 1 : 0); gl.uniform1f(U.gloss, it.gloss); gl.uniform1f(U.alpha, it.alpha);
      gl.uniform3f(U.tint, it.tint[0], it.tint[1], it.tint[2]);
      gl.drawArrays(it.mode, 0, it.count);
    }
    gl.depthMask(true);
  };
  /* Проекция мировой точки в CSS-пиксели канваса */
  Scene.prototype.project = function (p) {
    var M = this.VP; if (!M) return null;
    var x = M[0] * p[0] + M[4] * p[1] + M[8] * p[2] + M[12], y = M[1] * p[0] + M[5] * p[1] + M[9] * p[2] + M[13], w = M[3] * p[0] + M[7] * p[1] + M[11] * p[2] + M[15];
    return [(x / w * 0.5 + 0.5) * this.cv.clientWidth, (1 - (y / w * 0.5 + 0.5)) * this.cv.clientHeight];
  };

  /* ---------- процедурные текстуры материалов ---------- */
  function rng(seed) { var s = seed || 1; return function () { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; }; }
  function cnv(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  /* Древесина: годичные кольца + поры. tone — основной цвет, dark — цвет волокон */
  function wood(o) {
    o = o || {}; var W = 512, H = 1024, c = cnv(W, H), x = c.getContext('2d'), r = rng(o.seed || 7);
    x.fillStyle = o.tone || '#B98D5E'; x.fillRect(0, 0, W, H);
    var dark = o.dark || 'rgba(90,55,25,', lines = o.lines || 70;
    for (var i = 0; i < lines; i++) {
      var x0 = r() * W, amp = 6 + r() * 26, fr = 0.002 + r() * 0.006, ph = r() * 6, wdt = 0.6 + r() * 2.6, al = 0.06 + r() * 0.22;
      x.beginPath(); for (var y = 0; y <= H; y += 8) { var xx = x0 + Math.sin(y * fr + ph) * amp + Math.sin(y * fr * 3.1 + ph) * amp * 0.25; y ? x.lineTo(xx, y) : x.moveTo(xx, y); }
      x.strokeStyle = dark + al + ')'; x.lineWidth = wdt; x.stroke();
    }
    for (var k = 0; k < (o.knots || 0); k++) { var kx = r() * W, ky = r() * H; for (var j = 1; j < 9; j++) { x.beginPath(); x.ellipse(kx, ky, j * 5, j * 11, 0, 0, 7); x.strokeStyle = dark + (0.25 - j * 0.02) + ')'; x.lineWidth = 1.4; x.stroke(); } }
    for (var p = 0; p < 2600; p++) { x.fillStyle = dark + (r() * 0.12) + ')'; x.fillRect(r() * W, r() * H, 1, 2 + r() * 6); }
    if (o.planks) { x.strokeStyle = 'rgba(40,25,10,.35)'; x.lineWidth = 2; for (var q = 1; q < o.planks; q++) { x.beginPath(); x.moveTo(W * q / o.planks, 0); x.lineTo(W * q / o.planks, H); x.stroke(); } }
    return c;
  }
  /* Камень/мрамор: прожилки */
  function marble(o) {
    o = o || {}; var W = 512, H = 1024, c = cnv(W, H), x = c.getContext('2d'), r = rng(o.seed || 3);
    x.fillStyle = o.tone || '#ECE9E4'; x.fillRect(0, 0, W, H);
    for (var s = 0; s < 3000; s++) { x.fillStyle = 'rgba(' + (o.speck || '120,115,110') + ',' + r() * 0.08 + ')'; x.fillRect(r() * W, r() * H, 2 + r() * 4, 2 + r() * 4); }
    for (var i = 0; i < (o.veins || 9); i++) {
      var px = r() * W, py = -20, ang = 0.6 + r() * 1.2;
      x.beginPath(); x.moveTo(px, py);
      for (var k = 0; k < 60; k++) { ang += (r() - 0.5) * 0.5; px += Math.cos(ang) * 14; py += Math.abs(Math.sin(ang)) * 22 + 4; x.lineTo(px, py); }
      x.strokeStyle = 'rgba(' + (o.vein || '90,88,86') + ',' + (0.25 + r() * 0.45) + ')'; x.lineWidth = 0.6 + r() * 2.4; x.stroke();
    }
    return c;
  }
  /* Ровный цвет с лёгкой фактурой и, при желании, фрезеровкой рамки */
  function solid(o) {
    o = o || {}; var W = 512, H = 1024, c = cnv(W, H), x = c.getContext('2d'), r = rng(o.seed || 5);
    x.fillStyle = o.tone || '#EDEAE4'; x.fillRect(0, 0, W, H);
    for (var s = 0; s < 1500; s++) { x.fillStyle = 'rgba(0,0,0,' + r() * 0.02 + ')'; x.fillRect(r() * W, r() * H, 2, 2); }
    if (o.frame) {
      var m = 62, i2 = 82;
      /* фрезеровка рамки: тень сверху-слева, блик снизу-справа */
      x.lineWidth = 14; x.strokeStyle = 'rgba(0,0,0,.16)'; x.strokeRect(m, m, W - 2 * m, H - 2 * m);
      x.lineWidth = 6; x.strokeStyle = 'rgba(255,255,255,.7)'; x.strokeRect(m + 10, m + 10, W - 2 * m - 20, H - 2 * m - 20);
      x.lineWidth = 4; x.strokeStyle = 'rgba(0,0,0,.18)'; x.strokeRect(i2, i2, W - 2 * i2, H - 2 * i2);
      x.fillStyle = 'rgba(0,0,0,.035)'; x.fillRect(i2, i2, W - 2 * i2, H - 2 * i2);
    }
    if (o.shine) { x.fillStyle = 'rgba(255,255,255,.07)'; x.beginPath(); x.moveTo(0, H * 0.15); x.lineTo(W, H * 0.02); x.lineTo(W, H * 0.22); x.lineTo(0, H * 0.4); x.fill(); }
    return c;
  }
  /* Срез ДСП: стружка */
  function chip(o) {
    o = o || {}; var W = 256, H = 256, c = cnv(W, H), x = c.getContext('2d'), r = rng(o.seed || 9);
    x.fillStyle = '#C9A877'; x.fillRect(0, 0, W, H);
    for (var s = 0; s < 1400; s++) { x.fillStyle = ['#A9824F', '#DCC293', '#8F6A3C', '#E8D3A8'][s % 4]; x.save(); x.translate(r() * W, r() * H); x.rotate(r() * 3); x.fillRect(0, 0, 3 + r() * 7, 1 + r() * 2); x.restore(); }
    return c;
  }

  window.GL3D = { Scene: Scene, Geo: Geo, trs: trs, mul: mul, hex: hex, tex: { wood: wood, marble: marble, solid: solid, chip: chip } };
})();
