from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('solution/', views.create_or_update_solution, name='create_or_update_solution'),
    path('solution/get/', views.get_user_solution, name='get_solution'),
    path('', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
]
