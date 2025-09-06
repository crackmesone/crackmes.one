"""
Notification model
Python equivalent of app/model/notifications.go
"""

from datetime import datetime
from bson import ObjectId
from app.shared.database import get_collection


class NotificationValidationError(Exception):
    """Notification validation error"""
    pass


class Notification:
    """Notification model"""
    
    def __init__(self, **kwargs):
        self.object_id = kwargs.get('_id')
        self.hex_id = kwargs.get('hexid', '')
        self.user = kwargs.get('user', '')
        self.text = kwargs.get('text', '')
        self.time = kwargs.get('time', datetime.utcnow())
        self.seen = kwargs.get('seen', False)
    
    def to_dict(self):
        """Convert notification to dictionary for MongoDB storage"""
        doc = {
            'hexid': self.hex_id,
            'user': self.user,
            'text': self.text,
            'time': self.time,
            'seen': self.seen
        }
        
        if self.object_id:
            doc['_id'] = self.object_id
            
        return doc
    
    @classmethod
    def from_dict(cls, doc):
        """Create Notification instance from MongoDB document"""
        if not doc:
            return None
        return cls(**doc)
    
    def validate(self):
        """Validate notification data"""
        errors = []
        
        if not self.user:
            errors.append("User is required")
            
        if not self.text:
            errors.append("Text is required")
        
        if errors:
            raise NotificationValidationError("; ".join(errors))
    
    def save(self):
        """Save notification to database"""
        collection = get_collection('notifications')
        
        # Validate before saving
        self.validate()
        
        if self.object_id:
            # Update existing notification
            result = collection.update_one(
                {'_id': self.object_id},
                {'$set': self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # Create new notification
            # Generate hex ID
            if not self.hex_id:
                temp_id = ObjectId()
                self.hex_id = str(temp_id)
            
            doc = self.to_dict()
            result = collection.insert_one(doc)
            self.object_id = result.inserted_id
            
            # Update hex_id with the actual object ID
            self.hex_id = str(self.object_id)
            collection.update_one(
                {'_id': self.object_id},
                {'$set': {'hexid': self.hex_id}}
            )
            
            return True


class NotificationModel:
    """Notification database operations"""
    
    @staticmethod
    def get_by_user(username, limit=50, skip=0):
        """Get notifications for a user"""
        collection = get_collection('notifications')
        cursor = collection.find({'user': username}).sort('time', -1).skip(skip).limit(limit)
        
        notifications = []
        for doc in cursor:
            notification = Notification.from_dict(doc)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def get_unseen_by_user(username):
        """Get unseen notifications for a user"""
        collection = get_collection('notifications')
        cursor = collection.find({'user': username, 'seen': False}).sort('time', -1)
        
        notifications = []
        for doc in cursor:
            notification = Notification.from_dict(doc)
            if notification:
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def count_unseen_by_user(username):
        """Count unseen notifications for a user"""
        collection = get_collection('notifications')
        return collection.count_documents({'user': username, 'seen': False})
    
    @staticmethod
    def mark_as_seen(username, notification_hex_id=None):
        """Mark notification(s) as seen"""
        collection = get_collection('notifications')
        
        if notification_hex_id:
            # Mark specific notification as seen
            result = collection.update_one(
                {'user': username, 'hexid': notification_hex_id},
                {'$set': {'seen': True}}
            )
            return result.modified_count > 0
        else:
            # Mark all notifications as seen
            result = collection.update_many(
                {'user': username, 'seen': False},
                {'$set': {'seen': True}}
            )
            return result.modified_count
    
    @staticmethod
    def delete_notification(username, notification_hex_id):
        """Delete a notification"""
        collection = get_collection('notifications')
        result = collection.delete_one({
            'user': username,
            'hexid': notification_hex_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    def create_notification(username, text):
        """Create a new notification"""
        notification = Notification(
            user=username,
            text=text
        )
        notification.save()
        return notification
    
    @staticmethod
    def notify_crackme_approved(username, crackme_name):
        """Create notification for approved crackme"""
        text = f"Your crackme '{crackme_name}' has been accepted!"
        return NotificationModel.create_notification(username, text)
    
    @staticmethod
    def notify_solution_approved(username, crackme_name):
        """Create notification for approved solution"""
        text = f"Your solution for '{crackme_name}' has been accepted!"
        return NotificationModel.create_notification(username, text)
    
    @staticmethod
    def notify_new_solution(crackme_author, crackme_name, solution_author):
        """Create notification for new solution"""
        text = f"A new solution for your crackme '{crackme_name}' has been submitted by: {solution_author}"
        return NotificationModel.create_notification(crackme_author, text)
    
    @staticmethod
    def notify_new_comment(crackme_author, crackme_name, comment_author):
        """Create notification for new comment"""
        text = f"A new comment on your crackme '{crackme_name}' was posted by: {comment_author}"
        return NotificationModel.create_notification(crackme_author, text)