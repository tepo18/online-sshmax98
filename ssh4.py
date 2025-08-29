#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import threading
import urllib.request
import socket
from typing import List, Dict

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.json",
]

FINAL_JSON = "final.json"

def fetch_json(url: str) -> List[Dict]:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except:
        return []

def is_port_open(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def validate_config(cfg: Dict) -> bool:
    # بررسی کلیدهای ضروری
    if not cfg or "remarks" not in cfg or "outbounds" not in cfg:
        return False
    return True

def test_config(cfg: Dict) -> bool:
    # فقط کانفیگ‌های TCP/WS/gRPC با سرور قابل اتصال
    for outbound in cfg.get("outbounds", []):
        settings = outbound.get("settings", {})
        vnext = settings.get("vnext", [])
        if vnext:
            host = vnext[0].get("address")
            port = vnext[0].get("port")
            if host and port and is_port_open(host, port):
                return True
    return False

def update_subs():
    all_configs = []
    threads = []
    results = [None] * len(LINK_PATH)

    def worker(i, url):
        results[i] = fetch_json(url)

    for i, url in enumerate(LINK_PATH):
        t = threading.Thread(target=worker, args=(i, url))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    for r in results:
        if r:
            for cfg in r:
                if validate_config(cfg) and test_config(cfg):
                    all_configs.append(cfg)

    # حذف کانفیگ‌های تکراری بر اساس remark
    unique = {}
    for cfg in all_configs:
        key = cfg.get("remarks", "")
        if key not in unique:
            unique[key] = cfg

    final_list = list(unique.values())

    # ذخیره نهایی
    with open(FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)

    print(f"[✅] Updated {FINAL_JSON} ({len(final_list)} configs passed test)")

if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater with connectivity test...")
    update_subs()
    print("[*] Done. All valid configs saved.")
