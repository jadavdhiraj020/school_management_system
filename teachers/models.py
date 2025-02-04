from django.db import models
from accounts.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Teacher(models.Model):
    """
    Teacher Model representing teachers in the school.
    - Linked with `CustomUser` for authentication.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        help_text="The user associated with this teacher."
    )
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(22), MaxValueValidator(65)],
        help_text="Age must be between 22 and 65."
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        help_text="Optional phone number."
    )
    address = models.TextField(help_text="Home address of the teacher.")
    joining_date = models.DateField(
        auto_now_add=True,
        help_text="Date when teacher joined."
    )
    subject = models.ManyToManyField(
        'subjects.Subject',
        related_name="teachers",
        blank=True,
        help_text="Subjects the teacher is teaching."
    )

    @property
    def name(self):
        # This property mimics a 'name' attribute for compatibility.
        return self.user.get_full_name() or self.user.username

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        self.user.first_name = self.user.first_name.capitalize()
        self.user.last_name = self.user.last_name.capitalize()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        indexes = [models.Index(fields=["user"])]
        permissions = [
            ("can_view_teacher", "Can view teacher"),
            ("can_edit_teacher", "Can edit teacher"),
        ]
