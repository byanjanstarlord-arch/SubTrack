"""Signals for accounts app."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserSettings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """Create default UserSettings when a new user is created."""
    if created:
        UserSettings.objects.create(
            user=instance,
            currency=instance.currency,
        )


@receiver(post_save, sender=User)
def save_user_settings(sender, instance, **kwargs):
    """Ensure user settings are saved when user is saved."""
    if hasattr(instance, 'settings'):
        instance.settings.save()
