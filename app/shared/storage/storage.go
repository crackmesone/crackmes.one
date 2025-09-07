package storage

import (
	"os"
)

// *****************************************************************************
// Storage Configuration
// *****************************************************************************

// Info contains the storage configuration
type Info struct {
	CrackmePath  string `json:"CrackmePath"`
	SolutionPath string `json:"SolutionPath"`
}

// Configure reads environment variables and sets up storage paths
func Configure() Info {
	crackmePath := os.Getenv("CRACKME_STORAGE_PATH")
	if crackmePath == "" {
		crackmePath = "tmp/crackme"
	}

	solutionPath := os.Getenv("SOLUTION_STORAGE_PATH")
	if solutionPath == "" {
		solutionPath = "tmp/solution"
	}

	return Info{
		CrackmePath:  crackmePath,
		SolutionPath: solutionPath,
	}
}

// Global storage configuration instance
var config Info

// Initialize the storage configuration
func init() {
	config = Configure()
}

// GetCrackmePath returns the configured crackme storage path
func GetCrackmePath() string {
	return config.CrackmePath
}

// GetSolutionPath returns the configured solution storage path
func GetSolutionPath() string {
	return config.SolutionPath
}