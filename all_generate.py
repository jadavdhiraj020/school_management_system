from django.core.management.base import BaseCommand
from teachers.models import Teacher
import random
from faker import Faker
from django.db.utils import IntegrityError
from datetime import date


class Command(BaseCommand):
    help = "Generate random teacher data."

    def add_arguments(self, parser):
        parser.add_argument(
            "number",
            type=int,
            nargs="?",
            default=12,
            help="Number of teachers to generate (default: 12)",
        )
        # Optional arguments for age range
        parser.add_argument(
            "--min-age",
            type=int,
            default=25,
            help="Minimum age of teachers (default: 25)",
        )
        parser.add_argument(
            "--max-age",
            type=int,
            default=60,
            help="Maximum age of teachers (default: 60)",
        )

    def handle(self, *args, **options):
        number = options["number"]
        min_age = options["min_age"]
        max_age = options["max_age"]

        if min_age > max_age:
            self.stdout.write(
                self.style.ERROR("Minimum age cannot be greater than maximum age.")
            )
            return

        fake = Faker()
        Faker.seed(0)  # Seed for reproducibility
        fake.unique.clear()  # Clear unique generator
        created_count = 0
        attempt = 0
        max_attempts = number * 2  # To prevent infinite loops

        while created_count < number and attempt < max_attempts:
            attempt += 1
            name = fake.name()
            email = fake.unique.email()
            age = random.randint(min_age, max_age)
            phone = fake.phone_number()[:15]
            address = fake.address()
            joining_date = fake.date_between(start_date="-10y", end_date=date.today())

            try:
                teacher = Teacher.objects.create(
                    name=name,
                    email=email,
                    age=age,
                    phone=phone,
                    address=address,
                    joining_date=joining_date,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created teacher: {name}"))
            except IntegrityError as e:
                # Handle potential unique constraint violations
                fake.unique.clear()  # Reset unique generator in case of duplicate email
                self.stdout.write(
                    self.style.ERROR(f"Failed to create teacher {name}: {e}")
                )
                continue

        if created_count < number:
            self.stdout.write(
                self.style.WARNING(
                    f"Only created {created_count} teachers out of requested {number} due to constraints."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {created_count} teachers.")
            )


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


from django.core.management.base import BaseCommand
from students.models import Student
from school_class.models import Class
from subjects.models import Subject
import random
from faker import Faker
from django.db.utils import IntegrityError
from datetime import date

class Command(BaseCommand):
    help = "Generate random student data."

    def add_arguments(self, parser):
        parser.add_argument(
            "number",
            type=int,
            nargs="?",
            default=100,
            help="Number of students to generate (default: 100)",
        )
        # Optional arguments for age range
        parser.add_argument(
            "--min-age",
            type=int,
            default=15,
            help="Minimum age of students (default: 15)",
        )
        parser.add_argument(
            "--max-age",
            type=int,
            default=25,
            help="Maximum age of students (default: 25)",
        )

    def handle(self, *args, **options):
        number = options["number"]
        min_age = options["min_age"]
        max_age = options["max_age"]

        if min_age > max_age:
            self.stdout.write(
                self.style.ERROR("Minimum age cannot be greater than maximum age.")
            )
            return

        fake = Faker()
        Faker.seed(0)  # Seed for reproducibility
        fake.unique.clear()  # Clear unique generator

        # Define the classes and their subjects
        class_subject_mapping = {
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

        # Fetch the classes and their associated subjects
        classes = {}
        for class_name, subject_names in class_subject_mapping.items():
            class_obj = Class.objects.filter(name=class_name).first()
            if not class_obj:
                self.stdout.write(
                    self.style.ERROR(
                        f'Class "{class_name}" does not exist. Please create it first.'
                    )
                )
                return
            # Get the subject objects
            subjects = Subject.objects.filter(name__in=subject_names)
            if subjects.count() != len(subject_names):
                missing_subjects = set(subject_names) - set(
                    subjects.values_list("name", flat=True)
                )
                self.stdout.write(
                    self.style.ERROR(
                        f'Missing subjects for class "{class_name}": {", ".join(missing_subjects)}. Please create them first.'
                    )
                )
                return
            classes[class_obj] = list(subjects)

        if not classes:
            self.stdout.write(
                self.style.ERROR(
                    "No classes found. Please create the necessary classes and subjects first."
                )
            )
            return

        created_count = 0
        attempt = 0
        max_attempts = number * 2  # To prevent infinite loops

        while created_count < number and attempt < max_attempts:
            attempt += 1
            name = fake.name()
            email = fake.unique.email()
            age = random.randint(min_age, max_age)
            phone = fake.phone_number()[:15]
            address = fake.address()
            enrollment_date = fake.date_between(start_date="-2y", end_date=date.today())  # Fix here with `date.today()`
            # Randomly select a class
            class_obj, class_subjects = random.choice(list(classes.items()))

            # Assign all subjects from the class to the student
            student_subjects = class_subjects

            try:
                student = Student.objects.create(
                    name=name,
                    email=email,
                    age=age,
                    phone=phone,
                    address=address,
                    enrollment_date=enrollment_date,
                    class_obj=class_obj,
                )
                student.subjects.set(student_subjects)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created student: {name} in class "{class_obj.name}"'
                    )
                )
            except IntegrityError as e:
                # Handle potential unique constraint violations
                fake.unique.clear()  # Reset unique generator in case of duplicate email
                self.stdout.write(
                    self.style.ERROR(f"Failed to create student {name}: {e}")
                )
                continue

        if created_count < number:
            self.stdout.write(
                self.style.WARNING(
                    f"Only created {created_count} students out of requested {number} due to constraints."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {created_count} students.")
            )

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

from django.core.management.base import BaseCommand
from time_tables.models import Timetable, TimeSlot
from school_class.models import Class
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from datetime import time
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
import random

class Command(BaseCommand):
    help = "Generate timetables and time slots based on existing classes, subjects, and teachers."

    def handle(self, *args, **kwargs):
        self.create_time_slots()
        self.generate_timetables()
        self.stdout.write(self.style.SUCCESS("Successfully generated timetables and time slots."))

    def create_time_slots(self):
        """
        Create predefined time slots, including breaks.
        """
        predefined_slots = [
            {"start_time": time(10, 30), "end_time": time(11, 30), "is_break": False},
            {"start_time": time(11, 30), "end_time": time(12, 30), "is_break": False},
            {"start_time": time(12, 30), "end_time": time(13, 0), "is_break": True},  # Recess
            {"start_time": time(13, 0), "end_time": time(14, 0), "is_break": False},
            {"start_time": time(14, 0), "end_time": time(15, 0), "is_break": False},
            {"start_time": time(15, 0), "end_time": time(15, 15), "is_break": True},  # Short Break
            {"start_time": time(15, 15), "end_time": time(16, 15), "is_break": False},
            {"start_time": time(16, 15), "end_time": time(17, 15), "is_break": False},
        ]

        for slot in predefined_slots:
            TimeSlot.objects.get_or_create(
                start_time=slot["start_time"],
                end_time=slot["end_time"],
                is_break=slot["is_break"]
            )

    def generate_timetables(self):
        """
        Generate timetable entries ensuring unique constraints and proper assignments.
        """
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        # Define class and subject mappings
        class_subject_mapping = {
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

        # Fetch classes and their subjects
        classes = {}
        for class_name, subject_names in class_subject_mapping.items():
            class_obj = Class.objects.filter(name=class_name).first()
            if not class_obj:
                self.stdout.write(self.style.ERROR(f'Class "{class_name}" does not exist. Please create it first.'))
                continue
            subjects = Subject.objects.filter(name__in=subject_names)
            if subjects.count() != len(subject_names):
                missing_subjects = set(subject_names) - set(subjects.values_list('name', flat=True))
                self.stdout.write(self.style.ERROR(f'Missing subjects for class "{class_name}": {", ".join(missing_subjects)}. Please create them first.'))
                continue
            classes[class_obj] = list(subjects)

        if not classes:
            self.stdout.write(self.style.ERROR('No valid classes found.'))
            return

        # Fetch time slots
        time_slots = TimeSlot.objects.all().order_by('start_time')
        break_time_slots = time_slots.filter(is_break=True)
        teaching_time_slots = time_slots.filter(is_break=False)

        # Fetch teachers and their qualifications
        teachers = Teacher.objects.all()
        if not teachers.exists():
            self.stdout.write(self.style.ERROR('No teachers found. Please create teachers first.'))
            return

        # Build a mapping of subjects to their qualified teachers
        subject_teacher_map = {}
        for subject in Subject.objects.all():
            qualified_teachers = Teacher.objects.filter(
                teacher_class_subjects__subject=subject
            ).distinct()
            subject_teacher_map[subject] = list(qualified_teachers)

        # Generate timetables for each class
        for class_obj, class_subjects in classes.items():
            self.stdout.write(self.style.SUCCESS(f'Generating timetable for class "{class_obj.name}"'))
            for day in days_of_week:
                # Shuffle subjects to vary the schedule
                subjects_cycle = class_subjects.copy()
                random.shuffle(subjects_cycle)
                subject_index = 0

                for time_slot in time_slots:
                    # Handle break time slots
                    if time_slot.is_break:
                        # Create break entry
                        try:
                            Timetable.objects.create(
                                class_model=class_obj,
                                subject=None,
                                teacher=None,
                                time_slot=time_slot,
                                day_of_week=day
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Added break for "{class_obj.name}" at {time_slot} on {day}.'
                                )
                            )
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f"Error creating break entry: {e}"))
                        continue

                    # Get the next subject in the cycle
                    subject = subjects_cycle[subject_index % len(subjects_cycle)]
                    subject_index += 1

                    # Get teachers qualified to teach this subject in this class
                    qualified_teachers = Teacher.objects.filter(
                        teacher_class_subjects__class_obj=class_obj,
                        teacher_class_subjects__subject=subject
                    ).distinct()

                    # Exclude teachers already scheduled at this time slot
                    available_teachers = qualified_teachers.exclude(
                        timetables__day_of_week=day,
                        timetables__time_slot=time_slot
                    )

                    if not available_teachers.exists():
                        self.stdout.write(self.style.WARNING(
                            f'No available teachers for subject "{subject.name}" in class "{class_obj.name}" at {time_slot} on {day}.'
                        ))
                        continue

                    # Select a teacher
                    teacher = random.choice(list(available_teachers))

                    # Create the timetable entry
                    try:
                        with transaction.atomic():
                            tt_entry = Timetable.objects.create(
                                class_model=class_obj,
                                subject=subject,
                                teacher=teacher,
                                time_slot=time_slot,
                                day_of_week=day
                            )
                            self.stdout.write(self.style.SUCCESS(
                                f'Assigned "{subject.name}" to "{class_obj.name}" with teacher "{teacher.name}" at {time_slot} on {day}.'
                            ))
                    except ValidationError as ve:
                        self.stderr.write(self.style.ERROR(f"Validation error: {ve.messages}"))
                    except IntegrityError as ie:
                        self.stderr.write(self.style.ERROR(f"Integrity error: {ie}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error creating timetable entry: {e}"))

        self.stdout.write(self.style.SUCCESS("Timetable generation complete."))
