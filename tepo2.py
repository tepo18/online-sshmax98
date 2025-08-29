#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import base64
import threading
import signal
import psutil
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

# ===================== تنظیمات =====================
CONF_PATH = "config1.json"
TEXT_PATH = "normal1.txt"
FIN_PATH = "final1.txt"
LINK_PATH = [
    "https://raw.githubusercontent.com/sab-vip10/tepo40.txt",
    "https://raw.githubusercontent.com/sab-vip10/tepo50.txt",
    "https://raw.githubusercontent.com/sab-vip10/tepo60.txt"
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== مدیریت پردازش =====================
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
            pid_to_stop = self.active_processes.pop(name, None)
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
            for name in list(self.active_processes.keys()):
                self.stop_process(name)

process_manager = ProcessManager()

# ===================== کلاس کانفیگ =====================
@dataclass
class ConfigParams:
    protocol: str
    address: str
    port: int
    tag: Optional[str] = ""
    id: Optional[str] = ""
    extra_params: Dict[str, Any] = field(default_factory=dict)

# ===================== توابع =====================
def remove_empty_strings(lst: List[str]) -> List[str]:
    return [str(x).strip() for x in lst if x and str(x).strip()]

def parse_config_line(line: str) -> Optional[ConfigParams]:
    try:
        line = urllib.parse.unquote(line.strip())
        if line.startswith("vmess://"):
            encoded = line.split("://")[1]
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += "=" * (4 - missing_padding)
            data = json.loads(base64.b64decode(encoded).decode())
            return ConfigParams(
                protocol="vmess",
                address=data.get("add"),
                port=int(data.get("port", 0)),
                id=data.get("id", ""),
                tag=data.get("ps", "")
            )
        elif line.startswith("vless://"):
            parts = line.split("://")[1].split("@")
            if len(parts) == 2:
                uid, addrport = parts
                addr, port = addrport.split(":")
                return ConfigParams(protocol="vless", id=uid, address=addr, port=int(port))
        elif line.startswith("trojan://"):
            parts = line.split("://")[1].split("@")
            if len(parts) == 2:
                pwd, addrport = parts
                addr, port = addrport.split(":")
                return ConfigParams(protocol="trojan", id=pwd, address=addr, port=int(port))
        elif line.startswith("hy2://") or line.startswith("hysteria://"):
            parts = line.split("://")[1].split("@")
            if len(parts) == 2:
                pwd, addrport = parts
                addr, port = addrport.split(":")
                return ConfigParams(protocol="hy2", id=pwd, address=addr, port=int(port))
        elif line.startswith("ss://"):
            return ConfigParams(protocol="ss", address=line, port=0)
        elif line.startswith("socks://"):
            return ConfigParams(protocol="socks", address=line, port=0)
        elif line.startswith("wireguard://"):
            return ConfigParams(protocol="wireguard", address=line, port=0)
        return None
    except Exception:
        return None

def clear_and_unique(configs: List[str]) -> List[str]:
    unique = {}
    for line in configs:
        line = line.strip()
        if not line:
            continue
        key = line.split("#")[0]
        if key not in unique:
            unique[key] = line
    return remove_empty_strings(list(unique.values()))

def fetch_subs(url: str) -> List[str]:
    try:
        with urllib.request.urlopen(url) as resp:
            content = resp.read().decode()
        return content.splitlines()
    except:
        return []

def update_subscriptions():
    all_configs = []
    for url in LINK_PATH:
        lines = fetch_subs(url)
        for line in lines:
            if parse_config_line(line):
                all_configs.append(line)
    all_configs = clear_and_unique(all_configs)
    all_configs.insert(0, FILE_HEADER_TEXT)

    try:
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_configs))
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_configs))
        print(f"[✅] Updated {FIN_PATH} with {len(all_configs)} lines")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== حلقه اصلی =====================
if __name__ == "__main__":
    print("[*] Starting full-feature subscription updater...")
    update_subscriptions()
    print("[*] Next update in 60 minutes...")
