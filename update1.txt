#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, threading, time, requests, base64, urllib.parse, socket, subprocess
from typing import List, Dict

# ===================== تنظیمات =====================
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"
UPDATE_INTERVAL = 3600  # ثانیه، آپدیت هر 1 ساعت

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo30.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo40.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo50.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo60.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo70.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo80.txt",
    "https://raw.githubusercontent.com/tepo18/reza-shah1320/main/tepo90.txt",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== توابع =====================
def fetch_link(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            lines = r.text.splitlines()
            return [l.strip() for l in lines if l.strip()]
    except:
        pass
    return []

def is_valid_config(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 5:
        return False
    lower = line.lower()
    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False
    return True

def parse_config_line(line: str):
    try:
        line = urllib.parse.unquote(line.strip())
        for p in ["vmess", "vless", "trojan", "hy2", "hysteria2", "ss", "socks", "wireguard"]:
            if line.startswith(p + "://"):
                return line
    except:
        pass
    return None

def tcp_test(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def process_configs(lines: List[str], precise_test=False) -> List[str]:
    valid_configs = []
    lock = threading.Lock()

    def worker(line):
        cfg = parse_config_line(line)
        passed = False
        if cfg:
            try:
                # استخراج آدرس و پورت ساده
                import re
                m = re.search(r"@([^:]+):(\d+)", cfg)
                host, port = (m.group(1), int(m.group(2))) if m else ("", 443)
                if precise_test and host:
                    passed = tcp_test(host, port)
                else:
                    passed = True
            except:
                passed = False
        if passed and is_valid_config(line):
            with lock:
                valid_configs.append(line)

    threads = []
    for line in lines:
        t = threading.Thread(target=worker, args=(line,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # حذف تکراری
    final_list = list(dict.fromkeys(valid_configs))
    return final_list

def save_outputs(lines: List[str]):
    try:
        # ذخیره normal
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join([FILE_HEADER_TEXT]+lines))
        # ذخیره final
        final_lines = process_configs(lines, precise_test=True)
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))
        print(f"[✅] Saved outputs ({len(final_lines)} configs):")
        print(f"  -> {TEXT_PATH}")
        print(f"  -> {FIN_PATH}")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== بروزرسانی کانفیگ ها =====================
def update_subs():
    all_lines = []
    for url in LINK_PATH:
        fetched = fetch_link(url)
        if not fetched:
            print(f"[⚠️] Cannot fetch or empty source: {url}")
        else:
            all_lines.extend(fetched)
    all_lines = process_configs(all_lines)
    save_outputs(all_lines)

# ===================== حلقه اصلی =====================
if __name__ == "__main__":
    print("[*] Starting subscription updater with hourly auto-update...")
    while True:
        update_subs()
        print(f"[*] Next update in {UPDATE_INTERVAL//60} minutes.\n")
        time.sleep(UPDATE_INTERVAL)
