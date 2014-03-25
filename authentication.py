__author__ = 'ben'
import os

# username = raw_input("What is your user name?")
# password = raw_input("What is your password?")

home = os.path.expanduser("~")
if os.path.isdir(os.path.join(home, "OneDir")):
    print "It's a directory!"
    if os.path.exists(os.path.join(os.path.join(home, "OneDir"), ".info")):
        # login the user and update OneDir on the server
        print ".info file exists"
    else:
        # prompt the user for login or sign up
        print "no .info file exists"
else:
    print "Nope"


