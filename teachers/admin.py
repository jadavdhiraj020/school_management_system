from django.contrib import admin
from teachers.models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'age', 'joining_date')
    search_fields = ('name', 'email')
    ordering = ('name',)
