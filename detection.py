import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# List of file extensions to monitor
monitored_extensions = ['.txt', '.exe', '.py', '.bat', '.vbs']

# Dictionary to track recently deleted files (for detecting moves)
recently_deleted_files = {}

class MonitorHandler(FileSystemEventHandler):
    # Only log files with specific extensions
    def should_log(self, src_path):
        _, ext = os.path.splitext(src_path)
        return ext in monitored_extensions

    # Track file creation and detect possible moves
    def on_created(self, event):
        if not event.is_directory and self.should_log(event.src_path):
            filename = os.path.basename(event.src_path)

            # Check if the file was recently deleted (possible move)
            if filename in recently_deleted_files:
                time_since_deleted = time.time() - recently_deleted_files[filename]['timestamp']
                if time_since_deleted < 5:
                    original_path = recently_deleted_files[filename]['path']
                    print(f"Moved file: from {original_path} to {event.src_path}")
                    del recently_deleted_files[filename]
                    return

            print(f"Created file: {event.src_path}")

    # Track file deletions
    def on_deleted(self, event):
        if not event.is_directory and self.should_log(event.src_path):
            filename = os.path.basename(event.src_path)
            recently_deleted_files[filename] = {
                'path': event.src_path,
                'timestamp': time.time()
            }
            print(f"Deleted file: {event.src_path}")

    # Track file movements
    def on_moved(self, event):
        if not event.is_directory and self.should_log(event.dest_path):
            print(f"Moved file: from {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detection.py <folder_path>")
        sys.exit(1)

    path_to_watch = sys.argv[1]

    if not os.path.exists(path_to_watch):
        print(f"Error: The path {path_to_watch} does not exist.")
        sys.exit(1)

    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)

    try:
        observer.start()
        print(f"Monitoring started on {path_to_watch}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Monitoring stopped")

    observer.join()
