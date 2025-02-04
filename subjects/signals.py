# subjects/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Subject

@receiver(post_migrate)
def add_subject_permissions(sender, **kwargs):
    # Optionally, check if the sender is the subjects app:
    # if sender.name != 'subjects':
    #     return

    content_type = ContentType.objects.get_for_model(Subject)
    Permission.objects.get_or_create(
        codename='can_assign_subject',
        name='Can assign subject to class teacher',
        content_type=content_type,
    )
    print("Subject permissions added.")
