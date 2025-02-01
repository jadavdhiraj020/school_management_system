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
            phone = fake.phone_number()
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
