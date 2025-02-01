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
