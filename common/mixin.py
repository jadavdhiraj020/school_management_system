from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated.
    If not, redirect to the login page with an error message.
    """
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class CustomPermissionRequiredMixin(AccessMixin):
    """
    Verify that the current user has the required permissions.
    If not, redirect to a safe URL (e.g., home) with an error message.
    """
    # Set permission_required as a string or a list of permission codenames.
    permission_required = None

    def dispatch(self, request, *args, **kwargs):
        perms = self.get_permission_required()
        if not request.user.has_perms(perms):
            messages.error(request, "You do not have permission to view this page.")
            return redirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)

    def get_permission_required(self):
        if isinstance(self.permission_required, str):
            return (self.permission_required,)
        return self.permission_required
