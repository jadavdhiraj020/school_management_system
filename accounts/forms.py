# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
    )
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
