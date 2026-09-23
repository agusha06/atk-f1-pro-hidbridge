#!/usr/bin/env python3
import hid
import time
import random
import os
import sys
import argparse    

    

REPORT_ID = 0x08

WIRELESS = {
    "vendor_id":  0x373b,
    "product_id": 0x101b,
}

WIRED = {
    "vendor_id":  0x373b,
    "product_id": 0x1014,
}

def find_mouse():
    for mode in (WIRELESS, WIRED):
        devices = hid.enumerate(mode["vendor_id"], mode["product_id"])
        for dev in devices:
            if dev.get("interface_number") == 1:
                return dev["path"]
    return None

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
            break
    return None

def bat():
    dev = find_mouse()
    if not dev:
        print("nfaund")
        exit(1)
    else:
        with hid.Device(path=dev) as h:
            while h.read(64, timeout=10):
                pass

            res_03 = transfer_for_result(h, make_packet(0x03), expected_cmd=0x03)

            rand_bytes = [random.randint(0, 255) for _ in range(4)]
            handshake_payload = [0x00, 0x00, 0x00, 0x08] + rand_bytes
            
            res_01 = transfer_for_result(h, make_packet(0x01, handshake_payload), expected_cmd=0x01)

            res_04 = transfer_for_result(h, make_packet(0x04), expected_cmd=0x04)

            if res_04:
                base_offset = 5
                battery_level = res_04[base_offset]
                battery_charge = res_04[base_offset + 1]
                voltage_raw = (res_04[base_offset + 2] << 8) | res_04[base_offset + 3]
                voltage_v = voltage_raw / 1000.0


                print(f"{battery_level}%")
                print(f"{voltage_v:.3f}")
                print(battery_charge)





def set_dpi(h, mode: int):
    packets = {
        1: bytes([0x08, 0x07, 0x00, 0x00, 0x00, 0x0A, 0x40, 0x15, 0x03, 0x52, 0x01, 0x54, 0x00, 0x00, 0x00, 0x55, 0xE8]),
        2: bytes([0x08, 0x07, 0x00, 0x00, 0x00, 0x0A, 0x40, 0x15, 0x03, 0x52, 0x02, 0x53, 0x00, 0x00, 0x00, 0x55, 0xE8]),
        3: bytes([0x08, 0x07, 0x00, 0x00, 0x00, 0x0A, 0x40, 0x15, 0x03, 0x52, 0x00, 0x55, 0x00, 0x00, 0x00, 0x55, 0xE8]),
    }
    h.write(packets[mode])
    print(f"DPI mode {mode} set")

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--ds", type=int, choices=[1, 2, 3],
                        help="Set DPI stage (1, 2 or 3)")




    args = parser.parse_args()

    if len(sys.argv) == 1:
        bat()
        return

    path = find_mouse()
    if not path:
        print("Мышь не найдена")
        sys.exit(1)

    with hid.Device(path=path) as h:
        if args.ds is not None:
            set_dpi(h, args.ds)


if __name__ == "__main__":
    main()
