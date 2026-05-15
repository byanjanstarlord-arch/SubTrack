from django.contrib import admin
from .models import GmailDetection, ScanSession


@admin.register(GmailDetection)
class GmailDetectionAdmin(admin.ModelAdmin):
    list_display = ('detected_service', 'user', 'detected_amount', 'confidence_score', 'status', 'created_at')
    list_filter = ('status', 'detection_method', 'created_at')
    search_fields = ('detected_service', 'email_subject', 'user__email')


@admin.register(ScanSession)
class ScanSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'emails_scanned', 'subscriptions_found', 'started_at')
    list_filter = ('status', 'started_at')
