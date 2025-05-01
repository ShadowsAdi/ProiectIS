# from django.db import models
# from django.contrib.auth.models import User
#
# class Post(models.Model):
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     ip_address = models.CharField(max_length=45)
#     title = models.CharField(max_length=60)
#     content = models.TextField()
#     post_score = models.FloatField()
#     views = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)
#
#     def __str__(self):
#         return self.title
#
# class Friendships(models.Model):
#     user1 = models.ForeignKey(User, on_delete=models.CASCADE)
#     user2 = models.ForeignKey(User, on_delete=models.CASCADE)
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('accepted', 'Accepted'),
#         ('blocked', 'Blocked'),
#         ('none', 'None'),
#     ]
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='none')
#     created_at = models.DateTimeField(auto_now_add=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)