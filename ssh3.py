#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import threading
import urllib.request
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== Paths & Settings =====================
CONFIG_PATH = "config.json"
NORMAL_PATH = "normal.json"
FINAL_PATH = "final.json"

DOWNLOAD_COPY_PATH = "/sdcard/Download/Akbar98/final.json"

LINK_PATHS = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.json",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== Data Classes =====================
@dataclass
class ConfigParams:
    raw: Dict[str, Any]
    remark: str = ""
    valid: bool = True
    ping: Optional[int] = None

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
    # کانفیگ ناقص یا بدون remark/outbounds را رد کن
    if not cfg or "remarks" not in cfg or "outbounds" not in cfg:
        return False
    return True

def ping_server(address: str, port: int = 443, timeout: int = 3) -> Optional[int]:
    try:
        # از ping ساده برای بررسی اتصال استفاده می‌کنیم
        import socket, time
        start = time.time()
        s = socket.create_connection((address, port), timeout=timeout)
        s.close()
        return int((time.time() - start) * 1000)  # میلی‌ثانیه
    except:
        return None

# ===================== Main Processing =====================
def update_subscriptions():
    all_configs: List[ConfigParams] = []

    threads: List[threading.Thread] = []
    results: List[List[Dict[str, Any]]] = [None] * len(LINK_PATHS)

    # دانلود منابع همزمان
    def worker(i: int, url: str):
        results[i] = fetch_json(url)

    for i, url in enumerate(LINK_PATHS):
        t = threading.Thread(target=worker, args=(i, url))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # اعتبارسنجی اولیه و اضافه کردن به لیست
    for r in results:
        if r:
            for cfg in r:
                if validate_config(cfg):
                    all_configs.append(ConfigParams(raw=cfg, remark=cfg.get("remarks", "")))

    # حذف تکراری بر اساس remark
    unique = {}
    for cfg in all_configs:
        if cfg.remark not in unique:
            unique[cfg.remark] = cfg
    final_configs = list(unique.values())

    # تست اتصال هر کانفیگ
    print(f"[*] Testing {len(final_configs)} configs...")
    for cfg in final_configs:
        try:
            outbounds = cfg.raw.get("outbounds", [])
            if outbounds:
                address = outbounds[0]["settings"]["vnext"][0]["address"] if "vnext" in outbounds[0]["settings"] else "127.0.0.1"
                port = outbounds[0]["settings"]["vnext"][0].get("port", 443) if "vnext" in outbounds[0]["settings"] else 443
                ping = ping_server(address, port)
                cfg.ping = ping
                cfg.valid = ping is not None
            else:
                cfg.valid = False
        except:
            cfg.valid = False

    # فقط کانفیگ‌های سالم
    valid_configs = [cfg.raw for cfg in final_configs if cfg.valid]

    # اضافه کردن هدر
    output_list = [FILE_HEADER_TEXT] + valid_configs

    # ذخیره فایل‌ها
    try:
        # ذخیره موقت normal.json
        with open(NORMAL_PATH, "w", encoding="utf-8") as f:
            json.dump(valid_configs, f, indent=4, ensure_ascii=False)
        # ذخیره نهایی final.json
        with open(FINAL_PATH, "w", encoding="utf-8") as f:
            json.dump(valid_configs, f, indent=4, ensure_ascii=False)
        # کپی خودکار به مسیر دانلود
        os.makedirs(os.path.dirname(DOWNLOAD_COPY_PATH), exist_ok=True)
        with open(DOWNLOAD_COPY_PATH, "w", encoding="utf-8") as f:
            json.dump(valid_configs, f, indent=4, ensure_ascii=False)
        print(f"[✅] Updated {FINAL_PATH} and copied to {DOWNLOAD_COPY_PATH} ({len(valid_configs)} configs)")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater with ping test...")
    update_subscriptions()
    print("[*] Done. All valid configs saved.")
