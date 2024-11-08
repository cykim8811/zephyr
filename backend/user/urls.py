from django.urls import path
from django.urls import include
from . import views

from allauth.account.views import SignupView, LoginView

urlpatterns = [
    path('solution/', views.create_or_update_solution, name='create_or_update_solution'),
    path('solution/get/', views.get_user_solution, name='get_solution'),
    path('info/', views.user_info, name='user_info'),
    path('login2/', views.minimal_login, name='minimal_login'),
    path('', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
]
