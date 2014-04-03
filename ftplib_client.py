__author__ = 'ben'
from ftplib import FTP
import os
import sys

def getBinaryFile(ftp, filename, outfile=None):
    # get a binary file
    if outfile is None:
        outfile = sys.stdout
    ftp.retrbinary('RETR ' + filename, outfile.write)

def getTextFile(ftp, filename, outfile=None):
    # get a text file
    if outfile is None:
        outfile = sys.stdout
    ftp.retrlines('RETR ' + filename, lambda s, w = outfile.write: w(s + '\n'))

def upload(ftp, file):
    # upload a file
    extension = os.path.splitext(file)[1]
    if extension in ('.txt', '.htm', '.html'):
        ftp.storlines('STOR ' + file, open(file))
    else:
        ftp.storbinary('STOR ' + file, open(file, 'rb'), 1024)

def run():
    # do a sample run, logging in to a local ftp server with my credentials
    ftp = FTP('localhost')
    ftp.login('ben', 'edgar')
    getTextFile(ftp, 'ben.txt')

if __name__ == '__main__':
    run()

