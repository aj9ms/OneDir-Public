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
    def __init__(self):
        logging.basicConfig(filename='user.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    #on_modified doesn't get called unless we create a new file
    #useless because on_created gets called when creating new file anyway
    """def on_modified(self, event):
        source = event.src_path
        directorylist = source.split('/')
        last = directorylist[len(directorylist) - 1]
        if not last.startswith('.goutputstream'):
            logging.warning(event.src_path + ' modified')
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' modified'"""
    #creates both files and directories
    #for directories, the created directory will ALWAYS first be called "Untitled Folder"
    #renaming folders comes in on_moved
    def on_created(self, event):
        #creating directory
        if event.is_directory:
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
        #creating a file
        else:
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
    #moving files
    #renaming a directory
    #moving a directory
    def on_moved(self, event):
        source = event.src_path
        directorylist = source.split('/')
        last = directorylist[len(directorylist) - 1]
        dest = event.dest_path
        destlist = dest.split('/')
        #not a temp file but is still a file (file moving)
        if not last.startswith('.goutputstream') and not event.is_directory:
            #not a temp file but is still a file
            logging.warning(event.src_path + ' movedto ' + event.dest_path)
            print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
        #event is a directory (directory moving AND renaming)
        elif event.is_directory:
            sourcepath = source[0:source.find(directorylist[len(directorylist)-1])]
            destpath = dest[0:dest.find(destlist[len(destlist)-1])]
            #rename directory
            if sourcepath == destpath:
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' renamedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
                logging.warning(event.src_path + ' renamedto ' + event.dest_path)
            #move directory
            else:
                print source[source.find("/OneDir/", 0, len(source))+8:] + ' movedto ' + dest[dest.find("/OneDir/", 0, len(dest))+8:]
                logging.warning(event.src_path + ' movedto ' + event.dest_path)
    #deleting files and folders (when deleting a folder, it lists all files to delete as well)
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
