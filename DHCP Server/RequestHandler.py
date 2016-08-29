import struct
import socket
import time

import DHCPAck
import GlobalParameters
import DHCPConverter

""" This method takes request message object,
    generates ack message and returns it's bytes
"""


def handle_request(message, cfg_json, record_table, offer_table):
    xid = struct.unpack('!L', message.get_xid())[0]
    ciaddr = struct.unpack('!L', message.get_ciaddr())[0]

    # take offered ip for this mac address
    mac_address_str = "%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB", message.get_chaddr())

    # if request is from other unknown client
    if mac_address_str not in offer_table:
        print("not offered")
        return None

    offered_ip = offer_table[mac_address_str]
    yiaddr = struct.unpack("!L", socket.inet_aton(offered_ip))[0]
    siaddr = struct.unpack("!L", socket.inet_aton(GlobalParameters.MY_SERVER_IP))[0]

    # get gateway from config file as string
    gate_way_ip = cfg_json[GlobalParameters.CONFIG_GATEWAY_IP_ADDRESS]
    # convert gateway ip as int and keep in giaddr
    giaddr = struct.unpack("!L", socket.inet_aton(gate_way_ip))[0]

    chaddr = message.get_chaddr()
    magic_cookie = struct.unpack("!L", message.get_magic_cookie())[0]

    # now we need to check whether client chose our offered
    # ip address or not, we need to take DHCP server from options

    options = message.get_options_dict()
    server_in_bytes = options[GlobalParameters.DHCP_SERVER_IDENTIFIER]
    # take server ip as string
    server_ip = socket.inet_ntoa(server_in_bytes)

    ack_type = None

    if server_ip == GlobalParameters.MY_SERVER_IP:
        ack_type = GlobalParameters.DHCP_ACK
    else:
        ack_type = GlobalParameters.DHCP_NACK

    options_dict = dict()
    options_dict[GlobalParameters.DHCP_SERVER_IDENTIFIER] = struct.unpack("!L",
                                                                          socket.inet_aton(
                                                                              GlobalParameters.MY_SERVER_IP))[0]
    options_dict[GlobalParameters.OFFER_ROUTER] = struct.unpack("!L",
                                                                socket.inet_aton(GlobalParameters.MY_SERVER_IP))[0]

    subnet_mask = cfg_json[GlobalParameters.CONFIG_SUBNET_MASK]
    options_dict[GlobalParameters.OFFER_SUBNET_MASK] = struct.unpack("!L", socket.inet_aton(subnet_mask))[0]
    options_dict[GlobalParameters.OFFER_LEASE_TIME] = cfg_json[GlobalParameters.CONFIG_LEASE]

    # take dns servers list as strings
    dns_servers = cfg_json[GlobalParameters.CONFIG_DNS]

    # here we'll keep dns server ips in integer formats
    int_dns = list()

    for dns in dns_servers:
        int_dns.append(struct.unpack("!L", socket.inet_aton(dns))[0])

    options_dict[GlobalParameters.OFFER_DNS_SERVERS] = int_dns

    ack = DHCPAck.DHCPAck(xid, ciaddr, yiaddr, siaddr, giaddr,
                          chaddr, magic_cookie, options_dict)

    # take bytes from offer
    converter = DHCPConverter.DHCPConverter()
    ack_bytes = converter.get_DHCPACK_bytes(ack, ack_type)

    # if DHCP server ip was chosen, we need to keep it in record table
    if ack_type == GlobalParameters.DHCP_ACK:
        acked_ip = offered_ip
        acked_mac = mac_address_str
        current_time = int(time.time())
        record_table[acked_ip] = (acked_mac, current_time)

    # since this ip is no in offered state, we remove it from
    # offer table
    del offer_table[mac_address_str]

    # return ack bytes
    return ack_bytes
