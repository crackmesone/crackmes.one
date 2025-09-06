"""
Solution model
Python equivalent of app/model/solution.go
"""

from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.shared.database import get_collection


class SolutionValidationError(Exception):
    """Solution validation error"""
    pass


class Solution:
    """Solution model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.hex_id = kwargs.get('hexid', '')
        self.info = kwargs.get('info', '')
        self.crackme_id = kwargs.get('crackmeid')  # ObjectId of the crackme
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.author = kwargs.get('author', '')
        self.visible = kwargs.get('visible', False)  # Default false for moderation
        self.deleted = kwargs.get('deleted', False)
    
    def to_dict(self):
        """Convert solution to dictionary for MongoDB storage"""
        doc = {
            'hexid': self.hex_id,
            'info': self.info,
            'crackmeid': self.crackme_id,
            'created_at': self.created_at,
            'author': self.author,
            'visible': self.visible,
            'deleted': self.deleted
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create Solution instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate solution data"""
        errors = []
        
        # Validate info
        if not self.info or len(self.info.strip()) < 10:
            errors.append("Solution description must be at least 10 characters long")
        
        # Validate author
        if not self.author:
            errors.append("Author is required")
            
        # Validate crackme_id
        if not self.crackme_id:
            errors.append("Crackme ID is required")
        
        if errors:
            raise SolutionValidationError("; ".join(errors))
    
    def save(self):
        """Save solution to database"""
        collection = get_collection('solution')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing solution
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new solution
            # Generate hex ID
            if not self.hex_id:
                temp_id = ObjectId()
                self.hex_id = str(temp_id)
            
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            return True


class SolutionExtended:
    """Extended solution with crackme information"""
    
    def __init__(self, solution, crackme_hex_id, crackme_name):
        self.solution = solution
        self.crackme_hex_id = crackme_hex_id
        self.crackme_name = crackme_name


class SolutionModel:
    """Solution database operations"""
    
    @staticmethod
    def get_by_hex_id(hex_id):
        """Get solution by hex ID"""
        collection = get_collection('solution')
        doc = collection.find_one({'hexid': hex_id, 'deleted': False})
        return Solution.from_dict(doc)
    
    @staticmethod
    def get_by_crackme(crackme_hex_id, limit=20, skip=0):
        """Get solutions for a specific crackme"""
        # First get the crackme to find its ObjectId
        from app.models.crackme import CrackmeModel
        crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
        if not crackme:
            return []
        
        collection = get_collection('solution')
        cursor = collection.find(
            {'crackmeid': crackme.object_id, 'visible': True, 'deleted': False}
        ).sort('created_at', -1).skip(skip).limit(limit)
        
        solutions = []
        for doc in cursor:
            solution = Solution.from_dict(doc)
            if solution:
                solutions.append(solution)
        
        return solutions
    
    @staticmethod
    def get_by_author(author, limit=20, skip=0):
        """Get solutions by author with crackme information"""
        collection = get_collection('solution')
        cursor = collection.find(
            {'author': author, 'visible': True, 'deleted': False}
        ).sort('created_at', -1).skip(skip).limit(limit)
        
        solutions_extended = []
        for doc in cursor:
            solution = Solution.from_dict(doc)
            if solution:
                # Get crackme information
                crackme_collection = get_collection('crackme')
                crackme_doc = crackme_collection.find_one({'_id': solution.crackme_id})
                
                if crackme_doc:
                    extended = SolutionExtended(
                        solution,
                        crackme_doc.get('hexid', ''),
                        crackme_doc.get('name', 'Unknown Crackme')
                    )
                    solutions_extended.append(extended)
        
        return solutions_extended
    
    @staticmethod
    def count_solutions():
        """Count total solutions"""
        collection = get_collection('solution')
        return collection.count_documents({'deleted': False})
    
    @staticmethod
    def count_by_user(username):
        """Count solutions by user"""
        collection = get_collection('solution')
        return collection.count_documents({'author': username, 'visible': True, 'deleted': False})
    
    @staticmethod
    def count_by_crackme(crackme_hex_id):
        """Count solutions for a specific crackme"""
        # First get the crackme to find its ObjectId
        from app.models.crackme import CrackmeModel
        crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
        if not crackme:
            return 0
        
        collection = get_collection('solution')
        return collection.count_documents({'crackmeid': crackme.object_id, 'visible': True, 'deleted': False})
    
    @staticmethod
    def create_solution(crackme_hex_id, author, info):
        """Create a new solution"""
        # Get the crackme
        from app.models.crackme import CrackmeModel
        crackme = CrackmeModel.get_by_hex_id(crackme_hex_id)
        if not crackme:
            raise SolutionValidationError("Crackme not found")
        
        # Create solution
        solution = Solution(
            info=info,
            author=author,
            crackme_id=crackme.object_id
        )
        solution.save()
        
        return solution