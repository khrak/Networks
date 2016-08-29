import Header
import Question
import Answer
import Authority
import Additional
import Tools
import Constants


'''
    This class takes whole dns packet and parses it. It creates
    header, question, answer, authority and additional objects
    and keeps them.
'''


class Packet:
    def __init__(self, dns_packet_data):
        # pass header chunk of data and get header object
        self.header = Header.Header(dns_packet_data[0:12])

        # get questions from dns packet data
        self.questions = list()
        # offset from headers first byte is 12
        offset = 12

        for i in range(self.header.num_questions):
            question, offset = get_question(dns_packet_data, offset)
            self.questions.append(question)

        # get answers from dns packet data
        self.answers = list()

        for i in range(self.header.num_answers):
            answer, offset = get_answer(dns_packet_data, offset)
            self.answers.append(answer)

        # get authorities from dns packet data
        self.authorities = list()

        for i in range(self.header.num_authority):
            a_list, offset = get_authority_or_additional(dns_packet_data, offset)
            authority = Authority.Authority(a_list[0], a_list[1], a_list[2],
                                            a_list[3], a_list[4], a_list[5])
            self.authorities.append(authority)

        # get additionals from dns packet data
        self.additionals = list()

        for i in range(self.header.num_additional):
            a_list, offset = get_authority_or_additional(dns_packet_data, offset)
            additional = Additional.Additional(a_list[0], a_list[1], a_list[2],
                                               a_list[3], a_list[4], a_list[5])
            self.additionals.append(additional)
        return

    ''' This method takes answer object and adds it to packet '''

    def add_answer(self, answer):
        self.answers.append(answer)

''' This method returns a list of authorities or additional extracted from dns packet '''


def get_authority_or_additional(dns_packet_data, offset):
    name, offset = Tools.get_compressed_text(dns_packet_data, offset)
    a_type = int.from_bytes(dns_packet_data[offset: offset + 2],
                            byteorder=Constants.INTERNET_ENDIANNESS)
    # skip type's bytes
    offset += 2
    a_class = int.from_bytes(dns_packet_data[offset: offset + 2],
                             byteorder=Constants.INTERNET_ENDIANNESS)
    # skip class's bytes
    offset += 2
    ttl = int.from_bytes(dns_packet_data[offset: offset + 4],
                         byteorder=Constants.INTERNET_ENDIANNESS)

    # skip ttl bytes
    offset += 4
    rd_length = int.from_bytes(dns_packet_data[offset: offset + 2],
                               byteorder=Constants.INTERNET_ENDIANNESS)

    # skip rd_length bytes
    offset += 2
    r_data, offset = Tools.get_response_data(dns_packet_data, a_type, rd_length, offset)

    # list these parameters
    authority = (name, a_type, a_class, ttl, rd_length, r_data)

    return authority, offset


''' This method returns a list of questions extracted from dns packet '''


def get_question(dns_packet_data, offset):
    q_name, offset = Tools.get_compressed_text(dns_packet_data, offset)
    q_type = int.from_bytes(dns_packet_data[offset: offset + 2],
                            byteorder=Constants.INTERNET_ENDIANNESS)
    q_class = int.from_bytes(dns_packet_data[offset + 2: offset + 4],
                             byteorder=Constants.INTERNET_ENDIANNESS)

    # point offset to the byte right after the Question Class parameter,
    # for this reason we need to skip 4 bytes
    offset += 4
    # construct Question object
    question = Question.Question(q_name, q_type, q_class)

    return question, offset


''' This method returns a list of answers extracted from dns packet '''


def get_answer(dns_packet_data, offset):
    a_name, offset = Tools.get_compressed_text(dns_packet_data, offset)

    a_type = int.from_bytes(dns_packet_data[offset: offset + 2],
                            byteorder=Constants.INTERNET_ENDIANNESS)
    a_class = int.from_bytes(dns_packet_data[offset + 2: offset + 4],
                             byteorder=Constants.INTERNET_ENDIANNESS)
    a_ttl = int.from_bytes(dns_packet_data[offset + 4: offset + 8],
                           byteorder=Constants.INTERNET_ENDIANNESS)
    rd_length = int.from_bytes(dns_packet_data[offset + 8: offset + 10],
                               byteorder=Constants.INTERNET_ENDIANNESS)

    offset += 10
    r_data, offset = Tools.get_response_data(dns_packet_data, a_type, rd_length, offset)

    answer = Answer.Answer(a_name, a_type, a_class, a_ttl, rd_length, r_data)
    return answer, offset
