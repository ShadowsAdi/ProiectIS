# social_network_app/views.py
from urllib import request

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, PostForm
from django.contrib import messages
from .models import Post, Friendships, Profile, CustomUser
from django.db.models import Q

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

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
    if request.user.is_authenticated:
        return redirect('home')

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
    if not request.user.is_authenticated:
        return redirect('register')

    user = request.user
    friendships_user = Friendships.objects.filter(Q(user1=user) | Q(user2=user), status="accepted")

    #fetch all friends of user in order to show their posts on user's main page
    friend_ids = [f.user1 for f in friendships_user] + [f.user1 for f in friendships_user]

    #if we put the id of user in friend_ids, we remove it:
    friend_ids = [friend_id for friend_id in friend_ids if friend_id != user.id]

    #show posts of all user's friends
    # posts = Post.objects.filter(user__in=friend_ids).order_by('-created_at')

    posts = Post.objects.filter(is_published=True)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = user
            post.save()
            return redirect('home')  # Redirect to home page after saving
    else:
        form = PostForm()
    context = {
        'user': request.user.username,
        'posts': posts,
        'form': form,
    }
    return render(request, 'app_pages/home.html', context)

def search_users(request):
    query = request.GET.get('q', '')
    print(query)
    results = []

    if query:
        users = CustomUser.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )[:10]  # Limit to 10 results
        results = [
            {'username': user.username, 'email': user.email}
            for user in users
        ]
    return JsonResponse({'results': results})

@login_required
def profile(request, username=None):
    if username is None:
        # Show logged-in user's profile
        viewed_user = request.user
    else:
        # Show other user's profile
        viewed_user = get_object_or_404(CustomUser, username=username)

    profile = Profile.objects.filter(user=viewed_user).first()

    return render(request, 'app_pages/profile.html', {
        'user': viewed_user,
        'profile': profile
    })

def notifications(request):
    if not request.user.is_authenticated:
        return redirect('register')

    return render(request, 'app_pages/notifications.html')

def settings(request):
    if not request.user.is_authenticated:
        return redirect('register')

    return render(request, 'app_pages/settings.html')