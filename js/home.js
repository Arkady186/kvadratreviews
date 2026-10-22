/* ASD — главная страница: чертёж, витрина, направления, отзывы, анимации */
Chrome.init('home');
const { esc, ICONS, stars, fmtNum, plural } = Chrome;
const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="square" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>';
const prefersReduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

/* ---------- Чертёж: три кухни по кругу ---------- */
    const W = window.WORKS;
    const bp = document.getElementById('bp');
    const bpSvg = bp.querySelector('svg');
    const reduce = prefersReduce;
    const fmt = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00A0');
    let cnts = [];
    const timers = [];
    const later = (fn, ms) => timers.push(setTimeout(fn, ms));
    let inView = true, idx = -1;
    new IntersectionObserver((e) => { inView = e[0].isIntersecting; }, { threshold: 0.35 }).observe(bp);

    function counters(dir) {            // dir: 1 — набираем, -1 — откатываем
      cnts.forEach((el) => {
        const v = +el.dataset.val, d0 = parseFloat(el.style.getPropertyValue('--d'));
        const delay = dir > 0 ? d0 * 1000 : (7.2 - d0) * 0.28 * 1000, dur = dir > 0 ? 1100 : 900, t0 = performance.now() + delay;
        const tick = (now) => {
          const k = Math.min(1, Math.max(0, (now - t0) / dur)), e = 1 - Math.pow(1 - k, 3);
          el.textContent = fmt(Math.round(dir > 0 ? v * e : v * (1 - e)));
          if (k < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    }
    function load(i) {                  // подставляем чертёж i
      const list = window.KITCHENS || [];
      if (!list.length) { cnts = [...bp.querySelectorAll('.cnt')]; return; }
      bpSvg.innerHTML = list[i % list.length];
      cnts = [...bp.querySelectorAll('.cnt')];
    }
    function draw() {
      idx = (idx + 1) % Math.max(1, (window.KITCHENS || []).length || 1);
      const sn = document.getElementById('sheet-no'); if (sn) sn.textContent = String(idx + 1).padStart(2, '0') + ' / ' + String(Math.max(1, (window.KITCHENS || []).length || 1)).padStart(2, '0');
      bp.classList.remove('is-drawing', 'is-undrawing');
      load(idx); void bp.getBoundingClientRect();
      bp.classList.add('is-drawing');
      cnts.forEach((el) => { el.textContent = '0'; });
      counters(1);
      later(waitThenRewind, 7200 + 5000);
    }
    function waitThenRewind() {
      if (!inView || document.hidden) { later(waitThenRewind, 1000); return; }   // не мешаем, пока чертёж не на виду
      bp.classList.remove('is-drawing'); void bp.getBoundingClientRect();
      bp.classList.add('is-undrawing');
      counters(-1);
      later(draw, 3200 + 1000);
    }
    if (reduce) { cnts = [...bp.querySelectorAll('.cnt')]; cnts.forEach((el) => { el.textContent = fmt(+el.dataset.val); }); bp.classList.remove('is-drawing'); }
    else draw();


/* ---------- Бегущая строка ---------- */
(function () {
  const words = W.categories.map((c) => c.title).concat(['Под ваши размеры', 'Дизайн-проект']);
  const g = words.map((w) => `<span>${esc(w)}</span><span class="s">&#10022;</span>`).join('');
  document.getElementById('marq').innerHTML = `<div class="marq__g">${g}</div><div class="marq__g">${g}</div>`;
})();

/* ---------- Витрина работ ---------- */
(function () {
  const counts = Chrome.counts();
  const total = (W.items || []).length;
  ['st-works', 'sc-total'].forEach((id) => { const el = document.getElementById(id); if (el) { el.dataset.count = total; el.textContent = total; } });
  const picks = [
    ['a', 'kuhni', 'kuhni-121-738113'],
    ['b', 'kuhni', 'kuhni-144-376436'],
    ['c', 'sanuzly', 'sanuzly-014-8acf25'],
    ['d', 'shkafy', 'shkafy-017-94616f'],
    ['e', 'tv-zony', 'tv-zony-004-029cba'],
    ['f', 'shkafy', 'shkafy-031-508fd6'],
    ['g', 'kuhni', 'kuhni-125-0a1707'],
  ];
  const html = picks.map(([cls, cat, file], i) => {
    const item = (W.items || []).find((x) => x.full.indexOf(file) !== -1);
    const c = W.categories.find((x) => x.id === cat);
    if (!item || !c) return '';
    return `
      <a class="tile tile--${cls}" href="works.html?c=${cat}" data-reveal style="--i:${i % 4}" aria-label="Раздел «${esc(c.title)}»">
        <img src="${esc(item.full)}" alt="${esc(c.title)} на заказ — работа ASD" loading="lazy" width="${item.w}" height="${item.h}" data-parallax="0.05">
        <span class="tile__cap"><span><small>${counts[cat] ? Chrome.photosWord(counts[cat]) : ''}</small><b>${esc(c.title)}</b></span><span class="tile__go">${ARROW}</span></span>
      </a>`;
  }).join('');
  document.getElementById('mosaic').innerHTML = html;
})();

/* ---------- Направления ---------- */
(function () {
  const counts = Chrome.counts();
  document.getElementById('cats').innerHTML = W.categories.map((c, i) => {
    const art = (window.CAT_ART || {})[c.id];
    return `
      <a class="cat ${art ? 'cat--bp' : ''}" href="works.html?c=${c.id}" data-reveal style="--i:${i}">
        <span class="cat__idx">0${i + 1}</span><span class="cat__arrow">${ARROW}</span>
        ${art ? `<span class="cat__art" aria-hidden="true">${art}</span>` : `<span class="cat__icon">${ICONS[c.id]}</span>`}
        <span class="cat__name">${esc(c.title)}<span class="cat__n">${counts[c.id] ? Chrome.photosWord(counts[c.id]) : 'скоро'}</span></span>
      </a>`;
  }).join('');
})();

/* ---------- Отзывы ---------- */
Api.listReviews().then((list) => {
  const real = list.filter((r) => !r.sample);
  if (real.length) {
    const avg = real.reduce((s, r) => s + r.rating, 0) / real.length;
    document.getElementById('hero-proof').innerHTML = `${stars(avg)} <span><strong>${fmtNum(avg)}</strong> по ${real.length} ${plural(real.length, ['отзыву', 'отзывам', 'отзывам'])}</span>`;
  }
  const top = list.slice(0, 5);
  if (!top.length) return;
  const sec = document.getElementById('latest');
  sec.hidden = false;
  const base = real.length ? real : list;
  const avg = base.reduce((s, r) => s + r.rating, 0) / base.length;
  document.getElementById('rvs-score').innerHTML = `<b>${fmtNum(avg)}</b><div>${stars(avg)}<small>средняя оценка по ${base.length} ${plural(base.length, ['отзыву', 'отзывам', 'отзывам'])}</small></div>`;
  const qc = document.getElementById('qc');
  qc.innerHTML = top.map((r, i) => `
    <figure class="qc__slide ${i === 0 ? 'is-on' : ''}" style="margin:0">
      <p>«${esc(r.body.length > 260 ? r.body.slice(0, 257).trim() + '…' : r.body)}»</p>
      <figcaption class="qc__who"><i>${esc((r.name || '?').trim().charAt(0).toUpperCase())}</i><div><strong>${esc(r.name)}</strong><small>${Chrome.fmtDate(r.created_at)}${r.sample ? ' · пример отзыва' : ''}</small></div>${stars(r.rating)}</figcaption>
    </figure>`).join('');
  const slides = [...qc.children];
  const dots = document.getElementById('qc-dots');
  dots.innerHTML = slides.map((_, i) => `<button type="button" aria-label="Отзыв ${i + 1}"></button>`).join('');
  const dotEls = [...dots.children];
  let cur = 0, timer = null;
  const show = (n) => {
    cur = (n + slides.length) % slides.length;
    slides.forEach((s, i) => s.classList.toggle('is-on', i === cur));
    dotEls.forEach((d, i) => { d.classList.remove('is-on'); d.classList.toggle('is-done', i < cur); });
    void dots.offsetWidth; dotEls[cur].classList.add('is-on');
    clearTimeout(timer);
    if (!prefersReduce && slides.length > 1) timer = setTimeout(() => show(cur + 1), 7000);
  };
  dotEls.forEach((d, i) => d.addEventListener('click', () => show(i)));
  document.getElementById('qc-prev').addEventListener('click', () => show(cur - 1));
  document.getElementById('qc-next').addEventListener('click', () => show(cur + 1));
  if (slides.length < 2) document.querySelector('.qc__nav').hidden = true;
  qc.addEventListener('mouseenter', () => clearTimeout(timer));
  qc.addEventListener('mouseleave', () => show(cur));
  show(0);
  observe(sec);
}).catch(() => {});

/* ---------- Анимации ---------- */
function countUp(el) {
  const to = +el.dataset.count || 0;
  const suffix = el.dataset.suffix ? `<sup>${esc(el.dataset.suffix)}</sup>` : '';
  if (prefersReduce || !to) { el.innerHTML = fmt(to) + suffix; return; }
  const t0 = performance.now(), dur = 1600;
  const tick = (t) => {
    const p = Math.min(1, (t - t0) / dur);
    el.innerHTML = fmt(Math.round(to * (1 - Math.pow(1 - p, 3)))) + suffix;
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
let io = null;
function observe(root) {
  const els = [...(root.matches && root.matches('[data-reveal]') ? [root] : []), ...root.querySelectorAll('[data-reveal]')];
  if (!io) return els.forEach((el) => el.classList.add('is-in'));
  els.forEach((el) => io.observe(el));
}
if ('IntersectionObserver' in window) {
  io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      en.target.querySelectorAll('[data-count]').forEach(countUp);
      io.unobserve(en.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
}
observe(document);
/* первый экран и заголовок */
requestAnimationFrame(() => setTimeout(() => {
  document.getElementById('h-title').classList.add('is-in');
  document.getElementById('hero').classList.add('is-in');
}, 120));
document.querySelectorAll('.sc-head__count').forEach((el) => { if (io) io.observe(el); });

/* ---------- Прокрутка: индикатор, шапка, параллакс ---------- */
const bar = document.getElementById('h-progress');
const header = document.querySelector('.site-header');
const par = () => [...document.querySelectorAll('[data-parallax]')];
let ticking = false;
function onScroll() {
  ticking = false;
  const vh = innerHeight, max = document.documentElement.scrollHeight - vh;
  if (bar && max > 0) bar.style.transform = `scaleX(${Math.min(1, scrollY / max)})`;
  if (header) header.classList.toggle('is-scrolled', scrollY > 24);
  if (prefersReduce) return;
  par().forEach((el) => {
    const r = el.parentElement.getBoundingClientRect();
    if (r.bottom < -80 || r.top > vh + 80) return;
    const y = (r.top + r.height / 2 - vh / 2) * -parseFloat(el.dataset.parallax);
    el.style.transform = `translate3d(0, ${y.toFixed(1)}px, 0)`;
  });
}
addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
addEventListener('resize', onScroll);
onScroll();

/* ---------- Подсветка за курсором в первом экране ---------- */
if (finePointer && !prefersReduce) {
  const hero = document.getElementById('hero'), spot = document.getElementById('hero-spot');
  hero.addEventListener('pointermove', (e) => {
    const r = hero.getBoundingClientRect();
    spot.style.setProperty('--sx', (e.clientX - r.left) + 'px');
    spot.style.setProperty('--sy', (e.clientY - r.top) + 'px');
  });
}
