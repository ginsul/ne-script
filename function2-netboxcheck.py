# ['"172.25.30.192"']
# ['"172.25.30.192"', '"172.25.30.193"']
# ['"172.25.30.192"', '"172.25.30.193"', '"172.25.30.198"']

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

                try:
                    ip_address = nb.ipam.ip_addresses.get(address=str(current_ip)).status

                except (AttributeError):
                    print("IP: " + str(current_ip) + " Has not Status on Netbox")

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
