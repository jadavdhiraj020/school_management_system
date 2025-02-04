from django import forms
from .models import Teacher
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, ButtonHolder, Submit

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'age', 'phone', 'address', 'subject']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Age'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Address'}),
            'subject': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'user': 'Teacher (User)',
            'age': 'Age',
            'phone': 'Phone Number',
            'address': 'Address',
            'subject': 'Subjects',
        }

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Fieldset(
                'Teacher Information',
                Div('user', 'age', 'phone', 'address'),
                'subject',
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )
