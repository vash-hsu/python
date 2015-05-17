#!/usr/bin/env python

from collections import defaultdict
import os, sys

CONST_FORMAT_WIDTH = 16

def parse_raw_data_to_list(_text_in, dict_list_out):
  byte_offset = 0
  row_offset  = 0
  for i in _text_in:
    dict_list_out[row_offset].append(i)
    byte_offset += 1
    if byte_offset >= CONST_FORMAT_WIDTH:
      byte_offset = 0
      row_offset += 1

def convert_str_to_hex(_list_in):
  list_out = list()
  for i in _list_in:
    list_out.append(i.encode('hex'))
  return list_out
  
def convert_data_to_printable(_list_in):
  list_out = list()
  for ch in _list_in:
    if ord(ch) <  32 or ord(ch) > 126:
      list_out.append('.')
    else:
      list_out.append(ch)
  return list_out


def show_hex_view(_dictlist_in):
  for i in sorted(_dictlist_in.keys()):
    line_in = _dictlist_in[i]
    line_out = convert_str_to_hex(line_in)
    # hex
    if len(line_in) < CONST_FORMAT_WIDTH:
      tab_offset = CONST_FORMAT_WIDTH - len(line_in)
    else:
      tab_offset = 0
    print ' '.join(line_out), '   '*tab_offset + ';',
    friendly_print = convert_data_to_printable(line_in)
    print ''.join(friendly_print)

if __name__ == '__main__':
  for i in sys.argv[1:]:
    if os.path.isfile(i):
      with open(i, 'rb') as fdr:
        raw_data = fdr.read()
    else:
      continue
    if raw_data != None:
      print '----- %s ----- %d' % (i, len(raw_data))
      dict_list = defaultdict(list)
      parse_raw_data_to_list(raw_data, dict_list)
      show_hex_view(dict_list)