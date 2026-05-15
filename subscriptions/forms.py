from django import forms
from .models import Subscription, Category


class SubscriptionForm(forms.ModelForm):
    """Form for creating and editing subscriptions."""
    
    class Meta:
        model = Subscription
        fields = [
            'name', 'logo', 'description', 'category', 'price', 'currency',
            'billing_cycle', 'renewal_date', 'trial_end_date', 'status',
            'payment_method', 'website_url', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
                'placeholder': 'e.g., Netflix, Spotify...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all resize-none',
                'placeholder': 'Brief description...',
                'rows': 3,
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'currency': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
            }),
            'billing_cycle': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
            }),
            'renewal_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
                'type': 'date',
            }),
            'trial_end_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
                'type': 'date',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all',
                'placeholder': 'https://...',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all resize-none',
                'placeholder': 'Additional notes...',
                'rows': 3,
            }),
        }
