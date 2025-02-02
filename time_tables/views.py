from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
from django.db import transaction
from .models import Timetable, TimeSlot
from .forms import TimetableForm, TimeSlotForm
from teachers.models import Teacher
from subjects.models import Subject, ClassTeacherSubject
from school_class.models import Class
from ortools.sat.python import cp_model
import csv
from django.http import HttpResponse
from django.utils.timezone import now

###############################################
# CRUD Views (existing, unchanged)
###############################################


class TimetableListView(ListView):
    model = Timetable
    template_name = "time_tables/timetable_list.html"
    context_object_name = "timetables"
    ordering = ["day_of_week", "time_slot__start_time"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # List of days
        context["days"] = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]

        # Get all time slots
        context["timeslots"] = TimeSlot.objects.all()

        # Prepare timetables for each day and timeslot
        timetables = {}
        for day in context["days"]:
            day_entries = Timetable.objects.filter(day_of_week=day)
            timetables[day] = {ts.id: ts for ts in context["timeslots"]}
            for entry in day_entries:
                timetables[day][entry.time_slot.id] = entry

        context["timetables"] = timetables

        return context


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


###############################################
# New Dynamic Scheduling and Saving View with OR-Tools
###############################################


class TimetableGenerateView(TemplateView):
    template_name = "time_tables/timetable_generate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Provide a list of available classes for the selection form.
        available_classes = Class.objects.all()
        context["available_classes"] = available_classes

        # Get the target class from GET parameter (if submitted).
        target_class_name = self.request.GET.get("class_name")
        if not target_class_name:
            # If no class selected yet, simply return the form.
            return context

        try:
            selected_class = Class.objects.get(name=target_class_name)
        except Class.DoesNotExist:
            context["error"] = f"Class '{target_class_name}' not found."
            return context

        # Define days for a 6-day week.
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        all_timeslots = list(TimeSlot.objects.all().order_by("start_time"))
        lesson_timeslots = [ts for ts in all_timeslots if not ts.is_break]

        # Build assignments for all classes (for conflict checking across classes).
        classes = list(Class.objects.all())
        class_assignments = {}
        for cls in classes:
            assignments_qs = ClassTeacherSubject.objects.filter(class_obj=cls)
            assignments = []
            for cts in assignments_qs:
                assignments.append(
                    {
                        "subject_id": cts.subject.id,
                        "teacher_id": cts.teacher.id,
                        "subject_name": cts.subject.name,
                        "teacher_name": cts.teacher.name,
                    }
                )
            if len(assignments) != len(lesson_timeslots):
                context["error"] = (
                    f"Class {cls.name} has {len(assignments)} assignments but "
                    f"{len(lesson_timeslots)} lesson slots per day."
                )
                return context
            class_assignments[cls.id] = assignments

        # Build the CP-SAT model.
        model = cp_model.CpModel()
        decision_vars = {}
        teacher_vars = {}

        for cls in classes:
            assignments = class_assignments[cls.id]
            n_assignments = len(assignments)
            teacher_ids_list = [assignment["teacher_id"] for assignment in assignments]
            for day in days:
                day_vars = []
                for slot_index in range(n_assignments):
                    var = model.NewIntVar(
                        0, n_assignments - 1, f"cls{cls.id}_{day}_slot{slot_index}"
                    )
                    decision_vars[(cls.id, day, slot_index)] = var
                    day_vars.append(var)
                    t_var = model.NewIntVar(
                        min(teacher_ids_list),
                        max(teacher_ids_list),
                        f"cls{cls.id}_{day}_slot{slot_index}_teacher",
                    )
                    teacher_vars[(cls.id, day, slot_index)] = t_var
                    # Link the decision variable with the teacher ID from the assignment.
                    model.AddElement(var, teacher_ids_list, t_var)
                # Each lesson slot in a day gets a unique assignment.
                model.AddAllDifferent(day_vars)

        # Ensure that for each day and each lesson slot (across classes), teachers are not double-booked.
        for day in days:
            for slot_index in range(len(lesson_timeslots)):
                teacher_vars_this_slot = []
                for cls in classes:
                    teacher_vars_this_slot.append(
                        teacher_vars[(cls.id, day, slot_index)]
                    )
                model.AddAllDifferent(teacher_vars_this_slot)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            context["error"] = (
                "No feasible timetable found. Please check class assignments and timeslot configurations."
            )
            return context

        # Build the timetable solution structure.
        timetable_solution = {cls.id: {day: {} for day in days} for cls in classes}
        for cls in classes:
            lesson_counter = 0
            for ts in all_timeslots:
                if ts.is_break:
                    for day in days:
                        timetable_solution[cls.id][day][ts.id] = {
                            "is_break": True,
                            "display": f"Break ({ts.start_time.strftime('%I:%M %p')} - {ts.end_time.strftime('%I:%M %p')})",
                        }
                else:
                    for day in days:
                        var = decision_vars[(cls.id, day, lesson_counter)]
                        assign_index = solver.Value(var)
                        assignment = class_assignments[cls.id][assign_index]
                        timetable_solution[cls.id][day][ts.id] = {
                            "is_break": False,
                            "subject": assignment["subject_name"],
                            "teacher": assignment["teacher_name"],
                        }
                    lesson_counter += 1

        # Save the generated timetable for the selected class.
        try:
            with transaction.atomic():
                # Delete any existing timetable for the class.
                Timetable.objects.filter(class_model=selected_class).delete()
                for day in days:
                    for ts in all_timeslots:
                        cell = timetable_solution[selected_class.id][day].get(ts.id)
                        if cell:
                            if ts.is_break:
                                Timetable.objects.create(
                                    class_model=selected_class,
                                    time_slot=ts,
                                    day_of_week=day,
                                    subject=None,
                                    teacher=None,
                                )
                            else:
                                subject = Subject.objects.filter(
                                    name=cell["subject"]
                                ).first()
                                teacher = Teacher.objects.filter(
                                    name=cell["teacher"]
                                ).first()
                                Timetable.objects.create(
                                    class_model=selected_class,
                                    time_slot=ts,
                                    day_of_week=day,
                                    subject=subject,
                                    teacher=teacher,
                                )
        except Exception as e:
            context["error"] = f"An error occurred while saving the timetable: {e}"
            return context

        context["selected_class"] = selected_class
        context["days"] = days
        context["timeslots"] = all_timeslots
        context["timetable"] = timetable_solution[selected_class.id]
        context["message"] = "Timetable generated and saved successfully."
        return context


class TimetableDownloadView(View):
    def get(self, request, *args, **kwargs):
        target_class_name = request.GET.get("class_name", "")
        try:
            selected_class = Class.objects.get(name=target_class_name)
        except Class.DoesNotExist:
            return HttpResponse("Class not found.", status=404)

        timetable_qs = Timetable.objects.filter(class_model=selected_class).order_by(
            "day_of_week", "time_slot__start_time"
        )
        response = HttpResponse(content_type="text/csv")
        filename = f"timetable_{selected_class.name.replace(' ', '_')}_{now().strftime('%Y%m%d')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        header = [
            "Time Slot",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        writer.writerow(header)
        timeslot_ids = sorted({entry.time_slot.id for entry in timetable_qs})
        timeslot_map = {}
        for entry in timetable_qs:
            ts = entry.time_slot
            timeslot_map[ts.id] = (
                f"{ts.start_time.strftime('%I:%M %p')} - {ts.end_time.strftime('%I:%M %p')}"
            )

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        schedule = {ts_id: {} for ts_id in timeslot_ids}
        for entry in timetable_qs:
            schedule[entry.time_slot.id][entry.day_of_week] = entry

        for ts_id in timeslot_ids:
            row = [timeslot_map.get(ts_id, "")]
            sample_entry = schedule[ts_id].get(days[0])
            if sample_entry and sample_entry.time_slot.is_break:
                break_text = f"Break ({sample_entry.time_slot.start_time.strftime('%I:%M %p')} - {sample_entry.time_slot.end_time.strftime('%I:%M %p')})"
                row.append(break_text)
                row.extend([""] * (len(days) - 1))
            else:
                for day in days:
                    entry = schedule[ts_id].get(day)
                    if entry:
                        cell_text = f"{entry.subject.name if entry.subject else ''}\n{entry.teacher.name if entry.teacher else ''}"
                        row.append(cell_text)
                    else:
                        row.append("--")
            writer.writerow(row)
        return response
