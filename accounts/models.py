# accounts/models.py

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=7, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} Profile"
