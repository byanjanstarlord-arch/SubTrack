from django.urls import path
from . import views

app_name = 'gmail_detection'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('connect/', views.connect_gmail, name='connect'),
    path('disconnect/', views.disconnect_gmail, name='disconnect'),
    path('scan/', views.scan_emails, name='scan'),
    path('detection/<int:pk>/confirm/', views.confirm_detection, name='confirm'),
    path('detection/<int:pk>/reject/', views.reject_detection, name='reject'),
    path('api/scan-status/', views.api_scan_status, name='api_scan_status'),
]
