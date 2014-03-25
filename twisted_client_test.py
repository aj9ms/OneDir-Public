__author__ = 'ben'
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

class Greeter(Protocol):
    def sendMessage(self, msg):
        self.transport.write("MESSAGE %s\n" % msg)

    def writeUserName(self):
        self.transport.write("ben")

    def connectionMade(self):
        reactor.callLater(1, self.writeUserName)

    def dataReceived(self, data):
        if data.strip() == "Username:":
            self.transport.write("ben")
        elif data.strip() == "Password:":
            self.transport.write("pass")

def gotProtocol(p):
    p.sendMessage("Hello")
    reactor.callLater(1, p.sendMessage, "This is sent in a second")
    reactor.callLater(2, p.transport.loseConnection)

point = TCP4ClientEndpoint(reactor, "localhost", 8007)
d = connectProtocol(point, Greeter())
# d.addCallback(gotProtocol)
reactor.run()