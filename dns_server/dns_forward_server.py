#!/usr/bin/env python

# inspired from Crypt0s/FakeDns
# https://github.com/Crypt0s/FakeDns/blob/master/fakedns.py
# https://docs.python.org/2/library/socketserver.html


import getopt
import sys
import ipaddr

from SocketServer import ThreadingMixIn, UDPServer, BaseRequestHandler
import threading
import socket

CONST_VERSION = '0.1'
DEBUG = False
VERIFIED_Not_IP = 0
VERIFIED_IPv4_Private = 1
VERIFIED_IPv4_Global = 2
VERIFIED_IPv6_Private = 3
VERIFIED_IPv6_Global = 4

BACKEND_DNS_SERVER = '8.8.8.8'
BACKEND_DNS_PORT = 53


def print_usage():
    print '''\
Usage: -p <PORT>  -f IPv4:PORT  [--verbose]  [-h]
    -p PORT      : i.e. 10053 (root is necessary if port < 1024)
    -f IPv4:PORT : i.e. 8.8.8.8:53
    -h           : show help
    --verbose    : show debug/diagnostic info on stdout
Example:
    -p 10053 -f 8.8.8.8:53
    '''


# VERIFIED_IPv4_Private, VERIFIED_IPv4_Global
# VERIFIED_IPv6_Private, VERIFIED_IPv6_Global, VERIFIED_Not_IP
def get_type_of_ip(str_uri):
    try:
        target = ipaddr.IPAddress(str_uri)
        if target.version == 4:
            if target.is_private:
                return VERIFIED_IPv4_Private
            else:
                return VERIFIED_IPv4_Global
        else:
            if target.is_private:  # is_reserved
                return VERIFIED_IPv6_Private
            else:
                return VERIFIED_IPv6_Global
    except ValueError:
        pass
    return VERIFIED_Not_IP


def is_valid_ipv4(str_ip):
    if get_type_of_ip(str_ip) in (VERIFIED_IPv4_Private, VERIFIED_IPv4_Global):
        return True
    else:
        return False


def is_valid_port(int_port):
    if isinstance(int_port, int) and 0 < int_port < 65536:
        return True
    else:
        return False


class Profile:
    def __init__(self, sport, dip, dport):
        self.sip = None  # reserved for future use
        self.sport = sport
        self.dip = dip
        self.dport = dport

    def is_valid(self):
        if is_valid_ipv4(get_type_of_ip(self.dip)) and \
                is_valid_port(self.sport) and \
                is_valid_port(self.dport):
            return True
        else:
            return False

    @property
    def valid(self):
        return self.is_valid()

    @property
    def source(self):
        return self.sip, self.sport

    @property
    def destination(self):
        return self.dip, self.dport


def parse_parameter(argv):
    try:
        opts, args = getopt.getopt(argv, 'hp:f:', ['verbose'])
    except getopt.GetoptError as err:
        print "Exception: GetoptError: ", str(err.args)
        sys.exit(-2)
    s_port, d_ip, d_port = None, None, None
    for opt, arg in opts:
        if opt in ("-p",):
            if arg.isdigit():
                s_port = int(arg) if 0 < int(arg) < 65536 else None
        elif opt in ("-f",):
            pairs = arg.split(':')
            if 2 == len(pairs) and is_valid_ipv4(pairs[0]) and \
                pairs[1].isdigit() and is_valid_port(int(pairs[1])):
                d_ip = pairs[0]
                d_port = int(pairs[1])
        elif opt in ('--verbose',):
            global DEBUG
            DEBUG = True
        elif opt in ('-h', '--help'):
            print_usage()
            sys.exit(0)
    return s_port, d_ip, d_port


class UDPHandler(BaseRequestHandler):

    def handle(self):
        (data, socket_client) = self.request
        socket_client.sendto(data, self.client_address)


class MyThreadedUDPRequestHandler(BaseRequestHandler):

    def handle(self):
        cur_thread = threading.current_thread()
        query_payload = self.request[0].strip()
        socket_client = self.request[1]
        #
        if DEBUG:
            debugmsg = "{}: {}".format(cur_thread.name, self.client_address[0])
            print debugmsg
        # Man in the Middle
        socket_mim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_mim.sendto(query_payload, (BACKEND_DNS_SERVER, BACKEND_DNS_PORT))
        response_payload = socket_mim.recv(1024)
        #
        socket_client.sendto(response_payload, self.client_address)


class MyThreadedUDPServer(ThreadingMixIn, UDPServer):
    pass


def invoke_dns_server(config):
    global BACKEND_DNS_SERVER
    BACKEND_DNS_SERVER = config.dip
    global BACKEND_DNS_PORT
    BACKEND_DNS_PORT = config.dport
    server = MyThreadedUDPServer(('', config.sport),
                                 MyThreadedUDPRequestHandler)
    ip, port = server.server_address
    print "INFO: service starting at %s %s" % (ip, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "INFO: User Cancel by CTRL + C"
    server.shutdown()
    server.server_close()


if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        print_usage()
        sys.exit(0)
    sport, dip, dport = parse_parameter(sys.argv[1:])
    if None in (sport, dip, dport):
        print "ERROR: invalid parameters:", sys.argv[1:]
        print_usage()
        sys.exit(-1)
    profile = Profile(sport=sport, dip=dip, dport=dport)
    if profile.is_valid():
        invoke_dns_server(profile)
