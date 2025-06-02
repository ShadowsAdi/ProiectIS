# social_network_app/views.py
from datetime import timedelta
from urllib import request
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from ibm_platform_services.user_management_v1 import UserSettings
from .forms import RegisterForm, PostForm, ProfileForm, SettingsForm
from django.contrib import messages
from .models import Post, Friendships, Profile, CustomUser, UserSettings
from django.db.models import Q
from .forms import RegisterForm, PostForm
from .models import CustomUser, Post, Friendships, Profile
from .tokens import email_verification_token
from .utils import get_client_ip
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.conf import settings as st

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    current_site = get_current_site(request)

    verification_link = f"{st.SITE_PROTOCOL}://{st.SITE_DOMAIN}{reverse('verify_email', kwargs={'uidb64': uid, 'token': token})}"


    subject = 'Confirm your email address'
    html_message = render_to_string('emails/verify_email.html', {
        'user': user,
        'verification_link': verification_link,
    })

    email = EmailMultiAlternatives(subject, "", to=[user.email])
    email.attach_alternative(html_message, "text/html")
    email.send()

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.email_verified_at = timezone.now()
        user.save()
        return HttpResponse("✅ Email verified successfully. You may now log in.")
    else:
        return HttpResponse("❌ Invalid or expired verification link.")

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        print("POST REQUEST RECEIVED")
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("form is valid")
            user = form.save()
            ip = get_client_ip(request)
            form.save(ip_address=ip)
            send_verification_email(request, user)
            messages.success(request, 'Account created! Please check your email to verify your address.')
            return redirect('login')
        else:
            print("Form errors:", form.errors)
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})

def custom_login(request):
    show_resend_link = False
    if request.user.is_authenticated:
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            profile = Profile.objects.filter(user=user).first()
            if profile and user.email_verified_at is None:
                show_resend_link = True
                messages.error(request, "Please verify your email address before logging in.")
            else:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'authentication/login.html', {
        'form': form,
        'show_resend_link': show_resend_link,
    })

def home(request):

    if not request.user.is_authenticated:
        return redirect('register')

    user = request.user

    try:
        user_settings = user.settings
    except UserSettings.DoesNotExist:
        user_settings = UserSettings.objects.create(user=user)

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
        'theme': user_settings.theme,
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

    user_settings = getattr(to_user, 'settings', None)
    if not user_settings:
        # If no settings found, treat as 'everyone'
        permission = 'everyone'
    else:
        permission = user_settings.friend_request_permission

    if permission == 'no_one':
        # No one can send request
        # You can add a message here if you want
        return redirect('user_profile', username=username)

    if permission == 'friends_of_friends':
        # Check if request.user is friend of friend of to_user

        # Get to_user's friends (accepted)
        friends_of_to_user = Friendships.objects.filter(
            (Q(user1=to_user) | Q(user2=to_user)) & Q(status='accepted')
        )

        # Extract friend user IDs
        to_user_friend_ids = set()
        for f in friends_of_to_user:
            if f.user1 == to_user:
                to_user_friend_ids.add(f.user2.id)
            else:
                to_user_friend_ids.add(f.user1.id)

        # Get request.user's friends (accepted)
        friends_of_request_user = Friendships.objects.filter(
            (Q(user1=request.user) | Q(user2=request.user)) & Q(status='accepted')
        )

        request_user_friend_ids = set()
        for f in friends_of_request_user:
            if f.user1 == request.user:
                request_user_friend_ids.add(f.user2.id)
            else:
                request_user_friend_ids.add(f.user1.id)

        # Now check if any friend of request.user is also friend of to_user
        # That means request.user and to_user share at least one friend
        common_friends = to_user_friend_ids.intersection(request_user_friend_ids)

        if not common_friends:
            # Not a friend of friend, so reject request
            return redirect('user_profile', username=username)

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


@login_required
def notifications(request):
    user = request.user
    # Pending friend requests
    pending_requests = Friendships.objects.filter(user2=user, status='pending')

    # Get accepted friendships for the current user
    friendships = Friendships.objects.filter(
        (Q(user1=user) | Q(user2=user)),
        status='accepted'
    )

    friend_ids = set()
    for friendship in friendships:
        if friendship.user1 == user:
            friend_ids.add(friendship.user2.id)
        else:
            friend_ids.add(friendship.user1.id)

    # Optional: Filter recent posts, e.g., last 7 days
    recent_days = 7
    recent_date = now() - timedelta(days=recent_days)

    friend_posts = Post.objects.filter(
        user__id__in=friend_ids,
        is_published=True,
        created_at__gte=recent_date
    ).order_by('-created_at')

    return render(request, 'app_pages/notifications.html', {
        'pending_requests': pending_requests,
        'friend_posts': friend_posts,
    })

@login_required
def settings(request):
    user = request.user
    user_settings, _ = UserSettings.objects.get_or_create(user=user)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        settings_form = UserSettingsForm(request.POST, instance=user_settings)

        if profile_form.is_valid() and settings_form.is_valid():
            profile_form.save()
            settings_form.save()

            messages.success(request, "Settings updated successfully!")
            return redirect('settings')
    else:
        profile_form = ProfileForm(instance=profile)
        settings_form = UserSettingsForm(instance=user_settings)


    return render(request, 'app_pages/settings.html', {
        'profile_form': profile_form,
        'settings_form': settings_form,
        'theme': user_settings.theme,
    })
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'app_pages/settings.html', context)
  
def resend_verification_email(request):
    username = request.GET.get('username')
    try:
        user = CustomUser.objects.get(username=username)
        if user.email_verified_at:
            messages.info(request, "Your email is already verified.")
            return redirect('login')

        # You would call your actual email sending logic here:
        send_verification_email(request, user)

        messages.success(request, "Verification email has been resent.")
        return redirect('login')

    except ObjectDoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')
