import RipEntry
"""
    This class takes rip message parameters and encapsualtes them
"""


class Message:
    def __init__(self, command, version, unused, rip_entries):
        self.command = command
        self.version = version
        self.unused = unused
        self.entries = rip_entries

    def get_entries(self):
        return self.entries

    def get_command(self):
        return self.command

    def get_version(self):
        return self.version

    def get_unused(self):
        return self.unused

    def to_string(self):
        st = "command : " + str(self.command) + \
             "\nversion :" + str(self.version) + \
             "\nunused : " + str(self.unused)

        for entry in self.entries:
            st += "\nfamily : " + str(entry.get_address_family()) + \
                  "\nroute tag : " + str(entry.get_route_tag()) + \
                  "\nip address : " + entry.get_ip_address() + \
                  "\nsubnet mask : " + entry.get_subnet_mask() + \
                  "\nnext hop : " + entry.get_next_hop() + \
                  "\nmetrict : " + str(entry.get_metric())

        return st


