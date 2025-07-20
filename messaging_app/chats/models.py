from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    # Override the default id with UUID
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    
    # These fields are already in AbstractUser, but we'll ensure they're required
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False, db_index=True)
    
    # Additional fields not in AbstractUser
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Override username to use email instead
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Conversation(models.Model):
    """
    Model to track conversations between users
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'conversations'
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        participant_names = ", ".join([str(user) for user in self.participants.all()[:3]])
        if self.participants.count() > 3:
            participant_names += "..."
        return f"Conversation: {participant_names}"


class Message(models.Model):
    """
    Model for individual messages within conversations
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        db_column='sender_id'
    )
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        db_column='conversation_id'
    )
    message_body = models.TextField(blank=False, null=False)
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'messages'
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
        ]
        ordering = ['-sent_at']  # Most recent messages first
    
    def __str__(self):
        return f"Message from {self.sender.first_name}: {self.message_body[:50]}..."

# Create your models here.
