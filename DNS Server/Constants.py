""" This class declares constant static variables
    which are used all over the DNS server
"""

INTERNET_ENDIANNESS = "big"
DNS_PORT_NUMBER = 53
DNS_RECURSION_MAX_DEPTH  = 64
NUM_ROOT_SERVERS = 13
DOMAIN_LENGTH = 30
TTL_LENGTH = 10
CLASS_LENGTH = 5
TYPE_LENGTH = 10
DATA_LENGTH = 50

A = 0x0001
AAAA = 0x001c
NS = 0x0002
MX = 0x000f
SOA = 0x0006
TXT = 0x0010
CNAME = 0x0005
ANY = 0x00ff