from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class GmailDetection(models.Model):
    """Detected subscription from Gmail scanning."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('duplicate', 'Duplicate'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gmail_detections')
    
    # Email info
    email_sender = models.CharField(max_length=255)
    email_subject = models.CharField(max_length=500)
    email_date = models.DateTimeField()
    email_message_id = models.CharField(max_length=255, unique=True)
    raw_email_snippet = models.TextField()
    
    # Detected data
    detected_service = models.CharField(max_length=100)
    detected_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    detected_currency = models.CharField(max_length=3, default='USD')
    detected_billing_cycle = models.CharField(max_length=20, blank=True)
    detected_date = models.DateField(null=True, blank=True)
    
    # Confidence
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    detection_method = models.CharField(max_length=20, default='regex')  # regex, nlp, manual
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # If confirmed, link to subscription
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gmail_detections'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gmail_detection_gmaildetection'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.detected_service} ({self.user.email})"


class ScanSession(models.Model):
    """Track Gmail scan sessions."""
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    emails_scanned = models.PositiveIntegerField(default=0)
    subscriptions_found = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'gmail_detection_scansession'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Scan #{self.id} - {self.user.email}"
