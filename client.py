__author__ = 'ben'
from ftplib import FTP
from ftplib import all_errors
import os
import sys
import time
import logging
from threading import Thread
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

ftp = FTP('localhost')

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        logging.basicConfig(filename='user.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    #on_modified doesn't get called unless we create a new file
    #useless because on_created gets called when creating new file anyway
    """def on_modified(self, event):
        source = event.src_path
        directorylist = source.split('/')
        last = directorylist[len(directorylist) - 1]
        if not last.startswith('.goutputstream'):
            logging.warning(event.src_path + ' modified')
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' modified'"""
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
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' director created'
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
        if source_tilde == "~":
            logging.warning(source[0:len(source)-1] + ' deleted')
            print source[source.find("/OneDir/", 0, len(source))+8:len(source)-1] + ' deleted'
        else:
            logging.warning(event.src_path + ' deleted')
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' deleted'

def watchTheDog(directory):
    event_handler = MyHandler()
    logging.warning('watchdog started')
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "stopping the observer"
        observer.stop()
    observer.join()

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


def syncOneDir(ftp, folder):
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
            syncOneDir(ftp, fil)
        else:
            syncOneDir(ftp, fil)
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

def run():
    watchDogThread = Thread(target=watchTheDog, args=('OneDir',))
    while True:
        command = raw_input('Enter a command (login, change password, create user): ')
        if command == 'login':
            username = raw_input('Username: ')
            password = raw_input('Password: ')
            ftp.login(username, password)
            syncOneDir(ftp, 'OneDir')
            watchDogThread.start()
            break
        elif command == 'change password':
            # do something to change the password
            pass
        elif command == 'create user':
            # append to the pass.dat file probably
            pass
    # filelist = ftp.nlst('OneDir')
    # ftp.cwd('OneDir')
    # ftp.voidcmd('TYPE I')
    # for fil in filelist:
    #     print fil
    #     if is_file(ftp, fil):
    #         print fil + " on server: " + str(ftp.size(fil))
    # for fil in os.listdir('OneDir'):
    #     print fil + " on client: " + str(os.path.getsize(os.path.join('OneDir', fil)))

    # do a sample run, logging in to a local ftp server with my credentials
    # ftp = FTP('localhost')

    # ftp.login('ben', 'edgar')
    # getFile(ftp, 'OneDir/ben111/test1234.txt', 'OneDir/ben111/test1234.txt')
    # printos.chdir(folder) is_file(ftp, '/OneDir/ben111/test1234.txt')
    # getFile(ftp, 'OneDir/ben111/test1234.txt', 'newFile.txt')
    # upload(ftp, 'OneDir/test1234.txt', 'test1234.txt')
    # upload(ftp, 'OneDir/test.py', 'test.py')
    # upload(ftp, 'OneDir/test.py', 'test.py')
    # deleteDir(ftp, 'OneDir')

    # rename(ftp, 'OneDir/ben111/', 'OneDir/ben44/')
    # createDirectory(ftp, '/OneDir/ben44/anotheranotheranother')
if __name__ == '__main__':
    run()
