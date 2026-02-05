# CSC581CloudComputing_Project

This project implements an event-driven cloud logging platform designed to demonstrate infrastructure-focused cloud deployment using containerization. The system consists of decoupled services that communicate asynchronously over a network, simulating how modern distributed systems collect and process application logs at scale.

## Architecture

The system consists of three main services communicating asynchronously through RabbitMQ:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Client    │────▶│   Producer   │────▶│  RabbitMQ   │────▶│  Processor   │
│             │     │   Service    │     │    Queue    │     │   Service    │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                         :5000                                        │
                                                                      ▼
                                                               ┌──────────────┐
                                                               │   Storage    │
                                                               │   Service    │
                                                               └──────────────┘
                                                                    :5002
```

### Services

1. **Producer Service** (Port 5000)
   - REST API that accepts log entries
   - Publishes logs to RabbitMQ message queue
   - Supports single and batch log submission

2. **Processor Service**
   - Consumes logs from RabbitMQ asynchronously
   - Processes and enriches log data
   - Categorizes logs by priority
   - Forwards processed logs to storage service

3. **Storage Service** (Port 5002)
   - Receives processed logs from processor
   - Stores logs in memory and persists to disk
   - Provides query API for retrieving logs
   - Generates statistics about stored logs

4. **RabbitMQ** (Ports 5672, 15672)
   - Message broker for asynchronous communication
   - Ensures reliable message delivery
   - Management UI available at http://localhost:15672

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/MeghaSarathe1055851/CSC581CloudComputing_Project.git
cd CSC581CloudComputing_Project
```

2. Build and start all services:
```bash
docker-compose up --build
```

3. Wait for all services to be healthy (approximately 30 seconds)

## Usage

### Submit a Log Entry

```bash
curl -X POST http://localhost:5000/logs \
  -H "Content-Type: application/json" \
  -d '{
    "level": "INFO",
    "message": "User logged in successfully",
    "service": "auth-service",
    "metadata": {"user_id": "12345"}
  }'
```

### Submit Multiple Logs

```bash
curl -X POST http://localhost:5000/logs/batch \
  -H "Content-Type: application/json" \
  -d '[
    {
      "level": "ERROR",
      "message": "Database connection failed",
      "service": "db-service"
    },
    {
      "level": "WARNING",
      "message": "High memory usage detected",
      "service": "monitoring"
    }
  ]'
```

### Query Stored Logs

```bash
# Get all logs
curl http://localhost:5002/logs

# Get logs by level
curl http://localhost:5002/logs?level=ERROR

# Get logs by service
curl http://localhost:5002/logs?service=auth-service

# Get limited number of logs
curl http://localhost:5002/logs?limit=10
```

### View Log Statistics

```bash
curl http://localhost:5002/logs/stats
```

### Health Checks

```bash
# Producer service
curl http://localhost:5000/health

# Storage service
curl http://localhost:5002/health
```

## Testing

A test script is provided to demonstrate the system:

```bash
python test_system.py
```

This script will:
1. Submit various log entries
2. Wait for processing
3. Query and display stored logs
4. Show statistics

## Monitoring

- **RabbitMQ Management UI**: http://localhost:15672
  - Username: `guest`
  - Password: `guest`

## System Features

### Event-Driven Architecture
- Services communicate asynchronously through message queues
- Decoupled architecture allows independent scaling
- Resilient to temporary service failures

### Containerization
- Each service runs in its own Docker container
- Easy deployment and scaling
- Consistent environment across development and production

### Distributed Processing
- Logs flow through multiple services
- Processing pipeline can be extended with new services
- Load can be distributed across multiple processor instances

### Persistence
- Logs stored both in-memory and on disk
- Volume mounting ensures data survives container restarts
- Easy backup and recovery

## Development

### Project Structure
```
.
├── producer/
│   ├── app.py           # Producer service code
│   ├── requirements.txt
│   └── Dockerfile
├── processor/
│   ├── app.py           # Processor service code
│   ├── requirements.txt
│   └── Dockerfile
├── storage/
│   ├── app.py           # Storage service code
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml   # Service orchestration
└── test_system.py       # System test script
```

### Stopping Services

```bash
docker-compose down
```

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs producer
docker-compose logs processor
docker-compose logs storage
```

### Rebuilding Services

```bash
docker-compose up --build
```

## Scaling

The processor service can be scaled to handle higher load:

```bash
docker-compose up --scale processor=3
```

## Clean Up

To remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

## Technologies Used

- **Python 3.11**: Service implementation
- **Flask**: REST API framework
- **RabbitMQ**: Message broker
- **Pika**: RabbitMQ Python client
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## License

This project is part of CSC581 Cloud Computing coursework.
