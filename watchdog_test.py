import sys
import time
import logging
from watchdog.events import LoggingEventHandler, FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
#Thread-safe event queue that skips adding same events consecutively.
#Has single queue_event() method
from watchdog.observers.api import EventQueue
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

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

def walker_callback(path, stat_info, self=None):
    return

#class SnapshotMonitor():
#    def scan(self):        

if __name__ == "__main__":
#    logging.basicConfig(level=logging.INFO,
#                        format='%(asctime)s - %(message)s',
#                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyHandler()
    logging.warning('watchdog started')
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    #stringtest = "/OneDir/Test Folder/test.txt"
    #print stringtest[stringtest.find("OneDir", 0, len(stringtest))+6:]
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
