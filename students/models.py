from django.db import models
from school_class.models import Class
from subjects.models import Subject
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


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
