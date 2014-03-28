import rsync
from rsync import Cookie

def sync():
    cookie = Cookie()
    cookie.sink_root = "OneDir-ToSync"
    cookie.target_root = "OneDir"
    dirname = "OneDir"
    #names of files to update
    names = ["test.txt", "test2.txt", "test3.txt"]
    rsync.visit(cookie, dirname, names)


if __name__ == "__main__":
    sync()
