from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch, Q
from .models import Message, Notification

@login_required
def inbox(request):
    """Display user's inbox with unread messages"""
    unread_messages = Message.unread.for_user(request.user)
    
    context = {
        'unread_messages': unread_messages,
        'unread_count': unread_messages.count()
    }
    return render(request, 'messaging/inbox.html', context)

@cache_page(60)  # Cache for 60 seconds
@login_required
def conversation_view(request, conversation_id):
    """Display a conversation with threaded replies"""
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
    """Display messages with their threading structure"""
    # Get root messages (no parent) with their replies
    root_messages = Message.objects.filter(
        parent_message__isnull=True,
        receiver=request.user
    ).select_related('sender').prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender').order_by('timestamp')
        )
    )
    
    context = {'root_messages': root_messages}
    return render(request, 'messaging/threaded.html', context)

@login_required
def delete_user(request):
    """Delete user account and trigger cleanup signals"""
    if request.method == 'POST':
        user = request.user
        user.delete()  # This triggers the post_delete signal
        return redirect('login')
    
    return render(request, 'messaging/delete_confirm.html')