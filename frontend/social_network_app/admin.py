from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NLPAnalysisLog, Post

@admin.register(CustomUser)
class CustomUser(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_groups'
    )

    def get_user_groups(self, obj):
        return ", ".join(group.name for group in obj.groups.all())
    get_user_groups.short_description = 'Auth Groups'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'created_at')

@admin.register(NLPAnalysisLog)
class AIAnalysisLog(admin.ModelAdmin):
    list_display = ('id', 'target_type', 'related_object', 'is_toxic', 'run_time')
    list_filter = ('target_type', 'is_toxic', 'run_time')
    search_fields = ('post__content', 'comment__content', 'result')
    readonly_fields = ('target_type', 'post', 'comment', 'is_toxic', 'result', 'run_time')

    def related_object(self, obj):
        if obj.target_type == 'post' and obj.post:
            return f"Post #{obj.post.id}"
        elif obj.target_type == 'commentariu' and obj.comment:
            return f"Comment #{obj.comment.id}"
        return '-'
    related_object.short_description = 'Target'