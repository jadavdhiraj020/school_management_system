from django import forms
from .models import Student
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, ButtonHolder, Submit
from accounts.models import CustomUser


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'age', 'phone', 'address', 'class_obj', 'subjects']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Age'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Address'}),
            'class_obj': forms.Select(attrs={'class': 'form-control'}),
            'subjects': forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'Student (User)',
            'age': 'Age',
            'phone': 'Phone Number',
            'address': 'Address',
            'class_obj': 'Class',
            'subjects': 'Subjects',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users not already linked to a student
        self.fields['user'].queryset = CustomUser.objects.filter(
            student_profile__isnull=True
        )
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Fieldset(
                'Student Information',
                Div('user', 'age', 'phone', 'address'),
                'class_obj',
                'subjects',
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )
