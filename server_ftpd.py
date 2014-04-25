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

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer, MultiprocessFTPServer

class Handler(FTPHandler):
    def ftp_STAT(self, line):
        a = line.split(":")
        a[0] = a[0][a[0].rfind('/')+1:]
        for i in range(len(a)):
            a[i] = a[i].strip()
        if a[0].startswith('createuser'):
            with open('pass.dat', 'a') as f:
                f.write(a[1] + ":" + a[2] + '\n')
            try:
                os.mkdir(a[1])
            except:
                pass
            self.authorizer.add_user(a[1], a[2], os.path.join(os.getcwd(), a[1]), perm='elradfmwM')
        elif a[0].startswith('changepassword'):
            temp = ""
            with open('pass.dat', 'r') as f:
                for line in f:
                    temp = temp + line
            with open('pass.dat', 'w') as f:
                temp2 = temp.split('\n')
                for line in temp2:
                    if line.split(':')[0] == a[1]:
                        f.write(a[1] + ':' + a[2] + '\n')
                    else:
                        f.write(line + '\n')
            self.authorizer.remove_user(a[1])
            self.authorizer.add_user(a[1], a[2], os.path.join(os.getcwd(), a[1]), perm='elradfmwM')
        elif a[0].startswith('removeuser'):
            # syntax is removeuser:username:True/False
            temp = ""
            with open('pass.dat', 'r') as f:
                for line in f:
                    temp = temp + line
            with open('pass.dat', 'w') as f:
                temp2 = temp.split('\n')
                for line in temp2:
                    if line.split(':')[0] == a[1]:
                        pass
                    else:
                        f.write(line + '\n')
            self.authorizer.remove_user(a[1])
            if bool(a[2]):
                os.rmdir(a[1])
        elif a[0].startswith('userinfo'):
            with open('root/userinfo.txt', 'w') as f:
                for user in self.authorizer.user_table.keys():
                    size = 0
                    numFiles = 0
                    numDirs = -1
                    info = os.walk(os.path.join(user, 'OneDir'))
                    for tup in info:
                        numDirs = numDirs + 1
                        for fil in tup[2]:
                            numFiles = numFiles + 1
                            size = size + os.path.getsize(os.path.join(tup[0], fil))
                    f.write(user + '\n')
                    if numDirs == -1: numDirs = 0
                    f.write('Number of Directories: ' + str(numDirs) + '\n')
                    f.write('Number of Files: ' + str(numFiles) + '\n')
                    f.write('Total File Size: ' + str(size) + '\n')
        self.respond('213 Done')
        return

def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    # anonymous user
    for line in open('pass.dat'):
        info = line.split(':')
        try:
            os.mkdir(os.path.join(os.getcwd(), info[0]))
        except:
            pass
        authorizer.add_user(info[0], info[1].strip(), os.path.join(os.getcwd(), info[0]), perm='elradfmwM')
    try:
        os.mkdir(os.path.join(os.getcwd(), 'root'))
    except:
        pass
    authorizer.add_user('root', 'password', os.path.join(os.getcwd()), perm='elradfmwM')
    # authorizer.remove_user('ben')
    # authorizer.add_user('ben', 'edgar', os.path.join(os.getcwd(), 'ben'), perm='elradfmwM')
    # authorizer.add_user('ben', 'lol', os.getcwd())
    # authorizer.add_anonymous(os.getcwd())

    # Instantiate FTP handler class
    handler = Handler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "OneDir Ready"

    # Specify a masquerade address and the range of ports to use for
    # passive connections.  Decomment in case you're behind a NAT.
    #handler.masquerade_address = '151.25.42.11'
    #handler.passive_ports = range(60000, 65535)

    # Instantiate FTP server class and listen on 0.0.0.0:2121
    address = ('localhost', 2121)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':
    main()
