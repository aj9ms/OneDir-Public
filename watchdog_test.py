import sys
import time
import logging
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from watchdog.observers import Observer
#Thread-safe event queue that skips adding same events consecutively.
#Has single queue_event() method
from watchdog.observers.api import EventQueue
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
import sync_test
import rsync

class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        names = []
        if event.src_path not in names:
	        names.append(event.src_path)
	#line below only used for testing; sync_test figures out which option it is and what to do.
	#figure out how to get the event's source path (ie, the file/folder that was modified) to be added
	#to a names list, which can then be used in sync_test
	print "something (file/folder) was modified/created/deleted!"
	print event.src_path
"""    def on_modified(self, event):
        print "file modified!"
    def on_created(self, event):
        print "file created!"
    def on_moved(self, event):
	print "file moved!"
    def on_any_event(self, event):
        if event.is_directory:
	     print "directory changed"
        print event.src_path"""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    # This event handler inherits from FileSystemEventHandler
    # Which has methods to implement like on_any_event(FileSystemEvent)
    # on_modified(event), on_moved(event), etc...
    # Check out this page -- https://pythonhosted.org/watchdog/api.html

    # Events have fields like -- event_type, is_directory, src_path,
    #event_handler = LoggingEventHandler()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    #not entirely sure how walker_callback works
    #snap = DirectorySnapshot(path, recursive=True, walker_callback=(lambda p, s: None))
    observer.start()
    try:
        while True:
            time.sleep(1)
            #would potentially be used to sync the files after the Observer object finds differences
            #sync_test.sync(sink, target, names)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
