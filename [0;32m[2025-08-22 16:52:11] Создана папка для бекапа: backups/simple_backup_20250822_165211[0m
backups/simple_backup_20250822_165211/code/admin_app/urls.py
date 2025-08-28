"""
URL configuration for Check Your Crypto admin app
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.shortcuts import redirect

def health_check(request):
    """Health check endpoint"""
    return JsonResponse({"status": "ok", "service": "checkyourcrypto-admin"})

urlpatterns = [
    # Стандартная Django админка
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('api/', include('core.urls')),
]
