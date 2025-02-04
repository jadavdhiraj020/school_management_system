from core.mixins import RoleRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import Student
from students.forms import StudentForm  # Ensure this import is correct


# List View: Display all students
class StudentListView(RoleRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 10
    ordering = ["user__first_name"]
    allowed_roles = ['admin', 'teacher', 'student']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("name", "")
        return context


# Detail View: Display a single student's details
class StudentDetailView(RoleRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"
    context_object_name = "student"
    allowed_roles = ['admin', 'teacher', 'student']


# Create View: Add a new student
class StudentCreateView(RoleRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")
    allowed_roles = ['admin']


# Update View: Edit an existing student
class StudentUpdateView(RoleRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")
    allowed_roles = ['admin', 'teacher']


# Delete View: Delete a student
class StudentDeleteView(RoleRequiredMixin, DeleteView):
    model = Student
    template_name = "students/student_confirm_delete.html"
    success_url = reverse_lazy("student_list")
    allowed_roles = ['admin']
