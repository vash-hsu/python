#!/usr/bin/env python

import sys, getopt
import socket

import dns.resolver


# http://code.activestate.com/recipes/410692/

class switch(object):
  def __init__(self, value):
    self.value = value
    self.fall = False
  def __iter__(self):
    """Return the match method once, then stop"""
    yield self.match
    raise StopIteration
  def match(self, *args):
    """Indicate whether or not to enter a case suite"""
    if self.fall or not args:
      return True
    elif self.value in args: # changed for v1.5, see below
      self.fall = True
      return True
    else:
      return False

def usage():
  print 'Usage: -h / --help'
  print '       -t / --type [ ns | mx | a | aaaa ]'

def dig_nslookup(qtype, qstring):
  for case in switch(qtype):
    if case('ptr'):
      hostname, aliaslist, ipaddrlist= socket.gethostbyaddr(qstring)
      print "ptr :", hostname
      break
    if case('ns'):
      break
    if case('mx'):
      break
    if case('a'):
      (hostname, aliaslist, ipaddrlist) = socket.gethostbyname_ex(qstring)
      print "ipaddrlist:", ipaddrlist
      break
    if case('aaaa'):
      break

    if case(): # default
      print "WARM: unrecognized:", qtype
  pass


def dig_resolve(qtype, qstring):
  try:
    queried = dns.resolver.query(qstring, qtype)
    for i in queried.response.answer:
      for j in i.items:
        print "%s = %s" % (qtype, j)
  except dns.resolver.NXDOMAIN:
    print "NXDOMAIN: the query name does not exist"
  except dns.resolver.Timeout:
    print "Timeout: no answers could be found in the specified lifetime"
  except dns.resolver.YXDOMAIN:
    print "YXDOMAIN: the query name is too long after DNAME substitution"
  except dns.resolver.NoAnswer:
    print "NoAnswer: the response did not contain an answer and raise_on_no_answer is True."
  except dns.resolver.NoNameservers:
    print "NoNameservers: no non-broken nameservers are available to answer the question."


def main(argv):
  query_type = 'a'
  query_set = ()
  try:
    opts, args = getopt.getopt(argv, "ht:", ["type"])
    query_set = args
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt in  ('-h', '--help'):
      usage()
      sys.exit()
    elif opt in ("-t", "--type"):
      qtype = arg.lower()
      if qtype in ('a', 'cname', 'aaaa', 'ptr', 'ns','mx', 'txt'):
        query_type = qtype
      else:
        print "DM: unrecognized query type:", qtype
  if len(query_set) == 0:
    usage()
    sys.exit(0)
  for i in query_set:
    print "DM:", query_type, i
    for case in switch(qtype):
      if case('ptr'):
        dig_nslookup(query_type,i)
        break
      if case(): # default
        dig_resolve(query_type, i)
        break
    print


if __name__ == "__main__":
  main(sys.argv[1:])
