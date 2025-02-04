from django.db import models
from accounts.models import CustomUser  # Importing CustomUser from users app
from school_class.models import Class
from subjects.models import Subject
from django.core.validators import MinValueValidator, MaxValueValidator

class Student(models.Model):
    """
    Student Model representing students enrolled in school.
    - Linked with `CustomUser` for authentication.
    - Linked with `Class` (ForeignKey) and `Subject` (ManyToManyField).
    """
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
        """Return full name if available, otherwise username."""
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        """Override save method for data validation and consistency."""
        self.user.first_name = self.user.first_name.capitalize()
        self.user.last_name = self.user.last_name.capitalize()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [models.Index(fields=["user"])]
        permissions = [
            ("can_view_student", "Can view student"),
            ("can_edit_student", "Can edit student"),
        ]
