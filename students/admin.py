from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'age', 'class_obj', 'enrollment_date')
    search_fields = ('name', 'email')
    list_filter = ('class_obj', 'enrollment_date')
