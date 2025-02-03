from django.db import models
from students.models import Student
from teachers.models import Teacher
from school_class.models import Class

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=[('Present', 'Present'), ('Absent', 'Absent')]
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

    class Meta:
        permissions = [
            ('can_mark_attendance', 'Can mark attendance'),
            ('can_view_attendance', 'Can view attendance'),
            ('can_edit_attendance', 'Can edit attendance'),
        ]
