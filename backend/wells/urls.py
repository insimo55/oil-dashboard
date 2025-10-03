# backend/wells/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WellViewSet, TaskViewSet 

# Создаем роутер
router = DefaultRouter()
# Регистрируем наш ViewSet. 'wells' - это префикс URL
router.register(r'wells', WellViewSet)
router.register(r'tasks', TaskViewSet)

# Наши URL-ы генерируются роутером автоматически
urlpatterns = [
    path('', include(router.urls)),
]