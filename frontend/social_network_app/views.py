# social_network_app/views.py
from urllib import request

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
# from .models import Post,Friendships
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        print("POST REQUEST RECEIVED")
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("form is valid")
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('/auth/login/')  # Redirect to login page after successful registration
        else:
            print("Form errors:",form.errors)
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
    user = request.user
    # friendships_user = Friendships.objects.filter(Q(user1=user) | Q(user2=user), status="accepted")
    #
    # #fetch all friends of user in order to show their posts on user's main page
    # friend_ids = [f.user1 for f in friendships_user] + [f.user1 for f in friendships_user]
    #
    # #if we put the id of user in friend_ids, we remove it:
    # friend_ids = [friend_id for friend_id in friend_ids if friend_id != user.id]
    #
    # #show posts of all user's friends
    # posts = Post.objects.filter(user__in=friend_ids).order_by('-created_at')
    #
    context = {
        'user': request.user.username,
        # 'posts': posts,
    }
    # if request.method == 'POST':
    #     form = PostForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         post = form.save(commit=False)
    #         post.user = user
    #         post.save()
    #         return redirect('home')  # Redirect to home page after saving
    # else:
    #     form = PostForm()
    # context['form'] = form
    return render(request, 'app_pages/home.html', context)

@login_required
def profile(request):
    # Add any context you need for the profile page
    return render(request, 'app_pages/profile.html')

def notifications(request):
    return render(request, 'app_pages/notifications.html')

def settings(request):
    return render(request, 'app_pages/settings.html')