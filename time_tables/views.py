from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from .models import Timetable, TimeSlot
from .forms import TimetableForm, TimeSlotForm
from teachers.models import Teacher
from subjects.models import Subject
from school_class.models import Class

# Timetable Views

class TimetableListView(ListView):
    model = Timetable
    template_name = "time_tables/timetable_list.html"
    context_object_name = "timetables"
    ordering = ['day_of_week', 'time_slot__start_time']

class TimetableDetailView(DetailView):
    model = Timetable
    template_name = "time_tables/timetable_detail.html"
    context_object_name = "timetable"

class TimetableCreateView(CreateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "time_tables/timetable_form.html"
    success_url = reverse_lazy("timetable_list")

class TimetableUpdateView(UpdateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "time_tables/timetable_form.html"
    success_url = reverse_lazy("timetable_list")

class TimetableDeleteView(DeleteView):
    model = Timetable
    template_name = "time_tables/timetable_confirm_delete.html"
    context_object_name = "timetable"
    success_url = reverse_lazy("timetable_list")

# TimeSlot Views

class TimeSlotListView(ListView):
    model = TimeSlot
    template_name = "time_tables/timeslot_list.html"
    context_object_name = "timeslots"
    ordering = ["start_time"]

class TimeSlotDetailView(DetailView):
    model = TimeSlot
    template_name = "time_tables/timeslot_detail.html"
    context_object_name = "timeslot"

class TimeSlotCreateView(CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = "time_tables/timeslot_form.html"
    success_url = reverse_lazy("timeslot_list")

class TimeSlotUpdateView(UpdateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = "time_tables/timeslot_form.html"
    success_url = reverse_lazy("timeslot_list")

class TimeSlotDeleteView(DeleteView):
    model = TimeSlot
    template_name = "time_tables/timeslot_confirm_delete.html"
    context_object_name = "timeslot"
    success_url = reverse_lazy("timeslot_list")
