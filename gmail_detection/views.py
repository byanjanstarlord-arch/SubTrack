from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import GmailDetection, ScanSession
from .detection_engine import get_detector


@login_required
def dashboard(request):
    """Gmail detection dashboard."""
    user = request.user
    
    # Check if Gmail is connected
    if not user.gmail_connected:
        return render(request, 'gmail_detection/connect.html')
    
    # Get recent detections
    recent_detections = GmailDetection.objects.filter(user=user)[:20]
    
    # Stats
    pending_count = GmailDetection.objects.filter(user=user, status='pending').count()
    confirmed_count = GmailDetection.objects.filter(user=user, status='confirmed').count()
    total_found = GmailDetection.objects.filter(user=user).count()
    
    # Recent scan sessions
    scan_sessions = ScanSession.objects.filter(user=user)[:5]
    
    context = {
        'recent_detections': recent_detections,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'total_found': total_found,
        'scan_sessions': scan_sessions,
    }
    return render(request, 'gmail_detection/dashboard.html', context)


@login_required
def connect_gmail(request):
    """Redirect to Google OAuth."""
    from django.urls import reverse
    return redirect(reverse('accounts:google_auth'))


@login_required
def disconnect_gmail(request):
    """Disconnect Gmail account."""
    user = request.user
    user.gmail_connected = False
    user.gmail_access_token = None
    user.gmail_refresh_token = None
    user.save()
    
    messages.success(request, 'Gmail account disconnected successfully.')
    return redirect('gmail_detection:dashboard')


@login_required
def scan_emails(request):
    """Trigger email scan."""
    user = request.user
    
    if not user.gmail_connected:
        messages.error(request, 'Please connect your Gmail account first.')
        return redirect('gmail_detection:dashboard')
    
    try:
        # Create scan session
        session = ScanSession.objects.create(user=user, status='running')
        
        # Start scan (in production, this would be a Celery task)
        _perform_scan(user, session)
        
        session.status = 'completed'
        session.save()
        
        messages.success(
            request, 
            f'Scan complete! Found {session.subscriptions_found} potential subscriptions.'
        )
        
    except Exception as e:
        messages.error(request, f'Scan failed: {str(e)}')
    
    return redirect('gmail_detection:dashboard')


def _perform_scan(user, session):
    """Perform the actual email scan."""
    # In a real implementation, this would:
    # 1. Use Gmail API to fetch emails
    # 2. Parse each email with the detection engine
    # 3. Save results
    # For now, this is a placeholder structure
    
    from googleapiclient.discovery import build
    
    try:
        # Build Gmail service
        # service = build('gmail', 'v1', credentials=credentials)
        
        # Search for subscription-related emails
        # query = 'subject:(subscription OR receipt OR invoice OR payment OR billing)'
        # results = service.users().messages().list(userId='me', q=query).execute()
        
        # Process each email
        detector = get_detector()
        
        # Placeholder: In production, iterate through emails
        # For demo, we'll simulate some detections
        session.emails_scanned = 0
        session.subscriptions_found = 0
        session.save()
        
    except Exception as e:
        session.status = 'failed'
        session.error_message = str(e)
        session.save()
        raise


@login_required
def confirm_detection(request, pk):
    """Confirm a detected subscription and create it."""
    detection = get_object_or_404(GmailDetection, pk=pk, user=request.user)
    
    if detection.status == 'confirmed':
        messages.info(request, 'This subscription is already confirmed.')
        return redirect('gmail_detection:dashboard')
    
    if request.method == 'POST':
        # Create subscription from detection
        from subscriptions.models import Subscription, Category
        
        # Try to find matching category
        category = None
        try:
            category = Category.objects.filter(name__icontains=detection.detected_service).first()
        except:
            pass
        
        subscription = Subscription.objects.create(
            user=request.user,
            name=detection.detected_service,
            category=category,
            price=detection.detected_amount or 0,
            currency=detection.detected_currency,
            billing_cycle=detection.detected_billing_cycle or 'monthly',
            renewal_date=detection.detected_date or timezone.now().date(),
            status='active',
            is_auto_detected=True,
            gmail_detection=detection,
        )
        
        detection.status = 'confirmed'
        detection.subscription = subscription
        detection.save()
        
        messages.success(request, f'{detection.detected_service} has been added to your subscriptions.')
        return redirect('gmail_detection:dashboard')
    
    return render(request, 'gmail_detection/confirm.html', {'detection': detection})


@login_required
def reject_detection(request, pk):
    """Reject a detected subscription."""
    detection = get_object_or_404(GmailDetection, pk=pk, user=request.user)
    
    detection.status = 'rejected'
    detection.save()
    
    messages.success(request, 'Detection rejected.')
    return redirect('gmail_detection:dashboard')


@login_required
@require_POST
def api_scan_status(request):
    """AJAX endpoint for scan status."""
    user = request.user
    
    latest_session = ScanSession.objects.filter(user=user).first()
    
    if latest_session:
        return JsonResponse({
            'status': latest_session.status,
            'emails_scanned': latest_session.emails_scanned,
            'subscriptions_found': latest_session.subscriptions_found,
        })
    
    return JsonResponse({'status': 'no_scan'})
