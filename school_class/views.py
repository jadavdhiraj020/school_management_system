from core.mixins import RoleRequiredMixin
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

class ClassListView(RoleRequiredMixin, ListView):
    model = Class
    template_name = "class/class_list.html"
    context_object_name = "classes"
    ordering = ["name"]

class ClassDetailView(RoleRequiredMixin, DetailView):
    model = Class
    template_name = "class/class_detail.html"
    context_object_name = "class"

class ClassCreateView(RoleRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = "class/class_form.html"
    success_url = reverse_lazy("class_list")

class ClassUpdateView(RoleRequiredMixin, UpdateView):
    model = Class
    form_class = ClassForm
    template_name = "class/class_form.html"
    success_url = reverse_lazy("class_list")

class ClassDeleteView(RoleRequiredMixin, DeleteView):
    model = Class
    template_name = "class/class_confirm_delete.html"
    success_url = reverse_lazy("class_list")
