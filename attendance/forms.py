from django import forms
from .models import Attendance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "teacher", "class_assigned", "date", "status", "comments"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "class": "border rounded px-3 py-2"}
            ),
            "status": forms.Select(attrs={"class": "border rounded px-3 py-2"}),
            "comments": forms.Textarea(
                attrs={"class": "border rounded px-3 py-2", "rows": 3}
            ),
        }

class AttendanceReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "border rounded px-3 py-2"}
        ),
        label="Start Date",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "border rounded px-3 py-2"}
        ),
        label="End Date",
    )
