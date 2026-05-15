from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model for SubTrack."""
    
    CURRENCY_CHOICES = [
        ('USD', '$ - US Dollar'),
        ('EUR', '€ - Euro'),
        ('GBP', '£ - British Pound'),
        ('INR', '₹ - Indian Rupee'),
        ('JPY', '¥ - Japanese Yen'),
        ('CAD', 'C$ - Canadian Dollar'),
        ('AUD', 'A$ - Australian Dollar'),
    ]
    
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    gmail_connected = models.BooleanField(default=False)
    gmail_access_token = models.TextField(blank=True, null=True)
    gmail_refresh_token = models.TextField(blank=True, null=True)
    gmail_token_expiry = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserSettings(models.Model):
    """User preferences and settings."""
    
    THEME_CHOICES = [
        ('light', 'Light'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    email_notifications = models.BooleanField(default=True)
    renewal_alert_days = models.PositiveIntegerField(default=3)
    currency = models.CharField(max_length=3, choices=User.CURRENCY_CHOICES, default='USD')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_usersettings'
    
    def __str__(self):
        return f"{self.user.email} settings"
