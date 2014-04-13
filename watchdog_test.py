import sys
import time
import logging
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
from watchdog.observers import Observer
#Thread-safe event queue that skips adding same events consecutively.
#Has single queue_event() method
from watchdog.observers.api import EventQueue
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

class MyHandler(FileSystemEventHandler):
#class MyHandler(PatternMatchingEventHandler):
    #def __init__(self, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        #saves all changes made in user.log
        #super(MyHandler, self).__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)
    def __init__(self):
        logging.basicConfig(filename='user.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    def on_modified(self, event):
        source = event.src_path
        directorylist = source.split('/')
        last = directorylist[len(directorylist) - 1]
        if not last.startswith('.goutputstream'):
            logging.warning(event.src_path + ' modified')
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' modified'
    def on_created(self, event):
        source = event.src_path
        source_tilde = source[len(source)-1]
        directorylist = source.split('/')
        last = directorylist[len(directorylist) - 1]
        if not last.startswith('.goutputstream'):
            if source_tilde == "~":
                logging.warning(source[0:len(source)-1] + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:len(source)-1] + ' created'
            else:
                logging.warning(event.src_path + ' created')
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' created'
    def on_moved(self, event):
        source = event.src_path
        directorylist = source.split('/')
        last = directorylist[len(directorylist) - 1]
        dest = event.dest_path
        destlist = dest.split('/')
        if not last.startswith('.goutputstream') and not event.is_directory:
            #not a temp file and not a directory
            logging.warning(event.src_path + ' movedto ' + event.dest_path)
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
        elif event.is_directory:
            #event is directory (so can't be temp file)
            sourcepath = source[0:source.find(directorylist[len(directorylist)-1])]
            destpath = dest[0:dest.find(destlist[len(destlist)-1])]
            if sourcepath == destpath:
                #rename
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' renamedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
                logging.warning(event.src_path + ' renamedto ' + event.dest_path)
            else:
                #moved directory
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
                logging.warning(event.src_path + ' movedto ' + event.dest_path)
    def on_deleted(self, event):
        source = event.src_path
        source_tilde = source[len(source)-1]
        if source_tilde == "~":
            logging.warning(source[0:len(source)-1] + ' deleted')
            print source[source.find("/OneDir/", 0, len(source))+8:len(source)-1] + ' deleted'
        else:
            logging.warning(event.src_path + ' deleted')
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' deleted'
if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyHandler()
    logging.warning('watchdog started')
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
