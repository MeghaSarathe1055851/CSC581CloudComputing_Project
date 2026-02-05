#!/usr/bin/env python3
"""
Test script for the Event-Driven Cloud Logging Platform
This script demonstrates the system by submitting logs and querying them
"""
import requests
import time
import json
from datetime import datetime

# Service endpoints
PRODUCER_URL = "http://localhost:5000"
STORAGE_URL = "http://localhost:5002"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_health():
    """Check health of services"""
    print_section("Health Check")
    
    services = [
        ("Producer", f"{PRODUCER_URL}/health"),
        ("Storage", f"{STORAGE_URL}/health")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {name} service is healthy")
                print(f"  Response: {response.json()}")
            else:
                print(f"✗ {name} service returned status {response.status_code}")
        except Exception as e:
            print(f"✗ {name} service is not accessible: {e}")
    
    return True

def submit_single_log():
    """Submit a single log entry"""
    print_section("Submitting Single Log")
    
    log_data = {
        "level": "INFO",
        "message": "User authentication successful",
        "service": "auth-service",
        "metadata": {
            "user_id": "usr_12345",
            "ip_address": "192.168.1.100"
        }
    }
    
    try:
        response = requests.post(
            f"{PRODUCER_URL}/logs",
            json=log_data,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def submit_batch_logs():
    """Submit multiple log entries"""
    print_section("Submitting Batch Logs")
    
    logs = [
        {
            "level": "ERROR",
            "message": "Database connection timeout",
            "service": "database-service",
            "metadata": {"retry_count": 3}
        },
        {
            "level": "WARNING",
            "message": "Memory usage above 80%",
            "service": "monitoring-service",
            "metadata": {"memory_percent": 85}
        },
        {
            "level": "INFO",
            "message": "API request processed successfully",
            "service": "api-gateway",
            "metadata": {"endpoint": "/api/users", "response_time_ms": 45}
        },
        {
            "level": "DEBUG",
            "message": "Cache hit for user profile",
            "service": "cache-service",
            "metadata": {"cache_key": "user:12345"}
        },
        {
            "level": "CRITICAL",
            "message": "Security breach attempt detected",
            "service": "security-service",
            "metadata": {"source_ip": "10.0.0.5", "attack_type": "sql_injection"}
        }
    ]
    
    try:
        response = requests.post(
            f"{PRODUCER_URL}/logs/batch",
            json=logs,
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def query_logs(level=None, service=None, limit=10):
    """Query stored logs"""
    print_section(f"Querying Logs (level={level}, service={service}, limit={limit})")
    
    params = {"limit": limit}
    if level:
        params["level"] = level
    if service:
        params["service"] = service
    
    try:
        response = requests.get(
            f"{STORAGE_URL}/logs",
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['count']} logs")
            
            for i, log in enumerate(data['logs'], 1):
                print(f"\nLog {i}:")
                print(f"  Time: {log.get('timestamp')}")
                print(f"  Level: {log.get('level')}")
                print(f"  Service: {log.get('service')}")
                print(f"  Priority: {log.get('priority')}")
                print(f"  Message: {log.get('message')}")
                if log.get('metadata'):
                    print(f"  Metadata: {log.get('metadata')}")
            
            return True
        else:
            print(f"Error: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_statistics():
    """Get log statistics"""
    print_section("Log Statistics")
    
    try:
        response = requests.get(f"{STORAGE_URL}/logs/stats", timeout=5)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"Total Logs: {stats['total_logs']}")
            print(f"\nBy Level:")
            for level, count in stats['by_level'].items():
                print(f"  {level}: {count}")
            print(f"\nBy Service:")
            for service, count in stats['by_service'].items():
                print(f"  {service}: {count}")
            print(f"\nBy Priority:")
            for priority, count in stats['by_priority'].items():
                print(f"  {priority}: {count}")
            
            return True
        else:
            print(f"Error: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test workflow"""
    print("\n" + "="*60)
    print("  Event-Driven Cloud Logging Platform - System Test")
    print("="*60)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if services are running
    if not check_health():
        print("\n⚠ Services are not healthy. Please start the system with:")
        print("  docker-compose up")
        return
    
    # Submit logs
    print("\nSubmitting logs to the system...")
    submit_single_log()
    time.sleep(1)
    submit_batch_logs()
    
    # Wait for processing
    print("\n⏳ Waiting for logs to be processed...")
    time.sleep(5)
    
    # Query logs
    query_logs()
    
    time.sleep(1)
    query_logs(level="ERROR")
    
    time.sleep(1)
    get_statistics()
    
    print_section("Test Completed Successfully")
    print("✓ All operations completed successfully!")
    print("\nNext steps:")
    print("  - View RabbitMQ dashboard: http://localhost:15672 (guest/guest)")
    print("  - Query logs: curl http://localhost:5002/logs")
    print("  - Submit more logs: curl -X POST http://localhost:5000/logs -H 'Content-Type: application/json' -d '{...}'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
