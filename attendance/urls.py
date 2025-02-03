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
