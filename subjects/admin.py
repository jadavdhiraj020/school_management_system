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
    ordering = ("subject__name",)
