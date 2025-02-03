from django.db import models
from teachers.models import Teacher
from school_class.models import Class

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ('can_view_subject', 'Can view subject'),
            ('can_edit_subject', 'Can edit subject'),
        ]

class ClassTeacherSubject(models.Model):
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="class_teacher_subjects"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="teacher_class_subjects"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="subject_class_subjects"
    )

    class Meta:
        unique_together = ("class_obj", "teacher", "subject")
        constraints = [
            models.UniqueConstraint(
                fields=["class_obj", "teacher", "subject"],
                name="unique_class_teacher_subject",
            )
        ]
        permissions = [
            ('can_assign_subject', 'Can assign subject to class teacher'),
        ]
