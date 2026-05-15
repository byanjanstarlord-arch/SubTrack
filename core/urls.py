from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def landing_page(request):
    """Landing page view."""
    return render(request, 'landing.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('analytics/', include('analytics_app.urls')),
    path('gmail/', include('gmail_detection.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
