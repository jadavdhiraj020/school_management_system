from django import forms
from .models import Class
from teachers.models import Teacher
from subjects.models import Subject

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ["name", "class_teacher", "teachers", "subjects"]
        widgets = {
            "teachers": forms.CheckboxSelectMultiple(),
            "subjects": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        # Order class_teacher and teachers by the teacher's first name from the related user
        self.fields["class_teacher"].queryset = Teacher.objects.order_by("user__first_name")
        self.fields["teachers"].queryset = Teacher.objects.order_by("user__first_name")
        # Order subjects by name
        self.fields["subjects"].queryset = Subject.objects.order_by("name")
