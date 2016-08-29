import threading

# import local files
import config

''' this class takes config object, iterates over all vhosts
and for each of them opens file in log and keeps them open.
'''
class Log:

    def __init__(self, config_object):
        self.files = {}

        # take all vhost names
        vhosts = config_object.get_vhost_names()
        # take log path
        log_path = config_object.get_log()

        # for each vhost open file
        # and for each file keep lock
        for vhost in vhosts:
            logfile = open(log_path + vhost + ".log", "w")
            self.files[vhost] = (logfile, threading.Lock())

    ''' This method takes vhost name and returns opened
     file from log assigned to this vhost
    '''
    def get_file(self, vhost_name):
        if vhost_name in self.files:
            return self.files[vhost_name]
        else:
            return None