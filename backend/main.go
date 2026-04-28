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

	// MongoDB connection string
	mongoURI := "mongodb://mongodb:27017"

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var err error
	client, err = mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Mongo connection error:", err)
	}

	err = client.Ping(ctx, nil)
	if err != nil {
		log.Fatal("Mongo ping failed:", err)
	}

	fmt.Println("Connected to MongoDB successfully!")

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
