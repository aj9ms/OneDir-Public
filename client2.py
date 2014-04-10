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








# need to get pass.dat file from the server first
def userExists(username):
    with open('pass.dat',"r") as file:
        for line in file:
            account = line.split(':')
            user = account[0]
            if user == username:
                return True
    return False

# need to get pass.dat file from the server
# need to open the file within the program -- don't write it to the client's filesystem
# add a line to the pass.dat file if the user doesn't exist already
# send the pass.dat file back to the server
# login with the new user?
# Start watchdog after this function
def createUser(user, password):
    ftp = FTP('localhost')
    ftp.login()
    if not userExists(user):
        if not userDirectoryExists(user):
            with open("pass.dat", "a") as accountfile:
                accountfile.write(user + ':' + password + '\n')
            ftp.close()
            ftp = FTP('localhost')
            ftp.login(user, password)
            makeUserDirectory(ftp, user)
        else:
            print "User directory already exists. Request ignored."
    else:
        print "Username already exists. Request ignored."
    ftp.close()

def userDirectoryExists(user):
    newDir = os.path.join(os.getcwd(), user)
    return os.path.isdir(newDir)

def makeUserDirectory(ftp, user):
    newDirectory = os.path.join(os.getcwd(), user)
    ftp.mkd(newDirectory)

def run():
    # do a sample run, logging in to a local ftp server with my credentials
    createUser('alice', 'pass')
    ftp = FTP('localhost')
    username = 'ann'
    password = 'pass'
    ftp.login(username, password)
    upload(ftp,'ben.txt')
    upload(ftp, 'pass.dat')

if __name__ == '__main__':
    run()