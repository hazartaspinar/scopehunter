#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import argparse
import time
import threading
import itertools

# --- COLORS (Professional Orange Theme) ---
ORANGE = '\033[38;5;208m'
GREEN = '\033[92m'
RED = '\033[91m'
GREY = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'
CLEAR_LINE = '\033[K'

# Global variable for thread result
scan_result = False

def banner():
    # ANSI Shadow / Bloody Style ASCII Art
    ascii_art = r"""
 ███████╗ ██████╗ ██████╗ ██████╗ ███████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
 ██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
 ███████╗██║     ██║   ██║██████╔╝█████╗      ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
 ╚════██║██║     ██║   ██║██╔═══╝ ██╔══╝      ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
 ███████║╚██████╗╚██████╔╝██║     ███████╗    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
 ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    """
    print(f"{ORANGE}{BOLD}{ascii_art}{RESET}")
    print(f"{GREY}                     Network Access Verification Tool{RESET}\n")

def check_dependency():
    """Checks if Nmap is installed."""
    rc = subprocess.call(['which', 'nmap'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if rc != 0:
        print(f"{RED}[!] Error: 'nmap' is not installed.{RESET}")
        sys.exit(1)

def run_nmap_thread(subnet):
    """
    Runs Nmap with balanced settings for both VPN and Local LAN.
    Includes 'Fast Fail' logic to skip dead subnets quickly.
    """
    global scan_result
    try:
        # Nmap Configuration:
        # -sn: Host Discovery only (No Port Scan)
        # -PE: ICMP Ping
        # -PS...: TCP SYN Ping to critical ports (FTP, SSH, Web, SMB, RDP, Alt-Web)
        # -n: No DNS resolution
        # -T4: Aggressive timing
        # --max-retries 1: Speed up scanning by not retrying dead hosts too often
        # --max-rtt-timeout 400ms: Wait max 400ms for a packet (Good for VPN)
        # --min-parallelism 64: Force parallel scanning
        cmd = [
            "nmap", 
            "-sn",
            "-PE",
            "-PS21,22,80,443,445,3389,8080",
            "-n",
            "-T4",
            "--max-retries", "1",
            "--max-rtt-timeout", "400ms",
            "--min-parallelism", "64",
            subnet
        ]
        
        process = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.DEVNULL, 
            text=True
        )
        
        if "Host is up" in process.stdout:
            scan_result = True
        else:
            scan_result = False
            
    except Exception:
        scan_result = False

def main():
    global scan_result
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path to scope file", required=True)
    args = parser.parse_args()

    os.system('clear')
    banner()
    check_dependency()

    if not os.path.exists(args.file):
        print(f"{RED}[!] File not found: {args.file}{RESET}")
        sys.exit(1)

    with open(args.file, "r") as f:
        subnets = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    total = len(subnets)
    
    # Simple configuration info
    print(f"{GREY}[*] Target Ports: 21, 22, 80, 443, 445, 3389, 8080{RESET}")
    print(f"{GREY}[*] Loaded {total} subnets. Starting scan...{RESET}\n")

    unreachable_list = []
    
    # Loading Spinner
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    for i, subnet in enumerate(subnets):
        # Start thread
        t = threading.Thread(target=run_nmap_thread, args=(subnet,))
        t.start()
        
        # Animation loop
        while t.is_alive():
            current_spin = next(spinner)
            print(f"\r{ORANGE}{current_spin}{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} {GREY}[Scanning...]{RESET}", end="", flush=True)
            time.sleep(0.1)
        
        t.join()

        # Result display
        if scan_result:
            print(f"\r{CLEAR_LINE}{GREEN}[✔]{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} -> {GREEN}ACCESSIBLE{RESET}")
        else:
            print(f"\r{CLEAR_LINE}{RED}[✘]{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} -> {RED}UNREACHABLE{RESET}")
            unreachable_list.append(subnet)

    # --- FINAL REPORT ---
    print(f"\n{ORANGE}" + "="*55 + f"{RESET}")
    
    if unreachable_list:
        print(f"\n{RED}{BOLD}[!] UNREACHABLE SUBNETS ({len(unreachable_list)}):{RESET}")
        print(f"{GREY}(Copy list below for client){RESET}\n")
        
        for item in unreachable_list:
            print(f"  - {item}")
        
        print(f"\n{GREY}Total: {len(unreachable_list)} / {total} subnets are unreachable.{RESET}")
    else:
        print(f"\n{GREEN}[OK] Perfect! All subnets are accessible.{RESET}")

    print(f"{ORANGE}" + "="*55 + f"{RESET}")

if __name__ == "__main__":
    main()
