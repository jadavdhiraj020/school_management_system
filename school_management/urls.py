from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', lambda request: redirect('students/', permanent=True)),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("classes/", include("school_class.urls")),
    path("subjects/", include("subjects.urls")),
    path("timetables/", include("time_tables.urls")),
]
