"""
Log Processor Service - Processes logs from the message queue
This service consumes logs from RabbitMQ, processes them, and forwards to storage
"""
import os
import json
import time
from datetime import datetime
import pika
import requests

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_QUEUE = 'logs'

# Storage service configuration
STORAGE_HOST = os.environ.get('STORAGE_HOST', 'storage')
STORAGE_PORT = int(os.environ.get('STORAGE_PORT', 5002))

def get_rabbitmq_connection():
    """Establish connection to RabbitMQ with retry logic"""
    max_retries = 10
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

def process_log(log_data):
    """Process log data - add processing metadata"""
    processed_log = log_data.copy()
    processed_log['processed_at'] = datetime.utcnow().isoformat()
    processed_log['processor_id'] = 'processor-1'
    
    # Simulate processing - categorize by level
    level = processed_log.get('level', 'INFO').upper()
    if level in ['ERROR', 'CRITICAL']:
        processed_log['priority'] = 'high'
    elif level == 'WARNING':
        processed_log['priority'] = 'medium'
    else:
        processed_log['priority'] = 'low'
    
    return processed_log

def send_to_storage(log_data):
    """Send processed log to storage service"""
    try:
        storage_url = f"http://{STORAGE_HOST}:{STORAGE_PORT}/logs"
        response = requests.post(
            storage_url,
            json=log_data,
            timeout=5
        )
        return response.status_code == 201
    except Exception as e:
        print(f"Error sending to storage: {e}")
        return False

def callback(ch, method, properties, body):
    """Callback function for processing messages"""
    try:
        log_data = json.loads(body)
        print(f"Processing log: {log_data.get('message', 'No message')[:50]}...")
        
        # Process the log
        processed_log = process_log(log_data)
        
        # Send to storage
        if send_to_storage(processed_log):
            print(f"Log stored successfully: {processed_log['timestamp']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f"Failed to store log, requeuing...")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    """Main processor loop"""
    print("Starting Log Processor Service...")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    print(f"Storage Host: {STORAGE_HOST}:{STORAGE_PORT}")
    
    # Wait for storage service to be ready
    print("Waiting for storage service...")
    time.sleep(10)
    
    connection, channel = get_rabbitmq_connection()
    
    # Set QoS to process one message at a time
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback
    )
    
    print("Waiting for logs to process. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Processor shutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise
