#!/usr/bin/env python

from collections import defaultdict, Counter

CONST_FORMAT_WIDTH      = 26
CONST_ASCII_BASECODE    = 97 # ord('a')
CONST_CAESAR_CIPHER_ITR = 26 # from 0 ~ 25, because of mod 26

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

def show_hex_view(_dictlist_in):
  for i in sorted(_dictlist_in.keys()):
    line_in = _dictlist_in[i]
    line_out = convert_str_to_hex(line_in)
    print ' '.join(line_in), '     ',
    if len(line_in) < CONST_FORMAT_WIDTH:
      tab_offset = CONST_FORMAT_WIDTH - len(line_in)
    else:
      tab_offset = 0
    print '  '*tab_offset+' '.join(line_out)

def encode_Caesar_Cipher(_list_input, offset, list_output):
  for i in _list_input:
    if i < 'a' or i > 'z':
      list_output.append(i)
    else:
      int_small = ord(i) - CONST_ASCII_BASECODE
      int_small += offset
      int_new = int_small % CONST_CAESAR_CIPHER_ITR + CONST_ASCII_BASECODE
      list_output.append(chr(int_new))

def decode_Caesar_Cipher(_list_input, offset, list_output):
  for i in _list_input:
    if i < 'a' or i > 'z':
      list_output.append(i)
    else:
      int_small = ord(i) - CONST_ASCII_BASECODE
      int_small -= offset
      if int_small < 0:
        int_small += CONST_CAESAR_CIPHER_ITR
      int_new = int_small % CONST_CAESAR_CIPHER_ITR + CONST_ASCII_BASECODE
      list_output.append(chr(int_new))

def print_list_in_table(_list_in, _function):
  for i in range(26):
    candidat = defaultdict(list)
    for j in sorted(_list_in.keys()):
      _function(_list_in[j], i, candidat[j])
    print '%02d'%(i),
    show_hex_view(candidat)

def example_encode():
  plaintext         = 'abcdefghijklmnopqrstuvwxyz'
  dict_list_rawdata = defaultdict(list)
  parse_raw_data_to_list(plaintext, dict_list_rawdata)
  print_list_in_table(dict_list_rawdata, encode_Caesar_Cipher)

def example_decode():
  ciphertext        = 'abcdefghijklmnopqrstuvwxyz'
  dict_list_rawdata = defaultdict(list)
  parse_raw_data_to_list(ciphertext, dict_list_rawdata)
  print_list_in_table(dict_list_rawdata, decode_Caesar_Cipher)

  
if __name__ == '__main__':
  print "example: encode_Caesar_Cipher"
  example_encode()
  print
  print "example: decode_Caesar_Cipher"
  example_decode()
  