"""
Modified arprequest lib
by me )) macs13
"""

import socket
from struct import pack, unpack
import signal

ARP_GRATUITOUS = 1
ARP_STANDARD = 2


def val2int(val):
    '''Retourne une valeur sous forme d'octet en valeur sous forme
       d'entier.'''

    return int.from_bytes(val, byteorder='big')


class TimeoutError(Exception):
    '''Exception levée après un timeout.'''
    pass


def timeout(function, timeout=10):
    '''Exécute la fonction function (référence) et stoppe son exécution
       au bout d'un certain temps déterminé par timeout.

       Retourne None si la fonction à été arretée par le timeout, et
       la valeur retournée par la fonction si son exécution se
       termine.'''

    def raise_timeout(num, frame):
        raise TimeoutError

    # On mappe la fonction à notre signal
    signal.signal(signal.SIGALRM, raise_timeout)
    # Et on définie le temps à attendre avant de lancer le signal
    signal.alarm(timeout)
    try:
        retvalue = function()
    except TimeoutError:  # = Fonction quittée à cause du timeout
        return None
    else:  # = Fonction quittée avant le timeout
        # On annule le signal
        signal.alarm(0)
        return retvalue


# Classes :
###########

class ArpRequest:
    '''Génère une requête ARP et attend la réponse'''

    def __init__(self, ipaddr, if_name, server_ip, arp_type=ARP_GRATUITOUS):
        # Initialisation du socket (socket brut, donc besoin d'ê root)
        self.arp_type = arp_type
        self.if_ipaddr = server_ip

        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                                    socket.SOCK_RAW)
        self.socket.bind((if_name, socket.SOCK_RAW))
        _ls = list()
        for curr in ipaddr.split('.'):
            _ls.append(int(curr))
        self.ipaddr = _ls

    def request(self):
        '''Envois une requête arp et attend la réponse'''

        # Envois de 5 requêtes ARP
        for _ in range(5):
            self._send_arp_request()
        # Puis attente de la réponse
        if timeout(self._wait_response, 5):
            return True
        else:
            return False

    def _send_arp_request(self):
        '''Envois une requête ARP pour la machine'''

        saddr = pack('!4B', self.ipaddr[0], self.ipaddr[1],
                     self.ipaddr[2], self.ipaddr[3])
        if_addr = list()
        for elem in self.if_ipaddr.split('.'):
            if_addr.append(int(elem))
        if_addr = pack('!4B', if_addr[0], if_addr[1],
                       if_addr[2], if_addr[3])
        # Forge de la trame :
        frame = [
            ### Partie ETHERNET ###
            # Adresse mac destination (=broadcast) :
            pack('!6B', *(0xFF,) * 6),
            # Adresse mac source :
            self.socket.getsockname()[4],
            # Type de protocole (=ARP) :
            pack('!H', 0x0806),

            ### Partie ARP ###
            # Type de protocole matériel/logiciel (=Ethernet/IP) :
            pack('!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
            # Type d'opération (=ARP Request) :
            pack('!H', 0x0001),
            # Adresse matériel de l'émetteur :
            self.socket.getsockname()[4],
            # Adresse logicielle de l'émetteur :
            if_addr,
            # Adresse matérielle de la cible (=00*6) :
            pack('!6B', *(0,) * 6),
            # Adresse logicielle de la cible (=adresse fournie au
            # conenucteur) :
            saddr
        ]

        self.socket.send(b''.join(frame))  # Envois de la trame sur le
        # réseau

    def _wait_response(self):
        '''Attend la réponse de la machine'''
        while 0xBeef:
            # Récupération de la trame :
            frame = self.socket.recv(1024)

            # Récupération du protocole sous forme d'entier :
            proto_type = val2int(unpack('!2s', frame[12:14])[0])
            if proto_type != 0x0806:  # On passe le traitement si ce
                continue  # n'est pas de l'arp

            # Récupération du type d'opération sous forme d'entier :
            op = val2int(unpack('!2s', frame[20:22])[0])
            if op != 2:  # On passe le traitement pour tout ce qui n'est
                continue  # pas une réponse ARP

            # Récupération des différentes addresses de la trame :
            arp_headers = frame[18:20]
            arp_headers_values = unpack('!1s1s', arp_headers)
            hw_size, pt_size = [val2int(v) for v in arp_headers_values]
            total_addresses_byte = hw_size * 2 + pt_size * 2
            arp_addrs = frame[22:22 + total_addresses_byte]
            src_hw, src_pt, dst_hw, dst_pt = unpack('!%ss%ss%ss%ss'
                                                    % (hw_size, pt_size, hw_size, pt_size), arp_addrs)

            # Comparaison de l'adresse recherchée avec l'adresse trouvée
            # dans la trame :
            if src_pt == pack('!4B', self.ipaddr[0], self.ipaddr[1],
                              self.ipaddr[2], self.ipaddr[3]):
                return True  # Quand on a trouvé, on arrete de chercher !
                # Et oui, c'est mal de faire un retour dans une boucle,
                # je sais :)
