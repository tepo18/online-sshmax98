#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import threading
import urllib.request
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Any

# ===================== Paths & Settings =====================
FIN_PATH = "final.json"    
DOWNLOAD_COPY_PATH = "/sdcard/Download/Akbar98/final.json"

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.json",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== Config Class =====================
@dataclass
class ConfigParams:
    raw: Dict[str, Any]
    remark: str = ""
    valid: bool = True

# ===================== Helper Functions =====================
def fetch_json(url: str) -> List[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            content = resp.read().decode()
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def validate_config(cfg: Dict[str, Any]) -> bool:
    if not cfg or "remarks" not in cfg or "outbounds" not in cfg:
        return False
    return True

def test_ping(config: Dict[str, Any]) -> bool:
    """پینگ ساده برای بررسی اتصال"""
    try:
        # نمونه: ping سرور
        address = config.get("outbounds", [{}])[0].get("settings", {}).get("vnext", [{}])[0].get("address", "")
        if not address:
            return False
        result = subprocess.run(["ping", "-c", "1", "-W", "2", address], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

# ===================== Main Update Function =====================
def update_subs():
    all_configs: List[ConfigParams] = []
    results: List[List[Dict[str, Any]]] = [None] * len(LINK_PATH)
    threads: List[threading.Thread] = []

    # دانلود همزمان
    def worker(i: int, url: str):
        results[i] = fetch_json(url)

    for i, url in enumerate(LINK_PATH):
        t = threading.Thread(target=worker, args=(i, url))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # اعتبارسنجی کانفیگ‌ها
    for r in results:
        if r:
            for cfg in r:
                if validate_config(cfg):
                    all_configs.append(ConfigParams(raw=cfg, remark=cfg.get("remarks", "")))

    # حذف تکراری‌ها بر اساس remark
    unique = {}
    for cfg in all_configs:
        key = cfg.remark
        if key not in unique:
            unique[key] = cfg
    final_candidates = [cfg.raw for cfg in unique.values()]

    # پینگ و تست اتصال
    final_list = []
    for cfg in final_candidates:
        if test_ping(cfg):
            final_list.append(cfg)

    # اضافه کردن هدر
    output_list = [FILE_HEADER_TEXT] + final_list

    # ذخیره نهایی
    try:
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            json.dump(output_list, f, indent=4, ensure_ascii=False)
        os.makedirs(os.path.dirname(DOWNLOAD_COPY_PATH), exist_ok=True)
        with open(DOWNLOAD_COPY_PATH, "w", encoding="utf-8") as f:
            json.dump(output_list, f, indent=4, ensure_ascii=False)
        print(f"[✅] Updated {FIN_PATH} and copied to {DOWNLOAD_COPY_PATH} ({len(final_list)} configs passed ping test)")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting JSON subscription updater with ping test...")
    update_subs()
    print("[*] Done. All valid configs saved.")
