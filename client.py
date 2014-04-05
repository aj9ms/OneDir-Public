__author__ = 'ben'
from ftplib import FTP
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

        logging.warning(event.src_path + ' modified')
    def on_created(self, event):
       """ if event.is_directory:
            print "directory created"
        else:
            print "file created!"""
       # if it's a file, just put it on the server

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
    #stringtest = "/OneDir/Test Folder/test.txt"
    #print stringtest[stringtest.find("OneDir", 0, len(stringtest))+6:]
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "stopping the observer"
        observer.stop()
    observer.join()


def getBinaryFile(ftp, filename, outfile=None):
    # get a binary file
    if outfile is None:
        outfile = sys.stdout
    ftp.retrbinary('RETR ' + filename, outfile.write)

def getTextFile(ftp, filename, outfile=None):
    # get a text file
    if outfile is None:
        outfile = sys.stdout
    else:
        outfile = open(outfile, 'w')
    ftp.retrlines('RETR ' + filename, lambda s, w = outfile.write: w(s + '\n'))

def upload(ftp, filePath, fileName):
    # upload a file
    if filePath != fileName:
        # ensures that the directory exists on the server
        print 'the file is in a subdirectory'
        # changes to that directory on the server

        # then upload the file
    extension = os.path.splitext(fileName)[1]
    if extension in ('.txt', '.htm', '.html'):
        ftp.storlines('STOR ' + fileName, open(filePath))
    else:
        ftp.storbinary('STOR ' + fileName, open(filePath, 'rb'), 1024)

def run():
    # do a sample run, logging in to a local ftp server with my credentials
    # ftp = FTP('localhost')
    ftp.login('ben', 'edgar')
    directory = 'OneDir'
    watchDogThread = Thread(target=watchTheDog, args=(directory,))
    watchDogThread.start()
    print "IT STARTEDD"

    getTextFile(ftp, 'ben.txt', 'ben.txt')

if __name__ == '__main__':
    run()
