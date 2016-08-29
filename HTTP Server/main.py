import socket
import sys
import os
from _thread import *
import threading
import time
import mimetypes
import urllib.request
from os import listdir
import hashlib

# import local files
import config
import log
import counter

# Request fields
GET = "GET"
HEAD = "HEAD"
HOST = "Host:"
CONNECTION = "Connection:"
USER_AGENT = "User-Agent:"
RANGE = "Range:"
IF_NONE_MATCH = "If-None-Match:"
# status code constants
OK = "200"
NOT_FOUND = "404"
RANGE_CODE = "206"
CACHE_CODE = "304"

# constant number values
TIME_OUT = 5
MAX_NUM_USERS = 1024

# constant directory/file names
SERVER_ROOT = "root"
DEFAULT_FILE = "index.html"

''' This method takes response header parameter values,
constructs response header and returns it
'''


def get_response_header(status, content_length, content_type, range_response="", file_checksum=""):
    response = ""

    # check for status code
    if status == OK:
        response = 'HTTP/1.1 200 OK\r\n'
    else:
        if status == NOT_FOUND:
            response = 'HTTP/1.1 404 Not Found\r\n'
        else:
            if status == CACHE_CODE:
                response = "HTTP/1.1 304 Not Modified\r\n"
            else:
                response = "HTTP/1.1 206 Partial Content\r\n"

    response += "Content-Type: " + content_type + "\r\n"
    response += "Content-Length: " + str(content_length) + "\r\n"
    response += "Cache-Control: max-age=120\r\n"
    response += 'ETag: "' + file_checksum + '"\r\n'

    if status == RANGE_CODE:
        response += range_response

    response += "\r\n"

    return response


''' This method takes request data, splits it by spaces
and creates dictionary for each key value field from request
'''


def get_request_map(request_data):

    # initialize resulting dictionary
    request_dic = {}

    lines = request_data.split("\r\n")

    for line in lines:

        if line.startswith(GET):
            request_dic[GET] = line.split()[1]
        if line.startswith(HEAD):
            request_dic[HEAD] = line.split()[1]
        if line.startswith(HOST):
            request_dic[HOST] = line.split()[1]
        if line.startswith(CONNECTION):
            request_dic[CONNECTION] = line.split()[1]
        if line.startswith(USER_AGENT):
            request_dic[USER_AGENT] = line.split(USER_AGENT)[1]
        if line.startswith(RANGE):
            request_dic[RANGE] = line.split("=")[1]
        if line.startswith(IF_NONE_MATCH):
            # remove " " endings from string and keep that way
            request_dic[IF_NONE_MATCH] = line.split()[1].replace('"', '')

    return request_dic


''' This method takes connection socket and full path,
and sends file via this socket
'''


def handle_file_request(sock, full_path, log_writer, request_dic, send_body):

    # get file content-length
    file_content_length = os.path.getsize(full_path)

    # get file hash checksum
    file_checksum = hashlib.md5(open(full_path, 'rb').read()).hexdigest()

    # keep default ranges
    range_left = 0
    range_right = file_content_length - 1

    # keep status code as "200"
    status_code = OK

    file_not_changed = False

    if RANGE in request_dic:
        status_code = RANGE_CODE
        range_byte = request_dic[RANGE]
        range_left = int(range_byte.split("-")[0])
        if range_byte.split("-")[1] != "":
            range_right = int(range_byte.split("-")[1])
    else:
        # check if checksum was contained in request
        if IF_NONE_MATCH in request_dic:
            print(request_dic[IF_NONE_MATCH] + " none match \r\n")
            print(file_checksum + " file checksum \r\n")
            # check if file was changed
            if request_dic[IF_NONE_MATCH] == file_checksum:
                file_not_changed = True

    file_response_length = range_right - range_left + 1

    # open file in byte mode and read all of it
    # or defined by range
    file = open(full_path, "rb")
    file.seek(range_left)
    byte_file_content = file.read(file_response_length)

    url = urllib.request.pathname2url(full_path)
    # get file content-type
    content_type = mimetypes.guess_type(url)[0]

    range_response = ""
    if status_code == RANGE_CODE:
        range_response = "Accept-Ranges: bytes\r\n"
        range_response = range_response + "Content-Range: bytes " + str(range_left) + "-" + str(range_right)
        range_response = range_response + "/" + str(file_response_length) + "\r\n"

    if file_not_changed:
        status_code = "304"
        file_response_length = 0
        print("File not changed")

    # get byte response header
    response_header = get_response_header(status_code, file_response_length, content_type, range_response, file_checksum)

    byte_response_header = response_header.encode()

    # send file header and content
    sock.sendall(byte_response_header)

    print("Response: " + response_header)

    num_sent_bytes = len(byte_response_header)

    # check if file should be sent
    # file is sent when method is not HEAD
    # and file checksum is different
    if send_body and not file_not_changed:
        sock.sendall(byte_file_content)
        num_sent_bytes += file_response_length

    # check for sending body

    # set status code and content-length parameters and log
    log_writer.set_status_code(status_code)
    log_writer.set_content_length(str(num_sent_bytes))
    log_writer.write_log()


''' This method takes connection socket and full path,
sends index.html file via this socket, or scans directory
and sends generated html page
'''


def handle_dir_request(sock, document_root, relative_path, log_writer, send_body):

    # get full path
    full_path = SERVER_ROOT + "/" + document_root + relative_path

    # keep if index.html is in current directory
    default_exists = False

    # construct html scanner for this directory

    scanned_html_file = "<!doctype html>\r\n <ul>"

    for f in listdir(full_path):
        if f == DEFAULT_FILE:
            default_exists = True

        relative_path_to_file = ""
        if relative_path == "/":
            relative_path_to_file = relative_path + f
        else:
            relative_path_to_file = relative_path + "/" + f

        # add new linkable entry to unordered list in html format
        scanned_html_file += "<li> <a href='" + relative_path_to_file + "'>" + f + "</a> </li>\r\n"

    scanned_html_file += "</li> \r\n </html> \r\n"

    byte_response_content = None
    byte_response_header = None

    # check if index.html exists
    if default_exists:
        # get full path to file
        full_path_to_file = full_path + "/" + DEFAULT_FILE
        # open index.html file in byte mode
        def_file = open(full_path_to_file, "rb")
        byte_response_content = def_file.read()

        response_header = get_response_header(OK, os.path.getsize(full_path_to_file), "text/html")
        byte_response_header = response_header.encode()
    else:
        byte_response_content = scanned_html_file.encode()
        response_header = get_response_header(OK, len(byte_response_content), "text/html")
        byte_response_header = response_header.encode()

    sock.sendall(byte_response_header)

    # send header response
    num_sent_bytes = len(byte_response_header)

    # check for sending body
    if send_body:
        sock.sendall(byte_response_content)
        num_sent_bytes += len(byte_response_content)

    # set status code and content-length parameters and log
    log_writer.set_status_code("200")
    log_writer.set_content_length(str(num_sent_bytes))
    log_writer.write_log()


''' This method simply sends file not found message
via this socket
'''


def handle_file_not_found(sock, log_writer, send_body):

    response_body = '<!doctype html> <h1> File Not Found </h1> </html>'

    byte_response_body = response_body.encode()
    # status code is "404", content-type is 'text/html'
    response_header = get_response_header(NOT_FOUND, len(byte_response_body), 'text/html')

    byte_response_header = response_header.encode()
    sock.sendall(byte_response_header)

    num_sent_bytes = len(byte_response_header)

    # check for sending body
    if send_body:
        sock.sendall(byte_response_body)
        num_sent_bytes += len(byte_response_body)

    log_writer.set_status_code("404")
    log_writer.set_content_length(str(num_sent_bytes))

    # write log in logging file
    log_writer.write_log()


''' This method takes connection socket and request key-value pairs and
handles request.
'''


def handle_request(sock, document_root, request_dic, log_writer):

    # take requested relative path
    path = request_dic[GET]

    # get full path
    full_path = SERVER_ROOT + "/" + document_root + path

    # set file name
    log_writer.set_file_name(path)

    # mark whether we should send content body or not
    # depending on whether request method was GET or HEAD
    send_body = GET in request_dic

    # check if file was requested
    if os.path.isfile(full_path):
        handle_file_request(sock, full_path, log_writer, request_dic, send_body)
    else:
        if os.path.isdir(full_path):
            handle_dir_request(sock, document_root, path, log_writer, send_body)
        else:
            handle_file_not_found(sock, log_writer, send_body)

''' this method takes socket and sends 'requested domain
not found found' message as response '''


def requested_domain_not_found(con_socket):

    # take response content
    response = "<!doctype html> <h1> Requested domain not found </h1> </html>"
    byte_response = response.encode()

    # get response header byte format
    response_header = get_response_header("404", len(byte_response), "text/html")
    byte_response_header = response_header.encode()

    # send response
    con_socket.sendall(byte_response_header + byte_response)
    return

''' this method takes connection socket and handles
client with multiple requests. Closes connection when client
stops sending requests for 5 seconds '''


def clientthread(con_socket, logger, log_writer, configger, ip, port):
    # set socket as blocking
    # con_socket.setblocking(1)
    # set socket time out with TIME_OUT seconds
    # con_socket.settimeout(TIME_OUT)

    # infinite loop for infinite many request handling
    while True:
        # Receiving from client
        byte_data = con_socket.recv(1024)

        # convert to string data
        string_data = byte_data.decode()

        print("Request: " + string_data)

        # get (key,value) pars from request
        request_dic = get_request_map(string_data)
        # take host parameter from request
        host_header = request_dic[HOST]

        # check if vhost exists
        if not configger.vhost_exists(host_header):
            requested_domain_not_found(con_socket)
            break


        # get file and its lock from logger
        file_lock_tuple = logger.get_file(host_header)

        # take vhost body from config
        vhost_body = configger.get_domain_vhost(ip, port, host_header)

        # take document root
        document_root = vhost_body["documentroot"]

        # set time
        log_writer.set_time(time.strftime("%c"))
        # set host
        log_writer.set_host(host_header)
        # set user agent
        log_writer.set_user_agent(request_dic[USER_AGENT])
        # set file lock tuple
        log_writer.set_log_file_with_lock(file_lock_tuple[0], file_lock_tuple[1])

        handle_request(con_socket, document_root, request_dic, log_writer)

        if "\r\n\r\n" in string_data or not byte_data:
            break

    # came out of loop

    print("end connection")

    con_socket.close()


''' This method takes (ip,port) tuple, creates socket
with this parameters and starts listening to this specific ip and port
'''


def start_listening(ip, port, logger, configger):
    print("listening started")
    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    # Bind socket to local host and port
    try:
        s.bind((ip, port))
    except socket.error as msg:
        print("Bind failed. Error Code : " + str(msg))
        sys.exit()

    print('Socket bind complete')

    # Start listening on socket
    s.listen(MAX_NUM_USERS)
    print('Socket now listening')

    # now keep talking with the client
    while 1:
        # wait to accept a connection - blocking call
        conn, addr = s.accept()
        log_writer = counter.Counter()

        # set source ip address
        log_writer.set_source_ip(addr[0])

        # handle new connection
        start_new_thread(clientthread, (conn, logger, log_writer, configger, ip, port))
    s.close()


''' Start Server '''

# create config object
config_object = config.Config(sys.argv[1])

# create log_object
log_object = log.Log(config_object)

# get (ip,port) list from config object
ip_port_list = config_object.get_ip_ports()

# keep child threads in this list
children = list()


# start listening to all of them
for ip_port in ip_port_list:
    # keep new child
    current_thread = threading.Thread(target=start_listening,
                                      args=(ip_port[0], int(ip_port[1]), log_object, config_object,))
    children.append(current_thread)
    current_thread.start()

# wait for all children
for child in children:
    child.join()
