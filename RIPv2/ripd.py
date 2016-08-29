""" Library imports
"""
import netifaces
import struct
import socket
import sys
import _thread
import threading
import time

import Helper
import Message
import RipEntry
import Interfaces
import Request
import Response
import GlobalParameters

''' Global containers '''
routing_table = Interfaces.scann_interfaces()
neighbours_list = list()

''' This is infinite thread which in every 30 seconds sends
    update to its neighbours by split horizon '''


def split_horizon(sock):

    while True:

        ''' sleep thread for 30 seconds '''
        time.sleep(GlobalParameters.UPDATE_TIME_INTERVAL_SECONDS)

        ''' log routing table'''
        current_time = int(time.time())

        GlobalParameters.logging_lock.acquire()
        print("\nSending update...")

        # lock neighbours list
        GlobalParameters.neighbours_lock.acquire()

        ''' take each neighbour from neighbours list '''
        for neighbour in neighbours_list:
            entry_list = list()
            ''' construct message from routing table for neighbour '''

            # lock routing table
            GlobalParameters.routing_table_lock.acquire()

            print("Sending update to " + neighbour)

            for (network, mask) in routing_table:

                (hop_count, src_ip, last_update_time) = routing_table[(network, mask)]
                ''' don't send message back to neighbour '''
                if src_ip == neighbour:
                    continue

                ''' increase hop count '''
                if hop_count < GlobalParameters.INFINITY_HOP_COUNT:
                    hop_count += 1

                ''' check if 180 seconds passed without update
                    on this entry
                '''
                if current_time - last_update_time > GlobalParameters.INVALID_TIMER_DEFAULT_SECONDS \
                        and last_update_time > 0:
                    hop_count = GlobalParameters.INFINITY_HOP_COUNT
                    ''' update routing table entry metric as infinite '''
                    routing_table[(network, mask)] = (hop_count, src_ip, current_time)

                ''' log this entry '''
                Helper.log(network, mask, hop_count)

                entry = RipEntry.RipEntry(GlobalParameters.ADDRESS_FAMILY,
                                          GlobalParameters.ROUTE_TAG,
                                          network,
                                          mask,
                                          GlobalParameters.NEXT_HOP_ZERO,
                                          hop_count)

                entry_list.append(entry)
            GlobalParameters.routing_table_lock.release()

            ''' make 25-25 entry messages and send them one-by-one '''
            while len(entry_list) > 0:
                ''' construct message '''
                result_list, entry_list = Helper.pop_first_n_element(entry_list,
                                                                     GlobalParameters.MAX_NUMBER_OF_ENTRIES)

                ''' get message '''
                rip_message = Message.Message(GlobalParameters.RESPONSE,
                                              GlobalParameters.RIPv2_VERSION,
                                              GlobalParameters.UNUSED,
                                              result_list)
                ''' take message bytes '''
                message_bytes = Helper.message_to_bytes(rip_message)
                ''' send message '''
                neighbour_address = (neighbour, GlobalParameters.RIP_PORT)
                sock.sendto(message_bytes, neighbour_address)

        # release locks
        GlobalParameters.logging_lock.release()
        GlobalParameters.neighbours_lock.release()


request = Helper.construct_first_request()
multi_cast_address = (GlobalParameters.IP_MULTI_CAST_ADDRESS,
                      GlobalParameters.RIP_PORT)

''' setup socket and start server '''

print("\nStart listening on socket UDP 520")

''' set socket listening to multi casts and reusable port '''

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                   socket.IPPROTO_UDP) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((GlobalParameters.IP_MULTI_CAST_ADDRESS,
                        GlobalParameters.RIP_PORT))

    server_socket.setsockopt(socket.IPPROTO_IP,
                             socket.IP_MULTICAST_TTL,
                             GlobalParameters.TTL)

    server_socket.setsockopt(socket.IPPROTO_IP,
                             socket.IP_ADD_MEMBERSHIP,
                             socket.inet_aton(GlobalParameters.IP_MULTI_CAST_ADDRESS) +
                             socket.inet_aton(GlobalParameters.LISTEN_ALL_INTERFACES))

    print("\nSending request to 224.0.0.9")
    sent = server_socket.sendto(request, multi_cast_address)

    ''' Send multi cast request to neighbours '''

    _thread.start_new_thread(split_horizon, (server_socket,))

    ''' Run server '''
    while True:

        ''' get byte data from socket '''
        data, server = server_socket.recvfrom(GlobalParameters.MAX_NUMBER_OF_RECEIVED_BYTES)
        message = Helper.bytes_to_message(data)
        neighbour_ip = server[0]

        ''' lock and update neighbours list '''
        GlobalParameters.neighbours_lock.acquire()
        if neighbour_ip not in neighbours_list:
            neighbours_list.append(neighbour_ip)
        GlobalParameters.neighbours_lock.release()

        ''' assert version number to be 2 '''
        if message.get_version() != GlobalParameters.RIPv2_VERSION:
            GlobalParameters.logging_lock.acquire()
            print("Not RIPv2 version. Nothing to respond\n")
            GlobalParameters.logging_lock.release()
            continue

        if message.get_command() is GlobalParameters.REQUEST:
            Request.handle_request(message, server_socket, server, routing_table)
        else:
            Response.handle_response(message, server, routing_table)
