"""
crackmes.one - Python Web Application

This is the Python version of the crackmes.one website, 
rewritten from the original Go codebase.

Original Go application was created using GoWebApp framework.
This Python version uses Flask to provide equivalent functionality.
"""

import os
import json
import logging
from flask import Flask
from flask_session import Session
from pymongo import MongoClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s:%(lineno)d %(message)s'
)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config_path = os.path.join('config', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Configure Flask app
        app.config['SECRET_KEY'] = config.get('Session', {}).get('Key', 'default-secret-key')
        app.config['SESSION_TYPE'] = 'mongodb'
        app.config['UPLOAD_FOLDER'] = 'tmp'
        
        # Configure MongoDB
        mongo_config = config.get('Database', {}).get('MongoDB', {})
        mongo_url = mongo_config.get('URL', 'mongodb://127.0.0.1:27017')
        mongo_db = mongo_config.get('Database', 'crackmesone')
        
        app.config['MONGO_URL'] = mongo_url
        app.config['MONGO_DB'] = mongo_db
        
        # Setup MongoDB connection
        app.mongo_client = MongoClient(mongo_url)
        app.mongo_db = app.mongo_client[mongo_db]
        
        # Configure session
        app.config['SESSION_MONGODB'] = app.mongo_client
        app.config['SESSION_MONGODB_DB'] = mongo_db
        app.config['SESSION_MONGODB_COLLECT'] = 'sessions'
        
    else:
        # Default configuration for development
        app.config['SECRET_KEY'] = 'dev-secret-key'
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['UPLOAD_FOLDER'] = 'tmp'
        
        # Default MongoDB connection
        app.mongo_client = MongoClient('mongodb://127.0.0.1:27017')
        app.mongo_db = app.mongo_client['crackmesone']
    
    # Initialize Flask-Session
    Session(app)
    
    # Register blueprints
    from app.routes import main_bp, auth_bp, crackme_bp, user_bp, api_bp, inject_notification_count
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(crackme_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register context processor
    app.context_processor(inject_notification_count)
    
    return app
    
    return app

def main():
    """Main entry point - equivalent to Go's main function"""
    # Create uploads directories
    os.makedirs('tmp/crackme', exist_ok=True)
    os.makedirs('tmp/solution', exist_ok=True)
    os.makedirs('static/crackme', exist_ok=True)
    os.makedirs('static/solution', exist_ok=True)
    
    # Create Flask app
    app = create_app()
    
    # Run the application
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()