from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def list_notifications(request):
    """List all notifications."""
    notifications = request.user.notifications.all()
    
    # Filter by type if specified
    type_filter = request.GET.get('type', 'all')
    if type_filter != 'all':
        notifications = notifications.filter(type=type_filter)
    
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'type_filter': type_filter,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def mark_read(request, pk):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')


@login_required
def delete_notification(request, pk):
    """Delete a notification."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notifications:list')


@login_required
def unread_count(request):
    """Get unread notification count (AJAX)."""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


def create_notification(user, type, title, message, subscription=None, scheduled_time=None):
    """Helper to create a notification."""
    notification = Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        subscription=subscription,
        scheduled_time=scheduled_time,
    )
    return notification
