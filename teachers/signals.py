# teachers/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Teacher

@receiver(post_migrate)
def add_teacher_permissions(sender, **kwargs):
    # Optionally, you can restrict this to run only when your app is migrated.
    # For example:
    # if sender.name != 'teachers':
    #     return

    Permission.objects.get_or_create(
        codename='can_assign_teacher',
        name='Can assign teacher to class',
        content_type=ContentType.objects.get_for_model(Teacher),
    )
    Permission.objects.get_or_create(
        codename='can_view_teacher',
        name='Can view teacher details',
        content_type=ContentType.objects.get_for_model(Teacher),
    )
