from flask import Flask, jsonify
import os
import math

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'healthy',
        'pod': os.environ.get('HOSTNAME', 'unknown'),
        'message': 'URL Shortener Autoscaler Demo'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/cpu')
def cpu_intensive():
    # Simulates CPU load for autoscaler to react to
    result = sum(math.sqrt(i) for i in range(1, 100000))
    return jsonify({
        'status': 'computed',
        'result': result,
        'pod': os.environ.get('HOSTNAME', 'unknown')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)