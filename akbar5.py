#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

# ===================== Colors =====================
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# ===================== Repo Paths =====================
REPOS = {
    "1": {"name": "sab-vip10", "path": os.path.expanduser("~/sab-vip10"), "script": "sab-vip10.py"},
    "2": {"name": "reza-shah", "path": os.path.expanduser("~/reza-shah1320"), "script": "reza-shah.py"},
    "3": {"name": "sshmax98", "path": os.path.expanduser("~/online-sshmax98"), "script": "sshmax98.py"},
    "4": {"name": "sshmax98-2", "path": os.path.expanduser("~/online-sshmax98"), "script": "sshmax98-2.py"},
}

def run_update(repo_info):
    path = repo_info["path"]
    script = repo_info["script"]
    
    if not os.path.isdir(path):
        print(f"{YELLOW}Directory for {repo_info['name']} not found: {path}{RESET}")
        input(f"{CYAN}Press Enter to return to main menu...{RESET}")
        return
    
    os.chdir(path)
    print(f"{GREEN}Running update for {repo_info['name']}...{RESET}")
    cmd = ["python3", script]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{YELLOW}Error running {script}: {e}{RESET}")
    
    input(f"{CYAN}Press Enter to return to main menu...{RESET}")

def main_menu():
    while True:
        print(f"\n{CYAN}Select an update to run:{RESET}")
        print(f"{CYAN}1) update sab-vip10{RESET}")
        print(f"{CYAN}2) update reza-shah{RESET}")
        print(f"{CYAN}3) update sshmax98{RESET}")
        print(f"{CYAN}4) update sshmax98-2{RESET}")
        print(f"{CYAN}5) Exit{RESET}")
        choice = input(f"{CYAN}Choice: {RESET}").strip()
        
        if choice in ["1", "2", "3", "4"]:
            run_update(REPOS[choice])
        elif choice == "5":
            print(f"{GREEN}Exiting.{RESET}")
            break
        else:
            print(f"{YELLOW}Invalid choice!{RESET}")

if __name__ == "__main__":
    main_menu()
