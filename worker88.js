// ======= My Semi-Pro Panel (KV + Auth + Sources + Outputs) =======
// KV binding: SUBS
// ENV vars: PANEL_PASS, UUID

const KV_SOURCES_KEY = "sources";           // JSON array of strings
const KV_SETTINGS_KEY = "cfg:settings";     // JSON { protos:[], count, format }
const KV_PANEL_PASS = "cfg:panel_pass";     // string
const KV_UUID = "cfg:uuid";                 // string

const DEFAULT_SETTINGS = {
  protos: ["vmess", "vless", "trojan", "ss"],
  count: 500,
  format: "raw" // raw|txt|json|yaml|sub
};

const VALID_PROTOS = ["vmess", "vless", "trojan", "ss"];

function b64encode(str) {
  return btoa(unescape(encodeURIComponent(str)));
}
function b64decode(str) {
  try {
    return decodeURIComponent(escape(atob(str)));
  } catch {
    try { return atob(str); } catch { return ""; }
  }
}

function htmlLogin() {
  return `<!doctype html>
<html lang="fa"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ورود به پنل</title>
<style>
  :root{
    --bg:#0f172a;
    --card:#111827;
    --txt:#e5e7eb;
    --accent:#22d3ee;
    --muted:#9ca3af;
    --danger:#ef4444;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0;background:radial-gradient(1200px 600px at 50% -10%, #0ea5e9 0%, transparent 60%), var(--bg);font-family:ui-sans-serif,system-ui,Segoe UI,Roboto; color:var(--txt)}
  .wrap{min-height:100%;display:flex;align-items:center;justify-content:center;padding:24px}
  .card{width:380px;max-width:94%; background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01)); border:1px solid rgba(255,255,255,.06); backdrop-filter: blur(6px); border-radius:16px;padding:24px;box-shadow:0 30px 120px rgba(0,0,0,.4)}
  h1{margin:0 0 12px;font-size:22px;letter-spacing:.3px}
  p{margin:0 0 14px;color:var(--muted)}
  input{width:100%;padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,.12); background:#0b1220;color:#fff;font-size:15px;outline:none}
  .row{display:flex;gap:10px;margin-top:12px}
  button{flex:1;padding:11px 12px;background:linear-gradient(90deg,#06b6d4,#22d3ee); border:0;border-radius:10px;color:#001018;font-weight:700;cursor:pointer}
  .small{font-size:12px;margin-top:10px;color:var(--muted)}
</style>
</head>
<body>
<div class="wrap">
  <form class="card" method="post" action="/login">
    <h1>⚡ ورود به پنل</h1>
    <p>برای ورود، رمز پنل را وارد کنید.</p>
    <input name="pass" type="password" placeholder="رمز پنل" required />
    <div class="row">
      <button type="submit">ورود</button>
    </div>
    <div class="small">پس از ورود، مدیریت منابع، تنظیمات و خروجی‌ها در دسترس است.</div>
  </form>
</div>
</body>
</html>`;
}

function htmlPanel(hostname){
  const base = `https://${hostname}`;
  return `<!doctype html>
<html lang="fa"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>My Semi-Pro Panel</title>
<style>
  :root{
    --bg:#0f172a;
    --card:#0b1220;
    --txt:#e5e7eb;
    --muted:#9ca3af;
    --accent:#22d3ee;
    --accent2:#a78bfa;
    --danger:#ef4444;
    --ok:#10b981;
  }
  *{box-sizing:border-box}
  body{margin:0;background:radial-gradient(1200px 600px at 50% -10%, #0ea5e9 0%, transparent 60%), var(--bg); font-family:ui-sans-serif,system-ui,Segoe UI,Roboto;color:var(--txt)}
  .container{max-width:1100px;margin:18px auto;padding:0 16px}
  .header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
  .title{font-size:22px;font-weight:800;letter-spacing:.3px}
  .tag{padding:4px 10px;border-radius:999px;background:rgba(255,255,255,.06);color:var(--accent);font-size:12px}
  .grid{display:grid;grid-template-columns:1fr;gap:14px}
  @media(min-width:940px){ .grid{grid-template-columns:1fr 1fr} }
  .card{background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01)); border:1px solid rgba(255,255,255,.06); backdrop-filter: blur(6px); border-radius:14px;padding:16px}
  h2{margin:0 0 10px;font-size:18px}
  .muted{color:var(--muted); font-size:13px}
  textarea,input,select{width:100%;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,.12); background:#0b1220;color:#fff;font-size:14px;outline:none}
  .row{display:flex;gap:10px;flex-wrap:wrap}
  .btn{padding:10px 12px;border:0;border-radius:10px;background:linear-gradient(90deg,#06b6d4,#22d3ee);color:#001018;font-weight:700;cursor:pointer}
  .btn.gray{background:#1f2937;color:#e5e7eb}
  .btn.red{background:#991b1b;color:#fff}
  .btn.ok{background:#065f46;color:#fff}
  .klist{max-height:260px;overflow:auto;border:1px dashed rgba(255,255,255,.1);border-radius:10px;padding:8px}
  .item{padding:6px;border-bottom:1px dashed rgba(255,255,255,.08);word-break:break-all;font-size:12px}
  .badge{display:inline-block;padding:3px 6px;border-radius:999px;background:rgba(255,255,255,.06);font-size:12px;margin-left:6px}
  .out{font-family:monospace;background:#0b1220;padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,.08);word-break:break-all}
  .copy{float:right;font-size:12px;cursor:pointer;color:var(--accent)}
  .note{font-size:12px;color:var(--muted)}
  .tabs{display:flex;gap:10px;margin-top:8px}
  .tab{padding:6px 10px;border-radius:8px;border:1px solid rgba(255,255,255,.12);cursor:pointer}
  .tab.active{background:rgba(255,255,255,.06)}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="title">⚡ My Semi-Pro Panel</div>
    <div class="tag">Worker Host: ${hostname}</div>
    <div class="tag">Subscription: ${base}/sub</div>
  </div>

  <div class="tabs">
    <div class="tab active" data-tab="sources">Sources</div>
    <div class="tab" data-tab="settings">Settings</div>
    <div class="tab" data-tab="outputs">Outputs</div>
  </div>

  <div id="tab-sources" class="card" style="margin-top:10px">
    <h2>📡 Sources</h2>
    <div class="muted">Add/Remove your sub-links or raw config pages. Duplicates are ignored.</div>
    <div style="margin-top:8px">
      <textarea id="addLinks" rows="5" placeholder="Paste vmess://, vless://, trojan://, ss:// or links (txt/json)"></textarea>
      <div class="row" style="margin-top:8px">
        <button class="btn" id="btnAdd">Add</button>
        <button class="btn gray" id="btnClear">Clear All</button>
      </div>
    </div>
    <div style="margin-top:8px">
      <div class="muted">Current Items</div>
      <div id="list" class="klist"></div>
      <div class="row" style="margin-top:8px">
        <input id="delIndices" placeholder="Indices to delete, e.g. 0,2,5"/>
        <button class="btn red" id="btnDeleteSel">Delete Selected</button>
      </div>
      <div class="note">Index starts at 0.</div>
    </div>
  </div>

  <div id="tab-settings" class="card" style="display:none;margin-top:10px">
    <h2>⚙️ Settings</h2>
    <div class="row">
      <div style="flex:1">
        <label>Protocols</label>
        <div class="row" style="margin-top:6px">
          <label><input type="checkbox" class="proto" value="vmess" checked> vmess</label>
          <label><input type="checkbox" class="proto" value="vless" checked> vless</label>
          <label><input type="checkbox" class="proto" value="trojan" checked> trojan</label>
          <label><input type="checkbox" class="proto" value="ss" checked> ss</label>
        </div>
      </div>
      <div style="width:160px">
        <label>Count</label>
        <input id="count" type="number" min="1" max="5000" value="500"/>
      </div>
      <div style="width:180px">
        <label>Default Output</label>
        <select id="format">
          <option value="raw">raw</option>
          <option value="txt">txt</option>
          <option value="json">json</option>
          <option value="yaml">yaml</option>
          <option value="sub">sub (v2rayN)</option>
        </select>
      </div>
    </div>
    <div class="row" style="margin-top:10px">
      <button class="btn ok" id="btnSaveSettings">Save Settings</button>
    </div>
    <div class="note">Settings are stored in KV and used as defaults for output endpoints.</div>

    <div style="margin-top:14px">
      <label>Panel Password (optional)</label>
      <input id="newPass" placeholder="Leave empty = no change"/>
      <label style="margin-top:8px">UUID (optional)</label>
      <input id="newUUID" placeholder="Leave empty = no change"/>
      <div class="row" style="margin-top:10px">
        <button class="btn" id="btnSaveSecrets">Save Password/UUID</button>
      </div>
    </div>
  </div>

  <div id="tab-outputs" class="card" style="display:none;margin-top:10px">
    <h2>🔗 Outputs</h2>
    <div class="muted">Use query params: <code>?proto=vmess,vless&amp;n=500&amp;shuffle=1</code></div>
    <div style="margin-top:8px">
      <div class="out">RAW: <span id="rawUrl">${base}/raw</span> <span class="copy" data-copy="rawUrl">copy</span></div>
      <div class="out" style="margin-top:6px">TXT: <span id="txtUrl">${base}/txt</span> <span class="copy" data-copy="txtUrl">copy</span></div>
      <div class="out" style="margin-top:6px">JSON: <span id="jsonUrl">${base}/json</span> <span class="copy" data-copy="jsonUrl">copy</span></div>
      <div class="out" style="margin-top:6px">YAML: <span id="yamlUrl">${base}/yaml</span> <span class="copy" data-copy="yamlUrl">copy</span></div>
      <div class="out" style="margin-top:6px">SUB (v2rayN): <span id="subUrl">${base}/sub</span> <span class="copy" data-copy="subUrl">copy</span></div>
    </div>
    <div class="note" style="margin-top:6px">Example: <code>${base}/raw?proto=vless,vmess&n=300&shuffle=1</code></div>
  </div>
</div>

<script>
  const $ = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));

  // Tabs
  $$(".tab").forEach(t=>{
    t.addEventListener('click',()=>{
      $$(".tab").forEach(x=>x.classList.remove('active'));
      t.classList.add('active');
      const target = t.dataset.tab;
      $("#tab-sources").style.display = target==="sources"?"block":"none";
      $("#tab-settings").style.display = target==="settings"?"block":"none";
      $("#tab-outputs").style.display = target==="outputs"?"block":"none";
    });
  });

  // Copy buttons
  $$(".copy").forEach(c=>{
    c.addEventListener('click',()=>{
      const id = c.dataset.copy;
      const el = document.getElementById(id);
      if(!el) return;
      navigator.clipboard.writeText(el.textContent.trim());
      c.textContent = "copied!";
      setTimeout(()=>c.textContent="copy",800);
    });
  });

  // Load sources
  async function loadSources(){
    const r = await fetch('/api/sources');
    const js = await r.json();
    const list = $("#list");
    list.innerHTML = "";
    if(!js.items || !js.items.length){
      list.innerHTML = "<div class='muted'>No sources added.</div>";
      return;
    }
    js.items.forEach((s,idx)=>{
      const div = document.createElement('div');
      div.className="item";
      div.textContent = "#"+idx+"  " + s;
      list.appendChild(div);
    });
  }

  // Add links
  $("#btnAdd").addEventListener('click', async ()=>{
    const txt = $("#addLinks").value;
    if(!txt.trim()) return;
    const r = await fetch('/api/sources',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({add:txt})});
    $("#addLinks").value="";
    await loadSources();
  });

  // Clear all
  $("#btnClear").addEventListener('click', async ()=>{
    await fetch('/api/sources',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({clear:true})});
    await loadSources();
  });

  // Delete selected
  $("#btnDeleteSel").addEventListener('click', async ()=>{
    const raw = $("#delIndices").value;
    if(!raw.trim()) return;
    const arr = raw.split(",").map(x=>parseInt(x.trim(),10)).filter(x=>!isNaN(x));
    if(!arr.length) return;
    await fetch('/api/sources',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({delete:arr})});
    $("#delIndices").value="";
    await loadSources();
  });

  // Load settings
  async function loadSettings(){
    const r = await fetch('/api/settings');
    const js = await r.json();
    // protocols
    $$(".proto").forEach(cb=>{
      cb.checked = (js.protos||[]).includes(cb.value);
    });
    $("#count").value = js.count || 500;
    $("#format").value = js.format || "raw";
  }

  $("#btnSaveSettings").addEventListener('click', async ()=>{
    const protos = $$(".proto").filter(cb=>cb.checked).map(cb=>cb.value);
    const count = parseInt($("#count").value,10) || 500;
    const format = $("#format").value;
    await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({protos,count,format})});
    alert("Saved.");
  });

  $("#btnSaveSecrets").addEventListener('click', async ()=>{
    const pass = $("#newPass").value.trim();
    const uuid = $("#newUUID").value.trim();
    if(!pass && !uuid){ alert("Nothing to update."); return; }
    await fetch('/api/secrets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pass,uuid})});
    $("#newPass").value=""; $("#newUUID").value="";
    alert("Saved. (Password/UUID)");
  });

  loadSources();
  loadSettings();
</script>
</body></html>`;
}

// ---------- Helpers ----------
async function getPanelPass(env) {
  const fromKV = await env.SUBS.get(KV_PANEL_PASS);
  if (fromKV) return fromKV;
  return env.PANEL_PASS || "12345678";
}
async function getUUID(env) {
  const fromKV = await env.SUBS.get(KV_UUID);
  if (fromKV) return fromKV;
  return env.UUID || "";
}

async function getSources(env) {
  const s = await env.SUBS.get(KV_SOURCES_KEY);
  if (!s) return [];
  try {
    const arr = JSON.parse(s);
    return Array.isArray(arr) ? arr : [];
  } catch { return []; }
}
async function setSources(env, arr) {
  await env.SUBS.put(KV_SOURCES_KEY, JSON.stringify(arr));
}

async function getSettings(env) {
  const s = await env.SUBS.get(KV_SETTINGS_KEY);
  if (!s) return DEFAULT_SETTINGS;
  try {
    const js = JSON.parse(s);
    // sanity
    const out = { ...DEFAULT_SETTINGS, ...js };
    out.protos = (out.protos || []).filter(p=>VALID_PROTOS.includes(p));
    if(!out.protos.length) out.protos = DEFAULT_SETTINGS.protos;
    out.count = Math.min(Math.max(parseInt(out.count||500,10),1),5000);
    out.format = ["raw","txt","json","yaml","sub"].includes(out.format) ? out.format : "raw";
    return out;
  } catch {
    return DEFAULT_SETTINGS;
  }
}
async function setSettings(env, js) {
  await env.SUBS.put(KV_SETTINGS_KEY, JSON.stringify(js));
}

function setCookie(name,value,maxAge=3600){
  return `${name}=${value}; Path=/; HttpOnly; Max-Age=${maxAge}; SameSite=Lax`;
}
function getCookie(req,name){
  const c = req.headers.get("Cookie")||"";
  const m = c.match(new RegExp('(^|; )'+name+'=([^;]+)'));
  return m ? m[2] : null;
}

function extractLinksFromText(text){
  const out = new Set();
  const re = /(vmess|vless|trojan|ss):\/\/[^\s"']+/gi;
  let m;
  while ((m = re.exec(text)) !== null) {
    out.add(m[0].trim());
  }
  return Array.from(out);
}
function extractFromJSON(text){
  try {
    const obj = JSON.parse(text);
    const acc = new Set();
    const walk = (v)=>{
      if (typeof v === "string"){
        extractLinksFromText(v).forEach(x=>acc.add(x));
      } else if (Array.isArray(v)) {
        v.forEach(walk);
      } else if (v && typeof v === "object") {
        Object.values(v).forEach(walk);
      }
    };
    walk(obj);
    return Array.from(acc);
  } catch {
    return [];
  }
}
function maybeDecodeBase64AndExtract(text){
  const s = text.trim();
  // require not too big and without spaces
  if (!s || /\s/.test(s) || s.length<20) return [];
  const dec = b64decode(s);
  if (!dec) return [];
  return extractLinksFromText(dec);
}

function filterByProtos(links,protos){
  return links.filter(l=>{
    const low = l.toLowerCase();
    return protos.some(p=>low.startsWith(p+"://"));
  });
}
function dedupe(arr) {
  const set = new Set();
  const out = [];
  for(const x of arr) {
    const k = x.trim();
    if(!k) continue;
    if(!set.has(k)){
      set.add(k);
      out.push(x);
    }
  }
  return out;
}
function shuffleInPlace(arr){
  for (let i=arr.length-1; i>0; i--){
    const j = Math.floor(Math.random()*(i+1));
    [arr[i],arr[j]] = [arr[j],arr[i]];
  }
  return arr;
}

async function fetchAllLinks(env, sources){
  const out = [];
  const tasks = sources.map(async (u)=>{
    try{
      const res = await fetch(u, { cf: { cacheTtl: 0 } });
      if(!res.ok) return;
      const text = await res.text();
      // direct parse
      extractLinksFromText(text).forEach(x=>out.push(x));
      // try JSON
      extractFromJSON(text).forEach(x=>out.push(x));
      // try base64 subscription decode
      maybeDecodeBase64AndExtract(text).forEach(x=>out.push(x));
    } catch {}
  });
  await Promise.all(tasks);
  return dedupe(out);
}

function toYAMLList(links){
  // minimal YAML for list of links
  let s = "proxies:\n";
  for(const l of links){
    s += `  - ${l}\n`;
  }
  return s;
}

// ---------- Router ----------
export default {
  async fetch(req, env) {
    try{
      const url = new URL(req.url);
      const path = url.pathname;

      // Auth check
      const authed = getCookie(req,"auth") === "1";
      const method = req.method.toUpperCase();

      // Login
      if (path === "/login" && method === "GET") {
        if (authed) return Response.redirect("/panel", 302);
        return new Response(htmlLogin(), { headers: { "Content-Type":"text/html; charset=utf-8" }});
      }
      if (path === "/login" && method === "POST") {
        const body = await req.formData();
        const pass = (body.get("pass")||"").trim();
        const real = await getPanelPass(env);
        if (pass && pass === real) {
          return new Response("", { status:302, headers: { "Location":"/panel", "Set-Cookie": setCookie("auth","1", 3600*12) }});
        } else {
          return new Response(htmlLogin(), { headers: { "Content-Type":"text/html; charset=utf-8" }, status:401 });
        }
      }

      // Panel
      if (path === "/" || path === "/panel") {
        if (!authed) return Response.redirect("/login", 302);
        return new Response(htmlPanel(url.hostname), { headers: { "Content-Type":"text/html; charset=utf-8" }});
      }

      // API: sources
      if (path === "/api/sources") {
        if (!authed) return new Response("Unauthorized", { status:401 });
        if (method === "GET") {
          const items = await getSources(env);
          return new Response(JSON.stringify({items}), { headers: { "Content-Type":"application/json" }});
        }
        if (method === "POST") {
          const js = await req.json().catch(()=>({}));
          let items = await getSources(env);
          if (js.clear) {
            items = [];
          }
          if (Array.isArray(js.delete) && js.delete.length) {
            const del = new Set(js.delete.filter(x=>Number.isInteger(x)));
            items = items.filter((_,i)=>!del.has(i));
          }
          if (js.add) {
            const adds = String(js.add).split(/\r?\n/).map(x=>x.trim()).filter(Boolean);
            for(const a of adds) {
              if (!items.includes(a)) items.push(a);
            }
          }
          await setSources(env, items);
          return new Response(JSON.stringify({ok:true,count:items.length}), { headers: { "Content-Type":"application/json" }});
        }
      }

      // API: settings
      if (path === "/api/settings") {
        if (!authed) return new Response("Unauthorized", { status:401 });
        if (method === "GET") {
          const st = await getSettings(env);
          return new Response(JSON.stringify(st), { headers: { "Content-Type":"application/json" }});
        }
        if (method === "POST") {
          const js = await req.json().catch(()=>({}));
          const current = await getSettings(env);
          const next = { ...current };
          if (Array.isArray(js.protos)) {
            next.protos = js.protos.filter(p=>["vmess","vless","trojan","ss"].includes(p));
            if (!next.protos.length) next.protos = current.protos;
          }
          if (js.count) {
            const n = parseInt(js.count,10);
            if (!isNaN(n)) next.count = Math.min(Math.max(n,1),5000);
          }
          if (js.format && ["raw","txt","json","yaml","sub"].includes(js.format)) {
            next.format = js.format;
          }
          await setSettings(env, next);
          return new Response(JSON.stringify({ok:true,settings:next}), { headers: { "Content-Type":"application/json" }});
        }
      }

      // API: secrets (pass/uuid)
      if (path === "/api/secrets" && method === "POST") {
        if (!authed) return new Response("Unauthorized", { status:401 });
        const js = await req.json().catch(()=>({}));
        if (js.pass && String(js.pass).trim()) {
          await env.SUBS.put(KV_PANEL_PASS, String(js.pass).trim());
        }
        if (js.uuid && String(js.uuid).trim()) {
          await env.SUBS.put(KV_UUID, String(js.uuid).trim());
        }
        return new Response(JSON.stringify({ok:true}), { headers: { "Content-Type":"application/json" }});
      }

      // Outputs
      if (["/raw","/txt","/json","/yaml","/sub"].includes(path)) {
        // defaults from KV settings
        const st = await getSettings(env);
        // query overrides
        let protos = st.protos.slice();
        const qp = url.searchParams.get("proto");
        if (qp) {
          const cand = qp.split(",").map(s=>s.trim().toLowerCase()).filter(Boolean);
          const good = cand.filter(p=>VALID_PROTOS.includes(p));
          if (good.length) protos = good;
        }
        let n = st.count;
        const qn = parseInt(url.searchParams.get("n")||"",10);
        if (!isNaN(qn) && qn>0) n = Math.min(qn, 5000);
        const shuffle = url.searchParams.get("shuffle") === "1";

        const sources = await getSources(env);
        // aggregate
        let links = await fetchAllLinks(env, sources);
        links = filterByProtos(links, protos);
        if (shuffle) shuffleInPlace(links);
        if (n && links.length>n) links = links.slice(0,n);

        if (path === "/raw" || path === "/txt") {
          return new Response(links.join("\n"), { headers: { "Content-Type":"text/plain; charset=utf-8" }});
        }
        if (path === "/json") {
          return new Response(JSON.stringify({ count:links.length, items:links }), { headers: { "Content-Type":"application/json" }});
        }
        if (path === "/yaml") {
          return new Response(toYAMLList(links), { headers: { "Content-Type":"text/yaml; charset=utf-8" }});
        }
        if (path === "/sub") {
          // v2rayN subscription = Base64 of "link1\nlink2\n..."
          const raw = links.join("\n");
          const b64 = b64encode(raw);
          return new Response(b64, { headers: { "Content-Type":"text/plain; charset=utf-8" }});
        }
      }

      // Unknown
      if (path === "/uuid") {
        const id = await getUUID(env);
        return new Response(id, { headers: { "Content-Type":"text/plain; charset=utf-8" }});
      }

      return new Response("Not found", { status:404 });
    } catch(e) {
      return new Response("Server error: " + (e && e.message ? e.message : String(e)), { status:500 });
    }
  }
}; 
