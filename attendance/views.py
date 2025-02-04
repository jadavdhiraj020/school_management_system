from core.mixins import RoleRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Attendance
from .forms import AttendanceForm, AttendanceReportForm

class AttendanceListView(RoleRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/attendance_list.html"
    context_object_name = "attendances"
    ordering = ["-date"]
    permission_required = "attendance.can_view_attendance"

class AttendanceCreateView(RoleRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "attendance/attendance_form.html"
    success_url = reverse_lazy("attendance-list")
    permission_required = "attendance.can_mark_attendance"

    def form_valid(self, form):
        # Automatically assign the logged-in teacher if available.
        if hasattr(self.request.user, "teacher"):
            form.instance.teacher = self.request.user.teacher
        return super().form_valid(form)

class AttendanceUpdateView(RoleRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "attendance/attendance_form.html"
    success_url = reverse_lazy("attendance-list")
    permission_required = "attendance.can_edit_attendance"

class AttendanceReportPDFView(RoleRequiredMixin, FormView):
    template_name = "attendance/attendance_report_form.html"
    form_class = AttendanceReportForm
    permission_required = "attendance.can_view_attendance"

    def form_valid(self, form):
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]

        # Filter attendance records within the date range.
        attendances = Attendance.objects.filter(date__range=[start_date, end_date]).order_by("date")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="attendance_report.pdf"'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 14)
        p.drawString(100, 800, "Attendance Report")
        p.setFont("Helvetica", 10)
        p.drawString(100, 780, f"From: {start_date} To: {end_date}")

        # Draw table header.
        y = 750
        p.drawString(50, y, "Student")
        p.drawString(250, y, "Date")
        p.drawString(350, y, "Status")
        y -= 20

        for attendance in attendances:
            if y < 50:
                p.showPage()
                y = 800
            p.drawString(50, y, str(attendance.student))
            p.drawString(250, y, str(attendance.date))
            p.drawString(350, y, attendance.status)
            y -= 20

        p.showPage()
        p.save()
        return response
