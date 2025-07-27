from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    UserSerializer
)

# ✅ Import custom permissions
from .permissions import (
    MessagePermissions,
    ConversationPermissions,
    CanViewUserList,
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    Provides CRUD operations for conversations and related actions
    """
    permission_classes = [ConversationPermissions]  # ✅ Use custom permission
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['participants', 'created_at']
    search_fields = ['participants__username', 'participants__first_name', 'participants__last_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.select_related('sender'))
        ).distinct().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participant_ids = request.data.get('participant_ids', [])
        if request.user.id not in participant_ids:
            participant_ids.append(request.user.id)

        if len(participant_ids) < 2:
            return Response(
                {'error': 'A conversation must have at least 2 participants'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = serializer.save()
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.set(participants)

        return_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add-participant')
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            conversation.participants.add(user)
            serializer = ConversationSerializer(conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove-participant')
    def remove_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if conversation.participants.count() <= 2:
            return Response(
                {'error': 'Cannot remove participant. Conversation must have at least 2 participants'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
            conversation.participants.remove(user)
            serializer = ConversationSerializer(conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='messages')
    def get_messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender').order_by('sent_at')
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    Provides CRUD operations for messages
    """
    serializer_class = MessageSerializer
    permission_classes = [MessagePermissions]  # ✅ Use custom permission
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sender', 'sent_at']
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation').order_by('-sent_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation_id = request.data.get('conversation_id')

        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if not conversation.participants.filter(id=request.user.id).exists():
                return Response({'error': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=request.data.get('message_body', '')
        )

        return_serializer = MessageSerializer(message, context={'request': request})
        return Response(return_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        conversation_id = request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)

        sender_id = request.query_params.get('sender_id')
        if sender_id:
            queryset = queryset.filter(sender_id=sender_id)

        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(message_body__icontains=search)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response({'error': 'You can only update your own messages'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response({'error': 'You can only delete your own messages'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_messages(self, request):
        queryset = self.get_queryset()[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        return Response({'message': f'Message {message.id} marked as read'}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user information (read-only)
    Used for getting user details for conversation participants
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [CanViewUserList]  # ✅ Use custom permission
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['username', 'first_name', 'last_name']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']

    @action(detail=False, methods=['get'], url_path='search')
    def search_users(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response({'error': 'Search query must be at least 2 characters'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
