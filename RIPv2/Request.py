import socket
import time
import threading

import RipEntry
import Helper
import Message
import GlobalParameters

""" This method takes source of request and
    responses it by routing table entries
"""


def handle_request(rip_message, sock, src_server, routing_table):

    print(str(sock))
    entries = rip_message.get_entries()

    current_time = int(time.time())

    response_entries = list()

    GlobalParameters.logging_lock.acquire()
    print("\nReceived request from " + src_server[0] + " for:")

    ''' for every entry '''
    for entry in entries:
        network = entry.get_ip_address()
        mask = entry.get_subnet_mask()
        ''' log network '''
        Helper.log2(network, mask)

        ''' check for whole routing table request '''
        if network == GlobalParameters.LISTEN_ALL_INTERFACES:
            ''' get entries by split horizon principle'''
            response_entries = routing_table_to_entries(routing_table, src_server[0])
            break
        else:
            GlobalParameters.routing_table_lock.acquire()
            (hop_count, src_ip, last_updated) = routing_table[(network, mask)]
            routing_table.release()

            ''' increase metric by one'''
            if hop_count < GlobalParameters.INFINITY_HOP_COUNT:
                hop_count += 1

            ''' check entry for invalid timer expiration '''
            if current_time - last_updated > GlobalParameters.INVALID_TIMER_DEFAULT_SECONDS\
                    and last_updated > 0:
                hop_count = GlobalParameters.INFINITY_HOP_COUNT
                routing_table[(network, mask)] = (hop_count, src_ip, current_time)

            rsp_entry = RipEntry.RipEntry(GlobalParameters.ADDRESS_FAMILY,
                                          GlobalParameters.ROUTE_TAG,
                                          network,
                                          mask,
                                          GlobalParameters.NEXT_HOP_ZERO,
                                          hop_count)

            ''' don't send back to neighbours '''
            if src_ip != src_server[0]:
                response_entries.append(rsp_entry)

    print("\nSending response to " + src_server[0])

    for entry in response_entries:
        Helper.log(entry.get_ip_address(), entry.get_subnet_mask(), entry.get_metric())

    GlobalParameters.logging_lock.release()

    ''' constract messages with 25 entries at maximum '''
    while len(response_entries) > 0:
        ''' construct message '''
        result_list, response_entries = Helper.pop_first_n_element(response_entries,
                                                                   GlobalParameters.MAX_NUMBER_OF_ENTRIES)

        rip_message = Message.Message(GlobalParameters.RESPONSE,
                                      GlobalParameters.RIPv2_VERSION,
                                      GlobalParameters.UNUSED,
                                      result_list)
        ''' take message bytes '''
        message_bytes = Helper.message_to_bytes(rip_message)

        sock.sendto(message_bytes, src_server)



''' This method takes routing entry and source_ip, and from routing table
    constructs a list of entries, source_ip of which is different from sender_ip
'''


def routing_table_to_entries(routing_table, sender_ip):

    entries_list = list()

    current_time = int(time.time())

    GlobalParameters.routing_table_lock.acquire()
    for (network, mask) in routing_table:
        (hop_count, src_ip, last_updated) = routing_table[(network, mask)]

        ''' increase metric '''
        if hop_count < GlobalParameters.INFINITY_HOP_COUNT:
            hop_count += 1
        ''' check for time expiration '''
        if current_time - last_updated > GlobalParameters.INVALID_TIMER_DEFAULT_SECONDS \
                and last_updated > 0:
            hop_count = GlobalParameters.INFINITY_HOP_COUNT
            routing_table[(network, mask)] = (hop_count, src_ip, current_time)

        ''' construct entry and add to entries_list'''
        entry = RipEntry.RipEntry(GlobalParameters.ADDRESS_FAMILY,
                                  GlobalParameters.ROUTE_TAG,
                                  network,
                                  mask,
                                  GlobalParameters.NEXT_HOP_ZERO,
                                  hop_count)
        if src_ip != sender_ip:
            entries_list.append(entry)

    GlobalParameters.routing_table_lock.release()

    return entries_list
