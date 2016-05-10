#!/usr/bin/env python

from dns_forward_server import *
import dnslib

CONST_VERSION = '0.1'
ZONE_FILE_DICT = dict()


def is_valid_domain_name(string_in):
    if len(string_in) > 2 and '.' in string_in:
        return True
    return False


def print_usage():
    print '''\
Usage: -p <PORT>  -f IPv4:PORT  [--verbose]  [-h]
    -p PORT      : i.e. 10053 (root is necessary if port < 1024)
    -f IPv4:PORT : i.e. 8.8.8.8:53
    -a FQDN:IPv4 : i.e. google.com:127.0.0.1 (NXDOMAIN return without IPv4)
    -h           : show help
Example:
    -p 10053 -f 8.8.8.8:53
    -p 10053 -f 8.8.8.8:53 -f 168.95.1.1:53
    -p 10053 -f 8.8.8.8:53 -f 168.95.1.1:53 -a google.com:127.0.0.1
    -p 10053 -f 8.8.8.8:53 -f 168.95.1.1:53 -a unknown.com:
    '''


def parse_parameter(argv, log_cb=None):
    try:
        opts, args = getopt.getopt(argv, 'hp:f:a:', ['verbose'])
    except getopt.GetoptError as err:
        if log_cb:
            log_cb.error('Exception: GetoptError: '+str(err.args))
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
        elif opt in ("-a",): # -a google.com:127.0.0.1
            pairs = arg.split(':')
            if 2 == len(pairs) and is_valid_domain_name(pairs[0]):
                if is_valid_ipv4(pairs[1]):
                    profiles.append(ResourceRecord(fqdn=pairs[0],
                                                   answer=pairs[1],
                                                   type=4))
                else: # NXDOMAIN
                    profiles.append(ResourceRecord(fqdn=pairs[0],
                                                   answer=None,
                                                   type=4))
        elif opt in ('-h', '--help'):
            print_usage()
            sys.exit(0)
    if s_port:
        profiles.insert(0, Profile(sport=s_port, dip=None, dport=None))
    return profiles


class ResourceRecord:
    def __init__(self, fqdn, answer, type=4):
        self.fqdn = fqdn        # 'google.com'
        self.answer = answer    # '127.0.0.1'
        self.type = type        # 4 or 6 in integer

    def is_valid(self):
        if get_type_of_ip(self.answer) == self.type and \
                is_valid_domain_name(self.fqdn):
            return True
        else:
            return False

    @property
    def valid(self):
        return self.is_valid()

    @property
    def query(self):
        return self.fqdn

    @property
    def response(self):
        return self.answer


class MyThreadedUDPRequestHandler(BaseRequestHandler):

    def handle(self):
        cur_thread = threading.current_thread()
        query_payload = self.request[0]
        socket_client = self.request[1]
        #
        if DEBUG:
            debugmsg = "{}: {}".format(cur_thread.name, self.client_address[0])
            DEBUG.debug(debugmsg)
            DEBUG.info("%s --> " % self.client_address[0])
            DEBUG.dpi('dns', query_payload)
        # if in current zone file
        reader = dnslib.DNSRecord.parse(query_payload)
        if reader.q.qtype == 1: # A
            qname = str(reader.q.get_qname())
            sn_id = reader.header.id
            if qname in ZONE_FILE_DICT.keys():
                qanswer = ZONE_FILE_DICT[qname]
                if qanswer:
                    mock = dnslib.DNSRecord(dnslib.DNSHeader(qr=1, aa=1, ra=1,
                                                             id=sn_id),
                                            q=dnslib.DNSQuestion(qname),
                                            a=dnslib.RR(qname,
                                                        rdata=dnslib.A(qanswer)))
                else: # NXDOMAIN
                    mock = dnslib.DNSRecord(dnslib.DNSHeader(qr=1, aa=0, ra=0,
                                                             id=sn_id,
                                                             rcode=getattr(dnslib.RCODE, 'NXDOMAIN')),
                                            q=dnslib.DNSQuestion(qname))
                socket_client.sendto(mock.pack(), self.client_address)
                print mock
                return
        # if not in current zone file
        children = list()
        answers = Queue.Queue()
        try:
            for i in BACKEND_DNS_SERVERS:
                child = ThreadDig(query_payload, i[0], i[1], answers)
                children.append(child)
            for i in children:
                i.start()
            source, response_payload = answers.get(True, CONST_TIMEOUT)
            socket_client.sendto(response_payload, self.client_address)
            if DEBUG:
                DEBUG.info('<-- %s' % source)
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
        except BaseException as err:
            if DEBUG:
                DEBUG.warning('Oops! %s %s' % (str(err), whereami()))


def invoke_dns_server(configs, log_cb=None):
    global DEBUG
    if log_cb:
        DEBUG = log_cb
    global BACKEND_DNS_SERVERS
    global ZONE_FILE_DICT
    local_server_port = 53  # default
    for i in configs:
        # single local profile and multiple forward servers
        if isinstance(i, Profile):
            if i.source[1]:
                local_server_port = i.source[1]
                continue
            if i.destination:
                BACKEND_DNS_SERVERS.append(i.destination)
        # pre-defined fqdn -> ip
        elif isinstance(i, ResourceRecord):
            ZONE_FILE_DICT[i.query] = i.response
    server = MyThreadedUDPServer(('', local_server_port),
                                 MyThreadedUDPRequestHandler)
    ip, port = server.server_address
    if log_cb:
        log_cb.info("service starting at %s %s" % (ip, port))
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    try:
        server_thread.start()
        while raw_input().lower() not in ('exit', 'quit'):
            continue
        if log_cb:
            log_cb.info("User Cancel")
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
