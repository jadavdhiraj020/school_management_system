from common.mixin import CustomLoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import UserRegisterForm
from .models import Profile
from django.contrib.auth.models import Group

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        user = form.save()
        role = form.cleaned_data.get('role')
        Profile.objects.create(user=user, role=role)
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        login(self.request, user)
        return super().form_valid(form)

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

class LogoutView(CustomLoginRequiredMixin, TemplateView):
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')
