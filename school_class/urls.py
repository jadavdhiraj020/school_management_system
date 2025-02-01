from django.urls import path
from . import views

urlpatterns = [
    path("", views.ClassListView.as_view(), name="class_list"),
    path("create/", views.ClassCreateView.as_view(), name="class_create"),
    path("<int:pk>/", views.ClassDetailView.as_view(), name="class_detail"),
    path("<int:pk>/update/", views.ClassUpdateView.as_view(), name="class_update"),
    path("<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),
]
