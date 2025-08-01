import logging
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

# Configure logger for request logging
logger = logging.getLogger('request_logging')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log each user's requests with timestamp, user, and request path.
    """
    
    def __init__(self, get_response=None):
        """
        Initialize the middleware.
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        """
        Process the request and log user activity.
        Args:
            request: The HTTP request object
        Returns:
            The response from the next middleware/view
        """
        # Get the user (handle both authenticated and anonymous users)
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username or f"User-{request.user.id}"
        else:
            user = "Anonymous"
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Continue processing the request
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access based on time constraints.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and apply time-based restrictions.
        Args:
            request: The HTTP request object
        Returns:
            The response from the next middleware/view
        """
        # Add your time-based access logic here
        # For now, just pass through to the next middleware/view
        response = self.get_response(request)
        return response
