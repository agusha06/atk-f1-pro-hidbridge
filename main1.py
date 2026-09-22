#!/usr/bin/env python3
import hid
import time
import random
import os

REPORT_ID = 0x08
VENDOR_ID  = 0x373b
PRODUCT_ID = 0x101b
LOG_FILE = "/home/agusha/.config/dotfiles/hyprland/scripts/mouselog.log"

ENABLE_LOGGING = True

def find_mouse():
    for dev in hid.enumerate(VENDOR_ID, PRODUCT_ID):
        if dev['interface_number'] == 1:
            return dev['path']
    return None
def log(msg):
    if ENABLE_LOGGING:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")

def calc_checksum(packet_15_bytes):
    return (0x4D - sum(packet_15_bytes)) & 0xFF

def make_packet(cmd_id, payload=None):
    pkt = [cmd_id] + [0] * 14
    if payload:
        for i, b in enumerate(payload):
            pkt[1 + i] = b
    pkt.append(calc_checksum(pkt))
    return bytes([REPORT_ID]) + bytes(pkt)

def transfer_for_result(h, pkt, expected_cmd, timeout_ms=600):
    h.write(pkt)
    t0 = time.time()
    while (time.time() - t0) * 1000 < timeout_ms:
        res = h.read(64, timeout=50)
        if not res:
            continue
        offset = 1 if res[0] == REPORT_ID else 0
        cmd = res[offset]
        if cmd == expected_cmd:
            return res[offset:]
        else:
            log(f"CMD 0x{cmd:02X}")
    return None

def main():
    try:
        dev = find_mouse()
        if not dev:
            print("nfaund")
            exit(1)
        else:
            with hid.Device(path=dev) as h:
                while h.read(64, timeout=10):
                    pass

                log("GetWirelessMouseOnline 0x03")
                res_03 = transfer_for_result(h, make_packet(0x03), expected_cmd=0x03)
                if res_03:
                    is_online = res_03[4] == 1
                    log(f"0x03: {is_online}")
                else:
                    log("0x03- timeout")

                rand_bytes = [random.randint(0, 255) for _ in range(4)]
                handshake_payload = [0x00, 0x00, 0x00, 0x08] + rand_bytes
                log(f"DownLoadData 0x01 {bytes(rand_bytes).hex(' ')}")
                
                res_01 = transfer_for_result(h, make_packet(0x01, handshake_payload), expected_cmd=0x01)
                if res_01:
                    log("0x01 ok")
                else:
                    log("0x01 not 0k")
                    return

                log("GetBatteryLevel 0x04")
                res_04 = transfer_for_result(h, make_packet(0x04), expected_cmd=0x04)

                if res_04:
                    base_offset = 5
                    battery_level = res_04[base_offset]
                    battery_charge = res_04[base_offset + 1]
                    voltage_raw = (res_04[base_offset + 2] << 8) | res_04[base_offset + 3]
                    voltage_v = voltage_raw / 1000.0

                    log(f" {battery_level}%, {voltage_v:.3f}V, ChargeFlag={battery_charge}")
                    log("_"*30)

                    print(f"{battery_level}%")
                    print(f"{voltage_v:.3f}")
                    print(battery_charge)

                else:
                    log("0x04 not out")

    except Exception as e:
        log(f"{e}")

if __name__ == "__main__":
    main()
