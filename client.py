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
    def on_modified(self, event):
        """if event.is_directory:
            print "directory modified"
        else:
            print "file modified!"""
        print "this is being modified " + event.src_path
        # if not event.is_directory:
        #     print 'uploading ' + event.src_path
        #     upload(ftp, event.src_path[event.src_path.rfind('OneDir'):])
        logging.warning(event.src_path + ' modified')
    def on_created(self, event):
       """ if event.is_directory:
            print "directory created"
        else:
            print "file created!"""
       # if it's a file, just put it on the server
       # if not event.is_directory:
       #      upload(ftp, event.src_path)

       # if it's a directory, create the directory on the server
       logging.warning(event.src_path + ' created')
    def on_moved(self, event):
        """if event.is_directory:
            print "directory moved"
        else:
            print "file moved!"""
        logging.warning(event.src_path + ' moved')
    def on_deleted(self, event):
        """if event.is_directory:
            print "directory deleted"
        else:
            print "file deleted"""
        logging.warning(event.src_path + ' deleted')
    def on_any_event(self, event):
        source = event.src_path
        #directory = source.split("/")
        print source[source.find("/OneDir/", 0, len(source))+8:]

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
        ftp.retrlines('RETR ' + filePath, lambda s, w = outfile.write: w(s + '\n'))
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
    if len(ftp.nlst(direc)) == 0:
        ftp.rmd(direc)
    else:
        curr = ftp.pwd()
        filelist = ftp.nlst(direc)
        ftp.cwd(direc)
        for fil in filelist:
            if is_file(ftp, fil):
                deleteFile(ftp, fil)
            else:
                deleteDir(ftp, fil)
        ftp.cwd(curr)
        ftp.rmd(direc)

def upload(ftp, filePath):
    # upload a file @param ftp -- the ftp connection to use
    #               @param filePath -- the file path of the file to be uploaded
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
    # do a sample run, logging in to a local ftp server with my credentials
    # ftp = FTP('localhost')
    ftp.login('ben', 'edgar')
    directory = 'OneDir'
    watchDogThread = Thread(target=watchTheDog, args=(directory,))
    # watchDogThread.start()

    # print is_file(ftp, '/OneDir/Test_Folder/test.txt')
    # getFile(ftp, 'OneDir/Test_Folder/test.txt', 'newFile.txt')
    # upload(ftp, 'OneDir/test.txt', 'test.txt')
    # upload(ftp, 'OneDir/test.py', 'test.py')
    # upload(ftp, 'OneDir/test.py', 'test.py')
    # deleteDir(ftp, 'OneDir/ben2')

if __name__ == '__main__':
    run()
