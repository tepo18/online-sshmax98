#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.request
import urllib.parse
import base64
import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ===================== Paths & Settings =====================
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"

LINK_PATH = [
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/online-sshmax98/main/tepo30.txt",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== Config Class =====================
@dataclass
class ConfigParams:
    protocol: str
    address: str
    port: int
    tag: str = ""
    id: str = ""
    extra_params: Dict[str, Any] = field(default_factory=dict)

# ===================== Helper Functions =====================
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
            return ConfigParams(
                protocol="vmess",
                address=data.get("add", ""),
                port=int(data.get("port", 0)),
                id=data.get("id", ""),
                tag=data.get("ps", "")
            )
        elif line.startswith("vless://") or line.startswith("trojan://") or line.startswith("hy2://") or line.startswith("hysteria://"):
            parts = line.split("://")[1].split("@")
            if len(parts) == 2:
                uid, addrport = parts
                addr, port = addrport.split(":")
                proto = line.split("://")[0]
                return ConfigParams(protocol=proto, id=uid, address=addr, port=int(port))
        elif line.startswith("ss://") or line.startswith("socks://") or line.startswith("wireguard://"):
            proto = line.split("://")[0]
            return ConfigParams(protocol=proto, address=line, port=0)
        return None
    except Exception:
        return None

def fetch_subs(url: str) -> List[str]:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            content = resp.read().decode()
        return content.splitlines()
    except Exception:
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
    all_configs.insert(0, FILE_HEADER_TEXT)

    try:
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_configs))
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(all_configs))
        print(f"[✅] Updated {FIN_PATH} with {len(all_configs)} lines")
    except Exception as e:
        print(f"[❌] Error saving files: {e}")

# ===================== Main =====================
if __name__ == "__main__":
    print("[*] Starting full-feature subscription updater...")
    update_subscriptions()
    print("[*] Done. All valid configs saved.")
