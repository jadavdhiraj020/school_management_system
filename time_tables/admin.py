from django.contrib import admin
from time_tables.models import TimeSlot, Timetable

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'is_break')
    list_filter = ('is_break',)
    ordering = ('start_time',)

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_model', 'subject', 'teacher', 'time_slot', 'day_of_week')
    list_filter = ('day_of_week', 'class_model')
    ordering = ('day_of_week', 'time_slot__start_time')
