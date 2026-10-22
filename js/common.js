/* ============================================================
   Общее для всех страниц: шапка, подвал, иконки, помощники.
   ============================================================ */
const Chrome = (() => {
  const S = window.SITE || {};
  const W = window.WORKS || { categories: [], items: [] };

  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const plural = (n, f) => { const a = Math.abs(n) % 100, b = a % 10; return (a > 10 && a < 20) ? f[2] : b > 1 && b < 5 ? f[1] : b === 1 ? f[0] : f[2]; };
  const fmtDate = (iso) => { try { return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return ''; } };
  const stars = (n, cls) => `<span class="stars ${cls || ''}" role="img" aria-label="Оценка ${n} из 5">${[1, 2, 3, 4, 5].map((i) => `<span class="${i <= Math.round(n) ? '' : 'off'}" aria-hidden="true">★</span>`).join('')}</span>`;
  const fmtNum = (n) => (Math.round(n * 10) / 10).toFixed(1).replace('.', ',');

  const sv = (inner) => `<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="square" stroke-linejoin="miter" aria-hidden="true">${inner}</svg>`;
  const ICONS = {
    kuhni: sv('<rect x="8" y="8" width="48" height="14"/><path d="M32 8v14M24 15h-3M43 15h-3"/><path d="M4 36h56"/><rect x="8" y="36" width="48" height="20"/><path d="M32 36v20M26 46h-2M40 46h-2"/>'),
    shkafy: sv('<rect x="12" y="6" width="40" height="50"/><path d="M32 6v50M28 28v8M36 28v8M16 56v4M48 56v4"/>'),
    sanuzly: sv('<path d="M6 30h52v6a12 12 0 0 1-12 12H18A12 12 0 0 1 6 36z"/><path d="M14 30V12h12M18 48l-3 8M46 48l3 8"/>'),
    'tv-zony': sv('<rect x="8" y="8" width="48" height="30"/><path d="M26 38v4h12v-4M10 46h44v10H10z"/>'),
    ofis: sv('<path d="M6 34h52M10 34v22M54 34v22"/><rect x="21" y="12" width="22" height="16"/><path d="M32 28v6M26 46h12"/>'),
    check: sv('<path d="M12 34l14 14 26-30" stroke-width="3"/>'),
    camera: sv('<rect x="6" y="16" width="52" height="38"/><circle cx="32" cy="35" r="10"/><path d="M22 16l4-8h12l4 8"/>'),
  };

  const root = () => (location.pathname.replace(/[^/]*$/, ''));
  const abs = (page) => new URL(page, location.href).href;

  function header(active) {
    const phone = S.phone ? `<a href="tel:${esc(S.phone.replace(/[^+\d]/g, ''))}">${esc(S.phone)}</a>` : '';
    return `
      <header class="site-header">
        <div class="wrap site-header__in">
          <a class="logo" href="index.html" aria-label="${esc(S.brand)} — на главную"><img src="${active === 'home' ? 'img/logo-light.svg' : 'img/logo.svg'}" alt="${esc(S.brand)}" width="116" height="42"></a>
          <button class="menu-btn" id="menu-btn" aria-label="Меню" aria-expanded="false" aria-controls="nav"><span></span></button>
          <nav class="nav" id="nav" aria-label="Основное меню">
            <a href="works.html" ${active === 'works' ? 'aria-current="page"' : ''}>Наши работы</a>
            <a href="reviews.html" ${active === 'reviews' ? 'aria-current="page"' : ''}>Отзывы</a>
            <a href="quiz.html" ${active === 'quiz' ? 'aria-current="page"' : ''}>Дизайн-проект</a>
            ${phone}
            <a class="btn btn--brass btn--sm" href="reviews.html#leave">Оставить отзыв</a>
          </nav>
        </div>
      </header>`;
  }

  function footer() {
    const contacts = [
      S.phone ? `<li><a href="tel:${esc(S.phone.replace(/[^+\d]/g, ''))}">${esc(S.phone)}</a></li>` : '',
      S.whatsapp ? `<li><a href="${esc(S.whatsapp)}" target="_blank" rel="noopener">WhatsApp</a></li>` : '',
      S.telegram ? `<li><a href="${esc(S.telegram)}" target="_blank" rel="noopener">Telegram</a></li>` : '',
      S.city ? `<li>${esc(S.city)}</li>` : '',
    ].join('');
    return `
      <footer class="site-footer">
        <div class="site-footer__word" aria-hidden="true">ASD</div>
        <div class="wrap site-footer__in">
          <div class="site-footer__grid">
            <div>
              <a class="logo logo--foot" href="index.html" aria-label="${esc(S.brand)} — на главную"><img src="img/logo-light.svg" alt="${esc(S.brand)}" width="150" height="55"></a>
              <p style="margin-top:16px;max-width:34ch">${esc(S.tagline || '')}. Смотрите наши работы и читайте отзывы тех, кто уже живёт с нашей мебелью.</p>
            </div>
            <div><h4>Разделы</h4><ul>
              <li><a href="works.html">Наши работы</a></li>
              <li><a href="reviews.html">Отзывы</a></li>
              <li><a href="quiz.html">Дизайн-проект мебели</a></li>
            </ul></div>
            <div><h4>Связаться</h4><ul>${contacts || '<li>Контакты скоро появятся</li>'}</ul></div>
          </div>
          <div class="site-footer__bottom"><span>© ${new Date().getFullYear()} ${esc(S.brand)}</span>
            <button class="support-btn" type="button" data-support><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z" stroke-linejoin="round"/><path d="M12 9v3M12 14.2v.1" stroke-linecap="round"/></svg>Поддержка сайта</button>
          </div>
        </div>
      </footer>`;
  }

  function toast(msg) {
    let t = document.getElementById('kv-toast');
    if (!t) {
      t = document.createElement('div'); t.id = 'kv-toast'; t.setAttribute('role', 'status');
      t.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(20px);background:#16201C;color:#fff;padding:12px 20px;font-weight:500;z-index:120;opacity:0;transition:all .25s ease;max-width:90vw;border-left:3px solid #B8924A';
      document.body.appendChild(t);
    }
    t.textContent = msg; t.style.opacity = '1'; t.style.transform = 'translateX(-50%) translateY(0)';
    clearTimeout(toast._t); toast._t = setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(-50%) translateY(20px)'; }, 2200);
  }

  async function copyLink(url, btn) {
    try {
      if (navigator.share && /Android|iPhone|iPad/i.test(navigator.userAgent)) { await navigator.share({ url, title: S.brand }); return; }
    } catch (e) { if (e && e.name === 'AbortError') return; }
    try { await navigator.clipboard.writeText(url); }
    catch (e) {
      const ta = document.createElement('textarea'); ta.value = url; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (er) { /* ignore */ } ta.remove();
    }
    toast('Ссылка скопирована');
    if (btn) { const old = btn.textContent; btn.textContent = 'Скопировано'; setTimeout(() => { btn.textContent = old; }, 1800); }
  }

  /* Пачка квадратиков — награда за отправленный отзыв */
  function confetti() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let c = document.getElementById('confetti');
    if (!c) { c = document.createElement('div'); c.id = 'confetti'; c.setAttribute('aria-hidden', 'true'); document.body.appendChild(c); }
    const colors = ['#B8924A', '#DDBF85', '#16201C', '#8C6B2C', '#D9D5CD'];
    const cx = innerWidth / 2, cy = innerHeight * 0.35;
    for (let i = 0; i < 70; i++) {
      const p = document.createElement('i');
      p.style.background = colors[i % colors.length]; if (i % 3 === 0) p.style.height = '3px';
      p.style.left = cx + 'px'; p.style.top = cy + 'px';
      const ang = Math.random() * Math.PI * 2, v = 160 + Math.random() * 360;
      const dx = Math.cos(ang) * v, dy = Math.sin(ang) * v - 120, rot = (Math.random() - .5) * 720;
      p.animate([
        { transform: 'translate(0,0) rotate(0)', opacity: 1 },
        { transform: `translate(${dx}px, ${dy + 420}px) rotate(${rot}deg)`, opacity: 0 },
      ], { duration: 1500 + Math.random() * 900, easing: 'cubic-bezier(.15,.7,.3,1)', fill: 'forwards' });
      c.appendChild(p);
    }
    setTimeout(() => { c.innerHTML = ''; }, 2800);
  }

  function counts() {
    const m = {}; (W.items || []).forEach((i) => { m[i.cat] = (m[i.cat] || 0) + 1; }); return m;
  }
  const photosWord = (n) => `${n} ${plural(n, ['фото', 'фото', 'фото'])}`;


  /* ---------- Поддержка сайта: «сообщить об ошибке» ---------- */
  let lastJsError = '';
  window.addEventListener('error', (e) => { lastJsError = (e.message || 'error') + (e.filename ? ' @ ' + e.filename.split('/').pop() + ':' + e.lineno : ''); });
  window.addEventListener('unhandledrejection', (e) => { lastJsError = 'promise: ' + String((e.reason && e.reason.message) || e.reason || '').slice(0, 200); });

  const KINDS = [['bug', 'Ошибка на сайте'], ['ui', 'Неудобно или криво'], ['idea', 'Предложение'], ['other', 'Другое']];
  function supportDialog() {
    let d = document.getElementById('support');
    if (d) return d;
    d = document.createElement('div'); d.id = 'support'; d.className = 'sup'; d.hidden = true;
    d.innerHTML = `
      <div class="sup__back" data-sup-close></div>
      <div class="sup__box" role="dialog" aria-modal="true" aria-labelledby="sup-t">
        <button class="sup__x" type="button" data-sup-close aria-label="Закрыть">×</button>
        <form id="sup-form" novalidate>
          <h2 id="sup-t">Поддержка сайта</h2>
          <p class="sup__lead">Что-то не работает или выглядит неправильно? Опишите, мы исправим.</p>
          <div class="sup__kinds" role="radiogroup" aria-label="Тип сообщения">
            ${KINDS.map(([v, t], i) => `<label><input type="radio" name="kind" value="${v}" ${i === 0 ? 'checked' : ''}><span>${t}</span></label>`).join('')}
          </div>
          <label class="sup__f"><span>Что случилось</span>
            <textarea id="sup-msg" rows="5" maxlength="2000" placeholder="Например: на странице «Отзывы» не открывается форма, кнопка ничего не делает."></textarea></label>
          <label class="sup__f"><span>Как с вами связаться <em>(необязательно)</em></span>
            <input id="sup-contact" type="text" maxlength="120" autocomplete="off" placeholder="Телефон или Telegram, если нужен ответ"></label>
          <input id="sup-site" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;opacity:0;height:0;width:0">
          <p class="sup__hint">Мы автоматически прикладываем страницу, тип устройства и размер экрана, чтобы быстрее найти причину.</p>
          <div class="sup__err" id="sup-err" role="alert"></div>
          <button class="btn btn--brass sup__send" type="submit">Отправить</button>
        </form>
        <div class="sup__ok" id="sup-ok" hidden>
          <div class="sup__mark">${ICONS.check}</div>
          <h2>Спасибо!</h2>
          <p>Сообщение получено. Мы посмотрим и исправим.</p>
          <button class="btn" type="button" data-sup-close>Закрыть</button>
        </div>
      </div>`;
    document.body.appendChild(d);
    d.addEventListener('click', (e) => { if (e.target.closest('[data-sup-close]')) closeSupport(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !d.hidden) closeSupport(); });
    d.querySelector('#sup-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = d.querySelector('#sup-msg').value.trim(), err = d.querySelector('#sup-err'), btn = d.querySelector('.sup__send');
      const fail = (t) => { err.textContent = t; err.classList.add('is-on'); };
      err.classList.remove('is-on');
      if (msg.length < 5) { fail('Опишите проблему хотя бы парой слов.'); d.querySelector('#sup-msg').focus(); return; }
      if (d.querySelector('#sup-site').value) { showOk(d); return; }       // «ловушка» для роботов
      btn.disabled = true; const old = btn.textContent; btn.textContent = 'Отправляем…';
      try {
        await Api.submitBug({
          kind: d.querySelector('input[name=kind]:checked').value, message: msg, contact: d.querySelector('#sup-contact').value,
          page: location.pathname.replace(/^.*\//, '') + location.search, ua: navigator.userAgent,
          viewport: innerWidth + 'x' + innerHeight + '@' + (window.devicePixelRatio || 1), err: lastJsError,
        });
        showOk(d);
      } catch (er) { fail(er.message || 'Не получилось отправить. Попробуйте ещё раз.'); }
      btn.disabled = false; btn.textContent = old;
    });
    return d;
  }
  function showOk(d) { d.querySelector('#sup-form').hidden = true; d.querySelector('#sup-ok').hidden = false; d.querySelector('#sup-ok .btn').focus(); }
  let supReturn = null;
  function openSupport() {
    const d = supportDialog(); supReturn = document.activeElement;
    d.querySelector('#sup-form').hidden = false; d.querySelector('#sup-ok').hidden = true;
    d.querySelector('#sup-form').reset(); d.querySelector('#sup-err').classList.remove('is-on');
    d.hidden = false; document.documentElement.classList.add('sup-open');
    setTimeout(() => d.querySelector('#sup-msg').focus({ preventScroll: true }), 30);
  }
  function closeSupport() {
    const d = document.getElementById('support'); if (!d) return;
    d.hidden = true; document.documentElement.classList.remove('sup-open');
    if (supReturn && supReturn.focus) supReturn.focus({ preventScroll: true });
  }

  function init(active) {
    const h = document.getElementById('site-header'); if (h) h.innerHTML = header(active);
    const f = document.getElementById('site-footer'); if (f) f.innerHTML = footer();
    const b = document.getElementById('menu-btn'), n = document.getElementById('nav');
    if (b && n) b.addEventListener('click', () => { const o = n.classList.toggle('is-open'); b.setAttribute('aria-expanded', String(o)); });
    document.addEventListener('click', (e) => {
      if (e.target.closest('[data-support]')) { e.preventDefault(); openSupport(); return; }
      const s = e.target.closest('[data-copy]');
      if (s) { e.preventDefault(); copyLink(abs(s.getAttribute('data-copy')), s); }
    });
  }

  return { init, esc, plural, fmtDate, stars, fmtNum, ICONS, copyLink, toast, confetti, openSupport, counts, photosWord, abs, root };
})();
