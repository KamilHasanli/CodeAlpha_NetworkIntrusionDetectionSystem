# Findings - Network Intrusion Detection System

## Setup summary

- Suricata 7.0.3 running on Ubuntu, monitoring interface `wlo1`
- ET Open rule set loaded via `suricata-update` (community signatures, thousands of rules)
- Logging to `fast.log` (human-readable) and `eve.json` (structured, used by `auto_block.py`)
- Response mechanism: `auto_block.py` watches `eve.json` live and blocks offending IPs with `iptables`

## Test 1 - testmyids.com

Ran:
```bash
curl http://testmyids.com/
```

This site is built specifically to trigger IDS/IPS test signatures. Suricata picked it up almost instantly.

**Result:** Alert logged in `fast.log`:
```
GPL ATTACK_RESPONSE id check returned root
```
Classification: Potentially Bad Traffic, Priority 2.

This confirms the sensor is actively inspecting traffic on `wlo1` and matching it against loaded signatures correctly.

## Test 2 - auto_block.py response

With `auto_block.py` running in the background, repeated the `testmyids.com` request.

**Result:**
- Script printed `[ALERT] ... from <source_ip>`
- Immediately followed by `[!] Blocking IP: <source_ip>`
- Confirmed with `sudo iptables -L INPUT -n --line-numbers` - the IP appeared with a `DROP` target

This confirms the full detect → parse → respond loop works end to end, not just detection on its own.

## Notes / things I ran into

- Scanning my own machine's IP with `nmap` didn't generate any alerts. That traffic goes through the loopback path internally and never actually goes out through `wlo1`, so Suricata (bound to that interface) never sees it. Using an external test target (testmyids.com) or scanning a different device on the network worked as expected.
- Ran into a recurring "pidfile exists, aborting" issue caused by a leftover systemd-managed Suricata process fighting with the one I started manually. Had to stop/disable/mask the systemd service to run Suricata manually without it respawning.
- pcap logging was enabled in the config to save raw packet captures alongside the alerts, useful for later inspection in Wireshark/tshark if needed.

## Conclusion

The setup successfully detects known-signature attacks in real time and automatically responds by blocking the source IP at the firewall level, fulfilling both the detection and response requirements of this task.
