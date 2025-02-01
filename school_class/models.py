from django.db import models
from teachers.models import Teacher

class Class(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class_teacher = models.OneToOneField(
        Teacher, on_delete=models.SET_NULL, null=True, related_name="managed_classes"
    )
    teachers = models.ManyToManyField(
        Teacher,
        related_name="teaching_classes",
        through="subjects.ClassTeacherSubject",
        through_fields=("class_obj", "teacher"),
    )
    subjects = models.ManyToManyField(
        "subjects.Subject",
        related_name="classes",
        through="subjects.ClassTeacherSubject",
        through_fields=("class_obj", "subject"),
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_class_name")
        ]
