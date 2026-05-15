from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta, date
from .models import Subscription, Category, SubscriptionHistory
from .forms import SubscriptionForm


@login_required
def subscription_list(request):
    """List all user subscriptions with filtering."""
    user = request.user
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category', 'all')
    search = request.GET.get('search', '')
    
    subscriptions = Subscription.objects.filter(user=user)
    
    if status_filter != 'all':
        subscriptions = subscriptions.filter(status=status_filter)
    if category_filter != 'all':
        subscriptions = subscriptions.filter(category_id=category_filter)
    if search:
        subscriptions = subscriptions.filter(name__icontains=search)
    
    # Stats
    total_active = Subscription.objects.filter(user=user, status='active').count()
    total_monthly = sum(s.monthly_cost for s in Subscription.objects.filter(user=user, status='active'))
    total_yearly = sum(s.yearly_cost for s in Subscription.objects.filter(user=user, status='active'))
    upcoming_renewals = Subscription.objects.filter(
        user=user, 
        status='active',
        renewal_date__lte=timezone.now().date() + timedelta(days=7)
    ).count()
    
    categories = Category.objects.all()
    
    context = {
        'subscriptions': subscriptions,
        'categories': categories,
        'total_active': total_active,
        'total_monthly': total_monthly,
        'total_yearly': total_yearly,
        'upcoming_renewals': upcoming_renewals,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search': search,
    }
    return render(request, 'subscriptions/list.html', context)


@login_required
def subscription_create(request):
    """Create a new subscription."""
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='created',
                details={'message': 'Subscription created manually'}
            )
            messages.success(request, f'{subscription.name} has been added successfully.')
            return redirect('subscriptions:list')
    else:
        form = SubscriptionForm()
    
    categories = Category.objects.all()
    return render(request, 'subscriptions/form.html', {
        'form': form,
        'categories': categories,
        'title': 'Add Subscription',
    })


@login_required
def subscription_edit(request, pk):
    """Edit an existing subscription."""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, request.FILES, instance=subscription)
        if form.is_valid():
            form.save()
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='updated',
                details={'message': 'Subscription updated'}
            )
            messages.success(request, f'{subscription.name} has been updated.')
            return redirect('subscriptions:list')
    else:
        form = SubscriptionForm(instance=subscription)
    
    categories = Category.objects.all()
    return render(request, 'subscriptions/form.html', {
        'form': form,
        'subscription': subscription,
        'categories': categories,
        'title': 'Edit Subscription',
    })


@login_required
def subscription_detail(request, pk):
    """View subscription details."""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    history = subscription.history.all()[:10]
    
    return render(request, 'subscriptions/detail.html', {
        'subscription': subscription,
        'history': history,
    })


@login_required
def subscription_delete(request, pk):
    """Delete a subscription."""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = subscription.name
        subscription.delete()
        messages.success(request, f'{name} has been deleted.')
        return redirect('subscriptions:list')
    
    return render(request, 'subscriptions/confirm_delete.html', {
        'subscription': subscription,
    })


@login_required
def subscription_toggle_status(request, pk):
    """Toggle subscription status (pause/resume)."""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    if subscription.status == 'active':
        subscription.status = 'paused'
        action = 'paused'
        msg = f'{subscription.name} has been paused.'
    elif subscription.status == 'paused':
        subscription.status = 'active'
        action = 'resumed'
        msg = f'{subscription.name} has been resumed.'
    else:
        subscription.status = 'active'
        action = 'reactivated'
        msg = f'{subscription.name} has been reactivated.'
    
    subscription.save()
    SubscriptionHistory.objects.create(
        subscription=subscription,
        action=action,
        details={'message': f'Subscription {action}'}
    )
    messages.success(request, msg)
    return redirect('subscriptions:list')


@login_required
def subscription_cancel(request, pk):
    """Cancel a subscription."""
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    
    if request.method == 'POST':
        subscription.status = 'cancelled'
        subscription.save()
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='cancelled',
            details={'message': 'Subscription cancelled by user'}
        )
        messages.success(request, f'{subscription.name} has been cancelled.')
        return redirect('subscriptions:list')
    
    return render(request, 'subscriptions/confirm_cancel.html', {
        'subscription': subscription,
    })


@login_required
def upcoming_renewals(request):
    """View upcoming renewals."""
    user = request.user
    today = timezone.now().date()
    
    # Next 7 days
    week_ahead = today + timedelta(days=7)
    month_ahead = today + timedelta(days=30)
    
    this_week = Subscription.objects.filter(
        user=user,
        status='active',
        renewal_date__range=[today, week_ahead]
    ).order_by('renewal_date')
    
    this_month = Subscription.objects.filter(
        user=user,
        status='active',
        renewal_date__range=[week_ahead, month_ahead]
    ).order_by('renewal_date')
    
    context = {
        'this_week': this_week,
        'this_month': this_month,
        'today': today,
    }
    return render(request, 'subscriptions/renewals.html', context)


@login_required
def trials(request):
    """View active trials."""
    user = request.user
    active_trials = Subscription.objects.filter(
        user=user,
        status='trial',
        trial_end_date__gte=timezone.now().date()
    ).order_by('trial_end_date')
    
    expired_trials = Subscription.objects.filter(
        user=user,
        status='trial',
        trial_end_date__lt=timezone.now().date()
    )
    
    context = {
        'active_trials': active_trials,
        'expired_trials': expired_trials,
    }
    return render(request, 'subscriptions/trials.html', context)


@login_required
def export_csv(request):
    """Export subscriptions to CSV."""
    import csv
    from django.http import HttpResponse
    
    user = request.user
    subscriptions = Subscription.objects.filter(user=user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subtrack_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Category', 'Price', 'Currency', 'Billing Cycle',
        'Renewal Date', 'Status', 'Payment Method', 'Website', 'Notes'
    ])
    
    for sub in subscriptions:
        writer.writerow([
            sub.name,
            sub.category.name if sub.category else '',
            sub.price,
            sub.currency,
            sub.get_billing_cycle_display(),
            sub.renewal_date,
            sub.get_status_display(),
            sub.get_payment_method_display(),
            sub.website_url,
            sub.notes,
        ])
    
    return response
