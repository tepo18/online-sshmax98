#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import base64
import urllib.request
import urllib.parse
import socket
import threading
import subprocess
import time
from typing import List

# ===================== Paths & Settings =====================
NORMAL_PATH = "normal.txt"
FINAL_TXT = "final.txt"
BASE64_TXT = "base64.txt"
FINAL_RAW = "final.raw"

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.txt",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="
THREADS = 10

# ===================== Helper Functions =====================
def fetch_subs(url: str) -> List[str]:
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            content = resp.read().decode()
        return [line.strip() for line in content.splitlines() if line.strip()]
    except:
        return []

def remove_empty_strings(lst: List[str]) -> List[str]:
    return [x for x in lst if x and x.strip()]

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
    return line

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

def precise_test(line: str) -> bool:
    parsed = parse_config_line(line)
    if isinstance(parsed, dict):
        host = parsed.get("add") or parsed.get("server")
        port = int(parsed.get("port", 443))
        if host:
            return tcp_test(host, port) and ping_test(host) and http_test(f"https://{host}")
    return True

def process_configs(lines: List[str], precise=False) -> List[str]:
    valid_configs = []
    lock = threading.Lock()

    def worker(line):
        passed = precise_test(line) if precise else tcp_test(parse_config_line(line).get("add", "127.0.0.1"), parse_config_line(line).get("port", 443)) if isinstance(parse_config_line(line), dict) else True
        if passed:
            with lock:
                valid_configs.append(line)

    threads_list = []
    for line in lines:
        while threading.active_count() > THREADS:
            time.sleep(0.01)
        t = threading.Thread(target=worker, args=(line,))
        t.start()
        threads_list.append(t)

    for t in threads_list:
        t.join()

    return clear_and_unique(valid_configs)

def save_outputs(configs: List[str]):
    try:
        with open(FINAL_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        b64_lines = [base64.b64encode(line.encode()).decode() for line in configs]
        with open(BASE64_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(b64_lines))
        with open(FINAL_RAW, "w", encoding="utf-8") as f:
            f.write("\n".join(configs))
        with open(NORMAL_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join([FILE_HEADER_TEXT]+configs))
        print(f"[✅] Saved outputs ({len(configs)} configs):")
        print(f"  -> {FINAL_TXT}")
        print(f"  -> {BASE64_TXT}")
        print(f"  -> {FINAL_RAW}")
        print(f"  -> {NORMAL_PATH}")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Fetching configs from sources...")
    all_lines = []
    for url in LINK_PATH:
        subs = fetch_subs(url)
        all_lines.extend(subs)

    print(f"[*] {len(all_lines)} lines fetched. Clearing duplicates...")
    all_lines = clear_and_unique(all_lines)

    # مرحله اول: ذخیره اولیه در normal.txt و تست سریع TCP
    normal_configs = process_configs(all_lines, precise=False)
    with open(NORMAL_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join([FILE_HEADER_TEXT]+normal_configs))
    print(f"[*] {len(normal_configs)} configs saved to {NORMAL_PATH} (preliminary)")

    # مرحله دوم: تست دقیق‌تر از normal.txt
    print("[*] Running precise tests (TCP+Ping+HTTP) on normal configs...")
    final_configs = process_configs(normal_configs, precise=True)
    save_outputs([FILE_HEADER_TEXT]+final_configs)
    print("[*] Done. All valid configs saved.")
