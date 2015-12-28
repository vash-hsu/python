#!/usr/bin/env python

from functools import partial, wraps
from dns_forward_server import *


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
        self.print_stdout("DEBUG", message)

    def info(self, message):
        self.print_stdout("INFO", message)

    def warning(self, message):
        self.print_stdout("WARNING", message)

    def dpi(self, protocol, payload):
        pass


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

