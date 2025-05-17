from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.custom_login, name="login"),
    path('', views.home, name="home"),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
]