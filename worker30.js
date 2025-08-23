// ======= Advanced Semi-Pro Panel (KV + Auth + Sources + Settings + Outputs) =======
// KV binding: SUBS
// ENV vars: PANEL_PASS, UUID

const KV_SOURCES_KEY = "sources";           // JSON array of strings
const KV_SETTINGS_KEY = "cfg:settings";     // JSON { protos:[], count, format, fragment }
const KV_PANEL_PASS = "cfg:panel_pass";     // string
const KV_UUID = "cfg:uuid";                 // string

const DEFAULT_SETTINGS = {
  protos: ["vmess", "vless", "trojan", "ss"],
  count: 500,
  format: "raw", // raw|txt|json|yaml|sub
  fragment: ""
};

const VALID_PROTOS = ["vmess", "vless", "trojan", "ss"];

function b64encode(str){ return btoa(unescape(encodeURIComponent(str))); }
function b64decode(str){ try{return decodeURIComponent(escape(atob(str)))}catch{return""} }

function htmlLogin(){
  return `<!doctype html>
<html lang="fa"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ورود به پنل</title>
<style>
  :root{--bg:#0f172a;--card:#111827;--txt:#e5e7eb;--accent:#22d3ee;--muted:#9ca3af}
  html,body{height:100%;margin:0;background:var(--bg);font-family:ui-sans-serif,system-ui;color:var(--txt)}
  .wrap{height:100%;display:flex;align-items:center;justify-content:center}
  .card{width:380px;background:var(--card);border-radius:16px;padding:24px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
  h1{margin:0 0 12px;font-size:22px}
  p{margin:0 0 14px;color:var(--muted)}
  input{width:100%;padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#0b1220;color:#fff;font-size:15px;outline:none}
  button{width:100%;padding:11px;background:linear-gradient(90deg,#06b6d4,#22d3ee);border:0;border-radius:10px;color:#001018;font-weight:700;cursor:pointer}
</style>
</head>
<body>
<div class="wrap">
  <form class="card" method="post" action="/login">
    <h1>⚡ ورود به پنل</h1>
    <p>رمز پنل را وارد کنید.</p>
    <input name="pass" type="password" placeholder="رمز پنل" required/>
    <div style="margin-top:12px">
      <button type="submit">ورود</button>
    </div>
  </form>
</div>
</body></html>`;
}

function htmlPanel(hostname, settings, sources){
  const base = `https://${hostname}`;
  const sourcesHTML = sources.length ? sources.map((s,i)=>`<div class="item">#${i} ${s}</div>`).join('') : `<div class="muted">هیچ منبعی اضافه نشده.</div>`;
  return `<!doctype html>
<html lang="fa"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Advanced Semi-Pro Panel</title>
<style>
:root{--bg:#0f172a;--card:#0b1220;--txt:#e5e7eb;--muted:#9ca3af;--accent:#22d3ee;--ok:#10b981;--danger:#ef4444}
body{margin:0;background:var(--bg);font-family:ui-sans-serif,system-ui;color:var(--txt)}
.container{max-width:1100px;margin:18px auto;padding:0 16px}
.header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.title{font-size:22px;font-weight:800}
.grid{display:grid;grid-template-columns:1fr;gap:14px}
@media(min-width:940px){.grid{grid-template-columns:1fr 1fr}}
.card{background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01));border:1px solid rgba(255,255,255,.06);backdrop-filter: blur(6px);border-radius:14px;padding:16px}
h2{margin:0 0 10px;font-size:18px}
textarea,input,select{width:100%;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:#0b1220;color:#fff;font-size:14px;outline:none}
.row{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
.btn{padding:10px 12px;border:0;border-radius:10px;background:linear-gradient(90deg,#06b6d4,#22d3ee);color:#001018;font-weight:700;cursor:pointer}
.btn.gray{background:#1f2937;color:#e5e7eb}
.btn.red{background:#991b1b;color:#fff}
.btn.ok{background:#065f46;color:#fff}
.klist{max-height:260px;overflow:auto;border:1px dashed rgba(255,255,255,.1);border-radius:10px;padding:8px}
.item{padding:6px;border-bottom:1px dashed rgba(255,255,255,.08);word-break:break-all;font-size:12px}
.out{font-family:monospace;background:#0b1220;padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,.08);word-break:break-all}
.copy{float:right;font-size:12px;cursor:pointer;color:var(--accent)}
.muted{color:var(--muted);font-size:13px}
</style>
</head>
<body>
<div class="container">
  <div class="header"><div class="title">⚡ Advanced Semi-Pro Panel</div></div>

  <div class="card">
    <h2>📡 مدیریت منابع</h2>
    <textarea id="addLinks" rows="5" placeholder="Paste vmess://,vless://,trojan://,ss:// or URLs"></textarea>
    <div class="row">
      <button class="btn" id="btnAdd">افزودن/بروزرسانی</button>
      <button class="btn gray" id="btnClear">پاک کردن همه</button>
    </div>
    <div class="klist" id="list">${sourcesHTML}</div>
  </div>

  <div class="card">
    <h2>⚙️ تنظیمات پیشرفته</h2>
    <label>پروتکل‌ها:</label>
    <div class="row">
      ${VALID_PROTOS.map(p=>`<label><input type="checkbox" class="proto" value="${p}" ${settings.protos.includes(p)?"checked":""}> ${p}</label>`).join('')}
    </div>
    <div class="row">
      <label>تعداد خروجی:</label>
      <input id="count" type="number" min="1" max="5000" value="${settings.count}">
    </div>
    <div class="row">
      <label>فرمت خروجی:</label>
      <select id="format">
        <option value="raw" ${settings.format==="raw"?"selected":""}>raw</option>
        <option value="txt" ${settings.format==="txt"?"selected":""}>txt</option>
        <option value="json" ${settings.format==="json"?"selected":""}>json</option>
        <option value="yaml" ${settings.format==="yaml"?"selected":""}>yaml</option>
        <option value="sub" ${settings.format==="sub"?"selected":""}>sub</option>
      </select>
    </div>
    <div class="row">
      <label>Fragment دلخواه:</label>
      <input id="fragment" type="text" placeholder="اختیاری" value="${settings.fragment}">
    </div>
    <div class="row">
      <button class="btn ok" id="btnSaveSettings">ذخیره تنظیمات</button>
    </div>
  </div>

  <div class="card">
    <h2>🔗 خروجی Subscriptions</h2>
    <div class="out">Raw: <span id="rawUrl">${base}/sub?format=raw</span> <span class="copy" data-copy="rawUrl">copy</span></div>
    <div class="out">TXT: <span id="txtUrl">${base}/sub?format=txt</span> <span class="copy" data-copy="txtUrl">copy</span></div>
    <div class="out">JSON: <span id="jsonUrl">${base}/sub?format=json</span> <span class="copy" data-copy="jsonUrl">copy</span></div>
    <div class="out">YAML: <span id="yamlUrl">${base}/sub?format=yaml</span> <span class="copy" data-copy="yamlUrl">copy</span></div>
    <div class="out">SUB: <span id="subUrl">${base}/sub?format=sub</span> <span class="copy" data-copy="subUrl">copy</span></div>
  </div>
</div>

<script>
const $=s=>document.querySelector(s);
const $$=s=>Array.from(document.querySelectorAll(s));

$$(".copy").forEach(c=>{
  c.addEventListener("click",()=>{
    const id=c.dataset.copy;
    navigator.clipboard.writeText($("#"+id).textContent.trim());
    c.textContent="copied!"; setTimeout(()=>c.textContent="copy",800);
  });
});

// Add/Update sources
$("#btnAdd").addEventListener("click",async e=>{
  e.preventDefault();
  const txt=$("#addLinks").value;
  if(!txt.trim()) return;
  await fetch("/api/sources",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({add:txt})});
  $("#addLinks").value="";
  loadSources();
});
$("#btnClear").addEventListener("click",async ()=>{
  await fetch("/api/sources",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({clear:true})});
  loadSources();
});

async function loadSources(){
  const r=await fetch("/api/sources");
  const js=await r.json();
  const list=$("#list");
  list.innerHTML="";
  if(!js.items.length){ list.innerHTML="<div class='muted'>هیچ منبعی اضافه نشده.</div>"; return; }
  js.items.forEach((s,i)=>{
    const div=document.createElement("div"); div.className="item"; div.textContent="#"+i+" "+s; list.appendChild(div);
  });
}

// Load settings
async function loadSettings(){
  const r=await fetch("/api/settings");
  const js=await r.json();
  $$(".proto").forEach(cb=>cb.checked=js.protos.includes(cb.value));
  $("#count").value=js.count;
  $("#format").value=js.format;
  $("#fragment").value=js.fragment;
}
$("#btnSaveSettings").addEventListener
