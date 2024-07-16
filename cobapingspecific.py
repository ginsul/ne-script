import subprocess
import re
import pynetbox
import ipaddress
from extras.scripts import *

class PingSpecific(Script):
    class Meta:
        name = "Coba Ping Spesific"
        description = "Coba Ping Spesific Deacription"
        field_order = ['input_data']

    CHOICES = (
        ('172.25.30.7/31', '172.25.30.7/31'),
        ('s', 'South')
    )

    input_data = ChoiceVar(
        choices=CHOICES,
        description="Pilih Network"
    )

    def run(self, data, commit):

        # List of CIDR blocks to scan
        cidr_blocks = [data['input_data']]

        hosts_up = []
        hosts_down = []
        nb = pynetbox.api('http://172.25.30.129:8000', token='347076470e3d60698be8d50d00d1be814ff7dd97')

        # Function to get Specific Subnet
        get_netbox_prefix = list(nb.ipam.prefixes.filter())
        netbox_prefix = []
        for pref in get_netbox_prefix:
            netbox_prefix.append(str(pref))

        def get_most_specific_subnet(ip_address):
            a = ipaddress.ip_address(ip_address)
            most_specific_subnet = None

            for p in netbox_prefix:
                if a in ipaddress.ip_network(p):
                    if most_specific_subnet is None or ipaddress.ip_network(p) > ipaddress.ip_network(most_specific_subnet):
                        most_specific_subnet = p

            if most_specific_subnet is not None:
                return str(a) + '/' + str(ipaddress.ip_network(most_specific_subnet).prefixlen)
            else:
                return "notsubnet"

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
                        
                        scanned_ip_format=ipaddress.ip_address(current_ip)
                        current_ip_compressed=scanned_ip_format.compressed

                        hosts_down.append(f'"{current_ip_compressed}"')

                        try:
                            ip_address = nb.ipam.ip_addresses.get(address=str(current_ip_compressed)).status
                            
                        # if present in netbox and status is down
                            update_status_ip_host_down = nb.ipam.ip_addresses.get(address=str(current_ip_compressed)).update(
                                {
                                    "status": "deprecated"
                                }
                            )
                            self.log_info(current_ip_compressed + " is down")

                        except (AttributeError):
                        # if not present in netbox and status is down 
                            ip_address = 0

                    else:
                        current_ip = line.split()[-1]  # Correct index for up hosts

                        scanned_ip_format=ipaddress.ip_address(current_ip)
                        current_ip_compressed=scanned_ip_format.compressed
                        
                        # Resolve IP if it is a hostname
                        if re.match(r'^[a-zA-Z]', current_ip_compressed):
                            resolved_ip = resolve_ip(currencurrent_ip_compressedt_ip)
                            if resolved_ip:
                                current_ip_compressed = resolved_ip

                        hosts_up.append(f'"{current_ip_compressed}"')

                        try:
                        # if present in netbox and status is up
                            ip_address = nb.ipam.ip_addresses.get(address=str(current_ip_compressed)).status
                            update_status_ip_host_up = nb.ipam.ip_addresses.get(address=str(current_ip_compressed)).update(
                                {
                                "status": "active"
                                }
                            )
                            self.log_info(current_ip_compressed + " is up")

                        # if not present in netbox, create ip address with the most specific subnet
                        except (AttributeError):
                            ip_address = nb.ipam.ip_addresses.create(address=get_most_specific_subnet(current_ip_compressed))
                            self.log_info(current_ip_compressed + " - new IP discovered")

        return(f'Hosts up: [{", ".join(hosts_up)}]')
        return(f'Hosts down: [{", ".join(hosts_down)}]')      