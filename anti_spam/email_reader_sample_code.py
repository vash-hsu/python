#!/usr/bin/env python

import sys, os, glob, getopt
import email, mimetypes, hashlib
from collections import defaultdict

from email_reader import EmlDictionary, cook_email_from_string

DM_DUPLICATED  = 'duplicated'
DM_WRITE_ERROR = 'error'
DM_OK          = 'ok'

def print_usage():
  print '''
to process input eml file and split it into text, html and attachments

Usage:
  -i <input folder> -o <output folder>
  -i --inputdir: indicate path of folder contains eml to process
  -i --outputdir: indicate path of folder (to be created and) to store processed files
'''

def parse_parameter(argv, input_dir_list, output_dir_list):
  if len (argv) == 0:
    print_usage()
    sys.exit(0)
  try:
    opts, args = getopt.getopt(argv[1:], "hi:o:", ["help", "inputdir=", "outputdir="])
  except getopt.GetoptError:
    print_usage()
    sys.exit(2)
  for opt, arg in opts:
    if '-h' == opt:
      print_usage()
      sys.exit(0)
    elif opt in ('-i', '--inputdir'):
      if os.path.isdir(arg):
        input_dir_list.append(arg)
      else:
        print "ERROR: invalid:", arg
    elif opt in ('-o', '--outputdir'):
      if os.path.isfile(arg):
        print "ERROR: path belongs to file:", arg
      elif os.path.isdir(arg):
        output_dir_list.append(arg)
      elif os.path.exists(arg):
        print "ERROR: invalid path to create folder:", arg
      else:
        output_dir_list.append(arg)

def dump_rawdata_to_filename(_raw, _sha1, _dir, _name):
  path_file2write = os.path.join(_dir, '.'.join([_sha1, _name]))
  if os.path.exists(path_file2write):
    return DM_DUPLICATED
  try:
    with open(path_file2write,'wb') as fhwrite:
      fhwrite.write(_raw)
      #print "DM: fhwrite:", path_file2write
      is_file_write_done = True
  except IOError:
      print "ERROR: IOError with open/write", path_file2write
      return DM_WRITE_ERROR
  return DM_OK

def adhoc_store_text(myeml, _dir_output):
  for body_type in myeml.get_body_content_type_sequence():
    print '\tContent :', body_type
    for data_list in myeml.retrive_body_by_type(body_type):
      for rawbuffer in data_list:
        # get each mail entity related to text/*
        body_sha1 = hashlib.sha1(rawbuffer).hexdigest()
        print '\tSHA-1   :', body_sha1
        print '\tFilesize:', len(rawbuffer)
        body_ext = body_type.split('/')[-1]
        if body_ext == 'plain':
          body_ext = 'txt'
        elif body_ext == 'html':
          body_ext = 'htm'
        else:
          body_ext = '.undef' # useless, should not happen
        #
        dump_status = dump_rawdata_to_filename(rawbuffer, body_sha1, _dir_output, body_ext)
        if dump_status == DM_DUPLICATED: # according to SHA1_filename
          #print "DM: bypass redundant file:",  name_candidate
          break
        if dump_status == DM_WRITE_ERROR:
          print "DM: fail to write file:", name_candidate
          continue
        if dump_status == DM_OK:
          break
        else:
          print "DM: todo: there is something out of my mind"

def adhoc_store_attachment(myeml, _dir_output):
  if len(myeml.get_attach_content_type_sequence()) > 0:
    #print '( ) demo, dump all attachments'
    for sha1_value, name_list, raw_content in myeml.retrive_attach_all():
      print '\tSHA-1   :', sha1_value
      print '\tFilename:', ';'.join(name_list)
      print '\tFilesize:', len(raw_content)
      is_file_write_done = False
      for name_candidate in name_list:
        dump_status = dump_rawdata_to_filename(raw_content, sha1_value,
                                               _dir_output, name_candidate)
        if dump_status == DM_DUPLICATED: # according to SHA1_filename
          #print "DM: bypass redundant file:",  name_candidate
          break
        if dump_status == DM_WRITE_ERROR:
          print "DM: fail to write file:", name_candidate
          continue
        if dump_status == DM_OK:
          break
        else:
          print "DM: todo: there is something out of my mind"

def process_eml_example(_rawbuffer, _dir_output):
  # ---------- ---------- ---------- ---------- ----------
  myeml = EmlDictionary()
  cook_email_from_string(_rawbuffer, myeml)
  ## ---------- ---------- ---------- ---------- ----------
  print '( ) demo, print interesting headers'
  for i in myeml.get_header_name_sequence():
    if myeml.is_header_about_what(i):
      print "\t%s:\t%s" % (i, myeml.get_header_by_name(i)[0])
    elif myeml.is_header_about_who(i):
      for j in myeml.get_header_by_name(i):
        print "\t%s:\t%s\t%s" %(i, j[0], j[1])
  #print '( ) demo, print mail entity with text/'
  #print myeml.get_body_content_type_sequence()
  #print
  ## ---------- ---------- ---------- ---------- ----------
  #print '( ) demo, if you are interested in text (a.k.a text/*)'
  #for entity_txt in myeml.retrive_body_by_type('text'):
  #  print entity_txt
  #print
  ## ---------- ---------- ---------- ---------- ----------
  # print '( ) demo, or we only care about html (a.k.a text/html)'
  # for entity_txt in myeml.retrive_body_by_type('html'):
  #  print entity_txt
  # print
  dir_text = os.path.join(dir_output, 'text')
  if not os.path.exists(dir_text):
    try:
      os.makedirs(dir_text)
    except os.error:
      print "ERROR: fail to create output folder:", dir_text
      sys.exit(0)
  adhoc_store_text(myeml, dir_text)
  ## ---------- ---------- ---------- ---------- ----------
  #print '( ) demo, print types of mail attachment'
  #print myeml.get_attach_content_type_sequence()
  #print
  # ---------- ---------- ---------- ---------- ----------
  dir_attachment = os.path.join(dir_output, 'attachment')
  try:
    if not os.path.exists(dir_attachment):
      os.makedirs(dir_attachment)
  except os.error:
    print "ERROR: fail to create output folder:", dir_attachment
    sys.exit(0)
  adhoc_store_attachment(myeml, dir_attachment)

if __name__ == '__main__':
  # ----------
  # parse input parameter, dir_list['input'] and dir_output
  # ----------
  dir_list = defaultdict(list)
  parse_parameter(sys.argv, dir_list['input'], dir_list['output'])
  if len(dir_list['input']) == 0 or len(dir_list['output']) == 0:
    print_usage()
    sys.exit(0)
  dir_output = dir_list['output'][-1]
  # ----------
  # prepare output folder
  # ----------
  try:
    if not os.path.exists(dir_output):
      os.makedirs(dir_output)
  except os.error:
    print "ERROR: fail to create output folder:", dir_output
  # ----------
  # process input folder one by one
  # ----------
  for dir_input in dir_list['input']:
    if not os.path.isdir(dir_input): # simple error handline (useless?)
      continue
    # for each *.eml, not recursive support
    for inputsample in glob.glob( os.path.join(dir_input,'*.eml') ):
      print "++", inputsample
      try:
        with open(inputsample, 'r') as fdread:
          rawbuffer = fdread.read()
      except IOError:
        print "ERROR: IOError while open", inputsample
      if rawbuffer == None or len(rawbuffer) == 0:
        print "ERROR: fail to retrieve:", inputsample
        continue
      process_eml_example(rawbuffer, dir_output)
