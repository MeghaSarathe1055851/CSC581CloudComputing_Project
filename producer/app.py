"""
Log Producer Service - Generates and sends logs to the message queue
This service accepts log entries via REST API and publishes them to RabbitMQ
"""
import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
import pika

app = Flask(__name__)

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_QUEUE = 'logs'

def get_rabbitmq_connection():
    """Establish connection to RabbitMQ with retry logic"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            return connection, channel
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'producer'}), 200

@app.route('/logs', methods=['POST'])
def create_log():
    """Accept log entries and publish to message queue"""
    try:
        log_data = request.get_json()
        
        if not log_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Enrich log with metadata
        enriched_log = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': log_data.get('level', 'INFO'),
            'message': log_data.get('message', ''),
            'service': log_data.get('service', 'unknown'),
            'metadata': log_data.get('metadata', {})
        }
        
        # Publish to RabbitMQ
        connection, channel = get_rabbitmq_connection()
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(enriched_log),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Log queued for processing',
            'log_id': enriched_log['timestamp']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logs/batch', methods=['POST'])
def create_logs_batch():
    """Accept multiple log entries in batch"""
    try:
        logs_data = request.get_json()
        
        if not isinstance(logs_data, list):
            return jsonify({'error': 'Expected array of logs'}), 400
        
        connection, channel = get_rabbitmq_connection()
        processed_count = 0
        
        for log_data in logs_data:
            enriched_log = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': log_data.get('level', 'INFO'),
                'message': log_data.get('message', ''),
                'service': log_data.get('service', 'unknown'),
                'metadata': log_data.get('metadata', {})
            }
            
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(enriched_log),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            processed_count += 1
        
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': f'{processed_count} logs queued for processing'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Log Producer Service...")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    app.run(host='0.0.0.0', port=5000, debug=False)
