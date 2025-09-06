"""
Database connection and utilities
Python equivalent of app/shared/database/database.go
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.config = None
    
    def connect(self, config):
        """
        Connect to MongoDB database
        
        Args:
            config: Dictionary with MongoDB configuration
        """
        self.config = config
        
        try:
            # Extract MongoDB configuration
            mongo_config = config.get('MongoDB', {})
            url = mongo_config.get('URL', 'mongodb://127.0.0.1:27017')
            database_name = mongo_config.get('Database', 'crackmesone')
            
            # Connect to MongoDB
            self.client = MongoClient(url, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            self.client.admin.command('ismaster')
            
            # Get database
            self.db = self.client[database_name]
            
            logging.info(f"Connected to MongoDB: {url}")
            
        except ConnectionFailure as e:
            logging.error(f"MongoDB connection failed: {e}")
            raise
        except Exception as e:
            logging.error(f"Database error: {e}")
            raise
    
    def check_connection(self):
        """
        Check if database connection is available
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.client is None:
            return False
        
        try:
            self.client.admin.command('ismaster')
            return True
        except:
            return False
    
    def get_collection(self, name):
        """
        Get a MongoDB collection
        
        Args:
            name: Collection name
            
        Returns:
            Collection object
        """
        if self.db is None:
            raise Exception("Database not connected")
        
        return self.db[name]

# Global database instance
db = Database()

def connect(config):
    """Connect to database with configuration"""
    db.connect(config)

def check_connection():
    """Check if database is connected"""
    return db.check_connection()

def get_collection(name):
    """Get a collection from the database"""
    return db.get_collection(name)