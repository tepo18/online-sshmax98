#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, time, requests, base64, urllib.parse, socket, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from dataclasses import dataclass, field

# ===================== تنظیمات =====================
TH_MAX_WORKER = 5
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"
BASE64_TXT = "base64.txt"
FINAL_RAW = "final.raw"
UPDATE_INTERVAL = 3600  # ثانیه، آپدیت هر 1 ساعت
LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo98.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo98.yaml",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo98.json",
]
FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

@dataclass
class ConfigParams:
    protocol: str
    address: str
    port: int
    tag: Optional[str] = ""
    id: Optional[str] = ""
    extra_params: dict = field(default_factory=dict)

# ===================== توابع =====================
def remove_empty_strings(lst: List[str]) -> List[str]:
    return [str(item).strip() for item in lst if item and str(item).strip()]

def is_valid_config(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 5:
        return False
    lower = line.lower()
    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False
    return True

def parse_config_line(line: str) -> Optional[ConfigParams]:
    try:
        line = urllib.parse.unquote(line.strip())
        protocol = None
        for p in ["vmess", "vless", "trojan", "hy2", "hysteria2", "ss", "socks", "wireguard"]:
            if line.startswith(p + "://"):
                protocol = p
                break
        if not protocol:
            return None
        addr, port = "unknown", 0
        import re
        match = re.search(r"@([^:]+):(\d+)", line)
        if match:
            addr = match.group(1)
            port = int(match.group(2))
        tag = line.split("#", 1)[1] if "#" in line else ""
        return ConfigParams(protocol=protocol, address=addr, port=port, tag=tag)
    except:
        return None

def fetch_link(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text.splitlines()
    except:
        pass
    return []

def tcp_test(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def ping_test(host: str, count=1, timeout=1000) -> bool:
    try:
        result = subprocess.run(["ping", "-c", str(count), "-W", str(timeout), host],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def http_test(host: str, timeout=5) -> bool:
    try:
        url = f"https://{host}"
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False

def validate_config(line: str, precise=False) -> Optional[str]:
    cfg = parse_config_line(line)
    if not cfg:
        return line if not precise else None
    try:
        host = cfg.address
        port = cfg.port or 443
        if precise:
            if tcp_test(host, port) and ping_test(host) and http_test(host):
                return line
        else:
            if tcp_test(host, port):
                return line
    except:
        return None
    return None

def process_configs(lines: List[str], precise=False) -> List[str]:
    valid_configs = []
    with ThreadPoolExecutor(max_workers=TH_MAX_WORKER) as executor:
        future_to_line = {executor.submit(validate_config, line, precise): line for line in lines}
        for future in as_completed(future_to_line):
            res = future.result()
            if res:
                valid_configs.append(res)
    return list(dict.fromkeys(valid_configs))  # remove duplicates

def save_outputs(lines: List[str]):
    try:
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        b64_lines = [base64.b64encode(line.encode()).decode() for line in lines]
        with open(BASE64_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(b64_lines))
        with open(FINAL_RAW, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join([FILE_HEADER_TEXT]+lines))
        print(f"[✅] Saved outputs ({len(lines)} configs).")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

def update_subs():
    all_lines = []
    for url in LINK_PATH:
        all_lines.extend(fetch_link(url))
    all_lines = remove_empty_strings(all_lines)
    all_lines = process_configs(all_lines, precise=False)
    # ذخیره اولیه در normal.txt
    with open(TEXT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join([FILE_HEADER_TEXT]+all_lines))
    print(f"[*] {len(all_lines)} configs saved to {TEXT_PATH} (preliminary)")
    # پردازش دقیق روی normal.txt
    final_configs = process_configs(all_lines, precise=True)
    save_outputs(final_configs)
    print("[*] Done. All valid configs saved.")

if __name__ == "__main__":
    print("[*] Starting full-feature subscription updater...")
    while True:
        print("[*] Updating subscriptions...")
        update_subs()
        print(f"[*] Next update in {UPDATE_INTERVAL // 60} minutes.\n")
        time.sleep(UPDATE_INTERVAL)
