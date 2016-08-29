import Tools
import Constants

'''' This class takes packet, goes through it and prints
    its parameters on stdout
'''


def print_packet(packet):

    if packet.header.num_questions > 0:
        print(";; QUESTION SECTION:")

    questions = packet.questions

    for question in questions:
        print(";" + fill_up_to(str(question.q_name),
                               Constants.DOMAIN_LENGTH),
              fill_up_to(Tools.class_to_string(question.q_class),
                         Constants.CLASS_LENGTH),
              fill_up_to(Tools.type_to_string(question.q_type),
                         Constants.TYPE_LENGTH))

    if packet.header.num_answers > 0:
        print("\n;;ANSWER SECTION:")

    for answer in packet.answers:

        print(fill_up_to(answer.a_name,
                         Constants.DOMAIN_LENGTH),
              fill_up_to(str(answer.a_ttl),
                         Constants.TTL_LENGTH),
              fill_up_to(Tools.class_to_string(answer.a_class),
                         Constants.CLASS_LENGTH),
              fill_up_to(Tools.type_to_string(answer.a_type),
                         Constants.TYPE_LENGTH),
              fill_up_to(str(answer.response_data),
                         Constants.DATA_LENGTH))

    if packet.header.num_authority > 0:
        print("\n;;AUTHORITY SECTION:")

    for authority in packet.authorities:
        print(fill_up_to(authority.name,
                         Constants.DOMAIN_LENGTH),
              fill_up_to(str(authority.ttl),
                         Constants.TTL_LENGTH),
              fill_up_to(Tools.class_to_string(authority.a_class),
                         Constants.CLASS_LENGTH),
              fill_up_to(Tools.type_to_string(authority.a_type),
                         Constants.TYPE_LENGTH),
              fill_up_to(authority.data,
                         Constants.DATA_LENGTH))

    if packet.header.num_additional > 0:
        print("\n;;ADDITIONAL SECTION:")

    for additional in packet.additionals:
        print(fill_up_to(additional.name,
                         Constants.DOMAIN_LENGTH),
              fill_up_to(str(additional.ttl),
                         Constants.TTL_LENGTH),
              fill_up_to(Tools.class_to_string(additional.a_class),
                         Constants.CLASS_LENGTH),
              fill_up_to(Tools.type_to_string(additional.a_type),
                         Constants.TYPE_LENGTH),
              fill_up_to(additional.data,
                         Constants.DATA_LENGTH))

    # space between two presentations
    print("\r\n\r\n")


''' this method takes string and adds spaces to the end until
    its size becomes equal to up_length '''


def fill_up_to(msg, up_length):
    while len(msg) < up_length:
        msg += " "

    return msg
