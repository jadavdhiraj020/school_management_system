# views.py
from common.mixin import CustomLoginRequiredMixin, CustomPermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Class
from .forms import ClassForm


class ClassListView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, ListView):
    model = Class
    template_name = "class/class_list.html"
    context_object_name = "classes"
    ordering = ["name"]


class ClassDetailView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, DetailView):
    model = Class
    template_name = "class/class_detail.html"
    context_object_name = "class"


class ClassCreateView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = "class/class_form.html"
    success_url = reverse_lazy("class_list")


class ClassUpdateView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    model = Class
    form_class = ClassForm
    template_name = "class/class_form.html"
    success_url = reverse_lazy("class_list")


class ClassDeleteView(CustomLoginRequiredMixin, CustomPermissionRequiredMixin, DeleteView):
    model = Class
    template_name = "class/class_confirm_delete.html"
    success_url = reverse_lazy("class_list")
