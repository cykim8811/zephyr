from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    # allauth
    path('', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
]