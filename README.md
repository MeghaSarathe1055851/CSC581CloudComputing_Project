# CSC581 – Cloud Computing Project  
# Personalized Recipe Suggestion Engine

## Overview

The Personalized Recipe Suggestion Engine is a containerized microservice-based application designed to suggest recipes based on user-provided ingredients. The system is implemented using the Go programming language for the backend API and MongoDB for persistent storage. Docker and Docker Compose are used to containerize and orchestrate the services, enabling consistent deployment both locally and on CloudLab.

The project demonstrates key cloud computing concepts including service isolation, container networking, environment-based configuration, multi-stage builds, and database-backed microservice communication.

---

## System Architecture

The application follows a two-tier microservice architecture composed of:
- A backend API service implemented in Go.
- A MongoDB database service for structured recipe storage.

The backend exposes REST endpoints that accept ingredient lists and return matching recipes. The MongoDB service stores recipe documents containing fields such as name, ingredients, and cooking instructions. The backend communicates with MongoDB using the official MongoDB Go driver over TCP via Docker’s internal bridge network.

When deployed using Docker Compose, both containers are attached to an isolated virtual network. Docker provides built-in DNS-based service discovery, allowing the backend container to reference MongoDB using the service hostname `db`. This eliminates the need for hard-coded IP addresses and mirrors real-world cloud-native deployments.

The architecture intentionally separates compute (API logic) from storage (database), reflecting best practices in distributed systems and modern cloud platforms.



### Architecture Diagram
![Architecture Diagram](docs/architecture.png)

*(Click the image to view full size.)*

---

## Containerization Strategy

The backend service is containerized using a custom Dockerfile located in the backend/ directory. The Dockerfile uses a multi-stage build process to optimize image size and improve security.

The build stage uses the `golang:1.22-alpine` base image, which includes the full Go toolchain within a lightweight Alpine Linux distribution. Dependencies are downloaded using Go modules, and the application is compiled into a standalone binary.

The runtime stage uses a minimal Alpine image. Only the compiled binary is copied into this final stage, significantly reducing the attack surface and overall container size. This approach reflects industry-standard container hardening practices.

MongoDB is deployed using the official `mongo:7.0` image, which is widely adopted in production systems and actively maintained by MongoDB.

## Networking Model

Docker Compose automatically creates a dedicated bridge network when the application is started. Both the API and MongoDB services are attached to this network.

Within this environment:

- The backend connects to MongoDB using the hostname `db`.
- Communication occurs over port 27017 inside the private network.
- `Port 8080` is published to the host machine to allow external HTTP access.
- `Port 27017` may optionally be exposed for development and debugging purposes.

This setup simulates real cloud networking principles where services communicate internally within a private network while selectively exposing only required endpoints.

## Application Workflow

When the system starts, the backend attempts to establish a connection to MongoDB using an environment variable `(MONGO_URI)`. A retry mechanism ensures the database is available before serving traffic.

If the recipe collection is empty, the system automatically seeds default recipes such as Tomato Pasta, Apple Pie, Vanilla Cake, and Dandan Noodles. This guarantees deterministic behavior during demonstrations.

When a client sends a `POST /recipes/suggest` request containing a list of ingredients, the backend constructs a MongoDB query using the `$all` operator. This ensures that only recipes containing all provided ingredients are returned. The matching recipe document, including its cooking instructions, is serialized as JSON and sent back to the client.

This interaction demonstrates real database querying rather than static response generation, strengthening the system’s academic value


## Build Process

The backend container is built using Docker’s layered image system. Dependency files are copied first to leverage layer caching, improving rebuild performance. The Go compiler produces a static binary which is then executed as the container’s entry point.

The use of a multi-stage build reduces the final image size while maintaining a clean separation between build-time and runtime environments. This design aligns with production-grade container practices.

## Deployment on CloudLab

The application is fully compatible with CloudLab environments. Deployment requires:
- Installing Docker on the CloudLab node.
- Cloning the repository.
- Running `docker-compose up --build`.

Docker Compose handles network creation, container startup order, and health checks. Once deployed, the system can be validated using standard HTTP requests via `curl`.

This deployment approach ensures portability and reproducibility across different infrastructure environments.

## Design Considerations

The system was designed with the following cloud computing principles in mind:

Service isolation through containerization
Stateless API logic with externalized state
Environment-based configuration
Lightweight and optimized container images
Internal service discovery using DNS
Production-style database querying

The separation of application logic and persistent storage makes the architecture extensible and adaptable to orchestration platforms such as Kubernetes.

## Conclusion

This project demonstrates a fully containerized microservice architecture deployed using Docker Compose and validated on CloudLab. It integrates real-time database querying with RESTful API design while adhering to cloud-native best practices.

The Personalized Recipe Suggestion Engine reflects foundational distributed systems concepts including container networking, service discovery, environment-based configuration, and infrastructure portability. The final system is production-structured, academically rigorous, and aligned with modern cloud computing standards.

