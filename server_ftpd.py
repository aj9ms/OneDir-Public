import os
import socket
import smtplib
from shutil import rmtree
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
            with open('pass.dat', 'r') as f:
                for line in f:
                    line2 = line.split(':')
                    if a[1] == line2[0]:
                        self.respond('214 user already exists')
                        return
            with open('pass.dat', 'a') as f:
                f.write(a[1] + ":" + a[2] + ':' + a[3] + '\n')
            try:
                os.mkdir(a[1])
            except:
                pass
            self.authorizer.add_user(a[1], a[2], os.path.join(os.getcwd(), a[1]), perm='elradfmwM')
        elif a[0].startswith('verify'):
            temp = ""
            #with open('pass.dat', 'r') as f:
                #for line in f:        
        elif a[0].startswith('changepassword'):
            temp = ""
            b = False
            if len(a) == 3:
                a.append(":")
            with open('pass.dat', 'r') as f:
                for line in f:
                    line2 = line.split(':')
                    if a[1] == line2[0] and a[3] == line2[1]:
                        b = True
                    temp = temp + line
            if not b:
                self.respond('215 user does not exist')
                return
            with open('pass.dat', 'w') as f:
                temp2 = temp.split('\n')
                for line in temp2:
                    v = line.split(':')
                    if len(v) == 2:
                        if line.split(':')[0] == a[1]:
                            f.write(a[1] + ':' + a[2] + '\n')
                        else:
                            f.write(line + '\n')
                    else:
                        if line.split(':')[0] == a[1]:
                            f.write(a[1] + ':' + a[2] + ':' + v[2] + '\n')
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
            if a[2] == 'True':
                rmtree(a[1])
        elif a[0].startswith('userinfo'):
            with open('root/userinfo.txt', 'w') as f:
                totSize = 0
                for user in self.authorizer.user_table.keys():
                    if user == 'root':
                        continue
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
                    f.write('Total File Size (bytes): ' + str(size) + '\n')
                    totSize = totSize + size
                f.write('Total Storage Used (bytes): ' + str(totSize) + '\n')
        elif a[0].startswith('users'):
            with open('root/users.txt', 'w') as f:
                f.write('Users: \n')
                for user in self.authorizer.user_table.keys():
                    if user == 'root':
                        continue
                    f.write(user + '\n')
        elif a[0].startswith('forgot'):
            b = False
            temp = ""
            with open('pass.dat', 'r') as f:
                for line in f:
                    if a[1] == line.split(':')[0].strip():
                        a2 = line.split(':')
                        if len(a2) > 2:
                            if a2[2].strip() == a[3]:
                                b = True
                    else:
                        temp = temp + line
            if not b:
                self.respond('216 something went wrong')
                return
            else:
                with open('pass.dat', 'w') as f:
                    f.write(a[1] + ':' + a[2] + ':' + a[3] + '\n')
                    temp2 = temp.split('\n')
                    for line in temp2:
                        f.write(line + '\n')
                self.authorizer.remove_user(a[1])
                self.authorizer.add_user(a[1], a[2], os.path.join(os.getcwd(), a[1]), perm='elradfmwM')
        self.respond('213 Done')
        return

def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions and a read-only
    # anonymous user
    for line in open('pass.dat'):
        info = line.split(':')
        if len(info) < 2:
            continue
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
    # authorizer.remove_user('alice')
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ip = str(s.getsockname()[0])
    s.close()
    address = (ip, 2121)
    server = FTPServer(address, handler)

    # set a limit for connections
    server.max_cons = 256
    server.max_cons_per_ip = 5

    # start ftp server
    server.serve_forever()


if __name__ == '__main__':
    main()
