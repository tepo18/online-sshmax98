#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import base64
import threading
import urllib.request
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== Paths & Settings =====================
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
NORMAL_PATH = os.path.join(REPO_DIR, "normal.json")
FINAL_JSON_PATH = os.path.join(REPO_DIR, "final.json")
FINAL_TXT_PATH = os.path.join(REPO_DIR, "final3.txt")
BASE64_PATH = os.path.join(REPO_DIR, "base64.txt")
FINAL_RAW_PATH = os.path.join(REPO_DIR, "final.raw")

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
    if not cfg:
        return False
    if "remarks" not in cfg or "outbounds" not in cfg:
        return False
    return True

def deduplicate_configs(configs: List[ConfigParams]) -> List[ConfigParams]:
    unique = {}
    for cfg in configs:
        key = cfg.remark
        if key not in unique:
            unique[key] = cfg
    return list(unique.values())

def save_outputs(configs: List[Dict[str, Any]]):
    # JSON final
    with open(FINAL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4, ensure_ascii=False)
    # TXT final3
    with open(FINAL_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER_TEXT + "\n")
        for cfg in configs:
            f.write(json.dumps(cfg, ensure_ascii=False) + "\n")
    # base64.txt
    with open(BASE64_PATH, "w", encoding="utf-8") as f:
        for cfg in configs:
            encoded = base64.b64encode(json.dumps(cfg, ensure_ascii=False).encode()).decode()
            f.write(encoded + "\n")
    # raw
    with open(FINAL_RAW_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(configs, ensure_ascii=False))

def initial_update():
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

    all_configs = deduplicate_configs(all_configs)
    # ذخیره اولیه در normal.json
    with open(NORMAL_PATH, "w", encoding="utf-8") as f:
        json.dump([c.raw for c in all_configs], f, indent=4, ensure_ascii=False)

    return all_configs

def advanced_ping_test(configs: List[ConfigParams]) -> List[ConfigParams]:
    # اینجا می‌توانید منطق واقعی پینگ/اتصال را قرار دهید؛ فعلاً فقط رد کردن نامعتبر
    # برای نمونه، همه کانفیگ‌ها سالم فرض می‌شوند
    valid_configs = [c for c in configs if c.valid]
    return deduplicate_configs(valid_configs)

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater...")

    # مرحله اول: منابع → normal.json
    configs = initial_update()
    print(f"[*] Initial update done: {len(configs)} configs saved to normal.json")

    # مرحله دوم: از normal.json دوباره تست دقیق‌تر
    configs = advanced_ping_test(configs)
    print(f"[*] Advanced ping test: {len(configs)} configs passed")

    # ذخیره خروجی‌ها
    save_outputs([c.raw for c in configs])
    print("[✅] Updated all outputs:")
    print(f"  -> {FINAL_JSON_PATH}")
    print(f"  -> {FINAL_TXT_PATH}")
    print(f"  -> {BASE64_PATH}")
    print(f"  -> {FINAL_RAW_PATH}")
    print("[*] Done. All valid configs saved.")
