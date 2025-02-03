from django.db import models
from school_class.models import Class
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from django.core.exceptions import ValidationError


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)

    class Meta:
        unique_together = ("start_time", "end_time")
        ordering = ["start_time"]
        permissions = [
            ("can_view_timeslot", "Can view time slot"),
            ("can_edit_timeslot", "Can edit time slot"),
        ]

    def __str__(self):
        if self.is_break:
            return f"Break: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"


class Timetable(models.Model):
    DAYS_OF_WEEK_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]

    class_model = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="timetables"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="timetables",
        null=True,
        blank=True,
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="timetables",
        null=True,
        blank=True,
    )
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK_CHOICES)

    class Meta:
        unique_together = ("class_model", "time_slot", "day_of_week")
        ordering = ["day_of_week", "time_slot__start_time"]
        permissions = [
            ("can_view_timetable", "Can view timetable"),
            ("can_edit_timetable", "Can edit timetable"),
        ]

    def clean(self):
        if not self.time_slot.is_break:
            overlapping_teachers = Timetable.objects.filter(
                teacher=self.teacher,
                time_slot=self.time_slot,
                day_of_week=self.day_of_week,
            ).exclude(pk=self.pk)
            if overlapping_teachers.exists():
                raise ValidationError(
                    f"Teacher {self.teacher} is already assigned to another class at this time."
                )

            overlapping_subjects = Timetable.objects.filter(
                class_model=self.class_model,
                time_slot=self.time_slot,
                day_of_week=self.day_of_week,
            ).exclude(pk=self.pk)

            if overlapping_subjects.exists():
                raise ValidationError(
                    "This subject is already assigned to the same class and time slot."
                )

            if self.subject and self.teacher:
                if not ClassTeacherSubject.objects.filter(
                    teacher=self.teacher,
                    subject=self.subject,
                    class_obj=self.class_model,
                ).exists():
                    raise ValidationError(
                        f"Teacher {self.teacher} is not qualified to teach {self.subject} in this class."
                    )

        if self.time_slot.is_break:
            if self.subject or self.teacher:
                raise ValidationError(
                    "Break slots cannot be assigned subjects or teachers."
                )
        elif not self.time_slot.is_break and not (self.subject and self.teacher):
            raise ValidationError(
                "Subject and Teacher are required for non-break slots."
            )

    def __str__(self):
        if self.time_slot.is_break:
            return f"{self.day_of_week} - {self.time_slot} (Break)"
        return f"{self.class_model.name} - {self.subject.name} by {self.teacher.name} on {self.day_of_week} at {self.time_slot}"
