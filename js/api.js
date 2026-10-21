/* ============================================================
   Api — работа с отзывами.
   Если в config.js заданы ключи Supabase — отзывы хранятся там
   (общие для всех посетителей). Иначе включается демо-режим:
   данные лежат только в браузере.
   ============================================================ */
const Api = (() => {
  const S = window.SITE || {};
  const configured = !!(S.supabaseUrl && S.supabaseAnonKey);
  const base = (S.supabaseUrl || '').replace(/\/+$/, '');

  const LS = {
    get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignore */ } },
  };

  /* ---------- Идентификатор устройства ----------
     Хранится в трёх местах сразу (localStorage, cookie, IndexedDB):
     если очищено одно — восстанавливается из другого. */
  const DEV_KEY = 'kv_device';
  const uuid = () => (crypto.randomUUID ? crypto.randomUUID() : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0; return (c === 'x' ? r : (r & 3) | 8).toString(16);
  }));
  const readCookie = () => { const m = document.cookie.match(new RegExp('(?:^|; )' + DEV_KEY + '=([^;]+)')); return m ? m[1] : null; };
  const writeCookie = (v) => { try { document.cookie = DEV_KEY + '=' + v + '; max-age=63072000; path=/; SameSite=Lax'; } catch (e) { /* ignore */ } };
  function idb(mode, value) {
    return new Promise((resolve) => {
      try {
        const open = indexedDB.open('kv', 1);
        open.onupgradeneeded = () => open.result.createObjectStore('s');
        open.onerror = () => resolve(null);
        open.onsuccess = () => {
          try {
            const tx = open.result.transaction('s', mode === 'set' ? 'readwrite' : 'readonly');
            const st = tx.objectStore('s');
            if (mode === 'set') { st.put(value, DEV_KEY); tx.oncomplete = () => resolve(value); }
            else { const r = st.get(DEV_KEY); r.onsuccess = () => resolve(r.result || null); r.onerror = () => resolve(null); }
          } catch (e) { resolve(null); }
        };
      } catch (e) { resolve(null); }
    });
  }

  let devPromise = null;
  function deviceId() {
    if (!devPromise) {
      devPromise = (async () => {
        let id = LS.get(DEV_KEY, null) || readCookie() || await idb('get');
        if (!id || !/^[a-f0-9-]{20,64}$/.test(id)) id = uuid();
        LS.set(DEV_KEY, id); writeCookie(id); idb('set', id);
        return id;
      })();
    }
    return devPromise;
  }

  async function sha256(text) {
    try {
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
      return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
    } catch (e) {
      let h = 5381; for (let i = 0; i < text.length; i++) h = ((h << 5) + h + text.charCodeAt(i)) | 0;
      return 'f' + (h >>> 0).toString(16);
    }
  }
  /* «Мягкий» отпечаток: нужен только администратору, чтобы заметить повторы. Блокировку не выполняет. */
  async function fingerprint() {
    const n = navigator;
    const raw = [n.userAgent, n.language, n.hardwareConcurrency, screen.width + 'x' + screen.height, screen.colorDepth,
      Intl.DateTimeFormat().resolvedOptions().timeZone].join('|');
    return sha256(raw);
  }

  /* ---------- Демо-режим ---------- */
  const SAMPLE = [
    { id: 's1', name: 'Анна', topic: 'kuhni', rating: 5, body: 'Пример отзыва: здесь будет текст клиента о кухне — что понравилось, как прошли замеры и установка.', created_at: '2026-10-10T10:00:00Z', sample: true },
    { id: 's2', name: 'Дмитрий', topic: 'shkafy', rating: 5, body: 'Пример отзыва: так будет выглядеть отзыв о шкафе-купе. Настоящие отзывы появятся после подключения хранилища.', created_at: '2026-10-07T10:00:00Z', sample: true },
    { id: 's3', name: 'Екатерина', topic: 'sanuzly', rating: 5, body: 'Пример отзыва: пара слов о том, как всё прошло. Этот текст — образец оформления, он исчезнет сам.', created_at: '2026-10-03T10:00:00Z', sample: true },
  ];

  /* ---------- Запросы к Supabase ---------- */
  function headers(token, extra) {
    return Object.assign({ apikey: S.supabaseAnonKey, Authorization: 'Bearer ' + (token || S.supabaseAnonKey), 'Content-Type': 'application/json' }, extra || {});
  }
  async function rest(path, opts, token) {
    let res;
    try { res = await fetch(base + path, Object.assign({}, opts, { headers: headers(token, opts && opts.headers) })); }
    catch (e) { const err = new Error('Нет соединения. Проверьте интернет и попробуйте ещё раз.'); err.code = 'network'; throw err; }
    let data = null;
    const text = await res.text();
    try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
    if (!res.ok) {
      const err = new Error((data && (data.message || data.error_description || data.msg)) || ('Ошибка ' + res.status));
      err.status = res.status; err.code = data && data.code; throw err;
    }
    return data;
  }

  /* ---------- Публичные методы ---------- */
  async function listReviews() {
    if (!configured) {
      const mine = LS.get('kv_demo', []);
      return SAMPLE.concat(mine).sort((a, b) => b.created_at.localeCompare(a.created_at));
    }
    return rest('/rest/v1/public_reviews?select=id,created_at,name,topic,rating,body&order=created_at.desc&limit=500');
  }

  /* 'none' | 'pending' | 'approved' | 'hidden' */
  async function myStatus() {
    const local = LS.get('kv_reviewed', null);
    if (!configured) return local ? 'approved' : 'none';
    const id = await deviceId();
    try {
      const r = await rest('/rest/v1/rpc/my_review_status', { method: 'POST', body: JSON.stringify({ dev: id }) });
      if (r && r !== 'none') { LS.set('kv_reviewed', { at: Date.now(), status: r }); return r; }
      if (local && !r) return 'none';
      return r || 'none';
    } catch (e) {
      return local ? (local.status || 'pending') : 'none';
    }
  }

  async function submitReview(r) {
    const payload = {
      name: String(r.name || '').trim(), topic: r.topic || null,
      rating: Number(r.rating), body: String(r.body || '').trim(),
    };
    if (!configured) {
      const item = Object.assign({ id: 'd' + Date.now(), created_at: new Date().toISOString(), sample: false }, payload);
      if (LS.get('kv_reviewed', null)) { const e = new Error('duplicate'); e.code = 'duplicate'; throw e; }
      const list = LS.get('kv_demo', []); list.push(item); LS.set('kv_demo', list);
      LS.set('kv_reviewed', { at: Date.now(), status: 'approved' });
      return item;
    }
    const [dev, fp] = await Promise.all([deviceId(), fingerprint()]);
    try {
      await rest('/rest/v1/reviews', {
        method: 'POST', headers: { Prefer: 'return=minimal' },
        body: JSON.stringify(Object.assign({}, payload, { device_id: dev, fp })),
      });
    } catch (e) {
      if (e.status === 409 || e.code === '23505') { LS.set('kv_reviewed', { at: Date.now(), status: 'pending' }); const d = new Error('duplicate'); d.code = 'duplicate'; throw d; }
      if (/слишком много|too many|flood/i.test(e.message)) { const d = new Error('Сейчас очень много отзывов. Попробуйте через несколько минут.'); throw d; }
      throw e;
    }
    LS.set('kv_reviewed', { at: Date.now(), status: 'pending' });
    return payload;
  }

  /* ---------- Администратор ---------- */
  const AT = 'kv_admin_token';
  function adminToken() {
    try { const t = JSON.parse(sessionStorage.getItem(AT)); return t && t.exp > Date.now() ? t.token : null; } catch (e) { return null; }
  }
  async function adminLogin(email, password) {
    if (!configured) { const e = new Error('Сначала подключите Supabase (см. README.md).'); throw e; }
    const r = await rest('/auth/v1/token?grant_type=password', { method: 'POST', body: JSON.stringify({ email, password }) });
    try { sessionStorage.setItem(AT, JSON.stringify({ token: r.access_token, exp: Date.now() + (r.expires_in - 60) * 1000 })); } catch (e) { /* ignore */ }
    return true;
  }
  function adminLogout() { try { sessionStorage.removeItem(AT); } catch (e) { /* ignore */ } }
  async function adminList(status) {
    const t = adminToken(); if (!t) { const e = new Error('auth'); e.code = 'auth'; throw e; }
    const q = status ? '&status=eq.' + status : '';
    try { return await rest('/rest/v1/reviews?select=*&order=created_at.desc&limit=500' + q, {}, t); }
    catch (e) { if (e.status === 401) e.code = 'auth'; throw e; }
  }
  async function adminSet(id, status) {
    return rest('/rest/v1/reviews?id=eq.' + encodeURIComponent(id), { method: 'PATCH', headers: { Prefer: 'return=minimal' }, body: JSON.stringify({ status }) }, adminToken());
  }
  async function adminDelete(id) {
    return rest('/rest/v1/reviews?id=eq.' + encodeURIComponent(id), { method: 'DELETE', headers: { Prefer: 'return=minimal' } }, adminToken());
  }

  /* ---------- Заявки из опросника ---------- */
  const BUCKET = 'lead-files';
  const MAX_FILES = 8, MAX_BYTES = 10 * 1024 * 1024;

  /* Фото сжимаем в браузере (до 2000 px, JPEG): быстрее грузится и не занимает место в хранилище. PDF и HEIC уходят как есть. */
  async function prepareFile(file) {
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return { blob: file, type: file.type || 'application/octet-stream', ext: (file.name.match(/\.([A-Za-z0-9]{2,5})$/) || [, 'bin'])[1].toLowerCase() };
    try {
      const bmp = await createImageBitmap(file);
      const k = Math.min(1, 2000 / Math.max(bmp.width, bmp.height));
      const w = Math.round(bmp.width * k), h = Math.round(bmp.height * k);
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); g.drawImage(bmp, 0, 0, w, h);
      const blob = await new Promise((res) => c.toBlob(res, 'image/jpeg', 0.84));
      if (blob && blob.size < file.size) return { blob, type: 'image/jpeg', ext: 'jpg' };
    } catch (e) { /* отправим оригинал */ }
    return { blob: file, type: file.type, ext: file.type === 'image/png' ? 'png' : file.type === 'image/webp' ? 'webp' : 'jpg' };
  }
  async function uploadOne(path, blob, type) {
    let res;
    try {
      res = await fetch(base + '/storage/v1/object/' + BUCKET + '/' + path, {
        method: 'POST', body: blob,
        headers: { apikey: S.supabaseAnonKey, Authorization: 'Bearer ' + S.supabaseAnonKey, 'Content-Type': type, 'x-upsert': 'false' },
      });
    } catch (e) { const err = new Error('Нет соединения. Проверьте интернет и попробуйте ещё раз.'); err.code = 'network'; throw err; }
    if (!res.ok) {
      let m = ''; try { m = (await res.json()).message || ''; } catch (e) { /* ignore */ }
      throw new Error(/exceed|size|too large/i.test(m) ? 'Файл слишком большой (максимум 10 МБ).' : 'Не удалось загрузить файл. ' + m);
    }
  }

  /* lead: { items[], itemsOther, stage, plan, name, phone, comment, files: File[] }, onProgress(done,total) */
  async function submitLead(lead, onProgress) {
    const id = uuid();
    const payload = {
      id, items: lead.items, items_other: lead.itemsOther || null, stage: lead.stage, plan: lead.plan,
      name: String(lead.name || '').trim(), phone: String(lead.phone || '').trim(),
      comment: String(lead.comment || '').trim() || null, files: [],
    };
    if (!configured) {
      payload.created_at = new Date().toISOString(); payload.status = 'new';
      payload.files = (lead.files || []).map((f) => ({ name: f.name, size: f.size, type: f.type }));
      const list = LS.get('kv_leads_demo', []); list.push(payload); LS.set('kv_leads_demo', list);
      return payload;
    }
    const files = (lead.files || []).slice(0, MAX_FILES);
    for (let i = 0; i < files.length; i++) {
      const f = files[i];
      if (f.size > 40 * 1024 * 1024) throw new Error('Файл «' + f.name + '» слишком большой.');
      const pr = await prepareFile(f);
      if (pr.blob.size > MAX_BYTES) throw new Error('Файл «' + f.name + '» больше 10 МБ. Уменьшите его или выберите другой.');
      const path = id + '/' + (i + 1) + '-file.' + pr.ext.replace(/[^a-z0-9]/g, '').slice(0, 5);
      await uploadOne(path, pr.blob, pr.type);
      payload.files.push({ path, name: f.name.slice(0, 120), size: pr.blob.size, type: pr.type });
      if (onProgress) onProgress(i + 1, files.length);
    }
    try {
      await rest('/rest/v1/leads', { method: 'POST', headers: { Prefer: 'return=minimal' }, body: JSON.stringify(payload) });
    } catch (e) {
      if (/too many|flood/i.test(e.message)) throw new Error('Сейчас очень много заявок. Попробуйте через несколько минут.');
      throw e;
    }
    return payload;
  }

  async function adminLeads() {
    const t = adminToken(); if (!t) { const e = new Error('auth'); e.code = 'auth'; throw e; }
    try { return await rest('/rest/v1/leads?select=*&order=created_at.desc&limit=500', {}, t); }
    catch (e) { if (e.status === 401) e.code = 'auth'; throw e; }
  }
  async function adminLeadPatch(id, patch) {
    return rest('/rest/v1/leads?id=eq.' + encodeURIComponent(id), { method: 'PATCH', headers: { Prefer: 'return=minimal' }, body: JSON.stringify(patch) }, adminToken());
  }
  async function adminLeadDelete(lead) {
    const t = adminToken();
    const paths = (lead.files || []).map((f) => f.path).filter(Boolean);
    if (paths.length) {
      try { await rest('/storage/v1/object/' + BUCKET, { method: 'DELETE', body: JSON.stringify({ prefixes: paths }) }, t); } catch (e) { /* файлы можно убрать и вручную */ }
    }
    return rest('/rest/v1/leads?id=eq.' + encodeURIComponent(lead.id), { method: 'DELETE', headers: { Prefer: 'return=minimal' } }, t);
  }
  /* временные ссылки (на 2 часа) для просмотра файлов заявки */
  async function adminSignFiles(paths) {
    if (!paths.length) return {};
    const r = await rest('/storage/v1/object/sign/' + BUCKET, { method: 'POST', body: JSON.stringify({ expiresIn: 7200, paths }) }, adminToken());
    const out = {};
    (r || []).forEach((x) => { if (x && x.signedURL) out[x.path || x.signedURL] = base + '/storage/v1' + x.signedURL; });
    return out;
  }

  return {
    configured, listReviews, myStatus, submitReview, deviceId,
    adminToken, adminLogin, adminLogout, adminList, adminSet, adminDelete,
    submitLead, MAX_FILES, MAX_BYTES, adminLeads, adminLeadPatch, adminLeadDelete, adminSignFiles,
  };
})();
