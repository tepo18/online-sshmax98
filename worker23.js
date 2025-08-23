// ======= Advanced Semi-Pro Panel (KV + Auth + Sources + Outputs + Fragments) =======
// KV binding: SUBS
// ENV vars: PANEL_PASS, UUID

const KV_SOURCES_KEY = "sources";           
const KV_SETTINGS_KEY = "cfg:settings";     
const KV_PANEL_PASS = "cfg:panel_pass";     
const KV_UUID = "cfg:uuid";                 

const DEFAULT_SETTINGS = {
  protos: ["vmess", "vless", "trojan", "ss"],
  count: 500,
  format: "raw",
  fragment: ""
};

const VALID_PROTOS = ["vmess","vless","trojan","ss"];

function b64encode(str){return btoa(unescape(encodeURIComponent(str)))}
function b64decode(str){try{return decodeURIComponent(escape(atob(str)))}catch{try{return atob(str)}catch{return""}}}

function htmlLogin(){
return `<!doctype html>
<html lang="fa"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ورود به پنل</title>
<style>
:root{--bg:#0f172a;--card:#111827;--txt:#e5e7eb;--accent:#22d3ee;--muted:#9ca3af;}
html,body{height:100%;margin:0;background:radial-gradient(1200px 600px at 50% -10%, #0ea5e9 0%, transparent 60%), var(--bg);font-family:ui-sans-serif,system-ui; color:var(--txt)}
.wrap{min-height:100%;display:flex;align-items:center;justify-content:center;padding:24px}
.card{width:380px;max-width:94%; background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01)); border:1px solid rgba(255,255,255,.06); backdrop-filter: blur(6px); border-radius:16px;padding:24px;box-shadow:0 30px 120px rgba(0,0,0,.4)}
h1{margin:0 0 12px;font-size:22px;letter-spacing:.3px}
p{margin:0 0 14px;color:var(--muted)}
input{width:100%;padding:12px;border-radius:10px;border:1px solid rgba(255,255,255,.12); background:#0b1220;color:#fff;font-size:15px;outline:none}
.row{display:flex;gap:10px;margin-top:12px}
button{flex:1;padding:11px 12px;background:linear-gradient(90deg,#06b6d4,#22d3ee); border:0;border-radius:10px;color:#001018;font-weight:700;cursor:pointer}
</style>
</head><body>
<div class="wrap">
<form class="card" method="post" action="/login">
<h1>⚡ ورود به پنل</h1>
<p>برای ورود، رمز پنل را وارد کنید.</p>
<input name="pass" type="password" placeholder="رمز پنل" required />
<div class="row"><button type="submit">ورود</button></div>
</form></div></body></html>`;
}

function htmlPanel(hostname){
const base = `https://${hostname}`;
return `<!doctype html>
<html lang="fa"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Advanced Semi-Pro Panel</title>
<style>
:root{--bg:#0f172a;--card:#0b1220;--txt:#e5e7eb;--muted:#9ca3af;--accent:#22d3ee;--ok:#10b981;}
body{margin:0;background:radial-gradient(1200px 600px at 50% -10%, #0ea5e9 0%, transparent 60%), var(--bg);font-family:ui-sans-serif,system-ui;color:var(--txt)}
.container{max-width:1100px;margin:18px auto;padding:0 16px}
.header{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.title{font-size:22px;font-weight:800;letter-spacing:.3px}
.card{background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01)); border:1px solid rgba(255,255,255,.06); backdrop-filter: blur(6px); border-radius:14px;padding:16px;margin-top:10px;}
textarea,input,select{width:100%;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,.12); background:#0b1220;color:#fff;font-size:14px;outline:none}
.row{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.btn{padding:10px 12px;border:0;border-radius:10px;background:linear-gradient(90deg,#06b6d4,#22d3ee);color:#001018;font-weight:700;cursor:pointer}
</style></head><body>
<div class="container">
<div class="header">
<div class="title">⚡ Advanced Semi-Pro Panel</div>
<div class="tag">Host: ${hostname}</div>
</div>

<div class="card">
<h2>📡 مدیریت منابع</h2>
<textarea id="addLinks" rows="5" placeholder="Paste vmess://,vless://,trojan://,ss:// or URLs"></textarea>
<div class="row"><button class="btn" id="btnAdd">افزودن/بروزرسانی</button><button class="btn" id="btnClear">پاک کردن همه</button></div>
<div id="list" style="margin-top:10px">هیچ منبعی اضافه نشده.</div>
</div>

<div class="card">
<h2>⚙️ تنظیمات پیشرفته</h2>
<label>پروتکل‌ها:</label>
<div class="row">
<label><input type="checkbox" class="proto" value="vmess" checked> vmess</label>
<label><input type="checkbox" class="proto" value="vless" checked> vless</label>
<label><input type="checkbox" class="proto" value="trojan" checked> trojan</label>
<label><input type="checkbox" class="proto" value="ss" checked> ss</label>
</div>
<label>تعداد خروجی:</label>
<input id="count" type="number" min="1" max="5000" value="500"/>
<label>فرمت خروجی:</label>
<select id="format">
<option value="raw">raw</option>
<option value="txt">txt</option>
<option value="json">json</option>
<option value="yaml">yaml</option>
<option value="sub">sub</option>
</select>
<label>Fragment دلخواه:</label>
<input id="fragment" placeholder="اختیاری"/>
<div class="row"><button class="btn" id="btnSaveSettings">ذخیره تنظیمات</button></div>
</div>

<div class="card">
<h2>🔗 خروجی Subscriptions</h2>
<div>Raw: <span id="rawUrl">${base}/sub?format=raw</span></div>
<div>TXT: <span id="txtUrl">${base}/sub?format=txt</span></div>
<div>JSON: <span id="jsonUrl">${base}/sub?format=json</span></div>
<div>YAML: <span id="yamlUrl">${base}/sub?format=yaml</span></div>
<div>SUB: <span id="subUrl">${base}/sub?format=sub</span></div>
</div>
<script>
const $=s=>document.querySelector(s);
const $$=s=>Array.from(document.querySelectorAll(s));

async function loadSources(){
const r=await fetch('/api/sources');
const js=await r.json();
const list=$("#list"); list.innerHTML="";
if(!js.items||!js.items.length){list.innerHTML="هیچ منبعی اضافه نشده."; return;}
js.items.forEach((s,idx)=>{const div=document.createElement('div');div.textContent="#"+idx+" "+s;list.appendChild(div);});}

$("#btnAdd").addEventListener('click',async ()=>{
const txt=$("#addLinks").value;if(!txt.trim())return;
await fetch('/api/sources',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({add:txt})});
$("#addLinks").value=""; await loadSources();});
$("#btnClear").addEventListener('click',async ()=>{
await fetch('/api/sources',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({clear:true})}); await loadSources();});
$("#btnSaveSettings").addEventListener('click',async ()=>{
const protos=$$(".proto").filter(cb=>cb.checked).map(cb=>cb.value);
const count=parseInt($("#count").value)||500;
const format=$("#format").value;
const fragment=$("#fragment").value;
await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({protos,count,format,fragment})});
alert("تنظیمات ذخیره شد.");});
loadSources();
</script>
</body></html>`;}

// ---------- KV Helpers ----------
async function getPanelPass(env){const p=await env.SUBS.get(KV_PANEL_PASS);return p||env.PANEL_PASS||"12345678";}
async function getSources(env){const s=await env.SUBS.get(KV_SOURCES_KEY);if(!s)return[];try{return JSON.parse(s)||[];}catch{return[];}}
async function setSources(env,arr){await env.SUBS.put(KV_SOURCES_KEY,JSON.stringify(arr));}
async function getSettings(env){const s=await env.SUBS.get(KV_SETTINGS_KEY);if(!s)return DEFAULT_SETTINGS;try{return {...DEFAULT_SETTINGS,...JSON.parse(s)}}catch{return DEFAULT_SETTINGS};}
async function setSettings(env,js){await env.SUBS.put(KV_SETTINGS_KEY,JSON.stringify(js));}
function setCookie(n,v,a=3600){return n+"="+v+"; Path=/; HttpOnly; Max-Age="+a+"; SameSite=Lax";}
function getCookie(req,n){const c=req.headers.get("Cookie")||"";const m=c.match(new RegExp('(^|; )'+n+'=([^;]+)'));return m?m[2]:null;}

// ---------- Router ----------
export default {
async fetch(req,env){
try{
const url=new URL(req.url); const path=url.pathname; const method=req.method.toUpperCase();
const panelPass=await getPanelPass(env); const auth=getCookie(req,"auth");

// Login
if(path==="/login"&&method==="GET"){return new Response(htmlLogin(),{headers:{"Content-Type":"text/html; charset=utf-8"}});}
if(path==="/login"&&method==="POST"){
const body=await req.formData();
if(body.get("pass")===panelPass){return new Response("",{status:302,headers:{"Location":"/panel","Set-Cookie":setCookie("auth",panelPass,3600*12)}});}
return new Response(htmlLogin(),{status:401,headers:{"Content-Type":"text/html; charset=utf-8"}});}
if(auth!==panelPass) return Response.redirect("/login",302);

// Panel
if(path==="/"||path==="/panel"){return new Response(htmlPanel(url.hostname),{headers:{"Content-Type":"text/html; charset=utf-8"}});}

// API sources
if(path==="/api/sources"){
if(method==="GET"){const items=await getSources(env);return new Response(JSON.stringify({items}),{headers:{"Content-Type":"application/json"}});}
if(method==="POST"){const js=await req.json().catch(()=>({}));let items=await getSources(env); if(js.clear)items=[]; if(Array.isArray(js.delete)) {const del=new Set(js.delete.filter(x=>Number.isInteger(x))); items=items.filter((_,i)=>!del.has(i));} if(js.add){const adds=String(js.add).split(/\r?\n/).map(x=>x.trim()).filter(Boolean); for(const a of adds) if(!items
