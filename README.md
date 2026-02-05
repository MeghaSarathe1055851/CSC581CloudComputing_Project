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




