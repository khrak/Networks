import Constructor
import Packet
import Constants
import Presenter
import Tools


import socket

''' This method takes demanded domain name, type of question
    fields and question class. Also it takes server ip where
    this question will be resolved.
'''


def resolve(d_name, q_type, q_class, server_ip):
    # this is packet we will send to client
    demanded_packet = None

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(Constants.DNS_RECURSION_MAX_DEPTH):
        random_id = Tools.random_int()
        data = Constructor.construct_header(random_id, 0x0100, 0x1, 0, 0, 0)
        data += Constructor.construct_question(d_name, q_type, q_class)

        server_address = (server_ip, Constants.DNS_PORT_NUMBER)

        sock.sendto(data, server_address)

        response_data, server = sock.recvfrom(4096)

        packet = Packet.Packet(response_data)

        Presenter.print_packet(packet)

        # check if its authoritative answer
        if packet.header.authoritative_answer:
            demanded_packet = packet
            break
        else:
            if len(packet.additionals) == 0:
                print("No additionals found")
                break
            for additional in packet.additionals:
                if additional.a_type == 0x0001:
                    server_ip = additional.data
                    break

    sock.close()

    return demanded_packet
