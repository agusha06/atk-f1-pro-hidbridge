#!/usr/bin/env python3
import hid
import time
import random
import os
import sys
import argparse    

    

REPORT_ID = 0x08
LOG_FILE = "/home/agusha/.config/dotfiles/hyprland/scripts/mouselog.log"

ENABLE_LOGGING = False

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


def set_smoothing(h, feature: str, enabled: bool):
    b = [0x07, 0x00, 0x00, 0xA9, 0x0A, 0x00, 0x55]
    packets = {
        ("m", True):  bytes([0x08] + b + [0x01, 0x54, 0x03, 0x52, 0x00, 0x55, 0x00, 0x55, 0xEA]),
        ("m", False): bytes([0x08] + b + [0x00, 0x55, 0x03, 0x52, 0x00, 0x55, 0x00, 0x55, 0xEA]),

        ("s", True):  bytes([0x08] + b + [0x01, 0x54, 0x03, 0x52, 0x01, 0x54, 0x00, 0x55, 0xEA]),
        ("s", False): bytes([0x08] + b + [0x01, 0x54, 0x03, 0x52, 0x00, 0x55, 0x00, 0x55, 0xEA]),

        ("r", True):  bytes([0x08] + b + [0x01, 0x54, 0x03, 0x52, 0x00, 0x55, 0x01, 0x54, 0xEA]),
        ("r", False): bytes([0x08] + b + [0x01, 0x54, 0x03, 0x52, 0x00, 0x55, 0x00, 0x55, 0xEA]),

        ("u", True):  bytes([0x08, 0x16, 0x00, 0x00, 0x00, 0x0A, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2C]),
        ("u", False): bytes([0x08, 0x16, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2D]),
    }

    key = (feature, enabled)
    if key not in packets:
        raise ValueError(f"Unknown feature/state: {feature} {enabled}")

    h.write(packets[key])
    state = "enabled" if enabled else "disabled"
    names = {
        "m": "Movement Synchronization",
        "s": "Straight Line Correction",
        "r": "Ripple Correction",
        "u": "Ultra Long Range Mode",
    }
    print(f"{names[feature]} → {state}")




def main():
    parser = argparse.ArgumentParser(description="ATK F1 Pro control")
    
    parser.add_argument("--ds", type=int, choices=[1, 2, 3],
                        help="Set DPI stage (1, 2 or 3)")
    parser.add_argument("-m", "--movement-sync", type=lambda x: x.lower() == "true",
                        choices=[True, False], metavar="true/false",
                        help="Movement Synchronization (true/false)")
    parser.add_argument("-s", "--straight-line", type=lambda x: x.lower() == "true",
                        choices=[True, False], metavar="true/false",
                        help="Straight Line Correction (true/false)")
    parser.add_argument("-r", "--ripple", type=lambda x: x.lower() == "true",
                        choices=[True, False], metavar="true/false",
                        help="Ripple Correction (true/false)")
    parser.add_argument("-u", "--ultra-long-range", type=lambda x: x.lower() == "true",
                        choices=[True, False], metavar="true/false",
                        help="Ultra Long Range Mode (true/false)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        return

    path = find_mouse()
    if not path:
        print("Мышь не найдена")
        sys.exit(1)



if __name__ == "__main__":
    main()
