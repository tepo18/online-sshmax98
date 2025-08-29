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

# ========================== Paths & Settings ==========================
CONF_PATH = "config.json"
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"
UPDATE_INTERVAL = 60 * 60  # هر 60 دقیقه

LINK_PATH = [
    "https://raw.githubusercontent.com/sab-vip10/tepo10.txt",
    "https://raw.githubusercontent.com/sab-vip10/tepo20.txt",
    "https://raw.githubusercontent.com/sab-vip10/tepo30.txt"
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ========================== Process Manager ==========================
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
        if pid_to_stop is None:
            return
        try:
            if psutil.pid_exists(pid_to_stop):
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

# ========================== Config Classes ==========================
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
    path: Optional[str] = None
    host: Optional[str] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)

# ========================== Helper Functions ==========================
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

# ========================== Config Parser ==========================
def safe_parse_config_line(line: str) -> Optional[ConfigParams]:
    line = line.strip()
    if not line:
        return None
    try:
        decoded_line = urllib.parse.unquote(line)
        if decoded_line.startswith("vmess://"):
            encoded = decoded_line.split("://")[1]
            missing_padding = len(encoded) % 4
            if missing_padding:
                encoded += "=" * (4 - missing_padding)
            data = json.loads(base64.b64decode(encoded).decode("utf-8"))
            return ConfigParams(
                protocol="vmess",
                address=data.get("add"),
                port=int(data.get("port", 0)),
                id=data.get("id"),
                tag=data.get("ps", "")
            )
        elif decoded_line.startswith("vless://") or decoded_line.startswith("trojan://") or decoded_line.startswith("hy2://") or decoded_line.startswith("hysteria://"):
            return ConfigParams(protocol=decoded_line.split("://")[0], address=decoded_line, port=0)
        elif decoded_line.startswith("ss://") or decoded_line.startswith("socks://") or decoded_line.startswith("wireguard://"):
            return ConfigParams(protocol=decoded_line.split("://")[0], address=decoded_line, port=0)
    except Exception:
        return None

# ========================== Fetch & Update ==========================
def fetch_subs(url: str) -> List[str]:
    try:
        with urllib.request.urlopen(url) as resp:
            content = resp.read().decode()
        return content.splitlines()
    except:
        return []

def update_subscriptions():
    all_lines = []
    for url in LINK_PATH:
        lines = fetch_subs(url)
        all_lines.extend(lines)

    valid_lines = []
    for line in all_lines:
        parsed = safe_parse_config_line(line)
        if parsed:
            valid_lines.append(line)

    # حذف تکراری و مرتب‌سازی
    valid_lines = sorted(list(dict.fromkeys(valid_lines)))

    with open(TEXT_PATH, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER_TEXT + "\n")
        f.write("\n".join(valid_lines))

    with open(FIN_PATH, "w", encoding="utf-8") as f:
        f.write(FILE_HEADER_TEXT + "\n")
        f.write("\n".join(valid_lines))

    print(f"[+] Updated {FIN_PATH} with {len(valid_lines)} valid lines")

# ========================== Auto Update Thread ==========================
def start_auto_update():
    while True:
        print("[*] Starting full-feature subscription updater...")
        update_subscriptions()
        print(f"[*] Next update in {UPDATE_INTERVAL // 60} minutes...")
        time.sleep(UPDATE_INTERVAL)

# ========================== Main ==========================
if __name__ == "__main__":
    updater_thread = threading.Thread(target=start_auto_update, daemon=True)
    updater_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all processes and exiting...")
        process_manager.stop_all()
