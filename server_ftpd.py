#!/usr/bin/env python
# $Id$

#  pyftpdlib is released under the MIT license, reproduced below:
#  ======================================================================
#  Copyright (C) 2007-2014 Giampaolo Rodola' <g.rodola@gmail.com>
#
#                         All Rights Reserved
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#  ======================================================================

"""A basic FTP server which uses a DummyAuthorizer for managing 'virtual
users', setting a limit for incoming connections.
"""

import os
from threading import Thread

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

# Instantiate a dummy authorizer for managing 'virtual' users
authorizer = DummyAuthorizer()

class Auth(Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.state = "initialize"

    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols+1

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols-1

    def dataReceived(self, data):
        print data + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        if data.strip().startswith('newuser'):
            info = data.strip().split(':')
            username = info[1]
            password = info[2]
            open('pass.dat', 'a').write(username + ':' + password + '\n')
            try:
                os.mkdir(os.path.join(os.getcwd(), info[1]))
            except:
                pass
            authorizer.add_user(info[1], info[2], os.path.join(os.getcwd(), info[1]), perm='elradfmwM')
        elif data.strip().startswith('newpass'):
            info = data.strip().split(':')
            username = info[1]
            password = info[2]
            authorizer.remove_user(info[1])
            authorizer.add_user(info[1], info[2], os.path.join(os.getcwd(), info[1]), perm='elradfmwM')

class AuthFactory(Factory):
    def __init__(self):
        self.numProtocols = 0
    def buildProtocol(self, addr):
        return Auth(self)

def runTwisted(server):
    server.serve_forever()

def main():
    # Define a new user having full r/w permissions and a read-only
    # anonymous user
    for line in open('pass.dat'):
        info = line.split(':')
        try:
            os.mkdir(os.path.join(os.getcwd(), info[0]))
        except:
            pass
        authorizer.add_user(info[0], info[1].strip(), os.path.join(os.getcwd(), info[0]), perm='elradfmwM')
    authorizer.add_user('root', 'password', os.path.join(os.getcwd()), perm='elradfmwM')
    # authorizer.remove_user('ben')
    # authorizer.add_user('ben', 'edgar', os.path.join(os.getcwd(), 'ben'), perm='elradfmwM')
    # authorizer.add_user('ben', 'lol', os.getcwd())
    # authorizer.add_anonymous(os.getcwd())

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "OneDir Ready"

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    #handler.masquerade_address = '151.25.42.11'
    #handler.passive_ports = range(60000, 65535)

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    address = ('localhost', 21)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()
    twistThread = Thread(target=runTwisted, args=(server,))
    twistThread.start()
    endpoint = TCP4ServerEndpoint(reactor, 8007)
    endpoint.listen(AuthFactory())
    reactor.run()

if __name__ == '__main__':
    main()