from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create roles as groups and assign permissions."

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        teacher_group, _ = Group.objects.get_or_create(name="Teacher")
        student_group, _ = Group.objects.get_or_create(name="Student")

        # Get all permissions
        all_permissions = Permission.objects.all()

        # Assign all permissions to the Admin group
        admin_group.permissions.set(all_permissions)

        # Define and assign permissions for the Teacher group
        teacher_permissions = Permission.objects.filter(
            content_type__app_label__in=[
                "attendance",
                "school_class",
                "timetable",
                "subjects",
                "students",
                "teachers",
            ],
            codename__in=[
                "add_attendance",
                "change_attendance",
                "view_attendance",
                "add_grade",
                "change_grade",
                "view_grade",
                "view_timetable",
                "can_view_teacher",
                "can_edit_teacher",
                "can_view_class",
                "can_edit_class",
                "can_view_subject",
                "can_edit_subject",
            ],
        )
        teacher_group.permissions.set(teacher_permissions)

        # Define and assign permissions for the Student group
        student_permissions = Permission.objects.filter(
            content_type__app_label__in=[
                "attendance",
                "school_class",
                "timetable",
                "subjects",
                "students",
                "teachers",
            ],
            codename__in=[
                "view_attendance",
                "view_grade",
                "view_timetable",
                "can_view_student",
                "can_view_teacher",
                "can_view_class",
                "can_view_subject",
            ],
        )
        student_group.permissions.set(student_permissions)

        self.stdout.write(
            self.style.SUCCESS("Groups and permissions created successfully.")
        )
