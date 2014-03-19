# A simple program that uses watchdog to monitor directories specified as
# command-line arguments and logs events generated
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    # This event handler inherits from FileSystemEventHandler
    #   Which has methods to implement like on_any_event(FileSystemEvent)
    #   on_modified(event), on_moved(event), etc...
    #   Check out this page -- https://pythonhosted.org/watchdog/api.html

    # Events have fields like -- event_type, is_directory, src_path,
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()