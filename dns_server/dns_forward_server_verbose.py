#!/usr/bin/env python

from functools import partial, wraps
from dns_forward_server import *
import dnslib


# https://wiki.python.org/moin/PythonDecoratorLibrary
def singleton(cls):

    cls.__new_original__ = cls.__new__

    @wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it =  cls.__dict__.get('__it__')
        if it is not None:
            return it
        cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
        it.__init_original__(*args, **kw)
        return it
    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__
    return cls


@singleton
class Logger():

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self):
        pass

    @staticmethod
    def print_stdout(label, message):
        print "%s: %s" % (label, message)
        sys.stdout.flush()

    def error(self, message):
        self.print_stdout("ERROR", message)

    def debug(self, message):
        # self.print_stdout("DEBUG", message)
        pass

    def info(self, message):
        self.print_stdout("INFO", message)

    def warning(self, message):
        self.print_stdout("WARNING", message)

    # https://tools.ietf.org/html/rfc1035
    # https://pypi.python.org/pypi/dnslib
    # https://bitbucket.org/paulc/dnslib

    def dpiengine(self, protocol, payload):
        result = []
        try:
            result = self._dpiengine(protocol, payload)
        except dnslib.DNSError as err:
            self.warning("dnslib.DNSError: " + str(err))
        except BaseException:
            pass
        return result

    def _dpiengine(self, protocol, payload):
        if protocol == 'dns':
            reader = dnslib.DNSRecord.parse(payload)
            if reader.header.qr == 1: # response
                interested = []
                for each_rr in reader.rr:
                    if each_rr.rtype == 1:
                        dns_type = 'A'
                    elif each_rr.rtype == 28:
                        dns_type = 'AAAA'
                    else:
                        continue
                    interested.append("%s{%s}" % (dns_type,
                                                  str(each_rr.rdata)))
                return interested
            else: # query
                if reader.q.qtype == 1:
                    dns_type = 'A'
                elif reader.q.qtype == 28:
                    dns_type = 'AAAA'
                else:
                    return []
                return ["%s{%s}" % (dns_type, reader.q.get_qname())]
        return []

    def dpiengine_worry_free(self, protocol, payload):
        try:
            return self._dpiengine()
        except Exception:
            return []

    def dpi(self, protocol, payload):
        for i in self.dpiengine(protocol, payload):
            self.print_stdout("DPI", i)


if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        print_usage()
        sys.exit(0)
    logger = Logger() if '--verbose' in sys.argv[1:] else None
    # prepare all for log callback
    my_parse_parameter = partial(parse_parameter, log_cb=logger)
    my_invoke_dns_server = partial(invoke_dns_server, log_cb=logger)
    # action
    my_profiles = my_parse_parameter(sys.argv[1:])
    if len(my_profiles) <= 1:  # 1st: hosting server, 2nd ~ : forward servers
        logger.error("insufficient parameters: " ' '.join(sys.argv[1:]))
        print_usage()
        sys.exit(-1)
    my_invoke_dns_server(my_profiles)

