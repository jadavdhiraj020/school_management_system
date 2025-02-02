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
