package model

import (
	"context"
	"errors"
	"github.com/xusheng6/crackmes.one/app/shared/database"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"time"
)

// *****************************************************************************
// User
// *****************************************************************************

// User table contains the information for each user
type User struct {
	ObjectId    primitive.ObjectID `bson:"_id,omitempty"`
	HexId       string             `bson:"hexid,omitempty"`
	Name        string             `bson:"name,omitempty"`
	Email       string             `bson:"email,omitempty"`
	Password    string             `bson:"password,omitempty"`
	Visible     bool               `bson:"visible"`
	Deleted     bool               `bson:"deleted"`
	NbCrackmes  int
	NbSolutions int
	NbComments  int
}

// Username returns the user name
func (u *User) Username() string {
	return u.Name
}

func CountUsers() (int, error) {
	var err error
	var nb int64
	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")
		nb, err = collection.CountDocuments(database.Ctx, bson.D{})
	} else {
		err = ErrUnavailable
	}

	return int(nb), standardizeError(err)
}

// UserByEmail gets user information from email
func UserByName(name string) (User, error) {
	var err error

	result := User{}

	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")
		err = collection.FindOne(database.Ctx, bson.M{"name": primitive.Regex{Pattern: "^" + name + "$", Options: "i"}}).Decode(&result)
	} else {
		err = ErrUnavailable
	}

	return result, standardizeError(err)
}

func UserByMail(email string) (User, error) {
	var err error

	result := User{}

	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")
		err = collection.FindOne(database.Ctx, bson.M{"email": primitive.Regex{Pattern: "^" + email + "$", Options: "i"}}).Decode(&result)
	} else {
		err = ErrUnavailable
	}

	return result, standardizeError(err)
}

func UserByHexId(hexid string) (User, error) {
	var err error

	result := User{}

	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")

		err = collection.FindOne(database.Ctx, bson.M{"hexid": hexid}).Decode(&result)
	} else {
		err = ErrUnavailable
	}

	return result, standardizeError(err)
}

func AllUsersVisible() ([]User, error) {
	var result []User
	var err error
	var cursor *mongo.Cursor

	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")

		// Validate the object id
		cursor, err = collection.Find(database.Ctx, bson.M{"visible": true})
		err = cursor.All(database.Ctx, &result)
	} else {
		err = ErrUnavailable
	}
	return result, err
}

// UserCreate creates user
func UserCreate(name, email, password string) error {
	var err error

	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")

		objId := primitive.NewObjectID()
		user := &User{
			ObjectId: objId,
			HexId:    objId.Hex(),
			Name:     name,
			Email:    email,
			Password: password,
			Visible:  true,
			Deleted:  false,
		}
		_, err = collection.InsertOne(database.Ctx, user)
	} else {
		err = ErrUnavailable
	}

	return standardizeError(err)
}

// UpdateUserPassword updates the password for a user identified by their username.
// It finds the user by their username and updates the password field.
func UpdateUserPassword(username string, hashedPassword string) error {
	// Validate inputs
	if username == "" {
		return errors.New("username cannot be empty")
	}
	if hashedPassword == "" {
		return errors.New("hashed password cannot be empty")
	}

	// Create a context with timeout for the query
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Get the users collection
	collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("user")

	// Create the filter by matching the username
	filter := bson.M{"name": username}

	// Define the update operation
	update := bson.M{
		"$set": bson.M{
			"password": hashedPassword,
		},
	}

	// Perform the update
	result, err := collection.UpdateOne(ctx, filter, update)
	if err != nil {
		return err
	}

	// Check if any document was updated
	if result.MatchedCount == 0 {
		return errors.New("no user found with the provided username")
	}

	return nil
}
