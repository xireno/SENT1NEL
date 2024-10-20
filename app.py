from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from usb_monitor import get_drives_info, monitor_usb  # Import USB monitoring
from detection import monitor_directory  # Import directory monitoring logic
import threading
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for Electron

logs = []  # Store all received logs

@app.route('/')
def index():
    """Serve the index page."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page."""
    return render_template('dashboard.html')

@app.route('/monitoring')
def monitoring():
    """Serve the monitoring page."""
    return render_template('monitoring.html')

@app.route('/logs', methods=['GET', 'POST'])
def log_event():
    """Handle log retrieval and log submission."""
    if request.method == 'POST':
        log_data = request.json
        if log_data and isinstance(log_data.get('logs'), list):
            for log in log_data['logs']:
                # Avoid duplicate logs by checking if the log already exists
                if log not in logs:
                    logs.append(log)  # Append only unique logs
                    print(f"Received log: {log}")
            return jsonify({"status": "success", "message": "Logs received"}), 200
        return jsonify({"status": "error", "message": "Invalid log data"}), 400

    elif request.method == 'GET':
        return jsonify({"logs": logs}), 200

@app.route('/drives', methods=['GET'])
def drives():
    """Fetch and return information about connected drives."""
    try:
        return jsonify(get_drives_info()), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def start_monitoring():
    """Start both USB and directory monitoring in separate threads."""
    # Start USB monitoring in a background thread
    threading.Thread(target=monitor_usb, daemon=True).start()

    # Start directory monitoring in a background thread
    user_home = os.path.expanduser("~")
    desktop_path = os.path.join(user_home, "OneDrive", "桌面", "siem")
    api_url = "http://localhost:5000/logs"
    threading.Thread(target=monitor_directory, args=(desktop_path, api_url), daemon=True).start()

if __name__ == '__main__':
    print("Starting Flask server...")
    start_monitoring()  # Start monitoring tasks in background threads
    app.run(port=5000, debug=True)
