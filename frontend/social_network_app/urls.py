from django.urls import path

from . import views

urlpatterns = [
    path('social_network_app/', views.register, name="social_network_app"),
]