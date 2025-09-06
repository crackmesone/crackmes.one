"""
User model
Python equivalent of app/model/user.go
"""

from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import bcrypt
import re
from app.shared.database import get_collection


class UserValidationError(Exception):
    """User validation error"""
    pass


class User:
    """User model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.hex_id = kwargs.get('hexid', '')
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.password = kwargs.get('password', '')
        self.visible = kwargs.get('visible', True)
        self.deleted = kwargs.get('deleted', False)
        self.nb_crackmes = kwargs.get('nb_crackmes', 0)
        self.nb_solutions = kwargs.get('nb_solutions', 0)
        self.nb_comments = kwargs.get('nb_comments', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
    
    def to_dict(self):
        """Convert user to dictionary for MongoDB storage"""
        doc = {
            'hexid': self.hex_id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'visible': self.visible,
            'deleted': self.deleted,
            'nb_crackmes': self.nb_crackmes,
            'nb_solutions': self.nb_solutions,
            'nb_comments': self.nb_comments,
            'created_at': self.created_at
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create User instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate user data"""
        errors = []
        
        # Validate name
        if not self.name or len(self.name.strip()) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.name):
            errors.append("Username can only contain letters, numbers, underscores and hyphens")
        
        # Validate email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not self.email or not re.match(email_pattern, self.email):
            errors.append("Valid email address is required")
        
        # Validate password (only when setting new password)
        if hasattr(self, '_new_password') and self._new_password:
            if len(self._new_password) < 6:
                errors.append("Password must be at least 6 characters long")
        
        if errors:
            raise UserValidationError("; ".join(errors))
    
    def set_password(self, plain_password):
        """Hash and set password"""
        self._new_password = plain_password
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, plain_password):
        """Check if provided password matches stored hash"""
        if not self.password:
            return False
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))
    
    def save(self):
        """Save user to database"""
        collection = get_collection('user')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing user
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new user
            # Generate hex ID
            if not self.hex_id:
                temp_id = ObjectId()
                self.hex_id = str(temp_id)
            
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            return True


class UserModel:
    """User database operations - equivalent to Go model functions"""
    
    @staticmethod
    def get_by_name(name):
        """Get user by username"""
        collection = get_collection('user')
        doc = collection.find_one({'name': name, 'deleted': False})
        return User.from_dict(doc)
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        collection = get_collection('user')
        doc = collection.find_one({'email': email, 'deleted': False})
        return User.from_dict(doc)
    
    @staticmethod
    def get_by_hex_id(hex_id):
        """Get user by hex ID"""
        collection = get_collection('user')
        doc = collection.find_one({'hexid': hex_id, 'deleted': False})
        return User.from_dict(doc)
    
    @staticmethod
    def exists_by_name(name):
        """Check if user exists by name"""
        collection = get_collection('user')
        return collection.find_one({'name': name, 'deleted': False}) is not None
    
    @staticmethod
    def exists_by_email(email):
        """Check if user exists by email"""
        collection = get_collection('user')
        return collection.find_one({'email': email, 'deleted': False}) is not None
    
    @staticmethod
    def create_user(name, email, password):
        """Create a new user"""
        # Check if user already exists
        if UserModel.exists_by_name(name):
            raise UserValidationError("Username already exists")
        
        if UserModel.exists_by_email(email):
            raise UserValidationError("Email already exists")
        
        # Create new user
        user = User(name=name, email=email)
        user.set_password(password)
        user.save()
        
        return user
    
    @staticmethod
    def authenticate(name, password):
        """Authenticate user with name/email and password"""
        # Try to find user by name or email
        user = UserModel.get_by_name(name)
        if not user:
            user = UserModel.get_by_email(name)
        
        if user and user.check_password(password):
            return user
        
        return None