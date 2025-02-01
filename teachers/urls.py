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
