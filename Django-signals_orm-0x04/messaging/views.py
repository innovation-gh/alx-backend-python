from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch, Q
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

@login_required
def inbox(request):
    """Display user's inbox with unread messages using custom manager"""
    # Use custom manager with .only() optimization
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Additional optimization with .only() for related fields
    all_messages = Message.objects.filter(
        receiver=request.user
    ).only('id', 'sender', 'content', 'timestamp', 'read').order_by('-timestamp')
    
    context = {
        'unread_messages': unread_messages,
        'unread_count': unread_messages.count(),
        'all_messages': all_messages
    }
    return render(request, 'messaging/inbox.html', context)

@cache_page(60)  # Cache for 60 seconds
@login_required
def conversation_view(request, conversation_id):
    """Display a conversation with threaded replies using optimized queries"""
    # Get main messages and their replies efficiently
    messages = Message.objects.filter(
        Q(id=conversation_id) | Q(parent_message_id=conversation_id)
    ).select_related(
        'sender', 'receiver', 'parent_message'
    ).prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender'))
    ).order_by('timestamp')
    
    context = {
        'messages': messages,
        'conversation_id': conversation_id
    }
    return render(request, 'messaging/conversation.html', context)

@login_required
def threaded_messages(request):
    """Display messages sent by current user with their threading structure"""
    # Get messages sent by the current user with optimized queries and .only()
    user_messages = Message.objects.filter(
        sender=request.user
    ).select_related(
        'receiver', 'parent_message'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
        )
    ).only(
        'id', 'receiver', 'parent_message', 'content', 'timestamp', 'edited'
    ).order_by('-timestamp')
    
    # Get unread messages for user's inbox using custom manager
    unread_messages = Message.unread.unread_for_user(request.user)
    
    context = {
        'user_messages': user_messages,
        'unread_messages': unread_messages
    }
    return render(request, 'messaging/threaded_messages.html', context)

@login_required
def sent_messages(request):
    """Display all messages sent by the current user with replies"""
    # Messages sent by current user with optimized loading using .only()
    sent_messages = Message.objects.filter(
        sender=request.user
    ).select_related(
        'receiver'
    ).prefetch_related(
        'replies__sender',
        'replies__receiver'
    ).only(
        'id', 'receiver', 'content', 'timestamp', 'edited', 'read'
    ).order_by('-timestamp')
    
    # Also get unread messages using custom manager
    unread_messages = Message.unread.unread_for_user(request.user)
    
    context = {
        'sent_messages': sent_messages,
        'unread_messages': unread_messages
    }
    return render(request, 'messaging/sent_messages.html', context)

@login_required
def message_history(request, message_id):
    """Display edit history for a specific message"""
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    # Get message history with user information
    history = MessageHistory.objects.filter(
        message=message
    ).select_related(
        'edited_by'
    ).order_by('-edited_at')
    
    context = {
        'message': message,
        'history': history
    }
    return render(request, 'messaging/message_history.html', context)

@login_required
def user_conversations(request):
    """Display all conversations for current user with optimized queries"""
    # Get root messages (no parent) where user is sender or receiver
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        parent_message__isnull=True
    ).select_related(
        'sender', 'receiver'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
        )
    ).order_by('-timestamp')
    
    context = {
        'conversations': conversations
    }
    return render(request, 'messaging/conversations.html', context)

@login_required
def delete_user(request):
    """Delete user account and trigger cleanup signals"""
    if request.method == 'POST':
        user = request.user
        user.delete()  # This triggers the post_delete signal
        return redirect('login')
    
    return render(request, 'messaging/delete_confirm.html')

@login_required
def my_message_threads(request):
    """Display threaded conversations started by the current user"""
    # Get messages where current user is sender, optimized with select_related and prefetch_related
    my_threads = Message.objects.filter(
        sender=request.user,
        parent_message__isnull=True  # Only root messages
    ).select_related(
        'receiver'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver')
        )
    ).order_by('-timestamp')
    
    context = {
        'my_threads': my_threads
    }
    return render(request, 'messaging/my_threads.html', context)