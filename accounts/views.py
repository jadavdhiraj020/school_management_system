from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
from core.mixins import RoleRequiredMixin
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class RegisterView(FormView):
    """
    Handles user registration with role-based group assignment.
    """
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        role = form.cleaned_data.get('role')

        # Save user first
        user.save()

        # Assign user to group based on role
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        messages.success(self.request, 'Registration successful! You are now logged in.')
        login(self.request, user)  # Auto login after registration
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors below.')
        return super().form_invalid(form)


class LoginView(FormView):
    """
    Handles user login with Bootstrap-styled forms.
    """
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f'Welcome back, {user.get_username()}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid credentials. Please try again.')
        return super().form_invalid(form)


class LogoutView(TemplateView):
    """
    Handles user logout and redirects to login page.
    """
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(self.request, 'You have been logged out successfully.')
        return redirect('login')
