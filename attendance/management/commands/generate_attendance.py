# attendance/management/commands/generate_attendance.py
from django.core.management.base import BaseCommand
from attendance.models import Attendance
from students.models import Student
from teachers.models import Teacher
from school_class.models import Class
from faker import Faker
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Generate dummy attendance data."

    def add_arguments(self, parser):
        parser.add_argument(
            "number",
            type=int,
            nargs="?",
            default=200,
            help="Number of attendance records to generate (default: 200)"
        )
        parser.add_argument(
            "--start-date",
            type=str,
            default=None,
            help="Start date in YYYY-MM-DD format. Defaults to 7 days ago."
        )
        parser.add_argument(
            "--end-date",
            type=str,
            default=None,
            help="End date in YYYY-MM-DD format. Defaults to today."
        )

    def handle(self, *args, **options):
        number = options["number"]
        start_date_str = options["start_date"]
        end_date_str = options["end_date"]

        # Define date range defaults if not provided
        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        else:
            start_date = date.today() - timedelta(days=7)

        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
        else:
            end_date = date.today()

        if start_date > end_date:
            self.stdout.write(self.style.ERROR("Start date must be before end date."))
            return

        students = list(Student.objects.all())
        if not students:
            self.stdout.write(self.style.ERROR("No students available."))
            return

        fake = Faker()
        created_count = 0

        for _ in range(number):
            student = random.choice(students)
            class_assigned = student.class_obj  # Student's assigned class
            teacher = None
            if class_assigned:
                # Use the class teacher if set; otherwise, choose a random teacher
                teacher = class_assigned.class_teacher or random.choice(list(Teacher.objects.all()))
            # Random date between start_date and end_date
            random_days = random.randint(0, (end_date - start_date).days)
            attendance_date = start_date + timedelta(days=random_days)
            status = random.choice(['Present', 'Absent'])
            comments = fake.sentence() if status == 'Absent' else ''

            try:
                Attendance.objects.create(
                    student=student,
                    teacher=teacher,
                    class_assigned=class_assigned,
                    date=attendance_date,
                    status=status,
                    comments=comments
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Created attendance for {student.name} on {attendance_date}"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Failed to create attendance for {student.name}: {e}"
                ))
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} attendance records."))
