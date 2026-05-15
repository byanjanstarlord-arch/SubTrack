"""Analytics utility functions for SubTrack."""
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta, date
from subscriptions.models import Subscription, Category


def get_monthly_spending_data(user, months=6):
    """Get monthly spending data for the last N months."""
    today = timezone.now().date()
    data = []
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for i in range(months - 1, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_label = month_names[month_date.month - 1]
        
        # Get active subscriptions for that period (simplified)
        active_subs = Subscription.objects.filter(
            user=user,
            status='active',
            created_at__date__lte=month_date,
        )
        
        total = sum(s.monthly_cost for s in active_subs)
        
        data.append({
            'month': month_label,
            'amount': round(total, 2),
        })
    
    return data


def get_category_breakdown(user):
    """Get spending breakdown by category."""
    active_subs = Subscription.objects.filter(user=user, status='active')
    
    # Get all categories
    categories = Category.objects.all()
    data = []
    
    for category in categories:
        cat_subs = active_subs.filter(category=category)
        total = sum(s.monthly_cost for s in cat_subs)
        
        if total > 0:
            data.append({
                'category': category.name,
                'amount': round(total, 2),
                'color': category.color,
                'icon': category.icon,
            })
    
    # Add uncategorized
    uncategorized = active_subs.filter(category__isnull=True)
    uncategorized_total = sum(s.monthly_cost for s in uncategorized)
    if uncategorized_total > 0:
        data.append({
            'category': 'Other',
            'amount': round(uncategorized_total, 2),
            'color': '#9CA3AF',
            'icon': 'more-horizontal',
        })
    
    return sorted(data, key=lambda x: x['amount'], reverse=True)


def get_spending_trend(user):
    """Calculate spending trend (increase/decrease)."""
    today = timezone.now().date()
    
    # This month
    this_month_subs = Subscription.objects.filter(user=user, status='active')
    this_month_total = sum(s.monthly_cost for s in this_month_subs)
    
    # Last month (simplified - compare with subscriptions created before last month)
    last_month = today - timedelta(days=30)
    last_month_subs = Subscription.objects.filter(
        user=user,
        status='active',
        created_at__date__lte=last_month,
    )
    last_month_total = sum(s.monthly_cost for s in last_month_subs)
    
    if last_month_total > 0:
        change = ((this_month_total - last_month_total) / last_month_total) * 100
    else:
        change = 0
    
    return {
        'current': this_month_total,
        'previous': last_month_total,
        'change_percent': round(change, 1),
        'direction': 'up' if change > 0 else 'down' if change < 0 else 'stable',
    }


def get_yearly_projection(user):
    """Calculate yearly spending projection."""
    active_subs = Subscription.objects.filter(user=user, status='active')
    monthly = sum(s.monthly_cost for s in active_subs)
    yearly = monthly * 12
    
    return {
        'monthly': round(monthly, 2),
        'yearly': round(yearly, 2),
    }


def get_most_expensive_subscriptions(user, limit=5):
    """Get the most expensive active subscriptions."""
    return Subscription.objects.filter(
        user=user,
        status='active'
    ).order_by('-price')[:limit]


def get_subscription_count_by_status(user):
    """Get subscription counts grouped by status."""
    from django.db.models import Count
    
    status_counts = Subscription.objects.filter(user=user).values('status').annotate(
        count=Count('id')
    )
    
    result = {}
    for item in status_counts:
        result[item['status']] = item['count']
    
    return result
