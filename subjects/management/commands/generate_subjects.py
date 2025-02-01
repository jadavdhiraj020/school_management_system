import random
from django.core.management.base import BaseCommand
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from school_class.models import Class
from django.db.utils import IntegrityError
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Generate specific subjects and assign them to specific classes with teachers."
    )

    def handle(self, *args, **kwargs):
        # Subject names
        subject_names = [
            "Chemistry",
            "English",
            "Physics",
            "Mathematics",
            "Biology",
            "Computer",
        ]

        # Class assignments
        subject_mapping = {
            "12th Science A Groups": [
                "Mathematics",
                "Chemistry",
                "English",
                "Physics",
                "Computer",
            ],
            "12th Science B Groups": [
                "Biology",
                "Chemistry",
                "English",
                "Physics",
                "Computer",
            ],
        }

        # Step 1: Ensure classes exist
        class_names = ["12th Science A Groups", "12th Science B Groups"]
        classes = {}

        for class_name in class_names:
            class_obj, created = Class.objects.get_or_create(name=class_name)
            classes[class_name] = class_obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created class: {class_name}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Class '{class_name}' already exists.")
                )

        # Step 2: Create subjects
        subjects = {}
        for subject_name in subject_names:
            subject_obj, created = Subject.objects.get_or_create(name=subject_name)
            subjects[subject_name] = subject_obj
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created subject: {subject_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Subject '{subject_name}' already exists.")
                )

        # Step 3: Ensure there are enough teachers
        teachers = list(Teacher.objects.all())
        if not teachers:
            self.stdout.write(
                self.style.ERROR("No teachers available in the database.")
            )
            return

        # Step 4: Assign subjects to classes with teachers
        for class_name, subject_list in subject_mapping.items():
            assigned_class = classes[class_name]

            for subject_name in subject_list:
                subject = subjects[subject_name]

                # Assign a random teacher to the subject for the class
                # Ensure that the teacher is not assigned to another subject in the same class
                existing_assignments = ClassTeacherSubject.objects.filter(
                    class_obj=assigned_class, teacher__id=teachers[0].id
                )

                if existing_assignments.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Teacher {teachers[0].name} already assigned to another subject in this class. Skipping..."
                        )
                    )
                    continue

                teacher = random.choice(teachers)
                try:
                    with transaction.atomic():
                        assignment, created = ClassTeacherSubject.objects.get_or_create(
                            class_obj=assigned_class, teacher=teacher, subject=subject
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Assigned {subject.name} to {teacher.name} in {assigned_class.name}"
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Assignment already exists: {subject.name} with {teacher.name} in {assigned_class.name}"
                                )
                            )
                except IntegrityError as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to assign {subject.name}: {e}")
                    )
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                "Subject generation and assignment completed successfully."
            )
        )
