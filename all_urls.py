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


# accounts/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    # Class-based registration view
    path('register/', RegisterView.as_view(), name='register'),
    # Class-based login view (customized)
    path('login/', LoginView.as_view(), name='login'),
    # Class-based logout view (customized)
    path('logout/', LogoutView.as_view(), name='logout'),
]

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', lambda request: redirect('students/', permanent=True)),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('accounts.urls')),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("classes/", include("school_class.urls")),
    path("subjects/", include("subjects.urls")),
    path("timetables/", include("time_tables.urls")),
]

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

from django.urls import path
from subjects import views


urlpatterns = [
    path("", views.SubjectListView.as_view(), name="subject_list"),
    path("<int:pk>/", views.SubjectDetailView.as_view(), name="subject_detail"),
    path("create/", views.SubjectCreateView.as_view(), name="subject_create"),
    path("<int:pk>/update/", views.SubjectUpdateView.as_view(), name="subject_update"),
    path("<int:pk>/delete/", views.SubjectDeleteView.as_view(), name="subject_delete"),
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

from django.urls import path
from .views import (
    StudentListView,
    StudentDetailView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
)

urlpatterns = [
    path("", StudentListView.as_view(), name="student_list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="student_detail"),
    path("create/", StudentCreateView.as_view(), name="student_create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student_update"),
    path("<int:pk>/delete/", StudentDeleteView.as_view(), name="student_delete"),
]

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
