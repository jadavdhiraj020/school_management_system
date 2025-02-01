from django.core.management.base import BaseCommand
from students.models import Student
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from school_class.models import Class
from time_tables.models import Timetable, TimeSlot
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

# Teacher --> Subject --> Class --> Student --> TimeSlot --> Timetable

class Command(BaseCommand):
    help = "Delete all dummy data generated in the database"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        try:
            # Delete related objects first
            Timetable.objects.all().delete()
            TimeSlot.objects.all().delete()
            # Student.objects.all().delete()

            # Delete through model first
            # ClassTeacherSubject.objects.all().delete()

            # Then the rest
            # Class.objects.all().delete()
            # Subject.objects.all().delete()
            # Teacher.objects.all().delete()

            self.stdout.write(self.style.SUCCESS("Successfully deleted all dummy data"))
            logger.info("Dummy data deleted successfully.")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error occurred while deleting data: {e}")
            )
            logger.exception(f"Error deleting dummy data: {e}")
            raise