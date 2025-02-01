import random
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.db import transaction
from students.models import Student
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from school_class.models import Class
from time_tables.models import Timetable, TimeSlot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generates dummy data for models"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        fake = Faker()

        try:
            teachers = self.create_teachers(fake)
            subjects = self.create_subjects(teachers)
            classes = self.create_classes(teachers, subjects)
            self.create_students(fake, classes)
            time_slots = self.create_time_slots()
            self.create_timetables(classes, subjects, teachers, time_slots)

            self.stdout.write(self.style.SUCCESS("Dummy data generated successfully!"))

        except Exception as e:
            logger.exception(f"Error during data generation: {e}")
            self.stdout.write(
                self.style.ERROR(f"Data generation failed. See logs for details.")
            )

    def create_teachers(self, fake):
        teachers = []
        for _ in range(12):
            try:
                teacher = Teacher.objects.create(
                    name=fake.name(),
                    email=fake.unique.email(),
                    age=random.randint(25, 55),
                    phone=fake.phone_number(),
                    address=fake.address(),
                )
                teachers.append(teacher)
            except Exception as e:
                logger.error(f"Error creating teacher: {e}")
                raise

        return teachers

    def create_subjects(self, teachers):
        subjects = []
        subject_names = [
            "Mathematics",
            "Physics",
            "Chemistry",
            "Computer",
            "English",
            "Biology",
        ]
        for subject_name in subject_names:
            try:
                subject = Subject.objects.create(name=subject_name)
                # Assign exactly two unique teachers (using ClassTeacherSubject)
                assigned_teachers = random.sample(teachers, k=2)

                for teacher in assigned_teachers:
                    ClassTeacherSubject.objects.create(teacher=teacher, subject=subject)

                subjects.append(subject)
            except Exception as e:
                logger.error(f"Error creating subject: {e}")
                raise
        return subjects

    def create_classes(self, teachers, subjects):
        classes = []
        class_names = ["12th Science A Groups", "12th Science B Groups"]
        for class_name in class_names:
            try:
                class_obj = Class.objects.create(
                    name=class_name, class_teacher=random.choice(teachers)
                )

                # Assign subjects based on class (using ClassTeacherSubject)
                if class_name == "12th Science A Groups":
                    class_subjects = [
                        s
                        for s in subjects
                        if s.name
                        in [
                            "Mathematics",
                            "Physics",
                            "Chemistry",
                            "Computer",
                            "English",
                        ]
                    ]
                elif class_name == "12th Science B Groups":
                    class_subjects = [
                        s
                        for s in subjects
                        if s.name
                        in ["Physics", "Chemistry", "Biology", "Computer", "English"]
                    ]

                for subject in class_subjects:
                    for teacher in subject.teachers.all():
                        ClassTeacherSubject.objects.create(
                            class_obj=class_obj, teacher=teacher, subject=subject
                        )

                classes.append(class_obj)
            except Exception as e:
                logger.error(f"Error creating class: {e}")
                raise
        return classes

    def create_students(self, fake, classes):
        existing_student_emails = set(Student.objects.values_list("email", flat=True))
        for class_obj in classes:
            for _ in range(50):
                try:
                    email = fake.unique.email()
                    while email in existing_student_emails:
                        email = fake.unique.email()

                    Student.objects.create(
                        name=fake.name(),
                        email=email,
                        age=random.randint(16, 21),
                        phone=fake.phone_number(),
                        address=fake.address(),
                        class_obj=class_obj,
                    )
                    existing_student_emails.add(email)
                except Exception as e:
                    logger.error(f"Error creating student: {e}")
                    raise

    def create_time_slots(self):
        time_slots = []
        times = [
            (10, 30),
            (11, 30),
            (12, 30),
            (13, 00),
            (14, 00),
            (15, 00),
            (15, 15),
            (16, 15),
        ]
        for start_hour, start_minute in times:
            end_hour = start_hour + 1 if start_minute < 30 else start_hour
            end_minute = 30 if start_minute == 0 else 0
            try:
                time_slot = TimeSlot.objects.create(
                    start_time=timezone.now()
                    .replace(
                        hour=start_hour, minute=start_minute, second=0, microsecond=0
                    )
                    .time(),
                    end_time=timezone.now()
                    .replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                    .time(),
                    is_break=(12, 30) <= (start_hour, start_minute) <= (13, 00)
                    or (15, 00) <= (start_hour, start_minute) <= (15, 15),
                )
                time_slots.append(time_slot)
            except Exception as e:
                logger.error(f"Error creating time slot: {e}")
                raise
        return time_slots

    def create_timetables(self, classes, subjects, teachers, time_slots):
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        timetable_pattern = [
            "subject",
            "subject",
            "break",
            "subject",
            "subject",
            "break",
            "subject",
            "subject",
        ]

        for class_obj in classes:
            teacher_schedules = {teacher: {} for teacher in teachers}
            for day in days_of_week:
                for i, time_slot in enumerate(time_slots):
                    slot_type = timetable_pattern[i]
                    try:
                        if slot_type == "break":
                            Timetable.objects.create(
                                class_model=class_obj,
                                time_slot=time_slot,
                                day_of_week=day,
                            )
                        elif slot_type == "subject":
                            available_subjects = list(class_obj.subjects.all())
                            if available_subjects:
                                subject = random.choice(available_subjects)
                                available_teachers = list(subject.teachers.all())

                                if available_teachers:
                                    teacher = random.choice(available_teachers)
                                    if day not in teacher_schedules[teacher]:
                                        teacher_schedules[teacher][day] = []

                                    if time_slot not in teacher_schedules[teacher][day]:
                                        Timetable.objects.create(
                                            class_model=class_obj,
                                            subject=subject,
                                            teacher=teacher,
                                            time_slot=time_slot,
                                            day_of_week=day,
                                        )
                                        teacher_schedules[teacher][day].append(
                                            time_slot
                                        )
                                    else:
                                        logger.warning(
                                            f"Teacher {teacher} is booked at {time_slot} on {day}"
                                        )
                                else:
                                    logger.warning(
                                        f"No qualified teachers for {subject} in class {class_obj.name}"
                                    )
                            else:
                                logger.warning(
                                    f"No subjects found for class {class_obj.name}"
                                )

                    except Exception as e:
                        logger.error(f"Error creating timetable: {e}")
                        raise
