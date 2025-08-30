#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import base64
import urllib.request
import urllib.parse
import socket
import threading
import time
import subprocess
from typing import List

# ===================== Paths & Settings =====================
NORMAL_PATH = "normal.txt"
FINAL_TXT = "final.txt"
BASE64_TXT = "final64.txt"
FINAL_RAW = "final64.raw"

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.txt",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== Helper Functions =====================
def fetch_subs(url: str) -> List[str]:
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            content = resp.read().decode()
        return [line.strip() for line in content.splitlines() if line.strip()]
    except Exception:
        return []

def clear_and_unique(configs: List[str]) -> List[str]:
    unique = {}
    for line in configs:
        key = line.split('#')[0].strip()
        if key not in unique:
            unique[key] = line.strip()
    return list(unique.values())

def parse_config_line(line: str):
    line = urllib.parse.unquote(line.strip())
    if line.startswith("vmess://"):
        encoded = line[7:]
        padding = len(encoded) % 4
        if padding:
            encoded += "=" * (4 - padding)
        try:
            data = json.loads(base64.b64decode(encoded).decode())
            return data
        except:
            return None
    return line  # بقیه پروتکل‌ها بدون تغییر باقی می‌مانند

def tcp_test(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def ping_test(host: str, count: int = 1, timeout: int = 1000) -> bool:
    try:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def http_test(url: str, timeout=5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except:
        return False

def process_configs(lines: List[str]) -> List[str]:
    valid_configs = []
    lock = threading.Lock()

    def worker(line):
        parsed = parse_config_line(line)
        passed = False
        if isinstance(parsed, dict):
            host = parsed.get("add") or parsed.get("server")
            port = int(parsed.get("port", 443))
            if host and tcp_test(host, port) and ping_test(host) and http_test(f"https://{host}"):
                passed = True
        else:
            # برای پروتکل‌های دیگر بدون بررسی TCP مستقیم، فقط اضافه می‌کنیم
            passed = True

        if passed:
            with lock:
                valid_configs.append(line)

    threads = []
    for line in lines:
        t = threading.Thread(target=worker, args=(line,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    return clear_and_unique(valid_configs)

def save_outputs(configs: List[str]):
    try:
        # ذخیره normal.txt
        with open(NORMAL_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        # ذخیره final.txt
        with open(FINAL_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        # ذخیره base64.txt
        b64_lines = [base64.b64encode(line.encode()).decode() for line in configs]
        with open(BASE64_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(b64_lines))
        # ذخیره final.raw
        with open(FINAL_RAW, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        print(f"[✅] Updated all outputs ({len(configs)} configs)")
        print(f"  -> {FINAL_TXT}")
        print(f"  -> {BASE64_TXT}")
        print(f"  -> {FINAL_RAW}")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature subscription updater with TCP, ping, HTTP/HTTPS tests...")
    all_lines = []
    for url in LINK_PATH:
        subs = fetch_subs(url)
        all_lines.extend(subs)

    print(f"[*] Fetched {len(all_lines)} lines from sources.")
    valid_lines = process_configs(all_lines)
    print(f"[*] {len(valid_lines)} configs passed all tests.")

    save_outputs([FILE_HEADER_TEXT] + valid_lines)
    print("[*] Done. All valid configs saved.")
