""" This class takes parameters from answer fields
    and constructs object by them
"""


class Answer:
    def __init__(self, a_name, a_type, a_class, a_ttl, rdlength, response_data):
        self.a_name = a_name
        self.a_type = a_type
        self.a_class = a_class
        self.a_ttl = a_ttl
        self.rdlength = rdlength
        self.response_data = response_data
        return
