# Builder Stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o recipe-engine

# Runtime Stage
FROM alpine:3.20

WORKDIR /app
COPY --from=builder /app/recipe-engine .

EXPOSE 8080

CMD ["./recipe-engine"]
