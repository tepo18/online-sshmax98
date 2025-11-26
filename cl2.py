#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import threading
import time
import requests
import base64
import urllib.parse
import socket
from typing import List

# ===================== تنظیمات =====================
TEXT_PATH = "normal2.txt"
FIN_PATH = "final2.txt"

LINK_PATH = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/refs/heads/main/Sub5.txt",
    "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/splitted/ss",
    "https://raw.githubusercontent.com/Surfboardv2ray/TGParse/main/splitted/trojan",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/ss.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/trojan.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Splitted-By-Protocol/vmess.txt",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/tuic",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/hysteria",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/juicity",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/reality",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/shadowsocks",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/trojan",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/vless",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/refs/heads/main/channels/protocols/vmess",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub6.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub7.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub8.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub9.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub10.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list1.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list2.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list3.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list4.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list5.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list6.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Config%20list7.txt",
    "https://azadnet05.pages.dev/sub/4d794980-54c0-4fcb-8def-c2beaecadbad#EN-Normal",
    "https://raw.githubusercontent.com/iPsycho1/Subscription/refs/heads/main/iPsycho_Multi_Location",
    "https://raw.githubusercontent.com/rango-cfs/NewCollector/refs/heads/main/v2ray_links.txt",
    "https://elena.com.co/ELiV2-RAY-Sublink.txt",
    "https://raw.githubusercontent.com/AB-84-AB/Free-Shadowsocks/refs/heads/main/Telegram-id-AB_841",
    "https://raw.githubusercontent.com/SoliSpirit/v2ray-configs/refs/heads/main/all_configs.txt"
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== توابع =====================

def fetch_link(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            lines = r.text.splitlines()
            return [l.strip() for l in lines if l.strip()]
    except Exception as e:
        print(f"[⚠️] Cannot fetch {url}: {e}")
    return []

def is_valid_config(line: str) -> bool:
    line = line.strip()
    if not line or len(line) < 5:
        return False
    lower = line.lower()
    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False
    return True

def parse_config_line(line: str):
    try:
        line = urllib.parse.unquote(line.strip())
        for p in ["vmess", "vless", "trojan", "hy2", "hysteria2", "ss", "socks", "wireguard"]:
            if line.startswith(p + "://"):
                return line
    except:
        pass
    return None

def tcp_test(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def process_configs(lines: List[str], precise_test=False) -> List[str]:
    valid_configs = []
    lock = threading.Lock()

    def worker(line):
        cfg = parse_config_line(line)
        passed = False

        if cfg:
            try:
                import re
                m = re.search(r"@([^:]+):(\d+)", cfg)
                host, port = (m.group(1), int(m.group(2))) if m else ("", 443)

                if precise_test and host:
                    passed = tcp_test(host, port)
                else:
                    passed = True
            except:
                passed = False

        if passed and is_valid_config(line):
            with lock:
                valid_configs.append(line)

    threads = []
    for line in lines:
        t = threading.Thread(target=worker, args=(line,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # حذف تکراری
    final_list = list(dict.fromkeys(valid_configs))
    return final_list

def save_outputs(lines: List[str]):
    try:
        # ابتدا فایل‌ها را خالی می‌کنیم
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("")
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("")

        # مرحله نرمال
        normal_lines = lines
        with open(TEXT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join([FILE_HEADER_TEXT] + normal_lines))
        print(f"[ℹ️] Stage 1: {len(normal_lines)} configs saved to {TEXT_PATH}")

        # مرحله فینال با تست دقیق
        final_lines = process_configs(normal_lines, precise_test=True)
        with open(FIN_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(final_lines))
        print(f"[ℹ️] Stage 2: {len(final_lines)} configs saved to {FIN_PATH}")

        print(f"[✅] Update complete. Total sources: {len(lines)}")
        print(f"  -> Normal2 configs: {len(normal_lines)}")
        print(f"  -> Final2 configs: {len(final_lines)}")

    except Exception as e:
        print(f"[❌] Error saving files: {e}")

def update_subs():
    all_lines = []

    for url in LINK_PATH:
        fetched = fetch_link(url)
        if not fetched:
            print(f"[⚠️] Cannot fetch or empty source: {url}")
        else:
            all_lines.extend(fetched)

    print(f"[*] Total lines fetched from sources: {len(all_lines)}")
    all_lines = process_configs(all_lines)
    save_outputs(all_lines)

# ===================== اجرای دستی =====================
if __name__ == "__main__":
    print("[*] Starting manual subscription update...")
    update_subs()
    print("[*] Done. Run this script manually whenever needed.")
