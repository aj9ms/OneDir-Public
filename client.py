__author__ = 'ben'
from ftplib import FTP
from ftplib import all_errors
import os
import sys
import time
from getpass import getpass
import logging
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

ftp = FTP()
class MyHandler(FileSystemEventHandler):
    # need to have ftp.login(username, password) in here too so that class knows what login credentials are
    def __init__(self, ftp):
        logging.basicConfig(filename='OneDir/.user.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
        self.ftp = ftp
    #creates both files and directories
    #for directories, the created directory will ALWAYS first be called "Untitled Folder"
    #renaming folders comes in on_moved
    def on_created(self, event):
        #creating directory
        if event.is_directory:
            source = event.src_path
            source_tilde = source[len(source)-1]
            directorylist = source.split('/')
            last = directorylist[len(directorylist) - 1]
            if not last.startswith('.goutputstream'):
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' created'
                createDirectory(self.ftp, source[source.find("/OneDir/", 0, len(source))+8:])
        #creating a file
        else:
            source = event.src_path
            source_tilde = source[len(source)-1]
            directorylist = source.split('/')
            last = directorylist[len(directorylist) - 1]
            if last.endswith('~') and not last.startswith('.goutputstream'):
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:len(source)-1] + ' file created'
                upload (self.ftp, source[source.find("/OneDir/", 0, len(source))+8:len(source)-1])
            if not last.startswith('.goutputstream'):
                if '___jb_' in last:
                    time.sleep(0.2)
                    source = source[:source.find('___jb')]
                    print source
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' file created'
                upload(self.ftp, source[source.find("/OneDir/", 0, len(source))+8:])
    #moving files
    #renaming a directory
    #moving a directory
    def on_moved(self, event):
        try:
            source = event.src_path
            if source is None:
                d = event.dest_path
                logging.warning(event.dest_path + ' created')
                print d[d.find("/OneDir/", 0, len(d))+8:] + ' file created'
                upload(self.ftp, d[d.find("/OneDir/", 0, len(d))+8:])
            else:
                directorylist = source.split('/')
                last = directorylist[len(directorylist) - 1]
                dest = event.dest_path
                destlist = dest.split('/')
            #not a temp file but is still a file (file moving)
                if not last.startswith('.goutputstream') and '___jb_' not in last and '___jb_' not in dest:
                #not a temp file but is still a file
                    logging.warning(event.src_path + ' movedto ' + event.dest_path)
                    print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
                    rename(self.ftp, source[source.find("/OneDir/", 0, len(source))+8:], dest[dest.find("/OneDir/", 0, len(dest))+8:])
            #event is a directory (directory moving AND renaming)
            # elif event.is_directory:
            #         print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
            #         logging.warning(event.src_path + ' movedto ' + event.dest_path)
        except all_errors:
            pass
    #deleting files and folders (when deleting a folder, it lists all files to delete as well)
    def on_deleted(self, event):
        source = event.src_path
        source_tilde = source[len(source)-1]
        # if source_tilde == "~":
        #     logging.warning(source[0:len(source)-1] + ' deleted')
        #     print source[source.find("/OneDir/", 0, len(source))+8:len(source)-1] + ' deleted'
        #
        # else:
        logging.warning(event.src_path + ' deleted')
        print source[source.find("/OneDir/", 0, len(source))+8:] + ' deleted'
        if event.is_directory:
            deleteDir(self.ftp, source[source.find("/OneDir/", 0, len(source))+8:])
        else:
            deleteFile(self.ftp, source[source.find("/OneDir/", 0, len(source))+8:])

# DEPRECATED, USE getFile instead
# def getBinaryFile(ftp, filename, outfile=None):
#     # get a binary file
#     if outfile is None:
#         outfile = sys.stdout
#     ftp.retrbinary('RETR ' + filename, outfile.write)
#
# def getTextFile(ftp, filename, outfile=None):
#     # get a text file
#     if outfile is None:
#         outfile = sys.stdout
#     else:
#         outfile = open(outfile, 'w')
#     ftp.retrlines('RETR ' + filename, lambda s, w = outfile.write: w(s + '\n'))

def getFile(ftp, filePath, outfile=None):
    # get any kind of file, the file path should be from whatever the current directory is
    if outfile is None:
        outfile = sys.stdout
    else:
        outfile = open(outfile, 'w')
    extension = os.path.splitext(filePath)[1]
    # if extension in ('.txt', '.htm', '.html'):
    #     ftp.retrlines('RETR ' + filePath, lambda s, w = outfile.write: w(s) + '\n')
    # else:
    ftp.retrbinary('RETR ' + filePath, outfile.write)

def deleteFile(ftp, filePath):
    # delete a file on the server
    ftp.delete(filePath)

def is_file(ftp, filename):
    # check to see if a file is a file or a directory
    current = ftp.pwd()
    try:
        ftp.cwd(filename)
    except all_errors:
        ftp.cwd(current)
        return True
    ftp.cwd(current)
    return False

def deleteDir(ftp, direc):
    # delete a directory on the server and everything inside of it
    # REALLY weird error -- ftp.nlst() wasn't working on a directory called "ben111", but when I renamed
    # it everything worked... maybe something to ask about
    if len(ftp.nlst(direc)) == 0:
        ftp.rmd(direc)
    else:
        curr = ftp.pwd()
        print direc
        print os.path.abspath(curr)
        filelist = ftp.nlst(direc)
        print filelist
        ftp.cwd(direc)
        for fil in filelist:
            if is_file(ftp, fil):
                deleteFile(ftp, fil)
            else:
                deleteDir(ftp, fil)
        ftp.cwd(curr)
        ftp.rmd(direc)

def rename(ftp, fromname, toname):
    ftp.rename(fromname, toname)

def createDirectory(ftp, direc):
    ftp.mkd(direc)

def uploadAll(ftp, folder):
    # you pass in a folder and it uploads everything in that folder to the ftp server recursively
    try:
        ftp.mkd(folder)
    except all_errors:
        pass
    curr = ftp.pwd()
    filelist = os.listdir(folder)
    ftp.cwd(folder)
    curr2 = os.getcwd()
    os.chdir(folder)
    for fil in filelist:
        if os.path.isfile(fil):
            upload(ftp, fil)
        elif os.path.isdir(fil):
            uploadAll(ftp, fil)
    ftp.cwd(curr)
    os.chdir(curr2)

def syncOneDirClient(ftp, folder):
    curr_ftp = ftp.pwd()
    curr_cli = os.getcwd()
    filelist = os.listdir(folder)
    ftp_filelist = ftp.nlst(folder)
    ftp.cwd(folder)
    os.chdir(folder)
    # putting server in binary mode
    # ftp.voidcmd('binary')
    for fil in ftp_filelist:
        if is_file(ftp, fil):
            if fil in filelist:
                ftp.voidcmd('TYPE I')
                if os.path.getsize(fil) != ftp.size(fil):
                    # deleteFile(ftp, fil)
                    upload(ftp, fil)
            else:
                getFile(ftp, fil, os.path.join(curr_cli, os.path.join(folder, fil)))
        elif fil not in filelist:
            os.mkdir(fil)
            syncOneDirClient(ftp, fil)
        else:
            syncOneDirClient(ftp, fil)
    for fil in filelist:
        if fil not in ftp_filelist:
            upload(ftp, fil)
    # ftp.voidcmd('ascii')
    ftp.cwd(curr_ftp)
    os.chdir(curr_cli)

def syncOneDirServer(ftp, folder):
    curr_ftp = ftp.pwd()
    curr_cli = os.getcwd()
    filelist = os.listdir(folder)
    ftp_filelist = ftp.nlst(folder)
    ftp.cwd(folder)
    os.chdir(folder)
    # putting server in binary mode
    # ftp.voidcmd('binary')
    for fil in ftp_filelist:
        if is_file(ftp, fil):
            if fil in filelist:
                ftp.voidcmd('TYPE I')
                if os.path.getsize(fil) != ftp.size(fil):
                    getFile(ftp, fil, os.path.join(curr_cli, os.path.join(folder, fil)))
            else:
                getFile(ftp, fil, os.path.join(curr_cli, os.path.join(folder, fil)))
        elif fil not in filelist:
            os.mkdir(fil)
            syncOneDirServer(ftp, fil)
        else:
            syncOneDirServer(ftp, fil)
    for fil in filelist:
        if fil not in ftp_filelist:
            upload(ftp, fil)
    # ftp.voidcmd('ascii')
    ftp.cwd(curr_ftp)
    os.chdir(curr_cli)



def upload(ftp, filePath):
    # upload a file @param ftp -- the ftp connection to use
    #               @param filePath -- the file path of the file to be uploaded
    if os.path.isdir(filePath):
        uploadAll(ftp, filePath)
        return
    if '/' in filePath:
        fileName = filePath[filePath.rfind('/')+1:]
        current = ftp.pwd()
        folders = filePath.split('/')
        try:
            for x in range(0, len(folders) - 1):
                if folders[x] in ftp.nlst(ftp.pwd()):
                    ftp.cwd(folders[x])
                else:
                    ftp.mkd(folders[x])
                    ftp.cwd(folders[x])
        except all_errors:
            direc = filePath[0:filePath.rfind('/')]
            ftp.cwd(current)
            ftp.cwd(direc)
        extension = os.path.splitext(fileName)[1]
        if extension in ('.txt', '.htm', '.html'):
            ftp.storlines('STOR ' + fileName, open(filePath))
        else:
            ftp.storbinary('STOR ' + fileName, open(filePath, 'rb'), 1024)
        ftp.cwd(current)
    else:
        extension = os.path.splitext(filePath)[1]
        if extension in ('.txt', '.htm', '.html'):
            ftp.storlines('STOR ' + filePath, open(filePath))
        else:
            ftp.storbinary('STOR ' + filePath, open(filePath, 'rb'), 1024)

def run(ftp):
    server = raw_input('What is the IP Address of the server? ')
    try:
        port = int(raw_input('What is the port number to connect to? '))
    except ValueError:
        print "The port must be an integer ... quitting"
        os._exit(0)
    try:
        ftp.connect(server, port)
    except all_errors:
        print "Give a valid server and port number"
        os._exit(0)
    while True:
        command = raw_input('\nEnter a command (login, change password, create user, admin, quit): ')
        if command == 'login':
            username = raw_input('Username: ')
            password = getpass()
            try:
                ftp.login(username, password)
                event_handler = MyHandler(ftp)
                logging.warning('watchdog started')
                observer = Observer()
                observer.schedule(event_handler, 'OneDir', recursive=True)
                try:
                    syncOneDirServer(ftp, 'OneDir')
                except all_errors as e:
                    if str(e) == '550 No such file or directory.':
                        ftp.mkd('OneDir')
                        syncOneDirServer(ftp, 'OneDir')
                time.sleep(1)
                observer.start()
                #watchDogThread.start()
                break
            except all_errors as e:
                print "FTP error: " + str(e)
                # print "Login failed, try again."
        elif command == 'change password':
            # do something to change the password
            username = raw_input('Enter the user: ')
            print "Enter the current password"
            password1 = getpass()
            print "Enter the new password"
            password2 = getpass()
            ftp.login('root', 'password')
            try:
                ftp.sendcmd('STAT ' + 'changepassword:' + username + ':' + password2 + ':' + password1)
                if int(ftp.lastresp) == 215:
                    print "User does not exist"
            except:
                pass
        elif command == 'create user':
            # append to the pass.dat file probably
            ftp.login('root', 'password')
            username = raw_input("Enter the new username: ")
            password = getpass()
            password2 = getpass()
            if password != password2:
                print "Passwords do not match, please try again"
                continue
            try:
                ftp.sendcmd('STAT ' + "createuser:" + username + ":" + password)
                if int(ftp.lastresp) == 214:
                    print "User Already Exists, try again"
            except all_errors:
                pass
        elif command == 'admin':
            username = raw_input('\nPlease login as an admin\nUsername: ')
            password = getpass()
            if username=='root' and password=='password':
                ftp.login('root', 'password')
                while True:
                    command = raw_input('Enter a valid admin command (remove user, change password, get info, get users, see logs, go back): ')
                    if command == 'go back':
                        break
                    if command == 'get info':
                        try:
                            ftp.sendcmd('STAT ' + "userinfo")
                        except all_errors:
                            pass
                        getFile(ftp, 'root/userinfo.txt', 'userinfo.txt')
                        with open('userinfo.txt', 'r') as f:
                            for line in f:
                                print line,
                    if command == 'get users':
                        try:
                            ftp.sendcmd('STAT ' + "users")
                        except all_errors:
                            pass
                        getFile(ftp, 'root/users.txt', 'users.txt')
                        with open('users.txt', 'r') as f:
                            for line in f:
                                print line,
                    if command == 'see logs':
			try:
			    ftp.sendcmd('STAT ' + "seelogs")
			except all_errors:
			    pass
                        getFile(ftp, 'root/userlogs.txt', 'userlogs.txt')
                        with open('userlogs.txt', 'r') as f:
                            for line in f:
                                print line,
                    if command == 'remove user':
                        user = raw_input('Which user do you want to remove? ')
                        cond = raw_input('Do you want to delete their files? ')
                        if cond.startswith('Y') or cond.startswith('y'):
                            try:
                                ftp.sendcmd('STAT ' + "removeuser:" + user + ':True')
                            except all_errors:
                                pass
                        else:
                            try:
                                ftp.sendcmd('STAT ' + "removeuser:" + user + ':False')
                            except all_errors:
                                pass
                    if command == 'change password':
                        user = raw_input('Whose password do you want to change? ')
                        print "Type in their new password"
                        password = getpass()
                        try:
                            ftp.sendcmd('STAT ' + "changepassword:" + user + ':' + password)
                        except all_errors:
                            pass
        elif command == 'quit':
            os._exit(0)
    try:
        print "If you want to pause syncing type ctrl-C"
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        # print "stopping the observer"
        print "\nSynchronization is turned off."
        print "Note: Answering the following means you are done editing files.  Even if you are not exiting, you will be logged out, and your current files will be automatically synced to the server."
        resp = raw_input("\nDo you want to exit? (yes/no)")
        syncOneDirClient(ftp, 'OneDir')
        ftp.quit()
        ftp2 = FTP()
        ftp2.connect(server, port)
        observer.join()
        if resp.startswith('y') or resp.startswith('Y'):
            os._exit(0)
        else:
            run(ftp2)

if __name__ == '__main__':
    run(ftp)
