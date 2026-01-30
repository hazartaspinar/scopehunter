#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import argparse
import time
import threading
import itertools
import ipaddress

# --- COLORS (Professional Theme) ---
ORANGE = '\033[38;5;208m'
GREEN = '\033[92m'
RED = '\033[91m'
PURPLE = '\033[95m'  # Routing Error
BLUE = '\033[94m'    # Empty Subnet (Gateway Open)
GREY = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'
CLEAR_LINE = '\033[K'

# Global
scan_result = False
diagnosis_msg = ""

def banner():
    ascii_art = r"""
 ███████╗ ██████╗ ██████╗ ██████╗ ███████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
 ██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
 ███████╗██║     ██║   ██║██████╔╝█████╗      ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
 ╚════██║██║     ██║   ██║██╔═══╝ ██╔══╝      ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
 ███████║╚██████╗╚██████╔╝██║     ███████╗    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
 ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    """
    print(f"{ORANGE}{BOLD}{ascii_art}{RESET}")
    print(f"{GREY}           Network Access & Root Cause Analysis Tool v5{RESET}\n")

def check_dependency():
    rc = subprocess.call(['which', 'nmap'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if rc != 0:
        print(f"{RED}[!] Error: 'nmap' is not installed.{RESET}")
        sys.exit(1)

def check_gateway(subnet):
    """
    Tries to identify if the Gateway is alive even if hosts are down.
    Checks .1 and .254 IP addresses of the subnet.
    """
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        # Gateway Guesses: First IP (.1) and Last IP (.254)
        gateways = [str(network.network_address + 1), str(network.broadcast_address - 1)]
        
        for gw in gateways:
            # Send a quick ping
            cmd = f"nmap -sn -PE -n -T4 --max-retries 1 --max-rtt-timeout 200ms {gw}"
            proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if "Host is up" in proc.stdout:
                return True # Gateway is up!
        return False
    except:
        return False

def diagnose_subnet(subnet):
    """
    Deep Error Analysis:
    1. Is there a local Route?
    2. If Route exists, is Gateway responding?
    """
    try:
        # Step 1: Check Local Routing Table
        target_ip = subnet.split('/')[0]
        cmd = f"ip route get {target_ip}"
        process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if process.returncode != 0 or "unreachable" in process.stderr:
            return "No Route" # Computer doesn't know the path
        
        # Step 2: Check Gateway (Route exists but hosts are down)
        if check_gateway(subnet):
            return "Gateway Alive" # Access exists, subnet is just empty
        else:
            return "Timeout" # Neither host nor gateway, total timeout
            
    except Exception:
        return "Unknown"

def run_nmap_thread(subnet):
    global scan_result, diagnosis_msg
    diagnosis_msg = ""
    
    try:
        # Standard Scan
        cmd = [
            "nmap", "-sn", "-PE",
            "-PS21,22,80,443,445,3389,8080",
            "-n", "-T4",
            "--max-retries", "1",
            "--max-rtt-timeout", "400ms",
            "--min-parallelism", "64",
            subnet
        ]
        
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        
        if "Host is up" in process.stdout:
            scan_result = True
        else:
            scan_result = False
            # If scan fails, trigger DIAGNOSIS
            diagnosis_msg = diagnose_subnet(subnet)
            
    except Exception:
        scan_result = False
        diagnosis_msg = "Error"

def main():
    global scan_result, diagnosis_msg
    
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
    
    print(f"{GREY}[*] Analysis Mode: Active (Route Check + Gateway Probe){RESET}")
    print(f"{GREY}[*] Loaded {total} subnets. Starting scan...{RESET}\n")

    report_list = []
    
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    for i, subnet in enumerate(subnets):
        t = threading.Thread(target=run_nmap_thread, args=(subnet,))
        t.start()
        
        while t.is_alive():
            current_spin = next(spinner)
            print(f"\r{ORANGE}{current_spin}{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} {GREY}[Diagnosing...]{RESET}", end="", flush=True)
            time.sleep(0.1)
        
        t.join()

        # --- RESULT ANALYSIS ---
        if scan_result:
            # Case 1: Hosts found, everything is good
            print(f"\r{CLEAR_LINE}{GREEN}[✔]{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} -> {GREEN}ACCESSIBLE{RESET}")
        
        else:
            # Case 2: Error Analysis
            if "No Route" in diagnosis_msg:
                # No Route
                print(f"\r{CLEAR_LINE}{PURPLE}[✘]{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} -> {PURPLE}UNREACHABLE (No Route){RESET}")
                report_list.append(f"{subnet}  [{PURPLE}No Route{RESET}]")
            
            elif "Gateway Alive" in diagnosis_msg:
                # No hosts but Gateway is up (IMPORTANT!)
                print(f"\r{CLEAR_LINE}{BLUE}[?]{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} -> {BLUE}EMPTY SUBNET (Gateway Up){RESET}")
                # We do not add this to the 'Unreachable' list because access exists, it's just empty.
            
            else:
                # Neither host nor gateway exists
                print(f"\r{CLEAR_LINE}{RED}[✘]{RESET} [{i+1}/{total}] Checking: {BOLD}{subnet:<16}{RESET} -> {RED}UNREACHABLE (Timeout){RESET}")
                report_list.append(f"{subnet}  [{RED}Timeout{RESET}]")

    # --- FINAL REPORT ---
    print(f"\n{ORANGE}" + "="*65 + f"{RESET}")
    
    if report_list:
        print(f"\n{RED}{BOLD}[!] PROBLEM DETECTED IN FOLLOWING SUBNETS:{RESET}")
        
        for item in report_list:
            print(f"  - {item}")
        
        print(f"\n{GREY}Legend:{RESET}")
        print(f"  {PURPLE}No Route{RESET} : Your PC cannot find a path (Check VPN/IP Route).")
        print(f"  {RED}Timeout{RESET}  : Path exists but no response (Firewall/Dead Network).")
        print(f"  {BLUE}Empty{RESET}    : Subnet accessible (Gateway up) but no active hosts.")
    else:
        print(f"\n{GREEN}[OK] Perfect! All subnets are accessible.{RESET}")

    print(f"{ORANGE}" + "="*65 + f"{RESET}")

if __name__ == "__main__":
    main()
