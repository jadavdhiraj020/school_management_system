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
