from django.core.management.base import BaseCommand
from students.models import Student
from teachers.models import Teacher
from school_class.models import Class
from subjects.models import Subject, ClassTeacherSubject
from django.db.utils import IntegrityError
from django.db import transaction
import random


class Command(BaseCommand):
    help = "Generate classes with teachers, subjects, and assign students"

    def handle(self, *args, **kwargs):
        teachers = Teacher.objects.all()
        students = Student.objects.all()
        subjects = Subject.objects.all()

        if not teachers.exists():
            self.stdout.write(
                self.style.ERROR("No teachers found! Please create teachers first.")
            )
            return

        if not students.exists():
            self.stdout.write(
                self.style.ERROR("No students found! Please create students first.")
            )
            return

        if not subjects.exists():
            self.stdout.write(
                self.style.ERROR("No subjects found! Please create subjects first.")
            )
            return

        class_names = [
            "12th Science A Groups",
            "12th Science B Groups",
        ]

        used_teachers_as_class_teacher = set()

        for class_name in class_names:
            if not Class.objects.filter(name=class_name).exists():
                # Assign a random teacher as the class teacher who hasn't already been used
                available_teachers = teachers.exclude(
                    id__in=used_teachers_as_class_teacher
                ).order_by("?")
                if not available_teachers.exists():
                    self.stdout.write(
                        self.style.ERROR(
                            "Not enough teachers available for assigning as class teachers!"
                        )
                    )
                    return

                class_teacher = available_teachers.first()
                used_teachers_as_class_teacher.add(class_teacher.id)

                # Create the class with a class teacher
                class_instance = Class.objects.create(
                    name=class_name,
                    class_teacher=class_teacher,
                )

                # Assign subjects to the class
                # For simplicity, assign all available subjects
                class_subjects = list(
                    subjects.order_by("?")[:6]
                )  # Adjust the number as needed

                # For each subject, assign a random teacher
                for subject in class_subjects:
                    # Select a random teacher
                    teaching_teacher = random.choice(teachers)

                    try:
                        with transaction.atomic():
                            # Create the ClassTeacherSubject entry
                            ClassTeacherSubject.objects.create(
                                class_obj=class_instance,
                                teacher=teaching_teacher,
                                subject=subject,
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Assigned subject '{subject.name}' to class '{class_name}' with teacher '{teaching_teacher.name}'."
                                )
                            )
                    except IntegrityError as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to assign subject '{subject.name}' to class '{class_name}': {e}"
                            )
                        )
                        continue

                # Assign up to 50 random students to the class
                students_for_class = students.filter(class_obj__isnull=True).order_by(
                    "?"
                )[:50]
                for student in students_for_class:
                    student.class_obj = class_instance
                    student.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created class: "{class_name}" with class teacher: {class_teacher.name}, '
                        f"{len(class_subjects)} subjects assigned, and {students_for_class.count()} students."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Class "{class_name}" already exists, skipping.'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully generated classes with teachers, subjects, and students!"
            )
        )
