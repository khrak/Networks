import sys
import socket
import json
import _thread
import time

import Helper
import GlobalParameters
import DHCPMessageBuilder
import OfferHandler
import RequestHandler

''' get path to config file '''
config_file_name = sys.argv[1]

''' read file and converts its content to json '''
config_file = open(config_file_name, "r")
config_content = config_file.read()
config_json = json.loads(config_content)

lease_time = config_json[GlobalParameters.CONFIG_LEASE]

''' this method is infinite thread, which in every one second
    updates record table. Removes time expired entries from it. '''


def update_record_table(record_table, lease_time):

    while True:
        time.sleep(1)

        for record in record_table:
            (mac, update_time) = record_table[record]
            current_time = int(time.time())
            # check if lease time has passed
            if current_time - update_time > lease_time:
                del record_table[record]


''' dictionary of Acked ip addresses. key is ip address,
    value is (mac_address, offer_moment) tuple '''

record_table = dict()
# start thread which periodically updates record table
thread = _thread.start_new_thread(update_record_table, (record_table, lease_time, ))

''' dictionary of offered ip addresses. key is mac
    address of client and value is ip address which we
    offered him. '''

offer_Table = dict()

# setup socket to listen broadcasts
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((GlobalParameters.BROADCAST_IP_ADDRESS, 67))

while True:
    data, address = sock.recvfrom(4096)
    message_type = Helper.get_message_type(data)

    builder = DHCPMessageBuilder.DHCPDiscoverBuilder()

    if message_type == GlobalParameters.DHCP_DISCOVERY:
        message = builder.get_DHCPDiscover_Object(data)
        offer_bytes = OfferHandler.handle_discovery(message, config_json, record_table, offer_Table)
        sock.sendto(offer_bytes, ('255.255.255.255', 68))
        continue

    if message_type == GlobalParameters.DHCP_REQUEST:
        message = builder.get_DHCPRequest_Object(data)
        ack_bytes = RequestHandler.handle_request(message, config_json, record_table, offer_Table)
        if ack_bytes is not None:
            sock.sendto(ack_bytes, ('255.255.255.255', 68))
        continue

thread.join()