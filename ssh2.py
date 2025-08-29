#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import threading
import urllib.request
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== Paths & Settings =====================
CONF_PATH = "config1.json"
TEXT_PATH = "normal.json"
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
    valid: bool = True
    remark: str = ""

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
    # رد کردن کانفیگ های ناقص یا خطا
    if not cfg:
        return False
    # مثال: اگر کلید remarks یا outbounds نداشت رد شود
    if "remarks" not in cfg or "outbounds" not in cfg:
        return False
    return True

def update_subs():
    all_configs: List[ConfigParams] = []

    threads: List[threading.Thread] = []
    results: List[List[Dict[str, Any]]] = [None] * len(LINK_PATH)

    def worker(i: int, url: str):
        results[i] = fetch_json(url)

    for i, url in enumerate(LINK_PATH):
        t = threading.Thread(target=worker, args=(i, url))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    for r in results:
        if r:
            for cfg in r:
                if validate_config(cfg):
                    all_configs.append(ConfigParams(raw=cfg, valid=True, remark=cfg.get("remarks", "")))

    # حذف تکراری بر اساس remark
    unique = {}
    for cfg in all_configs:
        key = cfg.remark
        if key not in unique:
            unique[key] = cfg
    final_list = [cfg.raw for cfg in unique.values()]

    # اضافه کردن هدر
    output_list = [FILE_HEADER_TEXT] + final_list

    # ذخیره فایل
    try:
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        # کپی خودکار به مسیر دانلود
        os.makedirs(os.path.dirname(DOWNLOAD_COPY_PATH), exist_ok=True)
        with open(DOWNLOAD_COPY_PATH, "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        print(f"[✅] Updated {FIN_PATH} and copied to {DOWNLOAD_COPY_PATH} ({len(final_list)} configs)")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater...")
    update_subs()
    print("[*] Done. All valid configs saved.")
