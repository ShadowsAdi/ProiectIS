# social_network_app/views.py
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
    friendships_user = Friendships.objects.filter(Q(user1=user) | Q(user2=user), status="accepted")

    #fetch all friends of user in order to show their posts on user's main page
    friend_ids = [f.user1 for f in friendships_user] + [f.user2 for f in friendships_user]

    #if we put the id of user in friend_ids, we remove it:
    friend_ids = [friend_id for friend_id in friend_ids if friend_id != user]

    #show posts of all user's friends

    # posts = Post.objects.filter(user__in=friend_ids).order_by('-created_at')

    posts = Post.objects.all()

    if request.method == 'POST':
        form = PostForm(request.POST)
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

@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('register')

    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'app_pages/profile.html', {'profile': profile})

def notifications(request):
    if not request.user.is_authenticated:
        return redirect('register')

    return render(request, 'app_pages/notifications.html')

def settings(request):
    if not request.user.is_authenticated:
        return redirect('register')

    return render(request, 'app_pages/settings.html')

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