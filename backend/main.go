package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var client *mongo.Client

func main() {

	// Read Mongo URI from environment
	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("MONGO_URI environment variable not set")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var err error

	// Connect to MongoDB
	client, err = mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Mongo connection error:", err)
	}

	// Retry ping up to 5 times (handles container startup race condition)
	for i := 1; i <= 5; i++ {
		err = client.Ping(ctx, nil)
		if err == nil {
			fmt.Println("Connected to MongoDB successfully!")
			break
		}

		fmt.Println("Waiting for MongoDB to be ready... attempt", i)
		time.Sleep(3 * time.Second)
	}

	if err != nil {
		log.Fatal("Mongo ping failed after retries:", err)
	}

	// HTTP Routes
	http.HandleFunc("/", healthHandler)
	http.HandleFunc("/recipes/suggest", suggestHandler)

	port := "8080"
	fmt.Println("Server running on port", port)

	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Recipe Engine is running"))
}

func suggestHandler(w http.ResponseWriter, r *http.Request) {
	response := map[string]string{
		"recipe": "Tomato Pasta",
	}
	json.NewEncoder(w).Encode(response)
}
