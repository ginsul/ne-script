# ['"172.25.30.192"']
# ['"172.25.30.192"', '"172.25.30.193"']
# ['"172.25.30.192"', '"172.25.30.193"', '"172.25.30.198"']

import subprocess
import re
import pynetbox

# Define arrays
hosts_up = []
hosts_down = []

# List of CIDR blocks to scan
cidr_blocks = ["172.25.30.202/31"]

nb = pynetbox.api('http://172.25.30.129:8000', token='347076470e3d60698be8d50d00d1be814ff7dd97')

# Function to resolve hostnames to IP addresses
def resolve_ip(hostname):
    result = subprocess.run(['getent', 'hosts', hostname], stdout=subprocess.PIPE, text=True)
    if result.stdout:
        return result.stdout.split()[0]
    return None

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
                print(current_ip)

                try:
                    ip_address = nb.ipam.ip_addresses.get(address=str(current_ip)).status

                except (AttributeError):
                    ip_address = 0



            #############################################################################
            else:
                current_ip = line.split()[-1]  # Correct index for up hosts

                # Resolve IP if it is a hostname
                if re.match(r'^[a-zA-Z]', current_ip):
                    resolved_ip = resolve_ip(current_ip)
                    if resolved_ip:
                        current_ip = resolved_ip

                hosts_up.append(f'"{current_ip}"')
                print(current_ip)

                try:
                    ip_address = nb.ipam.ip_addresses.get(address=str(current_ip)).status

                #KALO BELUM ADA DI NETBOX, DITAMBAHIN
                except (AttributeError):
                    ip_address = nb.ipam.ip_addresses.create(address=str(current_ip))

# Print arrays in the desired format
print(f'Hosts up: [{", ".join(hosts_up)}]')
print(f'Hosts down: [{", ".join(hosts_down)}]')
