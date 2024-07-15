####
####
# nmap -sn -R -T3 --min-parallelism 10 -v 172.25.30.200/28
# Starting Nmap 7.70 ( https://nmap.org ) at 2024-07-16 00:32 WIB
# Initiating ARP Ping Scan at 00:32
# Scanning 15 hosts [1 port/host]
# Completed ARP Ping Scan at 00:32, 0.42s elapsed (15 total hosts)
# Initiating Parallel DNS resolution of 15 hosts. at 00:32
# Completed Parallel DNS resolution of 15 hosts. at 00:32, 4.01s elapsed
# Nmap scan report for 172.25.30.192 [host down]
# Nmap scan report for 172.25.30.193 [host down]
# Nmap scan report for 172.25.30.194
# Host is up (0.00098s latency).
# MAC Address: 00:15:5D:11:04:31 (Microsoft)
# Nmap scan report for 172.25.30.195
# Host is up (0.0012s latency).
# MAC Address: 00:15:5D:11:04:30 (Microsoft)
# Nmap scan report for 172.25.30.196
# Host is up (0.0012s latency).
# MAC Address: 00:15:5D:11:04:2F (Microsoft)
# Nmap scan report for 172.25.30.197
# Host is up (0.00097s latency).
# MAC Address: 00:15:5D:11:04:2E (Microsoft)
# Nmap scan report for 172.25.30.198 [host down]
# Nmap scan report for 172.25.30.199
# Host is up (0.00097s latency).
# MAC Address: 00:15:5D:10:A7:0F (Microsoft)
# Nmap scan report for 172.25.30.200
# Host is up (0.00096s latency).
# MAC Address: 00:15:5D:CD:AC:09 (Microsoft)
# Nmap scan report for 172.25.30.201 [host down]
# Nmap scan report for 172.25.30.202
# Host is up (0.00096s latency).
# MAC Address: 00:15:5D:10:A7:17 (Microsoft)
# Nmap scan report for 172.25.30.204 [host down]
# Nmap scan report for 172.25.30.205 [host down]
# Nmap scan report for 172.25.30.206 [host down]
# Nmap scan report for 172.25.30.207 [host down]
# Nmap scan report for mama.local (172.25.30.203)
# Host is up.
# Read data files from: /usr/bin/../share/nmap
# Nmap done: 16 IP addresses (8 hosts up) scanned in 4.49 seconds
#            Raw packets sent: 23 (644B) | Rcvd: 7 (196B)

import subprocess
import re

# Define arrays
hosts_up = []
hosts_down = []

# Function to resolve hostnames to IP addresses
def resolve_ip(hostname):
    result = subprocess.run(['getent', 'hosts', hostname], stdout=subprocess.PIPE, text=True)
    if result.stdout:
        return result.stdout.split()[0]
    return None

# List of CIDR blocks to scan
cidr_blocks = ["172.25.30.200/28", "192.168.1.0/24"]

# Run nmap for each CIDR block
for cidr in cidr_blocks:
    nmap_command = ['nmap', '-sn', '-R', '-T3', '--min-parallelism', '10', '-v', cidr]
    result = subprocess.run(nmap_command, stdout=subprocess.PIPE, text=True)

    # Process the nmap output line by line
    for line in result.stdout.splitlines():
        if "Nmap scan report for" in line:
            # Determine IP based on context
            if "[host down]" in line:
                current_ip = line.split()[-3]  # Correct index for down hosts
                hosts_down.append(f'"{current_ip}"')
            else:
                current_ip = line.split()[-1]  # Correct index for up hosts

                # Resolve IP if it is a hostname
                if re.match(r'^[a-zA-Z]', current_ip):
                    resolved_ip = resolve_ip(current_ip)
                    if resolved_ip:
                        current_ip = resolved_ip
                
                hosts_up.append(f'"{current_ip}"')

# Print arrays in the desired format
print(f'Hosts up: [{", ".join(hosts_up)}]')
print(f'Hosts down: [{", ".join(hosts_down)}]')
