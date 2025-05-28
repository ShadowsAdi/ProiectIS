from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
import json

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    karma_score = models.IntegerField(default=100, null=True)
    banned_at = models.DateTimeField(blank=True, null=True)
    banned_reason = models.CharField(max_length=255, blank=True, null=True)
    banned_by = models.IntegerField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

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

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=45)
    title = models.CharField(max_length=60)
    content = models.TextField()
    files = models.FileField(upload_to='post_files/', null=True, blank=True)
    images = models.ImageField(upload_to='post_images/', null=True, blank=True)
    post_score = models.FloatField(editable=False, default=0)
    views = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from .ai_moderation_service import moderate_post
        is_toxic = moderate_post(self.id, None, 'post')

        if not is_toxic and not self.is_published:
            self.is_published = True
            self.post_score = 1.0
            super().save(update_fields=['is_published', 'post_score'])

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    comment_score = models.FloatField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from .ai_moderation_service import moderate_post
        is_toxic = moderate_post(self.post, self.id, 'comment')

        if not is_toxic and not self.is_published:
            self.is_published = True
            self.comment_score = 1.0
            super().save(update_fields=['is_published', 'comment_score'])

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"

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
        ('comment', 'Comment'),
    ]

    id = models.AutoField(primary_key=True)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE)
    is_toxic = models.BooleanField(default=False)
    result = models.TextField()
    run_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NLP Analysis ({self.target_type}) at {self.run_time}"

class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')

    # Profile & Privacy
    private_account = models.BooleanField(default=False)
    friend_request_permission = models.CharField(
        max_length=20,
        choices=[
            ('everyone', 'Everyone'),
            ('friends_of_friends', 'Friends of Friends'),
            ('no_one', 'No one'),
        ],
        default='everyone'
    )

    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Appearance
    theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='light'
    )

    def __str__(self):
        return f"Settings for {self.user.username}"

class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('friend_request', 'Friend Request'),
        ('friend_post', 'Friend Post'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')  # who receives the notification
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)  # who triggered it
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)  # linked post for friend_post type
    friend_request = models.ForeignKey(Friendships, null=True, blank=True, on_delete=models.CASCADE)  # linked friend request
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification {self.notif_type} to {self.user.username} from {self.sender.username if self.sender else 'System'}"
