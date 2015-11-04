#!/usr/bin/env python

import sys, getopt
import os

CANONICAL = 1
CLANGUAGE = 2
PYTHON    = 3


def usage_help():
    #print '''Usage: -[C|c|p] FILEPATH
    print '''Usage: -[C|c] FILEPATH
    -C:  Canonical hex+ASCII display
    -c:  C style declaration
'''
    #-p:  python style declaration


def parse_parameter(list_para):
    display_type = CANONICAL
    candidate = list()
    try:
        opts, args = getopt.getopt(list_para, "hCcp", ["help",])
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                usage_help()
                return None
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
    return display_type, candidate


def header_write(offset):
    if offset == 0:
        print '         00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F' +\
             '     0123456789ABCDEF'
    text = ''.join("{:02x}".format(offset))
    header = '0'*(7 - len(text)) + text + '0'
    print header.upper(),


def payload_write(raw):
    hex_data = ' '.join("{:02x}".format(ord(ch)) for ch in raw)
    print hex_data.upper(),
    ascii_data = list()
    for character in raw:
        if character > '~' or character < ' ':
            ascii_data.append('.')
        else:
            ascii_data.append(character)
    print ' '*(16*3 - len(hex_data)) + ' | ' + ''.join(ascii_data)


def payload_write_c(raw, offset):
    if not raw:
        if offset > 0:
            sys.stdout.write('\n};')
        return
    meta = '\\x' + '\',\'\\x'.join("{:02x}".format(ord(ch)).upper() for ch in raw)
    if offset > 0:
        prefix = ','
    else:
        prefix = 'const char raw[] = {'
    sys.stdout.write(prefix + '\n  \'' + meta + '\'')


def dump_file(display_as, raw, offset):
    if display_as == CANONICAL and raw:
        header_write(offset)
        payload_write(raw)
    elif display_as == CLANGUAGE:
        payload_write_c(raw, offset)
    else:
        pass


def read_convert_write(display_as, files):
    for file in files:
        offset = 0
        with open(file, 'rb') as file_handler:
            while True:
                buffer = file_handler.read(16)
                if len(buffer) == 0:
                    break
                dump_file(display_as, buffer, offset)
                offset += 1
            dump_file(display_as, None, offset)


if __name__ == '__main__':
    metadata = None
    if len(sys.argv) == 1:
        usage_help()
    else:
        action, targets = parse_parameter(sys.argv[1:])
        if action and targets and len(targets):
            read_convert_write(action, targets)
        else:
            print "Oops"
