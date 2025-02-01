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
