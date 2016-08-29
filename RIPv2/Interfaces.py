import netifaces
import struct
import socket

import Helper
import GlobalParameters


''' This method scans interfaces, constructs starting
    routing table and returns it '''


def scann_interfaces():
    interfaces = netifaces.interfaces()

    print("\nInterfaces detected:")

    routing_table = dict()

    ''' for each interface '''
    for interface in interfaces:

        addrs = netifaces.ifaddresses(interface)

        if netifaces.AF_INET in addrs:
            if_addresses = addrs[netifaces.AF_INET]
            for if_address in if_addresses:
                ip_address = if_address[GlobalParameters.IP_ADDRESS]
                subnet_mask = if_address[GlobalParameters.SUBNET_MASK]

                ip_integer = struct.unpack(">I", socket.inet_aton(ip_address))[0]
                mask_integer = struct.unpack(">I", socket.inet_aton(subnet_mask))[0]

                network_integer = ip_integer & mask_integer
                network_address = socket.inet_ntoa(struct.pack(">I", network_integer))

                ''' check for 127.0.0.0/8 network which we must ignore '''
                if (network_address, subnet_mask) != GlobalParameters.IGNORE_NETWORK:
                    routing_table[(network_address, subnet_mask)] = (0,
                                                                     ip_address,
                                                                     GlobalParameters.DEFAULT_TIME_FOR_LOCAL_INTERFACES)
                    ''' log network with ip and subnet '''
                    Helper.log2(ip_address, subnet_mask)

    return routing_table
