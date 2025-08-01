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


class OffensiveLanguageMiddleware:
    """
    Middleware that limits the number of chat messages a user can send within a certain time window,
    based on their IP address. Blocks users who exceed 5 messages per minute.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        # Dictionary to store IP addresses and their message timestamps
        # Format: {ip_address: [timestamp1, timestamp2, ...]}
        self.ip_message_history = {}
        self.max_messages = 5  # Maximum messages allowed
        self.time_window = 60  # Time window in seconds (1 minute)
    
    def __call__(self, request):
        """
        Process the request and check for rate limiting on POST requests.
        Args:
            request: The HTTP request object
        Returns:
            The response from the next middleware/view or an error response
        """
        # Only check POST requests (chat messages)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = datetime.now()
            
            # Initialize IP history if not exists
            if ip_address not in self.ip_message_history:
                self.ip_message_history[ip_address] = []
            
            # Clean old timestamps outside the time window
            self.clean_old_timestamps(ip_address, current_time)
            
            # Check if user has exceeded the limit
            if len(self.ip_message_history[ip_address]) >= self.max_messages:
                # Block the request and return error
                from django.http import JsonResponse
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded. You can only send 5 messages per minute.',
                        'detail': f'Please wait before sending another message.'
                    },
                    status=429  # Too Many Requests
                )
            
            # Add current timestamp to history
            self.ip_message_history[ip_address].append(current_time)
        
        # Continue processing the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        Handles cases where the request comes through a proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def clean_old_timestamps(self, ip_address, current_time):
        """
        Remove timestamps that are outside the time window.
        Args:
            ip_address: The IP address to clean
            current_time: Current datetime object
        """
        if ip_address in self.ip_message_history:
            # Filter out timestamps older than the time window
            cutoff_time = current_time.timestamp() - self.time_window
            self.ip_message_history[ip_address] = [
                timestamp for timestamp in self.ip_message_history[ip_address]
                if timestamp.timestamp() > cutoff_time
            ]
