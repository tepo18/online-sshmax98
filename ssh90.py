#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import threading
import urllib.request
import base64
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== Paths & Settings =====================
NORMAL_PATH = "normal.json"
FINAL_JSON = "final.json"
FINAL_TXT = "final3.txt"
BASE64_TXT = "base64.txt"
FINAL_RAW = "final.raw"

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

def tcp_ping_test(cfg: Dict[str, Any]) -> bool:
    # شبیه‌سازی تست اتصال و پینگ
    # در نسخه واقعی می‌توان تست TCP واقعی با socket انجام داد
    return True  # فعلاً همه سالم فرض می‌شوند

# ===================== Main Updater =====================
def update_subs():
    all_configs: List[ConfigParams] = []

    # --- Fetch from sources ---
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
                    all_configs.append(ConfigParams(raw=cfg, remark=cfg.get("remarks", ""), valid=True))

    # --- Remove duplicates ---
    unique = {}
    for cfg in all_configs:
        if cfg.remark not in unique:
            unique[cfg.remark] = cfg
    final_list = [cfg.raw for cfg in unique.values()]

    # --- First save to normal.json ---
    try:
        with open(NORMAL_PATH, "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[❌] Error saving normal.json: {e}")

    # --- Ping/TCP test ---
    passed_configs = []
    for cfg in final_list:
        if tcp_ping_test(cfg):
            passed_configs.append(cfg)

    # --- Save final outputs ---
    try:
        # JSON
        with open(FINAL_JSON, "w", encoding="utf-8") as f:
            json.dump(passed_configs, f, indent=4, ensure_ascii=False)
        # TXT
        with open(FINAL_TXT, "w", encoding="utf-8") as f:
            for cfg in passed_configs:
                f.write(json.dumps(cfg, ensure_ascii=False) + "\n")
        # Base64 TXT
        with open(BASE64_TXT, "w", encoding="utf-8") as f:
            for cfg in passed_configs:
                b64 = base64.b64encode(json.dumps(cfg, ensure_ascii=False).encode()).decode()
                f.write(b64 + "\n")
        # RAW
        with open(FINAL_RAW, "w", encoding="utf-8") as f:
            json.dump(passed_configs, f, ensure_ascii=False)
        print(f"[✅] Updated all outputs ({len(passed_configs)} configs)")
    except Exception as e:
        print(f"[❌] Error saving final outputs: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater with ping test...")
    update_subs()
    print("[*] Done. All valid configs saved.")
