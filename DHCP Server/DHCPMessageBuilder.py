import GlobalParameters
import DHCPDiscover
import DHCPRequest


class DHCPDiscoverBuilder:
    @staticmethod
    def get_DHCPDiscover_Object(data):

        # take index in data bytearray to point
        # first byte
        i = 0

        # keep op htype hlen and hops bytes
        # and move to next four bytes
        op, htype, hlen, hops = data[i:i + 4]
        i += 4

        xid, i = data[i:i + 4], i + 4

        secs, i = data[i:i + 2], i + 2
        flags, i = data[i:i + 2], i + 2

        # keep IP addresses and MAC address
        ciaddr, i = data[i:i + 4], i + 4
        yiaddr, i = data[i:i + 4], i + 4
        siaddr, i = data[i:i + 4], i + 4
        giaddr, i = data[i:i + 4], i + 4
        chaddr, i = data[i:i + 6], i + 6

        # skip MAC address unused bytes
        i += GlobalParameters.NUM_CHADDR_UNUSED_BYTES

        # skip BOOTP legacy bytes
        i += GlobalParameters.NUM_BOOTP_LEGACY_BYTES

        # keep magic cookie
        magic_cookie, i = data[i:i + 4], i + 4

        # initialize options dictionary
        options_dict = dict()

        while True:
            option_code, i = data[i], i + 1

            # if option code is Message type, then skip this 3 bytes,
            # since we already know message type is discovery
            if option_code == GlobalParameters.DHCP_MESSAGE_TYPE:
                i += 2
                continue

            # if option code is requested ip
            if option_code == GlobalParameters.REQUESTED_IP_CODE:
                # skip one byte of length
                i += 1
                requested_ip, i = data[i: i + 4], i + 4

                # add requested_ip in options dictionary
                options_dict[GlobalParameters.REQUESTED_IP_CODE] = requested_ip

                continue

            # if option code is dhcp server identifier
            if option_code == GlobalParameters.DHCP_SERVER_IDENTIFIER:
                # skip length byte
                i += 1
                dhcp_server, i = data[i: i + 4], i + 4

                options_dict[GlobalParameters.DHCP_SERVER_IDENTIFIER] = dhcp_server
                continue

            # if option code is end
            if option_code == GlobalParameters.END_OPTION_CODE:
                i += 1
                break

            if option_code == GlobalParameters.PARAMETER_REQUEST_LIST_CODE:
                # take length byte and move one byte forward
                length, i = data[i], i + 1

                requested_parameter_list = list()
                for indx in range(length):
                    requested_parameter_list.append(data[i])
                    i += 1
                options_dict[GlobalParameters.PARAMETER_REQUEST_LIST_CODE] = requested_parameter_list
                continue

            # take length and skip its byte
            length, i = data[i], i + 1
            # skip this options body
            i = i + length

        # take dhcpdiscover from taken parameters
        dhcp_message = DHCPDiscover.DHCPDiscover(op, htype, hlen, hops, xid, secs, flags,
                                                 ciaddr, yiaddr, siaddr, giaddr, chaddr,
                                                 magic_cookie, options_dict)

        return dhcp_message

    @staticmethod
    def get_DHCPRequest_Object(data):
        dm = DHCPDiscoverBuilder.get_DHCPDiscover_Object(data)

        ''' extract whole parameters from dhcp discovery'''
        op = dm.get_op()
        htype = dm.get_htype()
        hlen = dm.get_hlen()
        hops = dm.get_hops()

        xid = dm.get_xid()
        secs = dm.get_secs()
        flags = dm.get_flags()

        ciaddr = dm.get_ciaddr()
        yiaddr = dm.get_yiaddr()
        siaddr = dm.get_siaddr()
        giaddr = dm.get_giaddr()
        chaddr = dm.get_chaddr()

        magic_cookie = dm.get_magic_cookie()
        options_dict = dm.get_options_dict()

        ''' construct DHCP Reqeust from these parameters and return it '''
        request_message = DHCPRequest.DHCPRequest(op, htype, hlen, hops, xid, secs, flags,
                                                  ciaddr, yiaddr, siaddr, giaddr, chaddr,
                                                  magic_cookie, options_dict)

        return request_message
