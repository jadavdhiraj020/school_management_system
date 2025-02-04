from django import forms
from .models import Subject, ClassTeacherSubject
from school_class.models import Class
from teachers.models import Teacher

class SubjectForm(forms.ModelForm):
    classes = forms.ModelMultipleChoiceField(
        queryset=Class.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Classes",
        help_text="Select classes for this subject.",
    )
    teachers = forms.ModelMultipleChoiceField(
        queryset=Teacher.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Teachers",
        help_text="Select teachers for this subject.",
    )

    class Meta:
        model = Subject
        fields = ["name", "classes", "teachers"]
