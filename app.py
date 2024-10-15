from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')
@app.route('/logs', methods=['POST'])
def log_event():
    log_data = request.json
    if log_data and 'log' in log_data:
        print(f"Received log: {log_data['log']}")
        return jsonify({"status": "success", "message": "Log received"}), 200
    return jsonify({"status": "error", "message": "Invalid log data"}), 400

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=5000, debug=True)
