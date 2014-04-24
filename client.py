__author__ = 'ben'
from ftplib import FTP
from ftplib import all_errors
import os
import sys
import time
import logging
import threading
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

ftp = FTP()
ftp.connect('localhost', 2121)
class MyHandler(FileSystemEventHandler):
    # need to have ftp.login(username, password) in here too so that class knows what login credentials are
    def __init__(self):
    #def __init(self, user, pw):
        logging.basicConfig(filename='user.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    #on_modified doesn't get called unless we create a new file
    #useless because on_created gets called when creating new file anyway
    """def on_modified(self, event):
        if event.is_directory:
            source = event.src_path
            source_tilde = source[len(source)-1]
            directorylist = source.split('/')
            last = directorylist[len(directorylist) - 1]
            if not last.startswith('.goutputstream'):
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' directory created'
                createDirectory(ftp, source[source.find("/OneDir/", 0, len(source))+8:])
        #creating a file
        else:
            source = event.src_path
            source_tilde = source[len(source)-1]
            directorylist = source.split('/')
            last = directorylist[len(directorylist) - 1]
            if not last.startswith('.goutputstream'):
                if '___jb_' in last:
                    time.sleep(0.2)
                    source = source[:source.find('___jb')]
                    print source
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' file created'
                upload(ftp, source[source.find("/OneDir/", 0, len(source))+8:])"""
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
                createDirectory(ftp, source[source.find("/OneDir/", 0, len(source))+8:])
        #creating a file
        else:
            source = event.src_path
            source_tilde = source[len(source)-1]
            directorylist = source.split('/')
            last = directorylist[len(directorylist) - 1]
            if last.endswith('~') and not last.startswith('.goutputstream'):
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:len(source)-1] + ' file created'
                upload (ftp, source[source.find("/OneDir/", 0, len(source))+8:len(source)-1])
            if not last.startswith('.goutputstream'):
                if '___jb_' in last:
                    time.sleep(0.2)
                    source = source[:source.find('___jb')]
                    print source
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' file created'
                upload(ftp, source[source.find("/OneDir/", 0, len(source))+8:])
    #moving files
    #renaming a directory
    #moving a directory
    def on_moved(self, event):
        try:
            source = event.src_path
            directorylist = source.split('/')
            last = directorylist[len(directorylist) - 1]
            dest = event.dest_path
            destlist = dest.split('/')
            #not a temp file but is still a file (file moving)
            if not last.startswith('.goutputstream') and '___jb_' not in last and '___jb_' not in dest:
                #not a temp file but is still a file
                logging.warning(event.src_path + ' movedto ' + event.dest_path)
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
                rename(ftp, source[source.find("/OneDir/", 0, len(source))+8:], dest[dest.find("/OneDir/", 0, len(dest))+8:])
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
            deleteDir(ftp, source[source.find("/OneDir/", 0, len(source))+8:])
        else:
            deleteFile(ftp, source[source.find("/OneDir/", 0, len(source))+8:])

#Integrated into run() instead
#Observer now stops when it's supposed to,
#so auto-synchronization on/off actually works
"""def watchTheDog(directory):
    #event_handler = MyHandler(user, pw)
    event_handler = MyHandler()
    logging.warning('watchdog started')
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()"""

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
    if extension in ('.txt', '.htm', '.html'):
        ftp.retrlines('RETR ' + filePath, lambda s, w = outfile.write: w(s))
    else:
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
    # do a sample run, logging in to a local ftp server with my credentials
    # ftp = FTP('localhost')
    #ftp.login('ben', 'edgar')
    event_handler = MyHandler()
    logging.warning('watchdog started')
    observer = Observer()
    observer.schedule(event_handler, 'OneDir', recursive=True)
    #watchDogThread = threading.Thread(target=watchTheDog, args=('OneDir',))
    #watchDogThread.start()
    #uploadAll(ftp, 'OneDir')
    #deleteDir(ftp, 'OneDir') 
    while True:
        command = raw_input('Enter a command (login, change password, create user, quit): ')
        if command == 'login':
            username = raw_input('Username: ')
            password = raw_input('Password: ')
            try:
                ftp.login(username, password)
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
            pass
        elif command == 'create user':
            # append to the pass.dat file probably
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
        ftp2.connect('localhost', 2121)
        observer.join()
        if resp.startswith('y') or resp.startswith('Y'):
            os._exit(0)
        else:
            run(ftp2)

if __name__ == '__main__':
    run(ftp)
