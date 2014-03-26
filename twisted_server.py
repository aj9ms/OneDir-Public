__author__ = 'ben'
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

class Auth(Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.state = "initialize"
        self.username = ""
        self.password = ""

    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols+1
        self.transport.write(
            "Welcome! There are currently %d open connections.\n" %
            (self.factory.numProtocols,))
        self.transport.write("Please Login.\n")
        self.transport.write("Username: ")
        self.state = "username"
        print "getting username"

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols-1

    def dataReceived(self, data):
        if self.state == "username":
            self.username = data.strip()
            self.transport.write("Password: ")
            self.state = "password"
            print "getting password"
        elif self.state == "password":
            self.password = data.strip()
            # Try to login using the database
            self.state = "loggedin"
            print "A user logged in"
            # If can't login, create new account with credentials

        elif data.strip() == "quit":
            self.transport.loseConnection()
        else:
            self.transport.write("Welcome " + self.username + "!\n")

class AuthFactory(Factory):
    def __init__(self):
        self.numProtocols = 0
    def buildProtocol(self, addr):
        return Auth(self)

# 8007 is the port you want to run under. Choose something >1024
endpoint = TCP4ServerEndpoint(reactor, 8007)
endpoint.listen(AuthFactory())
reactor.run()