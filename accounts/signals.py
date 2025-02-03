# accounts/signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile with a default role (e.g., 'Student')
        Profile.objects.create(user=instance, role='Student')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure the related profile is saved whenever the User is saved
    instance.profile.save()
