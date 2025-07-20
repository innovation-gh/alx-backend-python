from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic user information
    """
    full_name = serializers.CharField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.CharField(max_length=254)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'full_name']
    
    def to_representation(self, instance):
        """Add computed full_name to representation"""
        data = super().to_representation(instance)
        data['full_name'] = f"{instance.first_name} {instance.last_name}".strip()
        return data


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model with sender information
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    message_body = serializers.CharField(max_length=1000)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_id', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sent_at']
    
    def validate_sender_id(self, value):
        """Validate that the sender exists"""
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender ID")


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with participants and messages
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_ids', 'messages', 
            'message_count', 'last_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_message_count(self, obj):
        """Return the total number of messages in the conversation"""
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """Return the most recent message in the conversation"""
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            return {
                'id': last_msg.id,
                'sender': last_msg.sender.username,
                'message_body': last_msg.message_body,
                'sent_at': last_msg.sent_at
            }
        return None
    
    def validate_participant_ids(self, value):
        """Validate that all participant IDs exist and there are at least 2 participants"""
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants")
        
        # Check if all users exist
        existing_users = User.objects.filter(id__in=value)
        if existing_users.count() != len(value):
            raise serializers.ValidationError("One or more participant IDs are invalid")
        
        return value
    
    def create(self, validated_data):
        """Create a conversation with participants"""
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            participants = User.objects.filter(id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation
    
    def update(self, instance, validated_data):
        """Update conversation and handle participant updates"""
        participant_ids = validated_data.pop('participant_ids', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update participants if provided
        if participant_ids is not None:
            participants = User.objects.filter(id__in=participant_ids)
            instance.participants.set(participants)
        
        return instance


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for conversation lists (without nested messages)
    """
    participants = UserSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'message_count', 'last_message', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_message_count(self, obj):
        """Return the total number of messages in the conversation"""
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """Return the most recent message in the conversation"""
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            return {
                'id': last_msg.id,
                'sender': last_msg.sender.username,
                'message_body': last_msg.message_body[:50] + '...' if len(last_msg.message_body) > 50 else last_msg.message_body,
                'sent_at': last_msg.sent_at
            }
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating messages
    """
    sender_id = serializers.IntegerField(write_only=True)
    conversation_id = serializers.IntegerField(write_only=True)
    message_body = serializers.CharField(max_length=1000)
    
    class Meta:
        model = Message
        fields = ['sender_id', 'conversation_id', 'message_body']
    
    def validate_sender_id(self, value):
        """Validate that the sender exists"""
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid sender ID")
    
    def validate_conversation_id(self, value):
        """Validate that the conversation exists"""
        try:
            Conversation.objects.get(id=value)
            return value
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Invalid conversation ID")
    
    def validate(self, data):
        """Validate that the sender is a participant in the conversation"""
        try:
            conversation = Conversation.objects.get(id=data['conversation_id'])
            sender = User.objects.get(id=data['sender_id'])
            
            if not conversation.participants.filter(id=sender.id).exists():
                raise serializers.ValidationError(
                    "Sender must be a participant in the conversation"
                )
        except (Conversation.DoesNotExist, User.DoesNotExist):
            pass  # These will be caught by individual field validators
        
        return data
    
    def create(self, validated_data):
        """Create a message"""
        sender = User.objects.get(id=validated_data.pop('sender_id'))
        conversation = Conversation.objects.get(id=validated_data.pop('conversation_id'))
        
        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            **validated_data
        )
        return message