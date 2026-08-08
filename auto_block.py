import json
import subprocess
import time




LOG_FILE = "/var/log/suricata/eve.json"
blocked_ips = set()
def block_ip(ip):
    if ip in blocked_ips:
        return
    print(f"[!] Blocking IP: {ip}")
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    blocked_ips.add(ip)
def follow(file):
    file.seek(0, 2)  
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.5)
            continue
        yield line
with open(LOG_FILE, "r") as f:
    for line in follow(f):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event_type") == "alert":
            src_ip = event.get("src_ip")
            signature = event.get("alert", {}).get("signature", "")
            print(f"[ALERT] {signature} from {src_ip}")
            if src_ip:
                block_ip(src_ip)
