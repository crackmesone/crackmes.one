package model

import (
	"time"

	"github.com/crackmesone/crackmes.one/app/shared/database"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

// *****************************************************************************
// Comment
// *****************************************************************************

// Comment table contains the information for each comment
type Comment struct {
	ObjectId     primitive.ObjectID `bson:"_id,omitempty"`
	Content      string             `bson:"info,omitempty"`
	Author       string             `bson:"author,omitempty"`
	CrackMeHexId string             `bson:"crackmehexid,omitempty"`
	CrackmeName  string             `bson:"crackmename,omitempty"`
	CreatedAt    time.Time          `bson:"created_at"`
	Visible      bool               `bson:"visible"`
	Deleted      bool               `bson:"deleted"`
}

func CountCommentsByUser(username string) (int, error) {
	var err error
	var nb int64
	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("comment")
		nb, err = collection.CountDocuments(database.Ctx, bson.M{"author": username})
	} else {
		err = ErrUnavailable
	}
	return int(nb), standardizeError(err)
}

func CountCommentsByCrackme(crackmehexid string) (int, error) {
	var err error
	var nb int64
	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("comment")
		nb, err = collection.CountDocuments(database.Ctx, bson.M{"crackmehexid": crackmehexid, "visible": true})
	} else {
		err = ErrUnavailable
	}
	return int(nb), standardizeError(err)
}

func CommentsByUser(name string) ([]Comment, error) {
	var err error
	var cursor *mongo.Cursor
	var result []Comment
	if database.CheckConnection() {
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("comment")
		// Validate the object id
		opts := options.Find().SetSort(bson.D{{"created_at", -1}}).SetLimit(50)
		cursor, err = collection.Find(database.Ctx, bson.M{"author": name, "visible": true}, opts)
		err = cursor.All(database.Ctx, &result)
	} else {
		err = ErrUnavailable
	}
	return result, err
}

func CommentsByCrackMe(crackmehexid string) ([]Comment, error) {
	var err error
	var cursor *mongo.Cursor
	var result []Comment
	if database.CheckConnection() {
		// Create a copy of mongo
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("comment")
		opts := options.Find().SetSort(bson.D{{"created_at", 1}})

		// Validate the object id
		cursor, err = collection.Find(database.Ctx, bson.M{"crackmehexid": crackmehexid, "visible": true}, opts)
		err = cursor.All(database.Ctx, &result)
	} else {
		err = ErrUnavailable
	}
	return result, err
}

func CommentCreate(content, username, crackmehexid string) error {
	var err error

	// Fetch crackme to get its name
	crackme, err := CrackmeByHexId(crackmehexid)
	if err != nil {
		return standardizeError(err)
	}

	if database.CheckConnection() {
		objId := primitive.NewObjectID()
		collection := database.Mongo.Database(database.ReadConfig().MongoDB.Database).Collection("comment")
		comment := &Comment{
			ObjectId:     objId,
			Content:      content,
			Author:       username,
			CrackMeHexId: crackmehexid,
			CrackmeName:  crackme.Name,
			CreatedAt:    time.Now(),
			Visible:      true,
			Deleted:      false,
		}
		_, err = collection.InsertOne(database.Ctx, comment)
	} else {
		err = ErrUnavailable
	}

	return standardizeError(err)
}
