"""
URL configuration for teacher app
"""
from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
]

