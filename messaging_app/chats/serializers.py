"""
Serializers for the chats app.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - used for profile views.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        """
        Check that the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """
        Check that the username is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate(self, attrs):
        """
        Check that passwords match and validate password strength.
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        """
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (limited information).
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def validate_email(self, value):
        """
        Check that the email is unique (excluding current user).
        """
        user = self.instance
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """
        Check that new passwords match and validate password strength.
        """
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs


# Additional serializers for messaging functionality
class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    """
    participants = UserListSerializer(many=True, read_only=True)
    participants_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = None  # Will be set when you have the Conversation model
        fields = '__all__'  # Adjust based on your model fields
    
    def create(self, validated_data):
        """
        Create conversation with participants.
        """
        participants_ids = validated_data.pop('participants_ids', [])
        conversation = super().create(validated_data)
        
        # Add participants
        if participants_ids:
            participants = User.objects.filter(id__in=participants_ids)
            conversation.participants.set(participants)
        
        # Add creator as participant
        conversation.participants.add(self.context['request'].user)
        
        return conversation


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    """
    sender = UserListSerializer(read_only=True)
    
    class Meta:
        model = None  # Will be set when you have the Message model
        fields = '__all__'  # Adjust based on your model fields
        read_only_fields = ('sender', 'timestamp')
    
    def create(self, validated_data):
        """
        Create message with sender set to current user.
        """
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)