from core.mixins import RoleRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Student
from .forms import StudentForm

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

class StudentListView(RoleRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 10
    allowed_roles = ['admin', 'teacher', 'student']  # Add appropriate roles

    def get_queryset(self):
        search_query = self.request.GET.get('name', '')
        if search_query:
            return Student.objects.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )
        return Student.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('name', '')
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "Students generated and saved successfully."
        return context


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
