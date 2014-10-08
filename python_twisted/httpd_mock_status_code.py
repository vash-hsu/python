#!/usr/bin/env python

import sys
from twisted.protocols import basic
from twisted.internet import protocol, reactor

def printUsage(myname):
  print '''Usage: %s [Port Number]
  i.e. %s 8000
       hosting httpd on *:8000
''' % (myname, myname)


httpcodeFromWiki = {
  100 :'Continue',
  101 :'Switching Protocols',
  102 :'Processing (WebDAV; RFC 2518)',
  200 :'OK',
  201 :'Created',
  202 :'Accepted',
  203 :'Non-Authoritative Information (since HTTP/1.1)',
  204 :'No Content',
  205 :'Reset Content',
  206 :'Partial Content',
  207 :'Multi-Status (WebDAV; RFC 4918)',
  208 :'Already Reported (WebDAV; RFC 5842)',
  226 :'IM Used (RFC 3229)',
  300 :'Multiple Choices',
  301 :'Moved Permanently',
  302 :'Found',
  303 :'See Other (since HTTP/1.1)',
  304 :'Not Modified',
  305 :'Use Proxy (since HTTP/1.1)',
  306 :'Switch Proxy',
  307 :'Temporary Redirect (since HTTP/1.1)',
  308 :'Permanent Redirect (Experimental RFC; RFC 7238)',
  400 :'Bad Request',
  401 :'Unauthorized',
  402 :'Payment Required',
  403 :'Forbidden',
  404 :'Not Found',
  405 :'Method Not Allowed',
  406 :'Not Acceptable',
  407 :'Proxy Authentication Required',
  408 :'Request Timeout',
  409 :'Conflict',
  410 :'Gone',
  411 :'Length Required',
  412 :'Precondition Failed',
  413 :'Request Entity Too Large',
  414 :'Request-URI Too Long',
  415 :'Unsupported Media Type',
  416 :'Requested Range Not Satisfiable',
  417 :'Expectation Failed',
  418 :'I\'m a teapot (RFC 2324)',
  419 :'Authentication Timeout (not in RFC 2616)',
  420 :'Method Failure (Spring Framework)',
  420 :'Enhance Your Calm (Twitter)',
  422 :'Unprocessable Entity (WebDAV; RFC 4918)',
  423 :'Locked (WebDAV; RFC 4918)',
  424 :'Failed Dependency (WebDAV; RFC 4918)',
  426 :'Upgrade Required',
  428 :'Precondition Required (RFC 6585)',
  429 :'Too Many Requests (RFC 6585)',
  431 :'Request Header Fields Too Large (RFC 6585)',
  440 :'Login Timeout (Microsoft)',
  444 :'No Response (Nginx)',
  449 :'Retry With (Microsoft)',
  450 :'Blocked by Windows Parental Controls (Microsoft)',
  451 :'Unavailable For Legal Reasons (Internet draft)',
  451 :'Redirect (Microsoft)',
  494 :'Request Header Too Large (Nginx)',
  495 :'Cert Error (Nginx)',
  496 :'No Cert (Nginx)',
  497 :'HTTP to HTTPS (Nginx)',
  498 :'Token expired/invalid (Esri)',
  499 :'Client Closed Request (Nginx)',
  499 :'Token required (Esri)',
}

# default 200
def parseRequestHeader4ReturnCode(line):
  if not line or len(line) <=3:
    return 200
  terms = line.split()
  if len(terms) == 3 and terms[0].lower() == 'get':
    pathparam = terms[1].split('/')
    if len(pathparam) == 3 \
       and pathparam[1].lower() == 'returncode' \
       and pathparam[2].isdigit():
      return int(pathparam[2])
  return 200

# i.e. 200 OK
def convertCode2Str(intnum):
  if httpcodeFromWiki.has_key(intnum):
    return httpcodeFromWiki[intnum]
  else:
    return 'undefined'

class HTTPStatusProtocl(basic.LineReceiver):
  def __init__(self):
    self.lines = []
    self.rcode = 200 # default 200 OK
  def lineReceived(self, line):
    #print("DM: lineReceived()")
    self.lines.append(line)
    if not line:
      self.sendResponse()
  def sendResponse(self):
    #print("DM: sendResponse()")
    self.rcode = parseRequestHeader4ReturnCode(self.lines[0])
    head4http = ' '.join(['HTTP/1.1', str(self.rcode), convertCode2Str(self.rcode)])
    print "DM:", head4http
    self.sendLine(head4http)
    #self.sendLine('HTTP/1.1 200 OK')
    self.sendLine("")
    responseBody = "<BR />\r\n".join(self.lines)
    self.transport.write(responseBody)
    self.transport.loseConnection()

class HTTPStatusFactory(protocol.ServerFactory):
  def buildProtocol(self, addr):
    return HTTPStatusProtocl()

if __name__ == '__main__':
  if len(sys.argv) == 2 and sys.argv[1].isdigit():
    int_port = int(sys.argv[1])
    reactor.listenTCP(int_port, HTTPStatusFactory())
    reactor.run()
  else:
    printUsage(sys.argv[0])