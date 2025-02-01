from django import forms
from .models import TimeSlot, Timetable
from school_class.models import Class
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["start_time", "end_time", "is_break"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "is_break": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Start time must be before end time.")

        return cleaned_data


class TimetableForm(forms.ModelForm):
    class_model = forms.ModelChoiceField(queryset=Class.objects.all(), label="Class")
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(), required=False, label="Subject"
    )
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(), required=False, label="Teacher"
    )
    time_slot = forms.ModelChoiceField(queryset=TimeSlot.objects.all(), label="Time Slot")
    day_of_week = forms.ChoiceField(
        choices=Timetable.DAYS_OF_WEEK_CHOICES, label="Day of the Week"
    )

    class Meta:
        model = Timetable
        fields = ["class_model", "subject", "teacher", "time_slot", "day_of_week"]

    def clean(self):
        cleaned_data = super().clean()
        class_model = cleaned_data.get("class_model")
        subject = cleaned_data.get("subject")
        teacher = cleaned_data.get("teacher")
        time_slot = cleaned_data.get("time_slot")
        day_of_week = cleaned_data.get("day_of_week")

        # If the time slot is a break, ensure no subject or teacher is assigned
        if time_slot and time_slot.is_break:
            if subject or teacher:
                raise forms.ValidationError("Break slots cannot be assigned subjects or teachers.")

        # Ensure both subject and teacher are provided for non-break slots
        if time_slot and not time_slot.is_break:
            if not subject or not teacher:
                raise forms.ValidationError("Both subject and teacher are required for non-break slots.")

            # Check if the teacher is qualified to teach the subject in the given class
            if not ClassTeacherSubject.objects.filter(
                teacher=teacher, subject=subject, class_obj=class_model
            ).exists():
                raise forms.ValidationError(f"Teacher {teacher} is not assigned to teach {subject} in this class.")

            # Check for conflicts in timetable
            if Timetable.objects.filter(
                class_model=class_model, time_slot=time_slot, day_of_week=day_of_week
            ).exists():
                raise forms.ValidationError(
                    f"Class {class_model} already has a timetable entry at this time on {day_of_week}."
                )

            if Timetable.objects.filter(
                teacher=teacher, time_slot=time_slot, day_of_week=day_of_week
            ).exists():
                raise forms.ValidationError(
                    f"Teacher {teacher} is already assigned to another class at this time."
                )

        return cleaned_data
