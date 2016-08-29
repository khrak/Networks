import time

import GlobalParameters
import Helper

""" This method takes bytes data of response sent by
    server and updates routing table by it.
"""


def handle_response(rip_message, src_server, routing_table):
    sender_ip, response_port = src_server

    GlobalParameters.logging_lock.acquire()

    print("\nRecived update from " + sender_ip)

    entries = rip_message.get_entries()

    current_time = int(time.time())

    ''' for every entry '''
    for entry in entries:
        key = (entry.get_ip_address(), entry.get_subnet_mask())
        (network, subnet_mask) = key

        ''' check network for 127.0.0.0/8, which we must ignore '''
        if (network, subnet_mask) == GlobalParameters.IGNORE_NETWORK:
            continue

        # lock routing table
        GlobalParameters.routing_table_lock.acquire()
        if key not in routing_table:
            ''' log better found route '''
            print("Better route found through " + sender_ip + " to")
            Helper.log(network, subnet_mask, entry.get_metric())

            routing_table[key] = (entry.get_metric(), sender_ip, current_time)

        else:
            (hop_count, src_ip, last_updated) = routing_table[key]
            ''' check for better route or for same source and network update '''
            if hop_count > entry.get_metric() or src_ip == sender_ip:
                routing_table[key] = (entry.get_metric(), sender_ip, current_time)

            if hop_count > entry.get_metric():
                print("Better route found through " + sender_ip + " to")
                Helper.log(network, subnet_mask, entry.get_metric())
            else:
                if src_ip == sender_ip:
                    Helper.log(network, subnet_mask, entry.get_metric())
        # release routing table
        GlobalParameters.routing_table_lock.release()
    # release logging
    GlobalParameters.logging_lock.release()
