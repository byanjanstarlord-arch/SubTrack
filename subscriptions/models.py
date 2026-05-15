from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """Subscription category model."""
    
    ICON_CHOICES = [
        ('tv', 'TV/Entertainment'),
        ('zap', 'Productivity'),
        ('book-open', 'Education'),
        ('dumbbell', 'Fitness'),
        ('cloud', 'Cloud Services'),
        ('credit-card', 'Finance'),
        ('music', 'Music'),
        ('gamepad-2', 'Gaming'),
        ('newspaper', 'News'),
        ('shopping-bag', 'Shopping'),
        ('heart-pulse', 'Health'),
        ('plane', 'Travel'),
    ]
    
    COLOR_CHOICES = [
        ('#EF4444', 'Red'),
        ('#F97316', 'Orange'),
        ('#EAB308', 'Yellow'),
        ('#22C55E', 'Green'),
        ('#06B6D4', 'Cyan'),
        ('#3B82F6', 'Blue'),
        ('#6366F1', 'Indigo'),
        ('#8B5CF6', 'Purple'),
        ('#EC4899', 'Pink'),
        ('#14B8A6', 'Teal'),
        ('#F43F5E', 'Rose'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='tv')
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#3B82F6')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscriptions_category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Subscription model for tracking recurring payments."""
    
    BILLING_CYCLES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half-Yearly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('trial', 'Trial'),
        ('expired', 'Expired'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', '$ - US Dollar'),
        ('EUR', '€ - Euro'),
        ('GBP', '£ - British Pound'),
        ('INR', '₹ - Indian Rupee'),
        ('JPY', '¥ - Japanese Yen'),
        ('CAD', 'C$ - Canadian Dollar'),
        ('AUD', 'A$ - Australian Dollar'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscriptions')
    
    # Core fields
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='subscription_logos/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Dates
    renewal_date = models.DateField()
    trial_end_date = models.DateField(blank=True, null=True)
    started_date = models.DateField(default=timezone.now)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='credit_card')
    
    # Additional
    website_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_auto_detected = models.BooleanField(default=False)
    gmail_detection = models.ForeignKey('gmail_detection.GmailDetection', on_delete=models.SET_NULL, null=True, blank=True, related_name='subscriptions')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions_subscription'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    @property
    def monthly_cost(self):
        """Convert price to monthly equivalent."""
        multipliers = {
            'weekly': 4.33,
            'monthly': 1,
            'quarterly': 0.33,
            'half_yearly': 0.167,
            'yearly': 0.083,
            'lifetime': 0,
        }
        return float(self.price) * multipliers.get(self.billing_cycle, 1)
    
    @property
    def yearly_cost(self):
        """Calculate yearly cost."""
        return self.monthly_cost * 12
    
    @property
    def days_until_renewal(self):
        """Days until next renewal."""
        today = timezone.now().date()
        delta = self.renewal_date - today
        return delta.days
    
    @property
    def is_trial_active(self):
        """Check if trial is still active."""
        if self.trial_end_date and self.status == 'trial':
            return timezone.now().date() <= self.trial_end_date
        return False
    
    @property
    def currency_symbol(self):
        """Get currency symbol."""
        symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹',
            'JPY': '¥', 'CAD': 'C$', 'AUD': 'A$',
        }
        return symbols.get(self.currency, '$')


class SubscriptionHistory(models.Model):
    """Track subscription changes over time."""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50)  # created, updated, paused, cancelled, renewed
    details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscriptions_subscriptionhistory'
        ordering = ['-created_at']
