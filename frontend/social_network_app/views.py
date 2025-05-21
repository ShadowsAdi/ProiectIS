# social_network_app/views.py
from urllib import request
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, PostForm, SettingsForm, ProfileForm
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
    friendships_user = Friendships.objects.filter(
        Q(user1=user) | Q(user2=user),
        status="accepted"
    )

    # Get all friend user IDs (excluding the user themself)
    friend_ids = set()
    for friendship in friendships_user:
        if friendship.user1 == user:
            friend_ids.add(friendship.user2.id)
        else:
            friend_ids.add(friendship.user1.id)

    my_posts = Post.objects.filter(user=user, is_published=True)
    friend_posts = Post.objects.filter(user__id__in=friend_ids, is_published=True)
    others_posts = Post.objects.exclude(
        Q(user=user) | Q(user__id__in=friend_ids)
    ).filter(is_published=True)

    all_posts = list(my_posts) + list(friend_posts) + list(others_posts)
    all_posts.sort(key=lambda x: x.created_at, reverse=True)
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
        'posts': all_posts,
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

@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(CustomUser, username=username)
    if request.user == to_user:
        return redirect('home')
    existing = Friendships.objects.filter(
        (Q(user1=request.user) & Q(user2=to_user)) |
        (Q(user1=to_user) & Q(user2=request.user))
    ).first()

    if existing:
        # Optional: Update status if previously deleted
        if existing.status == 'none' and existing.deleted_at is not None:
            existing.status = 'pending'
            existing.deleted_at = None
            existing.save()
        return redirect('user_profile', username=username)

        # Create a new pending friendship
    Friendships.objects.create(user1=request.user, user2=to_user, status='pending')
    return redirect('user_profile', username=username)

@require_POST
@login_required
def accept_friend_request(request, username):
    from_user = get_object_or_404(CustomUser, username=username)
    friendship = Friendships.objects.filter(user1=from_user, user2=request.user, status='pending').first()
    if friendship:
        friendship.status = 'accepted'
        friendship.save()
        messages.success(request, f"You are now friends with {from_user.username}.")
    return redirect('notifications')


@require_POST
@login_required
def decline_friend_request(request, username):
    from_user = get_object_or_404(CustomUser, username=username)
    friendship = Friendships.objects.filter(user1=from_user, user2=request.user, status='pending').first()
    if friendship:
        friendship.delete()
        messages.info(request, f"You declined the friend request from {from_user.username}.")
    return redirect('notifications')


def notifications(request):
    if not request.user.is_authenticated:
        return redirect('register')
    pending_requests = Friendships.objects.filter(user2=request.user, status='pending')
    return render(request, 'app_pages/notifications.html', {'pending_requests': pending_requests})

@login_required
def settings(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = SettingsForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('settings')  # redirect to settings after saving
    else:
        user_form = SettingsForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'app_pages/settings.html', context)