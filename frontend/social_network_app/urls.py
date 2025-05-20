from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', views.custom_login, name="login"),
    path('', views.home, name="home"),
    path('search-users/', views.search_users, name='search_users'),
    path('profile/<str:username>/', views.profile, name='user_profile'),
    path('profile/', views.profile, name='my_profile'),
    path('accept-friend-request/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<str:username>/', views.decline_friend_request, name='decline_friend_request'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
]