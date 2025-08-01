from django.db import models


class UnreadMessagesManager(models.Manager):
    """Custom manager for filtering unread messages"""
    
    def for_user(self, user):
        """Get unread messages for a specific user"""
        return self.get_queryset().filter(
            receiver=user, 
            read=False
        ).only('id', 'sender', 'content', 'timestamp')
    
    def mark_as_read(self, user):
        """Mark all unread messages for user as read"""
        return self.for_user(user).update(read=True)
    
    def count_unread(self, user):
        """Count unread messages for a user"""
        return self.for_user(user).count()
    
    def get_unread_by_sender(self, user, sender):
        """Get unread messages from a specific sender"""
        return self.for_user(user).filter(sender=sender)