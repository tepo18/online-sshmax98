import json
import sys
import base64
import re
import yaml
import os

def is_valid_uuid(uuid):
    return re.fullmatch(r'[0-9a-fA-F-]{36}', uuid) is not None

def detect_config_type(line):
    line = line.strip()
    if line.startswith("vless://"):
        return "vless"
    elif line.startswith("vmess://"):
        return "vmess"
    elif line.startswith("trojan://"):
        return "trojan"
    elif line.startswith("ss://"):
        return "shadowsocks"
    elif line.startswith("wg://") or line.startswith("wireguard://"):
        return "wireguard"
    # try json detection
    try:
        js = json.loads(line)
        protocol = js.get("protocol", "").lower()
        if protocol == "vless":
            return "json_vless"
        elif protocol == "vmess":
            return "json_vmess"
        elif protocol == "trojan":
            return "json_trojan"
        elif protocol == "shadowsocks":
            return "json_shadowsocks"
        elif protocol == "wireguard":
            return "json_wireguard"
    except:
        pass
    return "unknown"

def convert_json_to_vless(js):
    try:
        cfg = json.loads(js)
        out = cfg.get("outbounds", [{}])[0]
        vnext = out.get("settings", {}).get("vnext", [{}])[0]
        user = vnext.get("users", [{}])[0]
        uuid = user.get("id", "")
        address = vnext.get("address", "")
        port = vnext.get("port", "")
        stream = out.get("streamSettings", {})
        net = stream.get("network", "tcp")
        sec = stream.get("security", "tls")
        sni = stream.get("tlsSettings", {}).get("serverName", "")
        path = ""
        if net == "ws":
            path = stream.get("wsSettings", {}).get("path", "")
        elif net == "grpc":
            path = stream.get("grpcSettings", {}).get("serviceName", "")
        if not (uuid and address and port and is_valid_uuid(uuid)):
            return None
        return f"vless://{uuid}@{address}:{port}?encryption=none&type={net}&security={sec}&sni={sni}&path={path}#{address}"
    except:
        return None

def main():
    print("Paste your configs (links or JSON), then press Enter and Ctrl+D:\n")
    input_text = sys.stdin.read().strip()
    if not input_text:
        print("No input detected.")
        return

    lines = [l.strip() for l in input_text.splitlines() if l.strip()]
    detected = {
        "vless": [],
        "vmess": [],
        "trojan": [],
        "shadowsocks": [],
        "wireguard": [],
        "json_vless": [],
        "json_vmess": [],
        "json_trojan": [],
        "json_shadowsocks": [],
        "json_wireguard": [],
        "unknown": []
    }

    for line in lines:
        t = detect_config_type(line)
        if t.startswith("json_"):
            # convert only json_vless for now
            if t == "json_vless":
                conv = convert_json_to_vless(line)
                if conv:
                    detected["json_vless"].append(conv)
                else:
                    detected["unknown"].append(line)
            else:
                detected[t].append(line)
        else:
            detected[t].append(line)

    total_count = sum(len(v) for v in detected.values())

    print(f"\nDetected configs: {total_count}")
    for key in detected:
        print(f"  {key}: {len(detected[key])}")

    if total_count == 0:
        print("No configs detected.")
        return

    print("\nChoose output format:")
    print("1) VLESS fragment links")
    print("2) VMess links")
    print("3) Shadowsocks links")
    print("4) WireGuard links")
    print("5) JSON (all configs)")
    print("6) YAML fragment")
    print("7) Plain text fragments")

    choice = input("Option (1-7): ").strip()
    save = input("Save output to /sdcard/Download? (y/n): ").strip().lower()
    base_path = "/sdcard/Download" if save == "y" else "."

    result_path = ""

    if choice == "1":
        result_path = os.path.join(base_path, "vless_fragment.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            for item in detected["vless"] + detected["json_vless"]:
                f.write(item + "\n")
    elif choice == "2":
        result_path = os.path.join(base_path, "vmess_fragment.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            for item in detected["vmess"] + detected["json_vmess"]:
                f.write(item + "\n")
    elif choice == "3":
        result_path = os.path.join(base_path, "shadowsocks_fragment.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            for item in detected["shadowsocks"] + detected["json_shadowsocks"]:
                f.write(item + "\n")
    elif choice == "4":
        result_path = os.path.join(base_path, "wireguard_fragment.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            for item in detected["wireguard"] + detected["json_wireguard"]:
                f.write(item + "\n")
    elif choice == "5":
        result_path = os.path.join(base_path, "all_configs.json")
        all_configs = []
        for key in detected:
            all_configs.extend(detected[key])
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(all_configs, f, ensure_ascii=False, indent=2)
    elif choice == "6":
        result_path = os.path.join(base_path, "fragments.yaml")
        yaml_data = {}
        for key in ["vless", "vmess", "shadowsocks", "wireguard"]:
            yaml_data[key] = detected[key]
        with open(result_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, allow_unicode=True)
    elif choice == "7":
        result_path = os.path.join(base_path, "fragments.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            for key in detected:
                for item in detected[key]:
                    f.write(item + "\n")
    else:
        print("Invalid option.")
        return

    print(f"\nSaved output to: {result_path}")

if __name__ == "__main__":
    main()
