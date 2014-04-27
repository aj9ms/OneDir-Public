from binascii import hexlify
from getpass import getpass
from sys import stdin

from simplecrypt import encrypt, decrypt

from cryptography.fernet import Fernet

from Crypto.Cipher import AES

from passlib.hash import sha256_crypt

def simplecrypt():
    #don't understand the point of the username here
    username = raw_input("username: ")
    password = getpass("password: ")
    ciphertext = encrypt(username, password.encode('utf8'))
    print "ciphertext: %s" % hexlify(ciphertext)
    plaintext = decrypt(username, ciphertext)
    print "plaintext: %s" % plaintext
    print "plaintext as string: %s" % plaintext.decode('utf8')

def cryptography():
    #a new key is generated each time, so that means this probably doesn't work if we ever turn server off and then on again
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt("password")
    print token
    untoken = f.decrypt(token)
    print untoken
    message = getpass("password: ")
    while message != "quit":
        t = f.encrypt(message)
        print t
        u = f.decrypt(t)
        print u
        message = getpass("password: ")

def pycrypto():
    #this one is weird and doesn't seem to work very well
    message = getpass("password: ")
    while message != "quit":
        obj = AES.new('this is a key123', AES.MODE_CBC, 'this is an iv456')
        ciph = obj.encrypt(message)
        print ciph
        obj2 = AES.new('this is a key123', AES.MODE_CBC, 'this is an iv456')
        unciph = obj2.decrypt(ciph)
        print unciph
        message = getpass("password: ")

def passlib():
    #this seems to work best
    message = getpass("password: ")
    while message != "quit":
        hashing = sha256_crypt.encrypt(message)
        print hashing
        m2 = getpass("password verification: ")
        print sha256_crypt.verify(m2, hashing)
        print sha256_crypt.verify("dummypassword", hashing)
        message = getpass("password: ")

if __name__ == '__main__':
    #simplecrypt()
    #cryptography()
    #pycrypto()
    passlib()
