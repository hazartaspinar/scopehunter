# Scope Hunter

**Scope Hunter** is a high-performance network reachability verifier designed for penetration testers and network administrators. It utilizes **Nmap** (ICMP & TCP SYN) to validate accessible subnets within a given scope, optimized for both local LANs and VPN environments.

Before running a heavy vulnerability scan (like Nessus or Qualys), use Scope Hunter to quickly identify which subnets are actually reachable, saving time and generating a clean "unreachable" report for clients.

### Live Scanning Process
The tool provides real-time visual feedback with a threading-based status indicator.

<img width="812" height="271" alt="image" src="https://github.com/user-attachments/assets/d56e5eaf-44d0-4ce7-a54c-b47931785c94" />



### Final Report
Generates a clear, copy-paste ready list of unreachable subnets for reporting.

<img width="840" height="333" alt="image" src="https://github.com/user-attachments/assets/d8315724-db6d-4181-8d25-b3be80463bb3" />

## 🚀 Features

* **Hybrid Discovery:** Uses both ICMP (Ping) and TCP SYN probes on critical ports (`21, 22, 80, 443, 445, 3389, 8080`) to bypass common firewall restrictions.
* **VPN Optimized:** Includes RTT tolerance (`--min-rtt-timeout`) to prevent false negatives on slow VPN connections.
* **Fast Fail Logic:** Optimized timing templates (`-T4`, limited retries) to quickly skip dead or empty subnets without wasting time.
* **Visual Feedback:** Clean, professional CLI output with status animations.
* **Root Accuracy:** Relies on Nmap's kernel-level packet crafting for maximum reliability.

## 📦 Installation

Scope Hunter requires **Python 3** and **Nmap**.

1.  **Install Nmap** (if not installed):
    ```bash
    sudo apt update
    sudo apt install nmap
    ```

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/hazartaspinar/scopehunter
    cd scope-hunter
    ```

3.  **Make executable:**
    ```bash
    chmod +x ScopeHunter.py
    ```

## 🛠 Usage

Since the tool uses TCP SYN packets for accurate discovery, it requires **root (sudo)** privileges.

```bash
sudo python3 ScopeHunter.py -f scope.txt
