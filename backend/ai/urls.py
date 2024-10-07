from django.urls import path
from . import views

urlpatterns = [
    # Define your URL patterns here
    path('ai/', views.request_ai, name='request_ai'),
]