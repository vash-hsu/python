#!/usr/bin/env python

# https://docs.python.org/2.6/library/poplib.html
# https://docs.python.org/2/library/hashlib.html
# https://docs.python.org/2.6/library/email.parser.html

import sys, os
import getpass, poplib
import email, hashlib

__all__ = ['']

import argv

string_Usage = '''\

usage     : -u user@abc.com -s pop.gmail.com -p 995 -l
          : -u user@abc.com -s pop.gmail.com -p 995 -m localmbox

-u user   : email address, i.e. user@abc.com
-s server : pop3 server, i.e. pop.gmail.com
-p port   : port number, default is 995
-l        : lise all pending emails, number and size in bytes
-ll       : lise email Subject and Date; save emil in local mailbox
-lll      : lise email Subject, Date, From and To; save emil in local mailbox
-m folder : specify path of local mailbox, default is localmbox
'''

def print_usage(banner):
  print banner + "\n"

def setup_pop3_worker(username, password, pop3server, pop3port):
  mailclient = poplib.POP3_SSL(pop3server, pop3port)
  secret = password
  #mailclient.apop(username, secret)
  mailclient.user(username)
  mailclient.pass_(secret)
  return mailclient

def pop3_worker_act(mailclient, listlevel, mailbox):
  localsave_ready = True
  # save email to local disk, auto
  if not os.path.exists(mailbox):
    os.makedirs(mailbox)
  elif not os.path.isdir(mailbox):
    print "ERROR: fail to prepare local output folder:", mailbox
    localsave_ready = False
  # list and save email in background
  if listlevel > 1:
    response, msglist, size = mailclient.list()
    print response
    for entry in msglist:
      (sn, size) = entry.split()
      (state, lines, size) = mailclient.retr(sn)
      rawbuffer = '\r\n'.join(lines)
      if localsave_ready:
        sha1 = hashlib.sha1(rawbuffer)
        string_sha1 = sha1.hexdigest()
        with open(os.path.join(mailbox,string_sha1+'.eml'),'wb') as wfd:
          wfd.write(rawbuffer)
      msg = email.message_from_string(rawbuffer)
      print '--', sn, '--------'
      print 'Date   :', msg['date']
      print 'Subject:', msg['subject']
      if listlevel > 2: # From, to, Subject
        print 'From   :', msg['from']
        print 'To     :', msg['to']
  elif listlevel > 0:
    response, msglist, size = mailclient.list()
    print response
    for entry in msglist:
      (sn, size) = entry.split()
      print "#%03d\t%d bytes" % (int(sn), int(size))
  else:
    (msg_ctr, mbox_size) = mailclient.stat()
    print "Pending Messages  :", msg_ctr
    print "Mailbox Size(Byte):", mbox_size

def teardown_pop3_worker(mailclient):
  mailclient.quit()

def main(arguments):
  param   = {'u':list(),
             's':list(),
             'p':list(['995']),      # default port 995
             'm':list(['localmbox']) # default path of mailbox
             }
  flag    = {'l':list()}

  if False == argv.prase_argv_to_param(arguments, param, flag, None):
    print_usage(string_Usage)
    sys.exit(0)
  while len(param['u']) == 0:
    print "user email address =",
    stringin = raw_input()
    if len(stringin) > 0 and stringin.strip() != "":
      param['u'].append(stringin)
  while len(param['s']) == 0:
    print "pop3 server =",
    stringin = raw_input()
    if len(stringin) > 0 and stringin.strip() != "":
      param['s'].append(stringin)
  # ----- -----
  # setup pop3 connection
  # ----- -----
  # it's safer to request password by getpass() than command line paramemter
  secret = getpass.getpass()
  mailclient = setup_pop3_worker(
    param['u'][-1],
    secret,
    param['s'][-1],
    param['p'][-1])
  if mailclient == None:
    print "ERROR: fail to connect to target server"
    sys.exit(0)
  # ----- -----
  # welcome
  # ----- -----
  print mailclient.getwelcome()
  (msg_count, mbx_size) = mailclient.stat()
  print msg_count, mbx_size
  # ----- -----
  # action
  # ----- -----
  if msg_count != 0 and len(flag['l']) > 0:
    pop3_worker_act(mailclient, len(flag['l']), mailbox)
  # ----- -----
  # tear down
  # ----- -----
  teardown_pop3_worker(mailclient)

if __name__ == '__main__':
  main(sys.argv[1:])
