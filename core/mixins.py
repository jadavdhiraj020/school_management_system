# core/mixins.py
import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

# Initialize logger for tracking unauthorized access
logger = logging.getLogger(__name__)

class RoleRequiredMixin(UserPassesTestMixin):
    """
    A mixin to restrict access based on user roles.
    - Ensures only allowed roles or superusers can access views.
    - Redirects unauthorized users with appropriate messages.
    - Logs unauthorized access attempts.
    """
    allowed_roles = []
    redirect_url = 'login'  # Default redirect for unauthorized users

    def test_func(self):
        """Check if the user is allowed to access the view."""
        try:
            request = getattr(self, "request", None)  # Ensure request is accessible
            if not request:
                logger.error("RoleRequiredMixin: self.request is not available.")
                return False  # Deny access if request is missing

            user = request.user  # Get user from request

            if not user.is_authenticated:
                logger.warning(f"Unauthorized access attempt: Anonymous user tried to access {request.path}")
                return False  # User not logged in

            if user.is_superuser or user.role in self.allowed_roles:
                return True  # Authorized user

            logger.warning(f"Unauthorized access: {user.username} ({user.role}) tried to access {request.path}")
            return False  # Access denied due to role restriction

        except Exception as e:
            logger.error(f"Error in RoleRequiredMixin: {str(e)}")
            return False  # Default to denying access on error

    def handle_no_permission(self):
        """Handle unauthorized access."""
        request = getattr(self, "request", None)  # Ensure request is accessible
        if not request:
            return HttpResponseForbidden("<h1>403 Forbidden</h1><p>Request object missing.</p>")

        user = request.user

        # Handle unauthenticated users
        if not user.is_authenticated:
            messages.warning(request, "You need to log in to access this page.")
            return redirect(self.redirect_url)

        # Handle unauthorized users
        messages.error(request, "You do not have permission to access this page.")
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You are not authorized to view this page.</p>")
