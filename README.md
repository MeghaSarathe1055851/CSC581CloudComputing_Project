# CSC581 – Cloud Computing Project  
## Event-Driven Cloud Logging Platform

This project implements an event-driven cloud logging platform designed to demonstrate infrastructure-focused cloud deployment using containerization. The emphasis of this project is on system architecture, container orchestration, and infrastructure-as-code concepts rather than complex application logic.

## Vision

The goal of this project is to build a distributed logging system where multiple services communicate asynchronously using containerized infrastructure. The system is composed of decoupled components to reflect real-world cloud deployments that prioritize scalability, fault tolerance, and service isolation.

### Architecture Overview

+-------------+        TCP / Message Queue       +--------------+
|  Producer   |  ------------------------------> |  Consumer    |
| (Log Source)|                                  | (Processor)  |
+-------------+                                  +--------------+


- The **Producer** service simulates applications generating log events.
- The **Consumer** service receives and processes these log events.
- Communication between components occurs over a TCP-based messaging mechanism, allowing loose coupling between services.

This architecture mirrors event-driven systems commonly used in cloud environments for logging, monitoring, and data processing.

## Proposal

The system will be implemented using Docker containers and orchestrated via `docker-compose` to deploy multiple services in isolated environments.

### Planned Base Images

- **Producer Service:** `python:3.11-slim`  
- **Consumer Service:** `python:3.11-slim`  
- **Message Broker (planned):** Official Redis image  

These lightweight base images are chosen to minimize container size while maintaining compatibility with CloudLab environments. At least one custom Dockerfile will be used to build application services, satisfying course requirements.

## Project Status

This repository is structured to be CloudLab-ready and serves as the foundation for future enhancements, including CI/CD automation, container security hardening, and registry-based deployments.



