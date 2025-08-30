#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import base64
import threading
import urllib.request
from typing import List, Dict, Any

# ===================== Paths & Settings =====================
LINKS = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.json",
]

FINAL_JSON = "final.json"
FINAL_TXT = "final3.txt"
BASE64_TXT = "base64.txt"
FINAL_RAW = "final.raw"
FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== Helper Functions =====================
def fetch_json(url: str) -> List[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list):
                return data
    except:
        pass
    return []

def validate_config(cfg: Dict[str, Any]) -> bool:
    if not cfg:
        return False
    if "remarks" not in cfg or "outbounds" not in cfg:
        return False
    return True

def config_to_base64(cfg: Dict[str, Any]) -> str:
    raw_json = json.dumps(cfg, ensure_ascii=False)
    return base64.b64encode(raw_json.encode()).decode()

# ===================== Main Update Function =====================
def update_configs():
    all_configs: List[Dict[str, Any]] = []
    threads = []
    results: List[List[Dict[str, Any]]] = [None] * len(LINKS)

    def worker(i, url):
        results[i] = fetch_json(url)

    for i, url in enumerate(LINKS):
        t = threading.Thread(target=worker, args=(i, url))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    for r in results:
        if r:
            for cfg in r:
                if validate_config(cfg):
                    all_configs.append(cfg)

    # حذف تکراری بر اساس remarks
    unique = {}
    for cfg in all_configs:
        key = cfg.get("remarks", "")
        if key not in unique:
            unique[key] = cfg
    final_list = list(unique.values())

    # --- ذخیره final.json ---
    with open(FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)

    # --- ذخیره final3.txt ---
    with open(FINAL_TXT, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER_TEXT + "\n")
        for cfg in final_list:
            f.write(json.dumps(cfg, ensure_ascii=False) + "\n")

    # --- ذخیره base64.txt ---
    with open(BASE64_TXT, "w", encoding="utf-8") as f:
        for cfg in final_list:
            f.write(config_to_base64(cfg) + "\n")

    # --- ذخیره final.raw ---
    with open(FINAL_RAW, "w", encoding="utf-8") as f:
        for cfg in final_list:
            f.write(json.dumps(cfg, ensure_ascii=False) + "\n")

    print(f"[✅] Updated all outputs ({len(final_list)} configs)")
    print(f"  -> {FINAL_JSON}")
    print(f"  -> {FINAL_TXT}")
    print(f"  -> {BASE64_TXT}")
    print(f"  -> {FINAL_RAW}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater with raw output...")
    update_configs()
    print("[*] Done. All valid configs saved.")
