import random
from ipaddress import IPv6Address
import socket
import struct
from os import listdir
from os.path import isfile, join

import Constants

''' This method checks is byte is representation of an offset
byte. Returns true if its offset byte and false otherwise '''


def is_offset_byte(byte):
    offset_bits = (1 << 7) + (1 << 6)
    return byte & offset_bits > 0


''' This method returns 2 byte random number '''


def random_int():
    lower_bound = 0
    upper_bound = (1 << 16) - 1
    return random.randint(lower_bound, upper_bound)


''' This method takes dns packet data and offset where it starts construction
    of string. It constructs string considering compression rules and returns
    first byte offset of Question Type '''


def get_compressed_text(dns_packet_data, offset):
    q_name = ""

    while True:
        octet = dns_packet_data[offset]
        # check octet if its offset byte
        if is_offset_byte(octet):
            # return string and point offset one byte right
            new_off = int.from_bytes(dns_packet_data[offset: offset + 2],
                                     byteorder=Constants.INTERNET_ENDIANNESS)
            # remove preceding 11 bits and get offset
            new_off &= 0x3fff
            recursive_string = recursive_construction(dns_packet_data, new_off)
            if len(q_name) > 0 and not q_name.endswith("."):
                q_name += "."
            return q_name + recursive_string, offset + 2

        if octet == 0:
            return q_name, offset + 1

        for i in range(octet):
            q_name += chr(dns_packet_data[offset + i + 1])
        # increase offset to point next length octet
        offset += octet + 1

        if dns_packet_data[offset] != 0 and not q_name.endswith("."):
            q_name += "."

    return None, 0


''' This method takes dns packet data and offset from headers first byte.
    Finds string, which starts from this offset and keeps it, or at some step
    expands recursively if this string contains some more offset strings. '''


def recursive_construction(dns_packet_data, offset):
    q_name = ""

    while offset < len(dns_packet_data):
        octet = dns_packet_data[offset]
        # check if it contains offset string
        if is_offset_byte(octet):
            # get offset string and concatenate
            octet = int.from_bytes(dns_packet_data[offset: offset + 2],
                                   byteorder=Constants.INTERNET_ENDIANNESS)
            octet &= 0x3fff
            if len(q_name) > 0 and not q_name.endswith("."):
                q_name += "."
            q_name += recursive_construction(dns_packet_data, octet)
            break
            # check if string ended
        if octet == 0:
            break

        # concatenate q_name to octet length string
        for i in range(octet):
            q_name += chr(dns_packet_data[offset + i + 1])

        # update offset value to point right after the end
        # of octet length string
        offset += octet + 1
        if dns_packet_data[offset] != 0 and not q_name.endswith("."):
            q_name += "."

    return q_name


''' This method takes dns packet data, answer type and offset where response
    data starts, and base on answer type, returns response data '''


def get_response_data(dns_packet_data, a_type, rd_length, offset):

    # check if type is MX
    if a_type == Constants.MX:
        # take preference
        preference = int.from_bytes(dns_packet_data[offset: offset + 2],
                                    byteorder=Constants.INTERNET_ENDIANNESS)
        # skip 2 byte integer
        offset += 2
        exchange, offset = get_compressed_text(dns_packet_data, offset)

        response_data = str(preference) + " " + exchange
        return response_data, offset

    # check if type is A
    if a_type == Constants.A:
        decimal_ip = int.from_bytes(dns_packet_data[offset: offset + 4],
                                    byteorder=Constants.INTERNET_ENDIANNESS)

        response_data = socket.inet_ntoa(struct.pack('!L', decimal_ip))
        # skip ip addres bytes
        offset += 4

        return response_data, offset

    # check if type is TXT
    if a_type == Constants.TXT:
        text = ""

        text_length = dns_packet_data[offset]
        offset += 1

        # read text
        for i in range(text_length):
            text += chr(dns_packet_data[offset + i])
        # update offset value
        offset += text_length

        return text, offset

    # check if type is NS or cname
    if a_type == Constants.NS or a_type == Constants.CNAME:
        name_server, offset = get_compressed_text(dns_packet_data, offset)
        return name_server, offset

    # check if type is AAAA
    if a_type == Constants.AAAA:
        decimal_ipv6 = int.from_bytes(dns_packet_data[offset: offset + 16],
                                      byteorder=Constants.INTERNET_ENDIANNESS)
        ipv6 = str(IPv6Address(decimal_ipv6))
        offset += 16
        return ipv6, offset

    # check if type is SOA
    if a_type == Constants.SOA:
        response_data, offset = get_soa_response(dns_packet_data, offset)
        return response_data, offset

    # if type is unknown
    response_data = dns_packet_data[offset: offset + rd_length]
    offset += rd_length
    return response_data, offset


''' This method takes dns packet data and offset which points to
    the first byte of response data of soa type field. It extraces
    soa fields and returns them as string. '''


def get_soa_response(dns_packet_data, offset):
    primary_name, offset = get_compressed_text(dns_packet_data, offset)
    r_name, offset = get_compressed_text(dns_packet_data, offset)

    serial_number = int.from_bytes(dns_packet_data[offset: offset + 4],
                                   byteorder=Constants.INTERNET_ENDIANNESS)
    offset += 4

    refresh_number = int.from_bytes(dns_packet_data[offset: offset + 4],
                                    byteorder=Constants.INTERNET_ENDIANNESS)
    offset += 4

    retry = int.from_bytes(dns_packet_data[offset: offset + 4],
                           byteorder=Constants.INTERNET_ENDIANNESS)
    offset += 4

    expire = int.from_bytes(dns_packet_data[offset: offset + 4],
                            byteorder=Constants.INTERNET_ENDIANNESS)
    offset += 4

    minimum = int.from_bytes(dns_packet_data[offset: offset + 4],
                             byteorder=Constants.INTERNET_ENDIANNESS)
    offset += 4

    response_data = primary_name + " " + r_name + " " + str(serial_number)
    response_data += " " + str(refresh_number) + " " + str(retry) + " " + str(expire)
    response_data += " " + str(minimum)

    return response_data, offset

''' This method takes int representation of a type
    and returns its string value '''


def type_to_string(type_number):
    if type_number == Constants.A:
        return "A"

    if type_number == Constants.AAAA:
        return "AAAA"

    if type_number == Constants.NS:
        return "NS"

    if type_number == Constants.MX:
        return "MX"

    if type_number == Constants.SOA:
        return "SOA"

    if type_number == Constants.TXT:
        return "TXT"

    if type_number == Constants.CNAME:
        return "CNAME"

    if type_number == Constants.ANY:
        return "ANY"

    return "TYPE257"


''' This method takes string type and returns its corresponding
    two byte integer. '''


def type_to_short(type_string):

    if type_string == "A":
        return Constants.A

    if type_string == "AAAA":
        return Constants.AAAA

    if type_string == "NS":
        return Constants.NS

    if type_string == "MX":
        return Constants.MX

    if type_string == "SOA":
        return Constants.SOA

    if type_string == "TXT":
        return Constants.TXT

    if type_string == "CNAME":
        return Constants.CNAME

    return Constants.ANY


''' This method takes int representation of a class
    and returns its string value '''


def class_to_string(class_number):
    if class_number == 0x0001:
        return "IN"

    return "UNKNOWN"


''' This method checks whether zone file exists
    in path directory '''


def zone_file_exists(zone, path):
    all_files = [f for f in listdir(path)
                 if isfile(join(path, f))]

    for file in all_files:
        if file == zone:
            return True
    return False
