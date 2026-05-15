from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserSettings


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'currency', 'gmail_connected', 'is_verified', 'created_at')
    list_filter = ('currency', 'gmail_connected', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_image', 'currency', 'timezone')}),
        ('Gmail Integration', {'fields': ('gmail_connected', 'gmail_access_token', 'gmail_refresh_token', 'gmail_token_expiry')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'renewal_alert_days', 'currency')
    list_filter = ('email_notifications', 'currency')
    search_fields = ('user__email',)
