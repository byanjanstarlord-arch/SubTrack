from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """In-app notification model."""
    
    TYPE_CHOICES = [
        ('renewal_reminder', 'Renewal Reminder'),
        ('trial_expiring', 'Trial Expiring'),
        ('payment_detected', 'Payment Detected'),
        ('scan_complete', 'Scan Complete'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Scheduling
    scheduled_time = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type}: {self.title} ({self.user.email})"
    
    @property
    def time_ago(self):
        """Human-readable time ago."""
        from django.utils import timezone
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.created_at)
