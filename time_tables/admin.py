# admin.py for TimeSlot model
from django.contrib import admin
from .models import TimeSlot, Timetable


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    pass
