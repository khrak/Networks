class DHCPRequest:

    def __init__(self, op, htype, hlen, hops, xid, secs, flags,
                 ciaddr, yiaddr, siaddr, giaddr, chaddr,
                 magic_cookie, options_dict):

        self.op = op
        self.htype = htype
        self.hlen = hlen
        self.hops = hops

        self.xid = xid
        self.secs = secs
        self.flags = flags

        self.ciaddr = ciaddr
        self.yiaddr = yiaddr
        self.siaddr = siaddr
        self.giaddr = giaddr
        self.chaddr = chaddr

        self.magic_cookie = magic_cookie

        self.options_dict = options_dict

    def get_op(self):
        return self.op

    def get_gtype(self):
        return self.htype

    def get_hlen(self):
        return self.hlen

    def get_hops(self):
        return self.hops

    def get_xid(self):
        return self.xid

    def get_secs(self):
        return self.secs

    def get_flags(self):
        return self.flags

    def get_ciaddr(self):
        return self.ciaddr

    def get_yiaddr(self):
        return self.yiaddr

    def get_siaddr(self):
        return self.siaddr

    def get_giaddr(self):
        return self.giaddr

    def get_chaddr(self):
        return self.chaddr

    def get_magic_cookie(self):
        return self.magic_cookie

    def get_options_dict(self):
        return self.options_dict

    def to_string(self):
        result = "xid : " + str(self.xid) + "\n" \
                 + "ciaddr : " + str(self.ciaddr) + "\n" \
                 + "yiaddr : " + str(self.yiaddr) + "\n" \
                 + "siaddr : " + str(self.siaddr) + "\n" \
                 + "giaddr : " + str(self.giaddr) + "\n" \
                 + "chaddr : " + str(self.chaddr) + "\n" \
                 + "magic_cookie : " + str(self.magic_cookie) + "\n" \
                 + "op : " + str(self.op) + "\n" \
                 + "htype : " + str(self.htype) + "\n" \
                 + "hlen : " + str(self.hlen) + "\n" \
                 + "hops : " + str(self.hops) + "\n" \
                 + "secs : " + str(self.secs) + "\n" \
                 + "flags : " + str(self.flags) + "\n" \
                 + "xid : " + str(self.xid) + "\n"
        return result
