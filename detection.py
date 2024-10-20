import os
import time
import hashlib
import threading
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, api_url, batch_interval=1.0):
        self.api_url = api_url
        self.log_batch = []  # Store logs temporarily for batching
        self.pending_moves = {}  # Track potential moves (deleted -> created)
        self.processed_events = set()  # Track unique events to avoid duplicates
        self.batch_interval = batch_interval  # Interval for sending logs
        self.session = self.get_session_with_retries()  # Session with retries
        self.start_batch_sender()  # Start background batch sender

    def get_session_with_retries(self, retries=3, backoff_factor=0.5):
        """Create a session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def generate_event_key(self, event, action):
        """Generate a unique key for each event."""
        return f"{event.src_path}_{action}"

    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            # Store deleted file with timestamp to detect moves
            self.pending_moves[event.src_path] = time.time()
            print(f"Pending move registered for: {event.src_path}")
            # Delay processing the deletion to check for potential moves
            threading.Timer(0.5, self.process_delete, [event]).start()

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            # Check if the file was recently deleted (indicating a move)
            for deleted_path, timestamp in list(self.pending_moves.items()):
                if time.time() - timestamp < 1.0:
                    # Log as a move instead of separate delete and create
                    self.add_log(deleted_path, f"moved to '{event.src_path}'")
                    del self.pending_moves[deleted_path]
                    return  # Don't log as a separate create event

            # If not part of a move, log as a regular creation event
            event_key = self.generate_event_key(event, "created")
            if event_key not in self.processed_events:
                self.processed_events.add(event_key)
                self.add_log(event.src_path, "created")

    def process_delete(self, event):
        """Log deletion if no corresponding move occurs."""
        if event.src_path in self.pending_moves:
            del self.pending_moves[event.src_path]  # Remove from pending moves
            event_key = self.generate_event_key(event, "deleted")
            if event_key not in self.processed_events:
                self.processed_events.add(event_key)
                self.add_log(event.src_path, "deleted")

    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            # Log the move directly if detected as a move event
            self.add_log(event.src_path, f"moved to '{event.dest_path}'")

    def add_log(self, file_path, action):
        """Add a structured log entry to the batch."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        log_entry = {"timestamp": timestamp, "file": file_path, "action": action}
        print(f"Log added: {log_entry}")
        self.log_batch.append(log_entry)

    def start_batch_sender(self):
        """Start a background thread to send logs in batches."""
        threading.Thread(target=self.send_logs_batch, daemon=True).start()

    def send_logs_batch(self):
        """Periodically send logs to the API in batches."""
        while True:
            time.sleep(self.batch_interval)
            if self.log_batch:
                logs_to_send = self.log_batch[:]
                self.log_batch.clear()
                self.send_logs(logs_to_send)

    def send_logs(self, logs):
        """Send logs via POST request."""
        try:
            payload = {"logs": logs}
            response = self.session.post(self.api_url, json=payload)
            if response.status_code == 200:
                print(f"Successfully sent {len(logs)} logs")
            else:
                print(f"Failed to send logs: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending logs: {e}")

def monitor_directory(path_to_monitor, api_url):
    """Monitor the specified directory."""
    if not os.path.exists(path_to_monitor):
        print(f"Error: Path '{path_to_monitor}' does not exist.")
        return

    event_handler = FileChangeHandler(api_url)
    observer = Observer()
    observer.schedule(event_handler, path=path_to_monitor, recursive=True)
    observer.start()

    print(f"Monitoring started on: {path_to_monitor}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
    finally:
        if event_handler.log_batch:
            print("Sending remaining logs before exiting...")
            event_handler.send_logs(event_handler.log_batch)
        observer.stop()
        observer.join()
