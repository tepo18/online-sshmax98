#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import base64
import threading
import signal
import psutil
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

CONF_PATH = "config.json"
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"
LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.txt"
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

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
                time.sleep(1)
                if psutil.pid_exists(pid_to_stop):
                    os.kill(pid_to_stop, signal.SIGKILL)
            except Exception as e:
                print(f"Error stopping process {name}: {e}")

    def stop_all(self):
        with self.lock:
            for name in list(self.active_processes.keys()):
                self.stop_process(name)

process_manager = ProcessManager()

@dataclass
class ConfigParams:
    protocol: str
    address: str
    port: int
    security: str = ""
    encryption: str = "none"
    network: str = "tcp"
    id: str = ""
    tag: str = ""
    path: str = None
    host: str = None
    extra_params: Dict[str, Any] = field(default_factory=dict)

def remove_empty_strings(lst: List[str]) -> List[str]:
    return [str(x).strip() for x in lst if x and str(x).strip()]

def clear_and_unique(configs: List[str]) -> List[str]:
    unique = {}
    for line in configs:
        line = line.strip()
        if not line:
            continue
        key = line.split('#')[0]
        if key not in unique:
            unique[key] = line
    return remove_empty_strings(list(unique.values()))

def parse_config_line(line: str) -> Optional[ConfigParams]:
    try:
        line = urllib.parse.unquote(line.strip())
        if line.startswith("vmess://"):
            encoded = line.split("://")[1]
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += '=' * (4 - missing_padding)
            data = json.loads(base64.b64decode(encoded).decode())
            return ConfigParams(protocol="vmess", address=data.get("add"), port=int(data.get("port",0)), id=data.get("id",""), tag=data.get("ps",""))
        elif line.startswith("vless://"):
            parts = line.split("://")[1].split("@")
            if len(parts)==2:
                uid, addrport = parts
                addr, port = addrport.split(":")
                return ConfigParams(protocol="vless", id=uid, address=addr, port=int(port))
        elif line.startswith("trojan://"):
            parts = line.split("://")[1].split("@")
            if len(parts)==2:
                pwd, addrport = parts
                addr, port = addrport.split(":")
                return ConfigParams(protocol="trojan", id=pwd, address=addr, port=int(port))
        elif line.startswith("hy2://") or line.startswith("hysteria://"):
            parts = line.split("://")[1].split("@")
            if len(parts)==2:
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
            parsed = parse_config_line(line)
            if parsed:
                all_configs.append(line)
    all_configs = clear_and_unique(all_configs)
    with open(TEXT_PATH,"w",encoding="utf-8") as f:
        f.write(FILE_HEADER_TEXT+"\n")
        f.write("\n".join(all_configs))
    with open(FIN_PATH,"w",encoding="utf-8") as f:
        f.write(FILE_HEADER_TEXT+"\n")
        f.write("\n".join(all_configs))
    print(f"[+] Updated {FIN_PATH} with {len(all_configs)} lines")

if __name__=="__main__":
    print("[*] Starting full-feature subscription updater...")
    update_subscriptions()
    print("[*] Next update in 60 minutes...")
