__author__ = 'ben'
from ftplib import FTP
import os
import sys

ftp = FTP('localhost')

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

def upload(ftp, file):
    # upload a file
    extension = os.path.splitext(file)[1]
    if extension in ('.txt', '.htm', '.html'):
        ftp.storlines('STOR ' + file, open(file))
    else:
        ftp.storbinary('STOR ' + file, open(file, 'rb'), 1024)








#write the pass.dat file to client side and then deletes it. Find a better way to do this
def userExists(ftp, username):
    filecontents = getFile(ftp, 'pass.dat', 'temp.txt')
    with open('temp.txt',"r") as tempfile:
        for line in tempfile:
            account = line.split(':')
            user = account[0]
            if user == username:
		#os.remove(os.path.join(os.getcwd(), 'temp.txt'))
                return True
    #os.remove(os.path.join(os.getcwd(), 'temp.txt'))
    return False

# need to open the file within the program -- don't write it to the client's filesystem
# send the pass.dat file back to the server
# login with the new user?
# Start watchdog after this function
def createUser(user, password):
    ftp.login('root', 'password')
    if not userExists(ftp, user):
        if not userDirectoryExists(ftp, user):
	    filecontents = getFile(ftp, 'pass.dat', 'temp.dat')
	    with open('temp.dat',"a") as accountfile:
                accountfile.write(user + ':' + password + '\n')
	    upload(ftp, 'temp.dat')
	    ftp.rename('temp.dat','pass.dat')
	    os.remove(os.path.join(os.getcwd(), 'temp.txt'))
            makeUserDirectory(ftp, user)
            ftp.close()
	    #logs in the new user
            #ftp.login(user, password)
        else:
            print "User directory already exists. Request ignored."
    else:
        print "Username already exists. Request ignored."
    ftp.close()

def userDirectoryExists(ftp, user):
    currentPath = ftp.pwd()
    newDir = os.path.join(currentPath, user)
    return os.path.isdir(newDir)

def makeUserDirectory(ftp, user):
    newDirectory = os.path.join(ftp.pwd(), user)
    print newDirectory
    ftp.mkd(newDirectory)

def run():
    # do a sample run, logging in to a local ftp server with my credentials
    createUser('alice', 'pass')
    #username = 'alice'
    #password = 'pass'
    #ftp.login(username, password)
    #upload(ftp,'ben.txt')
    #upload(ftp, 'pass.dat')

if __name__ == '__main__':
    run()
