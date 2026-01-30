# Scope Hunter

**Scope Hunter** is a professional network reachability verifier and **Root Cause Analysis** tool designed for penetration testers and network administrators.

Unlike standard ping sweepers, Scope Hunter doesn't just tell you *if* a subnet is unreachable—it tells you **why**. It distinguishes between client-side routing issues, firewall blocks, and empty subnets using smart kernel routing checks and gateway probing.

> **Perfect for:** Validating VPN access and cleaning up scope lists before launching heavy vulnerability scanners like Nessus or Qualys.

## Screenshots

### 1. Live Smart Scanning
Real-time threaded scanning with visual status indicators.

<img width="875" height="229" alt="image" src="https://github.com/user-attachments/assets/237d1aa4-9a18-4019-a4f4-30dd8e73145a" />


### 2. Root Cause Analysis Report
Final report categorizing subnets by specific error types (Timeout vs. No Route).

<img width="714" height="169" alt="image" src="https://github.com/user-attachments/assets/c174e7ca-8402-4862-a8b9-1abce354db8f" />


## Key Features

* ** Hybrid Discovery:** Uses ICMP Echo + TCP SYN Probes on critical ports (`21, 22, 80, 443, 445, 3389, 8080`) to bypass common firewalls.
* **🧠 Smart Diagnosis:** Automatically identifies the root cause of unreachable subnets:
    * **🟣 No Route:** Detects missing VPN routes or client-side config errors.
    * **🔴 Timeout:** Detects firewall blocks or dead networks.
    * **🔵 Empty Subnet:** Detects reachable networks (Gateway is UP) that have no active hosts.
* ** VPN Optimized:** Includes RTT tolerance (`--min-rtt-timeout`) to prevent false negatives on slow VPN connections.
* ** Fast Fail Logic:** Optimized timing templates to quickly skip dead IP blocks without wasting time.
* ** Visual Feedback:** Professional CLI output with color-coded results and thread animations.

## Installation

Scope Hunter requires **Python 3** and **Nmap**.

1.  **Install Nmap** (Required for packet crafting):
    ```bash
    sudo apt update
    sudo apt install nmap
    ```

2.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/scope-hunter.git](https://github.com/YOUR_USERNAME/scope-hunter.git)
    cd scope-hunter
    ```

3.  **Make Executable:**
    ```bash
    chmod +x ScopeHunter.py
    ```

## 🛠 Usage

This tool requires **root (sudo)** privileges to perform TCP SYN scans and access the kernel routing table.

```bash
sudo python3 ScopeHunter.py -f scope.txt
