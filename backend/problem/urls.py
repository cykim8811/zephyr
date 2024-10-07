from django.urls import path
from . import views

urlpatterns = [
    path('problem/', views.get_problem, name='get_problem'),
]