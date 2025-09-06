"""
Rating models for difficulty and quality
Python equivalent of app/model/rating_difficulty.go and rating_quality.go
"""

from datetime import datetime
from bson import ObjectId
from app.shared.database import get_collection


class RatingValidationError(Exception):
    """Rating validation error"""
    pass


class RatingDifficulty:
    """Difficulty rating model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.author = kwargs.get('author', '')
        self.crackme_hex_id = kwargs.get('crackmehexid', '')
        self.rating = kwargs.get('rating', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.visible = kwargs.get('visible', True)
        self.deleted = kwargs.get('deleted', False)
    
    def to_dict(self):
        """Convert rating to dictionary for MongoDB storage"""
        doc = {
            'author': self.author,
            'crackmehexid': self.crackme_hex_id,
            'rating': self.rating,
            'created_at': self.created_at,
            'visible': self.visible,
            'deleted': self.deleted
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create RatingDifficulty instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate rating data"""
        errors = []
        
        if not self.author:
            errors.append("Author is required")
            
        if not self.crackme_hex_id:
            errors.append("Crackme ID is required")
            
        if not isinstance(self.rating, int) or self.rating < 1 or self.rating > 5:
            errors.append("Rating must be between 1 and 5")
        
        if errors:
            raise RatingValidationError("; ".join(errors))
    
    def save(self):
        """Save rating to database"""
        collection = get_collection('rating_difficulty')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing rating
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new rating
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            return True


class RatingQuality:
    """Quality rating model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.author = kwargs.get('author', '')
        self.crackme_hex_id = kwargs.get('crackmehexid', '')
        self.rating = kwargs.get('rating', 0)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.visible = kwargs.get('visible', True)
        self.deleted = kwargs.get('deleted', False)
    
    def to_dict(self):
        """Convert rating to dictionary for MongoDB storage"""
        doc = {
            'author': self.author,
            'crackmehexid': self.crackme_hex_id,
            'rating': self.rating,
            'created_at': self.created_at,
            'visible': self.visible,
            'deleted': self.deleted
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create RatingQuality instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate rating data"""
        errors = []
        
        if not self.author:
            errors.append("Author is required")
            
        if not self.crackme_hex_id:
            errors.append("Crackme ID is required")
            
        if not isinstance(self.rating, int) or self.rating < 1 or self.rating > 5:
            errors.append("Rating must be between 1 and 5")
        
        if errors:
            raise RatingValidationError("; ".join(errors))
    
    def save(self):
        """Save rating to database"""
        collection = get_collection('rating_quality')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing rating
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new rating
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            return True


class RatingModel:
    """Rating database operations"""
    
    @staticmethod
    def is_already_rated_difficulty(username, crackme_hex_id):
        """Check if user already rated difficulty"""
        collection = get_collection('rating_difficulty')
        return collection.find_one({
            'author': username,
            'crackmehexid': crackme_hex_id,
            'deleted': False
        }) is not None
    
    @staticmethod
    def is_already_rated_quality(username, crackme_hex_id):
        """Check if user already rated quality"""
        collection = get_collection('rating_quality')
        return collection.find_one({
            'author': username,
            'crackmehexid': crackme_hex_id,
            'deleted': False
        }) is not None
    
    @staticmethod
    def get_average_difficulty(crackme_hex_id):
        """Get average difficulty rating for a crackme"""
        collection = get_collection('rating_difficulty')
        
        pipeline = [
            {'$match': {'crackmehexid': crackme_hex_id, 'visible': True, 'deleted': False}},
            {'$group': {'_id': None, 'average': {'$avg': '$rating'}, 'count': {'$sum': 1}}}
        ]
        
        result = list(collection.aggregate(pipeline))
        if result:
            return result[0]['average'], result[0]['count']
        return 0.0, 0
    
    @staticmethod
    def get_average_quality(crackme_hex_id):
        """Get average quality rating for a crackme"""
        collection = get_collection('rating_quality')
        
        pipeline = [
            {'$match': {'crackmehexid': crackme_hex_id, 'visible': True, 'deleted': False}},
            {'$group': {'_id': None, 'average': {'$avg': '$rating'}, 'count': {'$sum': 1}}}
        ]
        
        result = list(collection.aggregate(pipeline))
        if result:
            return result[0]['average'], result[0]['count']
        return 0.0, 0
    
    @staticmethod
    def rate_difficulty(username, crackme_hex_id, rating):
        """Rate the difficulty of a crackme"""
        # Check if already rated
        if RatingModel.is_already_rated_difficulty(username, crackme_hex_id):
            raise RatingValidationError("You have already rated the difficulty of this crackme")
        
        # Verify crackme exists
        from app.models.crackme import CrackmeModel
        crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
        if not crackme:
            raise RatingValidationError("Crackme not found")
        
        # Create rating
        rating_obj = RatingDifficulty(
            author=username,
            crackme_hex_id=crackme_hex_id,
            rating=rating
        )
        rating_obj.save()
        
        # Update crackme's average difficulty
        avg_difficulty, count = RatingModel.get_average_difficulty(crackme_hex_id)
        crackme.difficulty = avg_difficulty
        crackme.save()
        
        return rating_obj
    
    @staticmethod
    def rate_quality(username, crackme_hex_id, rating):
        """Rate the quality of a crackme"""
        # Check if already rated
        if RatingModel.is_already_rated_quality(username, crackme_hex_id):
            raise RatingValidationError("You have already rated the quality of this crackme")
        
        # Verify crackme exists
        from app.models.crackme import CrackmeModel
        crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
        if not crackme:
            raise RatingValidationError("Crackme not found")
        
        # Create rating
        rating_obj = RatingQuality(
            author=username,
            crackme_hex_id=crackme_hex_id,
            rating=rating
        )
        rating_obj.save()
        
        # Update crackme's average quality
        avg_quality, count = RatingModel.get_average_quality(crackme_hex_id)
        crackme.quality = avg_quality
        crackme.save()
        
        return rating_obj