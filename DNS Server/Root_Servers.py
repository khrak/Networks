import Constants

""" This list keeps ip addresses of all root servers
"""


class RootServers:
    root_servers = ['198.41.0.4',
                    '192.228.79.201',
                    '192.33.4.12',
                    '199.7.91.13',
                    '192.203.230.10',
                    '192.5.5.241',
                    '192.112.36.4',
                    '192.112.36.4',
                    '128.63.2.53',
                    '192.36.148.17',
                    '192.58.128.30',
                    '193.0.14.129',
                    '199.7.83.42',
                    '202.12.27.33']

    ''' This is round robin index for root servers. '''
    root_server_index = 0

    ''' This method returns ip address of root server by round robin rule. '''

    def get_root_server(self):
        root_server = self.root_servers[self.root_server_index]
        self.root_server_index += 1
        self.root_server_index %= Constants.NUM_ROOT_SERVERS
        return root_server
