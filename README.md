# CodeAlpha - Network Intrusion Detection System

This is Task 4 of my CodeAlpha Cyber Security internship. The goal was to set up a working NIDS (Network Intrusion Detection System) that can monitor live network traffic, detect suspicious activity, and actually do something about it (not just log it and forget it).

I used **Suricata** for this instead of Snort, mainly because it's actively maintained and has better multi-threading support, plus the ET Open rule set gives you thousands of ready-made detection signatures out of the box.

## What this project does

- Monitors live traffic on my WiFi interface (`wlo1`)
- Uses Suricata with ET Open rules to detect known attack patterns
- Logs every alert to `eve.json` (structured JSON) and `fast.log` (human readable)
- Optionally saves raw packet captures (`.pcap`) so you can inspect traffic later in Wireshark
- Runs a Python script (`auto_block.py`) that watches the alert log in real time and automatically blocks the offending IP using `iptables`

Basically it's not just "detect and log" - there's an actual response mechanism attached to it.

## Setup

1. Install Suricata
```bash
sudo apt update
sudo apt install suricata -y
```

2. Set your network in `suricata.yaml` (`HOME_NET`) and point `af-packet` to your interface (mine is `wlo1`, yours will probably be `eth0` or similar - check with `ip a`)

3. Update the rules
```bash
sudo suricata-update
```

4. Run it
```bash
sudo suricata -c /etc/suricata/suricata.yaml -i wlo1 -D
```

The config file I uploaded here (`config/suricata.yaml`) has my real local network range removed and replaced with a generic one, just to avoid putting my actual network info on a public repo.

## Testing it

I didn't have a real attacker on hand, so I used two ways to trigger alerts:

- `curl http://testmyids.com/` - a site specifically made to trigger IDS test signatures, works every time
- `nmap -sS` scans against another device on my network (scanning your own machine doesn't work well since that traffic doesn't actually leave the network interface, learned that the hard way)

Once Suricata picks something up, it shows up almost instantly in `fast.log`.

## The response part (auto_block.py)

This was the part I found most interesting. Suricata alone just tells you something happened - it doesn't stop it. So I wrote a small Python script that:

1. Tails `eve.json` continuously (similar to `tail -f`)
2. Parses each new line as JSON
3. If the event type is `alert`, grabs the source IP
4. Runs `iptables -A INPUT -s <ip> -j DROP` to block it
5. Keeps a set of already-blocked IPs so it doesn't spam the same rule over and over

Run it with:
```bash
sudo python3 auto_block.py
```

Then trigger a test alert in another terminal and watch it block the IP live. You can confirm the block actually landed with:
```bash
sudo iptables -L INPUT -n --line-numbers
```

## What I learned

- How rule-based detection actually works under the hood (signature matching against traffic patterns, not magic)
- Why scanning your own machine doesn't generate traffic Suricata can see
- Reading `eve.json` properly with `jq` instead of squinting at raw JSON
- That systemd will happily fight you if you're running something manually while its own service definition is still enabled - cost me a good chunk of time figuring out why Suricata kept "already running" on me
- Basic packet capture inspection with pcap files and Wireshark/tshark

## Screenshots

Check the `screenshots/` folder for:
- Suricata running and monitoring the interface
- Live alerts in `fast.log` after triggering a test
- `auto_block.py` catching and blocking an IP in real time
- `iptables` output confirming the block

## Demo video

Full walkthrough here: [LinkedIn video](www.linkedin.com/in/kamil-hasanli-7b4427327)

---


