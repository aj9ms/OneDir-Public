import rsync
from rsync import Cookie

#def sync():
def sync(sink, target, names):
    cookie = Cookie()
    cookie.sink_root = sink
    cookie.target_root = target
    dirname = target
    #names of files to update
    name = ["test.txt", "test.py"]
    rsync.visit(cookie, dirname, name)

if __name__ == "__main__":
    names = []
    sync("SyncWithOneDir", "OneDir", names)
