"""
Custom permissions for the chats app to ensure users can only access their own data.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow access to the owner of the object
        return obj.owner == request.user


class IsMessageOwnerOrConversationParticipant(permissions.BasePermission):
    """
    Permission for messages: allow access if user is the message sender
    or a participant in the conversation.
    """
    def has_object_permission(self, request, view, obj):
        # Allow access if user is the message sender
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True
        
        # Allow access if user is a participant in the conversation
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        
        return False


class IsConversationParticipant(permissions.BasePermission):
    """
    Permission for conversations: allow access only to participants.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return obj.participants.filter(id=request.user.id).exists()

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated


class CanCreateMessage(permissions.BasePermission):
    """
    Permission to check if user can create a message in a conversation.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For creating messages, check if user is participant in the conversation
        if request.method == 'POST':
            conversation_id = request.data.get('conversation_id') or view.kwargs.get('conversation_id')
            if conversation_id:
                from .models import Conversation  # Import here to avoid circular imports
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    return conversation.participants.filter(id=request.user.id).exists()
                except Conversation.DoesNotExist:
                    return False
        
        return True


class IsUserProfile(permissions.BasePermission):
    """
    Permission to check if user is accessing their own profile.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow users to access their own profile
        return obj == request.user


class CanViewUserList(permissions.BasePermission):
    """
    Permission to control who can view the user list.
    Only authenticated users can view limited user information.
    """
    def has_permission(self, request, view):
        # Only authenticated users can view user list
        return request.user and request.user.is_authenticated


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission that allows access to admins or owners of the object.
    """
    def has_object_permission(self, request, view, obj):
        # Allow access to admin users
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Allow access to owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class CanDeleteOwnMessage(permissions.BasePermission):
    """
    Permission to allow users to delete only their own messages.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            # Only allow message sender to delete the message
            return hasattr(obj, 'sender') and obj.sender == request.user
        
        return True


class ConversationPermissionMixin:
    """
    Mixin to add conversation-based permissions to views.
    """
    def get_queryset(self):
        """
        Filter queryset to only include conversations where user is a participant.
        """
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.filter(participants=self.request.user)
        return super().get_queryset().filter(participants=self.request.user)


class MessagePermissionMixin:
    """
    Mixin to add message-based permissions to views.
    """
    def get_queryset(self):
        """
        Filter queryset to only include messages from conversations where user is a participant.
        """
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.filter(conversation__participants=self.request.user)
        return super().get_queryset().filter(conversation__participants=self.request.user)


# Custom permission classes combinations
class MessagePermissions(permissions.BasePermission):
    """
    Combined permission class for message operations.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # For reading messages
        if request.method in permissions.SAFE_METHODS:
            return obj.conversation.participants.filter(id=request.user.id).exists()
        
        # For updating/deleting messages
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
        
        return False


class ConversationPermissions(permissions.BasePermission):
    """
    Combined permission class for conversation operations.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # User must be a participant in the conversation
        return obj.participants.filter(id=request.user.id).exists()


# Utility functions for permission checking
def user_can_access_conversation(user, conversation):
    """
    Check if a user can access a specific conversation.
    """
    return conversation.participants.filter(id=user.id).exists()


def user_can_access_message(user, message):
    """
    Check if a user can access a specific message.
    """
    return message.conversation.participants.filter(id=user.id).exists()


def user_owns_message(user, message):
    """
    Check if a user owns (sent) a specific message.
    """
    return message.sender == user