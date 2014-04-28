import os
import socket
import smtplib
from shutil import rmtree
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer, MultiprocessFTPServer

#Handles all commands from the client side
class Handler(FTPHandler):
    def ftp_STAT(self, line):
        a = line.split(":")
        a[0] = a[0][a[0].rfind('/')+1:]
        for i in range(len(a)):
            a[i] = a[i].strip()
        #Creates a user on the server
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
        #Change a local user's password on the server
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
        #Remove a user from the server and the DummyAuthorizer table
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
        #Admin functionality: prints out the information about all users
        #including number of directories and files and total file size
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
        #Admin functionality: prints out all users saved on the server
        elif a[0].startswith('users'):
            with open('root/users.txt', 'w') as f:
                f.write('Users: \n')
                for user in self.authorizer.user_table.keys():
                    if user == 'root':
                        continue
                    f.write(user + '\n')
        #Allows changepassword when local user forgets password
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
        #Admin functionality: shows a "traffic report log" for all users based on watchdog events
        elif a[0].startswith('seelogs'):
            with open('root/userlogs.txt', 'w') as f:
                for user in self.authorizer.user_table.keys():
                    if os.path.isdir(os.path.join(user, 'OneDir')):
                        with open(os.path.join(os.path.join(user, 'OneDir'), '.user.log'), 'r') as f2:
                            f.write(user + ':\n')
                            for line in f2:
                                f.write(line)
        self.respond('213 Done')
        return

#Runs the server
def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Creates a pass.dat file if it does not exist
    # Creates a root/admin user's folder and gives it full r/w permissions
    try:
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
    except:
        f = open('pass.dat', 'w')
        f.close()
    authorizer.add_user('root', 'd63dc919e201d7bc4c825630d2cf25fdc93d4b2f0d46706d29038d01', os.path.join(os.getcwd()), perm='elradfmwM')

    # Instantiate FTP handler class
    handler = Handler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "OneDir Ready"

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
