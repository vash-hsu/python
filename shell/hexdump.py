#!/usr/bin/env python

import sys, getopt
import os

CANONICAL = 1
CLANGUAGE = 2
PYTHON    = 3


def usage_help():
    print '''Usage: -[C|c|p] FILEPATH
    -C:  Canonical hex+ASCII display
    -c:  C style declaration
    -p:  Python style declaration'''


def parse_parameter(list_para):
    display_type = None
    candidate = list()
    try:
        opts, args = getopt.getopt(list_para, 'hCcp', ['help', ])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                return display_type, candidate
            elif opt == '-C':
                display_type = CANONICAL
            elif opt == '-c':
                display_type = CLANGUAGE
            elif opt == '-p':
                display_type = PYTHON
        for input_one in args:
            if not os.path.isfile(input_one):
                continue
            candidate.append(input_one)
    except getopt.GetoptError as err:
        print str(err)
    if not display_type and len(candidate) > 0:
        display_type = CANONICAL
    return display_type, candidate


class Dumper:
    def __init__(self, stream, type=CANONICAL):
        self.stream = stream
        self.offset = 0
        if type == CANONICAL:
            self.function = self.dump_canonical
        elif type == CLANGUAGE:
            self.function = self.dump_c
        elif type == PYTHON:
            self.function = self.dump_python
        else:
            self.function = self.dump_canonical

    @property
    def bulk(self):
        while True:
            buffer = self.stream.read(16)
            if len(buffer) == 16:
                yield self.function(buffer, self.offset)
            else:
                yield self.function(buffer, self.offset, end=True)
                break
            self.offset += 1

    def dump_canonical(self, raw, offset, end=False):
        buffer2write = ''
        if len(raw) > 0:
            hex_ = b' '.join(["%0*X" % (2, ord(ch)) for ch in raw])
            text = b''.join([ch if 0x20 <= ord(ch) < 0x7F else b'.' for ch in raw])
            buffer2write = b"%07X0 %-*s %s" % (offset, 16*(2+1), hex_, text)
            if offset == 0:
                header = ' ' * 9 + '00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F' +\
                     ' ' * 2 + '0123456789ABCDEF'
                return header + '\n' + buffer2write
        return buffer2write

    def dump_c(self, raw, offset, end=False):
        prefix = ''
        meta = ''
        postfix = ''
        if offset == 0:
            prefix = 'const char raw[] = {\n'
        if len(raw) > 0:
            meta = '  \'' + \
                   '\\x' + '\',\'\\x'.join("{:02X}".format(ord(ch)) for ch in raw) +\
                   '\''
        if end is False:
            postfix = ','
        else:
            postfix = '\n};'
        return prefix + meta + postfix

    def dump_python(self, raw, offset, end=False):
        prefix = ''
        meta = ''
        postfix = ''
        if len(raw) > 0:
            meta = '\'\\x' + \
                   '\\x'.join("{:02x}".format(ord(ch)).upper() for ch in raw) + \
                   '\''
        if offset == 0:
            prefix = 'raw = '
        else:
            prefix = '    '
        if end is False:
            postfix = '\\'
        return prefix + meta + postfix


def read_convert_write(display_as, files):
    for file in files:
        with open(file, 'rb') as file_handler:
            worker = Dumper(file_handler, display_as)
            for i in worker.bulk:
                print i


if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        usage_help()
    else:
        action, targets = parse_parameter(sys.argv[1:])
        if action and targets and len(targets):
            read_convert_write(action, targets)
        else:
            usage_help()
