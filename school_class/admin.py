from django.contrib import admin
from school_class.models import Class

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_teacher')
    search_fields = ('name',)
