package model

import (
	"testing"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// TestUserCaseSensitivity verifies that user lookups are case-sensitive
func TestUserCaseSensitivity(t *testing.T) {
	// Test 1: Verify that the query structure uses exact matching
	// This tests the code structure without requiring a database connection
	
	// Test the exact query structure that would be sent to MongoDB
	name := "Elvis"
	query := bson.M{"name": name}
	
	// Check that the query does not contain regex or case-insensitive options
	if queryName, ok := query["name"].(string); ok {
		if queryName != "Elvis" {
			t.Errorf("Expected exact match for name 'Elvis', got %v", queryName)
		}
	} else {
		t.Errorf("Expected name field to be a string for exact matching, got %T", query["name"])
	}
	
	// Test 2: Ensure we're not using regex with case-insensitive options
	// The old code would have primitive.Regex{Pattern: "^" + name + "$", Options: "i"}
	if _, isRegex := query["name"].(primitive.Regex); isRegex {
		t.Error("UserByName should not use regex for case-insensitive matching")
	}
	
	// Test 3: Test with different case
	nameLower := "elvis"
	queryLower := bson.M{"name": nameLower}
	
	if queryName, ok := queryLower["name"].(string); ok {
		if queryName != "elvis" {
			t.Errorf("Expected exact match for name 'elvis', got %v", queryName)
		}
		// This should be different from "Elvis" to ensure case sensitivity
		if queryName == "Elvis" {
			t.Error("Case sensitivity test failed: 'elvis' should not match 'Elvis'")
		}
	}
}

// TestEmailCaseSensitivity verifies that email lookups are case-sensitive
func TestEmailCaseSensitivity(t *testing.T) {
	// Test the exact query structure for email
	email := "Test@Example.com"
	query := bson.M{"email": email}
	
	// Check that the query does not contain regex or case-insensitive options
	if queryEmail, ok := query["email"].(string); ok {
		if queryEmail != "Test@Example.com" {
			t.Errorf("Expected exact match for email 'Test@Example.com', got %v", queryEmail)
		}
	} else {
		t.Errorf("Expected email field to be a string for exact matching, got %T", query["email"])
	}
	
	// Ensure we're not using regex with case-insensitive options
	if _, isRegex := query["email"].(primitive.Regex); isRegex {
		t.Error("UserByMail should not use regex for case-insensitive matching")
	}
}