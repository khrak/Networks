from easyzone import easyzone

import Answer
import Tools
import Presenter

''' This file takes client packet and config directory path,
    searches zone file in directory, extracts demanded information
    and returns it as byte data. '''


def get_authority_data(packet, config_dir):
    zone_file_name = packet.questions[0].q_name

    z = easyzone.zone_from_file(zone_file_name,
                                config_dir + "/" + zone_file_name)

    types_list = ["A", "AAAA", "MX", "NS", "SOA", "TXT", "CNAME"]

    requested_type = packet.questions[0].q_type

    for name in z.names:
        value = z.names.get(name)

        for dns_type in types_list:
            if value.records(dns_type) is not None:

                # check if this type of field is required by client
                if Tools.type_to_short(dns_type) == requested_type or \
                                Tools.type_to_short("ANY") == requested_type:

                    data_items = value.records(dns_type).items

                    # iterate over all item, construct answer from it
                    # and add keep its byte data
                    for data_item in data_items:
                        # tricky case, zone returns tuple so we
                        # remake it as string
                        if dns_type == "MX":
                            data_item = str(data_item[0]) + \
                                        ' ' + str(data_item[1])

                        answer = Answer.Answer(z.domain,
                                               Tools.type_to_short(dns_type),
                                               0x0001,
                                               value.ttl,
                                               len(data_item),
                                               data_item)
                        packet.add_answer(answer)

    # log this packet
    Presenter.print_packet(packet)
    return packet
