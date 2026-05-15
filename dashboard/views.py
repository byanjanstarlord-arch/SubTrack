from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date
from subscriptions.models import Subscription, Category
from analytics_app.utils import (
    get_monthly_spending_data,
    get_category_breakdown,
    get_spending_trend,
    get_yearly_projection,
)


@login_required
def index(request):
    """Main dashboard view - premium analytics overview."""
    user = request.user
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # ===== STATS =====
    active_subscriptions = Subscription.objects.filter(user=user, status='active')
    total_subscriptions = active_subscriptions.count()
    
    # Monthly spend
    monthly_spend = sum(s.monthly_cost for s in active_subscriptions)
    
    # Yearly projection
    yearly_projection = monthly_spend * 12
    
    # Upcoming renewals (next 7 days)
    week_ahead = today + timedelta(days=7)
    upcoming_renewals = Subscription.objects.filter(
        user=user,
        status='active',
        renewal_date__range=[today, week_ahead]
    ).order_by('renewal_date')[:5]
    
    upcoming_count = Subscription.objects.filter(
        user=user,
        status='active',
        renewal_date__range=[today, week_ahead]
    ).count()
    
    # ===== SUBSCRIPTIONS LIST =====
    subscriptions = active_subscriptions[:8]
    
    # ===== CHART DATA =====
    monthly_spending = get_monthly_spending_data(user)
    category_data = get_category_breakdown(user)
    
    # ===== INSIGHTS =====
    insights = generate_insights(user, monthly_spend, category_data)
    
    context = {
        # Stats
        'total_subscriptions': total_subscriptions,
        'monthly_spend': monthly_spend,
        'yearly_projection': yearly_projection,
        'upcoming_count': upcoming_count,
        'upcoming_renewals': upcoming_renewals,
        
        # Subscriptions
        'subscriptions': subscriptions,
        
        # Chart data (JSON for Chart.js)
        'monthly_spending_labels': [d['month'] for d in monthly_spending],
        'monthly_spending_values': [float(d['amount']) for d in monthly_spending],
        'category_labels': [d['category'] for d in category_data],
        'category_values': [float(d['amount']) for d in category_data],
        'category_colors': [d['color'] for d in category_data],
        
        # Insights
        'insights': insights,
        
        # Time reference
        'today': today,
    }
    return render(request, 'dashboard/index.html', context)


def generate_insights(user, monthly_spend, category_data):
    """Generate smart insights for the dashboard."""
    insights = []
    
    # Top category insight
    if category_data:
        top_category = max(category_data, key=lambda x: x['amount'])
        total = sum(d['amount'] for d in category_data)
        percentage = (top_category['amount'] / total * 100) if total > 0 else 0
        insights.append({
            'type': 'info',
            'icon': 'pie-chart',
            'message': f"You spend <strong>{percentage:.0f}%</strong> on {top_category['category']}.",
        })
    
    # Yearly projection warning
    if monthly_spend > 0:
        yearly = monthly_spend * 12
        if yearly > 20000:
            insights.append({
                'type': 'warning',
                'icon': 'alert-triangle',
                'message': f"Your yearly spending projection is <strong>{user.currency_symbol}{yearly:,.0f}</strong>.",
            })
        else:
            insights.append({
                'type': 'success',
                'icon': 'trending-down',
                'message': f"Your yearly projection is <strong>{user.currency_symbol}{yearly:,.0f}</strong>. Well managed!",
            })
    
    # Subscription count
    active_count = Subscription.objects.filter(user=user, status='active').count()
    paused_count = Subscription.objects.filter(user=user, status='paused').count()
    
    if paused_count > 0:
        insights.append({
            'type': 'info',
            'icon': 'pause-circle',
            'message': f"You have <strong>{paused_count}</strong> paused subscription{'s' if paused_count > 1 else ''}.",
        })
    
    if active_count > 10:
        insights.append({
            'type': 'warning',
            'icon': 'layers',
            'message': f"You're subscribed to <strong>{active_count}</strong> services. Consider reviewing unused ones.",
        })
    
    return insights
