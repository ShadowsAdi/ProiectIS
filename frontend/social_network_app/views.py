# social_network_app/views.py
from urllib import request

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})


def custom_login(request):
   if request.method == 'POST':
       form = AuthenticationForm(request,data=request.POST)
       if form.is_valid():
           user = form.get_user()
           login(request, user)
           messages.success(request, f"Welcome back, {user.username}!")
           return redirect('home')  # Redirect after successful login
       else:
           messages.error(request, "Invalid username or password.")
   else:
        form = AuthenticationForm()
   return render(request, 'authentication/login.html', {'form': form})


def home(request):
    context = {
        'username': request.user.username,  # Display the logged-in user's username
        # Add more context here as needed (e.g., posts, notifications, etc.)
    }
    return render(request, 'app_pages/home.html', context)

@login_required
def profile(request):
    # Add any context you need for the profile page
    return render(request, 'app_pages/profile.html')

def messages(request):
    return render(request, 'app_pages/messages.html')

def notifications(request):
    return render(request, 'app_pages/notifications.html')

def settings(request):
    return render(request, 'app_pages/settings.html')