import threading

''' This class keeps parameters which should be written
in log file, it takes log file also and when it has all parameters
set, it writes in log file
'''

class Counter:

    # set default values
    def __init__(self):
        self.log_file = None
        self.time = ""
        self.src_ip = ""
        self.host_name = ""
        self.file_name = ""
        self.status_code = ""
        self.content_length = ""
        self.user_agent = ""

    # keeps time parameter
    def set_time(self,time):
        self.time = time

    # keep source ip
    def set_source_ip(self,source_ip):
        self.src_ip = source_ip

    # keep host name
    def set_host(self,host_name):
        self.host_name = host_name

    # keep file name
    def set_file_name(self,file_name):
        self.file_name = file_name

    # keep status code
    def set_status_code(self,status_code):
        self.status_code = status_code

    # keep content length
    def set_content_length(self,content_length):
        self.content_length = content_length

    # keep user agent
    def set_user_agent(self,user_agent):
        self.user_agent = user_agent


    # keep log file to write in, and keep lock of this file
    def set_log_file_with_lock(self,log_file,lock):
        self.log_file = log_file
        self.lock = lock


    ''' write in log file. So at first, tries to take lock
        and then writes info in log file and flushes it and at
        last releases the lock'''

    def write_log(self):
        # take lock
        self.lock.acquire()
        # construct log text
        log_text = "[" + self.time + "] " + self.src_ip + " " + self.host_name + " " + self.file_name
        log_text += " " + self.status_code + " " + self.content_length + ' "' + self.user_agent + "\"" + "\n"

        # write and flush text
        self.log_file.write(log_text)
        self.log_file.flush()

        self.lock.release()
