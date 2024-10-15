import time
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, api_url):
        self.api_url = api_url

    def on_modified(self, event):
        if not event.is_directory:
            log_message = f"File modified: {event.src_path}"
            print(log_message)
            self.send_log(log_message)

    def on_created(self, event):
        if not event.is_directory:
            log_message = f"File created: {event.src_path}"
            print(log_message)
            self.send_log(log_message)

    def on_deleted(self, event):
        if not event.is_directory:
            log_message = f"File deleted: {event.src_path}"
            print(log_message)
            self.send_log(log_message)

    def on_moved(self, event):
        if not event.is_directory:
            log_message = f"File moved from {event.src_path} to {event.dest_path}"
            print(log_message)
            self.send_log(log_message)

    def send_log(self, log_message):
        try:
            response = requests.post(self.api_url, json={"log": log_message})
            if response.status_code != 200:
                print(f"Failed to send log: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error sending log: {e}")

def monitor_directory(path_to_monitor, api_url):
    event_handler = FileChangeHandler(api_url)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_monitor, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    path_to_monitor = r'C:\Users\User\OneDrive\桌面\siem'  # Change this to your desired path
    api_url = "http://localhost:5000/logs"
    monitor_directory(path_to_monitor, api_url)
