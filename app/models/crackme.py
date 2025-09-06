"""
Crackme model
Python equivalent of app/model/crackme.go
"""

from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
import re
from app.shared.database import get_collection


class CrackmeValidationError(Exception):
    """Crackme validation error"""
    pass


class Crackme:
    """Crackme model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.hex_id = kwargs.get('hexid', '')
        self.name = kwargs.get('name', '')
        self.info = kwargs.get('info', '')
        self.lang = kwargs.get('lang', '')
        self.arch = kwargs.get('arch', '')
        self.author = kwargs.get('author', '')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.visible = kwargs.get('visible', False)  # Default false for moderation
        self.deleted = kwargs.get('deleted', False)
        self.difficulty = kwargs.get('difficulty', 0.0)
        self.quality = kwargs.get('quality', 0.0)
        self.platform = kwargs.get('platform', '')
        
        # Computed fields (not stored in DB)
        self.nb_solutions = kwargs.get('nb_solutions', 0)
        self.nb_comments = kwargs.get('nb_comments', 0)
    
    def to_dict(self):
        """Convert crackme to dictionary for MongoDB storage"""
        doc = {
            'hexid': self.hex_id,
            'name': self.name,
            'info': self.info,
            'lang': self.lang,
            'arch': self.arch,
            'author': self.author,
            'created_at': self.created_at,
            'visible': self.visible,
            'deleted': self.deleted,
            'difficulty': self.difficulty,
            'quality': self.quality,
            'platform': self.platform
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create Crackme instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate crackme data"""
        errors = []
        
        # Validate name
        if not self.name or len(self.name.strip()) < 3:
            errors.append("Crackme name must be at least 3 characters long")
        
        # Validate author
        if not self.author:
            errors.append("Author is required")
        
        # Validate language
        if not self.lang:
            errors.append("Programming language is required")
            
        # Validate architecture
        if not self.arch:
            errors.append("Architecture is required")
            
        # Validate platform
        if not self.platform:
            errors.append("Platform is required")
        
        if errors:
            raise CrackmeValidationError("; ".join(errors))
    
    def save(self):
        """Save crackme to database"""
        collection = get_collection('crackme')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing crackme
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new crackme
            # Generate hex ID
            if not self.hex_id:
                temp_id = ObjectId()
                self.hex_id = str(temp_id)
            
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            return True


class CrackmeModel:
    """Crackme database operations"""
    
    @staticmethod
    def get_by_hex_id(hex_id):
        """Get crackme by hex ID"""
        collection = get_collection('crackme')
        doc = collection.find_one({'hexid': hex_id, 'deleted': False})
        crackme = Crackme.from_dict(doc)
        
        if crackme:
            # Load computed fields
            crackme.nb_solutions = CrackmeModel.count_solutions_by_crackme(hex_id)
            crackme.nb_comments = CrackmeModel.count_comments_by_crackme(hex_id)
        
        return crackme
    
    @staticmethod
    def get_visible_crackmes(limit=20, skip=0):
        """Get visible crackmes with pagination"""
        collection = get_collection('crackme')
        cursor = collection.find(
            {'visible': True, 'deleted': False}
        ).sort('created_at', -1).skip(skip).limit(limit)
        
        crackmes = []
        for doc in cursor:
            crackme = Crackme.from_dict(doc)
            if crackme:
                # Load computed fields
                crackme.nb_solutions = CrackmeModel.count_solutions_by_crackme(crackme.hex_id)
                crackme.nb_comments = CrackmeModel.count_comments_by_crackme(crackme.hex_id)
                crackmes.append(crackme)
        
        return crackmes
    
    @staticmethod
    def get_by_author(author, limit=20, skip=0):
        """Get crackmes by author"""
        collection = get_collection('crackme')
        cursor = collection.find(
            {'author': author, 'visible': True, 'deleted': False}
        ).sort('created_at', -1).skip(skip).limit(limit)
        
        crackmes = []
        for doc in cursor:
            crackme = Crackme.from_dict(doc)
            if crackme:
                crackme.nb_solutions = CrackmeModel.count_solutions_by_crackme(crackme.hex_id)
                crackme.nb_comments = CrackmeModel.count_comments_by_crackme(crackme.hex_id)
                crackmes.append(crackme)
        
        return crackmes
    
    @staticmethod
    def count_crackmes():
        """Count total visible crackmes"""
        collection = get_collection('crackme')
        return collection.count_documents({'visible': True, 'deleted': False})
    
    @staticmethod
    def count_by_user(username):
        """Count crackmes by user"""
        collection = get_collection('crackme')
        return collection.count_documents({'author': username, 'visible': True, 'deleted': False})
    
    @staticmethod
    def count_solutions_by_crackme(crackme_hex_id):
        """Count solutions for a crackme"""
        try:
            from app.models.solution import SolutionModel
            return SolutionModel.count_by_crackme(crackme_hex_id)
        except:
            return 0
    
    @staticmethod
    def count_comments_by_crackme(crackme_hex_id):
        """Count comments for a crackme"""
        try:
            from app.models.comment import CommentModel
            return CommentModel.count_by_crackme(crackme_hex_id)
        except:
            return 0
    
    @staticmethod
    def search_crackmes(query, limit=20, skip=0):
        """Search crackmes by name or description"""
        collection = get_collection('crackme')
        
        # Create text search query
        search_filter = {
            'visible': True,
            'deleted': False,
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'info': {'$regex': query, '$options': 'i'}},
                {'author': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        cursor = collection.find(search_filter).sort('created_at', -1).skip(skip).limit(limit)
        
        crackmes = []
        for doc in cursor:
            crackme = Crackme.from_dict(doc)
            if crackme:
                crackme.nb_solutions = CrackmeModel.count_solutions_by_crackme(crackme.hex_id)
                crackme.nb_comments = CrackmeModel.count_comments_by_crackme(crackme.hex_id)
                crackmes.append(crackme)
        
        return crackmes