# library imports
import socket
import sys

# local file imports
import Packet
import Tools
import Constructor
import Resolver
import Root_Servers
import Authority_Server

# take config directory path
config_dir_path = sys.argv[1]

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 53)
print("start DNS server...")
sock.bind(server_address)

root_servers = Root_Servers.RootServers()

while True:
    data, address = sock.recvfrom(4096)

    client_packet = Packet.Packet(data)

    # keep parameters for response header
    num_questions = 0
    num_answers = 0
    num_authority = 0
    num_additional = 0

    # keep byte data for each fields
    question_data = bytearray()
    answer_data = bytearray()
    authority_data = bytearray()
    additional_data = bytearray()

    for question in client_packet.questions:
        # keep new question byte data and increase its count
        question_data += Constructor.question_to_bytes(question)
        num_questions += 1

        # if zone file exists locally
        if Tools.zone_file_exists(question.q_name, config_dir_path) is True:
            answer_packet = Authority_Server.get_authority_data(client_packet, config_dir_path)

            # here we assume that local zone file contains only answer fields
            # since our sample file on classroom was like this
            for answer in answer_packet.answers:
                answer_data += Constructor.answer_to_bytes(answer)
                num_answers += 1

            continue
        # choose root server ip address
        server_ip = root_servers.get_root_server()

        # here we already have got resolved packet object
        resolved_packet = Resolver.resolve(question.q_name, question.q_type, question.q_class, server_ip)

        if resolved_packet is None:
            print("send error code: resolved packet is None")
            continue

        for answer in resolved_packet.answers:
            answer_data += Constructor.answer_to_bytes(answer)
            num_answers += 1

        for authority in resolved_packet.authorities:
            authority_data += Constructor.authority_to_bytes(authority)
            num_authority += 1

        for additional in resolved_packet.additionals:
            additional_data += Constructor.additional_to_bytes(additional)
            num_additional += 1

    client_packet.header.flags |= 0x8080
    response_data = Constructor.construct_header(client_packet.header.id, client_packet.header.flags,
                                                 num_questions,
                                                 num_answers,
                                                 num_authority,
                                                 num_additional)

    response_data += question_data + answer_data + authority_data + additional_data

    sock.sendto(response_data, address)

    print("end here!")
