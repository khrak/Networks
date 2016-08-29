import Constants

''' This class takes header data from dns packet and
    extracts specific fields from it.
'''


class Header:
    def __init__(self, data):
        # take ID field from data. Depending on
        # endianness of an internet
        self.id = int.from_bytes(data[0:2],
                                 byteorder=Constants.INTERNET_ENDIANNESS)

        # keep flags as two bytes
        self.flags = int.from_bytes(data[2:4],
                                    byteorder=Constants.INTERNET_ENDIANNESS)
        # take one byte after ID field
        # QR-1 bit | OPCODE 4-bit | AA 1-bit | TC 1-bit | RD 1-bit
        header_flags = data[2]
        # take bit flags from request
        self.is_response = header_flags & (1 << 7)
        self.is_query = not self.is_response
        self.opcode = (header_flags >> 3) & 0x0f
        self.authoritative_answer = (header_flags >> 2) & 0x01
        self.message_truncated = (header_flags >> 1) & 0x01
        self.recursion_desired = header_flags & 0x01

        # RA 1-bit | Z 3-bit | RCODE 4-bit
        header_flags = data[3]
        self.recursion_available = header_flags & (1 << 7)
        self.reserved_bits = (header_flags >> 4) & 0x07
        self.response_code = header_flags & 0x0f

        # get count of questions, answers, authorities and additionals
        self.num_questions = int.from_bytes(data[4:6],
                                            byteorder=Constants.INTERNET_ENDIANNESS)

        self.num_answers = int.from_bytes(data[6:8],
                                          byteorder=Constants.INTERNET_ENDIANNESS)

        self.num_authority = int.from_bytes(data[8:10],
                                            byteorder=Constants.INTERNET_ENDIANNESS)

        self.num_additional = int.from_bytes(data[10:12],
                                             byteorder=Constants.INTERNET_ENDIANNESS)
