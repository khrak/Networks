""" This class takes parameters from question fields
    and constructs object by them
"""


class Question:
    def __init__(self, q_name, q_type, q_class):
        self.q_name = q_name
        self.q_type = q_type
        self.q_class = q_class
        return
