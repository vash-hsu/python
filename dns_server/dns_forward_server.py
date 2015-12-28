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
import Queue

CONST_VERSION = '0.2'
DEBUG = None
CONST_TIMEOUT = 2  # 2 seconds

VERIFIED_Not_IP = 0
VERIFIED_IPv4_Private = 1
VERIFIED_IPv4_Global = 2
VERIFIED_IPv6_Private = 3
VERIFIED_IPv6_Global = 4


BACKEND_DNS_SERVERS = list()


def print_usage():
    print '''\
Usage: -p <PORT>  -f IPv4:PORT  [--verbose]  [-h]
    -p PORT      : i.e. 10053 (root is necessary if port < 1024)
    -f IPv4:PORT : i.e. 8.8.8.8:53
    -h           : show help
Example:
    -p 10053 -f 8.8.8.8:53
    -p 10053 -f 8.8.8.8:53 -f 168.95.1.1:53
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


def parse_parameter(argv, log_cb=None):
    try:
        opts, args = getopt.getopt(argv, 'hp:f:', ['verbose'])
    except getopt.GetoptError as err:
        if log_cb:
            log_cb.error('Exception: GetoptError: '+str(err.args))
        # print "Exception: GetoptError: ", str(err.args)
        sys.exit(-2)
    s_port = None
    profiles = list()
    for opt, arg in opts:
        if opt in ("-p",):
            if arg.isdigit() and is_valid_port(int(arg)):
                s_port = int(arg)
        elif opt in ("-f",):
            pairs = arg.split(':')
            if 2 == len(pairs) and is_valid_ipv4(pairs[0]) and \
                pairs[1].isdigit() and is_valid_port(int(pairs[1])):
                profiles.append(Profile(sport=None,
                                        dip=pairs[0],
                                        dport=int(pairs[1])))
        elif opt in ('-h', '--help'):
            print_usage()
            sys.exit(0)
    if s_port:
        profiles.insert(0, Profile(sport=s_port, dip=None, dport=None))
    return profiles


class ThreadDig(threading.Thread):
    def __init__(self, payload, ip, port, answer_pool):
        threading.Thread.__init__(self)
        self.payload = payload
        self.ip = ip
        self.port = port
        self.answer = answer_pool
        self.socket_mim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_mim.settimeout(CONST_TIMEOUT)

    def run(self):
        cur_thread = threading.current_thread()
        if DEBUG:
            debugmsg = "{}: IP {} Port {}".format(cur_thread.name,
                                                  self.ip, self.port)
            DEBUG.debug(debugmsg)
        try:
            self.socket_mim.sendto(self.payload, (self.ip, self.port))
            response_payload = self.socket_mim.recv(1024)
            self.answer.put(response_payload)
            if DEBUG:
                DEBUG.dpi('dns', response_payload)
        except socket.timeout:
            if DEBUG:
                DEBUG.warning("EXCEPTION: {} socket.timeout in {} seconds"
                              .format(cur_thread.name, CONST_TIMEOUT))


class MyThreadedUDPRequestHandler(BaseRequestHandler):

    def handle(self):
        cur_thread = threading.current_thread()
        query_payload = self.request[0].strip()
        socket_client = self.request[1]
        #
        if DEBUG:
            debugmsg = "{}: {}".format(cur_thread.name, self.client_address[0])
            DEBUG.debug(debugmsg)
        # Man in the Middle
        socket_mim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_mim.settimeout(CONST_TIMEOUT)
        children = list()
        answers = Queue.Queue()
        try:
            for i in BACKEND_DNS_SERVERS:
                child = ThreadDig(query_payload, i[0], i[1], answers)
                children.append(child)
            for i in children:
                i.start()
            response_payload = answers.get(True, CONST_TIMEOUT)
            socket_client.sendto(response_payload, self.client_address)
            if DEBUG:
                DEBUG.dpi('dns', query_payload)
                DEBUG.dpi('dns', response_payload)
            for i in children:
                i.join()
        except socket.timeout:
            if DEBUG:
                DEBUG.warning('EXCEPTION: socket.timeout in %d' % CONST_TIMEOUT)
        except socket.error as err:
            if DEBUG:
                DEBUG.warning('EXCEPTION: Watchout %s' % str(err))
        except Queue.Empty:
            if DEBUG:
                DEBUG.warning('EXCEPTION: Watchout, no answer returned')
        finally:
            socket_mim.close()


class MyThreadedUDPServer(ThreadingMixIn, UDPServer):
    pass


def invoke_dns_server(configs, log_cb=None):
    global DEBUG
    if log_cb:
        DEBUG = log_cb
    global BACKEND_DNS_SERVERS
    local_server_port = 53  # default
    # single local profile and multiple forward servers
    for i in configs:
        if i.source[1]:
            local_server_port = i.source[1]
            continue
        if i.destination:
            BACKEND_DNS_SERVERS.append(i.destination)
    server = MyThreadedUDPServer(('', local_server_port),
                                 MyThreadedUDPRequestHandler)
    ip, port = server.server_address
    if log_cb:
        log_cb.info("service starting at %s %s" % (ip, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if log_cb:
            log_cb.info("User Cancel by CTRL + C")
        # what should I do here to clean up?
    finally:
        server.shutdown()
    server.server_close()


if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        print_usage()
        sys.exit(0)
    profiles = parse_parameter(sys.argv[1:])
    if len(profiles) <= 1:  # 1st: hosting server, 2nd ~ : forward servers
        print "ERROR: insufficient parameters:", sys.argv[1:]
        print_usage()
        sys.exit(-1)
    invoke_dns_server(profiles)
