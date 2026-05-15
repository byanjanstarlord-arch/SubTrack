import secrets
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .forms import LoginForm, SignUpForm, UserProfileForm, UserSettingsForm, PasswordResetRequestForm
from .models import UserSettings


def login_view(request):
    """Premium split-screen login view."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', reverse('dashboard:index'))
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'google_client_id': '',  # Will be populated from settings
    })


def signup_view(request):
    """Premium signup view."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Signal may already create settings; keep this idempotent.
            UserSettings.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard:index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')


@login_required
def profile_view(request):
    """User profile view."""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def settings_view(request):
    """User settings view."""
    user = request.user
    
    # Get or create settings
    user_settings, created = UserSettings.objects.get_or_create(
        user=user,
        defaults={
            'email_notifications': True,
            'renewal_alert_days': 3,
            'currency': user.currency,
        }
    )
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            # Sync currency back to user
            user.currency = form.cleaned_data['currency']
            user.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('accounts:settings')
    else:
        form = UserSettingsForm(instance=user_settings)
    
    return render(request, 'accounts/settings.html', {'form': form})


def password_reset_request_view(request):
    """Password reset request."""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            # Implementation would send email - placeholder for now
            messages.success(request, 'If an account exists with this email, you will receive password reset instructions.')
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})


# =============================================================================
# GOOGLE OAUTH VIEWS
# =============================================================================

def google_auth_init(request):
    """Initiate Google OAuth flow."""
    # Generate state token
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    
    # Build OAuth URL
    from django.conf import settings
    redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
    
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=code"
        "&scope=email profile https://www.googleapis.com/auth/gmail.readonly"
        f"&state={state}"
        "&access_type=offline"
        "&prompt=consent"
    )
    
    return redirect(auth_url)


def google_auth_callback(request):
    """Handle Google OAuth callback."""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # Verify state
    if state != request.session.get('google_oauth_state'):
        messages.error(request, 'Invalid OAuth state. Please try again.')
        return redirect('accounts:login')
    
    if not code:
        messages.error(request, 'Authorization failed. Please try again.')
        return redirect('accounts:login')
    
    try:
        import requests
        from django.conf import settings
        
        redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
        
        # Exchange code for tokens
        token_response = requests.post('https://oauth2.googleapis.com/token', data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        })
        
        tokens = token_response.json()
        
        if 'error' in tokens:
            messages.error(request, 'Failed to authenticate with Google.')
            return redirect('accounts:login')
        
        # Get user info
        userinfo_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        )
        userinfo = userinfo_response.json()
        
        # Get or create user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(email=userinfo['email'])
        except User.DoesNotExist:
            user = User.objects.create(
                email=userinfo['email'],
                username=userinfo['email'].split('@')[0],
                first_name=userinfo.get('given_name', ''),
                last_name=userinfo.get('family_name', ''),
                is_verified=True,
                gmail_connected=True,
            )
            # Signal may already create settings; keep this idempotent.
            UserSettings.objects.get_or_create(user=user)
        
        # Store Gmail tokens
        user.gmail_connected = True
        user.gmail_access_token = tokens.get('access_token')
        user.gmail_refresh_token = tokens.get('refresh_token')
        user.save()
        
        login(request, user)
        messages.success(request, f'Welcome, {user.first_name}!')
        return redirect('dashboard:index')
        
    except Exception as e:
        messages.error(request, 'An error occurred during authentication.')
        return redirect('accounts:login')
