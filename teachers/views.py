from common.mixin import CustomLoginRequiredMixin, CustomPermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from .models import Teacher
from .forms import TeacherForm


class TeacherListView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    model = Teacher
    template_name = "teachers/teacher_list.html"
    context_object_name = "teachers"
    ordering = ["name"]


class TeacherCreateView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "teachers/teacher_form.html"
    success_url = reverse_lazy("teacher_list")


class TeacherDeleteView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_confirm_delete.html"
    success_url = reverse_lazy("teacher_list")


class TeacherDetailView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, DetailView):
    model = Teacher
    template_name = "teachers/teacher_detail.html"
    context_object_name = "teacher"


class TeacherUpdateView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "teachers/teacher_form.html"
    success_url = reverse_lazy("teacher_list")
