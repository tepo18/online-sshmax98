#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request
from dataclasses import dataclass
from typing import List, Dict, Any
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== Paths & Settings =====================
FIN_PATH = "final.json"  # خروجی فقط در ریپو
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
    remark: str

# ===================== Helper Functions =====================
def fetch_json(url: str) -> List[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            content = resp.read().decode()
        data = json.loads(content)
        return data if isinstance(data, list) else []
    except:
        return []

def validate_config(cfg: Dict[str, Any]) -> bool:
    return bool(cfg and "remarks" in cfg and "outbounds" in cfg)

def test_tcp(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def extract_server_port(cfg: Dict[str, Any]):
    try:
        out = cfg.get("outbounds", [])
        if not out:
            return None, None
        vnext = out[0].get("settings", {}).get("vnext", [])
        if not vnext:
            return None, None
        server = vnext[0].get("address", "")
        port = vnext[0].get("port", 0)
        return server, port
    except:
        return None, None

# ===================== Main Update Function =====================
def update_subs():
    # --- دانلود کانفیگ‌ها ---
    all_configs: List[ConfigParams] = []
    for url in LINK_PATH:
        data = fetch_json(url)
        for cfg in data:
            if validate_config(cfg):
                all_configs.append(ConfigParams(raw=cfg, remark=cfg.get("remarks", "")))

    # --- حذف تکراری‌ها ---
    unique = {cfg.remark: cfg for cfg in all_configs}
    final_candidates = [cfg.raw for cfg in unique.values()]

    # --- تست TCP همزمان ---
    final_list = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_cfg = {}
        for cfg in final_candidates:
            server, port = extract_server_port(cfg)
            if server and port:
                future = executor.submit(test_tcp, server, port)
                future_to_cfg[future] = cfg

        for future in as_completed(future_to_cfg):
            cfg = future_to_cfg[future]
            try:
                if future.result():
                    final_list.append(cfg)
            except:
                continue

    # --- اضافه کردن هدر ---
    output_list = [FILE_HEADER_TEXT] + final_list

    # --- ذخیره نهایی ---
    try:
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            json.dump(output_list, f, indent=4, ensure_ascii=False)
        print(f"[✅] Updated {FIN_PATH} ({len(final_list)} configs passed TCP test)")
    except Exception as e:
        print(f"[❌] Error saving file: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting JSON subscription updater with TCP test (multi-threaded)...")
    update_subs()
    print("[*] Done. All valid configs saved.")
