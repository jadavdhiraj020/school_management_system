from django.contrib import admin
from students.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "age", "class_obj", "enrollment_date")
    search_fields = ("name", "email")
    list_filter = ("class_obj", "enrollment_date")


from django.contrib import admin
from subjects.models import Subject, ClassTeacherSubject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ClassTeacherSubject)
class ClassTeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ("class_obj", "teacher", "subject")
    search_fields = ("class_obj__name", "teacher__name", "subject__name")


from django.contrib import admin
from teachers.models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "age", "joining_date")
    search_fields = ("name", "email")


from django.contrib import admin
from time_tables.models import TimeSlot, Timetable


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "is_break")
    list_filter = ("is_break",)
    ordering = ("start_time",)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("class_model", "subject", "teacher", "time_slot", "day_of_week")
    list_filter = ("day_of_week", "class_model")
    ordering = ("day_of_week", "time_slot__start_time")


from django.contrib import admin
from school_class.models import Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "class_teacher")
    search_fields = ("name",)
