"""Celery tasks for notification system."""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from subscriptions.models import Subscription
from .models import Notification
from .views import create_notification


@shared_task
def check_upcoming_renewals():
    """Check for upcoming subscription renewals and send notifications."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    today = timezone.now().date()
    
    for user in User.objects.filter(is_active=True):
        # Get user's alert preference
        alert_days = 3
        if hasattr(user, 'settings'):
            alert_days = user.settings.renewal_alert_days
        
        alert_date = today + timedelta(days=alert_days)
        
        # Find subscriptions renewing within alert period
        upcoming = Subscription.objects.filter(
            user=user,
            status='active',
            renewal_date__lte=alert_date,
            renewal_date__gte=today,
        )
        
        for sub in upcoming:
            days_left = (sub.renewal_date - today).days
            
            # Check if notification already exists for this subscription and date
            exists = Notification.objects.filter(
                user=user,
                subscription=sub,
                type='renewal_reminder',
                created_at__date=today,
            ).exists()
            
            if not exists:
                if days_left == 0:
                    title = f"{sub.name} renews today"
                    message = f"Your {sub.name} subscription (${sub.price}) renews today."
                elif days_left == 1:
                    title = f"{sub.name} renews tomorrow"
                    message = f"Your {sub.name} subscription (${sub.price}) renews tomorrow."
                else:
                    title = f"{sub.name} renews in {days_left} days"
                    message = f"Your {sub.name} subscription (${sub.price}) renews on {sub.renewal_date}."
                
                create_notification(
                    user=user,
                    type='renewal_reminder',
                    title=title,
                    message=message,
                    subscription=sub,
                )
    
    return f"Checked renewals for {User.objects.filter(is_active=True).count()} users"


@shared_task
def check_expiring_trials():
    """Check for trials expiring soon and send notifications."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    today = timezone.now().date()
    alert_date = today + timedelta(days=2)
    
    for user in User.objects.filter(is_active=True):
        expiring_trials = Subscription.objects.filter(
            user=user,
            status='trial',
            trial_end_date__lte=alert_date,
            trial_end_date__gte=today,
        )
        
        for trial in expiring_trials:
            days_left = (trial.trial_end_date - today).days
            
            exists = Notification.objects.filter(
                user=user,
                subscription=trial,
                type='trial_expiring',
                created_at__date=today,
            ).exists()
            
            if not exists:
                if days_left == 0:
                    title = f"{trial.name} trial ends today"
                    message = f"Your {trial.name} free trial ends today. You'll be charged ${trial.price} if you don't cancel."
                else:
                    title = f"{trial.name} trial ends in {days_left} days"
                    message = f"Your {trial.name} free trial ends on {trial.trial_end_date}. You'll be charged ${trial.price} if you don't cancel."
                
                create_notification(
                    user=user,
                    type='trial_expiring',
                    title=title,
                    message=message,
                    subscription=trial,
                )
    
    return "Trial check complete"


@shared_task
def send_daily_digest():
    """Send daily digest email to users (placeholder)."""
    # This would send an email summary of upcoming renewals
    # Implementation depends on email backend configuration
    return "Daily digest sent"
