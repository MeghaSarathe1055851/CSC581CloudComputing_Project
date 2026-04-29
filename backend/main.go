package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var client *mongo.Client
var recipeCollection *mongo.Collection

type Recipe struct {
	Name         string   `json:"name" bson:"name"`
	Ingredients  []string `json:"ingredients" bson:"ingredients"`
	Instructions string   `json:"instructions" bson:"instructions"`
}

func main() {

	mongoURI := os.Getenv("MONGO_URI")
	if mongoURI == "" {
		log.Fatal("MONGO_URI environment variable not set")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var err error
	client, err = mongo.Connect(ctx, options.Client().ApplyURI(mongoURI))
	if err != nil {
		log.Fatal("Mongo connection error:", err)
	}

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

	recipeCollection = client.Database("recipes").Collection("recipes")

	seedRecipes()

	http.HandleFunc("/", healthHandler)
	http.HandleFunc("/recipes/suggest", suggestHandler)

	fmt.Println("Server running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func seedRecipes() {

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	count, _ := recipeCollection.CountDocuments(ctx, bson.M{})
	if count > 0 {
		return
	}

	defaultRecipes := []interface{}{
		Recipe{
			Name: "Tomato Pasta",
			Ingredients: []string{"tomato", "pasta", "salt"},
			Instructions: "Boil pasta. Cook tomatoes with salt, herbs and basic spices. Mix together and serve.",
		},
		Recipe{
			Name: "Apple Pie",
			Ingredients: []string{"apple", "flour", "sugar"},
			Instructions: "Prepare crust. Fill with apple mixture. Bake at 180°C for 40 minutes.",
		},
		Recipe{
			Name: "Vanilla Cake",
			Ingredients: []string{"flour", "sugar", "vanilla"},
			Instructions: "Mix ingredients. Bake at 180°C for 30 minutes.",
		},
		Recipe{
			Name: "Dandan Noodles",
			Ingredients: []string{"noodles", "soy sauce", "chili"},
			Instructions: "Cook noodles. Prepare toasted sesame paste. Add soy sauce and chilli oil, Combine, tooped with scallions and serve hot.",
		},
	}

	recipeCollection.InsertMany(ctx, defaultRecipes)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Recipe Engine is running"))
}

func suggestHandler(w http.ResponseWriter, r *http.Request) {

	var input struct {
		Ingredients []string `json:"ingredients"`
	}

	err := json.NewDecoder(r.Body).Decode(&input)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	filter := bson.M{
		"ingredients": bson.M{
			"$all": input.Ingredients,
		},
	}

	var result Recipe
	err = recipeCollection.FindOne(ctx, filter).Decode(&result)
	if err != nil {
		http.Error(w, "No matching recipe found", http.StatusNotFound)
		return
	}

	json.NewEncoder(w).Encode(result)
}
