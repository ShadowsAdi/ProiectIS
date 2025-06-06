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
    path('send_friend_request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<str:username>/', views.decline_friend_request, name='decline_friend_request'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('notifications/', views.notifications, name='notifications'),
    path('settings/', views.settings, name='settings'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
]