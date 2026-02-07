# Build stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum first (good caching)
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN go build -o recipe-api ./main.go

# Final stage - minimal image
FROM alpine:3.20

WORKDIR /app

# Copy the compiled binary from builder
COPY --from=builder /app/recipe-api .

# Run as non-root user (good practice, even for Deliverable 1)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Expose port
EXPOSE 8080

# Run the app
CMD ["./recipe-api"]
