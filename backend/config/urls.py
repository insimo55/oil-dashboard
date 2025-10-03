# backend/config/urls.py

from django.contrib import admin
from django.urls import path, include # Убедись, что 'include' импортирован

urlpatterns = [
    path('admin/', admin.site.urls),
    # Добавляем эту строчку
    path('api/', include('wells.urls')), 
]