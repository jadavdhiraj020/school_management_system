# time_tables/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Timetable URLs
    path('', views.TimetableListView.as_view(), name='timetable_list'),
    path('add/', views.TimetableCreateView.as_view(), name='timetable_create'),
    path('<int:pk>/', views.TimetableDetailView.as_view(), name='timetable_detail'),
    path('<int:pk>/edit/', views.TimetableUpdateView.as_view(), name='timetable_update'),
    path('<int:pk>/delete/', views.TimetableDeleteView.as_view(), name='timetable_delete'),
    
    # TimeSlot URLs (if needed)
    path('timeslots/', views.TimeSlotListView.as_view(), name='timeslot_list'),
    path('timeslots/add/', views.TimeSlotCreateView.as_view(), name='timeslot_create'),
    path('timeslots/<int:pk>/', views.TimeSlotDetailView.as_view(), name='timeslot_detail'),
    path('timeslots/<int:pk>/edit/', views.TimeSlotUpdateView.as_view(), name='timeslot_update'),
    path('timeslots/<int:pk>/delete/', views.TimeSlotDeleteView.as_view(), name='timeslot_delete'),
]
