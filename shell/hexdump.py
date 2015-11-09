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


def header_write(offset):
    if offset == 0:
        print ' ' * 9 + '00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F' +\
             ' ' * 5 + '0123456789ABCDEF'
    text = ''.join("{:02x}".format(offset))
    header = '0'*(7 - len(text)) + text + '0 '
    return header.upper()


def payload_write(raw, offset):
    buffer2write = ''
    if raw:
        ascii_data = list()
        for character in raw:
            if character > '~' or character < ' ':
                ascii_data.append('.')
            else:
                ascii_data.append(character)
        hex_data = ' '.join("{:02x}".format(ord(ch)).upper() for ch in raw)
        lineup = "%s %s | %s" % \
                 (hex_data, ' '*(16*3 - len(hex_data)), ''.join(ascii_data))
        buffer2write = header_write(offset) + lineup
    sys.stdout.write(buffer2write)


def payload_write_c(raw, offset):
    buffer2write = ''
    if not raw:
        if offset > 0:
            buffer2write = '\n};'
    else:
        meta = '\\x' + '\',\'\\x'.join("{:02x}".format(ord(ch)).upper() for ch in raw)
        if offset > 0:
            prefix = ','
        else:
            prefix = 'const char raw[] = {'
        buffer2write = prefix + '\n  \'' + meta + '\''
    sys.stdout.write(buffer2write)


def payload_write_python(raw, offset):
    buffer2write = ''
    if not raw:
        if offset > 0:
            buffer2write = '\n'
    else:
        meta = '\'\\x' + \
               '\\x'.join("{:02x}".format(ord(ch)).upper() for ch in raw) + \
               '\''
        if offset > 0:
            buffer2write = ' \\\n      ' + meta
        else:
            buffer2write = 'raw = ' + meta
    sys.stdout.write(buffer2write)


def dump_file(display_as, raw, offset):
    if display_as == CANONICAL and raw:
        payload_write(raw, offset)
    elif display_as == CLANGUAGE:
        payload_write_c(raw, offset)
    elif display_as == PYTHON:
        payload_write_python(raw, offset)
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
    if len(sys.argv[1:]) == 0:
        usage_help()
    else:
        action, targets = parse_parameter(sys.argv[1:])
        if action and targets and len(targets):
            read_convert_write(action, targets)
        else:
            usage_help()
