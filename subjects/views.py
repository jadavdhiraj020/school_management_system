from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db import IntegrityError, transaction
from .models import Subject, ClassTeacherSubject
from school_class.models import Class
from teachers.models import Teacher
from .forms import SubjectForm


class SubjectListView(ListView):
    model = Subject
    template_name = "subjects/subject_list.html"
    context_object_name = "subjects"
    ordering = ["name"]


class SubjectDetailView(DetailView):
    model = Subject
    template_name = "subjects/subject_detail.html"
    context_object_name = "subject"


class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "subjects/subject_form.html"
    success_url = reverse_lazy("subject_list")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                self.save_related(form)
                return response
        except IntegrityError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def save_related(self, form):
        classes = form.cleaned_data.get('classes')
        teachers = form.cleaned_data.get('teachers')
        subject = self.object

        # Create ClassTeacherSubject entries
        for class_obj in classes:
            for teacher in teachers:
                ClassTeacherSubject.objects.get_or_create(
                    class_obj=class_obj,
                    teacher=teacher,
                    subject=subject
                )


class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "subjects/subject_form.html"
    success_url = reverse_lazy("subject_list")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                self.save_related(form)
                return response
        except IntegrityError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

    def save_related(self, form):
        classes = form.cleaned_data.get('classes')
        teachers = form.cleaned_data.get('teachers')
        subject = self.object

        # Remove existing relationships
        ClassTeacherSubject.objects.filter(subject=subject).delete()

        # Create new ClassTeacherSubject entries
        for class_obj in classes:
            for teacher in teachers:
                ClassTeacherSubject.objects.get_or_create(
                    class_obj=class_obj,
                    teacher=teacher,
                    subject=subject
                )


class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = "subjects/subject_confirm_delete.html"
    context_object_name = "subject"
    success_url = reverse_lazy("subject_list")
