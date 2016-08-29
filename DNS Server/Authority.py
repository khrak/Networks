""" This class takes authority field parameters
    and constructs object by them
"""


class Authority:
    def __init__(self, name, a_type, a_class, ttl, rd_length, data):
        self.name = name
        self.a_type = a_type
        self.a_class = a_class
        self.ttl = ttl
        self.rd_length = rd_length
        self.data = data
        return
