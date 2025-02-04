from core.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView
from .models import Teacher
from .forms import TeacherForm

class TeacherListView(RoleRequiredMixin, PermissionRequiredMixin, ListView):
    model = Teacher
    template_name = "teachers/teacher_list.html"
    context_object_name = "teachers"
    ordering = ["user__first_name"]
    permission_required = "teachers.can_view_teacher"

class TeacherCreateView(RoleRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "teachers/teacher_form.html"
    success_url = reverse_lazy("teacher_list")
    # Use Django's default add permission
    permission_required = "teachers.add_teacher"

class TeacherUpdateView(RoleRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "teachers/teacher_form.html"
    success_url = reverse_lazy("teacher_list")
    # Use Django's default change permission
    permission_required = "teachers.change_teacher"

class TeacherDeleteView(RoleRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_confirm_delete.html"
    success_url = reverse_lazy("teacher_list")
    # Use Django's default delete permission
    permission_required = "teachers.delete_teacher"

class TeacherDetailView(RoleRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Teacher
    template_name = "teachers/teacher_detail.html"
    context_object_name = "teacher"
    permission_required = "teachers.can_view_teacher"
