from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'age', 'phone', 'address', 'class_obj', 'subjects']
    
    # Custom form field styling can be handled in the template as shown earlier.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizing the form fields to add classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
