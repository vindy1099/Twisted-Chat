from twisted.internet import stdio, reactor, protocol
from twisted.protocols import basic

me = ""
username = ""

class DataForwardingProtocol(protocol.Protocol):
    
    def dataReceived(self, data):
        self.output.write(username + ": " + data)

class StdioProxyProtocol(DataForwardingProtocol):
    
      def connectionMade(self):
        inputForwarder = DataForwardingProtocol()
        inputForwarder.output = self.transport
  
        stdioWrapper = stdio.StandardIO(inputForwarder)
        self.output = stdioWrapper

        if me == "server":
          print("Peer connected...\n")
        else:
          print("Connected to peer...\n")
 
      def dataReceived(self, data):

          if(data.find("exit") != -1):
            print("\nDisconnecting from peer...\n")
            reactor.stop() 
          else:
            print(data)
        
  
class StdioProxyFactory(protocol.ClientFactory):
    protocol = StdioProxyProtocol

    def clientConnectionLost(self, transport, reason):
        print("\nPeer disconnected...\n") 
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()

IP = raw_input("\nEnter IP address to connect to: ")
username = raw_input("\nEnter your username: ")

EndPoint = StdioProxyFactory()

try:
  print("\nWaiting for peer to connect...\n")
  reactor.listenTCP(8007, EndPoint)
  me = "server"
except Exception as ex:
  print("\nAttempting to connect to peer...\n")
  reactor.connectTCP(IP, 8007, EndPoint)
  me = "client"

reactor.run()
