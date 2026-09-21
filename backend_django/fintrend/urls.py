from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
from pathlib import Path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analytics_api.urls')),
    path('api', include('analytics_api.urls')),
]

def serve_index(request):
    return render(request, 'index.html')

urlpatterns += [
    re_path(r'^(?!api|admin|static).*$', serve_index),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
