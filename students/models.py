from django.db import models
from school_class.models import Class
from subjects.models import Subject

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    enrollment_date = models.DateField(auto_now_add=True)
    class_obj = models.ForeignKey(
        Class, on_delete=models.SET_NULL, null=True, related_name="students"
    )
    subjects = models.ManyToManyField(Subject, related_name="students", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        permissions = [
            ('can_view_student', 'Can view student'),
            ('can_edit_student', 'Can edit student'),
        ]
