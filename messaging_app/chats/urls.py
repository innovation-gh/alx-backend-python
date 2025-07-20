from django.urls import path, include
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet

# Create a DefaultRouter for conversations
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Create a nested router for messages under conversations
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]

app_name = 'chats'