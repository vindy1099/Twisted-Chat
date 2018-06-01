from twisted.internet import reactor, protocol
from twisted.protocols import basic
from threading import Thread
import curses
import atexit
import time

me = ""
username = ""

IP = raw_input("\nEnter IP address to connect to: ")
username = raw_input("\nEnter your username: ")

whole_screen = curses.initscr()
whole_screen.erase()

def restore_console():
    curses.endwin()

atexit.register(restore_console)

curses.curs_set(0)

chat_window = curses.newwin(int(float(curses.LINES*0.67)), curses.COLS, 0, 0)
chat_window.scrollok(1)
chat_window.idlok(1)
chat_window.refresh()

divider = curses.newwin(1, curses.COLS, int(float(curses.LINES*0.67)) + 1, 0)

for i in range(curses.COLS - 1):
  divider.addch('_')

divider.refresh()

input_window = curses.newwin(curses.LINES - int(float(curses.LINES*0.67)) - 3, curses.COLS, int(float(curses.LINES*0.67)) + 3, 0)
input_window.scrollok(1)
input_window.idlok(1)

input_window.refresh()

class PeerProtocol(protocol.Protocol):

      def connectionMade(self):
          if me == "server":
            chat_window.addstr("\nPeer connected...\n")
          else:
            chat_window.addstr("\nConnected to peer...\n")
            self.transport.write("\n" + username + " has entered the chat...\n")
          
          chat_window.refresh()
          input_window.move(0, 0)
          input_window.refresh()

      def dataReceived(self, data):
          if(data.find("exit chat") != -1):
            chat_window.addstr("\nDisconnecting from peer...\n")
            chat_window.refresh()
            time.sleep(0.5)
            reactor.stop()
          else:
            chat_window.addstr(data)
            chat_window.refresh()
            input_window.refresh()

      def sendMessage(self, data):
          if(data.find("exit chat") != -1):
            chat_window.addstr("\nDisconnecting from peer...\n")
            chat_window.refresh()
            self.transport.write(data)
            time.sleep(0.5)
            reactor.stop()
          else:
            chat_window.addstr("\n" + username + ": " + data + "\n")
            chat_window.refresh()
            self.transport.write("\n" + username + ": " + data + "\n")
            input_window.refresh()

class PeerFactory(protocol.ClientFactory):

      PROTOCOL = PeerProtocol()

      def buildProtocol(self, addr):
          return self.PROTOCOL

      def startedConnecting(self, transport):
          chat_window.addstr("Attempting to connect to peer...\n")
          chat_window.refresh()
          me = "client"

      def clientConnectionLost(self, transport, reason):
          chat_window.addstr("\nPeer disconnected...\n")
          chat_window.refresh()
          time.sleep(0.5)
          reactor.stop()

      def clientConnectionFailed(self, transport, reason):
          chat_window.addstr("\nCouldn't connect to peer...\n")
          chat_window.refresh()
          chat_window.addstr("\nWaiting for peer to connect...\n")
          chat_window.refresh()
          input_window.move(0, 0)
          input_window.refresh()
          reactor.listenTCP(8007, EndPoint)
          me = "server"

EndPoint = PeerFactory()

class InputWorker(Thread):
   def __init__(self):

       Thread.__init__(self)

   def run(self):

       while True:
            if EndPoint.PROTOCOL is not None:
               curses.curs_set(1)
               EndPoint.PROTOCOL.sendMessage(input_window.getstr())
               input_window.refresh()
               input_window.erase()
               curses.curs_set(0)

input = InputWorker()
input.daemon = True

try:
  input.start()
except Exception as ex:
  input_window(ex)

reactor.connectTCP(IP, 8007, EndPoint, 3)

reactor.run()
curses.endwin()
