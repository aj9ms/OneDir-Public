__author__ = 'ben'
from twisted.internet import protocol, reactor

# how to do servers -- https://twistedmatrix.com/documents/current/core/howto/servers.html
# how to do clients -- https://twistedmatrix.com/documents/current/core/howto/clients.html

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        if data.strip() == 'update':
            self.transport.write('you are trying to update')
        else:
            self.transport.write(str(type(data)) + '\n' + data)
        # self.transport.write('Sup Dawg\n')
        # self.transport.write(data)
        # shuts down the connection after transmitting all data, use
        # abortConnection() if you want to shut down transmitting immediately
        #self.transport.loseConnection()

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

reactor.listenTCP(1234, EchoFactory())
reactor.run()