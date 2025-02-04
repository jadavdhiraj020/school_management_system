from django.contrib import admin
from .models import Subject, ClassTeacherSubject
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Register Subject model in admin
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']

admin.site.register(Subject, SubjectAdmin)

# Register ClassTeacherSubject model in admin
class ClassTeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'teacher', 'subject')
    list_filter = ('class_obj', 'teacher', 'subject')

admin.site.register(ClassTeacherSubject, ClassTeacherSubjectAdmin)

# Removed direct permission creation from here.
