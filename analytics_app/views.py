from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from subscriptions.models import Subscription, Category
from .utils import (
    get_monthly_spending_data,
    get_category_breakdown,
    get_spending_trend,
    get_yearly_projection,
    get_most_expensive_subscriptions,
    get_subscription_count_by_status,
)


@login_required
def overview(request):
    """Analytics overview page."""
    user = request.user
    
    # Spending trend
    trend = get_spending_trend(user)
    
    # Yearly projection
    projection = get_yearly_projection(user)
    
    # Monthly spending chart data
    monthly_data = get_monthly_spending_data(user, months=12)
    
    # Category breakdown
    category_data = get_category_breakdown(user)
    
    # Status distribution
    status_data = get_subscription_count_by_status(user)
    
    # Most expensive
    top_expensive = get_most_expensive_subscriptions(user)
    
    # Active vs cancelled stats
    total_active = Subscription.objects.filter(user=user, status='active').count()
    total_cancelled = Subscription.objects.filter(user=user, status='cancelled').count()
    total_paused = Subscription.objects.filter(user=user, status='paused').count()
    
    context = {
        'trend': trend,
        'projection': projection,
        'monthly_labels': [d['month'] for d in monthly_data],
        'monthly_values': [float(d['amount']) for d in monthly_data],
        'category_labels': [d['category'] for d in category_data],
        'category_values': [float(d['amount']) for d in category_data],
        'category_colors': [d['color'] for d in category_data],
        'status_data': status_data,
        'top_expensive': top_expensive,
        'total_active': total_active,
        'total_cancelled': total_cancelled,
        'total_paused': total_paused,
    }
    return render(request, 'analytics_app/overview.html', context)


@login_required
def spending(request):
    """Detailed spending analysis."""
    user = request.user
    
    monthly_data = get_monthly_spending_data(user, months=12)
    category_data = get_category_breakdown(user)
    trend = get_spending_trend(user)
    
    context = {
        'monthly_labels': [d['month'] for d in monthly_data],
        'monthly_values': [float(d['amount']) for d in monthly_data],
        'category_labels': [d['category'] for d in category_data],
        'category_values': [float(d['amount']) for d in category_data],
        'category_colors': [d['color'] for d in category_data],
        'trend': trend,
    }
    return render(request, 'analytics_app/spending.html', context)


@login_required
def categories(request):
    """Category-wise analytics."""
    user = request.user
    
    categories = Category.objects.all()
    category_analytics = []
    
    for category in categories:
        cat_subs = Subscription.objects.filter(user=user, category=category, status='active')
        if cat_subs.exists():
            total = sum(s.monthly_cost for s in cat_subs)
            count = cat_subs.count()
            category_analytics.append({
                'category': category,
                'total': round(total, 2),
                'count': count,
                'subscriptions': cat_subs,
            })
    
    # Sort by total spending
    category_analytics.sort(key=lambda x: x['total'], reverse=True)
    
    context = {
        'category_analytics': category_analytics,
    }
    return render(request, 'analytics_app/categories.html', context)
