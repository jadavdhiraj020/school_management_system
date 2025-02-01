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


from django.db import models
from teachers.models import Teacher
from school_class.models import Class
from django.db.models import UniqueConstraint


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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
            UniqueConstraint(
                fields=["class_obj", "teacher", "subject"],
                name="unique_class_teacher_subject",
            )
        ]


from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


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
