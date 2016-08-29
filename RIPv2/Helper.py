import struct
import socket

import Message
import GlobalParameters
import RipEntry

""" This method takes string st and adds it spaces
    at the end to make its size equal to sizet
"""


def lengthen_string_to_sizet(st, sizet):
    while len(st) < sizet:
        st += " "

    return st


''' This method takes bytes data and constructs message
    object from it
'''


def bytes_to_message(byte_data):
    byte_indx = 4
    ''' list f entries '''
    entries = list()

    while byte_indx < len(byte_data):
        address_family_bytes = byte_data[byte_indx: byte_indx + 2]
        address_family = struct.unpack('!h', address_family_bytes)[0]

        route_tag_bytes = byte_data[byte_indx + 2: byte_indx + 4]
        route_tag = struct.unpack('h', route_tag_bytes)[0]

        ip_address_bytes = byte_data[byte_indx + 4: byte_indx + 8]
        ip_address = socket.inet_ntoa(struct.pack("!I",
                                                  struct.unpack('!I', ip_address_bytes)[0]))

        subnet_mask_bytes = byte_data[byte_indx + 8: byte_indx + 12]
        subnet_mask = socket.inet_ntoa(struct.pack("!I", struct.unpack('!I', subnet_mask_bytes)[0]))

        next_hop_bytes = byte_data[byte_indx + 12: byte_indx + 16]
        next_hop = socket.inet_ntoa(struct.pack("!I", struct.unpack('!I', next_hop_bytes)[0]))

        metric_bytes = byte_data[byte_indx + 16: byte_indx + 20]
        metric = struct.unpack('!I', metric_bytes)[0]

        ''' create new entry '''
        entry = RipEntry.RipEntry(address_family, route_tag, ip_address, subnet_mask, next_hop, metric)

        ''' add new entry to list '''
        entries.append(entry)

        ''' go to next entry starting position '''
        byte_indx += 20

    ''' get header fields '''
    command_byte = byte_data[0:1]
    command = struct.unpack('b', command_byte)[0]

    version_byte = byte_data[1:2]
    version = struct.unpack('b', version_byte)[0]

    unused_byte = byte_data[2:4]
    unused = struct.unpack('!h', unused_byte)[0]

    message = Message.Message(command, version, unused, entries)

    return message

''' this method takes message object and constructs byte data from it '''


def message_to_bytes(rip_message):

    message_bytes = struct.pack('b', rip_message.get_command())
    message_bytes += struct.pack('b', rip_message.get_version())
    message_bytes += struct.pack('h', rip_message.get_unused())

    entries = rip_message.get_entries()

    for entry in entries:
        message_bytes += struct.pack('!h', entry.get_address_family())
        message_bytes += struct.pack('!h', entry.get_route_tag())

        ip_integer = struct.unpack(">I", socket.inet_aton(entry.get_ip_address()))[0]
        message_bytes += struct.pack("!I", ip_integer)

        mask_integer = struct.unpack(">I", socket.inet_aton(entry.get_subnet_mask()))[0]
        message_bytes += struct.pack("!I", mask_integer)

        next_hop = struct.unpack(">I", socket.inet_aton(entry.get_next_hop()))[0]
        message_bytes += struct.pack("!I", next_hop)

        message_bytes += struct.pack('!I', entry.get_metric())

    return message_bytes


''' This method constructs request which will be sent only
    once. Converts this message to byte and returns it in byte
    form
'''


def construct_first_request():

    entry = RipEntry.RipEntry(0, 0, "0.0.0.0", "0.0.0.0", "0.0.0.0", GlobalParameters.INFINITY_HOP_COUNT)
    entry_list = list()
    entry_list.append(entry)

    rip_message = Message.Message(GlobalParameters.REQUEST,
                                  GlobalParameters.VERSION,
                                  GlobalParameters.UNUSED,
                                  entry_list)

    message_bytes = message_to_bytes(rip_message)

    return message_bytes

''' this method takes list and integer n. It constructs new list
    result by first n elements from list, removes firs n elements
    from original list and returns two new lists as tuple'''


def pop_first_n_element(elements, n):
    size_t = min(len(elements), n)

    result_list = elements[0:size_t]
    elements = elements[size_t:]

    return result_list, elements

''' this method logs network, subnet and metric parameters on terminal '''


def log(network, subnet, metric):
    network_str = lengthen_string_to_sizet("Network: " + network,
                                           GlobalParameters.SCANNING_INTERFACE_STRING_LENGTH)
    subnet_str = lengthen_string_to_sizet("Mask: " + subnet,
                                          GlobalParameters.SCANNING_INTERFACE_STRING_LENGTH)
    metric_str = lengthen_string_to_sizet("Metric: " + str(metric),
                                          GlobalParameters.SCANNING_INTERFACE_STRING_LENGTH)

    print(network_str + subnet_str + metric_str)

''' This method logs only ip address and subnet mask '''


def log2(network, subnet):
    network_str = lengthen_string_to_sizet("Network: " + network,
                                           GlobalParameters.SCANNING_INTERFACE_STRING_LENGTH)
    subnet_str = lengthen_string_to_sizet("Mask: " + subnet,
                                          GlobalParameters.SCANNING_INTERFACE_STRING_LENGTH)

    print(network_str + subnet_str)
