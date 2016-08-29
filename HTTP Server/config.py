import json

''' This class takes path to config file and creates ConfConfig
object, has useful methods for retrieving some information about
vhosts and ip/port tuples
'''


class Config:
    """ Initialize config object and json data
        in dictionary
    """

    def __init__(self, config_file_path):

        with open(config_file_path) as data_file:
            self.data = json.load(data_file)

        # keep log path
        self.log = self.data["log"]

        # keep all vhost objects identified by
        # (ip,port) tuple key
        self.virtual_hosts = {}

        # keep all ip,port tuples
        self.ip_ports = list()

        for vhost in self.data["server"]:
            ip = str(vhost["ip"])
            port = str(vhost["port"])
            self.ip_ports.append((ip, port))
            if ip + ":" + port not in self.virtual_hosts:
                self.virtual_hosts[ip + ":" + port] = list()
            self.virtual_hosts[ip + ":" + port].append(vhost)

        # make unique ip,port tuples
        self.ip_ports = list(set(self.ip_ports))

    ''' Returns path to log directory '''

    def get_log(self):
        return self.log

    ''' returns ip,port,vhost,logfile parameters for specific
        ip/port tuples
    '''

    def get_vhost(self, ip, port):
        return (self.virtual_hosts[str(ip) + ":" + str(port)])

    ''' return all vhost names this server has '''

    def get_vhost_names(self):
        result = list()
        for key in self.virtual_hosts:
            vhost_list = self.virtual_hosts[key]
            for vhost in vhost_list:
                if "vhost" in vhost:
                    result.append(vhost["vhost"])
        result = list(set(result))

        return result

    ''' this method return all distinct ip,port tuples'''

    def get_ip_ports(self):
        return self.ip_ports

    ''' this method returns vhost body by indicating ip, port and domain name '''

    def get_domain_vhost(self, ip, port, host):

        # get list of vhost bodies by ip,port
        vhosts = self.get_vhost(ip, port)

        # choose the one with host domain name from this list
        for vhost in vhosts:
            if vhost["vhost"] == host:
                return vhost

        # if nothing was found
        return None

    ''' this method takes vhost name and checks if server owns this host '''
    def vhost_exists(self, vhost):
        lst = self.get_vhost_names()

        return vhost in lst