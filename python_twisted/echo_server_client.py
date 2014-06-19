#!/usr/bin/env python

# https://twistedmatrix.com/trac/

import sys
from twisted.internet import protocol, reactor

# ----- server
class EchoServer(protocol.Protocol):
  def connectionMade(self):
    client_ip = self.transport.getPeer()
    print "Client(%s) connected" % (client_ip)
  def ConnectionLost(self):
    client_ip = self.transport.getPeer()
    print "Client(%s) disconnected" % (client_ip)
  def dataReceived(self, data):
    client_ip = self.transport.getPeer()
    print "Client(%s) said:" % (client_ip) , data.rstrip()
    self.transport.write(data)
    #self.transport.loseConnection()

class EchoServerFactory(protocol.Factory):
  def buildProtocol(self, addr):
    return EchoServer()

# ----- client
class EchoClient(protocol.Protocol):
  def pass_user_input_to_server(self):
    myinput = raw_input("Want to say: ")
    if len(myinput) > 0:
      self.transport.write(myinput)
    else:
      self.transport.loseConnection()
      # or closes the connection immediately,
      # regardless of buffered data that is still unwritten in the transport,
      #self.transport.abortConnection()
  def connectionMade(self):
      self.pass_user_input_to_server()
  def dataReceived(self, data):
    print "Server said:", data
    self.pass_user_input_to_server()
    #self.transport.loseConnection()

class EchoClientFactory(protocol.ClientFactory):
  def buildProtocol(self, addr):
    return EchoClient()
  def clientConnectionFailed(self, connector, reason):
    print "Connection faield"
    reactor.stop()
  def clientConnectionLost(self, connector, reason):
    print "Connection lost"
    reactor.stop()


def print_usage(myname):
  print '''Usage:
  %s server 8080
    working as echo server at port 8080
  %s client 127.0.0.1 8080
    connecting to echo server at ip 127.0.0.1 and port 8080
''' % (myname, myname)

if __name__ == '__main__':
  isReady = False
  while(1):
    # client
    if len(sys.argv) == 4:
      (str_type, str_ip, str_port) = sys.argv[1:]
      if str_type == 'client' and int(str_port) > 1024 and len(str_ip.split('.')) == 4:
        reactor.connectTCP(str_ip, int(str_port), EchoClientFactory())
        isReady = True
        break
    # server
    if len(sys.argv) == 3:
      (str_type, str_port) = sys.argv[1:]
      if str_type == 'server' and int(str_port) > 1024:
        reactor.listenTCP(int(str_port), EchoServerFactory())
        isReady = True
        break
    print_usage(sys.argv[0])
    break
  if isReady:
    reactor.run()
