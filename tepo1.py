#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import threading
import time
import requests
import base64
import urllib.parse
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== تنظیمات =====================
CONF_PATH = "config1.json"
TEXT_PATH = "normal.json"
FIN_PATH = "final.json"
UPDATE_INTERVAL = 3600  # ثانیه، آپدیت هر 1 ساعت
DOWNLOAD_COPY_PATH = "/sdcard/Download/Akbar98/final.json"

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/sab-vip10/main/tepo10.json",
    "https://raw.githubusercontent.com/tepo18/sab-vip10/main/tepo20.json",
    "https://raw.githubusercontent.com/tepo18/sab-vip10/main/tepo30.json",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== کلاس کانفیگ =====================
@dataclass
class ConfigParams:
    protocol: str
    address: str
    port: int
    tag: Optional[str] = ""
    id: Optional[str] = ""
    extra_params: Dict[str, Any] = field(default_factory=dict)

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
        match = re.search(r"@([^:]+):(\d+)", line)
        if match:
            addr = match.group(1)
            port = int(match.group(2))
        tag = line.split("#", 1)[1] if "#" in line else ""
        return ConfigParams(protocol=protocol, address=addr, port=port, tag=tag)
    except Exception:
        return None

def fetch_link(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text.splitlines()
        else:
            return []
    except Exception:
        return []

def clear_and_merge_configs(lines: List[str]) -> List[str]:
    final_lines = []
    unique_keys = {}
    for line in lines:
        if not is_valid_config(line):
            continue
        cfg = parse_config_line(line)
        if cfg:
            key = f"{cfg.protocol}|{cfg.address}|{cfg.port}|{cfg.id}"
        else:
            key = line
        if key not in unique_keys:
            unique_keys[key] = line
    for val in unique_keys.values():
        final_lines.append(val)
    return final_lines

def update_subs():
    # بارگذاری لینک‌ها از config.json در صورت موجود بودن
    if os.path.exists(CONF_PATH):
        try:
            with open(CONF_PATH, "r", encoding="utf-8") as f:
                conf_data = json.load(f)
                global LINK_PATH, UPDATE_INTERVAL
                LINK_PATH = conf_data.get("link_path", LINK_PATH)
                UPDATE_INTERVAL = conf_data.get("update_interval", UPDATE_INTERVAL)
        except Exception as e:
            print(f"[!] Failed to read {CONF_PATH}: {e}")

    all_lines: List[str] = []
    threads: List[threading.Thread] = []
    results: List[List[str]] = [None] * len(LINK_PATH)

    def worker(i: int, url: str):
        results[i] = fetch_link(url)

    for i, url in enumerate(LINK_PATH):
        t = threading.Thread(target=worker, args=(i, url))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for r in results:
        if r:
            all_lines.extend(r)

    total_before = len(all_lines)
    all_lines = remove_empty_strings(all_lines)
    all_lines = clear_and_merge_configs(all_lines)
    all_lines = list(dict.fromkeys(all_lines))
    total_after = len(all_lines)
    removed_count = total_before - total_after

    all_lines.insert(0, FILE_HEADER_TEXT)

    # ذخیره در فایل‌ها
    try:
        os.makedirs(os.path.dirname(DOWNLOAD_COPY_PATH), exist_ok=True)
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_lines))
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_lines))
        with open(DOWNLOAD_COPY_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_lines))
        print(f"[✅] Updated {FIN_PATH} and copied to {DOWNLOAD_COPY_PATH} ({total_after} lines, removed {removed_count})")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== حلقه اصلی =====================
if __name__ == "__main__":
    print("[*] Starting full-feature subscription updater...")
    while True:
        print("[*] Updating subscriptions...")
        update_subs()
        print(f"[*] Next update in {UPDATE_INTERVAL // 60} minutes...\n")
        time.sleep(UPDATE_INTERVAL)
