from django.db import models
from accounts.models import CustomUser
from school_class.models import Class
from subjects.models import Subject
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student_profile",
        help_text="The user associated with this student."
    )
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(12), MaxValueValidator(25)],
        help_text="Age must be between 12 and 25."
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        help_text="Optional phone number."
    )
    address = models.TextField(help_text="Home address of the student.")
    enrollment_date = models.DateField(
        auto_now_add=True,
        help_text="Date when student was enrolled."
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students",
        help_text="The class this student is enrolled in."
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="students",
        blank=True,
        help_text="Subjects the student is studying."
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        # Capitalize and save user names
        self.user.first_name = self.user.first_name.strip().capitalize()
        self.user.last_name = self.user.last_name.strip().capitalize()
        self.user.save()  # Save user changes first
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [models.Index(fields=["user"])]
        permissions = [
            ("can_view_student", "Can view student"),
            ("can_edit_student", "Can edit student"),
        ]
