"""
URL configuration for chats app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .auth import (
    RegisterView, 
    LogoutView, 
    UserProfileView, 
    ChangePasswordView,
    current_user
)

# Create a router for ViewSets
router = DefaultRouter()
# Add your ViewSets here when you create them
# router.register(r'conversations', views.ConversationViewSet)
# router.register(r'messages', views.MessageViewSet)
# router.register(r'users', views.UserViewSet)

urlpatterns = [
    # Authentication endpoints (additional to JWT)
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/me/', current_user, name='current_user'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Custom endpoints (examples - uncomment when you have the views)
    # path('conversations/', views.ConversationListCreateView.as_view(), name='conversation_list'),
    # path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    # path('conversations/<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message_list'),
    # path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
]