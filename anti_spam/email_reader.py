#!/usr/bin/env python

import sys, os, hashlib
import email, mimetypes
from collections import defaultdict

import unittest
import optparse

CONST_DEFAULT_CHARSET = 'big5'

# 2014/5/1

# __name__ = ['Attachment', 'EmlDictionary',
#             'cook_email_header', 'cook_email_body']

#----------
class Attachment:
  def __init__(self, sha1, content_type, filename, binary):
    self._sha1 = sha1
    self._content_type = content_type
    self._filename = filename
    self._binary = binary
  def get_sha1(self):
    return self._sha1
  def get_content_type(self):
    return self._content_type
  def get_filename(self):
    return self._filename
  def get_binary(self):
    return self._binary
#----------
class EmlDictionary:
  def __init__(self):
    self._header_list     = list()            # use list to keep original order 
    self._charset_chain   = defaultdict(list)
    self._header          = defaultdict(list) # key is lower case for usability
    self._header_in_lines = ['received', 'x-received',
                             'authentication-results', 'received-spf',
                             'dkim-signature', 'domainKey-signature'
                            ]
    self._header_about_what = ['subject']
    self._header_about_who = ['from', 'to', 'cc', 'bcc']
    self._body_type   = list()
    self._body        = defaultdict(list)
    self._attach_type = defaultdict(list) # i.e. image/png -> [SHA1, SHA2]
    self._attach_bin  = dict()            # i.e. SHA1 --> MZ...
    self._attach_name = defaultdict(list) # i.e. SHA1 --> ['n1', 'n2']
  # set
  def is_header_multiline(self, name):
    return name.lower() in self._header_in_lines
  def is_header_about_what(self, name):
    return name.lower() in self._header_about_what
  def is_header_about_who(self, name):
    return name.lower() in self._header_about_who
  def record_charset_chain(self, source_field, charset):
    self._charset_chain[source_field.lower()].append(charset)
  def insert_header(self, name, value):
    self._header_list.append(name)
    self._header[name.lower()].append(value)
  def insert_body(self, cont_type, charset, rawdata):
    self.record_charset_chain(cont_type, charset)
    self._body_type.append(cont_type)
    self._body[cont_type.lower()].append(rawdata)
  def insert_attachment(self, attach):
    key_sha1 = attach.get_sha1()
    key_type = attach.get_content_type()
    self._attach_type[key_type].append(key_sha1)
    self._attach_bin[key_sha1] = attach.get_binary()
    self._attach_name[key_sha1].append(attach.get_filename())
  # get
  def get_header_name_sequence(self):
    return self._header_list
  def get_header_by_name(self, name):
    header_id = name.lower()
    if self._header.has_key(header_id):
      return self._header[header_id]
    else:
      return None
  def get_body_content_type_sequence(self):
    return self._body_type
  def get_attach_content_type_sequence(self):
    return self._attach_type.keys()
  def retrive_body_by_type(self, string_type):
    body_id = string_type.lower()
    if self._body.has_key(body_id):
      yield self._body[body_id]
    else:
      for entry in self._body.keys():
        if string_type in entry.split('/'):
          yield self._body[entry]
  def retrive_attach_by_type(self, string_type):
    attach_type = string_type.lower()
    if self._attach_type.has_key(attach_type):
      for sha1_key in self._attach_type[attach_type]:
        yield (sha1_key,                    # string
               self._attach_name[sha1_key], # string list
               self._attach_bin[sha1_key])  # binary buffer
  def retrive_attach_all(self):
    for type in self._attach_type.keys():
      for sha1_key in self._attach_type[type]:
        yield (sha1_key,                    # string
               self._attach_name[sha1_key], # string list
               self._attach_bin[sha1_key])  # binary buffer
#----------
def unicode_convert(buffer_src, charset_src, charset_dst):
  try:
    rawbuffer_uc = unicode(buffer_src, charset_src)
    rawbuffer_uc = rawbuffer_uc.encode(charset_dst, 'ignore')
  except UnicodeDecodeError:
    print "ERROR: UnicodeDecodeError, fail to covert from", charset_src, "to unicode"
    return ''
  except UnicodeEncodeError:
    print "ERROR: UnicodeEncodeError, fail to covert from unicode to", charset_dst
    return ''
  return rawbuffer_uc
#----------
def cook_email_from_string(rawbuffer, email_dict):
  if rawbuffer == None or len(rawbuffer) == 0:
    return False
  try:
    emailmsg = email.message_from_string(rawbuffer)
  except email.errors.MessageError:
    print "Exception: something wrong with email.message_from_string"
    print "           todo: find something which you can take actions on ~~~"
    return False
  else:
    return cook_email_header(emailmsg, email_dict) and cook_email_body(emailmsg, email_dict)
#----------
def cook_email_header(python_email, email_dict):
  if python_email == None or email_dict == None:
    return False
  for hname, hvalue in python_email.items():
    normalized = hvalue.strip()
    header_id = hname.lower()
    # to format multi-lines headers if necessary
    if email_dict.is_header_multiline(header_id):
      normalized = ' '.join(normalized.rsplit()) # strip \r\n\t
      email_dict.insert_header(hname, normalized)
    # # for To, CC, ...
    elif email_dict.is_header_about_who(header_id):
      for single_who in normalized.splitlines():
        realname, eaddr = email.utils.parseaddr(single_who)
        if eaddr == None:
          continue
        if realname != None:
          realname = email.Utils.collapse_rfc2231_value(realname).strip()
          (rawdata, charset) = email.Header.decode_header(realname)[0]
          charset_candidate = charset
          if rawdata != None:
            if charset == None:
              charset_candidate = CONST_DEFAULT_CHARSET
            else:
              email_dict.record_charset_chain(hname, charset)
            # unicode conversion
            rawbuffer_uc = unicode_convert(rawdata, charset_candidate, 'utf-8')
            if len(rawbuffer_uc) == 0:
              rawbuffer_uc = rawdata
            email_dict.insert_header(hname, [rawbuffer_uc, eaddr])
        else:
          email_dict.insert_header(hname, [None, eaddr])
    # for Subject
    elif email_dict.is_header_about_what(header_id):
      normalized = email.Utils.collapse_rfc2231_value(normalized).strip()
      (rawdata, charset) = email.Header.decode_header(normalized)[0]
      charset_candidate = charset
      if rawdata == None:
        print "DM: email.Header.decode_header() got nothing"
        continue
      if charset == None:
        charset_candidate = CONST_DEFAULT_CHARSET
      # unicode conversion
      rawbuffer_uc = unicode_convert(rawdata, charset_candidate, 'utf-8')
      if len(rawbuffer_uc) == 0:
        rawbuffer_uc = rawdata
      email_dict.insert_header(hname, rawbuffer_uc)
      email_dict.record_charset_chain(hname, charset)
    else:
      email_dict.insert_header(hname, normalized)
  return True

def cook_email_body_by_entity(_pythoneml, _email_dict):
  main_type = _pythoneml.get_content_maintype()
  cont_type = _pythoneml.get_content_type()
  if 'text' == main_type:
    eml_charset  = _pythoneml.get_content_charset()
    rawbuffer    = _pythoneml.get_payload(None, True)
    if rawbuffer == None:
      print "DM: get_payload() got nothing"
      return False
    if eml_charset == None:
      eml_charset = CONST_DEFAULT_CHARSET
    # unicode conversion
    rawbuffer_uc = unicode_convert(rawbuffer, eml_charset, 'utf-8')
    if len(rawbuffer_uc) == 0:
        rawbuffer_uc = rawbuffer
    _email_dict.insert_body(cont_type, eml_charset, rawbuffer_uc)
  # multiple part
  elif 'multipart' == main_type: # ignore due to empty without useful info
    #print "========= multipart ========="
    pass
  # attachment
  else:
    # payload, filename and its sha1
    string_filename = _pythoneml.get_filename()
    rawbuffer       = _pythoneml.get_payload(None, True)
    if rawbuffer == None:
      print "ERROR: fail to get_payload()"
      return False
    string_sha1 = hashlib.sha1(rawbuffer).hexdigest()
    if string_filename == None:
      string_ext = mimetypes.guess_extension(_pythoneml.get_content_type())
      if string_ext == None:
        string_ext = '.bin'
      string_filename = string_sha1 + string_ext
    else:
      # *** process filename ***
      # from =?UTF-8?B?5Zyw542E5bua5oi/LnBuZw==?=
      # to ('\xe5\x9c\xb0\xe7\x8d\x84\xe5\xbb\x9a\xe6\x88\xbf.png', 'utf-8')
      fn_new = email.Utils.collapse_rfc2231_value(string_filename).strip()
      (string_filename, charset) = email.Header.decode_header(fn_new)[0]
      if charset != None and len(charset) > 0:
        filename_uc = unicode_convert(string_filename, charset, 'utf-8')
        if len(filename_uc) > 0:
          string_filename = filename_uc
    attach = Attachment(string_sha1, cont_type, string_filename, rawbuffer)
    _email_dict.insert_attachment(attach)
  return True

def cook_email_body(python_email, email_dict):
  if python_email == None or email_dict == None:
    return False
  # single entity
  if not python_email.is_multipart():
    cook_email_body_by_entity(python_email, email_dict)
  # multi-part
  else:
    for part in python_email.walk():
      cook_email_body_by_entity(part, email_dict)
  return True

class email_unicode_handleTest(unittest.TestCase):
  _eml_raw = '''Subject: =?UTF-8?B?5ris6Kmm5Lit5paH5L+h5Lu26ZmE5aS+5qqU?=
From: =?UTF-8?B?5ZOy6Z2S?= <hello@world.com>
To: =?big5?B?r3WquqxP?= <hi@world.com>
Cc: =?UTF-8?B?6L+U5Zue?= <byebye@world.com>
Content-Type: multipart/mixed; boundary=f46d041c4148d7bf9f04f8450fce

--f46d041c4148d7bf9f04f8450fce
Content-Type: multipart/alternative; boundary=f46d041c4148d7bf9a04f8450fcc

--f46d041c4148d7bf9a04f8450fcc
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: base64

5Lit5paH5YWn5a65
--f46d041c4148d7bf9a04f8450fcc
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: base64

5Lit5paH5YWn5a65
--f46d041c4148d7bf9a04f8450fcc--
--f46d041c4148d7bf9f04f8450fce
Content-Type: image/png; name="=?UTF-8?B?5Zyw542E5bua5oi/LnBuZw==?="
Content-Disposition: attachment; filename="=?UTF-8?B?5Zyw542E5bua5oi/LnBuZw==?="
Content-Transfer-Encoding: base64
X-Attachment-Id: f_humu8d9n0

iVBORw0KGgoAAAANSUhEUgAAApQAAAHOCAIAAACpUA5nAAAAAXNSR0IArs4c6QAAAARnQU1BAACx
jwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAP+lSURBVHhetP0FeORInu4Lu8yUZma208yUzkwn
uVl5N36rvHmNrYL7yZsvE1XKG98Ukv678qZ7gy1R3Ffe9CEgr/9Gebc0/hfWY6hubYsRpwAAAABJ
RU5ErkJggg==
--f46d041c4148d7bf9f04f8450fce--
'''
  def setUp(self):
    self.emailmsg = email.message_from_string(self._eml_raw)
    self.myeml = EmlDictionary()
    cook_email_header(self.emailmsg, self.myeml)
    cook_email_body(self.emailmsg, self.myeml)
  def tearDown(self):
    del self.myeml
    del self.emailmsg
  def test_RAT_retrieve_mail_from_to_cc(self):
    "FAST: retrieve name of From, To, CC field"
    #for i in self.myeml.get_header_by_name('from'):
    #  print "From [%s]" % (i[0])
    self.assertEqual(self.myeml.get_header_by_name('from')[0][0],
      '\xe5\x93\xb2\xe9\x9d\x92')
    #for i in self.myeml.get_header_by_name('to'):
    #  print "To   [%s]" % (i[0])
    self.assertEqual(self.myeml.get_header_by_name('to')[0][0],
      '\xe7\x9c\x9f\xe7\x9a\x84\xe6\x98\xaf')
    #for i in self.myeml.get_header_by_name('cc'):
    #  print "Cc   [%s]" % (i[0])
    self.assertEqual(self.myeml.get_header_by_name('cc')[0][0],
      '\xe8\xbf\x94\xe5\x9b\x9e')
  def test_RAT_retrieve_mail_subject(self):
    "FAST: retrieve Subject"
    #for i in self.myeml.get_header_by_name('subject'):
    #  print "Subject [%s]" % (i)
    self.assertEqual(self.myeml.get_header_by_name('subject')[0],
      '\xe6\xb8\xac\xe8\xa9\xa6\xe4\xb8\xad\xe6\x96\x87\xe4\xbf\xa1\xe4\xbb\xb6\xe9\x99\x84\xe5\xa4\xbe\xe6\xaa\x94')
  def test_RAT_retrieve_mail_body(self):
    "FAST: retrieve Body plain-text"
    for data_list in self.myeml.retrive_body_by_type('text/plain'):
      for rawbuffer in data_list:
        #print "Body [%s]" % (rawbuffer)
        self.assertEqual(rawbuffer, '\xe4\xb8\xad\xe6\x96\x87\xe5\x85\xa7\xe5\xae\xb9')
  def test_RAT_retrieve_mail_filename(self):
    "FAST: retrieve Filename of Attachment"
    for sha1_value, name_list, _ in self.myeml.retrive_attach_all():
      #print "Attachment [%s]" % (name_list[0])
      self.assertEqual(name_list[0], '\xe5\x9c\xb0\xe7\x8d\x84\xe5\xbb\x9a\xe6\x88\xbf.png')

class email_readerTest(unittest.TestCase):
  _eml_raw = '''Delivered-To: hi.kitty@gmail.com
Received: by 8.8.8.8 with SMTP id bk7csp389239vec;
        Thu, 19 Sep 2013 07:06:33 -0700 (PDT)
Return-Path: <undelivered+96055+5305+38277702@msgapp.com>
Received: from smtp.gogo.power (smtp.gogo.power. [10.10.10.10])
        by mx.google.com with ESMTP id i5si6886367eeg.235.1969.12.31.16.00.00;
        Thu, 19 Sep 2013 07:06:32 -0700 (PDT)
Received: from Hi-Moto (192.168.2.170) by smtp.gogo.power (PowerMTA(TM) v3.5r16) id h7c2be1m5qg5 for <hi.kitty@gmail.com>; Thu, 19 Sep 2013 10:05:33 -0400 (envelope-from <undelivered+96055+5305+38277702@msgapp.com>)
Date: Thu, 19 Sep 2013 10:06:15 -0400
Subject: Hello World Salutes Veterans with Super Savings
Content-Type: multipart/mixed; boundary=14dae94edfed9095a004f845201a
From: "Hello World" <cs@listserve.gogo.power>
To: "Kitty Hi" <hi.kitty@gmail.com>

--14dae94edfed9095a004f845201a
Content-Type: multipart/alternative; boundary=14dae94edfed90959504f8452018

--14dae94edfed90959504f8452018
Content-Type: text/plain; charset=UTF-8

*BE CONSISTENT*.

--14dae94edfed90959504f8452018
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

<div dir=3D"ltr"><p style=3D"color:rgb(51,51,51);font-family:sans-serif;fon=
t-size:13.3333px;font-style:normal;font-variant:normal;font-weight:normal;l=
etter-spacing:normal;line-height:normal;text-align:start;text-indent:0px;te=
xt-transform:none;white-space:normal;word-spacing:0px">
</div>

--14dae94edfed90959504f8452018--
--14dae94edfed9095a004f845201a
Content-Type: image/png; name="=?UTF-8?B?5Zyw542E5bua5oi/LnBuZw==?="
Content-Disposition: attachment; filename="=?UTF-8?B?5Zyw542E5bua5oi/LnBuZw==?="
Content-Transfer-Encoding: base64
X-Attachment-Id: f_humugwe70

iVBORw0KGgoAAAANSUhEUgAAApQAAAHOCAIAAACpUA5nAAAAAXNSR0IArs4c6QAAAARnQU1BAACx
jwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAP+lSURBVHhetP0FeORInu4Lu8yUZma208yUzkwn
uVl5N36rvHmNrYL7yZsvE1XKG98Ukv678qZ7gy1R3Ffe9CEgr/9Gebc0/hfWY6hubYsRpwAAAABJ
RU5ErkJggg==
--14dae94edfed9095a004f845201a--
'''
  def setUp(self):
    self.emailmsg = email.message_from_string(self._eml_raw)
    self.myeml = EmlDictionary()
    cook_email_header(self.emailmsg, self.myeml)
    cook_email_body(self.emailmsg, self.myeml)
  def tearDown(self):
    del self.myeml
    del self.emailmsg
  def test_RAT_retrieve_mail_header(self):
    "RAT: parse eml in memory and try get info of mail header"
    self.assertEqual(10, len(self.myeml.get_header_name_sequence()))
  def test_RAT_retrieve_mail_body(self):
    "RAT: parse eml in memory and try get info of mail body"
    self.assertEqual(2, len(self.myeml.get_body_content_type_sequence()))
  def test_RAT_retrieve_mail_attachment(self):
    "RAT: parse eml in memory and try get info of mail body"
    self.assertEqual(1, len(self.myeml.get_attach_content_type_sequence()))

    
if __name__ == '__main__':

  testruner  = unittest.TextTestRunner(verbosity=2)
  testloader = unittest.TestLoader()
  
  list_testsuit = list()
  for i in [email_readerTest,
            email_unicode_handleTest]:
    testsuit = testloader.loadTestsFromTestCase(i)
    list_testsuit.append(testsuit)
  alltests = unittest.TestSuite(list_testsuit)
  
  testruner.run(alltests)
