import socket
import struct
import ipaddress

import Tools
import Constants

''' This method takes data, headerID, flag bytes, Question count,
    Answer count, Authority count and Additional count
    and constructs header bytes using them and puts them in data
    and returns it.
'''


def construct_header(header_id, flags, q_count,
                     an_count, ath_count, add_count):
    data = bytearray()
    data += short_to_bytes(header_id)
    data += short_to_bytes(flags)
    data += short_to_bytes(q_count)
    data += short_to_bytes(an_count)
    data += short_to_bytes(ath_count)
    data += short_to_bytes(add_count)

    return data


''' This method takes question object and converts it
    to byte array. '''


def question_to_bytes(question):
    return construct_question(question.q_name,
                              question.q_type,
                              question.q_class)


''' This method takes data, q_name, q_type, q_class and
    constructs Question bytes using them and puts it in data
    and returns it.
'''


def construct_question(q_name, q_type, q_class):
    data = get_bytes_from_domain_name(q_name.split("."))
    # add Question type bytes
    data += short_to_bytes(q_type)
    # add Question class bytes
    data += short_to_bytes(q_class)

    return data


''' this method takes answer object and converts it
    to byte array. '''


def answer_to_bytes(answer):
    return construct_answer(answer.a_name, answer.a_type,
                            answer.a_class, answer.a_ttl,
                            answer.rdlength, answer.response_data)


''' This method takes a_name, a_type, a_class, ttl, rd_length and r_data
    parameters of Answer field and constructs answer bytes by them. '''


def construct_answer(a_name, a_type, a_class, ttl, rd_length, r_data):
    data = get_bytes_from_domain_name(a_name.split("."))
    data += short_to_bytes(a_type)
    data += short_to_bytes(a_class)
    data += int_to_bytes(ttl)

    byte_rdata = get_bytes_from_rdata(r_data, a_type, rd_length)

    data += short_to_bytes(len(byte_rdata))
    data += byte_rdata

    return data


''' This method takes authority object and converts it to bytes. '''


def authority_to_bytes(authority):
    return construct_byte_authority(authority.name,
                                    authority.a_type,
                                    authority.a_class,
                                    authority.ttl,
                                    authority.rd_length,
                                    authority.data)


''' This method takes authority parameters and constructs byte array by it. '''


def construct_byte_authority(a_name, a_type, a_class, ttl, rd_length, data):

    byte_data = get_bytes_from_domain_name(a_name.split("."))
    byte_data += short_to_bytes(a_type)
    byte_data += short_to_bytes(a_class)
    byte_data += int_to_bytes(ttl)
    byte_domain = get_bytes_from_rdata(data, a_type, rd_length)
    byte_data += short_to_bytes(len(byte_domain))
    byte_data += byte_domain

    return byte_data


''' This method takes additional object and converts it to bytes. '''


def additional_to_bytes(additional):
    return construct_byte_additional(additional.name,
                                     additional.a_type,
                                     additional.a_class,
                                     additional.ttl,
                                     additional.rd_length,
                                     additional.data)


''' This method takes authority parameters and constructs byte array by it. '''


def construct_byte_additional(a_name, a_type, a_class, ttl, rd_length, data):

    byte_data = get_bytes_from_domain_name(a_name.split("."))
    byte_data += short_to_bytes(a_type)
    byte_data += short_to_bytes(a_class)
    byte_data += int_to_bytes(ttl)
    r_data = get_bytes_from_rdata(data, a_type, rd_length)
    byte_data += short_to_bytes(len(r_data))
    byte_data += r_data

    return byte_data


''' This method takes r_data and its type and converts it to byte array. '''


def get_bytes_from_rdata(r_data, a_type, rd_length):
    # A
    if a_type == Constants.A:
        ip = struct.unpack("!I", socket.inet_aton(r_data))[0]
        return int_to_bytes(ip)

    # AAAA
    if a_type == Constants.AAAA:
        ipv6 = int(ipaddress.IPv6Address(r_data))
        return ipv6int_to_bytes(ipv6)

    # NS
    if a_type == Constants.NS:
        byte_data = get_bytes_from_domain_name(r_data.split("."))
        return get_bytes_from_domain_name(r_data.split("."))

    # MX
    if a_type == Constants.MX:
        preference, exchange = r_data.split(" ")
        data_bytes = short_to_bytes(int(preference))
        data_bytes += get_bytes_from_domain_name(exchange.split("."))

        return data_bytes

    # SOA
    if a_type == Constants.SOA:
        soa_parameters = r_data.split(" ")
        m_name = soa_parameters[0]
        r_name = soa_parameters[1]
        serial = soa_parameters[2]
        refresh = soa_parameters[3]
        retry = soa_parameters[4]
        expire = soa_parameters[5]
        minimum = soa_parameters[6]

        byte_data = get_bytes_from_domain_name(m_name.split("."))
        byte_data += get_bytes_from_domain_name(r_name.split("."))
        byte_data += int_to_bytes(int(serial))
        byte_data += int_to_bytes(int(refresh))
        byte_data += int_to_bytes(int(retry))
        byte_data += int_to_bytes(int(expire))
        byte_data += int_to_bytes(int(minimum))

        return byte_data

    # TXT
    if a_type == Constants.TXT:
        byte_data = bytes(r_data, 'utf-8')
        text_len = len(byte_data)
        r_data = chr(text_len) + r_data

        return bytes(r_data, 'utf-8')

    # CNAME
    if a_type == Constants.CNAME:
        return get_bytes_from_domain_name(r_data.split("."))

    # unknown
    return bytes(r_data)


''' This method converts 128 bit integer
    to byte data. '''


def ipv6int_to_bytes(ipv6):
    left_bytes = ipv6 >> 64
    right_bytes = ipv6 % (1 << 64)

    data = long_to_bytes(left_bytes)
    data += long_to_bytes(right_bytes)

    return data


''' This method converts 64 bit integer
    to byte data. '''


def long_to_bytes(long):
    left_bytes = long >> 32
    right_bytes = long % (1 << 32)

    data = int_to_bytes(left_bytes)
    data += int_to_bytes(right_bytes)

    return data


''' This method takes int type number, splits these bytes
    and adds in byte array one-by-one.
'''


def int_to_bytes(four_bytes):
    data = bytearray()
    data += short_to_bytes(four_bytes >> 16)
    data += short_to_bytes(four_bytes % (1 << 16))

    return data


''' This method takes short type number, splits these bytes
    and adds in byte array one-by-one.
'''


def short_to_bytes(two_bytes):
    # two_bytes = socket.htons(two_bytes)
    data = bytearray()
    data.append(two_bytes >> 8)
    data.append(two_bytes % (1 << 8))

    return data


def get_bytes_from_domain_name(domain_name_zones):
    domain_name_bytes = bytearray()

    for zone in domain_name_zones:
        if len(zone) > 0:
            zone_bytes = get_bytes(zone)
            for zone_byte in zone_bytes:
                domain_name_bytes.append(zone_byte)

    # indicated the end of string
    domain_name_bytes.append(0x00)
    return domain_name_bytes


def get_bytes(zone):
    arr = bytearray()
    arr.append(len(zone))
    for ch in zone:
        arr.append(ord(ch))

    return arr
