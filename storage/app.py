"""
Log Storage Service - Stores processed logs
This service receives processed logs and stores them in-memory and on disk
"""
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

# Storage configuration
STORAGE_DIR = os.environ.get('STORAGE_DIR', '/data/logs')
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)

# In-memory storage for quick retrieval
logs_memory = []

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'storage',
        'logs_count': len(logs_memory)
    }), 200

@app.route('/logs', methods=['POST'])
def store_log():
    """Store a processed log entry"""
    try:
        log_data = request.get_json()
        
        if not log_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Add storage metadata
        log_data['stored_at'] = datetime.utcnow().isoformat()
        
        # Store in memory
        logs_memory.append(log_data)
        
        # Persist to disk
        timestamp = log_data.get('timestamp', datetime.utcnow().isoformat())
        filename = f"{timestamp.replace(':', '-')}.json"
        filepath = os.path.join(STORAGE_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': 'Log stored successfully',
            'log_id': timestamp
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """Retrieve stored logs with optional filters"""
    try:
        # Query parameters
        level = request.args.get('level')
        service = request.args.get('service')
        limit = int(request.args.get('limit', 100))
        
        # Filter logs
        filtered_logs = logs_memory
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.get('level', '').upper() == level.upper()]
        
        if service:
            filtered_logs = [log for log in filtered_logs if log.get('service') == service]
        
        # Apply limit
        filtered_logs = filtered_logs[-limit:]
        
        return jsonify({
            'status': 'success',
            'count': len(filtered_logs),
            'logs': filtered_logs
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs/stats', methods=['GET'])
def get_stats():
    """Get statistics about stored logs"""
    try:
        total_logs = len(logs_memory)
        
        # Count by level
        level_counts = {}
        service_counts = {}
        priority_counts = {}
        
        for log in logs_memory:
            level = log.get('level', 'UNKNOWN')
            service = log.get('service', 'unknown')
            priority = log.get('priority', 'unknown')
            
            level_counts[level] = level_counts.get(level, 0) + 1
            service_counts[service] = service_counts.get(service, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return jsonify({
            'status': 'success',
            'total_logs': total_logs,
            'by_level': level_counts,
            'by_service': service_counts,
            'by_priority': priority_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs/clear', methods=['DELETE'])
def clear_logs():
    """Clear all stored logs (for testing/demo purposes)"""
    try:
        logs_memory.clear()
        return jsonify({
            'status': 'success',
            'message': 'All logs cleared from memory'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Log Storage Service...")
    print(f"Storage Directory: {STORAGE_DIR}")
    app.run(host='0.0.0.0', port=5002, debug=False)
