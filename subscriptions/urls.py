from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.subscription_list, name='list'),
    path('create/', views.subscription_create, name='create'),
    path('<int:pk>/', views.subscription_detail, name='detail'),
    path('<int:pk>/edit/', views.subscription_edit, name='edit'),
    path('<int:pk>/delete/', views.subscription_delete, name='delete'),
    path('<int:pk>/toggle/', views.subscription_toggle_status, name='toggle'),
    path('<int:pk>/cancel/', views.subscription_cancel, name='cancel'),
    path('renewals/', views.upcoming_renewals, name='renewals'),
    path('trials/', views.trials, name='trials'),
    path('export/csv/', views.export_csv, name='export_csv'),
]
