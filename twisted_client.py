__author__ = 'ben'
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol
stateMachine = {
    'username': 'password',
    'password': 'ready',

}
class Greeter(Protocol):
    # def sendMessage(self, msg):
    #     self.transport.write("MESSAGE %s\n" % msg)

    def __init__(self):
        self.state = 'username'

    def writeUserName(self):
        self.transport.write("ben")
        self.state = 'password'

    def connectionMade(self):
        reactor.callLater(1, self.writeUserName)

    def sendFile(self, filePath):
        self.transport.write("file")

    def dataReceived(self, data):
        if self.state == 'username':
            self.transport.write("ben")
            self.state = stateMachine[self.state]
        elif self.state == 'password':
            self.transport.write("pass")
            self.state = stateMachine[self.state]

# def gotProtocol(p):
#     p.sendMessage("Hello")
#     reactor.callLater(1, p.sendMessage, "This is sent in a second")
#     reactor.callLater(2, p.transport.loseConnection)

point = TCP4ClientEndpoint(reactor, "localhost", 8007)
d = connectProtocol(point, Greeter())
# d.addCallback(gotProtocol)
reactor.run()