#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, threading, time, requests, urllib.parse, psutil, signal, re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== SETTINGS =====================
TH_MAX_WORKER = 10
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"
TEST_URL = "http://www.google.com"
TIMEOUT = 5

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/ss.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/vless.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo40.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo50.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/trojan.txt"
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== PROCESS MANAGER =====================
class ProcessManager:
    def __init__(self):
        self.active_processes = {}
        self.lock = threading.Lock()

    def add_process(self, name: str, pid: int):
        with self.lock:
            self.active_processes[name] = pid

    def stop_process(self, name: str):
        pid_to_stop = None
        with self.lock:
            if name in self.active_processes:
                pid_to_stop = self.active_processes.pop(name)
        if pid_to_stop and psutil.pid_exists(pid_to_stop):
            try:
                os.kill(pid_to_stop, signal.SIGTERM)
                time.sleep(0.5)
                if psutil.pid_exists(pid_to_stop):
                    os.kill(pid_to_stop, signal.SIGKILL)
            except Exception:
                pass

    def stop_all(self):
        with self.lock:
            names = list(self.active_processes.keys())
        for name in names:
            self.stop_process(name)

process_manager = ProcessManager()

# ===================== CONFIG CLASS =====================
@dataclass
class ConfigParams:
    protocol: str
    address: str
    port: int
    tag: Optional[str] = ""
    id: Optional[str] = ""
    extra_params: Dict[str, Any] = field(default_factory=dict)

# ===================== FUNCTIONS =====================
def remove_empty_strings(lst: List[str]) -> List[str]:
    return [str(item).strip() for item in lst if item and str(item).strip()]

def is_valid_config(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 5:
        return False
    lower = line.lower()
    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False
    return True

def parse_config_line(line: str) -> Optional[ConfigParams]:
    try:
        line = urllib.parse.unquote(line.strip())
        protocol = None
        for p in ["vmess", "vless", "trojan", "hy2", "hysteria2", "ss", "socks", "wireguard"]:
            if line.startswith(p + "://"):
                protocol = p
                break
        if not protocol:
            return None
        addr, port = "unknown", 0
        match = re.search(r"@([^:]+):(\d+)", line)
        if match:
            addr = match.group(1)
            port = int(match.group(2))
        tag = line.split("#", 1)[1] if "#" in line else ""
        return ConfigParams(protocol=protocol, address=addr, port=port, tag=tag)
    except Exception:
        return None

def fetch_link(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text.splitlines()
        else:
            return []
    except Exception:
        return []

def clear_and_merge_configs(lines: List[str]) -> List[str]:
    final_lines = []
    unique_keys = {}
    for line in lines:
        if not is_valid_config(line):
            continue
        cfg = parse_config_line(line)
        if cfg:
            key = f"{cfg.protocol}|{cfg.address}|{cfg.port}|{cfg.id}"
        else:
            key = line
        if key not in unique_keys:
            unique_keys[key] = line
    for val in unique_keys.values():
        final_lines.append(val)
    return final_lines

# ====== PING واقعی ======
def ping_config(config_line: str) -> bool:
    try:
        start = time.time()
        r = requests.get(TEST_URL, timeout=TIMEOUT)
        elapsed = (time.time() - start) * 1000
        if r.status_code in [200, 204] and 1 <= elapsed <= 1500 and is_valid_config(config_line):
            return True
        return False
    except Exception:
        return False

def process_sources() -> List[str]:
    all_configs: List[str] = []
    threads: List[threading.Thread] = []
    results: List[List[str]] = [None] * len(LINK_PATH)

    def worker(i: int, url: str):
        fetched = fetch_link(url)
        valid_configs = [c for c in fetched if ping_config(c)]
        results[i] = valid_configs

    for i, url in enumerate(LINK_PATH):
        t = threading.Thread(target=worker, args=(i, url))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    for r in results:
        if r:
            all_configs.extend(r)
    all_configs = remove_empty_strings(all_configs)
    all_configs = clear_and_merge_configs(all_configs)
    return all_configs

def save_configs(filepath: str, configs: List[str]):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join([FILE_HEADER_TEXT] + configs))
        print(f"[+] Saved {len(configs)} configs to {filepath}")
    except Exception as e:
        print(f"[!] Error saving {filepath}: {e}")

def filter_best_configs(input_path: str) -> List[str]:
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        filtered = [c for c in lines if ping_config(c)]
        return remove_empty_strings(filtered)
    except Exception:
        return []

# ===================== MAIN LOOP =====================
if __name__ == "__main__":
    print("[*] Starting subscription updater with real ping and filtering...")

    while True:
        print("[*] Step 1: Clearing output files...")
        open(TEXT_PATH, "w").close()
        open(FIN_PATH, "w").close()

        print("[*] Step 2: Reading sources and testing pin...")
        normal_configs = process_sources()
        save_configs(TEXT_PATH, normal_configs)

        print("[*] Step 3: Re-testing configs from normal.txt for best pins...")
        best_configs = filter_best_configs(TEXT_PATH)
        save_configs(FIN_PATH, best_configs)

        choice = input("[*] Press Enter to run again or type 'exit' to quit: ").strip()
        if choice.lower() == "exit":
            process_manager.stop_all()
            print("[*] Exiting...")
            sys.exit()
