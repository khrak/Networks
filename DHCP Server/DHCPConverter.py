import DHCPOffer
import GlobalParameters
import struct
import socket

"""
    This class takes DHCPMessage object and converts it
    to byte array.
"""

''' This method takes four byte integer and returns
    an array of four bytes.
'''


def int_to_bytes(k):
    return struct.pack('!L', k)


''' This method takes two byte integer and returns
    an array of two bytes
'''


def short_to_bytes(k):
    return struct.pack('!H', k)


class DHCPConverter:
    @staticmethod
    def get_DHCPOffer_bytes(offer):
        byte_data = bytearray()

        # add first four bytes
        byte_data.append(offer.get_op())
        byte_data.append(offer.get_htype())
        byte_data.append(offer.get_hlen())
        byte_data.append(offer.get_hops())

        # add xid four bytes
        byte_data += int_to_bytes(offer.get_xid())

        # add two two byte parameters
        byte_data += short_to_bytes(offer.get_secs())
        byte_data += short_to_bytes(offer.get_flags())

        # add ip addresses
        byte_data += int_to_bytes(offer.get_ciaddr())
        byte_data += int_to_bytes(offer.get_yiaddr())
        byte_data += int_to_bytes(offer.get_siaddr())
        byte_data += int_to_bytes(offer.get_giaddr())

        # add mac address
        byte_data += offer.get_chaddr()
        # add mac padding bytes
        byte_data += bytes(10)
        # add bootp legacy bytes
        byte_data += bytes(192)

        # add magic cookie
        byte_data += int_to_bytes(offer.get_magic_cookie())

        # add DHCP message type code
        byte_data.append(GlobalParameters.DHCP_MESSAGE_TYPE)
        # add length byte
        byte_data.append(1)
        # add offer type
        byte_data.append(GlobalParameters.DHCP_OFFER)

        options = offer.get_options_dict()

        for key in options:
            if key == GlobalParameters.OFFER_DHCP_SERVER or \
                            key == GlobalParameters.OFFER_LEASE_TIME or \
                            key == GlobalParameters.OFFER_ROUTER or \
                            key == GlobalParameters.OFFER_SUBNET_MASK:

                # add option code
                byte_data.append(key)
                # add length
                byte_data.append(4)
                # add option value
                byte_data += int_to_bytes(options[key])
                continue

            if key == GlobalParameters.OFFER_DNS_SERVERS:
                lst = options[key]
                # get parameters count
                dns_servers_count = len(lst)
                # get num bytes for dns server addresses
                num_bytes = dns_servers_count * 4

                # add option code
                byte_data.append(key)
                # add byte length
                byte_data.append(num_bytes)

                # iterate over dns servers an add them in bytes
                for dns_server in lst:
                    byte_data += int_to_bytes(dns_server)

        # end of options
        byte_data.append(255)

        return byte_data

    @staticmethod
    def get_DHCPACK_bytes(ack, ack_type):
        byte_data = bytearray()

        # add first four bytes
        byte_data.append(ack.get_op())
        byte_data.append(ack.get_htype())
        byte_data.append(ack.get_hlen())
        byte_data.append(ack.get_hops())

        # add xid four bytes
        byte_data += int_to_bytes(ack.get_xid())

        # add two two byte parameters
        byte_data += short_to_bytes(ack.get_secs())
        byte_data += short_to_bytes(ack.get_flags())

        # add ip addresses
        byte_data += int_to_bytes(ack.get_ciaddr())
        byte_data += int_to_bytes(ack.get_yiaddr())
        byte_data += int_to_bytes(ack.get_siaddr())
        byte_data += int_to_bytes(ack.get_giaddr())

        # add mac address
        byte_data += ack.get_chaddr()
        # add mac padding bytes
        byte_data += bytes(10)
        # add bootp legacy bytes
        byte_data += bytes(192)

        # add magic cookie
        byte_data += int_to_bytes(ack.get_magic_cookie())

        # add DHCP message type code
        byte_data.append(GlobalParameters.DHCP_MESSAGE_TYPE)
        # add length byte
        byte_data.append(1)
        # add ack type
        byte_data.append(ack_type)

        options = ack.get_options_dict()

        for key in options:
            if key == GlobalParameters.ACK_DHCP_SERVER or \
                            key == GlobalParameters.ACK_LEASE_TIME or \
                            key == GlobalParameters.ACK_ROUTER or \
                            key == GlobalParameters.ACK_SUBNET_MASK:

                # add option code
                byte_data.append(key)
                # add length
                byte_data.append(4)
                # add option value
                byte_data += int_to_bytes(options[key])
                continue

            if key == GlobalParameters.ACK_DNS_SERVERS:
                lst = options[key]
                # get parameters count
                dns_servers_count = len(lst)
                # get num bytes for dns server addresses
                num_bytes = dns_servers_count * 4

                # add option code
                byte_data.append(key)
                # add byte length
                byte_data.append(num_bytes)

                # iterate over dns servers an add them in bytes
                for dns_server in lst:
                    byte_data += int_to_bytes(dns_server)

        # end of options
        byte_data.append(255)

        return byte_data
