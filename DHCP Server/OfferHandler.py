# import standart libraries
import struct
import socket

# local imports
import GlobalParameters
import Arprequest
import DHCPOffer
import DHCPConverter

"""
    This class implements handler methods which are used when
    DHCP server gets discovery or request messages
"""

''' This method takes discovery message object,
    generates offer message and returns it's bytes
'''


def handle_discovery(disc_message, cfg_json, record_table, offer_table):
    # get ip address which we will give to client
    free_ip = get_ip_for_client(disc_message, cfg_json, record_table, offer_table)

    # now we definitely have free ip address
    xid = struct.unpack('!L', disc_message.get_xid())[0]
    ciaddr = struct.unpack('!L', disc_message.get_ciaddr())[0]
    yiaddr = struct.unpack("!L", socket.inet_aton(free_ip))[0]
    siaddr = struct.unpack("!L", socket.inet_aton(GlobalParameters.MY_SERVER_IP))[0]

    # get gateway from config file as string
    gate_way_ip = cfg_json[GlobalParameters.CONFIG_GATEWAY_IP_ADDRESS]
    # convert gateway ip as int and keep in giaddr
    giaddr = struct.unpack("!L", socket.inet_aton(gate_way_ip))[0]
    chaddr = disc_message.get_chaddr()
    magic_cookie = struct.unpack("!L", disc_message.get_magic_cookie())[0]

    # now we need to construct dictionary of options
    options = dict()
    options[GlobalParameters.DHCP_SERVER_IDENTIFIER] = struct.unpack("!L",
                                                                     socket.inet_aton(GlobalParameters.MY_SERVER_IP))[0]
    options[GlobalParameters.OFFER_ROUTER] = struct.unpack("!L",
                                                           socket.inet_aton(GlobalParameters.MY_SERVER_IP))[0]

    subnet_mask = cfg_json[GlobalParameters.CONFIG_SUBNET_MASK]
    options[GlobalParameters.OFFER_SUBNET_MASK] = struct.unpack("!L", socket.inet_aton(subnet_mask))[0]
    options[GlobalParameters.OFFER_LEASE_TIME] = cfg_json[GlobalParameters.CONFIG_LEASE]

    # take dns servers list as strings
    dns_servers = cfg_json[GlobalParameters.CONFIG_DNS]

    # here we'll keep dns server ips in integer formats
    int_dns = list()

    for dns in dns_servers:
        int_dns.append(struct.unpack("!L", socket.inet_aton(dns))[0])

    options[GlobalParameters.OFFER_DNS_SERVERS] = int_dns

    # construct offer
    offer = DHCPOffer.DHCPOffer(xid, ciaddr, yiaddr, siaddr, giaddr,
                                chaddr, magic_cookie, options)

    # take bytes from offer
    converter = DHCPConverter.DHCPConverter()
    offer_bytes = converter.get_DHCPOffer_bytes(offer)

    # return offer bytes
    return offer_bytes


''' This method return ip address which DHCP server will offer to client '''


def get_ip_for_client(disc_message, cfg_json, record_table, offer_table):
    # ip address which we will offer to client
    free_ip = None

    is_fixed, fixed_ip = check_for_rules(disc_message, cfg_json, offer_table)

    # if ip address for client mac address is specified
    # by config file, then return fixed ip address
    if is_fixed:
        return fixed_ip

    options_dict = disc_message.get_options_dict()

    # take client mac address in string form
    mac_address_str = "%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB", disc_message.get_chaddr())

    if GlobalParameters.REQUESTED_IP_CODE in options_dict:
        ip_in_bytes = options_dict[GlobalParameters.REQUESTED_IP_CODE]
        ip_integer = struct.pack('!L', ip_in_bytes)
        client_requested_ip = socket.inet_ntoa(struct.pack('!L', ip_integer))
        # check if client reqeusted ip is free
        ar = Arprequest.ArpRequest(client_requested_ip, 'wlan0', GlobalParameters.MY_SERVER_IP)
        # if not used, then keep ip in
        # string format and break
        if not ar.request():
            # keep in offer table that we offered client_requested_ip
            # to client with mac_address_st mac address
            offer_table[mac_address_str] = client_requested_ip
            return client_requested_ip

    # if client requested ip was not free, then we
    # need to find free ip address from our range

    # get client ip address in byte format
    client_ip = disc_message.get_ciaddr()
    clinet_ip_int = struct.pack('!L', client_ip)
    client_ip_str = socket.inet_ntoa(struct.pack('!L', clinet_ip_int))

    # check if client has this ip from our record table
    # and if so, return the same ip address
    if client_ip_str in record_table:
        offer_table[mac_address_str] = client_ip_str
        return client_ip_str

    # take from and to parameters from range in string formats
    range_dict = cfg_json[GlobalParameters.CONFIG_IP_ADDRESSES_RANGE]
    range_from_str = range_dict[GlobalParameters.CONFIG_RANGE_FROM]
    range_to_str = range_dict[GlobalParameters.CONFIG_RANGE_TO]

    # convert from and to ip parameters in integer formats
    range_from = struct.unpack("!L", socket.inet_aton(range_from_str))[0]
    range_to = struct.unpack("!L", socket.inet_aton(range_to_str))[0]

    # iterate from 'from' to 'to' values to find
    # ip which is unused yet
    integer_ip = range_from

    while integer_ip <= range_to:
        ip = socket.inet_ntoa(struct.pack('!L', integer_ip))

        # check if we have already acked this ip
        if ip in record_table:
            continue
        # sen arp request
        ar = Arprequest.ArpRequest(ip, 'wlan0', GlobalParameters.MY_SERVER_IP)
        # if not used, then keep ip in
        # string format and break
        if not ar.request():
            free_ip = ip
            break

    offer_table[mac_address_str] = free_ip

    return free_ip


''' This method takes discovery message and checks if
mac address of this message in ruled by config file '''


def check_for_rules(disc_message, cfg_json, offer_table):
    # take rules list
    rules_list = cfg_json[GlobalParameters.CONFIG_RULES]
    mac_address_str = "%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB", disc_message.get_chaddr())

    # iterate over rules
    for rule in rules_list:
        # take mac address from each rule
        mac_address = rule[GlobalParameters.CONFIG_RULES_MAC]
        # check if mac address are equal and return if it is
        if mac_address == mac_address_str:
            fix_address = rule[GlobalParameters.CONFIG_RULES_FIX_ADDRESS]
            # keep this offer
            offer_table[mac_address_str] = fix_address
            return True, fix_address

    return False, None
