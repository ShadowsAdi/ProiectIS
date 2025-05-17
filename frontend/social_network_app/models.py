from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class Role(models.Model):
    name = models.CharField(max_length=20, unique=True)  # 'admin', 'moderator', 'membru'

    def __str__(self):
        return self.name

# Custom user model (extinde AbstractUser)
class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    karma_score = models.IntegerField(default=100, null=True)
    role = models.ForeignKey('Role', null=True, blank=True, on_delete=models.SET_NULL)
    banned_at = models.DateTimeField(blank=True, null=True)
    banned_reason = models.CharField(max_length=255, blank=True, null=True)
    banned_by = models.IntegerField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    # Fix for reverse accessor clash on groups and user_permissions:
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_query_name='customuser',
    )

    def __str__(self):
        return self.username

# Profilul utilizatorului
class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_say', 'Prefer not to say'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='images/avatar', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Postările
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)
    title = models.CharField(max_length=60)
    content = models.TextField()
    post_score = models.FloatField(editable=False, default=0)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    comment_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

# Relațiile de prietenie
class Friendships(models.Model):
    id = models.AutoField(primary_key=True)
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
        ('none', 'None'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user1} - {self.user2} ({self.status})"

class NLPAnalysisLog(models.Model):
    TARGET_TYPE_CHOICES = [
        ('post', 'Post'),
        ('commentariu', 'Commentariu'),
    ]

    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE)
    result = models.TextField()
    run_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NLP Analysis ({self.target_type}) at {self.run_time}"