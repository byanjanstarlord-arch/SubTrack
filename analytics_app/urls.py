from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('spending/', views.spending, name='spending'),
    path('categories/', views.categories, name='categories'),
]
