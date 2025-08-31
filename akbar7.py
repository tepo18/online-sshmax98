#!/data/data/com.termux/files/usr/bin/python3
import os
import re
import json
import yaml
import subprocess
from urllib.parse import urlparse, parse_qs
import base64

# -------- مسیر و فایل --------
BASE_DIR = "/storage/emulated/0/Download/ProxyTool"
os.makedirs(BASE_DIR, exist_ok=True)
INPUT_FILE = os.path.join(BASE_DIR, "input.txt")

# -------- باز کردن nano --------
with open(INPUT_FILE, "w", encoding="utf-8") as f:
    f.write("")  # خالی کردن قبل از باز کردن
subprocess.call(["nano", INPUT_FILE])

# -------- مسیر و نام فایل خروجی --------
output_folder = input("Enter output folder name in Download: ").strip()
if not output_folder:
    print("Folder name cannot be empty!")
    exit(1)
output_dir = os.path.join("/storage/emulated/0/Download", output_folder)
os.makedirs(output_dir, exist_ok=True)

output_name = input("Enter output file name (without extension): ").strip()
if not output_name:
    print("File name cannot be empty!")
    exit(1)
OUTPUT_FILE = os.path.join(output_dir, f"{output_name}.yaml")

# -------- پاکسازی و یکتا کردن نام‌ها --------
used_names = set()
def clean_name(raw):
    name = re.sub(r'[^\w\s-]', '', raw).strip()
    if not name:
        name = "Proxy"
    base = name
    count = 1
    unique = name
    while unique in used_names:
        count += 1
        unique = f"{base} {count}"
    used_names.add(unique)
    return unique

# -------- استخراج JSON --------
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

# -------- خواندن محتوا --------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

proxies = []

# -------- پردازش JSON ----------
for frag_text in extract_json_objects(content):
    try:
        fragment = json.loads(frag_text)
        for outbound in fragment.get("outbounds", []):
            proto = outbound.get("protocol", "").lower()
            if proto not in ["vless", "vmess", "trojan", "shadowsocks"]:
                continue
            name = clean_name(fragment.get("remarks", proto))
            proxy = {
                "name": name,
                "type": proto,
                "server": "",
                "port": 0,
                "uuid": "",
                "password": "",
                "cipher": "",
                "tls": False,
                "network": "tcp",
                "grpc_opts": {},
                "ws_opts": {},
                "fallback": False
            }
            stream = outbound.get("streamSettings", {})
            proxy["network"] = stream.get("network", "tcp")
            proxy["tls"] = stream.get("security", "").lower() == "tls"

            try:
                if proto in ["vless", "vmess"]:
                    vnext = outbound["settings"]["vnext"][0]
                    user = vnext["users"][0]
                    proxy["server"] = vnext.get("address", "")
                    proxy["port"] = vnext.get("port", 443)
                    proxy["uuid"] = user.get("id", "")
                    if proxy["network"] == "grpc":
                        grpc = stream.get("grpcSettings", {})
                        proxy["grpc_opts"] = {"serviceName": grpc.get("serviceName", "/")}
                    elif proxy["network"] == "ws":
                        ws = stream.get("wsSettings", {})
                        proxy["ws_opts"] = {"path": ws.get("path", "/"), "headers": ws.get("headers", {})}
                elif proto == "trojan":
                    s = outbound["settings"]["servers"][0]
                    proxy["server"] = s.get("address", "")
                    proxy["port"] = s.get("port", 443)
                    proxy["password"] = s.get("password", "")
                elif proto == "shadowsocks":
                    s = outbound["settings"]["servers"][0]
                    proxy["server"] = s.get("address", "")
                    proxy["port"] = s.get("port", 8388)
                    proxy["password"] = s.get("password", "")
                    proxy["cipher"] = s.get("method", "aes-256-gcm")
            except Exception:
                proxy["fallback"] = True

            if proxy["server"] and proxy["port"] and (proxy["uuid"] or proxy["password"]):
                proxies.append(proxy)
            else:
                proxy["fallback"] = True
                proxies.append(proxy)
    except Exception:
        continue

# -------- پردازش خطی (VLESS/VMESS/Trojan/SS) ----------
lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith('{')]
for line in lines:
    try:
        if line.startswith("vless://"):
            parsed = urlparse(line)
            uuid = parsed.username
            server = parsed.hostname
            port = parsed.port or 443
            query = parse_qs(parsed.query)
            name = clean_name(uuid or "VLESS")
            proxy = {
                "name": name,
                "type": "vless",
                "server": server,
                "port": port,
                "uuid": uuid,
                "tls": query.get("security", [""])[0] == "tls",
                "network": query.get("type", ["tcp"])[0],
                "grpc_opts": {},
                "ws_opts": {},
                "fallback": False
            }
            if proxy["network"] == "ws":
                proxy["ws_opts"] = {"path": query.get("path", ["/"])[0]}
            if proxy["server"] and proxy["port"] and proxy["uuid"]:
                proxies.append(proxy)
        elif line.startswith("vmess://"):
            decoded = base64.b64decode(line[8:]).decode(errors="ignore")
            info = json.loads(decoded)
            name = clean_name(info.get("ps", "VMESS"))
            proxy = {
                "name": name,
                "type": "vmess",
                "server": info.get("add"),
                "port": int(info.get("port", 443)),
                "uuid": info.get("id"),
                "alterId": int(info.get("aid", 0)),
                "cipher": "auto",
                "tls": info.get("tls") == "tls",
                "network": info.get("net", "tcp"),
                "grpc_opts": {},
                "ws_opts": {},
                "fallback": False
            }
            if proxy["network"] == "ws":
                proxy["ws_opts"] = {"path": info.get("path", "/")}
            if proxy["server"] and proxy["port"] and proxy["uuid"]:
                proxies.append(proxy)
        elif line.startswith("trojan://"):
            parsed = urlparse(line)
            password = parsed.username
            server = parsed.hostname
            port = parsed.port or 443
            name = clean_name(password or "TROJAN")
            proxy = {
                "name": name,
                "type": "trojan",
                "server": server,
                "port": port,
                "password": password,
                "tls": True,
                "network": "tcp",
                "fallback": False
            }
            if proxy["server"] and proxy["port"] and proxy["password"]:
                proxies.append(proxy)
        elif line.startswith("ss://"):
            m = re.match(r"ss://([^:]+):([^@]+)@([^:]+):(\d+)", line)
            if m:
                cipher, password, server, port = m.groups()
                name = clean_name(server)
                proxy = {
                    "name": name,
                    "type": "shadowsocks",
                    "server": server,
                    "port": int(port),
                    "password": password,
                    "cipher": cipher,
                    "network": "tcp",
                    "fallback": False
                }
                proxies.append(proxy)
    except Exception:
        continue

# -------- ساخت کانفیگ نهایی --------
proxy_names = [p["name"] for p in proxies]
meta_config = {
    "proxies": proxies,
    "proxy-groups": [
        {"name": "Selector", "type": "select", "proxies": proxy_names},
        {"name": "BestPing", "type": "url-test", "url": "https://www.gstatic.com/generate_204",
         "interval": 20, "tolerance": 30, "proxies": proxy_names},
        {"name": "Global", "type": "select", "proxies": proxy_names},
        {"name": "Direct", "type": "select", "proxies": proxy_names},
        {"name": "Block", "type": "select", "proxies": proxy_names},
        {"name": "Fallback", "type": "fallback", "proxies": proxy_names, "url": "https://www.gstatic.com/generate_204"}
    ],
    "rules": ["MATCH,Selector"]
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    yaml.safe_dump(meta_config, f, allow_unicode=True, sort_keys=False)

print(f"[✅] Output saved to {OUTPUT_FILE}")

# -------- خالی کردن فایل ورودی بعد از ذخیره --------
