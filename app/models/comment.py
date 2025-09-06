"""
Comment model
Python equivalent of app/model/comment.go
"""

from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.shared.database import get_collection


class CommentValidationError(Exception):
    """Comment validation error"""
    pass


class Comment:
    """Comment model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.content = kwargs.get('info', '')  # Note: uses 'info' field in MongoDB like Go version
        self.author = kwargs.get('author', '')
        self.crackme_hex_id = kwargs.get('crackmehexid', '')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.visible = kwargs.get('visible', True)  # Comments are visible by default
        self.deleted = kwargs.get('deleted', False)
    
    def to_dict(self):
        """Convert comment to dictionary for MongoDB storage"""
        doc = {
            'info': self.content,
            'author': self.author,
            'crackmehexid': self.crackme_hex_id,
            'created_at': self.created_at,
            'visible': self.visible,
            'deleted': self.deleted
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create Comment instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate comment data"""
        errors = []
        
        # Validate content
        if not self.content or len(self.content.strip()) < 3:
            errors.append("Comment must be at least 3 characters long")
        
        if len(self.content) > 1000:
            errors.append("Comment must be less than 1000 characters")
        
        # Validate author
        if not self.author:
            errors.append("Author is required")
            
        # Validate crackme_hex_id
        if not self.crackme_hex_id:
            errors.append("Crackme ID is required")
        
        if errors:
            raise CommentValidationError("; ".join(errors))
    
    def save(self):
        """Save comment to database"""
        collection = get_collection('comment')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing comment
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new comment
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            return True


class CommentModel:
    """Comment database operations"""
    
    @staticmethod
    def get_by_crackme(crackme_hex_id, limit=50, skip=0):
        """Get comments for a specific crackme"""
        collection = get_collection('comment')
        cursor = collection.find(
            {'crackmehexid': crackme_hex_id, 'visible': True, 'deleted': False}
        ).sort('created_at', 1).skip(skip).limit(limit)  # Oldest first for comments
        
        comments = []
        for doc in cursor:
            comment = Comment.from_dict(doc)
            if comment:
                comments.append(comment)
        
        return comments
    
    @staticmethod
    def get_by_author(author, limit=20, skip=0):
        """Get comments by author"""
        collection = get_collection('comment')
        cursor = collection.find(
            {'author': author, 'visible': True, 'deleted': False}
        ).sort('created_at', -1).skip(skip).limit(limit)  # Newest first for user profile
        
        comments = []
        for doc in cursor:
            comment = Comment.from_dict(doc)
            if comment:
                comments.append(comment)
        
        return comments
    
    @staticmethod
    def count_by_user(username):
        """Count comments by user"""
        collection = get_collection('comment')
        return collection.count_documents({'author': username, 'visible': True, 'deleted': False})
    
    @staticmethod
    def count_by_crackme(crackme_hex_id):
        """Count comments for a specific crackme"""
        collection = get_collection('comment')
        return collection.count_documents({'crackmehexid': crackme_hex_id, 'visible': True, 'deleted': False})
    
    @staticmethod
    def create_comment(crackme_hex_id, author, content):
        """Create a new comment"""
        # Verify crackme exists
        from app.models.crackme import CrackmeModel
        crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
        if not crackme:
            raise CommentValidationError("Crackme not found")
        
        # Create comment
        comment = Comment(
            content=content,
            author=author,
            crackme_hex_id=crackme_hex_id
        )
        comment.save()
        
        return comment
    
    @staticmethod
    def get_recent_comments(limit=10):
        """Get recent comments across all crackmes"""
        collection = get_collection('comment')
        cursor = collection.find(
            {'visible': True, 'deleted': False}
        ).sort('created_at', -1).limit(limit)
        
        comments = []
        for doc in cursor:
            comment = Comment.from_dict(doc)
            if comment:
                comments.append(comment)
        
        return comments