from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def assign_default_role(sender, instance, created, **kwargs):
    if created and not instance.role:
        # Assign the default role as 'student' if not explicitly set
        instance.role = 'student'
        instance.save()
