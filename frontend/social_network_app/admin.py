from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = UserAdmin.list_display + ('role',)
