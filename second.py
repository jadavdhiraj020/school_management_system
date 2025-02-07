from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    search_fields = ("username", "email", "role")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Roles & Permissions",
            {
                "fields": (
                    "role",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "role", "password1", "password2"),
            },
        ),
    )
    ordering = ("username",)


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, RoleChangeRequest


class CustomUserCreationForm(UserCreationForm):
    """
    A registration form with Bootstrap styling and custom validation.
    """

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "password1",
            "password2",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter email"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter first name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter last name"}
            ),
            "role": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter phone number"}
            ),
            "password1": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": "Enter password"}
            ),
            "password2": forms.PasswordInput(
                attrs={"class": "form-control", "placeholder": "Confirm password"}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone


class CustomAuthenticationForm(AuthenticationForm):
    """
    A login form with Bootstrap styling.
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter username"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        ),
    )


class RoleChangeRequestForm(forms.ModelForm):
    """
    Form for users to request a change in their role.
    """

    class Meta:
        model = RoleChangeRequest
        fields = ["requested_role"]
        widgets = {
            "requested_role": forms.Select(attrs={"class": "form-select"}),
        }


from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    ROLES = (
        ("admin", "Admin"),
        ("teacher", "Teacher"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=20, choices=ROLES, default="student")
    phone = models.CharField(max_length=20, blank=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="customuser_set",  # changed from the default 'user_set'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="customuser_permissions_set",
    )

    @property
    def full_name(self):
        # Returns a concatenation of first and last names.
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.username} ({self.role})"


class RoleChangeRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="role_change_requests"
    )
    requested_role = models.CharField(max_length=20, choices=CustomUser.ROLES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Role change for {self.user.username} to {self.requested_role} ({self.status})"


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_default_role(sender, instance, created, **kwargs):
    if created and not instance.role:
        # Assign the default role as 'student' if not explicitly set
        instance.role = "student"
        instance.save()


# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    RoleChangeRequestCreateView,
    RoleChangeRequestListView,
    RoleChangeRequestUpdateView,
)

urlpatterns = [
    # Class-based registration view
    path("register/", RegisterView.as_view(), name="register"),
    # Class-based login view (customized)
    path("login/", LoginView.as_view(), name="login"),
    # Class-based logout view (customized)
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "role-change/request/",
        RoleChangeRequestCreateView.as_view(),
        name="role-change-request",
    ),
    path(
        "role-change/requests/list/",
        RoleChangeRequestListView.as_view(),
        name="role-change-request-list",
    ),
    path(
        "role-change/requests/<int:pk>/update/",
        RoleChangeRequestUpdateView.as_view(),
        name="role-change-request-update",
    ),
]
from django.utils import timezone


from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import (
    FormView,
    TemplateView,
    CreateView,
    ListView,
    UpdateView,
)

# from core.mixins import RoleRequiredMixin
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    RoleChangeRequest,
    RoleChangeRequestForm,
)


class RegisterView(FormView):
    """
    Handles user registration with role-based group assignment.
    """

    template_name = "accounts/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        user = form.save(commit=False)
        role = form.cleaned_data.get("role")

        # Save user first
        user.save()

        # Assign user to group based on role
        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        messages.success(
            self.request, "Registration successful! You are now logged in."
        )
        login(self.request, user)  # Auto login after registration
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "Registration failed. Please correct the errors below."
        )
        return super().form_invalid(form)


class LoginView(FormView):
    """
    Handles user login with Bootstrap-styled forms.
    """

    template_name = "accounts/login.html"
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Welcome back, {user.get_username()}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid credentials. Please try again.")
        return super().form_invalid(form)


class LogoutView(TemplateView):
    """
    Handles user logout and redirects to login page.
    """

    template_name = "accounts/logout.html"

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(self.request, "You have been logged out successfully.")
        return redirect("login")


# View for users to request a role change.
class RoleChangeRequestCreateView(LoginRequiredMixin, CreateView):
    model = RoleChangeRequest
    form_class = RoleChangeRequestForm
    template_name = "accounts/request_role_change.html"
    success_url = reverse_lazy("role-change-request-list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Prevent requesting the same role as the current one.
        if form.instance.requested_role == self.request.user.role:
            form.add_error("requested_role", "You already have this role.")
            return self.form_invalid(form)
        return super().form_valid(form)


# Mixin to restrict views to admin users.
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == "admin"


# View for admin to see all pending role change requests.
class RoleChangeRequestListView(LoginRequiredMixin, ListView):
    model = RoleChangeRequest
    template_name = "accounts/role_change_request_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        return RoleChangeRequest.objects.filter(status="pending")


# View for admin to update (approve or reject) a role change request.


class RoleChangeRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = RoleChangeRequest
    fields = ["status"]
    template_name = "accounts/role_change_request_update.html"
    success_url = reverse_lazy("role-change-request-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.status == "approved":
            user = form.instance.user
            user.role = form.instance.requested_role
            user.save()
        form.instance.reviewed_at = timezone.now()
        form.instance.save()
        return response


from django.contrib import admin
from .models import Attendance

admin.site.register(Attendance)
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


from django.db import models
from students.models import Student
from teachers.models import Teacher
from school_class.models import Class


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )
    class_assigned = models.ForeignKey(
        Class, on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=[("Present", "Present"), ("Absent", "Absent")]
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

    class Meta:
        permissions = [
            ("can_mark_attendance", "Can mark attendance"),
            ("can_view_attendance", "Can view attendance"),
            ("can_edit_attendance", "Can edit attendance"),
        ]


from django.urls import path
from .views import (
    AttendanceListView,
    AttendanceCreateView,
    AttendanceReportPDFView,
    AttendanceUpdateView,
)

urlpatterns = [
    path("", AttendanceListView.as_view(), name="attendance-list"),
    path("create/", AttendanceCreateView.as_view(), name="attendance-create"),
    path("update/<int:pk>/", AttendanceUpdateView.as_view(), name="attendance-update"),
    path("report/", AttendanceReportPDFView.as_view(), name="attendance-report"),
]
from core.mixins import RoleRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, FormView
from django.urls import reverse_lazy
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Attendance
from .forms import AttendanceForm, AttendanceReportForm


class AttendanceListView(RoleRequiredMixin, ListView):
    model = Attendance
    template_name = "attendance/attendance_list.html"
    context_object_name = "attendances"
    ordering = ["-date"]
    permission_required = "attendance.can_view_attendance"
    allowed_roles = ["admin", "teacher"]


class AttendanceCreateView(RoleRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "attendance/attendance_form.html"
    success_url = reverse_lazy("attendance-list")
    permission_required = "attendance.can_mark_attendance"
    allowed_roles = ["admin", "teacher"]

    def form_valid(self, form):
        # Automatically assign the logged-in teacher if available.
        if hasattr(self.request.user, "teacher"):
            form.instance.teacher = self.request.user.teacher
        return super().form_valid(form)


class AttendanceUpdateView(RoleRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "attendance/attendance_form.html"
    success_url = reverse_lazy("attendance-list")
    permission_required = "attendance.can_edit_attendance"
    allowed_roles = ["admin", "teacher"]


class AttendanceReportPDFView(RoleRequiredMixin, FormView):
    template_name = "attendance/attendance_report_form.html"
    form_class = AttendanceReportForm
    permission_required = "attendance.can_view_attendance"
    allowed_roles = ["admin", "teacher"]

    def form_valid(self, form):
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]

        # Filter attendance records within the date range.
        attendances = Attendance.objects.filter(
            date__range=[start_date, end_date]
        ).order_by("date")

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="attendance_report.pdf"'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 14)
        p.drawString(100, 800, "Attendance Report")
        p.setFont("Helvetica", 10)
        p.drawString(100, 780, f"From: {start_date} To: {end_date}")

        # Draw table header.
        y = 750
        p.drawString(50, y, "Student")
        p.drawString(250, y, "Date")
        p.drawString(350, y, "Status")
        y -= 20

        for attendance in attendances:
            if y < 50:
                p.showPage()
                y = 800
            p.drawString(50, y, str(attendance.student))
            p.drawString(250, y, str(attendance.date))
            p.drawString(350, y, attendance.status)
            y -= 20

        p.showPage()
        p.save()
        return response


import logging
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseForbidden

# Initialize logger for tracking unauthorized access
logger = logging.getLogger(__name__)


class RoleRequiredMixin(UserPassesTestMixin):
    """
    A mixin to restrict access based on user roles.
    - Ensures only allowed roles or superusers can access views.
    - Redirects unauthorized users with appropriate messages.
    - Logs unauthorized access attempts.
    - Renders a custom Bootstrap error page for unauthorized access.
    """

    allowed_roles = []
    redirect_url = "login"  # Default redirect for unauthenticated users
    error_template_name = "errors/403.html"  # Template for displaying errors

    def test_func(self):
        """Check if the user is allowed to access the view."""
        try:
            request = getattr(self, "request", None)
            if not request:
                logger.error("RoleRequiredMixin: self.request is not available.")
                return False

            user = request.user

            if not user.is_authenticated:
                logger.warning(
                    f"Unauthorized access attempt: Anonymous user tried to access {request.path}"
                )
                return False

            if user.is_superuser or user.role in self.allowed_roles:
                return True

            logger.warning(
                f"Unauthorized access: {user.username} ({user.role}) tried to access {request.path}"
            )
            return False

        except Exception as e:
            logger.error(f"Error in RoleRequiredMixin: {str(e)}", exc_info=True)
            return False

    def handle_no_permission(self):
        """
        Handle unauthorized access:
        - For unauthenticated users, redirect them with a warning message.
        - For authenticated but unauthorized users, render a custom error page
          with a Bootstrap styled template including an icon.
        """
        request = getattr(self, "request", None)
        if not request:
            # Fallback response if request object is missing
            return HttpResponseForbidden(
                "<h1>403 Forbidden</h1><p>Request object missing.</p>"
            )

        user = request.user

        # Redirect unauthenticated users
        if not user.is_authenticated:
            messages.warning(request, "You need to log in to access this page.")
            return redirect(self.redirect_url)

        # For authenticated users, show an error page with a Bootstrap template
        context = {
            "error_title": "403 Forbidden",
            "error_message": "You are not authorized to view this page.",
            "error_icon": "exclamation-triangle",  # Example: Font Awesome icon name
        }
        return render(request, self.error_template_name, context, status=403)


def custom_404(request, exception):
    """
    Custom 404 error handler that renders a Bootstrap-styled error page.
    """
    context = {
        "error_title": "404 Not Found",
        "error_message": "The page you are looking for does not exist. Please check the URL or return to the homepage.",
        "error_icon": "exclamation-triangle",  # Example: Font Awesome icon name
    }
    return render(request, "errors/404.html", context, status=404)


from django.contrib import admin
from school_class.models import Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("name", "class_teacher")
    search_fields = ("name",)


from django import forms
from .models import Class
from teachers.models import Teacher
from subjects.models import Subject


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ["name", "class_teacher", "teachers", "subjects"]

    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        # Order class_teacher and teachers by the teacher's first name from the related user
        self.fields["class_teacher"].queryset = Teacher.objects.order_by(
            "user__first_name"
        )
        self.fields["teachers"].queryset = Teacher.objects.order_by("user__first_name")
        # Order subjects by name
        self.fields["subjects"].queryset = Subject.objects.order_by("name")


from django.db import models
from teachers.models import Teacher


class Class(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class_teacher = models.OneToOneField(
        Teacher, on_delete=models.SET_NULL, null=True, related_name="managed_classes"
    )
    teachers = models.ManyToManyField(
        Teacher,
        related_name="teaching_classes",
        through="subjects.ClassTeacherSubject",
        through_fields=("class_obj", "teacher"),
    )
    subjects = models.ManyToManyField(
        "subjects.Subject",
        related_name="classes",
        through="subjects.ClassTeacherSubject",
        through_fields=("class_obj", "subject"),
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_class_name")
        ]
        permissions = [
            ("can_view_class", "Can view class"),
            ("can_edit_class", "Can edit class"),
        ]


from django.urls import path
from . import views

urlpatterns = [
    path("", views.ClassListView.as_view(), name="class_list"),
    path("create/", views.ClassCreateView.as_view(), name="class_create"),
    path("<int:pk>/", views.ClassDetailView.as_view(), name="class_detail"),
    path("<int:pk>/update/", views.ClassUpdateView.as_view(), name="class_update"),
    path("<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),
]
from core.mixins import RoleRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from subjects.models import ClassTeacherSubject
from .models import Class
from .forms import ClassForm


class ClassListView(RoleRequiredMixin, ListView):
    model = Class
    template_name = "class/class_list.html"
    context_object_name = "classes"
    ordering = ["name"]
    allowed_roles = ["admin", "teacher", "student"]


class ClassDetailView(RoleRequiredMixin, DetailView):
    model = Class
    template_name = "class/class_detail.html"
    context_object_name = "class"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unique_subjects"] = self.object.subjects.distinct()
        return context


class ClassCreateView(RoleRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm
    template_name = "class/class_form.html"
    success_url = reverse_lazy("class_list")

    def form_valid(self, form):
        # Save the Class instance first
        class_instance = form.save()

        # Get selected teachers and subjects
        teachers = form.cleaned_data["teachers"]
        subjects = form.cleaned_data["subjects"]

        # Ensure that each teacher-subject pair is correctly assigned in ClassTeacherSubject
        for teacher in teachers:
            for subject in subjects:
                ClassTeacherSubject.objects.create(
                    class_obj=class_instance, teacher=teacher, subject=subject
                )

        return super().form_valid(form)


class ClassUpdateView(RoleRequiredMixin, UpdateView):
    model = Class
    form_class = ClassForm
    template_name = "class/class_form.html"
    success_url = reverse_lazy("class_list")


class ClassDeleteView(RoleRequiredMixin, DeleteView):
    model = Class
    template_name = "class/class_confirm_delete.html"
    success_url = reverse_lazy("class_list")


"""
Django settings for school_management project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# settings.py
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "student_list"
LOGOUT_REDIRECT_URL = "login"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
import os

SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = ["*"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # new added
    "accounts.apps.AccountsConfig",
    "students.apps.StudentsConfig",
    "teachers.apps.TeachersConfig",
    "school_class.apps.SchoolClassConfig",
    "subjects.apps.SubjectsConfig",
    "time_tables.apps.TimeTablesConfig",
    "attendance.apps.AttendanceConfig",
    "crispy_forms",
    "django_extensions",
]

AUTH_USER_MODEL = "accounts.CustomUser"

CRISPY_TEMPLATE_PACK = "bootstrap4"  # or 'bootstrap5' if you prefer

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Message storage settings (optional)
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ROOT_URLCONF = "school_management.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "school_management.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from core import mixins  # Import the mixins module containing custom_404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("students/", permanent=True)),
    path("accounts/", include("accounts.urls")),
    path("attendance/", include("attendance.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("classes/", include("school_class.urls")),
    path("subjects/", include("subjects.urls")),
    path("timetables/", include("time_tables.urls")),
]

# Register the custom 404 error handler
handler404 = mixins.custom_404
# students/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, class_name):
    """
    Adds a CSS class to a form field widget.
    """
    return field.as_widget(attrs={"class": class_name})


from django.contrib import admin
from .models import Student


# Register Student model in admin
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "phone", "address", "class_obj")
    search_fields = [
        "user__username",
        "user__email",
        "class_obj__name",
    ]  # Searching by user info and class name
    list_filter = ("class_obj",)  # Filtering by Class
    ordering = ("user",)  # Sorting by user name
    readonly_fields = ("enrollment_date",)  # Making enrollment date readonly

    # Adding custom permissions for student model
    def has_delete_permission(self, request, obj=None):
        if request.user.role == "admin":
            return True
        return False


admin.site.register(Student, StudentAdmin)
from django import forms
from .models import Student
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, ButtonHolder, Submit
from accounts.models import CustomUser


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ["user", "age", "phone", "address", "class_obj", "subjects"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter Age"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Phone Number"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Enter Address"}
            ),
            "class_obj": forms.Select(
                attrs={"class": "form-control", "id": "class-select"}
            ),
            "subject": forms.CheckboxSelectMultiple(
                attrs={"class": "form-control", "disabled": True}
            ),
        }
        labels = {
            "user": "Student (User)",
            "age": "Age",
            "phone": "Phone Number",
            "address": "Address",
            "class_obj": "Class",
            "subjects": "Subjects",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subjects"].queryset = (
            Subject.objects.none()
        )  # Start with no subjects selected
        self.fields["subjects"].widget.attrs[
            "disabled"
        ] = True  # Make the field non-editable
        # Only show users not already linked to a student
        self.fields["user"].queryset = CustomUser.objects.filter(
            student_profile__isnull=True
        )
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Fieldset(
                "Student Information",
                Div("user", "age", "phone", "address"),
                "class_obj",
                "subjects",
            ),
            ButtonHolder(Submit("submit", "Submit", css_class="btn btn-primary")),
        )


from django import forms
from .models import Student
from school_class.models import Class
from subjects.models import Subject


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["user", "age", "phone", "address", "class_obj", "subjects"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter Age"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Phone Number"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Enter Address"}
            ),
            "class_obj": forms.Select(
                attrs={"class": "form-control", "id": "class-select"}
            ),
            "subjects": forms.CheckboxSelectMultiple(
                attrs={"class": "form-control", "disabled": True}
            ),
        }
        labels = {
            "user": "Student (User)",
            "age": "Age",
            "phone": "Phone Number",
            "address": "Address",
            "class_obj": "Class",
            "subjects": "Subjects",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


from django.db import models
from accounts.models import CustomUser
from school_class.models import Class
from subjects.models import Subject
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student_profile",
        help_text="The user associated with this student.",
    )
    first_name = models.CharField(
        max_length=50, help_text="First name of the student.", null=True
    )
    last_name = models.CharField(
        max_length=50, help_text="Last name of the student.", null=True
    )
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(12), MaxValueValidator(25)],
        help_text="Age must be between 12 and 25.",
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        help_text="Optional phone number.",
    )
    address = models.TextField(help_text="Home address of the student.")
    enrollment_date = models.DateField(
        auto_now_add=True, help_text="Date when student was enrolled."
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        related_name="students",
        help_text="The class this student is enrolled in.",
    )
    subjects = models.ManyToManyField(
        Subject,
        related_name="students",
        blank=True,
        help_text="Subjects the student is studying.",
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        # Capitalize and save user names
        self.user.first_name = self.user.first_name.strip().capitalize()
        self.user.last_name = self.user.last_name.strip().capitalize()
        self.user.save()  # Save user changes first
        super().save(*args, **kwargs)
        if self.class_obj:
            self.subjects.set(self.class_obj.subjects.all())

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [models.Index(fields=["user"])]
        permissions = [
            ("can_view_student", "Can view student"),
            ("can_edit_student", "Can edit student"),
        ]


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Student
from subjects.models import Subject


@receiver(post_save, sender=Student)
def assign_subjects_to_student(sender, instance, created, **kwargs):
    if created and instance.class_obj:
        subject_mapping = {
            "12th Science A Groups": [
                "Mathematics",
                "Physics",
                "Chemistry",
                "Computer",
                "English",
            ],
            "12th Science B Groups": [
                "Physics",
                "Chemistry",
                "Biology",
                "Computer",
                "English",
            ],
        }

        subject_names = subject_mapping.get(instance.class_obj.name, [])
        if subject_names:
            subjects = Subject.objects.filter(name__in=subject_names)
            if subjects.exists():
                instance.subjects.set(subjects)


from django.urls import path
from .views import (
    StudentListView,
    StudentDetailView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
)
from .views import home, get_class_subjects

urlpatterns = [
    path("home/", home, name="home"),
    path("get-class-subjects/", get_class_subjects, name="get_class_subjects"),
    path("", StudentListView.as_view(), name="student_list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="student_detail"),
    path("create/", StudentCreateView.as_view(), name="student_create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student_update"),
    path("<int:pk>/delete/", StudentDeleteView.as_view(), name="student_delete"),
]
from core.mixins import RoleRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Student
from .forms import StudentForm

from django.shortcuts import render

from django.http import JsonResponse
from school_class.models import Class


def get_class_subjects(request):
    class_id = request.GET.get("class_id")
    subjects = []

    if class_id:
        try:
            class_obj = Class.objects.get(id=class_id)
            subjects = list(class_obj.subjects.values("id", "name"))
        except Class.DoesNotExist:
            pass

    return JsonResponse({"subjects": subjects})


def home(request):
    return render(request, "home.html")


class StudentListView(RoleRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 10
    allowed_roles = ["admin", "teacher", "student"]  # Add appropriate roles

    def get_queryset(self):
        search_query = self.request.GET.get("name", "")
        if search_query:
            return Student.objects.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(user__username__icontains=search_query)
            )
        return Student.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("name", "")
        return context


# Detail View: Display a single student's details
class StudentDetailView(RoleRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"
    context_object_name = "student"
    allowed_roles = ["admin", "teacher", "student"]


# Create View: Add a new student
class StudentCreateView(RoleRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")
    allowed_roles = ["admin"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "Students generated and saved successfully."
        return context


# Update View: Edit an existing student
class StudentUpdateView(RoleRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("student_list")
    allowed_roles = ["admin", "teacher"]


# Delete View: Delete a student
class StudentDeleteView(RoleRequiredMixin, DeleteView):
    model = Student
    template_name = "students/student_confirm_delete.html"
    success_url = reverse_lazy("student_list")
    allowed_roles = ["admin"]


from django.contrib import admin
from .models import Subject, ClassTeacherSubject
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


# Register Subject model in admin
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]


admin.site.register(Subject, SubjectAdmin)


# Register ClassTeacherSubject model in admin
class ClassTeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ("class_obj", "teacher", "subject")
    list_filter = ("class_obj", "teacher", "subject")


admin.site.register(ClassTeacherSubject, ClassTeacherSubjectAdmin)

# Removed direct permission creation from here.
from django import forms
from .models import Subject
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


from django.db import models
from teachers.models import Teacher
from school_class.models import Class


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("can_view_subject", "Can view subject"),
            ("can_edit_subject", "Can edit subject"),
        ]


class ClassTeacherSubject(models.Model):
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="class_teacher_subjects"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="teacher_class_subjects"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="subject_class_subjects"
    )

    class Meta:
        # You can remove unique_together if using UniqueConstraint below
        unique_together = ("class_obj", "teacher", "subject")
        constraints = [
            models.UniqueConstraint(
                fields=["class_obj", "teacher", "subject"],
                name="unique_class_teacher_subject",
            )
        ]
        permissions = [
            ("can_assign_subject", "Can assign subject to class teacher"),
        ]


# subjects/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Subject


@receiver(post_migrate)
def add_subject_permissions(sender, **kwargs):
    # Optionally, check if the sender is the subjects app:
    # if sender.name != 'subjects':
    #     return

    content_type = ContentType.objects.get_for_model(Subject)
    Permission.objects.get_or_create(
        codename="can_assign_subject",
        name="Can assign subject to class teacher",
        content_type=content_type,
    )
    print("Subject permissions added.")


from django.urls import path
from subjects import views


urlpatterns = [
    path("", views.SubjectListView.as_view(), name="subject_list"),
    path("<int:pk>/", views.SubjectDetailView.as_view(), name="subject_detail"),
    path("create/", views.SubjectCreateView.as_view(), name="subject_create"),
    path("<int:pk>/update/", views.SubjectUpdateView.as_view(), name="subject_update"),
    path("<int:pk>/delete/", views.SubjectDeleteView.as_view(), name="subject_delete"),
]
from core.mixins import RoleRequiredMixin
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
from .forms import SubjectForm


class SubjectListView(RoleRequiredMixin, ListView):
    model = Subject
    template_name = "subjects/subject_list.html"
    context_object_name = "subjects"
    ordering = ["name"]
    allowed_roles = ["admin", "teacher", "student"]

    def get_queryset(self):
        return Subject.objects.all()


class SubjectDetailView(RoleRequiredMixin, DetailView):
    model = Subject
    template_name = "subjects/subject_detail.html"
    context_object_name = "subject"
    allowed_roles = ["admin"]


class SubjectCreateView(RoleRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "subjects/subject_form.html"
    success_url = reverse_lazy("subject_list")
    allowed_roles = ["admin"]

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
        classes = form.cleaned_data.get("classes")
        teachers = form.cleaned_data.get("teachers")
        subject = self.object

        for class_obj in classes:
            for teacher in teachers:
                ClassTeacherSubject.objects.get_or_create(
                    class_obj=class_obj, teacher=teacher, subject=subject
                )


class SubjectUpdateView(RoleRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "subjects/subject_form.html"
    success_url = reverse_lazy("subject_list")
    allowed_roles = ["admin"]

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
        classes = form.cleaned_data.get("classes")
        teachers = form.cleaned_data.get("teachers")
        subject = self.object

        ClassTeacherSubject.objects.filter(subject=subject).delete()

        for class_obj in classes:
            for teacher in teachers:
                ClassTeacherSubject.objects.get_or_create(
                    class_obj=class_obj, teacher=teacher, subject=subject
                )


class SubjectDeleteView(RoleRequiredMixin, DeleteView):
    model = Subject
    template_name = "subjects/subject_confirm_delete.html"
    context_object_name = "subject"
    success_url = reverse_lazy("subject_list")
    allowed_roles = ["admin"]


from django.contrib import admin
from teachers.models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("get_full_name", "get_email", "subject_list", "phone", "address")
    search_fields = ["user__username", "user__email", "subject__name"]
    list_filter = ("subject",)
    ordering = ("user__first_name",)

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = "Name"

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"

    def subject_list(self, obj):
        return ", ".join([str(s) for s in obj.subject.all()])

    subject_list.short_description = "Subjects"

    def has_delete_permission(self, request, obj=None):
        return request.user.role == "admin"


from django import forms
from .models import Teacher
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, ButtonHolder, Submit


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ["user", "age", "phone", "address", "subject"]
        widgets = {
            "user": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter Age"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Phone Number"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Enter Address"}
            ),
            "subject": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "user": "Teacher (User)",
            "age": "Age",
            "phone": "Phone Number",
            "address": "Address",
            "subject": "Subjects",
        }

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Fieldset(
                "Teacher Information",
                Div("user", "age", "phone", "address"),
                "subject",
            ),
            ButtonHolder(Submit("submit", "Submit", css_class="btn btn-primary")),
        )


# teachers/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Teacher


@receiver(post_migrate)
def add_teacher_permissions(sender, **kwargs):
    # Optionally, you can restrict this to run only when your app is migrated.
    # For example:
    # if sender.name != 'teachers':
    #     return

    Permission.objects.get_or_create(
        codename="can_assign_teacher",
        name="Can assign teacher to class",
        content_type=ContentType.objects.get_for_model(Teacher),
    )
    Permission.objects.get_or_create(
        codename="can_view_teacher",
        name="Can view teacher details",
        content_type=ContentType.objects.get_for_model(Teacher),
    )


from django.urls import path
from .views import (
    TeacherListView,
    TeacherCreateView,
    TeacherDetailView,
    TeacherUpdateView,
    TeacherDeleteView,
)

urlpatterns = [
    path("", TeacherListView.as_view(), name="teacher_list"),
    path("<int:pk>/", TeacherDetailView.as_view(), name="teacher_detail"),
    path("create/", TeacherCreateView.as_view(), name="teacher_create"),
    path("<int:pk>/update/", TeacherUpdateView.as_view(), name="teacher_update"),
    path("<int:pk>/delete/", TeacherDeleteView.as_view(), name="teacher_delete"),
]


from core.mixins import RoleRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from .models import Teacher
from .forms import TeacherForm


class TeacherListView(RoleRequiredMixin, PermissionRequiredMixin, ListView):
    model = Teacher
    template_name = "teachers/teacher_list.html"
    context_object_name = "teachers"
    ordering = ["user__first_name"]
    paginate_by = 6
    permission_required = "teachers.can_view_teacher"
    allowed_roles = ["admin", "teacher"]

    def get_queryset(self):
        search_query = self.request.GET.get("name", "")
        if search_query:
            return Teacher.objects.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(user__username__icontains=search_query)
            )
        return Teacher.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("name", "")
        return context


class TeacherCreateView(RoleRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "teachers/teacher_form.html"
    success_url = reverse_lazy("teacher_list")
    # Use Django's default add permission
    permission_required = "teachers.add_teacher"
    allowed_roles = ["admin"]


class TeacherUpdateView(RoleRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "teachers/teacher_form.html"
    success_url = reverse_lazy("teacher_list")
    # Use Django's default change permission
    permission_required = "teachers.change_teacher"
    allowed_roles = ["admin"]


class TeacherDeleteView(RoleRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_confirm_delete.html"
    success_url = reverse_lazy("teacher_list")
    # Use Django's default delete permission
    permission_required = "teachers.delete_teacher"
    allowed_roles = ["admin"]


class TeacherDetailView(RoleRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Teacher
    template_name = "teachers/teacher_detail.html"
    context_object_name = "teacher"
    permission_required = "teachers.can_view_teacher"
    allowed_roles = ["admin"]


from django.contrib import admin
from time_tables.models import TimeSlot, Timetable


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "is_break")
    list_filter = ("is_break",)
    ordering = ("start_time",)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("class_model", "subject", "teacher", "time_slot", "day_of_week")
    list_filter = ("day_of_week", "class_model")
    ordering = ("day_of_week", "time_slot__start_time")


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
            "start_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
            "end_time": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"}
            ),
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
    time_slot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.all(), label="Time Slot"
    )
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

        if time_slot and time_slot.is_break:
            if subject or teacher:
                raise forms.ValidationError(
                    "Break slots cannot be assigned subjects or teachers."
                )
        elif time_slot and not time_slot.is_break:
            if not subject or not teacher:
                raise forms.ValidationError(
                    "Both subject and teacher are required for non-break slots."
                )
            if not ClassTeacherSubject.objects.filter(
                teacher=teacher, subject=subject, class_obj=class_model
            ).exists():
                raise forms.ValidationError(
                    f"Teacher {teacher} is not assigned to teach {subject} in this class."
                )
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


from django.db import models
from school_class.models import Class
from subjects.models import Subject, ClassTeacherSubject
from teachers.models import Teacher
from django.core.exceptions import ValidationError


class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)

    class Meta:
        unique_together = ("start_time", "end_time")
        ordering = ["start_time"]
        permissions = [
            ("can_view_timeslot", "Can view time slot"),
            ("can_edit_timeslot", "Can edit time slot"),
        ]

    def __str__(self):
        if self.is_break:
            return f"Break: {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        return f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"


class Timetable(models.Model):
    DAYS_OF_WEEK_CHOICES = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
    ]

    class_model = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="timetables"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="timetables",
        null=True,
        blank=True,
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="timetables",
        null=True,
        blank=True,
    )
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK_CHOICES)

    class Meta:
        unique_together = ("class_model", "time_slot", "day_of_week")
        ordering = ["day_of_week", "time_slot__start_time"]
        permissions = [
            ("can_view_timetable", "Can view timetable"),
            ("can_edit_timetable", "Can edit timetable"),
        ]

    def clean(self):
        if not self.time_slot.is_break:
            overlapping_teachers = Timetable.objects.filter(
                teacher=self.teacher,
                time_slot=self.time_slot,
                day_of_week=self.day_of_week,
            ).exclude(pk=self.pk)
            if overlapping_teachers.exists():
                raise ValidationError(
                    f"Teacher {self.teacher} is already assigned to another class at this time."
                )

            overlapping_subjects = Timetable.objects.filter(
                class_model=self.class_model,
                time_slot=self.time_slot,
                day_of_week=self.day_of_week,
            ).exclude(pk=self.pk)

            if overlapping_subjects.exists():
                raise ValidationError(
                    "This subject is already assigned to the same class and time slot."
                )

            if self.subject and self.teacher:
                if not ClassTeacherSubject.objects.filter(
                    teacher=self.teacher,
                    subject=self.subject,
                    class_obj=self.class_model,
                ).exists():
                    raise ValidationError(
                        f"Teacher {self.teacher} is not qualified to teach {self.subject} in this class."
                    )

        if self.time_slot.is_break:
            if self.subject or self.teacher:
                raise ValidationError(
                    "Break slots cannot be assigned subjects or teachers."
                )
        elif not self.time_slot.is_break and not (self.subject and self.teacher):
            raise ValidationError(
                "Subject and Teacher are required for non-break slots."
            )

    def __str__(self):
        if self.time_slot.is_break:
            return f"{self.day_of_week} - {self.time_slot} (Break)"
        return f"{self.class_model.name} - {self.subject.name} by {self.teacher.user.get_full_name()} on {self.day_of_week} at {self.time_slot}"


from django.urls import path
from . import views

urlpatterns = [
    # CRUD URLs for Timetable entries
    path("", views.TimetableListView.as_view(), name="timetable_list"),
    path("add/", views.TimetableCreateView.as_view(), name="timetable_create"),
    path("<int:pk>/", views.TimetableDetailView.as_view(), name="timetable_detail"),
    path(
        "<int:pk>/edit/", views.TimetableUpdateView.as_view(), name="timetable_update"
    ),
    path(
        "<int:pk>/delete/", views.TimetableDeleteView.as_view(), name="timetable_delete"
    ),
    # CRUD URLs for TimeSlots
    path("timeslots/", views.TimeSlotListView.as_view(), name="timeslot_list"),
    path("timeslots/add/", views.TimeSlotCreateView.as_view(), name="timeslot_create"),
    path(
        "timeslots/<int:pk>/",
        views.TimeSlotDetailView.as_view(),
        name="timeslot_detail",
    ),
    path(
        "timeslots/<int:pk>/edit/",
        views.TimeSlotUpdateView.as_view(),
        name="timeslot_update",
    ),
    path(
        "timeslots/<int:pk>/delete/",
        views.TimeSlotDeleteView.as_view(),
        name="timeslot_delete",
    ),
    # New scheduling view using OR-Tools (generates & saves timetable)
    path("generate/", views.TimetableGenerateView.as_view(), name="timetable_generate"),
    # New download URL (CSV download example)
    path("download/", views.TimetableDownloadView.as_view(), name="timetable_download"),
]


# Standard Library Imports
import csv

# Django Imports
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.utils.timezone import now

# Third‑Party Imports
from ortools.sat.python import cp_model
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas

# Local App Imports
from core.mixins import RoleRequiredMixin
from .models import Timetable, TimeSlot
from .forms import TimetableForm, TimeSlotForm
from teachers.models import Teacher
from subjects.models import Subject, ClassTeacherSubject
from school_class.models import Class


###############################################
# CRUD Views for Timetable
###############################################


class TimetableListView(RoleRequiredMixin, ListView):
    model = Timetable
    template_name = "time_tables/timetable_list.html"
    context_object_name = "timetables"
    allowed_roles = ["admin", "teacher", "student"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_class_name = self.request.GET.get("class_name")
        context["selected_class"] = None
        context["available_classes"] = Class.objects.all()

        if selected_class_name:
            try:
                context["selected_class"] = Class.objects.get(name=selected_class_name)
            except Class.DoesNotExist:
                messages.error(self.request, f"Class {selected_class_name} not found")
        context["days"] = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        context["timeslots"] = TimeSlot.objects.all().order_by("start_time")

        timetables = {}
        if context["selected_class"]:
            entries = Timetable.objects.filter(
                class_model=context["selected_class"]
            ).select_related("time_slot", "subject", "teacher")
            for day in context["days"]:
                day_entries = entries.filter(day_of_week=day)
                timetables[day] = {entry.time_slot.id: entry for entry in day_entries}
        context["timetables"] = timetables
        return context


class TimetableDetailView(RoleRequiredMixin, DetailView):
    model = Timetable
    template_name = "time_tables/timetable_detail.html"
    context_object_name = "timetable"
    allowed_roles = [
        "admin",
    ]


class TimetableCreateView(RoleRequiredMixin, CreateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "time_tables/timetable_form.html"
    success_url = reverse_lazy("timetable_list")
    allowed_roles = [
        "admin",
    ]


class TimetableUpdateView(RoleRequiredMixin, UpdateView):
    model = Timetable
    form_class = TimetableForm
    template_name = "time_tables/timetable_form.html"
    success_url = reverse_lazy("timetable_list")
    allowed_roles = [
        "admin",
    ]


class TimetableDeleteView(RoleRequiredMixin, DeleteView):
    model = Timetable
    template_name = "time_tables/timetable_confirm_delete.html"
    context_object_name = "timetable"
    success_url = reverse_lazy("timetable_list")
    permission_required = "time_tables.can_edit_timetable"


###############################################
# CRUD Views for TimeSlot
###############################################


class TimeSlotListView(ListView):
    model = TimeSlot
    template_name = "time_slot/time_slot_list.html"
    context_object_name = "timeslots"
    ordering = ["start_time"]


class TimeSlotDetailView(DetailView):
    model = TimeSlot
    template_name = "time_slot/time_slot_detail.html"
    context_object_name = "timeslot"


class TimeSlotCreateView(CreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = "time_slot/time_slot_form.html"
    success_url = reverse_lazy("timeslot_list")


class TimeSlotUpdateView(UpdateView):
    model = TimeSlot
    form_class = TimeSlotForm
    template_name = "time_slot/time_slot_form.html"
    success_url = reverse_lazy("timeslot_list")


class TimeSlotDeleteView(DeleteView):
    model = TimeSlot
    template_name = "time_slot/time_slot_confirm_delete.html"
    context_object_name = "timeslot"
    success_url = reverse_lazy("timeslot_list")


class TimetableGenerateView(RoleRequiredMixin, TemplateView):
    template_name = "time_tables/timetable_generate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Provide a list of available classes for the selection form.
        available_classes = Class.objects.all()
        context["available_classes"] = available_classes

        # Get the target class from GET parameters (if submitted).
        target_class_name = self.request.GET.get("class_name")
        if not target_class_name:
            # If no class selected yet, simply return the form.
            return context

        try:
            selected_class = Class.objects.get(name=target_class_name)
        except Class.DoesNotExist:
            context["error"] = f"Class '{target_class_name}' not found."
            return context

        # Define days for a 6-day week.
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        all_timeslots = list(TimeSlot.objects.all().order_by("start_time"))
        lesson_timeslots = [ts for ts in all_timeslots if not ts.is_break]

        # Build assignments for all classes (for conflict checking across classes).
        classes = list(Class.objects.all())
        class_assignments = {}
        for cls in classes:
            assignments_qs = ClassTeacherSubject.objects.filter(class_obj=cls)
            assignments = []
            for cts in assignments_qs:
                assignments.append(
                    {
                        "subject_id": cts.subject.id,
                        "teacher_id": cts.teacher.id,
                        "subject_name": cts.subject.name,
                        "teacher_name": cts.teacher.user.username,
                        # assuming teacher's display name comes from the related user
                    }
                )
            # If assignments are fewer than lesson slots, append dummy assignments.
            if len(assignments) < len(lesson_timeslots):
                dummy_count = len(lesson_timeslots) - len(assignments)
                for i in range(dummy_count):
                    assignments.append(
                        {
                            "subject_id": 0,  # Dummy subject id
                            "teacher_id": 1000000
                            + i,  # Dummy teacher id (ensure these don't conflict with real ones)
                            "subject_name": "Free Period",
                            "teacher_name": "N/A",
                        }
                    )
            # If there are extra assignments, slice them to match lesson slot count.
            elif len(assignments) > len(lesson_timeslots):
                assignments = assignments[: len(lesson_timeslots)]
            class_assignments[cls.id] = assignments

        # Build the CP‑SAT model.
        model = cp_model.CpModel()
        decision_vars = {}
        teacher_vars = {}

        for cls in classes:
            assignments = class_assignments[cls.id]
            n_assignments = len(assignments)
            teacher_ids_list = [assignment["teacher_id"] for assignment in assignments]
            for day in days:
                day_vars = []
                for slot_index in range(n_assignments):
                    var = model.NewIntVar(
                        0, n_assignments - 1, f"cls{cls.id}_{day}_slot{slot_index}"
                    )
                    decision_vars[(cls.id, day, slot_index)] = var
                    day_vars.append(var)
                    t_var = model.NewIntVar(
                        min(teacher_ids_list),
                        max(teacher_ids_list),
                        f"cls{cls.id}_{day}_slot{slot_index}_teacher",
                    )
                    teacher_vars[(cls.id, day, slot_index)] = t_var
                    # Link the decision variable with the teacher ID from the assignment.
                    model.AddElement(var, teacher_ids_list, t_var)
                # Each lesson slot in a day gets a unique assignment.
                model.AddAllDifferent(day_vars)

        # Ensure that for each day and each lesson slot (across classes), teachers are not double-booked.
        for day in days:
            for slot_index in range(len(lesson_timeslots)):
                teacher_vars_this_slot = []
                for cls in classes:
                    teacher_vars_this_slot.append(
                        teacher_vars[(cls.id, day, slot_index)]
                    )
                model.AddAllDifferent(teacher_vars_this_slot)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            context["error"] = (
                "No feasible timetable found. Please check class assignments and timeslot configurations."
            )
            return context

        # Build the timetable solution structure.
        timetable_solution = {cls.id: {day: {} for day in days} for cls in classes}
        for cls in classes:
            lesson_counter = 0
            for ts in all_timeslots:
                if ts.is_break:
                    for day in days:
                        timetable_solution[cls.id][day][ts.id] = {
                            "is_break": True,
                            "display": f"Break ({ts.start_time.strftime('%I:%M %p')} - {ts.end_time.strftime('%I:%M %p')})",
                        }
                else:
                    for day in days:
                        var = decision_vars[(cls.id, day, lesson_counter)]
                        assign_index = solver.Value(var)
                        assignment = class_assignments[cls.id][assign_index]
                        # Check for a dummy assignment.
                        if assignment["subject_name"] == "Free Period":
                            display_text = "Free Period"
                        else:
                            display_text = f"{assignment['subject_name']}<br/>{assignment['teacher_name']}"
                        timetable_solution[cls.id][day][ts.id] = {
                            "is_break": False,
                            "subject": (
                                assignment["subject_name"]
                                if assignment["subject_name"] != "Free Period"
                                else ""
                            ),
                            "teacher": (
                                assignment["teacher_name"]
                                if assignment["teacher_name"] != "N/A"
                                else ""
                            ),
                            "display": display_text,
                        }
                    lesson_counter += 1

        # Save the generated timetable for the selected class.
        try:
            with transaction.atomic():
                # Delete any existing timetable for the class.
                Timetable.objects.filter(class_model=selected_class).delete()
                for day in days:
                    for ts in all_timeslots:
                        cell = timetable_solution[selected_class.id][day].get(ts.id)
                        if cell:
                            if ts.is_break or cell.get("subject") == "":
                                Timetable.objects.create(
                                    class_model=selected_class,
                                    time_slot=ts,
                                    day_of_week=day,
                                    subject=None,
                                    teacher=None,
                                )
                            else:
                                # Use the subject's name as usual.
                                subject_obj = Subject.objects.filter(
                                    name=cell["subject"]
                                ).first()
                                # For teacher, use the related user's username (change lookup field if needed).
                                teacher_obj = None
                                if cell["teacher"] and cell["teacher"] != "N/A":
                                    teacher_obj = Teacher.objects.filter(
                                        user__username=cell["teacher"]
                                    ).first()
                                Timetable.objects.create(
                                    class_model=selected_class,
                                    time_slot=ts,
                                    day_of_week=day,
                                    subject=subject_obj,
                                    teacher=teacher_obj,
                                )
        except Exception as e:
            context["error"] = f"An error occurred while saving the timetable: {e}"
            return context

        context["selected_class"] = selected_class
        context["days"] = days
        context["timeslots"] = all_timeslots
        context["timetable"] = timetable_solution[selected_class.id]
        context["message"] = "Timetable generated and saved successfully."
        return context


def add_page_number(canvas_obj, doc):
    """
    Adds the page number at the bottom-right of each page.
    """
    page_num = canvas_obj.getPageNumber()
    text = f"Page {page_num}"
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawRightString(doc.pagesize[0] - 40, 20, text)


class TimetableDownloadView(RoleRequiredMixin, View):
    allowed_roles = ["admin", "teacher", "student"]

    def get(self, request, *args, **kwargs):
        target_class_name = request.GET.get("class_name", "")
        try:
            selected_class = Class.objects.get(name=target_class_name)
        except Class.DoesNotExist:
            return HttpResponse("Class not found.", status=404)

        timetable_qs = Timetable.objects.filter(class_model=selected_class).order_by(
            "day_of_week", "time_slot__start_time"
        )

        # Create a PDF response.
        response = HttpResponse(content_type="application/pdf")
        filename = f"timetable_{selected_class.name.replace(' ', '_')}_{now().strftime('%Y%m%d')}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Create a PDF document with landscape letter size.
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=40,
        )
        elements = []

        # Custom styles for a professional look.
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="CellText",
                parent=styles["Normal"],
                fontSize=10,
                leading=12,
                alignment=1,  # Center aligned
                textColor=colors.HexColor("#2C3E50"),
            )
        )
        title_style = ParagraphStyle(
            name="Title",
            fontSize=26,
            leading=32,
            spaceAfter=20,
            alignment=1,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#2980B9"),
        )
        elements.append(Paragraph(f"{selected_class.name} Timetable", title_style))
        elements.append(Spacer(1, 12))

        # Prepare the table header.
        header = [
            "Time Slot",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        data = [header]

        # Map and sort time slots.
        timeslot_ids = sorted({entry.time_slot.id for entry in timetable_qs})
        timeslot_map = {}
        for entry in timetable_qs:
            ts = entry.time_slot
            timeslot_map[ts.id] = (
                f"{ts.start_time.strftime('%I:%M %p')} - {ts.end_time.strftime('%I:%M %p')}"
            )
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        schedule = {ts_id: {} for ts_id in timeslot_ids}
        for entry in timetable_qs:
            schedule[entry.time_slot.id][entry.day_of_week] = entry

        # Build table rows for each time slot.
        for ts_id in timeslot_ids:
            time_slot = timeslot_map.get(ts_id, "")
            row = [time_slot]
            for day in days:
                entry = schedule[ts_id].get(day)
                if entry:
                    subject = entry.subject.name if entry.subject else ""
                    teacher = (
                        entry.teacher.user.username
                        if entry.teacher and hasattr(entry.teacher, "user")
                        else ""
                    )
                    cell_content = f"<b>{subject}</b><br/><i>{teacher}</i>"
                    row.append(cell_content)
                else:
                    row.append("--")
            data.append(row)

        # Convert each cell to a Paragraph object.
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                if i == 0:  # header row
                    data[i][j] = Paragraph(f"<b>{cell}</b>", styles["Heading4"])
                else:
                    data[i][j] = Paragraph(cell, styles["CellText"])

        # Define column widths for the table.
        col_widths = [doc.width * 0.15] + [doc.width * 0.14] * 6
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Style the table with alternating row colors and padding.
        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498DB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F0F8FF")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
        table.setStyle(table_style)
        elements.append(table)

        # Build the PDF and add page numbers.
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

        return response


{% extends 'base.html' %}

{% block content %}
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white text-center">
                    <h3><i class="fas fa-user-lock"></i> Login</h3>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}

                        <div class="form-group mb-3">
                            <label><i class="fas fa-user-circle"></i> Username</label>
                            {{ form.username }}
                        </div>

                        <div class="form-group mb-3">
                            <label><i class="fas fa-key"></i> Password</label>
                            {{ form.password }}
                        </div>

                        {% if form.errors %}
                            <div class="alert alert-danger">
                                <ul>
                                    {% for field in form %}
                                        {% for error in field.errors %}
                                            <li>{{ error }}</li>
                                        {% endfor %}
                                    {% endfor %}
                                </ul>
                            </div>
                        {% endif %}

                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}


{% extends 'base.html' %}

{% block content %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-lg">
                <div class="card-header bg-primary text-white text-center">
                    <h3><i class="fas fa-sign-out-alt"></i> Logout</h3>
                </div>
                <div class="card-body">
                    <h4 class="text-center">You have been logged out.</h4>
                    <div class="text-center mt-3">
                        <a href="{% url 'login' %}" class="btn btn-primary">
                            <i class="fas fa-sign-in-alt"></i> Login again
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock %}


{% extends 'base.html' %}

{% block content %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-lg">
                <div class="card-header bg-success text-white text-center">
                    <h3><i class="fas fa-user-plus"></i> Register</h3>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}

                        <div class="form-group mb-3">
                            <label><i class="fas fa-user-circle"></i> Username</label>
                            {{ form.username }}
                        </div>

                        <div class="form-group mb-3">
                            <label><i class="fas fa-envelope"></i> Email</label>
                            {{ form.email }}
                        </div>

                        <div class="form-group mb-3">
                            <label><i class="fas fa-users"></i> Role</label>
                            {{ form.role }}
                        </div>

                        <div class="form-group mb-3">
                            <label><i class="fas fa-phone"></i> Phone</label>
                            {{ form.phone }}
                        </div>

                        <div class="form-group mb-3">
                            <label><i class="fas fa-key"></i> Password</label>
                            {{ form.password1 }}
                        </div>

                        <div class="form-group mb-3">
                            <label><i class="fas fa-key"></i> Confirm Password</label>
                            {{ form.password2 }}
                        </div>

                        {% if form.errors %}
                            <div class="alert alert-danger">
                                <ul>
                                    {% for field in form %}
                                        {% for error in field.errors %}
                                            <li>{{ error }}</li>
                                        {% endfor %}
                                    {% endfor %}
                                </ul>
                            </div>
                        {% endif %}

                        <button type="submit" class="btn btn-success w-100">
                            <i class="fas fa-user-check"></i> Register
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>
{% endblock %}

{% extends "base.html" %}
{% block content %}
  <h2>Pending Role Change Requests</h2>
  <ul>
    {% for request in requests %}
      <li>
        {{ request.user.username }}: requested "{{ request.requested_role }}"
        <a href="{% url 'role-change-request-update' request.pk %}">Review</a>
      </li>
    {% empty %}
      <li>No pending requests.</li>
    {% endfor %}
  </ul>
{% endblock %}


{% extends "base.html" %}
{% block content %}
  <h2>Pending Role Change Requests</h2>
  <ul>
    {% for request in requests %}
      <li>
        {{ request.user.username }}: requested "{{ request.requested_role }}"
        <a href="{% url 'role-change-request-update' request.pk %}">Review</a>
      </li>
    {% empty %}
      <li>No pending requests.</li>
    {% endfor %}
  </ul>
{% endblock %}


{% extends "base.html" %}
{% block content %}
  <h2>Review Role Change Request</h2>
  <p>User: {{ object.user.username }}</p>
  <p>Current Role: {{ object.user.role }}</p>
  <p>Requested Role: {{ object.requested_role }}</p>
  <p>Current Status: {{ object.status }}</p>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-success">Submit</button>
  </form>
{% endblock %}




{% extends 'base.html' %}

{% block content %}
    <div class="bg-white shadow-md rounded my-6 p-6 max-w-lg mx-auto">
        <h2 class="text-2xl font-bold mb-4">{% if object %}Edit Attendance{% else %}Mark Attendance{% endif %}</h2>
        <form method="post">
            {% csrf_token %}
            <div class="space-y-4">
                {{ form.as_p }}
            </div>
            <div class="mt-4">
                <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Save
                </button>
            </div>
        </form>
        <div class="mt-4">
            <a href="{% url 'attendance-list' %}" class="text-blue-500 hover:underline">
                Back to Attendance List
            </a>
        </div>
    </div>
{% endblock %}

{% extends 'base.html' %}

{% block content %}
    <div class="bg-white shadow-md rounded my-6 p-6 max-w-lg mx-auto">
        <h2 class="text-2xl font-bold mb-4">Generate Attendance Report (PDF)</h2>
        <form method="post">
            {% csrf_token %}
            <div class="space-y-4">
                {{ form.as_p }}
            </div>
            <div class="mt-4">
                <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                    Generate PDF
                </button>
            </div>
        </form>
    </div>
{% endblock %}


{% extends 'base.html' %}
{% load static %}
{% block extra_css %}
<style>
    body {
        background-color: #f8f9fa;
    }

    .error-container {
        margin-top: 10%;
    }
</style>
{% endblock %}

{% block content %}
    <div class="container error-container text-center">
        <div class="alert alert-danger d-inline-block p-5" role="alert">
            <i class="fa-solid fa-{{ error_icon }} fa-4x mb-3"></i>
            <h1 class="display-4">{{ error_title }}</h1>
            <p class="lead">{{ error_message }}</p>
            <hr>
            <a href="{% url 'student_list' %}" class="btn btn-primary">
                <i class="fa-solid fa-house"></i> Return Home
            </a>
        </div>
    </div>
{% endblock %}

{% extends 'base.html' %}
{% load static %}
{% block extra_css %}
    <style>
        body {
            background-color: #f8f9fa;
        }

        .error-container {
            margin-top: 10%;
        }
    </style>
{% endblock %}

{% block content %}
    <div class="container error-container text-center">
        <div class="alert alert-warning d-inline-block p-5" role="alert">
            <i class="fa-solid fa-{{ error_icon }} fa-4x mb-3"></i>
            <h1 class="display-4">{{ error_title }}</h1>
            <p class="lead">{{ error_message }}</p>
            <hr>
            <a href="{% url 'home' %}" class="btn btn-primary">
                <i class="fa-solid fa-house"></i> Return Home
            </a>
        </div>
    </div>
{% endblock %}

{% load static %}
{% load custom_filters %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{% block title %}School Management System{% endblock %}</title>

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"/>

    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"/>

    <!-- SweetAlert2 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/sweetalert2@11.0.10/dist/sweetalert2.min.css" rel="stylesheet">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}"/>

    {% block head %}{% endblock %}
    {% block extra_css %}{% endblock %}
</head>

<body>
<!-- Navbar -->
{% include "navbar.html" %}

<!-- messages messages.success(self.request, 'Registration successful! Please log in.')i-->
{#{% if messages %}#}
{#    <div id="messages">#}
{#        {% for message in messages %}#}
{#            <div class="message {{ message.tags }}">#}
{#                {{ message }}#}
{#            </div>#}
{#        {% endfor %}#}
{#    </div>#}
{#{% endif %}#}


<!-- Main Content -->
<div class="container my-4">
    {% block content %}{% endblock %}
</div>

<!-- Footer -->
<footer class="text-center mt-5 py-3 bg-light">
    <p class="mb-0">&copy; {{ year|default:"now"|date:"Y" }} School Management System. All Rights Reserved.</p>
</footer>

<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- SweetAlert2 JS -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.0.10/dist/sweetalert2.all.min.js"></script>

<!-- Custom JS -->
<script src="{% static 'js/main.js' %}"></script>

{% block scripts %}
    <script>
        // Display messages using SweetAlert
        $(document).ready(function () {
            {% if messages %}
                {% for message in messages %}
                    Swal.fire({
                        icon: "{{ message.tags }}",
                        title: "{{ message }}",
                        timer: 3000,
                        showConfirmButton: false,
                    });
                {% endfor %}
            {% endif %}
        });
    </script>
{% endblock %}

{% block extra_js %}
{% endblock %}
</body>
</html>


<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
        <a class="navbar-brand" href="{% url 'student_list' %}">
            <i class="fas fa-school me-2"></i> School Management
        </a>
        <button
                class="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarNav"
                aria-controls="navbarNav"
                aria-expanded="false"
                aria-label="Toggle navigation"
        >
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'student_list' %}"
                    >Students</a
                    >
                </li>
                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'teacher_list' %}"
                    >Teachers</a
                    >
                </li>
                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'class_list' %}"
                    >Classes</a
                    >
                </li>
                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'subject_list' %}"
                    >Subjects</a
                    >
                </li>
                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'timetable_list' %}"
                    >Timetables</a
                    >
                </li>
                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'role-change-request' %}"
                    >Changes Role</a
                    >
                </li>

                {% if request.user.is_authenticated %}
                    {% if request.user.role == "admin" %}
                        <li class="nav-item">
                            <a
                                    class="nav-link"
                                    href="{% url 'timetable_generate' %}"
                            >Generate</a
                            >
                        </li>
                    {% endif %}
                    <li class="nav-item">
                        <a
                                class="nav-link"
                                href="{% url 'logout' %}"
                        >Logout
                        </a
                        >
                    </li>
                {% else %}

                    <li class="nav-item">
                        <a
                                class="nav-link"
                                href="{% url 'login' %}"
                        >Login</a
                        >
                    </li>
                    <li class="nav-item">
                        <a
                                class="nav-link"
                                href="{% url 'register' %}"
                        >Register</a
                        >
                    </li>
                {% endif %}

                <li class="nav-item">
                    <a
                            class="nav-link"
                            href="{% url 'admin:index' %}"
                    >Admin</a
                    >
                </li>
            </ul>
        </div>
    </div>
</nav>

{% extends "base.html" %}

{% block title %}Delete Confirmation{% endblock %}

{% block content %}
    <div class="container mt-5">
        <h1 class="text-danger">Delete Student</h1>
        <p>Are you sure you want to delete <strong>{{ student.user.get_full_name }}</strong>?</p>

        <!-- Deletion Form -->
        <form method="post" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger">
                Yes, Delete
            </button>
        </form>

        <!-- Cancel Button -->
        <a href="{% url 'student_list' %}" class="btn btn-secondary">Cancel</a>
    </div>
{% endblock %}

{% extends "base.html" %}

{% block title %}Student Detail{% endblock %}

{% block content %}
    <div class="container mt-5">
        <h1 class="display-4">{{ student.user.get_full_name }}</h1>

        <!-- Student Info -->
        <div class="row mb-3">
            <div class="col-md-6">
                <p><strong>Email:</strong> {{ student.user.email }}</p>
                <p><strong>Age:</strong> {{ student.age }}</p>
                <p><strong>Phone:</strong> {{ student.phone }}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Address:</strong> {{ student.address }}</p>
                <p><strong>Enrollment Date:</strong> {{ student.enrollment_date }}</p>
            </div>
        </div>

        <!-- Enrolled Classes -->
        <div class="mb-3">
            <p><strong>Enrolled Classes:</strong></p>
            {% if student.class_obj %}
                <p>{{ student.class_obj.name }}</p>
            {% else %}
                <p>No classes enrolled.</p>
            {% endif %}
        </div>

        <!-- Back Button -->
        <a href="{% url 'student_list' %}" class="btn btn-primary mt-3">Back to List</a>
    </div>
{% endblock %}

{% extends "base.html" %}
{% load custom_filters %}

{% block title %}{% if object %}Update{% else %}Create{% endif %} Student {% endblock %}

{% block content %}
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="card shadow-lg">
                    <div class="card-header bg-primary text-white text-center">
                        <h4>{% if object %}Update{% else %}Create{% endif %} Student</h4>
                    </div>
                    <div class="card-body">
                        <form method="post" class="needs-validation" novalidate>
                            {% csrf_token %}

                            <!-- Form Fields with custom classes -->
                            <div class="mb-3">
                                <label for="{{ form.user.id_for_label }}" class="form-label">User:</label>
                                {{ form.user|add_class:"form-select" }}
                            </div>
                            <div class="mb-3">
                                <label for="{{ form.age.id_for_label }}" class="form-label">Age:</label>
                                {{ form.age|add_class:"form-control" }}
                            </div>
                            <div class="mb-3">
                                <label for="{{ form.phone.id_for_label }}" class="form-label">Phone:</label>
                                {{ form.phone|add_class:"form-control" }}
                            </div>
                            <div class="mb-3">
                                <label for="{{ form.address.id_for_label }}" class="form-label">Address:</label>
                                {{ form.address|add_class:"form-control" }}
                            </div>
                            <div class="mb-3">
                                <label for="{{ form.class_obj.id_for_label }}" class="form-label">Class:</label>
                                {{ form.class_obj|add_class:"form-select" }}
                            </div>
                            <div class="mb-3">
                                <label for="{{ form.subjects.id_for_label }}" class="form-label">Subjects:</label>
                                {{ form.subjects|add_class:"form-select" }}
                            </div>

                            <div class="d-flex justify-content-between mt-4">
                                <button type="submit" class="btn btn-success w-48">
                                    {% if object %}Update{% else %}Create{% endif %} Student
                                </button>

                                <a href="{% url 'student_list' %}" class="btn btn-secondary w-48">Cancel</a>
                            </div>
                        </form>

                        <!-- Display messages -->
                        {% if error %}
                            <div class="alert alert-danger text-center" role="alert">{{ error }}</div>
                        {% endif %}
                        {% if message %}
                            <div class="alert alert-success text-center" role="alert">{{ message }}</div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
{% endblock %}

{% block extra_js %}
{% load static %}
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

<script>
$(document).ready(function() {
    $('#class-select').change(function() {
        var class_id = $(this).val();
        $.ajax({
            url: "{% url 'get_class_subjects' %}",  // Make sure this URL is correct
            data: {'class_id': class_id},
            dataType: 'json',
            success: function(response) {
                var subjectsField = $('#id_subjects');
                subjectsField.empty();

                $.each(response.subjects, function(index, subject) {
                    subjectsField.append(
                        '<input type="checkbox" name="subjects" value="' + subject.id + '" checked disabled> ' +
                        subject.name + '<br>'
                    );
                });
            }
        });
    });
});
</script>
{% endblock %}


{% extends "base.html" %}

{% block title %}Teacher List{% endblock %}

{% block content %}
    <div class="container mt-2">
        <h1 class="mb-4 text-center">Students</h1>

        <!-- Add Teacher Button -->
        <a href="{% url 'student_create' %}" class="btn btn-primary mb-3">
            <i class="fas fa-plus-circle me-2"></i> Add Students
        </a>

        <!-- Search Card -->
        <div class="card shadow-sm mb-4">
            <div class="card-body">
                <form method="get" class="row g-3">
                    <div class="col-md-8">
                        <div class="input-group">
                            <span class="input-group-text bg-transparent"><i class="fas fa-search"></i></span>
                            <input type="text" name="name" class="form-control"
                                   placeholder="Search students by name..." value="{{ search_query }}">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <button type="submit" class="btn btn-outline-primary w-100">
                            <i class="fas fa-filter me-2"></i>Filter Results
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Teacher List -->
        <ul class="list-group shadow-lg">
            {% for student in students %}
                <li class="list-group-item d-flex justify-content-between align-items-center hover-shadow">
                    <a href="{% url 'student_detail' student.id %}" class="text-dark text-decoration-none">
                        <strong>{{ student.first_name }} {{ student.last_name }}</strong>
                    </a>
                    <div class="d-flex">
                        <a href="{% url 'student_update' student.id %}" class="btn btn-sm btn-warning me-2">
                            <i class="fas fa-edit"></i> Edit
                        </a>
                        <a href="{% url 'student_delete' student.id %}" class="btn btn-sm btn-danger">
                            <i class="fas fa-trash-alt"></i> Delete
                        </a>
                    </div>
                </li>
            {% endfor %}
        </ul>

        <!-- Pagination -->
        {% if is_paginated %}
            <div class="pagination mt-4 d-flex justify-content-center">
                <nav aria-label="Page navigation">
                    <ul class="pagination pagination-lg">
                        {% if page_obj.has_previous %}
                            <li class="page-item">
                                <a class="page-link" href="?page=1" aria-label="First">
                                    <span aria-hidden="true">&laquo; First</span>
                                </a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="?page={{ page_obj.previous_page_number }}"
                                   aria-label="Previous">
                                    <span aria-hidden="true">&lsaquo; Previous</span>
                                </a>
                            </li>
                        {% else %}
                            <li class="page-item disabled">
                                <span class="page-link">&laquo; First</span>
                            </li>
                            <li class="page-item disabled">
                                <span class="page-link">&lsaquo; Previous</span>
                            </li>
                        {% endif %}

                        <li class="page-item active">
                            <span class="page-link">
                                Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
                            </span>
                        </li>

                        {% if page_obj.has_next %}
                            <li class="page-item">
                                <a class="page-link" href="?page={{ page_obj.next_page_number }}" aria-label="Next">
                                    <span aria-hidden="true">Next &rsaquo;</span>
                                </a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}" aria-label="Last">
                                    <span aria-hidden="true">Last &raquo;</span>
                                </a>
                            </li>
                        {% else %}
                            <li class="page-item disabled">
                                <span class="page-link">Next &rsaquo;</span>
                            </li>
                            <li class="page-item disabled">
                                <span class="page-link">Last &raquo;</span>
                            </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        {% endif %}
    </div>
{% endblock %}




{% extends "base.html" %}

{% block title %}Delete Confirmation{% endblock %}

{% block content %}
    <div class="container mt-5">
        <h1 class="text-danger">Delete Teacher</h1>
        <p>Are you sure you want to delete <strong>{{ teacher.name }}</strong>?</p>

        <!-- Deletion Form -->
        <form method="post" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger">
                <i class="fas fa-trash-alt"></i> Yes, Delete
            </button>
        </form>

        <!-- Cancel Button -->
        <a href="{% url 'teacher_list' %}" class="btn btn-secondary"><i class="fas fa-times"></i> Cancel</a>
    </div>
{% endblock %}

{% extends "base.html" %}

{% block title %}Teacher List{% endblock %}

{% block content %}
    <div class="container mt-2">
        <h1 class="mb-4 text-center">Teachers</h1>

        <!-- Add Teacher Button -->
        <a href="{% url 'teacher_create' %}" class="btn btn-primary mb-3">
            <i class="fas fa-plus-circle me-2"></i> Add Teacher
        </a>

        <!-- Teacher List -->
        <ul class="list-group shadow-lg">
            {% for teacher in teachers %}
                <li class="list-group-item d-flex justify-content-between align-items-center hover-shadow">
                    <a href="{% url 'teacher_detail' teacher.id %}" class="text-dark text-decoration-none">
                        <strong>{{ teacher.first_name }} {{ teacher.last_name }}</strong>
                    </a>
                    <div class="d-flex">
                        <a href="{% url 'teacher_update' teacher.id %}" class="btn btn-sm btn-warning me-2">
                            <i class="fas fa-edit"></i> Edit
                        </a>
                        <a href="{% url 'teacher_delete' teacher.id %}" class="btn btn-sm btn-danger">
                            <i class="fas fa-trash-alt"></i> Delete
                        </a>
                    </div>
                </li>
            {% endfor %}
        </ul>

        <!-- Pagination -->
        {% if is_paginated %}
            <div class="pagination mt-4 d-flex justify-content-center">
                <nav aria-label="Page navigation">
                    <ul class="pagination pagination-lg">
                        {% if page_obj.has_previous %}
                            <li class="page-item">
                                <a class="page-link" href="?page=1" aria-label="First">
                                    <span aria-hidden="true">&laquo; First</span>
                                </a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="?page={{ page_obj.previous_page_number }}" aria-label="Previous">
                                    <span aria-hidden="true">&lsaquo; Previous</span>
                                </a>
                            </li>
                        {% else %}
                            <li class="page-item disabled">
                                <span class="page-link">&laquo; First</span>
                            </li>
                            <li class="page-item disabled">
                                <span class="page-link">&lsaquo; Previous</span>
                            </li>
                        {% endif %}

                        <li class="page-item active">
                            <span class="page-link">
                                Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
                            </span>
                        </li>

                        {% if page_obj.has_next %}
                            <li class="page-item">
                                <a class="page-link" href="?page={{ page_obj.next_page_number }}" aria-label="Next">
                                    <span aria-hidden="true">Next &rsaquo;</span>
                                </a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}" aria-label="Last">
                                    <span aria-hidden="true">Last &raquo;</span>
                                </a>
                            </li>
                        {% else %}
                            <li class="page-item disabled">
                                <span class="page-link">Next &rsaquo;</span>
                            </li>
                            <li class="page-item disabled">
                                <span class="page-link">Last &raquo;</span>
                            </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        {% endif %}
    </div>
{% endblock %}



