""" This method takes rip entry parametrs and encapsualtes them
"""


class RipEntry:
    def __init__(self, address_family, route_tag, ip_address, subnet_mask, next_hop, metric):
        self.address_family = address_family
        self.route_tag = route_tag
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.next_hop = next_hop
        self.metric = metric

    def get_address_family(self):
        return self.address_family

    def get_route_tag(self):
        return self.route_tag

    def get_ip_address(self):
        return self.ip_address

    def get_subnet_mask(self):
        return self.subnet_mask

    def get_next_hop(self):
        return self.next_hop

    def get_metric(self):
        return self.metric