#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, base64, threading, urllib.request, subprocess, time, platform
from typing import List, Dict

# ---------------- مسیرها ----------------
TEXT_JSON = "final.json"
TEXT_TXT = "final3.txt"
TEXT_BASE64 = "base64.txt"
TEXT_RAW = "final.raw"

LINKS_RAW = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.json",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.json",
]

FILE_HEADER = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ---------------- دریافت JSON ----------------
def fetch_json(url: str) -> List[Dict]:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return data if isinstance(data, list) else []
    except:
        return []

# ---------------- اعتبارسنجی ----------------
def validate_config(cfg: Dict) -> bool:
    return bool(cfg and "remarks" in cfg and "outbounds" in cfg)

# ---------------- Ping واقعی ----------------
def ping(host: str, count: int = 1, timeout: int = 1000) -> float:
    param_count = "-n" if platform.system().lower()=="windows" else "-c"
    param_timeout = "-w" if platform.system().lower()=="windows" else "-W"
    try:
        cmd = ["ping", param_count, str(count), param_timeout, str(timeout), host]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        # استخراج زمان از خروجی ping
        import re
        match = re.search(r'time[=<]\s*(\d+\.?\d*)', output)
        if match:
            return float(match.group(1))
    except:
        pass
    return float('inf')

# ---------------- پردازش کانفیگ‌ها ----------------
def process_configs(configs: List[Dict], max_threads=20) -> List[Dict]:
    results = []
    lock = threading.Lock()
    threads = []

    def worker(cfg):
        outbounds = cfg.get("outbounds", [])
        if outbounds:
            address = outbounds[0].get("settings", {}).get("vnext", [{}])[0].get("address")
            port = outbounds[0].get("settings", {}).get("vnext", [{}])[0].get("port", 443)
            if address and port:
                ping_time = ping(address)
                if ping_time < float('inf'):
                    with lock:
                        cfg["_ping"] = ping_time
                        results.append(cfg)

    for cfg in configs:
        t = threading.Thread(target=worker, args=(cfg,))
        threads.append(t)
        t.start()
        if len(threads) >= max_threads:
            for th in threads: th.join()
            threads = []
    for t in threads: t.join()

    # حذف تکراری و مرتب‌سازی بر اساس ping
    unique = {}
    for cfg in results:
        key = cfg.get("remarks")
        if key not in unique:
            unique[key] = cfg
    final_list = list(unique.values())
    final_list.sort(key=lambda x: x.get("_ping", float('inf')))
    return final_list

# ---------------- ذخیره فایل ----------------
def save_files(configs: List[Dict]):
    os.makedirs(os.path.dirname(os.path.abspath(TEXT_JSON)), exist_ok=True)
    for cfg in configs: cfg.pop("_ping", None)  # حذف زمان ping قبل ذخیره
    with open(TEXT_JSON, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4, ensure_ascii=False)
    with open(TEXT_TXT, "w", encoding="utf-8") as f:
        for cfg in configs:
            f.write(json.dumps(cfg, ensure_ascii=False) + "\n")
    with open(TEXT_BASE64, "w", encoding="utf-8") as f:
        for cfg in configs:
            f.write(base64.b64encode(json.dumps(cfg, ensure_ascii=False).encode()).decode() + "\n")
    with open(TEXT_RAW, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER + "\n")
        json.dump(configs, f, ensure_ascii=False)

# ---------------- بروزرسانی ----------------
def update_all():
    all_configs = []

    threads = []
    results = [None] * len(LINKS_RAW)

    def worker(i, url):
        results[i] = fetch_json(url)

    for i, url in enumerate(LINKS_RAW):
        t = threading.Thread(target=worker, args=(i,url))
        threads.append(t)
        t.start()
    for t in threads: t.join()

    for r in results:
        if r:
            for cfg in r:
                if validate_config(cfg):
                    all_configs.append(cfg)

    final_configs = process_configs(all_configs)
    save_files(final_configs)
    print(f"[✅] Updated all outputs ({len(final_configs)} configs)")
    print(f" -> {TEXT_JSON}\n -> {TEXT_TXT}\n -> {TEXT_BASE64}\n -> {TEXT_RAW}")

# ---------------- Main ----------------
if __name__ == "__main__":
    print("[*] Starting full-feature JSON subscription updater with Ping test...")
    start = time.time()
    update_all()
    print(f"[*] Done. Time elapsed: {time.time() - start:.2f}s")
