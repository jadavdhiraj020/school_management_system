from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("classes/", include("school_class.urls")),
    path("subjects/", include("subjects.urls")),
    path("timetables/", include("time_tables.urls")),  
]
