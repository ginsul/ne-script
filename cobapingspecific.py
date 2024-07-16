# ['"172.25.30.192"']
# ['"172.25.30.192"', '"172.25.30.193"']
# ['"172.25.30.192"', '"172.25.30.193"', '"172.25.30.198"']

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


    # input_data = StringVar(
    #     description="Pilih Network"
    # )

    CHOICES = (
        ('172.25.30.7/31', '172.25.30.7/31')
    )

    input_data = ChoiceVar(
        choices=CHOICES,
        description="Pilih Network"
    )

    def run(self, data, commit):

        # Define arrays
        hosts_up = []
        hosts_down = []

        # List of CIDR blocks to scan
        cidr_blocks = [data['input_data']]

        nb = pynetbox.api('http://172.25.30.129:8000', token='347076470e3d60698be8d50d00d1be814ff7dd97')

        ### Function Specific Subnet
        get_netbox_prefix = list(nb.ipam.prefixes.filter())
        netbox_prefix = []
        for pref in get_netbox_prefix:
            netbox_prefix.append(str(pref))
        #self.log_info(netbox_prefix) ['172.25.54.2', '172.25.54.3']

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
        # get_vm_ip_powershell = get_most_specific_subnet("172.25.30.200")
        # self.log_info(get_vm_ip_powershell)
        # 172.25.30.3/28        
        ####

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
                        self.log_info(current_ip)

                        try:
                            ip_address = nb.ipam.ip_addresses.get(address=str(current_ip)).status
                            
                            #KALO ADA DI NETBOX dan STATUS NYA DOWN
                            update_status_ip_host_down = nb.ipam.ip_addresses.get(address=str(current_ip)).update(
                                {
                                    "status": "deprecated"
                                }
                            )
                            self.log_info(current_ip + " - update deprecated")


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
                        self.log_info(current_ip)

                        try:
                            #KALO ADA DI NETBOX dan STATUS NYA UP
                            ip_address = nb.ipam.ip_addresses.get(address=str(current_ip)).status
                            update_status_ip_host_up = nb.ipam.ip_addresses.get(address=str(current_ip)).update(
                            {
                                "status": "active"
                            }
                            )
                            self.log_info(current_ip + " - update active")

                        #KALO BELUM ADA DI NETBOX, DITAMBAHIN DENGAN SUBNET TERENDAH NYA
                        except (AttributeError):
                            ip_address = nb.ipam.ip_addresses.create(address=get_most_specific_subnet(current_ip))

        # Print arrays in the desired format
        self.log_info(f'Hosts up: [{", ".join(hosts_up)}]')
        self.log_info(f'Hosts down: [{", ".join(hosts_down)}]')
        return("Done")