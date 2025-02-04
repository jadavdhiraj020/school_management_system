from django.core.management.base import BaseCommand
from teachers.models import Teacher
from accounts.models import CustomUser
import random
from faker import Faker
from django.db.utils import IntegrityError

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
            self.stdout.write(self.style.ERROR("Minimum age cannot be greater than maximum age."))
            return

        fake = Faker()
        Faker.seed(0)
        fake.unique.clear()
        created_count = 0
        attempt = 0
        max_attempts = number * 2

        while created_count < number and attempt < max_attempts:
            attempt += 1
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = fake.unique.user_name()
            email = fake.unique.email()
            age = random.randint(min_age, max_age)
            phone = fake.phone_number()[:15]
            address = fake.address()
            try:
                # Create a CustomUser with role teacher
                user = CustomUser.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='teacher'
                )
                Teacher.objects.create(
                    user=user,
                    age=age,
                    phone=phone,
                    address=address,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created teacher: {first_name} {last_name}"))
            except IntegrityError as e:
                fake.unique.clear()
                self.stdout.write(self.style.ERROR(f"Failed to create teacher {first_name} {last_name}: {e}"))
                continue

        if created_count < number:
            self.stdout.write(self.style.WARNING(
                f"Only created {created_count} teachers out of requested {number} due to constraints."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} teachers."))
