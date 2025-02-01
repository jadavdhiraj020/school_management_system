from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Student
from subjects.models import Subject

@receiver(post_save, sender=Student)
def assign_subjects_to_student(sender, instance, created, **kwargs):
    if created and instance.class_obj:
        subject_mapping = {
            "12th Science A Groups": ["Mathematics", "Physics", "Chemistry", "Computer", "English"],
            "12th Science B Groups": ["Physics", "Chemistry", "Biology", "Computer", "English"],
        }

        subject_names = subject_mapping.get(instance.class_obj.name, [])
        if subject_names:
            subjects = Subject.objects.filter(name__in=subject_names)
            if subjects.exists():
                instance.subjects.set(subjects)
