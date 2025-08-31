#!/data/data/com.termux/files/usr/bin/python3
import os, re, json, yaml, subprocess, base64, socket, time
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------- paths & editor ----------------
BASE_DIR = "/storage/emulated/0/Download/Akbar98"
os.makedirs(BASE_DIR, exist_ok=True)
INPUT_PATH = os.path.join(BASE_DIR, "input.txt")

# always start with an empty input file and open nano
with open(INPUT_PATH, "w", encoding="utf-8") as f:
    f.write("")
subprocess.call(["nano", INPUT_PATH])

out_folder = input("Enter output folder name in Download: ").strip()
if not out_folder:
    print("Folder name required."); exit(1)
OUT_DIR = os.path.join("/storage/emulated/0/Download", out_folder)
os.makedirs(OUT_DIR, exist_ok=True)

out_name = input("Enter output file name (without extension): ").strip()
if not out_name:
    print("File name required."); exit(1)
OUT_PATH = os.path.join(OUT_DIR, f"{out_name}.yaml")

# --------------- helpers ----------------
def b64fix(s: str) -> str:
    s = s.strip().replace("\n","").replace(" ","")
    pad = len(s) % 4
    if pad: s += "=" * (4 - pad)
    return s

def safe_int(x, default=0):
    try: return int(x)
    except: return default

def sanitize(s: str) -> str:
    if not s: return ""
    return re.sub(r"[^A-Za-z0-9_\- .]", "", str(s)).strip()

_used_names = set()
def uniq_name(base: str) -> str:
    base = sanitize(base) or "Proxy"
    name = base
    i = 2
    while name in _used_names:
        name = f"{base} {i}"; i += 1
    _used_names.add(name)
    return name

def tail(s: str, n=6):
    if not s: return ""
    s2 = re.sub(r"[-]","",s)
    return s2[-n:] if len(s2) >= n else s2

# ----------------- TCP ping check -----------------
def tcp_ping_ms(host, port, timeout=2.0):
    """Return latency in ms or None if failed."""
    try:
        start = time.monotonic()
        # socket.create_connection resolves DNS
        sock = socket.create_connection((host, int(port)), timeout=timeout)
        sock.close()
        return int((time.monotonic() - start) * 1000)
    except Exception:
        return None

# --------------- extract JSON fragments ---------------
def extract_json_objects(text):
    objs, stack, start = [], [], None
    for i, c in enumerate(text):
        if c == '{':
            if not stack: start = i
            stack.append(c)
        elif c == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    objs.append(text[start:i+1])
                    start = None
    return objs

# --------------- read input ----------------
try:
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
except Exception:
    content = ""

proxies = []

# --------------- parse JSON fragments ---------------
for frag in extract_json_objects(content):
    try:
        obj = json.loads(frag)
    except Exception:
        continue
    outbounds = obj.get("outbounds", []) or []
    for ob in outbounds:
        proto = (ob.get("protocol") or "").lower()
        if proto not in ("vless","vmess","trojan","shadowsocks"):
            continue
        stream = ob.get("streamSettings") or {}
        net = (stream.get("network") or "tcp").lower()
        security = (stream.get("security") or "").lower()
        tls_flag = security in ("tls","reality")

        # VLESS / VMESS from vnext
        if proto in ("vless","vmess"):
            try:
                vnext = (ob.get("settings") or {}).get("vnext", [])[0]
                user = (vnext.get("users") or [])[0]
            except Exception:
                continue
            server = vnext.get("address") or ""
            port = safe_int(vnext.get("port"), 0)
            uid = user.get("id") or ""
            if not (server and port and uid):
                continue
            base = f"{proto}-{server}-{tail(uid)}"
            name = uniq_name(base)
            p = {"name": name, "type": proto, "server": server, "port": port, "udp": True, "network": net}
            if proto == "vless":
                p["uuid"] = uid; p["encryption"] = "none"
            else:
                p["uuid"] = uid; p["alterId"] = safe_int(user.get("alterId", user.get("aid",0)))
                p["cipher"] = user.get("cipher", "auto") or ob.get("settings", {}).get("clients", [{}])[0].get("cipher","auto")
            if tls_flag:
                # try common places for servername
                sni = (stream.get("tlsSettings") or {}).get("serverName") or (stream.get("realitySettings") or {}).get("serverName") or server
                p["tls"] = True; p["servername"] = sni
            if net == "ws":
                ws = stream.get("wsSettings") or {}
                path = ws.get("path") or "/"
                headers = ws.get("headers") or {}
                p["ws-opts"] = {"path": path}
                if headers: p["ws-opts"]["headers"] = headers
            if net == "grpc":
                grpc = stream.get("grpcSettings") or {}
                svc = grpc.get("serviceName") or ""
                p["grpc-opts"] = {"grpc-service-name": svc}
            proxies.append(p)

        # Trojan
        elif proto == "trojan":
            try:
                s = (ob.get("settings") or {}).get("servers", [])[0]
            except Exception:
                continue
            server = s.get("address") or ""
            port = safe_int(s.get("port"), 0)
            pwd = s.get("password") or ""
            if not (server and port and pwd):
                continue
            name = uniq_name(f"trojan-{server}-{tail(pwd)}")
            p = {"name": name, "type": "trojan", "server": server, "port": port, "password": pwd, "udp": True, "network": "tcp"}
            if tls_flag:
                p["tls"] = True; p["sni"] = server
            proxies.append(p)

        # Shadowsocks
        elif proto == "shadowsocks":
            try:
                s = (ob.get("settings") or {}).get("servers", [])[0]
            except Exception:
                continue
            server = s.get("address") or ""
            port = safe_int(s.get("port"), 0)
            cipher = s.get("method") or s.get("cipher") or ""
            password = s.get("password") or ""
            if not (server and port and cipher and password):
                continue
            name = uniq_name(f"ss-{server}-{port}")
            p = {"name": name, "type": "ss", "server": server, "port": port, "cipher": cipher, "password": password, "udp": True}
            proxies.append(p)

# --------------- parse line links ---------------
for line in [ln.strip() for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("{")]:
    try:
        if line.startswith("vless://"):
            parsed = urlparse(line)
            uid = parsed.username or ""
            host = parsed.hostname or ""
            port = parsed.port or 443
            q = parse_qs(parsed.query)
            if not (uid and host and port):
                continue
            net = (q.get("type", ["tcp"])[0] or "tcp").lower()
            tls_flag = (q.get("security", [""])[0] or "").lower() in ("tls","reality")
            name = uniq_name(f"vless-{host}-{tail(uid)}")
            p = {"name": name, "type": "vless", "server": host, "port": port, "uuid": uid, "encryption":"none","udp":True,"network":net}
            if net == "ws":
                p["ws-opts"] = {"path": q.get("path", ["/"])[0]}
                hosth = q.get("host", []) or q.get("Host", [])
                if hosth: p["ws-opts"]["headers"] = {"Host":hosth[0]}
            elif net == "grpc":
                svc = q.get("serviceName", [""])[0]
                if svc: p["grpc-opts"] = {"grpc-service-name": svc}
            if tls_flag:
                sni = q.get("sni", []) or q.get("servername", []) or [host]
                p["tls"] = True; p["servername"] = sni[0]
            proxies.append(p)

        elif line.startswith("vmess://"):
            payload = line[8:]
            try:
                decoded = base64.b64decode(b64fix(payload)).decode(errors="ignore")
                info = json.loads(decoded)
            except Exception:
                continue
            host = info.get("add") or info.get("server") or ""
            port = safe_int(info.get("port"), 0)
            uid = info.get("id") or ""
            if not (host and port and uid):
                continue
            net = (info.get("net") or "tcp").lower()
            tls_flag = str(info.get("tls","")).lower() == "tls"
            name = uniq_name(f"vmess-{host}-{tail(uid)}")
            p = {"name": name, "type": "vmess", "server": host, "port": port, "uuid": uid, "alterId": safe_int(info.get("aid", info.get("alterId",0))), "cipher": info.get("scy","auto"), "udp": True, "network": net}
            if net == "ws":
                path = info.get("path") or "/"
                hosth = info.get("host") or ""
                p["ws-opts"] = {"path": path}
                if hosth: p["ws-opts"]["headers"] = {"Host": hosth}
            if tls_flag:
                sni = info.get("sni") or info.get("host") or host
                p["tls"] = True; p["servername"] = sni
            proxies.append(p)

        elif line.startswith("trojan://"):
            parsed = urlparse(line)
            pwd = parsed.username or ""
            host = parsed.hostname or ""
            port = parsed.port or 443
            if not (pwd and host and port):
                continue
            q = parse_qs(parsed.query)
            sni = q.get("sni", [host])[0]
            name = uniq_name(f"trojan-{host}-{tail(pwd)}")
            p = {"name": name, "type": "trojan", "server": host, "port": port, "password": pwd, "udp": True, "network":"tcp", "tls": True, "sni": sni}
            proxies.append(p)

        elif line.startswith("ss://"):
            # support multiple ss forms
            try:
                after = line[5:]
                # form: ss://method:pass@host:port
                if "@" in after and ":" in after.split("@",1)[0]:
                    cred, rest = after.split("@",1)
                    if ":" in cred:
                        method, password = cred.split(":",1)
                    else:
                        continue
                    host_port = rest.split("#",1)[0]
                    if ":" not in host_port: continue
                    host, port = host_port.rsplit(":",1)
                else:
                    # form: ss://base64(method:password)@host:port
                    if "@" not in after: continue
                    b64cred, rest = after.split("@",1)
                    method_password = base64.urlsafe_b64decode(b64fix(b64cred)).decode()
                    method, password = method_password.split(":",1)
                    host_port = rest.split("#",1)[0]
                    host, port = host_port.rsplit(":",1)
                method = method.strip(); password = password.strip(); host = host.strip(); port = safe_int(port.strip(),0)
                if not (method and password and host and port):
                    continue
                name = uniq_name(f"ss-{host}-{port}")
                p = {"name": name, "type":"ss", "server": host, "port": port, "cipher": method, "password": password, "udp": True}
                proxies.append(p)
            except Exception:
                continue

    except Exception:
        continue

# ----------------- perform parallel TCP ping checks -----------------
def check_and_attach_ping(proxy):
    host = proxy.get("server") or ""
    port = proxy.get("port") or 0
    if not host or not port:
        proxy["ping"] = None
        proxy["status"] = "dead"
        return proxy
    lat = tcp_ping_ms(host, port, timeout=3.0)
    if lat is None:
        proxy["ping"] = None
        proxy["status"] = "dead"
    else:
        proxy["ping"] = lat
        proxy["status"] = "ok"
    return proxy

# run concurrent checks (limit threads)
results = []
if proxies:
    max_workers = min(40, len(proxies))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(check_and_attach_ping, p): idx for idx,p in enumerate(proxies)}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                results.append(res)
            except Exception:
                pass
# keep order: use results mapping by name
# build mapping from name->proxy (updated)
name_map = {p["name"]: p for p in results} if results else {p["name"]: p for p in proxies}
final_proxies = [name_map.get(p["name"], p) for p in proxies]

# build GoodPing list sorted
good = [p for p in final_proxies if p.get("status")=="ok"]
good_sorted = sorted(good, key=lambda x: x.get("ping", 99999))

proxy_names = [p["name"] for p in final_proxies]

# ----------------- final config -----------------
config = {
    "proxies": final_proxies,
    "proxy-groups": [
        {"name":"Selector","type":"select","proxies":["GoodPing","Auto-URLTest","DIRECT"] + proxy_names},
        {"name":"GoodPing","type":"select","proxies":[p["name"] for p in good_sorted]},
        {"name":"Auto-URLTest","type":"url-test","url":"https://www.gstatic.com/generate_204","interval":25,"tolerance":50,"proxies":proxy_names},
        {"name":"Direct","type":"select","proxies":["DIRECT"]},
        {"name":"Block","type":"select","proxies":["REJECT","DIRECT"]}
    ],
    "rules": ["MATCH,Selector"]
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

# clear input
with open(INPUT_PATH, "w", encoding="utf-8") as f:
    f.write("")

print(f"[✅] Saved {len(final_proxies)} proxies to {OUT_PATH}")
