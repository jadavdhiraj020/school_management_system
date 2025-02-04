import random
from django.core.management.base import BaseCommand
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from school_class.models import Class
from django.db import IntegrityError, transaction

class Command(BaseCommand):
    help = "Generate specific subjects and assign them to specific classes with teachers."

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

        # Class assignments mapping
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
                self.stdout.write(self.style.WARNING(f"Class '{class_name}' already exists."))

        # Step 2: Create subjects
        subjects = {}
        for subject_name in subject_names:
            subject_obj, created = Subject.objects.get_or_create(name=subject_name)
            subjects[subject_name] = subject_obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created subject: {subject_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Subject '{subject_name}' already exists."))

        # Step 3: Ensure there are available teachers
        teachers = list(Teacher.objects.all())
        if not teachers:
            self.stdout.write(self.style.ERROR("No teachers available in the database."))
            return

        # Step 4: Assign subjects to classes with teachers
        for class_name, subject_list in subject_mapping.items():
            assigned_class = classes[class_name]
            for subject_name in subject_list:
                subject = subjects[subject_name]

                # Get IDs of teachers already assigned in this class
                assigned_teacher_ids = ClassTeacherSubject.objects.filter(
                    class_obj=assigned_class
                ).values_list('teacher_id', flat=True)
                # Filter available teachers not already assigned in this class
                available_teachers = [teacher for teacher in teachers if teacher.id not in assigned_teacher_ids]
                if not available_teachers:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No available teacher for {subject.name} in {assigned_class.name}. Skipping..."
                        )
                    )
                    continue

                teacher = random.choice(available_teachers)
                try:
                    with transaction.atomic():
                        assignment, created = ClassTeacherSubject.objects.get_or_create(
                            class_obj=assigned_class, teacher=teacher, subject=subject
                        )
                        if created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Assigned {subject.name} to {teacher.user.get_full_name()} in {assigned_class.name}"
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Assignment already exists: {subject.name} with {teacher.user.get_full_name()} in {assigned_class.name}"
                                )
                            )
                except IntegrityError as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to assign {subject.name}: {e}")
                    )
                    continue

        self.stdout.write(self.style.SUCCESS("Subject generation and assignment completed successfully."))
