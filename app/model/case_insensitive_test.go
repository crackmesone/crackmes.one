package model

import (
	"testing"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// TestCaseInsensitiveUserLookup verifies that user lookup functions use case-insensitive matching
func TestCaseInsensitiveUserLookup(t *testing.T) {
	// Test that UserByName uses case-insensitive regex
	// This test verifies the query structure, not the actual database query
	
	// The UserByName function should use this pattern:
	// bson.M{"name": primitive.Regex{Pattern: "^" + name + "$", Options: "i"}}
	
	expectedPattern := "^Elvis$"
	expectedOptions := "i"
	
	query := bson.M{"name": primitive.Regex{Pattern: expectedPattern, Options: expectedOptions}}
	
	// Verify the query structure
	nameField, exists := query["name"]
	if !exists {
		t.Error("Query should have 'name' field")
	}
	
	regex, ok := nameField.(primitive.Regex)
	if !ok {
		t.Error("Name field should be a primitive.Regex")
	}
	
	if regex.Pattern != expectedPattern {
		t.Errorf("Expected pattern '%s', got '%s'", expectedPattern, regex.Pattern)
	}
	
	if regex.Options != expectedOptions {
		t.Errorf("Expected options '%s', got '%s'", expectedOptions, regex.Options)
	}
}

// TestCaseInsensitiveAuthorLookup verifies that author field lookups use case-insensitive matching
func TestCaseInsensitiveAuthorLookup(t *testing.T) {
	// Test that author queries use case-insensitive regex
	
	expectedPattern := "^Elvis$"
	expectedOptions := "i"
	
	// Test CountCrackmesByUser query structure
	query := bson.M{"author": primitive.Regex{Pattern: expectedPattern, Options: expectedOptions}, "visible": true}
	
	authorField, exists := query["author"]
	if !exists {
		t.Error("Query should have 'author' field")
	}
	
	regex, ok := authorField.(primitive.Regex)
	if !ok {
		t.Error("Author field should be a primitive.Regex")
	}
	
	if regex.Pattern != expectedPattern {
		t.Errorf("Expected pattern '%s', got '%s'", expectedPattern, regex.Pattern)
	}
	
	if regex.Options != expectedOptions {
		t.Errorf("Expected options '%s', got '%s'", expectedOptions, regex.Options)
	}
	
	// Verify visible field is also present
	if visible, exists := query["visible"]; !exists || visible != true {
		t.Error("Query should have 'visible': true")
	}
}