# Standard Library Imports
import csv

# Django Imports
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
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.utils.timezone import now

# Third‑Party Imports
from ortools.sat.python import cp_model
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas

# Local App Imports
from core.mixins import RoleRequiredMixin
from .models import Timetable, TimeSlot
from .forms import TimetableForm, TimeSlotForm
from teachers.models import Teacher
from subjects.models import Subject, ClassTeacherSubject
from school_class.models import Class


###############################################
# CRUD Views for Timetable
###############################################

class TimetableListView(RoleRequiredMixin, ListView):
    model = Timetable
    template_name = "time_tables/timetable_list.html"
    context_object_name = "timetables"
    permission_required = "time_tables.can_view_timetable"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_class_name = self.request.GET.get("class_name")
        context["selected_class"] = None
        context["available_classes"] = Class.objects.all()

        if selected_class_name:
            try:
                context["selected_class"] = Class.objects.get(name=selected_class_name)
            except Class.DoesNotExist:
                messages.error(self.request, f"Class {selected_class_name} not found")
        context["days"] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        context["timeslots"] = TimeSlot.objects.all().order_by("start_time")

        timetables = {}
        if context["selected_class"]:
            entries = Timetable.objects.filter(class_model=context["selected_class"]).select_related("time_slot", "subject", "teacher")
            for day in context["days"]:
                day_entries = entries.filter(day_of_week=day)
                timetables[day] = {entry.time_slot.id: entry for entry in day_entries}
        context["timetables"] = timetables
        return context

class TimetableDetailView(RoleRequiredMixin, DetailView):
    model = Timetable
    template_name = "time_tables/timetable_detail.html"
    context_object_name = "timetable"
    permission_required = "time_tables.can_view_timetable"

class TimetableCreateView(RoleRequiredMixin, CreateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "time_tables/timetable_form.html"
    success_url = reverse_lazy("timetable_list")
    permission_required = "time_tables.can_edit_timetable"

class TimetableUpdateView(RoleRequiredMixin, UpdateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "time_tables/timetable_form.html"
    success_url = reverse_lazy("timetable_list")
    permission_required = "time_tables.can_edit_timetable"

class TimetableDeleteView(RoleRequiredMixin, DeleteView):
    model = Timetable
    template_name = "time_tables/timetable_confirm_delete.html"
    context_object_name = "timetable"
    success_url = reverse_lazy("timetable_list")
    permission_required = "time_tables.can_edit_timetable"

###############################################
# CRUD Views for TimeSlot
###############################################

class TimeSlotListView(ListView):
    model = TimeSlot
    template_name = "time_slot/time_slot_list.html"
    context_object_name = "timeslots"
    ordering = ["start_time"]

class TimeSlotDetailView(DetailView):
    model = TimeSlot
    template_name = "time_slot/time_slot_detail.html"
    context_object_name = "timeslot"

class TimeSlotCreateView(CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = "time_slot/time_slot_form.html"
    success_url = reverse_lazy("timeslot_list")

class TimeSlotUpdateView(UpdateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = "time_slot/time_slot_form.html"
    success_url = reverse_lazy("timeslot_list")

class TimeSlotDeleteView(DeleteView):
    model = TimeSlot
    template_name = "time_slot/time_slot_confirm_delete.html"
    context_object_name = "timeslot"
    success_url = reverse_lazy("timeslot_list")


class TimetableGenerateView(RoleRequiredMixin, TemplateView):
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



def add_page_number(canvas_obj, doc):
    """
    Adds the page number at the bottom-right of each page.
    """
    page_num = canvas_obj.getPageNumber()
    text = f"Page {page_num}"
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawRightString(doc.pagesize[0] - 40, 20, text)

class TimetableDownloadView(RoleRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        target_class_name = request.GET.get("class_name", "")
        try:
            selected_class = Class.objects.get(name=target_class_name)
        except Class.DoesNotExist:
            return HttpResponse("Class not found.", status=404)

        timetable_qs = Timetable.objects.filter(class_model=selected_class).order_by(
            "day_of_week", "time_slot__start_time"
        )

        # Create a PDF response
        response = HttpResponse(content_type="application/pdf")
        filename = f"timetable_{selected_class.name.replace(' ', '_')}_{now().strftime('%Y%m%d')}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Create a PDF document with landscape letter size
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=40
        )
        elements = []

        # Custom styles for a professional look
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CellText',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=1,  # Center aligned
            textColor=colors.HexColor('#2C3E50'),
        ))
        title_style = ParagraphStyle(
            name='Title',
            fontSize=26,
            leading=32,
            spaceAfter=20,
            alignment=1,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2980B9')
        )
        elements.append(Paragraph(f"{selected_class.name} Timetable", title_style))
        elements.append(Spacer(1, 12))

        # Prepare the table header
        header = ["Time Slot", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        data = [header]

        # Map and sort time slots
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

        # Build table rows for each time slot
        for ts_id in timeslot_ids:
            time_slot = timeslot_map.get(ts_id, "")
            row = [time_slot]
            for day in days:
                entry = schedule[ts_id].get(day)
                if entry:
                    subject = entry.subject.name if entry.subject else ''
                    teacher = entry.teacher.name if entry.teacher else ''
                    cell_content = f"<b>{subject}</b><br/><i>{teacher}</i>"
                    row.append(cell_content)
                else:
                    row.append("--")
            data.append(row)

        # Convert each cell to a Paragraph object
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                if i == 0:  # header row
                    data[i][j] = Paragraph(f"<b>{cell}</b>", styles['Heading4'])
                else:
                    data[i][j] = Paragraph(cell, styles['CellText'])

        # Define column widths for the table
        col_widths = [doc.width * 0.15] + [doc.width * 0.14] * 6
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Style the table with alternating row colors and padding
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9F9F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8FF')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF and add page numbers
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

        return response


